# PHASE 8 — MLOps Engineering Zoomcamp
### Weeks 45–50 · ~3.5h weekdays, ~2.5h Saturdays · 36 working days

---

## 1. Learning Goals

By the end of Phase 10 you can:

- Explain the MLOps maturity model and diagnose, for a real training script,
  exactly which level it's at (manual process → automated training pipeline →
  full CI/CD) and what the next investment actually buys you.
- Instrument any training script with MLflow tracking (params, metrics,
  artifacts) and manage a Model Registry (`Staging`/`Production`) as the
  single source of truth for "what's live" — not a judgment call made from
  memory.
- Express a training pipeline as a DAG of small, retryable, idempotent
  Prefect tasks (`ingest → train → evaluate → register`), and reason about
  scheduling, retry, and parameterization semantics instead of hoping a cron
  job just works.
- Choose the right deployment pattern — batch, web service, or streaming —
  for a given latency/freshness SLA, and defend the choice on paper, not
  default to whichever is more familiar.
- Detect and monitor data drift, target drift, and model decay with
  Evidently, and wire the numbers into infrastructure you already run
  (Grafana) instead of leaving them in a one-off notebook.
- Write CI that gates a merge on model *quality* (a regression-tested
  metric), not just code correctness.
- Take a raw scikit-learn/XGBoost training script from Phase 9 and turn it
  into a fully productionized module — tracked, orchestrated, deployed,
  monitored, CI-gated, end to end — three times, measurably faster each
  time.

---

## 2. Technologies Introduced This Phase

MLflow (Tracking, Model Registry) · Prefect (flows, tasks, schedules,
retries, deployments, state-change hooks) · Evidently AI (data drift /
target drift reports) · Poetry + Makefiles for reproducible training
environments · Terraform (intro-level only — `plan`/`apply`/`destroy`
against a single local resource) · GitHub Actions model-quality gates
(reusing the CI skills from Phase 4).

