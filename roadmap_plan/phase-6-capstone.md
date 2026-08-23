# PHASE 6 — Senior-Track Capstone
### Weeks 25–30 (6 weeks) · 36 working days

*(Note: the original overview sketched this as "Weeks 25–26, extended."
Fixed here to a clean 6 weeks — real capstone work, especially
AtlasMarket plus the system-design real-builds, needs the room.)*

---

## 1. Learning Goals
- Build a payment platform with idempotency and webhook handling done
  correctly — the two things that separate a toy payment integration from
  one that survives production.
- Harden a system for security: a real secrets manager (HashiCorp Vault,
  not just a better-organized `.env`), audit logging, and a real
  threat-modeling pass, not just "add HTTPS."
- Deploy AtlasMarket to a real cloud account (AWS or GCP) with
  least-privilege IAM, a VPC with public/private subnets, and a managed
  database — the first time all year infrastructure isn't a single VPS
  running Docker Compose.
- Run a genuine load test against your own infrastructure, read the
  results, derive a real SLO and error budget from them, and write an
  on-call runbook you then test blind against a self-inflicted incident.
- Write a real backup/restore drill for LedgerBase's financial data and
  prove, with a reconciled report, that the restore actually works — and
  write two narrow, honest compliance scoping notes (PCI-DSS for PayFlow,
  a HIPAA-adjacent note for CarePoint) precise enough to survive a real
  interview follow-up.
- Add a bulkhead to AtlasMarket's gateway (isolating each downstream
  service's connection pool) and ship one real change behind a feature
  flag with a percentage-based canary rollout.
- Rehearse system design interviews out loud using the full
  `system-design-problems.md` bank — one or two problems worked every
  week from Week 19 on, not crammed into three days at the end — and
  rehearse behavioral interviews the same way, using your own 6 months of
  concrete incidents as evidence instead of generic answers.
- Ship your fourth React/TypeScript app this year — AtlasMarket's
  storefront — building on the habits from CarePoint, FleetTrack, and
  DocuVault instead of starting from zero, add a real Playwright
  end-to-end test on top of the component tests, and be able to ship a
  small frontend feature yourself, not just talk to a frontend engineer as
  a peer.
- Kick off AtlasMarket — the marketplace capstone — honestly scoped as a
  **strong architectural skeleton with core flows working**, not a
  finished Amazon clone in 2 weeks. It's designed to keep growing after
  Day 180, which is the correct shape for a real portfolio centerpiece.

## 2. Technologies Introduced
Idempotency keys, webhook signature verification, HashiCorp Vault (dynamic
secrets, KV engine, fail-closed startup — replacing `.env` for anything
that touches production), a real cloud account (AWS or GCP): least-
privilege IAM, a VPC with public/private subnets, a managed Postgres (RDS
or Cloud SQL), `locust` load testing at a real scale (not the light Week-4
check), SLO/SLI/error-budget framework + an on-call runbook + a live
incident drill, `pg_dump`/`pg_restore` backup/DR drill, PCI-DSS/HIPAA
compliance-scoping vocabulary, the bulkhead pattern (bounded per-
downstream connection pools), feature flags + percentage-based canary
release, Playwright (end-to-end browser testing), React + TypeScript +
Vite + TanStack Query, system design interview technique.

Deliberately manual, not Terraform: the cloud deployment this phase is
done by hand via the `aws`/`gcloud` CLI or console — the same "manual for
now" call Phase 1 made about StockPilot's first deploy — so Phase 10/11's
Terraform lessons later solve a felt problem ("I don't want to click
through this again") instead of being taught in the abstract.

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
- Regulatory scope is a related but separate question the threat model
  above doesn't answer: `docs/pci-scope-note.md` for PayFlow (which
  PCI-DSS SAQ level applies given the mocked provider owns raw card
  numbers, never you; why tokenization plus webhook-based confirmation
  keeps you out of the highest-scope tier) and `docs/hipaa-considerations-
  note.md` for CarePoint (patient documents in a portfolio project aren't
  literally subject to HIPAA, but the access controls, audit logging, and
  encryption-at-rest you'd need *if* they were is worth stating precisely
  — a healthcare-domain interview question will probe exactly this). Both
  are narrow, honest scoping notes, not a real audit — the same discipline
  as every other "named precisely, not oversold" call this roadmap makes.

**Testing Strategy:** the idempotency test is the centerpiece — fire the
exact same request twice concurrently and assert only one charge occurs
and both callers get the identical response; a webhook-replay test
(same provider event ID delivered 3 times) asserting only one ledger entry
results.

**Load Testing:** `locust` scenario simulating realistic concurrent
payment traffic (not the light Week-4 smoke test) — you find the actual
bottleneck (likely the idempotency-key lookup under contention) and fix it
(index, or a short-lived lock) with before/after numbers.

**Reliability — SLO, On-Call, Incident Drill:** derive a real SLO from
Friday's load-test numbers (e.g. "99.5% of `POST /payments` requests
succeed in under 800ms, measured over a rolling 30 days") and the error
budget it implies. Write a one-page on-call runbook titled "payment
success rate has dropped": what to check first, second, third, using the
Prometheus/Grafana/Sentry stack already built in Phase 4. Then run a real
drill on Saturday — inject a failure (kill `ledger-service`, the one
downstream PayFlow depends on), follow the runbook blind, "page" yourself,
resolve it, and write a blameless postmortem.

