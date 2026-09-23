# System design map

| | |
|---|---|
| **Covers** | Every system-design concept Atlas practises in code, the 19-problem bank plus the SD20 closing exercise (`../../system-design-problems.md`), the extra "LLM gateway for 50 teams" problem, the 45-minute answer framework, and the three mock interviews |
| **When** | One SD session closes every stage; the weekly drill hour carries the week's SD or interview questions; mocks in [B1](buffers-and-job-sprint.md) (W18), [B2](buffers-and-job-sprint.md) (W37) and [S12](stage-12-data-at-scale-fraud.md) (W53) |
| **Where answers go** | `docs/sd/` (one file per problem or mock), `docs/sd20-retro.md`, `docs/star/` for the behavioural stories |
| **Old-spec theory** | The bank itself (`../../system-design-problems.md`), its 6-step skeleton, and the old mock-interview days in `../../phase-6-capstone.md` D166–D168 |

> **What this map is really for.** Most candidates answer system design from books. You will answer from a system you built, with the numbers you measured and the failures you caused on purpose. This file tells you which Atlas stage gives you evidence for which concept and which bank problem, which problems stay on the whiteboard and when you practise each one, and how to turn "I built this" into a structured 45-minute answer instead of a monologue.

---

## 1. How to use this map

1. **At every stage close**, run that stage's SD session (section 9 of every stage file). "Built" problems are answered from the repo; "whiteboard" problems are answered on paper, then compared with what Atlas would do.
2. **In the weekly drill hour**, rehearse one concept from section 2 aloud in two minutes: the claim, your number, the failure you saw, the fix, the trade-off.
3. **Before a mock or a real interview**, reread section 4 for the problems likely to come up and fill in the numbers table in section 5.3 from `docs/evidence/`.
4. **Never claim more than you measured.** "At synthetic volume on a laptop, under the ADR-002 protocol" is a strong sentence. An invented production number is a weak one that falls apart at the first follow-up question.

---

## 2. Concept → where in Atlas

The first 23 rows are the core concepts Atlas was designed around (see the [README](README.md) thesis and decision tables); the rest are concepts interviewers probe that Atlas also covers.