Deliberately **not yet introduced**: Kubernetes-based model serving
(KServe/Seldon/BentoML), a real feature store, full cloud IaC (multi-resource
Terraform modules, remote state, multiple environments — that's Phase 11), a
data warehouse / Spark-scale batch processing, A/B testing and canary-rollout
infrastructure, and a real paging/on-call stack. Each shows up later, at the
moment it solves a felt problem — same rule this whole curriculum has
followed since Phase 1.

This phase also **deliberately drops the daily DSA + SQL grind** carried
through Phases 1–6. Six months of that is in the bank; the next six weeks
are pure MLOps theory + hands-on + project time.

---

## 3. PROJECT — Productionizing StockPilot Demand Forecaster

### Business Problem
Phase 9 built a scikit-learn/XGBoost regression model in a notebook/script
that predicts per-SKU demand from StockPilot's order history, and it scores
well on a held-out split. None of that makes it production-safe. Nobody
tracks which hyperparameters produced which pickle file sitting on someone's
laptop; retraining silently overwrites the previous model with no diff, no
history, and no rollback; there is no scheduled retraining — someone has to
remember to rerun the script next month; nothing checks that predictions
still make sense after StockPilot's order schema changes; and if the
forecast pipeline breaks at 2am, nobody finds out until the owner complains
that this week's reorder suggestions look wrong. This is the concrete
"notebook to production" gap Phase 10 exists to close.

### Requirements

**Functional**
- Every training run logged to MLflow: params, metrics (MAE/RMSE/MAPE on a
  fixed rolling-origin validation split, never a random split for
  time-series data), and artifacts (model file, feature list, a hash of the
  training data snapshot).
- A registered model `stockpilot-demand-forecaster` with `Staging`/
  `Production` stages; promotion is an explicit, auditable action, never an
  implicit side effect of "the script ran."
- A Prefect flow running the full `ingest → build_features → train →
  evaluate → register_if_better` pipeline, scheduled weekly, retryable on
  transient DB read failures.
- Predictions served two ways: a nightly batch job writing
  `forecasted_demand` back into StockPilot's reporting tables, and a
  `POST /forecast` FastAPI endpoint for on-demand queries.
- A drift dashboard comparing this week's live order feature distribution to
  the training reference distribution, visible in the existing Phase-4
  Grafana instance.
- A CI gate blocking a merge if a retrained model's RMSE regresses past a
  documented tolerance versus the current `Production` model.

**Non-functional**
- Retraining is reproducible: same input data + same params → the same
  logged metrics, close enough to catch a silent regression immediately.
- The batch job and the web service always serve the *same* registered
  `Production` version — no drift between "what's in the DB" and "what the
  API answers."
- Nobody can promote a model to `Production` without a logged evaluation
  metric attached to that exact run.

### Architecture (tracking + orchestration + deployment + monitoring, textual)
```
StockPilot Postgres (order_items, stock_movements)
        |
        v
[Prefect flow: demand-forecaster-training]  (weekly schedule)
  ingest_orders -> build_features -> train_model -> evaluate_model -> register_if_better
        |                                                     |
        v (MLflow Tracking: params/metrics/artifacts/run)     v (MLflow Registry: Staging -> Production)
   MLflow Tracking Server (Postgres backend, local Docker)   Production model version
                                                                    |
                        --------------------------------------------  --------------------------------
                        |                                                                             |
                        v                                                                             v
        [batch_score.py — nightly Prefect/cron job]                         [FastAPI /forecast — always-on web service]
          writes forecasted_demand -> StockPilot DB                           loads Production model at container startup
                        |                                                                             |
                        --------------------------------------------  --------------------------------
                                                       v
                              [Evidently drift report -> Prometheus -> Grafana panel]
                                                       |
                                                       v
                        [GitHub Actions: retrain on CI sample, fail job if RMSE regresses]
```

### Testing Strategy
- Unit tests for every feature-transform function (lag features, rolling
  means) against hand-computed expected values.
- Data-validation check run before training: no nulls in required columns,
  price > 0, minimum weeks of history per SKU.
- Integration test: run the full Prefect flow against a small fixture
  dataset, assert a new MLflow run is logged and, if better, a new registry
  version appears.
- CI regression test: retrain on a frozen CI sample, assert RMSE stays
  within tolerance of the last known-good number checked into the repo.
- Contract test: the batch job's written column and the API's response
  schema must agree on units and rounding.

### Monitoring
Evidently's `DataDriftPreset` compares live feature distributions to the
training reference weekly; key metrics (share of drifted columns, PSI) are
exported to Prometheus and shown on a Grafana panel next to the existing
request-latency dashboards. Target drift is monitored by comparing actual
sales in the weeks *after* a forecast to the forecast itself (a calibration
check), not just input drift. A Prefect state-change hook logs a warning
when the training flow fails, the quality gate rejects a retrain, or drift
crosses a documented threshold — a real pager is a later-phase concern.

### Deployment
Batch: a scheduled Prefect deployment runs nightly, scores all active SKUs,
writes back into StockPilot's Postgres. Web service: a FastAPI endpoint
added to StockPilot's existing Docker Compose, loading the current
`Production` model from the registry at container startup (never per
request), redeployed whenever the registry's `Production` version changes.
Both surfaces are stateless with respect to the model file itself — the
registry is the single source of truth for "which model is live."

### Common Interview Questions
1. Where exactly does the "notebook" version of this model stop being
   production-safe — name three concrete failure modes.
2. Why register a model in MLflow instead of committing the pickle file to
   git or S3 directly?
3. How do batch scoring and the web-service endpoint stay in sync on which
   model version is live?
4. What's your rollback plan if a newly promoted `Production` model turns
   out to forecast badly a week in?
5. How do you tell the difference between "the input data drifted" and "the
   model itself decayed"?
6. Why does your CI gate compare against the current `Production` model's
   RMSE instead of a fixed hard-coded threshold?
7. What would you change if StockPilot needed sub-second forecasts instead
   of nightly ones?
8. Walk through what happens, step by step, from a new week of order data
   landing in Postgres to a new model being live in production.

### Possible Improvements
A real feature store instead of recomputing features in both training and
batch scoring; shadow/canary deployment of a newly promoted model before
full cutover; drift-triggered retraining instead of a fixed weekly schedule;
per-SKU models instead of one global model.

### Common Mistakes
Promoting a model to `Production` because "the notebook said the metric
improved," without a repeatable, automated evaluation; letting the batch job
and the web service load the model from two different places (one from a
local file, one from the registry) and silently diverging; treating a green
CI gate as proof there's no drift problem in production; forgetting to pin
the feature-engineering code version alongside the model version — same
model file, different feature code, silently wrong predictions.

---

## 4. PROJECT — Productionizing QuickServe Churn Predictor

### Business Problem
Phase 9's churn classifier flags QuickServe customers likely to stop
ordering, trained once on a historical POS extract. In the notebook,
"training" and "using the model" are the same interactive script run. In
production this breaks immediately: nobody records which features or
decision threshold produced the model a marketing campaign is currently
relying on; retraining happens whenever someone remembers, with no retry if
the POS extract job is mid-write when the script runs; the model has no
living deployment at all — someone runs `predict.py` by hand and emails a
CSV; and nobody would notice if the churn probabilities the model outputs
silently stopped matching reality after QuickServe changed its loyalty
program.

### Requirements

**Functional**
- A full training pipeline as a Prefect flow: ingest POS transaction
  history, build churn-relevant features (recency/frequency/monetary), train,
  evaluate (precision/recall/AUC against a **time-based** held-out split —
  never a random split, to avoid leakage), register.
- A weekly schedule with retry logic specifically on the ingest task, since
  the POS extract job is occasionally still writing when the flow starts.
- Real-time serving via a FastAPI web service — not batch-first — because a
  churn score needs to be available the moment a customer is looked up in a
  support/retention tool, not next morning.
- Drift monitoring on the RFM features and on the predicted
  churn-probability distribution itself.
- A CI quality gate on AUC/recall, matching the pattern built for the
  Demand Forecaster.

**Non-functional**
- Retry logic must not double-process the same POS extract if a retry
  happens after partial ingestion — ingestion must be idempotent per run.
- The web service must fail closed (a clear error, never a stale or wrong
  score) if it can't reach the registry at startup.

### Architecture (tracking + orchestration + deployment + monitoring, textual)
```
QuickServe Postgres (transactions, customers, loyalty_events)
        |
        v
[Prefect flow: churn-predictor-training]  (weekly schedule, retries=3 on ingest)
  ingest_transactions -> build_rfm_features -> train_model -> evaluate_model(AUC/recall) -> register_if_better
        |                                                                    |
        v  MLflow Tracking (shared server)                                  v  MLflow Registry (Staging -> Production)
   Tracking Server                                                   Production model version
                                                                              |
                                                                              v
                                                        [FastAPI /predict/churn — always-on web service]
                                                              loads Production model at startup
                                                                              |
                                                                              v
                                            [Evidently: RFM feature drift + churn-score distribution drift]
                                                                  -> Prometheus -> Grafana
                                                                              |
                                                                              v
                                      [GitHub Actions: retrain on CI sample, fail job if AUC/recall regresses]
```

### Testing Strategy
- Unit tests for RFM feature computation against hand-built customer
  histories.
- Time-based split test: assert the evaluation split never lets a future
  transaction leak into training.
- Idempotency test: run `ingest_transactions` twice against the same raw
  extract, assert the resulting feature table is identical (no duplicate
  rows).
- Integration test: run the full flow against a fixture POS dataset, assert
  a model registers only if it beats the current `Production` AUC.
- API test: `POST /predict/churn` with a known customer profile returns a
  probability in `[0, 1]`, and a 4xx (never a 500) for an unknown
  `customer_id`.

### Monitoring
Evidently reports RFM feature drift weekly, plus a second report tracking
the *distribution of predicted churn probabilities* over time — a rising
average score with no matching rise in actual churn is an early decay
signal. Both live on the same Grafana board as the Demand Forecaster's
panels. A Prefect state-change hook logs a warning if the in-flow quality
check rejects a retrain, as a belt-and-suspenders backup to the GitHub
Actions gate.

### Deployment
Web service only — no batch surface — reflecting the real need for
point-in-time lookup, and the deliberate contrast with the Demand
Forecaster's batch-first design. The FastAPI container loads the
`Production` model at startup and restarts (picking up a new version) via
the same deploy-on-registration pattern built in Week 46.

### Common Interview Questions
1. Why is a random train/test split actively dangerous for a churn model,
   and what do you use instead?
2. Why does this model get a web service while the Demand Forecaster gets a
   nightly batch job?
3. How do you make the ingestion task idempotent, and why does that matter
   specifically for retries?
4. What would you monitor to catch churn-model decay before the business
   notices underperforming marketing campaigns?
5. What happens to in-flight requests if the web service is mid-restart when
   a new model version is promoted?
6. Precision vs. recall for churn — which do you optimize for here, and why?
7. How would you extend this to a real-time streaming score updated on every
   new transaction, and what would that cost?

### Possible Improvements
Shadow-score every prediction against the previous `Production` version to
measure real-world lift before fully cutting over; a feature store shared
with other customer-scoring models; a SHAP-based explainability endpoint for
the retention team.

### Common Mistakes
Evaluating with a random split and getting an optimistic AUC that doesn't
hold up in production; treating "the flow ran" as "the flow succeeded"
without checking the evaluate step actually ran against fresh data;
non-idempotent ingestion causing double-counted transactions after a retry;
serving a model trained on features computed differently than the ones the
live API computes at request time.

---

## 5. PROJECT — Productionizing CarePoint No-Show Predictor

### Business Problem
Phase 9's no-show classifier predicts whether a booked appointment will be a
no-show, trained on CarePoint's historical appointment data with a
tree-based model. As a notebook artifact it can't help staff at all: the
front desk has no risk score before calling to confirm, the clinic manager
has no nightly list of tomorrow's high-risk appointments, and — because
appointment patterns shift with the season and with which doctors are
currently on staff — a model trained once will quietly get worse with no way
to know until someone eyeballs a spike in actual no-shows.

### Requirements

**Functional**
- MLflow-tracked training with registry promotion, the same pattern as the
  other two models.
- A Prefect training flow (`ingest → build_features → train → evaluate →
  register_if_better`).
- **Both** deployment surfaces, built deliberately in parallel so they can
  be compared head-to-head: a nightly batch job producing tomorrow's
  risk-ranked appointment list for staff, and a `POST /predict/no-show-risk`
  web service usable live during a booking call.
- A written decision doc comparing the two for this specific use case, with
  a concrete recommendation on which is the source of truth.
- Drift monitoring on appointment features (lead time, day of week, doctor,
  patient history) plus a quality-gated CI check.

**Non-functional**
- The batch list must be ready before clinic staff arrive each morning — a
  hard, business-driven latency requirement, unlike the Demand Forecaster's
  "eventually, tonight" job.
- The web-service path must respond fast enough to use during the live
  booking call (sub-second), which the batch path is not required to do.

### Architecture (tracking + orchestration + deployment + monitoring, textual)
```
CarePoint Postgres (appointments, patients, doctors)
        |
        v
[Prefect flow: no-show-predictor-training]
  ingest_appointments -> build_features -> train_model -> evaluate_model -> register_if_better
        |                                                             |
        v  MLflow Tracking (shared server)                            v  MLflow Registry (Staging -> Production)
   Tracking Server                                              Production model version
                                                                       |
                    ---------------------------------------------------  ------------------------------------
                    |                                                                                       |
                    v                                                                                       v
    [batch_score.py — nightly, before clinic opens]                              [FastAPI /predict/no-show-risk]
      writes risk-ranked list -> CarePoint staff dashboard                          used live during booking calls
                    |                                                                                       |
                    ---------------------------------------------------  ------------------------------------
                                                        v
                          [Evidently: appointment-feature drift -> Prometheus -> Grafana]
                                                        |
                                                        v
                          [GitHub Actions: retrain on CI sample, fail job if F1/recall regresses]
```

### Testing Strategy
- Unit tests for feature functions (lead-time bucketing, day-of-week/doctor
  encodings) against hand-built appointment fixtures.
- SLA test for the batch job: run it against a realistic-size fixture and
  assert it completes within the time budget before "clinic opens."
- Latency test for the web service: assert p95 response time is within the
  sub-second budget under light concurrent load.
- Integration test comparing predictions from the batch path and the
  web-service path for the *same* appointment on the *same* `Production`
  version — they must agree exactly.
- CI regression test gated on F1/recall — no-show data is class-imbalanced,
  so accuracy alone is explicitly rejected as a gating metric.

### Monitoring
Evidently's drift report on appointment features runs weekly, exported to
the same Grafana board as the other two models. An explicit comparison
panel plots batch-path predictions against web-service-path predictions for
the same day's appointments, to catch the two surfaces silently diverging
(different code path, stale cached model artifact, etc.). Class-imbalance
aware monitoring tracks predicted vs. actual no-show rate over time, not
just a generic drift score.

### Deployment
Both batch and web service were deployed already in Week 47; the Week
49/39 productionization pass hardens whichever the decision doc designates
the source of truth (the web service, since booking-time risk is the
higher-value use case) while keeping the batch list as a convenience view
for staff. Both surfaces pull from the same MLflow Registry `Production`
alias — never two separately-tracked model files.

### Common Interview Questions
1. Why build both batch and web-service deployment for this model instead
   of picking one immediately?
2. What's the concrete cost if the batch job finishes after clinic staff
   have already started their day?
3. Why is accuracy the wrong metric to gate this model's CI check on?
4. How do you detect the batch and web-service paths silently returning
   different scores for the same appointment?
5. What features here are most at risk of drifting when the clinic changes
   which doctors are on staff?
6. If you could keep only one of the two deployment surfaces, which would
   you keep and why?
7. How would this model's monitoring change if CarePoint added a second
   location?

### Possible Improvements
Push web-service predictions into the batch dashboard in real time instead
of maintaining two separate write paths; per-doctor sub-models if drift
analysis shows doctor-specific patterns; an automatic overbooking suggestion
driven directly by the risk score.

### Common Mistakes
Gating CI on accuracy for an imbalanced no-show dataset and getting a
falsely reassuring green check; letting the batch job and web service each
load "the latest model file" from two different places instead of one
shared registry alias; ignoring the SLA (a batch job finishing late) because
the model itself was "correct" — correctness and timeliness are both
requirements here, not just one.

---

## 6. Books & Documentation for This Phase

- MLflow docs: "Tracking" quickstart & concepts, "Model Registry" guide,
  "Deploy MLflow Models" (pyfunc) — Weeks 45 and 36, reused in 38–39.
- Prefect docs: "Flows," "Tasks," "Schedules," "Deployments," "Automations /
  state-change hooks" — Week 46, reused in Weeks 49–50.
- Evidently AI docs: "Get Started," Data Drift report reference — Week 48,
  reused in Weeks 49–50.
- Chip Huyen, *Designing Machine Learning Systems* — Ch. 6 (Model
  Development and Offline Evaluation, Week 45), Ch. 7 (Model Deployment and
  Prediction Service, Week 47), Ch. 8 (Data Distribution Shifts and
  Monitoring, Week 48), Ch. 10 (Infrastructure and Tooling for MLOps, Week
  45).
- Google Cloud Architecture Center: "MLOps: Continuous delivery and
  automation pipelines in machine learning" whitepaper — Week 45 (maturity
  levels).
