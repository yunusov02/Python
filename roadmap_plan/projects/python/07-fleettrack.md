# Project 7 — FleetTrack

**Fleet & delivery logistics platform — event-driven: Outbox + CQRS + Saga**

| | |
|---|---|
| Domain | Logistics |
| Level | Middle |
| Phase | 5 — Scaling & Advanced Architecture |
| Weeks | 19–20 (D109–D120) |
| Stack | Python, FastAPI, PostgreSQL, RabbitMQ, Prometheus/Grafana, Pact, **React + TS + TanStack Query**, WebSockets (stretch) |
| Repo | `fleettrack/` + `fleettrack-web/` |

> **This project exists to close one specific gap you documented in Phase 3
> Week 13:** "the DB commit succeeded but the broker publish failed." Same system
> family, same problem, now actually solved. Do not treat the Outbox pattern as a
> new topic — treat it as the answer to a bug you already watched happen.

---

## 1. Business Problem

A delivery company with a fleet of drivers needs near-real-time tracking of
delivery status across multiple steps (assigned → picked up → in transit →
delivered), reliable event publishing to a downstream analytics feed, and a
dispatcher view that never shows stale or duplicated events even when the broker
retries.

**The stake that justifies the Outbox pattern:** a lost `DeliveryStatusChanged`
event silently breaks downstream billing. Not a crash — a wrong invoice, weeks
later, that nobody can explain.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Deliveries moving through a validated status state machine
2. Every status change writing its event to an **outbox row in the same transaction**
3. A relay worker publishing outbox rows to RabbitMQ and marking them sent
4. A `delivery_view` CQRS read model, kept current by a consumer
5. A dispatcher dashboard reading **only** the read model
6. A 3-step choreographed cancellation saga
7. `fleettrack-web/`: the dispatcher table, polling

**Proof it is correct**
8. A fault-injection test: kill RabbitMQ mid-relay → **no event lost**, retried
   on the next poll
9. A Pact contract on `DeliveryStatusChanged`, failing CI on a shape change
10. An idempotency test: the same event applied twice does not double-apply
11. An **outbox-lag Grafana panel** with a threshold you can justify

**Written artefacts**
12. `docs/cancellation-saga.md` — designed on paper **before** any code
13. The CQRS staleness tradeoff, written down with the WareFlow contrast
14. The polling-vs-push comparison, having built both

---

## 3. Scope

**In scope**
- Deliveries, drivers, status state machine
- The Outbox pattern for guaranteed publishing
- A CQRS read model for the dispatcher dashboard
- A choreographed cancellation saga (overview depth, one hands-on example)
- Outbox-lag metric on Grafana
- A polling dispatcher frontend, plus a WebSocket-push stretch alternative

**Out of scope — named**

| Deferred | Why |
|---|---|
| Orchestrated saga with a dedicated coordinator | Named; you build the choreographed one and must be able to compare |
| Exactly-once semantics | Partially covered by Phase 3's idempotent-consumer work; genuine exactly-once is a much bigger claim than it sounds |
| CDC / Debezium reading the WAL instead of polling | The natural next step at scale. Named, not built |
| **Caching — none.** Dashboard reads are already fast via the read model | Adding a cache in front of a read model is caching a cache |

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`driver`** | See own assigned deliveries, advance own delivery through the status machine (picked up → in transit → delivered) | See other drivers' deliveries; assign work; cancel |
| **`dispatcher`** | See the full dashboard, create deliveries, assign and reassign drivers, cancel a delivery (triggering the saga) | Retroactively edit a delivery's event history |
| **`ops_manager`** | Everything a dispatcher can, plus outbox and queue health views, and replaying a stuck event | Alter `delivery_events` — the log is append-only |
| **`billing` (machine)** | Consume `DeliveryStatusChanged` from the broker | Call the API; it is a downstream consumer, not a client |

**The rule that shapes the model:** `delivery_events` is append-only. A status
change is a new row, never an edit. The current status is the latest event — the
same event-log discipline as StockPilot's stock movements and LedgerBase's journal.

---

## 5. Functional Modules

### 5.1 Delivery lifecycle
Create, assign, and advance a delivery through a validated state machine. Illegal
transitions are refused, not silently accepted.

### 5.2 Outbox
Every status change writes both the state change and an outbox row **in one
transaction**. A relay worker then publishes and marks the row sent.

### 5.3 Read model
A consumer projects events into `delivery_view`, denormalized specifically for the
dashboard's query shape.

### 5.4 Cancellation saga
Three steps across contexts, coordinated by events.

### 5.5 Dispatcher UI
A table that polls; and, as a stretch, the same view over a WebSocket push.

---

## 6. The Outbox Pattern (the centrepiece)

