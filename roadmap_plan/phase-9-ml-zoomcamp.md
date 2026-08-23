# PHASE 9 — Machine Learning Zoomcamp
### Weeks 42–49 · ~3.5h weekdays, ~2.5h Saturdays · 48 working days

---

## 1. Learning Goals

By the end of Phase 9 you can:

- Explain the bias-variance tradeoff and defend a regularization choice
  (Ridge `alpha`, tree `max_depth`, dropout rate) with a validation-curve
  number, not a gut feeling.
- Choose an evaluation metric (RMSE/MAE, precision/recall, ROC-AUC vs
  PR-AUC, an F-beta skewed toward recall) that matches the *business cost*
  of an error, and explain in one sentence why raw accuracy is usually the
  wrong answer once classes are imbalanced.
- Run a full ML pipeline end to end — EDA → feature engineering → baseline
  model → regularized/ensembled model → evaluation → packaged scoring
  service — on three different real business problems drawn from projects
  you already built in Phases 1, 2, and 4.
- Compare linear models, tree ensembles (random forest, XGBoost), and a
  small neural network on the same problem and state the actual tradeoff
  (interpretability, training cost, inference latency, accuracy) instead of
  defaulting to the fanciest option.
- Deploy the same trained model three different ways — a Dockerized
  FastAPI scoring service, AWS Lambda (serverless), and Kubernetes (a raw
  Deployment/Service *and* a KServe `InferenceService`) — and explain the
  operational tradeoffs of each from having actually run them.
- Recognize and avoid the most common ML footguns firsthand: train/test
  leakage (especially time-series leakage and label leakage), evaluating
  under class imbalance with the wrong metric, and skew between
  training-time and inference-time feature engineering.
- Write a model card and a short retrospective that honestly states a
  model's limitations — the same postmortem discipline from Phase 1,
  applied to ML artifacts instead of services.
- Derive gradient descent from the loss function by hand, on paper, before
  ever calling `.fit()` — so "the library minimizes the loss" stops being
  a black box and starts being a specific, checkable claim about a
  specific, checkable formula.

---

## 2. Technologies Introduced This Phase

