# PHASE 3 — Distributed Systems Primitives
### Weeks 9–13 (5 weeks) · 30 working days

---

## 1. Learning Goals
- Finish PeopleOps with scheduled jobs (cron via Celery Beat) so background
  work isn't just "fire and forget" but also "run reliably on a schedule."
- Formalize Repository + Service Layer + **Unit of Work** as a named pattern,
  not an accident of how you happened to structure Phase 1/2 code.
- Apply DDD-lite: bounded contexts, aggregates, and why WareFlow's
  "Inventory" and "Fulfillment" concerns shouldn't share one model.
- Introduce RabbitMQ for real event-driven communication between two parts
  of WareFlow (warehouse stock events → fulfillment reservations).
- Get hands-on with Postgres isolation levels, MVCC, deadlocks, and table
  partitioning — no longer conceptual, but debugged live in WareFlow.

## 2. Technologies Introduced
Celery Beat (scheduling/cron), RabbitMQ (producer/consumer, exchanges,
queues, dead-letter queues), Kafka (conceptual intro + one hands-on mini
project, contrasted with RabbitMQ), Repository/Service Layer/Unit of Work
formalized, DDD-lite (bounded contexts, aggregates), Postgres isolation
levels/MVCC/deadlocks/table partitioning, a custom mini-ORM exercise, a mini
Dependency Injection container.

Deliberately not yet: Kubernetes, CQRS/Event Sourcing/Outbox (Phase 5),
Elasticsearch, monitoring stack (Phase 4).

---

## 3. PROJECT 3 (finishes) — PeopleOps: Scheduling & Notifications

**What's added this phase:** Celery Beat schedules monthly leave-balance
accrual automatically (no more manual trigger). Notifications on approval/
rejection are async (built Phase 2) and now also fire a reminder job if a
request sits unapproved for 3+ days — your first taste of a *scheduled*
background workflow, not just a triggered one.

**Testing:** Celery Beat schedule tested with `freezegun` to fast-forward
time rather than actually waiting days.

**Deliverable:** tag `v0.2-peopleops-final`, `docs/postmortem-peopleops.md`.

---

## 4. PROJECT 4 — WareFlow (Multi-Warehouse Management System)

**Business Problem:** A growing retailer now operates 3 warehouses. Stock
needs to be received, transferred between warehouses, and reserved/picked
for outbound orders — and a stock transfer or pick that fails partway
through must never leave inventory numbers lying (this is the project where
transactions and locking stop being an exercise and become the whole
point).

**Requirements**
- Functional: receive stock at a warehouse, transfer stock between
  warehouses (two-step: dispatch → receive), reserve stock for an order,
  pick/pack workflow, view stock by warehouse.
- Non-functional: a transfer must be atomic across the source warehouse's
  decrement and the destination's eventual increment — but the destination
  increment happens only on *receipt confirmation*, which may be hours or
  days later. This is not one transaction — it's your first real encounter
  with a **process spanning multiple transactions**, and why an event
  (`StockDispatched`, `StockReceived`) is the right model instead of trying
  to force it into one DB transaction.

**Architecture — DDD-lite, two bounded contexts:**
```
Inventory context        Fulfillment context
  - Warehouse               - Order
  - StockLevel               - Reservation
  - StockMovement            - PickList
      ↑ publishes events ↓ consumes events (RabbitMQ)
```
Formal layering: `Repository` (per aggregate) → `UnitOfWork` (wraps a
transaction across multiple repositories, commits/rolls back as one unit)
→ `Service` (orchestrates UoW + publishes domain events after commit).

**ER Diagram (textual)**
```
warehouses(id, name, location)
stock_levels(id, warehouse_id -> warehouses.id, product_id, qty)   -- unique(warehouse_id, product_id)
stock_movements(id, warehouse_id, product_id, delta, reason, ref_id, created_at)
transfers(id, from_warehouse_id, to_warehouse_id, status[dispatched|received|cancelled], created_at)
transfer_items(id, transfer_id -> transfers.id, product_id, qty)
reservations(id, order_ref, warehouse_id, product_id, qty, status, created_at)
```

