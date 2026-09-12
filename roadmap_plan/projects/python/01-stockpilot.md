# Project 1 — StockPilot

**Single-store inventory & order management API**

| | |
|---|---|
| Domain | Retail / Inventory |
| Level | Junior |
| Phase | 1 — Foundations |
| Weeks | 1–4 (D1–D24) |
| Stack | Python 3.12+, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Pydantic v2, pytest + Hypothesis, `structlog`, `pre-commit`, Docker (multi-stage) + Compose, GitHub Actions |
| Repo | `StockPilot/` |

> **What this project is really for.** One architectural habit — the router never
> touches the ORM — and one correctness problem — two people selling the last unit
> at the same time. Everything else is scaffolding around those two lessons.

---

## 1. Business Problem

A small retail shop owner tracks stock in a spreadsheet. Stock counts drift from
reality, staff oversell out-of-stock items, there is no audit trail of who
changed what, and the owner has no visibility into order history or which
products are slow-moving.

StockPilot digitizes this: staff manage inventory and process orders through an
API (a future frontend or POS integrates with it), and the owner gets accurate
stock plus basic reporting.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. A running API with authentication, two roles, and eleven endpoints
2. Products, categories and suppliers manageable end to end
3. Stock that can only change through an audited movement — never by silent overwrite
4. Orders that decrement stock atomically and refuse to oversell
5. Three reports the owner actually asked for
6. `docker compose up` bringing the whole thing to life from a clean clone

**Proof it is correct**
7. A concurrency test where two simultaneous orders for the last unit produce
   exactly one success and one clean `409`
8. A property-based test (Hypothesis) on the pricing/stock math
9. 80%+ coverage on services and repositories, with mypy and ruff gating CI
10. A load-test number for `GET /products`, not a guess
11. `GET /categories/{id}/tree` served by a **recursive CTE**, and a stock-value
    report rolled up through the category tree
12. **Keyset (cursor) pagination** on `GET /orders`, benchmarked against offset on
    500k rows — so interview question 4 has a measured answer, not a guess
13. A **multi-stage, non-root Dockerfile** whose image size you know

**Written artefacts that become interview answers**
14. `docs/notes.md` — the descriptor decision you considered and rejected, the
    **UUID-vs-bigint primary-key decision**, and the **password-hashing choice**
15. `docs/scaling-notes.md` — what breaks first under load and why
16. `docs/postmortem.md` — what you would do differently

---

## 3. Scope

**In scope (v1)**
- CRUD for products, categories, suppliers
- Stock adjustments with reason + audit trail
- Orders with atomic stock decrement
- Two roles with different permissions
- List / filter / paginate products and orders
- Reports: stock value, low-stock list, orders in a date range
- Category tree (recursive CTE) and per-category roll-up (`GROUP BY ... ROLLUP`)
- Keyset pagination on `/orders`, offset pagination on `/products` — both, so the
  difference is something you measured

**Deliberately out of scope — each with a written TODO explaining why**

| Deferred | Where it lands | Why not now |
|---|---|---|
| Redis cache on `GET /products` | Phase 2 (QuickServe) | You have not felt the read pressure yet |
| Celery low-stock email alerts | Phase 2/3 (PeopleOps) | The synchronous version has to hurt first |
| Refresh tokens, OAuth | Phase 2 | One auth concept at a time |
| Soft deletes with audit history | Backlog | `stock_movements` already gives you the audit that matters |
| Webhooks on order status change | Backlog | No consumer exists |
| Multi-currency pricing | Backlog | Single store, single currency |
| Metrics, tracing, dashboards | Phase 4 | Nothing to compare across services yet |
| Real cloud deploy (IAM, VPC, managed DB) | Phase 6 | Not a system worth that setup cost yet |

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`owner`** | Everything: create/update/delete products, categories and suppliers; adjust stock; process orders; view revenue and stock-value reports | — |
| **`staff`** | List and view products; create stock movements; create orders; change order status; view the low-stock report | Delete products; view revenue or stock-value reports |

**Enforcement:** a short-lived JWT access token carries a `role` claim. A FastAPI
dependency `require_role("owner")` guards the sensitive routes. Role checks live
in one place — not scattered through handlers.

---

## 5. Functional Modules