NumPy-based linear algebra (vectors, matrices, dot products — the
operations every model underneath scikit-learn/Keras is actually doing) ·
calculus for ML (partial derivatives, the chain rule, gradient descent
derived and implemented by hand before ever using a library's `.fit()`) ·
probability & statistics deepened beyond Phase 7's confidence-interval
work (distributions, maximum likelihood estimation, the Bayesian
interpretation of a prior) · scikit-learn (`Pipeline`, preprocessing,
linear models, `model_selection`, metrics) · XGBoost · TensorFlow/Keras
(Sequential/functional API, `keras.applications` transfer learning,
callbacks) · Flask/FastAPI as a model-*scoring* layer (reusing Phase 1/4
API skills, now serving a model artifact instead of business CRUD) ·
Docker (reused, now packaging model artifacts + inference code) · AWS
Lambda (serverless inference) · Kubernetes (reused from Phase 5's `kind`
cluster, extended with HPA and probes tuned for ML workloads) · KServe.

Deliberately **not yet introduced**: MLflow / experiment tracking, feature
stores, data/prediction drift monitoring in production, distributed
training, Airflow-style orchestrated retraining pipelines, A/B-testing
infrastructure for models. You will feel the *lack* of experiment tracking
firsthand this phase — three projects' worth of "wait, which run had that
RMSE?" — which is exactly the itch Phase 10 (MLOps) scratches.

---

## 3. PROJECT 1 — StockPilot Demand Forecaster (Regression)

### Business Problem
StockPilot's owner (Phase 1) still reorders stock by gut feeling. They want
a next-week, per-product demand estimate so reordering stops being
guesswork and stockouts/overordering both go down.

### Requirements
**Functional:** a training pipeline reading StockPilot's own
`order_items`/`stock_movements` history; a per-product forecast; a weekly
retrain script.
**Non-functional:** forecast latency under ~200ms per request; the training
run must be reproducible (fixed seed, versioned model artifact); a forecast
must never be negative.

### Architecture (pipeline)
```
StockPilot Postgres (orders, order_items, products)
  → feature-extraction script (pandas) → weekly per-product feature table
  → training pipeline (scikit-learn Pipeline: preprocessing + Ridge / RandomForestRegressor)
  → model artifact (joblib, versioned) → FastAPI scoring service (Docker)
  → GET /forecast/{product_id}
```

### Data/Feature Design
Lag features (`lag_1`, `lag_2`, `lag_4` weeks of demand), 4-week rolling
mean, category one-hot, price, days-since-last-order, week-of-year
(seasonality proxy). A naive baseline ("demand next week = demand last
week") is computed alongside every model — nothing ships unless it beats
the naive baseline meaningfully.

### Evaluation Metric + Why
RMSE is primary (penalizes large misses that actually cause stockouts);
MAE/MAPE are tracked alongside because they're the numbers you can say out
loud to a shop owner ("we're off by about 4 units on average").

### Deployment Approach
Same FastAPI + Docker scoring-service pattern from Phases 1/4, model
artifact mounted into the image, `/forecast/{product_id}` endpoint, with an
explicit integration point noted into StockPilot's existing
`/reports/low-stock`.

### Common Interview Questions
1. Why is a random train/test split wrong for this data, and what do you do
   instead?
2. Walk through your feature set — which features would leak future
   information if built carelessly?
3. Why RMSE over accuracy-style metrics here, and when would you switch to
   MAPE?
4. How do you handle a brand-new product with zero order history (cold
   start)?
5. What does your naive baseline protect you from as a sanity check?
6. How would forecasting change if StockPilot suddenly had 10,000 SKUs
   instead of a few hundred?

### Possible Improvements
Hierarchical forecasting per category, a holiday/promotion calendar
feature, quantile regression for a safety-stock interval instead of a
single point estimate, MLflow-tracked experiments (Phase 10).

### Common Mistakes
Random-splitting time-series data (future leaks into training); skipping
the naive baseline comparison; forgetting to clip predictions at zero;
retraining without versioning the artifact so you can't reproduce last
week's number.

---

## 4. PROJECT 2 — QuickServe Churn Predictor (Classification)

### Business Problem
QuickServe (Phase 2 POS) wants to flag customers likely to stop ordering so
staff/marketing can intervene (a discount, a text) before losing them for
good.

### Requirements
**Functional:** a churn label definition (e.g. no order in the last 45 days
relative to a customer's historical cadence); a training pipeline; a
nightly batch job producing a ranked "at risk" list; an on-demand
single-customer scoring endpoint.
**Non-functional:** the model must expose a probability, not just a
label, so staff can pick their own threshold; precision on the flagged
list matters more than raw accuracy — a false positive spends real
discount budget.

### Architecture (pipeline)
```
QuickServe Postgres (orders, customers)
  → feature table (recency, frequency, monetary — classic RFM — + tenure)
  → training pipeline (scikit-learn Pipeline: preprocessing + LogisticRegression / XGBoostClassifier)
  → model artifact → FastAPI scoring service (Docker) → POST /predict {customer_id}
  → nightly batch job scores all active customers → at_risk_customers table
```

### Data/Feature Design
Recency (days since last order), frequency (orders per 30 days), monetary
(average basket size), tenure, order-channel mix — deliberately the
classic RFM feature set before reaching for anything fancier.

### Evaluation Metric + Why
ROC-AUC to compare models across the week (threshold-independent); the
actual business decision uses **Precision@K** — the top-N at-risk list
marketing can realistically act on — chosen over plain accuracy because
churn is imbalanced in any given window.

### Deployment Approach
Dockerized FastAPI scoring service (built Week 45), later the subject of
the phase's three-way serving comparison in Week 47 (Lambda / raw K8s
Deployment / KServe).

### Common Interview Questions
1. Why is accuracy misleading here, and what's your actual chosen metric?
2. How do you choose a decision threshold instead of defaulting to 0.5?
3. Where could this feature set leak "future" information if computed at
   the wrong point in time?
4. Compare logistic regression vs XGBoost for this problem — what did you
   actually gain moving to boosting?
5. How would you validate that k-fold CV isn't leaking a customer across
   folds?
6. What would you tell marketing about a customer flagged at 0.6 vs 0.95
   probability?

### Possible Improvements
Reframe as survival analysis (time-to-churn) instead of a fixed-window
binary label; uplift modeling (who churns *and* is actually savable by an
intervention); a shared feature store across projects.

### Common Mistakes
Computing recency/frequency as of "today" instead of as of the label's
reference date (label leakage); picking a threshold without consulting the
business cost of false positives vs false negatives; comparing models on
accuracy under imbalance instead of AUC/precision-recall.

---

## 5. PROJECT 3 — CarePoint No-Show Predictor (Classification + Trees)

### Business Problem
CarePoint (Phase 4 clinic system) loses revenue and appointment slots to
no-shows. Front-desk staff want a daily list of tomorrow's high-risk
appointments so they can call and remind proactively.

### Requirements
**Functional:** a no-show label from appointment status; features from
CarePoint's appointment/patient/reminder data; a nightly batch scoring job
producing a ranked risk list; an on-demand scoring endpoint.
**Non-functional:** must score a full day's appointment volume fast enough
to run nightly; tuned toward **recall** — missing a genuine no-show (an
empty, unfilled slot) costs more than an unnecessary reminder call.

### Architecture (pipeline)
```
CarePoint Postgres (appointments, patients, reminders_sent)
  → feature table (lead time, patient's historical no-show rate, day-of-week/time-of-day, reminder-sent flag, new-vs-returning)
  → training pipeline (LogisticRegression baseline → DecisionTree/XGBoost final, class_weight balanced)
  → model artifact → FastAPI scoring service (Docker) → nightly batch → at_risk_appointments table
```

### Data/Feature Design
Booking-to-appointment lead time, patient's historical no-show rate
(computed strictly *before* the appointment being predicted), day-of-week /
time-of-day, whether a reminder was sent and confirmed, new vs. returning
patient.

### Evaluation Metric + Why
An F-beta score weighted toward recall (or PR-AUC) rather than ROC-AUC or
accuracy — no-shows are the minority class, and the cost asymmetry (a
missed no-show vs. a wasted courtesy call) is the whole point of the
metric choice, same reasoning muscle as Project 2 applied to a different
cost structure.

### Deployment Approach
Reuses the exact FastAPI + Docker scoring-service pattern built twice
already this phase — the point of Project 3 is proving you can move fast
by reusing a pattern, shipped in three days (Week 49, Thu–Sat).

### Common Interview Questions
1. Why recall-oriented here versus precision-oriented for the churn
   predictor — walk through both cost structures.
2. How could "prior no-show rate" leak the label if computed carelessly?
3. How do you turn a probability score into an actionable front-desk
   worklist?
4. How would you handle a brand-new patient with no appointment history?
5. Why treat no-show and cancellation as different classes rather than
   merging them?

### Possible Improvements
An SMS-reminder A/B test fed back in as an intervention feature, calibrated
probabilities for a true risk score (not just a ranking), pooling data
across multiple clinic locations.

### Common Mistakes
Computing the historical no-show rate using data that includes the
appointment currently being predicted (label leakage); conflating no-shows
with cancellations; optimizing purely for AUC without ever asking the
front-desk staff what an "actionable" list should look like.

---

## 6. Books & Documentation for This Phase

- 3Blue1Brown "Essence of Linear Algebra" (free video series) — Week 42.
- Khan Academy "Multivariable calculus," partial derivatives + gradient
  sections (free) — Week 42.
- Christopher Bishop, *Pattern Recognition and Machine Learning* §1.2
  (Probability Theory / MLE) — or any free equivalent MLE treatment —
  Week 42.
- DataTalksClub *Machine Learning Zoomcamp*
  (github.com/DataTalksClub/machine-learning-zoomcamp) — modules: Intro to
  ML, Regression, Classification, Evaluation Metrics, Deployment, Trees
  (Decision Trees & Ensembles), Neural Networks & Deep Learning,
  Serverless, Kubernetes & KServe. Read the matching module the same week
  you use it, same discipline as Phase 1's Fluent Python chapters.
- *Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow*
  (Aurélien Géron) — Ch.2 (End-to-End Machine Learning Project), Ch.4
  (Training Models: Normal Equation, Ridge/Lasso), Ch.6 (Decision Trees),
  Ch.7 (Ensemble Learning and Random Forests), Ch.10–11 (Neural Networks,
  Training Deep Neural Networks), Ch.14 (Deep Computer Vision / CNNs).
- scikit-learn official docs — "Preprocessing data," "Model evaluation:
  quantifying the quality of predictions," "Cross-validation," "Choosing
  the right estimator."
- XGBoost docs — "Introduction to Boosted Trees," "Python Package
  Introduction."
- Keras/TensorFlow docs — "Transfer learning & fine-tuning," "Training &
  evaluation with the built-in methods," "Writing your own callbacks."
- AWS Lambda docs — "Building Lambda functions with Python," container
  image packaging for Lambda.
- Kubernetes docs — "Deployments," "Services," "HorizontalPodAutoscaler
  Walkthrough," "Configure Liveness, Readiness and Startup Probes" (reused
  and extended from Phase 5).
- KServe docs — "Getting Started," the `InferenceService` concept guide.

---

## 7. Weekly Interview Question Sets

**Week 42 — ML math foundations**
1. Derive the gradient of MSE with respect to the weight vector, from
   memory, on a whiteboard.
2. Why does gradient descent move in the direction of the *negative*
   gradient?
3. What does it mean, precisely, for logistic regression's loss to be the
   maximum-likelihood estimate under a Bernoulli model?
4. What is L2 regularization, in Bayesian terms — what prior does it
   correspond to, and why does a smaller `alpha` mean a wider prior?
5. Why derive gradient descent by hand once, when `sklearn`/`Keras` will
   always do it for you in practice?

**Week 43 — Intro to ML, Regression**
1. Explain the bias-variance tradeoff and how regularization addresses it.
2. Why split into train/validation/test instead of just train/test, and
   what leaks if you tune hyperparameters using the test set?
3. Explain the normal equation solution for linear regression — when does
   it become impractical?
4. Why is RMSE reasonable for demand forecasting, and when would you
   prefer MAE or MAPE instead?
5. What's the difference between L1 and L2 regularization in terms of the
   resulting coefficients?

**Week 44 — Classification, Evaluation**
1. Why is accuracy a bad metric for churn prediction, and what would you
   use instead?
2. Precision vs recall — for churn, which do you optimize for and why?
3. What does ROC-AUC actually measure, and when is it misleading under
   severe class imbalance?
4. Explain k-fold cross-validation and how a customer could leak across
   folds if you're not careful.
5. Name two ways to handle class imbalance and their tradeoffs.

**Week 45 — Deployment, Trees**
1. Compare a single decision tree, a random forest, and gradient boosting
   — what does each add over the last?
2. Why does a random forest reduce variance compared to one tree?
3. What's the tradeoff between a self-managed Dockerized scoring service
   and a managed model-serving platform?
4. How do you keep training-time and inference-time feature engineering
   from drifting apart?
5. Your Dockerized model service is fast in dev but slow in production —
   what do you check first?

**Week 46 — Deep Learning**
1. Why does transfer learning work — what is the pretrained network
   actually reusing?
2. What problem does dropout solve, and why does it apply only during
   training?
3. Convolution vs. a fully-connected layer for images — why is convolution
   the right inductive bias?
4. What's the purpose of early stopping and how do you pick the monitored
   metric?
5. When would a small CNN trained from scratch beat a fine-tuned
   pretrained model, and when would it lose?

**Week 47 — Serverless, Kubernetes, KServe**
1. What causes a Lambda cold start for an ML model, and how do you
   mitigate it?
2. Compare a raw Kubernetes Deployment vs. KServe for model serving — what
   does KServe give you for free?
3. Why does horizontal pod autoscaling need a good readiness probe
   specifically for ML workloads?
4. What are the cost/ops tradeoffs between serverless and a standing
   Kubernetes cluster for model serving?
5. How would you roll out a new model version with zero downtime and an
   easy rollback?

**Week 48 — Finalizing a Regression Project**
1. How do you decide a model is "good enough to ship" for a small-business
   forecasting use case?
2. What belongs in a model card, and why does "intended use / limitations"
   matter as much as the headline metric?
3. How would you detect the demand forecaster degrading in production
   before new ground-truth labels even arrive?
4. Why might you deliberately ship a simpler, slightly-less-accurate model
   over a marginally-better black box?
5. What triggers an out-of-cycle retrain, versus your normal retrain
   cadence?

**Week 49 — Shipping Two Projects Fast**
1. What's the minimum viable CI check for a model repo beyond lint/test —
   what does a "model regression test" actually verify?
2. For an imbalanced no-show problem, how do you pick a decision threshold
   instead of defaulting to 0.5?
3. What did formalizing the churn predictor into a `Pipeline` object buy
   you over ad hoc scripts?
4. Across all three projects this phase, which evaluation-metric choice
   are you most prepared to defend in an interview, and why?
5. With one more week, which of the three projects would you invest it in,
   and what specifically would you do?

---

## 8. Daily Plan — Week 42: ML Math Foundations

*Why this week exists: Phase 9 as originally scoped is deliberately
applied — `.fit()`, evaluate, deploy — which is the right pace for a
first pass, but it leaves "the library minimizes the loss" as a black
box. This week derives the machinery by hand, once, so every `.fit()`
call for the rest of the phase is a specific claim about a specific
formula you could reproduce, not incantation.*

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D247) | Linear algebra for ML: vectors, matrices, dot products, the geometric intuition behind "a model is a function of a weight vector" | 3Blue1Brown "Essence of Linear Algebra" (free video series) Ch.1-4, or Ch.1-2 of any standard linear algebra text | Implement matrix multiplication from scratch in pure Python (no NumPy), then again with NumPy, compare correctness and timing | `docs/ml-math-notes.md` — vectors/matrices section, in your own words, with the StockPilot feature vector as a concrete running example | Test your from-scratch matmul against `numpy.matmul` on random matrices for equality | `docs: linear algebra foundations + matmul from scratch` | Q1 | 3.5h |
| Tue (D248) | Calculus for ML: partial derivatives, the chain rule, why gradients point in the direction of steepest ascent | Khan Academy "Multivariable calculus" (free) — partial derivatives + gradient sections | Derive, on paper, the gradient of Mean Squared Error with respect to the weight vector for linear regression — no code yet, just the math | Add the derivation to `docs/ml-math-notes.md`, typed out step by step | — | `docs: mse gradient derived by hand` | Q2 | 3.5h |
| Wed (D249) | Gradient descent, implemented from scratch | — | Implement batch gradient descent for linear regression using only NumPy (no scikit-learn), converge on a toy dataset, plot the loss curve | Reproduce Phase 9 Week 43's upcoming baseline linear regression using your own from-scratch gradient descent instead of the normal equation, verify the learned weights match closely | Test: your from-scratch gradient descent converges to weights within a small tolerance of `sklearn.LinearRegression`'s closed-form solution on the same toy data | `feat: linear regression via from-scratch gradient descent` | Q3 | 4h |
| Thu (D250) | Probability & statistics deepened: distributions, maximum likelihood estimation | Any intro-statistics MLE chapter (e.g. Bishop's *Pattern Recognition and Machine Learning* §1.2, or a free equivalent) | Derive logistic regression's cross-entropy loss as the maximum-likelihood estimate under a Bernoulli model — on paper, then confirm numerically that maximizing likelihood equals minimizing the cross-entropy you already know from Phase 7/9 | Add the MLE derivation to `docs/ml-math-notes.md`, tied explicitly to the logistic regression you'll build in Week 44 | — | `docs: mle derivation for logistic regression loss` | Q4 | 3.5h |
| Fri (D251) | The Bayesian view: priors, posteriors, and what L2 regularization actually is | — | Show, numerically, that Ridge regression's solution is the MAP (maximum a posteriori) estimate under a Gaussian prior on the weights — vary the prior's variance and watch it match `alpha` | Implement Ridge regression from scratch via gradient descent (extending Wednesday's code with the L2 penalty term), compare coefficients against `sklearn.Ridge` on the same data | Test: your from-scratch Ridge coefficients match `sklearn.Ridge`'s within a small tolerance across 3 different `alpha` values | `feat: ridge regression from scratch, matches sklearn` | Q5 | 4h |
| Sat (D252) | **Review** | — | Redo Tuesday's MSE gradient derivation from memory, on paper, no notes | Re-read `docs/ml-math-notes.md` end to end, confirm every claim in it is something you could reproduce on a whiteboard | Full suite re-run (all from-scratch implementations) | — | Answer Week-42 Qs unscripted | 2.5h |

---

## 9. Daily Plan — Week 43: Intro to ML, Linear Regression, StockPilot Demand Forecaster

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D253)** | Supervised learning framing, CRISP-DM, train/val/test split | ML Zoomcamp Module 1 — Intro to ML; Géron Ch.2 "Look at the Big Picture" | Implement a train/val/test split function from scratch on a toy dataset | EDA on StockPilot's historical order data; aggregate weekly per-product demand | Test the split preserves proportions and leaks no rows across sets | `feat: demand forecaster - eda + train/val/test split` | Q1 | 3.5h |
| **Tue (D254)** | NumPy/Pandas refresher, missing data, groupby aggregation | Pandas docs "Working with missing data"; Géron Ch.2 data-cleaning section | Pandas groupby/aggregation drill on toy sales data | Build the weekly per-product feature table joining products + order_items + stock_movements | Unit test feature-table shape and confirm no NaNs leak through | `feat: feature table construction for demand forecaster` | Q2 | 3.5h |
| **Wed (D255)** | Linear regression from scratch (normal equation) | ML Zoomcamp Module 2 — Regression; Géron Ch.4 "The Normal Equation" | Implement normal-equation regression with NumPy on toy data, compare to `sklearn.LinearRegression` | Baseline linear regression predicting next-week demand from lag features | Unit test RMSE computed correctly; model reproducible with a fixed seed | `feat: baseline linear regression demand model` | Q3 | 3.5h |
| **Thu (D256)** | Feature engineering, one-hot encoding | scikit-learn docs "Preprocessing data" (OneHotEncoder); Géron Ch.2 categorical encoding | Encode a categorical column with `OneHotEncoder` vs `pd.get_dummies`, compare output | Add category/supplier one-hot features and a week-of-year seasonality feature | Test the feature pipeline is identical between train and inference (no train/test skew) | `feat: one-hot + seasonal features for demand model` | Q4 | 3.5h |
| **Fri (D257)** | Regularization (Ridge), RMSE evaluation, bias-variance in practice | ML Zoomcamp Module 2 — Regularized Linear Models; Géron Ch.4 "Ridge Regression" | Plot train vs. validation RMSE across Ridge `alpha` values (a learning curve) | Add Ridge regularization, tune `alpha` on the validation set, record final Week-43 RMSE vs. naive baseline | Test the regularized model beats the naive baseline by a defined margin | `feat: ridge-regularized demand model + evaluation` | Q5 | 3.5h |
| **Sat (D258)** | **Review** | — | Redo the normal-equation regression from memory, no notes | Re-read the feature table for anything that smells like leaked future information | Full suite re-run | — | Answer all 5 Week-43 questions out loud, unscripted | 2.5h |

---

## 10. Daily Plan — Week 44: Classification, Evaluation, QuickServe Churn Predictor

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D259)** | Logistic regression, sigmoid, log-loss | ML Zoomcamp Module 3 — Classification; Géron Ch.4 "Logistic Regression" | Implement sigmoid + log-loss manually, verify against `sklearn` | EDA on QuickServe customer order history; define the churn label (no repeat order within a cadence window) | Test the churn label computes correctly on a synthetic customer timeline | `feat: churn predictor - eda + churn label definition` | Q1 | 3.5h |
| **Tue (D260)** | Feature importance via coefficients | scikit-learn docs LogisticRegression; Géron Ch.4 coefficient interpretation | Fit logistic regression on toy data, inspect and plot coefficients | Build the RFM feature table (recency, frequency, monetary, tenure) + baseline logistic regression churn model | Unit test the feature table and confirm model output is a valid probability in [0,1] | `feat: baseline logistic regression churn model` | Q2 | 3.5h |
| **Wed (D261)** | Evaluation pitfalls — the accuracy trap, confusion matrix, precision/recall | ML Zoomcamp Module 4 — Evaluation Metrics; scikit-learn docs "Model evaluation" | Compute a confusion matrix and precision/recall by hand on a small prediction set, verify against `sklearn` | Evaluate the churn model with confusion matrix + precision/recall; document why accuracy is misleading here | Test precision/recall helper functions against known cases | `feat: precision/recall evaluation for churn model` | Q3 | 3.5h |
| **Thu (D262)** | ROC/AUC, k-fold cross-validation | ML Zoomcamp Module 4 — ROC/AUC; scikit-learn docs "Cross-validation" | Plot an ROC curve for a toy classifier, compute AUC manually vs. `sklearn` | Add k-fold CV to churn-model training, report mean/std AUC across folds | Test the CV split is customer-aware and doesn't leak a customer across folds | `feat: k-fold cv + roc/auc evaluation for churn model` | Q4 | 3.5h |
| **Fri (D263)** | Class imbalance handling | ML Zoomcamp Module 4 imbalance notes; scikit-learn docs `class_weight` parameter | Compare `class_weight='balanced'` vs. undersampling on a toy imbalanced dataset | Apply class-weight balancing to the churn model, re-evaluate precision/recall/AUC, pick the Week-44 final model | Test the class-weighted model improves recall on the minority (churn) class vs. baseline | `feat: class-imbalance-aware churn model, week 44 final` | Q5 | 3.5h |
| **Sat (D264)** | **Review** | — | Redo the manual confusion-matrix calculation from memory | Re-read the Week-44 model comparison notes for anything you'd argue differently now | Full suite re-run | — | Answer all 5 Week-44 questions out loud, unscripted | 2.5h |