```
Write path:      status update  +  outbox row inserted in ONE transaction
Relay process:   poll unsent rows → publish to RabbitMQ → mark sent
Delivery:        at-least-once  →  the consumer MUST be idempotent
```

**The rule that makes it work:** the outbox insert is in the **same transaction**
as the state change. Put it anywhere else and you have moved the gap, not closed it.

**What it guarantees:** if the transaction commits, the event *will* eventually be
published — the relay retries until it succeeds.
**What it does not guarantee:** that the event is published exactly once, or
immediately. Duplicates and lag are normal. Design for both.

**Relay implementation:** compare Celery Beat polling every few seconds against a
dedicated loop. Pick one, document why, and be aware that under multiple replicas
you need a lock or a `FOR UPDATE SKIP LOCKED` claim so two relays do not publish
the same row twice.

---

## 7. CQRS (applied, with the tradeoff written down)

The dispatcher dashboard reads `delivery_view`, rebuilt from the same events the
relay publishes. It is **eventually consistent** and explicitly *not*
real-time-guaranteed.

**Write down why that is acceptable here:** a few seconds of staleness on a
dashboard is fine. It would **not** have been fine for stock reservation back in
WareFlow, where a stale number causes an oversell. That contrast — same technique,
opposite verdict — is the interview answer.

**Polling vs push:** the dashboard polls. Week 20's stretch mini-project rebuilds
the same read model behind a **WebSocket push**, specifically so the tradeoff is
something you have felt on both sides rather than picked once and never revisited.

| | Polling | WebSocket push |
|---|---|---|
| Latency | Bounded by the interval | Immediate |
| Server cost | N clients × 1/interval requests | N held connections |
| Failure mode | Misses nothing; just late | Silent disconnect looks like "no updates" |
| Complexity | Trivial | Reconnection, backpressure, auth on the socket |

---

## 8. Saga — cancellation after pickup

Cancelling a delivery after pickup requires three steps across contexts, and no
single transaction can cover them:

1. Reverse the driver assignment
2. Notify the customer
3. Credit back the fee

Implemented as a **choreographed saga** — each step listens for the previous
step's event.

**Design it on paper first** (`docs/cancellation-saga.md`), then build it. Write
down honestly where a compensating action could fail and what you would do
(retry with backoff, alert a human). This is overview depth, not production
grade — say so rather than overclaiming.

**Choreographed vs orchestrated:** choreography has no central coordinator, so
there is no single place to ask "where is this saga?" That is precisely its
weakness, and why real systems with more than three steps usually orchestrate.

---

## 9. Domain Model

```
drivers(id, name, status)

deliveries(id, driver_id, status, created_at)

delivery_events(id, delivery_id, from_status, to_status, created_at)
    -- append-only

outbox(id, aggregate_type, aggregate_id, event_type, payload,
       created_at, sent_at NULL)
    -- partial index WHERE sent_at IS NULL, for efficient relay polling

delivery_view(id, driver_name, status, last_updated)   -- CQRS read model
```

**Status state machine:** `created → assigned → picked_up → in_transit →
delivered`, plus `cancelled` from any pre-delivery state.

---

## 10. API Design

| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/deliveries` | dispatcher | |
| POST | `/deliveries/{id}/assign` | dispatcher | |
| PATCH | `/deliveries/{id}/status` | driver (own) / dispatcher | State-machine validated; writes the outbox row in the same tx |
| GET | `/dispatch/dashboard` | dispatcher+ | Reads `delivery_view` **only** — never `deliveries` |
| POST | `/deliveries/{id}/cancel` | dispatcher | Triggers the saga |
| GET | `/ops/outbox-lag` | ops_manager | Also exported as a metric |

---

## 11. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL** | Deliveries, events, **the outbox table**, and `delivery_view` | The outbox living in the same database as the state change is the entire point — it is what makes the write atomic |
| **Partial index** `WHERE sent_at IS NULL` | The relay's polling query | Without it the relay scans a table that only grows |
| **RabbitMQ** | Carries relayed events to the read-model consumer, the saga steps, and downstream billing | Reused from WareFlow; the transport is not the lesson this time — the *guarantee* is |
| **Outbox relay worker** | A separate process: poll → publish → mark sent | Claim rows with `FOR UPDATE SKIP LOCKED` so multiple replicas are safe |
| **Prometheus + Grafana** | **Outbox lag** = `now() - oldest unsent row`; queue depth; consumer lag on the read model | Outbox lag is the single most important metric this project produces. If the relay stops, everything downstream is silently stale while the API looks perfectly healthy |
| **Pact** | Contract test on `DeliveryStatusChanged` | Reused from WareFlow, not re-derived |
| **WebSocket (stretch)** | The push variant of the dispatcher dashboard | Built to compare, not to replace |
| **Docker Compose** | Same stack as Phase 4 — **no new services** | Notable in itself: this project's difficulty is design, not infrastructure |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Redis cache** | The read model already exists to make reads fast. A cache in front of a read model is a second copy of a copy — with a second invalidation problem |
| **Kafka** | Tempting here, because "event streaming". But you need a work queue with per-message ack, not a replayable partitioned log. Say what would change your mind: a consumer that needs to replay history from the beginning |
| **Debezium / CDC** | The natural replacement for the polling relay at scale. Named, not built — and you should be able to explain what it buys (no polling, lower lag) and costs (WAL access, more operational surface) |
| **A saga orchestrator framework** | You are building choreography by hand precisely to feel why an orchestrator exists |

---

## 12. Build Plan (consolidated)

### Stage 1 — Outbox *(D109–D114, Week 19)*
- New repo `fleettrack/`: `Delivery`, `DeliveryEvent`, `outbox` models
- Status-update service: state change + outbox row in **one transaction**
- Outbox relay worker: poll → publish → mark sent
- **Fault injection:** kill RabbitMQ mid-relay, confirm no event is lost and it is
  retried on the next poll
- Add the **outbox-lag metric** to the Phase 4 Prometheus/Grafana stack

### Stage 2 — CQRS read model & saga *(D115–D120, Week 20)*
- `delivery_view` read model table
- Consumer updating `delivery_view` on each event — **idempotently**
- `GET /dispatch/dashboard` reading only from `delivery_view`
- `fleettrack-web/`: dispatcher table polling every few seconds
- **Design the cancellation saga on paper first** → `docs/cancellation-saga.md`
- Implement the 3-step choreographed saga
- *(Stretch)* the WebSocket-push variant, and the written comparison
- Tag `v0.1-fleettrack`

---

## 13. Testing Strategy

| Layer | What |
|---|---|
| **Fault injection** | Kill the RabbitMQ connection mid-relay — **no event lost**, retried next poll. This is the whole point of the pattern; prove it, do not assert it |
| Atomicity | Force the transaction to fail after the outbox insert — neither the state change nor the outbox row survives |
| Contract | Pact on `DeliveryStatusChanged`, failing CI on a payload shape change |
| **Idempotency** | Replay the same event twice — `delivery_view` is not double-applied |
| Concurrency | Two relay replicas do not publish the same row twice |
| State machine | Every illegal transition is refused |
| Saga | Each compensating step, plus at least one deliberate mid-saga failure |
| Metric | Stop the relay; assert outbox lag rises and the alert threshold is crossed |

---

## 14. Definition of Done

- [ ] Outbox row and state change committed in one transaction, proven by a
      forced failure
- [ ] Relay survives a broker kill with zero event loss
- [ ] Relay safe under two replicas
- [ ] Outbox-lag metric on a Grafana panel, with a justified alert threshold
- [ ] `delivery_view` read model; the dashboard reads it exclusively
- [ ] Read-model consumer proven idempotent
- [ ] CQRS staleness tradeoff written down, with the WareFlow contrast
- [ ] `docs/cancellation-saga.md` written **before** the code
- [ ] 3-step choreographed saga working, failure modes documented
- [ ] Pact contract green in CI
- [ ] `fleettrack-web/` dispatcher table live
- [ ] Polling-vs-push comparison written *(stretch: both built)*
- [ ] Tag `v0.1-fleettrack`

---

## 15. Interview Questions This Project Should Let You Answer

1. Walk me through exactly how the outbox pattern guarantees at-least-once
   delivery — what failure mode does it close that WareFlow had?
2. What does the outbox *not* guarantee?
3. When is CQRS worth the complexity, and when is it overkill? Give me an example
   of each from your own work.
4. Choreographed vs orchestrated saga — which did you build, and what would make
   you switch?
5. How would you detect and alert on outbox relay lag in production, and at what
   threshold?
6. Two relay replicas — how do you stop them publishing the same row twice?
7. Polling vs WebSocket push for a dashboard — you've built both; when does each win?
8. Why not Kafka here?
9. What would CDC change about this design?

---

## 16. Common Mistakes to Watch For

- The outbox insert **not** in the same transaction as the state change — you have
  moved the gap, not closed it
- Building a CQRS read model for a query that did not need one
- A non-idempotent read-model consumer under at-least-once delivery
- Treating a choreographed saga's compensating actions as guaranteed instead of
  "at-least-once, needs monitoring"
- Polling the outbox without a partial index, so the relay slows as the table grows
- Two relay replicas double-publishing because rows are not claimed
- Monitoring the API's health but not the relay's lag — the system looks fine while
  going quietly stale

---

## 17. How Real Companies Differ

At large scale the outbox relay becomes a **CDC pipeline** (Debezium) reading the
write-ahead log instead of polling a table: lower lag, no polling load, but WAL
access and more operational surface. Named here as the natural next step; out of
scope to build.
