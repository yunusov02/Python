# PHASE 5 — Scaling & Advanced Architecture
### Weeks 19–24 (6 weeks) · 36 working days

---

## 1. Learning Goals
- Close the outbox gap you deliberately left open in Phase 3: guarantee an
  event is published if and only if the transaction that produced it
  committed.
- Apply CQRS where it actually earns its complexity (a reporting read model
  that would otherwise require expensive joins on the write model) — and be
  able to argue when it *doesn't* earn it.
- Understand Saga at the level of a real interview answer: what it trades
  away (atomicity) for what it buys (no distributed transaction).
- Get real, hands-on Elasticsearch/OpenSearch experience: indexing,
  querying, and why it beats `LIKE '%term%'` at scale.
- Get Kubernetes fundamentals hands-on with `kind`/`minikube` — enough to
  deploy DocuVault and explain Pods/Services/Deployments/ConfigMaps in an
  interview, not to become a K8s specialist.
- Build two more React/TS frontends (FleetTrack's dispatcher view,
  DocuVault's search page) reusing Phase 4's setup instead of relearning
  it — polling and debounced-input patterns, the two UI problems these
  particular backends actually create.
- Go past *watching* consensus happen on etcd (Week 22) to *implementing*
  it: build a working Raft node from scratch — leader election, log
  replication, and the safety properties that make it correct — tested
  under a real simulated network partition, not just narrated in an
  interview answer.

## 2. Technologies Introduced
Outbox pattern, CQRS, Saga (overview + one hands-on choreographed example),
Elasticsearch/OpenSearch, database replication (read replicas), sharding
(conceptual + one hands-on partitioning-by-key exercise), consistent
hashing (hand-rolled ring with virtual nodes, benchmarked against naive
modulo hashing), Kubernetes (`kind`/`minikube`, Pods, Deployments,
Services, ConfigMaps, Secrets), Raft/consensus — conceptual fluency via a
real local 3-node etcd cluster (Week 22), *then* a from-scratch Raft
implementation (Weeks 23–24: leader election, log replication, safety
properties, partition testing), GitOps (conceptual — ArgoCD/Flux
reconciliation model, contrasted with manual `kubectl apply`), React +
TypeScript + TanStack Query (continued from Phase 4 — polling for
FleetTrack's dashboard, a WebSocket-push stretch alternative, debounced
search input for DocuVault).

Deliberately not yet: Event Sourcing as a full system (overview only, in
Week 20), full production Kubernetes (Helm, operators — named as "beyond
this bootcamp's scope" so you know the term without overclaiming depth),
an actually-installed GitOps controller (conceptual fluency only here —
same treatment as sharding: know when you'd reach for it, don't build it
on a `kind` cluster where it wouldn't earn its complexity).

---

## 3. PROJECT 7 — FleetTrack (Fleet & Delivery Logistics Platform)

**Business Problem:** A delivery company with a fleet of drivers needs
real-time-ish tracking of delivery status across multiple steps (assigned →
picked up → in transit → delivered), reliable event publishing to a
downstream analytics feed, and a dispatcher-facing view that must never
show stale or duplicated events even if the message broker retries.

**Requirements**
- Functional: create deliveries, assign drivers, update status through a
  defined state machine, dispatcher dashboard query (read-optimized).
- Non-functional: an event must be published for every status change,
  guaranteed — a lost `DeliveryStatusChanged` event silently breaks
  downstream billing, which is the concrete stake that justifies the
  Outbox pattern here.

**Architecture — Outbox pattern, applied for real:**
```
Write path: status update + outbox row inserted in ONE transaction
Relay process: polls outbox table, publishes to RabbitMQ, marks row sent
                (at-least-once — consumer must be idempotent, a callback to Phase 3)
```
This closes the exact gap you documented in Phase 3 Week 13 — same system
family (event-driven logistics), same problem, now actually solved.

**CQRS applied:** the dispatcher dashboard is a read model (`delivery_view`
table) rebuilt from the same events the outbox relay publishes — kept
eventually consistent, explicitly *not* real-time-guaranteed, and you write
down why that tradeoff is acceptable here (a few seconds of staleness on a
dashboard is fine; it would not be fine for the stock-reservation logic
back in WareFlow). The dashboard itself polls for updates (below) rather
than pushing them — a second, honest "not yet" call: Week 20's stretch
mini-project rebuilds the same read model behind a WebSocket push instead,
specifically so the polling-vs-push tradeoff is something you've felt on
both sides, not just picked once and never revisited.

**Saga (overview, one hands-on example):** a delivery cancellation after
pickup needs to: reverse a driver assignment, notify the customer, and
credit back a fee — three steps across contexts, no single transaction can
cover it. You implement this as a **choreographed saga** (each step listens
for the previous step's event) and write down, honestly, where a
compensating action could fail and what you'd do (retry with backoff,
alert a human) — this is an overview-depth exercise, not production-grade.

**ER Diagram (textual)**
```
drivers(id, name, status)
deliveries(id, driver_id, status, created_at)
delivery_events(id, delivery_id, from_status, to_status, created_at)
outbox(id, aggregate_type, aggregate_id, event_type, payload, created_at, sent_at NULL)
delivery_view(id, driver_name, status, last_updated)   -- CQRS read model
```

**API Design**
```
POST /deliveries
PATCH /deliveries/{id}/status
GET  /dispatch/dashboard          # reads delivery_view, not deliveries
POST /deliveries/{id}/cancel      # triggers the saga
```

**Database Design:** `outbox` table with an index on `sent_at IS NULL` for
efficient relay polling; `delivery_view` denormalized specifically for the
dashboard query pattern.

**Caching:** dashboard reads are already fast via the read model — you
explicitly note caching would add complexity without benefit here.

**Background Jobs:** the outbox relay itself is a long-running worker
(Celery beat polling every few seconds, or a dedicated loop — you compare
both and pick one, documenting why).

**Infrastructure:** no new Compose services — same stack, applied more
deliberately.

**CI/CD:** same pipeline pattern from Phase 4, applied to the new service
without re-deriving it — a sign the earlier investment is paying off.

**Testing Strategy:** integration test that kills the RabbitMQ connection
mid-relay and confirms no event is lost (it's just retried on next poll —
this is the whole point of the pattern, prove it under fault injection). The
outbox-relayed events (`DeliveryStatusChanged`) get the same Pact
message-contract treatment from Phase 3 — reused, not re-derived — so a
payload-shape change on the relay side fails CI before it reaches any
downstream consumer.

**Monitoring:** Grafana panel for outbox lag (`now() - oldest unsent row`)
— a concrete, interview-ready metric.

**Common Interview Questions**
1. Walk through exactly how the outbox pattern guarantees at-least-once
   delivery — what failure mode does it close that Phase 3's WareFlow had?
2. When is CQRS worth the complexity, and when is it overkill?
3. Choreographed vs orchestrated saga — which did you build, and why?
4. How would you detect and alert on outbox relay lag in production?

**Possible Improvements:** orchestrated saga with a dedicated coordinator
for more complex cancellation flows, exactly-once semantics via idempotency
keys on the consumer side (already partially covered by Phase 3's
idempotent-consumer work).

**What Companies Usually Do Differently:** at large scale, the outbox
relay itself becomes a CDC (change-data-capture) pipeline (e.g. Debezium)
reading the WAL instead of polling a table — named here as the natural
next step, out of scope to build.

**Common Mistakes:** forgetting the outbox insert must be in the *same*
transaction as the state change (otherwise you've just moved the gap, not
closed it); building a CQRS read model for a query that didn't actually
need it; treating a choreographed saga's compensating actions as
guaranteed instead of "at-least-once, needs monitoring."

---

## 4. PROJECT 8 — DocuVault (Document Management with Search & Versioning)

**Business Problem:** A mid-size company has thousands of internal
documents (policies, contracts, reports) scattered across drives with no
real search — "find the Q3 vendor contract" means asking around, not
searching.

**Requirements**
- Functional: upload/version documents (each edit creates a new version,
  old ones retained), full-text search across content and metadata,
  tag-based filtering.
- Non-functional: search must handle typos/partial matches reasonably and
  stay fast as the corpus grows past what `LIKE '%term%'` can handle.

**Architecture:** documents stored in MinIO/S3 (from Phase 4), metadata +
version history in Postgres, full-text index in Elasticsearch/OpenSearch
kept in sync via events (another outbox-relay consumer, reusing FleetTrack's
pattern rather than reinventing it).

**ER Diagram (textual)**
```
documents(id, title, current_version_id, created_by)
document_versions(id, document_id, s3_key, version_number, created_at)
tags(id, name)
document_tags(document_id, tag_id)
```

**API Design**
```
POST /documents                      # first upload
POST /documents/{id}/versions        # new version
GET  /documents/search?q=&tags=      # hits elasticsearch
GET  /documents/{id}/versions        # history
```

**Database Design:** Postgres remains the source of truth for metadata/
versions; Elasticsearch is a derived index, never authoritative — you
state this explicitly, since "which store is the source of truth" is a
standard system-design interview trap.

**Search Implementation:** analyzer configuration for reasonable typo
tolerance (fuzziness), boosting title matches over body matches — you
tune this against a small real test corpus and record what changed.

**Infrastructure:** `elasticsearch`/`opensearch` added to Compose; this is
also the point where Compose officially becomes unwieldy (6+ services) —
you write down the exact list and use it as the honest justification for
this week's Kubernetes work, rather than doing K8s because it's trendy.

**Kubernetes (hands-on, `kind` or `minikube`):** deploy DocuVault's
services as Pods behind a Service, config via ConfigMap, secrets via
Secret objects, and a Deployment with 2 replicas — enough to explain in an
interview what each object does and why, explicitly scoped as
fundamentals, not production operations (no Helm, no operators, no
autoscaling — named as next steps beyond this bootcamp). What makes
Kubernetes's own control plane agree on cluster state across nodes —
Raft-based consensus, the same primitive underneath RabbitMQ clustering
and Kafka's controller election — is used here without being explained on
Monday; Tuesday opens that box for real with a 3-node local etcd cluster
(etcd runs Raft under the hood, and is in fact what `kind`'s own control
plane uses one instance of).

**Replication/Sharding (conceptual + one hands-on piece):** set up a
Postgres read replica locally, route the search-indexing consumer's reads
to the replica, and write a decision record on what you'd shard by if
`document_versions` ever needed it (document_id is the natural shard key)
— sharding itself is not implemented, deliberately, since it's rarely
justified below very large scale and you should be able to say so in an
interview. *How* you'd distribute those shards (consistent hashing vs
naive `hash(key) % N`) is answered with a real, hand-built consistent-
hashing ring (virtual nodes included) benchmarked against naive modulo
hashing on a synthetic key set — the decision record's shard-key
recommendation gets a measured redistribution-percentage number behind it,
not just an assertion.

**Testing Strategy:** test that the Elasticsearch index recovers from a
missed event (a `reindex` endpoint you build specifically for this — since
ES is derived data, it must always be rebuildable from Postgres).

**Common Interview Questions**
1. Why is Elasticsearch never the source of truth here?
2. Walk through what a Kubernetes Deployment gives you over `docker run`.
3. What would you shard `document_versions` by, and why — and what does
   your consistent-hashing benchmark add to that answer over a hand-wave?
4. How do you keep a derived search index consistent with its source of
   truth over time?
5. What does Kubernetes's own control plane use consensus for, and what
   would you expect to happen if you killed its etcd leader?

**Possible Improvements:** access-control-aware search (don't show
documents the requester can't read — a real production concern, deferred
as noted complexity), semantic/vector search on top of keyword search.

**What Companies Usually Do Differently:** most production search systems
separate the indexing pipeline into its own scaled-independently service
much sooner than DocuVault does — sufficient here since your corpus is a
learning-scale dataset, but worth naming.

**Common Mistakes:** treating Elasticsearch as authoritative and losing
data when it's wiped; deploying to Kubernetes without ever having run the
services with plain Compose first (you didn't make this mistake — note why
that ordering mattered); sharding prematurely.

---

## 5. PROJECT — Raft Consensus, Implemented From Scratch

**Business Problem (why this earns two weeks):** Week 22 had you watch a
3-node etcd cluster elect a leader and survive a kill — genuinely useful,
but it's the same gap as reading about a deadlock instead of reproducing
one, which is exactly why Phase 3 made you reproduce a real deadlock
instead of just describing MVCC. Kubernetes's control plane, RabbitMQ
clustering (named in Phase 3), and Kafka's controller election all lean on
this same primitive. "I've read the Raft paper" and "I've implemented
leader election and watched it survive a partition I induced myself" are
different interview answers, and only one of them survives a follow-up
question.

**Scope, stated honestly:** this is not a production-grade consensus
library — no dynamic membership changes, no log compaction/snapshotting,
no optimized batching. It is a correct, tested implementation of the core
of the Raft paper (Ongaro & Ousterhout): leader election, log replication,
and the five safety properties, running as real separate processes
communicating over local HTTP, not a single-process simulation.

**Architecture (3–5 node cluster, one process per node)**
```
Each node: Follower | Candidate | Leader  (state machine, one of three)

RequestVote RPC   — candidate asks for votes during an election
AppendEntries RPC — leader replicates log entries AND serves as heartbeat
                     (empty AppendEntries = heartbeat, when no new entries)

Node state (persisted conceptually, in-memory here):
  currentTerm, votedFor, log[] (each entry: term, command)
Volatile state:
  commitIndex, lastApplied  (all nodes)
  nextIndex[], matchIndex[]  (leader only, per follower)
```

**Week 23 — Leader Election & Log Replication**
Build the state machine (Follower/Candidate/Leader transitions), the
election timeout (randomized, per the paper, specifically to make
split-votes rare rather than impossible — and you'll cause one on purpose
to see why randomization matters), `RequestVote` RPC handling and term
comparison, then `AppendEntries` for both heartbeats and real log
replication, `nextIndex`/`matchIndex` tracking, and the leader's commit-
index advancement rule (a majority must have replicated an entry before
it's committed). By Friday, five real processes on your machine elect a
leader and replicate a client-submitted command to a majority.

**Week 24 — Safety Properties Under Fault**
The Raft paper names five safety properties (Election Safety, Leader
Append-Only, Log Matching, Leader Completeness, State Machine Safety) —
Monday is spent stating each in your own words with a concrete scenario
where violating it would corrupt the system. Tuesday–Thursday you build a
fault-injection harness: drop messages between a chosen subset of nodes
(simulating a network partition), kill a node process outright, and kill
the leader specifically mid-replication — then assert, automatically, that
no committed log entry is ever lost, overwritten, or observed differently
by two nodes. Friday applies the implementation to something concrete: it
becomes the coordination layer for a toy leader-election use case (which
of N workers is allowed to run a scheduled job right now) — the exact
mechanism `system-design-problems.md`'s SD14 (Distributed Job Scheduler)
asks you to design on paper, and the direct foundation for Phase 6's real
Distributed Job Scheduler build (Week 30).

**Testing Strategy:** unit tests for the state machine's transition rules
(what turns a Follower into a Candidate, what turns a Candidate back into a
Follower on discovering a higher term); an integration test that starts a
5-node cluster, kills the leader, and asserts a new leader is elected
within a bounded number of election timeouts; a partition test that splits
5 nodes into a 3-node majority and a 2-node minority and asserts *only* the
majority side can elect a leader and commit entries (the minority must not
— this is the concrete, testable meaning of "split-brain prevention");
a "torture test" that randomly kills and restarts nodes and drops
messages for an extended run, asserting log consistency holds throughout,
not just at the end.

**Common Interview Questions**
1. Why is the election timeout randomized, specifically — what goes wrong
   with a fixed timeout?
2. Walk through exactly what makes a log entry "committed," and why a
   leader can't unilaterally commit an entry the moment it appends it
   locally.
3. Two nodes have logs that disagree past a certain index — walk through
   how `nextIndex` converges them to agreement.
4. In your partition test, why does the minority side correctly fail to
   elect a leader instead of just running slower?
5. What does Raft NOT give you that a real production system (etcd, your
   Week 22 exercise) adds on top?

**Possible Improvements:** log compaction/snapshotting (an unbounded log is
the most obvious gap versus production Raft), dynamic cluster membership
changes (adding/removing a node without downtime), batching multiple
client commands per `AppendEntries` round trip for throughput.

**What Companies Usually Do Differently:** nobody hand-rolls Raft for a
real system — they reach for etcd, Consul, or a Raft library (`hashicorp/
raft`, `etcd-io/raft`) exactly because getting the edge cases (log
compaction, membership changes, network partitions lasting arbitrarily
long) production-correct is a multi-year effort. You build it once, by
hand, specifically so reaching for the library later is an informed
choice, not a black box — the same reasoning Phase 8 uses for not
adopting LangChain until you've built a tool loop by hand first.

**Common Mistakes:** committing a log entry based on it merely being
*sent* to a majority instead of *acknowledged* by a majority; forgetting
that a candidate must revert to follower the instant it sees a higher term
in any RPC, even a rejected one; not resetting the election timer on a
valid heartbeat, causing spurious elections; testing only the happy path
and never actually inducing a partition or a leader kill mid-replication.

---

## 6. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| Outbox pattern mini demo (standalone, before FleetTrack) | 19 | The pattern in isolation, no domain noise |
| Mini CQRS read-model projector (rebuild a view table from an event log) | 20 | CQRS mechanics |
| WebSocket push upgrade for the FleetTrack dispatcher dashboard (contrast with Wednesday's polling version, before/after request-volume + staleness numbers) | 20 | Polling vs push, felt on both sides of the same read model |
| Elasticsearch indexing demo (index 1000 fake documents, query, tune analyzer) | 21 | ES fundamentals before applying to DocuVault |
| Mini load balancer (round-robin over 2 backend processes) | 22 | What Kubernetes Services/kube-proxy do underneath |

---

## 7. Books & Documentation
- Martin Fowler's blog: "What do you mean by Event-Driven?" and the Outbox
  pattern write-up (microservices.io/patterns/data/transactional-outbox.html).
- *Building Microservices* (Newman) Ch. 5 (data) for CQRS/Saga sections.
- WebSocket protocol overview (MDN) — Week 20, for the dispatcher-dashboard
  push stretch mini-project.
- Elasticsearch "Getting Started" official docs (Week 21).
- Kubernetes docs: "Learn Kubernetes Basics" interactive tutorial (Week 22).
- etcd documentation (etcd.io/docs) — "Understand failovers" (Week 22).
- *Designing Data-Intensive Applications* (Kleppmann) Ch. 6 (Partitioning,
  for consistent hashing) and Ch. 9 (Consistency and Consensus, for Raft)
  — Week 22.
- Postgres docs: replication chapter (Week 22).
- Ongaro & Ousterhout, "In Search of an Understandable Consensus
  Algorithm (Extended Version)" (raft.github.io/raft.pdf) — the full
  paper, read across Weeks 23-24, the same section the same day you
  implement it, not all at once up front.
- The Secret Lives of Data (thesecretlivesofdata.com/raft) — the
  interactive Raft visualization, useful for Week 23's election/
  replication debugging when your own cluster does something you can't
  explain from logs alone.

---

## 8. Weekly Interview Question Sets

**Week 19 — Outbox**
1. What exact failure does the outbox pattern prevent that a direct
   publish-after-commit doesn't?
2. Why must the outbox insert share a transaction with the state change?
3. Also work `system-design-problems.md` SD1 (URL Shortener) and SD2 (Rate
   Limiter) this week — the first two entries in the bank, chosen as
   warm-ups.

**Week 20 — CQRS, Saga**
1. When is CQRS overkill — give a concrete example from your own projects.
2. Choreographed vs orchestrated saga — tradeoffs?
3. What does your WebSocket-push stretch version change about the
   dispatcher dashboard's failure modes versus polling (what happens on
   disconnect)?
4. Also work SD7 (News Feed/Timeline) and SD8 (Chat System) this week —
   SD8 pairs directly with the WebSocket mini-project above.

**Week 21 — Elasticsearch**
1. Why does `LIKE '%term%'` fail at scale, mechanically?
2. Inverted index — explain it in one paragraph.
3. Also work SD5 (Web Crawler) and SD15 (Typeahead/Autocomplete) this
   week — both search-shaped problems.

**Week 22 — Kubernetes, consensus, replication, sharding, consistent hashing**
1. Pod vs Deployment vs Service — what does each actually do?
2. Explain Raft leader election in your own words — what did killing the
   etcd leader actually look like?
3. Read replica vs sharding — different problems, which is which?
4. What would you shard DocuVault's data by, and why that key?
5. Consistent hashing vs `hash(key) % N` — what specifically breaks with
   the naive version when a node is added or removed, and what did your
   benchmark show?
6. Also work SD3 (Distributed Cache), SD4 (Key-Value Store, Dynamo-Style),
   SD6 (Unique ID Generator), and SD14 (Distributed Job Scheduler) this
   week — SD14's leader-election deep-dive is a direct callback to
   Tuesday's etcd cluster.

**Week 23 — Raft: leader election, log replication**
1. Why randomize the election timeout instead of using a fixed value?
2. Walk through exactly what makes a log entry "committed."
3. How does `nextIndex` converge two disagreeing logs to agreement?
4. What's the difference between an `AppendEntries` heartbeat and a real
   replication call, mechanically?

**Week 24 — Raft: safety properties, partition testing**
1. State one of the five safety properties in your own words, with a
   concrete violation scenario.
2. Walk through your partition test — why does the minority side never
   elect a leader, specifically?
3. What happens to a stale leader's uncommitted entries when a partition
   heals?
4. What does your torture test actually prove that the happy-path tests
   don't?
5. What's the difference between what you built and what etcd/Consul give
   you on top?

---

## 9. Daily Plan — Week 19: Outbox Pattern, FleetTrack Scaffold

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D109) | Outbox pattern theory | Fowler/microservices.io outbox article | Standalone outbox demo (insert + relay script) | New repo `fleettrack/`, `Delivery`, `DeliveryEvent`, `outbox` models | Model tests | `feat: fleettrack scaffold + outbox table` | Q1 | Maximum Product Subarray | FleetTrack: unsent outbox rows older than 5 minutes | 3.5h |
| Tue (D110) | Transactional outbox insert | — | — | Status-update service: state change + outbox row, one transaction | Test both happen or neither happens | `feat: transactional status update + outbox insert` | Q2 | Word Break | Rising Temperature — self-join with LAG variant | 3.5h |
| Wed (D111) | Relay process design | — | — | Outbox relay worker (poll, publish, mark sent) | Test relay publishes and marks sent correctly | `feat: outbox relay worker` | — | Longest Increasing Subsequence | FleetTrack: delivery stuck longest in one status | 3.5h |
| Thu (D112) | Fault injection on the relay | — | — | Kill RabbitMQ mid-relay, confirm no event lost, retried next poll | Integration test with simulated broker outage | `test: outbox survives broker outage` | Q3 | Partition Equal Subset Sum | FleetTrack: avg time between status transitions | 3.5h |
| Fri (D113) | Outbox lag metric | — | — | Add outbox-lag metric to Prometheus/Grafana (from Phase 4 stack) | — | `feat: outbox lag metric` | — | Insert Interval | The Most Frequently Ordered Products for Each Customer | 3.5h |
| Sat (D114) | **Review** | — | Redo outbox demo from memory | — | Full suite | — | Answer Week-19 Qs unscripted | Review: redo Thursday's problem from memory — Partition Equal Subset Sum | Review: rewrite Tuesday's query from memory, then extend it — Rising Temperature — self-join with LAG variant | 2.5h |

---

## 10. Daily Plan — Week 20: CQRS Read Model, Saga

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D115) | CQRS theory | Fowler CQRS article | Mini CQRS projector (rebuild view from event log) | `delivery_view` read model table | — | `feat: delivery_view read model` | Q1 | Merge Intervals | FleetTrack: rebuild delivery_view from delivery_events by hand | 3.5h |
| Tue (D116) | Projector consuming outbox-relayed events | — | — | Consumer that updates `delivery_view` on each event | Test view reflects latest status within expected lag | `feat: delivery_view projector` | — | Non-overlapping Intervals | Article Views I | 3.5h |
| Wed (D117) | Dispatcher dashboard endpoint; frontend — second React/TS app, this time with polling for near-real-time data (reusing Phase 4's `carepoint-web` setup, not re-deriving it) | — | — | `GET /dispatch/dashboard` reading only from `delivery_view`; `fleettrack-web/` (Vite + React + TS + TanStack Query), one page: dispatcher table polling the dashboard endpoint every few seconds | Integration test dashboard query performance vs join-based alternative; component test confirms the table re-renders on a poll tick without a full page flicker | `feat: dispatcher dashboard (cqrs read path) + fleettrack-web dispatcher view` | Q2 | Meeting Rooms | FleetTrack: drivers with the most cancelled deliveries | 3.5h |
| Thu (D118) | Saga theory: choreography vs orchestration | Newman Ch.5 saga section | — | Design the cancellation saga on paper first (`docs/cancellation-saga.md`) | — | `docs: cancellation saga design` | Q3 | Meeting Rooms II | Article Views II | 3.5h |
| Fri (D119) | Implementing the choreographed saga | — | — | 3-step cancellation saga: reverse assignment → notify → credit fee | Test each step fires on the prior step's event; test one failure path | `feat: delivery cancellation saga` | — | Maximum Subarray | FleetTrack: dispatcher dashboard — join vs read-model | 3.5h |
| Sat (D120) | **Review** | — | Redo CQRS projector from memory | Tag `v0.1-fleettrack` | Full suite | — | Answer Week-20 Qs unscripted | Review: redo Thursday's problem from memory — Meeting Rooms II | Review: rewrite Tuesday's query from memory, then extend it — Article Views I | 2.5h |

---

## 11. Daily Plan — Week 21: DocuVault Scaffold, Elasticsearch

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D121) | Inverted index concept | ES "Getting Started" | Index 1000 fake docs, run basic queries | New repo `docuvault/`, `Document`/`DocumentVersion` models | Model tests | `feat: docuvault scaffold` | Q1 | Jump Game | DocuVault: documents with the most versions | 3.5h |
| Tue (D122) | Analyzers, fuzziness, boosting | ES docs analyzers | Tune analyzer on the mini exercise corpus | `POST /documents` + MinIO upload (reusing Phase 4 presigned pattern) | Integration test upload flow | `feat: document upload` | — | Jump Game II | Fix Names in a Table | 3.5h |
| Wed (D123) | Keeping a derived index in sync | — | — | Outbox-relay-style consumer indexing new/updated docs into ES | Test index reflects new doc within expected lag | `feat: elasticsearch sync consumer` | Q2 | Gas Station | DocuVault: documents tagged with more than 3 tags | 3.5h |
| Thu (D124) | Search query design; frontend — third React/TS app, this time a controlled search input with debounced queries | — | — | `GET /documents/search?q=&tags=`; `docuvault-web/` search page: debounced search box + tag filter chips calling the endpoint via TanStack Query | Test typo tolerance, tag filter, title-boost ranking; component test confirms the query only fires after the debounce window, not on every keystroke | `feat: document search endpoint + docuvault-web search page` | — | Hand of Straights | DocuVault: latest version per document | 3.5h |
| Fri (D125) | Reindex-from-source recovery | — | — | `POST /documents/reindex` — rebuilds ES fully from Postgres | Test ES wiped, reindex restores search correctly | `feat: full reindex recovery endpoint` | Q3 | Unique Paths | Recyclable and Low Fat Products | 3.5h |
| Sat (D126) | **Review** | — | Redo indexing mini exercise from memory | — | Full suite | — | Answer Week-21 Qs unscripted | Review: redo Thursday's problem from memory — Hand of Straights | Review: rewrite Tuesday's query from memory, then extend it — Fix Names in a Table | 2.5h |

---

## 12. Daily Plan — Week 22: Kubernetes Fundamentals, Replication, Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D127) | Pods, Deployments, Services | K8s "Learn Kubernetes Basics" pt.1-2 | Mini load balancer (round-robin, 2 processes) | `kind` cluster running locally, write Deployment+Service YAML for one DocuVault service | Verify pod reachable via Service | `feat: k8s deployment for docuvault service` | Q1 | Longest Common Subsequence | DocuVault: documents never tagged | 3.5h |
| Tue (D128) | ConfigMaps, Secrets; leader election & consensus — Raft explained (leader election, log replication, majority quorum) | K8s docs pt.3 + etcd docs "Understand failovers" | Stand up a 3-node local etcd cluster, watch leader election happen | Externalize config/secrets from that service into ConfigMap/Secret; `docs/consensus-notes.md` — Raft in your own words, tied to K8s/RabbitMQ/Kafka | Verify service picks up config correctly; verify the etcd cluster elected a leader | `feat: k8s configmap + secret; docs: 3-node etcd cluster stood up` | — | Best Time to Buy and Sell Stock with Cooldown | Primary Department for Each Employee | 3.5h |
| Wed (D129) | Scaling replicas, rolling updates; GitOps (conceptual) — why `kubectl apply` by hand doesn't scale past one cluster, and how ArgoCD/Flux would reconcile cluster state from this same YAML in git instead | K8s docs pt.4-5 + ArgoCD docs "Core Concepts" (read-only, not installed) | — | Scale to 2 replicas, do a rolling update, observe zero dropped requests; commit the Deployment/Service YAML to a `k8s/` directory as if a GitOps controller were about to watch it | Continuous-request test during rollout | `feat: k8s rolling update verified + k8s manifests as git-tracked source` | Q2 | Coin Change II | DocuVault: tags frequently used together | 3.5h |
| Thu (D130) | Postgres replication | Postgres replication docs | Local read-replica setup | Route ES-sync consumer's reads to replica | Test replica lag doesn't break sync correctness | `feat: postgres read replica for sync consumer` | — | Target Sum | DocuVault: EXPLAIN ANALYZE a metadata query on replica vs primary | 3.5h |
| Fri (D131) | Sharding (conceptual); consistent hashing — the ring, virtual nodes, redistribution vs naive `hash(key) % N` | *Designing Data-Intensive Applications* (Kleppmann) Ch.6 | Build a consistent-hashing ring from scratch (virtual nodes included) against a synthetic key set; simulate adding/removing a shard and measure redistribution % vs naive modulo hashing | `docs/sharding-decision-record.md` — what key, why, when it'd be justified, backed by the redistribution benchmark | Test redistribution stays near the theoretical `1/N` bound, not near 100% | `feat: consistent-hashing ring + redistribution benchmark; docs: sharding decision record` | Q3 | Interleaving String | Calculate Special Bonus | 4h |
| Sat (D132) | **Review**; consensus failover drill — kill Tuesday's etcd leader, watch failover | — | Explain the outbox → CQRS → saga chain end-to-end, out loud; kill the etcd leader process, watch failover, record the term/log-index numbers before/after | `docs/postmortem-week22.md` | Full suite; verify the etcd cluster elects a new leader and stays writable after the kill | `docs: week 22 notes + etcd failover observed` | Answer Week-22 Qs unscripted | Review: redo Thursday's problem from memory — Target Sum | Review: rewrite Tuesday's query from memory, then extend it — Primary Department for Each Employee | 3h |

---

## 13. Daily Plan — Week 23: Raft — Leader Election & Log Replication

*No DSA/SQL problem today — the Raft implementation work is itself the
day's algorithmic depth. Two ordinary weeks' worth of grind is already in
the bank from Weeks 19-22; see `dsa-problems.md`/`sql-problems.md` for why
this week and next are the deliberate exception.*

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D133) | The Raft paper: replicated state machines, why consensus is hard, the shape of the solution | Ongaro & Ousterhout, "In Search of an Understandable Consensus Algorithm" §1-5 | Trace the paper's Figure 2 (the state summary) by hand, node by node, for a 3-node example | New repo `raft-impl/`, `Node` class with the Follower/Candidate/Leader states and the state transition table | Unit test each legal transition; test an illegal transition (e.g. Follower directly to Leader) is impossible by construction | `feat: raft node scaffold + state machine` | Q1 | 3.5h |
| Tue (D134) | Leader election: randomized timeouts, `RequestVote`, term comparison | Raft paper §5.1-5.2 | Deliberately use a FIXED (non-random) timeout across all nodes, watch a split-vote loop happen, then randomize and watch it resolve | `RequestVote` RPC handler, randomized election timeout, term increment on election start | Test: fixed timeout reproduces a split vote reliably; randomized timeout resolves an election within N attempts | `feat: leader election with randomized timeouts` | Q2 | 3.5h |
| Wed (D135) | `AppendEntries` as heartbeat; log replication begins | Raft paper §5.3 | Wire 3 processes over local HTTP, confirm heartbeats keep a leader stable with no elections firing | `AppendEntries` RPC (empty = heartbeat), leader sends periodic heartbeats, followers reset their election timer on receipt | Test: no election occurs for the duration of a stable heartbeat run | `feat: appendentries heartbeat` | — | 3.5h |
| Thu (D136) | Log replication for real: `nextIndex`/`matchIndex`, commit index advancement | Raft paper §5.3 (cont.) | On paper, trace `nextIndex` converging for a follower whose log is 3 entries behind | Client-submitted command → leader appends locally → replicates via `AppendEntries` → advances `commitIndex` once a majority acks | Integration test: submit a command, assert it's applied on a majority of nodes and `commitIndex` advances correctly | `feat: log replication + commit index advancement` | Q3 | 3.5h |
| Fri (D137) | Log inconsistency repair | Raft paper §5.3 (log matching property) | Manually construct two divergent follower logs, run the repair loop, confirm convergence | Handle the follower-rejects-AppendEntries case: leader decrements `nextIndex` and retries until logs match | Test: a follower with a conflicting entry gets it overwritten by the leader's version, never the reverse | `feat: log repair on inconsistency` | — | 3.5h |
| Sat (D138) | **Review** | — | Redo the `nextIndex` convergence trace from memory, explain it out loud | Bring up a real 5-node cluster, submit 10 commands from a client script, confirm all 5 nodes converge to the same log | Full suite; manual 5-node convergence check | `docs: week 23 notes — 5-node cluster convergence verified` | Answer Week-23 Qs unscripted | 2.5h |

