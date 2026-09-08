# Project 4 — WareFlow

**Multi-warehouse management system with pick/pack workflows**

| | |
|---|---|
| Domain | Logistics / WMS |
| Level | Middle |
| Phase | 3 — Distributed Systems Primitives |
| Weeks | 10–13 (D55–D78) |
| Stack | Python, FastAPI, SQLAlchemy, PostgreSQL (MVCC, isolation levels, partitioning), **RabbitMQ**, Pact, Docker Compose |
| Repo | `wareflow/` |

> **This is the project where transactions and locking stop being an exercise and
> become the whole point.**

---

## 1. Business Problem

A growing retailer now operates 3 warehouses. Stock must be received, transferred
between warehouses, and reserved/picked for outbound orders — and a transfer or
pick that fails partway through must never leave inventory numbers lying.

---

## 2. The Core Insight This Project Teaches

**A warehouse transfer is not one transaction.**

Stock leaves warehouse A today. It arrives at warehouse B hours or days later,
and only on *receipt confirmation*. You cannot hold a database transaction open
for two days. So the process spans **multiple transactions connected by events**:

```
dispatch  → tx1: decrement source, transfer(dispatched)  → publish StockDispatched
             ... hours or days ...
receive   → tx2: increment destination, transfer(received) → publish StockReceived
```

Everything else in this project — the bounded contexts, the Unit of Work, the
message broker, the DLQ — follows from that one fact.

---

## 3. Outcomes — what exists when the project is finished

**A working system**
1. Two bounded contexts with no type leakage between them
2. A Unit of Work that commits across multiple repositories as one unit
3. A two-phase transfer working end to end, connected by events over RabbitMQ
4. Reservations created by a consumer reacting to a dispatch event
5. A DLQ you have configured, poisoned deliberately, and inspected by hand
6. `stock_movements` partitioned by month, with the query plans to justify it

**Proof it is correct**
7. A test that kills the consumer mid-processing and proves no message is lost
8. A Pact contract pinning the `StockDispatched` payload shape, failing CI on drift
9. A deadlock you reproduced on purpose, then fixed with consistent lock ordering
10. `EXPLAIN ANALYZE` before and after partitioning, recorded

**Written artefacts — these matter as much as the code**
11. `docs/architecture.md` — the context boundary, and where you found leaks
12. `docs/rabbitmq-vs-kafka.md` — a real decision record for *this* system
13. `docs/partitioning-notes.md` — the plans, the key, and when you would not partition
14. **The observed outbox bug** — the "DB commit succeeded, publish failed" case,
    triggered on purpose, documented, and deliberately left unfixed

---

## 4. Scope

**In scope**
- Receive stock at a warehouse
- Two-step transfers: dispatch → receive
- Reserve stock for an order
- Pick / pack workflow
- Stock by warehouse, paginated
- Event-driven communication between two bounded contexts
- Dead-letter queue
- Table partitioning
- Resource-scoped permissions

**Out of scope — felt as gaps, written down, solved later**

| Gap | Where it closes |
|---|---|
| **Outbox pattern** — you will *observe* the bug, not fix it | Phase 5 (FleetTrack) |
| Read replicas for stock-level queries | Phase 5 (DocuVault) |
| RabbitMQ clustering | Named only |
| **Caching — deliberately none.** Stock changes too often. Knowing when caching is *wrong* is an interview answer | n/a |

---

## 5. Roles & Permissions

This project introduces **resource-scoped permissions** — the new idea, and the
reason auth is worth revisiting here at all.

| Role | Can | Cannot |
|---|---|---|
| **`warehouse_worker`** *(scoped to assigned warehouses)* | Receive stock at their warehouse, dispatch transfers **out of their warehouse only**, confirm receipt **at their warehouse only**, pick and pack | Act on a warehouse they are not assigned to; cancel a transfer |
| **`warehouse_manager`** *(scoped to their site)* | Everything a worker can at their site, plus cancel a transfer and adjust stock with a reason | Act on another site |
| **`inventory_controller`** | View stock across all warehouses, run reconciliation, adjust with a reason | Dispatch or receive on behalf of a site |
| **`fulfillment_operator`** | Create reservations, manage pick lists | Move stock between warehouses |