**Backup & Disaster Recovery:** LedgerBase (Phase 4) has held financial
data since Week 16 with no stated backup story — a real gap for a system
built around double-entry correctness. Take a real `pg_dump` backup, write
down the RPO/RTO you're targeting with reasoning (not arbitrary numbers),
deliberately corrupt data in a scratch copy, restore from the backup, and
verify the trial-balance report reconciles identically to before.
`docs/backup-dr-plan.md`.

**Common Interview Questions**
1. Walk through your idempotency implementation end-to-end.
2. Why must webhook processing itself be idempotent, separately from the
   initial payment request?
3. What does your threat model say happens if the signing secret leaks,
   and what's your mitigation?
4. What did your load test reveal as the actual bottleneck, and how did
   you fix it?
5. Walk through your SLO and how you derived the error budget from it.
6. What did your incident drill reveal that your runbook didn't already
   account for?
7. What's your RPO/RTO for LedgerBase, and why those numbers specifically?
8. What keeps PayFlow out of the highest PCI-DSS scope tier?

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
project is designed to be your **ongoing portfolio project after Day 180**,
built on a foundation that's actually load-bearing instead of upfront-
overscoped the way the original AtlasCommerce plan was.

**Requirements (v1 scope — what actually ships in Weeks 27–28)**
- Vendor onboarding + product listing (reuses StockPilot's product/
  inventory model, now vendor-scoped).
- Unified catalog search (reuses DocuVault's Elasticsearch pattern).
- Cart → checkout → order split across vendors (reuses QuickServe's
  checkout logic, PayFlow's idempotent payment, LedgerBase's ledger for
  per-vendor payout tracking).
- Order fulfillment status per vendor (reuses WareFlow's warehouse/
  reservation concepts, vendor-scoped instead of warehouse-scoped).
- A real React/TypeScript storefront (product list, cart, checkout) — your
  fourth React/TS app this year (after CarePoint's schedule view,
  FleetTrack's dispatcher dashboard, DocuVault's search page), so this one
  is built on established habits, not learned from zero. Still honestly
  scoped: functional and tested, not a polished consumer product.

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
prior project's logic already solves the problem. The gateway calls all
five services synchronously — this is also where a **bulkhead** earns its
keep for the first time: a bounded connection pool per downstream service
so a saturated `payment-service` can't starve calls to a perfectly healthy
`catalog-service`, on top of the retry+circuit-breaker pattern already
built in Phase 4.

**Real cloud deployment:** the gateway and `catalog-service` deploy to a
real AWS or GCP account this phase — least-privilege IAM, a VPC with the
database in a private subnet, security groups scoped to exactly the needed
ports, and a managed Postgres instead of a container. `docs/cloud-
deployment-notes.md` records the IAM policy, the VPC layout, and a monthly
cost estimate.

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

**Frontend (React/TS, fourth app — built on established habits):** product
list page (TanStack Query for data fetching/caching — by now the cache-
invalidation parallels to your own Redis cache-aside pattern are second
nature, not a new idea), cart state (local component state, no Redux/
Zustand needed at this scope — you note *why* global state management
isn't justified yet, an honest architectural call, same discipline as
every "not yet" decision this whole curriculum makes), checkout form wired
to the real payment/order flow. Four builds in is enough to read a
frontend PR and ask the right questions, and to ship a small feature
yourself without a frontend engineer's help — still not the same as being
a frontend specialist, and the plan doesn't pretend otherwise. The
checkout-flow wiring itself ships behind a hand-rolled feature flag
(a config table + `is_enabled(flag, user_id)` check, percentage rollout)
— dark, then ramped 10% → 100% while watching Grafana, the first time all
year a change ships as a canary instead of all-at-once. A Playwright test
drives a real browser through the full checkout flow end-to-end, on top
of (not instead of) the React Testing Library component tests — the class
of bug a component test structurally can't catch (a broken route, a CSS
issue hiding the submit button) gets a real regression test for the first
time this year.

**Common Interview Questions**
1. Walk through the full checkout flow across the 5 services, start to
   finish, including where idempotency and the ledger come in.
2. How does `catalog-service` search stay consistent with vendor-scoped
   inventory changes?
3. What did you deliberately leave out of v1, and why was that the right
   call under a 2-week constraint?
4. If this needed to support 10,000 vendors tomorrow, what's the first
   thing that breaks?
5. Why does the database sit in a private subnet, and what's the blast
   radius if the gateway's IAM role leaked versus if you'd used the root
   account?
6. Walk through what your bulkhead does that the circuit breaker alone
   doesn't.
7. How does your feature flag's percentage rollout guarantee the same
   user always lands on the same side of it?

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

## 5. PROJECTS 26–28 — System Design, Built For Real

**Why real builds, not more paper designs:** `system-design-problems.md`
has had you *design* 19 systems on paper since Week 19. Paper designs are
necessary but not sufficient — an interviewer can tell the difference
between "I designed this on a whiteboard once" and "I hit the exact
edge case my design didn't account for and fixed it." These two weeks
take the three problems with the best return on real implementation time
and ship each as a small, real, tested service. Numbered 26-28 (after
AtlasMarket) rather than slotted in sequentially, since they're built
here in Phase 6 but conceptually belong beside the whole 25-project list.

### PROJECT 26 — URL Shortener (SD1, Week 29 Mon–Tue)

**Requirements:** `POST /shorten {url} -> {short_code}`, `GET /{short_code}`
redirects (301) to the original. Short codes are base62, generated from a
counter (not random — you argue why in your README, tying back to SD1's
"counter + base62 vs hash-based vs random" deep-dive). Deleted URLs return
404, not a redirect to a dead link.

