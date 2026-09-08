# Oracle Project 2 — PolisHub

**Policy administration & claims management system (Insurance)**

| | |
|---|---|
| Domain | Insurance — general/non-life (motor, property, health add-on) |
| Level | Middle+ |
| Stack | Oracle DB 19c/23ai, PL/SQL, APEX 23.2+, ORDS · **Java 21 + Spring Boot 3** · Redis, RabbitMQ / Oracle AQ, Elasticsearch, MinIO, Prometheus/Grafana |
| Target | Advanced SQL + advanced PL/SQL in a workflow-heavy, temporally-complex domain |

> **Why this project, and why it is harder than CreditLine.** Lending is
> temporally simple: one schedule, one direction. Insurance is temporally
> *messy* — a policy has a coverage period, an endorsement changes it
> mid-term and must be priced pro-rata from the change date, a claim is
> reported weeks after the incident, reserves move over the life of the claim,
> and every figure must be reconstructable **as of any date**. That is why this
> is the second project, and why it exercises Oracle features the first one
> doesn't need: temporal validity, versioning, `MERGE`-heavy processing, and
> real workflow.

---

## 1. Business Problem

An insurance company sells policies through agents and direct channels, and must:

- Quote and issue policies with **rating** that depends on the risk object
  (vehicle, property, insured person) and the chosen coverages
- Collect premium — in full or in instalments — and know at any moment whether a
  policy is **paid up, in grace, or lapsed**
- Handle **endorsements** mid-term: add a driver, change a vehicle, increase a
  sum insured, cancel — each priced pro-rata and each producing a new policy
  version, with the old one still readable
- Register **claims**, assign an adjuster, gather documents, reserve an estimated
  amount, approve or reject, and pay — with the reserve moving as the estimate
  changes
- Detect obvious fraud signals and route suspicious claims to investigation
- Renew policies, and pay **agent commissions** on written premium
- Produce technical reports management and the regulator need: written premium,
  earned premium, outstanding reserves, loss ratio, claims triangles

Today: policies in one legacy screen, claims in Excel, reserves recalculated by
hand, and nobody can answer "what was our outstanding reserve on 31 December?"

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Two APEX applications — internal back office and an agent/customer portal —
   with nine roles, each seeing only what it should
2. Full policy life cycle: quote → issue → instalments → endorsement → renewal →
   cancellation, with **every version preserved and reconstructable**
3. Full claim life cycle: FNOL → assignment → assessment → reserve → decision →
   payment → recovery/subrogation → closure, driven by a real workflow with
   approval limits
4. A rating engine driven entirely by **table-configured tariffs**, versioned by
   effective date, so a rate change never rewrites history
5. A nightly batch: premium earning, lapse processing, reserve revaluation,
   renewal notices, commission calculation
6. Technical reports including a **claims development triangle**
7. An ORDS REST API for agent-system integration
8. A **Spring Boot integration layer** (§10): quote and FNOL APIs, a customer
   claim-status projection, Redis tariff caching, RabbitMQ/AQ event publishing,
   and an Elasticsearch index over adjuster notes — every rule still in PL/SQL

**Proof it is correct**
9. **Premium reconciliation:** written = earned + unearned, at any date
10. **Reserve reconciliation:** opening + movements = closing, per period
11. A utPLSQL suite covering rating, pro-rata endorsement, earning and reserving
12. An "as of date" report that reproduces a past month's figures exactly

**Skills demonstrable in an interview**
13. Every row of the coverage matrix in §11, each pointing at real code

---

## 3. Roles

| Role | Sees | Can do | Cannot |
|---|---|---|---|
| **Customer** *(portal)* | Own policies, own claims, own documents | Get a quote, buy/renew online, pay an instalment, report a claim (FNOL), upload documents, track claim status | See internal reserves, adjuster notes, fraud flags, or anyone else's data |
| **Agent / Broker** | Own book of business | Quote, issue, endorse within authority, renew, view own commission statement, report a claim for a client | Exceed their authority limit, approve claims, see other agents' books or internal loss ratios |
| **Underwriter** | Risks referred to them | Accept/decline/refer a risk, apply loadings and discounts, override the rated premium **with a mandatory reason**, set policy conditions and exclusions | Handle or pay claims, change tariff tables |
| **Policy Administrator** | All policies | Issue, correct, endorse, cancel, reinstate; manage instalment plans | Approve out-of-authority endorsements, touch claims |
| **Claims Handler / Adjuster** | Claims assigned to them | Register FNOL, assign a surveyor, record damage assessment, **set and revise the reserve**, request documents, recommend a decision, approve within their limit | Approve above their limit, pay directly, alter policy data |
| **Claims Manager** | All claims | Approve claims above handler limits, reassign, waive requirements, approve *ex gratia* payments, close/reopen claims | Change tariffs or accounting periods |
| **Fraud Investigator** | Claims flagged or referred | Investigate, record findings, recommend rejection or referral, add a party to the watchlist | Approve or pay a claim |
| **Finance / Accounting** | All financial movements | Post premium receipts, execute claim payments, run period close, produce regulatory reports, calculate and pay commissions | Change policy or claim substance |
| **Actuary / Analyst** | Everything, read-only | Run triangles, loss ratios, portfolio analytics, export | Change any operational data |
| **System Administrator** | Everything | Manage users, roles, tariffs, products, coverages, workflow rules, calendars | *(Every action is audited)* |

**Separation of duties:** the handler who sets a reserve cannot approve a payment
above their limit; the person who approves a claim cannot execute its payment.
Enforced in the database.

---

## 4. Functional Modules

### 4.1 Product & tariff configuration
Products (motor TPL, motor casco, property, travel, personal accident) each with
a coverage catalogue, sums insured, deductibles, exclusions, and a **versioned
tariff**: base rate by risk class, plus coefficient tables (vehicle age, engine
power, driver age/experience, territory, claims history / bonus-malus, building
type, construction year). Every tariff row is **effective-dated** — quoting a
policy for a past date must use the tariff that was in force then.

### 4.2 Quotation & underwriting
Quote from risk data, run the rating engine, apply agent discount within
authority, auto-refer to an underwriter when a referral rule fires (sum insured
above threshold, adverse claims history, watchlisted party), record the decision.

