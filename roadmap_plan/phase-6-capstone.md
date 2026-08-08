# PHASE 6 — Senior-Track Capstone
### Weeks 23–26 (4 weeks) · 24 working days

*(Note: the original overview sketched this as "Weeks 23–24, extended."
Fixed here to a clean 4 weeks so the 6 phases total 26 weeks — real
capstone work, especially AtlasMarket, needs the room.)*

---

## 1. Learning Goals
- Build a payment platform with idempotency and webhook handling done
  correctly — the two things that separate a toy payment integration from
  one that survives production.
- Harden a system for security: secrets management, audit logging, and a
  real threat-modeling pass, not just "add HTTPS."
- Run a genuine load test against your own infrastructure, read the
  results, and fix what breaks first.
- Rehearse system design interviews out loud, using your own 6 months of
  projects as concrete evidence instead of abstract answers.
- Gain enough React/TypeScript literacy to build a thin storefront
  consuming your own API and to talk to a frontend engineer as a peer.
- Kick off AtlasMarket — the marketplace capstone — honestly scoped as a
  **strong architectural skeleton with core flows working**, not a
  finished Amazon clone in 2 weeks. It's designed to keep growing after
  Day 182, which is the correct shape for a real portfolio centerpiece.

## 2. Technologies Introduced
Idempotency keys, webhook signature verification, secrets management
(`.env` → a real secrets manager pattern), `locust` load testing at a real
scale (not the light Week-4 check), React + TypeScript + Vite +
TanStack Query (frontend literacy only), system design interview technique.

---

## 3. PROJECT 9 — PayFlow (Payment Processing Platform)

