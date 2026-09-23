# Stage 06 — Ship & operate → portfolio slice 1

| | |
|---|---|
| **Weeks** | W24–W28 (5 weeks) |
| **Hours** | 60 must + 5 stretch |
| **Architecture at start → at end** | market (modular monolith with the S5 `payments` module) + provider-sim, running only in Compose on your laptop → the same deployables on a **Terraform-provisioned VPS** behind **Nginx with TLS**, in a staging and a prod stack, with `/providers/*` on its **own gunicorn pool**, a **streaming replica**, a **WAL archive** in object storage, and **Prometheus / Grafana / Alertmanager / Loki / Tempo** plus Sentry |
| **New technologies** | Terraform (BSL; OpenTofu is a drop-in); Let's Encrypt; Docker secrets + SOPS/age; GHCR; Trivy, pip-audit and gitleaks as failing gates; squawk; OpenTelemetry → Tempo; Prometheus, Alertmanager, Grafana, Loki with Grafana Alloy; oha as the constant-rate latency probe; Sentry (SaaS developer tier); `pg_stat_statements`, `auto_explain`, `pgstattuple`; pgBackRest or wal-g; pgbench; py-spy; Playwright |
| **Portfolio tag** | `v0.6` — **slice 1** (W28): the marketplace deployed, observed and taking payments |
| **Old-spec theory to read** | [P6 LedgerBase](../python/06-ledgerbase.md) D97–D108 (security gates, staging → prod, health-gated rollover, graceful shutdown, expand/contract, then Prometheus, Alertmanager, Loki, OTel, Sentry); [P8 DocuVault](../python/08-docuvault.md) D127–D132 (stale statistics, bloat, `pg_stat_statements`, replica and read-your-own-write); [P9 PayFlow](../python/09-payflow.md) D151–D156 (pg_dump and PITR, Terraform, then locust, SLO, runbook and the live drill); [P10 AtlasMarket](../python/10-atlasmarket.md) D163–D165 (bulkhead sized from load, OTel end to end, Terraform cloud deploy, TLS) |

Version pins in this file are as of 2026-09. Re-check them with `scripts/compat_check.sh` at the start of the stage.

> **What this stage is really for.** Everything so far only runs on your laptop, and nobody knows what is slow. This stage puts S1–S5 on a public HTTPS URL and makes you *operate* it: deploy and change the schema under load without errors, see every request as metrics, logs and a trace, run Postgres rather than just query it, prove a backup by restoring it, and measure an SLO. It also builds the **split gate**: the reproducible measurement that every later service extraction must pass, so that "we split it" is always backed by numbers.

---

## 1. The problem this stage starts from

**Business view.** Atlas takes money since [Stage 05](stage-05-atlaspay-monolith.md), but only on a laptop. A buyer cannot reach it, there is no HTTPS, and a recruiter cannot see it. Nobody could tell you what the checkout success rate is, how fast Payme callbacks are answered, or how much data you would lose if the disk died tonight. The ledger holds (simulated) money with no restorable backup.

**Engineering view.**

1. **No deploy path.** There is no pipeline from `main` to a server, no staging, no health gate, no rollback anyone has ever tried.
2. **Schema changes lock tables.** A normal `ALTER TABLE` on `ordering_order` can queue every checkout behind it. You have never changed a column while traffic was flowing.
3. **No visibility.** There are structured logs, but no metrics, no traces and no alerts. "It is slow" cannot be turned into "this query, on this table".
4. **Postgres is queried, not operated.** Statistics, autovacuum, bloat, HOT updates, replication slots, lock queues and durability settings have never been looked at.
5. **No numbers behind any architecture claim.** The obvious next idea, "extract payments into its own service", is a hunch. Without a measured problem, [Stage 09](stage-09-strangler-atlaspay-auth.md) would be cargo-culting microservices.

---

## 2. Outcomes — what exists when the stage is finished

1. **Infrastructure as code:** a VM, a firewall, DNS records and object-storage buckets, all created by Terraform with remote, locked state; `terraform plan` on every infra PR, `apply` only from `main`.
2. **An HTTPS edge:** Nginx with Let's Encrypt certificates, HTTP→HTTPS redirect, HSTS and security headers, `limit_req` zones per IP and per API key id (parsed from `Authorization: Bearer …`, never the full key), a CORS allow-list, and secrets delivered as Docker secrets decrypted from SOPS/age files.
3. **A CD pipeline:** images in GHCR tagged by git SHA; failing security gates; staging deploys automatically; prod deploys the **same SHA** after approval; a health-gated container swap with an Nginx upstream switch; a post-swap contract-migration step; graceful shutdown in every process; an exercised rollback; post-deploy smoke tests.
4. **Zero-downtime migrations:** an expand/contract column rename done across 3 deploys plus a post-deploy contract step, under load with 0 errors, a squawk gate, `lock_timeout` in every migration, and a test that the previous release's code runs against the new schema.
5. **Full telemetry:** structlog with `request_id` and `trace_id`; OpenTelemetry traces from Nginx to the consumers, carried through the outbox, stored in Tempo; Prometheus RED and business metrics; Grafana dashboards; Alertmanager with `outbox_lag_seconds` fired and resolved; Loki; Sentry.
6. **Postgres operations evidence:** the top-10 query list, stale-statistics and extended-statistics proofs, bloat and autovacuum tuning, HOT-update ratios, a reproduced **lock-queue incident**, a reproduced **replication-slot disk fill**, and a measured `synchronous_commit=off` experiment.
7. **A streaming replica** serving reporting and the vendor dashboard, with a read-your-writes fix.
8. **Point-in-time recovery:** a restore to 1 second before a bad UPDATE with an identical trial balance, the achieved RPO/RTO recorded, and a nightly restore-verify workflow.
9. **A performance report:** the real bottleneck found with py-spy and `pg_stat_statements`, fixed, with before/after numbers.
10. **SLOs with an error budget**, each with an alert; a runbook; a live drill with a blameless postmortem.
11. **The split-gate baseline** (`bench/split-gate`, ADR-023) and the measured effect of the cheapest bulkhead: `/providers/*` on its own gunicorn pool.
12. **A minimal server-rendered storefront** and a Playwright test running against staging.
13. **Documents:** ADR-021, ADR-022, ADR-023; runbooks; the drill postmortem; a backup/DR plan; `docs/perf/s06.md`; `docs/privacy/data-governance.md` v1; README v1 with a diagram and a 5-minute demo; evidence under `docs/evidence/s06/`; two STAR stories.

---

## 3. Architecture at the end of the stage

