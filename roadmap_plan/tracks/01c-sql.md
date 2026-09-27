# Track 1C — SQL: PostgreSQL → Advanced PostgreSQL → Oracle SQL & PL/SQL

**Goal.** Go from "basic SELECT/JOIN/GROUP BY with mistakes" to writing correct,
fast, concurrency-safe SQL in PostgreSQL, then work confidently in Oracle SQL
and PL/SQL. At the end you should be able to design a schema, write any
reporting query (CTEs, window functions), read an execution plan, explain
isolation levels and locking, and write and test PL/SQL packages.

**Required knowledge.** None from other tracks. Basic command-line use and
Docker basics (running a container) help. Track 2 (Backend) and Track 4
(Java) both rely on this track.

**Total estimated time: ~145 h**

| Part | Content | Modules | Hours |
|---|---|---|---|
| Part 1 | SQL fundamentals in PostgreSQL | 7 | ~35 h |
| Part 2 | Advanced SQL + PostgreSQL internals | 11 | ~55 h |
| Part 3 | Oracle SQL + PL/SQL | 11 | ~55 h |

---

## How to use this track

- Work through the modules in order inside each part. Part 3 needs Parts 1–2.
- Each module has **lessons** (theory, with the exact resource to read) and
  **tasks** (problems). Tick `[x]` when done.
- **No solutions are in this file.** Each task gives the tables involved,
  the technique, and the expected output shape. If you are stuck for
  ~20–25 minutes, re-read the lesson resource for that technique — do not
  search for the answer to the task itself.
- **Redo rule.** Rewrite each task from a blank file 3 days later and again
  7 days later. If you cannot, it is not learned yet.
- Always run your query on real data. Insert 10–20 rows of test data that
  include the edge cases (NULLs, ties, empty groups, duplicates).
- Answers exist only for the self-check interview questions, below the
  separator at the end of each module. Answer out loud first, then check.

### Where your work goes

```
sql/
  p1-01-select-where-null/
    combine_two_tables.sql
    stockpilot_low_stock.sql
  p2-02-window-functions/
    rank_scores.sql
  p3-05-procedures-packages/
    pkg_schedule.sql
```

Pattern: `sql/<part>-<NN>-<module-slug>/<task_slug>.sql`. Each file starts
with the relevant table schema as comments (so the file is self-contained),
then the query:

```sql
-- Schema (StockPilot):
--   products(id, sku, name, category_id, supplier_id, price_cents,
--            current_stock, reorder_level)
-- Task: products below their reorder level, worst shortage first.

-- your query here
```

### Setup

**PostgreSQL (Parts 1–2)**

```bash
docker run -d --name pg17 -e POSTGRES_PASSWORD=dev -p 5432:5432 \
  -v pg17data:/var/lib/postgresql/data postgres:17
docker exec -it pg17 psql -U postgres
```

- Useful `psql` commands: `\l`, `\c db`, `\dt`, `\d table`, `\di`, `\timing on`,
  `\x auto`, `\i file.sql`, `\e`.
- Create one database per practice schema: `CREATE DATABASE stockpilot;`
- For generating volume: `generate_series()` (see PostgreSQL docs §9.26
  "Set Returning Functions").
- GUI (optional): DBeaver Community or pgAdmin.

**Oracle (Part 3)**

```bash
docker run -d --name oracle -p 1521:1521 \
  -e ORACLE_PASSWORD=dev -e APP_USER=learn -e APP_USER_PASSWORD=learn \
  -v oradata:/opt/oracle/oradata gvenzl/oracle-free:23-slim
docker logs -f oracle      # wait for "DATABASE IS READY TO USE!"
```

- Connect as the app user to the pluggable DB `FREEPDB1`:
  `sql learn/learn@localhost:1521/FREEPDB1` (SQLcl) or
  `docker exec -it oracle sqlplus learn/learn@FREEPDB1`.
- Tools: **SQLcl** (modern command line), SQL*Plus (inside the container),
  or **DBeaver** / SQL Developer / the Oracle SQL Developer VS Code extension.
- `SET SERVEROUTPUT ON` before running PL/SQL that uses `DBMS_OUTPUT`.
- For DBMS_SCHEDULER, V$ views and plans you may need extra grants — connect
  as `system` and `GRANT CREATE JOB, SELECT_CATALOG_ROLE TO learn;`.
