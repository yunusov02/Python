# Stage 03 — Redis, auth hardening, bot v1

| | |
|---|---|
| **Weeks** | W10–W12 (3 weeks) |
| **Hours** | 36 must + 5 stretch (41 total). The must tier includes a 2 h aiogram ramp (§4.0). |
| **Architecture at start → at end** | `market` as a layered monolith (identity, vendors, catalog, inventory, cart, ordering, promotions) on PG17 with RLS, plus the S3-compatible object store (Garage) → `market` + **`bot`** (a new client, not a split), the cart moved into Redis, two Redis instances (`redis-cache`, `redis-state`), and an ephemeral Valkey Cluster lab |
| **New technologies** | Valkey 9.1 through the redis-py client, Lua scripting, Valkey Cluster (hash slots, hash tags), aiogram 3.31.0 (Bot API 10.3), oha (constant rate, latency correction), locust, fakeredis, freezegun |
| **Portfolio tag** | `v0.3` |
| **Old-spec theory to read** | [P2 D31–D39](../python/02-quickserve-pos.md) (cache-aside D34, benchmarking D35, invalidation audit D36, simplejwt D37, DRF throttling internals D38); [P5 D85–D90](../python/05-carepoint.md) (refresh rotation and family revocation, login protection); [P9 D151–D153](../python/09-payflow.md) (Lua token bucket, "Redis for limits, never for idempotency"); [Proj27 D171–D173](../../phase-6-capstone.md) (the multi-instance limiter proven correct, memory at 100k keys); bot extensions [P2 Wk7 §20](../python/02-quickserve-pos.md) and [P3 Wk9 §18](../python/03-peopleops.md) |

Version pins are as of 2026-09. Re-check them with `scripts/compat_check.sh` before you start (ADR-001). aiogram 3.29.x was yanked, so pin 3.31.0 exactly.

> **What this stage is really for.** Redis is where "fast" and "correct" collide. By the end you should be able to show, with numbers, that a cache which lies about a price is worse than no cache, that a counter shared by 12 processes needs server-side atomicity, and that eviction and persistence settings are correctness settings, not tuning knobs. The Telegram bot is the second client of the service layer. It proves the business rules live in `market` and nowhere else.

---

## 1. The problem this stage starts from

S1 and S2 left four things broken or missing. You recorded most of them yourself.

**In business terms:**
- Browsing is slow on the pages people actually visit. Worldgen traffic is Pareto-shaped: a few categories and products get most of the views. Every one of those views still goes to Postgres.
- Login can be brute-forced. The S1 login limiter is a dictionary inside each gunicorn worker, so with 4 workers an attacker gets 4× the allowed guesses. You wrote that number down in S1. Adding containers makes it worse.
- "Log out" does not log anyone out. S1 issues simplejwt HS256 access and refresh tokens with no rotation, and you recorded the missing rotation as a gap. A stolen refresh token keeps working until it expires.
- Customers in Uzbekistan sign in with a phone number (S1 already normalizes +998 numbers), and many ask about their orders in a messenger rather than on a website. The platform has neither phone-OTP login nor a Telegram channel.