**Folder Structure**
```
wareflow/
  inventory/
    domain/            # entities, value objects, domain events
    repositories/
    services/
  fulfillment/
    domain/
    repositories/
    services/
  shared/
    unit_of_work.py
    event_bus.py        # thin wrapper over RabbitMQ publish/consume
    di_container.py      # mini DI container (from Week 10 mini-project, applied for real here)
```

**API Design**
```
POST /warehouses/{id}/stock/receive
POST /transfers                    # dispatch
POST /transfers/{id}/receive        # confirm receipt at destination
POST /reservations                  # reserve stock for an order
GET  /warehouses/{id}/stock
```

**Database Design:** `UNIQUE(warehouse_id, product_id)` on `stock_levels`,
composite index `(warehouse_id, product_id)` on `stock_movements`. In Week
12 you partition `stock_movements` by month once you simulate it growing
past a few million rows and feel the seq-scan pain on old-data queries.

**Authentication & Permissions:** role per warehouse (a warehouse worker at
Warehouse A shouldn't dispatch transfers from Warehouse B they're not
assigned to) — your first taste of resource-scoped permissions, not just
global roles.

**Caching:** not a focus this phase — stock numbers change too often to
benefit from caching; explicitly note this as a case where caching would be
*wrong*, an important interview-answer nuance.

**Background Jobs / Messaging:** RabbitMQ carries `StockDispatched` and
`StockReceived` events between Inventory and Fulfillment contexts. A
dead-letter queue is configured for events that fail processing 3 times —
you inspect a DLQ message by hand at least once so it's not just a
textbook term.

**Infrastructure:** Docker Compose gains `rabbitmq` service (with the
management UI exposed so you can *see* queues/exchanges, not just trust
they exist).

**CI/CD:** CI now spins up Postgres + Redis + RabbitMQ service containers.

**Testing Strategy:** integration test that publishes a `StockDispatched`
event and asserts the Fulfillment consumer reacts correctly; a deliberate
test that kills the consumer mid-processing and confirms the message isn't
lost (requeued, not acked until processing completes).

**Monitoring:** RabbitMQ management UI as your only visibility for now;
Prometheus-based queue depth monitoring is a concrete Phase 4 callback you
write down.

**Deployment:** same Compose deploy, now with more services — you'll feel
Compose starting to strain here, which sets up "why microservices need
better orchestration" for Phase 4/5.

**Scaling Strategy:** written notes — what happens to `stock_movements` at
100M rows (partitioning strategy you already applied), what happens if
RabbitMQ itself needs to scale (clustering, out of scope but named).

**Common Interview Questions**
1. Why is a warehouse transfer modeled as two events, not one transaction?
2. What's the difference between Repository and Unit of Work, precisely?
3. Explain MVCC — why do two concurrent reads never block each other in
   Postgres?
4. Walk through a deadlock you actually reproduced here and how you'd avoid
   it in the first place (consistent lock ordering).
5. RabbitMQ vs Kafka — when would you pick each?
6. What guarantees does a DLQ give you, and what doesn't it give you?
7. Why did you partition `stock_movements`, and by what key?
8. How do bounded contexts here prevent a change in Fulfillment from
   forcing a change in Inventory?

**Possible Improvements:** outbox pattern for guaranteed event publishing
(explicit Phase 5 callback — you'll notice right now that if the DB commit
succeeds but the RabbitMQ publish fails, you have a bug; you write this
down rather than solving it yet), read replicas for stock-level queries.

**What Companies Usually Do Differently:** real WMS platforms use the
outbox pattern specifically because "commit to DB, then publish to broker"
is not atomic without it — you're meant to *feel* this gap now, not have it
solved for you.

**Common Mistakes:** forgetting to ack a RabbitMQ message only after
successful processing (acking too early loses messages on crash); modeling
a transfer as one big transaction across two warehouses instead of two
separate ones connected by an event; leaking Fulfillment types into
Inventory's domain layer.

---