- Terraform docs: "Get Started" (Docker provider tutorial, intro-level only)
  — Week 48.
- GitHub Actions docs (reused from Phase 4): workflow syntax, required
  status checks / branch protection — Weeks 48–50.
- DataTalksClub `mlops-zoomcamp` repo (github.com/DataTalksClub/mlops-zoomcamp)
  — the module structure (Intro, Experiment-tracking, Orchestration,
  Deployment, Monitoring, Best practices, Project) this whole phase is built
  on; skim the matching module's README the week you hit it, not before.

---

## 7. Weekly Interview Question Sets

**Week 45 — Intro + Experiment Tracking**
1. What are the levels of MLOps maturity (manual → automated pipeline →
   CI/CD), and how do you tell which level a real team is at?
2. What's the difference between an MLflow "run," an "experiment," and a
   registered "model version"?
3. Why register a model instead of just pointing production code at a
   pickle file in S3?
4. What's the tradeoff of a `poetry.lock` for reproducibility versus a
   loose `requirements.txt`?
5. How would you compare 50 hyperparameter runs without eyeballing 50
   dashboards?

**Week 46 — Orchestration**
1. What does a workflow orchestrator give you that a cron job plus a script
   doesn't?
2. Why should `ingest`, `train`, `evaluate`, `register` be separate tasks
   instead of one big function?
