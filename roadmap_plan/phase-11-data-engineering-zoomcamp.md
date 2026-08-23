# PHASE 11 — Data Engineering Zoomcamp: Unified Analytics Platform
### Weeks 56–61 · ~3.5h weekdays, ~2.5h Saturdays · 36 working days (D331–D366)

*This is the final phase of the 12-month program. It follows the real
DataTalksClub "Data Engineering Zoomcamp" curriculum module-by-module
(Docker-terraform → Workflow orchestration → Data-warehouse → Analytics
engineering → Data platforms → Batch → Streaming) and applies every module
hands-on by building one thing: a unified analytics platform pulling from
the Postgres databases behind the year's OLTP systems — StockPilot,
QuickServe, PeopleOps, LedgerBase, FleetTrack, and AtlasMarket.*

---

## 1. Learning Goals

By the end of Phase 11 you can:

- Provision cloud infrastructure (a data warehouse, datasets, IAM) declaratively
  with Terraform instead of clicking through a console, and read a `terraform
  plan` diff carefully enough to trust — or reject — it before applying.
- Orchestrate a multi-source data pipeline with Airflow: DAGs, idempotent
  extract/load tasks, retries, and backfills — not a cron job that silently
  doubles data the first time it's retried.
- Reason about a columnar cloud warehouse (partitioning, clustering, the
  bytes-scanned cost model) the same rigorous way Phase 1/3 taught you to
  reason about Postgres's row-store planner and `EXPLAIN ANALYZE`.
- Build a real dbt project: staged sources, an intermediate layer, tested
  marts, and a lineage graph you could hand to another engineer on day one.
- Write and tune a Spark batch job — DataFrames, joins, shuffles, broadcast
  joins — and know when reaching for Spark is the right call versus just
  writing warehouse SQL, instead of reaching for it by default.
- Extend Phase 3's Kafka knowledge into ksqlDB/Kafka Streams for real-time
  aggregation, and reason precisely about at-least-once vs exactly-once
  semantics using an idempotent consumer — not a hand-wave.
- Unify data from six of the year's ten OLTP systems into one analytics
  platform a business owner could actually look at, while consciously
  documenting what's deferred rather than silently dropping it.
- Close out the entire 12-month program: a full retrospective, a final
  tag, and an honest account of what you'd do differently.

---

## 2. Technologies Introduced This Phase

