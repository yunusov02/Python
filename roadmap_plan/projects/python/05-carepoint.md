# Project 5 — CarePoint

**Clinic appointment & patient records system — the first real service split**

| | |
|---|---|
| Domain | Healthcare |
| Level | Middle |
| Phase | 4 — Microservices & Infrastructure |
| Weeks | 14–15 (D79–D90) |
| Stack | FastAPI (auth-service, **OAuth2/OIDC**, **RS256 + JWKS**), Django/DRF (clinic-service), PostgreSQL + `btree_gist`, Redis, Celery Beat, **Nginx**, **MinIO/S3**, **Keycloak** (local IdP), **React + TS + Vite + TanStack Query**, Docker Compose, GHCR |
| Repo | `carepoint/` + `carepoint-web/` |

> **Three lessons, all structural.** First: what a service split actually costs,
> learned with two services rather than ten. Second: let the *database* enforce
> the thing that must never happen, instead of hoping application code wins a race.
> Third: this is **the auth project** — `auth-service` exists, so OAuth2/OIDC,
> asymmetric keys with rotation, and a real browser-facing security posture
> (CORS, headers, login protection) land here and are reused by every later service.

---

## 1. Business Problem

A small clinic needs patients to book appointments online, staff to manage a daily
schedule per doctor, and doctors to attach documents (lab results, scans) to a
patient's record securely — currently juggled across a paper diary and emailed PDFs.

---

## 2. Outcomes — what exists when the project is finished

**A working system**
1. Two independently deployable services behind one Nginx entrypoint
2. JWTs issued by `auth-service` and validated **locally** by `clinic-service`,
   with no network call per request — signed **RS256**, public keys published at
   `/.well-known/jwks.json`, **rotated** with a `kid` and proven by rotating live
2a. **OAuth2 Authorization Code + PKCE** — patients log in with an external
   identity provider (Google, or a local Keycloak in Compose), and `auth-service`
   exchanges the code, verifies the IdP's ID token, and issues its own tokens
2b. Refresh-token **rotation and revocation** (logout actually logs out)
3. Appointment booking where double-booking is refused **by a Postgres constraint**
4. Patient documents uploaded and downloaded via presigned URLs — bytes never
   pass through the API process
5. A Redis-cached doctor schedule with correct invalidation
6. A 24h reminder job on Celery Beat
7. `carepoint-web/`: the first React/TS app, showing a doctor's daily schedule
8. CI building and pushing images for both services to GHCR

**Proof it is correct**
9. A concurrency test firing two identical bookings — exactly one survives, and
   the rejection comes from the database
10. A test that an expired presigned URL is refused
11. `/health` on each service failing when its dependency is down
12. `carepoint-web` works from a different origin because **CORS** is configured
    deliberately (no `*` with credentials), and every response carries security
    headers (`HSTS`, `X-Content-Type-Options`, `X-Frame-Options`, a starter CSP)
13. `/auth/login` protected against brute force (rate limit + lockout/backoff), and
    a test that a wrong password and an unknown email produce the *same* response
14. Appointment times are `timestamptz`; a **DST test** proves a 09:00 slot on the
    change-over day is still 09:00 clinic time
15. One `X-Request-ID` flows Nginx → auth-service → clinic-service → Celery and
    appears in every log line

**Written artefacts**
12. `docs/scaling-notes.md` — why `auth-service` might scale independently. If you
    cannot write this convincingly, the split was not justified

---

## 3. Scope

**In scope**
- Appointment booking with DB-enforced conflict prevention
- Patient records
- Secure document attachment via presigned URLs
- 24h appointment reminders
- Redis-cached doctor schedules
- A two-service split behind Nginx
- The first React/TS frontend

**Out of scope — named, not built**