---

## 14. Daily Plan — Week 24: Raft — Safety Properties Under Fault

*No DSA/SQL problem this week either — same reasoning as Week 23.*

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D139) | The five safety properties: Election Safety, Leader Append-Only, Log Matching, Leader Completeness, State Machine Safety | Raft paper §5.4-5.5 | For each property, write one concrete scenario where violating it corrupts the system — no abstractions, real node/term/entry numbers | `docs/raft-safety-properties.md` — each property in your own words, tied to a specific line of your own implementation that enforces it | — | `docs: raft safety properties, tied to implementation` | Q1 | 3.5h |
| Tue (D140) | Network partition simulation | — | Build a message-dropping proxy layer: any node pair can be "partitioned" by dropping messages between them on command | Partition a 5-node cluster into a 3-node majority and a 2-node minority; observe which side (if either) elects a leader | Test: majority side elects a leader and can commit; minority side never elects a leader, no matter how long it waits | `feat: partition simulation harness` | Q2 | 3.5h |
| Wed (D141) | Partition healing, stale leader step-down | Raft paper §5.1 (term comparison on RPC) | Reconnect a partitioned minority node to the majority, watch it discover the higher term and step down/update | Handle the healed-partition case: a stale leader (or stale follower with uncommitted entries) reconciles its log against the current leader's | Test: after healing, all 5 nodes converge to an identical log, including the minority nodes' now-overwritten uncommitted entries | `feat: partition-heal reconciliation` | — | 3.5h |
| Thu (D142) | Adversarial testing: kill the leader mid-replication, kill a follower mid-repair | — | — | Build the "torture test": randomly kill/restart nodes and drop messages for an extended run | Torture test asserts log consistency holds at every checkpoint, not just at the end; a deliberate "kill leader after majority ack, before followers confirm" case proves the entry survives | `test: raft torture test + adversarial leader-kill case` | Q3 | 4h |
| Fri (D143) | Applying Raft to a real use case | Revisit `system-design-problems.md` SD14 | — | Wire the Raft cluster as the coordination layer for a toy distributed job scheduler: only the current leader is allowed to dispatch a scheduled job | Test: kill the leader mid-dispatch-decision, confirm exactly one node (the new leader) takes over dispatching, never zero, never two | `feat: raft-backed leader-only job dispatcher` | — | 4h |
| Sat (D144) | **Phase 5 wrap review** | — | Explain all five safety properties out loud, unscripted, each with your own concrete violation scenario | `docs/postmortem-phase5.md` (full phase, Weeks 19-24), tag `v0.5-phase5` | Full suite, torture test re-run clean | `docs: phase 5 postmortem (weeks 19-24)` | Mock-answer all Phase-5 questions timed, including Weeks 23-24 | 3h |

