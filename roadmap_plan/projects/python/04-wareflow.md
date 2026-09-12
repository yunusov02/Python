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
11. RabbitMQ configured for **durability**: durable exchange/queues, persistent
    messages, **publisher confirms**, `prefetch_count` — proven by restarting the
    broker with messages in flight and losing none
12. A **`SERIALIZABLE` retry loop** built and compared with the `REPEATABLE READ`
    choice, with a reproduced write-skew anomaly behind the decision
13. `lock_timeout`, `statement_timeout` and `idle_in_transaction_session_timeout`
    set deliberately, with a demonstration of what each one prevents
14. A **BRIN** index and a **covering index** (`INCLUDE`), each chosen from a plan
15. **Keyset pagination** on `GET /warehouses/{id}/stock`
16. A partition-maintenance job that creates next month's partition before it is needed

**Written artefacts — these matter as much as the code**
11. `docs/architecture.md` — the context boundary, and where you found leaks
12. `docs/rabbitmq-vs-kafka.md` — a real decision record for *this* system
13. `docs/partitioning-notes.md` — the plans, the key, and when you would not partition
17. **The observed outbox bug** — the "DB commit succeeded, publish failed" case,
    triggered on purpose, documented, and deliberately left unfixed
18. `docs/rabbitmq-ops-notes.md` — durability, confirms, prefetch, TTL, heartbeats

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
- RabbitMQ durability, publisher confirms, QoS
- Isolation-level experiments including `SERIALIZABLE` + retry
- Postgres timeouts, BRIN and covering indexes, partition maintenance

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

**Durability is not the default.** A non-durable queue vanishes on broker
restart; a non-persistent message (`delivery_mode=1`) vanishes with it; a
publish without **publisher confirms** may never have reached the broker at all.
Configure all three (`durable=True`, `delivery_mode=2`, `confirm_delivery`),
then restart RabbitMQ with 100 messages in the queue and count them afterwards.
Set `prefetch_count` (QoS) so one slow consumer does not hoard messages other
workers could process, and set a heartbeat so a dead connection is noticed.
`docs/rabbitmq-ops-notes.md` records each setting and what you observed without it.

---

## 9. API Design

| Method | Path | Scope | Notes |
|---|---|---|---|
| POST | `/warehouses/{id}/stock/receive` | Own warehouse | Inbound stock |
| POST | `/transfers` | Own source warehouse | Dispatch: decrements source, publishes `StockDispatched` |
| POST | `/transfers/{id}/receive` | Own destination warehouse | Confirms receipt, publishes `StockReceived` |
| POST | `/reservations` | Fulfillment | Row-level locking |
| POST | `/pick-lists/{id}/complete` | Own warehouse | |
| GET | `/warehouses/{id}/stock` | Scoped | **Keyset** paginated (`cursor` on `(product_id)`), served from the covering index |

---

## 10. Database Design

| Item | Detail |
|---|---|
| `stock_levels` | `UNIQUE(warehouse_id, product_id)` |
| `stock_movements` | Composite index `(warehouse_id, product_id)` |
| `stock_movements` | **Range partitioned by month** — done in Week 12 *after* simulating growth past a few million rows and feeling the seq-scan pain on old-data queries |
| Isolation | Reservation creation runs at a **deliberately chosen and documented** isolation level. Write down what anomaly you are preventing. **Build the `SERIALIZABLE` version too**: catch `40001 serialization_failure` and retry with backoff; reproduce a **write skew** under `REPEATABLE READ` that `SERIALIZABLE` refuses. Then choose |
| Timeouts | `lock_timeout` (a blocked `ALTER TABLE` or `FOR UPDATE` gives up instead of queuing everyone behind it), `statement_timeout` (a runaway report cannot hold a connection forever), `idle_in_transaction_session_timeout` (a client that opened a transaction and went away stops holding locks). Set per role/connection, demonstrate each |
| `stock_movements(created_at)` | **BRIN** instead of B-tree on the partitioned append-only log — a fraction of the size, and correct because rows arrive in time order. Compare size and plan with a B-tree |
| `stock_levels` | **Covering index** `(warehouse_id, product_id) INCLUDE (qty)` so the stock lookup is an **index-only scan** (`Heap Fetches: 0` in the plan) |
| Partition maintenance | Who creates next month's partition? A Beat job (or `pg_partman`) creating partitions one month ahead, plus a `DEFAULT` partition as a safety net. A missing partition means inserts fail at midnight on the 1st |
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
| **Docker Compose** | `api` + `postgres` + **`rabbitmq`** + a consumer process. Redis is **not** used in WareFlow — remove it from this Compose, or keep it with a comment saying CarePoint needs it | This is where Compose starts to strain — note the moment. An unused service in Compose is a small lie about your architecture |
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
- **Durability pass**: durable queues, persistent messages, publisher confirms,
  `prefetch_count`, heartbeat. Restart the broker with messages in flight;
  count. `docs/rabbitmq-ops-notes.md`
- `POST /transfers/{id}/receive` → publishes `StockReceived`
- Trace one event end to end by hand, write it up in `docs/notes.md`

### Stage 3 — Postgres deep dive *(D67–D71, Week 12)*
- Reservation creation with row-level locking
- **Choose and document** the isolation level for reservations — after building
  the `SERIALIZABLE` + retry-on-`40001` version and reproducing write skew
