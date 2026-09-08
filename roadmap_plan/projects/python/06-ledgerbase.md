# Project 6 — LedgerBase

**Double-entry accounting & invoicing platform**

| | |
|---|---|
| Domain | FinTech |
| Level | Middle |
| Phase | 4 — Microservices & Infrastructure |
| Weeks | 16–18 (D91–D108) |
| Stack | FastAPI (ledger-service), Django/DRF (invoicing-service), PostgreSQL, Redis, Celery Beat, Nginx, **Prometheus + Grafana + Sentry**, GitHub Actions (full CD), `pip-audit` / `gitleaks` / Trivy, Docker Compose |
| Repo | `ledgerbase/` |

> **Three things make this project.** Money as integer cents — learned by writing
> the float version first, on purpose. The **first real synchronous
> service-to-service write**, which is therefore the first to need resilience
> patterns. And the deployment and observability work that four services finally
> justify.

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
3. A trial-balance report that actually reconciles
4. `invoicing-service` calling `ledger-service` behind retry + a hand-rolled
   circuit breaker
5. Overdue-invoice reminders on Celery Beat
6. Four services behind one Nginx gateway, sharing CarePoint's `auth-service`

**Operational capability — the real payoff of this project**
7. A full CI/CD pipeline: build → push → SSH → **zero-downtime deploy**
8. Security gates that fail the build: `pip-audit`, `gitleaks`, Trivy
9. Prometheus scraping four services, Grafana dashboards for latency and queue depth
10. Sentry across all four services

**Proof it is correct**
11. A regression test for the float-drift bug you deliberately created
12. An unbalanced entry rejected by the database even when app validation is bypassed
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

**Out of scope**

| Deferred | Why |
|---|---|
| Multi-currency ledger | Doubles the modelling with no new infrastructure lesson |
| Accountant-facing CSV/PDF export | Presentation |
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
    -- CHECK: exactly one of debit_cents / credit_cents is non-zero
    -- CHECK: both >= 0

invoices(id, client_name, total_cents, status, issued_at, due_at)

payments(id, invoice_id, amount_cents, journal_entry_id, received_at)
```

---

## 8. The Two Invariants (defense in depth)

1. **Every journal entry balances:** `SUM(debit_cents) = SUM(credit_cents)`.
   Validated in the service layer **and** refused by the database.
2. **Every line is one-sided:** a `CHECK` constraint ensures exactly one of
   `debit_cents` / `credit_cents` is non-zero.

Application validation catches it early with a good error message. The DB
constraint catches it when someone bypasses the service layer — a management
command, a data migration, a psql session, a future service.

**You will prove this** by injecting an unbalanced entry directly past app
validation and watching the database refuse it.

---

## 9. API Design

| Method | Path | Service | Role | Notes |
|---|---|---|---|---|
| POST | `/journal-entries` | ledger | accountant / service | Must balance, or `422` |
| GET | `/accounts/{id}/balance` | ledger | bookkeeper+ | **Not cached** — deliberately |
| POST | `/invoices` | invoicing | bookkeeper+ | |
| POST | `/invoices/{id}/payments` | invoicing | bookkeeper+ | Calls ledger-service to post the entry |
| GET | `/reports/trial-balance` | ledger | accountant+ | |
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

---

## 11. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **Nginx** | One entrypoint routing to all four services | Extended from CarePoint, not re-derived |
| **PostgreSQL** | Ledger and invoicing data | |
| **Redis — Celery broker** | Overdue-invoice reminders | Reused |
| **Celery Beat + worker** | The reminder job | Third time building this pattern — it should be fast now |
| **Circuit breaker (in-process)** | `invoicing-service`'s HTTP client for `ledger-service` | In-process state is correct here; a shared breaker across replicas is a distinct, harder problem — name it |
| **Prometheus** | Scrapes `/metrics` on all four services, plus Postgres and RabbitMQ exporters | Four services is the first point where comparing them is meaningful |
| **Grafana** | Two dashboards: request latency per service, queue depth | Build the dashboard you would actually open at 3am |
| **Sentry** | All four services | Stack traces with context that logs do not give you fast enough |
| **GHCR** | Images for all four services | |
| **GitHub Actions** | Build → security gates → push → SSH → zero-downtime deploy | The full pipeline lands here |
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

---

## 13. Build Plan (consolidated)

### Stage 1 — The float mistake, on purpose *(D91–D93, Week 16)*
- New repo `ledgerbase/`; `Account`, `JournalEntry`, `JournalLine` models —
  **float version, deliberately**
- Generate a trial balance that **does not reconcile** because of float drift
- Fix: convert every money field to **integer cents**
- Add a regression test that would have caught the original bug
- `CHECK` constraints on `journal_lines` + app-level balance validation

> Do not skip the broken version. Watching a report fail to reconcile by 0.03 is
> the lesson. Being told "use integers" is not the same thing, and an interviewer
> can tell the difference in ten seconds.

### Stage 2 — Invoicing & resilience *(D94–D96, Week 16)*
- `Invoice`, `Payment` models
- `invoicing-service` calls `ledger-service`, wrapped in **retry + circuit breaker**
- `GET /reports/trial-balance`
- Add `ledgerbase` to Nginx routing
- Kill `ledger-service` mid-call; confirm a clean failure, not a hang

### Stage 3 — Full CI/CD & zero-downtime deploy *(D97–D101, Week 17)*
- CI builds and pushes images for all four services
- Add `pip-audit`, `gitleaks`, Trivy as **failing** gates
- Deploy step: SSH, pull, health-gated rollover, Nginx upstream swap
- **Break the new version's health check** and confirm the abort path
- End to end: push to `main` → build → push → deploy, verified live

### Stage 4 — Monitoring stack *(D103–D108, Week 18)*
- `/metrics` on all four services; Prometheus scrape config
- Grafana dashboard: latency + queue depth
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

---

## 19. How Real Companies Differ

Real ledgers often use an **append-only event log as the source of truth**, with
balances as projections. That is an explicit, named preview of Phase 5's Event
Sourcing overview — and it is the same shape as `stock_movements` in StockPilot,
now applied to money.
