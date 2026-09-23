# Stage 10 — Kubernetes + gRPC inventory + bot webhook

| | |
|---|---|
| **Weeks** | W43–W46 (4 weeks) |
| **Hours** | 48 must + 6 stretch (stretch only if the must tier closes early) |
| **Architecture at start → at end** | market, atlaspay, auth, ai, bot (polling) and provider-sim on Compose on the Terraform VPS → **everything on Kubernetes**: kind locally, k3s in the cloud via Terraform (`atlas-staging`, `atlas-prod`), zero-downtime rollouts, **+ inventory** (grpc.aio, its own `pg-inventory` cluster), **PgBouncer**, the atlaspay scheduler leader-elected with a Lease, the bot on **webhooks** |
| **New technologies** | Kubernetes (kind, k3s), Kustomize, Helm (third-party charts only), Gateway API through Traefik (Gateway provider enabled) or Envoy Gateway, cert-manager (Gateway API support enabled), External Secrets Operator or Vault Agent, HPA + metrics-server, NetworkPolicy, `coordination.k8s.io` Lease, PgBouncer ≥ 1.24, gRPC (grpcio 1.84, `grpc.aio`), protobuf + buf (`buf.yaml` v2), kubeconform, aiogram 3.31 webhook mode, Telegram Login Widget |
| **Portfolio tag** | `v0.10` |
| **Old-spec theory to read** | P8 D127–D132 ([DocuVault](../python/08-docuvault.md) §10–§11 and [phase-5](../../phase-5-scaling-architecture.md) Week 22: kind, probes, preStop, HPA, `rollout undo`, etcd/Raft on D128 and D132, PgBouncer); P9 D151–D153 ([PayFlow](../python/09-payflow.md) §10a: gRPC deadlines, status codes, REST vs gRPC); Proj28 D175–D178 ([phase-6](../../phase-6-capstone.md) Week 30: leader-only dispatch, kill the leader mid-dispatch); P1 D19–D24 ([StockPilot](../python/01-stockpilot.md) Stage 4: naive order first, then `FOR UPDATE` vs atomic `UPDATE`); P10 D163–D168 ([AtlasMarket](../python/10-atlasmarket.md): bulkhead, `docs/distributed-transactions.md`, whiteboard checkout); P2 §20 Week 7 ([QuickServe](../python/02-quickserve-pos.md) Telegram extension: webhook vs polling) |

Version pins are as of 2026-09 — re-check with `scripts/compat_check.sh` at the start of the stage. DocuVault (P8) used the NGINX Ingress Controller; ingress-nginx is retired (announced 2025-11-11; no releases or security fixes after March 2026) [C] ([Kubernetes blog](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)), and the community recommends Gateway API, so do not copy that choice.

> **What this stage is really for.** Kubernetes is not the goal; operating a growing set of deployables (six production ones by the end of this stage, nine by S12) with zero-downtime rollouts, autoscaling and declarative state is. Along the way you meet three classic traps that only appear once there are replicas: gRPC pinning every call to one pod, a lock holder that does not know it has lost its lock, and Telegram's rule that only one process may poll a bot. You also extract inventory, but only after measuring whether cheaper fixes (a Redis gate, a separate checkout Deployment) already solve the flash sale.

**Schedule and checkpoint.** The block budgets below are bottom-up estimates sized to the 12 h/week floor; keep logging actual hours per block and re-plan with the actual/budget ratio you measured at B1 and B2. The end of this stage (W46) is not a formal checkpoint: the next one is B3 (W50), after S11. Still do the "behind" check here with your hours log. If you are more than one week behind, stop all S10–S11 stretch now and follow the "behind between checkpoints" playbook in [schedule-and-cuts](schedule-and-cuts.md); a spine block that overruns moves the date, it is never deferred silently. The degrade items that touch S10 are #22 (Lease → the atlaspay scheduler as a single-replica Deployment with the Recreate strategy; the UNIQUE run keys stay), #21 (real Kubernetes deploy → kind only, the cloud stays Compose-on-VPS) and #24 (inventory extraction → checkout Deployment + Redis gate, with ADR-036 recording "not extracted" with numbers; it saves 4.5 h net). If #24 applies, the gRPC foundation built in 4.5 (`libs/atlas-proto`, `buf lint`/`buf breaking` in CI, the interceptors, the status mapping and the HTTP/2 load-balancing exercise) moves to the ledger in [Stage 12](stage-12-data-at-scale-fraud.md) together with its hours: the never-cut spine keeps "Kubernetes basics (probes, preStop, HPA)" and "the gRPC ledger with the load-balancing fix". The hours each item saves are in [schedule-and-cuts §7](schedule-and-cuts.md#7-cut-order-and-the-degrade-list).

**Laptop RAM.** On 16 GB, use a 2-node kind cluster, keep `atlas-labs` experiments ephemeral, and scale the flash sale down while keeping the ratio of 5 buyers per unit (document the scaling).

---

## 1. The problem this stage starts from

[Stage 09](stage-09-strangler-atlaspay-auth.md) left three measured problems.

**Business terms.**
- **Flash sales take the whole site down.** A vendor runs a limited drop: one product, 1,000 units, thousands of buyers in the first minute. Checkout traffic exhausts market's database pool, so the **catalog** also times out, and the busiest minute of the month looks like an outage.
- **Deploys are slow and risky.** Five production deployables (market, atlaspay, auth, ai, bot) plus provider-sim are rolled out with the S6 hand-written health-gated swap, one service at a time. Nothing scales with load, and every deploy depends on a script that only you understand.
- **The bot cannot scale or survive a restart gracefully.** A second replica makes Telegram answer `409 Conflict`, so there is exactly one bot process and a restart is downtime.

**Engineering terms.**
- **Compose has stopped coping.** Count the containers in your Compose stack at the end of S9 and write the number down; ADR-035 uses it as evidence. Compose has no rolling updates, no HPA, no self-healing across hosts and no network policy.
- **Connection math.** `max_connections` on pg-market is fixed, but replicas × workers × threads × pool size is not. The first time autoscaling adds pods, Postgres refuses them.
- **Hot rows.** Every flash-sale buyer touches the same `stock_levels` row. Row locks serialize them; the S2 atomic decrement keeps stock correct, but the queue behind that row holds pool connections that catalog requests need.
- **Leader-only jobs.** The atlaspay scheduler (payouts, reconciliation) is a single instance with UNIQUE run keys as a backstop. Two replicas would both try to run every period.

---

## 2. Outcomes — what exists when the stage is finished

1. **ADR-035** records why Kubernetes now, with the Compose container count.
2. **Every service runs on kind** from Kustomize overlays (`deploy/k8s/base`, `overlays/{dev,staging,prod}`), with requests and limits, readiness and liveness probes, preStop hooks, an HPA on market web, a pre-deploy migration Job, NetworkPolicy, a Beat singleton and a gateway-level rate limit.
3. **Rollouts drop 0 requests**, proven by a before/after run (N errors without preStop, 0 with it).
4. **A Lease** elects the leader of the atlaspay scheduler; killing the leader mid-period still runs each period exactly once.
5. **PgBouncer ≥ 1.24 in transaction mode** in front of pg-market, with the prepared-statement breakage reproduced (with `max_prepared_statements = 0`) and fixed and the S2 RLS behaviour re-tested.
6. **A real cloud deployment:** Terraform provisions k3s (one server, one agent); cert-manager issues TLS for `atlas.<domain>` and `pay.<domain>`; CD deploys to `atlas-staging` automatically and to `atlas-prod` with approval, runs the migration Job and smoke tests, and rolls back automatically when smoke fails.
7. **ADR-036** with flash-sale numbers measured in three configurations before any extraction, each as a ported split-gate run on kind (5 runs for the final pair), the counter-argument answered and the revert thresholds stated.
8. **`libs/atlas-proto`** with `buf lint` and `buf breaking` in CI, and **`atlas.inventory.v1.InventoryService`** (Reserve, Commit, Release, BatchGetStock, WatchStock) on `grpc.aio` with deadlines, status mapping and interceptors. inventory is the first publisher of `stock.changed`, and market's catalog consumes it.
9. **The HTTP/2 load-balancing trap reproduced and fixed**, with a per-pod spread table after scaling 1 → 4.
10. **The flash sale holds:** 1 SKU, 1,000 units, 5,000 users, exactly 1,000 sold, with a Redis gate, holds with TTLs, fencing tokens checked in Postgres and a SKIP LOCKED sweeper.
11. **The bot runs N replicas on a webhook** with a secret token, Redis FSM storage, a per-chat lock and `update_id` dedup; auth verifies the Telegram Login Widget.
12. **The product-page waterfall measured**: call count and p95 of the product page composed through market REST once inventory is extracted, for ADR-037 v1 and for S11's BFF to beat.
13. **Documents:** ADR-035, ADR-036, ADR-037 (transport decision record v1; v2 is finalised in S11 with GraphQL numbers), evidence under `docs/evidence/s10/`, two STAR stories and a postmortem paragraph.