```
Internet
   |  DNS (Terraform): atlas.<domain>, staging.atlas.<domain>, sim.<domain>,
   |                   pay.<domain>, pay.staging.<domain> (reserved; AtlasPay's host from S9)
   v
+---------------------- VPS (Terraform: VM + firewall 22/80/443 + buckets) -----------------------+
|  Nginx: TLS (Let's Encrypt), HTTP->HTTPS, HSTS + headers, limit_req (per IP, per key id)        |
|    |-- /, /api/v1/*, /admin ---------> market-web  (blue | green, gunicorn)                     |
|    |-- /providers/* -----------------> market-providers (own gunicorn pool, no limit_req,       |
|    |                                     IP allowlist in the adapter)                           |
|    |-- sim.<domain> -----------------> provider-sim (plays Payme and Click)                     |
|                                                                                                 |
|  market-worker   market-beat   market-relay   market-consumers   (graceful on SIGTERM)          |
|                                                                                                 |
|  pg-market primary ==streaming==> pg-market replica  (reports, vendor dashboard)                |
|        \__ WAL archive + base backups (pgBackRest | wal-g) ---> bucket atlas-wal                |
|  pg-sim   redis-cache   redis-state   RabbitMQ                                                  |
|                                                                                                 |
|  otel-collector -> Tempo     Prometheus -> Alertmanager     Loki     Grafana (all data sources) |
+-------------------------------------------------------------------------------------------------+
    staging = a second Compose project with its own databases (same VM or a second small VM: ADR-021)

GitHub Actions: lint/test -> build -> Trivy/pip-audit/gitleaks -> GHCR (sha) -> migrate (expand only)
                -> deploy staging -> smoke + Playwright -> approval -> deploy prod (same digest) -> smoke
                -> contract migrations (per environment, only after its old containers have stopped)
Nightly: restore-verify, p95 budget (locust traffic, oha probe).     Sentry SaaS <- every process
```

**What changed and why.**

- **One VPS, provisioned by Terraform, still on Compose.** Compose still copes with this number of containers, and Kubernetes would add an operations job you have no measured need for yet. Write down the container count now: [Stage 10](stage-10-kubernetes-grpc-inventory.md) uses it as evidence (ADR-035) when Compose stops coping.
- **`/providers/*` gets its own gunicorn pool.** This is the cheapest possible bulkhead (a bulkhead isolates resources so one workload cannot starve another): a separate process group from the same image, with its own workers and its own DB connection budget, so a flood of catalog traffic cannot take the workers Payme callbacks need. The split gate measures whether this is enough.
- **A streaming replica.** It moves reporting and the vendor dashboard off the primary, and it teaches replication lag and read-your-writes. On the same VM it protects against nothing physical; the protection comes from the WAL archive in object storage. ADR-021 must say so.
- **Telemetry everywhere.** Metrics tell you *that* something is wrong, traces tell you *where*, logs tell you *what exactly*. Without all three, the incidents in this stage would be guesswork.
- **The provider simulator is deployed too.** It plays the role of Payme and Click on its own subdomain, so the public demo can take a (simulated) payment. Like a real provider, it sends no `traceparent`, so callback traces start at your Nginx.

---

## 4. Build plan

Suggested weekly split (12 h each, including a 1 h drill every week): **W24** Terraform + VPS, Nginx + TLS, the first half of CD. **W25** the rest of CD, zero-downtime migrations, the start of observability. **W26** observability, the first half of Postgres operations (SD19 in the drill hour). **W27** the rest of Postgres operations, replica, PITR, most of performance (SD17 in the drill hour). **W28** the rest of performance, SLO + drill, split gate, storefront + E2E; slice 1 and tag `v0.6`. The weekend blocks hold everything that needs uninterrupted state: `terraform apply`/`destroy`, the first deploy under load, the lock-queue and slot-fill incidents, the PITR restore, the live drill, the performance runs and the split-gate runs.

These block hours are the baseline. At [B1](buffers-and-job-sprint.md) you computed your actual/budget ratio from the hours log; if it was above 1 and you re-planned, use your re-planned numbers instead. Keep logging actual hours per block. The deploy, observability, PITR, drill and split gate are on the never-cut spine: if one of them overruns, the slice-1 date moves; nothing on the spine is silently deferred ([schedule-and-cuts](schedule-and-cuts.md)).

**Cost guard:** cloud spend is capped at $50 for Season 1. Pick a VM size you can justify in ADR-021, set a billing alert, and run `terraform destroy` on anything idle (staging can be destroyed and re-created; that is also your proof that Terraform is the source of truth).

### 4.1 Terraform + VPS [4.5 h, must]

**Why.** A server you configured by clicking exists only in your memory. Terraform turns infrastructure into reviewed code: `plan` shows exactly what will change before it changes, and `apply` makes it so. Remote, locked state means two runs can never fight over the same resources.

**What to build.**

