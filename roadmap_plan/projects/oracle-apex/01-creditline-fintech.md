# Oracle Project 1 — CreditLine

**Loan origination & servicing platform (FinTech)**

| | |
|---|---|
| Domain | FinTech — lending / credit |
| Level | Middle → Middle+ |
| Stack | Oracle DB 19c/23ai, PL/SQL, APEX 23.2+, ORDS · **Java 21 + Spring Boot 3** · Redis, RabbitMQ / Oracle AQ, MinIO, Prometheus/Grafana |
| Target | Advanced SQL + advanced PL/SQL, exercised by a system that genuinely needs them |

> **Why this project.** Lending is the domain where the database *is* the
> application. Interest accrual, amortization, penalty calculation, delinquency
> aging and month-end close are set-based, transactional, deadline-bound
> problems — exactly what Oracle and PL/SQL exist for. Nothing here is a
> contrived exercise to "use a feature": every advanced construct is used
> because the alternative is worse.

---

## 1. Business Problem

A lender (bank branch, microfinance organization, or a company's internal
employee-loan program) issues loans and must service them for their entire life:

- Take an application, score it, approve or decline it, and record **who
  decided what and when**
- Disburse the principal and generate a **repayment schedule**
- Accrue interest daily, apply payments in the correct order, charge penalties
  on overdue amounts
- Restructure or reschedule a loan when a borrower cannot pay
- Close the loan on final settlement or write it off
- Produce a **provisioning / delinquency report** that regulators and management
  can trust, where every number traces to a transaction

Today this lives in spreadsheets and a legacy screen. Numbers drift, no one can
reconstruct why a balance is what it is, and month-end takes three days.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. An APEX application that a loan officer, underwriter, cashier, and manager
   each log into and see only what their role permits
2. A loan's complete life cycle working end to end: application → scoring →
   approval → disbursement → schedule → repayments → delinquency → closure
3. A nightly batch that accrues interest and ages delinquency across the whole
   portfolio, restartable and idempotent
4. A month-end close that freezes a period and produces a provisioning report
5. A REST API exposing loan balance and payment posting to external callers —
   built on **ORDS and on Spring Boot**, so you can argue the tradeoff
6. A **Spring Boot integration layer** (§9) in front of the packages: partner
   APIs, a Spring Batch file importer, Redis caching and idempotency, and
   RabbitMQ/AQ event publishing — with every business rule still in PL/SQL

**Proof it is correct**
7. A reconciliation report where the sum of all transactions equals every
   outstanding balance, to the smallest currency unit
8. A utPLSQL test suite covering the amortization, allocation and penalty engines
9. A documented performance story: a slow query, its plan, what you changed, the
   new plan

**Skills demonstrable in an interview**
10. Every item in the coverage matrix in §10, each pointing at real code you wrote

---

## 3. Roles

