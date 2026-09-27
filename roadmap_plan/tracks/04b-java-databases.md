# Track 4B — Databases from Java (Part 5)

**Goal:** use relational databases, **Oracle** in particular, from Java the
way a middle+ Java engineer does. That means plain JDBC first, then connection
pooling, migrations, calling PL/SQL from Java, JPA/Hibernate, and Oracle
performance tuning seen from the application side. When you finish you
should be able to read a Hibernate SQL log and say *why* each statement was
issued. You should also be able to call a PL/SQL package with REF CURSOR
output and map its `RAISE_APPLICATION_ERROR` codes to typed Java exceptions.

**Required knowledge:**
- Track 4A Parts 1–4 (J1–J4): Java fundamentals, modern Java, concurrency
  basics, Maven/Gradle, JUnit 5/AssertJ/Mockito and **Testcontainers (J4.3)**.
- Track 1C Parts 1–2 (SQL fundamentals, advanced PostgreSQL: transactions,
  isolation, locking, indexes, EXPLAIN).
- Track 1C Part 3 (Oracle SQL + PL/SQL): packages, cursors, exceptions,
  collections, execution plans. This track reuses the **CreditLine** schema
  and the `pkg_schedule` / `pkg_payment` packages you wrote in Modules 3.5–3.9.
- **SQL itself is not re-taught here.** This part covers only how Java talks
  to the database.

**Estimated hours:** ~47 h modules + ~30 h project (JP2 BranchDesk) = **~77 h**.

**Files in Track 4:** [04a-java-core.md](04a-java-core.md) (Parts 1–4, JP1) ·
**04b-java-databases.md** (Part 5, JP2) · [04c-spring.md](04c-spring.md)
(Parts 6–9, JP3 and every later project). Overview: [../00-overview.md](../00-overview.md).

> **Spring comes later.** Everything here uses **plain JDBC and plain
> JPA/Hibernate** (no Spring). The Spring wrappers are taught in 04c,
> Module J7.5: `JdbcTemplate` / `JdbcClient`, `SimpleJdbcCall`, Spring Data
> `@Procedure` and `@Transactional`. They only make sense once you know
> what they wrap.

---

## How to use this file

- Tick `- [ ]` for each lesson you studied, each exercise that meets its
  acceptance criteria and each checklist item you can do or explain without
  notes.
- **No solutions here.** Exercises give a spec and acceptance criteria; you
  write the code. A mentor reviews, gives hints and explains concepts, but
  does not hand over the finished implementation.
- **Where the work goes:** `java/J5-databases/<module-slug>/` in this repo,
  as one Maven (or Gradle) multi-module project, e.g.
  `java/J5-databases/j5-1-jdbc/`. JP2 BranchDesk gets **its own GitHub repo**.
- **Databases:** run both locally in Docker, the same containers as in 1C:
  - PostgreSQL: `postgres:17`
  - Oracle: `gvenzl/oracle-free:23-slim`, service `FREEPDB1`, app user `learn`
  - Integration tests use Testcontainers (`PostgreSQLContainer`,
    `OracleContainer`), never a shared dev database.
- **Python comparisons** are given where they help. You already know
  psycopg and SQLAlchemy, and most concepts here have a direct counterpart.
- Each module ends with self-check interview questions. Answer them out
  loud first, then read the answers below the `---` separator.

---

## Module J5.1 — JDBC Fundamentals (~6h)

**Topics:**
- The JDBC architecture: API vs driver, `java.sql` vs `javax.sql`.
- `DriverManager` vs `DataSource` (and why production code uses `DataSource`).
- `Connection`, `Statement` vs `PreparedStatement`, `ResultSet` (cursor
  movement, typed getters, `wasNull()`), try-with-resources for every JDBC
  resource.
- Transactions: auto-commit (on by default!), `commit()`/`rollback()`,
  savepoints, isolation levels (`setTransactionIsolation`).
- Generated keys; batch updates (`addBatch`/`executeBatch`).
- Bind variables vs string concatenation: SQL injection and plan reuse.
- `SQLException` anatomy: SQLState, vendor error code, chained exceptions.

*Python comparison:* `Connection` ≈ psycopg `connection`, `PreparedStatement`
≈ a parametrized `cursor.execute(sql, params)`. The difference is that JDBC
auto-commits by default, while psycopg opens a transaction implicitly.

### Lessons
- [ ] **J5.1.L1 JDBC overview & connecting.** dev.java / Oracle Java Tutorials "JDBC Basics" trail: "Getting Started", "Processing SQL Statements with JDBC", "Establishing a Connection", "Connecting with DataSource Objects".
- [ ] **J5.1.L2 Statements & result sets.** "JDBC Basics": "Retrieving and Modifying Values from Result Sets", "Using Prepared Statements". Javadoc for `java.sql.ResultSet` (types, concurrency, holdability).
- [ ] **J5.1.L3 Transactions.** "JDBC Basics": "Using Transactions" (auto-commit, savepoints, isolation). Recap 1C Module 2.7 for the isolation anomalies themselves.
- [ ] **J5.1.L4 Batch & generated keys.** Javadoc `Statement.addBatch/executeBatch`, `Statement.RETURN_GENERATED_KEYS`. Baeldung: "Batch Processing in JDBC", "Retrieving Auto-Generated Keys in JDBC" [verify titles].
- [ ] **J5.1.L5 SQL injection.** OWASP Cheat Sheet Series: "SQL Injection Prevention Cheat Sheet" (Defense Option 1: Prepared Statements, Java examples); "Query Parameterization Cheat Sheet".
- [ ] **J5.1.L6 Errors.** "JDBC Basics": "Handling SQLExceptions" (SQLState, error code, `getNextException`, `SQLWarning`).

### Exercises (`java/J5-databases/j5-1-jdbc/`)
- [ ] **Ex J5.1.1 First connection.** Using PostgreSQL in Docker, write a small program that connects via `DriverManager`, prints the server version from `DatabaseMetaData`, and closes everything with try-with-resources. *Acceptance:* running it twice leaves no idle connections (`pg_stat_activity` shows none from your app).
- [ ] **Ex J5.1.2 Typed row mapping.** Create a `products(id, sku, name, price NUMERIC(12,2), discontinued_at TIMESTAMPTZ NULL)` table. Write a `ProductDao` with `findById`, `findAll`, `insert`, `update`, `delete` using only `PreparedStatement`. Map rows to a Java `record Product(...)` with `BigDecimal` price and `Optional`-style handling of the nullable timestamp. *Acceptance:* a JUnit test inserts, reads back and compares records, and a NULL `discontinued_at` round-trips correctly (no `0` or epoch surprises).
- [ ] **Ex J5.1.3 Break it with injection, then fix it.** Add a deliberately vulnerable `findByNameUnsafe(String name)` built by string concatenation. Write a test that proves the injection (e.g. input `x' OR '1'='1` returns every row). Then add the safe version. *Acceptance:* the same malicious input returns zero rows from the safe method; the unsafe method is kept only inside a test-only class with a comment explaining the vulnerability.
- [ ] **Ex J5.1.4 Manual transaction + savepoint.** Implement `transferStock(fromSku, toSku, qty)` over a `stock(sku, qty)` table. It must run with auto-commit off and set a savepoint after the debit. If the credit fails, roll back to the savepoint, log it, then roll back the whole transaction. *Acceptance:* a test that forces the credit to fail (unknown SKU) leaves both rows unchanged. A second test shows what happens if you forget `setAutoCommit(false)`: write the observation down in a comment.
- [ ] **Ex J5.1.5 Batch vs row-by-row.** Insert 50,000 rows once with individual `executeUpdate` calls and once with `addBatch`/`executeBatch` in chunks of 1,000, both inside a single transaction. Also try PostgreSQL's `reWriteBatchedInserts=true`. *Acceptance:* a small results table in `NOTES.md` with timings for the three variants, plus one sentence explaining the difference.
- [ ] **Ex J5.1.6 Error anatomy.** Trigger a unique-constraint violation, a NOT NULL violation and a syntax error. Print SQLState, vendor code and message for each. *Acceptance:* a `SqlErrors.classify(SQLException)` helper returns an enum (`UNIQUE_VIOLATION`, `NOT_NULL_VIOLATION`, `OTHER`) based on SQLState (not message text), with a test for each case.

