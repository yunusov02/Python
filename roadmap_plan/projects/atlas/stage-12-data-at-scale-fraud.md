# Stage 12 — Data at scale + fraud service + closing

| | |
|---|---|
| **Weeks** | W51–W53 (3 weeks), right after the B3 buffer (W50) |
| **Hours** | 36 must + 3 stretch (39 total) |
| **Architecture at start → at end** | 7 production deployables (`market`, `atlaspay`, `auth`, `ai`, `edge`, `bot`, `inventory`) plus `provider-sim`, on kind and k3s. The ledger is a module inside `atlaspay` on single-node PG17 (`pg-atlaspay`). Fraud v1 scores in shadow mode, in process, inside `atlaspay` (ported there in S9, with its feature function in the `libs/atlas-fraud-features` wheel and the `fraud.features` consumer as an atlaspay process). Chat lives on the S7 Mongo 8.0 replica set → **9 production deployables** plus `provider-sim`: + **`ledger`** (grpc.aio + SQLAlchemy Core on `citus-ledger`, distribution column `owner_account_id`) and + **`fraud`** (grpc.aio, model loaded at startup, called with a 50 ms deadline). Plus a **Mongo sharded lab** for chat and the **Redis Cluster lab** from S3, both written up in ADR-041. |
| **New technologies** | Citus 14.2 (distributed and reference tables, co-location, two-phase commit, the online rebalancer `citus_rebalance_start()`), grpc.aio server-streaming over SQLAlchemy Core, a MongoDB 8.0 sharded cluster (mongos, the config-shard option, ranged and hashed shard keys, `reshardCollection`), serving a scikit-learn model over gRPC behind a deadline and a breaker |
| **Portfolio tag** | `v1.0` |
| **Old-spec theory to read** | [P8 D131](../python/08-docuvault.md) (§11: the sharding decision record and the consistent-hashing ring with virtual nodes vs `hash % N`; daily plan in [phase-5 D131](../../phase-5-scaling-architecture.md)); [P9 D151–D156](../python/09-payflow.md) (Stage 2: gRPC `PostJournalEntry` with a deadline and a circuit breaker, status-code mapping, REST vs gRPC p50/p95, the restore verified against the trial balance; Stage 3: the load test and the drill that kills `ledger-service`; daily plan in [phase-6 Week 26](../../phase-6-capstone.md)); [P9 Wk26 ML extension](../python/09-payflow.md) (§21: a fraud-signal model with a latency histogram and a score-distribution panel, "a signal, not a decision"); the SD bank, [SD4 and SD20](../../system-design-problems.md) |

Version pins are as of 2026-09. Re-check them with `scripts/compat_check.sh` before you start (ADR-001). The Citus 14.2 image tag for PG17 is **[U]**; the fallback is to build FROM `postgres:17` and install the extension yourself. There is no official Compose recipe for a Mongo sharded cluster **[U]**; you build one from the `mongo` image. Add Citus (AGPL-3.0: this matters only if you modify it and offer it as a service) to the ADR-003 licences register.

> **What this stage is really for.** Sharding is the most over-prescribed cure in backend interviews. Here you earn it: fix the hot spot in place first, shard only on the key Atlas's own numbers point to, and then prove the money invariants still hold across shards and during a rebalance. You also move the fraud model into the payment path with a hard deadline, so a model outage can never become a payment outage. Then you close Season 1 by designing the whole system again on a blank page and arguing with your past self.

---

## 1. The problem this stage starts from

