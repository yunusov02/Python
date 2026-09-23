# Stage 01 — Layered monolith: vendors, catalog, identity v1

| | |
|---|---|
| **Weeks** | W3–W6 (4 weeks) |
| **Hours** | 48 must + 6 stretch (54 total) |
| **Architecture at start → at end** | the `market` skeleton on PG17 → `market` as a layered monolith with the `identity`, `vendors` and `catalog` apps, on PG17 + the S3-compatible object store (Garage) |
| **New technologies** | Django 5.2 (apps, ORM, Admin, migrations), DRF 3.18 (serializers, viewsets, routers, permissions), simplejwt, argon2, pytest-django, testcontainers, factory_boy, Hypothesis, import-linter, S3 presigned URLs (Garage), psycopg COPY; Postgres composite / partial / covering / expression / GIN / GiST indexes, `EXCLUDE`, recursive CTE, JSONB, UUIDv7 |
| **Portfolio tag** | `v0.1` |
| **Old-spec theory to read** | [P1 D7–D18](../python/01-stockpilot.md) (layers D7–D12, recursive CTE, `Repository[T]` D14, Money D15, rejected descriptors D16, EXPLAIN D17, keyset); [P2 D25–D39](../python/02-quickserve-pos.md) (Django/DRF scaffold, service layer D32, N+1 D33, simplejwt D37, throttling internals D38); [P5 D79–D90](../python/05-carepoint.md) (argon2, lockout, enumeration, `EXCLUDE` D79–D84; presigned URLs D85–D90); [P7 D109–D114](../python/07-fleettrack.md) (JSONB + GIN `jsonb_path_ops`, partial index); also [P4 D67–D71](../python/04-wareflow.md) (covering index, Heap Fetches 0) and [P3 D40–D41](../python/03-peopleops.md) (relationship permissions) |

Version pins in this file are as of 2026-09. Re-check them with `scripts/compat_check.sh` before you start (ADR-001). This stage adds the S3-compatible object store. The default is **Garage**, with SeaweedFS as the fallback: MinIO stopped publishing community images in 2025 and archived its repository in 2026, so `minio/minio` no longer pulls [C, as of 2026-09].

> **What this stage is really for.** You learn Django properly (not by guessing from FastAPI habits), continuing from the S0 orientation, and build the first third of a marketplace: ops onboard vendors, vendors publish products, customers browse a million of them. The real product of the stage, though, is a habit: **every Postgres claim is backed by a committed plan**, and every rule that must never break is enforced by the database or by a contract the CI checks. You also plant two deliberate defects (the HS256 token without rotation and the in-memory login limiter) that later stages fix with numbers.

---

## 1. The problem this stage starts from

