# Roadmap Progress Tracker

Check off each item as you finish it. 156 days total (130 weekdays + 26 Saturday review days) across 26 weeks / 6 phases. Every day has 5 independent checkboxes — Theory, Mini Exercise, Project, DSA, SQL — so you can track exactly what's left on a day you only half-finished.

---

## Phase 1 — Foundations (Weeks 1-4)

### Week 1 — Decorators, Closures, Project Skeleton

**D1 (Mon)**
- [ ] Theory: Functions as objects, closures — *Fluent Python Ch.7 §1-2*
- [ ] Mini Exercise: Write a `@timer` decorator
- [ ] Project: Scaffold repo: folder structure, `pyproject.toml`, ruff/mypy config
- [ ] DSA: Contains Duplicate
- [ ] SQL: Combine Two Tables

**D2 (Tue)**
- [ ] Theory: Decorators with args, `functools.wraps` — *Fluent Python Ch.7 §3*
- [ ] Mini Exercise: Write `@retry(times=3)`
- [ ] Project: Define `User`, `Product`, `Category` SQLAlchemy models
- [ ] DSA: Valid Anagram
- [ ] SQL: StockPilot: products where current_stock < reorder_level

**D3 (Wed)**
- [ ] Theory: Class-based decorators, stacking order — *docs.python.org `functools`*
- [ ] Mini Exercise: Combine `@timer` + `@retry`, verify stacking order
- [ ] Project: Add `Supplier`, `StockMovement`, `Order`, `OrderItem` models + Alembic init migration
- [ ] DSA: Two Sum
- [ ] SQL: StockPilot: products with no supplier

**D4 (Thu)**
- [ ] Theory: Reference counting basics — *Fluent Python Ch.6 (weak refs intro)*
- [ ] Mini Exercise: `sys.getrefcount` experiment script
- [ ] Project: Implement `core/config.py` (Pydantic settings) + `db/session.py` (async engine/session)
- [ ] DSA: Group Anagrams
- [ ] SQL: Find Customer Referee

**D5 (Fri)**
- [ ] Theory: Reference cycles + `gc` module — *docs.python.org `gc`*
- [ ] Mini Exercise: Deliberately create and detect a reference cycle
- [ ] Project: Docker Compose: `api` + `postgres` services, healthcheck
- [ ] DSA: Top K Frequent Elements
- [ ] SQL: StockPilot: categories with no products

**D6 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo `@retry` decorator from memory, no notes
- [ ] Project: Mentally walk through why models are shaped this way
- [ ] DSA: Review: redo Thursday's problem from memory — Group Anagrams
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — StockPilot: products where current_stock < reorder_level

### Week 2 — Generators, Iterators, Context Managers

**D7 (Mon)**
- [ ] Theory: Iterator protocol (`__iter__`/`__next__`) — *Fluent Python Ch.17 §1-2*
- [ ] Mini Exercise: Custom `Countdown` iterator class
- [ ] Project: Build `repositories/product_repository.py` (basic CRUD queries)
- [ ] DSA: Product of Array Except Self
- [ ] SQL: StockPilot: total stock value per category

**D8 (Tue)**
- [ ] Theory: Generator functions, `yield` — *Fluent Python Ch.17 §3*
- [ ] Mini Exercise: Lazy CSV row generator for 1M-row fake product import
- [ ] Project: Build `services/product_service.py` (validation rules on top of repo)
- [ ] DSA: Valid Sudoku
- [ ] SQL: Big Countries

**D9 (Wed)**
- [ ] Theory: Generator expressions, `yield from`, coroutine basics — *Fluent Python Ch.17 §4-5*
- [ ] Mini Exercise: Chain 3 generators with `yield from`
- [ ] Project: Build `api/products.py` router wired to service
- [ ] DSA: Encode and Decode Strings
- [ ] SQL: StockPilot: count orders per status

**D10 (Thu)**
- [ ] Theory: Context manager protocol — *Fluent Python Ch.15/16 (context mgrs)*
- [ ] Mini Exercise: Class-based context manager: auto-rollback DB session on exception
- [ ] Project: Wire real DB session as a context-managed dependency in FastAPI
- [ ] DSA: Longest Consecutive Sequence
- [ ] SQL: StockPilot: top 5 products by units sold

**D11 (Fri)**
- [ ] Theory: `@contextmanager` decorator version — *docs.python.org `contextlib`*
- [ ] Mini Exercise: Rewrite Thursday's context manager using `@contextmanager`
- [ ] Project: Add pagination + filtering (`category_id`, `low_stock`) to `GET /products`
- [ ] DSA: Valid Palindrome
- [ ] SQL: Classes More Than 5 Students

**D12 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo lazy CSV generator from memory
- [ ] Project: Re-read your own service layer, note anything that smells like a leaked business rule
- [ ] DSA: Review: redo Thursday's problem from memory — Longest Consecutive Sequence
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Big Countries

### Week 3 — Typing, Dataclasses, Descriptors, Indexing

**D13 (Mon)**
- [ ] Theory: `typing` deep dive: generics, `TypeVar` — *Fluent Python Ch.8*
- [ ] Mini Exercise: Generic `Stack[T]` class
- [ ] Project: Add `SupplierRepository`, `CategoryRepository`
- [ ] DSA: Two Sum II - Input Array Is Sorted
- [ ] SQL: StockPilot: orders with item count + total value

**D14 (Tue)**
- [ ] Theory: `Protocol` and structural typing — *mypy docs on Protocols*
- [ ] Mini Exercise: Typed `Repository[T]` Protocol abstraction
- [ ] Project: Refactor existing repositories to satisfy the `Repository[T]` protocol
- [ ] DSA: 3Sum
- [ ] SQL: StockPilot: stock movements joined to the user who made them

**D15 (Wed)**
- [ ] Theory: `dataclasses`: fields, `frozen`, `__post_init__` — *Fluent Python Ch.9*
- [ ] Mini Exercise: Immutable `Money` value object (cents-based, no float bugs)
- [ ] Project: Use `Money` dataclass for `price_cents`/order totals instead of raw ints everywhere
- [ ] DSA: Container With Most Water
- [ ] SQL: Rising Temperature

**D16 (Thu)**
- [ ] Theory: Descriptors: data vs non-data — *Fluent Python Ch.23*
- [ ] Mini Exercise: Descriptor-based `PositiveInt` field validator
- [ ] Project: (Applied conceptually — note in `docs/notes.md` where descriptors *would* replace repeated Pydantic validators)
- [ ] DSA: Trapping Rain Water
- [ ] SQL: StockPilot: suppliers whose products never sold

**D17 (Fri)**
- [ ] Theory: Postgres indexing: B-tree, composite index column order — *Use The Index Luke, Postgres docs Ch.11*
- [ ] Mini Exercise: Run `EXPLAIN ANALYZE` on `GET /orders?status=&from=&to=` before/after adding index
- [ ] Project: Add composite index `(status, created_at)` on `orders`, write the Alembic migration
- [ ] DSA: Best Time to Buy and Sell Stock
- [ ] SQL: Employees Earning More Than Their Managers