Terraform (providers, state, `plan`/`apply`/`destroy`) · Apache Airflow
(DAGs, operators, hooks, retries, backfills, scheduling) · a cloud data
warehouse — **BigQuery** is used throughout as the concrete reference
implementation, consistent with the real DataTalksClub Data Engineering
Zoomcamp curriculum this phase follows, though every concept covered
(partitioning, clustering, `MERGE` upserts, the bytes-scanned cost model)
transfers directly to Snowflake/Redshift/Fabric if that's what a future
employer runs · dbt (models, sources, tests, docs, lineage) · Apache
Spark / PySpark (DataFrames, joins, shuffle, broadcast joins, performance
tuning) · Kafka Streams / ksqlDB (extends Phase 3's Kafka work) · Grafana
(extends Phase 4's monitoring stack, now pointed at warehouse data instead
of application metrics).

This phase deliberately introduces almost no new *business domain* —
instead it reaches back into StockPilot, QuickServe, PeopleOps,
LedgerBase, FleetTrack, and AtlasMarket's Postgres databases and ties them
together. It's the data-engineering mirror of what Phase 6 did for backend
services: an integration capstone, not a fresh domain.

Deliberately out of scope, named and documented rather than silently
skipped: CDC via Debezium (this phase's extraction stays batch/polling on
purpose, so you feel the tradeoff), a lakehouse table format (Iceberg/
Delta), and running Airflow on a managed service (Cloud Composer/MWAA)
instead of local Docker Compose — all three are real "what you'd do at a
company" callouts, written down in `docs/platform-roadmap.md` so scope
creep doesn't eat Week 61.

---

## 3. PROJECT 11 — Year-2 Analytics Platform (Batch Core)

**Business Problem:** After a year of shipping StockPilot, QuickServe,
PeopleOps, and LedgerBase as separate OLTP systems, nobody — least of all
the fictional business owner behind all of them — can answer a question
that spans more than one system: "what's our total revenue and inventory
value this month, and did the headcount growth in PeopleOps correlate with
it?" Each system's Postgres database is optimized for fast writes on
today's transaction, not for a month-over-month scan across a year of
history from four services at once. Year-2 Analytics Platform exists to
answer exactly those cross-system questions, on a schedule, without
competing with the OLTP databases' own query load.

**Requirements**

Functional:
- Nightly, incremental extraction of `orders`/`order_items` (StockPilot),
  `sales`/`sale_items` (QuickServe), `leave_requests`/`employees`
  (PeopleOps), and `journal_entries`/`accounts` (LedgerBase) into a
  warehouse `raw` dataset.
- Idempotent load into a `staging` dataset — reruns of the same day never
  duplicate rows.
- A dbt project transforming staging into a tested `marts` layer:
  `fct_orders`, `dim_products`, `fct_leave_requests`, `fct_journal_entries`,
  `dim_employees`, `dim_date`.
- One dashboard reading only from `marts`, showing revenue, inventory
  value, headcount/leave, and ledger balance side by side.

Non-functional:
- The nightly pipeline must be safely rerunnable — a failed 2am run
  retried at 3am must produce the same end state as a clean run.
- No pipeline task ever runs a query against an OLTP production database
  heavy enough to compete with real user traffic — extraction is windowed
  and paced.
- Every mart table has at least one dbt test; a broken test fails the
  pipeline loudly instead of shipping bad numbers to the dashboard quietly.

**Architecture (textual)**
```
StockPilot Postgres ─┐
QuickServe Postgres  ─┼─▶ Airflow DAGs (nightly, one per source, incremental by updated_at)
PeopleOps Postgres   ─┤        │  extract → land in `raw` (append-only)
LedgerBase Postgres  ─┘        └▶ load → MERGE into `staging` (idempotent upsert)
                                          │
                                          ▼
                        dbt: staging → intermediate → marts
                     (fct_orders, dim_products, fct_leave_requests,
                      fct_journal_entries, dim_employees, dim_date)
                                          │
                                          ▼
                          Grafana dashboard (unified view, Week 61)
```
Terraform (Week 56) provisions `raw`, `staging`, and `marts` datasets plus
one dataset-scoped service account before any pipeline code runs. **Not
connected in this phase, documented rather than silently dropped:**
WareFlow, CarePoint, DocuVault, and PayFlow — the same honest-deferral
habit as AtlasMarket's `docs/atlasmarket-roadmap-post-bootcamp.md` from
Phase 6, now living in `docs/platform-roadmap.md`.

**Folder Structure**
```
year2-analytics-platform/
  terraform/
    main.tf              # datasets, service account, IAM bindings
    variables.tf
  airflow/
    dags/
      extract_load_stockpilot.py
      extract_load_quickserve.py
      extract_load_peopleops.py
      extract_load_ledgerbase.py
  dbt/
    models/
      staging/
      intermediate/
      marts/
    tests/
    dbt_project.yml
  dashboards/
    grafana/
      unified-year2-view.json
  docs/
    architecture.md
    platform-roadmap.md
```

**Testing Strategy:** dbt schema tests (`not_null`, `unique`,
`relationships`) on every mart's primary/foreign keys; one singular
reconciliation test asserting `fct_orders`' summed revenue matches a
recomputed sum from `stg_quickserve__sales` (catches a silent
transformation bug that schema tests alone would miss); an Airflow-level
idempotency test — run the same day's DAG twice, assert `staging` row
counts are identical, not doubled.

**Monitoring:** Airflow's own UI (task duration, success/failure history)
is the pipeline's monitoring for this phase — a dedicated pipeline-health
Grafana panel is named as a deferred nice-to-have, not built, matching
Phase 1's honest "not implemented in v1" call on caching.

**Deployment:** `terraform apply` run manually from a personal machine (no
CD for infra yet, deliberately — the same "manual for now" call Phase 1
made for StockPilot's first deploy); Airflow runs locally via Docker
Compose; in a real job this is where Cloud Composer/MWAA would sit
instead — named, not built.

**Common Interview Questions**
1. Why land raw data in an untouched `raw` dataset before transforming it,
   instead of transforming during extraction?
2. Walk through exactly how a rerun of last night's DAG avoids duplicating
   rows.
3. Why is a reconciliation test (a recomputed sum) a different kind of
   safety net than a `not_null` test?
4. What would you change if StockPilot's `orders` table had no
   `updated_at` column at all?
5. Why does the pipeline read from each OLTP database on a schedule
   instead of via CDC/replication?
6. How would this design change if PeopleOps had 50M leave-request rows
   instead of 50,000?
7. What's your rollback plan if a bad dbt model ships to `marts` and the
   dashboard shows wrong numbers for a day?

**Possible Improvements:** CDC via Debezium instead of batch-polling
extraction, dbt incremental models instead of full-refresh where volume
justifies it, a dedicated pipeline-health dashboard, Terraform remote
state + CI-driven `terraform plan` on pull requests.

**Common Mistakes:** transforming data on the way in instead of landing it
raw first (loses the ability to replay a fixed transformation against
history); using `INSERT` instead of `MERGE` for the staging load (silent
duplicate rows on any retry); writing dbt tests only on marts and never on
staging, so a source-data problem surfaces three layers downstream instead
of at the door.

---

## 4. PROJECT 11B — Year-2 Analytics Platform + Streaming Layer (FleetTrack)

**Business Problem:** The batch platform above answers "what happened last
night," which is fine for revenue and headcount, but useless for a
dispatcher who needs to know *right now* how many FleetTrack deliveries
are in progress. This extension adds a second, real-time path onto the
same platform, reusing FleetTrack's existing Phase 5 outbox/Kafka event
stream instead of building a new one.

**Requirements:** stream FleetTrack's `delivery_events` Kafka topic
(already produced via its outbox pattern) into a warehouse
`deliveries_in_progress` table that reflects current state within seconds,
not overnight, plus a Grafana panel showing live counts by status. A
duplicate or out-of-order event must never leave the table in a wrong
state — the same idempotency discipline PayFlow's webhooks demanded in
Phase 6, applied here to a stream instead of a single HTTP callback.

**Architecture**
```
FleetTrack Postgres --(outbox, Phase 5)--> Kafka topic `delivery_events`
                                                  │
                                    ksqlDB stream (windowed status aggregation)
                                                  │
                                Python consumer (idempotent, keyed on delivery_id+event_type)
                                                  │
                              BigQuery `deliveries_in_progress` (streaming upsert)
                                                  │
                                    Grafana panel (10s auto-refresh)
```
Reuses the same warehouse, service account, and Grafana instance the batch
core (Project 11) already provisioned — the "extends, doesn't rebuild"
pattern named explicitly for this week, the same spirit as WareFlow reusing
Phase 1's `Repository[T]` protocol instead of inventing a new one.

**Testing Strategy:** deliver the same `delivery_events` message 3 times
through the consumer and assert exactly one row results; a freshness
check — if no event has landed in `deliveries_in_progress` in the last N
minutes while the topic itself has traffic, that's a bug, not staleness.

**Monitoring:** the Grafana panel *is* the monitoring for this extension —
a stalled consumer shows up immediately as a flat line, which doubles as
an alert signal even without a formal alerting rule wired up yet (named as
the next step, not built).

**Deployment:** the consumer runs as one more container in the same
Docker Compose file as the rest of the platform; no new infrastructure
beyond what Project 11 and Phase 5's FleetTrack already stood up.

**Common Interview Questions**
1. Why key the idempotent upsert on `delivery_id` + `event_type` instead
   of just `delivery_id`?
2. What's the actual difference between "at-least-once" and
   "exactly-once" here, given your consumer isn't literally exactly-once
   at the Kafka level?
3. Why reuse FleetTrack's existing outbox-driven topic instead of adding a
   second producer?
4. How does ksqlDB's windowed aggregation differ from what your Python
   consumer does?
5. What would you check first if the dashboard "flatlined" — the
   consumer, the topic, or the source?

**Possible Improvements:** a real alerting rule on consumer lag, a Kafka
Connect BigQuery sink instead of a hand-rolled consumer, true exactly-once
semantics via Kafka transactions if the business case ever justified the
added complexity.

**Common Mistakes:** treating "streaming" as automatically meaning "no
idempotency needed" (the opposite is true — streams replay and duplicate
far more often than a single HTTP request does); building this as a
second, disconnected mini-project instead of landing it in the same
warehouse and dashboard as Project 11.

---

## 5. PROJECT 11C — Year-2 Analytics Platform + Vendor Analytics Extension (AtlasMarket)

**Business Problem:** AtlasMarket's vendors (Phase 6) currently have no
visibility into their own performance beyond what they can see in the
marketplace UI. A vendor-analytics extension answers "how is vendor X
doing relative to others" using the same platform infrastructure Projects
11 and 11B already built, rather than a bespoke reporting feature bolted
onto AtlasMarket's own API.

**Requirements:** extract AtlasMarket's `orders`/`order_vendor_groups`/
`vendors` tables via the same Airflow extraction pattern as Project 11;
one new dbt mart, `fct_vendor_revenue`, reconciled against `fct_orders`;
one new Grafana panel added to the existing unified dashboard.

**Architecture**
```
AtlasMarket Postgres --(Airflow, same DAG pattern as Project 11)--> raw --> staging
                                          │
                            dbt: fct_vendor_revenue (joins staging to fct_orders)
                                          │
                        existing Grafana dashboard, one new panel
```
No new Terraform, no new Airflow infrastructure, no new Kafka topic —
this is intentionally the smallest of the three projects, because it's an
*extension* of infrastructure that already exists, the same compression
Phase 7/9's Week-36/49 project pairs also used once their own base
infrastructure was already standing.

**Testing Strategy:** a reconciliation test asserting `fct_vendor_revenue`
summed across all vendors equals `fct_orders`' total revenue for the same
period (a vendor's revenue can't disappear or double just because it's
sliced a different way); a test for vendors with zero orders (must appear
as `0`, not be silently absent from the mart).

**Monitoring / Deployment:** rides on Project 11's existing Airflow/dbt/
Grafana stack — no new moving parts to monitor or deploy.

**Common Interview Questions**
1. Why does `fct_vendor_revenue` need to reconcile against `fct_orders`
   rather than being trusted on its own?
2. Why was this project scoped to take roughly one day instead of a full
   week?
3. What's the next vendor-analytics feature you'd build given another
   week, and why is that a deliberate deferral rather than scope creep?

**Possible Improvements:** vendor cohort analysis, a per-vendor self-serve
dashboard (would require AtlasMarket-side auth scoping, out of scope
here), anomaly detection on sudden vendor revenue drops.

**Common Mistakes:** re-deriving revenue from raw AtlasMarket tables
instead of joining against the already-tested `fct_orders`, which
duplicates logic and can silently drift from the canonical number.

---

## 6. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| Standalone Terraform plan/apply/destroy loop on a throwaway resource | 51 | Terraform's core loop before touching real infra |
| Hello-world Airflow DAG (2 `PythonOperator`s) | 52 | DAG/operator basics before real extract-load tasks |
| dbt "first models" walkthrough on a toy CSV source | 53 | dbt fundamentals before modeling real staging/marts |
| Local PySpark `groupBy`+`agg` on a synthetic CSV | 54 | Spark DataFrame basics before the real yearly aggregation job |
| ksqlDB stream + rolling `GROUP BY` demo on a toy topic | 55 | Declarative streaming aggregation before wiring FleetTrack |
| Idempotent-upsert demo (send the same fake event 3x) | 55 | Exactly-once-in-effect consumers, before it's load-bearing |

---

## 7. Books & Documentation for This Phase

- DataTalksClub *Data Engineering Zoomcamp*
  (github.com/DataTalksClub/data-engineering-zoomcamp) — this phase
  follows its module order end to end (Docker-terraform → Workflow
  orchestration → Data-warehouse → Analytics engineering → Data platforms
  → Batch → Streaming); read each module's own README the week you're in it.
- Terraform docs (developer.hashicorp.com/terraform/docs) —
  "Configuration Language" and the Google Cloud provider's
  `bigquery_dataset`/`google_service_account` resources — Week 56.
- Apache Airflow documentation (airflow.apache.org/docs) — "Core
  Concepts: DAGs", "Scheduling & Triggers", "Backfill" — Week 57.
- Google BigQuery documentation (cloud.google.com/bigquery/docs) —
  "Partitioned tables", "Clustered tables", "Query optimization best
  practices" — Week 58 (concepts transfer to any columnar warehouse).
- dbt documentation (docs.getdbt.com) — "Build your first models",
  "Testing", "How we structure our dbt projects" — Week 58.
- Apache Spark documentation (spark.apache.org/docs/latest) — "RDD
  Programming Guide", "SQL, DataFrames and Datasets Guide", "Performance
  Tuning" — Week 59.
- Confluent ksqlDB documentation
  (docs.confluent.io/platform/current/ksqldb) + Kafka's own "Message
  Delivery Semantics" design doc — Week 60.
- *Fundamentals of Data Engineering* (Reis & Housley, O'Reilly) — read
  alongside Week 59's lakehouse/data-platform topics; it's the
  book-length version of the same argument.

---

## 8. Weekly Interview Question Sets

**Week 56 — Docker & Terraform**
1. What's the difference between `terraform plan` and `terraform apply`,
   and why should you always read the plan?
2. What does Terraform state track, and why is losing the state file
   dangerous?
3. Why provision the warehouse with IaC instead of clicking through a
   console?
4. What's the blast-radius difference between a `terraform destroy` on a
   shared vs a project-scoped state?
5. How do you keep local dev and cloud environments in parity without
   duplicating config?

**Week 57 — Workflow Orchestration**
1. DAG vs a plain cron script — what does Airflow actually add?
2. Why must an extract-load task be idempotent, and how did you make
   yours idempotent (MERGE vs INSERT)?
3. What's a backfill, and why is `schedule_interval` + `start_date` the
   trap that catches people running one for the first time?
4. How do retries in Airflow interact with idempotency — what happens if
   a task fails halfway through a load?
5. How would you handle a source table with no reliable `updated_at`
   watermark?

**Week 58 — Data Warehouse + Analytics Engineering**
1. Why does clustering/partitioning reduce bytes scanned, concretely?
2. Columnar vs row storage — why does one favor `SELECT col FROM
   huge_table` and the other doesn't care?
3. What's the difference between a dbt source, a staging model, and a
   mart?
4. What does a dbt test actually check, and what's the difference between
   a generic and a singular test?
5. Why build an intermediate layer instead of joining straight from
   staging to mart?

**Week 59 — Data Platforms + Batch (Spark)**
1. RDD vs DataFrame — why do DataFrames usually win for analytics
   workloads today?
2. What triggers a Spark shuffle, and why is it expensive?
3. When would you reach for Spark instead of just writing the aggregation
   in warehouse SQL?
4. What's a broadcast join, and when does it help?
5. Explain the medallion (bronze/silver/gold) architecture in your own
   words, mapped to this platform's raw/staging/marts.

**Week 60 — Streaming**
1. At-least-once vs exactly-once delivery — where does the
   "exactly-once" claim usually hide extra work (idempotent consumers)?
2. Kafka Streams/ksqlDB vs a hand-rolled consumer doing the same
   aggregation — when does the declarative tool win?
3. Why key the deliveries table's upsert on `delivery_id` + `event_type`
   instead of just `delivery_id`?
4. How does a real-time dashboard stay "real-time" without polling the
   warehouse every second?
5. What breaks in your streaming consumer if the Kafka topic is
   reprocessed from offset 0?

**Week 61 — Final Capstone / Program Wrap**
1. Walk through the full pipeline for one row of data, from a StockPilot
   Postgres insert to it appearing on the unified dashboard, naming every
   hop.
2. Why were Project 2 and Project 3 this week so much faster to build
   than Project 1?
3. Of everything across all 12 months, which single piece of
   infrastructure paid for itself the most times over?
4. If you had to onboard a new data engineer onto this platform tomorrow,
   what's the first doc you'd hand them?
5. Looking back at Day 1 vs Day 366 — what's the biggest gap that closed?

---

## 9. Daily Plan — Week 56: Docker & Terraform, Warehouse Provisioning

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D331)** | IaC concepts, Terraform basics: providers, resources, HCL | Terraform docs "What is Terraform" + "Configuration Language" | Throwaway `.tf` file provisioning a local `null_resource`, run plan/apply/destroy | Init `year2-analytics-platform/` repo, `terraform/` scaffold, document local-state backend decision | Run `terraform validate` locally | `chore: repo scaffold + terraform init` | Q1 | 3.5h |
| **Tue (D332)** | Terraform state + providers deep dive; provisioning a warehouse dataset | Terraform docs "State" + Google provider `bigquery_dataset` resource | `plan`/`apply`/`destroy` a real dataset twice, read the state file by hand once | `main.tf` provisioning `raw` + `staging` BigQuery datasets | Confirm datasets visible via `bq ls`/console after apply | `feat: terraform-provisioned raw + staging datasets` | Q2 | 3.5h |
| **Wed (D333)** | Containerizing data pipelines (reusing Phase 1 Docker skills) | Docker Compose docs (recap) | Dockerfile for a tiny Python script reading Postgres, writing a CSV | `docker-compose.yml` scaffold: local Postgres mirror + placeholder Airflow service | Verify `docker compose up` boots cleanly | `chore: docker compose scaffold for pipeline services` | Q3 | 3.5h |
| **Thu (D334)** | Local vs cloud dev environment parity | Terraform docs workspaces/environments pattern | Config loader switching between a local Postgres "fake warehouse" and real BigQuery via one env flag | `warehouse_client.py` abstraction so later pipeline code is warehouse-agnostic | Unit test both backends against a stub | `feat: warehouse client abstraction (local/cloud parity)` | Q4 | 3.5h |
| **Fri (D335)** | Provisioning the real cloud warehouse end-to-end + least-privilege IAM | Terraform docs `google_service_account` + dataset IAM binding | `terraform validate` + apply against a real GCP sandbox project | Finalize `raw`/`staging`/`marts` datasets + one dataset-scoped service account; write `docs/architecture.md` | Confirm the service account can't touch datasets outside its scope | `feat: warehouse IAM + marts dataset provisioned` | Q5 | 3.5h |
| **Sat (D336)** | **Review** | — | Redo Tuesday's dataset provisioning from memory, no notes | Re-read `docs/architecture.md` for anything under-specified | `terraform plan` shows zero drift | — | Answer all 5 Week-56 questions out loud, unscripted | 2.5h |

---

## 10. Daily Plan — Week 57: Workflow Orchestration (Airflow)

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D337)** | Orchestration concepts: DAGs, operators, scheduler | Airflow docs "Core Concepts: DAGs" | Hello-world DAG, 2 `PythonOperator` tasks with a dependency | Bring up local Airflow via Docker Compose (webserver+scheduler+metadata DB) | Confirm DAG appears and runs green in the UI | `chore: local airflow via docker compose` | Q1 | 3.5h |
| **Tue (D338)** | Extract step: incremental pulls via an `updated_at` watermark | Airflow docs "Connections & Hooks" (`PostgresHook`) | Script pulling rows from StockPilot's `orders` where `updated_at > last_watermark` | `extract_load_stockpilot.py`: extract task landing StockPilot into `raw` | Test extraction returns zero new rows on a second run with no source changes | `feat: stockpilot extract task` | Q2 | 3.5h |
| **Wed (D339)** | Load step: landing raw data into staging | BigQuery docs "Loading data" | Load a CSV into a staging table via the BigQuery Python client | Complete StockPilot's load task into `staging`; add QuickServe's extract task | Integration test: run the full StockPilot DAG once end-to-end | `feat: stockpilot load task + quickserve extract` | Q3 | 3.5h |
| **Thu (D340)** | Idempotent, retriable pipeline design (MERGE vs INSERT) | BigQuery docs "MERGE statement" | Rerun the same DAG run twice, assert no duplicate rows land | Convert QuickServe + PeopleOps loads to idempotent `MERGE`-based upserts | Test: rerunning a load task twice leaves row counts unchanged | `fix: idempotent MERGE upserts for quickserve + peopleops` | Q4 | 3.5h |
| **Fri (D341)** | Backfills, `schedule_interval`, catchup | Airflow docs "DAG Runs" + backfill command reference | Backfill a toy DAG over a 7-day historical window | Finalize `@daily` schedules for all 3 DAGs; run one real historical backfill | Verify backfilled rows match a manual source-side count | `feat: nightly schedule + historical backfill` | Q5 | 3.5h |
| **Sat (D342)** | **Review** | — | Redo the MERGE-upsert idempotency test from memory | Trace one row from StockPilot Postgres through to `staging` by hand | Full DAG re-run, all green | — | Answer all 5 Week-57 questions out loud, unscripted | 2.5h |

