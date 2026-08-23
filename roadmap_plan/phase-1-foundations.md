# PHASE 1 — Foundations: Advanced Python + Production FastAPI
### Weeks 1–4 · ~4h weekdays, ~2–3h Saturdays · 24 working days

---

## 1. Learning Goals

By the end of Phase 1 you can:

- Explain and correctly use decorators, generators, context managers,
  dataclasses, descriptors, and Python's typing system (incl. `Protocol`) —
  not just syntax, but *why* each exists and when to reach for it.
- Explain reference counting and the GC generational collector well enough to
  debug a memory leak, and explain the GIL well enough to know when threads
  actually help.
- Structure a FastAPI service as **layered architecture**: API → Service →
  Repository, instead of business logic living in route handlers.
- Design a normalized PostgreSQL schema, add the right indexes, and read an
  `EXPLAIN ANALYZE` plan.
- Recognize and fix the N+1 query problem from first-hand pain, not from a
  rule you memorized.
- Write a real Pytest suite: unit tests with mocking, integration tests
  against a real Postgres via Docker, and fixtures/factories.
- Write one property-based test with Hypothesis and explain, concretely,
  what class of bug it catches that example-based tests structurally miss.
- Containerize a multi-service app with Docker Compose and get it running
  the same way on your machine and in CI.

---

## 2. Technologies Introduced This Phase

Python (decorators, generators, context managers, typing, dataclasses,
descriptors, intro to refcounting/GC/GIL) · FastAPI · SQLAlchemy 2.0 (async) ·
PostgreSQL (normalization, indexes, transactions, N+1) · Alembic migrations ·
Pytest + pytest-asyncio + factory_boy + Hypothesis (property-based testing) ·
Docker + Docker Compose · structlog · GitHub Actions (lint + test only,
deploy comes in Phase 4).

Deliberately **not yet introduced**: Redis, Celery, Django, threading/
multiprocessing in depth, Kubernetes, Kafka/RabbitMQ, CQRS,
monitoring stack. They show up later, at the moment they solve a felt problem.

---

## 3. PROJECT 1 — StockPilot (Single-Store Inventory & Order Management API)

### Business Problem
A small retail shop owner currently tracks stock in a spreadsheet. Stock
counts drift from reality, staff oversell out-of-stock items, there's no
audit trail of who changed what, and the owner has no visibility into order
history or which products are slow-moving. StockPilot digitizes this: staff
manage inventory and process orders through an API (a future frontend or POS
integrates with it), the owner gets accurate stock and basic reporting.

### Requirements

**Functional**
- CRUD for products, categories, suppliers.
- Stock adjustments (receive stock, manual correction) with a reason and
  audit trail — never allow silently overwriting a stock number.
- Create orders that decrement stock atomically; reject if insufficient
  stock; support partial fulfillment status.
- Two roles: `owner` (full access) and `staff` (can process orders and view
  stock, cannot delete products or view revenue reports).
- List/filter/paginate products and orders.
- Basic reporting: current stock value, low-stock list, orders in a date
  range.

**Non-functional**
- Stock decrement on order creation must be safe under concurrent requests
  (two staff selling the last unit at the same time) — this is your first
  real encounter with transactions and row locking.
- p95 latency for product list under 150 requests/sec load (you'll actually
  load-test this in Week 4, lightly, with `hey` or `locust`).
- All destructive actions must be traceable to a user.

### Architecture
Layered, single service, synchronous domain logic on an async I/O stack:

```
Client → FastAPI routers (API layer, request/response only)
       → Service layer (business rules: "can't sell below zero stock")
       → Repository layer (SQLAlchemy queries, no business logic)
       → PostgreSQL
```

Rule enforced all phase: **a router function never talks to SQLAlchemy
directly.** This is the single architectural habit Phase 1 is built to drill.

### ER Diagram (textual)
```
users(id, email, hashed_password, role, created_at)
categories(id, name, parent_id NULL -> categories.id)
suppliers(id, name, contact_email)
products(id, sku UNIQUE, name, category_id -> categories.id,
         supplier_id -> suppliers.id, price_cents, current_stock, reorder_level)
stock_movements(id, product_id -> products.id, delta, reason, created_by -> users.id, created_at)
orders(id, status, created_by -> users.id, created_at)
order_items(id, order_id -> orders.id, product_id -> products.id, qty, unit_price_cents)
```
`current_stock` is a denormalized cache updated only via `stock_movements`
inserts inside a transaction — you'll learn *why* denormalizing this one
field is a deliberate, defensible tradeoff, not laziness.