### 4.3 Policy issuance & premium
Issue with a coverage period, produce the premium breakdown per coverage, build
an instalment plan, print the policy document. Track receipts against
instalments; grace period, then lapse; reinstatement rules.

### 4.4 Endorsements (the temporal core)
Mid-term changes create a **new policy version** with a validity window. Each
endorsement is priced **pro-rata from its effective date** to policy expiry, and
may be a debit (extra premium) or a credit (refund). The prior version stays
queryable — "show me the policy as it stood on 12 March" must work.

### 4.5 Claims
FNOL capture (by customer, agent, or call centre), coverage verification against
the policy version **in force on the loss date** (not today's version — this is
the classic mistake), assignment to a handler, surveyor/assessment,
**reserve setting and revision**, document requirements checklist, decision with
approval limits, payment, salvage and subrogation recovery, closure and reopening.

### 4.6 Fraud screening
Rule-driven scoring: claim within N days of policy inception, repeat claimant
across policies, party on watchlist, loss date on a weekend/holiday pattern,
same repair shop recurring, claim amount near the sum insured. Score routes the
claim to normal, enhanced review, or investigation.

### 4.7 Renewals & commission
Renewal candidate generation with bonus-malus applied from claims history,
renewal notices, lapse-and-win-back tracking. Commission accrued on written
premium, clawed back on cancellation, paid per statement period.

### 4.8 Technical accounting & reporting
Written / earned / unearned premium, outstanding claim reserves (case reserves),
IBNR *(simplified, as a configured percentage — say plainly that this is not a
real actuarial reserving exercise)*, loss ratio by product/channel/period, and a
**claims development triangle**.

---

## 5. Data Model

```
-- Configuration (all effective-dated)
products            (product_id, code, name, line_of_business, is_active)
coverages           (coverage_id, product_id, code, name, is_mandatory,
                     default_sum_insured, default_deductible)
tariff_versions     (tariff_id, product_id, version_no, effective_from,
                     effective_to, approved_by, status)
tariff_base_rates   (rate_id, tariff_id, risk_class, base_rate)
tariff_factors      (factor_id, tariff_id, factor_type, band_from, band_to,
                     factor_value)
    -- factor_type: VEHICLE_AGE | ENGINE_POWER | DRIVER_AGE | DRIVER_EXP
    --              | TERRITORY | BONUS_MALUS | BUILDING_TYPE | ...
referral_rules      (rule_id, product_id, condition_sql, referral_reason, active)
fraud_rules         (rule_id, rule_code, description, points, active_from)
document_requirements (req_id, claim_type, doc_type, is_mandatory)
approval_limits     (role_code, limit_type, max_amount)
holiday_calendar    (calendar_date, is_working_day)
periods             (period_yyyymm, status, closed_by, closed_at)

-- Parties
parties             (party_id, party_type, tax_id, full_name, birth_date,
                     phone, address, is_watchlisted)
agents              (agent_id, party_id, code, channel, commission_rate,
                     authority_limit, manager_id NULL -> agents.agent_id)
app_users           (user_id, username, party_id, role_scope, is_active)
user_roles          (user_id, role_code, granted_by, granted_at)

-- Risk objects
vehicles            (vehicle_id, vin UNIQUE, make, model, year, engine_power,
                     value, plate_no)
properties          (property_id, address, building_type, construction_year,
                     area_sqm, value)
insured_persons     (ip_id, party_id, occupation, risk_class)

-- Quotation
quotes              (quote_id, product_id, agent_id, party_id, quote_date,
                     valid_until, status, rated_premium, offered_premium,
                     tariff_id_used)
quote_risks         (qrisk_id, quote_id, risk_type, risk_ref_id)
quote_coverages     (qcov_id, quote_id, coverage_id, sum_insured,
                     deductible, premium)
quote_factors       (qf_id, quote_id, factor_type, factor_value, applied_value)
    -- the rating audit trail: how the number was reached

-- Policy (versioned)
policies            (policy_id, policy_no UNIQUE, product_id, agent_id,
                     holder_party_id, status, inception_date, expiry_date,
                     current_version_no, renewed_from_policy_id NULL)
policy_versions     (version_id, policy_id, version_no,
                     valid_from, valid_to,
                     endorsement_id NULL, total_premium,
                     created_by, created_at)
policy_coverages    (pc_id, version_id, coverage_id, sum_insured,
                     deductible, premium)
policy_risks        (pr_id, version_id, risk_type, risk_ref_id)
policy_parties      (pp_id, version_id, party_id, role)
    -- role: HOLDER | INSURED | DRIVER | BENEFICIARY | LIENHOLDER
endorsements        (endorsement_id, policy_id, type, effective_date,
                     reason, premium_delta, requested_by, approved_by,
                     status, created_at)

-- Premium & receipts
premium_instalments (inst_id, policy_id, version_id, instalment_no,
                     due_date, amount, paid_amount, status)
receipts            (receipt_id, policy_id, amount, receipt_date,
                     method, reference, posted_by, reversal_of NULL)
receipt_allocations (alloc_id, receipt_id, inst_id, amount)
premium_earning     (earn_id, policy_id, period_yyyymm, written_amt,
                     earned_amt, unearned_amt, calc_run_id)

-- Claims
claims              (claim_id, claim_no UNIQUE, policy_id,
                     policy_version_id,          -- version in force on loss_date
                     loss_date, report_date, claim_type, description,
                     status, handler_id, manager_id,
                     fraud_score, fraud_status,
                     closed_at, reopened_count)
claim_items         (item_id, claim_id, coverage_id, description,
                     claimed_amount, assessed_amount, approved_amount)
claim_reserves      (reserve_id, claim_id, reserve_type, amount,
                     effective_date, set_by, reason)
    -- reserve_type: CASE | LAE ; history is kept, never updated in place
claim_documents     (doc_id, claim_id, doc_type, file_blob, mime_type,
                     uploaded_by, uploaded_at, is_verified)
claim_events        (event_id, claim_id, from_status, to_status, actor,
                     note, event_ts)
claim_payments      (payment_id, claim_id, payee_party_id, amount,
                     payment_date, approved_by, executed_by, status)
recoveries          (recovery_id, claim_id, type, amount, received_date)
    -- type: SALVAGE | SUBROGATION | REINSURANCE
fraud_findings      (finding_id, claim_id, rule_id, points, detail, detected_at)
investigations      (inv_id, claim_id, investigator_id, opened_at,
                     findings, recommendation, closed_at)

-- Commission
commission_entries  (comm_id, agent_id, policy_id, period_yyyymm,
                     base_amount, rate, amount, entry_type)
    -- entry_type: ACCRUAL | CLAWBACK | PAYMENT
commission_statements (stmt_id, agent_id, period_yyyymm, total, status, paid_at)

-- Operations
batch_runs          (batch_id, batch_name, business_date, started_at,
                     finished_at, status, records_processed, error_text)
batch_errors        (err_id, batch_id, entity_type, entity_id, error_code,
                     error_msg, raised_at)
audit_log           (audit_id, table_name, pk_value, action, old_row_json,
                     new_row_json, changed_by, changed_at)
```

