# Middle+ Python → AI/ML/Data Engineer — 12-Month Curriculum Overview

**This document replaces the previous 150-task AtlasCommerce roadmap.**
It is delivered phase by phase. This file is the map; each phase gets its own
detailed file with a full daily plan (`phase-1-foundations.md`, `phase-2-...md`, etc.).

The program has two tracks, back to back:

- **Track A — Python Backend Bootcamp (Phases 1-6, Weeks 1-26, ~6 months).**
  6 phases × 4 weeks ≈ 24 weeks. Each week runs Mon–Fri as core
  learning/project days (3–4h) + Saturday as a consolidated Review &
  Interview-Prep day (2–3h), covering DSA + SQL daily alongside the project work.
- **Track B — AI/ML/Data Zoomcamp Track (Phases 7-11, Weeks 27-56, ~6-7 months).**
  5 phases covering DataTalksClub's LLM, AI Dev Tools, Machine Learning,
  MLOps Engineering, and Data Engineering Zoomcamps — in that order (see
  "Zoomcamp Track Ordering Rationale" below). DSA/SQL grind is dropped here
  (already covered in Track A); each weekday still runs Theory + Mini
  Exercise + Project, Saturday is still a review day.

Sundays are intentionally left as rest/buffer throughout — not itemized, but
assumed for catch-up if a weekday slips. Total: **336 days, 56 weeks, 11
phases, ~12-13 months** (slightly over 12 months by design, since the
Zoomcamp track wasn't compressed to force an exact fit).

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

## The 15 Zoomcamp Track Projects (Phases 7-11)

Track B doesn't start new domains from scratch — it applies each Zoomcamp's
skills directly onto the 10 systems Track A already built, plus a handful of
fresh AI-native builds. This keeps the whole 12 months feeling like one
continuous system rather than 15 bolted-on course assignments.

| # | Project | Applies | Phase |
|---|---------|---------|-------|
| 11 | **CarePoint Patient-FAQ Assistant** — RAG chatbot for patients | LLM Zoomcamp | 7 |
| 12 | **DocuVault "Ask Your Documents" Chatbot** — multi-turn RAG over the document store | LLM Zoomcamp | 7 |
| 13 | **AtlasMarket Support Assistant** — RAG product Q&A for marketplace buyers | LLM Zoomcamp | 7 |
| 14 | **StockPilot Bug-Fix Coding Agent** — MCP server + guarded coding agent | AI Dev Tools Zoomcamp | 8 |
| 15 | **Cross-System Automation Pipeline** — LedgerBase reconciliation via CI/CD + low-code | AI Dev Tools Zoomcamp | 8 |
| 16 | **Freeform AI Dev Tool Capstone** | AI Dev Tools Zoomcamp | 8 |
| 17 | **StockPilot Demand Forecaster** — regression on order history | ML Zoomcamp | 9 |
| 18 | **QuickServe Churn Predictor** — classification on POS data | ML Zoomcamp | 9 |
| 19 | **CarePoint No-Show Predictor** — classification/trees on appointment data | ML Zoomcamp | 9 |
| 20 | **MLOps: Demand Forecaster, productionized** — tracking+orchestration+deployment+monitoring+CI | MLOps Zoomcamp | 10 |
| 21 | **MLOps: Churn Predictor, productionized** | MLOps Zoomcamp | 10 |
| 22 | **MLOps: No-Show Predictor, productionized** | MLOps Zoomcamp | 10 |
| 23 | **Year-2 Analytics Platform (batch)** — unified warehouse across StockPilot/QuickServe/PeopleOps/LedgerBase | Data Engineering Zoomcamp | 11 |
| 24 | **Year-2 Analytics Platform + Streaming** — FleetTrack delivery events, real time | Data Engineering Zoomcamp | 11 |
| 25 | **Year-2 Analytics Platform + Vendor Analytics** — AtlasMarket revenue extension | Data Engineering Zoomcamp | 11 |

### Zoomcamp Track Ordering Rationale

Two orderings were considered before this one: LLM → ML → MLOps → AI Dev
Tools → Data Engineering, and ML → MLOps → LLM → AI Dev Tools → Data
Engineering. The order actually used is **LLM → AI Dev Tools → ML → MLOps →
Data Engineering**, because:

- Coming straight off 6 months of backend work, **LLM Zoomcamp is the
  lowest-friction on-ramp**: you're wrapping API calls into services and
  building RAG pipelines — a small delta from what you already do, not a
  pivot into new math/stats. Starting here keeps momentum instead of
  front-loading the most theory-heavy material right after a long bootcamp.
- **AI Dev Tools follows immediately** because it's a direct continuation of
  LLM Zoomcamp's Agents module (tool-calling, MCP, coding-agent loops) —
  keeping them adjacent lets AI Dev Tools reuse LLM's agent-loop
  fundamentals without a gap.
- **ML Zoomcamp comes third**, once the LLM/agent momentum is established,
  shifting into classical ML's more theory/math-heavy territory
  (regression, evaluation metrics, trees, deep learning).
- **MLOps follows ML directly** — the one hard dependency in the whole
  track: MLOps productionizes the exact 3 models ML just built, so it can't
  be placed anywhere else.
- **Data Engineering closes the program** regardless of how the other four
  are ordered: it depends on data from every system built all year, so it's
  the only phase that structurally has to be last.

One minor sequencing quirk worth knowing: LLM Zoomcamp's Evaluation module
(hit rate, MRR, LLM-as-judge) comes before ML Zoomcamp's classical
evaluation metrics (precision/recall/AUC). This isn't a blocker — the two
metric families are independent — but you'll meet RAG-style evaluation
before the more foundational classification metrics it's sometimes compared
against in interviews.

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

### Phase 6 — Senior-Track Capstone (Weeks 23–26)
Idempotency, distributed transactions, security hardening, performance
profiling under load, mock system-design interviews, frontend architecture
literacy (React/TS/TanStack Query) for cross-functional communication.
**Project 9: PayFlow. Project 10: AtlasMarket (capstone).**

*— End of Track A (6-month Python Backend Bootcamp) —*

### Phase 7 — LLM Zoomcamp (Weeks 27–32)
RAG architecture, embeddings & vector search (Qdrant + Elasticsearch),
tool-calling agents, RAG evaluation (hit rate/MRR, LLM-as-judge), monitoring,
hybrid search/re-ranking, and prompt-injection guardrails.
**Project 11: CarePoint Patient-FAQ Assistant. Project 12: DocuVault "Ask
Your Documents" Chatbot. Project 13: AtlasMarket Support Assistant.**

### Phase 8 — AI Dev Tools Zoomcamp (Weeks 33–37)
AI-assisted coding workflows, the Model Context Protocol (custom MCP
servers), building a coding agent's tool loop from scratch, AI-assisted
CI/CD (PR-review bots), and low-code automation (n8n) — with an explicit
human-approval-gate/guardrails discipline for anything code-changing.
**Project 14: StockPilot Bug-Fix Coding Agent. Project 15: Cross-System
Automation Pipeline. Project 16: Freeform AI Dev Tool Capstone.**

### Phase 9 — Machine Learning Zoomcamp (Weeks 38–44)
Regression, classification, evaluation metrics, decision trees/ensembles
(random forest, XGBoost), deep learning (CNNs, transfer learning), and three
deployment styles (serverless/Lambda, Kubernetes, KServe) — applied to
StockPilot, QuickServe, and CarePoint's own data.
**Project 17: StockPilot Demand Forecaster. Project 18: QuickServe Churn
Predictor. Project 19: CarePoint No-Show Predictor.**

### Phase 10 — MLOps Engineering Zoomcamp (Weeks 45–50)
Productionizing Phase 9's three models: MLflow experiment tracking &
registry, Prefect orchestration, batch/web/streaming deployment patterns,
Evidently drift monitoring, and CI quality gates that fail a retrain on
metric regression.
**Project 20–22: all three Phase 9 models, fully productionized.**

### Phase 11 — Data Engineering Zoomcamp (Weeks 51–56)
Terraform IaC, Airflow orchestration, warehouse fundamentals + dbt analytics
engineering, Spark batch processing, and Kafka/ksqlDB streaming — unifying
data from every system built across the year into one analytics platform.
**Project 23–25: Year-2 Analytics Platform (batch → +streaming →
+vendor-analytics). Program wrap: tag `v2.0-year-plan-complete`.**

---

## How technologies get introduced (no dumping)

Every technology from your original spec appears exactly once, at the moment
it solves a real pain you've just felt — e.g. you meet the N+1 problem *while
building StockPilot's order list endpoint* in Phase 1, not as an abstract
lecture. Redis shows up in Phase 2 when QuickServe's product-lookup endpoint
gets slow under load. Kafka shows up in Phase 3 when WareFlow needs to react
to stock-level events across services. This ordering is fixed for Track A
(Phases 1-6) and won't be reshuffled between phases.

Track B (Phases 7-11) applies the same discipline, but reuses Track A's
infrastructure instead of introducing it twice: Phase 7's vector search sits
alongside Phase 5's Elasticsearch; Phase 9's model-serving Kubernetes work
reuses Phase 5's `kind` cluster; Phase 10's streaming-deployment discussion
reuses Phase 3's Kafka; Phase 11's warehouse pipelines extract straight out
of the Postgres databases every earlier phase built.

---

## Weekly rhythm (applies to every phase)

- **Mon–Fri:** 3–4h/day — theory reading, 1 mini-exercise, project build task,
  a testing task, a git commit with a real message, 1–2 interview questions
  to answer in writing. **Track A only (Phases 1-6):** also 1 DSA problem +
  1 SQL problem per day.
- **Saturday:** 2–3h — review the week, redo the hardest mini-exercise from
  memory, mock-answer 5 interview questions out loud, write a short "what I
  now understand that I didn't Monday" note.
- **Sunday:** rest / buffer for slipped days.

---

## What's next

`phase-1-foundations.md` — full Project 1 spec (StockPilot) + all 24 daily
entries for Weeks 1–4, mini-projects, books, weekly interview question sets,
deliverables, and GitHub milestones.

Track B, once Track A is complete: `phase-7-llm-zoomcamp.md` →
`phase-8-ai-devtools-zoomcamp.md` → `phase-9-ml-zoomcamp.md` →
`phase-10-mlops-zoomcamp.md` → `phase-11-data-engineering-zoomcamp.md`,
each structured the same way (Learning Goals, Technologies Introduced, full
project specs, Books & Documentation, Weekly Interview Question Sets, Daily
Plan tables, Deliverables & Milestones, Skills Checklist) — minus the
DSA/SQL columns, which Track A already covers. `progress.md` tracks every
day across both tracks in one file.