1. `deploy/terraform/`: the VM, its firewall (22 from your IP only, 80, 443), DNS records (`atlas.`, `staging.atlas.`, `sim.`, plus `pay.` and `pay.staging.`), and the object-storage buckets you need in the cloud (at least `atlas-wal`; the provider's object storage replaces the local S3-compatible store, Garage, there). `pay.<domain>` is reserved for AtlasPay's own public host from S9 (its `/v1/*` merchant API and provider callbacks). Create it now so the certificates and the Terraform plan already cover it; until S9, Nginx answers 404 on it.
2. **Remote state with locking** (a backend your provider supports; check that it locks).
3. **CI:** `terraform plan` on every PR touching `deploy/terraform/**`, posted to the PR; `terraform apply` only from `main`, behind an environment.
4. **ADR-021 region:** the data is synthetic, so an EU region is acceptable. A real launch would probably have to store Uzbek citizens' personal data inside Uzbekistan **[U]**; write that down as an open legal question, not a fact.
5. **`docs/privacy/data-governance.md` v1:** a PII inventory (which tables and logs hold phone numbers, emails, KYC documents, payout references), a retention table, and the erasure approach you intend (to be finished in S9 with crypto-shredding).

**Pain-first.** Following P9 D151–D153: once everything is applied, run `terraform destroy` and `terraform apply` again (weekend block). Observe whether everything comes back, and whether `plan` is clean afterwards. Anything that did not come back existed outside Terraform. Record it in `docs/evidence/s06/terraform-recreate.md`.

**Acceptance criteria.** `plan` is clean after `apply`; the destroy/re-apply log is committed; no resource exists that Terraform does not know about.

*Degrade option #10 ([schedule-and-cuts](schedule-and-cuts.md)):* Terraform manages DNS and buckets only; the VM is set up by hand and documented step by step (saves 1.5 h).

### 4.2 Nginx and TLS [2.5 h, must]

**Why.** Nginx is the single front door: it terminates TLS, redirects plain HTTP, adds the security headers browsers need, and applies the outermost rate limit before any Python code runs.

**What to build.**

1. Let's Encrypt certificates with automatic renewal; HTTP→HTTPS redirect; **HSTS** (tells browsers to never use plain HTTP for this host again); `X-Content-Type-Options`, a frame-ancestors policy, a Referrer-Policy.
2. **`limit_req`** zones keyed per client IP and per API key id, with a small burst and a JSON 429 body (E10: leaky bucket at the edge). The second zone is ready for S9's merchant keys, which arrive as `Authorization: Bearer sk_…` (the Stripe convention). Key the zone on the key's non-secret id, parsed from that header (an Nginx `map` is one way), never on the full key: a zone keyed on the raw header would keep secret key material in Nginx shared memory. Until S9 no request carries a key, the parsed value is empty, and Nginx does not count requests with an empty key.
3. **Provider callbacks are never rate limited** (E10): limiting them loses payments. `/providers/*` is excluded from `limit_req`; it is protected by the IP allowlist and Basic auth inside the adapter, and by its own pool.
4. The adapter's IP allowlist now sits behind a proxy: pass the real client address in a header only Nginx sets, and make the adapter trust that header only from Nginx.
5. A CORS allow-list (explicit origins, never `*` with credentials).
6. **Secrets:** SOPS-encrypted files in git (age keys), decrypted at deploy time into Docker secrets files that processes read at startup. SOPS encrypts the values inside YAML/ENV files with an age key (age is a small modern file-encryption tool), so the files can live in git while only the key holder can read them. No secret in an image, a build log or `docker inspect` output.

**Acceptance criteria.** A smoke check asserts: `http://` redirects to `https://`; the certificate is valid; HSTS and the other headers are present; a burst above the limit gets a JSON 429 on `/api/v1/*` but never on `/providers/*`; `gitleaks` finds nothing in the repo history.

> Your callback endpoint is now public. Click's browser Playground can test *your* Prepare/Complete with a secret you choose, no contract needed (it needs a CORS entry for its origin). If you have 15 spare minutes, it is a nice external check of your S5 adapter.

### 4.3 CD [8.5 h, must]

**Why.** A deploy is the most common cause of outages. The pipeline's job is to make the new version prove itself before it takes traffic, keep the old version alive until then, and make going back a button you have already pressed.

**What to build.**

1. **Images in GHCR tagged by git SHA** (never a moving `latest` for deploys).
2. **Failing security gates:** Trivy (image vulnerabilities) fails on HIGH and CRITICAL (`--severity HIGH,CRITICAL --exit-code 1`); `pip-audit` (dependency CVEs) has no severity threshold and fails on any known vulnerability, so each accepted exception is an `--ignore-vuln <ID>` with a dated justification in `docs/security/exceptions.md`; `gitleaks` fails on any committed secret. Pin the scanner actions by full commit SHA and the Trivy binary by version and checksum, and give the scan job no secrets: on 2026-03-19 the `aquasecurity/trivy-action` tags were force-pushed to a credential stealer (advisory GHSA-69fq-xp46-6x23), so a workflow pinned to a tag ran it. The general rule is in [testing-and-ci](testing-and-ci.md).
3. **Staging deploys automatically** from `main`; **prod requires a GitHub environment approval and deploys the same image digest** that passed staging.
4. **Pre-swap migrations** run as a one-off container using the `market_migrator` role, and are expand-only: they add, or they relax a constraint the old code already satisfies (see 4.4). **Post-swap (contract) migrations**, such as the physical `DROP COLUMN`, run as a separate pipeline step only after that environment's old containers have stopped.
5. **The health-gated swap** (P6 D97–D101): start the new containers next to the old ones, poll `/health` until it passes (a timeout aborts the deploy), switch the Nginx upstream, drain and stop the old ones.
6. **Graceful shutdown in every process type:** gunicorn stops accepting and finishes in-flight requests; Celery does a warm shutdown (your S4 `acks_late` makes an interrupted task safe); the relay finishes its batch and stops claiming rows; consumers stop consuming and ack what they finished. Set Compose `stop_grace_period` longer than the slowest of these.
7. **Rollback:** redeploying the previous SHA through the same pipeline. It is safe precisely because pre-swap migrations are expand-only. A contract migration is the point of no return for its change: run it only once you no longer want to roll back past it.
8. **Post-deploy smoke tests:** `/health`, a `/version` endpoint returning the SHA, a catalog page, and on staging one simulated payment.

**Pain-first.**

1. **Plant a problem for each gate:** a dependency with a known high CVE, a fake secret in a file, a vulnerable base image. Observe each gate fail the build. Record in `docs/evidence/s06/gates.md`.
2. **Break `/health` in the new version** on purpose and deploy it to staging. Observe the deploy abort with the old version still serving. Record the pipeline log in `docs/evidence/s06/health-abort.md`.
3. **Roll over without graceful shutdown** while `oha` hammers the site at a constant rate. Count connection resets and 5xx. Then add graceful shutdown and repeat. Record both numbers in `docs/evidence/s06/graceful.csv` (P6: zero-downtime is a property of the process, not only of the proxy switch).
4. **Exercise the rollback** once for real on staging and time it.

**Acceptance criteria.** Push to `main` → staging → approve → prod, verified live over HTTPS; prod reports the same SHA as staging; the rollover under load shows 0 resets with graceful shutdown; the rollback has been run at least once; the contract-migration step exists and refuses to run while an old container of that environment is still up.

> If you are stuck: what exactly does your `/health` check? If it returns 200 before the app can reach Postgres and RabbitMQ, what is it proving? And if it checks too much, what happens to a healthy deploy during a one-second Redis blip?

### 4.4 Zero-downtime migrations [5 h, must]

**Concept: expand/contract.** During a deploy, old and new code run **at the same time** against **one** schema (the old containers are still serving while the new ones start, and a rollback brings old code back). So every schema change must work with both versions. The technique has three phases:

1. **Expand:** add new structures that old code simply ignores (a nullable column, a new table, an index built `CONCURRENTLY`).
2. **Migrate:** make both versions of the data consistent (the code writes both old and new; a batched backfill fills history).
3. **Contract:** remove the old structures only when no running code, and no version you might roll back to, uses them.

A column rename in three deploys plus a contract step:

| Step | Migration | Code |
|---|---|---|
| Deploy 1 | Pre-swap: add the new column, nullable | Writes both columns, reads the old one. Then a batched backfill copies history in small chunks with pauses |
| Deploy 2 | Pre-swap: make the new column NOT NULL without a long lock: `ADD CONSTRAINT … CHECK (new IS NOT NULL) NOT VALID`, then `VALIDATE CONSTRAINT`, then `ALTER COLUMN new SET NOT NULL` (since PG12 this skips the table scan because the valid CHECK already proves there are no NULLs; it still takes a brief lock, so `lock_timeout` applies), then drop the CHECK | Reads the new column, still writes both (so a rollback to deploy 1 still sees fresh data) |
| Deploy 3 | Pre-swap: `ALTER COLUMN old DROP NOT NULL` (metadata only), plus `SeparateDatabaseAndState` to remove the old field from Django's model state while the column stays in the database | Uses only the new column |
| Contract (post-deploy, or a small deploy 4) | `DROP COLUMN old`, run only after the last deploy-2 container has drained | — |

**What to build.**

1. Pick a column that the checkout path reads, so the load test really exercises it, and rename it across the 3 deploys and the contract step **under load with 0 errors**.
2. A **batched backfill** (for example 10,000 rows per batch with a short sleep), never one giant UPDATE that locks the table and bloats WAL.
3. **`NOT VALID` + `VALIDATE`** for constraints; **`CREATE INDEX CONCURRENTLY`** for indexes (in Django this means a non-atomic migration; `django.contrib.postgres.operations` has operations for both).
4. **`lock_timeout = '3s'` in every migration**, so a DDL that cannot get its lock fails fast instead of queueing all traffic behind it. Decide whether you set it per migration or as a default of the `market_migrator` role, and write down why.
5. **A squawk gate:** squawk is a linter for Postgres migrations that flags DDL which takes heavy locks or rewrites a table. CI renders each new migration with `sqlmigrate` and fails on squawk's dangerous-operation rules.
6. **An old-code-against-new-schema test:** CI checks out the previous release tag, migrates the database to HEAD, and runs the previous release's smoke/integration tests against it.
7. **A new-code-against-its-own-schema insert test:** deploy-3 code inserts rows successfully against the deploy-3 schema, where the old column still exists.

**Pain-first.** On staging, under locust, ship a naive rename first: Django's `RenameField` and the code change in one deploy. Count the 500s during the rollover (old code asks for a column that no longer exists). Record in `docs/evidence/s06/naive-rename.md`, then do it properly (P6: "renaming a column and shipping the code change in the same deploy" is the named mistake).

**Acceptance criteria.** The 3-deploy rename and its contract step show 0 errors under load in `docs/evidence/s06/expand-contract.csv`; squawk blocks a deliberately bad migration (a plain `CREATE INDEX`, an `ALTER` that rewrites the table); the old-code test and the deploy-3 insert test are required checks.

> Questions to settle in your notes before deploy 3: what would every INSERT from deploy-3 code hit if deploy 3 skipped the `DROP NOT NULL`? And what would a still-running deploy-2 container, which still writes the old column, see if the contract step ran too early?

### 4.5 Observability [8.5 h, must]

**Why.** When something goes wrong at 3 am you need to answer three questions fast. **Metrics** say *that* something is wrong and how badly (rates, errors, latency). **Traces** say *where* the time went across processes. **Logs** say *what exactly* happened in one request. You also need **alerts**, or the 3 am incident is found at 9 am.

**What to build.**

1. **structlog** in every process, JSON, carrying `request_id` (from `X-Request-ID`, set by Nginx or generated) and `trace_id` / `span_id`.
2. **OpenTelemetry** instrumentation for Django, Celery, psycopg, httpx and AMQP. The trace context travels **through the outbox**: the API span's context is stored in the outbox row's `trace_context` (S4 already has the column), the relay puts it into AMQP headers, and the consumer continues the trace. Export through an OTel collector to **Tempo**.
3. **Prometheus** RED metrics (rate, errors, duration) per route *template* and per task, plus business metrics: `checkout_success_total`, `provider_callback_seconds` (histogram, labels provider and method), `outbox_lag_seconds`, `recon_drift_rows`. Exporters for Postgres, RabbitMQ and Redis. **No high-cardinality labels**: never a user id, order id or raw URL path as a label.
4. **Grafana** dashboards: RED per process type, business metrics, Postgres, queues; Loki and Tempo as data sources with links from a trace to its logs.
5. **Alertmanager** with a rule on `outbox_lag_seconds` whose threshold you derive from the relay's poll interval plus the staleness you can tolerate (P7's method), routed to a receiver you actually watch.
6. **Loki**, with **Grafana Alloy** as the log collector (Promtail reached end of life on 2026-03-02), collecting every container's stdout. Alloy is an OpenTelemetry Collector distribution, so it can also forward traces to Tempo and you may run one agent for both.
7. **Sentry** (SaaS developer tier) in every process, with release = git SHA and environment = staging/prod.