**The lesson:** permission here depends on the *record*, not only on the role. A
worker at Warehouse A dispatching from Warehouse B must be refused — and the
refusal must not depend on the UI hiding a button.

---

## 6. Architecture — DDD-lite, two bounded contexts

```
Inventory context           Fulfillment context
  - Warehouse                 - Order
  - StockLevel                - Reservation
  - StockMovement             - PickList
       │                            ▲
       └── publishes events ────────┘  (RabbitMQ)
```

**Formal layering:**

```
Repository (per aggregate)
    → UnitOfWork   (wraps a transaction across multiple repositories,
                    commits or rolls back as one unit)
        → Service  (orchestrates the UoW, publishes domain events AFTER commit)
```

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
    event_bus.py       # thin wrapper over RabbitMQ publish/consume
    di_container.py    # mini DI container (Week 10 mini-project, applied for real)
```

**Boundary rule:** Fulfillment types must never appear in Inventory's domain
layer. The two contexts communicate **only** through events. A shared import is
the leak to hunt for on D60.

---

## 7. Domain Model

```
warehouses(id, name, location)

warehouse_assignments(user_id, warehouse_id, role)   -- resource-scoped auth

stock_levels(id, warehouse_id -> warehouses.id, product_id, qty)
    UNIQUE(warehouse_id, product_id)

stock_movements(id, warehouse_id, product_id, delta, reason, ref_id, created_at)
    -- RANGE PARTITIONED BY month (Week 12)

transfers(id, from_warehouse_id, to_warehouse_id,
          status[dispatched|received|cancelled], created_at)

transfer_items(id, transfer_id -> transfers.id, product_id, qty)

reservations(id, order_ref, warehouse_id, product_id, qty, status, created_at)