| Concept | Where in Atlas | What you can show | What changes at 100× (the whiteboard extension) |
|---|---|---|---|
| **Caching and stampede** | [S3](stage-03-redis-auth-bot.md) Cache block | Cold vs warm p95; the invalidation audit with one test per price-write path; the DB spike when a hot key expires, fixed with single-flight, TTL jitter and stale-while-revalidate; the stale-set race fixed with delete-after-commit and versioned keys | Cache tiers, request coalescing at the proxy, CDN for public reads |
| **CDN** | [S11](stage-11-realtime-edge-graphql.md) React SPA, plus an S11 stretch item; no stage has a must-tier CDN block | S11 serves the hashed SPA assets from the edge host with long-lived `Cache-Control` and a short one on `index.html`: the cache-header half of a CDN. The S11 stretch item (0.5 h) puts those assets behind the cloud provider's CDN and records the cache-hit ratio and what a deploy must do so no browser gets a new `index.html` pointing at assets that are gone. If you skip it, the CDN itself stays a whiteboard concept (SD10) | SD10: almost no bytes touch your servers |
| **Load balancing** | [S6](stage-06-ship-and-operate.md) Nginx; [S10](stage-10-kubernetes-grpc-inventory.md) gRPC client-side LB | Nginx upstream switch during deploys; the HTTP/2 trap: after scaling 1→4 every RPC stays on one pod; the three-part fix (headless Service, `dns:///` with round_robin, server `max_connection_age`) and the per-pod spread table | L7 proxies or a mesh (Linkerd is the S10 stretch) |
| **Replication** | [S6](stage-06-ship-and-operate.md) streaming replica; [S9](stage-09-strangler-atlaspay-auth.md) logical replication; [S7](stage-07-polyglot-mongo-timescale.md) Mongo replica set | Replication lag; recovery-conflict cancellations; a publication of `payments_*` tables feeding the atlaspay DB during the strangler | Multi-region replicas, failover automation (Patroni is named only) |
| **Consistency: read-your-writes, write concerns** | [S6](stage-06-ship-and-operate.md), [S7](stage-07-polyglot-mongo-timescale.md) | "Unpaid" read from the replica right after paying, fixed with sticky-primary-after-write or an LSN wait (the primary returns its WAL position, the *log sequence number*, after the write, and the read waits until the replica has replayed past it); the number of acknowledged writes `w:1` lost when the primary died vs `w:"majority"` | Quorum reads/writes (SD4), causal consistency tokens |
| **Consensus** | etcd under kind and the Lease ([S10](stage-10-kubernetes-grpc-inventory.md)); Mongo elections ([S7](stage-07-polyglot-mongo-timescale.md)) | You rely on Raft (etcd) and on Mongo's election protocol and can explain what each guarantees; you did not implement consensus yourself (the old Phase 5 did) | Raft log replication, leader leases, split brain |
| **Sharding and consistent hashing** | [S9](stage-09-strangler-atlaspay-auth.md) webhook ring; [S12](stage-12-data-at-scale-fraud.md) Citus and Mongo; [S3](stage-03-redis-auth-bot.md) Redis Cluster | Keys moved going from 3 to 4 dispatchers with vnodes vs `hash % N` (consistent hashing for work assignment, not data sharding); the ledger distributed by `owner_account_id` with every entry single-shard; the naive key that triggered Citus 2PC; `reshardCollection` under writes; CROSSSLOT and hash tags | Resharding at petabyte scale, directory-based sharding, rebalancing policies |
| **ID generation** | [S1](stage-01-layered-monolith.md) Postgres proofs | bigint PK plus a UUIDv7 public id; UUIDv7 vs v4 insert speed and index size at 1M rows; UUIDv7 `event_id` on every event | SD6: Snowflake layout, clock skew |
| **Idempotency** | [S2](stage-02-checkout-correctness.md) Idempotent checkout; [S5](stage-05-atlaspay-monolith.md) Intents and idempotency | Why Redis was the wrong store (not transactional with the order, evictable, lost on restart); `INSERT … ON CONFLICT DO NOTHING RETURNING` with a request hash; Stripe semantics (stored once execution starts, 409 while in flight, `Idempotent-Replayed`); Payme's replay rule (the stored `result`/`error` bytes re-wrapped in an envelope with the *current* JSON-RPC `id`, caught by the provider-sim "retry with a new id" switch); `Idempotency-Key = ActionRequest.id` for agent refunds (S8); retry the same key on an unknown outcome (S9) | Idempotency across regions, key retention cost |
| **At-least-once delivery** | [S4](stage-04-async-events-boundaries.md) RabbitMQ, Outbox, Consumers | Publisher confirms; N messages before a broker restart = N after; the inbox table `UNIQUE(consumer, event_id)`; DLX retry tiers and a parking lot, with at-least-once dead-lettering on quorum queues so a missing parking queue loses nothing | Kafka consumer groups and offsets (Season 2, 2E) |
| **Backpressure** | [S4](stage-04-async-events-boundaries.md) (prefetch 1, bulk 429 backoff, the bot pacer); [S11](stage-11-realtime-edge-graphql.md) (bounded per-socket queues) | A 5,000-chat broadcast producing a 429 storm before the pacer; a slow WebSocket client dropped while the consumer keeps running | Load shedding, admission control, SD12's virtual waiting room |
| **Rate limiting** | The E10 table: [S1](stage-01-layered-monolith.md) → [S3](stage-03-redis-auth-bot.md) → [S9](stage-09-strangler-atlaspay-auth.md) → [S11](stage-11-realtime-edge-graphql.md) | 4× across workers, 12× across containers, the INCR/EXPIRE race, Lua; fail open vs fail closed per endpoint class, proven by killing the store; per-key token buckets with headers; GraphQL cost limits | SD2: global limits across regions, approximate counters |
| **Timeouts, circuit breaker, bulkhead** | [S2](stage-02-checkout-correctness.md) DB timeouts; [S6](stage-06-ship-and-operate.md) `/providers/*` pool; [S8](stage-08-ai-integration.md) Gateway; [S9](stage-09-strangler-atlaspay-auth.md) market as merchant | `lock_timeout`, `statement_timeout` and `idle_in_transaction_session_timeout` each shown against its failure; the LLM retry-storm arithmetic; the closed-breaker outage under 2 s latency with 0% errors, fixed with a bounded pool per downstream sized from locust | Adaptive concurrency limits, retry budgets across a fleet |
| **Saga and why not 2PC** | [S9](stage-09-strangler-atlaspay-auth.md) Saga; [S12](stage-12-data-at-scale-fraud.md) Citus | The cancel-a-vendor-group saga (refund → reverse transfer → restock) with a mid-saga failure test; ADR-034; the measured latency of Citus 2PC and the redesign that removed it | Choreography vs orchestration at many services |
| **CQRS** | [S4](stage-04-async-events-boundaries.md) Consumers and CQRS | The `vendor_order_view` projection, and the "same technique, opposite verdict" rule: stock is never read from a projection | Separate read stores per use case |
| **Event sourcing** | [S5](stage-05-atlaspay-monolith.md) Ledger | Append-only journal enforced by triggers and REVOKE; `rebuild_balances` reproduces balances bit for bit | Snapshots, event-schema evolution at scale |
| **Transactional outbox** | [S4](stage-04-async-events-boundaries.md) Outbox | The lost `order.placed` when publishing after commit with the broker killed; two relays with SKIP LOCKED and no double publish; `outbox_lag_seconds`; daily partitions instead of DELETE bloat | Log-based CDC (Season 2, 2E) |
| **Leader election** | [S10](stage-10-kubernetes-grpc-inventory.md) Lease | The Lease elects one replica of atlaspay's `scheduler` (payouts, reconciliation). Kill the leader mid-period; each period still runs exactly once, with UNIQUE run keys as the backstop | SD14 |
| **Search, vector search, time series** | [S4](stage-04-async-events-boundaries.md) Search; [S8](stage-08-ai-integration.md) RAG; [S7](stage-07-polyglot-mongo-timescale.md) Timescale | The 40-query judged set (LIKE → trgm → FTS, and OpenSearch only if Postgres failed); HNSW vs IVFFlat recall and p95; the filtered-ANN pitfall; hybrid RRF; CAGGs, compression ratio and retention | Dedicated search clusters, vector DBs beyond about 10M vectors, columnar metrics stores |
| **Multi-tenancy** | [S2](stage-02-checkout-correctness.md) RLS | A forgotten WHERE returns 0 rows; the `SET` leak through persistent connections; re-tested under PgBouncer in S10; ADR-009 | Schema or DB per tenant for whale tenants |
| **BFF and API gateway** | [S11](stage-11-realtime-edge-graphql.md) edge; [S6](stage-06-ship-and-operate.md) Nginx; [S10](stage-10-kubernetes-grpc-inventory.md) Gateway/Ingress | The product page going from a 6-call waterfall (measured through market REST in S10) to one client round trip with ≤ 3 downstream calls, one per backend, batched; the 50-item product list going from 51 to 2 downstream calls with DataLoader; the SPA never holds tokens; gateway-level rate limits | Federation, per-client BFFs |
| **Feature flags and canary** | [S8](stage-08-ai-integration.md) Prompts, flags and telemetry | Hash-bucket flags (a user always lands on the same side); a prompt rolled out 10 → 50 → 100% while watching cohort dashboards; S12's shadow → enforce flag for fraud | Progressive delivery platforms, automated canary analysis |
| **Strangler fig** | [S9](stage-09-strangler-atlaspay-auth.md) Strangler | Shadow mode with byte-for-byte reply diffs; logical replication; route switch with a seconds-long write freeze; exit only when the acceptance suite is green and the reconciliation diff is 0 | Multi-year migrations with dual writes |
| Fencing tokens and distributed locks | [S4](stage-04-async-events-boundaries.md) Celery import lock; [S10](stage-10-kubernetes-grpc-inventory.md) Flash sale | A worker paused past its hold TTL: without fencing, two holders commit; with the token checked in Postgres, one is refused. Redlock named with its fencing caveat (S3) | Lock services (etcd, ZooKeeper) |
| Exactly-once job execution | [S4](stage-04-async-events-boundaries.md), [S5](stage-05-atlaspay-monolith.md), [S10](stage-10-kubernetes-grpc-inventory.md) | UNIQUE run keys for the vendor digest; SKIP LOCKED sweeper with 1 vs 4 workers; `pg_try_advisory_xact_lock` on payouts; the Lease on atlaspay's scheduler | SD14 |
| Zero-downtime deploys and migrations | [S6](stage-06-ship-and-operate.md), [S10](stage-10-kubernetes-grpc-inventory.md) | A column rename by expand/contract under load with 0 errors (three deploys, then a separate post-deploy step that drops the old column); connection resets counted without and with graceful shutdown; preStop taking errors from N to 0 | Blue/green across regions |
| Observability and SLOs | [S6](stage-06-ship-and-operate.md) Observability, SLO and drill | One checkout trace end to end, carried through the outbox; RED metrics without high-cardinality labels; SLOs derived from measurements with an error budget; a blameless postmortem | SD19 |
| Backup and disaster recovery | [S6](stage-06-ship-and-operate.md) PITR | Restore to 1 second before a bad UPDATE with an identical trial balance; measured RPO and RTO; nightly restore-verify | Cross-region DR, backup immutability |
| Public API design, versioning and webhooks | [S9](stage-09-strangler-atlaspay-auth.md) API keys, Versioning, Webhooks | Dated `Atlas-Version` pinned per merchant; `oasdiff` gate; `Atlas-Signature` with rotation; no ordering guarantee; a webhook that arrives before the merchant stored its own intent | SD18 follow-ups |
| Double-entry ledger and reconciliation | [S5](stage-05-atlaspay-monolith.md) Ledger, Reconciliation | The float drift; the CHECK that let an unbalanced entry through and the deferred constraint trigger that stops it at COMMIT; nightly FULL OUTER JOIN against provider statements with an injected drift flagged | SD18 |
| Protocol choice | [E4 in the README](README.md); [S10](stage-10-kubernetes-grpc-inventory.md) ADR-037 v1; [S11](stage-11-realtime-edge-graphql.md) ADR-037 v2 | REST vs gRPC p50/p95 (S10); the GraphQL BFF numbers added in ADR-037 v2 (S11); SSE for one-way status, WS for two-way, long-polling measured on a tiny long-poll endpoint in edge, with the bot's own `getUpdates` loop as the everyday example | — |
| Hot keys and hot partitions | [S12](stage-12-data-at-scale-fraud.md) | The platform account hot in the ledger, fixed in place with bucketed sub-accounts before any sharding; `{created_at}` as a Mongo shard key producing one hot shard; whale vendors producing jumbo chunks | SD7's celebrity problem |
| LLM systems | [S8](stage-08-ai-integration.md) | Fallback chain, time-to-first-token timeout, retries only before the first token, $ budgets that fail closed, PII redaction, eval gate in CI, an agent that proposes but never executes money actions | The extra problem: LLM gateway for 50 teams |

