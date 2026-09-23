# Stage 00 — Bootstrap

| | |
|---|---|
| **Weeks** | W1–W2 (2 weeks) |
| **Hours** | 24 must + 3 stretch (27 total) |
| **Architecture at start → at end** | an empty folder → a Django orientation sandbox, the `market` skeleton + `postgres:17` in Compose, CI green behind a `ci-gate` job, a benchmark harness, a world-generator skeleton |
| **New technologies** | Django 5.2 basics (tutorial parts 1–2, settings, the deployment checklist), uv workspace, multi-stage Docker, Compose healthchecks, GitHub Actions, ruff, mypy `--strict` (+ the Django stubs decision), pre-commit, gitleaks, structlog, HDR histograms, a constant-rate load tool (oha with latency correction) |
| **Portfolio tag** | `v0.0` |
| **Old-spec theory to read** | [P1 D1–D6](../python/01-stockpilot.md) (Stage 1: scaffold, multi-stage non-root image, pre-commit, Compose healthcheck); [P2 D25–D30](../python/02-quickserve-pos.md) (Stage 1: Django scaffold, settings split, framework-choice rationale); [phase-1 D23](../../phase-1-foundations.md) (CI pipelines, Docker layer caching) |

Version pins in this file are as of 2026-09. Re-check them with `scripts/compat_check.sh` (which you write in this stage, ADR-001).

> **What this stage is really for.** For 53 weeks you will justify decisions with numbers, and those numbers are only worth something if they are comparable and reproducible. S0 builds the machinery that makes them so (a written benchmark protocol and a seeded data generator) and a repository that refuses bad habits (root images, unpinned versions, committed secrets) before there is any code worth protecting. It also gives you a first, deliberate contact with Django before you build anything in it. No feature ships in these two weeks, on purpose.

---

## 0. On-ramp: from StockPilot Day 5 to Atlas

You are arriving from Day 5 of the old Phase 1 (StockPilot: FastAPI + SQLAlchemy 2.0 async basics). Four things to know before you start:

1. **Keep the StockPilot repo; do not port it.** Those ~15 hours are not wasted. The FastAPI + SQLAlchemy async skills come back in `provider-sim` (S5), `atlaspay` (S9) and `ledger` (S12). ADR-000 (this stage) records that decision in writing, and it becomes your first STAR story.
2. **The old specs are your theory library.** Each stage header lists old days to reread (the concept, the "pain-first" moment, the interview questions). Read them for the *why*; never copy their code or their folder layout. Links in this plan point at [`../python/`](../python/) and at the phase files one level up.
3. **The weekly rhythm.** Three 2 h weekday sessions and one 5–6 h weekend block, with an optional fourth weekday session. Anything that needs uninterrupted state (a benchmark run, a `compose up` debugging session) goes to the weekend block.
4. **Log your actual hours from day one.** Every block below has a budget sized for someone doing this work for the first time. They are still estimates. Keep one CSV, `docs/hours.csv` (stage, block, budget, actual, date), and add a row whenever you close a block. At [B1](buffers-and-job-sprint.md) (W18) you compute actual/budget and re-plan the rest of the season with that ratio. If a block on the never-cut spine overruns, the date moves; its acceptance criteria are never silently deferred.

### Suggested two-week calendar (24 h must)

| Week | Session | Blocks | Hours |
|---|---|---|---|
| W1 | Weekday 1 | 4.0 Django orientation | 2 |
| W1 | Weekday 2 | 4.0 Django orientation (0.5) → 4.1 Workspace (1.5) | 2 |
| W1 | Weekday 3 | 4.1 Workspace | 2 |
| W1 | Weekend block | 4.2 Image (3) → 4.3 Compose (2) → 4.7 Drill (1) | 6 |
| W2 | Weekday 1 | 4.4 CI and hooks | 2 |
| W2 | Weekday 2 | 4.4 CI and hooks (1) → 4.7 Drill (1) | 2 |
| W2 | Weekday 3 | 4.5 Decisions | 2 |
| W2 | Weekend block | 4.5 Decisions (0.5) → 4.6 Measurement (5.5, including ≈35 min of unattended benchmark runs) | 6 |
| Either week | Optional 4th session | Stretch, only once the must tier is closed | up to 3 |

### The monorepo you are creating (names only)

This is the end-of-Season-1 shape from the glossary. Create only the parts marked **S0** now; the rest appear in the stage that needs them. Git does not track empty folders, so do not create placeholders.

```
atlas/
  pyproject.toml              S0  workspace root: tooling config, no application code
  uv.lock                     S0  one lock file for every member
  .pre-commit-config.yaml     S0
  .github/workflows/          S0
  services/
    market/                   S0  Django project (apps arrive in S1)
    provider-sim/  atlaspay/  auth/  ai/  edge/  bot/  inventory/  ledger/  fraud/     later
  libs/
    atlas-common/             S0  Money stub, error types, structlog JSON config
    atlas-worldgen/           S0  skeleton only
    atlas-events/ atlas-proto/ atlaspay-domain/ atlas-testkit/ atlas-fraud-features/   later
  deploy/
    compose/                  S0
    k8s/ (base, overlays/dev|staging|prod)   terraform/                                later
  bench/                      S0  harness + scenarios (bench/hello first)
  scripts/                    S0  compat_check.sh
  sandbox/                    S0  throwaway learning code (django-ramp, started in 4.0)
  prompts/  evals/                                                                     S8
  docs/
    adr/                      S0  ADR-000 … ADR-003 in this stage
    evidence/s00/             S0  every proof for this stage
    star/  postmortems/       S0  first entries at stage close
    deferred.md               S0  the list of things you chose not to build yet
    hours.csv                 S0  actual hours per block (the B1 recalibration input)
    learning/                 S0  fastapi-to-django.md (first lines in 4.0; S1 completes it)
    perf/ sd/ (S1)   design/ (S5)   runbooks/ privacy/ (S6)                            later
```

Python import names use underscores: the folder `libs/atlas-common` installs a package imported as `atlas_common`.

