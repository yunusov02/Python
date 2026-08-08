# Graph Report - .  (2026-08-08)

## Corpus Check
- Corpus is ~41,488 words - fits in a single context window. You may not need a graph.

## Summary
- 121 nodes · 244 edges · 9 communities
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.68)
- Token cost: 192,108 input · 0 output

## Community Hubs (Navigation)
- DSA Problem Patterns
- Foundations: Backend Craft
- SQL Query Techniques
- Concurrency & Django Caching
- Distributed Systems Primitives
- Microservices & Infra Ops
- Scaling & Advanced Architecture
- Capstone & Production Readiness

## God Nodes (most connected - your core abstractions)
1. `SQL Problem Bank` - 30 edges
2. `StockPilot (Inventory & Order API)` - 21 edges
3. `DSA Problem Bank` - 19 edges
4. `Phase 1 - Foundations` - 19 edges
5. `Phase 3 - Distributed Systems Primitives` - 17 edges
6. `WareFlow (Multi-Warehouse WMS)` - 17 edges
7. `Curriculum Overview` - 16 edges
8. `Phase 4 - Microservices & Infrastructure` - 14 edges
9. `LedgerBase (Double-Entry Accounting)` - 14 edges
10. `Phase 2 - Concurrency + Django/DRF + Caching` - 13 edges

## Surprising Connections (you probably didn't know these)
- `CQRS` --semantically_similar_to--> `Redis Cache-Aside Pattern`  [INFERRED] [semantically similar]
  phase-5-scaling-architecture.md → phase-2-concurrency-django-caching.md
- `Idempotency Keys` --semantically_similar_to--> `Postgres EXCLUDE Constraint`  [INFERRED] [semantically similar]
  phase-6-capstone.md → phase-4-microservices-infra.md
- `Curriculum Overview` --references--> `Phase 1 - Foundations`  [EXTRACTED]
  00-curriculum-overview.md → phase-1-foundations.md
- `Curriculum Overview` --references--> `StockPilot (Inventory & Order API)`  [EXTRACTED]
  00-curriculum-overview.md → phase-1-foundations.md
- `Curriculum Overview` --references--> `PeopleOps (HR & Leave Management)`  [EXTRACTED]
  00-curriculum-overview.md → phase-2-concurrency-django-caching.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Layered Architecture -> Repository -> Unit of Work Evolution** — roadmap_plan_phase_1_foundations_layered_architecture, roadmap_plan_phase_3_distributed_systems_repository_pattern, roadmap_plan_phase_3_distributed_systems_unit_of_work_pattern, roadmap_plan_phase_1_foundations_stockpilot, roadmap_plan_phase_3_distributed_systems_wareflow [INFERRED 0.85]
- **FleetTrack's Outbox -> CQRS -> Saga Architecture Chain** — roadmap_plan_phase_5_scaling_architecture_outbox_pattern, roadmap_plan_phase_5_scaling_architecture_cqrs, roadmap_plan_phase_5_scaling_architecture_saga_pattern, roadmap_plan_phase_5_scaling_architecture_fleettrack [EXTRACTED 1.00]
- **Shared auth-service Reused Across CarePoint, LedgerBase, AtlasMarket** — roadmap_plan_phase_4_microservices_infra_carepoint, roadmap_plan_phase_4_microservices_infra_ledgerbase, roadmap_plan_phase_6_capstone_atlasmarket [EXTRACTED 1.00]

## Communities (9 total, 0 thin omitted)

### Community 0 - "DSA Problem Patterns"
Cohesion: 0.10
Nodes (21): Arrays & Hashing Pattern, Backtracking Pattern, Binary Search Pattern, Bit Manipulation Pattern, 1-D Dynamic Programming Pattern, 2-D Dynamic Programming Pattern, DSA Problem Bank, Graphs Pattern (+13 more)