### Folder Structure
```
stockpilot/
  app/
    api/           # routers, request/response schemas (Pydantic)
    services/      # business logic, orchestrates repositories
    repositories/  # SQLAlchemy queries only
    models/        # SQLAlchemy ORM models
    core/          # config, security (JWT), logging setup
    db/            # session management, base
  alembic/
  tests/
    unit/          # service layer tests, mocked repositories
    integration/   # real Postgres via docker, repository + endpoint tests
    factories.py
  docker-compose.yml
  Dockerfile
  .github/workflows/ci.yml
```

### API Design (core endpoints)
```
POST   /auth/login
GET    /products?category_id=&low_stock=&page=&page_size=
POST   /products
PATCH  /products/{id}
POST   /products/{id}/stock-movements
GET    /orders?status=&from=&to=
POST   /orders
GET    /orders/{id}
PATCH  /orders/{id}/status
GET    /reports/stock-value
GET    /reports/low-stock
```

### Database Design
- Index `products.sku` (unique), `products.category_id`, `orders.created_at`,
  `stock_movements.product_id`.
- Composite index `(status, created_at)` on `orders` once you notice the
  "orders in date range by status" query doing a seq scan — you add this
  *after* seeing it in `EXPLAIN ANALYZE`, not before.

### Authentication & Permissions
JWT access tokens (short-lived), role stored in the token claim, a FastAPI
dependency `require_role("owner")` used on sensitive routes. No refresh
tokens yet — that nuance arrives in Phase 2 alongside OAuth.

### Caching
Explicitly **not implemented in v1**. Noted as a TODO with a comment
explaining exactly which endpoint (`GET /products`) would benefit and why —
this becomes a concrete Phase 2 task once Redis is introduced.

### Background Jobs
None yet. Low-stock "alerts" are computed synchronously on request via
`/reports/low-stock` for now — you will explicitly feel the wrongness of
this (what if the owner wants email alerts, not a page they have to poll?)
right before Celery is introduced in Phase 2.

### Infrastructure
`docker-compose.yml` with `api` + `postgres` services, `.env` for config,
healthcheck on the postgres service so `api` waits for real readiness (not
just "container started").

### CI/CD
GitHub Actions: on every push — `ruff` lint, `mypy` (basic), `pytest` against
a Postgres service container. No deployment step yet (Phase 4).

### Testing Strategy
- Unit tests: service layer with repositories mocked — test the *rule*
  ("reject order if stock insufficient") in isolation.
- Integration tests: spin up real Postgres, hit real repositories, verify
  the stock decrement is correct under a simulated race (two concurrent
  order creations for the last unit — one must fail cleanly).
- `factory_boy` factories for products/orders instead of hand-written
  fixtures everywhere.

### Monitoring
Structured JSON logging via `structlog` on every request (method, path,
status, latency, user_id). No metrics/tracing stack yet — that's Phase 4.

### Deployment
Single VPS or Render/Railway, `docker compose up -d`. Manual for now;
zero-downtime deploy technique is a Phase 4 topic. Real cloud
infrastructure (IAM, VPC, a managed database) is a deliberately later
topic too — named here as a gap, closed for real in Phase 6 once
AtlasMarket is a system worth deploying properly.

### Scaling Strategy (discussion, not implementation)
Written notes on: what breaks first under load (single Postgres instance,
no caching, no connection pool tuning), and what you'd do about it —
this becomes the seed of your system-design interview answers later.

### Common Interview Questions (this project should let you answer)
1. How would you prevent overselling the last unit of stock under concurrent
   requests?
2. Why is `current_stock` denormalized here — what's the tradeoff?
3. Walk me through your layered architecture and why the router never
   touches the ORM directly.
4. How would you paginate `/products` for 500k rows efficiently?
5. What does your JWT contain and why is the access token short-lived?
6. Where's the N+1 risk in `/orders/{id}` (order + its items + each item's
   product) and how did you avoid it?
7. How do you test a race condition deterministically?
8. What's your rollback strategy if a migration fails mid-deploy?