### The uv workspace idea, in plain words

A **uv workspace** is one repository holding several Python packages ("members") that share a single lock file. The root `pyproject.toml` lists the members; each member has its own `pyproject.toml` with its own dependencies. uv resolves all of them together, so `market` and (later) `atlaspay` can never silently run different versions of the same library.

Why it matters here:
- **One lock, many packages.** A single `uv.lock` means one `uv sync` reproduces the whole environment on any machine and in CI.
- **Local libraries without copy-paste.** `libs/atlas-common` is a real package. Services declare a dependency on it like any other library. Inside the workspace uv links the member directly, so editing it in dev needs no reinstall.
- **Consumed by version, not by path.** Atlas's rule is that `atlas-common` is *built as a wheel and consumed by version*. That means `market` declares a version range for `atlas-common` (for example, compatible with 0.1.x), and the production image installs the built wheel of that exact version rather than copying the `libs/` source tree. A breaking change in the library then forces a version bump that you can see in a diff. This is the habit that lets a library outlive the monorepo (S9 onward, when services have their own release cadence).

Guiding questions to answer in ADR-000 (not in code):
- What does a single workspace lock protect you from that per-service lock files do not? What does it cost you when two services genuinely need different versions?
- Why does the image install a wheel instead of the source folder? What would a `COPY libs/ …` into the market image couple together?

---

## 1. The problem this stage starts from

**Business terms.** There is no product yet. There is also no agreement on how "is it faster?" or "is it safer?" will be decided. Every later split, cache or shard in this plan must be argued from numbers. Without a protocol, those numbers would be anecdotes.

**Engineering terms.**
- No repository, no build, no CI. The first time a secret is committed or a root-running image is shipped, nothing stops it.
- Your toolchain comes from a single-service FastAPI project. Atlas is a multi-package monorepo whose first service is Django.
- Versions drift. Several of the stores used later have changed licence or edition since your old specs were written (Redis's licence; MinIO, whose community edition stopped publishing images in 2025 and was archived in 2026; Timescale's `-oss` images). Pins and licences need a written register before the first store is added.
- You have never used Django. Building a settings package and a gunicorn entry point as your very first Django code would mix two unknowns.
- Season 2 (ML/DS/DE) will analyse months of Atlas traffic. That data only exists if a deterministic generator exists from day one.

## 2. Outcomes — what exists when the stage is finished

1. A Django orientation sandbox (`sandbox/django-ramp/`, tutorial parts 1–2) and one-line answers about the five pieces a Django project is made of, at the top of `docs/learning/fastapi-to-django.md`.
2. A uv workspace at `atlas/` whose members build: `services/market` (Django 5.2 LTS, settings split into `base`/`dev`/`prod`) and `libs/atlas-common` (a `Money` stub, shared error types, structlog JSON configuration), plus the `libs/atlas-worldgen` skeleton.
3. A **multi-stage, pinned, non-root** `market` image. Size before and after the multi-stage change is recorded. `whoami` inside it does not print `root`, and an automated check proves there is no compiler in the runtime image.
4. `deploy/compose` runs `market` + `postgres:17` with a **real healthcheck**; `docker compose up` works from a clean clone.
5. GitHub Actions runs **ruff (lint + format check) → mypy `--strict` on `libs/` → pytest → `ci-gate`** on every push and pull request; branch protection requires only `ci-gate`. pre-commit runs ruff, mypy and gitleaks locally, and a planted secret is blocked.
6. `bench/` harness plus **ADR-002 (benchmark protocol)**. The `bench/hello` scenario has 3 recorded runs with a full environment fingerprint.
7. `libs/atlas-worldgen` skeleton: seeded RNG, a world-spec YAML, users and vendors generators, `history` mode (COPY-ready rows) and `traffic` mode (locust), with a determinism test.
8. **ADR-000** (Django monolith + monorepo, with the counter-argument), **ADR-001** (pins and compatibility, plus `scripts/compat_check.sh`), **ADR-003** (licences register).
9. Stage close: tag `v0.0`, a postmortem paragraph, **1 STAR story** (choosing Django despite the sunk FastAPI work), `docs/deferred.md` and `docs/hours.csv` started.

## 3. Architecture at the end of the stage

```
   developer laptop                                       GitHub
  ┌──────────────── deploy/compose ─────────────────┐    ┌──────────────────────────────┐
  │                                                 │    │ Actions on every push:        │
  │  market  (gunicorn, Django 5.2, non-root)       │    │  lint (ruff) → typecheck      │
  │    /health  ── SELECT 1 ──►  postgres:17        │    │  (mypy --strict libs/) →      │
  │    /bench/hello (constant JSON, no DB)          │    │  test-unit (pytest) → ci-gate │
  │        ▲       depends_on: service_healthy      │    └──────────────────────────────┘
  └────────┼────────────────────────────────────────┘
           │ constant-rate HTTP load (oha -q, latency-corrected; fixed CPU/memory limits)
  bench/ harness ──► HDR histogram ──► docs/evidence/s00/bench-hello.csv
                                         (+ git SHA, image digest, CPU, seed)

  libs/atlas-common ── built wheel, pinned by version ──► installed into market image
  libs/atlas-worldgen ── seed + world-spec YAML ──► history rows (COPY) / traffic (locust)   [used from S1]
  pre-commit (ruff, mypy, gitleaks) ── blocks the commit before CI ever sees it
```

**What changed and why.**
- *One deployable, one store.* Everything else is deferred until a measured problem asks for it; that discipline starts now.
- *The healthcheck gates start-up order*, so `market` never boots against a Postgres that is not accepting connections yet.
- *The bench harness sits outside the system under test*, with its own resource limits, so it measures `market` and not the laptop's mood.

---

## 4. Build plan

Each block has a must-tier hour budget, sized for a first attempt at this work. Log the actual hours in `docs/hours.csv` when you close it. If a block runs over, stop *polishing* and write the polish you skipped into `docs/deferred.md`, but finish the block's acceptance criteria: those are never deferred silently.