**What makes it real, not a toy:** a Redis cache in front of the mapping
table for hot redirects (cache-aside, the exact pattern from Phase 2 —
you're applying it, not relearning it), a rate limiter on `POST /shorten`
reusing SD2's work (see below) instead of an ad hoc one, and a load test
proving the redirect path holds up under realistic QPS with the cache
warm vs cold.

**Testing Strategy:** collision test (two `POST /shorten` calls for
different URLs never produce the same code); cache-invalidation test (a
deleted URL's cached redirect stops working immediately, not after TTL
expiry); load test comparing p95 redirect latency cache-cold vs cache-warm.

### PROJECT 27 — Rate Limiter Service (SD2, Week 29 Wed–Thu)

**Requirements:** a standalone service (not a library) that any of your
other 27 systems could point at: `POST /check {key, limit, window} ->
{allowed: bool, remaining: int}`. Implement two algorithms — token bucket
and sliding-window-counter — behind the same interface, and load-test both
to produce your own numbers for the memory/accuracy trade-off SD2 asks you
to argue on paper.

**What makes it real, not a toy:** it's genuinely distributed — run 3
instances of your own rate-limiter service behind Nginx (Phase 4's
reverse-proxy skill, reused) backed by one shared Redis, and prove a
client hammering all 3 instances still gets rate-limited correctly (this
is the exact "how does the limiter stay correct when replicated across 5
API gateway instances" question SD2 poses, now answered with a passing
test instead of an assertion).

**Testing Strategy:** correctness test per algorithm against a fixed
request schedule with known expected outcomes; the multi-instance test
above (the centerpiece); a benchmark comparing token-bucket vs sliding-
window-counter memory footprint at 100k tracked keys.

### PROJECT 28 — Distributed Job Scheduler (SD14, Week 30 Mon–Wed)

**Requirements:** `POST /jobs {cron_expr, payload} -> {job_id}`; the
scheduler dispatches each job exactly once per scheduled tick, even though
the scheduler itself runs as multiple processes for availability.

**What makes it real, not a toy:** this is where Phase 5's from-scratch
Raft implementation stops being an academic exercise and becomes
infrastructure — the scheduler's multiple processes form a Raft cluster,
and only the current leader dispatches jobs (reusing Phase 5 Week 24
Friday's toy version, hardened here into an actual service with real
persistence and an HTTP API in front of it). Job handlers are idempotent
(same discipline as every queue consumer since Phase 3), so a
dispatched-but-crashed job can be safely retried without double-running.

**Testing Strategy:** kill the leader process mid-dispatch-decision,
assert exactly one job execution results, never zero, never two (the
direct payoff of Phase 5's partition/torture testing); a 24-hour-simulated
run (compressed via `freezegun`, the same technique from every Celery Beat
test since Phase 2) asserting every scheduled tick fired exactly once.

**Common Interview Questions (all three)**
1. What's the one thing each of these has that your paper design on SD1/
   SD2/SD14 didn't force you to think about?
2. For the rate limiter: walk through what actually happens when 3
   instances race to check the same key at the same millisecond.
3. For the job scheduler: why does leader-only dispatch matter more than
   just "the scheduler works" — what breaks with two leaders?
4. If you had to productionize one of these three for real, which one
   needs the most additional work, and what specifically?

**Common Mistakes:** building all three as single-process toys instead of
proving the *distributed* property each one is actually about (a rate
limiter that's only ever tested from one process proves nothing new);
skipping the load test and only checking correctness at low volume, where
every naive implementation looks fine.

---

## 6. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| Idempotency key demo (standalone, before PayFlow) | 23 | The mechanic in isolation |
| Webhook signature verification demo (HMAC) | 23 | Signature verification before applying it |
| `locust` load test scenario against a toy endpoint | 24 | Load testing methodology before the real PayFlow test |
| `pg_dump`/`pg_restore` round-trip on a throwaway database | 24 | Backup/restore mechanics before the real LedgerBase drill |
| Shared component extraction (`Button`/`Card`) from 3 prior frontends | 25 | Componentization/reuse — the frontend analogue of Phase 1's layered architecture |
| Hand-rolled feature-flag service (config table + percentage rollout) | 26 | Feature flags before applying one to the real checkout ship |

---

## 7. Books & Documentation
- Stripe's own idempotency documentation (stripe.com/docs/api/idempotent_requests)
  — read Week 25, it's the industry-reference implementation.
- OWASP Top 10 (current edition) — read during Week 26's security week.
- HashiCorp Vault docs — "Getting Started" + "Secrets Engines: KV" — Week 26.
- AWS docs: "IAM best practices," "VPC and subnets," "Security groups" (or
  GCP equivalents: "IAM overview," "VPC network overview," "Firewall
  rules") — Week 26.
- `locust` official docs — Week 26.
- Google SRE Book (sre.google/books, free online) — Ch. 4 (Service Level
  Objectives), the On-Call chapter, the Postmortem chapter — Week 26.
- PostgreSQL docs — "Backup and Restore" chapter — Week 26.
- PCI Security Standards Council — "PCI DSS Quick Reference Guide" (free);
  HHS.gov — "HIPAA Security Rule" summary page — Week 26.
- *Release It!* (Michael Nygard) — Stability Patterns chapter (bulkhead
  section specifically, retry/circuit-breaker are a Phase 4 refresher by
  now) — Week 28.
- React Router docs "Tutorial" — Week 27 (your first multi-page frontend;
  the 3 prior React apps this year were single-view, so this is genuinely
  new, unlike React/TanStack Query itself, which is a refresher by now).
- React Testing Library docs "Example" — Week 27 (first real component test).
- Playwright documentation (playwright.dev) — "Getting started," "Writing
  tests" — Week 28.
- *The System Design Interview* volumes (Xu) — skim relevant chapters
  matching each mock interview topic during Week 28.
- `system-design-problems.md` and `behavioral-interview-questions.md` —
  reused every week from Week 19 through Week 28 (see each week's
  interview-question set below for which entries land when).
- Ongaro & Ousterhout, "In Search of an Understandable Consensus
  Algorithm" (raft.github.io/raft.pdf) — reused, not reread cover to
  cover, as a reference during Week 30's job-scheduler build.

---

## 8. Weekly Interview Question Sets

**Week 25 — Idempotency, webhooks**
1. Idempotency key vs idempotent HTTP methods (PUT) — how are they different?
2. Why store the request hash alongside the idempotency key?
3. How do you verify a webhook signature, and what does it actually prove?
4. Also work SD18 (Payment System) and SD12 (Ticket-Booking System) from
   `system-design-problems.md` this week — SD18 is the one problem this
   whole bank where you have direct, shipped, load-bearing experience.
5. Behavioral: pick 2 questions from `behavioral-interview-questions.md`
   §"Dealing with mistakes, bugs, and being wrong" and write STAR answers.

**Week 26 — Security, cloud, reliability, compliance**
1. Walk through one item from your threat model and its mitigation.
2. What did your load test's bottleneck teach you about where to optimize
   first?
3. Secrets manager vs `.env` — what's the actual risk `.env` carries in
   production?
4. Walk through your SLO and how you derived the error budget from it.
5. What's your RPO/RTO for LedgerBase, and why those numbers specifically?
6. What keeps PayFlow out of the highest PCI-DSS scope tier?
7. Also work SD9 (Notification System), SD17 (Distributed File Storage),
   and SD19 (Distributed Logging & Metrics Pipeline — the system
   underneath the Prometheus/Grafana/Sentry stack you've used since
   Phase 4, from the other side) this week.
8. Behavioral: 2 questions from §"Working under pressure / production
   incidents" — use the incident drill and backup/DR drill as evidence.

**Week 27 — Marketplace architecture, storefront**
1. Why does `order_vendor_groups` exist instead of one flat order table?
2. TanStack Query's cache — how is it similar to and different from your
   Redis cache-aside pattern from Phase 2?
3. Client-side routing (React Router) vs server-side routing — what
   actually changes on navigation in each, and why does it matter for
   perceived performance?
4. Also work SD11 (Ride-Sharing Service) and SD13 (Collaborative Document
   Editor) this week.
5. Behavioral: 2 questions from §"Scope, prioritization, and saying no" —
   AtlasMarket's v1 scope cut is the direct evidence.

**Week 28 — Full system design + behavioral marathon, program wrap**
1. Design a multi-vendor marketplace checkout system from scratch, 45
   minutes, using nothing but a whiteboard — then compare your answer to
   what you actually built.
2. Design a payment idempotency system from scratch, unprompted by your
   own PayFlow code.
3. Design a scalable product-search system, unprompted by your own
   DocuVault code.
4. Walk through what your bulkhead does that the circuit breaker alone
   doesn't, and how your feature flag's rollout guarantees a stable
   per-user assignment.
5. Also close out the bank: SD10 (Video Streaming), SD16 (Proximity/
   Nearby-Search), and SD20 — design AtlasMarket itself from a blank page,
   then compare the fresh answer against `docs/architecture.md`.
6. Behavioral: a full pass through `behavioral-interview-questions.md` —
   by Saturday you should be able to answer any question in the bank in
   under 90 seconds, unscripted, using a real project as evidence.

**Week 29 — URL Shortener + Rate Limiter, built for real**
1. Why counter-based base62 codes here instead of random or hash-based —
   what did you argue in your README?
2. Walk through exactly what happens when 3 rate-limiter instances race
   to check the same key at the same millisecond.
3. Token bucket vs sliding-window-counter — what did your benchmark show
   about the memory/accuracy trade-off?
4. What's the one thing building these for real forced you to handle that
   the SD1/SD2 paper designs didn't?

**Week 30 — Distributed Job Scheduler, built for real; final wrap**
1. Why does leader-only dispatch matter more than "the scheduler works" —
   what breaks with two leaders dispatching the same job?
2. Walk through your leader-kill-mid-dispatch test — what exactly does it
   prove that a happy-path test can't?
3. If you had to productionize one of Projects 26-28 for real, which one
   needs the most additional work, and specifically what?
4. Looking back at Day 1 vs Day 180 — what's the biggest gap that closed?

---

## 9. Daily Plan — Week 25: PayFlow — Idempotency, Webhooks

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D145) | Idempotency key mechanics | Stripe idempotency docs | Standalone idempotency-key demo | New repo `payflow/`, `PaymentIntent` model + idempotency table | Model tests | `feat: payflow scaffold + idempotency table` | Q1 | Longest Increasing Path in a Matrix | PayFlow: duplicate idempotency keys with different request hashes | 3.5h |
| Tue (D146) | Request hashing alongside the key | — | — | `POST /payments` idempotency middleware/service | Test duplicate request returns identical cached response | `feat: idempotent payment creation` | Q2 | Distinct Subsequences | Duplicate Emails revisited | 3.5h |
| Wed (D147) | Race-testing idempotency | — | — | Fire the same request twice concurrently, assert single charge | Integration test under concurrency | `test: concurrent duplicate payment request` | — | Edit Distance | PayFlow: webhook_events received more than once per provider_event_id | 3.5h |
| Thu (D148) | HMAC webhook signature verification | — | Standalone HMAC verify demo | Mock provider webhook endpoint + signature verification | Test invalid signature rejected | `feat: webhook signature verification` | Q3 | Single Number | PayFlow: payment_intents stuck 'pending' longer than 10 minutes | 3.5h |
| Fri (D149) | Webhook idempotency (provider event ID) | — | — | Webhook processing idempotent on `provider_event_id`, reconciles ledger via `ledger-service` | Test triplicate webhook delivery results in one ledger entry | `feat: idempotent webhook processing + ledger reconciliation` | — | Number of 1 Bits | Employees Whose Manager Left the Company | 3.5h |
| Sat (D150) | **Review** | — | Redo idempotency demo from memory | — | Full suite | — | Answer Week-25 Qs unscripted | Review: redo Thursday's problem from memory — Single Number | Review: rewrite Tuesday's query from memory, then extend it — Duplicate Emails revisited | 2.5h |

---

## 10. Daily Plan — Week 26: Security Hardening, Load Testing

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D151) | OWASP Top 10 relevant to your stack; backup & disaster recovery — LedgerBase has held financial data since Week 16 with no stated backup story | OWASP Top 10 + Postgres docs "Backup and Restore" | `pg_dump`/`pg_restore` round-trip on a throwaway DB | Refunds endpoint + API-key auth for server-to-server callers; real `pg_dump` backup of LedgerBase, RPO/RTO written down with reasoning, deliberate corruption in a scratch copy, restore, verify the trial-balance report reconciles identically; `docs/backup-dr-plan.md` | Test refund creates correct reversing journal entry; restored trial-balance report matches the pre-corruption report exactly | `feat: refunds + api-key auth; docs: ledgerbase backup/dr drill verified` | Q1 | Counting Bits | PayFlow: refunds exceeding their original payment amount | 4h |
| Tue (D152) | Secrets management with a real secrets manager (HashiCorp Vault) — dynamic secrets, leasing/rotation vs a static `.env` file | Vault docs "Getting Started" + "Secrets Engines" | Run Vault in dev mode, write/read one secret via the CLI, then via its HTTP API | Add `vault` to Docker Compose; move webhook secret + API keys out of `.env` into Vault's KV engine, app reads them via the API at startup | Verify no secret present in image/logs/env dump; test the app fails closed (refuses to start) if Vault is unreachable rather than falling back to a default | `feat: hashicorp vault for secrets, drop .env in prod` | — | Reverse Bits | PayFlow: same-day vs delayed refunds | 3.5h |
| Wed (D153) | Audit logging; cloud IAM & VPC design — least-privilege roles, public/private subnets | AWS "IAM best practices" + "VPC and subnets" (or GCP equivalents) | Sketch the IAM role's exact permission set and the VPC's subnet layout on paper before creating anything | Append-only audit log for payment/refund state changes; create the cloud account, the least-privilege IAM role, and a VPC with public/private subnets for AtlasMarket's future deploy | Test audit entries recorded for every state change; verify the IAM role has zero permissions beyond what's listed on paper | `feat: append-only audit log; chore: cloud account, iam role, vpc scaffold` | Q2 | Missing Number | PayFlow: EXPLAIN ANALYZE the idempotency-key lookup under load | 4h |
| Thu (D154) | Threat modeling; compliance scoping — PCI-DSS, HIPAA-adjacent considerations | PCI DSS Quick Reference Guide + HHS.gov HIPAA Security Rule summary | — | Write `docs/threat-model.md` (secret leak, key guessing, replay-after-expiry); `docs/pci-scope-note.md` (PayFlow) and `docs/hipaa-considerations-note.md` (CarePoint) | — | `docs: threat model + pci-dss/hipaa-adjacent compliance scoping notes` | — | Rotate Image | PayFlow: audit log for one payment_intent, ordered chronologically | 4h |
| Fri (D155) | `locust` load testing; SLOs/SLIs/error budgets, writing an on-call runbook | locust docs + Google SRE Book Ch.4 (SLOs) | Toy-endpoint locust scenario | Realistic-concurrency PayFlow load test, find + fix the bottleneck; write the payment-path SLO + error budget derived from the load-test numbers, and the "payment success rate dropped" on-call runbook | Before/after benchmark recorded | `perf: fix idempotency-lookup bottleneck under load; docs: payflow slo + on-call runbook` | Q3 | Spiral Matrix | Find Followers Count | 4h |
| Sat (D156) | **Review + live incident drill** | Google SRE Book On-Call/Postmortem chapters | Redo HMAC verify demo from memory | Run the incident drill: kill `ledger-service`, follow Friday's runbook blind, resolve it, write a blameless postmortem; tag `v0.1-payflow` | Full suite | `docs: incident drill postmortem` | Answer Week-26 Qs unscripted | Review: redo Thursday's problem from memory — Rotate Image | Review: rewrite Tuesday's query from memory, then extend it — PayFlow: same-day vs delayed refunds | 3h |

---

## 11. Daily Plan — Week 27: AtlasMarket Architecture + Integration Sprint (part 1), Storefront

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D157) | Integration planning — what to reuse vs rebuild | — | — | New repo `atlasmarket/`, `docs/architecture.md` mapping each service to its origin project | — | `docs: atlasmarket architecture + service map` | Q1 | Set Matrix Zeroes | AtlasMarket: revenue per vendor this month | 3.5h |
| Tue (D158) | Vendor-scoping the catalog | — | — | Adapt StockPilot's product model: add `vendor_id`, vendor onboarding endpoint | Test vendor-scoped product creation | `feat: vendor-scoped catalog` | — | Happy Number | Product Sales Analysis III | 3.5h |
| Wed (D159) | Vendor-scoped search | — | — | Adapt DocuVault's ES sync pattern to index vendor-scoped products | Test search respects vendor filters | `feat: vendor-scoped catalog search` | Q2 | Plus One | AtlasMarket: vendors with no products listed | 3.5h |
| Thu (D160) | Multi-page navigation with React Router — the one piece your 3 prior single-view frontends didn't need | React Router docs "Tutorial" | Extract a shared `Button`/`Card` component from copy-pasted markup across `carepoint-web`, `fleettrack-web`, `docuvault-web` into a tiny local component set `storefront/` can start from | `storefront/` scaffold (Vite + React + TS), React Router routes for product list / cart / checkout, product list page with TanStack Query | Basic render test per route | `feat: storefront scaffold + routed product list` | — | Pow(x, n) | AtlasMarket: top 5 vendors by order count | 3.5h |
| Fri (D161) | TanStack Query caching, cart state design | TanStack Query "Quick Start" | Write one React Testing Library test for the cart's add/remove logic | Cart state (local component state) + cart UI, wired to the router's cart route | Testing Library test for cart add/remove passes | `feat: storefront cart + cart test` | Q3 | Merge Sorted Array | The Most Recent Three Orders | 3.5h |
| Sat (D162) | **Review** | — | Explain TanStack Query cache vs your Redis cache-aside pattern, out loud | — | — | — | Answer Week-27 Qs unscripted | Review: redo Thursday's problem from memory — Pow(x, n) | Review: rewrite Tuesday's query from memory, then extend it — Product Sales Analysis III | 2.5h |

---

## 12. Daily Plan — Week 28: AtlasMarket Integration Sprint (part 2), Mock Interviews

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D163) | Multi-vendor checkout design; the bulkhead pattern — bounded per-downstream connection pools on the gateway | *Release It!* (Nygard) bulkhead section | Bounded semaphore demo: one slow "dependency" starves a shared pool, then a bulkhead fixes it | Checkout: cart → split into `order_vendor_groups` → PayFlow idempotent payment → per-vendor ledger entries; bulkhead pools added to the gateway's calls to each of the 5 downstream services | Test 2-vendor checkout creates 2 groups, 1 payment, 2 ledger entries; test a saturated `payment-service` pool doesn't block calls to `catalog-service` | `feat: multi-vendor checkout + gateway bulkhead pools` | Q1 | Design Twitter | AtlasMarket: orders split across 2+ vendors | 4h |
| Tue (D164) | Per-vendor fulfillment status; deploying to real cloud infrastructure | AWS/GCP managed-Postgres docs | — | Adapt WareFlow's status concepts to `order_vendor_groups`; deploy the gateway + `catalog-service` to real cloud compute, DB on managed Postgres in the private subnet from Wednesday; `docs/cloud-deployment-notes.md` | Integration test status updates independently per vendor; smoke test the deployed gateway from the public internet, confirm the DB is unreachable directly | `feat: per-vendor fulfillment status + atlasmarket on real cloud infra` | — | LFU Cache | AtlasMarket: per-vendor payout reconciliation | 4h |
| Wed (D165) | Checkout UI, end-to-end wiring; feature flags + canary release | — | Hand-rolled feature-flag service (config table + `is_enabled(flag, user_id)`, percentage rollout) | Storefront checkout form wired to the real API, shipped dark behind the feature flag then ramped 10% → 100% while watching Grafana | Manual end-to-end run: browse → cart → checkout, verified live; test the same `user_id` always lands on the same side of a given rollout percentage | `feat: storefront checkout flow behind feature flag` | Q2 | Word Search II | Capstone review: rewrite Week 12's partition-aware query from memory | 3.5h |
| Thu (D166) | Mock system design interview #1; SD10 (Video Streaming Platform) | System Design Interview (Xu), relevant chapter | — | Design multi-vendor checkout from scratch on a whiteboard (no code), then compare to what you built; work SD10 from `system-design-problems.md` | — | `docs: mock interview 1 notes + sd10 notes` | Q1 mock, timed | Merge k Sorted Lists | Capstone review: rewrite Week 6's window-function ranking query from memory | 3.5h |
| Fri (D167) | Mock system design interview #2 + #3; SD16 (Proximity/Nearby-Search Service); end-to-end browser testing with Playwright | Playwright docs "Getting started" + "Writing tests" | — | Design payment idempotency + product search from scratch, unprompted; work SD16; Playwright test driving a real browser through browse → cart → checkout | Playwright suite green against the real deployed instance | `docs: mock interviews 2-3 notes + sd16 notes; test: playwright e2e test for atlasmarket checkout` | Q2, Q3 mock, timed | Alien Dictionary | Capstone: the one query you'd hand an interviewer | 4h |
| Sat (D168) | **Review**; SD20 — design AtlasMarket from scratch; full behavioral pass | — | Design AtlasMarket itself, 45 min, blank page, no notes, then compare against `docs/architecture.md` — the closing synthesis of the whole 19-problem bank | `docs/atlasmarket-roadmap-post-bootcamp.md` (deferred features) | Full suite, all services | `docs: post-bootcamp roadmap + sd20 comparison` | Full mock behavioral (full pass through `behavioral-interview-questions.md`) + system design round, timed, no notes | Review: redo Thursday's problem from memory — Merge k Sorted Lists | Review: rewrite Tuesday's query from memory, then extend it — AtlasMarket: per-vendor payout reconciliation | 2.5h |

