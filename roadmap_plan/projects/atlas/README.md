# Atlas — one project, two seasons, from middle to middle+

| | |
|---|---|
| **What you build** | **AtlasMarket**, a multi-vendor marketplace (Django monolith), and **AtlasPay**, the platform's own Stripe-like payment operator, with Payme and Click adapters proven against **provider-sim**, a simulator that speaks each provider's real protocol. Plus a Telegram bot. All of it in one monorepo, `atlas/`. |
| **How it grows** | One layered Django monolith (W1) → modular monolith → first split → strangler-fig extraction → Kubernetes → realtime edge → sharded ledger (W53). The end state is 9 production deployables plus provider-sim. |
| **Season 1** | 53 weeks (about 12 months), backend + AI integration. **600 h must + 66 h stretch + 36 h buffers = 702 h** (≈ 13.2 h/week on average). Must + buffers = 636 h = 53 × 12, so the must tier fills a 12 h/week floor exactly. |
| **Season 2** | About 30–34 weeks (≈ 400–460 h at 13.5 h/week) of data science, ML, MLOps and data engineering on the same data. The re-estimate and the weeks per stage are in [season-2.md](season-2.md). |
| **What it replaces** | The ten separate Track A projects ([P1 StockPilot](../python/01-stockpilot.md) … [P10 AtlasMarket](../python/10-atlasmarket.md)) and the three SD-build projects 26–28 in [phase-6-capstone.md](../../phase-6-capstone.md). They stay untouched and are cited as theory reading. |
| **The rule** | This is a **specification, not a solution**. You write every line of code. The mentor explains, asks, reviews and points you to reading; it never hands you the implementation. |

> **What this README is for.** It is the entry point: it explains what Atlas is, why one evolving system teaches more than ten fresh ones, how the architecture changes stage by stage and why, and which decisions are fixed for the whole season. Read it once in full before [Stage 00](stage-00-bootstrap.md). Come back to the decision tables (§7) whenever a stage file says "see E3" or "see E10".

---

## Contents