---

## 11. Daily Plan — Week 58: Data Warehouse + Analytics Engineering (dbt)

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D343)** | Warehouse fundamentals: columnar storage, partitioning, clustering | BigQuery docs "Partitioned tables" | Create a date-partitioned+clustered table, compare bytes-scanned with/without a partition filter | Apply date-partitioning + clustering to `stg_orders`, `stg_stock_movements` | Confirm a partition-filtered query scans a fraction of the bytes | `perf: partition + cluster staging tables` | Q1 | 3.5h |
| **Tue (D344)** | Query optimization on a columnar warehouse vs Postgres tuning | BigQuery docs "Query optimization best practices" | Rewrite a `SELECT *` into a column-pruned query, compare bytes-scanned estimates | Audit and fix 3 wasteful queries in the Week 57 load tasks | Record before/after bytes-scanned for each | `perf: column-pruned load queries` | Q2 | 3.5h |
| **Wed (D345)** | dbt fundamentals: models, sources, tests | dbt docs "Build your first models" | `dbt init`, one source + one staging model + one `not_null`/`unique` test | `dbt/` project scaffold, `sources.yml` pointing at `raw`/`staging` | `dbt test` passes on the first model | `feat: dbt project scaffold + first source` | Q3 | 3.5h |
| **Thu (D346)** | Staging → intermediate → marts layering | dbt docs "How we structure our dbt projects" | Build one intermediate model joining 2 staging models | `stg_stockpilot__orders`, `stg_quickserve__sales`, `stg_peopleops__leave_requests`, `int_orders_enriched` | `dbt run` + `dbt test` green across all new models | `feat: staging + intermediate dbt models` | Q4 | 3.5h |
| **Fri (D347)** | dbt tests + docs, lineage graph | dbt docs "Testing" + "Documentation" | Add one singular test, run `dbt docs generate`, browse the lineage graph | Build `marts`: `fct_orders`, `dim_products`, `fct_leave_requests` with schema tests | `dbt docs generate` produces a clean lineage graph, no orphan models | `feat: marts layer + dbt docs site` | Q5 | 3.5h |
| **Sat (D348)** | **Review** | — | Redo Wednesday's `dbt init` from memory | Re-read the lineage graph for anything mis-joined | `dbt test` full suite green | — | Answer all 5 Week-58 questions out loud, unscripted | 2.5h |