| Role | Sees | Can do | Cannot |
|---|---|---|---|
| **Applicant / Borrower** *(self-service portal)* | Own applications, own loans, own schedule and balance | Submit an application, upload documents, view/print a schedule, see payment history | See anyone else's data, see internal scoring or comments |
| **Loan Officer** | Applications in their branch | Create and edit applications, run the scoring engine, attach documents, submit for underwriting | Approve a loan, change an approved amount, post payments |
| **Underwriter** | Applications submitted for decision | Approve, decline, or approve-with-conditions; override the score **with a mandatory written reason**; set limits | Disburse funds, edit the application's data |
| **Cashier / Teller** | Approved and active loans | Record a disbursement, post a repayment, print a receipt, reverse **today's own** mistaken entry | Approve loans, alter posted history, reverse another user's entry |
| **Collections Officer** | Delinquent loans in their portfolio | Log a contact attempt, promise-to-pay, propose a restructure | Approve a restructure, waive a penalty |
| **Branch Manager** | Everything in their branch | Approve restructures and penalty waivers within a limit, approve write-offs up to a threshold | Change system parameters, see other branches |
| **Finance / Back Office** | All branches, read-mostly | Run month-end close, generate provisioning and regulatory reports, export | Change loan data directly |
| **System Administrator** | Everything | Manage users, roles, product parameters, interest rate tables, holiday calendar | *(Actions are audited like everyone else's)* |

**Separation of duties is a real requirement, not decoration:** the person who
creates an application cannot approve it; the person who approves it cannot
disburse it. Enforce this in the database, not only in the UI.

---

## 4. Functional Modules

### 4.1 Product configuration
Loan products with: interest method (flat / declining balance / annuity), rate,
term bounds, amount bounds, grace period, penalty rate, fee schedule, allowed
repayment frequencies. **Parameters live in tables, never in code.**

### 4.2 Origination
Application capture, applicant KYC data, collateral and guarantor records,
document upload, a **scorecard** (rules-driven, table-configured) producing a
score and a recommendation, then an approval workflow with limits by role.

### 4.3 Disbursement
Full or tranched disbursement, generating the **repayment schedule** at
disbursement time and freezing it.

### 4.4 Servicing
- Daily interest accrual across the portfolio
- Payment posting with a strict **allocation waterfall**:
  `penalties → fees → overdue interest → current interest → principal`
- Early/partial repayment handling and schedule recalculation
- Penalty assessment on overdue instalments after the grace period
- Payment reversal (same-day, audited)

### 4.5 Collections & restructuring
Delinquency aging buckets (1–30 / 31–60 / 61–90 / 90+ days), contact log,
promise-to-pay tracking, restructure proposal → approval → new schedule with the
old one retained in history.

### 4.6 Closure
Settlement (including early settlement quote), write-off with approval, and
post-write-off recovery.

### 4.7 Accounting & reporting
Every money movement produces a **balanced double-entry transaction**. Reports:
portfolio at risk, aging, provisioning by bucket, officer performance, product
profitability, daily cash position.

---

## 5. Data Model

```
-- Reference / configuration
branches            (branch_id, code, name, region)
app_users           (user_id, username, full_name, branch_id, is_active)
user_roles          (user_id, role_code, granted_by, granted_at)
approval_limits     (role_code, limit_type, max_amount, currency)
loan_products       (product_id, code, name, interest_method, nominal_rate,
                     min_amount, max_amount, min_term_m, max_term_m,
                     grace_days, penalty_rate, valid_from, valid_to)
fee_definitions     (fee_id, product_id, fee_type, calc_method, value, is_upfront)
rate_history        (product_id, rate, effective_from, effective_to)
holiday_calendar    (calendar_date, is_working_day, description)
scorecard_rules     (rule_id, attribute, operator, threshold, points, active_from)

-- Parties
customers           (customer_id, tax_id UNIQUE, full_name, birth_date,
                     phone, address, kyc_status, blacklist_flag)
customer_documents  (doc_id, customer_id, doc_type, file_blob, mime_type,
                     uploaded_by, uploaded_at)

-- Origination
applications        (app_id, customer_id, product_id, branch_id,
                     requested_amount, requested_term_m, purpose,
                     status, score, recommendation,
                     created_by, created_at, decided_by, decided_at,
                     decision_reason)
application_events  (event_id, app_id, from_status, to_status, actor, note, event_ts)
collaterals         (collateral_id, app_id, type, description, valuation, currency)
guarantors          (guarantor_id, app_id, customer_id, guarantee_amount)

-- Loans
loans               (loan_id, app_id, customer_id, product_id, branch_id,
                     principal, rate, term_m, disbursed_at, first_due_date,
                     maturity_date, status, officer_id,
                     written_off_at, closed_at)
disbursements       (disb_id, loan_id, amount, disbursed_at, disbursed_by)
schedules           (schedule_id, loan_id, version, generated_at,
                     generated_by, reason, is_active)
schedule_lines      (line_id, schedule_id, instalment_no, due_date,
                     principal_due, interest_due, fee_due,
                     principal_paid, interest_paid, fee_paid, status)

-- Money movement
loan_transactions   (txn_id, loan_id, txn_type, amount, value_date, posted_at,
                     posted_by, reversal_of_txn_id NULL, batch_id NULL)
    -- txn_type: DISBURSE | REPAY | ACCRUAL | PENALTY | FEE | WAIVER
    --           | WRITEOFF | RECOVERY | REVERSAL
payment_allocations (alloc_id, txn_id, line_id, component, amount)
    -- component: PENALTY | FEE | INTEREST | PRINCIPAL

gl_accounts         (account_id, code UNIQUE, name, type)
gl_entries          (entry_id, txn_id, entry_date, description)
gl_lines            (line_id, entry_id, account_id, debit, credit)
    -- CHECK: exactly one of debit/credit is non-zero

-- Collections
delinquency_snapshots (snap_id, loan_id, snapshot_date, days_past_due,
                       bucket, overdue_principal, overdue_interest, provision_amt)
collection_actions    (action_id, loan_id, action_type, promise_date,
                       promise_amount, note, actor, action_ts)
restructures          (restr_id, loan_id, requested_by, approved_by,
                       old_schedule_id, new_schedule_id, reason, status, decided_at)

-- Operations
batch_runs          (batch_id, batch_name, business_date, started_at,
                     finished_at, status, records_processed, error_text)
batch_errors        (err_id, batch_id, loan_id, error_code, error_msg, raised_at)
audit_log           (audit_id, table_name, pk_value, action, old_row_json,
                     new_row_json, changed_by, changed_at)
period_status       (period_yyyymm, status, closed_by, closed_at)
```

**Partitioning:** `loan_transactions` and `delinquency_snapshots` are **range
partitioned by month** with a local index strategy — the portfolio grows without
bound and every report is date-scoped.

---

## 6. Invariants (enforced in the database)

1. `SUM(debit) = SUM(credit)` for every `gl_entry`.
2. A loan's outstanding balance always equals the replay of its transactions.
3. A payment allocation never exceeds the amount due on the line it targets.
4. Only one `schedules` row per loan has `is_active = 'Y'`
   *(enforce with a function-based unique index)*.
5. Nothing may be posted into a **closed period**.
6. The creator of an application cannot be its approver.
7. A reversal reverses exactly one transaction, and only once.
8. Interest accrual runs **at most once per loan per business date**.

---

## 7. PL/SQL Package Architecture

Business logic lives in packages. **APEX pages call packages; they never contain
business logic in page processes.**

| Package | Responsibility |
|---|---|
| `pkg_loan_product` | Product/rate/fee lookup, parameter resolution with date effectivity |
| `pkg_scoring` | Rule-driven scorecard evaluation, recommendation |
| `pkg_application` | Application state machine, submission, decision, separation-of-duties checks |
| `pkg_schedule` | Amortization engine — annuity, declining balance, flat; business-day adjustment |
| `pkg_disbursement` | Disbursement, tranches, schedule generation and freezing |
| `pkg_payment` | Payment posting, the **allocation waterfall**, reversal |
| `pkg_accrual` | Daily interest accrual, bulk-processed |
| `pkg_penalty` | Overdue detection, grace handling, penalty assessment and waiver |
| `pkg_delinquency` | Aging buckets, snapshot generation, provisioning rates |
| `pkg_restructure` | Restructure proposal, approval, new-schedule generation |
| `pkg_closure` | Settlement quote, closure, write-off, recovery |
| `pkg_gl` | Double-entry posting; refuses an unbalanced entry |
| `pkg_batch` | Batch orchestration, restartability, error capture |
| `pkg_security` | Current user, role checks, branch scoping, VPD predicates |
| `pkg_audit` | Autonomous-transaction audit writer |
| `pkg_report` | Pipelined report sources, ref cursors for APEX |
| `pkg_api` | ORDS-facing entry points, JSON in / JSON out |

**Conventions:** every package has a spec-level constant block for error codes;
every public procedure validates its inputs and raises via
`RAISE_APPLICATION_ERROR` with a code from that block; no package writes to
`DBMS_OUTPUT` in production paths.

---

## 8. APEX Application Design

### Applications
Two APEX apps sharing one schema and one authentication scheme:
- **`CreditLine Back Office`** — staff
- **`CreditLine Portal`** — borrower self-service

### Key pages

| Page | Type | Notes |
|---|---|---|
| Dashboard | Cards + JET charts | Portfolio, disbursements today, PAR by bucket, my queue. Role-dependent regions |
| Applications | Faceted search + IR | Facets on status, product, branch, amount band, date |
| Application detail | Master-detail form + wizard | Applicant, collateral, guarantors, documents, score panel |
| Underwriting queue | Interactive Grid | Inline decision; approve/decline with mandatory reason on override |
| Loan detail | Tabbed region set | Summary, schedule, transactions, delinquency, collections, documents |
| Repayment posting | Form + IG | Live allocation preview computed by `pkg_payment` before commit |
| Restructure | Wizard + approval | Side-by-side old vs new schedule |
| Collections worklist | IG + dynamic actions | Log contact, record promise-to-pay |
| Batch monitor | IR + refresh | `batch_runs` and `batch_errors`, with a re-run action |
| Reports | IR / IG + downloads | Aging, provisioning, officer performance, cash position |
| Parameters | Forms + IG | Products, rates, fees, scorecard rules, holiday calendar |

### APEX techniques to use deliberately
- **Interactive Grid** with a PL/SQL-based save process (not automatic DML) where
  business rules must run
- **Faceted search** on the applications and loans lists
- **Approvals / Unified Task List** (`APEX_APPROVAL`) for the underwriting and
  restructure decisions
- **Workflow** (APEX 23.x) for the origination flow, if available in your version
- **Authorization schemes** per role, applied to pages, regions, buttons **and
  columns**
- **Dynamic actions** for the live allocation preview and cascading LOVs
- **APEX Collections** for the multi-tranche disbursement basket before commit
- **`APEX_MAIL`** for decision notifications, sent from a background process
- **`APEX_WEB_SERVICE` / REST Data Source** for an external credit-bureau lookup
  (mock it)
- **Automations** for the promise-to-pay follow-up reminder
- **`APEX_ITEM` / `APEX_JSON`** where a report needs custom interactivity
- **Session state protection** enabled; **no** URL-parameter-driven authorization

---

## 9. Java / Spring Boot Integration Layer

APEX covers the internal back office. Spring Boot covers everything that faces
outward: partner systems, a mobile/web borrower app, bulk file intake, and any
integration that needs real request validation, versioned contracts, and CI.

**Spring Boot does not replace the PL/SQL layer — it sits on top of it.** The
packages in §7 remain the only place business rules live. Java validates input,
calls a package, translates the result, and maps errors to HTTP. If a rule can be
bypassed by calling the API instead of using APEX, the layering is wrong.

### 9.1 Services

| Service | Purpose | Calls |
|---|---|---|
| `loan-query-api` | Balance, schedule, transaction history for the borrower app and partner systems | Views + pipelined functions from `pkg_report` |
| `payment-api` | Accept repayments posted by a cashier terminal, bank channel, or payment gateway | `pkg_payment.post_payment` |
| `payment-file-import` | Bulk bank payment file intake — **Spring Batch** | `pkg_payment` per record, chunked |
| `scoring-gateway` | Call the external credit bureau, normalise the response | Hands the result to `pkg_scoring` |
| `notification-worker` | Send decision and reminder notifications | Reads the queue table (or Oracle AQ) written by the batch |

Everything else — underwriting, restructure approval, parameter maintenance,
batch monitoring — stays in APEX. Do not rebuild an internal screen in Java just
because you can.

### 9.2 Spring modules — which ones, and where

**Deployment shape — decide this before writing code.** The table above lists
*responsibilities*, not necessarily separate deployables. Start as a **modular
monolith**: one Spring Boot application with a package per responsibility and
strict module boundaries. Split out only where the runtime profile genuinely
differs — the batch importer and the queue workers, which scale and fail
differently from the request path. You already learned in the Python track what
an unjustified service split costs; do not pay it twice.

| Spring module / library | Used for | Where exactly |
|---|---|---|
| **Spring Boot** (starters, config, profiles, Actuator) | Application bootstrap, externalised config, health endpoints | Every service |
| **Spring Web MVC** | REST controllers, `@RestControllerAdvice` error mapping | Every API. **Not WebFlux** — JDBC is blocking, so reactive buys nothing and complicates transactions. Be able to say that |
| **Spring JDBC** (`JdbcTemplate`, `SimpleJdbcCall`) | **The primary data access path** — calling PL/SQL packages | Every write; every REF CURSOR read |
| **Spring Data JPA** | Only for tables **Java owns**: outbox, integration state, delivery receipts, API keys | Never for domain tables. Domain writes go through packages, and an ORM over package-owned tables invites a second implementation of the rules |
| **Spring Data Redis** + **Spring Cache** (`@Cacheable`) | Reference-data and tariff caching, idempotency fast path | See the infrastructure table above for exactly which keys |
| **Spring Transaction** (`@Transactional`) | The transaction boundary the packages deliberately do not own | Every service method that calls a writing package |
| **Spring Security** (OAuth2 Resource Server, method security) | Partner/agent/customer authentication and authorization | All external APIs. Internal staff stay on APEX's own auth |
| **Spring Validation** (Jakarta Bean Validation) | Request-shape validation: required fields, ranges, formats | Controllers only. **Business** rules stay in PL/SQL — validation here is about well-formed input, not about whether the action is allowed |
| **Spring AMQP** (`spring-boot-starter-amqp`) | RabbitMQ producers and consumers, retry policy, DLQ routing | Every queue in the infrastructure table |
| **Spring JMS** | Oracle AQ via AQ-JMS | The atomic first hop out of a transaction |
| **Spring Batch** | Chunked file import with restart and skip policy | The bulk file intake job |
| **Spring Retry** | Retry with backoff on transient third-party failures | Partner/bureau/registry calls |
| **Resilience4j** | Circuit breaker, bulkhead, timeout around external calls | Every outbound integration — a slow third party must not exhaust the request pool |
| **Micrometer** → Prometheus | Metrics: latency, queue depth, cache hit ratio, pool saturation | Wired through Actuator |
| **Flyway** | Schema **and package** deployment — versioned for tables, repeatable for packages/views | Runs on startup and in CI |
| **springdoc-openapi** | Published API contract for partner integrators | External APIs |
| **Spring Boot Test** + **Testcontainers** + **MockMvc / RestAssured** + **WireMock** | Integration tests against a real Oracle container; third parties stubbed | See the testing subsection below |
| **Spring Modulith** *(optional)* | Enforcing module boundaries inside the monolith, and documenting them | Worth trying precisely because it keeps the monolith honest |

**The rule that ties this together:** Spring owns the *transaction boundary*, the
*wire format*, and the *outside world*. Oracle owns the *rules*. Any Spring class
that decides whether something is allowed has crossed the line.

### 9.3 Calling a package from Spring

```java
@Repository
class PaymentGateway {

    private final SimpleJdbcCall postPayment;

    PaymentGateway(JdbcTemplate jdbc, RowMapper<Allocation> allocationMapper) {
        this.postPayment = new SimpleJdbcCall(jdbc)
            .withCatalogName("PKG_PAYMENT")
            .withProcedureName("POST_PAYMENT")
            .declareParameters(
                new SqlParameter("p_loan_id",     Types.NUMERIC),
                new SqlParameter("p_amount",      Types.NUMERIC),
                new SqlParameter("p_value_date",  Types.DATE),
                new SqlOutParameter("p_txn_id",   Types.NUMERIC),
                new SqlOutParameter("p_allocations", OracleTypes.CURSOR, allocationMapper));
    }

    PostedPayment post(long loanId, BigDecimal amount, LocalDate valueDate) { ... }
}
```

Three options exist; know when to use each:

| Approach | Use when |
|---|---|
| `SimpleJdbcCall` | Default. Calling a package procedure with scalar in/out params and a REF CURSOR |
| `JdbcTemplate` + `CallableStatementCreator` | You need full control: Oracle object types, arrays, non-trivial binds |
| JPA `@NamedStoredProcedureQuery` | Only if the rest of the module already lives in JPA. Mixing JPA entities with package-owned writes usually causes more trouble than it saves |

**Passing collections:** binding Oracle nested tables over JDBC is painful. The
practical route is to pass a JSON string and expand it inside PL/SQL with
`JSON_TABLE`. Build one call each way and record which you would choose.

### 9.4 Transaction ownership — the rule that keeps this honest

**No package procedure issues `COMMIT` or `ROLLBACK`.** The caller owns the
transaction boundary:

| Caller | Commits where |
|---|---|
| APEX | The page process |
| Spring Boot | `@Transactional` on the service method |
| `DBMS_SCHEDULER` batch | The batch orchestrator, per chunk |

The only exception is the deliberate one: `pkg_audit` and `batch_errors` write
through `PRAGMA AUTONOMOUS_TRANSACTION` so a rollback cannot erase the record of
what was attempted.

If a package commits inside a Spring `@Transactional` method, the commit silently
ends Spring's transaction and a later rollback will not undo the work already
written. Be able to explain exactly why.

### 9.5 Error contract

Domain errors travel as **codes**, never as messages:

```
pkg_payment: RAISE_APPLICATION_ERROR(-20007, 'PERIOD_CLOSED')
   ↓ SQLException, errorCode = 20007
   ↓ custom SQLExceptionTranslator  →  DomainException("PERIOD_CLOSED")
   ↓ @RestControllerAdvice          →  409 {"code":"PERIOD_CLOSED"}
```

The error-code constant block in each package spec (§7) is the contract. Java
binds to the numbers; message text and localisation stay on the Java side. A
package that returns a human-readable Uzbek or Russian string to the API layer
has leaked presentation into the domain.

Maintain one table mapping error code → HTTP status → client-facing message key,
and test it.

### 9.6 Type mapping — where the bugs actually are

| Oracle | Java | Note |
|---|---|---|
| `NUMBER` (money) | `BigDecimal` | **Never** `double` or `float`. Set scale explicitly |
| `NUMBER` (id) | `long` | |
| `DATE` | `LocalDateTime` | Oracle `DATE` carries a time component — mapping it to `LocalDate` silently truncates |
| `TIMESTAMP WITH TIME ZONE` | `OffsetDateTime` | |
| `CHAR(1)` `'Y'`/`'N'` | `boolean` | Oracle SQL has no `BOOLEAN` before 23ai; PL/SQL `BOOLEAN` cannot be bound over JDBC |
| `SYS_REFCURSOR` | `RowMapper<T>` | |
| Object type (`t_money`) | Java `record Money` | Map explicitly; do not let it degrade to a raw number |
| Nested table | JSON + `JSON_TABLE` | The pragmatic route |
| `CLOB` / `BLOB` | `String` / `byte[]` or streamed | Stream large document blobs; do not load them whole |

### 9.7 Supporting infrastructure — what to connect, and exactly where

The database does the domain work. These components exist only in the Java layer,
and each one is here because a specific requirement demands it. **Anything you
cannot tie to a line in this table, do not deploy.**

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **Redis — cache** | `pkg_loan_product` parameter lookups, GL account codes, branch list, holiday calendar, scorecard rules, fee definitions | Read on nearly every request, changed a few times a year. Cached in Java **and** result-cached in PL/SQL; measure both, keep the one that matters |
| **Redis — idempotency store** | `payment-api`: the `Idempotency-Key` header on every posted repayment; `scoring-gateway`: bureau request dedup | A gateway or teller terminal retrying a timeout must not create a second payment. Redis holds the key → response for the retention window; the **durable** copy is a table in Oracle, Redis is only the fast path |
| **Redis — rate limiting** | `loan-query-api` and `payment-api` per partner API key | Bucket4j or Spring Cloud Gateway with a Redis backend. A partner's retry storm must not reach the database |
| **Redis — distributed lock** | `payment-file-import`: one file processed by one pod | Two replicas must not import the same bank file. Note the alternative — `DBMS_LOCK` inside Oracle — and say which you chose and why |
| **Redis — JWT denylist** | Revoked partner tokens | Short list, high read rate |
| **RabbitMQ — notifications** | Decision emails/SMS, overdue reminders, disbursement confirmations | The batch and the API enqueue; `notification-worker` consumes with retry and a DLQ. Sending must never be inside the business transaction |
| **RabbitMQ — outbound integration events** | `LoanDisbursed`, `PaymentPosted`, `LoanWrittenOff` → core banking, accounting, BI | Downstream systems must not poll Oracle |
| **RabbitMQ — async bureau calls** | `scoring-gateway` fan-out when the bureau is slow | Keeps the quote request from blocking on a third party |
| **RabbitMQ — DLQ** | Every consumer above | A poison notification must not stall the queue. Inspect a DLQ message by hand at least once |
| **Oracle AQ** | The alternative to RabbitMQ for the *first* hop only | See §9.7.1 — this is the important design decision, not a detail |
| **MinIO / S3** | Customer KYC documents, collateral photos, generated PDF schedules and statements | Currently `customer_documents.file_blob`. Moving blobs out keeps the database small and backups fast — but they leave the transaction. Decide and write it down |
| **Prometheus + Grafana** | Batch step duration, outbox/queue lag, API p95, connection-pool saturation, DLQ depth, failed-payment rate | You already build the batch monitor in APEX; this is the same data for the Java side |
| **Sentry (or equivalent)** | All Java services | Stack traces the DB error log does not give you |
| **Keycloak / OAuth2 provider** | Partner and borrower-app authentication | APEX keeps its own session auth; the two are separate on purpose |
| **Quartz** | Nothing, initially | The nightly chain stays in `DBMS_SCHEDULER`. Only introduce Quartz if a job genuinely has no DB work — and then justify it |

**Deliberately NOT connected — and be ready to say why:**

| Component | Why not |
|---|---|
| **Redis on loan balances** | Financial data read for decisions. A stale balance means a wrong payoff quote. This is the same call the spec already makes about caching in `pkg_gl` — stay consistent |
| **Kafka** | Nothing here needs a replayable log or high-throughput streaming. RabbitMQ's work-queue semantics fit. Name Kafka as the answer if an analytics stream or event sourcing arrives later |
| **Elasticsearch** | The searches here are structured — loan number, tax ID, date range, status. Oracle indexes handle them. ES would be a derived index with no felt problem behind it |
| **A separate cache for `quote_factors`** | They are written once per quote and read once. Caching a write-once row is noise |

#### 9.7.1 The atomicity decision: Oracle AQ vs RabbitMQ

This is the design question worth getting right, because it is the same problem
FleetTrack solves in the Python track.

A `PaymentPosted` event must be published **if and only if** the payment
committed. Three options:

| Option | Guarantee | Cost |
|---|---|---|
| Publish to RabbitMQ inside the service method | **Broken.** The DB commit can succeed and the publish fail, or vice versa | — |
| **Oracle AQ**, enqueued inside the same transaction as the payment | Atomic by construction — the enqueue *is* a database write | Ties you to Oracle messaging; consumers need AQ-JMS |
| **Outbox table** + a Spring relay that polls and publishes to RabbitMQ | Atomic write, at-least-once delivery, consumers stay broker-agnostic | You maintain the relay; consumers must be idempotent |

**Recommended:** Oracle AQ for the first hop (the enqueue is free atomicity when
you are already in an Oracle transaction), then a bridge to RabbitMQ if
non-Oracle consumers appear. Build the outbox variant too — it is the pattern
every interviewer asks about, and you will already have built it once in
FleetTrack.

Whichever you choose, **every consumer must be idempotent**: at-least-once
delivery means duplicates are normal, not exceptional.

### 9.8 Spring Batch vs `DBMS_SCHEDULER` — build both, then choose

The nightly chain in §10 stays in PL/SQL: it is set-based work next to the data,
and moving it out would be a regression.

The **bank payment-file import** is the honest counter-example. Build it twice:

1. In PL/SQL with an external table / `UTL_FILE`
2. In Spring Batch with a chunked reader → processor → writer, restart support,
   and a skip policy

Then measure both on the same file and write `docs/batch-comparison.md`: throughput,
restartability, error visibility, and how hard each was to test. The conclusion
matters less than being able to defend it — this is exactly the question a Java +
Oracle shop will ask you.

### 9.9 Testing

- **Testcontainers** with `gvenzl/oracle-free`, one container per test class group
- **Flyway** runs the full schema on container start, including packages as
  repeatable migrations (`R__pkg_payment.sql`) so a package change redeploys
  automatically
- **utPLSQL** runs inside the same container — the PL/SQL suite from §11 is not
  replaced by Java tests, it is invoked alongside them
- Spring integration tests assert the **boundary**, not the domain logic: that the
  right package was called with the right binds, and that error code 20007 becomes
  a 409
- One test that proves the layering: call the API with input that violates a
  business rule and confirm the **database** rejected it, not a Java `if`

### 9.10 Operational concerns

| Item | Choice |
|---|---|
| Driver | `ojdbc11` |
| Pool | HikariCP by default; Oracle UCP only if you need RAC fast-connection-failover |
| Schema migrations | Flyway, versioned for tables, repeatable for packages/views |
| API docs | springdoc-openapi |
| Auth | OAuth2 / JWT resource server for partner APIs; distinct from APEX's session auth |
| Identity bridge | Set `DBMS_SESSION.SET_IDENTIFIER` (or a context) with the authenticated user before the call, so VPD and `pkg_audit` see the real actor rather than the pool user |

That last row is essential. With a connection pool, every session logs in as the
same database user. Unless Java pushes the authenticated identity into a session
context at the start of the transaction, your VPD policies and audit trail become
useless for API traffic.

### 9.11 ORDS or Spring Boot?

Both are in scope; the point is knowing the boundary.

| ORDS is enough | Spring Boot earns its place |
|---|---|
| Simple read endpoints over a view | Multi-step orchestration, external calls |
| Internal consumer | Partner-facing: OAuth2, rate limits, versioned contracts |
| Ship today | Contract tests, CI, staged rollout |
| No Java team | You need to fan out to other systems |

Implement `loan-query-api` **both ways** and write the comparison down.

### 9.12 Definition of Done — Java layer

- [ ] No package procedure commits; transaction boundaries owned by the caller
- [ ] Error-code contract implemented end to end, with a mapping test
- [ ] Money is `BigDecimal` throughout; no `double` anywhere near an amount
- [ ] Authenticated identity pushed into the DB session, so VPD and audit work
      for API traffic
- [ ] Testcontainers + Flyway + utPLSQL running in CI
- [ ] A test proving a business rule is enforced by the database, not by Java
- [ ] `docs/batch-comparison.md` — Spring Batch vs PL/SQL, with numbers
- [ ] `loan-query-api` built on both ORDS and Spring Boot, with the tradeoff written down

### 9.13 Interview Questions — the Java/Oracle boundary

1. Where does business logic belong in a Java + Oracle system, and how do you
   stop it drifting into both places?
2. What happens if a PL/SQL procedure commits inside a Spring `@Transactional`
   method?
3. How do you surface a `RAISE_APPLICATION_ERROR` as a meaningful HTTP status?
4. With a connection pool, how does the database know which end user is acting —
   and why does VPD break if you skip that?
5. How would you pass a collection of rows into a PL/SQL procedure from Java?
6. When would you move batch processing out of the database into Spring Batch,
   and when is that a mistake?
7. Why `BigDecimal` and not `double`, and what does Oracle `NUMBER` scale have to
   do with it?
8. Oracle `DATE` vs `TIMESTAMP` — which Java type for each, and what breaks if
   you get it wrong?
9. When is ORDS the right answer instead of a Spring Boot service?
10. How do you test code that is half Java and half PL/SQL?

---

## 10. Advanced SQL & PL/SQL Coverage Matrix

Every row is used somewhere real in this system. This table is also your
interview crib sheet — for each feature you should be able to name *the place in
CreditLine where you used it and why*.

### SQL

| Feature | Where it is used |
|---|---|
| Analytic functions (`ROW_NUMBER`, `RANK`, `LAG`/`LEAD`, `SUM() OVER`) | Running balance per loan, previous-payment gap, ranking officers by portfolio quality |
| Window frames (`ROWS BETWEEN`) | Rolling 90-day disbursement volume |
| `CONNECT BY` / recursive `WITH` | Guarantor and related-party chains; branch hierarchy roll-up |
| `MERGE` | Delinquency snapshot upsert; product parameter loads |
| Multi-table `INSERT ALL` | Splitting a posted payment into allocations and GL lines in one statement |
| `MODEL` clause | Amortization projection as a set-based alternative — build it once, compare to the PL/SQL engine |
| `PIVOT` / `UNPIVOT` | Aging report: buckets as columns |
| `GROUPING SETS` / `ROLLUP` / `CUBE` | Portfolio report by branch × product × bucket with subtotals |
| `MATCH_RECOGNIZE` | Detect a payment-behaviour pattern: three consecutive late payments |
| Hierarchical + aggregate combined | Provisioning roll-up across the branch tree |
| Set operators (`MINUS`, `INTERSECT`) | Reconciliation: schedule vs transactions |
| Scalar subqueries & `WITH` clause | Report readability; measured against the inline version |
| `FLASHBACK QUERY` (`AS OF TIMESTAMP`) | "What did this balance look like yesterday?" investigations |
| Function-based index | `UPPER(customer.full_name)` search; the one-active-schedule constraint |
| Bitmap / composite / covering indexes | Reporting queries on low-cardinality status columns |
| Range partitioning + partition pruning | `loan_transactions` by month; proven in the execution plan |
| Materialized view + fast refresh on commit | Dashboard portfolio aggregates |
| `EXPLAIN PLAN` / `DBMS_XPLAN` / SQL Trace | The documented tuning story |
| Optimizer hints (sparingly, justified) | One case where you show the hint helped **and** why you preferred a fix |
| JSON (`JSON_TABLE`, `JSON_OBJECT`, `IS JSON`) | Bureau response parsing; audit row snapshots |
| Global temporary table | Batch staging within a session |
| `VPD` / policy functions | Branch-level row filtering enforced in the DB |

### PL/SQL

| Feature | Where it is used |
|---|---|
| Packages (spec/body, overloading, constants, initialization block) | The entire architecture in §7 |
| Explicit cursors, cursor `FOR` loops, parameterized cursors | Schedule iteration, allocation waterfall |
| **`BULK COLLECT` + `LIMIT`** | Nightly accrual over the whole portfolio in chunks |
| **`FORALL` + `SAVE EXCEPTIONS`** | Bulk insert of accrual transactions; per-row failures captured into `batch_errors` without aborting the run |
| `%BULK_EXCEPTIONS` | Reporting exactly which loans failed and why |
| Collections: associative array, nested table, `VARRAY` | Rate lookup cache, allocation buffer, tranche list |
| Object types + member methods | `t_money` (amount + currency) with arithmetic that refuses cross-currency addition |
| Pipelined table functions | Report sources streamed to APEX without a temp table |
| Ref cursors (strong and weak) | APEX report regions and ORDS handlers |
| **Autonomous transactions** | Audit and error logging that survives a rollback |
| **Compound triggers** | Audit capture without mutating-table errors |
| `INSTEAD OF` triggers | An updatable view over the loan summary |
| `RAISE_APPLICATION_ERROR` + `PRAGMA EXCEPTION_INIT` | A defined error-code contract the APEX layer maps to messages |
| User-defined exceptions | Domain errors: `e_period_closed`, `e_limit_exceeded`, `e_own_approval` |
| Dynamic SQL: `EXECUTE IMMEDIATE`, `DBMS_SQL` | Generic report filter builder — written **with bind variables**, and you explain the injection risk of the naive version |
| Bind variables everywhere | Demonstrate the shared-pool difference against a literal-concatenated version |
| `DBMS_SCHEDULER` (jobs, chains, windows) | Nightly accrual → penalty → delinquency → provisioning chain |
| `DBMS_LOCK` / `DBMS_APPLICATION_INFO` | Preventing concurrent batch runs; instrumenting long jobs |
| `UTL_FILE` / external tables / `SQL*Loader` | Bulk payment file import from a bank |
| `DBMS_CRYPTO` or `STANDARD_HASH` | Hashing sensitive reference data |
| `DBMS_PROFILER` / `DBMS_HPROF` | Finding the hot spot in the accrual engine |
| `PLSQL_OPTIMIZE_LEVEL`, `NATIVE` compilation | Measured, not assumed |
| Result-cached functions | Product parameter lookup |
| Deterministic functions | Amortization helpers used in SQL |
| `PRAGMA UDF` / `WITH FUNCTION` | Calling a PL/SQL helper from SQL without the context-switch cost — measured |
| Conditional compilation (`$IF`) | Debug instrumentation compiled out of production |
| **utPLSQL** | The test suite in §12 |
| Invoker's vs definer's rights | Explain the choice for `pkg_security` |
| Edition-based redefinition *(read + write up, optional to implement)* | The online-upgrade story |

---

## 11. Batch Design (nightly, and this is where PL/SQL earns its keep)

```
DBMS_SCHEDULER chain, business-date driven:

  1. open_business_date      → guard: not a holiday, prior date closed
  2. accrue_interest         → BULK COLLECT + FORALL over active loans
  3. assess_penalties        → overdue lines past grace
  4. age_delinquency         → snapshot + bucket + provision
  5. refresh_dashboards      → materialized views
  6. send_notifications      → APEX_MAIL via a queue table
  7. close_business_date     → mark batch_run complete
```

**Requirements the batch must meet — these are the interesting part:**

- **Idempotent:** re-running for the same business date must not double-accrue.
  Enforce with a unique constraint, not just a check
- **Restartable:** a failure at step 3 resumes from step 3, not step 1
- **Non-blocking failure:** one bad loan is logged to `batch_errors` and the run
  continues (`SAVE EXCEPTIONS`), rather than rolling back 40,000 good rows
- **Single-instance:** `DBMS_LOCK` prevents two runs overlapping
- **Observable:** `DBMS_APPLICATION_INFO` so a DBA can see progress in `V$SESSION`
- **Bounded:** processes in chunks with a `LIMIT`, with the chunk size a parameter
  you actually tuned and recorded

---

## 12. Testing Strategy

| Layer | What |
|---|---|
| **utPLSQL unit** | Amortization: annuity vs declining vs flat, against hand-computed expected schedules |
| utPLSQL unit | Allocation waterfall: partial payment, overpayment, exact payment, payment on a fully-paid line |
| utPLSQL unit | Penalty: inside grace, on the grace boundary, after grace, on a non-working day |
| utPLSQL unit | Every domain exception raised where expected |
| Integration | Full life cycle: apply → approve → disburse → 6 payments → 2 missed → restructure → settle |
| **Reconciliation** | `SUM(transactions) = outstanding balance` for every loan, and `SUM(debit) = SUM(credit)` globally |
| Concurrency | Two cashiers post a payment against the same loan simultaneously — no lost update |
| Batch | Run twice for the same date: second run is a no-op |
| Batch | Inject a poison loan: it lands in `batch_errors`, the rest complete |
| Security | Branch A user cannot read a branch B loan **through SQL directly**, not just through the UI |
| Separation of duties | The creator cannot approve their own application |
| Performance | Aging report and accrual batch at 100k loans, with plans recorded before and after tuning |

---

## 13. Build Plan

### Stage 1 — Foundation
Schema, constraints, reference data, `pkg_security`, audit via compound triggers
and autonomous transactions, seed users and roles.
*Done when:* every table has its constraints and the audit log captures a change
you make by hand.

### Stage 2 — Origination
Application tables and state machine, scorecard engine, separation-of-duties
checks, APEX application-entry and underwriting pages, approvals.
*Done when:* an application can travel to a decision and cannot be approved by
its creator.

### Stage 3 — Amortization engine
`pkg_schedule` for all three interest methods, business-day adjustment against
the holiday calendar, plus the `MODEL`-clause set-based version for comparison.
Full utPLSQL coverage against hand-computed schedules.
*Done when:* every method matches a schedule you calculated by hand.

### Stage 4 — Disbursement & payments
Disbursement with tranches, schedule freezing, `pkg_payment` allocation
waterfall, reversal, GL double-entry posting.
*Done when:* the reconciliation report balances to zero.

### Stage 5 — Servicing batch
Accrual with `BULK COLLECT`/`FORALL`/`SAVE EXCEPTIONS`, penalties, delinquency
aging, provisioning, `DBMS_SCHEDULER` chain, batch monitor page.
*Done when:* the batch is idempotent, restartable, and survives a poison row.

### Stage 6 — Collections, restructure, closure
Worklist, contact log, promise-to-pay automation, restructure with schedule
versioning, settlement quote, write-off, recovery.
*Done when:* an old schedule is still readable after a restructure.

### Stage 7 — Reporting & analytics
Aging with `PIVOT`, provisioning with `GROUPING SETS`, payment-behaviour
detection with `MATCH_RECOGNIZE`, pipelined report sources, materialized views,
JET dashboards.

### Stage 8 — Integration & hardening
ORDS REST API, mock bureau call via `APEX_WEB_SERVICE`, bank payment-file import,
VPD policies, performance tuning pass with documented plans, month-end close.

---

## 14. Definition of Done

- [ ] All seven roles implemented, with **DB-enforced** branch scoping (VPD)
- [ ] Separation of duties enforced in the database
- [ ] All three interest methods correct against hand-computed schedules
- [ ] Allocation waterfall correct for every payment shape
- [ ] Reconciliation report balances to zero
- [ ] GL entries always balanced
- [ ] Nightly batch: idempotent, restartable, single-instance, error-tolerant
- [ ] Restructure preserves schedule history
- [ ] Closed periods reject postings
- [ ] Full audit trail via autonomous transactions
- [ ] utPLSQL suite green
- [ ] ORDS API with JSON in/out, documented
- [ ] Tuning story documented: query, old plan, change, new plan
- [ ] Every row of the §10 matrix pointing at real code

---

## 15. Interview Questions This Project Should Let You Answer

1. Walk me through your payment allocation waterfall and why the order matters.
2. How does your nightly accrual stay idempotent, and how do you *prove* it?
3. `BULK COLLECT` + `FORALL` — what problem does it solve, and what does
   `SAVE EXCEPTIONS` add?
4. Why is your audit logger an autonomous transaction?
5. Why a compound trigger instead of a row trigger here?
6. How do you prevent a mutating-table error, and what causes one?
7. How do you enforce "only one active schedule per loan" without a trigger?
8. Show me where you used dynamic SQL and how you made it injection-safe.
9. What does VPD give you that an APEX authorization scheme does not?
10. Walk me through a query you tuned: the plan before, what you changed, the
    plan after.
11. Why is `loan_transactions` partitioned, by what, and how did you verify
    pruning happens?
12. When would you use `MERGE` over separate insert/update logic?
13. What is the difference between a pipelined table function and a temp table
    here?
14. Definer's rights vs invoker's rights — where did it matter?

---

## 16. Common Mistakes to Watch For

- Business logic in APEX page processes instead of packages
- Row-by-row loops where a set-based statement or `FORALL` belongs
- Concatenating literals into dynamic SQL instead of binding
- Storing money in `NUMBER` without a defined scale, or mixing currencies silently
- An audit trigger that rolls back with the transaction it was meant to record
- Batch jobs that abort the whole run on one bad row
- Authorization enforced only in the UI, so ORDS or SQL*Plus bypasses it
- Adding indexes without looking at a plan