**Partitioning:** `claim_events`, `premium_earning`, `audit_log` range-partitioned
by month; `claims` optionally by loss-year for triangle queries.

---

## 6. The Temporal Rules (the heart of the project)

These four rules are what make PolisHub an advanced project. Get them right and
everything else follows.

1. **A claim is assessed against the policy version in force on the *loss date*,
   never the current version.** Store `policy_version_id` on the claim at
   registration and resolve it by `loss_date BETWEEN valid_from AND valid_to`.
2. **Policy versions never overlap and never gap.** Exactly one version covers
   any instant between inception and expiry.
3. **A tariff is chosen by the quote/endorsement effective date**, not by
   `SYSDATE`. Re-quoting an old policy must reproduce the old premium exactly.
4. **Reserves are an append-only history.** You never `UPDATE` a reserve amount;
   you insert a new row with an effective date. "Outstanding reserve as of
   31 December" is then a query, not a guess.

---

## 7. Invariants (enforced in the database)

1. No overlapping `policy_versions` for a policy — enforce with a constraint or
   a validated trigger, and test it under concurrency.
2. `SUM(policy_coverages.premium) = policy_versions.total_premium`.
3. `SUM(receipt_allocations.amount) <= receipts.amount`, and an instalment's
   `paid_amount` never exceeds its `amount`.
4. A claim payment cannot exceed `approved_amount`, which cannot exceed the
   coverage's sum insured less the deductible.
5. Nothing may post into a closed period.
6. An approval above the actor's `approval_limits` entry is rejected — in the
   database.
7. A claim cannot move to `PAID` while a mandatory document is unverified.
8. `written = earned + unearned` for every policy at every period end.

---

## 8. PL/SQL Package Architecture

| Package | Responsibility |
|---|---|
| `pkg_tariff` | Effective-dated tariff resolution, factor lookup, result-cached |
| `pkg_rating` | The rating engine: base rate × factors × coverage, with a full audit trail into `quote_factors` |
| `pkg_quote` | Quote life cycle, referral-rule evaluation |
| `pkg_underwriting` | Accept/decline/refer, loadings, overrides with reasons |
| `pkg_policy` | Issuance, versioning, the non-overlap guarantee, "as of date" retrieval |
| `pkg_endorsement` | Endorsement pricing (pro-rata), new-version creation, cancellation refunds |
| `pkg_premium` | Instalment plans, receipt posting and allocation, grace, lapse, reinstatement |
| `pkg_earning` | Monthly premium earning / unearned reserve |
| `pkg_claim` | FNOL, coverage verification against the loss-date version, status machine |
| `pkg_reserve` | Append-only reserve setting, movement queries, as-of-date outstanding |
| `pkg_claim_payment` | Approval limits, payment execution, recoveries |
| `pkg_fraud` | Rule-driven scoring, routing, watchlist |
| `pkg_renewal` | Candidate generation, bonus-malus, notices |
| `pkg_commission` | Accrual, clawback, statements |
| `pkg_workflow` | Task creation, assignment, escalation, SLA timers |
| `pkg_security` | Current user, role and authority checks, VPD predicates |
| `pkg_audit` | Autonomous-transaction audit writer |
| `pkg_report` | Pipelined sources, triangle generation, ref cursors |
| `pkg_batch` | Orchestration, restartability, error capture |
| `pkg_api` | ORDS handlers, JSON in / JSON out |

---

## 9. APEX Application Design

### Applications
- **`PolisHub Back Office`** — underwriting, policy admin, claims, finance
- **`PolisHub Portal`** — customer and agent self-service

### Key pages

| Page | Type | Notes |
|---|---|---|
| Underwriter dashboard | Cards + JET charts | Referral queue, bound premium today, loss ratio by product |
| Quote wizard | Multi-page wizard + APEX Collections | Risk data → coverages → rating result → bind. Basket held in a collection until bind |
| Rating breakdown | Report region | Every factor and its contribution — the rating audit trail made visible |
| Policy search | Faceted search | Product, status, agent, inception band, expiry band |
| Policy detail | Tabs | Versions (with an **as-of-date picker**), coverages, parties, instalments, receipts, claims, documents |
| Endorsement wizard | Wizard + approval | Pro-rata premium preview before commit |
| FNOL | Form + file upload | Available in both apps; auto-resolves the loss-date policy version |
| Claim workspace | Tabs + IG | Items, assessment, **reserve history**, documents checklist, events timeline, payments |
| Claims worklist | IG + faceted search | Handler queue with SLA colouring |
| Fraud review | IR + drill-down | Score, triggered rules, related claims |
| Approvals inbox | APEX Approvals / Task List | Underwriting referrals, endorsements, claim decisions, payments |
| Finance | IR + forms | Receipt posting, payment execution, period close |
| Commission | IR + statements | Agent statements, clawbacks |
| Analytics | Charts + IR | Triangle, loss ratio, portfolio mix, written vs earned |
| Batch monitor | IR | Runs, errors, re-run action |
| Configuration | IG + forms | Products, coverages, tariff versions, factors, rules, calendar |

### APEX techniques used deliberately
- **APEX Workflow** (23.x) for the claim life cycle, and **Approvals / Unified
  Task List** for every limit-based decision — this is the module that makes
  APEX the right tool for insurance