| Deferred | Why |
|---|---|
| Service-to-service mTLS | Named; the trust model here is **asymmetric JWT** (clinic-service holds only public keys), and you should be able to say what mTLS would add on top |
| Being a full OAuth2 *authorization server* for third parties | You are an OAuth2 *client* to an IdP and issue your own first-party tokens. Issuing tokens to third-party apps (client registration, consent screens, scopes) is named, not built |
| Doctor availability rules (recurring schedules) | Real feature, no new lesson |
| Waitlist for cancelled slots | Same |
| A synchronous cross-service *write* | Deliberately absent. LedgerBase provides the first one, and it is the first to need resilience patterns |

---

## 4. Roles & Permissions

| Role | Can | Cannot |
|---|---|---|
| **`patient`** | Book an appointment in an open slot, view and cancel **own** appointments, view **own** documents | See any other patient's data; see internal notes; upload to another patient's record |
| **`receptionist`** | Book, reschedule and cancel appointments for any patient; view the day's schedule for any doctor; register patients | Upload or read clinical documents |
| **`doctor`** | View **own** schedule, view records and documents of patients on their own schedule, upload documents to those records | See other doctors' schedules; alter another doctor's appointments |
| **`clinic_admin`** | Manage doctors, opening hours, and users; view all schedules | Read clinical document contents *(state the choice — this is where the HIPAA-style discipline in Phase 6 starts)* |

**Enforcement:** `auth-service` issues a JWT carrying the role and subject,
signed with an **RS256 private key it alone holds**. `clinic-service` fetches the
**JWKS** (`/.well-known/jwks.json`), caches it, picks the key by `kid`, and
validates locally. Document authorization is checked in the API **before** a
presigned URL is minted — once the URL exists, whoever holds it can use it until
it expires.

**Why asymmetric, not the shared HS256 secret from QuickServe:** with HS256 every
verifier can also *mint* tokens. A compromised `clinic-service` could forge an
admin token. With RS256, verifiers hold only public keys. Rotation becomes
possible without redeploying every service: publish the new key, sign with it,
keep the old one in the JWKS until the last old token expires, then drop it.
Do this rotation **live**, with requests flowing, and assert zero `401`s.

**Login flows — two, on purpose:**

| Flow | Who | Mechanism |
|---|---|---|
| Password login | Staff (`receptionist`, `doctor`, `clinic_admin`) | `POST /auth/login`, argon2 hash, rate-limited, lockout/backoff after N failures, constant response for "no such user" and "wrong password" |
| **OAuth2 Authorization Code + PKCE** | Patients | Browser → `auth-service` `/auth/oidc/start` → IdP (Google, or **Keycloak in Compose** so tests do not need the internet) → callback with `code` → `auth-service` exchanges it, validates the IdP's ID token (issuer, audience, nonce, signature via *the IdP's* JWKS), links or creates the patient, issues **its own** access + refresh tokens |

Refresh tokens are **rotated** on every use (the old one is invalidated; reuse of
a rotated token revokes the whole family — that is how you detect theft) and
stored hashed, so `POST /auth/logout` can actually revoke them.

---

## 5. Functional Modules

### 5.1 Identity (`auth-service`)
Password login for staff, OIDC login for patients, RS256 signing, JWKS
publication, key rotation, refresh-token rotation and revocation, login
protection. Still deliberately small — it is a first-party token issuer, not a
full identity platform, and it delegates *identity* for patients to an IdP.

### 5.2 Scheduling (`clinic-service`)
Doctors, slots, appointments. The conflict rule is a database constraint.

### 5.3 Records
Patients, and the documents attached to them. The API stores metadata and
authorizes access; object storage holds the bytes.

### 5.4 Reminders
Celery Beat sends a reminder 24h before a slot — the same pattern as PeopleOps,
reused rather than relearned. Rebuilding it quickly is the point.

### 5.5 Frontend (`carepoint-web/`)
One page: the doctor's daily schedule.

---

## 6. Architecture — the first real service split

```
                 Nginx  (reverse proxy / single entrypoint)
                   │
      /auth/*  ────┼────►  auth-service      (FastAPI)    — issues & signs JWTs
      everything ──┴────►  clinic-service    (Django/DRF) — appointments, records, docs
```