### Possible Improvements (backlog you'll consciously defer)
Redis cache on product list, Celery for low-stock email alerts, refresh
tokens, soft-deletes with audit history, webhook on order status change,
multi-currency pricing.

### What Companies Usually Do Differently at This Scale
Real inventory systems (Shopify, Square) never denormalize stock without an
event log backing it — `stock_movements` *is* your event log, so you're
already doing the honest version of this, just without the full event-
sourcing machinery (that's Phase 5 territory, introduced only as an
overview).

### Common Mistakes (things to watch yourself for)
- Doing the stock check and the stock decrement in two separate queries
  (classic TOCTOU bug) instead of one atomic `UPDATE ... WHERE stock >= qty`
  or a row lock.
- Business rules leaking into Pydantic schemas or route handlers.
- Testing only the happy path.
- Adding indexes speculatively instead of from an `EXPLAIN ANALYZE` you
  actually ran.

---

## 4. Mini-Projects (interleaved through the weeks, listed where they land)

| Mini-project | Week | Teaches |
|---|---|---|
| Retry + timing decorator library | 1 | Decorators, closures, `functools.wraps` |
| Lazy CSV row generator (for a 1M-row product import) | 2 | Generators, iterators, memory behavior |
| Config loader using a context manager (auto-rollback on error) | 2 | Context managers, `__enter__`/`__exit__` |
| Typed `Repository[T]` mini-abstraction using `Protocol` + generics | 3 | Typing, Protocols, structural typing |
| Descriptor-based field validator (mini ORM field) | 3 | Descriptors, dataclasses |
| Concurrent supplier-price fetcher (asyncio, 5 fake endpoints) | 4 | asyncio basics, `gather`, task cancellation |

---

## 5. Books & Documentation for This Phase

- *Fluent Python* (Ramalho) — Ch. 7 (decorators/closures), Ch. 9 (dataclasses),
  Ch. 17 (iterators/generators), Ch. 23 (descriptors). Read the matching
  chapter the same week you use the concept — not before.
- FastAPI official docs: Dependency Injection, Security (OAuth2/JWT) sections.
- SQLAlchemy 2.0 docs: ORM Querying Guide, Session Basics.
- PostgreSQL docs: Ch. 11 (Indexes), Ch. 13 (Concurrency Control) — read
  Ch. 13 in Week 4 right when you hit the race-condition task.
- *Use The Index, Luke* (free, use-the-index-luke.com) — read alongside
  Week 3's indexing work.

---

## 6. Weekly Interview Question Sets

**Week 1 — Python fundamentals**
1. What does `@wraps` fix and what breaks without it?
2. Difference between a decorator with and without arguments — how do you
   implement the latter?
3. Explain reference counting and when it alone frees an object.
4. What causes a reference cycle and how does the GC handle it?
5. Mutable default argument bug — why does it happen?

**Week 2 — Iterators, generators, context managers**
1. Iterator vs iterable — precise definitions.
2. Why do generators save memory over building a full list?
3. What does `yield from` do that a manual loop doesn't?
4. Write a context manager two ways (class-based and `@contextmanager`).
5. What happens to a generator if you never exhaust it (GC behavior)?

**Week 3 — Typing, dataclasses, descriptors, indexing**
1. `Protocol` vs `ABC` — when do you pick each?
2. What does `@dataclass(frozen=True)` buy you?
3. Data descriptor vs non-data descriptor — give an example of each.
4. When does an index *not* help a query?
5. What's a composite index's column-order rule?

**Week 4 — Async basics, transactions, testing**
1. What's actually happening at the OS level when you `await` an I/O call?
2. Why can't CPU-bound work be sped up by `asyncio` alone?
3. Explain a dirty read vs a phantom read.
4. How do you deterministically test a race condition in Pytest?
5. Why mock the repository, not the database, in a service-layer unit test?

---

## 7. Daily Plan — Week 1: Decorators, Closures, Project Skeleton