- **Interactive Grid** with PL/SQL save processes for claim items and tariff factors
- **Faceted search** on policies and claims
- **APEX Collections** for the quote basket before bind
- **Dynamic actions + cascading LOVs** across product → coverage → sum insured bands
- **Authorization schemes** on pages, regions, buttons, **and individual columns**
  (a handler must not see the fraud score on a claim not referred to them)
- **`APEX_MAIL`** for renewal notices and claim-status updates, queued and sent
  from a background process
- **`APEX_WEB_SERVICE`** for an external vehicle-registry or sanctions-list lookup
  (mocked)
- **File upload → BLOB** for claim documents, with a verification workflow
- **Automations** for SLA escalation on stale claims
- **Session state protection**; authorization never depends on a URL parameter

---

## 10. Java / Spring Boot Integration Layer

APEX owns the internal back office — underwriting, claims workspace, finance,
configuration. Spring Boot owns everything outward-facing: the agent-system API,
the customer mobile backend, partner integrations, and document intake.

**The packages in §8 remain the only place business rules live.** This matters
more here than in CreditLine, because insurance rules are temporal and easy to
re-implement *slightly* wrong. Two specific prohibitions:

> **Java must never choose a policy version.** It passes a loss date; PL/SQL
> resolves the version in force. A Java service that queries `policy_versions`
> and picks one has just created a second, divergent implementation of the most
> important rule in the system.
>
> **Java must never compute premium.** It passes risk attributes and an effective
> date; `pkg_rating` returns the premium and its factor breakdown. Rating in two
> places means two answers.

### 10.1 Services

| Service | Purpose | Calls |
|---|---|---|
| `quote-api` | Quotation for agent systems and the website | `pkg_rating.rate_quote`, `pkg_quote` |
| `policy-query-api` | Policy detail, coverages, instalments, **as-of-date view** | `pkg_policy.get_as_of` (REF CURSOR) |
| `fnol-api` | Claim registration from the mobile app / call centre, with photo upload | `pkg_claim.register_fnol` |
| `claim-status-api` | Customer-facing claim tracking — a **filtered** projection | A dedicated view; never the internal claim record |
| `payment-collection-api` | Instalment payment from a gateway or bank channel | `pkg_premium.post_receipt` |
| `partner-integration` | Vehicle registry, sanctions list, repair-shop network | Normalises responses, hands them to PL/SQL |
| `notification-worker` | Renewal notices, claim status updates | Oracle **AQ** via AQ-JMS, or the queue table |
| `agent-portal-bff` | Backend-for-frontend for the agent web app | Aggregates the services above |

### 10.2 Spring modules — which ones, and where

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

### 10.3 Two boundary rules that are specific to insurance

**Projection, not exposure.** `claim-status-api` must return a deliberately
reduced view: status, next required document, expected timeline. It must never
expose the reserve amount, the fraud score, adjuster notes, or the internal
status codes. Build this as a **separate database view with its own grants**, not
as a Java `if` that filters fields — then the rule survives someone adding a
column later.

**Idempotency on intake.** FNOL from a mobile app over a flaky connection will
arrive twice. Payment callbacks from a gateway will arrive twice. Both need an
idempotency key stored and checked in the database, returning the original
result on replay — the same discipline as PayFlow in the Python track, applied
here in PL/SQL.

### 10.4 Calling a package from Spring

```java
@Repository
class ClaimGateway {

    private final SimpleJdbcCall registerFnol;

    ClaimGateway(JdbcTemplate jdbc) {
        this.registerFnol = new SimpleJdbcCall(jdbc)
            .withCatalogName("PKG_CLAIM")
            .withProcedureName("REGISTER_FNOL")
            .declareParameters(
                new SqlParameter("p_policy_no",       Types.VARCHAR),
                new SqlParameter("p_loss_date",       Types.TIMESTAMP),
                new SqlParameter("p_claim_type",      Types.VARCHAR),
                new SqlParameter("p_description",     Types.VARCHAR),
                new SqlParameter("p_idempotency_key", Types.VARCHAR),
                new SqlOutParameter("p_claim_no",     Types.VARCHAR),
                new SqlOutParameter("p_version_used", Types.NUMERIC));
    }
}
```

Note `p_version_used` as an **out** parameter: the API returns which policy
version the claim was booked against, so the caller — and your integration test —
can assert the temporal rule held.

**Structured input.** A quote carries a nested structure (risk object + N
coverages + N drivers). Pass it as a JSON string and expand it inside PL/SQL with
`JSON_TABLE`, rather than fighting Oracle object-type binds over JDBC. Build one
call with `STRUCT`/`ARRAY` binds too, so you can speak to both.

### 10.5 Transaction ownership

**No package procedure commits.** The caller owns the boundary — APEX at the page
process, Spring at `@Transactional`, the scheduler per batch chunk. The sole
exception is the deliberate one: `pkg_audit`, `fraud_findings` logging and
`batch_errors` write through `PRAGMA AUTONOMOUS_TRANSACTION`.

A commit inside a package called from a `@Transactional` method silently ends
Spring's transaction; a later rollback then cannot undo what was written. In a
system that books financial reserves, that is a correctness bug, not an
inconvenience.

### 10.6 Error contract

```
pkg_claim: RAISE_APPLICATION_ERROR(-20014, 'NO_COVER_ON_LOSS_DATE')
   ↓ SQLException, errorCode = 20014
   ↓ SQLExceptionTranslator → DomainException("NO_COVER_ON_LOSS_DATE")
   ↓ @RestControllerAdvice  → 422 {"code":"NO_COVER_ON_LOSS_DATE"}
```

| Code | Meaning | HTTP |
|---|---|---|
| 20011 | `POLICY_NOT_IN_FORCE` | 409 |
| 20012 | `VERSION_OVERLAP` | 409 |
| 20014 | `NO_COVER_ON_LOSS_DATE` | 422 |
| 20015 | `DOCUMENT_REQUIRED` | 422 |
| 20021 | `LIMIT_EXCEEDED` | 403 |
| 20031 | `PERIOD_CLOSED` | 409 |
| 20041 | `TARIFF_NOT_EFFECTIVE` | 422 |