A **deliberately minimal split — two services, not ten** — so you feel the actual
cost before ever being tempted to over-split:

| What it costs | Concretely |
|---|---|
| Another deployable | A second image, a second health check, a second log stream |
| Shared secret management | Both services need the key, and must agree on rotation |
| Clock agreement | Both must agree on **clock skew tolerance** for JWT expiry |
| Local development | Two processes plus Nginx before anything works |

```
carepoint/
  auth-service/       # FastAPI, separate deployable
  clinic-service/     # Django/DRF
  nginx/
    nginx.conf
  docker-compose.yml

carepoint-web/        # Vite + React + TypeScript + TanStack Query
```

---

## 7. Domain Model

```
doctors(id, name, specialty)

patients(id, name, dob, contact, oidc_subject NULL, oidc_issuer NULL)

appointments(id, doctor_id, patient_id,
             slot_start timestamptz, slot_end timestamptz, status)
    -- EXCLUDE constraint prevents overlapping slots per doctor

documents(id, patient_id, s3_key, uploaded_by, uploaded_at)

-- auth-service
signing_keys(kid, private_pem, public_pem, created_at, retired_at NULL)
refresh_tokens(id, user_id, token_hash, family_id, issued_at,
               expires_at, revoked_at NULL, replaced_by NULL)
login_attempts(email, failed_count, locked_until NULL, updated_at)
```

**Time is `timestamptz`.** The clinic has a timezone (`Asia/Tashkent`); slots are
stored as instants in UTC and rendered in clinic time. The `tsrange` in the
`EXCLUDE` constraint becomes `tstzrange`. Test the DST change-over day: a slot
booked at 09:00 local before the change is still 09:00 local after it, and
two slots that look adjacent in local time do not overlap in UTC.

---

## 8. Database Design — the centrepiece

A Postgres **`EXCLUDE` constraint using `btree_gist`** prevents overlapping
appointment slots per doctor **at the database level**:

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE appointments ADD CONSTRAINT no_overlap
  EXCLUDE USING gist (
    doctor_id WITH =,
    tstzrange(slot_start, slot_end) WITH &&
  ) WHERE (status <> 'cancelled');
```

Fire two concurrent identical bookings and watch the database reject the second —
with **no application-level locking involved at all**.

**Why this beats an application check:** an application `SELECT ... then INSERT`
is two statements with a gap between them. Under concurrency, both requests see an
empty slot and both insert. A `SELECT ... FOR UPDATE` can close it, but you have to
remember to write it, on every path, forever. A constraint cannot be forgotten.

Also index `appointments(doctor_id, slot_start)` for the daily-schedule query.

---

## 9. API Design

| Method | Path | Service | Role | Notes |
|---|---|---|---|---|
| POST | `/auth/login` | auth | public | Staff password login. Rate-limited, lockout/backoff. Issues RS256 access + refresh |
| GET | `/auth/oidc/start` | auth | public | Redirects to the IdP with PKCE `code_challenge` + `state` + `nonce` |
| GET | `/auth/oidc/callback` | auth | public | Exchanges `code`, validates ID token, issues first-party tokens |
| POST | `/auth/token/refresh` | auth | public | **Rotates** the refresh token; reuse of an old one revokes the family |
| POST | `/auth/logout` | auth | any | Revokes the refresh-token family |
| GET | `/.well-known/jwks.json` | auth | public | Current + retiring public keys, by `kid` |
| GET | `/appointments?doctor_id=&date=` | clinic | staff+ | **Redis-cached** |
| POST | `/appointments` | clinic | patient+ | DB constraint prevents double-booking |
| PATCH | `/appointments/{id}/cancel` | clinic | owner / reception | Invalidates the cache |
| POST | `/documents/presigned-upload` | clinic | doctor | Returns a presigned PUT URL |
| GET | `/documents/{id}/presigned-download` | clinic | doctor / owning patient | Short-lived presigned GET |
| GET | `/health` | both | internal | Checks DB + Redis connectivity |

---

## 10. Document Storage (presigned URLs)

**Requirement:** patient documents must never be readable by URL guessing, and
file bytes must never flow through the API process.

```
Upload:    client → API: "I want to upload"
           API: authorize → mint presigned PUT → return URL
           client → object storage: PUT the bytes directly