---

## 3. SD1–SD20: what is built, what stays on the whiteboard, and when

**Status legend.**
- **Built:** the core of the problem exists in Atlas with tests and numbers. You answer from evidence.
- **Built-lite:** a real but smaller piece exists. You answer the core from evidence and whiteboard the scale-up.
- **Whiteboard:** paper design only. Where possible it is anchored on an Atlas-shaped scenario so you reuse real parts.
- **Closing:** SD20.

| SD | Title (from the bank) | Anchor in Atlas | Status | When | The bank's deep-dive | What to reuse from Atlas |
|---|---|---|---|---|---|---|
| SD1 | Design a URL Shortener | AtlasPay payment links at `/l/{code}` | Built-lite | [S9](stage-09-strangler-atlaspay-auth.md) (W40) | ID generation and redirect latency | Base62 codes, cache-aside, a deleted code returns 404 (Proj26 D169–D170); the bot sends these links for unpaid orders |
| SD2 | Design a Rate Limiter | The E10 table | **Built** | [S3](stage-03-redis-auth-bot.md) (W11) | Algorithm choice under distribution | The 4× → 12× → race → Lua path; `docs/rate-limit-algorithms.md`; the Cluster failover table; S9 per-key tiers |
| SD3 | Design a Distributed Cache | Stampede fix plus the Valkey Cluster lab | Built-lite | [S3](stage-03-redis-auth-bot.md) (W12) | Eviction and cache-instance failure | `allkeys-lru` evicting limiter keys; the cache/state split; CROSSSLOT; master failover under load |
| SD4 | Design a Key-Value Store (Dynamo-Style) | Contrast with Citus and Mongo | Whiteboard | [S12](stage-12-data-at-scale-fraud.md) (W52) | Replication and conflict resolution | The S9 hash ring; Mongo write concerns; why Citus and Mongo are not leaderless |
| SD5 | Design a Web Crawler | — | Whiteboard | [B1](buffers-and-job-sprint.md) (W18) | Politeness and dedup at scale | The outbound token bucket per provider (S5) as per-domain politeness; queues per priority |
| SD6 | Design a Unique ID Generator (Snowflake-Style) | The UUIDv7 benchmark | Built-lite | [S1](stage-01-layered-monolith.md) (W4) | Clock skew and ordering guarantees | UUIDv7 vs v4 at 1M rows; bigint PK plus public UUIDv7 |
| SD7 | Design a News Feed / Timeline | A "followed vendors" feed | Whiteboard | [S11](stage-11-realtime-edge-graphql.md) (W49) | Push vs pull | edge fan-out through Redis Streams; Pareto whale vendors as the celebrity case |
| SD8 | Design a Chat System | Conversations plus edge | **Built** | [S7](stage-07-polyglot-mongo-timescale.md) (W31), [S11](stage-11-realtime-edge-graphql.md) (built W47–W48, written up W49) | Message delivery and ordering | Per-conversation `seq`, dedup on `client_msg_id`, `w:"majority"`, resume from Streams ids, offline notification through the bot |
| SD9 | Design a Notification System | Celery plus the bot pacer | **Built** | [S4](stage-04-async-events-boundaries.md) (W17) | Provider failure and retries | One queue per task class; the leaky-bucket pacer honouring `retry_after`; idempotent on event id; DLQ for chats that blocked the bot |
| SD10 | Design a Video Streaming Platform | CDN and media | Whiteboard | [B2](buffers-and-job-sprint.md) (W37) | Adaptive bitrate and CDN placement | Presigned upload then async processing (thumbnails on the S4 media queue); when you revisit it after S11, the long-lived cache headers on hashed SPA assets and, if you did the S11 CDN stretch item, its cache-hit ratio |
| SD11 | Design a Ride-Sharing Service | Courier tracking | Whiteboard | [B2](buffers-and-job-sprint.md) (W37) | Driver-rider matching | WS vs SSE vs polling from S11; fan-out across pods |
| SD12 | Design a Ticket-Booking System | Oversell and the flash sale | **Built** | [S2](stage-02-checkout-correctness.md) (W8), [S10](stage-10-kubernetes-grpc-inventory.md) (W46) | Overselling prevention | Locked decrement vs EXCLUDE (S2); Lua gate, holds with TTLs, fencing tokens in Postgres, SKIP LOCKED sweeper, exactly 1,000 sold (S10) |
| SD13 | Design a Collaborative Document Editor | — | Whiteboard | [B2](buffers-and-job-sprint.md) (W37) | Conflict-free concurrent edits | WS resume by sequence id (S11) for the reconnect part |
| SD14 | Design a Distributed Job Scheduler | Run keys, SKIP LOCKED, the Lease | Built-lite | [S4](stage-04-async-events-boundaries.md) (W15), [S10](stage-10-kubernetes-grpc-inventory.md) (W45) | Exactly-once execution | UNIQUE run keys, the sweeper, advisory-lock payouts, Lease leader election for atlaspay's scheduler |
| SD15 | Design a Typeahead/Autocomplete Service | trgm and the suggester | Built-lite | [S4](stage-04-async-events-boundaries.md) (paper W16, compared W17) | Prefix matching at scale | pg_trgm, FTS with transliteration, the judged set; the completion suggester if OpenSearch was adopted |
| SD16 | Design a Proximity / Nearby-Search Service | PostGIS pickup points | Whiteboard | [B1](buffers-and-job-sprint.md) (W18) | Spatial indexing trade-offs | GiST knowledge from the S1 EXCLUDE constraint |
| SD17 | Design Distributed File Storage | Presigned URLs on the S3-compatible store (Garage), the WAL archive | Built-lite | [S1](stage-01-layered-monolith.md) (W4), [S6](stage-06-ship-and-operate.md) (W27) | Chunking, replication, metadata | Authorize before minting; TTL ≤ 5 min; metadata in Postgres, bytes in object storage |
| SD18 | Design a Payment System | AtlasPay | **Built** | [S5](stage-05-atlaspay-monolith.md) (W23), [S9](stage-09-strangler-atlaspay-auth.md) (W42); mock #2 in B2 | Idempotency and reconciliation | All of AtlasPay: intents, idempotency, the ledger, Connect, reconciliation, webhooks, keys |
| SD19 | Design a Distributed Logging & Metrics Pipeline | The S6 stack plus Timescale | Built-lite | [S6](stage-06-ship-and-operate.md) (W26), [S7](stage-07-polyglot-mongo-timescale.md) (W31) | High-volume ingestion | Prometheus/Loki/Tempo without high-cardinality labels; CAGGs, compression, retention; ADR-025 |
| SD20 | Design AtlasMarket, From Scratch | Everything | Closing | [S12](stage-12-data-at-scale-fraud.md) (W53) | Your own system | The whole repo, but only after the blank-page attempt |
| Extra | LLM gateway for 50 teams | The ai service | Whiteboard | [S8](stage-08-ai-integration.md) (W36) | Multi-tenant quotas and fallback | The S8 gateway: fallback chain, budgets, redaction, prompt registry, telemetry |