3. How do you make a flow retry-safe — what has to be true about a task for
   a retry to be correct?
4. How would you trigger deployment automatically when a new model is
   promoted, without native registry webhooks?
5. What do you look at first in the orchestrator UI when a scheduled run
   silently produced garbage predictions?

**Week 47 — Deployment**
1. Batch vs. web service vs. streaming deployment — how do you decide,
   concretely, for a given SLA?
2. What's the cost of "freshness" in a nightly batch scoring job — walk
   through a scenario where it burns the business?
3. Why load the model once at service startup instead of per request?
4. What breaks first if you routed real-time prediction requests through a
   Kafka consumer instead of a synchronous API?
5. How do you version the *model* independently of the *serving code* that
   wraps it?

**Week 48 — Monitoring + Best Practices**
1. Data drift vs. target drift vs. model decay — precise definitions and how
   you'd detect each.
2. Why can a model with unchanged accuracy still need retraining?
3. What would you unit test in a feature-engineering pipeline that a data
   scientist's notebook never tests?
4. What does a "model-quality gate" in CI actually gate on, and what's the
   risk of setting the tolerance too tight or too loose?
5. Why is Terraform out of scope for a single local MLflow container, and
   when does it start paying for itself?

**Week 49 — Project 1 (Demand Forecaster, full end-to-end)**
1. Walk through your full pipeline for the Demand Forecaster, start to
   finish, failure modes included.
