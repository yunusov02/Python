# PHASE 4 — Microservices & Infrastructure
### Weeks 14–18 (5 weeks) · 30 working days

---

## 1. Learning Goals
- Split a system into real services behind Nginx/an API Gateway and explain
  the actual tradeoff (network hop, independent deploys, failure isolation)
  instead of reciting "microservices are better."
- Ship a real CI/CD pipeline that builds, pushes, and deploys — not just
  tests — including a zero-downtime deploy technique.
- Gate that same pipeline on supply-chain security — dependency CVEs,
  committed secrets, vulnerable base images — and prove the gate actually
  blocks a bad merge, not just that the tools are installed.
- Stand up Prometheus + Grafana + Sentry and *use* them to find a real
  problem you inject on purpose, not just install them.
- Handle file uploads properly via presigned URLs against S3/MinIO instead
  of routing file bytes through your API process.
- Scaffold a real React + TypeScript frontend consuming your own API — the
  first of four times this year, so it's a habit you build on rather than
  a one-week crash course crammed in at the very end.

## 2. Technologies Introduced
Nginx (reverse proxy, basic API Gateway routing), Docker Compose multi-
service orchestration at real scale, GitHub Actions full CI/CD (build,
push image, deploy), zero-downtime deploy technique (health-check gated
rollover), `pip-audit`/`gitleaks`/Trivy as CI security gates (dependency,
secret, and container-image scanning), Prometheus, Grafana, Sentry,
structured health checks, S3/MinIO + presigned URLs, React + TypeScript +
Vite + TanStack Query (first real frontend page, reused and extended in
Phases 5 and 6).

Deliberately not yet: Kubernetes (Phase 5), CQRS/Outbox/Saga (Phase 5),
Elasticsearch (Phase 5).

---

## 3. PROJECT 5 — CarePoint (Clinic Appointment & Records System)

**Business Problem:** A small clinic needs patients to book appointments
online, staff to manage a daily schedule per doctor, and doctors to attach
documents (lab results, scans) to a patient's record securely — currently
juggled across a paper diary and emailed PDFs.

**Requirements**
- Functional: appointment booking with doctor/time-slot conflict
  prevention, patient records, document attachment, appointment
  reminders (Celery, from Phase 2/3 experience).
- Non-functional: patient documents must never be publicly readable by
  URL guessing; document upload/download shouldn't load your API process
  with file bytes.

**Architecture — first real service split:**
```
Nginx (reverse proxy / gateway)
  → auth-service (FastAPI) — issues/validates JWTs, used by both below
  → carepoint-service (Django/DRF) — appointments, records, documents
```
This is a deliberate, minimal split — two services, not ten — so you feel
the *actual* cost (an extra network hop for auth checks, two Compose
services to keep in sync) before ever being tempted to over-split later.

**ER Diagram (textual)**
```
doctors(id, name, specialty)
patients(id, name, dob, contact)
appointments(id, doctor_id, patient_id, slot_start, slot_end, status)
                 -- EXCLUDE constraint prevents overlapping slots per doctor
documents(id, patient_id, s3_key, uploaded_by, uploaded_at)
```

**Folder Structure**
```
carepoint/
  auth-service/          # FastAPI, separate deployable
  clinic-service/         # Django/DRF
  nginx/
    nginx.conf
  docker-compose.yml
```

**API Design**
```
POST /auth/login                              # auth-service
GET  /appointments?doctor_id=&date=            # clinic-service
POST /appointments
POST /documents/presigned-upload                # returns a presigned PUT URL
GET  /documents/{id}/presigned-download
```

**Database Design:** Postgres `EXCLUDE` constraint using `btree_gist` to
prevent overlapping appointment slots per doctor at the DB level — not
just application-level validation (you'll deliberately try to break it via
two concurrent bookings and watch the DB reject the second one).

**Authentication & Permissions:** `auth-service` issues the JWT,
`clinic-service` validates it via a shared secret/public key — your first
taste of auth as a *separate service* other services trust rather than
re-implement.

**Caching:** doctor schedule lookups cached with Redis, invalidated on any
booking/cancellation for that doctor+date.

**Background Jobs:** Celery task sends an appointment reminder 24h before
the slot (scheduled via Beat, same pattern as PeopleOps).

