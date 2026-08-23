# Roadmap Progress Tracker

Check off each item as you finish it. **366 days total across 61 weeks / 11 phases** (~14-15 months), split into two tracks:

- **Phases 1-6 (Weeks 1-30, D1-D180) — Python Backend Bootcamp.** Every day has 5 independent checkboxes — Theory, Mini Exercise, Project, DSA, SQL — except Weeks 23-24 (Phase 5, Raft implementation) and Weeks 29-30 (Phase 6, system-design real builds), which deliberately drop the DSA/SQL grind since the day's own algorithmic/systems work already carries that load. Systems-mastery/interview-readiness depth (resilience patterns, consistent hashing, consensus, gRPC, real cloud deployment, SLOs/on-call/DR, compliance scoping, a system-design bank, a behavioral bank) is woven into Phases 4-6 rather than a separate phase — see each phase file's Learning Goals.
- **Phases 7-11 (Weeks 31-61, D181-D366) — AI/ML/Data Zoomcamp Track** (LLM Zoomcamp → AI Dev Tools Zoomcamp → ML Zoomcamp → MLOps Zoomcamp → Data Engineering Zoomcamp). DSA/SQL grind is deliberately dropped here (already covered in Phases 1-6) — every day has 3 independent checkboxes: Theory, Mini Exercise, Project. Phase 9 opens with a dedicated Week 42 on ML math foundations.

Order rationale for the Zoomcamp track: LLM Zoomcamp comes first because it's the most directly transferable skill for a backend engineer (you're wrapping API calls into services, not training models) — a low-friction on-ramp right after 6 months of backend work. AI Dev Tools follows immediately since it builds on LLM's agent/tool-calling fundamentals. Then ML Zoomcamp shifts into more theory/math-heavy classical ML, with MLOps following directly since it's literally productionizing the models just built. Data Engineering closes the program as a capstone unifying data from every system built across the year.

> **Generated file — do not hand-edit.** This is derived from the daily-plan
> tables in `phase-1-foundations.md` … `phase-11-data-engineering-zoomcamp.md`
> by `scripts/gen_progress.py`. To change a day's content, edit the phase
> file and rerun the generator. Checkbox state (`[ ]`/`[x]`) is preserved
> across runs.

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
- [ ] DSA: Warm-up: implement a hash table from scratch; Two Sum
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
- [ ] Theory: Pytest architecture: fixtures, factories, mocking philosophy; property-based testing with Hypothesis — testing invariants instead of hand-picked examples — *pytest docs on fixtures + Hypothesis "Quick start guide"*
- [ ] Mini Exercise: Convert 3 hand-written test setups to `factory_boy` factories; write one Hypothesis test for `apply_discount(price, pct)` asserting the invariant `0 <= result <= price` across generated inputs
- [ ] Project: Add `factories.py`, replace manual test data across suite; add `hypothesis` to dev deps, one property-based test on a pure pricing/stock-math function
- [ ] DSA: Warm-up: implement a stack from scratch; Valid Parentheses
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
- [ ] DSA: Warm-up: implement a singly linked list from scratch; Reverse Linked List
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
- [ ] DSA: Warm-up: implement a queue from scratch; Binary Tree Level Order Traversal
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
- [ ] Theory: Consumer idempotency, ack/nack; consumer-driven contract testing — why a schema change on the publisher side shouldn't silently break the consumer — *RabbitMQ tutorial 4-5 + Pact docs "Message Pact"*
- [ ] Mini Exercise: Duplicate-message idempotency demo
- [ ] Project: Fulfillment consumer for `StockDispatched` → creates `Reservation`; Pact message-contract test pinning the `StockDispatched` payload shape between the WareFlow publisher and the fulfillment consumer
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
- [ ] Theory: **Review**; networking primer — TCP vs UDP, HTTP/1.1 vs HTTP/2, the TLS handshake, DNS resolution (what Nginx is actually terminating/proxying) — **High Performance Browser Networking* (free online) Ch.2 + TLS chapter*
- [ ] Mini Exercise: Redo nginx.conf from memory; capture a real TLS handshake with `openssl s_client` against a local HTTPS endpoint
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
- [ ] Theory: Redis cache on doctor schedules; frontend intro — React + TypeScript + Vite + TanStack Query scaffold, first real UI of the year — *React docs "Quick Start" + TanStack Query "Quick Start"*
- [ ] Mini Exercise: —
- [ ] Project: Cache `GET /appointments?doctor_id=&date=`, invalidate on booking/cancel; new `carepoint-web/` (Vite + React + TS), one page: doctor's daily schedule fetched via TanStack Query against the endpoint just cached
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
- [ ] Theory: Invoicing domain; resilient service-to-service calls — retry with exponential backoff+jitter, a hand-rolled circuit breaker (closed/open/half-open) — **Release It!* (Nygard) stability patterns chapter*
- [ ] Mini Exercise: Toy flaky endpoint (fails 50% of the time), wrap it in retry+circuit-breaker, force it to trip and recover
- [ ] Project: `Invoice`, `Payment` models, `invoicing-service` calling `ledger-service` internally, wrapped in retry-with-backoff + a circuit breaker (this is the system's first real synchronous cross-service call, so it's also the first to get resilience)
- [ ] DSA: Reconstruct Itinerary
- [ ] SQL: LedgerBase: unbalanced entries that slipped through

**D95 (Fri)**
- [ ] Theory: Trial balance report
- [ ] Mini Exercise: —
- [ ] Project: `GET /reports/trial-balance`
- [ ] DSA: Min Cost to Connect All Points
- [ ] SQL: Movie Rating

**D96 (Sat)**
- [ ] Theory: **Review**; fault injection on the resilient invoicing→ledger call
- [ ] Mini Exercise: Redo the float-bug repro from memory, explain the fix
- [ ] Project: Add `ledgerbase` to Nginx routing; kill `ledger-service` mid-call, confirm the circuit trips and `invoicing-service` fails clean (409/503) instead of hanging
- [ ] DSA: Review: redo Thursday's problem from memory — Reconstruct Itinerary
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — LedgerBase: account balance = debits minus credits

### Week 17 — Full CI/CD, Zero-Downtime Deploy

**D97 (Mon)**
- [ ] Theory: GitHub Actions: build + push to GHCR; supply-chain security gates — dependency, secret, and container scanning — *GitHub Actions Docker docs + `pip-audit`/`gitleaks`/Trivy READMEs*
- [ ] Mini Exercise: Run `gitleaks detect` against this repo's own git history, confirm it doesn't false-positive on real config
- [ ] Project: CI builds and pushes images for all 4 services; add `pip-audit` (dependency CVEs), `gitleaks` (committed-secret scan), and Trivy (container image scan) as CI steps that fail the build on high-severity findings
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