- Reproduce a deadlock on purpose, then fix it with consistent lock ordering
- Set `lock_timeout` / `statement_timeout` / `idle_in_transaction_session_timeout`;
  demonstrate each (a blocked DDL, a runaway query, an abandoned transaction)
- Partition `stock_movements` by month; partition-maintenance job + `DEFAULT` partition
- **BRIN** on `stock_movements(created_at)`, size and plan vs B-tree
- **Covering index** on `stock_levels`, index-only scan verified
- `EXPLAIN ANALYZE` before/after → `docs/partitioning-notes.md`

### Stage 4 — Kafka comparison, the outbox gap, wrap *(D74–D78, Week 13)*
- `docs/rabbitmq-vs-kafka.md` — a real decision record for WareFlow
- **Deliberately break** the "DB commit succeeds, publish fails" case, observe the
  inconsistency, write it down. **Do not fix it** — Phase 5 does
- `GET /warehouses/{id}/stock` with **keyset** pagination
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
| **Durability** | Broker restart with N messages queued → N messages after restart; a publish with confirms disabled and the broker down is *not* silently lost from the publisher's point of view |
| QoS | With `prefetch_count=1`, a slow consumer does not starve a fast one |
| **Serializable** | The write-skew scenario commits under `REPEATABLE READ` and raises `40001` under `SERIALIZABLE`; the retry loop succeeds on the second attempt |
| Timeouts | A `FOR UPDATE` blocked longer than `lock_timeout` fails fast; a query longer than `statement_timeout` is cancelled |
| Indexes | BRIN and B-tree sizes recorded; covering-index plan shows `Heap Fetches: 0` |
| Partitions | Inserting a row for next month succeeds because the partition already exists (or lands in `DEFAULT`, and that is alerted) |
| Keyset | Stable, gap-free pagination while stock rows are being inserted |

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
- [ ] `SERIALIZABLE` + retry built and compared; write skew reproduced
- [ ] Durable queues, persistent messages, publisher confirms, prefetch — broker-restart test green
- [ ] `lock_timeout` / `statement_timeout` / `idle_in_transaction_session_timeout` set and demonstrated
- [ ] BRIN + covering index chosen from plans; keyset pagination on stock
- [ ] Partition-maintenance job + `DEFAULT` partition
- [ ] `docs/rabbitmq-ops-notes.md`
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
13. What is write skew, and which isolation level in Postgres prevents it? Show me
    the retry loop.
14. Durable queue, persistent message, publisher confirm — what does each protect
    against, and what is still not guaranteed with all three?
15. What does `prefetch_count` do, and what goes wrong at the default of unlimited?
16. Why `lock_timeout` — what happens to a `FOR UPDATE` that waits forever, and to
    the queue of sessions behind it?
17. BRIN vs B-tree — when is BRIN right and when is it useless?
18. What is an index-only scan and how did you get `Heap Fetches: 0`?
19. Who creates next month's partition, and what happens if nobody does?

---

## 17. Common Mistakes to Watch For

- Acking a RabbitMQ message before processing succeeds — loses messages on crash
- Modeling a transfer as one big transaction across two warehouses
- Leaking Fulfillment types into Inventory's domain layer
- Publishing the event inside the transaction instead of after commit
- A non-idempotent consumer under at-least-once delivery
- Partitioning speculatively instead of after measuring the pain
- Enforcing warehouse scoping in the UI only
- Non-durable queues that look fine until the first broker restart
- Publishing without confirms and assuming the broker has the message
- Choosing an isolation level without reproducing the anomaly it prevents
- No `lock_timeout`, so one blocked migration queues every request behind it
- Partitioning without a maintenance job — the first insert of the month fails
- Leaving Redis in Compose because "it was there", with nothing using it

---

## 18. How Real Companies Differ

Real WMS platforms use the **outbox pattern** precisely because "commit to the DB,
then publish to the broker" is not atomic. You are meant to *feel* this gap now,
not have it solved for you — and FleetTrack in Phase 5 is where you close it.

---

## 19. ML Extension — Stage 5 *(Week 13, +3 days)*

> **Why here — and why this is new ground.** WareFlow has no Track B counterpart
> at all; this section closes that gap. `stock_movements`, partitioned and
> indexed since Stage 3, is exactly the shape of data anomaly detection needs:
> high volume, timestamped, one row per event.

**Scope (in)**
- An `IsolationForest` (`scikit-learn`) over `stock_movements`, features: `delta`
  magnitude, time-of-day, warehouse, product — flags movements that look
  statistically unlike the rest (a plausible proxy for data-entry errors or
  theft, named honestly as a proxy, not a fraud system)
- Run as a one-off batch script against the partitioned table (reads by month
  partition, not the whole table) — reusing the BRIN-indexed time-range query
  pattern from Stage 3
- A written review of the top 20 flagged movements: how many look like real
  anomalies vs. noise

**Scope (out)**

| Deferred | Why |
|---|---|
| Real-time flagging on write | This is a batch review tool, not a blocking control |
| A labeled fraud dataset / supervised model | None exists; unsupervised is the honest choice here |
| Alerting on flagged movements | Would need the Phase 4 observability stack wired to a model — named, not built |

**Definition of Done**
- [ ] Isolation Forest run against a full partition, `docs/anomaly-notes.md`
      written with the top-20 review
- [ ] The proxy nature of "anomalous ≠ fraudulent" stated explicitly

**Interview questions this adds**
1. Why unsupervised anomaly detection here instead of a classifier?
2. What would you need to turn this batch review into a real-time control?