**Infrastructure:** Nginx added to Docker Compose as the single entrypoint,
routing `/auth/*` to `auth-service` and everything else to
`clinic-service` — your first hand-written `nginx.conf`.

**CI/CD:** GitHub Actions now **builds and pushes** Docker images to GHCR
on merge to `main` (deploy step lands next week alongside LedgerBase, once
both services need it).

**Testing Strategy:** integration test that fires two concurrent booking
requests for the same doctor/slot and asserts exactly one succeeds (DB
constraint doing the work, not app-level locking).

**Monitoring:** basic `/health` endpoint on each service (checks DB +
Redis connectivity) — full Prometheus/Grafana wiring lands Week 17–18
once you have two services worth monitoring comparatively.

**Deployment:** still Compose-based; full CI/CD deploy automation lands
next week's project.

**Scaling Strategy:** notes on what happens when `auth-service` needs to
scale independently of `clinic-service` — this is the concrete argument
for the split you just made.

**Common Interview Questions**
1. Why split auth into its own service here, and what did it cost you?
2. How does a DB-level `EXCLUDE` constraint prevent double-booking better
   than an application-level check?
3. Why presigned URLs instead of routing file uploads through your API?
4. What does Nginx actually do in this setup vs what the API Gateway
   pattern would add on top?
5. How do two services agree on JWT validity without calling each other
   on every request?

**Possible Improvements:** service-to-service mTLS, doctor availability
rules (recurring schedules), waitlist for cancelled slots.

**What Companies Usually Do Differently:** most real systems don't split
auth out this early — you're doing it now specifically to *feel* the
tradeoff while the system is still small enough to reason about, not
because two services is the "right" number for a system this size.

**Common Mistakes:** validating slot overlap only in application code and
trusting it (race condition under concurrent bookings); making presigned
URLs valid too long (security window); forgetting `auth-service` and
`clinic-service` need to agree on clock skew tolerance for JWT expiry.

---

## 4. PROJECT 6 — LedgerBase (Double-Entry Accounting/Invoicing Platform)

**Business Problem:** A freelancer/small agency needs to issue invoices,
record payments against them, and see a real ledger (every transaction
recorded as a balanced debit/credit pair) instead of a spreadsheet that
silently drifts from reality — with an accountant able to trust every
number traces to a specific journal entry.

**Requirements**
- Functional: chart of accounts, journal entries (always balanced — debits
  = credits, enforced at write time), invoices, payments applied against
  invoices, trial balance report.
- Non-functional: **money is stored as integer cents, never float** —
  and this project is where you feel exactly why, via a deliberately
  broken float version first.

**Architecture:** Third service added behind the same Nginx gateway,
sharing `auth-service`. This is where Compose starts to genuinely strain
(3 services + Postgres + Redis + RabbitMQ) — you'll write down the exact
moment it stops feeling manageable, seeding Phase 5's Kubernetes intro.

**ER Diagram (textual)**
```
accounts(id, name, type[asset|liability|equity|revenue|expense])
journal_entries(id, description, created_at)
journal_lines(id, journal_entry_id, account_id, debit_cents, credit_cents)
                  -- CHECK: exactly one of debit/credit is nonzero per line
invoices(id, client_name, total_cents, status, issued_at, due_at)
payments(id, invoice_id, amount_cents, journal_entry_id, received_at)
```

**Folder Structure**
```
ledgerbase/
  ledger-service/          # FastAPI, core accounting logic
  invoicing-service/         # Django/DRF, invoices + payments, calls ledger-service internally
```

**API Design**
```
POST /journal-entries          # must balance or 422
GET  /accounts/{id}/balance
POST /invoices
POST /invoices/{id}/payments
GET  /reports/trial-balance
```

**Database Design:** `CHECK` constraint enforcing balanced entries at the
DB level too (defense in depth — application validates, DB refuses to
store an unbalanced entry regardless).

**Authentication & Permissions:** reuses `auth-service` from CarePoint —
your first real proof that the auth split paid off (zero duplicated auth
code for a brand-new service).

**Caching:** account balance is *not* cached (financial data — staleness
risk outweighs the read-speed benefit) — another deliberate "why we
didn't cache this" interview-ready note.