## Phase 5 — Scaling & Advanced Architecture (Weeks 19-24)

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
- [ ] Theory: Dispatcher dashboard endpoint; frontend — second React/TS app, this time with polling for near-real-time data (reusing Phase 4's `carepoint-web` setup, not re-deriving it)
- [ ] Mini Exercise: —
- [ ] Project: `GET /dispatch/dashboard` reading only from `delivery_view`; `fleettrack-web/` (Vite + React + TS + TanStack Query), one page: dispatcher table polling the dashboard endpoint every few seconds
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
- [ ] Theory: Search query design; frontend — third React/TS app, this time a controlled search input with debounced queries
- [ ] Mini Exercise: —
- [ ] Project: `GET /documents/search?q=&tags=`; `docuvault-web/` search page: debounced search box + tag filter chips calling the endpoint via TanStack Query
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
- [ ] Theory: ConfigMaps, Secrets; leader election & consensus — Raft explained (leader election, log replication, majority quorum) — *K8s docs pt.3 + etcd docs "Understand failovers"*
- [ ] Mini Exercise: Stand up a 3-node local etcd cluster, watch leader election happen
- [ ] Project: Externalize config/secrets from that service into ConfigMap/Secret; `docs/consensus-notes.md` — Raft in your own words, tied to K8s/RabbitMQ/Kafka
- [ ] DSA: Best Time to Buy and Sell Stock with Cooldown
- [ ] SQL: Primary Department for Each Employee

**D129 (Wed)**
- [ ] Theory: Scaling replicas, rolling updates; GitOps (conceptual) — why `kubectl apply` by hand doesn't scale past one cluster, and how ArgoCD/Flux would reconcile cluster state from this same YAML in git instead — *K8s docs pt.4-5 + ArgoCD docs "Core Concepts" (read-only, not installed)*
- [ ] Mini Exercise: —
- [ ] Project: Scale to 2 replicas, do a rolling update, observe zero dropped requests; commit the Deployment/Service YAML to a `k8s/` directory as if a GitOps controller were about to watch it
- [ ] DSA: Coin Change II
- [ ] SQL: DocuVault: tags frequently used together

**D130 (Thu)**
- [ ] Theory: Postgres replication — *Postgres replication docs*
- [ ] Mini Exercise: Local read-replica setup
- [ ] Project: Route ES-sync consumer's reads to replica
- [ ] DSA: Target Sum
- [ ] SQL: DocuVault: EXPLAIN ANALYZE a metadata query on replica vs primary

**D131 (Fri)**
- [ ] Theory: Sharding (conceptual); consistent hashing — the ring, virtual nodes, redistribution vs naive `hash(key) % N` — **Designing Data-Intensive Applications* (Kleppmann) Ch.6*
- [ ] Mini Exercise: Build a consistent-hashing ring from scratch (virtual nodes included) against a synthetic key set; simulate adding/removing a shard and measure redistribution % vs naive modulo hashing
- [ ] Project: `docs/sharding-decision-record.md` — what key, why, when it'd be justified, backed by the redistribution benchmark
- [ ] DSA: Interleaving String
- [ ] SQL: Calculate Special Bonus

**D132 (Sat)**
- [ ] Theory: **Review**; consensus failover drill — kill Tuesday's etcd leader, watch failover
- [ ] Mini Exercise: Explain the outbox → CQRS → saga chain end-to-end, out loud; kill the etcd leader process, watch failover, record the term/log-index numbers before/after
- [ ] Project: `docs/postmortem-week22.md`
- [ ] DSA: Review: redo Thursday's problem from memory — Target Sum
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Primary Department for Each Employee

### Week 23 — Raft — Leader Election & Log Replication

**D133 (Mon)**
- [ ] Theory: The Raft paper: replicated state machines, why consensus is hard, the shape of the solution — *Ongaro & Ousterhout, "In Search of an Understandable Consensus Algorithm" §1-5*
- [ ] Mini Exercise: Trace the paper's Figure 2 (the state summary) by hand, node by node, for a 3-node example
- [ ] Project: New repo `raft-impl/`, `Node` class with the Follower/Candidate/Leader states and the state transition table

**D134 (Tue)**
- [ ] Theory: Leader election: randomized timeouts, `RequestVote`, term comparison — *Raft paper §5.1-5.2*
- [ ] Mini Exercise: Deliberately use a FIXED (non-random) timeout across all nodes, watch a split-vote loop happen, then randomize and watch it resolve
- [ ] Project: `RequestVote` RPC handler, randomized election timeout, term increment on election start

**D135 (Wed)**
- [ ] Theory: `AppendEntries` as heartbeat; log replication begins — *Raft paper §5.3*
- [ ] Mini Exercise: Wire 3 processes over local HTTP, confirm heartbeats keep a leader stable with no elections firing
- [ ] Project: `AppendEntries` RPC (empty = heartbeat), leader sends periodic heartbeats, followers reset their election timer on receipt

**D136 (Thu)**
- [ ] Theory: Log replication for real: `nextIndex`/`matchIndex`, commit index advancement — *Raft paper §5.3 (cont.)*
- [ ] Mini Exercise: On paper, trace `nextIndex` converging for a follower whose log is 3 entries behind
- [ ] Project: Client-submitted command → leader appends locally → replicates via `AppendEntries` → advances `commitIndex` once a majority acks

**D137 (Fri)**
- [ ] Theory: Log inconsistency repair — *Raft paper §5.3 (log matching property)*
- [ ] Mini Exercise: Manually construct two divergent follower logs, run the repair loop, confirm convergence
- [ ] Project: Handle the follower-rejects-AppendEntries case: leader decrements `nextIndex` and retries until logs match

**D138 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the `nextIndex` convergence trace from memory, explain it out loud
- [ ] Project: Bring up a real 5-node cluster, submit 10 commands from a client script, confirm all 5 nodes converge to the same log

### Week 24 — Raft — Safety Properties Under Fault

**D139 (Mon)**
- [ ] Theory: The five safety properties: Election Safety, Leader Append-Only, Log Matching, Leader Completeness, State Machine Safety — *Raft paper §5.4-5.5*
- [ ] Mini Exercise: For each property, write one concrete scenario where violating it corrupts the system — no abstractions, real node/term/entry numbers
- [ ] Project: `docs/raft-safety-properties.md` — each property in your own words, tied to a specific line of your own implementation that enforces it

**D140 (Tue)**
- [ ] Theory: Network partition simulation
- [ ] Mini Exercise: Build a message-dropping proxy layer: any node pair can be "partitioned" by dropping messages between them on command
- [ ] Project: Partition a 5-node cluster into a 3-node majority and a 2-node minority; observe which side (if either) elects a leader

**D141 (Wed)**
- [ ] Theory: Partition healing, stale leader step-down — *Raft paper §5.1 (term comparison on RPC)*
- [ ] Mini Exercise: Reconnect a partitioned minority node to the majority, watch it discover the higher term and step down/update
- [ ] Project: Handle the healed-partition case: a stale leader (or stale follower with uncommitted entries) reconciles its log against the current leader's

**D142 (Thu)**
- [ ] Theory: Adversarial testing: kill the leader mid-replication, kill a follower mid-repair
- [ ] Mini Exercise: —
- [ ] Project: Build the "torture test": randomly kill/restart nodes and drop messages for an extended run

**D143 (Fri)**
- [ ] Theory: Applying Raft to a real use case — *Revisit `system-design-problems.md` SD14*
- [ ] Mini Exercise: —
- [ ] Project: Wire the Raft cluster as the coordination layer for a toy distributed job scheduler: only the current leader is allowed to dispatch a scheduled job

**D144 (Sat)**
- [ ] Theory: **Phase 5 wrap review**
- [ ] Mini Exercise: Explain all five safety properties out loud, unscripted, each with your own concrete violation scenario
- [ ] Project: `docs/postmortem-phase5.md` (full phase, Weeks 19-24), tag `v0.5-phase5`

---

## Phase 6 — Senior-Track Capstone (Weeks 25-30)

### Week 25 — PayFlow — Idempotency, Webhooks

**D145 (Mon)**
- [ ] Theory: Idempotency key mechanics — *Stripe idempotency docs*
- [ ] Mini Exercise: Standalone idempotency-key demo
- [ ] Project: New repo `payflow/`, `PaymentIntent` model + idempotency table
- [ ] DSA: Longest Increasing Path in a Matrix
- [ ] SQL: PayFlow: duplicate idempotency keys with different request hashes

**D146 (Tue)**
- [ ] Theory: Request hashing alongside the key
- [ ] Mini Exercise: —
- [ ] Project: `POST /payments` idempotency middleware/service
- [ ] DSA: Distinct Subsequences
- [ ] SQL: Duplicate Emails revisited

**D147 (Wed)**
- [ ] Theory: Race-testing idempotency
- [ ] Mini Exercise: —
- [ ] Project: Fire the same request twice concurrently, assert single charge
- [ ] DSA: Edit Distance
- [ ] SQL: PayFlow: webhook_events received more than once per provider_event_id

**D148 (Thu)**
- [ ] Theory: HMAC webhook signature verification
- [ ] Mini Exercise: Standalone HMAC verify demo
- [ ] Project: Mock provider webhook endpoint + signature verification
- [ ] DSA: Single Number
- [ ] SQL: PayFlow: payment_intents stuck 'pending' longer than 10 minutes

**D149 (Fri)**
- [ ] Theory: Webhook idempotency (provider event ID)
- [ ] Mini Exercise: —
- [ ] Project: Webhook processing idempotent on `provider_event_id`, reconciles ledger via `ledger-service`
- [ ] DSA: Number of 1 Bits
- [ ] SQL: Employees Whose Manager Left the Company

**D150 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo idempotency demo from memory
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Single Number
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Duplicate Emails revisited

### Week 26 — Security Hardening, Load Testing

**D151 (Mon)**
- [ ] Theory: OWASP Top 10 relevant to your stack; backup & disaster recovery — LedgerBase has held financial data since Week 16 with no stated backup story — *OWASP Top 10 + Postgres docs "Backup and Restore"*
- [ ] Mini Exercise: `pg_dump`/`pg_restore` round-trip on a throwaway DB
- [ ] Project: Refunds endpoint + API-key auth for server-to-server callers; real `pg_dump` backup of LedgerBase, RPO/RTO written down with reasoning, deliberate corruption in a scratch copy, restore, verify the trial-balance report reconciles identically; `docs/backup-dr-plan.md`
- [ ] DSA: Counting Bits
- [ ] SQL: PayFlow: refunds exceeding their original payment amount

**D152 (Tue)**
- [ ] Theory: Secrets management with a real secrets manager (HashiCorp Vault) — dynamic secrets, leasing/rotation vs a static `.env` file — *Vault docs "Getting Started" + "Secrets Engines"*
- [ ] Mini Exercise: Run Vault in dev mode, write/read one secret via the CLI, then via its HTTP API
- [ ] Project: Add `vault` to Docker Compose; move webhook secret + API keys out of `.env` into Vault's KV engine, app reads them via the API at startup
- [ ] DSA: Reverse Bits
- [ ] SQL: PayFlow: same-day vs delayed refunds

**D153 (Wed)**
- [ ] Theory: Audit logging; cloud IAM & VPC design — least-privilege roles, public/private subnets — *AWS "IAM best practices" + "VPC and subnets" (or GCP equivalents)*
- [ ] Mini Exercise: Sketch the IAM role's exact permission set and the VPC's subnet layout on paper before creating anything
- [ ] Project: Append-only audit log for payment/refund state changes; create the cloud account, the least-privilege IAM role, and a VPC with public/private subnets for AtlasMarket's future deploy
- [ ] DSA: Missing Number
- [ ] SQL: PayFlow: EXPLAIN ANALYZE the idempotency-key lookup under load

**D154 (Thu)**
- [ ] Theory: Threat modeling; compliance scoping — PCI-DSS, HIPAA-adjacent considerations — *PCI DSS Quick Reference Guide + HHS.gov HIPAA Security Rule summary*
- [ ] Mini Exercise: —
- [ ] Project: Write `docs/threat-model.md` (secret leak, key guessing, replay-after-expiry); `docs/pci-scope-note.md` (PayFlow) and `docs/hipaa-considerations-note.md` (CarePoint)
- [ ] DSA: Rotate Image
- [ ] SQL: PayFlow: audit log for one payment_intent, ordered chronologically

**D155 (Fri)**
- [ ] Theory: `locust` load testing; SLOs/SLIs/error budgets, writing an on-call runbook — *locust docs + Google SRE Book Ch.4 (SLOs)*
- [ ] Mini Exercise: Toy-endpoint locust scenario
- [ ] Project: Realistic-concurrency PayFlow load test, find + fix the bottleneck; write the payment-path SLO + error budget derived from the load-test numbers, and the "payment success rate dropped" on-call runbook
- [ ] DSA: Spiral Matrix
- [ ] SQL: Find Followers Count

**D156 (Sat)**
- [ ] Theory: **Review + live incident drill** — *Google SRE Book On-Call/Postmortem chapters*
- [ ] Mini Exercise: Redo HMAC verify demo from memory
- [ ] Project: Run the incident drill: kill `ledger-service`, follow Friday's runbook blind, resolve it, write a blameless postmortem; tag `v0.1-payflow`
- [ ] DSA: Review: redo Thursday's problem from memory — Rotate Image
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — PayFlow: same-day vs delayed refunds

### Week 27 — AtlasMarket Architecture + Integration Sprint (part 1), Storefront

**D157 (Mon)**
- [ ] Theory: Integration planning — what to reuse vs rebuild
- [ ] Mini Exercise: —
- [ ] Project: New repo `atlasmarket/`, `docs/architecture.md` mapping each service to its origin project
- [ ] DSA: Set Matrix Zeroes
- [ ] SQL: AtlasMarket: revenue per vendor this month

**D158 (Tue)**
- [ ] Theory: Vendor-scoping the catalog
- [ ] Mini Exercise: —
- [ ] Project: Adapt StockPilot's product model: add `vendor_id`, vendor onboarding endpoint
- [ ] DSA: Happy Number
- [ ] SQL: Product Sales Analysis III

**D159 (Wed)**
- [ ] Theory: Vendor-scoped search
- [ ] Mini Exercise: —
- [ ] Project: Adapt DocuVault's ES sync pattern to index vendor-scoped products
- [ ] DSA: Plus One
- [ ] SQL: AtlasMarket: vendors with no products listed

**D160 (Thu)**
- [ ] Theory: Multi-page navigation with React Router — the one piece your 3 prior single-view frontends didn't need — *React Router docs "Tutorial"*
- [ ] Mini Exercise: Extract a shared `Button`/`Card` component from copy-pasted markup across `carepoint-web`, `fleettrack-web`, `docuvault-web` into a tiny local component set `storefront/` can start from
- [ ] Project: `storefront/` scaffold (Vite + React + TS), React Router routes for product list / cart / checkout, product list page with TanStack Query
- [ ] DSA: Pow(x, n)
- [ ] SQL: AtlasMarket: top 5 vendors by order count

**D161 (Fri)**
- [ ] Theory: TanStack Query caching, cart state design — *TanStack Query "Quick Start"*
- [ ] Mini Exercise: Write one React Testing Library test for the cart's add/remove logic
- [ ] Project: Cart state (local component state) + cart UI, wired to the router's cart route
- [ ] DSA: Merge Sorted Array
- [ ] SQL: The Most Recent Three Orders

**D162 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Explain TanStack Query cache vs your Redis cache-aside pattern, out loud
- [ ] Project: —
- [ ] DSA: Review: redo Thursday's problem from memory — Pow(x, n)
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — Product Sales Analysis III

### Week 28 — AtlasMarket Integration Sprint (part 2), Mock Interviews

**D163 (Mon)**
- [ ] Theory: Multi-vendor checkout design; the bulkhead pattern — bounded per-downstream connection pools on the gateway — **Release It!* (Nygard) bulkhead section*
- [ ] Mini Exercise: Bounded semaphore demo: one slow "dependency" starves a shared pool, then a bulkhead fixes it
- [ ] Project: Checkout: cart → split into `order_vendor_groups` → PayFlow idempotent payment → per-vendor ledger entries; bulkhead pools added to the gateway's calls to each of the 5 downstream services
- [ ] DSA: Design Twitter
- [ ] SQL: AtlasMarket: orders split across 2+ vendors

**D164 (Tue)**
- [ ] Theory: Per-vendor fulfillment status; deploying to real cloud infrastructure — *AWS/GCP managed-Postgres docs*
- [ ] Mini Exercise: —
- [ ] Project: Adapt WareFlow's status concepts to `order_vendor_groups`; deploy the gateway + `catalog-service` to real cloud compute, DB on managed Postgres in the private subnet from Wednesday; `docs/cloud-deployment-notes.md`
- [ ] DSA: LFU Cache
- [ ] SQL: AtlasMarket: per-vendor payout reconciliation

**D165 (Wed)**
- [ ] Theory: Checkout UI, end-to-end wiring; feature flags + canary release
- [ ] Mini Exercise: Hand-rolled feature-flag service (config table + `is_enabled(flag, user_id)`, percentage rollout)
- [ ] Project: Storefront checkout form wired to the real API, shipped dark behind the feature flag then ramped 10% → 100% while watching Grafana
- [ ] DSA: Word Search II
- [ ] SQL: Capstone review: rewrite Week 12's partition-aware query from memory

**D166 (Thu)**
- [ ] Theory: Mock system design interview #1; SD10 (Video Streaming Platform) — *System Design Interview (Xu), relevant chapter*
- [ ] Mini Exercise: —
- [ ] Project: Design multi-vendor checkout from scratch on a whiteboard (no code), then compare to what you built; work SD10 from `system-design-problems.md`
- [ ] DSA: Merge k Sorted Lists
- [ ] SQL: Capstone review: rewrite Week 6's window-function ranking query from memory

**D167 (Fri)**
- [ ] Theory: Mock system design interview #2 + #3; SD16 (Proximity/Nearby-Search Service); end-to-end browser testing with Playwright — *Playwright docs "Getting started" + "Writing tests"*
- [ ] Mini Exercise: —
- [ ] Project: Design payment idempotency + product search from scratch, unprompted; work SD16; Playwright test driving a real browser through browse → cart → checkout
- [ ] DSA: Alien Dictionary
- [ ] SQL: Capstone: the one query you'd hand an interviewer

**D168 (Sat)**
- [ ] Theory: **Review**; SD20 — design AtlasMarket from scratch; full behavioral pass
- [ ] Mini Exercise: Design AtlasMarket itself, 45 min, blank page, no notes, then compare against `docs/architecture.md` — the closing synthesis of the whole 19-problem bank
- [ ] Project: `docs/atlasmarket-roadmap-post-bootcamp.md` (deferred features)
- [ ] DSA: Review: redo Thursday's problem from memory — Merge k Sorted Lists
- [ ] SQL: Review: rewrite Tuesday's query from memory, then extend it — AtlasMarket: per-vendor payout reconciliation

### Week 29 — URL Shortener + Rate Limiter, Built For Real

**D169 (Mon)**
- [ ] Theory: URL Shortener: base62 code generation, redirect semantics — *Revisit `system-design-problems.md` SD1*
- [ ] Mini Exercise: —
- [ ] Project: New repo `url-shortener/`, `POST /shorten` (counter-based base62 code) + `GET /{code}` (301 redirect); deleted codes return 404

**D170 (Tue)**
- [ ] Theory: Cache-aside for hot redirects — *Redis docs caching (Phase 2 refresher)*
- [ ] Mini Exercise: —
- [ ] Project: Redis cache-aside in front of the redirect path, TTL + immediate invalidation on delete; load test cache-cold vs cache-warm

**D171 (Wed)**
- [ ] Theory: Rate Limiter Service: token bucket vs sliding-window-counter — *Revisit SD2*
- [ ] Mini Exercise: —
- [ ] Project: New repo `rate-limiter/`, `POST /check {key, limit, window}` implementing both algorithms behind one interface

**D172 (Thu)**
- [ ] Theory: Proving it's actually distributed
- [ ] Mini Exercise: —
- [ ] Project: Run 3 rate-limiter instances behind Nginx, one shared Redis; benchmark memory footprint of both algorithms at 100k tracked keys

**D173 (Fri)**
- [ ] Theory: Retrofitting: URL Shortener calls the real Rate Limiter
- [ ] Mini Exercise: —
- [ ] Project: `POST /shorten` calls the Rate Limiter service instead of an ad hoc check; READMEs + model cards for both services; tag `v0.1-sd-builds-1`

**D174 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the token-bucket implementation from memory, explain the accuracy/memory trade-off out loud
- [ ] Project: —

### Week 30 — Distributed Job Scheduler, Built For Real; Full Program Wrap

**D175 (Mon)**
- [ ] Theory: Distributed Job Scheduler: wiring Phase 5's Raft cluster as real infrastructure — *Revisit SD14 + Phase 5 Week 24 Friday's toy dispatcher*
- [ ] Mini Exercise: —
- [ ] Project: New repo `job-scheduler/`, `Job` model + persistence, `POST /jobs {cron_expr, payload}`; the scheduler's processes form a real Raft cluster (reusing Phase 5's implementation, not rebuilding it)