2. Where exactly does "training" end and "deployment" begin in your
   architecture?
3. What's your rollback story if a newly registered model is bad in
   production?
4. What's the single biggest thing you'd change if you rebuilt this from
   scratch?
5. How does your alerting distinguish "the pipeline failed" from "the
   pipeline succeeded but produced a bad model"?

**Week 50 — Projects 2 + 3, Phase Wrap**
1. What did you reuse unchanged between the Churn Predictor and No-Show
   Predictor pipelines, and what genuinely differed?
2. Why does Churn Predictor need a real-time web service while No-Show
   Predictor is fine batch-first?
3. Across all 3 models, what's the one monitoring signal you'd want paged on
   at 3am, and why?
4. What's explicitly deferred to later phases, and why now rather than
   never?
5. If you had to onboard a new model into this same MLOps scaffolding
   tomorrow, how long would it take, and what would you copy first?

---

## 8. Daily Plan — Week 45: MLflow Tracking, Demand Forecaster Instrumentation

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D265)** | MLOps maturity levels & why MLOps | Google Cloud Architecture Center — "MLOps: CD & automation pipelines in ML" §maturity levels | Score your Phase-9 training scripts against the 3 maturity levels (manual → automated pipeline → CI/CD) | New module `mlops/demand-forecaster/`, copy in the Phase-9 training script as-is | None yet — explicitly write down what's untested (no versioned splits, no data validation) | `docs: mlops maturity assessment for demand forecaster` | Q1 | 3.5h |
| **Tue (D266)** | Reproducible environments: Poetry, Makefiles | Poetry docs "Basic usage" | Convert a scratch `requirements.txt` to a pinned `pyproject.toml` with Poetry | Add `pyproject.toml` (poetry) + `Makefile` (`make install`, `make train`, `make test`) to the demand-forecaster module | `make install && make train` runs clean on a fresh clone | `chore: poetry + makefile for reproducible training env` | Q2 | 3.5h |
| **Wed (D267)** | MLflow tracking basics: runs, params, metrics, artifacts | MLflow docs — Tracking Quickstart | Instrument a toy `LinearRegression` script with `mlflow.start_run()`, log 2 params + 1 metric + the model artifact | Wrap the real training script: log hyperparams, MAE/RMSE/MAPE, and artifacts (model, feature list) on every run | Unit test: a training run creates exactly one MLflow run with required keys present | `feat: mlflow tracking on demand-forecaster training` | Q3 | 3.5h |
| **Thu (D268)** | MLflow Model Registry: versioning & staging | MLflow docs — Model Registry guide | Register the toy model, transition it None → Staging → Production via the API | Register `stockpilot-demand-forecaster`, transition the current best run's model to `Staging` | Test: registry has exactly one version in `Staging` after the script runs | `feat: register demand-forecaster model in mlflow registry` | Q4 | 3.5h |
| **Fri (D269)** | Comparing many hyperparameter runs | Huyen, *Designing ML Systems* Ch.6 (Model Development & Offline Evaluation) | Run a 5-point grid search on the toy model, compare runs in the MLflow UI (parallel-coordinates view) | Sweep ~12 demand-forecaster hyperparam combos (XGBoost `max_depth`/`n_estimators`/`learning_rate`), promote the lowest-RMSE run's version to `Production`, archive the rest | Test: exactly one version is in `Production` after the promotion script runs | `feat: hyperparameter sweep + promote best demand-forecaster run to production` | Q5 | 3.5h |
| **Sat (D270)** | **Review** | — | Redo the toy MLflow instrumentation from memory, no notes | Re-read the registered model's run params, verify you can explain every choice made this week | Full test suite re-run | — | Answer all Week-34 questions unscripted | 2.5h |

---

