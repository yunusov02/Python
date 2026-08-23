# PHASE 2 — Concurrency + Django/DRF + Caching
### Weeks 5–8 · 24 working days

---

## 1. Learning Goals
- Explain the GIL precisely enough to know *when* threading helps (I/O-bound)
  vs when it doesn't (CPU-bound), and reach for multiprocessing correctly.
- Build a real Django/DRF service — not a CRUD tutorial, but one where you
  can explain *why* Django beats FastAPI here (admin panel, ORM migrations,
  batteries for admin-heavy back-office tools).
- Introduce Redis at the exact moment a synchronous endpoint gets slow under
  load — cache-aside pattern, invalidation, TTL tradeoffs.
- Introduce Celery once you've felt the pain of a slow synchronous email/
  notification call blocking a request.
- Implement real rate limiting and OAuth2 refresh-token flow.

## 2. Technologies Introduced
Django, Django REST Framework, `threading`, `multiprocessing`, `ThreadPoolExecutor`/
`ProcessPoolExecutor`, Locks/Queues/race conditions, Redis (cache-aside),
Celery + Redis broker, DRF throttling, `djangorestframework-simplejwt`
(access + refresh), OAuth2 concepts.

Deliberately not yet: RabbitMQ/Kafka, Kubernetes, monitoring stack, CQRS.

---

## 3. PROJECT 2 — QuickServe POS (Point-of-Sale System)

**Business Problem:** A retail cashier needs a fast checkout flow — scan/
select items, apply per-item or cart-level discounts, compute tax, take a
mock payment, issue a receipt, and process returns — with a manager able to
see daily sales totals without touching the database directly.

**Requirements**
- Functional: cart building, discount rules (fixed/percent, capped),
  checkout → receipt, returns against a receipt, daily sales summary.
- Non-functional: checkout endpoint must stay fast under repeated identical
  product lookups (this is the felt problem that justifies Redis); cashier
  and manager roles.

**Architecture:** Django project, DRF `ViewSet`s, service functions called
from viewsets (same layering discipline as Phase 1, adapted to Django's
idioms — "fat models, thin views" is rejected in favor of your service
layer, and you'll be able to argue why).

**ER Diagram (textual)**
```
products(id, sku, name, price_cents, tax_rate)
discounts(id, code, type[fixed|percent], value, max_cap_cents NULL)
receipts(id, cashier_id -> users.id, status, created_at)
receipt_items(id, receipt_id -> receipts.id, product_id -> products.id, qty, unit_price_cents, discount_id NULL)
returns(id, receipt_id -> receipts.id, reason, processed_by -> users.id, created_at)
```

**Folder Structure**
```
quickserve/
  config/                 # Django settings (base/dev/prod split)
  apps/
    catalog/               # products, models + admin.py customization
    sales/                 # receipts, checkout service, viewsets
    discounts/
  services/                # cross-app business logic, framework-agnostic where possible
  tests/
```

**API Design**
```
GET  /products?search=
POST /checkout                 # cart payload -> receipt
GET  /receipts/{id}
POST /returns
GET  /reports/daily-sales?date=
```

**Database Design:** index `products.sku`, `receipts.created_at`; Django
admin customized so a manager can browse receipts without an API client —
this is explicitly *why* Django was chosen for this project.

**Authentication & Permissions:** `simplejwt` with access + refresh tokens
now (the nuance deferred in Phase 1). DRF permission classes: `cashier` can
checkout/return, `manager` can view reports.

**Caching (introduced here, deliberately):** `GET /products?search=` hit
repeatedly during a rush is identical work every time. Cache-aside with
Redis: check cache → miss → query → populate cache with a short TTL →
invalidate on product price update. You will benchmark before/after with
`hey` and record the p95 improvement in `docs/caching-notes.md`.

**Background Jobs:** still none — explicitly deferred to Project 3, where a
slow synchronous email call becomes the trigger for Celery.

**Rate Limiting:** DRF `UserRateThrottle` on `/checkout` (prevent a buggy
client from double-submitting a sale).

**Infrastructure:** Docker Compose gains a `redis` service alongside `api` +
`postgres`.

**CI/CD:** same lint/typecheck/test gate as Phase 1, now running against
Postgres *and* Redis service containers.

**Testing Strategy:** unit tests on discount calculation logic (this is
where off-by-one/rounding bugs live — test them explicitly), integration
tests on checkout end-to-end, a cache-hit/cache-miss test using a fake Redis
(`fakeredis`) in unit tests and real Redis in integration tests.

**Monitoring:** structured logging continues; log cache hit/miss ratio as a
field for now (real metrics dashboards arrive Phase 4).

**Deployment:** same single-VPS Compose deploy as Phase 1.

**Scaling Strategy:** notes on cache stampede risk (many cache-misses at
once after TTL expiry) and how you'd mitigate it (jittered TTL, or a lock
around cache population) — written, not yet implemented; a concrete Phase 5
callback.