**D176 (Tue)**
- [ ] Theory: Leader-only dispatch, idempotent job handlers
- [ ] Mini Exercise: —
- [ ] Project: Only the current Raft leader dispatches due jobs; job handlers are idempotent (same discipline as every queue consumer since Phase 3)

**D177 (Wed)**
- [ ] Theory: Fault testing: kill the leader mid-dispatch-decision
- [ ] Mini Exercise: `freezegun`-compressed 24-hour simulated run (the same technique from every Celery Beat test since Phase 2)
- [ ] Project: Kill-leader-mid-dispatch test; 24h-simulated run asserting every scheduled tick fired exactly once

**D178 (Thu)**
- [ ] Theory: Polish, comparison writeup
- [ ] Mini Exercise: —
- [ ] Project: README + model card for the scheduler; `docs/sd-builds-vs-paper-designs.md` comparing all three real builds (Projects 26-28) against their original SD1/SD2/SD14 paper designs — what the real build forced you to handle that the paper design didn't; tag `v0.1-sd-builds-2`

**D179 (Fri)**
- [ ] Theory: Buffer / catch-up; final capstone integration check
- [ ] Mini Exercise: —
- [ ] Project: Confirm all of Phase 6 (PayFlow, AtlasMarket, and Projects 26-28) still runs green together — this is the first day all of it has been exercised as one whole

**D180 (Sat)**
- [ ] Theory: **FULL 6-MONTH PROGRAM WRAP**
- [ ] Mini Exercise: —
- [ ] Project: `docs/postmortem-phase6.md`, full 6-month retrospective across all 13 Track A projects (the original 10 plus Projects 26-28), tag `v1.0-bootcamp-complete`

---

## Phase 7 — LLM Zoomcamp (Weeks 31-36)

### Week 31 — Intro, Vector Search, DocuVault Semantic Search

**D181 (Mon)**
- [ ] Theory: LLM basics & prompting fundamentals — tokens, context window, temperature, zero/few-shot; open vs closed models — *OpenAI "Prompt engineering" guide + Ollama docs intro*
- [ ] Mini Exercise: Run the same question through a closed API model and a local Ollama model, compare answer/latency/cost
- [ ] Project: New `docuvault/rag/` module scaffold; `docs/llm-provider-decision.md` picking a primary API provider + Ollama as free dev fallback

**D182 (Tue)**
- [ ] Theory: RAG architecture overview — why RAG over fine-tuning/bigger context; retrieval+generation pipeline shape — *DataTalksClub llm-zoomcamp Module 1 README*
- [ ] Mini Exercise: Sketch the full pipeline diagram in `docs/rag-architecture.md` before writing any code
- [ ] Project: `docs/rag-architecture.md` for DocuVault: ingestion pipeline + query pipeline diagram

**D183 (Wed)**
- [ ] Theory: Embeddings & vector representations — how text becomes a vector, cosine similarity, embedding model choice — *OpenAI "Embeddings" guide*
- [ ] Mini Exercise: Embed 10 sample sentences, compute pairwise cosine similarity by hand with numpy, sanity-check similar pairs score higher
- [ ] Project: `rag/embeddings.py` wraps the chosen embedding model, batches DocuVault chunk text

**D184 (Thu)**
- [ ] Theory: Vector databases — Qdrant collections/points/payload, distance metrics, HNSW; brief comparison to Elasticsearch dense_vector — *Qdrant docs "Collections" + "Points"; Elastic docs "Dense vector field type" (Phase 5 refresher)*
- [ ] Mini Exercise: Spin up local Qdrant via Docker, create a collection, upsert 20 fake vectors, run a `search` query
- [ ] Project: Add `qdrant` service to DocuVault's compose; create `documents_chunks` collection sized to the embedding model's dimension

**D185 (Fri)**
- [ ] Theory: Building a basic semantic search endpoint — chunking strategy, indexing pipeline, query-time retrieval — *Qdrant docs "Search"; vector-DB vendor chunking-strategies guide*
- [ ] Mini Exercise: Chunk one long document 3 ways (fixed-size, fixed-size+overlap, paragraph-based), compare chunk counts/quality
- [ ] Project: `rag/ingest.py` (chunk existing documents → embed → upsert to Qdrant) + `GET /documents/semantic-search?q=` endpoint

**D186 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo Wednesday's cosine-similarity-by-hand exercise from memory
- [ ] Project: Re-read `rag/ingest.py` for anything hard-coded that shouldn't be

### Week 32 — Agents, PeopleOps HR-Policy Agent

**D187 (Mon)**
- [ ] Theory: Agentic patterns — tool use / function calling, how a model decides to call a tool — *OpenAI "Function calling" guide / Anthropic "Tool use" docs*
- [ ] Mini Exercise: Give a model one fake tool (`get_weather(city)`), confirm it emits a correctly structured tool call for an ambiguous prompt
- [ ] Project: New `peopleops/agent/` scaffold; tool schema for `get_leave_balance(employee_id)` wrapping PeopleOps' existing leave-balance API

**D188 (Tue)**
- [ ] Theory: ReAct-style reasoning loops — Reason → Act → Observe, why this beats a single forced tool call — *ReAct paper (Yao et al., arXiv:2210.03629), abstract + §3*
- [ ] Mini Exercise: Trace one ReAct loop by hand on paper for a 2-step question before writing code
- [ ] Project: `agent/loop.py` — basic ReAct loop: model reasons, optionally calls `get_leave_balance`, observes result, responds

**D189 (Wed)**
- [ ] Theory: Multi-step agents with memory — carrying conversation + tool-result history without blowing the context window — *OpenAI/Anthropic docs on context management*
- [ ] Mini Exercise: Simulate a 10-turn conversation, measure token growth, implement a sliding-window/summary trim
- [ ] Project: Add session memory (last N turns + running summary) to the HR agent

**D190 (Thu)**
- [ ] Theory: Agent guardrails & failure modes — looping, hallucinated tool args, calling tools it shouldn't — *OWASP Top 10 for LLM Applications — excessive-agency section*
- [ ] Mini Exercise: Provoke the unguarded agent into calling `get_leave_balance` with a malformed/unauthorized `employee_id`, observe the failure
- [ ] Project: Add tool-arg validation + max-step limit + a scope check ("agent may only look up the requesting employee's own balance")

**D191 (Fri)**
- [ ] Theory: Orchestrating an agent that calls an external API as a tool — end-to-end wiring, error handling on tool failure — *PeopleOps' own API docs + provider tool-use error-handling docs*
- [ ] Mini Exercise: Simulate the leave-balance API returning a 500/timeout, confirm the agent surfaces a clean fallback instead of crashing
- [ ] Project: `POST /hr-assistant/ask` endpoint wiring the full agent (HR-policy Q&A + leave-balance tool) into PeopleOps

**D192 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the ReAct loop trace from memory
- [ ] Project: Re-read `agent/loop.py` for the exact failure modes discussed this week

### Week 33 — Evaluation + Monitoring on DocuVault Semantic Search

**D193 (Mon)**
- [ ] Theory: RAG evaluation — offline metrics: hit rate, MRR — *RAGAS docs "Metrics"*
- [ ] Mini Exercise: Compute hit rate and MRR by hand on a 5-query toy retrieval result set
- [ ] Project: Golden eval set for DocuVault semantic search (20–30 query→expected-doc pairs) in `eval/golden_set.json`

**D194 (Tue)**
- [ ] Theory: Implementing an offline eval harness — hit rate/MRR computed automatically against the golden set
- [ ] Mini Exercise: —
- [ ] Project: `eval/retrieval_eval.py` runs the golden set through the semantic-search endpoint, reports hit rate@k and MRR

**D195 (Wed)**
- [ ] Theory: LLM-as-judge evaluation — using a model to grade answer quality/faithfulness — *RAGAS docs "faithfulness"/"answer relevancy"*
- [ ] Mini Exercise: Hand-grade 5 answers yourself, then have an LLM judge grade the same 5, compare agreement
- [ ] Project: `eval/llm_judge.py` scores a generated answer's faithfulness-to-context on a 1–5 scale, wired into the harness

