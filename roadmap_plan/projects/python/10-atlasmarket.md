# Project 10 — AtlasMarket

**Multi-vendor e-commerce marketplace — the capstone**

| | |
|---|---|
| Domain | E-commerce |
| Level | Middle+ / Senior |
| Phase | 6 — Senior-Track Capstone |
| Weeks | 27–28 (D157–D168) |
| Stack | Nginx gateway + 5 services, PostgreSQL (managed, **Row Level Security**), Elasticsearch, RabbitMQ, **real AWS/GCP via Terraform** (+ TLS, CDN for the storefront), OpenTelemetry end to end, React + TS + Vite + React Router + TanStack Query, **Playwright**, feature flags, `locust`, GraphQL BFF (stretch) |
| Repo | `atlasmarket/` + `atlasmarket/storefront/` |

> **This is an integration exercise, not a rewrite.** You are explicitly
> instructed to **import and adapt** prior projects' logic wherever it already
> solves the problem. If you find yourself designing something from scratch, stop
> and check which of the previous nine projects already did it.

---

## 1. Business Problem

Independent vendors need a shared marketplace to list products, manage their own
inventory, and receive payouts. Customers browse a unified catalog, check out
across multiple vendors in one order, and track fulfillment.

This is the convergence point of everything built so far:

| Capability | Comes from |
|---|---|
| Catalog & inventory | StockPilot (P1) |
| Checkout logic | QuickServe POS (P2) |
| Fulfillment status | WareFlow (P4) |
| Auth | CarePoint's `auth-service` (P5) |
| Per-vendor payout ledger | LedgerBase (P6) |
| Event-driven order flow, outbox | FleetTrack (P7) |
| Search | DocuVault's Elasticsearch work (P8) |
| Payments (idempotent) | PayFlow (P9) |

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Five services behind one Nginx gateway, each traceable to its origin project
2. Vendor onboarding and vendor-scoped product listing
3. Unified catalog search across all vendors
4. **Multi-vendor checkout: one cart, one payment, N vendor groups, N ledger entries**
5. Per-vendor fulfillment status
6. A React/TS storefront: product list, cart, checkout
7. Gateway + `catalog-service` deployed to **real cloud infrastructure** — created
   by **Terraform** (extending PayFlow's `infra/`), served over **HTTPS**, with the
   storefront's static build on **object storage + CDN**
7a. Vendor isolation enforced **twice**: in every query, and by **Postgres Row
   Level Security** — so a forgotten `WHERE vendor_id` cannot leak

**Operational firsts**
8. **Bulkhead** connection pools per downstream service
9. A change shipped **dark behind a feature flag**, then ramped 10% → 100% while
   watching Grafana — the first canary all year
10. A **Playwright** browser test through the whole checkout flow
10a. One **trace** for one checkout across all five services and the outbox relay —
    the observability demo of the whole curriculum
10b. A `locust` checkout load test that sets the bulkhead pool sizes from numbers
10c. **Gateway rate limiting** (Nginx `limit_req` per IP + per API key) as the
    outermost of three protection layers (rate limit → bulkhead → breaker)

**Proof it is correct**
11. The end-to-end test: two vendors, one checkout, two `order_vendor_groups`,
    two ledger entries, one idempotent payment
12. A saturation test proving the bulkhead isolates a slow service
13. A feature-flag test proving a user always lands on the same side of a 10% rollout

**Written artefacts**
14. `docs/architecture.md` mapping every service to its origin project
15. `docs/cloud-deployment-notes.md` — IAM policy, VPC layout, **monthly cost estimate**
16. `docs/atlasmarket-roadmap-post-bootcamp.md` — the deferred list, respected
17. Two system-design problems worked from scratch and compared to what you built
18. `docs/multi-tenancy-decision-record.md` — shared schema + RLS vs schema-per-tenant
    vs database-per-tenant
19. `docs/distributed-transactions.md` — why not 2PC, why the saga/outbox shape instead
20. `docs/cart-persistence.md` — client state now; the Redis-hash design that
    replaces it when carts must survive across devices
21. *(Stretch)* a **GraphQL BFF** for the storefront with **DataLoader**, and the
    N+1 it prevents, measured

---

## 3. Scope Honesty (stated upfront)

Two weeks is enough to stand up a **real architectural skeleton with core flows
genuinely working end to end** — not a feature-complete marketplace.

That is the correct shape. This project is designed to become your **ongoing
portfolio project after Day 180**, built on a foundation that is actually
load-bearing instead of upfront-overscoped the way the original AtlasCommerce plan
was.

**Explicitly NOT built** — documented so scope creep cannot quietly eat the timeline:

| Deferred | Note |
|---|---|
| Reviews / ratings | |
| Recommendation engine | |
| Vendor analytics dashboard | → Project 25, Phase 11 |
| Promotions / discounts across vendors | The cross-vendor accounting alone is a project |
| Kubernetes in production, a service mesh, a managed flag service | See §10 — named, deliberately not built |
| Returns workflow | |
| Vendor trust / fraud systems | What real marketplaces invest in first |
| Search relevance tuning at scale | |

> **Scope creep is the actual failure mode of this project — more than any
> technical mistake.** Write the deferred list on day one and re-read it on day ten.

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`customer`** | Browse and search, manage own cart, check out across vendors, view own orders and per-vendor fulfillment status | See vendor payout details, other customers' orders, or internal ledger entries |
| **`vendor_staff`** | Manage **own vendor's** products and stock, view **own vendor's** order groups and mark them fulfilled, view own payout statement | See another vendor's products, orders, revenue or payouts; see the customer's other vendor groups in the same order |
| **`vendor_owner`** | Everything vendor_staff can, plus manage vendor staff and payout account details | Anything outside their own vendor |
| **`marketplace_ops`** | View all orders and vendor groups, resolve stuck fulfillments, onboard and suspend vendors | Alter a posted ledger entry or a completed payment |
| **`finance`** | Reconcile payouts across vendors, run ledger reports | Change order or payment substance |
| **`platform_admin`** | Manage services, feature flags, rollout percentages | Bypass the ledger or payment invariants |

**The permission rule that defines this project:** *vendor isolation.* A vendor
sees their slice of an order and nothing else — not the customer's other vendor
groups, not the marketplace's total. One customer order is deliberately fragmented
along vendor lines, and that fragmentation is a **security boundary**, not just a
data-modelling convenience. Test it as one.

**Enforce it in two places.** Every query filters by `vendor_id` — that is the
first line. The second is **Postgres Row Level Security**: `ALTER TABLE products
ENABLE ROW LEVEL SECURITY` plus a policy `USING (vendor_id =
current_setting('app.vendor_id')::bigint)`, with the application setting
`SET LOCAL app.vendor_id = ...` at the start of each vendor-scoped transaction
(after resolving the vendor from the JWT). A query that forgets the `WHERE` now
returns nothing instead of everything. Test exactly that: comment out one
`WHERE vendor_id`, run vendor B's request, assert an empty result and a log line.

This is the same defense-in-depth philosophy as CarePoint's `EXCLUDE` and
LedgerBase's trigger, applied to authorization. RLS has costs — a per-transaction
`SET`, policies that the planner must apply, and a connection-pool interaction
(PgBouncer transaction mode and `SET LOCAL` are fine; `SET` without `LOCAL` is
not) — write them down in `docs/multi-tenancy-decision-record.md` alongside the
alternatives (schema-per-tenant, database-per-tenant) and when each wins.

---

## 5. Architecture — the payoff of six months of layering

```
                        Nginx gateway
                             │
   ┌──────────┬──────────────┼──────────────┬───────────────┐
   ▼          ▼              ▼              ▼               ▼
auth-      catalog-       order-        payment-        ledger-
service    service        service       service         service
(P5)       (P1 lineage,   (P2 checkout  (P9 PayFlow,    (P6, per-vendor
           vendor-scoped, + P4-style    idempotent)     payouts)
           P8 ES search)  fulfillment,
                          P7 outbox)

storefront/  (React + TS + Vite + TanStack Query) → consumes the gateway
```

### Bulkhead — new here, and it earns its keep

The gateway calls all five services synchronously. A **bounded connection pool per
downstream service** means a saturated `payment-service` cannot starve calls to a
perfectly healthy `catalog-service`.

| Pattern | Protects against | How |
|---|---|---|
| Retry + backoff (P4) | Transient failure | Try again, later |
| Circuit breaker (P6) | A *dead* dependency | Stop calling it entirely |
| **Bulkhead (here)** | A *slow* dependency | Cap how much of your capacity it can consume |

The breaker does not help against slow-but-succeeding calls: they never fail, so
it never trips, while every worker sits waiting. The bulkhead is what keeps the
rest of the system alive. Be able to say that.

You *saw* this in PayFlow's Toxiproxy run: 2s latency, 0% errors, breaker
closed, system dying. The bulkhead is the answer to that specific observation.

Add the outermost layer at the gateway: **Nginx `limit_req`** per client IP and,
for API-key callers, per key (`$http_x_api_key` as the zone key), with a small
burst. Rate limit → bulkhead → breaker → retry: four layers, each with a
different failure it handles. Draw the table in `docs/architecture.md`.

**Why not distributed transactions?** Checkout touches five services. The
tempting textbook answer is two-phase commit. `docs/distributed-transactions.md`
explains why not — blocking coordinators, in-doubt transactions, no 2PC support
in your brokers, and the availability cost — and why the shape you built (one
local transaction for the order split + outbox, idempotent payment, eventual
ledger entries with reconciliation) is the industry's actual answer. One page,
because the interviewer will ask "why not just use a transaction across services".

---

## 6. Domain Model (delta from prior projects)

```
vendors(id, name, payout_account_ref, status)

vendor_staff(user_id, vendor_id, role)

products(..., vendor_id -> vendors.id)          -- extends StockPilot's model

orders(id, customer_id, status, created_at)

order_vendor_groups(id, order_id, vendor_id, status, journal_entry_id)

payments(...)                                    -- one per order, via PayFlow
```

`order_vendor_groups` is the key structure: one customer order becomes N per-vendor
groups, each with its own fulfillment status and its own ledger entry — but **one**
payment, taken once, idempotently.

That asymmetry (one payment, many groups) is the whole design problem, and it is
what an interviewer will ask you to walk through.

---

## 7. The Checkout Flow (the thing to be able to narrate)

```
1. Cart is submitted
2. order-service validates stock per line, per vendor
3. Order created; split into order_vendor_groups            [one transaction]
4. Outbox rows written for OrderPlaced events               [same transaction]
5. payment-service charges ONCE, idempotently (Idempotency-Key = order id)
6. On webhook confirmation → per-vendor ledger entries via ledger-service
7. Outbox relay publishes; each vendor's fulfillment view updates
8. Customer sees one order; each vendor sees only its own group
```

Steps 3–4 are one transaction because that is what FleetTrack taught you. Step 5
is idempotent because that is what PayFlow taught you. Step 6 balances because
that is what LedgerBase taught you. **Nothing here is new** — that is the point of
a capstone.

---

## 8. Real Cloud Deployment

The gateway and `catalog-service` deploy to a **real AWS or GCP account**:

| Item | Requirement |
|---|---|
| **Terraform** | Everything below is in `infra/` (started in PayFlow Week 26): add the compute (a VM or a small container service), the managed Postgres instance, the object-storage bucket + CDN, DNS and the certificate. `plan` in CI, `apply` from `main`, remote locked state. **No console clicks** — if it is not in the code, it does not exist |
| IAM | Least-privilege role, **not** the root account |
| Network | VPC with the database in a **private subnet** |
| Security groups | Scoped to exactly the needed ports; `5432` admits only the gateway/service SG |
| Database | **Managed Postgres**, not a container; RLS policies applied by migration |
| **TLS** | A real certificate (ACM / managed cert on the load balancer, or Let's Encrypt on the gateway VM as in LedgerBase); HTTP → HTTPS; HSTS |
| **Static hosting** | Storefront build on object storage behind a CDN; cache headers set |
| Docs | `docs/cloud-deployment-notes.md` — the Terraform module layout, IAM policy, VPC diagram, **monthly cost estimate read from the actual bill after a week** |

*(The account, IAM role and VPC are created back in Week 26 alongside PayFlow's
security work, so they are ready when this project needs them.)*

**Blast radius is the interview question here:** what can an attacker do with the
gateway's IAM role, versus what they could do with root credentials? If the answer
is "the same thing", the role is not least-privilege.

---

## 9. Frontend — `storefront/` (fourth React/TS app)

Built on habits from CarePoint, FleetTrack and DocuVault — not learned from zero.

- **React Router** routes: product list / cart / checkout
- Product list via **TanStack Query** — by now the parallels to your own Redis
  cache-aside invalidation are second nature
- **Cart state in local component state.** No Redux/Zustand at this scope — and
  you write down *why* global state management is not justified yet. Same
  discipline as every other "not yet" call in this curriculum
- Checkout form wired to the real payment/order flow

**Honest framing:** four builds in is enough to read a frontend PR, ask the right
questions, and ship a small feature without a frontend engineer. It is **not** the
same as being a frontend specialist, and this plan does not pretend otherwise.

**Where the static files live.** The storefront is a static build. In the cloud
it goes to **object storage behind a CDN** (S3 + CloudFront, GCS + Cloud CDN, or
Cloudflare in front of either), with cache headers on hashed asset filenames
(`immutable`) and a short TTL on `index.html`. A backend engineer should know
this shape and its cost (near zero) even without owning the frontend.

**Cart persistence.** Cart state is client-side at this scope. Write
`docs/cart-persistence.md`: the Redis design that replaces it (a hash per user,
TTL, merge-on-login for anonymous carts) and the moment it becomes necessary
(second device, abandoned-cart emails). The **Idempotency-Key for checkout is
the order id** — which means a cart re-submitted as a *new* order needs a
*client-generated* key; state that explicitly, or two clicks become two orders.

### GraphQL BFF *(stretch)*

The storefront's product page fetches a product, its vendor, its stock and its
reviews-count from three services. A **backend-for-frontend** in GraphQL
(Strawberry) lets the page ask for exactly that in one query. The lesson is not
GraphQL syntax — it is the **N+1 problem**: a naive resolver for `vendor` on a
list of 50 products makes 50 calls; a **DataLoader** batches them into one.
Measure both. Then write the third column of PayFlow's transport decision
record: REST for resources, gRPC for internal RPC, GraphQL for a client that
composes. If time runs out, the decision record alone is acceptable; the
DataLoader measurement is what makes it more than reading.

### Feature flag + canary — the first all year

Checkout ships behind a **hand-rolled feature flag**: a config table plus an
`is_enabled(flag, user_id)` check with percentage rollout. Shipped **dark**, then
ramped **10% → 100% while watching Grafana**.

The rollout must be **stable per user** — the same user always lands on the same
side. Hash the user id into a bucket; do not roll a random number per request. A
user who sees the new checkout, refreshes, and gets the old one has had a worse
experience than either version alone.

### Playwright

A **Playwright** test drives a real browser through browse → cart → checkout,
**on top of** (not instead of) React Testing Library component tests. It catches
the class of bug a component test structurally cannot: a broken route, a CSS issue
hiding the submit button, a redirect loop after login.

---

## 10. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **Nginx gateway** | Single entrypoint routing to all five services; holds the bulkhead pools | Extended from CarePoint/LedgerBase |
| **Managed Postgres (cloud)** | `catalog-service` in production; **private subnet** | The first database you do not operate yourself — and the first with a real network boundary |
| **PostgreSQL (Compose)** | Everything else, locally | Do not migrate all five services to the cloud. One vertical slice is the lesson |
| **Elasticsearch** | Vendor-scoped product search | DocuVault's pattern reused: Postgres is truth, ES is derived and rebuildable |
| **RabbitMQ** | `OrderPlaced`, `VendorGroupFulfilled`; the outbox relay | FleetTrack's pattern reused |
| **Outbox table** | In `order-service`, written in the same transaction as the order split | Reused, not re-derived |
| **PayFlow's idempotency store** | Checkout, keyed on the order id | Reused |
| **Bulkhead pools** | The gateway's HTTP client, one bounded pool **per downstream service** | New here. Five synchronous dependencies is the first time it matters |
| **Circuit breaker + retry** | Each downstream call | Reused from LedgerBase |
| **Feature-flag table** | `is_enabled(flag, user_id)` with stable per-user bucketing | Deliberately hand-rolled — a flag service would hide the mechanism you are meant to understand |
| **Prometheus + Grafana** | Per-downstream latency and pool saturation, checkout success rate **split by flag cohort**, ledger-entry lag | The cohort split is what makes the canary meaningful. Without it you are ramping blind |
| **OpenTelemetry, end to end** | Every service carries LedgerBase's OTel setup; `traceparent` crosses the gateway, the sync calls, the outbox (FleetTrack) and the payment webhook | One checkout = one trace across five services and a relay. This is the demo you open in the interview |
| **Nginx `limit_req`** | Per IP and per API key at the gateway | The outermost protection layer, cheaper than anything behind it |
| **Postgres RLS** | `vendor_id` policies on `products`, `order_vendor_groups`, payout tables; `SET LOCAL app.vendor_id` per transaction | Isolation that survives a forgotten `WHERE` |
| **Terraform** | All cloud resources | See §8 |
| **`locust`** | Checkout flow at realistic concurrency | Bulkhead pool sizes come from these numbers, not from a guess |
| **GraphQL BFF** *(stretch)* | Strawberry + DataLoader for the product page | The N+1 measurement |
| **Playwright** | Browser E2E in CI | |
| **Cloud IAM / VPC / security groups** | Gateway + catalog-service | |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Kubernetes in production** | You ran `kind` locally in Phase 8 to understand the objects. Operating a production cluster is a different job, and two weeks is not enough to do it honestly |
| **A service mesh** | Five services, one gateway. The mesh would add operational surface you cannot justify |
| **A managed feature-flag service** | Hand-rolled on purpose — the bucketing logic *is* the lesson |
| **A shared cart cache** | Cart lives in the client at this scope. `docs/cart-persistence.md` designs the Redis version and names the trigger for building it |
| **Two-phase commit** | `docs/distributed-transactions.md`. The saga/outbox/idempotency shape you built *is* the answer to "how do you keep five services consistent" |
| **Per-service databases** | Tempting "proper microservices" instinct. At this scale it multiplies operational cost and forces distributed transactions you deliberately avoided. Say why you did not |

---

## 11. Build Plan (consolidated)

### Stage 1 — Architecture map & catalog *(D157–D161, Week 27)*
- New repo `atlasmarket/`; `docs/architecture.md` **mapping each service to its
  origin project** — write this first; it is the plan
- Adapt StockPilot's product model: add `vendor_id`; vendor onboarding endpoint
- **RLS policies** + `SET LOCAL app.vendor_id`; the "forgotten WHERE" test;
  `docs/multi-tenancy-decision-record.md`
- Extend PayFlow's `infra/` with compute, managed Postgres, bucket + CDN, DNS, cert
- Adapt DocuVault's ES sync pattern to index **vendor-scoped** products
- `storefront/` scaffold; React Router routes; product list via TanStack Query
- Cart state + cart UI, wired to the router's cart route

### Stage 2 — Checkout, cloud, canary *(D163–D165, Week 28)* *(v2: +2 days)*
- **Checkout:** cart → split into `order_vendor_groups` → PayFlow idempotent
  payment → per-vendor ledger entries
- **Bulkhead** pools on the gateway's calls to each of the five services — sized
  from a `locust` checkout run; Nginx `limit_req` in front
- OTel across all five + relay; one checkout trace end to end
- Adapt WareFlow's status concepts to `order_vendor_groups`
- `terraform apply`: gateway + `catalog-service` on **real cloud compute**, DB on
  managed Postgres in the private subnet, **HTTPS**, storefront on bucket + CDN
  → `docs/cloud-deployment-notes.md`; `docs/distributed-transactions.md`;
  `docs/cart-persistence.md`
- Storefront checkout wired to the real API, shipped **dark behind the flag**,
  ramped 10% → 100% while watching Grafana

### Stage 3 — Design practice & wrap *(D166–D168, Week 28)*
- **Whiteboard multi-vendor checkout from scratch, no code** — then compare to
  what you built. Work SD10 from `system-design-problems.md`
- Design payment idempotency + product search from scratch, unprompted; work SD16
- Playwright test: real browser through browse → cart → checkout
- *(Stretch)* GraphQL BFF with DataLoader; N+1 measured; transport DR completed
- Read the cloud bill; put the real number in `docs/cloud-deployment-notes.md`
- `docs/atlasmarket-roadmap-post-bootcamp.md`

---

## 12. Testing Strategy

| Layer | What |
|---|---|
| **End-to-end (the one that matters)** | Browse → add items from **two different vendors** → checkout **once** → verify **two `order_vendor_groups`**, **two separate ledger entries**, **one idempotent payment** |
| **Vendor isolation** | Vendor A cannot read vendor B's products, orders, or payouts — tested at the API, including a crafted request, not just a hidden UI element |
| Vendor isolation | Vendor A sees only its own group within a shared customer order |
| Browser E2E | Playwright through the real storefront flow |
| Component | React Testing Library on the storefront |
| **Bulkhead** | Saturate `payment-service` with slow responses; confirm `catalog-service` calls still succeed at normal latency |
| Feature flag | The same user always lands on the same side of a 10% rollout, across requests and sessions |
| Idempotency | A retried checkout charges once |
| Search | A vendor-scoped inventory change propagates to the catalog index |
| Cloud | The database is unreachable from the public internet |
| **RLS** | With one `WHERE vendor_id` removed from a query, vendor B's request returns nothing; the policy is enforced when connecting as the app role and bypassed only by the migration role |
| Rate limit | `limit_req` returns `429` past the burst; other clients unaffected |
| **Trace** | One `trace_id` from the storefront request through gateway → order → payment → ledger and the outbox relay |
| Load | Bulkhead pool sizes documented with the `locust` numbers that produced them |
| Terraform | `plan` clean after `apply`; the DB SG admits only the service SG; TLS certificate valid; the storefront loads from the CDN with `immutable` asset headers |
| GraphQL *(stretch)* | Product list with 50 vendors: 51 calls without DataLoader, 2 with |

---

## 13. Definition of Done

- [ ] `docs/architecture.md` maps every service to its origin project
- [ ] Vendor onboarding + vendor-scoped product listing
- [ ] Vendor-scoped catalog search backed by Elasticsearch
- [ ] **Multi-vendor checkout: one payment, N vendor groups, N ledger entries**
- [ ] Vendor isolation proven at the API, not assumed from the UI
- [ ] Bulkhead pools per downstream service, proven under saturation
- [ ] Gateway + catalog-service live on real cloud, DB in a private subnet
- [ ] `docs/cloud-deployment-notes.md` with IAM policy, VPC layout, cost estimate
- [ ] Storefront: product list, cart, checkout — against the real API
- [ ] Checkout shipped dark, ramped 10% → 100%, watched on Grafana **by cohort**
- [ ] Feature-flag bucketing stable per user, tested
- [ ] Playwright end-to-end test green
- [ ] RLS policies live; "forgotten WHERE" test passes
- [ ] Nginx `limit_req` at the gateway; four protection layers documented
- [ ] One checkout traced across all five services and the relay
- [ ] Cloud built by Terraform only; HTTPS; storefront on CDN; real bill recorded
- [ ] `docs/multi-tenancy-decision-record.md`, `docs/distributed-transactions.md`, `docs/cart-persistence.md`
- [ ] *(Stretch)* GraphQL BFF + DataLoader measurement; transport DR complete
- [ ] Two system-design problems worked from scratch (SD10, SD16) and compared
- [ ] `docs/atlasmarket-roadmap-post-bootcamp.md` written — **and respected**

---

## 14. Interview Questions This Project Should Let You Answer

1. Walk me through the full checkout flow across the five services, start to
   finish, including where idempotency and the ledger come in.
2. One payment, many vendor groups — how do you keep that consistent?
3. How does `catalog-service` search stay consistent with vendor-scoped inventory
   changes?
4. What did you deliberately leave out of v1, and why was that right under a
   two-week constraint?
5. If this needed to support 10,000 vendors tomorrow, what breaks first?
6. Why does the database sit in a private subnet, and what's the blast radius if
   the gateway's IAM role leaked versus if you'd used the root account?
7. Walk me through what your bulkhead does that the circuit breaker alone doesn't.
8. How does your feature flag guarantee the same user always lands on the same
   side of a rollout — and why does that matter?
9. Why one database rather than one per service?
10. How do you make sure a vendor can never see another vendor's data?
11. Row Level Security — how does it work, what does `SET LOCAL` have to do with
    connection pooling, and what would make you choose schema-per-tenant instead?
12. Why not a distributed transaction across the five services?
13. Rate limit, bulkhead, circuit breaker, retry — which failure does each handle,
    and in what order do they sit?
14. Show me one checkout as a trace. Where did the time go?
15. What is in your Terraform, and what would break if someone changed the security
    group in the console?
16. Where do the storefront's static files live, and why not on the gateway VM?
17. *(Stretch)* What is the N+1 problem in GraphQL and how does DataLoader solve it?

---

## 15. Common Mistakes to Watch For

- **Building the deferred features anyway under time pressure.** The failure mode
  of this project
- Treating the storefront as equally important as the backend integration
- Rebuilding instead of adapting prior projects' logic
- Enforcing vendor isolation in the UI or the serializer instead of the query
- Ramping a canary without splitting the dashboard by cohort — you learn nothing
- A per-request random feature-flag roll, so users flip between versions
- Splitting the database per service because "microservices", then discovering you
  need a distributed transaction for checkout
- Vendor isolation that lives only in the ORM query, one forgotten filter away from a leak
- `SET app.vendor_id` (not `LOCAL`) through a transaction-mode pool, leaking a vendor into the next request
- Cloud resources created by hand "just to get it working", never captured in Terraform
- Sizing bulkhead pools by feel instead of from the load test
- Shipping a portfolio capstone over plain HTTP

---

## 16. How Real Companies Differ

Real marketplaces invest heavily in **vendor trust and fraud systems** and **search
relevance tuning** long before most of what you built here — because a marketplace's
hardest problems are adversarial and economic, not architectural. Worth naming as
the next layer of depth beyond this bootcamp's scope.

---

## 17. What Comes After

AtlasMarket is the base for the rest of the program:

| Follow-on | Where |
|---|---|
| **Project 13** — AtlasMarket Support Assistant (RAG product Q&A) | Phase 7 |
| **Project 25** — Vendor analytics extension | Phase 11 |
| **Projects 26–28** — URL Shortener, Rate Limiter, Distributed Job Scheduler, built on this infrastructure and Phase 5's from-scratch Raft | Weeks 29–30 |

And, after Day 180, AtlasMarket is the portfolio project you keep growing — which
is why the deferred list in `docs/atlasmarket-roadmap-post-bootcamp.md` is a
roadmap, not a graveyard.
