# Stage 04 — Async, events, boundaries, search

| | |
|---|---|
| **Weeks** | W13–W17 (5 weeks) |
| **Hours** | 60 must + 7 stretch (67 total). The must tier includes the vendor bot flow in §4.6. |
| **Architecture at start → at end** | `market` as a layered monolith with a polling `bot`, `redis-cache` and `redis-state`. Checkout sends its confirmation email synchronously and modules import each other freely → a **modular monolith**: one `market` image running as the process types **web / worker / beat / relay / consumers**. RabbitMQ 4.3 with quorum queues serves as both the Celery broker and the event bus (`atlas.events`), fed by a transactional outbox. Boundaries are enforced by independence contracts. The bot gains a **`sender`** process. New modules: `notifications`, `search`, `reviews`, and catalog imports. OpenSearch is added only if Postgres FTS fails the judged set. |
| **New technologies** | Celery 5.6.3 + Beat; RabbitMQ 4.3 (quorum queues, dead-letter exchanges, publisher confirms, Native Delayed Delivery); Mailpit (SMTP test server); pg_partman; import-linter *independence* contracts; Pact message contracts; pg_trgm and Postgres full-text search; (OpenSearch 3.x, conditional stretch) |
| **Portfolio tag** | `v0.4` |
| **Old-spec theory to read** | [P3 D42–D53](../python/03-peopleops.md): D42–D43 the blocking email, D44–D47 Celery settings, D49–D53 Beat and run keys. [P4 D55–D78](../python/04-wareflow.md): D55–D60 bounded contexts and the leak hunt, D61–D66 RabbitMQ, D74–D78 the Kafka comparison and the commit-then-publish gap (D75 itself). [P7 D109–D120](../python/07-fleettrack.md): D109–D114 outbox, relay, SKIP LOCKED, lag; D115–D120 CQRS and the upcaster. [P8 D121–D126](../python/08-docuvault.md): LIKE → trgm → FTS → ES, derived-index rebuild. [P10 Wk28 Telegram ext](../python/10-atlasmarket.md) (§19: bot push through the outbox relay). |

Version pins are as of 2026-09. Re-check them with `scripts/compat_check.sh` before you start (ADR-001). Add two steps to the compatibility check: the pg_partman extension (the plain `postgres:17` image does not ship it), and a Celery worker started against the pinned RabbitMQ with its log grepped for the deprecated-feature error described in §4.2 step 4.

> **What this stage is really for.** Three habits that separate a middle+ engineer from a middle one:
> 1. Slow work never sits on the request path, and you can prove it with a p95.
> 2. A side effect is never lost or duplicated just because two systems failed at different moments. You will watch `order.placed` vanish before you build the outbox.
> 3. Module boundaries are a *number* you measure and drive to zero, not a diagram.
>
> Search is the fourth thread. It is the stage's lesson in adopting a new store only when a fixed test proves Postgres cannot do the job.

---

## 1. The problem this stage starts from

**In business terms:**
- **Slow checkout, and a failure you can't explain to customers.** S2 left the confirmation email synchronous, and you measured it in `docs/perf/blocking-email.md`. A slow mail server adds seconds to every checkout. A mail server hiccup turns a perfectly valid order into an error page.
- **Vendors can't upload their catalogues.** A CSV of 20,000 rows cannot be processed inside a request, and product images need thumbnails.
- **Stock gets stuck.** Nobody releases the S2 holds that customers abandoned, so the stock looks sold out.
- **Vendors are left out.** They want a daily digest, a live list of their own orders, and a Telegram message when a new order arrives, with a button to mark it shipped.
- **Customers get no updates and can't search.** They want a Telegram message when their order ships. They type queries in Latin and Cyrillic, sometimes misspelled, and the storefront has no search at all.
- **Reviews are missing.**