**Background Jobs:** overdue-invoice reminder job (Celery Beat, same
pattern as CarePoint/PeopleOps — by now you should be able to build this
one fast, which is the point).

**Infrastructure:** third service on the same Nginx gateway.

**CI/CD:** **full deploy pipeline lands this week** — GitHub Actions
builds, pushes to GHCR, SSHes into the VPS, and does a **zero-downtime
deploy**: bring up the new container, wait for its `/health` to pass, then
switch Nginx upstream, then stop the old container. You implement and test
this rollover technique for real, including a deliberate "new version's
health check never passes" test to confirm the rollback path works.

**Testing Strategy:** the float-vs-cents deliberate bug: write the ledger
math with floats first, generate a report that doesn't reconcile due to
float drift, then fix it with integer cents and add a regression test that
would have caught the original bug.

**Monitoring:** this is where the monitoring stack goes in for real —
Prometheus scrapes all 3 services + Postgres + RabbitMQ, Grafana
dashboards built for request latency and queue depth, Sentry wired for
exception tracking across all services. You inject a deliberate bug
(unbalanced entry slipping through App validation) and find it via Sentry
before checking the code.

**Deployment:** zero-downtime deploy, live.

**Scaling Strategy:** written notes on read-replica strategy for
`trial-balance` reporting once write volume grows — a concrete Phase 5
callback (replication).

**Common Interview Questions**
1. Why store money as integer cents, and show a concrete float bug you hit.
2. How do you enforce double-entry balance at both app and DB level, and
   why both?
3. Walk through your zero-downtime deploy step by step.
4. What does Sentry catch that your logs alone wouldn't have surfaced as
   fast?
5. Why didn't you cache account balances?

**Possible Improvements:** multi-currency ledger, accountant-facing
export (CSV/PDF), automated bank reconciliation import.

**What Companies Usually Do Differently:** real ledgers often use an
append-only event log as the source of truth with balances as projections
— an explicit, named preview of Phase 5's Event Sourcing overview.

**Common Mistakes:** floats for money (you'll have done this once, on
purpose, to feel it); allowing an unbalanced journal entry through a
missing DB constraint; caching anything financial "because it's slow" —
without checking whether staleness is actually acceptable here (it isn't).

---

## 5. Mini-Projects

| Mini-project | Week | Teaches |
|---|---|---|
| Hand-written `nginx.conf` reverse proxy for 2 dummy services | 14 | Reverse proxy routing, upstream blocks |
| Mini API Gateway (single FastAPI app routing to 2 backend URLs) | 15 | What a gateway adds over a plain reverse proxy |
| Presigned URL demo against MinIO (upload/download without API in the middle) | 15 | Object storage, presigned URL security model |
| Zero-downtime deploy script (health-check-gated container swap) | 17 | The actual mechanics behind "zero downtime" |
| Custom health-check aggregator (checks DB+Redis+RabbitMQ, one `/health`) | 18 | Composability of health checks |

---

## 6. Books & Documentation
- Nginx docs: reverse proxy + load balancing guide (Weeks 14–15).
- *Building Microservices* (Newman) Ch. 6 (Deployment) during Week 17.
- Prometheus docs: "Getting Started" + Grafana "Getting Started" (Week 17–18).
- Sentry docs: Python SDK integration guide.
- AWS S3 docs: presigned URL section; MinIO docs for local S3-compatible dev.
- React docs (react.dev) "Quick Start"; TanStack Query docs "Quick Start" — Week 15.

---

## 7. Weekly Interview Question Sets

**Week 14 — Service split, Nginx**
1. What's the actual cost of splitting `auth-service` out — be specific.
2. Reverse proxy vs load balancer vs API Gateway — where's the line?

**Week 15 — Object storage, presigned URLs**
1. Why not stream file bytes through your API for uploads?
2. What does a presigned URL actually authorize, and for how long should
   it be valid?

**Week 16 — Double-entry accounting, money-as-integers**
1. Show, concretely, a float rounding bug in financial math.
2. Why enforce balance at both the app and DB layer?

**Week 17 — CI/CD, zero-downtime deploy**
1. Walk through your deploy pipeline step by step, failure modes included.
2. What's the rollback path if the new version's health check never
   passes?

**Week 18 — Monitoring**
1. What's the difference between a metric, a log, and a trace?
2. How did Sentry help you find a bug faster than logs would have?

---

## 8. Daily Plan — Week 14: Service Split, Nginx, CarePoint Scaffold

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D79) | Reverse proxy fundamentals | Nginx reverse proxy guide | Hand-written `nginx.conf` for 2 dummy services | New repo `carepoint/`, `auth-service` scaffold (FastAPI, reused JWT logic from Phase 1) | Test auth-service issues valid JWT | `chore: carepoint scaffold + auth-service` | Q1 | Number of Islands | CarePoint: doctors with overlapping appointments | 3.5h |
| Tue (D80) | Service-to-service trust (shared secret/public key JWT validation) | — | — | `clinic-service` scaffold (Django/DRF), JWT validation middleware | Test protected endpoint rejects invalid token | `feat: clinic-service jwt validation` | — | Max Area of Island | Patients With a Condition | 3.5h |
| Wed (D81) | `EXCLUDE` constraints in Postgres | Postgres docs `btree_gist` | — | `Appointment` model with `EXCLUDE` constraint on overlapping slots | Test overlapping booking rejected at DB level | `feat: appointment model with exclude constraint` | Q2 | Clone Graph | CarePoint: appointment count per doctor per day | 3.5h |
| Thu (D82) | Concurrent booking race | — | — | `POST /appointments` endpoint, deliberately fire 2 concurrent identical bookings | Integration test: exactly one succeeds | `feat: appointment booking endpoint` | — | Islands and Treasure (Walls and Gates) | CarePoint: patients with no documents on file | 3.5h |
| Fri (D83) | Wiring Nginx as the single entrypoint | — | — | `nginx.conf` routing `/auth/*` → auth-service, rest → clinic-service, added to Compose | Manual + automated smoke test through Nginx | `feat: nginx gateway routing` | Q3 | Rotting Oranges | The Most Recent Orders for Each Product | 3.5h |
| Sat (D84) | **Review** | — | Redo nginx.conf from memory | — | Full suite | — | Answer Week-14 Qs unscripted | Review: redo Thursday's problem from memory — Islands and Treasure (Walls and Gates) | Review: rewrite Tuesday's query from memory, then extend it — Patients With a Condition | 2.5h |