**Mocks:** #1 in B1, #2 in B2, #3 in S12. **Every split ADR doubles as a design doc** (section 7).

---

## 4. Problem-by-problem preparation notes

Each note says what to bring from Atlas, what Atlas does not cover (so you must reason it out), and the follow-up question you should expect.

### SD1 — URL Shortener (Built-lite, S9)
- **Bring:** base62 code generation for payment links, cache-aside on the redirect path, and the rule that a deleted code returns 404 immediately (the cache is invalidated on delete, not left to expire). The bot sends a link for every unpaid order, so the links have a real client.
- **Not covered:** 100M new URLs a day and sharding the mapping table; click analytics at volume.
- **Expect:** "301 or 302, and what does each do to your analytics?"

### SD2 — Rate Limiter (Built, S3)
- **Bring:** the full pain path with its numbers (4× in memory, 12× across 3 containers, TTL-less keys from the INCR/EXPIRE race, over-admission from GET/SET), the Lua sliding counter, the memory and accuracy comparison of five algorithms at 100k keys, and which classes fail open or closed.
- **Not covered:** a global limit across regions.
- **Expect:** "Your Redis is down. What happens to login? To the public API?" (The E10 table answers it.)

### SD3 — Distributed Cache (Built-lite, S3)
- **Bring:** the stampede and its fix; the eviction pain that made you split `redis-cache` from `redis-state`; the Cluster lab and what happened to each limiter class during a master failover.
- **Not covered:** client-side consistent hashing across many independent cache nodes (Memcached style).
- **Expect:** "A cache node dies. What happens to database load in the next ten seconds?"

