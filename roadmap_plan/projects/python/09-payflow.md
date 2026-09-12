# Project 9 — PayFlow

**Payment processing platform: idempotency, webhooks, ledger reconciliation**

| | |
|---|---|
| Domain | FinTech |
| Level | Middle+ / Senior |
| Phase | 6 — Senior-Track Capstone |
| Weeks | 25–26 (D145–D156) |
| Stack | Python, FastAPI, PostgreSQL (**JSONB, generated columns, `ON CONFLICT`, PITR**), **HashiCorp Vault** (+ rotation, dynamic DB creds), **gRPC** to `ledger-service`, **Terraform** (cloud foundation for AtlasMarket), Prometheus/Grafana/Sentry, `locust` + **`py-spy`**, **Toxiproxy**, Redis (per-key rate limiting) |
| Repo | `payflow/` |

> **The whole point, in one sentence:** the same payment request retried by a
> flaky client must never charge twice.
>
> The second half of the project is not code at all — it is the operational
> discipline a system holding money actually needs: secrets management, a threat
> model, an SLO derived from measurements, a runbook, a live incident drill, and a
> disaster-recovery test with a verified restore.

---

## 1. Business Problem

A platform needs to accept payments, handle a provider's async webhook
confirmations reliably — a webhook can arrive twice, arrive late, or arrive
*before your own request even finishes* — and maintain a ledger that is provably
correct under retries and duplicate events.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Idempotent payment creation, implemented from scratch, keyed on
   `Idempotency-Key` **plus a request hash**
2. Signature-verified webhook intake that is itself idempotent
3. Payment status reconciled **from the webhook**, never from the API call's
   optimistic result
4. Refunds, with matching ledger entries
5. Secrets in Vault rather than `.env` — **and rotated once, live**, with a grace
   window where both signing secrets verify; the database password issued by
   Vault's **dynamic secrets** engine with a TTL
5a. The ledger call made over **gRPC** (one RPC, protobuf contract, deadline),
   alongside the REST path from LedgerBase, with latency and failure semantics compared
5b. **Per-merchant rate limiting** — a token bucket in Redis (Lua), enforced by API key
5c. A PII column (`payout_account_ref`) **encrypted at the application level** with a
   key held in Vault (envelope encryption)
6. An append-only audit log of every payment and refund state change

**Operational capability — half the value of this project**
7. `docs/threat-model.md`, `docs/pci-scope-note.md`, `docs/hipaa-considerations-note.md`
8. `docs/backup-dr-plan.md` with a **verified restore** and a reconciling trial
   balance — via `pg_dump` **and** via **PITR** (WAL archiving + `pg_basebackup`)
   to "14:03, one minute before the bad write"
8a. The cloud account, least-privilege IAM role, VPC, subnets and security groups
   for AtlasMarket created with **Terraform**, state in a remote backend, and
   destroyed and recreated once to prove the code is the source of truth
9. A payment-path SLO and error budget **derived from load-test numbers**
10. A one-page on-call runbook, **used blind in a live drill**
11. A blameless postmortem from that drill

**Proof it is correct**
12. Two concurrent identical requests → one charge, identical responses to both
13. The same `provider_event_id` delivered three times → exactly one ledger entry
14. A load test that found a real bottleneck, with before/after numbers — found
    with a **profiler** (`py-spy`, `EXPLAIN (ANALYZE, BUFFERS)`, `pg_stat_statements`),
    not a guess
15. A **network-chaos** run (Toxiproxy: 2s latency into `ledger-service`) showing
    the circuit breaker does *not* help against slow-but-succeeding calls — the
    motivation for AtlasMarket's bulkhead

---

## 3. Scope

**In scope**
- Payment intents with strict idempotency
- Mock provider webhooks with HMAC verification
- Refunds
- Ledger reconciliation via `ledger-service`
- Secrets management, audit logging, threat modelling
- Load testing, SLO, runbook, incident drill
- Backup and disaster recovery for LedgerBase (dump + PITR)
- Terraform for the cloud foundation; Vault rotation and dynamic credentials
- gRPC for the internal ledger call; per-key rate limiting; field-level encryption
- Profiling and network chaos

