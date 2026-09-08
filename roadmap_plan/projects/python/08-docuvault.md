# Project 8 — DocuVault

**Document management with full-text search & versioning**

| | |
|---|---|
| Domain | Enterprise / Search |
| Level | Middle |
| Phase | 5 — Scaling & Advanced Architecture |
| Weeks | 21–22 (D121–D132) |
| Stack | Python, FastAPI, PostgreSQL (+ **read replica**), MinIO/S3, **Elasticsearch/OpenSearch**, **Kubernetes (`kind`)**, **etcd**, React + TS + TanStack Query |
| Repo | `docuvault/` + `docuvault-web/` |

> **Two lessons.** First: a derived index is never the source of truth, and you
> prove it by rebuilding it from scratch. Second: Kubernetes, introduced only
> because Compose has genuinely stopped coping — with the service list written
> down as the evidence.

---

## 1. Business Problem

A mid-size company has thousands of internal documents — policies, contracts,
reports — scattered across drives with no real search. "Find the Q3 vendor
contract" means asking around, not searching.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Documents uploaded and versioned — every edit creates a version, old ones retained
2. Full-text search with typo tolerance and title boosting, plus tag filtering
3. Elasticsearch kept current by an event consumer, reusing FleetTrack's relay pattern
4. A `reindex` endpoint that rebuilds the entire index from Postgres
5. A Postgres read replica serving the indexing consumer
6. A `kind` cluster running one service as a Deployment with 2 replicas
7. `docuvault-web/`: a debounced search page

**Proof it is correct**
8. A recovery test: drop an event, confirm search is stale, run `reindex`, confirm
   it is correct again
9. A rolling update on Kubernetes with **zero dropped requests**, observed
10. A consistent-hashing ring benchmarked against naive modulo, with a **measured
    redistribution percentage**

**Written artefacts**
11. **The Compose service list** at the moment it stopped being manageable — the
    honest justification for doing Kubernetes work at all
12. `docs/consensus-notes.md` — Raft in your own words, tied to K8s, RabbitMQ, Kafka
13. `docs/sharding-decision-record.md` — the key, the reasoning, and **why you did
    not implement it**
14. Search relevance before and after tuning, on the same queries

---

## 3. Scope

**In scope**
- Upload and versioning
- Full-text search across content and metadata, with tag filtering
- Event-driven ES sync + full reindex
- Kubernetes fundamentals on `kind`
- A Postgres read replica
- A hand-built consistent-hashing ring, benchmarked
- A debounced search frontend

**Out of scope — deliberately**

| Deferred | Why |
|---|---|
| **Sharding itself** | Rarely justified below very large scale. You write the decision record instead, and being able to say *why not* is the point |
| Access-control-aware search — hiding documents the requester cannot read | A real production concern, deferred as noted complexity. Name it; it is a good interview follow-up |
| Semantic / vector search | → Phase 7, on this same corpus |
| Helm, operators, autoscaling, GitOps controllers | Named as next steps beyond this bootcamp. You commit GitOps-shaped YAML without running a controller |
| OCR / content extraction | Index the text you have |

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`reader`** | Search, view document metadata and versions, download a version | Upload; create a version; delete |
| **`contributor`** | Everything a reader can, plus upload new documents and add versions to documents they own | Delete; edit tags on others' documents |
| **`librarian`** | Manage tags and taxonomy, edit metadata on any document, trigger a reindex | Delete a version — history is immutable |
| **`platform_admin`** | Trigger a full reindex, manage the cluster and the index | — |

**Honest caveat, and it belongs in the docs:** search results are **not**
access-filtered in v1. Every role sees every document in search. That is a real
gap, deliberately deferred, and you should be able to describe how you would close
it (index the ACL alongside the document and filter at query time) and why it is
harder than it sounds (permission changes require reindexing, and a stale ACL in a
derived index is a data leak).

---

## 5. Functional Modules

