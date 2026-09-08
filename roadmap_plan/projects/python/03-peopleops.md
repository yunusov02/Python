# Project 3 — PeopleOps

**HR & leave management system**

| | |
|---|---|
| Domain | HR / Enterprise |
| Level | Middle |
| Phase | 2 (starts) → 3 (finishes) |
| Weeks | 7–9 (D40–D53) |
| Stack | Python, Django + DRF, PostgreSQL, **Celery + Celery Beat**, Redis (broker), `freezegun`, Docker Compose |
| Repo | `peopleops/` |

> **This is the project that exists to teach background jobs.** It is split
> across two phases on purpose: in Phase 2 you build it *without* Celery and feel
> a synchronous email destroy an endpoint; in Phase 3 you fix it properly and add
> scheduled work. Skipping the painful half wastes the project.

---

## 1. Business Problem

An office of ~50 staff needs leave requests routed to a manager for approval,
accurate leave-balance tracking (accrued monthly), and email notification on
approval or rejection. Today this happens over Slack DMs: no audit trail, no
balance anyone trusts, and no way to answer "how many days do I have left?"

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Employees, managers and HR admins each with the right view of leave
2. A leave request flowing from submission to decision, with the balance updated
   in the same transaction as the approval
3. Manager approval scoped to their **own reports** — a relationship-based
   permission, not a role flag
4. Decision emails sent **asynchronously**, with retries, never blocking the request
5. Monthly balance accrual running automatically on a schedule
6. A reminder job for requests left unapproved for 3+ days

**Proof it is correct**
7. `docs/blocking-email-problem.md` — the measured pain, with numbers, written
   *before* Celery was introduced
8. Beat schedules tested with `freezegun` rather than by waiting
9. An idempotency test proving a double-fired accrual does not double-accrue

**Written artefacts**
10. `docs/postmortem-peopleops.md`, tag `v0.2-peopleops-final`

---

## 3. Scope

**In scope**
- Employees with a manager relationship
- Leave requests: annual, sick, unpaid
- Leave balances accrued monthly per year
- Approval / rejection with scoped permissions
- Async notification emails with retry
- Scheduled accrual and stale-request reminders

**Out of scope**
- Payroll, attendance tracking, shift planning
- An org chart deeper than manager → report
- Calendar integrations (Google/Outlook)
- Public holidays affecting day counts *(name it; it is a realistic next feature)*

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`employee`** | Create leave requests, view own balance and own request history, cancel an own request while it is still pending | See anyone else's requests or balances; approve anything |
| **`manager`** | Everything an employee can, plus approve/reject requests **from their own direct reports only**, and view those reports' balances | Approve their own request; act on someone else's reports |
| **`hr_admin`** | View all requests and balances, correct a balance with a reason, trigger accrual manually | Approve requests on a manager's behalf *(unless you model a delegation feature — do not)* |

**The permission lesson:** manager approval is not a global role check. It depends
on the **relationship between two records** — `leave_request.employee.manager_id
== current_user.employee_id`. Getting this right, and testing it, is one of the
two things this project teaches.

---

## 5. Functional Modules

### 5.1 Employee directory
Employees linked to auth users, with a self-referencing `manager_id`. Department
and hire date. The hire date matters: accrual starts from it.

### 5.2 Leave requests
Submission validates against the remaining balance and against overlapping
approved requests. Status: `pending → approved | rejected`, plus `cancelled` by
the employee while still pending.

### 5.3 Leave balances
One row per employee per year: `accrued_days`, `used_days`. Accrual adds a
monthly increment. Approval increments `used_days` **in the same transaction as
the status change** — otherwise a crash between the two leaves a wrong balance.

### 5.4 Notifications
Decision emails. Built synchronously first (deliberately), then moved to Celery
with retries.

### 5.5 Scheduled work
Monthly accrual and a daily stale-request reminder, both on Celery Beat.

---

## 6. Domain Model