**Out of scope**

| Deferred | Why |
|---|---|
| Idempotency key expiry / cleanup job | Named; you should know the retention window is a real decision |
| Multi-provider abstraction | One mocked provider is enough to learn the pattern |
| Partial refunds across multiple ledger entries | Named as an improvement |
| Real card data, real PCI compliance | The provider owns card numbers; you own a token. **That is exactly what keeps you out of the highest scope tier**, and the note explains it |

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`merchant` (machine, API key)** | Create payment intents, request refunds, read own payments | Read another merchant's payments; alter a payment's status directly |
| **`provider` (machine, HMAC)** | POST to the webhook endpoint **only** | Anything else. It authenticates by signature, not by API key, and has no other route |
| **`support`** | Read payments and their event history, read the audit log | Create, refund, or alter anything |
| **`finance`** | Read everything, reconcile against the ledger, export | Alter a payment |
| **`ops`** | Read metrics, dashboards, alerts; execute the runbook | Read full payload bodies containing sensitive data *(state the choice)* |

**Two distinct auth mechanisms on purpose:**

| Caller | Mechanism | Why |
|---|---|---|
| Merchant server | **API key** | Server-to-server, long-lived, no user session, rotatable per merchant |
| Provider webhook | **HMAC signature over the raw body** | The caller is not authenticated as an identity; the *message* is authenticated |
| Humans elsewhere in the platform | JWT (from `auth-service`) | Short-lived, user-scoped |

Be able to explain when each is appropriate. "Why not just use JWTs everywhere?"
is a fair question with a real answer.

**Nobody — no role — can change a payment's status by hand.** Status is derived
from the webhook. That is a design decision, not a missing feature.

---

## 5. Architecture

PayFlow builds **directly on LedgerBase**. It calls `ledger-service` to record
each payment as a journal entry, rather than maintaining a parallel money-tracking
implementation.

```
Merchant ──API key + Idempotency-Key──► PayFlow ──► ledger-service (LedgerBase)
                                           ▲
Provider ──HMAC-signed webhook─────────────┘
```

---

## 6. Domain Model

```
merchants(id, name, api_key_hash, rate_limit_per_min,
          payout_account_ref_enc bytea, payout_key_version)
    -- payout_account_ref encrypted client-side (envelope encryption, DEK wrapped
    -- by a KEK in Vault transit); never stored in clear

payment_intents(id, idempotency_key UNIQUE, request_hash, amount_cents,
                status, journal_entry_id NULL, response_body jsonb, created_at)
    -- inserted with INSERT ... ON CONFLICT (idempotency_key) DO NOTHING RETURNING id

webhook_events(id,
               payload jsonb,
               provider_event_id text GENERATED ALWAYS AS (payload->>'id') STORED UNIQUE,
               event_type       text GENERATED ALWAYS AS (payload->>'type') STORED,
               processed_at NULL, received_at)
    -- GIN (payload jsonb_path_ops) for support queries by payment / merchant

refunds(id, payment_intent_id, amount_cents, journal_entry_id, created_at)

payment_audit(id, payment_intent_id, from_status, to_status,
              actor, source, occurred_at)
    -- append-only (trigger, as in LedgerBase)
```

**Two Postgres features earning their place here:**

- **`INSERT ... ON CONFLICT (idempotency_key) DO NOTHING RETURNING id`** is the
  idempotent insert in one statement: a returned row means "you won", no row
  means "someone else did — go read their response". No `try/except
  IntegrityError`, no race between check and insert. Know the difference from
  `DO UPDATE` (a true upsert) and why `DO NOTHING` is right for an idempotency record.