**D18 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo `Repository[T]` Protocol from memory
- [ ] Project: Re-read `Money` usage across codebase for consistency
- [ ] DSA: Review: redo Thursday's problem from memory — Trapping Rain Water
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — StockPilot: stock movements joined to the user who made them

### Week 4 — Async Basics, Transactions, Race Conditions, Testing, Docker CI

**D19 (Mon)**
- [ ] Theory: `async`/`await` mechanics, event loop basics — *RealPython asyncio guide*
- [ ] Mini Exercise: Concurrent fetch from 5 fake supplier endpoints with `asyncio.gather`
- [ ] Project: Build `OrderService.create_order` — happy path only, no concurrency handling yet
- [ ] DSA: Longest Substring Without Repeating Characters
- [ ] SQL: StockPilot: products priced above the average product price

**D20 (Tue)**
- [ ] Theory: Transactions, isolation levels, dirty/phantom reads — *Postgres docs Ch.13 §1-2*
- [ ] Mini Exercise: Write a script that intentionally reproduces a dirty read at `READ UNCOMMITTED` (Postgres treats it as READ COMMITTED — explain why)
- [ ] Project: Wrap `create_order` stock decrement in a transaction with `SELECT ... FOR UPDATE`
- [ ] DSA: Longest Repeating Character Replacement
- [ ] SQL: StockPilot: orders by users with zero stock movements

**D21 (Wed)**
- [ ] Theory: Row locks, deadlocks (conceptually) — *Postgres docs Ch.13 §3*
- [ ] Mini Exercise: Reproduce a deadlock with two scripts locking rows in opposite order, observe Postgres auto-cancel one
- [ ] Project: Handle "insufficient stock" as a clean 409 response, not a 500
- [ ] DSA: Permutation in String
- [ ] SQL: Second Highest Salary

**D22 (Thu)**
- [ ] Theory: Pytest architecture: fixtures, factories, mocking philosophy — *pytest docs on fixtures*
- [ ] Mini Exercise: Convert 3 hand-written test setups to `factory_boy` factories
- [ ] Project: Add `factories.py`, replace manual test data across suite
- [ ] DSA: Valid Parentheses
- [ ] SQL: StockPilot: EXPLAIN ANALYZE the low-stock query

**D23 (Fri)**
- [ ] Theory: CI pipelines, Docker layer caching, lightweight load testing — *GitHub Actions docs*
- [ ] Mini Exercise: Run `hey -n 500 -c 20 http://localhost:8000/products` against your own API, read the p95
- [ ] Project: Finalize `.github/workflows/ci.yml` (lint + mypy + pytest against Postgres service container)
- [ ] DSA: Min Stack
- [ ] SQL: Duplicate Emails

**D24 (Sat)**
- [ ] Theory: **Phase 1 wrap review**
- [ ] Mini Exercise: Redo the deadlock reproduction from memory, explain it out loud
- [ ] Project: Write `docs/postmortem.md`: what you'd do differently, what's deferred to Phase 2 and why
- [ ] DSA: Review: redo Thursday's problem from memory — Valid Parentheses
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — StockPilot: orders by users with zero stock movements

---

## Phase 2 — Concurrency, Django/DRF, Caching (Weeks 5-8)

### Week 5 — GIL, Threading, Multiprocessing, Django Scaffold

**D25 (Mon)**
- [ ] Theory: GIL mechanics — *Fluent Python Ch.19*
- [ ] Mini Exercise: GIL demo script (threads vs processes, CPU-bound)
- [ ] Project: New repo `quickserve/`, Django project init, settings split
- [ ] DSA: Evaluate Reverse Polish Notation
- [ ] SQL: QuickServe: daily revenue per cashier

**D26 (Tue)**
- [ ] Theory: `threading` module, I/O-bound concurrency — *Python docs `threading`*
- [ ] Mini Exercise: Multithreaded file downloader
- [ ] Project: `catalog` app: `Product` model + admin registration
- [ ] DSA: Generate Parentheses
- [ ] SQL: Department Highest Salary

**D27 (Wed)**
- [ ] Theory: `multiprocessing`, process overhead — *Python docs `multiprocessing`*
- [ ] Mini Exercise: Multiprocessing image resizer with `Pool`
- [ ] Project: `sales` app: `Receipt`, `ReceiptItem` models
- [ ] DSA: Daily Temperatures
- [ ] SQL: QuickServe: receipts with at least one return

**D28 (Thu)**
- [ ] Theory: Race conditions, minimal repro
- [ ] Mini Exercise: Deliberately trigger a race with 2 threads incrementing a shared counter
- [ ] Project: `discounts` app: `Discount` model + validation rules
- [ ] DSA: Car Fleet
- [ ] SQL: QuickServe: products never discounted

**D29 (Fri)**
- [ ] Theory: Locks, deadlocks (4 conditions)
- [ ] Mini Exercise: Fix Thursday's race with a `Lock`; then reproduce a deadlock on purpose
- [ ] Project: DRF serializers for products/receipts
- [ ] DSA: Binary Search
- [ ] SQL: Trips and Users

**D30 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo GIL demo from memory, explain results out loud
- [ ] Project: Re-read models for Django idioms vs FastAPI habits carried over wrongly
- [ ] DSA: Review: redo Thursday's problem from memory — Car Fleet
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Department Highest Salary

### Week 6 — DRF ViewSets, Checkout Flow, Redis Caching

**D31 (Mon)**
- [ ] Theory: DRF ViewSets, routers — *DRF docs Viewsets*
- [ ] Mini Exercise: —
- [ ] Project: `ProductViewSet` + `GET /products?search=`
- [ ] DSA: Search a 2D Matrix
- [ ] SQL: QuickServe: rank products by qty sold

**D32 (Tue)**
- [ ] Theory: Service layer in Django (keeping views thin) — *Two Scoops Ch.7*
- [ ] Mini Exercise: —
- [ ] Project: `checkout_service.py`: build receipt from cart payload
- [ ] DSA: Koko Eating Bananas
- [ ] SQL: QuickServe: running total of daily sales

**D33 (Wed)**
- [ ] Theory: `select_related`/`prefetch_related`, N+1 in Django ORM — *Django docs QuerySet*
- [ ] Mini Exercise: Reproduce N+1 on receipt-items listing, fix it
- [ ] Project: `POST /checkout` endpoint wired end-to-end
- [ ] DSA: Find Minimum in Rotated Sorted Array
- [ ] SQL: Rank Scores

**D34 (Thu)**
- [ ] Theory: Redis cache-aside pattern — *Redis docs caching*
- [ ] Mini Exercise: Standalone cache-aside demo script
- [ ] Project: Add Redis cache on `GET /products?search=`, TTL + invalidation on price update
- [ ] DSA: Search in Rotated Sorted Array
- [ ] SQL: QuickServe: EXPLAIN ANALYZE the cached product-search query