---

## 12. Daily Plan — Week 59: Data Platforms + Batch Processing (Spark)

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D349)** | Lakehouse concepts / data platform architecture (bronze/silver/gold) | Databricks "What is a data lakehouse" overview | Map this platform's raw/staging/marts onto bronze/silver/gold in one paragraph | Update `docs/architecture.md` with the lakehouse-terms mapping | — | `docs: map platform to lakehouse (bronze/silver/gold) terms` | Q1 | 3.5h |
| **Tue (D350)** | Spark fundamentals: RDDs vs DataFrames, SparkSession | Spark docs "RDD Programming Guide" + "SQL, DataFrames and Datasets Guide" | Local PySpark script: read a CSV, `groupBy().agg()`, `.show()` | `spark/` scaffold; PySpark job skeleton reading from BigQuery via the Spark-BigQuery connector | Job runs locally against a small sample table | `feat: spark job scaffold + bigquery connector` | Q2 | 3.5h |
| **Wed (D351)** | Batch aggregation: yearly stock-movement/order analytics | Spark docs "DataFrame aggregation functions" | Aggregate a synthetic multi-million-row CSV by month+product, time it | `yearly_stock_movement_agg.py`: joins StockPilot stock movements + QuickServe sales for the full year, writes to a `marts` table | Row-count + spot-check totals against a manual dbt query | `feat: yearly stock-movement spark aggregation job` | Q3 | 3.5h |
| **Thu (D352)** | Spark joins & performance tuning: broadcast join, shuffle | Spark docs "Performance Tuning" | Compare a shuffle join vs a broadcast join on skewed synthetic data via `.explain()` | Tune the yearly aggregation job: broadcast `dim_products`, repartition on `product_id` | Record before/after runtime and shuffle-stage count | `perf: broadcast join + repartition for yearly agg job` | Q4 | 3.5h |
| **Fri (D353)** | Choosing warehouse-SQL vs Spark for a given batch job | — | — | `docs/spark-vs-warehouse-sql.md`; re-implement one small job as a plain dbt SQL model for comparison | Compare runtime + cost of the Spark version vs the SQL version | `docs: spark vs warehouse-sql decision record` | Q5 | 3.5h |
| **Sat (D354)** | **Review** | — | Redo the broadcast-join tuning from memory | Re-read `docs/spark-vs-warehouse-sql.md` for a decision you'd now make differently | Full Spark job re-run, timings recorded | — | Answer all 5 Week-59 questions out loud, unscripted | 2.5h |

