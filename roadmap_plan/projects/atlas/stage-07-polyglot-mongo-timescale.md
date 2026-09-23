# Stage 07 — Polyglot I: MongoDB + TimescaleDB + fraud v1

| | |
|---|---|
| **Weeks** | W29–W31 (3 weeks) |
| **Hours** | 36 must + 5 stretch (41 total) |
| **Architecture at start → at end** | market (process types web / worker / beat / relay / consumers) + bot (sender) + provider-sim on a Terraform-provisioned VPS; stores PG17 `market` (+ replica, WAL archive), redis-cache, redis-state, RabbitMQ, the S3-compatible store (Garage), `sim` DB, Prometheus/Loki/Tempo → **same deployables** + a MongoDB 8.0 replica set (`atlas_conversations`) + a TimescaleDB cluster `tsdb` (schemas `analytics`, `pay_metrics`, `fraud_features`). market gains the `conversations` module on Mongo, velocity rules on Timescale continuous aggregates, and fraud v1 scoring in **shadow mode** inside `payments`. A new library, `libs/atlas-fraud-features`, holds the one feature function. |
| **New technologies** | MongoDB 8.0 (3-node replica set, write concerns, multi-document transactions, aggregation pipeline, TTL and partial indexes); PyMongo 4.18 (`MongoClient`, `AsyncMongoClient`); TimescaleDB 2.30 Community (hypertables, continuous aggregates, compression, retention) on `timescale/timescaledb-ha:pg17`; scikit-learn (logistic regression in the must tier; `HistGradientBoostingClassifier` is stretch); Mongo and Timescale testcontainers. Pins are as of 2026-09 — re-check with `scripts/compat_check.sh`. |
| **Portfolio tag** | `v0.7` |
| **Old-spec theory to read** | **Required, as part of the ML ramp (4.0):** phase-9 D259–D263 ([../../phase-9-ml-zoomcamp.md](../../phase-9-ml-zoomcamp.md): logistic regression, evaluation pitfalls, ROC vs PR, class imbalance). You have not reached these days in the curriculum yet, so treat them as new material, not revision. Also: P7 D109–D114 ([../python/07-fleettrack.md](../python/07-fleettrack.md), Stage 1: JSONB + GIN, "when JSONB fits and when it is a schema you were too lazy to design"); P2 D37–D39 ([../python/02-quickserve-pos.md](../python/02-quickserve-pos.md), Stage 3: live aggregate vs `REFRESH MATERIALIZED VIEW CONCURRENTLY`); P9 Wk26 ML extension ([../python/09-payflow.md](../python/09-payflow.md) §21: fraud-signal model, latency and drift panels); P4 Wk13 ML extension ([../python/04-wareflow.md](../python/04-wareflow.md) §19: IsolationForest, "anomalous is not fraudulent"). |

> **What this stage is really for.** You meet two new databases and one ML model, and every one of them has to earn its place with numbers. The main skill here is being honest: you build the Postgres version first, write down what you *predict* will happen, measure under the ADR-002 protocol, and let the result decide, even when the result is "Postgres was fine". You also train the one Season 1 model now, while there is still time, and run it in the payment path without letting it decide anything.

---

## 1. The problem this stage starts from

**Business view.** After [Stage 06](stage-06-ship-and-operate.md) the marketplace is live on a public URL, takes payments through AtlasPay and is observed end to end. Three requests now come in:

1. **Buyers and vendors need to talk.** A buyer asks about a product before paying, or a delivery goes wrong. When a buyer opens a dispute, ops need to read the conversation in Admin as evidence.
2. **AtlasPay needs velocity checks.** A velocity check asks "how many attempts has this card, phone or IP made in the last minute, hour or day?" Card-testing bots and account takeovers show up as bursts. Taking more traffic without these checks is irresponsible.
3. **Vendors want sales analytics**: daily revenue per vendor over months of history.

**Engineering view.** The Stage 06 exit row says it plainly: *analytics GROUP BYs and velocity rules are slow, and the chat table keeps growing.* In this stage you build each of these the plain-Postgres way first, and that is where the pain appears:

- A velocity rule written as `COUNT(*)` over 20M payment attempts runs inside the payment request and scans far too much.
- A vendor-sales `GROUP BY` over 20M order lines competes with OLTP traffic, even on the replica.
- Conversation messages are append-only, grow without bound and are always read one conversation at a time. That access pattern is very different from the rest of the `market` schema.

**Requirement view.** The requirements say MongoDB only "where it genuinely fits", built after a Postgres JSONB version and compared honestly. TimescaleDB is for payment metrics, fraud velocity features and vendor analytics. Season 1 also includes exactly one end-to-end ML model, AtlasPay fraud scoring. It is served as its own service in [Stage 12](stage-12-data-at-scale-fraud.md), but it has to be trained, and proven leakage-free, much earlier. That is now.

**Why now and not later.** [Stage 08](stage-08-ai-integration.md) stores AI transcripts in Mongo, and Stage 12 shards the conversations collection. Both need a Mongo you already understand. Season 2 analyses the Timescale data. Learning a new store under pressure at the end of the season is how people end up with a database they cannot defend in an interview.

---

## 2. Outcomes — what exists when the stage is finished

1. **An honest attribute benchmark.** The per-category product attributes (JSONB + GIN since [Stage 01](stage-01-layered-monolith.md)) are loaded into Mongo too. The same facet filters (9 of the 10 in the must tier), a write mix and index sizes are measured on both under ADR-002. The prediction is written down before the run, and the verdict follows the numbers.
2. **Conversations built twice.** First in Postgres: JSONB message parts, monthly partitions, measured writes/s, per-conversation p95 and retention by detaching and dropping old partitions, with its lock impact measured. Then in MongoDB 8.0 on a 3-node replica set, with schema, indexes and aggregations each verified with `explain('executionStats')`.
3. **A write-concern experiment** in which the primary is killed under `w:1` and under `w:"majority"`, with the count of acknowledged-but-lost writes recorded for each.
4. **A live migration** of conversations from JSONB to Mongo (dual-write through an outbox consumer, backfill, read switch) with a verification count.
5. **A Timescale cluster `tsdb`** started first on an `-oss` image, which breaks when you create the first continuous aggregate (the edition trap), and then on `timescale/timescaledb-ha:pg17`.
6. **Three hypertables** fed by outbox consumers: `pay_metrics.attempts`, `analytics.order_lines`, `fraud_features.events`.
7. **Velocity continuous aggregates** (`fraud_features.velocity_1m`, `velocity_1h`, `velocity_24h`) per card fingerprint, phone, merchant and IP, with real-time aggregation. The payments velocity rules read them.
8. **Vendor daily sales**: raw `GROUP BY` → materialized view (refresh cost measured) → `analytics.vendor_sales_daily` CAGG, plus compression after 7 days (ratio recorded), retention (90 days raw, 13 months aggregates) and a CAGG-vs-raw correctness test.
9. **Fraud v1**: an ML ramp in `sandbox/` first; then synthetic fraud patterns in worldgen, one feature function in `libs/atlas-fraud-features` shared by training and serving, a point-in-time-correct training set with a leakage test, a logistic regression beating (or honestly failing to beat) the rules baseline on a time-based split, an artifact in the `atlas-models` bucket with sha256 and feature-code version, a model card, and **shadow scores stored on every attempt, never enforced**.
10. **Documents:** ADR-024 (JSONB vs Mongo, both workloads), ADR-025 (Timescale vs matview vs Prometheus), ADR-026 (fraud v1), an updated ADR-003 licence register, SD8 storage-half notes, 2 STAR stories and a postmortem paragraph. Tag `v0.7`.

---

## 3. Architecture at the end of the stage