**D35 (Fri)**
- [ ] Theory: Benchmarking, `hey`/`locust` basics
- [ ] Mini Exercise: Load-test `/products` before/after cache, record p95
- [ ] Project: Write `docs/caching-notes.md` with before/after numbers
- [ ] DSA: Reverse Linked List
- [ ] SQL: Consecutive Numbers

**D36 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo cache-aside demo from memory
- [ ] Project: Re-check invalidation covers every write path to `price_cents`
- [ ] DSA: Review: redo Thursday's problem from memory — Search in Rotated Sorted Array
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — QuickServe: running total of daily sales

### Week 7 — Returns, Reports, JWT Refresh, Queues → PeopleOps Starts

**D37 (Mon)**
- [ ] Theory: `simplejwt` access/refresh flow — *djangorestframework-simplejwt docs*
- [ ] Mini Exercise: —
- [ ] Project: Wire refresh-token auth into QuickServe
- [ ] DSA: Merge Two Sorted Lists
- [ ] SQL: PeopleOps: employees with more than 3 pending leave requests

**D38 (Tue)**
- [ ] Theory: DRF throttling internals — *DRF throttling docs*
- [ ] Mini Exercise: —
- [ ] Project: Add `UserRateThrottle` to `/checkout`
- [ ] DSA: Reorder List
- [ ] SQL: Managers with at Least 5 Direct Reports

**D39 (Wed)**
- [ ] Theory: Returns flow, daily sales report query
- [ ] Mini Exercise: —
- [ ] Project: `POST /returns`, `GET /reports/daily-sales`
- [ ] DSA: Remove Nth Node From End of List
- [ ] SQL: PeopleOps: average leave balance per department

**D40 (Thu)**
- [ ] Theory: `queue.Queue`, producer/consumer pattern — *Python docs `queue`*
- [ ] Mini Exercise: Producer/consumer mini script with `Lock`
- [ ] Project: New repo `peopleops/`: Django scaffold, `Employee`, `LeaveRequest`, `LeaveBalance` models
- [ ] DSA: Copy List with Random Pointer
- [ ] SQL: PeopleOps: leave requests approved same-day vs delayed

**D41 (Fri)**
- [ ] Theory: Manager-approval permission modeling — *DRF permissions docs*
- [ ] Mini Exercise: —
- [ ] Project: `LeaveRequestViewSet` + approve/reject actions, manager-only permission
- [ ] DSA: Add Two Numbers
- [ ] SQL: Employee Bonus

**D42 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo producer/consumer from memory
- [ ] Project: Trace the approval endpoint's synchronous email call — note exactly where it blocks
- [ ] DSA: Review: redo Thursday's problem from memory — Copy List with Random Pointer
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Managers with at Least 5 Direct Reports

### Week 8 — The Synchronous-Email Pain Point, Celery Intro, Phase Wrap

**D43 (Mon)**
- [ ] Theory: Why synchronous side-effects in a request are dangerous
- [ ] Mini Exercise: Time the approval endpoint with a deliberately slow fake mail server (`time.sleep`)
- [ ] Project: Write `docs/blocking-email-problem.md` documenting the felt pain, numbers included
- [ ] DSA: Linked List Cycle
- [ ] SQL: PeopleOps: employees who never took leave

**D44 (Tue)**
- [ ] Theory: Celery architecture: broker, worker, result backend — *Celery docs "First Steps"*
- [ ] Mini Exercise: Celery producer/consumer mini task queue (`add.delay()`)
- [ ] Project: Add `celery.py` app config + Redis broker to `peopleops/`
- [ ] DSA: Find the Duplicate Number
- [ ] SQL: PeopleOps: leave requests pending 3+ days

**D45 (Wed)**
- [ ] Theory: Task retries, idempotent tasks — *Celery docs retries*
- [ ] Mini Exercise: —
- [ ] Project: Convert approval-email send into a Celery task with retry(3)
- [ ] DSA: LRU Cache
- [ ] SQL: Investments in 2016

**D46 (Thu)**
- [ ] Theory: Leave balance accrual logic
- [ ] Mini Exercise: —
- [ ] Project: `LeaveBalance` accrual calculation (manual trigger for now — cron comes Phase 3)
- [ ] DSA: Invert Binary Tree
- [ ] SQL: PeopleOps: monthly accrual totals per employee

**D47 (Fri)**
- [ ] Theory: Phase 2 wrap: CI update (add Redis+Celery to pipeline) — *GitHub Actions docs*
- [ ] Mini Exercise: —
- [ ] Project: Full CI green on both projects, Docker Compose gains `redis` + `celery-worker` services
- [ ] DSA: Maximum Depth of Binary Tree
- [ ] SQL: Sales Person

**D48 (Sat)**
- [ ] Theory: **Phase 2 wrap review**
- [ ] Mini Exercise: Redo Celery retry demo from memory
- [ ] Project: Write `docs/postmortem-phase2.md`
- [ ] DSA: Review: redo Thursday's problem from memory — Invert Binary Tree
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — PeopleOps: leave requests pending 3+ days

---

## Phase 3 — Distributed Systems (Weeks 9-13)

### Week 9 — PeopleOps Scheduling + Mini-Projects

**D49 (Mon)**
- [ ] Theory: Celery Beat scheduling — *Celery Beat docs*
- [ ] Mini Exercise: —
- [ ] Project: Monthly leave-accrual scheduled task
- [ ] DSA: Diameter of Binary Tree
- [ ] SQL: PeopleOps: reminder-job candidates, final polish

**D50 (Tue)**
- [ ] Theory: Reminder-job pattern
- [ ] Mini Exercise: —
- [ ] Project: 3-day unapproved-request reminder job
- [ ] DSA: Balanced Binary Tree
- [ ] SQL: Triangle Judgement

**D51 (Wed)**
- [ ] Theory: Dependency injection theory
- [ ] Mini Exercise: Mini DI container (register/resolve)
- [ ] Project: —
- [ ] DSA: Same Tree
- [ ] SQL: WareFlow: stock levels below zero

**D52 (Thu)**
- [ ] Theory: How ORMs work internally — *SQLAlchemy source skim (`orm/session.py` overview)*
- [ ] Mini Exercise: Mini-ORM: dict-row → object mapper + tiny query builder
- [ ] Project: —
- [ ] DSA: Subtree of Another Tree
- [ ] SQL: WareFlow: total stock per warehouse

**D53 (Fri)**
- [ ] Theory: PeopleOps wrap
- [ ] Mini Exercise: —
- [ ] Project: Finalize PeopleOps, `docs/postmortem-peopleops.md`, tag `v0.2-peopleops-final`
- [ ] DSA: Lowest Common Ancestor of a BST
- [ ] SQL: Exchange Seats