Codes are the contract; message text and localisation live in Java. Test the map.

### 10.7 Type mapping

| Oracle | Java | Note |
|---|---|---|
| `NUMBER` (premium, reserve, sum insured) | `BigDecimal` | Never `double` |
| `DATE` (loss date, effective date) | `LocalDateTime` | Oracle `DATE` has a time part; truncating it can move a claim onto the wrong policy version |
| `TIMESTAMP WITH TIME ZONE` | `OffsetDateTime` | Loss time zone matters for cross-border motor claims |
| `CHAR(1)` `'Y'`/`'N'` | `boolean` | |
| `SYS_REFCURSOR` | `RowMapper<T>` | As-of-date policy view, triangle rows |
| Object type | Java `record` | Map explicitly |
| Nested table | JSON + `JSON_TABLE` | Coverage baskets, driver lists |
| `BLOB` (claim photos, documents) | Streamed | Never load a document fully into heap; stream to storage |

The `DATE` row is not a style note. A loss recorded at `2026-03-12 23:40` that
Java truncates to `2026-03-12 00:00` can land on the pre-endorsement version when
the endorsement took effect that afternoon. That is a wrong coverage decision
caused by a type mapping.

### 10.8 Supporting infrastructure — what to connect, and exactly where

Oracle does the domain work. These components live only in the Java layer, and
each earns its place against a specific requirement in this system. **If you
cannot point at the row that justifies it, do not deploy it.**

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **Redis — tariff cache** | `pkg_tariff` factor lookups behind `quote-api`: base rates, and every factor table (vehicle age, engine power, driver age, territory, bonus-malus, building type) | The single highest-value cache in the system. Rating reads dozens of factor rows per quote, the tables change a few times a year, and they are **effective-dated — so the cache key must include the effective date**, never just the factor type. Get that wrong and you serve last year's rate |
| **Redis — quote session state** | The multi-step quote wizard in the agent portal, before bind | APEX uses APEX Collections for the same job. The Java portal needs its own scratch space; a quote that is never bound should not touch Oracle |
| **Redis — idempotency store** | `fnol-api` (mobile app retries), `payment-collection-api` (gateway callbacks retry by design) | Fast path only — the **durable** idempotency record is a table in Oracle. Redis being empty must never cause a double claim |
| **Redis — rate limiting** | `quote-api` and `policy-query-api` per agent / partner API key | Agent systems poll. One misconfigured integration must not become a denial of service against rating |
| **Redis — hot reference data** | Product and coverage catalogue, document requirement checklists, territory lists | Read constantly by the portal, changed rarely |
| **Redis — distributed lock** | Renewal-notice generation if you ever run it from Java rather than the scheduler | Two pods must not send the same customer two notices |
| **RabbitMQ — claim lifecycle events** | `ClaimRegistered`, `ClaimStatusChanged`, `ReserveRevised`, `ClaimPaid` | Feeds notification, analytics, and the partner repair network. Consumers must not poll the claims table |
| **RabbitMQ — notification dispatch** | Renewal notices (45/30/15 days), claim status updates, payment reminders, document requests | Enqueued by the nightly batch and by API actions; `notification-worker` consumes with retry + DLQ. Sending must never sit inside the business transaction |
| **RabbitMQ — document processing pipeline** | After a claim photo lands: virus scan → thumbnail → OCR of a repair estimate → mark verifiable | Slow, failure-prone, and irrelevant to the FNOL response. Classic async work |
| **RabbitMQ — async fraud scoring** | Enhanced screening on claims above a threshold, and partner watchlist checks | Registration must return fast; scoring can land seconds later. Note that the *rule-based* score stays synchronous in `pkg_fraud` — only the expensive external checks go async |
| **RabbitMQ — partner integration** | Vehicle registry, sanctions list, repair-shop network calls | Third-party latency must never block a quote or an FNOL |
| **RabbitMQ — DLQ** | Every consumer above | Inspect a poison message by hand at least once |
| **Oracle AQ** | The first hop out of a transaction — see §10.8.1 | The atomicity decision, not a detail |
| **Elasticsearch** | Free-text search across adjuster notes, claim descriptions, party names (fuzzy, transliterated), and OCR'd document text | **The one place ES is genuinely earned in this system.** "Find every claim mentioning this repair shop" is not a structured query. Oracle stays the source of truth; ES is a derived index, rebuildable — the same rule as DocuVault in the Python track |
| **MinIO / S3** | Claim photos, surveyor reports, policy PDFs, OCR outputs | See §10.9. Insurance document volume grows fast; this is the more likely of the two options there |
| **Prometheus + Grafana** | Quote latency (rating is the hot path), FNOL rate, **SLA breach count**, queue depth, DLQ depth, batch step duration, ES index lag, pool saturation | The claims SLA is a business commitment, so it belongs on a dashboard, not only in a table |
| **Sentry** | All Java services | |
| **Keycloak / OAuth2 provider** | Agent, partner and customer authentication | APEX keeps its own session auth for internal staff. Two identity domains on purpose — internal staff and external parties are not the same population |
| **Quartz** | Nothing, initially | The nightly chain in §11 stays in `DBMS_SCHEDULER`, next to the data it processes |

**Deliberately NOT connected — and be ready to say why:**

| Component | Why not |
|---|---|
| **Redis on reserves or outstanding balances** | Reserve figures drive financial reporting. A stale reserve is a wrong number in a regulatory report. Consistent with the append-only reserve rule in §6 |
| **Redis on the policy version resolution** | The most correctness-critical lookup in the system. Never serve it from a cache that can be stale or keyed slightly wrong |
| **Kafka** | Nothing here needs a replayable log, ordered partitions, or stream processing. If a real-time analytics pipeline arrives later, Kafka is the answer then — say so, don't pre-build it |
| **A search index over structured claim fields** | Status, date range, handler, product are structured filters. Oracle indexes and faceted search handle them. ES is only for the unstructured text |

#### 10.8.1 The atomicity decision: Oracle AQ vs RabbitMQ

A `ClaimPaid` or `ReserveRevised` event must be published **if and only if** the
database change committed. Three options:

| Option | Guarantee | Cost |
|---|---|---|
| Publish to RabbitMQ inside the service method | **Broken.** Commit can succeed while publish fails, or the reverse | — |
| **Oracle AQ**, enqueued in the same transaction | Atomic by construction — the enqueue *is* a database write | Oracle-specific; consumers need AQ-JMS |
| **Outbox table** + a Spring relay polling and publishing to RabbitMQ | Atomic write, at-least-once delivery, broker-agnostic consumers | You own the relay; consumers must be idempotent |

**Recommended:** Oracle AQ for the first hop, bridged to RabbitMQ when non-Oracle
consumers appear. Build the outbox variant as well — it is the pattern
interviewers ask about, and FleetTrack in the Python track already taught you the
failure mode it closes.

Every consumer must be **idempotent**. At-least-once means duplicates are normal.

#### 10.8.2 Elasticsearch sync — reuse, don't reinvent

The claim/notes index is kept current by the **same event stream** as everything
else: `ClaimRegistered` / `ClaimStatusChanged` / a `NoteAdded` event feeds an
indexing consumer. Plus a `POST /admin/reindex` endpoint that rebuilds the index
entirely from Oracle.

State the rule explicitly, because it is a standard interview trap: **Oracle is
the source of truth; Elasticsearch is derived and must always be rebuildable.**

### 10.9 Document handling

Multipart upload arrives at `fnol-api`. Two viable designs — pick one, document why:

| Option | Shape |
|---|---|
| **BLOB in Oracle** | Spring streams into `claim_documents.file_blob`. Simple, transactional, backed up with the database, but grows the DB fast |
| **Object storage + reference** | Spring writes to S3/MinIO, stores the key in Oracle. Scales better, but the document is no longer inside your transaction or your backup |

Whichever you choose, the **document requirement checklist** stays in PL/SQL —
whether a claim may progress is a business rule, not a storage concern.

### 10.10 Testing

- **Testcontainers** with `gvenzl/oracle-free`; Flyway builds the schema on start,
  packages as repeatable migrations (`R__pkg_claim.sql`)
- **utPLSQL** runs in the same container — the §12 suite is invoked, not replaced
- Spring integration tests assert the **boundary**: correct binds, correct error
  translation, correct projection
- **The temporal test must exist at the API level too.** Register a claim through
  `fnol-api` with a loss date before an endorsement, and assert the returned
  `version_used` is the pre-endorsement version. It is not enough that PL/SQL is
  right; prove the API did not silently pass today's date
- A test that the customer projection never leaks reserve, fraud score, or
  adjuster notes — assert on the whole response body, not on selected fields
- Idempotency tests: the same FNOL key twice returns one claim; the same payment
  callback twice posts one receipt

### 10.11 Operational concerns

| Item | Choice |
|---|---|
| Driver | `ojdbc11` |
| Pool | HikariCP; Oracle UCP only for RAC failover needs |
| Migrations | Flyway — versioned for tables, repeatable for packages and views |
| API docs | springdoc-openapi; publish the agent-facing contract |
| Auth | OAuth2 / JWT for agent and partner APIs; customers via the portal's own flow |
| **Identity bridge** | Push the authenticated principal into the DB session (`DBMS_SESSION.SET_IDENTIFIER` or an application context) at transaction start |
| Messaging | Oracle AQ via AQ-JMS for notification dispatch, so the enqueue is inside the same transaction as the business change |

The identity bridge is load-bearing here. Every agent hits the database as the
same pooled user. Without pushing the real principal into a session context, the
VPD policy that limits an agent to their own book **does not apply to API
traffic** — and the audit log records the pool user for every action. Test this
explicitly: call the API as agent A, request agent B's policy, expect an empty
result from the database itself.

### 10.12 Definition of Done — Java layer

- [ ] No package commits; caller owns the transaction boundary
- [ ] Java never resolves a policy version and never computes premium
- [ ] `version_used` returned by FNOL and asserted in an API-level temporal test
- [ ] Error-code table implemented end to end, with a mapping test
- [ ] Customer projection enforced by a view with its own grants, not Java filtering
- [ ] Idempotency on FNOL and payment callbacks, tested with duplicates
- [ ] Authenticated identity pushed into the DB session; VPD proven to apply to
      API traffic
- [ ] Money as `BigDecimal`; loss timestamps not truncated
- [ ] Testcontainers + Flyway + utPLSQL green in CI
- [ ] Document storage decision written down with its tradeoff

### 10.13 Interview Questions — the Java/Oracle boundary

1. In a Java + Oracle system, where do business rules live, and how do you keep
   them from being implemented twice?
2. Why must Java not pick the policy version itself?
3. What happens if a PL/SQL procedure commits inside a Spring `@Transactional`
   method?
4. How does the database know which agent is calling, when everyone shares a
   connection pool — and what breaks if you skip that?
5. How do you map `RAISE_APPLICATION_ERROR` to a meaningful HTTP status?
6. How would you pass a quote's nested structure into PL/SQL from Java?
7. Oracle `DATE` vs `TIMESTAMP` — and how could the wrong Java type produce a
   wrong coverage decision?
8. How do you guarantee a claim reported twice from a mobile app creates one claim?
9. Documents: BLOB in the database or object storage — argue both sides.
10. How do you test a feature that spans a Spring service and a PL/SQL package?

---

## 11. Advanced SQL & PL/SQL Coverage Matrix

This matrix is **additive** to CreditLine's — the features below are the ones
insurance forces you to use, or uses far more heavily.

### SQL