## 5. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| Mini Dependency Injection container (used for real in WareFlow later) | 9 | DI as a pattern, not just a framework feature |
| Custom mini-ORM (map a dict row to an object, minimal query builder) | 9 | What SQLAlchemy is actually doing underneath |
| RabbitMQ producer/consumer (standalone, before applying to WareFlow) | 11 | Exchanges, queues, bindings, ack/nack |
| Kafka event processing intro (single topic, produce+consume) | 13 | Contrast with RabbitMQ: log vs queue semantics |
| Unit of Work pattern demo (2 repositories, one commit boundary) | 10 | Transactional consistency across repositories |

---

## 6. Books & Documentation
- *Building Microservices* (Newman) — Ch. 4 (Integration) during Weeks 11–13.
- *Domain-Driven Design Distilled* (Vernon) — read fully during Week 10,
  specifically for bounded contexts and aggregates before modeling WareFlow.
- Postgres docs Ch. 13 (Concurrency Control) full read, plus Ch. 5 §11
  (Partitioning) during Week 12.
- RabbitMQ official tutorials 1–6 (rabbitmq.com/getstarted.html).
- Kafka: Confluent's "Kafka in a Nutshell" intro during Week 13.

---

## 7. Weekly Interview Question Sets

**Week 9 — Scheduling, DI, mini-ORM**
1. Cron via Celery Beat vs a plain OS crontab calling a script — tradeoffs?
2. What problem does dependency injection solve that a global import doesn't?
3. What does an ORM's session/unit-of-work actually track internally?

**Week 10 — DDD-lite, Unit of Work**
1. What's a bounded context, concretely, using WareFlow as the example?
2. Repository vs Unit of Work — what does each own?
3. Why shouldn't Fulfillment import Inventory's domain models directly?

**Week 11 — RabbitMQ**
1. Exchange vs queue — what's each one's job?
2. At-least-once delivery — what does your consumer have to do to handle
   duplicate messages safely (idempotency)?
3. What happens to an unacked message if the consumer dies?

**Week 12 — Postgres deep dive**
1. Explain MVCC in your own words, using a concrete two-transaction example.
2. What's a phantom read, and which isolation level prevents it?
3. Why did you partition by month instead of by warehouse?

**Week 13 — Kafka, phase review**
1. Kafka's log-based model vs RabbitMQ's queue model — when does each fit?
2. What does a Kafka consumer group actually coordinate?
3. Trace a `StockDispatched` event end-to-end through your system.

---

## 8. Daily Plan — Week 9: PeopleOps Scheduling + Mini-Projects

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
|---|---|---|---|---|---|---|---|---|
| Mon (D49) | Celery Beat scheduling | Celery Beat docs | — | Monthly leave-accrual scheduled task | `freezegun`-based schedule test | `feat: celery beat monthly accrual` | Q1 | 3.5h |
| Tue (D50) | Reminder-job pattern | — | — | 3-day unapproved-request reminder job | Test reminder fires at correct threshold | `feat: leave request reminder job` | — | 3.5h |
| Wed (D51) | Dependency injection theory | — | Mini DI container (register/resolve) | — | Unit tests for DI container | `feat: mini DI container` | Q2 | 3.5h |
| Thu (D52) | How ORMs work internally | SQLAlchemy source skim (`orm/session.py` overview) | Mini-ORM: dict-row → object mapper + tiny query builder | — | Unit tests for mini-ORM | `feat: mini orm exercise` | Q3 | 3.5h |
| Fri (D53) | PeopleOps wrap | — | — | Finalize PeopleOps, `docs/postmortem-peopleops.md`, tag `v0.2-peopleops-final` | Full suite | `docs: peopleops final postmortem` | — | 3.5h |
| Sat (D54) | **Review** | — | Redo mini-ORM query builder from memory | — | — | — | Answer Week-9 Qs unscripted | 2.5h |

---