```
                         Internet (HTTPS)
                               |
                         Nginx (VPS, S6)
             /api /admin       |        /providers/*  (own gunicorn pool)
                               v
   +-----------------------------------------------------------+     +--------------+
   | market (Django 5.2)                                        |<--->| provider-sim |
   |  web | worker | beat | relay | consumers                   |     +--------------+
   |  modules: ... conversations (Mongo), analytics,            |
   |           payments (+ velocity rules, shadow fraud score)  |
   |  consumers: tsdb.analytics-writer, tsdb.pay-metrics-writer,|
   |             fraud.features, market.chat-mongo-sync (temp)  |
   +---+------------+-------------+-------------+-----------+---+
       |            |             |             |           |
  PG17 market   redis-cache   RabbitMQ      Garage (S3)  bot (sender)
  (+ replica)   redis-state   atlas.events  atlas-models
       |
       |  outbox events: order.placed, payment_attempt.created,
       |                 chat.message_sent, ...
       v
  +-------------------------------+      +--------------------------------------+
  | MongoDB 8.0 replica set       |      | tsdb: TimescaleDB 2.30 on PG17        |
  | db atlas_conversations        |      |  analytics.order_lines  -> CAGG       |
  |  conversations, messages      |      |     analytics.vendor_sales_daily      |
  | local: primary + 2 secondaries|      |  pay_metrics.attempts                 |
  | VPS: single-member set        |      |  fraud_features.events -> CAGGs       |
  +-------------------------------+      |     velocity_1m / velocity_1h / 24h   |
                                         +--------------------------------------+
```

**What changed and why**

| Change | Why |
|---|---|
| Conversations move to Mongo (`atlas_conversations`), owned by market's `conversations` module | Document-shaped, append-only, TTL-driven, always read per conversation, and due to scale out in Stage 12. ADR-024 must also admit that Postgres partitions were adequate at the scale you measured. |
| Catalog attributes **stay** in Postgres JSONB | Predicted (and, you will check, confirmed) by the benchmark: attributes commit in the same transaction as offers and live under RLS. |
| `tsdb` is a **separate** Timescale cluster, not an extension inside `market` | Analytics and fraud-feature writes and scans stay off the OLTP primary; the TSL-licensed extension and its version cadence stay isolated; `fraud_features` moves with the fraud service in Stage 12. |
| Hypertables are fed by **outbox consumers** | They are projections. Postgres stays the truth for orders and money, so every hypertable must be rebuildable from it. |
| Fraud scoring runs **in-process** in `payments`, in shadow | You learn the latency, the failure modes and the image-size cost before you decide in Stage 12 whether it deserves its own service. Stage 09 moves this path, with the rest of the payments code, into atlaspay. |
| The feature function lives in `libs/atlas-fraud-features`, a framework-free wheel | The trainer and Django `payments` import it now; FastAPI atlaspay (Stage 09) and the gRPC fraud service (Stage 12) import the same wheel later. One definition of a feature, in every process that computes one. |
| On the VPS, Mongo runs as a **single-member replica set** | Transactions need a replica set, even with one member. The 3-node set and the primary-kill experiment run locally. Cloud HA for Mongo exists only locally; say so in the README. |

Names used here come from the [glossary](glossary.md). The temporary dual-write consumer reads the queue `market.chat-mongo-sync`; you delete the queue once reads have switched to Mongo and the Postgres writes have stopped.

---

## 4. Build plan

Before you start, run `scripts/compat_check.sh` against the new images (`mongo:8.0`, `timescale/timescaledb-ha:pg17`). Record the server and extension versions in `docs/evidence/s07/compat.txt`. Check your RAM too: on a 16 GB laptop, give this stage its own Compose profile and stop the Stage 06 observability stack while you run the Mongo replica set.

**Hours.** The blocks below add up to the 36 h must tier: 2.5 + 15 + 9 + 7 + 2.5. Keep logging actual hours per block, as you have since Stage 00. Multiply this stage's budget by the actual/budget ratio you computed at B1: if the result does not fit in W29–W31, the plan's dates move now, openly, at the stage start. Do not quietly defer must-tier work.

### 4.0 ML ramp [2.5 h must]

**Why this block exists.** Fraud v1 (4.3) is the first ML model you have ever trained. Learning scikit-learn through Atlas's payment path would mix two unknowns, as learning Django through Atlas code would have in Stage 01. So the ramp happens in a throwaway `sandbox/ml-ramp/` that nothing imports. It is not a workspace member and is excluded from strict type checks and coverage. Do it any time before 4.3. The first evenings of the stage, while the Mongo replica set is still new, are a good slot.

**Read first:** phase-9 D259–D263 ([../../phase-9-ml-zoomcamp.md](../../phase-9-ml-zoomcamp.md)), each day's theory reading only (not its project work): logistic regression and log-loss, coefficients, the accuracy trap and precision/recall, ROC/AUC, and class imbalance with `class_weight`.

**Build on a toy imbalanced dataset** (for example `sklearn.datasets.make_classification` with about 1% positives, plus a fake timestamp column). Give it some **drift**: in the last third of the time range, shift one feature for the positives, the way fraud patterns change from month to month.

1. `fit` / `predict_proba` with `LogisticRegression`. What does `predict` do that `predict_proba` does not, and why will 4.3 never use `predict`?
2. A `Pipeline` (scaler + model). Why does the scaler have to live *inside* the pipeline for the split to stay honest?
3. A random split against a **time split** on the fake timestamp (train on the oldest part, test on the newest). Predict which scores higher, commit it, then record both scores.
4. `class_weight="balanced"` against no weighting: precision, recall and PR-AUC for each.
5. A precision-recall curve, and the threshold that minimizes a cost you invent (false positive = 1, false negative = 20).

Write a one-page `docs/learning/ml-ramp.md`: the five results, and one sentence each on accuracy, PR-AUC, class weighting and a cost-based threshold, in your own words. **Calibration** (whether a predicted 0.2 really means "fraud 20% of the time") is only named here. The calibration curve is a stretch item.

**Acceptance criteria.** The five exercises run from `sandbox/ml-ramp/`, and the notes file exists. The mentor may ask you to explain any line of it.

### 4.1 MongoDB [15 h must]

Suggested split of the 15 h: (a) benchmark 3 h, (b) conversations in Postgres 3 h, (c) Mongo replica set, schema, indexes, aggregations, transactions, write concerns, migration and access 9 h. Part (c) is your first contact with Mongo, so spend its first hour on the official MongoDB CRUD and indexes pages and the PyMongo tutorial before you write Atlas code.

#### (a) The honest attribute benchmark

**What to build.** A benchmark under `bench/` (ADR-002 protocol) that runs the same workload against:

- **Postgres:** `catalog` products with the JSONB `attributes` column and GIN `jsonb_path_ops` index from Stage 01. You may add expression indexes for the two or three hottest range-filtered attributes, because that is what a competent Postgres team would do.
- **Mongo:** a throwaway benchmark database on your local replica set, loaded from the same worldgen seed. Give Mongo its best idiomatic design too. Research the *attribute pattern* (an array of `{k, v}` pairs with a compound index) and *wildcard indexes*, choose one, and record why.

Fairness rules (write them into the benchmark README):

1. The same container CPU and memory limits for both. Set the WiredTiger cache size and Postgres `shared_buffers` explicitly and record both.
2. The same data (worldgen version and seed recorded), the same warm-up (60 s) and at least 3 runs, reporting median and min–max, with p95/p99 from HDR histograms.
3. Each side gets its best index design. A benchmark where one side has no index measures your laziness, not the database.
4. **Correctness cost is a column in the result.** If the Mongo side needs a dual write to keep price in sync, or loses RLS, that counts against it even if it is faster.

**Wall-clock time.** One run is one 60 s warm-up followed by each query shape and write for a fixed 30 s. With about 12 shapes that is roughly 7 minutes per run, and 3 runs per engine make about 45 minutes of unattended benchmark time. It is included in the 3 h of part (a). Schedule the runs in the weekend block, and write the prediction and the harness on weekday evenings.

**The benchmark matrix to fill in** (`docs/evidence/s07/attr-bench.csv`, summarized in ADR-024):