```
employees(id, user_id -> users.id, full_name,
          manager_id NULL -> employees.id,
          hired_at, department)

leave_requests(id, employee_id -> employees.id,
               type[annual|sick|unpaid],
               start_date, end_date, days,
               status[pending|approved|rejected|cancelled],
               decided_by NULL -> employees.id, decided_at NULL,
               created_at)

leave_balances(id, employee_id -> employees.id, year,
               accrued_days, used_days,
               UNIQUE(employee_id, year))

accrual_runs(id, year_month, run_at, employees_processed)
    UNIQUE(year_month)     -- the idempotency guard
```

`accrual_runs` is small but load-bearing: the unique constraint on `year_month` is
what makes a double-fired Beat job a no-op instead of a double-accrual. Enforce
idempotency with a constraint, not with an `if` that races.

---

## 7. API Design

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/employees/me` | employee+ | |
| GET | `/leave-balances/me` | employee+ | |
| POST | `/leave-requests` | employee+ | Validates balance and overlap |
| GET | `/leave-requests` | employee+ | Own requests; managers additionally see their reports' |
| POST | `/leave-requests/{id}/cancel` | employee+ | Own, pending only |
| POST | `/leave-requests/{id}/approve` | manager | **Own reports only.** Async email |
| POST | `/leave-requests/{id}/reject` | manager | **Own reports only.** Async email |
| POST | `/leave-balances/accrue` | hr_admin | Manual trigger (Phase 2); scheduled from Phase 3 |

---

## 8. Business Rules (invariants)

1. A request cannot exceed the employee's remaining balance for the year.
2. A manager can only decide on requests from their own direct reports.
3. Nobody can approve their own request.
4. Approving increments `used_days` **in the same transaction** as the status change.
5. Overlapping approved requests for the same employee are rejected.
6. Sending the notification email must **never** fail or slow the approval.
7. Accrual for a given month runs at most once, regardless of how often it fires.

---

## 9. Architecture

Django + DRF, service layer, same discipline as QuickServe. The new structural
element is the worker:

```
              ┌── web (Django/DRF) ──┐
Client ──────►│  approve() → enqueue │──► Redis (broker) ──► celery-worker
              └── returns fast ──────┘                             │
                                                                   ▼
                                          celery-beat ──► scheduled tasks
