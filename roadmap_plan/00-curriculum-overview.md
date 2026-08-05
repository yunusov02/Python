# Middle+ Python Backend Engineering Bootcamp — 6-Month Curriculum Overview

**This document replaces the previous 150-task AtlasCommerce roadmap.**
It is delivered phase by phase. This file is the map; each phase gets its own
detailed file with a full daily plan (`phase-1-foundations.md`, `phase-2-...md`, etc.).

Format: 6 phases × 4 weeks ≈ 24 weeks (~6 months). Each week runs Mon–Fri as
core learning/project days (3–4h) + Saturday as a consolidated Review &
Interview-Prep day (2–3h). Sundays are intentionally left as rest/buffer —
not itemized, but assumed for catch-up if a weekday slips.

---

## The 10 Projects (spine of the curriculum)

| # | Project | Domain | Level | Phase |
|---|---------|--------|-------|-------|
| 1 | **StockPilot** — single-store inventory & order API | Retail/Inventory | Junior | 1 |
| 2 | **QuickServe POS** — point-of-sale system | Retail/POS | Junior | 2 |
| 3 | **PeopleOps** — HR & leave management system | HR/Enterprise | Middle | 2–3 |
| 4 | **WareFlow** — multi-warehouse WMS with pick/pack workflows | Logistics | Middle | 3 |
| 5 | **CarePoint** — clinic/hospital appointment & records system | Healthcare | Middle | 4 |
| 6 | **LedgerBase** — double-entry accounting/invoicing platform | FinTech | Middle | 4 |
| 7 | **FleetTrack** — fleet & delivery logistics platform (event-driven) | Logistics | Middle | 5 |
| 8 | **DocuVault** — document management with search & versioning | Enterprise/Search | Middle | 5 |
| 9 | **PayFlow** — payment processing platform (ledger, idempotency, webhooks) | FinTech | Middle+/Senior | 6 |
| 10 | **AtlasMarket** — AI-assisted multi-vendor e-commerce marketplace (capstone, absorbs everything) | E-commerce | Middle+/Senior | 6 |

Each project is **more complex than the last**, reuses infrastructure patterns
from earlier projects (so you're not starting from zero each time), and is
fully deployable. Project 10 is deliberately the spiritual successor to
AtlasCommerce — same ambition, built on 6 months of accumulated skill instead
of upfront over-scoping.

---

## Phase Map

### Phase 1 — Foundations: Advanced Python + Production FastAPI (Weeks 1–4)
Advanced Python (decorators, generators, context managers, typing, dataclasses,
descriptors), clean layered architecture, PostgreSQL fundamentals done right
(indexes, transactions, N+1), Pytest, Docker basics, structured logging.
**Project 1: StockPilot.**

### Phase 2 — Concurrency + Django/DRF + Caching (Weeks 5–8)
GIL, threading, multiprocessing, asyncio internals, Django/DRF for admin-heavy
CRUD, Redis caching, Celery + background jobs, rate limiting, JWT auth/OAuth.
**Project 2: QuickServe POS. Project 3 starts: PeopleOps.**

### Phase 3 — Distributed Systems Primitives (Weeks 9–13)
RabbitMQ, Kafka basics, event-driven patterns, Repository/Service Layer/Unit
of Work, DDD-lite, advanced Postgres (isolation levels, MVCC, deadlocks,
partitioning), database migrations at scale.
**Project 3 finishes: PeopleOps. Project 4: WareFlow.**

### Phase 4 — Microservices & Infrastructure (Weeks 14–18)
Docker Compose multi-service systems, Nginx reverse proxy, API Gateway
patterns, CI/CD (GitHub Actions), Prometheus/Grafana, Sentry, health checks,
zero-downtime deploys, S3/MinIO object storage.
**Project 5: CarePoint. Project 6: LedgerBase.**

### Phase 5 — Scaling & Advanced Architecture (Weeks 19–22)
CQRS, Outbox pattern, Saga (overview), Elasticsearch/OpenSearch, sharding,
replication, Kubernetes fundamentals, system design deep-dives (load
balancers, CDN, CAP theorem in practice).
**Project 7: FleetTrack. Project 8: DocuVault.**

### Phase 6 — Senior-Track Capstone (Weeks 23–24, extended)
Idempotency, distributed transactions, security hardening, performance
profiling under load, mock system-design interviews, frontend architecture
literacy (React/TS/TanStack Query) for cross-functional communication.
**Project 9: PayFlow. Project 10: AtlasMarket (capstone).**

---

## How technologies get introduced (no dumping)

Every technology from your original spec appears exactly once, at the moment
it solves a real pain you've just felt — e.g. you meet the N+1 problem *while
building StockPilot's order list endpoint* in Phase 1, not as an abstract
lecture. Redis shows up in Phase 2 when QuickServe's product-lookup endpoint
gets slow under load. Kafka shows up in Phase 3 when WareFlow needs to react
to stock-level events across services. This ordering is fixed for the whole
6 months and won't be reshuffled between phases.

---

## Weekly rhythm (applies to every phase)

- **Mon–Fri:** 3–4h/day — theory reading, 1 mini-exercise, project build task,
  a testing task, a git commit with a real message, 1–2 interview questions
  to answer in writing.
- **Saturday:** 2–3h — review the week, redo the hardest mini-exercise from
  memory, mock-answer 5 interview questions out loud, write a short "what I
  now understand that I didn't Monday" note.
- **Sunday:** rest / buffer for slipped days.

---

## What's next

`phase-1-foundations.md` — full Project 1 spec (StockPilot) + all 24 daily
entries for Weeks 1–4, mini-projects, books, weekly interview question sets,
deliverables, and GitHub milestones.