**Common Interview Questions**
1. Cache-aside vs write-through — which did you use and why?
2. How do you invalidate the cache correctly when a price changes?
3. What's a cache stampede and how would you prevent one?
4. Why Django here but FastAPI in Project 1 — how do you decide?
5. Access token vs refresh token — what goes in each, and why short-lived
   access tokens matter even with HTTPS?
6. How does DRF throttling work under the hood (cache-backed counters)?

**Possible Improvements:** idempotency key on checkout, discount stacking
rules, receipt PDF generation, real payment gateway integration.

**What Companies Usually Do Differently:** production POS systems often
run checkout fully offline-first with local queuing and background sync —
worth a note for interviews, not built here (offline-first is out of scope
for a backend-focused bootcamp).

**Common Mistakes:** caching without a clear invalidation story; forgetting
`fakeredis` in unit tests and accidentally depending on a real Redis being
up; rounding discounts with floats instead of integer cents.

---

## 4. PROJECT 3 (starts) — PeopleOps: HR & Leave Management

**Business Problem:** An office of ~50 staff needs leave requests routed to
a manager for approval, accurate leave-balance tracking (accrued monthly),
and email notification on approval/rejection — currently done over Slack
DMs with no audit trail.

*(Full spec — ER diagram, API design, background-job design — lands in
Phase 3's file, since Celery is introduced in Week 7 of this phase and the
project is genuinely split across Phase 2/3. This phase covers scaffold +
the auth/permissions/domain-modeling groundwork only.)*

**What you build in Phase 2 specifically:** Django project scaffold, `Employee`/
`LeaveRequest`/`LeaveBalance` models, manager-approval permission logic, and
the felt problem that ends this phase: sending an approval email
*synchronously* inside the request makes `/leave-requests/{id}/approve`
slow and occasionally fails the whole request if the mail server hiccups.
You'll write this pain down explicitly on Day 20 — it's the setup for
Celery in Phase 3.

---

## 5. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| GIL demo: CPU-bound task timed — threads vs processes vs single-thread | 5 | GIL, when threading doesn't help |
| Multithreaded file downloader (I/O-bound, threads *do* help) | 5 | `ThreadPoolExecutor`, I/O concurrency |
| Multiprocessing image resizer (`ProcessPoolExecutor`) | 6 | CPU-bound parallelism, process overhead |
| Redis cache-aside mini demo (standalone script) | 6 | Cache patterns before applying to QuickServe |
| Producer/consumer with `queue.Queue` + `threading.Lock` | 7 | Race conditions, locks, deadlock avoidance |
| Custom LRU cache decorator (`functools.lru_cache` reimplemented) | 7 | Ties back to Phase 1 decorators |
| Celery producer/consumer mini task queue | 8 | Task queues, retries, before applying to PeopleOps |

---

## 6. Books & Documentation
- *Fluent Python* Ch. 19–21 (concurrency chapters) — read across Weeks 5–6.
- David Beazley's "Understanding the GIL" talk notes/slides.
- Django docs: Models, Admin, Migrations. DRF docs: ViewSets, Permissions,
  Throttling.
