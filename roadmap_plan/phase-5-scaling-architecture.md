# PHASE 5 — Scaling & Advanced Architecture
### Weeks 19–22 (4 weeks) · 24 working days

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

## 2. Technologies Introduced
Outbox pattern, CQRS, Saga (overview + one hands-on choreographed example),
Elasticsearch/OpenSearch, database replication (read replicas), sharding
(conceptual + one hands-on partitioning-by-key exercise), Kubernetes
(`kind`/`minikube`, Pods, Deployments, Services, ConfigMaps, Secrets).

Deliberately not yet: Event Sourcing as a full system (overview only, in
Week 20), full production Kubernetes (Helm, operators — named as "beyond
this bootcamp's scope" so you know the term without overclaiming depth).

---

## 5. PROJECT 7 — FleetTrack (Fleet & Delivery Logistics Platform)

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
back in WareFlow).

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
this is the whole point of the pattern, prove it under fault injection).

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

## 6. PROJECT 8 — DocuVault (Document Management with Search & Versioning)

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
autoscaling — named as next steps beyond this bootcamp).

**Replication/Sharding (conceptual + one hands-on piece):** set up a
Postgres read replica locally, route the search-indexing consumer's reads
to the replica, and write a decision record on what you'd shard by if
`document_versions` ever needed it (document_id is the natural shard key)
— sharding itself is not implemented, deliberately, since it's rarely
justified below very large scale and you should be able to say so in an
interview.

**Testing Strategy:** test that the Elasticsearch index recovers from a
missed event (a `reindex` endpoint you build specifically for this — since
ES is derived data, it must always be rebuildable from Postgres).

**Common Interview Questions**
1. Why is Elasticsearch never the source of truth here?
2. Walk through what a Kubernetes Deployment gives you over `docker run`.
3. What would you shard `document_versions` by, and why?
4. How do you keep a derived search index consistent with its source of
   truth over time?

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

## 7. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| Outbox pattern mini demo (standalone, before FleetTrack) | 19 | The pattern in isolation, no domain noise |
| Mini CQRS read-model projector (rebuild a view table from an event log) | 20 | CQRS mechanics |
| Elasticsearch indexing demo (index 1000 fake documents, query, tune analyzer) | 21 | ES fundamentals before applying to DocuVault |
| Mini load balancer (round-robin over 2 backend processes) | 22 | What Kubernetes Services/kube-proxy do underneath |

---

## 8. Books & Documentation
- Martin Fowler's blog: "What do you mean by Event-Driven?" and the Outbox
  pattern write-up (microservices.io/patterns/data/transactional-outbox.html).
- *Building Microservices* (Newman) Ch. 5 (data) for CQRS/Saga sections.
- Elasticsearch "Getting Started" official docs (Week 21).
- Kubernetes docs: "Learn Kubernetes Basics" interactive tutorial (Week 22).
- Postgres docs: replication chapter (Week 22).

---

## 9. Weekly Interview Question Sets

**Week 19 — Outbox**
1. What exact failure does the outbox pattern prevent that a direct
   publish-after-commit doesn't?
2. Why must the outbox insert share a transaction with the state change?

**Week 20 — CQRS, Saga**
1. When is CQRS overkill — give a concrete example from your own projects.
2. Choreographed vs orchestrated saga — tradeoffs?

**Week 21 — Elasticsearch**
1. Why does `LIKE '%term%'` fail at scale, mechanically?
2. Inverted index — explain it in one paragraph.

**Week 22 — Kubernetes, replication, sharding**
1. Pod vs Deployment vs Service — what does each actually do?
2. Read replica vs sharding — different problems, which is which?
3. What would you shard DocuVault's data by, and why that key?

---

