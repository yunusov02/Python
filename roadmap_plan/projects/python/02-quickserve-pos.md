# Project 2 — QuickServe POS

**Point-of-sale system: cart, discounts, checkout, receipts, returns**

| | |
|---|---|
| Domain | Retail / POS |
| Level | Junior |
| Phase | 2 — Concurrency + Django/DRF + Caching |
| Weeks | 5–7 (D25–D39) |
| Stack | Python, **Django + DRF**, PostgreSQL, **Redis**, `djangorestframework-simplejwt`, `fakeredis`, Docker Compose, GitHub Actions |
| Repo | `quickserve/` |

> **Why Django here and FastAPI in Project 1?** This project is admin-heavy: a
> manager must browse receipts without an API client, and Django Admin gives that
> for free. The switch is deliberate and you must be able to defend it — "how do
> you choose a framework" is a real interview question, and "I used what I know"
> is not an answer.

---

## 1. Business Problem

A retail cashier needs a fast checkout flow — select items, apply per-item or
cart-level discounts, compute tax, take a mock payment, issue a receipt, and
process returns. A manager needs daily sales totals without touching the database
directly, and without waiting for someone to build them a screen.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. A Django/DRF service with cashier and manager roles on access + refresh tokens
2. A checkout flow that turns a cart payload into a correct, immutable receipt
3. Discounts — fixed, percent, capped — computed in integer cents with no drift
4. Returns processed against a real receipt, with over-return refused
5. A daily sales report for managers
6. Django Admin customized so a manager can browse receipts unaided
7. Compose running `api` + `postgres` + `redis`

**Proof it is correct**
8. `docs/caching-notes.md` with **real before/after p95 numbers** from `hey`
9. Cache invalidation proven to fire on every write path that touches a price
10. Discount rounding covered by explicit edge-case tests
11. Throttling on `/checkout` verified

**Written artefacts**
12. `docs/cache-stampede-notes.md` — the risk, and the mitigations you did not build
13. The framework-choice rationale, written down while the reasons are fresh

---

## 3. Scope

**In scope**
- Cart building and checkout
- Discount rules: fixed / percent, with an optional cap
- Receipts and returns
- Daily sales summary
- Redis cache-aside on product search, with correct invalidation
- Rate limiting on checkout
- Access + refresh token auth

**Out of scope — named, with the reason**

| Deferred | Why |
|---|---|
| Idempotency key on checkout | The real treatment arrives in PayFlow (Phase 6). Note the gap here |
| Discount stacking rules | Combinatorial complexity with no learning payoff |
| Receipt PDF generation | Presentation, not backend learning |
| Real payment gateway | Mocked; PayFlow does this properly |
| **Background jobs** | Deliberately none. The next project's slow synchronous email is what earns Celery |
| Offline-first local queuing + background sync | What real POS systems do — worth an interview note, out of scope for a backend bootcamp |

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`cashier`** | Search products, build carts, check out, process returns, print receipts | View any report; access Django Admin |
| **`manager`** | Everything a cashier can, plus the daily sales report and Django Admin access to browse receipts and their items | Change product prices without an audit trail *(if you add one)* |

**Auth:** `simplejwt` with **access + refresh tokens** — the nuance deliberately
deferred in Phase 1. DRF permission classes enforce roles at the viewset level.

Be ready to explain: what goes in an access token, what goes in a refresh token,
and why short-lived access tokens matter even over HTTPS.

---

## 5. Functional Modules

### 5.1 Catalogue (`catalog` app)
Products with SKU, name, price in cents, and a tax rate. Registered in Django
Admin. This is also the app whose read endpoint gets cached.

### 5.2 Discounts (`discounts` app)
A discount is fixed or percent, optionally capped. Validation rules live in the
model and are unit-tested — a percent discount above 100, a negative value, or a
cap on a fixed discount are all rejected.

### 5.3 Sales (`sales` app)
The checkout service turns a cart payload into a receipt:

```
for each line:   line_total = unit_price × qty
                 apply line discount (capped)
apply cart-level discount (capped)
compute tax per line at the product's rate
sum → grand total
```

All of it in integer cents. The receipt captures `unit_price_cents` at sale time
so a later price change never rewrites a past sale.

### 5.4 Returns
A return references a receipt and a reason. It cannot exceed the quantity sold on
that receipt.

### 5.5 Reporting
Daily sales for a given date: gross, discounts, tax, net, count of receipts.

---

## 6. Domain Model

