# Stage 02 — Checkout correctness

| | |
|---|---|
| **Weeks** | W7–W9 (3 weeks) |
| **Hours** | 36 must + 4 stretch (40 total) |
| **Architecture at start → at end** | `market` as a layered monolith (identity, vendors, catalog) on PG17 + the S3-compatible object store (Garage) → the same monolith plus `inventory`, `cart`, `ordering` (checkout, vendor groups, fulfillment) and `promotions`; PG17 with RLS, separate app/migrator roles and per-role timeouts; Mailpit for the (deliberately synchronous) email |
| **New technologies** | `SELECT … FOR UPDATE` vs conditional `UPDATE`, MVCC system columns, isolation levels, SERIALIZABLE (SSI) with retry, `INSERT … ON CONFLICT DO NOTHING RETURNING`, Row Level Security with `SET LOCAL`, per-role `lock_timeout` / `statement_timeout` / `idle_in_transaction_session_timeout`, barrier-based concurrency tests, Python's concurrency model (the GIL, threads vs processes), Mailpit |
| **Portfolio tag** | `v0.2` |
| **Old-spec theory to read** | [P1 D19–D24](../python/01-stockpilot.md) (naive order then `FOR UPDATE`, deadlock, clean 409, factories, Hypothesis); [P2 D31–D39](../python/02-quickserve-pos.md) (integer-cent pricing and half-cent rounding D31–D36, Strategy + Capped D37–D39); [P4 D67–D71](../python/04-wareflow.md) (row locks, MVCC, SERIALIZABLE + 40001, deadlock ordering, timeouts); [P9 D145–D153](../python/09-payflow.md) (Idempotency-Key + request hash D145–D149, `ON CONFLICT` and "why not Redis" D151–D153); [P10 D157–D165](../python/10-atlasmarket.md) (RLS D157–D161, vendor groups and the checkout key D163–D165); [P3 D42–D43](../python/03-peopleops.md) (the blocking email); also [phase-1 D20–D21](../../phase-1-foundations.md) (isolation and deadlock scripts) |

Version pins in this file are as of 2026-09. Re-check them with `scripts/compat_check.sh` before you start (ADR-001); this stage adds Mailpit, a maintained SMTP test server with a web UI and an HTTP API. (MailHog, which older tutorials use, has had no release since 2020.)

> **What this stage is really for.** This is the correctness that interviewers probe hardest: two people buying the last unit, one double-click, a promo used 101 times, one vendor seeing another's orders. You will make each of these happen on purpose, record it, and then make it impossible, with the database doing the enforcing wherever it can. Every race here is proven red before it is proven green, and those proofs are part of the portfolio spine that is never cut.

---

## 1. The problem this stage starts from

**Business terms.** Customers can browse a million products, but nobody can buy anything. A marketplace checkout is harder than a shop's: one customer cart holds items from several vendors, so one order must split into one **vendor group** per vendor, each fulfilled and (later) paid out separately. Vendors run their own promo codes. Vendors must never see each other's orders, even though one customer order contains all of them.

**Engineering terms.** [Stage 01](stage-01-layered-monolith.md) left:
- no stock, cart or orders; the S1 measured problem is that *placing orders needs stock that stays correct under concurrency*;
- vendor isolation that lives only in application code, one forgotten `WHERE vendor_id` away from a leak (P10 named exactly this);
- no idempotency: a double-click on "Place order" will create two orders;
- no timeouts: one abandoned transaction could hold a lock forever and stall every checkout behind it;
- still broken on purpose: the 4× login limiter and the refresh tokens that cannot be revoked (both fixed in S3).

## 2. Outcomes — what exists when the stage is finished

1. `inventory` with `stock_levels` and append-only `stock_movements`, always written in the same transaction.
2. A DB-backed `cart` and a checkout that creates **one order split into `order_vendor_groups`** with price snapshots, holds stock, and ends in `awaiting_payment`.
3. A fulfillment state machine per vendor group; vendor promo codes (fixed, percent, capped).
4. The confirmation email sent **synchronously** through Mailpit with an injected delay, **left painful on purpose**, with its cost recorded in `docs/perf/blocking-email.md`.
5. A race suite: the naive checkout failing a two-buyer barrier test; `FOR UPDATE` vs conditional `UPDATE` compared; the [A,B]/[B,A] deadlock produced and fixed; MVCC and isolation demos recorded.
6. The promo write-skew reproduced at REPEATABLE READ and fixed with SERIALIZABLE plus a jittered-retry decorator inside an `atomic_serializable()` context manager.
7. Idempotent checkout: first in Redis (and why that is wrong, in writing), then in Postgres with `INSERT … ON CONFLICT DO NOTHING RETURNING` and a request hash.
8. Per-role database timeouts, each demonstrated against the failure it prevents.
9. Pricing as a Strategy with a Capped wrapper, half-tiyin rounding, and Hypothesis properties.
10. Row Level Security on vendor tables, a `vendor_context()` issuing `SET LOCAL`, separate app and migrator roles, the forgotten-`WHERE` test, and the plain-`SET` leak reproduced and fixed.
11. A short Python concurrency experiment: the barrier race under threads and under processes, and CPU-bound work under a thread pool vs a process pool, with a note on what the GIL does and does not protect.
12. ADR-007 (isolation per operation), ADR-008 (idempotency store), ADR-009 (multi-tenancy); an SD12 session (built).
13. Stage close: tag `v0.2`, postmortem paragraph, 2 STAR stories.

## 3. Architecture at the end of the stage

```
   customer (API, JWT)             vendor staff (API, JWT)                 ops (Admin, session)
        │ POST /api/v1/checkout          │ PATCH vendor group status              │
        │ Idempotency-Key: <uuid>        │                                         │
        ▼                                ▼                                         ▼
 ┌─────────────────────────────── market (Django + DRF, sync) ──────────────────────────────────────┐
 │  identity · vendors · catalog · inventory · cart · ordering · promotions                         │
 │                                                                                                  │
 │  checkout service (one transaction, all or nothing):                                             │
 │    idempotency record · stock decrement + hold movement per line · price snapshots               │
 │    + vendor promos · order + order_vendor_groups + lines · the stored response                   │
 │  after commit: send confirmation email SYNCHRONOUSLY  ──SMTP (injected delay)──►  Mailpit        │
 │                                                                   [known pain, fixed in S4]      │
 │  vendor paths run inside vendor_context(): SET LOCAL app.vendor_id                               │
 └───────────────┬──────────────────────────────────────────────────────────────────────────────────┘
                 │ connects as market_app (NOBYPASSRLS) — migrations run as market_migrator
                 ▼
   PG17 `market`: RLS policies on vendor tables · CHECK (stock ≥ 0) · UNIQUE idempotency key
                  per-role lock_timeout / statement_timeout / idle_in_transaction_session_timeout
   Garage, S3 API (unchanged)
```