1. [What Atlas is](#1-what-atlas-is)
2. [Why one project replaces ten, and what is kept from them](#2-why-one-project-replaces-ten-and-what-is-kept-from-them)
3. [The two seasons](#3-the-two-seasons)
4. [The thesis](#4-the-thesis)
5. [How the architecture evolves](#5-how-the-architecture-evolves)
6. [The Season 1 stage plan](#6-the-season-1-stage-plan)
7. [Decision tables (E1–E8, E10)](#7-decision-tables)
8. [Conventions](#8-conventions)
9. [How to use the old P1–P10 specs and phase files](#9-how-to-use-the-old-p1p10-specs-and-phase-files)
10. [Working with the mentor](#10-working-with-the-mentor)
11. [Files in this folder](#11-files-in-this-folder)

---

## 1. What Atlas is

Atlas is **one product**. You build it in **one monorepo** (a single git repository that holds every service and shared library), on **one seeded dataset**, over **two seasons**.

**AtlasMarket** (the `market` service) is a *multi-vendor marketplace*: many independent vendors list products, and customers buy from several vendors in one checkout. It covers:
- a catalog of 1M products;
- inventory;
- a cart and a checkout that splits one order into one *vendor group* per vendor;
- fulfillment per vendor group, promotions, search and reviews;
- buyer↔vendor conversations and notifications;
- vendor analytics;
- a back office for ops: KYC review, moderation, refund approval and dispute evidence.

It is a Django 5.2 LTS + DRF *modular monolith*, meaning one deployable whose modules have enforced boundaries.

**AtlasPay** is the platform's own *payment operator*: the company that takes the customer's money, holds it on a ledger and pays vendors out. It is modelled on Stripe:
- a *PaymentIntent* lifecycle, the state machine of one attempt to collect one amount;
- an `Idempotency-Key` on every POST, so a retried request never charges twice;
- merchant API keys (`sk_…`) and signed webhooks;
- Connect-style splits, meaning one charge is split into transfers to the vendors minus a platform fee;
- refunds, payouts, reconciliation, and a double-entry ledger with balance transactions.

AtlasPay starts in S5 as the `payments` module inside market, built on a framework-free core library (`libs/atlaspay-domain`). In S9 it is extracted into its own `atlaspay` service on its own host, `pay.<domain>`. **From S9, market pays exactly the way an outside merchant would:** public REST, an `Idempotency-Key` on every POST, an `sk_` secret key sent as `Authorization: Bearer sk_…`, and signed webhooks. Market learns payment, refund and payout outcomes only from those webhooks; its internal S5–S8 event queue is deleted in the S9 cutover. Market is simply merchant #1.

**Payme and Click** are the two main Uzbek payment providers. AtlasPay talks to them through *provider adapters*. There is no real merchant contract, so the adapters are proven against **provider-sim**. This is a FastAPI service with its own database that follows each provider's real protocol:
- Payme's JSON-RPC 2.0 callbacks with HTTP 200 on every error;
- Click's form-encoded Prepare/Complete with MD5 signatures;
- the retries, timeouts and duplicate deliveries both providers really produce.

Facts that could not be confirmed from the providers' documentation are marked **[U]** and become simulator settings instead of hard-coded behaviour.

**The bot** (`services/bot`, aiogram 3) is a Telegram client that arrives in S3. It handles account linking, order tracking, vendor notifications with a "mark shipped" button (S4), the AI assistant (S8) and AtlasPay payment links (S9). It never touches another service's database and has no business logic of its own.

**The world generator** (`libs/atlas-worldgen`, from S0) builds the data both seasons use, with a seeded random-number generator:
- Pareto-sized vendors, a category tree, 1M products and users;
- orders with cart abandonment;
- payment attempts, including synthetic fraud patterns.

It has two modes. `history` writes months of COPY-ready rows; `traffic` drives locust load. Every benchmark records the generator's version and seed, so any number can be reproduced. Season 2 then analyses those months of seasonal, cohort-structured history.

**The shape at the end of Season 1:** 9 production deployables (market, atlaspay, auth, ai, edge, bot, inventory, ledger, fraud) plus provider-sim. Workers, relays, consumers and senders are *process types* of the same images, not separate services. If you apply the whole degrade list ([schedule-and-cuts.md](schedule-and-cuts.md)), you finish with 7 production deployables plus provider-sim. That is still a complete, defensible system.

---

## 2. Why one project replaces ten, and what is kept from them

### 2.1 Why

The old Track A had ten projects, each in a new domain and a new repository. It taught a great deal, but it had five structural problems that one evolving system fixes.

1. **Scaffolding tax.** Every project rebuilt settings, auth, Docker, CI and deploy. On 12–15 h a week, that setup time is time not spent on the lesson.
2. **Lessons that never meet.** FleetTrack's outbox never had to coexist with PayFlow's idempotency store and WareFlow's locks in the same checkout. Interviewers probe exactly those interactions, for example "what happens if the payment callback arrives while the order row is locked?". Only a single system forces you to answer.
3. **No honest "why did you split?"** The old projects started at their target architecture. CarePoint split auth-service on day one, on purpose, to feel the cost. In Atlas, every service leaves the monolith only after a measured problem and a split-gate run (§4). The ADR then records the numbers. That is the answer a middle+ interview expects.
4. **Shallow history.** One repository with tags v0.0 … v1.0, 43 ADRs (ADR-000 to ADR-042) with numbers, and a committed evidence folder shows growth. Ten small repos show only starts.
5. **Data for Season 2.** ML and data engineering need months of realistic, connected history: orders, payments, a ledger, chat. One world generator feeding one product produces it. Ten unrelated schemas do not.

### 2.2 What is kept

Nothing important is thrown away. The domains change; the lessons are kept, and so are their *pain-first* moments, where you build the broken version first, watch it fail and record the numbers. The table shows where each old project's lesson lands in Atlas.

| Old project (days) | The lesson that survives | Where it lands in Atlas |
|---|---|---|
| [P1 StockPilot](../python/01-stockpilot.md) (D1–D24) | The router never touches the ORM. Oversell is impossible under concurrency: exactly one 201 and one clean 409. `Repository[T]` Protocols, a multi-stage non-root image, and async pitfalls such as a password hash blocking the event loop. | S0 image; S1 layering and ports; S2 oversell; S9 async pitfalls (MissingGreenlet, `expire_on_commit`, argon2 on the loop); S10 flash sale |
| [P2 QuickServe](../python/02-quickserve-pos.md) (D25–D39) | Django chosen because the product is admin-heavy, keeping the service layer. Cache-aside where the invalidation audit matters more than the cache. Money in integer minor units with fixed/percent/capped discounts. simplejwt. | S0 Django orientation; S1 Django ramp, money and identity v1; S2 pricing; S3 cache and invalidation audit |
| [P3 PeopleOps](../python/03-peopleops.md) (D40–D53) | Feel a synchronous email wreck an endpoint, then fix it with Celery. Relationship-based permissions. Beat jobs fire twice, so guard them with a constraint. | S1 relationship permissions; S2 synchronous email left painful; S4 Celery, Beat and run keys |
| [P4 WareFlow](../python/04-wareflow.md) (D55–D78) | Transactions and locking as the whole point: MVCC, isolation levels, write skew, deadlock and timeouts. Partitioning. A business process spanning several transactions joined by events. The outbox gap, watched but not fixed. | S2 races and isolation; S4 events and outbox; S5 hold vs provider window |
| [P5 CarePoint](../python/05-carepoint.md) (D79–D90) | Let the database enforce what must never happen (EXCLUDE). The auth project: RS256, JWKS, rotation and OIDC. What a service split really costs. Presigned object storage. | S1 EXCLUDE on commission windows and KYC presigned URLs; S3 auth hardening; S9 the auth service; S11 frontend |
| [P6 LedgerBase](../python/06-ledgerbase.md) (D91–D108) | Build the float version first and watch the trial balance fail. Double-entry with a deferrable constraint trigger, window functions and matviews. The first synchronous service-to-service write and its resilience. Zero-downtime deploys, observability, API versioning. | S5 ledger; S6 ship and operate; S9 versioning and resilience |
| [P7 FleetTrack](../python/07-fleettrack.md) (D109–D120) | The outbox closes the dual-write gap. At-least-once delivery means idempotent consumers and a lag alert. CQRS, where the same technique can get the opposite verdict. Saga. WS/SSE compared with polling across two replicas. | S4 outbox and CQRS; S9 saga; S11 realtime |
| [P8 DocuVault](../python/08-docuvault.md) (D121–D132) | A derived index is never the source of truth; prove it by rebuilding. Go LIKE → pg_trgm → FTS → search engine only when a query fails. Kubernetes only once Compose stops coping. Postgres *operated*, not just queried. Consistent hashing, measured. | S4 search; S6 Postgres operations; S9 webhook hash ring; S10 Kubernetes and PgBouncer |
| [P9 PayFlow](../python/09-payflow.md) (D145–D156) | Idempotency-Key plus request hash stored durably in Postgres ("the most important why-not": not Redis). Vault, a threat model, SLOs, a live drill and a verified PITR restore. A per-merchant Lua token bucket. A gRPC ledger call measured against REST. | S2 idempotency; S3 limiter; S5 AtlasPay; S6 operations; S9 Vault and keys; S12 gRPC ledger |
| [P10 AtlasMarket](../python/10-atlasmarket.md) (D157–D168) | One payment against many vendor groups, kept consistent by a local transaction + outbox + idempotency + reconciliation instead of 2PC. Vendor isolation enforced twice (query filter + RLS). Bulkhead, hash-bucket flags with a canary, a GraphQL BFF with DataLoader (51 → 2 calls). Scope creep beaten with a deferred list. | The whole domain; S2 RLS and vendor groups; S5 Connect; S8 flags; S9 bulkhead; S11 GraphQL; `docs/deferred.md` in every stage |
| Projects 26–28 ([phase-6-capstone.md](../../phase-6-capstone.md), D169–D178) | URL shortener (Proj26 D169–D170); a rate limiter proven correct across 3 instances (Proj27 D171–D173); a job scheduler with leader-only dispatch and exactly-once ticks (Proj28 D175–D178) | S9 AtlasPay payment links `/l/{code}`; S3 limiter path; S10 Kubernetes Lease |

### 2.3 What changes

- **Domains.** The inventory shop, POS, HR, warehouse, clinic, accounting office, fleet and document vault are gone. Their techniques are applied to one marketplace plus its payment operator.
- **Splits are earned, not pre-planned.** The old projects split on purpose early (CarePoint's auth-service, LedgerBase's invoicing → ledger). Atlas stays a monolith until S8, and every extraction ADR carries split-gate numbers.
- **Search engine only on failure.** DocuVault's Elasticsearch becomes OpenSearch 3.x, adopted only if a fixed judged set of 40 queries fails on Postgres FTS + trigram + transliteration (ADR-016).
- **Leader election.** Project 28's hand-built Raft cluster becomes a Kubernetes Lease with UNIQUE run keys as the backstop. The exactly-once lesson is the same.
- **Real payment protocols.** PayFlow's generic provider becomes Payme and Click, as faithfully as their public documentation allows.
- **Polyglot only after Postgres.** MongoDB and TimescaleDB arrive in S7, after a Postgres version of the same workload has been measured.
- **Daily DSA/SQL problems become a weekly drill hour:** one SQL problem on the Atlas schema, or one DSA problem from [dsa-problems.md](../../dsa-problems.md) / [sql-problems.md](../../sql-problems.md), plus the week's SD or interview questions.

---

## 3. The two seasons

**Season 1: backend + AI integration** (53 weeks, stages S0–S12 plus buffers B1, B2 and B3). It takes you from a skeleton to 9 production deployables on Kubernetes. It includes two portfolio slices deployed early:
- **slice 1 at W28** (v0.6): the marketplace deployed, observed and taking payments;
- **slice 2 at W36** (v0.8): the AI features.

Job applications start in B2 (W37). Season 1 is specified in full, one file per stage.

**Season 2: ML, data science, MLOps and data engineering** (about 30–34 weeks, ≈ 400–460 h at 13.5 h/week, re-estimated from the Track B phase files minus what Season 1 already covers). It works on the same Atlas data and systems and maps onto the existing Track B phase files. It is outlined at stage level in [season-2.md](season-2.md), which also gives the weeks per stage:

| Stage | Atlas data / system used | Phase files |
|---|---|---|
| 2A Warehouse + batch DE | Airflow incremental extraction (updated_at watermark) from the market, atlaspay and ledger replicas → BigQuery (or DuckDB/ClickHouse locally) → dbt marts `fct_orders`, `fct_payments`, `fct_ledger`, `dim_vendor`, `fct_vendor_revenue`, with a reconciliation test against the ledger trial balance | [phase-11](../../phase-11-data-engineering-zoomcamp.md) W56–58 (D331–D348), D365 |
| 2B DS + statistics | EDA on 13 months of worldgen history (pandas/Polars in notebooks, plotly/matplotlib, scipy.stats/statsmodels; a "dirty data" worldgen mode). A/B analysis of the S8 prompt-flag and checkout cohorts, stratified by rollout phase plus a worldgen fixed-allocation window: sample-ratio check, confidence intervals by hand, power, peeking. Vendor cohorts. Math under `.fit()`. | [phase-9](../../phase-9-ml-zoomcamp.md) W42 (D247–D252), [phase-7](../../phase-7-llm-zoomcamp.md) D197 |
| 2C ML | Fraud deepening (imbalance, calibration, cost curves, label delay); a demand forecast per vendor SKU against a naive baseline; recommendations (co-purchase, kNN on S8 embeddings); raw K8s vs KServe | [phase-9](../../phase-9-ml-zoomcamp.md) W43–49 (D253–D294) |
| 2D MLOps | MLflow registry for fraud, forecast and recommendations; Prefect retraining with data validation; Evidently drift on Timescale features → Prometheus; a CI gate against Production; shadow/canary via the Atlas flags; fail closed if the registry is unreachable | [phase-10](../../phase-10-mlops-zoomcamp.md) W50–55 (D295–D330) |
| 2E Streaming + CDC | Debezium outbox event router → Kafka, compared with the S4 polling relay on lag and DB load; streaming fraud features vs Timescale CAGGs; Spark over ledger history; ksqlDB | [phase-11](../../phase-11-data-engineering-zoomcamp.md) W59–61 (D349–D366); adds CDC, which phase-11 left out |
| 2F Electives + capstone | Reranking and query rewriting, judge calibration, an AI PR-review bot, a guarded agent | [phase-7](../../phase-7-llm-zoomcamp.md) D199–D209, [phase-8](../../phase-8-ai-devtools-zoomcamp.md) D229–D240 |

Season 1 prepares for Season 2 on purpose:
- the world generator runs from S0;
- the feature flags in S8 create real A/B cohorts;
- the fraud model in S7 uses one feature function (`libs/atlas-fraud-features`) for training and serving;
- Kafka, CDC, MLflow, retraining and drift detection are explicitly *not* done in Season 1 so that Season 2 has something real to add.

---

## 4. The thesis

**1. Nothing leaves the monolith until the split gate has run.**

The *split gate* is a scripted, reproducible measurement (`bench/split-gate`, protocol in ADR-023). It is built in S6 and re-run before every extraction (ported to kind in S10; see §8.6). It runs one fixed 10-minute scenario:
- worldgen traffic, with the catalog at about 200 rps scaled to the container limits;
- plus a provider-sim callback storm with duplicates;
- plus one deploy with an expand migration in the middle.

It records callback p99, the percentage of Payme -32400/timeouts and Click errors, payment p99 against catalog load, checkout p95, DB pool saturation and the secrets each process holds.

Its result goes into the extraction ADR. **If the numbers do not hurt, the ADR must say so**, and argue only from *blast radius* (how much breaks when one part fails) or *security scope* (which process can see which secrets). Otherwise the split does not happen. This one rule turns "we moved to microservices" into "we moved *this* out, *because of this number*, and here is what would make us move it back".

**2. Services leave for a reason the monolith cannot fix cheaply.**

The services that leave use FastAPI, grpc.aio or aiogram. Each one leaves because it has at least one of these properties:
- it is async and I/O-heavy (ai streams LLM tokens; atlaspay does heavy outbound provider I/O);
- it holds long-lived connections (edge holds thousands of sockets);
- it is a trust boundary (auth mints tokens; atlaspay holds provider secrets; ai holds LLM keys and sees PII);
- it has a natural shard key (ledger, by connected account).

The back office stays in Django: KYC, moderation, refund approval, dispute evidence and ops tooling. That is roughly half of a marketplace, and Django Admin is the cheapest way to build it well.

**3. The priority lens is job readiness per hour.**

1. **Correctness first.** The correctness interviewers probe comes first: races, money, idempotency and the outbox. Each one is shown failing before it is fixed (S1–S5).
2. **Two portfolio slices, deployed early.** Slice 1 at W28 is the marketplace deployed, observed and taking payments. Slice 2 at W36 adds the AI features. From W37 you can apply for jobs with something real to show.
3. **Only then, architecture.** Extractions, Kubernetes, gRPC, realtime, GraphQL, sharding and the fraud model come last (S8–S12), and each one is forced by a measured problem.

**4. The budget is honest.**
- The must tier is **600 h**, sized to the 12 h/week floor: every stage's must hours are exactly 12 × its weeks.
- Stretch adds **66 h** and the three buffer weeks add **36 h**, for **702 h over 53 weeks (≈ 13.2 h/week)**.
- The block budgets were estimated bottom-up for a learner who has done about five days of FastAPI and has not yet used Django, aiogram, React, Kubernetes, Mongo or ML. The stages that introduce Django (S0), aiogram (S3), ML (S7) and React/TypeScript (S11) include explicit ramp blocks. They are still estimates. You log actual hours per block from S0; at B1 you compute actual/budget and re-plan the rest of the season with that ratio. If a block on the never-cut spine overruns, the date moves. Spine work is never silently deferred.
- All numbers come from one benchmark protocol (ADR-002). A number measured differently is not comparable, and "faster" without a protocol is an opinion.

---

## 5. How the architecture evolves

### 5.1 The evolution table

Read each row as: "at the end of this stage, this is what runs, and this is the measured problem that forces the next stage." The last column is the engine of the whole plan. Every next step exists because the previous one left something measurably broken.

| End of | Deployables | Market modules added or changed | Stores | Measured problem that forces the next step |
|---|---|---|---|---|
| [S0](stage-00-bootstrap.md) | market skeleton | — | PG17 | — |
| [S1](stage-01-layered-monolith.md) | market (layered) | identity, vendors, catalog | PG, S3-compatible store (Garage) | Placing orders needs stock that stays correct under concurrency |
| [S2](stage-02-checkout-correctness.md) | market | inventory, cart, ordering (checkout, vendor groups, fulfillment), promotions. The confirmation email is sent synchronously. | PG (RLS) | Catalog p95 is high under repeated reads. The limiter allows 4× the limit across workers. Refresh tokens cannot be revoked. |
| [S3](stage-03-redis-auth-bot.md) | market + **bot** (a new client, not a split) | cart moves to Redis | + redis-cache, redis-state | The synchronous email adds seconds to checkout, and an SMTP hiccup fails the checkout. Modules import each other freely. |
| [S4](stage-04-async-events-boundaries.md) | market with process types web/worker/beat/relay/consumers. Bot has a sender process. | Boundaries enforced (independence contracts). Adds notifications, search, reviews, imports. | + RabbitMQ (+ OpenSearch only if Postgres FTS fails) | The platform has to take money |
| [S5](stage-05-atlaspay-monolith.md) | + **provider-sim** (an external emulator) | + payments, the AtlasPay module (intents, providers, ledger, connect, payouts, reconciliation) | + sim DB | It only runs on a laptop, and nobody knows what is slow |
| [S6](stage-06-ship-and-operate.md) | Same, running on a Terraform-provisioned VPS behind Nginx. `/providers/*` gets its own gunicorn pool. | — | + replica, WAL archive, Prometheus/Loki/Tempo | Analytics GROUP BYs and velocity rules are slow. Buyers and vendors now need chat, an append-only, per-conversation, TTL workload. |
| [S7](stage-07-polyglot-mongo-timescale.md) | same | + conversations (Mongo), velocity rules on Timescale CAGGs, fraud v1 scoring in shadow mode | + Mongo 8.0 replica set, Timescale (`tsdb`) | Streamed LLM answers hold sync workers: 8 open chats stall checkout |
| [S8](stage-08-ai-integration.md) | + **ai** (FastAPI). This is the first split. | semantic/hybrid search, flags, ActionRequest | + `ai` DB (pgvector), pgvector in market, Mongo `atlas_ai` | Split gate: the S6 lock stall freezes Payme callbacks. market (the core) holds all the provider secrets. Every verifier of the HS256 token can also mint tokens (found in S8). AtlasPay has to be neutral between its merchants. |
| [S9](stage-09-strangler-atlaspay-auth.md) | + **atlaspay** and **auth** (FastAPI, each with its own DB), Keycloak, Vault | payments module is contracted away (fraud v1 shadow scoring and the tsdb/fraud consumers are ported into atlaspay). market calls AtlasPay as merchant #1 and learns outcomes only from webhooks. | + atlaspay DB, auth DB | Compose has no rolling updates or HPA (container count recorded). A flash sale starves market's DB pool. Two bot replicas get 409. |
| [S10](stage-10-kubernetes-grpc-inventory.md) | Everything on kind, and on k3s in the cloud. + **inventory** (gRPC). PgBouncer. Bot moves to webhook mode. | inventory module is contracted away | + inventory DB, Redis gate | Every market deploy drops 100% of Channels sockets. The product page is a 6-call waterfall (call count and p95 measured in S10 once inventory is out). The SPA must not hold tokens. |
| [S11](stage-11-realtime-edge-graphql.md) | + **edge** (FastAPI + Strawberry: GraphQL, WS, SSE, BFF session), React SPA | — | Redis pub/sub + Streams | The ledger reaches 50M lines and the platform account is hot. Model dependencies bloat every atlaspay replica. |
| [S12](stage-12-data-at-scale-fraud.md) | + **ledger** (gRPC, Citus), **fraud** (gRPC) | — | Citus. Mongo sharded lab. Redis Cluster lab (from S3). | End of Season 1 |

A few words used above, defined once:
- *Contracted away* is the last step of the *expand/contract* pattern. After a module has been copied into a new service and traffic has moved, the old code and tables are removed.
- A *CAGG* is a TimescaleDB continuous aggregate: a materialized rollup that refreshes incrementally.
- *HPA* is the Kubernetes Horizontal Pod Autoscaler.
- *Strangler fig* means replacing a piece of a live system by routing its traffic, bit by bit, to a new implementation until the old one can be removed.

### 5.2 The evolution in seven pictures

The seven steps below group the stages by architectural shape. They are called "steps" rather than "phases" so they are not confused with the old phase files.

#### Step 1 — Layered monolith (S0–S3, W1–W12)

```
   customers, vendors, ops                               Telegram users (S3)
   (DRF API + Django Admin)                                     |
              |                                                 v
              v                                         +----------------+
   +------------------------------+   internal REST     | bot (aiogram)  |
   |   market  (Django 5.2 + DRF) |<--------------------| polling mode,  |
   |                              |   static service    | FSM in Redis   |
   |   views                      |   token             +----------------+
   |     -> services / selectors  |
   |        -> ORM                |   S1 modules: identity, vendors, catalog
   |   (import-linter "layers")   |   S2 modules: inventory, cart, ordering, promotions
   +--------------+---------------+
                  |
    +-------------+--------------+-------------------+
    v             v              v                   v
 PG17 `market`  Garage (S3)    redis-cache         redis-state
 (RLS from S2)  (presigned     (allkeys-lru,       (noeviction,
                 URLs only)     no persistence;S3)  AOF everysec; S3)
```

**What changed and why:**
- **S1** sets the habit that every later stage relies on: views never touch the ORM. With the rule "business logic lives in services", extracting a module in S9 means moving a folder, not untangling views.
- **S2** makes checkout correct under concurrency *inside the database*, with atomic updates, lock ordering, SERIALIZABLE with retry, Postgres idempotency and RLS. The fixes are local transactions, so they only work while everything shares one database. This is the main reason checkout is never split.
- **S3** adds Redis only after measuring cold and warm catalog p95. Redis is split into two instances once one shared LRU instance silently evicts limiter keys.
- The bot is a *new client*, not a split. It calls market's service layer over internal REST.

#### Step 2 — Modular monolith with events and money (S4–S7, W13–W31)

```
                      one market image, several process types
 +---------------------------------------------------------------------------+
 |  web (gunicorn) | worker (Celery) | beat | relay (outbox) | consumers      |
 |---------------------------------------------------------------------------|
 |  identity  vendors  catalog  inventory  cart  ordering  promotions         |
 |  payments = AtlasPay (intents, providers, ledger, connect, payouts, recon) |
 |  search  reviews  notifications  conversations  analytics  outbox          |
 |  modules talk only through api.py facades and events (S4)                  |
 +------+------------------------------+-------------------------------------+
        | outbox row, same transaction  ^  Payme JSON-RPC / Click form POST
        v                               |  to /providers/*
   relay --> RabbitMQ `atlas.events`    |
             (quorum queues, DLX,       +---- provider-sim (FastAPI, own `sim` DB; S5)
              retry tiers)
                 |
                 +--> consumers (inbox dedup), bot sender --> Telegram (paced)

 Stores: PG `market` (+ streaming replica, WAL archive, PITR from S6), redis-cache,
         redis-state, Garage (S3 API), Mongo 8.0 replica set (S7), Timescale `tsdb` (S7)
 Runs on: Compose on a laptop (S4-S5) -> Terraform VPS behind Nginx + TLS,
          observed with Prometheus, Loki, Tempo, Sentry (S6)
```

**What changed and why:**
- **S4** moves slow work off the request path (Celery). It makes side effects lossless with a *transactional outbox*: the event is written as a row in the same transaction as the state change, and a relay publishes it later. It also enforces module boundaries with import-linter *independence* contracts, after a *leak hunt* that counts every cross-module import. That count is the coupling number that every later extraction ADR cites.
- **S5** adds money inside the monolith, on purpose. A payment system is easiest to make correct while the ledger, the order and the idempotency store share one transaction. provider-sim is not a split; it plays the external world.
- **S6** puts the system on a public HTTPS URL and makes it observable. It builds the split gate, and its lock-queue drill produces the first number that hurts: an `ALTER TABLE` stalls Payme callbacks.
- **S7** adds Mongo and Timescale only where each one measurably fits. For per-category attributes JSONB is expected to *win*, and the ADR says so.

#### Step 3 — The first split: ai (S8, W32–W36)

```
   browser, bot /ask                                  LLM providers
          |                                   primary -> cheaper tier -> second
          v                                   provider -> Ollama (fallback chain)
   +--------------+   REST + SSE                        ^
   |   market     |   /v1/assistant/*   +---------------+---------------+
   |   (Django)   |-------------------->|   ai (FastAPI)                |
   |              |<--------------------|   gateway: timeouts, breaker, |---> /mcp
   |   search:    |   internal REST     |   budgets, PII redaction      |  (MCP, read-only
   |   pgvector + |   with the caller's |   RAG, agent (proposes only)  |   tools)
   |   FTS (RRF)  |   delegated token   +---------------+---------------+
   +------+-------+                                     |
          | outbox: product.changed, policy.changed     |
          v                                             v
   RabbitMQ --- ai.embedding-sync ---------> PG `ai` (pgvector: kb_chunk, semantic_cache;
                                                      usage_ledger)
                                             Mongo `atlas_ai.transcripts` (redacted, TTL)
                                             redis-state (token and $ budgets)
                                             redis-cache (`sc:` cached answers, TTL)
```

**What changed and why:** you first build `/assistant/ask` as a streaming *sync* Django view. Eight concurrent 20-second chats stall checkout, because each open stream holds a gunicorn worker. That measured exhaustion, plus the boundary argument (LLM keys, PII and budgets belong behind one wall), is ADR-027. The threat review here also finds that `ai` verifying market's HS256 tokens means `ai` could *mint* market admin tokens. That is recorded now and fixed in S9.

#### Step 4 — Strangler fig: atlaspay and auth (S9, W38–W42)

```
                     Nginx route switch (a write freeze of a few seconds)
                                    |
          +-------------------------+------------------------+
          v                                                  v
   +--------------+  REST /v1, sk_ key, Idempotency-Key  +------------------+
   |   market     |------------------------------------->|   atlaspay       |<--- Payme / Click
   |  merchant #1 |<----- signed webhooks ---------------|   (FastAPI,      |     callbacks
   |  (bulkhead,  |       Atlas-Signature, via RabbitMQ  |   atlaspay-domain|     (provider-sim
   |  breaker,    |       delay tiers, hash-ring         |   moved as-is)   |      mirrors traffic
   |  saga)       |       dispatchers                    +--------+---------+      to old + new in
   +------+-------+                                               |                shadow mode)
          | Django session = BFF                    PG `atlaspay` (logical replication of
          v (confidential client)                   payments_* during cutover), Vault
   +--------------+  RS256 + kid + JWKS, PKCE,
   |   auth       |  client-credentials JWTs (aud, scope) ---> verified by every service
   |   (FastAPI)  |---- OIDC federation ----> Keycloak 26.7
   +--------------+
     PG `auth`
```

**What changed and why:** the split gate is re-run first. AtlasPay leaves because of four things:
- the S6 lock stall froze callbacks;
- market held every provider secret;
- there was an SLO gap;
- a payment operator must be neutral between its merchants, market included.

ADR-030 must answer the strongest counter-argument, "extract it as a Django service", which is lower risk because it moves code instead of rewriting it. The rewrite is acceptable only because `atlaspay-domain` is framework-free, so only the adapters are new.

AtlasPay gets its own host, `pay.<domain>`, for its public API, provider callbacks and payment links, so its routes never share a path prefix with ai's `/v1/assistant/*`. The fraud v1 path (velocity-rule reads from the `fraud_features` CAGGs, model loading, shadow scoring) and the `tsdb.pay-metrics-writer` and `fraud.features` consumers move into atlaspay with the adapters. In the contract step, `market.payment-events` is unbound and deleted: from then on, market learns payment outcomes only from signed webhooks.

auth leaves for three reasons: issuer neutrality across trust domains, the new OIDC/PKCE/MCP-client surface (strangler rule: new capability lands in the new service), and blast radius. The S6 lock drill slowed token refresh only indirectly: refresh does not touch `ordering_order`, but it shares market-web's threads and DB pool with the checkout requests queued behind the lock. A separate pool would cure that, so ADR-031 says honestly that the slowdown is not a reason to split. RS256 alone would *not* justify a split either. The exit criterion: the whole S5 acceptance suite is green against atlaspay, the reconciliation diff is 0, **and** shadow fraud scores are still recorded for 100% of attempts.

#### Step 5 — Kubernetes and gRPC inventory (S10, W43–W46)

```
  kind on the laptop  /  k3s in the cloud (Terraform: 1 server + 1 agent)
  namespaces: atlas-dev, atlas-staging, atlas-prod, atlas-labs
 +----------------------------------------------------------------------------+
 |  Gateway API / Ingress: Traefik or Envoy Gateway (+ rate-limit middleware) |
 |      |               |                |               |                    |
 |      v               v                v               v                    |
 |  market web       atlaspay          auth             ai        bot         |
 |  (HPA 2->5->2),   (reconciliation/                             (webhook,   |
 |  worker, beat     payout scheduler                              2+ pods,   |
 |  (singleton),     elected by a                                  per-chat   |
 |  market-checkout  Kubernetes Lease)                             lock,      |
 |  Deployment                                                     dedup)     |
 |      |                                                                     |
 |      | gRPC: headless Service + dns:/// + round_robin + max_connection_age |
 |      v                                                                     |
 |  inventory (grpc.aio) ---> PG `inventory` + redis-state flash-sale gate    |
 |                                                                            |
 |  PgBouncer (transaction mode) in front of Postgres; migrations as a        |
 |  pre-deploy Job; NetworkPolicy: PG `atlaspay` reachable only from atlaspay |
 +----------------------------------------------------------------------------+
```

**What changed and why:**
- **Kubernetes.** Compose has no rolling updates and no autoscaling, and ADR-035 records the container count as evidence. Kubernetes arrives with probes, preStop, HPA, a Lease and PgBouncer. PgBouncer is needed because HPA × pool size exhausts Postgres connections.
- **Inventory.** It is extracted only after three things have been measured: the flash-sale numbers in the monolith, then a Redis gate, then a separate `market-checkout` Deployment with its own pool. Each configuration runs as a split-gate run ported to kind (the mid-run deploy becomes a `kubectl rollout` with the migration Job), with the flash sale as the extra load. ADR-036 must answer the counter-argument that "reservation + order in one local transaction is the oversell-proof shape", and must state which numbers would revert the split.
- **Bot.** It moves to webhooks because two polling replicas get `409 Conflict`.

#### Step 6 — Realtime edge and GraphQL BFF (S11, W47–W49)

```
     React SPA (Vite + TypeScript + TanStack Query)
     holds only a cookie; never holds tokens
                  |
                  v
   +-------------------------------------------------+
   |  edge (FastAPI + Strawberry)                    |
   |   /graphql   DataLoaders per request, depth and |
   |              cost limits, persisted queries,    |
   |              Relay cursors, subscriptions       |
   |   /ws, /sse/*  single-use tickets, 20 s         |
   |              heartbeat, resume, bounded queues  |
   |   /session/* BFF: confidential OIDC client      |
   +-----+---------------+---------------+-----------+
         | REST          | gRPC          | REST                ^
         v               v               v                     | Redis Streams
      market         inventory        atlaspay                 | ws:stream:{user}
                                                               | (+ pub/sub pings)
   RabbitMQ atlas.events --> edge.fanout ----------------------+
```

**What changed and why:** a Django Channels spike in market is measured first. One market deploy drops 100% of sockets and causes a reconnect storm. The product page is a 6-call waterfall (measured in S10), and the SPA must not hold tokens. ADR-038 uses those three facts to justify `edge`, which holds sockets, composes backends through GraphQL, and keeps the OIDC session server-side. edge owns no database: redis-state only.

#### Step 7 — Data at scale: sharded ledger and fraud service (S12, W51–W53)

```
   atlaspay --outbox--> RabbitMQ `ledger.postings` --> ledger (grpc.aio + SQLAlchemy Core)
      |                                                    |
      +-- gRPC PostEntries / GetBalance (debits: sync,     |
      |   with a deadline; same key on unknown outcome) ---+
      |                                                    v
      |                                  citus-ledger: coordinator + workers,
      |                                  distributed by owner_account_id,
      |                                  every journal entry single-shard,
      |                                  per-shard platform sub-accounts
      |
      +-- gRPC FraudService/Score (50 ms deadline, breaker) --> fraud (grpc.aio)
                          model loaded at startup from bucket `atlas-models`;
                          features from tsdb `fraud_features` + redis-state
          fraud down => rules only: fail open below amount X, hold for review at >= X

   Labs: Mongo sharded cluster (conversations, {conversation_id: "hashed"}),
         Redis Cluster (from S3)
```

**What changed and why:** the ledger is seeded to 50M lines (20M on a 16 GB laptop). The hot platform account is **fixed in place first** with bucketed sub-accounts, and measured again. ADR-040 is labelled "the most debatable split, revertible". At synthetic volume single-node Postgres may well suffice, and the ADR must say so if it does. Sharding the naive way (by `ledger_account_id`) makes every fee-bearing entry a Citus two-phase commit. The redesign by `owner_account_id` makes every entry single-shard. Fraud leaves because model dependencies × replicas bloat atlaspay, the model needs its own deploy cadence, and the fallback becomes testable. The payment path keeps flowing when fraud is killed.

### 5.3 The final shape

The final shape is 9 production deployables (market, atlaspay, auth, ai, edge, bot, inventory, ledger, fraud) plus provider-sim. If you apply the whole degrade list, 7 production deployables plus provider-sim remain: the fraud service stays in-process and inventory stays a module, so gRPC is used on the ledger only, and the gRPC foundation (`libs/atlas-proto`, buf checks in CI, interceptors) is built in S12 instead of S10. See [schedule-and-cuts.md](schedule-and-cuts.md).

---

## 6. The Season 1 stage plan

### 6.1 Stage table

| Stage | Weeks | Hours M+S | Architecture at end | Headline lessons | Old-spec theory to read | Tag |
|---|---|---|---|---|---|---|
| [S0 Bootstrap (+ Django orientation)](stage-00-bootstrap.md) | W1–2 | 24+3 | skeleton, CI, bench harness, worldgen | multi-stage non-root image, pins, licences, benchmark protocol, Django orientation (official tutorial parts 1–2, settings and the deployment checklist) | P1 D1–D6, P2 D25–D30 | v0.0 |
| [S1 Layered monolith: vendors, catalog, identity v1](stage-01-layered-monolith.md) | W3–6 | 48+6 | market (layered) | Django ramp, EXPLAIN before index, keyset vs OFFSET, N+1, MoneyField descriptor, EXCLUDE, 4× in-memory limiter | P1 D7–D18, P2 D25–D39, P5 D79–D90, P7 D109–D114 | v0.1 |
| [S2 Checkout correctness](stage-02-checkout-correctness.md) | W7–9 | 36+4 | + ordering/inventory/promotions | oversell, deadlock, write skew, idempotency (why not Redis), timeouts, RLS | P1 D19–D24, P2 D31–D39, P4 D67–D71, P9 D145–D153, P10 D157–D165, P3 D42–D43 | v0.2 |
| [S3 Redis, auth hardening, bot v1](stage-03-redis-auth-bot.md) | W10–12 | 36+5 | + redis-cache/state, bot | stampede, invalidation race, eviction, limiter INCR race → Lua, refresh families, Cluster CROSSSLOT, aiogram ramp and FSM | P2 D31–D39, P5 D85–D90, P9 D151–D153, Proj27 D171–D173, P2 Wk7 / P3 Wk9 bot extensions | v0.3 |
| [S4 Async, events, boundaries, search](stage-04-async-events-boundaries.md) | W13–17 | 60+7 | modular monolith, Celery, RabbitMQ, outbox | sync email → Celery, visibility/consumer timeout, lost event → outbox, DLQ, leak hunt, FTS, vendor bot flow | P3 D42–D53, P4 D55–D78, P7 D109–D120, P8 D121–D126, P10 Wk28 Telegram extension | v0.4 |
| [B1 Buffer + checkpoint + mock #1](buffers-and-job-sprint.md) | W18 | 12 | — | SD5, SD16; recalibrate with the hours log (actual/budget) | — | — |
| [S5 AtlasPay v1 in the monolith + provider-sim](stage-05-atlaspay-monolith.md) | W19–23 | 60+6 | + payments module, provider-sim | Payme/Click protocols, Stripe idempotency, deferred constraint trigger, Connect math, 12 failure scenarios, reconciliation | P6 D91–D96, P9 D145–D153, P4 D67–D71, P10 D163–D165, phase-8 D241–D243, plus the Payme/Click protocol notes in the stage file | v0.5 |
| [S6 Ship & operate → slice 1](stage-06-ship-and-operate.md) | W24–28 | 60+5 | VPS (Terraform), observed, replica, PITR | CD, zero-downtime migrations, OTel/Tempo, Postgres operations, SLO, drill, split gate | P6 D97–D108, P8 D127–D132, P9 D151–D156, P10 D163–D165 | v0.6 |
| [S7 Polyglot I: Mongo + Timescale + fraud v1](stage-07-polyglot-mongo-timescale.md) | W29–31 | 36+5 | + Mongo replica set, tsdb | honest JSONB vs Mongo, write concerns, CAGGs, the `-oss` trap, ML ramp, leakage-safe features, logistic regression in shadow mode | P7 D109–D114, P2 D37–D39, P9 Wk26 ML extension, P4 Wk13 ML extension | v0.7 |
| [S8 AI integration → slice 2](stage-08-ai-integration.md) | W32–36 | 60+6 | + ai | gateway fallback/budgets/PII, RAG + evals, approval-gated agent, MCP, flags | phase-7 D181–D215, phase-8 D223–D227, P5 Wk15, P8 Wk22 RAG extension | v0.8 |
| [B2 Buffer + job sprint + mock #2](buffers-and-job-sprint.md) | W37 | 12 | — | CV, demo, SD10/11/13; job applications start | — | — |
| [S9 Strangler: AtlasPay + auth](stage-09-strangler-atlaspay-auth.md) | W38–42 | 60+6 | + atlaspay (with fraud v1 in shadow mode), auth, Keycloak, Vault | shadow cutover, logical replication, API keys, versioning, webhooks, bulkhead, saga, RS256/JWKS/PKCE/OIDC (Keycloak and Google) | P5 D79–D90, P9 D145–D156, P6 D94–D101, P7 D115–D120, P10 D163–D165, P8 D131, Proj26 D169–D170 | v0.9 |
| [S10 Kubernetes + gRPC inventory + bot webhook](stage-10-kubernetes-grpc-inventory.md) | W43–46 | 48+6 | kind + k3s cloud, + inventory, PgBouncer | probes/preStop/HPA/Lease, HTTP/2 load-balancing trap, flash sale with fencing, 409 → webhook | P8 D127–D132, P9 D151–D153, Proj28 D175–D178, P1 D19–D24, P10 D163–D168 | v0.10 |
| [S11 Realtime edge + GraphQL + React](stage-11-realtime-edge-graphql.md) | W47–49 | 36+4 | + edge, SPA | Channels vs FastAPI, fan-out/resume/backpressure, DataLoader 51→2, cost limits, BFF session, React/TS ramp | P7 D115–D120, P10 D157–D161 / D166–D168, P5 D85–D90 | v0.11 |
| [B3 Buffer + checkpoint](buffers-and-job-sprint.md) | W50 | 12 | — | Last catch-up before S12; re-plan S12 with the hours-log ratio | — | — |
| [S12 Data at scale + fraud service + closing](stage-12-data-at-scale-fraud.md) | W51–53 | 36+3 | + ledger (Citus), fraud | single-shard entries vs 2PC, rebalance, Mongo shard key/reshard, served model with fallback, SD20 | P8 D131, P9 D151–D156, P9 Wk26 extension, SD bank | v1.0 |
| **Total** | **53** | **600 + 66 + 36 buffer = 702** | | | | |

Two milestones matter more than the others:
- **Slice 1 (end of S6, W28, tag v0.6).** A public HTTPS URL, a dashboard, one checkout trace end to end, a deploy under load with 0 errors, a restore log, and a README with numbers.
- **Slice 2 (end of S8, W36, tag v0.8).** A streamed, cited answer; a leakage attempt refused; an agent-proposed refund executed exactly once after approval; an MCP client querying an order; the eval report.

### 6.2 The weekly rhythm (12–15 h)

| Session | Length | What goes here |
|---|---|---|
| Three weekday sessions | 2 h each | Reading the cited old theory days, writing tests, building features, and the **drill hour** |
| Optional fourth weekday session | 2 h | Catch-up first; stretch only if the must tier is on track |
| One weekend block (always) | 5–6 h | Anything that needs uninterrupted state: cutover rehearsals, deploys under load, PITR restores, chaos runs, resharding under load, `terraform apply`/`destroy`, split-gate runs, mock interviews |

The **drill hour** is 1 h a week: one SQL problem on the Atlas schema or one DSA problem from the banks, plus the week's SD or interview questions. It keeps interview muscles warm without stealing project time.

**Why weekend blocks are sacred.** A PITR restore, a shadow cutover or a Citus rebalance under load is a sequence of steps where the half-done state is fragile. Stopping in the middle on a Tuesday night means redoing the setup on Wednesday. Put those tasks only in the long block; weekday sessions get work that can stop at any test boundary.

### 6.3 Tiers, budgets and checkpoints

- **Must (M)** is the minimum to close a stage. Each stage's M is exactly 12 × its weeks, so the must tier plus the three buffer weeks fills a 12 h/week floor with no slack inside any stage.
- **Stretch (S)** is done only when M closes early. Stretch items are marked *Stretch* in every stage file.
- **Block budgets.** Each build block in a stage file has a must-tier hour budget in brackets, for example "Limiter [5 h]", and a stage's brackets add up to its must hours. Stages that introduce a tool you have not used (Django in S0, aiogram in S3, ML in S7, React/TypeScript in S11) carry an explicit ramp block. Benchmark blocks include the unattended wall-clock time of their runs (configurations × runs × about 11 min, plus harness and ADR time); schedule those runs in the weekend block.
- **The hours log.** From S0, log the actual hours of every block in `docs/hours.csv`. If a block goes over budget, stop polishing and move on, and record what you left in `docs/deferred.md`, unless the item is on the never-cut spine: a spine item gets finished and the date moves. Nothing on the spine is silently deferred.
- **Checkpoints** are at B1 (W18), B2 (W37) and B3 (W50). At B1, compute actual/budget from the hours log and re-plan the remaining stages with that ratio. If you are more than one week behind at any checkpoint:
  1. drop all remaining stretch;
  2. then apply the degrade list in its order until the gap closes.

  The *degrade list* ([schedule-and-cuts.md](schedule-and-cuts.md), with each item's hours) holds must-tier items that shrink to a cheaper version. Items that touch no explicit requirement come first. Items that touch one come last and only as partial degrades: GraphQL subscriptions survive (only the persisted-query build tooling goes), a 2-shard Mongo cluster with one shard-key experiment and a reshard survives (only the third key goes), and compression plus retention survive on one hypertable. The Mongo sharded-lab degrade and the Citus rebalance-under-load degrade are mutually exclusive (never apply both), so one resharding run under load always remains. A degrade item for a future stage frees hours only in that stage; it does not reduce today's backlog. The *never-cut spine* is what the portfolio cannot lose: the oversell, idempotency, outbox and ledger invariants shown red then green; the 12 provider scenarios; reconciliation; the S6 deploy, observability, PITR and drill; the split gate and every extraction ADR; the AtlasPay shadow cutover; the Lua limiter path; Kubernetes basics; the gRPC ledger with the load-balancing fix; the Citus single-shard rule; the RAG eval gate and the approval-gated agent; the fraud fallback; SD20 and the mocks.
- **Job search** starts in B2 (W37) and costs 2–4 h a week, taken from stretch time first. At the 12 h/week floor there is no stretch time, because must + buffers already use every hour (636 h = 53 × 12). So every job-search hour either comes from working above the floor or moves the end date: 2 h/week from W38 to W53 is 32 h, close to three weeks at 12 h/week. Plan for one of the two; do not cut the spine.

The scenario arithmetic (what 12, 13.5 and 15 h/week each buy), the risk list and the full degrade list are in [schedule-and-cuts.md](schedule-and-cuts.md). The buffer weeks are described in [buffers-and-job-sprint.md](buffers-and-job-sprint.md).

---

## 7. Decision tables

These tables are fixed for the whole season. Stage files refer to them by number ("see E3"). There is no E9 in this plan; the numbers match the references used in every other file. When you write an ADR that touches one of these decisions, cite the table and add *your* numbers. The table gives the decision, and your evidence makes it yours.

### E1. Framework per service

**The general rule behind every row:**
- **Django** where the work is database-bound and the back office is a large part of the product.
- **FastAPI** where the work is async I/O, long-lived connections, byte-level protocol control or a trust boundary.
- **grpc.aio** for internal, contract-first, deadline-bound calls.
- **aiogram** for Telegram.

The right-hand column is the strongest argument *against* each choice, and the answer you give in an interview.

| Service | Framework | Why | Counter-argument → answer |
|---|---|---|---|
| market | Django 5.2 LTS + DRF 3.18, gunicorn gthread, Celery 5.6 | The back office (KYC, moderation, refund approval, dispute evidence, ops) is about half the product. Admin, auth/CSRF, the migrations graph and the Celery ecosystem come built in. The work is DB-bound, so async buys nothing. It is the most-asked stack in the learner's market. | *"FastAPI reuses your 15 h and is async"* → the 15 h are reused in provider-sim, atlaspay and ledger. FastAPI wins for a fan-out product with no back office. *"Django async is partial; transactions don't work in async mode"* → market stays sync, and async workloads leave it. Django 6.1 is not used because 5.2 LTS has security support to 2028-04, covering both seasons, while 6.1's support ends around 2027-12 and would force a mid-season upgrade. |
| atlaspay | FastAPI + SQLAlchemy 2.0 async + Alembic | Byte-level protocol control (HTTP 200 on every Payme error, JSON-RPC and form bodies, no framework auth/CSRF). Heavy outbound I/O. Pydantic → OpenAPI for a versioned public API. Explicit SQL locking. | **Extracting it as a Django service is lower risk (move, don't rewrite).** The rewrite is accepted only because `atlaspay-domain` is framework-free, so only adapters are rewritten. ADR-030 argues it. |
| auth | FastAPI + Authlib 1.8 + joserfc | Small, crypto-heavy, async calls to IdPs, no UI | The usual real-world answer is to buy Keycloak or Auth0 and keep identity in the monolith. ADR-031 says so; it is built here for issuer mechanics and neutrality across trust domains. |
| ai | FastAPI | SSE, cancellation, concurrency caps, 10–60 s calls, its own boundary for keys and PII | Async Django views can stream; rejected by the measured worker exhaustion plus the boundary argument |
| edge | FastAPI + Strawberry 0.327 | Thousands of sockets per pod, concurrent resolvers, holds the BFF session | Channels keeps one codebase (measured in S11) and wins while deploys are rare. Graphene is stagnant. |
| inventory | grpc.aio | gRPC and async Redis on one event loop; tiny surface | Stay a module, backed by the checkout Deployment's numbers (the inventory-extraction degrade item, 24) |
| ledger | grpc.aio + SQLAlchemy Core | Internal only, a protobuf money contract, deadlines, streaming statements, SQL-first on Citus | Most companies keep the ledger inside payments. This is the most debatable split. |
| fraud | grpc.aio | p99 ≤ 30 ms, model loaded at startup, ML dependencies isolated | As an in-process library it has the lowest latency (the fraud-service degrade item, 23) |
| bot | aiogram 3.31 (aiohttp webhook server) | Routers, FSM storages, middlewares, webhook handler | python-telegram-bot is equally valid |
| provider-sim | FastAPI + SQLAlchemy 2.0 async | A network peer for two protocols, a fake clock, concurrent duplicates | A pytest fixture cannot reproduce real timeouts and lost responses |

**About the sunk FastAPI work.** You are around Day 5 of the old StockPilot (FastAPI + SQLAlchemy 2.0 async). ADR-000 records the choice of Django for market *despite* that sunk cost. The FastAPI skills are not wasted: provider-sim (S5), atlaspay (S9) and ledger (S12) reuse them. Your first STAR story is about exactly this decision.

### E2. Service catalog at the end of Season 1

*Origin → stage* says where the code came from and when it left. *Async* lists what each service publishes to and consumes from RabbitMQ's topic exchange `atlas.events`.

| Service | Origin → stage | Forcing problem | Sync interfaces | Async (RabbitMQ `atlas.events`) | Stores |
|---|---|---|---|---|---|
| market | — / S0 | — | REST `/api/v1`, Admin, internal REST (bot, ai, edge). Client of inventory gRPC and atlaspay REST (`Authorization: Bearer sk_…`). Receives signed AtlasPay webhooks (S9). | Publishes `order.*`, `vendor_group.*`, `product.changed`, `review.created`, `chat.message_sent`, `policy.changed`. Consumes `stock.changed` (S10), `user.*` (S9). Consumed `payment_intent.*` through `market.payment-events` in S5–S8 only; from S9, payment, refund and payout outcomes arrive only as signed AtlasPay webhooks. | PG `market` (+ replica, PgBouncer, RLS, FTS, pgvector), redis-cache/state, Mongo `atlas_conversations`, tsdb `analytics`, the S3-compatible store (Garage), (OpenSearch) |
| ai | market code / S8 | Streaming holds sync workers (8 chats stall checkout); key, PII and budget boundary | REST + SSE `/v1/assistant/*`, `/v1/descriptions/*`, MCP `/mcp` (on market's host `atlas.<domain>`, routed to ai by path); internal `/v1/embeddings` for market's product and query vectors (never routed publicly) | Consumes `product.changed`, `policy.changed` | PG `ai` (pgvector: KB and the semantic-cache index; usage), Mongo `atlas_ai`, redis-state (`budget:`), redis-cache (`sc:`) |
| atlaspay | payments / S9 | S6 lock stall freezes callbacks; secrets scope; SLO gap; operator neutrality | On its own host `pay.<domain>`: public REST `/v1/*` (keys as `Authorization: Bearer`, `Atlas-Version`), Payme/Click callbacks, `/l/{code}`. Click merchant API out. From S12, gRPC client to ledger and fraud. | Publishes `payment_intent.*`, `payment_attempt.created`, `refund.*`, `transfer.*`, `payout.*`. Runs the `tsdb.pay-metrics-writer` and `fraud.features` consumers ported from market in S9 (`fraud.features` moves to the fraud service in S12). Webhook dispatch queues. | PG `atlaspay`, redis-state, redis-cache (payment links), Vault, tsdb `pay_metrics` |
| auth | identity / S9 | Issuer neutrality; OIDC/PKCE/MCP-client surface; blast radius. The S6 refresh slowdown was indirect (shared pool); a separate pool cures it, so ADR-031 does not count it. | OAuth2/OIDC endpoints, JWKS, token (client credentials), Telegram login verification | Publishes `user.registered`, `user.updated`, `user.erased` | PG `auth`, redis-state, Keycloak |
| inventory | inventory / S10 | Flash sale, after the checkout-Deployment numbers | gRPC InventoryService | Publishes `stock.changed`; consumes `order.cancelled` | PG `inventory`, redis-state gate |
| edge | Channels spike + new / S11 | Deploys drop sockets; 6-call waterfall (measured in S10); tokens must stay out of the browser | GraphQL, WS, SSE, `/poll/*` (long-poll comparison), `/session/*`. Client of inventory gRPC, market REST and, if ADR-038 chooses it, AtlasPay REST `/v1/*` with market's read-only `rk_` key | Consumes `order.*`, `payment_intent.*`, `chat.*`, `vendor_group.*` → Redis Streams | redis-state only |
| bot | new client / S3 | — | Telegram (polling → webhook in S10); REST out with a service token | Consumes `bot.notifications` | redis-state (FSM, throttle, locks, dedup) |
| ledger | atlaspay.ledger / S12 | 50M lines; hot account (fixed in place first); a single natural shard key | gRPC LedgerService | Consumes `ledger.postings`; publishes `ledger.entry_posted` | Citus `ledger` |
| fraud | in-process in payments (S7), then in atlaspay (S9) / S12 | Model deps × replicas; model cadence; testable fallback | gRPC FraudService | Consumes `payment_attempt.created` (`fraud.features`) | tsdb `fraud_features`, redis-state, bucket `atlas-models` |
| provider-sim | external / S5 | No merchant contract | Payme and Click in both directions; an `llm` mode for CI. (The fake Telegram Bot API lives in `libs/atlas-testkit`, S4.) | — | PG `sim` |

**Deliberately not split:** catalog, cart, checkout/orders, promotions, fulfillment, vendors, reviews, search indexing, notifications, conversations, analytics. Checkout needs local transactions across cart, orders and promotions, and none of these modules has a measured forcing problem. Being able to name what you *didn't* split, and why, is as strong an interview signal as the splits themselves.

**Per-service databases, resolved.** This is the debate P10 left open: "Per-service databases" sits in the "Deliberately NOT connected" table of [10-atlasmarket.md](../python/10-atlasmarket.md) §10, with the matching mistake in §15.
- *Logical* ownership everywhere: app-label table prefixes, one set of roles (`<svc>_app`, `<svc>_migrator`, `<svc>_ro`) per service, and no cross-module FKs (enforced by a `pg_constraint` test from S4, with `identity_user` on the allow-list).
- *Physical* DB splits only where the forcing problem was at DB level: auth (security), atlaspay (lock stall and scope), inventory (contention), ledger (sharding), ai (boundary).

**Named future splits and their triggers.** These are written down so you can answer "what would you split next?" with a trigger instead of a wish.

| Future split | Trigger |
|---|---|
| search-indexer | Index lag above 60 s during imports |
| notifications | More than 3 channels with diverging SLOs |
| edge → BFF + realtime | BFF deploy churn dropping sockets beyond the budget |
| catalog read service | Reads exceed what 2 replicas can serve |

### E3. Data stores and sharding

**Postgres first, always.** Every other store arrives only after the Postgres version of the same workload has been measured, and each one has an explicit "not used for" column. That column is the part interviewers test.

| Store | Where it genuinely fits | Pain-first path | Stages | Not used for |
|---|---|---|---|---|
| **PostgreSQL 17** (the deep one) | Every system of record | S1: planner and all B-tree variants, GIN, GiST/EXCLUDE, CTE, JSONB. S2: MVCC, locks, isolation, SERIALIZABLE, timeouts, upsert, RLS. S4: SKIP LOCKED, partitioning, BRIN, FTS/trgm. S5: triggers, deferred constraint, window functions, matviews, generated columns, advisory locks. S6: pg_stat_statements, stats, bloat, HOT, lock queue, slots, sync commit, replica/RYW, PITR, zero-downtime migrations. S8: pgvector. S9: logical replication. S10: PgBouncer. S12: Citus. | all | — |
| Redis (Valkey 9.1) | Cache, semantic-cache answers (redis-cache); cart, limiters, stampede locks, fenced holds, FSM, budgets, pub/sub + Streams (redis-state) | One in-process dict → one shared LRU instance evicts limiter keys and a Celery task → split into cache and state instances → Cluster | S3, S4, S8, S10, S11 | Idempotency, balances, anything that must survive a restart |
| MongoDB 8.0 | Conversations and AI transcripts: append-heavy, document-shaped, TTL, accessed per conversation, needs to scale out | JSONB version first, measured → Mongo; replica set; transactions; aggregations; shard key; reshard | S7, S8, S12 | Catalog attributes (JSONB won the S7 benchmark); reviews (relational and small: a plain `order_item_id` column, no cross-module FK, verified through `ordering`'s `api.py` facade at write time, plus `UNIQUE(order_item_id)`) |
| TimescaleDB 2.30 (Community/TSL) | Payment attempt metrics, velocity features, vendor sales series | COUNT over 20M rows → matview → hypertable + CAGG, compression, retention | S7, S12 | OLTP; operational metrics (Prometheus) |
| OpenSearch 3.x vs PG FTS | Storefront search only if the judged set fails on FTS + trgm + transliteration | LIKE → trgm → FTS → OpenSearch | S4 (conditional) | Source of truth; vendor-admin search |
| pgvector 0.8.6 | Product semantic search (market DB); RAG KB and the semantic-cache similarity index, scoped by permission and prompt version inside SQL (ai DB; ADR-028) | Exact → HNSW vs IVFFlat → filtered-ANN pitfall → iterative scans | S8 | A separate vector DB below about 10M vectors |
| S3-compatible object store (Garage) | Images, KYC docs, imports, statements, WAL archive, models, eval sets | Presigned from the start; provider object storage in the cloud | S1, S6, S7 | Anything that gets queried |

A note on the Mongo row: "JSONB won the S7 benchmark" is the *prediction you verify*, not a conclusion you copy. The S7 prediction is "JSONB wins, because attributes are transactional with offers and live under RLS". If your numbers disagree, ADR-024 reports your numbers.

**Sharding.** *Sharding* splits one logical dataset across several nodes by a *shard key*. The key decides which rows live together, so it decides which transactions stay local.

| Target | Choice | Key | Resharding exercise |
|---|---|---|---|
| Ledger | Citus 14, preferred over app-level routing: co-location, single-shard transactions, an online rebalancer. App-level routing would mean owning cross-shard queries and moves yourself. | `owner_account_id` (connected account), not merchant_id: one platform merchant dominates, and tenant isolation cannot split a tenant. Per-shard platform sub-accounts. | `citus_rebalance_start()` under load |
| Webhook dispatch | App-level consistent-hash ring with vnodes | merchant id | 3 → 4 dispatchers, keys moved vs `% N` |
| Conversations | Mongo sharded cluster (lab) | `{conversation_id: "hashed"}` | First record the refusal: the S7 unique index `(conversation_id, client_msg_id)` blocks a shard key without `conversation_id` as its prefix. Then `reshardCollection` under writes; ADR-041 says what replaces the unique index under a hashed key |
| Limiter and cart | Redis Cluster (lab) | hash tags `{ip}`, `{api_key}` (the key id, never the secret), `{user}` | slot migration (stretch); master failover |
| orders, payment_intents | Not sharded | Two access keys (buyer and vendor), and lookups by provider id | Explained in ADR-041 |

### E4. Protocols

Each interaction gets the protocol whose guarantees it needs, and the "not chosen" column is the argument you should be able to make out loud. ADR-037 records the REST vs gRPC vs GraphQL decision: v1 in S10 with the measured REST vs gRPC p50/p95, and v2, finalized in S11 (must), with the GraphQL numbers.

| Interaction | Choice | Why | Not chosen |
|---|---|---|---|
| Storefront and dashboard → platform | GraphQL (edge BFF) | Composes 3–4 backends; shaped by the client | REST produces waterfalls; gRPC is not browser-native |
| Merchants, including market → AtlasPay | REST `/v1` on `pay.<domain>` + `Authorization: Bearer sk_…` + Idempotency-Key + dated versions | curl-able, SDK-friendly, the Stripe convention | GraphQL makes idempotency and caching awkward |
| Payme/Click → AtlasPay | Their JSON-RPC / form POST | Set by the providers | — |
| AtlasPay → merchants | Signed HTTPS webhooks through RabbitMQ delay tiers | Cross-organisation, at-least-once, retried for days | Synchronous callbacks |
| Vendor/ops → market | REST (DRF) + Admin | CRUD, ETag | — |
| market → inventory; atlaspay → ledger, fraud; edge → inventory | gRPC | Strict schema, deadlines, streaming, measured p95 | REST has no enforced contract or deadline propagation |
| Domain events; jobs | RabbitMQ (outbox); Celery on quorum queues | Per-message ack, DLQ, routing | Kafka (Season 2 CDC) |
| Status (S11) | SSE via `EventSource` | One-way, auto-reconnect, `Last-Event-ID` resume | WS is overkill |
| LLM tokens (S8) | SSE framing over a POST `fetch()` stream | One-way; `EventSource` cannot POST or set headers. No resume: a dropped stream ends with an error event and the client asks again | WS is overkill |
| Chat, dashboard, GraphQL subscriptions | WebSocket | Two-way | Polling (kept as the baseline) |
| edge fan-out | Redis Streams (resumable) + pub/sub (ephemeral pings) | Replay by id | A queue per socket |
| Telegram → bot | Webhook (dev: long polling) | Scales horizontally | Polling allows only one consumer (409) |
| External agents | MCP over stateless Streamable HTTP (spec 2026-07-28, Python SDK 2.x; re-check at stage start) with Keycloak OAuth | Standard tool discovery and authorization | — |

### E5. Auth evolution

Auth is built in layers, each added when a new threat or a new client appears. This follows the order in which real systems usually get them. You should be able to name, for each row, the attack or failure that forced it.

| Stage | Mechanism | Proof |
|---|---|---|
| S1 | argon2; session + CSRF (Admin); simplejwt HS256 access/refresh; RBAC + relationship permissions, with vendor membership resolved per request and never put in the token; enumeration-safe login with lockout | Permission matrix; byte-identical responses |
| S2 | RLS as the second wall, which depends on the per-request membership from S1 | Forgotten-WHERE test; SET leak |
| S3 | Refresh rotation with families, logout-everywhere, `jti` denylist; OTP failing closed; Lua limits | Replay revokes the family; OTP brute-force test |
| S5 | Provider auth: Payme Basic + IP allowlist, Click MD5 | -32504 and -1 tests |
| S8 | MCP static scoped token; agent acts with the delegated user token; the browser reaches ai's SSE with a short-lived (≤ 5 min) ai-audience token that market mints per page load (a known exposure, closed in S11); HS256 mint risk recorded | Confused-deputy test |
| S9 | auth service: RS256 + kid + JWKS + rotation; Authorization Code + PKCE; OIDC via Keycloak and Google; client-credentials JWTs (`aud`, `scope`) between services; merchant keys `pk/sk/rk × test/live`, sent as `Authorization: Bearer`; `whsec` webhook secrets; MCP OAuth via Keycloak; scoped client credentials for the bot, with an amount cap on bot-approved refunds and the approving ops user re-verified through their linked account (larger refunds are Admin-only); Vault | 0 × 401 during rotation; state/nonce/aud negative tests in CI |
| S10 | gRPC metadata interceptor verifying service tokens; NetworkPolicy; Telegram Login Widget HMAC; mTLS via Linkerd (stretch) | Cross-service denial test; forged hash rejected |
| S11 | BFF cookie session (edge as confidential client, per the OAuth browser-apps BCP, RFC 10017 [verify]); WS tickets; GraphQL field auth; Mini App initData (stretch) | Expired ticket rejected |

Two terms here trip people up:
- *RBAC* (role-based access control) answers "is this user a vendor_staff?".
- *Relationship-based* permission answers "is this user staff *of this vendor*?", a question about two records rather than one role.

The second kind is where real authorization bugs live, and S1 proves it with crafted requests.

### E6. aiogram 3

| Aspect | Design |
|---|---|
| Location | `services/bot` (S3). A thin client of market, ai and atlaspay; it never touches their DBs and has no business logic (P3). |
| Mode | Polling in dev (the `getUpdates` anchor for the S11 long-poll comparison, next to a tiny long-poll endpoint built in edge). In Kubernetes (S10): webhook via `SimpleRequestHandler(secret_token=…)`, port 443, `max_connections` tuned from the default of 40, `setWebhook` on deploy. `getUpdates` fails once a webhook is set. `TokenBasedRequestHandler` is avoided because it puts the token in the URL. |
| FSM | `RedisStorage` with TTLs (DefaultKeyBuilder prefix `fsm`). Flows: track order (S3); for vendor staff, a new-order message with an inline "mark shipped" button that goes through market's fulfillment API under the S1 relationship rule, plus a short FSM for the tracking number (S4); the ops refund-approval button (S8). |
| Concurrency across replicas | Per-chat Redis lock middleware plus `update_id` dedup; side effects idempotent on event id |
| Throttling | Inbound middleware using flags plus Redis (aiogram 3 has none built in) |
| Outbound | Leaky-bucket pacer: about 30 msg/s global, 1/s per chat, 20/min per group; honours `retry_after`; DLQ for chats that blocked the bot. Paid broadcasts are out of scope. |
| Notifications | `bot.notifications` fed by the outbox (S4): order updates for customers, new orders for vendor staff |
| AI | `/ask` calls ai; streamed with Bot API `sendMessageDraft` (Bot API 9.5+) [verify], with throttled message edits at ≤ 1/s as the fallback (S8) |
| Payments | **Primary (built in S9):** an AtlasPay payment link (SD1) that opens the provider checkout. When an order is `awaiting_payment`, the bot's message carries an inline URL button to a `/l/{code}` that market creates through AtlasPay; the "paid" message follows the webhook. **Stretch:** native Telegram Payments, as a spike run only against the fake Bot API in `libs/atlas-testkit` (no provider token needed); it is the first pick for spare hours. Click and Payme both appear in Telegram's provider list [C, older mirror]. The BotFather menu path, and whether test tokens are issued without a merchant contract, are **[U]**. A provider token routes money **directly to the provider and bypasses AtlasPay callbacks**, so `successful_payment` is imported as an external charge and reconciled against the ledger. Physical goods only: **digital goods and services (for example AI-assistant credits) must use Stars (`XTR`, empty `provider_token`)**, so AtlasMarket sells no digital goods in the bot in Season 1. |
| Tests | `AsyncMock` handlers; `Dispatcher.feed_raw_update()` for filters, middlewares and FSM; concurrent same-chat test; duplicate-tap test |

**Why the payment link is primary.** Native Telegram Payments send money straight to the provider under the provider's contract with the bot owner. AtlasPay would never see the callbacks, so its idempotency, ledger and reconciliation would be bypassed. A payment link keeps AtlasPay in the path. The native flow is a stretch spike (S10, testkit-only) that teaches the 10-second `pre_checkout_query` deadline and importing an external charge.

### E7. Where AI lives

In Season 1, AI is **backend engineering**. The hard parts are timeouts, retries that don't multiply, budgets, redaction, tenant isolation inside vector search, evals in CI and an agent that cannot move money. Prompt craft is a small part of it.

| Capability | Lives in | Key design | Stage |
|---|---|---|---|
| LLM gateway | ai | Fallback chain, breakers, TTFT timeout, retries before the first token only, budgets, redaction, registry, telemetry | S8 |
| RAG support assistant | ai (KB in ai PG + pgvector) | Tenant filter inside the query, hybrid RRF, citations, numeric guard, escalation | S8 |
| Semantic/hybrid product search | market search module | pgvector + FTS (or OpenSearch BM25) fused with RRF; embeddings refreshed by the `market.search-indexer` consumer | S8 |
| Vendor descriptions | market Celery → ai | Schema-validated structured output, approval gate, cost per vendor | S8 |
| Review summaries | market Beat → ai | Cites review ids; ratings taken from the DB | S8 |
| Agent (order help) | ai | Delegated token; ActionRequest approval; idempotent execution | S8 |
| MCP server | ai (second ASGI app) | Read-only tools; stateless Streamable HTTP (spec 2026-07-28); OAuth via Keycloak | S8/S9 |
| AI in the bot | bot → ai | Throttled message edits | S8 |
| Evals, cost, PII | CI + ai | Deterministic golden set on each PR; judge nightly (stretch); $ caps | S8 |
| **The one ML model: fraud** | Trained in S7 (shadow, in-process in market); ported into atlaspay in S9; served by `fraud` in S12 | Timescale 1h/24h CAGGs plus Redis 1m/10m windows; one feature function in the framework-free wheel `libs/atlas-fraud-features`; point-in-time correct; logistic regression after a short ML ramp (HistGradientBoosting, precision@k and calibration are stretch); PR-AUC with a cost threshold; artifact sha256 and model card; 50 ms deadline with rules fallback; `model_version` on every decision | S7, S12 |

Terms used above:
- *TTFT*: time to first token.
- *RRF*: reciprocal rank fusion, a way to merge two ranked lists, here keyword and vector results.
- *MCP*: Model Context Protocol, a standard way to expose tools to external agents.
- *ActionRequest*: the record an agent creates when it *proposes* a money action. A human approves it, and only then does the payments refund run, with `Idempotency-Key = ActionRequest.id`, exactly once.

### E8. Stack pins, compatibility and licences (ADR-001 / ADR-003)

> Pins are **as of 2026-09 — re-check with `scripts/compat_check.sh`** at the start of every stage. The script pulls every pinned image and prints server and extension versions. Anything marked [U] is an unconfirmed tag or fact, and the script is how you confirm it.

| Component | Pin | Why / trap | Licence note |
|---|---|---|---|
| Python | 3.13 | The version on which every pinned library's wheels are verified (aiogram, grpcio, Strawberry and Authlib need ≥ 3.10); re-check 3.14 with `compat_check.sh`. `uuid.uuid7()` is new in 3.14 [C], so you hand-roll UUIDv7 in S1, which is also the SD6 exercise. Type-check Django code with django-stubs and djangorestframework-stubs (mypy plugin) from S0. | — |
| Django / DRF / Channels | 5.2 LTS (to 2028-04) / 3.18.1 / 4.3.2 | Not 6.1: 5.2 LTS gets security fixes to 2028-04, covering both seasons, while 6.1's support ends around 2027-12. Transactions still do not work in async mode, so they need `sync_to_async`. | BSD |
| PostgreSQL | **17 on every cluster** | Timescale 2.30 supports PG16–18 (`timescale/timescaledb-ha:pg17`, never `-oss`). Citus 14.2 on PG17 [U: exact tag; fallback is to build FROM postgres:17]. pgvector 0.8.6 (PG13+). One major on every cluster means one set of operational skills, and PG17 is supported by Citus, Timescale and pgvector alike. PG18 (built-in `uuidv7()` [C]) is the S6 upgrade stretch drill. | PostgreSQL licence |
| TimescaleDB | 2.30 Community | CAGGs, compression, retention and `add_job` are TSL features, free to self-host unless offered as a DBaaS | TSL / Apache-2 split |
| Citus | 14.2 | Rebalancer online since 11.0 | AGPL-3.0 (matters only if modified and offered as a service) |
| Redis protocol | **Valkey 9.1** (redis-py client) | Redis 8 is also workable | Valkey BSD. Redis 8 is RSALv2/SSPLv1/AGPLv3; Valkey avoids a licence review and matches the managed clouds. |
| Search | OpenSearch 3.x | Only if adopted (S4) | Apache-2.0. Elasticsearch is AGPL/SSPL/ELv2. |
| MongoDB / driver | 8.0 / PyMongo 4.18 (`AsyncMongoClient`) | Motor reached end of life 2026-05-14 | SSPL server (internal use is fine) |
| RabbitMQ / Celery | 4.3 / 5.6.3 | Quorum queues (classic mirrored queues removed in 4.0); Native Delayed Delivery; no autoscale; `consumer_timeout`. Queues on a dead-letter path use `x-dead-letter-strategy: at-least-once` with `x-overflow: reject-publish`. **Trap:** RabbitMQ 4.3 denies transient non-exclusive queues by default, and Celery 5.6 / kombu 5.6 still declare their remote-control (pidbox) queues that way. For dev and staging, permit the deprecated `transient_nonexcl_queues` feature in `rabbitmq.conf` before the broker's first boot, as a tracked TODO to drop once a kombu fix ships. | MPL-2.0 / BSD |
| aiogram / Bot API | 3.31.0 (3.29.x yanked) / 10.3 | — | MIT |
| grpcio / buf | 1.84 (`grpc.aio` stable) / `buf.yaml` v2 | FILE breaking category by default | Apache-2.0 |
| Strawberry | 0.327 | Avoid graphene-django (stagnant) | MIT |
| Keycloak / Authlib | 26.7.4 / 1.8 + joserfc | `authlib.jose` is deprecated | Apache-2.0 / BSD |
| PgBouncer | ≥ 1.24 | Since 1.24, `max_prepared_statements` defaults to 200, so asyncpg's prepared statements work in transaction mode out of the box. To see the S10 breakage, first set it to 0 (the pre-1.24 behaviour), then restore it. | ISC |
| Object store (S3 API) | **Garage**, pinned dev image | MinIO is not used: its community images stopped in 2025 and the repository was archived in 2026, so it gets no fixes [C]. Garage speaks the S3 API, including presigned PUT/GET (verify both in S1). SeaweedFS is the fallback; in the cloud, the provider's object storage. Code uses the `ObjectStorage` port and generic `S3_*` settings. | Garage AGPLv3; SeaweedFS Apache-2.0 |
| Mail (dev) | **Mailpit**, pinned dev image | Replaces MailHog, which has been unmaintained since 2020. Its HTTP API lets a test assert "the email arrived once", and its SMTP delay/failure options serve the S4 slow-SMTP pain run. | MIT |
| Terraform | CLI | OpenTofu is a drop-in | BSL (OpenTofu MPL) |
| Ingress | Traefik (k3s default) or Envoy Gateway, through Gateway API | ingress-nginx is retired: announced 2025-11-11, with no releases or security fixes after March 2026 [C]. The community recommends Gateway API. k3s's Traefik needs its Gateway API provider enabled through a `HelmChartConfig`. | — |
| Observability | Prometheus, Grafana, Loki, **Tempo**, Alertmanager, Grafana Alloy (log shipping); Sentry SaaS | Promtail is deprecated; Alloy replaces it | Grafana stack is AGPLv3 (self-hosting is fine); Alloy Apache-2.0 |
| MCP Python SDK | 2.x (spec 2026-07-28) | v2 renamed `FastMCP` to `MCPServer`; the 2026-07-28 spec makes Streamable HTTP stateless (no session id, no `initialize`). The phase-8 D223–D227 notes are v1-era: concept reading only. Re-check at the start of S8. | MIT |
| Load tools | locust + oha | locust shapes the traffic; the reported percentiles come from a constant-rate oha probe (`--latency-correction -q`), cross-checked against server-side histograms | MIT / MIT |

**Why licences are an ADR (ADR-003).** A licence decides what you may do when you *offer* software, not only when you *run* it. Timescale's continuous aggregates exist only in the TSL (Community) build. On an `-oss` image, hypertables work, and the failure appears late: at the first continuous aggregate (`CREATE MATERIALIZED VIEW … WITH (timescaledb.continuous)`) or the first compression or retention policy, not at install time. That is the S7 "edition trap". Redis 8's licence change is why this plan uses Valkey. Keep the register updated as each store lands.

### E10. Rate limiting at every layer

The rule of thumb for the "store is down" column:
- **Fail closed** where the limiter protects security or money: OTP, AI spend.
- **Degraded fallback** for login: when redis-state is down, login falls back to the Postgres per-account `login_attempts` counter and raises an alert. That is neither fail-open nor fail-closed: the per-IP limit is lost for the window, and ADR-012 must answer "what does an attacker gain during the fallback window?".
- **Fail open, with an alert,** where it protects capacity and availability matters more: catalog, the AtlasPay API, GraphQL, bot inbound.
- **Never limit** provider callbacks. Limiting them loses payments, so they are protected by an IP allowlist and a pool bulkhead instead.

| Endpoint class | Key | Algorithm | Store | If the limiter store is down | Response | Stage |
|---|---|---|---|---|---|---|
| Login | IP + account | Sliding counter (Lua) + exponential lockout | redis-state | **Degraded fallback:** Postgres per-account `login_attempts` counter + alert; the per-IP limit is lost for the window | 429 + Retry-After, generic body | S1 (4× pain) → S3 |
| OTP send/verify | Phone + IP; attempts per OTP | Fixed window + attempt counter | redis-state | **Fail closed (503)** | 429 | S3 |
| Public catalog | IP / user | Sliding counter | redis-state | Fail open + alert | 429 | S3 |
| Nginx / gateway edge | IP; API-key id (the non-secret lookup prefix parsed from `Authorization: Bearer …`), never the full key | Leaky bucket (`limit_req` burst) | Shared memory | — | 429 JSON | S6, S10 |
| AtlasPay API | Key id × mode × tier | Token bucket (Lua) | redis-state | **Fail open** with a local per-pod bucket + alert (payment availability comes first) | 429, Retry-After, `X-RateLimit-Limit/Remaining/Reset` | S9 |
| Provider callbacks | — | **Never rate limited** (limiting them loses payments). IP allowlist + pool bulkhead instead. | — | — | — | S5, S6 |
| Outbound to providers | Provider | Token bucket | redis-state | Queue and delay | — | S5 |
| AI | User tokens/min; vendor $/day | Token bucket + budget reservation | redis-state + PG usage | **Fail closed on $** (downgrade or stop) | 429 / budget error | S8 |
| GraphQL | Client | Cost points per minute | redis-state | Fail open | Error before execution | S11 |
| Bot inbound | Telegram user | Throttle middleware | redis-state | Fail open | Silent drop / notice | S3 |
| Bot outbound | Global / chat / group | Leaky-bucket pacer + `retry_after` | redis-state | Queue, never drop | — | S4 |

**The pain path**, which is the story of your STAR "silent limiter" answers:
1. S1: an in-memory limiter becomes 4× the limit across gunicorn workers.
2. S3: that becomes 12× across 3 containers × 4 workers.
3. `INCR` then `EXPIRE` races and leaves TTL-less keys (a permanent lockout).
4. `GET`-then-`SET` over-admits.
5. Lua fixes it (S3).

The Redis Cluster failover under load is recorded against this table in S3, and repeated with a redis-state kill for API keys in S9. The algorithm comparison (fixed window, sliding log, sliding counter, token bucket, leaky bucket, on memory at 100k keys and on accuracy) lives in `docs/rate-limit-algorithms.md` (S3).

---

## 8. Conventions

These apply to every stage. The stage files assume them and do not repeat them.

### 8.1 Repository layout

```
atlas/
  services/{market,atlaspay,auth,ai,edge,bot,inventory,ledger,fraud,provider-sim}/
    edge/web/            the React SPA (S11)
  libs/{atlas-common,atlas-events,atlas-proto,atlaspay-domain,atlas-worldgen,atlas-testkit,
        atlas-fraud-features}/
  deploy/{compose,k8s/{base,overlays/{dev,staging,prod}},terraform}/
  bench/  prompts/  evals/  sandbox/  scripts/
  docs/{adr,design,runbooks,sd,evidence/sNN,postmortems,star,privacy,perf,learning}/
  docs/deferred.md  docs/hours.csv  docs/rate-limit-algorithms.md
```

Python import names use underscores (`atlas_common`, `atlas_fraud_features`, and so on). Every other fixed name is in [glossary.md](glossary.md): modules, databases, roles, Redis prefixes, buckets, queues, events, gRPC methods, HTTP paths, headers, key prefixes, namespaces, metrics and tags. Use those names exactly. Consistent names are what let you grep an event from the outbox to the consumer to the dashboard.

Atlas lives in **its own repository**, created in S0. It does not live inside this learning repo.

### 8.2 Pain-first

Most blocks start with a **pain-first exercise**. You build the naive or broken version first, run it until it fails in the way the stage predicts, and record the numbers. Only then do you fix it. Examples:
- the seq scan before any index;
- the in-memory limiter at 4×;
- the event lost when the broker dies after commit;
- the float commission that leaves the trial balance a few tiyin off.

This is not busywork. The failing run is what makes the fix *evidence* rather than a claim, and it is the most convincing part of an interview answer ("here is the plan before, here is the plan after"). Before each pain-first run, **write down your prediction and commit it**, then run. The exercise text tells you what to look at and record, not what you will see. Where the lesson is the surprise, the expected outcome sits in the stage's §16 "If you get stuck" under "Check your prediction"; open it only after your run. When the result surprises you, that surprise is a STAR story.

### 8.3 Evidence

Every "proof" in a stage file is an artifact committed under `docs/evidence/sNN/`, for example `docs/evidence/s01/`. Examples:
- an EXPLAIN plan (`EXPLAIN (ANALYZE, BUFFERS)` output as text);
- a benchmark CSV produced under the ADR-002 protocol;
- a red test turned green (the commit pair, or the test output before and after);
- a screenshot (Grafana panel, Tempo trace, Sentry issue) or a log excerpt.

Suggested naming: `<block>-<what>-<before|after>.<ext>`, for example `postgres-offset-400k-before.txt`. An ADR or a README number that does not link to an evidence file does not count.

### 8.4 ADRs

An *ADR* (architecture decision record) is a short document that records one decision: the context, the options, the choice, the numbers and the consequences. Atlas has ADR-000 to ADR-042. The index, with one line per ADR, is in [glossary.md](glossary.md#20-adr-index). ADRs live in `docs/adr/` as `ADR-NNN-slug.md`. Every extraction ADR doubles as the design doc for that split.

A short template:

```
# ADR-NNN: <decision in a few words>
Status: proposed | accepted | superseded by ADR-MMM   Stage: SNN   Date: YYYY-MM-DD
## Context          the problem, stated with numbers; links to docs/evidence/sNN/...
## Options          at least two, always including "stay as we are"
## Decision         one paragraph
## Numbers          metric | before | after | runs (ADR-002 protocol, seed, SHA)
## Counter-argument the strongest case against, stated fairly, and the answer
## Consequences     what gets harder; what number would make us revert this
```

Rules for extraction ADRs (027, 030, 031, 036, 040, 042):
- They must contain measured numbers under ADR-002, with 5 runs for the final before/after pair (intermediate configurations may use 3). These are the split-gate numbers, plus the stage's own measurements where the forcing problem is elsewhere (the flash sale for 036, posting p95 and hot-account lock waits for 040, model dependencies × replicas for 042).
- They must include the **"if the numbers don't hurt, say so"** clause, and then argue only from blast radius or security scope.
- They must state what would revert the split.

ADR-038 (edge) follows the same rules, with the Channels spike (at least 3 runs) as its gate instead of `bench/split-gate`, because edge is new code rather than a moved module.

Each stage file's §8 lists, for each ADR, the questions it must answer, the numbers it must contain and the counter-argument it must address.

### 8.5 The benchmark protocol (ADR-002)

All performance numbers in the plan come from one protocol, built in S0 in `bench/`:
- fixed container CPU and memory limits;
- a 60 s warm-up;
- at least 3 runs for intermediate configurations and 5 for the final before/after pair of an extraction ADR, reporting the median and min–max;
- locust shapes the traffic, and the reported p95/p99 come from a constant-rate oha probe (`--latency-correction -q`, HDR histograms), cross-checked against the server-side histograms;
- every result records the world-generator version and seed, the git SHA, image digests, CPU model and limits.

**Noise rule:** a difference that falls inside the run spread counts as "no difference". If you cannot reproduce a number from its recorded metadata, it is not a result.

**Wall-clock time.** A 10-minute scenario plus the 60 s warm-up is about 11 minutes per run, so a benchmark block costs configurations × runs × ~11 min of unattended time plus harness and ADR time. Four configurations at 5 runs each are almost four hours. Stage budgets include this time; schedule the runs in the weekend block.

### 8.6 The split gate (ADR-023)

`bench/split-gate` is built in S6 and re-run before every extraction (S8, S9, S10, S12). S8 and S9 re-run the full Compose gate, with chat load added in S8. From S10 the gate is ported to kind: the mid-run deploy becomes a `kubectl rollout` with the migration Job. S10 and S12 run it with the stage's forcing load: the flash sale for ADR-036, posting load for ADR-040, scoring load plus replica memory for ADR-042. The final before/after pair always uses 5 runs under ADR-002, and these runs replace the stage's own baseline runs rather than adding to them. §4 describes the scenario and what it records. One more rule: **measure the cheap fix first.** In S6, that means `/providers/*` on its own gunicorn pool. The extraction ADR must say how much of the problem the cheap fix already solved.

### 8.7 Closing a stage

Each stage ends with four things:
1. **A git tag** (v0.0 … v0.11, v1.0; see the glossary). You create it yourself when the stage's Definition of done is fully ticked.
2. **A postmortem paragraph** in `docs/postmortems/`: what you predicted, what happened, what you would do differently, and what went to `docs/deferred.md`.
3. **Two STAR stories** in `docs/star/` (S0 has one: choosing Django despite the sunk FastAPI work).
4. **The stage's system-design session**, built or on the whiteboard; see [system-design-map.md](system-design-map.md).

### 8.8 STAR stories

A *STAR story* is a behavioural interview answer in four parts: **S**ituation, **T**ask, **A**ction, **R**esult. Each stage names its two, for example the N+1 you found by counting, or the deadlock you produced. Write each one while it is fresh, in `docs/star/sNN-<slug>.md`, in under 250 words, with **one number in the Result** that links to its evidence. By the end of S12 you will have about 25 (one from S0 plus two from each of S1–S12). The Closing block in S12 picks the best 8. Use [behavioral-interview-questions.md](../../behavioral-interview-questions.md) to check which questions each story answers.

### 8.9 Keeping scope honest

- `docs/deferred.md` is started in S0. Re-read it at the start of every stage. Anything you are tempted to add goes there with the trigger that would justify it.
- Each stage file has a **Deliberately not doing** section: the item, why, and when it arrives. Treat it as part of the spec.
- Snippets in this plan are tiny and illustrative (≤ 6 lines). If a stage file seems to hand you an implementation, that is a mistake in the plan; tell the mentor.

---

## 9. How to use the old P1–P10 specs and phase files

The old specs stay untouched. Atlas cites them for **theory**: the concept explanations, the readings, the "why", the common mistakes and the interview questions. They are not a source of code.

**How to read a citation.**
- **"P5 D79–D90"** means project 5 ([05-carepoint.md](../python/05-carepoint.md)), the build stage(s) covering days 79–90. The daily plan for those days (theory reading, mini exercise, interview questions) is in the matching phase file, shown in the table below.
- **"P2 Wk7 bot extension"** means the Telegram-bot extension section of that project spec, scheduled in week 7.
- **"phase-7 D181–D215"** points straight into a Track B phase file.
- **"Proj26/27/28"** are the SD-build projects in [phase-6-capstone.md](../../phase-6-capstone.md).

| Code | Old spec | Days | Daily plan in |
|---|---|---|---|
| P1 | [01-stockpilot.md](../python/01-stockpilot.md) | D1–D24 | [phase-1-foundations.md](../../phase-1-foundations.md) |
| P2 | [02-quickserve-pos.md](../python/02-quickserve-pos.md) | D25–D39 | [phase-2-concurrency-django-caching.md](../../phase-2-concurrency-django-caching.md) |
| P3 | [03-peopleops.md](../python/03-peopleops.md) | D40–D53 | [phase-2](../../phase-2-concurrency-django-caching.md) (D40–D48) and [phase-3-distributed-systems.md](../../phase-3-distributed-systems.md) (D49–D53) |
| P4 | [04-wareflow.md](../python/04-wareflow.md) | D55–D78 | [phase-3-distributed-systems.md](../../phase-3-distributed-systems.md) |
| P5 | [05-carepoint.md](../python/05-carepoint.md) | D79–D90 | [phase-4-microservices-infra.md](../../phase-4-microservices-infra.md) |
| P6 | [06-ledgerbase.md](../python/06-ledgerbase.md) | D91–D108 | [phase-4-microservices-infra.md](../../phase-4-microservices-infra.md) |
| P7 | [07-fleettrack.md](../python/07-fleettrack.md) | D109–D120 | [phase-5-scaling-architecture.md](../../phase-5-scaling-architecture.md) |
| P8 | [08-docuvault.md](../python/08-docuvault.md) | D121–D132 | [phase-5-scaling-architecture.md](../../phase-5-scaling-architecture.md) |
| P9 | [09-payflow.md](../python/09-payflow.md) | D145–D156 | [phase-6-capstone.md](../../phase-6-capstone.md) |
| P10 | [10-atlasmarket.md](../python/10-atlasmarket.md) | D157–D168 | [phase-6-capstone.md](../../phase-6-capstone.md) |
| Proj26–28 | SD builds (URL shortener, rate limiter, job scheduler) | D169–D178 | [phase-6-capstone.md](../../phase-6-capstone.md) |
| Track B | LLM, AI dev tools, ML, MLOps, DE | D181–D366 | [phase-7](../../phase-7-llm-zoomcamp.md), [phase-8](../../phase-8-ai-devtools-zoomcamp.md), [phase-9](../../phase-9-ml-zoomcamp.md), [phase-10](../../phase-10-mlops-zoomcamp.md), [phase-11](../../phase-11-data-engineering-zoomcamp.md) |

**Rules.**
1. **Read the cited theory days before the block that needs them**, not all at once. A weekday session is the right place. Read the "Theory" and "Reading" columns of the daily plan and the concept sections of the spec.
2. **Never copy code**, including code you wrote yourself for an old project. The domain, the stack (often FastAPI there, Django here) and the constraints differ. Copying skips the thinking the stage exists to force.
3. **Do read the old "Common mistakes" and "Interview questions" sections.** They still apply, and many Atlas pain-first moments come from them.
4. **When the old spec and the Atlas stage disagree, Atlas wins.** Example: DocuVault reaches for Elasticsearch, but Atlas adopts OpenSearch only if the judged set fails. The old spec explains the concept; the Atlas stage sets the decision.
5. The reference banks stay in use: [system-design-problems.md](../../system-design-problems.md) (SD1–SD20; the Atlas mapping is in [system-design-map.md](system-design-map.md)), [behavioral-interview-questions.md](../../behavioral-interview-questions.md), [dsa-problems.md](../../dsa-problems.md) and [sql-problems.md](../../sql-problems.md) for the drill hour.

---

## 10. Working with the mentor

The mentor is Claude working in this learning repo, under the rules in its `CLAUDE.md`. It works as a senior Python, senior DevOps and senior AI/ML engineer reviewing *your* work.

**What the mentor does:**
- explains concepts and the reasons behind each step;
- asks guiding questions before giving hints;
- points you to the old-spec day to reread;
- reviews your code, tests, ADRs and evidence against the stage's acceptance criteria and invariants;
- runs through the interview questions with you;
- gives a tiny snippet (a few lines) only when that is the clearest way to show an idea or an interface shape.

**What the mentor will not do:**
- write the implementation: no full functions, Lua scripts, triggers, Dockerfiles, Kubernetes manifests, CI workflows or SQL solutions;
- commit, push or tag for you, under any circumstance. Those are always your own actions.

**Phrases that drive the workflow.**

| You say | The mentor does |
|---|---|
| "let's start stage NN" | Opens `stage-NN-*.md`, and checks that the previous stage's Definition of done is ticked and that `docs/deferred.md` has been re-read. It walks through §1–§3 with you: the problem, the outcomes and the target architecture. Then it starts block 1 by asking you to **predict** the pain-first result before you run anything. |
| "continue" | Finds the current stage (the first one whose Definition of done is not fully ticked) and the evidence already in `docs/evidence/sNN/`, then resumes at the first block whose acceptance criteria are not yet met. |
| "review block X" / "review my ADR-0NN" | Checks your work against the block's acceptance criteria, the stage invariants and the ADR's required questions, numbers and counter-argument. Flags what a senior reviewer would flag. |
| "I'm stuck on …" | Uses the stage file's §16 "If you get stuck": asks the guiding questions, then points to the specific old-spec day. It gives hints step by step, never the answer. |
| "drill" | Picks the week's SQL problem on the Atlas schema or a DSA problem from the banks, plus the stage's SD or interview questions. |
| "mock interview" | Runs the mock planned for B1, B2 or S12 (see [buffers-and-job-sprint.md](buffers-and-job-sprint.md)). |

**Tracking progress.** For Atlas, progress is tracked per stage, not per day:
- the **Definition of done** checklist at the end of each stage file (tick `[ ]` → `[x]`);
- the evidence folder;
- the stage tag in the `atlas/` repository.

The day-by-day `progress.md` belongs to the old Track A plan.

---

## 11. Files in this folder

| File | What it contains |
|---|---|
| [README.md](README.md) | This file: what Atlas is, the thesis, the evolution, the stage table, the decision tables, conventions, and how to use the old specs and the mentor |
| [glossary.md](glossary.md) | Every fixed name (repo layout, modules, databases, roles, Redis prefixes, buckets, queues, events and the envelope, gRPC, HTTP paths, headers, key prefixes, namespaces, metrics, tags) and the full ADR index |
| [stage-00-bootstrap.md](stage-00-bootstrap.md) | S0: Django orientation, workspace, image, Compose, CI and hooks, ADR-000..003, the benchmark protocol, the hours log, the worldgen skeleton |
| [stage-01-layered-monolith.md](stage-01-layered-monolith.md) | S1: Django ramp, layering, vendors and KYC, catalog, Money, the Postgres proofs, identity v1, the 4× limiter |
| [stage-02-checkout-correctness.md](stage-02-checkout-correctness.md) | S2: races, deadlock, write skew, idempotent checkout, timeouts, pricing, RLS |
| [stage-03-redis-auth-bot.md](stage-03-redis-auth-bot.md) | S3: cache and stampede, Redis operations, the limiter path to Lua, refresh families, the Cluster lab, the aiogram ramp and bot v1 |
| [stage-04-async-events-boundaries.md](stage-04-async-events-boundaries.md) | S4: Celery, RabbitMQ, outbox, consumers and CQRS, the leak hunt, notifications, bot push and the vendor bot flow, search, reviews |
| [stage-05-atlaspay-monolith.md](stage-05-atlaspay-monolith.md) | S5: provider-sim, intents and idempotency, Payme and Click adapters, ledger, Connect, payouts, reconciliation, the 12 failure scenarios |
| [stage-06-ship-and-operate.md](stage-06-ship-and-operate.md) | S6: Terraform and VPS, Nginx/TLS, CD, zero-downtime migrations, observability, Postgres operations, replica, PITR, SLOs, split gate (slice 1) |
| [stage-07-polyglot-mongo-timescale.md](stage-07-polyglot-mongo-timescale.md) | S7: JSONB vs Mongo, conversations, Timescale, the ML ramp, fraud v1 in shadow mode |
| [stage-08-ai-integration.md](stage-08-ai-integration.md) | S8: the ai split, gateway, budgets and PII, prompts and flags, SSE, RAG, product features, agent, MCP, evals (slice 2) |
| [stage-09-strangler-atlaspay-auth.md](stage-09-strangler-atlaspay-auth.md) | S9: the shadow cutover (with the fraud v1 port), API keys, versioning, webhooks, per-key limiter, Vault, market as merchant, saga, payment links from the bot, the auth service |
| [stage-10-kubernetes-grpc-inventory.md](stage-10-kubernetes-grpc-inventory.md) | S10: Kubernetes, Lease, PgBouncer, the k3s deploy, gRPC inventory, the flash sale, bot webhook and Telegram login |
| [stage-11-realtime-edge-graphql.md](stage-11-realtime-edge-graphql.md) | S11: the Channels spike, WS/SSE/long-poll, the GraphQL BFF, the React/TypeScript ramp and the SPA |
| [stage-12-data-at-scale-fraud.md](stage-12-data-at-scale-fraud.md) | S12: the Citus ledger, Mongo sharding, the fraud service, SD20 closing |
| [buffers-and-job-sprint.md](buffers-and-job-sprint.md) | B1, B2 and B3: catch-up rules, the hours-log recalibration, mocks, whiteboards, CV, demo, applications |
| [season-2.md](season-2.md) | Season 2 stages 2A–2F with their phase-file day ranges |
| [testing-and-ci.md](testing-and-ci.md) | The testing and CI growth matrix per stage, the workflow layout and required checks |
| [system-design-map.md](system-design-map.md) | Where each SD concept lives in Atlas, SD1–SD20 with timing (built vs whiteboard), the mock plan |
| [coverage-matrix.md](coverage-matrix.md) | Every requirement mapped to the stage(s) that cover it |
| [schedule-and-cuts.md](schedule-and-cuts.md) | Scenario arithmetic, risks, the stretch index, the degrade list and the never-cut spine |