**Pain-first.**

1. **A trace that stops at "published".** Instrument only the web process first. Before you open Tempo, predict and commit which spans of one checkout you will see and where the trace will end. Run one checkout, open it in Tempo, and record where it actually stops and which processes are missing. Screenshot it into `docs/evidence/s06/trace-before.png`. Then carry the context through the outbox and AMQP headers and capture the full waterfall, with the outbox lag visible as a gap, in `trace-after.png`.
2. **Fire and resolve the lag alert:** stop the relay, watch `outbox_lag_seconds` climb and the alert fire, start it again, watch it resolve.

The "find a bug through Sentry first" exercise (P6 D106) is in §14 Stretch.

**Acceptance criteria.** One checkout traced end to end from Nginx through the callback, the relay and the consumer; the lag alert fired and resolved (screenshots committed); one `request_id` searchable across all processes in Loki; the metric label audit (a short list of every label and its maximum cardinality) in `docs/evidence/s06/labels.md`.

### 4.6 Postgres operations [6.5 h, must]

**Why.** A backend engineer who can only write queries is helpless when the database itself is the incident. This block is a guided tour of the things that go wrong in real Postgres installations, each reproduced on purpose (P8 D127–D132 is the reading).

**What to build and reproduce.** Do each on the bench stack or a lab container unless it says staging.