**D54 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo mini-ORM query builder from memory
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Subtree of Another Tree
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Triangle Judgement

### Week 10 — WareFlow Scaffold, DDD-lite, Unit of Work

**D55 (Mon)**
- [ ] Theory: Bounded contexts, aggregates — *DDD Distilled Ch.1-3*
- [ ] Mini Exercise: —
- [ ] Project: New repo `wareflow/`, define Inventory + Fulfillment context boundaries in `docs/architecture.md`
- [ ] DSA: Binary Tree Level Order Traversal
- [ ] SQL: WareFlow: warehouses with more distinct products than average

**D56 (Tue)**
- [ ] Theory: Aggregate roots, entities vs value objects — *DDD Distilled Ch.4-5*
- [ ] Mini Exercise: —
- [ ] Project: `Warehouse`, `StockLevel` entities (Inventory context)
- [ ] DSA: Binary Tree Right Side View
- [ ] SQL: WareFlow: products in one warehouse but not another

**D57 (Wed)**
- [ ] Theory: Unit of Work pattern — *Cosmic Python (free online) Ch.6*
- [ ] Mini Exercise: UoW demo: 2 repos, 1 commit boundary
- [ ] Project: `UnitOfWork` class wrapping SQLAlchemy session
- [ ] DSA: Count Good Nodes in Binary Tree
- [ ] SQL: Swap Salary

**D58 (Thu)**
- [ ] Theory: Repository pattern formalized — *Cosmic Python Ch.2*
- [ ] Mini Exercise: —
- [ ] Project: `StockLevelRepository`, `WarehouseRepository` conforming to Phase 1's `Repository[T]` protocol
- [ ] DSA: Validate Binary Search Tree
- [ ] SQL: WareFlow: stock_movements reason breakdown

**D59 (Fri)**
- [ ] Theory: Domain services vs application services — *DDD Distilled Ch.6*
- [ ] Mini Exercise: —
- [ ] Project: `receive_stock` and `dispatch_transfer` domain services using UoW
- [ ] DSA: Kth Smallest Element in a BST
- [ ] SQL: Tree Node

**D60 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo UoW demo from memory
- [ ] Project: Re-read context boundary doc, check for leaks
- [ ] DSA: Review: redo Thursday's problem from memory — Validate Binary Search Tree
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — WareFlow: products in one warehouse but not another

### Week 11 — RabbitMQ, Fulfillment Context

**D61 (Mon)**
- [ ] Theory: RabbitMQ concepts: exchange, queue, binding — *RabbitMQ tutorial 1-3*
- [ ] Mini Exercise: Standalone producer/consumer script
- [ ] Project: Add `rabbitmq` to Docker Compose
- [ ] DSA: Construct Binary Tree from Preorder and Inorder Traversal
- [ ] SQL: WareFlow: reservations pending longer than 1 hour

**D62 (Tue)**
- [ ] Theory: Publishing domain events after commit
- [ ] Mini Exercise: —
- [ ] Project: `event_bus.py`: publish `StockDispatched`/`StockReceived` after UoW commit
- [ ] DSA: Binary Tree Maximum Path Sum
- [ ] SQL: WareFlow: products most frequently reserved

**D63 (Wed)**
- [ ] Theory: Consumer idempotency, ack/nack — *RabbitMQ tutorial 4-5*
- [ ] Mini Exercise: Duplicate-message idempotency demo
- [ ] Project: Fulfillment consumer for `StockDispatched` → creates `Reservation`
- [ ] DSA: Serialize and Deserialize Binary Tree
- [ ] SQL: Human Traffic of Stadium

**D64 (Thu)**
- [ ] Theory: Dead-letter queues — *RabbitMQ tutorial 6 (DLQ)*
- [ ] Mini Exercise: —
- [ ] Project: Configure DLQ, force a bad message, inspect it manually
- [ ] DSA: Implement Trie (Prefix Tree)
- [ ] SQL: WareFlow: transfers stuck 'dispatched' over 24h

**D65 (Fri)**
- [ ] Theory: Transfer receipt endpoint
- [ ] Mini Exercise: —
- [ ] Project: `POST /transfers/{id}/receive` — confirms receipt, publishes `StockReceived`
- [ ] DSA: Design Add and Search Words Data Structure
- [ ] SQL: Friend Requests I: Overall Acceptance Rate

**D66 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo idempotency demo from memory
- [ ] Project: Trace one event end-to-end by hand, write it in `docs/notes.md`
- [ ] DSA: Review: redo Thursday's problem from memory — Implement Trie (Prefix Tree)
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — WareFlow: products most frequently reserved

### Week 12 — Postgres Deep Dive — Isolation, MVCC, Deadlocks, Partitioning

**D67 (Mon)**
- [ ] Theory: MVCC mechanics — *Postgres docs Ch.13 §3*
- [ ] Mini Exercise: Two-transaction MVCC demo (concurrent reads never block)
- [ ] Project: Reservation creation with row-level locking
- [ ] DSA: Kth Largest Element in a Stream
- [ ] SQL: WareFlow: EXPLAIN ANALYZE reservation query before/after row-lock index

**D68 (Tue)**
- [ ] Theory: Isolation levels: read committed, repeatable read, serializable — *Postgres docs Ch.13 §2*
- [ ] Mini Exercise: Reproduce a non-repeatable read, then prevent it
- [ ] Project: Choose and document isolation level for reservations
- [ ] DSA: Last Stone Weight
- [ ] SQL: WareFlow: stock_movements query on new monthly partition vs old

**D69 (Wed)**
- [ ] Theory: Deadlocks in practice — *Postgres docs Ch.13 §3.4*
- [ ] Mini Exercise: Reproduce a deadlock with opposing lock order across 2 warehouses
- [ ] Project: Fix lock ordering in transfer dispatch logic
- [ ] DSA: K Closest Points to Origin
- [ ] SQL: Department Top Three Salaries

**D70 (Thu)**
- [ ] Theory: Table partitioning — *Postgres docs Ch.5 §11*
- [ ] Mini Exercise: —
- [ ] Project: Partition `stock_movements` by month
- [ ] DSA: Kth Largest Element in an Array
- [ ] SQL: WareFlow: a query that would deadlock under bad lock ordering

**D71 (Fri)**
- [ ] Theory: Query plan reading under partitioning
- [ ] Mini Exercise: —
- [ ] Project: `EXPLAIN ANALYZE` before/after partitioning, record in `docs/partitioning-notes.md`
- [ ] DSA: Task Scheduler
- [ ] SQL: Nth Highest Salary

**D72 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo deadlock reproduction from memory
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Kth Largest Element in an Array
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — WareFlow: stock_movements query on new monthly partition vs old

### Week 13 — Kafka Intro, Outbox Gap, Phase Wrap

**D73 (Mon)**
- [ ] Theory: Kafka concepts: topics, partitions, consumer groups — *Confluent Kafka intro*
- [ ] Mini Exercise: Single-topic produce/consume mini project
- [ ] Project: —
- [ ] DSA: Subsets
- [ ] SQL: WareFlow: warehouse stock report