### Community 1 - "Foundations: Backend Craft"
Cohesion: 0.22
Nodes (18): Alembic Migrations, Context Managers, Dataclasses (incl. Money value object), Decorators (with args, stacking, class-based), Descriptors (data vs non-data), Docker + Docker Compose, FastAPI, Generators & Iterator Protocol (+10 more)

### Community 2 - "SQL Query Techniques"
Cohesion: 0.11
Nodes (18): SQL Technique: Aggregation, SQL Technique: Anti-Join, SQL Technique: Conditional Logic, SQL Technique: Data Integrity Check, SQL Technique: Date Filtering, SQL Technique: Filtering, SQL Technique: NULL Handling, SQL Technique: Outer Join (+10 more)

### Community 3 - "Concurrency & Django Caching"
Cohesion: 0.24
Nodes (14): Celery Background Tasks, Django + Django REST Framework, DRF Throttling / Rate Limiting, Global Interpreter Lock (GIL), JWT Access+Refresh Tokens, multiprocessing / ProcessPoolExecutor, OAuth2 Concepts, PeopleOps (HR & Leave Management) (+6 more)

### Community 4 - "Distributed Systems Primitives"
Cohesion: 0.27
Nodes (14): DDD-lite (Bounded Contexts, Aggregates), Dead-Letter Queue (DLQ), Mini Dependency Injection Container, Kafka (topics, partitions, consumer groups), Mini-ORM Exercise, Outbox Gap (commit-then-publish problem), Phase 3 - Distributed Systems Primitives, Postgres Isolation Levels (+6 more)

### Community 5 - "Microservices & Infra Ops"
Cohesion: 0.29
Nodes (13): API Gateway Pattern, CarePoint (Clinic Appointment & Records), Postgres EXCLUDE Constraint, Full CI/CD Pipeline (build, push, deploy), Grafana Dashboards, LedgerBase (Double-Entry Accounting), Money as Integer Cents, Nginx Reverse Proxy / API Gateway Routing (+5 more)

### Community 6 - "Scaling & Advanced Architecture"
Cohesion: 0.36
Nodes (11): Curriculum Overview, CQRS, DocuVault (Document Management & Search), Elasticsearch / OpenSearch, FleetTrack (Fleet & Delivery Logistics), Kubernetes Fundamentals (kind/minikube), Outbox Pattern, Phase 5 - Scaling & Advanced Architecture (+3 more)

### Community 7 - "Capstone & Production Readiness"
Cohesion: 0.33
Nodes (11): AtlasMarket (Multi-Vendor Marketplace Capstone), Append-Only Audit Logging, Idempotency Keys, Locust Load Testing, PayFlow (Payment Processing Platform), Phase 6 - Senior-Track Capstone, React + TypeScript + Vite + TanStack Query, Secrets Management Pattern (+3 more)

## Knowledge Gaps
- **35 isolated node(s):** `OAuth2 Concepts`, `API Gateway Pattern`, `System Design Interview Technique`, `Arrays & Hashing Pattern`, `Two Pointers Pattern` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SQL Problem Bank` connect `SQL Query Techniques` to `DSA Problem Patterns`, `Foundations: Backend Craft`, `Concurrency & Django Caching`, `Distributed Systems Primitives`, `Microservices & Infra Ops`, `Scaling & Advanced Architecture`, `Capstone & Production Readiness`?**
  _High betweenness centrality (0.330) - this node is a cross-community bridge._
- **Why does `Roadmap Progress Tracker` connect `DSA Problem Patterns` to `Foundations: Backend Craft`, `SQL Query Techniques`, `Concurrency & Django Caching`, `Distributed Systems Primitives`, `Microservices & Infra Ops`, `Scaling & Advanced Architecture`, `Capstone & Production Readiness`?**
  _High betweenness centrality (0.300) - this node is a cross-community bridge._
- **What connects `OAuth2 Concepts`, `API Gateway Pattern`, `System Design Interview Technique` to the rest of the system?**
  _35 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DSA Problem Patterns` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `SQL Query Techniques` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._