| # | Query shape (you choose concrete attributes per category) | PG p95 (median, min–max) | Mongo p95 | Index used (PG plan / Mongo winning plan) | Notes |
|---|---|---|---|---|---|
| F1 | One attribute equality in one category | | | | |
| F2 | Two attribute equalities (AND) | | | | |
| F3 | Numeric range on an attribute | | | | Does `jsonb_path_ops` GIN help here? Check the plan. |
| F4 | IN-list on an attribute | | | | |
| F5 | F2 + `status='published'` + sort by price + keyset page | | | | Price lives in offers. What did Mongo have to denormalize? |
| F6 | Attribute key exists | | | | |
| F7 | Facet counts: products per value of one attribute in a category | | | | The storefront sidebar |
| F8 | Three facet counts at once | | | | `$facet` vs several aggregates |
| F9 | Category subtree (the recursive tree from S1) + an attribute filter | | | | *Stretch* (§14): the Mongo side needs its own tree design |
| F10 | F7 restricted to one vendor (vendor dashboard) | | | | RLS on the PG side; what enforces it on the Mongo side? |

| Write mix | PG throughput / p95 | Mongo throughput / p95 | Correctness cost |
|---|---|---|---|
| W1 update one attribute | | | |
| W2 insert a product with attributes | | | |
| W3 change an offer's price or stock | | | In PG, one transaction. In Mongo, a second write in another store. |
| W4 bulk import 10k products (the S4 import path) | | | *Stretch* (§14) |

| Size | PG | Mongo |
|---|---|---|
| Data size | | |
| Each index size (`pg_relation_size`; Mongo `indexSizes` from collection stats) | | |

**The prediction, written before you run anything** (paste it into ADR-024 with a timestamp): *"JSONB wins, because attributes are transactional with offers and live under RLS."* The prediction is not "Postgres is faster". Mongo may well win some rows. The claim is that the **total** of speed plus correctness cost favours JSONB.

**What would change the decision.** Write these into ADR-024 as explicit reversal conditions:

- Mongo beats Postgres by more than the run spread on the hot storefront queries (F5, F7, F8), **and** that gap still hurts after the Stage 03 cache, **and** the correctness cost column is acceptable (no lost vendor isolation, no unsafe dual write).
- Attribute schemas become so varied that neither GIN nor a handful of expression indexes can serve the hot range filters.
- Attributes stop needing to commit with offers, for example because offers move to another service.
- The catalog needs to scale writes beyond one Postgres primary. The named future split, "catalog read service", only triggers when reads exceed what 2 replicas can serve.

**Pain-first exercise**

1. Run F3 on Postgres with only the GIN index → look at the plan → record whether the range predicate used the index or was rechecked on a large candidate set (`docs/evidence/s07/attr-f3-plan.txt`).
2. Run F5 on Mongo with price **not** denormalized → observe what the query costs (`$lookup` or two round trips) → denormalize and record the extra write that W3 now needs.
3. Run F10 on Mongo → notice that nothing in the database stops a query that forgets the vendor filter → record it as a correctness-cost row.

**Acceptance criteria**

- Both engines ran the same seed under ADR-002, with digests and limits recorded.
- Every must-tier row in the matrix (F1–F8, F10, W1–W3 and sizes) is filled, differences inside the run spread are marked "no difference", and the prediction timestamp is earlier than the first result.
- ADR-024's attribute section states the verdict and the reversal conditions.

#### (b) Conversations built in Postgres first

**What to build.** A `conversations` module in market:

- `conversations_conversation`: participants (buyer, vendor), optional order reference, status, dispute flag, last message time, per-participant unread counters.
- `conversations_message`: conversation id, a per-conversation `seq`, sender, `parts` as JSONB (text, image reference, order reference), `client_msg_id` for dedup, created_at. **Range-partitioned by month** on created_at, with the partition maintenance you already know (pg_partman plus a DEFAULT partition, from Stage 04).
- A participants-only API (buyer, vendor staff of *that* vendor) and a read-only **dispute evidence view in Admin** for ops.
- Worldgen chat traffic: Pareto-distributed conversations (a few very chatty vendors), bursts around delivery days.

**Measure** (ADR-002):

| Metric | Value |
|---|---|
| Sustained message inserts/s at the container limits | |
| p95 "latest 50 messages of one conversation" | |
| p95 "vendor inbox with unread counts" | |
| Time and lock impact of removing the oldest month (detach the partition, then `DROP TABLE` it) | |
| Table and index size per month of messages | |

(PostgreSQL has no `DROP PARTITION` statement; that is MySQL and Oracle syntax. A partition is a table: you detach it, then drop it.)

**Pain-first exercise.** Run retention the naive way first: `DELETE` messages older than N months in batches → watch `n_dead_tup`, the vacuum work and the replica lag → then remove a partition instead → record both in `docs/evidence/s07/chat-retention.md`. Removing a partition has its own trap, the Stage 06 lock queue. Start a long `SELECT` on the messages table in another session, then compare a plain `DETACH PARTITION` (or a direct `DROP TABLE` on the partition) with `DETACH PARTITION … CONCURRENTLY` followed by `DROP TABLE`. Before you run it, predict which lock each variant takes on the parent table and what happens to new chat queries meanwhile, and commit the prediction. Then run it, record what you saw in `pg_locks`, and check it against the PG17 `ALTER TABLE` and "Table Partitioning" docs. Read the restrictions on `CONCURRENTLY` there too, and compare them with how your Stage 04 partition set is built. If they clash, decide how your retention job removes a month without stalling chat, and write the decision down. You saw the DELETE lesson with the outbox in Stage 04. Here it becomes the argument **for** Postgres: removing a month is cheap on data, while TTL deletes in Mongo are document-by-document deletes. Keep that honest point for ADR-024, together with the lock you had to avoid.

**Acceptance criteria.** A non-participant gets 404 (not 403, to avoid leaking existence) in a permission test. The Admin evidence view works. All five metrics are recorded.

#### (c) MongoDB 8.0 replica set: schema, indexes, transactions, write concerns, migration

**Why 8.0.** 8.0 is the current major line. Newer minors (8.2, 8.3) exist but are offered on-prem only for specific use cases. Pin 8.0 and let `compat_check.sh` flag changes.

**Driver.** PyMongo 4.18: `MongoClient` inside Django (market is sync) and `AsyncMongoClient` in async services (ai uses it in Stage 08). **Not Motor**: it reached end of life on 2026-05-14 and only gets critical fixes until 2027-05-14. An interviewer who sees Motor in a 2026 repo will ask why.

**Steps and requirements**

1. **Replica set.** Three `mongod` containers with a replica-set name, initiated once, with healthchecks that check replica-set status (not just "the port is open"). Connect with a replica-set connection string so the driver discovers the topology.
2. **Schema, measured, not guessed.** Model `atlas_conversations.conversations` and `atlas_conversations.messages`, and compare two message layouts under the same chat load:
   - *message-per-document*: one document per message;
   - *bucket*: one document per conversation per N messages (or per day).

   Embedding every message inside the conversation document is not an option. Documents have a 16 MB limit, and an unbounded array is a classic mistake. Write down why you rejected it.

   A message document has roughly this shape (the shape is the requirement, the field names are yours):

   ```
   { conversation_id, seq, sender: {kind, id}, parts: [ {type, ...} ],
     client_msg_id, created_at, expires_at? }
   ```