### 5.1 Catalogue
Products, categories (self-referencing for a simple hierarchy), suppliers. A
product has a unique SKU, a price, a current stock level and a reorder level.

### 5.2 Stock control
Every change to stock is a `stock_movement` row with a `delta`, a `reason` and
the user who made it. Receiving stock, manual corrections and order-driven
decrements all go through the same path. There is no endpoint that sets a stock
number directly — that is a deliberate design decision, not an omission.

### 5.3 Ordering
An order is created with its items in one transaction. Stock is decremented
atomically; if any line is short, the whole order is refused with a `409`.
Status moves `pending → partially_fulfilled → fulfilled | cancelled`.

### 5.4 Reporting
Stock value (owner only), low-stock list, and orders within a date range filtered
by status. Computed on request — the "the owner wants an email, not a page to
poll" problem is left deliberately unsolved here.

### 5.5 Auth
Login issuing a short-lived JWT. No refresh tokens yet; the gap is written down.

---

## 6. Domain Model

```
users(id, email UNIQUE, hashed_password, role, created_at)

categories(id, name, parent_id NULL -> categories.id)

suppliers(id, name, contact_email)

products(id, sku UNIQUE, name,
         category_id -> categories.id,
         supplier_id -> suppliers.id,
         price_cents, current_stock, reorder_level)

stock_movements(id, product_id -> products.id, delta, reason,
                created_by -> users.id, created_at)

orders(id, status, created_by -> users.id, created_at)

order_items(id, order_id -> orders.id, product_id -> products.id,
            qty, unit_price_cents)
```

### The one modelling decision worth defending

`products.current_stock` is a **denormalized cache**. It changes only when a
`stock_movements` row is inserted, in the same transaction.

- `stock_movements` is the **event log** — the truth
- `current_stock` is the **materialized sum** — the convenience

The alternative (summing movements on every read) is correct but gets slow, and
the alternative (trusting a mutable number with no log) is fast but unauditable.
This is a deliberate, defensible tradeoff — be ready to say so.

### Value objects

`unit_price_cents` and `price_cents` are integer cents wrapped in a frozen
`Money` dataclass. Not floats. Not `Decimal` scattered ad hoc. One type, with
arithmetic and immutability tested.

---

## 7. Database Design

| Index | Reason |
|---|---|
| `products.sku` UNIQUE | Natural key lookup and uniqueness constraint |
| `products.category_id` | Product-list filter |
| `orders.created_at` | Date-range reports |
| `stock_movements.product_id` | Audit trail per product |
| `orders(status, created_at)` composite | Added **after** seeing a seq scan in `EXPLAIN ANALYZE`, never before |

**Migrations:** Alembic. Every schema change is a migration; every migration runs
cleanly **both up and down**, and that is tested.

**Constraints worth having:** non-negative `qty`, non-negative `current_stock`,
`price_cents >= 0`. Let the database refuse nonsense even if the service layer
already does.

**Time is `timestamptz`, stored in UTC.** Every `created_at` is `TIMESTAMP WITH TIME
ZONE`. Naive timestamps are the bug you will otherwise meet in PeopleOps (leave
dates) and CarePoint (appointment slots). Start the habit here, in
`docs/notes.md`, with one sentence on why `timestamp` (without tz) is a trap.

**Primary keys — decide and write it down.** Internal `bigint` sequence plus a
public `UUID` (or ULID) exposed in the API, or UUID everywhere? Name the
trade-offs: sequential IDs leak volume and enable enumeration; random UUIDs
fragment B-tree indexes; ULID/UUIDv7 are the usual compromise. One paragraph in
`docs/notes.md` — this is asked in most backend interviews.

**Two query shapes worth knowing by name:**

| Query | SQL feature | Where |
|---|---|---|
| Category and all descendants | `WITH RECURSIVE` on `categories.parent_id` | `GET /categories/{id}/tree`, stock value by category subtree |
| Stock value with subtotals per category and a grand total | `GROUP BY ROLLUP(category_id)` (or `GROUPING SETS`) | `GET /reports/stock-value` |
| Orders page N of 500k | **Keyset**: `WHERE (created_at, id) < (:cursor_ts, :cursor_id) ORDER BY created_at DESC, id DESC LIMIT :n` on the `(status, created_at)` index | `GET /orders?cursor=` |

