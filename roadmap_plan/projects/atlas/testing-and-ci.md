# Testing and CI across Atlas

| | |
|---|---|
| **Covers** | Season 1, stages [S0](stage-00-bootstrap.md) to [S12](stage-12-data-at-scale-fraud.md); Season 2 reuses the same pipeline ([season-2.md](season-2.md)) |
| **Lives in** | `.github/workflows/` (workflow files), `libs/atlas-testkit` (shared fakes and fixtures), each service's `tests/` folder, `bench/` (measurements that are not tests) |
| **Old-spec theory to reread** | [StockPilot](../python/01-stockpilot.md) D1–D6, D13–D18, D19–D24 · [QuickServe](../python/02-quickserve-pos.md) D25–D39 · [WareFlow](../python/04-wareflow.md) D61–D66, D74–D78 · [CarePoint](../python/05-carepoint.md) D79–D90 · [LedgerBase](../python/06-ledgerbase.md) D97–D101 · [FleetTrack](../python/07-fleettrack.md) D109–D120 · [PayFlow](../python/09-payflow.md) D151–D156 · [AtlasMarket](../python/10-atlasmarket.md) D163–D168 · phase-7 D207 · phase-10 D316 |

> **What this document is for.** Each stage file lists the tests and CI jobs that stage adds. This file shows the whole picture: what each kind of test can and cannot prove, how the tests grow stage by stage, how the GitHub Actions workflows for the monorepo are laid out, which checks are required when, and what runs at night. It names files and responsibilities only. You write the workflows; YAML appears here only as tiny illustrations of a shape.

---

## 1. Principles every stage follows