---

## 11. Daily Plan — Week 45: Deployment, Trees, Churn Predictor Dockerized + Ensembles

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D265)** | Deployment patterns recap — Flask/FastAPI + Docker for model serving | Flask docs "Quickstart"; FastAPI docs (recap) | Minimal FastAPI `/predict` endpoint serving a pickled sklearn model, hit it with curl | Wrap the Week-44 churn model in a FastAPI scoring service (`/predict` with a Pydantic request/response schema) | Integration test hitting `/predict` with a sample payload, assert response shape and probability range | `feat: churn model fastapi scoring service` | Q1 | 3.5h |
| **Tue (D266)** | Containerizing the model service | Docker docs "Best practices for writing Dockerfiles" (model-artifact angle) | Write a multi-stage Dockerfile for the scoring service, check the resulting image size | docker-compose for the churn scoring service, with a `/health` endpoint | Test the container starts and `/health` returns 200 | `chore: dockerize churn scoring service` | Q2 | 3.5h |
| **Wed (D267)** | Decision trees | ML Zoomcamp Module 6 — Decision Trees; Géron Ch.6 | Fit a `DecisionTreeClassifier` on toy data, visualize it, discuss overfitting via `max_depth` | Rebuild the churn model as a decision tree; compare AUC/precision-recall against Week 44's logistic regression on the same held-out fold | Test the tree respects the `max_depth` constraint | `feat: decision-tree churn model + comparison` | Q3 | 3.5h |
| **Thu (D268)** | Random forests / ensembling (bagging) | ML Zoomcamp Module 6 — Random Forest; Géron Ch.7 | Bagging demo: train 10 trees on bootstrap samples, average predictions, compare variance to a single tree | Build a `RandomForestClassifier` churn model, tune `n_estimators`/`max_depth` via CV | Test the forest model beats the single tree on validation AUC | `feat: random forest churn model` | Q4 | 3.5h |
| **Fri (D269)** | Gradient boosting (XGBoost) | XGBoost docs "Introduction to Boosted Trees"; ML Zoomcamp Module 6 — XGBoost | Fit an `XGBClassifier` on toy data, plot feature importances | Build an XGBoost churn model; final comparison table (logreg vs. tree vs. forest vs. XGBoost); wire the winner into the scoring service | Test the scoring service now loads the XGBoost artifact and matches an offline batch score | `feat: xgboost churn model + finalize scoring service model choice` | Q5 | 3.5h |
| **Sat (D270)** | **Review** | — | Redo the bagging demo from memory, explain variance reduction out loud | Re-read the model comparison table and confirm the winner is justified, not just the last one tried | Full suite re-run | — | Answer all 5 Week-45 questions out loud, unscripted | 2.5h |