## 10. Daily Plan — Week 19: Outbox Pattern, FleetTrack Scaffold

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D109) | Outbox pattern theory | Fowler/microservices.io outbox article | Standalone outbox demo (insert + relay script) | New repo `fleettrack/`, `Delivery`, `DeliveryEvent`, `outbox` models | Model tests | `feat: fleettrack scaffold + outbox table` | Q1 | Maximum Product Subarray | FleetTrack: unsent outbox rows older than 5 minutes | 3.5h |
| Tue (D110) | Transactional outbox insert | — | — | Status-update service: state change + outbox row, one transaction | Test both happen or neither happens | `feat: transactional status update + outbox insert` | Q2 | Word Break | Rising Temperature — self-join with LAG variant | 3.5h |
| Wed (D111) | Relay process design | — | — | Outbox relay worker (poll, publish, mark sent) | Test relay publishes and marks sent correctly | `feat: outbox relay worker` | — | Longest Increasing Subsequence | FleetTrack: delivery stuck longest in one status | 3.5h |
| Thu (D112) | Fault injection on the relay | — | — | Kill RabbitMQ mid-relay, confirm no event lost, retried next poll | Integration test with simulated broker outage | `test: outbox survives broker outage` | Q3 | Partition Equal Subset Sum | FleetTrack: avg time between status transitions | 3.5h |
| Fri (D113) | Outbox lag metric | — | — | Add outbox-lag metric to Prometheus/Grafana (from Phase 4 stack) | — | `feat: outbox lag metric` | — | Insert Interval | The Most Frequently Ordered Products for Each Customer | 3.5h |
| Sat (D114) | **Review** | — | Redo outbox demo from memory | — | Full suite | — | Answer Week-19 Qs unscripted | Review: redo Thursday's problem from memory — Partition Equal Subset Sum | Review: rewrite Tuesday's query from memory, then extend it — Rising Temperature — self-join with LAG variant | 2.5h |

---

## 11. Daily Plan — Week 20: CQRS Read Model, Saga

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D115) | CQRS theory | Fowler CQRS article | Mini CQRS projector (rebuild view from event log) | `delivery_view` read model table | — | `feat: delivery_view read model` | Q1 | Merge Intervals | FleetTrack: rebuild delivery_view from delivery_events by hand | 3.5h |
| Tue (D116) | Projector consuming outbox-relayed events | — | — | Consumer that updates `delivery_view` on each event | Test view reflects latest status within expected lag | `feat: delivery_view projector` | — | Non-overlapping Intervals | Article Views I | 3.5h |
| Wed (D117) | Dispatcher dashboard endpoint | — | — | `GET /dispatch/dashboard` reading only from `delivery_view` | Integration test dashboard query performance vs join-based alternative | `feat: dispatcher dashboard (cqrs read path)` | Q2 | Meeting Rooms | FleetTrack: drivers with the most cancelled deliveries | 3.5h |
| Thu (D118) | Saga theory: choreography vs orchestration | Newman Ch.5 saga section | — | Design the cancellation saga on paper first (`docs/cancellation-saga.md`) | — | `docs: cancellation saga design` | Q3 | Meeting Rooms II | Article Views II | 3.5h |
| Fri (D119) | Implementing the choreographed saga | — | — | 3-step cancellation saga: reverse assignment → notify → credit fee | Test each step fires on the prior step's event; test one failure path | `feat: delivery cancellation saga` | — | Maximum Subarray | FleetTrack: dispatcher dashboard — join vs read-model | 3.5h |
| Sat (D120) | **Review** | — | Redo CQRS projector from memory | Tag `v0.1-fleettrack` | Full suite | — | Answer Week-20 Qs unscripted | Review: redo Thursday's problem from memory — Meeting Rooms II | Review: rewrite Tuesday's query from memory, then extend it — Article Views I | 2.5h |

---

## 12. Daily Plan — Week 21: DocuVault Scaffold, Elasticsearch

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D121) | Inverted index concept | ES "Getting Started" | Index 1000 fake docs, run basic queries | New repo `docuvault/`, `Document`/`DocumentVersion` models | Model tests | `feat: docuvault scaffold` | Q1 | Jump Game | DocuVault: documents with the most versions | 3.5h |
| Tue (D122) | Analyzers, fuzziness, boosting | ES docs analyzers | Tune analyzer on the mini exercise corpus | `POST /documents` + MinIO upload (reusing Phase 4 presigned pattern) | Integration test upload flow | `feat: document upload` | — | Jump Game II | Fix Names in a Table | 3.5h |
| Wed (D123) | Keeping a derived index in sync | — | — | Outbox-relay-style consumer indexing new/updated docs into ES | Test index reflects new doc within expected lag | `feat: elasticsearch sync consumer` | Q2 | Gas Station | DocuVault: documents tagged with more than 3 tags | 3.5h |
| Thu (D124) | Search query design | — | — | `GET /documents/search?q=&tags=` | Test typo tolerance, tag filter, title-boost ranking | `feat: document search endpoint` | — | Hand of Straights | DocuVault: latest version per document | 3.5h |
| Fri (D125) | Reindex-from-source recovery | — | — | `POST /documents/reindex` — rebuilds ES fully from Postgres | Test ES wiped, reindex restores search correctly | `feat: full reindex recovery endpoint` | Q3 | Unique Paths | Recyclable and Low Fat Products | 3.5h |
| Sat (D126) | **Review** | — | Redo indexing mini exercise from memory | — | Full suite | — | Answer Week-21 Qs unscripted | Review: redo Thursday's problem from memory — Hand of Straights | Review: rewrite Tuesday's query from memory, then extend it — Fix Names in a Table | 2.5h |

