# Stage 09 — Strangler: AtlasPay + auth extraction

| | |
|---|---|
| **Weeks** | W38–W42 (5 weeks) |
| **Hours** | 60 must + 6 stretch (stretch only if the must tier closes early) |
| **Architecture at start → at end** | market (Django modular monolith, with the in-process `payments` module) + ai + bot + provider-sim, on Compose on the Terraform VPS → **+ atlaspay** (on its own public host `pay.<domain>`) and **+ auth** (FastAPI, each with its own Postgres cluster), Keycloak, Vault. The `payments` module is contracted away; market pays AtlasPay exactly like an outside merchant (merchant #1). |
| **New technologies** | PostgreSQL logical replication; SQLAlchemy 2.0 async + Alembic in a production service; Authlib 1.8 + joserfc; Keycloak 26.7; Google as a second OIDC provider; MCP authorization (spec 2026-07-28); Vault (KV, database secrets engine, transit); Toxiproxy; Pact HTTP contracts + broker; oasdiff; a consistent-hash ring with virtual nodes |
| **Portfolio tag** | `v0.9` |
| **Old-spec theory to read** | P5 D79–D90 ([CarePoint](../python/05-carepoint.md): RS256/JWKS/rotation D79–D84, OIDC + PKCE + Keycloak + refresh families D85–D90); P9 D145–D156 ([PayFlow](../python/09-payflow.md): idempotency and webhooks D145–D149, per-merchant token bucket + Vault + gRPC D151–D153, Toxiproxy D154–D156); P6 D94–D101 ([LedgerBase](../python/06-ledgerbase.md): retry + breaker D94–D96, API versioning D97–D101); P7 D115–D120 ([FleetTrack](../python/07-fleettrack.md): saga, 202 + Location); P10 D163–D165 ([AtlasMarket](../python/10-atlasmarket.md): bulkhead, why not 2PC); P8 D131 ([phase-5](../../phase-5-scaling-architecture.md) Friday of Week 22: consistent hashing); Proj26 D169–D170 ([phase-6](../../phase-6-capstone.md): URL shortener); P1 D13–D18 ([StockPilot](../python/01-stockpilot.md) §10: the blocking-call demo) |

Version pins are as of 2026-09 — re-check with `scripts/compat_check.sh` at the start of the stage.

> **What this stage is really for.** You take the two most dangerous pieces out of a running monolith, money and identity, without losing a single payment. You also learn to justify a split with numbers instead of fashion. Every extraction here has a measured reason, a rehearsed cutover and a proof at the end: the same acceptance suite from [Stage 05](stage-05-atlaspay-monolith.md) goes green against the new service, and reconciliation shows zero drift. This stage is also where AtlasPay becomes a product that other merchants could use: API keys, dated versions and signed webhooks appear only now, because only now is there a real process boundary that needs them.

**Schedule note.** From B2 (W37) job applications take 2–4 h/week, taken from stretch time first ([buffers-and-job-sprint](buffers-and-job-sprint.md)). At the 12 h/week floor there is no stretch time to take them from, so follow the job-search cap in [schedule-and-cuts](schedule-and-cuts.md). The block budgets below are bottom-up estimates sized to the 12 h/week floor, and they are still estimates: keep logging actual hours per block, as you have since S0, and if the actual/budget ratio you computed at B1 and re-checked at B2 is above 1, re-plan this stage with it now. A spine block that overruns moves the date; nothing is deferred silently. If you are behind at the start of this stage, the degrade items that touch S9 are #17 (Pact HTTP dropped), the Google OIDC item placed right after it, #8 (Vault dynamic DB credentials become KV + transit only) and #7 (MCP OAuth and the version transform become a static MCP token plus header pin and oasdiff). Apply them in the list's order; the hours each one saves are in [schedule-and-cuts §7](schedule-and-cuts.md#7-cut-order-and-the-degrade-list). The shadow cutover, the split gate and the extraction ADRs are on the never-cut spine.

---

## 1. The problem this stage starts from

At the end of [Stage 08](stage-08-ai-integration.md) Atlas works and is deployed, but four facts, all measured, say the monolith has become the wrong shape for money and identity.

**Business terms.**
- A routine schema change on `ordering_order` can freeze payment callbacks. In the S6 lock-queue drill, a long SELECT plus an `ALTER TABLE` queued every writer behind it, **including Payme callbacks**. Payme sees timeouts, so payments fail or end up in manual resolution. A marketplace that loses payments during a deploy loses money and trust.
- AtlasPay is supposed to be a payment operator that treats every merchant the same way. Today its biggest merchant, AtlasMarket, calls it in-process, reads its tables and shares its database. No other merchant could ever get that treatment, so AtlasPay is not neutral, and it has no public surface (keys, versions, webhooks) that another merchant could use.
- Marketplaces want "log in with…" and third-party agents (MCP clients) want OAuth. None of that exists.

**Engineering terms.**
- **Secrets scope.** Every market process type (web, worker, beat, relay, consumers, times the replicas) loads settings that contain the Payme and Click keys. The S6 split gate recorded the secrets each process holds. One leaked worker means leaked provider keys.
- **Token minting.** In S8 you found that `ai` verifies market's HS256 tokens with the same shared secret that signs them, so `ai` can mint a market admin token. That is recorded as a threat finding, and this stage fixes it.
- **Refresh slowdown (indirect).** The S6 lock drill also slowed token refresh, but not through the lock itself: refresh rotation touches only identity tables, never `ordering_order`. It slowed because refresh shares market-web's workers and DB pool with the checkout requests queued behind the lock (you recorded refresh p99 during the stall in S6). A separate pool for the auth endpoints would cure that without a split, so this is the weakest of the auth-split reasons, and ADR-031 must say so.
- **SLO gap.** The callback-latency SLO from ADR-022 is violated whenever market's database misbehaves, even though payments did nothing wrong.

The S6 cheap fix, giving `/providers/*` its own gunicorn pool, isolates worker capacity but not the database. Whether it was enough is exactly what the split gate re-run must tell you.

---

## 2. Outcomes — what exists when the stage is finished

1. **atlaspay** runs as its own FastAPI + SQLAlchemy 2.0 async + Alembic service on its own cluster `pg-atlaspay` (database `atlaspay`), reusing `libs/atlaspay-domain` unchanged. It owns its own public host `pay.<domain>` (staging: `pay.staging.<domain>`): `/v1/*`, `/providers/payme/rpc`, `/providers/click/{prepare,complete}` and `/l/{code}`. It also runs the fraud v1 path ported from market (velocity reads from the `fraud_features` CAGGs, model loading, shadow scoring) and the `tsdb.pay-metrics-writer` and `fraud.features` consumers.
2. **A rehearsed, logged strangler cutover**: logical replication of the `payments_*` tables, a shadow period with a byte-for-byte reply diff, an Nginx route switch with a write freeze of a few seconds, and the old tables (and market's `market.payment-events` queue) contracted only after the exit criterion passed.
3. **The exit criterion is met and evidenced**: the S5 acceptance suite (all 12 failure scenarios, the Payme sandbox scenarios, Click's 15, with the chaos switches) is green against atlaspay, **and** the reconciliation diff is 0, **and** shadow fraud scores are still recorded for 100% of attempts.
4. **A merchant surface**: `pk_/sk_/rk_ × test/live` API keys (sent as `Authorization: Bearer sk_…`) with scopes, rotation and livemode isolation; a dated `Atlas-Version` header with one old-version transform and an `oasdiff` gate; signed webhooks (`Atlas-Signature`) delivered through RabbitMQ delay tiers by dispatchers assigned with a consistent-hash ring; a per-key Lua token-bucket limiter that fails open safely.
5. **market is merchant #1**: its `PaymentsGateway` port talks HTTP with an `sk_` key, with timeouts, jittered retries under a retry budget, a breaker and a **bulkhead** sized from locust numbers; it receives and verifies webhooks, which from the switch on are its only source of payment, refund and payout outcomes; it runs an orchestrated cancel-a-vendor-group saga.
6. **Vault** holds provider keys (KV), issues dynamic Postgres credentials to atlaspay, envelope-encrypts payout references (transit) with one KEK rotation done, and makes erasure of atlaspay's personal data a crypto-shredding operation.
7. **auth** runs as its own FastAPI service on `pg-auth`: RS256 with `kid` and JWKS, rotation under locust with 0 × 401, refresh families, first-party Authorization Code + PKCE, OIDC federation to Keycloak 26.7 and to Google (live on staging) with account linking, and client-credentials JWTs (`aud`, `scope`) between services, including a narrowly scoped bot credential that acts for a linked user under an amount cap. market's Django session is the BFF; a shadow users table in market is fed by `user.*` events.
8. **MCP over Streamable HTTP (spec 2026-07-28) with Keycloak as the authorization server**; stdio still works locally.
9. **Pact HTTP contracts** market → atlaspay and market → auth, with a broker and `can-i-deploy`.
10. **SD1 built-lite**: AtlasPay payment links at `/l/{code}`, which the bot sends as a pay button for orders awaiting payment.
11. **Documents**: ADR-030, ADR-031, ADR-032, ADR-033, ADR-034, the cutover runbook, evidence under `docs/evidence/s09/`, two STAR stories and a postmortem paragraph.

---

## 3. Architecture at the end of the stage

```
                                   Internet (TLS, Nginx on the VPS)
      host atlas.<domain>:           |  host pay.<domain>:           |  host atlas.<domain>:
      /api/v1/*, /admin, storefront  |  /v1/*, /providers/*, /l/*    |  /oauth2/*, /.well-known/*, /oidc/*, /telegram/login
                  |                  |               |               |               |
                  v                  |               v               |               v
      +-----------------------+      |    +-----------------------+  |   +-----------------------+   OIDC   +-----------+
      | market (Django)       |--sk_ REST (Idempotency-Key)-->  atlaspay (FastAPI)|  | auth (FastAPI)        |<-------->| Keycloak  |
      | web/worker/beat/relay |<--signed webhooks (Atlas-Signature)--|  api, relay,    |  | RS256 + JWKS, PKCE,   |          | realm     |
      | consumers; BFF session|      |    |  dispatchers x N,     |  |   | client credentials    |          | atlas     |
      | shadow identity_user  |      |    |  scheduler            |  |   +-----------------------+          +-----------+
      +-----------------------+      |    +-----------------------+  |        |  PG auth, redis-state
         |   PG market (+replica)    |        |  PG atlaspay           |
         |   redis-cache/state       |        |  redis-state (rl:),    |        Vault: KV (provider keys),
         |   Mongo, tsdb, Garage     |        |  redis-cache (links)   |        database engine (atlaspay creds),
         |                           |        |  tsdb pay_metrics,     |        transit (payout refs, subject keys)
         |                           |        |  fraud_features        |
      +--------+   +--------+        |    +----------------+
      | ai     |   | bot    | --client-credentials JWT--> market     provider-sim <--Payme JSON-RPC / Click forms--> atlaspay
      | /mcp   |   +--------+        |
      +--------+  (MCP tokens from Keycloak, aud = the MCP resource)
                                     |
      RabbitMQ: atlas.events (internal domain events)  |  atlaspay.webhooks -> atlaspay.webhook-dispatch.{n}
```

**What changed and why.**
- **Two new deployables, each with its own Postgres cluster.** E2 allows a physical DB split only where the forcing problem was at DB level. For atlaspay it was the lock stall and the secrets scope; for auth it is security. Everything else stays in market with logical ownership only.
- **market lost its `payments` module and gained a merchant client.** market reaches AtlasPay only through public REST with an `sk_` key and learns payment, refund and payout outcomes **only** from signed webhooks. It never reads the atlaspay DB. `market.payment-events` (S5–S8) is unbound and deleted at the contract step; ordering's payment consumer is replaced by the webhook receiver (same inbox table, dedup on event id). The internal `payment_intent.*` events on `atlas.events` remain for internal platform consumers only: the tsdb and fraud feature writers (now inside atlaspay) and edge from S11. The ledger (S12) consumes `ledger.postings`, not `payment_intent.*`.
- **AtlasPay has its own public host, `pay.<domain>`.** Its public API, payment links and provider callbacks live there, separate from any merchant's site, the way a payment operator's API host is. ai stays under market's host (`/v1/assistant/*`, `/v1/descriptions/*`, `/v1/embeddings`, `/mcp`).
- **Identity is issued in exactly one place.** Only auth signs user tokens; everyone else holds public keys. Keycloak and Google are external identity providers for auth, and Keycloak is also the authorization server for MCP clients; market and atlaspay never accept Keycloak or Google tokens directly.
- **Secrets moved to Vault.** Provider keys are readable only by atlaspay's Vault policy, and market's settings no longer contain them.
- **New process types inside atlaspay:** `api` (which also runs the fraud v1 shadow scoring ported from market), `relay` (its own outbox), `dispatcher` × N (webhook delivery), `scheduler` (the S5 payouts and reconciliation jobs, a single instance on Compose; [Stage 10](stage-10-kubernetes-grpc-inventory.md) makes it leader-elected with a Lease), and the `tsdb.pay-metrics-writer` and `fraud.features` consumers taken over from market.

---

## 4. Build plan

**Sequencing.** Blocks are listed in the design's order, but some depend on later ones: the route switch needs API keys and webhooks, because market must pay over HTTP once the module is gone. A workable order:

| Week | Work |
|---|---|
| W38 | 4.1 gate and ADR drafts; 4.2 steps 0–2 (atlaspay service and adapters, the fraud v1 port, replication) |
| W39 | 4.2 step 3 (shadow); 4.7 Vault (KV first: provider keys and the key pepper); 4.3 keys |
| W40 | 4.4 versioning, 4.5 webhooks, 4.6 limiter; 4.13 payment links and the bot's pay button (right after the keys they need) + SD1 |
| W41 | 4.8 market as merchant (behind a flag); rest of 4.7; 4.10 auth part 1 (RS256, JWKS, rotation, refresh families, Authorization Code + PKCE); weekend: **first cutover rehearsal** on staging |
| W42 | 4.2 steps 4–5 (cutover and contract), 4.9 saga, 4.10 auth part 2 (Keycloak and Google federation, client credentials, the bot's delegated calls), 4.11 MCP OAuth, 4.12 Pact; SD18 revisited; tag `v0.9` |

Cutover rehearsals, the route switch, split-gate runs and the Toxiproxy run need uninterrupted state, so they belong to the weekend block.

### 4.1 Gate and ADRs — 3 h [must]

**What to build.** No new code. Re-run `bench/split-gate` (ADR-023) against the current monolith with the ADR-002 protocol. Bulkhead off and bulkhead on are this ADR's final before/after pair, so each gets 5 runs (median and min–max). Add the S6 lock-queue incident (a long SELECT plus `ALTER TABLE ordering_order`) inside the 10-minute window, because ADR-030 needs callback p99 **during** a stall. locust (worldgen traffic) shapes the load; the percentiles you report come from a constant-rate oha probe (`--latency-correction -q`), cross-checked against the server-side histograms (ADR-002).

**This block contains about 110 min of unattended benchmark time (2 configurations × 5 runs × ~11 min). Schedule it in the weekend block.**

**PAIN-FIRST.**
1. Run the gate with the S6 bulkhead (`/providers/*` on its own gunicorn pool) turned **off**, then **on**. In the "on" configuration, give the token-refresh endpoint its own small pool as well, so ADR-031 can answer its cheap-fix question from the same runs.
2. Record callback p99, token-refresh p99 and the share of Payme `-32400`/timeouts and Click errors during the lock stall in both runs. Ask yourself whether a separate worker pool can help when the queue is inside Postgres.
3. Record both tables in `docs/evidence/s09/split-gate-before.csv`, plus the list of processes holding provider secrets (from the gate's secrets inventory).

**Acceptance criteria.**
- ADR-030 and ADR-031 drafts exist with a filled "numbers" section and a written counter-argument (see §8).
- If the numbers do not hurt, the ADR says so and argues only from blast radius or security scope. That is a legitimate outcome, not a failure.

### 4.2 Strangler — 15 h [must]

A **strangler fig** migration grows the new system around the old one and moves ownership one route at a time until the old code can be deleted. You never switch off the old system and hope; at every step there is a way to tell whether the new one behaves identically.

Suggested split: service and adapters 4.5 h; the fraud v1 port 1 h; replication 3 h; shadow 3 h; rehearsal, switch and contract 3.5 h.

```
 time ───────────────────────────────────────────────────────────────────────────────────────▶
  Step 1: build       Step 2: replicate           Step 3: shadow              Step 4: switch     Step 5: contract
  atlaspay service    pg-market ──publication──▶  provider-sim mirrors each   freeze, drain,     exit criterion met,
  (SHADOW mode)       pg-atlaspay (subscriber)    callback; replies diffed    route, unfreeze    then drop payments_*
  write owner:  market ─────────────────────────────────────────────────────┤ atlaspay ─────────────────────────▶
```

**Step 0 — preconditions (check, do not build).**
- The `payments` module talks to the rest of market only through its `api.py` facade and events. The S4 import-linter independence contract shows 0 violations.
- List every foreign key that touches a `payments_*` table. The S4 ban means nothing points **into** payments. FKs **out of** payments (for example to the allow-listed `identity_user`) cannot cross databases, so in atlaspay they become plain id columns. Write down how you keep them valid without an FK.
- Every `payments_*` table has a primary key (you will see why in step 2).
- Find where AtlasPay's idempotency records and raw `provider_events` live. If AtlasPay's idempotency records share a table with checkout's keys, you need a publication **row filter** (PG15+) or you must split the table first with expand/contract. Check the catch before you choose the filter: if the publication publishes UPDATE or DELETE, the row filter may use only columns covered by the replica identity; otherwise the publisher rejects UPDATEs on that table, which breaks the monolith's writes ([PG17 docs, Row Filters](https://www.postgresql.org/docs/17/logical-replication-row-filter.html)).
- Payments writes outbox rows into market's shared `outbox` table. Those rows are not replicated; they must be drained before the switch.

**Step 1 — build atlaspay.**
- `libs/atlaspay-domain` moves as-is. Record how many lines of the library you had to change: ideally 0, which is the proof that the S5 framework-free core paid off.
- Rewrite only the adapters: the Payme JSON-RPC route (always HTTP 200), the Click form routes, repositories on SQLAlchemy 2.0 async, atlaspay's own outbox relay and the scheduler process.
- The first Alembic migration must recreate the `payments_*` tables with **identical schema-qualified names, column names, types, constraints, indexes and triggers**. Logical replication matches tables by name, so renaming waits until after the cutover. Write a schema-diff test that compares `information_schema` (and the trigger list) between the two databases; the diff must be empty.
- **Port the fraud v1 path** (about 1 h of this block). In S7 it runs inside market's `payments` module; if nothing moves it, shadow scoring silently stops at the switch. Move into atlaspay: the velocity-rule reads from the `fraud_features` CAGGs, model loading with the sha256 check, shadow scoring on every attempt (with `model_version` stored), and the `tsdb.pay-metrics-writer` and `fraud.features` consumers as atlaspay process types. The feature function comes from the framework-free `libs/atlas-fraud-features` wheel (`atlas_fraud_features`), so nothing in it changes. SHADOW and HOLD modes (below) disable the scorer and both consumers, like the relay.
- atlaspay starts in a **SHADOW mode**: no scheduler, no relay, no dispatchers, no fraud consumers, no outbound provider calls, and every database transaction ends in ROLLBACK.
- **The -32400 trap again, in a new framework.** FastAPI parses a JSON body only when the Content-Type is `application/json` (or `…+json`). Payme sends `Content-Type: text/json` ([Stage 05 §4.0.1](stage-05-atlaspay-monolith.md#401-payme-paycom-merchant-api)), so even a **valid** Payme call against a route with a Pydantic body model gets a 422, and so does a malformed one. An unhandled exception is a 500. Payme sees all of them as `-32400`. Show all three failing first, then read the raw request body yourself and always answer HTTP 200 with the protocol's error object, as you did for DRF in S5.
- **Pain on the way** (write down each one in `docs/evidence/s09/async-pitfalls.md`, with the stack trace and the fix):
  - `MissingGreenlet`: a lazy relationship load inside an async session tries to do I/O implicitly, which async SQLAlchemy forbids. Ask yourself: which relationships does each use case need, and how do you load them eagerly?
  - `expire_on_commit`: after commit, the default session expires every loaded attribute, so the next attribute access is a hidden lazy load, which becomes a `MissingGreenlet` in async code. Decide the session setting on purpose and write down why.
  - CPU-bound work blocking the event loop. You meet it hardest in auth (argon2 password hashing, 4.10), but the rule is general: one slow synchronous call in an async handler stalls every other request on that loop. Reuse the measurement you did in P1 D13–D18 (StockPilot's blocking-call demo) and the S2 concurrency exercise (threads vs processes): measure p95 of an unrelated endpoint while the slow call runs, before and after moving it off the loop.

**Step 2 — logical replication.** **Logical replication** streams row changes (INSERT, UPDATE, DELETE) of chosen tables from a publisher to a subscriber database. Physical streaming replication (your S6 replica) copies the whole cluster byte for byte and the replica is read-only; logical replication copies tables into an independent database that has its own schema.
1. Set `wal_level=logical` on pg-market. This needs a Postgres restart: plan it as an operation, measure the blip with the S6 dashboards, and put the numbers in the runbook.
2. Create a replication role with `REPLICATION` and SELECT on exactly the payments tables. Create a **publication** listing the tables explicitly, and a **subscription** on pg-atlaspay. The initial copy runs first, then changes stream.
3. **PAIN-FIRST, on a scratch copy of the database:** add a table without a primary key to a publication that publishes updates. Before you run an UPDATE on the publisher, predict which side complains (publisher or subscriber), when, and with what error; commit the prediction. Then run it and record the exact message in `docs/evidence/s09/replica-identity.md`. (Check your prediction in §16.)
4. **PAIN-FIRST:** disable the subscription for ten minutes under worldgen traffic and watch the replication slot retain WAL on pg-market (`pg_replication_slots`). It is the S6 abandoned-slot drill again, now on a slot you depend on. Confirm `max_slot_wal_keep_size` is set.
5. Learn what logical replication does **not** carry, and write each item into the runbook with your mitigation: DDL (put a schema freeze on the payments tables during the window), sequence values (bump them at the switch if any table uses identity columns), and generated columns (check how PG17 treats the generated `provider_event_id` column; the subscriber must compute its own value or its UNIQUE dedup silently stops working).
6. Triggers on the subscriber do not fire for replicated rows: the apply worker runs with `session_replication_role=replica`. That is correct, because the publisher already enforced the balance and append-only rules. Write a test that proves the triggers **do** fire for atlaspay's own writes once it is primary.
7. Build the verification set you will run at the switch: per-table row counts, a checksum per table computed the same way on both sides, the trial balance on both sides, and the count of idempotency keys.
8. Add a replication-lag panel and an alert in Grafana.

**Step 3 — shadow mode.** In **shadow mode** the new implementation receives a copy of real traffic and computes replies that are compared but never used. provider-sim is your own program, so give it a **mirror mode**. For each callback:

```
provider-sim                  atlaspay (SHADOW)                   market (PRIMARY)        pg-market ─▶ pg-atlaspay
    | wait until the subscription has replayed the last primary commit (an LSN wait, see below)
    |── copy of request ───────▶| BEGIN; full handler; force deferred  |
    |                           | checks; ROLLBACK                     |
    |◀── shadow reply ──────────|                                      |
    |── real request ─────────────────────────────────────────────────▶| BEGIN; ...; COMMIT ──WAL──▶ replicated
    |◀── primary reply ────────────────────────────────────────────────|
    | diff(shadow bytes, primary bytes) ──▶ shadow-diff log
```

**An LSN wait.** An LSN (log sequence number) is a position in the write-ahead log (WAL). The publisher can tell you the LSN of its latest commit, and it also reports how far each subscription has confirmed applying (look at `pg_stat_replication` and `pg_replication_slots` on pg-market). An LSN wait means: read the first position, then wait until the subscription's position is at or past it. It is the same idea as the S6 read-your-writes fix, applied to a logical subscriber instead of a physical replica.

Why this shape:
- The shadow goes **first** so that both implementations see the same state before this request. If it went second, it would see the primary's write and exercise only the replay path.
- The shadow must never **commit**. A committed shadow row collides with the same row arriving through replication, and the apply worker then stops and retries forever, which halts replication and fills the slot. The shadow's transaction runs fully and then rolls back.
- The deferred balance trigger fires only at COMMIT, which the shadow never reaches. Ask yourself how you still make the shadow exercise it.
- "Byte for byte" is only meaningful if the two implementations produce the same bytes for correct behaviour. For Payme, compare the `result` (or `error`) member byte for byte, and separately assert that each reply's JSON-RPC `id` equals the id of the request it answers: JSON-RPC requires that, and a stored reply replayed with an old `id` is a bug the diff must catch. Some reply fields are generated (your own transaction id, `create_time`). Do the diff at two levels:
  1. **Corpus replay (deterministic):** run the recorded acceptance corpus with provider-sim's fake clock and a seeded id generator against both implementations, each on a fresh database. Here the diff must be empty **with no masks at all**. This is the CI `shadow-diff` job.
  2. **Live mirror on staging** during split-gate traffic: masks are allowed only for generated fields. Every masked field needs a one-line justification in the runbook. A mask list that keeps growing is a smell: it means you are hiding differences instead of explaining them.

**PAIN-FIRST.** Run the corpus replay before you think atlaspay is finished. The first non-empty diff is the point of the exercise and your first STAR story. Typical culprits: JSON key order or whitespace, an integer serialised as a float, error message text, timestamp precision, the `-31008` vs `-31050` choice, an HTTP status on a validation error. Record every diff class, its root cause and the fix in `docs/evidence/s09/shadow-diff.md`.

**Step 4 — rehearse, then switch.** Rehearse the whole switch on staging under split-gate traffic at least once, timing every step. Then run it for real.

Why there is no canary here: a canary splits traffic between two versions, but two owners writing the same payment state would diverge immediately. Write ownership moves in one step, protected by a short freeze. (Reads can be canaried; writes cannot.)

Before you write the runbook, answer these questions in it:
- For each Payme method and each Click action, what does the provider do if it gets **no answer** for 5 s? What does it do if it gets an **error**? Which of those is safe during a freeze? (See [Stage 05 §4.0.1](stage-05-atlaspay-monolith.md#401-payme-paycom-merchant-api) and §4.0.2: Payme publishes no response deadline [U], and what happens to debited money when Perform returns an error is [U].)
- Where do held requests wait, and what bounds the wait below the provider-sim timeout you configured?
- How do you count that every request that arrived during the freeze got exactly one answer?
- When do provider-sim's callback URLs (the equivalent of the endpoint URL you would set in the Payme cabinet) move to `pay.<domain>`: before the freeze, so the switch is a single upstream change, or at the switch? Justify it.

**Required properties.** Your runbook must show how each of these holds; the order of the steps is yours to design:
- No provider request is answered by both owners, and every request that arrives during the freeze gets exactly one answer, within the provider-sim timeout.
- Every writer of `payments_*` in market (web, Celery workers, Beat entries, the outbox relay) is stopped or drained before atlaspay takes its first write, and market's outbox holds no pending `payment_intent.*` rows.
- Replication lag is 0 at promotion (an LSN wait), and the verification set from step 2 is equal on both sides before promotion.
- The freeze is bounded: state a target in seconds before the rehearsal and measure it.
- After the switch, `pay.<domain>` (API, links and provider callbacks) is served by atlaspay, atlaspay's relay, dispatchers, scheduler and fraud consumers are running, and market's `PaymentsGateway` flag points at the HTTP adapter (4.8).
- The post-switch watch list is named in advance: `provider_callback_seconds`, `checkout_success_total`, `webhook_delivery_lag_seconds`, `recon_drift_rows`.

**Runbook headings** (fill each one yourself): preconditions and go/no-go checks; the freeze design (where it lives, how held requests wait, what bounds the wait); the ordered steps, each with an expected duration; the verification set and its output; the rollback decision; the post-switch watch list; the live-mirror masks (step 3).

Draft the ordered steps, then time every one of them in the rehearsal and correct the runbook from what you saw. If you get stuck, §16 has staged hints. Record the freeze duration and the number of requests held.

**Rollback decision.** Before atlaspay takes its first write, rollback means reverting the route and the flag. After that, the monolith's tables are stale, and going back would lose writes unless you replicate in reverse (atlaspay → market). Decide in the runbook: either build reverse replication for a rollback window, or declare this a one-way door once the verification set passes, and explain why that is acceptable.

**Step 5 — exit criterion, then contract.**
- **Exit criterion:** the S5 acceptance suite (all 12 scenarios, Payme sandbox scenarios, Click's 15, with the chaos switches) is green against atlaspay, **and** a full nightly reconciliation run reports drift 0, **and** an injected drift is still flagged, **and** shadow fraud scores with `model_version` are stored for 100% of the attempts made against atlaspay.
- One replay check that proves "0 idempotency keys lost". Replies are deterministic and follow each provider's replay rule ([Stage 05 §4.0.1](stage-05-atlaspay-monolith.md#401-payme-paycom-merchant-api) and §4.0.2), so pick 20 provider ids created **before** the cutover and, for each, resend the method that matches its state: for Payme, Perform for state 2, Cancel for -1/-2, Create for state 1; for Click, Complete (a completed payment answers -4). Send every Payme retry with a **new** JSON-RPC `id` (provider-sim's "retry with a new JSON-RPC id" chaos switch). The `result`/`error` member must be byte-identical to the stored reply for that method, and the envelope's `id` must equal the new request's id.
- Only then contract: drop the subscription and confirm the slot is gone on pg-market; unbind `market.payment-events` from `atlas.events` and delete the queue (ordering's payment consumer is now the webhook receiver from 4.5, same inbox table, dedup on event id); drop the `payments_*` tables in a contract migration (with `lock_timeout` and the squawk gate from S6, after a verified backup); delete the `payments` module code; update the import-linter contracts; and remove the provider secrets from market's settings and Vault policy. Decide whether `wal_level` stays `logical` and write down why.

**Acceptance criteria.**
- `docs/runbooks/atlaspay-cutover.md` exists and was executed at least twice (rehearsal and real). `docs/evidence/s09/cutover-rehearsal.md` holds the step timings, freeze duration, held-request count and verification output.
- Corpus replay diff = 0 with no masks; the live-mirror mask list is justified line by line.
- 0 payments lost and 0 idempotency keys lost, proven by the verification set and the replay check.
- Exit criterion met before any table was dropped, including shadow scores on 100% of attempts.
- `market.payment-events` no longer exists, and a test proves market changes an order's payment state only from a verified webhook: a `payment_intent.succeeded` published on `atlas.events` changes nothing in market.

### 4.3 API keys — 3 h [must]

**What to build.** Keys in six kinds: `pk_test_`, `pk_live_`, `sk_test_`, `sk_live_`, `rk_test_`, `rk_live_`.
- **Presentation.** A merchant sends its key as `Authorization: Bearer sk_…` (Stripe's convention; `pk_` and `rk_` keys travel the same way). The edge rate-limit zones (the S6 Nginx `limit_req`, the S10 gateway) key on the non-secret lookup prefix parsed from that header, never on the full key.
- `pk_` (publishable) keys are safe to embed in a client, so they may call only a tiny allow-list of client-safe endpoints that move no money. You define that list.
- `sk_` (secret) keys are unrestricted for their account and mode.
- `rk_` (restricted) keys carry scopes such as `payment_intents:write` or `refunds:read`. Stripe recommends restricted keys as the default for integrations; ask yourself which key type market should use and why.
- **Storage.** Show the key once at creation and never again. Store a non-secret lookup prefix (indexed, unique) and a SHA-256 hash of the full key with a **pepper** (a server-side secret kept in Vault, not in the database). HMAC-SHA256 keyed by the pepper is the clean construction. Verify with a constant-time compare.
- **Why not bcrypt or argon2?** Slow hashes exist to protect low-entropy secrets (passwords) from offline guessing. Is an API key low-entropy? What would a slow hash cost on every request, and who could exploit that cost? Hint: measure the verification cost per request with SHA-256 and with bcrypt (ADR-032 asks for both numbers) and argue from your own measurement in ADR-032. Add what the pepper buys you (hint: think about an attacker who can **write** to the keys table).
- **Rotation with a grace period.** Rolling a key creates a new one; the old one keeps working until an `expires_at` you choose (Stripe allows up to 7 days), then stops.
- **Livemode isolation.** Every object carries `livemode`. The mode comes from the key, and every query filters on account and mode in one central place (a repository base class, or RLS with `SET LOCAL` as in S2). Test objects and live objects must never reference each other. In Atlas both modes talk to provider-sim (with different profiles), so the separation you prove is logical, which is exactly the part that matters.
- Keep keys out of logs: add a structlog processor that masks `sk_`, `rk_` and `whsec_` patterns, and a gitleaks rule for them.

**PAIN-FIRST.** First call a live intent with an `sk_test_` key through a query that forgets the mode filter. Observe the leak. Then centralise the filter and make the same call return 404 (not 403: a 403 confirms the object exists).

**Acceptance criteria.** A test matrix over {pk, sk, rk} × {test, live} × {test object, live object} × {allowed scope, missing scope} passes; a rotated key works during the grace period and fails after it; a grep of a day's logs finds no key material.

### 4.4 Versioning — 1.5 h [must]

**What to build.** A dated `Atlas-Version` header (for example `2026-09-01`). The merchant's version is pinned when its first key is created; a request may send the header to override it. Handlers always run the latest code; a chain of **response transforms** turns the latest shape into the pinned version's shape. Build exactly one transform for one real change you make now. Deprecated versions get `Deprecation` and `Sunset` response headers. Add an `oasdiff` breaking-change gate in CI. In LedgerBase (P6 D97–D101) you versioned in the URL (`/v1` → `/v2`); here you do it the Stripe way, and ADR-032 must say why.

**PAIN-FIRST.** Make the change first **without** a transform and run a client pinned to the old version: observe it break. Then add the transform and see the pinned client pass while a new client gets the new shape.

Questions to answer yourself: Which OpenAPI document does `oasdiff` compare, and how do you get one per supported version? Do webhook payloads also need to be rendered at the endpoint's pinned version? (Stripe does this.)

**Acceptance criteria.** An old-version client test and a new-version client test both pass against the same build; a deliberate breaking change to a supported version fails CI (keep the red run as evidence).

### 4.5 Webhooks — 4.5 h [must]

**What to build.**
- Endpoints registered through `/v1/webhook_endpoints`, each with its own `whsec_` secret. The secret must be recoverable to sign with, so it is **encrypted** (Vault transit), not hashed.
- Signature header (the format is the contract):

```
Atlas-Signature: t=1790000000,v1=5f1c…9ab2,v1=77d0…31ce
signed_payload  = "<t>" + "." + <raw request body bytes>      # HMAC-SHA256 with the endpoint secret
```

- Receivers reject a `t` older than 5 minutes. During secret rotation two secrets are valid, so the header carries two `v1` signatures.
- Delivery through RabbitMQ: exchange `atlaspay.webhooks` → queues `atlaspay.webhook-dispatch.{n}`, retries through the `atlas.retry` tiers (`10s`, `1m`, `10m`, cycling the last tier until a maximum age you choose; Stripe retries live-mode events for up to 3 days), then the parking lot `<queue>.parking` and an alert. Quorum queues dead-letter **at-most-once** by default, so every queue on this dead-letter path (the dispatch queues, their retry tiers and their parking queues) needs `x-dead-letter-strategy: at-least-once` and `x-overflow: reject-publish`, exactly as you set up in S4; reuse the S4 test that a missing parking queue loses nothing. **No ordering guarantee**: say so in the docs, and make merchants treat each event as "something changed, fetch or apply monotonically".
- Metric `webhook_delivery_lag_seconds`.
- **Consistent-hash ring.** Assigning each merchant to one dispatcher lets a dispatcher keep per-merchant connection pools and concurrency caps, so one slow merchant endpoint cannot eat every dispatcher's capacity. A **consistent-hash ring** with virtual nodes places both dispatchers and merchants on a hash circle; each merchant belongs to the next dispatcher clockwise, so adding a dispatcher moves only the merchants that now fall into its arcs.
- **market's receiver:** verify before parsing (raw bytes first, JSON second), dedup on event id through the S4 inbox (`UNIQUE(consumer, event_id)`), and handle a webhook that arrives **before** market has stored its own intent (P9 D145–D149). From the switch on, this receiver is market's only source of payment, refund and payout outcomes: it replaces ordering's `market.payment-events` consumer (that queue is deleted at the contract step, 4.2 step 5) and writes into the same inbox table.

**PAIN-FIRST.**
1. Predict, from first principles, the fraction of merchants that move when going from 3 to 4 dispatchers with `hash % N` and with the ring. Then measure both on 10,000 synthetic merchant ids and record `docs/evidence/s09/ring-3-to-4.csv` (P8 D131 did the same benchmark on a key set). Also record the load spread per dispatcher for two vnode counts.
2. Make provider-sim pay instantly so `payment_intent.succeeded` reaches market before market has committed the row that links the intent to the order. Observe the failure (a 500, or a silently dropped event). Then choose a fix and justify it: store the event and process it when the intent appears, answer non-2xx so AtlasPay retries later, or record a pending row keyed by your Idempotency-Key before calling AtlasPay.

**Acceptance criteria.** A body that is not valid JSON with a bad signature fails on the **signature**, never on parsing; a stale `t` is rejected; both secrets verify during rotation and only the new one after it; a triple delivery produces one side effect; a killed dispatcher's messages are delivered after restart; ring numbers recorded.

### 4.6 Per-key limiter — 2 h [must]

**What to build.** A Lua **token bucket** per key × mode × tier in redis-state (prefix `rl:`, hash tag `{api_key}`). Use the key **id** in the Redis key name, never the secret (key names show up in `MONITOR`, the slow log and dumps). Responses: 429 with `Retry-After` and `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (choose epoch seconds or a delta and document it). This is the E10 row for the AtlasPay API: **fail open** with a local per-pod bucket plus an alert, because payment availability comes first. Provider callbacks are never rate limited (limiting them loses payments). Reuse P9 D151–D153's token bucket thinking and your S3 Lua work; take the clock from Redis inside the script so pods with skewed clocks agree.

**PAIN-FIRST.** Kill redis-state under locust. Record what happens with no fallback (does every request fail, or is none limited?), then add the local bucket and repeat. Merchant B's p95 comes from the constant-rate oha probe, as everywhere under ADR-002. Ask yourself: what limit does each pod's local bucket use when you do not know how many pods exist right now? Record both runs in `docs/evidence/s09/limiter-redis-kill.md`.

**Acceptance criteria.** Merchant A at 10× its limit gets 429s while merchant B sees 0 × 429 and a p95 within the noise band; the Redis-kill run shows fail-open with the alert firing; headers are correct at the boundary.

### 4.7 Vault — 4 h [must]

**What to build.**
- **KV** for the Payme and Click credentials. A Vault policy lets only atlaspay read them.
- **Dynamic Postgres credentials** for atlaspay. The database secrets engine creates a short-lived role per instance and revokes it when the lease ends. The dynamic role must be a member of `atlaspay_app` and must never own objects; tables stay owned by `atlaspay_migrator`. atlaspay renews its lease in the background and rebuilds its connection pool when the credentials change.
- **Transit envelope encryption** of payout references: a per-row data key encrypts the value, transit wraps the data key with a key-encryption key (KEK) that never leaves Vault; store ciphertext, wrapped key and key version. Rotate the KEK once and rewrap (P9 D151–D153).
- **Per-data-subject keys, so erasure is crypto-shredding.** **Crypto-shredding** erases data by destroying the only key that can decrypt it. Personal data belonging to one person is encrypted under that person's key; to erase them, destroy the key. The ledger holds only pseudonymous ids (`acct_…`, user UUIDs), so the append-only ledger never has to change. The must tier builds this for atlaspay's own database; extending it to the event log (outbox partitions, RabbitMQ payloads) and to ai's Mongo transcripts is a stretch item (§14), but ADR-033 must still say how erasure works in each of those places.
- Update ADR-003 (licences): Vault moved to the BSL 1.1 licence in 2023, and OpenBao (MPL-2.0) is the community fork [C] ([HashiCorp's announcement](https://www.hashicorp.com/blog/hashicorp-adopts-business-source-license), [OpenBao](https://github.com/openbao/openbao)).

**PAIN-FIRST.**
1. Let a dynamic credential lease expire while atlaspay is under load. Observe what happens to pooled connections and to new connections. Record it, then fix renewal and pool rotation.
2. Shred one test subject and then restore last night's PITR backup into a scratch database. Ask yourself: does the backup bring the key back? What does ADR-033 say about the backup retention window as the real erasure horizon?

**Acceptance criteria.** `grep` finds no provider secret in market's image, settings or environment; a lease revocation is survived; one KEK rotation plus rewrap is done with data still readable; a shredded subject's data is unreadable in atlaspay's live database, and ADR-033 records what the PITR restore in pain-first step 2 (and a Vault backup, if you keep one) brings back.

### 4.8 market as merchant + resilience — 4 h [must]

**What to build.** Swap market's `PaymentsGateway` Protocol implementation from the in-process adapter to an HTTP adapter using an `sk_` key, behind a flag (flipped in step 9 of the cutover).
- Separate connect and read timeouts, chosen from measured atlaspay latency, not defaults.
- Jittered retries only on retryable outcomes, under a **retry budget** (a cap on retries as a fraction of normal traffic, so retries cannot multiply load during an outage; you met the multiplication in S8's gateway).
- A breaker.
- **On a timeout the outcome is unknown**: the payment may exist. Retry with the **same** `Idempotency-Key` (stored before the first attempt). A new key on retry is how double charges happen.
- A **bulkhead**: a hard cap on how much of market's capacity calls to atlaspay may occupy (a bounded connection pool or semaphore per downstream), failing fast when full.

**PAIN-FIRST** (P9 D154–D156 did this with Toxiproxy; P10 D163–D165 added the bulkhead).
1. Put Toxiproxy between market and atlaspay and add **2 s of latency with 0% errors**.
2. Before you run anything, predict what the breaker does, what market's worker threads do and what happens to catalog p95; commit the prediction. Then run locust on a mix of checkout and catalog traffic, with a constant-rate oha probe on one catalog endpoint for the p95. Screenshot the breaker-state panel next to catalog p95, and take a py-spy dump of a market worker. (Check your prediction in §16.)
3. Add the bulkhead. Size it with Little's law (concurrency = throughput × latency) from locust numbers, not by feel. Repeat, and record what checkout and catalog do now.
4. Record both runs in `docs/evidence/s09/toxiproxy-bulkhead.md`. This is your second STAR story. The two configurations × 3 runs are about 65 min of unattended runtime: weekend block.

**Acceptance criteria.** A forced timeout followed by a retry creates exactly one intent; the retry budget holds during a total outage (retries ≤ your stated ratio); with the bulkhead, catalog p95 under the Toxiproxy run stays within the noise band of the baseline.

### 4.9 Saga — 2.5 h [must]

**What to build.** An **orchestrated** saga in market that cancels one vendor group of a paid order: refund via atlaspay (`/v1/refunds`) → reverse that vendor's transfer (`/v1/transfers`) → restock. With separate charges and transfers, a refund does not touch transfers, so the platform must reverse them itself (Stripe works the same way).
- A `sagas` table (id, type, state, current step, attempts, last error). The orchestrator writes the step it is about to run **before** running it, so a crash resumes instead of restarting.
- `POST` returns **202 + Location** pointing at the saga resource (P7 D115–D120 built this for FleetTrack; returning 200 while work is still running is the lie that pattern exists to stop).
- Each step is idempotent with its own key (for example saga id plus step name as the `Idempotency-Key`).
- Identify the **pivot step**: after the money is back with the buyer you cannot "un-refund", so steps after it must be retried until they succeed (or parked for a human), never compensated.
- FleetTrack used choreography; write down why this saga is orchestrated (hint: where do you ask "where is this cancellation stuck?").

**PAIN-FIRST.** Kill the worker between the refund and the transfer reversal. Observe the half-done state in the `sagas` table and in atlaspay. Then prove resume: restart and watch it complete without a second refund.

**Acceptance criteria.** A mid-saga failure test shows `failed` or `compensating` with the exact step; a retry never double-refunds; ADR-034 is written.

### 4.10 Auth service — 11.5 h [must]

Suggested split: RS256, JWKS and rotation 2 h; refresh families and data move 2 h; Authorization Code + PKCE and the BFF 2.5 h; Keycloak federation and the OIDC negatives 2 h; Google as a second provider 1 h; client credentials and the bot's delegated calls 1.5 h; argon2 off the event loop 0.5 h.

**What to build.**
- **RS256 with `kid` and JWKS.** auth alone holds private keys (in its DB, encrypted, or in Vault). Verifiers fetch **JWKS** (a JSON document listing the public keys a verifier may use, each identified by `kid`) from `/.well-known/jwks.json` and verify locally with no network call per request. Pin the accepted algorithm to RS256 in every verifier: never take `alg` from the token header (the "alg confusion" attack makes a verifier treat the public key as an HS256 secret, and `alg: none` skips verification). Allow a small clock-skew leeway on `exp`/`nbf`/`iat`, agreed across services and tested at the boundary with freezegun.
- **Rotation with 0 × 401** (P5 D79–D84 did this under load):

```
t0  JWKS = {A}      sign with A
t1  JWKS = {A, B}   sign with A    wait ≥ the verifiers' JWKS cache TTL
t2  JWKS = {A, B}   sign with B    A-signed tokens stay valid until they expire
t3  JWKS = {B}      sign with B    t3 ≥ t2 + access-token TTL + leeway
```

```
client            market (verifier)                                   auth
  |─ Bearer JWT ─▶| header: alg=RS256 (pinned), kid=B
  |               | kid in cached JWKS? no ─▶ refetch (with a cooldown) ─▶| GET /.well-known/jwks.json
  |               |◀───────────────────────────────────────────────────────| {keys: [A, B]}
  |               | verify signature with B; check iss, aud, exp/nbf (+leeway), scope
  |◀── 200 / 401 ─|
```

- **Refresh families move into auth** (from market's identity module, S3). Reuse the S3 rules: rotation on every refresh, reuse revokes the family, hashes only.
- **Moving identity data.** Credentials (password hashes, refresh families, OIDC links) move to the `auth` DB. Reuse the step-2 replication technique or do a one-off backfill under a short login freeze; justify the choice in the runbook. During a transition window market accepts both its old HS256 tokens (until the longest one expires) and auth's RS256 tokens, then HS256 verification is deleted. This closes the S8 finding: `ai` holds only public keys now.
- **First-party Authorization Code + PKCE.** **PKCE** (Proof Key for Code Exchange) lets the client prove at the token endpoint that it is the same party that started the authorization request. market's Django session is the **BFF** (backend-for-frontend: a server that holds tokens on behalf of the browser; it is the pattern the OAuth 2.0 for Browser-Based Applications BCP, RFC 10017 [verify], recommends); market is a **confidential client** of auth, and the browser never sees a token:

```
Browser                    market (BFF, server-side session)                    auth /oauth2/*
  |── GET /login ────────────▶| code_verifier (random); code_challenge = S256(verifier); state
  |                           | store {state, verifier} in the session
  |◀── 302 /oauth2/authorize?response_type=code&client_id=market&redirect_uri=…
  |          &code_challenge=…&code_challenge_method=S256&state=…
  |────────────────────────────────────────────────────────────────────────────▶| log the user in
  |◀── 302 market /callback?code=…&state=… ─────────────────────────────────────|
  |── GET /callback ─────────▶| state == session.state, else reject
  |                           |── POST /oauth2/token (code, verifier, client auth) ─▶| S256(verifier) == challenge?
  |                           |                                                     | code single-use? redirect_uri exact?
  |                           |◀── access token (RS256) + refresh token (family) ───|
  |                           | keep tokens server-side; rotate the session id
  |◀── Set-Cookie: session (HttpOnly, Secure, SameSite) — no token in the browser
```

- **OIDC federation to Keycloak 26.7** with account linking. Here auth is a relying party of Keycloak, and on success it issues **its own** tokens:

```
Browser               auth /oidc/keycloak/*                               Keycloak (realm "atlas")
  | picks "Keycloak" on auth's login page
  |── GET /oidc/keycloak/start ─▶| state, nonce, PKCE verifier saved with the pending authorize request
  |◀── 302 …/protocol/openid-connect/auth?…&state&nonce&code_challenge
  |──────────────────────────────────────────────────────────────────────▶| user logs in
  |◀── 302 /oidc/keycloak/callback?code&state ─────────────────────────────|
  |── callback ─────────────────▶| check state
  |                              |── token request (code, verifier, client secret) ──▶|
  |                              |◀── id_token, access_token ─────────────────────────|
  |                              | verify id_token: signature via Keycloak JWKS (alg pinned), iss == realm URL,
  |                              |   aud contains our client_id, nonce == saved, exp/iat with leeway
  |                              | link (iss, sub) → auth user; resume the original /oauth2/authorize
```

What each check prevents (learn this table, it is an interview favourite):

| Check | What it prevents |
|---|---|
| `state` | Login CSRF: an attacker making your browser finish **their** login, so you end up in their account. It binds the callback to the browser session that started the flow. |
| `nonce` | ID-token replay or injection: an ID token obtained elsewhere cannot be used to complete **this** login, because it does not carry the nonce you stored. |
| PKCE | Authorization-code interception and injection: a stolen code is useless without the `code_verifier`. Current guidance (the OAuth 2.0 Security BCP, RFC 9700) recommends it for confidential clients too. |
| `aud` | Token substitution and confused-deputy bugs: a token issued for another client or service (for example one minted for `ai`) is refused here. |
| `iss` | Mix-up between issuers: a token from a different IdP, or signed with keys that do not belong to the issuer you trust, is refused. |
| Signature + pinned `alg` | Forgery, `alg: none`, and algorithm confusion. |
| Exact `redirect_uri` | Codes sent to an attacker-controlled redirect. |

  Account linking keys on `(iss, sub)`, never on email alone. Ask yourself: what happens if you auto-link on an email the IdP never verified?
- **Google as a second provider** on the same `/oidc/{provider}` flow, live on staging only; the CI negatives stay against Keycloak. With two real issuers, the `iss` check and the `(iss, sub)` linking key stop being theoretical. Add a test, against a crafted ID token from a fake IdP, that an email with `email_verified` false never auto-links to an existing account.
- **Client-credentials JWTs** between services. bot, ai and the rest call `/oauth2/token` with `grant_type=client_credentials` and get a short-lived JWT with `sub` = the client, `aud` = the target service and a `scope` list. The receiver checks `aud` and scope. This replaces the bot's static service token from S3.
- **The bot acts for a linked user, never as anyone.** A plain client-credentials token says only "this is the bot", so market would have to trust whatever Telegram user id the bot asserts, including for the S8 refund-approval button. Close that: auth issues the bot a token with a narrow scope (for example `bot:linked_user`); market accepts a Telegram user id only on tokens with that scope, resolves the link and applies that user's own permissions. The approving ops user is re-verified through their linked account at tap time, and a refund approved through the bot must be below an amount cap you choose; larger refunds are Admin-only in the web UI. Record the blast radius of a leaked bot credential in ADR-031. Tests: bot token + unlinked Telegram id → 404; a bot approval above the cap is refused; a rotated bot credential stops working.
- **market as BFF with a shadow users table.** market keeps `identity_user` (the allow-listed FK target) as a projection fed by `user.registered`, `user.updated`, `user.erased` through the inbox. Ask yourself: a user registers and places an order one second later, before `user.registered` arrived. What does market do? (Hint: the verified token already carries the claims you need.)
- Libraries: Authlib 1.8 with joserfc (`authlib.jose` is deprecated).
- argon2 is CPU-bound. In an async service one hash blocks the event loop for every request on that worker (step 1's pitfall list). Measure the p99 of an unrelated endpoint with the hash inline, with `asyncio.to_thread` and with a `ProcessPoolExecutor`, as in the S2 concurrency exercise. Then write down why a thread is enough here (check whether argon2-cffi releases the GIL while it hashes) and when you would need processes instead.

**PAIN-FIRST.**
1. Rotate naively under locust: publish B and start signing with B at the same moment. Count the 401s. Then rotate with the timeline above and with refetch-on-unknown-`kid` (with a cooldown, so random `kid`s cannot force a JWKS fetch per request) and reach 0 × 401. Record `docs/evidence/s09/rotation-locust.csv`.
2. Write the OIDC negative tests **before** the checks exist and watch them pass the attack: wrong `state`, wrong `nonce`, ID token for a second Keycloak client (wrong `aud`), expired token, `alg: none`, bad signature. Then add each check and watch each test turn red → green.

**Acceptance criteria.** Rotation under locust with 0 × 401; a token signed by a retired key is rejected; all OIDC negatives run in CI against a real Keycloak through headless Playwright; "Sign in with Google" works on staging and the unverified-email test is green; the three bot-delegation tests pass; the argon2 loop-lag numbers are recorded; `ai` can no longer produce a token market accepts as admin (the S8 finding is closed, with the test that proves it).

### 4.11 MCP OAuth — 1.5 h [must]

**What to build.** ai's `/mcp` (Streamable HTTP) becomes an OAuth-protected resource with Keycloak as the authorization server; stdio stays for local use. Target the MCP spec revision 2026-07-28 (stateless Streamable HTTP) and the Python SDK 2.x you used in S8 (as of 2026-09; re-check both at stage start). The MCP server validates Keycloak-issued access tokens: issuer = the realm, audience = the `/mcp` resource URL. Tools stay read-only and the static token from S8 is removed. Three current facts to plan around ([Keycloak's MCP guide](https://www.keycloak.org/securing-apps/mcp-authz-server), [the MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)):
- Keycloak 26.7 ignores the RFC 8707 `resource` parameter that MCP clients send. Bind the audience with a client scope whose Audience mapper puts the `/mcp` URL into `aud`, and have MCP clients request that scope. Otherwise the wrong-audience test below fails in a confusing way.
- ai itself must publish OAuth protected-resource metadata at `/.well-known/oauth-protected-resource` (RFC 9728) and answer a 401 with `WWW-Authenticate: Bearer resource_metadata=…`. Keycloak does not do this for you.
- The 2026-07-28 spec deprecates dynamic client registration in favour of Client ID Metadata Documents, which Keycloak supports only experimentally. Use a pre-registered client for your test client, and record DCR vs CIMD in ADR-031.

Two questions to answer in ADR-031:
- market accepts only auth-issued tokens. When an MCP tool needs a user's order data, which token does `ai` send to market, and why must it **not** be the token the MCP client sent to `ai`? (Passing a token through to a service it was not issued for is the confused-deputy problem again.)
- Keycloak now issues access tokens. How is that compatible with the invariant "only auth mints user tokens"? (Hint: who accepts which issuer.)

**Acceptance criteria.** An MCP client completes the OAuth flow and queries an order; a token with the wrong audience is refused; a market-issued token is refused by `/mcp`; an unauthenticated request gets a 401 whose `WWW-Authenticate` header points at the protected-resource metadata.

### 4.12 Pact — 1 h [must]

**What to build.** Consumer-driven HTTP contracts market → atlaspay (create intent, refund, transfer reversal) and market → auth (token endpoint, JWKS shape), published to a Pact broker; provider verification in atlaspay's and auth's CI; `can-i-deploy` gates each deploy.

**Acceptance criteria.** Renaming a response field atlaspay's consumer uses fails atlaspay's CI before any deploy.

### 4.13 Drills + SD1 — 6.5 h [must]

Suggested split: payment links 2 h; the bot's pay button 0.5 h; the weekly drill, about 45 min a week (4 h over the five weeks, including the SD18 revisit in §9).

**What to build.**
- AtlasPay **payment links** at `https://pay.<domain>/l/{code}` (Proj26 D169–D170): a base62 code maps to a stored payment-link object; the redirect goes to the provider checkout; cache-aside in redis-cache; a deleted code returns 404 immediately, never a stale redirect until the TTL ends.
- **The bot's pay button** (the bot's primary payment path, E6). When an order is `awaiting_payment`, the `bot.notifications` message carries an inline URL button to a `/l/{code}` that market creates through AtlasPay's public API with an Idempotency-Key derived from the order id (ask yourself what else the key must contain so that a deleted link can be replaced instead of replayed). After payment, the webhook → market → `bot.notifications` path sends "paid".
- The weekly drill: one SQL or DSA problem and the week's interview questions.

Questions for you: Proj26 used a counter-based code. Is an enumerable code acceptable for a payment link? What leaks if someone walks the code space? Why is 301 the wrong redirect here?

**Acceptance criteria.** A delete-then-GET test gets 404 with a warm cache; cold vs warm p95 recorded; a `Dispatcher.feed_raw_update()` test shows the pay button's URL resolves to a live code; after the link is deleted, the bot gets a fresh one for the same order; one staging E2E goes from the button to "paid".

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| The cutover loses 0 payments and 0 idempotency keys | Replication, bounded freeze, drain, verification set, exit criterion before contract | Rehearsal script asserting equal counts, checksums, trial balance and idempotency-key counts; 20 pre-cutover provider ids replayed under each provider's replay rule (`result`/`error` byte-identical, `id` equal to the new request's id) |
| Replies to a repeated provider request are deterministic and follow each provider's replay rule | Stored `result`/`error` members wrapped in a new envelope with the current JSON-RPC `id`; Click's -4 for a completed payment | Replay check with provider-sim's new-id chaos switch on |
| market never reads the atlaspay DB | Separate cluster; market holds no DSN or role on pg-atlaspay | Settings/env scan of every market process finds no pg-atlaspay DSN; `pg_roles` on pg-atlaspay lists only `atlaspay_*` roles after contract |
| market learns payment outcomes only from verified webhooks | `market.payment-events` deleted at contract; ordering's payment consumer is the webhook receiver | A `payment_intent.succeeded` published on `atlas.events` changes nothing in market; the same outcome as a verified webhook marks the order paid once |
| Every attempt against atlaspay gets a shadow fraud score | The fraud v1 path ported into atlaspay (4.2 step 1) | Count of attempts = count of stored scores with `model_version`, checked in the exit criterion |
| A live key never touches test objects | `livemode` on every object; mode comes from the key; one central filter | {pk, sk, rk} × {test, live} × object-mode matrix: cross-mode reads return 404 |
| Webhooks are verified before parsing | Receiver verifies HMAC and timestamp on raw bytes first | Invalid JSON + bad signature fails on signature; stale `t` rejected; rotation window accepts both secrets |
| Only auth mints user tokens; rotation causes 0 × 401 | Private keys only in auth; verifiers hold JWKS; pinned `alg`; pre-published rotation | Locust rotation run (0 × 401); retired-key token rejected; no signing key in any other service's config |
| One merchant's limit never affects another | Token bucket per key × mode × tier | Merchant A at 10× its limit; merchant B 0 × 429 and p95 within noise |
| One DB role per service | `<svc>_app`, `<svc>_migrator`, `<svc>_ro`; dynamic credentials are members of `atlaspay_app` | CI query of `pg_stat_activity` / `pg_roles` per cluster during the acceptance run |
| The S5 invariants still hold on atlaspay | Same domain library, same acceptance suite | `sim-acceptance` green against atlaspay with the chaos switches |

---

## 6. Tests to write

- **Cutover:** schema-diff test (publisher vs subscriber), shadow corpus replay (0 diffs, no masks, reply `id` = request `id`), rehearsal verification script, pre-cutover replay check with the new-id chaos switch, trigger-fires-after-promotion test, webhooks-only test for market (after contract), shadow-score coverage check.
- **Acceptance:** `sim-acceptance` as a matrix `target = [market, atlaspay]` until contract, then atlaspay only.
- **Keys:** the scope/mode matrix; rotation grace; prefix lookup with constant-time compare; no key material in logs.
- **Versioning:** old-pinned and latest client tests; one transform unit test.
- **Webhooks:** signature (valid, bad, stale, two secrets), dedup on event id, webhook-before-intent, dispatcher kill and redelivery, ring movement benchmark.
- **Limiter:** isolation between merchants, boundary headers, Redis-kill fail-open.
- **Vault:** lease expiry survival, KEK rotation and rewrap, crypto-shred of atlaspay data.
- **market as merchant:** timeout then retry with the same key → one intent; retry budget under outage; nightly Toxiproxy run with and without bulkhead.
- **Saga:** mid-saga failure, resume after crash, no double refund.
- **Auth:** rotation under locust, retired-key rejection, clock-skew boundary, `alg` pinning, OIDC negatives against Keycloak (state, nonce, aud, expiry, signature), the unverified-email no-auto-link test, refresh reuse revokes the family, client-credentials `aud`/scope checks, the bot delegation tests (unlinked id → 404, above-cap approval refused, rotated credential dead), just-in-time shadow user, the argon2 loop-lag measurement.
- **MCP:** OAuth round trip; wrong-audience refusal; 401 with `WWW-Authenticate` pointing at the protected-resource metadata.
- **Pact:** consumer tests in market; provider verification in atlaspay and auth.
- **Payment links and the bot:** delete-then-GET 404 with a warm cache; the pay button resolves to a live code (`feed_raw_update`); a replaced link after deletion.

See [testing-and-ci](testing-and-ci.md) for how these slot into the whole matrix.

---

## 7. CI changes

| Job | What it gates |
|---|---|
| Reusable workflows per service with a path-filtered matrix | Each service's lint, typecheck, unit and integration jobs run only when its paths (or a lib it depends on) change |
| `pact-verify` + Pact broker + `can-i-deploy` | A provider deploy cannot break a consumer contract |
| `oasdiff` | No breaking change to a supported `Atlas-Version` schema |
| Keycloak OIDC negatives (headless Playwright) | Every check in the §4.10 table stays in place |
| `shadow-diff` | Corpus replay against both implementations is byte-identical in the `result`/`error` member, and every reply's `id` equals its request's id (until contract, then kept as a regression suite against recorded replies) |
| Nightly Toxiproxy | The bulkhead keeps catalog p95 flat under a slow atlaspay |
| `sim-acceptance` (extended) | S5 suite green against atlaspay |

---

## 8. ADRs and documents

**ADR-030 — AtlasPay split.**
- *Questions:* What did the split gate measure, and does it justify extraction? Did the S6 pool bulkhead fix the stall, and why or why not? Which processes held provider secrets before and after? What is the SLO gap? Why must an operator be neutral towards its own merchant? Why FastAPI instead of moving the Django module as-is?
- *Numbers:* lock-stall callback p99 before and after (median and min–max over 5 runs); % Payme `-32400`/timeouts and Click errors during the stall; checkout p95; DB pool saturation; count of processes holding provider secrets before and after; freeze duration and held-request count from the cutover.
- *Counter-argument it must address:* "**Extract it as a Django service**" (move, do not rewrite: lower risk). The answer must rest on `atlaspay-domain` being framework-free, so only the adapters were rewritten, plus byte-level protocol control. It must include the clause "if the numbers don't hurt, say so".

**ADR-031 — auth split.**
- *Questions:* RS256 alone does **not** need a split (the monolith could sign RS256 and publish JWKS), so what does? Issuer neutrality across trust domains (market, atlaspay, ai, bot and MCP clients all trust one issuer none of them controls); the new OIDC/PKCE/MCP-client surface (strangler rule: new capability lands in the new service); blast radius. The S6 refresh slowdown is the weakest reason: refresh never touches `ordering_order`, so it slowed only through the shared workers and DB pool. Did a separate pool for the auth endpoints (the cheap fix, measured in 4.1) remove it? If it did, that reason carries no weight, and the ADR says so. How do Keycloak-issued MCP tokens coexist with "only auth mints user tokens"? What can a leaked bot credential do, given the scope and the amount cap? DCR vs CIMD for MCP clients (4.11).
- *Numbers:* refresh p99 during the lock drill with the shared pool, with a separate auth pool (4.1) and after the split; rotation 401 count naive vs planned; token verification cost per request (local JWKS vs a network call).
- *Counter-argument:* "**Buy Keycloak or Auth0** and keep identity in the monolith". Admit that this is the usual real-world answer, and explain what building it teaches.

**ADR-032 — keys, versioning and webhooks.**
- *Questions:* key format, presentation (`Authorization: Bearer`), storage and the pepper; why not bcrypt; scopes; rotation grace; livemode isolation; the version pin and the transform chain; the deprecation window and headers; the webhook signature scheme, tolerance, rotation and retry schedule; the no-ordering contract; the ring.
- *Numbers:* verification cost per request with SHA-256 vs bcrypt (measured); fraction of merchants moved 3 → 4 with the ring vs `hash % N`; per-dispatcher load spread for two vnode counts; `webhook_delivery_lag_seconds` p95.
- *Counter-argument:* "Version in the URL (`/v2`) like LedgerBase did" — say what dated versions give merchants that URL versions do not, and what they cost you.

**ADR-033 — secrets and data governance.**
- *Questions:* what each process can read from Vault; dynamic credentials vs static; envelope encryption; how erasure works against an append-only ledger, event logs (outbox partitions, RabbitMQ messages), Mongo transcripts, embeddings and backups (built for atlaspay's database in the must tier; designed for the rest); what is pseudonymous and where the mapping lives. Build on `docs/privacy/data-governance.md` v1 from S6 and update the S5 threat model with the new public surface.
- *Numbers:* the retention per data class; the erasure horizon (including backups); time to erase one subject; number of places personal data lives.
- *Counter-argument:* "Vault is operational overhead for one developer; SOPS/age plus environment variables (S6) are enough."

**ADR-034 — why not 2PC.**
- *Questions:* why a saga; why orchestration here and choreography in FleetTrack; which step is the pivot; what happens when a compensation fails.
- *Numbers:* saga completion p95; share of sagas that ended parked in the failure test.
- *Counter-argument:* "Postgres supports `PREPARE TRANSACTION`, so use real distributed transactions." Answer with blocking coordinators, in-doubt transactions holding locks, HTTP APIs and providers that cannot take part, and the availability cost (P10 D163–D165). Note that Citus will use 2PC internally in [Stage 12](stage-12-data-at-scale-fraud.md), which is why its design avoids cross-shard entries.

**Other documents:** `docs/runbooks/atlaspay-cutover.md` (steps, freeze design, verification set, rollback decision, masks); `docs/evidence/s09/*`; `docs/star/` two stories.

---

## 9. System design session

- **SD1 URL shortener — built-lite** as AtlasPay payment links (W40). Reuse the Proj26 design, then argue what changes when the "URL" carries money: enumeration, redirect caching, deletion.
- **SD18 payment system — revisited** (W42, per the [system-design-map](system-design-map.md)). In S5 you built the payment system inside a monolith; now whiteboard it as a service with a public API: keys, idempotency, webhooks, versioning, the ledger boundary and reconciliation. Compare your whiteboard with the repo afterwards and write the differences in `docs/sd/sd18-v2.md`.
- The concept map entries you now own: **strangler fig**, **logical replication**, **saga / why not 2PC**, **consistent hashing** (the ring), **bulkhead** (outbound).

---

## 10. Interview questions this stage lets you answer

1. Why was AtlasPay split, and with what numbers?
2. Walk through the shadow cutover, step by step. Where could it have lost a payment?
3. Why is market a merchant of its own payment operator?
4. Your breaker was closed and the system still died. Why?
5. What do PKCE, `state` and `nonce` each prevent? And `aud`, and `iss`?
6. How do you erase a user from an append-only system? What about the backups?
7. How do you evolve a public API without breaking old merchants?
8. What does logical replication not replicate, and what did that force in your runbook?
9. Why can you not canary a change of write ownership?
10. Why SHA-256 with a pepper for API keys, but argon2 for passwords?
11. How does your webhook signature prevent replay, and how do you rotate the secret without dropping deliveries?
12. A payment request timed out. What do you do next?
13. How do you rotate a JWT signing key with zero 401s? What is algorithm confusion?
14. How many merchants moved when you added a fourth dispatcher, and why not `hash % N`?
15. Why an orchestrated saga here when FleetTrack used choreography? What is the pivot step?
16. Your bot calls market for a Telegram user. How does market know the bot is not lying about which user, and what can a leaked bot credential do?

---

## 11. Common mistakes to watch for

- A shadow that commits, publishes events or sends webhooks, which breaks replication or duplicates side effects.
- A byte diff made "green" by a mask list that hides real differences.
- Forgetting what logical replication skips: sequences, DDL, generated column values. Or publishing a table with no replica identity and breaking the monolith's UPDATEs.
- Leaving the replication slot behind after the cutover, so pg-market's disk fills weeks later.
- Leaving `market.payment-events` bound after the switch, so market processes every outcome twice (queue and webhook) and keeps a private channel no outside merchant has.
- Replaying stored Payme reply bytes verbatim, old JSON-RPC `id` included; forgetting to port the fraud shadow scoring, so it stops silently at the switch.
- Parsing a webhook before verifying it, verifying against re-serialised JSON instead of the raw bytes, or comparing signatures with `==` instead of a constant-time compare.
- bcrypt on every API request; API keys stored in plaintext, logged, or used as Redis key names.
- Retrying a timed-out payment with a **new** Idempotency-Key (a double charge).
- Trusting the breaker against a dependency that is slow but never fails, or sizing the bulkhead by feel.
- A JWKS with no `kid` (rotation becomes a flag day), signing with the new key before verifiers have it, or refetching JWKS on every unknown `kid` without a cooldown.
- Taking `alg` from the token header; not checking `aud`; skipping `nonce` because "we already check `state`"; auto-linking accounts by unverified email.
- Dynamic database roles that own tables, so revocation fails; "secrets in Vault" that were never rotated.
- Calling crypto-shredding "erasure" without accounting for the backup retention window.

---

## 12. How real companies differ

- Most teams **buy identity** (Auth0, Okta, Keycloak run as a product) instead of running their own issuer, and keep a thin user projection in each service. ADR-031 must say so. Building it once is how you learn what you are buying.
- Large migrations often use **CDC** (for example Debezium) or dual writes verified by an experiment framework (GitHub's Scientist library is the classic shadow-comparison tool), and keep **reverse replication** running for a rollback window. Your logical replication plus a mirror-mode simulator is the same idea at learning scale.
- Stripe-scale APIs implement versioning as **version-change modules** in a gateway layer and run webhook delivery as its own platform (companies such as Svix sell exactly that). Your single transform and ring are the minimal honest version of both.
- Service-to-service trust is often handled by a **service mesh with mTLS** plus token exchange (RFC 8693) for delegation, instead of every service verifying JWTs itself. mTLS arrives as a [Stage 10](stage-10-kubernetes-grpc-inventory.md) stretch.
- A real AtlasPay would need a Central Bank licence under ЗРУ-578 Art. 15, or would use the providers' own splits (Payme `receivers`, Click Split Shop) (ADR-017). The simulated money is why the learning version is legitimate.

---

## 13. Deliberately not doing

| Item | Why | When it arrives |
|---|---|---|
| Per-module databases for what stays in market | No DB-level forcing problem; logical ownership (prefixes, roles, FK ban) is enough | Only when a named trigger in E2 fires (for example the search-indexer at > 60 s index lag) |
| Consent screens and dynamic client registration | That is where buying Keycloak beats building. For MCP clients Keycloak provides DCR (deprecated by the MCP 2026-07-28 spec) and experimental CIMD; your test client is pre-registered (4.11) | Not in Season 1 |
| A service mesh | Two new services do not justify it; JWT + NetworkPolicy come first | Linkerd mTLS is a [Stage 10](stage-10-kubernetes-grpc-inventory.md) stretch |
| Kubernetes | Compose still copes; you record its container count now as evidence | [Stage 10](stage-10-kubernetes-grpc-inventory.md) (ADR-035) |
| gRPC from atlaspay to the ledger and to fraud | The ledger has no forcing problem yet | [Stage 12](stage-12-data-at-scale-fraud.md) |
| Kafka / CDC for the cutover or the outbox | Logical replication is enough for a one-time move | Season 2, stage 2E |
| Disputes | Neither provider has a dispute protocol | Whiteboard only (S5 stretch) |

---

## 14. Stretch

Only if the must tier closes early, in any order (Google OIDC moved to the must tier, 4.10):
- **Crypto-shredding beyond atlaspay** [1]: per-subject keys for the event log (outbox partitions, RabbitMQ payloads) and for ai's Mongo transcripts, with a test that a shredded subject is unreadable in both.
- **Keycloak SSO for Django Admin** [1].
- **IP allowlist per key** [0.5].
- **A second version transform** [1], to prove the chain composes.
- **A webhook resend UI and endpoint** [1].
- **Payme `receivers` split** [1.5]: a design where the provider splits the money natively instead of AtlasPay holding seller funds.

---

## 15. Definition of done

- [ ] Split gate re-run recorded (5 runs each, bulkhead off and on; `docs/evidence/s09/split-gate-before.csv`, including refresh p99); ADR-030 and ADR-031 have numbers and counter-arguments
- [ ] atlaspay serves `pay.<domain>` (`/v1/*`, `/providers/*`, `/l/*`) from its own cluster; `libs/atlaspay-domain` changes recorded
- [ ] Fraud v1 ported: shadow scores with `model_version` recorded for 100% of attempts against atlaspay; the tsdb and fraud consumers run as atlaspay processes
- [ ] Cutover runbook (required properties, your own ordered steps) executed twice (rehearsal + real); rehearsal log with timings, freeze duration and held-request count
- [ ] Shadow corpus diff = 0 with no masks; live-mirror masks justified
- [ ] Exit criterion met: S5 acceptance suite green against atlaspay **and** reconciliation diff = 0; injected drift still flagged
- [ ] 20 pre-cutover provider ids replayed under each provider's replay rule (`result`/`error` byte-identical, `id` equal to the new request's id); 0 payments and 0 idempotency keys lost
- [ ] Old `payments_*` tables contracted; replication slot gone; provider secrets gone from market; `market.payment-events` deleted and the webhooks-only test green
- [ ] Keys: the {pk, sk, rk} × mode × object mode × scope matrix green; a rotated key fails after its grace period; no key material in a day's logs
- [ ] Versioning: an old-pinned and a latest client pass against one build; the red `oasdiff` run kept as evidence
- [ ] Webhooks: an invalid body with a bad signature fails on the signature; a triple delivery has one side effect; `ring-3-to-4.csv` recorded
- [ ] Limiter: merchant A at 10× gets 429s while merchant B sees 0 × 429; the Redis-kill run shows fail-open with the alert firing
- [ ] Vault: KV, dynamic credentials survive a lease expiry, KEK rotated, crypto-shred of atlaspay data demonstrated
- [ ] market pays over HTTP; Toxiproxy run with and without bulkhead recorded
- [ ] Saga with 202 + Location and a passing mid-saga failure test
- [ ] auth: RS256 + JWKS; rotation under locust with 0 × 401; Keycloak login with all OIDC negatives green in CI; "Sign in with Google" on staging and the unverified-email test green; client credentials in use; bot delegation tests green; the S8 minting finding closed
- [ ] MCP OAuth round trip works; wrong-audience token refused; protected-resource metadata served
- [ ] Pact broker with `can-i-deploy` gating
- [ ] Payment links at `/l/{code}` with the delete-then-404 test; the bot's pay button test and one staging E2E
- [ ] ADR-030 … ADR-034 written
- [ ] Two STAR stories in `docs/star/`: **the shadow diff you caught**; **the closed-breaker outage**
- [ ] Postmortem paragraph: what the cutover taught you, and what you would do differently
- [ ] Tag `v0.9`

---

## 16. If you get stuck

**4.1 Gate.** Can you reproduce the S6 lock-queue stall on demand? If not, reread your S6 evidence before measuring anything. Are your runs inside each other's spread (the ADR-002 noise rule)? Then the honest answer may be "no difference".

**4.2 Strangler.** Which state does each implementation see when the mirrored request arrives? Draw it on paper with timestamps. If the apply worker is stuck, what does the subscriber's log say about a conflicting key? What exactly is in your verification set, and would it notice one missing idempotency row? Read the PostgreSQL 17 manual chapter *Logical Replication* (architecture, restrictions, monitoring); logical replication is new to the curriculum. For the async pitfalls, reread P1 D13–D18 (the blocking-call demo in [StockPilot](../python/01-stockpilot.md) §10) and the SQLAlchemy asyncio guide.

<details>
<summary>Check your prediction (step 2, the table without a primary key)</summary>

The **publisher** refuses the UPDATE, with an error saying the table has no replica identity and publishes updates. The subscriber never sees anything. That is why a careless publication breaks production writes in the monolith, not just the copy.
</details>

**The cutover runbook, staged hints.** Open one at a time, only after your own draft has failed a rehearsal.

<details>
<summary>Hint 1</summary>

If your rehearsal answered a callback twice, or not at all, ask where the freeze should live: in the old owner, in the router, or in the new owner? Which of them can hold a request and still answer it exactly once?
</details>

<details>
<summary>Hint 2</summary>

One shape that works: the freeze lives in the **new** service. atlaspay goes from SHADOW to a HOLD mode in which write requests wait, bounded, until it becomes PRIMARY, and the route switch happens while atlaspay holds. Now list what must be drained in market before promotion, and what the last check before promotion is.
</details>

<details>
<summary>Hint 3</summary>

Writers people forget: the payments Beat entries and the payments Celery queue; checkout's own payment writes (answer 503 with `Retry-After` while frozen); market's outbox rows for `payment_intent.*`; sequences, if any table uses identity columns; the subscription itself, which must stop before atlaspay writes.
</details>

**4.3 Keys.** If a key leaks, what can an attacker do with it, and what can they do with a DB dump alone? Reread P9 D151–D153 (API-key auth for server-to-server callers).

**4.4 Versioning.** What is the smallest change that forces a transform? Reread P6 D97–D101 ([LedgerBase](../python/06-ledgerbase.md) `/v1` → `/v2`, Deprecation and Sunset).

**4.5 Webhooks.** Are you verifying the bytes you received, or bytes you rebuilt? Reread P9 D148–D149 (HMAC verification, provider-event idempotency) and P8 D131 ([phase-5](../../phase-5-scaling-architecture.md), the consistent-hashing ring).

**4.6 Limiter.** What does each pod know about the others when Redis is gone? Reread your S3 Lua work and `docs/rate-limit-algorithms.md`.

**4.7 Vault.** Who owns the tables, and what happens to a role that owns something when Vault revokes it? Reread P9 D151–D153 (Vault dynamic credentials, transit, KEK rotation).

**4.8 Resilience.** What is each thread doing during the Toxiproxy run? Take a py-spy dump. Reread P6 D94–D96 (retry and breaker), P9 D154–D156 (the Toxiproxy observation) and P10 D163–D165 (bulkhead sized from locust).

<details>
<summary>Check your prediction (the 2 s latency run)</summary>

The breaker stays **closed**, because nothing fails: every call succeeds, just slowly. market's worker threads fill up waiting on atlaspay, and unrelated catalog endpoints climb in latency because they wait for a free thread. With the bulkhead, checkout degrades and fails fast while catalog stays flat. A breaker protects you from a dependency that fails; a bulkhead protects you from one that is slow.
</details>

**4.9 Saga.** After which step can you no longer undo? Reread P7 D115–D120 ([FleetTrack](../python/07-fleettrack.md) §8 and the `sagas` table).

**4.10 Auth.** Draw the rotation timeline with real TTLs before touching code. For each OIDC check, can you describe the attack it stops in one sentence? Reread P5 D79–D84 (RS256, JWKS, rotation under load) and P5 D85–D90 (Keycloak, PKCE, ID-token validation, refresh families) in [CarePoint](../python/05-carepoint.md).

**4.10 Google and the bot.** Which claims does Google's ID token carry that Keycloak's did not, and which one decides whether you may link by email? For the bot: which token proves "this is the bot", and what extra check proves "this user tapped the button"?

**4.11 MCP.** Who is the audience of the token the MCP client sends, and who is the audience of the token `ai` sends to market? If the wrong-audience test passes for the wrong reason, decode the token Keycloak issued and look at `aud`: did your client request the scope that carries the Audience mapper? Read [Keycloak's MCP guide](https://www.keycloak.org/securing-apps/mcp-authz-server) and the authorization section of the MCP 2026-07-28 spec.

**4.13 Payment links.** Reread Proj26 D169–D170 in [phase-6](../../phase-6-capstone.md) (base62 codes, deleted code → 404, cache invalidation).