- **JSONB + generated columns**: the webhook payload is stored as received
  (`jsonb`), and the fields you need to constrain or index are **generated
  columns** derived from it — so `provider_event_id UNIQUE` is enforced by the
  database on a value inside the JSON, and support can query
  `payload @> '{"payment_id": 42}'` through a GIN index.

---

## 7. API Design

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/payments` | API key | **Requires `Idempotency-Key`** |
| POST | `/webhooks/provider` | HMAC signature | Idempotent on `provider_event_id` |
| POST | `/payments/{id}/refund` | API key | |
| GET | `/payments/{id}` | API key / support | |
| GET | `/metrics` | internal | |

---

## 8. Idempotency — the core mechanic

Every `POST /payments` requires an `Idempotency-Key` header. The service stores:

```
(key UNIQUE, request_hash, response_body, status)
```

On a repeated key it returns the **original response** instead of re-processing.

**The detail that matters most:** store the **request hash** alongside the key.
Without it, a *different* request that accidentally reuses the same key silently
receives the wrong cached response — a client's retry logic bug becomes your
correctness bug, and it is nearly invisible in logs. With the hash, a key reused
with a different body is an explicit error.

**Concurrency:** two identical requests can arrive simultaneously, before either
has written its record. The unique constraint on `idempotency_key` is what makes
this safe — one insert wins, the other catches the violation and waits for or
reads the winner's response. An `if exists` check is not enough.

Implemented from scratch, tested with a literal duplicate fired twice in a tight
loop.

**Per-merchant rate limiting.** Each API key has a limit (`rate_limit_per_min`).
Enforce it with a **token bucket in Redis, atomically, in a Lua script** (read
tokens, refill by elapsed time, decrement or refuse — one round trip, no race).
Return `429` with `Retry-After`. This is the right use of Redis in PayFlow —
counters that may be lost — in deliberate contrast to the idempotency records
that may not. Compare the token bucket with a fixed window and a sliding log in
`docs/rate-limiting-notes.md`; Project 27 later generalises this into a service.

---

## 9. Webhook Handling

1. **Verify the HMAC signature over the raw body** — before parsing. Handle
   verification failure *explicitly*; never silently accept an unsigned payload
2. **Handle out-of-order and duplicate delivery** — processing is idempotent,
   keyed on `provider_event_id`
3. **Reconcile payment status only from the webhook** — never trust the initial
   API call's "it probably worked"

> Webhook idempotency is a **separate** concern from request idempotency. The
> first protects against *your client* retrying; the second against *the provider*
> retrying. Different keys, different tables, both required. Be ready to explain
> why one does not cover the other.

**The ordering case worth testing:** the webhook can arrive before your own
request has finished committing. Handle it — do not assume your row exists.

---

## 10. Security Hardening

| Item | What you do |
|---|---|
| **Secrets** | Add `vault` to Compose. Move the webhook signing secret and API keys out of `.env` into Vault's KV engine; the app reads them via the API at startup. **Then rotate**: the webhook secret gets a new version; for a grace window the app accepts signatures under *either* version; then the old one is removed — with webhooks flowing the whole time. And the **database password stops being a secret you know**: Vault's database secrets engine issues a short-lived role per app instance (`CREATE ROLE ... VALID UNTIL`), renewed by the app, revoked on shutdown |
| **Field-level encryption** | `payout_account_ref` is encrypted in the application before it reaches Postgres: a per-row data key (DEK) encrypts the value; Vault **transit** wraps the DEK with a key-encryption key (KEK) that never leaves Vault. Store ciphertext + wrapped DEK + key version. Rotate the KEK once (`transit/keys/.../rotate`) and re-wrap. Envelope encryption is what "encryption at rest for PII" means in practice — disk encryption is not it |
| **Audit log** | Append-only record of every payment/refund state change: who, what, when, and *what triggered it* |
| **Threat model** | `docs/threat-model.md`: what if the signing secret leaks? if an idempotency key is guessable? if a request replays after the retention window expires? Each with a mitigation |
| **PCI scope** | `docs/pci-scope-note.md`: which SAQ level applies given the provider owns raw card numbers and you never do; why tokenization plus webhook confirmation keeps you out of the highest tier |
| **HIPAA note** | `docs/hipaa-considerations-note.md` (for CarePoint): patient documents in a portfolio project are not literally subject to HIPAA, but state precisely what access controls, audit logging and encryption-at-rest you would need *if* they were |

Both scoping notes are narrow and honest — **not a real audit**. Same discipline
as every other "named precisely, not oversold" call in this roadmap. Overclaiming
compliance in an interview is worse than saying "here is the scoping I did and
here is what I would need a specialist for."

## 10a. gRPC — the internal call gets a second transport

`PayFlow → ledger-service` is machine-to-machine, internal, latency-sensitive
and contract-bound: the textbook fit for **gRPC**. Add **one** RPC to
`ledger-service` — `PostJournalEntry` — defined in a `.proto`, served by
`grpcio` next to the existing FastAPI app, and called from PayFlow with a
**deadline** (`timeout=`) and the circuit breaker wrapped around it.

Do not port the whole service. One RPC is enough to answer the question
properly:

| | REST/JSON (existing) | gRPC/protobuf (new) |
|---|---|---|
| Contract | OpenAPI, loosely enforced | `.proto` is the contract; codegen for client and server; breaking changes are visible in the diff |
| Wire | Text, HTTP/1.1 | Binary, HTTP/2, multiplexed |
| Errors | HTTP status + body | `grpc.StatusCode` — map `PERIOD_CLOSED` → `FAILED_PRECONDITION`, unbalanced → `INVALID_ARGUMENT` |
| Timeouts | Client-side, ad hoc | **Deadlines** propagate with the call |
| Browser / humans | Native | Needs grpc-web or a gateway |
| Measured here | p50/p95 of `PostJournalEntry` over both, same load | Record it; the number is usually smaller than people expect |

`docs/transport-decision-record.md`: REST vs gRPC vs GraphQL (AtlasMarket) —
when each is the right default. Interview question 13 below.

## 10b. Terraform — the cloud foundation, as code

AtlasMarket (next) deploys to a real cloud. Its account, IAM role, VPC, subnets
and security groups are created **now**, in Week 26, and they are created with
**Terraform**, not in a console:

```
infra/
  main.tf         # provider, remote state backend (S3 + DynamoDB lock, or GCS)
  network.tf      # VPC, public + private subnets, route tables, NAT (or not — cost!)
  iam.tf          # least-privilege role for the gateway; no wildcard actions
  security.tf     # security groups: 443 in to the gateway, 5432 only from the gateway SG
  variables.tf / outputs.tf