---

## 12. Daily Plan — Week 46: Deep Learning, CarePoint Document-Image Classifier

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D271)** | Neural network basics — layers, activations, backprop intuition | ML Zoomcamp "Neural Networks & Deep Learning" module; Géron Ch.10 | Forward-pass-only tiny dense net in NumPy on toy data | Assemble a labeled CarePoint scanned-document dataset (referral letter, insurance card, lab result, prescription) + data-loading pipeline | Test the loader produces correctly shaped and labeled batches | `feat: carepoint doc-image classifier - dataset + loader` | Q1 | 3.5h |
| **Tue (D272)** | CNNs — convolution, pooling | ML Zoomcamp CNN section; Géron Ch.14 | Build a tiny CNN in Keras on a toy image dataset, train a few epochs | Define and train a baseline CNN for CarePoint document-type classification, log accuracy | Test model output shape equals the number of classes and training loss decreases over the first epochs | `feat: baseline cnn for document classification` | Q2 | 3.5h |
| **Wed (D273)** | Transfer learning | Keras docs "Transfer learning & fine-tuning"; ML Zoomcamp transfer-learning section | Load a pretrained model via `keras.applications`, freeze the base, fine-tune the head on toy data | Replace the baseline CNN with a pretrained-base + custom-head model for the document classifier, compare accuracy to Tuesday's baseline | Test that base layers are frozen (`trainable=False`) and only the head trains | `feat: transfer-learning document classifier` | Q3 | 3.5h |
| **Thu (D274)** | Keras training-loop internals — callbacks, checkpoints | Keras docs "Training & evaluation with the built-in methods"; "Writing your own callbacks" | Add `EarlyStopping` + `ModelCheckpoint` to a toy training loop | Add early stopping and best-model checkpointing to the document classifier's training run, retrain | Test the checkpoint file is written and reloadable, and the reloaded model matches the saved validation accuracy | `feat: training callbacks + checkpointing for document classifier` | Q4 | 3.5h |
| **Fri (D275)** | Regularization/dropout for deep nets | Géron Ch.11 regularization section; Keras docs on image augmentation | Add `Dropout` layers to the toy CNN, compare the train/val gap with vs. without | Add dropout + data augmentation to the document classifier, final model selection, evaluate on a held-out test set, write a short model card | Test the augmentation pipeline varies images per epoch and final test accuracy clears a defined threshold | `feat: dropout + augmentation, finalize document classifier` | Q5 | 3.5h |
| **Sat (D276)** | **Review** | — | Redo the transfer-learning freeze/fine-tune setup from memory | Re-read the model card and confirm the stated limitations are actually true | Full suite re-run | — | Answer all 5 Week-46 questions out loud, unscripted | 2.5h |