---

## 13. Daily Plan — Week 60: Streaming

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D355)** | Streaming concepts recap, bridging Phase 3's Kafka | Kafka docs "Introduction" (recap) + ksqlDB docs "Overview" | Stand up local Kafka (Phase 3 compose), produce/consume 10 test messages | Add a Kafka broker service back into this repo's compose, pointed at FleetTrack's existing topic | Confirm 10 messages round-trip correctly | `chore: kafka broker wired into platform compose` | Q1 | 3.5h |
| **Tue (D356)** | Kafka Streams / ksqlDB for real-time aggregation | ksqlDB docs "Create a Stream" + "Aggregate Streaming Data" | A ksqlDB stream + rolling `GROUP BY` count on a toy topic | `deliveries_stream.sql`: ksqlDB stream over FleetTrack's `delivery_events` topic | Query the stream, confirm counts update as new events arrive | `feat: ksqldb stream over fleettrack delivery_events` | Q2 | 3.5h |
| **Wed (D357)** | Streaming FleetTrack's events into the warehouse | BigQuery docs "Streaming data" (insert API) | Minimal consumer inserting one row per event via the streaming-insert API | `streaming/consumer.py` consuming `delivery_events`, upserting into `deliveries_in_progress` | Manual test: fire 5 events, confirm 5 rows land within seconds | `feat: kafka-to-warehouse streaming consumer` | Q3 | 3.5h |
| **Thu (D358)** | Exactly-once vs at-least-once semantics | Kafka docs "Message Delivery Semantics" | Reprocess the same message twice, observe the duplicate, then fix it | Make the consumer idempotent: `MERGE` keyed on `delivery_id` + `event_type` | Test: same event delivered 3x results in exactly one row | `fix: idempotent upsert for streaming consumer` | Q4 | 3.5h |
| **Fri (D359)** | Real-time dashboard on streamed data (Grafana, Phase 4 stack) | Grafana docs "Add a data source" | Point Grafana at the warehouse table, one panel: live in-progress count | `dashboards/grafana/deliveries-in-progress.json`, panel refreshing every 10s | Confirm panel updates within one refresh cycle of a new event | `feat: real-time deliveries-in-progress dashboard` | Q5 | 3.5h |
| **Sat (D360)** | **Review** | — | Redo the idempotent-upsert fix from memory | Re-watch the dashboard while manually firing a few test events | Full streaming pipeline smoke test | — | Answer all 5 Week-60 questions out loud, unscripted | 2.5h |