| Day          | Topics                                  | Reading                              | Mini Exercise                                      | StockPilot Task                                                                         | Testing                                                           | Git Commit                                    | Interview Prep                                     | DSA Problem                                                  | SQL Problem                                                                                                            | Time |
| ------------ | --------------------------------------- | ------------------------------------ | -------------------------------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | ---- |
| **Mon (D1)** | Functions as objects, closures          | Fluent Python Ch.7 §1-2              | Write a `@timer` decorator                         | Scaffold repo: folder structure, `pyproject.toml`, ruff/mypy config                     | Add pytest, write one trivial passing test to confirm CI wiring   | `chore: project scaffold + tooling`           | Q1 from Week1 set — write answer                   | Contains Duplicate                                           | Combine Two Tables                                                                                                     | 3.5h |
| **Tue (D2)** | Decorators with args, `functools.wraps` | Fluent Python Ch.7 §3                | Write `@retry(times=3)`                            | Define `User`, `Product`, `Category` SQLAlchemy models                                  | Unit test model field defaults                                    | `feat: core models (user, product, category)` | Q2                                                 | Valid Anagram                                                | StockPilot: products where current_stock < reorder_level                                                               | 3.5h |
| **Wed (D3)** | Class-based decorators, stacking order | docs.python.org `functools` | Combine `@timer` + `@retry`, verify stacking order | Add `Supplier`, `StockMovement`, `Order`, `OrderItem` models + Alembic init migration | Test migration runs up/down cleanly | `feat: remaining models + initial migration` | Q3 | Warm-up: implement a hash table from scratch; Two Sum | StockPilot: products with no supplier | 3.5h |
| **Thu (D4)** | Reference counting basics               | Fluent Python Ch.6 (weak refs intro) | `sys.getrefcount` experiment script                | Implement `core/config.py` (Pydantic settings) + `db/session.py` (async engine/session) | Test settings load from `.env` correctly                          | `feat: config + db session management`        | Q4                                                 | Group Anagrams                                               | Find Customer Referee                                                                                                  | 3.5h |
| **Fri (D5)** | Reference cycles + `gc` module          | docs.python.org `gc`                 | Deliberately create and detect a reference cycle   | Docker Compose: `api` + `postgres` services, healthcheck                                | Verify `docker compose up` boots both services and migration runs | `chore: docker compose for local dev`         | Q5                                                 | Top K Frequent Elements                                      | StockPilot: categories with no products                                                                                | 3.5h |
| **Sat (D6)** | **Review**                              | —                                    | Redo `@retry` decorator from memory, no notes      | Mentally walk through why models are shaped this way                                    | Re-run full test suite                                            | —                                             | Answer all 5 Week-1 questions out loud, unscripted | Review: redo Thursday's problem from memory — Group Anagrams | Review: rewrite Tuesday's query from memory, then extend it — StockPilot: products where current_stock < reorder_level | 2.5h |

---

## 8. Daily Plan — Week 2: Generators, Iterators, Context Managers

| Day | Topics | Reading | Mini Exercise | StockPilot Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D7)** | Iterator protocol (`__iter__`/`__next__`) | Fluent Python Ch.17 §1-2 | Custom `Countdown` iterator class | Build `repositories/product_repository.py` (basic CRUD queries) | Unit test repository against real Postgres (integration) | `feat: product repository` | Q1 | Product of Array Except Self | StockPilot: total stock value per category | 3.5h |
| **Tue (D8)** | Generator functions, `yield` | Fluent Python Ch.17 §3 | Lazy CSV row generator for 1M-row fake product import | Build `services/product_service.py` (validation rules on top of repo) | Unit test service with mocked repository | `feat: product service layer` | Q2 | Valid Sudoku | Big Countries | 3.5h |
| **Wed (D9)** | Generator expressions, `yield from`, coroutine basics | Fluent Python Ch.17 §4-5 | Chain 3 generators with `yield from` | Build `api/products.py` router wired to service | Integration test: `POST /products`, `GET /products` end-to-end | `feat: products API endpoints` | Q3 | Encode and Decode Strings | StockPilot: count orders per status | 3.5h |
| **Thu (D10)** | Context manager protocol | Fluent Python Ch.15/16 (context mgrs) | Class-based context manager: auto-rollback DB session on exception | Wire real DB session as a context-managed dependency in FastAPI | Test that a failing request rolls back partial writes | `feat: transactional session dependency` | Q4 | Longest Consecutive Sequence | StockPilot: top 5 products by units sold | 3.5h |
| **Fri (D11)** | `@contextmanager` decorator version | docs.python.org `contextlib` | Rewrite Thursday's context manager using `@contextmanager` | Add pagination + filtering (`category_id`, `low_stock`) to `GET /products` | Test pagination edge cases (empty page, last page) | `feat: product list pagination + filters` | Q5 | Valid Palindrome | Classes More Than 5 Students | 3.5h |
| **Sat (D12)** | **Review** | — | Redo lazy CSV generator from memory | Re-read your own service layer, note anything that smells like a leaked business rule | Full suite re-run | — | Answer all Week-2 questions unscripted | Review: redo Thursday's problem from memory — Longest Consecutive Sequence | Review: rewrite Tuesday's query from memory, then extend it — Big Countries | 2.5h |

