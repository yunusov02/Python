# Stage 05 — AtlasPay v1 inside the monolith + provider-sim

| | |
|---|---|
| **Weeks** | W19–W23 (5 weeks) |
| **Hours** | 60 must + 6 stretch |
| **Architecture at start → at end** | Modular monolith `market` (process types web / worker / beat / relay / consumers; RabbitMQ `atlas.events`, outbox, redis-cache / redis-state) with orders stuck in `awaiting_payment` → the same monolith plus a **`payments` module** (the in-monolith AtlasPay: intents, providers, ledger, connect, payouts, reconciliation) whose core lives in the framework-free `libs/atlaspay-domain`, plus **`provider-sim`**, an external emulator of Payme and Click with its own `sim` DB |
| **New technologies** | JSON-RPC 2.0; Payme Merchant API; Click SHOP API and Merchant API; FastAPI + SQLAlchemy 2.0 async (provider-sim, reusing your D1–D5 skills); PL/pgSQL `DEFERRABLE INITIALLY DEFERRED` constraint triggers and append-only triggers; generated columns; advisory locks; window functions; materialized views refreshed `CONCURRENTLY`; server-side cursors; Hypothesis `RuleBasedStateMachine`; freezegun plus an injectable clock |
| **Portfolio tag** | `v0.5` |
| **Old-spec theory to read** | [P6 LedgerBase](../python/06-ledgerbase.md) D91–D96 (float drift, CHECK vs constraint trigger, append-only, window functions, matview, streaming export); [P9 PayFlow](../python/09-payflow.md) D145–D153 (idempotency key + request hash, concurrent duplicates, JSONB + generated UNIQUE column + GIN, `ON CONFLICT DO NOTHING RETURNING`); [P4 WareFlow](../python/04-wareflow.md) D67–D71 (write skew and SERIALIZABLE, timeouts, BRIN); [P10 AtlasMarket](../python/10-atlasmarket.md) D163–D165 (one payment, many vendor groups); [phase-8](../../phase-8-ai-devtools-zoomcamp.md) D241–D243 (a scheduled reconciliation pipeline); the provider documentation linked in §4.0 |

Version pins in this file are as of 2026-09. Re-check them with `scripts/compat_check.sh` at the start of the stage.

> **What this stage is really for.** This is the payments heart of Atlas and the stage interviewers will probe hardest. You build a Stripe-shaped payment module whose core is plain Python, connect it to two real Uzbek provider protocols through a simulator that behaves like the real thing (duplicates, lost responses, 12-hour timeouts), and keep a double-entry ledger that always balances and can be rebuilt from scratch. Every failure the protocols can produce is shown red before it is made green.

---

## 1. The problem this stage starts from

**Business view.** After [Stage 04](stage-04-async-events-boundaries.md) a buyer can fill a multi-vendor cart and check out. The order is split into vendor groups, stock is held for 30 minutes, and the order sits in `awaiting_payment`. Then nothing happens, because the platform cannot take money. A marketplace has to do four things with money:

1. collect one payment from the buyer, through Payme or Click, the two providers Uzbek buyers actually use;
2. owe each vendor their share, minus the platform's commission (the commission schedule you built with `EXCLUDE` in [Stage 01](stage-01-layered-monolith.md));
3. pay vendors out on a schedule, and refund buyers, fully or partly;
4. prove at any moment that every tiyin is accounted for.

**Engineering view.** Payme and Click do not work like Stripe. With Stripe, *you* call the provider and hear back later through signed, retried webhooks. With Payme's Merchant API and Click's SHOP API it is the other way round: **the provider calls you, synchronously, and your reply is part of their transaction.** Check and Prepare approve a payment; Perform and Complete record it. If your reply is wrong, late or lost, the buyer can be charged while the order stays unpaid, or the case goes to manual handling by the provider's staff. The network will lose responses, the provider will retry with the same parameters, two providers can be used for one order at the same time, and staff at the provider can resolve a transaction by hand without telling you.

Nothing you have built so far covers this. The S2 idempotency store knows about one client and one order. There is no ledger. Nothing reconciles your records against someone else's.

---

## 2. Outcomes — what exists when the stage is finished

1. **`provider-sim`**, a FastAPI + SQLAlchemy 2.0 async service with its own `sim` database on `pg-sim`, which speaks Payme's Merchant API and Click's SHOP and Merchant APIs as documented, drives a fake clock, and has chaos switches (drop the response after commit, delay, duplicate, send concurrently, reorder, retry with a new JSON-RPC id).
2. **`libs/atlaspay-domain`**, a framework-free Python package (no Django, no FastAPI, no SQLAlchemy imports, enforced by import-linter) holding the PaymentIntent and PaymentAttempt state machines, the idempotency semantics, the posting rules, the split math and the ports.
3. **The `payments` Django app in market** (tables prefixed `payments_`), which adapts the domain to Postgres and to the provider callback endpoints `/providers/payme/rpc`, `/providers/click/prepare` and `/providers/click/complete`.
4. **A double-entry ledger** with connected accounts (`acct_…` per vendor) and platform accounts, enforced by a deferred constraint trigger and append-only triggers, with a running-balance query, a `trial_balance_mv`, a `rebuild_balances` command and a streaming CSV statement.
5. **Connect-style money movement:** separate charges and transfers, application fees from the S1 commission schedule, proportional transfer reversal on refunds, daily payouts.
6. **Nightly reconciliation** against both providers, reporting drift rows and alerting on `recon_drift_rows > 0`.
7. **The acceptance suite:** the Payme sandbox scenarios 1–2, Click's 15 Postman scenarios, and the 12 failure scenarios in §4.0.3, each committed red first and then green, run under the chaos switches in CI.
8. **market pays through a port:** `PaymentsGateway` with an in-process adapter, and payment state changes leave through the outbox as `payment_intent.*` events.
9. **Documents:** ADR-017, ADR-018, ADR-019, ADR-020, threat model v1, `docs/design/reconciliation.md`, evidence under `docs/evidence/s05/`, two STAR stories, the SD18 session notes and the stage postmortem paragraph.

---

## 3. Architecture at the end of the stage

```
                              Buyer browser
                  checkout |        ^ redirect back to status page
                           v        |
+----------------------------- market (Django 5.2 monolith) ------------------------------+
| web (gunicorn)                                                                           |
|   /api/v1/*   ordering --PaymentsGateway (port, in-process adapter)--> payments module  |
|   /providers/payme/rpc        <------------- JSON-RPC 2.0, text/json ------------+      |
|   /providers/click/prepare    <------------- form-urlencoded (action=0) ---------+      |
|   /providers/click/complete   <------------- form-urlencoded (action=1) ---------+      |
|                                                                                  |      |
|   payments = Django adapters (ORM repos, plain views)  +  libs/atlaspay-domain   |      |
|     intents | attempts | idempotency | ledger | connect | payouts | reconciliation |      |
|                                                                                  |      |
|   worker (Celery: refunds out, reversal client)   beat (payouts, recon, mv)      |      |
|   relay (outbox -> RabbitMQ)   consumers (market.payment-events -> ordering)     |      |
+------------|------------------------------------------|-------------------------|------+
             | one short transaction:                   | after commit only,      |
             | state + journal lines + outbox row       | outbound token bucket   |
             v                                          v                         |
   pg-market / DB market                          provider-sim (FastAPI, async) --+
     payments_* tables, constraint trigger,         Payme mode | Click mode | chaos
     append-only triggers, trial_balance_mv         fake clock | /v2/merchant/* (Click)
             |                                      own DB: pg-sim / sim
             v relay
   RabbitMQ atlas.events --payment_intent.*--> market.payment-events --> order marked paid
                                               (S5-S8 only; signed AtlasPay webhooks from S9)
   redis-state: outbound token bucket (rl:)         S3 store (Garage) atlas-statements (optional export)
```

**What changed and why.**

- **A new module, not a new service.** Payments lives inside market for now. You have no measured reason to split it yet. [Stage 06](stage-06-ship-and-operate.md) builds the split gate that produces those numbers, and [Stage 09](stage-09-strangler-atlaspay-auth.md) extracts AtlasPay only after the numbers are in. Building it as a module with a framework-free core is what makes that later extraction a rewrite of adapters only.
- **A framework-free core.** `libs/atlaspay-domain` holds everything that is *about money*: states, transitions, posting rules, split math, idempotency semantics. The Django app holds everything that is *about Django*: models, views, Admin. In S9 the domain package moves unchanged and only the adapters are rewritten in FastAPI.
- **A simulator as a real network peer.** `provider-sim` is a separate process on purpose. A pytest fixture cannot lose a response after your commit, cannot retry 3 seconds later over a real socket, and cannot make two callbacks race. Those are the failures that cost real money.
- **Callbacks do one short transaction.** Every callback validates, writes the state change, the journal lines and an outbox row, commits and answers. Emails, fulfilment, vendor notifications and any outbound call to a provider happen after commit, through the outbox and Celery.
- **market talks to payments through a port.** The `PaymentsGateway` Protocol is the seam S9 cuts along: its in-process adapter becomes an HTTP adapter with an `sk_` key.
- **The payment-events queue is temporary.** `market.payment-events` carries `payment_intent.*` to ordering from S5 to S8 only. From S9, market learns payment, refund and payout outcomes only from signed AtlasPay webhooks, like any outside merchant, and the queue is unbound and deleted in the S9 contract step. Build ordering's consumer on the S4 inbox (dedup on event id) so the S9 webhook receiver can reuse the same table.

---

## 4. Build plan

Suggested weekly split (12 h each, including a 1 h drill every week): **W19** most of provider-sim. **W20** the rest of provider-sim, intents and idempotency, the start of the Payme adapter. **W21** the rest of the Payme adapter, the Click adapter, the cross-provider lock. **W22** the ledger and most of Connect. **W23** the rest of Connect, payouts, reconciliation, hold and long transactions, the port, SD18 in the drill hour. Keep the chaos runs, the concurrency tests and the ADR-019 posting benchmark for the weekend block, because they need uninterrupted state.