Offset pagination on `/products` stays — it is fine for a few thousand rows and
the admin needs "jump to page 7". Keyset on `/orders` is where you show the
`EXPLAIN` of `OFFSET 400000` reading 400k rows to throw them away.

---

## 8. API Design

| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/auth/login` | public | Returns a short-lived JWT access token |
| GET | `/products` | staff+ | Query: `category_id`, `low_stock`, `page`, `page_size` |
| POST | `/products` | owner | |
| PATCH | `/products/{id}` | owner | |
| POST | `/products/{id}/stock-movements` | staff+ | Body: `delta`, `reason`. Audited |
| GET | `/orders` | staff+ | Query: `status`, `from`, `to`, **`cursor`, `limit`** — keyset pagination |
| GET | `/categories/{id}/tree` | staff+ | Recursive CTE; the category and all descendants |
| POST | `/orders` | staff+ | Atomic decrement; `409` if insufficient |
| GET | `/orders/{id}` | staff+ | Order + items + product info — **the N+1 lives here** |
| PATCH | `/orders/{id}/status` | staff+ | |
| GET | `/reports/stock-value` | owner | `ROLLUP` by category: subtotals + grand total |
| GET | `/reports/low-stock` | staff+ | `current_stock < reorder_level` |

**Error contract:** insufficient stock → `409`. Validation failure → `422`.
Missing role → `403`. Never a `500` for a condition you anticipated.

---

## 9. Business Rules (invariants)

1. Stock can never go below zero.
2. `current_stock` changes **only** through a `stock_movements` insert, in the
   same transaction.
3. Every destructive or stock-changing action is traceable to a `user_id`.
4. Insufficient stock is a `409`, never a `500`.
5. Two concurrent orders for the last unit → exactly one succeeds.
6. A router function never touches SQLAlchemy directly.
7. An order's `unit_price_cents` is captured at order time — a later price change
   must not rewrite history.

---

## 10. Architecture

```
Client → FastAPI routers      (API layer — request/response shape only)
       → Service layer        (business rules: "can't sell below zero")
       → Repository layer     (SQLAlchemy queries, no business logic)
       → PostgreSQL
```

**The habit this project exists to drill:** the router never talks to the ORM.

A useful self-test: could you swap FastAPI for something else and keep the
service layer untouched? If not, the boundary has leaked.

```
StockPilot/
  app/
    api/           # routers + Pydantic request/response schemas
    services/      # business logic, orchestrates repositories
    repositories/  # SQLAlchemy queries only
    models/        # SQLAlchemy ORM models
    core/          # config, security (JWT), logging setup
    db/            # session management, declarative base
  alembic/
  tests/
    unit/          # service tests, repositories mocked
    integration/   # real Postgres, repository + endpoint tests
    factories.py
  docker-compose.yml
  Dockerfile
  .github/workflows/ci.yml