**What changed and why.**
- *Four new modules in the same process.* Checkout needs one local transaction across cart, inventory, ordering and promotions; splitting any of them would turn checkout into a distributed problem with nothing measured to justify it (checkout stays in `market` all season; see [E2](README.md#e2-service-catalog-at-the-end-of-season-1)).
- *Two database roles.* RLS only means something if the application connects as a role that cannot bypass it.
- *Mailpit* is added only to make the synchronous email's cost measurable (its HTTP API also lets a test assert that exactly one email arrived).

### What checkout must guarantee

The client sends `POST /api/v1/checkout` with a client-generated `Idempotency-Key` (a fresh UUID per checkout attempt; without it, two clicks become two orders, as P10 D163–D165 warned). Whatever you build must satisfy all of these:

1. **Never oversell.** Stock never goes below zero, and two buyers racing for the last unit get exactly one `201` and one `409`.
2. **All or nothing.** If any line is short, nothing is written, and the `409` names the short lines. The order, its vendor groups (status `awaiting_payment`, with a hold expiry time) and its lines commit together.
3. **No deadlocks** for carts that hold the same offers in any order.
4. **Exactly one order per `Idempotency-Key`**, even for two identical requests in the same millisecond, and the retry gets the same response as the first.
5. **A reused key with a different body is rejected** (`422`), never answered with the stored response.
6. **Prices are snapshotted.** Changing a product's price after checkout never changes the order.
7. **The confirmation email is sent synchronously** (the deliberate pain, fixed in S4).

How you satisfy each one is the work of section 4. Once it is built, narrate the flow from the click to the `201` in your own words (interview question 12 in section 10).

---

## 4. Build plan

### Suggested calendar (36 h over three weeks)

| Week | Blocks | Hours |
|---|---|---|
| W7 | 4.1 Domain (7.5; the blocking-email benchmark in the weekend block) · 4.2 Races, the barrier helper and step 1 (3.5) · drill (1) | 12 |
| W8 | 4.2 Races, steps 2–4 (4.5; the lock-comparison benchmark and the deadlock runs in the weekend block) · 4.8 Python concurrency (1) · 4.3 Write skew (3.5) · 4.5 Timeouts (2) · SD12 (1) | 12 |
| W9 | 4.4 Idempotent checkout (4.5) · 4.6 Pricing (2.5) · 4.7 RLS (4; the leak repro in the weekend block) · drill (1) | 12 |

The block budgets are estimates for a first attempt; log the actual hours per block in `docs/hours.csv`. If a block runs over, stop polishing, but finish its acceptance criteria: everything in this stage is on the never-cut spine or feeds it.

**Predict before you run.** Every pain-first run in this stage has a surprise in it. Before each one, write your prediction in the evidence file and commit it; then run. The expected outcomes are in section 16 under "Check your prediction". Open them only after your prediction is committed.

Every concurrency test in this stage must use a test mode that **really commits** (pytest-django's `transaction=True`). A test wrapped in one outer transaction cannot show a race between two transactions. Build a small barrier helper once (two or more threads that each open their own connection and wait on a `threading.Barrier` before the critical call) and reuse it everywhere.

---

### 4.1 Domain [7.5 h]

**What to build**
- **`inventory`:** `stock_levels` (one row per offer) and **append-only** `stock_movements` (offer, signed delta, reason such as `receive` / `hold` / `release` / `correction`, a reference to the vendor group or document that caused it, actor, timestamp). A level changes **only** in the same transaction as the movement that explains it. A `CHECK` keeps stock at or above zero.
  - Guiding question: one number per offer (available) or two (on hand and reserved)? What does each make easy: the oversell guard, the Admin's "how many are physically here?", and releasing a hold later?
- **`cart`:** one open DB-backed cart per authenticated customer, with lines (offer, quantity). No price is stored in the cart; prices are snapshotted at checkout. (The cart moves to Redis in S3.)
- **`ordering`:**
  - `order` (customer, status, totals, created_at);
  - `order_vendor_groups` (order, vendor, status, subtotal, discount, total, hold expiry time);
  - order lines (group, offer, quantity, **unit price snapshot**, product title snapshot, line total).
  - The order and all its groups and lines commit together or not at all.
  - Checkout ends with every group in `awaiting_payment`.
- **Fulfillment state machine per vendor group**, for example `awaiting_payment → paid → packed → shipped → delivered`, with `cancelled` allowed before `shipped`. Illegal transitions return 409, never 500. Vendor staff advance only their own vendor's groups (the S1 relationship rule). Until payments exist (S5), the `awaiting_payment → paid` step is triggered only by a clearly labelled dev-only management command or test helper, removed in S5.
  - Guiding question: is the order's status stored, or derived from its groups? What happens to it when one group is cancelled and another delivered?
- **`promotions`:** vendor promo codes of three kinds (fixed amount, percent, percent with a cap), a validity window, and a **maximum number of uses**. Each use is a redemption row linked to a vendor group. A promo applies only to its own vendor's group; cross-vendor promos are out of scope.
- **The synchronous confirmation email.** Add Mailpit to Compose and pin its image in ADR-001. Send the email in the request, synchronously. Make its delay controllable: either use Mailpit's own SMTP failure-testing ("chaos") options [verify which delays and failures your pinned version can inject], put Toxiproxy in front of it, or wrap the email backend with a configurable delay and failure switch for the experiment. Record which one you chose.
- **Worldgen:** extend `history` mode with orders (every order line has a matching stock movement, so stock reconciles) and **cart abandonment** at a configurable rate. Season 2 analyses both. From S3 on, carts live in Redis with a sliding TTL and emit no events, so this worldgen history is Season 2's only source of abandonment data (S3 §13 says the same).

**Pain-first: the email that blocks checkout** (P3 D42–D43 did the same with an approval email)

This pain-first contains about 65 min of unattended benchmark time (2 configurations × 3 runs × ≈11 min); schedule it in the weekend block. Keep the 0 s baseline: 4.4 reuses it.
1. Measure checkout p95 under the ADR-002 protocol (3 runs) with no SMTP delay.
2. Inject a 2-second SMTP delay. Measure again.
3. Stop the mail server entirely. Place an order. Record what the customer gets and what state the order is in.
4. Try both placements of the send: inside the checkout transaction and after commit. For each, record the order's final state, the HTTP status the customer sees, and how long the stock rows stay locked.
5. Record all numbers and both behaviours in `docs/perf/blocking-email.md`. **Do not fix it.** It is fixed in S4 (Celery, with the confirmation moving onto the outbox-backed `order.placed` event). Add it to `docs/deferred.md` as a *known violation* of the "never 500 for anticipated conditions" invariant.

**Acceptance criteria**
- A two-vendor cart produces one order, two vendor groups and correct line snapshots; changing a product's price afterwards does not change the order.
- For every offer, the sum of its movements equals its stock level (an integrity query that must return 0 rows).
- A forced failure after the groups are inserted leaves no order, no group, no line and no movement.
- The email numbers are recorded.

---

### 4.2 Races [8 h]

This block contains about 65 min of unattended benchmark time (the lock comparison: 2 approaches × 3 runs × ≈11 min) plus the 100-iteration deadlock run; schedule both in the weekend block.

**Step 1 — the naive checkout fails** (P1 D19–D24: "writing it correctly the first time teaches you nothing about why")
1. Write the stock step naively: read the level, check it in Python, write back the new value.
2. Set stock to 1. Two buyers check out the same offer through the barrier helper.
3. Predict first: how many orders, what final stock, and does the `CHECK` fire? Then run it and record the order count, the final stock and every error. Save the log to `docs/evidence/s02/oversell-red.log`.
4. Variation: decrement with an unguarded `UPDATE … SET qty = qty - n`. Predict again, run, and record what the second buyer gets (status code and error). Whatever it is, the only acceptable answer to "out of stock" is a clean `409`.

**Step 2 — two correct fixes, compared**
- **Row lock:** `SELECT … FOR UPDATE` on the stock rows, then decide, then update.
- **Conditional update:** one `UPDATE … WHERE qty >= n RETURNING …`; zero rows means "short" and becomes 409.
- For each, record in `docs/evidence/s02/lock-comparison.md`:
  - *what* is locked (which rows, which lock mode) and *for how long* (until commit, so the length of the transaction matters);
  - what the second buyer experiences while waiting, and what happens after the first commits;
  - checkout throughput and p95 on one hot offer under ADR-002 (3 runs each), at a constant arrival rate chosen so that about 50 checkouts are in flight at once (the open-model rule from S0 §4.6).
- Guiding questions: after the second `UPDATE` waits for the first to commit, does it use the old row or the new one when it checks `qty >= n`? (Read the READ COMMITTED section of the Postgres transaction-isolation docs.) Django's `QuerySet.update()` returns a row count: is the count enough here, or do you need `RETURNING`, and for what? Which row should checkout lock or update: the offer or its stock level, and what else touches each of them (an order line's foreign key references the offer)?
- Choose one approach for checkout and record why in ADR-007. A multi-line checkout is all-or-nothing: if any line is short, every decrement rolls back.

**Step 3 — the deadlock**
1. Cart X holds offers [A, B]; cart Y holds [B, A]. Lock lines in cart order, with a barrier between the first and second lock.
2. Predict what Postgres does and after how long, then run. Save the client error (with its SQLSTATE code) and the server log entry to `docs/evidence/s02/deadlock.log`. Read the `deadlock_timeout` setting in the Postgres docs to explain the delay you saw.
3. Fix it without giving up concurrency. Guiding question: what rule about the *order* in which every transaction takes its locks makes a cycle of waits impossible, and which code paths (single-line checkouts, the dev-only commands) must follow it too?
4. Prove it: 100 iterations of opposite-order carts, zero deadlocks. Keep the reproduction as a test with your fix disabled by a flag, so the red version can be shown in an interview.

**Step 4 — see what Postgres is doing** (demos, recorded, not features)
- **MVCC** (multi-version concurrency control: every update writes a new row version, and each transaction sees the versions valid for its snapshot). In two `psql` sessions: A updates a stock row inside an open transaction; B reads the same row. Predict whether B blocks and which value it sees, then run. Select the hidden `xmin` and `xmax` columns before and after A commits. Record in `mvcc-demo.md`.
- **Isolation.** Read a value twice in one transaction while another session commits a change between the reads, once at READ COMMITTED and once at REPEATABLE READ. Predict both outcomes, run, and record in `isolation-demo.md`.
- (The foreign-key lock demo, `FOR KEY SHARE` vs `FOR NO KEY UPDATE`, is a stretch item in section 14.)

**Acceptance criteria**
- The two-buyer barrier test gives **exactly one 201 and one 409**, every time.
- The deadlock reproduction and its fix are both runnable.
- Both demos are recorded, each with its committed prediction.

---

### 4.3 Write skew [3.5 h]

**Write skew** is an anomaly where two transactions each read the same data, each make a decision that is valid on its own, and each write a *different* row, so neither sees a conflict, yet together they break a rule.

**Pain-first**
1. Model the cap by counting: a checkout counts the promo's existing redemptions and inserts a new redemption row if the count is below the cap.
2. Set the cap to 100 and the current count to 99. Run 20 concurrent checkouts using the promo (different customers and offers, so no stock row is shared) at REPEATABLE READ.
3. Predict the final redemption count and whether any transaction fails, commit the prediction, then run. Record the count, every error, and your explanation of why REPEATABLE READ did or did not catch it. Save to `docs/evidence/s02/write-skew-rr.log`.

**The fix: SERIALIZABLE plus retry**
- Run the operation at SERIALIZABLE. Postgres implements it with SSI (serializable snapshot isolation), which tracks read/write dependencies and aborts one transaction with error `40001` when the result could not have happened serially.
- A context manager, **`atomic_serializable()`**: opens an *outermost* transaction at SERIALIZABLE. Isolation must be set as the first statement of the transaction; Django configures isolation per connection, so you issue it yourself. It must refuse to run nested inside another transaction (read about `atomic(durable=True)` and `connection.in_atomic_block`).
- A decorator, **`@retry_on_serialization_failure`**: catches `40001`, waits with **jittered** exponential backoff, and re-runs the *whole* decorated function; after the last attempt it raises a domain error that becomes 409.
- The retry wraps the transaction from **outside**. Retrying inside a transaction that already failed cannot work.
- Rerun the 20-way test: exactly 100 redemptions, the rest get a clean "promo exhausted" 409. Save `write-skew-serializable.log`, including how many retries happened.

Guiding questions (answer them in ADR-007):
- Isolation is set per transaction, not per statement. If promo redemption needs SERIALIZABLE, what happens to the checkout transaction that contains it?
- Two alternatives avoid SERIALIZABLE: lock the promotion row, or keep a counter on it and increment it with a conditional update. Each "materializes" the conflict onto one row. Which is simpler here, what does each cost under contention, and why might you still keep SERIALIZABLE?
- What happens if the retried function sends an email?

**Acceptance criteria**
- The write-skew test commits more than 100 at REPEATABLE READ and exactly 100 at SERIALIZABLE (or under your chosen alternative, if ADR-007 argues for it; the reproduction stays).
- The decorator and context manager are typed, unit-tested (retry count, jitter bounds, refusal to nest), and reusable (S5 payouts use them).

---

### 4.4 Idempotent checkout [4.5 h]

**Idempotency** means that repeating the same request has the same effect as sending it once. The client sends an `Idempotency-Key` header; the server remembers what it did for that key.

**Pain-first: the tempting wrong store** (P9: "the most important why-not in the whole roadmap")
1. Run a throwaway Valkey container under a `labs` Compose profile. It is not part of the architecture yet; Redis joins properly in S3.
2. Store keys there: set-if-absent before checkout, write the response after.
3. Try to break it three ways. For each, predict what a retry of the same checkout does, then run it and record the number of orders and the state of the key in `docs/evidence/s02/redis-idempotency.md`:
   - **Not transactional with the order:** kill the process after the order commits but before the response is written to Redis; separately, let the order transaction fail after the key was set.
   - **Evictable:** give the instance a small `maxmemory` and an LRU eviction policy, then fill it.
   - **Lost on restart:** restart the container without persistence.
4. Write the conclusion in your own words: what property must the record that says "I already took this order" have, relative to the order itself?

**The fix: Postgres**

Requirements (the design is yours):
- An idempotency table in `ordering`. A sketch of its columns (a requirement, not a schema to copy): scope (the customer), key, request hash, response status, response body (JSONB), the order it produced, created_at. The key is **unique per scope**.
- The claim is durable and lives in the **same transaction** as the order: it commits or rolls back with it.
- A duplicate with the same body gets the stored response; a duplicate with a different body gets `422`.

Guiding questions:
- Which single SQL statement both claims the key and tells you whether you were first? What must the executor do after it, and what must the loser read and compare?
- Why `DO NOTHING` and not `DO UPDATE`, and why not simply catch the integrity error? Be ready to explain (P9 D151–D153).
- What does a concurrent duplicate's `INSERT` do while the first transaction is still open, and what does it do after the first commits, or after it rolls back? Watch it with two `psql` sessions before you rely on it, and commit your prediction first.
- Does that behaviour depend on the isolation level? Repeat the two-session experiment at READ COMMITTED and at the level ADR-007 chose for checkout. If checkout runs at SERIALIZABLE, what does the waiting duplicate get once the first commits, and what does your `@retry_on_serialization_failure` decorator (4.3) then do with it? Run the double-click test at the isolation level checkout actually uses.

**Measure the cost of the claim.** After the claim works, rerun the 0 s-delay checkout baseline from 4.1 (3 runs, same seed and limits, ≈35 min unattended, in the weekend block) and compare it with the 4.1 numbers under the noise rule. That difference is the ADR-008 latency number.

**Acceptance criteria**
- A double-click (two concurrent identical requests with one key) gives **one order and two identical responses**, at the isolation level checkout actually runs at.
- The same key with a different body gives 422, never the cached response.
- The claim's latency cost is recorded against the 4.1 baseline.
- ADR-008 records the Redis failures with evidence.

Guiding questions for ADR-008: if the checkout body is only a cart id, what must the request hash cover so that "same key, different request" is detectable? A checkout that fails with 409 rolls back, so its key row disappears too: is that the behaviour you want on a retry? (S5 generalizes this store to Stripe's rules: a result is stored once execution starts, an in-flight duplicate returns 409, replays carry `Idempotent-Replayed: true`, and keys are kept at least 24 h.)

---

### 4.5 Timeouts [2 h]

Set three timeouts **per database role** (`market_app`, `market_migrator`, `market_ro`) and demonstrate each against the failure it prevents (P4 D67–D71 did the same):

| Timeout | Failure it prevents | Demonstration (do → observe → record in `docs/evidence/s02/timeouts.md`) |
|---|---|---|
| `lock_timeout` | A request waiting forever for a row lock, tying up a gunicorn worker | In `psql`, lock a stock row and leave the transaction open; place a checkout for that offer → without the timeout it hangs; with it, it fails fast with `55P03` |
| `statement_timeout` | A runaway query eating a connection and CPU | Run a deliberately slow query (for example, a facet filter that cannot use an index, or `pg_sleep`) → cancelled with `57014` |
| `idle_in_transaction_session_timeout` | An abandoned transaction holding locks and blocking vacuum | `BEGIN`, update a stock row, walk away → checkouts queue behind it; with the timeout, the session is terminated and the lock released |

Requirements:
- Values differ by role on purpose (short for the web role; the migrator gets its own values, and S6 adds `lock_timeout = 3s` inside every migration). Record the values and reasons in ADR-007.
- Map `55P03` and `57014` on the request path to a 4xx/503 response with a clear body, never a 500.
- Guiding question: role settings apply when a session starts. With persistent connections, when does a changed value actually take effect?

**Acceptance criteria:** all three demonstrations recorded; mapping tests pass.

---

### 4.6 Pricing [2.5 h]

Build this as a **refactor** after checkout totals already work (P2 D37–D39 did the Strategy refactor the same way).

**What to build**
- A **Strategy pattern** for discounts: one small class per kind (fixed, percent), each with one method that takes a `Money` and returns the discount as `Money`.
- A **Capped wrapper** that wraps any strategy and limits its result (a decorator in the design-pattern sense). Capped is tested once, not once per strategy.
- **Half-tiyin rounding:** a percent of an odd tiyin amount produces half a tiyin; apply the rounding rule you chose in ADR-006, in exactly one place.
- **Allocation:** a vendor group's discount is spread across its lines so that the parts sum exactly to the group discount (largest remainder, as in ADR-006).
- **Hypothesis properties** (seed pinned): a discount is never negative and never exceeds the amount it applies to; the cap is always respected; line parts sum to the group total; group totals sum to the order total.

Prices are treated as tax-inclusive in Season 1; there is no tax computation.

**Acceptance criteria:** strategies and the wrapper are unit-tested in isolation; the properties pass; checkout totals are unchanged by the refactor (the existing tests stay green). If you are behind, the degrade list ([schedule-and-cuts §7](schedule-and-cuts.md#7-cut-order-and-the-degrade-list)) lets the capped discount go (the item "Capped discount dropped", saves 1 h).

---

### 4.7 RLS [4 h]

**Row Level Security** is a Postgres feature where a table carries policies that filter which rows a role can see or change. With a policy like "`vendor_id` equals the current vendor setting", a query that forgets its `WHERE vendor_id = …` returns **nothing** instead of everything. It is the second wall behind the S1 relationship checks (P10 D157–D161).

**What to build**
- **Roles.** `market_migrator` owns the tables and runs migrations; it bypasses RLS. `market_app` is what the web process connects as: not the owner, `NOBYPASSRLS`, and only the grants it needs. `market_ro` is read-only for later reporting. Guiding question: does RLS apply to a table's *owner*? Read about `FORCE ROW LEVEL SECURITY` and decide how ownership is arranged.
- **Policies on vendor tables.** At minimum: order vendor groups and their lines, stock levels and movements, promotions and redemptions. Decide in ADR-009 which other tables need them and how non-vendor paths still work: the public catalog (published products from every vendor), a customer reading their own order across vendors, and ops working across vendors in the Admin. A vendor-scoped request that forgets to set the context must see **zero** vendor rows, never an error (fail closed).
- **`vendor_context(vendor_id)`**, a context manager used on every vendor-scoped path. It runs inside a transaction and sets `app.vendor_id` with **`SET LOCAL`**, so the value does not outlive the transaction. Guiding questions: what happens if `SET LOCAL` runs outside a transaction (try it and read the warning)? `SET` cannot take a bind parameter; which Postgres function does the same job and can? After a `SET LOCAL` transaction ends, what does `current_setting('app.vendor_id', true)` return on the *same* connection, and what does it return on a brand-new connection that never set it? Write the policy so that both cases give zero rows and never an error (read about the `missing_ok` argument and think about `NULLIF(…, '')` before a cast).
- **Membership is resolved per request** from `vendors_vendor_staff`, never baked into the token ([E5](README.md#e5-auth-evolution)).

**Pain-first A — the forgotten WHERE**
1. Create a test-only variant of a vendor selector with its `vendor_id` filter removed.
2. Run it as vendor B's staff, **connected as `market_app`**, inside `vendor_context(B)`.
3. Predict how many rows, and whose, each of three runs returns, then run them: as `market_app` inside `vendor_context(B)`; as the migrator role; and as `market_app` *without* entering `vendor_context()` (the target for this last one is zero vendor rows, fail closed). Save all three outputs to `docs/evidence/s02/rls-forgotten-where.log`, with one sentence on what the migrator run tells you about which role the tests must use.

**Pain-first B — the plain `SET` leak**
1. Implement `vendor_context()` with plain `SET` (the bug). Enable persistent connections (`CONN_MAX_AGE > 0`, or Django's psycopg connection pool option), and run one gunicorn worker so the connection is reused deterministically.
2. Request 1: vendor A's staff reads their groups. Request 2 on the same connection: a path that does not enter `vendor_context()`.
3. Predict which rows request 2 sees, then run it and record them. Save `rls-set-leak.log`.
4. Switch to `SET LOCAL`. Repeat. The target: request 2 sees zero vendor rows and returns a normal response, not a 500 (this is where the empty-string question above bites). Keep both variants as a test. **This test is re-run under PgBouncer transaction pooling in S10.**

**Acceptance criteria**
- The forgotten-`WHERE` test passes as the app role.
- The `SET` leak is reproduced (red) and fixed (green).
- A request without `vendor_context()` on a connection that previously ran one returns 0 vendor rows, not a 500; so does the same request on a fresh connection.
- Staff of vendor A get 404 for vendor B's group through every endpoint (the S1 permission matrix, extended).
- ADR-009 is written (section 8).

---

### 4.8 Python concurrency [1 h]

**Why this block exists.** You have just proved races with threads. The usual interview follow-ups are "Python has a GIL, so how can two threads race at all?" and "when do you use threads and when processes?". This hour answers both with your own numbers. Reread the old GIL demo first ([phase-2 D25](../../phase-2-concurrency-django-caching.md)). Work in `sandbox/`, not in `market`.

1. **The race does not care about the GIL.** Run the naive barrier race from 4.2 (stock 1, two buyers) once with two threads and once with two processes, each with its own database connection. Predict both outcomes, commit the prediction, then run. In `docs/evidence/s02/gil-race.md`, write two sentences: what the GIL serializes, and where this race actually lives.
2. **CPU-bound work: threads vs processes.** Take two CPU-bound functions: a pure-Python loop, and an `argon2-cffi` password hash (the hasher from S1, whose work happens in C; set its parallelism to 1 for this experiment so one hash uses one core). Run each one N times sequentially, through a `ThreadPoolExecutor` and through a `ProcessPoolExecutor` with 4 workers. Predict which combinations speed up, then measure wall time and record the 2 × 3 table.
3. **Five lines in the same file:** when `asyncio.to_thread` (which hands work to a thread pool) is enough for a blocking call made from async code, when you need a process pool instead, and what a C extension releasing the GIL changes. Python 3.13 also ships an experimental free-threaded build (PEP 703) [C]; say in one line why Atlas does not use it yet.

Async services arrive from S4 on; there this choice decides whether one slow call stalls the event loop for every other request.

**Acceptance criteria:** `gil-race.md` holds both committed predictions, the race outcomes, the 2 × 3 table and the five lines.

---

### 4.9 Drills + SD12 [3 h]

- **Drill hours (W7 and W9):** one SQL problem on your own schema (suggestions: the "movements sum equals level, must return 0 rows" integrity query; vendor-group totals per vendor per day; top promos by redemptions) or one DSA problem from [`../../dsa-problems.md`](../../dsa-problems.md); plus this stage's interview questions out loud.
- **SD12 (W8, week 2 of the stage):** see section 9.

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| Stock never goes below zero | `CHECK` on the level **plus** an atomic decrement (conditional update or row lock) | Two-buyer barrier test (one 201, one 409); a raw-SQL test that the `CHECK` rejects a negative value |
| Stock changes only through `stock_movements` | The inventory service is the only writer and writes level and movement in one transaction | Integrity query "movements sum ≠ level" returns 0 rows after the race suite |
| An order and its groups commit together | One `atomic()` block for the whole checkout | Forced failure after inserting groups leaves nothing behind |
| One key means one order | Unique key per scope; `INSERT … ON CONFLICT DO NOTHING RETURNING` in the checkout transaction | Concurrent double-click test: one order, identical responses; different body → 422 |
| Promo use never exceeds its cap | SERIALIZABLE + `@retry_on_serialization_failure` (or the alternative ADR-007 chooses) | 20-way concurrent test at cap − 1 |
| No cross-vendor rows, even with a missing `WHERE` | RLS policies; `market_app` is `NOBYPASSRLS` and not the owner; `SET LOCAL` via `vendor_context()`; policies that give zero rows, not an error, when the setting is empty or missing | Forgotten-`WHERE` test as the app role; `SET` leak test; reused-connection and fresh-connection tests without a context |
| Anticipated conditions return 409/422, never 500 | Domain errors and the Postgres codes `23P01`, `40001`, `40P01`, `55P03`, `57014` mapped explicitly | One test per condition. **Known violation until S4:** SMTP down during checkout |
| Locks are always taken in one global order | The lock-ordering rule you chose in 4.2 step 3, applied on every path that locks stock | 100-iteration opposite-order test, zero deadlocks |
| An order line's price never changes after checkout | Unit price snapshotted onto the line | Change the product price after checkout; the order total is unchanged |

## 6. Tests to write

- **Barrier race:** two buyers, one unit → exactly one 201 and one 409 (and the naive version kept behind a flag, red).
- **Multi-line all-or-nothing:** one short line rolls back every decrement.
- **Deadlock:** opposite-order carts deadlock with sorting disabled; zero deadlocks in 100 iterations with it enabled.
- **Write skew:** more than the cap at REPEATABLE READ; exactly the cap at SERIALIZABLE; retry counts logged.
- **Retry decorator and context manager:** unit tests for attempts, jitter bounds, final error, refusal to nest.
- **Idempotent replay:** concurrent double-click → one order, identical responses, run at the isolation level checkout uses; different body → 422; the Redis failure scenarios kept as documented reproductions.
- **Timeouts:** each of the three errors is raised in its scenario and mapped to a non-500 response.
- **RLS, run as the app role:** forgotten `WHERE`; `SET` leak red and green; no context on a reused connection and on a fresh one gives 0 rows, not a 500; cross-vendor 404s.
- **Fulfillment state machine:** every legal transition works; every illegal one returns 409; staff cannot move another vendor's group.
- **Hypothesis:** pricing properties, allocation sums, seed pinned.
- **Integrity queries** as tests: movements sum equals level; every order has at least one group; every group's total equals the sum of its lines minus its discount.
- **factory_boy** factories for carts, orders, groups, promos and stock.

## 7. CI changes

| Job | Gates |
|---|---|
| `concurrency` | Runs the race suite (barrier race, deadlock, write skew, idempotent double-click, RLS leak) **20 times**. A race test that passes once proves little; twenty passes in a row makes a flaky "fix" visible. It uses real commits and connects as the app role. |
| `test-integration` (extended) | Integration tests connect as `market_app`, with migrations applied as `market_migrator`, so RLS is live in CI |
| `migrations` (extended) | The role and policy migrations go up and down cleanly |

## 8. ADRs and documents

**ADR-007 — Isolation level per operation**
- *Questions:* for each operation (checkout stock decrement, promo redemption, fulfillment transition, catalog reads, reports), which isolation level, which locking strategy, which anomaly it prevents, what the retry policy is, and which timeouts apply. Present it as a table, and give it one extra row: *a duplicate idempotency key at the isolation level checkout runs at* (what the waiting duplicate gets, and whether the retry decorator turns it into a clean replay; see 4.4). Answer the "isolation is per transaction" question from 4.3. Record the per-role timeout values and why.
- *Numbers:* throughput and p95 of `FOR UPDATE` vs conditional update at the hot-offer rate from 4.2 (about 50 checkouts in flight); deadlocks before and after your lock-ordering fix; redemptions at REPEATABLE READ vs SERIALIZABLE; retries per successful checkout under SERIALIZABLE at your test concurrency.
- *Counter-arguments:* "just run everything SERIALIZABLE" (hint: argue from your retry counts in `docs/evidence/s02/write-skew-serializable.log` and what a retry costs on a hot row); "just lock the promo row" (it may be the simpler answer; say so if your numbers agree).

**ADR-008 — Idempotency store: Postgres, not Redis**
- *Questions:* what is stored, when, and with what scope; how concurrent duplicates behave; what the request hash covers; whether failed checkouts are stored; how long keys live (S5 sets ≥ 24 h).
- *Numbers:* the three Redis failure scenarios with what you observed; the latency the Postgres claim adds to checkout (median and spread).
- *Counter-argument:* "Redis is faster, and we are adding it anyway in S3." Hint: argue from `docs/evidence/s02/redis-idempotency.md`. Which property of the record matters more than speed, and what kind of data *is* Redis the right store for?

**ADR-009 — Multi-tenancy: shared schema + RLS vs schema-per-tenant vs database-per-tenant**
- *Questions:* which model and why for Atlas's Pareto-shaped vendors (many small, a few whales); which tables carry policies; how the public catalog, customer order history and ops Admin paths work alongside vendor policies; the role layout and table ownership; what happens when a vendor path forgets its context (it must fail closed); the pooled-connection rule (`SET LOCAL`, never `SET`) and the S10 re-test under PgBouncer.
- *Numbers:* the number of policies; the plan and timing of the vendor order list with and without its policy (RLS is not free: the planner adds the policy predicate); the leak test results.
- *Counter-arguments:* "RLS is hidden magic, and a forgotten context produces empty pages that look like bugs" (hint: what is the right way for a security boundary to fail, and which of your tests in `docs/evidence/s02/rls-forgotten-where.log` would catch the empty page?); "database-per-tenant is the strongest isolation" (hint: name the kind of tenant for whom it wins, then count what it costs in migrations and connections at Atlas's vendor count).

**`docs/perf/blocking-email.md`:** checkout p95 with 0 s and 2 s SMTP delay (ADR-002, 3 runs each), what happens with SMTP down in each send placement, and the line "fixed in S4".

**`docs/evidence/s02/gil-race.md`:** the Python concurrency experiment from 4.8.

## 9. System design session

**SD12 — Design a ticket-booking system** (W8, week 2 of the stage, **built**). Problem text: [`../../system-design-problems.md`](../../system-design-problems.md).
- *Built (your evidence):* the locked decrement from 4.2 (your race suite and the `FOR UPDATE` vs conditional-update numbers), and a constraint-based rejection like S1's commission `EXCLUDE`. The bank asks you to name which of the two generalizes better for 50,000 people buying 20,000 seats, and why. Ask yourself: are seats fungible like units of stock, or individually numbered? What does each approach lock, and what does the loser see?
- *Whiteboard (45 min, the six-step skeleton):* short-lived seat holds with an expiry and what happens to abandoned holds (your S2 holds have an expiry time but nothing sweeps them yet); a virtual waiting room that sheds load before it reaches the booking path.
- *Reuse from Atlas:* the checkout guarantees (section 3) and how you met them, the deadlock story, the idempotency key.
- *Later:* SD12 is revisited in S10 with a Redis gate, fenced holds and a 1,000-unit flash sale.

Save notes to `docs/sd/sd12.md`.

## 10. Interview questions this stage lets you answer

1. What does `FOR UPDATE` lock, and for how long? What does the waiting transaction see when it finally gets the row?
2. Show me the deadlock you produced. How did you fix it, and how do you know it is fixed?
3. Why doesn't REPEATABLE READ stop write skew? Show me the retry loop.
4. Why is idempotency in Postgres and not Redis?
5. How does RLS interact with a pooled connection?
6. How do you test a race deterministically?
7. Why can't a `CHECK` constraint stop the lost update in the naive checkout?
8. `FOR UPDATE` or `UPDATE … WHERE qty >= n`: which did you choose, and what did the numbers say?
9. What happens when two identical checkout requests arrive in the same millisecond?
10. Why `ON CONFLICT DO NOTHING RETURNING` instead of catching the integrity error?
11. What does each of your three timeouts protect against?
12. Walk me through checkout from the click to the 201: every step in order, and why it sits where it does. (Write this narration yourself once 4.7 is done; it is the answer to the guarantees in section 3.)
13. Why is the email still synchronous, and what did it cost? (Answered fully in S4.)
14. Why does an order line store its own price?
15. Shared schema with RLS, schema per tenant, or database per tenant: when does each win?
16. Python has a GIL, so how did two threads oversell? When do you reach for a process pool instead of threads?
17. At which isolation level does your checkout run, and what does a concurrent duplicate idempotency key get at that level?

## 11. Common mistakes to watch for

- Doing the stock check and the decrement as two separate statements (the classic TOCTOU, time-of-check to time-of-use, bug; P1 D19–D24).
- Believing a `CHECK` constraint protects against lost updates.
- Locking rows in whatever order each cart happens to list them.
- Choosing an isolation level without reproducing the anomaly it prevents (P4 D67–D71).
- Retrying inside the failed transaction, or retrying a function that has side effects such as sending email.
- Running everything at SERIALIZABLE "to be safe" and then fighting retry storms.
- Using an "if the key exists" check instead of a unique constraint (P9 D145–D149).
- Storing idempotency records in Redis (P9).
- Plain `SET` instead of `SET LOCAL` on a pooled connection (P10 D157–D161).
- Testing RLS as a superuser or as the table owner, so every policy is silently bypassed.
- Sending the email inside the transaction, so a mail failure rolls back a valid order (P3).
- Writing race tests inside a transaction-wrapped test case, where they can never fail.
- Caching stock for "performance": stale stock is an oversell (P4).
- Reading the product's current price when showing an old order (P1, P2).

## 12. How real companies differ

- **Idempotency by default.** Payment platforms make every mutating call idempotent at the infrastructure or client-library level rather than endpoint by endpoint (P9 named this). Atlas generalizes its store in S5 and applies it to every AtlasPay POST in S9.
- **Isolation in practice.** Most production OLTP systems run READ COMMITTED with explicit row locks and constraints, and use SERIALIZABLE only for narrow invariants. Reproducing the anomalies yourself is what lets you make that call deliberately.
- **Inventory at scale.** Large retailers often run a reservation service with TTL holds and a sweeper, and gate flash sales in memory before touching the database. Atlas adds the sweeper in S4 and the gate in S10, each after a measured need.
- **Multi-tenancy.** Shared schema plus RLS is common for SaaS with many small tenants; regulated or very large tenants often get dedicated databases. Your ADR-009 should say where Atlas would switch.
- **Email.** No production checkout sends email synchronously. You do it once, on purpose, to measure what the queue in S4 buys.

## 13. Deliberately not doing

| Item | Why not now | When |
|---|---|---|
| Payments | Checkout correctness first; payment protocols are their own stage | S5 (groups stay in `awaiting_payment` until then) |
| Celery, background email | The synchronous version has to hurt first, with numbers | S4 |
| Caching stock | Stale stock used for a decision is an oversell ("stale stock = oversell", P4) | Never; S3 lists stock on the never-cached list |
| Cross-vendor promos | Cross-vendor accounting is a project of its own (P10 deferred it too) | Not in Season 1 |
| Returns | No new backend lesson beyond what refunds and the cancel saga teach | Money side in S5 (refunds); cancel-a-vendor-group saga in S9 |
| Expiring holds automatically | Holds carry an expiry time, but the sweeper needs a scheduler | S4 (`FOR UPDATE SKIP LOCKED` sweeper) |
| In-flight 409, `Idempotent-Replayed`, 24 h retention | Stripe semantics are needed when AtlasPay takes money | S5 |
| PgBouncer | One process, few connections | S10 (the RLS leak test is re-run under it) |
| Guest carts and merge on login | The cart moves to Redis with merge on login | S3 |
| Tax computation | Prices are tax-inclusive in Season 1 | Not in Season 1 (fiscal receipts: S5 stretch) |

## 14. Stretch

Only after the must tier closes:
- **The foreign-key lock demo and a lock-mode matrix [1.5 h]:** inserting an order line that references an offer takes a lock on that offer row. In two `psql` sessions, hold `SELECT … FOR UPDATE` on the offer in A and insert an order line referencing it in B; repeat with a plain `UPDATE` of a non-key column (or `FOR NO KEY UPDATE`). Predict whether B blocks each time, then run, and record in `docs/evidence/s02/fk-key-share.md`. Which lock does Django's `select_for_update()` take by default, and what does `no_key=True` change? Then write a one-page table of which row lock modes (`FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE`) conflict, annotated with the Atlas operation that takes each.
- **`EXCLUDE` on promo validity windows [1 h]:** a vendor cannot have two active windows of the same promo code that overlap; concurrent test as in S1.
- **A stateful test for the fulfillment state machine [1 h]:** Hypothesis's rule-based state machine drives random sequences of transitions (by owners, by other vendors' staff, by ops) and checks after every step that no illegal state was reached and no other vendor's group moved.
- **A "who blocks whom" query [0.5 h]:** a saved SQL script over `pg_stat_activity` and `pg_blocking_pids()` that shows the blocking tree during the timeout demos; keep it in `scripts/` for the S6 on-call runbook.

## 15. Definition of done

- [ ] Barrier test: exactly one `201` and one `409` in 20 of 20 CI runs; the naive version is kept red behind a flag.
- [ ] `FOR UPDATE` vs conditional update compared with numbers; one chosen in ADR-007.
- [ ] The deadlock reproduced (log committed) and fixed (100 iterations, zero deadlocks).
- [ ] MVCC and isolation demos recorded, each with its committed prediction.
- [ ] The promo race holds: exactly the cap under concurrency.
- [ ] Double-click gives one order and identical responses at the isolation level checkout uses; the Redis failures are documented; the claim's latency cost is recorded.
- [ ] All three timeouts demonstrated and mapped to non-500 responses.
- [ ] Fulfillment state machine: every legal transition works, every illegal one returns `409`, and staff cannot move another vendor's group.
- [ ] Pricing strategies, Capped wrapper and Hypothesis properties green.
- [ ] The RLS forgotten-`WHERE` test and the `SET` leak test pass as the app role; a request without a context returns 0 vendor rows (not a 500) on a reused and on a fresh connection.
- [ ] Staff of vendor A get `404` for vendor B's groups through every endpoint (the extended permission matrix is green).
- [ ] `docs/evidence/s02/gil-race.md` complete (4.8).
- [ ] The email numbers are recorded in `docs/perf/blocking-email.md` and listed in `docs/deferred.md`.
- [ ] CI `concurrency` job (×20) green.
- [ ] ADR-007, ADR-008, ADR-009 merged; SD12 notes in `docs/sd/sd12.md`.
- [ ] `docs/hours.csv` has one row per block of this stage, with budget and actual.
- [ ] Postmortem paragraph written (use the budget-vs-actual numbers).
- [ ] 2 STAR stories in `docs/star/`: the deadlock; the Redis idempotency mistake.
- [ ] Tagged `v0.2`.

## 16. If you get stuck

- **Domain.** If the order and its groups end up half-written: where does your `atomic()` block begin and end, and does anything commit inside it? If movements and levels drift: which code path writes a level without a movement? Reread P1's event-log idea ([../python/01-stockpilot.md](../python/01-stockpilot.md), §6 and D19–D24) and P10's vendor-group checkout ([../python/10-atlasmarket.md](../python/10-atlasmarket.md), D163–D165).
- **Races.** If the naive race never fails: do both threads really start at the same moment, on separate connections, in transactions that commit? If the fixed race still oversells: is the check and the decrement truly one statement, or one locked read followed by the write? Reread [phase-1 D20–D21](../../phase-1-foundations.md) and P4 D67–D71 ([../python/04-wareflow.md](../python/04-wareflow.md), Stage 3).
- **Deadlock.** If you cannot produce it: is there a pause between the first and second lock? If the fix does not hold: do *all* code paths that lock stock follow your ordering rule, including single-line checkouts and the dev-only commands?
- **Write skew.** If SERIALIZABLE never raises `40001`: did the isolation statement run first in the transaction, and is the whole redemption (count and insert) inside that transaction? If retries loop forever: is the retry outside the transaction, with a maximum?
- **Idempotency.** If the duplicate creates a second order: is the claim inside the same transaction as the order, and is the key unique in the database (not just checked in code)? If the duplicate hangs: what is it waiting for, and when does that transaction end? Reread P9 D145–D153 ([../python/09-payflow.md](../python/09-payflow.md), Stages 1–2).
- **Timeouts.** If a timeout never fires: is the setting on the role your app connects as, and did you open a new session after changing it?
- **Pricing.** If Hypothesis finds a sum that is off by one tiyin: where does rounding happen, and does it happen more than once? Reread P2 D31–D39 ([../python/02-quickserve-pos.md](../python/02-quickserve-pos.md), Stages 2–3).
- **RLS.** If a policy never filters anything: which role are you connected as, and does that role own the table? If the `SET` leak does not reproduce: is the connection actually being reused between the two requests? If `SET LOCAL` seems to do nothing: are you inside a transaction? If the second request on a reused connection answers 500 with an "invalid input syntax" error, or a fresh connection fails with "unrecognized configuration parameter": what does `current_setting` return in each case, and does your policy cast it before checking for empty? Reread P10 D157–D161 ([../python/10-atlasmarket.md](../python/10-atlasmarket.md), §4).
- **Email.** If you are tempted to fix it now: don't. Record the numbers; they are the argument for S4. Reread P3 D42–D43 ([../python/03-peopleops.md](../python/03-peopleops.md), Stage 2).
- **Python concurrency.** If threads show no speed-up on argon2: is the hasher's own parallelism set to 1, and are you timing the hashing or the pool start-up? If processes are slower than sequential: how big is N compared with the cost of starting workers and pickling arguments?

<details>
<summary>Check your prediction (open only after you committed yours)</summary>

- **4.1, email placements.** Send inside the transaction: a mail failure rolls back a valid order, and the stock rows stay locked for the whole SMTP delay. Send after commit: the order exists, but the customer gets a 500, which invites a retry (and, without idempotency, a second order).
- **4.2 step 1, the naive race.** Two orders and final stock 0. The `CHECK` never fires, because each transaction wrote a legal value: a *lost update*, where one write silently overwrote the other.
- **4.2 step 1, the unguarded `UPDATE`.** The `CHECK` now catches the second buyer, but as an integrity error that surfaces as a 500, not a 409.
- **4.2 step 3, the deadlock.** After `deadlock_timeout` (1 s by default) Postgres aborts one of the two transactions with SQLSTATE `40P01`; the server log names both processes and the locks they wait for.
- **4.2 step 4, MVCC.** B is not blocked and sees the old value until A commits. **Isolation:** at READ COMMITTED the two reads differ; at REPEATABLE READ they do not.
- **4.3, write skew at REPEATABLE READ.** More than 100 redemptions and no error: each transaction saw 99 in its snapshot and inserted its *own* row, so no row was written twice and REPEATABLE READ had nothing to detect.
- **4.4, Redis as the store.** Kill after commit: the key is never marked done, so a retry either creates a second order or finds a key stuck "in progress" forever. Eviction and restart: the key is gone, and a retry creates a second order.
- **4.4, the concurrent duplicate.** At READ COMMITTED its `INSERT … ON CONFLICT DO NOTHING` waits on the first transaction's uncommitted unique-index entry, then returns no row once the first commits (or becomes the executor if the first rolled back). At REPEATABLE READ or SERIALIZABLE it fails with `40001` once the first commits, because the conflicting row is not in its snapshot (the Postgres docs note that the skip-on-conflict behaviour is "only the case in Read Committed mode"). It then replays cleanly only if `@retry_on_serialization_failure` wraps the claim.
- **4.7 A, the forgotten `WHERE`.** Inside `vendor_context(B)`: only B's rows, although the query has no vendor filter. As the migrator: every vendor's rows, because the owner (and a `BYPASSRLS` role) skips the policies. Without a context: zero rows, if the policy handles an empty setting.
- **4.7 B, the plain `SET` leak.** Request 2 sees vendor A's rows: the setting survived on the reused connection. With `SET LOCAL`, the value reverts to an empty string (not "unset") after the transaction, which is why a naive `::bigint` cast in the policy turns request 2 into a 500.
- **4.8, the GIL.** The race happens with threads and with processes alike: the GIL serializes Python bytecode inside one process, but the race is between two database transactions. The pure-Python loop speeds up only with processes; the argon2 hash speeds up with threads too, because the C code releases the GIL while it works.

</details>

Previous: [Stage 01 — Layered monolith](stage-01-layered-monolith.md) · Next: [Stage 03 — Redis, auth hardening, bot v1](stage-03-redis-auth-bot.md).