**D74 (Tue)**
- [ ] Theory: Kafka vs RabbitMQ tradeoffs
- [ ] Mini Exercise: —
- [ ] Project: Write `docs/rabbitmq-vs-kafka.md` decision record for WareFlow
- [ ] DSA: Combination Sum
- [ ] SQL: Actors and Directors Who Cooperated At Least Three Times

**D75 (Wed)**
- [ ] Theory: The commit-then-publish gap
- [ ] Mini Exercise: —
- [ ] Project: Deliberately break the "DB commit succeeds, publish fails" case, observe the bug
- [ ] DSA: Permutations
- [ ] SQL: WareFlow: paginated GET /warehouses/{id}/stock query

**D76 (Thu)**
- [ ] Theory: Stock-by-warehouse reporting endpoint
- [ ] Mini Exercise: —
- [ ] Project: `GET /warehouses/{id}/stock` with pagination
- [ ] DSA: Subsets II
- [ ] SQL: Product Sales Analysis I

**D77 (Fri)**
- [ ] Theory: CI update, full pipeline
- [ ] Mini Exercise: —
- [ ] Project: CI with Postgres+Redis+RabbitMQ service containers, all green
- [ ] DSA: Word Search
- [ ] SQL: WareFlow: recursive CTE over one product's transfer history

**D78 (Sat)**
- [ ] Theory: **Phase 3 wrap review**
- [ ] Mini Exercise: Redo Kafka mini exercise from memory
- [ ] Project: `docs/postmortem-phase3.md`, tag `v0.3-phase3`
- [ ] DSA: Review: redo Thursday's problem from memory — Subsets II
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Actors and Directors Who Cooperated At Least Three Times

---

## Phase 4 — Microservices & Infrastructure (Weeks 14-18)

### Week 14 — Service Split, Nginx, CarePoint Scaffold

**D79 (Mon)**
- [ ] Theory: Reverse proxy fundamentals — *Nginx reverse proxy guide*
- [ ] Mini Exercise: Hand-written `nginx.conf` for 2 dummy services
- [ ] Project: New repo `carepoint/`, `auth-service` scaffold (FastAPI, reused JWT logic from Phase 1)
- [ ] DSA: Number of Islands
- [ ] SQL: CarePoint: doctors with overlapping appointments

**D80 (Tue)**
- [ ] Theory: Service-to-service trust (shared secret/public key JWT validation)
- [ ] Mini Exercise: —
- [ ] Project: `clinic-service` scaffold (Django/DRF), JWT validation middleware
- [ ] DSA: Max Area of Island
- [ ] SQL: Patients With a Condition

**D81 (Wed)**
- [ ] Theory: `EXCLUDE` constraints in Postgres — *Postgres docs `btree_gist`*
- [ ] Mini Exercise: —
- [ ] Project: `Appointment` model with `EXCLUDE` constraint on overlapping slots
- [ ] DSA: Clone Graph
- [ ] SQL: CarePoint: appointment count per doctor per day

**D82 (Thu)**
- [ ] Theory: Concurrent booking race
- [ ] Mini Exercise: —
- [ ] Project: `POST /appointments` endpoint, deliberately fire 2 concurrent identical bookings
- [ ] DSA: Islands and Treasure (Walls and Gates)
- [ ] SQL: CarePoint: patients with no documents on file

**D83 (Fri)**
- [ ] Theory: Wiring Nginx as the single entrypoint
- [ ] Mini Exercise: —
- [ ] Project: `nginx.conf` routing `/auth/*` → auth-service, rest → clinic-service, added to Compose
- [ ] DSA: Rotting Oranges
- [ ] SQL: The Most Recent Orders for Each Product

**D84 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo nginx.conf from memory
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Islands and Treasure (Walls and Gates)
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Patients With a Condition

### Week 15 — Patient Records, Presigned Uploads, Reminders

**D85 (Mon)**
- [ ] Theory: Object storage basics, MinIO local setup — *MinIO docs*
- [ ] Mini Exercise: —
- [ ] Project: Add `minio` to Compose
- [ ] DSA: Pacific Atlantic Water Flow
- [ ] SQL: CarePoint: appointments in next 24h needing a reminder

**D86 (Tue)**
- [ ] Theory: Presigned URLs — *S3 presigned URL docs*
- [ ] Mini Exercise: Presigned upload/download demo
- [ ] Project: `POST /documents/presigned-upload` endpoint
- [ ] DSA: Surrounded Regions
- [ ] SQL: CarePoint: doctors with the most documents on their patients

**D87 (Wed)**
- [ ] Theory: Mini API Gateway concept
- [ ] Mini Exercise: Mini FastAPI gateway routing to 2 backend URLs
- [ ] Project: `GET /documents/{id}/presigned-download`
- [ ] DSA: Course Schedule
- [ ] SQL: Reformat Department Table

**D88 (Thu)**
- [ ] Theory: Redis cache on doctor schedules
- [ ] Mini Exercise: —
- [ ] Project: Cache `GET /appointments?doctor_id=&date=`, invalidate on booking/cancel
- [ ] DSA: Course Schedule II
- [ ] SQL: CarePoint: EXPLAIN ANALYZE the doctor-schedule query

**D89 (Fri)**
- [ ] Theory: Appointment reminder job
- [ ] Mini Exercise: —
- [ ] Project: Celery Beat: 24h-before reminder task
- [ ] DSA: Redundant Connection
- [ ] SQL: Queries Quality and Percentage

**D90 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo presigned URL demo from memory
- [ ] Project: Tag `v0.1-carepoint`
- [ ] DSA: Review: redo Thursday's problem from memory — Course Schedule II
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — CarePoint: doctors with the most documents on their patients

### Week 16 — LedgerBase Scaffold, Money-as-Cents, Double-Entry

**D91 (Mon)**
- [ ] Theory: Double-entry bookkeeping fundamentals — *(any intro accounting primer)*
- [ ] Mini Exercise: —
- [ ] Project: New repo `ledgerbase/`, `Account`, `JournalEntry`, `JournalLine` models — **float version, on purpose**
- [ ] DSA: Number of Connected Components in an Undirected Graph
- [ ] SQL: LedgerBase: verify every journal_entry balances

**D92 (Tue)**
- [ ] Theory: Why floats break money math
- [ ] Mini Exercise: —
- [ ] Project: Fix: convert all money fields to integer cents
- [ ] DSA: Graph Valid Tree
- [ ] SQL: LedgerBase: account balance = debits minus credits

**D93 (Wed)**
- [ ] Theory: Enforcing balance: app + DB layer — *Postgres `CHECK` constraint docs*
- [ ] Mini Exercise: —
- [ ] Project: `CHECK` constraint on `journal_lines`, app-level balance validation in service
- [ ] DSA: Word Ladder
- [ ] SQL: Rising Temperature — window function version