**In engineering terms:**
- **No background processing.** Every "and also do Y" runs inside the request.
- **No event stream.** Each new reaction to "an order was placed" becomes another call inside checkout, so checkout's latency and failure rate grow with every feature.
- **Modules import each other freely.** The [README §5.1 evolution table](README.md#51-the-evolution-table) records this for S3. Without a coupling number, no later extraction ADR (S8, S9, S10, S12) can argue from data. It could only argue from taste.
- **No second source for search.** If a search engine is ever adopted, you need a way to keep a derived index in sync. That need depends on the event stream too.

---

## 2. Outcomes — what exists when the stage is finished

1. **Celery 5.6** runs one queue per task class: `emails`, `imports`, `media` and `beat-jobs`. Each queue has its own worker process.
   - Checkout p95 is recorded before and after the confirmation email moves off the request path.
   - Checkout succeeds while SMTP is down.
   - The order confirmation ends the stage on the event path (`order.placed` → `market.notifications`, outbox-backed). `on_commit` enqueue remains only for loss-tolerant tasks such as thumbnails and digests. One checkout produces exactly one confirmation email.
2. **The CSV import** returns `202` + `Location`.
   - It streams the file with a generator, loads rows with COPY, and reports progress on an import resource.
   - At most one import runs per vendor, enforced by a Redis lock whose fencing token is checked in Postgres.
3. **A hold-expiry sweeper** uses `FOR UPDATE SKIP LOCKED`, with throughput measured at 1 and 4 workers.
   - A daily vendor digest is guarded by a UNIQUE run key.
   - A test at the Tashkent midnight boundary (19:00 UTC) proves the digest runs once for the right local date.
4. **Each Celery setting has evidence of what breaks without it:** `on_commit` enqueue, retry with backoff, `acks_late` + `reject_on_worker_lost` (tested with `kill -9`), prefetch 1, and soft/hard time limits.
5. **Two broker pain runs are recorded, each with a committed prediction:** a long `acks_late` task under a lowered `visibility_timeout`, and queued tasks on an allkeys-lru instance while the cache fills.
6. **RabbitMQ 4.3 topology is declared in code:**
   - the topic exchange `atlas.events` and quorum queues;
   - publisher confirms, with a restart test showing N messages before and N after;
   - the DLX retry tiers (10 s, 1 m, 10 m) and parking lots, plus one poison message inspected by hand. (A DLX, *dead-letter exchange*, is where RabbitMQ routes messages that were rejected, expired or exceeded a limit.) Every queue on a dead-letter path dead-letters *at-least-once*, and a test shows that a missing parking queue loses nothing.
7. **Celery runs on RabbitMQ quorum queues** (`task_default_queue_type='quorum'`, `worker_detect_quorum_queues=True`). Countdown retries work through Native Delayed Delivery.
   - The 35-minute import that tripped the 30-minute `consumer_timeout` is recorded, then fixed by chunking.
8. **A transactional outbox:**
   - the dual-write loss is reproduced first;
   - the atomicity test forces a failure;
   - two relays claim rows with SKIP LOCKED and never double-publish;
   - a partial index `WHERE sent_at IS NULL`, `trace_context` as JSONB, and an `outbox_lag_seconds` metric;
   - retention by daily pg_partman partitions (with a DEFAULT partition and BRIN) instead of DELETE, with the bloat numbers for both. (BRIN, a *block-range index*, stores only the min and max per range of table blocks: tiny, and good for naturally ordered columns like `created_at`.)
9. **Consumers:**
   - an inbox table `UNIQUE(consumer, event_id)` written in the same transaction as the effect;
   - Pact message contracts for `order.placed` and `vendor_group.fulfilled`;
   - a versioned envelope with a v1→v2 upcaster;
   - a `vendor_order_view` projection.
10. **Boundaries:**
    - import-linter independence contracts;
    - a **leak count recorded, then driven to 0**;
    - modules talk only through `api.py` facades and events;
    - a `pg_constraint` test bans cross-module FKs (allow-list: `identity_user`);
    - a composition root per module;
    - `libs/atlas-events` built as a wheel.
11. **Notifications:**
    - an email task;
    - a bot `sender` process consuming `bot.notifications`, idempotent on event id;
    - an outbound leaky-bucket pacer (about 30 msg/s global, 1/s per chat, 20/min per group, honouring `retry_after`), tested against a fake Bot API in `atlas-testkit`;
    - the **vendor bot flow**: linked vendor staff get a new-order message with an inline "mark shipped" button, and the callback goes through market's fulfillment API under the S1 vendor-staff relationship rule.
12. **Search:** LIKE → pg_trgm → FTS (a generated `tsvector` with the `simple` config and setweight, `websearch_to_tsquery`, and a Latin↔Cyrillic transliteration column). A 40-query judged set has p95 and top-3 hits recorded for each step.
13. **Reviews:** verified purchase through `ordering`'s facade (a plain `order_item_id` column, no cross-module FK) with `UNIQUE(order_item_id)`, plus a rating aggregator consumer.
14. **Documents:** ADR-013, ADR-014, ADR-015 (with the leak count) and ADR-016 (the search verdict), plus SD9, SD14 and SD15. The stage is tagged `v0.4`.

---

## 3. Architecture at the end of the stage

```
 clients ──> market web (gunicorn) ──── one transaction ────> PG17 market
               │  on_commit enqueue           orders, stock, reviews, imports
               │  (loss-tolerant tasks only)
               │                              outbox (daily partitions, BRIN,
               │                                      partial idx sent_at IS NULL)
               │                              inbox, vendor_order_view, tsvector
               v                                            │
 ┌──────────── RabbitMQ 4.3 (all quorum queues) ───────────┐│ FOR UPDATE SKIP LOCKED
 │ Celery: emails  imports  media  beat-jobs               ││
 │   ^ beat (exactly one)      └─> worker per queue ──> Mailpit, Garage (S3 API)
 │                                                         │v
 │ atlas.events (topic) <──── publisher confirms ─────── relay ×2
 │   ├─ market.notifications    ──> consumers: notifications ──> emails task
 │   │     (order.placed → the order confirmation, among others)
 │   ├─ market.vendor-order-view ─> consumers: projection
 │   ├─ market.rating-aggregator ─> consumers: reviews aggregate
 │   ├─ bot.notifications       ──> bot sender ── pacer ──> Telegram
 │   └─ market.search-indexer   ──> (only if OpenSearch is adopted; S8 adds it anyway)
 │ atlas.retry  *.retry.10s / *.retry.1m / *.retry.10m ──> back to the queue
 │ atlas.dlx ──> <queue>.parking   (inspected by hand)
 └──────────────────────────────────────────────────────────┘
 redis-state: import lock + fencing counter, pacer buckets, bot dedup, FSM
 redis-cache: unchanged from S3
```

**Process types.** One image, many roles. None of these is a separate service.

| Process type | Runs | How many in Compose | Why separate |
|---|---|---|---|
| `web` | gunicorn | as in S3 | serves requests only |
| `worker` | Celery, one process per queue | 1 per queue (4) | a slow import must not delay an email (head-of-line blocking, P3 D44–D47) |
| `beat` | Celery Beat | **exactly one** | two Beats means every schedule fires twice. The run keys are the backstop, not the plan. S10 adds a Lease. |
| `relay` | outbox → RabbitMQ loop | 2 | proves the SKIP LOCKED claim; survives one relay dying |
| `consumers` | one loop per queue | 1 per queue | a slow projection must not delay notifications |
| `bot` / `bot sender` | aiogram polling / queue consumer | 1 each | a broadcast must not block inbound updates |

**What changed and why:**
- **The request only does what the caller needs answered.** Everything else is a task (triggered work) or an event (a fact other modules react to). Triggered and scheduled work have different failure models (P3). Beat jobs fire twice, and you design for that with a constraint.
- **RabbitMQ replaces Redis as the broker.** Redis only emulates acknowledgements. You will watch that emulation redeliver a running task and lose a queued one. RabbitMQ gives per-message acks, routing, dead-lettering and durable replicated queues (ADR-013).
- **The outbox makes "an event exists if and only if its transaction committed" true.** It is at-least-once, not exactly-once. Every consumer therefore writes an inbox row (ADR-014).
- **The module map becomes enforceable.** From here on, the extraction ADRs can quote a coupling number (ADR-015).

---

## 4. Build plan

A suggested order across the five weeks. Weekend blocks hold the long-running and chaos runs. Log your actual hours per block in the hours log (see [schedule-and-cuts.md](schedule-and-cuts.md) §1): B1 comes right after this stage and uses that log.

| When | Work |
|---|---|
| W13 weekdays | 4.1 Celery app, the email task, the CSV import with its fencing lock, thumbnails, the settings |
| W13 weekend | Re-measure the checkout pain under ADR-002; the `kill -9` runs; the visibility-timeout and LRU-vanish runs; the sweeper at 1 vs 4 workers |
| W14 weekdays | Finish 4.1 (digest, Tashkent tests); 4.2 topology, confirms, retry tiers and parking lots; Celery on quorum queues |
| W14 weekend | The RabbitMQ restart N = N test; the poison message through every tier; the real 35-minute `consumer_timeout` run, then the chunked re-run |
| W15 weekdays | 4.3 outbox; start 4.4 consumers; SD14 |
| W15 weekend | Broker-kill and relay-kill chaos; DELETE vs partition bloat under worldgen checkout traffic |
| W16 weekdays | Finish 4.4 (inbox, upcaster, Pact, projection); 4.5 boundaries; start 4.6; SD15 paper design |
| W16 weekend | The leak-hunt refactor down to 0 and the FK-drop migrations (a long refactor goes better uninterrupted) |
| W17 weekdays | Finish 4.6 (pacer, vendor flow, the confirmation on the event path); 4.7 search; 4.8 reviews; SD9; the SD write-ups |
| W17 weekend | The 5,000-chat broadcast before and after the pacer; the judged-set runs for every search step |

### 4.1 Celery [13 h, must]

**Why this exists.** "Because it is best practice" is not an interview answer (P3 D42–D43). You have the numbers from S2. Now you move the email off the request path, and you learn every worker setting by breaking it first.

**Unattended time in this block:** about 45 min. The checkout benchmark is 3 configurations (no email, synchronous email with delayed SMTP, Celery with delayed SMTP) × 3 runs × ~4 min ≈ 36 min, plus the sweeper runs (2 variants × 1 and 4 workers). Schedule these in the weekend block.

**What to build:**
1. **Re-measure the pain.**
   - Re-run S2's checkout benchmark under ADR-002, with an injected SMTP delay in front of Mailpit (the SMTP test server from S2, pinned in ADR-001). A reliable way to inject it is Toxiproxy, a small TCP proxy, with a latency toxic on Mailpit's SMTP port (S9 reuses Toxiproxy); Mailpit's own chaos options can inject SMTP errors if your pinned version has them [verify].
   - Stop SMTP entirely and show checkout failing.
   - These are the "before" numbers for this stage's Done-when.
2. **Celery app in `market`, first on a Redis broker** pointed at `redis-state`. Why not `redis-cache`? You will find out in the pain runs below. Tasks by queue:
   - **`emails`:** the order confirmation.
     - Enqueue with `transaction.on_commit` for now. This gets the email off the request path before the outbox exists. §4.6 moves the confirmation's trigger to the event path, and ADR-014 asks you why it cannot stay on `on_commit`.
     - Retry with exponential backoff and jitter.
     - Keep a "sent" marker (unique per order and template), because `acks_late` will redeliver.
     - Explicit enqueue from the service layer, never from a `post_save` signal. Signals hide the call site and fire on fixtures and Admin edits (P3).
   - **`imports`:** the vendor CSV import.
     - `POST` returns `202` with `Location: /api/v1/imports/{id}`. The file goes to `atlas-imports` through a presigned PUT (the S1 pattern).
     - The worker streams the file with a generator and never holds it in memory whole. It validates rows, COPYs them into a staging table and merges them into `catalog`. Every merged price change must hit the S3 invalidation path. It is already a row in your audit table.
     - Progress lives on the import row: done, total and an error sample.
     - **One import per vendor:** a Redis lock in `redis-state` (`lock:` prefix) hands out a monotonically increasing **fencing token**. The import row in Postgres stores the highest token seen, and every write checks it. A worker that was paused past its lock's TTL wakes up holding a stale token, and Postgres rejects its writes. This is the fencing caveat S3 named when it declined Redlock.
   - **`media`:** product-image thumbnails, read from and written to `atlas-media`.
   - **`beat-jobs`:**
     - the **hold-expiry sweeper**: claim expired holds with `FOR UPDATE SKIP LOCKED` in batches and release each through a `stock_movements` row (the S2 invariant: stock changes only through movements). Run it with 1 worker and with 4, and measure throughput;
     - the **daily vendor digest**, guarded by a UNIQUE run key such as (job, vendor, local date). A second run for the same key is a no-op.
3. **Settings, each demonstrated once:**
   - `on_commit` enqueue: a rollback test shows nothing was enqueued;
   - retry with backoff: tested against a failing mail backend;
   - `acks_late` + `reject_on_worker_lost`, with `kill -9`;
   - `worker_prefetch_multiplier=1`;
   - soft and hard time limits: a task past the soft limit receives `SoftTimeLimitExceeded` and cleans up;
   - one queue per task class, with `task_routes` and a routing test.

   Record every setting and what broke without it in a Celery ops note (P3's `docs/celery-ops-notes.md` is the model).
4. **Beat at the Tashkent midnight boundary.**
   - Asia/Tashkent is a fixed UTC+5 zone with no DST. There is no DST night to test, so test the boundary itself: local midnight is 19:00 UTC on the previous UTC day.
   - With freezegun, run at 18:59:59 and 19:00:00 UTC, and assert the digest runs once, for the correct local date.
   - Assert that an order placed at 19:30 UTC appears in the *next* local day's digest.
   - Guiding question: do you set Celery's timezone to Asia/Tashkent and schedule 00:00, or keep UTC and schedule 19:00? Which survives the day Atlas adds a second country?

**Pain-first exercises.** For each row, write your prediction into the evidence file and commit it, then run. Compare afterwards with "Check your prediction" in §16.

| Do this first | Look at and record | Record in `docs/evidence/s04/` |
|---|---|---|
| Checkout with the synchronous email and Mailpit's SMTP delayed; then SMTP stopped | Checkout p95 against the no-email baseline; the checkout response with SMTP down | `checkout-email-before.csv` |
| Default `acks_late=False`; `kill -9` the worker mid-send | Whether the email ever arrives in Mailpit; what the broker's queue shows for that message | `acks-late.md` |
| `acks_late=True` + `reject_on_worker_lost`; `kill -9` again | Whether the task runs again, and how many emails arrive without the sent marker | `acks-late.md` |
| Redis broker with `visibility_timeout` lowered to 60 s (so you don't wait an hour); a task with `acks_late=True` that sleeps 90 s (or a countdown longer than 60 s) | Which workers start the task and when, from both workers' logs; any error lines | `visibility-timeout.log` |
| Point the broker at `redis-cache` (allkeys-lru, small `maxmemory`), queue tasks, then fill the cache from locust | Tasks queued vs tasks executed; `evicted_keys`; any error lines | `lru-broker-vanish.log`. This tests the S3 split rule. |
| Sweeper with plain `FOR UPDATE` (no SKIP LOCKED) on 4 workers | Holds released per second at 1 and 4 workers | `skip-locked-1v4.csv` (both variants) |

**Acceptance criteria:**
- Checkout p95 with the delayed SMTP matches the no-email baseline within the ADR-002 noise rule.
- Checkout succeeds with SMTP down, and the email arrives once SMTP returns.
- Each setting has its evidence row.
- The routing test proves an email never lands on the `imports` worker.
- The run-key double-fire test and the Tashkent boundary tests are green.
- The fencing test is green: a stale-token write is rejected by Postgres.

### 4.2 RabbitMQ 4.3 [9 h, must]

**Why this exists.** The Redis runs you just did showed that Redis only emulates acks. You now need four things it cannot give: real per-message acknowledgement tied to a connection, routing so one event reaches many consumers, dead-lettering for poison messages, and queues that survive a broker restart. WareFlow (P4 D61–D66) introduced these ideas. Here you use them on RabbitMQ 4.3, where quorum queues are the replicated *work-queue* type. (Streams are the other replicated type: a log that consumers read by offset. Classic mirrored queues were removed in 4.0.)

**Unattended time in this block:** about 1.5 h. The 35-minute `consumer_timeout` run happens twice (the failing single task, then the chunked re-run) ≈ 75 min, plus the poison message's trip through the tiers (just over 11 min of TTLs). Schedule these in the weekend block.

**What to build:**
1. **Topology as code.**
   - Declare it from a topology module or a definitions file, never by clicking in the management UI. It should be reproducible from a clean broker.
   - The topic exchange is `atlas.events`, and the routing key is the event `type` (for example `order.placed`).
   - Queues, named as in the [glossary](glossary.md): `market.notifications`, `market.vendor-order-view`, `market.rating-aggregator`, `bot.notifications`, plus `market.search-indexer` only if OpenSearch is adopted (S8 creates it anyway, to refresh product embeddings). All are quorum queues. Each has a parking lot `<queue>.parking`.
2. **Durability.**
   - Persistent messages with publisher confirms: the publisher treats a message as sent only after the broker confirms it.
   - **Restart test:** publish N messages with confirms, restart RabbitMQ, count N.
   - Observe what happens without each safeguard, as WareFlow did: a publish with confirms off while the broker restarts.
3. **Retry tiers and the parking lot.**
   - Consumers ack manually, *after* their DB transaction commits.
   - On failure, the message moves to the next retry tier on `atlas.retry` (`*.retry.10s`, `*.retry.1m`, `*.retry.10m`). Each tier holds it for its TTL, then dead-letters it back to the work queue. After the last tier it goes through `atlas.dlx` to `<queue>.parking`.
   - Craft one poison message. Watch it move through 10 s → 1 m → 10 m → parking, then open it by hand in the management UI and write down what you would have needed to debug it.
   - **Dead-lettering must not lose messages.** By default a quorum queue dead-letters *at-most-once*: the message is removed from the source queue and republished without confirms, so if the target is missing, unroutable or rejecting, the message is silently gone. Every work, retry-tier and parking queue on a dead-letter path therefore needs `x-dead-letter-strategy: at-least-once` together with `x-overflow: reject-publish` (as queue arguments or a policy). Read the [quorum queue docs](https://www.rabbitmq.com/docs/quorum-queues) section on dead-lettering to see why the two go together.
   - **Test it:** delete or unbind a parking queue, push a message past the last tier, and show that it is retained (not dropped), then delivered once the parking queue exists again.
   - Quorum queues also count deliveries, and since RabbitMQ 4.0 they dead-letter a message after a default delivery limit of 20. The `acks_late` redelivery loop, the delivery limit and your tiers must agree on which one is the authority for "give up". Decide, and record the decision in ADR-013.
4. **Move the Celery broker to RabbitMQ.**
   - Set `task_default_queue_type='quorum'` and `worker_detect_quorum_queues=True`.
   - Countdown/ETA retries now rely on **Native Delayed Delivery**.
   - Worker **autoscale does not work** with quorum queues. Set a fixed concurrency per queue worker and say so in the ops note.
   - **A deprecated feature you will trip over.** RabbitMQ 4.3 refuses to declare transient (non-durable) non-exclusive queues by default, and Celery 5.6 / kombu 5.6 still declare their remote-control ("pidbox") queues that way. Expect a "Feature `transient_nonexcl_queues` is deprecated" error on worker start, and `celery inspect` failing. For dev and staging, permit the feature in the broker's `rabbitmq.conf` before its first boot (`deprecated_features.permit.transient_nonexcl_queues = true`), and add a tracked TODO to remove the line once a kombu release fixes the pidbox declaration (re-check with `scripts/compat_check.sh`). Record the choice, and the alternative you rejected (disabling Celery remote control), in the Celery ops note and ADR-013. It makes a good short story about reading release notes before upgrading.
5. **The `consumer_timeout` pain** (below).

#### Two timeouts that look alike

Both settings answer the same question: "the consumer took the message and has not acknowledged it; is it slow, or dead?" A broker cannot tell slow from dead. Each system therefore picks a deadline, and each deadline has a different failure shape.

| | Redis broker: `visibility_timeout` | RabbitMQ: `consumer_timeout` |
|---|---|---|
| What it is | kombu's emulation of acks on Redis. A fetched message is parked as "unacked" with a timestamp, and if no ack arrives in time, the client side puts it back on the queue. | A broker-side limit on how long a consumer may hold a delivery unacknowledged |
| Default | 1 hour | 30 minutes |
| Who enforces it | The consumers (kombu restores stale unacked messages) | The broker |
| What happens when exceeded | The message is delivered **again, to another worker, while the first is still running it** | The broker **closes the consumer's channel** with an error and requeues that channel's unacked deliveries |
| What it looks like | Silent. Two executions overlap. Nothing logs an error. | Loud. A channel error (PRECONDITION_FAILED, delivery acknowledgement timed out) appears in the broker and worker logs, the task starts again, and the first execution's ack fails because its channel is gone. Record exactly what *you* see. |
| Why it exists | Redis has no connection-bound delivery. Without the timeout, a crashed worker's message would be lost forever. | A dead consumer's messages are already requeued the moment its connection drops. The timeout catches consumers that are stuck but still connected. |
| Also bites | A countdown or ETA longer than the timeout makes the task get redelivered in a loop | Long `acks_late` tasks, and any consumer doing slow work before its ack |
| Tempting wrong fix | Raise it to 24 h (now a crashed worker's tasks wait 24 h) | Raise it for the queue (now a stuck consumer holds messages for hours, and you have removed your stuck-consumer detector) |
| Right fix | Keep tasks well under the timeout, and make them idempotent | Keep each delivery short. How you do that for the import is the exercise below. |

The phrase to remember: **the timeout has changed shape, not disappeared.** Moving to RabbitMQ does not remove the need to keep deliveries short. It changes a silent duplicate into a loud one.

**The exercise:**
- *Real run, weekend block:* make the import take 35 minutes as a single `acks_late` task (a large worldgen CSV, or a throttled merge) on the RabbitMQ broker with the default 30-minute `consumer_timeout`. Predict what happens at minute 30 and commit the prediction, then run. Record the broker and worker logs in `docs/evidence/s04/consumer-timeout.log`. This is one of your STAR stories.
- *Fast regression:* reproduce it in the integration suite with a lowered `consumer_timeout` on the test broker, so CI does not wait 30 minutes.
- *Then fix it.* Design the fix yourself, after the run, from these questions:
  - How do you split one 35-minute import into deliveries that each finish in a few minutes?
  - What makes re-running a piece harmless if its worker dies halfway? What key would a merge need so that doing it twice changes nothing?
  - Where does progress live, so a restart knows what is done?
  - What marks the whole import complete, and who does it?
  - Re-run the 35-minute file and show no channel closure.

#### Quorum queues and Native Delayed Delivery, in plain words

- **A quorum queue** is a replicated queue built on the Raft consensus algorithm. A message counts as safely stored once a majority of the queue's replicas have written it.
  - Quorum queues are always durable. They have no "non-durable" or "exclusive" mode, and they track how many times each message was delivered, which gives you poison-message handling.
  - In Compose you run one RabbitMQ node, so the "majority" is one node and replication is not exercised. You still use quorum queues because they are the replicated work-queue type in 4.x (streams replicate too, but they are a log, not a work queue), and dev should behave like prod.
- **Why Celery needs a special mode for delays.**
  - Classic Celery handles a countdown by letting the worker take the message early and keep it unacknowledged in memory until it is due. That relies on changing the channel's prefetch dynamically (global QoS), and quorum queues do not support global QoS. `worker_detect_quorum_queues=True` makes the worker notice this and stop relying on it.
  - With **Native Delayed Delivery**, Celery instead publishes a delayed task into a ladder of delay levels that RabbitMQ builds from message TTLs and dead-lettering. The message falls through the levels and arrives in the real queue when it is due.
  - Consequences you should be able to state:
    - a delayed retry now lives in the broker, not in a worker's memory, so a worker restart no longer drops or re-runs it;
    - the delay objects exist as RabbitMQ exchanges and queues, so find them in the management UI and list them in the ops note;
    - purging a work queue does not purge tasks still in the delay ladder.
- **Autoscale** (`--autoscale`) is not supported with quorum queues. You size each queue's worker explicitly. This matches how you will size pods in S10.

**Pain-first exercises for 4.2:** the restart without confirms or persistence, the poison message through every tier, the missing-parking-queue run, and the 35-minute `consumer_timeout` run, each with a committed prediction and recorded under `docs/evidence/s04/` (`rabbit-restart.md`, `poison-message.md`, `dlx-at-least-once.md`, `consumer-timeout.log`).

**Acceptance criteria:**
- The topology is rebuilt from code on a clean broker.
- The restart test shows N = N.
- The poison message reaches parking and is inspected.
- With the parking queue missing, the dead-lettered message is retained, not dropped (test).
- Workers start cleanly on the pinned RabbitMQ, `celery inspect ping` answers, and the deprecated-feature choice is recorded.
- Celery retries with countdown on quorum queues (a test asserts the retry happens after the delay).
- The chunked import survives past 30 minutes without a channel closure.
- The fast `consumer_timeout` regression is in the integration suite.

### 4.3 Outbox [8.5 h, must]

**Why this exists.** This is one of the never-cut invariants. It closes a bug WareFlow made you watch and leave unfixed (P4 D75). FleetTrack fixed that bug (P7 D109–D114).

**Unattended time in this block:** about 1 h for the two retention runs (DELETE, then partitions) under worldgen checkout traffic, at about 30 minutes each. Schedule them, and the broker-kill and relay-kill runs, in the weekend block.

#### The dual-write problem

The database and the broker are two different systems. **There is no order in which you can write to both that survives a crash between the two writes.** Walk through each option with checkout's `order.placed`:

1. **Commit, then publish.** The order commits. Then the process dies (a deploy's SIGTERM, an OOM kill, a lost node) or the broker is unreachable.
   - The customer already has the confirmation page: the order exists. The event never will. The vendor is never notified, the vendor dashboard never shows the order, the rating aggregator and the bot never hear of it.
   - No log line says anything, because nothing failed from the web process's point of view.
   - If the publish raised *after* the commit, you return a 500 for an order that exists. The client retries with the same `Idempotency-Key`, S2 correctly replays the stored 201, and there is still no event.
2. **Publish, then commit.** The event goes out, and then the commit fails: a S2 serialization failure, a `lock_timeout`, a constraint.
   - The vendor starts packing an order that does not exist.
   - Worse, S2's `@retry_on_serialization_failure` re-runs the whole transaction, so a retried checkout publishes *twice*, once per attempt.
3. **Publish inside the transaction.** The broker is not part of your database transaction. The message leaves when you call publish, so this is option 2 with nicer indentation.

Retrying the publish helps with a flaky broker. It does not help with a process that died between the two writes.

The outbox turns two writes into one. The event becomes a row, committed atomically with the order. Publishing becomes a separate, retryable job whose only input is committed rows. The price is that delivery is at-least-once (a relay can publish and then crash before marking the row sent) and has lag. Both are acceptable, and both must be designed for: consumers dedupe (§4.4), and lag is a metric.

**What to build:**
1. **Pain first.**
   - Implement `order.placed` as publish-after-commit.
   - Kill the broker between the commit and the publish: add a fault hook after the commit, or stop the RabbitMQ container at that point.
   - Count the order rows, the messages in `market.notifications`, and the log lines about it.
   - Then try publish-before-commit with a forced rollback, and count the same three things.
   - Record both in `docs/evidence/s04/dual-write.md`, next to the outcome the section above led you to expect. This is your "lost event" STAR story.
2. **The outbox table** (in the `outbox` module).
   - A column sketch to start from: `event_id` (UUIDv7), `type`, `version`, `account_id`, `payload` JSONB, `trace_context` JSONB, `created_at`, `sent_at`.
   - The service layer writes the row through one helper, in the same `atomic()` block as the state change.
   - **Forced-failure atomicity test:** raise after the outbox insert and assert that neither the order nor the outbox row survives.
3. **The relay process type**, run as two instances.
   - It claims a batch of unsent rows with `FOR UPDATE SKIP LOCKED`, publishes them with confirms, and sets `sent_at`.
   - **Two-relay test:** run both against a backlog and assert that every `event_id` was published exactly once.
   - **Broker-kill test:** kill RabbitMQ mid-batch. The rows stay unsent and publish after recovery, with 0 lost.
   - **Relay-kill test:** kill a relay between the publish and the mark. Observe a duplicate, and let the consumers' inbox absorb it.
   - Guiding questions for ADR-014:
     - If claim, publish and mark share one DB transaction, the row locks are held across network I/O to the broker. What bounds that time: the batch size, the publish timeout? What is the alternative with a lease column?
     - Why a dedicated loop and not a Beat task every second? (P7 D111 asked you to compare them.)
     - With two relays, events for the same order can be published out of order. Which consumers care, and what in the envelope lets them cope?
4. **Indexes and signals.**
   - A partial index `WHERE sent_at IS NULL`, so the relay's poll stays fast as the table grows.
   - `trace_context` stored as JSONB now, even though OTel arrives in S6, so S6 needs no migration on a hot table.
   - The `outbox_lag_seconds` metric (now minus the oldest unsent `created_at`), exposed now. S6 scrapes it and makes Alertmanager fire on it.
5. **Retention without bloat.**
   - *Pain first:* a Beat job deletes sent rows older than N days in batches. Predict what VACUUM will do to the table's size, and commit it. Under worldgen checkout traffic, record `n_dead_tup` and the table's on-disk size before the job, after it, and after a VACUUM.
   - *Replace it* with daily partitions managed by pg_partman, a DEFAULT partition as the safety net, and BRIN on `created_at` (the block-range index defined in §2). Retention becomes dropping whole old partitions: no dead tuples, no vacuum debt.
   - **Guard:** never drop a partition that still holds an unsent row. Check first, and alert if one exists.
   - Record both runs' numbers in `docs/evidence/s04/outbox-bloat.csv`.
   - Guiding questions:
     - A UNIQUE constraint on a partitioned table must include the partition key. So what happens to `UNIQUE(event_id)`? Why is that acceptable for the outbox, which generates each `event_id` once, but not for the inbox, whose whole job is uniqueness?
     - What happens to rows that land in DEFAULT because pg_partman did not create tomorrow's partition in time, and how would you notice?

**Acceptance criteria:**
- The dual-write loss and the phantom event are recorded.
- The atomicity test is green.
- Killing the broker and a relay mid-flow loses 0 events.
- Two relays publish no row twice.
- The partial index shows in the relay's plan (`EXPLAIN` committed).
- The lag metric rises when the relay is stopped and falls when it restarts.
- DELETE and partition bloat numbers are recorded.
- The retention guard is tested.

### 4.4 Consumers and CQRS [5 h, must]

**Why this exists.** At-least-once delivery means duplicates are normal operation, not an edge case (P4 D63). Each consumer must turn a second delivery into a no-op. It must do that inside the same transaction as its effect. Otherwise you have moved the gap, not closed it.

**What to build:**
1. **A consumer loop per queue** (the `consumers` process type).
   - Choose a client library. kombu arrives with Celery; pika is the plain alternative. Record why you chose one.
   - Consume with manual ack, prefetch sized deliberately, and ack only after the DB commit.
2. **The inbox.** A table with `UNIQUE(consumer, event_id)`, inserted in the same transaction as the consumer's effect. A duplicate hits the conflict, the effect is skipped, and the message is acked.
   - Test: deliver the same event twice, and assert one effect and two acks.
3. **The event envelope.** Every event carries these fields (glossary):

   ```
   event_id (UUIDv7) · type · version · occurred_at
   producer · account_id · trace_context · data
   ```

   - Write a v1→v2 **upcaster**: pick a real change to `order.placed` (add one field and rename one, as P7 did). Consumers upcast v1 to v2 before handling. Test both shapes.
   - The rule goes into ADR-014: never publish v2 until every consumer can read it.
4. **Pact message contracts** for `order.placed` and `vendor_group.fulfilled`.
   - The consumer tests produce the pact, and provider verification checks that the outbox serializer produces a matching message.
   - They run in the `pact-verify` CI job. A payload change that breaks a consumer fails CI before it merges.
5. **The `vendor_order_view` projection**, fed from `market.vendor-order-view`.
   - Rows are denormalized to the vendor dashboard's query shape. The dashboard endpoint reads only the view. S11's live dashboard reads it too.
   - The view holds vendor data, so it needs the same RLS policy as every other vendor table (S2).
   - A rebuild command regenerates it from the source tables. That is the invariant "derived indexes can be rebuilt".
6. **"Same technique, opposite verdict"** (P7 D115–D120). Write one paragraph in ADR-014: a few seconds of staleness is fine for the vendor dashboard. Stock must **never** be read from a projection, because stale stock means oversell (P4, S2).

**Pain-first exercise:**
- Before the inbox exists, replay one `vendor_group.fulfilled` twice through the projection and the notifications consumer. Predict the result first.
- Record the projection's counters and the emails in Mailpit after the second delivery.
- Record it in `docs/evidence/s04/duplicate-delivery.md`.

**Acceptance criteria:** the duplicate test is green for every consumer; `pact-verify` is green; the upcaster is tested on both shapes; the projection rebuild produces a view identical to the incremental one on the same data.

### 4.5 Boundaries [5.5 h, must]

**Why this exists.** Every later split (S8 ai, S9 atlaspay and auth, S10 inventory, S12 ledger and fraud) needs an ADR that argues from numbers. The first number is how coupled the modules are. WareFlow asked you to "re-read the boundary doc and hunt for leaking shared imports" (P4 D60). Here the hunt is mandatory and produces a count.

**What to build:**
1. **Write the module map first** (ADR-015 draft), covering each `market` module (see the [glossary](glossary.md) for the list):
   - the tables it owns, by app-label prefix;
   - its `api.py` facade (the functions other modules may call);
   - the events it publishes and consumes.
2. **An import-linter independence contract** over all `market` modules, allowing each to import only the others' `api`.
   - Find out how import-linter expresses "independent, except through `<module>.api`". Read its contract types (layers, independence, forbidden) and their ignore options.
3. **The leak hunt.**
   - Run the contract *before* any refactor and count the violations. That number is the first line of ADR-015's evidence. Commit it as `docs/evidence/s04/leak-count.txt`, with the command that produced it.
   - Drive it to 0 by replacing direct imports with facade calls, or with events where the caller does not need an answer.
   - Record the count at each step, so the ADR can show the curve.
4. **The cross-module FK ban.**
   - A test queries `pg_constraint` for foreign keys whose source and target tables belong to different app labels. It fails on any that are not allow-listed. The only allow-listed target is `identity_user`.
   - Count those FKs too. Replace each with a plain id column plus a snapshot of the data the module needs (S2's price snapshots are the precedent), or with a check through the owning module's facade.
   - The migrations that drop the FKs must be reversible (S1 rule).
   - Reviews follow the same rule. `reviews` and `ordering` are different modules, so a review holds a plain `order_item_id` column with no FK. The verified-purchase check goes through `ordering`'s `api.py` at write time, and `UNIQUE(order_item_id)` enforces one review per item (§4.8). ADR-015 records this, including what you lose without the FK (what happens if an order item is ever deleted?).
5. **A composition root per module.** It extends S1's manual composition root: each module wires its own repositories, ports and adapters, and exposes only its facade.
6. **`libs/atlas-events` as a wheel**, consumed by version, like `atlas-common` in S0. It holds the envelope, serialization, the upcaster registry and the publisher port.
   - Why a wheel now: the bot sender already consumes the envelope, and atlaspay (S9) and ledger (S12) will too.
   - Start the envelope code inside `market` during §4.3–4.4, then extract it here.

**Pain-first exercise:** before counting, try to write this sentence of a future extraction ADR: "`payments` would depend on N other modules." You cannot, because there is no N yet. Then count.

**Acceptance criteria:**
- The leak count before and after is recorded, and the final count is 0.
- The FK ban test is green, with only `identity_user` allow-listed.
- The independence contract runs in CI.
- `atlas-events` is built and consumed as a versioned wheel.

### 4.6 Notifications and bot push [6 h, must]

**Why this exists.** "Why does the bot's push go through the outbox relay instead of calling the Telegram API from the fulfillment endpoint?" (P10 Wk28). Because Telegram is a slow third party with strict rate limits. Because the endpoint must not wait on it (the invariant: requests never wait on SMTP or Telegram). And because a notification is a reaction to a committed fact, which is exactly what the outbox guarantees.

**Unattended time in this block:** about 15 min (the 5,000-chat broadcast without the pacer, then with it, plus the sender-kill run). Schedule the broadcast runs in the weekend block.

**What to build:**
1. **The `notifications` module.**
   - Consumes `market.notifications`, with its inbox.
   - For each event, decides which user gets which channel, customers and vendor staff alike.
   - Sends email through the `emails` Celery queue.
   - **Move the order confirmation to the event path.** From now on `order.placed` on `market.notifications` triggers the confirmation, so it inherits the outbox's guarantee. Remove the §4.1 `on_commit` enqueue for it; keep `on_commit` only for tasks whose loss is harmless (thumbnails, digests). Exactly one path may send the confirmation: add a test that one checkout produces exactly one confirmation email, and record the choice in ADR-014.
2. **The route to Telegram.**
   - The bot has no business logic (E6), so "who gets told what" stays in `market`.
   - Decide how a message reaches `bot.notifications`, and record the decision in ADR-014:
     - (a) the queue is bound to domain events on `atlas.events`, and the sender only renders them;
     - (b) the `notifications` module emits a message through the outbox that already carries the chat and the text.
   - Which option keeps rules out of the bot? Which survives a second bot channel?
3. **The bot `sender` process.**
   - Consumes `bot.notifications`.
   - Idempotent on `event_id`, using SET NX with a TTL in `redis-state` under the `bot:` prefix. The bot has no database.
   - Handles Telegram errors:
     - on **429**, honour the `retry_after` the Bot API returns;
     - on **403 (the bot was blocked by the user)**, do not retry. Park the message and tell `market` to mark the link inactive.
   - Never drop a message (E10: "Queue, never drop").
4. **The outbound leaky-bucket pacer** in `redis-state`, with its state under the `bot:` prefix (glossary).
   - About 30 msg/s globally, about 1 msg/s per chat, 20 msg/min per group.
   - It delays; it does not reject. It is shared through Redis, so it stays correct if you run two senders.
5. **A fake Bot API in `libs/atlas-testkit`.** An HTTP server that mimics `sendMessage`, enforces Telegram-like limits, and answers over-limit calls with the real error shape:

   ```
   {"ok": false, "error_code": 429,
    "description": "Too Many Requests: retry after 7",
    "parameters": {"retry_after": 7}}
   ```

6. **The vendor bot flow (about 1 h of this block).** E6 promises vendors a Telegram side; this is it.
   - On `order.placed`, the linked chats of each vendor group's vendor staff get a new-order message with an inline "Mark shipped" button. "Who is told" is decided in `notifications`, as for customers.
   - Pressing the button sends a `callback_query` to the bot. The bot passes it to market's fulfillment API through internal REST, and **market** applies the S1 vendor-staff relationship check. The bot decides nothing.
   - A short FSM asks for the tracking number before the call.
   - Guiding questions: what must the callback data carry, and what must it never be trusted to carry? What does the bot answer when market refuses?
   - Test with `feed_raw_update`: a callback from the right vendor's staff succeeds; a crafted callback from another vendor's staff is refused by market; the same button pressed twice does not ship twice.

**Pain-first exercise:**
- Broadcast to 5,000 linked chats (from worldgen) through the fake Bot API, **without** the pacer. Predict the outcome and commit it.
- Count the 429s, the retries and the total time, and check whether any message was lost or duplicated.
- Add the pacer and repeat. Work out the floor first (how long must 5,000 messages take at about 30 msg/s?), then compare your total and your 429 count with it.
- Record both runs in `docs/evidence/s04/pacer-429.csv`.

**Acceptance criteria:**
- A fulfillment event reaches a linked chat through the outbox, the relay and the sender, proven by the fault-injection style of the relay test: kill the sender mid-broadcast, restart it, and every chat gets exactly one message.
- The pacer run has near-zero 429s.
- A blocked chat is parked and not retried.
- One checkout produces exactly one confirmation email, sent from the event path.
- The vendor flow's tests are green, including the refused cross-vendor callback.

### 4.7 Search [5 h, must]

**Why this exists.** DocuVault's rule (P8 D121–D126): reach for a search engine only after LIKE → pg_trgm → Postgres FTS has been tried and has failed on a *specific* query, measured against a fixed query set. Otherwise you cannot answer the interview question "what was the exact query that made you add a search engine?"

**What to build:**
1. **The judged set first: 40 queries.**
   - Each query has the product ids a human judges relevant, taken from the worldgen catalogue.
   - Cover exact names, brands, category words, the same word in Latin and in Cyrillic, common misspellings, multi-word queries, attribute-like queries, and mixed Uzbek/Russian.
   - **Write the pass bar into ADR-016 before measuring anything:** a minimum top-3 hit rate and a p95 budget. Fixing the goalposts first is the whole point.
2. **Step 1: `LIKE '%term%'`.** Commit the EXPLAIN (a sequential scan), record p95 and top-3 hits, and explain why a leading wildcard cannot use a B-tree.
3. **Step 2: pg_trgm.** Add a GIN trigram index on the product name, so ILIKE and similarity become indexable. Record the numbers, and where it breaks: relevance is only character similarity, with no weighting and no word boundaries.
4. **Step 3: FTS.**
   - A generated `tsvector` column using the `simple` configuration, with `setweight`: name highest, then brand and category, then description. Index it with GIN, query it with `websearch_to_tsquery`, and rank.
   - Why `simple`: there is no Uzbek stemmer, and catalogue text mixes Uzbek (Latin), Russian (Cyrillic) and brand names.
   - Add a **Latin↔Cyrillic transliteration column**, so a Cyrillic query finds a Latin-named product and the other way round.
   - Hint: a generated column needs an IMMUTABLE expression. What does that mean for how you write the transliteration?
5. **Record p95 and top-3 for every step** in `docs/evidence/s04/judged-set.csv` and in the table in ADR-016.
6. **The verdict.**
   - If the judged set passes on Postgres, ADR-016 says **"OpenSearch not adopted"**, and the 6 h OpenSearch stretch goes to the cut list.
   - If it fails, the ADR names the failing queries and the stretch becomes justified.
7. **A relevance regression test** runs on the judged set for whichever engine wins.
8. **Rebuild proof.** The generated columns recompute themselves, and indexes can be rebuilt with `REINDEX CONCURRENTLY`. Test that dropping and rebuilding the search index gives identical judged-set results.

**Acceptance criteria:**
- The judged-set table is filled in for LIKE, trgm and FTS (and OpenSearch, if adopted).
- The pass bar was committed before the first measurement: git history shows it.
- ADR-016 carries the verdict.
- The regression test is in CI.

### 4.8 Reviews [2 h, must]

**What to build:**
- A `reviews` module. Only a customer with a **delivered** order item may review it. `order_item_id` is a plain column with no FK (the §4.5 ban). Check the purchase through `ordering`'s `api.py` at write time, and enforce one review per item with `UNIQUE(order_item_id)`.
- Why reviews stay in Postgres rather than Mongo: they are small and relational (a verified-purchase check next to the orders data, aggregated in SQL beside ratings, read per product with pagination). Write that sentence into ADR-015.
- A `review.created` event published through the outbox.
- A **rating aggregator consumer** on `market.rating-aggregator`, keeping per-product rating count and sum idempotently through its inbox. The aggregate can be rebuilt from `reviews`.

**Acceptance criteria:** a non-buyer and an undelivered item are both refused (tested); a duplicate review is refused by the constraint; a replayed `review.created` does not double-count.

*If behind schedule:* the degrade list's rating-aggregator item ([schedule-and-cuts.md](schedule-and-cuts.md) §7) removes the rating aggregator consumer (it saves 1 h). Compute the rating on read instead, and say so in ADR-015.

### 4.9 Drills + SD9 / SD14 / SD15 [6 h, must]

- Weekly drill hour (×5): one SQL problem on the Atlas schema (the outbox lag query, a digest by local date, a projection rebuild) or one DSA problem, plus this stage's questions from §10 out loud. The 45-minute paper designs take the drill hour's question slot: SD14 in W15, SD15 in W16, SD9 in W17.
- 1 h to write up the three SD comparisons in `docs/sd/` once the matching blocks are built: see §9.

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| An event exists if and only if its transaction committed | The outbox row is written in the same transaction as the state change; the relay reads only committed rows | Forced-failure atomicity test; rollback leaves no outbox row; broker-kill test loses 0 |
| A duplicate delivery is a no-op | Inbox `UNIQUE(consumer, event_id)` in the effect's transaction; the bot sender dedups with SET NX | Duplicate-delivery test per consumer; relay-kill test (a duplicate published, one effect) |
| A message is acked only after its effect committed | Manual ack after commit | Kill a consumer between commit and ack: the message is redelivered and the inbox absorbs it |
| A message on a dead-letter path is never silently dropped | `x-dead-letter-strategy: at-least-once` + `x-overflow: reject-publish` on every work, retry-tier and parking queue | Missing-parking-queue test: the message is retained, then delivered |
| Requests never wait on SMTP or Telegram | Notifications driven by outbox events (the order confirmation included); `on_commit` enqueue only for loss-tolerant tasks; the bot sender | Checkout p95 unchanged with Mailpit's SMTP delayed; checkout succeeds with SMTP stopped |
| One checkout sends exactly one confirmation email | Only the `order.placed` → `market.notifications` path sends it | One-checkout-one-email test (count in Mailpit) |
| Each Beat job runs at most once per key | UNIQUE run key (job, subject, local date) | Double-fire test; Beat restart test; Tashkent boundary tests |
| At most one import runs per vendor, even with an expired lock | Redis lock + fencing token checked in Postgres | A stale-token write is rejected |
| Two relays never publish the same row | `FOR UPDATE SKIP LOCKED` claim | Two-relay backlog test: every `event_id` published exactly once |
| Retention never drops an unsent outbox row | Partition-drop guard | Test with an unsent row in an expired partition: no drop, and an alert |
| No queued task lives on an evicting Redis | The broker points at `redis-state`, then RabbitMQ (ADR-013) | Config test; the LRU-vanish evidence explains why |
| Modules import only each other's `api` | import-linter independence contract | CI job `import-contracts` (independence contracts added to S1's layers contract) |
| No cross-module foreign keys (allow-list: `identity_user`) | Migrations + a `pg_constraint` test | FK ban test |
| Derived indexes can be rebuilt | Generated columns; rebuild commands for `vendor_order_view` and the rating aggregate | Wipe-and-rebuild tests: identical results |
| Stock is never read from a projection | Only `inventory`'s facade answers stock questions | A test (or linter rule) that no checkout path reads `vendor_order_view` or any other projection |

---

## 6. Tests to write

- **Rollback, so nothing is enqueued:** a transaction that rolls back enqueues no Celery task and writes no outbox row.
- **Worker death:** `kill -9` mid-task under `acks_late=False` (lost) and `True` (redelivered, deduplicated by the sent marker). Evidence plus an integration test.
- **Routing:** an `emails` task never runs on the `imports` worker.
- **Time limits:** a task past its soft limit cleans up.
- **Beat:** the run-key double fire; the Tashkent boundary at 18:59:59 / 19:00:00 UTC; an order at 19:30 UTC landing in the next local day's digest (freezegun).
- **SKIP LOCKED:** the sweeper on 4 workers releases each expired hold exactly once (the `stock_movements` count equals the expired holds).
- **Fencing:** an expired lock holder's write is rejected.
- **RabbitMQ:** restart N = N with confirms; a poison message reaches parking after the last tier; with the parking queue missing, the message is retained, not dropped; a countdown retry arrives after its delay on quorum queues; the lowered `consumer_timeout` reproduction, and the chunked import passing it.
- **Outbox:** forced-failure atomicity; broker-kill relay (0 lost); relay kill (duplicate absorbed); two relays (no double publish); lag rises with the relay stopped; the retention guard.
- **Consumers:** duplicate delivery per consumer; the upcaster on v1 and v2 payloads; Pact message tests for `order.placed` and `vendor_group.fulfilled`; projection rebuild equals the incremental result.
- **Boundaries:** the import-linter independence contract; the `pg_constraint` FK ban.
- **Notifications:** the pacer against the fake Bot API (429 handling, `retry_after`, 403 parking); sender idempotency across a restart mid-broadcast; one checkout → exactly one confirmation email; the vendor flow through `feed_raw_update` (own vendor succeeds, another vendor's staff refused by market, a double press ships once).
- **Search:** relevance regression on the judged set; the rebuild gives identical results.
- **Reviews:** verified purchase only; one review per item; aggregator idempotency.
- **Unit/integration split:** unit tests run without any service; integration tests use real Postgres, Valkey and RabbitMQ.

---

## 7. CI changes

| Job | What it runs | What it gates |
|---|---|---|
| RabbitMQ service container in `test-integration` | Everything that touches Celery, the relay, consumers and topology | Merges that break delivery guarantees |
| `pact-verify` | Consumer pacts and provider verification for `order.placed` and `vendor_group.fulfilled` | Payload changes that would break a consumer |
| `import-contracts` (independence contracts added to S1's layers contract; same job, so `ci-gate` already requires it) | Module independence except through `api` | Any new cross-module import |
| Unit/integration split | `test-unit` (no services, fast, every push) and `test-integration` (Postgres + Valkey + RabbitMQ) | Keeps the fast feedback loop fast |
| Inside `test-integration` | FK ban test, relevance regression, lowered `consumer_timeout` reproduction, the missing-parking-queue test | Schema coupling, search regressions, the timeout fix, silent dead-letter loss |

The S2 `concurrency` job and the S3 jobs keep running.

---

## 8. ADRs and documents

**ADR-013 — Broker: Redis → RabbitMQ; vs Kafka; vs Redis Streams; quorum queues**
- *Questions:*
  - What did the Redis broker get wrong (emulated acks, `visibility_timeout`, eviction)?
  - What does RabbitMQ give (per-message acks, routing, DLX, quorum queues)?
  - What is the retry and parking design? Is the retry tier or the delivery limit the authority? Which dead-letter strategy and overflow setting does every queue on the path use, and what did the missing-parking-queue test show?
  - How do `consumer_timeout` and chunking interact?
  - How did you handle the `transient_nonexcl_queues` deprecation, and what removes the workaround?
- *Numbers:* the visibility-timeout duplicate; the LRU vanish; restart N = N; the 35-minute run; the poison message's path and timings.
- *Counter-arguments:*
  - **Kafka.** Hint: argue from P4 D74 and from what your consumers need (per-message ack, a parking lot) versus what a partitioned log gives. Name what would change the decision; Season 2's CDC work is a candidate.
  - **Redis Streams, already in the stack.** Hint: list what you would have to build yourself on Streams to match your `docs/evidence/s04/poison-message.md` run. S11 uses Streams for resumable fan-out; say why the trade-off differs there.
  - **A RabbitMQ stream instead of quorum work queues.** One line: what does a replicated log with offsets not give a work queue?

**ADR-014 — Outbox and delivery semantics**
- *Questions:*
  - What does the outbox guarantee (a committed event is eventually published)?
  - What does it not guarantee (exactly-once, immediacy, ordering across relays)?
  - How do consumers dedupe (the inbox)?
  - How do envelopes evolve (versions, the upcaster, "never publish v2 before every consumer can read it")?
  - How does a message reach `bot.notifications` (§4.6)?
  - Which side effects may use `on_commit` enqueue instead of an event? `on_commit` is itself a small dual write: a process killed after the commit and before the enqueue loses the task. Say which tasks can tolerate that (a thumbnail, a digest) and which cannot, and why the order confirmation moved to `order.placed` → `market.notifications` in §4.6.
  - Include the "same technique, opposite verdict" paragraph.
- *Numbers:* relay throughput with 2 relays; lag under worldgen checkout load; DELETE bloat (`n_dead_tup`, size) against partition-drop numbers.
- *Counter-arguments:*
  - "CDC with Debezium instead of a polling relay." Hint: compare lag, DB load and operational surface; Season 2 (2E) measures it against this relay, so say what you expect it to show.
  - "Just retry the publish after commit." Hint: argue from `docs/evidence/s04/dual-write.md`.

**ADR-015 — Module map, including the leak count**
- *Questions:* every module's owned tables, facade and events; the allowed dependency directions; the FK allow-list, and how reviews reference an order item without an FK (and why reviews stay relational); the composition-root rule.
- *Numbers:* the import-linter violations before, at each step and at 0; the cross-module FK count before and after.
- *Counter-arguments:*
  - "Boundaries inside a monolith are ceremony; split into services if you want boundaries." Hint: argue from `docs/evidence/s04/leak-count.txt`. What does the count make cheaper later, and which later ADRs will quote it?
  - "Why not split now?" Hint: which measured problem would a split solve today? (The split gate arrives in S6.)

**ADR-016 — Search engine**
- *Questions:* what is the judged set, and what was the pass bar (committed before measuring)? What did each step achieve? Which queries failed where?
- *Numbers:* p95 and top-3 per step, for all 40 queries.
- *Verdict:* if Postgres passes, "OpenSearch not adopted", and the 6 h go to the cut list.
- *Counter-arguments:* "Everyone uses Elasticsearch or OpenSearch." Hint: argue from `docs/evidence/s04/judged-set.csv`, and list what a second store costs to operate and keep in sync (P8's documented gap is one item). If OpenSearch *is* adopted, answer the opposite counter: "Postgres FTS would have been enough", with the failing queries.

**Documents:** a Celery ops note (every setting and what broke without it); a RabbitMQ ops note (topology, confirms, prefetch, the retry design and dead-letter strategy, the delay-ladder objects, the deprecated-feature workaround and its TODO); `docs/perf/blocking-email.md` closed with the after numbers; the judged set committed as data.

---

## 9. System design session

| SD | Built or whiteboard | When | What you reuse from Atlas |
|---|---|---|---|
| **SD9 — Notification system** | **Built** | W17 | A queue-backed worker per channel (email on Celery, Telegram through the sender), so a slow channel does not block the other. Retry with backoff per provider. Idempotency on `event_id`. The pacer. SD9 asks how you prevent duplicates when the trigger is delivered twice, and you have the inbox and the SET NX dedup. Name what a third channel (SMS, push) would add, and the E2 split trigger: more than 3 channels with diverging SLOs. |
| **SD14 — Distributed job scheduler** | Built-lite | W15 | UNIQUE run keys, the SKIP LOCKED sweeper, one Beat. SD14's leader-election part is S10's Lease. For now, answer how a dispatched-but-crashed job is retried without double-running (idempotent handlers, run keys), and what Celery Beat does not give you (HA of the scheduler itself). |
| **SD15 — Typeahead** | Built-lite | W16 (paper), W17 (compare) | Trigram prefix matching on product names, ranked by popularity from worldgen views; client-side debounce; caching hot prefixes in `redis-cache`. The completion suggester is part of the OpenSearch stretch. |

Do each paper design first (45 minutes, no notes), then compare it with the build in `docs/sd/`.

---

## 10. Interview questions this stage lets you answer

1. When does work belong in a background job instead of the request cycle? Show the p95.
2. What does the outbox guarantee, and what doesn't it?
3. Walk me through the dual-write problem. Why doesn't "publish after commit, with retries" fix it?
4. What does `acks_late` force on you? What happens to a task when the worker dies mid-execution, under each setting?
5. Explain `visibility_timeout` vs `consumer_timeout`. What happens to a 2-hour task on each broker?
6. Why enqueue on commit rather than inside the transaction? And what can `on_commit` still lose?
7. How do two relays avoid double-publishing? What ordering do you lose?
8. How do you make a consumer idempotent? Why must the inbox row be in the same transaction as the effect?
9. How do you make a scheduled job idempotent, and why must you? How do you test a midnight job without waiting?
10. Durable queue, persistent message, publisher confirm: what does each protect against, and what is still not guaranteed with all three?
11. What does a DLQ give you, and what does it not? What did your poison message look like?
12. Why quorum queues? Why does Celery need Native Delayed Delivery on them?
13. What does `prefetch` do, and what goes wrong with a large prefetch on long tasks?
14. How do you change an event's schema without breaking a consumer that has not deployed yet?
15. When is CQRS worth it? Why is the vendor dashboard a projection while stock never is?
16. How do you enforce module boundaries in a monolith? What was your leak count?
17. Why ban cross-module foreign keys, and what do you lose?
18. Why not Kafka? What would change your mind?
19. What was the exact query that made you add a search engine, or the numbers that made you not add one?
20. Why can't `LIKE '%term%'` use a B-tree? What do pg_trgm and `tsvector` each add?
21. Why does the bot's push go through the outbox instead of calling Telegram from the endpoint? How do you respect Telegram's rate limits across many chats?
22. What is a fencing token, and why is a Redis lock alone not enough for "one import per vendor"?
23. A vendor presses "Mark shipped" in Telegram. Where is the permission checked, and how do you stop a crafted callback from shipping another vendor's order?
24. Quorum queues dead-letter at-most-once by default. What does that mean, and what did you change?

---

## 11. Common mistakes to watch for

- Sending the email inside the transaction, so a mail failure rolls back an order that should exist, or enqueueing before commit, so the worker reads rows that don't exist yet (P3).
- Running the default `acks_late=False` and calling the system "reliable" (P3).
- A `visibility_timeout` shorter than the longest task, producing duplicate runs nobody can explain (P3). Or "fixing" `consumer_timeout` by raising it instead of chunking.
- One queue for everything, so a burst of 5,000 digest emails delays a password reset (P3).
- Acking a message before processing succeeds (P4), or acking before the DB commit.
- Publishing without confirms and assuming the broker has the message; non-durable queues that look fine until the first restart (P4).
- The outbox insert not in the same transaction as the state change: "you have moved the gap, not closed it" (P7).
- Polling the outbox without a partial index; an outbox that grows forever; retention by DELETE on a hot table (P7).
- Two relays double-publishing because rows are not claimed (P7).
- Monitoring API health but not relay lag, so the system looks fine while going quietly stale (P7).
- Publishing v2 before every consumer can read it (P7).
- Building a CQRS read model for a query that did not need one (P7).
- Tuning search relevance by feel instead of against a fixed query set, or moving the pass bar after seeing the numbers (P8).
- A rebuild command that has never been run against real drift (P8).

---

## 12. How real companies differ

- **CDC instead of polling.** At scale, outbox relays are replaced by change data capture: Debezium reads the WAL and routes outbox rows to Kafka. Atlas compares that with this relay in Season 2 (2E), on lag and DB load.
- **RabbitMQ runs as a 3-node cluster**, so quorum queues really replicate and survive a node loss. Your single node exercises the semantics but not the replication.
- **Workflow engines for long jobs.** Teams often use Temporal, or a job framework with checkpoints, instead of chunked Celery tasks, so that long work has durable state by design. Your chunked import is that idea built by hand.
- **Boundaries are enforced by packaging and ownership.** Separate packages, code owners and sometimes separate repos. import-linter is the monolith's cheap version, and it fails a build instead of a code review.
- **Search.** Most large e-commerce sites end up on a search engine or a hosted search service. Many stay on Postgres FTS far longer than expected, and the judged set is how you know which one you are.
- **Notifications** are usually a platform team's service with per-channel providers (FCM, SMS gateways, email SaaS). SD9 is that service. Atlas keeps it as a module until E2's trigger fires (more than 3 channels with diverging SLOs).

The learning version is still right: each piece is the smallest version of the production pattern that still fails in the same ways.

---

## 13. Deliberately not doing

| Item | Why not now | When it arrives |
|---|---|---|
| Kafka and CDC (Debezium) | Work queues with ack and a DLQ are the need; a replayable log is not (ADR-013) | Season 2, 2E: Debezium outbox router vs this relay |
| Saga | No multi-step cross-boundary process exists yet | S9: cancel-a-vendor-group saga, ADR-034 why not 2PC |
| Caching search results | Result sets are query-specific and the catalogue changes, so the hit rate is poor and invalidation is bad (P8) | Never; hot typeahead prefixes are the exception (SD15) |
| OpenSearch | Only if the judged set fails on Postgres (ADR-016) | Stretch below, conditional |
| Exactly-once claims | At-least-once plus idempotent consumers is the honest shape | Never claimed |
| Tracing across the broker | The `trace_context` column exists; OTel does not yet | S6 |
| Payment events | No payments module yet | S5 (`payment_intent.*` through this outbox) |
| A separate search-indexer or notifications service | No forcing problem; E2's named triggers are index lag above 60 s during imports, and more than 3 channels with diverging SLOs | Only if those triggers fire |
| The `market.search-indexer` queue, unless OpenSearch is adopted | A generated `tsvector` column updates itself, so Postgres FTS needs no indexer consumer | S8 creates it in any case, bound to `product.changed`, to refresh product embeddings (or extends it, if this stage adopted OpenSearch) |
| `stock.changed` events | Nothing outside `inventory` needs a stock-change stream yet, and stock decisions never read events or projections (ADR-010, ADR-014) | S10: the extracted inventory service publishes it; market consumes it for the listing's "in stock" flag |
| Per-module databases | Checkout needs local transactions across cart, orders and promotions; logical ownership (prefixes, roles, no FKs) is enough | Physical splits only where the forcing problem is at DB level (E2) |
| Flower or a task dashboard | Optional; the observability stack arrives in S6 | S6 (queue metrics in Prometheus) |

---

## 14. Stretch

Only when the must tier closes early.

- **OpenSearch 3.x [6 h], only if the judged set fails on Postgres FTS:**
  - an ICU analyzer plus a transliteration filter; fuzziness for the misspelled queries; facets; a completion suggester (feeds SD15);
  - a derived index fed by `product.changed` through `market.search-indexer`;
  - `_bulk` indexing with backoff on 429, so the loop slows down rather than retrying harder (P8);
  - `POST /search/reindex` returning `202` plus a job resource, rebuilding into `products_v{n+1}` and swapping the `products` alias;
  - a wipe-and-rebuild test: drop the index, show search is wrong, reindex, show the judged set passes again.
  - If adopted, ADR-016 records the failing queries that justified it.
- **Quorum-queue priority for password resets [1 h]:** give the `emails` queue message priorities, so a password-reset email overtakes a backlog of digests. Demonstrate the overtaking under a 5,000-digest backlog, and read the RabbitMQ 4.3 docs on how many priority levels a quorum queue distinguishes.

---

## 15. Definition of done

- [ ] Checkout p95 before and after moving email off the request path recorded under ADR-002; checkout succeeds with SMTP down; the confirmation is sent from the event path, exactly once per checkout
- [ ] Celery queues `emails`, `imports`, `media`, `beat-jobs` with one worker each; the routing test green
- [ ] CSV import: `202` + `Location`, streamed, COPY, progress, fencing test green; chunked so it passes 30 minutes
- [ ] Sweeper with SKIP LOCKED measured at 1 vs 4 workers; the digest run-key and Tashkent boundary tests green
- [ ] Evidence for `acks_late`/`kill -9`, `visibility_timeout` redelivery and the LRU vanish
- [ ] RabbitMQ topology from code; restart N = N; the poison message through all tiers to parking, inspected; at-least-once dead-lettering proven by the missing-parking-queue test
- [ ] Celery on quorum queues with Native Delayed Delivery; the deprecated-feature workaround recorded with its TODO; the `consumer_timeout` run recorded and fixed by chunking
- [ ] Dual-write loss and phantom event recorded; the outbox atomicity test green
- [ ] **Killing the broker and a relay mid-flow loses 0 events**; two relays publish nothing twice
- [ ] Partial index, `trace_context`, `outbox_lag_seconds` in place; DELETE vs partition bloat numbers recorded; the retention guard tested
- [ ] Inbox on every consumer; Pact message contracts green in `pact-verify`; the upcaster tested; `vendor_order_view` rebuildable
- [ ] **Leak count recorded, then 0**; FK ban test green (allow-list `identity_user`); `atlas-events` wheel consumed by version
- [ ] Bot sender with the pacer: the 5,000-chat broadcast recorded before and after
- [ ] Vendor bot flow: new-order message, "mark shipped" through market's fulfillment API, the cross-vendor callback refused (tested)
- [ ] **Judged-set table filled in** for every search step; ADR-016 verdict written
- [ ] Reviews with verified purchase; aggregator idempotent (or degraded, and recorded)
- [ ] ADR-013, ADR-014, ADR-015, ADR-016 written with their numbers
- [ ] SD9, SD14, SD15 written up in `docs/sd/`
- [ ] Actual hours per block logged in the hours log; postmortem paragraph in `docs/postmortems/` (which blocks overran, and by what ratio)
- [ ] 2 STAR stories in `docs/star/`: **the lost event**, and **the `consumer_timeout` surprise**
- [ ] `docs/deferred.md` re-read and updated
- [ ] Git tag `v0.4`

Next comes the B1 buffer and checkpoint (W18, [buffers-and-job-sprint.md](buffers-and-job-sprint.md)). There you compute your measured ratio (actual hours ÷ budgeted hours, from the hours log for S0–S4) and re-plan the rest of the season with it. If you are more than one week behind, drop the remaining stretch and apply the degrade list in order ([schedule-and-cuts.md](schedule-and-cuts.md) §7, requirement-neutral items first). If a spine block overran, the date moves; nothing is deferred silently.

---

## 16. If you get stuck

**Celery (4.1)**
- If the email still slows checkout, is the enqueue really inside `on_commit`, and is the broker call itself fast? Time just the `.delay()`.
- If `kill -9` shows no difference between the settings, did the kill land *during* the task? Make the task sleep first.
- If the visibility-timeout duplicate never appears, is the task really `acks_late=True` (an early ack leaves nothing to restore)? Is your worker's prefetch holding the message, or is the timeout still at its 1-hour default?
- For the Tashkent tests: write the UTC instant, the local instant and the local date on paper for three orders, then write the assertions.
- Reread P3 D42–D47 and §11 of [03-peopleops.md](../python/03-peopleops.md) ("two things that must be right").

<details>
<summary>Check your prediction (4.1 pain-first), only after you have run it</summary>

- Synchronous email: checkout p95 grows by roughly the injected delay, and with SMTP stopped the checkout itself fails.
- `acks_late=False` + `kill -9`: the email is simply gone. The broker already counts it as delivered.
- `acks_late=True` + `reject_on_worker_lost` + `kill -9`: the task is redelivered, and without the sent marker the customer gets two emails.
- `visibility_timeout` 60 s with a 90 s `acks_late` task: a second worker starts the *same* task while the first is still running, and nothing logs an error.
- Broker on `redis-cache`: queued tasks vanish as the cache fills. No worker ever sees them, and nothing logs an error. That is the S3 split rule proven for queues.
- Plain `FOR UPDATE` on 4 workers: they queue behind each other's row locks, so 4 workers are barely faster than 1. SKIP LOCKED lets each take different rows.

</details>

**RabbitMQ (4.2)**
- If restart loses messages, check all three: the queue type, message persistence, and whether the publisher waited for confirms.
- If the countdown retry fires immediately or never, find the delay objects in the management UI. Did Celery declare them? Is the worker's queue a quorum queue?
- If the channel closes on something other than the long import, which consumer is holding a delivery unacked while doing slow work?
- If the worker refuses to start with a deprecated-feature error, reread §4.2 step 4. If the missing-parking-queue test still loses the message, check both queue arguments on *every* queue on the path, including the retry tiers.
- Reread P4 D61–D66 in [04-wareflow.md](../python/04-wareflow.md) (durability, confirms, prefetch, DLQ).

<details>
<summary>Check your prediction (4.2), only after you have run it</summary>

- With confirms off, a publish during a broker restart can be lost with no error on the publisher side.
- With the default at-most-once dead-lettering and a missing parking queue, the message leaves the last tier and disappears. With at-least-once + `reject-publish`, it stays in the source queue until the target exists.
- At minute 30 the broker closes the consumer's channel (PRECONDITION_FAILED, delivery acknowledgement timed out), requeues the delivery and the import starts again from the beginning, while the first execution's ack fails.

</details>

**Outbox (4.3)**
- If you can't make the dual-write loss happen, put the fault hook exactly between the commit and the publish, not before the commit.
- If two relays double-publish, look at the claim query. Does it lock rows, skip locked ones, and mark them before releasing the locks?
- If partition retention would drop unsent rows, what does the guard check, and what happens if the relay is down for longer than the retention window?
- Reread P7 D109–D114 in [07-fleettrack.md](../python/07-fleettrack.md) and the D75 gap in [04-wareflow.md](../python/04-wareflow.md).

<details>
<summary>Check your prediction (4.3), only after you have run it</summary>

- Publish-after-commit with the broker killed: the order row is present, `market.notifications` holds zero messages, and nothing in the logs says so.
- Publish-before-commit with a forced rollback: a phantom `order.placed` for an order that does not exist.
- Retention by DELETE: `n_dead_tup` climbs, and after VACUUM the on-disk size does not shrink (the space is reusable, not returned). Dropping a partition returns it at once.

</details>

**Consumers (4.4)**
- If a duplicate still double-applies, is the inbox insert in the *same* transaction as the effect, and does the effect run only when the insert succeeded?
- If Pact verification fails, is the provider test using the real outbox serializer, or a hand-built dict?
- Reread P7 D115–D120 (CQRS, the upcaster).

<details>
<summary>Check your prediction (4.4), only after you have run it</summary>

- Without the inbox, the second delivery doubles the projection's counter and sends a second email.

</details>

**Boundaries (4.5)**
- If the leak count feels too big to reach 0, sort the violations by target module. Usually two or three facades remove most of them.
- If a module needs another module's data on every request, is that a facade call, a snapshot column, or a sign that the two are really one module?
- Reread P4 D55–D60 (bounded contexts, the leak hunt).

**Notifications (4.6)**
- If the pacer still gets 429s, is it shared through `redis-state`, or does each sender keep its own bucket? Are you honouring `retry_after` per chat or globally?
- If two confirmation emails arrive for one checkout, is the §4.1 `on_commit` enqueue for the confirmation still in place?
- If the vendor callback test passes for another vendor's staff, where is the relationship check? It belongs in market's fulfillment service, not in the bot.
- Reread §19 of [10-atlasmarket.md](../python/10-atlasmarket.md) and the SD9 prompt in [system-design-problems.md](../../system-design-problems.md).

<details>
<summary>Check your prediction (4.6), only after you have run it</summary>

- Without the pacer: a 429 storm, with retries piling onto the limit, a long total time, and a real risk of lost or duplicated messages if the retry path is careless.
- With the pacer: the floor is about 5,000 / 30 ≈ 170 s, and the 429 count falls to about 0.

</details>

**Search (4.7)**
- If FTS misses Cyrillic queries, check which column the query hit, and whether the transliteration column is in the `tsvector` at all.
- If the judged set feels subjective, that is why the relevant ids are written down before any run.
- Reread P8 D121–D126 in [08-docuvault.md](../python/08-docuvault.md) (fixed query set, derived index, rebuild).

Previous stage: [Stage 03 — Redis, auth hardening, bot v1](stage-03-redis-auth-bot.md). Next stage: [Stage 05 — AtlasPay v1 in the monolith + provider-sim](stage-05-atlaspay-monolith.md). Stack and decisions: [README](README.md), [glossary](glossary.md), [testing-and-ci](testing-and-ci.md), [system-design-map](system-design-map.md), [schedule-and-cuts](schedule-and-cuts.md).
