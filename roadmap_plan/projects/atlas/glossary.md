# Atlas glossary — fixed names and the ADR index

> **What this file is for.** Every stage file, ADR, test and dashboard in Atlas uses the names below, exactly as written. When you create a table, a queue, an event, a Redis key, a metric or a tag, take the name from here. Fixed names are what let you follow one checkout from the HTTP request to the outbox row, the RabbitMQ queue, the consumer, the Tempo trace and the Grafana panel with a single `grep`. If you need a name that is not listed, choose one that follows the pattern of its neighbours, and record it in your repo's docs.

Back to the [README](README.md). Decision tables E1–E10 are in the [README §7](README.md#7-decision-tables).

## Contents

1. [Core vocabulary](#1-core-vocabulary)
2. [Repository layout](#2-repository-layout)
3. [Deployables and process types](#3-deployables-and-process-types)
4. [market modules](#4-market-modules)
5. [PostgreSQL clusters, databases and roles](#5-postgresql-clusters-databases-and-roles)
6. [MongoDB](#6-mongodb)
7. [Redis: instances, key prefixes, hash tags](#7-redis-instances-key-prefixes-hash-tags)
8. [Object storage buckets](#8-object-storage-buckets)
9. [OpenSearch](#9-opensearch)
10. [RabbitMQ: exchanges, queues, parking lots, Celery queues](#10-rabbitmq-exchanges-queues-parking-lots-celery-queues)
11. [Events and the envelope](#11-events-and-the-envelope)
12. [gRPC](#12-grpc)
13. [HTTP surface](#13-http-surface)
14. [Headers](#14-headers)
15. [Key and secret prefixes](#15-key-and-secret-prefixes)
16. [Kubernetes namespaces](#16-kubernetes-namespaces)
17. [Metrics](#17-metrics)
18. [Git tags](#18-git-tags)
19. [Provider codes you will meet](#19-provider-codes-you-will-meet)
20. [ADR index](#20-adr-index)

---

## 1. Core vocabulary

These words recur in every stage file. Each is defined once here.

| Term | Meaning | First matters in |
|---|---|---|
| **Atlas** | The whole product and its monorepo `atlas/`: AtlasMarket + AtlasPay + provider-sim + bot, and later services | S0 |
| **AtlasMarket**, `market` | The multi-vendor marketplace: a Django 5.2 LTS + DRF monolith, modular from S4 | S0 |
| **AtlasPay** | The platform's own Stripe-like payment operator. It is the `payments` module inside market in S5–S8 and the `atlaspay` service from S9. | S5 |
| `atlaspay-domain` | The framework-free AtlasPay core library (`libs/atlaspay-domain`). It moves as-is to the atlaspay service in S9; only adapters are rewritten. | S5 |
| **provider-sim** | A FastAPI emulator of Payme and Click that follows each provider's real protocol, including duplicates, timeouts and lost responses. It also has an `llm` mode for CI. The fake Telegram Bot API is not part of it; it lives in `libs/atlas-testkit` (S4). | S5 |
| **Payme**, **Click** | The two Uzbek payment providers AtlasPay integrates with through adapters | S5 |
| **merchant #1** | market itself, once it pays through AtlasPay's public API like any outside merchant and learns outcomes only from signed webhooks | S9 |
| **connected account** (`acct_…`) | One AtlasPay account per vendor, next to the platform accounts. Ledger entries carry `owner_account_id`, the connected account that owns the entry. | S5 |
| **application fee** | The platform's cut of each vendor group, taken from the S1 commission schedule | S5 |
| **transfer** | Money moved to a vendor's connected account: vendor-group total − application fee | S5 |
| **tiyin** | 1/100 of a soum. All money in Atlas is an integer number of tiyin (`Money(tiyin:int, currency)`); never float. | S1 |
| **vendor group** | The per-vendor part of one order (`order_vendor_groups`), with its own price snapshot and fulfillment state machine | S2 |
| **stock hold** | A time-limited stock reservation made at checkout. It is 30 minutes, compared with Payme's 12-hour window in ADR-020. | S2, S5 |
| **trial balance** | Σdebit − Σcredit across the ledger. It is always 0. | S5 |
| **reconciliation**, **drift** | Comparing the provider's view with the ledger using a FULL OUTER JOIN. For Payme, the provider's view is a statement export from provider-sim, standing in for the Payme Business cabinet report [U]; for Click, it is `payment/status_by_mti`. A mismatched row is *drift*; drift is 0 or it raises an alert. Payme reconciles *its own* side the other way round, by calling AtlasPay's GetStatement method. | S5 |
| **world generator**, worldgen | `libs/atlas-worldgen`: a seeded, versioned generator. `history` mode writes COPY-ready rows; `traffic` mode drives locust. | S0 |
| **stage** (S0–S12), **buffer** (B1, B2, B3) | The 13 build units of Season 1 (53 weeks), plus three buffer weeks (W18, W37, W50) | — |
| **block** | One build unit inside a stage, with a must-tier hour budget in brackets, for example "Limiter [5 h]". A stage's brackets add up to its must hours. | — |
| **must** (M), **stretch** (S) | Must is the minimum to close a stage; in Season 1, M = 12 × weeks for every stage (600 h in total, the 12 h/week floor). Stretch (66 h) is done only if M closes early. | — |
| **hours log** | `docs/hours.csv`: the actual hours of every block, kept from S0. At B1 its actual/budget ratio re-plans the rest of the season. | S0 |
| **checkpoint** | B1 (W18), B2 (W37), B3 (W50). At B1, recalibrate with the hours log. More than one week behind at any checkpoint means you drop stretch, then apply the degrade list. If a spine block overruns, the date moves. | B1 |
| **degrade list** | Must-tier items that shrink to a cheaper version, applied in a fixed order ([schedule-and-cuts.md](schedule-and-cuts.md) lists each item's hours). Items that touch no explicit requirement come first; items that touch one come last and only as partial degrades. The Mongo sharded-lab and Citus rebalance-under-load items are mutually exclusive. "Degrade item 24" is the inventory extraction; its net saving is 4.5 h, because the gRPC foundation then moves to S12. | B1 |
| **never-cut spine** | The portfolio core that no schedule problem may remove ([schedule-and-cuts.md](schedule-and-cuts.md)) | — |
| **slice 1**, **slice 2** | The two early portfolio releases: v0.6 at W28 (deployed, observed, taking payments) and v0.8 at W36 (AI features) | S6, S8 |
| **pain-first** | Build the naive version first, watch it fail as predicted, record the numbers, then fix it | every stage |
| **evidence** | The artifact behind a claim, committed under `docs/evidence/sNN/`: an EXPLAIN plan, an ADR-002 benchmark CSV, a red→green test, a screenshot or a log | every stage |
| **benchmark protocol** | ADR-002: fixed limits, 60 s warm-up, ≥ 3 runs for intermediate configurations and 5 for the final before/after pair of an extraction ADR, median and min–max, p95/p99 from a constant-rate oha probe (HDR, `--latency-correction`) cross-checked against server-side histograms, full metadata. A difference inside the spread is "no difference". A 10-minute scenario costs about 11 min of wall-clock time per run, so benchmark blocks budget configurations × runs × ~11 min and run in the weekend block. | S0 |
| **split gate** | `bench/split-gate` (ADR-023): a 10-minute scripted scenario (worldgen traffic + provider-sim callback storm + one deploy with an expand migration). It is re-run before every extraction (S8, S9, S10, S12), and its numbers go into the extraction ADR. S8 and S9 run the full Compose gate. From S10 it is ported to kind (the mid-run deploy becomes a `kubectl rollout` with the migration Job) and runs with the stage's forcing load: the flash sale (S10), posting load and scoring load (S12). | S6 |
| **"numbers don't hurt" clause** | The rule that an extraction ADR whose numbers show no pain must say so and argue only from blast radius or security scope, or the split does not happen | S8 |
| **cheap fix first** | Measure the in-place fix before extracting, for example a separate gunicorn pool for `/providers/*` (S6), bucketed sub-accounts for the hot ledger account (S12), or a `market-checkout` Deployment (S10) | S6 |
| **leak hunt**, **leak count** | Counting every cross-module import that breaks the import-linter independence contracts, recording the number, then driving it to 0 | S4 |
| **deployable** vs **process type** | A deployable is a separately built and deployed service. A process type (web, worker, beat, relay, consumers, sender) is another command run from the same image. | S4 |
| **expand/contract** | A zero-downtime change done in steps: add the new shape, migrate, switch readers and writers, then remove the old shape. "Contracted away" means the old module or tables are removed. | S6, S9 |
| **strangler fig** | Replacing part of a live system by routing its traffic, piece by piece, to a new implementation until the old one can be removed | S9 |
| **shadow mode** | Two uses. In the S9 cutover, provider-sim mirrors traffic to the old and new AtlasPay and the replies are diffed byte for byte. For fraud (S7; inside atlaspay from S9), the score is stored with `model_version` and never enforced. | S7, S9 |
| **judged set** | The fixed 40 search queries with expected top hits. Each search step is scored on p95 and top-3 hits. | S4 |
| **golden set** | 30–40 eval items with recorded embeddings and a fake LLM, measuring hit@k and MRR on every PR | S8 |
| **ActionRequest** | The record the agent creates when it *proposes* a money action. After ops approve it, the refund runs once with `Idempotency-Key = ActionRequest.id`. | S8 |
| **STAR story** | A behavioural answer: Situation, Task, Action, Result (with a number). Two per stage (one in S0), in `docs/star/`. | every stage |
| **[C]**, **[U]**, **[verify]** | Confirmed from a primary source, or unconfirmed. [U] facts become settings, and the assumption is written in the test. [verify] marks a fact believed current as of 2026-09 that you re-check at the start of the stage that uses it. | S0, S5 |

---

## 2. Repository layout

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

Python import names use underscores: `atlas_common`, `atlas_events`, `atlas_proto`, `atlaspay_domain`, `atlas_worldgen`, `atlas_testkit`, `atlas_fraud_features`.

| Path | What lives there | From |
|---|---|---|
| `services/market` | The Django monolith (settings split into base/dev/prod) | S0 |
| `services/bot` | aiogram 3 Telegram client | S3 |
| `services/provider-sim` | Payme/Click emulator on its own `sim` DB | S5 |
| `services/ai` | LLM gateway, RAG, agent, MCP server | S8 |
| `services/atlaspay`, `services/auth` | The strangler extractions | S9 |
| `services/inventory` | gRPC inventory | S10 |
| `services/edge` | GraphQL BFF, WS, SSE, sessions, the long-poll comparison endpoint | S11 |
| `services/edge/web/` | The React + Vite + TypeScript SPA | S11 |
| `services/ledger`, `services/fraud` | gRPC ledger on Citus, gRPC fraud scoring | S12 |
| `libs/atlas-common` | Money, errors, structlog JSON config; built as a wheel and consumed by version | S0 |
| `libs/atlas-worldgen` | Seeded RNG, world-spec YAML, generators, `history` and `traffic` modes | S0 |
| `libs/atlas-events` | The event envelope and upcasters; built as a wheel | S4 |
| `libs/atlas-testkit` | Shared test helpers, including the fake Telegram Bot API used to test the outbound pacer | S4 |
| `libs/atlaspay-domain` | The framework-free AtlasPay core | S5 |
| `libs/atlas-fraud-features` | The one fraud feature function, as a framework-free, versioned wheel. Imported by market's `payments` module (S7–S8), the training script, atlaspay (S9) and the fraud service (S12). | S7 |
| `libs/atlas-proto` | Protobuf definitions checked by `buf lint` and `buf breaking` | S10 (S12 if degrade item 24 is applied) |
| `deploy/compose` | Compose files and per-stage profiles | S0 |
| `deploy/terraform` | VM, firewall, DNS, bucket (S6); k3s cluster (S10) | S6 |
| `deploy/k8s/base`, `deploy/k8s/overlays/{dev,staging,prod}` | Kustomize for our services (Helm only for third-party charts) | S10 |
| `bench/` | The benchmark harness (ADR-002): `bench/hello` (S0), `bench/split-gate` (S6) | S0 |
| `prompts/` | Versioned prompts, `prompts/<id>/<version>.md`; `prompt_id@version` is logged on every call | S8 |
| `evals/` | The eval harness and golden set | S8 |
| `sandbox/` | Throwaway learning code, for example `sandbox/django-ramp/` (started in the S0 Django orientation, continued in S1) | S0 |
| `scripts/` | Helper scripts, for example `scripts/compat_check.sh` (ADR-001) | S0 |
| `docs/adr/` | ADR-000 … ADR-042 | S0 |
| `docs/design/` | Design docs (every split ADR doubles as one); threat model; reconciliation doc | S5 |
| `docs/runbooks/` | For example "payment success rate dropped" and the cutover runbook | S6 |
| `docs/sd/` | System-design session write-ups | S1 |
| `docs/evidence/sNN/` | Proofs per stage | S0 |
| `docs/postmortems/` | Stage postmortem paragraphs and the drill postmortem | S0 |
| `docs/star/` | STAR stories | S0 |
| `docs/privacy/` | `data-governance.md`: PII inventory, retention, erasure | S6 |
| `docs/perf/` | Performance notes, for example `s1.md` (plans) and `blocking-email.md` (S2) | S1 |
| `docs/learning/` | Learning notes, for example `fastapi-to-django.md` (started in S0, filled in during the S1 ramp) | S0 |
| `docs/deferred.md` | The deferred list: what you left out and the trigger that would justify it; re-read at the start of every stage | S0 |
| `docs/rate-limit-algorithms.md` | The limiter algorithm comparison (README E10) | S3 |
| `docs/hours.csv` | The hours log: one row per closed block (stage, block, budget, actual, date); the input to the B1 recalibration | S0 |

Also referenced by the stage files: `docs/sd20-retro.md` (S12).

---

## 3. Deployables and process types

| Deployable | Framework | Arrives | Process types and notes |
|---|---|---|---|
| market | Django 5.2 LTS + DRF 3.18, gunicorn gthread, Celery 5.6 | S0 | `web`, `worker` (Celery), `beat`, `relay` (outbox), `consumers` from S4; the `tsdb.pay-metrics-writer` and `fraud.features` consumers in S7–S8. `/providers/*` on its own gunicorn pool (S6, until S9). A separate `market-checkout` Deployment with its own pool (S10). |
| bot | aiogram 3.31 (aiohttp webhook server) | S3 | Polling in dev; webhook in Kubernetes (S10). A `sender` process consuming `bot.notifications` (S4). |
| provider-sim | FastAPI + SQLAlchemy 2.0 async | S5 | Modes: Payme, Click, `llm`. Chaos switches: drop the response after commit, delay, duplicate, send concurrently, reorder, and (Payme) retry with a new JSON-RPC `id`. The fake Telegram Bot API lives in `libs/atlas-testkit`, not here. |
| ai | FastAPI | S8 | Main app (REST + SSE) plus a second ASGI app at `/mcp` |
| atlaspay | FastAPI + SQLAlchemy 2.0 async + Alembic | S9 | `api` (also runs the fraud v1 shadow scoring ported from market), `relay` (its own outbox), `dispatcher` × N (`atlaspay.webhook-dispatch.{n}`), `scheduler` (payouts and reconciliation, leader-elected with a Kubernetes Lease from S10), and the `tsdb.pay-metrics-writer` and `fraud.features` consumers taken over from market |
| auth | FastAPI + Authlib 1.8 + joserfc | S9 | — |
| inventory | grpc.aio | S10 | — |
| edge | FastAPI + Strawberry 0.327 | S11 | — |
| ledger | grpc.aio + SQLAlchemy Core | S12 | Consumer of `ledger.postings` |
| fraud | grpc.aio | S12 | Model loaded at startup; takes over the `fraud.features` consumer from atlaspay |

**9 production deployables** (market, atlaspay, auth, ai, edge, bot, inventory, ledger, fraud) plus provider-sim. With the full degrade list, 7 plus provider-sim remain: fraud stays in-process and inventory stays a module.

Third-party components, by arrival:
- Garage, the S3-compatible object store (S1);
- Mailpit (S2);
- Valkey (S3);
- RabbitMQ (S4), plus OpenSearch only if adopted;
- Nginx, Prometheus, Grafana, Loki, Grafana Alloy (log shipping), Tempo, Alertmanager and Sentry SaaS (S6);
- Mongo and Timescale (S7);
- Ollama (S8);
- Keycloak, Vault and Toxiproxy (S9);
- PgBouncer, Traefik or Envoy Gateway, cert-manager and External Secrets Operator or Vault Agent (S10);
- Citus (S12).

---

## 4. market modules

market modules are Django apps. **Their tables are prefixed with the app label**, for example `ordering_order` or `identity_user`. Stage files often use the short name (`stock_levels`); the physical table carries the prefix. No foreign key may cross modules; the only allowed target is `identity_user`, enforced by a `pg_constraint` test from S4.

| Module | Owns (main tables and concepts) | Arrives | Later |
|---|---|---|---|
| `identity` | Custom User (bigint PK + UUIDv7 public id, email, +998 phone, argon2), roles, `login_attempts`; refresh families, `jti` denylist and phone OTP (S3) | S1 | Token issuing moves to the auth service in S9; market keeps a shadow users table fed by `user.*` events |
| `vendors` | vendors, `vendor_staff` (membership), KYC documents (private bucket), the Admin KYC queue, the commission schedule (GiST EXCLUDE) | S1 | — |
| `catalog` | Category tree (recursive CTE with a cycle guard), products, offers, per-category JSONB attributes, images. Includes **imports** (CSV import from S4). | S1 | — |
| `inventory` | `stock_levels`, append-only `stock_movements` | S2 | Contracted away to the inventory service in S10 |
| `cart` | DB-backed cart (S2) → Redis hash with TTL, merged on login (S3) | S2 | — |
| `ordering` | Checkout, `order`, `order_vendor_groups` with price snapshots, the fulfillment state machine | S2 | The cancel-a-vendor-group saga lives here (S9) |
| `promotions` | Vendor promo codes (fixed, percent, capped), usage caps | S2 | — |
| `payments` | The in-monolith AtlasPay: intents, providers, ledger, connect, payouts, reconciliation; fraud v1 shadow scoring (S7) | S5 | Contracted away to atlaspay in S9 (the `payments_*` tables are replicated, then dropped; fraud v1 and the tsdb/fraud consumers move with it) |
| `search` | FTS (generated `tsvector`, `simple` config, transliteration column), trigram | S4 | Semantic/hybrid search with pgvector `catalog_product_embedding` (S8) |
| `reviews` | Verified-purchase reviews: a plain `order_item_id` column (no cross-module FK), checked through `ordering`'s `api.py` facade at write time, with `UNIQUE(order_item_id)`; the rating aggregator | S4 | — |
| `conversations` | Buyer↔vendor chat: Postgres JSONB with monthly partitions first, then Mongo `atlas_conversations` | S7 | Mongo sharded lab (S12) |
| `notifications` | Consumes `market.notifications`: the order confirmation email (from `order.placed`), other emails, bot push via `bot.notifications`, including the vendor-staff new-order message with its "mark shipped" button | S4 | — |
| `analytics` | Vendor sales analytics: tsdb `analytics` schema, `analytics.order_lines`, `analytics.vendor_sales_daily` | S7 | — |
| `flags` | Hash-bucket feature flags (a user always lands on the same side) | S8 | Season 2 A/B analysis |
| `outbox` | The outbox table (daily partitions via pg_partman, DEFAULT partition, BRIN, partial index `WHERE sent_at IS NULL`, `trace_context` JSONB), the relay | S4 | — |

**Deliberately not split:** catalog, cart, checkout/orders, promotions, fulfillment, vendors, reviews, search indexing, notifications, conversations, analytics (README E2).

---

## 5. PostgreSQL clusters, databases and roles

**Every cluster runs PostgreSQL 17** (ADR-001): one major on every cluster, supported by Citus, Timescale and pgvector alike, so you learn one set of operational behaviour. PG18 is the S6 upgrade stretch drill.

| Cluster | Databases | Notes | Arrives |
|---|---|---|---|
| `pg-market` | `market` (+ replica) | pgvector table `catalog_product_embedding`; streaming replica, WAL archive and PITR from S6; PgBouncer from S10 | S0 |
| `pg-sim` | `sim` | provider-sim's own state | S5 |
| `tsdb` (Timescale) | schemas `analytics`, `pay_metrics`, `fraud_features` | hypertables `analytics.order_lines`, `pay_metrics.attempts`, `fraud_features.events`; CAGGs `fraud_features.velocity_1m`, `velocity_1h`, `velocity_24h`, `analytics.vendor_sales_daily` | S7 |
| `pg-ai` | `ai` | tables `kb_chunk`, `usage_ledger`, `semantic_cache` (the pgvector similarity index for the semantic cache, filtered by permission scope and prompt version inside SQL; ADR-028) | S8 |
| `pg-atlaspay` | `atlaspay` | Filled by logical replication of `payments_*` during the S9 cutover; reachable only from atlaspay pods (NetworkPolicy, S10) | S9 |
| `pg-auth` | `auth` | | S9 |
| `pg-inventory` | `inventory` | | S10 |
| `citus-ledger` | `ledger` | distribution column `owner_account_id`. The S5 ledger triggers meet Citus in an S12 pain-first step, and ADR-040 records how they run there; `REVOKE` of UPDATE/DELETE still enforces append-only | S12 |

**Timescale image:** `timescale/timescaledb-ha:pg17`, never an `-oss` tag. `-oss` has no continuous aggregates, compression or retention policies, and the failure appears late, at the first continuous aggregate or policy, not at install time; that is the S7 edition trap. Compression runs after 7 days; retention keeps 90 days of raw data and 13 months of aggregates.

**Roles for every service:** `<svc>_app`, `<svc>_migrator`, `<svc>_ro` (for example `market_app`, `market_migrator`, `market_ro`).

| Role | Used by | Rules |
|---|---|---|
| `<svc>_app` | The running service | `NOBYPASSRLS` (S2). Per-role `lock_timeout`, `statement_timeout` and `idle_in_transaction_session_timeout` (S2). On ledger tables: append-only triggers plus `REVOKE` of UPDATE/DELETE (S5). For atlaspay, issued as dynamic credentials by Vault (S9). |
| `<svc>_migrator` | Migrations only (from S10, a pre-deploy Kubernetes Job) | Owns DDL; bypasses RLS; `lock_timeout=3s` in every migration (S6) |
| `<svc>_ro` | Read-only access, for example reporting and reconciliation queries | No writes |

Invariant from S9: **one DB role per service, and market never reads the atlaspay DB.**

Table names that appear across stage files (short names; market tables carry the app-label prefix):
- `stock_levels`, `stock_movements`, `order_vendor_groups`, `login_attempts`;
- the idempotency store (S2, generalized in S5);
- `journal_entries`, `journal_lines`, `balance_transactions`, `trial_balance_mv`, `provider_events`;
- the outbox and the inbox, `UNIQUE(consumer, event_id)`;
- `vendor_order_view`, `sagas`;
- `kb_chunk`, `usage_ledger`, `semantic_cache`, `catalog_product_embedding`.

---

## 6. MongoDB

MongoDB 8.0, driver PyMongo 4.18. Use `MongoClient` in Django and `AsyncMongoClient` in async services. Do not use Motor, which reached end of life on 2026-05-14.

| Database.collection | Owner | Arrives | Notes |
|---|---|---|---|
| `atlas_conversations.conversations` | market | S7 | 3-node replica set; multi-document transaction (message + conversation counters) needs a replica set and primary read preference |
| `atlas_conversations.messages` | market | S7 | Indexes `(conversation_id, seq)`, the unique `(conversation_id, client_msg_id)` for client dedup, TTL and partial, each checked with `explain('executionStats')`; acknowledged writes use `w:"majority"`. S12 lab: sharded and resharded to `{conversation_id: "hashed"}` while writes continue. The unique index limits which shard keys MongoDB accepts; the lab records the refusal it causes, and ADR-041 says what replaces the index under the final key. |
| `atlas_ai.transcripts` | ai | S8 | Written via `AsyncMongoClient`, redacted before write, with a TTL |

---

## 7. Redis: instances, key prefixes, hash tags

Redis protocol server: **Valkey 9.1**, client redis-py (ADR-011).

| Instance | Policy | Holds | Arrives |
|---|---|---|---|
| `redis-cache` | `allkeys-lru`, no persistence | `cache:` and `sc:` entries, and AtlasPay's cache-aside payment links: anything whose loss is only a miss. It is never a Celery broker: S4 proves a queued task vanishes there. | S3 |
| `redis-state` | `noeviction`, AOF `everysec` | Everything whose loss would break a rule: limiter counters, locks, holds, carts, OTP codes, the `jti` denylist, FSM, bot keys, budgets, WS tickets, edge streams, sessions | S3 |

Per-service use (README E2): bot and edge use redis-state only; ai uses redis-state (`budget:`) and redis-cache (`sc:`); atlaspay uses redis-state (limiter) and redis-cache (payment links); market uses both.

| Prefix | Holds | Arrives |
|---|---|---|
| `cache:` | Cache-aside entries (namespaced, versioned keys) | S3 |
| `rl:` | Rate-limiter counters and buckets (README E10) | S3 (S1 is in-memory, on purpose) |
| `lock:` | Locks: stampede single-flight (S3), the one-import-per-vendor lock with a fencing token (S4), the bot per-chat lock (S10) | S3 |
| `hold:` | Flash-sale stock holds with TTLs and fencing tokens checked in Postgres | S10 |
| `cart:` | Carts as Redis hashes with a sliding TTL: `cart:{user}` for a logged-in user (the id in a hash tag), `cart:anon:<id>` for an anonymous cart from a cookie; merged on login | S3 |
| `otp:` | Phone-OTP codes, stored hashed with a short TTL and an attempt counter | S3 |
| `jti:` | The access-token `jti` denylist; TTL = the token's remaining lifetime | S3 |
| `fsm:` | aiogram FSM state (`RedisStorage`, DefaultKeyBuilder prefix `fsm`) | S3 |
| `bot:` | Bot keys: throttle, `update_id` dedup (SET NX EX), pacer state | S3 |
| `budget:` | AI budgets: tokens/min per user, $/day per vendor (reserve-then-reconcile) | S8 |
| `sc:` | Semantic-cache answer bodies in **redis-cache**, with a TTL per entry (losing one is only a miss). An entry is identified by (normalized question, permission scope, prompt version), never by the question alone; the similarity lookup runs in the `ai` DB's `semantic_cache` pgvector table, filtered by scope and prompt version inside SQL (ADR-028) | S8 |
| `ws:stream:{user}` | edge's per-user Redis Stream, used for resume by id | S11 |
| `sess:` | Sessions (the edge BFF cookie session) | S11 |
| `wst:` | Single-use WS tickets with a TTL of a few seconds | S11 |

**Hash tags:** `{ip}`, `{api_key}` (the key id, never the secret), `{user}`. In Redis Cluster only the part inside `{}` is hashed, so every key sharing a tag lands in the same slot. That is how a multi-key Lua script avoids `CROSSSLOT`. Cluster lab: Valkey 3 masters + 3 replicas (S3).

---

## 8. Object storage buckets

| Bucket | Holds | Arrives | Access |
|---|---|---|---|
| `atlas-media` | Product images and thumbnails | S1 | Presigned |
| `atlas-kyc` | Vendor KYC documents | S1 | Private; presigned PUT/GET minted **only after authorization**, TTL ≤ 5 min |
| `atlas-imports` | Vendor CSV imports | S4 | Presigned |
| `atlas-statements` | Streaming CSV statements | S5 | Presigned |
| `atlas-wal` | WAL archive and base backups for PITR (pgBackRest or wal-g) | S6 | Backup tooling only |
| `atlas-models` | Fraud model artifacts with sha256, feature-code version and model card | S7 | Read by `payments` (S7–S8), atlaspay (S9–S11), fraud (S12) |
| `atlas-evals` | Eval sets | S8 | CI and ai |

The object store is **Garage**, an S3-compatible store with presigned PUT/GET, in dev and staging; in the cloud, the provider's object storage. SeaweedFS is the fallback. MinIO is not used: its community images stopped in 2025 and its repository was archived in 2026, so it receives no fixes [C] (as of 2026-09; re-check with `scripts/compat_check.sh`). Code talks to the store through the `ObjectStorage` port with generic `S3_*` settings, so the bucket names above never change.

---

## 9. OpenSearch

The alias `products` points to `products_v{n}`. OpenSearch is used only if the S4 judged set fails on Postgres FTS (ADR-016; OpenSearch 3.x is an S4 stretch). Reindex with `POST /search/reindex` → 202, build `products_v{n+1}`, then swap the alias. The index is derived, and a wipe-and-rebuild test proves it.

---

## 10. RabbitMQ: exchanges, queues, parking lots, Celery queues

RabbitMQ 4.3. **All queues are quorum queues** (the one exception, Celery's remote-control queues, is under *Celery queues* below). Classic mirrored queues were removed in 4.0. Every queue on a dead-letter path sets `x-dead-letter-strategy: at-least-once` with `x-overflow: reject-publish`, because the default dead-lettering is at-most-once and can drop a message; a test proves that a missing parking queue loses nothing.

**Exchanges**

| Exchange | Type / role | Arrives |
|---|---|---|
| `atlas.events` | Topic exchange for all domain events | S4 |
| `atlas.dlx` | Dead-letter exchange | S4 |
| `atlas.retry` | Retry tiers `*.retry.10s`, `*.retry.1m`, `*.retry.10m` | S4 |
| `atlaspay.webhooks` | Outbound merchant webhook dispatch | S9 |

**Queues**

| Queue | Consumer | Fed by | Arrives |
|---|---|---|---|
| `market.search-indexer` | market (the OpenSearch index and/or `catalog_product_embedding`) | `product.changed` | S4 if OpenSearch is adopted; otherwise created in S8 for the product-embedding refresh |
| `market.notifications` | market `notifications` (email and bot push) | `order.placed` (the order confirmation email, outbox-backed; `on_commit` is kept only for loss-tolerant tasks) and the other events that trigger customer or vendor emails and bot messages | S4 |
| `market.vendor-order-view` | market (CQRS projection `vendor_order_view`) | order and vendor-group events | S4 |
| `market.rating-aggregator` | market | `review.created` | S4 |
| `market.payment-events` | market | `payment_intent.*` | S5; unbound and deleted at the S9 contract step (from then on market learns outcomes only from signed webhooks) |
| `bot.notifications` | bot `sender` | outbox-fed notifications | S4 |
| `tsdb.analytics-writer` | writer into `analytics.order_lines` | order events | S7 |
| `market.chat-mongo-sync` | market (the temporary Mongo dual-write consumer) | `chat.message_sent` | S7; deleted after reads switch to Mongo and the Postgres writes stop |
| `tsdb.pay-metrics-writer` | writer into `pay_metrics.attempts`: market (S7–S8), atlaspay (S9+) | payment-attempt events | S7 |
| `fraud.features` | feature writer into `fraud_features.events`: market (S7–S8), atlaspay (S9–S11), fraud (S12) | `payment_attempt.created` | S7 |
| `ai.embedding-sync` | ai | `product.changed`, `policy.changed` | S8 |
| `atlaspay.webhook-dispatch.{n}` | atlaspay dispatcher replica `n`; merchants assigned by a consistent-hash ring with vnodes | `atlaspay.webhooks` | S9 |
| `edge.fanout` | edge → Redis Streams | `order.*`, `payment_intent.*`, `chat.*`, `vendor_group.*` | S11 |
| `ledger.postings` | ledger | atlaspay's outbox postings | S12 |

**Parking lots:** `<queue>.parking`, for example `market.notifications.parking`. A message that exhausts its retry tiers goes there, to be inspected by hand.

**Celery queues:** `emails`, `imports`, `media`, `ai-jobs`, `beat-jobs`, with one queue per task class. Celery runs on RabbitMQ with `task_default_queue_type='quorum'` and `worker_detect_quorum_queues=True`. Countdown/ETA retries rely on Native Delayed Delivery, and autoscale does not work. Celery 5.6 / kombu 5.6 declare their remote-control (pidbox) queues as transient and non-exclusive, which RabbitMQ 4.3 denies by default: dev and staging permit the deprecated `transient_nonexcl_queues` feature in `rabbitmq.conf`, as a tracked TODO to drop once a kombu fix ships (ADR-013).

---

## 11. Events and the envelope

**Envelope fields:** `event_id` (UUIDv7), `type`, `version`, `occurred_at`, `producer`, `account_id`, `trace_context`, `data`. The shape, for illustration only:

```
{"event_id": "0192…(UUIDv7)", "type": "order.placed", "version": 2,
 "occurred_at": "2026-09-23T14:00:00Z", "producer": "market",
 "account_id": "acct_…", "trace_context": {"traceparent": "00-…"}, "data": {…}}
```

- `event_id` is the dedup key. Consumers record it in an inbox table, `UNIQUE(consumer, event_id)`, in the same transaction as their own write (S4).
- `version` drives the v1 → v2 **upcaster**: old events are converted to the new shape on read (S4).
- `account_id` is the account the event concerns, for example a connected account `acct_…`.
- `trace_context` carries the W3C `traceparent` through the outbox, so a trace does not stop at "published" (S6).

| Event | Producer | Arrives | Known consumers |
|---|---|---|---|
| `order.placed` | market | S4 | `market.vendor-order-view` (projection); `market.notifications` (the order confirmation email and the vendor-staff bot message); edge (S11); Pact message contract (S4) |
| `order.cancelled` | market | S4 | inventory (S10); edge |
| `vendor_group.fulfilled` | market | S4 | Pact message contract (S4); edge |
| `vendor_group.cancelled` | market | S4 (the S9 saga cancels groups) | edge |
| `product.changed` | market | S4 | `market.search-indexer` (S4 if OpenSearch is adopted, otherwise S8); `ai.embedding-sync` (S8) |
| `stock.changed` | the inventory service | S10 | market catalog: the "in stock" flag on listings, search and the product-page cache, never checkout decisions (ADR-010) |
| `review.created` | market | S4 | `market.rating-aggregator` |
| `chat.message_sent` | market | S7 | the Mongo dual-write consumer (`market.chat-mongo-sync`, S7 only); edge (S11) |
| `policy.changed` | market | S8 | ai (knowledge base) |
| `user.registered`, `user.updated`, `user.erased` | auth | S9 | market (shadow users table) |
| `payment_attempt.created` | payments (S5); atlaspay (S9) | S5 | `fraud.features` (market S7–S8, atlaspay S9–S11, fraud S12); `tsdb.pay-metrics-writer` |
| `payment_intent.succeeded`, `payment_intent.payment_failed`, `payment_intent.canceled` | payments (S5); atlaspay (S9) | S5 | market (`market.payment-events`, S5–S8 only; from S9, signed AtlasPay webhooks instead); edge (S11); the tsdb and fraud feature writers. From S9 these events on `atlas.events` serve internal platform consumers only; the ledger consumes `ledger.postings`, not these. |
| `refund.created`, `refund.succeeded`, `refund.failed` | payments / atlaspay | S5 | also delivered to merchants as webhooks (S9) |
| `transfer.created`, `transfer.reversed` | payments / atlaspay | S5 | also webhooks (S9) |
| `payout.paid`, `payout.failed` | payments / atlaspay | S5 | also webhooks (S9) |
| `ledger.entry_posted` | ledger | S12 | — |

Topic wildcards used in the plan: `order.*`, `vendor_group.*`, `payment_intent.*`, `chat.*`, `user.*`.

---

## 12. gRPC

- Package naming: `atlas.<svc>.v1`.
- Definitions live in `libs/atlas-proto`, checked with `buf lint` (STANDARD) and `buf breaking --against '.git#branch=main'` (FILE category by default). Removed fields leave **reserved tags**.
- Runtime: grpcio 1.84, `grpc.aio`.
- Everything here arrives in S10 with inventory. If degrade item 24 is applied (inventory stays a module), `libs/atlas-proto`, the buf checks in CI, the interceptors and the status-code mapping are built in S12 with the ledger instead.

| Service | Method | Kind | Notes | Arrives |
|---|---|---|---|---|
| `atlas.inventory.v1.InventoryService` | `Reserve` | unary | Out of stock → `FAILED_PRECONDITION`; contention → `ABORTED`; deadline propagated from market | S10 |
| | `Commit` | unary | | S10 |
| | `Release` | unary | | S10 |
| | `BatchGetStock` | unary | Used by the product page | S10 |
| | `WatchStock` | server-streaming | | S10 |
| `atlas.ledger.v1.LedgerService` | `PostEntries` | unary | Idempotent by `entry_key`; the UNIQUE constraint includes the distribution column | S12 |
| | `GetBalance` | unary | Used for the synchronous check before debits (payouts, refunds) | S12 |
| | `StreamStatement` | server-streaming | | S12 |
| `atlas.fraud.v1.FraudService` | `Score` | unary | p99 ≤ 30 ms server-side; atlaspay calls with a 50 ms deadline behind a breaker | S12 |

**Rules:**
- Interceptors handle the service token, OTel and logging.
- Every RPC has a deadline no longer than the caller's remaining budget.

**Load-balancing fix in Kubernetes (S10):** a headless Service + a `dns:///…` target with `round_robin` in the service config + a server-side `max_connection_age`. All three are needed. `max_connection_age` alone does not fix it.

---

## 13. HTTP surface

| Owner | Host | Paths |
|---|---|---|
| market | `atlas.<domain>` (staging `staging.atlas.<domain>`) | `/api/v1/*` |
| atlaspay | `pay.<domain>` (staging `pay.staging.<domain>`) | `/v1/{payment_intents,refunds,transfers,payouts,accounts,webhook_endpoints,events}`, `/providers/payme/rpc`, `/providers/click/{prepare,complete}`, `/l/{code}` |
| auth | `atlas.<domain>` | `/oauth2/{authorize,token}`, `/.well-known/{openid-configuration,jwks.json}`, `/oidc/{provider}/{start,callback}`, `/telegram/login` |
| ai | `atlas.<domain>` (public paths routed to ai by path); `/v1/embeddings` is internal only | `/v1/assistant/ask` (SSE), `/v1/descriptions/jobs`, `/mcp`; internal `/v1/embeddings` |
| edge | `atlas.<domain>` | `/graphql`, `/ws`, `/sse/*`, `/poll/*` (long-poll comparison endpoint, S11), `/session/*` |

`<domain>` is the public domain you register in S6. AtlasPay has its own host, the way a payment operator's API host is separate from any merchant's site, so its public API, provider callbacks and payment links never share a path prefix with ai's `/v1/*` routes. Until S9, the `payments` module inside market serves `/providers/*` on its own gunicorn pool; the S9 route switch sends `pay.<domain>` to atlaspay as a whole (when provider-sim's callback URLs move to `pay.<domain>` is an S9 decision). From S10 the Gateway routes by host.

What each path is for:

| Path | Purpose | Arrives |
|---|---|---|
| `/api/v1/*` (market) | Public catalog, customer, vendor and ops REST (DRF), next to Django Admin and the internal REST used by bot, ai and edge. market also receives signed AtlasPay webhooks (S9), its only source of payment, refund and payout outcomes from then on. | S1 |
| `/providers/payme/rpc` | Payme JSON-RPC callbacks: always HTTP 200; outside DRF's default auth, CSRF and HTML error pages | S5 (served by market's `payments` until S9; own gunicorn pool from S6) |
| `/providers/click/prepare`, `/providers/click/complete` | Click form-urlencoded Prepare (action=0) and Complete (action=1) | S5 (same) |
| `/v1/payment_intents`, `/v1/refunds`, `/v1/transfers`, `/v1/payouts`, `/v1/accounts` | AtlasPay's public merchant API on `pay.<domain>`: `sk_`/`rk_` keys sent as `Authorization: Bearer`, `Idempotency-Key`, `Atlas-Version` | S9 |
| `/v1/webhook_endpoints`, `/v1/events` | Merchant webhook configuration and the event log | S9 |
| `/l/{code}` | AtlasPay payment links: base62 codes, cache-aside in redis-cache, a deleted code returns 404 (SD1). The bot sends one as an inline URL button for an order that is `awaiting_payment` (S9). | S9 |
| `/oauth2/authorize`, `/oauth2/token` | Authorization Code + PKCE; client credentials for services | S9 |
| `/.well-known/openid-configuration`, `/.well-known/jwks.json` | Discovery and the RS256 public keys (with `kid`) | S9 |
| `/oidc/{provider}/start`, `/oidc/{provider}/callback` | Federation to Keycloak and Google, validating state, nonce, iss, aud and signature | S9 |
| `/telegram/login` | Telegram Login Widget verification: HMAC-SHA256 keyed with SHA256(bot_token), plus an `auth_date` freshness check | S10 |
| `/v1/assistant/ask` | Streamed RAG answers over SSE; a client disconnect cancels the upstream stream and stops billing | S8 |
| `/v1/descriptions/jobs` | Vendor product-description jobs (called from market's Celery `ai-jobs` queue) | S8 |
| `/v1/embeddings` | Internal embeddings endpoint: market calls it for product vectors (the `market.search-indexer` consumer) and query vectors. Service token only; never routed publicly, so the public host returns 404 for it. | S8 |
| `/mcp` | MCP server over stateless Streamable HTTP (spec 2026-07-28, Python SDK 2.x; re-check at stage start), with read-only tools, resources and prompts. Validates the `Origin` header. Static scoped token in S8, Keycloak OAuth from S9; stdio for local use. | S8 |
| `/graphql` | Strawberry GraphQL BFF (queries, subscriptions over `graphql-transport-ws`) | S11 |
| `/ws`, `/sse/*` | Live order/payment status, dashboard and chat; SSE with `Last-Event-ID` | S11 |
| `/session/*` | The BFF cookie session; edge is the confidential OIDC client | S11 |

provider-sim also emulates the providers' own surfaces:
- the Payme checkout page `/<base64(m=;ac.order_id=;a=)>`;
- the Payme side of reconciliation: the sim *calls* AtlasPay's GetStatement nightly, and exports its own records as the statement AtlasPay reconciles against (standing in for the Payme Business cabinet report [U]);
- Click's `/v2/merchant/*`, which AtlasPay calls for status and reversals.

Before the ai split, S8's pain-first exercise builds a sync streaming view `/assistant/ask` inside market. It exists only to be measured and replaced.

---

## 14. Headers

**Headers Atlas defines or uses**

| Header | Direction | Meaning | Arrives |
|---|---|---|---|
| `Authorization: Bearer sk_…` (or `rk_…`, `pk_…`) | merchant → AtlasPay | How a merchant, including market, presents its API key (the Stripe convention). The edge rate-limit zones and the per-key limiter key on the key id (the non-secret lookup prefix), never on the full key. | S9 |
| `Idempotency-Key` | client → server, on every POST that creates something | One key means one result. The key is stored once execution starts (including 500s); different parameters with the same key → error; still in flight → 409; kept ≥ 24 h. | S2 (checkout), S5 (AtlasPay semantics) |
| `Idempotent-Replayed` | server → client | `true` when the response is a replay of the stored one | S5 |
| `Atlas-Signature` | AtlasPay → merchant webhook | `t=…,v1=HMAC-SHA256(t.raw_body)`; 5-minute tolerance; two valid secrets during rotation; verified before parsing | S9 |
| `Atlas-Version` | merchant → AtlasPay | A dated API version, pinned per merchant at key creation; old versions served through response transforms; `Deprecation` and `Sunset` headers announce removal | S9 |
| `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` | server → client | Per-key token-bucket state on the AtlasPay API | S9 |
| `Retry-After` | server → client | Sent with 429 | S3 |
| `X-Request-ID` | entry point → every hop | Request correlation id, carried in structlog next to `trace_id` | S6 |
| `traceparent` | every hop | W3C trace context. Stored in the outbox `trace_context` and passed as AMQP headers so traces cross the broker. | S6 |
| `X-Telegram-Bot-Api-Secret-Token` | Telegram → bot webhook | Proves the update came from Telegram. Rely on it, not on the leftmost `X-Forwarded-For`. | S10 |

**Headers set by the providers** (AtlasPay verifies them; it does not define them):

| Header | From | Meaning |
|---|---|---|
| `Authorization: Basic base64(Paycom:<key>)` | Payme → AtlasPay | Payme's merchant auth; compare in constant time; failure → -32504. Content-Type `text/json`. |
| `Auth: user:sha1(ts+secret):ts` | AtlasPay → Click `/v2/merchant/*` | Click Merchant API auth |

Click's Shop API signs the *body* (`sign_string`, MD5 over the raw received strings) instead of using a header.

---

## 15. Key and secret prefixes

| Prefix | What | Notes |
|---|---|---|
| `pk_test_`, `pk_live_` | Publishable keys | Safe to expose to a browser |
| `sk_test_`, `sk_live_` | Secret keys | Full access for the merchant. market uses an `sk_` key as merchant #1 from S9. |
| `rk_test_`, `rk_live_` | Restricted keys | Scoped to a subset of operations |
| `whsec_` | Webhook signing secrets | Two valid during rotation |

Rules (S9):
- Keys are stored as SHA-256 plus a pepper, with a prefix lookup. bcrypt is not used, because the keys are high-entropy.
- Rotation has a grace period.
- A live key never touches test objects (livemode isolation).
- Keys arrive as `Authorization: Bearer <key>` (§14).
- The per-key limiter keys on key id × mode × tier; the key id (the lookup prefix) is what appears in Redis key names and Nginx/gateway zones, never the secret.

---

## 16. Kubernetes namespaces

| Namespace | Used for |
|---|---|
| `atlas-dev` | Local development on kind (`overlays/dev`) |
| `atlas-staging` | Deployed automatically by CD from GHCR (`overlays/staging`) |
| `atlas-prod` | Deployed with approval, the same SHA as staging (`overlays/prod`) |
| `atlas-labs` | Lab and experiment workloads that are not part of the product, when you run them on Kubernetes |

Cluster state comes only from git. The deploy ServiceAccount is scoped.

---

## 17. Metrics

Prometheus naming: `_total` is a counter; `_seconds` is a duration, a histogram for latencies and a gauge for lags. **No high-cardinality labels** (no user ids, order ids or raw paths).

| Metric | Measures | Arrives | Used for |
|---|---|---|---|
| `outbox_lag_seconds` | Age of the oldest unsent outbox row | S4 | Alertmanager rule fired and resolved in S6; the S6 relay-kill drill |
| `webhook_delivery_lag_seconds` | Delay between an AtlasPay event and a successful merchant webhook delivery | S9 | Webhook delivery health (retry tiers, DLQ) |
| `recon_drift_rows` | Rows where the provider statement and the ledger disagree | S5 | Alerts whenever it is non-zero |
| `checkout_success_total` | Successful checkouts | S6 | Checkout-success SLO and error budget |
| `provider_callback_seconds` | Latency of Payme/Click callback handling | S6 | Callback-latency SLO; split-gate callback p99 |
| `llm_cost_usd_total` | LLM spend in dollars | S8 | Budgets, the AI cost model, dashboards |
| `llm_ttft_seconds` | Time to first token | S8 | Gateway timeouts and fallback tuning |
| `fraud_score_seconds` | Fraud scoring latency | S7 (in-process, shadow); S12 (fraud service) | The 50 ms deadline and latency panel; ADR-042's in-process vs service comparison |

---

## 18. Git tags

Tags run v0.0 … v0.11 and v1.0, one per stage. You create each tag yourself when the stage's Definition of done is fully ticked.

| Tag | Stage | What must be true (short form of "Done when") |
|---|---|---|
| v0.0 | S0 | A clean clone runs `compose up`; CI is green; `bench/hello` has 3 runs recorded |
| v0.1 | S1 | Ops approves a vendor; the vendor uploads a product and image; the 1M-row catalog pages by keyset with p95 recorded |
| v0.2 | S2 | A two-terminal race gives 201 + 409; the promo race holds; the RLS leak test passes; the email numbers are recorded |
| v0.3 | S3 | Cold/warm p95 recorded; the stampede fix holds under locust; the limiter holds across 12 processes; the failover table is filled in; the bot links an account and tracks an order |
| v0.4 | S4 | Checkout p95 before/after moving email to Celery; killing the broker and a relay loses 0 events; the leak count recorded, then 0; the judged-set table filled in |
| v0.5 | S5 | Intent → simulated Payme checkout → Perform → order paid → transfers and fees posted → trial balance 0; the chaos run is green; an injected drift is flagged |
| v0.6 | S6 (**slice 1**) | Public HTTPS URL; dashboard; one checkout trace end to end; a deploy under load with 0 errors; the restore log; README with numbers |
| v0.7 | S7 | Both ADRs have numbers; chat on Mongo survives a primary kill; velocity rules run on CAGGs; shadow scores are stored |
| v0.8 | S8 (**slice 2**) | A streamed, cited answer; a leakage attempt refused; an agent-proposed refund executed exactly once after approval; an MCP client querying an order; the eval report |
| v0.9 | S9 | The cutover rehearsal log; diff = 0; the acceptance suite green against atlaspay; shadow fraud scores still recorded for 100% of attempts; `market.payment-events` deleted; Keycloak and Google login and rotation under locust |
| v0.10 | S10 | A cloud staging URL on k3s; a rollout under load with 0 errors; exactly 1,000 units sold; the per-pod spread table; the bot answering on its webhook |
| v0.11 | S11 | The live dashboard works across pods; chat resumes after a reconnect; the product list takes 2 downstream calls (51 → 2) and the full product page ≤ 3; Playwright is green |
| v1.0 | S12 | A rebalance under load with 0 failed postings; the resharded chat; fraud in the payment path with its fallback shown; SD20 retro written |

---

## 19. Provider codes you will meet

These come from the providers' public documentation. [U] items are unconfirmed and are simulator settings in provider-sim. Full detail is in [Stage 05](stage-05-atlaspay-monolith.md).

**Payme (JSON-RPC 2.0; always HTTP 200)**

| Code / value | Meaning |
|---|---|
| -32400 | System error. Also what Payme records when the merchant answers with any non-200 status, for example a DRF 401 or an HTML 500 (failure scenario 7). |
| -32504 | Insufficient privileges (auth failed) |
| -31001 | Wrong amount |
| -31003 | Transaction not found |
| -31007 | Cannot cancel: goods already delivered (returned for Cancel after Perform if the order has shipped) |
| -31008 | Operation not possible in the current state (including a timed-out transaction) |
| -31050..-31099 | Invalid `account` input. The sandbox expects -31008, not -31050, for a new transaction on an order already awaiting payment; the official template disagrees (failure scenario 2). |
| states 1 / 2 / -1 / -2 | Created / completed / cancelled from created / cancelled after completion |
| 43,200,000 ms | The 12-hour timeout. Which timestamp starts the clock is **[U]**. |
| ids, times | Transaction ids are 24-character strings; timestamps are 13-digit milliseconds (UTC); amounts are integer tiyin |

**Click (Shop API, form-urlencoded, MD5 `sign_string`)**

| Code / value | Meaning |
|---|---|
| action=0 / action=1 | Prepare / Complete |
| -1 | Sign check failed |
| -4 | Already paid (a repeated Complete returns -4, unlike Payme, which replays success) |
| -6 | Transaction does not exist (bad `merchant_prepare_id`) |
| -9 | Transaction cancelled (the merchant's answer whenever Click sends a negative `error`) |
| -5017 | Used by Click's test scenarios in Complete for a failed or cancelled payment; its exact meaning is **[U]** |
| amount | Sent in soums as a string. Its exact format is **[U]**, so compute MD5 over the raw received string and convert to integer tiyin with Decimal. |

---

## 20. ADR index

ADRs live in `docs/adr/ADR-NNN-slug.md`. The template and the rules for extraction ADRs are in the [README §8.4](README.md#84-adrs). Each stage file's §8 lists what each of its ADRs must answer.

| ADR | Topic | Stage | The decision it records |
|---|---|---|---|
| 000 | Framework / monorepo | S0 | market is a Django monolith in a uv-workspace monorepo, against the counter-argument of the sunk FastAPI D1–D5 work, which is reused in provider-sim, atlaspay and ledger |
| 001 | Pins and compatibility | S0 | The version pins in E8 and `scripts/compat_check.sh`, which pulls every image, prints server and extension versions and flags the [U] tags; includes why Python 3.13 and PG17 stay, and the object store (Garage by default, SeaweedFS fallback; MinIO is archived) |
| 002 | Benchmark method | S0 | The one measurement protocol: fixed limits, 60 s warm-up, 3 runs for intermediate configurations and 5 for the final before/after pair, median and min–max, p95/p99 from a constant-rate oha probe cross-checked against server-side histograms, full metadata, the noise rule, and the wall-clock cost per run |
| 003 | Licences | S0 | The licence register (E8), updated as each store lands: Valkey over Redis 8, the Timescale TSL/`-oss` split, Citus AGPL, Mongo SSPL, Terraform BSL vs OpenTofu |
| 004 | Layering | S1 | views → services/selectors → ORM, enforced by an import-linter layers contract; ports as Protocols; a manual composition root |
| 005 | IDs | S1 | A bigint primary key plus a UUIDv7 public id, backed by the v7 vs v4 insert-speed and index-size benchmark at 1M rows |
| 006 | Money | S1 | Money as integer tiyin in a frozen value object with a `MoneyField` descriptor, and the rounding rules |
| 007 | Isolation | S2 | Which isolation level and locking strategy each write operation uses, for example SERIALIZABLE with a jittered retry on 40001 for the promo cap |
| 008 | Idempotency store | S2 | The idempotency store is Postgres (`INSERT … ON CONFLICT DO NOTHING RETURNING` with a request hash), not Redis, which is not transactional with the order, is evictable and loses data on restart |
| 009 | Multi-tenancy | S2 | Shared schema + RLS (`SET LOCAL app.vendor_id`, NOBYPASSRLS app role) rather than a schema or database per tenant |
| 010 | Cache policy | S3 | Cache-aside with namespaced, versioned keys, delete-after-commit invalidation, stampede protection, and the never-cached list (stock used for decisions, balances, payment and order state) |
| 011 | Redis topology | S3 | Two instances (redis-cache: allkeys-lru, no persistence, for anything whose loss is a miss; redis-state: noeviction, AOF everysec, for anything whose loss breaks a rule), and Valkey 9.1 over Redis 8 |
| 012 | Rate limiting | S3 | Rate limiting per layer (E10): algorithm, key, store and fail-open, fail-closed or degraded fallback per endpoint class (login degrades to the Postgres per-account counter with an alert; the ADR answers "what does an attacker gain during the fallback window?"), with the Cluster failover results |
| 013 | Broker | S4 | RabbitMQ with quorum queues over the Redis broker, Kafka and Redis Streams, including the RabbitMQ 4.3 deprecated-feature permit for Celery's pidbox queues |
| 014 | Outbox | S4 | The transactional outbox and delivery semantics: at-least-once, inbox dedup, two relays with SKIP LOCKED, partitioned retention; the order confirmation moves to `order.placed` → `market.notifications`, and `on_commit` stays only for loss-tolerant tasks |
| 015 | Module map | S4 | The module map and boundary rules (api.py facades, events, no cross-module FKs), including the leak count |
| 016 | Search | S4 | Postgres FTS + trigram + transliteration, or OpenSearch, decided by the 40-query judged set. If Postgres passes, "OpenSearch not adopted". |
| 017 | AtlasPay domain | S5 | The Stripe-shaped AtlasPay domain (intents, attempts, idempotency, Connect), with the legal note that under ЗРУ-578 Art. 15 a real AtlasPay needs a Central Bank licence or would use the providers' own splits (Payme `receivers`, Click Split Shop) |
| 018 | Adapters / simulator | S5 | The provider adapter contract and how faithful provider-sim must be, including which [U] facts are settings |
| 019 | Ledger / Connect | S5 | The double-entry ledger (deferred constraint trigger, append-only, reversal-only corrections, event-sourced rebuild) and the Connect model (separate charges and transfers, proportional refund reversal with largest-remainder rounding) |
| 020 | Hold window | S5 | How the 30-minute stock hold coexists with Payme's 12-hour transaction window |
| 021 | Deploy / region | S6 | The deploy topology (Terraform VPS, Nginx, health-gated swap, same SHA staging → prod) and the region: EU is acceptable for synthetic data, while a real launch probably must keep Uzbek citizens' personal data in Uzbekistan [U] |
| 022 | SLOs | S6 | SLOs for checkout success and callback latency, derived from measurements, with error budgets and an alert per SLO |
| 023 | Split gate | S6 | The split-gate protocol and its baseline numbers, including the cheap fix measured first (`/providers/*` pool), the 3-vs-5-run rule and the kind port used from S10 |
| 024 | JSONB vs Mongo | S7 | JSONB vs Mongo for both workloads: attributes stay in JSONB; conversations move to Mongo because they are document-shaped, append-only, TTL, accessed per conversation, and will need to scale out in S12. It states honestly that Postgres partitions were adequate up to the measured scale. |
| 025 | Timescale | S7 | Timescale vs matview vs Prometheus for velocity features, payment metrics and vendor sales series |
| 026 | Fraud v1 | S7 | Fraud v1: synthetic labels with label delay, one feature function (`libs/atlas-fraud-features`), a point-in-time training set, logistic regression (the HistGradientBoosting comparison, precision@k and calibration are stretch), PR-AUC and a cost threshold, shadow scoring in-process |
| 027 | ai split | S8 | Extracting ai as the first split (worker exhaustion from streaming, plus the keys/PII/budget boundary), with the "if the numbers don't hurt" clause and the HS256 mint finding |
| 028 | Vector store | S8 | pgvector over Qdrant or OpenSearch kNN: a separate vector DB is not needed below about 10M vectors. Also the semantic cache: the similarity index in pgvector (scoped inside SQL), the answer bodies under `sc:` in redis-cache |
| 029 | Agent authority | S8 | What the agent may do: it acts with the caller's delegated token, proposes money actions as ActionRequests, and never executes them without approval |
| 030 | AtlasPay split | S9 | Extracting AtlasPay as a FastAPI service. Evidence: lock-stall callback p99, the S6 pool-bulkhead result, secrets scope, the SLO gap, operator neutrality. It argues against "extract it as a Django service" and includes "if the numbers don't hurt, say so". |
| 031 | Auth split | S9 | Extracting auth for issuer neutrality across trust domains, the new OIDC/PKCE/MCP-client surface and blast radius (RS256 alone does not need a split), against "buy Keycloak or Auth0". It says honestly that the S6 refresh slowdown was indirect (shared market-web threads and DB pool) and that a separate pool would cure it |
| 032 | Keys / versioning / webhooks | S9 | Merchant key types and storage, dated `Atlas-Version` pinning with oasdiff, and signed webhooks with rotation, delay tiers and a hash-ring dispatcher |
| 033 | Secrets / governance | S9 | Vault (KV, dynamic credentials, transit) and data governance: erasure vs the append-only ledger, event logs, transcripts and embeddings; erasure as crypto-shredding |
| 034 | No 2PC | S9 | Why the cancel-a-vendor-group flow is an orchestrated saga with compensations rather than two-phase commit |
| 035 | Kubernetes | S10 | Moving from Compose to Kubernetes (kind + k3s), with the Compose container count as the evidence that Compose stopped coping |
| 036 | Inventory split | S10 | Extracting inventory over gRPC, only after the monolith flash-sale numbers, the Redis gate and the `market-checkout` Deployment; answers the "one local transaction is oversell-proof" counter and states the revert numbers |
| 037 | Transport | S10 (v1), S11 (v2) | REST vs gRPC vs GraphQL per interaction (E4): v1 with the REST vs gRPC p50/p95 comparison; v2, finalized in S11 (must), with the GraphQL numbers |
| 038 | Edge / BFF | S11 | Creating edge (FastAPI) for sockets, composition and the BFF session: the Channels socket-drop numbers, the product-page waterfall and BFF security vs a public PKCE SPA client |
| 039 | GraphQL | S11 | Strawberry over Graphene, with DataLoaders per request, cost limits, persisted queries in prod and field-level auth |
| 040 | Ledger + Citus | S12 | Extracting the ledger to Citus, labelled the most debatable split and revertible: hot account fixed in place first, the 2PC cost of the naive key, the `owner_account_id` redesign, how the S5 ledger triggers run on Citus; says so if single-node suffices |
| 041 | Sharding | S12 | Shard keys and tools across Atlas: Citus vs app-level routing for the ledger, Mongo shard keys (and what replaces the S7 unique index under the final key), Redis Cluster, and why orders and payment_intents are not sharded |
| 042 | Fraud serving | S12 | Serving fraud as a gRPC service (model deps × replicas, separate deploy cadence, testable fallback) against the lower latency of in-process scoring, plus the model card |
