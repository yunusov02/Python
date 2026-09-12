# Project 7 — FleetTrack

**Fleet & delivery logistics platform — event-driven: Outbox + CQRS + Saga**

| | |
|---|---|
| Domain | Logistics |
| Level | Middle |
| Phase | 5 — Scaling & Advanced Architecture |
| Weeks | 19–20 (D109–D120) |
| Stack | Python, FastAPI, PostgreSQL (**JSONB + GIN**), RabbitMQ, Prometheus/Alertmanager/Grafana, OpenTelemetry, Pact, **React + TS + TanStack Query**, **WebSockets** (required) + SSE (comparison), Redis pub/sub (WS fan-out) |
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
7. `fleettrack-web/`: the dispatcher table, **polling first, then WebSocket push**
7a. A **WebSocket** dashboard that survives two replicas (fan-out over Redis
   pub/sub), authenticates the socket, heartbeats, and reconnects — plus an
   **SSE** variant, so the polling/SSE/WS comparison is something you built
7b. `POST /deliveries/{id}/cancel` returning **`202 Accepted`** with a saga
   status resource to poll — the REST contract for a long-running operation

**Proof it is correct**
8. A fault-injection test: kill RabbitMQ mid-relay → **no event lost**, retried
   on the next poll
9. A Pact contract on `DeliveryStatusChanged`, failing CI on a shape change
10. An idempotency test: the same event applied twice does not double-apply
11. An **outbox-lag Grafana panel** with a threshold you can justify — and an
    **Alertmanager rule** on it that fires when you stop the relay
12. One **trace** spanning API → outbox → relay → RabbitMQ → projection consumer,
    because `traceparent` rides in the message headers
13. `outbox.payload` as **JSONB** with a GIN index, queried by `payload->>'driver_id'`
14. An outbox **cleanup** job, and a written **event-schema versioning** rule
    (v1 → v2 with an upcaster) tested against Pact

**Written artefacts**
12. `docs/cancellation-saga.md` — designed on paper **before** any code
13. The CQRS staleness tradeoff, written down with the WareFlow contrast
15. The polling-vs-SSE-vs-WebSocket comparison, having built all three

---

## 3. Scope

**In scope**
- Deliveries, drivers, status state machine
- The Outbox pattern for guaranteed publishing
- A CQRS read model for the dispatcher dashboard
- A choreographed cancellation saga (overview depth, one hands-on example)
- Outbox-lag metric on Grafana
- A polling dispatcher frontend, then the same view over **WebSocket push** (required) and **SSE** (comparison)
- Trace propagation through the broker; alerting on outbox lag; outbox cleanup; JSONB payloads; event versioning

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
A table that polls; then the same view over a **WebSocket** push — with auth on
connect, heartbeats, reconnection, and fan-out across replicas — and, for the
comparison, over SSE. Build polling first so the push versions have a baseline.

### 5.6 Long-running operations over REST
Cancelling triggers a saga that finishes seconds later. The endpoint returns
**`202 Accepted`** with `Location: /sagas/{id}`; the client polls that resource
(`pending | compensating | completed | failed`). Returning `200` and pretending
it finished is the lie this section exists to stop.

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

**Polling, SSE, WebSocket:** the dashboard polls first. Then the same read model
is pushed over a **WebSocket** and over **Server-Sent Events**, specifically so
the trade-off is something you have felt from all three sides.

| | Polling | SSE | WebSocket push |
|---|---|---|---|
| Direction | Client pulls | Server → client only | Both ways |
| Latency | Bounded by the interval | Immediate | Immediate |
| Transport | Plain HTTP | Plain HTTP, `text/event-stream`, auto-reconnect built into `EventSource` | Upgrade; Nginx needs `Upgrade`/`Connection` headers and a long `proxy_read_timeout` |
| Server cost | N × 1/interval requests | N held connections | N held connections |
| Failure mode | Misses nothing; just late | Reconnects itself; `Last-Event-ID` can resume | Silent disconnect looks like "no updates" unless you heartbeat |
| Auth | Normal headers | Normal headers (cookie or query param — `EventSource` cannot set headers) | Token on the first message or a short-lived ticket in the query string; never the long-lived token in the URL |
| **Scaling** | Stateless | Stateful: with 2 replicas, an event consumed by replica A must reach a client connected to B → **fan-out via Redis pub/sub** | Same |
| Complexity | Trivial | Low | Reconnection, **backpressure** (a slow client must not stall the consumer), heartbeat, auth |