---

## 9. Daily Plan — Week 15: Patient Records, Presigned Uploads, Reminders

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D85) | Object storage basics, MinIO local setup | MinIO docs | — | Add `minio` to Compose | Verify bucket reachable | `chore: minio service` | Q1 | Pacific Atlantic Water Flow | CarePoint: appointments in next 24h needing a reminder | 3.5h |
| Tue (D86) | Presigned URLs | S3 presigned URL docs | Presigned upload/download demo | `POST /documents/presigned-upload` endpoint | Test URL expires correctly | `feat: presigned document upload` | — | Surrounded Regions | CarePoint: doctors with the most documents on their patients | 3.5h |
| Wed (D87) | Mini API Gateway concept | — | Mini FastAPI gateway routing to 2 backend URLs | `GET /documents/{id}/presigned-download` | Integration test full upload→download flow | `feat: presigned document download` | Q2 | Course Schedule | Reformat Department Table | 3.5h |
| Thu (D88) | Redis cache on doctor schedules; frontend intro — React + TypeScript + Vite + TanStack Query scaffold, first real UI of the year | React docs "Quick Start" + TanStack Query "Quick Start" | — | Cache `GET /appointments?doctor_id=&date=`, invalidate on booking/cancel; new `carepoint-web/` (Vite + React + TS), one page: doctor's daily schedule fetched via TanStack Query against the endpoint just cached | Cache invalidation test; component renders loading/error/loaded states correctly against a mocked API response | `feat: cache doctor schedule lookups + carepoint-web schedule view` | — | Course Schedule II | CarePoint: EXPLAIN ANALYZE the doctor-schedule query | 3.5h |
| Fri (D89) | Appointment reminder job | — | — | Celery Beat: 24h-before reminder task | `freezegun` schedule test | `feat: appointment reminder job` | Q3 | Redundant Connection | Queries Quality and Percentage | 3.5h |
| Sat (D90) | **Review** | — | Redo presigned URL demo from memory | Tag `v0.1-carepoint` | Full suite | — | Answer Week-15 Qs unscripted | Review: redo Thursday's problem from memory — Course Schedule II | Review: rewrite Tuesday's query from memory, then extend it — CarePoint: doctors with the most documents on their patients | 2.5h |

