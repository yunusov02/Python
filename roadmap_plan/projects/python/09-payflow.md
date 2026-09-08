# Project 9 — PayFlow

**Payment processing platform: idempotency, webhooks, ledger reconciliation**

| | |
|---|---|
| Domain | FinTech |
| Level | Middle+ / Senior |
| Phase | 6 — Senior-Track Capstone |
| Weeks | 25–26 (D145–D156) |
| Stack | Python, FastAPI, PostgreSQL, **HashiCorp Vault**, Prometheus/Grafana/Sentry, `locust`, LedgerBase's `ledger-service` |
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
5. Secrets in Vault rather than `.env`
6. An append-only audit log of every payment and refund state change

**Operational capability — half the value of this project**
7. `docs/threat-model.md`, `docs/pci-scope-note.md`, `docs/hipaa-considerations-note.md`
8. `docs/backup-dr-plan.md` with a **verified restore** and a reconciling trial balance
9. A payment-path SLO and error budget **derived from load-test numbers**
10. A one-page on-call runbook, **used blind in a live drill**
11. A blameless postmortem from that drill

**Proof it is correct**
12. Two concurrent identical requests → one charge, identical responses to both
13. The same `provider_event_id` delivered three times → exactly one ledger entry
14. A load test that found a real bottleneck, with before/after numbers

---

## 3. Scope

**In scope**
- Payment intents with strict idempotency
- Mock provider webhooks with HMAC verification
- Refunds
- Ledger reconciliation via `ledger-service`
- Secrets management, audit logging, threat modelling
- Load testing, SLO, runbook, incident drill
- Backup and disaster recovery for LedgerBase

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
payment_intents(id, idempotency_key UNIQUE, request_hash, amount_cents,
                status, journal_entry_id NULL, response_body, created_at)

webhook_events(id, provider_event_id UNIQUE, payload,
               processed_at NULL, received_at)

refunds(id, payment_intent_id, amount_cents, journal_entry_id, created_at)

payment_audit(id, payment_intent_id, from_status, to_status,
              actor, source, occurred_at)
    -- append-only
```

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
| **Secrets** | Add `vault` to Compose. Move the webhook signing secret and API keys out of `.env` into Vault's KV engine; the app reads them via the API at startup |
| **Audit log** | Append-only record of every payment/refund state change: who, what, when, and *what triggered it* |
| **Threat model** | `docs/threat-model.md`: what if the signing secret leaks? if an idempotency key is guessable? if a request replays after the retention window expires? Each with a mitigation |
| **PCI scope** | `docs/pci-scope-note.md`: which SAQ level applies given the provider owns raw card numbers and you never do; why tokenization plus webhook confirmation keeps you out of the highest tier |
| **HIPAA note** | `docs/hipaa-considerations-note.md` (for CarePoint): patient documents in a portfolio project are not literally subject to HIPAA, but state precisely what access controls, audit logging and encryption-at-rest you would need *if* they were |

Both scoping notes are narrow and honest — **not a real audit**. Same discipline
as every other "named precisely, not oversold" call in this roadmap. Overclaiming
compliance in an interview is worse than saying "here is the scoping I did and
here is what I would need a specialist for."

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
6. `docs/backup-dr-plan.md`

Step 5 is the one that matters. A backup you have never restored is a hope, not a
plan; a restore you have never *verified* is a slightly better hope.

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
light Week-4 smoke test. Find the **actual** bottleneck (likely the
idempotency-key lookup under contention) and fix it — an index, or a short-lived
lock — with **before/after numbers**.

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
| **Redis for idempotency** | Tempting, and wrong here. Idempotency for money must be **durable and transactional** with the payment record. Redis is the right cache for a rate limiter; it is not the right store for "did I already take this person's money?" **This is the most important "why not" in the whole roadmap** — be able to argue it |
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

### Stage 2 — Refunds, secrets, DR *(D151–D153, Week 26)*
- Refunds endpoint + API-key auth for server-to-server callers
- Real `pg_dump` backup of LedgerBase; RPO/RTO with reasoning; corrupt a scratch
  copy, restore, **verify the trial balance reconciles** → `docs/backup-dr-plan.md`
- Add `vault` to Compose; move the webhook secret + API keys into Vault
- Append-only audit log for payment/refund state changes
- *(In parallel, for AtlasMarket's later deploy: create the cloud account, a
  least-privilege IAM role, and a VPC with public/private subnets)*

### Stage 3 — Threat model, load test, incident drill *(D154–D156, Week 26)*
- `docs/threat-model.md`, `docs/pci-scope-note.md`, `docs/hipaa-considerations-note.md`
- Realistic-concurrency load test; find and fix the bottleneck
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

---

## 20. How Real Companies Differ

Real payment platforms (Stripe) treat idempotency as **infrastructure-level**, not
per-endpoint — a client-library concern as much as a server one, so that every
call is idempotent by default rather than by remembering. Worth naming even though
you built it per-endpoint here.
