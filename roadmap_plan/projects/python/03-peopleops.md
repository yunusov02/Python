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
10. A Celery worker configured **on purpose**: `acks_late`,
    `task_reject_on_worker_lost`, prefetch, time limits, and the Redis-broker
    `visibility_timeout` — each one with a test or a demonstration behind it
11. Two queues (`emails`, `accruals`) with separate workers, and a written reason
12. A **DST/timezone test**: accrual on the night the clocks change still runs once,
    and leave overlap is computed with `daterange`

**Written artefacts**
13. `docs/celery-ops-notes.md` — every worker setting above, what breaks without it
14. `docs/postmortem-peopleops.md`, tag `v0.2-peopleops-final`

---

## 3. Scope

**In scope**
- Employees with a manager relationship
- Leave requests: annual, sick, unpaid
- Leave balances accrued monthly per year
- Approval / rejection with scoped permissions
- Async notification emails with retry
- Scheduled accrual and stale-request reminders
- Celery operational configuration and queue routing
- Timezone-correct dates (`USE_TZ=True`, Beat `timezone`, DST test)

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

Overlap detection uses Postgres **range types**: `daterange(start_date, end_date,
'[]') && daterange(:s, :e, '[]')`, not four hand-written comparisons. This is the
warm-up for CarePoint's `EXCLUDE` constraint, where the database enforces the
same rule for appointment slots.

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

**The alternative you should be able to name:** `pg_advisory_xact_lock(hash)` at
the start of the accrual serializes concurrent runs without a table. Write two
sentences on why the unique constraint is still better here (it leaves an audit
row, and it works across restarts and across processes that forget to take the
lock).

**Dates and time zones.** `start_date`/`end_date` are `date` — that is right for
leave. But "the 1st of the month at 00:00" for accrual is a *timezone question*:
`USE_TZ = True`, `CELERY_TIMEZONE` set explicitly, and Beat's crontab
interpreted in that zone. Test the DST transition night with `freezegun`: the
job must fire once, not zero or two times.

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

**Explicit enqueue, not Django signals.** It is tempting to send the email from
a `post_save` signal. Do not: signals hide the call site, fire on every save
(including fixtures and admin edits), and are miserable to test. The service
function enqueues, inside `transaction.on_commit`. Write the reason down.

---

## 10. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL** | Everything | |
| **Redis — Celery broker** | The queue between web and worker | Already in Compose from QuickServe; reused rather than re-derived |
| **Redis — Celery result backend** | Only where you actually inspect a result | Do not enable it reflexively; most of these tasks are fire-and-forget |
| **Celery worker** | Sending decision emails with `retry(3)` and backoff | The whole point of the project |
| **Celery worker configuration** | `task_acks_late=True` + `task_reject_on_worker_lost=True` (a task is re-delivered if the worker dies mid-task); `worker_prefetch_multiplier=1` for long tasks; `task_time_limit` / `task_soft_time_limit`; `broker_transport_options={"visibility_timeout": ...}` set **longer than your longest task** | Defaults are tuned for short tasks. With the Redis broker, a task running longer than `visibility_timeout` (default 1h) is **re-delivered while still running** — a second cause of "Beat fired twice" that has nothing to do with Beat |
| **Two queues** (`emails`, `accruals`) + `task_routes` | Separate workers per queue | A burst of 500 emails must not delay the accrual, and vice versa: head-of-line blocking is the felt problem. One queue is fine until it is not |
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
3. **Worker death and redelivery.** With `acks_late=False` (the default) a task is
   acked when *received*; kill the worker mid-send and the email is simply gone.
   With `acks_late=True` it is redelivered — which means the task must be
   idempotent (the accrual already is; the email needs a "sent" marker or an
   acceptable duplicate). Demonstrate both settings with `kill -9`.
4. **Visibility timeout.** Set it above your longest task, and know that a stuck
   task will be redelivered after it expires. This is the Redis-broker-specific
   gotcha an interviewer will probe if you say "Redis as a broker".

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
- Worker config: `acks_late`, `reject_on_worker_lost`, prefetch, time limits,
  `visibility_timeout` — each demonstrated once (`kill -9` the worker mid-task)
- `emails` and `accruals` queues, `task_routes`, two worker processes in Compose
- Compose gains `celery-worker` ×2; CI green