---

## 13. Daily Plan — Week 47: Serverless, Kubernetes, KServe — Three-Way Deployment

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D277)** | AWS Lambda / serverless model serving concepts | AWS Lambda docs "Building Lambda functions with Python"; ML Zoomcamp Module 8 — Serverless | Package a tiny sklearn model + Lambda handler locally, invoke it | Convert the churn model to a Lambda-compatible handler (model loaded once outside the handler, cold-start aware) | Test the handler returns the correct prediction shape for a sample event payload | `feat: serverless lambda handler for model serving` | Q1 | 3.5h |
| **Tue (D278)** | Lightweight-inference packaging, cold-start tradeoffs | AWS Lambda docs "Container images"; ML Zoomcamp Module 8 | Measure cold-start latency of the local handler across a few repeated invokes | Package the model as a Lambda container image, deploy locally (SAM/LocalStack), measure invoke latency | Test warm-start invocation latency stays under a defined budget | `chore: package model as lambda container image` | Q2 | 3.5h |
| **Wed (D279)** | Kubernetes deployment of a model service (reusing Phase 5's `kind` cluster) | Kubernetes docs "Deployments" + "Services" (recap) | — | Write Deployment + Service YAML for the FastAPI scoring service (Week 45's image), deploy to the local `kind` cluster | Test `kubectl get pods` shows Running and curling through the Service returns a prediction | `feat: k8s deployment+service for model scoring api` | Q3 | 3.5h |
| **Thu (D280)** | Scaling the K8s model service — HPA, readiness/liveness probes for ML pods | Kubernetes docs "HorizontalPodAutoscaler Walkthrough"; "Configure Liveness, Readiness and Startup Probes" | — | Add readiness/liveness probes tuned to model load time, add an HPA based on CPU, lightly load-test to confirm scale-out | Test the readiness probe fails until the model is loaded and passes once it is | `feat: readiness/liveness probes + hpa for model service` | Q4 | 3.5h |
| **Fri (D281)** | KServe model serving on Kubernetes | KServe docs "Getting Started" / `InferenceService` concept guide | — | Install KServe on the `kind` cluster, deploy the model as an `InferenceService`, hit its predict endpoint; write `docs/serving-comparison.md` (Lambda vs. raw K8s Deployment vs. KServe: cold start, ops overhead, autoscaling, cost story) | Test the `InferenceService` reports Ready and the predict endpoint returns the expected schema | `feat: kserve inferenceservice + serving comparison writeup` | Q5 | 3.5h |
| **Sat (D282)** | **Review** | — | Explain the Lambda-vs-K8s-vs-KServe tradeoffs out loud, unscripted | Re-read `docs/serving-comparison.md` for anything you'd argue differently now | Full suite re-run across all three deployments | — | Answer all 5 Week-47 questions out loud, unscripted | 2.5h |