```
products(id, sku, name, price_cents, tax_rate)

discounts(id, code, type[fixed|percent], value, max_cap_cents NULL)

receipts(id, cashier_id -> users.id, status, created_at)

receipt_items(id, receipt_id -> receipts.id, product_id -> products.id,
              qty, unit_price_cents, discount_id NULL)

returns(id, receipt_id -> receipts.id, reason,
        processed_by -> users.id, created_at)
```

**Money rule, carried from Project 1:** all money is integer cents. Discounts and
tax are computed with integer arithmetic — **never floats**. This is exactly
where rounding bugs live, and where an interviewer will poke.

**Immutability:** a receipt is a historical record. `unit_price_cents` is copied
onto `receipt_items` at checkout. Nothing recomputes a past receipt.

---

## 7. Database Design

| Index | Reason |
|---|---|
| `products.sku` | Lookup during checkout |
| `receipts.created_at` | Daily sales report range scan |
| `receipt_items.receipt_id` | Receipt detail fetch |

**Django Admin** is customized — list display, filters, search, inline receipt
items — so a manager can work without an API client. This customization *is* the
justification for choosing Django; if you skip it, the choice was arbitrary.

---

## 8. API Design

| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/auth/token` | public | simplejwt: access + refresh |
| POST | `/auth/token/refresh` | public | |
| GET | `/products?search=` | cashier+ | **Redis cache-aside**, short TTL |
| POST | `/checkout` | cashier+ | Cart payload → receipt. **Throttled** |
| GET | `/receipts/{id}` | cashier+ | |
| POST | `/returns` | cashier+ | Against an existing receipt |
| GET | `/reports/daily-sales?date=` | manager | |

---

## 9. Business Rules (invariants)

1. All money arithmetic in integer cents; rounding is deterministic and specified.
2. A percent discount never exceeds `max_cap_cents` when a cap is set.
3. A return references a real receipt and cannot exceed the quantity sold.
4. Cache invalidation fires on **every** write path that can change
   `price_cents` — including admin edits, not just the obvious API route.
5. `/checkout` is throttled so a buggy client cannot double-submit a sale.
6. A receipt is immutable once created.

---

## 10. Architecture

Django project, DRF `ViewSet`s, **service functions called from viewsets.**

The Django idiom "fat models, thin views" is **deliberately rejected** in favour
of the same service-layer discipline as Phase 1. You must be able to argue why:
testability without the ORM, framework-agnostic business rules, and no god-model
that every app imports.

```
quickserve/
  config/          # Django settings, base/dev/prod split
  apps/
    catalog/       # products; models + admin.py customization
    sales/         # receipts, checkout service, viewsets
    discounts/
  services/        # cross-app business logic, framework-agnostic where possible
  tests/
