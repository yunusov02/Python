# Oracle + APEX Projects

Two projects, built on Oracle Database and Oracle APEX, designed so that
**advanced SQL and advanced PL/SQL are exercised because the domain genuinely
requires them** — not as feature checklists bolted onto a CRUD app.

| # | Project | Domain | Level | Focus |
|---|---|---|---|---|
| 1 | [CreditLine](01-creditline-fintech.md) | FinTech — lending / credit | Middle → Middle+ | Set-based batch processing, transactional money movement, double-entry accounting, `BULK COLLECT`/`FORALL`, `DBMS_SCHEDULER` |
| 2 | [PolisHub](02-polishub-insurance.md) | Insurance — policy & claims | Middle+ | Temporal data (versioning, effective dating, as-of-date queries), workflow & approvals, `MERGE`-heavy processing, analytics (`PIVOT`, `MATCH_RECOGNIZE`) |

Both carry a **Java / Spring Boot integration layer** (§9 in CreditLine, §10 in
PolisHub) — because this is the stack these systems actually run on in practice:
Oracle holds the rules, APEX serves internal staff, and Spring Boot serves
everything outward-facing.

---

## Order

**Build CreditLine first.** It establishes the foundations — package
architecture, audit via autonomous transactions, batch discipline, double-entry
posting, VPD, utPLSQL — that PolisHub then assumes and extends.

PolisHub is deliberately the harder of the two. Lending is temporally simple:
one schedule, moving one direction. Insurance is temporally messy: a policy has
versions, a claim is judged against the version in force on the **loss date**,
reserves move over time, and every number must be reconstructable **as of any
date**. That difficulty is the point.

---

## What each project covers

Both files carry a **coverage matrix** (§10 in CreditLine, §11 in PolisHub) that
maps every advanced SQL and PL/SQL feature to the exact place in the system where
it is used. Together they cover:

**SQL** — analytic functions and window frames, `MATCH_RECOGNIZE`, `MODEL`,
`PIVOT`/`UNPIVOT`, `GROUPING SETS`/`ROLLUP`/`CUBE`, recursive `WITH` and
`CONNECT BY`, `MERGE`, multi-table insert, temporal joins, flashback query,
JSON, partitioning and pruning, function-based/bitmap/composite indexes,
materialized views, virtual columns, VPD/FGAC, `DBMS_XPLAN` and a real tuning
story.

**PL/SQL** — package architecture, object types with member methods, all three
collection types, `BULK COLLECT` + `LIMIT`, `FORALL` + `SAVE EXCEPTIONS` +
`%BULK_EXCEPTIONS`, pipelined table functions, ref cursors, autonomous
transactions, compound and `INSTEAD OF` triggers, user-defined exceptions with
`PRAGMA EXCEPTION_INIT`, safe dynamic SQL (`EXECUTE IMMEDIATE` and `DBMS_SQL`),
`DBMS_SCHEDULER` chains, `DBMS_LOCK`, `DBMS_APPLICATION_INFO`, result cache /
`DETERMINISTIC` / `PRAGMA UDF` (measured, not assumed), conditional compilation,
`DBMS_HPROF` profiling, and utPLSQL test suites.

**APEX** — Interactive Grids with PL/SQL save processes, faceted search, wizards,
APEX Collections, Approvals / Unified Task List, Workflow, authorization schemes
down to column level, dynamic actions, `APEX_MAIL`, `APEX_WEB_SERVICE`, REST
Data Sources, Automations, BLOB document handling, session state protection, and
ORDS REST APIs.

---

## The rule that governs both

**Business logic lives in PL/SQL packages. APEX pages call packages.**

An APEX page process that contains business rules is a defect in both projects.
The test for whether you got this right: every rule in the system must be
enforceable — and testable with utPLSQL — with the APEX application switched off
entirely. Security follows the same rule: authorization enforced in the database
(VPD, approval limits, separation of duties), so ORDS and a direct SQL session
cannot bypass what the UI blocks.

---

## The Java / Spring Boot layer

Each project's Java section specifies: the services and how they map to PL/SQL
packages, the Spring modules used and where, transaction ownership, the
error-code contract, Oracle→Java type mapping, the supporting infrastructure
(Redis, RabbitMQ, Oracle AQ, MinIO, Elasticsearch, Prometheus) with **the exact
place each one is used and the places it is deliberately not used**, testing with
Testcontainers, and an interview-question set on the Java/Oracle boundary.

**Spring modules across the two projects:** Spring Boot + Actuator, Web MVC,
Spring JDBC (`JdbcTemplate` / `SimpleJdbcCall` — the primary data path), Spring
Data JPA (only for Java-owned tables), Spring Data Redis + Spring Cache, Spring
Transaction, Spring Security (OAuth2 resource server), Spring Validation, Spring
AMQP, Spring JMS (Oracle AQ), Spring Batch, Spring Retry, Resilience4j,
Micrometer, Flyway, springdoc-openapi, Spring Boot Test + Testcontainers +
WireMock, and optionally Spring Modulith.

### Two rules that hold across both projects

**1. Oracle owns the rules; Spring owns the boundary.** Spring validates input
shape, opens the transaction, calls a package, maps errors to HTTP, and talks to
the outside world. Any Spring class that decides whether an action is *allowed*
has crossed the line. The test: every business rule must still be enforced with
the Java layer switched off entirely.

**2. No package commits.** Transaction boundaries belong to the caller — APEX at
the page process, Spring at `@Transactional`, the scheduler per chunk. The only
exception is the deliberate one: audit and error logging through
`PRAGMA AUTONOMOUS_TRANSACTION`.

### Start as a modular monolith

Both service tables list responsibilities, not deployables. Build one Spring Boot
application with a module per responsibility, and split out only the pieces whose
runtime profile genuinely differs — the batch importer and the queue workers.