---

## 13. Daily Plan — Week 29: URL Shortener + Rate Limiter, Built For Real

*No DSA/SQL problem across Weeks 29-30 — same reasoning as Phase 5's
Raft weeks: the day's own systems work already carries that load.*

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D169) | URL Shortener: base62 code generation, redirect semantics | Revisit `system-design-problems.md` SD1 | — | New repo `url-shortener/`, `POST /shorten` (counter-based base62 code) + `GET /{code}` (301 redirect); deleted codes return 404 | Collision test: distinct URLs never share a code; test a deleted code 404s, never redirects | `feat: url shortener core — shorten + redirect` | Q1 | 3.5h |
| Tue (D170) | Cache-aside for hot redirects | Redis docs caching (Phase 2 refresher) | — | Redis cache-aside in front of the redirect path, TTL + immediate invalidation on delete; load test cache-cold vs cache-warm | Cache-invalidation test (delete → immediate 404, not stale-redirect-until-TTL); load test p95 recorded both ways | `feat: redis cache-aside on redirect path + load test` | Q2 | 3.5h |
| Wed (D171) | Rate Limiter Service: token bucket vs sliding-window-counter | Revisit SD2 | — | New repo `rate-limiter/`, `POST /check {key, limit, window}` implementing both algorithms behind one interface | Correctness test per algorithm against a fixed request schedule with known expected outcomes | `feat: rate limiter service — token bucket + sliding window` | Q3 | 3.5h |
| Thu (D172) | Proving it's actually distributed | — | — | Run 3 rate-limiter instances behind Nginx, one shared Redis; benchmark memory footprint of both algorithms at 100k tracked keys | The centerpiece test: a client hammering all 3 instances is still correctly rate-limited overall, not 3x the real limit | `feat: multi-instance rate limiter, proven correct + benchmarked` | — | 3.5h |
| Fri (D173) | Retrofitting: URL Shortener calls the real Rate Limiter | — | — | `POST /shorten` calls the Rate Limiter service instead of an ad hoc check; READMEs + model cards for both services; tag `v0.1-sd-builds-1` | Integration test: shortener's rate limit is enforced by the real service, verified end-to-end | `feat: url shortener uses real rate-limiter service, tag v0.1-sd-builds-1` | Q4 | 3.5h |
| Sat (D174) | **Review** | — | Redo the token-bucket implementation from memory, explain the accuracy/memory trade-off out loud | — | Full suite, both services | — | Answer Week-29 Qs unscripted | 2.5h |