- Redis docs: caching patterns page.
- *Two Scoops of Django* — chapters on settings split and app structure.

---

## 7. Weekly Interview Question Sets

**Week 5 — GIL, threading, multiprocessing**
1. What exactly does the GIL prevent, and what does it *not* prevent?
2. Why does adding threads speed up a file-download script but not a
   prime-number-crunching script?
3. `ThreadPoolExecutor` vs `ProcessPoolExecutor` — memory-sharing implications?
4. What's a race condition — minimal reproducible example?
5. Deadlock — the four conditions, and one way to break one of them.

**Week 6 — Django/DRF, Redis**
1. Django ORM vs SQLAlchemy — one real tradeoff, not a preference.
2. What does `select_related` vs `prefetch_related` fix, and when does
   each apply?
3. Cache-aside vs write-through vs write-behind.
4. What determines a good Redis TTL for a given endpoint?
5. How does DRF's permission class chain execute?

**Week 7 — JWT refresh, throttling, queues**
1. Why rotate refresh tokens, and what's the risk if you don't?
2. How would you rate-limit per-user vs per-IP, and when does each matter?
3. Why does an unbounded `queue.Queue` risk memory blowup, and how do you
   bound it safely?
4. When would you choose a `Lock` over a `Semaphore`?
5. What's the actual permission check that stops a non-manager from
   approving a leave request, and where does it live?

**Week 8 — Celery, idempotent tasks, review**
1. Why are synchronous side-effects inside a request dangerous — what's
   the concrete failure mode you measured this week?
2. What happens to a Celery task if the worker crashes mid-execution?
3. At-least-once vs exactly-once task delivery — how does `retry(3)`
   relate to making the email task idempotent?
4. How would you make a monthly accrual calculation safe to run twice
   without double-crediting an employee?
5. Walk through your CI pipeline now that Redis and a Celery worker are
   required service containers — what would break if either were missing?

---

## 8. Daily Plan — Week 5: GIL, Threading, Multiprocessing, Django Scaffold

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D25) | GIL mechanics | Fluent Python Ch.19 | GIL demo script (threads vs processes, CPU-bound) | New repo `quickserve/`, Django project init, settings split | Confirm `manage.py check` passes | `chore: django project scaffold` | Q1 | Evaluate Reverse Polish Notation | QuickServe: daily revenue per cashier | 3.5h |
| Tue (D26) | `threading` module, I/O-bound concurrency | Python docs `threading` | Multithreaded file downloader | `catalog` app: `Product` model + admin registration | Model field test | `feat: product model + admin` | Q2 | Generate Parentheses | Department Highest Salary | 3.5h |
| Wed (D27) | `multiprocessing`, process overhead | Python docs `multiprocessing` | Multiprocessing image resizer with `Pool` | `sales` app: `Receipt`, `ReceiptItem` models | Migration test | `feat: receipt models` | Q3 | Daily Temperatures | QuickServe: receipts with at least one return | 3.5h |
| Thu (D28) | Race conditions, minimal repro | — | Deliberately trigger a race with 2 threads incrementing a shared counter | `discounts` app: `Discount` model + validation rules | Unit test discount calc (fixed/percent, cap) | `feat: discount model + calc rules` | Q4 | Car Fleet | QuickServe: products never discounted | 3.5h |
| Fri (D29) | Locks, deadlocks (4 conditions) | — | Fix Thursday's race with a `Lock`; then reproduce a deadlock on purpose | DRF serializers for products/receipts | Serializer validation tests | `feat: DRF serializers` | Q5 | Binary Search | Trips and Users | 3.5h |
| Sat (D30) | **Review** | — | Redo GIL demo from memory, explain results out loud | Re-read models for Django idioms vs FastAPI habits carried over wrongly | Full suite | — | Answer all Week-5 Qs unscripted | Review: redo Thursday's problem from memory — Car Fleet | Review: rewrite Tuesday's query from memory, then extend it — Department Highest Salary | 2.5h |