### SD4 — Key-Value Store, Dynamo-style (Whiteboard, S12)
- **Bring:** the S9 consistent-hash ring (keys moved from 3 to 4 dispatchers); Mongo write concerns and what `w:1` lost; why Citus is coordinator-based and single-leader per shard.
- **Not covered:** leaderless replication, N/W/R quorums, vector clocks, hinted handoff. Work these out on paper.
- **Expect:** "What does W + R > N buy you, and what does it not?"

### SD5 — Web Crawler (Whiteboard, B1)
- **Bring:** per-destination politeness is the same idea as the outbound token bucket to providers (S5); priority queues map to RabbitMQ queues with DLX tiers.
- **Not covered:** a URL frontier at billions of pages, Bloom-filter dedup, `robots.txt`.
- **Expect:** "Why not a plain hash set for seen URLs?"

### SD6 — Unique ID Generator (Built-lite, S1)
- **Bring:** your UUIDv7 vs v4 numbers at 1M rows (insert speed and index size) and why a bigint PK with a public UUIDv7 is the Atlas choice (ADR-005).
- **Not covered:** a Snowflake bit layout and a clock that jumps backwards.
- **Expect:** "What happens to your IDs if the clock goes back 2 seconds?"

### SD7 — News Feed (Whiteboard, S11)
- **Bring:** edge fan-out through Redis Streams with resume; whale vendors (the Pareto head) as the celebrity case.
- **Not covered:** precomputed timelines at millions of followers.
- **Expect:** "Walk me through why a celebrity breaks fan-out-on-write, with numbers."

### SD8 — Chat (Built, S7 + S11)
- **Bring:** the Postgres-partitions baseline and why conversations moved to Mongo anyway (ADR-024: document-shaped, append-only, TTL, per-conversation access, needs to scale out); `w:"majority"`; per-conversation `seq`; `client_msg_id` dedup; WS fan-out across pods; resume from Streams ids; the "half the updates missing" pain.
- **Not covered:** end-to-end encryption; group chats of thousands.
- **Expect:** "A client reconnects after 30 seconds offline. How does it get exactly the messages it missed?"

### SD9 — Notification System (Built, S4)
- **Bring:** one queue per task class so a slow channel cannot block another; the leaky-bucket pacer (about 30 msg/s global, 1/s per chat, 20/min per group, honouring `retry_after`); the 429 storm you produced before the pacer; idempotency on event id.
- **Not covered:** SMS and mobile push providers.
- **Expect:** "The triggering event is delivered twice. Does the user get two messages?"

### SD10 — Video Streaming (Whiteboard, B2)
- **Bring:** the presigned-upload-then-process pattern (images and thumbnails in S1/S4). SD10 is whiteboarded in B2 (W37), before S11. When you revisit it after S11, add the cache headers on hashed SPA assets and, if you did the S11 CDN stretch item, its cache-hit ratio.
- **Not covered:** transcoding ladders, adaptive bitrate manifests.
- **Expect:** "Why should almost no video bytes touch your servers?"

### SD11 — Ride Sharing (Whiteboard, B2)
- **Bring:** the protocol choice (WS for two-way, SSE for one-way) and multi-pod fan-out from S11; a Tashkent courier-tracking framing keeps it concrete.
- **Not covered:** geospatial indexing of moving objects, matching algorithms.
- **Expect:** "Greedy nearest driver or batched assignment? When would you switch?"