---

## 3. Architecture at the end of the stage

```
                                         Internet
                                            |
                      Gateway (Traefik or Envoy Gateway) + cert-manager TLS + edge rate limit
        routes by host: pay.<domain> -> atlaspay as a whole; atlas.<domain> -> the path routes below
   /api/v1,/admin   /api/v1/checkout*   pay.<domain>/*      /oauth2,/.well-known   /v1/assistant,/mcp   /telegram/webhook
        |                 |                    |                     |                    |                   |
  +------------+  +----------------+  +------------------+   +-------------+       +-----------+     +---------------+
  | market-web |  | market-checkout|  | atlaspay-api     |   | auth        |       | ai        |     | bot x N       |
  | HPA 2..5   |  | own DB pool    |  | dispatchers      |   | (JWKS,      |       |           |     | webhook,      |
  +------------+  +----------------+  | scheduler x2 ----+-- Lease (leader) |       +-----------+     | RedisStorage, |
  market-worker, market-beat (1, Recreate),| relay         |   +-------------+                         | chat locks,   |
  market-relay, market-consumers      +------------------+                                           | update dedup  |
        |                 |                    |                                                     +---------------+
        |   gRPC: dns:///<inventory headless Service>, round_robin, deadlines, service-token metadata
        |                 v
        |       +----------------------+        +--------------------------------------------+
        |       | inventory-0..3       |------> | pg-inventory (truth: levels, movements,     |
        |       | grpc.aio,            |        | reservations + fence tokens)                |
        |       | max_connection_age   |------> | redis-state: gate counter, holds (hold:)    |
        |       +----------------------+        +--------------------------------------------+
        v
  PgBouncer (transaction mode) ---> pg-market (+replica)
  atlaspay pods --->  pg-atlaspay   (NetworkPolicy: only pods labelled as atlaspay may connect)

  Namespaces: atlas-dev (kind), atlas-staging + atlas-prod (k3s: 1 server + 1 agent, provisioned by Terraform), atlas-labs
  Cluster state: only from git (Kustomize for our services, Helm for third-party charts); secrets via ESO or Vault Agent
```

**What changed and why.**
- **One Deployment per process type, not per service.** market's web, worker, beat, relay and consumers were already process types of one image (S4). Kubernetes makes that explicit: each gets its own replica count, resources and probes.
- **`market-checkout` is a separate Deployment of the market image** with its own database pool. It exists because a flash sale must be able to saturate checkout without touching the catalog. It is measured before inventory is extracted.
- **inventory is a new deployable with its own database.** E2 allows a physical DB split where the forcing problem is at the database level; here it is contention on hot stock rows. market reaches inventory only over gRPC, and learns about stock changes from `stock.changed`, which inventory is the first to publish.
- **The gateway routes by host.** `pay.<domain>` goes to atlaspay as a whole (public API, payment links, provider callbacks); `atlas.<domain>` routes by path to market, auth, ai and the bot webhook.
- **A headless Service for inventory**, because gRPC load balancing has to happen in the client (4.5).
- **PgBouncer** sits between market's many pods and pg-market, so the number of Postgres connections no longer grows with the HPA.
- **The bot receives updates by webhook**, because long polling allows only one consumer.
- **The atlaspay scheduler runs two replicas** and one of them holds a Lease; the UNIQUE run keys from S4/S5 stay as the backstop.

---

## 4. Build plan

**Sequencing.** Blocks are listed in the design's order, but ADR-036 needs flash-sale numbers from the monolith **before** you extract inventory, so part of 4.6 comes before 4.5. A workable order:

| Week | Work |
|---|---|
| W43 | 4.1 Kubernetes on kind, part 1 (ADR-035, manifests, gateway, secrets, resources, probes, preStop) |
| W44 | 4.1 part 2 (HPA, `rollout undo`, the migration Job, NetworkPolicy, Beat singleton, edge rate limit); 4.3 PgBouncer; 4.2 Lease |
| W45 | 4.4 real deploy on k3s; 4.6 steps 1–2 (flash-sale harness, Redis gate) and 4.5 step 1 (ported split gate, the three configurations, ADR-036); SD14 |
| W46 | 4.5 steps 2–8 (proto, service, deadlines, data move, the load-balancing trap, the product-page waterfall); 4.6 steps 3–5 (holds, fencing, exactly 1,000); 4.7 bot; SD12; stage-end hours check |

Rollouts under load, `terraform apply`/`destroy`, the flash sale, the split-gate runs and the load-balancing measurements need uninterrupted state: they belong to the weekend block.

### 4.1 Kubernetes — 14 h [must]

Suggested split: manifests, gateway and secrets 4 h; resources, OOMKill and probes 2 h; preStop 2 h; HPA 1.5 h; `rollout undo` and the migration Job 1.5 h; NetworkPolicy 1 h; Beat singleton and edge rate limit 1.5 h; ADR-035 0.5 h.