Download:  client → API: "give me document 42"
           API: authorize → mint short-lived presigned GET → return URL
           client → object storage: GET
```

The API handles **metadata and authorization only**. It never buffers a scan in
memory, never becomes the bandwidth bottleneck, and never has to stream a 50MB
file through a worker.

**Security window:** presigned URL lifetime is a real tradeoff. Keep it short
(minutes) and be able to justify the number. A leaked URL is valid until it expires
regardless of who holds it.

---

## 11. Infrastructure — what to connect, and exactly where

| Component | Where exactly it is used | Why it is justified |
|---|---|---|
| **Nginx** | Single entrypoint; routes `/auth/*` → auth-service, everything else → clinic-service. Also: `proxy_set_header X-Request-ID $request_id`, `proxy_read_timeout`, upstream `keepalive`, `gzip`, `client_max_body_size` **small** (bytes go to MinIO, not through here), and the **security headers** (`Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a starter `Content-Security-Policy`) | Your first hand-written `nginx.conf`. Two services need one front door. Every option you set, you can explain |
| **CORS** | `carepoint-web` on `localhost:5173` calls the API on `localhost:8080`. Configure allowed origins explicitly (an allow-list, never `*` when `credentials` are involved), allowed methods/headers, and understand the preflight `OPTIONS`. Decide whether Nginx or the apps answer preflight, and write down why | The first frontend is the first CORS error. Fix it by understanding it, not by `Access-Control-Allow-Origin: *` |
| **Keycloak** (Compose) | The OIDC identity provider for patient login in local dev and CI | Real OIDC flow without depending on Google in tests. Also the first look at an IdP's admin console, realms, and clients |
| **Request ID** | Nginx generates `$request_id`, forwards it; both services log it via `structlog` bind; Celery tasks receive it as a header/kwarg | Grepping one request across three processes is the smallest form of tracing. Full OpenTelemetry arrives in LedgerBase |
| **PostgreSQL + `btree_gist`** | Appointments, patients, documents metadata | The extension is required for the `EXCLUDE` constraint |
| **Redis — cache** | `GET /appointments?doctor_id=&date=` only, invalidated on booking/cancel for that doctor+date | Reception refreshes the same day view constantly |
| **Redis — Celery broker** | The reminder job | Reused from earlier phases |
| **Celery Beat + worker** | 24h-before appointment reminders | Pattern reuse; build it fast |
| **MinIO (S3-compatible)** | Patient document bytes, via presigned PUT/GET | Keeps bytes out of the API process and out of Postgres |
| **Docker Compose** | `nginx` + `auth-service` + `clinic-service` + `postgres` + `redis` + `minio` + worker | Six services. **Note how this feels** — it is the input to Phase 5's Kubernetes decision |
| **GHCR** | CI builds and pushes an image per service on merge to `main` | The deploy step lands in Week 17 with LedgerBase |
| **`/health` endpoints** | One per service, checking DB and Redis connectivity | Real readiness, not "the process started" |

**Deliberately NOT connected:**

| Component | Why not |
|---|---|
| **Prometheus / Grafana** | Two services is barely enough to compare. Wiring the full stack lands in Week 17–18 with four services and a reason |
| **A message broker between the two services** | They do not exchange events. Auth is validated locally by design — adding a broker here would be architecture for its own sake |
| **A service mesh / mTLS** | Two services on one Compose network. Name what mTLS would add and move on |
| **A second database** | Two services, one Postgres, separate schemas. Splitting the database too would double the cost with no new lesson |

---

## 12. Frontend — `carepoint-web/` (first of four)

Vite + React + TypeScript + TanStack Query. **One page:** the doctor's daily
schedule, fetched via TanStack Query against the endpoint you just cached.

The goal is not frontend depth. It is to establish habits the next three frontends
reuse instead of relearning:

- A typed API client generated from or matched to the backend schema
- Query keys that mirror the cache keys on the server — notice the parallel with
  your Redis cache-aside invalidation
- Invalidate on mutation rather than refetching everything

---

## 13. Build Plan (consolidated)

### Stage 1 — Service split & booking *(D79–D84, Week 14)*
- New repo `carepoint/`; `auth-service` scaffold (FastAPI, reusing Phase 1 JWT logic)
  — now **RS256**: `signing_keys` table, `/.well-known/jwks.json`, `kid` in the header
- `clinic-service` scaffold (Django/DRF) with JWT validation middleware that
  fetches and caches the JWKS and selects the key by `kid`
- **Live key rotation**: add key B, sign with B, keep A published, let A's tokens
  expire, retire A — under load, zero `401`s
- Staff login hardening: argon2, per-IP + per-account rate limit, lockout/backoff,
  identical responses for unknown user / wrong password
- All appointment columns `timestamptz`; `tstzrange` in the constraint
- `Appointment` model with the `EXCLUDE` constraint
- `POST /appointments`, then **deliberately fire two concurrent identical bookings**
- `nginx.conf` routing both services; add Nginx to Compose

### Stage 2 — Documents, caching, reminders, frontend *(D85–D90, Week 15)*
- Add `minio` to Compose
- `POST /documents/presigned-upload`
- `GET /documents/{id}/presigned-download`
- Cache the doctor schedule, invalidate on booking/cancel
- Scaffold `carepoint-web/` — the schedule page via TanStack Query — and hit the
  **CORS** wall; fix it with an explicit allow-list, understand the preflight
- Security headers in `nginx.conf`; check them with a header scanner
- **OIDC patient login**: Keycloak in Compose, Authorization Code + PKCE, ID-token
  validation against Keycloak's JWKS, patient linking, first-party token issuance
- Refresh-token rotation + family revocation; `POST /auth/logout`
- `X-Request-ID` end to end: Nginx → both services → Celery
- Celery Beat: 24h reminder task
- DST test for slots
- `docs/scaling-notes.md`, `docs/auth-notes.md` (HS256→RS256, OIDC flow, rotation); tag `v0.1-carepoint`

---

## 14. Testing Strategy

| Layer | What |
|---|---|
| **Integration** | Two concurrent bookings for the same doctor/slot — exactly one succeeds, **and the DB constraint is what rejects it** |
| Integration | Presigned upload → object lands in MinIO → presigned download retrieves it |
| Security | An expired presigned URL is refused |
| Security | A patient cannot mint a download URL for another patient's document |
| Cache | Booking and cancelling both invalidate the doctor+date schedule |
| Auth | A token signed with the wrong key is rejected by `clinic-service` |
| Auth | Clock-skew tolerance behaves as configured at the expiry boundary |
| Task | The reminder fires 24h before, tested with time travel |
| Health | `/health` fails when Postgres or Redis is down |
| **Key rotation** | Rotate the signing key while a load test runs; zero `401`s; a token signed by the retired key is rejected after retirement |
| **OIDC** | Full code flow against Keycloak in CI: wrong `state` rejected, wrong `nonce` rejected, ID token with the wrong `aud` rejected, happy path links the patient |
| Refresh rotation | Using a refresh token twice revokes the family; logout invalidates every device's refresh token |
| Login protection | 10 wrong passwords → lockout/backoff; unknown email and wrong password return byte-identical bodies and similar timing |
| **CORS** | Preflight from the allowed origin succeeds; from another origin it is refused; no `*` when credentials are sent |
| Headers | Every response carries HSTS, `nosniff`, `X-Frame-Options`, CSP |
| **DST** | A 09:00 slot on the change-over day renders as 09:00 clinic time; adjacent local slots do not collide |
| Request ID | One `X-Request-ID` appears in Nginx, both services' and the Celery worker's logs for a single booking |

---

## 15. CI/CD

GitHub Actions now **builds and pushes** Docker images to GHCR on merge to `main`,
one per service. The deploy step deliberately waits until Week 17, when LedgerBase
makes four services and automating by hand stops being reasonable.

---

## 16. Definition of Done

- [ ] Two services running behind Nginx, one entrypoint
- [ ] JWT issued by auth-service, validated locally by clinic-service
- [ ] `EXCLUDE` constraint proven under concurrent booking
- [ ] Presigned upload/download working; bytes never touch the API
- [ ] Presigned URL expiry tested
- [ ] Schedule cache with correct invalidation on both booking and cancellation
- [ ] 24h reminder job on Beat
- [ ] `carepoint-web/` schedule page working against the real API
- [ ] `/health` per service, checking real dependencies
- [ ] RS256 + JWKS + `kid`; live rotation with zero `401`s
- [ ] OIDC Authorization Code + PKCE login for patients, tested against Keycloak in CI
- [ ] Refresh-token rotation, family revocation, working logout
- [ ] Login rate limit + lockout; no user enumeration
- [ ] CORS allow-list and security headers in place and tested
- [ ] `timestamptz` everywhere; DST test green
- [ ] `X-Request-ID` propagated through Nginx, both services, Celery
- [ ] `docs/auth-notes.md`
- [ ] Images built and pushed to GHCR by CI
- [ ] `docs/scaling-notes.md` written
- [ ] Tag `v0.1-carepoint`

---

## 17. Scaling Notes (written)

What happens when `auth-service` needs to scale independently of `clinic-service`,
and what it costs to keep them in sync. **This is the concrete argument for the
split you just made** — if the note is unconvincing, say so honestly in the
postmortem rather than pretending the split paid off.

---

## 18. Interview Questions This Project Should Let You Answer

1. Why split auth into its own service here, and what did it cost you?
2. How does a DB-level `EXCLUDE` constraint prevent double-booking better than an
   application-level check?
3. Why presigned URLs instead of routing file uploads through your API?
4. How long should a presigned URL live, and what is the tradeoff?
5. What does Nginx actually do here, versus what an API Gateway would add on top?
6. How do two services agree on JWT validity without calling each other on every
   request — and what has to be shared for that to work?
7. What is clock skew tolerance and why does it matter across two services?
8. Your `/health` returns 200 — what exactly did it check?
9. HS256 or RS256 for JWTs across services — why does it matter who can mint a token?
10. Walk me through the OAuth2 Authorization Code flow with PKCE. What do `state`
    and `nonce` each protect against?
11. How do you rotate a JWT signing key with zero downtime?
12. What is refresh-token rotation, and how does reuse detection catch a stolen token?
13. Explain a CORS preflight. Why is `Access-Control-Allow-Origin: *` with
    credentials refused by browsers?
14. What does each security header you set actually prevent?
15. How do you prevent user enumeration on a login endpoint?
16. Why `timestamptz`, and what would have gone wrong with `timestamp` on the DST day?

---

## 19. Common Mistakes to Watch For

- Validating slot overlap only in application code and trusting it
- Presigned URLs valid too long
- Authorizing the *download* but not the *minting* of the URL
- Forgetting that the two services must agree on clock skew tolerance
- A `/health` endpoint that returns 200 without touching its dependencies
- Splitting the database as well as the service, doubling the cost for no lesson
- HS256 with a shared secret across services, so any service can forge any token
- A JWKS with no `kid`, so rotation means a flag day
- Refresh tokens that live forever and cannot be revoked — "logout" that only deletes a cookie
- `Access-Control-Allow-Origin: *` to make the error go away
- Different error messages for "no such user" and "wrong password"
- Naive `timestamp` for slots, so the DST day double-books or gaps
- Validating the IdP's ID token by parsing it without checking `iss`, `aud`, `nonce`, and signature

---

## 20. How Real Companies Differ

Most real systems do not split auth out this early. You are doing it now
specifically to *feel* the tradeoff while the system is still small enough to
reason about — not because two services is the right number at this size.