## 9. Daily Plan — Week 46: Orchestration, Churn Predictor Scheduled Flow

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D271)** | Workflow orchestration concepts, DAGs | Prefect docs — "Why Prefect?" + Flows concepts | Write a 3-task toy Prefect flow (`extract → transform → load` on fake data), run it locally | Sketch the churn-predictor DAG (`ingest → train → evaluate → register`) in `docs/`, scaffold `flows/churn_training_flow.py` with empty `@task` stubs | `prefect` runs the stub flow with no errors | `chore: scaffold churn-predictor prefect flow` | Q1 | 3.5h |
| **Tue (D272)** | Building a training pipeline as a DAG | Prefect docs — Flows & Tasks | Add a retry to the toy flow's `transform` task | Implement each task body: `ingest_transactions`, `build_rfm_features`, `train_model`, `evaluate_model`, `register_if_better`, wire them into the flow | Unit test each task function in isolation with fake data | `feat: implement churn-predictor training DAG tasks` | Q2 | 3.5h |
| **Wed (D273)** | Scheduling, retries, parameterized runs | Prefect docs — Schedules + Retries | Add `retries=3, retry_delay_seconds=30` to a toy task that fails twice then succeeds, watch it recover | Add a daily schedule to the churn flow, retry policy on `ingest_transactions` (simulated flaky DB read), parameterize by `training_window_days` | Test: a deliberately-failing ingest task retries the configured number of times before the flow fails | `feat: schedule + retries + parameterized churn training flow` | Q3 | 3.5h |
| **Thu (D274)** | Triggering deployment on new model registration | MLflow docs — Registry stage transitions + Prefect docs on task composition | Write a toy task that polls the registry for the latest `Production` version, prints "would deploy" only if it changed | Add a `maybe_deploy` task at the end of the churn flow: if `register_if_better` promoted a new `Production` version, trigger a stub redeploy task (real deploy logic lands Week 47) | Test: `maybe_deploy` fires the stub only when the version actually changed, not on every run | `feat: trigger stub deploy task on new production model version` | Q4 | 3.5h |
| **Fri (D275)** | Observability of pipeline runs | Prefect docs — UI, states & logging | — | Wire structured logging (reuse `structlog` from Phase 1) inside each task, verify flow-run states/logs are visible end-to-end in the Prefect UI | Run the full flow, confirm every task shows Completed with logs; deliberately break `evaluate_model` to confirm the run shows Failed clearly | `feat: structured logging across churn-predictor flow, verified in prefect ui` | Q5 | 3.5h |
| **Sat (D276)** | **Review** | — | Redo the toy retry-and-recover flow from memory | Re-trace the full churn DAG on paper without opening the code | Full test suite re-run | — | Answer all Week-35 questions unscripted | 2.5h |

---