### Stage 4 — Scheduling *(D49–D53, Phase 3 Week 9)*
- **Celery Beat**: monthly accrual runs automatically
- 3-day unapproved-request reminder job
- Idempotency guard on accrual, tested; advisory-lock alternative written down
- `daterange && daterange` overlap; DST-night test with `freezegun`
- `docs/celery-ops-notes.md`
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
| **Worker death** | `kill -9` mid-task with `acks_late=True` → task redelivered; with the default → task lost. Both observed |
| Visibility timeout | A task sleeping longer than `visibility_timeout` is redelivered while running — observed, then fixed by raising the timeout |
| Routing | An email task never lands on the `accruals` worker |
| Time limits | A task exceeding `soft_time_limit` gets `SoftTimeLimitExceeded` and cleans up |
| **DST** | Accrual scheduled at 00:00 on the DST-change night runs exactly once |
| Overlap | `daterange` overlap: adjacent, contained, partially overlapping, identical |

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
- [ ] `acks_late`/`reject_on_worker_lost`/prefetch/time limits/`visibility_timeout` configured and demonstrated
- [ ] Two queues, two workers, routing tested
- [ ] `daterange` overlap; DST test green
- [ ] `docs/celery-ops-notes.md` written
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
9. What does `acks_late` change, and why does it force your tasks to be idempotent?
10. Explain `visibility_timeout` with the Redis broker. What happens to a
    2-hour task with the default?
11. Why two queues? What is head-of-line blocking in a task queue?
12. Why not send the email from a `post_save` signal?
13. How do you make a nightly job safe across a DST change?
14. `pg_advisory_xact_lock` or a unique constraint for "run at most once" — trade-offs?

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
- Running the default `acks_late=False` and calling the system "reliable"
- A `visibility_timeout` shorter than the longest task, producing duplicate runs nobody can explain
- One queue for everything, so a notification storm delays the month-end accrual
- Sending email from a signal, then wondering why the test fixtures send email
- Naive dates around DST, so a "midnight" job runs at 23:00 or 01:00 — or twice

---

## 17. Data Engineering Extension — Stage 4 *(Week 9, +2 days)*

> **Why here.** `leave_requests`/`leave_balances` are exactly the kind of HR data
> Track B's **Project 23** (Year-2 Analytics Platform, Phase 11) later unifies
> across StockPilot/QuickServe/PeopleOps/LedgerBase. This section is the first,
> single-system version: get one clean export right before combining four.

**Scope (in)**
- A Celery Beat job (reusing the queue infrastructure this project already
  builds) exporting `leave_requests` + `leave_balances` to Parquet monthly, after
  accrual runs
- Partition the export by `year_month`, matching `accrual_runs`' own key — the
  same idempotency discipline as the accrual job itself

**Definition of Done**
- [ ] Monthly export job scheduled on Beat, idempotent per `year_month`
- [ ] Parquet files partitioned by month, readable by `pandas.read_parquet`

**Interview question this adds**
1. Why partition the export the same way the accrual job is keyed?

---

## 18. Telegram Bot Extension — Stage 3 *(Week 9, +2 days)*

> **Why here, and why this is the deep build.** This is the first bot in the
> curriculum with real, stateful business logic and the first with **push**
> (Celery now exists). Approving a leave request from a chat message is a genuine
> multi-step flow — the natural place to learn a proper **FSM** (finite-state
> conversation) and **inline keyboards**, on top of QuickServe's webhook/auth
> foundation.

**Scope (in)**
- Same linked-account pattern as QuickServe's bot (reused, not reinvented)
- `/request_leave` — an FSM conversation: type → start date → end date → confirm,
  each step validated against the same service layer the REST API calls (no
  parallel business-logic path)
- **Push**: on submission, the manager's linked chat receives an inline-keyboard
  message — `✅ Approve` / `❌ Reject` — sent via a new Celery task alongside
  `send_decision_email` (same queue discipline: justify whether it shares the
  `emails` queue or gets its own `bot_notifications` queue)
- Button tap calls the **same** `approve`/`reject` service function the REST
  endpoint calls — the bot is another caller of the service layer, not a second
  implementation of the business rule

**Scope (out)**

| Deferred | Why |
|---|---|
| Editing an in-flight FSM conversation ("go back a step") | Real UX feature, no new lesson |
| Bot-only actions with no REST equivalent | The rule that "the bot calls the same service layer" would break |

**New artifacts**
```
bot/
  states.py        # aiogram FSM states for the leave-request flow
  handlers.py       # /request_leave conversation, approve/reject callback handlers
```

**Testing**
- The FSM conversation is tested with a fake update sequence, asserting each state
  transition and the final service call
- Tapping "Approve" twice (a stale/duplicate callback) does not double-approve —
  same idempotency discipline as the rest of this project
- A manager's inline keyboard cannot approve a report that is not their own —
  same relationship-based permission check as the REST endpoint

**Definition of Done**
- [ ] `/request_leave` FSM flow working end to end via the bot
- [ ] Inline-keyboard approve/reject calls the existing service layer, proven by
      a shared test helper used by both the REST and bot test suites
- [ ] Duplicate callback tap does not double-approve
- [ ] `docs/telegram-bot-notes.md` updated with the FSM design

**Interview questions this adds**
1. How do you keep a Telegram bot's business logic from diverging from the REST API's?
2. What stops a duplicate button tap from double-approving a request?
3. Why an FSM here, when QuickServe's bot needed none?
