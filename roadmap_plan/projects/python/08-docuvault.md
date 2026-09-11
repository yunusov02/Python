# Project 8 — DocuVault

**Document management with full-text search & versioning**

| | |
|---|---|
| Domain | Enterprise / Search |
| Level | Middle |
| Phase | 5 — Scaling & Advanced Architecture |
| Weeks | 21–22 (D121–D132) |
| Stack | Python, FastAPI, PostgreSQL (**FTS `tsvector`/`pg_trgm`**, + **read replica**, **PgBouncer**, `pg_stat_statements`), MinIO/S3, **Elasticsearch/OpenSearch**, **Kubernetes (`kind`)** + Ingress, **etcd**, React + TS + TanStack Query |
| Repo | `docuvault/` + `docuvault-web/` |

> **Three lessons.** First: a derived index is never the source of truth, and you
> prove it by rebuilding it from scratch — and you reach for Elasticsearch only
> after **Postgres full-text search** has been tried and found wanting on a
> specific query. Second: Kubernetes, introduced only because Compose has
> genuinely stopped coping — with the service list written down as the evidence.
> Third: this is where Postgres gets **operated**, not just queried — statistics,
> autovacuum, `pg_stat_statements`, connection pooling.

---

## 1. Business Problem

A mid-size company has thousands of internal documents — policies, contracts,
reports — scattered across drives with no real search. "Find the Q3 vendor
contract" means asking around, not searching.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Documents uploaded and versioned — every edit creates a version, old ones retained
2. Full-text search with typo tolerance and title boosting, plus tag filtering —
   after a **Postgres FTS** (`tsvector` + GIN, `pg_trgm`) version that you kept
   until it could not do what a specific query needed
3. Elasticsearch kept current by an event consumer, reusing FleetTrack's relay pattern
4. A `reindex` endpoint that rebuilds the entire index from Postgres — **`202
   Accepted`** + a job resource, using **bulk** reads (server-side cursor) and
   ES `_bulk` writes in tuned batches
5. A Postgres read replica serving the indexing consumer
6. A `kind` cluster running one service as a Deployment with 2 replicas, **resource
   requests/limits**, an **Ingress**, a **preStop hook**, and an HPA you scaled once
6a. **PgBouncer** in front of Postgres, with the prepared-statement gotcha met and solved
6b. A **stale-statistics demonstration**: a plan that goes bad because `ANALYZE`
   never ran, then `pg_stat_statements` finding the slow query
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
15. `docs/postgres-ops-notes.md` — autovacuum, bloat, statistics, `pg_stat_statements`,
    pooling: what you observed and what you set
16. `docs/search-decision-record.md` — `LIKE` → Postgres FTS → Elasticsearch, with
    the query that forced each step

---

## 3. Scope

**In scope**
- Upload and versioning
- Full-text search across content and metadata, with tag filtering
- Postgres FTS first, Elasticsearch second, with a decision record
- Event-driven ES sync + full reindex (bulk, `202` + job status)
- Kubernetes fundamentals on `kind`, plus requests/limits, Ingress, preStop, HPA
- A Postgres read replica, with a read-your-own-write mitigation
- Postgres operations: autovacuum/bloat, statistics, `pg_stat_statements`, PgBouncer
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
documents(id, title, current_version_id, created_by,
          search_tsv tsvector GENERATED ALWAYS AS
            (setweight(to_tsvector('simple', title), 'A') ||
             setweight(to_tsvector('simple', coalesce(body_excerpt,'')), 'B')) STORED)
    -- GIN (search_tsv)            : Postgres FTS, stage 1 of the search story
    -- GIN (title gin_trgm_ops)    : pg_trgm, so LIKE '%term%' / similarity() can use an index

document_versions(id, document_id, s3_key, version_number, created_at)
    UNIQUE(document_id, version_number)
    -- version_number assigned under SELECT ... FOR UPDATE on the parent
    -- documents row, so two concurrent uploads never collide (the UNIQUE
    -- constraint is the backstop, the lock is the mechanism)

tags(id, name)

document_tags(document_id, tag_id)