**D196 (Thu)**
- [ ] Theory: Cost & latency tracking for LLM calls; logging chat sessions & feedback loops — *OpenAI/Anthropic API docs — usage/token accounting*
- [ ] Mini Exercise: Log token counts + wall-clock latency for 10 sample calls, compute $ cost from published pricing
- [ ] Project: `rag/telemetry.py` wraps LLM + embedding calls, logs tokens/cost/latency (reusing Phase 1's structlog); `POST /documents/semantic-search/feedback` (thumbs up/down)

**D197 (Fri)**
- [ ] Theory: A/B testing prompts/models — the statistics underneath: null hypothesis, p-values, confidence intervals, and why a hit-rate delta on 30 golden-set queries usually isn't statistically significant — *OpenAI "Best practices for prompt engineering" + Practical Statistics for Data Scientists Ch.3 (or Khan Academy "Significance tests" as a free alternative)*
- [ ] Mini Exercise: Compute a 95% confidence interval by hand on the two prompt variants' hit rates from Thu's golden set; decide honestly whether the delta is real or noise
- [ ] Project: Prompt-variant flag on the search endpoint; log which variant served each request, feeding the eval harness; `docs/ab-test-readout.md` reporting the confidence interval, not just "variant B looked better"

**D198 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the hit-rate/MRR by-hand calculation from memory
- [ ] Project: Re-run the full eval harness + judge suite; review cost/latency numbers

### Week 34 — Best Practices, Project Example — CarePoint Prototype

**D199 (Mon)**
- [ ] Theory: Query rewriting — reformulating a user's raw question for better retrieval (resolving pronouns, expanding acronyms) — *Qdrant docs: Q&A/RAG tutorial*
- [ ] Mini Exercise: Take 5 real conversational follow-ups ("what about the second one?") and hand-write the rewritten standalone version
- [ ] Project: New `carepoint/rag/` scaffold; query-rewrite step using conversation history before embedding

**D200 (Tue)**
- [ ] Theory: Hybrid search — combining sparse keyword (Elasticsearch) + dense vector (Qdrant) results — *Elastic docs "Hybrid search"; Qdrant docs on combining with keyword search*
- [ ] Mini Exercise: Run the same query keyword-only, vector-only, and naively combined; compare top-5 results
- [ ] Project: Ingest CarePoint's FAQ/policy docs into both ES and Qdrant; implement hybrid retrieval (weighted score fusion / RRF)

**D201 (Wed)**
- [ ] Theory: Re-ranking retrieved chunks before generation — *Cross-encoder re-ranking overview*
- [ ] Mini Exercise: Re-rank Tuesday's hybrid top-20 down to top-5 using a simple cross-encoder or LLM-scored rerank, compare ordering
- [ ] Project: Add a re-ranking step to CarePoint's retrieval pipeline before prompt assembly

**D202 (Thu)**
- [ ] Theory: Caching LLM responses to cut cost; guardrails — prompt injection basics & output validation — *OWASP Top 10 for LLM Applications — prompt injection section*
- [ ] Mini Exercise: Try 3 basic prompt-injection strings ("ignore previous instructions and...") against the unguarded pipeline, observe what breaks
- [ ] Project: Semantic response cache (normalized-query+context hash) + output validator rejecting injected instructions/unsupported claims

**D203 (Fri)**
- [ ] Theory: Reference end-to-end RAG project walkthrough mapped onto CarePoint; writing a short decision record for the chosen stack — *DataTalksClub llm-zoomcamp "Project examples" module*
- [ ] Mini Exercise: —
- [ ] Project: Prototype the full CarePoint patient-FAQ assistant end-to-end (hybrid retrieval + rerank + generation + injection guardrail) behind `POST /patient-faq/ask`; `docs/carepoint-rag-decision-record.md`

**D204 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the RRF/hybrid fusion math from memory
- [ ] Project: Re-run all injection tests; re-read the decision record for gaps before next week's build

### Week 35 — Project 1 — CarePoint Patient-FAQ Assistant (Full Build)

**D205 (Mon)**
- [ ] Theory: Formalizing the ingestion pipeline for production — versioned re-index, source-doc tracking — *Revisit Phase 5 DocuVault reindex notes*
- [ ] Mini Exercise: —
- [ ] Project: Production-grade ingestion: `POST /patient-faq/reindex` (rebuild ES + Qdrant from source docs, DocuVault-style recovery), chunk versioning metadata

**D206 (Tue)**
- [ ] Theory: Hardening the retrieval+generation API — auth, rate limiting, per-session conversation state — *Revisit Phase 1/4 auth & rate-limiting notes*
- [ ] Mini Exercise: —
- [ ] Project: Add auth to `/patient-faq/ask`, per-session short conversation memory, rate limiting per patient account

**D207 (Wed)**
- [ ] Theory: Full evaluation suite wired to CI — hit rate, MRR, LLM-judge faithfulness, injection-guardrail regression
- [ ] Mini Exercise: —
- [ ] Project: Wire Week 33's eval harness + Week 34's injection tests into CI as a required check on every PR

**D208 (Thu)**
- [ ] Theory: Monitoring — cost/latency dashboards, escalation logging (when the assistant hands off to a human) — *Revisit Phase 4 Grafana/Prometheus stack docs*
- [ ] Mini Exercise: —
- [ ] Project: Grafana panel for cost/latency/hit-rate over time; explicit "escalate to staff" path logged separately on low confidence

**D209 (Fri)**
- [ ] Theory: Deployment — containerize and ship the assistant inside CarePoint's existing service mesh — *Revisit Phase 4/5 deployment notes (Compose/K8s)*
- [ ] Mini Exercise: —
- [ ] Project: Add `patient-faq` service to CarePoint's compose/K8s manifests; deploy and smoke-test in the local cluster

**D210 (Sat)**
- [ ] Theory: **Review/retrospective**
- [ ] Mini Exercise: Mock-answer all Week-35 questions timed
- [ ] Project: `docs/postmortem-carepoint-faq.md`, tag `v0.1-carepoint-faq`

### Week 36 — Project 2 (DocuVault Chat) + Project 3 (AtlasMarket Assistant), Phase Wrap

**D211 (Mon)**
- [ ] Theory: Formalizing Weeks 31/29's DocuVault prototype into a conversational "ask your documents" chatbot (multi-turn, citations) — *Revisit own Week 31/29 notes + provider multi-turn chat docs*
- [ ] Mini Exercise: —
- [ ] Project: `POST /documents/chat` — multi-turn RAG chat over the DocuVault corpus, reusing Week 34's hybrid+rerank pipeline, with per-document citation

**D212 (Tue)**
- [ ] Theory: Access-control-aware retrieval — never answer from a document the requester can't read (the Phase 5 deferred concern, solved now) — *Revisit Phase 5 DocuVault "Possible Improvements" note*
- [ ] Mini Exercise: —
- [ ] Project: Filter Qdrant/ES retrieval results by the requesting user's document permissions before they ever reach the prompt

**D213 (Wed)**
- [ ] Theory: Evaluation + deployment for the DocuVault chatbot
- [ ] Mini Exercise: —
- [ ] Project: Wire DocuVault chat into Week 33's eval harness (new golden set for conversational queries); deploy alongside existing DocuVault services

**D214 (Thu)**
- [ ] Theory: AtlasMarket product Q&A — scoping retrieval per-vendor, ingesting product catalog + reviews as the knowledge base — *Revisit Phase 6 AtlasMarket vendor-scoping notes + Qdrant/ES metadata-filtering docs*
- [ ] Mini Exercise: —
- [ ] Project: Ingest AtlasMarket product descriptions/specs/reviews with `vendor_id`/`product_id` payload; vendor/product-scoped retrieval

**D215 (Fri)**
- [ ] Theory: Generation + guardrails + API for the buyer-facing support assistant — no invented specs/prices, escalate to vendor when unsure
- [ ] Mini Exercise: —
- [ ] Project: `POST /support/ask` — generation with a strict "answer only from retrieved product data" system prompt + output guardrail rejecting invented prices/specs; escalation path to vendor support

**D216 (Sat)**
- [ ] Theory: **Phase 7 wrap review**
- [ ] Mini Exercise: Mock-answer all Phase-7 questions timed, no notes
- [ ] Project: `docs/postmortem-phase7.md` comparing all three assistants; tag `v0.7-phase7`

---

## Phase 8 — AI Dev Tools Zoomcamp (Weeks 37-41)

### Week 37 — AI Dev Tools Overview, End-to-End Workflow, AtlasMarket Feature

**D217 (Mon)**
- [ ] Theory: Landscape of AI dev tools: Claude Code vs. GitHub Copilot vs. Cursor, how they differ architecturally — *Claude Code docs Quickstart/Overview; GitHub Copilot docs "What is Copilot"*
- [ ] Mini Exercise: Install/configure Claude Code CLI on the AtlasMarket repo, run one trivial prompt end to end
- [ ] Project: Write `docs/ai-tools-landscape.md` comparison notes; pick the AtlasMarket feature to build this week

**D218 (Tue)**
- [ ] Theory: End-to-end AI-assisted workflow: spec → code → test → PR — *Claude Code docs "Common workflows"*
- [ ] Mini Exercise: Write a one-page feature spec (business problem, requirements, acceptance criteria)
- [ ] Project: Commit the spec to AtlasMarket: `docs/features/<feature>.md`

**D219 (Wed)**
- [ ] Theory: Prompt/context engineering for coding tasks: `CLAUDE.md`, repo context, scoping the ask — *Claude Code docs "Manage Claude's memory" (`CLAUDE.md`); Anthropic prompt engineering guide*
- [ ] Mini Exercise: Write a `CLAUDE.md` for AtlasMarket capturing architecture + conventions
- [ ] Project: Prompt the agent with spec + `CLAUDE.md` context to implement the feature; capture the first diff (do not merge)

**D220 (Thu)**
- [ ] Theory: Evaluating AI-generated code: review checklist, common failure modes (over-broad diffs, silently wrong edge cases, missing tests) — *Anthropic Engineering blog "Claude Code: Best Practices for Agentic Coding"*
- [ ] Mini Exercise: Build your own AI-diff review checklist (5-8 items)
- [ ] Project: Apply the checklist to yesterday's diff, write review notes, request specific revisions from the agent

**D221 (Fri)**
- [ ] Theory: Shipping the workflow: reviewed diff → merged PR; retro on the process itself — *Claude Code docs on PR/GitHub Actions workflow*
- [ ] Mini Exercise: —
- [ ] Project: Merge the revised diff, open/land the PR on AtlasMarket; write `docs/features/<feature>-retro.md` documenting prompts + diffs + review notes end to end

**D222 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo Wednesday's `CLAUDE.md` from memory, compare against the real one
- [ ] Project: Re-read your own retro doc, note one thing you'd do differently next time

### Week 38 — MCP Fundamentals, Custom MCP Server, Minimal Coding Agent

**D223 (Mon)**
- [ ] Theory: MCP protocol fundamentals: resources, tools, prompts, transports (stdio/SSE) — *MCP docs "Introduction" + "Core architecture"*
- [ ] Mini Exercise: Run the MCP Python SDK "hello tool" quickstart server locally, connect a client to it
- [ ] Project: Scaffold `stockpilot-mcp/` with the MCP SDK installed

**D224 (Tue)**
- [ ] Theory: Writing a custom MCP server: tool schema design, input validation, error handling — *MCP docs "Build an MCP Server" (Python SDK); "Tools" spec*
- [ ] Mini Exercise: Extend the hello-tool server with a second tool taking structured args
- [ ] Project: Design tool schemas for StockPilot: `get_low_stock`, `get_product`, `list_orders` (read-only)

**D225 (Wed)**
- [ ] Theory: Wiring an MCP server to a real API: auth, scoped read-only tokens — *MCP docs "Resources"*
- [ ] Mini Exercise: —
- [ ] Project: Implement the 3 tools against the real StockPilot API with a read-only service token, expose as an MCP server

**D226 (Thu)**
- [ ] Theory: Coding-agent architectures: tool loops, planning, ReAct-style reasoning, stop conditions — *Anthropic Engineering blog "Building Effective Agents"*
- [ ] Mini Exercise: On paper, design your own agent's loop (plan → act → observe → decide) before writing any code
- [ ] Project: Scaffold `mini-agent/`: LLM client + hand-rolled tool-loop skeleton, no framework

**D227 (Fri)**
- [ ] Theory: Connecting the agent to the MCP server end-to-end; logging every tool call for observability — *MCP docs "Prompts" spec*
- [ ] Mini Exercise: —
- [ ] Project: Wire `mini-agent` to call the StockPilot MCP server's tools; ask it "what products are low on stock right now?" end-to-end

**D228 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the tool-loop stop-condition logic from memory, explain it out loud
- [ ] Project: Re-read the run log from Friday's session, note anything surprising

### Week 39 — AI-Assisted CI/CD, Low-Code Automation, Guardrails

**D229 (Mon)**
- [ ] Theory: AI-assisted CI/CD: automated PR-review bots — *GitHub Actions docs "Building and testing" (reused from Phase 4); Claude Code docs "GitHub Actions integration"*
- [ ] Mini Exercise: Run a Claude-Code-based GitHub Action on a scratch PR in a test repo, read its comment
- [ ] Project: Add a PR-review-bot workflow to one real repo (comment-only, no approve/merge permission)

**D230 (Tue)**
- [ ] Theory: AI in incident response / log triage — *Claude Code docs "Headless mode"/SDK for scripted use*
- [ ] Mini Exercise: Feed a sample log dump to a headless Claude Code invocation, ask for a triage summary
- [ ] Project: Script `triage_logs.py`: summarize a repo's latest CI failure logs via the LLM API, post a summary comment

**D231 (Wed)**
- [ ] Theory: Low-code automation platforms: n8n fundamentals — triggers, nodes, workflow model — *n8n docs "Workflow basics," "Nodes"*
- [ ] Mini Exercise: Stand up n8n locally (Docker), build a trivial workflow (webhook → log)
- [ ] Project: Environment setup only — no project code this day

**D232 (Thu)**
- [ ] Theory: Building a cross-system automation workflow — *n8n docs "HTTP Request node," "Webhooks"*
- [ ] Mini Exercise: —
- [ ] Project: Build an n8n workflow connecting two systems: StockPilot low-stock data → Slack/email notification

**D233 (Fri)**
- [ ] Theory: Guardrails for autonomous CI actions: what may/may not auto-merge, scoped permissions, branch protection — *GitHub Actions docs "Security hardening for GitHub Actions"*
- [ ] Mini Exercise: Write a guardrails policy doc: bot may comment, may not approve, may not merge, may not push to `main`, tokens are read-only/scoped
- [ ] Project: Lock down the PR-review bot's GitHub token permissions explicitly; configure branch protection requiring human review regardless of bot output

**D234 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the guardrails policy doc from memory
- [ ] Project: Re-read both automations (PR bot + n8n workflow) for any scope creep

### Week 40 — Project 1 — StockPilot Bug-Fix Coding Agent

**D235 (Mon)**
- [ ] Theory: Designing the agent: ticket scope, classifier rules, guardrails plan — *Claude Code docs "Subagents"/"Hooks"*
- [ ] Mini Exercise: Draft the ticket classifier's decision rules on paper (in-scope vs. out-of-scope examples)
- [ ] Project: Write `docs/bugfix-agent-design.md` (business problem, scope, guardrails); scaffold `bugfix-agent/`

**D236 (Tue)**
- [ ] Theory: Building the planner + tool loop wired to StockPilot MCP + repo file tools — *MCP Python SDK docs (tool implementation, recap)*
- [ ] Mini Exercise: —
- [ ] Project: Implement the planner (ticket + repo context → bounded plan); wire `read_file`/`list_dir`/`write_file` scoped to a path allow-list

**D237 (Wed)**
- [ ] Theory: Implementing the human-approval gate — *Claude Code docs "Permissions"*
- [ ] Mini Exercise: —
- [ ] Project: Add the approval gate (agent stops after diff+test output, requires explicit "approve"); add an "open PR" tool only — no merge/push-to-main tool exists

**D238 (Thu)**
- [ ] Theory: Guardrails: reject-by-default classifier, scoped permission enforcement, adversarial testing — *GitHub Actions docs "Security hardening" (recap)*
- [ ] Mini Exercise: —
- [ ] Project: Make the classifier a mandatory first step (reject-by-default); run full test/lint/type-check gate before showing the diff to a human, verbatim

**D239 (Fri)**
- [ ] Theory: End-to-end real run — *— (application day)*
- [ ] Mini Exercise: —
- [ ] Project: Feed the agent one real, defined StockPilot ticket end-to-end: ticket → plan → diff → tests → human approval → PR opened; verify it declines a second, out-of-scope ticket

**D240 (Sat)**
- [ ] Theory: **Review / retrospective**
- [ ] Mini Exercise: Redo the classifier's decision rules from memory
- [ ] Project: Write `docs/bugfix-agent-retro.md` — what worked, what you'd tighten

### Week 41 — Project 2 — Reconciliation Pipeline; Project 3 — Freeform Capstone; Phase Wrap

**D241 (Mon)**
- [ ] Theory: Designing the reconciliation pipeline: schedule trigger, read-only token scoping — *GitHub Actions docs "Events that trigger workflows: schedule"*
- [ ] Mini Exercise: —
- [ ] Project: Write `docs/reconciliation-pipeline-design.md`; scaffold the GitHub Actions cron job in LedgerBase calling `/reports/trial-balance` with a read-only token

**D242 (Tue)**
- [ ] Theory: Building the reconciliation-check + report artifact — *— (application day)*
- [ ] Mini Exercise: —
- [ ] Project: Implement the reconciliation-check function; render markdown/JSON report artifact; upload as workflow artifact and POST to an n8n webhook

**D243 (Wed)**
- [ ] Theory: n8n branch + notify workflow, failure-path testing — *n8n docs "Credentials" (webhook auth/HMAC)*
- [ ] Mini Exercise: —
- [ ] Project: Build the n8n workflow: authenticated webhook → branch on pass/fail → distinct Slack/email node per outcome; export workflow JSON into the repo

**D244 (Thu)**
- [ ] Theory: Project 3 kickoff: scoping the freeform capstone — *Recap of MCP docs + Claude Code "Best practices," as needed for your chosen direction*
- [ ] Mini Exercise: —
- [ ] Project: Write the one-page design note (business problem, scope, guardrail, what's left out); scaffold its repo/dir

**D245 (Fri)**
- [ ] Theory: Building the capstone, reusing Phase 8 patterns fast — *— (application day)*
- [ ] Mini Exercise: —
- [ ] Project: Implement the MCP tool(s) + tool loop/workflow + the stated guardrail; get one real end-to-end path working

**D246 (Sat)**
- [ ] Theory: **Phase 8 wrap review**
- [ ] Mini Exercise: Explain your bug-fix agent's full pipeline out loud, start to finish, from memory
- [ ] Project: Write `docs/postmortem-phase8.md` (what's deferred to Phase 11, what you'd harden first); tag `v0.8-phase8`

---

## Phase 9 — Machine Learning Zoomcamp (Weeks 42-49)

### Week 42 — ML Math Foundations

**D247 (Mon)**
- [ ] Theory: Linear algebra for ML: vectors, matrices, dot products, the geometric intuition behind "a model is a function of a weight vector" — *3Blue1Brown "Essence of Linear Algebra" (free video series) Ch.1-4, or Ch.1-2 of any standard linear algebra text*
- [ ] Mini Exercise: Implement matrix multiplication from scratch in pure Python (no NumPy), then again with NumPy, compare correctness and timing
- [ ] Project: `docs/ml-math-notes.md` — vectors/matrices section, in your own words, with the StockPilot feature vector as a concrete running example

**D248 (Tue)**
- [ ] Theory: Calculus for ML: partial derivatives, the chain rule, why gradients point in the direction of steepest ascent — *Khan Academy "Multivariable calculus" (free) — partial derivatives + gradient sections*
- [ ] Mini Exercise: Derive, on paper, the gradient of Mean Squared Error with respect to the weight vector for linear regression — no code yet, just the math
- [ ] Project: Add the derivation to `docs/ml-math-notes.md`, typed out step by step

**D249 (Wed)**
- [ ] Theory: Gradient descent, implemented from scratch
- [ ] Mini Exercise: Implement batch gradient descent for linear regression using only NumPy (no scikit-learn), converge on a toy dataset, plot the loss curve
- [ ] Project: Reproduce Phase 9 Week 43's upcoming baseline linear regression using your own from-scratch gradient descent instead of the normal equation, verify the learned weights match closely

**D250 (Thu)**
- [ ] Theory: Probability & statistics deepened: distributions, maximum likelihood estimation — *Any intro-statistics MLE chapter (e.g. Bishop's *Pattern Recognition and Machine Learning* §1.2, or a free equivalent)*
- [ ] Mini Exercise: Derive logistic regression's cross-entropy loss as the maximum-likelihood estimate under a Bernoulli model — on paper, then confirm numerically that maximizing likelihood equals minimizing the cross-entropy you already know from Phase 7/9
- [ ] Project: Add the MLE derivation to `docs/ml-math-notes.md`, tied explicitly to the logistic regression you'll build in Week 44

**D251 (Fri)**
- [ ] Theory: The Bayesian view: priors, posteriors, and what L2 regularization actually is
- [ ] Mini Exercise: Show, numerically, that Ridge regression's solution is the MAP (maximum a posteriori) estimate under a Gaussian prior on the weights — vary the prior's variance and watch it match `alpha`
- [ ] Project: Implement Ridge regression from scratch via gradient descent (extending Wednesday's code with the L2 penalty term), compare coefficients against `sklearn.Ridge` on the same data

**D252 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo Tuesday's MSE gradient derivation from memory, on paper, no notes
- [ ] Project: Re-read `docs/ml-math-notes.md` end to end, confirm every claim in it is something you could reproduce on a whiteboard

### Week 43 — Intro to ML, Linear Regression, StockPilot Demand Forecaster

**D253 (Mon)**
- [ ] Theory: Supervised learning framing, CRISP-DM, train/val/test split — *ML Zoomcamp Module 1 — Intro to ML; Géron Ch.2 "Look at the Big Picture"*
- [ ] Mini Exercise: Implement a train/val/test split function from scratch on a toy dataset
- [ ] Project: EDA on StockPilot's historical order data; aggregate weekly per-product demand

**D254 (Tue)**
- [ ] Theory: NumPy/Pandas refresher, missing data, groupby aggregation — *Pandas docs "Working with missing data"; Géron Ch.2 data-cleaning section*
- [ ] Mini Exercise: Pandas groupby/aggregation drill on toy sales data
- [ ] Project: Build the weekly per-product feature table joining products + order_items + stock_movements

**D255 (Wed)**
- [ ] Theory: Linear regression from scratch (normal equation) — *ML Zoomcamp Module 2 — Regression; Géron Ch.4 "The Normal Equation"*
- [ ] Mini Exercise: Implement normal-equation regression with NumPy on toy data, compare to `sklearn.LinearRegression`
- [ ] Project: Baseline linear regression predicting next-week demand from lag features

**D256 (Thu)**
- [ ] Theory: Feature engineering, one-hot encoding — *scikit-learn docs "Preprocessing data" (OneHotEncoder); Géron Ch.2 categorical encoding*
- [ ] Mini Exercise: Encode a categorical column with `OneHotEncoder` vs `pd.get_dummies`, compare output
- [ ] Project: Add category/supplier one-hot features and a week-of-year seasonality feature

**D257 (Fri)**
- [ ] Theory: Regularization (Ridge), RMSE evaluation, bias-variance in practice — *ML Zoomcamp Module 2 — Regularized Linear Models; Géron Ch.4 "Ridge Regression"*
- [ ] Mini Exercise: Plot train vs. validation RMSE across Ridge `alpha` values (a learning curve)
- [ ] Project: Add Ridge regularization, tune `alpha` on the validation set, record final Week-43 RMSE vs. naive baseline

**D258 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the normal-equation regression from memory, no notes
- [ ] Project: Re-read the feature table for anything that smells like leaked future information

### Week 44 — Classification, Evaluation, QuickServe Churn Predictor

**D259 (Mon)**
- [ ] Theory: Logistic regression, sigmoid, log-loss — *ML Zoomcamp Module 3 — Classification; Géron Ch.4 "Logistic Regression"*
- [ ] Mini Exercise: Implement sigmoid + log-loss manually, verify against `sklearn`
- [ ] Project: EDA on QuickServe customer order history; define the churn label (no repeat order within a cadence window)

**D260 (Tue)**
- [ ] Theory: Feature importance via coefficients — *scikit-learn docs LogisticRegression; Géron Ch.4 coefficient interpretation*
- [ ] Mini Exercise: Fit logistic regression on toy data, inspect and plot coefficients
- [ ] Project: Build the RFM feature table (recency, frequency, monetary, tenure) + baseline logistic regression churn model

**D261 (Wed)**
- [ ] Theory: Evaluation pitfalls — the accuracy trap, confusion matrix, precision/recall — *ML Zoomcamp Module 4 — Evaluation Metrics; scikit-learn docs "Model evaluation"*
- [ ] Mini Exercise: Compute a confusion matrix and precision/recall by hand on a small prediction set, verify against `sklearn`
- [ ] Project: Evaluate the churn model with confusion matrix + precision/recall; document why accuracy is misleading here

**D262 (Thu)**
- [ ] Theory: ROC/AUC, k-fold cross-validation — *ML Zoomcamp Module 4 — ROC/AUC; scikit-learn docs "Cross-validation"*
- [ ] Mini Exercise: Plot an ROC curve for a toy classifier, compute AUC manually vs. `sklearn`
- [ ] Project: Add k-fold CV to churn-model training, report mean/std AUC across folds

**D263 (Fri)**
- [ ] Theory: Class imbalance handling — *ML Zoomcamp Module 4 imbalance notes; scikit-learn docs `class_weight` parameter*
- [ ] Mini Exercise: Compare `class_weight='balanced'` vs. undersampling on a toy imbalanced dataset
- [ ] Project: Apply class-weight balancing to the churn model, re-evaluate precision/recall/AUC, pick the Week-44 final model

**D264 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the manual confusion-matrix calculation from memory
- [ ] Project: Re-read the Week-44 model comparison notes for anything you'd argue differently now

### Week 45 — Deployment, Trees, Churn Predictor Dockerized + Ensembles

**D265 (Mon)**
- [ ] Theory: Deployment patterns recap — Flask/FastAPI + Docker for model serving — *Flask docs "Quickstart"; FastAPI docs (recap)*
- [ ] Mini Exercise: Minimal FastAPI `/predict` endpoint serving a pickled sklearn model, hit it with curl
- [ ] Project: Wrap the Week-44 churn model in a FastAPI scoring service (`/predict` with a Pydantic request/response schema)

**D266 (Tue)**
- [ ] Theory: Containerizing the model service — *Docker docs "Best practices for writing Dockerfiles" (model-artifact angle)*
- [ ] Mini Exercise: Write a multi-stage Dockerfile for the scoring service, check the resulting image size
- [ ] Project: docker-compose for the churn scoring service, with a `/health` endpoint

**D267 (Wed)**
- [ ] Theory: Decision trees — *ML Zoomcamp Module 6 — Decision Trees; Géron Ch.6*
- [ ] Mini Exercise: Fit a `DecisionTreeClassifier` on toy data, visualize it, discuss overfitting via `max_depth`
- [ ] Project: Rebuild the churn model as a decision tree; compare AUC/precision-recall against Week 44's logistic regression on the same held-out fold

**D268 (Thu)**
- [ ] Theory: Random forests / ensembling (bagging) — *ML Zoomcamp Module 6 — Random Forest; Géron Ch.7*
- [ ] Mini Exercise: Bagging demo: train 10 trees on bootstrap samples, average predictions, compare variance to a single tree
- [ ] Project: Build a `RandomForestClassifier` churn model, tune `n_estimators`/`max_depth` via CV

**D269 (Fri)**
- [ ] Theory: Gradient boosting (XGBoost) — *XGBoost docs "Introduction to Boosted Trees"; ML Zoomcamp Module 6 — XGBoost*
- [ ] Mini Exercise: Fit an `XGBClassifier` on toy data, plot feature importances
- [ ] Project: Build an XGBoost churn model; final comparison table (logreg vs. tree vs. forest vs. XGBoost); wire the winner into the scoring service

**D270 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the bagging demo from memory, explain variance reduction out loud
- [ ] Project: Re-read the model comparison table and confirm the winner is justified, not just the last one tried

### Week 46 — Deep Learning, CarePoint Document-Image Classifier

**D271 (Mon)**
- [ ] Theory: Neural network basics — layers, activations, backprop intuition — *ML Zoomcamp "Neural Networks & Deep Learning" module; Géron Ch.10*
- [ ] Mini Exercise: Forward-pass-only tiny dense net in NumPy on toy data
- [ ] Project: Assemble a labeled CarePoint scanned-document dataset (referral letter, insurance card, lab result, prescription) + data-loading pipeline

**D272 (Tue)**
- [ ] Theory: CNNs — convolution, pooling — *ML Zoomcamp CNN section; Géron Ch.14*
- [ ] Mini Exercise: Build a tiny CNN in Keras on a toy image dataset, train a few epochs
- [ ] Project: Define and train a baseline CNN for CarePoint document-type classification, log accuracy

**D273 (Wed)**
- [ ] Theory: Transfer learning — *Keras docs "Transfer learning & fine-tuning"; ML Zoomcamp transfer-learning section*
- [ ] Mini Exercise: Load a pretrained model via `keras.applications`, freeze the base, fine-tune the head on toy data
- [ ] Project: Replace the baseline CNN with a pretrained-base + custom-head model for the document classifier, compare accuracy to Tuesday's baseline

**D274 (Thu)**
- [ ] Theory: Keras training-loop internals — callbacks, checkpoints — *Keras docs "Training & evaluation with the built-in methods"; "Writing your own callbacks"*
- [ ] Mini Exercise: Add `EarlyStopping` + `ModelCheckpoint` to a toy training loop
- [ ] Project: Add early stopping and best-model checkpointing to the document classifier's training run, retrain

**D275 (Fri)**
- [ ] Theory: Regularization/dropout for deep nets — *Géron Ch.11 regularization section; Keras docs on image augmentation*
- [ ] Mini Exercise: Add `Dropout` layers to the toy CNN, compare the train/val gap with vs. without
- [ ] Project: Add dropout + data augmentation to the document classifier, final model selection, evaluate on a held-out test set, write a short model card

**D276 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the transfer-learning freeze/fine-tune setup from memory
- [ ] Project: Re-read the model card and confirm the stated limitations are actually true

### Week 47 — Serverless, Kubernetes, KServe — Three-Way Deployment

**D277 (Mon)**
- [ ] Theory: AWS Lambda / serverless model serving concepts — *AWS Lambda docs "Building Lambda functions with Python"; ML Zoomcamp Module 8 — Serverless*
- [ ] Mini Exercise: Package a tiny sklearn model + Lambda handler locally, invoke it
- [ ] Project: Convert the churn model to a Lambda-compatible handler (model loaded once outside the handler, cold-start aware)

**D278 (Tue)**
- [ ] Theory: Lightweight-inference packaging, cold-start tradeoffs — *AWS Lambda docs "Container images"; ML Zoomcamp Module 8*
- [ ] Mini Exercise: Measure cold-start latency of the local handler across a few repeated invokes
- [ ] Project: Package the model as a Lambda container image, deploy locally (SAM/LocalStack), measure invoke latency

**D279 (Wed)**
- [ ] Theory: Kubernetes deployment of a model service (reusing Phase 5's `kind` cluster) — *Kubernetes docs "Deployments" + "Services" (recap)*
- [ ] Mini Exercise: —
- [ ] Project: Write Deployment + Service YAML for the FastAPI scoring service (Week 45's image), deploy to the local `kind` cluster

**D280 (Thu)**
- [ ] Theory: Scaling the K8s model service — HPA, readiness/liveness probes for ML pods — *Kubernetes docs "HorizontalPodAutoscaler Walkthrough"; "Configure Liveness, Readiness and Startup Probes"*
- [ ] Mini Exercise: —
- [ ] Project: Add readiness/liveness probes tuned to model load time, add an HPA based on CPU, lightly load-test to confirm scale-out

**D281 (Fri)**
- [ ] Theory: KServe model serving on Kubernetes — *KServe docs "Getting Started" / `InferenceService` concept guide*
- [ ] Mini Exercise: —
- [ ] Project: Install KServe on the `kind` cluster, deploy the model as an `InferenceService`, hit its predict endpoint; write `docs/serving-comparison.md` (Lambda vs. raw K8s Deployment vs. KServe: cold start, ops overhead, autoscaling, cost story)

**D282 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Explain the Lambda-vs-K8s-vs-KServe tradeoffs out loud, unscripted
- [ ] Project: Re-read `docs/serving-comparison.md` for anything you'd argue differently now

### Week 48 — Project 1 Finalize — StockPilot Demand Forecaster

**D283 (Mon)**
- [ ] Theory: Revisit and polish EDA + feature set — *Géron Ch.2 "Fine-Tune Your Model" (recap); ML Zoomcamp Regression module (recap)*
- [ ] Mini Exercise: —
- [ ] Project: Re-run EDA with fresh eyes; prune/expand features (rolling averages, promotions flag); document data assumptions in the README

**D284 (Tue)**
- [ ] Theory: Final model selection (linear/Ridge vs. tree-based regressor) — *scikit-learn docs "Choosing the right estimator"; XGBoost docs regression-objective section*
- [ ] Mini Exercise: —
- [ ] Project: Train/compare 3-4 candidate regressors with consistent CV; pick the winner by RMSE plus a stated business rationale (interpretability vs. accuracy for a small shop owner)

**D285 (Wed)**
- [ ] Theory: Deployment — *FastAPI docs (recap); Docker docs (recap)*
- [ ] Mini Exercise: —
- [ ] Project: Wrap the final demand model in the same FastAPI-scoring-service pattern from Week 45, dockerize, wire an integration point into StockPilot's `/products/{id}/forecast`

**D286 (Thu)**
- [ ] Theory: README + model card — *Model-card guidance (Google Model Cards overview); scikit-learn docs "Model persistence"*
- [ ] Mini Exercise: —
- [ ] Project: Write `README.md` (setup/run) and `docs/model-card.md` (training data, features, metric, known limitations, intended use)

**D287 (Fri)**
- [ ] Theory: Retrospective + improvements write-up
- [ ] Mini Exercise: —
- [ ] Project: Write `docs/postmortem-demand-forecaster.md` (more history, holiday effects, hierarchical forecasting, MLflow foreshadowing Phase 10); tag `v0.1-demand-forecaster`

**D288 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Explain the full demand-forecaster pipeline end to end, out loud, unscripted
- [ ] Project: Re-read the postmortem and confirm every "deferred" item is genuinely deferred, not silently done

### Week 49 — Project 2 Finalize + Project 3 — Churn Predictor & CarePoint No-Show Predictor

**D289 (Mon)**
- [ ] Theory: Formalize the churn predictor's training pipeline — *scikit-learn docs "Pipeline and FeatureUnion" (recap); XGBoost docs "Python Package Introduction"*
- [ ] Mini Exercise: —
- [ ] Project: Refactor Weeks 44-45's churn work into a clean `training.py` (sklearn `Pipeline`: preprocessing + model) + a `predict_service` package; re-save the winning XGBoost model

**D290 (Tue)**
- [ ] Theory: Testing + CI for the churn predictor — *pytest docs (recap); GitHub Actions docs (recap, ML-artifact caching angle)*
- [ ] Mini Exercise: —
- [ ] Project: Add unit tests (feature engineering, evaluation metrics) + a CI workflow that retrains on a sample and asserts AUC clears a threshold ("model regression test")

**D291 (Wed)**
- [ ] Theory: Documentation + ship
- [ ] Mini Exercise: —
- [ ] Project: README + model card for the churn predictor; finalize the Week-45 Dockerized scoring service; tag `v0.1-churn-predictor`

**D292 (Thu)**
- [ ] Theory: CarePoint No-Show Predictor — EDA + baseline — *ML Zoomcamp Classification + Trees modules (recap); Géron Ch.6/7 (recap)*
- [ ] Mini Exercise: —
- [ ] Project: EDA on CarePoint appointment data; define the no-show label; engineer features (lead time, prior no-show rate, day-of-week, reminder-sent flag); baseline logistic regression + decision tree comparison

**D293 (Fri)**
- [ ] Theory: No-Show Predictor — final model + deployment — *XGBoost docs (recap)*
- [ ] Mini Exercise: —
- [ ] Project: Train an XGBoost no-show model (class-weight balanced); evaluate with a recall-weighted metric; wrap in a FastAPI scoring service, dockerize, README + model card; tag `v0.1-noshow-predictor`

**D294 (Sat)**
- [ ] Theory: **Phase-wide review**
- [ ] Mini Exercise: Explain, unscripted, why each of the three projects picked the metric it picked
- [ ] Project: `docs/postmortem-phase9.md` — full phase retrospective across all 3 projects and all 3 serving methods; tag `v0.9-phase9`

---

## Phase 10 — MLOps Engineering Zoomcamp (Weeks 50-55)

### Week 50 — MLflow Tracking, Demand Forecaster Instrumentation

**D295 (Mon)**
- [ ] Theory: MLOps maturity levels & why MLOps — *Google Cloud Architecture Center — "MLOps: CD & automation pipelines in ML" §maturity levels*
- [ ] Mini Exercise: Score your Phase-9 training scripts against the 3 maturity levels (manual → automated pipeline → CI/CD)
- [ ] Project: New module `mlops/demand-forecaster/`, copy in the Phase-9 training script as-is

**D296 (Tue)**
- [ ] Theory: Reproducible environments: Poetry, Makefiles — *Poetry docs "Basic usage"*
- [ ] Mini Exercise: Convert a scratch `requirements.txt` to a pinned `pyproject.toml` with Poetry
- [ ] Project: Add `pyproject.toml` (poetry) + `Makefile` (`make install`, `make train`, `make test`) to the demand-forecaster module

**D297 (Wed)**
- [ ] Theory: MLflow tracking basics: runs, params, metrics, artifacts — *MLflow docs — Tracking Quickstart*
- [ ] Mini Exercise: Instrument a toy `LinearRegression` script with `mlflow.start_run()`, log 2 params + 1 metric + the model artifact
- [ ] Project: Wrap the real training script: log hyperparams, MAE/RMSE/MAPE, and artifacts (model, feature list) on every run

**D298 (Thu)**
- [ ] Theory: MLflow Model Registry: versioning & staging — *MLflow docs — Model Registry guide*
- [ ] Mini Exercise: Register the toy model, transition it None → Staging → Production via the API
- [ ] Project: Register `stockpilot-demand-forecaster`, transition the current best run's model to `Staging`

**D299 (Fri)**
- [ ] Theory: Comparing many hyperparameter runs — *Huyen, *Designing ML Systems* Ch.6 (Model Development & Offline Evaluation)*
- [ ] Mini Exercise: Run a 5-point grid search on the toy model, compare runs in the MLflow UI (parallel-coordinates view)
- [ ] Project: Sweep ~12 demand-forecaster hyperparam combos (XGBoost `max_depth`/`n_estimators`/`learning_rate`), promote the lowest-RMSE run's version to `Production`, archive the rest

**D300 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the toy MLflow instrumentation from memory, no notes
- [ ] Project: Re-read the registered model's run params, verify you can explain every choice made this week

### Week 51 — Orchestration, Churn Predictor Scheduled Flow

**D301 (Mon)**
- [ ] Theory: Workflow orchestration concepts, DAGs — *Prefect docs — "Why Prefect?" + Flows concepts*
- [ ] Mini Exercise: Write a 3-task toy Prefect flow (`extract → transform → load` on fake data), run it locally
- [ ] Project: Sketch the churn-predictor DAG (`ingest → train → evaluate → register`) in `docs/`, scaffold `flows/churn_training_flow.py` with empty `@task` stubs

**D302 (Tue)**
- [ ] Theory: Building a training pipeline as a DAG — *Prefect docs — Flows & Tasks*
- [ ] Mini Exercise: Add a retry to the toy flow's `transform` task
- [ ] Project: Implement each task body: `ingest_transactions`, `build_rfm_features`, `train_model`, `evaluate_model`, `register_if_better`, wire them into the flow

**D303 (Wed)**
- [ ] Theory: Scheduling, retries, parameterized runs — *Prefect docs — Schedules + Retries*
- [ ] Mini Exercise: Add `retries=3, retry_delay_seconds=30` to a toy task that fails twice then succeeds, watch it recover
- [ ] Project: Add a daily schedule to the churn flow, retry policy on `ingest_transactions` (simulated flaky DB read), parameterize by `training_window_days`

**D304 (Thu)**
- [ ] Theory: Triggering deployment on new model registration — *MLflow docs — Registry stage transitions + Prefect docs on task composition*
- [ ] Mini Exercise: Write a toy task that polls the registry for the latest `Production` version, prints "would deploy" only if it changed
- [ ] Project: Add a `maybe_deploy` task at the end of the churn flow: if `register_if_better` promoted a new `Production` version, trigger a stub redeploy task (real deploy logic lands Week 52)

**D305 (Fri)**
- [ ] Theory: Observability of pipeline runs — *Prefect docs — UI, states & logging*
- [ ] Mini Exercise: —
- [ ] Project: Wire structured logging (reuse `structlog` from Phase 1) inside each task, verify flow-run states/logs are visible end-to-end in the Prefect UI

**D306 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the toy retry-and-recover flow from memory
- [ ] Project: Re-trace the full churn DAG on paper without opening the code

### Week 52 — Deployment Patterns, No-Show Predictor Dual Deploy

**D307 (Mon)**
- [ ] Theory: Deployment patterns: batch / web service / streaming — *Huyen Ch.7 (Model Deployment & Prediction Service) §batch vs. online*
- [ ] Mini Exercise: Write comparison notes: latency/cost/complexity for batch vs. web vs. streaming on a toy example
- [ ] Project: Write `docs/deployment-decision.md` first draft for no-show-predictor: CarePoint's actual need (nightly list vs. booking-time prediction), decide to build both this week to compare directly

**D308 (Tue)**
- [ ] Theory: Batch scoring job design — *MLflow docs — "Deploy MLflow Models" (pyfunc, batch)*
- [ ] Mini Exercise: Load a registered MLflow model in a toy script, score a 100-row CSV, write predictions to a new CSV
- [ ] Project: Build `batch_score.py`: loads the Production model from the registry, scores tomorrow's appointments, writes `no_show_risk` back into CarePoint

**D309 (Wed)**
- [ ] Theory: Web service deployment: FastAPI + Docker — *FastAPI docs (reused from Phase 1) + MLflow docs pyfunc serving*
- [ ] Mini Exercise: —
- [ ] Project: `POST /predict/no-show-risk` FastAPI endpoint loading the same Production model, Dockerfile, added to CarePoint's compose

**D310 (Thu)**
- [ ] Theory: Streaming deployment concept (Kafka consumer) — *Huyen Ch.7 §streaming; Phase-3 Kafka notes (reused)*
- [ ] Mini Exercise: Sketch (don't wire up) a toy Kafka consumer that would score each `appointment.created` event as it arrives
- [ ] Project: Write `docs/streaming-option.md` + a stubbed `score_appointment_event(event) -> float`; note why a Kafka-consumer deployment isn't adopted this week

**D311 (Fri)**
- [ ] Theory: Choosing the right pattern for a given SLA — *Huyen Ch.7 §choosing a deployment pattern*
- [ ] Mini Exercise: —
- [ ] Project: Finish `docs/deployment-decision.md`: side-by-side batch vs. web-service table (staleness, infra cost, latency, failure mode) with a concrete recommendation — web service as the source of truth at booking time, batch as the staff's daily overview

**D312 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the batch-scoring toy script from memory
- [ ] Project: Re-read the finished decision doc, argue the opposite recommendation out loud, then explain why you didn't pick it

### Week 53 — Monitoring + Best Practices, Demand Forecaster Drift + CI Gate

**D313 (Mon)**
- [ ] Theory: ML monitoring concepts: data drift, target drift, model decay — *Huyen Ch.8 (Data Distribution Shifts & Monitoring)*
- [ ] Mini Exercise: Compute a toy PSI (population stability index) between two synthetic distributions
- [ ] Project: Write `docs/monitoring-plan.md` for demand-forecaster: drift-risk features (seasonality, price changes), what "decay" looks like (RMSE creeping up week over week)

**D314 (Tue)**
- [ ] Theory: Building a drift dashboard with Evidently — *Evidently AI docs — Get Started + Data Drift report*
- [ ] Mini Exercise: Run Evidently's `DataDriftPreset` on two toy dataframes (reference vs. current), view the HTML report
- [ ] Project: Generate an Evidently drift report comparing demand-forecaster's training reference data vs. last week's live order data; export key metrics as Prometheus-scrapable numbers (reuse Phase 4 Prometheus client)

**D315 (Wed)**
- [ ] Theory: Testing ML code: feature-transform unit tests, data validation — *Huyen Ch.5 (Feature Engineering) §validation; pytest docs (reused)*
- [ ] Mini Exercise: Write a unit test that catches a broken feature transform (a lag feature shifted by the wrong number of periods)
- [ ] Project: Add unit tests for every feature-engineering function in demand-forecaster (lag features, rolling means, categorical encodings) + a pre-training data-validation check

**D316 (Thu)**
- [ ] Theory: CI/CD for ML: model-quality gates in GitHub Actions — *GitHub Actions docs (reused, Phase 4) + MLflow docs on comparing run metrics*
- [ ] Mini Exercise: —
- [ ] Project: Add a GitHub Actions job that retrains demand-forecaster on a fixed CI dataset sample, compares new RMSE to the current Production model's logged RMSE, fails if it regresses beyond tolerance

**D317 (Fri)**
- [ ] Theory: IaC intro for ML infra: Terraform — *Terraform docs — Get Started (Docker provider tutorial)*
- [ ] Mini Exercise: Write a minimal Terraform file provisioning one local Docker container (the MLflow tracking server) via the `docker` provider; `plan`/`apply`/`destroy` it
- [ ] Project: Write (don't necessarily apply to real cloud) a Terraform stub describing the MLflow tracking server + Postgres backend as resources — deliberately shallow, real cloud provisioning explicitly deferred to Phase 11

**D318 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the toy Evidently drift-report run from memory
- [ ] Project: Re-read the CI-gate workflow file, explain every step out loud without looking

### Week 54 — Project 1 — Demand Forecaster, Fully Productionized

**D319 (Mon)**
- [ ] Theory: Consolidating tracking + orchestration for Project 1 — *MLflow docs — MLproject packaging; Prefect docs — Deployments*
- [ ] Mini Exercise: —
- [ ] Project: Build the full `ingest → train → evaluate → register` Prefect flow for demand-forecaster (mirrors Week 51's churn-flow pattern), wire it to the existing MLflow tracking/registry from Week 50

**D320 (Tue)**
- [ ] Theory: Consolidating deployment (batch + web service) for Project 1 — *— (apply Week 52 patterns)*
- [ ] Mini Exercise: —
- [ ] Project: Add both the nightly batch scoring job and the FastAPI web-service endpoint for demand-forecaster (mirrors CarePoint's dual deployment), Dockerized, added to StockPilot's compose

**D321 (Wed)**
- [ ] Theory: Consolidating monitoring + CI gate for Project 1 — *— (apply Week 53 patterns)*
- [ ] Mini Exercise: —
- [ ] Project: Wire the Evidently drift report + Prometheus export + Grafana dashboard permanently into this module; finalize the CI RMSE-regression gate as a required check on `main`

**D322 (Thu)**
- [ ] Theory: Hardening: retries, alerting, failure modes — *Prefect docs — Automations / state-change hooks*
- [ ] Mini Exercise: —
- [ ] Project: Add a Prefect notification/state-change hook that alerts (log line or webhook stub) when the training flow fails, or when a retrain is auto-rejected by the quality gate

**D323 (Fri)**
- [ ] Theory: Polish: README, architecture diagram, tagged release
- [ ] Mini Exercise: —
- [ ] Project: Write the module's `README.md` (architecture diagram, how to run tracking/orchestration/deployment/monitoring locally), tag `v0.1-mlops-demand-forecaster`

**D324 (Sat)**
- [ ] Theory: **Review / Project 1 retrospective**
- [ ] Mini Exercise: Explain the full tracking → orchestration → deployment → monitoring pipeline out loud, unscripted
- [ ] Project: Write `docs/retrospective-project1.md`: what took longer than expected, what you'd change to build Projects 2 and 3 faster

### Week 55 — Project 2 — Churn Predictor, Project 3 — No-Show Predictor, Phase Wrap

**D325 (Mon)**
- [ ] Theory: Project 2 — Churn Predictor: tracking + registry — *— (apply Week 50 patterns)*
- [ ] Mini Exercise: —
- [ ] Project: Instrument churn-predictor training with MLflow tracking + registry (reuse Week 50's code as a template), register the best model

**D326 (Tue)**
- [ ] Theory: Project 2 — Churn Predictor: deployment + monitoring — *— (apply Weeks 51–53 patterns)*
- [ ] Mini Exercise: —
- [ ] Project: Deploy churn-predictor as a FastAPI web service (orchestration flow already exists from Week 51), add the drift-monitoring dashboard (Evidently + Grafana, reusing Week 53's pattern)

**D327 (Wed)**
- [ ] Theory: Project 2 — Churn Predictor: CI gate, polish, tag — *— (apply Week 53's CI-gate pattern)*
- [ ] Mini Exercise: —
- [ ] Project: Add the model-quality CI gate, write the README, tag `v0.1-mlops-churn-predictor`

**D328 (Thu)**
- [ ] Theory: Project 3 — No-Show Predictor: tracking + orchestration — *— (apply Weeks 50–51 patterns)*
- [ ] Mini Exercise: —
- [ ] Project: Add MLflow tracking/registry **and** a Prefect training flow to no-show-predictor in one sitting (deployment already exists from Week 52)

**D329 (Fri)**
- [ ] Theory: Project 3 — No-Show Predictor: monitoring, CI gate, polish, tag — *— (apply Weeks 52–53 patterns)*
- [ ] Mini Exercise: —
- [ ] Project: Add the drift dashboard + CI quality gate (reuse Week 53's pattern), write the README, tag `v0.1-mlops-no-show-predictor`

**D330 (Sat)**
- [ ] Theory: **Phase 10 wrap review**
- [ ] Mini Exercise: Explain, unscripted, the full tracking → orchestration → deployment → monitoring pipeline for all 3 models back to back
- [ ] Project: Write `docs/postmortem-phase10.md` (what's deferred: full IaC/Terraform, Kubernetes-based serving, feature stores, A/B testing infra), tag `v0.10-phase10`

---

## Phase 11 — Data Engineering Zoomcamp (Weeks 56-61)

### Week 56 — Docker & Terraform, Warehouse Provisioning

**D331 (Mon)**
- [ ] Theory: IaC concepts, Terraform basics: providers, resources, HCL — *Terraform docs "What is Terraform" + "Configuration Language"*
- [ ] Mini Exercise: Throwaway `.tf` file provisioning a local `null_resource`, run plan/apply/destroy
- [ ] Project: Init `year2-analytics-platform/` repo, `terraform/` scaffold, document local-state backend decision

**D332 (Tue)**
- [ ] Theory: Terraform state + providers deep dive; provisioning a warehouse dataset — *Terraform docs "State" + Google provider `bigquery_dataset` resource*
- [ ] Mini Exercise: `plan`/`apply`/`destroy` a real dataset twice, read the state file by hand once
- [ ] Project: `main.tf` provisioning `raw` + `staging` BigQuery datasets

**D333 (Wed)**
- [ ] Theory: Containerizing data pipelines (reusing Phase 1 Docker skills) — *Docker Compose docs (recap)*
- [ ] Mini Exercise: Dockerfile for a tiny Python script reading Postgres, writing a CSV
- [ ] Project: `docker-compose.yml` scaffold: local Postgres mirror + placeholder Airflow service

**D334 (Thu)**
- [ ] Theory: Local vs cloud dev environment parity — *Terraform docs workspaces/environments pattern*
- [ ] Mini Exercise: Config loader switching between a local Postgres "fake warehouse" and real BigQuery via one env flag
- [ ] Project: `warehouse_client.py` abstraction so later pipeline code is warehouse-agnostic

**D335 (Fri)**
- [ ] Theory: Provisioning the real cloud warehouse end-to-end + least-privilege IAM — *Terraform docs `google_service_account` + dataset IAM binding*
- [ ] Mini Exercise: `terraform validate` + apply against a real GCP sandbox project
- [ ] Project: Finalize `raw`/`staging`/`marts` datasets + one dataset-scoped service account; write `docs/architecture.md`

**D336 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo Tuesday's dataset provisioning from memory, no notes
- [ ] Project: Re-read `docs/architecture.md` for anything under-specified

### Week 57 — Workflow Orchestration (Airflow)

**D337 (Mon)**
- [ ] Theory: Orchestration concepts: DAGs, operators, scheduler — *Airflow docs "Core Concepts: DAGs"*
- [ ] Mini Exercise: Hello-world DAG, 2 `PythonOperator` tasks with a dependency
- [ ] Project: Bring up local Airflow via Docker Compose (webserver+scheduler+metadata DB)

**D338 (Tue)**
- [ ] Theory: Extract step: incremental pulls via an `updated_at` watermark — *Airflow docs "Connections & Hooks" (`PostgresHook`)*
- [ ] Mini Exercise: Script pulling rows from StockPilot's `orders` where `updated_at > last_watermark`
- [ ] Project: `extract_load_stockpilot.py`: extract task landing StockPilot into `raw`

**D339 (Wed)**
- [ ] Theory: Load step: landing raw data into staging — *BigQuery docs "Loading data"*
- [ ] Mini Exercise: Load a CSV into a staging table via the BigQuery Python client
- [ ] Project: Complete StockPilot's load task into `staging`; add QuickServe's extract task

**D340 (Thu)**
- [ ] Theory: Idempotent, retriable pipeline design (MERGE vs INSERT) — *BigQuery docs "MERGE statement"*
- [ ] Mini Exercise: Rerun the same DAG run twice, assert no duplicate rows land
- [ ] Project: Convert QuickServe + PeopleOps loads to idempotent `MERGE`-based upserts

**D341 (Fri)**
- [ ] Theory: Backfills, `schedule_interval`, catchup — *Airflow docs "DAG Runs" + backfill command reference*
- [ ] Mini Exercise: Backfill a toy DAG over a 7-day historical window
- [ ] Project: Finalize `@daily` schedules for all 3 DAGs; run one real historical backfill

**D342 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the MERGE-upsert idempotency test from memory
- [ ] Project: Trace one row from StockPilot Postgres through to `staging` by hand

### Week 58 — Data Warehouse + Analytics Engineering (dbt)

**D343 (Mon)**
- [ ] Theory: Warehouse fundamentals: columnar storage, partitioning, clustering — *BigQuery docs "Partitioned tables"*
- [ ] Mini Exercise: Create a date-partitioned+clustered table, compare bytes-scanned with/without a partition filter
- [ ] Project: Apply date-partitioning + clustering to `stg_orders`, `stg_stock_movements`

**D344 (Tue)**
- [ ] Theory: Query optimization on a columnar warehouse vs Postgres tuning — *BigQuery docs "Query optimization best practices"*
- [ ] Mini Exercise: Rewrite a `SELECT *` into a column-pruned query, compare bytes-scanned estimates
- [ ] Project: Audit and fix 3 wasteful queries in the Week 57 load tasks

**D345 (Wed)**
- [ ] Theory: dbt fundamentals: models, sources, tests — *dbt docs "Build your first models"*
- [ ] Mini Exercise: `dbt init`, one source + one staging model + one `not_null`/`unique` test
- [ ] Project: `dbt/` project scaffold, `sources.yml` pointing at `raw`/`staging`

**D346 (Thu)**
- [ ] Theory: Staging → intermediate → marts layering — *dbt docs "How we structure our dbt projects"*
- [ ] Mini Exercise: Build one intermediate model joining 2 staging models
- [ ] Project: `stg_stockpilot__orders`, `stg_quickserve__sales`, `stg_peopleops__leave_requests`, `int_orders_enriched`

**D347 (Fri)**
- [ ] Theory: dbt tests + docs, lineage graph — *dbt docs "Testing" + "Documentation"*
- [ ] Mini Exercise: Add one singular test, run `dbt docs generate`, browse the lineage graph
- [ ] Project: Build `marts`: `fct_orders`, `dim_products`, `fct_leave_requests` with schema tests

**D348 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo Wednesday's `dbt init` from memory
- [ ] Project: Re-read the lineage graph for anything mis-joined

### Week 59 — Data Platforms + Batch Processing (Spark)

**D349 (Mon)**
- [ ] Theory: Lakehouse concepts / data platform architecture (bronze/silver/gold) — *Databricks "What is a data lakehouse" overview*
- [ ] Mini Exercise: Map this platform's raw/staging/marts onto bronze/silver/gold in one paragraph
- [ ] Project: Update `docs/architecture.md` with the lakehouse-terms mapping

**D350 (Tue)**
- [ ] Theory: Spark fundamentals: RDDs vs DataFrames, SparkSession — *Spark docs "RDD Programming Guide" + "SQL, DataFrames and Datasets Guide"*
- [ ] Mini Exercise: Local PySpark script: read a CSV, `groupBy().agg()`, `.show()`
- [ ] Project: `spark/` scaffold; PySpark job skeleton reading from BigQuery via the Spark-BigQuery connector

**D351 (Wed)**
- [ ] Theory: Batch aggregation: yearly stock-movement/order analytics — *Spark docs "DataFrame aggregation functions"*
- [ ] Mini Exercise: Aggregate a synthetic multi-million-row CSV by month+product, time it
- [ ] Project: `yearly_stock_movement_agg.py`: joins StockPilot stock movements + QuickServe sales for the full year, writes to a `marts` table

**D352 (Thu)**
- [ ] Theory: Spark joins & performance tuning: broadcast join, shuffle — *Spark docs "Performance Tuning"*
- [ ] Mini Exercise: Compare a shuffle join vs a broadcast join on skewed synthetic data via `.explain()`
- [ ] Project: Tune the yearly aggregation job: broadcast `dim_products`, repartition on `product_id`

**D353 (Fri)**
- [ ] Theory: Choosing warehouse-SQL vs Spark for a given batch job
- [ ] Mini Exercise: —
- [ ] Project: `docs/spark-vs-warehouse-sql.md`; re-implement one small job as a plain dbt SQL model for comparison

**D354 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the broadcast-join tuning from memory
- [ ] Project: Re-read `docs/spark-vs-warehouse-sql.md` for a decision you'd now make differently

### Week 60 — Streaming

**D355 (Mon)**
- [ ] Theory: Streaming concepts recap, bridging Phase 3's Kafka — *Kafka docs "Introduction" (recap) + ksqlDB docs "Overview"*
- [ ] Mini Exercise: Stand up local Kafka (Phase 3 compose), produce/consume 10 test messages
- [ ] Project: Add a Kafka broker service back into this repo's compose, pointed at FleetTrack's existing topic

**D356 (Tue)**
- [ ] Theory: Kafka Streams / ksqlDB for real-time aggregation — *ksqlDB docs "Create a Stream" + "Aggregate Streaming Data"*
- [ ] Mini Exercise: A ksqlDB stream + rolling `GROUP BY` count on a toy topic
- [ ] Project: `deliveries_stream.sql`: ksqlDB stream over FleetTrack's `delivery_events` topic

**D357 (Wed)**
- [ ] Theory: Streaming FleetTrack's events into the warehouse — *BigQuery docs "Streaming data" (insert API)*
- [ ] Mini Exercise: Minimal consumer inserting one row per event via the streaming-insert API
- [ ] Project: `streaming/consumer.py` consuming `delivery_events`, upserting into `deliveries_in_progress`

**D358 (Thu)**
- [ ] Theory: Exactly-once vs at-least-once semantics — *Kafka docs "Message Delivery Semantics"*
- [ ] Mini Exercise: Reprocess the same message twice, observe the duplicate, then fix it
- [ ] Project: Make the consumer idempotent: `MERGE` keyed on `delivery_id` + `event_type`

**D359 (Fri)**
- [ ] Theory: Real-time dashboard on streamed data (Grafana, Phase 4 stack) — *Grafana docs "Add a data source"*
- [ ] Mini Exercise: Point Grafana at the warehouse table, one panel: live in-progress count
- [ ] Project: `dashboards/grafana/deliveries-in-progress.json`, panel refreshing every 10s

**D360 (Sat)**
- [ ] Theory: **Review**
- [ ] Mini Exercise: Redo the idempotent-upsert fix from memory
- [ ] Project: Re-watch the dashboard while manually firing a few test events

### Week 61 — Project 1 + Project 2 + Project 3, Full Program Wrap

**D361 (Mon)**
- [ ] Theory: Project 1 integration: run the full batch pipeline top to bottom for the first time — *dbt docs "dbt run" / orchestrating dbt (recap)*
- [ ] Mini Exercise: —
- [ ] Project: `terraform apply` → trigger all 4 Airflow DAGs → `dbt run && dbt test`; record total run time

**D362 (Tue)**
- [ ] Theory: Project 1: unified BI-style dashboard (StockPilot+QuickServe+PeopleOps+LedgerBase) — *Grafana docs "Panels" (recap)*
- [ ] Mini Exercise: —
- [ ] Project: Build the unified dashboard: revenue, inventory value, headcount/leave, ledger balance, all from `marts`

**D363 (Wed)**
- [ ] Theory: Project 1: hardening — remaining dbt tests, docs, milestone tag — *dbt docs "dbt-utils" package (recap)*
- [ ] Mini Exercise: —
- [ ] Project: Add referential-integrity + `accepted_values` tests, `dbt docs generate`, tag `v0.1-year2-analytics-platform`

**D364 (Thu)**
- [ ] Theory: Project 2 (smaller, faster — extends Project 1's infra): land the streaming layer as a first-class part of the platform
- [ ] Mini Exercise: —
- [ ] Project: Fold Week 60's streaming consumer + dashboard panel officially into this repo; finalize its dbt tests/docs; tag `v0.2-plus-streaming`

**D365 (Fri)**
- [ ] Theory: Project 3 (smaller still — extends Project 1's infra): freeform extension — AtlasMarket vendor analytics
- [ ] Mini Exercise: —
- [ ] Project: Extract AtlasMarket vendor/order data, `fct_vendor_revenue` dbt model, one new dashboard panel, tag `v0.3-plus-vendor-analytics`

**D366 (Sat)**
- [ ] Theory: **FULL 12-MONTH PROGRAM WRAP**
- [ ] Mini Exercise: —
- [ ] Project: Write `docs/program-retrospective.md`: a phase-by-phase retrospective across all 11 phases and every project, from StockPilot's first decorator to this platform's last dbt model; tag `v2.0-year-plan-complete`

---

**PROGRAM COMPLETE — 366 days, 61 weeks, 11 phases, 28 projects. Tag `v2.0-year-plan-complete`.**