**Business Problem:** A platform needs to accept payments, handle a
payment provider's async webhook confirmations reliably (a webhook can
arrive twice, arrive late, or arrive before your own request even
finishes), and maintain a ledger (reusing LedgerBase's double-entry model)
that's provably correct even under retries and duplicate events.

**Requirements**
- Functional: create a payment intent, process a (mocked) provider
  callback via webhook, reconcile against the ledger, handle refunds.
- Non-functional: **the same payment request retried by a flaky client
  must never charge twice** — this is the whole point of the project.

**Architecture:** builds directly on LedgerBase (Phase 4) — PayFlow calls
into `ledger-service` to record the payment as a journal entry, rather than
maintaining its own parallel money-tracking logic.

**Idempotency (the core mechanic):** every `POST /payments` requires an
`Idempotency-Key` header. The service stores `(key, request_hash, response,
status)` and, on a repeated key, returns the *original* response instead of
re-processing — you implement this from scratch and test it against a
literal duplicate request sent twice in a tight loop.

**Webhook handling:** the mock provider sends a signed webhook on payment
confirmation. You verify the signature (HMAC), handle out-of-order and
duplicate delivery (webhook processing is itself idempotent, keyed on the
provider's event ID), and reconcile the payment status only from the
webhook — never trust the initial API call's "it probably worked."

**ER Diagram (textual)**
```
payment_intents(id, idempotency_key UNIQUE, amount_cents, status, journal_entry_id NULL, created_at)
webhook_events(id, provider_event_id UNIQUE, payload, processed_at NULL, received_at)
refunds(id, payment_intent_id, amount_cents, journal_entry_id, created_at)
```

**API Design**
```
POST /payments                 # requires Idempotency-Key header
POST /webhooks/provider        # signature-verified, idempotent on provider_event_id
POST /payments/{id}/refund
GET  /payments/{id}
```

**Authentication & Permissions:** API-key-based auth for server-to-server
callers (distinct from the JWT user-auth used elsewhere — you explain when
each is appropriate).

**Security Hardening (this week's real focus):**
- Secrets (webhook signing secret, API keys) moved out of `.env` files
  into a proper secrets-manager pattern (even a local-only Docker secret
  or Vault-lite setup counts — the pattern matters more than the specific
  tool).
- Audit log: every payment/refund state change recorded with who/what/when,
  append-only.
- A written threat model: what happens if the webhook secret leaks? If an
  idempotency key is guessable? If a request replays after the key's
  retention window expires? You answer each in `docs/threat-model.md`.

**Testing Strategy:** the idempotency test is the centerpiece — fire the
exact same request twice concurrently and assert only one charge occurs
and both callers get the identical response; a webhook-replay test
(same provider event ID delivered 3 times) asserting only one ledger entry
results.

**Load Testing:** `locust` scenario simulating realistic concurrent
payment traffic (not the light Week-4 smoke test) — you find the actual
bottleneck (likely the idempotency-key lookup under contention) and fix it
(index, or a short-lived lock) with before/after numbers.

**Common Interview Questions**
1. Walk through your idempotency implementation end-to-end.
2. Why must webhook processing itself be idempotent, separately from the
   initial payment request?
3. What does your threat model say happens if the signing secret leaks,
   and what's your mitigation?
4. What did your load test reveal as the actual bottleneck, and how did
   you fix it?

**Possible Improvements:** idempotency key expiry/cleanup job, multi-
provider abstraction, partial refunds with multiple ledger entries.

**What Companies Usually Do Differently:** real payment platforms (Stripe)
treat idempotency as infrastructure-level, not per-endpoint — a client
library concern as much as a server one; worth naming even though you
built it per-endpoint here.

**Common Mistakes:** storing the idempotency key without the request hash
(so a *different* request accidentally reusing the same key silently
returns the wrong cached response); trusting the initial payment API call
result instead of the webhook; not handling webhook signature verification
failure explicitly (silently accepting unsigned payloads).

---

## 4. PROJECT 10 — AtlasMarket (Multi-Vendor E-Commerce Marketplace Capstone)

**Business Problem:** Independent vendors need a shared marketplace to
list products, manage their own inventory, and receive payouts, while
customers browse a unified catalog, check out across multiple vendors in
one order, and track fulfillment — the natural convergence point for every
service you've built: catalog (StockPilot's lineage), checkout (QuickServe),
multi-warehouse fulfillment (WareFlow), payments and ledger (LedgerBase +
PayFlow), and search (DocuVault's Elasticsearch work).

**Scope honesty, stated upfront:** two weeks is enough to stand up a real
architectural skeleton with core flows genuinely working end-to-end — not
enough for a feature-complete marketplace. That's the correct shape: this
project is designed to be your **ongoing portfolio project after Day 182**,
built on a foundation that's actually load-bearing instead of upfront-
overscoped the way the original AtlasCommerce plan was.

**Requirements (v1 scope — what actually ships in Weeks 25–26)**
- Vendor onboarding + product listing (reuses StockPilot's product/
  inventory model, now vendor-scoped).
- Unified catalog search (reuses DocuVault's Elasticsearch pattern).
- Cart → checkout → order split across vendors (reuses QuickServe's
  checkout logic, PayFlow's idempotent payment, LedgerBase's ledger for
  per-vendor payout tracking).
- Order fulfillment status per vendor (reuses WareFlow's warehouse/
  reservation concepts, vendor-scoped instead of warehouse-scoped).
- A thin React/TypeScript storefront (product list, cart, checkout) —
  frontend-literacy scope only, not a polished consumer product.

**Architecture — the payoff of 6 months of layering:**
```
Nginx gateway
  → auth-service            (Phase 4)
  → catalog-service         (StockPilot lineage, vendor-scoped, Elasticsearch-backed search)
  → order-service           (QuickServe checkout logic + WareFlow-style fulfillment, event-driven via outbox)
  → payment-service         (PayFlow, idempotent, calls ledger-service)
  → ledger-service           (LedgerBase, tracks per-vendor payouts)
storefront/ (React + TS + Vite + TanStack Query) — consumes the gateway
```
This is not a rewrite — it's an integration exercise. You are explicitly
instructed to **import and adapt**, not rebuild from scratch, wherever a
prior project's logic already solves the problem.

**ER Diagram (textual, delta from prior projects)**
```
vendors(id, name, payout_account_ref)
products(..., vendor_id -> vendors.id)             -- extends StockPilot's model
orders(..., split into order_vendor_groups per vendor for fulfillment/payout)
order_vendor_groups(id, order_id, vendor_id, status, journal_entry_id)
```

**What you explicitly do NOT build in these 2 weeks** (documented as
`docs/atlasmarket-roadmap-post-bootcamp.md`, so scope creep doesn't quietly
eat the timeline): reviews/ratings, recommendation engine, vendor
analytics dashboard, promotions/discounts across vendors, returns
workflow. All named, all deliberately deferred.

**Testing Strategy:** end-to-end test: browse → add items from 2 different
vendors → checkout once → verify two `order_vendor_groups` created, two
separate ledger entries, one idempotent payment.

**Frontend Literacy (React/TS, scoped narrowly):** product list page
(TanStack Query for data fetching/caching — you'll recognize the cache-
invalidation parallels to Redis immediately), cart state (local component
state, no Redux/Zustand needed at this scope — you note *why* global state
management isn't justified yet, an honest architectural call), checkout
form. Enough to read a frontend PR and ask the right questions, not enough
to call yourself a frontend engineer.

**Common Interview Questions**
1. Walk through the full checkout flow across the 5 services, start to
   finish, including where idempotency and the ledger come in.
2. How does `catalog-service` search stay consistent with vendor-scoped
   inventory changes?
3. What did you deliberately leave out of v1, and why was that the right
   call under a 2-week constraint?
4. If this needed to support 10,000 vendors tomorrow, what's the first
   thing that breaks?

**Possible Improvements:** everything in the explicitly-deferred list
above — this is the honest, ready-made answer to "what would you do next"
in an interview.

**What Companies Usually Do Differently:** real marketplaces invest
heavily in vendor trust/fraud systems and search relevance tuning long
before most of what you built here — worth naming as the next layer of
depth beyond this bootcamp's scope.

**Common Mistakes:** trying to build all the deferred features anyway
under time pressure (scope creep is the actual failure mode of this
project, more than any technical mistake); treating the storefront as
equally important as the backend integration (it isn't, for this
bootcamp's purpose).

---

## 5. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| Idempotency key demo (standalone, before PayFlow) | 23 | The mechanic in isolation |
| Webhook signature verification demo (HMAC) | 23 | Signature verification before applying it |
| `locust` load test scenario against a toy endpoint | 24 | Load testing methodology before the real PayFlow test |
| React + TanStack Query mini product list (dummy API) | 25 | Frontend data-fetching pattern before AtlasMarket |

---

## 6. Books & Documentation
- Stripe's own idempotency documentation (stripe.com/docs/api/idempotent_requests)
  — read Week 23, it's the industry-reference implementation.
- OWASP Top 10 (current edition) — read during Week 24's security week.
- `locust` official docs — Week 24.
- React docs (new react.dev) — "Describing the UI" + "Managing State"
  sections, TanStack Query "Quick Start" — Week 25.
- *The System Design Interview* volumes (Xu) — skim relevant chapters
  matching each mock interview topic during Week 26.

---

## 7. Weekly Interview Question Sets

**Week 23 — Idempotency, webhooks**
1. Idempotency key vs idempotent HTTP methods (PUT) — how are they different?
2. Why store the request hash alongside the idempotency key?
3. How do you verify a webhook signature, and what does it actually prove?

**Week 24 — Security, load testing**
1. Walk through one item from your threat model and its mitigation.
2. What did your load test's bottleneck teach you about where to optimize
   first?
3. Secrets manager vs `.env` — what's the actual risk `.env` carries in
   production?

**Week 25 — Marketplace architecture, frontend literacy**
1. Why does `order_vendor_groups` exist instead of one flat order table?
2. TanStack Query's cache — how is it similar to and different from your
   Redis cache-aside pattern from Phase 2?

**Week 26 — Full system design (mock interviews)**
1. Design a multi-vendor marketplace checkout system from scratch, 45
   minutes, using nothing but a whiteboard — then compare your answer to
   what you actually built.
2. Design a payment idempotency system from scratch, unprompted by your
   own PayFlow code.
3. Design a scalable product-search system, unprompted by your own
   DocuVault code.

---

## 8. Daily Plan — Week 23: PayFlow — Idempotency, Webhooks

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D133) | Idempotency key mechanics | Stripe idempotency docs | Standalone idempotency-key demo | New repo `payflow/`, `PaymentIntent` model + idempotency table | Model tests | `feat: payflow scaffold + idempotency table` | Q1 | Longest Increasing Path in a Matrix | PayFlow: duplicate idempotency keys with different request hashes | 3.5h |
| Tue (D134) | Request hashing alongside the key | — | — | `POST /payments` idempotency middleware/service | Test duplicate request returns identical cached response | `feat: idempotent payment creation` | Q2 | Distinct Subsequences | Duplicate Emails revisited | 3.5h |
| Wed (D135) | Race-testing idempotency | — | — | Fire the same request twice concurrently, assert single charge | Integration test under concurrency | `test: concurrent duplicate payment request` | — | Edit Distance | PayFlow: webhook_events received more than once per provider_event_id | 3.5h |
| Thu (D136) | HMAC webhook signature verification | — | Standalone HMAC verify demo | Mock provider webhook endpoint + signature verification | Test invalid signature rejected | `feat: webhook signature verification` | Q3 | Single Number | PayFlow: payment_intents stuck 'pending' longer than 10 minutes | 3.5h |
| Fri (D137) | Webhook idempotency (provider event ID) | — | — | Webhook processing idempotent on `provider_event_id`, reconciles ledger via `ledger-service` | Test triplicate webhook delivery results in one ledger entry | `feat: idempotent webhook processing + ledger reconciliation` | — | Number of 1 Bits | Employees Whose Manager Left the Company | 3.5h |
| Sat (D138) | **Review** | — | Redo idempotency demo from memory | — | Full suite | — | Answer Week-23 Qs unscripted | Review: redo Thursday's problem from memory — Single Number | Review: rewrite Tuesday's query from memory, then extend it — Duplicate Emails revisited | 2.5h |

---

## 9. Daily Plan — Week 24: Security Hardening, Load Testing

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D139) | OWASP Top 10 relevant to your stack | OWASP Top 10 | — | Refunds endpoint + API-key auth for server-to-server callers | Test refund creates correct reversing journal entry | `feat: refunds + api-key auth` | Q1 | Counting Bits | PayFlow: refunds exceeding their original payment amount | 3.5h |
| Tue (D140) | Secrets management patterns | — | — | Move webhook secret + API keys out of `.env` into a secrets-manager pattern | Verify no secret present in image/logs | `feat: secrets manager pattern` | — | Reverse Bits | PayFlow: same-day vs delayed refunds | 3.5h |
| Wed (D141) | Audit logging | — | — | Append-only audit log for payment/refund state changes | Test audit entries recorded for every state change | `feat: append-only audit log` | Q2 | Missing Number | PayFlow: EXPLAIN ANALYZE the idempotency-key lookup under load | 3.5h |
| Thu (D142) | Threat modeling | — | — | Write `docs/threat-model.md` (secret leak, key guessing, replay-after-expiry) | — | `docs: threat model` | — | Rotate Image | PayFlow: audit log for one payment_intent, ordered chronologically | 3.5h |
| Fri (D143) | `locust` load testing | locust docs | Toy-endpoint locust scenario | Realistic-concurrency PayFlow load test, find + fix the bottleneck | Before/after benchmark recorded | `perf: fix idempotency-lookup bottleneck under load` | Q3 | Spiral Matrix | Find Followers Count | 3.5h |
| Sat (D144) | **Review** | — | Redo HMAC verify demo from memory | Tag `v0.1-payflow` | Full suite | — | Answer Week-24 Qs unscripted | Review: redo Thursday's problem from memory — Rotate Image | Review: rewrite Tuesday's query from memory, then extend it — PayFlow: same-day vs delayed refunds | 2.5h |

---

## 10. Daily Plan — Week 25: AtlasMarket Architecture + Integration Sprint (part 1)

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D145) | Integration planning — what to reuse vs rebuild | — | — | New repo `atlasmarket/`, `docs/architecture.md` mapping each service to its origin project | — | `docs: atlasmarket architecture + service map` | Q1 | Set Matrix Zeroes | AtlasMarket: revenue per vendor this month | 3.5h |
| Tue (D146) | Vendor-scoping the catalog | — | — | Adapt StockPilot's product model: add `vendor_id`, vendor onboarding endpoint | Test vendor-scoped product creation | `feat: vendor-scoped catalog` | — | Happy Number | Product Sales Analysis III | 3.5h |
| Wed (D147) | Vendor-scoped search | — | — | Adapt DocuVault's ES sync pattern to index vendor-scoped products | Test search respects vendor filters | `feat: vendor-scoped catalog search` | Q2 | Plus One | AtlasMarket: vendors with no products listed | 3.5h |
| Thu (D148) | React/TS fundamentals, Vite setup | react.dev "Describing the UI" | — | `storefront/` scaffold (Vite + React + TS), product list page with TanStack Query | Basic render test | `feat: storefront scaffold + product list` | — | Pow(x, n) | AtlasMarket: top 5 vendors by order count | 3.5h |
| Fri (D149) | TanStack Query caching | TanStack Query "Quick Start" | Mini product list against a dummy API | Cart state (local component state) + cart UI | — | `feat: storefront cart` | Q3 | Merge Sorted Array | The Most Recent Three Orders | 3.5h |
| Sat (D150) | **Review** | — | Explain TanStack Query cache vs your Redis cache-aside pattern, out loud | — | — | — | Answer Week-25 Qs unscripted | Review: redo Thursday's problem from memory — Pow(x, n) | Review: rewrite Tuesday's query from memory, then extend it — Product Sales Analysis III | 2.5h |

---

## 11. Daily Plan — Week 26: AtlasMarket Integration Sprint (part 2), Mock Interviews, Program Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D151) | Multi-vendor checkout design | — | — | Checkout: cart → split into `order_vendor_groups` → PayFlow idempotent payment → per-vendor ledger entries | Test 2-vendor checkout creates 2 groups, 1 payment, 2 ledger entries | `feat: multi-vendor checkout` | Q1 | Design Twitter | AtlasMarket: orders split across 2+ vendors | 3.5h |
| Tue (D152) | Per-vendor fulfillment status | — | — | Adapt WareFlow's status concepts to `order_vendor_groups` | Integration test status updates independently per vendor | `feat: per-vendor fulfillment status` | — | LFU Cache | AtlasMarket: per-vendor payout reconciliation | 3.5h |
| Wed (D153) | Checkout UI, end-to-end wiring | — | — | Storefront checkout form wired to the real API | Manual end-to-end run: browse → cart → checkout, verified live | `feat: storefront checkout flow` | Q2 | Word Search II | Capstone review: rewrite Week 12's partition-aware query from memory | 3.5h |
| Thu (D154) | Mock system design interview #1 | System Design Interview (Xu), relevant chapter | — | Design multi-vendor checkout from scratch on a whiteboard (no code), then compare to what you built | — | `docs: mock interview 1 notes` | Q1 mock, timed | Merge k Sorted Lists | Capstone review: rewrite Week 6's window-function ranking query from memory | 3.5h |
| Fri (D155) | Mock system design interview #2 + #3 | — | — | Design payment idempotency + product search from scratch, unprompted | — | `docs: mock interviews 2-3 notes` | Q2, Q3 mock, timed | Alien Dictionary | Capstone: the one query you'd hand an interviewer | 3.5h |
| Sat (D156) | **Program wrap** | — | — | `docs/atlasmarket-roadmap-post-bootcamp.md` (deferred features), `docs/postmortem-phase6.md`, full 6-month retrospective across all 10 projects, tag `v1.0-bootcamp-complete` | Full suite, all services | `docs: 6-month retrospective + post-bootcamp roadmap` | Full mock behavioral + system design round, timed, no notes | Review: redo Thursday's problem from memory — Merge k Sorted Lists | Review: rewrite Tuesday's query from memory, then extend it — AtlasMarket: per-vendor payout reconciliation | 2.5h |

---

## 12. Deliverables & GitHub Milestones

**Milestone: `Phase 6 — PayFlow v0.1 + AtlasMarket v0.1 (capstone)`**
- [ ] Idempotent payment creation, proven under concurrent duplicate requests
- [ ] Webhook signature verification + idempotent webhook processing
- [ ] `docs/threat-model.md` written and addressed
- [ ] Load test bottleneck found and fixed, before/after numbers recorded
- [ ] AtlasMarket: vendor-scoped catalog + search, multi-vendor checkout,
      per-vendor ledger + fulfillment status, all reusing prior projects'
      logic (documented in `docs/architecture.md`'s service map)
- [ ] Thin React/TS storefront: product list, cart, checkout, working
      end-to-end against the real API
- [ ] `docs/atlasmarket-roadmap-post-bootcamp.md` — explicit deferred scope
- [ ] 3 timed mock system-design interviews completed and logged
- [ ] Tag: `v1.0-bootcamp-complete`

## 13. Skills Acquired Checklist
- [ ] Idempotency keys — implemented and race-tested
- [ ] Webhook signature verification + idempotent webhook processing
- [ ] Threat modeling as a concrete written exercise
- [ ] Real load testing with `locust`, bottleneck found and fixed
- [ ] Integrating multiple prior services into one coherent system, with
      honest scope discipline (documented deferrals, not silent scope creep)
- [ ] React + TypeScript + Vite + TanStack Query — enough to build a thin
      UI and communicate with frontend engineers as a peer
- [ ] System design interview technique, rehearsed out loud, timed,
      grounded in your own 6 months of concrete decisions

---

## 14. What Comes After Day 182

AtlasMarket is designed to be unfinished on purpose. The honest next steps
— reviews/ratings, recommendations, vendor analytics, promotions, returns
— are sitting in `docs/atlasmarket-roadmap-post-bootcamp.md`, ready to
become your ongoing portfolio project. Every one of those features now has
6 months of infrastructure underneath it to land on, instead of being
built on the upfront-overscoped foundation the original AtlasCommerce plan
would have produced.