reindex_jobs(id, status, total, done, started_at, finished_at NULL, error NULL)
    -- the pollable resource behind 202 Accepted
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
| GET | `/documents/search?q=&tags=` | reader+ | Hits Elasticsearch (stage 3). `?engine=pg` keeps the Postgres FTS path alive for comparison |
| POST | `/documents/reindex` | platform_admin | **Rebuilds ES fully from Postgres**. `202 Accepted` + `Location: /reindex-jobs/{id}` |
| GET | `/reindex-jobs/{id}` | platform_admin | Progress: `done/total`, status |

---

## 9. Search Implementation — three stages, one decision record

Elasticsearch is a choice, and a choice needs an alternative you actually tried.
Most companies never get past stage 2. Build all three against the same test
corpus and the same fixed query set.

| Stage | Mechanism | What it gives | Where it breaks (the query that forces the next stage) |
|---|---|---|---|
| 1 — `LIKE '%term%'` | Sequential scan | Nothing but simplicity | Cannot use a B-tree (leading wildcard). Show the seq scan at 100k docs |
| 1b — **`pg_trgm`** | `GIN (title gin_trgm_ops)`; `LIKE '%term%'`, `ILIKE`, `similarity()` | Indexed substring and fuzzy-ish matching **without leaving Postgres** | Relevance is just similarity; no stemming, no field weighting |
| 2 — **Postgres FTS** | `tsvector` generated column + GIN, `to_tsquery`/`websearch_to_tsquery`, `ts_rank`, `setweight` (title A, body B), `ts_headline` | Stemming, stop words, ranking, weights, phrase search, highlighting — indexed, transactional, in the source of truth | **No typo tolerance** (`documnet` finds nothing), weak relevance tuning, one dictionary per column (Uzbek/Russian mixed text hurts), limited faceting |
| 3 — **Elasticsearch** | Analyzer + fuzziness, title boost, tag filter clause | Typo tolerance, tunable relevance, aggregations | A second store that is **never authoritative** and must be rebuildable |

For each stage record on the fixed query set: p95 latency at 100k docs, and
relevance (did the expected document land in the top 3?). The moment stage 2
fails a query you care about — typos in a title search is the usual one — is the
moment Elasticsearch is justified. `docs/search-decision-record.md` carries the
table and the query.

Elasticsearch side:
- Analyzer configuration for reasonable **typo tolerance** (fuzziness)
- **Boost title matches over body matches**
- Tag filters as a structured filter clause, not part of the text query
- Tune against the corpus and **record what changed** — same queries, before and after

Non-functional requirement: search must handle typos and partial matches
reasonably and stay fast as the corpus grows. Be able to say *why* `LIKE
'%term%'` cannot use a B-tree, what `pg_trgm` and `tsvector` each give you, and
what only Elasticsearch gave you here.

### 9a. Reindex as a bulk, long-running operation

`POST /documents/reindex` returns **`202 Accepted`** and a `reindex_jobs` row.
The worker streams Postgres with a server-side cursor (`yield_per(1000)`, from
the replica), builds ES `_bulk` requests of N docs, and updates `done` every
batch. Tune N (500? 5000?) by measuring throughput and ES rejection rate; too
large a batch and ES pushes back — that push-back is **backpressure**, and you
must slow down rather than retry harder. Record the batch size you chose and why.
The same pattern (cursor → batch → progress) is how any bulk job should look;
`COPY` is the even faster path for Postgres→Postgres, named here and used once
to load the test corpus.

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
| **Ingress** | Nginx Ingress Controller routing a hostname to the Service — the Kubernetes form of the `nginx.conf` you wrote in CarePoint |
| ConfigMap | Externalized configuration |
| Secret | Externalized secrets |
| **`resources.requests` / `limits`** | Set for CPU and memory. Then set memory `limits` too low on purpose, watch the pod get **OOMKilled** and restart, read it in `kubectl describe`. Without requests the scheduler is guessing; without limits one pod can starve the node |
| Probes | Readiness and liveness — and the difference between them, in your own words. A failing readiness probe removes the pod from the Service; a failing liveness probe restarts it |
| **`preStop` hook + `terminationGracePeriodSeconds`** | Zero dropped requests during a rolling update **does not happen by default**: the pod is removed from the Service and sent `SIGTERM` at roughly the same time, and kube-proxy/Ingress may still route to it for a moment. A `preStop` sleep of a few seconds plus the application's graceful shutdown (LedgerBase) closes the gap. Do the rolling update without it first and count the errors |
| **HPA** | One CPU-based HorizontalPodAutoscaler; drive load with `hey`, watch replicas go 2 → 4 → 2. Fundamentals only |
| `kubectl rollout undo` | Roll back a bad image once, on purpose |
| Rolling update | Performed, with **zero dropped requests** observed — *after* the preStop/graceful-shutdown work |

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