## 9. Daily Plan — Week 10: WareFlow Scaffold, DDD-lite, Unit of Work

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
|---|---|---|---|---|---|---|---|---|
| Mon (D55) | Bounded contexts, aggregates | DDD Distilled Ch.1-3 | — | New repo `wareflow/`, define Inventory + Fulfillment context boundaries in `docs/architecture.md` | — | `docs: wareflow bounded contexts` | Q1 | 3.5h |
| Tue (D56) | Aggregate roots, entities vs value objects | DDD Distilled Ch.4-5 | — | `Warehouse`, `StockLevel` entities (Inventory context) | Domain model unit tests | `feat: inventory domain models` | — | 3.5h |
| Wed (D57) | Unit of Work pattern | Cosmic Python (free online) Ch.6 | UoW demo: 2 repos, 1 commit boundary | `UnitOfWork` class wrapping SQLAlchemy session | Test rollback on partial failure | `feat: unit of work implementation` | Q2 | 3.5h |
| Thu (D58) | Repository pattern formalized | Cosmic Python Ch.2 | — | `StockLevelRepository`, `WarehouseRepository` conforming to Phase 1's `Repository[T]` protocol | Repository tests | `feat: inventory repositories` | — | 3.5h |
| Fri (D59) | Domain services vs application services | DDD Distilled Ch.6 | — | `receive_stock` and `dispatch_transfer` domain services using UoW | Service unit tests (mocked UoW) | `feat: receive/dispatch stock services` | Q3 | 3.5h |
| Sat (D60) | **Review** | — | Redo UoW demo from memory | Re-read context boundary doc, check for leaks | Full suite | — | Answer Week-10 Qs unscripted | 2.5h |

---

## 10. Daily Plan — Week 11: RabbitMQ, Fulfillment Context

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
|---|---|---|---|---|---|---|---|---|
| Mon (D61) | RabbitMQ concepts: exchange, queue, binding | RabbitMQ tutorial 1-3 | Standalone producer/consumer script | Add `rabbitmq` to Docker Compose | Verify management UI reachable | `chore: rabbitmq service` | Q1 | 3.5h |
| Tue (D62) | Publishing domain events after commit | — | — | `event_bus.py`: publish `StockDispatched`/`StockReceived` after UoW commit | Test event published only on successful commit | `feat: event bus wrapper` | — | 3.5h |
| Wed (D63) | Consumer idempotency, ack/nack | RabbitMQ tutorial 4-5 | Duplicate-message idempotency demo | Fulfillment consumer for `StockDispatched` → creates `Reservation` | Test duplicate event doesn't double-reserve | `feat: fulfillment stock-dispatched consumer` | Q2 | 3.5h |
| Thu (D64) | Dead-letter queues | RabbitMQ tutorial 6 (DLQ) | — | Configure DLQ, force a bad message, inspect it manually | Test message lands in DLQ after 3 failures | `feat: dead-letter queue config` | — | 3.5h |
| Fri (D65) | Transfer receipt endpoint | — | — | `POST /transfers/{id}/receive` — confirms receipt, publishes `StockReceived` | Integration test full dispatch→receive flow | `feat: transfer receipt endpoint` | Q3 | 3.5h |
| Sat (D66) | **Review** | — | Redo idempotency demo from memory | Trace one event end-to-end by hand, write it in `docs/notes.md` | Full suite | — | Answer Week-11 Qs unscripted | 2.5h |

---