**D94 (Thu)**
- [ ] Theory: Invoicing domain
- [ ] Mini Exercise: —
- [ ] Project: `Invoice`, `Payment` models, `invoicing-service` calling `ledger-service` internally
- [ ] DSA: Reconstruct Itinerary
- [ ] SQL: LedgerBase: unbalanced entries that slipped through

**D95 (Fri)**
- [ ] Theory: Trial balance report
- [ ] Mini Exercise: —
- [ ] Project: `GET /reports/trial-balance`
- [ ] DSA: Min Cost to Connect All Points
- [ ] SQL: Movie Rating

**D96 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the float-bug repro from memory, explain the fix
- [ ] Project: Add `ledgerbase` to Nginx routing
- [ ] DSA: Review: redo Thursday's problem from memory — Reconstruct Itinerary
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — LedgerBase: account balance = debits minus credits

### Week 17 — Full CI/CD, Zero-Downtime Deploy

**D97 (Mon)**
- [ ] Theory: GitHub Actions: build + push to GHCR — *GitHub Actions Docker docs*
- [ ] Mini Exercise: —
- [ ] Project: CI builds and pushes images for all 4 services
- [ ] DSA: Network Delay Time
- [ ] SQL: LedgerBase: overdue unpaid invoices

**D98 (Tue)**
- [ ] Theory: SSH deploy step, secrets management — *GitHub Actions secrets docs*
- [ ] Mini Exercise: —
- [ ] Project: Deploy step: SSH to VPS, pull new images
- [ ] DSA: Swim in Rising Water
- [ ] SQL: LedgerBase: monthly revenue trend from paid invoices

**D99 (Wed)**
- [ ] Theory: Zero-downtime rollover mechanics
- [ ] Mini Exercise: Zero-downtime deploy script (health-gated swap)
- [ ] Project: Apply the script: bring up new container, health-check gate, swap Nginx upstream, stop old
- [ ] DSA: Climbing Stairs
- [ ] SQL: Replace Employee ID With The Unique Identifier

**D100 (Thu)**
- [ ] Theory: Rollback path
- [ ] Mini Exercise: —
- [ ] Project: Deliberately break new version's health check, confirm deploy aborts and old version stays live
- [ ] DSA: Min Cost Climbing Stairs
- [ ] SQL: LedgerBase: trial balance report

**D101 (Fri)**
- [ ] Theory: Full pipeline hardening
- [ ] Mini Exercise: —
- [ ] Project: End-to-end: push to `main` → build → push → deploy, verified live
- [ ] DSA: House Robber
- [ ] SQL: Top Travellers

**D102 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo zero-downtime script from memory, explain every step
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Min Cost Climbing Stairs
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — LedgerBase: monthly revenue trend from paid invoices

### Week 18 — Monitoring Stack, Phase Wrap

**D103 (Mon)**
- [ ] Theory: Prometheus: scraping, metrics types — *Prometheus "Getting Started"*
- [ ] Mini Exercise: Custom health-check aggregator (DB+Redis+RabbitMQ in one `/health`)
- [ ] Project: Add `/metrics` endpoint to all 4 services, Prometheus scrape config
- [ ] DSA: House Robber II
- [ ] SQL: LedgerBase: accounts with no activity this month

**D104 (Tue)**
- [ ] Theory: Grafana dashboards — *Grafana "Getting Started"*
- [ ] Mini Exercise: —
- [ ] Project: Build a latency + queue-depth dashboard
- [ ] DSA: Longest Palindromic Substring
- [ ] SQL: LedgerBase: largest single journal entry this quarter

**D105 (Wed)**
- [ ] Theory: Sentry integration — *Sentry Python SDK docs*
- [ ] Mini Exercise: —
- [ ] Project: Wire Sentry into all 4 services
- [ ] DSA: Palindromic Substrings
- [ ] SQL: Sales Analysis I

**D106 (Thu)**
- [ ] Theory: Finding a bug via Sentry, not code-reading
- [ ] Mini Exercise: —
- [ ] Project: Inject an unbalanced-entry bug past app validation (bypass service layer directly), find it via Sentry alert first
- [ ] DSA: Decode Ways
- [ ] SQL: LedgerBase: underpaid invoices

**D107 (Fri)**
- [ ] Theory: Phase wrap: docs, CI final check
- [ ] Mini Exercise: —
- [ ] Project: `docs/postmortem-phase4.md`, full CI green across everything
- [ ] DSA: Coin Change
- [ ] SQL: Sales Analysis III

**D108 (Sat)**
- [ ] Theory: **Phase 4 wrap review**
- [ ] Mini Exercise: Explain your full deploy pipeline out loud, start to finish
- [ ] Project: Tag `v0.4-phase4`
- [ ] DSA: Review: redo Thursday's problem from memory — Decode Ways
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — LedgerBase: largest single journal entry this quarter

---

## Phase 5 — Scaling & Advanced Architecture (Weeks 19-22)

### Week 19 — Outbox Pattern, FleetTrack Scaffold

**D109 (Mon)**
- [ ] Theory: Outbox pattern theory — *Fowler/microservices.io outbox article*
- [ ] Mini Exercise: Standalone outbox demo (insert + relay script)
- [ ] Project: New repo `fleettrack/`, `Delivery`, `DeliveryEvent`, `outbox` models
- [ ] DSA: Maximum Product Subarray
- [ ] SQL: FleetTrack: unsent outbox rows older than 5 minutes

**D110 (Tue)**
- [ ] Theory: Transactional outbox insert
- [ ] Mini Exercise: —
- [ ] Project: Status-update service: state change + outbox row, one transaction
- [ ] DSA: Word Break
- [ ] SQL: Rising Temperature — self-join with LAG variant

**D111 (Wed)**
- [ ] Theory: Relay process design
- [ ] Mini Exercise: —
- [ ] Project: Outbox relay worker (poll, publish, mark sent)
- [ ] DSA: Longest Increasing Subsequence
- [ ] SQL: FleetTrack: delivery stuck longest in one status

**D112 (Thu)**
- [ ] Theory: Fault injection on the relay
- [ ] Mini Exercise: —
- [ ] Project: Kill RabbitMQ mid-relay, confirm no event lost, retried next poll
- [ ] DSA: Partition Equal Subset Sum
- [ ] SQL: FleetTrack: avg time between status transitions

**D113 (Fri)**
- [ ] Theory: Outbox lag metric
- [ ] Mini Exercise: —
- [ ] Project: Add outbox-lag metric to Prometheus/Grafana (from Phase 4 stack)
- [ ] DSA: Insert Interval
- [ ] SQL: The Most Frequently Ordered Products for Each Customer

**D114 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo outbox demo from memory
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Partition Equal Subset Sum
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Rising Temperature — self-join with LAG variant

### Week 20 — CQRS Read Model, Saga