---

## 10. Daily Plan — Week 16: LedgerBase Scaffold, Money-as-Cents, Double-Entry

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D91) | Double-entry bookkeeping fundamentals | (any intro accounting primer) | — | New repo `ledgerbase/`, `Account`, `JournalEntry`, `JournalLine` models — **float version, on purpose** | Test that reveals float drift after many entries | `feat: ledger models (float version — deliberate bug)` | Q1 | Number of Connected Components in an Undirected Graph | LedgerBase: verify every journal_entry balances | 3.5h |
| Tue (D92) | Why floats break money math | — | — | Fix: convert all money fields to integer cents | Regression test proving the float bug is gone | `fix: money as integer cents` | — | Graph Valid Tree | LedgerBase: account balance = debits minus credits | 3.5h |
| Wed (D93) | Enforcing balance: app + DB layer | Postgres `CHECK` constraint docs | — | `CHECK` constraint on `journal_lines`, app-level balance validation in service | Test unbalanced entry rejected both ways | `feat: enforce balanced entries (app + db)` | Q2 | Word Ladder | Rising Temperature — window function version | 3.5h |
| Thu (D94) | Invoicing domain | — | — | `Invoice`, `Payment` models, `invoicing-service` calling `ledger-service` internally | Integration test invoice→payment→journal entry | `feat: invoicing service + ledger integration` | — | Reconstruct Itinerary | LedgerBase: unbalanced entries that slipped through | 3.5h |
| Fri (D95) | Trial balance report | — | — | `GET /reports/trial-balance` | Test report reconciles to zero | `feat: trial balance report` | Q3 | Min Cost to Connect All Points | Movie Rating | 3.5h |
| Sat (D96) | **Review** | — | Redo the float-bug repro from memory, explain the fix | Add `ledgerbase` to Nginx routing | Full suite | — | Answer Week-16 Qs unscripted | Review: redo Thursday's problem from memory — Reconstruct Itinerary | Review: rewrite Tuesday's query from memory, then extend it — LedgerBase: account balance = debits minus credits | 2.5h |

---

## 11. Daily Plan — Week 17: Full CI/CD, Zero-Downtime Deploy

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D97) | GitHub Actions: build + push to GHCR; supply-chain security gates — dependency, secret, and container scanning | GitHub Actions Docker docs + `pip-audit`/`gitleaks`/Trivy READMEs | Run `gitleaks detect` against this repo's own git history, confirm it doesn't false-positive on real config | CI builds and pushes images for all 4 services; add `pip-audit` (dependency CVEs), `gitleaks` (committed-secret scan), and Trivy (container image scan) as CI steps that fail the build on high-severity findings | Verify images appear in GHCR; verify the pipeline actually fails when a deliberately-vulnerable dependency/secret is introduced, then goes green once removed | `ci: build/push images to ghcr + dependency/secret/container scanning gates` | Q1 | Network Delay Time | LedgerBase: overdue unpaid invoices | 3.5h |
| Tue (D98) | SSH deploy step, secrets management | GitHub Actions secrets docs | — | Deploy step: SSH to VPS, pull new images | Manual verify deploy runs end-to-end | `ci: ssh deploy step` | — | Swim in Rising Water | LedgerBase: monthly revenue trend from paid invoices | 3.5h |
| Wed (D99) | Zero-downtime rollover mechanics | — | Zero-downtime deploy script (health-gated swap) | Apply the script: bring up new container, health-check gate, swap Nginx upstream, stop old | Test deploy causes zero dropped requests (hit endpoint continuously during deploy) | `feat: zero-downtime deploy script` | Q2 | Climbing Stairs | Replace Employee ID With The Unique Identifier | 3.5h |
| Thu (D100) | Rollback path | — | — | Deliberately break new version's health check, confirm deploy aborts and old version stays live | Test the abort path explicitly | `feat: deploy rollback on failed health check` | — | Min Cost Climbing Stairs | LedgerBase: trial balance report | 3.5h |
| Fri (D101) | Full pipeline hardening | — | — | End-to-end: push to `main` → build → push → deploy, verified live | — | `ci: full pipeline verified end-to-end` | Q3 | House Robber | Top Travellers | 3.5h |
| Sat (D102) | **Review** | — | Redo zero-downtime script from memory, explain every step | — | — | — | Answer Week-17 Qs unscripted | Review: redo Thursday's problem from memory — Min Cost Climbing Stairs | Review: rewrite Tuesday's query from memory, then extend it — LedgerBase: monthly revenue trend from paid invoices | 2.5h |

