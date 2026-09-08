# Project 5 — CarePoint

**Clinic appointment & patient records system — the first real service split**

| | |
|---|---|
| Domain | Healthcare |
| Level | Middle |
| Phase | 4 — Microservices & Infrastructure |
| Weeks | 14–15 (D79–D90) |
| Stack | FastAPI (auth-service), Django/DRF (clinic-service), PostgreSQL + `btree_gist`, Redis, Celery Beat, **Nginx**, **MinIO/S3**, **React + TS + Vite + TanStack Query**, Docker Compose, GHCR |
| Repo | `carepoint/` + `carepoint-web/` |

> **Two lessons, both structural.** First: what a service split actually costs,
> learned with two services rather than ten. Second: let the *database* enforce
> the thing that must never happen, instead of hoping application code wins a race.

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
   with no network call per request
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
| Service-to-service mTLS | Named; the trust model here is a shared key, and you should be able to say what mTLS would add |
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

**Enforcement:** `auth-service` issues a JWT carrying the role and subject.
`clinic-service` validates the signature locally and applies the rules. Document
authorization is checked in the API **before** a presigned URL is minted — once
the URL exists, whoever holds it can use it until it expires.

---

## 5. Functional Modules

### 5.1 Identity (`auth-service`)
Login, JWT issuance, key material. Deliberately small. It exists to be a separate
deployable, not to be a full identity platform.

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

patients(id, name, dob, contact)

appointments(id, doctor_id, patient_id, slot_start, slot_end, status)
    -- EXCLUDE constraint prevents overlapping slots per doctor

documents(id, patient_id, s3_key, uploaded_by, uploaded_at)
```

---

## 8. Database Design — the centrepiece

A Postgres **`EXCLUDE` constraint using `btree_gist`** prevents overlapping
appointment slots per doctor **at the database level**:

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE appointments ADD CONSTRAINT no_overlap
  EXCLUDE USING gist (
    doctor_id WITH =,
    tsrange(slot_start, slot_end) WITH &&
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
| POST | `/auth/login` | auth | public | Issues JWT |
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
| **Nginx** | Single entrypoint; routes `/auth/*` → auth-service, everything else → clinic-service | Your first hand-written `nginx.conf`. Two services need one front door |
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
- `clinic-service` scaffold (Django/DRF) with JWT validation middleware
- `Appointment` model with the `EXCLUDE` constraint
- `POST /appointments`, then **deliberately fire two concurrent identical bookings**
- `nginx.conf` routing both services; add Nginx to Compose

### Stage 2 — Documents, caching, reminders, frontend *(D85–D90, Week 15)*
- Add `minio` to Compose
- `POST /documents/presigned-upload`
- `GET /documents/{id}/presigned-download`
- Cache the doctor schedule, invalidate on booking/cancel
- Scaffold `carepoint-web/` — the schedule page via TanStack Query
- Celery Beat: 24h reminder task
- `docs/scaling-notes.md`; tag `v0.1-carepoint`

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

---

## 19. Common Mistakes to Watch For

- Validating slot overlap only in application code and trusting it
- Presigned URLs valid too long
- Authorizing the *download* but not the *minting* of the URL
- Forgetting that the two services must agree on clock skew tolerance
- A `/health` endpoint that returns 200 without touching its dependencies
- Splitting the database as well as the service, doubling the cost for no lesson

---

## 20. How Real Companies Differ

Most real systems do not split auth out this early. You are doing it now
specifically to *feel* the tradeoff while the system is still small enough to
reason about — not because two services is the right number at this size.