---

## 9. Daily Plan — Week 3: Typing, Dataclasses, Descriptors, Indexing

| Day | Topics | Reading | Mini Exercise | StockPilot Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D13)** | `typing` deep dive: generics, `TypeVar` | Fluent Python Ch.8 | Generic `Stack[T]` class | Add `SupplierRepository`, `CategoryRepository` | Unit tests for both | `feat: supplier + category repositories` | Q1 | Two Sum II - Input Array Is Sorted | StockPilot: orders with item count + total value | 3.5h |
| **Tue (D14)** | `Protocol` and structural typing | mypy docs on Protocols | Typed `Repository[T]` Protocol abstraction | Refactor existing repositories to satisfy the `Repository[T]` protocol | Type-check with mypy in CI (make it a real gate) | `refactor: repositories conform to Repository protocol` | Q2 | 3Sum | StockPilot: stock movements joined to the user who made them | 3.5h |
| **Wed (D15)** | `dataclasses`: fields, `frozen`, `__post_init__` | Fluent Python Ch.9 | Immutable `Money` value object (cents-based, no float bugs) | Use `Money` dataclass for `price_cents`/order totals instead of raw ints everywhere | Unit test `Money` arithmetic and immutability | `feat: Money value object` | Q3 | Container With Most Water | Rising Temperature | 3.5h |
| **Thu (D16)** | Descriptors: data vs non-data | Fluent Python Ch.23 | Descriptor-based `PositiveInt` field validator | (Applied conceptually — note in `docs/notes.md` where descriptors *would* replace repeated Pydantic validators) | — | `docs: descriptor notes + rejected alternative` | Q4 | Trapping Rain Water | StockPilot: suppliers whose products never sold | 3.5h |
| **Fri (D17)** | Postgres indexing: B-tree, composite index column order | Use The Index Luke, Postgres docs Ch.11 | Run `EXPLAIN ANALYZE` on `GET /orders?status=&from=&to=` before/after adding index | Add composite index `(status, created_at)` on `orders`, write the Alembic migration | Assert query plan uses index scan, not seq scan, in a test | `perf: composite index on orders(status, created_at)` | Q5 | Best Time to Buy and Sell Stock | Employees Earning More Than Their Managers | 3.5h |
| **Sat (D18)** | **Review** | — | Redo `Repository[T]` Protocol from memory | Re-read `Money` usage across codebase for consistency | Full suite + mypy re-run | — | Answer all Week-3 questions unscripted | Review: redo Thursday's problem from memory — Trapping Rain Water | Review: rewrite Tuesday's query from memory, then extend it — StockPilot: stock movements joined to the user who made them | 2.5h |

---

## 10. Daily Plan — Week 4: Async Basics, Transactions, Race Conditions, Testing, Docker CI