---

## 12. Daily Plan — Week 18: Monitoring Stack, Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | DSA Problem | SQL Problem | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mon (D103) | Prometheus: scraping, metrics types | Prometheus "Getting Started" | Custom health-check aggregator (DB+Redis+RabbitMQ in one `/health`) | Add `/metrics` endpoint to all 4 services, Prometheus scrape config | Verify metrics visible in Prometheus UI | `feat: prometheus metrics on all services` | Q1 | House Robber II | LedgerBase: accounts with no activity this month | 3.5h |
| Tue (D104) | Grafana dashboards | Grafana "Getting Started" | — | Build a latency + queue-depth dashboard | — | `feat: grafana dashboards` | — | Longest Palindromic Substring | LedgerBase: largest single journal entry this quarter | 3.5h |
| Wed (D105) | Sentry integration | Sentry Python SDK docs | — | Wire Sentry into all 4 services | Trigger a deliberate exception, confirm it appears in Sentry | `feat: sentry error tracking` | Q2 | Palindromic Substrings | Sales Analysis I | 3.5h |
| Thu (D106) | Finding a bug via Sentry, not code-reading | — | — | Inject an unbalanced-entry bug past app validation (bypass service layer directly), find it via Sentry alert first | Write regression test for the found bug | `fix: bug found via sentry — regression test added` | — | Decode Ways | LedgerBase: underpaid invoices | 3.5h |
| Fri (D107) | Phase wrap: docs, CI final check | — | — | `docs/postmortem-phase4.md`, full CI green across everything | Full suite, all 4 services | `docs: phase 4 postmortem` | Q3 | Coin Change | Sales Analysis III | 3.5h |
| Sat (D108) | **Phase 4 wrap review** | — | Explain your full deploy pipeline out loud, start to finish | Tag `v0.4-phase4` | — | — | Mock-answer all Phase-4 questions timed | Review: redo Thursday's problem from memory — Decode Ways | Review: rewrite Tuesday's query from memory, then extend it — LedgerBase: largest single journal entry this quarter | 2.5h |

---

## 13. Deliverables & GitHub Milestones

**Milestone: `Phase 4 — CarePoint v0.1 + LedgerBase v0.1`**
- [ ] 4 services behind one Nginx gateway (`auth`, `clinic`, `ledger`, `invoicing`)
- [ ] `EXCLUDE` constraint preventing double-booked appointments, proven
      under concurrency
- [ ] Presigned upload/download flow working against MinIO
- [ ] Money-as-cents fix with a regression test proving the original float bug
- [ ] Balanced-entry enforcement at app + DB layer
- [ ] Full CI/CD: build, push, zero-downtime deploy, verified rollback path
- [ ] Prometheus + Grafana + Sentry wired across all services, one bug
      found via Sentry and documented
- [ ] Tag: `v0.4-phase4`

## 14. Skills Acquired Checklist
- [ ] Real service split with a stated, honest cost/benefit
- [ ] Nginx reverse proxy / gateway routing, hand-written config
- [ ] Presigned URL pattern for file storage
- [ ] Money-as-integer-cents, felt through a real bug
- [ ] Double-entry balance enforcement, app + DB layer
- [ ] Full CI/CD pipeline: build, push, deploy
- [ ] Supply-chain security gates in CI (dependency/secret/container scanning), proven to actually block a bad merge
- [ ] Zero-downtime deploy technique, including tested rollback
- [ ] Prometheus + Grafana + Sentry, used to find a real injected bug
- [ ] React + TypeScript + Vite + TanStack Query: first real page consuming your own API

---

**Next:** Phase 5 pushes into CQRS, the Outbox pattern (closing the gap
identified in Phase 3), Elasticsearch, Kubernetes fundamentals, and
replication/sharding — building FleetTrack and DocuVault.