### SD12 — Ticket Booking (Built, S2 + S10)
- **Bring:** the two-buyer race and why `UPDATE … WHERE qty >= n RETURNING` beats `FOR UPDATE` for a single row; the EXCLUDE pattern for time slots; the flash sale (Redis gate, holds with TTLs, fencing tokens checked in Postgres, SKIP LOCKED sweeper) with exactly 1,000 sold; the paused-worker pain.
- **Not covered:** a virtual waiting room in front of the booking path (whiteboard it).
- **Expect:** "What happens to a hold when the buyer closes the tab?"

### SD13 — Collaborative Editor (Whiteboard, B2)
- **Bring:** reconnect-and-resume by sequence id from S11.
- **Not covered:** OT and CRDTs.
- **Expect:** "Why does locking the document fail the requirement?"

### SD14 — Job Scheduler (Built-lite, S4 + S10)
- **Bring:** UNIQUE run keys (the vendor digest), the SKIP LOCKED sweeper, advisory locks on payouts, and the Lease that elects atlaspay's scheduler, with its exactly-once test after killing the leader. The old Project 28 (`../../phase-6-capstone.md` D175–D178) used a from-scratch Raft cluster; Atlas uses the Kubernetes Lease, which relies on etcd's Raft underneath. Say that difference out loud.
- **Not covered:** a scheduler for millions of user-defined jobs.
- **Expect:** "The job succeeded, then the worker crashed before recording it. What prevents a second run?"

### SD15 — Typeahead (Built-lite, S4)
- **Bring:** the judged-set table (LIKE → trgm → FTS), Latin↔Cyrillic transliteration, p95 per step.
- **Not covered:** a trie service with popularity ranking at Google scale.
- **Expect:** "How do you keep p99 under 50 ms when every keystroke is a request?"

### SD16 — Proximity Search (Whiteboard, B1)
- **Bring:** GiST from the S1 EXCLUDE constraint; a PostGIS pickup-point framing.
- **Not covered:** geohash vs quadtree vs R-tree trade-offs; dense vs sparse areas.
- **Expect:** "How do you re-rank by rating without losing the spatial index's speed?"

### SD17 — Distributed File Storage (Built-lite, S1 + S6)
- **Bring:** authorize before minting a presigned URL, TTL ≤ 5 min (S1); the WAL archive in object storage (S6); metadata in Postgres, bytes in the S3-compatible store (Garage).
- **Not covered:** chunking, dedup and replica placement.
- **Expect:** "Two users upload the same 2 GB file. Do you store it twice?"

### SD18 — Payment System (Built, S5 + S9)
- **Bring:** everything. The intent lifecycle, the idempotency rules stated precisely from memory, the 12 failure scenarios, the ledger with the deferred constraint trigger, Connect math with largest-remainder refunds, reconciliation catching a transaction Payme staff resolved by hand, the shadow cutover with diff = 0, signed webhooks.
- **Not covered:** card networks and disputes (neither provider has a dispute protocol; disputes are a whiteboard stretch in S5); a licence (ADR-017 notes ЗРУ-578 Art. 15).
- **Expect:** "Your call to the provider timed out. Did the customer pay?"

### SD19 — Logs and Metrics Pipeline (Built-lite, S6 + S7)
- **Bring:** RED metrics with no high-cardinality labels; traces carried through the outbox; ADR-025 (Timescale vs matview vs Prometheus); compression ratio and retention.
- **Not covered:** a log shipper fleet at terabytes a day; columnar stores (ClickHouse is part of the answer, not built).
- **Expect:** "How do alerts stay fast without every rule scanning raw data?"

### SD20 — AtlasMarket from scratch (Closing, S12)
- **Rules:** 45 minutes, blank page, no notes, no repo. Only then open the repo and write `docs/sd20-retro.md`: every difference between the fresh design and what you shipped, and for each, whether the shipped system was right or you would now build it differently.
- **Why it matters:** this becomes your answer to "walk me through a system you built", and you can defend every disagreement with your past self.

### Extra — LLM gateway for 50 teams (Whiteboard, S8)
- **Bring:** the fallback chain and what triggers each hop, retries only before the first token, SDK retries counted, per-provider breakers and bulkheads, $ budgets with reserve-then-reconcile, PII redaction before prompts and logs, `prompt_id@version` on every call, OTel GenAI spans.
- **Not covered:** chargeback between 50 teams, per-team model allow-lists, a shared semantic cache across tenants (and why the S8 cache-key lesson forbids a naive one).
- **Expect:** "Team A's runaway job is burning the shared quota. What stops it?"

---

## 5. The 45-minute answer framework

### 5.1 The clock

This follows the bank's six-step skeleton (clarify, estimate, high-level design, data model, deep dive, trade-offs), with a time box for each step.

| Minutes | Step | What you produce | Common failure |
|---|---|---|---|
| 0–5 | **Clarify scope** | 3–5 functional requirements written down; the non-functional ones (latency, availability, consistency, durability); what is out of scope | Designing before agreeing what is being designed |
| 5–10 | **Estimate** | Read and write QPS, storage growth per year, peak-to-average ratio; round numbers are fine | No numbers at all, so no later choice can be justified |
| 10–20 | **High-level design** | Boxes and arrows for the 2 main flows, one sentence per box | Drawing 15 boxes nobody asked for |
| 20–25 | **Data model** | The 2–4 core tables or collections, their keys, and the access pattern that chose each key | A full schema, or none |
| 25–38 | **Deep dive** | The one hardest part (the bank names it per problem), solved with numbers and failure modes | Spreading the deep dive thinly across everything |
| 38–43 | **Trade-offs and operations** | What breaks first at 10×, what you would measure, the SLO, the alert, the rollback | Claiming the design has no weaknesses |
| 43–45 | **Summary** | The design in three sentences, and the next two things you would do | Running out of time mid-sentence |