| Day | Topics | Reading | Mini Exercise | StockPilot Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D19)** | `async`/`await` mechanics, event loop basics | RealPython asyncio guide | Concurrent fetch from 5 fake supplier endpoints with `asyncio.gather` | Build `OrderService.create_order` — happy path only, no concurrency handling yet | Unit test happy-path order creation | `feat: order creation (happy path)` | Q1 | Longest Substring Without Repeating Characters | StockPilot: products priced above the average product price | 3.5h |
| **Tue (D20)** | Transactions, isolation levels, dirty/phantom reads | Postgres docs Ch.13 §1-2 | Write a script that intentionally reproduces a dirty read at `READ UNCOMMITTED` (Postgres treats it as READ COMMITTED — explain why) | Wrap `create_order` stock decrement in a transaction with `SELECT ... FOR UPDATE` | Test that decrement + insert are atomic (kill mid-transaction, verify no partial write) | `fix: atomic stock decrement with row lock` | Q2 | Longest Repeating Character Replacement | StockPilot: orders by users with zero stock movements | 3.5h |
| **Wed (D21)** | Row locks, deadlocks (conceptually) | Postgres docs Ch.13 §3 | Reproduce a deadlock with two scripts locking rows in opposite order, observe Postgres auto-cancel one | Handle "insufficient stock" as a clean 409 response, not a 500 | Integration test: two concurrent `POST /orders` for the last unit — exactly one succeeds | `test: concurrent order creation race condition` | Q3 | Permutation in String | Second Highest Salary | 3.5h |
| **Thu (D22)** | Pytest architecture: fixtures, factories, mocking philosophy; property-based testing with Hypothesis — testing invariants instead of hand-picked examples | pytest docs on fixtures + Hypothesis "Quick start guide" | Convert 3 hand-written test setups to `factory_boy` factories; write one Hypothesis test for `apply_discount(price, pct)` asserting the invariant `0 <= result <= price` across generated inputs | Add `factories.py`, replace manual test data across suite; add `hypothesis` to dev deps, one property-based test on a pure pricing/stock-math function | Coverage report — target 80%+ on services/repositories; Hypothesis test run with `--hypothesis-seed` pinned in CI for reproducible failures | `test: introduce factory_boy + hypothesis property test, raise coverage` | Q4 | Warm-up: implement a stack from scratch; Valid Parentheses | StockPilot: EXPLAIN ANALYZE the low-stock query | 3.5h |
| **Fri (D23)** | CI pipelines, Docker layer caching, lightweight load testing | GitHub Actions docs | Run `hey -n 500 -c 20 http://localhost:8000/products` against your own API, read the p95 | Finalize `.github/workflows/ci.yml` (lint + mypy + pytest against Postgres service container) | Confirm CI is green on a clean clone | `ci: full pipeline — lint, typecheck, test` | Q5 | Min Stack | Duplicate Emails | 3.5h |
| **Sat (D24)** | **Phase 1 wrap review** | — | Redo the deadlock reproduction from memory, explain it out loud | Write `docs/postmortem.md`: what you'd do differently, what's deferred to Phase 2 and why | Full suite, full CI, tag `v0.1-phase1` | `docs: phase 1 postmortem + retrospective` | Mock-answer all 20 Phase-1 interview questions back to back, timed | Review: redo Thursday's problem from memory — Valid Parentheses | Review: rewrite Tuesday's query from memory, then extend it — StockPilot: orders by users with zero stock movements | 2.5h |

---

## 11. Deliverables & GitHub Milestones

**Milestone: `Phase 1 — StockPilot v0.1`**
- [ ] Repo scaffolded with layered architecture (api/services/repositories/models)
- [ ] All 8 core endpoints implemented and tested
- [ ] Alembic migrations for full schema, including the composite index
- [ ] Race-condition test proving atomic stock decrement
- [ ] `factory_boy`-based test suite, 80%+ coverage on services/repositories
- [ ] Docker Compose local dev environment
- [ ] GitHub Actions CI green (lint + mypy + pytest)
- [ ] `docs/postmortem.md` written
- [ ] Tag: `v0.1-phase1`

---

## 12. Skills Acquired Checklist

- [ ] Decorators (with/without args, stacked, class-based)
- [ ] Generators & iterator protocol
- [ ] Context managers (both styles)
- [ ] `typing`: generics, `Protocol`
- [ ] `dataclasses` incl. `frozen`, `__post_init__`
- [ ] Descriptors (data vs non-data) — conceptual fluency
- [ ] Reference counting + GC generational collector — conceptual fluency
- [ ] Layered architecture (API/Service/Repository) applied, not just described
- [ ] PostgreSQL indexing decisions backed by `EXPLAIN ANALYZE`
- [ ] Transactions, row locks, isolation-level vocabulary
- [ ] N+1 avoidance (felt firsthand, not memorized)
- [ ] Pytest: unit + integration split, fixtures, factories, mocking discipline
- [ ] Property-based testing with Hypothesis — invariants over hand-picked examples
- [ ] Docker Compose multi-service local dev
- [ ] Basic CI pipeline (lint, typecheck, test)

---

**Next:** say "start Phase 2" when you're ready, or tell me what to adjust
in Phase 1 first (pacing, project domain, depth on any topic).