3. **Indexes, each checked with `explain('executionStats')`.** Look at the winning plan, `totalDocsExamined` against `nReturned`, and whether a `SORT` stage appears in memory.
   - `(conversation_id, seq)` for the conversation view;
   - a **TTL index** for retention. Decide whether retention applies to conversations under dispute. A **partial** index is how you keep dispute evidence out of TTL;
   - a unique index on `(conversation_id, client_msg_id)` that makes client resends safe (Stage 11's chat relies on it). Note it for later: in Stage 12, a unique index limits which shard keys MongoDB will accept for this collection;
   - one more partial index if an inbox query needs it.

   Commit each explain output to `docs/evidence/s07/mongo-explain/`.
4. **Aggregations.** Unread counts per participant, and vendor response time (median time from a buyer message to the next vendor message, per vendor per week) as aggregation pipelines. Check their explain output too.
5. **A multi-document transaction.** Inserting a message and updating the conversation counters (`seq`, `last_message_at`, the other side's unread count) must commit together. Show first that this **fails on a standalone `mongod`**. Transactions need a replica set (or a sharded cluster) and read preference `primary`, with one open transaction per session.
6. **The write-concern experiment**, below.
7. **Migration JSONB → Mongo, live.**
   1. *Dual-write*: market keeps writing to Postgres. A consumer on the temporary queue `market.chat-mongo-sync`, bound to `chat.message_sent` on `atlas.events`, writes the same message into Mongo, idempotently on the event id plus the `(conversation_id, client_msg_id)` unique index.
   2. *Backfill*: stream old messages from the replica with a server-side cursor (the Stage 05 statement pattern) into Mongo in batches, with flat memory.
   3. *Verify*: per-conversation counts and max `seq` equal on both sides. Commit the diff report.
   4. *Switch reads* behind a setting and keep dual-write for a few days.
   5. *Stop the Postgres writes* only after the diff stays at 0. The Postgres tables become read-only history and follow the retention table. Then unbind and delete `market.chat-mongo-sync`.
8. **Participants-only access.** Mongo has no RLS. The `conversations` module's `api.py` is the only code that queries these collections, and every query it builds includes the participant filter. A test crafts a request as another buyer and as another vendor's staff and expects 404.
9. **Admin.** Django Admin works on ORM models, so the Mongo-backed evidence view becomes a custom read-only admin page that calls the module's `api.py`. Log every ops read of a conversation.

**The write-concern experiment (`w:1` vs `w:"majority"`)**

Some background first. **`w:1`** means the primary acknowledges a write as soon as it has applied it, before any secondary has a copy. **`w:"majority"`** means the acknowledgement waits until a majority of voting members have the write. If a primary dies holding writes that no secondary has, the remaining members elect a new primary without them. When the old primary rejoins, it **rolls back** those writes and saves them to rollback files. The client was told "ok" for data that no longer exists. The default write concern has been majority since MongoDB 5.0, so to see the loss you must deliberately opt into `w:1`. That is exactly what teams do "for speed".

Steps:

1. Write a load script that inserts messages with increasing sequence numbers and appends every **acknowledged** id to a local file.
2. Run it with `w:1`. You need a **window** in which the client can still reach the primary, but no secondary can replicate from it. Which topology or container-level action gives you that? Think about which Docker networks the client and each `mongod` are attached to, or about freezing the secondary containers. Cutting the primary off from *every* network also cuts off your load script, so that alone gives no window. How long will an isolated primary keep acknowledging `w:1` writes before it steps down? Look up `electionTimeoutMillis`. Record the window length you expect; your loss count should be bounded by it.
3. Kill the primary while the window is open. Let the secondaries elect a new primary (undo whatever you did to them in step 2), then restart the old primary and let it rejoin.
4. Count: acknowledged ids that are **missing** from the collection. Look inside the old primary's rollback directory and record what you find.
5. Repeat with `w:"majority"` (and a `wtimeout`), using the same window.
6. Record latency for both runs.

Before step 2, write your prediction for every column of the table below (lost count, latency, errors during the election) and commit it. Then run.

| Write concern | Attempted | Acknowledged | Present after failover | Acknowledged but lost | p50 / p95 write latency | Errors or timeouts during election |
|---|---|---|---|---|---|---|
| `w:1` | | | | | | |
| `w:"majority"` | | | | | | |

Record the numbers in `docs/evidence/s07/write-concern.csv` and the story in a STAR. Compare them with your committed prediction; §16 has a "check your prediction" note.

Two things to write down while you are here:

- **Retryable writes.** PyMongo retries a write once on a network error or a "not primary" error, and the server deduplicates that retry itself (by session id and transaction number), so the driver's own retry never inserts twice. What, then, does the `(conversation_id, client_msg_id)` unique index protect against that retryable writes do not? Think of a client that resends after a timeout, a dual-write consumer that gets a redelivery, a writer that restarts. Those resends surface as a duplicate-key error (E11000). How does your code treat it, and why must it count as success?
- **Read concern.** Why does an acknowledged majority write not help a reader who reads from a lagging secondary? Chat reads use primary read preference in this stage.

**Acceptance criteria**

- The replica set survives a primary kill under chat load with **0 acknowledged writes lost** under majority.
- The transaction test fails on standalone and passes on the replica set.
- Every index has a committed explain output.
- The migration diff is 0 before reads switch, and the participants-only test passes against Mongo.

### 4.2 TimescaleDB [9 h must]

Suggested split of the 9 h: steps 1–2 (baseline and edition trap) 1.5 h, step 3 (hypertables, consumers, rebuild) 3 h, step 4 (velocity CAGGs) 2 h, step 5 (vendor sales comparison) 1.5 h, step 6 (compression, retention, correctness) 1 h. Loading 20M worldgen rows into each store takes unattended time; start the loads before the evenings you need them.

**Some background.** A **hypertable** is a Postgres table that Timescale splits into time-based chunks automatically. A **continuous aggregate (CAGG)** is a materialized view over a hypertable that refreshes **incrementally**, only the time buckets whose raw data changed, instead of recomputing everything. **Real-time aggregation** lets a CAGG query combine the materialized buckets with the newest raw rows that have not been materialized yet. The company behind it, Timescale Inc., was renamed TigerData in June 2025; the extension is still called TimescaleDB and its docs now live on tigerdata.com.

#### Step 1: velocity rules v0 in plain Postgres (the baseline)

Write the velocity rules as plain `COUNT`s over 20M `payments` attempts in the market DB (worldgen history). For example: attempts per card fingerprint in the last 1 minute, 1 hour and 24 hours; attempts per phone; attempts per IP. Run them the way the payment path would, one rule set per attempt. Commit `EXPLAIN (ANALYZE, BUFFERS)` and timings to `docs/evidence/s07/velocity-v0/`. Then ask yourself: *how much of the payment latency budget did the rules just eat, and what happens to that number as the table grows?*

The card fingerprint is a pseudonymous identifier generated by worldgen and the simulator. Atlas never holds a card number (the Stage 05 PCI note). What a real provider would expose to a merchant about a card is an open question to record in ADR-026.

#### Step 2: the `-oss` edition trap

1. Start `tsdb` on the tag with the `-oss` suffix of the plain `timescale/timescaledb` image for pg17.
2. `CREATE EXTENSION`, create a hypertable. It **works**, because hypertables are in the Apache-2 edition.
3. Create the first continuous aggregate (`CREATE MATERIALIZED VIEW … WITH (timescaledb.continuous)`). It **fails**. Copy the exact error text; it names the licence.
4. Check which licence the server runs, for example `SHOW timescaledb.license;`.
5. Switch to `timescale/timescaledb-ha:pg17`, repeat, and check that the licence now reports the community (TSL) edition.
6. Update ADR-003 (the licence register). **TSL** is the Timescale License, the source-available licence of the "Community" features. CAGGs, compression, retention policies and `add_job` are **TSL features**, free to self-host but not to offer as a database service. Make `compat_check.sh` print the Timescale licence so the trap cannot come back silently.

Record the trap in `docs/evidence/s07/oss-trap.md`. It is a STAR story. The lesson is that the failure appears **late**, at the first continuous aggregate (or the first compression or retention policy), not at install time. A demo that "works" on `-oss` breaks the day someone adds an aggregate or retention.

#### Step 3: hypertables fed by outbox consumers

| Hypertable | Fed by (queue) | Source events | Used for |
|---|---|---|---|
| `pay_metrics.attempts` | `tsdb.pay-metrics-writer` | `payment_attempt.created` (on the payments outbox since Stage 05) and the `payment_intent.*` outcomes | Payment success-rate series, provider latency, SLO context |
| `analytics.order_lines` | `tsdb.analytics-writer` | `order.placed` (line-level data in the event) | Vendor sales |
| `fraud_features.events` | `fraud.features` | `payment_attempt.created` plus identity signals | Velocity CAGGs, training data |

Who runs the two payment-side consumers changes over the season. `tsdb.pay-metrics-writer` is a market process in Stages 07–08 and an atlaspay process from Stage 09. `fraud.features` is a market process in Stages 07–08, an atlaspay process in Stages 09–11, and the fraud service's from Stage 12. Stage 09 ports both with the payments code, so write them against the payments module's own interfaces, not against other market modules.

Requirements:

- **Idempotent writes into a different database.** Stage 04's inbox table lives in the market DB, and it cannot commit in the same transaction as a write into `tsdb`. Where must the dedup record live so that it commits together with the hypertable row? Note that a unique index on a hypertable must include the time column.
- **Rebuildable.** A management command rebuilds each hypertable from Postgres source tables (read from the replica, streamed, batched). A test truncates a hypertable, rebuilds it and compares the aggregates.
- **Chunk interval.** Choose it from expected rows per day and memory. Write down the number and the reason.
- One DB role per writer (the `<svc>_app` convention), with grants limited to its schema.

#### Step 4: velocity CAGGs with real-time aggregation

- `fraud_features.velocity_1m`, `velocity_1h`, `velocity_24h`, grouped per card fingerprint, phone, merchant and IP. (Distinct counts, for example "distinct cards per IP", need care: check what CAGGs in 2.30 support and whether you need an approximate hyperfunction.)
- Refresh policies with start and end offsets you can justify.
- **Real-time aggregation on**, because a velocity rule at time *t* must count the attempt from 20 seconds ago that no refresh has materialized yet. The default for `timescaledb.materialized_only` has changed between versions, so set it explicitly and test it.
- The payments velocity rules now read the CAGGs instead of `COUNT(*)` over raw rows. Rule hits are recorded with the attempt. Whether a hit blocks or only flags is ADR-026's call. The safe default in Stage 07 is **flag for review**, because the labels are synthetic and nobody has tuned thresholds on real traffic.

**Pain-first exercise.** Measure the rule-set latency at payment time three ways: v0 raw counts, CAGG with `materialized_only`, CAGG with real-time aggregation. Also insert an attempt, and read the 1m velocity immediately under each mode. Record the latency and the **correctness** (did the rule see the attempt?) in `docs/evidence/s07/velocity-cagg.csv`.

#### Step 5: vendor daily sales, raw → matview → CAGG (the second honest comparison)

This repeats the P2 D37–D39 exercise at 20M rows, with a third contender.

| Variant | p95 "one vendor, last 30 days" | p95 "all vendors, yesterday" | Refresh cost (time, WAL/IO, locks) | Staleness at query time | Storage | Equals raw? |
|---|---|---|---|---|---|---|
| Raw `GROUP BY` on the market replica | | | — | 0 | — | by definition |
| Raw `GROUP BY` on `analytics.order_lines` | | | — | consumer lag | | |
| Matview + `REFRESH ... CONCURRENTLY` | | | | refresh interval | | |
| CAGG `analytics.vendor_sales_daily`, materialized only | | | | policy lag | | |
| CAGG with real-time aggregation | | | | ~0 | | |

**Predict first.** Before you fill the table, write down how you expect each variant's refresh cost to grow as history grows from 1 month to 13 months, and why. Read what `REFRESH MATERIALIZED VIEW CONCURRENTLY` actually does and what a CAGG refresh actually does, then commit the prediction. Measure the refresh cost at two history sizes at least, so growth is visible. §16 has a "check your prediction" note. **What would change the decision:** if daily staleness is acceptable and the table stays small, the matview is simpler and ADR-025 must say so. If the analytics need ad-hoc wide scans over many dimensions, the honest answer is a columnar store (ClickHouse, part of the SD19 answer, not built). If the data is operational metrics about the system, it belongs in Prometheus.

#### Step 6: compression, retention, and a correctness test

- **Compression** (current docs call it the columnstore or hypercore) on chunks older than 7 days. Choose the segment-by and order-by columns from the query patterns, and record the **compression ratio** and the effect on a 30-day query.
- **Retention:** raw hypertables 90 days, aggregates 13 months. Guiding question: *what happens to a 13-month aggregate if its refresh window reaches back into raw data that retention has already dropped?* Test it before you trust it.
- **CAGG-vs-raw correctness test:** for a closed time range, the CAGG result equals a raw `GROUP BY` exactly. For the open range, the test states which mode it expects (real-time or materialized-only) and asserts accordingly.

**Acceptance criteria.** The `-oss` trap is documented, velocity rules read the CAGGs, the matview-vs-CAGG table and the compression ratio are recorded, the rebuild and correctness tests pass, and ADR-025 cites the numbers.

### 4.3 Fraud v1 [7 h must]

Do the ML ramp (4.0) first. Suggested split of the 7 h: worldgen patterns 1 h, the feature library with point-in-time correctness and the leakage test 2 h, split + baseline + logistic regression + metrics 1.5 h, artifact and model card 1 h, shadow scoring 1.5 h. The must tier trains **one** model, logistic regression. HistGradientBoosting, precision@k and the calibration curve are stretch (§14).

**The shape of the problem.** Fraud is rare, which makes the classes **imbalanced**: perhaps a few attempts in a thousand. Labels arrive late: a real chargeback lands weeks after the payment, so there is a **label delay**. The patterns also change over time, so a random train/test split lies about how the model will do next month. Everything below exists because of those three facts.

**Steps and requirements**

1. **Worldgen fraud patterns** (in `libs/atlas-worldgen`), each with a label:
   - *card testing*: bursts of small attempts, many cards, one IP or device, a high failure rate;
   - *account takeover*: an old account changes phone or device, then places high-value orders;
   - *amount spikes*: amounts far above the customer's or the merchant's history.

   Labels are **declared synthetic** in the model card, and each label has an **availability time** (attempt time + delay). The model can only honestly claim to find patterns you planted. Say so.
2. **One feature function for training and serving.** It lives in a new framework-free, versioned library, `libs/atlas-fraud-features` (import `atlas_fraud_features`), built and installed as a wheel the way `atlas-common` is (Stage 00). It computes the feature vector for "attempt X at time *t*" and carries a version string. The training script and the payments module import it now. FastAPI atlaspay (Stage 09) and the gRPC fraud service (Stage 12) will import the same wheel, which is why it must not import Django. Guiding question: *if the library cannot import Django or a DB driver, how does it get the velocity counts it needs?* (Think of the ports from Stage 01: who passes in a reader?) Training-serving skew (the model saw one feature definition in training and another in production) is the most common silent ML bug, and one shared function is the cheapest defence.
3. **Point-in-time correctness.** Every feature for an attempt at time *t* uses only events that happened **before** *t*. Watch for two traps:
   - *Bucket alignment.* A materialized 1h bucket that contains *t* also contains events **after** *t*. Serving at time *t* never sees those future events, but a training query that reads the finished bucket does. How does your single feature function avoid this?
   - *Label leakage.* Features derived from the outcome (a refund, a manual review, a chargeback) must not appear in training. Neither may labels that were not yet available at the training cutoff.

   **Leakage test:** build the features for an attempt at *t*, insert an event at *t* + 1 s that would change a velocity count, rebuild the features "as of *t*", and assert they are unchanged.
4. **Time-based split.** For example: train on the oldest months, validate on the next, test on the newest. Also compare against a **rules-only baseline** (the Stage 4.2 velocity rules). A model that does not beat the rules does not ship, not even in shadow (P7 Wk20 lineage: beat the naive baseline first).
5. **One model: logistic regression**, a straight line through the features, which you can explain coefficient by coefficient. Put it in a `Pipeline`, as in the ramp, and use class weighting (or an equivalent) for the imbalance. A tree model (`HistGradientBoostingClassifier`) is the stretch comparison in §14.
6. **Metrics that fit the problem:**
   - **PR-AUC** (area under the precision-recall curve). ROC-AUC looks excellent on imbalanced data because true negatives are so many.
   - a **cost-based threshold**: choose the threshold that minimizes (cost of a false positive × FP) + (cost of a false negative × FN), with both costs written down as assumptions.

   | Model | PR-AUC (test) | Recall at threshold | Expected cost at threshold | Train time | In-process p95 score time | Artifact size |
   |---|---|---|---|---|---|---|
   | Rules only | — | | | — | | — |
   | Logistic regression | | | | | | |
7. **Artifact.** Upload the model to the `atlas-models` bucket (the S3-compatible store) with its **sha256**, the feature-code version, the training data window, the worldgen seed and the metrics. The loader refuses to load if the sha256 does not match. Write a **model card**: intended use (shadow only), data (synthetic), metrics, threshold and costs, known limits, and an owner.
8. **Shadow scoring in-process inside `payments`.** Stage 09 moves this path into atlaspay, so keep model loading and scoring behind the payments module's own interfaces. The port should then be a move, not a rewrite.
   - Load the model **once** at process start, never per request, and verify its hash.
   - For every attempt, compute the features, score, and store the score and `model_version` (plus the feature version) on the attempt or on a side table keyed by attempt id. Decide which and record why.
   - The score is **never enforced**: no code path reads it to change the outcome. A test proves it.
   - Scoring has a strict time budget. On timeout or error, record "unscored" and continue. Shadow scoring must never fail a payment.
   - Record the score-time histogram (the glossary metric is `fraud_score_seconds`) and the market image size before and after adding scikit-learn. Both are evidence for ADR-042 in Stage 12.

**Pain-first exercise.** Predict first, and commit it: which split will score higher, and will the leakage fix raise or lower PR-AUC? Then do a random 80/20 split → record the PR-AUC → do the time-based split → record it → explain the difference in ADR-026. Then build training features from the **finished** 1h buckets without the point-in-time rule → run the leakage test → watch it fail → fix it → record the before/after metrics. §16 has a "check your prediction" note.

**Acceptance criteria.** The leakage and feature-parity tests pass, a hash mismatch refuses to load, shadow scores and `model_version` are stored for every attempt in a checkout run, the no-enforcement test passes, and ADR-026 and the model card are committed.

### 4.4 Drills + SD8 (storage half) [2.5 h must]

- **Drill hour:** one SQL problem on the Atlas schema (suggestion: vendor response time as a window-function query on the Postgres conversation tables, then the same question as a Mongo aggregation) and one DSA problem from the bank.
- **SD8 storage half** (see §9), about 1.5 h.

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| Postgres remains the truth for orders and money; Timescale (and OpenSearch, if adopted in S4) are rebuildable projections | Hypertables are written only by outbox consumers; rebuild commands read from Postgres | Truncate → rebuild → aggregates equal the pre-truncate values |
| Acknowledged chat writes use majority | The conversations client is configured with `w:"majority"`; no per-call override is allowed | Primary-kill test under load: acknowledged-but-lost = 0; a config test fails if the write concern is not majority |
| Only a conversation's participants can read it | Every query goes through `conversations/api.py`, which always adds the participant filter; ops reads go through the logged Admin view | Crafted requests as another buyer and another vendor's staff get 404 |
| Training features and serving features come from the same code | One versioned, framework-free wheel (`atlas_fraud_features`) imported by both the trainer and `payments` (later atlaspay and fraud) | Feature-parity test: training path and serving path produce identical vectors for the same attempt and time |
| Features are point-in-time correct | The feature function takes an explicit "as of" time and never reads buckets that contain later events | Leakage test with an event at *t* + 1 s |
| A shadow score never changes a payment outcome | The outcome code does not read the score; scoring failures are caught and recorded | No-enforcement test; a scoring timeout test in which the payment still succeeds |
| A model is loaded only if its hash matches | Loader compares sha256 against the artifact metadata | Tampered artifact is refused at startup |
| CAGG results equal raw aggregates for closed ranges | Refresh policy plus the correctness test | CAGG-vs-raw test |
| Every chat message is stored once, even when the client resends or a consumer is redelivered | Unique index on `(conversation_id, client_msg_id)`; E11000 on insert is treated as success | Replay the same message twice and expect one document and two successful responses |

---

## 6. Tests to write

- **Mongo integration** on testcontainers (a single-member replica set is enough for transactions in CI): schema and index creation, the transaction commit/abort test, a test that fails on standalone, TTL and partial-index behaviour (the test checks the index definition, since TTL deletion runs on a background schedule), participants-only access, `client_msg_id` dedup.
- **Write-concern test** (local or nightly, not on every PR): the primary-kill script runs as a test with the loss count asserted (0 for majority).
- **Migration tests:** dual-write consumer idempotency (the same event twice gives one document), the backfill diff tool reports 0 on a seeded fixture and non-zero after a planted gap.
- **Timescale integration** on testcontainers with the `-ha` image: hypertable and CAGG creation, the **CAGG-vs-raw** test, consumer idempotency, rebuild from Postgres, a retention test, and a licence check test that fails on an `-oss` image.
- **Velocity-rule tests:** each rule fires on its worldgen pattern, and an attempt 20 seconds old is counted (real-time aggregation).
- **Model tests:** leakage, feature parity, artifact hash, deterministic training on a small fixture (fixed seed gives the same metrics), no-enforcement, scoring timeout, and an import test that `atlas_fraud_features` imports without Django installed.
- **Benchmark scripts** are not tests, but they are committed and reproducible from `bench/`.

---

## 7. CI changes

| Job | What it gates |
|---|---|
| `store-integration` (matrix: `mongo`, `timescale`) with path filters | Runs only when `conversations`, `analytics`, `payments` fraud code, the consumers or the store configs change. Runs the Mongo and Timescale testcontainer suites, including CAGG-vs-raw and the licence check. |
| `model-tests` | Leakage, parity, artifact-hash, deterministic-training and no-enforcement tests on every PR that touches `libs/atlas-fraud-features`, the trainer or `payments`. |
| Nightly (optional, only if runners allow) | The write-concern failover script and the rebuild-from-Postgres check. |

Keep the Stage 05 path filters honest: a change to `libs/atlas-fraud-features` must trigger `model-tests`, and later the tests of every service that installs the wheel, even though the code lives outside `payments`. See [testing and CI](testing-and-ci.md).

---

## 8. ADRs and documents

**ADR-024 — JSONB vs Mongo, for both workloads**

- *Questions:* Which store holds catalog attributes, and which holds conversations? What was predicted, what was measured, and why do the two workloads get opposite verdicts?
- *Numbers:* the full attribute matrix (F1–F10, W1–W4, sizes); the conversations table (Postgres partitions vs Mongo message-per-document vs bucket); the write-concern table; the migration diff.
- *Must say honestly:* Postgres partitions were adequate up to the measured scale. What tipped conversations to Mongo is a document-shaped, append-only, TTL workload accessed per conversation, which will need to scale out in Stage 12. Removing a month of partitions (detach, then `DROP TABLE`) was cheaper than TTL deletes, as long as you avoided the parent-table lock you measured.
- *Counter-argument to address:* "One more database is one more thing to back up, secure, upgrade and page on. Keep chat in Postgres." Answer it with the operational cost you actually saw. The degrade list in [schedule and cuts](schedule-and-cuts.md) §7 keeps exactly that option alive (the item "conversations stay in Postgres JSONB").
- *Reversal conditions* for both verdicts.

**ADR-025 — Timescale vs matview vs Prometheus**

- *Questions:* Where do velocity features and vendor sales series live? Why not a Postgres matview in `market`? Why not Prometheus?
- *Numbers:* velocity v0 vs CAGG latency and correctness; the matview-vs-CAGG table; the compression ratio; retention settings.
- *Counter-argument:* "Prometheus already stores time series." Hint: argue from the Stage 06 label-cardinality rule applied to a card fingerprint or merchant label, and from what your rebuild test needs that Prometheus samples cannot give you (`docs/evidence/s07/velocity-cagg.csv`, the rebuild-from-Postgres test). Also record the `-oss` trap and the licence facts.

**ADR-026 — Fraud v1**

- *Questions:* What does the model predict, from which features, under what label assumptions? Why shadow mode? What does a rule hit do in Stage 07?
- *Numbers:* the model table (rules only vs logistic regression, plus the tree model if you did the stretch), the random-vs-time split difference, the before/after-leakage-fix metrics, the in-process score p95, the image-size increase.
- *Counter-argument:* "Unsupervised anomaly detection (the P4 and P9 extensions) needs no labels. Why a supervised model on synthetic labels?" Answer it honestly, including what synthetic labels cannot prove. The IsolationForest stretch item gives you numbers for this answer.

**ADR-003 update** (licences): TimescaleDB TSL vs Apache-2 split, the `-oss` tags; MongoDB server SSPL (fine for internal use).

**Also:** the model card, `docs/evidence/s07/` (all tables above), `docs/sd/sd8-storage.md`.

---

## 9. System design session

**SD8 — Design a chat system, storage half** ([../../system-design-problems.md](../../system-design-problems.md)). Built in Atlas: the storage and ordering part now, the realtime part in [Stage 11](stage-11-realtime-edge-graphql.md). See the [system design map](system-design-map.md).

Cover, using your own numbers:

1. Data model: conversation and message documents, the bucket-vs-document measurement, why not one growing array.
2. Ordering: a per-conversation `seq` allocated in the transaction, and client dedup by `client_msg_id` (the same idempotent-consumer discipline, applied to messages).
3. Durability: what `w:1` lost in your experiment and what majority cost.
4. Retention and evidence: TTL with a partial index for disputes vs detaching and dropping partitions.
5. Scale-out: which shard key you would pick and why. Which shard keys does your `(conversation_id, client_msg_id)` unique index still allow? Do not decide yet: Stage 12 tries several keys under load.
6. Offline recipients: store-and-forward, then a push through the Stage 04 bot sender.

**SD19 tie-in** (built-lite across S6 and S7): when asked "design a metrics pipeline", your Timescale CAGGs and compression ratio are the time-series half of the answer, and ClickHouse is the named alternative for wide analytical scans.

---

## 10. Interview questions this stage lets you answer

1. When is Mongo the right choice, and why did your catalog attributes stay in JSONB?
2. What does `w:1` lose when the primary dies? Show me the numbers.
3. Why do MongoDB transactions need a replica set?
4. Continuous aggregate or materialized view? What did the refresh cost look like as history grew?
5. Why does the `-oss` image matter?
6. What is point-in-time correctness, and how did you test it?
7. Why PR-AUC and not ROC-AUC or accuracy?
8. When is JSONB the right column type, and when is it a design smell? (P7 D109–D114)
9. Why did you model messages as separate documents (or buckets) and not as an array inside the conversation?
10. How do you enforce "participants only" in a database without row-level security?
11. What is training-serving skew, and what did you do about it?
12. Why run the model in shadow mode, and what would you need before enforcing it? (P9 Wk26)
13. How did you migrate a live table to another database without losing messages?
14. Why is Prometheus the wrong place for per-card velocity counts?

---

## 11. Common mistakes to watch for

1. **An unfair benchmark:** default Mongo against a tuned Postgres (or the reverse), warm cache on one side only, or no written protocol. The result is then just your opinion with numbers attached.
2. **Writing the prediction after seeing the result.** It is no longer a prediction.
3. **Believing a replica set means no data loss.** Only majority-acknowledged writes survive an election, and only reads at a matching read concern are guaranteed to see them.
4. **Unbounded arrays** in a document (all messages inside the conversation): the 16 MB limit and ever-growing rewrites.
5. **Queries without a checked plan.** A `COLLSCAN` in `explain` on a hot path is the Mongo version of a Postgres seq scan.
6. **Using Motor** in new code (end of life 2026-05-14), or opening a new client per request instead of one per process.
7. **The `-oss` image**, or not knowing which features are TSL. It only fails once you create the first continuous aggregate or policy.
8. **Treating Timescale as a source of truth**, with no rebuild path from Postgres.
9. **Retention and refresh windows that overlap**, silently emptying old aggregates.
10. **Random train/test splits, features read from finished buckets, or labels used before they were available.** All three flatter the model. The P4/P9 lesson "anomalous is not fraudulent" still applies: a score is a signal, not a verdict.

---

## 12. How real companies differ

- **Chat at very large scale** usually ends up in a wide-column store. Discord's public engineering story went MongoDB → Cassandra → ScyllaDB. Many companies keep chat in Postgres far longer than this stage does. Atlas uses Mongo because the requirements ask for it where it fits, and ADR-024 records that Postgres was adequate at the measured scale. Being able to say that is the interview skill.
- **Managed services** (MongoDB Atlas, TigerData's cloud) replace self-hosted replica sets and version pinning. You run them yourself here to see elections, rollbacks and licence editions, which managed services hide.
- **Analytics** at larger companies goes to a warehouse or a columnar store (BigQuery, ClickHouse, Druid) fed by CDC. Season 2 builds the warehouse path ([Season 2](season-2.md), 2A and 2E). Timescale is the right step here because it keeps SQL, the Postgres operational skills you already have, and one fewer query language.
- **Fraud** teams use streaming feature pipelines (Kafka/Flink), feature stores, vendor scoring (Stripe Radar-style), chargeback labels with long delays, and human review queues. The learning version keeps one feature function, point-in-time discipline and shadow mode. Those are the parts that separate a real model from a demo, and they carry over to any stack.
- **Model registries** (MLflow) track versions. Here, a sha256 and a model card in the `atlas-models` bucket do the same job at the smallest possible cost; MLflow arrives in Season 2 (2D).

---

## 13. Deliberately not doing

| Item | Why not now | When it arrives |
|---|---|---|
| Mongo sharding | You first need a working replica set and a measured access pattern to choose a shard key | [Stage 12](stage-12-data-at-scale-fraud.md) (shard-key choice against the S7 unique index, then `reshardCollection` under writes) |
| A tree model (HistGradientBoosting), precision@k, calibration | The first model should be one you can explain line by line; the ramp is short | Stretch (§14); [Season 2](season-2.md), 2C |
| Change streams | Named only. The outbox consumer already feeds Mongo; a second event path would duplicate it | Named in ADR-024 |
| ClickHouse | Part of the SD19 answer; one analytical store at a time | Whiteboard only |
| MLflow | The artifact + sha256 + model card covers Season 1 | [Season 2](season-2.md), 2D |
| Enforcing fraud decisions | Synthetic labels and an untuned threshold; shadow first | Stage 12 (enforce via a flag, with a rules fallback) |
| Redis 1m/10m velocity windows | CAGGs cover Stage 07; Redis windows are for the served model's latency budget | Stage 12 |
| Moving catalog attributes to Mongo | The benchmark predicts (and, once measured, should confirm) that JSONB wins | Only if an ADR-024 reversal condition is met |
| Kafka/CDC to feed `tsdb` | The polling outbox relay is enough here | Season 2, 2E |

---

## 14. Stretch

Only if the must tier closes early. Total 5 h.

- **Tree model and precision@k [1.5 h]:** train `HistGradientBoostingClassifier` (trees, which handle feature interactions and missing values natively) on the same time split, and add two columns to the model table: **precision@k**, where *k* is the daily review capacity (for example, ops can review 50 attempts a day), and the tree model's row. Does the better PR-AUC survive the in-process p95 and artifact-size columns?
- **Calibration curve [1 h]:** are the predicted probabilities honest? Compare the models and note what a cost-based threshold assumes about calibration.
- **IsolationForest baseline [1 h]** (P4 lineage, [../python/04-wareflow.md](../python/04-wareflow.md) §19): unsupervised scores on the same time split. How many planted frauds does it catch at the same review capacity?
- **Bucket pattern with pre-aggregated counters [1 h]:** keep per-bucket message counts and last-message fields in the bucket document, and measure the inbox query against the message-per-document design.
- **Benchmark rows F9 and W4 [0.5 h]:** the category-subtree filter (design the tree on the Mongo side: parent references, an ancestors array or a materialized path) and the 10k bulk import.

---

## 15. Definition of done

- [ ] `compat.txt` records Mongo and Timescale versions and the Timescale licence.
- [ ] ML ramp: the five `sandbox/ml-ramp/` exercises run and `docs/learning/ml-ramp.md` is written.
- [ ] Attribute benchmark: prediction committed before the first run; matrix F1–F8, F10, W1–W3 and sizes filled in under ADR-002.
- [ ] Conversations in Postgres measured (writes/s, per-conversation p95, inbox p95, DELETE vs detach-and-drop, and the parent-table lock of plain vs `CONCURRENTLY` detach with a long SELECT running).
- [ ] Mongo 3-node replica set; schema comparison measured; every index has a committed `explain('executionStats')`.
- [ ] The transaction test fails on standalone and passes on the replica set.
- [ ] Write-concern table filled in against a committed prediction and a recorded window length: `w:1` loss counted, majority loses 0; rollback files inspected.
- [ ] JSONB → Mongo migration: dual-write through `market.chat-mongo-sync`, backfill, diff = 0, reads switched, the temporary queue deleted.
- [ ] Participants-only test passes against Mongo; the Admin evidence view works and logs reads.
- [ ] `-oss` trap reproduced and documented; ADR-003 updated; `compat_check.sh` prints the licence.
- [ ] Three hypertables fed by idempotent outbox consumers; rebuild-from-Postgres test passes.
- [ ] Velocity rules read `velocity_1m/1h/24h` with real-time aggregation; latency and correctness recorded.
- [ ] Vendor sales: raw → matview → CAGG table filled; compression ratio and retention recorded; CAGG-vs-raw test passes.
- [ ] Fraud v1: worldgen patterns, `libs/atlas-fraud-features` imported by the trainer and `payments` (no Django import), leakage and parity tests, the rules-vs-logistic-regression table, artifact with sha256 in `atlas-models`, model card.
- [ ] Shadow scores and `model_version` stored on every attempt; the no-enforcement and scoring-timeout tests pass.
- [ ] CI: `store-integration` matrix and `model-tests` green.
- [ ] ADR-024, ADR-025 and ADR-026 committed with numbers.
- [ ] SD8 storage-half notes in `docs/sd/`.
- [ ] Postmortem paragraph: what surprised you, what you would measure differently.
- [ ] 2 STAR stories in `docs/star/`: **the writes `w:1` lost**; **the `-oss` trap**.
- [ ] Git tag `v0.7`.

---

## 16. If you get stuck

**Benchmark (4.1a)**
- Is each side using its best index? Read both plans before you trust any number.
- Is your difference bigger than the min–max spread? If not, the ADR-002 noise rule says "no difference".
- Reread P7 D109–D114 ([../python/07-fleettrack.md](../python/07-fleettrack.md)) on when JSONB fits, and P8 D121–D126 ([../python/08-docuvault.md](../python/08-docuvault.md)) on benchmarking with a fixed query set.

**Conversations in Postgres (4.1b)**
- Who creates next month's partition, and what happens if nobody does? (WareFlow D67–D71, [../python/04-wareflow.md](../python/04-wareflow.md).)
- Why does a 404 leak less than a 403 for a conversation you may not see?
- Chat queries froze while you removed a partition. Which lock did your statement queue for on the parent, and who was holding a conflicting one? (The Stage 06 lock-queue drill, again.)

**ML ramp (4.0)**
- Your time split and random split score the same. Did you add the drift? On data that never changes over time, the two splits agree, which is exactly why real fraud data, which does change, needs the time split.
- Everything scores 0.99 accuracy. Count the positives in your test set. What does a model that always says "not fraud" score?

**Mongo (4.1c)**
- Your transaction fails with a topology error. Is the server a replica set? Is the session's read preference primary?
- Your `w:1` run lost nothing. Did acknowledgements happen *while* the primary was cut off from its secondaries? If replication kept up, there was no window. Check what your load script could still reach during step 2, and compare the acknowledged-id file's timestamps with the moment you isolated the primary.
- Your index is not used. Compare the query's filter and sort order with the index's key order (the same leftmost-prefix thinking as a Postgres composite index).

**Timescale (4.2)**
- The CAGG ignores the newest rows. Check `materialized_only` and your refresh policy's end offset.
- Aggregates disappeared after retention ran. Compare the refresh window with the retention window.
- Consumers write duplicates after a redelivery. Where does your dedup record commit? It must be the same database and the same transaction as the hypertable row.
- Reread P2 D37–D39 ([../python/02-quickserve-pos.md](../python/02-quickserve-pos.md)) for the matview baseline and its "equals the live query" test.

**Fraud v1 (4.3)**
- The model looks too good. Ask which feature could have seen the future, and run the leakage test on it first.
- PR-AUC is low but ROC-AUC is high. That is normal on imbalanced data; reread phase-9 D261–D263 ([../../phase-9-ml-zoomcamp.md](../../phase-9-ml-zoomcamp.md)) and your ramp notes.
- You cannot beat the rules. That is a valid result: record it, keep shadow mode, and let ADR-026 say so. Reread P9 Wk26 ([../python/09-payflow.md](../python/09-payflow.md) §21) on why a score is a signal first.
- `payments` cannot import the feature library in its image. Is `atlas-fraud-features` a built wheel pinned in market's dependencies, like `atlas-common`, or a path install that only works on your laptop?

<details>
<summary>Check your prediction (open only after you committed yours and ran the exercise)</summary>

- **4.1b, removing a partition.** A plain `DETACH PARTITION`, and a direct `DROP TABLE` on a partition, need ACCESS EXCLUSIVE on the parent table. Behind your long SELECT, the statement waits, and every new chat query queues behind it: the Stage 06 lock queue. `DETACH PARTITION … CONCURRENTLY` takes only SHARE UPDATE EXCLUSIVE on the parent, so reads and writes continue (it still waits for the long SELECT before it completes); you then `DROP TABLE` the detached table, which no chat query touches any more. The clash: the PG17 docs say `CONCURRENTLY` cannot run inside a transaction block and is **not allowed if the partitioned table has a DEFAULT partition**, and your Stage 04 pattern added one. Either give up the DEFAULT partition for messages (and make sure future partitions always exist, with an alert if they do not), or keep it and run the plain detach with a short `lock_timeout` and retries, the Stage 06 technique. Both are defensible; ADR-024 records which one you chose.
- **4.1c, write concerns.** Under `w:1`, the writes acknowledged during the window are lost: a non-zero number, bounded by the window length and your write rate. The old primary saves them in its rollback directory when it rejoins. Under `w:"majority"`, the lost count is 0. You pay in write latency, and during the isolation and the election the writes time out or fail instead of being acknowledged.
- **4.2 step 5, refresh cost.** `REFRESH … CONCURRENTLY` recomputes the whole query and diffs it against the old contents, so its cost grows with the **total** history. A CAGG refresh only recomputes the buckets whose raw data changed, so its cost grows with the **changed** data and it pulls ahead as history grows. At small sizes the matview is often just as good.
- **4.3, splits and leakage.** The random split usually scores higher than the time split, because it lets the model train on attempts from the same bursts and days it is tested on. Fixing the leakage usually makes the model look **worse**. That lower number is the honest one, and the one ADR-026 reports.

</details>

**Running out of time?** Stretch goes first. After that, the degrade list in [schedule and cuts](schedule-and-cuts.md) §7 has two items for this stage, applied in its global order. Both are **partial**:

- *The Timescale partial degrade* (about 1.5 h): drop the vendor-sales CAGG and the raw → matview → CAGG comparison (step 5). **Keep** compression (with its ratio recorded) and retention on `fraud_features.events`, and keep the velocity CAGGs. Compression and retention are named in the requirements, so they are never cut completely.
- *Conversations stay in Postgres JSONB* (about 3 h): Mongo then holds only the AI transcripts (Stage 08) and the benchmark, and the replica set, write-concern experiment and transactions run on those.

The Mongo write-concern lesson and the leakage-safe fraud model are what interviewers remember. Protect those. If a block on the never-cut spine overruns, the date moves; nothing is deferred silently.