**What to build.**
- **ADR-035 first.** Record the Compose container count at the end of S9, what Compose cannot do that you now need (rolling updates, HPA, self-healing, network policy, declarative state), and the counter-argument (see §8). P8 D127–D132 asked for the same list; this time it is your own system.
- **Manifests.** Kustomize for Atlas's own services: `deploy/k8s/base` plus `overlays/{dev,staging,prod}`. Helm only for third-party charts (the gateway, cert-manager, External Secrets, metrics-server on kind). Use Kustomize's `configMapGenerator` so a config change produces a new name and therefore a new ReplicaSet; ask yourself what `rollout undo` does to a config change without it.
- **Gateway.** Traefik (k3s ships it by default) or Envoy Gateway, using Gateway API routes, routed by host (`atlas.<domain>`, `pay.<domain>`). Gateway API does not work out of the box on k3s: the packaged Traefik has its Kubernetes Gateway provider off until a HelmChartConfig sets `providers.kubernetesGateway.enabled: true`, and you must install the Gateway API CRDs at the version that Traefik supports ([k3s networking docs](https://docs.k3s.io/networking/networking-services)). On kind, install the CRDs and your gateway chart yourself. Keep both under git (Helm values). Otherwise your HTTPRoutes are silently ignored. Not ingress-nginx: it is retired [C].
- **Secrets.** External Secrets Operator or Vault Agent, reading the Vault paths from S9. Write the trade-off into ADR-035: ESO materialises a Kubernetes Secret (stored in etcd; check whether etcd encryption at rest is on), whereas the Vault Agent injector keeps secrets in the pod's memory.
- **Stateful stores.** Decide in ADR-035 whether Postgres, Valkey, RabbitMQ and Mongo run inside the cluster (simple StatefulSets or third-party charts, no operators) or stay outside it, and how the S6 PITR backups and the nightly restore-verify keep working either way.
- **Resources.** Every container has CPU and memory requests and limits. Start from the numbers your S6 dashboards show, not guesses.
- **Probes.** A **readiness** probe says "send me traffic"; failing it removes the pod from the Service endpoints. A **liveness** probe says "I am stuck, restart me"; failing it kills the container. A **startup** probe protects slow starters from liveness. Liveness must check only the process itself, never shared dependencies.
- **preStop + termination grace period** (the core zero-downtime lesson, see the PAIN-FIRST below).
- **HPA** on market web, CPU-based, 2 → 5 → 2 under locust. Install metrics-server on kind (k3s ships it).
- **`kubectl rollout undo`** on a deliberately bad image.
- **Migrations as a pre-deploy Job**, expand-only: the Job runs with the `<svc>_migrator` role and the new image before the Deployment changes; CD waits for it to complete; contract migrations ship in a later release (the S6 rule, now enforced by the pipeline). Ask yourself: what happens if two migration Jobs run at once because a CD run was retried?
- **NetworkPolicy:** default-deny ingress in each namespace, then allow rules. The atlaspay database accepts connections only from atlaspay pods (and its migration Job). Check that your CNI actually enforces NetworkPolicy: k3s ships a policy controller, and kind ≥ v0.24 enforces NetworkPolicy with its default CNI (kindnetd, through kube-network-policies) [C]. Still prove enforcement with the denial test: a policy on a CNI that ignores it is silently a no-op.
- **Beat singleton:** market-beat runs one replica with the **Recreate** strategy. A rolling update would briefly run two Beats and fire every due task twice; Recreate accepts a short gap instead. The S4 UNIQUE run keys stay as the backstop.
- **Gateway-level rate-limit middleware** (the E10 edge row: per IP, and for API callers on `pay.<domain>` per API-key prefix, the non-secret lookup prefix parsed from `Authorization: Bearer sk_…` (S9), never the full key; 429 JSON). Traefik's OSS RateLimit middleware is a token bucket, and it counts per Traefik replica unless its `redis` option is configured; Envoy Gateway's global rate limit uses Redis [C] ([Traefik RateLimit docs](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/ratelimit/)). With two gateway replicas and per-replica counters the effective limit doubles: you have seen that before, in S1. Record which mode you run and why.

**PAIN-FIRST.**
1. **OOMKill.** Set the memory limit of `market-worker` below the peak of a CSV import. Run the import and watch the pod get OOMKilled (exit code 137) and restart. Read it in `kubectl describe` and record it in `docs/evidence/s10/oomkill.md`, then set the limit from the measured peak.
2. **Liveness that checks the database.** Make market's liveness probe query Postgres, then stop Postgres for a minute. Watch every market pod restart in a loop, so the outage is now a restart storm as well. Record it, then split the probes correctly and repeat: pods go unready, nobody restarts, and they come back when Postgres does.
3. **Rolling update without preStop.** Run locust against market web and roll out a new image. Count the failed requests (connection refused, 502 or 503 from the gateway). Then add a preStop pause and graceful shutdown and repeat until the count is 0. Record both numbers in `docs/evidence/s10/prestop.csv`.

Why the errors happen, and why readiness does not prevent them:

```
t=0      pod marked Terminating
         ├─ EndpointSlice updated: pod removed ──▶ kube-proxy and the gateway update on their own schedule
         └─ kubelet runs preStop (pause S seconds)     ◀── requests still arriving here are served normally
t=S      kubelet sends SIGTERM ──▶ app stops accepting, drains in-flight requests (graceful timeout D)
t=S+D    process exits
t=G      terminationGracePeriodSeconds reached: SIGKILL if still alive          so you need  G > S + D
```

  Removal from the endpoints and SIGTERM start at roughly the same time, and the routing layers learn about the removal a moment later. Readiness cannot help: the pod is already being removed; the problem is how long the rest of the cluster takes to notice. preStop buys that time. Two things to check: the grace period **includes** the preStop time, and your process must actually receive SIGTERM (if the container starts through `sh -c`, the shell gets the signal, not gunicorn). If your runtime image has no `sleep` binary, use the built-in `lifecycle.preStop.sleep.seconds` action (GA in Kubernetes 1.34, beta and on by default since 1.30) [C].
4. **HPA.** Drive market web with locust until it scales 2 → 5, then stop. Record the timings. Ask yourself why scale-down takes about five minutes (look up the HPA scale-down stabilization window).

**Acceptance criteria.** All services run on kind from `kustomize build`; the OOMKill, restart-storm and preStop evidence exists; a rollout under locust shows 0 failed requests; HPA scaled 2 → 5 → 2; a bad image was rolled back with `rollout undo`; the migration Job runs before the rollout and a contract migration is refused by review; a pod without the atlaspay label cannot reach pg-atlaspay; Beat never runs twice during a rollout; a burst above the gateway limit gets a JSON 429, and per-replica vs global counting is recorded.

### 4.2 Lease — 2 h [must]

**What to build.** Leader election for the atlaspay scheduler (reconciliation and payouts) with a Kubernetes **Lease**, an object in the `coordination.k8s.io/v1` API that records who holds leadership and until when. Its shape:

```
kind: Lease            # coordination.k8s.io/v1
spec:
  holderIdentity: atlaspay-scheduler-<pod>
  leaseDurationSeconds: 15
  acquireTime / renewTime / leaseTransitions
```

- Two scheduler replicas. The holder renews periodically; a candidate takes over only after the lease has gone unrenewed for its duration. Updates use optimistic concurrency (the object's `resourceVersion`), so two candidates cannot both win the same update: the loser gets a conflict.
- Do not compare `renewTime` with your own wall clock (the nodes' clocks may disagree). Measure how long **you** have observed the lease unchanged, using a local monotonic clock.
- A ServiceAccount with a Role that allows get/create/update on leases in its own namespace only.
- The UNIQUE run key per (job, period) from S4/S5 stays. A Lease can have two holders for a moment (a paused process that has not noticed it lost the lease), and the database constraint is what makes that harmless.
- Question to answer in your notes: could `leaseTransitions` serve as a fencing token? What would you have to store and compare, and where? (You build real fencing tokens in 4.6.)

**PAIN-FIRST** (Proj28 D175–D178 did this with a Raft cluster). With short periods (for example one minute) in `atlas-labs`: kill the leader pod with no grace period in the middle of a period, several times. Observe the gap before the other replica takes over, and check that each period ran exactly once: never zero, never two. Then remove the UNIQUE run key in a scratch branch, pause the leader with SIGSTOP past its lease, resume it and watch a period run twice. Record `docs/evidence/s10/lease-kill.md`.

**Acceptance criteria.** The exactly-once test passes with the backstop in place; the red run without the backstop is recorded; the ServiceAccount can touch nothing but leases in its namespace.

### 4.3 PgBouncer — 3 h [must]

**What to build.** PgBouncer ≥ 1.24 in **transaction mode** in front of pg-market. In transaction mode a client gets a real server connection only for the length of one transaction, then the connection goes back to the pool, so thousands of client connections share a few dozen server connections.

**PAIN-FIRST.**
1. Compute the connection demand before touching anything: HPA maximum × gunicorn workers × threads (each with a persistent connection), plus Celery workers, the relay and the consumers, plus market-checkout. Compare with `max_connections`.
2. Drive the HPA to 5 under locust. Observe Postgres refusing new connections (`FATAL: sorry, too many clients already`) and the errors it causes. Record the arithmetic and the error count in `docs/evidence/s10/pgbouncer.md`. Raising `max_connections` to 500 is the named wrong answer (P8): each Postgres connection is a process with its own memory.
3. Put PgBouncer in transaction mode in front and repeat. Watch `SHOW POOLS` under load (clients waiting vs server connections in use).
4. Prepared statements. Current PgBouncer (≥ 1.24) supports protocol-level prepared statements by default (`max_prepared_statements = 200`; it was 0, off, up to 1.23) ([PgBouncer changelog](https://www.pgbouncer.org/changelog.html)). To see the breakage the old default caused, first set `max_prepared_statements = 0`, point an asyncpg-based service at PgBouncer and record the errors: asyncpg prepares statements and caches them per connection, and the next transaction can land on a server connection that never saw them. Then fix it either by restoring PgBouncer's support with a value you size, or by disabling the driver's caches (asyncpg's `statement_cache_size=0` and SQLAlchemy's own asyncpg-dialect cache; read the SQLAlchemy asyncpg dialect notes on PgBouncer). Measure both, and record which fix you chose and its cost. SQL-level `PREPARE`/`DEALLOCATE` is still not supported in transaction mode.

Other transaction-mode rules to check against your code (write the result of each check down):
- **`SET` vs `SET LOCAL` + RLS.** Re-run the S2 leak test through PgBouncer. A plain `SET app.vendor_id` now leaks the vendor to **a different client**, possibly on another pod, not just to the next request on the same Django connection. `SET LOCAL` inside the request's transaction is safe; confirm that `vendor_context()` always runs inside a transaction (outside one, `SET LOCAL` does nothing and RLS sees no vendor).
- **Advisory locks.** Session-level advisory locks break; transaction-level ones (`pg_try_advisory_xact_lock`, which S5's payouts use) are fine. Check every advisory lock in the codebase.
- **Server-side cursors.** Django's `.iterator()` uses server-side cursors that can outlive a transaction; Django's documentation says to set `DISABLE_SERVER_SIDE_CURSORS` when using transaction pooling. Check your import and export paths.
- `LISTEN/NOTIFY` and anything else that relies on session state.
- Vault's dynamic credentials (S9) create database users PgBouncer does not know. If atlaspay goes through PgBouncer, how does PgBouncer authenticate them? Decide whether atlaspay needs PgBouncer at all and write down why.

**Acceptance criteria.** HPA at 5 with 0 connection errors behind PgBouncer; the prepared-statement breakage reproduced and fixed; the RLS test passes through PgBouncer with `SET LOCAL` and demonstrably fails with `SET`; the pool sizes are derived from the arithmetic, not guessed.

### 4.4 Real deploy — 5 h [must]

**What to build.**
- **Terraform** provisions k3s: one server and one agent VM, the firewall, DNS records (`atlas.`, `pay.` and their staging variants) and the bucket (reusing the S6 remote locked state). k3s is installed through cloud-init. The kubeconfig never lands in the repository.
- **cert-manager** with a Let's Encrypt issuer through the gateway. Its Gateway API support is off by default: enable it (`config.enableGatewayAPI=true`, or `gatewayAPI.enabled` on v1.21+), and install the Gateway API CRDs before cert-manager starts (or restart it after), otherwise certificates for your Gateway listeners are never issued ([cert-manager Gateway docs](https://cert-manager.io/docs/usage/gateway/)) [C as of 2026-09]. Use the Let's Encrypt **staging** environment while iterating; the production environment has rate limits you can hit in an afternoon.
- **CD** from GHCR images tagged by SHA: automatic deploy to `atlas-staging`, deploy to `atlas-prod` through a GitHub environment with approval, the **same SHA** in both. Each deploy runs the migration Job, waits for the rollout, runs the smoke tests and runs **`rollout undo` automatically when smoke fails**. The undo does not undo the migration; that is exactly why migrations are expand-only.
- **A scoped deploy ServiceAccount:** the CI credential may update Deployments, create Jobs and read pods in `atlas-staging` and `atlas-prod`, and nothing cluster-wide. No cluster-admin kubeconfig in GitHub secrets.
- Keep cloud spend under the $50 cap: `terraform destroy` when idle, and `apply` again for the weekend block.

**PAIN-FIRST.** Push an image to staging whose smoke test fails (for example a broken route). Watch CD roll it out, run smoke, fail and undo on its own. Record the timeline (deploy start, first failed smoke, undo complete, how many user requests failed in between) in `docs/evidence/s10/auto-rollback.md`.

**Acceptance criteria.** A public HTTPS staging URL on k3s; prod deployed with approval from the same SHA; the automatic rollback exercised; the deploy ServiceAccount denied a cluster-scoped action in a test.

### 4.5 gRPC inventory — 13 h [must]

Suggested split: the ported split gate, the three measurements and ADR-036 4 h; proto and buf 1 h; service 3 h; deadlines, status codes and interceptors 1.5 h; the load-balancing trap 1.5 h; data move, contract and the extracted-service run 1.5 h; the product-page waterfall 0.5 h.

**Step 1 — measure before extracting (ADR-036).** ADR-036 must record, **before** any extraction, three configurations under the same flash sale, each run as a **ported split-gate run**:
1. **The monolith as it is:** checkout p95/p99, catalog p95 during the sale, DB pool saturation, lock waits on the stock row, errors, units sold.
2. **With the Redis gate** (4.6 step 2) inside market's inventory module.
3. **With a separate `market-checkout` Deployment** that has its own pool, so a sale can saturate checkout without starving catalog.

First port `bench/split-gate` to kind: its mid-run deploy becomes a `kubectl rollout` with the migration Job, and this stage's forcing load is the flash sale (the harness from 4.6 step 1). ADR-002 protocol: 5 runs for configurations 1 and 3 (the before/after pair the extraction decision rests on) and 3 runs for configuration 2. locust shapes the traffic; the reported percentiles come from a constant-rate oha probe (`--latency-correction -q`) on checkout and on one catalog endpoint, cross-checked against the server-side histograms.

**This step contains about 145 min of unattended benchmark time (13 runs × ~11 min). Schedule it in the weekend block.**

Then decide. The ADR must answer the counter-argument: "**reservation + order in one local transaction is the oversell-proof shape; extraction turns checkout into a saga with compensations**", and it must state **which numbers would make you revert the split**. If configuration 3 already meets the SLOs, the honest ADR says "not extracted", which is degrade item #24, a legitimate outcome.

**Step 2 — `libs/atlas-proto`.** `buf.yaml` v2; `buf lint` with the STANDARD rules; `buf breaking --against '.git#branch=main'` (the default category is FILE). When you remove a field, `reserve` its number and name so nobody reuses them: reusing a field number silently reinterprets old bytes. Generate Python stubs into a package the services depend on by version. The interface:

```
service InventoryService {           // package atlas.inventory.v1
  rpc Reserve(ReserveRequest) returns (ReserveResponse);
  rpc Commit(CommitRequest) returns (CommitResponse);
  rpc Release(ReleaseRequest) returns (ReleaseResponse);
  rpc BatchGetStock(BatchGetStockRequest) returns (BatchGetStockResponse);
  rpc WatchStock(WatchStockRequest) returns (stream StockEvent); }  // server streaming
```

**Step 3 — the service.** `grpc.aio` with async SQLAlchemy on pg-inventory and async Redis on the same event loop. Reserve, Commit and Release carry a caller-generated id, so a retry after an unknown outcome cannot reserve twice (the lesson from S9: a timeout does not tell you what happened). It publishes `stock.changed` through its own outbox (this is the event's first publisher) and consumes `order.cancelled` to release holds. market's catalog consumes `stock.changed` for the "in stock" flag on listings and search and for the product-page cache, never for checkout decisions (ADR-010). WatchStock streams changes for a set of SKUs (edge will consume it in [Stage 11](stage-11-realtime-edge-graphql.md)).

**How checkout changes.** In the monolith, reservation and order creation were one local transaction. Now inventory is remote:

```
market-checkout                          inventory
  |── Reserve(id, sku, qty, deadline) ──▶| gate, hold with TTL, fence token
  |◀── ok (hold id, token) ──────────────|
  | BEGIN; create order + groups + outbox; COMMIT     (if this fails ─▶ Release(id) as compensation)
  | ... payment succeeds (webhook) ...
  |── Commit(id, token, deadline) ───────▶| token still valid? ─▶ sold
  | order.cancelled / payment failed ─────▶ Release ; hold TTL + sweeper is the safety net if Release is lost
```

**Step 4 — deadlines and status codes.** market sets a deadline from the **remaining** request budget (minus a margin), never a fixed number, and inventory passes what is left down to its database calls (check `time_remaining()` in the server context against your statement timeout). Status mapping:

| Situation | Status | What the client does |
|---|---|---|
| Out of stock / sold out at the gate | `FAILED_PRECONDITION` | Do not retry; answer 409 |
| Contention (lock timeout, serialization failure) | `ABORTED` | Retry the whole operation with the same id, jittered |
| Budget exhausted | `DEADLINE_EXCEEDED` | Outcome unknown: retry with the same id or query, never with a new id |
| Pod going away, no connection | `UNAVAILABLE` | Retry with backoff |
| Bad input | `INVALID_ARGUMENT` | Do not retry; it is a bug |

**Step 5 — interceptors and health.**
- A **service-token** interceptor: the client attaches its client-credentials JWT from auth (S9) as metadata; the server verifies it through JWKS and checks `aud = inventory` and the scope. This is the E5 row for S10: write a cross-service denial test (for example the bot's token is refused).
- OTel and structured logging interceptors, so one checkout trace crosses HTTP and gRPC.
- A client interceptor that **refuses to send an RPC without a deadline**, so the invariant is enforced, not hoped for.
- The gRPC health service plus Kubernetes' native gRPC probes.

**Step 6 — move the data.** Reuse the S9 cutover runbook, abbreviated: replicate the `inventory_*` tables to pg-inventory, a short write freeze, switch market's `InventoryGateway` from the in-process module to the gRPC client behind a flag, verify, contract. The exit criterion is the flash-sale test (exactly 1,000 sold) against the service plus a stock reconciliation (Σ movements = levels) on pg-inventory. Then run the ported split gate against the extracted service (5 runs, about 55 min unattended, weekend block) for ADR-036's last row.

**Step 7 — the HTTP/2 load-balancing trap.** gRPC runs on HTTP/2, which multiplexes every call over **one long-lived connection**. A normal (ClusterIP) Service is balanced by kube-proxy at L4, which chooses a pod **once per connection**. So all RPCs from one market pod go to one inventory pod, forever.

```
ClusterIP Service (the trap)                     The three-part fix
market pod                                       market pod
  channel ── one HTTP/2 connection ──┐             channel: dns:///<headless Service>, round_robin
  kube-proxy picks a pod per          │               ├── conn ──▶ inventory-0
  connection, once                     ▼               ├── conn ──▶ inventory-1
                                 inventory-0           ├── conn ──▶ inventory-2
                          inventory-1..3 idle          └── conn ──▶ inventory-3
                                                   server max_connection_age ─▶ GOAWAY ─▶ client re-resolves DNS
```

The fix has three parts, and each covers a different gap:
1. **A headless Service** (`clusterIP: None`): DNS returns the IP of every **ready** pod instead of one virtual IP.
2. **A `dns:///…` target with `round_robin`** in the client's service config (`loadBalancingConfig`): the client opens a connection per resolved address and spreads calls across them. The default policy (`pick_first`) would use only one address.
3. **Server-side `max_connection_age`**: the server periodically closes connections gracefully (GOAWAY), which makes clients re-resolve DNS and discover pods that were added after they started.

The Python setup [C]: the channel target is `dns:///<svc>.<ns>.svc.cluster.local:<port>` and the channel option `grpc.service_config` carries a service config whose `loadBalancingConfig` selects `round_robin`; on the server, the options `grpc.max_connection_age_ms` and `grpc.max_connection_age_grace_ms` set the age and the grace period. Check the names against the [gRPC core channel-argument keys](https://grpc.github.io/grpc/core/group__grpc__arg__keys.html) and the gRPC name-resolution and load-balancing docs.

**PAIN-FIRST.** Scale inventory 1 → 4 while market sends steady Reserve/BatchGetStock traffic, and record the share of RPCs per pod over a few minutes for each variant:

| Variant | pod-0 | pod-1 | pod-2 | pod-3 | Time to spread after scale-up |
|---|---|---|---|---|---|
| ClusterIP, defaults | | | | | |
| ClusterIP + `max_connection_age` only | | | | | |
| Headless + `round_robin`, no max age | | | | | |
| All three | | | | | |

Before you measure, predict each row and commit the prediction (the empty table with your guesses, in `docs/evidence/s10/grpc-spread.md`, before the first run). Count calls with a per-pod counter from your server interceptor (a pod label is bounded cardinality). Also check what `max_connection_age` does to a long-running `WatchStock` stream, and make the client resume. Record the measured table next to your prediction; it is your first STAR story. (Check your prediction in §16.)

**Step 8 — the product-page waterfall (for ADR-037 v1 and S11).** With inventory extracted, load one product page the way the storefront does today: one REST call after another to market for everything the page shows (product, vendor, stock, reviews and whatever else your page needs). Count the calls and measure the page's p95 under ADR-002, with a constant-rate probe that replays the call sequence. Record `docs/evidence/s10/product-page-waterfall.csv`. You do not fix it here: S11's BFF is measured against this number.

**Acceptance criteria.** ADR-036 has all three measurement rows (ported split-gate runs, 5 runs for the final pair), the extracted-service row and revert thresholds; `buf breaking` fails a PR that renumbers a field; every RPC carries a deadline no longer than the caller's remaining budget; the status mapping is tested per row; the spread table shows an even split with all three parts; a checkout trace spans market → inventory; market's catalog updates its "in stock" flag from `stock.changed`; the product-page waterfall (call count, p95) is recorded.

### 4.6 Flash sale — 4 h [must]

This is SD12 (ticket booking) built for real, scaled up from the S2 locked decrement.

**Step 1 — harness.** One SKU, 1,000 units, 5,000 users (locust driven by worldgen traffic mode shapes the load; the reported percentiles come from the constant-rate oha probe, as in 4.5 step 1), a fixed ramp and the ADR-002 protocol. Measure: units sold, checkout p95/p99, catalog p95 **during** the sale, DB pool saturation and lock waits on the stock row. Run it against the monolith first (feeds ADR-036).

**Step 2 — the Redis gate.** A Lua script that decrements a per-SKU counter in redis-state only if it is positive. A buyer who fails the gate gets "sold out" in a millisecond, without touching Postgres. The gate is an **admission filter, not the truth**: Postgres keeps the stock CHECK and the atomic decrement from S2. The gate may under-admit; it must never be the only thing preventing oversell. Decide what happens to the gate count when a hold expires.

**Step 3 — holds with TTLs and fencing tokens checked in Postgres.** A hold reserves units for one buyer until it expires. Each hold grant gets a **fencing token**: a number that only ever increases, issued by the grant authority (for example in the same Lua script as the gate). Commit sends the token, and **Postgres**, inside the commit transaction, accepts it only if it is still the valid token for that hold. The storage that performs the write decides whether the holder is still the holder, because a client can pause for any length of time between checking and writing.

```
worker A                        Redis (gate, holds)                 Postgres (truth)
  |── gate: admitted, token 41, hold TTL 10 s (short, for the lab)
  | (SIGSTOP for 20 s) ...
                                   hold 41 expires
  sweeper (SKIP LOCKED) releases hold 41 in Postgres, returns the unit to the gate
worker B |── gate: admitted, token 42 ───────────────────────────────▶ Commit(42): valid ─▶ sold
worker A | (SIGCONT) ── Commit(41) ───────────────────────────────────▶ without fencing: accepted (two holders)
                                                                       with fencing:    rejected, token 41 is stale
```

**PAIN-FIRST.**
1. Implement the naive commit first: it trusts that "my hold existed when I checked".
2. Configure a short hold TTL in `atlas-labs`, start a buyer's checkout, SIGSTOP that worker past the TTL, let the sweeper release the hold and another buyer take and commit the units, then SIGCONT the first worker. Observe **two holders commit**: 1,001 units sold, or two orders for the same units. Record it in `docs/evidence/s10/fencing.md`; it is your second STAR story.
3. Ask yourself why the S2 `CHECK (stock ≥ 0)` did not save you. (Hint: with hundreds of other holds outstanding, the aggregate counters are nowhere near zero.)
4. Add the fencing check in Postgres and repeat: the stale commit is rejected and the buyer gets a clean error.
5. Question: does a status column you compare-and-set give you the same protection? Only if a hold can never return to "held" for someone else. Can your design ever re-grant the same reservation row?

The S3 notes named Redlock with its fencing caveat; this is that caveat, reproduced.

**Step 4 — the sweeper.** A `FOR UPDATE SKIP LOCKED` sweeper (the S4 hold-expiry sweeper, reused) releases expired holds in batches and returns units to the gate. Run it with 1 and with 2 replicas and confirm no hold is released twice.

**Step 5 — exactly 1,000.** Run the full sale against the gRPC inventory with the SIGSTOP chaos switched on for a sample of workers.

**Acceptance criteria.** Exactly 1,000 units sold: committed reservations = 1,000, stock 0, Σ movements consistent, no negative counter; the red run without fencing is recorded; catalog p95 during the sale stays within its SLO; the flash-sale test runs in CI (scaled down).

### 4.7 Bot in Kubernetes + Telegram login — 3 h [must]

**What to build.**
- **Long polling allows only one consumer.** With polling, the bot asks Telegram for updates with `getUpdates`. Telegram serves one poller per bot: a second one gets `409 Conflict: terminated by other getUpdates request; make sure that only one bot instance is running`.
- **Webhook mode.** Telegram POSTs each update to your HTTPS URL. With N replicas behind the gateway, any replica can take any update. Use aiogram's `SimpleRequestHandler` with a `secret_token`; Telegram sends it back in the `X-Telegram-Bot-Api-Secret-Token` header on every delivery. Serve on port 443 (Telegram allows 443, 80, 88 and 8443). Avoid `TokenBasedRequestHandler`: it puts the bot token in the URL.
- **Set the webhook once per deploy** (a CD step or a one-off Job), not from every replica at startup. Tune `max_connections` from its default of 40. Keep a **separate bot token for development**: once a webhook is set, `getUpdates` fails, and calling `deleteWebhook` from your laptop against the production token would silently take production off its webhook.
- **FSM storage.** `RedisStorage` with TTLs (prefix `fsm`, as in S3).
- **Concurrency across pods.** Telegram can deliver several updates at once (up to `max_connections`), and the Service spreads them across pods, so two quick taps from the same user can run in parallel on different pods and race on the same FSM state. Add:
  - a **per-chat lock middleware** in redis-state (prefix `lock:`): acquire with a random token and an expiry; release with a compare-and-delete that removes the key only if it still holds **your** token (otherwise you could delete a lock someone else acquired after yours expired);
  - **`update_id` dedup** with `SET NX EX` (prefix `bot:`). Telegram retries a delivery that did not get a 2xx in time, and your own retries and network-level redeliveries can replay an update too, so the same update can arrive twice.
  - **When does Telegram get its 200?** `SimpleRequestHandler` defaults to `handle_in_background=True` [C] ([aiogram webhook docs](https://docs.aiogram.dev/en/latest/dispatcher/webhook.html)): Telegram gets 200 before your handler runs, so it will not redeliver an update whose handler failed. Duplicates are then rare; the real risk flips to **losing** updates, through exceptions and through SIGTERM during processing. Either drain background tasks in graceful shutdown (preStop plus grace period, as in 4.1), or switch to `False` and accept Telegram's retries. Record the choice and why in the bot README.
- **Do not trust the leftmost `X-Forwarded-For`** behind the gateway: a client can send its own header, and proxies append to it, so the leftmost value is whatever the caller wrote. aiogram's IP filter reads the leftmost value. Rely on the secret token.
- **Telegram Login Widget verification in auth** (`/telegram/login`). This is an external protocol contract, a requirement you cannot invent; the source is Telegram's [Login Widget docs, "Checking authorization"](https://core.telegram.org/widgets/login#checking-authorization). In short: build the data-check string from the received fields (every field except `hash`, sorted by key, `key=value` lines joined by newlines), compute HMAC-SHA256 over it with a key equal to SHA-256(bot token), compare with `hash` in constant time, and reject a stale `auth_date`. Turn the official page into a table of test cases first (valid, forged hash, missing field, stale `auth_date`), then write the code against it. Then link the Telegram id to an auth user with the S9 account-linking rules. (The Mini App `initData` check in S11 uses a different key derivation; do not mix them up.)

```
Polling, 2 replicas                              Webhook, N replicas
bot-0 ── getUpdates ──▶ Telegram                 Telegram ── HTTPS POST + secret header ──▶ Gateway :443 ──▶ Service
bot-1 ── getUpdates ──▶ 409 Conflict                       (up to max_connections at once)        ├──▶ bot-0
                                                                                                  ├──▶ bot-1
                                                                                                  └──▶ bot-N
```

**PAIN-FIRST.**
1. Run the polling bot with `replicas: 2` on kind. Watch the `409 Conflict` in the logs and count missed updates. Record it.
2. Switch to webhooks, then deliberately configure `MemoryStorage` with 2 replicas and walk through "track my order". Observe the conversation break when consecutive updates land on different pods (a different failure from the restart loss you saw in S3). Move back to `RedisStorage`.
3. With `RedisStorage` but **no** lock, fire two `Dispatcher.feed_raw_update()` calls for the same chat concurrently against real Redis and show the FSM race. Add the lock and dedup; the same test passes.

For local testing, drive the webhook with the fake Bot API from `atlas-testkit` (S4); real Telegram only talks to the k3s staging URL.

**Acceptance criteria.** The bot answers on its webhook with N ≥ 2 replicas; a request without the right secret header is rejected; a duplicate `update_id` has no side effect; the concurrent same-chat test passes; a rollout of the bot under a stream of fed updates loses none (or the `handle_in_background=False` choice is recorded with its retry evidence); a forged Login Widget hash and a stale `auth_date` are both rejected.

### 4.8 Drills + SD14 (Lease) — 4 h [must]

The weekly drill hour over the four weeks (one SQL problem on the Atlas schema or one DSA problem, plus the week's interview questions), and SD14 (distributed job scheduler) worked against what you built in 4.2, plus the SD12 whiteboard (see §9).

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| Rollouts drop 0 requests | preStop + graceful shutdown + grace period > preStop + drain; readiness; `maxUnavailable` 0 | Rollout under locust in `kind-e2e`: failed requests = 0 |
| Exactly 1,000 units are sold | Postgres truth (CHECK, atomic decrement), Redis gate as admission, fencing check at commit, sweeper | Flash-sale concurrency test (with SIGSTOP chaos): committed = 1,000, stock = 0, Σ movements consistent |
| Every pod has requests and limits | Manifests; a namespace policy (ResourceQuota/LimitRange or an admission policy); CI check | CI fails on a container without resources in `kustomize build` output; such a pod is rejected in `atlas-staging` |
| Cluster state comes only from git | CD applies `kustomize build` output; no `kubectl edit`; scoped deploy ServiceAccount | Nightly `kubectl diff` against each overlay reports no drift |
| No breaking proto change is merged | `buf breaking` as a required check | A PR that renumbers or retypes a field fails CI (red run kept as evidence) |
| Every RPC has a deadline no longer than the caller's remaining budget | Client interceptor computes deadlines from the request budget and refuses to call without one; server checks `time_remaining()` | RPC without a deadline is refused in tests; propagated deadline ≤ remaining budget; DB timeout ≤ remaining |
| *(from 4.1)* The atlaspay DB is reachable only from atlaspay pods | NetworkPolicy on an enforcing CNI | Connection from a market pod times out; from an atlaspay pod succeeds |
| *(from 4.2)* Each scheduler period runs exactly once | Lease + UNIQUE run key | Kill-the-leader test over many periods |
| *(from 4.7)* One Telegram update is handled once | `update_id` dedup + per-chat lock | Duplicate delivery and concurrent same-chat tests |

---

## 6. Tests to write

- **Kubernetes:** readiness keeps a failing pod out of the Service; liveness does not depend on Postgres; the preStop rollout (0 errors); HPA scale-up and scale-down; migration Job runs before rollout and is safe to re-run; NetworkPolicy denial; Beat never duplicated during a rollout; a burst above the gateway limit gets a JSON 429.
- **Lease:** exactly-once under repeated leader kills; the RBAC scope of the scheduler ServiceAccount.
- **PgBouncer:** the prepared-statement case; RLS with `SET LOCAL` through the pooler and the `SET` leak; no session advisory locks or server-side cursors left.
- **gRPC:** per-method contract tests on the generated stubs; deadline propagation; status mapping per row of the table; the no-deadline refusal; service-token interceptor (cross-service denial); idempotent Reserve after `DEADLINE_EXCEEDED`; per-pod spread after scale-up (on kind, as a scripted measurement); `WatchStock` resume after a GOAWAY; market's catalog consumer for `stock.changed` (idempotent, never used by checkout).
- **Flash sale:** exactly 1,000 with chaos; the fencing red/green pair; the sweeper with 2 replicas.
- **Benchmarks (scripted, not CI):** the ported split gate on kind; the product-page waterfall probe.
- **Bot:** 409 reproduction (manual evidence); secret-header rejection; `update_id` dedup; concurrent same-chat with and without the lock; no update lost across a rollout (the background-handler drain); Telegram Login Widget valid, forged and stale.
- **Deploy:** smoke tests; the automatic rollback path; the deploy ServiceAccount denied a cluster-scoped action.

See [testing-and-ci](testing-and-ci.md) for how these fit the whole matrix.

---

## 7. CI changes

| Job | What it gates |
|---|---|
| `buf lint` / `buf breaking` | Proto style (STANDARD) and no breaking change against `main` |
| `kustomize build` + kubeconform | Every overlay renders and validates. By default kubeconform fails on a resource it has no schema for, so CRDs (Gateway API routes, ExternalSecrets) need their schemas supplied with `-schema-location` (for example the datreeio CRDs-catalog). Never add `-ignore-missing-schemas`: it turns the check into a silent skip |
| `kind-e2e` | Create a kind cluster, deploy the overlay, run the migration Job, run smoke tests and a small rollout under load |
| CD to k3s with automatic rollback | Staging on merge, prod with approval, same SHA; failed smoke → `rollout undo` |
| Flash-sale concurrency test | Exactly-once selling at a scaled-down size |
| Bot webhook tests | Secret header, dedup, per-chat lock |
| Nightly drift check | `kubectl diff` finds nothing that is not in git |

---

## 8. ADRs and documents

**ADR-035 — Kubernetes.**
- *Questions:* Why now? What exactly can Compose not do for Atlas? kind vs k3s vs managed Kubernetes; Kustomize vs Helm for your own services; which gateway and why (ingress-nginx is retired [C]; what enabling Gateway API on k3s cost you); ESO vs Vault Agent and where secrets end up; whether stateful stores live in the cluster, and how PITR and restore-verify continue; namespace layout (`atlas-dev`, `atlas-staging`, `atlas-prod`, `atlas-labs`).
- *Numbers:* the Compose container count at the end of S9; laptop RAM with the full kind cluster; failed requests during a rollout without and with preStop; HPA scale-up and scale-down times; monthly cloud cost of the k3s pair.
- *Counter-argument:* "One developer, one VPS: Compose plus the S6 health-gated swap is enough, and Kubernetes is operational overhead you will spend your time feeding." Answer with the measured gaps, and say which of them a smaller tool could close.

**ADR-036 — inventory split.**
- *Questions:* Does the flash sale still hurt after the Redis gate and after the separate checkout Deployment? What does extraction cost (a saga with compensations, a network hop, a second database)? What would make you revert?
- *Numbers:* for each of the three configurations (monolith, + Redis gate, + checkout Deployment) and then for the extracted service, each from ported split-gate runs (5 runs for the monolith, configuration 3 and the extracted service; 3 for the Redis gate): checkout p95/p99, catalog p95 during the sale, DB pool saturation, stock-row lock waits, errors, units sold; the added latency of the gRPC hop; the rate of compensations (Release) during the sale.
- *Counter-argument:* "Reservation + order in one local transaction is the oversell-proof shape; extraction turns checkout into a saga with compensations." It must also state the numbers that would revert the split. If the numbers do not hurt after configuration 3, the ADR says "not extracted".

**ADR-037 — transport decision record v1 (REST vs gRPC vs GraphQL).**
- *Questions:* which interactions use which protocol (the E4 table) and why; what gRPC costs (browser access needs grpc-web or a gateway, the load-balancing trap, tooling); what a REST contract lacks (enforced schema, deadline propagation, streaming). GraphQL has no numbers yet: write down the question it must answer for the storefront BFF. ADR-037 v2 (dated, must) in [Stage 11](stage-11-realtime-edge-graphql.md) answers it with the measured GraphQL numbers and updates the decision per interaction.
- *Numbers:* REST vs gRPC p50/p95 for the same operation (for example BatchGetStock) on the same data, hardware and concurrency, ADR-002 protocol (P9 D151–D153 made the same comparison for one ledger RPC); payload sizes; the product-page waterfall (call count and p95, 4.5 step 8), the baseline v2 compares against.
- *Counter-argument:* "REST everywhere is simpler and the latency difference is small." P9 already warned that the number is usually smaller than people expect, so the answer must rest on contracts, deadlines and streaming, not only on latency.

**Other documents:** `docs/evidence/s10/*`; the S9 cutover runbook updated with the inventory move; `docs/star/` two stories.

---

## 9. System design session

- **SD14 distributed job scheduler — built-lite** (W45). You now have all three layers: UNIQUE run keys and SKIP LOCKED workers (S4), a Beat singleton with Recreate, and Lease-based leader election for the atlaspay scheduler. Whiteboard SD14 first, then compare with Proj28's Raft-based version and with your Lease: what does each give you, and what still needs the database backstop?
- **SD12 ticket booking — built** (W46). The flash sale is SD12's hardest part: the gate, holds with expiry, fencing and abandoned-hold cleanup. Whiteboard the part you did not build: a virtual waiting room that sheds load before it reaches checkout.
- **Consensus.** The Lease is only as strong as the store behind it. kind's control plane runs etcd, which uses Raft; reread your P8 D128/D132 etcd notes and explain why the Lease update cannot be won by two candidates at once.
- **Load balancing.** Client-side gRPC balancing (this stage) vs the Nginx L7 balancing you built in S6: write one paragraph on where each decision is made.

---

## 10. Interview questions this stage lets you answer

1. Readiness vs liveness: what breaks if you conflate them, and what goes wrong if liveness checks the database?
2. What does preStop do that readiness does not?
3. Why does gRPC balance badly behind a ClusterIP Service, and what are the three parts of the fix? Why is `max_connection_age` alone not enough?
4. How do deadlines propagate through your call chain?
5. `FAILED_PRECONDITION` vs `ABORTED` vs `UNAVAILABLE`: which ones does your client retry, and why?
6. How do you evolve a protobuf message without breaking old clients?
7. Why fencing tokens? What exactly went wrong without them?
8. What breaks with PgBouncer transaction mode?
9. Why does a Telegram bot need a webhook to scale? And why is `RedisStorage` alone not enough with several replicas?
10. How do you run exactly one scheduler across replicas, and what happens if two believe they are the leader?
11. Why are migrations in a pre-deploy Job expand-only?
12. What does your NetworkPolicy protect, and what does it not protect?
13. Why did you (or did you not) extract inventory, and which numbers would make you merge it back?
14. How would you verify a Telegram Login Widget payload?

---

## 11. Common mistakes to watch for

- A liveness probe that checks the database, turning a DB blip into a restart storm; or a readiness probe that checks every dependency and takes all pods out at once.
- No preStop, a grace period shorter than preStop plus drain, or an app that never receives SIGTERM because a shell is PID 1.
- A rolling update that "worked" because nobody was sending requests (P8).
- Pods without requests, or memory limits below the real peak (OOMKill loops). Setting CPU limits without measuring the throttling they cause.
- Expecting `rollout undo` to revert a ConfigMap change or a migration.
- A contract migration in the pre-deploy Job while old pods still run.
- Two Beat pods during a rolling update.
- A ClusterIP Service for gRPC; `max_connection_age` alone; RPCs without deadlines; retrying `FAILED_PRECONDITION`; reusing a proto field number.
- Raising `max_connections` instead of pooling; `SET` instead of `SET LOCAL`; session advisory locks or server-side cursors under transaction pooling.
- Trusting a Redis lock or hold without a fencing check in the store that performs the write.
- Polling in development with the production bot token; calling `setWebhook` from every replica; trusting the leftmost `X-Forwarded-For`; putting the bot token in the URL.
- `kubectl edit` in production; a deploy credential with cluster-admin; a NetworkPolicy on a CNI that does not enforce it; the Let's Encrypt production issuer while you are still iterating.
- HTTPRoutes that nothing serves because the Gateway provider (k3s Traefik) or cert-manager's Gateway API support was never enabled; `-ignore-missing-schemas` in kubeconform, so the CRDs are never validated.
- Keying an edge rate-limit zone on the raw `Authorization` header, which keeps secret key material in the limiter's memory.
- Trusting `handle_in_background=True` without draining background handlers on SIGTERM, so a rollout silently drops updates.

---

## 12. How real companies differ

- Most teams run **managed Kubernetes** (EKS, GKE, AKS) with a **GitOps controller** (Argo CD, Flux) that pulls from git, so CI never holds cluster credentials. Your manifests are GitOps-shaped on purpose, so adding a controller later changes nothing in them.
- L7 gRPC balancing is usually done by a **service mesh** (Linkerd, Istio) or proxyless gRPC with xDS, not DNS round-robin plus connection ageing. Doing it by hand is how you learn what the mesh is doing for you.
- Production databases run on **managed services or operators** (for example CloudNativePG), not hand-written StatefulSets.
- Real flash sales put a **virtual waiting room** at the edge and pre-split inventory into buckets or tokens, so the database sees a steady trickle. Your Redis gate is the in-house version of that admission control.
- Large Telegram bots **acknowledge the webhook immediately and enqueue**, then process updates per chat in order from a partitioned queue. The per-chat lock is the small-scale version of that ordering.
- Node autoscaling (cluster autoscaler, Karpenter) adds machines; your k3s pair has a fixed two nodes, so the HPA is bounded by what they can hold.

---

## 13. Deliberately not doing

| Item | Why | When it arrives |
|---|---|---|
| Argo CD / Flux | One cluster, one developer; the manifests are already declarative and GitOps-shaped (P8 D129 read the concepts) | Named only; a real team adds it first |
| Multi-region | No latency or availability requirement that justifies it, and it doubles cost | Not in Season 1 |
| Postgres operators | Operating an operator is its own subject; simple StatefulSets or external stores are enough here | Named only |
| A service mesh | The three-part fix and JWT service tokens cover today's needs | Linkerd mTLS is a stretch below |
| Managed Kubernetes | Costs more; k3s teaches the same objects | Stretch below |
| The ledger over gRPC | The ledger has no forcing problem yet | [Stage 12](stage-12-data-at-scale-fraud.md) |
| edge consuming `WatchStock` | edge does not exist yet | [Stage 11](stage-11-realtime-edge-graphql.md) |
| Native Telegram Payments | Money would go directly to the provider and bypass AtlasPay; the payment link and the bot's pay button (S9) are the primary path | Stretch below (testkit-only spike) |
| A CDN | Nothing here serves static assets worth caching at the edge yet | [Stage 11](stage-11-realtime-edge-graphql.md), optional, for the SPA assets |

---

## 14. Stretch

Only if the must tier closes early:
- **Linkerd mTLS** [2]: mutual TLS between pods, and L7 gRPC balancing you can compare against your three-part fix.
- **Managed Kubernetes via Terraform** [2]: the same overlays on a managed cluster; compare setup time and monthly cost with k3s.
- **Native Telegram Payments spike** [2] (E6): `sendInvoice`; answer `pre_checkout_query` within 10 s with a reservation check only; import `successful_payment` as an **external charge** and reconcile it against the ledger, because the provider token routes money directly to the provider and bypasses AtlasPay's callbacks. Physical goods only: digital goods and services (for example AI-assistant credits) must be sold in Telegram Stars (`XTR`, empty `provider_token`). Run it fully against the fake Bot API in `atlas-testkit` (S4), so no provider token or merchant contract is needed; whether real Click or Payme test tokens can be obtained without a merchant contract is [U]. Once the bot's pay button (S9) is built, this is the first pick for spare hours.

---

## 15. Definition of done

- [ ] ADR-035 written with the Compose container count and the counter-argument answered
- [ ] All services run on kind from Kustomize overlays; Helm only for third-party charts
- [ ] OOMKill, liveness restart storm and preStop evidence recorded (`docs/evidence/s10/`)
- [ ] A rollout under locust drops 0 requests; HPA 2 → 5 → 2 recorded; `rollout undo` exercised
- [ ] Migration Job pre-deploy and expand-only; NetworkPolicy denial test green; Beat singleton with Recreate
- [ ] Edge rate limit: a burst above the gateway limit gets a JSON 429; per-replica vs global counting recorded; API callers limited by key prefix, never the full key
- [ ] Lease exactly-once test green, with the red run without the backstop recorded
- [ ] PgBouncer: "too many clients" reproduced, transaction mode in place, prepared-statement breakage reproduced with `max_prepared_statements = 0` and fixed, RLS re-tested
- [ ] Cloud staging URL on k3s (Terraform) for `atlas.` and `pay.`, TLS by cert-manager through Gateway API; prod with approval from the same SHA; automatic rollback exercised; scoped deploy ServiceAccount
- [ ] ADR-036 with all measurement rows from ported split-gate runs (5 runs for the final pair) and revert thresholds; ADR-037 v1 with REST vs gRPC p50/p95 and the product-page waterfall
- [ ] `libs/atlas-proto` with `buf lint` and `buf breaking` in CI; InventoryService with deadlines, status mapping and interceptors; `stock.changed` consumed by market's catalog
- [ ] The per-pod spread table filled in for all four variants, next to your committed prediction
- [ ] Flash sale: exactly 1,000 units sold; the fencing red/green pair recorded
- [ ] Bot answering on its webhook with ≥ 2 replicas; 409 recorded; lock and dedup tests green; no update lost across a rollout; Telegram Login Widget verification in auth
- [ ] Two STAR stories in `docs/star/`: **gRPC pinning to one pod**; **two holders without fencing**
- [ ] Postmortem paragraph: what Kubernetes cost you and what it bought
- [ ] Stage-end note (W46): actual vs budgeted hours per block, and which degrade items were applied (the next checkpoint is B3, W50)
- [ ] Tag `v0.10`

---

## 16. If you get stuck

**4.1 Kubernetes.** If a rollout drops requests, which happened first in the pod's events: SIGTERM or removal from the endpoints? What does your process do on SIGTERM, and is it really PID 1? If the HPA never scales, is metrics-server running and do your pods have CPU requests (the HPA computes utilisation against requests)? Reread P8 D127–D132 (DocuVault §10 and the [phase-5](../../phase-5-scaling-architecture.md) Week 22 rows D127–D129).

**4.2 Lease.** Who wins when two candidates update the Lease at the same moment, and what tells the loser? Where is the backstop if a paused leader wakes up? Reread Proj28 D175–D178 in [phase-6](../../phase-6-capstone.md) (leader-only dispatch, kill the leader mid-decision, "never zero, never two").

**4.3 PgBouncer.** For each statement your app sends, ask: does it depend on anything that outlives the transaction? Reread the PgBouncer and prepared-statement item in P8 D127–D132 (DocuVault §11a and the testing table).

**4.4 Real deploy.** Can the CI credential do anything you would not want a leaked token to do? Reread your S6 CD pipeline; only the target changed.

**4.5 gRPC.** For each variant in the spread table, how many connections does the client hold, and to which addresses? When does it resolve DNS? Reread P9 D151–D153 ([PayFlow](../python/09-payflow.md) §10a: deadlines, status mapping, REST vs gRPC) and P10 D163–D165 ([AtlasMarket](../python/10-atlasmarket.md) §5: bulkhead, why checkout was one local transaction). For the ADR-036 counter-argument, reread P10 D166 (whiteboarding multi-vendor checkout).

<details>
<summary>Check your prediction (the spread table)</summary>

`max_connection_age` alone does **not** fix it: after a reconnect through the ClusterIP, the client still holds one connection, so traffic hops between pods instead of spreading. Headless + `round_robin` without a max age spreads across the pods that existed when the client resolved, and never discovers the new ones. Only all three parts together give an even split that follows scale-up.
</details>

**4.6 Flash sale.** Draw the timeline of one hold from grant to commit, then insert a 20-second pause at every arrow. Which arrow is dangerous? Reread P1 D19–D24 ([StockPilot](../python/01-stockpilot.md) Stage 4: the naive version first, then the locked or atomic decrement) and your S2 race tests.

**4.7 Bot.** Which component retries, Telegram or you, and when? With `handle_in_background=True`, what happens to an update whose handler is still running when the pod gets SIGTERM? What does the lock protect that `RedisStorage` does not? Reread P2 §20 ([QuickServe](../python/02-quickserve-pos.md) Telegram extension, Week 7: webhook vs polling) and your S3 bot notes.
