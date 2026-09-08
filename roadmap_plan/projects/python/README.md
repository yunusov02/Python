# Track A — The 10 Projects

Consolidated, build-ready specs for the ten projects that form the spine of the
Python backend bootcamp (Phases 1–6, Weeks 1–30).

**What these files are.** The phase files (`phase-1-foundations.md` …
`phase-6-capstone.md`) describe each project spread across a day-by-day plan, with
project work interleaved between theory, mini-exercises, DSA and SQL. These files
pull the *project* out of that structure and present it whole.

**How to use them.** Work top to bottom through a project's Build Plan. When you
hit something you don't understand, open the matching phase file and read only the
theory entry for that topic, then come back. The day numbers in each stage heading
tell you exactly where to look.

---

## The projects

| # | Project | Domain | Level | Phase | Weeks | Days |
|---|---|---|---|---|---|---|
| 1 | [StockPilot](01-stockpilot.md) — inventory & order API | Retail | Junior | 1 | 1–4 | D1–D24 |
| 2 | [QuickServe POS](02-quickserve-pos.md) — point-of-sale | Retail | Junior | 2 | 5–7 | D25–D39 |
| 3 | [PeopleOps](03-peopleops.md) — HR & leave management | HR | Middle | 2→3 | 7–9 | D40–D53 |
| 4 | [WareFlow](04-wareflow.md) — multi-warehouse WMS | Logistics | Middle | 3 | 10–13 | D55–D78 |
| 5 | [CarePoint](05-carepoint.md) — clinic appointments & records | Healthcare | Middle | 4 | 14–15 | D79–D90 |
| 6 | [LedgerBase](06-ledgerbase.md) — double-entry accounting | FinTech | Middle | 4 | 16–18 | D91–D108 |
| 7 | [FleetTrack](07-fleettrack.md) — event-driven delivery logistics | Logistics | Middle | 5 | 19–20 | D109–D120 |
| 8 | [DocuVault](08-docuvault.md) — documents, search & versioning | Enterprise | Middle | 5 | 21–22 | D121–D132 |
| 9 | [PayFlow](09-payflow.md) — payment processing | FinTech | Middle+ | 6 | 25–26 | D145–D156 |
| 10 | [AtlasMarket](10-atlasmarket.md) — multi-vendor marketplace (capstone) | E-commerce | Middle+ | 6 | 27–28 | D157–D168 |

Each file follows the same structure: business problem · outcomes · scope
(including what is deliberately deferred) · roles & permissions · functional
modules · domain model · database design · API · invariants · architecture ·
**infrastructure — what to connect and exactly where** · consolidated build plan ·
testing strategy · definition of done · interview questions · common mistakes.

---

## Where each technology enters, and why

Nothing is introduced before a project has made you feel the problem it solves.
This table is the whole curriculum in one view.

| Project | New this project | The felt problem that justified it |
|---|---|---|
| **1 StockPilot** | FastAPI, SQLAlchemy, Alembic, Postgres, pytest, Hypothesis, Docker Compose, `structlog`, GitHub Actions | Starting point |
| **2 QuickServe** | Django/DRF, **Redis (cache)**, simplejwt, DRF throttling, `fakeredis` | The same product search runs over and over during a rush |
| **3 PeopleOps** | **Celery**, **Celery Beat**, `freezegun` | A synchronous approval email blocks the endpoint and fails the request when the mail server hiccups |
| **4 WareFlow** | **RabbitMQ**, DLQ, Pact, Unit of Work, DDD-lite, partitioning, isolation levels | A warehouse transfer cannot be one transaction — it spans days |
| **5 CarePoint** | **Nginx**, a second service, **MinIO/S3**, presigned URLs, `btree_gist` `EXCLUDE`, React/TS | Two staff book the same slot; documents must not flow through the API |
| **6 LedgerBase** | **Prometheus, Grafana, Sentry**, full CD, zero-downtime deploy, `pip-audit`/`gitleaks`/Trivy, **circuit breaker** | Four services, a report that doesn't reconcile, and the first cross-service write |
| **7 FleetTrack** | **Outbox pattern**, **CQRS**, **Saga**, outbox-lag metric | The Phase 3 bug: commit succeeded, publish failed, billing broke silently |
| **8 DocuVault** | **Elasticsearch**, **Kubernetes (`kind`)**, **etcd**, read replica, consistent hashing | `LIKE '%term%'` stops working; Compose stops coping at 17 services |
| **9 PayFlow** | **Vault**, `locust`, SLO + error budget, on-call runbook, incident drill, backup/DR | A retried request must not charge twice; a ledger with no backup story |
| **10 AtlasMarket** | **Real cloud (IAM/VPC/managed Postgres)**, **bulkhead**, feature flags + canary, **Playwright** | Five synchronous dependencies; a change too risky to ship all at once |