**The WebSocket build, concretely:** `/ws/dispatch` endpoint in FastAPI; the
read-model consumer publishes each change to a Redis channel; every replica
subscribes and forwards to its own connected sockets; a `ping` every 20s and a
client that reconnects with backoff; a bounded per-socket send queue that drops
or closes a client that cannot keep up. Run **two API replicas** behind Nginx
and prove a change lands on a socket connected to the *other* replica. Write
down what Nginx needed (`proxy_http_version 1.1`, `Upgrade`, `Connection
"upgrade"`, timeouts) and what would change with sticky sessions vs pub/sub.

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

outbox(id, aggregate_type, aggregate_id, event_type, event_version,
       payload jsonb, trace_context jsonb, created_at, sent_at NULL)
    -- partial index WHERE sent_at IS NULL, for efficient relay polling
    -- GIN index ON payload jsonb_path_ops, for ops queries by driver/delivery
    -- cleanup: rows with sent_at < now() - interval '7 days' archived/deleted nightly

sagas(id, delivery_id, status, step, started_at, finished_at NULL, error NULL)
    -- the pollable resource behind 202 Accepted

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
| POST | `/deliveries/{id}/cancel` | dispatcher | Triggers the saga. **`202 Accepted`** + `Location: /sagas/{id}` |
| GET | `/sagas/{id}` | dispatcher+ | Saga status resource |
| WS | `/ws/dispatch` | dispatcher+ | Push variant of the dashboard; ticket auth, heartbeat |
| GET | `/sse/dispatch` | dispatcher+ | SSE variant, `Last-Event-ID` resume |
| GET | `/ops/outbox?driver_id=` | ops_manager | JSONB query `payload->>'driver_id'` via the GIN index |
| GET | `/ops/outbox-lag` | ops_manager | Also exported as a metric |

---

## 11. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL** | Deliveries, events, **the outbox table**, and `delivery_view` | The outbox living in the same database as the state change is the entire point — it is what makes the write atomic |
| **Partial index** `WHERE sent_at IS NULL` | The relay's polling query | Without it the relay scans a table that only grows |
| **RabbitMQ** | Carries relayed events to the read-model consumer, the saga steps, and downstream billing | Reused from WareFlow; the transport is not the lesson this time — the *guarantee* is |
| **Outbox relay worker** | A separate process: poll → publish → mark sent | Claim rows with `FOR UPDATE SKIP LOCKED` so multiple replicas are safe |
| **Prometheus + Grafana** | **Outbox lag** = `now() - oldest unsent row`; queue depth; consumer lag on the read model; WebSocket connections per replica | Outbox lag is the single most important metric this project produces. If the relay stops, everything downstream is silently stale while the API looks perfectly healthy |
| **Alertmanager** | `outbox_lag_seconds > 30 for 2m` → page. Stop the relay, watch it fire, restart, watch it resolve | LedgerBase built the alerting stack; this is the first alert whose threshold you had to *derive* (from relay poll interval + tolerable dashboard staleness) |
| **OpenTelemetry through the broker** | The API span's `traceparent` is stored in `outbox.trace_context`; the relay puts it in the AMQP headers; the consumer extracts it and continues the trace | A trace that stops at "published" is half a trace. Seeing API → relay → consumer → projection as one waterfall — with the outbox lag visible as a gap — is the demo of this project |
| **JSONB + GIN** | `outbox.payload jsonb` with `GIN (payload jsonb_path_ops)`; ops queries by `payload->>'driver_id'` or `@>` containment | Payloads are semi-structured by nature; know when JSONB is right (heterogeneous event payloads) and when it is a schema you were too lazy to design |
| **Redis pub/sub** | Fan-out of read-model changes to WebSocket/SSE connections across replicas | The only Redis use in FleetTrack, and it is not a cache — say so |
| **Outbox cleanup** | Beat job: delete (or move to `outbox_archive`) rows sent more than 7 days ago, in batches | The partial index keeps the relay fast; nothing keeps the table small unless you do |
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
- Add the **outbox-lag metric** to the Phase 4 Prometheus/Grafana stack, and the
  **Alertmanager rule**; fire it by stopping the relay
- `outbox.payload` as JSONB + GIN; `GET /ops/outbox?driver_id=`
- `traceparent` into `outbox.trace_context` → AMQP headers → consumer; one trace
  end to end in Tempo/Jaeger
- Outbox cleanup job