**D115 (Mon)**
- [ ] Theory: CQRS theory — *Fowler CQRS article*
- [ ] Mini Exercise: Mini CQRS projector (rebuild view from event log)
- [ ] Project: `delivery_view` read model table
- [ ] DSA: Merge Intervals
- [ ] SQL: FleetTrack: rebuild delivery_view from delivery_events by hand

**D116 (Tue)**
- [ ] Theory: Projector consuming outbox-relayed events
- [ ] Mini Exercise: —
- [ ] Project: Consumer that updates `delivery_view` on each event
- [ ] DSA: Non-overlapping Intervals
- [ ] SQL: Article Views I

**D117 (Wed)**
- [ ] Theory: Dispatcher dashboard endpoint
- [ ] Mini Exercise: —
- [ ] Project: `GET /dispatch/dashboard` reading only from `delivery_view`
- [ ] DSA: Meeting Rooms
- [ ] SQL: FleetTrack: drivers with the most cancelled deliveries

**D118 (Thu)**
- [ ] Theory: Saga theory: choreography vs orchestration — *Newman Ch.5 saga section*
- [ ] Mini Exercise: —
- [ ] Project: Design the cancellation saga on paper first (`docs/cancellation-saga.md`)
- [ ] DSA: Meeting Rooms II
- [ ] SQL: Article Views II

**D119 (Fri)**
- [ ] Theory: Implementing the choreographed saga
- [ ] Mini Exercise: —
- [ ] Project: 3-step cancellation saga: reverse assignment → notify → credit fee
- [ ] DSA: Maximum Subarray
- [ ] SQL: FleetTrack: dispatcher dashboard — join vs read-model

**D120 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo CQRS projector from memory
- [ ] Project: Tag `v0.1-fleettrack`
- [ ] DSA: Review: redo Thursday's problem from memory — Meeting Rooms II
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Article Views I

### Week 21 — DocuVault Scaffold, Elasticsearch

**D121 (Mon)**
- [ ] Theory: Inverted index concept — *ES "Getting Started"*
- [ ] Mini Exercise: Index 1000 fake docs, run basic queries
- [ ] Project: New repo `docuvault/`, `Document`/`DocumentVersion` models
- [ ] DSA: Jump Game
- [ ] SQL: DocuVault: documents with the most versions

**D122 (Tue)**
- [ ] Theory: Analyzers, fuzziness, boosting — *ES docs analyzers*
- [ ] Mini Exercise: Tune analyzer on the mini exercise corpus
- [ ] Project: `POST /documents` + MinIO upload (reusing Phase 4 presigned pattern)
- [ ] DSA: Jump Game II
- [ ] SQL: Fix Names in a Table

**D123 (Wed)**
- [ ] Theory: Keeping a derived index in sync
- [ ] Mini Exercise: —
- [ ] Project: Outbox-relay-style consumer indexing new/updated docs into ES
- [ ] DSA: Gas Station
- [ ] SQL: DocuVault: documents tagged with more than 3 tags

**D124 (Thu)**
- [ ] Theory: Search query design
- [ ] Mini Exercise: —
- [ ] Project: `GET /documents/search?q=&tags=`
- [ ] DSA: Hand of Straights
- [ ] SQL: DocuVault: latest version per document

**D125 (Fri)**
- [ ] Theory: Reindex-from-source recovery
- [ ] Mini Exercise: —
- [ ] Project: `POST /documents/reindex` — rebuilds ES fully from Postgres
- [ ] DSA: Unique Paths
- [ ] SQL: Recyclable and Low Fat Products

**D126 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo indexing mini exercise from memory
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Hand of Straights
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Fix Names in a Table

### Week 22 — Kubernetes Fundamentals, Replication, Phase Wrap

**D127 (Mon)**
- [ ] Theory: Pods, Deployments, Services — *K8s "Learn Kubernetes Basics" pt.1-2*
- [ ] Mini Exercise: Mini load balancer (round-robin, 2 processes)
- [ ] Project: `kind` cluster running locally, write Deployment+Service YAML for one DocuVault service
- [ ] DSA: Longest Common Subsequence
- [ ] SQL: DocuVault: documents never tagged

**D128 (Tue)**
- [ ] Theory: ConfigMaps, Secrets — *K8s docs pt.3*
- [ ] Mini Exercise: —
- [ ] Project: Externalize config/secrets from that service into ConfigMap/Secret
- [ ] DSA: Best Time to Buy and Sell Stock with Cooldown
- [ ] SQL: Primary Department for Each Employee

**D129 (Wed)**
- [ ] Theory: Scaling replicas, rolling updates — *K8s docs pt.4-5*
- [ ] Mini Exercise: —
- [ ] Project: Scale to 2 replicas, do a rolling update, observe zero dropped requests
- [ ] DSA: Coin Change II
- [ ] SQL: DocuVault: tags frequently used together

**D130 (Thu)**
- [ ] Theory: Postgres replication — *Postgres replication docs*
- [ ] Mini Exercise: Local read-replica setup
- [ ] Project: Route ES-sync consumer's reads to replica
- [ ] DSA: Target Sum
- [ ] SQL: DocuVault: EXPLAIN ANALYZE a metadata query on replica vs primary

**D131 (Fri)**
- [ ] Theory: Sharding (conceptual)
- [ ] Mini Exercise: —
- [ ] Project: `docs/sharding-decision-record.md` — what key, why, when it'd be justified
- [ ] DSA: Interleaving String
- [ ] SQL: Calculate Special Bonus

**D132 (Sat)**
- [ ] Theory: **Phase 5 wrap review**
- [ ] Mini Exercise: Explain the outbox → CQRS → saga chain end-to-end, out loud
- [ ] Project: `docs/postmortem-phase5.md`, tag `v0.5-phase5`
- [ ] DSA: Review: redo Thursday's problem from memory — Target Sum
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Primary Department for Each Employee

---

## Phase 6 — Senior-Track Capstone (Weeks 23-26)

### Week 23 — PayFlow — Idempotency, Webhooks

**D133 (Mon)**
- [ ] Theory: Idempotency key mechanics — *Stripe idempotency docs*
- [ ] Mini Exercise: Standalone idempotency-key demo
- [ ] Project: New repo `payflow/`, `PaymentIntent` model + idempotency table
- [ ] DSA: Longest Increasing Path in a Matrix
- [ ] SQL: PayFlow: duplicate idempotency keys with different request hashes

**D134 (Tue)**
- [ ] Theory: Request hashing alongside the key
- [ ] Mini Exercise: —
- [ ] Project: `POST /payments` idempotency middleware/service
- [ ] DSA: Distinct Subsequences
- [ ] SQL: Duplicate Emails revisited

**D135 (Wed)**
- [ ] Theory: Race-testing idempotency
- [ ] Mini Exercise: —
- [ ] Project: Fire the same request twice concurrently, assert single charge
- [ ] DSA: Edit Distance
- [ ] SQL: PayFlow: webhook_events received more than once per provider_event_id