```

**Settings split** (base/dev/prod) from day one — not one `settings.py` with
`if DEBUG` scattered through it.

---

## 11. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL** | Everything | |
| **Redis — cache** | `GET /products?search=` only. Cache-aside: check → miss → query → populate with a short TTL. Invalidated on any write to `price_cents` | During a rush the same search runs over and over, returning identical rows. This is the *felt* problem, measured before and after |
| **Redis — throttle counters** | DRF `UserRateThrottle` on `/checkout` | DRF throttling is cache-backed; know that it is Redis doing the counting |
| **`fakeredis`** | Unit tests | So the suite does not silently depend on a real Redis being up |
| **Docker Compose** | `api` + `postgres` + **`redis`** | |
| **GitHub Actions** | Same lint / typecheck / test gate as Phase 1, now against Postgres **and** Redis service containers | |
| **`hey`** | Benchmarking `GET /products?search=` before and after the cache | The numbers in `docs/caching-notes.md` |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Celery / a broker** | The next project's synchronous approval email is what earns it. Adding it here would waste the lesson |
| **Cache on `/checkout` or `/receipts/{id}`** | Writes and immutable single-row reads. Nothing to gain, correctness to lose |
| **Nginx / gateway** | Still one service |
| **Prometheus** | Log the cache hit/miss ratio as a structured field for now; dashboards arrive in Phase 4 |

---

## 12. Caching Design (the centrepiece)

`GET /products?search=` hit repeatedly during a rush is identical work every time.

| Aspect | Decision |
|---|---|
| Pattern | **Cache-aside** (read-through on miss) |
| Key | Normalized search term + page |
| TTL | Short — seconds to a couple of minutes |
| Invalidation | On product price update, from **every** write path |
| Testing | `fakeredis` in unit tests, real Redis in integration tests |
| Observability | Cache hit/miss ratio logged as a structured field |
| Deliverable | `docs/caching-notes.md` with real before/after p95 |

**Cache stampede** — many misses at once when a popular key expires — is
documented as a risk with proposed mitigations (jittered TTL, or a lock around
cache population). **Written, not implemented.** A deliberate Phase 5 callback.

**The invalidation audit matters more than the cache.** Spend a day (D36 exists
for this) tracing every code path that can change a price: the API route, the
Django Admin form, a data migration, a management command. A cache with one
uninvalidated write path is worse than no cache, because it fails silently.

---

## 13. Build Plan (consolidated)

### Stage 1 — Django scaffold & models *(D25–D30, Week 5)*
- New repo `quickserve/`, Django project init, **settings split** (base/dev/prod)
- `catalog` app: `Product` model + admin registration
- `sales` app: `Receipt`, `ReceiptItem` models
- `discounts` app: `Discount` model + validation rules
- DRF serializers for products and receipts
- Review pass: find FastAPI habits carried over wrongly into Django idioms

*Done when:* `manage.py check` passes, migrations apply, discount validation is
unit-tested.

### Stage 2 — Checkout & caching *(D31–D36, Week 6)*
- `ProductViewSet` + `GET /products?search=`
- `checkout_service.py` — cart payload → receipt (line totals, discounts, tax,
  grand total), all integer cents
- `POST /checkout` wired end to end
- **Redis cache-aside** on product search, with TTL and invalidation
- Benchmark with `hey`; record p95 before/after in `docs/caching-notes.md`
- **Invalidation audit:** does every write path to `price_cents` invalidate?

*Done when:* checkout works end to end, cache hit/miss is tested both ways, and
the benchmark numbers are written down.

### Stage 3 — Returns, reports, auth hardening *(D37–D39, Week 7)*
- Wire refresh-token auth into QuickServe
- `UserRateThrottle` on `/checkout`
- `POST /returns` with over-return rejection
- `GET /reports/daily-sales?date=`
- `docs/cache-stampede-notes.md`

---

## 14. Testing Strategy

| Layer | What |
|---|---|
| **Unit** | Discount calculation: fixed, percent, capped, rounding at the half-cent, zero-value, 100%. **This is where the bugs are** |
| Unit | Tax computed per line at the product's rate, not on the discounted cart total by accident |
| Unit | Cache hit and cache miss paths with `fakeredis` |
| Integration | Checkout end to end against real Postgres + real Redis |
| Integration | Return against a receipt, including over-return rejection |
| **Invalidation** | Update a price through each write path, assert the cache was cleared each time |
| Throttle | Rapid repeated `/checkout` gets throttled |
| Serializer | Validation tests on products and receipts |
| Migration | Every migration up and down |
| Benchmark | `hey` against the cached endpoint, cold and warm |

---

## 15. Definition of Done

- [ ] All endpoints implemented and tested
- [ ] Discount math correct in integer cents, edge cases covered
- [ ] Cache-aside working; invalidation proven on **every** price write path
- [ ] `docs/caching-notes.md` with real benchmark numbers
- [ ] Throttling on `/checkout` verified
- [ ] Refresh-token flow working
- [ ] Django Admin genuinely usable by a manager
- [ ] `docs/cache-stampede-notes.md` written
- [ ] Framework-choice rationale written down
- [ ] CI green against Postgres + Redis

---

## 16. Interview Questions This Project Should Let You Answer

1. Cache-aside vs write-through — which did you use and why?
2. How do you invalidate the cache correctly when a price changes, and how do you
   know you found every write path?
3. What is a cache stampede and how would you prevent one?
4. Why Django here but FastAPI in Project 1 — how do you decide?
5. Access token vs refresh token — what goes in each, and why do short-lived
   access tokens matter even over HTTPS?
6. How does DRF throttling work under the hood?
7. Why integer cents, and what does a float discount bug actually look like?
8. Why is a receipt immutable, and what breaks if it is not?
9. You rejected "fat models, thin views" — defend that.

---

## 17. Common Mistakes to Watch For

- Caching without a clear invalidation story
- Forgetting `fakeredis` in unit tests and accidentally depending on a live Redis
- Rounding discounts with floats instead of integer cents
- Letting business logic slide into viewsets because "Django does it that way"
- Reading the product's current price when displaying an old receipt
- Benchmarking the cache with a warm cache only, and reporting the flattering number

---

## 18. How Real Companies Differ

Production POS systems often run checkout **fully offline-first**, with local
queuing and background sync, because a shop cannot stop selling when the network
drops. Worth naming in an interview; out of scope for a backend-focused bootcamp.