| Feature | Where it is used |
|---|---|
| Temporal joins (`BETWEEN valid_from AND valid_to`) | Resolving the policy version in force on a loss date; tariff in force on a quote date |
| `MERGE` (heavily) | Premium earning per period; reserve snapshot upsert; renewal candidate refresh |
| Analytic `LAG`/`LEAD` | Reserve movement: this reserve vs the previous one, per claim |
| `SUM() OVER (PARTITION BY ... ORDER BY ...)` | Cumulative paid and cumulative incurred, per claim, per development period |
| **`PIVOT` on a self-joined aggregate** | The **claims development triangle**: accident period × development period |
| `GROUPING SETS` / `ROLLUP` | Loss ratio by product × channel × period with subtotals |
| `MATCH_RECOGNIZE` | Fraud patterns: claim shortly after inception followed by another shortly after endorsement |
| Recursive `WITH` | Agent hierarchy for override commission |
| `LISTAGG` | Coverage summary strings, triggered fraud-rule lists |
| `INTERVAL` / date arithmetic / `MONTHS_BETWEEN` / `ADD_MONTHS` | Pro-rata endorsement pricing, earning fractions, SLA deadlines |
| Business-day arithmetic against a calendar table | Claim SLA and grace-period calculation |
| Set operators (`MINUS`) | Reconciliation: written vs earned + unearned |
| `FLASHBACK QUERY` / `FLASHBACK VERSIONS QUERY` | "Who changed this reserve and when" investigations, alongside your own audit log |
| Function-based unique index | One current version per policy; case-insensitive party search |
| Range partitioning + pruning | `claim_events`, `premium_earning`, `audit_log` |
| Composite + bitmap indexes | Claim worklist filters on low-cardinality status/type |
| Materialized view with query rewrite | Loss-ratio dashboard aggregates |
| **JSON** (`JSON_TABLE`, `JSON_OBJECT`, `JSON_SERIALIZE`) | ORDS payloads, external registry responses, audit row snapshots |
| `XMLTABLE` *(if a regulator feed needs it)* | Optional; regulatory export |
| Virtual columns | Derived `policy_year`, `accident_period` used in the triangle |
| `DBMS_XPLAN`, SQL Monitor | The tuning story on the triangle query |
| VPD / FGAC | Agents see only their own book, enforced in the database |
| Data Redaction *(optional)* | Masking party tax IDs from non-privileged roles |

### PL/SQL

| Feature | Where it is used |
|---|---|
| Packages, overloading, initialization sections | The architecture in §8 |
| Object types + member methods | `t_money`, `t_coverage_line`; rating result as an object |
| Nested tables / `VARRAY` / associative arrays | Factor sets, coverage baskets, document checklists |
| **Table functions + `PIPELINED`** | Triangle rows, rating breakdown, as-of-date policy view |
| **`BULK COLLECT` + `LIMIT`** | Monthly earning across the whole portfolio |
| **`FORALL` + `SAVE EXCEPTIONS`** | Bulk earning and reserve snapshot writes; failures isolated |
| Ref cursors (weak/strong) | APEX regions, ORDS handlers |
| **Autonomous transactions** | Audit and fraud-detection logging that survives a rollback |
| **Compound triggers** | Version-overlap validation without mutating-table errors |
| `INSTEAD OF` triggers | Updatable "current policy" view over the versioned tables |
| User-defined exceptions + `PRAGMA EXCEPTION_INIT` | `e_no_cover_on_loss_date`, `e_limit_exceeded`, `e_period_closed`, `e_version_overlap` |
| Dynamic SQL with binds | `referral_rules.condition_sql` evaluated safely — and you explain exactly why the naive version is an injection hole |
| `DBMS_SQL` | The generic report builder where the column list is not known at compile time |
| `DBMS_SCHEDULER` chains + windows | The nightly chain in §12 |
| `DBMS_LOCK` | Single-instance batch guard |
| `DBMS_APPLICATION_INFO` | Long-running job instrumentation |
| Result-cached functions | Tariff factor lookup |
| Deterministic functions | Earning-fraction helpers used inside SQL |
| `WITH FUNCTION` / `PRAGMA UDF` | Pro-rata helper called from SQL without the context switch — measured |
| Conditional compilation | Debug tracing compiled out |
| `DBMS_HPROF` | Profiling the rating engine under a bulk re-rate |
| **utPLSQL** | The suite in §13 |
| `APEX_APPROVAL`, `APEX_WORKFLOW` APIs | Driving the claim workflow from PL/SQL, not just declaratively |
| Advanced Queuing (AQ) *(stretch)* | Decoupling notification dispatch from the transaction |

---

## 12. Batch Design

```
DBMS_SCHEDULER chain, run nightly on the business date:

  1. open_business_date        → guard: prior date closed, not a holiday
  2. lapse_processing          → instalments past grace → policy LAPSED
  3. earn_premium              → MERGE per policy per period
  4. revalue_reserves          → snapshot outstanding case reserves
  5. score_new_claims          → fraud rules over claims registered today
  6. escalate_sla_breaches     → workflow tasks past SLA
  7. generate_renewal_notices  → 45/30/15 days before expiry
  8. accrue_commission         → on premium written today
  9. refresh_analytics         → materialized views
 10. dispatch_notifications    → APEX_MAIL from the queue table
 11. close_business_date
```

Same non-negotiables as CreditLine — **idempotent, restartable, single-instance,
error-tolerant (`SAVE EXCEPTIONS`), observable, chunked with a tuned `LIMIT`** —
plus one more that is specific to insurance:

- **Period-aware.** Once a monthly period is closed, re-running the batch for a
  date inside it must refuse, not silently rewrite earned premium.

---

## 13. Testing Strategy

| Layer | What |
|---|---|
| **utPLSQL** | Rating: each factor applied in the right order; the same risk quoted with two tariff versions gives two different, correct premiums |
| utPLSQL | Pro-rata endorsement: mid-term increase, mid-term decrease, cancellation refund, endorsement on the inception date, endorsement on the expiry date |
| utPLSQL | Earning: a 12-month policy earns exactly its premium over 12 periods, no rounding drift on the last one |
| utPLSQL | Reserve movement: opening + movements = closing |
| utPLSQL | Every domain exception raised where expected |
| **Temporal (the critical one)** | A claim with a loss date **before** an endorsement is assessed on the **pre-endorsement** version. Write this test first |
| Temporal | Policy versions never overlap or gap — including under two concurrent endorsements |
| Integration | Full life cycle: quote → bind → 3 instalments → endorsement → claim → reserve revised twice → approval → payment → recovery → renewal |
| **Reconciliation** | Written = earned + unearned at every period end; reserve roll-forward ties |
| As-of-date | Reproduce last month's outstanding-reserve report exactly, after this month's movements |
| Authority | A handler cannot approve above their limit — attempted **directly in SQL**, not just through the UI |
| Separation of duties | The approver cannot also execute the payment |
| Security | An agent cannot read another agent's book through ORDS |
| Concurrency | Two endorsements on the same policy at once — one must fail cleanly |
| Batch | Re-run for a closed period is refused; re-run for an open date is a no-op |
| Performance | Triangle query and monthly earning at 100k policies / 20k claims, plans recorded before and after |