**Read-your-own-write — build one mitigation.** The indexing consumer receives
`DocumentVersionAdded` and reads the version from the replica — which may not
have it yet. Options: (a) wait until the replica's replay LSN ≥ the LSN the
event was committed at (`pg_current_wal_lsn()` captured in the event,
`pg_last_wal_replay_lsn()` on the replica); (b) retry with backoff on "not
found"; (c) read that one row from the primary. Implement (a) or (b), name all
three, and write down the trade-off.

### 11a. Postgres operations — `docs/postgres-ops-notes.md`

This is the project where the database gets busy enough to misbehave. Meet each
problem once, deliberately:

| Topic | Do this | What you will see |
|---|---|---|
| **Statistics** | Load 200k `document_versions` with autovacuum **off**; `EXPLAIN` a filtered query; compare estimated vs actual rows; run `ANALYZE`; `EXPLAIN` again | A plan chosen on a 1-row estimate against a 200k-row reality. `pg_stats`, `default_statistics_target` |
| **Autovacuum / bloat** | Update every row twice with autovacuum off; check `pg_stat_user_tables.n_dead_tup` and table size (`pg_total_relation_size`); `VACUUM`; compare. Then turn autovacuum on and tune `autovacuum_vacuum_scale_factor` for the busy table | Dead tuples, bloat that `VACUUM` does not shrink (only `VACUUM FULL` / `pg_repack` does), and why MVCC makes this unavoidable |
| **`pg_stat_statements`** | Enable it; run the load test; query the top 10 by `total_exec_time` and by `mean_exec_time` | The actual slowest query is rarely the one you guessed. Feed the top one into `EXPLAIN (ANALYZE, BUFFERS)` |
| **Slow query log** | `log_min_duration_statement = 200ms` | Every slow query, with its bind values, in the log |
| **PgBouncer** | Put PgBouncer in **transaction pooling** mode between the K8s replicas + the indexing consumer and Postgres. Size the pool (`max_connections` on Postgres is not free — each backend is a process). Then hit the **prepared-statement gotcha**: asyncpg's implicit prepared statements break in transaction mode; fix with `statement_cache_size=0` or PgBouncer ≥1.21 `max_prepared_statements` | Why "just raise `max_connections`" is wrong; the difference between session, transaction and statement pooling |
| `pg_stat_activity` | Watch connections while the load test runs; find `idle in transaction` | The connection that is holding a lock and doing nothing |

None of this is a DBA course. It is the minimum a backend engineer needs to
stop blaming "the database" and start reading it.

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
| **Kubernetes (`kind`)** | One service deployed as a Deployment + Service + **Ingress**, config in ConfigMap/Secret, 2 replicas, **requests/limits**, **preStop**, an HPA, rolling update and `rollout undo` | Justified by the written Compose service list, not by fashion |
| **PgBouncer** | Transaction-mode pool between all Postgres clients and the primary | Replicas × pool size exceeds what Postgres backends should be asked to hold. Also the first place the asyncpg prepared-statement gotcha bites |
| **`pg_stat_statements`, slow query log, `pg_stat_user_tables`** | Enabled on the primary | Finding the slow query instead of guessing it |
| **Postgres FTS + `pg_trgm`** | Stages 1b–2 of the search story; kept behind `?engine=pg` | The alternative Elasticsearch has to beat |
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
- Load the test corpus with `COPY`
- **Search stage 1–2**: `LIKE` seq scan → `pg_trgm` GIN → `tsvector` + GIN +
  `ts_rank`; measure on the fixed query set; find the query FTS cannot serve
- Outbox-relay-style consumer indexing new/updated docs into Elasticsearch
- **Search stage 3**: `GET /documents/search?q=&tags=`, analyzer and boosting
  tuned against the corpus; `docs/search-decision-record.md`
- `version_number` under `FOR UPDATE` on the parent row; concurrency test
- `docuvault-web/` search page: debounced box + tag chips
- `POST /documents/reindex` — `202` + job; cursor → `_bulk` batches; batch size tuned