```

Repositories conform to a `Repository[T]` **Protocol** — structural typing, not
inheritance — and mypy enforces it in CI.

**Async discipline, made concrete once.** `GET /orders/{id}` fetches the order,
its items and the product rows. Do it three ways and time them: sequential
awaits, `asyncio.gather` over independent repository calls, and one joined
query. Then put a deliberately blocking call (e.g. `time.sleep`, or a sync
`bcrypt` hash) inside a handler, watch every other request stall, and move it to
`run_in_executor`. Write two sentences in `docs/notes.md` on what the event loop
actually does, and when `gather` helps versus when the database is the
bottleneck anyway.

---

## 11. Infrastructure — what to connect, and exactly where

Phase 1 is deliberately thin. That thinness is the point: every later project
adds a component only when a felt problem demands it.

| Component | Where exactly it is used | Why |
|---|---|---|
| **PostgreSQL** | Everything | The only datastore |
| **Dockerfile** | **Multi-stage** (builder with compilers → slim runtime), **non-root user**, `.dockerignore`, dependency layer cached before the code layer, pinned base image. Record the image size before and after multi-stage | The first Dockerfile sets the habit for the next nine. A root container that ships `gcc` is the default you must deliberately avoid |
| **Docker Compose** | `api` + `postgres`, with a **real Postgres healthcheck** so `api` waits for readiness, not just "container started" | Reproducible local environment |
| **`pre-commit`** | ruff + mypy + a secrets check running on every commit, before CI sees it | CI should confirm, not discover |
| **`structlog`** | One structured JSON line per request: method, path, status, latency, `user_id` | Your only observability this phase |
| **GitHub Actions** | ruff → mypy → pytest against a Postgres service container | The quality gate |
| **`hey` or `locust`** | One light load test on `GET /products` in Week 4 | A number for `docs/scaling-notes.md` |

**Deliberately NOT connected — and you must be able to say why:**

| Component | Why not, and where it arrives |
|---|---|
| **Redis** | You have not measured a slow read yet. Adding a cache before you can show the p95 it fixes is guessing. → Phase 2 |
| **Celery / a broker** | The only async-shaped need is low-stock alerts, and you deliberately keep them synchronous so the pain is real. → Phase 2/3 |
| **Nginx / a gateway** | One service. Nothing to route. → Phase 4 |
| **Prometheus / Grafana** | Nothing to compare. One service's metrics are just numbers. → Phase 4 |
| **Object storage** | No files. → Phase 4 |

---

## 12. Build Plan (consolidated)

The daily plan splits this across D1–D24. Here it is merged into four coherent
stages. Each ends green and committed.

### Stage 1 — Skeleton & data layer *(D1–D6, Week 1)*
- Scaffold: folder structure, `pyproject.toml`, ruff + mypy config, pytest wired,
  one trivial passing test to confirm CI plumbing
- Define **all** ORM models at once: `User`, `Product`, `Category`, `Supplier`,
  `StockMovement`, `Order`, `OrderItem`
- Alembic init + the initial migration — verify **up and down**
- `core/config.py` — Pydantic settings from `.env`
- `db/session.py` — async engine + session factory
- `docker-compose.yml` — `api` + `postgres` with a healthcheck
- **`Dockerfile`: multi-stage, non-root, `.dockerignore`**; note the image size
- **`pre-commit`** with ruff + mypy + `gitleaks` (or `detect-secrets`)
- All timestamps `timestamptz`; `docs/notes.md` gets the tz and PK decisions

*Done when:* `docker compose up` boots both services, migrations run, tests pass,
and `docker run --rm <image> whoami` is not `root`.

### Stage 2 — Products vertical slice *(D7–D12, Week 2)*
- `repositories/product_repository.py` — CRUD queries only
- `services/product_service.py` — validation rules on top of the repository
- `api/products.py` — router wired to the service
- DB session as a **context-managed** FastAPI dependency: a failed request rolls
  back partial writes
- Pagination + filtering (`category_id`, `low_stock`) on `GET /products` (offset)
- **`GET /categories/{id}/tree`** with `WITH RECURSIVE`; test on a 4-level tree
- Review pass: re-read your own service layer and find anything that smells like
  a business rule that leaked into a schema or handler

*Done when:* products work end to end, pagination edge cases (empty page, last
page) are tested, and a failing request leaves no partial write.

### Stage 3 — Typing discipline & value objects *(D13–D18, Week 3)*
- `SupplierRepository`, `CategoryRepository`
- Refactor all repositories to satisfy the `Repository[T]` Protocol
- Make **mypy a real CI gate**, not advisory
- Introduce `Money`; replace raw `price_cents` ints across the codebase
- Run `EXPLAIN ANALYZE` on the "orders in a date range by status" query, see the
  seq scan, **then** add the `(status, created_at)` composite index and its
  migration. Write a test asserting the plan uses an index scan
- **Keyset pagination on `GET /orders`**: seed 500k orders, `EXPLAIN ANALYZE`
  `OFFSET 400000` vs the keyset predicate, record both plans in
  `docs/scaling-notes.md`
- `GET /reports/stock-value` with `ROLLUP` — subtotal per category, grand total
- The async exercise from §10: sequential vs `gather` vs one join, plus the
  blocking-call demonstration and `run_in_executor`
- `docs/notes.md`: where descriptors *would* replace repeated Pydantic
  validators, and why you rejected that

### Stage 4 — Orders, concurrency & hardening *(D19–D24, Week 4)*
- `OrderService.create_order` — happy path first, no concurrency handling
- **Then** wrap the stock decrement in a transaction with `SELECT ... FOR UPDATE`
  (or an atomic `UPDATE ... WHERE stock >= qty`)
- Insufficient stock → clean `409`
- `factories.py` with `factory_boy`, replacing hand-written test data
- One Hypothesis property test on a pure pricing/stock-math function, seed pinned
  in CI for reproducible failures
- Finalize `.github/workflows/ci.yml`
- Light load test on `GET /products`; write `docs/scaling-notes.md`
- `docs/postmortem.md`; tag `v0.1-phase1`

> **Do the happy path before the concurrency fix on purpose.** Writing the naive
> version, then breaking it with two concurrent requests, then fixing it, is the
> lesson. Writing it correctly the first time teaches you nothing about why.

---

## 13. Testing Strategy

| Layer | What | How |
|---|---|---|
| Unit | Business rules in isolation | Service layer, repositories mocked — "reject order if stock insufficient" |
| Unit | `Money` arithmetic and immutability | Pure |
| Integration | Real queries, real constraints | Real Postgres in Docker; repositories + endpoints |
| **Race** | **The overselling bug** | Two concurrent `POST /orders` for the last unit — exactly one succeeds, the other gets a clean `409` |
| Transaction | Rollback correctness | A failing request leaves no partial write |
| Property | Pure math | Hypothesis on pricing/stock functions, seed pinned |
| Migration | Reversibility | Every migration up **and** down |
| Plan | Index actually used | Assert index scan, not seq scan |
| Pagination | Edge cases | Empty page, last page, page beyond the end |
| **Keyset** | Cursor correctness | Stable ordering under ties on `created_at`; no duplicates or gaps across pages when rows are inserted mid-walk; plan uses the index |
| Recursive CTE | Tree correctness | 4-level tree returns every descendant once; a cycle guard (`UNION` not `UNION ALL`, or a depth cap) is tested |
| Report | `ROLLUP` | Subtotals sum to the grand total |
| Image | Non-root | Container user is not root; image contains no compiler |

**Target:** 80%+ coverage on `services/` and `repositories/` — not on everything.
Coverage on routers and schemas is mostly self-congratulation.

---

## 14. Non-functional Targets & Observability

- p95 latency on `GET /products` under ~150 req/s — **measured** in Week 4
- Stock decrement correct under concurrent load
- Every destructive action traceable to a user
- One structured JSON log line per request: method, path, status, latency, `user_id`

---

## 15. CI/CD & Deployment

- **CI:** GitHub Actions on every push — ruff, mypy, pytest against a Postgres
  service container. No deploy step yet
- **Deploy:** single VPS or Render/Railway, `docker compose up -d`, manual.
  Zero-downtime is Phase 4; real cloud is Phase 6

---

## 16. Definition of Done

- [ ] All eleven endpoints implemented and integration-tested
- [ ] Overselling proven impossible by a passing concurrency test
- [ ] mypy clean, ruff clean, both gating CI
- [ ] 80%+ coverage on services and repositories
- [ ] Every migration reversible, and tested that way
- [ ] Composite index added from a real `EXPLAIN ANALYZE`, with a plan assertion
- [ ] Keyset pagination on `/orders`, offset-vs-keyset plans recorded
- [ ] `WITH RECURSIVE` category tree and `ROLLUP` stock-value report, tested
- [ ] All timestamps `timestamptz`; PK and password-hashing decisions in `docs/notes.md`
- [ ] Multi-stage, non-root Dockerfile; `pre-commit` configured
- [ ] `Money` used consistently; no raw cent ints in business code
- [ ] `docker compose up` works from a clean clone
- [ ] `docs/notes.md`, `docs/scaling-notes.md`, `docs/postmortem.md` written
- [ ] Tagged `v0.1-phase1`

---

## 17. Scaling Notes (written, not built)

What breaks first under load: a single Postgres instance, no caching, an untuned
connection pool. What you would do about each, and in what order. This document
is the seed of your system-design interview answers — write it as if someone will
read it back to you.

---

## 18. Interview Questions This Project Should Let You Answer

1. How would you prevent overselling the last unit of stock under concurrent requests?
2. Why is `current_stock` denormalized here — what's the tradeoff, and what would
   change your mind?
3. Walk me through your layered architecture, and why the router never touches the ORM.
4. How would you paginate `/products` for 500k rows efficiently?
5. What does your JWT contain, and why is the access token short-lived?
6. Where's the N+1 risk in `GET /orders/{id}` and how did you avoid it?
7. How do you test a race condition deterministically?
8. What's your rollback strategy if a migration fails mid-deploy?
9. Why did you *not* add caching here?
10. What does `SELECT ... FOR UPDATE` actually lock, and for how long?
11. Offset vs keyset pagination — show me the two plans and tell me when offset is
    still the right choice.
12. Write me a recursive CTE for a category tree. What stops it looping forever?
13. UUID or bigint primary keys — what did you choose and what would change your mind?
14. Why `timestamptz` and not `timestamp`?
15. What does `asyncio.gather` buy you here, and what happens when you put a
    blocking call inside an async handler?
16. Why does your Dockerfile have two stages, and why is the runtime user not root?

---

## 19. Common Mistakes to Watch For

- Doing the stock check and the decrement as two separate queries — the classic
  TOCTOU bug — instead of one atomic statement or a row lock
- Business rules leaking into Pydantic schemas or route handlers
- Testing only the happy path
- Adding indexes speculatively instead of from an `EXPLAIN ANALYZE` you ran
- Letting `unit_price_cents` read through to the product, so old orders change
  when a price changes
- Treating 100% coverage as the goal instead of coverage where the rules live
- Naive `timestamp` columns, so the same instant means different things on two machines
- A recursive CTE with `UNION ALL` and no depth guard on data that can contain a cycle
- A single-stage Dockerfile running as root with build tools left in the image
- Calling a sync, CPU-heavy function (password hashing!) directly inside an async handler

---

## 20. How Real Companies Differ

Real inventory systems (Shopify, Square) never denormalize stock without an event
log behind it. `stock_movements` **is** that event log — so you are already doing
the honest version, just without the full event-sourcing machinery. That machinery
is Phase 5 territory, and even there only as an overview.

---

## 21. AI/ML/Data Extension — Stage 5 *(Week 4, +3 days)*

> **Why here.** `stock_movements` is already an append-only event log — the cleanest
> possible raw material for a first brush with both data engineering and applied
> ML. This is deliberately the lightest AI touch in the whole curriculum: one
> mental model — *features come from your own operational data, not from a
> vendor API* — not a production system. Track B's **Project 17** (Phase 9,
> StockPilot Demand Forecaster) rebuilds this exact problem with real rigor
> (train/validation/test discipline, several model families, full evaluation,
> deployment). This section is the "before" picture that makes Project 17 feel
> like a continuation, not a cold start.

**Scope (in)**
- A read-only export script pulling `orders` + `order_items` + `stock_movements`
  into a weekly-aggregated Parquet file — the smallest possible ETL
- A single-feature linear regression (`scikit-learn`) forecasting next week's
  units sold per product from the last N weeks
- A naive baseline ("next week = this week") computed on the same data
- MAE and RMSE for both, compared

**Scope (out) — named**

| Deferred | Where it lands |
|---|---|
| Train/validation/test split discipline, cross-validation | Phase 9, Project 17 |
| Multiple model families, feature engineering beyond lag features | Phase 9 |
| Model serving, an API endpoint, a retraining schedule | Phase 9/10 |
| A feature store | Never — the export script *is* the pipeline at this scale |

**New artifacts**
```
analytics/
  export_analytics.py   # repository-layer reads → weekly Parquet, no new endpoints
  forecast.py            # pandas + scikit-learn LinearRegression, lag features
docs/forecast-notes.md   # MAE/RMSE vs. naive baseline, and why beating naive matters
```

**Testing**
- The export script produces one row per `(product_id, iso_week)` with no gaps for
  weeks that had zero sales (explicit zero, not a missing row — a missing week
  silently corrupts a lag feature)
- The forecast script is deterministic given a fixed random seed

**Definition of Done**
- [ ] `export_analytics.py` produces a Parquet file with zero-filled weekly rows
- [ ] Linear regression MAE/RMSE computed against the naive baseline, both recorded
- [ ] `docs/forecast-notes.md` written, including one honest sentence on whether the
      model actually beat the baseline

**Interview questions this adds**
1. Why export to Parquet instead of querying Postgres directly for every training run?
2. What is a naive baseline, and why must a forecasting model beat it to be worth anything?
3. What would this need before it could run against production traffic — and where in the curriculum does that get built?