### Stage 2 — CQRS read model, saga, real-time *(D115–D120, Week 20)* *(v2: +3 days)*
- `delivery_view` read model table
- Consumer updating `delivery_view` on each event — **idempotently**
- `GET /dispatch/dashboard` reading only from `delivery_view`
- `fleettrack-web/`: dispatcher table polling every few seconds
- **Design the cancellation saga on paper first** → `docs/cancellation-saga.md`
- Implement the 3-step choreographed saga; `POST .../cancel` → `202` + `/sagas/{id}`
- **WebSocket** dashboard: ticket auth, heartbeat, reconnect, bounded send queue,
  Redis pub/sub fan-out, **two replicas behind Nginx**
- **SSE** variant with `Last-Event-ID`; the three-way comparison written up
- **Event schema versioning**: `DeliveryStatusChanged` v2 adds a field and renames
  one; consumer upcasts v1 → v2; Pact covers both shapes
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
| **Alert** | The `outbox_lag` alert fires within its `for` window and resolves after the relay restarts |
| **WebSocket** | A change consumed by replica A reaches a client connected to replica B; a client that stops reading is disconnected, not the consumer stalled; an expired ticket is refused on connect; a dropped connection is re-established and no update is lost (the client refetches on reconnect) |
| SSE | `Last-Event-ID` resume delivers exactly the events missed during a disconnect |
| 202 | Cancel returns `202` immediately; `/sagas/{id}` moves `pending → completed`; a mid-saga failure shows `failed` with the compensation state |
| Tracing | One `trace_id` spans the API request, the relay publish and the projection consumer |
| JSONB | The `driver_id` query uses the GIN index (`EXPLAIN` shows a bitmap index scan) |
| Versioning | A v1 payload from the old publisher is upcast and applied by the v2 consumer; Pact fails CI if v2 drops a field v1 consumers need |
| Cleanup | Sent rows older than the retention are removed; unsent rows never are |

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
- [ ] WebSocket dashboard: auth, heartbeat, reconnect, backpressure, fan-out across two replicas
- [ ] SSE variant; polling/SSE/WebSocket comparison written from having built all three
- [ ] `202 Accepted` + saga status resource
- [ ] Alertmanager rule on outbox lag, fired and resolved
- [ ] Trace continues through the outbox and broker into the consumer
- [ ] JSONB payload + GIN; ops query uses the index
- [ ] Event schema v1 → v2 with an upcaster, Pact-covered
- [ ] Outbox cleanup job
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
10. Your dashboard has two API replicas. A driver updates a delivery; how does the
    update reach a WebSocket connected to the *other* replica?
11. How do you authenticate a WebSocket, and why not put the JWT in the URL?
12. What is backpressure on a WebSocket, and what happens to your consumer if one
    client reads slowly and you did nothing about it?
13. SSE or WebSocket for a dashboard that only ever pushes — which and why?
14. Why does `cancel` return `202` and not `200`? What does the client do next?
15. How does a trace survive a trip through RabbitMQ?
16. How did you derive the 30-second alert threshold on outbox lag?
17. When is JSONB the right column type, and when is it a design smell?
18. How do you change an event's schema without breaking a consumer that has not deployed yet?

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
- A WebSocket that works with one replica and silently drops half the updates with two
- No heartbeat, so a dead socket looks like a quiet fleet
- An unbounded per-client send buffer, so one slow browser stalls the read-model consumer
- The JWT in the WebSocket URL — logged by every proxy on the path
- `200 OK` from `cancel` while the saga is still running
- Publishing a v2 event before every consumer can read it
- An outbox table that grows forever because nothing deletes sent rows

---

## 17. How Real Companies Differ

At large scale the outbox relay becomes a **CDC pipeline** (Debezium) reading the
write-ahead log instead of polling a table: lower lag, no polling load, but WAL
access and more operational surface. Named here as the natural next step; out of
scope to build.

---

## 18. ML Extension — Stage 2 *(Week 20, +2 days)*

> **Why here.** `delivery_events`' timestamps between `assigned` and `delivered`
> are a ready-made regression target, and this feeds directly into Track B's
> **Project 24** (Year-2 Analytics + Streaming, Phase 11), which streams this
> same project's events.

**Scope (in)**
- A regression model (`scikit-learn`) predicting delivery duration from: driver,
  time of day, day of week, number of prior deliveries that day
- Trained on synthetic seed data expanded to a few thousand deliveries
- Compared against a naive baseline (the driver's historical median duration)

**Scope (out)** — no serving, no real-time ETA on the dispatcher dashboard (that
would need this wired into `delivery_view`, a real Phase 9/10-level project).

**Definition of Done**
- [ ] Model trained, MAE compared to the per-driver median baseline
- [ ] `docs/eta-notes.md` written

**Interview question this adds**
1. Why compare against the driver's own historical median instead of the global average?