---

## 14. Daily Plan — Week 61: Project 1 + Project 2 + Project 3, Full Program Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D361)** | Project 1 integration: run the full batch pipeline top to bottom for the first time | dbt docs "dbt run" / orchestrating dbt (recap) | — | `terraform apply` → trigger all 4 Airflow DAGs → `dbt run && dbt test`; record total run time | Full pipeline run, zero failed tasks, all dbt tests green | `feat: first full end-to-end platform run` | Q1 | 3.5h |
| **Tue (D362)** | Project 1: unified BI-style dashboard (StockPilot+QuickServe+PeopleOps+LedgerBase) | Grafana docs "Panels" (recap) | — | Build the unified dashboard: revenue, inventory value, headcount/leave, ledger balance, all from `marts` | Manually verify each panel's number against a hand-run SQL query | `feat: unified year-2 analytics dashboard` | Q2 | 3.5h |
| **Wed (D363)** | Project 1: hardening — remaining dbt tests, docs, milestone tag | dbt docs "dbt-utils" package (recap) | — | Add referential-integrity + `accepted_values` tests, `dbt docs generate`, tag `v0.1-year2-analytics-platform` | Full `dbt test` suite green, docs site builds clean | `docs: dbt docs + test hardening, tag v0.1` | Q3 | 3.5h |
| **Thu (D364)** | Project 2 (smaller, faster — extends Project 1's infra): land the streaming layer as a first-class part of the platform | — | — | Fold Week 60's streaming consumer + dashboard panel officially into this repo; finalize its dbt tests/docs; tag `v0.2-plus-streaming` | Duplicate-event + freshness tests both green | `feat: streaming layer finalized, tag v0.2` | Q4 | 3.5h |
| **Fri (D365)** | Project 3 (smaller still — extends Project 1's infra): freeform extension — AtlasMarket vendor analytics | — | — | Extract AtlasMarket vendor/order data, `fct_vendor_revenue` dbt model, one new dashboard panel, tag `v0.3-plus-vendor-analytics` | Reconciliation test: `fct_vendor_revenue` sums to `fct_orders` total | `feat: vendor analytics extension, tag v0.3` | Q5 | 3.5h |
| **Sat (D366)** | **FULL 12-MONTH PROGRAM WRAP** | — | — | Write `docs/program-retrospective.md`: a phase-by-phase retrospective across all 11 phases and every project, from StockPilot's first decorator to this platform's last dbt model; tag `v2.0-year-plan-complete` | Run the entire platform (all 3 projects) one final time, end to end, everything green | `docs: full 12-month program retrospective, tag v2.0-year-plan-complete` | Full mock behavioral + "walk me through your year" round, timed, no notes | 2.5h |

*Note on pacing:* Project 2 (Thursday) and Project 3 (Friday) are
deliberately smaller and faster than Project 1 (Monday–Wednesday) — they
extend infrastructure Project 1 already built rather than starting fresh,
the same compression Phase 7's Week-36 and Phase 9's Week-49 project pairs
used once *their* base infrastructure was already standing.

---

## 15. Deliverables & GitHub Milestones

**Milestone: `Phase 11 — Year-2 Analytics Platform v0.1 / v0.2 / v0.3`**
- [ ] Terraform-provisioned `raw`/`staging`/`marts` warehouse datasets +
      least-privilege service account
- [ ] 4 idempotent, retriable Airflow DAGs (StockPilot, QuickServe,
      PeopleOps, LedgerBase) on a nightly schedule, backfill proven
- [ ] dbt project: staging → intermediate → marts, schema tests + one
      reconciliation test on every mart, docs + lineage graph generated
- [ ] Spark batch job (yearly stock-movement/order aggregation) tuned with
      a measured broadcast-join before/after
- [ ] `docs/spark-vs-warehouse-sql.md` decision record
- [ ] ksqlDB stream + idempotent Kafka-to-warehouse consumer streaming
      FleetTrack's `delivery_events` into `deliveries_in_progress`
- [ ] Real-time Grafana dashboard on the streaming table
- [ ] Unified BI-style dashboard across StockPilot + QuickServe +
      PeopleOps + LedgerBase marts
- [ ] AtlasMarket vendor-analytics extension (`fct_vendor_revenue`),
      reconciled against `fct_orders`
- [ ] `docs/platform-roadmap.md` — explicit deferred scope (WareFlow,
      CarePoint, DocuVault, PayFlow not yet connected)
- [ ] `docs/program-retrospective.md` — full 12-month retrospective
- [ ] Tags: `v0.1-year2-analytics-platform`, `v0.2-plus-streaming`,
      `v0.3-plus-vendor-analytics`, `v2.0-year-plan-complete`

---

## 16. Skills Acquired Checklist

- [ ] Terraform: providers, state, plan/apply/destroy, least-privilege IAM
- [ ] Airflow: DAGs, operators, hooks, retries, idempotent extract/load,
      backfills, scheduling
- [ ] Columnar warehouse fundamentals: partitioning, clustering, the
      bytes-scanned cost model
- [ ] dbt: sources, staging/intermediate/marts layering, tests, docs,
      lineage
- [ ] Spark/PySpark: DataFrames, joins, shuffle, broadcast joins,
      performance tuning
- [ ] Kafka Streams/ksqlDB for real-time aggregation, extended from
      Phase 3
- [ ] Exactly-once-in-effect streaming consumers via idempotent upserts
- [ ] Real-time dashboarding on streamed data (Grafana, extended from
      Phase 4)
- [ ] Integrating 6 of the year's 10 OLTP systems into one coherent
      analytics platform, with honest, documented scope deferral
- [ ] Full-program retrospective and closing discipline (tagging,
      retrospective writing)

---

**This is the end of the 12-month plan.** Tag `v2.0-year-plan-complete`
and celebrate — you went from mid-level Python backend engineer to a
builder who ships ML models, LLM/RAG features, AI coding agents, and full
data platforms, on top of a decade-deep backend systems foundation.