pick_lists(id, reservation_id, status, picked_by, picked_at)
```

`stock_levels.qty` is the current number; `stock_movements` is the log behind it —
the same event-log/materialized-sum pattern as StockPilot, now across warehouses.

---

## 8. Domain Events

| Event | Published by | Consumed by | Effect |
|---|---|---|---|
| `StockDispatched` | Inventory, **after** the dispatch commit | Fulfillment | Creates a `Reservation` |
| `StockReceived` | Inventory, **after** the receipt commit | Fulfillment | Confirms / releases reservation state |

The `StockDispatched` payload shape is pinned by a **Pact message-contract test**
between the publisher and the consumer, so a shape change fails CI before it
reaches anything downstream.

**Consumers must be idempotent.** RabbitMQ redelivers on nack, on consumer crash,
and on connection loss. Duplicate delivery is normal operation, not an incident.

---

## 9. API Design

| Method | Path | Scope | Notes |
|---|---|---|---|
| POST | `/warehouses/{id}/stock/receive` | Own warehouse | Inbound stock |
| POST | `/transfers` | Own source warehouse | Dispatch: decrements source, publishes `StockDispatched` |
| POST | `/transfers/{id}/receive` | Own destination warehouse | Confirms receipt, publishes `StockReceived` |
| POST | `/reservations` | Fulfillment | Row-level locking |
| POST | `/pick-lists/{id}/complete` | Own warehouse | |
| GET | `/warehouses/{id}/stock` | Scoped | Paginated |

---

## 10. Database Design

| Item | Detail |
|---|---|
| `stock_levels` | `UNIQUE(warehouse_id, product_id)` |
| `stock_movements` | Composite index `(warehouse_id, product_id)` |
| `stock_movements` | **Range partitioned by month** — done in Week 12 *after* simulating growth past a few million rows and feeling the seq-scan pain on old-data queries |
| Isolation | Reservation creation runs at a **deliberately chosen and documented** isolation level. Write down what anomaly you are preventing |
| Locking | Consistent lock ordering in transfer dispatch, adopted **after** reproducing a real deadlock |

**On partitioning:** the point is not that partitioning is good. The point is that
you measured a query getting slow on old data, chose a key that matches the access
pattern (date), verified pruning in the plan, and can say when you would *not*
partition.

---

## 11. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL** | Both contexts, one database, separate schemas or table prefixes | Two contexts do not require two databases at this scale — say why |
| **RabbitMQ — topic exchange** | Carries `StockDispatched` and `StockReceived` from Inventory to Fulfillment | The transfer genuinely spans transactions. This is the felt need |
| **RabbitMQ — DLQ** | On the Fulfillment consumer queue, after 3 failed attempts | Configure it, **force a poison message through it, and inspect the message by hand at least once** so it is not just a textbook term |
| **RabbitMQ management UI** | Exposed in Compose | Your only visibility this phase. You need to *see* queues, bindings and depths, not trust they exist |
| **Pact** | Message contract on `StockDispatched`, run in CI | Publisher and consumer are in the same repo today and will not be forever |
| **Docker Compose** | `api` + `postgres` + `redis` + **`rabbitmq`** + a consumer process | This is where Compose starts to strain — note the moment |
| **GitHub Actions** | CI now spins up Postgres + Redis + RabbitMQ service containers | |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Any cache** | Stock numbers change constantly and are read for decisions. A stale stock level causes an oversell. **This is the project where you write down that caching would be wrong** |
| **Kafka** | You need work queues with per-message ack and a DLQ, not a replayable partitioned log. Write the comparison (`docs/rabbitmq-vs-kafka.md`) rather than adding a second broker |
| **Prometheus** | Still the RabbitMQ UI only. Write down the Phase 4 callback: queue-depth alerting |
| **An outbox table** | You are meant to feel its absence. → Phase 5 |

---

## 12. Build Plan (consolidated)

### Stage 1 — Contexts, UoW, repositories *(D55–D60, Week 10)*
- New repo `wareflow/`; define the Inventory + Fulfillment boundary in
  `docs/architecture.md` **before** writing code
- `Warehouse`, `StockLevel` entities (Inventory)
- `UnitOfWork` wrapping the SQLAlchemy session
- `StockLevelRepository`, `WarehouseRepository` conforming to Phase 1's
  `Repository[T]` protocol
- `receive_stock` and `dispatch_transfer` domain services using the UoW
- Review pass: re-read the boundary doc, hunt for leaks

### Stage 2 — Messaging *(D61–D66, Week 11)*
- Add `rabbitmq` to Compose **with the management UI exposed**
- `event_bus.py`: publish `StockDispatched` / `StockReceived` **after** UoW commit
- Fulfillment consumer for `StockDispatched` → creates a `Reservation`
- **Pact message-contract test** pinning the payload shape
- Configure a **DLQ**, force a bad message through it, inspect it by hand
- `POST /transfers/{id}/receive` → publishes `StockReceived`
- Trace one event end to end by hand, write it up in `docs/notes.md`

### Stage 3 — Postgres deep dive *(D67–D71, Week 12)*
- Reservation creation with row-level locking
- **Choose and document** the isolation level for reservations
- Reproduce a deadlock on purpose, then fix it with consistent lock ordering
- Partition `stock_movements` by month
- `EXPLAIN ANALYZE` before/after → `docs/partitioning-notes.md`

### Stage 4 — Kafka comparison, the outbox gap, wrap *(D74–D78, Week 13)*
- `docs/rabbitmq-vs-kafka.md` — a real decision record for WareFlow
- **Deliberately break** the "DB commit succeeds, publish fails" case, observe the
  inconsistency, write it down. **Do not fix it** — Phase 5 does
- `GET /warehouses/{id}/stock` with pagination
- CI green with Postgres + Redis + RabbitMQ
- `docs/postmortem-phase3.md`, tag `v0.3-phase3`

---

## 13. Testing Strategy

| Layer | What |
|---|---|
| Unit | Domain rules per context, with repositories faked |
| Integration | UoW commits across two repositories as one unit; a failure rolls both back |
| Integration | Publish `StockDispatched`, assert the Fulfillment consumer reacts correctly |
| **Resilience** | **Kill the consumer mid-processing** — the message is requeued, not lost, because you ack *after* processing |
| Idempotency | Deliver the same event twice → one reservation, not two |
| Contract | Pact on `StockDispatched`, failing CI on a shape change |
| Concurrency | Two reservations for the same stock; the deadlock reproduction and its fix |
| Performance | `EXPLAIN ANALYZE` before/after partitioning, pruning verified |
| DLQ | Poison message fails 3 times, lands in the DLQ, is inspected |
| Authorization | A worker at Warehouse A cannot dispatch from Warehouse B — tested at the API, not assumed from the UI |

---

## 14. Definition of Done

- [ ] Two bounded contexts, no type leakage, boundary documented
- [ ] UoW commits/rolls back across multiple repositories as one unit
- [ ] Events published only **after** commit
- [ ] Resource-scoped permissions enforced and tested
- [ ] Pact contract test green in CI
- [ ] DLQ configured and a poison message inspected by hand
- [ ] Consumer crash does not lose a message
- [ ] Deadlock reproduced and fixed by lock ordering
- [ ] Isolation level chosen and justified in writing
- [ ] `stock_movements` partitioned, with before/after plans recorded
- [ ] `docs/architecture.md`, `docs/rabbitmq-vs-kafka.md`, `docs/partitioning-notes.md`, `docs/postmortem-phase3.md`
- [ ] **The outbox gap documented, not solved**
- [ ] Tag `v0.3-phase3`

---

## 15. Scaling Notes (written)

- `stock_movements` at 100M rows — the partitioning strategy you already applied,
  and what you would do next (archival, a rollup table)
- What happens if RabbitMQ itself must scale — clustering, quorum queues; named,
  out of scope
- Where Compose stopped feeling manageable, and what that implies

---

## 16. Interview Questions This Project Should Let You Answer

1. Why is a warehouse transfer modeled as two events, not one transaction?
2. What is the difference between a Repository and a Unit of Work, precisely?
3. Explain MVCC — why do two concurrent reads never block each other in Postgres?
4. Walk me through a deadlock you actually reproduced, and how consistent lock
   ordering avoids it.
5. Which isolation level did you use for reservations, and what anomaly does it
   prevent?
6. RabbitMQ vs Kafka — when would you pick each?
7. What guarantees does a DLQ give you, and what does it *not* give you?
8. When should a consumer ack — and what breaks if it acks early?
9. Why did you partition `stock_movements`, by what key, and how did you verify
   pruning?
10. How do bounded contexts prevent a change in Fulfillment from forcing a change
    in Inventory?
11. Where is caching the *wrong* answer, and why is this project an example?
12. You published after commit. What can still go wrong?

---

## 17. Common Mistakes to Watch For

- Acking a RabbitMQ message before processing succeeds — loses messages on crash
- Modeling a transfer as one big transaction across two warehouses
- Leaking Fulfillment types into Inventory's domain layer
- Publishing the event inside the transaction instead of after commit
- A non-idempotent consumer under at-least-once delivery
- Partitioning speculatively instead of after measuring the pain
- Enforcing warehouse scoping in the UI only

---

## 18. How Real Companies Differ

Real WMS platforms use the **outbox pattern** precisely because "commit to the DB,
then publish to the broker" is not atomic. You are meant to *feel* this gap now,
not have it solved for you — and FleetTrack in Phase 5 is where you close it.