1. **CI confirms; it does not discover.** pre-commit runs ruff, mypy and gitleaks on your machine first (S0). If CI is the first place a lint error appears, the local loop is broken. This is the StockPilot rule from D1–D6.
2. **Every invariant has a test, and the test was red first.** A stage's invariants table (section 5 of every stage file) names the test that proves each one. You write the failing version of the system, watch the test go red, and commit that evidence under `docs/evidence/sNN/` before fixing it.
3. **Integration tests use the real store.** Postgres 17, Valkey, RabbitMQ, Mongo, Timescale and Citus, in containers. Never SQLite pretending to be Postgres: most Atlas invariants (RLS, EXCLUDE, SKIP LOCKED, deferred constraint triggers) do not exist there.
4. **Deterministic or it does not count.** Pinned Hypothesis seeds, fake clocks (freezegun, provider-sim's fake clock), barriers instead of `sleep`, recorded embeddings and a fake LLM, a fixed worldgen seed. A test that passes 19 times out of 20 is not a test; it is a bug report you have not read yet.
5. **Coverage is measured where the rules live.** At least 80% on services and domain code only (S1). Coverage of views, serializers and settings is not a goal. StockPilot calls router coverage "self-congratulation".
6. **Three speeds.** The PR path stays fast. Slow but automatable things run at night. Anything that needs long uninterrupted state (cutover rehearsals, the split gate, resharding under load, PITR drills) runs in the weekend block by hand, with its log committed as evidence. Plan its unattended wall-clock time before you start: configurations × runs × about 11 minutes per split-gate run (a 10-minute scenario plus the 60 s warm-up), with 3 runs for intermediate configurations and 5 only for the final before/after pair (ADR-023).
7. **Build once, deploy the same SHA.** Images are built once, tagged by git SHA, and the exact image that passed staging goes to prod (S6 invariant).

---

## 2. The test pyramid for Atlas

```
                         +---------------------------+
                         | weekend runs (by hand)    |  split gate, cutover rehearsal,
                         |                           |  PITR drill, reshard under load
                      +--+---------------------------+--+
                      | nightly: load, restore-verify,  |
                      | chaos, judge, security rescans  |
                   +--+---------------------------------+--+
                   | E2E: Playwright, kind-e2e, smoke       |
                +--+----------------------------------------+--+
                | acceptance and contracts: provider-sim,        |
                | Pact, buf breaking, oasdiff, schema diff, evals |
             +--+-------------------------------------------------+--+
             | integration on real stores, SQL invariants, migrations, |
             | concurrency (barrier races x20)                         |
          +--+---------------------------------------------------------+--+
          | unit and property tests (pure domain, Hypothesis, fakes)          |
       +--+-------------------------------------------------------------------+--+
       | static checks: ruff, mypy --strict, import-linter, squawk, kubeconform     |
       +-----------------------------------------------------------------------------+
```

The base is cheap and runs on every commit. Each layer up is slower, needs more of the system running, and proves something the layer below cannot. The table says exactly what.

| Test type | What it proves | What it cannot prove | Atlas examples | Tools | First stage | Runs |
|---|---|---|---|---|---|---|
| **Static checks** | Code and config have the right shape: types line up, layers are not crossed, migrations are safe to run, manifests are valid | That anything works at runtime | mypy strict on `libs/` and the domain (Django and DRF ship no type hints, so market needs the community stubs and their mypy plugin, or stays out of mypy until S1: an S0 decision); import-linter *layers* (S1) and *independence* (S4) contracts; squawk on `sqlmigrate` output (S6); kubeconform (S10) | ruff, mypy, import-linter, squawk, kubeconform, terraform validate | S0 | Every PR |
| **Unit** | One rule behaves correctly in isolation | That the rule is wired in, or that the database agrees | Pricing strategies and the Capped wrapper; PaymentIntent state transitions; the Payme error mapping; aiogram handlers with `AsyncMock` | pytest, fakeredis, freezegun | S0 | Every PR |
| **Property-based** | A rule holds for all inputs of a shape, including ones you did not think of | That the property you wrote is the right one | Money never negative, parts sum to the total (S1, S2); split math and largest-remainder refunds (S5); a `RuleBasedStateMachine` keeping the trial balance at 0 across any sequence (S5); PII redaction never leaks a Luhn-valid card number (S8) | Hypothesis with a pinned seed | S1 | Every PR (more examples nightly if you want) |
| **Integration on real stores** | The code and the store agree: queries, constraints, locks, RLS, transactions | Behaviour across processes, networks or deploys | Plan assertions (the index is used); RLS tests run as the app role; outbox atomicity; Mongo transactions; CAGG vs raw; pgvector filtered ANN | pytest-django, testcontainers locally, service containers in CI | S1 | Every PR (path-filtered from S5) |
| **SQL invariants** | The database itself refuses bad states, even when the app is bypassed | That the app never tries | A psql tamper test: an unbalanced entry fails at COMMIT; the ledger is append-only for every role; the app role cannot UPDATE journal lines | Plain SQL run by pytest | S5 | Every PR touching money paths |
| **Migration** | Schema changes go both ways, and old code survives the new schema | That the migration is fast on production-size data | `makemigrations --check`; up/down (S1); old code against the new schema, `lock_timeout` present (S6); expand-only migration Job (S10); Citus distributed DDL (S12) | Django migrations, Alembic, squawk | S1 | Every PR |
| **Concurrency** | Two or more actors interleaving cannot break an invariant | Rare interleavings the barrier does not force | Two buyers, one unit: exactly one 201 and one 409 (S2); [A,B] vs [B,A] deadlock; write skew on a promo cap; two relays, no double publish (S4); duplicate Payme Create (S5); flash sale sells exactly 1,000 (S10) | `threading.Barrier`, separate DB connections, repeated ×20 | S2 | Every PR touching those paths |
| **Contract** | A producer and a consumer that deploy separately still agree | That either side is correct | Pact message contracts for `order.placed` and `vendor_group.fulfilled` (S4); Pact HTTP with broker and can-i-deploy (S9); `buf breaking` (S10); `oasdiff` on the public API (S9); GraphQL schema diff (S11) | Pact, buf, oasdiff | S4 | Every PR |
| **Simulator acceptance** | AtlasPay speaks Payme and Click correctly under every failure the protocols allow | That the real providers match the simulator (there is no contract to test against) | Payme sandbox scenarios, Click's 15 Postman scenarios, the 12 failure scenarios of S5, all run with the chaos switches on | provider-sim on the Compose stack | S5 | Every PR touching payments or the sim |
| **Resilience and chaos** | The system degrades the way the design says when a dependency is slow, dead or restarted | Failures you did not inject | `kill -9` of Valkey under RDB vs AOF (S3); broker kill mid-relay (S4); graceful shutdown resets (S6); Mongo primary kill under `w:1` vs majority (S7); Toxiproxy 2 s latency (S9); kill fraud mid-load (S12) | Toxiproxy, `docker kill`, `kubectl delete pod` | S3 | PR for the cheap ones; nightly for Toxiproxy |
| **Load and performance** | A number: p95, p99, throughput, pool saturation, under a stated protocol | That the number holds on other hardware | `bench/hello` (S0); keyset p95 at 1M rows (S1); stampede under locust (S3); checkout p95 and py-spy profile (S6); per-pod spread after scaling (S10); fraud p99 ≤ 30 ms (S12) | locust shapes the traffic; the percentiles you report come from a constant-rate oha probe (`-q <rate> --latency-correction`, which measures from each request's intended send time) recorded into HDR histograms, cross-checked against server-side Prometheus histograms; pgbench, py-spy; all under the ADR-002 protocol | S0 | Benchmarks by hand; a small p95 tripwire nightly |
| **End-to-end and browser** | A real user flow works through the real stack | Which component is at fault when it fails | Catalog → cart → checkout → simulator redirect → paid (S6, against staging); Keycloak OIDC negatives (S9, headless); login → order → live "paid" in the SPA (S11) | Playwright, React Testing Library | S6 | After staging deploy (S6); on kind in PRs (S11) |
| **Bot** | Handlers, filters, middlewares and FSM behave, including across replicas | How Telegram itself behaves | FSM survives a restart with RedisStorage (S3); the pacer against a fake Bot API, and a crafted "mark shipped" callback from another vendor's staff refused (S4); the pay button on an unpaid order resolves to a live `/l/{code}` payment link (S9); two concurrent updates for one chat (S10) | `AsyncMock`, `Dispatcher.feed_raw_update()`, the fake Bot API in `atlas-testkit` | S3 | Every PR touching the bot |
| **AI evals** | Retrieval quality, refusal behaviour and agent trajectories have not regressed | That the live model answers well today (only the recorded responses are tested) | Golden set of 30–40 items for hit@k and MRR; injection and cross-vendor paraphrase-leak suites; agent trajectory tests; SSE cancel stops billing; MCP round-trip (S8) | recorded embeddings, the fake LLM (provider-sim `llm` mode) | S8 | Every PR touching `services/ai/**` or `prompts/**` |
| **Model tests** | Training data has no leakage, serving uses the same features, the artifact is the one you think | That the model is good in the real world | Leakage test on the point-in-time training set; artifact sha256; feature parity (S7); latency budget and fraud-down (S12) | pytest | S7 | Every PR touching model code |
| **Operational** | Deploys, rollbacks, alerts and backups work when you need them | Anything about features | Smoke after deploy; an exercised rollback; `outbox_lag_seconds` fires and resolves; restore-verify (S6); auto `rollout undo` (S10) | CD workflows, Alertmanager, pgBackRest or wal-g | S6 | CD and nightly |
| **Security (cross-cutting)** | Planted problems are caught and attacks the design names are refused | That no other attack exists | Planted secret blocked (S0); byte-identical login errors (S1); forgotten WHERE returns 0 rows (S2); refresh replay revokes the family (S3); -32504 on a bad IP (S5); planted CVE fails CI (S6); confused-deputy test (S8); wrong state/nonce/aud, and an unverified email that never auto-links an account (S9); forged Telegram hash (S10); expired WS ticket (S11) | gitleaks, pip-audit, Trivy, crafted requests | S0 | Every PR; rescans nightly |

### 2.1 Making race tests deterministic

A race test that relies on timing passes on your laptop and fails in CI, or the other way round. The Atlas pattern:

1. Start N workers (threads or processes), each with **its own database connection**.
2. Each worker prepares its request, then waits on a shared barrier.
3. The barrier releases them together, so the critical sections really overlap.
4. Assert on the outcome (exactly one 201 and one 409), not on timing.
5. Repeat the test 20 times in CI (the S2 `concurrency` job).

One trap to know before you start: pytest-django's default database fixture wraps each test in a transaction, so threads in the same test cannot see each other's commits. Race tests need the transactional variant of the fixture. If a race test hangs or always passes, ask yourself which transaction each thread is actually in.

### 2.2 Markers and layout

- Each service has `tests/unit`, `tests/integration` and, where needed, `tests/concurrency`, `tests/contract`, `tests/e2e`.
- pytest markers select what a CI job runs, for example `unit`, `integration`, `concurrency`, `contract`, `sim`, `chaos`, `e2e`, `evals`, `slow`. S4 introduces the unit/integration split.
- `libs/atlas-testkit` holds what several services share: the fake Bot API (S4), barrier helpers, testcontainers factories, recorded embeddings and fixtures for the fake LLM, and small world specs for worldgen.
- Test data comes from factory_boy (S1) for small cases and worldgen for anything that needs realistic volume or distributions.

### 2.3 Local versus CI

| Need | Locally | In CI |
|---|---|---|
| Single Postgres, Valkey, RabbitMQ | testcontainers | GitHub Actions service containers (S1, S3, S4) |
| Multi-node stores (Mongo replica set, Valkey cluster, Citus, Timescale with extensions) | testcontainers or a Compose profile | testcontainers or a Compose profile started inside the job (service containers cannot pass the arguments a replica set needs) |
| The whole stack (provider-sim acceptance, Playwright) | `compose up` with the stage's profile | the same Compose profile inside the job |
| Object storage (S1+) | Garage, the default S3-compatible store (SeaweedFS is the fallback, ADR-001), in a testcontainer or the Compose profile | The same Garage image as a service container or in the Compose profile; presigned PUT/GET tests run against it, never against a mocked S3 client |
| Mail (S2+) | Mailpit as the SMTP test server (MailHog is unmaintained), with Toxiproxy in front of it for the slow-SMTP runs | The same Mailpit container; tests read its HTTP API to count messages (the S4 one-checkout-one-email test) |
| PgBouncer (S10) | A pinned PgBouncer ≥ 1.24 in front of Postgres | The same pin, inside kind or Compose. Since 1.24 `max_prepared_statements` defaults to 200, so the asyncpg pain test first sets it to 0 to reproduce the error, then restores it |
| Kubernetes | kind | kind inside the job (S10) |

---

## 3. Stage by stage

### 3.1 Stage × test-type matrix

`N` = this test type starts in this stage; `+` = the stage extends it; blank = unchanged.

| Test type | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Static checks | N | + | | | + | | + | | | + | + | + | |
| Unit | N | + | + | + | + | + | | | + | + | | | |
| Property-based | | N | + | | | + | | | + | | | | |
| Integration on real stores | | N | + | + | + | + | | + | + | + | + | + | + |
| SQL invariants | | | | | | N | | | | | | | + |
| Migration | | N | | | | | + | | | | + | | + |
| Concurrency | | | N | + | + | + | | | | | + | | |
| Contract | | | | | N | | | | | + | + | + | |
| Simulator acceptance | | | | | | N | | | | + | | | |
| Resilience and chaos | | | | N | + | + | + | + | | + | + | + | + |
| Load and performance | N | + | | + | | | + | | + | | + | | + |
| End-to-end and browser | | | | | | | N | | | + | | + | |
| Bot | | | | N | + | | | | + | + | + | | |
| AI evals | | | | | | | | | N | | | | |
| Model tests | | | | | | | | N | | | | | + |
| Operational | | | | | | | N | | | | + | | + |
| Security | N | + | + | + | | + | + | | + | + | + | + | |

### 3.2 What each stage adds

| Stage | Tests added (what they prove) | CI jobs added | Added to the required gate |
|---|---|---|---|
| [S0](stage-00-bootstrap.md#7-ci-changes) | A trivial test that proves the plumbing; the image has no compiler and does not run as root; a planted secret is blocked by pre-commit | `lint` (ruff), `typecheck` (mypy strict on `libs/`; market either with django-stubs and djangorestframework-stubs through their mypy plugin, or excluded until S1, recorded in ADR-001), `test-unit`, `ci-gate` (the only required status check, section 4.4), pre-commit with gitleaks, compat check | `lint`, `typecheck`, `test-unit` (as `ci-gate` needs) |
| [S1](stage-01-layered-monolith.md#7-ci-changes) | Integration on real Postgres; factory_boy; Hypothesis with a pinned seed; plan assertions; migration up/down; the permission matrix (staff act only for their own vendor) | `test-integration` (Postgres service container), `migrations` (`makemigrations --check`, up/down), `import-contracts` (the import-linter layers contract), coverage ≥ 80% on services/domain | `test-integration`, `migrations`, `import-contracts` |
| [S2](stage-02-checkout-correctness.md#7-ci-changes) | Barrier races, the deadlock, write skew, idempotent replay, RLS as the app role | `concurrency` (race suite ×20) | `concurrency` |
| [S3](stage-03-redis-auth-bot.md#7-ci-changes) | fakeredis units and real Valkey integration; the stale-set barrier; the 3-container limiter; `kill -9` persistence; freezegun on token expiry; aiogram tests with `feed_raw_update` | Valkey service container, `bot-tests`, nightly locust with a p95 budget | `bot-tests` |
| [S4](stage-04-async-events-boundaries.md#7-ci-changes) | Worker death, routing, rollback-means-nothing-enqueued, broker-kill relay, restart N = N, a missing parking queue loses nothing (at-least-once dead-lettering on quorum queues), Pact message contracts, the v1→v2 upcaster, the 40-query judged set, the Tashkent-midnight Beat boundary, one checkout sends exactly one confirmation email (counted in Mailpit) | RabbitMQ service container, `pact-verify`, the independence contracts added to `import-contracts`, unit/integration split | `pact-verify` (and independence joins `import-contracts`) |
| [S5](stage-05-atlaspay-monolith.md#7-ci-changes) | Simulator acceptance (Payme sandbox, Click 15, failures 1–12) with chaos switches; the ledger state machine; the psql tamper test; split math | `provider-sim` image build, `sim-acceptance` on the Compose stack, `sql-invariants`, an `import-contracts` rule that `libs/atlaspay-domain` imports no framework, **path filters and a matrix start here** | `changes`, `provider-sim`, `sim-acceptance`, `sql-invariants` |
| [S6](stage-06-ship-and-operate.md#7-ci-changes) | Playwright E2E against staging, smoke, migration compatibility (old code on the new schema), alert-fires, restore-verify, locust + py-spy | `build-push` (GHCR by SHA), `trivy` (fails on HIGH/CRITICAL: `--severity HIGH,CRITICAL --exit-code 1`), `pip-audit` (fails on any known vulnerability; each accepted exception is an `--ignore-vuln <ID>` with a dated justification in `docs/security/exceptions.md`), `gitleaks` gate, `migration-lint` (squawk), `migration-compat`, `terraform-plan` / `terraform-apply`, `deploy-staging` → `deploy-prod` with approval, `rollback`, nightly `restore-verify`, nightly `locust` | `pip-audit`, `gitleaks`, `migration-lint`, `migration-compat`, `trivy` (image built without push on PRs), `terraform-plan` |
| [S7](stage-07-polyglot-mongo-timescale.md#7-ci-changes) | Mongo and Timescale testcontainers, CAGG vs raw, the leakage test, artifact hash, feature parity | `store-integration` (matrix: `mongo`, `timescale`) with path filters, `model-tests` | `store-integration`, `model-tests` |
| [S8](stage-08-ai-integration.md#7-ci-changes) | Golden set (hit@k, MRR), injection and leakage suites, trajectory tests, budget tests, SSE cancel stops billing, MCP round-trip | Required `ai-evals` on `services/ai/**` and `prompts/**`; nightly judge (stretch) | `ai-evals` |
| [S9](stage-09-strangler-atlaspay-auth.md#7-ci-changes) | Pact HTTP, OIDC negatives against Keycloak (Google, a second provider on the same flow, runs on staging only), key rotation under load, the shadow diff, Toxiproxy, webhook signature and secret rotation, key scopes; market's webhook receiver dedups on event id (it replaces the payment-events consumer at the contract step); after the fraud v1 port, shadow scores and `model_version` are stored for every attempt made against atlaspay; the bot's pay button issues a fresh link when the old one was deleted | Reusable per-service workflows with a path-filtered matrix, `pact-verify` extended with HTTP pacts, the Pact broker and can-i-deploy, `oasdiff` gate, Keycloak OIDC negatives via headless Playwright, `shadow-diff`, `sim-acceptance` against atlaspay, nightly Toxiproxy | per-service jobs, `pact-verify` (with can-i-deploy), `oasdiff`, `oidc-negatives`, `shadow-diff` (byte-identical until the contract step, then kept as a regression suite against recorded replies) |
| [S10](stage-10-kubernetes-grpc-inventory.md#7-ci-changes) | gRPC deadline, status and contract tests; per-pod spread; flash-sale concurrency; Lease exactly-once; preStop gives 0 errors; RLS with `SET LOCAL` and HPA at 5 through PgBouncer ≥ 1.24; bot concurrency and dedup | `buf lint` / `buf breaking`, `kustomize build` + kubeconform (CRDs such as Gateway API routes and ExternalSecrets need their schemas supplied with `-schema-location`, for example from the datreeio CRDs-catalog; never add `-ignore-missing-schemas`, which turns the check into a silent skip), `kind-e2e` (cluster, deploy, migration Job, smoke, a small rollout under load), CD to k3s with automatic rollback, flash-sale concurrency test, bot webhook tests, nightly drift check | `buf`, `k8s-manifests`, `kind-e2e`, `flash-sale`, `bot-webhook` |
| [S11](stage-11-realtime-edge-graphql.md#7-ci-changes) | WS auth, resume and backpressure; the long-poll endpoint used for the comparison; fan-out across pods on kind; GraphQL cost, persisted-only, field auth and DataLoader counts; RTL; the Playwright BFF flow | `edge-tests`, `edge-fanout-kind`, `graphql-schema-diff`, `playwright-bff` (on kind), `spa-build` (type-check, build, persisted-query allow-list) | `edge-tests`, `edge-fanout-kind`, `graphql-schema-diff`, `playwright-bff`, `spa-build` |
| [S12](stage-12-data-at-scale-fraud.md#7-ci-changes) | Citus router-plan assertion, rebalance under load (weekend), Mongo reshard (weekend), fraud latency budget and fraud-down chaos | `citus-ddl-migrations` (ephemeral Citus with `citus.enable_unsafe_triggers` set as ADR-040 records, up/down, fails if a posting statement loses its router plan), `ledger-tests`, `fraud-tests` (latency budget, fraud-down chaos), nightly `restore-verify` extended to the ledger | `citus-ddl-migrations`, `ledger-tests`, `fraud-tests` |

Job names match the stage files' section 7 and are suggestions; keep them stable once the gate refers to them.

---

## 4. GitHub Actions layout for the monorepo

### 4.1 Workflow files

Reusable workflows must sit directly in `.github/workflows/` (GitHub does not look in subfolders). A leading underscore marks a file as "called, never triggered on its own".

| File | Triggered by | Responsibility | From |
|---|---|---|---|
| `ci.yml` | `pull_request`; `push` to `main` | The one PR pipeline. Detects what changed (from S5), runs or calls every check, and ends in the single required job `ci-gate`. Before S9, its jobs are written inline. | S0 |
| `_python-service.yml` | `workflow_call` | For one service or lib: lint, typecheck, unit, integration with the stores it needs, coverage threshold. Inputs name the service path and the stores. Replaces the inline per-service jobs. | S9 |
| `_compose-suite.yml` | `workflow_call` | Starts a named Compose profile, waits for health, runs one suite, uploads logs and evidence. Used by `sim-acceptance`, `sql-invariants`, `shadow-diff`, `oidc-negatives`. | S5 |
| `_image.yml` | `workflow_call` | Builds one service image with a layer cache, scans it with Trivy, and pushes it to GHCR tagged with the git SHA (push only on `main`). | S6 |
| `_terraform.yml` | `workflow_call` | `fmt`, `validate` and `plan` on PRs (plan posted as an artifact); `apply` only from `main`. Remote locked state. | S6 |
| `_deploy.yml` | `workflow_call` | Deploys one SHA to one environment: expand-only migrations, health-gated switch, smoke, rollback on failure. S6 targets the VPS; S10 targets k3s. | S6 |
| `_kind-suite.yml` | `workflow_call` | Creates a kind cluster, applies the dev overlay, runs the migration Job and one suite (`kind-e2e`, WS fan-out, Playwright on kind). | S10 |
| `cd.yml` | `ci.yml` completing successfully on `main` (a `workflow_run` trigger); manual dispatch for rollback | Builds changed images once, deploys to staging, runs smoke and Playwright, waits for the `production` environment approval, deploys the **same digests** to prod, smokes, rolls back on failure. | S6 |
| `nightly.yml` | `schedule`; manual dispatch | The jobs in [section 5](#5-nightly-and-scheduled-jobs). Each job is independent, so one red job does not hide the others. | S3 |
| `weekly.yml` | `schedule`; manual dispatch | `scripts/compat_check.sh`, a pip-audit and Trivy rescan of what is deployed (CVEs are published after you merge). | S0 (compat), S6 (rescan) |

Why one PR workflow instead of one per service: a job can only wait on (`needs`) jobs in the **same** workflow. Keeping every PR check inside `ci.yml`, with reusable workflows called as jobs, lets a single `ci-gate` job see all results. Separate per-service workflows would each need their own required check, and path filters make that break (see 4.4).

### 4.2 How the PR pipeline is wired

```
pull_request
    |
    v
 changes  (S5+: which services, libs, deploy dirs, prompts changed?)
    |
    +--> lint, typecheck, pip-audit, gitleaks, import-contracts, migration-lint   (cheap)
    |
    +--> per service (matrix from `changes`):  _python-service.yml     (S9+; inline before)
    |        unit -> integration -> coverage
    |
    +--> suites (only if their paths changed):
    |        concurrency, bot-tests, pact-verify, sim-acceptance, sql-invariants,
    |        store-integration, model-tests, ai-evals, oasdiff, oidc-negatives,
    |        shadow-diff, buf, k8s-manifests, kind-e2e, edge-tests, citus-ddl-migrations ...
    |
    +--> trivy on a PR build (no push), terraform-plan (if deploy/terraform changed)
    |
    v
 ci-gate  (needs all of the above; the ONLY required status check)
```

### 4.3 Path filters (from S5)

The `changes` job maps changed paths to the jobs that must run. Everything not triggered is skipped, and `ci-gate` treats "skipped" as "not affected".

| Changed paths | Jobs that run |
|---|---|
| `services/market/**` | market service jobs, `concurrency`, `pact-verify`, `migrations`, `migration-lint`; `sim-acceptance` and `sql-invariants` while the payments module lives in market (until S9) |
| `services/provider-sim/**` | `sim-acceptance` |
| `services/atlaspay/**` (S9) | atlaspay service jobs, `sim-acceptance`, `sql-invariants`, `pact-verify` (as HTTP provider), `oasdiff`, `shadow-diff` |
| `services/auth/**` | auth service jobs, `oidc-negatives`, `pact-verify` |
| `services/ai/**`, `prompts/**`, `evals/**` | ai service jobs, `ai-evals` (required), MCP round-trip |
| `services/edge/**`, the SPA | `edge-tests`, `edge-fanout-kind`, `graphql-schema-diff`, `playwright-bff`, `spa-build` |
| `services/bot/**` | `bot-tests`, `bot-webhook` (S10) |
| `services/inventory/**` | inventory jobs, gRPC contract tests, `flash-sale` |
| `services/ledger/**` | `ledger-tests`, `citus-ddl-migrations` |
| `services/fraud/**` | `fraud-tests`, `model-tests` |
| `libs/atlas-common/**` | the lib's tests plus the unit tests of every service that depends on it |
| `libs/atlas-events/**` | the lib's tests plus `pact-verify` for every producer and consumer, and `edge-tests` (edge consumes events) |
| `libs/atlas-proto/**` | `buf` (lint and breaking), stub generation, gRPC tests of every client and server (`ledger-tests`, `fraud-tests`, inventory jobs) |
| `libs/atlaspay-domain/**` | the lib's property and state-machine tests, `sim-acceptance`, `sql-invariants` |
| `libs/atlas-fraud-features/**` (S7) | the lib's tests, `model-tests` (leakage and training/serving feature parity), and the tests of whichever service scores (market S7–S8, atlaspay S9–S11, `fraud-tests` from S12) |
| `libs/atlas-worldgen/**` | the lib's tests, the determinism test, invariants on a small generated world |
| `libs/atlas-testkit/**`, `uv.lock`, root `pyproject.toml`, `.github/workflows/**` | everything (a change to shared test code, the lockfile or CI itself must prove itself on the full suite) |
| `deploy/compose/**` | `docker compose config` validation and the Compose suites |
| `deploy/k8s/**` | `k8s-manifests`, `kind-e2e` |
| `deploy/terraform/**` | `terraform-plan` |
| `bench/**` | lint only (benchmarks run by hand under ADR-002) |
| `docs/**` only | nothing heavy; `ci-gate` passes |

Why libs trigger their consumers even though they are "consumed by version" (S0): the version pin protects consumers that have not bumped yet, but the next bump will pull the change in. Running the consumers' tests now tells you about a break while the change is still fresh.

### 4.4 Required checks and the gate job

Branch protection on `main` requires one status check: `ci-gate`. There are two different traps the gate avoids. A whole **workflow** skipped by `on.*.paths` leaves its required checks Pending forever, so the PR can never merge. A **job** skipped by an `if:` condition reports Success, so a required check passes without having run. The gate always runs, and it fails unless `changes` succeeded and every needed job ended in `success` or an intentional `skipped`. Its shape:

```yaml
ci-gate:            # the only required status check
  if: always()      # runs even when some needs were skipped
  needs: [changes, lint, typecheck, test-unit, test-integration, concurrency]
  # fail unless 'changes' succeeded and every other need is
  # 'success' or a 'skipped' the path filter intended
```

Each stage adds its jobs to `needs` (the last column of the table in 3.2). Two things make the gate honest:

1. The `changes` job itself must succeed. If path detection breaks, everything downstream is skipped and a naive gate would pass. Make `changes` a hard dependency.
2. Adding a new job to `ci.yml` without adding it to the gate's `needs` means nothing requires it. Review the gate list at every stage close.

Other required settings on `main`: PRs only (no direct pushes), linear history or squash merges (your choice), and the `production` environment protected by a required reviewer (you).

### 4.5 The CD pipeline

| Step | S6 (VPS behind Nginx) | S10 (k3s via Terraform) |
|---|---|---|
| 1. Build | Changed images built once, tagged by SHA, pushed to GHCR | Same |
| 2. Scan | Trivy on the pushed digest; HIGH or CRITICAL fails (pip-audit already ran on the PR) | Same |
| 3. Migrate | Expand-only migrations with `lock_timeout=3s`, before the new code | Migration Job (expand-only) before the rollout |
| 4. Deploy staging | Health-gated container swap plus Nginx upstream switch; graceful shutdown for gunicorn, Celery, relay and consumers | `atlas-staging` namespace applied from the Kustomize overlay with pinned digests; `rollout status` |
| 5. Verify staging | Smoke tests, Playwright E2E | Smoke tests; automatic `rollout undo` when smoke fails |
| 6. Approve | `production` environment approval | Same |
| 7. Deploy prod | The same SHA that passed staging | `atlas-prod` with the same digests; a scoped deploy ServiceAccount |
| 8. Verify prod | Smoke; rollback to the previous SHA on failure | Smoke; automatic `rollout undo` |

The **contract** half of an expand/contract migration (dropping the old column) is never automatic. It ships in a later deploy, after the old code is gone everywhere, as a PR of its own.

Rollback is a first-class path, not an emergency improvisation: the S6 exercise is to run it on purpose (the STAR story "the rollback nobody had ever exercised").

### 4.6 Hygiene of the workflows themselves

A CI system holds deploy credentials; treat it as production.

- **Least-privilege tokens.** Set workflow permissions to read-only by default; grant `packages: write` only to the image job, `id-token: write` only where OIDC federation to the cloud is used, and comment permissions only to jobs that comment.
- **Pin third-party actions to a full commit SHA**, not a moving tag. Renovate (the S0 stretch item) keeps the pins current. A real example from this year: on 2026-03-19 the `aquasecurity/trivy-action` and `setup-trivy` tags were force-pushed to a credential stealer, and Trivy v0.69.4 was malicious (advisory GHSA-69fq-xp46-6x23). The S6 scan job is exactly that victim profile. Pin actions by full SHA, pin the Trivy binary version and its checksum, and give the scan job no secrets.
- **No secrets on untrusted code.** PRs run on `pull_request`, never `pull_request_target`, so a fork cannot read secrets.
- **Environment secrets** for staging and prod, not repository-wide secrets. Prefer short-lived cloud credentials through OIDC over long-lived keys.
- **Concurrency groups.** Cancel superseded PR runs on the same branch; never cancel a running deploy.
- **Artifacts as evidence.** Upload EXPLAIN plans, locust CSVs, eval reports and the Terraform plan as artifacts, and copy the ones a stage needs into `docs/evidence/sNN/`.

### 4.7 Speed

A slow PR pipeline gets bypassed. Guidance, not a rule: keep the typical PR run under about 10–12 minutes.

- Cache the uv download cache keyed on `uv.lock`, and Docker layers with the buildx GitHub Actions cache.
- Split integration tests per service through the matrix, so a market change does not wait for ledger tests.
- Keep heavy suites path-filtered (`kind-e2e`, `sim-acceptance`), and move anything slower than the budget to nightly.
- GitHub-hosted runners have limited memory; run kind and multi-node stores with the smallest profile that still proves the point (the same tactics as the 16 GB laptop in [schedule-and-cuts.md](schedule-and-cuts.md#9-laptop-resources-16-gb-vs-32-gb)).

---

## 5. Nightly and scheduled jobs

| Job | From | What it runs | Pass condition | Where it runs |
|---|---|---|---|---|
| `nightly-locust` | S3 | A locust smoke against the Compose stack: cached catalog reads | p95 within a budget set from the S3 recorded numbers, with headroom for runner noise | GitHub runner |
| `nightly-locust` (extended) | S6 | Adds the worldgen traffic-mode checkout scenario against staging to the S3 catalog smoke (S6 §7 lists it as the nightly `locust` job); reported percentiles come from the oha probe | p95 budget and 0 errors | Against staging |
| `restore-verify` | S6 | Restores the latest base backup plus WAL into a scratch instance, recovers to a target time, runs the trial balance and row-count checks, records the time taken (your measured RTO) | Trial balance identical; restore completes | A runner or the staging VM, with read-only access to the backup bucket |
| `restore-verify` (ledger) | S12 | The same for `citus-ledger` | Trial balance identical across shards | Same |
| `nightly-store-checks` (optional) | S7 | The Mongo write-concern failover script and the rebuild-from-Postgres check for the projections | Majority writes survive; rebuilt projections match | A runner, only if its memory allows a 3-node replica set |
| `nightly-toxiproxy` | S9 | 2 s of latency with 0% errors injected in front of atlaspay; checks that the bulkhead holds and unrelated endpoints keep their latency | Unrelated endpoints within their p95 budget | Compose on a runner |
| `nightly-drift` | S10 | `kubectl diff` of every overlay against the cluster | Nothing in the cluster that is not in git (the "cluster state comes only from git" invariant) | Against staging and prod, with a read-only ServiceAccount |
| `nightly-e2e` | S11 | The slow edge jobs (`edge-fanout-kind`, `playwright-bff`) on `main`, in addition to PRs that touch edge or the SPA | Green | kind on a runner |
| `nightly-judge` | S8 (stretch) | The LLM judge on a small answer set, calibrated on 15 hand-graded answers | Faithfulness above threshold; a hard $ cap stops the run | Runner, real provider API |
| `weekly-rescan` | S6 | pip-audit on `main`'s lockfiles and a Trivy rescan of the digests currently in prod | Trivy: no new HIGH/CRITICAL finding; pip-audit: no known vulnerability except the dated `--ignore-vuln` exceptions in `docs/security/exceptions.md` (pip-audit has no severity threshold) | Runner |
| `weekly-compat` | S0 | `scripts/compat_check.sh`: pulls every pinned image, prints server and extension versions, flags the [U] tags | Script succeeds; review the output at each stage start | Runner |

Rules for scheduled jobs:

1. A red nightly job opens an issue (or notifies you) and **blocks the next stage close** until it is green or explained.
2. Nightly load jobs are **tripwires, not benchmarks**. Runner hardware is shared and noisy. Real numbers come from `bench/` on a fixed machine with the ADR-002 protocol; CI only catches large regressions.
3. Product jobs are not CI jobs. The review summaries and the vendor digest run in market's Celery Beat (a single-replica Recreate Deployment from S10); payouts and reconciliation run in atlaspay's `scheduler` process type (from S9; leader-elected with a Kubernetes Lease from S10). None of them runs in GitHub Actions.

---

## 6. What CI deliberately does not do

| Not in CI | Why | Where it happens instead |
|---|---|---|
| Real Payme or Click sandbox calls | There is no merchant contract | provider-sim; the same suite can be pointed at test.paycom.uz and the Click Playground if an account ever exists |
| Live LLM calls on PRs | Flaky, slow and costly | The fake LLM and recorded embeddings on PRs; the nightly judge (stretch) with a $ cap |
| The split gate, cutover rehearsal, resharding under load, PITR drills | They need long, uninterrupted, controlled runs | Weekend blocks, logs committed as evidence |
| `terraform apply` from a PR | A PR must never change real infrastructure | `apply` only from `main` |
| Auto-applying the contract step of a migration | Irreversible; must wait until no old code runs | A separate PR and deploy |
| Mutation testing, fuzzing services | Not in the budget | Named only |

---

## 7. Common mistakes

1. **Requiring individual checks in a path-filtered monorepo.** A required check from a workflow that `paths` filtered out stays Pending, so the PR can never merge and someone disables the requirement. A required job skipped by `if:` reports Success, so a broken `changes` step or a wrong condition merges untested code as green. Require only the gate job, and make it fail when `changes` did not succeed.
2. **Building a different image for prod.** Rebuilding on promotion means prod runs something staging never saw. Promote digests.
3. **`sleep` in race tests.** Use a barrier; sleeps make tests slow and still flaky.
4. **Race tests inside one wrapping transaction.** The threads never really compete. Use separate connections and the transactional test fixture.
5. **Retrying flaky tests automatically.** It hides exactly the races Atlas is built to catch.
6. **Mocking the database in "integration" tests.** RLS, deferred triggers and EXCLUDE constraints only exist in real Postgres.
7. **Coverage as a target everywhere.** It pushes you to test serializers instead of invariants.
8. **Secrets reachable from forked PRs** (`pull_request_target` with a checkout of the PR head).
9. **Unpinned third-party actions.** A moving tag can change what runs with your deploy credentials.
10. **Treating nightly load numbers as benchmarks.** They are for regressions only.

---

## 8. If you get stuck

- **The gate passes when it should not.** Print the result of every job in its `needs`; check that `changes` really ran and that the new job is in the list. Then ask: which of those "skipped" results was intended by the path filter, and which one came from an `if:` that silently evaluated to false?
- **mypy is red on day 1 with `import-untyped` on `import django`.** Django and DRF ship no type hints. Which is cheaper for you now: the community stubs with their mypy plugin (what does the plugin need to know about your settings?), or excluding market's framework imports until S1? And the usual pre-commit mypy hook runs in its own virtualenv: how will it see `atlas_common` and your pinned dependencies?
- **A test is green locally and red in CI.** Suspect time zones (CI runs in UTC; the Beat test uses Asia/Tashkent), ordering between tests, a missing store extension in the CI image, or less memory.
- **Integration tests are too slow.** Reuse one container per test session, truncate between tests instead of recreating, and run services in parallel through the matrix.
- **Pact can-i-deploy blocks you.** Ask whether the consumer or the provider changed first, and whether the other side has already published a verification for that version. Reread [WareFlow D61–D66](../python/04-wareflow.md) and [FleetTrack D109–D120](../python/07-fleettrack.md).
- **The CD rollback does not restore service.** Check whether the migration that shipped with the bad version was expand-only. If it was not, rollback cannot work; that is why S6 lints migrations. Reread [LedgerBase D97–D101](../python/06-ledgerbase.md).