```

Rules: `terraform plan` in CI on every PR to `infra/`, `apply` only from `main`;
state is remote and locked; **`terraform destroy` and re-`apply` once** to prove
the console holds nothing the code does not. Tag everything with a cost-center
tag, and read the bill. The managed Postgres instance itself is added in
AtlasMarket, when there is something to connect to it.

Clicking through a console teaches you where the buttons are. Terraform teaches
you what the resources *are*, and gives you a diff to review.

---

## 11. Backup & Disaster Recovery

LedgerBase has held financial data since Week 16 **with no stated backup story** —
a real gap for a system built around double-entry correctness. Close it here:

1. Take a real `pg_dump` backup
2. Write down the **RPO/RTO you are targeting, with reasoning** — not arbitrary
   numbers. What does an hour of lost ledger data actually cost?
3. Deliberately corrupt data in a scratch copy
4. Restore from the backup
5. **Verify the trial-balance report reconciles identically to before**
6. **PITR**: enable `archive_mode` + `archive_command`, take a `pg_basebackup`,
   post a few entries, note the time, post a "bad" entry at 14:04, then restore
   with `recovery_target_time = '14:03'`. The bad entry is gone; the good ones are
   there; the trial balance reconciles. Your RPO just went from "since last dump"
   to "seconds"
7. `docs/backup-dr-plan.md` — both procedures, the RPO/RTO each achieves, and
   the storage cost of keeping WAL

Step 5 is the one that matters. A backup you have never restored is a hope, not a
plan; a restore you have never *verified* is a slightly better hope. Step 6 is
what makes the RPO number you wrote in step 2 honest.

---

## 12. Reliability — SLO, On-Call, Incident Drill

- **SLO derived from real load-test numbers**, e.g. *"99.5% of `POST /payments`
  succeed in under 800ms, measured over a rolling 30 days"* — plus the **error
  budget** it implies. Derive it; do not wish it
- **On-call runbook**, one page, titled *"payment success rate has dropped"*: what
  to check first, second, third, using the Prometheus/Grafana/Sentry stack built
  in Phase 4
- **Live incident drill:** kill `ledger-service`, "page" yourself, follow the
  runbook **blind**, resolve it, and write a **blameless postmortem**

The drill's value is what it reveals the runbook missed. Write that down honestly —
"my runbook assumed I could reach the dashboard, and the first thing I did was
guess" is a better artefact than a runbook that was never tested.

---

## 13. Load Testing

A `locust` scenario simulating realistic concurrent payment traffic — **not** the
light Week-4 smoke test. Find the **actual** bottleneck — **with a profiler,
not a hunch**: `py-spy record` (or `dump`) against the running process for the
Python side, `pg_stat_statements` for the top query, `EXPLAIN (ANALYZE, BUFFERS)`
for that query's plan. Then fix it — an index, a short-lived lock, a connection
pool size — with **before/after numbers**. The bottleneck may well be the
idempotency-key path under contention; the point is that you *found* it.

Then break the network on purpose: put **Toxiproxy** between PayFlow and
`ledger-service`, add 2 seconds of latency (no failures), and re-run the load
test. The circuit breaker stays closed — every call *succeeds*, slowly — while
your worker pool fills up and the p95 of *unrelated* endpoints climbs. Write
down what you saw: this is the failure the breaker cannot see and the reason
AtlasMarket adds a bulkhead.

Those numbers are the input to the SLO. That dependency is the point: the SLO is
downstream of measurement, not of ambition.

---

## 14. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **PostgreSQL** | Payment intents, webhook events, refunds, audit | The unique constraints on `idempotency_key` and `provider_event_id` **are** the idempotency mechanism — not a cache, not application logic |
| **`ledger-service`** (LedgerBase) | Every payment and refund posts a journal entry | Reused, not reimplemented. PayFlow does not track money itself |
| **HashiCorp Vault** | Webhook signing secret, merchant API keys; read via the API at startup | Secrets in `.env` are in your shell history, your backups, and eventually your git history |
| **Prometheus + Grafana** | `POST /payments` latency and success rate (the SLO metrics), webhook processing lag, duplicate-key rate, circuit state on the ledger call | The SLO must be measured by something. This is that something |
| **Sentry** | Exceptions across the service | |
| **`locust`** | Realistic concurrent payment traffic | The numbers behind the SLO |
| **Circuit breaker** (from LedgerBase) | PayFlow's call into `ledger-service` | Reused, not re-derived — the pattern should be routine by now |
| **`pg_dump` + a scratch restore target** | The DR drill | |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Redis for idempotency** | Tempting, and wrong here. Idempotency for money must be **durable and transactional** with the payment record. Redis is the right store for the **rate limiter you do build here**; it is not the right store for "did I already take this person's money?" **This is the most important "why not" in the whole roadmap** — be able to argue it, with both uses of Redis sitting side by side in the same codebase |
| **GraphQL / a gateway in front of PayFlow** | One resource, machine clients. Nothing to aggregate. Named in the transport decision record |
| **A queue in front of `/payments`** | The merchant needs a synchronous answer. Making it async changes the contract, not just the transport |
| **A cache on `GET /payments/{id}`** | Financial state read for decisions. Same rule as LedgerBase balances |
| **A real payment provider** | Mocked deliberately. The lesson is the protocol — signatures, retries, ordering — not a vendor SDK |

---

## 15. Build Plan (consolidated)

### Stage 1 — Idempotency & webhooks *(D145–D149, Week 25)*
- New repo `payflow/`: `PaymentIntent` model + idempotency table
- `POST /payments` idempotency middleware/service, with `request_hash`
- Fire the same request **twice concurrently**, assert a single charge
- Mock provider webhook endpoint + HMAC signature verification over the raw body
- Webhook processing idempotent on `provider_event_id`, reconciling the ledger via
  `ledger-service`

### Stage 2 — Refunds, secrets, DR, gRPC, Terraform *(D151–D153, Week 26)* *(v2: +4 days)*
- Refunds endpoint + API-key auth for server-to-server callers
- **Per-merchant token-bucket rate limiting** (Redis + Lua); `docs/rate-limiting-notes.md`
- `ON CONFLICT DO NOTHING RETURNING` for the idempotency insert; JSONB +
  generated columns + GIN on `webhook_events`
- Real `pg_dump` backup of LedgerBase; RPO/RTO with reasoning; corrupt a scratch
  copy, restore, **verify the trial balance reconciles**
- **PITR**: WAL archiving, `pg_basebackup`, `recovery_target_time` restore →
  `docs/backup-dr-plan.md`
- Add `vault` to Compose; move the webhook secret + API keys into Vault; **rotate
  the webhook secret live** with a grace window; **dynamic DB credentials**
- **Field-level encryption** of `payout_account_ref` via Vault transit; rotate the KEK
- Append-only audit log for payment/refund state changes
- **gRPC** `PostJournalEntry` on `ledger-service`; PayFlow calls it with a deadline;
  REST vs gRPC measured → `docs/transport-decision-record.md`
- **Terraform**: cloud account, remote state, IAM role, VPC/subnets, security
  groups for AtlasMarket; `plan` in CI; `destroy` + re-`apply` once

### Stage 3 — Threat model, load test, incident drill *(D154–D156, Week 26)* *(v2: +1 day)*
- `docs/threat-model.md`, `docs/pci-scope-note.md`, `docs/hipaa-considerations-note.md`
- Realistic-concurrency load test; find the bottleneck **with `py-spy` +
  `pg_stat_statements` + `EXPLAIN (ANALYZE, BUFFERS)`**; fix it; before/after
- **Toxiproxy**: 2s latency into `ledger-service`; observe the breaker not tripping
  and the worker pool filling; write it down
- Write the payment-path SLO + error budget **derived from those numbers**
- Write the "payment success rate dropped" on-call runbook
- **Run the incident drill**: kill `ledger-service`, follow the runbook blind,
  resolve, write a blameless postmortem
- Tag `v0.1-payflow`

---

## 16. Testing Strategy

| Layer | What |
|---|---|
| **Idempotency (centrepiece)** | The exact same request fired **twice concurrently** — only one charge, and **both callers receive the identical response** |
| Idempotency | A *different* request reusing the same key is rejected explicitly, not silently served the cached response |
| Idempotency | The race where neither request has written its record yet — the unique constraint resolves it |
| **Webhook replay** | The same `provider_event_id` delivered 3 times → **exactly one** ledger entry |
| Webhook | An invalid signature is explicitly rejected, and logged as a security event |
| Webhook | A webhook arriving **before** the API call commits is handled |
| Refund | A refund never exceeds the original payment |
| Audit | Every status change produces an audit row; the log cannot be edited |
| Load | Realistic concurrency; bottleneck identified with before/after numbers |
| **DR** | Restore from backup → trial balance reconciles identically |
| Resilience | `ledger-service` down → clean failure, circuit trips, no hang |
| **Rate limit** | Merchant at limit gets `429` + `Retry-After`; another merchant is unaffected; the Lua script is atomic under concurrent hits |
| Upsert | Two concurrent identical inserts: exactly one `RETURNING` row; the loser reads the winner's response |
| JSONB | `provider_event_id` uniqueness enforced by the database on the generated column; a support query by `payment_id` uses the GIN index |
| **Rotation** | Webhooks signed with the old secret verify during the grace window and are rejected after; DB credentials from Vault expire and the app renews them without a restart |
| Encryption | The `payout_account_ref` column contains ciphertext; decrypt round-trips; after KEK rotation old rows still decrypt |
| **gRPC** | `PostJournalEntry` posts a balanced entry; an unbalanced one returns `INVALID_ARGUMENT`; a deadline of 200ms against a slow ledger returns `DEADLINE_EXCEEDED` fast |
| **PITR** | Restore to `14:03` contains every entry before it and none after; trial balance reconciles |
| **Terraform** | `terraform plan` is clean after `apply`; `destroy` + `apply` reproduces the same resources; the DB security group admits only the gateway SG |
| Profiling | The bottleneck is identified from a `py-spy` flame graph or a `pg_stat_statements` row, and the before/after numbers are on the same load profile |
| **Chaos** | With 2s latency and 0% errors, the breaker stays closed and worker saturation is observed |

---

## 17. Definition of Done

- [ ] Idempotency implemented from scratch, **with `request_hash`**, proven under
      concurrent duplicates
- [ ] Webhook signature verification over the raw body, with explicit failure handling
- [ ] Webhook processing idempotent on `provider_event_id`
- [ ] Payment status reconciled from the webhook, not the API call
- [ ] Out-of-order webhook handled
- [ ] Refunds working, ledger entries correct
- [ ] Secrets in Vault, not `.env`
- [ ] Append-only audit log
- [ ] `docs/threat-model.md`, `docs/pci-scope-note.md`, `docs/hipaa-considerations-note.md`
- [ ] `docs/backup-dr-plan.md` with a **verified** restore
- [ ] PITR restore to a point in time, verified
- [ ] Webhook secret rotated live; dynamic DB credentials from Vault
- [ ] Field-level encryption with envelope keys; KEK rotated
- [ ] Per-merchant token-bucket rate limiting; `docs/rate-limiting-notes.md`
- [ ] `ON CONFLICT DO NOTHING RETURNING`; JSONB generated columns + GIN
- [ ] gRPC `PostJournalEntry` with deadline; `docs/transport-decision-record.md`
- [ ] Terraform: IAM/VPC/SG with remote state, `plan` in CI, destroy/apply proven
- [ ] Bottleneck found with a profiler; Toxiproxy latency run documented
- [ ] SLO + error budget derived from real numbers
- [ ] On-call runbook written **and used blind in a live drill**
- [ ] Blameless postmortem written, including what the runbook missed
- [ ] Tag `v0.1-payflow`

---

## 18. Interview Questions This Project Should Let You Answer

1. Walk me through your idempotency implementation end to end.
2. Why store the request hash alongside the key — what breaks without it?
3. Why must webhook processing be idempotent *separately* from the initial payment
   request?
4. Why is Redis the wrong place to store idempotency records here?
5. What happens when two identical requests arrive at the same millisecond?
6. What does your threat model say if the signing secret leaks, and what is your
   mitigation?
7. What did your load test reveal as the actual bottleneck, and how did you fix it?
8. Walk me through your SLO and how you derived the error budget from it.
9. What did your incident drill reveal that your runbook didn't account for?
10. What's your RPO/RTO for LedgerBase, and why those numbers specifically?
11. What keeps PayFlow out of the highest PCI-DSS scope tier?
12. API key vs JWT vs HMAC signature — when does each apply?
13. REST, gRPC, GraphQL — when is each the right default? What did gRPC change for
    the ledger call, and what would it cost to expose to a browser?
14. Why `ON CONFLICT DO NOTHING RETURNING` instead of catching the integrity error?
15. How do you put a unique constraint on a value inside a JSON document?
16. How do you rotate a webhook signing secret without dropping a single webhook?
17. What are dynamic database credentials, and what problem with `.env` passwords do they solve?
18. What is envelope encryption, and why is disk encryption not "encryption of PII"?
19. Token bucket vs sliding window — and why is Redis fine here but not for idempotency?
20. `pg_dump` vs PITR — what RPO does each give you, and what does PITR cost?
21. Why Terraform instead of the console? What does remote state with locking prevent?
22. Your circuit breaker was closed and the system was still dying. Explain.
23. How did you find the bottleneck — show me the flame graph or the `pg_stat_statements` row.

---

## 19. Common Mistakes to Watch For

- Storing the idempotency key **without** the request hash
- Using a cache instead of a durable store for idempotency
- An `if exists` check instead of a unique constraint, which loses the race
- Trusting the initial payment API call's result instead of the webhook
- Parsing the body before verifying the signature
- Not handling signature-verification failure explicitly
- Deriving an SLO from a wish instead of from measured numbers
- A backup that has never been restored, or a restore that was never verified
- A runbook that has never been executed under pressure
- "Secrets in Vault" that have never been rotated — so nobody knows whether rotation works
- Encrypting the disk and calling PII "encrypted at rest"
- Clicking the cloud console, so the VPC exists only in someone's memory
- Trusting the circuit breaker against a dependency that is slow but never fails
- Guessing the bottleneck instead of profiling it
- A backup with a stated RPO of one hour and no WAL archiving

---

## 20. How Real Companies Differ

Real payment platforms (Stripe) treat idempotency as **infrastructure-level**, not
per-endpoint — a client-library concern as much as a server one, so that every
call is idempotent by default rather than by remembering. Worth naming even though
you built it per-endpoint here.

---

## 21. ML/MLOps Extension — Stage 3 *(Week 26, +3 days)*

> **Why here — closing the last real gap.** PayFlow has no Track B counterpart,
> and it is already the most heavily observed system in Track A (Prometheus,
> Grafana, Sentry, an SLO). That makes it the right place for the curriculum's
> most senior AI work: a model whose **operational behavior** — latency, drift —
> gets the same monitoring discipline as everything else in this project.

**Scope (in)**
- A classification model (`scikit-learn`, e.g. `IsolationForest` or logistic
  regression on engineered features) flagging payments that look anomalous:
  amount vs. merchant's history, velocity (payments per minute per merchant),
  time-of-day — named honestly as a **fraud-signal proxy**, not a real fraud
  system
- **MLflow** tracking (reused from LedgerBase's habit) for training runs
- **A model-serving metric wired into the existing Prometheus stack**:
  prediction latency (histogram) and a simple drift signal (the mean of the
  model's score over a rolling window, alerting if it moves outside a band) —
  the same RED-metric discipline this project already applies to its API
- One Grafana panel showing the anomaly score distribution alongside payment
  volume

**Scope (out)**

| Deferred | Why |
|---|---|
| A real fraud rules engine, blocking payments | This is a signal, not a decision — a false positive here means an interview note, not a declined transaction |
| A model registry, automated retraining | Phase 10 — this project reuses the *monitoring* habit, not the full MLOps pipeline |
| Labeled fraud data | None exists; the model is unsupervised, and that limitation is stated honestly |

**Definition of Done**
- [ ] Model trained and tracked in MLflow
- [ ] Prediction-latency histogram and a drift-signal metric visible in Grafana,
      alongside the existing RED dashboards
- [ ] `docs/fraud-signal-notes.md`: what this model can and cannot claim to detect

**Interview questions this adds**
1. Why treat this as a signal for a human to review rather than an automatic block?
2. What does "drift" mean for a model in production, and how did you detect it here
   without a labeled ground truth?
3. Why does a model's latency belong on the same dashboard as the API's?