## 10. Daily Plan — Week 47: Deployment Patterns, No-Show Predictor Dual Deploy

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D277)** | Deployment patterns: batch / web service / streaming | Huyen Ch.7 (Model Deployment & Prediction Service) §batch vs. online | Write comparison notes: latency/cost/complexity for batch vs. web vs. streaming on a toy example | Write `docs/deployment-decision.md` first draft for no-show-predictor: CarePoint's actual need (nightly list vs. booking-time prediction), decide to build both this week to compare directly | — | `docs: deployment pattern comparison for no-show-predictor` | Q1 | 3.5h |
| **Tue (D278)** | Batch scoring job design | MLflow docs — "Deploy MLflow Models" (pyfunc, batch) | Load a registered MLflow model in a toy script, score a 100-row CSV, write predictions to a new CSV | Build `batch_score.py`: loads the Production model from the registry, scores tomorrow's appointments, writes `no_show_risk` back into CarePoint | Test: batch script scores a fixture of appointments, output column shape/range is `[0, 1]` | `feat: no-show-predictor nightly batch scoring job` | Q2 | 3.5h |
| **Wed (D279)** | Web service deployment: FastAPI + Docker | FastAPI docs (reused from Phase 1) + MLflow docs pyfunc serving | — | `POST /predict/no-show-risk` FastAPI endpoint loading the same Production model, Dockerfile, added to CarePoint's compose | Integration test: post a sample appointment payload, assert a probability in `[0, 1]`; test service loads the correct model version at startup | `feat: no-show-predictor fastapi web service + docker` | Q3 | 3.5h |
| **Thu (D280)** | Streaming deployment concept (Kafka consumer) | Huyen Ch.7 §streaming; Phase-3 Kafka notes (reused) | Sketch (don't wire up) a toy Kafka consumer that would score each `appointment.created` event as it arrives | Write `docs/streaming-option.md` + a stubbed `score_appointment_event(event) -> float`; note why a Kafka-consumer deployment isn't adopted this week | Unit test the stub scoring function only | `docs+stub: streaming deployment concept for no-show-predictor (not adopted)` | Q4 | 3.5h |
| **Fri (D281)** | Choosing the right pattern for a given SLA | Huyen Ch.7 §choosing a deployment pattern | — | Finish `docs/deployment-decision.md`: side-by-side batch vs. web-service table (staleness, infra cost, latency, failure mode) with a concrete recommendation — web service as the source of truth at booking time, batch as the staff's daily overview | — | `docs: finalize no-show-predictor deployment decision` | Q5 | 3.5h |
| **Sat (D282)** | **Review** | — | Redo the batch-scoring toy script from memory | Re-read the finished decision doc, argue the opposite recommendation out loud, then explain why you didn't pick it | Full test suite re-run | — | Answer all Week-36 questions unscripted | 2.5h |

---

## 11. Daily Plan — Week 48: Monitoring + Best Practices, Demand Forecaster Drift + CI Gate

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D283)** | ML monitoring concepts: data drift, target drift, model decay | Huyen Ch.8 (Data Distribution Shifts & Monitoring) | Compute a toy PSI (population stability index) between two synthetic distributions | Write `docs/monitoring-plan.md` for demand-forecaster: drift-risk features (seasonality, price changes), what "decay" looks like (RMSE creeping up week over week) | — | `docs: drift & decay monitoring plan for demand-forecaster` | Q1 | 3.5h |
| **Tue (D284)** | Building a drift dashboard with Evidently | Evidently AI docs — Get Started + Data Drift report | Run Evidently's `DataDriftPreset` on two toy dataframes (reference vs. current), view the HTML report | Generate an Evidently drift report comparing demand-forecaster's training reference data vs. last week's live order data; export key metrics as Prometheus-scrapable numbers (reuse Phase 4 Prometheus client) | Test: the metrics-export function returns expected keys for a known drift scenario | `feat: evidently drift report + prometheus metrics export` | Q2 | 3.5h |
| **Wed (D285)** | Testing ML code: feature-transform unit tests, data validation | Huyen Ch.5 (Feature Engineering) §validation; pytest docs (reused) | Write a unit test that catches a broken feature transform (a lag feature shifted by the wrong number of periods) | Add unit tests for every feature-engineering function in demand-forecaster (lag features, rolling means, categorical encodings) + a pre-training data-validation check | Coverage target: the feature module at high coverage, all tests green | `test: unit tests + data validation for demand-forecaster features` | Q3 | 3.5h |
| **Thu (D286)** | CI/CD for ML: model-quality gates in GitHub Actions | GitHub Actions docs (reused, Phase 4) + MLflow docs on comparing run metrics | — | Add a GitHub Actions job that retrains demand-forecaster on a fixed CI dataset sample, compares new RMSE to the current Production model's logged RMSE, fails if it regresses beyond tolerance | Deliberately worsen a feature to prove the gate fails, then fix it and confirm the gate passes | `ci: model-quality gate — fail on rmse regression` | Q4 | 3.5h |
| **Fri (D287)** | IaC intro for ML infra: Terraform | Terraform docs — Get Started (Docker provider tutorial) | Write a minimal Terraform file provisioning one local Docker container (the MLflow tracking server) via the `docker` provider; `plan`/`apply`/`destroy` it | Write (don't necessarily apply to real cloud) a Terraform stub describing the MLflow tracking server + Postgres backend as resources — deliberately shallow, real cloud provisioning explicitly deferred to Phase 11 | `terraform validate` passes; `terraform plan` produces the expected diff against an empty state | `chore: terraform intro stub for mlflow tracking infra (deferred: real cloud in phase 11)` | Q5 | 3.5h |
| **Sat (D288)** | **Review** | — | Redo the toy Evidently drift-report run from memory | Re-read the CI-gate workflow file, explain every step out loud without looking | Full test suite + CI re-run | — | Answer all Week-37 questions unscripted | 2.5h |

---

## 12. Daily Plan — Week 49: Project 1 — Demand Forecaster, Fully Productionized

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D289)** | Consolidating tracking + orchestration for Project 1 | MLflow docs — MLproject packaging; Prefect docs — Deployments | — | Build the full `ingest → train → evaluate → register` Prefect flow for demand-forecaster (mirrors Week 46's churn-flow pattern), wire it to the existing MLflow tracking/registry from Week 45 | End-to-end test: run the whole flow against a small fixture dataset, assert a model lands in the registry | `feat: demand-forecaster full training orchestration (project 1, part 1)` | Q1 | 3.5h |
| **Tue (D290)** | Consolidating deployment (batch + web service) for Project 1 | — (apply Week 47 patterns) | — | Add both the nightly batch scoring job and the FastAPI web-service endpoint for demand-forecaster (mirrors CarePoint's dual deployment), Dockerized, added to StockPilot's compose | Integration tests for both deployment paths | `feat: demand-forecaster batch + web service deployment (project 1, part 2)` | Q2 | 3.5h |
| **Wed (D291)** | Consolidating monitoring + CI gate for Project 1 | — (apply Week 48 patterns) | — | Wire the Evidently drift report + Prometheus export + Grafana dashboard permanently into this module; finalize the CI RMSE-regression gate as a required check on `main` | Confirm the CI gate is a required status check (branch protection); confirm the Grafana panel renders real drift numbers | `feat: demand-forecaster monitoring + ci gate finalized (project 1, part 3)` | Q3 | 3.5h |
| **Thu (D292)** | Hardening: retries, alerting, failure modes | Prefect docs — Automations / state-change hooks | — | Add a Prefect notification/state-change hook that alerts (log line or webhook stub) when the training flow fails, or when a retrain is auto-rejected by the quality gate | Test: a deliberately failing flow triggers the alert hook | `feat: alerting on demand-forecaster pipeline failures` | Q4 | 3.5h |
| **Fri (D293)** | Polish: README, architecture diagram, tagged release | — | — | Write the module's `README.md` (architecture diagram, how to run tracking/orchestration/deployment/monitoring locally), tag `v0.1-mlops-demand-forecaster` | Fresh-clone smoke test — `make install && make train && make serve` all work per the README | `docs: demand-forecaster productionization README + tag v0.1` | Q5 | 3.5h |
| **Sat (D294)** | **Review / Project 1 retrospective** | — | Explain the full tracking → orchestration → deployment → monitoring pipeline out loud, unscripted | Write `docs/retrospective-project1.md`: what took longer than expected, what you'd change to build Projects 2 and 3 faster | Full test suite + CI green | `docs: project 1 retrospective` | Answer all Week-38 questions unscripted | 2.5h |

---

## 13. Daily Plan — Week 50: Project 2 — Churn Predictor, Project 3 — No-Show Predictor, Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D295)** | Project 2 — Churn Predictor: tracking + registry | — (apply Week 45 patterns) | — | Instrument churn-predictor training with MLflow tracking + registry (reuse Week 45's code as a template), register the best model | Same test pattern as Week 45's, adapted to churn-predictor | `feat: churn-predictor mlflow tracking + registry (project 2, part 1)` | Q1 | 3.5h |
| **Tue (D296)** | Project 2 — Churn Predictor: deployment + monitoring | — (apply Weeks 46–48 patterns) | — | Deploy churn-predictor as a FastAPI web service (orchestration flow already exists from Week 46), add the drift-monitoring dashboard (Evidently + Grafana, reusing Week 48's pattern) | Integration tests + drift-report tests | `feat: churn-predictor web service + drift monitoring (project 2, part 2)` | Q2 | 3.5h |
| **Wed (D297)** | Project 2 — Churn Predictor: CI gate, polish, tag | — (apply Week 48's CI-gate pattern) | — | Add the model-quality CI gate, write the README, tag `v0.1-mlops-churn-predictor` | Fresh-clone smoke test | `docs+ci: churn-predictor productionization complete (project 2)` | Q3 | 3.5h |
| **Thu (D298)** | Project 3 — No-Show Predictor: tracking + orchestration | — (apply Weeks 45–46 patterns) | — | Add MLflow tracking/registry **and** a Prefect training flow to no-show-predictor in one sitting (deployment already exists from Week 47) | End-to-end flow test | `feat: no-show-predictor tracking + orchestration (project 3, part 1)` | Q4 | 3.5h |
| **Fri (D299)** | Project 3 — No-Show Predictor: monitoring, CI gate, polish, tag | — (apply Weeks 47–48 patterns) | — | Add the drift dashboard + CI quality gate (reuse Week 48's pattern), write the README, tag `v0.1-mlops-no-show-predictor` | Fresh-clone smoke test covering all 3 deployment surfaces (batch, web, monitoring) | `docs+ci: no-show-predictor productionization complete (project 3)` | Q5 | 3.5h |
| **Sat (D300)** | **Phase 10 wrap review** | — | Explain, unscripted, the full tracking → orchestration → deployment → monitoring pipeline for all 3 models back to back | Write `docs/postmortem-phase10.md` (what's deferred: full IaC/Terraform, Kubernetes-based serving, feature stores, A/B testing infra), tag `v0.10-phase10` | Full test suite + all 3 CI gates green | `docs: phase 10 postmortem + retrospective` | Mock-answer all Phase-10 questions timed | 2.5h |

---

## 14. Deliverables & GitHub Milestones

**Milestone: `Phase 10 — MLOps v0.10`**
- [ ] MLflow tracking + registry wired for all 3 Phase-9 models
- [ ] Prefect training flow (`ingest → train → evaluate → register`) for all
      3 models, scheduled with retries
- [ ] Demand Forecaster: batch + web-service deployment, live
- [ ] Churn Predictor: web-service deployment (real-time), live
- [ ] No-Show Predictor: batch + web-service deployment + written decision
      doc
- [ ] Evidently drift dashboards for all 3 models feeding the existing
      Grafana instance
- [ ] GitHub Actions model-quality CI gate on all 3 models, each proven to
      fail on a deliberate regression and pass after the fix
- [ ] Terraform intro stub for the MLflow tracking server (not applied to
      real cloud — Phase 11 territory)
- [ ] `docs/postmortem-phase10.md` written
- [ ] Tag: `v0.10-phase10`

---

## 15. Skills Acquired Checklist

- [ ] MLOps maturity model — can diagnose a real pipeline's level
- [ ] MLflow tracking (params/metrics/artifacts) on every run, no exceptions
- [ ] MLflow Model Registry — Staging/Production promotion as an explicit,
      auditable step
- [ ] Reproducible environments: Poetry + Makefiles
- [ ] Workflow orchestration with Prefect: flows, tasks, schedules, retries,
      parameterized runs
- [ ] Triggering deployment on new model registration
- [ ] Deployment pattern selection: batch vs. web service vs. streaming,
      defended by SLA
- [ ] Batch scoring job design
- [ ] Web-service model serving (FastAPI + Docker), reusing Phase 1/4 skills
- [ ] Streaming deployment — conceptual fluency (Kafka consumer pattern),
      not yet built for real
- [ ] Data drift / target drift / model decay — precise vocabulary, detected
      with Evidently
- [ ] ML-specific testing: feature-transform unit tests, data validation
- [ ] CI/CD model-quality gates in GitHub Actions
- [ ] IaC — first Terraform touch (intro-level, deliberately shallow)
- [ ] Full end-to-end productionization of 3 real ML models, each faster
      than the last

---

**Next:** say "start Phase 11" when you're ready, or tell me what to adjust
