# Requirements coverage matrix

| | |
|---|---|
| **Covers** | Every bullet of the requirements collected on 2026-09-23 (R1–R41), split into sub-items, each mapped to the stage that delivers it and the exact section of the stage file where it is specified |
| **How to read a link** | `§4.N` is block N of section "4. Build plan" in a stage file, and the link opens that block (for example *S3 §4.4 · Limiter*); text in brackets after the block name says which part of the block. `§6` is "Tests to write", `§7` is "CI changes", `§8` is "ADRs and documents", `§14` is "Stretch", `§15` is "Definition of done". |
| **Status** | No requirement bullet is unaddressed in the must tier. Section 4 lists the limits of the setup, which are not gaps. Section 5 lists which rows each degrade item weakens, and [schedule-and-cuts §4](schedule-and-cuts.md#4-scenario-arithmetic) shows which degrades your measured hours ratio makes likely. |

> **What this matrix is for.** It is the contract check between what you asked for and what the plan delivers. Use it three ways: before a stage, to see which requirements that stage carries (section 3 is the reverse index); during an interview prep, to find where a technology is practised; and at the end of Season 1, to tick every row against the evidence in `docs/evidence/`.

Stage files: [S0](stage-00-bootstrap.md) · [S1](stage-01-layered-monolith.md) · [S2](stage-02-checkout-correctness.md) · [S3](stage-03-redis-auth-bot.md) · [S4](stage-04-async-events-boundaries.md) · [S5](stage-05-atlaspay-monolith.md) · [S6](stage-06-ship-and-operate.md) · [S7](stage-07-polyglot-mongo-timescale.md) · [S8](stage-08-ai-integration.md) · [S9](stage-09-strangler-atlaspay-auth.md) · [S10](stage-10-kubernetes-grpc-inventory.md) · [S11](stage-11-realtime-edge-graphql.md) · [S12](stage-12-data-at-scale-fraud.md) · [buffers](buffers-and-job-sprint.md) · [Season 2](season-2.md)

---

## 1. The matrix

### 1.1 Who, constraints and structure (R1–R9)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R1 | Full-time job, 12–15 h/week, honest hours | C (53 weeks; must tier = 12 h/week floor; hours log from S0, re-plan with the measured ratio at B1, B2, B3), J scenarios | [schedule §1 · budget](schedule-and-cuts.md#1-the-budget), [§2 · weekly rhythm](schedule-and-cuts.md#2-weekly-rhythm), [§4 · scenario arithmetic](schedule-and-cuts.md#4-scenario-arithmetic), [§5 · checkpoints](schedule-and-cuts.md#5-checkpoints); the Hours row of every stage header |
| R2 | Currently at Day 5 of FastAPI + SQLAlchemy async; reuse that work | ADR-000; S5 (sim), S9 (atlaspay), S12 (ledger) | [S0 §8 · ADR-000](stage-00-bootstrap.md#8-adrs-and-documents), [S5 §4.1 · provider-sim](stage-05-atlaspay-monolith.md#41-provider-sim-14-h-must), [S9 §4.2 · Strangler](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must), [S12 §4.1 · Ledger on Citus](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R3 | Middle+ profile; confident; understands the WHY of each step | Proofs in every stage, ADRs with numbers, split gate (S6+) | §2 Outcomes and §8 ADRs of every stage; [S6 §4.11 · Split gate + bulkhead](stage-06-ship-and-operate.md#411-split-gate--bulkhead-45-h-must); [design docs per split](system-design-map.md#7-design-docs-per-split) |
| R4 | The plan is a spec, never full solution code | All of D (snippets only) | [README](README.md) conventions; §4 of every stage (requirements, not code) |
| R5 | English; old 10 specs untouched and cited with P#/D# | All stages | The "Old-spec theory to read" row of every stage header, and §16 "If you get stuck"; [the old specs in ../python/](../README.md) |
| R6 | One monorepo; monolith → microservices step by step | B, C, L | [README](README.md) evolution storyline and stage table; [glossary](glossary.md) repository layout; §3 Architecture of every stage |
| R7 | Two seasons on the same project and the same data | C, I, worldgen (S0 → S12) | [Season 2 §3 · worldgen data contract](season-2.md#3-the-worldgen-data-contract); [S0 §4.6 · Measurement](stage-00-bootstrap.md#46-measurement-55-h), [S1 §4.8 · Worldgen v1](stage-01-layered-monolith.md#48-worldgen-v1-3-h), [S2 §4.1 · Domain](stage-02-checkout-correctness.md#41-domain-75-h), [S7 §4.3 · Fraud v1](stage-07-polyglot-mongo-timescale.md#43-fraud-v1-7-h-must), [S12 §4.1 · Ledger on Citus](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R8 | Season 1 = backend + AI integration | S0–S12 | [README](README.md) stage table; AI in [S8](stage-08-ai-integration.md) |
| R9 | Season 2 = ML/DS/MLOps/DE on phase-7..11, outlined at stage level | I | [Season 2 §4 · stage map](season-2.md#4-stage-map) |

### 1.2 Domain (R10–R13)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R10.1 | Marketplace: catalog | S1 | [S1 §4.4 · Catalog](stage-01-layered-monolith.md#44-catalog-65-h) |
| R10.2 | Inventory | S2, S10 | [S2 §4.1 · Domain](stage-02-checkout-correctness.md#41-domain-75-h), [S10 §4.5 · gRPC inventory](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must) |
| R10.3 | Cart and checkout | S2, S3 | [S2 §4.1 · Domain](stage-02-checkout-correctness.md#41-domain-75-h), [S3 §4.3 · Cart](stage-03-redis-auth-bot.md#43-cart-15-h-must) |
| R10.4 | Orders | S2 | [S2 §4.1 · Domain](stage-02-checkout-correctness.md#41-domain-75-h) |
| R10.5 | Fulfillment | S2, S4 | [S2 §4.1 · Domain](stage-02-checkout-correctness.md#41-domain-75-h), [S4 §4.4 · Consumers and CQRS](stage-04-async-events-boundaries.md#44-consumers-and-cqrs-5-h-must) |
| R10.6 | Vendor payouts | S5, S12 | [S5 §4.8 · Payouts](stage-05-atlaspay-monolith.md#48-payouts-3-h-must), [S12 §4.1 · Ledger on Citus](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R10.7 | Search | S4, S8 | [S4 §4.7 · Search](stage-04-async-events-boundaries.md#47-search-5-h-must), [S8 §4.7 · Product features](stage-08-ai-integration.md#47-product-features-45-h-must) |
| R10.8 | Reviews | S4 | [S4 §4.8 · Reviews](stage-04-async-events-boundaries.md#48-reviews-2-h-must) |
| R11.1 | AtlasPay: PaymentIntent-style lifecycle | S5 | [S5 §4.2 · Intents and idempotency](stage-05-atlaspay-monolith.md#42-intents-and-idempotency-6-h-must) |
| R11.2 | Idempotency-Key | S2, S5 | [S2 §4.4 · Idempotent checkout](stage-02-checkout-correctness.md#44-idempotent-checkout-45-h), [S5 §4.2 · Intents and idempotency](stage-05-atlaspay-monolith.md#42-intents-and-idempotency-6-h-must) |
| R11.3 | Signed webhooks | S9 | [S9 §4.5 · Webhooks](stage-09-strangler-atlaspay-auth.md#45-webhooks--45-h-must); from the S9 contract step they are market's only source of payment, refund and payout outcomes ([§4.2 · Strangler](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must)) |
| R11.4 | Merchant API keys | S9 | [S9 §4.3 · API keys](stage-09-strangler-atlaspay-auth.md#43-api-keys--3-h-must) |
| R11.5 | Connect-style split and payouts | S5 | [S5 §4.7 · Connect](stage-05-atlaspay-monolith.md#47-connect-3-h-must), [S5 §4.8 · Payouts](stage-05-atlaspay-monolith.md#48-payouts-3-h-must) |
| R11.6 | Refunds | S5, S9 | [S5 §4.7 · Connect (partial refunds)](stage-05-atlaspay-monolith.md#47-connect-3-h-must), [S9 §4.9 · Saga](stage-09-strangler-atlaspay-auth.md#49-saga--25-h-must) |
| R11.7 | Ledger and balance transactions | S5, S12 | [S5 §4.6 · Ledger](stage-05-atlaspay-monolith.md#46-ledger-9-h-must), [S12 §4.1 · Ledger on Citus](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R12 | Payme and Click adapters, and a simulator that speaks the exact protocol | S5 (re-run against the service in S9) | [S5 §4.1 · provider-sim](stage-05-atlaspay-monolith.md#41-provider-sim-14-h-must), [§4.3 · Payme adapter](stage-05-atlaspay-monolith.md#43-payme-adapter-7-h-must), [§4.4 · Click adapter](stage-05-atlaspay-monolith.md#44-click-adapter-4-h-must); [S9 §4.2 · Strangler (exit criterion)](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must) |
| R13.1 | Telegram bot as a client | S3 | [S3 §4.0 · aiogram ramp](stage-03-redis-auth-bot.md#40-aiogram-ramp-2-h-must), [§4.7 · Bot v1](stage-03-redis-auth-bot.md#47-bot-v1-45-h-must) |
| R13.2 | Bot notifications | S4 | [S4 §4.6 · Notifications and bot push (customer pushes; the vendor flow: new-order message with a "mark shipped" button under the vendor-staff rule)](stage-04-async-events-boundaries.md#46-notifications-and-bot-push-6-h-must) |
| R13.3 | AI assistant in the bot | S8 | [S8 §4.10 · Bot /ask](stage-08-ai-integration.md#410-bot-ask-1-h-must) |
| R13.4 | Bot on webhooks in Kubernetes | S10 | [S10 §4.7 · Bot in Kubernetes + Telegram login](stage-10-kubernetes-grpc-inventory.md#47-bot-in-kubernetes--telegram-login--3-h-must) |
| R13.5 | Payments from the bot: AtlasPay payment links | S9 | [S9 §4.13 · Drills + SD1 (payment links and the bot's pay button, built and tested)](stage-09-strangler-atlaspay-auth.md#413-drills--sd1--65-h-must) |
| R13.6 | Native Telegram Payments (Stars rule, provider tokens) | S10 stretch (a testkit-only spike, the first spare-hours pick), E6 | [S10 §14](stage-10-kubernetes-grpc-inventory.md#14-stretch); E6 in the [README](README.md); the must-tier bot payment path is R13.5 |

### 1.3 Languages, frameworks, architecture (R14–R18)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R14 | FastAPI | S5, S8, S9, S10, S11 | [S5 §4.1 · provider-sim](stage-05-atlaspay-monolith.md#41-provider-sim-14-h-must), [S8 §4.2 · Gateway](stage-08-ai-integration.md#42-the-gateway-105-h-must), [S9 §4.2 · Strangler](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must), [§4.10 · Auth service](stage-09-strangler-atlaspay-auth.md#410-auth-service--115-h-must), [S10 §4.3 · PgBouncer (asyncpg under the FastAPI services)](stage-10-kubernetes-grpc-inventory.md#43-pgbouncer--3-h-must), [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R15 | Django + DRF | S0 (orientation), S1 onward | [S0 §4.0 · Django orientation](stage-00-bootstrap.md#40-django-orientation-25-h), [S1 §4.1 · Django ramp](stage-01-layered-monolith.md#41-django-ramp-7-h), [§4.2 · Layering](stage-01-layered-monolith.md#42-layering-35-h); [S11 §4.1 · ADR and Channels spike](stage-11-realtime-edge-graphql.md#41-adr-and-channels-spike-35-h-must) |
| R16 | A defensible framework choice per service | E1, ADR-000 | E1 in the [README](README.md); [S0 §8 · ADR-000](stage-00-bootstrap.md#8-adrs-and-documents); the split ADRs in [design docs per split](system-design-map.md#7-design-docs-per-split) |
| R17.1 | Python: async and concurrency | S2, S5, S8, S9 | [S2 §4.8 · Python concurrency (GIL, threads vs processes, `to_thread` vs `ProcessPoolExecutor`)](stage-02-checkout-correctness.md#48-python-concurrency-1-h), [S5 §4.1 · provider-sim](stage-05-atlaspay-monolith.md#41-provider-sim-14-h-must), [S8 §4.2 · Gateway (TaskGroup, `asyncio.timeout`, async generators, lifespan)](stage-08-ai-integration.md#42-the-gateway-105-h-must), [S9 §4.2 · Strangler (MissingGreenlet, `expire_on_commit`, argon2 blocking the loop)](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must) |
| R17.2 | Typing | S0, S1 | [S0 §4.4 · CI and hooks (mypy --strict)](stage-00-bootstrap.md#44-ci-and-hooks-3-h), [S1 §4.2 · Layering (Protocols with generics)](stage-01-layered-monolith.md#42-layering-35-h) |
| R17.3 | OOP and SOLID | S1, S2, S5 (LSP contract suite) | [S1 §4.2 · Layering](stage-01-layered-monolith.md#42-layering-35-h), [S2 §4.6 · Pricing (Strategy + Capped wrapper)](stage-02-checkout-correctness.md#46-pricing-25-h), [S5 §6 Tests and §8 · ADR-018 (one contract suite for every provider adapter)](stage-05-atlaspay-monolith.md#6-tests-to-write) |
| R17.4 | Dependency injection | S1, S4 | [S1 §4.2 · Layering (manual composition root)](stage-01-layered-monolith.md#42-layering-35-h), [S4 §4.5 · Boundaries (composition root per module)](stage-04-async-events-boundaries.md#45-boundaries-55-h-must) |
| R17.5 | Context managers | S2 | [S2 §4.3 · Write skew (`atomic_serializable()`)](stage-02-checkout-correctness.md#43-write-skew-35-h), [§4.7 · RLS (`vendor_context()`)](stage-02-checkout-correctness.md#47-rls-4-h) |
| R17.6 | Generators | S4, S5, S0 | [S4 §4.1 · Celery (streaming CSV import)](stage-04-async-events-boundaries.md#41-celery-13-h-must), [S5 §4.6 · Ledger (streaming CSV statement)](stage-05-atlaspay-monolith.md#46-ledger-9-h-must), [S0 §4.6 · Measurement (worldgen)](stage-00-bootstrap.md#46-measurement-55-h) |
| R17.7 | Descriptors | S1 (MoneyField) | [S1 §4.5 · Money](stage-01-layered-monolith.md#45-money-3-h) |
| R17.8 | Packaging | S0, S4, S9 | [S0 §4.1 · Workspace](stage-00-bootstrap.md#41-workspace-35-h), [S4 §4.5 · Boundaries (`atlas-events` wheel)](stage-04-async-events-boundaries.md#45-boundaries-55-h-must), [S9 §4.2 · Strangler (`atlaspay-domain` moves as-is)](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must) |
| R18 | Monolith → modular monolith → strangler → microservices, with the WHY and ADR numbers | S1, S4 (leak count), S6 (gate), S8, S9, S10, S11, S12 | [S1 §4.2 · Layering](stage-01-layered-monolith.md#42-layering-35-h), [S4 §4.5 · Boundaries](stage-04-async-events-boundaries.md#45-boundaries-55-h-must), [S6 §4.11 · Split gate + bulkhead](stage-06-ship-and-operate.md#411-split-gate--bulkhead-45-h-must), [S8 §4.1 · Pain → first split](stage-08-ai-integration.md#41-pain--first-split-85-h-must), [S9 §4.1 · Gate and ADRs](stage-09-strangler-atlaspay-auth.md#41-gate-and-adrs--3-h-must), [S10 §8 · ADR-036](stage-10-kubernetes-grpc-inventory.md#8-adrs-and-documents), [S11 §4.1 · ADR and Channels spike](stage-11-realtime-edge-graphql.md#41-adr-and-channels-spike-35-h-must), [S12 §8 · ADR-040, ADR-042](stage-12-data-at-scale-fraud.md#8-adrs-and-documents) |

### 1.4 Auth and infrastructure (R19–R20)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R19.1 | JWT access/refresh | S1 | [S1 §4.7 · Identity v1](stage-01-layered-monolith.md#47-identity-v1-6-h) |
| R19.2 | Rotation and revocation | S3 | [S3 §4.5 · Auth hardening](stage-03-redis-auth-bot.md#45-auth-hardening-45-h-must) |
| R19.3 | RS256 + JWKS | S9 | [S9 §4.10 · Auth service](stage-09-strangler-atlaspay-auth.md#410-auth-service--115-h-must) |
| R19.4 | OAuth2 Authorization Code + PKCE | S9 | [S9 §4.10 · Auth service](stage-09-strangler-atlaspay-auth.md#410-auth-service--115-h-must) |
| R19.5 | OIDC with Keycloak locally, Google | S9 (both must: Google is a second provider on the same flow, live on staging; CI negatives run against Keycloak) | [S9 §4.10 · Auth service (Keycloak federation; Google as a second provider; an unverified email never auto-links)](stage-09-strangler-atlaspay-auth.md#410-auth-service--115-h-must) |
| R19.6 | API keys for AtlasPay merchants | S9 | [S9 §4.3 · API keys](stage-09-strangler-atlaspay-auth.md#43-api-keys--3-h-must) |
| R19.7 | Service-to-service auth | S9, S10 | [S9 §4.10 · Auth service (client credentials)](stage-09-strangler-atlaspay-auth.md#410-auth-service--115-h-must), [S10 §4.5 · gRPC inventory (interceptors)](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must), [§4.1 · Kubernetes (NetworkPolicy)](stage-10-kubernetes-grpc-inventory.md#41-kubernetes--14-h-must) |
| R19.8 | RBAC + relationship-based permissions | S1, S2 | [S1 §4.7 · Identity v1](stage-01-layered-monolith.md#47-identity-v1-6-h), [S2 §4.7 · RLS](stage-02-checkout-correctness.md#47-rls-4-h) |
| R20.1 | Docker multi-stage | S0 | [S0 §4.2 · Image](stage-00-bootstrap.md#42-image-3-h) |
| R20.2 | Compose | S0 | [S0 §4.3 · Compose](stage-00-bootstrap.md#43-compose-2-h) |
| R20.3 | Kubernetes: kind locally → real deploy | S10 | [S10 §4.1 · Kubernetes](stage-10-kubernetes-grpc-inventory.md#41-kubernetes--14-h-must), [§4.4 · Real deploy](stage-10-kubernetes-grpc-inventory.md#44-real-deploy--5-h-must) |
| R20.4 | Cloud deployment | S6, S10 | [S6 §4.1 · Terraform + VPS](stage-06-ship-and-operate.md#41-terraform--vps-45-h-must), [S10 §4.4 · Real deploy](stage-10-kubernetes-grpc-inventory.md#44-real-deploy--5-h-must) |
| R20.5 | Terraform | S6, S10 | [S6 §4.1 · Terraform + VPS](stage-06-ship-and-operate.md#41-terraform--vps-45-h-must), [S10 §4.4 · Real deploy](stage-10-kubernetes-grpc-inventory.md#44-real-deploy--5-h-must) |
| R20.6 | Zero-downtime deploys and migrations | S6, S10 | [S6 §4.3 · CD](stage-06-ship-and-operate.md#43-cd-85-h-must), [§4.4 · Zero-downtime migrations](stage-06-ship-and-operate.md#44-zero-downtime-migrations-5-h-must), [S10 §4.1 · Kubernetes (preStop, migration Job)](stage-10-kubernetes-grpc-inventory.md#41-kubernetes--14-h-must) |
| R20.7 | Secrets with Vault | S9 | [S9 §4.7 · Vault](stage-09-strangler-atlaspay-auth.md#47-vault--4-h-must) |

### 1.5 Redis, RabbitMQ and databases (R21–R26)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R21.1 | Redis: cache patterns | S3 | [S3 §4.1 · Cache](stage-03-redis-auth-bot.md#41-cache-75-h-must) |
| R21.2 | Stampede | S3 | [S3 §4.1 · Cache](stage-03-redis-auth-bot.md#41-cache-75-h-must) |
| R21.3 | Locks | S4, S10 | [S4 §4.1 · Celery (import lock with a fencing token)](stage-04-async-events-boundaries.md#41-celery-13-h-must), [S10 §4.6 · Flash sale](stage-10-kubernetes-grpc-inventory.md#46-flash-sale--4-h-must), [§4.7 · Bot in Kubernetes (per-chat lock)](stage-10-kubernetes-grpc-inventory.md#47-bot-in-kubernetes--telegram-login--3-h-must) |
| R21.4 | Rate limiting with Lua | S3, S9 | [S3 §4.4 · Limiter](stage-03-redis-auth-bot.md#44-rate-limiter-65-h-must), [S9 §4.6 · Per-key limiter](stage-09-strangler-atlaspay-auth.md#46-per-key-limiter--2-h-must) |
| R21.5 | Pub/sub | S11 | [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R21.6 | Streams | S11 | [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R21.7 | Persistence and eviction | S3, S4 | [S3 §4.2 · Redis ops](stage-03-redis-auth-bot.md#42-redis-operations-25-h-must), [S4 §4.1 · Celery (broker on redis-cache)](stage-04-async-events-boundaries.md#41-celery-13-h-must) |
| R21.8 | Cluster | S3 | [S3 §4.6 · Redis Cluster lab](stage-03-redis-auth-bot.md#46-redis-cluster-lab-35-h-must) |
| R22 | RabbitMQ (exchanges, DLQ, retries, idempotent consumers); Celery + Beat | S4 (S9 webhooks) | [S4 §4.1 · Celery](stage-04-async-events-boundaries.md#41-celery-13-h-must), [§4.2 · RabbitMQ 4.3](stage-04-async-events-boundaries.md#42-rabbitmq-43-9-h-must), [§4.4 · Consumers and CQRS](stage-04-async-events-boundaries.md#44-consumers-and-cqrs-5-h-must), [S9 §4.5 · Webhooks (delay tiers, DLQ)](stage-09-strangler-atlaspay-auth.md#45-webhooks--45-h-must) |
| R23.1 | PostgreSQL: EXPLAIN and the planner | S1, S6 | [S1 §4.6 · Postgres proofs](stage-01-layered-monolith.md#46-postgres-proofs-10-h), [S6 §4.6 · Postgres operations](stage-06-ship-and-operate.md#46-postgres-operations-65-h-must) |
| R23.2 | All index types (B-tree, partial, covering, GIN, GiST, BRIN) | S1, S4, S5 | [S1 §4.6 · Postgres proofs](stage-01-layered-monolith.md#46-postgres-proofs-10-h), [§4.4 · Catalog](stage-01-layered-monolith.md#44-catalog-65-h), [S4 §4.3 · Outbox (partial, BRIN)](stage-04-async-events-boundaries.md#43-outbox-85-h-must), [S5 §4.9 · Reconciliation (BRIN vs B-tree)](stage-05-atlaspay-monolith.md#49-reconciliation-4-h-must) |
| R23.3 | MVCC | S2 | [S2 §4.2 · Races](stage-02-checkout-correctness.md#42-races-8-h) |
| R23.4 | Isolation levels | S2 | [S2 §4.2 · Races](stage-02-checkout-correctness.md#42-races-8-h), [§4.3 · Write skew](stage-02-checkout-correctness.md#43-write-skew-35-h) |
| R23.5 | Locking and deadlocks | S2 | [S2 §4.2 · Races](stage-02-checkout-correctness.md#42-races-8-h) |
| R23.6 | SKIP LOCKED | S4 | [S4 §4.1 · Celery (sweeper)](stage-04-async-events-boundaries.md#41-celery-13-h-must), [§4.3 · Outbox (two relays)](stage-04-async-events-boundaries.md#43-outbox-85-h-must) |
| R23.7 | Advisory locks | S5 | [S5 §4.8 · Payouts](stage-05-atlaspay-monolith.md#48-payouts-3-h-must) |
| R23.8 | Constraints and exclusion | S1, S5 | [S1 §4.6 · Postgres proofs (EXCLUDE)](stage-01-layered-monolith.md#46-postgres-proofs-10-h), [S5 §4.5 · Cross-provider lock](stage-05-atlaspay-monolith.md#45-cross-provider-lock-15-h-must), [§4.6 · Ledger](stage-05-atlaspay-monolith.md#46-ledger-9-h-must) |
| R23.9 | Triggers | S5 | [S5 §4.6 · Ledger (deferred constraint trigger, append-only)](stage-05-atlaspay-monolith.md#46-ledger-9-h-must) |
| R23.10 | Window functions | S5 | [S5 §4.6 · Ledger (running balance)](stage-05-atlaspay-monolith.md#46-ledger-9-h-must) |
| R23.11 | CTEs | S1 | [S1 §4.4 · Catalog (recursive category tree)](stage-01-layered-monolith.md#44-catalog-65-h) |
| R23.12 | Materialized views | S5, S7 | [S5 §4.6 · Ledger (`trial_balance_mv`)](stage-05-atlaspay-monolith.md#46-ledger-9-h-must), [S7 §4.2 · Timescale (matview → CAGG)](stage-07-polyglot-mongo-timescale.md#42-timescaledb-9-h-must) |
| R23.13 | JSONB | S1, S5 | [S1 §4.4 · Catalog (attributes, GIN)](stage-01-layered-monolith.md#44-catalog-65-h), [S5 §4.3 · Payme adapter (raw callbacks, generated column)](stage-05-atlaspay-monolith.md#43-payme-adapter-7-h-must) |
| R23.14 | Full-text search | S4 | [S4 §4.7 · Search](stage-04-async-events-boundaries.md#47-search-5-h-must) |
| R23.15 | Partitioning | S4, S7 | [S4 §4.3 · Outbox (pg_partman)](stage-04-async-events-boundaries.md#43-outbox-85-h-must), [S7 §4.1 · Mongo (b: conversations in Postgres partitions)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| R23.16 | Replication and read replicas | S6, S9 | [S6 §4.7 · Replica and read-your-writes](stage-06-ship-and-operate.md#47-replica-and-read-your-writes-25-h-must), [S9 §4.2 · Strangler (logical replication)](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must) |
| R23.17 | PgBouncer | S10 | [S10 §4.3 · PgBouncer (≥ 1.24; the prepared-statement pain step)](stage-10-kubernetes-grpc-inventory.md#43-pgbouncer--3-h-must) |
| R23.18 | Vacuum and bloat | S6 | [S6 §4.6 · Postgres operations](stage-06-ship-and-operate.md#46-postgres-operations-65-h-must) (first seen in [S4 §4.3 · Outbox](stage-04-async-events-boundaries.md#43-outbox-85-h-must)) |
| R23.19 | pg_stat_statements | S6 | [S6 §4.6 · Postgres operations](stage-06-ship-and-operate.md#46-postgres-operations-65-h-must), [§4.9 · Performance](stage-06-ship-and-operate.md#49-performance-3-h-must) |
| R23.20 | Row-level security | S2 | [S2 §4.7 · RLS](stage-02-checkout-correctness.md#47-rls-4-h) |
| R23.21 | Backup and PITR | S6 | [S6 §4.8 · PITR](stage-06-ship-and-operate.md#48-pitr-35-h-must) |
| R23.22 | Zero-downtime migrations | S6 | [S6 §4.4 · Zero-downtime migrations](stage-06-ship-and-operate.md#44-zero-downtime-migrations-5-h-must) |
| R23.23 | pgvector | S8 | [S8 §4.6 · RAG](stage-08-ai-integration.md#46-rag-9-h-must), [§4.7 · Product features](stage-08-ai-integration.md#47-product-features-45-h-must) |
| R24.1 | MongoDB only where it genuinely fits | S7 | [S7 §4.1 · Mongo](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must), [S7 §8 · ADR-024](stage-07-polyglot-mongo-timescale.md#8-adrs-and-documents) |
| R24.2 | Built after a Postgres JSONB version, with an honest comparison | S7 | [S7 §4.1 · Mongo (a) and (b)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| R24.3 | Aggregation pipeline | S7 | [S7 §4.1 · Mongo (c)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| R24.4 | Indexes | S7 | [S7 §4.1 · Mongo (c)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| R24.5 | Schema design | S7 | [S7 §4.1 · Mongo (c)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| R24.6 | Transactions | S7 | [S7 §4.1 · Mongo (c)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| R24.7 | Replica set | S7 | [S7 §4.1 · Mongo (c)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| R24.8 | Sharding and shard-key choice | S12 | [S12 §4.2 · Mongo sharding](stage-12-data-at-scale-fraud.md#42-mongo-sharding-45-h-must) |
| R25.1 | TimescaleDB: payment/transaction metrics | S7 | [S7 §4.2 · Timescale (`pay_metrics.attempts`)](stage-07-polyglot-mongo-timescale.md#42-timescaledb-9-h-must) |
| R25.2 | Fraud velocity features | S7 (S12 serving) | [S7 §4.2 · Timescale](stage-07-polyglot-mongo-timescale.md#42-timescaledb-9-h-must), [§4.3 · Fraud v1](stage-07-polyglot-mongo-timescale.md#43-fraud-v1-7-h-must), [S12 §4.3 · Fraud service](stage-12-data-at-scale-fraud.md#43-fraud-service-8-h-must) |
| R25.3 | Vendor sales analytics | S7 | [S7 §4.2 · Timescale (`analytics.vendor_sales_daily`)](stage-07-polyglot-mongo-timescale.md#42-timescaledb-9-h-must) |
| R25.4 | Hypertables, continuous aggregates, compression, retention | S7 | [S7 §4.2 · Timescale](stage-07-polyglot-mongo-timescale.md#42-timescaledb-9-h-must) |
| R26.1 | Sharding: Postgres with Citus, by account | S12 | [S12 §4.1 · Ledger on Citus (step 6: distributed by `owner_account_id`, deliberately not by `merchant_id`, because market as merchant #1 would put almost every line on one shard)](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R26.2 | Consistent hashing at the application level | S9, S12 | [S9 §4.5 · Webhooks (hash ring with vnodes)](stage-09-strangler-atlaspay-auth.md#45-webhooks--45-h-must): the ring assigns merchants to dispatcher workers; it assigns work and shards no data. App-level *database* sharding is compared with Citus on paper only, in [S12 §8 · ADR-041](stage-12-data-at-scale-fraud.md#8-adrs-and-documents) |
| R26.3 | Mongo sharding | S12 | [S12 §4.2 · Mongo sharding](stage-12-data-at-scale-fraud.md#42-mongo-sharding-45-h-must) |
| R26.4 | Redis Cluster hash slots | S3 | [S3 §4.6 · Redis Cluster lab](stage-03-redis-auth-bot.md#46-redis-cluster-lab-35-h-must) |
| R26.5 | Resharding pain | S12 (+ S3 stretch) | [S12 §4.1 · Ledger on Citus (rebalance under load)](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must), [§4.2 · Mongo sharding (`reshardCollection`)](stage-12-data-at-scale-fraud.md#42-mongo-sharding-45-h-must), [S3 §14 (slot reshard)](stage-03-redis-auth-bot.md#14-stretch) |

### 1.6 Telegram, realtime, rate limiting, gRPC, GraphQL (R27–R31)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R27.1 | aiogram: vendor/customer notifications | S4 | [S4 §4.6 · Notifications and bot push (item 6: the vendor flow, with a crafted callback from another vendor's staff refused)](stage-04-async-events-boundaries.md#46-notifications-and-bot-push-6-h-must) |
| R27.2 | Order tracking | S3 | [S3 §4.7 · Bot v1](stage-03-redis-auth-bot.md#47-bot-v1-45-h-must) |
| R27.3 | AI assistant in Telegram | S8 | [S8 §4.10 · Bot /ask](stage-08-ai-integration.md#410-bot-ask-1-h-must) |
| R27.4 | FSM in Redis | S3 | [S3 §4.7 · Bot v1](stage-03-redis-auth-bot.md#47-bot-v1-45-h-must) |
| R27.5 | Webhook mode in Kubernetes | S10 | [S10 §4.7 · Bot in Kubernetes + Telegram login](stage-10-kubernetes-grpc-inventory.md#47-bot-in-kubernetes--telegram-login--3-h-must) |
| R27.6 | Throttling middleware | S3 | [S3 §4.7 · Bot v1](stage-03-redis-auth-bot.md#47-bot-v1-45-h-must) |
| R27.7 | Telegram outbound rate limits | S4 | [S4 §4.6 · Notifications and bot push (pacer)](stage-04-async-events-boundaries.md#46-notifications-and-bot-push-6-h-must) |
| R28.1 | WebSockets, SSE and a long-polling comparison | S11 | [S11 §4.2 · Realtime (the long-poll column is measured on a small long-poll endpoint in edge; the bot's `getUpdates` loop is the everyday example)](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.2 | Live order/payment status | S11 | [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.3 | Vendor live dashboard | S11 | [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.4 | Buyer↔vendor chat | S7, S11 | [S7 §4.1 · Mongo (b), (c)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must), [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.5 | LLM streaming via SSE | S8 | [S8 §4.5 · SSE](stage-08-ai-integration.md#45-sse-25-h-must) |
| R28.6 | Django Channels vs FastAPI WS | S11 | [S11 §4.1 · ADR and Channels spike](stage-11-realtime-edge-graphql.md#41-adr-and-channels-spike-35-h-must) |
| R28.7 | Multi-pod fan-out via Redis | S11 | [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.8 | WS auth | S11 | [S11 §4.2 · Realtime (single-use tickets)](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.9 | Heartbeat, reconnect, resume | S11 | [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.10 | Nginx and Ingress upgrade config | S11 | [S11 §4.2 · Realtime](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R28.11 | Graceful shutdown | S11 | [S11 §4.2 · Realtime (close code 1012, drain)](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must); also [S6 §4.3 · CD](stage-06-ship-and-operate.md#43-cd-85-h-must) |
| R29.1 | Rate limiting: login/OTP brute force | S1, S3 | [S1 §4.7 · Identity v1](stage-01-layered-monolith.md#47-identity-v1-6-h), [S3 §4.4 · Limiter](stage-03-redis-auth-bot.md#44-rate-limiter-65-h-must), [§4.5 · Auth hardening](stage-03-redis-auth-bot.md#45-auth-hardening-45-h-must) |
| R29.2 | AtlasPay per-API-key tiers with 429, Retry-After, X-RateLimit-* | S9 | [S9 §4.6 · Per-key limiter](stage-09-strangler-atlaspay-auth.md#46-per-key-limiter--2-h-must) |
| R29.3 | Public catalog | S3 | [S3 §4.4 · Limiter](stage-03-redis-auth-bot.md#44-rate-limiter-65-h-must) |
| R29.4 | AI token and cost budgets | S8 | [S8 §4.3 · Budgets, PII and cache](stage-08-ai-integration.md#43-budgets-pii-and-cache-7-h-must) |
| R29.5 | aiogram throttling | S3 | [S3 §4.7 · Bot v1](stage-03-redis-auth-bot.md#47-bot-v1-45-h-must) |
| R29.6 | Outbound limits (Telegram, providers) | S4, S5 | [S4 §4.6 · Notifications and bot push](stage-04-async-events-boundaries.md#46-notifications-and-bot-push-6-h-must), [S5 §4.9 · Reconciliation (outbound token bucket)](stage-05-atlaspay-monolith.md#49-reconciliation-4-h-must) |
| R29.7 | Nginx `limit_req` | S6 | [S6 §4.2 · Nginx and TLS](stage-06-ship-and-operate.md#42-nginx-and-tls-25-h-must) |
| R29.8 | The pain path: in-memory → N× → INCR race → Lua | S1 → S3 | [S1 §4.7 · Identity v1 (4×)](stage-01-layered-monolith.md#47-identity-v1-6-h), [S3 §4.4 · Limiter](stage-03-redis-auth-bot.md#44-rate-limiter-65-h-must) |
| R29.9 | Algorithms compared (fixed, sliding log, sliding counter, token bucket, leaky bucket) | S3 | [S3 §4.4 · Limiter (`docs/rate-limit-algorithms.md`)](stage-03-redis-auth-bot.md#44-rate-limiter-65-h-must) |
| R29.10 | Fail-open vs fail-closed | S3, S9 | [S3 §4.4 · Limiter](stage-03-redis-auth-bot.md#44-rate-limiter-65-h-must), [§4.6 · Redis Cluster lab](stage-03-redis-auth-bot.md#46-redis-cluster-lab-35-h-must), [S9 §4.6 · Per-key limiter](stage-09-strangler-atlaspay-auth.md#46-per-key-limiter--2-h-must) |
| R30.1 | gRPC: AtlasPay → ledger | S12 | [S12 §4.1 · Ledger on Citus](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R30.2 | Order → inventory reserve | S10 | [S10 §4.5 · gRPC inventory](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must) |
| R30.3 | Protobuf evolution and `buf breaking` in CI | S10 | [S10 §4.5 · gRPC inventory](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must), [S10 §7](stage-10-kubernetes-grpc-inventory.md#7-ci-changes) |
| R30.4 | Deadlines | S10 | [S10 §4.5 · gRPC inventory](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must) |
| R30.5 | Status codes | S10 | [S10 §4.5 · gRPC inventory](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must) |
| R30.6 | Interceptors | S10 | [S10 §4.5 · gRPC inventory](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must) |
| R30.7 | Streaming | S10, S12 | [S10 §4.5 · gRPC inventory (WatchStock)](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must), [S12 §4.1 · Ledger on Citus (StreamStatement)](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R30.8 | HTTP/2 long-lived connection load-balancing pitfall in Kubernetes | S10 | [S10 §4.5 · gRPC inventory](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must) |
| R31.1 | GraphQL storefront BFF | S11 | [S11 §4.3 · GraphQL](stage-11-realtime-edge-graphql.md#43-graphql-85-h-must) |
| R31.2 | N+1 → DataLoader | S11 | [S11 §4.3 · GraphQL (51 → 2)](stage-11-realtime-edge-graphql.md#43-graphql-85-h-must) |
| R31.3 | Depth and complexity limits (cost-based rate limit) | S11 | [S11 §4.3 · GraphQL](stage-11-realtime-edge-graphql.md#43-graphql-85-h-must) |
| R31.4 | Persisted queries | S11 | [S11 §4.3 · GraphQL](stage-11-realtime-edge-graphql.md#43-graphql-85-h-must) |
| R31.5 | Cursor pagination | S11 | [S11 §4.3 · GraphQL (Relay cursors on keyset)](stage-11-realtime-edge-graphql.md#43-graphql-85-h-must) |
| R31.6 | Subscriptions over WS | S11 | [S11 §4.3 · GraphQL](stage-11-realtime-edge-graphql.md#43-graphql-85-h-must) |
| R31.7 | Field-level auth | S11 | [S11 §4.3 · GraphQL](stage-11-realtime-edge-graphql.md#43-graphql-85-h-must) |
| R31.8 | Strawberry vs Graphene decision | S11 (ADR-039) | [S11 §8 · ADR-039](stage-11-realtime-edge-graphql.md#8-adrs-and-documents) |
| R31.9 | REST vs GraphQL vs gRPC decision doc | S10 (ADR-037 v1), S11 (ADR-037 v2 with the GraphQL numbers, must) | [S10 §8 · ADR-037 v1](stage-10-kubernetes-grpc-inventory.md#8-adrs-and-documents), [S11 §8 · ADR-037 v2](stage-11-realtime-edge-graphql.md#8-adrs-and-documents) |

### 1.7 CI/CD, testing, observability, resilience (R32–R35)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R32.1 | GitHub Actions: ruff | S0 | [S0 §7](stage-00-bootstrap.md#7-ci-changes); [testing-and-ci §3](testing-and-ci.md#3-stage-by-stage) |
| R32.2 | mypy | S0 | [S0 §7](stage-00-bootstrap.md#7-ci-changes) |
| R32.3 | pytest + coverage | S0, S1 | [S0 §7](stage-00-bootstrap.md#7-ci-changes), [S1 §7](stage-01-layered-monolith.md#7-ci-changes) |
| R32.4 | Service containers | S1 | [S1 §7](stage-01-layered-monolith.md#7-ci-changes) |
| R32.5 | Image build and push to GHCR | S6 | [S6 §7](stage-06-ship-and-operate.md#7-ci-changes) |
| R32.6 | Monorepo path filters and matrix | S5 | [S5 §7](stage-05-atlaspay-monolith.md#7-ci-changes); [testing-and-ci §4.3](testing-and-ci.md#4-github-actions-layout-for-the-monorepo) |
| R32.7 | pip-audit, gitleaks, Trivy | S0, S6 | [S0 §4.4 · CI and hooks](stage-00-bootstrap.md#44-ci-and-hooks-3-h), [S6 §7](stage-06-ship-and-operate.md#7-ci-changes) |
| R32.8 | `buf breaking` | S10 | [S10 §7](stage-10-kubernetes-grpc-inventory.md#7-ci-changes) |
| R32.9 | Staging and prod deploys to Kubernetes | S10 | [S10 §4.4 · Real deploy](stage-10-kubernetes-grpc-inventory.md#44-real-deploy--5-h-must) |
| R32.10 | Migrations in the pipeline | S6, S10 | [S6 §4.4 · Zero-downtime migrations](stage-06-ship-and-operate.md#44-zero-downtime-migrations-5-h-must), [S10 §4.1 · Kubernetes (migration Job)](stage-10-kubernetes-grpc-inventory.md#41-kubernetes--14-h-must) |
| R32.11 | Smoke tests | S6 | [S6 §4.3 · CD](stage-06-ship-and-operate.md#43-cd-85-h-must) |
| R32.12 | Rollback | S6, S10 | [S6 §4.3 · CD](stage-06-ship-and-operate.md#43-cd-85-h-must), [S10 §4.4 · Real deploy (automatic `rollout undo`)](stage-10-kubernetes-grpc-inventory.md#44-real-deploy--5-h-must) |
| R33.1 | Testing: unit and integration with testcontainers on real Postgres | S1 | [S1 §6](stage-01-layered-monolith.md#6-tests-to-write) |
| R33.2 | fakeredis | S3 | [S3 §6](stage-03-redis-auth-bot.md#6-tests-to-write) |
| R33.3 | freezegun | S3 | [S3 §6](stage-03-redis-auth-bot.md#6-tests-to-write) |
| R33.4 | Hypothesis property tests | S1 | [S1 §4.5 · Money](stage-01-layered-monolith.md#45-money-3-h), [S1 §6](stage-01-layered-monolith.md#6-tests-to-write) |
| R33.5 | Concurrency tests (oversell, double charge) | S2 | [S2 §6](stage-02-checkout-correctness.md#6-tests-to-write) |
| R33.6 | Pact contract tests | S4, S9 | [S4 §4.4 · Consumers and CQRS](stage-04-async-events-boundaries.md#44-consumers-and-cqrs-5-h-must), [S9 §4.12 · Pact](stage-09-strangler-atlaspay-auth.md#412-pact--1-h-must) |
| R33.7 | Payme/Click simulator tests | S5 | [S5 §6](stage-05-atlaspay-monolith.md#6-tests-to-write) |
| R33.8 | locust load tests | S6 | [S6 §4.9 · Performance](stage-06-ship-and-operate.md#49-performance-3-h-must) |
| R33.9 | py-spy profiling | S6 | [S6 §4.9 · Performance](stage-06-ship-and-operate.md#49-performance-3-h-must) |
| R33.10 | Toxiproxy chaos | S9 | [S9 §4.8 · market as merchant + resilience](stage-09-strangler-atlaspay-auth.md#48-market-as-merchant--resilience--4-h-must) |
| R33.11 | Playwright E2E | S6, S11 | [S6 §4.12 · Storefront and E2E](stage-06-ship-and-operate.md#412-storefront-and-e2e-3-h-must), [S11 §4.4 · React SPA](stage-11-realtime-edge-graphql.md#44-react-spa-8-h-must) |
| R33.12 | aiogram bot tests | S3 | [S3 §6](stage-03-redis-auth-bot.md#6-tests-to-write) |
| R33.13 | AI eval harness | S8 | [S8 §4.9 · Evals](stage-08-ai-integration.md#49-evals-35-h-must) |
| R33.14 | Migration tests | S1 | [S1 §6](stage-01-layered-monolith.md#6-tests-to-write) |
| R33.15 | WebSocket tests | S11 | [S11 §6](stage-11-realtime-edge-graphql.md#6-tests-to-write) |
| R34.1 | Observability: structlog | S0 | [S0 §4.1 · Workspace (structlog JSON config)](stage-00-bootstrap.md#41-workspace-35-h) |
| R34.2 | OpenTelemetry traces | S6 | [S6 §4.5 · Observability](stage-06-ship-and-operate.md#45-observability-85-h-must) |
| R34.3 | Prometheus, Grafana, Alertmanager | S6 | [S6 §4.5 · Observability](stage-06-ship-and-operate.md#45-observability-85-h-must) |
| R34.4 | Loki | S6 | [S6 §4.5 · Observability (logs shipped by Grafana Alloy; Promtail is end-of-life)](stage-06-ship-and-operate.md#45-observability-85-h-must) |
| R34.5 | Sentry | S6 | [S6 §4.5 · Observability](stage-06-ship-and-operate.md#45-observability-85-h-must) |
| R34.6 | SLO, SLI and error budgets | S6 | [S6 §4.10 · SLO and drill](stage-06-ship-and-operate.md#410-slo-and-drill-3-h-must), [S6 §8 · ADR-022](stage-06-ship-and-operate.md#8-adrs-and-documents) |
| R34.7 | Runbooks | S6 | [S6 §4.10 · SLO and drill](stage-06-ship-and-operate.md#410-slo-and-drill-3-h-must) |
| R34.8 | Incident drill | S6 (+ S12 stretch) | [S6 §4.10 · SLO and drill](stage-06-ship-and-operate.md#410-slo-and-drill-3-h-must), [S12 §14](stage-12-data-at-scale-fraud.md#14-stretch) |
| R34.9 | DR restore test | S6, S12 | [S6 §4.8 · PITR](stage-06-ship-and-operate.md#48-pitr-35-h-must), [S12 §4.1 · Ledger on Citus (restore-verify extended)](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must) |
| R35.1 | Resilience: timeouts | S8, S9 | [S8 §4.2 · Gateway](stage-08-ai-integration.md#42-the-gateway-105-h-must), [S9 §4.8 · market as merchant + resilience](stage-09-strangler-atlaspay-auth.md#48-market-as-merchant--resilience--4-h-must) (DB timeouts first in [S2 §4.5 · Timeouts](stage-02-checkout-correctness.md#45-timeouts-2-h)) |
| R35.2 | Retries with jitter | S8, S9 | [S8 §4.2 · Gateway](stage-08-ai-integration.md#42-the-gateway-105-h-must), [S9 §4.8 · market as merchant + resilience](stage-09-strangler-atlaspay-auth.md#48-market-as-merchant--resilience--4-h-must) |
| R35.3 | Circuit breaker | S8, S9 | [S8 §4.2 · Gateway](stage-08-ai-integration.md#42-the-gateway-105-h-must), [S9 §4.8 · market as merchant + resilience](stage-09-strangler-atlaspay-auth.md#48-market-as-merchant--resilience--4-h-must) |
| R35.4 | Bulkhead | S6, S9 | [S6 §4.11 · Split gate + bulkhead](stage-06-ship-and-operate.md#411-split-gate--bulkhead-45-h-must), [S9 §4.8 · market as merchant + resilience](stage-09-strangler-atlaspay-auth.md#48-market-as-merchant--resilience--4-h-must) |
| R35.5 | Backpressure | S4, S11 | [S4 §4.1 · Celery](stage-04-async-events-boundaries.md#41-celery-13-h-must), [§4.6 · Notifications and bot push](stage-04-async-events-boundaries.md#46-notifications-and-bot-push-6-h-must), [S11 §4.2 · Realtime (bounded queue per socket)](stage-11-realtime-edge-graphql.md#42-realtime-105-h-must) |
| R35.6 | Idempotency | S2, S5 | [S2 §4.4 · Idempotent checkout](stage-02-checkout-correctness.md#44-idempotent-checkout-45-h), [S5 §4.2 · Intents and idempotency](stage-05-atlaspay-monolith.md#42-intents-and-idempotency-6-h-must) |
| R35.7 | Outbox | S4 | [S4 §4.3 · Outbox](stage-04-async-events-boundaries.md#43-outbox-85-h-must) |
| R35.8 | Saga | S9 | [S9 §4.9 · Saga](stage-09-strangler-atlaspay-auth.md#49-saga--25-h-must) |
| R35.9 | CQRS | S4 | [S4 §4.4 · Consumers and CQRS](stage-04-async-events-boundaries.md#44-consumers-and-cqrs-5-h-must) |
| R35.10 | Event sourcing (ledger) | S5 | [S5 §4.6 · Ledger (`rebuild_balances`)](stage-05-atlaspay-monolith.md#46-ledger-9-h-must) |
| R35.11 | Why not 2PC | S9 | [S9 §8 · ADR-034](stage-09-strangler-atlaspay-auth.md#8-adrs-and-documents) (and the measured cost in [S12 §4.1 · Ledger on Citus](stage-12-data-at-scale-fraud.md#41-ledger-on-citus-175-h-must)) |

### 1.8 System design, AI, ML, Season 2, frontend, interviews (R36–R41)

| # | Requirement (sub-item) | Stage(s) | Where it is specified |
|---|---|---|---|
| R36.1 | System design: concept → where in Atlas | G | [system-design-map §2](system-design-map.md#2-concept--where-in-atlas) |
| R36.2 | The SD1–SD20 bank mapped to what was built; the rest whiteboard-only | G | [system-design-map §3](system-design-map.md#3-sd1sd20-what-is-built-what-stays-on-the-whiteboard-and-when), and §9 of every stage |
| R36.3 | Closing SD20 plus mock interviews | S12, B1, B2 | [S12 §4.4 · Closing](stage-12-data-at-scale-fraud.md#44-closing-4-h-must), [buffers](buffers-and-job-sprint.md), [mock plan](system-design-map.md#6-mock-interview-plan) |
| R36.4 | Design docs per split | Every split ADR | [design docs per split](system-design-map.md#7-design-docs-per-split) |
| R37.1 | AI: RAG support assistant on pgvector | S8 | [S8 §4.6 · RAG](stage-08-ai-integration.md#46-rag-9-h-must) |
| R37.2 | Tool-calling agent with human approval for money actions | S8 | [S8 §4.8 · Agent, MCP and transcripts](stage-08-ai-integration.md#48-agent-mcp-and-transcripts-65-h-must) |
| R37.3 | MCP server exposing platform tools | S8 (OAuth in S9) | [S8 §4.8 · Agent, MCP and transcripts](stage-08-ai-integration.md#48-agent-mcp-and-transcripts-65-h-must), [S9 §4.11 · MCP OAuth](stage-09-strangler-atlaspay-auth.md#411-mcp-oauth--15-h-must) |
| R37.4 | Semantic search | S8 | [S8 §4.7 · Product features](stage-08-ai-integration.md#47-product-features-45-h-must) |
| R37.5 | Vendor product-description generation | S8 | [S8 §4.7 · Product features](stage-08-ai-integration.md#47-product-features-45-h-must) |
| R37.6 | Review summarization | S8 | [S8 §4.7 · Product features](stage-08-ai-integration.md#47-product-features-45-h-must) |
| R37.7 | AI assistant in the Telegram bot | S8 | [S8 §4.10 · Bot /ask](stage-08-ai-integration.md#410-bot-ask-1-h-must) |
| R37.8 | LLM gateway service | S8 | [S8 §4.2 · Gateway](stage-08-ai-integration.md#42-the-gateway-105-h-must) |
| R37.9 | SSE streaming | S8 | [S8 §4.5 · SSE](stage-08-ai-integration.md#45-sse-25-h-must) |
| R37.10 | Token and cost budgets | S8 | [S8 §4.3 · Budgets, PII and cache](stage-08-ai-integration.md#43-budgets-pii-and-cache-7-h-must) |
| R37.11 | Model fallback | S8 | [S8 §4.2 · Gateway](stage-08-ai-integration.md#42-the-gateway-105-h-must) |
| R37.12 | PII redaction | S8 | [S8 §4.3 · Budgets, PII and cache](stage-08-ai-integration.md#43-budgets-pii-and-cache-7-h-must) |
| R37.13 | Prompt versioning | S8 | [S8 §4.4 · Prompts, flags and telemetry](stage-08-ai-integration.md#44-prompts-flags-and-telemetry-45-h-must) |
| R37.14 | Eval harness | S8 | [S8 §4.9 · Evals](stage-08-ai-integration.md#49-evals-35-h-must), [S8 §7](stage-08-ai-integration.md#7-ci-changes) |
| R38.1 | One ML model: AtlasPay fraud scoring with Timescale velocity features | S7 (ported into atlaspay in S9) | [S7 §4.0 · ML ramp](stage-07-polyglot-mongo-timescale.md#40-ml-ramp-25-h-must), [§4.2 · Timescale](stage-07-polyglot-mongo-timescale.md#42-timescaledb-9-h-must), [§4.3 · Fraud v1 (a logistic regression; the feature function in `libs/atlas-fraud-features`)](stage-07-polyglot-mongo-timescale.md#43-fraud-v1-7-h-must), [S9 §4.2 · Strangler (the fraud v1 port; shadow scores on every attempt)](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must) |
| R38.2 | Served as a service | S12 | [S12 §4.3 · Fraud service](stage-12-data-at-scale-fraud.md#43-fraud-service-8-h-must) |
| R38.3 | Latency budget | S12 | [S12 §4.3 · Fraud service (p99 ≤ 30 ms; 50 ms deadline)](stage-12-data-at-scale-fraud.md#43-fraud-service-8-h-must) |
| R38.4 | Fallback when the model is down | S12 | [S12 §4.3 · Fraud service](stage-12-data-at-scale-fraud.md#43-fraud-service-8-h-must) |
| R38.5 | Model versioning | S7, S12 | [S7 §4.3 · Fraud v1 (artifact sha256, model card)](stage-07-polyglot-mongo-timescale.md#43-fraud-v1-7-h-must), [S12 §4.3 · Fraud service (`model_version` on every decision)](stage-12-data-at-scale-fraud.md#43-fraud-service-8-h-must) |
| R39.1 | Season 2 DS: EDA, A/B analysis from feature flags, statistics, vendor analytics | I (flags S8, worldgen S0+) | [Season 2 · 2B (pandas/Polars, notebooks, plotly/matplotlib, scipy.stats/statsmodels; the dirty-data pass; A/B stratified by rollout phase plus a fixed-allocation window)](season-2.md#6-stage-2b--data-science-and-statistics-weeks-69), [§3.7 · analytics-faults switch](season-2.md#37-the-analytics-faults-switch-dirty-data), [2A (vendor revenue)](season-2.md#5-stage-2a--warehouse-and-batch-data-engineering-weeks-15); [S8 §4.4 · Prompts, flags and telemetry](stage-08-ai-integration.md#44-prompts-flags-and-telemetry-45-h-must) |
| R39.2 | ML: fraud deepening, recommendations, demand forecasting | I | [Season 2 · 2C](season-2.md#7-stage-2c--machine-learning-weeks-1017) |
| R39.3 | Math under `.fit()` (phase-9 Week 42) | I | [Season 2 · 2B](season-2.md#6-stage-2b--data-science-and-statistics-weeks-69) |
| R39.4 | MLOps: tracking, registry, monitoring/drift, retraining pipelines | I | [Season 2 · 2D](season-2.md#8-stage-2d--mlops-weeks-1825) |
| R39.5 | Data engineering: Airflow/dbt warehouse from Atlas DBs, Kafka streaming, CDC | I | [Season 2 · 2A](season-2.md#5-stage-2a--warehouse-and-batch-data-engineering-weeks-15), [2E](season-2.md#9-stage-2e--streaming-and-cdc-weeks-2630) |
| R40 | Minimal but real React + TS only where needed | S11 (S6 server-rendered baseline) | [S11 §4.0 · React and TypeScript ramp](stage-11-realtime-edge-graphql.md#40-react-and-typescript-ramp-35-h-must), [§4.4 · React SPA](stage-11-realtime-edge-graphql.md#44-react-spa-8-h-must), [S6 §4.12 · Storefront and E2E](stage-06-ship-and-operate.md#412-storefront-and-e2e-3-h-must) |
| R41.1 | Behavioural bank | 2 STAR per stage → final 8 (S12) | §15 of every stage; [S12 §4.4 · Closing](stage-12-data-at-scale-fraud.md#44-closing-4-h-must); [mock plan](system-design-map.md#6-mock-interview-plan) |
| R41.2 | Per-stage interview questions | D | §10 of every stage |
| R41.3 | Portfolio, README and demo checklist | S6, S8, B2, S12 | [S6 §15](stage-06-ship-and-operate.md#15-definition-of-done), [S8 §15](stage-08-ai-integration.md#15-definition-of-done), [buffers](buffers-and-job-sprint.md), [S12 §15](stage-12-data-at-scale-fraud.md#15-definition-of-done) |

---

## 2. Design-review items resolved

| Item | Resolved in | Where it is specified |
|---|---|---|
| Licences | ADR-003 / E8 | [S0 §8 · ADR-003](stage-00-bootstrap.md#8-adrs-and-documents); E8 in the [README](README.md) |
| Pinned compatibility matrix | ADR-001 / E8 | [S0 §8 · ADR-001](stage-00-bootstrap.md#8-adrs-and-documents) (with `scripts/compat_check.sh`) |
| Mongo driver (PyMongo `AsyncMongoClient`, not Motor) | S7 | [S7 §4.1 · Mongo (c)](stage-07-polyglot-mongo-timescale.md#41-mongodb-15-h-must) |
| Celery on quorum queues and `consumer_timeout` | S4 | [S4 §4.2 · RabbitMQ 4.3](stage-04-async-events-boundaries.md#42-rabbitmq-43-9-h-must) |
| aiogram N-replica concurrency | S10 | [S10 §4.7 · Bot in Kubernetes + Telegram login](stage-10-kubernetes-grpc-inventory.md#47-bot-in-kubernetes--telegram-login--3-h-must) |
| Benchmark methodology | ADR-002, S0 | [S0 §4.6 · Measurement](stage-00-bootstrap.md#46-measurement-55-h) (constant-rate oha probe with latency correction for reported percentiles; locust only shapes traffic; 3 runs for intermediate configurations, 5 for the final pair) |
| Object storage after MinIO's community edition was archived | S1 / ADR-001 | [S1 §4.3 · Vendors and KYC](stage-01-layered-monolith.md#43-vendors-and-kyc-5-h) (Garage by default, SeaweedFS as the fallback, presigned PUT/GET verified) |
| How market learns payment outcomes after the split | S9 | [S9 §4.2 · Strangler](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must) (signed webhooks only; `market.payment-events` is unbound and deleted at the contract step) |
| Fraud v1 across the AtlasPay extraction | S7 → S9 → S12 | [S7 §4.3 · Fraud v1](stage-07-polyglot-mongo-timescale.md#43-fraud-v1-7-h-must), [S9 §4.2 · Strangler](stage-09-strangler-atlaspay-auth.md#42-strangler--15-h-must) (the port, with shadow scores on 100% of attempts), [S12 §4.3 · Fraud service](stage-12-data-at-scale-fraud.md#43-fraud-service-8-h-must) |
| Season-2 world generator | S0 → S12 | [Season 2 §3](season-2.md#3-the-worldgen-data-contract) |
| Telegram Stars rule | E6 | E6 in the [README](README.md) |
| Data governance, erasure and region | S6, S9 | [S6 §4.1 · Terraform + VPS (ADR-021, data-governance v1)](stage-06-ship-and-operate.md#41-terraform--vps-45-h-must), [S9 §4.7 · Vault (crypto-shredding)](stage-09-strangler-atlaspay-auth.md#47-vault--4-h-must), [S9 §8 · ADR-033](stage-09-strangler-atlaspay-auth.md#8-adrs-and-documents) |
| AtlasPay API versioning | S9 | [S9 §4.4 · Versioning](stage-09-strangler-atlaspay-auth.md#44-versioning--15-h-must) |
| Honest hour sizing | C, J (53 weeks; blocks re-budgeted bottom-up; hours log from S0; re-plan with the measured ratio) | [schedule §1 · budget](schedule-and-cuts.md#1-the-budget), [§4 · scenario arithmetic](schedule-and-cuts.md#4-scenario-arithmetic), [§5 · checkpoints](schedule-and-cuts.md#5-checkpoints) |
| Weekly rhythm | C | [schedule §2](schedule-and-cuts.md#2-weekly-rhythm) |
| Django async caveats | E1, E8, S11 | E1 and E8 in the [README](README.md); [S11 §4.1 · ADR and Channels spike](stage-11-realtime-edge-graphql.md#41-adr-and-channels-spike-35-h-must) |

---

## 3. Reverse index: which requirements each stage carries

Read this row before you start a stage: these are the requirement lines your stage close must tick.

| Stage | Requirements it delivers (primary) |
|---|---|
| [S0](stage-00-bootstrap.md) | R2 (ADR-000), R7 (worldgen skeleton), R15 (Django orientation), R16, R17.2, R17.6, R17.8, R20.1, R20.2, R32.1–R32.3, R32.7 (gitleaks in pre-commit), R34.1 |
| [S1](stage-01-layered-monolith.md) | R7 (worldgen v1), R10.1, R15, R17.2–R17.4, R17.7, R18, R19.1, R19.8, R23.1, R23.2, R23.8, R23.11, R23.13, R29.1, R29.8, R32.3, R32.4, R33.1, R33.4, R33.14 |
| [S2](stage-02-checkout-correctness.md) | R7 (orders history), R10.2–R10.5, R11.2, R17.1 (concurrency), R17.3, R17.5, R19.8, R23.3–R23.5, R23.20, R33.5, R35.6 |
| [S3](stage-03-redis-auth-bot.md) | R10.3, R13.1, R19.2, R21.1, R21.2, R21.4, R21.7, R21.8, R26.4, R27.2, R27.4, R27.6, R29.1, R29.3, R29.5, R29.8–R29.10, R33.2, R33.3, R33.12 |
| [S4](stage-04-async-events-boundaries.md) | R10.5, R10.7, R10.8, R13.2, R17.4, R17.6, R17.8, R18, R21.3, R21.7, R22, R23.2, R23.6, R23.14, R23.15, R27.1, R27.7, R29.6, R33.6, R35.5, R35.7, R35.9 |
| [S5](stage-05-atlaspay-monolith.md) | R2, R10.6, R11.1, R11.2, R11.5–R11.7, R12, R17.1, R17.3, R17.6, R23.2, R23.7–R23.10, R23.12, R23.13, R29.6, R32.6, R33.7, R35.6, R35.10 |
| [S6](stage-06-ship-and-operate.md) | R3 (split gate), R18, R20.4–R20.6, R23.1, R23.16, R23.18, R23.19, R23.21, R23.22, R29.7, R32.5, R32.7, R32.10–R32.12, R33.8, R33.9, R33.11, R34.2–R34.9, R35.4, R40 (baseline), R41.3 |
| [S7](stage-07-polyglot-mongo-timescale.md) | R7 (fraud patterns), R23.12, R23.15, R24.1–R24.7, R25.1–R25.4, R28.4, R38.1, R38.5 |
| [S8](stage-08-ai-integration.md) | R13.3, R18, R23.23, R27.3, R28.5, R29.4, R33.13, R35.1–R35.3, R37.1–R37.14, R39.1 (flags), R41.3 |
| [S9](stage-09-strangler-atlaspay-auth.md) | R2, R11.3, R11.4, R11.6, R12 (re-run), R13.5, R14, R17.1, R17.8, R18, R19.3–R19.7, R20.7, R21.4, R22, R26.2, R29.2, R29.10, R33.6, R33.10, R35.1–R35.4, R35.8, R35.11, R37.3, R38.1 (the fraud v1 port) |
| [S10](stage-10-kubernetes-grpc-inventory.md) | R10.2, R13.4, R13.6 (stretch), R14, R18, R19.7, R20.3–R20.6, R21.3, R23.17, R27.5, R30.2–R30.8, R31.9, R32.8–R32.10, R32.12 |
| [S11](stage-11-realtime-edge-graphql.md) | R14, R15, R18, R21.5, R21.6, R28.1–R28.11, R31.1–R31.9 (ADR-037 v2), R33.11, R33.15, R35.5, R40 |
| [S12](stage-12-data-at-scale-fraud.md) | R2, R10.6, R11.7, R18, R24.8, R25.2, R26.1, R26.3, R26.5, R30.1, R30.7, R34.9, R36.3, R38.2–R38.5, R41.1, R41.3 |
| [Season 2](season-2.md) | R9, R39.1–R39.5 |

---

## 4. Limits of the setup (not gaps)

| Limit | Why | What you do instead |
|---|---|---|
| No real Payme or Click sandbox run | There is no merchant contract | provider-sim follows each protocol; the same acceptance suite can be re-run against test.paycom.uz and the Click Playground when an account exists ([S5](stage-05-atlaspay-monolith.md)) |
| Cloud high availability for Citus, Mongo and OpenSearch exists only locally | Cost and the cloud cap ([schedule §6](schedule-and-cuts.md#6-risks)) | Local clusters in [S7](stage-07-polyglot-mongo-timescale.md) and [S12](stage-12-data-at-scale-fraud.md); the cloud runs the smaller shape |
| Cart abandonment exists only in worldgen history | From S3 carts are Redis hashes with a sliding TTL and emit no event, so the running system leaves no abandonment record | Season 2 analyses history-mode cart sessions and labels the result "synthetic history only" ([Season 2 §3.3](season-2.md#33-entities-owners-and-volumes)); a real shop would emit a cart event |
| Kafka and CDC move to Season 2 | RabbitMQ with the outbox covers Season 1's needs; the comparison is more useful once there is a warehouse to feed | [Season 2 · 2E](season-2.md#9-stage-2e--streaming-and-cdc-weeks-2630) |

---

## 5. Rows the degrade list weakens

The degrade list ([schedule-and-cuts §7](schedule-and-cuts.md#7-cut-order-and-the-degrade-list)) shrinks must-tier items when you fall behind. Most items only remove depth, but some turn a "built" row into "designed, measured in part, or written up". If you apply one, mark the affected rows accordingly in your end-of-season check, and be ready to say in an interview what you did instead.

The table follows the cut order of the degrade list. Group A (orders 1–14) touches no requirement you named as a feature; where it weakens a row, it removes only a sub-part. Group B (orders 15–27) holds the partial degrades of requested features: each keeps a hands-on minimum of that feature.

| Order | Degrade # | What shrinks | Rows affected | What remains true |
|---|---|---|---|---|
| 1 | 11 | UUIDv7 benchmark becomes reading only | none (SD6 depth) | ADR-005 argues from the literature and says so |
| 2 | 16 | Capped discount dropped | none | Strategy pattern, rounding and Hypothesis properties (R17.3) |
| 3 | 18 | gthread comparison dropped | none | py-spy and pg_stat_statements still find the bottleneck (R33.9, R23.19) |
| 4 | 14 | Rating aggregator consumer dropped; the rating is computed on read | R10.8 (partly) | Verified-purchase reviews remain |
| 5 | 22 | Lease replaced by the atlaspay scheduler as a single-replica Deployment with the Recreate strategy | SD14 depth (no R row) | UNIQUE run keys still guarantee exactly-once |
| 6 | 12 | Agent trajectory tests dropped | R37.14 (partly) | Golden set, injection and leakage suites remain |
| 7 | 17 | Pact HTTP dropped | R33.6 (HTTP part) | Pact message contracts, the acceptance suite and oasdiff remain |
| 8 | 25 | Google OIDC dropped; Keycloak only | R19.5 (Google part) | OIDC federation with PKCE against Keycloak, and the "unverified email never auto-links" test |
| 9 | 10 | Terraform covers DNS and bucket only; the VM is set up by hand | R20.5 (partly) | Terraform again provisions k3s in S10 |
| 10 | 15 | Click reversal client becomes a manual-refund runbook | R11.6 (Click reversal path) | Payme cancel and the refund ledger path remain; reconciliation still flags the case |
| 11 | 8 | Vault dynamic DB credentials dropped | R20.7 (partly) | KV, transit and crypto-shredding remain |
| 12 | 7 | MCP OAuth and the version transform dropped | R37.3 (OAuth part); AtlasPay API versioning depth (section 2) | Static MCP token; header pin plus oasdiff |
| 13 | 26 | Ledger REST-vs-gRPC benchmark cited instead of run; ledger restore-verify extension becomes a written, reviewed procedure | R34.9 (ledger part) | ADR-037's REST vs gRPC numbers from S10; the S6 restore-verify job |
| 14 | 27 | The S11 and S12 drill hours become real interviews and their retros | none | SD20, mock #3 and the stage SD work remain |
| 15 | 3 | Review summaries dropped | R37.6 | Other AI features unchanged |
| 16 | 13 | Semantic product search dropped (RAG only) | R37.4, R10.7 (AI part) | Hybrid retrieval still exists inside RAG; Season 2 2C generates product embeddings first |
| 17 | 9 | Citus rebalance runs idle, not under load. **Never together with 4'** | R26.5 (Citus part) | The rebalancer, the identical trial balance and the single-shard rule; `reshardCollection` under writes stays the resharding-under-load run |
| 18 | 2 | Channels spike becomes a one-deploy socket-drop count | R28.6 | The comparison still has its key number for ADR-038 |
| 19 | 20 | Conversations stay in Postgres JSONB; Mongo only for transcripts and the benchmark | R24 (chat part), R28.4 (store) | Mongo still backs `atlas_ai.transcripts` and the honest benchmark; the S12 sharding lab loads a worldgen copy of the messages |
| 20 | 6' | Vendor-sales CAGG and the raw → matview → CAGG comparison dropped | R25.3; R23.12 (the matview comparison) | Compression (ratio recorded) and retention on `fraud_features.events`, and the velocity CAGGs, so R25.4 stays built; the Season 2 2A marts cover vendor sales |
| 21 | 5 | Redis Cluster lab becomes a CROSSSLOT demo; failover written up | R21.8 and R26.4 (partly), R29.10 (failover measurement) | A real cluster still runs, with hash slots and hash tags hands-on; fail-open vs fail-closed is still proven by stopping `redis-state` (S3 §4.4, S9 §4.6) |
| 22 | 1' | Persisted-query build tooling replaced by a hand-maintained allow-list of the SPA's operations, still enforced in prod | R31.4 (tooling only) | Persisted queries, subscriptions over WS, DataLoader, cost limits, cursors and field auth are all still built |
| 23 | 4' | Mongo sharded lab drops one of the two bad shard keys. **Only if 9 was not applied** | R24.8, R26.3 (depth) | The 2-shard cluster, the unique-index step, one bad key, the reshard under writes from it, targeted vs scatter-gather `explain` |
| 24 | 19 | React SPA (and the S11 React/TypeScript ramp) becomes server-rendered pages plus a WS client script | R40 | The BFF cookie session, live updates and the Playwright test; the BFF session design is still argued in ADR-038 |
| 25 | 21 | Real Kubernetes deploy dropped; kind only, the cloud stays Compose-on-VPS | R20.3 (real deploy), R32.9; R13.4 and R27.5 (a real Telegram webhook never runs in Kubernetes: the webhook is tested with the fake Bot API on kind only) | Probes, preStop and HPA are still proven on kind |
| 26 | 23 | Fraud service stays in-process in atlaspay | R38.2 | Same fallback, versioning and latency test (R38.3–R38.5) |
| 27 | 24 | Inventory not extracted | R30.2, R10.2 (service part) | gRPC is still learned on the ledger: R30.1 stays, and R30.3–R30.8 move to S12 together with the gRPC foundation's hours (about 2.5 h); ADR-036 records "not extracted" with numbers |

Items 11, 16, 18 and 27 remove depth without weakening any requirement row. Items 4' and 9 are mutually exclusive, so R26.5 always keeps one resharding run under load.

---

## 6. How to verify coverage at the end of Season 1

1. For every row in section 1, open the linked section and find the evidence it asks for under `docs/evidence/sNN/`. No evidence means the row is not done, whatever the code says.
2. For rows listed in section 5, write down which degrade items you applied and what the row now honestly claims.
3. Any row you cannot tick becomes a line in `docs/deferred.md` with a reason and a date.