---

## 14. Daily Plan — Week 30: Distributed Job Scheduler, Built For Real; Full Program Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D175) | Distributed Job Scheduler: wiring Phase 5's Raft cluster as real infrastructure | Revisit SD14 + Phase 5 Week 24 Friday's toy dispatcher | — | New repo `job-scheduler/`, `Job` model + persistence, `POST /jobs {cron_expr, payload}`; the scheduler's processes form a real Raft cluster (reusing Phase 5's implementation, not rebuilding it) | Test the cluster elects a leader on startup the same way Phase 5's did | `feat: job scheduler scaffold + raft cluster wiring` | Q1 | 3.5h |
| Tue (D176) | Leader-only dispatch, idempotent job handlers | — | — | Only the current Raft leader dispatches due jobs; job handlers are idempotent (same discipline as every queue consumer since Phase 3) | Test: a job dispatched twice (simulated duplicate) executes its side effect exactly once | `feat: leader-only dispatch + idempotent handlers` | Q2 | 3.5h |
| Wed (D177) | Fault testing: kill the leader mid-dispatch-decision | — | `freezegun`-compressed 24-hour simulated run (the same technique from every Celery Beat test since Phase 2) | Kill-leader-mid-dispatch test; 24h-simulated run asserting every scheduled tick fired exactly once | Test: exactly one execution results from a leader kill mid-decision, never zero, never two | `feat: leader-kill fault test + 24h simulated run, all green` | Q3 | 4h |
| Thu (D178) | Polish, comparison writeup | — | — | README + model card for the scheduler; `docs/sd-builds-vs-paper-designs.md` comparing all three real builds (Projects 26-28) against their original SD1/SD2/SD14 paper designs — what the real build forced you to handle that the paper design didn't; tag `v0.1-sd-builds-2` | Full suite across all three services | `docs: sd-builds retrospective vs paper designs, tag v0.1-sd-builds-2` | Q4 | 3.5h |
| Fri (D179) | Buffer / catch-up; final capstone integration check | — | — | Confirm all of Phase 6 (PayFlow, AtlasMarket, and Projects 26-28) still runs green together — this is the first day all of it has been exercised as one whole | Full suite, every service in Phase 6, one clean run | — | — | 3.5h |
| Sat (D180) | **FULL 6-MONTH PROGRAM WRAP** | — | — | `docs/postmortem-phase6.md`, full 6-month retrospective across all 13 Track A projects (the original 10 plus Projects 26-28), tag `v1.0-bootcamp-complete` | Full suite, all services, everything green one last time | `docs: 6-month retrospective, tag v1.0-bootcamp-complete` | Full mock behavioral + system design round, timed, no notes | 2.5h |