**D136 (Thu)**
- [ ] Theory: HMAC webhook signature verification
- [ ] Mini Exercise: Standalone HMAC verify demo
- [ ] Project: Mock provider webhook endpoint + signature verification
- [ ] DSA: Single Number
- [ ] SQL: PayFlow: payment_intents stuck 'pending' longer than 10 minutes

**D137 (Fri)**
- [ ] Theory: Webhook idempotency (provider event ID)
- [ ] Mini Exercise: —
- [ ] Project: Webhook processing idempotent on `provider_event_id`, reconciles ledger via `ledger-service`
- [ ] DSA: Number of 1 Bits
- [ ] SQL: Employees Whose Manager Left the Company

**D138 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo idempotency demo from memory
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Single Number
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Duplicate Emails revisited

### Week 24 — Security Hardening, Load Testing

**D139 (Mon)**
- [ ] Theory: OWASP Top 10 relevant to your stack — *OWASP Top 10*
- [ ] Mini Exercise: —
- [ ] Project: Refunds endpoint + API-key auth for server-to-server callers
- [ ] DSA: Counting Bits
- [ ] SQL: PayFlow: refunds exceeding their original payment amount

**D140 (Tue)**
- [ ] Theory: Secrets management patterns
- [ ] Mini Exercise: —
- [ ] Project: Move webhook secret + API keys out of `.env` into a secrets-manager pattern
- [ ] DSA: Reverse Bits
- [ ] SQL: PayFlow: same-day vs delayed refunds

**D141 (Wed)**
- [ ] Theory: Audit logging
- [ ] Mini Exercise: —
- [ ] Project: Append-only audit log for payment/refund state changes
- [ ] DSA: Missing Number
- [ ] SQL: PayFlow: EXPLAIN ANALYZE the idempotency-key lookup under load

**D142 (Thu)**
- [ ] Theory: Threat modeling
- [ ] Mini Exercise: —
- [ ] Project: Write `docs/threat-model.md` (secret leak, key guessing, replay-after-expiry)
- [ ] DSA: Rotate Image
- [ ] SQL: PayFlow: audit log for one payment_intent, ordered chronologically

**D143 (Fri)**
- [ ] Theory: `locust` load testing — *locust docs*
- [ ] Mini Exercise: Toy-endpoint locust scenario
- [ ] Project: Realistic-concurrency PayFlow load test, find + fix the bottleneck
- [ ] DSA: Spiral Matrix
- [ ] SQL: Find Followers Count

**D144 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo HMAC verify demo from memory
- [ ] Project: Tag `v0.1-payflow`
- [ ] DSA: Review: redo Thursday's problem from memory — Rotate Image
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — PayFlow: same-day vs delayed refunds

### Week 25 — AtlasMarket Architecture + Integration Sprint (part 1)

**D145 (Mon)**
- [ ] Theory: Integration planning — what to reuse vs rebuild
- [ ] Mini Exercise: —
- [ ] Project: New repo `atlasmarket/`, `docs/architecture.md` mapping each service to its origin project
- [ ] DSA: Set Matrix Zeroes
- [ ] SQL: AtlasMarket: revenue per vendor this month

**D146 (Tue)**
- [ ] Theory: Vendor-scoping the catalog
- [ ] Mini Exercise: —
- [ ] Project: Adapt StockPilot's product model: add `vendor_id`, vendor onboarding endpoint
- [ ] DSA: Happy Number
- [ ] SQL: Product Sales Analysis III

**D147 (Wed)**
- [ ] Theory: Vendor-scoped search
- [ ] Mini Exercise: —
- [ ] Project: Adapt DocuVault's ES sync pattern to index vendor-scoped products
- [ ] DSA: Plus One
- [ ] SQL: AtlasMarket: vendors with no products listed

**D148 (Thu)**
- [ ] Theory: React/TS fundamentals, Vite setup — *react.dev "Describing the UI"*
- [ ] Mini Exercise: —
- [ ] Project: `storefront/` scaffold (Vite + React + TS), product list page with TanStack Query
- [ ] DSA: Pow(x, n)
- [ ] SQL: AtlasMarket: top 5 vendors by order count

**D149 (Fri)**
- [ ] Theory: TanStack Query caching — *TanStack Query "Quick Start"*
- [ ] Mini Exercise: Mini product list against a dummy API
- [ ] Project: Cart state (local component state) + cart UI
- [ ] DSA: Merge Sorted Array
- [ ] SQL: The Most Recent Three Orders

**D150 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Explain TanStack Query cache vs your Redis cache-aside pattern, out loud
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Pow(x, n)
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Product Sales Analysis III

### Week 26 — AtlasMarket Integration Sprint (part 2), Mock Interviews, Program Wrap

**D151 (Mon)**
- [ ] Theory: Multi-vendor checkout design
- [ ] Mini Exercise: —
- [ ] Project: Checkout: cart → split into `order_vendor_groups` → PayFlow idempotent payment → per-vendor ledger entries
- [ ] DSA: Design Twitter
- [ ] SQL: AtlasMarket: orders split across 2+ vendors

**D152 (Tue)**
- [ ] Theory: Per-vendor fulfillment status
- [ ] Mini Exercise: —
- [ ] Project: Adapt WareFlow's status concepts to `order_vendor_groups`
- [ ] DSA: LFU Cache
- [ ] SQL: AtlasMarket: per-vendor payout reconciliation

**D153 (Wed)**
- [ ] Theory: Checkout UI, end-to-end wiring
- [ ] Mini Exercise: —
- [ ] Project: Storefront checkout form wired to the real API
- [ ] DSA: Word Search II
- [ ] SQL: Capstone review: rewrite Week 12's partition-aware query from memory

**D154 (Thu)**
- [ ] Theory: Mock system design interview #1 — *System Design Interview (Xu), relevant chapter*
- [ ] Mini Exercise: —
- [ ] Project: Design multi-vendor checkout from scratch on a whiteboard (no code), then compare to what you built
- [ ] DSA: Merge k Sorted Lists
- [ ] SQL: Capstone review: rewrite Week 6's window-function ranking query from memory

**D155 (Fri)**
- [ ] Theory: Mock system design interview #2 + #3
- [ ] Mini Exercise: —
- [ ] Project: Design payment idempotency + product search from scratch, unprompted
- [ ] DSA: Alien Dictionary
- [ ] SQL: Capstone: the one query you'd hand an interviewer

**D156 (Sat)**
- [ ] Theory: **Program wrap**
- [ ] Mini Exercise: —
- [ ] Project: `docs/atlasmarket-roadmap-post-bootcamp.md` (deferred features), `docs/postmortem-phase6.md`, full 6-month retrospective across all 10 projects, tag `v1.0-bootcamp-complete`
- [ ] DSA: Review: redo Thursday's problem from memory — Merge k Sorted Lists
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — AtlasMarket: per-vendor payout reconciliation

---

