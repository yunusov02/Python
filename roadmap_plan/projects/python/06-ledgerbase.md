# Project 6 — LedgerBase

**Double-entry accounting & invoicing platform**

| | |
|---|---|
| Domain | FinTech |
| Level | Middle |
| Phase | 4 — Microservices & Infrastructure |
| Weeks | 16–18 (D91–D108) |
| Stack | FastAPI (ledger-service), Django/DRF (invoicing-service), PostgreSQL (**triggers, window functions, matviews**), Redis, Celery Beat, Nginx (**TLS / Let's Encrypt**), **Prometheus + Alertmanager + Grafana + Loki + Tempo/Jaeger (OpenTelemetry) + Sentry**, GitHub Actions (full CD, **staging + prod**), `pip-audit` / `gitleaks` / Trivy, Docker Compose |
| Repo | `ledgerbase/` |

> **Three things make this project.** Money as integer cents — learned by writing
> the float version first, on purpose. The **first real synchronous
> service-to-service write**, which is therefore the first to need resilience
> patterns. And the deployment and observability work that four services finally
> justify — deploy **with TLS**, migrate **without downtime**, and observe with
> **metrics, logs and traces** together rather than metrics alone.
>
> It is also the project where Postgres stops being "a place to put rows":
> a **constraint trigger** enforces the one rule a `CHECK` cannot, a **window
> function** produces the running balance, and a **materialized view** serves
> the trial balance.

---

## 1. Business Problem

A freelancer or small agency needs to issue invoices, record payments against
them, and see a real ledger — every transaction recorded as a balanced
debit/credit pair — instead of a spreadsheet that silently drifts from reality.
An accountant must be able to trace **every number to a specific journal entry**.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. A chart of accounts and a journal where every entry balances
2. Invoices and payments, with each payment producing a ledger entry
3. A trial-balance report that actually reconciles — as a live query **and** as a
   materialized view, timed against each other
3a. `GET /accounts/{id}/ledger` with a **running balance** computed by a window
   function, and a **streaming CSV export** of a million journal lines that never
   loads them into memory
4. `invoicing-service` calling `ledger-service` behind retry + a hand-rolled
   circuit breaker
5. Overdue-invoice reminders on Celery Beat
6. Four services behind one Nginx gateway, sharing CarePoint's `auth-service`

**Operational capability — the real payoff of this project**
7. A full CI/CD pipeline: build → push → **staging** → **prod** over SSH with a
   **zero-downtime deploy**, behind **HTTPS** (Let's Encrypt), with **graceful
   shutdown** so the old container finishes in-flight requests
7a. A schema change shipped with the **expand/contract** pattern across three
   deploys, with `CREATE INDEX CONCURRENTLY` and a `lock_timeout`, under load,
   with zero errors
7b. One **versioned API** (`/v1` → `/v2`) on `ledger-service`, with a deprecation
   window, because PayFlow and AtlasMarket will depend on this contract
8. Security gates that fail the build: `pip-audit`, `gitleaks`, Trivy
9. Prometheus scraping four services, **RED** dashboards in Grafana, **Alertmanager**
   firing a real alert to a (mock) Slack channel
9a. **Loki** aggregating every service's structured logs, searchable by `request_id`
9b. **OpenTelemetry tracing**: one trace for `POST /invoices/{id}/payments` spanning
   Nginx → invoicing-service → ledger-service → Postgres, visible in Tempo/Jaeger
10. Sentry across all four services

**Proof it is correct**
11. A regression test for the float-drift bug you deliberately created
12. An unbalanced entry rejected by the database even when app validation is bypassed — by a **deferrable constraint trigger**, because a `CHECK` cannot see other rows
13. A circuit breaker verified against a killed dependency
14. A deliberately broken health check proving the deploy **aborts** and the old
    version stays live
15. An injected bug found **via Sentry first**, before reading the code

---

## 3. Scope

**In scope**
- Chart of accounts, journal entries, journal lines
- Invoices and payments
- Trial balance
- Resilience on the cross-service call
- Overdue-invoice reminders
- Full CI/CD with zero-downtime deploy and rollback
- Prometheus / Grafana / Sentry
- HTTPS, staging environment, graceful shutdown, expand/contract migrations
- Loki, Alertmanager, OpenTelemetry tracing
- Postgres triggers / PL/pgSQL, window functions, materialized views
- Streaming export, API versioning

**Out of scope**

| Deferred | Why |
|---|---|
| Multi-currency ledger | Doubles the modelling with no new infrastructure lesson |
| PDF export | Presentation. **CSV export is in scope** — not for the format, but because streaming a million rows without loading them is a backend skill |
| Automated bank-reconciliation import | Real feature, no new lesson here |
| **Caching of account balances — deliberately not done** | Financial data; staleness risk outweighs read speed. Be ready to say so |
| Idempotency on payment posting | PayFlow (Phase 6) does this properly |

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`bookkeeper`** | Create invoices, record payments, view invoices and the ledger | Post a manual journal entry; change the chart of accounts |
| **`accountant`** | Everything a bookkeeper can, plus post manual journal entries and run the trial balance | Delete a posted entry — nothing can. Corrections are reversing entries |
| **`admin`** | Manage the chart of accounts and users | Bypass the balance rule; the database refuses regardless of role |
| **`service` (machine)** | `invoicing-service` calling `ledger-service` | Anything not needed for posting an entry — a scoped machine credential, not an admin token |

Auth reuses CarePoint's `auth-service` with **zero duplicated auth code for a
brand-new service** — the first real proof that the split paid off.

**One rule that overrides every role:** nothing and nobody can post an unbalanced
entry, or delete a posted one. Correction happens by posting a reversing entry, so
history stays intact. That is what makes the ledger auditable.

---

## 5. Functional Modules

### 5.1 Chart of accounts
Accounts typed as asset / liability / equity / revenue / expense. The type
determines whether a debit increases or decreases the balance — encode that once,
in one place.

### 5.2 Journal
An entry is a description plus two or more lines. Each line hits one account, and
carries **either** a debit **or** a credit, never both. The entry balances or it
does not exist.

### 5.3 Invoicing
Invoices with a total, an issue date and a due date. Payments applied against
them. Each payment posts a journal entry through `ledger-service`.

### 5.4 Reporting
Trial balance: every account with its debit and credit totals, summing to equal
grand totals. If it does not reconcile, something upstream is wrong — that is the
report's job.

### 5.5 Reminders
Overdue-invoice reminders on Celery Beat.

---

## 6. Architecture

```
Nginx
  ├─► auth-service        (from CarePoint — reused)
  ├─► clinic-service      (CarePoint)
  ├─► invoicing-service   (Django/DRF)  ──sync call──►  ledger-service
  └─► ledger-service      (FastAPI, core accounting logic)
```

```
ledgerbase/
  ledger-service/       # FastAPI, core accounting logic
  invoicing-service/    # Django/DRF, invoices + payments, calls ledger-service
```

**Write down the moment Compose stops feeling manageable** — four services plus
Postgres, Redis, RabbitMQ, MinIO and Nginx. That note is the honest input to
Phase 5's Kubernetes work.

---

## 7. Domain Model

```
accounts(id, name, type[asset|liability|equity|revenue|expense])

journal_entries(id, description, created_at)

journal_lines(id, journal_entry_id, account_id, debit_cents, credit_cents)
    -- CHECK: exactly one of debit_cents / credit_cents is non-zero   (one row)
    -- CHECK: both >= 0                                                (one row)
    -- CONSTRAINT TRIGGER (DEFERRABLE INITIALLY DEFERRED): at commit,
    --   SUM(debit) = SUM(credit) per journal_entry                    (many rows)
    -- TRIGGER: BEFORE UPDATE OR DELETE → RAISE EXCEPTION            (append-only)

invoices(id, client_name, total_cents, status, issued_at, due_at)

payments(id, invoice_id, amount_cents, journal_entry_id, received_at)

trial_balance_mv  -- MATERIALIZED VIEW over journal_lines, unique index on account_id
```

---

## 8. The Two Invariants (defense in depth) — and why one of them needs a trigger

1. **Every journal entry balances:** `SUM(debit_cents) = SUM(credit_cents)`.
   Validated in the service layer **and** refused by the database.
2. **Every line is one-sided:** a `CHECK` constraint ensures exactly one of
   `debit_cents` / `credit_cents` is non-zero.

Application validation catches it early with a good error message. The DB
constraint catches it when someone bypasses the service layer — a management
command, a data migration, a psql session, a future service.

**Invariant 2 is a `CHECK`. Invariant 1 cannot be.** A `CHECK` constraint sees
one row; balance is a property of *all* the lines of an entry, and they are
inserted one statement (or several) at a time — after the first line, the entry
is *always* unbalanced. The tool for a multi-row invariant is a **deferrable
constraint trigger**:

```sql
CREATE OR REPLACE FUNCTION assert_entry_balanced() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  v_debit  bigint;
  v_credit bigint;
BEGIN
  SELECT COALESCE(SUM(debit_cents),0), COALESCE(SUM(credit_cents),0)
    INTO v_debit, v_credit
    FROM journal_lines
   WHERE journal_entry_id = COALESCE(NEW.journal_entry_id, OLD.journal_entry_id);
  IF v_debit <> v_credit THEN
    RAISE EXCEPTION 'journal entry % is unbalanced (debit %, credit %)',
      COALESCE(NEW.journal_entry_id, OLD.journal_entry_id), v_debit, v_credit
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NULL;
END $$;

CREATE CONSTRAINT TRIGGER journal_entry_balanced
  AFTER INSERT OR UPDATE OR DELETE ON journal_lines
  DEFERRABLE INITIALLY DEFERRED
  FOR EACH ROW EXECUTE FUNCTION assert_entry_balanced();
```

`DEFERRABLE INITIALLY DEFERRED` is the whole trick: the check runs **at
commit**, when all lines are present. Inside the transaction the entry may be
temporarily unbalanced; it can never *become durable* that way.

A second, simpler trigger makes the ledger **append-only in the database**:
`BEFORE UPDATE OR DELETE ON journal_lines` (and `journal_entries`) → `RAISE
EXCEPTION`. Corrections are reversing entries; the service layer already refuses
edits, and now `psql` does too.

Write `docs/triggers-notes.md`: when a trigger is the right tool (multi-row
invariants, append-only enforcement, audit stamps) and when it is the wrong one
(business logic hidden from the application, silent side effects, performance on
bulk loads). Triggers have a bad reputation because of the second list; know
both.

**You will prove this** by injecting an unbalanced entry directly past app
validation (`psql`, two `INSERT`s, `COMMIT`) and watching the commit fail, and by
trying `UPDATE journal_lines SET debit_cents = 0` and watching it refuse.

---

## 9. API Design

| Method | Path | Service | Role | Notes |
|---|---|---|---|---|
| POST | `/journal-entries` | ledger | accountant / service | Must balance, or `422` |
| GET | `/accounts/{id}/balance` | ledger | bookkeeper+ | **Not cached** — deliberately |
| GET | `/accounts/{id}/ledger` | ledger | bookkeeper+ | Every line with a **running balance**: `SUM(...) OVER (PARTITION BY account_id ORDER BY created_at, id)`; keyset paginated |
| GET | `/journal-lines/export.csv` | ledger | accountant+ | **Streaming**: `StreamingResponse` + a generator over a server-side cursor (`yield_per`). Constant memory at 1M rows |
| GET | `/reports/trial-balance` | ledger | accountant+ | Live aggregate **or** `trial_balance_mv` (`?source=mv`), both timed |
| POST | `/v2/journal-entries` | ledger | accountant / service | The **versioned** contract: `v2` returns lines with running balances and renames a field. `v1` stays for a written deprecation window with a `Deprecation` header |
| POST | `/invoices` | invoicing | bookkeeper+ | |
| POST | `/invoices/{id}/payments` | invoicing | bookkeeper+ | Calls ledger-service to post the entry |
| GET | `/health` | all | internal | |
| GET | `/metrics` | all | internal | Prometheus scrape target |

---

## 10. Resilience — the first real cross-service call

`invoicing-service → ledger-service` is the system's first genuine synchronous
service-to-service **write**. It therefore gets the resilience treatment.

**Retry with exponential backoff** on transient failure — plus a **hand-rolled
circuit breaker**:

| State | Meaning | Transition |
|---|---|---|
| `closed` | Normal; calls pass through | → `open` after N consecutive failures |
| `open` | Fail fast; no call attempted | → `half-open` after a cooldown |
| `half-open` | One trial call allowed | Success → `closed`; failure → `open` |

**Verification:** kill `ledger-service` mid-call and confirm the circuit trips and
`invoicing-service` fails **clean** (`409`/`503`) instead of hanging.

**Why retry alone is not enough:** retrying into a dead dependency amplifies load
on something already failing, and holds your own workers hostage waiting on
timeouts. The breaker's job is to stop *trying* — and, just as importantly, to
start trying again on its own.

A breaker that never half-opens is worse than no breaker: one incident leaves you
permanently degraded until someone restarts a process.

## 10a. SQL that earns its name here

| Need | Feature | Note |
|---|---|---|
| Running balance per account | **Window function**: `SUM(credit - debit) OVER (PARTITION BY account_id ORDER BY created_at, id ROWS UNBOUNDED PRECEDING)`; `LAG()` for "change since previous line"; `ROW_NUMBER()` for keyset cursors | The single most-asked SQL interview topic. Build it, `EXPLAIN` it, and know why the `(account_id, created_at, id)` index makes it a single ordered scan |
| Trial balance | **Materialized view** with a unique index on `account_id`; `REFRESH MATERIALIZED VIEW CONCURRENTLY` from a Beat job or after each posting; compare to the live `GROUP BY` at 1M lines | Financial data — so document the staleness window and show it on the response (`as_of`). This is *not* a cache in the Redis sense: it is rebuilt from the source of truth, never invalidated by a code path you might forget |
| Append-only and balance | **Triggers** (§8) | The only two triggers in the whole curriculum, both defensible |
| Million-row export | **Server-side cursor** (`yield_per`, or `cursor.itersize` in psycopg) + a generator + `StreamingResponse` | Watch RSS in a profiler with and without streaming; record both numbers |

---

## 11. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **Nginx + TLS** | One entrypoint routing to all four services, **terminating HTTPS** with a Let's Encrypt certificate (`certbot`, auto-renewal), HTTP→HTTPS redirect, HSTS. Nothing in this roadmap has been served over TLS until now; the VPS deploy is where it starts | Extended from CarePoint, not re-derived. Every deployed system you will ever touch has TLS in front of it — configure it once by hand so it is not magic |
| **Staging environment** | A second Compose stack (second VPS or a second project on the same one) fed by the same pipeline: `main` → staging automatically, staging → prod on a manual approval in GitHub Actions. Same images, different config | "We deploy straight to prod" is not a sentence a middle+ engineer says out loud. Environment parity and promotion are the lesson |
| **PostgreSQL** | Ledger and invoicing data | |
| **Redis — Celery broker** | Overdue-invoice reminders | Reused |
| **Celery Beat + worker** | The reminder job | Third time building this pattern — it should be fast now |
| **Circuit breaker (in-process)** | `invoicing-service`'s HTTP client for `ledger-service` | In-process state is correct here; a shared breaker across replicas is a distinct, harder problem — name it |
| **Prometheus** | Scrapes `/metrics` on all four services, plus Postgres and RabbitMQ exporters. Metrics follow **RED** per endpoint (rate, errors, duration as a histogram with sane buckets); **no high-cardinality labels** (never `user_id`, `invoice_id`) | Four services is the first point where comparing them is meaningful. Know what a histogram bucket is and why `p95` from a summary cannot be aggregated across replicas |
| **Alertmanager** | Rules: `5xx ratio > 1% for 5m`, `p95 > 800ms for 10m`, `circuit breaker open for 2m`, `celery queue depth > N`; routed to a mock Slack webhook (or a local receiver) | A dashboard nobody is looking at is not monitoring. PayFlow's on-call drill needs something that *pages*; build it here |
| **Grafana** | Dashboards: RED per service, queue depth, breaker state — and, via Loki and Tempo data sources, logs and traces in the same UI | Build the dashboard you would actually open at 3am |
| **Loki + Promtail** (or Alloy) | Ships every container's stdout (structured JSON from `structlog`/Django) to Loki; label by service; search by `request_id`, `trace_id` | Four services + workers = eight log streams. `docker logs` in eight terminals is not observability |
| **OpenTelemetry → Tempo (or Jaeger)** | OTel SDK in both frameworks, auto-instrumentation for HTTP clients, SQLAlchemy/psycopg and Celery; `traceparent` propagated on the invoicing → ledger call and into Celery task headers; `trace_id` injected into every log line | The first synchronous cross-service call is the first time "where did the time go?" has two answers. A trace shows both. Metrics say *that* it is slow; traces say *where* |
| **Sentry** | All four services | Stack traces with context that logs do not give you fast enough |
| **GHCR** | Images for all four services | |
| **GitHub Actions** | Build → security gates → push → deploy to **staging** → manual approval → deploy to **prod**; zero-downtime rollover on each | The full pipeline lands here |
| **Dockerfiles** | Multi-stage, non-root, pinned base, `HEALTHCHECK`; Trivy findings traced to image layers | Started in StockPilot; here four images make the discipline pay off in scan time and attack surface |
| **Graceful shutdown** | `uvicorn --timeout-graceful-shutdown`, `gunicorn --graceful-timeout`, Celery warm shutdown on `SIGTERM`; Compose `stop_grace_period` | Step 7 of the deploy ("stop the old container") drops in-flight requests unless the process finishes them. Zero-downtime is a property of the *process*, not only of the proxy switch |
| **`pip-audit`** | CI step — dependency CVEs | **Fails the build** on high severity |
| **`gitleaks`** | CI step — committed secrets | **Fails the build** |
| **Trivy** | CI step — container image scan | **Fails the build** on high severity |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Redis cache on `/accounts/{id}/balance`** | It is financial data read for decisions. A stale balance is a wrong answer, and "it was slow" is not a defence. **This is the deliberate contrast with QuickServe's product cache** |
| **A message broker between invoicing and ledger** | The call is a synchronous write that the caller needs an answer to. Making it async would change the semantics, not just the transport — say why |
| **Kubernetes** | You are about to feel Compose strain. Feel it fully first; Phase 5 acts on it |
| **A distributed circuit breaker** | In-process is right at this scale. Know that replicas each hold their own state, and what that implies |

---

## 12. Zero-Downtime Deploy

```
1. CI builds and pushes new images
2. Security gates pass (pip-audit, gitleaks, Trivy) — or the build fails here
3. SSH to the VPS, pull the new images
4. Start the NEW container alongside the old one
5. Poll its /health until it passes  ── if it never passes: ABORT, leave old live
6. Switch the Nginx upstream to the new container
7. Stop the old container
```

**Test the abort path deliberately.** Break the new version's health check on
purpose and confirm the deploy stops at step 5 with the old version still serving
traffic. A rollback path you have never exercised is a rollback path you do not
have.

**Test step 7 under load.** Run `hey` against the endpoint during the rollover.
Without graceful shutdown you will see a burst of connection resets at step 7;
with `SIGTERM` handled and `stop_grace_period` set, zero errors. Record both.

### 12a. Zero-downtime *schema* changes — expand/contract

The deploy above rolls the code with no downtime. The schema is the harder half:
during the rollover, **old and new code run against the same database at the
same time**, so every migration must be compatible with both.

Ship one real change this way — rename `journal_entries.description` to `memo`:

| Deploy | Migration | Code |
|---|---|---|
| 1 — **expand** | `ADD COLUMN memo text` (nullable, no default — instant) | Write both columns, read `description` |
| between | Backfill in batches of 10k with `UPDATE ... WHERE id BETWEEN` and a sleep; never one giant `UPDATE` that locks the table and bloats WAL | — |
| 2 — **migrate reads** | `ALTER COLUMN memo SET NOT NULL` (after backfill) | Read `memo`, still write both |
| 3 — **contract** | `DROP COLUMN description` | Read and write `memo` only |

Rules that go with it, each demonstrated once:

- `SET lock_timeout = '3s'` at the top of every migration. A DDL waiting for an
  `ACCESS EXCLUSIVE` lock blocks **every** query behind it; better to fail and retry.
- `CREATE INDEX CONCURRENTLY` — never a plain `CREATE INDEX` on a live table.
  Alembic needs `op.execute` outside a transaction for this; know why.
- `ADD COLUMN ... DEFAULT <constant>` is instant on PG11+; `DEFAULT now()` or a
  volatile default rewrites the table. Know the difference.
- Never rename or drop in the same deploy that stops using the column.
- A migration that cannot be rolled back (data destroyed) must say so in its
  docstring and be shipped alone.

This closes the question StockPilot asked in Week 4 ("what is your rollback
strategy if a migration fails mid-deploy?") with something you have actually done.

### 12b. API versioning

PayFlow (Phase 6) and AtlasMarket will call `ledger-service`. Introduce a
breaking change on purpose — `POST /v2/journal-entries` returns lines with
running balances and renames `description` → `memo` in the payload — and keep
`/v1` alive with a `Deprecation` and `Sunset` header for a written window.
Decision record: URL versioning vs header versioning vs additive-only changes,
and why you picked URL for this service.

---

## 13. Build Plan (consolidated)

### Stage 1 — The float mistake, on purpose *(D91–D93, Week 16)* *(v2: +1 day)*
- New repo `ledgerbase/`; `Account`, `JournalEntry`, `JournalLine` models —
  **float version, deliberately**
- Generate a trial balance that **does not reconcile** because of float drift
- Fix: convert every money field to **integer cents**
- Add a regression test that would have caught the original bug
- `CHECK` constraints on `journal_lines` + app-level balance validation
- **Deferrable constraint trigger** for balance; append-only triggers; prove both
  from `psql`. `docs/triggers-notes.md`
- `GET /accounts/{id}/ledger` with the **window-function** running balance

> Do not skip the broken version. Watching a report fail to reconcile by 0.03 is
> the lesson. Being told "use integers" is not the same thing, and an interviewer
> can tell the difference in ten seconds.

### Stage 2 — Invoicing & resilience *(D94–D96, Week 16)* *(v2: +1 day)*
- `Invoice`, `Payment` models
- `invoicing-service` calls `ledger-service`, wrapped in **retry + circuit breaker**
- `GET /reports/trial-balance` — live and `trial_balance_mv`, timed at 1M lines
- Streaming CSV export with a server-side cursor; memory measured
- Add `ledgerbase` to Nginx routing
- Kill `ledger-service` mid-call; confirm a clean failure, not a hang

### Stage 3 — Full CI/CD & zero-downtime deploy *(D97–D101, Week 17)* *(v2: +3 days)*
- Multi-stage, non-root Dockerfiles for all four services
- CI builds and pushes images for all four services
- Add `pip-audit`, `gitleaks`, Trivy as **failing** gates
- **TLS**: certbot on the VPS, Nginx terminates HTTPS, redirect + HSTS
- **Staging** stack; pipeline promotes staging → prod on manual approval
- Deploy step: SSH, pull, health-gated rollover, Nginx upstream swap
- **Graceful shutdown** in every process; rollover under `hey` with zero errors
- **Break the new version's health check** and confirm the abort path
- **Expand/contract**: the `description → memo` change across three deploys, under
  load, with `lock_timeout` and `CREATE INDEX CONCURRENTLY`
- `/v2/journal-entries` + deprecation headers on `/v1`; `docs/api-versioning.md`
- End to end: push to `main` → staging → approve → prod, verified live over HTTPS

### Stage 4 — Observability stack *(D103–D108, Week 18)* *(v2: +3 days)*
- `/metrics` on all four services (RED, histograms, no high-cardinality labels);
  Prometheus scrape config
- **Alertmanager** with the four rules above → mock Slack; fire one on purpose
- **Loki + Promtail**; search one `request_id` across all services
- **OpenTelemetry** in both frameworks; `traceparent` across the sync call and into
  Celery; `trace_id` in logs; one payment traced end to end in Tempo/Jaeger
- Grafana: RED per service, queue depth, breaker state; Loki and Tempo as data sources
- Sentry across all four services
- **Inject an unbalanced-entry bug past app validation and find it via a Sentry
  alert before looking at the code**
- `docs/postmortem-phase4.md`, full CI green, tag `v0.4-phase4`

---

## 14. Testing Strategy

| Layer | What |
|---|---|
| **Regression** | The float-drift bug — a test that would have caught it |
| Unit | Balance validation; the one-sided line rule; debit/credit direction per account type |
| **DB** | An unbalanced entry is rejected by the `CHECK`/constraint even when app validation is bypassed entirely |
| Integration | Invoice → payment → journal entry posted correctly, and the trial balance still reconciles |
| **Resilience** | Circuit breaker trips after N failures, half-opens after cooldown, closes on success |
| Resilience | `ledger-service` down → `invoicing-service` returns `409`/`503` **fast**, does not hang |
| **Deploy** | A failing health check on the new version aborts the deploy and leaves the old one live |
| Security | CI fails on a planted high-severity dependency, a planted secret, and a vulnerable base image |
| Observability | The injected bug produces a Sentry event with enough context to locate it |
| **Trigger** | Two unbalanced `INSERT`s then `COMMIT` in `psql` → commit fails with `check_violation`; `UPDATE`/`DELETE` on posted lines refused |
| Window | Running balance equals a Python fold over the same lines; plan is a single ordered scan on the account index |
| Matview | `trial_balance_mv` after `REFRESH ... CONCURRENTLY` equals the live query; `as_of` exposed |
| Streaming | Exporting 1M lines: RSS stays flat (measured), first byte arrives before the last row is read |
| **Graceful shutdown** | Rollover under `hey`: zero connection errors with `SIGTERM` handled; the burst of errors without it is recorded |
| **Expand/contract** | Each of the three migrations applied while old and new code run together under load — zero errors; `lock_timeout` makes a blocked DDL fail fast instead of queuing traffic |
| TLS | `curl http://` redirects to `https://`; certificate valid; HSTS present |
| Staging | The same image SHA is what reaches prod after approval |
| Versioning | `/v1` still serves with `Deprecation` header; `/v2` contract tested; a client pinned to `/v1` is unaffected by the rename |
| **Tracing** | One `trace_id` spans Nginx → invoicing → ledger → Postgres spans; the same id appears in Loki for all three |
| Alerting | Kill `ledger-service`: the breaker-open alert fires within its `for` window and resolves after recovery |

---

## 15. Definition of Done

- [ ] Money is integer cents everywhere; float regression test in place
- [ ] Double-entry enforced at both app and DB level, proven by bypassing the app
- [ ] Trial balance reconciles
- [ ] Circuit breaker verified against a killed dependency, including half-open recovery
- [ ] CI builds and pushes all four images
- [ ] `pip-audit`, `gitleaks`, Trivy all failing the build on planted problems
- [ ] Zero-downtime deploy working, **including the abort path**
- [ ] Prometheus + Grafana + Sentry live across all four services
- [ ] Injected bug found via Sentry first
- [ ] Read-replica scaling note written
- [ ] Deferrable constraint trigger + append-only triggers, proven from `psql`; `docs/triggers-notes.md`
- [ ] Running-balance ledger endpoint (window function), keyset paginated
- [ ] `trial_balance_mv` vs live query, timed; streaming CSV export with flat memory
- [ ] HTTPS with auto-renewing certificate; HSTS
- [ ] Staging → prod promotion with manual approval
- [ ] Graceful shutdown; rollover under load with zero errors
- [ ] Expand/contract migration shipped in three deploys under load
- [ ] `/v2` with deprecation headers on `/v1`; `docs/api-versioning.md`
- [ ] Alertmanager rules firing; Loki searchable by `request_id`; one end-to-end trace in Tempo/Jaeger
- [ ] Multi-stage, non-root images for all four services
- [ ] The "Compose stopped being manageable" note written
- [ ] `docs/postmortem-phase4.md`, tag `v0.4-phase4`

---

## 16. Scaling Notes (written)

Read-replica strategy for `trial-balance` reporting once write volume grows — a
concrete Phase 5 callback. Plus: what you would do if `ledger-service` became the
bottleneck, and why sharding a ledger is harder than sharding most things.

---

## 17. Interview Questions This Project Should Let You Answer

1. Why store money as integer cents — show me a concrete float bug you hit.
2. How do you enforce double-entry balance at both app and DB level, and why both?
3. Walk me through your zero-downtime deploy, step by step — including what
   happens when the new version is broken.
4. What does Sentry catch that your logs alone wouldn't have surfaced as fast?
5. Why didn't you cache account balances, when you did cache product search?
6. Walk through your circuit breaker's three states — what moves it between them,
   and why isn't retry-with-backoff alone enough?
7. Your circuit breaker is in-process. What happens with three replicas?
8. What do `pip-audit`, `gitleaks` and Trivy each catch, and why fail the build
   rather than warn?
9. How do you correct a mistaken journal entry?
10. Why can a `CHECK` constraint not enforce "the entry balances", and what does
    `DEFERRABLE INITIALLY DEFERRED` change?
11. When is a database trigger the right tool, and when is it a trap?
12. Write the running-balance query. Why does the frame matter, and what index makes it fast?
13. Materialized view or Redis cache for the trial balance — they both hold stale
    data, so why is one acceptable here and the other not?
14. How do you export a million rows without running out of memory?
15. Walk me through renaming a column with zero downtime. Why three deploys?
16. What does `lock_timeout` protect against during a migration? Why `CREATE INDEX CONCURRENTLY`?
17. What does graceful shutdown mean for a web process, and what happens at step 7
    of your deploy without it?
18. How did you get HTTPS on the VPS, and what does HSTS add?
19. Metrics, logs, traces — what question does each answer that the others cannot?
20. Why no `user_id` label on your Prometheus metrics?
21. URL versioning vs header versioning — what did you choose and why?

---

## 18. Common Mistakes to Watch For

- Floats for money — you will have done this once, on purpose, to feel it
- Allowing an unbalanced entry because the DB constraint is missing
- Caching anything financial "because it's slow" without checking whether
  staleness is acceptable — here it is not
- A circuit breaker that never half-opens
- A deploy pipeline whose rollback path has never been exercised
- Security scanners that warn instead of failing, and are therefore ignored
- Deleting or editing a posted entry instead of reversing it
- Claiming "the database enforces balance" with a `CHECK` that only ever saw one row
- A plain `CREATE INDEX` or a giant `UPDATE` on a live table during a deploy
- Renaming a column and shipping the code change in the same deploy
- Stopping the old container without letting it finish in-flight requests
- Serving the deployed system over plain HTTP because "it's just a portfolio"
- Deploying straight to prod with no staging
- Dashboards with no alerts — so the 3am incident is discovered at 9am
- Logs on eight containers with no aggregation and no shared request id

---

## 19. How Real Companies Differ

Real ledgers often use an **append-only event log as the source of truth**, with
balances as projections. That is an explicit, named preview of Phase 5's Event
Sourcing overview — and it is the same shape as `stock_movements` in StockPilot,
now applied to money.