---

## 15. Deliverables & GitHub Milestones

**Milestone: `Phase 5 — FleetTrack v0.1 + DocuVault v0.1`**
- [ ] Outbox pattern implemented and proven under fault injection
- [ ] CQRS read model powering the dispatcher dashboard
- [ ] Choreographed cancellation saga, with a documented failure path
- [ ] Elasticsearch search with typo tolerance and full reindex recovery
- [ ] DocuVault deployed to a local Kubernetes cluster (`kind`), rolling
      update verified with zero dropped requests
- [ ] Postgres read replica wired to the sync consumer
- [ ] Consistent-hashing ring built and benchmarked; `docs/sharding-decision-record.md` written with the redistribution numbers behind it
- [ ] 3-node local etcd cluster stood up, leader election and failover observed and documented in `docs/consensus-notes.md`
- [ ] WebSocket push stretch version of the FleetTrack dispatcher dashboard, before/after numbers recorded against the polling version
- [ ] Raft implemented from scratch: leader election, log replication, all
      five safety properties tested, a partition test proving the minority
      side can't elect a leader, a torture test proving log consistency
      under random faults, and a real Raft-backed leader-only job
      dispatcher built on top
- [ ] Tag: `v0.5-phase5`

## 16. Skills Acquired Checklist
- [ ] Outbox pattern — implemented and fault-tested, not just described
- [ ] CQRS — applied where justified, articulable where it's not
- [ ] Saga (choreographed) — implemented at overview depth, honestly scoped
- [ ] Elasticsearch: indexing, querying, keeping a derived index in sync
- [ ] Kubernetes fundamentals: Pods, Deployments, Services, ConfigMaps,
      Secrets, rolling updates — hands-on, not just terminology
- [ ] GitOps (ArgoCD/Flux) — conceptual fluency, correctly scoped as not-yet-needed
- [ ] Postgres read replicas — hands-on
- [ ] Sharding — conceptual fluency, correctly scoped as not-yet-needed
- [ ] Consistent hashing — implemented, benchmarked, applied to a real decision record
- [ ] Raft/consensus — conceptual fluency (etcd) AND a from-scratch
      implementation: leader election, log replication, safety properties,
      partition testing, a real application on top — not just terminology
- [ ] Two more React/TS frontends shipped: polling UI (FleetTrack, with a WebSocket-push stretch alternative built and compared), debounced search UI (DocuVault) — reusing Phase 4's setup

---

**Next:** Phase 6 is the senior-track capstone — idempotency, distributed
transaction thinking, security hardening, real cloud deployment, load
testing, mock system-design interviews, two more system-design problems
built for real (reusing this phase's Raft implementation), and finally
AtlasMarket, the marketplace capstone that consciously reuses everything
built across the last 24 weeks.