**Business terms.** Atlas has a skeleton and nothing to sell. A marketplace needs, in this order: people (customers, vendor staff, ops) who can log in; vendors that ops have checked (KYC, "know your customer": verifying a business's identity documents before it may sell); and a catalog that customers can browse and filter quickly, even at a million products.

**Engineering terms.**
- [Stage 00](stage-00-bootstrap.md) left a Django project with no apps, no domain and no data.
- You know FastAPI + SQLAlchemy from StockPilot Day 1–5. Django you have met only in the S0 orientation (tutorial parts 1–2, settings, the deployment checklist). Without a deliberate ramp you would write FastAPI-shaped code inside Django and fight the framework.
- Nothing yet stops a view from querying the database directly, a float from entering money code, or a migration that cannot be reversed.
- There is no data volume, so no query has ever been slow. A catalog of 1M products will make the planner's choices visible, and every index must be earned from a plan you ran.

## 2. Outcomes — what exists when the stage is finished

1. `sandbox/django-ramp/` with the rest of the official tutorial and the DRF quickstart done, and the mapping table in `docs/learning/fastapi-to-django.md` filled in.
2. Three Django apps (`identity`, `vendors`, `catalog`) layered as **views → services/selectors → ORM**, with an import-linter contract proving views never touch the ORM, Protocol-typed ports, mypy strict on the domain and a manual composition root.
3. Vendor onboarding with KYC documents in the private `atlas-kyc` bucket via presigned URLs (authorized before minting, TTL ≤ 5 min), and a customized Admin KYC queue ops actually use.
4. A catalog: a category tree (recursive CTE with a cycle guard), products and offers, per-category JSONB attributes with a GIN index for facets, presigned image uploads to `atlas-media`, and a public catalog API.
5. A frozen `Money(tiyin, currency)` value object and a `MoneyField` custom model field whose **descriptor** returns `Money`, with Hypothesis properties and a "no float in money code" test.
6. Eight Postgres proofs, each with a committed plan or measurement in `docs/perf/s1.md` and `docs/evidence/s01/`.
7. Identity v1: custom User (bigint PK plus UUIDv7 public id, email, +998 phone, argon2), session + CSRF for Admin, simplejwt HS256 access/refresh (missing rotation recorded as a gap), enumeration-safe login with `login_attempts` lockout, roles plus relationship permissions proven by crafted requests, and the **4× in-memory limiter recorded**.
8. `atlas-worldgen` v1 seeding 1M products through COPY.
9. ADR-004 (layering), ADR-005 (IDs), ADR-006 (money and rounding); an SD6 session.
10. Stage close: tag `v0.1`, postmortem paragraph, 2 STAR stories.

## 3. Architecture at the end of the stage

```
   browser (Django Admin: session + CSRF)          API clients (JWT HS256 access/refresh)
                 │                                               │
                 ▼                                               ▼
 ┌─────────────────────────── market (Django 5.2 + DRF, gunicorn 4 workers) ───────────────────────────┐
 │                                                                                                      │
 │   views / viewsets / Admin      ← may import only services and selectors (import-linter)            │
 │            │                                                                                         │
 │   services (writes) · selectors (reads)   ← the only code that uses the ORM                          │
 │            │               │                                                                         │
 │   domain (pure Python, mypy --strict): Money, commission rules, category-tree rules, vendor states  │
 │            │                                                                                         │
 │   ports (Protocols): ObjectStorage, Clock, Repository[T] … wired in a manual composition root        │
 │                                                                                                      │
 │   apps:  identity  ·  vendors  ·  catalog                                                            │
 │   in-memory login limiter (per worker!)  →  effective limit 4×   [known defect, fixed in S3]         │
 └───────────────┬──────────────────────────────────────────────┬───────────────────────────────────────┘
                 │ SQL                                          │ mints presigned PUT/GET (TTL ≤ 5 min)
                 ▼                                              ▼
   PG17 `market`: identity_user, login_attempts,        Garage (S3 API): atlas-kyc (private), atlas-media
   vendors_*, catalog_* (1M products), EXCLUDE,                   ▲
   GIN/GiST/partial/covering/expression indexes                  │ bytes go straight from the client,
                                                                 └─ never through market
```

**What changed and why.**
- *Django apps with an enforced layer order.* Business rules live in one place (services and domain), so the back office (Admin) and the API cannot disagree, and later extractions (S9, S10) move services, not views.
- *An S3-compatible object store (Garage) joins as the first object store,* because KYC documents and images are bytes that do not belong in Postgres or in the request path. Code only sees the `ObjectStorage` port and `S3_*` settings, so the product behind it can change.
- *Postgres becomes a design tool,* not a bucket: exclusion constraints, JSONB with GIN, and indexes chosen from plans.

---

## 4. Build plan

### Suggested calendar (48 h over four weeks)

| Week | Blocks | Hours |
|---|---|---|
| W3 | 4.1 Django ramp (7) · 4.2 Layering (3.5) · drill (1) | 11.5 |
| W4 | 4.3 Vendors and KYC (5) · 4.4 Catalog (6.5) · SD6 (1) | 12.5 |
| W5 | 4.5 Money (3) · 4.8 Worldgen v1 (3; the 1M-product load in the weekend block) · 4.6 Postgres proofs 1–4 (5) · drill (1) | 12 |
| W6 | 4.6 Postgres proofs 5–8 (5; the keyset p95 and UUID benchmarks in the weekend block) · 4.7 Identity v1 (6) · drill (1) | 12 |

The block budgets are estimates for a first attempt; log the actual hours per block in `docs/hours.csv`, as in S0. If a block runs over, stop polishing, but finish its acceptance criteria.

Two ordering rules override the block order below:
- **Create the custom User model before the very first `migrate`** (in the Layering block). Changing `AUTH_USER_MODEL` after migrations exist is one of Django's most painful mistakes. The rest of Identity v1 still happens in W6.
- **Run Worldgen v1 before the Postgres proofs.** Plans on a few hundred rows prove nothing.

---

### 4.1 Django ramp [7 h]

**Why this block exists.** Django is opinionated: projects contain apps, querysets are lazy, migrations form a graph, and Admin, sessions and CSRF are built in. Learning it through Atlas's own code would mix two unknowns. The ramp continues in the throwaway `sandbox/django-ramp/` you started in [S0 §4.0](stage-00-bootstrap.md#40-django-orientation-25-h). Nothing imports it, it is not a workspace member, and it is excluded from strict type checks and coverage.

**The reading and doing path (in order)**

| # | Resource (official docs for Django 5.2 and DRF 3.18) | What to take from it | Budget |
|---|---|---|---|
| 1 | Django tutorial "Writing your first Django app", **parts 1–2**, plus the settings and deployment-checklist reading | Done in the S0 Django orientation (4.0); reread only what you need | — |
| 2 | Tutorial **parts 3–4** | URLconf, views, generic views; how a request becomes a response | 1.5 h |
| 3 | Tutorial **part 5** (testing) and **part 7** (customizing the Admin); skim parts 6 and 8 | Django's test client and database handling; `list_display`, filters, search, inlines | 1 h |
| 4 | DRF **quickstart**, then the DRF tutorial parts **1** (serialization), **2** (requests and responses), **3** (class-based views), **4** (authentication and permissions), **6** (viewsets and routers) | Serializers as validation *and* output; permission classes; routers | 2 h |
| 5 | djangorestframework-simplejwt "Getting started" | Access/refresh endpoints; what the token contains | 0.5 h |
| 6 | Experiments in the sandbox (see below) | The behaviours that bite FastAPI developers | 1.5 h |
| 7 | Complete `docs/learning/fastapi-to-django.md` | The mapping table below, under the five answers from S0 | 0.5 h |

**Sandbox experiments (step 6).** Do each and write one line of what you observed:
1. **Lazy querysets.** Build a queryset, do not iterate it, and check how many queries ran (Django's `connection.queries` in debug mode, or the test framework's query counting). Iterate it twice. Slice it. When exactly does SQL run?
2. **The migrations graph.** Run `showmigrations --plan` and `sqlmigrate` on one migration. Write a data migration with `RunPython` and a reverse function; migrate forward, back and forward again.
3. **Admin.** Register a model with `list_display`, `list_filter`, `search_fields` and one custom action.
4. **Transactions.** Django runs in autocommit by default. Wrap two writes in `transaction.atomic()`, raise inside, and confirm neither survived. What does `ATOMIC_REQUESTS` change, and why will Atlas not turn it on?
5. **Permissions.** Write one DRF permission class that checks an object-level rule (`has_object_permission`) and observe when DRF calls it (and when it does not, for example on list views).

**The concept mapping you must fill in.** Copy this table into `docs/learning/fastapi-to-django.md` and complete every empty row: the Django/DRF equivalent, and the trap (where the analogy breaks). Three rows are filled as examples. The four anchor rows are Pydantic, Session, Alembic and `Depends`; the `Depends` row is yours. Hint: there is no single equivalent; it splits across two or three Django/DRF mechanisms.

| FastAPI / SQLAlchemy concept | Django / DRF equivalent | Where the analogy breaks |
|---|---|---|
| Pydantic request model (validation) | DRF `Serializer` (`is_valid()`, `validated_data`) | A serializer also renders output and can save models; keep it to shape and validation, and put business rules in services |
| `AsyncSession` per request (`Depends(get_db)`) | The Django ORM with one connection per thread, autocommit by default, `transaction.atomic()` for explicit boundaries | There is no session object to pass around; the unit of work is the `atomic()` block, not a session |
| Alembic revision + autogenerate | `makemigrations` → migration files forming a graph per app; `migrate` | Dependencies are per app and form a graph; `RunPython` needs a reverse function or the migration cannot go down |
| `FastAPI()` app object + `uvicorn` | | |
| `APIRouter` + path-operation function | | |
| `response_model` | | |
| `Depends(get_current_user)`, `Depends(require_role(...))` | | |
| `HTTPException` and exception handlers | | |
| Middleware (`@app.middleware("http")`) | | |
| `pydantic-settings` `BaseSettings` | | |
| SQLAlchemy `Mapped[...]` model | | |
| `relationship()` lazy loading; `selectinload` / `joinedload` | | |
| `expire_on_commit`, identity map | | |
| `lifespan` start-up / shutdown | | |
| `BackgroundTasks` | | |
| `TestClient` + `dependency_overrides` | | |
| Automatic OpenAPI docs | | |
| `async def` endpoints | | |
| CORS middleware | | |
| (nothing) | Django Admin | |
| (nothing) | Sessions + CSRF | |

**Acceptance criteria**
- Every sandbox experiment has a one-line observation.
- The mapping table has every row filled, including a trap for each.
- You can explain, without notes, when a queryset hits the database.

---

### 4.2 Layering [3.5 h]

**Terms.** A **service** is a function or class that performs one write use case ("approve vendor", "publish product") inside a transaction. A **selector** is a read-side query function ("published products in category C"). A **port** is a `Protocol` describing something the service needs from outside (object storage, a clock), so tests can supply a fake. A **composition root** is the one place where concrete implementations are chosen and wired together; here it is written by hand, with no dependency-injection library.

**What to build**
- The `identity`, `vendors` and `catalog` Django apps inside `services/market`. Tables are prefixed with the app label (for example `identity_user`, `vendors_vendor`, `catalog_product`); the glossary relies on these prefixes later.
- Inside each app, separate modules or packages for: views/viewsets/Admin, services, selectors, domain (pure Python), and the Django models.
- **Rule:** views, viewsets, serializers and Admin actions call services and selectors only. Only services and selectors use the ORM.
- An **import-linter layers contract** encoding views → services/selectors → models. Guiding question: does a layers contract stop a view from *skipping* a layer and importing models directly? Read the import-linter docs on its contract types; you may need a second contract.
- **Ports as Protocols with generics.** At minimum an `ObjectStorage` port (mint presigned PUT/GET) and a `Clock` port. A generic `Repository[T]` Protocol (the P1 D13–D18 idea) is used wherever a service's rules are unit-tested against an in-memory fake instead of the database.
- **mypy `--strict` on every domain module.** The domain imports nothing from Django. (The rest of `market` keeps the plain mypy run and the Django stubs decision from S0 §4.4.)
- **A manual composition root:** one module that builds services with their concrete adapters (the S3 storage adapter, the system clock). Tests build the same services with fakes.
- **The custom User model** in `identity`, created *before* the first `migrate` (fields can be minimal now; Identity v1 completes it).

**Acceptance criteria**
- import-linter fails CI if a view imports a model (prove it once with a deliberate violation on a branch; save the failing output to `docs/evidence/s01/import-linter-red.txt`).
- At least one service is unit-tested with fakes only, without the database.
- ADR-004 is drafted (section 8).

---

### 4.3 Vendors and KYC [5 h]

**What to build**
- `vendors_vendor` with a status lifecycle, for example `applied → kyc_pending → approved | rejected`, and `suspended` from `approved`. Illegal transitions are refused by the domain, never silently accepted.
- `vendors_vendor_staff`: the **membership** of a user in a vendor with a role (`vendor_owner` or `vendor_staff`). One user can belong to several vendors.
- KYC documents: metadata rows in Postgres; bytes in the private `atlas-kyc` bucket.
  - Upload: the client asks `market` for a **presigned PUT** URL (a time-limited URL that lets the holder upload one object directly to storage without credentials), uploads straight to the object store, then confirms.
  - Download: ops ask for a **presigned GET** URL, minted per click.
  - **Authorize before minting.** A URL is a bearer credential until it expires: whoever holds it can use it. TTL ≤ 5 minutes.
- **The S3-compatible store (Garage by default) added to Compose**, with the two buckets from the glossary (`atlas-kyc` private, `atlas-media`). Before you build on it, verify that presigned PUT and GET work against the image you pinned (a two-line check from a script is enough), and record the result and the pinned tag in ADR-001. If they do not work, switch to SeaweedFS behind the same S3 API. Code and settings name only the `ObjectStorage` port and generic `S3_*` settings, never the product, so the swap is a configuration change.
- **A customized Admin KYC queue:** vendors awaiting review, filters by status and age, a document link that mints a fresh GET URL after a permission check, approve/reject actions that call the vendor service (not the ORM), and a record of who approved and when.
- A `vendors_commission_rate` table (the commission Atlas charges a vendor, in basis points, valid over a time range). The overlap rule for it is proof 4.6.7. S5 uses this schedule to compute application fees at order time.

**Observe first (not a bug to fix, a property to feel)**
1. Mint a presigned GET for a KYC document. Open it in a private browser window where you are not logged in.
2. Observe that it works: storage does not know who you are. Wait past the TTL and try again.
3. Record both results in `docs/evidence/s01/presigned-bearer.md`, with one sentence on why authorization must happen before minting.

Guiding question: a presigned PUT cannot limit the size of the uploaded object; a presigned POST policy can. Which do you need for KYC documents, and why? If you choose POST policies, check that your store supports them before you rely on them [verify on your pinned Garage tag]. Record the answer where ADR-004 describes the `ObjectStorage` port, since it changes the port's contract. (For the demo above, mint with a one-minute TTL so you do not have to wait long.)

**Acceptance criteria**
- Ops approve a vendor from the Admin queue; the approval is attributed to a user.
- A vendor_staff user of vendor A cannot obtain a URL for vendor B's document (test).
- An expired URL is refused (test with a short TTL and the fake clock, or a real wait in an integration test).

---

### 4.4 Catalog [6.5 h]

**What to build**
- **Categories as a tree** (`parent_id`). An endpoint returns a category with all its descendants using a recursive CTE (`WITH RECURSIVE`) that has a **cycle guard**. Choose one guard and justify it in one line; Postgres 14+ offers a `CYCLE` clause, and a `UNION`-based guard with a depth cap is the other common option (the side-by-side comparison is a stretch item). Test on a 4-level tree (every descendant once) and on a deliberately cyclic tree (terminates).
- **Products and offers.** A *product* is the catalog entry (title, description, category, attributes, images, status). An *offer* is a vendor's sellable listing for it (vendor, SKU, price as `Money`, status). In S1 a vendor creates a product together with its first offer; matching several vendors' offers to one shared product is deliberately not built. Stock (S2) and order lines (S2) attach to offers.
- **Per-category attributes in JSONB.** Each category carries an attribute schema (allowed keys and types); a product's attributes are a JSONB document validated against its category's schema in the service. A **GIN index with the `jsonb_path_ops` operator class** serves facet filters written as containment (`@>`). S8 reuses the schema to validate LLM-written descriptions.
- **Presigned image uploads** to `atlas-media`, same pattern as KYC.
- **The public catalog API** (DRF): category listing with facet filters and keyset pagination; product detail with its offers, vendor and category. No authentication is required to browse published products.

**Acceptance criteria**
- A vendor creates a product with an offer, uploads an image, and publishes it; a customer sees it in the category listing.
- Attributes that violate the category schema are rejected with 422, never 500.
- Facet filtering by containment works and is fast at 1M rows (proof in 4.6).

Guiding questions for your notes (they feed an interview question): which facet types can a `jsonb_path_ops` index serve, and which can it not (think numeric ranges)? When would you promote an attribute to a real column?

---

### 4.5 Money [3 h]

**What to build**
- `Money(tiyin: int, currency)` in `atlas-common`: frozen, integer minor units only (1 soum = 100 tiyin), currency code required, arithmetic only between equal currencies, and allocation of an amount into N parts that sum exactly to the total.
- A **`MoneyField` custom model field** in `market` (not in `atlas-common`, which must stay free of Django). It stores integer tiyin in a bigint column, and its **descriptor** (`__get__` / `__set__`) returns and accepts `Money`.
  - A **descriptor** is an object on a class that intercepts attribute access on instances. Django's own related fields and `FileField` work this way.
  - This is the natural use of a descriptor that P1 D13–D18 considered and rejected for Pydantic validators ([../python/01-stockpilot.md](../python/01-stockpilot.md), Stage 3; phase-1 D16).
- **Hypothesis properties:** addition is associative and commutative; adding zero changes nothing; allocation parts always sum to the total and differ by at most 1 tiyin; mixing currencies raises; no operation produces a negative amount from non-negative inputs unless it is subtraction. Pin the seed in CI.
- **A "no float in money code" test** that fails if a float enters any money path (for example: `Money` refuses a float at construction, and a scan of the money modules for float literals or `float(` calls).

Guiding questions:
- Django already calls `from_db_value` when it loads a row. What does `__set__` give you that `from_db_value` does not? (Think about `offer.price = 12.5`.)
- One column (tiyin, with the currency fixed per field) or two columns (tiyin + currency)? Decide in ADR-006.

**Acceptance criteria**
- Assigning a float to a `MoneyField` attribute raises immediately.
- Reading an offer's price returns `Money`, never an `int`.
- The Hypothesis suite passes with the pinned seed.

---

### 4.6 Postgres proofs [10 h]

Each proof follows one shape: **name the query → run it without the index and save the plan → add the index or constraint → save the new plan → add a test that protects it.** Tie every index to a named query; speculative indexes are not allowed (P1 D13–D18). Save plans with `EXPLAIN (ANALYZE, BUFFERS)`; summarise all eight in `docs/perf/s1.md`; raw plans go in `docs/evidence/s01/`.

This block contains about 70 min of unattended benchmark time: the keyset p95 (3 runs × ≈11 min) and the UUID insert runs (2 key types × 3 runs of 1M inserts, roughly 30–40 min on a laptop depending on how you insert). Schedule both in the weekend block. Before proofs 3, 4 and 7, write down what you expect to see and commit it; the expected results are in section 16 under "Check your prediction".

A plan-assertion test is a test that runs EXPLAIN on the query a selector produces and asserts the node type (Index Scan, Index Only Scan, Bitmap Index Scan), so a later change cannot silently lose the index. Django's `QuerySet.explain()` accepts a format and PostgreSQL options.

> Guiding question you will hit: your plan-assertion test reports a Seq Scan on a 100-row test table even though the index exists. Is the planner wrong? You have two options (seed enough rows and ANALYZE, or disable sequential scans for that one transaction). What does each one actually prove?

| # | Proof | Pain-first: do → observe → record |
|---|---|---|
| 1 | **Seq scan first, then a composite index and a plan-assertion test.** Named query: a vendor's own products filtered by status, newest first. | Run it at 1M rows with no index → observe a Seq Scan and its time → save `seqscan-before.txt`. Add the composite index (think about column order: equality columns first, then the sort column) → save `composite-after.txt` → add the plan test. |
| 2 | **Partial index `WHERE status = 'published'`.** Named query: storefront listing of published products in a category. | Compare the size and plan of a full index vs the partial one → record both sizes. Guiding question: what must the query's `WHERE` clause contain for the planner to use a partial index? |
| 3 | **Covering `INCLUDE` index reaching Heap Fetches 0 after VACUUM.** Named query: the price/vendor lookup for a listing card. | Run it right after the load and record the plan node and its Heap Fetches → VACUUM → run again and record the same two things → save both (`heap-fetches-before-after.txt`). Explain the visibility map in two sentences (P4 D67–D71 did the same on `stock_levels`). |
| 4 | **Expression indexes: `lower(email)` and the normalized +998 phone.** | Query with the raw input first and record whether the planner uses the expression index → make the query use the *same* expression → save both plans. Guiding question: normalize at write time and index the column, or index an expression? |
| 5 | **OFFSET 400k vs keyset at 1M rows.** | Run `OFFSET 400000` → observe it reads and discards 400k rows → save the plan. Run the keyset form with a `(created_at, id)` tuple comparison → save the plan. Commit both. Record keyset p95 under the ADR-002 protocol (this is the "Done when" number). |
| 6 | **N+1 on a nested serializer.** The product list serializer nests vendor, category and offers. | Write it naively → count queries with `django_assert_num_queries` for 10 and for 50 products → record `n-plus-one.md`. Fix it so the count no longer depends on N. Guiding question: which Django queryset methods turn per-row access to a forward FK into a JOIN, and per-row access to a reverse FK or many-to-many into one extra query? Then read `ForwardManyToOneDescriptor.__get__` in Django's `related_descriptors.py` and write three sentences on *why* each access issued a query. |
| 7 | **GiST `EXCLUDE (vendor_id WITH =, tstzrange WITH &&)` on commission rates.** | First enforce "no overlap" with a check-then-insert in the service. Fire two overlapping inserts concurrently with a barrier (two threads that start at the same instant) → record how many committed and whether an overlap now exists → save `commission-race.log`. Add the exclusion constraint (it needs the `btree_gist` extension for the `=` on an integer) → rerun. The target: exactly one insert fails, in the database, with an exclusion violation mapped to 409 → save the log. |
| 8 | **UUIDv7 vs v4 insert speed and index size at 1M rows.** | Insert 1M rows keyed by v4, then by v7, under the ADR-002 protocol (3 runs each) → record insert time and index size (`bench/uuid` CSV). Explain the difference with B-tree page splits. Note: Python 3.13 has no `uuid.uuid7()` (it arrived in 3.14) and Postgres 17 has no `uuidv7()` (it arrived in 18) [C]; ADR-001 records why the pins stay. Your options: implement the RFC 9562 layout yourself (a 48-bit millisecond timestamp, version and variant bits, randomness; it is the SD6 bit-layout exercise, and the recommended path), or pin a small library that provides v7 (for example `uuid-utils` or `uuid6`). Record the choice in ADR-005. |

**Keyset tests (proof 5)** — required cases:
- ties on `created_at` (many rows with the same timestamp): no row is skipped or repeated;
- rows inserted mid-walk: walking older pages while newer rows arrive produces no duplicates and no gaps;
- the plan uses the index;
- the cursor is opaque to clients (encoded, not raw column values).

**OFFSET is kept on purpose** for the Admin's "jump to page 7", where exact page numbers matter and page depth is small. Whether the public API uses DRF's `CursorPagination` or your own keyset class is your call, as long as it passes the four keyset tests above; say which in one line in `docs/perf/s1.md`. (A written comparison of how `CursorPagination` handles ties is a stretch item.)

**Acceptance criteria**
- Eight entries in `docs/perf/s1.md`, each with the named query, before/after plans or numbers, and the protecting test.
- Plan-assertion tests for proofs 1, 2, 3, 4 and 5 run in CI.

---

### 4.7 Identity v1 [6 h]

**What to build**
- **Custom User:** bigint primary key for joins plus a **UUIDv7 public id** used in URLs and API responses; email (unique, case-insensitive via proof 4); +998 phone (normalized, unique); **argon2** password hashing configured as the first hasher (it needs the `argon2-cffi` package).
- **Session + CSRF for the Admin; JWT for the API.** Admin uses session cookies, which the browser sends automatically, so it needs CSRF protection. The API uses a JWT in the `Authorization` header, which the browser never adds on its own, so it does not. Write that paragraph in your own words (P2 made the same point: CSRF-exempting a session endpoint, or CSRF-protecting a JWT API "to be safe", are both wrong).
- **simplejwt access/refresh with HS256.** Short-lived access token, longer refresh token. **Refresh rotation is missing on purpose:** write it into `docs/deferred.md` as a gap ("a stolen refresh token works until it expires; logout cannot revoke it"). S3 fixes it with rotation, families and reuse detection.
- **Enumeration-safe login.** Unknown email and wrong password return **byte-identical** responses (same status, same body, same headers) with **similar timing**. Read `ModelBackend.authenticate` in Django's source: what does it already do for unknown users, and why?
- **`login_attempts` lockout:** per-account failure counter and `locked_until` in Postgres, with exponential backoff; the response does not reveal whether the account exists.
- **Roles plus relationship permissions.** Roles: `customer`, `vendor_owner`, `vendor_staff`, `ops`, `platform_admin` (`finance` arrives with money in S5). The rule that matters is a **relationship**, not a role: vendor staff act only for vendors they are a member of. Resolve membership from `vendors_vendor_staff` on each request; never put vendor ids in the token ([E5](README.md#e5-auth-evolution) makes this explicit in S2, when RLS depends on it). The same idea as PeopleOps' "manager decides only for direct reports" ([../python/03-peopleops.md](../python/03-peopleops.md), D40–D41).
- **An in-memory login limiter per IP** (a dict inside the process), running under gunicorn with **4 workers**.

**Pain-first A — the login that leaks**
1. Write the naive login first: "no user with this email" vs "wrong password".
2. Send 50 attempts of each kind. Record status, body bytes and the latency distribution in `docs/evidence/s01/login-enumeration.md`.
3. Fix it. Repeat and record: bodies identical byte for byte; latency distributions overlapping.

**Pain-first B — the 4× limiter**
1. Configure the in-memory limiter at, say, 5 attempts per minute per IP.
2. Run `market` under gunicorn with 4 workers. Send 40 failed logins from one IP, each on a new connection and each against a *different* account (a keep-alive client can pin every request to one worker and hide the effect, and repeated failures on one account trip the per-account lockout first; if you observe exactly 1×, check both).
3. Observe that roughly 20 attempts get through before 429: each worker counts separately, so the effective limit is about **4×**. Record the observed number and your explanation in `docs/evidence/s01/limiter-4x.csv` and `.md`.
4. **Do not fix it.** It is fixed in S3 (Redis, then Lua), where the same test is re-run with 3 containers × 4 workers. Add it to `docs/deferred.md`.

Note that the per-account `login_attempts` lockout lives in Postgres, so it is shared by every worker and *is* correct. Only the per-IP limiter is broken. Make sure your write-up says which is which.

**Acceptance criteria**
- The permission matrix test (section 6) passes, including crafted requests: vendor A's staff guessing vendor B's product and document ids.
- Login responses are byte-identical; the lockout triggers after N failures.
- The 4× number is recorded and listed in `docs/deferred.md`.

---

### 4.8 Worldgen v1 [3 h]

**What to build**
- Extend `atlas-worldgen` with: vendors whose sizes follow a **Pareto distribution** (a few "whale" vendors own most products; this skew matters later for hot shards and jumbo chunks), a category tree, **1M products** with offers and schema-valid attributes, and users.
- A **COPY seeder driven by a generator**: rows stream from the generator into Postgres through psycopg 3's COPY support, so memory stays flat at any row count. Record the load time for 1M products. Run the full 1M load in the weekend block; iterate on 10k rows first.
- The world spec, version and seed for this dataset are written into `docs/perf/s1.md`, because every plan in 4.6 depends on them.

**Acceptance criteria**
- Loading 1M products is one command and deterministic (same seed → same row hash).
- Memory stays flat during the load (watch the process RSS; record the peak).

---

### 4.9 Drills + SD6 [4 h]

- **Drill hour, weekly (4 × 1 h, with SD6 taking the W4 hour):** one SQL problem on your own Atlas schema (suggestions: category subtree with product counts via the recursive CTE; top 10 vendors by published products; the keyset query written by hand in `sql/`), or one DSA problem from [`../../dsa-problems.md`](../../dsa-problems.md); plus this stage's interview questions out loud.
- **SD6 (unique ID generator)** in W4 (week 2 of the stage): see section 9.

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| Views never touch the ORM | Layered module structure; the import-linter contract(s) you chose in 4.2 | CI `import-contracts` job; a deliberate violation once went red |
| Money is integer tiyin | `Money` refuses floats; `MoneyField` stores bigint and its descriptor returns `Money` | Hypothesis properties; "no float in money code" test |
| No overlapping commission windows for a vendor | `EXCLUDE USING gist (vendor_id WITH =, valid range WITH &&)` | Concurrent barrier test: exactly one insert fails, and it fails in the database |
| Presigned URLs are minted only after authorization | The service checks permission before calling the `ObjectStorage` port; TTL ≤ 5 min | Test: another vendor's staff cannot mint; an expired URL is refused |
| Staff act only for their own vendor | Membership resolved from `vendors_vendor_staff` per request, never from token claims | Permission matrix with crafted requests |
| Every migration is reversible | `RunPython`/`RunSQL` always have a reverse | CI migration up/down test |
| All timestamps are timestamptz in UTC | `USE_TZ = True`; UTC everywhere in storage | Test querying `information_schema.columns` finds zero `timestamp without time zone` columns |
| Login does not reveal whether an account exists | Identical response construction and a dummy hash on unknown users (E5) | Byte-comparison test; timing distribution recorded |
| The category tree query terminates | Cycle guard in the recursive CTE | Cyclic-tree test |

## 6. Tests to write

- **pytest-django on real Postgres:** testcontainers locally, a Postgres service container in CI. No SQLite anywhere: plans, JSONB, GiST and exclusion constraints do not exist there.
- **factory_boy** factories for users, vendors, memberships, categories, products and offers (replacing hand-written test data, as P1 D19–D24 did).
- **Hypothesis** for `Money` and allocation, seed pinned in CI.
- **Plan assertions** for proofs 1–5.
- **Migration up/down:** migrate every app to zero and back up on an empty database.
- **Permission matrix:** parametrized over role × endpoint × own/other vendor → expected status. Decide once whether "other vendor's object" returns 404 (hides existence) or 403, and apply it everywhere.
- **Keyset:** ties, mid-walk inserts, index used.
- **Recursive CTE:** 4-level tree, cyclic tree.
- **Presigned:** cannot mint for another vendor; expiry.
- **Commission EXCLUDE:** concurrent overlap rejected by the database. Use a test mode that really commits (pytest-django's `transaction=True`), because a test wrapped in one transaction cannot show a race between two.
- **Login:** byte-identical failure responses; lockout after N failures.
- **Service unit tests with fakes** for at least the vendor approval and product publish use cases.

## 7. CI changes

| Job | Gates |
|---|---|
| `test-integration` | pytest-django against a Postgres 17 service container (plan assertions, constraints, permissions) |
| `migrations` | `makemigrations --check` (no model change without a migration) and migration up/down |
| `import-contracts` | import-linter: the contract(s) you chose in 4.2; S4 adds the independence contracts to the same job |
| coverage | ≥ 80% on services and domain modules only; views, serializers and migrations are excluded (coverage belongs where the rules live, P1) |
| `typecheck` (extended) | mypy `--strict` now also covers `market`'s domain modules; the rest of `market` keeps the plain run with the S0 stubs decision |

## 8. ADRs and documents

**ADR-004 — Layering**
- *Questions:* What are the layers, what may import what, and how is it enforced? Which ports exist (at least `ObjectStorage`, `Clock`) and why each one? Where does a `Repository[T]` Protocol earn its keep in Django, and where do services use the ORM directly? What is in the composition root?
- *Numbers:* the count of import-linter contracts; the share of service tests that run without a database; unit-test suite time with fakes vs integration time.
- *Counter-argument:* "Django's ORM already *is* a repository and `atomic()` already *is* a unit of work; wrapping them is ceremony, and 'fat models' is the idiomatic Django answer." Hint: argue from your own numbers (the share of service tests that need no database, the two suite times) and from `docs/evidence/s01/import-linter-red.txt`. Say honestly where the wrapper adds nothing, and ask what S9 will need from a domain module that must leave the monolith unchanged.

**ADR-005 — IDs**
- *Questions:* Why a bigint internal key plus a UUIDv7 public id? Where does each appear (joins, URLs, events, logs)? How do you generate v7 on Python 3.13 / PG17 (hand-rolled RFC 9562 layout or a small pinned library, see proof 8)? What does a sequential public id leak (volume, enumeration)?
- *Numbers:* insert time and index size for v4 vs v7 at 1M rows (median and spread, ADR-002).
- *Counter-argument:* "Use UUIDs everywhere; one id type is simpler" and "use bigint and obfuscate it". Hint: argue from your `bench/uuid` numbers and from what a sequential id leaks.

**ADR-006 — Money and rounding**
- *Questions:* Why integer tiyin? One column or two? Which rounding mode (half-even or half-up) and where rounding is allowed to happen; how allocation distributes remainders (largest remainder); commission rates in basis points; how provider amounts will be normalized in S5 (Payme sends integer tiyin; Click sends decimal soum strings [U: exact format]).
- *Numbers:* show one concrete float error in tiyin (for example, summing a float price many times) and its size.
- *Counter-argument:* "`Decimal` is exact enough, and libraries such as django-money exist." Hint: argue from your float-error evidence, then ask what `Decimal` still leaves you to decide (rounding, currency) and what S5's balanced ledger needs from every amount.

**Documents**
- `docs/perf/s1.md`: the eight proofs, the worldgen seed and version, the keyset p95.
- `docs/learning/fastapi-to-django.md`: the mapping table, under the five answers from S0 §4.0.
- `docs/deferred.md`: refresh rotation gap; the 4× limiter; caching (no measured p95 yet); the search engine question.

## 9. System design session

**SD6 — Design a unique ID generator (Snowflake-style)**, W4 (week 2 of the stage), **built-lite**. Problem text: [`../../system-design-problems.md`](../../system-design-problems.md).
- *Built:* the UUIDv7 vs v4 benchmark (proof 4.6.8) and your generator choice (ADR-005). UUIDv7 is a Snowflake cousin: a millisecond timestamp in the high bits, randomness instead of a machine id and sequence.
- *Whiteboard (45 min):* the six-step skeleton. The deep dive is the bank's: what happens when a machine's clock goes backwards? Also cover why a central auto-increment counter does not scale here, and where you would still use a bigint (joins, internal keys).
- *Reuse from Atlas:* your B-tree index-size numbers are the evidence for the index-locality argument the problem asks for. Proof 8 runs in W6, after this session; add the numbers to `docs/sd/sd06.md` when you have them.
- *Also anchored here (light touch):* the system-design map places part of **SD17 (file storage)** at S1 because of the presigned flow. You do not run a full SD17 session now (it comes in S6). Write five lines in `docs/sd/` on what your KYC flow already answers: the metadata store (Postgres) vs the blob store (the S3-compatible store), and bytes that never pass through the API.

Save the whiteboard photo or notes to `docs/sd/sd06.md`.

## 10. Interview questions this stage lets you answer

1. How does lazy FK access cause N+1, and how did you prove the fix? (Show the counts for 10 and 50 items.)
2. `select_related` vs `prefetch_related`: which did you use where, and why?
3. When is OFFSET still the right choice?
4. Why can Heap Fetches be non-zero on a covering index?
5. JSONB or columns for category attributes? Which facets can GIN serve?
6. Why can't a CHECK constraint prevent overlapping windows? What did the race look like before `EXCLUDE`?
7. How does your `MoneyField` work? What does the descriptor add over `from_db_value`?
8. Why UUIDv7? Show me the index-size numbers.
9. Walk me through your layers. Why do views never touch the ORM, and how does CI enforce it?
10. How do you prevent user enumeration on login?
11. Why does the Admin need CSRF protection when your JWT API does not?
12. Why is a presigned URL minted only after authorization, and how long does it live?
13. What stops your recursive CTE from looping forever?
14. Your login limiter allowed 4× the limit. Why, and what is the fix? (Answered fully after S3.)
15. What goes in an access token and a refresh token, and what is still missing from yours?

## 11. Common mistakes to watch for

- Swapping `AUTH_USER_MODEL` after the first migration instead of creating the custom User first.
- Business rules in serializers, viewsets or model `save()` because "Django does it that way" (P2 named this; so did the review pass in P2 D25–D30).
- Adding indexes speculatively instead of from a plan you ran (P1 D13–D18).
- Fixing N+1 with `select_related` everywhere "just in case" instead of measuring with query counts (P2 D31–D39).
- A plan-assertion test that passes only because the table is tiny, or fails only because it is tiny.
- Keyset pagination without a unique tie-breaker, so equal timestamps skip or repeat rows.
- A recursive CTE with `UNION ALL` and no guard on data that can contain a cycle (P1).
- Different error messages for "no such user" and "wrong password" (P5 D79–D84).
- Presigned URLs valid for hours, or authorizing the download page but not the minting (P5 D85–D90).
- Floats anywhere near money, including "just for display".
- Trusting a vendor id from the token or the request body instead of checking membership.
- Believing an in-process limiter is global.
- Querying with a raw value when the index is on an expression of that value.

## 12. How real companies differ

- **Layering style.** Many Django teams use "fat models", others a services/selectors style (for example the HackSoft Django styleguide). Both work in production; what matters is one consistent home for rules. Atlas uses services because rules are shared by Admin and API and because parts of the code will leave the monolith.
- **KYC.** Real marketplaces usually outsource document checks to a verification provider, so the platform never stores raw identity documents. You store them to learn private buckets and presigned URLs; data governance for them arrives in S6 and S9.
- **Public ids.** Payment companies often use prefixed, typed public ids (`acct_…`, `pi_…`). AtlasPay adopts that style in S5; `market` keeps UUIDv7.
- **Catalog search.** Large catalogs usually serve browsing and search from a search engine, with Postgres as the source of truth. Atlas earns that step only if Postgres fails a judged query set (S4).
- **Money.** Teams often use a money library. Writing `Money` and `MoneyField` yourself is the right learning choice because the descriptor and the rounding policy are exactly what interviewers probe.

## 13. Deliberately not doing

| Item | Why not now | When |
|---|---|---|
| Cart and orders | The catalog must exist first; checkout is its own correctness stage | [Stage 02](stage-02-checkout-correctness.md) |
| Caching | No measured p95 problem yet; caching now would be guessing | S3 (cold/warm p95 first) |
| A search engine | Postgres has not failed yet | S4 (only if the judged query set fails on FTS) |
| Refresh-token rotation and families | One auth concept at a time; the gap is written down | S3 |
| A correct cross-process login limiter | The 4× defect must be felt and measured first | S3 |
| RLS on vendor tables | Relationship checks come first; RLS is the second wall | S2 |
| RS256, JWKS, OIDC | HS256 is enough inside one process; S8 discovers why it is not later | S9 |
| Any frontend | Admin and the API are enough to prove the flows | S6 (server-rendered), S11 (React) |
| Shared products with many vendors' offers | Catalog matching is a product problem with no new backend lesson here | Not in Season 1 |

## 14. Stretch

Only after the must tier closes, in this order of value:
- **Trigram GIN index for Admin search [1 h]:** `pg_trgm` for "contains" search on product titles in the Admin; compare with `ILIKE` without it.
- **ROLLUP report [1 h]:** a `GROUP BY ROLLUP` over the category tree (for example, published offers and their listed value per category, with subtotals and a grand total; a test checks that subtotals sum to the total). It becomes the real stock-value report once S2 adds stock (P1 D13–D18).
- **DRF serializer vs `values()` benchmark [1 h]:** list endpoint throughput with full serializers vs `values()` plus a thin serializer, under ADR-002.
- **COPY vs `bulk_create` vs `executemany` [1.5 h]:** load time for 100k rows each, 3 runs.
- **Offset-vs-keyset note [0.5 h]:** a one-page explainer in `docs/perf/` you could hand to a colleague.
- **Cycle guards side by side [0.5 h]:** the `CYCLE` clause vs a `UNION`-based guard with a depth cap on the cyclic test tree; compare the output and the plans, and say when each is the better choice.
- **`CursorPagination` vs your keyset [0.5 h]:** read how DRF's `CursorPagination` handles ties on `created_at`, run your four keyset tests against it, and write the comparison into `docs/perf/s1.md`.

If you are behind at the B1 checkpoint (W18), the degrade list ([schedule-and-cuts §7](schedule-and-cuts.md#7-cut-order-and-the-degrade-list)) allows proof 8 to shrink to reading only (the item "UUIDv7 benchmark → reading only", saves 1 h); ADR-005 then cites the literature instead of your numbers and says so.

## 15. Definition of done

- [ ] Ops approve a vendor from the Admin KYC queue; the approval is attributed.
- [ ] The vendor uploads a product with an offer and an image, and publishes it.
- [ ] The 1M-row catalog pages by keyset, with p95 recorded under ADR-002.
- [ ] Eight Postgres proofs in `docs/perf/s1.md`, with plans and evidence files.
- [ ] N+1 counts before and after committed; `ForwardManyToOneDescriptor.__get__` explanation written.
- [ ] Commission `EXCLUDE` race: red log before, green log after.
- [ ] Login enumeration: before/after evidence; lockout tested.
- [ ] The 4× limiter number recorded and listed in `docs/deferred.md`.
- [ ] `docs/learning/fastapi-to-django.md` complete.
- [ ] CI: `test-integration`, `migrations`, `import-contracts` and the coverage gate green.
- [ ] ADR-004, ADR-005, ADR-006 merged.
- [ ] SD6 session notes in `docs/sd/sd06.md`.
- [ ] `docs/hours.csv` has one row per block of this stage, with budget and actual.
- [ ] Postmortem paragraph written (use the budget-vs-actual numbers).
- [ ] 2 STAR stories in `docs/star/`: the N+1 you found by counting; discovering the 4× limiter.
- [ ] Tagged `v0.1`.

## 16. If you get stuck

- **Django ramp.** If Django feels like it is fighting you, ask: "which FastAPI habit am I carrying?" Check your mapping table's "trap" column. Reread the review pass in P2 D25–D30 ([../python/02-quickserve-pos.md](../python/02-quickserve-pos.md), Stage 1).
- **Layering.** If a view "needs" the ORM: which selector is missing? If a service is hard to test: which external thing does it call directly that should be a port? Reread P1 D7–D18 ([../python/01-stockpilot.md](../python/01-stockpilot.md), Stages 2–3) and the Two Scoops chapter on services that P2 D32 cites ([phase-2 D32](../../phase-2-concurrency-django-caching.md)).
- **KYC and presigned URLs.** If a URL works for the wrong person: at which line did you check permission, before or after calling storage? If uploads fail from the browser but work from a script: is it CORS on the bucket, or a clock skew between your machine and the object store? If presigned URLs fail on Garage only: did the two-line check in 4.3 pass on the tag you pinned, and does your client sign for the region and endpoint style (path vs virtual-host) the store expects? Reread P5 D85–D90 ([../python/05-carepoint.md](../python/05-carepoint.md), Stage 2).
- **Catalog.** If the recursive CTE never ends: what does your query do the second time it meets a node it has seen? If facets are slow: does the query use `@>` or a function on the column?
- **Money.** If the descriptor never runs: how does a field install a descriptor on the model class? Look at how Django's `FileField` does it (`contribute_to_class`).
- **Postgres proofs.** If the planner ignores your index: did you run ANALYZE after loading? Does the query's shape (column order, expression, `WHERE` predicate for a partial index) match the index exactly? If Heap Fetches stay above 0: has VACUUM run since the last write? Reread P1 D13–D18 (EXPLAIN, keyset) and P4 D67–D71 ([../python/04-wareflow.md](../python/04-wareflow.md), Stage 3, covering index).
- **EXCLUDE race.** If both inserts still commit in the test: is the test really running two transactions at the same time, and are they committing (not wrapped in one test transaction)?
- **Identity.** If timing still differs between unknown and known emails: what work does the known-email path do that the unknown path skips? If the limiter shows 1×: is your client reusing one connection? Reread P5 D79–D84 ([../python/05-carepoint.md](../python/05-carepoint.md), Stage 1) and P2 D37–D39 (simplejwt and throttling internals).
- **Worldgen.** If memory climbs during the load: where are rows being collected into a list? A generator only helps if nothing downstream materialises it.

<details>
<summary>Check your prediction (open only after you committed yours)</summary>

- **Proof 3.** Right after a bulk load the plan is usually an Index Only Scan with *non-zero* Heap Fetches, because the visibility map does not yet mark those pages all-visible; after VACUUM, Heap Fetches drop to 0. (If the first run already shows 0, autovacuum got there first: check `last_autovacuum` in `pg_stat_user_tables`, and repeat after an update burst.)
- **Proof 4.** A query on the raw value (`email = 'X@Y'`) does not use an index built on `lower(email)`; the planner only matches an expression index when the query uses the same expression.
- **Proof 7.** With check-then-insert, both overlapping inserts usually commit: each transaction checked before the other inserted, so neither saw a conflict. With the exclusion constraint, the second one fails in the database with an exclusion violation (SQLSTATE `23P01`).

</details>

Previous: [Stage 00 — Bootstrap](stage-00-bootstrap.md) · Next: [Stage 02 — Checkout correctness](stage-02-checkout-correctness.md).