1. **Find the expensive queries.** Enable `pg_stat_statements`; after a locust run, list the top 10 by total and by mean execution time; feed the top one to `EXPLAIN (ANALYZE, BUFFERS)`. Turn on `auto_explain` for slow statements. Record in `docs/perf/s06.md`.
2. **Stale statistics.** With autovacuum off on a lab table, bulk-load rows. Predict and commit how far the planner's row estimate for a filtered query will be from the truth, then run `EXPLAIN (ANALYZE)` and record estimated vs actual rows. Run `ANALYZE` and repeat. Then show a correlated-columns misestimate on `(vendor_id, category_id)` in the catalog, and fix it with `CREATE STATISTICS`.
3. **Bloat on the payment tables.** Watch `n_dead_tup` and `pgstattuple` on the status-churning S5 tables under traffic; tune autovacuum per table; write down why `VACUUM` usually does not shrink the file, the one case where it does (empty pages at the end of the table), and what does shrink it (`VACUUM FULL`, pg_repack).
4. **HOT updates.** A HOT (heap-only tuple) update writes the new row version on the same page without touching any index, which is much cheaper. It only happens when no indexed column changes and the page has free space. Run the experiment on a status-churning table whose indexes do not mention the status column (check with `\d`; `ordering_order`, `payment_intents` or `order_vendor_groups` are candidates): set `fillfactor` to 85 and compare the `n_tup_hot_upd` ratio before and after. Then predict and commit: does the same change help on the S5 attempts table, whose partial unique indexes mention `state` in their `WHERE`? Run it there too and record the contrast (check your prediction in §16). If attempts cannot get HOT updates, record that as a deliberate trade-off of correctness over HOT; do not drop the S5 indexes.
5. **The lock-queue incident** (staging, weekend block). Start a long SELECT on `ordering_order`, then run `ALTER TABLE ordering_order …` without `lock_timeout`. The ALTER waits for its ACCESS EXCLUSIVE lock behind the SELECT. Before you run it, predict and commit: what happens to a plain read of `ordering_order` that arrives while the ALTER waits, to checkout, to Payme callbacks, and to token refresh (the S3 refresh-rotation endpoint)? Then run it, and find the blocker with `pg_blocking_pids()` and `pg_stat_activity`. Record the numbers: duration, checkout errors, callback p99, how many callbacks the sim saw time out, and **token-refresh p99 during the stall**. Refresh rotation never touches `ordering_order`, so if its p99 rises anyway, write down which shared resource it waited on. Check your prediction in §16. **Keep the numbers: they are evidence for ADR-030 and ADR-031 in S9.**
6. **Replication-slot disk fill** (lab container with a small, dedicated volume, never prod and never the laptop's main disk). Create a slot, stop its consumer, generate WAL with pgbench, and watch `pg_wal` grow (`pg_replication_slots.wal_status`, `safe_wal_size`). Do it twice. **Run 1** with the default `max_slot_wal_keep_size = -1`: predict and commit what happens when the volume fills, then observe; expect to lose the lab instance. **Run 2** with a limit set: record how `wal_status` changes and when the slot is invalidated (check both predictions in §16). Record what each run costs you, and what you would alert on.
7. **`synchronous_commit=off`, measured.** With pgbench, compare TPS for small standalone inserts with it on and off. Use it (as `SET LOCAL`) only for standalone event and telemetry inserts that live in their own transactions. **Never for the ledger**, and never for a transaction that also writes orders or the outbox. Write down what an acknowledged-but-lost commit would mean for each table.

**Acceptance criteria.** Every item has an evidence file under `docs/evidence/s06/pg/`; the lock-queue numbers (including token-refresh p99) are in a table ready to paste into ADR-030 and ADR-031; a runbook entry exists for "checkout hangs: find the blocker".

### 4.7 Replica and read-your-writes [2.5 h, must]

**Why.** A read replica takes load off the primary, but it is always a little behind. "Read-your-writes" is the guarantee that after you change something, you see your change; a replica breaks it silently.

**What to build.**

1. A streaming replica of `market`; a Django database router sending reporting and the vendor dashboard to it. Anything that decides about money or stock keeps reading the primary.
2. Replication lag exported as a metric and shown on the Postgres dashboard.

**Pain-first.**

1. Route the order status page to the replica. Induce lag deterministically (pause replay on the replica with `pg_wal_replay_pause()`).
2. Predict and commit what the status page will show after you pay. Then pay through the simulator and record what the redirect to the status page shows, and whether the Perform callback had committed on the primary by then (check your prediction in §16).
3. Record in `docs/evidence/s06/ryw.md`, then fix it with sticky-primary-after-write or an **LSN wait**. An LSN (log sequence number) is a position in the WAL. The primary can tell you the WAL position after your commit (`pg_current_wal_lsn()`), and the replica can tell you how far it has replayed (`pg_last_wal_replay_lsn()`). An LSN wait compares the two: the replica serves the read only once its replay position has reached the LSN you recorded. What it does while it waits, and for how long, is your design.
4. Also run a long reporting query on the replica during heavy writes and note any "canceling statement due to conflict with recovery". Write down the two settings that trade this against primary bloat or replica staleness.

**Acceptance criteria.** A test with replay paused proves the status page no longer shows stale state; the measured lag range is recorded.

> A subtlety worth a paragraph in your notes: the write the buyer needs to see was made by the **provider's callback**, not by the buyer's own request. A naive "stick to the primary for 5 seconds after *this session* writes" misses it. Which write in the buyer's session can you anchor on instead, or should this read never go to a replica at all?

### 4.8 PITR [3.5 h, must]

**Concept: point-in-time recovery.** `pg_dump` gives you the database as it was when the dump ran; everything after that is lost, so its **RPO** (recovery point objective: how much data you can lose) is "since the last dump". PITR combines a **base backup** (a physical copy of the data directory) with a **continuous archive of the WAL** (the write-ahead log, which records every change). To restore, you restore the base backup and replay the WAL up to a chosen moment, for example one second before a bad UPDATE. RPO drops to seconds (bounded by how quickly WAL segments reach the archive). **RTO** (recovery time objective: how long until you are serving again) is the restore plus the replay time. A backup is only a backup once you have restored it.

**What to build.**

1. pgBackRest or wal-g archiving WAL and taking base backups to the `atlas-wal` bucket (choose one and write down why).
2. **The drill** (weekend block): take a base backup; run traffic; note the time; run a deliberately bad UPDATE (for example every offer price set to 0); restore into a scratch instance to 1 second before it; verify the prices are correct and **the trial balance is identical** to before the incident.
3. **A nightly restore-verify workflow:** restore the latest backup into an ephemeral container, run the trial balance, the S5 `sql-invariants` queries and row-count checks, and fail loudly if anything differs. Alert if the newest successful backup is older than your RPO.
4. `docs/runbooks/backup-dr.md`: both procedures (pg_dump and PITR), the achieved RPO and RTO, and the monthly storage cost of the WAL archive.

**Acceptance criteria.** The restore log with timestamps is committed in `docs/evidence/s06/pitr-restore.md`; the achieved RPO/RTO are measured, not estimated; the nightly job has run green at least three times.

### 4.9 Performance [3 h, must]

**Why.** Everyone has a theory about what is slow; profilers have facts. The lesson is the method: measure, find the actual hot spot, fix it, measure again on the same load profile.

**What to build.**

1. A locust checkout scenario driven by worldgen's `traffic` mode, run under the ADR-002 protocol (fixed limits, warm-up, median and min–max). locust shapes the traffic; the p95/p99 you report come from a constant-rate **oha probe** running alongside it (`oha -q <rate> --latency-correction`, so latency is measured from each request's intended send time and coordinated omission is corrected), with the server-side Prometheus histograms as a cross-check. The final before/after pair uses 5 runs each; the intermediate `gthread` configuration uses 3.
2. Find the real bottleneck with **py-spy** (a flame graph of the gunicorn workers; the container needs the ptrace capability) and a **`pg_stat_statements`** row. It is **not** the idempotency-key index: that column is already UNIQUE, so it is already indexed, and dropping the index would drop the guarantee (P9 D155's "add an index" advice is wrong here). Likelier suspects: unique-insert contention, DB pool exhaustion, a network call inside a transaction, an N+1 on the checkout path, or the gunicorn worker model.
3. Compare gunicorn `sync` and `gthread` workers on the same profile.

This block contains about 80 minutes of unattended benchmark time (before and after: 2 configurations × 5 runs; `gthread`: 1 configuration × 3 runs; about 6 minutes per run at 5-minute runs plus warm-up). Schedule it in the weekend block.

**Pain-first.** Before profiling, write down your guess for the bottleneck. Then profile. Record the guess next to the answer in `docs/perf/s06.md`.

**Acceptance criteria.** Flame graph and the `pg_stat_statements` row committed; before/after p95 on the same profile; the sync vs gthread table.

*Degrade option #18:* drop the gthread comparison (saves 0.5 h).

### 4.10 SLO and drill [3 h, must]

**Concept: SLI, SLO, error budget.** An **SLI** (service level indicator) is a measured ratio of good events to valid events, for example "checkout requests answered with a success or an expected 4xx within 800 ms, out of all checkout requests". An **SLO** (objective) is a target for that ratio over a window, for example 99.5% over 28 days. The **error budget** is what the SLO allows to fail: 0.5% of that window's checkouts. While budget remains you may ship risky changes; when it is spent, you slow down and fix reliability. An SLO must be **derived from measurements** of what the system actually does, never wished (P9 D154–D156).

**What to build.**

1. **Two SLOs** in ADR-022: checkout success, and provider callback latency (callbacks answered within a threshold with a protocol-valid reply). Define each SLI precisely (which requests count, what "good" means), the window, the target, and the error budget in events per window. Take the numbers from your locust and split-gate runs.
2. **Every SLO has an alert.** Test the alert rules with `promtool test rules` and fire each one once for real.
3. **Runbook "payment success rate dropped"** (`docs/runbooks/payment-success-dropped.md`): what to check first, second and third, using the dashboards you built.
4. **A live drill:** kill the relay under traffic, follow the runbook blind, resolve it, and write a blameless postmortem in `docs/postmortems/` that includes **what the runbook missed**.

**Pain-first.** The drill is the pain. Before the drill, predict and commit what the buyer and the provider each see while the relay is dead; afterwards, compare with what happened (§16). Did your runbook lead from "payment success dropped" to the actual cause quickly, or did you guess?

**Acceptance criteria.** ADR-022 merged with the numbers it was derived from; alert tests green; the postmortem committed.

### 4.11 Split gate + bulkhead [4.5 h, must]

**Concept: the split gate.** Atlas never extracts a service because "that is how microservices are done". It extracts one only when a **measured problem** says the monolith is hurting, and only after the cheap fix inside the monolith was measured first. The split gate is that measurement, as a script anyone can re-run and get comparable numbers from. Its result goes into every extraction ADR from here on: ADR-027 (ai, [Stage 08](stage-08-ai-integration.md)), ADR-030 and ADR-031 (atlaspay and auth, [Stage 09](stage-09-strangler-atlaspay-auth.md)), ADR-036 (inventory, [Stage 10](stage-10-kubernetes-grpc-inventory.md)), ADR-040 and ADR-042 (ledger and fraud, [Stage 12](stage-12-data-at-scale-fraud.md)). **If the numbers do not hurt, the ADR must say so, and argue only from blast radius or security scope, or the split does not happen.**

**What to build: `bench/split-gate` and ADR-023.**

1. **The scenario, 10 minutes:**
   - worldgen `traffic` mode driving the catalog at about 200 rps (scaled to your bench limits, stated in the result);
   - a provider-sim **callback storm with duplicates** (Payme and Click, chaos switches on);
   - **one deploy with an expand migration in the middle** of the run, using your CD swap script.
2. **What it records:**

   | Metric | Why it matters for a split decision |
   |---|---|
   | Callback p99 | Providers treat slow answers as failures |
   | % of Payme -32400s and timeouts, and Click errors | Payment failures caused by *your* side |
   | Payment p99 against catalog load | Does unrelated traffic hurt payments? |
   | Checkout p95 | The buyer-facing cost |
   | DB pool saturation | Are workloads competing for connections? |
   | The secrets each process holds (names only, never values) | Security scope: which processes could leak which keys |

3. **The protocol** (ADR-002 applied): fixed container CPU and memory limits, 60 s warm-up, **5 runs for the final before/after pair** of a split-gate ADR and 3 runs for any intermediate configuration, median and min–max, and every result stamped with the worldgen version and seed, the git SHA, image digests, CPU model and limits. worldgen and the callback storm shape the traffic; the reported p95/p99 come from a constant-rate oha probe (`-q <rate> --latency-correction`) recorded into an HDR histogram, cross-checked against the server-side Prometheus histograms. **Noise rule:** a difference inside the run spread counts as "no difference".
4. **The cheap fix first:** run the gate with the shared pool, then with `/providers/*` on its own gunicorn pool (outcome 11 in §2), and compare. This is the final before/after pair, so 5 runs each. Write down what the pool fixed, and what it could not fix (both pools still share one database, its migrations, its locks, and every secret).
5. **ADR-023** holds the protocol (including the 5-runs / 3-runs rule) and the **baseline numbers**; the raw CSVs live in `docs/evidence/s06/split-gate/`.

This block contains about 110 minutes of unattended benchmark time (2 configurations × 5 runs × 11 minutes, warm-up included). Schedule it in the weekend block; build and dry-run the harness with one short run first.

**Acceptance criteria.** Two gate results (shared pool, separate pool), each 5 runs, reproducible from the committed command line; the baseline table in ADR-023; the secrets-per-process table.

### 4.12 Storefront and E2E [3 h, must]

**Why.** A portfolio needs something a person can click, and an end-to-end test catches what unit tests cannot: a broken route, a hidden submit button, a redirect loop.

**What to build.** A minimal server-rendered storefront (Django templates): catalog → cart → checkout → redirect to the simulator's checkout page → back to a **status page that polls** until the order is paid. Record how many polls a payment takes and the time to "paid": this is the baseline the realtime work in [Stage 11](stage-11-realtime-edge-graphql.md) must beat. A Playwright test drives that flow against **staging** after every staging deploy.

**Acceptance criteria.** Playwright green in CI against staging; the poll count and time-to-paid recorded in `docs/evidence/s06/polling-baseline.md`.

### 4.13 Drills + SD19 / SD17 [5 h, must]

One hour a week for five weeks: one SQL problem on the Atlas schema (this stage: the `pg_stat_statements` top-N, a replication-lag query, a batched-backfill query) or one DSA problem, plus the week's interview questions out loud. In W26 the drill hour is the SD19 session, and in W27 the SD17 session (§9).

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| HTTPS only | Nginx redirect + HSTS | Smoke: `http://` → 301 to `https://`, HSTS present, certificate valid |
| Prod runs the exact SHA that passed staging | Prod deploys by image digest from the staging run; `/version` returns the SHA | Deploy-prod job compares the running digest with staging's |
| No deploy skips the health gate | The swap script refuses to switch the upstream until `/health` passes | The broken-health deploy aborts with the old version live |
| Every migration works with both old and new code | Expand/contract discipline; squawk; `lock_timeout` | The old-code-against-new-schema CI job |
| Every SLO has an alert | Alert rules committed next to ADR-022 | `promtool test rules`; each alert fired once live |
| A backup counts only once it has been restored | Nightly restore-verify; backup-age alert | The restore-verify workflow's history |
| No resource exists outside Terraform | Plan on PR, apply from main | Clean `plan` after `apply`; the destroy/re-apply log |
| Provider callbacks are never rate limited | `/providers/*` excluded from `limit_req`; allowlist + own pool instead | Smoke: a burst on `/providers/*` never gets 429 |
| No payment or stock decision reads the replica | The DB router's allow-list | A test that the router sends those models to the primary |

---

## 6. Tests to write

1. **Playwright E2E** against staging: browse → cart → checkout → simulated Payme payment → status "paid".
2. **Smoke tests** after every deploy (health, version SHA, catalog, one simulated payment on staging, TLS and header checks).
3. **Migration compatibility:** the previous release's tests against the HEAD schema; deploy-3 code inserting against the deploy-3 schema; a squawk-must-fail fixture migration.
4. **Graceful shutdown:** a rollover under load with the reset count asserted to be 0.
5. **Alert rules:** `promtool test rules` for every alert; a live alert-fires test for `outbox_lag_seconds`.
6. **Trace propagation:** the consumer's span has the same `trace_id` as the API span that wrote the outbox row.
7. **Read-your-writes** with replica replay paused.
8. **`lock_timeout`:** a migration run against a table with a held lock fails within about 3 seconds instead of hanging.
9. **Restore-verify** (nightly).
10. **locust + py-spy** runs under the ADR-002 protocol, with percentiles from the oha probe; the nightly p95 budget from S3 now also covers checkout.

---

## 7. CI changes

| Job | What it gates |
|---|---|
| `build-push` | Images built once, tagged by SHA, pushed to GHCR |
| `trivy`, `pip-audit`, `gitleaks` | Trivy fails on HIGH/CRITICAL image CVEs; pip-audit fails on any known vulnerable dependency not listed in `docs/security/exceptions.md` (`--ignore-vuln`); gitleaks fails on committed secrets |
| `migration-lint` | squawk on `sqlmigrate` output of new migrations |
| `migration-compat` | The previous release's tests against the HEAD schema |
| `terraform-plan` / `terraform-apply` | Plan on PRs touching `deploy/terraform/**`; apply only from `main` behind an environment |
| `deploy-staging` | Automatic on `main`: migrate (expand only), health-gated swap, smoke, Playwright; then contract migrations once the old containers have stopped |
| `deploy-prod` | Environment approval; same digest; smoke; automatic redeploy of the previous SHA if smoke fails |
| `rollback` | Manual trigger: redeploy a given previous SHA |
| `restore-verify` (nightly) | Restore the latest backup and check the trial balance and invariants |
| `locust` (nightly) | Checkout and catalog p95 budgets (locust traffic, percentiles from the oha probe) |

See [testing-and-ci](testing-and-ci.md) for the full matrix.

---

## 8. ADRs and documents

**ADR-021 Deploy topology and region.**
- Questions: one VM or two? Where does staging live, and how isolated is it? What runs where, and how much RAM does it use at peak? What does a replica on the same VM protect against, and what does not? Why an EU region for synthetic data, and what would change for a real launch (Uzbek personal-data localisation, [U])?
- Numbers: VM size, peak memory, container count (kept for ADR-035), monthly cost against the $50 cap.
- Counter-argument: "Use a PaaS and a managed database." Hint: argue from your peak-memory and monthly-cost numbers, and from the evidence under `docs/evidence/s06/pg/`: which of those lessons would a managed service have hidden from you, and which would you still buy in real life?

**ADR-022 SLOs.**
- Questions: which SLIs, defined how precisely; which windows; which targets; what happens when the budget is spent; which alert protects each SLO.
- Numbers: the measured success rates and latencies the targets were derived from, and the resulting budget in events per window.
- Counter-argument: "Aim for 99.99%", or "a portfolio does not need SLOs". Hint: argue from your measured success rates and the drill postmortem: what would each extra nine do to the error budget in events per window?

**ADR-023 Split-gate protocol.**
- Questions: what the gate measures and why each metric bears on a split; the scenario; the run protocol and noise rule (5 runs for the final before/after pair, 3 for intermediate configurations; percentiles from the constant-rate probe); what counts as "the numbers hurt"; what must be tried inside the monolith first.
- Numbers: the **baseline** table (shared pool) and the **cheap-fix** table (separate `/providers/*` pool), with medians and spreads, plus the secrets-per-process table.
- Counter-argument: "Everyone splits payments out; just do it", or "the gate is overhead". Hint: argue from your cheap-fix table (`docs/evidence/s06/split-gate/`): what did the separate pool already fix without a split, and what would you have had to undo in S9 if you had split first?

**Other documents:**
- Runbooks: payment success dropped; outbox lag; checkout hangs (lock blocker); replication slot growing; restore from PITR.
- The drill postmortem (blameless, including what the runbook missed).
- `docs/runbooks/backup-dr.md` with the achieved RPO/RTO.
- `docs/perf/s06.md`: top queries, the bottleneck hunt, before/after, sync vs gthread.
- `docs/privacy/data-governance.md` v1.
- **README v1:** what Atlas is, an architecture diagram, the numbers you are proud of (0-error deploy, restore RPO/RTO, SLOs, split-gate baseline), the public URL, and a 5-minute demo script (or recording).

---

## 9. System design session

- **SD19 — Design a distributed logging and metrics pipeline** ([system-design-problems.md](../../system-design-problems.md)). **Built-lite**, W26; revisited in [Stage 07](stage-07-polyglot-mongo-timescale.md) with Timescale. Whiteboard first: shipping logs and metrics off a fleet without the shipping becoming the bottleneck (local buffering, async batches, sampling), why a time-series store differs from a Postgres row store (columnar, downsampling), and how alerting stays fast without rescanning raw data. Then compare with what you run: Prometheus's pull model and local TSDB, Loki's label index, Tempo's trace storage, the OTel collector as the buffer.
- **SD17 — Design distributed file storage.** **Built-lite**, W27: presigned uploads to the S3-compatible store (Garage) since S1, and now the WAL archive in object storage. Whiteboard chunking, dedup, replication and placement, and the split between a small, strongly consistent metadata store (your Postgres) and a large blob store. Where does pgBackRest or wal-g sit in that picture?
- Write `docs/sd/sd19.md` and `docs/sd/sd17.md`, each with a "what I built vs what I drew" diff.

---

## 10. Interview questions this stage lets you answer

- Walk me through a deploy where the new version is broken.
- Metrics vs logs vs traces: what does each answer?
- A query plan went bad overnight and no code changed. Where do you look?
- Why does VACUUM usually not shrink the file? When does it, and what does?
- Rename a column in 3 deploys. Why three, and when does the old column actually get dropped?
- pg_dump vs PITR: what RPO does each give you, and what did your restore achieve?
- What does an abandoned replication slot do?
- One long SELECT and one ALTER TABLE stalled your checkout and your payment callbacks. Explain the lock queue.
- How does a trace survive a trip through the outbox and RabbitMQ?
- Why no user id label on your Prometheus metrics?
- How did you derive your SLO, and what is your error budget in requests?
- What did your drill reveal that the runbook did not cover?
- How did you find the bottleneck? Show me the flame graph or the `pg_stat_statements` row.
- When is `synchronous_commit=off` acceptable, and why never on the ledger?
- Why is `/providers/*` on its own pool, and what did that not fix?
- What would make you *not* split a service, even if everyone expects it?

---

## 11. Common mistakes to watch for

1. **Scanners that warn instead of fail**, and are then ignored (P6 D97–D101).
2. **Rebuilding the image for prod**, so prod runs something staging never saw.
3. **A health check that checks nothing**, or one so strict that a one-second Redis blip fails every deploy.
4. **Renaming a column in the same deploy as the code change; one giant UPDATE backfill; a plain `CREATE INDEX` on a live table; a migration without `lock_timeout`** (P6).
5. **High-cardinality labels** (user id, order id, raw path), which explode Prometheus memory (P6 D103–D108).
6. **Dashboards with no alerts.**
7. **A backup nobody has restored** ("a backup you have never restored is a hope, not a plan", P9).
8. **An SLO derived from a wish** instead of from measurements (P9 D154–D156).
9. **Rate limiting provider callbacks** at Nginx, which loses payments (E10).
10. **Reading payment state from the replica**, or setting `synchronous_commit=off` for the ledger.
11. **Disabling autovacuum "for performance"** (P8).
12. **Guessing the bottleneck**, for example "add an index on the idempotency key" when it is already UNIQUE (P9 D155 suggests that index; §4.9 explains why it is wrong).

---

## 12. How real companies differ

- **Managed databases.** Most teams buy RDS or Cloud SQL, where PITR, replicas and failover are settings. You do it by hand once so you know what those settings actually do and can reason about RPO and failover when they fail.
- **Orchestrators and progressive delivery.** Production teams deploy with Kubernetes or a PaaS, and ship with canaries that are analysed automatically. Your health-gated script is the same idea without the platform; canaries arrive with the flags in S8, Kubernetes in S10.
- **On-call and paging.** Real teams have rotations, paging tools and multi-window burn-rate alerts. Your single-person drill is the minimum version of that discipline.
- **High availability.** Real primaries fail over automatically (Patroni, cloud HA) across zones. Your replica is on the same host and is there to learn lag and read-your-writes, not to survive a host failure.
- **Observability at scale** uses sampling, retention tiers and often a SaaS vendor. The pillars and the questions they answer are the same.

---

## 13. Deliberately not doing

| Item | Why not now | When it arrives |
|---|---|---|
| Kubernetes | Compose still copes; record the container count as future evidence | [Stage 10](stage-10-kubernetes-grpc-inventory.md) (ADR-035) |
| Vault | Secrets are still few and in one trust domain; SOPS + Docker secrets are enough | [Stage 09](stage-09-strangler-atlaspay-auth.md) |
| A managed database | You are learning to operate Postgres; in real life you would buy it | Named in ADR-021; the Season 2 warehouse may use a managed service |
| Canary releases | They need stable per-user flags | [Stage 08](stage-08-ai-integration.md) (hash-bucket flags) |
| Service extraction | The split gate has only just produced a baseline | S8 onward, each with its gate run |

---

## 14. Stretch

Only if the must tier closes early.

- **SLO burn-rate alerts [1 h]:** alert on how fast the error budget is being spent (a fast and a slow window), instead of on a raw threshold.
- **pg_repack demo [1 h]:** remove the bloat you measured without a long exclusive lock, and compare with `VACUUM FULL`.
- **A PG 17 → 18 upgrade rehearsal via logical replication [2 h]:** a PG 18 instance subscribed to a publication, a cutover, and a note on what logical replication does not copy. This is also a rehearsal for the S9 strangler.
- **Find a bug through Sentry first [1 h]** (P6 D106). Ask someone (or a script with a random seed) to inject a bug into a posting path, for example one that makes the S5 constraint trigger fail at COMMIT inside a Celery task. Find it from the Sentry alert, with its context, **before** reading the code. Write down what Sentry showed you and what was missing.

Two smaller ideas carry no budgeted hours; do them only after everything above: **`auto_explain` sampling** (log a sample of plans instead of only slow ones, and measure its overhead) and **Nginx microcaching** (a one-second cache on public catalog pages, and a note on why it must never cover anything personalised or financial).

---

## 15. Definition of done

- [ ] **Slice 1:** a public HTTPS URL where a visitor can browse, check out and pay through the simulator.
- [ ] A Grafana dashboard with RED, business, Postgres and queue panels, linked from the README.
- [ ] One checkout traced end to end in Tempo (Nginx → web → callback → relay → consumer).
- [ ] A deploy under load with 0 errors, and the expand/contract rename across 3 deploys and the contract step with 0 errors.
- [ ] The broken-health abort and one real rollback, both logged.
- [ ] The PITR restore log with an identical trial balance and the achieved RPO/RTO; nightly restore-verify green.
- [ ] The lock-queue incident numbers (including token-refresh p99) saved for ADR-030 and ADR-031; the slot-fill and other Postgres evidence under `docs/evidence/s06/pg/`.
- [ ] ADR-021, ADR-022 (with alerts tested) and ADR-023 (with the baseline and cheap-fix numbers) merged.
- [ ] Runbooks, the drill postmortem, `docs/perf/s06.md`, `docs/privacy/data-governance.md` v1.
- [ ] README v1 with a diagram, the numbers and a 5-minute demo.
- [ ] `docs/sd/sd19.md` and `docs/sd/sd17.md`.
- [ ] Two STAR stories in `docs/star/`: **the lock-queue stall** and **the rollback nobody had ever exercised**.
- [ ] A postmortem paragraph for the stage.
- [ ] `docs/deferred.md` re-read and updated.
- [ ] Git tag `v0.6`.

---

## 16. If you get stuck

- **Terraform.** Start with one resource (a DNS record), apply it, change it, watch `plan` show the diff. Only then add the VM. Reread [P9](../python/09-payflow.md) D151–D153.
- **Nginx and TLS.** Test every rule with `curl -I` before trusting it. Which header does your adapter trust for the client IP, and could a client forge it?
- **CD.** Write the swap as numbered steps on paper first (P6 D97–D101 lists seven). At which step does a broken version get stopped? At which step would requests be dropped without graceful shutdown?
- **Zero-downtime migrations.** For each deploy, ask: if the previous version's containers are still running right now, does anything break? If you rolled back right now, would anything break? Reread [P6](../python/06-ledgerbase.md) D97–D101.
- **Observability.** If a trace breaks, find the first process where the `trace_id` changes. Is the context being written into the outbox row, and read back by the relay? Reread [P6](../python/06-ledgerbase.md) D103–D108.
- **Postgres operations.** Compare estimated and actual rows first; most bad plans start there. For the lock queue, remember that the waiting ALTER blocks newcomers, not only the SELECT that is in its way. Reread [P8](../python/08-docuvault.md) D127–D132.
- **Replica.** Can you make the lag deterministic before you try to fix read-your-writes? If the test only fails sometimes, it is not a test yet.
- **PITR.** Rehearse the restore on your laptop before the weekend drill. Did you write down the exact time of the bad UPDATE, in which time zone?
- **Performance.** If the flame graph shows workers mostly waiting, the problem is not Python CPU: look at the pool and at `pg_stat_activity`.
- **SLO and drill.** Start from what you measured, not from a round number. During the drill, write down every guess you made; each guess is a missing runbook line. Reread [P9](../python/09-payflow.md) D154–D156.
- **Split gate.** If two runs disagree by more than the effect you are measuring, fix the protocol (limits, warm-up, seed) before drawing any conclusion. For the bulkhead, [P10](../python/10-atlasmarket.md) D163–D165 shows sizing pools from load numbers.
- **Storefront.** Keep it ugly and server-rendered; the E2E test is the point.

<details>
<summary>Check your prediction (open only after you committed yours and ran the exercise)</summary>

- **4.5, the trace that stops at "published".** Without context propagation the trace ends at the outbox insert in the web process. The relay, RabbitMQ and the consumer that marks the order paid either do not appear or start traces of their own with new `trace_id`s.
- **4.6 item 2, stale statistics.** The estimate is typically off by one to two orders of magnitude (around 100× is common after a large bulk load) until `ANALYZE` runs.
- **4.6 item 4, HOT on attempts.** No. A column used in a partial index's `WHERE` counts as indexed for HOT, so every state change on attempts is a non-HOT update whatever the fillfactor: `n_tup_hot_upd` stays flat there, while the table without such an index improves.
- **4.6 item 5, the lock queue.** Every new query on `ordering_order`, even a plain read, queues behind the *waiting* ALTER, not only behind the SELECT. Checkout stalls. Payme callbacks stall too, because the callback path reads `ordering_order` inside its transaction (through ordering's `api`, to confirm the order is still payable), and the consumer that marks orders paid queues as well. Token refresh never touches `ordering_order`, so any slowdown there is indirect: market-web's gunicorn threads and DB connections fill up with checkout requests stuck behind the lock. A separate pool for the auth endpoints would cure that, which is why ADR-031 has to treat it as the weakest reason for the auth split.
- **4.6 item 6, the replication slot.** Run 1: the slot keeps every WAL segment, `pg_wal` grows until the volume is full, and the server stops with a PANIC ("No space left on device"): an outage. Run 2: `wal_status` moves from `reserved` to `extended` to `unreserved`, and at a checkpoint to `lost`; the slot is invalidated and the server stays up, but the subscriber must be rebuilt.
- **4.7, read-your-writes.** The status page shows "unpaid": it read the replica, which had not yet replayed the Perform callback's commit, although the primary had committed it before the redirect.
- **4.10, the relay drill.** Provider callbacks still succeed, because a callback commits its state and an outbox row and answers, so the provider sees a healthy merchant. Nothing relays the outbox, so orders are never marked paid and the buyer's status page keeps polling. The first clear signal is outbox lag, not a payment error.

</details>