---

## 14. Daily Plan — Week 48: Project 1 Finalize — StockPilot Demand Forecaster

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D283)** | Revisit and polish EDA + feature set | Géron Ch.2 "Fine-Tune Your Model" (recap); ML Zoomcamp Regression module (recap) | — | Re-run EDA with fresh eyes; prune/expand features (rolling averages, promotions flag); document data assumptions in the README | Re-run the full Week-43 test suite, confirm still green after feature changes | `refactor: polish demand forecaster eda + feature set` | Q1 | 3.5h |
| **Tue (D284)** | Final model selection (linear/Ridge vs. tree-based regressor) | scikit-learn docs "Choosing the right estimator"; XGBoost docs regression-objective section | — | Train/compare 3-4 candidate regressors with consistent CV; pick the winner by RMSE plus a stated business rationale (interpretability vs. accuracy for a small shop owner) | Test the model-selection script is deterministic and reproducible with a fixed seed | `feat: final model selection for demand forecaster` | Q2 | 3.5h |
| **Wed (D285)** | Deployment | FastAPI docs (recap); Docker docs (recap) | — | Wrap the final demand model in the same FastAPI-scoring-service pattern from Week 45, dockerize, wire an integration point into StockPilot's `/products/{id}/forecast` | Integration test the forecast endpoint returns a plausible non-negative number for a known product | `feat: dockerized demand forecaster scoring service` | Q3 | 3.5h |
| **Thu (D286)** | README + model card | Model-card guidance (Google Model Cards overview); scikit-learn docs "Model persistence" | — | Write `README.md` (setup/run) and `docs/model-card.md` (training data, features, metric, known limitations, intended use) | Verify the README's instructions actually work on a clean checkout | `docs: readme + model card for demand forecaster` | Q4 | 3.5h |
| **Fri (D287)** | Retrospective + improvements write-up | — | — | Write `docs/postmortem-demand-forecaster.md` (more history, holiday effects, hierarchical forecasting, MLflow foreshadowing Phase 10); tag `v0.1-demand-forecaster` | Full suite + CI green | `docs: demand forecaster retrospective, tag v0.1-demand-forecaster` | Q5 | 3.5h |
| **Sat (D288)** | **Review** | — | Explain the full demand-forecaster pipeline end to end, out loud, unscripted | Re-read the postmortem and confirm every "deferred" item is genuinely deferred, not silently done | Full suite + CI re-run | — | Answer all 5 Week-48 questions out loud, unscripted | 2.5h |