If the interviewer steers, follow them; the clock is a default, not a script.

### 5.2 The Atlas move: turning evidence into an answer

When a question touches something you built, answer in five beats. It takes about 90 seconds.

1. **Claim:** "In my marketplace, two buyers racing for the last unit could both succeed."
2. **Number:** "A barrier test with two buyers sold 2 of 1 unit on the naive version."
3. **Cause:** "Read-then-write in two statements; both reads saw 1."
4. **Fix:** "A conditional `UPDATE … WHERE qty >= n RETURNING`; I compared it with `FOR UPDATE` on what each locks and for how long."
5. **Trade-off:** "For a flash sale at 5,000 users that is not enough on its own; I put a Redis gate with fenced holds in front of it."

Then stop and let the interviewer choose where to go. If they ask about a scale you did not test, say so, then reason: "I measured this at 1M rows on a laptop; at 100× I would expect … and I would check it by …".

### 5.3 Your numbers table

Fill this in from `docs/evidence/` before mock #1 and keep it current. Do not invent values; an empty cell is better than a made-up one.

| Measurement | Stage | Your value | Protocol / conditions |
|---|---|---|---|
| Catalog p95 cold vs warm | S3 | | |
| OFFSET 400k vs keyset at 1M rows | S1 | | |
| UUIDv7 vs v4 insert speed and index size at 1M rows | S1 | | |
| Checkout p95 before and after moving the confirmation email off the request path | S2 → S4 | | |
| Limiter over-admission: in memory, 3 containers, after Lua | S1 → S3 | | |
| Carts lost on `kill -9` under RDB vs AOF | S3 | | |
| Payme callback p99 during the lock-queue incident | S6 | | |
| Split-gate baseline: callback p99, % -32400/timeouts, checkout p95, pool saturation | S6 | | |
| Token-refresh p99 during the lock-queue stall | S6 | | |
| Replication lag; RPO and RTO achieved | S6 | | |
| Acknowledged writes lost under `w:1` | S7 | | |
| 8 streamed chats vs checkout latency | S8 | | |
| HNSW vs IVFFlat recall@10 and p95 | S8 | | |
| Keys moved from 3 to 4 dispatchers: ring vs `% N` | S9 | | |
| Unrelated-endpoint p95 under 2 s latency, before and after the bulkhead | S9 | | |
| Request errors during rollout without and with preStop | S10 | | |
| Per-pod RPC spread after scaling 1→4, before and after the fix | S10 | | |
| REST vs gRPC p50/p95 | S10, S12 | | |
| Product-page waterfall through market REST: call count and p95 | S10 | | |
| Socket drops per market deploy (Channels) | S11 | | |
| Product-list downstream calls (51 → 2 with DataLoader) and product-page calls (≤ 3) with p95 | S11 | | |
| Posting p95 single node, with 2PC, and single-shard | S12 | | |
| Fraud p99 and payment success with fraud killed | S12 | | |

### 5.4 Back-of-envelope helpers

- A day has 86,400 seconds, roughly 10^5. So 1M requests a day is about 12 per second on average; multiply by your peak-to-average ratio.
- Storage per year = rows per day × bytes per row × 365 × replication factor, plus indexes (often as large as the table).
- Say which resource runs out first (CPU, connections, IOPS, memory, network) and why. The split gate taught you that the answer is often the connection pool.

---

## 6. Mock interview plan

The full formats (minute by minute), the rubrics and the retro template live in [buffers-and-job-sprint.md](buffers-and-job-sprint.md); this is the summary and how each mock connects to the SD work above.

| Mock | When | Format | Content | Output |
|---|---|---|---|---|
| **#1** | [B1](buffers-and-job-sprint.md) (W18) | 60 min, timed, plus a 30-min retro | Backend deep dive on S1–S4 (Postgres proofs, races, idempotency, Redis, outbox) plus SD12 | `docs/sd/mock-01-retro.md`; every rubric row scored 1 or 2 becomes a drill item for the next two weeks |
| **#2** | [B2](buffers-and-job-sprint.md) (W37) | 60 min, timed | Payments deep dive (SD18 on AtlasPay: the 12 scenarios, the ledger, reconciliation) plus behavioural questions answered with your STAR stories | `docs/sd/mock-02-retro.md` |
| **#3** | [S12](stage-12-data-at-scale-fraud.md) (W53), inside the Closing block | 60 min, timed | A bank problem you have only whiteboarded (SD4, SD5, SD7, SD10, SD11, SD13 or SD16) at a scale you have not rehearsed, then a backend deep dive on S9–S12 | `docs/sd/mock-03-retro.md` |
| **SD20** | [S12](stage-12-data-at-scale-fraud.md) (W53) | 45 min, solo, blank page | Design AtlasMarket from scratch, then diff against the repo | `docs/sd20-retro.md` |

SD20 and mock #3 are different exercises: SD20 is about the system you built, alone; mock #3 is with an interviewer, on a problem you did not build.

