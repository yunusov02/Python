# Season 2 — ML, Data Science, MLOps and Data Engineering on Atlas's own data

| | |
|---|---|
| **Length** | About 33 weeks, about 445 h (≈ 13.5 h/week, the same 12–15 h/week rhythm as Season 1). Re-estimated from the phase files in [section 4](#4-stage-map); before 2A starts, scale it by the actual/budget ratio your Season 1 hours log measured |
| **Starts from** | The `v1.0` tag at the end of [Stage 12](stage-12-data-at-scale-fraud.md) (W53): 9 production deployables plus provider-sim, running on the seeded world. Season 2 week 1 is the week after W53, or after the end week you wrote down at a Season 1 checkpoint if the date moved. Season 2 numbers its weeks 1–33 on their own, so its stage headings use those numbers, not W54 onward |
| **Stages** | 2A Warehouse + batch DE → 2B DS + statistics → 2C ML → 2D MLOps → 2E Streaming + CDC → 2F Electives + capstone |
| **Theory source** | The Track B phase files: `../../phase-7-llm-zoomcamp.md`, `../../phase-8-ai-devtools-zoomcamp.md`, `../../phase-9-ml-zoomcamp.md`, `../../phase-10-mlops-zoomcamp.md`, `../../phase-11-data-engineering-zoomcamp.md` (exact day ranges per stage below) |
| **Level of detail** | Stage level: goals, data, deliverables and the bar. Before each stage starts, write its block plan with hour brackets in the same form as a Season 1 stage file, estimated bottom-up and multiplied by your measured ratio. |

> **What Season 2 is really for.** Season 1 makes you a backend engineer who can prove every claim about correctness and scale. Season 2 takes the data that system produced and makes you able to reason about it: build a warehouse that reconciles to the ledger, analyse an experiment you ran yourself, train models on data with known ground truth, and operate those models the way you operate services. Everything runs on Atlas and its world generator, not on new toy datasets. The phase files supply the theory; their original projects (StockPilot forecaster, QuickServe churn, CarePoint no-show) are replaced by the Atlas deliverables in this file.

---

## 1. Why Season 2 runs on Atlas and not on fresh datasets

The Track B phase files were written around separate projects, each with its own small dataset. That teaches the technique, but it leaves out three things an employer cares about:

1. **The data has a history you understand.** You wrote the checkout, the ledger and the fraud rules. When a chart looks wrong you can tell whether it is a bug in the pipeline, a bug in the product, or a real effect. That is most of what data work is.
2. **The ground truth is known.** The world generator (`libs/atlas-worldgen`, started in [Stage 00](stage-00-bootstrap.md)) decides how customers behave, how fraud happens and what effect a checkout variant has. So you can check your analysis against the truth. On real data you never get that check, which is why learning on synthetic-but-known data first is the right order.
3. **The ML sits next to a real serving path.** The fraud model already runs behind a 50 ms deadline with a rules fallback ([Stage 12](stage-12-data-at-scale-fraud.md)). Season 2 deepens that model and puts a registry, retraining and drift monitoring around it. The skills transfer directly to a job where the model is one component of a payments system.

**How to use the phase files.** Read the cited days for theory and the mini exercises. Skip their project tasks: the Atlas deliverables below replace them. Never copy code from them; they are reading material, the same rule as the old Track A specs in Season 1.

---

## 2. Entry conditions: what Season 1 must have left behind

Season 2 depends on these Season 1 artifacts. Check each one before week 1.

| Needed | Built in | Used by | If it is missing |
|---|---|---|---|
| Worldgen `history` mode with 13 months of seasonal, cohort-structured history, and `traffic` mode for locust | [S0](stage-00-bootstrap.md), extended in [S1](stage-01-layered-monolith.md), [S2](stage-02-checkout-correctness.md), [S7](stage-07-polyglot-mongo-timescale.md), [S12](stage-12-data-at-scale-fraud.md) | Every stage | Close the gap first (see the data contract in §3); nothing else in Season 2 works without it |
| Streaming replica of `market` and read-only roles `<svc>_ro` | [S6](stage-06-ship-and-operate.md) | 2A extraction | Add a replica or at least a `<svc>_ro` role with a `statement_timeout` before extracting |
| Hash-bucket feature flags and prompt-flag cohorts | [S8](stage-08-ai-integration.md) | 2B A/B analysis, 2D shadow/canary | 2B cannot analyse an experiment that never ran; see the note on the checkout variant below |
| Timescale hypertables and CAGGs (`fraud_features.velocity_1m/1h/24h`, `analytics.vendor_sales_daily`) | [S7](stage-07-polyglot-mongo-timescale.md) | 2C fraud features, 2D drift, 2E comparison | If degrade item 6' was applied, `vendor_sales_daily` does not exist; the 2A marts cover vendor sales instead |
| Fraud v1 (a logistic regression; the one feature function in `libs/atlas-fraud-features`; point-in-time training set; artifact with sha256 and model card), ported into atlaspay in S9 with shadow scores on every attempt, and the served fraud path with `model_version` on every decision | [S7](stage-07-polyglot-mongo-timescale.md), [S9](stage-09-strangler-atlaspay-auth.md), [S12](stage-12-data-at-scale-fraud.md) | 2C, 2D | If degrade item 23 was applied, the model is in-process in atlaspay; the registry consumer in 2D is then atlaspay instead of `fraud` |
| Product embeddings in the market DB (`catalog_product_embedding`) | [S8](stage-08-ai-integration.md) semantic product search | 2C kNN recommendations | If degrade item 13 was applied, generate the embeddings in 2C as a small batch job before the kNN work |
| Outbox with `trace_context`, quorum queues, `atlas.events` | [S4](stage-04-async-events-boundaries.md) | 2E CDC comparison | — |
| Ledger on Citus with 50M lines (20M on a 16 GB laptop) | [S12](stage-12-data-at-scale-fraud.md) | 2A `fct_ledger`, 2E Spark | If degrade item 9 or the 16 GB tactics were used, 20M lines is fine |
| Buckets `atlas-models` and `atlas-evals` in the S3-compatible store (Garage) | [S7](stage-07-polyglot-mongo-timescale.md), [S8](stage-08-ai-integration.md) | 2C, 2D | — |
| Cart-abandonment data | Worldgen history only ([S2](stage-02-checkout-correctness.md) history mode) | 2B funnel analysis | Nothing to fix: from [S3](stage-03-redis-auth-bot.md) carts are Redis hashes with a sliding TTL and emit no event, so the running system leaves no abandonment record by design (see §3.3) |

**The checkout-variant cohort.** 2B analyses "the S8 prompt-flag and checkout cohorts". The checkout-variant A/B is an S8 *stretch* item ([Stage 08 §14](stage-08-ai-integration.md#14-stretch)). If you skipped it, 2B still has the prompt-flag experiment; for the checkout analysis, add a checkout-variant cohort to the world spec (the generator assigns the arm and applies a known effect) and analyse that instead. Record which of the two you did.

**The prompt-flag experiment is a ramp, not a clean A/B.** S8 releases a prompt through 10 → 50 → 100%. Allocation changes while the metrics drift, and the 100% phase has no control, so pooling all phases mixes time with arm. 2B therefore compares arms only where both ran at the same time (stratified by ramp phase), and uses a **fixed-allocation window** from the world spec (a 50/50 split held for a set number of weeks, §3.4) as its primary prompt experiment.

---

## 3. The worldgen data contract

Season 2 is only as good as the data the world generator produces. This section is the contract between `libs/atlas-worldgen` (a Season 1 deliverable) and every Season 2 stage. Treat it like an API: version it, test it, and do not change it silently.

### 3.1 Principles

1. **One generator, two modes.** `history` mode writes COPY-ready files for bulk loading months of data. `traffic` mode drives the running system through locust with the same distributions. Both read the same world-spec YAML.
2. **Deterministic.** The same generator version, seed and world spec must produce identical output. A test regenerates a small world twice and compares content hashes.
3. **Provenance on everything.** Every generated dataset carries the generator version, the seed, a hash of the world spec and the git SHA. This is the same rule ADR-002 applies to benchmark results in Season 1. A manifest file committed next to each generated dataset is enough.
4. **Consistent with the product's invariants.** History is not random rows. It must look like it came out of the real system: balanced ledger, no negative stock, one order per idempotency key. If history violates an invariant the product enforces, every analysis built on it is wrong.
5. **Ground truth is kept apart.** Labels and true effects live in a separate artifact (for example in the `atlas-evals` bucket), never in the tables an analyst queries. You look at the truth only after you have written down your answer.
6. **Synthetic and declared so.** Every model card and readout states that the data and labels are synthetic, so metrics say nothing about real-world fraud rates or demand.

### 3.2 Calendar and time

| Rule | Why |
|---|---|
| At least **13 months** of history | 2B needs a full year plus one month to see annual seasonality and compare the same month year over year; it also matches the 13-month retention of Timescale aggregates set in S7 |
| All timestamps are `timestamptz` in UTC | The Season 1 invariant from S1; the warehouse inherits it |
| Business days follow **Asia/Tashkent** (fixed UTC+5, no DST) | Vendor revenue "per day" means a Tashkent day; its boundary is 19:00 UTC, the same boundary the S4 Beat test checks |
| Daily cycle, weekly cycle and named annual peaks are declared in the world spec | So seasonality is a parameter you can recover in 2B, not an accident |
| A scheduled **regime change** in a late month (for example a new fraud pattern, or a shift in provider mix) | 2D needs drift to detect; you should know exactly when it starts |

Note on Timescale retention: S7 keeps 90 days of raw hypertable data and 13 months of aggregates. So raw fraud events older than 90 days are not in `tsdb` after a history load. Training sets that reach further back must be rebuilt from the systems of record (or the 2A warehouse) through the **same feature function**. That is one more reason the "one feature function for training and serving" rule from S7 matters.

### 3.3 Entities, owners and volumes

| Entity | Owner (store) | Volume target | Season 2 use |
|---|---|---|---|
| Users (customers, vendor staff, ops) with signup-month cohorts; synthetic +998 phones and emails | market `identity` / auth | Set in the world spec | Cohorts (2B), recommendations (2C), erasure handling (2A) |
| Vendors, Pareto-sized, with onboarding-month cohorts | market `vendors` | Pareto (S1) | Vendor analytics (2A, 2B) |
| Categories, products, offers with per-category JSONB attributes | market `catalog` | 1M products (S1) | Recommendations, forecasting |
| Carts, including abandoned carts | **Worldgen history only.** From S3 carts live in Redis with a sliding TTL and emit no event, so traffic-mode runs leave no abandonment record; history mode writes cart sessions and their checkout outcome directly | Abandonment rate in the world spec (S2) | Funnel analysis (2B), labelled "synthetic history only". Acceptable because the rate and its drivers are known ground truth; a real shop would emit a cart event for this |
| Orders, `order_vendor_groups`, order items with price snapshots, promo uses | market `ordering`, `promotions` | Enough for 20M order lines (the S7 GROUP BY target) | `fct_orders`, forecasting, co-purchase |
| `stock_levels` and `stock_movements` | market `inventory` or the `inventory` DB (S10) | Every stock change has a movement | Censored-demand handling in 2C |
| Reviews (verified purchase) | market `reviews` | Set in the world spec | EDA, recommendations |
| Payment intents and attempts per provider (Payme, Click), refunds, transfers, payouts | atlaspay DB | 20M attempts (the S7 velocity-rule target) | `fct_payments`, fraud |
| Journal entries and lines, balance transactions | `citus-ledger` | 50M lines (20M on 16 GB) | `fct_ledger`, Spark (2E) |
| Provider events, including a low rate of the 12 S5 failure scenarios | atlaspay `provider_events` | Rates in the world spec | Reconciliation checks, EDA of failure modes |
| Flag assignments (hash buckets) and the prompt version of every assistant call | market `flags`, ai `usage_ledger` | Every exposed user | 2B A/B, 2D canary |
| Fraud patterns: card-testing bursts, account takeover, amount spikes | Generated behaviour plus labels in the truth artifact | Rates in the world spec | 2C, 2D |
| `user.erased` events for a small share of users | auth events | Set in the world spec | 2A must honour erasure |

### 3.4 Behavioural structure (the "physics" of the world)

These are the effects the generator must build in, so that Season 2 has something real to find:

1. **Vendor concentration.** A few vendors carry most revenue (Pareto). One platform account dominates the ledger, which is the hot account S12 fixes and the data skew Spark hits in 2E.
2. **Cohort behaviour.** Users and vendors decay or grow by cohort. Retention curves should differ between cohorts in a way you can explain.
3. **Seasonality and promotions.** Weekly and daily cycles in Tashkent time, annual peaks, and promotion effects on demand.
4. **Stockouts that censor demand.** When stock hits zero, observed sales stop even though demand did not. The generator records true demand in the truth artifact; the forecaster only sees sales and stock movements, and must handle the censoring.
5. **Co-purchase structure.** Category affinities (things bought together), so a co-purchase recommender has signal to find and a popularity baseline to beat.
6. **Payment mix and failures.** A Payme/Click mix, a low rate of each S5 failure scenario (duplicate Create, timeout, -5017 and so on), refunds and partial refunds.
7. **Fraud with label delay.** Fraud labels become known only some days after the attempt. Recent data therefore looks cleaner than it is. The delay is a world-spec parameter.
8. **Experiments with known effects.** Flag arms are assigned by the same hash-bucket rule the product uses (S8). The true effect of each arm is written to the truth artifact. The world spec also holds a **fixed-allocation window**: the prompt flag stays at 50/50 for a set number of weeks, so 2B has one experiment whose allocation never changes.
9. **Drift.** The scheduled regime change from §3.2.

### 3.5 Invariants the generated history must satisfy

Load a small generated world and run the Season 1 invariant checks against it. The `sql-invariants` CI job from [Stage 05](stage-05-atlaspay-monolith.md#7-ci-changes) is the natural place. Every one must pass:

| Invariant | Check |
|---|---|
| Trial balance is 0 | The ledger reconciliation query from S5, and across shards from S12 |
| Stock never below zero, and changes only through `stock_movements` | Replay movements; compare with `stock_levels` |
| One idempotency key means one order | `UNIQUE` holds; no duplicate orders per key |
| Σ transfers + fees = the charge; refunds ≤ captured | The S5 split-math properties, run as SQL over the history |
| Money is integer tiyin everywhere | No float or numeric-with-fraction columns in money paths |
| Every event has a UUIDv7 `event_id` and the envelope fields of the glossary | Schema check on the generated outbox rows |
| No cross-module foreign keys (allow-list: `identity_user`) | The S4 `pg_constraint` test |
| Projections that were bulk-loaded match a rebuild from their source | The S7 CAGG-vs-raw test; the S4 projection rebuild |

History mode may bulk-load projections (Timescale, the vendor order view) directly instead of pushing 20M rows through consumers. That is fine for speed, as long as each projection loaded that way passes the same rebuild-equivalence test as one fed by consumers.

### 3.6 Versioning

- A change that alters distributions, adds entities or changes a column is a **new generator version**. Record it in the manifest.
- Season 2 **pins** one generator version and one seed per stage. A readout that does not name them cannot be reproduced and does not count as evidence.
- If you must regenerate mid-season (a bug in the generator), rerun the analyses that depend on it and say so in the readout.

### 3.7 The analytics-faults switch (dirty data)

Principle 4 keeps the systems of record clean, because the product's invariants must hold. Real analytics data is not clean, though, and most data work is finding out how it is dirty. So the world spec has an **analytics-faults** switch that affects **only the warehouse extract**, never the systems of record:

- duplicated events (the same `event_id` twice);
- late-arriving rows (an extract that sees a row days after its `updated_at`);
- timestamps mislabelled between UTC and Asia/Tashkent;
- a burst of nulls in one column for a few days.

The faults, their rates and their windows go into the truth artifact like every other effect. 2B starts by finding and quantifying them before any analysis.

---

## 4. Stage map

| Stage | Weeks | Estimated hours | Atlas data / system used | Phase-file days to read |
|---|---|---|---|---|
| [2A Warehouse + batch DE](#5-stage-2a--warehouse-and-batch-data-engineering-weeks-15) | 1–5 | ≈ 67 | market, atlaspay and ledger replicas → warehouse → dbt marts | phase-11 W56–58 (D331–D348), D365 |
| [2B DS + statistics](#6-stage-2b--data-science-and-statistics-weeks-69) | 6–9 | ≈ 54 | 13 months of history; S8 prompt-flag and checkout cohorts; vendor cohorts | phase-9 W42 (D247–D252), phase-7 D197 |
| [2C ML](#7-stage-2c--machine-learning-weeks-1017) | 10–17 | ≈ 108 | Fraud (S7/S12), demand per vendor SKU, recommendations on orders and S8 embeddings | phase-9 W43–49 (D253–D294) |
| [2D MLOps](#8-stage-2d--mlops-weeks-1825) | 18–25 | ≈ 108 | Fraud, forecast and recommendation models; Timescale features; Atlas flags | phase-10 W50–55 (D295–D330) |
| [2E Streaming + CDC](#9-stage-2e--streaming-and-cdc-weeks-2630) | 26–30 | ≈ 67 | Outbox via Debezium → Kafka; fraud features; ledger history | phase-11 W59–61 (D349–D366), plus CDC, which phase-11 left out |
| [2F Electives + capstone](#10-stage-2f--electives-and-capstone-weeks-3133) | 31–33 | ≈ 41 | The ai service, the repo itself | phase-7 D199–D209 (plus D195 for the judge), phase-8 D229–D240 |
| **Total** | **33** | **≈ 445** | | |

### 4.1 How the hours were estimated

The first Season 2 outline spread 320 h over 24 weeks in proportion to weeks. Season 1 showed that top-down numbers like that are too small, so this estimate starts from the phase files, which budget about 20 h per week (3.5 h weekdays plus a 2.5 h Saturday). From each stage's phase-file weeks it subtracts what Season 1 already taught, then adds the Atlas work the phase files do not have.

| Stage | Phase-file baseline | Minus: already covered in Season 1 | Plus: Atlas-only work | Estimate |
|---|---|---|---|---|
| 2A | phase-11 W56–W58 + D365 ≈ 64 h | Terraform and Docker basics (S6, S10): −6 | three sources instead of one, reconciliation to the ledger, erasure, three pain-first runs: +9 | ≈ 67 h |
| 2B | phase-9 W42 + phase-7 D197 ≈ 24 h | logistic-regression basics from the S7 ML ramp: −2 | four readouts (EDA, two A/B analyses with phase stratification, vendor cohorts), the dirty-data pass (§3.7, ≈ 3 h), the notebook toolchain: +32 | ≈ 54 h |
| 2C | phase-9 W43–W49 ≈ 140 h | W44 basics (S7 ramp): −8; W46 neural networks, read for theory only: −12; W47 cluster setup (kind exists since S10): −6; W49 CI basics: −6 | three Atlas models replace the three phase-file projects: ±0 | ≈ 108 h |
| 2D | phase-10 W50–W55 ≈ 120 h | model serving with a fallback (S12): −8; Terraform layout (S6): −4 | Atlas flags and Timescale features replace the phase-file equivalents: ±0 | ≈ 108 h |
| 2E | phase-11 W59–W61 ≈ 60 h | W61 integrates three separate projects; Atlas closes one: −8 | Debezium CDC and its measured comparison with the S4 relay, which phase-11 left out: +15 | ≈ 67 h |
| 2F | phase-7 D195, D199–D209 and phase-8 D229–D240 ≈ 85 h if you did all of it | caching, guardrails and hardening already built in S8: −14 | you choose two or three electives, not all five: −30 | ≈ 41 h |

**Result: about 33 weeks and about 445 h at 13.5 h/week** (about 37 weeks at the 12 h/week floor). Treat it the way Season 1 treats its budget:

- **Re-scale before 2A.** Multiply every stage by the actual/budget ratio your Season 1 hours log measured. The phase-file baseline is itself an estimate for a learner who had not built Atlas; your own ratio is better evidence.
- **Checkpoint after 2C** (end of week 17), with the Season 1 procedure ([schedule-and-cuts §5](schedule-and-cuts.md#5-checkpoints)): more than one week behind means dropping the electives in 2F first, then shrinking the stage you are in.
- **Interview hours come first.** If you are interviewing while Season 2 runs, those hours come out of Season 2, and its end date moves; never the other way round.
- When you plan a stage, keep the Season 1 rule: the must tier fits the 12 h/week floor, stretch only after must closes.

**Stage close** follows the Season 1 convention: a git tag, a postmortem paragraph, 2 STAR stories in `docs/star/`, and evidence committed under `docs/evidence/`. Proposal for Season 2 code folders: add a data folder (Airflow, dbt, Spark) and an ML folder (training, flows) at the top level of `atlas/`, and record the names in the [glossary](glossary.md) when you create them.

---

## 5. Stage 2A — Warehouse and batch data engineering (weeks 1–5)

| | |
|---|---|
| Phase-file days | phase-11 W56 (D331–D336: Terraform and warehouse provisioning), W57 (D337–D342: Airflow, watermark extraction, MERGE, backfills), W58 (D343–D348: partitioning, query cost, dbt layering and tests), and D365 (the AtlasMarket vendor-analytics extension) |
| Atlas systems | Replicas of `market`, `atlaspay` and `ledger`, read with the `<svc>_ro` roles; Terraform from [S6](stage-06-ship-and-operate.md); Grafana from S6 |
| Warehouse | BigQuery, or DuckDB/ClickHouse locally if you want no cloud dependency |

**Goal.** A warehouse that can answer cross-service questions (revenue per vendor, payment success by provider, ledger movements per account) without touching production primaries, and that provably agrees with the ledger.

**Why this stage comes first.** Every later stage needs one place where orders, payments and ledger lines can be joined. In Season 1 that join is forbidden on purpose (market never reads the atlaspay DB). The warehouse is the one sanctioned place where it happens, read-only and after the fact.

### What to build

1. **Provisioning.** Terraform for the warehouse datasets (raw, staging, marts) and a least-privilege service account, reusing the S6 Terraform layout and remote state (phase-11 D331–D336).
2. **Extraction DAGs in Airflow.** One DAG per source: market, atlaspay, ledger. Incremental extraction by an `updated_at` watermark (D338), landing into raw, then idempotent `MERGE` into staging (D340). Backfill support for any date range (D341). Extraction is paced (bounded batch size, a `statement_timeout`) so it cannot hurt the OLTP side.
3. **dbt project** with the staging → intermediate → marts layering (D345–D347). Required marts: `fct_orders`, `fct_payments`, `fct_ledger`, `dim_vendor`, `fct_vendor_revenue`.
4. **Tests.** `unique`, `not_null`, `relationships` and `accepted_values` on the keys and statuses, plus singular tests for the business rules below.
5. **The reconciliation test against the ledger.** Σ debits = Σ credits in `fct_ledger` (the trial balance is 0), and vendor revenue in the marts reconciles to the transfers and fees the ledger recorded. From D365: summed vendor revenue equals the `fct_orders` total, and a vendor with zero orders appears as `0`, not as a missing row.
6. **Erasure.** When `user.erased` arrives, the warehouse must not keep or resurrect the erased user's personal data. Decide how (drop or null the PII columns in staging and downstream; the ledger holds only pseudonymous ids since S9) and write a test.
7. **One dashboard panel** on the marts in Grafana (the S6 stack), for example vendor revenue per Tashkent day.
8. **Docs.** `dbt docs` lineage graph, a short architecture note, and a decision note: "Airflow for data pipelines, Celery Beat for product jobs — why both".

### Pain-first exercises

1. **The watermark gap.** Before adding any overlap logic, open two psql sessions against the source. In session 1, start a transaction that updates an order and hold it open. In session 2, run the extraction and let it advance the watermark past that row's `updated_at`. Now commit session 1. Run the next extraction.
   - *Observe:* the committed update is never extracted, because its `updated_at` is older than the watermark.
   - *Record* in `docs/evidence/` (a 2A folder): the timeline, the missed row, and the fix you chose (an overlap window plus idempotent `MERGE`, or a watermark that trails `now()` by the longest allowed transaction). Note that 2E's CDC removes this class of bug entirely.
2. **The query the replica cancels.** Run a long extraction against the market replica while S6-style write load runs on the primary.
   - *Observe:* `canceling statement due to conflict with recovery` (the recovery conflict S6 noted).
   - *Record* the setting you changed (`max_standby_streaming_delay`, `hot_standby_feedback`, or smaller batches) and its cost for the primary.
3. **The rerun that duplicates.** Implement the load as a plain INSERT first, run the same DAG interval twice, and count duplicates. Then switch to `MERGE` and show the count is stable (D340).

### What makes it senior

- Reruns and backfills never duplicate rows, and you can prove it with a test.
- The warehouse **reconciles to the ledger**, not just to itself. Totals that only agree with other warehouse tables prove nothing.
- Money stays integer tiyin all the way to the mart; conversion to soum happens only at display.
- Extraction is paced and reads replicas through read-only roles; you can say what load it adds.
- Partitioning and clustering are chosen from the actual query shapes, with bytes-scanned numbers (D343–D344).

### Interview questions this stage lets you answer

- How does a timestamp watermark lose rows, and how did you prove it?
- Why `MERGE` and not INSERT for an incremental load?
- How do you know the warehouse agrees with the ledger?
- Airflow or Celery Beat: what does each give you?
- How do you handle a GDPR-style erasure in a warehouse fed from append-only sources?

### Not doing

- CDC (that is 2E, and the comparison is the point).
- A lakehouse table format (Iceberg/Delta): not needed at this size; phase-11 also leaves it out.
- Real-time dashboards (2E).

### If you get stuck

- The watermark gap will not reproduce? Ask yourself which timestamp the row gets: the statement time or the commit time. Reread phase-11 D338.
- Reconciliation off by a few tiyin? Look for a float or a rounding step anywhere between the source and the mart. The S5 float-drift lesson (and [LedgerBase D91–D93](../python/06-ledgerbase.md)) is the same bug in a new place.

---

## 6. Stage 2B — Data science and statistics (weeks 6–9)

| | |
|---|---|
| Phase-file days | phase-9 W42 (D247–D252: linear algebra, gradients, gradient descent from scratch, MLE, the Bayesian view of Ridge) and phase-7 D197 (A/B testing statistics: null hypothesis, p-values, confidence intervals) |
| Atlas data | 13 months of history in the 2A warehouse, extracted with the analytics-faults switch on (§3.7); the S8 prompt-flag cohorts and the world-spec fixed-allocation window; the checkout cohorts (see §2); vendor cohorts |
| Toolchain | pandas or Polars for the frames, Jupyter notebooks rendered into each readout (so the readout shows the code that produced every number), plotly or matplotlib for figures, scipy.stats and statsmodels for tests and intervals |

**Goal.** Answer questions about Atlas with statistics you can defend: what the data looks like, whether an experiment worked, and how vendor cohorts behave. Then derive the math under `.fit()` once, by hand, so later models are not black boxes.

### What to build

1. **EDA readout** on 13 months of history: order-value distribution (expect a heavy tail), daily/weekly/annual seasonality, provider mix and failure rates, cart abandonment (worldgen history only, §3.3), vendor concentration (a Lorenz curve or Gini of vendor revenue). Every figure names the query and the worldgen version and seed that produced it. The readout opens with a **data-quality section**: the faults you found (§3.7), how many rows each touched, and how you handled them.
2. **A/B readout for the S8 prompt experiment.** The primary experiment is the fixed-allocation window from the world spec. The 10 → 50 → 100% rollout is analysed only where both arms ran at the same time: stratified by ramp phase, with the 100% phase excluded because it has no control. Required parts, in this order:
   1. An analysis plan written *before* looking at results: primary metric, guardrail metrics, unit of randomization, minimum detectable effect, sample size.
   2. A **sample-ratio mismatch** check (is the split really what the flag says?), run **per ramp phase**; one pooled check across phases is meaningless when the intended split changes.
   3. The effect with a **confidence interval computed by hand** (difference in proportions with the normal approximation), cross-checked with a bootstrap.
   4. **Power**: was the experiment large enough to detect the effect you cared about?
   5. **Peeking**: simulate checking the p-value every day and stopping at the first "significant" result. Count how often that declares a winner when the true effect is zero.
3. **Checkout-cohort readout**, same structure, on the checkout-variant cohort. Afterwards, open the truth artifact and compare your interval with the true effect.
4. **Vendor cohorts**: revenue retention by onboarding month; check the result per category too, and look for Simpson's paradox (a trend that reverses when you split the data).
5. **ML math notes** (phase-9 W42): derive the MSE gradient, implement gradient descent in NumPy, derive logistic loss as a maximum-likelihood estimate, and show Ridge as the MAP estimate under a Gaussian prior. Then apply it to Atlas: fit the S7 fraud logistic regression with your own gradient descent and match scikit-learn's coefficients within a tolerance you state.

### Pain-first exercises

1. **The dirty extract.** Before any analysis, run a naive daily-revenue query on the faulted extract and compare it with the ledger-reconciled 2A mart.
   - *Observe:* where the totals disagree, and on which days.
   - *Record* each fault you found, how you detected it (duplicate `event_id`s, rows arriving after their day closed, a timezone offset that shifts the day boundary, a null burst), how many rows it touched, and your fix. Then compare your list with the faults in the truth artifact. (About 3 h.)
2. **The unit mismatch.** The prompt flag buckets *users*, but a naive analysis treats every *request* as independent. Compute the interval both ways.
   - *Observe:* the per-request interval is much narrower, because heavy users contribute many correlated requests.
   - *Record* both intervals and which one you trust, with the reason.
3. **The peeking false positive.** Run the daily-peek simulation on an A/A split (both arms identical).
   - *Observe:* far more than 5% of runs declare a winner.
   - *Record* the rate you measured and the stopping rule you adopt.
4. **The planted SRM.** Ask a friend (or use a world-spec switch) to exclude one class of users from one arm only, for example bot-originated sessions. Run your SRM check blind and see whether it catches it.
5. **The pooled ramp.** Estimate the prompt effect by pooling all ramp phases, then stratified by phase, then on the fixed-allocation window. Predict first which of the three will be furthest from the truth, and write the prediction down.
   - *Observe:* how far apart the three estimates are, and why allocation changing while the metric drifts matters.
   - *Record* the three estimates next to the true effect from the truth artifact, and which one you would have shipped a decision on.

### What makes it senior

- The analysis plan exists before the result. "B looked better" is not a result (phase-7 D197 says the same).
- You match the unit of analysis to the unit of randomization, and you compare arms only over periods when both ran at the same allocation.
- You check the data before you trust it: the faults are found and counted before the first chart.
- You report an interval and a power statement, not a bare p-value.
- You validated your method against known ground truth, which almost nobody can do on real data.

### Interview questions this stage lets you answer

- What is a sample-ratio mismatch, and what usually causes one?
- Why can't you stop an experiment the first day it looks significant?
- Your metric is per request but you randomize per user. What goes wrong?
- How would you size an experiment before running it?
- A feature was ramped 10 → 50 → 100%. Why can't you pool the whole ramp to estimate its effect?
- How do you find duplicated or late-arriving events in an analytics extract?
- Derive the gradient of MSE. What does L2 regularization mean in Bayesian terms?

### Not doing

- Bayesian A/B frameworks or sequential-testing libraries: name them, don't adopt them.
- Causal-inference methods beyond the randomized experiment (difference-in-differences and similar are interview vocabulary only).

### If you get stuck

- Your hand-computed interval disagrees with the bootstrap? Check the variance formula for a difference of two proportions, then check whether the units are independent. Reread phase-7 D197.
- Gradient descent does not converge? Plot the loss per step, then scale the features. Reread phase-9 D249.

---

## 7. Stage 2C — Machine learning (weeks 10–17)

| | |
|---|---|
| Phase-file days | phase-9 W43 (D253–D258: framing, splits, linear regression, Ridge), W44 (D259–D264: logistic regression, precision/recall, ROC, class imbalance), W45 (D265–D270: serving, trees, random forests, gradient boosting), W46 (D271–D276: neural networks, theory only here), W47 (D277–D282: serverless, Kubernetes, KServe), W48 (D283–D288: finalizing a forecaster), W49 (D289–D294: pipelines, CI, model cards) |
| Atlas data | Payment attempts and fraud labels; orders and stock movements per vendor SKU; order lines for co-purchase; the S8 product embeddings |

**Goal.** Three models, each compared against a baseline you could explain to a product manager: a deeper fraud model, a demand forecast per vendor SKU, and product recommendations. Plus one honest comparison of two ways to serve a model on Kubernetes.

### What to build

1. **Fraud deepening** (continuing S7 and S12; S7's must tier is a logistic regression, and its gradient-boosted model, precision@K and calibration were stretch):
   - A gradient-boosted challenger (HistGradientBoosting, D269) against the S7 logistic regression, unless you already built it as the S7 stretch item.
   - Imbalance: compare `class_weight` against undersampling (D263) on a time-based split.
   - Calibration: a reliability curve and a Brier score; calibrate if needed (this extends the S7 stretch item). A score that is going to be thresholded on cost must mean a probability.
   - Cost curves: expected cost across thresholds using the S7 cost model, plus a capacity constraint (ops can review only K holds a day, so precision@K matters).
   - Label delay: the training cutoff and the evaluation window respect the label-maturity delay from the world spec.
   - Champion/challenger: the new model against the one S12 serves, on the same frozen evaluation set.
2. **Demand forecast per vendor SKU:**
   - A **seasonal-naive baseline** first (same weekday last week). No model counts until it beats this.
   - Ridge with lag and rolling features (D253–D258), then a gradient-boosted regressor (D269), on a rolling-origin backtest.
   - A metric that survives zero demand (WAPE or MASE; explain why MAPE breaks).
   - **Censored demand:** mark days where stock was zero (from `stock_movements`) and decide how the model treats them.
   - The long tail: most SKUs of small vendors sell rarely. Decide whether to forecast them per SKU, per category, or not at all, and say why.
   - Output: a nightly forecast table that the vendor dashboard can read (a rebuildable projection, never a source of truth).
3. **Recommendations:**
   - A popularity baseline.
   - Co-purchase item-to-item from order lines, with a minimum support threshold.
   - Content kNN on the S8 product embeddings (pgvector in the market DB).
   - Offline evaluation on a time split: hit@k or recall@k on the next orders, plus catalog coverage.
   - Rules: never recommend an unpublished product or a product of a suspended vendor.
   - Serving: a precomputed table refreshed nightly, read by market under `/api/v1/*`. This is the pattern the old AtlasMarket spec proposed for its Week 28 AI/ML convergence extension (see [../python/10-atlasmarket.md](../python/10-atlasmarket.md)).
4. **Raw Kubernetes vs KServe** (D277–D282): deploy the forecast or recommendation scorer on the S10 kind cluster twice, once as a plain Deployment and Service, once as a KServe `InferenceService`. Compare manifests, cold start, autoscaling and what you have to operate. Write the decision, and say why the fraud path stays a grpc.aio service with a 30 ms p99 budget (an extra hop and a generic serving layer do not fit it).
5. **Model cards** for all three models: data (synthetic, generator version and seed), features, metrics against the baseline, known failure cases, the threshold and its cost reasoning.

### Pain-first exercises

1. **The random split that lies.** Train the fraud model on a random split first.
   - *Observe:* the metric is better than on the time-based split.
   - *Record* both numbers and the leak that explains the gap (future behaviour of the same card or user in the training set).
2. **The model that loses to naive.** Fit the first forecaster before building the baseline, then build the baseline.
   - *Observe:* for many SKUs the naive forecast wins or ties.
   - *Record* the share of SKUs where the model beats naive, and where you will use each.
3. **The stockout that looks like no demand.** Train the forecaster without the stockout flag, then with it, and compare errors on the days right after a restock.

### What makes it senior

- Every model has a baseline, and the baseline is reported first.
- Splits follow time; leakage is tested, not assumed away.
- The threshold is chosen from business cost and review capacity, not from 0.5 or from F1.
- Training and serving use the same feature code (the S7 rule), and a parity test proves it.
- The serving decision is argued from the latency budget, not from fashion.

### Interview questions this stage lets you answer

- Why PR-AUC and precision@K for fraud, not accuracy or ROC-AUC?
- How does label delay bias your evaluation?
- Why does MAPE fail on sparse demand, and what did you use?
- What is censored demand?
- How do you evaluate a recommender offline, and what does offline evaluation miss?
- When would you use KServe, and why not for fraud?

### Not doing

- Deep learning in production. W46 is read for theory; if you want an Atlas exercise, a small product-image category suggester over `atlas-media` is an elective outside the budget.
- Collaborative filtering with matrix factorization at scale: named, not built.
- A feature-store product (for example Feast): the one feature function plus Timescale is the Atlas answer at this size.

### If you get stuck

- Fraud metrics look too good? Look for a feature computed with data from after the attempt. Rerun the S7 leakage test.
- Forecasts are flat? Check that lag features are built from past rows only and that the rolling window does not include the target day. Reread phase-9 D256–D257.

---

## 8. Stage 2D — MLOps (weeks 18–25)

| | |
|---|---|
| Phase-file days | phase-10 W50 (D295–D300: MLflow tracking and registry), W51 (D301–D306: Prefect orchestration, retries, schedules), W52 (D307–D312: batch vs web vs streaming serving), W53 (D313–D318: drift, Evidently, testing ML code, CI model gates, Terraform for ML infra), W54 (D319–D324) and W55 (D325–D330): full productionization |
| Atlas systems | The `fraud` service (or atlaspay, if degrade item 23 was applied); the forecast and recommendation jobs; `fraud_features` CAGGs in `tsdb`; the S6 Prometheus/Grafana/Alertmanager stack; the S8 hash-bucket flags; the `atlas-models` bucket |

**Goal.** Operate the three models the way Season 1 operates services: versioned, retrained by a pipeline that can refuse bad data, monitored for drift, gated in CI, and rolled out through the same flags as any other change.

### What to build

1. **MLflow tracking and registry** for fraud, forecast and recommendations, with Postgres as the backend store and the S3-compatible store (Garage, bucket `atlas-models`) as the artifact store. Every run records the dataset (generator version and seed, warehouse snapshot), the feature-code version and the metrics against the baseline. The phase-10 file uses registry stages (Staging → Production); newer MLflow versions steer towards aliases instead [U: check the version you install].
2. **Prefect retraining flows** per model: extract from the warehouse → **validate** → build features with the one feature function → train → evaluate against the current Production model → register the candidate. Retries and schedules (D301–D306). The validation step fails the flow closed: schema, null rates, value ranges, row counts against the source, and label maturity (no labels younger than the delay).
3. **Drift monitoring**: Evidently reports on the Timescale velocity features and on the score distribution, exported as Prometheus metrics, with Alertmanager rules (the S6 stack). Prove the alert fires on the scheduled regime change from the world spec, and that it does not fire on an ordinary week.
4. **CI gate against Production** (D316): a PR that changes model code retrains on a small frozen dataset and fails if it regresses against the Production model beyond a stated tolerance. It is the S8 `ai-evals` idea applied to models; see [testing-and-ci.md](testing-and-ci.md).
5. **Shadow and canary through Atlas flags**: the challenger scores every attempt in shadow; then the hash-bucket flag from S8 moves a percentage of traffic to enforce the challenger (the S12 shadow → enforce flag); dashboards split by arm.
6. **Serving discipline**:
   - The model is loaded at startup, never per request (already true in S12).
   - Batch scoring and online serving always use the same registry version.
   - **Fail closed if the registry is unreachable**: the service does not become ready with an unknown or unversioned model. This is different from the payment path's behaviour when `fraud` is down, which stays as S12 defined it (rules only: fail open below amount X, hold for review at or above X). Write both rules next to each other so nobody confuses them.
7. **Runbook**: "fraud model drift alert fired" — what to check, when to roll back to the previous version, who decides.

### Pain-first exercises

1. **The silent bad retrain.** Break the input on purpose (for example a world-spec switch that nulls one feature for a week) and run the flow without the validation step.
   - *Observe:* a model trains, registers and looks fine on aggregate metrics.
   - *Record* what it would have done in production, then add validation and show the flow now refuses.
2. **The registry outage.** Stop the MLflow server and restart the fraud service.
   - *Observe* whether it starts with a cached artifact, an old version, or not at all.
   - *Record* the behaviour you want and prove it with a test.
3. **Drift you know is coming.** Before the regime-change month, write down which feature should drift first. Then check the report.

### What makes it senior

- Promotion is an explicit, audited step with the numbers attached, not "the latest run wins".
- A retraining pipeline can say no.
- Model rollouts use the same flags, dashboards and rollback discipline as code rollouts.
- You can explain the difference between "fail closed on an unknown model" and "fail open on a missing model service" in one minute.

### Interview questions this stage lets you answer

- How do you decide a new model may replace the current one?
- What does your retraining pipeline validate, and what happens when validation fails?
- How do you detect drift, and how do you avoid alert fatigue?
- Why must batch and online scoring use the same model version?
- What happens to payments if the model registry is down? And if the fraud service is down?

### Not doing

- Automatic promotion without a human decision.
- A managed ML platform: everything stays on the Season 1 infrastructure.
- Online learning.

### If you get stuck

- The CI gate is flaky? A gate on a random split or a changing dataset will be. Freeze the dataset and the seed, then set the tolerance from the run-to-run spread (the ADR-002 noise rule applies to models too).
- Drift fires every day? Check the reference window. Reread phase-10 D313–D314.

---

## 9. Stage 2E — Streaming and CDC (weeks 26–30)

| | |
|---|---|
| Phase-file days | phase-11 W59 (D349–D354: lakehouse layers, Spark DataFrames, aggregation, broadcast vs shuffle joins, Spark vs warehouse SQL), W60 (D355–D360: Kafka, ksqlDB, streaming into the warehouse, exactly-once vs at-least-once, a live dashboard), W61 (D361–D366: integration and wrap). Phase-11 deliberately skipped CDC via Debezium; this stage adds it. |
| Atlas systems | The market and atlaspay outbox tables from [S4](stage-04-async-events-boundaries.md); the S4 polling relay; the `fraud_features` CAGGs; the S12 ledger history; the 2A warehouse |

**Goal.** Replace the polling relay's job with log-based change data capture where it pays off, measure the difference, and add a streaming layer next to (not instead of) the batch warehouse.

### What to build

1. **Debezium on the outbox.** Kafka Connect with Debezium reading the market outbox through logical decoding, using the **outbox event router** to route events to topics by aggregate type, with the aggregate id as the message key (so events of one aggregate stay ordered). Kafka runs in KRaft mode in Compose.
2. **The comparison with the S4 relay**, under the same traffic (worldgen traffic mode, ADR-002 protocol): end-to-end lag p50/p95/p99, primary CPU and WAL volume, behaviour while the consumer side is down, and ordering per aggregate. The S4 relay claims rows with `SKIP LOCKED`; Debezium reads the WAL, so the outbox table no longer needs to be polled.
3. **An ADR** on where Kafka sits: a replayable log for analytics and ML consumers, while RabbitMQ keeps commands, Celery work queues and webhook dispatch. Revisit ADR-013 ("why not Kafka") with the numbers you now have; changing only what the numbers justify.
4. **Streaming into the warehouse**: a consumer that merges events into the warehouse idempotently, keyed on event id and type (D358), plus a live panel (D359).
5. **Streaming fraud features vs Timescale CAGGs**: ksqlDB windowed counts per card fingerprint, phone and IP (D356), compared with the S7 CAGGs on freshness, late-event handling, correctness against raw data, and what each costs to run.
6. **Spark over ledger history** (D349–D354): monthly balances per account over the 50M (or 20M) lines. The dominant platform account creates a skewed partition; find it in the Spark UI, then fix it (salting or a separate path). Finish with the Spark-vs-warehouse-SQL decision (D353): which of these jobs did not need Spark?
7. **Close the program** (D361–D366): run the full batch and streaming paths end to end, then write the retrospective. D365 (vendor analytics) was already done in 2A; here you only check it still reconciles with the streaming path added.

### Pain-first exercises

1. **The slot that fills the disk, again.** Stop Kafka Connect for an hour under write load.
   - *Observe:* the replication slot holds WAL and disk use climbs, exactly the S6 lesson.
   - *Record* the growth rate and confirm `max_slot_wal_keep_size` stops it; write down what you lose when it does (the connector must re-snapshot).
   - Run it on a small, dedicated volume, never on your laptop's main disk.
2. **The duplicate after a restart.** Kill the streaming consumer between processing and committing its offset.
   - *Observe:* the same event is processed twice.
   - *Record* how the idempotent merge makes the duplicate harmless (D358), and why "exactly once" in Kafka does not reach your warehouse on its own.
3. **The skewed stage.** Run the ledger aggregation without any skew handling and screenshot the one task that runs far longer than the others.

### What makes it senior

- You adopted CDC with a measured reason and kept RabbitMQ where it is still the right tool.
- You know what a replication slot costs and have a guard on it.
- Every streaming consumer is idempotent, and you can explain delivery semantics end to end, not just inside Kafka.
- You can say which batch job did not need Spark.

### Interview questions this stage lets you answer

- Polling outbox relay or log-based CDC: what did each cost in your system?
- What happens to Postgres when a CDC connector is down?
- How do you keep per-aggregate ordering in Kafka?
- Exactly-once: where does it hold and where does it stop?
- What is data skew in Spark and how did you find it?

### Not doing

- Moving every queue to Kafka.
- Schema-registry governance beyond one versioned schema per topic (named only).
- Flink or Spark Structured Streaming in production: ksqlDB and one consumer are enough to learn the concepts.

### If you get stuck

- Debezium sees no changes? Check `wal_level=logical`, the publication and the replication role. The S9 logical replication work used the same settings.
- Consumer lag keeps growing? Measure per-partition lag; one hot key (the platform account again) can pin one partition.

---

## 10. Stage 2F — Electives and capstone (weeks 31–33)

| | |
|---|---|
| Phase-file days | phase-7 D199–D209 (query rewriting D199, re-ranking D201, caching and guardrails D202, production hardening D205–D209) plus D195 for the LLM judge itself; phase-8 D229–D240 (AI PR-review bot D229, log triage D230, guardrails for CI actions D233, the guarded code-changing agent D235–D240) |
| Atlas systems | The ai service and its eval harness from [S8](stage-08-ai-integration.md); the monorepo and its CI |

**Goal.** Pick the electives that your evals or your job search say matter, build them to the same standard as the rest of Atlas, then close Season 2.

### Electives (choose; each needs a stated reason)

| Elective | Condition to start | Done when |
|---|---|---|
| **Re-ranking** of retrieved chunks (D201) | The S8 eval report shows a retrieval gap. The S8 rule stands: rerank only if evals show a gap. | hit@k or MRR improves on the golden set, and the latency and $ cost of the extra step are recorded |
| **Query rewriting** for follow-up questions (D199) | Multi-turn chat in the assistant produces pronoun follow-ups that retrieval misses | A fixture test on a pronoun follow-up passes |
| **Judge calibration** (D195, D207) | The nightly judge (an S8 stretch item) exists or you build it now | The judge agrees with your hand grades on a stated share of 15 or more answers, with a $ cap per night |
| **AI PR-review bot** (D229, D233) | — | The bot comments on PRs in the Atlas repo; its token cannot approve or merge, and an attempt to do so is shown to fail |
| **Guarded agent** (D235–D240), retargeted at the Atlas repo | — | A reject-by-default classifier, a path allow-list, sandboxed tests, a PR-only tool, a human approval gate, and an adversarial ticket that is refused |

### Capstone and close

1. **Season 2 demo and README section**: the warehouse reconciliation, one A/B readout checked against ground truth, the fraud champion/challenger, the drift alert, and the CDC comparison, each with its number.
2. **An ML-platform whiteboard for Atlas** (a suggested closing exercise, not from the SD bank): feature pipeline, training, registry, serving with fallback, monitoring. 45 minutes on a blank page, then diff it against what you built, the same way SD20 closes Season 1 ([system-design-map.md](system-design-map.md)).
3. **Final STAR selection**: add the best 2–3 Season 2 stories to the Season 1 set.
4. **Program retrospective** (the D366 idea): what you would build differently now.

### Not doing

- Fine-tuning, GPUs, multi-agent frameworks (the S8 "not doing" list still holds).

---

## 11. Season 2 as a whole

### Deliberately not doing

| Item | Why | When |
|---|---|---|
| Real customer data | Synthetic data with known truth is the point; real data needs a legal basis and a DPA | A job |
| Fine-tuning LLMs, GPU training | Not needed for the backend-with-AI profile; cost | Not planned |
| A feature-store product | One feature function plus Timescale covers the need at this size | Name it in interviews |
| Lakehouse table formats | Warehouse plus object storage is enough for these volumes | Not planned |
| Multi-region data | Season 1 is single-region (ADR-021) | Not planned |

### How degrade-list choices from Season 1 change Season 2

| Degrade item applied in Season 1 | Effect on Season 2 |
|---|---|
| 6' (vendor-sales CAGG and the matview comparison dropped; compression and retention kept on one hypertable) | 2A marts provide vendor sales; 2E compares streaming features with the velocity CAGGs only |
| 13 (semantic product search dropped) | 2C must first generate product embeddings for kNN recommendations |
| 20 (conversations stay in Postgres) | No effect on Season 2 marts; conversations are not a Season 2 source |
| 21 (kind only, no cloud Kubernetes) | 2C's KServe comparison runs on kind, which it does anyway |
| 23 (fraud stays in-process) | 2D's registry consumer and fail-closed test move into atlaspay |
| 24 (inventory not extracted) | Stock data for 2C comes from the market DB instead of the `inventory` DB |

### Common mistakes across Season 2

1. Analysing data whose generator version and seed you did not record.
2. Looking at the ground truth before writing your answer.
3. Reporting a model without its baseline.
4. Random splits on time-ordered data.
5. A warehouse that reconciles only with itself.
6. Treating the synthetic metrics as if they said something about real fraud rates.
7. Adopting a tool (Kafka, Spark, KServe) without a measured reason, the exact habit Season 1's split gate trained out of you.