### Must be able to do / explain
- [ ] Explain why `DataSource` is preferred over `DriverManager` in applications.
- [ ] Close every JDBC resource correctly with try-with-resources (and say what leaks if you don't).
- [ ] Explain the danger of auto-commit mode and control transaction boundaries manually.
- [ ] Explain why bind variables prevent SQL injection **and** help the database reuse plans.
- [ ] Use batch updates and generated keys.
- [ ] Read an `SQLException` (SQLState vs vendor code) and react to specific errors.

**Estimated hours:** ~6 h

### Self-check interview questions
1. What is the difference between `Statement` and `PreparedStatement`? Why should you almost never use `Statement` with user input?
2. JDBC connections are in auto-commit mode by default. What does that mean for a method that runs three UPDATEs?
3. What is a savepoint, and when is it useful?
4. Why must `ResultSet`, `Statement` and `Connection` be closed, and in which order?
5. How does `ResultSet.getInt()` behave for a SQL NULL, and how do you detect it?
6. What is SQLState, and why is it better to branch on it than on the message text?
7. How do batch updates improve performance, and what is the trade-off with error reporting?

---

**Answers**
1. `PreparedStatement` is precompiled with placeholders, and values are sent separately as binds. That makes it immune to SQL injection, lets the database reuse the plan, and handles typing and escaping for you. `Statement` concatenates values into SQL text: it is injectable, and every distinct text is parsed as a new statement.
2. Each statement commits on its own. If the third UPDATE fails, the first two are already committed and the data is inconsistent. You need `setAutoCommit(false)`, then commit or rollback explicitly, with rollback in the failure path.
3. A marker inside a transaction. `rollback(savepoint)` undoes the work after it but keeps the earlier work and the transaction open. It is useful for partial retries, or for "try this optional step, and if it fails continue without it".
4. They hold client and server resources: cursors, memory, sockets, and pooled connections that the pool never gets back. Close them in reverse order of creation (ResultSet → Statement → Connection). Try-with-resources does this automatically.
5. It returns `0`. You call `wasNull()` right after the getter, or use `getObject(col, Integer.class)`, which returns `null`.
6. SQLState is a standardized five-character code whose class, e.g. `23` for integrity constraint violation, is portable. Message text is localized, vendor-specific and can change between driver versions.
7. Many statements travel in one round trip, and some drivers rewrite them into multi-row inserts. The trade-off: if one row fails, `BatchUpdateException` reports per-statement update counts, and you must decide whether the batch commits partially or rolls back as a whole.

---

## Module J5.2 — Connection Pooling with HikariCP (~2h)

**Topics:**
- Why opening a connection is expensive (TCP, TLS, auth, server process or
  session).
- Pool basics: borrow and return, `close()` returns to the pool.
- HikariCP configuration: `maximumPoolSize`, `minimumIdle`,
  `connectionTimeout`, `idleTimeout`, `maxLifetime`, `leakDetectionThreshold`.
- Pool sizing ("fewer connections than you think").
- Pool exhaustion under load and why a larger pool is not the fix.
- Metrics. HikariCP vs PgBouncer, a recap of Track 2 B28.

*Python comparison:* SQLAlchemy's `QueuePool` (`pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`).

### Lessons
- [ ] **J5.2.L1 HikariCP README.** github.com/brettwooldridge/HikariCP: "Configuration (knobs, baby!)" → essentials and frequently used settings.
- [ ] **J5.2.L2 Pool sizing.** HikariCP wiki: "About Pool Sizing" (the Oracle Real-World Performance video reference, the `connections = ((core_count * 2) + effective_spindle_count)` starting point).
- [ ] **J5.2.L3 Pitfalls.** HikariCP wiki: "Down the Rabbit Hole" (skim) and the `leakDetectionThreshold` docs. Vlad Mihalcea blog: "The best way to determine the optimal connection pool size" [verify title].

### Exercises (`java/J5-databases/j5-2-hikari/`)
- [ ] **Ex J5.2.1 Swap to a pool.** Make the J5.1 DAO depend on a `DataSource` and wire a `HikariDataSource`. *Acceptance:* the J5.1 tests pass unchanged, and the pool logs its configuration at startup.
- [ ] **Ex J5.2.2 Starve the pool.** Configure `maximumPoolSize=2`, `connectionTimeout=1000`. Start 10 threads (or virtual threads) that each hold a connection for 500 ms. *Acceptance:* you observe and log `SQLTransientConnectionException`, and in `NOTES.md` you explain why raising the pool to 100 is the wrong fix.
- [ ] **Ex J5.2.3 Catch a leak.** Write code that "forgets" to close a connection. Enable `leakDetectionThreshold=2000`. *Acceptance:* Hikari logs the leak with the stack trace of the borrowing code, and you fix the leak.

### Must be able to do / explain
- [ ] Configure HikariCP and explain each of the six main settings.
- [ ] Explain why pool size should be small and bounded.
- [ ] Diagnose pool exhaustion vs a connection leak.

**Estimated hours:** ~2 h

### Self-check interview questions
1. What does `connection.close()` do when the connection comes from a pool?
2. Why can a pool with 200 connections make a database *slower* than one with 20?
3. What is `maxLifetime` for, and how should it relate to database or firewall timeouts?
4. What symptoms tell you that you have a connection leak?
5. You have 5 app instances, each with pool size 20. What does the database see, and why does it matter?

---

**Answers**
1. It returns the connection to the pool; the physical connection stays open. The pool also resets state such as auto-commit and read-only if it was changed.
2. The database has a limited number of CPU cores and disks. Beyond a point, extra active sessions cause context switching, lock contention and cache thrashing, so throughput drops and latency grows. Requests should wait in the app's queue instead of inside the database.
3. It retires connections before the database, a proxy or a firewall silently kills them. Set it a bit shorter (e.g. 30 s shorter) than any infrastructure idle or lifetime limit.
4. The number of active connections grows and never returns to idle. You see `Connection is not available, request timed out`, and the pool's active count equals its max while the app is idle. Leak detection logs name the borrowing stack trace.
5. Up to 100 connections. The total across all instances (plus batch jobs and admin tools) must fit the database's `processes`/`sessions` or `max_connections`, and each Oracle dedicated-server session costs memory.

---

## Module J5.3 — Oracle from Java: Drivers, UCP, Types, Testcontainers (~5h)

**Topics:**
- The Oracle JDBC driver: `ojdbc11` (Java 11+) vs `ojdbc17` (Java 17+),
  Maven coordinates `com.oracle.database.jdbc`, the thin driver.
- Connection URLs: EZConnect `jdbc:oracle:thin:@//host:1521/FREEPDB1`,
  service name vs SID.
- `OracleDataSource`. Universal Connection Pool (UCP) vs HikariCP.
- Oracle Database Free in Docker (`gvenzl/oracle-free`) and Testcontainers
  `OracleContainer` (startup time, container reuse, init scripts).
- Type mapping:
  - `NUMBER(p,s)` → `BigDecimal` / `long` / `int`; the danger of
    `double` for money.
  - `VARCHAR2` / `NVARCHAR2`, and the empty string being NULL in Oracle.
  - `DATE`, which includes time, → `LocalDateTime`.
  - `TIMESTAMP` → `LocalDateTime`; `TIMESTAMP WITH TIME ZONE` →
    `OffsetDateTime`; `TIMESTAMP WITH LOCAL TIME ZONE`.
  - `CLOB`/`BLOB` via streams; `BOOLEAN` in 23ai; `RAW`.
- Sequences vs identity columns, and retrieving generated keys from Oracle
  (`prepareStatement(sql, new String[]{"ID"})`).

### Lessons
- [ ] **J5.3.L1 Driver & connecting.** Oracle *JDBC Developer's Guide* (23ai): "Introducing JDBC", "Getting Started" and "Data Sources and URLs" (EZConnect, thin driver). The Maven Central page for `com.oracle.database.jdbc:ojdbc17` (the version matrix).
- [ ] **J5.3.L2 UCP.** Oracle *Universal Connection Pool Developer's Guide* (23ai): "Introduction to UCP" and "Getting Database Connections in UCP". Write a short note on when UCP's Oracle-specific features matter (FAN, Application Continuity, RAC load balancing) and why HikariCP is fine for a single instance.
- [ ] **J5.3.L3 Type mapping.** *JDBC Developer's Guide*: "Accessing and Manipulating Oracle Data" (data type mappings) and "Working with LOBs and BFILEs". Java `java.time` ↔ JDBC 4.2 `getObject(col, LocalDateTime.class)`.
- [ ] **J5.3.L4 Dates & time zones.** *JDBC Developer's Guide*: the datetime section (DATE vs TIMESTAMP, session time zone). Recap Oracle datetime types from 1C Module 3.1.
- [ ] **J5.3.L5 Testcontainers Oracle.** testcontainers.com → Modules → "Oracle Database Free" (`org.testcontainers:oracle-free`), plus the `gvenzl/oracle-free` README (the `-faststart` images and `APP_USER`).
- [ ] **J5.3.L6 Keys.** *JDBC Developer's Guide*: "Retrieval of Auto-Generated Keys". *SQL Language Reference*: `CREATE SEQUENCE` and the identity_clause of `CREATE TABLE`.

### Exercises (`java/J5-databases/j5-3-oracle/`)
- [ ] **Ex J5.3.1 Port the DAO to Oracle.** Run the J5.1 `ProductDao` against Oracle (`learn@FREEPDB1`) with the Oracle driver. Adapt the DDL: `NUMBER(12,2)`, `VARCHAR2`, `TIMESTAMP WITH TIME ZONE`, identity PK. *Acceptance:* the same tests pass against both PostgreSQL and Oracle, using JUnit parameterization or two test classes that share an abstract base.
- [ ] **Ex J5.3.2 Type round-trip matrix.** Create an Oracle table with one column each of `NUMBER(18,0)`, `NUMBER(14,2)`, `BINARY_DOUBLE`, `VARCHAR2(100)`, `DATE`, `TIMESTAMP`, `TIMESTAMP WITH TIME ZONE`, `CLOB`, `BLOB`. Write and read each through JDBC with the Java type you think is correct. *Acceptance:* a test per column proves exact round-trip, including `DATE` keeping its time part and the `''`→NULL behaviour of `VARCHAR2`. A `NOTES.md` table lists the SQL type, Java type and any gotcha.
- [ ] **Ex J5.3.3 Money precision trap.** Store `0.1 + 0.2` computed in `double` and in `BigDecimal` into a `NUMBER(14,2)` column and sum 10,000 such rows. *Acceptance:* a test shows the `double` path drifting and the `BigDecimal` path being exact; one paragraph explains why.
- [ ] **Ex J5.3.4 Testcontainers OracleContainer.** Replace the "Oracle must be running locally" requirement with `OracleContainer` (`gvenzl/oracle-free:23-slim-faststart`) plus an init script. *Acceptance:* `mvn verify` on a clean machine with only Docker runs the Oracle tests. Startup time is measured, and container reuse is tried and documented.
- [ ] **Ex J5.3.5 Sequence vs identity.** Insert rows into one table with an identity PK and one with a sequence plus a `DEFAULT seq.NEXTVAL` column, retrieving the generated key in Java both times. *Acceptance:* both keys come back in the same round trip; you note what `RETURNING … INTO` would give you in PL/SQL, compared with JDBC generated keys.

### Must be able to do / explain
- [ ] Connect to Oracle with the thin driver using EZConnect and a service name.
- [ ] Choose the right Java type for every common Oracle type (and explain `DATE` ≠ date-only).
- [ ] Explain why `NUMBER` money must map to `BigDecimal`.
- [ ] Run Oracle integration tests with Testcontainers.
- [ ] Explain the difference between UCP and HikariCP, and when UCP matters.

**Estimated hours:** ~5 h

### Self-check interview questions
1. What is the difference between an Oracle SID and a service name, and which does EZConnect use?
2. Which Java type should an Oracle `DATE` column map to, and why is `LocalDate` often wrong?
3. What happens when you insert an empty Java string into a `VARCHAR2` column?
4. Why is `double` unacceptable for monetary `NUMBER` columns?
5. How do you get the generated identity value back after an INSERT in Oracle via JDBC?
6. When would you choose UCP over HikariCP?
7. What makes Oracle containers slow in tests, and how can you mitigate it?

---

**Answers**
1. The SID identifies an instance. A service name is a logical name for a database or PDB, and several services can map to one PDB. EZConnect uses `//host:port/service_name` (e.g. `FREEPDB1`), which is the modern default and works with PDBs.
2. `LocalDateTime`, because Oracle `DATE` stores date **and** time to the second. Mapping to `LocalDate` silently drops the time, so comparisons and round-trips break.
3. Oracle treats `''` as NULL. You get NULL stored (and a NOT NULL constraint will fail), so code that relies on "empty but not null" behaves differently than on PostgreSQL.
4. Binary floating point cannot represent most decimal fractions exactly, so sums drift and rounding differs. `BigDecimal` holds exact decimal values and matches `NUMBER(p,s)` semantics.
5. Call `prepareStatement(sql, new String[]{"ID_COLUMN"})`, execute, then read `getGeneratedKeys()`. Oracle needs the column names; otherwise it returns the ROWID.
6. When you need Oracle-specific HA and scalability features: RAC runtime load balancing, Fast Application Notification (FAN) for fast failover, Application Continuity/Transaction Guard, or Oracle-recommended Data Guard setups. For a single instance, HikariCP is simpler and fine.
7. Oracle images are large, and database creation or startup takes tens of seconds. Mitigations: `-faststart` images, one shared container per test run (a static or singleton container), Testcontainers reuse locally, and truncating tables instead of recreating the schema.

---

## Module J5.4 — Schema Migrations: Flyway & Liquibase (~4h)

**Topics:**
- Why migrations are code: versioning, repeatability, no manual DDL in prod.
- Flyway:
  - versioned `V1__init.sql` and repeatable `R__pkg_payment.sql`
    migrations (re-applied when their checksum changes, which is ideal for
    PL/SQL packages and views);
  - the `flyway_schema_history` table, `validate`, `baseline`, `repair`,
    `clean` (disabled in prod!);
  - placeholders; the Java API vs the Maven plugin;
  - Oracle specifics: `/` delimiters for PL/SQL blocks; DDL auto-commits,
    so a migration that fails halfway is not rolled back.
- Liquibase: changelogs (XML/YAML/SQL), changesets, `runOnChange`,
  contexts/labels, rollback blocks.
- Flyway vs Liquibase: when to pick which.
- Expand/contract migrations, a recap of Track 2 B23.

*Python comparison:* Alembic revisions ≈ Flyway versioned migrations. There is no direct Alembic equivalent of repeatable migrations.

### Lessons
- [ ] **J5.4.L1 Flyway concepts.** documentation.red-gate.com → Flyway → Concepts → "Migrations" (versioned, undo, repeatable; naming; checksums) and "Schema history table".
- [ ] **J5.4.L2 Flyway usage.** Flyway docs: "Getting started" → the Maven or Java API quickstart; Commands: `migrate`, `info`, `validate`, `baseline`, `repair`, `clean` (and `cleanDisabled`).
- [ ] **J5.4.L3 Flyway + Oracle.** Flyway docs → Supported databases → "Oracle" (PL/SQL delimiters, SQL*Plus commands support).
- [ ] **J5.4.L4 Liquibase.** docs.liquibase.com: "Liquibase Concepts" → Changelog, Changeset, Changeset attributes (`runOnChange`, `runAlways`), "Rollback", "Contexts" and "Labels".
- [ ] **J5.4.L5 Choosing.** Baeldung: "Liquibase vs Flyway" [verify title]. Write a half-page decision note in your own words.

### Exercises (`java/J5-databases/j5-4-migrations/`)
- [ ] **Ex J5.4.1 Flyway on PostgreSQL.** Move the J5.1 DDL into `V1__create_products.sql` and add `V2__add_category.sql`. Run it via the Java API at app start and via the Maven plugin. *Acceptance:* `flyway info` shows both migrations applied; editing V1 afterwards makes `validate` fail, and you write down why that is a feature.
- [ ] **Ex J5.4.2 Flyway on Oracle with a repeatable package.** Create the CreditLine `loan_products` table in `V1__…` and put a small PL/SQL package (e.g. your 1C `pkg_schedule` spec + body) into `R__pkg_schedule.sql`. *Acceptance:* changing the package body and re-running re-applies only the R__ migration; a broken package body makes the migration fail with a clear error (check `USER_ERRORS` in the migration or in a test).
- [ ] **Ex J5.4.3 Migrations in tests.** Run Flyway against the Testcontainers Oracle database before the tests. *Acceptance:* tests start from an empty container, migrate and pass; no test uses hand-written DDL.
- [ ] **Ex J5.4.4 Same change in Liquibase.** Re-express Ex J5.4.1 as a Liquibase YAML (or SQL-formatted) changelog with a rollback block for V2. *Acceptance:* `update` then `rollback-count 1` returns the schema to V1; a short `NOTES.md` comparison lists what you liked and disliked about each tool.
- [ ] **Ex J5.4.5 Failed migration on Oracle.** Write a migration with two DDL statements where the second fails. *Acceptance:* you observe that the first DDL stayed applied (Oracle DDL auto-commits), recover with a fix and `repair`, and write down the rule "one DDL per migration or idempotent DDL on Oracle".

### Must be able to do / explain
- [ ] Set up Flyway with versioned and repeatable migrations, from both the Java API and Maven.
- [ ] Explain the schema history table, checksums, and why applied migrations must never be edited.
- [ ] Manage PL/SQL packages as repeatable migrations on Oracle.
- [ ] Explain why a failing Oracle migration is not atomic, and how to design for it.
- [ ] Compare Flyway and Liquibase and justify a choice.

**Estimated hours:** ~4 h

### Self-check interview questions
1. What is the difference between a versioned and a repeatable migration in Flyway?
2. What happens if someone edits an already-applied versioned migration?
3. Why are PL/SQL packages a good fit for repeatable migrations?
4. Why is a failed multi-statement migration more dangerous on Oracle than on PostgreSQL?
5. What does `baseline` do, and when do you need it?
6. Name two situations where Liquibase fits better than Flyway.

---

**Answers**
1. A versioned migration (`V<version>__desc.sql`) runs exactly once, in version order. A repeatable one (`R__desc.sql`) has no version and runs again whenever its checksum changes, after all pending versioned migrations.
2. Its checksum no longer matches `flyway_schema_history`, so `validate`/`migrate` fails. That protects every environment from drifting apart. The fix is a new migration, or `repair` only when you consciously accept the change.
3. They are defined with `CREATE OR REPLACE`, which is idempotent, and their source is the thing you edit over time. A repeatable migration keeps one file per package in version control and re-applies it on change, like deploying code.
4. PostgreSQL supports transactional DDL, so the whole migration rolls back. On Oracle each DDL commits implicitly, so a failure leaves the schema half-migrated and the history table records a failure you must repair manually.
5. It marks an existing, non-empty database as already at a given version, so Flyway only applies later migrations. You need it when introducing Flyway to a legacy schema.
6. When you need database-agnostic changelogs (XML/YAML generating vendor SQL), built-in rollback definitions, contexts/labels to run changes per environment, or diff/generate-changelog tooling against an existing database.

---

## Project JP2 — BranchDesk · Junior (~30h)

### Goal
Build a small **branch-banking back-office application on Oracle** using
**only plain JDBC** (no ORM, no Spring). It manages customers and their
accounts, and records deposits, withdrawals and transfers so that balances
can never go wrong. It must hold even with concurrent transfers. The point of
the project is correct transaction handling, locking and type mapping at the
JDBC level. You will later appreciate what JPA and Spring do for you, and
what they hide.

The interface is a **command-line app** (a picocli-free simple menu or
argument parser you write yourself with J1 knowledge), plus a set of
integration tests. There is no HTTP layer.

### Features
- [ ] Customers: create, find by id / tax id, list with paging (`OFFSET … FETCH NEXT … ROWS ONLY`), update contact data, soft-close.
- [ ] Accounts: open an account for a customer (currency `UZS`/`USD`, `NUMBER(18,2)` balance, status OPEN/FROZEN/CLOSED), list accounts of a customer, freeze or close an account (closing only with zero balance).
- [ ] Deposits and withdrawals: a withdrawal never makes the balance negative; frozen and closed accounts reject all movements.
- [ ] Transfers between two accounts (same currency) in **one transaction**: both rows locked with `SELECT … FOR UPDATE` **in a fixed order (lower account id first)** to avoid deadlocks; the debit, the credit and two `account_movements` rows are all-or-nothing.
- [ ] Every movement writes an `account_movements` row (`movement_id` identity, `account_id`, `type` DEPOSIT/WITHDRAWAL/TRANSFER_IN/TRANSFER_OUT, `amount`, `balance_after`, `transfer_ref`, `created_at TIMESTAMP WITH TIME ZONE`).
- [ ] Audit table `audit_log(audit_id, entity, entity_id, action, details CLOB, performed_by, performed_at)` written in the **same transaction** as the change.
- [ ] Idempotent transfers: a client-supplied `transfer_ref` is UNIQUE, so retrying the same transfer returns the original result instead of moving money twice.
- [ ] Reports (SQL from 1C Part 3):
  - account statement for a date range, with a running balance computed by an **analytic function** (`SUM(...) OVER (ORDER BY ...)`);
  - total balances per currency per branch using `ROLLUP`;
  - the top 10 customers by total balance.
- [ ] Error handling: Oracle errors are translated into domain exceptions: `InsufficientFundsException`, `AccountFrozenException`, `DuplicateTransferException` (ORA-00001 on `transfer_ref`), `CustomerNotFoundException`.

### Tech stack
| Tool / technique | Taught in |
|---|---|
| Java 25, records, enums, exceptions, collections | 4A Part 1–2 (J1–J2) |
| Concurrency test harness (ExecutorService / virtual threads, CountDownLatch) | 4A Part 3 (J3) |
| Maven (multi-module optional), JUnit 5, AssertJ | 4A Part 4 (J4.1, J4.2) |
| Testcontainers + `OracleContainer` | J4.3, J5.3 |
| SLF4J + Logback | J4.4 |
| JDBC: `PreparedStatement`, transactions, savepoints, batch, generated keys | J5.1 |
| HikariCP | J5.2 |
| Oracle thin driver `ojdbc17`, type mapping (`BigDecimal`, `OffsetDateTime`, CLOB) | J5.3 |
| Flyway (versioned migrations on Oracle) | J5.4 |
| Oracle SQL: identity columns, constraints, `FOR UPDATE`, analytic functions, `ROLLUP`, paging | 1C Part 3 (3.1, 3.2) and 1C 2.8 (locking concepts) |

### Required knowledge
- Track 4A: J1 (all), J2 (records, lambdas and streams for small in-memory transforms), J3.1–J3.3 (threads, executors, synchronizers for the concurrency test), J4.1–J4.4.
- Track 4B: J5.1–J5.4.
- Track 1C: 1.6 (constraints), 2.7–2.8 (transactions, isolation, row locks, deadlocks), 3.1–3.2 (Oracle SQL, analytic functions, ROLLUP).

### Milestones
**M1 — Schema & skeleton** (`v0.1-schema`)
- [ ] Maven project with `ojdbc17`, HikariCP, Flyway, SLF4J/Logback, JUnit 5, AssertJ, Testcontainers.
- [ ] Flyway `V1__customers_accounts.sql`, `V2__movements_audit.sql` with PKs (identity), FKs, `CHECK (balance >= 0)`, `CHECK (status IN (...))`, UNIQUE on `tax_id` and `transfer_ref`.
- [ ] `Db` bootstrap: builds a `HikariDataSource` from a properties file or env variables and runs Flyway at startup.
- [ ] One green Testcontainers test that migrates an empty Oracle container.

**M2 — Customers & accounts CRUD** (`v0.2-crud`)
- [ ] `CustomerRepository` and `AccountRepository` using `PreparedStatement` only, with row mappers to records.
- [ ] Paging for customer lists; soft-close for customers; close-account rule (zero balance only).
- [ ] CLI commands: `customer add|find|list`, `account open|list|freeze|close`.
- [ ] Integration tests for every repository method, including NULL handling and `''`→NULL behaviour.

**M3 — Money movements & transactions** (`v0.3-money`)
- [ ] `MoneyService.deposit/withdraw/transfer` with explicit transaction boundaries (auto-commit off, commit/rollback in `finally`-safe structure).
- [ ] Transfers lock both accounts via `SELECT … FOR UPDATE` in ascending id order.
- [ ] Movement rows with `balance_after`; the audit row in the same transaction.
- [ ] Idempotent `transfer_ref` handling (ORA-00001 → return the existing transfer).
- [ ] Error translation from `SQLException` (error codes) to domain exceptions.

**M4 — Concurrency proof** (`v0.4-concurrency`)
- [ ] A test that runs 1,000 random concurrent transfers between 10 accounts (e.g. 50 virtual threads). It asserts that the total money is unchanged, no balance is negative, and movement rows reconcile with balances.
- [ ] A test that deliberately reverses the lock order (in a test-only variant), reproduces an `ORA-00060` deadlock, and documents it in `docs/deadlocks.md` with a fix explanation.

**M5 — Reports & polish** (`v1.0-branchdesk`)
- [ ] Statement report with analytic running balance; ROLLUP totals per branch/currency; top-10 customers.
- [ ] The report queries are bound with parameters (date range, account id); none are built by concatenation.
- [ ] `README.md`: how to run (Docker + `mvn verify`), the schema diagram, the design decisions (why lock order, why `BigDecimal`, why audit in the same transaction).

### Definition of done
- [ ] `mvn verify` passes on a clean machine with only Docker and a JDK installed (Oracle comes from Testcontainers).
- [ ] No string-concatenated SQL anywhere with user input (checked by grep in review).
- [ ] Every JDBC resource is closed via try-with-resources; the leak detection threshold is enabled in tests and logs no leaks.
- [ ] Money is `BigDecimal` end to end; no `double`/`float` in the domain.
- [ ] The concurrency test passes 10 runs in a row.
- [ ] Flyway owns the whole schema; there are no manual DDL steps in the README.
- [ ] `docs/deadlocks.md` and the design-decisions section are written.

### Estimated hours
~30 h (M1 5 h · M2 7 h · M3 8 h · M4 5 h · M5 5 h)

### Interview questions about this project
1. How do you guarantee that a transfer never leaves the two balances inconsistent?
2. Why do you lock the two accounts in ascending id order, and what happens if you don't?
3. How did you make transfers idempotent, and why is a UNIQUE constraint better than checking first in Java?
4. Why did you use `BigDecimal` and `NUMBER(18,2)`? What would go wrong with `double`?
5. How did you test concurrency, and what exactly do your assertions prove?

---

**Answers**
1. Everything happens in one database transaction with auto-commit off: lock both rows, validate, debit, credit, insert movement and audit rows, then commit. Any exception triggers rollback. The `CHECK (balance >= 0)` constraint is a last line of defence even if the Java check has a bug.
2. Two opposite transfers (A→B and B→A) running concurrently could each lock one row and wait for the other, which is a deadlock. Oracle detects it and raises ORA-00060 in one session. A global lock order means both transactions request locks in the same sequence, so a cycle can't form.
3. The client sends a `transfer_ref`, and the column has a UNIQUE constraint. A retry fails with ORA-00001, which I translate into "return the existing transfer". A check-then-insert in Java has a race window: two requests can both see "not exists" and both insert. The constraint is enforced atomically by the database.
4. Money needs exact decimal arithmetic, and `NUMBER(18,2)` stores exact decimals. `double` is binary floating point: 0.1 + 0.2 ≠ 0.3, sums drift, and rounding at the cent level becomes inconsistent. That is unacceptable in banking.
5. Many virtual threads run random transfers between a small set of accounts to force contention. Afterwards the test asserts four invariants:
   - the total of all balances is unchanged (conservation of money);
   - no balance is negative;
   - each account's balance equals its opening balance plus the sum of its movements;
   - no duplicate `transfer_ref`s exist.

   Together these prove atomicity and isolation under real concurrency, not just the happy path.

---

## Module J5.5 — Calling PL/SQL from Java (~7h)

**Topics:**
- `CallableStatement` and the JDBC escape syntax `{call pkg.proc(?, ?)}`
  vs an anonymous block `BEGIN pkg.proc(:1, :2); END;`.
- IN, OUT and IN OUT parameters; `registerOutParameter` with `java.sql.Types`
  and `oracle.jdbc.OracleTypes`.
- Calling functions (`{? = call pkg.fn(?)}`).
- **REF CURSOR** outputs (`OracleTypes.CURSOR` → `ResultSet`).
- Calling package procedures and overloaded procedures (named notation in
  anonymous blocks).
- Mapping `RAISE_APPLICATION_ERROR(-20xxx, …)` codes to typed Java
  exceptions: `SQLException.getErrorCode()` returns `20xxx`.
- Passing collections:
  - SQL object and collection types (`CREATE TYPE … AS TABLE OF …`) with
    `OracleConnection.createOracleArray`, and `Struct`;
  - the pragmatic alternative: a JSON string param expanded with
    `JSON_TABLE` inside PL/SQL.
- Transaction rules: no `COMMIT` inside packages when Java owns the
  transaction; autonomous transactions are for audit or error logs only.
- Session context for auditing and VPD: `DBMS_SESSION.SET_IDENTIFIER`,
  `DBMS_APPLICATION_INFO.SET_MODULE/SET_ACTION`,
  `OracleConnection.setClientInfo` / end-to-end metrics. Reset them when the
  connection returns to a pool.

### Lessons
- [ ] **J5.5.L1 CallableStatement basics.** Oracle Java Tutorials "JDBC Basics" → "Using Stored Procedures". Javadoc `java.sql.CallableStatement`.
- [ ] **J5.5.L2 Oracle specifics.** Oracle *JDBC Developer's Guide* (23ai): "Oracle Extensions" (`OracleTypes`, `OracleCallableStatement`) and the section on calling PL/SQL stored procedures and REF CURSORs ("Using PL/SQL" / "REF CURSOR Support" [verify exact section names]).
- [ ] **J5.5.L3 Collections & objects.** *JDBC Developer's Guide*: "Working with Oracle Collections" (`createOracleArray`) and "Working with Oracle Object Types" (`Struct`, `SQLData`). *PL/SQL Language Reference*: "PL/SQL Collections and Records" (schema-level vs package-level types: only schema-level are visible to JDBC before 18c/23ai improvements [verify]).
- [ ] **J5.5.L4 JSON alternative.** *SQL Language Reference*: `JSON_TABLE`. *JSON Developer's Guide*: "SQL/JSON Function JSON_TABLE".
- [ ] **J5.5.L5 Errors & codes.** *PL/SQL Language Reference*: "PL/SQL Error Handling" → "Raising Exceptions Explicitly" (`RAISE_APPLICATION_ERROR`, the range −20000..−20999).
- [ ] **J5.5.L6 Session context.** *PL/SQL Packages and Types Reference*: `DBMS_SESSION.SET_IDENTIFIER`, `DBMS_APPLICATION_INFO`. *JDBC Developer's Guide*: "End-to-End Tracing" / `setClientInfo` [verify section name].
- [ ] **J5.5.L7 Recap your PL/SQL.** Re-read your own 1C solutions for `pkg_schedule` (T3.5.2) and `pkg_payment.post_payment` (T3.5.3) plus their error codes: you will call them from Java now.

### Exercises (`java/J5-databases/j5-5-plsql/`) — all on the CreditLine schema from 1C Part 3
- [ ] **Ex J5.5.1 Call a function.** Call a scalar function from your 1C packages (e.g. a function returning the outstanding principal of a loan) through `{? = call …}`. *Acceptance:* the result maps to `BigDecimal`, and a NULL result (unknown loan) is handled explicitly.
- [ ] **Ex J5.5.2 IN/OUT procedure.** Call `pkg_payment.post_payment` with IN parameters (loan id, amount, value date) and OUT parameters (e.g. the new transaction id and the allocation summary). *Acceptance:* a Testcontainers test (schema + packages migrated by Flyway R__ files) posts a payment, reads the OUT values, and verifies the rows written by the package.
- [ ] **Ex J5.5.3 REF CURSOR.** Write (or reuse) a package procedure returning the active schedule of a loan as a `SYS_REFCURSOR` OUT parameter. Map it to `List<ScheduleLine>` records in Java. *Acceptance:* the list size equals the loan term; the cursor and statement are closed; a test for a loan without an active schedule returns an empty list, not an exception.
- [ ] **Ex J5.5.4 Error-code translation.** Your packages raise codes such as `-20007` (PERIOD_CLOSED) and others you defined. Build an `OracleErrorTranslator` that maps `getErrorCode()` values to typed exceptions (`PeriodClosedException`, `InvalidAmountException`, …) and falls back to a generic `DataAccessError`. *Acceptance:* one test per mapped code that triggers the real package error (not a mock).
- [ ] **Ex J5.5.5 Passing a collection, two ways.** Implement "post several payments at once" twice:
  - (a) a schema-level SQL type `payment_t` + `payment_tab`, passed via `createOracleArray` of `Struct`s;
  - (b) a JSON array string, expanded with `JSON_TABLE` inside the procedure.

  *Acceptance:* both produce identical results. `NOTES.md` compares them on code complexity, type safety, performance for 1,000 items, and portability.
- [ ] **Ex J5.5.6 Who did it?** Before each business call, set `DBMS_SESSION.SET_IDENTIFIER(<app user>)` and `DBMS_APPLICATION_INFO.SET_MODULE('branchdesk', '<action>')`, and clear them when done. Make your 1C audit trigger/package record `SYS_CONTEXT('USERENV','CLIENT_IDENTIFIER')`. *Acceptance:* audit rows show the application user, not the pooled DB user. A test proves that a connection borrowed afterwards does **not** inherit the previous identifier.

### Must be able to do / explain
- [ ] Call procedures and functions with IN, OUT and IN OUT parameters.
- [ ] Consume a REF CURSOR and map it to records, closing everything properly.
- [ ] Translate application error codes (−20000..−20999) into typed Java exceptions.
- [ ] Pass collections to PL/SQL (SQL object types or JSON), and explain the trade-offs.
- [ ] Explain who owns the transaction when Java calls PL/SQL, and why packages shouldn't `COMMIT`.
- [ ] Propagate the end-user identity to the database through a pooled connection and clean it up.

**Estimated hours:** ~7 h

### Self-check interview questions
1. How do you call a PL/SQL procedure with an OUT parameter from JDBC?
2. What is a REF CURSOR, and how do you read it in Java?
3. Your procedure raises `RAISE_APPLICATION_ERROR(-20007, 'Period closed')`. What does Java receive, and how do you turn it into an HTTP 409 later?
4. Why is `COMMIT` inside a PL/SQL package a problem when called from a Java service?
5. What are two ways to pass a list of objects to a PL/SQL procedure, and their trade-offs?
6. All connections in the pool log in as the same database user. How can an audit trigger still know which application user made the change?
7. Why must you reset session context (client identifier, module) before returning a connection to the pool?

---

**Answers**
1. Prepare `{call pkg.proc(?, ?)}` (or an anonymous block) with `prepareCall`, set the IN values, `registerOutParameter(index, Types.X)` for each OUT, then `execute()` and read OUT values with the getters (`getBigDecimal(index)`, …).
2. A pointer to an open query result that PL/SQL returns to the caller. You register the OUT parameter as `OracleTypes.CURSOR`, execute, then `getObject(index, ResultSet.class)` (or cast), iterate it like a normal `ResultSet` and close it.
3. An `SQLException` with `getErrorCode() == 20007` and message `ORA-20007: Period closed…`. A translator maps 20007 to `PeriodClosedException`, and the web layer (in Spring later, `@ControllerAdvice`) maps that to `409 Conflict` with a ProblemDetail body.
4. It commits the caller's whole transaction, including work done before the call, and breaks atomicity. Java can no longer roll back on a later failure. The rule: the caller owns the transaction; packages don't commit (except in autonomous transactions for logging).
5. (a) SQL object/collection types via `createOracleArray` and `Struct`: type-safe and efficient, but you need schema-level types, more boilerplate and Oracle-specific code. (b) A JSON string plus `JSON_TABLE`: simple and portable in Java, and easy to evolve, but you pay parsing cost, lose compile-time types, and must validate inside PL/SQL.
6. Set a session-level identifier on the borrowed connection (`DBMS_SESSION.SET_IDENTIFIER`, or client info / end-to-end metrics). The trigger reads `SYS_CONTEXT('USERENV','CLIENT_IDENTIFIER')`. VPD policies can use the same context.
7. Pooled connections are reused by other requests. Without a reset, the next user's actions would be attributed to the previous user, which corrupts the audit trail and can bypass VPD rules.

---

## Module J5.6 — JPA & Hibernate I: Entities, Relationships, Fetching (~8h)

**Topics:**
- JPA as a specification (Jakarta Persistence 3.2) vs Hibernate ORM 6/7 as
  its implementation.
- Setup without Spring: `persistence.xml`, `EntityManagerFactory`,
  `EntityManager`.
- `@Entity`, `@Table`, `@Id`. Generators: `IDENTITY` vs `SEQUENCE`
  (preferred on Oracle; `@SequenceGenerator` with `allocationSize` and the
  pooled optimizer) vs `UUID`.
- Basic mappings: `@Column`, enums (`EnumType.STRING`), `java.time`,
  `BigDecimal` with precision and scale, `@Embeddable` value objects.
- Relationships: `@ManyToOne`, `@OneToMany(mappedBy)`, `@OneToOne`,
  `@ManyToMany` (and why a join entity is often better); owning side vs
  inverse side.
- Fetch types: the default EAGER on `@ManyToOne` and why to make it LAZY;
  `LazyInitializationException`.
- The **N+1 problem**: detect it (SQL logging, Hibernate statistics, a
  query-count assertion), fix it (`JOIN FETCH`, `@EntityGraph`/entity
  graphs, `@BatchSize` / `hibernate.default_batch_fetch_size`).
- `equals`/`hashCode` for entities.

*Python comparison:* SQLAlchemy `relationship(lazy="select")` ≈ LAZY; `selectinload`/`joinedload` ≈ batch fetching / `JOIN FETCH`. You met N+1 in Track 2 B5/B10.

### Lessons
- [ ] **J5.6.L1 Getting started.** Hibernate ORM User Guide (6.x/7.x) → "Introduction to Hibernate" / "Getting Started Guide" → bootstrap with `persistence.xml` (the "Obtaining an EntityManagerFactory" section).
- [ ] **J5.6.L2 Domain model mapping.** Hibernate User Guide → "Domain Model": Basic types (incl. `java.time`, `BigDecimal`), Embeddable types, Entity types, Identifiers → "Generated identifier values" (sequence, identity, pooled optimizers).
- [ ] **J5.6.L3 Associations.** Hibernate User Guide → "Associations" (`@ManyToOne`, `@OneToMany`, `@OneToOne`, `@ManyToMany`, bidirectional helpers). Jakarta Persistence 3.2 spec §2.9 "Entity Relationships" [verify section number].
- [ ] **J5.6.L4 Fetching.** Hibernate User Guide → "Fetching" (FetchType, fetch profiles, entity graphs, `@BatchSize`).
- [ ] **J5.6.L5 Performance classics.** Vlad Mihalcea: *High-Performance Java Persistence*, Part 2 "JPA and Hibernate": the chapters on identifiers, relationships and fetching. Blog posts: "The best way to map a @OneToMany relationship with JPA and Hibernate", "N+1 query problem with JPA and Hibernate", "How to implement equals and hashCode using the JPA entity identifier" [verify titles].
- [ ] **J5.6.L6 Sequences on Oracle.** Vlad Mihalcea blog: "Hibernate pooled and pooled-lo identifier generators" and "Why you should never use the TABLE identifier generator" [verify titles].

### Exercises (`java/J5-databases/j5-6-jpa/`)
- [ ] **Ex J5.6.1 Bootstrap Hibernate on Oracle.** Map `LoanProduct`, `Customer` and `Loan` (CreditLine schema) as entities in a plain-Java project with `persistence.xml`. The schema is still created by Flyway, and Hibernate runs with `hbm2ddl=validate`. *Acceptance:* validation passes against the migrated Testcontainers Oracle database; a test persists and reloads one `Loan`.
- [ ] **Ex J5.6.2 Sequence tuning.** Use `@SequenceGenerator` with `allocationSize=50` matching `INCREMENT BY 50` on the Oracle sequence. Insert 1,000 loans. *Acceptance:* SQL logging shows ~20 sequence calls instead of 1,000; `NOTES.md` explains what goes wrong when `allocationSize` and `INCREMENT BY` disagree.
- [ ] **Ex J5.6.3 Relationships done right.** Map `Loan` → `Schedule` → `ScheduleLine` (one active schedule per loan, lines ordered by `instalment_no`), with all `@ManyToOne` LAZY and bidirectional helper methods. *Acceptance:* tests cover adding and removing lines, and orphan removal behaves as you intended (documented).
- [ ] **Ex J5.6.4 Reproduce and kill N+1.** List 100 loans with their customer names and product codes. First run it naively and count the SQL statements (Hibernate `Statistics` or a datasource-proxy query counter). Then fix it three ways: `JOIN FETCH`, an entity graph and batch fetching. *Acceptance:* a test asserts the statement count for each fix (e.g. 1 or 3, not 201); `NOTES.md` explains when each fix is appropriate, including pagination with `JOIN FETCH` on collections.
- [ ] **Ex J5.6.5 LazyInitializationException.** Close the `EntityManager`, then access a lazy collection. *Acceptance:* reproduce the exception in a test and list two correct fixes and one anti-pattern (Open Session in View / `enable_lazy_load_no_trans`) with reasons.

### Must be able to do / explain
- [ ] Bootstrap JPA/Hibernate without Spring and validate mappings against a Flyway-managed schema.
- [ ] Choose and configure ID generation on Oracle (sequence + pooled optimizer).
- [ ] Map all association types correctly, with LAZY fetching by default.
- [ ] Detect N+1 with statement counting and fix it with the right tool.
- [ ] Explain owning vs inverse side and `mappedBy`.
- [ ] Implement entity `equals`/`hashCode` safely.

**Estimated hours:** ~8 h

### Self-check interview questions
1. What is the difference between JPA and Hibernate?
2. Why is `GenerationType.SEQUENCE` preferred over `IDENTITY` with Hibernate, especially for batching?
3. What is the owning side of a bidirectional relationship, and why does it matter?
4. What is the N+1 problem? Give three ways to solve it in Hibernate.
5. Why should `@ManyToOne` usually be LAZY even though the JPA default is EAGER?
6. What causes `LazyInitializationException`, and why is Open Session in View considered an anti-pattern?
7. How should you implement `equals`/`hashCode` for an entity with a generated id?
8. What does `allocationSize` do, and what happens if it doesn't match the sequence increment?

---

**Answers**
1. JPA (Jakarta Persistence) is the specification: annotations, the `EntityManager` API, JPQL. Hibernate is the most widely used implementation, and it adds its own features (extra annotations, statistics, batch fetching, second-level cache providers).
2. With `IDENTITY` the id is only known after the INSERT executes, so Hibernate must insert immediately and cannot batch inserts. `SEQUENCE` lets Hibernate get ids ahead of time (in blocks with the pooled optimizer), defer and batch INSERTs, and reduce round trips.
3. The owning side holds the foreign key; in `@OneToMany(mappedBy=…)` it is the `@ManyToOne` side. Only changes to the owning side are written to the database, so if you only update the inverse collection, nothing is persisted.
4. One query loads N parents, then N more queries load each parent's association. Fixes: `JOIN FETCH` in JPQL, entity graphs (`@EntityGraph` or `EntityGraph` hints), and batch fetching (`@BatchSize` / `default_batch_fetch_size`). Subselect fetching and DTO projections also help.
5. EAGER loads the association every time, often with extra queries or joins you don't need. It can't be turned off per query, while LAZY can be turned into eager fetching per use case with fetch joins or graphs.
6. Accessing an uninitialized lazy proxy or collection after the persistence context is closed. OSIV keeps the session open during view rendering, which hides N+1 problems, holds DB connections longer and blurs transaction boundaries.
7. Use a business key when one exists. Otherwise base `equals` on the id with null-safety (a transient entity equals only itself) and return a constant `hashCode` (e.g. `getClass().hashCode()`), so the hash doesn't change when the id is assigned on persist.
8. It is the number of ids Hibernate reserves per sequence call (the pooled optimizer uses the sequence value as a hi/lo boundary). It must equal the sequence's `INCREMENT BY`. Otherwise you get duplicate ids (increment smaller than allocation) or gaps and wasted values, and multi-instance apps can collide.

---

## Module J5.7 — JPA & Hibernate II: Persistence Context, Caching, Locking, Batching (~7h)

**Topics:**
- The persistence context as a first-level cache and identity map.
- Entity lifecycle (transient, managed, detached, removed); `persist` vs
  `merge`.
- Dirty checking and automatic UPDATEs; flush modes (AUTO, COMMIT) and
  when flushes happen (before queries, at commit).
- `@Transactional`-free transaction handling (`EntityTransaction`).
- Second-level cache: concepts, regions, when it helps and when it hurts;
  the query cache.
- **Optimistic locking** with `@Version` (`OptimisticLockException`,
  retry). **Pessimistic locking** with `LockModeType.PESSIMISTIC_WRITE`
  (→ `SELECT … FOR UPDATE` on Oracle), lock timeouts, `NOWAIT` /
  `SKIP LOCKED` hints.
- JDBC batching in Hibernate: `hibernate.jdbc.batch_size`, `order_inserts`,
  `order_updates`; `flush()`/`clear()` in loops.
- Bulk `UPDATE`/`DELETE` via JPQL, and their effect on the persistence
  context.

### Lessons
- [ ] **J5.7.L1 Persistence context.** Hibernate User Guide → "Persistence Contexts" (entity states, `persist`, `merge`, `detach`, `refresh`), plus "Flushing" (flush modes, automatic flush before queries).
- [ ] **J5.7.L2 Dirty checking.** Vlad Mihalcea blog: "How does the dirty checking mechanism work in JPA and Hibernate" and "A beginner's guide to JPA and Hibernate entity state transitions" [verify titles].
- [ ] **J5.7.L3 Caching.** Hibernate User Guide → "Caching" (second-level cache configuration, concurrency strategies, query cache). *High-Performance Java Persistence*, the "Caching" chapter.
- [ ] **J5.7.L4 Locking.** Hibernate User Guide → "Locking" (optimistic with `@Version`, pessimistic `LockModeType`, lock timeouts). Jakarta Persistence 3.2 spec, the "Locking and Concurrency" chapter. Recap 1C Modules 2.7–2.8 and 3.x (Oracle row locking).
- [ ] **J5.7.L5 Batching.** Hibernate User Guide → "Batching" (JDBC batching, session batching, `flush`/`clear`). Vlad Mihalcea blog: "How to batch INSERT and UPDATE statements with Hibernate" [verify title].

### Exercises (`java/J5-databases/j5-7-hibernate-advanced/`)
- [ ] **Ex J5.7.1 Watch dirty checking.** Load a `Customer`, change a field, commit without calling any "save" method. *Acceptance:* SQL logs show the UPDATE; a second test shows a flush triggered by a JPQL query before commit, and `NOTES.md` explains both.
- [ ] **Ex J5.7.2 persist vs merge.** Write tests that show: `merge` returns a *different* managed instance; changes to the detached object after `merge` are ignored; `persist` on a detached entity throws. *Acceptance:* each behaviour is proven by an assertion, not by reading logs.
- [ ] **Ex J5.7.3 Optimistic locking race.** Add `@Version` to `Loan`. Simulate two users editing the same loan (two `EntityManager`s). *Acceptance:* the second commit fails with `OptimisticLockException`; add a small retry-with-reload helper and a test that it succeeds on retry when the change doesn't conflict.
- [ ] **Ex J5.7.4 Pessimistic lock on Oracle.** Implement "take the next unprocessed payment file row" with `PESSIMISTIC_WRITE` plus a `SKIP LOCKED` hint (`jakarta.persistence.lock.timeout = -2` / Hibernate `LockOptions.SKIP_LOCKED` [verify]). Run 4 concurrent workers. *Acceptance:* each row is processed exactly once; the SQL log shows `FOR UPDATE SKIP LOCKED`.
- [ ] **Ex J5.7.5 Batch 100k inserts.** Insert 100,000 `LoanTransaction` rows. Compare no batching, `batch_size=50`, and `batch_size=50` with `flush()`/`clear()` every 50 rows. *Acceptance:* a timing and memory table in `NOTES.md`; SQL logs confirm the JDBC batching; the naive version's memory growth is explained.
- [ ] **Ex J5.7.6 Second-level cache for reference data.** Cache `LoanProduct` (read-mostly) in the second-level cache (e.g. with a JCache/Ehcache or Caffeine provider). *Acceptance:* the statistics show cache hits on repeated reads in new `EntityManager`s. `NOTES.md` explains why balances or transactions must **not** be cached.

### Must be able to do / explain
- [ ] Explain entity states and predict when Hibernate will issue SQL.
- [ ] Use optimistic locking with `@Version` and handle conflicts.
- [ ] Use pessimistic locking (incl. `SKIP LOCKED`) and explain the SQL it generates on Oracle.
- [ ] Configure JDBC batching and process large data sets without running out of memory.
- [ ] Decide what belongs in the second-level cache and what doesn't.

**Estimated hours:** ~7 h

### Self-check interview questions
1. What is the persistence context, and what guarantees does it give within one transaction?
2. How does dirty checking work, and when does Hibernate flush?
3. What is the difference between `persist` and `merge`?
4. When would you choose optimistic over pessimistic locking?
5. What SQL does `PESSIMISTIC_WRITE` generate on Oracle, and how do `NOWAIT`/`SKIP LOCKED` change it?
6. Why can inserting 1 million entities in one persistence context cause an OutOfMemoryError, and how do you avoid it?
7. What are the risks of using the second-level cache?
8. What happens to already-loaded entities when you run a JPQL bulk UPDATE?

---

**Answers**
1. A first-level cache and identity map for managed entities within an `EntityManager`: one Java instance per database row, repeatable reads of the same entity without re-querying, and change tracking for dirty checking.
2. At load time Hibernate keeps a snapshot of each entity's state. At flush it compares the current state with the snapshot and generates UPDATEs for changed entities. A flush happens at commit, before queries that could be affected (in AUTO mode), and on an explicit `flush()`.
3. `persist` makes a transient instance managed (the same object) and schedules an INSERT; it fails for detached entities. `merge` copies the state of a (usually detached) object onto a managed instance, loading or creating it, and returns that managed instance. The argument stays detached.
4. Optimistic locking fits when conflicts are rare and transactions may span user think-time: no DB locks are held, conflicts are detected at commit via the version, then you retry. Pessimistic locking fits when conflicts are frequent or the cost of a retry is high (money movements, queue-like work distribution), at the price of blocking.
5. `SELECT … FOR UPDATE`. With a timeout of 0 you get `FOR UPDATE NOWAIT` (fail immediately if locked); with SKIP LOCKED you get `FOR UPDATE SKIP LOCKED` (skip locked rows, which is ideal for worker queues).
6. Every managed entity and its snapshot stays in the persistence context until it is closed, so memory grows linearly and dirty checking gets slower. Flush and `clear()` every N rows (matching `batch_size`), or use `StatelessSession` for pure bulk loads.
7. Stale data if the database is modified outside Hibernate (PL/SQL batches, other apps), extra memory, and harder reasoning about consistency. It is only safe for read-mostly reference data with a clear invalidation story, never for balances.
8. The bulk statement goes straight to the database and bypasses the persistence context, so managed entities keep stale state. Run bulk operations in a separate transaction or clear/refresh affected entities afterwards.

---

## Module J5.8 — JPQL, Native Queries & Criteria API (~4h)

**Topics:**
- JPQL: SELECT with joins, `JOIN FETCH`, aggregates, `GROUP BY`,
  constructor expressions / DTO projections (`select new …`), named
  parameters, pagination (`setFirstResult`/`setMaxResults`), named queries.
- Native SQL queries (`createNativeQuery`) and result mappings
  (`@SqlResultSetMapping`, or Hibernate's tuple and record mapping). When to
  drop to native SQL: analytic functions, `CONNECT BY`, hints.
- Criteria API with the static metamodel for dynamic, type-safe filters.
- Stored procedures via JPA: `StoredProcedureQuery` and
  `@NamedStoredProcedureQuery` as a **preview**; the Spring Data
  `@Procedure` wrapper comes in 04c J7.5.

### Lessons
- [ ] **J5.8.L1 JPQL/HQL.** Hibernate User Guide → "Hibernate Query Language" (the select statement, joins, fetch joins, projections, pagination, parameters). Jakarta Persistence 3.2 spec → "Query Language" chapter (skim).
- [ ] **J5.8.L2 Native queries.** Hibernate User Guide → "Native SQL Queries" (scalar queries, entity queries, `@SqlResultSetMapping`).
- [ ] **J5.8.L3 Criteria.** Hibernate User Guide → "Criteria" and the Jakarta Persistence metamodel (`hibernate-jpamodelgen` annotation processor).
- [ ] **J5.8.L4 Stored procedures in JPA.** Hibernate User Guide → "Native SQL Queries" → the stored procedure section (`StoredProcedureQuery`, REF CURSOR parameters on Oracle). Vlad Mihalcea blog: "How to call Oracle stored procedures and functions with JPA and Hibernate" [verify title].
- [ ] **J5.8.L5 DTO projections.** Vlad Mihalcea blog: "The best way to map a projection query to a DTO with JPA and Hibernate" [verify title].

### Exercises (`java/J5-databases/j5-8-queries/`)
- [ ] **Ex J5.8.1 JPQL report with DTOs.** Query "loans per product with total principal and average rate" into a Java record via `select new …`. *Acceptance:* a single SQL statement; results match an equivalent SQL query you run in SQLcl (compare in the test).
- [ ] **Ex J5.8.2 Native analytic query.** Implement the "delinquency ranking" (rank loans by days past due within each branch using `DENSE_RANK() OVER (PARTITION BY …)`) as a native query mapped to a record. *Acceptance:* results are correct for seeded data; `NOTES.md` explains why this is native and not JPQL.
- [ ] **Ex J5.8.3 Dynamic search with Criteria.** Build `LoanSearch` with optional filters (branch, product, status, min principal, disbursed date range) and sorting, plus pagination using the metamodel. *Acceptance:* tests for 5 filter combinations; a bound parameter for every filter value (no string building); a count query for total pages.
- [ ] **Ex J5.8.4 Stored procedure via JPA.** Call the J5.5 REF CURSOR schedule procedure with `StoredProcedureQuery`. *Acceptance:* same result as the JDBC version; `NOTES.md` lists which approach you prefer and why.

### Must be able to do / explain
- [ ] Write JPQL with joins, fetch joins, aggregates and DTO projections.
- [ ] Decide when native SQL is the right tool and map its results safely.
- [ ] Build dynamic type-safe queries with the Criteria API.
- [ ] Call a stored procedure (incl. REF CURSOR) through JPA.

**Estimated hours:** ~4 h

### Self-check interview questions
1. What is the difference between `JOIN` and `JOIN FETCH` in JPQL?
2. Why do DTO projections often perform better than loading entities for read-only screens?
3. Why can pagination combined with `JOIN FETCH` on a collection be dangerous?
4. When would you use the Criteria API instead of JPQL strings?
5. Give two reasons to use a native query.

---

**Answers**
1. `JOIN` only lets you filter or project on the association; the association is not initialized. `JOIN FETCH` loads the associated entities in the same query and initializes the association (fixing N+1 for that use case).
2. They select only the needed columns, create no managed entities (no snapshots, no dirty checking, no persistence-context memory) and can't trigger lazy loading. That means less memory and CPU, and often less I/O.
3. The join multiplies rows, so the database can't apply LIMIT per parent. Hibernate then fetches everything and paginates in memory (with a warning `HHH90003004` [verify code]), which is a performance trap. The fix: paginate parent ids first, then fetch the collections for those ids.
4. When the query structure is dynamic (optional filters, sort fields chosen by the user). Criteria with the metamodel gives compile-time checking and avoids fragile string concatenation.
5. Database-specific features JPQL lacks: analytic functions, hierarchical queries, hints and optimizer control, set operations in older versions, JSON functions. And hand-tuned SQL for performance-critical reports.

---

## Module J5.9 — Oracle Performance from Java (~4h)

**Topics:**
- Round trips as the main cost: **fetch size** (Oracle's default is 10 rows
  per round trip; `setFetchSize`, `defaultRowPrefetch`, Hibernate
  `jdbc.fetch_size`).
- **Statement caching** in the Oracle driver (implicit statement cache,
  `setImplicitCachingEnabled`, `oracle.jdbc.implicitStatementCacheSize`)
  vs HikariCP (which intentionally has no statement cache).
- Batching recap; **array binds** for bulk DML (bind a collection and let
  PL/SQL `FORALL` do the work).
- Bind variables and hard vs soft parses (why literals kill the shared
  pool); bind peeking and adaptive cursor sharing (awareness only).
- Reading execution plans for your app's SQL: `DBMS_XPLAN.DISPLAY_CURSOR`
  with `SQL_ID`, finding your statements in `V$SQL` by module/action
  (the J5.5 `DBMS_APPLICATION_INFO`), `GATHER_PLAN_STATISTICS`.
- The access you need for `V$` views in dev (`SELECT_CATALOG_ROLE`).
- Common app-side anti-patterns: N+1, row-by-row processing ("slow by
  slow"), too-small fetch size, unindexed foreign keys causing lock
  escalation on Oracle.

### Lessons
- [ ] **J5.9.L1 Driver performance.** Oracle *JDBC Developer's Guide* (23ai): "Performance Extensions" (row prefetching / fetch size, update batching) and "Statement and Result Set Caching" (implicit vs explicit statement caching).
- [ ] **J5.9.L2 Parsing & binds.** Oracle *SQL Tuning Guide* (23ai): "SQL Processing" (hard vs soft parse, shared pool) and "Improving Real-World Performance Through Cursor Sharing" (bind variables, adaptive cursor sharing).
- [ ] **J5.9.L3 Plans.** *SQL Tuning Guide*: "Generating and Displaying Execution Plans" and "Reading Execution Plans". *PL/SQL Packages and Types Reference*: `DBMS_XPLAN.DISPLAY_CURSOR` (format `ALLSTATS LAST`). Recap 1C Module 3.10.
- [ ] **J5.9.L4 Application-side tuning.** Vlad Mihalcea: *High-Performance Java Persistence*, Part 1 "JDBC and Database Essentials": the chapters on connection management, batch updates, statement caching and ResultSet fetching. Blog: "How does the JDBC fetch size work" / "Oracle JDBC statement caching" [verify titles].
- [ ] **J5.9.L5 Real-world view.** Oracle Real-World Performance videos on YouTube: "Connection pools" and "Row-by-row vs set-based" [verify titles]. Tom Kyte's "slow-by-slow" mantra (asktom.oracle.com).

### Exercises (`java/J5-databases/j5-9-oracle-perf/`)
- [ ] **Ex J5.9.1 Fetch size experiment.** Read 200,000 `loan_transactions` rows with fetch sizes 10 (default), 100, 1,000 and 5,000. *Acceptance:* a timing and memory table; the number of round trips estimated or measured (e.g. via `V$SESSTAT` "SQL*Net roundtrips to/from client"); a recommended value for this app with justification.
- [ ] **Ex J5.9.2 Literals vs binds.** Run the same query 10,000 times with literals and then with binds. *Acceptance:* `V$SQL` shows thousands of child cursors or distinct SQL_IDs for literals and one for binds; parse counts are compared in `NOTES.md`.
- [ ] **Ex J5.9.3 Statement cache.** Enable the Oracle implicit statement cache on the data source (keep HikariCP as the pool). Measure a hot loop of prepare/execute/close. *Acceptance:* before and after timings plus parse-count statistics, with an explanation of why HikariCP leaves statement caching to the driver.
- [ ] **Ex J5.9.4 Array bind + FORALL.** Insert 100,000 rows three ways: JDBC batch of single INSERTs, a PL/SQL procedure taking an array (`createOracleArray`) and using `FORALL`, and row-by-row calls. *Acceptance:* a timing table; one paragraph on when each approach fits.
- [ ] **Ex J5.9.5 Find and explain your own SQL.** Tag a service call with `DBMS_APPLICATION_INFO` (module/action), run it, find its statements in `V$SQL` by module, and display the actual plan with `DBMS_XPLAN.DISPLAY_CURSOR(sql_id, NULL, 'ALLSTATS LAST')`. *Acceptance:* `docs/plan-review.md` with the plan, what you expected and what you saw, and one improvement (an index, a rewrite or a fetch-size change) with a before and after measurement.

### Must be able to do / explain
- [ ] Tune fetch size and explain its effect on round trips and memory.
- [ ] Explain hard vs soft parses and why bind variables matter for scalability.
- [ ] Configure Oracle statement caching alongside HikariCP.
- [ ] Choose between JDBC batching and array binds with `FORALL` for bulk work.
- [ ] Find your application's SQL in `V$SQL` and read its actual execution plan.

**Estimated hours:** ~4 h

### Self-check interview questions
1. What is Oracle's default JDBC fetch size, and why can it make a simple report slow?
2. What is a hard parse, and why do literal values in SQL hurt a busy Oracle database?
3. Where does statement caching happen when you use HikariCP with Oracle?
4. When would you pass an array to PL/SQL with `FORALL` instead of using JDBC batching?
5. How do you find the execution plan of a statement your Java service just ran?
6. What is "slow-by-slow" processing, and how do you avoid it from Java?

---

**Answers**
1. 10 rows per round trip. Reading 100k rows costs about 10,000 network round trips, so latency dominates. Raise the fetch size (per statement or via `defaultRowPrefetch`), within memory limits.
2. Full parsing and optimization of a statement not found in the shared pool. It takes CPU and shared-pool latches. Literals make every statement text unique, which forces hard parses, floods the shared pool and limits concurrency; binds allow reuse (soft parses).
3. In the Oracle JDBC driver (implicit statement caching per physical connection). HikariCP deliberately has no statement cache, because the driver's cache is more efficient and aware of the driver's internals.
4. When the processing logic lives in PL/SQL, or for very large volumes where one call with a collection plus a set-based `FORALL` minimizes round trips and context switches. It is also a good fit when you want validation or business rules applied inside the database in the same call.
5. Tag the session with `DBMS_APPLICATION_INFO` (module/action), find the SQL_ID in `V$SQL` by module or a text filter, then run `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('<sql_id>', NULL, 'ALLSTATS LAST'))`. Use `/*+ GATHER_PLAN_STATISTICS */` or `STATISTICS_LEVEL=ALL` to get actual row counts.
6. Processing rows one at a time in a loop, each with its own round trip or statement. Avoid it with set-based SQL, JDBC batching, array binds with `FORALL`, larger fetch sizes, and pushing aggregation to the database.

---

## Track 4B progress summary

| Item | Name | Hours | Lessons | Exercises | Done |
|---|---|---|---|---|---|
| J5.1 | JDBC fundamentals | 6 | 6 | 6 | [ ] |
| J5.2 | Connection pooling with HikariCP | 2 | 3 | 3 | [ ] |
| J5.3 | Oracle from Java: drivers, UCP, types, Testcontainers | 5 | 6 | 5 | [ ] |
| J5.4 | Schema migrations: Flyway & Liquibase | 4 | 5 | 5 | [ ] |
| **JP2** | **BranchDesk · Junior (Oracle, plain JDBC)** | **30** | — | 5 milestones | [ ] |
| J5.5 | Calling PL/SQL from Java | 7 | 7 | 6 | [ ] |
| J5.6 | JPA & Hibernate I | 8 | 6 | 5 | [ ] |
| J5.7 | JPA & Hibernate II | 7 | 5 | 6 | [ ] |
| J5.8 | JPQL, native queries & Criteria API | 4 | 5 | 4 | [ ] |
| J5.9 | Oracle performance from Java | 4 | 5 | 5 | [ ] |
| | **Total** | **~77 h** (47 h modules + 30 h project) | **48** | **45** | |

Next: [04c-spring.md](04c-spring.md). Spring Framework core, Spring Boot and
the ecosystem, microservices, interview prep, and projects JP3, JM1–JM3 and
JMP1–JMP3.