### 4.0 Django orientation [2.5 h]

**Why this block exists.** Block 4.1 asks you to create a Django project with a settings package, env-driven prod settings and a WSGI entry point for gunicorn. Doing that as your very first contact with Django would mix two unknowns: the framework and Atlas's own rules. So you meet Django first in a throwaway `sandbox/django-ramp/` that nothing imports. It is not a workspace member and is excluded from type checks and coverage. S1's Django ramp continues in the same sandbox.

| # | Resource (official Django 5.2 docs) | What to take from it | Budget |
|---|---|---|---|
| 1 | Tutorial "Writing your first Django app", **part 1** | Project vs app; `runserver`; the root URLconf; a first view | 0.75 h |
| 2 | Tutorial **part 2** | `settings`, `INSTALLED_APPS`, models, `makemigrations` / `migrate`, the Admin | 0.75 h |
| 3 | Topic guide "Django settings" | How Django finds the settings module (`DJANGO_SETTINGS_MODULE`), how settings are loaded, what you must never hard-code | 0.5 h |
| 4 | "Deployment checklist", then run `manage.py check --deploy` on the sandbox | Which settings a production deployment must change, and what the check reports as errors vs warnings | 0.5 h |

**The five pieces 4.1 needs.** Find each one in the docs and answer its question in one line at the top of `docs/learning/fastapi-to-django.md` (S1 adds the full concept-mapping table to the same file):
1. `startproject`: which files does it create, and which one would you turn into a `settings/` package?
2. The settings module path: how do `manage.py` and gunicorn know which settings module to load, and how will you switch between dev and prod without editing code?
3. The root `urls.py`: where does Django look for it, and how does a URL path reach a view?
4. A function view: what does it receive, and what must it return? (`/health` and `/bench/hello` in 4.3 are function views.)
5. The WSGI entry point: which module-level object does gunicorn import, and in which file did `startproject` put it?

**Acceptance criteria**
- The tutorial app runs in the sandbox and you can log in to its Admin.
- The five one-line answers are written.
- You can say, without notes, what `DJANGO_SETTINGS_MODULE` does and which `check --deploy` findings are errors rather than warnings.

### 4.1 Workspace [3.5 h]