---

## 15. Deliverables & GitHub Milestones

**Milestone: `Phase 6 — PayFlow v0.1 + AtlasMarket v0.1 (capstone) + 3 System-Design Builds`**
- [ ] Idempotent payment creation, proven under concurrent duplicate requests
- [ ] Webhook signature verification + idempotent webhook processing
- [ ] `docs/threat-model.md` written and addressed
- [ ] `docs/pci-scope-note.md` and `docs/hipaa-considerations-note.md` written
- [ ] Load test bottleneck found and fixed, before/after numbers recorded
- [ ] SLO + error budget + on-call runbook written for PayFlow; one real
      incident drill run and a blameless postmortem written
- [ ] `docs/backup-dr-plan.md` for LedgerBase, with a verified restore
- [ ] AtlasMarket: vendor-scoped catalog + search, multi-vendor checkout,
      per-vendor ledger + fulfillment status, all reusing prior projects'
      logic (documented in `docs/architecture.md`'s service map)
- [ ] AtlasMarket's gateway + `catalog-service` deployed to a real cloud
      account with least-privilege IAM, a VPC, and a managed database —
      `docs/cloud-deployment-notes.md` written
- [ ] Bulkhead pools added to the gateway's calls to all 5 downstream services
- [ ] React/TS storefront: routed product list, cart, checkout, working
      end-to-end against the real API — your fourth shipped frontend,
      shipped behind a feature flag with a real percentage-based canary
      rollout, covered by a Playwright end-to-end test
- [ ] `docs/atlasmarket-roadmap-post-bootcamp.md` — explicit deferred scope
- [ ] All 19 `system-design-problems.md` problems worked across Weeks
      19-28, plus the SD20 closing synthesis; 3 timed mock system-design
      interviews completed and logged
- [ ] A full pass through `behavioral-interview-questions.md`, answered in
      writing with STAR method
- [ ] Project 26 (URL Shortener): base62 counter-based codes, Redis
      cache-aside on the redirect path, measured cache-cold vs cache-warm
- [ ] Project 27 (Rate Limiter Service): token bucket + sliding-window-
      counter, proven correct across 3 real instances sharing one Redis
- [ ] Project 28 (Distributed Job Scheduler): Phase 5's Raft cluster
      wired as real leader-election infrastructure, leader-kill fault
      test passing, a 24h-simulated run with every tick firing exactly once
- [ ] `docs/sd-builds-vs-paper-designs.md` comparing Projects 26-28 against
      their original SD1/SD2/SD14 paper designs
- [ ] Tag: `v1.0-bootcamp-complete`

## 16. Skills Acquired Checklist
- [ ] Idempotency keys — implemented and race-tested
- [ ] Webhook signature verification + idempotent webhook processing
- [ ] HashiCorp Vault: dynamic secrets, KV engine, fail-closed startup — not just a tidier `.env`
- [ ] Threat modeling as a concrete written exercise
- [ ] PCI-DSS and HIPAA compliance scoping — narrow, honest, interview-ready, not a full audit
- [ ] Real load testing with `locust`, bottleneck found and fixed
- [ ] SLOs/SLIs/error budgets, an on-call runbook, and a live incident
      drill with a blameless postmortem
- [ ] Backup/DR: a real, verified restore, not just a stated policy
- [ ] Real cloud deployment: IAM least privilege, VPC subnetting, security
      groups, a managed database — hands-on, not simulated
- [ ] The bulkhead pattern, applied on top of Phase 4's retry+circuit-breaker
- [ ] Feature flags + percentage-based canary rollout
- [ ] End-to-end browser testing with Playwright, on top of component tests
- [ ] Integrating multiple prior services into one coherent system, with
      honest scope discipline (documented deferrals, not silent scope creep)
- [ ] React + TypeScript + Vite + TanStack Query + React Router + React
      Testing Library — four shipped apps in, enough to build a real UI
      and ship a small frontend feature yourself, not just talk to a
      frontend engineer as a peer
- [ ] 19 system-design problems worked end to end across the second half
      of the bootcamp, plus a from-scratch redesign of AtlasMarket compared
      against reality
- [ ] Three of those problems (SD1, SD2, SD14) taken all the way from
      paper design to a real, tested, running service — the difference
      between designing a system and shipping one, felt firsthand
- [ ] A rehearsed, evidence-grounded behavioral-interview bank, alongside
      system design interview technique — both timed, unscripted, grounded
      in your own 6 months of concrete decisions

---

## 17. What Comes After Day 180

AtlasMarket is designed to be unfinished on purpose. The honest next steps
— reviews/ratings, recommendations, vendor analytics, promotions, returns
— are sitting in `docs/atlasmarket-roadmap-post-bootcamp.md`, ready to
become your ongoing portfolio project. Every one of those features now has
6 months of infrastructure underneath it to land on, instead of being
built on the upfront-overscoped foundation the original AtlasCommerce plan
would have produced.

---

**Next:** `phase-7-llm-zoomcamp.md` opens Track B — the AI/ML/Data
Zoomcamp track — starting with RAG architecture, embeddings and vector
search, and agentic tool-calling, applied to CarePoint, PeopleOps,
DocuVault, and AtlasMarket. Seven months of backend systems work is in the
bank: resilience patterns and gRPC (Phase 4), a from-scratch Raft
implementation on top of consistent hashing and consensus (Phase 5), and
real cloud deployment, SLOs/on-call/DR, compliance scoping, a full
system-design + behavioral interview bank, and three of those system-design
problems shipped as real services (Phase 6) — the whole "senior backend
engineer" half of the program, finished before the pivot into AI/ML.