**In engineering terms:**
- The catalog p95 is high under repeated reads, which is the S2 exit condition in the [README §5.1 evolution table](README.md#51-the-evolution-table). Nothing sits between the read path and Postgres.
- The limiter's state is per process. It has to move to a store that all processes share, and that store must never silently forget counters.
- Refresh tokens have no server-side state, so there is nothing to revoke.
- The cart is a set of Postgres rows (S2). Every add-to-cart is a write on the primary, and abandoned anonymous carts pile up. Cart data is ephemeral and high-churn. Losing a cart is annoying but never wrong, because checkout re-validates everything. So the cart can move to Redis. Idempotency keys cannot (S2, ADR-008).

---

## 2. Outcomes — what exists when the stage is finished

1. Catalog reads (product detail, category listing, facet filters) go through **cache-aside** with namespaced, versioned keys. Cold and warm p95 are recorded under the ADR-002 protocol.
2. An **invalidation audit** table lists every path that writes a price. Each path has a test proving it invalidates.
3. A locust run shows the **stampede** (a DB spike when a hot key expires), and a second run shows the fix holding: single-flight, TTL jitter and stale-while-revalidate.
4. A barrier test reproduces the **stale-set race**, and the fix (delete after commit plus versioned keys) turns it green.
5. Two Redis instances run in Compose. `redis-cache` uses allkeys-lru with no persistence. `redis-state` uses noeviction with AOF everysec. (RDB = point-in-time snapshots of the whole dataset, written on a schedule; AOF = an append-only log of every write, replayed on restart, which `everysec` fsyncs once a second.) Evidence shows why: limiter keys evicted on a shared LRU instance, and lost carts counted after `kill -9` under RDB and under AOF.
6. The **cart** is a Redis hash with a TTL, merged on login. Checkout still reads prices from Postgres.
7. A **Lua sliding-window limiter** holds across 3 containers × 4 workers = 12 processes. The pain path (in-memory on 4 workers, then 3 containers, then INCR + EXPIRE, then GET/SET, then Lua) is committed as evidence, with a prediction committed before each run.
8. Limiter classes behave as E10 says when `redis-state` is down: login **degrades** to the Postgres per-account counter and raises an alert (the per-IP limit is lost for that window), OTP fails closed with a 503, catalog fails open with an alert.
9. `docs/rate-limit-algorithms.md` compares fixed window, sliding log, sliding counter, token bucket and leaky bucket on memory at 100k keys and on accuracy against a fixed request schedule.
10. **Refresh rotation with family reuse detection**, hashed storage, logout-everywhere, a `jti` denylist in `redis-state`, and phone-OTP login with a hashed OTP and 5 attempts.
11. A **Valkey Cluster lab** (3 masters + 3 replicas) shows CROSSSLOT and the hash-tag fix. A failover table records what each limiter class actually did while a master failed over under load.
12. **`services/bot`** (aiogram 3.31, polling) links an account with `/start <one-time code>`, lists `/orders`, runs a "track my order" FSM on `RedisStorage`, and throttles inbound updates. It calls `market` only through internal REST with a static service token. A short aiogram ramp note (`docs/learning/aiogram-ramp.md`) comes first.
13. ADR-010, ADR-011 and ADR-012 are written with numbers. SD2 and SD3 are done. The stage is tagged `v0.3`.

---

## 3. Architecture at the end of the stage

```
   browsers / curl / locust / oha                        Telegram Bot API
             |                                             ^        |
   +---------+-----------+----------------+                |        | getUpdates (long polling)
   v                     v                v                |        v
 market web #1      market web #2     market web #3     +------------------+
 gunicorn x4        gunicorn x4       gunicorn x4       | bot (aiogram)    |
   |  \                  |               /  |           | routers, FSM,    |
   |   +-----------------+--------------+   |           | throttle mw      |
   |          internal REST <---------------+-----------+ static svc token |
   |                                        |           +--+---------------+
   v                                        v              |
+-----------+   +-----------------+   +-------------------+ |   +----------+
| PG17      |   | redis-cache     |   | redis-state       |<+   | object   |
| market    |   | allkeys-lru     |   | noeviction        |     | store    |
| RLS, idem |   | no persistence  |   | AOF everysec      |     | (Garage) |
| refresh   |   | cache:*         |   | rl:* lock:* fsm:* |     +----------+
| families  |   | (lossy is fine) |   | bot:* cart:*      |
+-----------+   +-----------------+   | otp:* jti:*       |
                                      +-------------------+

 labs profile (ephemeral, weekend block):
   Valkey Cluster  3 masters + 3 replicas  <-- Lua limiter under a master failover
```

**What changed and why:**
- **Two Redis instances, not one.** `maxmemory-policy` and persistence are set per instance. A cache wants to evict and does not care about restarts. Limiter counters, FSM state and carts must not be evicted, and should survive a restart where that is cheap. One instance cannot serve both, and you will prove it in §4.2. The rule for every later key: if losing it is only a miss, it goes to `redis-cache` (S8's semantic cache `sc:` follows this rule); if losing it breaks a rule, it goes to `redis-state`.
- **Logical Redis databases (`SELECT 1`) do not solve this.** They share one memory limit and one eviction policy. Keep that answer ready for ADR-011.
- **`market` web runs as 3 containers.** This is not a scaling decision. It is the test rig that makes the limiter pain visible: 3 × 4 = 12 processes.
- **The bot is a new deployable, not a split.** Nothing leaves `market`. The bot is a thin client with no database and no business logic (E6). Its only state lives in `redis-state`.
- **Refresh families live in Postgres, in `identity` tables.** The access-token `jti` denylist lives in `redis-state`. The difference is deliberate. Losing a family would let a stolen refresh token live on. Losing the denylist on a restart re-opens a window no longer than one access-token lifetime. ADR-010 or ADR-012 should say this in one sentence.
- **Idempotency stays in Postgres (S2, ADR-008).** Nothing in this stage moves it. Having Redis in the stack is exactly when someone will suggest it.

---

## 4. Build plan

A suggested order across the three weeks. The weekend blocks hold the tasks that need uninterrupted state. Log your actual hours per block in the hours log (see [schedule-and-cuts.md](schedule-and-cuts.md) §1): at B1 you compute actual ÷ budget from it and re-plan with that ratio.

| When | Work |
|---|---|
| W10 weekdays | 4.1 cache-aside, the invalidation audit and its tests; 4.3 cart |
| W10 weekend | 4.1 baseline runs (no cache, cold, warm), stampede and stale-set under locust; 4.2 eviction and `kill -9` runs |
| W11 weekdays | 4.4 limiter steps 1–6 and the algorithms doc; 4.5 auth hardening |
| W11 weekend | The 12-process limiter run; the fixed-schedule and 100k-key memory runs; SD2 paper design |
| W12 weekdays | Finish 4.5; 4.0 aiogram ramp; 4.7 bot v1 |
| W12 weekend | 4.6 Cluster lab with the failover under load; SD3 paper design |

### 4.0 aiogram ramp [2 h, must]

**Why this exists.** §4.7 is your first aiogram service. If you did not build the optional bot extensions in P2 Wk7 and P3 Wk9, you have never seen aiogram's update pipeline, and the bot block would turn into reading the docs under time pressure. Do this ramp in W12, in the session right before §4.7.

**What to do:**
1. **Read (about 1 h)** the aiogram 3 docs at [docs.aiogram.dev](https://docs.aiogram.dev/en/latest/):
   - Dispatcher and Router: how an update travels from polling to a handler, and what `include_router` does;
   - filters: `Command`, the magic filter `F`, and what happens when no handler matches;
   - finite state machine: `StatesGroup`, `FSMContext`, and the storages page (`MemoryStorage`, `RedisStorage`, key builders);
   - middlewares: outer vs inner scope, and which one runs before the filters;
   - testing: `Dispatcher.feed_raw_update()` and calling handlers with `AsyncMock`.
   Then skim the Bot API pages on [`getUpdates`](https://core.telegram.org/bots/api#getupdates) (what `offset` does, and why only one poller may run) and [deep linking](https://core.telegram.org/bots/features#deep-linking).
2. **A throwaway toy bot (about 45 min)** on a dev token from @BotFather, in polling mode, outside the Atlas repo or on a scratch branch: one command, one router, a two-state FSM on `MemoryStorage`, and one outer middleware that logs the update type. Write one test that pushes a raw update through `feed_raw_update` with the network disabled.
3. **A one-page note (about 15 min)** in `docs/learning/aiogram-ramp.md`: an ASCII diagram of an update's path through outer middleware → router → filters → inner middleware → handler, where FSM state is keyed (which ids?), and one sentence on where a throttling middleware belongs and why.

**Acceptance criteria:**
- The toy bot answered a command on a real dev token.
- The toy test passes with the network disabled.
- The note has the diagram and answers the two questions.

### 4.1 Cache [7.5 h, must]

**Why this exists.** You add a cache only after a measured number says reads are slow. Then you spend more time proving the cache never lies than you spent building it. QuickServe's lesson (P2 D36) was that "the invalidation audit matters more than the cache". A cache with one uninvalidated write path fails silently.

**Unattended time in this block:** about 2.3 h. The baseline is 3 conditions (no cache, cold, warm) × 3 endpoints × 3 runs × ~4 min (a 60 s warm-up plus a 3-minute run, if that is your ADR-002 run length) ≈ 1.8 h, plus about 30 min of locust stampede runs. Schedule this in the weekend block.

**What to build:**
1. **Baseline first.** Load-test the public catalog endpoints: product detail, category listing (keyset page 1), and one facet filter. Use oha at a fixed rate with latency correction (`-q <rate> --latency-correction`), so each request's latency is measured from when it *should* have been sent and coordinated omission cannot flatter the tail. Run it under the ADR-002 protocol: fixed container CPU/memory limits, 60 s warm-up, at least 3 runs, median and min–max, p95/p99 from HDR histograms.
   - Define "cold" precisely in the evidence file. A reasonable definition: warm the process and connection pool with the cache disabled, then flush `redis-cache` and measure.
   - Measure again with the cache warm. Report both numbers, never only the flattering warm one.
2. **Cache-aside.** Check the cache, fall back to the DB on a miss, then populate with a TTL.
   - Keys are namespaced under `cache:` and include a version component, for example `cache:catalog:product:<id>:v<n>`. Exactly how `<n>` is produced is your design decision (see step 5).
   - Values hold what the serializer returns. Money stays integer tiyin (ADR-006), never a float, even inside a cached JSON blob.
   - Log hit or miss as a structlog field on every lookup.
3. **Invalidation audit.** Write a table in `docs/perf/s3-invalidation-audit.md` listing every code path that can change a price or anything else a cached payload shows. At minimum:

   | Write path | Where it lives | How it invalidates | Test |
   |---|---|---|---|
   | Vendor API updates an offer price | `catalog` service layer | ? | ? |
   | Ops edits a price in Django Admin | Admin `save_model` or form | ? | ? |
   | Catalog import command | management command (it becomes a Celery task in S4) | ? | ? |
   | Bulk price-adjust management command | management command | ? | ? |

   Search the code for writes to the price columns (`.update(`, `bulk_update`, raw SQL, `F()` expressions). Any path you find later goes into the table with its own test.
4. **Stampede.**
   - Give one hot key (a top category listing) a short TTL and run locust with worldgen traffic.
   - locust shapes the traffic, but it is a closed-loop tool with its own rounded percentiles, so never quote its p99 in an ADR. Run a constant-rate oha probe against the hot endpoint alongside it, and report the p99 from that probe. Cross-check it against the request durations in your structlog output.
   - Watch the DB at the moment the key expires. Use `pg_stat_statements` call deltas or the Postgres log: Prometheus arrives in S6.
   - Then add three fixes, one at a time, re-measuring after each:
     - **single-flight**: only one worker recomputes a missing key, under a short `lock:` key, while the others wait briefly or serve stale;
     - **TTL jitter**: randomize expiries so hot keys do not expire together;
     - **stale-while-revalidate**: keep serving the old value past its soft expiry while one worker refreshes it.
5. **Stale-set race.**
   - The interleaving: reader A misses and reads the old price from the DB. Writer B commits a new price and deletes the key. Reader A then writes the old price into the cache, and it stays wrong until the TTL expires.
   - Reproduce it deterministically with a barrier test that forces this exact order.
   - Fix it with delete-after-commit (`transaction.on_commit`) plus versioned keys, so a slow reader can only populate a version nobody will read.
6. **The never-cached list** goes into ADR-010: stock used for decisions, balances, payment state and order state. Stale stock means oversell (P4). A stale balance or payment state is simply a wrong answer.

**Pain-first exercises.** For each row, write your prediction into the evidence file and commit it, then run. Compare afterwards with "Check your prediction" in §16.

| Do this first | Look at and record | Record in |
|---|---|---|
| Benchmark with no cache at all, then cold, then warm | p95/p99 for each condition, side by side | `docs/evidence/s03/cache-p95.csv` (+ ADR-002 metadata: worldgen seed, SHA, image digests, CPU, limits) |
| Expire a hot key under locust with no protection | DB calls per second and the probe's p99, on one time axis with the expiry marked | `docs/evidence/s03/stampede-before.png`, `stampede-after.png`, and DB call deltas |
| Run the barrier test before the fix | The cached price vs the committed price after the writer finishes | `docs/evidence/s03/stale-set-red.log`, then green |
| Change a price through each write path before the audit exists | For each path, the cached price vs the DB price one second later | The audit table, with any path that was missing |

**Acceptance criteria:**
- Cold and warm p95/p99 are recorded under ADR-002.
- Every row in the audit table has a passing test.
- The stampede fix keeps DB calls per second flat through a hot-key expiry under the same locust profile.
- The stale-set barrier test is green, and it fails again if you remove the on-commit delete (try it once).
- A test proves no never-cached item is read through the cache helper.

### 4.2 Redis operations [2.5 h, must]

**Why this exists.** QuickServe asked you to *write* about eviction and persistence (P2 D37–D39). Here you make both fail on purpose. The lesson is that `maxmemory-policy` decides whether your security limits exist.

**What to build and observe:**
1. **One shared LRU instance (the wrong setup, on purpose).**
   - Run a single Valkey with a small `maxmemory` (your choice, small enough to fill in a minute) and `allkeys-lru`. Put both the cache and a Redis-backed limiter on it (the naive one from §4.4 step 3 is fine).
   - Predict what happens to the limiter while the cache fills, and commit the prediction.
   - Run locust over the long tail of products to fill the cache. At the same time, run a brute-force script against login.
   - Watch `evicted_keys` in `INFO stats`, `EXISTS` on the limiter key, and the number of attempts admitted.
   - Record the admitted attempts against the configured limit in `docs/evidence/s03/eviction-reset.log`. It becomes one of this stage's two STAR stories (§15).
2. **The split.**
   - `redis-cache`: allkeys-lru, no RDB, no AOF.
   - `redis-state`: noeviction, AOF with `appendfsync everysec`.
   - Think through what noeviction means. When `redis-state` is full, writes fail with an OOM error instead of silently dropping keys. Your code must treat that error as "limiter store unavailable" and apply the class's fail mode (§4.4). Loud failure is the point.
3. **`kill -9` and lost carts.**
   - Write carts at a steady rate, each carrying a sequence number. Kill the Redis container with SIGKILL, restart it, and count the missing sequence numbers.
   - Do it three ways: RDB only with the default save points, AOF everysec, and (out of curiosity) AOF always. Predict the lost count for each mode before the first kill.
   - Record the counts in `docs/evidence/s03/kill9-carts.csv`.
   - Whatever the numbers, ask what this experiment actually tested. A process crash is not an OS crash. What has already reached the kernel when the process dies, and what does `fsync` protect against that `kill -9` never triggers?
4. **No `KEYS` in code.** Valkey runs commands one at a time, so one O(N) command such as `KEYS` stalls every client while it runs. Add a test or lint rule that fails on `KEYS` anywhere in application code, and use `SCAN` with a COUNT where you need to iterate. Measuring the stall itself is a stretch item (§14).

**Acceptance criteria:**
- The eviction reset is reproduced and recorded.
- Both instances run in Compose with their configs committed.
- The `kill -9` table has all three rows.
- No code path uses `KEYS` (a test or lint rule greps for it).

### 4.3 Cart [1.5 h, must]

**Why this exists.** The cart is the textbook case for Redis-as-state: high write rate, short life, tied to one user, and cheap to lose. It is also the place to practise saying what Redis must never hold.

**What to build:**
- A Redis hash per cart in `redis-state` with a TTL that slides on activity. The hash holds offer ids and quantities only, never prices.
- Keys use the glossary's `cart:` prefix. Anonymous carts are keyed by a cart id from a cookie (`cart:anon:<id>`). Logged-in carts are keyed by user, with the user id in a hash tag (`cart:{user}`, per E3), so the Cluster lab can host carts later without CROSSSLOT.
- **Merge on login.** Define the rule before coding it: what happens when the anonymous and the logged-in cart hold the same offer? Test the rule, including the case where the anonymous cart has already expired.
- Checkout (S2) reads the cart from Redis. It still snapshots prices from Postgres, holds stock in Postgres and uses the Postgres idempotency store. Nothing about checkout correctness moves.

**Acceptance criteria:**
- The merge rule is tested.
- The TTL slides on activity.
- Checkout passes the full S2 race suite (the ×20 `concurrency` job) with the Redis cart.
- The `kill -9` numbers from §4.2 are quoted in the cart note.
- A written sentence says why a lost cart is acceptable and a lost idempotency key is not.

### 4.4 Rate limiter [6.5 h, must]

**Why this exists.** This is the "Lua limiter path" on the never-cut spine (see [schedule-and-cuts.md](schedule-and-cuts.md)). Interviewers like it because every naive version looks correct in a unit test and fails only under concurrency or partial failure. You will build each wrong version and watch it fail before you write the right one.

**Unattended time in this block:** about 45 min (the 20-run distribution in step 4, the 12-process runs, and the fixed-schedule runs for the algorithms doc). Schedule the 12-process and fixed-schedule runs in the weekend block.

#### The pain path, step by step

Run every step against the same fixed test. With a limit of `L` attempts per window for one IP and one account, fire `N > L` requests concurrently, spread across all processes. Assert how many were admitted.

To keep the expected number exact, start each run from an empty state, so the previous window is empty (why does that matter for the sliding counter?). Spread the load yourself: the test harness can round-robin across the three containers' ports, because there is no proxy until S6.

**Before every step, write the admitted count you expect (or the failure you expect) into `docs/evidence/s03/limiter-pain.csv` and commit it. Then run.** The expected outcomes are in §16 under "Check your prediction"; open them only after the run.

**Step 1 — Re-measure S1's 4×.**
- Run the in-memory limiter under one container with gunicorn at 4 workers.
- Record the admitted count out of `N`.
- Compare it with S1's `docs/evidence/s01/limiter-4x.csv`, then record it as the first row of `docs/evidence/s03/limiter-pain.csv`.

**Step 2 — Scale to 3 containers.**
- Run `market` web as 3 containers × 4 workers.
- Record the admitted count as the second row. Ask what this number does as your deployment grows, and who benefits from that.

**Step 3 — Move the counter to Redis naively: INCR, then EXPIRE.**
- The obvious code increments the counter and, if the result is 1, sets the expiry. It looks atomic. Is it?
- Inject a failure between them: a fault hook that raises after INCR, or kill the worker at that line.
- Inspect the key afterwards with `TTL`, then send that IP's or account's next request a few windows later.
- Record what you found and how you produced it in `docs/evidence/s03/incr-expire-ttl.log`.

**Step 4 — Try GET, compare, then SET.**
- Read the count, compare it with the limit, then write count + 1.
- Run it under the concurrent barrier 20 times and record the distribution of admitted counts.
- Then explain the result on paper as an interleaving of two processes. Which S2 bug has the same shape?

**Step 5 — Lua sliding-window counter.**
- Move the whole decision into one Lua script on `redis-state`.
- Why this works: the server runs a script as one unit, and no other command interleaves with it. Reading, deciding, incrementing and setting the TTL happen in one step, so neither step 3's TTL-less key nor step 4's lost update can occur.
- Questions to answer before writing it:
  - Which keys does the script touch? Pass them in `KEYS`, never build key names inside the script. Why will the Cluster lab (§4.6) punish you if you do?
  - Where does "now" come from: the caller's clock or the server's `TIME`? What happens with 12 processes whose clocks disagree by 300 ms?
  - What does the script return, so the caller can build `Retry-After` without a second round trip?
  - What happens when the script's SHA is not in the server's cache (`NOSCRIPT`), for example right after a restart or failover? What does redis-py's script helper do about it?
- Re-run the step-1 test on 12 processes. The test asserts exactly `L` admitted, every run.
- Record the final row. This is the number that closes the S1 gap.

**Step 6 — Classes and failure modes.**
- Kill `redis-state` during each class's test and observe what the class does. E10 says what it must do. Your job is to make the code agree, then prove it.

| Class | Key | Algorithm | If `redis-state` is down | Response |
|---|---|---|---|---|
| Login | IP + account | Sliding counter (Lua) + exponential lockout | **Degraded fallback + alert**: the per-account S1 `login_attempts` lockout in Postgres keeps working; the per-IP limit is lost until `redis-state` returns. Never fail open on the account dimension. | 429 + `Retry-After`, with the same generic body as a failed login (S1 enumeration rule) |
| OTP send / verify | Phone + IP; attempts per OTP | Fixed window + attempt counter | **Fail closed (503)** | 429 |
| Public catalog | IP / user | Sliding counter | **Fail open + alert** | 429 |

  - "Alert" means a structured ERROR log event plus a counter in S3, for both the login fallback and the catalog class. S6 wires them to Alertmanager.
  - Be precise with the words. *Fail closed* rejects everything (OTP). *Fail open* admits everything (catalog). Login does neither: it **degrades** to a weaker limiter in a second store. Say which attack the degraded mode still stops, and which one it lets through (one IP spraying many accounts?). ADR-012 records that answer.
  - Why the difference between classes? Availability of browsing is worth more than a perfect limit. A login or OTP endpoint without a limit is an open door, and for OTP it is also a bill: every send is a paid SMS. Search for "SMS pumping".

#### The five algorithms, compared conceptually

You build two of these now: the sliding counter for login and catalog, and the fixed window for OTP. The token bucket arrives for AtlasPay API keys in S9 and the leaky bucket for the bot's outbound pacer in S4. Nginx `limit_req` (S6) is also a leaky bucket. You still need to understand all five, because SD2 and every rate-limiter interview ask you to choose between them.

| Algorithm | State per key | What it gets right | What it gets wrong | Where Atlas uses it |
|---|---|---|---|---|
| **Fixed window** | One counter per key per window | Cheapest; a limit users can understand ("5 codes per 10 minutes") | Boundary burst: up to 2 × L in a short span straddling two windows | OTP send limit (S3) |
| **Sliding log** | One timestamp per request inside the window (a sorted set) | Exact | Memory grows with the limit: 100k keys × L entries each | Stretch only (a sliding-log limiter, 1 h) |
| **Sliding window counter** | Two counters (current and previous window), weighted by overlap | Near-exact with O(1) memory; no boundary burst | Approximate: it assumes the previous window's requests were spread evenly | Login and catalog (S3) |
| **Token bucket** | Token count + last refill time | Allows controlled bursts up to capacity, with a steady average rate | Needs a refill rule and careful time handling; the burst size is a product decision | AtlasPay per-key tiers (S9), outbound calls to providers (S5), AI token budgets (S8) |
| **Leaky bucket** | A queue or next-allowed time, drained at a fixed rate | Smooth output; can *delay* instead of *reject* | Adds latency; a full bucket still has to reject or queue | Nginx `limit_req` (S6), the bot's outbound pacer (S4) |

Two ideas to take from the table:
- **Reject or delay?** Token and leaky buckets are close relatives. The practical difference is whether excess requests are rejected (a limiter protecting you from a client) or queued (a pacer protecting a third party from you). The bot pacer in S4 must never drop a notification, so it delays.
- **Accuracy costs memory.** Only the sliding log is exact, and it pays for that with memory proportional to the limit.

**`docs/rate-limit-algorithms.md` requirements (Proj27 D171–D173 is the model):**
1. **A fixed request schedule written before any run, with expected outcomes for each algorithm.** For example, with a limit of 10 per 60 s: 10 requests at t=59 s, then 10 at t=61 s, then one every 5 s. Write what each algorithm should admit, then run it and compare. If an actual count differs from your expectation, explain which of the two was wrong.
2. **Memory at 100k tracked keys.** Measure with `MEMORY USAGE` on sample keys and `INFO memory` totals:
   - measure the fixed window and the sliding counter, which you built;
   - measure the token bucket with a small bench-only script (S9 reuses the idea);
   - for the sliding log and the leaky bucket, compute the expected size from the key structure and show the arithmetic;
   - measure the sliding log too if you do the stretch sliding-log limiter.
3. A paragraph per algorithm on when you would choose it, tied to the E10 row that uses it.

**Acceptance criteria:**
- The pain CSV has a committed prediction and a measured row for each of steps 1–5 (step 4 as a 20-run distribution), and the Lua row admits exactly `L`.
- The 3-container limiter test is green in CI (§7).
- Each class's down-store behaviour is proven by a test.
- 429 responses carry `Retry-After`, and login's body is byte-identical to an ordinary failed login.
- The algorithms doc has the schedule table and the memory table.

### 4.5 Auth hardening [4.5 h, must]

**Why this exists.** S1 left refresh tokens that cannot be revoked. CarePoint taught the answer (P5 D85–D90): rotate on every use, and treat reuse of an old token as proof of theft.

**What to build:**
1. **Refresh rotation with families.**
   - Every refresh returns a new refresh token and invalidates the old one.
   - All tokens descended from one login share a `family_id`.
   - Presenting an already-rotated token revokes the whole family. The attacker and the victim are both logged out, and that is the correct outcome.
   - Store tokens hashed. A table shape to start from (from P5):

     ```
     refresh_tokens(id, user_id, token_hash, family_id,
                    issued_at, expires_at, revoked_at, replaced_by)
     ```

   - Guiding question: simplejwt ships rotation and a blacklist app. What does it give you, and what does it not give you (family revocation)? Decide whether you extend it or replace its refresh view, and record why in the auth notes.
2. **Logout and logout-everywhere.** Logout revokes the current family. Logout-everywhere revokes every family for the user.
   - Guiding question: after logout-everywhere, what about access tokens already issued on other devices? The denylist only knows the `jti`s it has been told about. Decide your answer, and write down the exposure window in minutes.
3. **`jti` denylist in `redis-state`** (glossary prefix `jti:`). On logout, the current access token's `jti` goes into the denylist with a TTL equal to the token's remaining lifetime.
   - Explain in one sentence why this is acceptable in Redis while the families are not: losing it re-opens at most one access-token lifetime.
4. **Phone-OTP login.**
   - A 6-digit code sent to the normalized +998 phone, stored hashed with a short TTL under the `otp:` prefix in `redis-state`, allowing 5 verification attempts before the code dies. The send and verify limits come from §4.4's OTP class.
   - Sending goes through an `SmsSender` port (a Protocol) with a fake adapter that writes to the log. No real SMS provider in Season 1.
   - Guiding question: a 6-digit code has only 10^6 values. What does a plain SHA-256 of it protect against if the store leaks? What would a keyed hash with a server-side secret change? Which is your real defence, the hash or the attempt counter?
5. **Expiry tests with freezegun.** Test an access token exactly at expiry with your leeway, a refresh token one second after expiry, an OTP at TTL, and a family revoked mid-rotation.

**Pain-first exercise:**
- Before building families, log in, capture the refresh token, "log out", and refresh with the captured token.
- Observe a fresh access token issued to a logged-out session.
- Record the request/response pair in `docs/evidence/s03/refresh-replay-before.log`. After the fix, the same replay revokes the family: `refresh-replay-after.log`.

**Acceptance criteria:**
- The replay test revokes the family.
- Logout-everywhere is tested across two simulated devices.
- OTP brute force stops at 5 attempts, and at the send limit.
- OTP returns 503 when `redis-state` is down.
- No refresh token is stored in clear (a test reads the table).

### 4.6 Redis Cluster lab [3.5 h, must]

**Why this exists.** Sharding comes back three times in Atlas: the webhook ring (S9), Citus (S12) and Mongo (S12). Redis Cluster is the smallest place to learn the vocabulary: hash slots (16,384 of them), which node owns a key, why a multi-key operation must stay on one node, and what a failover looks like to the client. It also tests §4.4 for real: does the limiter behave during a failover the way ADR-012 claims?

**What to build (a Compose `labs` profile; ephemeral; weekend block):**
1. A Valkey Cluster with 3 masters and 3 replicas. Your app connects through redis-py's cluster client, which follows `MOVED` and `ASK` redirects.
2. **Multi-key scripts on a cluster.** Run your unmodified multi-key Lua sliding counter (it touches the current and the previous window keys) against the cluster. Predict first: will it run, and if not, what will the error say?
   - Record the error you get.
   - Then fix it. Guiding questions: which part of a key name does Redis Cluster hash to pick a slot? What syntax makes two different keys hash to the same slot? Check your answer with `CLUSTER KEYSLOT` before you change the script.
   - Explain what your fix costs. Everything that shares one hashed part lives on one node. Is the client IP a safe choice for that part? Would a single global counter be?
3. **Failover under load.**
   - Run the 3-class limiter load (login, OTP, catalog) against the cluster.
   - Force a master failover: `CLUSTER FAILOVER` on its replica for a clean one, and kill the master container for a dirty one.
   - Record per class: errors seen, how long that slot range was unavailable, and what the class **actually did** (failed open, failed closed, or degraded). Compare each with E10 and ADR-012.
   - Also check whether scripts hit `NOSCRIPT` on the promoted node, and what happened when they did.

**Unattended time in this block:** about 30 min of load runs (clean and dirty failover, with a restart between). Schedule the whole lab in the weekend block, and tear it down afterwards.

**Pain-first exercise:** run the unmodified Lua limiter against the cluster first → record the error in `docs/evidence/s03/crossslot.log`. Then run the failover without looking at the class code → fill in `docs/evidence/s03/cluster-failover.md`:

| Class | E10 says | During clean failover | During dirty failover | Matches? | If not, the fix |
|---|---|---|---|---|---|
| Login | Degraded fallback (DB per-account counter) + alert | | | | |
| OTP | Fail closed (503) | | | | |
| Catalog | Fail open + alert | | | | |

**Acceptance criteria:** the multi-key error reproduced and fixed; `CLUSTER KEYSLOT` shows both keys in one slot; the failover table is filled with observed numbers; every mismatch with E10 is either fixed or recorded in ADR-012 with a reason.

*If behind schedule:* the degrade list's Redis Cluster item ([schedule-and-cuts.md](schedule-and-cuts.md) §7) shrinks this block to the CROSSSLOT demo only, with the failover written up instead of run. A real cluster still runs, and hash slots stay hands-on. It saves 2 h.

### 4.7 Bot v1 [4.5 h, must]

**Why this exists.** A second client of the service layer is the cheapest honest test of layering (ADR-004). If the bot needs a rule that REST does not have, the rule is in the wrong place. The PeopleOps bot (P3 Wk9) put it this way: the bot is another caller of the service layer, not a second implementation of the business rule.

Do §4.0 (the aiogram ramp) first. This block assumes you can already draw an update's path through the dispatcher. The vendor side of the bot (a new-order message to vendor staff with a "mark shipped" button) needs the event stream, so it is built in [S4 §4.6](stage-04-async-events-boundaries.md#46-notifications-and-bot-push-6-h-must).

**What to build (`services/bot`, aiogram 3.31, polling mode):**
1. **Account linking with `/start <one-time code>`.**
   - A logged-in user asks `market` for a link code. `market` stores it hashed with a short TTL, single use, bound to that user.
   - The user opens the bot's deep link with the code as the start parameter. The bot sends the code and the Telegram user and chat ids to `market`'s internal REST endpoint. `market` redeems the code and stores the link in `identity`.
   - Check the Bot API deep-linking rules for the start parameter's allowed length and characters before choosing the code format.
2. **`/orders`**: the linked user's recent orders with per-vendor-group status, fetched from internal REST. An unlinked chat gets a clear "link your account first" reply, never a stack trace (P2 bot test).
3. **FSM "track my order".**
   - Ask for an order number, validate it through REST (only the owner's orders), then show each vendor group's status.
   - **Pain-first:** build it on `MemoryStorage` first. Start a conversation, restart the bot container mid-flow, and continue. Record what the bot does with your next message in `docs/evidence/s03/fsm-restart.log`.
   - Then move to `RedisStorage` on `redis-state` with TTLs, using the `fsm` key prefix via `DefaultKeyBuilder`, and repeat the restart. The acceptance test is that the conversation survives.
   - S10 shows a different loss: two replicas with MemoryStorage. This one is about restarts.
4. **Throttling middleware.**
   - aiogram 3 has no built-in throttling. Write an inbound middleware that reads a per-handler flag (the rate for that command) and counts in `redis-state` per Telegram user.
   - When the store is down, fail open, per E10 "Bot inbound".
   - Decide whether throttled updates are dropped silently or get a notice, and record the choice.
5. **Internal REST with a static service token.** The bot authenticates to `market` with one static token, read from the environment. It is replaced by client-credentials JWTs in S9.
   - Write down now what an attacker with that token could do. That paragraph becomes S9's motivation.

**Rules:**
- The bot never imports `market` code and never touches its database. An import-linter or dependency check enforces this.
- Every rule is tested in `market`. Bot tests only check that the right REST call is made and the reply is rendered.
- No test may reach `api.telegram.org`. Run bot tests with the network disabled in CI.

**Testing approach:** call handlers directly with `AsyncMock` objects, and push raw update JSON through `Dispatcher.feed_raw_update()` to exercise filters, middlewares and FSM transitions. aiogram ships no MockedBot, so mock the Bot's API methods yourself.

**Acceptance criteria:**
- An account is linked through the deep link.
- A code cannot be used twice or after its TTL (tested).
- `/orders` and the FSM work end to end on a real bot token in dev.
- The FSM survives a bot restart.
- Throttling is tested with `feed_raw_update`.
- `bot-tests` is green in CI.

### 4.8 Drills + SD2 / SD3 [3.5 h, must]

- Weekly drill hour (×3): one SQL problem on the Atlas schema, or one DSA problem from the banks, plus this stage's interview questions from §10 answered out loud. In W11 and W12 the 45-minute SD2 and SD3 paper designs take the drill hour's question slot.
- 0.5 h to write up both SD comparisons in `docs/sd/`: see §9.

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| Never cached: stock used for decisions, balances, payment state, order state | ADR-010 never-cached list; the cache helper refuses those namespaces | A test that reads each of them and asserts no cache call happened (and `assertNumQueries` shows the DB read) |
| Every price write path invalidates | Delete after commit (`on_commit`) + versioned keys, called from each path | One test per row of the invalidation audit table; the barrier stale-set test |
| Limits hold across 12 processes | One Lua script per decision on `redis-state`; no in-process state | The 3-container × 4-worker limiter test admits exactly `L` |
| No limiter key ever lives without a TTL | The TTL is set inside the same Lua script as the increment | After the chaos run, a `SCAN` over `rl:*` finds no key with `TTL = -1` |
| Replaying a refresh token revokes its family | `family_id` + rotation + reuse check in `identity` | Refresh-replay test; logout-everywhere test |
| OTP fails closed | OTP class maps store errors to 503 | OTP test with `redis-state` stopped (or a fault-injected client) |
| Login never fails open on the account dimension (it degrades, and says so) | Login class falls back to the Postgres per-account `login_attempts` counter and raises the fallback alert; the per-IP limit is knowingly lost for that window (ADR-012) | Login brute-force test with `redis-state` stopped: the per-account lockout still holds and the alert event is emitted |
| The bot has no business logic of its own | Bot calls only internal REST; dependency check forbids importing `market` | Import check in CI; bot tests contain no rule assertions, only REST-call assertions |
| Idempotency stays out of Redis | ADR-008 (S2), restated in ADR-011 | The S2 idempotent-replay test still passes with Redis running; a grep test finds no idempotency key written to Redis |

---

## 6. Tests to write

- **Unit tests on fakeredis:** cache-aside hit and miss paths, key building (namespaces, versions, hash tags), cart merge rules, and limiter class mapping (store error → fail mode). The unit suite must not silently depend on a live Redis (P2 mistake).
- **Integration tests on real Valkey** (a service container in CI): the Lua script's atomicity, TTL presence, NOSCRIPT handling, and noeviction OOM errors surfacing as "store down".
- **Barrier stale-set test:** forces the reader/writer interleaving; red before the fix, green after.
- **Invalidation tests:** one per write path in the audit table.
- **3-container limiter test:** exactly `L` admitted out of `N` spread over 12 processes. Run it in CI against a Compose stack, or as a nightly job if CI time is tight. Record which.
- **`kill -9` persistence test:** a scripted run that produces the carts-lost count. Evidence rather than a CI gate, because it is timing-sensitive.
- **freezegun:** access and refresh expiry at the boundary with leeway, OTP TTL, family revocation.
- **Auth security tests:** refresh replay, logout-everywhere across two devices, OTP brute force (5 attempts, send limit), login fallback when `redis-state` is down (per-account lockout holds, the alert fires).
- **aiogram tests:** handlers with `AsyncMock`; `Dispatcher.feed_raw_update()` for `/start` linking (valid, expired, reused code), `/orders` for linked and unlinked chats, FSM transitions, throttling. Network disabled.
- **Nightly locust smoke** with a p95 budget on catalog endpoints, so a cache regression is caught.

---

## 7. CI changes

| Job | What it runs | What it gates |
|---|---|---|
| Valkey service container added to `test-integration` | Integration tests against real Valkey 9.1 | Merges that break Lua atomicity, TTLs or store-error handling |
| `bot-tests` | aiogram tests with `feed_raw_update`, network disabled | Merges touching `services/bot/**` (path filter) |
| Limiter multi-process test (inside `test-integration`, or nightly) | The 12-process exactly-`L` test | A regression back to per-process state |
| Nightly locust smoke | Catalog scenario with a p95 budget (locust's own percentiles are fine for a smoke alarm; ADR tables use the constant-rate oha probe) | Performance regressions: failing it opens an issue, it does not block merges |

The S2 `concurrency` job (×20) keeps running, and must stay green with the Redis cart.

---

## 8. ADRs and documents

**ADR-010 — Cache policy and the never-cached list**
- *Questions:* What is cached, under which key scheme, with which TTLs and jitter? How does invalidation work (on-commit delete, versions)? How was completeness of the audit established? What is never cached, and why?
- *Numbers:* cold and warm p95/p99 before and after; hit ratio under worldgen traffic; DB calls per second through a hot-key expiry before and after the stampede fix.
- *Counter-argument to address:* "Cache stock too, with a 1-second TTL; it is the hottest read." Hint: argue from P4's oversell reasoning and S2's invariants (`docs/evidence/s02/`). Also address "use write-through instead of cache-aside".

**ADR-011 — Redis topology, and Valkey vs Redis 8**
- *Questions:* Why two instances? What policy and persistence does each have? What does each hold? What happens when each is down or full? Why Valkey?
- *Numbers:* the eviction reset (admitted attempts vs limit), carts lost under RDB / AOF everysec / AOF always, Cluster failover durations (and the KEYS vs SCAN p99 if you did the stretch).
- *Counter-arguments:* "Use one Redis with two logical databases." Hint: argue from `docs/evidence/s03/eviction-reset.log` and from which settings are per instance. "Use Redis 8." Hint: compare the licences and what the managed clouds offer (the ADR-003 register). Note Sentinel vs Cluster in one paragraph.

**ADR-012 — Rate limiting per layer (E10)**
- *Questions:* For each class: key, algorithm, store, fail mode, response. Why does login degrade to a per-account counter, OTP fail closed and catalog fail open? **What does an attacker gain during the login fallback window**, how long can that window last, and who is alerted? Where do the layers added later go (Nginx S6, API keys S9, AI budgets S8, GraphQL cost S11)?
- *Numbers:* 4× and 12× measured; the over-admission distribution; Lua exactly `L`; the Cluster failover table.
- *Counter-arguments:* "Just use Nginx `limit_req`." Hint: what does Nginx know about accounts, and how many Nginx nodes will there be? (It arrives in S6 as an outer layer.) "Fail open everywhere, availability first." Hint: show what an OTP endpoint without a limit costs. Name Redlock only to say why it is not used (see §13).

**Documents:** `docs/rate-limit-algorithms.md` (the §4.4 requirements); `docs/perf/s3-invalidation-audit.md`; an auth note covering families, the denylist exposure window and the OTP hashing answer; a short `services/bot/README.md` covering linking, the FSM, throttling and the service-token risk paragraph.

---

## 9. System design session

| SD | Built or whiteboard | What you reuse from Atlas |
|---|---|---|
| **SD2 — Rate limiter** | **Built** (E10) | The pain CSV, the algorithms doc, the class table, the failover table. Do the paper design first, 45 minutes, then compare it with what you built. SD2 asks how the limiter stays correct across 5 gateway instances. You have measured 12 processes. |
| **SD3 — Distributed cache** | Built-lite | The stampede numbers, the stale-set race, allkeys-lru, and the Cluster lab. SD3 asks how clients pick the node that owns a key: you have hash slots now, and the consistent-hash ring arrives in S9. Also answer what happens to DB load the instant one cache node dies. You saw a version of it in the stampede run. |

Write each session up in `docs/sd/` with a "what the build forced that the paper design missed" paragraph. Proj27 D178 is the model.

---

## 10. Interview questions this stage lets you answer

1. What is a cache stampede, and how did you fix it? Show the before and after DB curve.
2. How do you know you found every invalidation path?
3. Cache-aside or write-through: which did you use, and why?
4. Walk me through the stale-set race. Why does "delete on write" alone not fix it?
5. Why does INCR followed by EXPIRE race? What exactly goes wrong?
6. Why does GET-then-SET over-admit, and what does that have in common with an oversell?
7. Why is a Lua script atomic in Redis? What must you pass in `KEYS`, and why?
8. Which endpoints fail open, which fail closed, and which degrade to a second store? Why? What does an attacker gain while login is degraded?
9. Token bucket vs sliding window counter: memory, accuracy, bursts. When is each right?
10. Why is Redis fine for a rate limiter but wrong for idempotency?
11. What does refresh-token reuse detection catch? Why revoke the whole family?
12. How does logout-everywhere treat access tokens that were already issued?
13. What is CROSSSLOT, and how do hash tags help? What do they cost?
14. What happened to your limiter during a Redis failover?
15. Why two Redis instances? Why not two logical databases?
16. What happens to your throttling when Redis runs out of memory? Which eviction policy did you choose for which instance?
17. RDB vs AOF: what did `kill -9` lose under each? Why is a process crash a weak test of `fsync`?
18. Why is the cart allowed in Redis when idempotency is not?
19. How do you keep a Telegram bot's business logic from diverging from the REST API's?
20. How do you test aiogram handlers without talking to Telegram?
21. Why link the bot to an existing user instead of giving Telegram its own auth?

---

## 11. Common mistakes to watch for

- Caching without a clear invalidation story, then discovering the Admin path months later (P2).
- Benchmarking only a warm cache and reporting the flattering number (P2).
- Unit tests that silently need a live Redis because fakeredis was forgotten (P2).
- One Redis instance with allkeys-lru for the cache, the limiter and (in S4) the Celery broker, so security limits and queued tasks are evicted with the cache.
- The opposite mistake: `noeviction` with no code handling the OOM error, so throttling starts throwing 500s (P2, "Running Redis with noeviction and discovering it when throttling starts throwing").
- INCR + EXPIRE as two commands, leaving TTL-less keys that lock users out forever.
- A Lua script that builds key names internally instead of receiving them in `KEYS`. It works on one node and breaks on Cluster.
- Using `KEYS *` anywhere in application code.
- Refresh tokens that live forever, and a "logout" that only deletes a cookie (P5).
- Caching anything financial "because it is slow", without checking whether staleness is acceptable (P6 D94–D96).
- A bot handler that re-implements an eligibility check instead of calling the service layer (P3 Wk9).

---

## 12. How real companies differ

- **Managed Redis or Valkey.** Most teams use ElastiCache, Memorystore or similar, with replicas and automatic failover, and never run a cluster by hand until one node's memory is not enough. The lab still matters: when the managed service fails over, you will know what your client is doing.
- **Rate limiting starts at the edge.** CDNs, WAFs, API gateways or Envoy's global rate-limit service reject abusive traffic before it reaches the app. Account-aware limits such as login and OTP still live in the app, as here. Atlas adds the outer layer in S6 (Nginx) and S10 (the gateway).
- **Auth is usually bought.** Auth0, Cognito or Keycloak handle refresh rotation for most companies. Building families yourself once is how you learn to judge a vendor's claims. S9's ADR-031 takes up this counter-argument.
- **Invalidation is often event-driven.** Large shops invalidate caches from change events (CDC) instead of from each write path, precisely because audits like yours keep finding missed paths. You will have the event stream in S4.
- **OTP sits behind fraud controls and a paid SMS provider.** Real systems add per-country limits and anomaly detection against SMS pumping. Your fake `SmsSender` port is where that provider would plug in.
- **Bots run on webhooks behind a load balancer.** Polling is a development convenience. Atlas switches in S10, when a second replica makes polling impossible.

The learning version is still right because each production shortcut above hides a failure mode you have now seen yourself.

---

## 13. Deliberately not doing

| Item | Why not now | When it arrives |
|---|---|---|
| **Redlock** | Named only. A lock that can expire while its holder is paused needs a **fencing token** checked by the resource. Otherwise two holders both "own" it. Kleppmann's critique is the reading. | Fencing tokens checked in Postgres: S4 (one import per vendor) and S10 (flash-sale holds) |
| Redis pub/sub and Streams | Nothing needs fan-out yet | S11 (edge fan-out, resume by stream id) |
| Celery and a broker | This stage fixes reads and limits; the synchronous email pain stays for S4 | S4 |
| RS256 / JWKS | HS256 is still acceptable while only `market` verifies tokens; the "every verifier can mint" threat appears when `ai` verifies them | Threat recorded in S8, fixed in S9 |
| Webhook mode for the bot | One polling replica is enough; a second replica is what makes polling fail (409) | S10 |
| Per-API-key token-bucket limiter with `X-RateLimit-*` headers | No merchant API surface exists yet | S9 |
| Caching stock, balances, payment or order state | Stale means wrong: oversell, wrong balance | Never |
| Redis for idempotency | Not transactional with the order, evictable, lost on restart (ADR-008) | Never |
| A real SMS provider | No contract; the port is enough to test the flows | Not in Season 1 |
| Cart events or a durable cart-activity record | From this stage a cart is a Redis hash with a TTL, and an abandoned cart simply expires, so the running system leaves no abandonment record. That is acceptable: Season 2's funnel analysis takes cart abandonment from worldgen history mode (S2), which already writes carts and their checkout outcome at a configurable abandonment rate. | Season 2 uses worldgen history ([season-2.md](season-2.md)); no cart events in Season 1 |

---

## 14. Stretch

Only when the must tier closes early. Each item is independent.

- **ETag / 304 [1 h]:** conditional GETs on catalog endpoints; a price change produces a new ETag; a matching `If-None-Match` returns 304 with no body. Explain the two caches and their two invalidation stories (P2 D37–D39).
- **Trending ZSET + HyperLogLog viewers [1 h]:** trending products per category from a sorted set with decay; unique viewers per product from HLL. Compare the HLL estimate with the exact count at worldgen volume.
- **Slot reshard under load [1 h]:** move slots between cluster masters while the limiter runs. Observe `MOVED` and `ASK` redirects in client logs, and record errors during the move.
- **Sliding-log limiter [1 h]:** the fifth algorithm built for real. Measure its memory at 100k keys and replace the computed row in `docs/rate-limit-algorithms.md`.
- **KEYS vs SCAN stall [1 h]:** load about 1M keys and run a tight GET loop that records its latency. In another shell, run `KEYS cache:*`, then iterate with `SCAN` and a COUNT. Record the GET loop's p99 during each in `docs/evidence/s03/keys-vs-scan.csv`, and add the number to ADR-011.

---

## 15. Definition of done

- [ ] Cold and warm p95/p99 recorded under ADR-002 in `docs/evidence/s03/cache-p95.csv`
- [ ] Invalidation audit table complete, one passing test per write path
- [ ] Stampede reproduced under locust; the fix holds under the same profile (before and after evidence)
- [ ] Stale-set barrier test red, then green
- [ ] Eviction reset on a shared LRU instance recorded; `redis-cache` and `redis-state` split with configs committed
- [ ] `kill -9` lost-cart counts for RDB, AOF everysec and AOF always recorded; a test or lint rule forbids `KEYS` in code
- [ ] Cart in Redis with merge-on-login tests; the S2 race suite green with it
- [ ] Limiter pain CSV complete (a committed prediction and a measured row for each of steps 1–5); the limiter holds across 12 processes
- [ ] Each limiter class proven to behave as E10 says with `redis-state` down (login degrades with an alert, OTP fails closed, catalog fails open with an alert)
- [ ] `docs/rate-limit-algorithms.md` with the fixed-schedule table and the memory-at-100k-keys table
- [ ] Refresh families, reuse detection, logout-everywhere, `jti` denylist and phone-OTP login, all tested
- [ ] Cluster lab: CROSSSLOT fixed with a hash tag; the failover table filled in against E10
- [ ] aiogram ramp note in `docs/learning/aiogram-ramp.md`
- [ ] Bot links an account, lists orders and tracks an order through an FSM that survives a restart; `bot-tests` green
- [ ] ADR-010, ADR-011 and ADR-012 written with their numbers
- [ ] SD2 and SD3 written up in `docs/sd/`
- [ ] Actual hours per block logged in the hours log; postmortem paragraph in `docs/postmortems/` (what surprised you, which blocks took longer than budgeted and by what ratio, what you would do differently)
- [ ] 2 STAR stories in `docs/star/`: **the stampede**, and **the silent limiter reset caused by eviction**
- [ ] `docs/deferred.md` re-read and updated
- [ ] Git tag `v0.3`

---

## 16. If you get stuck

**aiogram ramp (4.0)**
- If the toy bot never answers, is anything else polling the same token? Only one `getUpdates` consumer may run per bot.
- If you cannot tell which middleware scope you need, ask whether it must run for updates that no filter matches.

**Cache (4.1)**
- Is your "cold" number really cold? What did the warm-up touch?
- For the audit, which writes do not go through your service layer? Admin, commands, raw SQL and `QuerySet.update()` all skip `save()`.
- For the stale-set race, draw the timeline of two requests on paper, with the commit and the delete on it. Where would a version number make the late write harmless?
- Reread P2 D34–D36 and `docs/cache-stampede-notes.md` from QuickServe (§12 of [02-quickserve-pos.md](../python/02-quickserve-pos.md)).

<details>
<summary>Check your prediction (4.1 pain-first), only after you have run it</summary>

- No cache, cold and warm give three clearly different p95s. Warm alone would flatter you.
- With no stampede protection, DB calls per second and p99 spike exactly at the hot key's expiry.
- Before the fix, the barrier test leaves the old price in the cache after the writer committed.
- Before the audit, at least one write path leaves a stale price, usually Admin or a management command.

</details>

**Redis ops (4.2)**
- If eviction does not seem to happen, is `maxmemory` actually set on the instance you think? Check `CONFIG GET` on the running container.
- If AOF loses nothing, ask what `kill -9` of a process leaves in the kernel's page cache.
- Reread the Redis-notes table in [02-quickserve-pos.md](../python/02-quickserve-pos.md) §12.

<details>
<summary>Check your prediction (4.2), only after you have run it</summary>

- On the shared LRU instance, `evicted_keys` rises, the limiter key disappears (`EXISTS` returns 0) and the attacker's attempts are admitted again. The limiter resets silently, with no error anywhere.
- RDB with the default save points loses every cart written since the last snapshot. AOF everysec usually loses almost nothing after `kill -9`, because the written data is already in the kernel's page cache; only an OS crash or power loss would test the one-second fsync window.

</details>

**Limiter (4.4)**
- If the naive versions never fail, are your requests really concurrent? A barrier (all workers wait, then fire together) makes races show up on every run instead of once in fifty.
- If the Lua limiter admits `L+1`, is the previous window really empty? Is "now" coming from two different clocks?
- If Cluster refuses the script, list every key the script touches. Were they all in `KEYS`, and do they share a hash tag?
- Reread Proj27 D171–D173 in [phase-6-capstone.md](../../phase-6-capstone.md) and the per-merchant limiter section of [09-payflow.md](../python/09-payflow.md) (D151–D153).

<details>
<summary>Check your prediction (4.4 steps 1–5), only after you have run them</summary>

- Step 1: up to 4 × L admitted, because each worker has its own dictionary.
- Step 2: up to 12 × L. The limit grows with the deployment, which is exactly the property an attacker wants, and the number that justifies a shared store.
- Step 3: `TTL` returns -1. INCR and EXPIRE are two commands, so a failure between them leaves a key that never expires, and that IP or account is locked out forever. A limiter bug has become a denial of service against your own users.
- Step 4: more than L admitted, and a different number on most runs. Two processes both read `L-1`, both decide "allowed" and both write `L`: a lost update, the same shape as S2's oversell.
- Step 5: exactly `L`, every run.

</details>

**Auth (4.5)**
- What exactly makes a refresh token "reused"? Which column tells you it was already rotated?
- For the OTP hash question: how long would it take to try all 10^6 codes offline against a stolen hash?
- Reread the refresh-rotation rows and the auth test suite in [05-carepoint.md](../python/05-carepoint.md) (D85–D90).

**Cluster (4.6)**
- Run `CLUSTER KEYSLOT` on your two keys. Are they the same number?
- During failover, which errors does the client raise, and which layer of your code sees them first?

<details>
<summary>Check your prediction (4.6), only after you have run it</summary>

- The unmodified script fails with `CROSSSLOT Keys in request don't hash to the same slot`. The fix is a hash tag: only the part inside `{}` is hashed, so `rl:{<ip>}:login:...` keys for one IP share a slot (glossary §7). The cost is that everything under one tag lives on one node, which is fine for an IP and fatal for a single global counter.

</details>

**Bot (4.7)**
- If a handler seems to need a rule, stop. Which `market` endpoint should own that rule?
- If `feed_raw_update` does nothing, is your router included in the dispatcher, and does the raw update JSON have the fields your filter reads?
- If the FSM loses state on restart even with `RedisStorage`, which instance and key prefix is it writing to? Look for `fsm:` keys in `redis-state`.
- Reread the bot extensions in [02-quickserve-pos.md](../python/02-quickserve-pos.md) §20 (linking, error paths) and [03-peopleops.md](../python/03-peopleops.md) §18 (FSM, shared service layer).

Previous stage: [Stage 02 — Checkout correctness](stage-02-checkout-correctness.md). Next stage: [Stage 04 — Async, events, boundaries, search](stage-04-async-events-boundaries.md). Stack and decisions: [README](README.md), [glossary](glossary.md), [testing-and-ci](testing-and-ci.md), [system-design-map](system-design-map.md).