**What to build**
- The root `pyproject.toml` declares the workspace and its members, and holds shared tool config (ruff, mypy, pytest).
- `services/market`: a Django 5.2 LTS project, built from the five pieces you found in 4.0. Settings are a package with `base`, `dev` and `prod` modules; `dev` and `prod` import from `base` and override only what differs. No `if DEBUG:` branches scattered through one file (P2 D25–D30 made the same rule).
- Settings read secrets and connection strings from environment variables. The dev defaults are safe to commit; the prod module has **no** defaults for secrets, so a missing variable fails loudly at start-up.
- `libs/atlas-common` with three small things:
  - a frozen `Money` stub (integer minor units plus a currency code; the real one is S1's job);
  - a base error hierarchy that later services share (for example, a "domain error" with a stable machine-readable code);
  - one function that configures structlog for JSON output (one JSON object per log line, with timestamp, level, logger and event).
- `market` depends on `atlas-common` by version range and calls the structlog configuration at start-up.
- A trivial pytest test in each member, so CI has something to run.

**Pain-first**
1. Before creating the workspace, create `atlas-common` as a plain folder and import it from `market` by adding it to `sys.path` or by relative import.
2. Observe: it works on your machine, but `mypy` cannot find it cleanly, the image would have to copy the whole folder, and nothing records which version of the library `market` was built against.
3. Record in `docs/evidence/s00/workspace-before-after.md` a few lines: what broke or felt wrong, and what the workspace changed.

**Acceptance criteria**
- `uv sync` from a clean clone creates one environment; `uv run pytest` passes in both members.
- `uv build` for `atlas-common` produces a wheel whose version matches the library's `pyproject.toml`.
- `market` starts with `DJANGO_SETTINGS_MODULE` pointing at `dev`; with `prod` and no secret variables set, it refuses to start with a clear message.
- `atlas-common` does **not** import Django. It will be used by FastAPI and gRPC services later.

### 4.2 Image [3 h]

**What to build**
- A `market` image built in stages:
  - a **builder stage** that has uv and whatever build tooling the dependencies need, and produces a virtual environment;
  - a **runtime stage** from a slim base that receives only the virtual environment and the application code, and runs as a dedicated non-root user.
- The base image is **pinned** (a specific version tag, ideally also its digest).
- **Layer order:** the dependency layer is built from the lock file and project metadata *before* the application source is copied, so editing a view does not reinstall every dependency. Read the uv documentation page on using uv in Docker (the section on intermediate layers).
- A `.dockerignore` that keeps `.git`, virtual environments, caches, `.env` files and `docs/` out of the build context.
- The `atlas-common` wheel is built and installed by version, as described in 4.1.
- An automated **image test** (a small script or pytest test that runs the container) asserting:
  1. the process user is not root;
  2. no C compiler is on the `PATH` in the runtime image;
  3. the app imports and `manage.py check --deploy` passes with prod settings and dummy secrets. "Passes" means no errors at the default fail level. Warnings such as HSTS or SSL redirect are expected until TLS arrives in S6; list them in `docs/deferred.md`.
  4. `atlas-common` is installed in the image as a regular distribution of the version you declared, not as a path or editable install. Commit the command output that shows it to `docs/evidence/s00/`.

**Pain-first**
1. Write the naive version first, the way many tutorials do: a single stage from the full (non-slim) Python image, which ships a compiler; `COPY . .` then install; running as the default user.
2. Observe and record in `docs/evidence/s00/image-size.md`:
   - the image size (`docker image ls`);
   - the output of `whoami` inside the container (it will be `root`);
   - whether a C compiler is present (it will be);
   - how long a rebuild takes after changing one line in a view (every dependency reinstalls).
3. Rewrite as multi-stage, non-root and cache-friendly. Record the same four observations again, side by side.

**Acceptance criteria**
- The runtime image is measurably smaller than the naive one, and both sizes are committed.
- `docker run --rm <image> whoami` prints your app user, not `root`.
- A one-line code change rebuilds only the last layers (record the rebuild time).
- The image test passes locally and is wired into CI (it can run in the `test-unit` job or its own step).

### 4.3 Compose [2 h]

**What to build**
- `deploy/compose` with two services: `market` and `postgres:17`.
- Postgres has a **real healthcheck**: it asks the server whether it accepts connections for the actual database and user, with an interval, timeout and retry count you chose on purpose.
- `market` waits for Postgres to be *healthy*, not merely *started*.
- `market` exposes `/health`, which runs `SELECT 1` against the database and returns non-200 if it cannot. A health endpoint that returns 200 without touching its dependencies is a lie (P5 D79–D90 named this mistake).
- `market` also exposes `/bench/hello`, a constant JSON response with no DB access, used only by the benchmark in 4.6. Enable it only in dev and benchmark settings, never in prod.
- Named volume for Postgres data; credentials from an env file that is git-ignored, with a committed example file.

**Pain-first**
1. Start with `depends_on` in its short form (start order only) and no healthcheck.
2. Run `docker compose down -v && docker compose up` a few times. Observe `market` crashing or erroring on its first DB access because Postgres is still initialising.
3. Save the failing log to `docs/evidence/s00/compose-race.log`, then add the healthcheck and the `service_healthy` condition, and show the clean start.

**Acceptance criteria**
- From a clean clone: copy the example env file, `docker compose up`, and `/health` returns 200 within a minute.
- Stopping the Postgres container makes `/health` return non-200 (test it by hand; record it).

### 4.4 CI and hooks [3 h]

**What to build**
- A GitHub Actions workflow, `.github/workflows/ci.yml` (the one PR pipeline for the whole season; see [testing-and-ci.md](testing-and-ci.md)), with three jobs in order: **`lint`** (ruff lint and ruff format check) → **`typecheck`** (mypy `--strict` on `libs/`) → **`test-unit`** (pytest). Each later job depends on the earlier one passing. They are followed by a **`ci-gate`** job that `needs` all three and turns their results into one verdict. Branch protection on `main` requires only `ci-gate` (see [testing-and-ci §4.4](testing-and-ci.md#44-required-checks-and-the-gate-job)). Keep the job names stable, because the gate's `needs` list refers to them, and every later stage adds its jobs to that list.
- uv is installed in CI and the lock file is used as-is (a CI run must fail if the lock is out of date, rather than silently re-resolving).
- Dependency caching keyed on the lock file.
- mypy is `--strict` on `libs/` from day one. `market` gets a normal mypy run now; strict mode on the domain arrives in S1.
- **Django and DRF ship no type hints of their own.** Plain mypy on `market` reports errors on the first `import django` unless you decide how to handle that. Decide between the community stubs (`django-stubs` and `djangorestframework-stubs`, with their mypy plugin, which needs to know your settings module) and excluding market's framework imports for now. Record the choice and the stub versions in ADR-001's pin table.
- pre-commit with three hooks: ruff (lint + format), mypy, and **gitleaks** (a secrets scanner). Guiding question: the usual pre-commit mypy hook runs in its own isolated virtualenv. How will it see `atlas_common`, the stubs and your pinned dependencies? (Compare that hook with a local hook that runs mypy from your uv environment.)
- The CI growth matrix in [testing-and-ci.md](testing-and-ci.md) also lists a **compat check** for S0: run `scripts/compat_check.sh` from 4.5 in a separate `weekly.yml` workflow (scheduled plus manual dispatch), not on every push (it pulls images and is slow).

**Pain-first**
1. Create a throwaway branch. Add a file containing something that looks like a real credential (for example, a fake AWS-style key pair or a Postgres URL with a password).
2. Try to commit it. Observe gitleaks blocking the commit and naming the rule it matched.
3. Record the blocked output in `docs/evidence/s00/gitleaks-blocked.txt`. Delete the branch.
4. Also try a commit that breaks ruff formatting and one that introduces a mypy error in `atlas-common`; confirm both are blocked locally and would be blocked in CI.

**Acceptance criteria**
- CI is green on `main` and red on a branch that breaks lint, types or tests (keep a link to one red run in the evidence folder).
- The planted-secret commit is refused by pre-commit.
- Hooks run in under ~10 seconds on a small change; if they are slower, find out why before you get used to skipping them.

### 4.5 Decisions [2.5 h]

Three short ADRs (Architecture Decision Records). An ADR is a one-to-two-page file in `docs/adr/` that records one decision: its context, the options, the choice, the consequences, and what would make you revisit it. Use one template for all of them (see section 8).

**ADR-000 — Django monolith + monorepo.** The decision for `market` and for the repository shape, with the counter-argument written out honestly. It must say where the sunk FastAPI D1–D5 work is reused: `provider-sim` (S5), `atlaspay` (S9) and `ledger` (S12). Details in section 8.

**ADR-001 — Pins and compatibility**, plus `scripts/compat_check.sh`.
- The ADR contains the pin table from [E8 in the README](README.md#e8-stack-pins-compatibility-and-licences-adr-001--adr-003): Python 3.13; Django 5.2 LTS / DRF 3.18.1 / Channels 4.3.2, plus the Django stubs you chose in 4.4; PostgreSQL 17 on every cluster; Timescale 2.30 Community via `timescale/timescaledb-ha:pg17` (never `-oss`); Citus 14.2 on PG17 [U: exact tag]; pgvector 0.8.6; Valkey 9.1; MongoDB 8.0 / PyMongo 4.18; RabbitMQ 4.3 / Celery 5.6.3; aiogram 3.31.0 / Bot API 10.3; grpcio 1.84 / buf v2; Strawberry 0.327; Keycloak 26.7.4 / Authlib 1.8 + joserfc; PgBouncer ≥ 1.24 (prepared statements on by default since 1.24); the S3-compatible object store, **Garage**, with SeaweedFS as the fallback; Mailpit as the dev SMTP server (S2); Traefik or Envoy Gateway via the Gateway API (ingress-nginx is retired: announced 2025-11-11, no releases or security fixes after March 2026 [C]). All pins are *as of 2026-09 — re-check with `scripts/compat_check.sh`*.
- **Why Python 3.13 and PostgreSQL 17, not 3.14 and 18** (write the reasons into the ADR and let `compat_check.sh` confirm them): every pinned library must ship wheels for the Python version you pick (aiogram, grpcio, Strawberry, Authlib and the rest), and every cluster, including the extension-based ones (Citus, Timescale, pgvector), runs one Postgres major that all those extensions support. The price is known: `uuid.uuid7()` arrived in Python 3.14 and `uuidv7()` in PostgreSQL 18 [C], so S1 generates UUIDv7 itself (the SD6 exercise).
- **Why Garage and not MinIO** [C, as of 2026-09]: MinIO stopped publishing community images in 2025 and archived its repository in 2026, so `minio/minio` no longer pulls and receives no fixes. Garage speaks the S3 API, including presigned URLs; S1 verifies presigned PUT and GET on it before relying on them. Code and settings never name the product: they use the `ObjectStorage` port (S1) and generic `S3_*` settings.
- Only `python` and `postgres:17` are used in this stage. The table is written in full now so that each stage starts by re-running the check rather than rediscovering versions.
- `compat_check.sh` requirements (you write it):
  - reads the list of pinned images from one place (not hard-coded in several files);
  - pulls each image and prints the server version and, for Postgres-family images, the available extension versions;
  - flags every row marked [U] with a visible warning;
  - exits non-zero if a pinned tag no longer exists (exactly what would have caught a `minio/minio` pin).
- Commit its first output to `docs/evidence/s00/compat-check.txt`.

**ADR-003 — Licences register.** A table of every third-party component with its licence and a one-line "what this means for us". It is updated each time a store lands. Seed it from [E8](README.md#e8-stack-pins-compatibility-and-licences-adr-001--adr-003)'s licence column: Django/DRF (BSD); PostgreSQL (PostgreSQL licence); Valkey (BSD) vs Redis 8 (RSALv2/SSPLv1/AGPLv3); Citus (AGPL-3.0, matters only if modified and offered as a service); Timescale (TSL / Apache-2 split: CAGGs, compression, retention and `add_job` are TSL features, free to self-host unless offered as a DBaaS); MongoDB server (SSPL, internal use is fine); RabbitMQ (MPL-2.0); OpenSearch (Apache-2.0) vs Elasticsearch (AGPL/SSPL/ELv2); Garage (AGPLv3) vs SeaweedFS (Apache-2.0); Terraform (BSL; OpenTofu MPL); Grafana stack (AGPLv3, self-hosting is fine).

**Acceptance criteria**
- Three ADRs merged, each with a "revisit when" line.
- `compat_check.sh` runs and its output is committed.

### 4.6 Measurement [5.5 h]

This block is large in consequence: every benchmark CSV for the rest of the season follows the protocol you write here. Two pieces: the bench harness with ADR-002 (about 3 h, of which about 35 min are unattended runs: two short hand runs plus 3 protocol runs of ≈11 min each; schedule this in the weekend block), and the world-generator skeleton (about 2.5 h). Do the protocol and the harness first. The generator skeleton may be the thinnest thing that passes its determinism test, because S1 grows it.

#### The benchmark protocol (ADR-002), step by step

A few definitions first:
- **p95 / p99**: the latency below which 95% / 99% of requests finished. They describe the slow tail that users actually feel; the mean hides it.
- **HDR histogram**: a histogram designed for latency that records values with a fixed relative precision across a huge range, so p99 and p99.9 are accurate without storing every sample.
- **Warm-up**: the first period of a run, discarded, while caches, connection pools and the interpreter settle.
- **Coordinated omission**: a trap where a load generator waits for each slow response before sending the next request, so it quietly sends *fewer* requests exactly when the server is slow, and the tail looks better than it is. A constant-arrival-rate load tool avoids it only if each request's latency is measured from the time it was *supposed* to be sent, not from the time it actually went out.
- **Open vs closed load model**: a closed model (a fixed number of virtual users, each waiting for its response before the next request; locust works this way) slows down with the server. An open model sends at a fixed rate regardless. Only the open model gives honest tail percentiles.

The protocol ADR-002 must fix, as numbered steps:

1. **Fix the resources.** The system under test runs with fixed container CPU and memory limits (a dedicated Compose profile or override for benchmarks). The load generator also has its own limits, so it cannot steal CPU from the server. Write down the laptop conditions you control (on mains power, heavy apps closed).
2. **Fingerprint the environment.** Every result records: world-generator version and seed, git SHA, image digests, CPU model, CPU and memory limits. (Adding the Docker version and kernel costs nothing.)
3. **Seed deterministically.** Data comes from `atlas-worldgen` with a recorded seed, never from hand-made fixtures. (`bench/hello` needs no data, but the column exists from the first run.)
4. **Warm up for 60 s** and discard those results.
5. **Measure at least 3 runs** of fixed duration at a fixed target rate. The default duration is 10 min, so one run takes ≈11 min with its warm-up; a scenario may choose a shorter duration if it records it. Intermediate configurations use **3 runs**; the final before/after pair of a split-gate ADR (S6 onward, ADR-023) uses **5 runs**.
6. **Compute p95/p99 from HDR histograms**, per run. Latency is measured from each request's *intended* send time (with oha: a fixed rate `-q <rate>` together with `--latency-correction`, which oha ignores without `-q`). The harness records the per-request latencies into an HDR histogram itself rather than trusting a tool's rounded summary. When a scenario uses locust (the worldgen `traffic` mode) to shape realistic mixed traffic, locust is closed-model: the p95/p99 in ADR tables come from a constant-rate oha probe running alongside, and from S6 on, from server-side histograms as a cross-check.
7. **Report the median** of the per-run values **and the min–max spread**.
8. **Noise rule:** a difference that falls inside the run spread counts as **"no difference"**. You may not claim an improvement smaller than your own noise.
9. **Commit raw output and the summary CSV** to `docs/evidence/sNN/`, next to the claim they support.

A minimal CSV column list for results (a shape, not a solution):
`scenario, run, started_at, git_sha, image_digest, worldgen_version, seed, cpu_model, cpu_limit, mem_limit, target_rps, duration_s, requests, errors, p50_ms, p95_ms, p99_ms, max_ms`

**What to build**
- `bench/` holds the harness (a small Python CLI you write) and one folder per scenario. The harness applies the resource limits, runs the warm-up, runs N measured runs, gathers the fingerprint, and appends rows to the scenario's CSV.
- `bench/hello` drives `/bench/hello` at a fixed rate with a latency-corrected, constant-rate tool (oha; `hey` and plain locust are closed-loop and do not qualify). Its only purpose is to validate the harness and to measure your laptop's **noise floor**: the smallest difference you will ever be able to claim.

**Pain-first**
1. Before writing the protocol, run a load test against `/bench/hello` twice by hand: no limits, no warm-up, one run each, other apps open.
2. Observe how much the two p95 values disagree. Record both in `docs/evidence/s00/bench-noise.md`.
3. Then apply the protocol and record 3 runs. Write two sentences: how much the spread shrank, and what the smallest difference is that you could now call real.

**Acceptance criteria**
- `bench/hello` has 3 recorded runs with every fingerprint column filled.
- ADR-002 contains the nine steps above, the CSV columns, the noise rule and the 3-run / 5-run rule, in your own words.

#### The world-generator skeleton (`libs/atlas-worldgen`)

A **world generator** produces a synthetic but realistic Atlas world (users, vendors and, later, products, orders, payments) from a seed. The same seed and the same world spec always produce the same world. S1 uses it to load 1M products; Season 2 analyses the months of traffic it produces.

**What to build (skeleton only)**
- **Seeded RNG:** every generator receives an explicit random-number generator created from the seed. No module-level `random` calls anywhere; they make output depend on import order and test order.
- **World-spec YAML:** counts, date range, distribution parameters and the seed live in a file, not in code.
- **Generators for users and vendors:** generator functions that yield rows one at a time, so a million rows never sit in memory.
- **`history` mode:** yields COPY-ready rows (tuples or CSV lines in the column order of a target table). The actual COPY loader arrives in S1.
- **`traffic` mode:** a locust entry point whose simulated users draw their actions from the same world spec. For now it can only hit `/bench/hello`.
- **The library version** is exposed in one place and recorded by the bench harness.
- A **determinism test**: two runs with the same seed and spec produce byte-identical output (compare a hash of the first N rows); a different seed produces different output.

**Acceptance criteria**
- `atlas-worldgen` passes mypy `--strict` (it lives in `libs/`).
- The determinism test is green in CI.

### 4.7 Drill [2 h]

The weekly drill hour (one per week, so two in this stage): one SQL problem on the Atlas schema or one DSA problem from the banks, plus the week's interview questions. There is no Atlas schema yet, so in both weeks take one problem from [`../../dsa-problems.md`](../../dsa-problems.md) (write it in the learning repo's `dsa/` convention: docstring, solution, `tests()` with asserts called at module level) and answer half of the interview questions in section 10 out loud, timed, without notes.

### Stretch — Renovate with pin groups [1 h]

Configure Renovate (a dependency-update bot) so that pinned versions get pull requests instead of silent drift. Group related pins (for example, Django + DRF + Channels together; the Postgres family together) so that a compatible set moves as one PR. Record in ADR-001 which groups you chose and why.

### Stretch — Harness calibration [1 h]

Point the harness at a tiny stub server whose latency you control (a fixed delay for most requests, a much longer one for a small, known share). Predict the p50 and p99 the harness should report, commit the prediction, then run. Then make the stub stall once for a few seconds and compare oha with and without `--latency-correction`. That comparison is coordinated omission, measured on your own laptop. Record it in `docs/evidence/s00/harness-calibration.md`.

### Stretch — Worldgen properties [1 h]

Add a Hypothesis property test to `atlas-worldgen`: for any seed and any spec within sane bounds, every generated row respects the spec (counts, date range, non-negative values, references only to rows generated earlier). Pin the Hypothesis seed in CI.

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| The runtime container never runs as root | Dedicated user in the runtime stage | Image test: process user ≠ root |
| The runtime image contains no compiler | Build tooling only in the builder stage | Image test: no C compiler on `PATH` |
| Every image and tool version is pinned | ADR-001 pin table; `compat_check.sh` | `compat_check.sh` exits non-zero on a missing or changed tag |
| No secret reaches git | gitleaks in pre-commit (and in CI from S6) | Planted-secret commit is blocked (evidence file) |
| `market` never starts against an unready database | Healthcheck + `service_healthy` | Clean-clone `compose up` log; `/health` fails when Postgres is stopped |
| `libs/` is fully typed | mypy `--strict` gate | `typecheck` job |
| `atlas-common` is framework-free | No Django import in the library | A test that imports it in an environment without Django (or an import-linter forbidden contract, arriving S1) |
| Same seed + spec ⇒ same world | Explicit RNG passed to every generator | Determinism test |
| Every benchmark number is reproducible | ADR-002 protocol and fingerprint columns | Review: every CSV row has all fingerprint columns filled |

## 6. Tests to write

- A trivial passing test in each workspace member (proves the CI plumbing before real code exists; P1 D1–D6).
- Image test: not root, no compiler, prod settings import with dummy secrets and `check --deploy` reports no errors, `atlas-common` installed as a distribution of the declared version.
- `/health` returns 200 with the DB up (integration test against the Compose Postgres or a throwaway container).
- Settings test: `prod` settings refuse to load without the required secret variables.
- structlog test: a log call produces one parseable JSON object with the expected keys.
- `Money` stub test: construction from an integer, refusal of a float, immutability.
- worldgen determinism test.

## 7. CI changes

| Job | Gates |
|---|---|
| `lint` | ruff lint and ruff format check on the whole repo |
| `typecheck` | mypy `--strict` on `libs/`; plain mypy on `services/market`, with the Django stubs decision from 4.4 |
| `test-unit` | pytest in every member, plus the image test |
| `ci-gate` | `needs` `lint`, `typecheck` and `test-unit`; fails if any of them failed or was cancelled. It is the **only** required status check in branch protection ([testing-and-ci §4.4](testing-and-ci.md#44-required-checks-and-the-gate-job)); every later stage adds its jobs to its `needs` list |
| pre-commit (local) | ruff, mypy, gitleaks on every commit; CI confirms rather than discovers |
| compat check (`weekly.yml`: scheduled + manual) | `scripts/compat_check.sh` output; fails on a missing pinned tag; review it at every stage start |

## 8. ADRs and documents

Use one ADR template everywhere: **Context → Options considered → Decision → Consequences → Numbers / evidence → Counter-argument and answer → Revisit when**.

**ADR-000 — Django monolith + monorepo**
- *Questions it must answer:*
  - Why is `market` Django 5.2 LTS + DRF rather than FastAPI? Use the reasons from [E1](README.md#e1-framework-per-service): the back office (KYC, moderation, refund approval, dispute evidence, ops) is about half of a marketplace; Admin, session auth/CSRF, the migrations graph and the Celery ecosystem come built in; the work is database-bound, so async buys nothing; it is the most-asked stack in your job market.
  - Why 5.2 LTS and not 6.1? Hint: compare each release's end of security support with the length of both seasons on the [Django download page](https://www.djangoproject.com/download/); what would a non-LTS release force you to do mid-season? As a secondary check, look at which Django versions your pinned third-party packages declare as tested (their PyPI classifiers).
  - Why one monorepo rather than a repository per service?
  - What happens to the StockPilot FastAPI work? (Reused in `provider-sim` S5, `atlaspay` S9, `ledger` S12.)
- *Numbers it must contain:* the hours already sunk into FastAPI (about 15); the LTS end date; the share of the product that is back office.
- *Counter-arguments it must address:*
  - "FastAPI reuses your 15 h and is async." Hint: where do those 15 h come back in this plan (§0, item 1), and what kind of product, with how much back office, would make FastAPI the right call for `market`?
  - "Django async is partial; transactions don't work in async mode." Hint: which Atlas workloads actually need async, and which services do they live in ([E1](README.md#e1-framework-per-service))?
  - For the monorepo, "polyrepos give independent versioning and permissions." Hint: which part of that does "consumed by version" (§0) already give you, and what will path filters give you in S5?

**ADR-001 — Pins and compatibility** (section 4.5): the pin table, the [U] rows, why Python 3.13 and PG17, the object-store choice (Garage, SeaweedFS as the fallback) and why, the Django stubs decision (4.4), and the rule that every stage starts by running `compat_check.sh`.

**ADR-002 — Benchmark method** (section 4.6): the nine steps, the fingerprint, the noise rule, how latency is measured (intended send time, HDR histogram, the constant-rate probe beside locust), and the run counts: 3 runs for intermediate configurations, 5 for the final before/after pair of a split-gate ADR. *Counter-argument:* "a single quick run is good enough for a learning project." Hint: argue from the two disagreeing hand-run numbers in `docs/evidence/s00/bench-noise.md`.

**ADR-003 — Licences register** (section 4.5): one row per component, updated as each store lands; the first real decision it records (Valkey over Redis 8) comes in S3.

**Documents:** `docs/deferred.md` (start it now; re-read it at the start of every stage), `docs/hours.csv` (one row per closed block), `docs/learning/fastapi-to-django.md` (the five answers from 4.0), `docs/evidence/s00/*`, the postmortem paragraph in `docs/postmortems/`, the STAR story in `docs/star/`.

## 9. System design session

No SD problem is attached to S0. Instead, read the six-step skeleton at the top of [`../../system-design-problems.md`](../../system-design-problems.md) (clarify scope, estimate scale, high-level design, data model, deep dive, trade-offs) once, slowly. Every SD session from S1 onward uses it, and step 2 ("wrong numbers are fine; no numbers is the mistake") is the same idea as ADR-002. The first session, SD6 (ID generator), comes in [Stage 01](stage-01-layered-monolith.md).

## 10. Interview questions this stage lets you answer

1. Why does your Dockerfile have two stages, and why is the runtime user not root?
2. What does pinning a base image protect you from? What does pinning by digest add over pinning by tag?
3. Why do you measure with a written protocol? What is your noise floor, and how did you find it?
4. uv workspace or a single `pyproject.toml`? When would you split the lock?
5. Why is the dependency layer copied before the source code?
6. What does your healthcheck actually check, and what does `/health` check?
7. Where do secrets live in dev, and what stops one reaching git?
8. What is coordinated omission, and how does your harness avoid it?
9. Why Django for the marketplace when you already know FastAPI? (Your first STAR story.)
10. Why is mypy strict on `libs/` but not yet on the whole service? How did you make mypy understand Django?
11. How does Django find its settings, and what differs between your dev and prod settings?
12. Why does branch protection require one `ci-gate` job instead of every job by name?

## 11. Common mistakes to watch for

- A single-stage image running as root with build tools left in it (P1 D1–D6 named this).
- `COPY . .` before installing dependencies, so every code change reinstalls everything.
- Using `latest` tags, or pinning the Python version but not the base image.
- A healthcheck that only proves the container started; a `/health` that returns 200 without touching the database.
- One `settings.py` full of `if DEBUG:` branches instead of a base/dev/prod split (P2 D25–D30).
- Committing a real `.env`, or putting default secret values in prod settings.
- Making mypy "advisory for now". It never becomes a gate later.
- Benchmarking once, on a busy laptop, and reporting the best number.
- Calling module-level `random` in the generator, so the "same seed" gives a different world depending on test order.
- Letting `atlas-common` import Django "just for one helper".

## 12. How real companies differ

- **Base images.** Larger teams maintain internal hardened base images (or distroless images) and sign them. You pin a public slim image; the lesson (small, non-root, reproducible) is the same.
- **Build systems.** Very large monorepos use Bazel or Pants for incremental builds. A uv workspace with CI path filters (S5) is the right size for one person and a dozen packages.
- **Dependency updates.** Renovate or Dependabot run for every repo, with auto-merge for patch releases. You do it by hand (or as the stretch) so you understand what the bot is doing.
- **Performance testing.** Mature teams run continuous benchmarks on dedicated hardware and alert on regressions. Your laptop protocol with a noise rule is the honest small-scale version of that.
- **Supply chain.** Production pipelines add SBOMs, image signing and vulnerability scanning (Trivy and pip-audit arrive in S6).

## 13. Deliberately not doing

| Item | Why not now | When |
|---|---|---|
| Any feature (catalog, users, orders) | Measurement and hygiene come first | [Stage 01](stage-01-layered-monolith.md) |
| A second service | Nothing forces it; the split gate decides every extraction | `provider-sim` S5 (an external emulator); first real split S8 |
| Kubernetes | One container does not need an orchestrator | S10 |
| Image push to GHCR, Trivy, pip-audit | Nothing is deployed yet | S6 |
| Nginx | One service, nothing to route | S6 |
| Redis, RabbitMQ, the S3-compatible object store | No measured need yet | Object store (Garage) S1, Redis S3, RabbitMQ S4 |
| Real traffic scenarios in worldgen | Only the skeleton is needed to prove determinism | Grows each stage (1M products in S1) |

## 14. Stretch

Only if the must tier closed early (the Stretch subsections at the end of section 4), in this order:
- **Renovate with pin groups [1 h].**
- **Harness calibration [1 h]:** a stub server with a known latency; coordinated omission with and without latency correction.
- **Worldgen properties [1 h]:** a Hypothesis property test over seeds and specs.

## 15. Definition of done

- [ ] The sandbox tutorial app runs; the five one-line answers from 4.0 are at the top of `docs/learning/fastapi-to-django.md`.
- [ ] A clean clone runs `docker compose up` and `/health` returns 200.
- [ ] CI (`lint` → `typecheck` → `test-unit` → `ci-gate`) is green on `main`; branch protection requires only `ci-gate`; one red run on a broken branch is linked in the evidence.
- [ ] Image size before and after multi-stage committed; `whoami` is not root; the no-compiler test passes.
- [ ] A planted secret was blocked by pre-commit (evidence committed).
- [ ] `atlas-common` builds as a wheel, and the image contains it as an installed distribution of the declared version (not a path or editable install); the command output is committed.
- [ ] `bench/hello` has 3 runs recorded under ADR-002, with all fingerprint columns, measured latency-corrected at a constant rate.
- [ ] `atlas-worldgen` skeleton with a green determinism test.
- [ ] ADR-000, ADR-001 (with `compat_check.sh` output and the Django stubs decision), ADR-002, ADR-003 merged.
- [ ] `docs/deferred.md` started.
- [ ] `docs/hours.csv` has one row per block of this stage, with budget and actual.
- [ ] Postmortem paragraph written (what took longer than budgeted and why, using the numbers in `docs/hours.csv`).
- [ ] 1 STAR story in `docs/star/`: choosing Django despite the sunk FastAPI work.
- [ ] Tagged `v0.0`.

## 16. If you get stuck

- **Django orientation.** If the tutorial app will not start: which settings module is it loading (print `DJANGO_SETTINGS_MODULE`), and is the app listed in `INSTALLED_APPS`? If `check --deploy` output looks alarming: which lines are errors and which are warnings, and which of them only matter once there is TLS (S6)?
- **Workspace.** Ask yourself: which file decides which packages are members, and which file decides that `market` depends on `atlas-common`? If `uv run` cannot import the library, run `uv tree` and check whether it appears as a workspace member. Reread the uv docs on workspaces, not a blog post.
- **Image.** If the image is still large: which stage are you copying from, and what exactly are you copying? If the rebuild is still slow: what is the first `COPY` instruction that includes a file you edit often? If `whoami` still prints root: in which stage did you switch user? Reread P1 D1–D6 ([../python/01-stockpilot.md](../python/01-stockpilot.md), Stage 1) and [phase-1 D23](../../phase-1-foundations.md) on layer caching.
- **Compose.** If `market` still races Postgres: is your `depends_on` using a *condition*, and does the healthcheck test the database your app uses, with the user your app uses?
- **CI.** If CI passes locally and fails remotely: is CI using the lock file as-is, or re-resolving? Is a tool reading config you only have locally? If `typecheck` goes red on the first `import django`: did you decide between the Django stubs (with their plugin and a settings module for it) and excluding the framework imports, and is that decision in ADR-001? If a PR can never merge: is branch protection waiting for a job that was skipped, instead of for `ci-gate`?
- **Hooks.** If gitleaks does not fire: is the hook scanning staged changes, and does your planted string look like any rule it knows? If the mypy hook fails where CI passes (or the reverse): which environment does the hook run in, and can it see `atlas_common`, the stubs and your pinned dependencies?
- **Benchmark.** If your 3 runs still disagree wildly: is the load generator limited to its own CPUs? Is anything else running? Are you using a constant arrival rate, or a closed loop that slows down with the server? Is oha given both `-q` and `--latency-correction`?
- **Worldgen.** If the determinism test is flaky: search the package for any call to the module-level random functions, and for anything that iterates over a set or reads the current time.
- **ADR-000.** If the argument feels weak: write the strongest version of the FastAPI case first, as if a colleague were defending it, and then answer it. Reread P2's framework-choice rationale ([../python/02-quickserve-pos.md](../python/02-quickserve-pos.md), D25–D30): "I used what I know" is not an answer.

Next: [Stage 01 — Layered monolith](stage-01-layered-monolith.md).