These block hours are the baseline. At [B1](buffers-and-job-sprint.md) you computed your actual/budget ratio from the hours log; if it was above 1 and you re-planned, use your re-planned numbers instead. Keep logging actual hours per block. If a spine block overruns (the 12 scenarios, the ledger invariants, reconciliation), the date moves; nothing on the spine is silently deferred ([schedule-and-cuts](schedule-and-cuts.md)).

### 4.0 Reference: how Payme and Click actually talk to you

Read this section before any block. Everything here comes from the providers' own documentation, their flowchart images and the official sample repositories they link to, checked in September 2026. **[C]** means confirmed from a primary source. **[U]** means unconfirmed: the documentation does not say, so the simulator makes it a *setting*, and your tests state the assumption.

#### 4.0.1 Payme (Paycom) Merchant API

**Who calls whom.** Payme's server calls **your** billing endpoint (the "Endpoint URL" configured in the Payme Business web-kassa). You never call the Merchant API; you answer it. [C]

```
Buyer        market / payments                     Payme (provider-sim in Payme mode)
  |--pay------->| intent -> requires_action               |
  |<-redirect---| <checkout_url>/base64(m=..;ac.order_id=..;a=..)
  |-------------------------------- opens checkout page -->|
  |             |<-- CheckPerformTransaction(amount, account)   "may I take this payment?"
  |             |--> {allow: true}                              (or -31001 / -31050..-31099)
  |             |<-- CreateTransaction(id, time, amount, account)   sandbox: sent twice
  |             |--> {create_time, transaction, state: 1}           identical both times
  |             |         ... Payme debits the card ...
  |             |<-- PerformTransaction(id)                     sandbox: sent twice
  |             |--> {transaction, perform_time, state: 2}
  |<---------------------------- redirect back (c=return URL) --|
  |             |<-- CheckTransaction(id)  (status, at any time)
  |             |<-- CancelTransaction(id, reason)  (debit failed, timeout, or refund)
  |             |<-- GetStatement(from, to)  (Payme reconciles its side against yours)
```