---

## 9. Daily Plan — Week 6: DRF ViewSets, Checkout Flow, Redis Caching

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D31) | DRF ViewSets, routers | DRF docs Viewsets | — | `ProductViewSet` + `GET /products?search=` | Integration test | `feat: product list/search endpoint` | Q1 | Search a 2D Matrix | QuickServe: rank products by qty sold | 3.5h |
| Tue (D32) | Service layer in Django (keeping views thin) | Two Scoops Ch.7 | — | `checkout_service.py`: build receipt from cart payload | Unit test checkout math | `feat: checkout service` | Q2 | Koko Eating Bananas | QuickServe: running total of daily sales | 3.5h |
| Wed (D33) | `select_related`/`prefetch_related`, N+1 in Django ORM | Django docs QuerySet | Reproduce N+1 on receipt-items listing, fix it | `POST /checkout` endpoint wired end-to-end | Integration test full checkout | `feat: checkout endpoint` | Q3 | Find Minimum in Rotated Sorted Array | Rank Scores | 3.5h |
| Thu (D34) | Redis cache-aside pattern | Redis docs caching | Standalone cache-aside demo script | Add Redis cache on `GET /products?search=`, TTL + invalidation on price update | Cache hit/miss test with `fakeredis` | `feat: redis cache-aside on product search` | Q4 | Search in Rotated Sorted Array | QuickServe: EXPLAIN ANALYZE the cached product-search query | 3.5h |
| Fri (D35) | Benchmarking, `hey`/`locust` basics | — | Load-test `/products` before/after cache, record p95 | Write `docs/caching-notes.md` with before/after numbers | — | `perf: benchmark cache impact` | Q5 | Warm-up: implement a singly linked list from scratch; Reverse Linked List | Consecutive Numbers | 3.5h |
| Sat (D36) | **Review** | — | Redo cache-aside demo from memory | Re-check invalidation covers every write path to `price_cents` | Full suite | — | Answer all Week-6 Qs unscripted | Review: redo Thursday's problem from memory — Search in Rotated Sorted Array | Review: rewrite Tuesday's query from memory, then extend it — QuickServe: running total of daily sales | 2.5h |

---