---

## 14. Build Plan

### Stage 1 — Configuration & rating
Products, coverages, effective-dated tariff versions and factors, `pkg_tariff`
and `pkg_rating` with a full audit trail into `quote_factors`, utPLSQL coverage.
*Done when:* re-quoting a past date reproduces the historical premium exactly.

### Stage 2 — Quote, underwriting, issuance
Quote wizard with APEX Collections, referral rules, underwriting decisions with
overrides and reasons, policy issuance, version 1 created.
*Done when:* a referral routes to an underwriter and the decision is recorded
with its reason.

### Stage 3 — Versioning & endorsements
`pkg_policy` version management with the non-overlap guarantee, as-of-date
retrieval, `pkg_endorsement` pro-rata pricing, cancellation refunds.
*Done when:* the temporal tests in §13 pass, including under concurrency.

### Stage 4 — Premium & receipts
Instalment plans, receipt posting and allocation, grace, lapse, reinstatement,
period earning with `MERGE`.
*Done when:* written = earned + unearned reconciles.

### Stage 5 — Claims core
FNOL, **loss-date version resolution**, coverage verification, status machine,
assignment, assessment, append-only reserves, document checklist.
*Done when:* the pre-endorsement-loss-date test passes.

### Stage 6 — Claims decisions & payment
Approval limits, APEX Approvals/Workflow wiring, payment execution with
separation of duties, recoveries, closure and reopening.

### Stage 7 — Fraud, renewals, commission
Fraud rules and routing, investigations, watchlist; renewal generation with
bonus-malus and notices; commission accrual, clawback, statements.

### Stage 8 — Batch, analytics, integration, hardening
The nightly chain, the **claims triangle**, loss-ratio analytics, materialized
views, ORDS API, VPD policies, the documented tuning pass, period close.

---

## 15. Definition of Done

- [ ] All ten roles implemented; agent/branch scoping enforced by **VPD**, not the UI
- [ ] Separation of duties and approval limits enforced in the database
- [ ] Tariffs effective-dated; a past quote reproduces exactly
- [ ] Policy versions never overlap or gap, proven under concurrency
- [ ] As-of-date policy retrieval working
- [ ] Endorsements priced pro-rata, both debit and credit, with prior versions intact
- [ ] **Claims assessed against the loss-date policy version**
- [ ] Reserves append-only; as-of-date outstanding reserve reproducible
- [ ] Written = earned + unearned reconciles at every period end
- [ ] Reserve roll-forward ties: opening + movements = closing
- [ ] Claim workflow with approval limits, SLA escalation, document gating
- [ ] Fraud scoring routing claims correctly
- [ ] Renewals with bonus-malus; commission accrual and clawback
- [ ] Claims development triangle produced from real data
- [ ] Nightly batch: idempotent, restartable, period-aware, error-tolerant
- [ ] Closed periods reject postings
- [ ] Full audit trail via autonomous transactions
- [ ] utPLSQL suite green
- [ ] ORDS API documented
- [ ] Tuning story documented with before/after plans
- [ ] Every row of §11 pointing at real code

---

## 16. Interview Questions This Project Should Let You Answer

**Domain / modelling**
1. Why is a claim assessed against the policy version in force on the loss date,
   and what breaks if you use the current version?
2. How do you guarantee policy versions never overlap or gap — and how did you
   test that under concurrent endorsements?
3. Why are reserves append-only instead of updated in place?
4. How do you reproduce last quarter's outstanding reserve after this quarter's
   movements?
5. Walk me through pro-rata endorsement pricing, including the cancellation case.
6. What does "written = earned + unearned" mean, and how do you prove it holds?
7. How is a claims development triangle built in SQL?

**Oracle / PL-SQL**
8. Where did you use `MERGE`, and why not separate insert/update logic?
9. `BULK COLLECT` + `FORALL` + `SAVE EXCEPTIONS` — what does each part buy you?
10. Why a compound trigger for version validation instead of a row trigger?
11. Why is your audit writer an autonomous transaction, and what's the risk of one?
12. Show me your dynamic SQL and explain how it's injection-safe.
13. What does a pipelined table function give you over a global temporary table?
14. How does VPD differ from an APEX authorization scheme, and why do you need both?
15. How did you make the triangle query fast — what did the plan look like before?
16. Result cache, `DETERMINISTIC`, `PRAGMA UDF` — when does each actually help,
    and how did you measure it?

**APEX**
17. When do you use a declarative Interactive Grid save versus a PL/SQL process?
18. How does APEX Approvals let you enforce approval limits without hand-rolling
    a workflow table?
19. How do you stop a user from reaching a page or a column they shouldn't see,
    including via a crafted URL?

---

## 17. Common Mistakes to Watch For

- **Verifying a claim against the current policy version.** The single most
  important mistake this project exists to teach you not to make
- Updating reserves in place, destroying the movement history
- Rating with `SYSDATE` instead of the effective date
- Rounding drift so the last instalment or last earning period doesn't tie
- Business logic in APEX processes instead of packages
- Row-by-row processing where `FORALL` or a set-based statement belongs
- Authorization only in the UI, so ORDS or SQL*Plus bypasses it
- Treating IBNR as if a configured percentage were real actuarial reserving —
  **say plainly in your documentation that it is a simplification**
- Letting the batch rewrite a closed period

---

## 18. Scope Honesty

This is a **portfolio-scale** insurance system, not a production policy
administration platform. Deliberately out of scope, and worth naming in an
interview as what you'd tackle next:

- Real actuarial reserving (chain-ladder, Bornhuetter-Ferguson)
- Reinsurance treaties and cessions
- Coinsurance and multi-insurer risk sharing
- Regulatory reporting to a specific jurisdiction's format
- Full IFRS 17 measurement models
- Multi-currency portfolios