**Transport rules** (source: https://developer.help.paycom.uz/protokol-merchant-api/ and its sub-pages):

| Rule | Detail |
|---|---|
| Protocol | JSON-RPC 2.0 over HTTPS POST, named params only. The example header is `Content-Type: text/json; charset=UTF-8`. [C] |
| **HTTP 200 always** | "Статусы отличные от 200 воспринимаются как RPC-ошибка: -32400". Any non-200 (a 401, a 415, a 301 redirect, an HTML 500 page) is recorded by Payme as a system error. Errors travel **inside** an HTTP 200 JSON body. [C] |
| Request / response | Request `{method, params, id}`. Success `{result, id}`. Error `{error: {code, message: {ru, uz, en}, data}, id}`; the localized `message` is shown to the buyer. [C] |
| Auth | `Authorization: Basic base64(login:password)`. The password is the 36-character kassa key. The official PHP template says the login "is always Paycom". Failed auth returns **-32504**. Each kassa has a production key and a separate TEST_KEY. [C] |
| Source IPs | Payme sends requests only from **185.234.113.1–185.234.113.15**. [C] |
| Data types | `ID`: 24-character string. `Timestamp`: 13 digits, milliseconds since epoch, UTC. `Amount`: positive integer **in tiyin**. `Account`: merchant-defined object, e.g. `{"order_id": ...}`. [C] (https://developer.help.paycom.uz/metody-merchant-api/tipy-dannykh/) |
| Retries | If the response to Create or Perform is lost, Payme **repeats the request with the same parameters**. With no answer for a long time, the payment is suspended and handled manually by Payme staff. If the debit fails, Payme calls CancelTransaction. [C] The retry schedule and your response deadline are **not documented [U]**, so design for a short deadline. Whether a retry reuses the JSON-RPC envelope `id` is also **not documented [U]**; the response `id` must always equal the id of the request it answers [C] (https://developer.help.paycom.uz/protokol-merchant-api/format-otveta/). |
| **Sandbox double-send** | In the sandbox, Create, Perform and Cancel "посылаются два раза… ответ должен совпадать с ответом из первого запроса": sent twice, and the second answer must match the first. [C] (https://developer.help.paycom.uz/pesochnitsa/) |
| **12-hour timeout** | "Отмена по таймауту производится через 12 часов — 43 200 000 миллисекунд с момента создания транзакции в Payme Business". The result is state -1, reason 4. [C] Whether the clock starts at Payme's `time` or at your `create_time` is **[U]**: the docs name Payme's creation time, the official template compares against the merchant's `create_time`. |
| Checkout redirect | `GET <checkout_url>/base64(params)`, params `key=value` joined with `;`: `m` merchant id, `ac.<field>` account, `a` amount in tiyin, `l` language, `c` return URL, `ct` return delay (ms), `cr` currency. The official example decodes to `m=587f72c72cac0d162c722ae2;ac.order_id=197;a=500`. Sandbox host `https://test.paycom.uz`, production `https://checkout.paycom.uz`. [C] |

The envelope shape, for orientation only:

```
-> {"method": "PerformTransaction", "params": {"id": "<24 chars>"}, "id": 7}
<- {"result": {"transaction": "<your id>", "perform_time": 1726000000000, "state": 2}, "id": 7}
<- {"error": {"code": -31003, "message": {"ru": "...", "uz": "...", "en": "..."}, "data": null}, "id": 7}
```

**Methods** (all called by Payme on you; source: https://developer.help.paycom.uz/metody-merchant-api/):

| Method | Params → result | What you must do [C] |
|---|---|---|
| CheckPerformTransaction | `amount, account` → `{allow: true}` (+ optional `detail` fiscal items) | Check the order exists, is payable and the amount matches. Payme recommends also checking every system Create and Perform will need, and returning -32400 if one is down. Errors -31001, -31050..-31099. |
| CreateTransaction | `id, time, amount, account` → `create_time, transaction, state` (+ optional `receivers`) | Store the transaction durably, validate account and amount, **reserve the order and block changes to it**. Errors -31001, -31008, -31050..-31099. |
| PerformTransaction | `id` → `transaction, perform_time, state` | Credit the merchant, mark the order paid. Errors -31003, -31008, -31050..-31099. |
| CancelTransaction | `id, reason` → `transaction, cancel_time, state` | Cancel a created or a performed transaction. Errors -31003, **-31007** (order already fulfilled). Refunds to the buyer exist only through this method. |
| CheckTransaction | `id` → `create_time, perform_time, cancel_time, transaction, state, reason` | Report status. Error -31003. |
| GetStatement | `from, to` → `{transactions: [...]}` | **Mandatory.** Select `from <= time <= to` using **Payme's** `time`, sort ascending, include only transactions whose Create succeeded. |
| SetFiscalData | `id, type (PERFORM or CANCEL), fiscal_data` | Optional (stretch). Fiscal receipt data. |
| ChangePassword | `password` | [U] Not in the current method list, still handled in the official PHP template. Treat as legacy; do not build. |

**The official flowcharts: external protocol contract (requirement).** Each method page under https://developer.help.paycom.uz/metody-merchant-api/ (for example `.../createtransaction/`) has a flowchart image, and those images are the spec for the Payme adapter. Before you read the paraphrase below, turn each official image into a decision table of test cases yourself (one row per branch: input state, condition, expected reply, expected state change). Then compare your table with this paraphrase, which is here as a checked reference because the source is in Russian. Where they disagree, the official image wins.

- **Create:** look the transaction up by `id`. Found and `state != 1` → -31008. Found, state 1, but past the timeout → set state -1 reason 4, return -31008. Found otherwise → return the stored `state, create_time, transaction`. Not found → run the CheckPerform logic and return its error if any; otherwise store with state 1 and reserve the order.
- **Perform:** not found → -31003. State 2 → return the stored `state, perform_time, transaction` again. State neither 1 nor 2 → -31008. State 1 past the timeout → cancel with -1 reason 4, return -31008. Otherwise mark the order paid, set state 2, return.
- **Cancel:** not found → -31003. State 1 → -1 with `reason` from the request. State 2 → if the order can no longer be cancelled, -31007; otherwise mark it cancelled and move to -2. Already cancelled → return the stored `state, cancel_time, transaction`.
- **CheckPerform (one-time account):** order missing or not payable → -31050..-31099. Amount mismatch → -31001. Otherwise `allow: true`.

**States, reasons and errors** (https://developer.help.paycom.uz/metody-merchant-api/oshibki-errors):

| Transaction state | Meaning | | Cancel reason | Meaning |
|---|---|---|---|---|
| 1 | created, waiting for Perform | | 1 | receiver not found or inactive |
| 2 | performed (paid) | | 2 | debit error at the processing centre |
| -1 | cancelled from state 1 | | 3 | transaction execution error |
| -2 | cancelled after Perform (refund) | | 4 | timeout |
| | | | 5 | refund |
| | | | 10 | unknown |

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| -32300 | not a POST | -31001 | wrong amount |
| -32700 | JSON parse error | -31003 | transaction not found |
| -32600 | missing fields or wrong types | -31007 | cannot cancel: goods already delivered |
| -32601 | method not found (method name in `data`) | -31008 | operation impossible in the current state |
| -32504 | insufficient privileges (auth) | -31050..-31099 | invalid `account`; localized `message` required, `data` = the account sub-field name |
| -32400 | system error (DB down, and every non-200) | | |

**A known discrepancy you must test.** The sandbox documentation says a CreateTransaction with a **new** transaction id for an order that is already waiting for payment must return **-31008**. The official PHP template returns **-31050** in that case. Treat the sandbox doc as authoritative, make the other behaviour a simulator setting, and keep a test that documents the difference.

#### 4.0.2 Click SHOP API and Merchant API

**Who calls whom.** In the **SHOP API**, Click calls you: two form-urlencoded POSTs, **Prepare** (`action=0`) and **Complete** (`action=1`), to URLs you give Click; you answer with JSON. In the **Merchant API**, you call Click (invoices, payment status, reversal, card tokens). Source: https://docs.click.uz/shop-api/requests and https://docs.click.uz/merchant-api/requests. [C]

```
Buyer        market / payments                        Click (provider-sim in Click mode)
  |--pay------->| intent -> requires_action                  |
  |<-redirect---| my.click.uz/services/pay?service_id=..&merchant_id=..&amount=N.NN&transaction_param=..
  |-------------------------------------- pays on Click --->|
  |             |<-- Prepare(click_trans_id, merchant_trans_id, amount, action=0, sign_string, ...)
  |             |--> {click_trans_id, merchant_trans_id, merchant_prepare_id, error: 0}
  |             |         ... Click debits the card ...
  |             |<-- Complete(..., merchant_prepare_id, action=1, error: 0 or <0, sign_string)
  |             |--> {click_trans_id, merchant_trans_id, merchant_confirm_id, error: 0}
  | (you -> Click, Merchant API)  GET payment/status_by_mti/..., DELETE payment/reversal/...
```

| Stage | Request fields | Response fields |
|---|---|---|
| Prepare | `click_trans_id` (bigint), `service_id` (int), `click_paydoc_id` (bigint), `merchant_trans_id` (your order id), `amount` (float, **in soums**), `action=0`, `error` (int), `error_note`, `sign_time` ("YYYY-MM-DD HH:mm:ss"), `sign_string` | `click_trans_id, merchant_trans_id, merchant_prepare_id` (int), `error, error_note` |
| Complete | the Prepare fields plus `merchant_prepare_id`, with `action=1` | `click_trans_id, merchant_trans_id, merchant_confirm_id` (int), `error, error_note` |

**Signature** [C]:

```
Prepare:  md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + amount + action + sign_time)
Complete: md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + merchant_prepare_id + amount + action + sign_time)
```

The exact string format Click uses for `amount` ("1000" or "1000.00") is **not documented [U]**. Compute the MD5 over the **raw strings you received**, never over a number you parsed and re-formatted.

**Error codes you return** (https://docs.click.uz/shop-api/errors):

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| 0 | success | -5 | user or order does not exist (`merchant_trans_id`) |
| -1 | SIGN CHECK FAILED | -6 | transaction does not exist (`merchant_prepare_id`) |
| -2 | incorrect amount | -7 | failed to update user |
| -3 | action not found | -8 | error in request from Click (missing params) |
| -4 | already paid | -9 | transaction cancelled |

**Complete rules** [C]:

- Click's own `error` field: 0 means success; **any negative value means the payment failed, and you must cancel it and answer -9.** Click's test scenarios use `error = -5017` for this. What -5017 means exactly is **[U]** (it is commonly said to be insufficient funds).
- Once Prepare succeeded and the card was debited, "the response to the Complete request cannot be an error", except **-4** (already confirmed) and **-9** (confirming a cancelled payment). If your own fulfilment fails after the debit, answer Complete successfully and then call the Merchant API `payment/reversal`.
- Repeated error responses can move the payment into manual investigation by Click support.
- **Contrast with Payme:** a repeated Complete on an already-paid payment returns **-4**. Payme, for a repeated Perform, expects the **identical success `result`** (in an envelope carrying the current request's `id`). This difference belongs inside each adapter, never in the core.

**Merchant API (you call Click)** [C]:

- Auth header `Auth: merchant_user_id:digest:timestamp`, where `digest = sha1(timestamp + secret_key)` and the timestamp is 10-digit UNIX seconds.
- Under `https://api.click.uz/v2/merchant/`: `POST invoice/create`, `GET invoice/status/...`, `GET payment/status/:service_id/:payment_id`, **`GET payment/status_by_mti/:service_id/:merchant_trans_id/YYYY-MM-DD`**, **`DELETE payment/reversal/:service_id/:payment_id`**, plus `card_token/*`. Errors are plain HTTP status codes (400, 401, 403, 404, 406, 410, 500, 502).
- **Reversal conditions:** the payment completed successfully; only payments from the **current reporting month** (previous-month payments only on the 1st day of the new month); online cards only; **UZCARD may reject the reversal.** Which time zone defines "month" is not stated; make it a setting (Asia/Tashkent is the natural guess [U]).

**Testing without a contract** [C]: Click hosts no sandbox of its own, but provides a browser Playground and a **Postman collection generator with 15 scenarios** that aim at *your* server (https://docs.click.uz/en/testing/postman). The scenarios named in the docs include -1 bad sign, -5 missing order, -2 with `amount=300`, -4 repeated Complete, -9 with `error=-5017`, -6 with `prepare_id=999999999`, a repeated cancel and confirming a cancelled payment. Generate the collection and port all 15 into the simulator's Click script. No Merchant API test environment was found [U].

**Review exercise: the official Click Django sample has bugs** (https://github.com/click-llc/click-integration-django, `click/utils.py`). Before you write your adapter, read it and find at least five defects. Look at: how it validates that the parameters are present, how it compares the amount, what `merchant_prepare_id` refers to, what happens when Prepare and Complete for one payment run concurrently, and the types of the values it returns. For each defect, write the failing test you would add. Then do the same for the Payme PHP template's timeout check on a new transaction. Official samples are not specs. Compare your list with the one in §16 only after you have written yours.

#### 4.0.3 The 12 failure scenarios — the acceptance table

These are the tests you write **red first**, in the block named in the last column, and keep green forever. They run in the `sim-acceptance` CI job with the chaos switches on. "Provider-visible reply" is what the simulator must receive; "internal state" is what your database must contain afterwards. Test names are suggestions; keep them greppable.

| # | Scenario (how the sim produces it) | Expected provider-visible reply | Expected internal state | Test name | Block |
|---|---|---|---|---|---|
| 1 | **Duplicate CreateTransaction**, same `id`: once sequentially (response dropped after commit), once as two copies sent at the same moment, and once as a retry with a **new JSON-RPC `id`** (chaos switch) | Both replies carry the stored first `result` member **byte for byte** (same `create_time`, `transaction`, `state: 1`), and each reply's envelope `id` equals the `id` of the request it answers | Exactly one attempt row (UNIQUE on provider + provider transaction id), state `reserved`; intent `processing`; one raw event row | `test_s05_01_payme_create_duplicate_sequential`, `test_s05_01_payme_create_duplicate_concurrent` | 4.3 |
| 2 | **New Create `id` for an order that already has a state-1 transaction** | **-31008** (sandbox doc). The simulator setting `payme.second_create_error` can expect -31050 (PHP template); the test documents the discrepancy | No second attempt; the first attempt unchanged | `test_s05_02_payme_second_create_for_pending_order` | 4.3 |
| 3 | **Perform more than 43,200,000 ms after creation** (fake clock advanced) | **-31008**; a later CheckTransaction reports `state: -1, reason: 4` | Attempt `canceled` with reason 4 and the time it was cancelled; intent back to `requires_payment_method` (or `canceled`, per ADR-020); a `payment_intent.payment_failed` outbox row | `test_s05_03_payme_perform_after_12h_timeout` | 4.3 |
| 4 | **Perform after AtlasMarket's 30-minute stock hold expired**, still inside Payme's 12 hours | As decided in **ADR-020**. Constraint: once Payme has debited the card, what Payme does with an error reply is undocumented [U], so the design must never leave a buyer charged with no order and no refund path | Consistent with the ADR: either the payment succeeds (stock re-reserved, or the vendor group marked unfulfillable with a refund task opened for ops), or the design prevented the situation earlier | `test_s05_04_payme_perform_after_hold_expiry` | 4.10 |
| 5 | **CancelTransaction after Perform** (reason 5, refund) | Order not yet shipped → `{cancel_time, transaction, state: -2}`. Any vendor group shipped → **-31007**. A repeated Cancel → the **original** `cancel_time` | Not shipped: attempt `refunded`, a Refund object, reversing journal entries (charge, transfers, fees) balanced, stock restored through `stock_movements`. Shipped: nothing changed | `test_s05_05_payme_cancel_after_perform_refunds`, `test_s05_05_payme_cancel_after_ship_31007`, `test_s05_05_payme_cancel_replay` | 4.3, 4.7 |
| 6 | **Amount mismatch**: the ×100 soum/tiyin bug; a tampered `a=` in the checkout URL; Click `"1000.00"` vs `1000`; float rounding | Payme: **-31001** from both Check and Create. Click: **-2** for a real mismatch, and **never a false -1** caused by re-formatting the amount before the MD5 | No attempt created; intent unchanged | `test_s05_06_payme_amount_x100`, `test_s05_06_click_amount_formats` | 4.3, 4.4 |
| 7 | **Auth and transport failures**: bad Basic auth; source IP outside the allowlist; then deliberately a DRF 401, a `text/json` 415, an HTML 500 page and an `APPEND_SLASH` 301 | Bad auth or IP → HTTP 200 with **-32504**. Every other failure → HTTP 200 JSON with **-32400**. The endpoint **never** returns a non-200 status or HTML | Nothing written except a security log line (and the raw request, if you log rejected requests separately) | `test_s05_07_payme_bad_auth_32504`, `test_s05_07_payme_never_non200_or_html` | 4.3 |
| 8 | **Click Complete with `error=-5017`**; then a second such Complete; then a Complete on an already-cancelled payment | **-9** each time | Attempt `canceled`; reservation released (the partial UNIQUE slot is free again); intent back to `requires_payment_method`; `payment_intent.payment_failed` emitted once | `test_s05_08_click_complete_5017_cancels` | 4.4 |
| 9 | **Click Complete with a wrong or missing `merchant_prepare_id`**; a bad `sign_string`; a Complete retried after success | **-6**; **-1**; **-4** (not 0) | No state change in any of the three | `test_s05_09_click_bad_prepare_id`, `test_s05_09_click_bad_sign`, `test_s05_09_click_complete_replay_4` | 4.4 |
| 10 | **Duplicate Click Prepare** for the same `merchant_trans_id` with a **new** `click_trans_id` (the buyer retried) | As decided in ADR-018: either the new Prepare supersedes a stale reservation (the old one is cancelled in the same transaction, and a late Complete for it gets -9), or the new Prepare is refused with a documented code | At no moment two `reserved` attempts for one intent; exactly one attempt can reach `succeeded`; the loser ends `canceled` and holds nothing | `test_s05_10_click_duplicate_prepare_one_completes` | 4.4, 4.5 |
| 11 | **Payme and Click in parallel for one order** (both started within milliseconds) | The second provider is refused at Check/Prepare time: Payme with a code from -31050..-31099 carrying a localized message and `data` naming the account field (or -31008, per ADR-018); Click with the code chosen in ADR-018, or -4 once the order is paid. If a second success slips through anyway, it is **accepted** (never an error after a debit) | The partial `UNIQUE(intent_id) WHERE state='reserved'` holds; at most one `succeeded` attempt per intent; a forced second success lands in a separate duplicate state and gets an automatic refund (Payme: an ops task to cancel from the cabinet; Click: a reversal) | `test_s05_11_parallel_providers_one_reservation`, `test_s05_11_second_success_auto_refund` | 4.5 |
| 12 | **Reconciliation drift and refused refunds**: (a) AtlasPay says state 1, Payme's records say 2 (your Perform response was lost and Payme staff resolved it by hand in the sim); (b) a Click reversal rejected because the payment is from last month, or UZCARD declined it | (a) The sim's nightly GetStatement shows the mismatch on Payme's side. (b) The sim's `/v2/merchant/payment/reversal` answers with an HTTP error | (a) A drift row in the reconciliation report, `recon_drift_rows > 0`, an alert, and a runbook entry for resolving it. (b) The refund goes to `requires_action` with a manual-refund task; the ledger does not pretend the money moved | `test_s05_12_recon_detects_manual_resolution`, `test_s05_12_click_reversal_rejected_manual_refund` | 4.9 |

Each scenario gets a short file under `docs/evidence/s05/scenarios/NN-<slug>.md`: the red output (what actually happened first), the fix in one sentence, and the green output.

---

### 4.1 provider-sim [14 h, must]

**Why this block exists.** You have no merchant contract, and without a peer that behaves like the real provider you would only ever test the happy path. The simulator is also your contract-test harness: if you ever get a real sandbox account, the same acceptance suite runs against test.paycom.uz and Click's Playground.

**What to build.**

1. `services/provider-sim`: FastAPI + SQLAlchemy 2.0 async + Alembic, on its own `sim` database on `pg-sim`. This is the first place your D1–D5 FastAPI work is reused. It is an *external* system: it never imports market or `atlaspay-domain` code, and it talks to market only over HTTP.
2. **Payme mode.**
   - Sends JSON-RPC 2.0 with `Authorization: Basic base64(Paycom:<key>)`, `Content-Type: text/json; charset=UTF-8`, 24-character hex transaction ids and 13-digit millisecond timestamps.
   - Sends every Create, Perform and Cancel **twice** by default. It compares the `result` (or `error`) members of the two replies byte for byte, and checks that each reply's `id` equals the `id` of the request it answers.
   - A chaos switch **retry with a new JSON-RPC id** (the [U] setting `payme.retry_reuses_rpc_id`, default `false`, the strict case), so a reply that replays the old envelope verbatim is caught.
   - A **fake clock** it controls through an admin endpoint (advance by N ms), which drives the 43,200,000 ms timeout.
   - Serves `/<base64(m=;ac.order_id=;a=)>` as a fake checkout page: decoding, a "Pay" button, a "Pay but fail the debit" button, then redirect to the `c=` return URL.
   - A nightly GetStatement call into your endpoint, compared with its own records (this is Payme reconciling *its* side against yours).
   - An export of its own records for a day, standing in for the Payme Business cabinet report [U]. Your reconciliation reads it in 4.9, because the Merchant API has no method *you* can call to fetch Payme's view.
   - An admin action "staff resolved this transaction by hand" that changes the sim's state without calling you (scenario 12a), and an admin action "merchant staff cancelled from the cabinet", which triggers CancelTransaction with reason 5.
3. **Click mode.**
   - Sends form-urlencoded Prepare and Complete with correct MD5 `sign_string` values, and can send wrong ones.
   - Runs all 15 Postman scenarios as scripts, including `error=-5017`, `amount=300` and `prepare_id=999999999`.
   - Serves `/v2/merchant/*`: checks `Auth: user:sha1(ts+secret):ts`, implements `payment/status_by_mti` and `payment/reversal` with the month rules and a "UZCARD declines" switch.
4. **Chaos switches** (per request or per scenario): drop the response *after* the merchant committed (the sim reads your reply, then pretends it never arrived and retries); delay; duplicate; send N copies concurrently; reorder (for example deliver a Cancel before the late second Perform).
5. **Every [U] fact becomes a setting** with the default you believe, documented in ADR-018: which timestamp starts the 12-hour clock; whether a Payme retry reuses the JSON-RPC `id`; Click's `amount` string format; the meaning of -5017; the second-Create error code (-31008 vs -31050); the reversal month's time zone.
6. **A request log.** The sim stores every request it sent and every reply it received (status, headers, raw body). Your evidence files and several assertions read from it.

**Pain-first.** None in this block: the simulator *is* the instrument that produces the pain in the next blocks. Record `docs/evidence/s05/sim-fidelity.md`: a table of each behaviour, whether it is [C] or [U], and the setting that controls it.

**Acceptance criteria.**

- The sim runs in Compose with a healthcheck, and a smoke script drives one Payme and one Click payment against a stub merchant that always answers success.
- A property of the sim itself is tested: the MD5 and Basic-auth headers it produces match hand-computed examples.
- Advancing the fake clock by 43,200,001 ms and then sending Perform is scriptable in one command.

### 4.2 Intents and idempotency [6 h, must]

**Why.** A PaymentIntent is the one object that follows a buyer's attempt to pay, across providers and retries. Idempotency makes "the client retried" harmless. You built a simple version in [Stage 02](stage-02-checkout-correctness.md); now it gets Stripe's exact semantics, because in S9 merchants will depend on them.

**What to build.**

1. **PaymentIntent state machine** in `libs/atlaspay-domain`. Illegal transitions raise and are never silently accepted (the P7 discipline: one test per illegal transition).

   | From | Event | To |
   |---|---|---|
   | (new) | market creates the intent for an order (amount, currency, order id, idempotency key) | `requires_payment_method` |
   | `requires_payment_method` | buyer picks Payme or Click; the redirect is built | `requires_action` |
   | `requires_action` | an attempt becomes `reserved` (Payme Create or Click Prepare succeeded) | `processing` |
   | `processing` | the attempt `succeeded` (Payme Perform or Click Complete with error 0) | `succeeded` |
   | `processing` | the attempt was `canceled` (timeout, failed debit, Click error < 0) | `requires_payment_method` |
   | `requires_payment_method`, `requires_action` | the intent is cancelled (order cancelled, hold expired: see ADR-020) | `canceled` |

   `succeeded` and `canceled` are final. Refunds are separate Refund objects, as in Stripe; the intent stays `succeeded`. Stripe allows cancelling only before `processing` or `succeeded` [C]; decide in ADR-020 whether you copy that rule, because it changes what the S4 hold sweeper may do.
2. **PaymentAttempt** per provider interaction, with a provider-neutral state machine:

   | Attempt state | Payme | Click |
   |---|---|---|
   | `reserved` | state 1 after Create | Prepare answered 0 |
   | `succeeded` | state 2 after Perform | Complete with `error=0` answered 0 |
   | `canceled` | state -1 (with the reason) | Complete with `error<0` answered -9, or superseded |
   | `refunded` | state -2 | reversal succeeded |
   | `duplicate` | a Perform for an intent that already succeeded through another attempt (should be impossible; reconciliation or a race can force it) | the same, for Complete |

   A `duplicate` attempt means money came in that the platform owes back: it always gets an automatic refund, and it never touches the intent's one `succeeded` attempt.

   Store the provider's own ids (Payme `params.id`; Click `click_trans_id` and `click_paydoc_id`) with a UNIQUE constraint on (provider, provider transaction id). You will need every id the provider sends when you call status and reversal endpoints later.
3. **The S2 idempotency store, generalized to Stripe semantics** (https://docs.stripe.com/api/idempotent_requests):
   - A result is stored **once execution starts, including 500s**. Validation failures before execution are not stored.
   - The same key with **different parameters** (a different request hash) is an explicit error, never a silently served cached response.
   - The same key while the first request is **still in flight** → **409**.
   - A replayed response carries `Idempotent-Replayed: true`.
   - Keys are retained **at least 24 hours**; a cleanup job removes older ones.
   - It applies to the port's state-changing operations (create intent, cancel intent, refund) and to the market HTTP endpoints that front them. Merchants' public `Idempotency-Key` header arrives in S9 and must map onto this unchanged.
4. **An injectable `Clock` port** in the domain. freezegun only freezes time inside one process; the acceptance suite runs two processes (sim and market), so market needs a clock you can set from a test-only admin hook.

**Pain-first.**

1. Run two identical "create intent" calls with the same key at the same moment, using the S2 barrier harness, **before** you add any in-flight handling.
2. Before you run it, predict and commit: the key claim is an `INSERT … ON CONFLICT DO NOTHING` inside the first request's still-open transaction. Does the second call fail at once, return at once, or wait? Does the answer change at the isolation level your S2 checkout actually uses (ADR-007)? Then run it at that level, and once at READ COMMITTED if that is not the one you use. Check your prediction in §16.
3. Record in `docs/evidence/s05/idempotency-in-flight.md` what you saw and how you turned it into a 409 without waiting. Guiding question: which Postgres lock function returns immediately with true or false instead of waiting for the lock?

**Acceptance criteria.** Tests: replay returns the stored status and body plus `Idempotent-Replayed: true`; a different body with the same key errors; concurrent same key gives exactly one execution and one 409; a handled 500 is replayed as the same 500; a key older than the retention window can be reused.

> If you are stuck: where does the key row commit relative to the business effects? If an exception happens halfway, what must be rolled back and what must survive so a retry sees the stored 500? (A savepoint is one tool.) Reread [P9](../python/09-payflow.md) D145–D149.

### 4.3 Payme adapter [7 h, must]

**Why.** This is where the HTTP 200 rule, the flowcharts and byte-for-byte replay stop being text and become code that a lost network packet cannot break.

**What to build.**

0. **The decision tables first.** Turn the official flowchart images (§4.0.1) into test tables, one row per branch, and commit them before any adapter code.
1. `/providers/payme/rpc` as a **plain Django view**, outside DRF: no DRF authentication, CSRF-exempt, no HTML error pages, no redirects, JSON-RPC errors always inside HTTP 200.
2. **Auth inside the adapter:** constant-time comparison of the Basic credentials, and an IP allowlist (a setting: Payme's 185.234.113.1–15 in production, the sim's address locally) returning -32504. Behind Nginx (S6) the client IP comes from a header only your proxy sets; decide now which one you will trust.
3. **The five flowcharts** from §4.0.1 (Check, Create, Perform, Cancel, CheckTransaction), each a function in the domain that returns a result or a Payme error code, with the Django view only translating.
4. **Replay the first result byte for byte, under the current id.** Store the exact bytes of the `result` (or `error`) member you sent the first time. On a replay, wrap those stored bytes in a new envelope that carries the **current** request's `id`: JSON-RPC requires the response id to equal the request id, and Payme does not document whether a retry reuses it [U]. Do not re-render the member: a re-render produces a new `perform_time` or a different key order.
5. **Raw callbacks as JSONB** in a `provider_events` table (columns sketch: provider, method, `payload` jsonb, a **generated** `provider_event_id` column, the exact response bytes in a text or bytea column, received_at, a duplicate counter) plus a GIN `jsonb_path_ops` index for support queries by `order_id` (P9 D151–D153). Build `provider_event_id` from the provider's method **and** its transaction id (Payme: `method || ':' || params.id`; Click: `action || ':' || click_trans_id`), with UNIQUE on (provider, provider_event_id). Payme reuses one `params.id` for Create, Perform, Cancel and every CheckTransaction of a transaction, and Click reuses `click_trans_id` for Prepare and Complete, so the provider id alone would make Perform collide with Create. Decide whether read-only calls (CheckTransaction, GetStatement) are logged at all, or logged without dedup, and write the choice in ADR-018. Test: a Create and then a Perform for one id store two rows.
6. **GetStatement** filtered on **Payme's** `time`, ascending, only transactions whose Create succeeded; tested with transactions created just inside and just outside the range.
7. Localized messages `{ru, uz, en}` for every error, and `data` naming the account field for -31050..-31099.

**Pain-first.**

1. **Let the framework answer first.** Mount the endpoint as a normal DRF view with the project's default authentication. Run the sim's Payme scenario. Observe what the sim records: a 401 or 403 for the Basic header DRF does not understand; a 415, because DRF's default JSON parser only accepts `application/json` and Payme sends `text/json`; an HTML 500 page when you raise inside the view with `DEBUG=False`; a 301 when the URL lacks its trailing slash. Every one of them becomes **-32400** on Payme's side. Record the list in `docs/evidence/s05/payme-32400.md`, then move the route out of DRF.
2. **Side effects inside Perform.** Temporarily send the confirmation email and call fulfilment synchronously inside Perform, with a delay injected in front of Mailpit (the S2 mail catcher) and the sim's response timeout shorter than that delay. Predict and commit: how many emails and fulfilment rows will one payment produce, and what will the sim record for the first Perform? Then run it, count emails and fulfilment rows, and look at what the sim's request log says about the first Perform and its retry. Your result depends on whether your Perform locks the attempt before its side effects; write down which case you hit and why (check your prediction in §16). Record the counts in `docs/evidence/s05/perform-side-effects.md`. Then fix it: Perform does one short transaction and everything else leaves through the outbox (inbox dedup from S4 makes consumers safe).
3. Turn scenarios **1, 2, 3, 5, 6 (Payme half) and 7** green.

**Acceptance criteria.** Payme sandbox scenario 1 (bad auth, bad amount from Check and Create, missing account, Check → Create ×2 identical → CheckTransaction, a new Create for a pending order → -31008, Cancel) and scenario 2 (Create, Perform ×2, Check, Cancel after Perform) pass against the sim with duplicates on, including the "retry with a new JSON-RPC id" switch. A replay test compares the `result`/`error` member byte for byte and asserts that the reply `id` equals the incoming request `id`.

> A trap to think about: JSONB normalizes whitespace and key order. What does that mean for "replay the first response byte for byte" if you stored the reply as JSONB?

### 4.4 Click adapter [4 h, must]

**Why.** Click has different replay rules, a different money format and a signature you can get subtly wrong. Keeping those differences inside the adapter proves the core is really provider-neutral.

**What to build.**

1. `/providers/click/prepare` and `/providers/click/complete` as plain views reading the **raw** form strings.
2. **MD5 over the raw received strings**, compared in constant time; -1 on mismatch.
3. **Money:** parse the soum amount with `Decimal` from the raw string, convert to integer tiyin, compare with the intent amount; -2 on mismatch. No float anywhere (your S1 "no float in money code" test must cover this module).
4. A repeated Complete on a paid payment returns **-4**; `error=-5017` (any negative `error`) → cancel the attempt, release the reservation, answer **-9**; a wrong `merchant_prepare_id` → **-6**; missing parameters → **-8**; an unknown order → **-5**.
5. A duplicate Prepare with a new `click_trans_id` for the same `merchant_trans_id`, handled per ADR-018 (scenario 10).

**Pain-first.**

1. Compute the MD5 over a **re-formatted** amount: `str(float(raw))`, `f'{Decimal(raw):.2f}'`, or the amount converted to tiyin and back to soums. Before you run, predict and commit which of the amounts `"1000"`, `"1000.00"` and `"1000.5"` will fail under each formatting. Then run the sim with those three amounts.
2. Record which ones give a false -1 (sign check failed on a correct request) and compare with your prediction (§16).
3. Record in `docs/evidence/s05/click-sign-raw-string.md`, then fix by signing the raw strings. Note: `str(Decimal(raw))` happens to round-trip all three strings. Why is relying on that still fragile?

**Acceptance criteria.** All 15 Postman scenarios green against the sim; scenarios 6 (Click half), 8, 9 and 10 green.

### 4.5 Cross-provider lock [1.5 h, must]

**Why.** A buyer can open Payme in one tab and Click in another. Without a database-level rule, both can reserve and both can charge.

**What to build.** A partial unique index `UNIQUE(intent_id) WHERE state='reserved'` on attempts, plus the intent-state check (an order already paid answers Payme's CheckPerform with an account error, and Click's Prepare with -4). Decide the exact codes in ADR-018.

**Pain-first.** Run scenario 11 with the index absent: fire a Payme Create and a Click Prepare for the same order concurrently. Observe two `reserved` attempts. Record it, add the index, and turn scenario 11 green.

**Acceptance criteria.** The concurrency test fires both providers 20 times in a loop; at most one reservation exists in every run.

### 4.6 Ledger [9 h, must]

**Why.** The ledger is where money is *true*. Everything else (intent states, order status, dashboards) is a claim about money; the ledger is the evidence. Double-entry bookkeeping means every movement is recorded as lines that debit some accounts and credit others by the same total, so errors show up as imbalance instead of hiding.

**What to build.**

1. **Accounts:** one connected account per vendor (`acct_…`), plus platform accounts. Decide the minimum set yourself and justify it in ADR-019; you will need at least: money the providers owe the platform (one clearing account per provider), the platform's balance, the platform's fee revenue, and each vendor's pending and available balances.
2. **`journal_entries` and `journal_lines`**, with an **`owner_account_id` on every entry** (the connected account the entry belongs to; this is the future shard key in [Stage 12](stage-12-data-at-scale-fraud.md), so put it in now), and **`balance_transactions`** that move from `pending` to `available` on an `available_on` date, modelled on Stripe balance transactions.
3. **A one-sided CHECK on lines:** exactly one of debit or credit is non-zero, both are non-negative.
4. **A `DEFERRABLE INITIALLY DEFERRED` constraint trigger** enforcing Σdebit = Σcredit per entry, checked at COMMIT.
5. **Append-only:** `BEFORE UPDATE OR DELETE` triggers that raise on `journal_entries` and `journal_lines`, plus `REVOKE UPDATE, DELETE` from `market_app`. Corrections happen only by posting a reversing entry.
6. **Running balance** with a window function over a covering index, and **`trial_balance_mv`** refreshed `CONCURRENTLY` (it needs a unique index), with an `as_of` exposed.
7. **`rebuild_balances`**, a management command that recomputes every balance projection from the journal and proves it matches the live values **bit for bit** (for example by comparing checksums). The ledger is event-sourced: the journal is the source of truth, balances are derived.
8. **A streaming CSV statement** per connected account, built on a generator and a server-side cursor, with flat RSS proven at 1M lines.

**Pain-first.**

1. **Float commissions** (P6 D91–D93). On a scratch branch, compute commission as `amount * rate` with a float rate, post a worldgen month of orders, run the trial balance. Observe it is off by a few tiyin. Your S1 no-float test should catch this at CI time: disable it on the branch to see the runtime symptom, then re-enable it. Record the drift in `docs/evidence/s05/float-drift.md`.
2. **CHECK is not enough.** Add only the CHECK first. From `psql` as the migrator, insert an entry with one debit line and no credit. Before you COMMIT, predict and commit your prediction: will it commit? Then COMMIT and record what happened. Then add the constraint trigger, repeat, and confirm the COMMIT now fails with `check_violation`. Record both outputs in `docs/evidence/s05/check-vs-trigger.md` (this corrects the P6 claim that a CHECK can enforce balance).
3. **Tamper.** From `psql`, try `UPDATE journal_lines SET …` and `DELETE` as the app role and as the owner. Both direct statements must be refused. Then write down, for the threat model, what the owner or a superuser could still do to get around the triggers.

**Acceptance criteria.** A Hypothesis `RuleBasedStateMachine` performs random sequences of charges, transfers, refunds, reversals and payouts and asserts the trial balance is 0 after every step. `rebuild_balances` matches. The statement endpoint streams 1M lines with RSS recorded at start, middle and end in `docs/evidence/s05/statement-rss.csv`. ADR-019's posting p95 with and without the constraint trigger is an ADR-002 measurement: 2 configurations × 3 runs, about 40 minutes of unattended run time at 5-minute runs plus warm-up. Schedule it in the weekend block.

> Guiding questions: what does `DEFERRABLE INITIALLY DEFERRED` change about *when* the check runs, and why is that the only way a multi-row rule can work? Do your row triggers catch `TRUNCATE`? What happens to server-side cursors when a transaction-mode pooler sits in front of Postgres (you will meet this in [Stage 10](stage-10-kubernetes-grpc-inventory.md))?

### 4.7 Connect [3 h, must]

**Why.** One cart, many vendors, one payment. Stripe's model for exactly this is **separate charges and transfers**: the charge lands on the platform, then the platform transfers each vendor's share to their connected account and keeps its application fee. With this model, **refunds do not reverse transfers automatically**; the platform must reverse them itself [C] (https://docs.stripe.com/connect/separate-charges-and-transfers).

**What to build.**

1. On a succeeded intent: one charge entry, then one transfer per vendor group, where **transfer = group total − application fee**, and the fee comes from the S1 commission schedule valid at the order's time.
2. On a partial refund: reverse transfers and refund fees **proportionally**, rounded with the **largest-remainder** method so the parts sum exactly to the refund.
3. Refunds never exceed the captured amount; many partial refunds are allowed.

A worked example (numbers only; the posting lines are yours to design): an order of 250,000 tiyin has group A of 150,000 at 10% commission (transfer 135,000, fee 15,000) and group B of 100,000 at 8% (transfer 92,000, fee 8,000). Transfers plus fees equal 250,000. A refund of 50,000 on group A reverses 45,000 of A's transfer and 5,000 of A's fee. Now try a refund of 10,001 on the whole order: the proportional parts are not whole tiyin. Largest remainder decides who gets the extra tiyin, deterministically.

**Pain-first.** The float drift in 4.6 is this block's pain too: run the split with float rounding first and let Hypothesis find a case where the parts do not sum to the whole.

**Acceptance criteria.** Hypothesis properties: Σtransfers + Σfees = charge; every part ≥ 0; Σrefunds ≤ captured; after any refund sequence the trial balance is 0.

### 4.8 Payouts [3 h, must]

**Why.** Paying a vendor is where concurrency meets money: a payout and a refund can both read the same available balance and both decide there is enough.

**What to build.** A daily Beat job (Celery queue `beat-jobs`) that pays each vendor their available balance. The exactly-once guarantee is a UNIQUE run key `(vendor_id, payout_date)` on the payout record (the S4 run-key pattern), which makes a second run for the same day a no-op. `pg_try_advisory_xact_lock` per vendor is used in addition, so a concurrent scheduler skips the vendor instead of waiting on the unique index. A transaction-level advisory lock is released at COMMIT, so on its own it stops two schedulers paying one vendor at the same moment, but not one after the other. A payout moves money from the vendor's available balance to a payout record and emits `payout.paid` or `payout.failed`. There is no bank; the payout is simulated.

**Pain-first.**

1. Reproduce the **write skew**: a payout and a refund on the same vendor run concurrently at the default isolation level, each reads the available balance, each subtracts, both commit.
2. Observe the vendor's available balance go negative.
3. Record it in `docs/evidence/s05/payout-write-skew.md`, then fix it with either row locks on the vendor's balance or SERIALIZABLE plus your S2 retry decorator. Write down which you chose and why (P4 D67–D71 is the reading).

**Acceptance criteria.** The concurrency test repeats payout-vs-refund 20 times; the balance never goes negative; two schedulers started together, **and** a second scheduler started after the first has finished, each result in every vendor being paid exactly once per `payout_date`.

### 4.9 Reconciliation [4 h, must]

**Why.** Your database is only your opinion. Providers can resolve transactions by hand, responses get lost, and a bug can post the wrong amount. Reconciliation compares your records with the provider's, every night, and makes every difference visible.

**What to build.**

1. **Payme.** Your GetStatement endpoint is what Payme uses to reconcile *its* side against yours; the sim calls it nightly and compares. For *your* side you also need Payme's view of the day: in the sim this is an export of its records, standing in for the Payme Business cabinet report (the Merchant API documents no merchant-initiated statement method [U]; record this assumption in ADR-018).
2. **Click.** Call `payment/status_by_mti` for each of the day's `merchant_trans_id` values, through an **outbound token bucket** (E10: outbound calls to providers are paced by a token bucket in redis-state, and queued and delayed rather than dropped).
3. **The comparison:** a `FULL OUTER JOIN` of the provider rows against your attempts and journal, reporting every row that exists on one side only or differs in state or amount. Export the count as `recon_drift_rows` and alert when it is above 0.
4. **Index choice:** measure BRIN vs B-tree on `provider_events(created_at)` for the nightly range query (size and plan), and keep the winner (P4 D67–D71).
5. **The Click reversal client** (`DELETE payment/reversal/...`) behind the same token bucket, with a **manual-refund fallback** when the reversal is rejected (last month's payment, or UZCARD declined).

**Pain-first.** Scenario 12: drop a Perform response, let the sim's "staff" resolve it by hand, run the nightly job, and see the drift row appear. Then reject a reversal and see the refund go to manual handling. Record both in `docs/evidence/s05/recon-drift.md`.

**Acceptance criteria.** On a clean seeded day the report has 0 rows. Injected drift is flagged and alerts. `docs/design/reconciliation.md` describes the sources, the join, the drift categories and who resolves each (phase-8 D241–D243 is a useful model for the scheduled-report shape).

*Degrade option #15 (see [schedule-and-cuts](schedule-and-cuts.md)):* if you are behind, the Click reversal client shrinks to a manual-refund runbook (saves 1 h).

### 4.10 Hold and long transactions [2 h, must]

**Why.** Payme gives a transaction 12 hours; your stock hold lasts 30 minutes. And any outbound network call made while a database transaction is open holds that transaction's locks for as long as the network takes.

**What to build.** Write **ADR-020: the 30-minute stock hold vs Payme's 12-hour window.** Decide what happens when Perform arrives after the hold expired (scenario 4), and implement it. The options you must weigh at least: keep holds for intents in `processing` up to the provider's window; refuse late payments before any money moves; accept the payment and handle unfulfillable stock with a refund.

**Pain-first.**

1. Make one outbound provider call **inside** `transaction.atomic()`: for example the Click reversal, with the sim's delay switch set to 10 seconds.
2. Predict and commit first: what state will `pg_stat_activity` show for that session, which locks will it hold, and what happens to a concurrent payout for the same vendor? While the call waits, look at `pg_stat_activity` and `pg_locks`, and start that payout. If your S2 `idle_in_transaction_session_timeout` is set, keep watching until it fires. Check your prediction in §16.
3. Record the snapshot in `docs/evidence/s05/idle-in-tx.md`. Then restructure: commit the intent to refund plus an outbox row, call the provider from a worker after commit, record the result in a second short transaction.

**Acceptance criteria.** Scenario 4 green according to your ADR. A test asserts no provider HTTP call happens while a transaction is open (for example by making the HTTP client fail if `connection.in_atomic_block` is true).

### 4.11 Port [1.5 h, must]

**Why.** market must not know how payments works inside, so that in S9 the whole module can move behind HTTP without market changing.

**What to build.** A `PaymentsGateway` Protocol in market (create intent, get intent, cancel intent, refund) with an in-process adapter calling the payments module. Payment state changes leave through the outbox as `payment_intent.succeeded`, `payment_intent.payment_failed`, `payment_intent.canceled`, plus `payment_attempt.created`, `refund.*`, `transfer.*` and `payout.*`, using the S4 envelope. market's ordering module consumes them from `market.payment-events` through the S4 inbox (dedup on event id) and marks the order paid. This queue lives from S5 to S8 only: in S9, ordering's consumer is replaced by a receiver for signed AtlasPay webhooks that writes to the same inbox table, and the queue is unbound and deleted in the contract step. The import-linter contract from S4 forbids ordering from importing anything in payments except its `api`.

**Acceptance criteria.** An end-to-end test: checkout → intent → sim Payme checkout → Perform → `payment_intent.succeeded` → order `paid` → transfers and fees posted → trial balance 0. A fake `PaymentsGateway` lets ordering's unit tests run without payments.

### 4.12 Drills + SD18 [5 h, must]

One hour a week for five weeks: one SQL problem on the Atlas schema (this stage: the running balance, the trial balance, the reconciliation FULL OUTER JOIN) or one DSA problem, plus the week's interview questions out loud. In W23, the drill hour is the SD18 session (§9).

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| At most one succeeded attempt per intent | Partial unique index on attempts `WHERE state='succeeded'`; a forced second success goes to a separate duplicate state with an automatic refund | `test_s05_11_second_success_auto_refund`; the parallel-providers loop |
| At most one reserved attempt per intent | Partial `UNIQUE(intent_id) WHERE state='reserved'` | `test_s05_11_parallel_providers_one_reservation` |
| Replies to a repeated provider request are deterministic and follow each provider's replay rule | Payme: wherever the official flowchart calls for a replay, the stored first `result`/`error` bytes are returned in an envelope carrying the current request's `id` (other states answer as the flowchart says, for example -31008); Click: a repeated successful Complete is always -4; both rules live in the adapters | Scenarios 1, 5 (replay), 9; the replay test (member bytes + `id` match), also with the "new JSON-RPC id" switch |
| Every money movement is balanced | Deferred constraint trigger at COMMIT, plus service-layer validation for a good error message | `test_ledger_psql_unbalanced_commit_fails`; the state-machine test |
| The ledger is append-only for the runtime roles (`market_app`; the owner role is never used at runtime) | `BEFORE UPDATE OR DELETE` triggers; REVOKE on `market_app`; corrections by reversal only. The owner or a superuser can still disable triggers: see the threat model for detection | `test_ledger_psql_tamper_refused` (in `sql-invariants`) |
| Σ transfers + fees = the charge; refunds ≤ the captured amount | Split math in the domain with largest-remainder rounding; refund guard | Hypothesis split properties |
| Money is integer tiyin | `Money` value object and `MoneyField` from S1; Click amounts parsed with Decimal from the raw string | The S1 no-float test extended to payments; scenario 6 |
| Callbacks do one short transaction, with no outbound call inside it | Callback handlers commit state + journal + outbox and answer; outbound calls run in workers after commit | The "no HTTP inside atomic" guard test; the perform-side-effects test |
| Payme endpoints always answer HTTP 200 JSON | Plain view with a catch-all translating exceptions to -32400 | `test_s05_07_payme_never_non200_or_html` |
| Balances can be rebuilt from the journal | `rebuild_balances` | `test_rebuild_balances_bit_for_bit` |
| Drift is 0, or it raises an alert | Nightly reconciliation + `recon_drift_rows` alert | `test_s05_12_recon_detects_manual_resolution`; clean-day test |

---

## 6. Tests to write

1. **The acceptance suite** (`sim-acceptance`): Payme sandbox scenarios 1–2, Click's 15 Postman scenarios and the 12 failure scenarios in §4.0.3, run against the Compose stack with the chaos switches (duplicate, drop after commit, delay, concurrent, reorder, new JSON-RPC id on retry).
2. **freezegun plus the injectable clock** for the 12-hour timeout on both sides.
3. **A Hypothesis `RuleBasedStateMachine`** keeping the trial balance at 0 across any sequence of charges, transfers, refunds, reversals and payouts.
4. **Split-math properties:** sums, non-negativity, refund caps, deterministic rounding.
5. **Concurrency:** duplicate callbacks at the same moment; parallel providers; payout vs refund; two payout schedulers. Reuse the S2 barrier harness.
6. **The psql tamper test:** unbalanced entry fails at COMMIT; direct UPDATE and DELETE refused as `market_app` and as the owner.
7. **An LSP contract suite:** one set of contract tests that every implementation of a domain port must pass: the in-memory fake and the Django repository for the ledger and the idempotency store, the real and fake `Clock`. If the fake passes and the real one fails, one of them is not a valid substitute.
8. **Idempotency semantics** (§4.2) and **state-machine illegal transitions** (one test each).
9. **Streaming statement:** RSS stays flat and the first byte arrives before the last row is read.

---

## 7. CI changes

| Job | What it gates |
|---|---|
| `provider-sim` image build | The simulator builds, passes its own unit tests and ships as an image the other jobs use |
| `sim-acceptance` | Brings up the Compose stack (market, provider-sim, Postgres, RabbitMQ, redis-state) and runs the full acceptance suite with chaos on. A red scenario blocks the merge |
| `sql-invariants` | Runs raw-SQL checks as each DB role: unbalanced COMMIT fails, tamper refused, reconciliation returns 0 rows on a clean seed, the integrity-audit queries return 0 rows |
| Path filters (monorepo) | Start here: changes under `services/provider-sim/**`, `libs/atlaspay-domain/**` or the payments app trigger the payments jobs; unrelated changes skip them |
| import-linter | Extended: `libs/atlaspay-domain` may not import django, rest_framework, fastapi or sqlalchemy |

See [testing-and-ci](testing-and-ci.md) for the full matrix.

---

## 8. ADRs and documents

**ADR-017 AtlasPay domain.**
- Questions: what are an intent, an attempt, a refund, a transfer and a payout, and who owns each? Which Stripe concepts did you copy, and which did you drop (`requires_confirmation`, `requires_capture`)? What are the idempotency semantics and retention?
- Numbers: the retention window and the estimated table size at worldgen volume; the count of states and legal transitions.
- **Legal note (required):** under ЗРУ-578 "О платежах и платежных системах", Art. 15, providing payment services in Uzbekistan without a Central Bank licence is prohibited (except payment agents and sub-agents), and Art. 14 lists processing electronic payments as a payment service (https://lex.uz/docs/4575788). A real AtlasPay that collects and holds sellers' money would need a licence, or would use the providers' own splits (Payme `receivers`, Click Split Shop). This is a learning project with simulated money. Not legal advice.
- Counter-argument: "Why build an operator at all? market could integrate Payme and Click directly." Hint: argue from the four money jobs in §1 and what two direct integrations would leave undone, then use the legal note to say what a real company would do instead.

**ADR-018 Adapter contract and simulator fidelity.**
- Questions: what does the domain expect from any provider adapter? Which behaviours does the sim reproduce, marked [C] or [U]? What does it deliberately not reproduce (real card processing, Payme's undocumented retry schedule and response deadline)? Does a Payme retry reuse the JSON-RPC `id`, and what does your replay do if it does not? Which codes answer the cross-provider conflict and the duplicate Click Prepare? Which calls does `provider_events` log, and with what dedup key? Where does "Payme's view" for your reconciliation come from?
- Numbers: scenario counts (2 Payme sandbox, 15 Click, 12 failures), the chaos-run results, every [U] default.
- Counter-argument: "A pytest mock would be enough." Hint: argue from `docs/evidence/s05/sim-fidelity.md` and the scenario files under `docs/evidence/s05/scenarios/`: which of those red runs could a mock have produced?

**ADR-019 Ledger and Connect model.**
- Questions: chart of accounts; posting rules for charge, transfer, fee, refund, transfer reversal and payout; why separate charges and transfers rather than destination or direct charges; why a deferred trigger; how corrections work.
- Numbers: the float drift you measured; posting p95 with and without the constraint trigger; `trial_balance_mv` refresh time vs the live GROUP BY at 1M lines; `rebuild_balances` time; statement RSS.
- Counter-argument: "Use the providers' native splits and skip your own ledger." Hint: argue from `docs/evidence/s05/recon-drift.md` and the Connect refund cases: which of them would native splits handle for you? Then weigh the legal note honestly.

**ADR-020 Hold vs provider window.**
- Questions: what happens to stock between Create and Perform? May an intent in `processing` be cancelled? What reply does a late Perform get, and why is that safe for the buyer's money?
- Numbers: the distribution of Create→Perform delay in your simulated traffic; the share of payments that would outlive a 30-minute hold; stock-hours locked under each option; the `idle in transaction` evidence from 4.10 (`docs/evidence/s05/idle-in-tx.md`).
- Counter-argument: "Just hold stock for 12 hours." Hint: argue from the stock-hours number in this ADR's own table.

**Threat model v1** (`docs/design/threat-model.md`): a leaked Payme kassa key; forged callbacks (IP allowlist + Basic auth; Click MD5 with a shared secret); an edited `a=` in the checkout URL (base64 is encoding, not a signature, so Check and Create must verify the amount); replayed old Click requests; an insider editing the ledger (the owner role or a superuser can disable the append-only triggers, for example with `ALTER TABLE … DISABLE TRIGGER` or `session_replication_role = replica`; mitigations: the owner is never used at runtime, an event trigger or a `log_statement = 'ddl'` alert on trigger changes, and detection through the nightly `rebuild_balances` checksum and reconciliation); secrets readable by every market process (the S6 split gate will count them). Each with a mitigation or an accepted risk.

**`docs/design/reconciliation.md`**: sources, schedule, join, drift categories, alert, resolution runbook.

---

## 9. System design session

**SD18 — Design a payment system** ([system-design-problems.md](../../system-design-problems.md)). **Built**, in W23; it returns as the payments deep-dive in mock #2 ([B2](buffers-and-job-sprint.md)) and is extended in S9.

1. Whiteboard first, 45 minutes, no notes: a Stripe-style payment system with idempotency keys, a double-entry ledger as the source of truth, and reconciliation that catches a payment you think succeeded while the provider's records disagree days later.
2. Then diff your whiteboard against what you built: where did the real protocols (provider-calls-you, HTTP 200, 12-hour window, -4 vs replay) force something your whiteboard missed?
3. Reuse from Atlas: the acceptance table, the ledger schema, the reconciliation join, ADR-020.
4. Write `docs/sd/sd18.md` with the diff.

---

## 10. Interview questions this stage lets you answer

- Walk me through a Payme payment and every retry it can produce.
- Why does Payme require HTTP 200 on errors? What happens if your framework returns a 401?
- What do you store for idempotency, and when? Why does Stripe answer 409 to a concurrent duplicate while your Payme adapter waits and replays?
- Why a deferred trigger? Why can a CHECK constraint not enforce "the entry balances"?
- How do refunds reverse transfers? Show me the rounding.
- How does reconciliation catch a transaction Payme staff resolved by hand?
- How do you stop an order being paid through both providers?
- Why integer tiyin? Show me the float bug you hit.
- How do you correct a mistaken journal entry?
- A payout and a refund run at the same time on the same vendor. What goes wrong, and what did you choose to prevent it?
- Materialized view or Redis cache for the trial balance? They both hold stale data.
- How do you export a million ledger lines without running out of memory?
- Why is your payment core framework-free, and what will that buy you later?

---

## 11. Common mistakes to watch for

1. **Float money anywhere**, including a float commission rate "just for the multiplication" (P6 D91–D93).
2. **Claiming the database enforces balance with a CHECK.** A CHECK sees one row, so it cannot compare an entry's lines (P6 D91–D93 claimed otherwise; your §4.6 check-vs-trigger evidence shows it).
3. **Letting the framework answer Payme:** DRF auth (401/403), the JSON parser (415 on `text/json`), CSRF, the HTML 500 page, `APPEND_SLASH` redirects. Each becomes -32400.
4. **Re-rendering a replay** instead of returning the stored bytes, storing the reply as JSONB and re-serializing it, or replaying the whole old envelope with the first request's JSON-RPC `id`.
5. **Slow or outbound work inside a callback transaction:** email, fulfilment, a Click API call.
6. **Signing a re-formatted Click amount**, or parsing it with float.
7. **Answering Click Complete with an error after the card was debited** (only -4 and -9 are allowed), which pushes the payment into manual investigation.
8. **"If exists, then insert"** instead of a UNIQUE constraint, which loses the race (P9 D145–D149).
9. **Editing or deleting ledger rows** instead of posting a reversal.
10. **Copying an official sample** (the Click Django sample and the Payme PHP template both have bugs; see §4.0.2).
11. **Trusting the checkout URL's amount**, or measuring the 12-hour timeout from a timestamp you never decided on.

---

## 12. How real companies differ

- **They start from a contract and a sandbox.** A real integration runs against test.paycom.uz with a TEST_KEY and Click's Playground with a real `service_id`. Your acceptance suite is written so it can be pointed at them unchanged.
- **They rarely hold sellers' money themselves.** In Uzbekistan that is a licensed activity (ЗРУ-578 Art. 15); a real marketplace would more likely use Payme `receivers` or Click Split Shop, or a licensed payment company. Building the ledger yourself is still the right learning version, because the ledger reasoning is what interviews test and what native splits hide from you.
- **Reconciliation is partly a human workflow.** Real teams reconcile against provider settlement reports and bank statements, and finance staff resolve drift. Your nightly job and runbook are the automated half of that.
- **The ledger often stays inside payments.** Some companies split it into its own service or database; that is the most debatable split in Atlas ([Stage 12](stage-12-data-at-scale-fraud.md)).
- **Card data never touches them.** Providers own card numbers and the platform keeps tokens, which keeps PCI scope small. You never see a card number at all.

---

## 13. Deliberately not doing

| Item | Why not now | When it arrives |
|---|---|---|
| Merchant API keys, signed outbound webhooks, the per-key limiter, Vault | They only make sense once a process boundary exists between AtlasPay and its merchants | [Stage 09](stage-09-strangler-atlaspay-auth.md) |
| Disputes | Neither Payme nor Click has a dispute protocol | Whiteboard only (stretch) |
| Raw card data | PCI scope; providers own card numbers | Never; a PCI note in the threat model |
| Real provider sandboxes | No merchant contract | Re-run the same suite if an employer account appears |
| Fraud scoring | Needs time-series velocity features first | [Stage 07](stage-07-polyglot-mongo-timescale.md) (shadow), [Stage 12](stage-12-data-at-scale-fraud.md) (served) |
| Extracting payments into its own service | No measured forcing problem yet | Measured in [Stage 06](stage-06-ship-and-operate.md), done in [Stage 09](stage-09-strangler-atlaspay-auth.md) |

---

## 14. Stretch

Only if the must tier closes early.

- **Payme Subscribe API card tokens and test-card behaviours in the simulator [2 h].** The direction is reversed (you call Payme: `cards.create`, `cards.verify`, `receipts.create`, `receipts.pay`); `receipts.pay` then triggers Check, Create and Perform on your server. Emulate Payme's test cards (all expire 03/99, SMS code 666666), including the "10-second delay, then error" card.
- **SetFiscalData [1 h].** Accept fiscal receipt data for PERFORM and CANCEL, with its own error codes.
- **A design using `receivers` / Split Shop [1 h].** Write how Atlas would look if the providers split the money natively, and what your ledger would still need to do.
- **A promo-abuse rule [1 h].** One rule on top of S2 promotions, fed by payment attempts.
- **Disputes whiteboard [1 h].** Stripe's dispute lifecycle and what a marketplace would need without provider support.

---

## 15. Definition of done

- [ ] A buyer pays end to end: intent → simulated Payme checkout → Perform → order `paid` → transfers and fees posted → trial balance 0. The same works through Click.
- [ ] The chaos run is green: Payme sandbox scenarios 1–2, Click's 15 and the 12 failure scenarios, each with its red-then-green evidence file under `docs/evidence/s05/scenarios/`.
- [ ] An injected drift is flagged by reconciliation and fires the alert.
- [ ] The psql tamper test and the unbalanced-COMMIT test pass in `sql-invariants`.
- [ ] `rebuild_balances` reproduces balances bit for bit; the statement streams 1M lines with flat RSS.
- [ ] ADR-017 (with the legal note), ADR-018, ADR-019 and ADR-020 merged, each with its numbers and counter-argument; threat model v1; `docs/design/reconciliation.md`.
- [ ] `docs/sd/sd18.md` with the whiteboard-vs-built diff.
- [ ] Two STAR stories in `docs/star/`: **the lost Perform response** and **the float drift**.
- [ ] A postmortem paragraph for the stage: what took longer than budgeted, which [U] fact surprised you, what you would do differently.
- [ ] `docs/deferred.md` re-read and updated.
- [ ] Git tag `v0.5`.

---

## 16. If you get stuck

- **provider-sim.** Ask yourself: what is the smallest thing that can *send* a Payme request and *record* the reply? Build that, then add duplication, then the clock, then the chaos switches. Reuse your D1–D5 FastAPI + async SQLAlchemy setup.
- **Intents and idempotency.** Draw the two state machines on paper first, with every arrow labelled by the provider event that causes it. What must be in the same transaction as the key row? Reread [P9](../python/09-payflow.md) D145–D149 and D151–D153.
- **Payme adapter.** Take one flowchart at a time and write its test table before its code. If a replay test fails, print both replies as bytes and diff them. Which layer of Django touched the request or response before your view did?
- **Click adapter.** Print the exact string you are hashing next to the one the sim hashed. Are they the same characters?
- **Cross-provider lock.** Which state should the partial index cover so that it frees itself when an attempt fails?
- **Ledger.** Start from one example order and write its journal lines by hand before writing any posting code. If the trigger fires when it should not, check whether it runs per row or at commit. Reread [P6](../python/06-ledgerbase.md) D91–D96.
- **Connect.** Do the 10,001-tiyin refund by hand with largest remainder. Then write the property test before the function.
- **Payouts.** Can you reproduce the negative balance reliably with a barrier? If not, the test is not proving anything yet. Reread [P4](../python/04-wareflow.md) D67–D71.
- **Reconciliation.** Write the FULL OUTER JOIN against two tiny hand-made tables first. What distinguishes "missing on our side" from "missing on theirs" in the result?
- **Hold vs window.** List what the buyer, the vendor and the platform each lose under each option, in money and in stock-hours.
- **Port.** Could ordering's tests run if the payments app were deleted? If not, the port is leaking. Reread [P10](../python/10-atlasmarket.md) D163–D165 for the one-payment-many-groups flow.

<details>
<summary>Check your prediction (open only after you committed yours and ran the exercise)</summary>

- **4.2, concurrent same key.** At READ COMMITTED the second `INSERT … ON CONFLICT DO NOTHING` does not fail: it waits on the first transaction's uncommitted unique-index entry, and once the first commits it sees the conflict and inserts nothing (if the first rolls back, it inserts). At REPEATABLE READ or SERIALIZABLE, once the first commits, the waiting insert gets 40001 ("could not serialize access due to concurrent update") because the conflicting row is outside its snapshot; your S2 retry decorator then re-runs the request, which now replays. Either way the duplicate is stuck for as long as the first transaction is open, which is why Stripe answers 409 instead of waiting.
- **4.3, side effects inside Perform.** If your Perform locks the attempt before its side effects, the sim's retry blocks on that lock until the slow first Perform commits, then sees state 2 and replays: one email, but the first Perform timed out on the sim's side (money debited, your reply lost). If it does not lock first, both copies run the side effects: two emails and two fulfilment rows.
- **4.4, signing a re-formatted amount.** `str(float(raw))` turns `"1000"` and `"1000.00"` into `"1000.0"`, so both give a false -1. `f'{Decimal(raw):.2f}'` turns `"1000"` into `"1000.00"` and `"1000.5"` into `"1000.50"`. The tiyin round trip turns `"1000.00"` into `"1000"`. Every re-format fails for some string Click might send. `str(Decimal(raw))` round-trips these three, but it is still parse-and-print: a `normalize()`, a `quantize()` or another library breaks it, and the format is not documented.
- **4.6, CHECK is not enough.** It commits. A CHECK is evaluated on the one row being written, so a one-line entry satisfies every CHECK. Only a rule evaluated at COMMIT over all of the entry's lines, the deferred constraint trigger, can refuse it.
- **4.10, a network call inside a transaction.** `pg_stat_activity` shows the session `idle in transaction`: it waits on the network, not on Postgres, and keeps its row locks. The concurrent payout for that vendor blocks for the whole delay. `idle_in_transaction_session_timeout` kills the session, which rolls back everything the transaction had written.

</details>

<details>
<summary>Check your findings: the official samples review in §4.0.2 (open only after you wrote your own list)</summary>

- Click `click/utils.py`: an `isset()` with inverted logic, so the -8 check fires only when *every* parameter is missing.
- `abs(float(amount) - float(order.total) > 0.01)`: the parenthesis is in the wrong place, and the comparison uses float money.
- `merchant_prepare_id` is set to the order id, so no transaction row is ever stored.
- No locking between Prepare and Complete.
- `error` is returned as a string.
- Payme PHP template: the time check on a new transaction looks inverted (`paycom_time - now >= TIMEOUT`).

</details>