---

## 15. Daily Plan — Week 49: Project 2 Finalize + Project 3 — Churn Predictor & CarePoint No-Show Predictor

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D289)** | Formalize the churn predictor's training pipeline | scikit-learn docs "Pipeline and FeatureUnion" (recap); XGBoost docs "Python Package Introduction" | — | Refactor Weeks 44-45's churn work into a clean `training.py` (sklearn `Pipeline`: preprocessing + model) + a `predict_service` package; re-save the winning XGBoost model | Regression test that the training pipeline reproduces the same metrics as Week 45 | `refactor: formalize churn predictor training pipeline` | Q1 | 3.5h |
| **Tue (D290)** | Testing + CI for the churn predictor | pytest docs (recap); GitHub Actions docs (recap, ML-artifact caching angle) | — | Add unit tests (feature engineering, evaluation metrics) + a CI workflow that retrains on a sample and asserts AUC clears a threshold ("model regression test") | CI green on a clean clone | `test: ci pipeline + model regression test for churn predictor` | Q2 | 3.5h |
| **Wed (D291)** | Documentation + ship | — | — | README + model card for the churn predictor; finalize the Week-45 Dockerized scoring service; tag `v0.1-churn-predictor` | Full suite + container smoke test | `docs: churn predictor readme + model card, tag v0.1-churn-predictor` | Q3 | 3.5h |
| **Thu (D292)** | CarePoint No-Show Predictor — EDA + baseline | ML Zoomcamp Classification + Trees modules (recap); Géron Ch.6/7 (recap) | — | EDA on CarePoint appointment data; define the no-show label; engineer features (lead time, prior no-show rate, day-of-week, reminder-sent flag); baseline logistic regression + decision tree comparison | Unit test the label and feature-engineering functions | `feat: no-show predictor - eda + baseline models` | Q4 | 3.5h |
| **Fri (D293)** | No-Show Predictor — final model + deployment | XGBoost docs (recap) | — | Train an XGBoost no-show model (class-weight balanced); evaluate with a recall-weighted metric; wrap in a FastAPI scoring service, dockerize, README + model card; tag `v0.1-noshow-predictor` | Integration test the `/predict` endpoint; CI green | `feat: xgboost no-show model + dockerized scoring service, tag v0.1-noshow-predictor` | Q5 | 3.5h |
| **Sat (D294)** | **Phase-wide review** | — | Explain, unscripted, why each of the three projects picked the metric it picked | `docs/postmortem-phase9.md` — full phase retrospective across all 3 projects and all 3 serving methods; tag `v0.9-phase9` | Full suite across all three services | `docs: phase 9 retrospective, tag v0.9-phase9` | Full mock: answer all 35 Phase-9 interview questions back to back, timed | 2.5h |