### And where each one is deliberately *not* used

Knowing when **not** to add something is the harder half, and each spec says so
explicitly. The recurring ones:

| Not used | Where, and why |
|---|---|
| **Cache** | WareFlow (stock changes too fast), LedgerBase (balances drive decisions), FleetTrack (a read model is already fast), PayFlow (idempotency must be durable, not cached) |
| **Kafka** | WareFlow and FleetTrack both need work queues with per-message ack, not a replayable log. Both write the decision record instead |
| **Elasticsearch** | Everywhere except DocuVault — the other searches are structured, and Postgres indexes handle them |
| **A message broker** | CarePoint (the two services exchange no events), LedgerBase (the caller needs a synchronous answer) |
| **Kubernetes in production** | Local `kind` only. Operating a real cluster is a different job |
| **Per-service databases** | AtlasMarket — it would force distributed transactions you deliberately avoided |

---

## The through-line

Each project is harder than the last, and each **reuses infrastructure from the
one before**. A gap you feel in one project is closed in a later one:

| Gap felt in | Closed in |
|---|---|
| P1: no caching; low-stock report polled synchronously | P2: Redis cache-aside · P3: Celery |
| P3: manual accrual trigger | P3 (Phase 3): Celery Beat |
| **P4: "DB commit succeeds, publish fails" — observed, not fixed** | **P7: the Outbox pattern** |
| P4: no queue-depth visibility | P6: Prometheus + Grafana |
| P4: Compose straining | P8: Kubernetes on `kind` |
| P6: LedgerBase holds financial data with no backup story | P9: backup/DR drill with a verified restore |
| P6: retry + circuit breaker on one call | P10: bulkhead pools across five |
| P2: cache stampede risk noted, not solved | P8: discussed alongside real replication work |
| Everything | P10: AtlasMarket integrates all of it |

Three further Track A projects (26–28: URL Shortener, Rate Limiter, Distributed
Job Scheduler) ship in Weeks 29–30 on top of AtlasMarket and Phase 5's
from-scratch Raft implementation — see `phase-6-capstone.md` §5.

---

## Recurring disciplines

Every project, without exception:

- **Layering** — the router never touches the ORM
- **Money as integer cents** — never floats
- **Append-only history** — `stock_movements`, `journal_lines`, `delivery_events`,
  `payment_audit`, document versions. Correction is a new row, never an edit
- **Idempotent consumers** — at-least-once delivery makes duplicates normal
- **Enforce it in the database** where it must never happen: `EXCLUDE` constraints,
  `CHECK` constraints, unique keys on idempotency
- **Tests before green** — unit for rules, integration for wiring, plus one test
  for the specific failure this project exists to teach
- **Migrations are reversible**, and that is tested
- **Every "we didn't do X" is written down with the reason** — those notes are
  your interview answers
- **Measure before optimizing** — indexes come from `EXPLAIN ANALYZE`, SLOs from
  load tests, sharding decisions from benchmarks, canaries from dashboards