### 5.1 Documents & versioning
A document has a title, an owner, tags, and an ordered list of versions. Each
version points at an object in storage. `current_version_id` is a pointer, not a
copy. Nothing is ever overwritten.

### 5.2 Indexing
An event consumer projects document and version changes into Elasticsearch.
Plus a full rebuild endpoint.

### 5.3 Search
Query across title, body and tags with fuzziness and field boosting.

### 5.4 Platform work
The `kind` cluster, the read replica, the consistent-hashing benchmark.

---

## 6. Architecture

```
       ┌── Postgres ──────────  SOURCE OF TRUTH (metadata + version history)
       │        │
Client ┤        └── replica ──  read-only, serves the indexing consumer
       │
       ├── MinIO/S3 ─────────  document bytes (Phase 4 presigned pattern, reused)
       │
       └── Elasticsearch ────  DERIVED INDEX, never authoritative
                    ▲
                    └── outbox-relay-style consumer (FleetTrack pattern, reused)
```

**State this explicitly, in the code and in the docs:** Postgres is the source of
truth; Elasticsearch is a derived index that must always be rebuildable from it.
"Which store is the source of truth?" is a standard system-design interview trap,
and the honest answer requires that `reindex` actually works.

---

## 7. Domain Model

```
documents(id, title, current_version_id, created_by)

document_versions(id, document_id, s3_key, version_number, created_at)
    UNIQUE(document_id, version_number)

tags(id, name)

document_tags(document_id, tag_id)
```

---

## 8. API Design

| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/documents` | contributor+ | First upload |
| POST | `/documents/{id}/versions` | contributor+ | New version; old ones retained |
| GET | `/documents/{id}` | reader+ | Metadata + current version |
| GET | `/documents/{id}/versions` | reader+ | Full history |
| GET | `/documents/{id}/versions/{n}/download` | reader+ | Presigned GET |
| GET | `/documents/search?q=&tags=` | reader+ | Hits Elasticsearch |
| POST | `/documents/reindex` | platform_admin | **Rebuilds ES fully from Postgres** |

---

## 9. Search Implementation

- Analyzer configuration for reasonable **typo tolerance** (fuzziness)
- **Boost title matches over body matches**
- Tag filters as a structured filter clause, not part of the text query
- Tune against a small real test corpus and **record what changed** — the same
  queries, relevance before and after

Non-functional requirement: search must handle typos and partial matches
reasonably and stay fast as the corpus grows past what `LIKE '%term%'` can handle.
Be able to say *why* `LIKE '%term%'` cannot use an index, and what Postgres
full-text search would have given you instead — Elasticsearch is a choice, and a
choice needs an alternative.

---

## 10. Kubernetes (hands-on, `kind`)

**First, the justification.** Compose is now running: `nginx`, `auth-service`,
`clinic-service`, `invoicing-service`, `ledger-service`, `fleettrack`, a relay
worker, `docuvault`, a Celery worker, Beat, `postgres`, a replica, `redis`,
`rabbitmq`, `minio`, `elasticsearch`, `prometheus`, `grafana`. **Write that list
down.** It is the evidence, and it is what separates "I learned Kubernetes" from
"I learned Kubernetes because I needed it."

Scoped as **fundamentals, not production operations**:

| Object | What you do with it |
|---|---|
| Deployment | One DocuVault service, 2 replicas |
| Service | Stable endpoint in front of the pods |
| ConfigMap | Externalized configuration |
| Secret | Externalized secrets |
| Rolling update | Performed, with **zero dropped requests** observed |
| Probes | Readiness and liveness — and the difference between them, in your own words |

Commit the Deployment/Service YAML to a `k8s/` directory **as if a GitOps
controller were about to watch it** — declarative, no imperative `kubectl edit`
state, nothing that only exists in your shell history.

**Consensus:** Kubernetes' control plane agrees on cluster state via Raft-based
consensus — the same primitive underneath RabbitMQ clustering and Kafka's
controller election. You use it on Monday without explanation, then open the box
on Tuesday with a real **3-node local etcd cluster** (etcd runs Raft, and is what
`kind`'s own control plane uses one instance of).

Deliverable: `docs/consensus-notes.md` — Raft in your own words, tied to all three.

---

## 11. Replication & Sharding

**Replication (hands-on):** a Postgres read replica, with the search-indexing
consumer's reads routed to it. Writes still go to the primary. Notice and write
down the replication lag you can actually observe, and what it means for a
consumer reading its own recent write.

**Sharding (decision record, not implemented):**
`docs/sharding-decision-record.md` — what key (`document_id` is the natural one),
why, and at what scale it would be justified.

**Consistent hashing (hands-on, backing the decision record):** build a real
consistent-hashing ring **with virtual nodes** and benchmark it against naive
`hash(key) % N` on a synthetic key set. Measure what fraction of keys move when a
node is added and when one is removed.

The decision record then carries a **measured number** instead of an assertion —
"adding a node moves ~1/N of keys with consistent hashing versus ~all of them with
modulo" is a much better answer when you have the benchmark behind it.

---

## 12. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL (primary)** | Documents, versions, tags — **the source of truth** | |
| **PostgreSQL (read replica)** | Reads for the ES indexing consumer only | Indexing is a bulk read workload that should not compete with user traffic. It also makes replication lag a thing you can see |
| **MinIO / S3** | Document bytes, via the presigned pattern reused from CarePoint | Bytes never pass through the API |
| **Elasticsearch / OpenSearch** | Full-text search over title, body and tags | The felt problem: `LIKE '%term%'` cannot use an index and cannot do fuzziness. **Derived, never authoritative** |
| **RabbitMQ** | Carries document-change events to the indexing consumer | The relay pattern from FleetTrack, reused |
| **Kubernetes (`kind`)** | One service deployed as a Deployment + Service, config in ConfigMap/Secret, 2 replicas, rolling update | Justified by the written Compose service list, not by fashion |
| **etcd (3-node, local)** | A hands-on look at Raft-backed consensus | Because you used it implicitly on Monday and should not leave it a black box |
| **Prometheus + Grafana** | Index lag (events behind), search latency, replica lag, pod restarts | Index lag is this project's outbox lag: if the consumer stalls, search silently goes stale while everything looks healthy |
| **`docuvault-web/`** | Debounced search box + tag chips via TanStack Query | Second frontend; reuses CarePoint's setup |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Redis cache on search results** | Result sets are query-specific and the corpus changes; the hit rate would be poor and the invalidation story bad. Elasticsearch already has its own caching |
| **Kafka** | Same reasoning as FleetTrack. Nothing here needs a replayable log |
| **Helm / operators / autoscaling** | Fundamentals only. Naming them as next steps is the honest scope |
| **A real GitOps controller (Argo/Flux)** | Conceptual this phase. You commit the YAML in the right shape without adding a controller to operate |
| **Access-control filtering in the index** | Deferred, and documented as a known gap |

---

## 13. Build Plan (consolidated)

### Stage 1 — Documents, versioning, search *(D121–D126, Week 21)*
- New repo `docuvault/`: `Document` / `DocumentVersion` models
- `POST /documents` + MinIO upload (reusing the Phase 4 presigned pattern)
- Outbox-relay-style consumer indexing new/updated docs into Elasticsearch
- `GET /documents/search?q=&tags=`, with analyzer and boosting tuned against a
  real test corpus
- `docuvault-web/` search page: debounced box + tag chips
- `POST /documents/reindex` — full rebuild from Postgres

### Stage 2 — Kubernetes, replication, sharding *(D127–D132, Week 22)*
- **Write down the Compose service list** — the justification
- `kind` cluster; Deployment + Service YAML for one DocuVault service
- Externalize config/secrets into ConfigMap / Secret
- 3-node etcd cluster; `docs/consensus-notes.md`
- Scale to 2 replicas, rolling update, observe **zero dropped requests**; commit
  YAML to `k8s/`
- Postgres read replica; route the ES-sync consumer's reads to it
- Build and benchmark the consistent-hashing ring
- `docs/sharding-decision-record.md`, backed by the benchmark
- `docs/postmortem-week22.md`

---

## 14. Testing Strategy

| Layer | What |
|---|---|
| **Recovery (the important one)** | Drop an event so the index goes stale → confirm search is wrong → run `reindex` → confirm it is right again. **ES must always be rebuildable from Postgres** |
| Search | Relevance on the test corpus: typo tolerance, title boosting, tag filtering |
| Versioning | A new version never destroys an old one; `current_version_id` always correct; version numbers are contiguous |
| Concurrency | Two versions added simultaneously do not collide on `version_number` |
| Replica | The indexing consumer reads from the replica; writes still reach the primary |
| Replica | Behaviour under visible replication lag is understood and documented |
| K8s | A rolling update drops zero requests |
| K8s | A failing readiness probe keeps a pod out of the Service |
| Benchmark | Consistent hashing vs naive modulo — measured redistribution on node add and remove |

---

## 15. Definition of Done

- [ ] Upload → version → search → history all working
- [ ] ES kept in sync by the event consumer **and** fully rebuildable via `/reindex`
- [ ] The recovery test passes
- [ ] Source-of-truth boundary stated in writing
- [ ] Search tuned against a real corpus, before/after relevance recorded
- [ ] The Compose service list written down as the Kubernetes justification
- [ ] `kind`: Deployment + Service + ConfigMap + Secret, 2 replicas, rolling update
      with zero dropped requests
- [ ] `k8s/` YAML committed GitOps-style
- [ ] 3-node etcd cluster explored; `docs/consensus-notes.md` written
- [ ] Read replica serving the indexing consumer
- [ ] Consistent-hashing ring built and benchmarked
- [ ] `docs/sharding-decision-record.md` with a **measured number** in it
- [ ] The access-control-in-search gap documented honestly
- [ ] `docuvault-web/` search page live
- [ ] `docs/postmortem-week22.md`

---

## 16. Interview Questions This Project Should Let You Answer

1. Why is Elasticsearch never the source of truth here, and how do you prove your
   index is rebuildable?
2. Why not Postgres full-text search — what did Elasticsearch actually buy you?
3. Walk me through what a Kubernetes Deployment gives you over `docker run`.
4. Readiness vs liveness probe — what breaks if you conflate them?
5. What would you shard `document_versions` by, and why — and what does your
   consistent-hashing benchmark add over a hand-wave?
6. How do you keep a derived search index consistent with its source of truth over
   time, and how do you detect when it drifts?
7. What does Kubernetes' own control plane use consensus for, and what would you
   expect if you killed its etcd leader?
8. Your search is not access-filtered. How would you fix that, and why is it harder
   than adding a `WHERE` clause?
9. You routed the indexing consumer to a read replica. What can go wrong?

---

## 17. Common Mistakes to Watch For

- Treating Elasticsearch as authoritative and losing data when it is wiped
- A `reindex` endpoint that exists but has never been run against a real drift
- Deploying to Kubernetes without ever having run the services with plain Compose
  first — you did not make this mistake; **note why that ordering mattered**
- Sharding prematurely
- Tuning search relevance by feel instead of against a fixed query set
- Monitoring the API but not the index lag, so search goes quietly stale

---

## 18. How Real Companies Differ

Most production search systems split the indexing pipeline into its own,
independently scaled service much sooner than DocuVault does — indexing load and
query load have completely different shapes. Sufficient here because the corpus is
learning-scale, but worth naming.

---

## 19. Related — Weeks 23–24

The rest of Phase 5 is **not** DocuVault. Weeks 23–24 are a from-scratch **Raft
implementation** (`raft-impl/`) — leader election, log replication, all five safety
properties, tested under a real simulated network partition. Project 28's
distributed job scheduler is later built on it. See
`phase-5-scaling-architecture.md` §5.