---

## 16. Deliverables & GitHub Milestones

**Milestone: `Phase 9 — ML Zoomcamp v0.1`**
- [ ] `docs/ml-math-notes.md`: linear algebra, the MSE gradient derived by
      hand, gradient descent implemented from scratch and verified against
      `sklearn.LinearRegression`, MLE derivation for logistic regression's
      loss, and Ridge regression from scratch matching `sklearn.Ridge`
      within tolerance across 3 `alpha` values
- [ ] StockPilot Demand Forecaster: EDA, feature-engineered regression
      pipeline (Ridge + tree-based comparison), beats the naive baseline on
      RMSE, Dockerized scoring service, README + model card, tag
      `v0.1-demand-forecaster`
- [ ] QuickServe Churn Predictor: baseline logistic regression through
      tuned XGBoost, k-fold CV + AUC/precision-recall evaluation,
      class-imbalance handling, formal `Pipeline`-based training script +
      CI model-regression test, Dockerized scoring service, tag
      `v0.1-churn-predictor`
- [ ] The same model deployed three ways — AWS Lambda, a raw Kubernetes
      Deployment/Service, and a KServe `InferenceService` — with
      `docs/serving-comparison.md` written
- [ ] CarePoint document-image classifier: baseline CNN → transfer-learning
      model, dropout + augmentation, checkpointing, short model card
- [ ] CarePoint No-Show Predictor: EDA → baseline → XGBoost, recall-weighted
      evaluation, Dockerized scoring service, README + model card, tag
      `v0.1-noshow-predictor`
- [ ] `docs/postmortem-phase9.md` phase-wide retrospective written, tag
      `v0.9-phase9`

---

## 17. Skills Acquired Checklist

- [ ] Linear algebra, calculus, and probability/statistics foundations for
      ML — gradient descent, MLE, and the Bayesian view of L2
      regularization, each derived by hand and verified against a library
- [ ] Train/validation/test split discipline, incl. time-series-aware
      splitting
- [ ] Linear regression from first principles (normal equation) through
      Ridge regularization
- [ ] Feature engineering: lag/rolling features, one-hot encoding, RFM
      features
- [ ] Logistic regression, sigmoid, log-loss — conceptual and applied
      fluency
- [ ] Evaluation metric selection matched to business cost: RMSE/MAE,
      confusion matrix, precision/recall, ROC-AUC vs. PR-AUC, F-beta
- [ ] k-fold cross-validation, done leakage-aware
- [ ] Class-imbalance handling (`class_weight`, threshold selection)
- [ ] Decision trees, random forests, gradient boosting (XGBoost) — applied
      and compared on the same problem
- [ ] Packaging a trained model as a Flask/FastAPI scoring service, then
      Dockerizing it
- [ ] Neural network basics, CNNs, transfer learning, dropout/augmentation,
      Keras callbacks
- [ ] Serverless model inference on AWS Lambda, incl. cold-start awareness
- [ ] Kubernetes model serving: Deployment/Service, HPA, readiness/liveness
      probes tuned for ML workloads
- [ ] KServe `InferenceService` deployment
- [ ] Writing a model card and an honest ML-project retrospective

---

**Next:** say "start Phase 10" when you're ready, or tell me what to adjust