## 11. Daily Plan — Week 12: Postgres Deep Dive — Isolation, MVCC, Deadlocks, Partitioning

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
|---|---|---|---|---|---|---|---|---|
| Mon (D67) | MVCC mechanics | Postgres docs Ch.13 §3 | Two-transaction MVCC demo (concurrent reads never block) | Reservation creation with row-level locking | Test concurrent reservations for same stock | `feat: reservation row locking` | Q1 | 3.5h |
| Tue (D68) | Isolation levels: read committed, repeatable read, serializable | Postgres docs Ch.13 §2 | Reproduce a non-repeatable read, then prevent it | Choose and document isolation level for reservations | — | `docs: isolation level decision for reservations` | — | 3.5h |
| Wed (D69) | Deadlocks in practice | Postgres docs Ch.13 §3.4 | Reproduce a deadlock with opposing lock order across 2 warehouses | Fix lock ordering in transfer dispatch logic | Test no deadlock under simulated concurrent transfers | `fix: consistent lock ordering in transfers` | Q2 | 3.5h |
| Thu (D70) | Table partitioning | Postgres docs Ch.5 §11 | — | Partition `stock_movements` by month | Test queries against old vs current partition | `perf: partition stock_movements by month` | — | 3.5h |
| Fri (D71) | Query plan reading under partitioning | — | — | `EXPLAIN ANALYZE` before/after partitioning, record in `docs/partitioning-notes.md` | — | `docs: partitioning benchmark notes` | Q3 | 3.5h |
| Sat (D72) | **Review** | — | Redo deadlock reproduction from memory | — | Full suite | — | Answer Week-12 Qs unscripted | 2.5h |

---

## 12. Daily Plan — Week 13: Kafka Intro, Outbox Gap, Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
|---|---|---|---|---|---|---|---|---|
| Mon (D73) | Kafka concepts: topics, partitions, consumer groups | Confluent Kafka intro | Single-topic produce/consume mini project | — | Test consumer receives all messages | `feat: kafka mini exercise` | Q1 | 3.5h |
| Tue (D74) | Kafka vs RabbitMQ tradeoffs | — | — | Write `docs/rabbitmq-vs-kafka.md` decision record for WareFlow | — | `docs: messaging tech decision record` | — | 3.5h |
| Wed (D75) | The commit-then-publish gap | — | — | Deliberately break the "DB commit succeeds, publish fails" case, observe the bug | Test reproducing the gap (expected to fail — document why) | `docs: outbox pattern gap identified` | Q2 | 3.5h |
| Thu (D76) | Stock-by-warehouse reporting endpoint | — | — | `GET /warehouses/{id}/stock` with pagination | Integration test | `feat: warehouse stock reporting` | — | 3.5h |
| Fri (D77) | CI update, full pipeline | — | — | CI with Postgres+Redis+RabbitMQ service containers, all green | Full suite both remaining projects | `ci: add rabbitmq service container` | Q3 | 3.5h |
| Sat (D78) | **Phase 3 wrap review** | — | Redo Kafka mini exercise from memory | `docs/postmortem-phase3.md`, tag `v0.3-phase3` | Full suite | `docs: phase 3 postmortem` | Mock-answer all Phase-3 questions timed | 2.5h |

---

## 13. Deliverables & GitHub Milestones

**Milestone: `Phase 3 — PeopleOps final + WareFlow v0.1`**
- [ ] PeopleOps: Celery Beat scheduled accrual + reminder jobs, tagged final
- [ ] WareFlow: Inventory + Fulfillment bounded contexts, UoW, repositories
- [ ] RabbitMQ event flow (dispatch → receive) with DLQ demonstrated
- [ ] Reproduced and fixed a real deadlock; documented lock-ordering fix
- [ ] `stock_movements` partitioned with before/after `EXPLAIN ANALYZE`
- [ ] `docs/rabbitmq-vs-kafka.md` and `docs/outbox-gap.md` written
- [ ] Tag: `v0.3-phase3`

## 14. Skills Acquired Checklist
- [ ] Celery Beat scheduling
- [ ] Repository / Service Layer / Unit of Work as a named, deliberate pattern
- [ ] DDD-lite: bounded contexts, aggregates
- [ ] RabbitMQ: exchanges, queues, ack/nack, DLQ
- [ ] Kafka basics, contrasted with RabbitMQ
- [ ] Postgres MVCC, isolation levels, deadlocks — debugged firsthand
- [ ] Table partitioning with measured before/after impact
- [ ] Identified (not yet solved) the outbox-pattern gap — seed for Phase 5

---

**Next:** Phase 4 moves into microservices infrastructure — Nginx, API
Gateway, full CI/CD with deploy, Prometheus/Grafana/Sentry, S3/MinIO —
building CarePoint and LedgerBase.