S11 ended with two problems (the [README §5.1 evolution table](README.md#51-the-evolution-table), row S11): **the ledger reaches 50M lines and the platform account is hot**, and **model dependencies bloat every `atlaspay` replica**. You measure both in this stage before you change anything. S7 added a third, deferred one: chat was moved to Mongo partly because it "will need to scale out in S12" (ADR-024).

**In business terms:**
- Every money movement AtlasPay makes is a journal entry. Every payment also touches the platform's fee account. At peak, postings queue behind each other on that one account, and slower postings mean slower payouts, slower refunds and slower statements for every vendor.
- Fraud is still scored in shadow mode only. The S7 model sees card-testing bursts and does nothing about them. The business wants it enforced, but not at the price of payments failing whenever the model misbehaves.
- Buyer↔vendor chat keeps growing. It is append-only and per conversation. One replica set will eventually run out of write capacity or disk.

**In engineering terms:**
- The ledger shares `pg-atlaspay` with the provider callbacks. Vacuum on a 50M-line table, lock waits on the hot platform account and long statement reads all compete with the callbacks' short transactions (S6's lock-queue incident showed what that costs).
- Scoring in process means every `atlaspay` replica carries scikit-learn, the model and its memory. When HPA (the Kubernetes autoscaler, S10) scales `atlaspay` for a flash sale, it scales the model's memory too. A new model version means a payments deploy. And a library inside the process cannot be killed on purpose, so the fallback has never really been tested.
- The chat collection has no shard key, and choosing one is a decision you cannot easily undo.

---

## 2. Outcomes — what exists when the stage is finished

1. **Single-node ledger numbers at 50M lines** (20M on a 16 GB laptop): posting p95, lock waits on the platform account, vacuum time. Measured again after fixing the hot account **in place** with bucketed sub-accounts.
2. **ADR-040**, labelled **the most debatable split, revertible**, with the "if the numbers don't hurt, say so" clause.
3. **`services/ledger`**: `atlas.ledger.v1.LedgerService` with `PostEntries` (idempotent by `entry_key`), `GetBalance` and server-streaming `StreamStatement`, on grpc.aio + SQLAlchemy Core, served over gRPC with the S10 load-balancing fix.
4. **Citus, naive first:** the S5 triggers meet `create_distributed_table`, then distribution by `ledger_account_id`, with the two-phase-commit cost of cross-shard entries measured. **Then the redesign:** distribution by `owner_account_id` with per-shard platform sub-accounts, reference tables and co-location, and **every journal entry single-shard**, enforced by a router-plan assertion test. The S5 balance and append-only triggers run per shard under `citus.enable_unsafe_triggers`, a conscious choice recorded in ADR-040.
5. **The posting paths:** async postings from `atlaspay`'s outbox through `ledger.postings`; synchronous gRPC checks for debits (payouts, refunds) with a deadline and same-key retries; a nightly `atlaspay`↔`ledger` reconciliation.
6. **A rebalance under load:** add a worker, run `citus_rebalance_start()`, record p99 and errors (target: 0 failed postings), trial balance identical before and after.
7. **REST vs gRPC p50/p95** for the ledger, and the restore-verify job extended to the ledger.
8. **The Mongo sharded lab:** the S7 unique index meeting `shardCollection`, two bad shard keys measured, `reshardCollection` while writes continue, and targeted vs scatter-gather `explain` output.
9. **ADR-041 (sharding):** Citus vs app-level routing, the Mongo shard keys, Redis Cluster, and what Atlas deliberately does not shard.
10. **`services/fraud`**: `atlas.fraud.v1.FraudService/Score` with p99 ≤ 30 ms, called by `atlaspay` with a 50 ms deadline behind a breaker, falling back to rules, recording `model_version` on every decision, moved from shadow to enforce through a flag. Killing it mid-load leaves payments flowing.
11. **ADR-042** and an updated **model card**.
12. **Season 1 closing:** SD20 on a blank page in 45 minutes plus `docs/sd20-retro.md`; mock interview #3; the final 8 STAR stories chosen from about 25; the final README, diagrams and demo. Tag **`v1.0`**.

---

## 3. Architecture at the end of the stage

```
                     provider-sim (Payme / Click)
                              | callbacks
                              v
   market --REST sk_--> atlaspay -------------- gRPC Score, 50 ms deadline, breaker ---> fraud (x2+)
     ^   webhooks          |   |                    fallback: rules only                   |  model loaded at start
     |                     |   |                                                           |  (S3 store: atlas-models)
     |                     |   +-- gRPC PostEntries (debits: payouts, refunds),            +--> redis-state (1m/10m windows)
     |                     |       deadline, same entry_key on retry                        +--> tsdb fraud_features
     |                     |              |                                                       (velocity_1h / _24h)
     |                     +-- outbox --> RabbitMQ atlas.events                              ^
     |                                    |   queue ledger.postings  (credits, async)        | queue fraud.features
     |                                    |   queue fraud.features <- payment_attempt.created-+
     |                                    v
     |                               ledger (x2+, grpc.aio + SQLAlchemy Core)
     |                                    |  headless Service + round_robin + max_connection_age
     |                                    v
     |                          citus-ledger coordinator
     |                           /        |          \
     |                     worker 1    worker 2    worker 3 (added under load, rebalanced)
     |                     shards by owner_account_id; accounts, journal_entries, journal_lines,
     |                     balance_transactions co-located; reference tables on every node
     |
     +-- conversations --> Mongo 8.0 replica set (production path, S7)
                           Mongo sharded LAB: mongos + config shard + shard RS; messages
                           resharded {vendor_id} -> {conversation_id: "hashed"}
```

**What changed and why:**
- **`ledger` left `atlaspay` and runs on Citus.** It has a single natural shard key (the connected account that owns the money), 50M lines, and a hot account. That last one was fixed in place first, so the ADR can say how much of the problem the cheap fix already solved (the split-gate rule, §8.6 of the [README](README.md)). The ledger's vacuum, lock waits and long statement reads no longer share a database with the provider callbacks.
- **`fraud` left the payment process.** Its dependencies, its memory and its deploy cadence are now its own. Its failure is now something you can cause on purpose, so the fallback is finally testable. The price is a network hop on the payment path, bounded by a 50 ms deadline.
- **Chat is sharded only in a lab.** The production chat path stays on the S7 replica set. The lab proves you can choose, and change, a shard key with numbers, and ADR-041 records what production sharding would need.
- **Orders and payment intents are not sharded** (E3). They have two access keys (buyer and vendor), and lookups arrive by provider id. ADR-041 explains why a single shard key would hurt more than it helps.

---

## 4. Build plan

The hours in brackets are must-tier budgets, sized bottom-up, and they include the unattended time of benchmark runs (configurations × runs × about 11 minutes). Keep logging actual hours per block in `docs/hours.csv`, and multiply this stage's budget by the actual/budget ratio you re-checked at B3: if the result does not fit in W51–W53, the date moves now, openly. The ledger block and the fraud fallback carry never-cut spine items (the gRPC ledger with the load-balancing fix, the Citus single-shard rule, the fraud fallback, SD20): if one of them overruns, finish it and let the date move rather than deferring it silently.

| Block | Must hours |
|---|---|
| 4.1 Ledger on Citus | 17.5 |
| 4.2 Mongo sharding | 4.5 |
| 4.3 Fraud service | 8 |
| 4.4 Closing | 4 |
| 4.5 Drills + SD4 | 2 |
| **Total** | **36** |

A suggested order across the three weeks:

| When | Work |
|---|---|
| W51 weekdays | 4.1 steps 1–4: seed, find the hot spot, the bucket fix, the ADR-040 Context, the `ledger` service skeleton; start step 7 (the credits consumer) |
| W51 weekend | 4.1 baseline runs before and after buckets; steps 5–6: the trigger refusal, naive Citus and its 2PC runs, the redesign and its runs |
| W52 weekdays | 4.1 the rest of step 7 (debits, the data move, reconciliation) and step 9 (REST vs gRPC, restore-verify); 4.5 SD4 whiteboard and drill |
| W52 weekend | 4.1 step 8 rebalance under load; 4.2 Mongo lab, the shard keys and the reshard under writes |
| W53 weekdays | 4.3 fraud service, client, fallback, flag and tests; 4.4 STAR selection, README and demo refresh |
| W53 weekend | 4.3 latency runs and the fraud-down chaos run; 4.4 SD20 and mock #3 |

The rebalance under load, the reshard under writes, the fraud-down chaos run and SD20 are weekend-block tasks: each needs uninterrupted state.

### 4.1 Ledger on Citus [17.5 h, must]

**Why this exists.** A *distributed database* splits one logical table into *shards* (pieces) spread over several servers, so writes and storage scale out. It also makes every operation that touches more than one shard slower and harder to keep correct. The whole block is about choosing the key that keeps the operations you care about on one shard. For a ledger, that operation is posting a journal entry, because the balance invariant (Σ debits = Σ credits) must hold inside it.

Suggested split of the 17.5 hours: baseline and in-place fix 2.5; ADR draft and service skeleton 3.5; the trigger refusal, naive Citus and the 2PC cost 2; redesign and router-plan test 2.5; posting paths, the data move and reconciliation 3.5; rebalance under load 1.5; REST vs gRPC and restore-verify 2. About 4.5 h of this is unattended benchmark time: 3 runs before the bucket fix and 5 after it, 3 runs on the naive key and 5 on the redesign (the final before/after pair for ADR-040 is single-node-with-buckets vs the redesigned cluster, so both get 5 runs), one long rebalance run, and 2 × 3 runs for REST vs gRPC. Schedule the runs in the weekend blocks.

The baseline runs are split-gate runs: use `bench/split-gate` as you ported it to kind in S10 (the mid-run deploy is a `kubectl rollout` with the migration Job), with worldgen posting load as this stage's forcing load. They replace separate baseline runs; they are not extra.

**What to build:**

1. **Baseline on a single node.**
   - Seed 50M journal lines with worldgen in `history` mode (COPY-ready). On a 16 GB laptop, 20M. Record which one in every evidence file.
   - Run a posting load shaped like real traffic (worldgen `traffic` mode: payments, transfers, fees, refunds, payouts) through the ported split gate, under the ADR-002 protocol.
   - Record in `docs/evidence/s12/ledger-single-node.csv`: posting p95/p99, lock waits on the platform fee account (from `pg_locks`/`pg_stat_activity` wait events, or `log_lock_waits`), and vacuum time on the lines table.
   - Before you measure, find where your S5 posting path actually serializes on an account. Is it a balance row being updated? A `FOR UPDATE` for the no-negative check? Something else? Write the prediction down.

2. **Fix the hot account in place first.**
   - Split the platform fee account into N *bucketed sub-accounts*. A posting chooses its bucket, and the platform balance is the sum of the buckets.
   - Choose the bucket **deterministically** from something stable in the posting (for example its key), not at random. Ask yourself why: think about a retried posting, and about `rebuild_balances` (S5) reproducing balances bit for bit.
   - Measure again with the same load (5 runs: this is the "before" half of ADR-040's final pair). Add the "after" row to the same CSV.

3. **ADR-040 decision point.** Write the ADR's Context and Numbers now, before Citus. At synthetic volume, single-node Postgres with buckets may well be enough. If it is, the ADR says so plainly. It then argues only from blast radius (the ledger's vacuum, lock waits and long reads no longer share `pg-atlaspay` with provider callbacks) and security scope (one `ledger_app` role, append-only, no other service's secrets), and it states the numbers that would **revert** the split. That label, "most debatable, revertible", is the honest part, and it is exactly what an interviewer wants to hear.

4. **The service skeleton.** `services/ledger` on grpc.aio + SQLAlchemy **Core** (not the ORM). The reasons belong in the ADR: SQL-first on Citus, statements whose plans you assert in tests, no identity map to hide what is sent. The interface, from the glossary:

   ```proto
   service LedgerService {
     rpc PostEntries(PostEntriesRequest) returns (PostEntriesResponse);
     rpc GetBalance(GetBalanceRequest) returns (GetBalanceResponse);
     rpc StreamStatement(StreamStatementRequest) returns (stream StatementLine);
   }
   ```

   Requirements for each method:
   - **`PostEntries`**: carries an `entry_key`, the owner and the lines (account, integer tiyin amount, direction). It is **idempotent by `entry_key`**: the same key with the same content returns the original result; the same key with different content is an error. Pick the gRPC status code and compare it with your S5 rule for "same key, different parameters". An unbalanced entry is `INVALID_ARGUMENT`, and insufficient funds is `FAILED_PRECONDITION`, as in the status mapping of P9 D151–D153. The ledger stays append-only for the runtime role (`ledger_app`; the owner role that runs migrations is never used at runtime), and corrections happen only by reversal (S5). The owner or a superuser could still disable a trigger; write down how you would detect that (an alert on trigger DDL, and the nightly trial balance and reconciliation).
   - **`GetBalance`**: a consistent read of one owner's balances.
   - **`StreamStatement`**: server-streaming, built on a generator over a server-side cursor like the S5 CSV statement. Memory stays flat, and the stream stops as soon as the client cancels.
   - Reuse the S10 interceptors (service token, OTel, logging). **If degrade item 24 was applied in S10**, that gRPC foundation does not exist yet: first create `libs/atlas-proto` with `buf lint`/`buf breaking` in CI, the interceptors, the status-code mapping, and the HTTP/2 load-balancing exercise below. Its hours move here from S10 with the degrade (about 2.5 h, [schedule-and-cuts.md](schedule-and-cuts.md) §7); they are not inside this block's 17.5 h. Every RPC honours the caller's deadline. When the deadline has passed, stop the database work too, rather than finishing an answer nobody is waiting for.
   - **Load balancing:** the S10 HTTP/2 trap applies to the ledger too. Use a headless Service, a `dns:///…` target with `round_robin` in the service config, and a server-side `max_connection_age`. Run at least 2 `ledger` replicas and record the per-pod spread in `docs/evidence/s12/ledger-grpc-spread.csv`. This is on the never-cut spine: if degrade item 24 removed the inventory extraction, this is where the fix is demonstrated.

5. **Citus, naive first.**
   - Start `citus-ledger` with 1 coordinator and 2 workers (enough on 16 GB too).
   - **Pain first: the S5 triggers.** Your S5 ledger tables carry the `DEFERRABLE INITIALLY DEFERRED` balance constraint trigger and the append-only triggers. Load the S5 schema as it is, predict what `create_distributed_table` will say about those tables, then run it on `journal_lines` and record the result in `docs/evidence/s12/citus-triggers.txt`. Read the Citus docs on triggers for your version, and find the setting `citus.enable_unsafe_triggers`: what does it change, where do triggers then fire, and why does Citus call it unsafe?
   - Once you have the result, decide and record in ADR-040 as a conscious choice: Atlas keeps the S5 triggers **per shard** under `citus.enable_unsafe_triggers`. That is correct only if every journal entry lives on one shard, which is why the single-shard rule in step 6 is an invariant and not a performance tweak. Keep a balance check in `PostEntries` as well, so a caller gets a clear `INVALID_ARGUMENT` instead of a trigger error, and keep append-only enforced by REVOKE on `ledger_app` too.
   - Distribute the lines table by `ledger_account_id`, the obvious choice.
   - Post an entry that credits a vendor's connected account and the platform fee account. Its lines now live on different shards, usually on different workers. Citus has to commit it with **two-phase commit** (*2PC*: every worker first prepares the transaction and promises it can commit, then the coordinator tells all of them to commit).
   - Measure p50/p95/p99 for single-shard vs cross-shard postings (3 runs), and look at the prepared transactions on the workers while the load runs. Record in `docs/evidence/s12/citus-2pc-cost.csv`.
   - Two questions to write answers to:
     - What happens to a prepared-but-not-committed transaction if the coordinator dies between the two phases? Who finishes it, and what do readers see meanwhile?
     - With the triggers running per shard, post one entry whose lines land on two shards. Predict what each shard's balance trigger sees, then check (§16, "Check your prediction").

6. **The redesign: distribute by `owner_account_id`.** The *owner* is the connected account whose money the entry moves (a vendor's `acct_…`), or a platform account.
   - **Why not `merchant_id`?** In AtlasPay, a merchant is the business calling the API, and `market` is merchant #1: almost all Season 1 traffic belongs to it. Sharding by merchant puts nearly every line on one shard, so you would have a distributed database with one hot node. Citus can isolate a big tenant onto its own shard, but it **cannot split one tenant** across shards (E3). Owners are many, and although they are Pareto-sized, even a whale vendor is small next to "all of `market`".
   - **The rule:** every line of an entry carries the same `owner_account_id`. So how do the platform's fees get posted? With **per-shard platform sub-accounts**: the platform side of a vendor's entry posts to a platform sub-account that lives with that vendor's owner key, and the platform's true balance is the sum of its sub-accounts, aggregated later. Ask yourself: for an entry that belongs only to the platform (for example a charge before its transfers exist), how do you choose its owner deterministically, so a retry lands on the same shard?
   - **Idempotency depends on it.** A UNIQUE constraint on a distributed table must include the distribution column, so idempotency is really `UNIQUE (owner_account_id, entry_key)`. That only works if a retry computes the same owner. Make the owner a pure function of the business event.
   - **Co-location and reference tables.** Distribute accounts, journal entries, journal lines and balance transactions by the same column and co-locate them, so joins and foreign keys stay on one node. Small, rarely changing lookup tables (for example currencies and account types) become reference tables, copied to every node.
   - Table sketch (requirements, not DDL): `journal_entries(owner_account_id, entry_id, entry_key, kind, occurred_at, …)`; `journal_lines(owner_account_id, entry_id, line_no, account_id, debit_tiyin, credit_tiyin)`; `accounts(owner_account_id, account_id, code, …)`. Every primary key and unique key starts with `owner_account_id`.
   - **The invariant test:** an EXPLAIN of every statement on the posting path must show a **router plan**, meaning a single task on one shard (look at the task count in the Citus custom scan node). Commit the plans in `docs/evidence/s12/router-plans.txt`.
   - Re-run the step-5 load (5 runs: the "after" half of ADR-040's final pair). Cross-shard postings must now be 0, and the per-shard balance trigger now sees every line of every entry. A bonus of single-shard entries: the no-negative-balance check for a debit is a local transaction on one worker again, exactly as in S5.

7. **The posting paths.**
   - **Credits, async:** `atlaspay` writes postings to its outbox. They travel through RabbitMQ to the queue `ledger.postings`. The `ledger` consumer is idempotent by `entry_key`, which doubles as its inbox. `ledger` publishes `ledger.entry_posted` when done.
   - **Debits, sync:** a payout or a refund must not overdraw a balance, so `atlaspay` makes a synchronous gRPC call with a deadline before it tells a provider or a vendor anything. On `DEADLINE_EXCEEDED` or `UNAVAILABLE`, the outcome is **unknown**, so retry with the **same** `entry_key`, a bounded number of times with jitter. Never mint a new key for a retry.
   - **Moving the data:** migrate the existing ledger rows from `atlaspay` (COPY, in owner order), switch `atlaspay` to the gRPC and outbox paths, then contract the old tables, as in S9. Keep the S9 exit criterion: the reconciliation diff is 0 before anything is dropped.
   - **Nightly reconciliation** between `atlaspay` and `ledger`: every posting `atlaspay` believes it made exists in `ledger` with the same amounts, and nothing else does. Drift feeds `recon_drift_rows` and alerts, as in S5.

8. **Rebalance under load.**
   - Start the posting load. Add a third worker (`citus_add_node`), then run `citus_rebalance_start()` and watch it with `citus_rebalance_status()`.
   - Record in `docs/evidence/s12/rebalance-under-load.csv`: posting p99 before, during and after; errors (target: **0 failed postings**); the rebalance duration; any short write pause at the end of a shard move (measure it rather than assume it); and the **trial balance before and after, which must be identical**.
   - If a table refuses to move, read the error carefully. Online shard moves rely on logical replication, which needs a replica identity.
   - *If you are behind:* degrade item 9 allows an idle rebalance instead (saves 1 h). Never apply it together with degrade item 4 (§4.2): one resharding run under load must always survive.

9. **REST vs gRPC, and restore.**
   - Put a thin REST endpoint in front of the same posting code, for the benchmark only, and compare p50/p95 for `PostEntries` under the ADR-002 protocol (3 runs each; P9 D151–D153 asked the same question with one RPC). Record in `docs/evidence/s12/ledger-rest-vs-grpc.csv`.
   - Extend the nightly restore-verify job to the ledger. A Citus cluster is several Postgres servers, so a restore is only consistent if every node is restored to the same point. Citus provides a cluster-wide named restore point, `citus_create_restore_point(name)`, run on the coordinator ([Citus docs](https://docs.citusdata.com/en/stable/develop/api_udf.html)) [verify: check the function against your Citus version]; every node is then recovered to that name (`recovery_target_name`). The job passes only if the restored cluster's trial balance equals the live one at that point.
   - *If you are behind:* degrade item 26, which is requirement-neutral, replaces this benchmark with a citation of the P9 D151–D153 result and the S10 REST vs gRPC numbers (ADR-037), and the restore-verify extension with a written, reviewed procedure (saves 1.5 h; [schedule-and-cuts.md](schedule-and-cuts.md) §7).

**Acceptance criteria:**
- Single-node numbers, before and after the bucket fix, are committed.
- `citus-triggers.txt` records the refusal and the choice; the balance and append-only triggers exist on every shard, and ADR-040 explains why `citus.enable_unsafe_triggers` is correct here only because entries are single-shard.
- The 2PC cost is measured for the naive key, and cross-shard postings are 0 after the redesign.
- The router-plan test is green and fails if a statement stops being single-shard (try one on a branch).
- A duplicate `PostEntries` returns the original result; a same-key, different-content call is refused.
- A rebalance under load has 0 failed postings and an identical trial balance.
- The per-pod spread across `ledger` replicas is even after scaling.
- Reconciliation reports 0 drift; a planted drift is flagged.

### 4.2 Mongo sharding [4.5 h, must]

**Why this exists.** In Citus you chose a key by reasoning about transactions. In Mongo the dominant failure is different: a shard key that sends all new writes to one shard, or piles one huge value into a chunk that can never be split (MongoDB flags a chunk it cannot split below the size limit as *jumbo*). The only way to believe these failure modes is to cause them. The *balancer* is the background process that moves chunks (ranges of shard-key values) between shards to even them out.

Suggested split of the 4.5 hours: the lab cluster 1.5; the unique-index refusal and the two bad keys (rows a and b) 1.25; the reshard under writes 1 (a reshard takes at least 5 minutes by design, plus the count check); `explain` and the ADR-041 Mongo section 0.75. Run rows a–c in the weekend block.

**What to build:**

1. **The lab cluster.** MongoDB 8.0, built from the `mongo` image (no official Compose recipe [U]), in the `atlas-labs` namespace or a Compose profile, ephemeral:
   - one `mongos` router;
   - a config server replica set using the 8.0 **config-shard** option, so it also holds data and you save RAM;
   - one or two more shard replica sets, as small as the lab allows (at least 2 shards in total, counting the config shard).
   Load a worldgen copy of `atlas_conversations.messages`, with the S7 indexes, including the unique index on `(conversation_id, client_msg_id)`. The production chat path stays on the S7 replica set.

2. **Pain first: the unique index meets the shard key.** Before row a, try to shard the copy on `{created_at}` with the S7 unique index still in place. Record exactly what MongoDB answers in `docs/evidence/s12/mongo-shard-keys.md`, then read the MongoDB manual page [Unique Indexes](https://www.mongodb.com/docs/manual/core/index-unique/) (the sharded-collections section) and explain the answer in one sentence. If the shard key and the unique index cannot live together, you have two ways forward for the lab:
   - shard on a key that has `conversation_id` as its prefix; or
   - drop the unique index in the lab copy only, and write down that dedup is now **per writer**: retryable writes, plus a writer that never resends the same `client_msg_id`, keep the "acknowledged vs present" count honest.
   Rows a and b need the second way, because neither key starts with `conversation_id`.

3. **Pain first, the shard keys.** Keep a writer inserting messages the whole time, with `w: "majority"` (the S7 invariant) and retryable writes, and count acknowledged writes. Before each row, write your prediction in the evidence file.

   | Step | Shard key | Observe | Record in `docs/evidence/s12/mongo-shard-keys.md` |
   |---|---|---|---|
   | a | `{created_at}` (ranged) | Inserts per second per shard over time; which chunk receives new inserts; what the balancer moves | Inserts per second per shard; chunk distribution over time |
   | b | `{vendor_id}` (on a fresh copy) | Data and chunks per shard; chunks that hold a single key value; any chunk flagged *jumbo*, and which vendors own it (worldgen is Pareto-shaped) | `getShardDistribution()` output; the jumbo chunks and which vendors own them |
   | c | `reshardCollection` from `{vendor_id}` to `{conversation_id: "hashed"}` **while the writer keeps writing** | Writer throughput and errors during the reshard; the length of the final write pause (predict it, then look up the documented bound for your patch version in [Reshard a Collection](https://www.mongodb.com/docs/v8.0/core/sharding-reshard-a-collection/)); spare disk used; duration (a reshard takes at least 5 minutes by design) | Your MongoDB patch version, duration, spare disk used, the write pause you measured, and **acknowledged writes vs documents present afterwards (must match)** |
   | d | `explain` two queries on the resharded collection: one conversation's messages (equality on `conversation_id` plus a `seq` range), and a vendor's inbox (by `vendor_id`) | Which shards each plan touches (the shards section of the explain output), and the latency of each | Both plans; latency of each at your data size |

   Open "Check your prediction" in §16 only after each row's prediction is committed.

4. **Questions to answer in ADR-041:**
   - Why does a hashed `conversation_id` fit chat? Consider cardinality, write distribution and the main access pattern: messages of one conversation in `seq` order.
   - The vendor inbox is now a broadcast query. Do you accept that at this scale, or maintain a per-vendor summary collection from `chat.message_sent` events?
   - The S7 dedup guarantee after resharding: a hashed shard key cannot back a unique compound index (the manual: "You cannot specify a unique constraint on a hashed index", and a unique index on a sharded collection needs the shard key as its prefix). What replaces it: dedup through retryable writes plus a `client_msg_id` check on read, or a non-hashed `{conversation_id: 1, …}` shard key that can carry the unique index? Choose, and say what each costs. And what does `_id` uniqueness mean when `_id` is not the shard key?
   - The S7 multi-document transaction (a message plus the conversation's counters): after sharding, is it now a distributed transaction? Is that the same cost story as Citus 2PC?

**Acceptance criteria:** the unique-index result and the four rows are recorded with your predictions and numbers; the reshard loses 0 acknowledged writes; ADR-041 has the Mongo section, including what replaces the unique index.

*If you are behind:* degrade item 4 is a partial degrade, because Mongo sharding and the shard-key choice are explicit requirements. Keep the 2-shard cluster, the unique-index step, **one** bad key (row a or row b), the reshard under writes from that key and the `explain` row; drop the other bad key (saves 0.5 h). Never apply it together with degrade item 9 (§4.1 step 8).

### 4.3 Fraud service [8 h, must]

**Why this exists.** A fraud model in the payment path is a dependency that can be slow, wrong or down. The engineering problem is not the model; S7 already trained it. The problem is making sure the payment path has a **bounded wait** and a **defined answer** when the model cannot give one. P9's extension called its model "a signal, not a decision". This block turns it into a decision, safely.

Suggested split of the 8 hours: ADR and service 1.5; the latency budget table and the p99 runs 2.5 (in-process vs gRPC scoring is ADR-042's final pair, so 2 × 5 runs of about 11 minutes, ≈ 1.8 h unattended, run through the ported split gate with scoring load and the replica memory recorded); client with deadline, breaker and fallback 1.5; versioning and the flag 0.5; chaos runs and panels 1.25; tests 0.75. The p99 runs and the chaos runs go in the weekend block.

**What to build:**

1. **ADR-042 first** (§8). It must be honest: the extraction is justified by model dependencies × replicas, a separate model deploy cadence and a fallback that becomes testable. The counter-argument is real: **in process is the lowest latency**.

2. **The service.** `atlas.fraud.v1.FraudService/Score` on grpc.aio.
   - The model is loaded **at startup** from the `atlas-models` bucket, never per request. Verify its sha256 and its feature-code version against the model card (S7) before serving. If they do not match, refuse to become ready: the caller's fallback handles it.
   - The readiness probe passes only after the model is loaded (S10: readiness vs liveness).
   - Features come from the **one feature function** shared by training and serving: `atlas_fraud_features`, the framework-free `libs/atlas-fraud-features` wheel from S7, which Django `payments`, the trainer and `atlaspay` already import. It reads the Timescale CAGGs `fraud_features.velocity_1h` and `velocity_24h`, plus Redis 1m/10m windows in `redis-state`. The `fraud.features` consumer (`payment_attempt.created`) moves from `atlaspay`, where it has run since S9, to `fraud`, which now keeps those windows fresh. Features must be point-in-time correct: computed only from events *before* the attempt being scored.
   - Target: **p99 ≤ 30 ms** inside the service, measured under the ADR-002 protocol (5 runs, the same runs as the in-process vs gRPC comparison). Build a latency budget table first (network, feature reads from Redis and from Timescale, model prediction, serialization) and measure each part. If one part eats the budget, fix that part. For example, ask whether the 1h/24h features need a Timescale query per request at all.

3. **The client in `atlaspay`.**
   - Every call has a **50 ms deadline** and sits behind a **breaker** (the S8/S9 breaker pattern). Should you retry inside a 50 ms budget? Write down your answer and why.
   - **Fallback: rules only** (the S7 velocity rules). Below amount X the payment **fails open** (it proceeds); at or above X it is **held for review**. X comes from the cost-based threshold analysis of S7. It is configuration, documented in ADR-042, not a constant in code.
   - Every decision records `model_version` (and the feature-code version, the score, whether the model or the fallback decided, and the latency). A fallback decision records a rules version in the same field, never a blank.
   - **Where does the score get used?** Payme and Click call AtlasPay **synchronously** (see [Stage 05 §4.0](stage-05-atlaspay-monolith.md#40-reference-how-payme-and-click-actually-talk-to-you), how Payme and Click talk to you). CheckPerformTransaction and CreateTransaction on Payme's side, Prepare on Click's side, are where AtlasPay approves or refuses. The provider is waiting for your answer, and Payme's own window is 12 hours (ADR-020). So what does "hold for review" mean for each provider: refuse now and let the buyer retry after review, or accept the money and hold fulfilment and the vendor transfer? Decide, and put the reasoning in ADR-042.

4. **Shadow → enforce through a flag.** Use the S8 hash-bucket flag mechanism, and ramp 10 → 50 → 100% while watching panels split by cohort. The assignment function is shared code: move it into `libs/atlas-common` if it is still inside `market`. The flag config for payment-path flags is `atlaspay`'s own. Why must `atlaspay` never read `market`'s flags table, and what would that do to the S9 neutrality argument (AtlasPay treats every merchant the same way)? What do you bucket on for a payment-path flag: the merchant, the buyer or the attempt? What happens to a retried attempt if its bucket is not stable?

5. **Chaos and panels.**

   Build the client first, then run these to check it. The "Check that" column is the design target, not a surprise: if any row fails, the client is wrong.

   | Do this | Check that | Record in |
   |---|---|---|
   | Put a slow fake `fraud` (200 ms per call) behind Toxiproxy, or a fake server, under payment load | `atlaspay` gives up at 50 ms, decides by the fallback, and the payment path's p99 grows by at most the deadline; then the breaker opens and stops even that wait | `docs/evidence/s12/fraud-slow.csv` |
   | **Kill `fraud` mid-load** (delete its pods or scale to 0) | **Payments continue.** Decisions switch to the fallback, holds appear only at or above X, and nothing errors | `docs/evidence/s12/fraud-down.csv`: payment success rate, `atlaspay` p99, fallback share, holds, time to breaker open and close |
   | Bring `fraud` back | Decisions return to the model; the breaker closes | same file |

   Grafana panels: the `fraud_score_seconds` latency histogram, score distribution by `model_version`, fallback share and holds. Put them beside the payment RED metrics (P9's lesson: a model's latency belongs on the same dashboard as the API's).

*If you are behind:* degrade item 23 keeps fraud in process in `atlaspay`, with the same fallback, versioning and latency test (saves 3.5 h: the service, the gRPC half of the comparison runs and the kill-the-pods run). The fallback itself is on the never-cut spine.

**Acceptance criteria:**
- p99 ≤ 30 ms inside `fraud` (ADR-002 protocol).
- With `fraud` slow or dead, `atlaspay` never waits more than 50 ms, and payments continue.
- Every decision in a load run has a `model_version`.
- The flag moves shadow → enforce without a deploy.
- ADR-042 and the model card are updated.

### 4.4 Closing [4 h, must]

**Why this exists.** Season 1's real output is not the code; it is your ability to explain it under pressure. This block turns 53 weeks of evidence into an interview-ready story.

Suggested split of the 4 hours: SD20 and its retro 1.25; mock #3 (preparation, the 60-minute run and its retro) 1.5; choosing the final 8 STAR stories 0.5; the README, diagram and demo refresh 0.75. The README and demo have been maintained since B2 and refreshed at B3, so this is an update, not a rewrite.

1. **SD20 — design AtlasMarket from scratch** ([system-design-problems.md](../../system-design-problems.md), SD20). Weekend block.
   - Rules: 45 minutes on a timer, a blank page, no notes, no repo. Use the bank's six-step skeleton: clarify scope, estimate scale, high-level design, data model, one deep dive, trade-offs.
   - Photograph or export the page and commit it as it is.
   - Only then open the repo and write `docs/sd20-retro.md`, one row per difference:

     | Area | Blank-page design | What Atlas does | Verdict (Atlas right / blank page right / depends) | Why | Evidence link |
     |---|---|---|---|---|---|

   - For each difference, decide honestly: was the real system right, or would you build it differently today? This retro is your centerpiece answer to "walk me through a system you built".
2. **Mock interview #3** (system design + backend deep dive). Format, rubric and retro template: [buffers-and-job-sprint.md](buffers-and-job-sprint.md#mock-interview-3-s12-w53).
3. **The final 8 STAR stories**, chosen from about 25 using the selection rules in [buffers-and-job-sprint.md](buffers-and-job-sprint.md#the-star-story-bank).
4. **Final README, diagrams and demo**: the architecture diagram at `v1.0`, the "what this proves" table updated with the S9–S12 evidence, and the demo re-cut if the storyline changed. Checklists: [buffers-and-job-sprint.md](buffers-and-job-sprint.md#readme-checklist).

### 4.5 Drills + SD4 [2 h, must]

- **SD4 Key-value store (whiteboard, W52).** The bank asks for a Dynamo-style store: partitioning by consistent hashing, N/W/R quorums, and conflict resolution after a partition (vector clocks or last-write-wins). The Atlas anchor is a *contrast*. Put the designs you built next to Dynamo's in `docs/sd/sd04-kv-store.md`:

  | | Partitioning | Replication and writes | Multi-key operations | Rebalancing |
  |---|---|---|---|---|
  | Dynamo-style (the SD4 answer) | ? | ? | ? | ? |
  | Citus ledger (this stage) | ? | ? | ? | ? |
  | Mongo sharded chat (this stage) | ? | ? | ? | ? |
  | Redis Cluster lab (S3) | ? | ? | ? | ? |
  | Webhook dispatch ring (S9) | ? | ? | ? | ? |

  Fill it from your own evidence, then answer: which of your systems is closest to Dynamo, and what would you gain and lose by making the ledger leaderless?
- **Drill hour:** one SQL problem on the Atlas schema (a good one: the multi-shard trial balance as a single query) or one DSA problem, plus this stage's interview questions out loud. If real interviews are happening, a real interview and its retro may replace the drill hour (a requirement-neutral degrade, [schedule-and-cuts.md](schedule-and-cuts.md) §7).

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| Every posting is idempotent and single-shard. | `UNIQUE (owner_account_id, entry_key)`; the owner is a pure function of the business event; every line of an entry carries the same `owner_account_id`; co-located tables. | Duplicate `PostEntries` returns the original result; the router-plan test on every posting statement; a property test that generated entries never span owners. |
| The trial balance is 0 across shards. | The S5 deferred balance trigger, running per shard under `citus.enable_unsafe_triggers` (correct only because every entry is single-shard), plus the balance check in `PostEntries` for a clear error; append-only through the per-shard triggers and REVOKE on `ledger_app`; nightly reconciliation. | The multi-shard trial-balance query returns 0 before and after the rebalance; the S5 Hypothesis state machine re-run against the `ledger` service. |
| Resharding loses no writes. | `w: "majority"` retryable writes (in the lab, with the unique index dropped, dedup rests on them and on a writer that never resends a `client_msg_id`); `reshardCollection`; Citus online shard moves. | The writer's acknowledged count equals the documents or lines present after the reshard and after the rebalance. |
| The payment path never waits more than 50 ms on fraud. | A 50 ms deadline, a breaker and the rules fallback in `atlaspay`. | A slow fake `fraud` (200 ms) → the decision arrives within budget with source = fallback; `fraud` killed → payments continue. |
| Every decision records the model version. | The decision record requires `model_version` (a rules version for fallback decisions). | Every decision row from a load run has it; the fallback rows carry the rules version. |

---

## 6. Tests to write

**Ledger:**
- `PostEntries`: balanced entry posts; unbalanced → `INVALID_ARGUMENT`; insufficient funds → `FAILED_PRECONDITION`; duplicate key → original result; same key, different content → refused.
- Router-plan assertions for every statement on the posting path and for `GetBalance`.
- Triggers per shard: the balance and append-only triggers exist on every shard of the distributed tables; an UPDATE or DELETE on `journal_lines` as `ledger_app` is refused.
- A property test (Hypothesis) that the owner function is deterministic and that no generated entry spans two owners.
- The S5 `RuleBasedStateMachine` re-run against the service: the trial balance stays 0 across any sequence.
- `StreamStatement`: flat memory over a long statement; stops on client cancel.
- Deadlines: a call whose deadline has already passed does no database work.
- Debit retries: a simulated `DEADLINE_EXCEEDED` followed by a retry with the same key posts exactly once.
- Reconciliation: a planted missing or extra posting shows up as drift.
- Rebalance under load: 0 failed postings, identical trial balance (a weekend-block test; keep the script in `bench/`).

**Mongo lab:** acknowledged vs present writes across `reshardCollection`; targeted vs scatter-gather plan assertions.

**Fraud:**
- Startup refuses to become ready with a wrong sha256 or feature-code version.
- Feature parity: the serving features equal the training features for the same point in time (S7 test, now across a process boundary).
- The latency-budget test: against a fake `fraud` that sleeps 200 ms, `atlaspay` returns a fallback decision within 50 ms plus a small, stated tolerance. This checks the invariant deterministically. The real p99 ≤ 30 ms is measured in `bench/`, not asserted on a noisy CI runner.
- Fraud-down chaos: with no `fraud` pods, payments succeed; amounts ≥ X are held.
- Every decision has a `model_version`.

---

## 7. CI changes

| Job | What it gates |
|---|---|
| `citus-ddl-migrations` | Starts an ephemeral Citus coordinator and workers with `citus.enable_unsafe_triggers` set, runs the ledger migrations up and down (distribution and reference-table calls first, then the triggers, so they are created on every shard), checks the triggers exist on the shards, and fails if any posting statement loses its router plan |
| `ledger-tests` (path filter `services/ledger/**`, `libs/atlas-proto/**`) | Unit and integration tests above; `buf lint`/`buf breaking` already cover the new protos (S10; if degrade item 24 was applied, you add them in §4.1 step 4) |
| `fraud-tests` | Startup verification, feature parity, the latency-budget test and the fraud-down chaos test |
| Nightly `restore-verify` (extended) | Restores `citus-ledger` to a consistent point and checks the trial balance |

The Mongo sharded lab and the rebalance under load stay out of per-PR CI. They are weekend-block runs whose evidence is committed.

---

## 8. ADRs and documents

### ADR-040 — Ledger service on Citus (extraction ADR: split-gate rules apply)

Label it in the title: **the most debatable split, revertible.**

**Questions it must answer:**
- What problem does the split solve, in numbers? How much did the in-place bucket fix already solve?
- If single-node Postgres suffices at synthetic volume, say so, and then argue only from blast radius and security scope.
- Why a separate service and not a module inside `atlaspay` on its own database? Why grpc.aio + SQLAlchemy Core?
- Why `owner_account_id`, and why not `ledger_account_id` or `merchant_id`?
- How are platform fees posted without cross-shard entries, and how is the platform's balance aggregated?
- Why run the S5 triggers per shard under `citus.enable_unsafe_triggers`, a setting Citus itself calls unsafe? State the condition that makes it correct here (every entry single-shard, proven by the router-plan test), what would make it wrong, and what the service-layer check and REVOKE add.
- Which postings are async (outbox → `ledger.postings`) and which are synchronous (debits), and why?
- How does reconciliation prove nothing was lost between `atlaspay` and `ledger`?
- **What would revert it?** The numbers (for example, if single-node Postgres with buckets handled a stated multiple of the projected load) and the steps (keep the ledger domain framework-free; move the data back; switch `atlaspay`'s port back).

**Numbers (ADR-002; the ported split gate with posting load; 5 runs for the final pair, single-node with buckets vs the redesigned cluster, and 3 runs for the intermediate configurations):** single-node posting p95 before and after buckets; lock waits on the platform account; vacuum time; single-shard vs cross-shard (2PC) posting p95/p99; rebalance p99, errors and duration; REST vs gRPC p50/p95.

**Counter-argument:** "Most companies keep the ledger inside payments" (E1). State it fairly. It is probably what you would do at a real company of this size.

### ADR-041 — Sharding

**Questions it must answer:**
- **Citus vs app-level routing.** Citus gives co-location, single-shard transactions and an online rebalancer. App-level routing would mean owning cross-shard queries and shard moves yourself (E3). When would app-level routing win anyway?
- **Mongo shard keys:** the unique-index conflict, the measured failure of `{created_at}` and `{vendor_id}`, why `{conversation_id: "hashed"}`, what replaces the unique index, the reshard cost, and the scatter-gather queries you accepted.
- **Redis Cluster** (S3 lab): hash slots, the hash tags `{ip}`, `{api_key}` and `{user}`, CROSSSLOT, and the failover table recorded against E10.
- **The webhook dispatch ring** (S9): app-level consistent hashing by merchant id with virtual nodes, and the keys moved from 3 → 4 dispatchers vs `hash % N` (P8 D131's lesson, applied).
- **What is not sharded, and why:** orders and payment intents (two access keys, lookups by provider id).
- A one-line resharding story for each target.

**Counter-argument:** "You did not need any of this at your volume." Agree where true, and point to the numbers that would make each one necessary.

### ADR-042 — Fraud serving (extraction ADR)

**Questions it must answer:**
- Why extract: model dependencies × replicas (image size and memory per `atlaspay` replica with and without the model, times the replica count under HPA), a separate model deploy cadence, and a fallback that becomes testable.
- The latency budget: p99 ≤ 30 ms in `fraud`, 50 ms deadline in `atlaspay`, and where the time goes.
- The fallback: which rules, the value of X and how it was derived, and what "hold for review" means for Payme and for Click given their synchronous protocols.
- Fail open below X and hold at or above it: why not fail closed for everything? Relate it to E10's fail-open vs fail-closed reasoning.
- The shadow → enforce ramp and the bucketing key.
- What each decision records (`model_version` and more), and how you would answer "why was this payment held?" a month later.

**Numbers (ADR-002; the ported split gate with scoring load; 5 runs for the in-process vs gRPC pair):** in-process vs gRPC scoring p99; `fraud` p99; the payment path's p99 with `fraud` healthy, slow and dead; fallback share; memory and image size per `atlaspay` replica before and after.

**Counter-argument:** "In process is the lowest latency" (and degrade item 23 is exactly that). Say at what latency or memory numbers you would move it back.

**Model card:** update the S7 card with a serving section: artifact sha256, feature-code version, features, threshold, X, fallback rules version, known limits, and the fact that labels are synthetic.

### Documents

- `docs/sd20-retro.md` and `docs/sd/sd04-kv-store.md`.
- The cutover and reconciliation runbook for the ledger move; a runbook for "fraud is down".
- The ADR-003 licences register updated for Citus.
- The README at `v1.0`.

---

## 9. System design session

| SD | Built or whiteboard | When | What to reuse from Atlas |
|---|---|---|---|
| SD4 Key-value store | Whiteboard | W52 | The Citus / Mongo / Redis Cluster / webhook-ring contrast table |
| **SD20 AtlasMarket from scratch** | **Closing** | W53 | Everything, but only *after* the 45 minutes on a blank page |

SD20 is the last exercise of the bank and of Season 1. Treat the retro as seriously as the design. An interviewer who hears "here is where my first design and my shipped system disagree, and here is which one was right" is hearing a senior habit.

---

## 10. Interview questions this stage lets you answer

1. What is your ledger shard key, and why not `merchant_id`?
2. What did 2PC cost?
3. How did you reshard without downtime?
4. Why do monotonic shard keys hurt?
5. How does scoring degrade when the model is down?
6. Why is the ledger split debatable?
7. Why did you fix the hot account in place before sharding? What did it buy?
8. How do you keep idempotency when the unique key must include the shard key?
9. What happens to a two-phase commit if the coordinator dies halfway?
10. What is a jumbo chunk, and how did you create one?
11. Hashed or ranged shard key for chat: what do you lose with hashed?
12. Your payment path has a 50 ms fraud budget. Where do the milliseconds go?
13. Why fail open below a threshold and hold above it, rather than one rule for all?
14. How do you know which model version made a decision a month ago?
15. Why is a fraud model a better fit for gRPC than REST here?
16. Design AtlasMarket from scratch. Where did your blank-page design disagree with what you built?

---

## 11. Common mistakes to watch for

1. **Sharding before fixing the hot spot in place.** Bucketed sub-accounts may remove the problem entirely, and then the split must be argued differently.
2. **Sharding by tenant when one tenant dominates.** `merchant_id` puts almost everything on one shard, and tenant isolation cannot split a tenant.
3. **Letting entries span shards "just for the platform fee line".** That puts 2PC on every payment.
4. **Idempotency that silently stops working.** The unique key includes the distribution column, and a retry computes a different owner.
5. **Computing the trial balance per shard only.** That misses errors between the platform's sub-accounts.
6. **A monotonic shard key** (`created_at`, an increasing id) → one hot shard.
7. **A low-cardinality or skewed shard key** (`vendor_id` with whale vendors) → jumbo chunks that cannot be split. The balancer skips them; moving one needs `forceJumbo` (which blocks writes) or the balancer setting for ranges that exceed the size limit, and either way the skew moves with the chunk instead of going away.
8. **Assuming resharding is free.** It needs disk, time and a short write pause at the end.
9. **Loading the model per request, or serving an artifact you did not verify.**
10. **A fraud call without a deadline or a breaker, or a fail-closed fallback on every amount.** Either one turns a model outage into a payments outage.

---

## 12. How real companies differ

- **Most companies keep the ledger inside the payments service** and scale it vertically, or by time partitioning, for far longer than Atlas does. Some very large fintechs run a dedicated ledger service, sometimes on a purpose-built ledger database. The learning version is still right: you now know what a distributed ledger costs, and you can say why you would *not* build it at a smaller company.
- **Managed distributed SQL is common** (for example the managed Citus offering on Azure, CockroachDB, Spanner or Vitess). You would rarely run a Citus cluster yourself in production. Running it once teaches what those products hide: distribution keys, co-location and 2PC.
- **MongoDB in production usually means a managed cluster**, with the shard key chosen before the data arrives. `reshardCollection` exists but is treated as a rare, planned operation.
- **Fraud systems combine rules, models and a manual review queue**, often with a vendor product in front and a feature store behind. Champion/challenger rollouts and drift monitoring are standard. Atlas keeps one model, one fallback and one flag, which is the core those systems are built around.
- **Feature pipelines are usually shared infrastructure** (a feature store), not a function inside the scoring service. The "one feature function for training and serving" rule is the same idea at small scale.

---

## 13. Deliberately not doing

| Item | Why | When it arrives |
|---|---|---|
| Kafka and CDC | Polling relays and outboxes cover Season 1 | Season 2, stage 2E ([season-2.md](season-2.md)) |
| MLflow, retraining, drift detection beyond a panel | Model lifecycle is a Season 2 topic | Season 2, stages 2C–2D |
| Patroni / automatic Postgres failover | Named only; failover of the Citus nodes stays a local lab concern | Named in ADR-040 |
| Cloud HA for Citus and Mongo | They run only locally; this is a stated limit of the setup ([coverage-matrix.md](coverage-matrix.md)) | Not in Season 1 |
| An app-level shard router for the ledger | Citus does it; ADR-041 says when you would build one | Not planned |
| Sharding orders and payment intents | Two access keys; lookups by provider id | Explained in ADR-041 |
| A public ledger API | The ledger is internal; merchants see balance transactions through AtlasPay REST | Not planned |

---

## 14. Stretch

Only when the must tier closes early.

| Item | Hours | Notes |
|---|---|---|
| Isolate a whale vendor with `isolate_tenant_to_new_shard` | 1 | Give the largest owner its own shard and measure its posting p95 and its neighbours' before and after. Note what it cannot do: it cannot split one tenant across shards. |
| Mongo balancer window and a forced jumbo move under writes | 1 | In the lab, restrict the balancer to a window and watch migrations queue up; then move one jumbo chunk from row b with `moveChunk`/`moveRange` and `forceJumbo` while the writer runs, and record the write block it causes and where the skew ends up. (The Redis slot reshard under load is the S3 stretch item; do it there, once.) |
| Blind incident drill: kill `ledger` | 1 | P9 D156's drill, on the new architecture. Someone else (or a script with a random delay) kills it; you follow the runbook without looking at the code, then write a blameless postmortem that includes what the runbook missed |

---

## 15. Definition of done

- [ ] `ledger-single-node.csv` with before and after the bucketed sub-accounts.
- [ ] `citus-triggers.txt` with the refusal and the choice; the triggers exist on every shard.
- [ ] `citus-2pc-cost.csv` for the naive key; 0 cross-shard postings after the redesign.
- [ ] `router-plans.txt` committed; the router-plan test is required in CI.
- [ ] `services/ledger` serves `PostEntries`, `GetBalance` and `StreamStatement`; `ledger-grpc-spread.csv` shows an even spread.
- [ ] Credits flow through `ledger.postings`; debits use the synchronous gRPC path with same-key retries; nightly reconciliation shows 0 drift and flags a planted one.
- [ ] **A rebalance under load with 0 failed postings** and an identical trial balance (`rebalance-under-load.csv`).
- [ ] `ledger-rest-vs-grpc.csv` committed; the restore-verify job covers the ledger.
- [ ] **The resharded chat:** `mongo-shard-keys.md` with the unique-index result and the four rows, and 0 acknowledged writes lost.
- [ ] **Fraud in the payment path with its fallback shown:** `fraud-slow.csv` and `fraud-down.csv`; payments continued; every decision has a `model_version`; shadow → enforce done through `atlaspay`'s own flag config.
- [ ] ADR-040 (labelled most debatable, revertible, with the `citus.enable_unsafe_triggers` choice), ADR-041 (with what replaces the Mongo unique index) and ADR-042 accepted; model card updated; ADR-003 register updated.
- [ ] `docs/sd/sd04-kv-store.md` written.
- [ ] **SD20 done on a blank page in 45 minutes; `docs/sd20-retro.md` written.**
- [ ] Mock interview #3 done and its retro written (see [buffers-and-job-sprint.md](buffers-and-job-sprint.md)).
- [ ] The final 8 STAR stories selected and polished.
- [ ] README, diagrams and demo updated to `v1.0`.
- [ ] Postmortem paragraph in `docs/postmortems/`: what you predicted for the 2PC cost, the triggers, the Mongo keys and the fraud-down run; what happened; what went to `docs/deferred.md`. Add a short Season 1 retrospective paragraph, including the season's actual/budget ratio from `docs/hours.csv` and where the estimates were most wrong (it is the input for planning Season 2).
- [ ] STAR story 1 in `docs/star/`: **the 2PC surprise**.
- [ ] STAR story 2 in `docs/star/`: **fraud-down with payments still flowing**.
- [ ] Tag `v1.0` created by you.

---

## 16. If you get stuck

**4.1 Ledger on Citus**
- The single-node numbers look fine. Good: that is a legitimate result. Did you measure at the peak shape worldgen produces, or at the average? Then write the ADR honestly.
- You cannot find the hot spot. Which row does every posting touch? Look at `pg_locks` while the load runs, not afterwards.
- `create_distributed_table` rejects your unique constraint. What does Citus require every unique constraint on a distributed table to contain?
- The triggers exist on the coordinator's table but not on the shards. Did you create them before or after distribution, and was `citus.enable_unsafe_triggers` set in the session that created them?
- A posting is still cross-shard after the redesign. Print the `owner_account_id` of each line of that entry. Which line disagrees, and which business event produced it?
- Retries create duplicate entries. Is the owner computed from the business event, or from something that changes between attempts?
- The rebalance errors out. Read the message about replica identity. Which of your tables has no primary key?
- Reread: [P8 D131](../python/08-docuvault.md) (the sharding decision record: key, reasoning, the scale at which it is justified); [P9 D151–D153](../python/09-payflow.md) (`PostJournalEntry`, the deadline, the status mapping, REST vs gRPC).

<details>
<summary>Check your prediction (open after the step 5 results are committed)</summary>

- **The triggers.** By default Citus refuses to distribute a table that has user triggers ("cannot distribute relation … because it has triggers"). With `citus.enable_unsafe_triggers` on, triggers are created on each shard and fire on the worker against that shard's rows only.
- **The cross-shard entry.** On the naive `ledger_account_id` key, each shard's deferred balance trigger sees only its own lines of the entry, so a valid entry can look unbalanced on every shard and be refused. That is the practical reason the single-shard rule is an invariant: on `owner_account_id`, every line of an entry is on one shard and the per-shard trigger sees the whole entry.

</details>

**4.2 Mongo sharding**
- You cannot see the hot shard. Are you looking at inserts per shard, or at data size? Which one shows a monotonic key's problem first?
- No jumbo chunk appears. Is your data skewed enough? How many messages does the biggest worldgen vendor have compared with the chunk size limit?
- `reshardCollection` fails straight away. Check the prerequisites in the docs: disk space, and the indexes the new key needs.
- The acknowledged and present counts differ after the reshard. Did the writer resend a `client_msg_id` after a timeout while the unique index was gone? Were retryable writes on?
- Reread: E3 in the [README](README.md) and your S7 ADR-024.

<details>
<summary>Check your prediction (open after each row's prediction is committed)</summary>

- **Row a, `{created_at}`.** Every new message has the largest key so far, so every insert lands in the last chunk: one hot shard while the others idle. The balancer moves old chunks, but the hot spot stays where the newest range is.
- **Row b, `{vendor_id}`.** Whale vendors produce chunks that hold a single key value. Such a chunk cannot be split, grows past the size limit and is marked *jumbo*. The balancer skips it; it can be moved only with `forceJumbo` (which blocks writes) or the balancer setting for ranges that exceed the limit, and the skew moves with it. Data per shard stays skewed.
- **Row c, the reshard.** The collection is copied under the new key in the background while writes continue; writes are blocked only in the short final *critical section*, the moment MongoDB switches the collection to the new key. That block is bounded by the critical-section timeout: 2 s by default up to 8.0.12, 500 ms from 8.0.13 [verify: the 8.0 "Reshard a Collection" page for your patch version]. Acknowledged writes and documents present match.
- **Row d, `explain`.** One conversation's messages go to one shard (a targeted plan). A vendor's inbox goes to every shard (scatter-gather, merged by `mongos`).

</details>

**4.3 Fraud service**
- p99 is above 30 ms. Which row of your latency budget table is the biggest? Is the Timescale query in the hot path?
- `atlaspay` waits longer than 50 ms. Is the deadline set on the call itself, or only on something around it? Is anything retrying inside the budget?
- The breaker never opens. Does a deadline expiry count as a failure for your breaker?
- Held payments pile up during the chaos run. Is X set from the cost analysis, or did you leave a default?
- Reread: [P9 Wk26 ML extension](../python/09-payflow.md) (§21: "a signal, not a decision", the latency histogram, the drift signal); your S7 ADR-026 and model card.

**4.4 Closing**
- SD20 feels impossible in 45 minutes. Spend the first 5 minutes only on scope and numbers, and skip every detail that is not the one deep dive you choose.
- You cannot choose 8 STAR stories. Use the coverage table in [buffers-and-job-sprint.md](buffers-and-job-sprint.md#the-star-story-bank): each of the six behavioral categories needs at least one story, and at least one story must be about being wrong.

**4.5 SD4**
- The contrast table looks the same in every row. For each system, ask: who decides the order of two concurrent writes to the same key?