```

The web process **never** waits for an email. It enqueues and returns.

---

## 10. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL** | Everything | |
| **Redis — Celery broker** | The queue between web and worker | Already in Compose from QuickServe; reused rather than re-derived |
| **Redis — Celery result backend** | Only where you actually inspect a result | Do not enable it reflexively; most of these tasks are fire-and-forget |
| **Celery worker** | Sending decision emails with `retry(3)` and backoff | The whole point of the project |
| **Celery Beat** | Monthly accrual, daily stale-request reminder | Scheduled, not triggered — a different failure model, and that difference is the Phase 3 lesson |
| **SMTP (mocked / MailHog)** | Local email delivery you can actually look at | Asserting "the task was enqueued" is not the same as seeing the mail |
| **Docker Compose** | `api` + `postgres` + `redis` + **`celery-worker`** + **`celery-beat`** | |
| **`freezegun`** | Testing Beat schedules by fast-forwarding time | You cannot wait a month for a test |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **RabbitMQ** | Redis as a Celery broker is enough for fire-and-forget notifications. RabbitMQ arrives in WareFlow, where routing, DLQs and delivery guarantees genuinely matter — and you will then be able to compare the two |
| **A cache** | Balances change on every approval and are read rarely. Caching would risk showing someone a wrong entitlement |
| **Flower / a task dashboard** | Optional. Useful, but the observability lesson lands properly in Phase 4 |

---

## 11. Background Jobs Design

| Job | Trigger | Retry | Notes |
|---|---|---|---|
| `send_decision_email` | Triggered on approve/reject | 3, with exponential backoff | Must never fail the HTTP request |
| `accrue_monthly_balances` | Beat, monthly | — | **Idempotent** — guarded by `accrual_runs.year_month` |
| `remind_stale_requests` | Beat, daily | — | Requests pending 3+ days |

**Two things that must be right:**

1. **Enqueue after commit, not inside the transaction.** If you enqueue inside
   the transaction and the transaction rolls back, you have emailed someone about
   an approval that never happened. If the worker picks the task up before the
   commit lands, it reads stale data. Use `transaction.on_commit(...)`.
2. **Beat jobs fire twice.** Worker restarts, clock skew, and a redeployed
   scheduler all cause it. Design for it with a constraint.

---

## 12. Build Plan (consolidated)

### Stage 1 — Scaffold & domain *(D40–D41, Phase 2 Week 7)*
- New repo `peopleops/`: Django scaffold
- `Employee`, `LeaveRequest`, `LeaveBalance` models
- `LeaveRequestViewSet` + approve / reject actions
- Manager-only permission logic, scoped to own reports

### Stage 2 — Feel the pain *(D42–D43, Phase 2 Week 8)*
- Trace the approval endpoint's **synchronous** email call — find exactly where
  it blocks
- Write `docs/blocking-email-problem.md` with **real numbers**: how long the
  request takes when the mail server is slow, and what happens to the whole
  approval when it hiccups

> Do not skip this stage. Celery is only worth learning once you have measured
> the problem it solves. "Because it is best practice" is not an interview answer.

### Stage 3 — Celery *(D44–D47, Phase 2 Week 8)*
- `celery.py` app config + Redis broker
- Convert the approval email into a Celery task with `retry(3)`
- Enqueue with `transaction.on_commit`
- `LeaveBalance` accrual calculation — manual trigger for now
- Compose gains `celery-worker`; CI green

### Stage 4 — Scheduling *(D49–D53, Phase 3 Week 9)*
- **Celery Beat**: monthly accrual runs automatically
- 3-day unapproved-request reminder job
- Idempotency guard on accrual, tested
- Finalize: `docs/postmortem-peopleops.md`, tag `v0.2-peopleops-final`

---

## 13. Testing Strategy

| Layer | What |
|---|---|
| Unit | Balance validation, overlap detection, accrual math |
| Unit | Permission: a manager cannot approve a non-report's request |
| Unit | Nobody approves their own request |
| Integration | Approve returns fast; the email task is **enqueued, not sent inline** |
| Integration | Approval and `used_days` update commit together — kill mid-way, verify neither happened |
| Task | Retry behaviour against a failing mail backend |
| **Schedule** | **Beat tested with `freezegun`** — fast-forward a month, assert accrual ran |
| **Idempotency** | Run accrual twice for the same month → second run is a no-op |
| Ordering | Enqueue happens after commit, not before |

---

## 14. Definition of Done

- [ ] Request → approval → balance update working end to end
- [ ] Manager scoping enforced and tested, including the self-approval case
- [ ] Approval endpoint responds fast; email is async with retries
- [ ] `docs/blocking-email-problem.md` with real before/after numbers
- [ ] Enqueue happens on commit, proven by a rollback test
- [ ] Monthly accrual on Beat, proven with `freezegun`
- [ ] Accrual idempotent, guarded by a database constraint
- [ ] Stale-request reminder working
- [ ] `docs/postmortem-peopleops.md`, tag `v0.2-peopleops-final`

---

## 15. Interview Questions This Project Should Let You Answer

1. When does work belong in a background job instead of the request cycle?
2. What happens to a Celery task if the worker dies mid-execution?
3. How do you make a scheduled job idempotent, and why must you?
4. How do you test time-dependent scheduled behaviour without waiting?
5. Why Redis as a Celery broker here, and when would you want RabbitMQ instead?
6. How do you enforce a permission that depends on the relationship between two
   records rather than on a role flag?
7. Why enqueue on commit rather than inside the transaction — what breaks otherwise?
8. What is the difference in failure model between a triggered job and a
   scheduled one?

---

## 16. Common Mistakes to Watch For

- Sending the email inside the transaction, so a mail failure rolls back an
  approval that logically already happened
- Enqueueing before commit, so the worker reads data that does not exist yet
- A Beat job that double-accrues on restart
- Testing "the email was sent" by actually sending mail instead of asserting the
  task was enqueued
- Treating manager permission as a global role check
- Updating the balance in a second transaction after the status change