### Stage 2 — Kubernetes, replication, Postgres ops, sharding *(D127–D132, Week 22)* *(v2: +3 days)*
- **Write down the Compose service list** — the justification
- `kind` cluster; Deployment + Service YAML for one DocuVault service
- Externalize config/secrets into ConfigMap / Secret
- 3-node etcd cluster; `docs/consensus-notes.md`
- `resources` requests/limits; the deliberate OOMKill; Ingress
- Scale to 2 replicas; rolling update **without** preStop — count the errors;
  add `preStop` + graceful shutdown; repeat, observe **zero dropped requests**;
  `rollout undo` once; HPA 2→4→2 under `hey`; commit YAML to `k8s/`
- Postgres read replica; route the ES-sync consumer's reads to it; **read-your-own-write** mitigation
- **PgBouncer** in transaction mode; the prepared-statement gotcha, solved
- Stale-statistics demo, autovacuum/bloat demo, `pg_stat_statements` top-10,
  slow-query log → `docs/postgres-ops-notes.md`
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
| **Search stages** | Fixed query set: latency and top-3 relevance recorded for `LIKE`, `pg_trgm`, FTS, ES; the typo query fails on FTS and passes on ES |
| Bulk reindex | `202` returned in <100ms; job progresses; memory flat during a 100k-doc rebuild; an ES `429` slows the batch loop rather than crashing it |
| Version lock | 20 concurrent uploads to one document → `version_number` 1..20 with no gaps or collisions |
| Read-your-own-write | Consumer never indexes a "not found" — the LSN wait (or retry) is exercised under induced replica lag |
| K8s resources | A pod with a too-low memory limit is OOMKilled and restarted, visible in `describe` |
| **preStop** | Rolling update without preStop: N errors recorded; with preStop + graceful shutdown: 0 |
| HPA | Replicas scale up under load and back down after |
| Statistics | Plan estimate vs actual differs by >100× before `ANALYZE`, matches after |
| Bloat | `n_dead_tup` and relation size before/after `VACUUM` recorded |
| **PgBouncer** | The app works in transaction mode with the statement-cache fix; `SHOW POOLS` observed under load |

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
- [ ] `LIKE` → `pg_trgm` → FTS → ES built on one corpus; `docs/search-decision-record.md`
- [ ] Reindex is `202` + job, cursor + `_bulk`, batch size tuned, backpressure handled
- [ ] `version_number` safe under concurrency via parent-row lock
- [ ] Ingress, requests/limits (OOMKill seen), preStop + graceful shutdown, HPA, `rollout undo`
- [ ] Read-your-own-write mitigation on the replica
- [ ] PgBouncer transaction pooling; prepared-statement gotcha solved
- [ ] Stale-stats, bloat/vacuum, `pg_stat_statements` demonstrated; `docs/postgres-ops-notes.md`
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
10. Why can `LIKE '%term%'` not use a B-tree, and how does `pg_trgm` change that?
11. What did Postgres full-text search give you, and what was the exact query that
    made you add Elasticsearch?
12. How does a rolling update drop zero requests? What does `preStop` do that
    the readiness probe does not?
13. What happens to a pod without a memory limit? With one that is too low?
14. Your consumer reads its own write from a replica and gets "not found". Three fixes?
15. Why PgBouncer, why transaction mode, and what broke with asyncpg?
16. A query's plan went bad overnight and no code changed. Where do you look first?
17. What is table bloat, why does `VACUUM` not shrink the file, and what does?
18. How do you find the slowest query in production without guessing?
19. Why does `reindex` return `202`? How do you handle Elasticsearch pushing back with `429`?

---

## 17. Common Mistakes to Watch For

- Treating Elasticsearch as authoritative and losing data when it is wiped
- A `reindex` endpoint that exists but has never been run against a real drift
- Deploying to Kubernetes without ever having run the services with plain Compose
  first — you did not make this mistake; **note why that ordering mattered**
- Sharding prematurely
- Tuning search relevance by feel instead of against a fixed query set
- Monitoring the API but not the index lag, so search goes quietly stale
- Jumping to Elasticsearch without ever trying `tsvector` — and being unable to say what it added
- A rolling update that "worked" because nobody was sending requests during it
- Pods with no resource requests, so the scheduler packs them until the node falls over
- Raising `max_connections` to 500 instead of pooling
- Autovacuum disabled "for performance", and a table three times its live size a month later
- A reindex that loads every document into a Python list first

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
