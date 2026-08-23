# SQL Practice — Full Problem Bank

130 problems, one per weekday across most of Track A (D1–D131, D145–D167),
mixing two kinds of practice. Weeks 23–24 (Phase 5, Raft implementation)
and Weeks 29–30 (Phase 6, system-design real builds) deliberately drop
this daily grind — the day's own algorithmic/systems work already carries
that load; see those weeks' framing in their phase files.

- **Generic** problems are well-known LeetCode-SQL-style exercises. They're
  **paraphrased here with their own self-contained mini schema** (not copied
  verbatim from LeetCode's official wording) so this file works standalone —
  if you want the official version with a runnable judge, search the title on
  LeetCode's Database study plan.
- **Project-schema** problems run directly against whichever project you're
  building that week (StockPilot, QuickServe, PeopleOps, WareFlow, CarePoint,
  LedgerBase, FleetTrack, DocuVault, PayFlow, AtlasMarket). Schemas are in the
  appendix below — copy the relevant tables into a scratch Postgres DB (or
  just use your project's real dev database) and run the query for real.

Every entry states the **task** — what tables are involved and what the
output should look like — plus a *Technique* tag naming the general category
(join, subquery, window function, …), the same way the DSA file names a
pattern. Neither tells you the actual clause to write. If you get stuck,
that's the point where you go look up the technique, not where you read the
answer off this page.

Difficulty ramps with the phase: SELECT/WHERE and simple JOINs in Phase 1,
aggregation and multi-table JOINs through Phase 2, subqueries and `EXPLAIN
ANALYZE` in Phase 3 (matching the Postgres deep-dive), window functions and
CTEs from Phase 3 onward, and integrity-audit/reconciliation-style queries
(the kind that actually gets asked in fintech interviews) in Phase 6.

Saturdays have no new problem — they repeat the week's Tuesday task from
memory, then ask you to extend it with one more condition or column.

---

## Appendix — Project Schemas

**StockPilot** (Phase 1): `users(id, email, hashed_password, role, created_at)`
· `categories(id, name, parent_id → categories.id)` ·
`suppliers(id, name, contact_email)` · `products(id, sku, name, category_id,
supplier_id, price_cents, current_stock, reorder_level)` ·
`stock_movements(id, product_id, delta, reason, created_by → users.id,
created_at)` · `orders(id, status, created_by, created_at)` ·
`order_items(id, order_id, product_id, qty, unit_price_cents)`

**QuickServe** (Phase 2): `products(id, sku, name, price_cents, tax_rate)` ·
`discounts(id, code, type, value, max_cap_cents)` · `receipts(id, cashier_id,
status, created_at)` · `receipt_items(id, receipt_id, product_id, qty,
unit_price_cents, discount_id)` · `returns(id, receipt_id, reason,
processed_by, created_at)`

**PeopleOps** (Phase 2–3): `employees(id, name, department, manager_id,
hire_date)` · `leave_requests(id, employee_id, start_date, end_date, status,
requested_at, approved_at)` · `leave_balances(id, employee_id, year,
accrued_days, used_days)`

**WareFlow** (Phase 3): `warehouses(id, name, location)` ·
`stock_levels(id, warehouse_id, product_id, qty)` — unique(warehouse_id,
product_id) · `stock_movements(id, warehouse_id, product_id, delta, reason,
ref_id, created_at)` · `transfers(id, from_warehouse_id, to_warehouse_id,
status, created_at)` · `transfer_items(id, transfer_id, product_id, qty)` ·
`reservations(id, order_ref, warehouse_id, product_id, qty, status,
created_at)`

**CarePoint** (Phase 4): `doctors(id, name, specialty)` · `patients(id, name,
dob, contact)` · `appointments(id, doctor_id, patient_id, slot_start,
slot_end, status)` · `documents(id, patient_id, s3_key, uploaded_by,
uploaded_at)`

**LedgerBase** (Phase 4): `accounts(id, name, type)` · `journal_entries(id,
description, created_at)` · `journal_lines(id, journal_entry_id, account_id,
debit_cents, credit_cents)` · `invoices(id, client_name, total_cents, status,
issued_at, due_at)` · `payments(id, invoice_id, amount_cents,
journal_entry_id, received_at)`

**FleetTrack** (Phase 5): `drivers(id, name, status)` · `deliveries(id,
driver_id, status, created_at)` · `delivery_events(id, delivery_id,
from_status, to_status, created_at)` · `outbox(id, aggregate_type,
aggregate_id, event_type, payload, created_at, sent_at)` ·
`delivery_view(id, driver_name, status, last_updated)`

**DocuVault** (Phase 5): `documents(id, title, current_version_id,
created_by)` · `document_versions(id, document_id, s3_key, version_number,
created_at)` · `tags(id, name)` · `document_tags(document_id, tag_id)`

**PayFlow** (Phase 6): `payment_intents(id, idempotency_key, amount_cents,
status, journal_entry_id, created_at)` · `webhook_events(id,
provider_event_id, payload, processed_at, received_at)` · `refunds(id,
payment_intent_id, amount_cents, journal_entry_id, created_at)`

**AtlasMarket** (Phase 6, delta on StockPilot): `vendors(id, name,
payout_account_ref)` · `products(..., vendor_id → vendors.id)` ·
`order_vendor_groups(id, order_id, vendor_id, status, journal_entry_id)`

---

## Week 1 (Phase 1) — SELECT / WHERE Basics

### D1 — LeetCode SQL: Combine Two Tables
*Technique: Outer join*
Mini schema: `Person(person_id, first_name, last_name)`,
`Address(address_id, person_id, city, state)`

Return `first_name, last_name, city, state` for every person. People with no
address on file should still appear, with `city`/`state` as `NULL`.

### D2 — StockPilot: products where current_stock < reorder_level
*Technique: Filtering*

List `sku, name, current_stock, reorder_level` for every product currently
below its reorder point, worst shortages first.

### D3 — StockPilot: products with no supplier
*Technique: Outer join*

List `sku, name` for products that don't have a valid supplier on file —
either no supplier set, or one that no longer exists in `suppliers`.

### D4 — LeetCode SQL: Find Customer Referee
*Technique: NULL handling*
Mini schema: `Customer(id, name, referee_id)` — `referee_id` points at the
`id` of whoever referred them.

Return the names of customers **not** referred by the customer with `id =
2` — including customers with no referee at all.

### D5 — StockPilot: categories with no products
*Technique: Anti-join*

List category names that currently have zero products assigned to them.

---

## Week 2 (Phase 1) — Aggregation & GROUP BY

### D7 — StockPilot: total stock value per category
*Technique: Aggregation*

For each category, compute total stock value (`current_stock × price_cents`,
summed across its products). Return categories from highest to lowest value.

### D8 — LeetCode SQL: Big Countries
*Technique: Filtering*
Mini schema: `World(name, continent, area, population, gdp)`

Return `name, population, area` for "big" countries — area of at least
3,000,000, or population of at least 25,000,000.

### D9 — StockPilot: count orders per status
*Technique: Aggregation*

Return the count of orders for each `status` value.

### D10 — StockPilot: top 5 products by units sold
*Technique: Aggregation + ranking*

Across all `order_items`, find the 5 products with the highest total
quantity sold.

### D11 — LeetCode SQL: Classes More Than 5 Students
*Technique: Aggregation*
Mini schema: `Courses(student, class)`

Return the names of classes with 5 or more distinct students enrolled.

---

## Week 3 (Phase 1) — Multi-Table JOINs

### D13 — StockPilot: orders with item count + total value
*Technique: Aggregation*

For each order, return how many line items it has and its total value
(quantity × unit price, summed).

### D14 — StockPilot: stock movements joined to the user who made them
*Technique: Join*

Return each stock movement's `id, delta, reason, created_at`, alongside the
`email` of the user who made it.

### D15 — LeetCode SQL: Rising Temperature
*Technique: Row-to-row comparison*
Mini schema: `Weather(id, recordDate, temperature)`

Return the `id`s of dates where the temperature was strictly higher than on
the immediately preceding calendar day.

### D16 — StockPilot: suppliers whose products never sold
*Technique: Anti-join across 3 tables*

Find suppliers whose products have never appeared in a single order.

### D17 — LeetCode SQL: Employees Earning More Than Their Managers
*Technique: Self-join*
Mini schema: `Employee(id, name, salary, managerId)`

Return the names of employees who earn more than their own direct manager.

---

## Week 4 (Phase 1) — Subqueries & EXPLAIN

### D19 — StockPilot: products priced above the average product price
*Technique: Subquery*

List every product priced above the average price across all products.

### D20 — StockPilot: orders by users with zero stock movements
*Technique: Subquery*

Return orders placed by users who have never recorded a single stock
movement. Think carefully about how `NULL`s behave if you reach for `NOT
IN`.

### D21 — LeetCode SQL: Second Highest Salary
*Technique: Subquery / ranking*
Mini schema: `Employee(id, salary)`

Return the second-highest **distinct** salary, or `NULL` if it doesn't
exist — including the edge case where the table only has one distinct
salary.

### D22 — StockPilot: EXPLAIN ANALYZE the low-stock query
*Technique: Query planning*

Take D2's query, run `EXPLAIN ANALYZE` on it, then try an index that could
help and re-run. Note whether the plan changes, and at what table size it
would start to matter.

### D23 — LeetCode SQL: Duplicate Emails
*Technique: Aggregation*
Mini schema: `Person(id, email)`

Return every email address that appears more than once.

---

## Week 5 (Phase 2) — QuickServe Reporting

### D25 — QuickServe: daily revenue per cashier
*Technique: Join + aggregation*

For a given day, compute total revenue (quantity × unit price, summed) per
cashier, counting only completed receipts.

### D26 — LeetCode SQL: Department Highest Salary
*Technique: Subquery + join*
Mini schema: `Employee(id, name, salary, departmentId)`,
`Department(id, name)`

Return department name, employee name, and salary for every employee who
earns the highest salary in their own department (include ties).

### D27 — QuickServe: receipts with at least one return
*Technique: Existence check*

Return `receipt_id, cashier_id, created_at` for receipts that have at least
one associated return.

### D28 — QuickServe: products never discounted
*Technique: Anti-join*

Return the products that have never been sold with a discount applied.

### D29 — LeetCode SQL: Trips and Users
*Technique: Multi-join + conditional aggregation*
Mini schema: `Trips(id, client_id, driver_id, city_id, status, request_at)`,
`Users(users_id, banned, role)`

For each date in a given range, compute the cancellation rate among trip
requests where **neither** the client **nor** the driver is banned, rounded
to 2 decimals.

---

## Week 6 (Phase 2) — Window Functions I

### D31 — QuickServe: rank products by qty sold
*Technique: Window function*

Return every product's total quantity sold, and its rank among all products
by that total.

### D32 — QuickServe: running total of daily sales
*Technique: Window function*

Given daily revenue totals, return each day's revenue alongside the
cumulative total up to and including that day.

### D33 — LeetCode SQL: Rank Scores
*Technique: Window function*
Mini schema: `Scores(id, score)`

Return `score, rank`, where equal scores share the same rank and there are
no gaps in the ranking afterward.

### D34 — QuickServe: EXPLAIN ANALYZE the cached product-search query
*Technique: Query planning*

Run `EXPLAIN ANALYZE` on the product-search-by-name query, and write down
why a plain B-tree index can't help a leading-wildcard search — and what
kind of index would.

### D35 — LeetCode SQL: Consecutive Numbers
*Technique: Window function*
Mini schema: `Logs(id, num)`

Find every number that appears at least 3 times in a row, reading rows in
increasing `id` order.

---

## Week 7 (Phase 2) — PeopleOps I

### D37 — PeopleOps: employees with more than 3 pending leave requests
*Technique: Aggregation*

Return employees who currently have more than 3 pending leave requests.

### D38 — LeetCode SQL: Managers with at Least 5 Direct Reports
*Technique: Self-join + aggregation*
Mini schema: `Employee(id, name, department, managerId)`

Return the names of managers with 5 or more people reporting directly to
them.

### D39 — PeopleOps: average leave balance per department
*Technique: Join + aggregation*

Return the average remaining leave balance (accrued minus used) per
department.

### D40 — PeopleOps: leave requests approved same-day vs delayed
*Technique: Conditional labeling*

For every approved leave request, label it `same-day` or `delayed`
depending on whether it was approved the same calendar day it was
requested.

### D41 — LeetCode SQL: Employee Bonus
*Technique: Outer join*
Mini schema: `Employee(empId, name, supervisorId, salary)`,
`Bonus(empId, bonus)`

Return the name and bonus of every employee whose bonus is less than 1000 —
including employees with no bonus row at all.

---

## Week 8 (Phase 2) — PeopleOps II

### D43 — PeopleOps: employees who never took leave
*Technique: Anti-join*

Return employees who have never filed a single leave request.

### D44 — PeopleOps: leave requests pending 3+ days
*Technique: Date filtering*

Return leave requests that have been sitting in `pending` status for 3 or
more days.

### D45 — LeetCode SQL: Investments in 2016
*Technique: Aggregation with multiple conditions*
Mini schema: `Insurance(pid, tiv_2015, tiv_2016, lat, lon)`

Return the total 2016 investment value summed across policyholders who both
(a) share their 2015 investment value with at least one other policyholder,
and (b) have a location not shared with anyone else.

### D46 — PeopleOps: monthly accrual totals per employee
*Technique: Aggregation by date bucket*

Return total accrued leave days per employee, grouped by month.

### D47 — LeetCode SQL: Sales Person
*Technique: Multi-table anti-join*
Mini schema: `SalesPerson(sales_id, name)`, `Company(com_id, name)`,
`Orders(order_id, sales_id, com_id)`

Return the names of sales persons who have never had an order involving the
company named `"RED"`.

---

## Week 9 (Phase 3) — PeopleOps Wrap & WareFlow Scaffold

### D49 — PeopleOps: reminder-job candidates, final polish
*Technique: Date filtering*

Same as D44, but now also exclude requests that already had a reminder
sent (assume a `reminder_sent_at` column).

### D50 — LeetCode SQL: Triangle Judgement
*Technique: Conditional logic*
Mini schema: `Triangle(x, y, z)`

For each row of three side lengths, report whether they can form a valid
triangle.

### D51 — WareFlow: stock levels below zero
*Technique: Data-integrity check*

Find any `stock_levels` row where quantity has gone negative — this should
never happen; treat any result as a bug.

### D52 — WareFlow: total stock per warehouse
*Technique: Aggregation*

Return total quantity on hand per warehouse.

### D53 — LeetCode SQL: Exchange Seats
*Technique: Conditional row transformation*
Mini schema: `Seat(id, student)`

Return the seating list with every adjacent pair of ids swapped (1↔2, 3↔4,
…); if the row count is odd, the last id keeps its own seat. Do it as a
single `SELECT`, not an `UPDATE`.

---

## Week 10 (Phase 3) — WareFlow Domain

### D55 — WareFlow: warehouses with more distinct products than average
*Technique: Subquery*

Return warehouses that stock more distinct products than the average
warehouse does.

### D56 — WareFlow: products in one warehouse but not another
*Technique: Set comparison*

Given two warehouse ids, return the products stocked in the first but not
the second.

### D57 — LeetCode SQL: Swap Salary
*Technique: Conditional update*
Mini schema: `Salary(id, name, sex, salary)`

Update the table so every `'m'` becomes `'f'` and every `'f'` becomes
`'m'` in the `sex` column, in a single statement.

### D58 — WareFlow: stock_movements reason breakdown
*Technique: Aggregation*

Return a count and total quantity delta grouped by movement reason.

### D59 — LeetCode SQL: Tree Node
*Technique: Self-join + conditional classification*
Mini schema: `Tree(id, p_id)`

Classify every node as `'Root'`, `'Leaf'`, or `'Inner'`, based on whether
it has a parent and whether anything points to it as a parent.

---

## Week 11 (Phase 3) — WareFlow / RabbitMQ Week

### D61 — WareFlow: reservations pending longer than 1 hour
*Technique: Date filtering*

Return reservations that have been pending for more than an hour.

### D62 — WareFlow: products most frequently reserved
*Technique: Aggregation*

Return the products with the highest number of reservations.

### D63 — LeetCode SQL: Human Traffic of Stadium
*Technique: Window function*
Mini schema: `Stadium(id, visit_date, people)`

Return every row that's part of a run of 3 or more **consecutive ids**
where `people` is always at least 100.

### D64 — WareFlow: transfers stuck 'dispatched' over 24h
*Technique: Date filtering*

Return transfers that have been sitting in `dispatched` status for over 24
hours without being received.

### D65 — LeetCode SQL: Friend Requests I: Overall Acceptance Rate
*Technique: Ratio aggregation*
Mini schema: `FriendRequest(sender_id, send_to_id, request_date)`,
`RequestAccepted(requester_id, accepter_id, accept_date)`

Compute the overall acceptance rate — distinct accepted pairs divided by
distinct requested pairs — rounded to 2 decimals. Handle the case where no
requests exist at all.

---

## Week 12 (Phase 3) — Postgres Deep Dive

### D67 — WareFlow: EXPLAIN ANALYZE reservation query before/after row-lock index
*Technique: Query planning*

Run `EXPLAIN ANALYZE` on the query used to reserve stock (the one with the
row lock). Confirm it's actually using an index rather than scanning the
table.

### D68 — WareFlow: stock_movements query on new monthly partition vs old
*Technique: Query planning*

Compare `EXPLAIN ANALYZE` for a date-range query that stays within one
partition vs. one that spans several months.

### D69 — LeetCode SQL: Department Top Three Salaries
*Technique: Window function*
Mini schema: `Employee(id, name, salary, departmentId)`,
`Department(id, name)`

Return the top 3 distinct salaries within each department.

### D70 — WareFlow: a query that would deadlock under bad lock ordering
*Technique: Transaction design*

Write two `UPDATE` statements that lock the same two warehouses in
opposite orders, and explain in a one-line comment why running them
concurrently deadlocks.

### D71 — LeetCode SQL: Nth Highest Salary
*Technique: Subquery / ranking*
Mini schema: `Employee(id, salary)`

Return the Nth highest distinct salary (N given as a parameter), or `NULL`
if it doesn't exist.

---

## Week 13 (Phase 3) — WareFlow Wrap

### D73 — WareFlow: warehouse stock report
*Technique: Join + conditional labeling*

For each warehouse and product, return quantity, stock value, and a
low-stock flag.

### D74 — LeetCode SQL: Actors and Directors Who Cooperated At Least Three Times
*Technique: Aggregation*
Mini schema: `ActorDirector(actor_id, director_id, timestamp)`

Return actor/director pairs that have worked together at least 3 times.

### D75 — WareFlow: paginated GET /warehouses/{id}/stock query
*Technique: Pagination*

Write a paginated version of the warehouse stock list query, and confirm
it's using an index rather than sorting the whole table on every page.

### D76 — LeetCode SQL: Product Sales Analysis I
*Technique: Join*
Mini schema: `Sales(sale_id, product_id, year, quantity, price)`,
`Product(product_id, product_name)`

Return product name, year, and price for every sale.

### D77 — WareFlow: recursive CTE over one product's transfer history
*Technique: Recursive CTE*

Write a recursive query that walks a single product's transfer history in
creation order. (Recursive CTEs are more naturally suited to hierarchical
data like StockPilot's `categories.parent_id` tree — try it there
afterward too.)

---

## Week 14 (Phase 4) — CarePoint I

### D79 — CarePoint: doctors with overlapping appointments
*Technique: Self-join on ranges*

Find pairs of appointments for the same doctor whose time slots overlap.

### D80 — LeetCode SQL: Patients With a Condition
*Technique: Pattern matching*
Mini schema: `Patients(patient_id, patient_name, conditions)`

Return patients whose `conditions` field contains a code starting with
`DIAB1` as a whole word — not as a substring of a longer code.

### D81 — CarePoint: appointment count per doctor per day
*Technique: Aggregation*

Return how many appointments each doctor has on each day.

### D82 — CarePoint: patients with no documents on file
*Technique: Anti-join*

Return patients who have no documents attached to their record.

### D83 — LeetCode SQL: The Most Recent Orders for Each Product
*Technique: Window function*
Mini schema: `Orders(order_id, order_date, customer_id, product_id)`,
`Product(product_id, product_name)`

Return the most recent order date for each product.

---

## Week 15 (Phase 4) — CarePoint II

### D85 — CarePoint: appointments in next 24h needing a reminder
*Technique: Date filtering*

Return appointments starting within the next 24 hours.

### D86 — CarePoint: doctors with the most documents on their patients
*Technique: Multi-join + aggregation*

Return the doctors whose patients collectively have the most documents on
file.

### D87 — LeetCode SQL: Reformat Department Table
*Technique: Pivot*
Mini schema: `Department(id, revenue, month)`

Pivot the monthly revenue rows into one row per department id, with one
column per month.

### D88 — CarePoint: EXPLAIN ANALYZE the doctor-schedule query
*Technique: Query planning*

Run `EXPLAIN ANALYZE` on the doctor-schedule lookup query and judge whether
it's cheap enough that caching is buying real speed rather than masking a
missing index.

### D89 — LeetCode SQL: Queries Quality and Percentage
*Technique: Aggregation with computed columns*
Mini schema: `Queries(query_name, result, position, rating)`

Per `query_name`, compute an average "quality" score (rating relative to
position) and the percentage of ratings below 3.

---

## Week 16 (Phase 4) — LedgerBase I

### D91 — LedgerBase: verify every journal_entry balances
*Technique: Aggregation / integrity check*

Find any `journal_entry` where total debits don't equal total credits —
should return zero rows.

### D92 — LedgerBase: account balance = debits minus credits
*Technique: Conditional aggregation*

For each account, compute its balance from its journal lines, using the
correct sign convention for its account type.

### D93 — LeetCode SQL: Rising Temperature — window function version
*Technique: Window function*

Redo D15 without a self-join, comparing each row directly to the one
before it.

### D94 — LedgerBase: unbalanced entries that slipped through
*Technique: Integrity check*

Same shape as D91, framed as an audit query you'd run on a schedule or wire
into an alert.

### D95 — LeetCode SQL: Movie Rating
*Technique: Multi-table ranking*
Mini schema: `Movies(movie_id, title)`, `Users(user_id, name)`,
`MovieRating(movie_id, user_id, rating, created_at)`

Find (1) the user who has rated the most movies, and (2) the movie with the
highest average rating in February 2020 — ties broken alphabetically in
both cases.

---

## Week 17 (Phase 4) — LedgerBase II

### D97 — LedgerBase: overdue unpaid invoices
*Technique: Date filtering*

Return invoices past their due date that haven't been paid.

### D98 — LedgerBase: monthly revenue trend from paid invoices
*Technique: Aggregation by date bucket*

Return total revenue from paid invoices, grouped by month.

### D99 — LeetCode SQL: Replace Employee ID With The Unique Identifier
*Technique: Outer join*
Mini schema: `Employees(id, name)`, `EmployeeUNI(id, unique_id)`

Return each employee's name alongside their `unique_id` — employees without
one should still appear, with `NULL`.

### D100 — LedgerBase: trial balance report
*Technique: Aggregation*

Return total debits and credits per account type, and confirm the whole
report nets to zero.

### D101 — LeetCode SQL: Top Travellers
*Technique: Outer join + aggregation*
Mini schema: `Users(id, name)`, `Rides(id, user_id, distance)`

Return each user's total distance traveled — users with zero rides should
still show `0` — ordered by distance descending, then name.

---

## Week 18 (Phase 4) — LedgerBase Wrap

### D103 — LedgerBase: accounts with no activity this month
*Technique: Anti-join*

Return accounts with no journal line entries so far this month.

### D104 — LedgerBase: largest single journal entry this quarter
*Technique: Aggregation + ranking*

Return the journal entry with the largest total debit amount this quarter.

### D105 — LeetCode SQL: Sales Analysis I
*Technique: Join + aggregation*
Mini schema: `Product(product_id, product_name, unit_price)`,
`Sales(seller_id, product_id, buyer_id, sale_date, quantity, price)`

Return the seller(s) with the highest total sales value (include ties).

### D106 — LedgerBase: underpaid invoices
*Technique: Subquery comparison*

Return invoices where total payments received fall short of the invoice
total.

### D107 — LeetCode SQL: Sales Analysis III
*Technique: Aggregation with a range condition*
Mini schema: same as D105

Return products that were only ever sold during Spring 2019 — every sale of
that product falls within that date range.

---

## Week 19 (Phase 5) — FleetTrack Outbox

### D109 — FleetTrack: unsent outbox rows older than 5 minutes
*Technique: Date filtering*

Return outbox rows that haven't been sent yet and were created more than 5
minutes ago — this is the exact query behind the outbox-lag metric.

### D110 — LeetCode SQL: Rising Temperature — self-join with LAG variant
*Technique: Window function*

Same task as D15/D93 — write it once more, cold, no notes.

### D111 — FleetTrack: delivery stuck longest in one status
*Technique: Join + aggregation*

Return the delivery that has spent the longest time in its current status.

### D112 — FleetTrack: avg time between status transitions
*Technique: Window function*

For each delivery, compute the time gap between consecutive status-change
events, then average those gaps.

### D113 — LeetCode SQL: The Most Frequently Ordered Products for Each Customer
*Technique: Window function*
Mini schema: `Customers(customer_id, customer_name)`,
`Orders(order_id, customer_id)`, `OrderItems(order_id, product_id,
quantity)`

For each customer, return the product(s) they've ordered the most units of
(include ties).

---

## Week 20 (Phase 5) — FleetTrack CQRS/Saga

### D115 — FleetTrack: rebuild delivery_view from delivery_events by hand
*Technique: Window function*

Write the query that reconstructs each delivery's current status and
last-updated time from its raw event history — this is what the CQRS
projector runs.

### D116 — LeetCode SQL: Article Views I
*Technique: Self-referencing filter*
Mini schema: `Views(article_id, author_id, viewer_id, view_date)`

Return the distinct author ids of authors who have viewed their own
articles.

### D117 — FleetTrack: drivers with the most cancelled deliveries
*Technique: Aggregation*

Return the drivers with the highest count of cancelled deliveries.

### D118 — LeetCode SQL: Article Views II
*Technique: Self-join*
Mini schema: same as D116

Return viewer ids who viewed 2 or more different articles on the same date.

### D119 — FleetTrack: dispatcher dashboard — join vs read-model
*Technique: Query planning*

Write the live-join version of the dispatcher dashboard query (no read
model), then compare its `EXPLAIN ANALYZE` cost against querying
`delivery_view` directly.

---

## Week 21 (Phase 5) — DocuVault Search

### D121 — DocuVault: documents with the most versions
*Technique: Aggregation*

Return the documents with the highest number of versions.

### D122 — LeetCode SQL: Fix Names in a Table
*Technique: String functions*
Mini schema: `Users(user_id, name)`

Return each name with only its first letter capitalized and the rest
lowercased, ordered by `user_id`.

### D123 — DocuVault: documents tagged with more than 3 tags
*Technique: Aggregation*

Return documents that have more than 3 tags attached.

### D124 — DocuVault: latest version per document
*Technique: Window function*

Return only the most recent version row for each document.

### D125 — LeetCode SQL: Recyclable and Low Fat Products
*Technique: Filtering*
Mini schema: `Products(product_id, low_fats, recyclable)`

Return the product ids that are both low-fat and recyclable — a breather
before Week 22.

---

## Week 22 (Phase 5) — Kubernetes/Replication Wrap

### D127 — DocuVault: documents never tagged
*Technique: Anti-join*

Return documents that have no tags attached at all.

### D128 — LeetCode SQL: Primary Department for Each Employee
*Technique: Set operations*
Mini schema: `Employee(employee_id, department_id, primary_flag)`

Return exactly one department per employee — their primary one if flagged,
or their only department if they belong to just one.

### D129 — DocuVault: tags frequently used together
*Technique: Self-join*

Return pairs of tags that frequently appear on the same document together,
most common pairs first.

### D130 — DocuVault: EXPLAIN ANALYZE a metadata query on replica vs primary
*Technique: Query planning*

Run the same metadata query against both the primary and the read-replica
connection, and confirm the replica is actually being used.

### D131 — LeetCode SQL: Calculate Special Bonus
*Technique: Conditional logic*
Mini schema: `Employees(employee_id, name, salary)`

Compute a bonus equal to salary for employees with an odd id whose name
doesn't start with `'M'` — everyone else gets `0`.

---

## Week 25 (Phase 6) — PayFlow Idempotency

### D145 — PayFlow: duplicate idempotency keys with different request hashes
*Technique: Aggregation / integrity check*

Find any `idempotency_key` associated with more than one distinct request
hash — should return zero rows.

### D146 — LeetCode SQL: Duplicate Emails revisited
*Technique: Aggregation*

Apply the exact pattern from D23 to PayFlow's own `webhook_events` table,
keyed on `provider_event_id` instead of email.

### D147 — PayFlow: webhook_events received more than once per provider_event_id
*Technique: Aggregation*

Same query as D146 — this is the dedup check your idempotent webhook
handler needs to satisfy.

### D148 — PayFlow: payment_intents stuck 'pending' longer than 10 minutes
*Technique: Date filtering*

Return payment intents that have been pending for more than 10 minutes.

### D149 — LeetCode SQL: Employees Whose Manager Left the Company
*Technique: Anti-join*
Mini schema: `Employees(employee_id, name, manager_id, salary)`

Return employee ids whose `manager_id` points at someone no longer in the
table.

---

## Week 26 (Phase 6) — PayFlow Security & Load Testing

### D151 — PayFlow: refunds exceeding their original payment amount
*Technique: Join + integrity check*

Find refunds whose amount exceeds the original payment's amount — should
return zero rows.

### D152 — PayFlow: same-day vs delayed refunds
*Technique: Conditional aggregation*

Label each refund `same-day` or `delayed` relative to its original payment,
then count each group.

### D153 — PayFlow: EXPLAIN ANALYZE the idempotency-key lookup under load
*Technique: Query planning*

Run `EXPLAIN ANALYZE` on the idempotency-key lookup, confirm it uses an
index, then test what happens to the plan without one — that's the
bottleneck the load test is supposed to find.

### D154 — PayFlow: audit log for one payment_intent, ordered chronologically
*Technique: Filtering + ordering*

Return every audit-log entry for a single `payment_intent`, oldest first.

### D155 — LeetCode SQL: Find Followers Count
*Technique: Aggregation*
Mini schema: `Followers(user_id, follower_id)`

Return each user's follower count. Then apply the same shape to PayFlow's
`audit_log` to count state changes per `payment_intent`.

---

## Week 27 (Phase 6) — AtlasMarket Vendor Scoping

### D157 — AtlasMarket: revenue per vendor this month
*Technique: Join + aggregation*

Return each vendor's total revenue for the current month.

### D158 — LeetCode SQL: Product Sales Analysis III
*Technique: Window function*
Mini schema: `Sales(sale_id, product_id, year, quantity, price)`

Return the sales rows from the first year each product was ever sold.

### D159 — AtlasMarket: vendors with no products listed
*Technique: Anti-join*

Return vendors who haven't listed a single product yet.

### D160 — AtlasMarket: top 5 vendors by order count
*Technique: Aggregation*

Return the 5 vendors with the most distinct orders.

### D161 — LeetCode SQL: The Most Recent Three Orders
*Technique: Window function*
Mini schema: `Customers(customer_id, name)`,
`Orders(order_id, order_date, customer_id)`

Return each customer's 3 most recent orders.

---

## Week 28 (Phase 6) — AtlasMarket Checkout & Capstone Review

### D163 — AtlasMarket: orders split across 2+ vendors
*Technique: Aggregation*

Return orders that were split across two or more vendors.

### D164 — AtlasMarket: per-vendor payout reconciliation
*Technique: Join + comparison*

For each vendor, compare their ledger payout total against their expected
order total, and flag any mismatch.

### D165 — Capstone review: rewrite Week 14's partition-aware query from memory
Redo D68 without looking it up.

### D166 — Capstone review: rewrite Week 8's window-function ranking query from memory
Redo D31 without looking it up.

### D167 — Capstone: the one query you'd hand an interviewer
Write, cleanly and from scratch, the query for "top vendor by revenue this
month" — no notes this time. It should be something you'd be comfortable
reading aloud, cold, in a live interview.