- **Fallback:** Oracle Live SQL (https://livesql.oracle.com) — runs in the
  browser, no install; enough for Modules 3.1–3.8 (not for Scheduler/tuning).

### Main resources (used throughout)

| Resource | Link | Used in |
|---|---|---|
| PostgreSQL 17 Documentation | https://www.postgresql.org/docs/17/ | Parts 1–2 |
| PostgreSQL Exercises | https://pgexercises.com | Parts 1–2 |
| Use The Index, Luke! (Markus Winand) | https://use-the-index-luke.com | 2.5, 2.6, 3.10 |
| LeetCode Database problems | https://leetcode.com/problemset/database/ | Parts 1–2 (and re-solving in Oracle) |
| Oracle Database SQL Language Reference (23ai) | https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/ | Part 3 |
| Oracle Database PL/SQL Language Reference (23ai) | https://docs.oracle.com/en/database/oracle/oracle-database/23/lnpls/ | Part 3 |
| Oracle PL/SQL Packages and Types Reference (23ai) | https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/ | 3.9, 3.10 |
| Oracle SQL Tuning Guide (23ai) | https://docs.oracle.com/en/database/oracle/oracle-database/23/tgsql/ | 3.10 |
| Oracle Dev Gym (free classes & quizzes) | https://devgym.oracle.com | Part 3 |
| utPLSQL | https://www.utplsql.org/utPLSQL/latest/ | 3.11 |

---

## Practice schemas

All tasks use these schemas. Money is stored as integer cents (`*_cents`)
in PostgreSQL and as `NUMBER(14,2)` in Oracle. Write the `CREATE TABLE`
statements yourself in Module 1.6; before that, create the tables with
simple types and focus on the queries.

**StockPilot** (inventory)
- `users(id, email, hashed_password, role, created_at)`
- `categories(id, name, parent_id → categories.id)`
- `suppliers(id, name, contact_email)`
- `products(id, sku, name, category_id → categories.id, supplier_id → suppliers.id, price_cents, current_stock, reorder_level)`
- `stock_movements(id, product_id → products.id, delta, reason, created_by → users.id, created_at)`
- `orders(id, status, created_by → users.id, created_at)`
- `order_items(id, order_id → orders.id, product_id → products.id, qty, unit_price_cents)`

**QuickServe** (point of sale)
- `products(id, sku, name, price_cents, tax_rate)`
- `discounts(id, code, type, value, max_cap_cents)`
- `receipts(id, cashier_id, status, created_at)`
- `receipt_items(id, receipt_id → receipts.id, product_id → products.id, qty, unit_price_cents, discount_id → discounts.id NULL)`
- `returns(id, receipt_id → receipts.id, reason, processed_by, created_at)`

**PeopleOps** (HR / leave)
- `employees(id, name, department, manager_id → employees.id, hire_date)`
- `leave_requests(id, employee_id → employees.id, start_date, end_date, status, requested_at, approved_at, reminder_sent_at NULL)`
- `leave_balances(id, employee_id → employees.id, year, accrued_days, used_days)`

**WareFlow** (multi-warehouse)
- `warehouses(id, name, location)`
- `stock_levels(id, warehouse_id, product_id, qty)` — `UNIQUE(warehouse_id, product_id)`
- `stock_movements(id, warehouse_id, product_id, delta, reason, ref_id, created_at)`
- `transfers(id, from_warehouse_id, to_warehouse_id, status, created_at)`
- `transfer_items(id, transfer_id → transfers.id, product_id, qty)`
- `reservations(id, order_ref, warehouse_id, product_id, qty, status, created_at)`

**CarePoint** (clinic)
- `doctors(id, name, specialty)`
- `patients(id, name, dob, contact)`
- `appointments(id, doctor_id → doctors.id, patient_id → patients.id, slot_start, slot_end, status)`
- `documents(id, patient_id → patients.id, s3_key, uploaded_by, uploaded_at)`

**LedgerBase** (double-entry accounting)
- `accounts(id, name, type)` — type ∈ asset, liability, equity, revenue, expense
- `journal_entries(id, description, created_at)`
- `journal_lines(id, journal_entry_id → journal_entries.id, account_id → accounts.id, debit_cents, credit_cents)`
- `invoices(id, client_name, total_cents, status, issued_at, due_at)`
- `payments(id, invoice_id → invoices.id, amount_cents, journal_entry_id → journal_entries.id, received_at)`

**FleetTrack** (deliveries, event-driven)
- `drivers(id, name, status)`
- `deliveries(id, driver_id → drivers.id, status, created_at)`
- `delivery_events(id, delivery_id → deliveries.id, from_status, to_status, created_at)`
- `outbox(id, aggregate_type, aggregate_id, event_type, payload JSONB, created_at, sent_at NULL)`
- `delivery_view(id, driver_name, status, last_updated)` — read model

**DocuVault** (documents)
- `documents(id, title, body_text, current_version_id, created_by)`
- `document_versions(id, document_id → documents.id, s3_key, version_number, created_at)`
- `tags(id, name)`
- `document_tags(document_id, tag_id)` — PK(document_id, tag_id)

**PayFlow** (payments)
- `payment_intents(id, idempotency_key, request_hash, amount_cents, status, journal_entry_id NULL, created_at)`
- `webhook_events(id, provider_event_id, payload JSONB, processed_at NULL, received_at)`
- `refunds(id, payment_intent_id → payment_intents.id, amount_cents, journal_entry_id, created_at)`
- `audit_log(id, entity_type, entity_id, action, old_state JSONB NULL, new_state JSONB NULL, actor, created_at)`

**AtlasMarket** (marketplace; StockPilot tables plus)
- `vendors(id, name, payout_account_ref)`
- `products(..., vendor_id → vendors.id)`
- `order_vendor_groups(id, order_id → orders.id, vendor_id → vendors.id, status, journal_entry_id)`

**CreditLine** (Oracle, Part 3 — loan servicing)
- `branches(branch_id, code, name, region)`
- `customers(customer_id, tax_id UNIQUE, full_name, birth_date, phone, kyc_status, blacklist_flag)`
- `loan_products(product_id, code, name, interest_method, nominal_rate, min_amount, max_amount, min_term_m, max_term_m, grace_days, penalty_rate, valid_from, valid_to)` — interest_method ∈ FLAT, DECLINING, ANNUITY
- `loans(loan_id, customer_id, product_id, branch_id, principal, rate, term_m, disbursed_at, first_due_date, maturity_date, status)`
- `schedules(schedule_id, loan_id, version, generated_at, reason, is_active)` — only one active per loan
- `schedule_lines(line_id, schedule_id, instalment_no, due_date, principal_due, interest_due, fee_due, principal_paid, interest_paid, fee_paid, status)`
- `loan_transactions(txn_id, loan_id, txn_type, amount, value_date, posted_at, posted_by, reversal_of_txn_id NULL, batch_id NULL)` — txn_type ∈ DISBURSE, REPAY, ACCRUAL, PENALTY, FEE, WAIVER, WRITEOFF, RECOVERY, REVERSAL
- `payment_allocations(alloc_id, txn_id, line_id, component, amount)` — component ∈ PENALTY, FEE, INTEREST, PRINCIPAL
- `gl_accounts(account_id, code UNIQUE, name, type, parent_account_id NULL)` — chart of accounts tree
- `gl_entries(entry_id, txn_id, entry_date, description)`
- `gl_lines(line_id, entry_id, account_id, debit, credit)` — exactly one of debit/credit is non-zero
- `delinquency_snapshots(snap_id, loan_id, snapshot_date, days_past_due, bucket, overdue_principal, overdue_interest)`
- `period_status(period_yyyymm, status, closed_by, closed_at)`
- `batch_runs(batch_id, batch_name, business_date, started_at, finished_at, status, records_processed, error_text)`
- `batch_errors(err_id, batch_id, loan_id, error_code, error_msg, raised_at)`
- `audit_log(audit_id, table_name, pk_value, action, old_row_json, new_row_json, changed_by, changed_at)`

---

# PART 1 — SQL fundamentals in PostgreSQL (~35 h)

## Module 1.1 — SELECT, WHERE, NULL semantics, ORDER BY / LIMIT

**Estimated: 5 h**

**Topics:** logical order of evaluation (FROM → WHERE → GROUP BY → HAVING →
SELECT → ORDER BY → LIMIT); column aliases; `DISTINCT`; comparison and
`BETWEEN`/`IN`/`LIKE`; three-valued logic (TRUE/FALSE/UNKNOWN); `IS NULL`,
`IS DISTINCT FROM`; `COALESCE`, `NULLIF`; `ORDER BY` with `NULLS FIRST/LAST`
and a deterministic tie-breaker; `LIMIT`/`OFFSET` and `FETCH FIRST`.

**Lessons**
- [ ] **L1.1.1 Querying a table** — PostgreSQL docs, Tutorial Ch.2 "The SQL Language": §2.5 Querying a Table, §2.6 (skim). Ch.7 "Queries": §7.1 Overview, §7.3 Select Lists (incl. §7.3.3 DISTINCT).
- [ ] **L1.1.2 NULL and three-valued logic** — §9.1 Logical Operators (truth tables), §9.2 Comparison Functions and Operators (`IS NULL`, `IS DISTINCT FROM`), §9.18.2 COALESCE, §9.18.3 NULLIF.
- [ ] **L1.1.3 Sorting and paging** — §7.5 Sorting Rows (ORDER BY), §7.6 LIMIT and OFFSET. pgexercises.com → **Basic** (all 10 exercises).

**Tasks**
- [ ] **T1.1.1 StockPilot: products below their reorder level** · *Filtering* · StockPilot
  Return `sku, name, current_stock, reorder_level` for every product whose stock is below its reorder level, worst shortage (largest `reorder_level − current_stock`) first.
- [ ] **T1.1.2 Find Customer Referee** · *NULL handling* · [LeetCode 584](https://leetcode.com/problems/find-customer-referee/)
  Mini schema: `Customer(id, name, referee_id)`. Return names of customers **not** referred by customer `id = 2` — including customers with no referee at all.
- [ ] **T1.1.3 Big Countries** · *Filtering with OR* · [LeetCode 595](https://leetcode.com/problems/big-countries/)
  Mini schema: `World(name, continent, area, population, gdp)`. Return `name, population, area` for countries with area ≥ 3,000,000 or population ≥ 25,000,000.
- [ ] **T1.1.4 Recyclable and Low Fat Products** · *Filtering* · [LeetCode 1757](https://leetcode.com/problems/recyclable-and-low-fat-products/)
  Mini schema: `Products(product_id, low_fats, recyclable)` (values `'Y'`/`'N'`). Return ids of products that are both low-fat and recyclable.
- [ ] **T1.1.5 StockPilot: product catalogue page 3** · *ORDER BY + LIMIT/OFFSET* · StockPilot
  Return page 3 (20 rows per page) of products sorted by `name`, then `id`. Explain in a comment why the `id` tie-breaker matters, and what goes wrong with OFFSET paging when rows are inserted between page requests.
- [ ] **T1.1.6 NULL truth table** · *Three-valued logic* · no schema
  Write one `SELECT` with a `VALUES` list of `(a, b)` pairs including NULLs that shows, per row, the result of `a = b`, `a <> b`, `a IS DISTINCT FROM b`, `COALESCE(a, b)` and `NULLIF(a, b)`. Output: one row per pair, one column per expression.

**Must be able to do / explain**
- [ ] Say in which order a `SELECT` is logically evaluated and why an alias from `SELECT` cannot be used in `WHERE`.
- [ ] Explain why `WHERE x = NULL` returns nothing and what to write instead.
- [ ] Explain why `NOT (referee_id = 2)` loses NULL rows.
- [ ] Write a deterministic `ORDER BY` for paging.

**Self-check questions**
1. What are the three truth values in SQL, and what does `WHERE` do with UNKNOWN?
2. What is the difference between `a <> b` and `a IS DISTINCT FROM b`?
3. Is `ORDER BY` guaranteed without an explicit `ORDER BY` clause?
4. Why is `OFFSET 100000` slow?
5. What do `COALESCE` and `NULLIF` return? Give a use for each.
6. Where do NULLs sort by default in PostgreSQL, ascending order?

---

**Answers**
1. TRUE, FALSE, UNKNOWN. `WHERE` keeps only rows where the condition is TRUE, so UNKNOWN rows are dropped just like FALSE.
2. `<>` returns NULL (UNKNOWN) if either side is NULL; `IS DISTINCT FROM` treats NULL as a comparable value and always returns TRUE/FALSE.
3. No. Without `ORDER BY`, row order is unspecified and can change between runs, plans or versions.
4. The database must still produce and throw away the first 100 000 rows; cost grows with the offset. Keyset (seek) pagination avoids this.
5. `COALESCE(a, b, …)` returns the first non-NULL argument (defaults, e.g. `COALESCE(city, 'unknown')`). `NULLIF(a, b)` returns NULL if `a = b`, else `a` (e.g. avoid division by zero: `x / NULLIF(y, 0)`).
6. Last (`NULLS LAST` is the default for `ASC`, `NULLS FIRST` for `DESC`).

---

## Module 1.2 — Aggregates, GROUP BY, WHERE vs HAVING

**Estimated: 4 h**

**Topics:** `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)`; `SUM`,
`AVG`, `MIN`, `MAX` and how they ignore NULLs; `GROUP BY` rules (every
non-aggregated column must be grouped); `WHERE` filters rows before
grouping, `HAVING` filters groups after; the `FILTER (WHERE …)` clause;
`ROUND` and integer division pitfalls.

**Lessons**
- [ ] **L1.2.1 Aggregate functions** — Tutorial §2.7 Aggregate Functions; §9.21 Aggregate Functions (general-purpose table); §4.2.7 Aggregate Expressions (FILTER, DISTINCT inside aggregates).
- [ ] **L1.2.2 GROUP BY and HAVING** — Ch.7 §7.2.3 The GROUP BY and HAVING Clauses. pgexercises.com → **Aggregates** (first 10 exercises, stop at the window-function ones).

**Tasks**
- [ ] **T1.2.1 StockPilot: orders per status** · *Aggregation* · StockPilot
  Return `status, order_count` for every order status, most frequent first.
- [ ] **T1.2.2 Classes More Than 5 Students** · *GROUP BY + HAVING* · [LeetCode 596](https://leetcode.com/problems/classes-more-than-5-students/)
  Mini schema: `Courses(student, class)`. Return classes with at least 5 distinct students.
- [ ] **T1.2.3 Duplicate Emails** · *GROUP BY + HAVING* · [LeetCode 182](https://leetcode.com/problems/duplicate-emails/)
  Mini schema: `Person(id, email)`. Return every email that appears more than once.
- [ ] **T1.2.4 StockPilot: stock value per category** · *Aggregation with expression* · StockPilot
  For each `category_id`, return total stock value (`current_stock × price_cents` summed), highest first. (Names come in Module 1.3.)
- [ ] **T1.2.5 PeopleOps: leave request summary per employee** · *Conditional aggregation with FILTER* · PeopleOps
  One row per `employee_id` with columns `pending`, `approved`, `rejected` (counts), and `total`. Return only employees with more than 3 pending requests.

**Must be able to do / explain**
- [ ] Choose correctly between `COUNT(*)`, `COUNT(col)` and `COUNT(DISTINCT col)`.
- [ ] Explain the difference between `WHERE` and `HAVING` with an example.
- [ ] Explain why `AVG(col)` over NULLs may differ from `SUM(col)/COUNT(*)`.
- [ ] Use `FILTER` instead of `SUM(CASE …)`.

**Self-check questions**
1. What does `COUNT(col)` count that `COUNT(*)` does not (and vice versa)?
2. Can you use an aggregate in `WHERE`? Why?
3. What does `SELECT department, name, MAX(salary) FROM e GROUP BY department` do in PostgreSQL?
4. What does `SUM` return on zero rows?
5. What is `5 / 2` in PostgreSQL, and how do you get 2.5?

---

**Answers**
1. `COUNT(*)` counts rows; `COUNT(col)` counts rows where `col` is not NULL.
2. No — `WHERE` runs before grouping, when aggregates do not exist yet. Use `HAVING`.
3. It fails: `name` must appear in `GROUP BY` or be used in an aggregate (unless grouped by a primary key that functionally determines it).
4. NULL, not 0. Wrap in `COALESCE(SUM(x), 0)` if you need 0.
5. `2` (integer division). Cast one side: `5::numeric / 2` or `5 / 2.0`.

---

## Module 1.3 — JOINs (all types, anti-join, self-join)

**Estimated: 6 h**

**Topics:** `INNER`, `LEFT/RIGHT/FULL OUTER`, `CROSS` joins; join condition
in `ON` vs filter in `WHERE` (and how a `WHERE` on the right table silently
turns a LEFT JOIN into an INNER JOIN); **anti-join** (`LEFT JOIN … WHERE
right.id IS NULL`); **self-join** (hierarchies, comparing rows of the same
table); joining 3+ tables; row multiplication (fan-out) when joining one-to-many.

**Lessons**
- [ ] **L1.3.1 Joins** — Tutorial §2.6 Joins Between Tables; Ch.7 §7.2.1.1 Joined Tables (read every join type and the ON vs WHERE note).
- [ ] **L1.3.2 Practice** — pgexercises.com → **Joins and Subqueries**: exercises 1–6 (joins only; subqueries come in 1.4).
- [ ] **L1.3.3 Fan-out** — Read about join fan-out: join `orders` to `order_items` and to `stock_movements` in one query and see totals double. Write down why, and the rule "aggregate before you join".

**Tasks**
- [x] **T1.3.1 Combine Two Tables** · *LEFT JOIN* · [LeetCode 175](https://leetcode.com/problems/combine-two-tables/)
  Mini schema: `Person(person_id, first_name, last_name)`, `Address(address_id, person_id, city, state)`. Return `first_name, last_name, city, state` for every person; people with no address still appear with NULLs.
- [x] **T1.3.2 StockPilot: products with no valid supplier** · *Outer join / anti-join* · StockPilot
  Return `sku, name` for products that have no supplier set, or whose `supplier_id` no longer exists in `suppliers`.
- [ ] **T1.3.3 StockPilot: categories with no products** · *Anti-join* · StockPilot
  Return names of categories that have zero products.
- [ ] **T1.3.4 Employees Earning More Than Their Managers** · *Self-join* · [LeetCode 181](https://leetcode.com/problems/employees-earning-more-than-their-managers/)
  Mini schema: `Employee(id, name, salary, managerId)`. Return names of employees who earn more than their direct manager.
- [ ] **T1.3.5 StockPilot: suppliers whose products never sold** · *Anti-join across 3 tables* · StockPilot
  Return suppliers none of whose products has ever appeared in `order_items`. Include suppliers with no products at all, and state in a comment whether that is the right business answer.
- [ ] **T1.3.6 Top Travellers** · *LEFT JOIN + aggregation* · [LeetCode 1407](https://leetcode.com/problems/top-travellers/)
  Mini schema: `Users(id, name)`, `Rides(id, user_id, distance)`. Each user's total distance (0 if no rides), ordered by distance desc, then name.

**Must be able to do / explain**
- [ ] Draw what each join type returns for two small tables.
- [ ] Explain why `LEFT JOIN b ON … WHERE b.x = 5` behaves like an inner join, and how to fix it.
- [ ] Write an anti-join in three ways (LEFT JOIN/IS NULL, NOT EXISTS, NOT IN) — the last two come in 1.4.
- [ ] Recognise and fix fan-out double counting.

**Self-check questions**
1. What is the difference between putting a condition in `ON` and in `WHERE` for a LEFT JOIN?
2. What is an anti-join and when do you need one?
3. What does a CROSS JOIN produce and when is it useful?
4. How many rows can `a JOIN b` return at most?
5. Why might `SUM(order_items.qty)` be too large after joining another one-to-many table?
6. What is a self-join? Give two real uses.

---

**Answers**
1. In `ON`, it limits which right-side rows match; unmatched left rows are still kept. In `WHERE`, it runs after the join and removes rows where the right side is NULL — so left rows without a match disappear.
2. It returns rows from A that have **no** matching row in B ("customers with no orders"). Written as LEFT JOIN + `IS NULL`, `NOT EXISTS`, or `NOT IN` (careful with NULLs).
3. Every combination of rows (|A| × |B|). Useful for generating grids, e.g. all dates × all products for a report with zeros.
4. |A| × |B| (when every row matches every row).
5. Each order item row is repeated once per matching row of the other table (fan-out), so sums multiply. Aggregate each side first, then join.
6. Joining a table to itself with aliases — manager/employee comparisons, finding overlapping bookings, consecutive rows.

---

## Module 1.4 — Subqueries, EXISTS vs IN, set operations

**Estimated: 5 h**

**Topics:** scalar subqueries; subqueries in `FROM` (derived tables);
correlated subqueries; `IN`, `EXISTS`, `ANY/ALL`; **the `NOT IN` + NULL
trap**; `EXISTS` vs `IN` semantics and performance; `UNION` vs `UNION ALL`,
`INTERSECT`, `EXCEPT`; column count/type rules for set operations.

**Lessons**
- [ ] **L1.4.1 Subquery expressions** — §9.23 Subquery Expressions (EXISTS, IN, NOT IN, ANY/SOME, ALL — read the NULL notes carefully); §4.2.11 Scalar Subqueries; §7.2.1.3 Subqueries (in FROM).
- [ ] **L1.4.2 Set operations** — Ch.7 §7.4 Combining Queries (UNION, INTERSECT, EXCEPT).
- [ ] **L1.4.3 Practice** — pgexercises.com → **Joins and Subqueries**: remaining exercises (7–11).

**Tasks**
- [ ] **T1.4.1 StockPilot: products priced above the average** · *Scalar subquery* · StockPilot
  Return `sku, name, price_cents` and the overall average price as a column, for products priced above that average.
- [ ] **T1.4.2 StockPilot: orders by users with zero stock movements** · *NOT IN vs NOT EXISTS* · StockPilot
  Write the query twice: with `NOT IN` and with `NOT EXISTS`. Insert a `stock_movements` row with `created_by = NULL` and show in a comment how the results differ and why.
- [ ] **T1.4.3 Second Highest Salary** · *Subquery* · [LeetCode 176](https://leetcode.com/problems/second-highest-salary/)
  Mini schema: `Employee(id, salary)`. Return the second-highest distinct salary as `SecondHighestSalary`, or NULL if none — also when the table has one distinct salary.
- [ ] **T1.4.4 QuickServe: receipts with at least one return** · *EXISTS* · QuickServe
  Return `id, cashier_id, created_at` of receipts that have at least one return. No duplicates even if a receipt has several returns.
- [ ] **T1.4.5 WareFlow: products in warehouse A but not in warehouse B** · *EXCEPT* · WareFlow
  Given two warehouse ids, return product ids stocked (qty > 0) in the first but not the second. Then write the same with `NOT EXISTS`.
- [ ] **T1.4.6 Sales Person** · *Anti-join through 2 tables* · [LeetCode 607](https://leetcode.com/problems/sales-person/)
  Mini schema: `SalesPerson(sales_id, name)`, `Company(com_id, name)`, `Orders(order_id, sales_id, com_id)`. Names of sales persons with no orders for company `'RED'`.

**Must be able to do / explain**
- [ ] Explain exactly why `NOT IN (subquery)` returns zero rows when the subquery contains a NULL.
- [ ] Choose between a correlated subquery, a join and `EXISTS`.
- [ ] Explain `UNION` vs `UNION ALL` and when `UNION ALL` is correct.
- [ ] Write a scalar subquery that must return one row, and know what happens if it returns two.

**Self-check questions**
1. What happens with `x NOT IN (1, 2, NULL)`?
2. When is `EXISTS` better than `IN`?
3. What is a correlated subquery?
4. What is the difference between `UNION` and `UNION ALL`?
5. What does `EXCEPT` return, and does it keep duplicates?
6. What happens if a scalar subquery returns more than one row?

---

**Answers**
1. It is never TRUE: for any x not equal to 1 or 2, `x <> NULL` is UNKNOWN, so the whole `NOT IN` is UNKNOWN and the row is filtered out.
2. `EXISTS` stops at the first match and has clean NULL semantics; `NOT EXISTS` is the safe anti-join. PostgreSQL often plans `IN`/`EXISTS` the same (semi-join), but `NOT IN` cannot be turned into an anti-join when NULLs are possible.
3. A subquery that references columns of the outer query, so it is (logically) evaluated once per outer row.
4. `UNION` removes duplicates (extra sort/hash); `UNION ALL` keeps all rows and is faster. Use `UNION ALL` when duplicates are impossible or wanted.
5. Rows of the first query that are not in the second, with duplicates removed (`EXCEPT ALL` keeps them).
6. Runtime error: "more than one row returned by a subquery used as an expression".

---

## Module 1.5 — CASE, string and date functions

**Estimated: 4 h**

**Topics:** simple and searched `CASE`; `CASE` inside aggregates; string
functions (`||`, `concat`, `lower/upper/initcap`, `substring`, `trim`,
`split_part`, `position`, `length`); `LIKE`/`ILIKE` and regular expressions
(`~`, `regexp_replace`); date/time types (`date`, `timestamp`,
`timestamptz`, `interval`); `now()` vs `current_date`; `EXTRACT`,
`date_trunc`, interval arithmetic; time zones (`AT TIME ZONE`).

**Lessons**
- [ ] **L1.5.1 CASE** — §9.18.1 CASE.
- [ ] **L1.5.2 Strings and pattern matching** — §9.4 String Functions and Operators; §9.7 Pattern Matching (§9.7.1 LIKE, §9.7.3 POSIX Regular Expressions). pgexercises.com → **String** (all).
- [ ] **L1.5.3 Dates and times** — §8.5 Date/Time Types (read the `timestamptz` explanation twice); §9.9 Date/Time Functions and Operators (EXTRACT, date_trunc, AT TIME ZONE). pgexercises.com → **Date** (all).

**Tasks**
- [ ] **T1.5.1 Triangle Judgement** · *CASE* · [LeetCode 610](https://leetcode.com/problems/triangle-judgement/)
  Mini schema: `Triangle(x, y, z)`. Return each row plus a column `triangle` = `'Yes'`/`'No'`.
- [ ] **T1.5.2 Fix Names in a Table** · *String functions* · [LeetCode 1667](https://leetcode.com/problems/fix-names-in-a-table/)
  Mini schema: `Users(user_id, name)`. First letter upper-case, rest lower-case, ordered by `user_id` (do it without `initcap`, then compare with `initcap`).
- [ ] **T1.5.3 Patients With a Condition** · *Regex / LIKE* · [LeetCode 1527](https://leetcode.com/problems/patients-with-a-condition/)
  Mini schema: `Patients(patient_id, patient_name, conditions)` (space-separated codes). Patients having a code that **starts with** `DIAB1` as a whole word (not `ACNE+DIAB100` style substrings in the middle of another code).
- [ ] **T1.5.4 PeopleOps: same-day vs delayed approvals** · *CASE + date* · PeopleOps
  For each approved leave request return `id, employee_id, requested_at, approved_at, label` where label is `'same-day'` or `'delayed'`; then a second query counting each label.
- [ ] **T1.5.5 LedgerBase: monthly revenue from paid invoices** · *date_trunc + GROUP BY* · LedgerBase
  One row per month (`month`, `revenue_cents`) for paid invoices, including months with zero revenue in the last 12 months (hint: you need a generated list of months).

**Must be able to do / explain**
- [ ] Explain `timestamp` vs `timestamptz` and which one to store.
- [ ] Group by month/week/day with `date_trunc`.
- [ ] Use `CASE` for labelling and for conditional sums.
- [ ] Explain why `LIKE '%abc'` cannot use a normal B-tree index.

**Self-check questions**
1. What does `timestamptz` actually store?
2. What is the difference between `now()` and `clock_timestamp()` inside a transaction?
3. What does `date_trunc('month', ts)` return?
4. What does a `CASE` without `ELSE` return when nothing matches?
5. `LIKE` vs `ILIKE` vs `~*`?
6. How do you compute "requests pending for 3 or more days"?

---

**Answers**
1. A UTC instant. Input is converted from the session time zone to UTC; output is converted back to the session time zone. No zone name is stored.
2. `now()` (= `transaction_timestamp()`) is fixed at the start of the transaction; `clock_timestamp()` changes on every call.
3. The timestamp rounded down to the first moment of that month (same type as input).
4. NULL.
5. `LIKE` is case-sensitive pattern matching with `%`/`_`; `ILIKE` is the case-insensitive version (PostgreSQL extension); `~*` is a case-insensitive POSIX regex match.
6. `WHERE status = 'pending' AND requested_at <= now() - interval '3 days'` — keep the column bare on one side so an index can be used.

---

## Module 1.6 — DDL, data types, constraints, INSERT/UPDATE/DELETE

**Estimated: 5 h**

**Topics:** `CREATE/ALTER/DROP TABLE`; choosing types (`integer`/`bigint`,
`numeric` vs `real/double`, integer cents for money, `text` vs
`varchar(n)`, `boolean`, `date`/`timestamptz`, `uuid`); identity columns
vs `serial`; `DEFAULT`; constraints: `NOT NULL`, `UNIQUE`, `PRIMARY KEY`,
`FOREIGN KEY` (with `ON DELETE` actions), `CHECK`; `INSERT … VALUES /
SELECT`; `UPDATE … FROM`; `DELETE … USING`; `TRUNCATE`; DDL is
transactional in PostgreSQL.

**Lessons**
- [ ] **L1.6.1 Data definition** — Ch.5 Data Definition: §5.1 Table Basics, §5.2 Default Values, §5.3 Identity Columns, §5.5 Constraints (all subsections), §5.7 Modifying Tables.
- [ ] **L1.6.2 Data types** — Ch.8: §8.1 Numeric Types (read the money/float warning), §8.3 Character Types, §8.5 Date/Time Types, §8.6 Boolean, §8.12 UUID.
- [ ] **L1.6.3 Data manipulation** — Ch.6: §6.1 Inserting Data, §6.2 Updating Data, §6.3 Deleting Data. pgexercises.com → **Modifying Data** (all).

**Tasks**
- [ ] **T1.6.1 StockPilot DDL** · *DDL + constraints* · StockPilot
  Write the full `CREATE TABLE` script for all 7 StockPilot tables with identity PKs, FKs (choose and justify each `ON DELETE`), `CHECK (price_cents >= 0)`, `CHECK (qty > 0)`, unique `sku`, unique `email`, and sensible `NOT NULL`s. Then insert rows that violate each constraint and record each error message.
- [ ] **T1.6.2 Swap Salary** · *Single UPDATE with CASE* · [LeetCode 627](https://leetcode.com/problems/swap-salary/)
  Mini schema: `Salary(id, name, sex, salary)`. Swap `'m'` ↔ `'f'` in one `UPDATE`, no temp table.
- [ ] **T1.6.3 Delete Duplicate Emails** · *DELETE … USING / subquery* · [LeetCode 196](https://leetcode.com/problems/delete-duplicate-emails/)
  Mini schema: `Person(id, email)`. Delete duplicates, keeping the row with the smallest `id` for each email.
- [ ] **T1.6.4 StockPilot: apply a price increase** · *UPDATE … FROM* · StockPilot
  Increase `price_cents` by 10% (rounded to whole cents) for all products of one supplier, identified by supplier **name**, in one statement. Do it inside `BEGIN … ROLLBACK` first and check the row count.
- [ ] **T1.6.5 Money types experiment** · *Data types* · no schema
  Show with `SELECT` that `0.1::float8 + 0.2::float8 <> 0.3` while `0.1::numeric + 0.2::numeric = 0.3`, and write in a comment which type (and why integer cents) you will use for money.

**Must be able to do / explain**
- [ ] Choose the right type for ids, money, names, timestamps and flags.
- [ ] Choose `ON DELETE RESTRICT/CASCADE/SET NULL` deliberately.
- [ ] Explain identity columns vs `serial`.
- [ ] Run risky DML inside a transaction and verify before `COMMIT`.

**Self-check questions**
1. Why not use `float` for money?
2. What is the difference between `PRIMARY KEY` and `UNIQUE NOT NULL`?
3. Does a UNIQUE constraint allow multiple NULLs in PostgreSQL?
4. `DELETE FROM t` vs `TRUNCATE t`?
5. When would you use `ON DELETE CASCADE`, and when is it dangerous?
6. Is DDL transactional in PostgreSQL?
7. `varchar(255)` vs `text` in PostgreSQL?

---

**Answers**
1. Binary floating point cannot represent most decimal fractions exactly, so sums drift (0.1 + 0.2 ≠ 0.3). Use `numeric` or integer minor units (cents).
2. Functionally similar, but a table has only one primary key; it is the default FK target and documents identity. PK also implies NOT NULL on all columns.
3. Yes by default (NULLs are not equal). PostgreSQL 15+ supports `UNIQUE NULLS NOT DISTINCT` to allow only one NULL.
4. `DELETE` removes rows one by one (fires row triggers, can have WHERE, leaves dead tuples); `TRUNCATE` drops all rows at once, is much faster, needs a stronger lock and resets storage.
5. For child rows that make no sense without the parent (order_items of an order). Dangerous when a delete on a central table silently wipes large amounts of related data (e.g. deleting a user deletes financial history).
6. Yes — `CREATE/ALTER/DROP` can be rolled back (a few exceptions like `CREATE INDEX CONCURRENTLY`).
7. Same storage and performance; `varchar(n)` only adds a length check. Use `text` plus a `CHECK` if you need a limit.

---

## Module 1.7 — Normalization, schema design, views

**Estimated: 6 h**

**Topics:** functional dependencies; keys (candidate, primary, surrogate vs
natural); 1NF, 2NF, 3NF (and a glance at BCNF); update/insert/delete
anomalies; when to denormalize on purpose; modelling one-to-many,
many-to-many (junction tables), hierarchies (adjacency list); naming
conventions; views, updatable views, `WITH CHECK OPTION`.

**Lessons**
- [ ] **L1.7.1 Normalization** — *Database Design – 2nd Edition* (Adrienne Watt, BCcampus open textbook, free online): Ch.8 The Entity Relationship Data Model, Ch.9 Integrity Rules and Constraints, Ch.11 Functional Dependencies, Ch.12 Normalization.
- [ ] **L1.7.2 Views** — PostgreSQL Tutorial §3.2 Views; SQL Commands → `CREATE VIEW` (read "Updatable Views" and `WITH CHECK OPTION`).
- [ ] **L1.7.3 Schema design practice** — Compare the StockPilot and LedgerBase practice schemas above and write down, for each table, its key and one design decision (e.g. why `stock_movements` exists instead of only `current_stock`).

**Tasks**
- [ ] **T1.7.1 Normalize an orders spreadsheet** · *1NF → 3NF* · custom
  Given one wide table `sales_sheet(order_no, order_date, customer_name, customer_phone, customer_city, product_codes (comma list), product_names (comma list), unit_prices (comma list), qtys (comma list), salesperson_name, salesperson_office)`, list every anomaly, then write the 3NF DDL. Output: DDL + a short note per NF step.
- [ ] **T1.7.2 CarePoint schema from requirements** · *Schema design* · CarePoint
  Requirements: doctors have several specialties; patients can have several contacts; an appointment belongs to one doctor and one patient and has a status history. Extend the CarePoint schema accordingly (DDL with keys and constraints) and draw the ERD (text/mermaid is fine).
- [ ] **T1.7.3 Spot the violation** · *Normal forms* · custom
  For each table, name the highest normal form it satisfies and why: (a) `enrolment(student_id, course_id, course_title, grade)` with PK (student_id, course_id); (b) `employee(id, name, dept_id, dept_name)`; (c) `order(id, tags)` where tags = `'a,b,c'`.
- [ ] **T1.7.4 StockPilot: low-stock view** · *Views* · StockPilot
  Create view `v_low_stock` (sku, name, category name, supplier name, shortage). Then try `UPDATE v_low_stock SET …` and explain why it fails or works; create a simple single-table updatable view with `WITH CHECK OPTION` and show the check rejecting a row.
- [ ] **T1.7.5 LedgerBase design question** · *Schema design* · LedgerBase
  In a comment, explain why the schema uses `journal_entries` + `journal_lines` instead of `debit_account_id, credit_account_id, amount` on one table. Give one real transaction that the one-table design cannot represent.

**Must be able to do / explain**
- [ ] State 1NF, 2NF and 3NF in one sentence each with an example violation.
- [ ] Design a many-to-many relationship and a self-referencing hierarchy.
- [ ] Explain when denormalization is a good idea (and what it costs).
- [ ] Explain what a view is (stored query), and when a view is updatable.

**Self-check questions**
1. Define 1NF, 2NF and 3NF.
2. What anomalies does normalization prevent?
3. Surrogate vs natural key — pros and cons?
4. Give a case where you would denormalize on purpose.
5. Does a (non-materialized) view store data? Does it make queries faster?
6. How do you model a many-to-many relationship?

---

**Answers**
1. 1NF: atomic values, no repeating groups. 2NF: 1NF and no non-key column depends on only part of a composite key. 3NF: 2NF and no non-key column depends on another non-key column (no transitive dependencies).
2. Update anomalies (same fact stored twice, updated in one place only), insert anomalies (can't store a fact without an unrelated one), delete anomalies (deleting one fact loses another).
3. Surrogate (identity/UUID): stable, small, never changes, but meaningless and needs a separate unique constraint on the natural key. Natural: meaningful, prevents duplicates by itself, but can change and be wide.
4. A read-heavy report or cache column such as `products.current_stock` derived from `stock_movements`, or a read model — accepted because you control how it is kept in sync.
5. No, it stores only the query text; it is expanded into the query at plan time, so it is not faster by itself. Materialized views (Module 2.9) store data.
6. A junction table with two FKs and a composite PK/unique constraint, e.g. `document_tags(document_id, tag_id)`.

---

# PART 2 — Advanced SQL + PostgreSQL (~55 h)

Before starting Part 2, fill the StockPilot, WareFlow and FleetTrack
databases with volume (100k–1M rows) using `generate_series()` — plans and
locking only become interesting with real row counts.

## Module 2.1 — CTEs and recursive CTEs

**Estimated: 5 h**

**Topics:** `WITH` for readability; CTE materialization (`MATERIALIZED` /
`NOT MATERIALIZED`, PostgreSQL 12+ inlining); data-modifying CTEs;
`WITH RECURSIVE` (anchor + recursive part, termination); depth and path
tracking; cycle detection (`CYCLE` clause, PostgreSQL 14+); `SEARCH
DEPTH/BREADTH FIRST`.

**Lessons**
- [ ] **L2.1.1 WITH queries** — Ch.7 §7.8 WITH Queries (Common Table Expressions): §7.8.1 SELECT in WITH, §7.8.2 Recursive Queries (incl. search order and cycle detection), §7.8.3 Common Table Expression Materialization, §7.8.4 Data-Modifying Statements in WITH.
- [ ] **L2.1.2 Practice** — pgexercises.com → **Recursive** (all).

**Tasks**
- [ ] **T2.1.1 StockPilot: category tree** · *Recursive CTE* · StockPilot
  Return every category with `depth` (root = 0) and `path` (e.g. `Electronics > Phones > Android`), ordered so that children come right after their parent.
- [ ] **T2.1.2 StockPilot: product count per category subtree** · *Recursive CTE + aggregation* · StockPilot
  For each category, count products in that category **and all its descendants**. Output: `category_id, name, total_products`.
- [ ] **T2.1.3 PeopleOps: management chain** · *Recursive CTE upward* · PeopleOps
  For a given employee id, return the chain up to the top manager: `level, employee_id, name`. Then insert a cycle (A manages B, B manages A) and make the query terminate using the `CYCLE` clause.
- [ ] **T2.1.4 Refactor with CTEs** · *Readability* · QuickServe
  Write "daily revenue per cashier for completed receipts, only cashiers above that day's average" first as nested subqueries, then as a chain of named CTEs. Compare `EXPLAIN` of both.
- [ ] **T2.1.5 Archive with a data-modifying CTE** · *DML in WITH* · FleetTrack
  In one statement, move `outbox` rows sent more than 7 days ago into `outbox_archive` (same columns) and return the number of rows moved.

**Must be able to do / explain**
- [ ] Write a recursive CTE for a tree both downward and upward.
- [ ] Explain how recursion terminates and how to protect against cycles.
- [ ] Explain when PostgreSQL inlines a CTE and when it materializes it.

**Self-check questions**
1. What are the two parts of a recursive CTE?
2. How does a recursive CTE stop?
3. Is a CTE an optimization fence in PostgreSQL 17?
4. When would you force `MATERIALIZED`?
5. `UNION` vs `UNION ALL` in a recursive CTE?
6. Give two non-tree uses of recursive CTEs.

---

**Answers**
1. The non-recursive anchor term and the recursive term (which references the CTE), joined by `UNION [ALL]`.
2. When the recursive term returns no new rows.
3. Not by default: since PG 12, a non-recursive, side-effect-free CTE referenced once is inlined. Referenced more than once, or marked `MATERIALIZED`, it is computed once.
4. When the CTE is expensive and used several times, or to stop the planner pushing a condition into it (a deliberate fence).
5. `UNION` removes duplicates each step (can stop some cycles, costs more); `UNION ALL` keeps everything and is the usual choice with explicit cycle protection.
6. Generating series of dates/numbers, walking graphs (routes, transfer chains), bill-of-materials explosion.

---

## Module 2.2 — Window functions

**Estimated: 8 h**

**Topics:** `OVER (PARTITION BY … ORDER BY …)`; window vs `GROUP BY`
(rows are kept); ranking: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`;
offsets: `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`;
aggregates as windows (running totals, moving averages, share of total);
frames: `ROWS` vs `RANGE` vs `GROUPS`, `UNBOUNDED PRECEDING`, default frame
trap with `LAST_VALUE`; named windows (`WINDOW w AS …`); top-N per group;
gaps-and-islands.

**Lessons**
- [ ] **L2.2.1 Window basics and ranking** — Tutorial §3.5 Window Functions; §9.22 Window Functions (table of functions).
- [ ] **L2.2.2 Frames** — §4.2.8 Window Function Calls (frame clause: ROWS/RANGE/GROUPS, frame_start/frame_end, EXCLUDE). pgexercises.com → **Aggregates**: the window-function exercises (rank, running totals, NTILE).

**Tasks — ranking and offsets**
- [ ] **T2.2.1 Rank Scores** · *DENSE_RANK* · [LeetCode 178](https://leetcode.com/problems/rank-scores/)
  Mini schema: `Scores(id, score)`. Return `score, rank` — equal scores share a rank, no gaps.
- [ ] **T2.2.2 Rising Temperature (both ways)** · *Self-join vs LAG* · [LeetCode 197](https://leetcode.com/problems/rising-temperature/)
  Mini schema: `Weather(id, recordDate, temperature)`. Ids of days warmer than the previous **calendar** day. Solve with a self-join, then with `LAG`; explain what `LAG` gets wrong if a date is missing, and fix it.
- [ ] **T2.2.3 Department Top Three Salaries** · *DENSE_RANK per partition* · [LeetCode 185](https://leetcode.com/problems/department-top-three-salaries/)
  Mini schema: `Employee(id, name, salary, departmentId)`, `Department(id, name)`. Employees whose salary is in the top 3 distinct salaries of their department.
- [ ] **T2.2.4 DocuVault: latest version per document** · *ROW_NUMBER top-1 per group* · DocuVault
  Return exactly one row per document: its latest version (`document_id, version_number, s3_key, created_at`). Then do the same with `DISTINCT ON` and compare.
- [ ] **T2.2.5 Consecutive Numbers** · *LAG/LEAD or gaps-and-islands* · [LeetCode 180](https://leetcode.com/problems/consecutive-numbers/)
  Mini schema: `Logs(id, num)`. Numbers appearing at least 3 times in a row (by `id`).

**Tasks — running totals and frames**
- [ ] **T2.2.6 QuickServe: running total of daily sales** · *SUM OVER ORDER BY* · QuickServe
  Per day: `day, revenue_cents, running_total_cents`, plus `pct_of_month` (day's share of its month's revenue).
- [ ] **T2.2.7 QuickServe: 7-day moving average** · *Frame ROWS BETWEEN* · QuickServe
  Per day: revenue and 7-day trailing average. Then show how `ROWS` and `RANGE` differ when some days have no sales, and pick the correct one.
- [ ] **T2.2.8 FleetTrack: time between status transitions** · *LAG + aggregation* · FleetTrack
  For each delivery, the time between consecutive `delivery_events`; then the average gap per `to_status`.
- [ ] **T2.2.9 LedgerBase: running account balance** · *Running SUM per partition* · LedgerBase
  For one account: each journal line with `debit_cents, credit_cents, balance_after` in time order.
- [ ] **T2.2.10 (OPTIONAL, Hard) Human Traffic of Stadium** · *Gaps-and-islands* · [LeetCode 601](https://leetcode.com/problems/human-traffic-of-stadium/)
  Mini schema: `Stadium(id, visit_date, people)`. Rows in runs of ≥ 3 consecutive ids with `people ≥ 100`, ordered by `visit_date`.

**Must be able to do / explain**
- [ ] Explain the difference between `ROW_NUMBER`, `RANK` and `DENSE_RANK` on ties.
- [ ] Write top-N-per-group three ways (window, `DISTINCT ON`, `LATERAL` — last one in 2.3).
- [ ] Explain the default frame and why `LAST_VALUE` "doesn't work" without a frame clause.
- [ ] Solve a gaps-and-islands problem.

**Self-check questions**
1. How is a window function different from `GROUP BY`?
2. Can you filter on a window function in `WHERE`? What do you do instead?
3. What is the default frame when `ORDER BY` is present?
4. `ROWS` vs `RANGE`?
5. `RANK` vs `DENSE_RANK` for salaries 100, 100, 90?
6. How do you compute "percent of total" per row?
7. What is the gaps-and-islands technique?

---

**Answers**
1. Window functions compute over a set of rows related to the current row but do not collapse rows; every input row stays in the output.
2. No — window functions are evaluated after `WHERE`/`GROUP BY`/`HAVING`. Wrap the query in a subquery/CTE and filter outside (or use `QUALIFY`-style logic in a CTE; PostgreSQL has no `QUALIFY`).
3. `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — including peer rows with the same ORDER BY value.
4. `ROWS` counts physical rows; `RANGE` works on values of the ORDER BY key (peers with equal values are included together; with offsets it means value distance, e.g. `INTERVAL '6 days'`).
5. RANK: 1, 1, 3. DENSE_RANK: 1, 1, 2.
6. `value / SUM(value) OVER ()` (or `OVER (PARTITION BY group)` for share of group), cast to numeric.
7. Give each row `value − ROW_NUMBER()` (or `date − ROW_NUMBER() * interval`); consecutive rows share the same difference, so grouping by it finds each "island".

---

## Module 2.3 — LATERAL, ON CONFLICT, RETURNING

**Estimated: 3 h**

**Topics:** `LATERAL` subqueries (per-row subquery that can reference
earlier FROM items; top-N per group); `INSERT … ON CONFLICT DO NOTHING /
DO UPDATE` (upsert, `EXCLUDED`, conflict target must match a unique
index); `RETURNING` on INSERT/UPDATE/DELETE; `MERGE` (PostgreSQL 15+,
`RETURNING` in 17); race-safety of upsert vs "SELECT then INSERT".

**Lessons**
- [ ] **L2.3.1 LATERAL** — Ch.7 §7.2.1.5 LATERAL Subqueries.
- [ ] **L2.3.2 Upsert and RETURNING** — SQL Commands → `INSERT` (section "ON CONFLICT Clause"); Ch.6 §6.4 Returning Data from Modified Rows; SQL Commands → `MERGE`.

**Tasks**
- [ ] **T2.3.1 The Most Recent Three Orders** · *LATERAL top-N* · [LeetCode 1532](https://leetcode.com/problems/the-most-recent-three-orders/) (premium; mini schema is enough)
  Mini schema: `Customers(customer_id, name)`, `Orders(order_id, order_date, customer_id, cost)`. Each customer's 3 most recent orders: `customer_name, customer_id, order_id, order_date`. Solve with `LATERAL`, then with `ROW_NUMBER`.
- [ ] **T2.3.2 StockPilot: top 3 best-selling products per category** · *LATERAL* · StockPilot
  For every category, its 3 products with the highest units sold (categories with fewer products show fewer rows; categories with none are still listed once with NULLs).
- [ ] **T2.3.3 PayFlow: idempotent payment create** · *ON CONFLICT DO NOTHING RETURNING* · PayFlow
  With a unique index on `idempotency_key`, write one statement that inserts a payment intent or does nothing if the key exists, and returns the row id **only when inserted**. Then a second statement that returns the existing row in the duplicate case. Test from two psql sessions at the same time.
- [ ] **T2.3.4 WareFlow: stock upsert** · *ON CONFLICT DO UPDATE* · WareFlow
  Apply a movement `(warehouse_id, product_id, delta)`: insert into `stock_levels` if missing, else add `delta` to `qty`, and return the new `qty`. Reject (with a `CHECK`) any result below zero.
- [ ] **T2.3.5 LedgerBase: MERGE a payments file** · *MERGE* · LedgerBase
  Given a staging table `payments_import(invoice_id, amount_cents, received_at, external_ref)`, use `MERGE` to insert new payments and update amounts of already-imported ones (matched by `external_ref`).

**Must be able to do / explain**
- [ ] Explain why "SELECT, then INSERT if missing" is a race and upsert is not.
- [ ] Write `ON CONFLICT` with a correct conflict target and `EXCLUDED`.
- [ ] Use `LATERAL` for top-N per group.

**Self-check questions**
1. What does `LATERAL` allow that a normal subquery in FROM doesn't?
2. What is `EXCLUDED` in `ON CONFLICT DO UPDATE`?
3. Why does `ON CONFLICT` need a unique index or constraint?
4. What does `ON CONFLICT DO NOTHING RETURNING id` return on conflict?
5. `MERGE` vs `INSERT … ON CONFLICT`?

---

**Answers**
1. It can reference columns of FROM items that appear before it, so it runs once per outer row (like a correlated subquery that returns several rows/columns).
2. The row that was proposed for insertion (the one that conflicted).
3. The conflict is detected by the unique index during insertion; without one there is nothing to "conflict" with.
4. Nothing — zero rows. You must query the existing row separately (or use a `DO UPDATE SET col = col` trick, which has side effects).
5. `ON CONFLICT` is an atomic, concurrency-safe upsert based on a unique index. `MERGE` is the SQL-standard, more general statement (multiple WHEN branches, deletes) but under concurrency it can still fail with unique violations — it is not a guaranteed race-free upsert.

---

## Module 2.4 — JSONB and arrays

**Estimated: 4 h**

**Topics:** `json` vs `jsonb`; operators `->`, `->>`, `#>`, `@>`, `?`;
`jsonb_build_object`, `jsonb_agg`, `jsonb_array_elements`,
`jsonb_to_recordset`; SQL/JSON path (`jsonb_path_query`); generated
columns extracted from JSONB; GIN indexes (`jsonb_ops` vs
`jsonb_path_ops`); arrays: literals, `ANY`, `array_agg`, `unnest`,
`&&`/`@>`; when JSONB is the wrong choice (relational data you filter/join on).

**Lessons**
- [ ] **L2.4.1 JSON types and functions** — Ch.8 §8.14 JSON Types (incl. §8.14.3 jsonb Containment and Existence, §8.14.4 jsonb Indexing); Ch.9 §9.16 JSON Functions and Operators.
- [ ] **L2.4.2 Arrays** — Ch.8 §8.15 Arrays; Ch.9 §9.19 Array Functions and Operators.

**Tasks**
- [ ] **T2.4.1 FleetTrack: query outbox payloads** · *JSONB operators* · FleetTrack
  Payload example: `{"delivery_id": 17, "driver_id": 4, "status": "picked_up", "meta": {"lat": 41.3, "lon": 69.2}}`. Return unsent `DeliveryStatusChanged` events for driver 4, with `delivery_id` and `lat/lon` as typed columns.
- [ ] **T2.4.2 FleetTrack: index the containment query** · *GIN* · FleetTrack
  With 500k outbox rows, compare `EXPLAIN ANALYZE` of `payload @> '{"driver_id": 4}'` with no index, a `jsonb_ops` GIN and a `jsonb_path_ops` GIN. Record sizes (`pg_relation_size`) and timings.
- [ ] **T2.4.3 PayFlow: generated column for dedup** · *Generated column from JSONB* · PayFlow
  Add a stored generated column `provider_event_id` extracted from `payload->>'id'` with a unique constraint, and show that inserting the same webhook twice fails.
- [ ] **T2.4.4 StockPilot: order as JSON** · *jsonb_build_object + jsonb_agg* · StockPilot
  For one order return a single JSON document: `{id, status, created_at, items: [{sku, name, qty, unit_price_cents}], total_cents}`.
- [ ] **T2.4.5 DocuVault: tags as array vs junction table** · *Arrays* · DocuVault
  Build `document_tags` into `text[]` per document with `array_agg`, find documents having **both** tags `'contract'` and `'2025'` using array operators, then write the same with the junction table. Write in a comment which design you would keep and why.

**Must be able to do / explain**
- [ ] Choose `jsonb` over `json` and explain why.
- [ ] Index JSONB for containment queries.
- [ ] Say when data should be columns, not JSON.

**Self-check questions**
1. `json` vs `jsonb`?
2. `->` vs `->>`?
3. Which queries can a GIN `jsonb_path_ops` index support?
4. Why not store everything in one JSONB column?
5. How do you turn a JSON array into rows?

---

**Answers**
1. `json` stores the raw text (keeps whitespace, key order, duplicates) and re-parses on each use; `jsonb` stores a decomposed binary form — faster to query, indexable, no duplicate keys.
2. `->` returns `jsonb`; `->>` returns `text`.
3. Containment (`@>`) and jsonpath match operators (`@?`, `@@`); not key-existence (`?`) — that needs the default `jsonb_ops`.
4. You lose types, constraints, foreign keys, planner statistics and simple indexing; queries become harder and slower. Use JSONB for truly variable/sparse attributes or raw payloads.
5. `jsonb_array_elements()` (or `jsonb_to_recordset()` for typed columns) in FROM / LATERAL.

---

## Module 2.5 — Indexes

**Estimated: 7 h**

**Topics:** how a B-tree works (leaf nodes, tree traversal, leaf chain);
index scan vs index-only scan vs bitmap scan vs seq scan; selectivity;
**composite index column order** (equality first, then range; leftmost
prefix); indexes for `ORDER BY` / top-N; partial indexes; expression
indexes; `INCLUDE` (covering) and the visibility map; unique indexes;
`GIN` (arrays, JSONB, full text, `pg_trgm`), `GiST` (ranges,
geometry, exclusion constraints), `BRIN` (huge append-only tables);
`CREATE INDEX CONCURRENTLY`; cost of indexes on writes; unused-index detection.

**Lessons**
- [ ] **L2.5.1 How indexes work** — Use The Index, Luke!: "Anatomy of an SQL Index" and "The Where Clause" (sections: The Equality Operator, Concatenated Indexes, Functions, Partial Indexes, Searching for Ranges).
- [ ] **L2.5.2 PostgreSQL indexes** — Ch.11 Indexes: §11.1 Introduction, §11.2 Index Types, §11.3 Multicolumn Indexes, §11.4 Indexes and ORDER BY, §11.5 Combining Multiple Indexes, §11.6 Unique Indexes, §11.7 Indexes on Expressions, §11.8 Partial Indexes, §11.9 Index-Only Scans and Covering Indexes.
- [ ] **L2.5.3 Beyond B-tree** — Use The Index, Luke!: "Sorting and Grouping", "Partial Results" (top-N, keyset paging). PostgreSQL docs → "Built-in Index Access Methods": GiST, GIN, BRIN introductions; Appendix F → `pg_trgm`, `btree_gist`.

**Tasks**
- [ ] **T2.5.1 StockPilot: composite index order** · *Composite index* · StockPilot (1M orders)
  Query: orders with `status = 'pending'` created in the last 7 days, newest first, limit 50. Try indexes `(created_at)`, `(status)`, `(created_at, status)`, `(status, created_at)`. Table of `EXPLAIN (ANALYZE, BUFFERS)` results; explain the winner.
- [ ] **T2.5.2 StockPilot: partial + expression indexes** · *Partial / expression* · StockPilot
  (a) Index only products below reorder level (hint: you can't compare two columns in a partial predicate directly — find a way or explain why not). (b) Case-insensitive login lookup `lower(email) = lower($1)` using an index. Show the plans.
- [ ] **T2.5.3 Covering index** · *INCLUDE / index-only scan* · StockPilot
  Make `SELECT sku, price_cents FROM products WHERE category_id = $1` an index-only scan. Show `Heap Fetches` before and after `VACUUM`, and explain the visibility map.
- [ ] **T2.5.4 QuickServe: leading-wildcard search** · *GIN + pg_trgm* · QuickServe (200k products)
  `name ILIKE '%cola%'`: compare seq scan, B-tree (useless — show it), and a trigram GIN index.
- [ ] **T2.5.5 CarePoint: no double booking** · *GiST exclusion constraint* · CarePoint
  Add an `EXCLUDE USING gist` constraint so a doctor cannot have two non-cancelled appointments with overlapping `tstzrange(slot_start, slot_end)`. Prove it by inserting an overlap. (Needs `btree_gist`.)
- [ ] **T2.5.6 WareFlow: BRIN on an append-only table** · *BRIN* · WareFlow (5M stock_movements)
  Compare size and query time of B-tree vs BRIN on `created_at` for "movements in one day". Then shuffle `created_at` physical order (insert randomly) and show BRIN stops helping — explain why.

**Must be able to do / explain**
- [ ] Explain B-tree structure and why a leading-column rule exists.
- [ ] Pick column order for a composite index from the query.
- [ ] Choose B-tree / GIN / GiST / BRIN for a given workload.
- [ ] Explain the write cost of indexes and find unused ones (`pg_stat_user_indexes`).

**Self-check questions**
1. For `WHERE a = ? AND b > ?`, which composite order is better: `(a, b)` or `(b, a)`?
2. When does PostgreSQL ignore an existing index?
3. What is an index-only scan and what does it need?
4. What is a partial index? Give a real example.
5. When would you use GIN, GiST and BRIN?
6. Why can too many indexes hurt?
7. What does `CREATE INDEX CONCURRENTLY` change?
8. Why doesn't `WHERE lower(email) = …` use an index on `email`?

---

**Answers**
1. `(a, b)`: equality column first, so the range on `b` is a contiguous slice of the index. With `(b, a)` the range scan on `b` must filter `a` across many entries.
2. When the planner estimates a seq scan is cheaper (low selectivity, small table), when a function/cast is applied to the column, when the leading column isn't used, or when statistics are wrong.
3. Answering a query from the index alone without visiting the table. Needs all referenced columns in the index (key or `INCLUDE`) and pages marked all-visible in the visibility map (kept by VACUUM).
4. An index over a subset of rows defined by a `WHERE`, e.g. `CREATE INDEX … ON outbox (created_at) WHERE sent_at IS NULL` — tiny, and exactly what the relay polls.
5. GIN: many values per row (arrays, JSONB, full-text, trigrams). GiST: ranges/geometric/nearest-neighbour and exclusion constraints. BRIN: very large tables whose values correlate with physical order (append-only timestamps).
6. Each INSERT/UPDATE must maintain every index (write amplification, WAL, bloat, less room in cache); they can also block HOT updates.
7. It builds the index without blocking writes (takes longer, two table scans, can't run in a transaction, may leave an INVALID index on failure).
8. The index stores `email` values, not `lower(email)`; you need an expression index on `lower(email)` (or `citext`).

---

## Module 2.6 — EXPLAIN ANALYZE and query tuning

**Estimated: 5 h**

**Topics:** reading plans (nodes, cost, rows, width, loops); `EXPLAIN
(ANALYZE, BUFFERS)`; estimated vs actual rows; scan types; join algorithms
(nested loop, hash join, merge join) and when each is chosen; sorts and
`work_mem` spills; statistics (`ANALYZE`, `pg_stats`, extended statistics);
`pg_stat_statements` for finding the slow queries; keyset pagination;
common anti-patterns (functions on indexed columns, `OR` across columns,
implicit casts, N+1).

**Lessons**
- [ ] **L2.6.1 Using EXPLAIN** — Ch.14 Performance Tips: §14.1 Using EXPLAIN (all subsections), §14.2 Statistics Used by the Planner.
- [ ] **L2.6.2 Plans and joins** — Use The Index, Luke!: "The Join Operation" (Nested Loops, Hash Join, Sort Merge) and Appendix "Execution Plans → PostgreSQL". Tool: https://explain.depesz.com or https://explain.dalibo.com for visualising plans.
- [ ] **L2.6.3 Finding slow queries** — Appendix F → `pg_stat_statements` (enable it in the container with `shared_preload_libraries`).

**Tasks**
- [ ] **T2.6.1 StockPilot: the low-stock query** · *Plan reading* · StockPilot (1M products)
  Run `EXPLAIN (ANALYZE, BUFFERS)` on T1.1.1, annotate every node in comments, try one improvement, and state at what table size the change starts to matter.
- [ ] **T2.6.2 WareFlow: OFFSET vs keyset pagination** · *Keyset (seek) pagination* · WareFlow
  Paginate stock of one warehouse ordered by `(product_id)`: page 1, 100 and 10 000 with OFFSET vs keyset (`WHERE product_id > $last`). Table of timings and buffers.
- [ ] **T2.6.3 Join algorithm hunt** · *Join strategies* · StockPilot
  Write three queries (or change filters/`work_mem`) so the planner picks a nested loop, a hash join and a merge join. Explain from the plan why each was chosen.
- [ ] **T2.6.4 Bad estimates** · *Statistics* · PeopleOps
  Create correlated columns (e.g. `department` and `city`), show a bad row estimate, fix it with `CREATE STATISTICS … (dependencies)` + `ANALYZE`, and show the corrected estimate.
- [ ] **T2.6.5 FleetTrack: live join vs read model** · *Plan comparison* · FleetTrack
  Write the dispatcher dashboard (latest status per delivery with driver name) as a live query over `delivery_events`, then as a query over `delivery_view`. Compare plans and explain the trade-off (freshness vs cost).

**Must be able to do / explain**
- [ ] Read a plan bottom-up and find the expensive node.
- [ ] Spot a misestimate (estimated vs actual rows) and name likely causes.
- [ ] Explain when each join algorithm wins.
- [ ] Find top queries by total time with `pg_stat_statements`.

**Self-check questions**
1. `EXPLAIN` vs `EXPLAIN ANALYZE`? Is `EXPLAIN ANALYZE` safe on an `UPDATE`?
2. What does `BUFFERS` show?
3. When is a nested loop join a good choice?
4. What happens when a sort doesn't fit in `work_mem`?
5. Why can a query be fast in dev and slow in prod?
6. What is keyset pagination and what does it require?

---

**Answers**
1. `EXPLAIN` shows the estimated plan; `ANALYZE` actually runs the query and adds real times/rows. On `UPDATE`/`DELETE` it really modifies data — wrap it in `BEGIN … ROLLBACK`.
2. Shared buffer hits (from cache) and reads (from disk/OS), plus dirtied/written blocks — the real I/O work of each node.
3. When the outer side is small and the inner side has an index on the join key (e.g. fetch 50 orders and their items).
4. It spills to disk ("external merge Disk: …"), which is much slower. Raise `work_mem` for that query or reduce rows sorted (index).
5. Different data volume and distribution, stale statistics, different settings (`work_mem`, `random_page_cost`), cold cache, concurrency/locks.
6. Paging by "where key > last seen key ORDER BY key LIMIT n" instead of OFFSET. Needs a unique, indexed, stable sort key (often a composite like `(created_at, id)`); you can't jump to arbitrary page numbers.

---

## Module 2.7 — Transactions, isolation levels, anomalies, MVCC

**Estimated: 6 h**

**Topics:** ACID; `BEGIN/COMMIT/ROLLBACK`, savepoints; anomalies: dirty
read, non-repeatable read, phantom read, lost update, **write skew**,
serialization anomaly; PostgreSQL levels: Read Committed (default),
Repeatable Read (snapshot isolation), Serializable (SSI) — and that Read
Uncommitted behaves as Read Committed; retrying serialization failures
(SQLSTATE `40001`); MVCC: tuple versions, `xmin`/`xmax`, snapshots,
why readers don't block writers.

**Lessons**
- [ ] **L2.7.1 Transactions** — Tutorial §3.4 Transactions; SQL Commands → `BEGIN`, `SAVEPOINT`, `SET TRANSACTION`.
- [ ] **L2.7.2 Isolation** — Ch.13 Concurrency Control: §13.1 Introduction, §13.2 Transaction Isolation (§13.2.1 Read Committed, §13.2.2 Repeatable Read, §13.2.3 Serializable) — read the examples in each section.
- [ ] **L2.7.3 MVCC internals** — §5.6 System Columns (`xmin`, `xmax`, `ctid`); Ch.13 §13.5 Serialization Failure Handling. Optional: "Designing Data-Intensive Applications" (Kleppmann) Ch.7 Transactions.

All tasks use **two psql sessions** side by side (A and B). Write the
exact interleaving as numbered comments in the file.

**Tasks**
- [ ] **T2.7.1 Lost update on stock** · *Read Committed anomaly* · StockPilot
  Two sessions read `current_stock = 10`, each computes `10 − 3` in the application and writes it back. Show the lost update, then fix it two ways: an atomic `UPDATE … SET current_stock = current_stock − 3 WHERE … AND current_stock >= 3`, and `SELECT … FOR UPDATE`.
- [ ] **T2.7.2 Non-repeatable read vs Repeatable Read** · *Snapshots* · LedgerBase
  In session A read an account balance twice inside one transaction while B commits a new journal line in between. Show the difference between Read Committed and Repeatable Read.
- [ ] **T2.7.3 Write skew** · *Repeatable Read vs Serializable* · PeopleOps
  Rule: at least one person in department X must not be on leave on a given day. Two employees request leave for the same day concurrently; each transaction checks the rule and inserts. Show that Repeatable Read lets both through, Serializable aborts one with `40001`, and write the retry loop as pseudo-code.
- [ ] **T2.7.4 Watch MVCC** · *xmin/xmax/ctid* · any table
  Select `xmin, xmax, ctid, *` for one row, update it in session A without committing, read it in B, commit, read again. Explain every change in the system columns.
- [ ] **T2.7.5 Savepoints** · *Partial rollback* · StockPilot
  Insert an order and 3 items in one transaction where the 3rd item violates a constraint; use a savepoint so the order and first 2 items survive. Explain why an error without a savepoint makes the whole transaction unusable ("current transaction is aborted").

**Must be able to do / explain**
- [ ] Name each anomaly and the lowest level that prevents it in PostgreSQL.
- [ ] Explain snapshot isolation and why it still allows write skew.
- [ ] Explain why Serializable needs application retries.
- [ ] Explain MVCC in 3 sentences.

**Self-check questions**
1. What is the default isolation level in PostgreSQL?
2. Which anomalies can happen at Read Committed?
3. What is write skew? Give an example.
4. What does SSI do differently from locking-based serializable?
5. What must the application do on SQLSTATE 40001?
6. Why don't readers block writers in PostgreSQL?
7. What is a lost update and how do you prevent it?

---

**Answers**
1. Read Committed.
2. Non-repeatable reads, phantom reads, lost updates (with read-modify-write in the app), write skew. Dirty reads never happen in PostgreSQL.
3. Two transactions read an overlapping set of data, each makes a decision based on it and writes to *different* rows, together breaking a rule neither broke alone (two doctors both go off call; two leave requests leaving nobody on duty).
4. It runs transactions on snapshots without extra blocking, tracks read/write dependencies (predicate "SIRead" locks), and aborts one transaction when a dangerous cycle is detected.
5. Roll back and retry the whole transaction (from the beginning, including reads), usually with a limit and backoff.
6. MVCC: an update creates a new row version; readers see the version valid for their snapshot, so they need no lock on the row being written.
7. Two read-modify-write cycles overwrite each other. Prevent with an atomic `UPDATE … SET x = x − n`, `SELECT … FOR UPDATE`, optimistic version checks, or Repeatable Read/Serializable with retry.

---

## Module 2.8 — Locking: FOR UPDATE, SKIP LOCKED, deadlocks

**Estimated: 4 h**

**Topics:** row-level locks (`FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR
SHARE`, `FOR KEY SHARE`); `NOWAIT` and `SKIP LOCKED` (job queues);
table-level lock modes and which statements take them (why `ALTER TABLE`
can stall production); deadlocks and lock ordering; `lock_timeout`,
`statement_timeout`, `idle_in_transaction_session_timeout`; advisory
locks; inspecting `pg_locks` and `pg_stat_activity`.

**Lessons**
- [ ] **L2.8.1 Explicit locking** — Ch.13 §13.3 Explicit Locking: §13.3.1 Table-Level Locks (read the conflict table), §13.3.2 Row-Level Locks, §13.3.4 Deadlocks, §13.3.5 Advisory Locks.
- [ ] **L2.8.2 The locking clause** — SQL Commands → `SELECT`, section "The Locking Clause" (NOWAIT, SKIP LOCKED); Ch.20 Server Configuration → Client Connection Defaults (`lock_timeout`, `statement_timeout`, `idle_in_transaction_session_timeout`); Ch.27 Monitoring → `pg_stat_activity`, `pg_locks`.

**Tasks**
- [ ] **T2.8.1 WareFlow: reserve stock safely** · *SELECT … FOR UPDATE* · WareFlow
  Write the transaction that reserves `qty` of a product in a warehouse only if enough is available, safe under concurrency. Test with two sessions reserving the last units at once.
- [ ] **T2.8.2 FleetTrack: outbox relay with SKIP LOCKED** · *Job queue pattern* · FleetTrack
  Two worker sessions each claim a batch of 100 unsent outbox rows, oldest first, without ever taking the same row, mark them sent and commit. Show what happens with `FOR UPDATE` alone vs with `SKIP LOCKED`.
- [ ] **T2.8.3 WareFlow: deadlock and its fix** · *Lock ordering* · WareFlow
  Two transfers update the same two `stock_levels` rows in opposite order. Reproduce `deadlock detected`, read the server log message, then fix it by locking rows in a consistent order (e.g. by id).
- [ ] **T2.8.4 Who is blocking whom** · *pg_locks / pg_stat_activity* · any
  While session A holds a row lock and B waits, write the query that shows blocked pid, blocking pid, both queries and wait time (use `pg_blocking_pids()`). Then set `lock_timeout = '2s'` in B and observe.
- [ ] **T2.8.5 PeopleOps: advisory lock for a monthly job** · *Advisory locks* · PeopleOps
  Make the "monthly accrual" script safe to start twice: the second run must exit immediately if the first is running (`pg_try_advisory_lock`). Compare with a `UNIQUE (year_month)` constraint on an `accrual_runs` table and say which guarantees idempotency.

**Must be able to do / explain**
- [ ] Choose between atomic UPDATE, `FOR UPDATE` and optimistic locking.
- [ ] Build a job queue with `FOR UPDATE SKIP LOCKED`.
- [ ] Explain the 4 conditions of deadlock and how lock ordering prevents it.
- [ ] Find the blocking session in production.

**Self-check questions**
1. What does `SKIP LOCKED` do and where is it used?
2. `FOR UPDATE` vs `FOR NO KEY UPDATE`?
3. How does PostgreSQL resolve a deadlock?
4. Why can `ALTER TABLE … ADD COLUMN` block all queries on a busy table?
5. What is an advisory lock?
6. Why set `idle_in_transaction_session_timeout`?

---

**Answers**
1. It skips rows already locked by other transactions instead of waiting — used for work queues where multiple workers claim different rows.
2. `FOR UPDATE` blocks even FK checks (KEY SHARE) from other transactions; `FOR NO KEY UPDATE` is weaker and is what a normal `UPDATE` that doesn't change key columns takes, so inserts into child tables referencing the row are not blocked.
3. The deadlock detector (after `deadlock_timeout`, default 1s) aborts one of the transactions with an error; the other continues.
4. It needs an `ACCESS EXCLUSIVE` lock; while waiting behind a long transaction it queues, and every new query queues behind it. Use `lock_timeout` and retry.
5. An application-defined lock on a number, managed by PostgreSQL but not tied to any table row; session- or transaction-scoped.
6. An open idle transaction holds locks and prevents VACUUM from removing dead rows; the timeout kills such sessions.

---

## Module 2.9 — VACUUM, partitioning, materialized views

**Estimated: 5 h**

**Topics:** dead tuples and bloat; `VACUUM` vs `VACUUM FULL`; autovacuum
and its thresholds; `ANALYZE`; transaction ID wraparound (what freezing
is); HOT updates and `fillfactor`. Declarative partitioning (range, list,
hash), default partition, partition pruning, indexes on partitioned
tables, attach/detach, dropping old partitions instead of `DELETE`.
Materialized views, `REFRESH MATERIALIZED VIEW [CONCURRENTLY]` and its
unique-index requirement.

**Lessons**
- [ ] **L2.9.1 Vacuum** — PostgreSQL docs chapter "Routine Database Maintenance Tasks" → "Routine Vacuuming" (all subsections: recovering disk space, updating planner statistics, visibility map, preventing transaction ID wraparound, autovacuum daemon).
- [ ] **L2.9.2 Partitioning** — Ch.5 §5.12 Table Partitioning (§5.12.2 Declarative Partitioning, §5.12.4 Partition Pruning, §5.12.6 Best Practices).
- [ ] **L2.9.3 Materialized views** — "The Rule System" chapter → "Materialized Views"; SQL Commands → `REFRESH MATERIALIZED VIEW`.

**Tasks**
- [ ] **T2.9.1 Make bloat visible** · *VACUUM* · StockPilot
  Update every row of a 1M-row table 3 times with autovacuum off for that table. Record table size and `n_dead_tup` (`pg_stat_user_tables`), then run `VACUUM`, then `VACUUM FULL`, recording size each time. Explain the difference.
- [ ] **T2.9.2 WareFlow: monthly partitions** · *Range partitioning* · WareFlow
  Recreate `stock_movements` partitioned by month on `created_at` with 12 partitions and a default partition; load 5M rows. Show pruning in `EXPLAIN` for a one-month query vs a query without a date filter.
- [ ] **T2.9.3 WareFlow: retention** · *DETACH/DROP vs DELETE* · WareFlow
  Remove data older than 12 months two ways: `DELETE` vs `DETACH PARTITION … CONCURRENTLY` + `DROP`. Compare time, WAL generated (`pg_current_wal_lsn()` difference) and bloat left behind.
- [ ] **T2.9.4 QuickServe: daily sales matview** · *Materialized view* · QuickServe
  Create `mv_daily_sales(day, cashier_id, revenue_cents, receipts)`. Refresh it normally while another session reads it, then `CONCURRENTLY` — show what blocks and what doesn't, and what index `CONCURRENTLY` requires.
- [ ] **T2.9.5 LedgerBase: trial balance live vs matview** · *Freshness trade-off* · LedgerBase
  Build the trial balance (total debits/credits per account type, must net to zero) as a live query and as a matview. Write when each is the right choice for an accounting system.

**Must be able to do / explain**
- [ ] Explain why MVCC needs VACUUM.
- [ ] Explain transaction ID wraparound and freezing at a high level.
- [ ] Design a partitioning scheme and prove pruning.
- [ ] Choose between a view, a materialized view and a summary table.

**Self-check questions**
1. What does VACUUM do? What does VACUUM FULL do differently?
2. What is table bloat and what causes it?
3. What is transaction ID wraparound?
4. When is partitioning worth it? When is it not?
5. What is partition pruning?
6. What does `REFRESH MATERIALIZED VIEW CONCURRENTLY` need and what does it give you?

---

**Answers**
1. VACUUM marks dead tuples' space reusable, updates the visibility map and freezes old rows; it does not return space to the OS and doesn't block reads/writes. VACUUM FULL rewrites the table compactly, returning space, but takes an ACCESS EXCLUSIVE lock.
2. Space occupied by dead row versions (and empty index pages) that isn't reused — caused by heavy UPDATE/DELETE when vacuum can't keep up or is blocked by long transactions.
3. Transaction IDs are 32-bit and wrap around; rows with very old xids must be "frozen" by VACUUM or they would appear to be in the future. If freezing falls too far behind, PostgreSQL stops accepting writes to protect data.
4. For very large tables with a natural key used in most queries (time), and for cheap retention (drop old partitions). Not worth it for small tables or when queries don't filter on the partition key (they scan every partition).
5. The planner/executor skipping partitions that cannot contain matching rows, based on the partition key in the WHERE clause.
6. A unique index on the matview (covering all rows). Readers are not blocked during the refresh; it is slower than a normal refresh because it computes a diff.

---

## Module 2.10 — Full-text search basics

**Estimated: 3 h**

**Topics:** why `LIKE` is not search; `tsvector` and `tsquery`;
dictionaries and stemming (`english` vs `simple` config);
`to_tsvector`, `plainto_tsquery`, `websearch_to_tsquery`; `@@`; weights
(`setweight`) and ranking (`ts_rank`, `ts_rank_cd`); `ts_headline`;
stored generated `tsvector` column + GIN index; `pg_trgm` for fuzzy /
typo-tolerant matching; limits of Postgres FTS (when you'd use
Elasticsearch — Track 2).

**Lessons**
- [ ] **L2.10.1 Full text search** — Ch.12 Full Text Search: §12.1 Introduction, §12.2 Tables and Indexes, §12.3 Controlling Text Search (parsing documents and queries, ranking, highlighting), §12.9 Preferred Index Types for Text Search.
- [ ] **L2.10.2 Trigram matching** — Appendix F → `pg_trgm` (similarity, `%` operator, `word_similarity`).

**Tasks**
- [ ] **T2.10.1 DocuVault: LIKE vs trigram vs FTS** · *Search progression* · DocuVault (200k documents)
  Search titles/body for "invoice payment": `ILIKE`, trigram similarity, and `to_tsvector @@ websearch_to_tsquery`. Compare results (which finds "payments invoiced"?) and timings with the right index for each.
- [ ] **T2.10.2 DocuVault: indexed search column** · *Generated tsvector + GIN* · DocuVault
  Add a stored generated `search_vector` with title weighted `A` and body `B`, GIN index it, and return the top 10 documents ranked by `ts_rank` with a `ts_headline` snippet.
- [ ] **T2.10.3 Typo tolerance** · *pg_trgm* · DocuVault
  Return documents whose title is similar to the misspelled query `"contarct"`, ordered by similarity, with a threshold you choose and justify.

**Must be able to do / explain**
- [ ] Explain tsvector/tsquery, stemming and stop words.
- [ ] Index and rank full-text search in PostgreSQL.
- [ ] Say when Postgres FTS is enough and when to move to a search engine.

**Self-check questions**
1. What is a `tsvector`?
2. Why does `'running'` match `'run'` with the `english` config?
3. `plainto_tsquery` vs `websearch_to_tsquery`?
4. Which index type is used for FTS and why?
5. When is PostgreSQL FTS not enough?

---

**Answers**
1. A sorted list of normalized lexemes (with optional positions and weights) produced from a document.
2. The english dictionary stems words to their lexeme; both become `run`.
3. `plainto_tsquery` ANDs all words; `websearch_to_tsquery` understands web-style syntax: quotes for phrases, `or`, `-` for exclusion.
4. GIN — an inverted index from each lexeme to the rows containing it, ideal for "which documents contain these words".
5. Need for advanced relevance tuning, faceting/aggregations at scale, many languages/analyzers, synonyms, very large corpora or distributed search — then Elasticsearch/OpenSearch.

---

## Module 2.11 — PL/pgSQL functions and triggers

**Estimated: 5 h**

**Topics:** SQL functions vs PL/pgSQL functions vs procedures (`CALL`,
transaction control in procedures); parameters, `RETURNS TABLE`,
`SETOF`; volatility (`IMMUTABLE`/`STABLE`/`VOLATILE`) and why it matters
for indexes/planning; variables, `IF`, loops, `RAISE`, exception blocks;
trigger functions (`NEW`, `OLD`, `TG_OP`), `BEFORE` vs `AFTER`, row vs
statement triggers; constraint triggers and `DEFERRABLE INITIALLY
DEFERRED`; when logic belongs in the database vs the application.

**Lessons**
- [ ] **L2.11.1 Functions** — "Extending SQL" chapter → "User-Defined Functions" (Query Language (SQL) Functions, Function Volatility Categories); SQL Commands → `CREATE FUNCTION`, `CREATE PROCEDURE`.
- [ ] **L2.11.2 PL/pgSQL** — "PL/pgSQL — SQL Procedural Language" chapter: Structure of PL/pgSQL, Declarations, Basic Statements, Control Structures (incl. Trapping Errors), Errors and Messages, Trigger Functions.
- [ ] **L2.11.3 Triggers** — "Triggers" chapter → Overview of Trigger Behavior; SQL Commands → `CREATE TRIGGER` (incl. `CONSTRAINT TRIGGER`, `DEFERRABLE`).

**Tasks**
- [ ] **T2.11.1 LedgerBase: trial balance function** · *RETURNS TABLE* · LedgerBase
  `trial_balance(p_from date, p_to date)` returning `account_type, total_debit_cents, total_credit_cents`. Mark volatility correctly and explain your choice.
- [ ] **T2.11.2 LedgerBase: balanced entries at commit** · *Deferrable constraint trigger* · LedgerBase
  Guarantee that every journal entry's debits equal its credits **at commit time** (lines are inserted one by one inside the transaction). Show a balanced transaction committing and an unbalanced one failing at `COMMIT`.
- [ ] **T2.11.3 LedgerBase: append-only lines** · *BEFORE trigger* · LedgerBase
  Reject any `UPDATE` or `DELETE` on `journal_lines` with a clear error; corrections must be new reversing entries. Also make `TRUNCATE` fail.
- [ ] **T2.11.4 PayFlow: audit trigger** · *AFTER trigger + JSONB* · PayFlow
  Every status change of `payment_intents` writes a row to `audit_log` with `old_state`/`new_state` as JSONB and the actor from `current_setting('app.user', true)`. Then return the full history of one payment in time order.
- [ ] **T2.11.5 StockPilot: procedure with transaction control** · *CREATE PROCEDURE + COMMIT* · StockPilot
  A procedure that recalculates `current_stock` from `stock_movements` in batches of 10 000 products, committing after each batch. Explain why this needs a procedure, not a function.

**Must be able to do / explain**
- [ ] Write a PL/pgSQL function and a trigger.
- [ ] Explain function volatility and its effect on the planner/indexes.
- [ ] Explain deferrable constraints/triggers.
- [ ] Argue when business rules belong in triggers and when they don't.

**Self-check questions**
1. Function vs procedure in PostgreSQL?
2. What do `IMMUTABLE`, `STABLE`, `VOLATILE` mean?
3. `BEFORE` vs `AFTER` triggers — when to use each?
4. What does `DEFERRABLE INITIALLY DEFERRED` do?
5. Downsides of putting a lot of logic in triggers?
6. What does a BEFORE row trigger returning NULL do?

---

**Answers**
1. Functions return a value and run inside the caller's transaction (no COMMIT). Procedures are invoked with `CALL`, return no value (OUT params allowed) and can `COMMIT`/`ROLLBACK` inside.
2. IMMUTABLE: same result for same arguments forever (can be used in index expressions). STABLE: same result within one statement (can read tables). VOLATILE: can change on every call or has side effects (default; never optimized away).
3. BEFORE: validate or modify `NEW` before the row is written (or cancel it). AFTER: react to a completed change (audit, derived tables), sees final values.
4. The check runs at `COMMIT` instead of after each statement, so intermediate states inside the transaction may violate it.
5. Hidden behaviour (surprising side effects), harder testing and debugging, performance cost per row, ordering issues between triggers, and logic split between app and DB.
6. The operation is silently skipped for that row.

---

# PART 3 — Oracle SQL + PL/SQL (~55 h)

All tasks use the **CreditLine** schema (loan servicing) from the Practice
schemas section. Create it in Module 3.1 and keep extending it; Track 4
(Java) calls the packages you write here. Rules that carry over to Track 4:

- Business rules live in **packages**, not in anonymous scripts.
- Packages **do not commit** — the caller owns the transaction (the only
  exception is autonomous-transaction logging in Module 3.9).
- Errors are raised with `RAISE_APPLICATION_ERROR(-20xxx, …)` using a fixed
  list of codes you document (e.g. `-20007 PERIOD_CLOSED`).

LeetCode database problems also accept **Oracle** as a language: re-solving
2–3 Part 1–2 problems in Oracle is a good warm-up for Module 3.1.

## Module 3.1 — Setup, Oracle vs PostgreSQL

**Estimated: 5 h**

**Topics:** Oracle architecture in one page (instance vs database, CDB/PDB,
user = schema, tablespaces); connecting (`FREEPDB1`, SQLcl/SQL*Plus);
data types (`NUMBER(p,s)`, `VARCHAR2(n CHAR)`, `DATE` has a time part,
`TIMESTAMP [WITH TIME ZONE]`, `CLOB`/`BLOB`, `BOOLEAN` in SQL since 23ai);
**empty string is NULL**; `DUAL`; identity columns and sequences;
`FETCH FIRST n ROWS ONLY` and `ROWNUM`; `NVL`, `NVL2`, `DECODE`; date
functions (`SYSDATE`, `SYSTIMESTAMP`, `TRUNC(date)`, `ADD_MONTHS`,
`MONTHS_BETWEEN`, `LAST_DAY`); **DDL commits implicitly**; no
`BEGIN`-to-start transactions (a transaction starts with the first DML);
dictionary views (`USER_TABLES`, `USER_CONSTRAINTS`, `USER_OBJECTS`, `USER_ERRORS`).

**Lessons**
- [ ] **L3.1.1 Environment** — `gvenzl/oracle-free` README on Docker Hub (environment variables, `APP_USER`, volumes, health check); Oracle Database Free "Get Started" page; SQLcl documentation → "Getting Started".
- [ ] **L3.1.2 Oracle SQL basics** — SQL Language Reference: Ch.2 "Basic Elements of Oracle SQL" (Data Types, Nulls, Literals, Format Models), Ch.5 "Functions" (skim: single-row functions — character, datetime, NULL-related, `DECODE`), and `CREATE TABLE` (identity_clause). Oracle Dev Gym → class **"Databases for Developers: Foundations"** (modules on tables, constraints, joins, aggregates).
- [ ] **L3.1.3 Differences checklist** — Write your own `docs/oracle-vs-postgres.md` table while working: types, NULL/empty string, paging, upsert, sequences, booleans, auto-commit/DDL, string concatenation, case sensitivity, date arithmetic.

**Tasks**
- [ ] **T3.1.1 Create the CreditLine schema** · *Oracle DDL* · CreditLine
  Write DDL for all CreditLine tables with identity PKs, FKs, `CHECK` constraints (e.g. `interest_method IN (…)`, exactly one of debit/credit non-zero, `is_active IN ('Y','N')`), and `NUMBER`/`VARCHAR2`/`DATE` types chosen deliberately. Insert seed data: 3 branches, 3 products (one per interest method), 20 customers, 30 loans.
- [ ] **T3.1.2 The empty-string trap** · *NULL semantics* · CreditLine
  Insert a customer with `phone = ''`. Show what `WHERE phone = ''`, `WHERE phone IS NULL` and `LENGTH(phone)` return, and write the PostgreSQL equivalent results in a comment.
- [ ] **T3.1.3 Port three PostgreSQL queries** · *Dialect differences* · CreditLine
  Rewrite in Oracle: (a) keyset pagination of loans by `(disbursed_at, loan_id)`, 20 per page; (b) case-insensitive customer search by name; (c) "loans disbursed in the current month" using `TRUNC`/`ADD_MONTHS` so an index on `disbursed_at` can still be used.
- [ ] **T3.1.4 DDL commits** · *Transaction semantics* · CreditLine
  Insert a row, then run `CREATE TABLE tmp_x (id NUMBER)`, then `ROLLBACK`. Is the row still there? Explain, and compare with PostgreSQL.
- [ ] **T3.1.5 Date arithmetic** · *DATE functions* · CreditLine
  For each loan return `first_due_date`, the due date of instalment 6 (`ADD_MONTHS`), the last day of the disbursement month, and whole months between disbursement and today. Explain what `ADD_MONTHS` does with 31 January.

**Must be able to do / explain**
- [ ] Start Oracle Free in Docker, connect to the PDB, create a schema user.
- [ ] List 10 practical Oracle vs PostgreSQL differences.
- [ ] Explain why `DATE` in Oracle is not like `date` in PostgreSQL.

**Self-check questions**
1. What is the difference between a CDB and a PDB?
2. In Oracle, what is the relationship between a user and a schema?
3. What is `''` in Oracle?
4. What does Oracle `DATE` store?
5. How do you get the first 10 rows in Oracle (two ways)?
6. What happens to an open transaction when you run DDL?
7. What is `DUAL`?

---

**Answers**
1. The container database (CDB) holds the root and system metadata; pluggable databases (PDBs, e.g. `FREEPDB1`) are the self-contained databases you connect applications to.
2. They are the same thing: a schema is the set of objects owned by a user with the same name.
3. NULL — Oracle treats a zero-length `VARCHAR2` as NULL.
4. Date **and** time to the second (century, year, month, day, hour, minute, second), no time zone and no fractions.
5. `FETCH FIRST 10 ROWS ONLY` (12c+), or `WHERE ROWNUM <= 10` (applied before `ORDER BY` unless the ordered query is wrapped in a subquery).
6. DDL issues an implicit COMMIT before (and after) itself, so the open transaction is committed.
7. A one-row, one-column dummy table used to select expressions (`SELECT SYSDATE FROM dual`); since 23ai `FROM dual` is optional.

---

## Module 3.2 — Oracle SQL power features

**Estimated: 7 h**

**Topics:** analytic functions (same idea as PostgreSQL windows) plus
Oracle extras (`RATIO_TO_REPORT`, `KEEP (DENSE_RANK FIRST/LAST)`,
`LISTAGG`); hierarchical queries with `CONNECT BY` (`START WITH`,
`PRIOR`, `LEVEL`, `SYS_CONNECT_BY_PATH`, `CONNECT_BY_ISLEAF`,
`NOCYCLE`, `ORDER SIBLINGS BY`) vs recursive `WITH`; `MERGE` (insert +
update [+ delete] in one statement); `PIVOT` / `UNPIVOT`; `GROUPING
SETS`, `ROLLUP`, `CUBE`, `GROUPING()`; (optional) `MATCH_RECOGNIZE`.

**Lessons**
- [ ] **L3.2.1 Analytic functions** — SQL Language Reference Ch.5 "Functions" → "Analytic Functions" (introduction and the analytic_clause/windowing_clause syntax), plus `LISTAGG`, `RATIO_TO_REPORT`, `FIRST`/`LAST`. Oracle Dev Gym → class **"Analytic SQL for Developers"**.
- [ ] **L3.2.2 Hierarchical queries** — SQL Language Reference Ch.9 "SQL Queries and Subqueries" → "Hierarchical Queries" (and "Hierarchical Query Pseudocolumns" in Ch.3).
- [ ] **L3.2.3 MERGE, PIVOT, grouping extensions** — SQL Language Reference: `MERGE` statement; `SELECT` → `pivot_clause`, `unpivot_clause`; `SELECT` → `group_by_clause` (`ROLLUP`, `CUBE`, `GROUPING SETS`) and the `GROUPING` function.

**Tasks**
- [ ] **T3.2.1 Running balance per loan** · *Analytic SUM* · CreditLine
  For each loan, list its `loan_transactions` in `value_date` order with a running outstanding principal (DISBURSE adds, REPAY principal allocations subtract — use `payment_allocations`). Output: `loan_id, txn_id, txn_type, value_date, amount, outstanding_after`.
- [ ] **T3.2.2 Days between repayments** · *LAG + KEEP* · CreditLine
  Per loan: average days between consecutive REPAY transactions, and the amount of the **latest** repayment using `MAX(...) KEEP (DENSE_RANK LAST ORDER BY value_date)`.
- [ ] **T3.2.3 Chart of accounts tree** · *CONNECT BY vs recursive WITH* · CreditLine
  Print the `gl_accounts` hierarchy with indentation by `LEVEL`, full path (`SYS_CONNECT_BY_PATH`) and a leaf flag, siblings ordered by code. Then write the same with recursive `WITH` and compare.
- [ ] **T3.2.4 Daily delinquency snapshot** · *MERGE* · CreditLine
  One `MERGE` that, for a given business date, inserts or updates `delinquency_snapshots` for every active loan: `days_past_due` from the oldest unpaid due `schedule_lines` row, and `bucket` (`CURRENT`, `1-30`, `31-60`, `61-90`, `90+`). Running it twice for the same date must not create duplicates.
- [ ] **T3.2.5 Aging report** · *PIVOT + ROLLUP* · CreditLine
  (a) PIVOT: one row per branch, one column per bucket with overdue principal. (b) ROLLUP: overdue principal by region and branch with subtotals and a grand total, labelled with `GROUPING()`. (c) UNPIVOT: turn each `schedule_lines` row's `principal_due, interest_due, fee_due` columns into rows `(line_id, component, amount)`.

**Must be able to do / explain**
- [ ] Write `CONNECT BY` queries and convert them to recursive `WITH`.
- [ ] Use `MERGE` for idempotent upserts.
- [ ] Pivot rows to columns and back.
- [ ] Produce subtotal reports with `ROLLUP` and identify subtotal rows.

**Self-check questions**
1. What does `PRIOR` mean in `CONNECT BY PRIOR id = parent_id`?
2. How do you prevent an infinite loop in a hierarchical query?
3. What can `MERGE` do in one statement?
4. What does `KEEP (DENSE_RANK LAST ORDER BY …)` do?
5. `ROLLUP(a, b)` vs `CUBE(a, b)`?
6. What does `GROUPING(col)` return?

---

**Answers**
1. It refers to the parent row: the child's `parent_id` must equal the `id` of the prior (parent) row — i.e. walk from parents to children.
2. `CONNECT BY NOCYCLE`, and check `CONNECT_BY_ISCYCLE` to find the offending rows.
3. Match source rows to target rows on a condition and `UPDATE` (optionally `DELETE`) the matched ones and `INSERT` the unmatched ones.
4. Applies the aggregate only to rows that rank last by the given order — e.g. "the amount of the latest payment" without a subquery.
5. `ROLLUP(a, b)` gives (a,b), (a), () — a hierarchy of subtotals. `CUBE(a, b)` gives all combinations: (a,b), (a), (b), ().
6. 1 if the column is aggregated away in that row (a subtotal/total row), 0 if it is a real group value.

---

## Module 3.3 — PL/SQL basics

**Estimated: 6 h**

**Topics:** block structure (`DECLARE … BEGIN … EXCEPTION … END`);
anonymous blocks; variables and constants; `%TYPE` and `%ROWTYPE`;
`SELECT INTO` (and its two exceptions); `IF`/`CASE`; loops (`LOOP`,
`WHILE`, `FOR i IN`, `EXIT WHEN`, `CONTINUE`); `DBMS_OUTPUT`; exceptions:
predefined (`NO_DATA_FOUND`, `TOO_MANY_ROWS`, `DUP_VAL_ON_INDEX`,
`ZERO_DIVIDE`), user-defined, `PRAGMA EXCEPTION_INIT`,
`RAISE_APPLICATION_ERROR`, `SQLCODE`/`SQLERRM`,
`DBMS_UTILITY.FORMAT_ERROR_BACKTRACE`; exception propagation.

**Lessons**
- [ ] **L3.3.1 Fundamentals** — PL/SQL Language Reference: Ch.1 "Overview of PL/SQL", Ch.2 "PL/SQL Language Fundamentals" (declarations, `%TYPE`, scope), Ch.3 "PL/SQL Data Types" (skim), Ch.4 "PL/SQL Control Statements".
- [ ] **L3.3.2 Error handling** — PL/SQL Language Reference Ch.11 "PL/SQL Error Handling" (predefined/user-defined exceptions, propagation, `RAISE_APPLICATION_ERROR`, handling in `OTHERS`). Oracle Dev Gym → PL/SQL quizzes/workouts on exceptions.

**Tasks**
- [ ] **T3.3.1 Customer exposure** · *Anonymous block, %TYPE, SELECT INTO* · CreditLine
  For a given `customer_id` (substitution variable), print full name, number of active loans and total outstanding principal. Handle an unknown customer with a clear message.
- [ ] **T3.3.2 Flat-interest schedule preview** · *Loops* · CreditLine
  For principal, annual rate and term in months, print a flat-interest schedule (instalment no, due date, principal part, interest part, remaining principal). The last instalment must absorb rounding so principal parts sum exactly to the principal.
- [ ] **T3.3.3 Error codes** · *RAISE_APPLICATION_ERROR* · CreditLine
  Create an `error_codes` reference (table or documented list): `-20001 CUSTOMER_NOT_FOUND`, `-20002 CUSTOMER_BLACKLISTED`, `-20003 AMOUNT_OUT_OF_RANGE`, `-20007 PERIOD_CLOSED`. Write a block that validates a new loan request against `loan_products` limits and `customers.blacklist_flag` and raises the right code.
- [ ] **T3.3.4 Exception propagation** · *Nested blocks* · no schema
  Write nested blocks showing: an exception handled in the inner block; one that propagates to the outer block; one raised in a declaration section; and printing the backtrace line with `FORMAT_ERROR_BACKTRACE`.

**Must be able to do / explain**
- [ ] Use `%TYPE`/`%ROWTYPE` and explain why they matter.
- [ ] Explain which exceptions `SELECT INTO` can raise.
- [ ] Explain why `WHEN OTHERS THEN NULL` is a bug.
- [ ] Raise application errors with documented codes.

**Self-check questions**
1. What are the sections of a PL/SQL block? Which are optional?
2. Why use `%TYPE`?
3. Which two exceptions can `SELECT INTO` raise?
4. What is the valid range for `RAISE_APPLICATION_ERROR` codes?
5. What does `PRAGMA EXCEPTION_INIT` do?
6. Why is `WHEN OTHERS THEN NULL;` dangerous?

---

**Answers**
1. `DECLARE` (optional), `BEGIN … END` executable section (required), `EXCEPTION` (optional).
2. The variable takes the column's type, so code keeps working when the column type changes, and intent is clear.
3. `NO_DATA_FOUND` (zero rows) and `TOO_MANY_ROWS` (more than one).
4. -20000 to -20999.
5. Binds a user-declared exception name to an Oracle error number so you can handle that error by name.
6. It silently swallows every error (including bugs and data corruption), so failures look like success. Log and re-raise instead.

---

## Module 3.4 — Cursors

**Estimated: 4 h**

**Topics:** implicit cursors and `SQL%ROWCOUNT`/`SQL%FOUND`; explicit
cursors (`OPEN`/`FETCH`/`CLOSE`, `%NOTFOUND`, `%ISOPEN`); cursor
`FOR` loops; parameterized cursors; `SELECT … FOR UPDATE` cursors and
`WHERE CURRENT OF`; cursor variables (`REF CURSOR`, `SYS_REFCURSOR`) —
returning result sets to callers such as Java/JDBC.

**Lessons**
- [ ] **L3.4.1 Cursors** — PL/SQL Language Reference Ch.6 "PL/SQL Static SQL": "Cursors Overview" (implicit, explicit, attributes), "Processing Query Result Sets" (cursor FOR loops, parameters), "Cursor Variables", "SELECT FOR UPDATE and FOR UPDATE Cursors".

**Tasks**
- [ ] **T3.4.1 Overdue lines report** · *Explicit cursor* · CreditLine
  Loop over all `schedule_lines` due before a business date and not fully paid; print loan, instalment, due date and unpaid amount; print total count at the end using cursor attributes.
- [ ] **T3.4.2 Parameterized cursor FOR loop** · *Cursor parameters* · CreditLine
  One cursor with parameters `(p_branch_id, p_status)`; call it for two branches in the same block.
- [ ] **T3.4.3 Mark overdue lines** · *FOR UPDATE + WHERE CURRENT OF* · CreditLine
  Set `status = 'OVERDUE'` for due unpaid lines using a `FOR UPDATE` cursor and `WHERE CURRENT OF`. Then rewrite as one `UPDATE` statement and write in a comment which is better and why.
- [ ] **T3.4.4 Loans by branch as REF CURSOR** · *SYS_REFCURSOR* · CreditLine
  Function `get_loans_by_branch(p_branch_id) RETURN SYS_REFCURSOR` returning `loan_id, customer name, principal, status`. Consume it from SQLcl (`VARIABLE rc REFCURSOR; EXEC :rc := …; PRINT rc`). Track 4 will call this from Java.

**Must be able to do / explain**
- [ ] Explain implicit vs explicit cursors and cursor attributes.
- [ ] Return a result set from PL/SQL with a REF CURSOR.
- [ ] Explain why row-by-row processing ("slow by slow") is usually worse than one SQL statement.

**Self-check questions**
1. What does `SQL%ROWCOUNT` give you and when is it reset?
2. Explicit cursor vs cursor FOR loop?
3. What is a REF CURSOR and why do APIs use it?
4. What does `WHERE CURRENT OF` do?
5. Strong vs weak REF CURSOR?

---

**Answers**
1. Number of rows affected by the most recent implicit-cursor SQL statement (DML or `SELECT INTO`) in the session; each new statement resets it.
2. With an explicit cursor you manage OPEN/FETCH/CLOSE yourself; the FOR loop opens, fetches (with automatic array prefetch of 100 rows) and closes for you and is usually preferred.
3. A pointer to an open query result that can be passed around and returned to a client, which fetches rows from it — the standard way to return result sets from PL/SQL to Java.
4. Updates/deletes the row most recently fetched from a `FOR UPDATE` cursor, without repeating the WHERE condition.
5. Strong has a declared return row type (checked at compile time); weak (`SYS_REFCURSOR`) can be opened for any query.

---

## Module 3.5 — Procedures, functions, packages

**Estimated: 7 h**

**Topics:** stored procedures and functions; parameter modes `IN`,
`OUT`, `IN OUT`, `NOCOPY`; default parameters and named notation;
functions callable from SQL (restrictions, `DETERMINISTIC`,
`RESULT_CACHE`); **packages**: specification vs body, public vs private,
package state and initialization, overloading, `ORA-04068` (package
state discarded); dependency tracking and invalidation; compiling and
reading errors (`SHOW ERRORS`, `USER_ERRORS`); the "packages don't commit"
rule.

**Lessons**
- [ ] **L3.5.1 Subprograms** — PL/SQL Language Reference Ch.8 "PL/SQL Subprograms" (parameter modes, defaults, overloading, `DETERMINISTIC`, result cache, invoker's vs definer's rights).
- [ ] **L3.5.2 Packages** — PL/SQL Language Reference Ch.10 "PL/SQL Packages" (spec, body, state, initialization, `SERIALLY_REUSABLE`); Ch.14 "SQL Statements for Stored PL/SQL Units" → `CREATE PACKAGE`, `CREATE PACKAGE BODY`.
- [ ] **L3.5.3 Style** — Optional: Steven Feuerstein, *Oracle PL/SQL Programming* (6th ed.), Part IV "PL/SQL Application Construction" (procedures, functions, packages).

**Tasks**
- [ ] **T3.5.1 Annuity payment function** · *DETERMINISTIC function usable in SQL* · CreditLine
  `fn_annuity_payment(p_principal, p_annual_rate, p_term_m) RETURN NUMBER` rounded to 2 decimals; handle rate = 0. Use it in a `SELECT` over `loans`. Check 3 values against a hand/online calculation.
- [ ] **T3.5.2 `pkg_schedule`** · *Package* · CreditLine
  Public `generate(p_loan_id, p_reason)` creates a new `schedules` version with `schedule_lines` for the loan's interest method (FLAT and ANNUITY at least), deactivates the previous version, and returns the new `schedule_id` as an OUT parameter. Private helpers for each method. No COMMIT inside.
- [ ] **T3.5.3 `pkg_payment.post_payment`** · *IN/OUT parameters + business rules* · CreditLine
  `post_payment(p_loan_id IN, p_amount IN, p_value_date IN, p_txn_id OUT, p_allocations OUT SYS_REFCURSOR)`: inserts a REPAY transaction and allocates it by the waterfall **penalty → fee → interest → principal**, oldest line first; raises `-20007` if the period of `p_value_date` is closed and `-20004` if the amount exceeds the total due. Test 3 scenarios in anonymous blocks.
- [ ] **T3.5.4 Package state** · *ORA-04068* · CreditLine
  Add a package-level counter variable, call it in session A, recompile the body in session B, call again in A. Record the error and explain it (and why stateless packages are preferred behind a connection pool).
- [ ] **T3.5.5 Overloading and named notation** · *Overloading* · CreditLine
  Overload `pkg_payment.post_payment` with a version taking `p_loan_id` and `p_amount` only (value date defaults to today) and call both using named notation.

**Must be able to do / explain**
- [ ] Design a package API (spec) and hide helpers in the body.
- [ ] Use OUT parameters and REF CURSORs for callers.
- [ ] Explain why packages should not commit, and who commits instead.
- [ ] Explain package state and ORA-04068.

**Self-check questions**
1. Why split a package into spec and body?
2. What happens to dependents when you recompile a package body vs a spec?
3. What does `DETERMINISTIC` promise?
4. `IN OUT` vs `OUT`? What is `NOCOPY`?
5. Why should a package procedure not `COMMIT`?
6. Definer's rights vs invoker's rights?
7. When would you use `RESULT_CACHE`?

---

**Answers**
1. The spec is the public contract; the body holds the implementation and private code. Callers depend only on the spec, so body changes don't invalidate them.
2. Recompiling the body doesn't invalidate code that depends on the spec (but resets package state in sessions); changing the spec invalidates all dependents.
3. Same inputs always give the same output with no side effects, so Oracle may cache/reuse results (and allow use in function-based indexes).
4. `OUT` starts as NULL inside the procedure; `IN OUT` passes the caller's value in and returns the modified value. `NOCOPY` is a hint to pass by reference instead of copying (faster for large collections, but changes are visible even if an exception occurs).
5. The caller (application / Spring `@Transactional`) owns the transaction; a commit inside breaks atomicity of the caller's unit of work and makes rollback impossible.
6. Definer's rights (default) runs with the privileges of the owner; invoker's rights (`AUTHID CURRENT_USER`) runs with the privileges and name resolution of the caller.
7. For functions whose results for given inputs rarely change and are read often (e.g. tariff/rate lookups); Oracle caches results across sessions and invalidates them on dependent table changes.

---

## Module 3.6 — Triggers (incl. mutating table error)

**Estimated: 4 h**

**Topics:** DML triggers (`BEFORE`/`AFTER`, row vs statement, `:NEW`,
`:OLD`, `INSERTING`/`UPDATING`/`DELETING`, `WHEN` clause); compound
triggers; `INSTEAD OF` triggers on views; system/DDL triggers (overview);
**ORA-04091 mutating-table error** — what it is and how compound triggers
avoid it; trigger ordering (`FOLLOWS`); why "API in packages" usually beats
triggers for business logic, and where triggers are right (audit,
guarding invariants).

**Lessons**
- [ ] **L3.6.1 Triggers** — PL/SQL Language Reference Ch.9 "PL/SQL Triggers": DML Triggers, Compound DML Triggers, "Mutating-Table Restriction", Order in Which Triggers Fire, `INSTEAD OF` DML triggers.

**Tasks**
- [ ] **T3.6.1 Audit trigger with JSON** · *AFTER row trigger* · CreditLine
  On `loans`, write every INSERT/UPDATE/DELETE to `audit_log` with `old_row_json`/`new_row_json` built with `JSON_OBJECT`, and `changed_by` from `SYS_CONTEXT('USERENV','CLIENT_IDENTIFIER')` falling back to `USER`.
- [ ] **T3.6.2 Reproduce ORA-04091** · *Mutating table* · CreditLine
  A row trigger on `schedule_lines` that checks "the sum of principal_due for this schedule must not exceed the loan principal" by querying `schedule_lines`. Trigger the error with a multi-row UPDATE, then fix it with a compound trigger (collect ids in the row section, check in the `AFTER STATEMENT` section).
- [ ] **T3.6.3 Closed period guard** · *BEFORE trigger* · CreditLine
  Reject any insert into `loan_transactions` whose `value_date` falls in a period marked `CLOSED` in `period_status`, raising `-20007`. Then write in a comment whether this belongs in the trigger, in `pkg_payment`, or both.
- [ ] **T3.6.4 One active schedule** · *Trigger vs constraint* · CreditLine
  Enforce "only one active schedule per loan" first with a trigger, then with a function-based unique index (`CASE WHEN is_active = 'Y' THEN loan_id END`). Show which one is safe under two concurrent sessions and explain.

**Must be able to do / explain**
- [ ] Write row, statement and compound triggers.
- [ ] Explain the mutating-table error and two ways around it.
- [ ] Explain why a trigger that reads the same table cannot reliably enforce multi-row rules under concurrency.

**Self-check questions**
1. What is a mutating table?
2. What is a compound trigger and why was it introduced?
3. Row vs statement trigger?
4. Can a trigger `COMMIT`?
5. Why can a trigger-based uniqueness check fail under concurrency while a unique index doesn't?
6. When is a trigger the right tool?

---

**Answers**
1. A table currently being modified by the statement that fired a row-level trigger; the trigger may not query or modify it (ORA-04091) because it would see an inconsistent, half-changed state.
2. One trigger with sections for before statement, before each row, after each row and after statement, sharing state — so you can collect row data and do the table-level check once after the statement.
3. A row trigger fires once per affected row (has `:NEW`/`:OLD`); a statement trigger fires once per statement, even if zero rows are affected.
4. No (except inside an autonomous transaction), because it runs inside the triggering statement's transaction.
5. Each session's trigger can't see the other's uncommitted row, so both pass the check and both commit. A unique index checks against all entries, including uncommitted ones, and makes the second session wait/fail.
6. Auditing, keeping simple derived columns, and guarding invariants that must hold no matter which client writes (defence in depth) — not for complex business workflows.

---

## Module 3.7 — Records, collections, BULK COLLECT / FORALL

**Estimated: 6 h**

**Topics:** records (`%ROWTYPE`, user-defined `RECORD`); collections:
associative arrays (`INDEX BY`), nested tables, VARRAYs; collection
methods (`COUNT`, `FIRST/LAST/NEXT`, `EXISTS`, `EXTEND`, `DELETE`);
schema-level types (`CREATE TYPE … AS OBJECT / TABLE OF`) and `TABLE()`
in SQL; context switches between PL/SQL and SQL engines; `BULK COLLECT`
(with `LIMIT`), `FORALL` (with `SAVE EXCEPTIONS`, `SQL%BULK_EXCEPTIONS`,
`SQL%BULK_ROWCOUNT`); pipelined table functions (optional).

**Lessons**
- [ ] **L3.7.1 Collections and records** — PL/SQL Language Reference Ch.5 "PL/SQL Collections and Records" (collection types, methods, records).
- [ ] **L3.7.2 Bulk processing** — PL/SQL Language Reference Ch.12 "PL/SQL Optimization and Tuning" → "Bulk SQL and Bulk Binding" (FORALL, SAVE EXCEPTIONS, BULK COLLECT, LIMIT) and "Chaining Pipelined Table Functions" (optional).

**Tasks**
- [ ] **T3.7.1 Rate cache** · *Associative array* · CreditLine
  Load `loan_products` rates into an associative array indexed by `product_id` once, then look them up in a loop over 30 000 loans. Compare time with a `SELECT INTO` per loan.
- [ ] **T3.7.2 Daily interest accrual in bulk** · *BULK COLLECT LIMIT + FORALL* · CreditLine (generate 200 000 loans)
  For a business date, insert one ACCRUAL `loan_transactions` row per active loan (interest = outstanding × rate / 365, rounded). Implement row-by-row first, then with `BULK COLLECT … LIMIT 1000` + `FORALL`. Record both timings.
- [ ] **T3.7.3 Keep going past bad rows** · *SAVE EXCEPTIONS* · CreditLine
  Make 5 loans fail (e.g. violate a check). The bulk accrual must insert all good rows and write each failure into `batch_errors` (loan_id, error code, message) using `SQL%BULK_EXCEPTIONS`.
- [ ] **T3.7.4 SQL over a collection** · *Schema-level nested table + TABLE()* · CreditLine
  Create `TYPE t_id_list AS TABLE OF NUMBER`; write a function that takes a list of loan ids and returns their total outstanding using one SQL statement with `TABLE(p_ids)`.

**Must be able to do / explain**
- [ ] Choose between associative array, nested table and VARRAY.
- [ ] Explain context switching and why bulk binding is faster.
- [ ] Write a restartable, error-tolerant bulk load.

**Self-check questions**
1. What are the three collection types and a use for each?
2. What is a context switch in PL/SQL?
3. Why use `LIMIT` with `BULK COLLECT`?
4. What does `SAVE EXCEPTIONS` do?
5. Is `FORALL` a loop?
6. When is a single SQL statement better than any PL/SQL loop?

---

**Answers**
1. Associative array (in-memory lookup table / cache, PL/SQL only); nested table (unbounded list, can be a schema type used in SQL and columns); VARRAY (bounded, ordered, small fixed-size lists).
2. The switch between the PL/SQL engine and the SQL engine each time a SQL statement is executed from PL/SQL; done per row it adds large overhead.
3. To bound PGA memory — fetching millions of rows into one collection can exhaust memory; `LIMIT` fetches in chunks.
4. Lets `FORALL` continue after a failing element; at the end it raises ORA-24381 and `SQL%BULK_EXCEPTIONS` lists each failed index and error code.
5. No — it is a single bulk DML statement sent to the SQL engine with a collection of bind values.
6. Almost always when the logic can be expressed in SQL (`INSERT … SELECT`, `MERGE`, `UPDATE` with a join): "do it in SQL, if you can't then bulk PL/SQL, row-by-row last".

---

## Module 3.8 — Dynamic SQL and bind variables

**Estimated: 3 h**

**Topics:** `EXECUTE IMMEDIATE` (with `USING`, `INTO`, `RETURNING INTO`);
`OPEN cursor FOR dynamic_string USING …`; `DBMS_SQL` (when the number of
binds is unknown); bind variables vs literals — hard parse, shared pool,
cursor sharing; **SQL injection** in PL/SQL and how to prevent it
(binds for values, `DBMS_ASSERT` for identifiers); DDL from PL/SQL.

**Lessons**
- [ ] **L3.8.1 Dynamic SQL** — PL/SQL Language Reference Ch.7 "PL/SQL Dynamic SQL" (native dynamic SQL, `DBMS_SQL` package, **"SQL Injection"** section with techniques to avoid it).
- [ ] **L3.8.2 Why binds matter** — Oracle Database Concepts → "Memory Architecture" → Shared Pool / Library Cache (skim); SQL Tuning Guide → "SQL Processing" (hard vs soft parse).

**Tasks**
- [ ] **T3.8.1 Loan search with optional filters** · *OPEN FOR with binds* · CreditLine
  `search_loans(p_branch_id, p_status, p_min_principal, p_customer_name) RETURN SYS_REFCURSOR` where any parameter may be NULL (= no filter). Build the SQL dynamically with **bind variables only**.
- [ ] **T3.8.2 Injection: break it, then fix it** · *SQL injection* · CreditLine
  Write a deliberately vulnerable version that concatenates `p_customer_name`, exploit it to return all customers, then fix it. For a dynamic `ORDER BY` column, validate the identifier with `DBMS_ASSERT.SIMPLE_SQL_NAME` against an allow-list.
- [ ] **T3.8.3 Hard parses: literals vs binds** · *Shared pool* · CreditLine
  Run 1 000 lookups by `loan_id` with literals and with binds; compare the number of distinct statements in `V$SQL` (filter by a comment tag) and elapsed time.

**Must be able to do / explain**
- [ ] Write dynamic SQL with binds and explain when dynamic SQL is needed at all.
- [ ] Explain SQL injection and the two defences (binds for values, validation for identifiers).
- [ ] Explain hard vs soft parse and why binds matter for scalability.

**Self-check questions**
1. When do you need dynamic SQL?
2. Can you bind a table or column name?
3. What is a hard parse?
4. How does `DBMS_ASSERT` help?
5. `EXECUTE IMMEDIATE` vs `DBMS_SQL`?

---

**Answers**
1. When the statement text isn't known at compile time: optional filters/sort columns, DDL, object names chosen at runtime.
2. No — binds are for values only; identifiers must be validated (allow-list / `DBMS_ASSERT`) and concatenated.
3. Full parsing and optimization of a statement not found in the shared pool — CPU-heavy and serialized on latches; literals cause one hard parse per distinct value.
4. It validates/quotes identifiers and literals (`SIMPLE_SQL_NAME`, `SQL_OBJECT_NAME`, `ENQUOTE_LITERAL`) so user input can't change the statement structure.
5. `EXECUTE IMMEDIATE`/`OPEN FOR` are simpler and faster when the number of binds and select-list columns is known; `DBMS_SQL` handles an unknown number of binds/columns and can describe results.

---

## Module 3.9 — Autonomous transactions and DBMS_SCHEDULER

**Estimated: 4 h**

**Topics:** `PRAGMA AUTONOMOUS_TRANSACTION` — an independent transaction
that commits on its own; the legitimate use (error/audit logging that must
survive a rollback) and the misuses; `DBMS_SCHEDULER`: programs, jobs,
schedules (calendaring syntax), chains, job logs (`USER_SCHEDULER_JOBS`,
`USER_SCHEDULER_JOB_RUN_DETAILS`); making batch jobs idempotent and
restartable; `DBMS_APPLICATION_INFO` for progress; single-instance guard
(`DBMS_LOCK` or a status row).

**Lessons**
- [ ] **L3.9.1 Autonomous transactions** — PL/SQL Language Reference Ch.6 "PL/SQL Static SQL" → "Autonomous Transactions".
- [ ] **L3.9.2 Scheduler** — Database Administrator's Guide → "Scheduling Jobs with Oracle Scheduler" (creating jobs, schedules, chains, monitoring); PL/SQL Packages and Types Reference → `DBMS_SCHEDULER` (`CREATE_JOB`, `CREATE_CHAIN`, `DEFINE_CHAIN_STEP`, `DEFINE_CHAIN_RULE`), `DBMS_APPLICATION_INFO`.

**Tasks**
- [ ] **T3.9.1 `pkg_audit.log_error`** · *Autonomous transaction* · CreditLine
  A procedure that writes to `batch_errors` in an autonomous transaction. Prove it: call it inside a transaction that then rolls back — the error row must remain, the business rows must not.
- [ ] **T3.9.2 Idempotent accrual** · *Unique constraint + batch_runs* · CreditLine
  Wrap T3.7.2 in `pkg_batch.run_accrual(p_business_date)`: records a `batch_runs` row (RUNNING → DONE/FAILED, records processed), refuses to run twice for the same date (unique constraint on `(loan_id, value_date, txn_type)` for ACCRUAL and a check on `batch_runs`), and reports progress via `DBMS_APPLICATION_INFO`.
- [ ] **T3.9.3 Nightly job** · *DBMS_SCHEDULER job* · CreditLine
  Schedule `run_accrual` daily at 01:00 with a calendaring expression; run it once manually with `RUN_JOB`; read the result from `USER_SCHEDULER_JOB_RUN_DETAILS`.
- [ ] **T3.9.4 Batch chain** · *DBMS_SCHEDULER chain* · CreditLine
  Chain: `open_business_date → accrue_interest → assess_penalties → age_delinquency (MERGE from T3.2.4) → close_business_date`, where a failure stops the chain and a re-run continues from the failed step. Stub steps may just log.

**Must be able to do / explain**
- [ ] Explain the one legitimate use of autonomous transactions and its risks.
- [ ] Create and monitor Scheduler jobs and chains.
- [ ] Design a batch that is idempotent, restartable and safe to start twice.

**Self-check questions**
1. What is an autonomous transaction?
2. Why is using one to "commit inside a trigger" usually wrong?
3. Can an autonomous transaction see the caller's uncommitted changes?
4. DBMS_SCHEDULER vs DBMS_JOB vs cron?
5. How do you make a nightly batch idempotent?
6. What is a Scheduler chain?

---

**Answers**
1. A transaction started from within another one that commits or rolls back independently of the calling (main) transaction.
2. It breaks atomicity: the autonomous part is committed even if the main transaction rolls back, producing inconsistent data; it also can't see the main transaction's changes (so validations become wrong).
3. No — it behaves like a separate session; it sees only committed data. It can even deadlock with its caller if it touches the same rows.
4. DBMS_SCHEDULER is the modern, full-featured scheduler (calendars, chains, logging, resource management); DBMS_JOB is legacy. Cron lives outside the database and knows nothing about DB state or failures.
5. Key each unit of work by business date (unique constraints so a second run can't duplicate), record run status, make each step either skip already-done work or be safe to repeat (MERGE), and guard against concurrent runs.
6. A set of named steps (programs or other chains) plus rules that decide which step runs next based on the results of earlier steps.

---

## Module 3.10 — Execution plans and basic tuning

**Estimated: 5 h**

**Topics:** `EXPLAIN PLAN` + `DBMS_XPLAN.DISPLAY` vs
`DBMS_XPLAN.DISPLAY_CURSOR` (actual plan) with `GATHER_PLAN_STATISTICS`
and `'ALLSTATS LAST'`; reading plans (E-Rows vs A-Rows, Starts, Buffers);
access paths (full scan, index range/unique/skip scan, fast full scan);
join methods (nested loops, hash, sort merge); optimizer statistics
(`DBMS_STATS.GATHER_TABLE_STATS`, histograms); function-based indexes;
bind variable peeking and adaptive cursor sharing (awareness); range and
interval partitioning with partition pruning (`Pstart/Pstop`); local vs
global indexes.

**Lessons**
- [ ] **L3.10.1 Plans** — SQL Tuning Guide: "Generating and Displaying Execution Plans" and "Reading Execution Plans"; PL/SQL Packages and Types Reference → `DBMS_XPLAN` (`DISPLAY_CURSOR` format options).
- [ ] **L3.10.2 Indexes and statistics** — Use The Index, Luke!: re-read "The Where Clause" and "Execution Plans → Oracle"; SQL Tuning Guide → "Optimizer Statistics Concepts" (skim) and "Histograms" (skim).
- [ ] **L3.10.3 Partitioning** — VLDB and Partitioning Guide: "Partitioning Concepts" (range, interval, list, hash) and "Partitioning for Availability, Manageability, and Performance" → partition pruning.

**Tasks**
- [ ] **T3.10.1 Actual vs estimated plan** · *DISPLAY_CURSOR ALLSTATS LAST* · CreditLine
  Query "all loans of one customer with their outstanding principal". Show the actual plan before and after adding an index on `loans(customer_id)`; explain E-Rows vs A-Rows and Buffers.
- [ ] **T3.10.2 Function-based unique index** · *FBI* · CreditLine
  (If not done in T3.6.4.) Enforce one active schedule per loan with a function-based unique index and show it in `USER_IND_EXPRESSIONS`. Also create an FBI for `UPPER(full_name)` and show the search from T3.1.3(b) using it.
- [ ] **T3.10.3 Interval-partitioned transactions** · *Partition pruning* · CreditLine (2M loan_transactions)
  Recreate `loan_transactions` interval-partitioned by month on `value_date` with a local index on `loan_id`. Show `Pstart/Pstop` for a one-month query vs a query with `TRUNC(value_date)` on the column — and explain why the second one can't prune well.
- [ ] **T3.10.4 Stale statistics** · *DBMS_STATS* · CreditLine
  Load 1M new rows without gathering stats, show a wrong cardinality estimate and a bad plan choice, gather stats, show the corrected plan.
- [ ] **T3.10.5 Tuning write-up** · *Report* · CreditLine
  Pick the slowest query from your Part 3 work, tune it (index, rewrite, stats) and write `docs/tuning-<name>.md`: before/after plan, buffers, time, and why it improved.

**Must be able to do / explain**
- [ ] Get the actual execution plan of a statement and read it.
- [ ] Spot bad cardinality estimates and fix stale stats.
- [ ] Explain partition pruning and local vs global indexes.

**Self-check questions**
1. `EXPLAIN PLAN` vs `DBMS_XPLAN.DISPLAY_CURSOR`?
2. What do E-Rows and A-Rows tell you?
3. When does the optimizer prefer a full table scan?
4. What is a function-based index?
5. Local vs global partitioned index?
6. What is bind peeking and what problem can it cause?

---

**Answers**
1. `EXPLAIN PLAN` shows what the optimizer *would* do (can differ from reality, e.g. with binds); `DISPLAY_CURSOR` shows the plan actually used by an executed cursor, and with `ALLSTATS LAST` the real row counts and buffers.
2. Estimated vs actual rows per step; a large difference points to wrong statistics or unfortunate predicates, which leads to bad plans.
3. When a large fraction of rows is needed, the table is small, or no usable index exists — multiblock reads beat many single-block index lookups.
4. An index on an expression (e.g. `UPPER(name)`, a `CASE`), used when the query uses the same expression.
5. A local index is partitioned the same way as the table (easy maintenance, pruning); a global index has its own partitioning or none (good for unique lookups not containing the partition key, but partition maintenance can invalidate it).
6. At hard parse the optimizer looks at the first bind values to choose a plan; if those values are unusual (skewed data), everybody reuses a plan that is bad for typical values. Adaptive cursor sharing mitigates it.

---

## Module 3.11 — Testing PL/SQL with utPLSQL

**Estimated: 4 h**

**Topics:** why test PL/SQL; utPLSQL v3 architecture; test packages with
annotations (`--%suite`, `--%test`, `--%beforeall`, `--%beforeeach`,
`--%throws`, `--%rollback`); expectations (`ut.expect(...).to_equal`,
comparing cursors); test data setup and automatic rollback; running with
`ut.run` and `utPLSQL-cli`; reporters (JUnit XML, coverage) for CI.

**Lessons**
- [ ] **L3.11.1 utPLSQL** — utPLSQL docs: "Getting Started", "Installation", "Annotations", "Expectations", "Running tests", "Reporters" (incl. coverage).

**Tasks**
- [ ] **T3.11.1 Install utPLSQL** · *Setup* · Oracle Free
  Install utPLSQL into the container (headless install script) and run `ut.run()` successfully on an empty suite.
- [ ] **T3.11.2 Test `fn_annuity_payment`** · *Expectations* · CreditLine
  At least 5 tests: normal case against hand-computed values, zero rate, 1-month term, rounding, invalid input raising the right error (`--%throws`).
- [ ] **T3.11.3 Test `pkg_payment.post_payment`** · *Data setup + cursor comparison* · CreditLine
  Tests: exact payment of one instalment, partial payment (waterfall order), overpayment rejected with `-20004`, closed period rejected with `-20007`. Compare the allocations REF CURSOR to an expected cursor.
- [ ] **T3.11.4 Test the batch** · *Integration test* · CreditLine
  Accrual for a date inserts exactly one row per active loan, a second run inserts nothing, and a poison loan ends up in `batch_errors` while others succeed.
- [ ] **T3.11.5 Run in CI format** · *Reporters* · CreditLine
  Run all suites with `utPLSQL-cli` producing JUnit XML and a coverage report; commit the command in `docs/testing.md`.

**Must be able to do / explain**
- [ ] Write a utPLSQL suite with setup, tests and expected exceptions.
- [ ] Explain how utPLSQL isolates test data.
- [ ] Run PL/SQL tests from the command line in a CI-friendly format.

**Self-check questions**
1. How does utPLSQL find tests?
2. How is test data cleaned up?
3. How do you test that a procedure raises -20007?
4. How can you compare query results in a test?
5. Why run database tests in CI (e.g. against a Testcontainers Oracle)?

---

**Answers**
1. Through annotations in package specs: `--%suite` marks the package, `--%test` marks procedures as tests.
2. By default each test runs inside a savepoint that is rolled back after the test (`--%rollback(auto)`), unless the code commits.
3. Annotate the test with `--%throws(-20007)` (or catch it and use expectations).
4. `ut.expect(actual_cursor).to_equal(expected_cursor)` — utPLSQL compares cursor data and reports differences row by row.
5. PL/SQL is code with business rules; regressions there break every client. CI runs catch them before deployment, and Testcontainers give each run a fresh, identical database.

---

## Progress summary

| Part | Module | Tasks done / total | Module done |
|---|---|---|---|
| 1 | 1.1 SELECT, WHERE, NULL, ORDER BY/LIMIT | 2 / 6 | [ ] |
| 1 | 1.2 Aggregates, GROUP BY, HAVING | 0 / 5 | [ ] |
| 1 | 1.3 JOINs | 2 / 6 | [ ] |
| 1 | 1.4 Subqueries, EXISTS vs IN, set operations | 0 / 6 | [ ] |
| 1 | 1.5 CASE, string & date functions | 0 / 5 | [ ] |
| 1 | 1.6 DDL, data types, constraints, DML | 0 / 5 | [ ] |
| 1 | 1.7 Normalization, schema design, views | 0 / 5 | [ ] |
| 2 | 2.1 CTEs & recursive CTEs | 0 / 5 | [ ] |
| 2 | 2.2 Window functions | 0 / 10 | [ ] |
| 2 | 2.3 LATERAL, ON CONFLICT, RETURNING | 0 / 5 | [ ] |
| 2 | 2.4 JSONB & arrays | 0 / 5 | [ ] |
| 2 | 2.5 Indexes | 0 / 6 | [ ] |
| 2 | 2.6 EXPLAIN ANALYZE & tuning | 0 / 5 | [ ] |
| 2 | 2.7 Transactions, isolation, MVCC | 0 / 5 | [ ] |
| 2 | 2.8 Locking | 0 / 5 | [ ] |
| 2 | 2.9 VACUUM, partitioning, matviews | 0 / 5 | [ ] |
| 2 | 2.10 Full-text search | 0 / 3 | [ ] |
| 2 | 2.11 PL/pgSQL functions & triggers | 0 / 5 | [ ] |
| 3 | 3.1 Setup, Oracle vs PostgreSQL | 0 / 5 | [ ] |
| 3 | 3.2 Oracle SQL power features | 0 / 5 | [ ] |
| 3 | 3.3 PL/SQL basics | 0 / 4 | [ ] |
| 3 | 3.4 Cursors | 0 / 4 | [ ] |
| 3 | 3.5 Procedures, functions, packages | 0 / 5 | [ ] |
| 3 | 3.6 Triggers | 0 / 4 | [ ] |
| 3 | 3.7 Collections, BULK COLLECT/FORALL | 0 / 4 | [ ] |
| 3 | 3.8 Dynamic SQL & bind variables | 0 / 3 | [ ] |
| 3 | 3.9 Autonomous transactions & DBMS_SCHEDULER | 0 / 4 | [ ] |
| 3 | 3.10 Execution plans & tuning | 0 / 5 | [ ] |
| 3 | 3.11 utPLSQL | 0 / 5 | [ ] |
| | **Total** | **4 / 145** | |