---

## 13. Daily Plan — Week 22: Kubernetes Fundamentals, Replication, Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D127) | Pods, Deployments, Services | K8s "Learn Kubernetes Basics" pt.1-2 | Mini load balancer (round-robin, 2 processes) | `kind` cluster running locally, write Deployment+Service YAML for one DocuVault service | Verify pod reachable via Service | `feat: k8s deployment for docuvault service` | Q1 | Longest Common Subsequence | DocuVault: documents never tagged | 3.5h |
| Tue (D128) | ConfigMaps, Secrets | K8s docs pt.3 | — | Externalize config/secrets from that service into ConfigMap/Secret | Verify service picks up config correctly | `feat: k8s configmap + secret` | — | Best Time to Buy and Sell Stock with Cooldown | Primary Department for Each Employee | 3.5h |
| Wed (D129) | Scaling replicas, rolling updates | K8s docs pt.4-5 | — | Scale to 2 replicas, do a rolling update, observe zero dropped requests | Continuous-request test during rollout | `feat: k8s rolling update verified` | Q2 | Coin Change II | DocuVault: tags frequently used together | 3.5h |
| Thu (D130) | Postgres replication | Postgres replication docs | Local read-replica setup | Route ES-sync consumer's reads to replica | Test replica lag doesn't break sync correctness | `feat: postgres read replica for sync consumer` | — | Target Sum | DocuVault: EXPLAIN ANALYZE a metadata query on replica vs primary | 3.5h |
| Fri (D131) | Sharding (conceptual) | — | — | `docs/sharding-decision-record.md` — what key, why, when it'd be justified | — | `docs: sharding decision record` | Q3 | Interleaving String | Calculate Special Bonus | 3.5h |
| Sat (D132) | **Phase 5 wrap review** | — | Explain the outbox → CQRS → saga chain end-to-end, out loud | `docs/postmortem-phase5.md`, tag `v0.5-phase5` | Full suite | `docs: phase 5 postmortem` | Mock-answer all Phase-5 questions timed | Review: redo Thursday's problem from memory — Target Sum | Review: rewrite Tuesday's query from memory, then extend it — Primary Department for Each Employee | 2.5h |

---

## 14. Deliverables & GitHub Milestones

**Milestone: `Phase 5 — FleetTrack v0.1 + DocuVault v0.1`**
- [ ] Outbox pattern implemented and proven under fault injection
- [ ] CQRS read model powering the dispatcher dashboard
- [ ] Choreographed cancellation saga, with a documented failure path
- [ ] Elasticsearch search with typo tolerance and full reindex recovery
- [ ] DocuVault deployed to a local Kubernetes cluster (`kind`), rolling
      update verified with zero dropped requests
- [ ] Postgres read replica wired to the sync consumer
- [ ] `docs/sharding-decision-record.md` written
- [ ] Tag: `v0.5-phase5`

## 15. Skills Acquired Checklist
- [ ] Outbox pattern — implemented and fault-tested, not just described
- [ ] CQRS — applied where justified, articulable where it's not
- [ ] Saga (choreographed) — implemented at overview depth, honestly scoped
- [ ] Elasticsearch: indexing, querying, keeping a derived index in sync
- [ ] Kubernetes fundamentals: Pods, Deployments, Services, ConfigMaps,
      Secrets, rolling updates — hands-on, not just terminology
- [ ] Postgres read replicas — hands-on
- [ ] Sharding — conceptual fluency, correctly scoped as not-yet-needed

---

**Next:** Phase 6 is the senior-track capstone — idempotency, distributed
transaction thinking, security hardening, load testing, mock system-design
interviews, and finally AtlasMarket, the marketplace capstone that
consciously reuses everything built across the last 22 weeks.