**Who plays the interviewer** (in order of preference, as the buffers file sets out): a person (a colleague, someone from a local backend community, or a peer mock-interview partner); the mentor, by saying "mock interview"; or, as a last resort, a recorded self-mock scored 24 hours later. Part of what you practise is thinking aloud in front of someone, so use a person whenever you can.

**Scoring.** Use the technical-deep-dive, system-design and behavioural rubrics in the buffers file (each row 1–4; pass bar: an average of at least 3 with no row at 1). For the system-design part, the dimensions map directly onto the clock in section 5.1: scope, estimation, high-level design, data model, deep dive, trade-offs, and time management. The one habit this map adds: for every score, write one sentence of evidence ("scored 2 on estimation: gave no storage number").

**Behavioural preparation.** Each stage produces 2 STAR stories (`docs/star/`); by S12 you have about 25 and choose the final 8. Map them to the categories of `../../behavioral-interview-questions.md` (mistakes, scope and saying no, incidents, disagreement, ownership, system-level trade-offs) so every category has at least one real story. The buffers file has the template, the quality bar and the stage-by-stage story list.

---

## 7. Design docs per split

Every extraction ADR is also a design doc and doubles as interview material. Each one must follow this outline:

1. **Context and forcing problem**, with the split-gate numbers (the S6 protocol, re-run for every extraction).
2. **Options**, always including "do not split" and the named counter-argument in the table below.
3. **Decision**, and the reason in one paragraph.
4. **What it costs**: new failure modes (network, partial failure, consistency), new operational work.
5. **Migration plan**: strangler steps, exit criterion, rollback.
6. **What would revert it**: the numbers that would make you merge it back.
7. **The "if the numbers don't hurt" clause**: if the measurements do not show pain, the ADR says so and argues only from blast radius or security scope, or the split does not happen.

| ADR | Split | Stage | Counter-argument it must answer |
|---|---|---|---|
| ADR-027 | ai | [S8](stage-08-ai-integration.md) | Async Django views can stream |
| ADR-030 | atlaspay | [S9](stage-09-strangler-atlaspay-auth.md) | Extract it as a Django service (move, don't rewrite) |
| ADR-031 | auth | [S9](stage-09-strangler-atlaspay-auth.md) | Buy Keycloak or Auth0; RS256 alone does not need a split; a separate DB pool inside market would cure the token-refresh stall S6 measured (so the split must argue from issuer neutrality, the new OIDC/PKCE/MCP-client surface and blast radius, not from the stall) |
| ADR-036 | inventory | [S10](stage-10-kubernetes-grpc-inventory.md) | Reservation and order in one local transaction is the oversell-proof shape; extraction turns checkout into a saga |
| ADR-038 | edge | [S11](stage-11-realtime-edge-graphql.md) | Channels keeps one codebase and wins while deploys are rare |
| ADR-040 | ledger on Citus | [S12](stage-12-data-at-scale-fraud.md) | Most companies keep the ledger inside payments; single-node Postgres may suffice at this volume (labelled the most debatable split, revertible) |
| ADR-042 | fraud serving | [S12](stage-12-data-at-scale-fraud.md) | In-process is the lowest latency |

---

## 8. SD calendar

| Week | Stage | SD work |
|---|---|---|
| W4 | S1 | SD6 (UUIDv7 benchmark); SD17 part 1 (presigned URLs, a five-line note) |
| W8 | S2 | SD12 built: locked decrement vs EXCLUDE |
| W11 | S3 | SD2 built |
| W12 | S3 | SD3 built-lite |
| W15 | S4 | SD14 part 1 (run keys, SKIP LOCKED) |
| W16 | S4 | SD15 paper design |
| W17 | S4 | SD9 built; SD15 compared with the built-lite version |
| W18 | B1 | SD5 and SD16 whiteboards; mock #1 (S1–S4 plus SD12) |
| W23 | S5 | SD18 built (in the monolith) |
| W26 | S6 | SD19 part 1 (observability stack) |
| W27 | S6 | SD17 part 2 (WAL archive) |
| W31 | S7 | SD8 storage half; SD19 part 2 (Timescale) |
| W36 | S8 | LLM gateway for 50 teams (whiteboard) |
| W37 | B2 | SD10, SD11, SD13 whiteboards; mock #2 (payments plus behavioural) |
| W40 | S9 | SD1 built-lite (payment links) |
| W42 | S9 | SD18 revisited after the extraction |
| W45 | S10 | SD14 part 2 (Lease) |
| W46 | S10 | SD12 again: the flash sale |
| W49 | S11 | SD8 realtime half written up (built in W47–W48); SD7 whiteboard |
| W50 | B3 | Catch-up first; no new SD problem. If on track, redo the weakest topic from mocks #1 and #2 using the numbers table (section 5.3) |
| W52 | S12 | SD4 whiteboard |
| W53 | S12 | SD20 closing; mock #3 |

---

## 9. Common mistakes in system-design answers

1. Jumping to technology names ("Kafka, Redis, Kubernetes") before requirements.
2. No numbers, so every choice is a matter of taste.
3. Describing Atlas as if it ran at production scale. Say "synthetic volume" and reason about the gap.
4. Deep-diving the part you know best instead of the part the problem is about.
5. Forgetting failure: what happens when this box is slow, not just when it is down (the closed-breaker lesson from S9).
6. Treating a split as free. Every service boundary adds a network hop, partial failure and a consistency question.
7. Not saying what you would measure to know you were right.