## 10. Daily Plan — Week 7: Returns, Reports, JWT Refresh, Queues → PeopleOps Starts

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D37) | `simplejwt` access/refresh flow | djangorestframework-simplejwt docs | — | Wire refresh-token auth into QuickServe | Test token refresh + rotation | `feat: jwt access+refresh auth` | Q1 | Merge Two Sorted Lists | PeopleOps: employees with more than 3 pending leave requests | 3.5h |
| Tue (D38) | DRF throttling internals | DRF throttling docs | — | Add `UserRateThrottle` to `/checkout` | Test throttle triggers at limit | `feat: checkout rate limiting` | Q2 | Reorder List | Managers with at Least 5 Direct Reports | 3.5h |
| Wed (D39) | Returns flow, daily sales report query | — | — | `POST /returns`, `GET /reports/daily-sales` | Integration tests, tag `v0.1-quickserve` | `feat: returns + daily sales report` | Q3 | Remove Nth Node From End of List | PeopleOps: average leave balance per department | 3.5h |
| Thu (D40) | `queue.Queue`, producer/consumer pattern | Python docs `queue` | Producer/consumer mini script with `Lock` | New repo `peopleops/`: Django scaffold, `Employee`, `LeaveRequest`, `LeaveBalance` models | Model tests | `feat: peopleops scaffold + core models` | Q4 | Copy List with Random Pointer | PeopleOps: leave requests approved same-day vs delayed | 3.5h |
| Fri (D41) | Manager-approval permission modeling | DRF permissions docs | — | `LeaveRequestViewSet` + approve/reject actions, manager-only permission | Permission tests (staff can't approve) | `feat: leave request approval flow` | Q5 | Add Two Numbers | Employee Bonus | 3.5h |
| Sat (D42) | **Review** | — | Redo producer/consumer from memory | Trace the approval endpoint's synchronous email call — note exactly where it blocks | Full suite | — | Answer all Week-7 Qs unscripted | Review: redo Thursday's problem from memory — Copy List with Random Pointer | Review: rewrite Tuesday's query from memory, then extend it — Managers with at Least 5 Direct Reports | 2.5h |

---

## 11. Daily Plan — Week 8: The Synchronous-Email Pain Point, Celery Intro, Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D43) | Why synchronous side-effects in a request are dangerous | — | Time the approval endpoint with a deliberately slow fake mail server (`time.sleep`) | Write `docs/blocking-email-problem.md` documenting the felt pain, numbers included | — | `docs: document blocking email problem` | Q1 | Linked List Cycle | PeopleOps: employees who never took leave | 3.5h |
| Tue (D44) | Celery architecture: broker, worker, result backend | Celery docs "First Steps" | Celery producer/consumer mini task queue (`add.delay()`) | Add `celery.py` app config + Redis broker to `peopleops/` | Test a trivial task executes async | `feat: celery + redis broker wired up` | Q2 | Find the Duplicate Number | PeopleOps: leave requests pending 3+ days | 3.5h |
| Wed (D45) | Task retries, idempotent tasks | Celery docs retries | — | Convert approval-email send into a Celery task with retry(3) | Test task retries on simulated failure | `feat: async email task with retries` | Q3 | LRU Cache | Investments in 2016 | 3.5h |
| Thu (D46) | Leave balance accrual logic | — | — | `LeaveBalance` accrual calculation (manual trigger for now — cron comes Phase 3) | Unit test accrual math | `feat: leave balance accrual logic` | Q4 | Invert Binary Tree | PeopleOps: monthly accrual totals per employee | 3.5h |
| Fri (D47) | Phase 2 wrap: CI update (add Redis+Celery to pipeline) | GitHub Actions docs | — | Full CI green on both projects, Docker Compose gains `redis` + `celery-worker` services | Full suite both projects | `ci: add redis + celery worker to pipeline` | Q5 | Maximum Depth of Binary Tree | Sales Person | 3.5h |
| Sat (D48) | **Phase 2 wrap review** | — | Redo Celery retry demo from memory | Write `docs/postmortem-phase2.md` | Tag `v0.2-phase2` | `docs: phase 2 postmortem` | Mock-answer all 20 Phase-2 questions timed | Review: redo Thursday's problem from memory — Invert Binary Tree | Review: rewrite Tuesday's query from memory, then extend it — PeopleOps: leave requests pending 3+ days | 2.5h |

---

## 12. Deliverables & GitHub Milestones

**Milestone: `Phase 2 — QuickServe v0.1 + PeopleOps v0.1`**
- [ ] QuickServe: checkout, returns, daily sales report, Redis-cached search
- [ ] Redis cache-aside benchmarked with before/after numbers
- [ ] `simplejwt` access+refresh flow, DRF throttling on checkout
- [ ] PeopleOps: employee/leave models, approval flow, first Celery task
- [ ] `docs/blocking-email-problem.md` and `docs/caching-notes.md` written
- [ ] CI green with Postgres + Redis + Celery worker service containers
- [ ] Tag: `v0.2-phase2`

## 13. Skills Acquired Checklist
- [ ] GIL, threading vs multiprocessing — correct tool selection
- [ ] Locks, race conditions, deadlocks — identified and fixed firsthand
- [ ] Django/DRF: models, admin, viewsets, serializers, permissions, throttling
- [ ] Redis cache-aside pattern with measured impact
- [ ] JWT access+refresh token flow
- [ ] Celery basics: tasks, retries, broker/worker architecture
- [ ] Recognizing when a synchronous request-path side-effect needs to move
      to a background job — from firsthand pain, not a rule

---

**Next:** Phase 3 continues PeopleOps (cron scheduling, notifications) and
starts WareFlow, introducing RabbitMQ, Unit of Work, and advanced Postgres.
