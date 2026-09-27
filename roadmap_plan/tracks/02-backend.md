# Track 2 — Backend Engineering with Python

**Goal:** become a middle+/senior-ready Python backend engineer. Build ten
real systems, from a single-store inventory API up to a multi-vendor
marketplace. Along the way you learn how to design, build, test, ship,
observe and scale them, and how to defend every decision in an interview.

**Required knowledge:**
- Track 1A (Python), all of it.
- Track 1C Part 1 (SQL fundamentals) and Part 2 (advanced PostgreSQL).
- Track 1B (DSA) is recommended in parallel. Nothing here blocks on it, but
  interviews will.

**Total estimated hours:** ~983 h core (~423 h modules + ~560 h projects),
plus ~128 h OPTIONAL (React + TS module, Telegram bots module, from-scratch
Raft build, three system-design builds).

---

## How to use this track

- **Checkboxes everywhere.** Tick a lesson when you have read it and can
  explain it without notes. Tick an exercise when it meets its acceptance
  criteria. Tick a project milestone when every deliverable in it is
  committed.
- **No solutions in this file.** It gives specs, acceptance criteria and
  checklists. You write all the code. Ask your mentor for review, hints and
  concepts, never for the finished implementation.
- **Order.** The modules are in a logical order, and every project comes
  right after the modules it needs. Every backend tool a project uses is
  taught in an earlier module of this track (or in Track 1). Modules marked
  **OPTIONAL** can be skipped. The project parts that depend on them are
  optional too.
- **Where the work goes:**
  - Module exercises: this repo, `backend/<Bnn-slug>/`
    (e.g. `backend/B04-fastapi/ex_4_2_items_api/`).
  - Projects: **one GitHub repo per project** (`StockPilot/`,
    `QuickServe/`, …), because later projects reuse infrastructure from
    earlier ones.
- **Self-check questions** close every module. Answer them out loud first,
  then read the answers below the `---` separator.

---

## Roadmap of this track

| #       | Item                                                                              | Level / type       | Hours    |
| ------- | --------------------------------------------------------------------------------- | ------------------ | -------- |
| B1      | HTTP & REST API design                                                            | Module             | 8        |
| B2      | Linux & CLI basics                                                                | Module             | 8        |
| B3      | Docker & Docker Compose                                                           | Module             | 12       |
| B4      | FastAPI                                                                           | Module             | 15       |
| B5      | SQLAlchemy 2.0 (sync → async), Alembic, layered architecture                      | Module             | 18       |
| B6      | Auth I: password hashing, sessions vs JWT, OAuth2 password flow, RBAC             | Module             | 8        |
| B7      | Transactions & concurrency in applications                                        | Module             | 8        |
| B8      | Testing web applications                                                          | Module             | 10       |
| B9      | CI with GitHub Actions                                                            | Module             | 6        |
| **P1**  | **StockPilot** — single-store inventory & order API                               | **Junior**         | **60**   |
| B10     | Django                                                                            | Module             | 18       |
| B11     | Django REST Framework (+ simplejwt, permissions, throttling)                      | Module             | 14       |
| B12     | Redis I: data structures, caching patterns, stampede, HTTP caching, rate limiting | Module             | 12       |
| B-opt   | Telegram bots with aiogram                                                        | Module · OPTIONAL  | 8        |
| **P2**  | **QuickServe POS** — point-of-sale system                                         | **Junior**         | **45**   |
| B13     | Celery: tasks, retries, acks_late, idempotent tasks, beat                         | Module             | 12       |
| **P3**  | **PeopleOps** — HR & leave management                                             | **Middle**         | **45**   |
| B14     | Architecture patterns: DI, Repository, Unit of Work, DDD-lite                     | Module             | 10       |
| B15     | RabbitMQ: exchanges, routing, DLQ, publisher confirms, contract tests             | Module             | 12       |
| B16     | Kafka: topics, partitions, consumer groups, offsets, delivery semantics           | Module             | 10       |
| **P4**  | **WareFlow** — multi-warehouse WMS                                                | **Middle**         | **60**   |
| B17     | Networking (TCP, HTTP/2, TLS, DNS) + Nginx                                        | Module             | 12       |
| B18     | Auth II: OAuth2/OIDC, PKCE, RS256/JWKS, token rotation, Keycloak                  | Module             | 12       |
| B19     | Web security basics: OWASP Top 10, CORS/CSRF, security headers                    | Module             | 8        |
| B20     | Object storage: S3/MinIO, presigned URLs                                          | Module             | 4        |
| B21     | Frontend for backend engineers: React + TypeScript                                | Module · OPTIONAL  | 25       |
| **P5**  | **CarePoint** — clinic appointments & records                                     | **Middle**         | **50**   |
| B22     | Resilience patterns: retry + backoff, circuit breaker, bulkhead, timeouts         | Module             | 8        |
| B23     | CI/CD II & VPS deploy: GHCR, supply-chain gates, zero-downtime, expand/contract   | Module             | 15       |
| B24     | Logging & monitoring: Prometheus, Grafana, Loki, OpenTelemetry, Sentry            | Module             | 15       |
| **P6**  | **LedgerBase** — double-entry accounting & invoicing                              | **Middle**         | **65**   |
| B25     | Event-driven patterns: outbox, saga, CQRS, event versioning                       | Module             | 12       |
| B26     | Real-time: WebSocket, SSE, Redis pub/sub                                          | Module             | 8        |
| **P7**  | **FleetTrack** — event-driven fleet & delivery platform                           | **Middle+**        | **45**   |
| B27     | Search: PostgreSQL FTS → Elasticsearch                                            | Module             | 12       |
| B28     | Replication, connection pooling (PgBouncer), sharding, consistent hashing         | Module             | 10       |
| B29     | Consensus & Raft, etcd (from-scratch Raft build OPTIONAL, +40 h)                  | Module             | 10 (+40) |
| B30     | Kubernetes                                                                        | Module             | 20       |
| **P8**  | **DocuVault** — document management with search & versioning                      | **Middle+**        | **60**   |
| B31     | Secrets management with Vault                                                     | Module             | 8        |
| B32     | gRPC + Protobuf                                                                   | Module             | 8        |
| B33     | Cloud basics (IAM, VPC, managed DB) + Terraform                                   | Module             | 15       |
| B34     | Payment-grade idempotency keys & HMAC-signed webhooks                             | Module             | 6        |
| B35     | Reliability & SRE: backup/DR, load testing, profiling, chaos, SLOs, incidents     | Module             | 12       |
| **P9**  | **PayFlow** — payment processing platform                                         | **Middle+**        | **60**   |
| B36     | GraphQL (Strawberry, DataLoader)                                                  | Module             | 8        |
| B37     | Multi-tenancy (Postgres RLS), feature flags, canary releases                      | Module             | 6        |
| B38     | System design fundamentals                                                        | Module             | 20       |
| **P10** | **AtlasMarket** — AI-assisted multi-vendor marketplace (capstone)                 | **Middle+**        | **70**   |
| B39     | MongoDB                                                                           | Module             | 8        |
| B40     | TimescaleDB                                                                       | Module             | 5        |
| O1      | URL Shortener                                                                     | Project · OPTIONAL | 15       |
| O2      | Rate Limiter Service                                                              | Project · OPTIONAL | 15       |
| O3      | Distributed Job Scheduler (needs the OPTIONAL Raft build from B29)                | Project · OPTIONAL | 25       |

---

## Module B1 — HTTP & REST API Design (~8h)

**Topics:** the request/response model; methods and their semantics (safe,
idempotent, cacheable); status codes and the families people get wrong
(400 vs 422, 401 vs 403, 404 vs 410, 409, 429, 503); headers (Content-Type,
Accept, Authorization, Location, ETag, Cache-Control, Retry-After);
resource-oriented URL design; collections vs items; filtering, sorting and
pagination (offset vs cursor); versioning strategies; an error contract
(RFC 9457 Problem Details); long-running operations (202 + status
resource); OpenAPI as a contract.

### Lessons
- [ ] **B1.L1 How HTTP works.** MDN: "An overview of HTTP", "HTTP messages", "Evolution of HTTP".
- [ ] **B1.L2 Methods and their guarantees.** MDN: "HTTP request methods". RFC 9110 §9.2 "Common Method Properties" (safe, idempotent, cacheable).
- [ ] **B1.L3 Status codes.** MDN: "HTTP response status codes". Read every 2xx/4xx/5xx page you would use in an API.
- [ ] **B1.L4 Resource design and naming.** Zalando RESTful API Guidelines (opensource.zalando.com/restful-api-guidelines): sections "REST Basics – URLs", "REST Basics – HTTP requests", "REST Basics – HTTP status codes".
- [ ] **B1.L5 Pagination, filtering, versioning.** Zalando guidelines: "Pagination", "Compatibility" and "Deprecation". Microsoft REST API Guidelines (github.com/microsoft/api-guidelines): "Collections" and "Versioning".
- [ ] **B1.L6 Error contracts.** RFC 9457 "Problem Details for HTTP APIs", §3 "The Problem Details JSON Object".
- [ ] **B1.L7 OpenAPI as a contract.** OpenAPI Initiative "Getting Started" (learn.openapis.org), sections "Introduction" through "Describing responses".

### Exercises (`backend/B01-http-rest/`)
- [ ] **Ex B1.1 Talk HTTP by hand.** Use `curl -v` against a public API (e.g. httpbin.org) to send GET, POST, PUT, PATCH and DELETE. Save the raw request/response pairs in `http-log.md`. For each one, annotate the status line, three headers and whether the method is idempotent. *Acceptance:* 5 annotated exchanges, including a 301/302 and a 404.
- [ ] **Ex B1.2 Design an API on paper.** Write `library-api.md` for a small library system (books, members, loans). Include endpoints, methods, request/response bodies and status codes for success and each failure. *Acceptance:* no verbs in URLs; creating a loan returns 201 + `Location`; returning an already-returned book has a defined error; each list endpoint has pagination parameters.
- [ ] **Ex B1.3 Status-code drill.** Write 15 short scenarios, e.g. "the token is valid but the user may not delete this", "the email already exists", "the body is valid JSON but `qty` is negative", and pick the correct status code for each with a one-line reason. *Acceptance:* 401/403, 400/422 and 404/409 each appear at least twice.
- [ ] **Ex B1.4 Error contract.** Define a Problem Details error schema for `library-api.md` and write three example error bodies. *Acceptance:* each has `type`, `title`, `status`, `detail`, plus one extension field (`errors[]` for validation).
- [ ] **Ex B1.5 OpenAPI by hand.** Write `openapi.yaml` for two endpoints of your library API and render it in Swagger Editor (editor.swagger.io). *Acceptance:* renders with no errors; the schemas are shared through `components/schemas`.

### Must be able to do / explain
- [ ] Explain safe vs idempotent, and why PUT is idempotent but POST is not.
- [ ] Choose the right status code for a validation error, a conflict, a missing permission and rate limiting.
- [ ] Design URLs for nested resources without deep nesting.
- [ ] Explain offset vs cursor pagination and when each one fits.
- [ ] Explain three API versioning strategies and their trade-offs.
- [ ] Describe what an ETag is for.

**Estimated hours:** ~8h

### Self-check interview questions
1. What makes an HTTP method idempotent? Is DELETE idempotent?
2. 401 vs 403: what is the difference?
3. When would you return 409 instead of 422?
4. What problems does offset pagination have on a large, frequently changing table?
5. How would you version a public API, and what do you do with the old version?
6. What should an API return for an operation that takes 5 minutes?
7. Why should error responses follow one contract?

---

**Answers**
1. Repeating the same request has the same effect on server state as sending it once. Yes: the second DELETE may return 404, but the state (resource gone) is the same.
2. 401: the request is not authenticated (missing or invalid credentials). 403: you are authenticated, but not allowed to do this.
3. 409: the request conflicts with the current state of the resource (duplicate key, version mismatch, insufficient stock). 422: the body is syntactically valid, but its content fails validation.
4. The database still reads and throws away all the skipped rows, so cost grows with the offset. Rows inserted or deleted between page loads cause duplicates or gaps.
5. Options: URL (`/v2`), header or media type. Keep the old version for a published deprecation window, signal it with `Deprecation`/`Sunset` headers, and monitor usage before removing it.
6. `202 Accepted` with a `Location` of a status resource the client can poll (or a webhook or callback when it finishes).
7. Clients can handle errors generically, logs and alerts are consistent, and nothing internal leaks through ad-hoc messages.

---

## Module B2 — Linux & CLI Basics (~8h)

**Topics:** the filesystem hierarchy; navigation and file manipulation;
permissions and ownership (`chmod`, `chown`, umask); processes and signals
(`ps`, `top`/`htop`, `kill`, SIGTERM vs SIGKILL); environment variables;
pipes and redirection; searching (`grep`, `find`); text processing (`awk`,
`sed`, `cut`, `sort`, `uniq`); package managers; SSH and keys; `systemd`
services and `journalctl`; basic networking tools (`curl`, `ss`, `dig`);
simple shell scripts with `set -euo pipefail`.

### Lessons
- [ ] **B2.L1 The shell and the filesystem.** *The Linux Command Line*, 2nd ed. (William Shotts, free at linuxcommand.org), Ch.1–5 (What Is the Shell?, Navigation, Exploring the System, Manipulating Files and Directories, Working with Commands).
- [ ] **B2.L2 Redirection, pipes and expansion.** Same book, Ch.6 (Redirection) and Ch.7 (Seeing the World as the Shell Sees It).
- [ ] **B2.L3 Permissions and processes.** Same book, Ch.9 (Permissions) and Ch.10 (Processes).
- [ ] **B2.L4 Environment and packages.** Same book, Ch.11 (The Environment) and Ch.14 (Package Management).
- [ ] **B2.L5 Searching and text processing.** Same book, Ch.17 (Searching for Files), Ch.19 (Regular Expressions) and Ch.20 (Text Processing).
- [ ] **B2.L6 Networking and SSH.** Same book, Ch.16 (Networking). DigitalOcean tutorial "SSH Essentials: Working with SSH Servers, Clients, and Keys".
- [ ] **B2.L7 Services and logs.** `man systemd.service` (sections "Options" and "Service Types"), `man journalctl`. DigitalOcean tutorial "Systemd Essentials: Working with Services, Units, and the Journal".
- [ ] **B2.L8 Writing safe shell scripts.** Same book, Ch.24–27 (Writing Your First Script, Starting a Project, Top-Down Design, Flow Control). Read about `set -euo pipefail` in the Bash manual, section "The Set Builtin".

### Exercises (`backend/B02-linux/`)
- [ ] **Ex B2.1 Log detective.** Download an Nginx sample access log (or generate one). Using only a pipeline of `grep`/`awk`/`sort`/`uniq`/`head`, produce: the top 10 IPs, the count per status code, and the 5 slowest paths (if the log has request time). *Acceptance:* each answer is a single pipeline saved in `log-queries.sh`.
- [ ] **Ex B2.2 Permissions lab.** Create a user and a group, and a directory that only the group can write to. Show with `ls -l` and a failed write attempt that another user cannot write. *Acceptance:* `permissions.md` with the commands and outputs, and an explanation of the octal modes used.
- [ ] **Ex B2.3 Signals.** Write a small Python script that handles SIGTERM (logs "shutting down gracefully" and exits 0) but not SIGINT. Start it, then stop it with `kill -TERM`, `kill -INT` and `kill -KILL`. *Acceptance:* `signals.md` explains the three different outcomes, and why a container orchestrator sends SIGTERM first.
- [ ] **Ex B2.4 A systemd service.** Run a trivial Python HTTP server as a systemd unit that restarts on failure. Read its logs with `journalctl -u`. *Acceptance:* killing the process makes systemd restart it; the unit file is committed.
- [ ] **Ex B2.5 Backup script.** Write `backup.sh`: tar + gzip a directory into a timestamped file, keep only the last 5 archives, and exit non-zero on any error. *Acceptance:* uses `set -euo pipefail`; running it 7 times leaves 5 archives.

### Must be able to do / explain
- [ ] Navigate, find files and grep logs without a GUI.
- [ ] Read and set permissions in both symbolic and octal notation.
- [ ] Explain SIGTERM vs SIGKILL and what graceful shutdown means.
- [ ] Generate an SSH key pair and log in with key-based auth only.
- [ ] Manage a service with `systemctl` and read its logs.
- [ ] Explain what an environment variable is and how a child process inherits it.

**Estimated hours:** ~8h

### Self-check interview questions
1. What does `chmod 640 file` mean?
2. What happens when a process receives SIGTERM vs SIGKILL?
3. How would you find which process is listening on port 8000?
4. What is the difference between `>` and `>>`, and what does `2>&1` do?
5. Why use SSH keys instead of passwords, and where does the public key go?
6. What does `set -euo pipefail` protect you from?
7. What is a zombie process?

---

**Answers**
1. Owner: read+write (6), group: read (4), others: nothing (0).
2. SIGTERM can be caught: the process can clean up and exit. SIGKILL cannot be caught or ignored; the kernel kills the process immediately.
3. `ss -ltnp | grep 8000` (or `lsof -i :8000`).
4. `>` truncates the file and writes; `>>` appends. `2>&1` redirects stderr to wherever stdout currently points.
5. Keys cannot be brute-forced like passwords and can be revoked per key. The public key goes in the server's `~/.ssh/authorized_keys`.
6. `-e` exits on any error, `-u` fails on unset variables, and `pipefail` makes a pipeline fail when any command in it fails, not only the last one.
7. A process that has exited, but whose parent has not yet collected its exit status with `wait()`.

---

## Module B3 — Docker & Docker Compose (~12h)

**Topics:** images vs containers; layers and the build cache; the
Dockerfile instructions (FROM, RUN, COPY, WORKDIR, ENV, ARG, USER,
EXPOSE, ENTRYPOINT vs CMD); exec vs shell form and PID 1 / signal
handling; `.dockerignore`; **multi-stage builds**; **running as a non-root
user**; pinning base images; image size; volumes vs bind mounts; networks
and service DNS; Compose services, `depends_on` with
`condition: service_healthy`, **healthchecks**, env files, profiles;
container logs and `exec`.

### Lessons
- [ ] **B3.L1 Concepts.** Docker docs: "What is a container?", "What is an image?", "Docker overview".
- [ ] **B3.L2 Writing Dockerfiles.** Docker docs: "Dockerfile reference" (FROM, RUN, COPY, CMD, ENTRYPOINT, USER, HEALTHCHECK) and "Understanding the image layers" / "Using the build cache".
- [ ] **B3.L3 Best practices.** Docker docs: "Building best practices" (all sections, especially "Use multi-stage builds", "Create reusable stages", "Don't install unnecessary packages", "Sort multi-line arguments", "USER").
- [ ] **B3.L4 Multi-stage builds.** Docker docs: "Multi-stage builds".
- [ ] **B3.L5 Python in containers.** Docker docs guide "Python language-specific guide" ("Containerize your app", "Develop your app"). Itamar Turner-Trauring, pythonspeed.com: "Docker packaging for Python" articles on multi-stage builds and the slim base image.
- [ ] **B3.L6 Storage and networking.** Docker docs: "Volumes", "Bind mounts", "Networking overview".
- [ ] **B3.L7 Compose.** Docker docs: "Docker Compose overview", "Compose file reference" (services, healthcheck, depends_on, volumes, networks, env_file, profiles), "Control startup and shutdown order in Compose".

### Exercises (`backend/B03-docker/`)
- [ ] **Ex B3.1 First image.** Containerize a tiny Python HTTP app (stdlib `http.server` is fine). *Acceptance:* `docker run -p 8000:8000` serves it; `CMD` uses exec form; `docker stop` shuts it down in under 2 s (no 10-second SIGKILL wait).
- [ ] **Ex B3.2 Cache-friendly layering.** Build an image for a Python app that has `pyproject.toml` dependencies. Order the layers so that changing application code does NOT reinstall dependencies. *Acceptance:* the second build after a code-only change shows `CACHED` on the dependency layer; you explain why in `README.md`.
- [ ] **Ex B3.3 Multi-stage + non-root.** Rebuild Ex B3.2 as a multi-stage build (a builder stage with compilers → a slim runtime stage) running as a non-root user, with a `.dockerignore`. *Acceptance:* record the image size before and after; `docker run --rm <image> whoami` is not `root`; `gcc` is not present in the final image.
- [ ] **Ex B3.4 Compose with a healthy database.** A Compose file with `app` + `postgres:17`: a named volume for data, a Postgres healthcheck using `pg_isready`, and `app` depending on `condition: service_healthy`. *Acceptance:* `docker compose up` from nothing never shows the app failing to connect; data survives `docker compose down` (without `-v`).
- [ ] **Ex B3.5 Debug a container.** Deliberately break the app (wrong env var) and diagnose it using only `docker compose logs`, `docker compose exec`, and `docker inspect`. *Acceptance:* `debugging.md` lists the commands and what each told you.

### Must be able to do / explain
- [ ] Explain layers and why instruction order matters for caching.
- [ ] Write a multi-stage, non-root Dockerfile from memory.
- [ ] Explain ENTRYPOINT vs CMD, and exec vs shell form (PID 1 and signals).
- [ ] Explain volumes vs bind mounts and when to use each.
- [ ] Make a service wait for a truly ready dependency with a healthcheck.
- [ ] Explain how containers find each other on a Compose network.

**Estimated hours:** ~12h

### Self-check interview questions
1. What is the difference between an image and a container?
2. Why does the order of `COPY` and `RUN pip install` matter?
3. Why use a multi-stage build?
4. Why should a container not run as root?
5. What goes wrong when `CMD` uses shell form?
6. Does `depends_on` wait until Postgres is ready to accept connections?
7. Where does container data go when the container is removed?
8. How does the `app` container reach the `postgres` container?

---

**Answers**
1. An image is an immutable, layered template; a container is a running (or stopped) instance of an image with its own writable layer.
2. Each instruction creates a cached layer, and a change invalidates every layer after it. Copy the dependency files and install first, then copy the code, so code changes don't reinstall dependencies.
3. To build with heavy tools (compilers, dev dependencies) and ship only the runtime artefacts, which gives a smaller image with a smaller attack surface.
4. If the app is compromised, root inside the container makes privilege escalation and container escape far easier. Least privilege.
5. The process runs as a child of `/bin/sh`, which becomes PID 1 and does not forward SIGTERM, so graceful shutdown breaks and the container is SIGKILLed after the timeout.
6. Not by default; it only waits for the container to start. Use a healthcheck + `condition: service_healthy`.
7. The container's writable layer is deleted. Only data in volumes or bind mounts survives.
8. Through Compose's default network, which has built-in DNS: the hostname `postgres` (the service name) resolves to that container.

---

## Module B4 — FastAPI (~15h)

**Topics:** ASGI and how FastAPI sits on Starlette; path operations; path,
query, body and header parameters; **Pydantic v2** models (field types,
validators, `model_config`, serialization, `response_model`); **dependency
injection** with `Depends` (including `yield` dependencies for resources);
**settings with pydantic-settings** and `.env`; error handling (custom
exception handlers, `HTTPException`, one error contract); routers and
bigger-application layout; lifespan events; middleware; OpenAPI generation
and docs; `async def` vs `def` handlers and the threadpool; **structured
request logging with structlog** (one JSON line per request with
request id, method, path, status, latency).

### Lessons
- [ ] **B4.L1 First steps and parameters.** FastAPI docs → Tutorial: "First Steps", "Path Parameters", "Query Parameters", "Request Body", "Query Parameters and String Validations", "Header Parameters".
- [ ] **B4.L2 Pydantic v2.** Pydantic docs: "Models", "Fields", "Validators", "Serialization", "Configuration". FastAPI Tutorial: "Response Model – Return Type", "Extra Models".
- [ ] **B4.L3 Dependency injection.** FastAPI Tutorial: "Dependencies" (all subpages, especially "Dependencies with yield" and "Classes as Dependencies").
- [ ] **B4.L4 Errors.** FastAPI Tutorial: "Handling Errors" (custom exception handlers, overriding the validation error handler).
- [ ] **B4.L5 App structure and settings.** FastAPI Tutorial: "Bigger Applications – Multiple Files". FastAPI Advanced: "Settings and Environment Variables". pydantic-settings docs: "Settings Management".
- [ ] **B4.L6 Lifespan and middleware.** FastAPI Advanced: "Lifespan Events". FastAPI Tutorial: "Middleware".
- [ ] **B4.L7 async vs sync handlers.** FastAPI docs: "Concurrency and async / await". Connect it to 1A.12: what blocks the event loop, and why FastAPI runs `def` handlers in a threadpool.
- [ ] **B4.L8 Structured logging.** structlog docs: "Getting Started", "Context Variables" (`structlog.contextvars`), "Logging Best Practices".

### Exercises (`backend/B04-fastapi/`)
- [ ] **Ex B4.1 Items API in memory.** CRUD for `items` stored in a dict: list with `limit`/`offset`, get, create, patch, delete. *Acceptance:* correct status codes (201 on create, 404 on a missing item, 204 on delete); separate Pydantic models for create/update/read (the read model hides internal fields).
- [ ] **Ex B4.2 Validation rules.** Add Pydantic constraints and one custom validator (e.g. `sku` must match `^[A-Z]{3}-\d{4}$`; `price_cents >= 0`; `name` is stripped and non-empty). *Acceptance:* invalid bodies return 422 with a readable error; you can explain field vs model validators.
- [ ] **Ex B4.3 One error contract.** Replace FastAPI's default error bodies with your Problem Details format from Ex B1.4, for `HTTPException`, validation errors and a custom `DomainError`. *Acceptance:* every error response has the same shape; unexpected exceptions return 500 without a stack trace in the body.
- [ ] **Ex B4.4 Settings and DI.** Move configuration into a `Settings(BaseSettings)` class read from `.env`, and inject a fake "repository" object through `Depends`. Override the dependency in a test. *Acceptance:* the app starts with no hard-coded config; a test swaps the repository with `app.dependency_overrides`.
- [ ] **Ex B4.5 Blocking the event loop.** Add one `async def` endpoint that calls `time.sleep(2)` and one that awaits `asyncio.sleep(2)`. Fire 10 concurrent requests at each (with `hey` or a small `httpx` script). *Acceptance:* `blocking.md` shows the total times and explains the difference, plus the two correct fixes (a `def` handler, or `run_in_threadpool`/`run_in_executor`).
- [ ] **Ex B4.6 Request logging middleware.** A middleware that binds a `request_id` (taken from the `X-Request-ID` header or generated), logs one structlog JSON line per request (method, path, status, latency_ms) and returns the id in a response header. *Acceptance:* the logs are valid JSON, one line per request; the id appears in every log line emitted during that request.

### Must be able to do / explain
- [ ] Build a CRUD API with correct status codes and separate input/output models.
- [ ] Explain how `Depends` works, including `yield` dependencies and overriding them in tests.
- [ ] Load configuration from the environment with pydantic-settings.
- [ ] Produce one consistent error contract.
- [ ] Explain `async def` vs `def` handlers and what blocks the event loop.
- [ ] Add structured, correlated request logging.

**Estimated hours:** ~15h

### Self-check interview questions
1. What is ASGI and how is it different from WSGI?
2. What happens if you call a blocking function inside an `async def` handler?
3. How does FastAPI run a plain `def` handler?
4. What is a `yield` dependency useful for?
5. Why use separate Pydantic models for create, update and read?
6. How do you replace a dependency in tests?
7. Why log in JSON with a request id?
8. What is the lifespan event used for?

---

**Answers**
1. ASGI is the async successor of WSGI: it supports async handlers, long-lived connections (WebSockets) and many concurrent requests on one event loop. WSGI is synchronous, one request per worker thread.
2. It blocks the whole event loop: every other request on that worker waits until it finishes.
3. In a threadpool (via Starlette's `run_in_threadpool`), so it does not block the loop, but it is limited by the pool size.
4. Setup/teardown around a request, e.g. open a DB session, yield it, then commit/rollback and close it after the response.
5. They have different fields and rules: clients must not set `id` or `created_at`; update fields are optional; the read model must not leak internals such as `hashed_password`.
6. `app.dependency_overrides[original] = fake`.
7. Machines can parse and query JSON; the request id lets you pull every line belonging to one request, across services.
8. Code that runs once at startup and shutdown: creating and closing connection pools, loading models, warming caches.

---

## Module B5 — SQLAlchemy 2.0, Alembic & Layered Architecture (~18h)

**Topics:** Core vs ORM; the 2.0-style `select()` API; engines,
connections and **sessions** (unit of work, identity map, flush vs commit,
expire on commit); declarative models with `Mapped[]` / `mapped_column`;
relationships and **loading strategies** (lazy, `selectinload`,
`joinedload`) and the **N+1 problem**; transactions and
`session.begin()`; **sync first, then async** (`AsyncEngine`,
`AsyncSession`, why lazy loading breaks in async, `expire_on_commit=False`);
running raw SQL through `text()` for reporting (recursive CTEs,
`GROUP BY ROLLUP`/`GROUPING SETS` in PostgreSQL); **Alembic**
(autogenerate and its limits, reviewing migrations, upgrade/downgrade,
data migrations); **layered architecture** router → service → repository
→ database; a `Repository[T]` Protocol; a session per request as a FastAPI
dependency.

### Lessons
- [ ] **B5.L1 Core and the 2.0 query style.** SQLAlchemy 2.0 docs → "SQLAlchemy Unified Tutorial": "Establishing Connectivity – the Engine", "Working with Transactions and the DBAPI", "Working with Database Metadata", "Working with Data" (Using INSERT, Using SELECT, Using UPDATE and DELETE).
- [ ] **B5.L2 The ORM.** Unified Tutorial: "Data Manipulation with the ORM", "Working with ORM Related Objects". ORM docs: "ORM Mapped Class Overview" (Declarative with `Mapped`).
- [ ] **B5.L3 Sessions and transactions.** ORM docs: "Session Basics", "Managing Transactions" (`session.begin()`, commit/rollback, `expire_on_commit`).
- [ ] **B5.L4 Loading strategies and N+1.** ORM docs → "ORM Querying Guide": "Relationship Loading Techniques" (lazy, `selectinload`, `joinedload`, `raiseload`).
- [ ] **B5.L5 Async SQLAlchemy.** ORM docs: "Asynchronous I/O (asyncio)", especially "Preventing Implicit IO when Using AsyncSession".
- [ ] **B5.L6 Reporting SQL from the app.** Core docs: "Using Textual SQL" (`text()`, bound parameters). PostgreSQL docs §7.2.4 "GROUPING SETS, CUBE, and ROLLUP" and §7.8 "WITH Queries (Common Table Expressions)" (recursive part). You learned CTEs in 1C 2.1; ROLLUP is new here.
- [ ] **B5.L7 Alembic.** Alembic docs: "Tutorial" (create an environment, first migration, upgrade/downgrade), "Auto Generating Migrations" (read "What does Autogenerate Detect (and what does it not detect?)").
- [ ] **B5.L8 Layered architecture.** *Architecture Patterns with Python* (Percival & Gregory, free at cosmicpython.com): Ch.2 "Repository Pattern" and Ch.4 "Our First Use Case: Flask API and Service Layer" (read the ideas; you'll apply them with FastAPI). Python typing docs: `typing.Protocol` (refresh from 1A.7).

### Exercises (`backend/B05-sqlalchemy/`)
- [ ] **Ex B5.1 Sync ORM basics.** A sync script with models `Author` and `Book` (one-to-many) on PostgreSQL in Docker: create tables, insert data, query with `select()`, update and delete. *Acceptance:* uses `Mapped[]`/`mapped_column`; every write is inside `with Session.begin():`.
- [ ] **Ex B5.2 Catch the N+1.** List 50 authors with their books, and turn on `echo=True` to count the queries. Then fix it with `selectinload` and with `joinedload`. *Acceptance:* `n-plus-one.md` records the query counts for lazy / selectinload / joinedload and says when each strategy is the right choice.
- [ ] **Ex B5.3 Go async.** Port Ex B5.1 to `AsyncEngine`/`AsyncSession` with asyncpg. Deliberately trigger the lazy-load error on a relationship after the query, then fix it. *Acceptance:* you can explain in two sentences why implicit lazy loading is forbidden in async.
- [ ] **Ex B5.4 Alembic workflow.** Put Ex B5.3 under Alembic: an initial migration, then a second migration that adds a NOT NULL column to a table with existing rows (you will need a server default or a data step). *Acceptance:* `alembic upgrade head`, `alembic downgrade base` and `alembic upgrade head` all succeed on a database with data; you have reviewed and edited the autogenerated file.
- [ ] **Ex B5.5 Layered FastAPI + DB.** Rebuild Ex B4.1 on PostgreSQL with router → service → repository layers. The repository satisfies a `Repository[T]` Protocol; the session is a `yield` dependency that commits on success and rolls back on an exception. *Acceptance:* no router imports SQLAlchemy; a request that fails halfway leaves no partial write (prove it with a test or a manual check).
- [ ] **Ex B5.6 Reporting query.** Add a category tree to Ex B5.5 (`parent_id`) and two endpoints: all descendants of a category (recursive CTE) and item counts with subtotals per category + a grand total (`GROUP BY ROLLUP`). *Acceptance:* results are correct on a 4-level tree; the CTE is protected against cycles; the ROLLUP subtotals add up to the grand total.

### Must be able to do / explain
- [ ] Explain the Session: identity map, unit of work, flush vs commit, expire on commit.
- [ ] Write 2.0-style queries with joins, filters and loading options.
- [ ] Detect and fix an N+1 problem, and choose between `selectinload` and `joinedload`.
- [ ] Use async SQLAlchemy correctly and explain its restrictions.
- [ ] Write, review, upgrade and downgrade Alembic migrations, including a data step.
- [ ] Explain why the router never touches the ORM, and what each layer owns.

**Estimated hours:** ~18h

### Self-check interview questions
1. What is the difference between `flush()` and `commit()`?
2. What is the identity map?
3. What is the N+1 problem and how do you fix it in SQLAlchemy?
4. `selectinload` vs `joinedload`: when would you use each?
5. Why does lazy loading fail with `AsyncSession`?
6. What can Alembic autogenerate NOT detect?
7. How do you add a NOT NULL column to a table that already has millions of rows?
8. What belongs in a service vs a repository?
9. What does `GROUP BY ROLLUP(category_id)` return?

---

**Answers**
1. `flush()` sends pending SQL to the database inside the current transaction; `commit()` flushes and then commits the transaction, making the changes durable and visible to others.
2. A per-session map from primary key to object: the same row loaded twice in one session is the same Python object.
3. One query for the parent list plus one query per parent for the children. Fix it with eager loading (`selectinload`/`joinedload`) or an explicit join.
4. `selectinload` issues a second `IN (...)` query; best for one-to-many collections (no row explosion). `joinedload` uses a JOIN in the same query; best for many-to-one/one-to-one.
5. Lazy loading does implicit IO when an attribute is accessed, which cannot be awaited; in async that IO must be explicit.
6. Among others: table and column renames (it sees drop + add), some constraint and type changes, server default changes, and anything data-related.
7. Add it as nullable (or with a server default), backfill in batches, then add the NOT NULL constraint (in PostgreSQL, `NOT VALID` check + `VALIDATE` to avoid a long lock). This is expand/contract, covered again in B23.
8. Service: business rules and orchestration ("cannot sell below zero"), transaction boundaries. Repository: data access only (queries), no business decisions.
9. One row per category with its aggregate, plus an extra row with `category_id` NULL holding the grand total.

---

## Module B6 — Auth I: Hashing, Sessions vs JWT, OAuth2 Password Flow, RBAC (~8h)

**Topics:** authentication vs authorization; password storage (never
encrypt, always hash with a slow, salted algorithm: argon2id or bcrypt;
work factors; why a fast hash is wrong); **hashing is CPU-bound**, so keep
it off the event loop; server-side sessions vs stateless tokens; **JWT**
structure (header, payload, signature), claims (`sub`, `exp`, `iat`,
`role`), HS256; short-lived access tokens and why revocation is hard; the
**OAuth2 password flow** as FastAPI implements it (`OAuth2PasswordBearer`,
`OAuth2PasswordRequestForm`); role-based access control with a
`require_role()` dependency; **object/record-level authorization** (a user
may only touch rows they own or are assigned to — IDOR/BOLA); user
enumeration and generic error messages.
(Refresh tokens, OAuth2/OIDC, RS256 and JWKS come in B11 and B18.)

### Lessons
- [ ] **B6.L1 Password storage.** OWASP Cheat Sheet Series: "Password Storage Cheat Sheet" (Argon2id, bcrypt, work factors, pepper).
- [ ] **B6.L2 Sessions.** OWASP: "Session Management Cheat Sheet" (session id properties, cookie attributes `HttpOnly`, `Secure`, `SameSite`).
- [ ] **B6.L3 JWT.** jwt.io "Introduction to JSON Web Tokens". RFC 7519 §4.1 "Registered Claim Names". OWASP: "JSON Web Token for Java Cheat Sheet" → sections on "None hashing algorithm", "Token sidejacking" and "No built-in token revocation" (the concepts are language-independent).
- [ ] **B6.L4 FastAPI security.** FastAPI Tutorial → "Security": "Security – First Steps", "Get Current User", "Simple OAuth2 with Password and Bearer", "OAuth2 with Password (and hashing), Bearer with JWT tokens". Use `pwdlib` or `argon2-cffi` for hashing and `PyJWT` for tokens.
- [ ] **B6.L5 Authorization.** OWASP: "Authorization Cheat Sheet" (deny by default, least privilege, checks on every request).

### Exercises (`backend/B06-auth/`)
- [ ] **Ex B6.1 Hashing benchmark.** Time SHA-256, bcrypt (cost 10 and 12) and argon2id (default params) for 100 hashes each. *Acceptance:* `hashing.md` with a timing table and a paragraph on why the slow ones are the right choice for passwords.
- [ ] **Ex B6.2 Login with JWT.** Add `/auth/register` and `/auth/login` to your B5 app: argon2id hashes, and a 15-minute access token carrying `sub` and `role`. *Acceptance:* a wrong email and a wrong password return the same error (no user enumeration); an expired token returns 401; hashing does not block the event loop (explain how you ensured it).
- [ ] **Ex B6.3 Decode a token.** Paste your token into jwt.io, then change the `role` claim by hand and send the modified token. *Acceptance:* the API rejects it; `jwt-notes.md` explains why the signature catches it, and why the payload is readable by anyone (so no secrets go in it).
- [ ] **Ex B6.4 RBAC dependency.** Write a `require_role(*roles)` dependency and protect write endpoints with `owner` and read endpoints with `staff`+. *Acceptance:* role checks live in one place; tests cover 401 (no token), 403 (wrong role) and 200 (right role).

### Must be able to do / explain
- [ ] Explain why passwords are hashed with a slow, salted algorithm, not encrypted.
- [ ] Explain the structure of a JWT and what the signature does and does not guarantee.
- [ ] Compare server-side sessions and JWTs (revocation, scaling, storage, CSRF exposure).
- [ ] Implement the OAuth2 password flow + JWT in FastAPI.
- [ ] Implement role checks in one reusable dependency.
- [ ] Explain user enumeration and how to prevent it.

**Estimated hours:** ~8h

### Self-check interview questions
1. Why not store passwords encrypted?
2. Why is bcrypt/argon2 preferred over SHA-256 for passwords?
3. What does a JWT signature guarantee? Is the payload secret?
4. Why are access tokens short-lived?
5. Sessions vs JWT: give one advantage of each.
6. Where should role checks live in a FastAPI app?
7. Why must "wrong email" and "wrong password" look the same to the client?

---

**Answers**
1. Encryption is reversible: whoever gets the key gets every password. A hash is one-way.
2. They are deliberately slow and salted, with tunable cost, which makes brute-force and rainbow-table attacks expensive. SHA-256 is fast by design.
3. Integrity and authenticity: nobody without the key changed it. The payload is only base64url-encoded, so anyone can read it.
4. A stateless token cannot easily be revoked, so a short lifetime limits the damage if it is stolen.
5. Sessions: instant revocation, small cookie. JWT: no server-side lookup per request, easy to verify across services.
6. In one reusable dependency (or a small authorization module), never copied into each handler.
7. Otherwise an attacker can find out which emails are registered.

---

## Module B7 — Transactions & Concurrency in Applications (~8h)

**Topics:** what a race condition looks like in a web app; **TOCTOU**
("check stock, then decrement" as two statements); the lost update
anomaly; three fixes and their trade-offs: **pessimistic row locks**
(`SELECT … FOR UPDATE`, `with_for_update()` in SQLAlchemy), an **atomic
conditional update** (`UPDATE … SET stock = stock - :q WHERE id = :id AND
stock >= :q` + check the row count), and **optimistic locking** with a
`version` column (SQLAlchemy `version_id_col`); a preview of Django's
`F()` expressions and `select_for_update()` (same ideas, used in P2/P3);
lock duration and why transactions must be short; deadlocks from
inconsistent lock order; `lock_timeout`; **idempotency basics** (retries
duplicate writes; unique constraints and client-supplied keys as the
defence; full idempotency keys come in B34); **writing a deterministic
race test**.

### Lessons
- [ ] **B7.L1 The anomalies.** *Designing Data-Intensive Applications* (Kleppmann), Ch.7 "Transactions": sections "Weak Isolation Levels" → "Preventing Lost Updates" (atomic writes, explicit locking, compare-and-set) and "Write Skew and Phantoms".
- [ ] **B7.L2 Row locks in PostgreSQL.** PostgreSQL docs §13.3.2 "Row-Level Locks" and the `SELECT` reference → "The Locking Clause" (`FOR UPDATE`, `NOWAIT`, `SKIP LOCKED`). Refresh 1C 2.7–2.8.
- [ ] **B7.L3 Locks and versioning in SQLAlchemy.** SQLAlchemy docs: `Select.with_for_update()` (API reference) and ORM docs "Configuring a Version Counter" (`version_id_col`, `StaleDataError`).
- [ ] **B7.L4 The Django way (preview).** Django docs: "Query Expressions → F() expressions" (and "Avoiding race conditions using F()") and QuerySet API reference → `select_for_update()`.
- [ ] **B7.L5 Idempotency basics.** Stripe engineering blog: "Designing robust and predictable APIs with idempotency" (Brandur Leach). Just the problem statement and the idea; the full implementation is B34.

### Exercises (`backend/B07-concurrency/`)
- [ ] **Ex B7.1 Reproduce the race.** An endpoint `POST /tickets/{id}/buy` implemented naively (read `remaining`, check it in Python, write `remaining - 1`). Fire 50 concurrent requests with `remaining = 10`. *Acceptance:* you show overselling (more than 10 successes, or `remaining` < 0) and explain the interleaving that caused it.
- [ ] **Ex B7.2 Three fixes.** Fix Ex B7.1 three ways, in separate branches or functions: `FOR UPDATE`, an atomic conditional `UPDATE`, and optimistic locking with a `version` column plus retry. *Acceptance:* each version sells exactly 10 under the same load; `fixes.md` compares them (lock waits, retries, throughput, complexity).
- [ ] **Ex B7.3 A deterministic race test.** Write a pytest test that runs two buyers for the last ticket at the same time against a real Postgres and asserts exactly one success and one clean `409`. *Acceptance:* the test fails reliably on the naive version and passes on the fixed one (use two separate sessions/connections and `asyncio.gather` or threads + a barrier).
- [ ] **Ex B7.4 Make a deadlock.** Two transactions updating rows A and B in opposite orders. *Acceptance:* PostgreSQL reports `deadlock detected`; you then fix it with a consistent lock order and explain why that works.
- [ ] **Ex B7.5 Duplicate submission.** Simulate a client retry of `POST /orders` after a timeout. *Acceptance:* without protection two orders are created; with a client-supplied `request_id` + UNIQUE constraint, the retry returns the original order instead of a new one.

### Must be able to do / explain
- [ ] Explain TOCTOU and the lost update anomaly with a concrete timeline.
- [ ] Choose between a row lock, an atomic conditional update and optimistic locking.
- [ ] Explain what `FOR UPDATE` locks and for how long.
- [ ] Write a race test that fails on buggy code and passes on fixed code.
- [ ] Explain how deadlocks happen and the standard prevention.
- [ ] Explain why retries make idempotency necessary.

**Estimated hours:** ~8h

### Self-check interview questions
1. Two users buy the last item at the same time. What can go wrong and how do you prevent it?
2. What does `SELECT … FOR UPDATE` lock, and when is the lock released?
3. When is optimistic locking better than pessimistic locking?
4. Why is `UPDATE … WHERE stock >= :qty` safe without an explicit lock?
5. How do you prevent deadlocks?
6. How do you test a race condition deterministically?
7. What does `F('stock') - 1` do in Django, and why is it safer than `obj.stock -= 1`?
8. Why do retries require idempotency?

---

**Answers**
1. Both read stock = 1, both pass the check, both decrement, so you oversell. Prevent it by making check + write atomic: a row lock, a conditional update checking the affected row count, or optimistic locking.
2. The selected rows, against other writers and other `FOR UPDATE` readers (plain SELECTs still read). The lock lasts until the transaction commits or rolls back.
3. When conflicts are rare and you don't want to hold locks (e.g. long user think-time, low contention). Under high contention the retries get expensive.
4. The row-level check and the write happen in one statement. PostgreSQL locks the row while updating and re-checks the WHERE condition on the latest version.
5. Always lock rows in a consistent order, keep transactions short, and set `lock_timeout`; retry when a deadlock is reported.
6. Real database, two separate connections, start them together (barrier or gather), and assert on outcomes and final state; repeat it in a loop to be sure.
7. It makes the database compute `stock = stock - 1` in the UPDATE itself, instead of writing back a value Python read earlier, which is a lost update.
8. The client cannot tell whether a timed-out request succeeded, so it retries; without idempotency every retry may create a duplicate.

---

## Module B8 — Testing Web Applications (~10h)

**Topics:** the test pyramid for a web backend (unit tests of services with
fakes, integration tests against a **real PostgreSQL**, a few API tests);
pytest fixtures with scopes; a **per-test transaction that is rolled back**
(or recreate the schema); testing FastAPI with `TestClient` and
**`httpx.AsyncClient` + ASGI transport**; dependency overrides; **factory_boy**
for test data (SQLAlchemy factories, sub-factories, sequences);
**Hypothesis** for pure domain logic (money math, stock math) with a
pinned seed in CI; testing migrations up and down; asserting a query plan
uses an index; **coverage** where the rules live (services, repositories);
a first light load test with **`hey`** and how to read p50/p95/p99.

### Lessons
- [ ] **B8.L1 Fixtures in depth.** pytest docs: "How to use fixtures" (scope, `yield` fixtures, `conftest.py`, factories as fixtures), "How to parametrize fixtures and test functions".
- [ ] **B8.L2 Testing FastAPI.** FastAPI docs: Tutorial "Testing", Advanced "Async Tests", Advanced "Testing Dependencies with Overrides". httpx docs: "Async Support" → "Calling into Python Web Apps" (`ASGITransport`).
- [ ] **B8.L3 A real database per test.** SQLAlchemy docs: "Joining a Session into an External Transaction (such as for test suites)". pytest-asyncio docs: "Concepts" and fixture scopes/event loop scope.
- [ ] **B8.L4 Test data.** factory_boy docs: "Introduction", "Reference" (Sequence, SubFactory, LazyAttribute) and "ORMs → SQLAlchemy".
- [ ] **B8.L5 Properties and coverage.** Hypothesis docs: "Quick start guide", "Settings" (`derandomize`, `seed`, profiles). coverage.py docs: "Quick start", "Branch coverage". pytest-cov README.
- [ ] **B8.L6 Load testing basics.** `hey` README (github.com/rakyll/hey). Gil Tene's talk "How NOT to Measure Latency" (the first 20 minutes: percentiles and coordinated omission).

### Exercises (`backend/B08-testing/`)
- [ ] **Ex B8.1 Test infrastructure.** For your B5 app: a session-scoped Postgres (the Compose one or a separate test database), migrations applied once, and a per-test transaction rolled back after each test. *Acceptance:* tests can run in any order; no test sees another test's data; the full suite runs in under 10 s.
- [ ] **Ex B8.2 API tests with httpx.** Test every endpoint through `httpx.AsyncClient(transport=ASGITransport(app=...))`: happy path, validation error, not found, auth failures. *Acceptance:* at least one test per status code the API can return.
- [ ] **Ex B8.3 Factories.** Replace hand-written test data with factory_boy factories (including a SubFactory for a relation and a Sequence for unique fields). *Acceptance:* no test builds a model by hand.
- [ ] **Ex B8.4 Properties.** Write Hypothesis tests for a `Money` value object (addition is associative and commutative; adding and subtracting the same amount is the identity; negative amounts are rejected). *Acceptance:* runs with a pinned profile in CI; a deliberately introduced bug is caught and shrunk.
- [ ] **Ex B8.5 Migration and plan tests.** A test that runs `alembic downgrade base` + `upgrade head`, and a test asserting that a filtered query uses an index scan (parse `EXPLAIN (FORMAT JSON)`). *Acceptance:* both pass; dropping the index makes the plan test fail.
- [ ] **Ex B8.6 Coverage and a load number.** Measure coverage for `services/` and `repositories/` only, and run `hey -z 30s -c 50` against a list endpoint. *Acceptance:* coverage ≥ 80% on those layers; `load.md` records p50/p95/p99 and requests/s, with one sentence on what limited throughput.

### Must be able to do / explain
- [ ] Set up isolated database tests with transactional rollback.
- [ ] Test async FastAPI endpoints with httpx and dependency overrides.
- [ ] Build test data with factories.
- [ ] Write a property-based test and explain shrinking.
- [ ] Test migrations and query plans.
- [ ] Run a basic load test and explain p95 vs average.

**Estimated hours:** ~10h

### Self-check interview questions
1. Why test against a real PostgreSQL rather than SQLite or mocks?
2. How do you keep database tests isolated from each other?
3. What is the difference between unit and integration tests in this app?
4. What is a factory and why is it better than fixtures full of literal data?
5. What does Hypothesis do that example-based tests don't?
6. Why is 100% coverage not the goal?
7. Why report p95/p99 instead of average latency?

---

**Answers**
1. Constraints, locking, SQL dialect features (ON CONFLICT, CTEs, JSONB) and transaction behaviour differ; mocks and SQLite hide exactly the bugs that matter.
2. A transaction per test that is rolled back (or a truncate/recreate between tests); never share mutable data between tests.
3. Unit: a service with its dependencies faked, no IO, fast. Integration: real repository + database (and HTTP layer) working together.
4. A factory generates valid objects with sensible defaults, so each test states only what matters to it; it is DRY and survives schema changes.
5. It generates many inputs, including edge cases you would not think of, checks a property, and shrinks a failure to a minimal counterexample.
6. Coverage shows what was executed, not what was verified. Spend effort where the business rules live, not on trivial glue.
7. The average hides the tail; users feel the slow requests, and at scale the tail is hit constantly.

---

## Module B9 — CI with GitHub Actions (~6h)

**Topics:** workflows, events (`push`, `pull_request`), jobs, steps,
runners; actions from the marketplace (`actions/checkout`,
`actions/setup-python`, `astral-sh/setup-uv`); **service containers**
(PostgreSQL for integration tests, health options); dependency **caching**;
a **matrix** (Python versions); quality gates in order: ruff → mypy →
pytest with coverage threshold; secrets and `GITHUB_TOKEN` permissions;
**building and pushing a Docker image to GHCR** with
`docker/build-push-action`; branch protection with required checks.

### Lessons
- [ ] **B9.L1 Concepts.** GitHub Docs: "Understanding GitHub Actions", "Workflow syntax for GitHub Actions" (`on`, `jobs`, `steps`, `needs`, `if`).
- [ ] **B9.L2 Python CI.** GitHub Docs: "Building and testing Python". astral-sh/setup-uv README (caching).
- [ ] **B9.L3 Service containers.** GitHub Docs: "About service containers", "Creating PostgreSQL service containers".
- [ ] **B9.L4 Caching and matrices.** GitHub Docs: "Caching dependencies to speed up workflows", "Running variations of jobs in a workflow" (matrix).
- [ ] **B9.L5 Images and permissions.** GitHub Docs: "Publishing Docker images", "Working with the Container registry", "Automatic token authentication" (`permissions:`). docker/build-push-action README (cache-from/cache-to `type=gha`).
- [ ] **B9.L6 Protecting main.** GitHub Docs: "About protected branches" (require status checks to pass).

### Exercises (`backend/B09-ci/` — or a throwaway repo, since workflows run per repo)
- [ ] **Ex B9.1 Lint and type gate.** A workflow running ruff and mypy on every push and pull request. *Acceptance:* a PR with a type error goes red; fixing it goes green.
- [ ] **Ex B9.2 Integration tests in CI.** Add a job with a `postgres:17` service container (health-cmd `pg_isready`) that runs your B8 test suite with a coverage threshold. *Acceptance:* tests pass in CI against the real database; dropping coverage below the threshold fails the job.
- [ ] **Ex B9.3 Faster pipeline.** Add dependency caching and a Python 3.12/3.13 matrix. *Acceptance:* the second run is measurably faster (record both times); both matrix legs are green.
- [ ] **Ex B9.4 Ship an image.** On pushes to `main` only, build your B3 multi-stage image and push it to GHCR tagged with the commit SHA, using the least `permissions:` needed. *Acceptance:* the image appears under your GitHub packages; PR builds do not push.
- [ ] **Ex B9.5 Branch protection.** Protect `main` so the lint and test jobs are required. *Acceptance:* a PR with a failing check cannot be merged (screenshot or note in `ci.md`).

### Must be able to do / explain
- [ ] Write a workflow with jobs, dependencies (`needs`) and conditions.
- [ ] Run integration tests against a service container.
- [ ] Use caching and a matrix, and explain what each costs and saves.
- [ ] Build and push an image to GHCR with least-privilege token permissions.
- [ ] Explain why CI should confirm what pre-commit already checked locally.

**Estimated hours:** ~6h

### Self-check interview questions
1. What is the difference between a job and a step?
2. How do you run tests against PostgreSQL in GitHub Actions?
3. Why pin action versions (or SHAs)?
4. What does the `permissions:` block protect against?
5. Why tag images with the commit SHA instead of only `latest`?
6. What order would you run lint, type check and tests in, and why?

---

**Answers**
1. A job runs on its own runner and jobs can run in parallel; steps run sequentially inside one job and share its filesystem.
2. Declare a `services: postgres:` container with health options, and connect to it via `localhost` and the mapped port (or the service name when the job runs in a container).
3. Supply-chain safety and reproducibility: a moving tag can change underneath you, or be hijacked.
4. It limits what `GITHUB_TOKEN` can do if a step or action is compromised (least privilege).
5. `latest` is mutable and ambiguous; a SHA tag is immutable and traceable to exact code, which makes rollbacks reliable.
6. Fastest and cheapest first (ruff, then mypy, then tests), so failures show up quickly and you save runner minutes.

---

## Project P1 — StockPilot · Junior (~60h)

**Single-store inventory & order management API.**

> **What this project is really for.** One architectural habit — the router
> never touches the ORM — and one correctness problem — two people selling
> the last unit at the same time. Everything else is scaffolding around
> those two lessons.

### Goal
A small shop tracks stock in a spreadsheet: counts drift, staff oversell
items that are out of stock, nobody knows who changed what, and the owner
has no view of orders or slow movers. StockPilot replaces the spreadsheet
with an authenticated API (a future POS or frontend plugs into it). Stock
changes only through audited movements, orders never oversell, and the
owner gets the three reports they asked for.

### Features
- [ ] JWT login with two roles, `owner` and `staff`, enforced by one `require_role()` dependency
- [ ] CRUD for products, categories (self-referencing hierarchy) and suppliers
- [ ] Stock changes **only** through an audited `stock_movements` insert (delta, reason, user). There is deliberately no "set stock" endpoint
- [ ] Orders created with their items in one transaction; stock decremented atomically; any short line → the whole order is refused with `409`
- [ ] Order status machine: `pending → partially_fulfilled → fulfilled | cancelled`
- [ ] `unit_price_cents` captured at order time (later price changes don't rewrite history)
- [ ] `GET /categories/{id}/tree` with a recursive CTE (with a cycle guard)
- [ ] Reports: stock value with `ROLLUP` subtotals per category + a grand total (owner only), low-stock list, orders in a date range by status
- [ ] Offset pagination on `/products`; **keyset (cursor) pagination** on `/orders`, benchmarked against offset on 500k rows
- [ ] A frozen `Money` value object (integer cents) used everywhere
- [ ] One structured JSON log line per request (method, path, status, latency, `user_id`)
- [ ] `docker compose up` brings the whole system up from a clean clone

**Roles**

| Role | Can | Cannot |
|---|---|---|
| `owner` | Everything, including deletes and revenue/stock-value reports | — |
| `staff` | List/view products, create stock movements and orders, change order status, view the low-stock report | Delete products; view stock-value/revenue reports |

**Domain model**
```
users(id, email UNIQUE, hashed_password, role, created_at)
categories(id, name, parent_id NULL -> categories.id)
suppliers(id, name, contact_email)
products(id, sku UNIQUE, name, category_id, supplier_id, price_cents, current_stock, reorder_level)
stock_movements(id, product_id, delta, reason, created_by -> users.id, created_at)
orders(id, status, created_by -> users.id, created_at)
order_items(id, order_id, product_id, qty, unit_price_cents)
```
`products.current_stock` is a **denormalized cache** of the `stock_movements`
event log, updated only in the same transaction as a movement insert.
Be ready to defend that trade-off.

**API**

| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/auth/login` | public | Short-lived JWT |
| GET | `/products` | staff+ | `category_id`, `low_stock`, `page`, `page_size` (offset) |
| POST | `/products` | owner | |
| PATCH | `/products/{id}` | owner | |
| POST | `/products/{id}/stock-movements` | staff+ | `delta`, `reason`; audited |
| GET | `/categories/{id}/tree` | staff+ | Recursive CTE |
| GET | `/orders` | staff+ | `status`, `from`, `to`, `cursor`, `limit` (keyset) |
| POST | `/orders` | staff+ | Atomic decrement; `409` if insufficient |
| GET | `/orders/{id}` | staff+ | Order + items + products (the N+1 lives here) |
| PATCH | `/orders/{id}/status` | staff+ | |
| GET | `/reports/stock-value` | owner | `ROLLUP` by category |
| GET | `/reports/low-stock` | staff+ | `current_stock < reorder_level` |

Error contract: insufficient stock → 409, validation → 422, missing role →
403. Never a 500 for a condition you anticipated.

**Business rules (invariants)**
1. Stock can never go below zero (checked in the service **and** by a DB `CHECK`).
2. `current_stock` changes only through a `stock_movements` insert, in the same transaction.
3. Every stock-changing action is traceable to a `user_id`.
4. Two concurrent orders for the last unit → exactly one succeeds.
5. A router function never touches SQLAlchemy directly.

### Tech stack

| Tool / technique | Where it is taught |
|---|---|
| Python 3.12+, dataclasses (`Money`), `Protocol` (`Repository[T]`) | 1A.6, 1A.7 |
| FastAPI, Pydantic v2, pydantic-settings, DI, error contract | B4 |
| structlog request logging | 1A.9, B4 |
| asyncio: `gather`, blocking calls, `run_in_executor` | 1A.12, B4.L7 |
| PostgreSQL: constraints, `timestamptz`, data types | 1C 1.5, 1C 1.6 |
| Recursive CTE | 1C 2.1, B5.L6 |
| `GROUP BY ROLLUP` | B5.L6 |
| Indexes, composite column order, `EXPLAIN ANALYZE`, keyset pagination | 1C 2.5, 1C 2.6 |
| SQLAlchemy 2.0 async, Alembic, layered architecture | B5 |
| Password hashing (argon2id/bcrypt), JWT, RBAC | B6 |
| Row locks / atomic conditional update, race tests | B7, 1C 2.8 |
| pytest, httpx, factory_boy, Hypothesis, coverage, `hey` | 1A.8, B8 |
| ruff, mypy, pre-commit, gitleaks/detect-secrets | 1A.7, 1A.9 |
| Docker multi-stage non-root image, Compose with Postgres healthcheck | B3 |
| GitHub Actions with a Postgres service container | B9 |

### Required knowledge
1A.1–1A.12 (especially 1A.6, 1A.7, 1A.8, 1A.9, 1A.12) · 1C 1.1–1.7, 1C 2.1,
2.5, 2.6, 2.7, 2.8 · B1–B9.

### Milestones

**M1 — Skeleton & data layer (~14h)**
- [ ] Repo scaffold: folder layout below, `pyproject.toml`, ruff + mypy config, pytest wired, one trivial passing test
- [ ] All ORM models defined at once (`User`, `Product`, `Category`, `Supplier`, `StockMovement`, `Order`, `OrderItem`); all timestamps `timestamptz`
- [ ] Alembic initialised; the initial migration verified **up and down**
- [ ] `core/config.py` (pydantic-settings from `.env`) and `db/session.py` (async engine + session factory)
- [ ] Multi-stage, non-root `Dockerfile` + `.dockerignore`; image size recorded
- [ ] `docker-compose.yml`: `api` + `postgres` with a real healthcheck
- [ ] `pre-commit` with ruff, mypy and a secret scanner
- [ ] `docs/notes.md`: the `timestamptz` decision, the UUID-vs-bigint primary-key decision, the password-hashing choice
- [ ] *Done when:* `docker compose up` boots both services, migrations run, tests pass, and `docker run --rm <image> whoami` is not `root`. Suggested tag: `m1-skeleton`

```
StockPilot/
  app/
    api/           # routers + Pydantic schemas
    services/      # business rules
    repositories/  # SQLAlchemy queries only
    models/        # ORM models
    core/          # config, security, logging
    db/            # session, base
  alembic/
  tests/{unit,integration}/ + factories.py
  docs/
  Dockerfile  docker-compose.yml  .github/workflows/ci.yml
```

**M2 — Products vertical slice & auth (~14h)**
- [ ] `/auth/login` with argon2id/bcrypt (off the event loop) and a short-lived JWT carrying `role`; `require_role()` dependency
- [ ] Product repository → service → router; the session is a `yield` dependency that rolls back on failure
- [ ] `GET /products` with filters and offset pagination; edge cases tested (empty page, last page, page beyond the end)
- [ ] `POST /products/{id}/stock-movements` updating `current_stock` in the same transaction
- [ ] `GET /categories/{id}/tree` with `WITH RECURSIVE`; tested on a 4-level tree and with a cycle guard
- [ ] Review pass: find any business rule that leaked into a schema or handler, and move it
- [ ] *Done when:* products work end to end, and a failing request leaves no partial write. Tag: `m2-products`

**M3 — Typing discipline, value objects & SQL (~16h)**
- [ ] `SupplierRepository`, `CategoryRepository`; every repository satisfies a `Repository[T]` Protocol; mypy is a real CI gate
- [ ] `Money` frozen dataclass replaces raw cent ints in business code
- [ ] `EXPLAIN ANALYZE` on "orders in a date range by status": see the seq scan, **then** add the `(status, created_at)` index via a migration; a test asserts an index scan
- [ ] Seed 500k orders; keyset pagination on `GET /orders`; `OFFSET 400000` vs keyset plans recorded in `docs/scaling-notes.md`
- [ ] `GET /reports/stock-value` with `ROLLUP` (subtotals + grand total) and `GET /reports/low-stock`
- [ ] Async exercise on `GET /orders/{id}`: sequential awaits vs `asyncio.gather` vs one joined query, timed; then a deliberately blocking call in a handler, fixed with `run_in_executor`; two sentences in `docs/notes.md`
- [ ] `docs/notes.md`: where descriptors *could* replace repeated validators, and why you rejected that
- [ ] *Done when:* mypy strict passes in CI; both plans are recorded. Tag: `m3-typing-sql`

**M4 — Orders, concurrency & hardening (~16h)**
- [ ] `OrderService.create_order`: the happy path first, with **no** concurrency handling, on purpose
- [ ] Break it with a race test (two concurrent orders for the last unit); then fix it with `SELECT … FOR UPDATE` or an atomic `UPDATE … WHERE current_stock >= :qty`
- [ ] Insufficient stock → clean `409`; the whole order is refused if any line is short
- [ ] Order status transitions; `GET /orders/{id}` without N+1
- [ ] factory_boy factories replace hand-written data; a Hypothesis property test on stock/pricing math with a pinned seed
- [ ] structlog JSON line per request with `user_id`
- [ ] Final `.github/workflows/ci.yml`: ruff → mypy → pytest (Postgres service container, coverage ≥ 80% on services + repositories)
- [ ] Load test `GET /products` with `hey`; `docs/scaling-notes.md` (what breaks first and in what order you'd fix it); `docs/postmortem.md`
- [ ] *Done when:* see Definition of done. Tag: `v1.0-stockpilot`

**Deliberately NOT in this project (write a TODO for each, with why):**
Redis cache (→ P2: you haven't measured a slow read yet), Celery alerts
(→ P3: the synchronous version must hurt first), refresh tokens/OAuth
(→ P2/P5), metrics and dashboards (→ P6), deployment to a server
(→ P6, after B23).

### Definition of done
- [ ] All endpoints implemented and integration-tested
- [ ] Overselling proven impossible by a passing concurrency test
- [ ] mypy and ruff clean, both gating CI
- [ ] 80%+ coverage on `services/` and `repositories/`
- [ ] Every migration reversible, and tested that way
- [ ] Composite index added from a real `EXPLAIN ANALYZE`, with a plan assertion
- [ ] Keyset pagination on `/orders`; offset-vs-keyset plans recorded
- [ ] Recursive-CTE category tree and `ROLLUP` report tested (subtotals add up to the grand total)
- [ ] All timestamps `timestamptz`; PK and password-hashing decisions in `docs/notes.md`
- [ ] Multi-stage, non-root Dockerfile; `pre-commit` configured
- [ ] `Money` used consistently; no raw cent ints in business code
- [ ] `docker compose up` works from a clean clone
- [ ] `docs/notes.md`, `docs/scaling-notes.md`, `docs/postmortem.md` written

**Estimated hours:** ~60h (M1 14 · M2 14 · M3 16 · M4 16)

### OPTIONAL extension — demand baseline (ML, ~12h)
*Requires Track 3: ML Zoomcamp modules 1–2 (Intro, Regression).*
`stock_movements` is already an append-only event log, so it is good raw
material for a first brush with data work.
- [ ] `analytics/export_analytics.py`: read-only export of orders + items + movements into a weekly Parquet file, one row per `(product_id, iso_week)`, with explicit zero rows for weeks with no sales
- [ ] `analytics/forecast.py`: a lag-feature linear regression (scikit-learn) vs a naive "next week = this week" baseline; MAE and RMSE for both; deterministic with a fixed seed
- [ ] `docs/forecast-notes.md`: one honest sentence on whether the model beat the baseline

### Interview questions about this project
1. How did you prevent overselling the last unit under concurrent requests, and how did you prove it?
2. Why is `current_stock` denormalized, and what keeps it correct?
3. Walk me through your layers. Why does the router never touch the ORM?
4. Offset vs keyset pagination: what did your two plans show, and when is offset still fine?
5. What happens when a blocking call (e.g. password hashing) runs inside an async handler, and how did you fix it?

---

**Answers**
1. Check and decrement happen atomically, with a row lock (`FOR UPDATE`) or a conditional `UPDATE … WHERE current_stock >= :qty` with a row-count check, inside one transaction with the order insert. A race test with two concurrent orders for the last unit asserts exactly one 201 and one 409, backed by a DB `CHECK (current_stock >= 0)`.
2. Summing movements on every read is correct but slow; a mutable number alone is fast but unauditable. `stock_movements` is the truth (event log), `current_stock` is a cache updated only in the same transaction as each movement insert, so the two cannot diverge.
3. Router: HTTP shape only. Service: business rules and transaction boundaries. Repository: queries only. This keeps the rules testable without HTTP or a database, and lets the web framework change without touching the rules.
4. `OFFSET 400000` reads and throws away 400k rows, so it gets slower with every page; keyset seeks directly through the `(created_at, id)` index in constant time. Offset is still fine for small tables and "jump to page 7" admin screens.
5. It blocks the event loop, so every other request on that worker stalls. The fix is `run_in_executor`/`run_in_threadpool` (or a `def` endpoint); CPU-heavy work belongs off the loop.

---

## Module B10 — Django (~18h)

**Why now:** QuickServe is admin-heavy. A manager must browse receipts without
an API client, and Django Admin gives you that almost for free. After FastAPI
(B4) you learn the "batteries included" framework. By the end you must be able
to argue when you would choose each one.

**Topics:**
- Project vs app structure; `manage.py`; `INSTALLED_APPS`; request → URLconf → view → response cycle
- Models, fields, `Meta` (indexes, constraints, ordering), relations (FK, O2O, M2M), `related_name`
- Migrations: `makemigrations`, `migrate`, `sqlmigrate`, data migrations (`RunPython`), reversibility, squashing
- QuerySet API: laziness, chaining, evaluation points, `values()`/`values_list()`, `annotate()`/`aggregate()`, `exists()`, `count()`, `iterator()`
- Complex lookups with `Q()`; `F()` expressions for atomic updates (`update(stock=F("stock") - 1)`) and field-to-field comparisons
- `select_related` (JOIN, FK/O2O) vs `prefetch_related` (second query, reverse FK/M2M); `Prefetch` objects
- Spotting N+1 queries with `django-debug-toolbar`; proving the fix with `assertNumQueries`
- Transactions: `ATOMIC_REQUESTS`, `transaction.atomic`, savepoints, `select_for_update()` (`nowait`, `skip_locked`), `transaction.on_commit`
- PostgreSQL-specific fields in `django.contrib.postgres`: `DateRangeField`, `ArrayField`, range lookups (`overlap`), `ExclusionConstraint`
- Time zones: `USE_TZ=True`, aware vs naive datetimes, `timezone.now()`, `date` vs `datetime`
- Django Admin customization: `list_display`, `list_filter`, `search_fields`, inlines, `readonly_fields`, custom actions, `get_queryset` scoping
- Settings split (base/dev/prod), secrets from env vars
- Service layer and thin views instead of "fat models"
- CSRF protection: why session auth needs it and header-based token auth does not

### Lessons
- [ ] **B10.1 First Django project** — Django docs "Writing your first Django app", parts 1–4 (docs.djangoproject.com/en/stable/intro/tutorial01/); Two Scoops of Django 3.x, chapter "How to Lay Out Django Projects" and "Fundamentals of Django App Design".
- [ ] **B10.2 Models and migrations** — Django docs Topics → "Models"; "Migrations"; Reference → "Model field reference", "Model Meta options" (`indexes`, `constraints`); Two Scoops chapter "Model Best Practices".
- [ ] **B10.3 QuerySets in depth** — Django docs Topics → "Making queries" (including "Complex lookups with Q objects" and "Filters can reference fields on the model", i.e. `F()`); Reference → "QuerySet API reference"; "Query Expressions"; Two Scoops chapter "Queries and the Database Layer".
- [ ] **B10.4 Query optimization and N+1** — Django docs Topics → "Database access optimization"; QuerySet API reference sections `select_related()` and `prefetch_related()`; django-debug-toolbar docs "Installation" (django-debug-toolbar.readthedocs.io); Django docs "Testing tools" → `assertNumQueries`.
- [ ] **B10.5 Transactions and row locks in Django** — Django docs Topics → "Database transactions" (`atomic`, `on_commit`, savepoints); QuerySet API reference → `select_for_update()`. Cross-reference: 1C Module 2.8 (FOR UPDATE / SKIP LOCKED) and B7.
- [ ] **B10.6 PostgreSQL fields and time zones** — Django docs Reference → "django.contrib.postgres" → "PostgreSQL specific model fields" (Range fields, `ArrayField`) and "PostgreSQL specific database constraints" (`ExclusionConstraint`); Topics → "Time zones".
- [ ] **B10.7 Django Admin** — Django docs "The Django admin site" (ModelAdmin options, InlineModelAdmin, admin actions); tutorial part 7.
- [ ] **B10.8 Settings, environments, service layer, CSRF** — Two Scoops chapter "Settings and Requirements Files"; Django docs "Django settings" and "Deployment checklist"; Django docs "Cross Site Request Forgery protection" (How it works section); HackSoft Django Styleguide (github.com/HackSoftware/Django-Styleguide), sections "Services" and "Selectors".

### Exercises
- [ ] **Ex B10.1 Library catalogue** — Create a project `library/` with a `books` app: `Author`, `Book` (FK to Author), `Tag` (M2M). Add one DB-level `UniqueConstraint` and one `CheckConstraint`. *Acceptance:* `manage.py check` passes, migrations apply and roll back (`migrate books zero`), and `sqlmigrate` output is saved to `notes.md` with one sentence per constraint.
- [ ] **Ex B10.2 QuerySet drills** — Write a management command that seeds 1 000 books, then answer 8 questions using only the ORM (e.g. authors with more than 5 books, books without tags, average books per tag, books whose `updated_at` is later than `published_at` using `F()`, titles matching A OR B using `Q()`). *Acceptance:* each answer prints the SQL (`str(qs.query)`), and you can say at which line each QuerySet is evaluated.
- [ ] **Ex B10.3 Find and kill the N+1** — Build a view listing every book with its author and tags. First write it naively, measure the query count with django-debug-toolbar, then fix it. *Acceptance:* a test with `assertNumQueries(N)` where N stays constant for 10 and 100 books; `notes.md` explains why `select_related` fits one relation and `prefetch_related` fits the other.
- [ ] **Ex B10.4 Race-free borrow** — Add `copies_available` and a `borrow(book_id)` service. Implement two versions: (a) `select_for_update()` inside `atomic`; (b) a single `update(... F() - 1)` with a `filter(copies_available__gt=0)` guard. *Acceptance:* a threaded test with 20 concurrent borrows of 5 copies ends with exactly 5 successes and 0 negative stock, for both versions.
- [ ] **Ex B10.5 Admin a librarian can use** — Customize admin for `Book`: list display, filters, search, author inline, read-only audit fields, and an admin action "mark as out of print". *Acceptance:* a non-developer can find "all books by X tagged Y" in under 30 seconds.
- [ ] **Ex B10.6 Settings split + time zone check** — Split settings into `base/dev/prod`, read secrets from env vars, set `USE_TZ=True`. Write a test showing why comparing a naive `datetime` with an aware one fails, and how `timezone.now()` fixes it.

### Must be able to do / explain
- [ ] Draw the Django request/response cycle, including where middleware runs.
- [ ] Say when a QuerySet hits the database and why it is lazy.
- [ ] Choose between `select_related` and `prefetch_related` and prove the choice with a query count.
- [ ] Use `F()` for an atomic update and say which race condition it removes.
- [ ] Say what `transaction.atomic` does, what a savepoint is, and why `select_for_update` must run inside a transaction.
- [ ] Write a reversible data migration.
- [ ] Customize the admin so a non-technical user can work with it.
- [ ] Argue "service layer + thin views" against "fat models".
- [ ] Say why Django session views need CSRF protection and a JWT-in-header API does not.

**Estimated time:** ~18h

### Self-check interview questions
1. Django or FastAPI for a new project — how do you decide?
2. What is the difference between `select_related` and `prefetch_related`? What SQL does each produce?
3. How do you detect N+1 queries in Django, in development and in tests?
4. What does `F()` do, and why is `obj.stock -= 1; obj.save()` dangerous?
5. What happens if you call `select_for_update()` outside a transaction?
6. What is `transaction.on_commit` for?
7. How do you make a data migration safe to reverse?
8. Why is `USE_TZ=True` important, and what goes wrong without it?
9. Why might a team reject "fat models, thin views"?

---

#### Answers
1. Pick Django when you need admin, auth, ORM, migrations and forms out of the box, the domain is CRUD-heavy, and sync is fine. Pick FastAPI for API-only services, async I/O, strong typing with Pydantic, and a small footprint. Team experience and the ecosystem also matter. The honest answer names the trade-offs, not "what I know".
2. `select_related` adds a SQL JOIN and works for FK/one-to-one (forward). `prefetch_related` runs a second query with `WHERE id IN (...)` and joins in Python. It works for reverse FK and M2M.
3. In development, use django-debug-toolbar's SQL panel (duplicate queries). In tests, use `assertNumQueries` with a count that stays constant as data grows. You can also log `connection.queries` with `DEBUG=True`.
4. `F()` refers to the column's value inside SQL, so the update happens as one atomic `UPDATE ... SET stock = stock - 1`. Read-modify-write in Python is a lost-update race: two requests read 5 and both write 4.
5. On PostgreSQL with autocommit, Django raises `TransactionManagementError` when the queryset is evaluated. The lock would be released straight away, so it would be meaningless.
6. It runs a callback only after the outermost transaction commits. You use it to enqueue tasks or send notifications so they never fire for work that rolled back, and never run before the data is visible.
7. Give `RunPython` a `reverse_code` function (or `migrations.RunPython.noop` when that is honestly right), keep the transformation idempotent, and test `migrate app <previous>`.
8. With `USE_TZ=True`, datetimes are stored in UTC and are timezone-aware. Without it you get naive datetimes, which break across DST changes and servers in different time zones, and comparisons between aware and naive values raise errors.
9. Fat models turn into god objects that every app imports, and their logic is hard to test without the ORM. Side effects end up in `save()` and signals. A service layer keeps business rules explicit, testable and framework-agnostic.

---

## Module B11 — Django REST Framework (~14h)

**Topics:**
- Serializers: `Serializer` vs `ModelSerializer`, field-level and object-level validation, nested and read-only fields, `to_representation`
- Views: `APIView`, generic views, `ViewSet`/`ModelViewSet`, `@action`, routers
- Authentication vs authorization; `SessionAuthentication` vs token/JWT authentication
- Permissions: global, view-level, object-level (`has_object_permission`), relationship-based permissions ("manager of this employee")
- Throttling internals: `AnonRateThrottle`, `UserRateThrottle`, `ScopedRateThrottle`, cache-backed counters, why throttling needs a shared cache when you run several processes
- `djangorestframework-simplejwt`: access vs refresh token, lifetimes, `ROTATE_REFRESH_TOKENS`, `BLACKLIST_AFTER_ROTATION`, token blacklist app
- Pagination: `PageNumberPagination`, `LimitOffsetPagination`, `CursorPagination`
- Filtering and search; exception handling; consistent error format
- Testing: `APIClient`, `APITestCase`, `force_authenticate`, testing permissions and throttles
- OpenAPI schema generation (drf-spectacular)

### Lessons
- [ ] **B11.1 DRF tutorial** — DRF docs "Tutorial" parts 1–6 (www.django-rest-framework.org/tutorial/1-serialization/).
- [ ] **B11.2 Serializers and validation** — DRF API Guide → "Serializers", "Serializer fields", "Serializer relations", "Validators".
- [ ] **B11.3 Views, ViewSets, routers** — DRF API Guide → "Generic views", "ViewSets" (including "Marking extra actions for routing"), "Routers".
- [ ] **B11.4 Auth and permissions** — DRF API Guide → "Authentication", "Permissions" (object-level permissions, custom permissions). Cross-reference: B6 (Auth I).
- [ ] **B11.5 JWT with simplejwt** — django-rest-framework-simplejwt docs (django-rest-framework-simplejwt.readthedocs.io): "Getting started", "Settings" (`ACCESS_TOKEN_LIFETIME`, `REFRESH_TOKEN_LIFETIME`, `ROTATE_REFRESH_TOKENS`, `BLACKLIST_AFTER_ROTATION`), "Blacklist app".
- [ ] **B11.6 Throttling internals** — DRF API Guide → "Throttling" (read the section "Setting up the cache" and the source of `SimpleRateThrottle.allow_request` in `rest_framework/throttling.py`).
- [ ] **B11.7 Pagination, filtering, errors, schema** — DRF API Guide → "Pagination", "Filtering", "Exceptions"; drf-spectacular docs "Usage".
- [ ] **B11.8 Testing DRF** — DRF API Guide → "Testing" (`APIClient`, `force_authenticate`, `APITestCase`).

### Exercises
- [ ] **Ex B11.1 Library API** — Put the B10 library behind DRF: `ModelViewSet` for books, nested author (read) and `author_id` (write), and an `@action` `POST /books/{id}/borrow/` that calls the B10 service. *Acceptance:* the viewset holds no business logic; there are validation tests for 3 invalid payloads.
- [ ] **Ex B11.2 Relationship-based permission** — Add `Member` with a `librarian` FK. Only a member's own librarian may extend their loan. *Acceptance:* tests cover own librarian → 200, another librarian → 403, the member themself → 403, anonymous → 401.
- [ ] **Ex B11.3 JWT with rotation** — Configure simplejwt with a 5-minute access token, a 1-day refresh token, rotation and blacklist. *Acceptance:* a test shows that reusing an old refresh token after rotation fails; `notes.md` lists which claims are in each token.
- [ ] **Ex B11.4 Throttle and prove it** — Add `ScopedRateThrottle` with scope `borrow` = 5/min. *Acceptance:* the 6th request inside a minute gets 429 with `Retry-After`. Explain in `notes.md` why a locmem cache breaks this under 2 gunicorn workers.
- [ ] **Ex B11.5 Cursor pagination** — Add `CursorPagination` to `/books/` ordered by `created_at`. *Acceptance:* inserting a row between page 1 and page 2 neither duplicates nor skips rows (test it); explain why offset pagination would.

### Must be able to do / explain
- [ ] Write serializer validation at field level and object level.
- [ ] Explain the difference between `has_permission` and `has_object_permission`, and when the second one is called.
- [ ] Implement a permission based on the relationship between two records.
- [ ] Explain what goes into an access token vs a refresh token, and what rotation + blacklisting protect against.
- [ ] Explain how DRF counts throttle hits and why the cache must be shared.
- [ ] Choose a pagination style for a feed vs an admin table.
- [ ] Test permissions and throttles with `APIClient`.

**Estimated time:** ~14h

### Self-check interview questions
1. What is the difference between authentication and authorization in DRF?
2. When is `has_object_permission` NOT called automatically?
3. Why keep access tokens short-lived even over HTTPS?
4. What does refresh-token rotation protect against, and what does the blacklist add?
5. How does DRF throttling work under the hood? What happens with several app processes and a local-memory cache?
6. Offset vs cursor pagination — trade-offs?
7. Where should business logic live in a DRF app, and why not in the serializer's `create()`?

---

#### Answers
1. Authentication works out who the caller is (it sets `request.user`). Authorization (permissions) decides whether that caller may do this action on this object.
2. It is not called for list views, and not when you override `get_object` without calling `self.check_object_permissions(request, obj)`. For lists you must filter the queryset yourself.
3. A stolen access token (from logs, browser storage, a proxy or an XSS) is valid until it expires. Short lifetimes limit the damage, because a JWT cannot be revoked without extra state.
4. With rotation, each refresh issues a new refresh token, so a stolen one has a short useful life. The blacklist makes the old token unusable, so reuse fails and can be detected.
5. `SimpleRateThrottle` stores a list of request timestamps per key in the Django cache and trims old entries on every request. If each process has its own local-memory cache, every process counts separately, so the real limit is N × rate. A shared cache (Redis) fixes this.
6. Offset is simple and lets you jump to page N, but it gets slow at deep offsets and shifts rows when data changes. Cursor (keyset) pagination is stable and fast but has no random access. Use cursor for feeds and infinite scroll, offset for small admin tables.
7. Keep it in a service layer that views call. Serializers should validate and convert data. Logic hidden in `create()` is hard to reuse from the admin, Celery tasks or a bot, and hard to test in isolation.

---

## Module B12 — Redis I: Caching and Rate Limiting (~12h)

**Topics:**
- What Redis is: an in-memory data-structure server, single-threaded command execution, why `KEYS *` is dangerous and `SCAN` is not
- Data structures: strings, hashes, lists, sets, sorted sets, TTL/`EXPIRE`, atomic `INCR`
- Key naming and namespacing (`products:search:<term>:<page>`); deleting by prefix with `SCAN`
- Caching patterns: cache-aside, read-through, write-through, write-behind; choosing TTLs; negative caching
- Invalidation: finding every write path (API, admin, migrations, management commands); an invalidation audit
- Cache stampede (thundering herd): TTL jitter, locking around cache population, probabilistic early expiration
- HTTP caching as a separate layer: `Cache-Control`, `ETag` + `If-None-Match` → `304`, `immutable`, `private` vs `public`
- Memory and durability: `maxmemory`, eviction policies (`allkeys-lru`, `volatile-ttl`, `noeviction`), RDB vs AOF persistence
- Rate limiting: fixed window (`INCR` + `EXPIRE`), sliding window (sorted set), token bucket (Lua script, atomicity)
- Django cache framework with the built-in Redis backend; redis-py; `fakeredis` for unit tests
- Measuring the effect: p50/p95 before and after with `hey` (B8)

### Lessons
- [ ] **B12.1 Redis data types** — redis.io docs "Understand Redis data types" (strings, hashes, lists, sets, sorted sets); "Redis keys" / `EXPIRE` command page; "Try Redis" in Docker (B3): `docker run -p 6379:6379 redis:7`.
- [ ] **B12.2 Caching patterns** — AWS whitepaper "Database Caching Strategies Using Redis" (sections "Caching patterns": cache-aside/lazy loading, write-through); Django docs "Django's cache framework" (the Redis backend, low-level cache API).
- [ ] **B12.3 Invalidation and stampede** — Wikipedia "Cache stampede" (sections on locking, external recomputation, probabilistic early expiration); Martin Fowler bliki "TwoHardThings".
- [ ] **B12.4 HTTP caching** — MDN "HTTP caching"; MDN reference pages "Cache-Control" and "ETag"; Django docs "Conditional View Processing" (`@condition`, `@etag`).
- [ ] **B12.5 Memory, eviction and persistence** — redis.io docs "Key eviction" and "Redis persistence" (RDB, AOF, trade-offs); the `SCAN` command page (guarantees and cost).
- [ ] **B12.6 Rate limiting** — redis.io `INCR` command page, section "Pattern: Rate limiter" (both patterns); redis.io docs "Scripting with Lua" (`EVAL`, atomicity); Stripe engineering blog "Scaling your API with rate limiters".
- [ ] **B12.7 Testing with Redis** — fakeredis docs (fakeredis.readthedocs.io) "Getting started"; redis-py docs "Connecting to Redis"/connection pools.

### Exercises
- [ ] **Ex B12.1 Data-structure tour** — In `redis-cli`, model: a page-view counter (string + `INCR`), a user profile (hash), a leaderboard (sorted set, top 10), and "unique visitors today" (set). *Acceptance:* `notes.md` records the command and the Big-O of each operation (from the command pages).
- [ ] **Ex B12.2 Cache-aside with an invalidation audit** — Add cache-aside to the library's `GET /books?search=` with a namespaced key and a 60 s TTL. List every code path that can change a book title (API, admin, management command, data migration) and invalidate on each. *Acceptance:* one test per write path asserts the key is gone; a hit/miss test runs with fakeredis; you have a `hey` p95 number before and after.
- [ ] **Ex B12.3 Stampede simulation** — Make the uncached query take 500 ms. Fire 100 concurrent requests just after the key expires and count database calls. Then add a lock (`SET key NX PX`) around population. *Acceptance:* DB calls drop from ~100 to 1–2; `notes.md` explains the trade-off of the lock (waiting clients, lock expiry).
- [ ] **Ex B12.4 ETag and 304** — Add an `ETag` to `GET /books/{id}` computed from `updated_at`. *Acceptance:* a request with a matching `If-None-Match` returns 304 with no body; after an update the ETag changes; `notes.md` says what the client cache saves vs what the Redis cache saves.
- [ ] **Ex B12.5 Three rate limiters** — Implement fixed window, sliding window (sorted set) and token bucket (Lua) behind one interface `allow(key, limit, window) -> bool`. *Acceptance:* one test drives all three with the same request schedule and shows the burst behaviour of each at a window boundary.
- [ ] **Ex B12.6 Eviction experiment** — Run Redis with `maxmemory 5mb`: first with `allkeys-lru`, then with `noeviction`, and fill it up. *Acceptance:* `notes.md` records what each policy did and what that would mean for DRF throttling.

### Must be able to do / explain
- [ ] Pick the right Redis data structure for a counter, a profile, a leaderboard and a set of unique IDs.
- [ ] Implement cache-aside and explain how it differs from write-through.
- [ ] Run an invalidation audit and prove it with tests.
- [ ] Explain a cache stampede and two ways to prevent it.
- [ ] Explain HTTP caching (`ETag`/`304`, `Cache-Control`) vs server-side caching.
- [ ] Choose an eviction policy and a persistence mode for a cache vs a broker.
- [ ] Explain why `KEYS *` is dangerous in production.
- [ ] Implement and compare fixed-window, sliding-window and token-bucket rate limiting.

**Estimated time:** ~12h

### Self-check interview questions
1. Cache-aside vs write-through — how do they differ, and when do you use each?
2. How do you make sure a cache is invalidated on every write path?
3. What is a cache stampede and how do you prevent one?
4. What does an `ETag` save compared with a Redis cache? Can a `304` still be a cache miss on your side?
5. Redis is single-threaded — what does that mean for you in practice?
6. Which eviction policy fits a pure cache? What happens with `noeviction` when memory is full?
7. RDB vs AOF — which would you pick for a cache, and which for a Celery broker?
8. Fixed window vs sliding window vs token bucket — which one allows bursts at the window boundary?
9. Why must a token-bucket check be done in a Lua script (or a transaction)?

---

#### Answers
1. Cache-aside: the app reads the cache, and on a miss reads the DB and fills the cache. It is lazy, and only data that is actually read gets cached. Write-through: every write goes to the cache and the DB together, so the cache is always fresh, but writes cost more and data that is never read gets cached anyway. Cache-aside is the default for read-heavy data with tolerable staleness.
2. List every path that mutates the source data (API, admin, bulk updates, migrations, commands, other services), invalidate from a shared function, and write one test per path. Short TTLs are a safety net, not a replacement.
3. Many requests miss a popular key at the same moment and all hit the DB. Prevent it with TTL jitter, a lock so only one request recomputes, serving stale data while one worker refreshes, or probabilistic early recomputation.
4. An `ETag` lets the client skip downloading the body, and sometimes skip the request entirely with `max-age`. The Redis cache saves your DB work. A `304` can still mean you computed the whole response (or a hash of it) on the server, so it saves bandwidth but not necessarily CPU or DB time.
5. Commands run one at a time. One slow command (`KEYS *`, a huge `SMEMBERS`, a long Lua script) blocks every other client. Use `SCAN` and keep values and commands small.
6. For a pure cache, use `allkeys-lru` (or `allkeys-lfu`). With `noeviction`, writes fail with OOM errors, so anything that writes counters, such as throttling, starts raising exceptions.
7. For a cache, often neither (or RDB), because data can be rebuilt. For a broker, AOF (for example `everysec`), because losing queued tasks on restart is a real loss.
8. Fixed window allows up to 2× the limit around the boundary. A sliding window smooths this out. A token bucket allows controlled bursts up to the bucket size and then a steady refill rate.
9. The check reads state, computes and writes. Without atomicity, two concurrent requests can both see a token and both spend it. A Lua script runs atomically on the Redis server.

---

## Module B-opt — Telegram bots with aiogram · OPTIONAL (~8h)

**Why:** QuickServe and PeopleOps have optional bot extensions. This module
teaches the tool before those extensions use it. Skip it if you skip the
extensions.

**Topics:**
- Telegram Bot API basics: bot token, updates, `chat_id`, BotFather
- Long polling vs webhooks; why a webhook needs a public HTTPS URL (a tunnel such as ngrok or cloudflared in dev); `secret_token` header verification
- aiogram 3: `Bot`, `Dispatcher`, `Router`, message and callback-query handlers, filters, middlewares
- Finite State Machine (FSM): states, storage (memory vs Redis), multi-step conversations
- Inline keyboards and callback data; handling duplicate or stale callbacks
- Linking a Telegram `chat_id` to an existing user account with a one-time code (no second identity system)
- Calling your own API or service layer from the bot; error handling; never leaking stack traces to users
- Testing handlers with fake updates

### Lessons
- [ ] **Bopt.1 Bot API basics** — Telegram "Bots: An introduction for developers" (core.telegram.org/bots); Bot API reference sections "Getting updates" (`getUpdates`, `setWebhook`, `secret_token`).
- [ ] **Bopt.2 aiogram 3 fundamentals** — aiogram 3 docs (docs.aiogram.dev): "Quick start", "Dispatcher", "Router", "Handling events" (message, callback query), "Filters".
- [ ] **Bopt.3 FSM and keyboards** — aiogram 3 docs "Finite State Machine" (states, storages incl. RedisStorage) and "Keyboard builder" (utils).
- [ ] **Bopt.4 Webhooks in aiogram** — aiogram 3 docs "Webhook" (aiohttp integration); ngrok or cloudflared quick start for a dev tunnel.

### Exercises
- [ ] **Ex Bopt.1 Echo bot, both ways** — Build a bot that answers `/start` and echoes text: first with polling, then with a webhook through a tunnel, verifying the `secret_token` header. *Acceptance:* `notes.md` compares the two modes (latency, infrastructure, when each fits).
- [ ] **Ex Bopt.2 Linked account** — Add `/link <code>`: the library API issues a one-time code (5-minute TTL, stored in Redis), and the bot stores `chat_id → user_id`. *Acceptance:* an expired or reused code fails with a clear message; an unlinked chat calling a protected command gets "link your account first", not a stack trace.
- [ ] **Ex Bopt.3 FSM conversation** — `/borrow`: pick a book → confirm, with an inline keyboard. It calls the same service function as the REST API. *Acceptance:* a test feeds a fake update sequence and asserts each state transition; tapping "Confirm" twice borrows only once.

### Must be able to do / explain
- [ ] Explain polling vs webhook and set up a webhook securely.
- [ ] Build a multi-step FSM conversation with inline keyboards.
- [ ] Link a bot user to an existing account without inventing a second auth system.
- [ ] Keep business logic in the service layer, with the bot as just another caller.

**Estimated time:** ~8h

### Self-check interview questions
1. Webhook vs polling — trade-offs?
2. How do you verify that a webhook request really comes from Telegram?
3. Why link the bot to an existing user instead of giving Telegram its own auth?
4. How do you stop a duplicate button tap from doing the action twice?
5. Where should FSM state live when you run two bot replicas?

---

#### Answers
1. Polling needs no public URL and is simple in dev, but it keeps a connection open and cannot scale to several instances easily. A webhook pushes updates to you with low latency, but needs a public HTTPS endpoint and has to handle retries.
2. Set `secret_token` in `setWebhook` and check the `X-Telegram-Bot-Api-Secret-Token` header on every request. Also keep the URL path unguessable.
3. One identity means one permission model. Roles and object permissions are reused, and there is no second place where access control can drift.
4. Make the action idempotent: check the current state in the service (for example "already approved" → no-op) under a transaction or constraint, and answer the callback either way.
5. In shared storage (for example Redis `RedisStorage`), not in memory. Otherwise a conversation breaks when the next update lands on the other replica.

---

## Project P2 — QuickServe POS · Junior (~45h)

**Goal:** a point-of-sale backend for a retail shop: cart → discounts → tax →
checkout → immutable receipt → returns, plus a daily sales report for managers.
It is admin-heavy on purpose: Django Admin must let a manager browse receipts
without an API client. That is the reason for choosing Django over FastAPI here,
and you must be able to defend the choice.

**Business problem:** a cashier needs a fast checkout that applies per-item and
cart-level discounts, computes tax, takes a mock payment, issues a receipt and
processes returns. A manager needs daily sales totals without touching the
database or waiting for someone to build a screen.

### Features
- [ ] Two roles, `cashier` and `manager`, with simplejwt access + refresh tokens; DRF permission classes enforce roles at viewset level
- [ ] Catalogue: products with SKU, name, `price_cents`, `tax_rate`; registered in Django Admin
- [ ] Discounts: fixed or percent with an optional cap; model-level validation (percent > 100, negative value, or a cap on a fixed discount are rejected)
- [ ] Discount calculation as an explicit **Strategy** (`FixedDiscount`, `PercentDiscount`, each with `apply(line_total_cents) -> int`) wrapped by a `Capped` decorator
- [ ] Checkout service: line total → line discount → cart discount → per-line tax → grand total, all in **integer cents** with deterministic rounding
- [ ] Immutable receipts: `unit_price_cents` copied at sale time, so a later price change never rewrites history
- [ ] Returns against a real receipt; over-return refused
- [ ] Daily sales report (gross, discounts, tax, net, receipt count), built twice: as a live aggregate and as the materialized view `daily_sales_mv` refreshed `CONCURRENTLY` from a management command
- [ ] Redis cache-aside on `GET /products?search=` with namespaced keys, a short TTL and invalidation on **every** write path that changes `price_cents`
- [ ] `UserRateThrottle` on `/checkout` (Redis-backed counters)
- [ ] HTTP caching: `ETag`/`304` on `GET /products`; `Cache-Control: private, max-age=86400, immutable` on `GET /receipts/{id}`
- [ ] `GET /receipts/{id}` N+1-free, proven with `assertNumQueries`
- [ ] Customized Django Admin: list display, filters, search, inline receipt items
- [ ] Settings split `base/dev/prod` from the start

**API:**

| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/auth/token` | public | access + refresh |
| POST | `/auth/token/refresh` | public | |
| GET | `/products?search=` | cashier+ | Redis cache-aside + `ETag` |
| POST | `/checkout` | cashier+ | throttled |
| GET | `/receipts/{id}` | cashier+ | immutable; `select_related`/`prefetch_related` |
| POST | `/returns` | cashier+ | against an existing receipt |
| GET | `/reports/daily-sales?date=` | manager | |

**Domain model:**
```
products(id, sku, name, price_cents, tax_rate)
discounts(id, code, type[fixed|percent], value, max_cap_cents NULL)
receipts(id, cashier_id -> users.id, status, created_at)
receipt_items(id, receipt_id, product_id, qty, unit_price_cents, discount_id NULL)
returns(id, receipt_id, reason, processed_by -> users.id, created_at)
```
Indexes: `products.sku`, `receipts.created_at`, `receipt_items.receipt_id`.

**Business rules (invariants):**
1. All money arithmetic is in integer cents, with specified rounding.
2. A capped percent discount never exceeds `max_cap_cents`.
3. A return references a real receipt and cannot exceed the quantity sold.
4. Cache invalidation fires on every write path that can change `price_cents`, including admin edits.
5. `/checkout` is throttled.
6. A receipt is immutable once created.

**Deliberately out of scope:**
- Idempotency keys on checkout. PayFlow (P9) does this properly; note the gap.
- Discount stacking.
- PDF receipts.
- A real payment gateway.
- Background jobs. PeopleOps earns Celery.
- Offline-first local queuing. Name it as "how real POS systems differ".

### Tech stack
| Tool | Where it is used | Taught in |
|---|---|---|
| Django (models, migrations, admin, settings split) | whole app | B10 |
| Django REST Framework, ViewSets, permissions, throttling | API | B11 |
| djangorestframework-simplejwt | access + refresh tokens | B11 |
| PostgreSQL (indexes, materialized view `CONCURRENTLY`) | storage, report | 1C 1.x, 2.5, 2.9 |
| Redis (cache-aside, throttle counters) | product search, `/checkout` throttle | B12 |
| fakeredis | unit tests | B12 |
| HTTP caching (`ETag`, `Cache-Control`) | `/products`, `/receipts/{id}` | B12, B1 |
| django-debug-toolbar, `assertNumQueries` | N+1 proof | B10 |
| Strategy / Decorator patterns | discounts | 1A.6, B10 (service layer) |
| pytest / pytest-django | tests | 1A.8, B8 |
| hey | before/after p95 | B8 |
| Docker Compose (`api` + `postgres` + `redis`) | local stack | B3 |
| GitHub Actions with Postgres + Redis service containers | CI | B9 |
| aiogram (OPTIONAL extension) | manager bot | B-opt |
| scikit-learn (OPTIONAL extension) | churn first touch | Track 3, ML Zoomcamp modules 3–4 |

### Required knowledge
- **Track 2:** B1–B9 (from P1), B10, B11, B12.
- **Track 1:** 1A.6 (design patterns / dataclasses), 1A.8 (pytest); 1C Modules 1.2 (aggregates), 1.3 (joins), 2.5 (indexes), 2.9 (materialized views).
- You should have built **P1 StockPilot**: layering discipline and CI are reused.

### Milestones
- [ ] **M1 — Scaffold and models.** New repo `quickserve/`, settings split, apps `catalog`, `sales`, `discounts`; `Product`, `Receipt`, `ReceiptItem`, `Discount` models + admin registration; discount validation unit-tested; review pass for "FastAPI habits carried into Django". *Done when:* `manage.py check` passes, migrations apply and roll back. Tag `v0.1-scaffold`.
- [ ] **M2 — Checkout.** `ProductViewSet` + search; `checkout_service` in integer cents; `POST /checkout` end to end; discount rounding edge cases (half-cent, 0, 100 %, cap) tested. Tag `v0.2-checkout`.
- [ ] **M3 — Caching.** Redis cache-aside on product search; `hey` p95 cold vs warm recorded in `docs/caching-notes.md`; **invalidation audit** across API, admin form, management command and data migration, with one test per path. Tag `v0.3-caching`.
- [ ] **M4 — Returns, reports, auth hardening.** Refresh-token flow; throttle on `/checkout`; `POST /returns` with over-return rejection; daily report as live query **and** `daily_sales_mv`, both timed at 1M receipt lines. Tag `v0.4-reports`.
- [ ] **M5 — HTTP caching, N+1, patterns, docs.** `ETag`/`304`, `Cache-Control: immutable`; `GET /receipts/{id}` naive → `assertNumQueries` → fixed; Strategy refactor; `docs/cache-stampede-notes.md` (risk + mitigations you did not build); `docs/redis-notes.md` (eviction, persistence, `SCAN`, key shape); a paragraph on CSRF (admin) vs JWT (API); framework-choice rationale; CI green against Postgres + Redis. Tag `v1.0-quickserve`.

### Definition of done
- [ ] All endpoints implemented and tested (unit, integration against real Postgres + Redis, serializer, migration up/down)
- [ ] Discount math correct in integer cents; edge cases covered
- [ ] Cache-aside working; invalidation proven on every price write path
- [ ] `docs/caching-notes.md` with real before/after p95 (cold and warm)
- [ ] Throttling on `/checkout` verified by a test
- [ ] Refresh-token flow working
- [ ] Django Admin genuinely usable by a manager
- [ ] `ETag`/`304` and `Cache-Control: immutable` working and tested (a price change produces a new ETag)
- [ ] `GET /receipts/{id}` N+1-free (constant query count regardless of item count)
- [ ] `daily_sales_mv` built, and its result equals the live query for the same date
- [ ] Discount rules implemented as an explicit Strategy; `Capped` tested once
- [ ] `docs/cache-stampede-notes.md`, `docs/redis-notes.md` and the framework-choice rationale written
- [ ] CI green

### OPTIONAL extensions
- [ ] **Churn first touch (~2 days)** — *Requires Track 3, ML Zoomcamp modules 3 (classification) and 4 (evaluation).* Add a documented, ML-only scope exception: `customers(id, phone_hash UNIQUE)` and a nullable `receipts.customer_id`. Label "returns within 30 days of first receipt" = 1. Train logistic regression on 4 features (receipt count, average basket, discount usage, days since first visit) and record precision, recall and the confusion matrix in `docs/churn-notes.md`. No deployment.
- [ ] **Pull-only Telegram bot (~2 days)** — *Requires B-opt.* aiogram in webhook mode: `/link <code>` links a manager's `chat_id` to their existing user; `/report [date]` is manager-only and reuses the daily-sales query and the same permission logic. An unlinked chat gets a clear message; a cashier is refused. `docs/telegram-bot-notes.md` covers webhook vs polling and why the bot is pull-only (no Celery yet).

**Estimated time:** ~45h (+~4h per optional extension)

### Interview questions
1. Cache-aside vs write-through — which did you use, and how did you make sure every write path invalidates the cache?
2. Why Django here and FastAPI in StockPilot — how do you decide?
3. Why integer cents, and what does a float discount bug look like?
4. `ETag` vs your Redis cache — which problem does each solve?
5. Materialized view or live aggregate for the daily report — what did your numbers say, and how much staleness is acceptable?

---

#### Answers
1. Cache-aside on product search, because it is read-heavy, repeats the same queries, and tolerates a few seconds of staleness. I listed every path that changes `price_cents` (API, admin form, management command, data migration), invalidated through one shared function, and wrote one test per path. The short TTL is only a safety net.
2. QuickServe needs an admin UI for managers, auth, an ORM and migrations out of the box, and it is sync CRUD, so Django gives the most for free. StockPilot was an API-only service where async and Pydantic typing mattered more.
3. Floats cannot represent most decimal fractions exactly, so 0.1 + 0.2 ≠ 0.3. Summing and discounting many lines drifts by a cent, and the receipt stops matching the payment. Integer cents with a specified rounding rule are exact and deterministic.
4. The `ETag` lets the client or a CDN skip downloading an unchanged body (a 304). Redis saves the server's database work. They are two layers with two separate invalidation stories.
5. Give your measured numbers at 1M lines. Typically the matview is far faster to read but stale until refreshed, which is acceptable for an end-of-day report and wrong for a live dashboard. `CONCURRENTLY` needs a unique index but does not block readers.

---

## Module B13 — Celery and Background Jobs (~12h)

**Why now:** in PeopleOps you will first **measure** how a synchronous email
blocks an approval endpoint, and only then fix it. This module gives you the
tool and its failure modes.

**Topics:**
- When work belongs outside the request cycle: slow I/O, retries, fan-out, scheduled work
- Architecture: producer → broker → worker → (optional) result backend; Redis vs RabbitMQ as a broker (RabbitMQ in depth in B15)
- Defining tasks, `delay`/`apply_async`, arguments must be serializable (pass IDs, not ORM objects)
- Retries: `autoretry_for`, `retry_backoff`, `retry_jitter`, `max_retries`, manual `self.retry`
- Delivery guarantees: `acks_late`, `task_reject_on_worker_lost`, what happens when a worker dies mid-task
- Worker tuning: `worker_prefetch_multiplier`, concurrency, `task_time_limit` / `task_soft_time_limit` (`SoftTimeLimitExceeded`)
- Redis broker specifics: `visibility_timeout` and redelivery of long tasks
- Idempotent tasks: a unique constraint vs `pg_advisory_xact_lock` vs "sent" markers
- Queues and routing: `task_routes`, dedicated workers, head-of-line blocking
- Celery Beat: crontab schedules, the `timezone` setting, "Beat fired twice", DST
- Django integration: `transaction.on_commit` for enqueueing; why not signals
- Testing: eager mode (`task_always_eager`) and its limits vs a real worker; `freezegun` for time; MailHog/Mailpit to see real emails
- Monitoring: Flower, task events

### Lessons
- [ ] **B13.1 Why background jobs** — Celery docs "Introduction to Celery"; "First Steps with Celery"; "Next Steps".
- [ ] **B13.2 Celery with Django** — Celery docs "First steps with Django" (the `celery.py` app, `autodiscover_tasks`, `shared_task`).
- [ ] **B13.3 Tasks and calling them** — Celery User Guide → "Tasks" (sections "Retrying", "Automatic retry for known exceptions", "Avoid launching synchronous subtasks", "Database transactions" / `on_commit`); "Calling Tasks" (`apply_async` options, ETA/countdown, serializers).
- [ ] **B13.4 Reliability settings** — Celery User Guide → "Optimizing" (prefetch limits, `acks_late`); "Workers Guide" (time limits, concurrency); "Configuration and defaults" (`task_acks_late`, `task_reject_on_worker_lost`, `worker_prefetch_multiplier`); Getting Started → Backends and Brokers → "Using Redis" (section "Visibility timeout" and its caveats).
- [ ] **B13.5 Routing and queues** — Celery User Guide → "Routing Tasks" (`task_routes`, starting workers with `-Q`).
- [ ] **B13.6 Scheduling** — Celery User Guide → "Periodic Tasks" (crontab, time zones, "Beat must run only once"); 1C Module 2.8 (advisory locks) for the alternative to a constraint.
- [ ] **B13.7 Testing Celery and time** — Celery User Guide → "Testing with Celery" (pytest plugin, `celery_worker` fixture, why eager mode is not a real test); freezegun README (github.com/spulec/freezegun); Mailpit README (github.com/axllent/mailpit), a maintained drop-in for MailHog.
- [ ] **B13.8 Monitoring** — Flower docs (flower.readthedocs.io) "Getting started"; Celery User Guide → "Monitoring and Management Guide".

### Exercises
- [ ] **Ex B13.1 Feel the pain first** — In the library app, send a "book borrowed" email synchronously through an SMTP backend that sleeps 3 s. Measure p95 with `hey`, then make the mail server fail. *Acceptance:* `notes.md` records the latency and shows that a mail failure fails the whole borrow. Do this before writing any Celery code.
- [ ] **Ex B13.2 Move it to Celery correctly** — A task `send_borrow_email(loan_id)` with `autoretry_for`, exponential backoff and jitter, enqueued in `transaction.on_commit`. *Acceptance:* the endpoint returns fast; a rollback test proves no task is enqueued when the transaction fails; retries are visible in the worker log against a failing SMTP; the emails appear in Mailpit.
- [ ] **Ex B13.3 Kill the worker** — Run a 30 s task, `kill -9` the worker in the middle: first with the defaults, then with `acks_late=True` + `task_reject_on_worker_lost=True`. *Acceptance:* `notes.md` shows the task was lost in the first case and redelivered in the second, and explains why the second setting forces idempotency.
- [ ] **Ex B13.4 Visibility timeout trap** — With the Redis broker, set `visibility_timeout=10` and run a 20 s task. *Acceptance:* you observe the task running twice, then fix it and write down the rule.
- [ ] **Ex B13.5 Two queues** — Split `emails` and `reports` queues with `task_routes` and run two workers in Compose. *Acceptance:* a test or log proves an email task never lands on the reports worker; flooding 500 emails does not delay a report task.
- [ ] **Ex B13.6 Idempotent scheduled job** — A Beat job `monthly_overdue_fees` guarded by a `UNIQUE(year_month)` run table. *Acceptance:* running it twice for the same month is a no-op (test); a `freezegun` test fast-forwards to the 1st of the month and asserts that it ran; a test on a DST-change night asserts that it ran exactly once.

### Must be able to do / explain
- [ ] Decide what belongs in a background job and argue it with measurements.
- [ ] Explain producer, broker, worker and result backend, and when you need a result backend at all.
- [ ] Configure retries with backoff and jitter.
- [ ] Explain `acks_late`, `reject_on_worker_lost` and the redelivery they cause.
- [ ] Explain the Redis broker's `visibility_timeout` gotcha.
- [ ] Make a task idempotent with a constraint, and compare that with an advisory lock.
- [ ] Route tasks to separate queues and explain head-of-line blocking.
- [ ] Enqueue on commit and explain what breaks otherwise.
- [ ] Test schedules with `freezegun` and explain why eager mode is not enough.

**Estimated time:** ~12h

### Self-check interview questions
1. When should work move out of the request cycle?
2. What happens to a task if the worker dies mid-execution, with and without `acks_late`?
3. Why does `acks_late` force tasks to be idempotent?
4. Explain `visibility_timeout` with the Redis broker. What happens to a 2-hour task with the default?
5. Why enqueue in `transaction.on_commit` rather than inside the transaction?
6. Why not send the email from a `post_save` signal?
7. Why two queues? What is head-of-line blocking?
8. How do you make "run at most once per month" safe, and why can Beat fire twice?
9. Why is `task_always_eager` not a real test of your Celery setup?

---

#### Answers
1. When it is slow or unreliable (email, external APIs, reports), needs retries, fans out, or is scheduled, and the user does not need the result in the same response.
2. Without `acks_late`, the message is acknowledged on receipt, so the task is lost. With `acks_late` (+ `reject_on_worker_lost`), the message is acknowledged after completion, so it is redelivered and runs again.
3. Because redelivery means the same task can run twice, or partially then fully. Side effects must be safe to repeat, or they must be guarded by a constraint or a "done" marker.
4. If a task is not acknowledged within `visibility_timeout` (default 1 hour), Redis redelivers it to another worker while the first is still running. A 2-hour task therefore runs twice. Set the timeout above your longest task.
5. Inside the transaction, the worker may run before the commit and read stale or missing rows. If the transaction rolls back, the task still runs for work that never happened.
6. Signals hide the call site, fire on every save (fixtures, admin, bulk scripts), run inside the transaction, and are hard to test. An explicit enqueue in the service is clear and testable.
7. Head-of-line blocking means a flood of slow or numerous tasks in one queue delays unrelated, urgent tasks behind them. Separate queues with separate workers isolate them.
8. Guard it with a DB unique constraint on the period key, or an advisory lock. Beat can fire twice because of restarts, two Beat instances, redeploys, clock or DST issues, and broker redelivery.
9. Eager mode runs the task inline in the same process and transaction. It skips serialization, the broker, routing, acknowledgement behaviour and `on_commit` timing, so it hides exactly the bugs that happen in production.

---

## Project P3 — PeopleOps · Middle (~45h)

**Goal:** an HR and leave-management system for an office of ~50 people: leave
requests routed to the right manager, balances accrued monthly, and decision
emails sent in the background. **This project exists to teach background jobs.**
You build the email synchronously first, measure the damage, and only then
introduce Celery and scheduled work.

**Business problem:** today leave is handled over chat DMs. There is no audit
trail, no balance anyone trusts, and no answer to "how many days do I have left?"

### Features
- [ ] Employee directory linked to auth users, with a self-referencing `manager_id`, department and hire date (accrual starts from it)
- [ ] Leave requests: annual, sick, unpaid; status `pending → approved | rejected`, plus `cancelled` by the employee while still pending
- [ ] Validation against the remaining balance and against overlapping approved requests, using PostgreSQL `daterange(start, end, '[]') && ...` instead of hand-written comparisons
- [ ] Approval increments `used_days` **in the same transaction** as the status change
- [ ] **Relationship-based permission:** a manager may decide only on requests from their own direct reports; nobody approves their own request
- [ ] Decision emails sent asynchronously by Celery with 3 retries and exponential backoff, enqueued via `transaction.on_commit` (not signals)
- [ ] Monthly balance accrual on Celery Beat, idempotent via `accrual_runs UNIQUE(year_month)`
- [ ] Daily reminder for requests pending 3+ days
- [ ] Two queues (`emails`, `accruals`) with separate workers and `task_routes`
- [ ] Deliberate worker configuration: `task_acks_late`, `task_reject_on_worker_lost`, `worker_prefetch_multiplier=1`, time limits, `visibility_timeout` longer than the longest task — each one demonstrated
- [ ] Timezone-correct scheduling: `USE_TZ=True`, explicit Celery `timezone`, a DST-night test
- [ ] HR admin: view everything, correct a balance with a reason, trigger accrual manually

**Roles:**

| Role | Can | Cannot |
|---|---|---|
| `employee` | create requests, see own balance and history, cancel own pending request | see others' data, approve anything |
| `manager` | employee rights + approve/reject **own direct reports** only, see their balances | approve own request, act on other managers' reports |
| `hr_admin` | see all requests and balances, correct a balance with a reason, trigger accrual | approve on a manager's behalf |

**API:**

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/employees/me` | employee+ | |
| GET | `/leave-balances/me` | employee+ | |
| POST | `/leave-requests` | employee+ | balance + overlap validation |
| GET | `/leave-requests` | employee+ | own; managers also see their reports' |
| POST | `/leave-requests/{id}/cancel` | employee+ | own, pending only |
| POST | `/leave-requests/{id}/approve` | manager | own reports only, async email |
| POST | `/leave-requests/{id}/reject` | manager | own reports only, async email |
| POST | `/leave-balances/accrue` | hr_admin | manual trigger |

**Domain model:**
```
employees(id, user_id -> users.id, full_name, manager_id NULL -> employees.id, hired_at, department)
leave_requests(id, employee_id, type[annual|sick|unpaid], start_date, end_date, days,
               status[pending|approved|rejected|cancelled], decided_by NULL, decided_at NULL,
               reminder_sent_at NULL, created_at)
leave_balances(id, employee_id, year, accrued_days, used_days, UNIQUE(employee_id, year))
accrual_runs(id, year_month, run_at, employees_processed, UNIQUE(year_month))
```

**Business rules (invariants):**
1. A request cannot exceed the remaining balance for the year.
2. A manager decides only on their own direct reports' requests.
3. Nobody approves their own request.
4. Approval and the `used_days` increment happen in one transaction.
5. Overlapping approved requests for the same employee are rejected.
6. Sending the email never fails or slows the approval.
7. Accrual for a given month runs at most once, however often it fires.

**Deliberately out of scope:**
- Payroll, attendance, shifts.
- Org charts deeper than manager → report.
- Calendar integrations.
- Public holidays. Name them as the realistic next feature.
- RabbitMQ. WareFlow earns it.
- Caching balances. It would risk showing a wrong entitlement.

### Tech stack
| Tool | Where it is used | Taught in |
|---|---|---|
| Django + DRF (service layer, viewsets, `@action`) | whole API | B10, B11 |
| DRF object-level / relationship-based permissions | manager approval | B11 |
| simplejwt | auth | B11 |
| PostgreSQL `daterange` + `&&`, `django.contrib.postgres` range fields | overlap validation | B10 (B10.6) |
| `transaction.atomic`, `transaction.on_commit` | approval + enqueue | B10 (B10.5), B13 |
| `pg_advisory_xact_lock` (the alternative you must name) | accrual guard discussion | 1C 2.8 |
| Celery (retries, `acks_late`, routing, time limits) | emails, accrual | B13 |
| Celery Beat (crontab, timezone) | monthly accrual, daily reminder | B13 |
| Redis as the Celery broker (`visibility_timeout`) | queue | B12, B13 |
| freezegun | schedule and DST tests | B13 |
| Mailpit / MailHog | local SMTP you can inspect | B13 |
| hey | measuring the blocking email | B8 |
| Docker Compose (`api`, `postgres`, `redis`, 2 × `celery-worker`, `celery-beat`) | local stack | B3 |
| GitHub Actions (Postgres + Redis service containers) | CI | B9 |
| Parquet export (OPTIONAL) | DE extension | Track 3, DE Zoomcamp module 1 (Docker/Postgres ingestion) + pandas |
| aiogram FSM + inline keyboards (OPTIONAL) | bot extension | B-opt |

### Required knowledge
- **Track 2:** B1–B13 (P2 QuickServe built).
- **Track 1:** 1A.8 (pytest), 1A.11 (concurrency basics); 1C Modules 2.7 (transactions), 2.8 (locking / advisory locks).

### Milestones
- [ ] **M1 — Scaffold and domain.** Repo `peopleops/`; `Employee`, `LeaveRequest`, `LeaveBalance` models; `LeaveRequestViewSet` with `approve`/`reject` actions; relationship-based permission with tests (own report / non-report / self / anonymous). Tag `v0.1-domain`.
- [ ] **M2 — Feel the pain.** A synchronous decision email through a slow or failing SMTP; trace exactly where it blocks; `docs/blocking-email-problem.md` with **real numbers** (latency with a slow mail server, what happens to the approval on a mail failure). Do not skip this. Tag `v0.2-sync-pain`.
- [ ] **M3 — Celery.** `celery.py` + Redis broker; `send_decision_email` with `retry(3)` + backoff, enqueued via `on_commit`; accrual calculation (manual trigger); worker config demonstrated (`kill -9` with and without `acks_late`; `visibility_timeout` redelivery observed, then fixed; soft time limit cleanup); `emails` and `accruals` queues with two workers in Compose; CI green. Tag `v0.3-celery`.
- [ ] **M4 — Scheduling and correctness.** Celery Beat monthly accrual and daily stale-request reminder; idempotency guard tested (a double run is a no-op) and the advisory-lock alternative written down; `daterange` overlap tests (adjacent, contained, partial, identical); DST-night `freezegun` test; `docs/celery-ops-notes.md`; `docs/postmortem-peopleops.md`. Tag `v1.0-peopleops`.

### Definition of done
- [ ] Request → approval → balance update works end to end
- [ ] Manager scoping enforced and tested, including self-approval
- [ ] Approval endpoint responds fast; email is async with retries
- [ ] `docs/blocking-email-problem.md` with real before/after numbers
- [ ] Enqueue happens on commit, proven by a rollback test
- [ ] Approval and `used_days` commit together (a crash mid-way leaves neither)
- [ ] Monthly accrual on Beat, proven with `freezegun`; idempotent via a DB constraint
- [ ] Stale-request reminder working (and not sent twice, via `reminder_sent_at`)
- [ ] `acks_late` / `reject_on_worker_lost` / prefetch / time limits / `visibility_timeout` configured and demonstrated
- [ ] Two queues, two workers, routing tested
- [ ] `daterange` overlap and DST tests green
- [ ] `docs/celery-ops-notes.md` and `docs/postmortem-peopleops.md` written; tag `v1.0-peopleops`

### OPTIONAL extensions
- [ ] **Monthly Parquet export (~2 days)** — *Requires Track 3, DE Zoomcamp module 1 (or basic pandas).* A Beat job exports `leave_requests` + `leave_balances` to Parquet after accrual, partitioned by `year_month`, and is idempotent per month like the accrual itself. The files must be readable with `pandas.read_parquet`.
- [ ] **Telegram bot with FSM and push (~2 days)** — *Requires B-opt.* Reuse the linked-account pattern. `/request_leave` is an FSM conversation (type → start → end → confirm) validated by the **same service layer**. On submission, a Celery task pushes an inline keyboard (Approve / Reject) to the manager; justify whether it shares the `emails` queue or gets its own. Tapping calls the same `approve`/`reject` service. Required tests: a double tap does not double-approve, and a non-report cannot be approved from the keyboard.

**Estimated time:** ~45h (+~4h per optional extension)

### Interview questions
1. What happens to a Celery task if the worker dies mid-execution, and how did you configure for it?
2. How do you make a scheduled job idempotent, and why must you?
3. Why enqueue on commit rather than inside the transaction, and why not from a `post_save` signal?
4. How do you enforce a permission that depends on the relationship between two records?
5. How did you test time-dependent behaviour (monthly accrual, DST night) without waiting?

---

#### Answers
1. With `acks_late=True` + `task_reject_on_worker_lost=True`, the message is acknowledged only after success, so a killed worker's task is redelivered. I demonstrated both behaviours with `kill -9`. Because of redelivery the tasks are idempotent: accrual is guarded by `UNIQUE(year_month)`, and an email duplicate is either acceptable or marked as sent.
2. Beat can fire twice (restarts, redeploys, broker redelivery, DST). A unique constraint on the period key makes the second run fail fast and become a no-op, it survives restarts, and it leaves an audit row, which is better than an `if` that races.
3. Inside the transaction the worker may read uncommitted state, or email about an approval that later rolls back. Signals hide the side effect, fire on every save including fixtures and admin, and are hard to test. An explicit `on_commit` enqueue in the service is correct and testable.
4. In the permission/service layer: `leave_request.employee.manager_id == current_user.employee.id` and the request is not the manager's own, checked on the object (`has_object_permission`) and on the queryset for lists. Tests cover the report, a non-report, self and anonymous cases.
5. `freezegun` moves time to "1st of the month 00:00" and to the DST-change night, and the tests assert the job ran exactly once. The tests use a real worker, and eager mode only where it is enough.

## Module B14 — Architecture Patterns: DI, Repository, Unit of Work, DDD-lite (~10h)

**Why now:** from WareFlow on, one request touches several aggregates and must
commit or roll back as one unit, and two parts of the system (Inventory,
Fulfillment) must evolve without breaking each other. These patterns are the
vocabulary for that.

**Topics**
- Dependency injection as a design idea (constructor injection, composition
  root) vs a DI *framework*; FastAPI `Depends` as a DI container you already use
- A mini DI container: registration, resolution, lifetimes (singleton vs per
  request), why "service locator" is the anti-pattern version
- Repository pattern formalized: collection-like interface per aggregate,
  `Repository[T]` as a `Protocol`, fake in-memory repositories for unit tests
- Unit of Work: one transaction spanning several repositories, `commit()` /
  `rollback()`, the UoW as a context manager, who owns the session
- How ORMs work internally: identity map, unit of work inside the SQLAlchemy
  `Session`, flush vs commit, lazy loading and why it causes N+1
- DDD-lite: bounded contexts, ubiquitous language, aggregates and aggregate
  roots, entities vs value objects, invariants guarded by the aggregate root
- Domain services vs application services; thin API layer → application
  service → domain
- Domain events: collected by aggregates, published by the application service
  **after** commit; why publishing inside the transaction is wrong
- Context boundaries: no type leakage, anti-corruption layer (named)

**Theory**
- [ ] **B14.T1 Dependency injection** — *Cosmic Python* (Percival & Gregory, cosmicpython.com) ch. 13 "Dependency Injection (and Bootstrapping)"; FastAPI docs "Dependencies" (all sub-pages) re-read as DI.
- [ ] **B14.T2 Repository pattern** — *Cosmic Python* ch. 2 "Repository Pattern" and ch. 3 "A Brief Interlude: On Coupling and Abstractions".
- [ ] **B14.T3 Service layer** — *Cosmic Python* ch. 4 "Our First Use Case: Flask API and Service Layer" (read it as FastAPI) and ch. 5 "TDD in High Gear and Low Gear".
- [ ] **B14.T4 Unit of Work** — *Cosmic Python* ch. 6 "Unit of Work Pattern"; SQLAlchemy 2.0 docs "Session Basics" (sections "What does the Session do?", "Flushing", "Committing").
- [ ] **B14.T5 How ORMs work inside** — SQLAlchemy docs "Session Basics → Identity Map" and "ORM Querying Guide → Relationship Loading Techniques"; optional skim of `sqlalchemy/orm/session.py` (`Session.flush`, `Session.commit`).
- [ ] **B14.T6 Aggregates and consistency boundaries** — *Cosmic Python* ch. 7 "Aggregates and Consistency Boundaries"; *Domain-Driven Design Distilled* (Vaughn Vernon) ch. 5 "Tactical Design with Aggregates".
- [ ] **B14.T7 Bounded contexts** — *DDD Distilled* ch. 1 "DDD for Me", ch. 2 "Strategic Design with Bounded Contexts and the Ubiquitous Language", ch. 4 "Strategic Design with Context Mapping".
- [ ] **B14.T8 Domain events** — *Cosmic Python* ch. 8 "Events and the Message Bus"; *DDD Distilled* ch. 6 "Tactical Design with Domain Events".

**Exercises** (`backend/b14-architecture/`)
- [ ] **B14.E1 Mini DI container** — a `Container` class with `register(interface, factory, lifetime="singleton"|"transient")` and `resolve(interface)`, resolving constructor dependencies by type hints. Acceptance: resolving a service with a two-level dependency chain works; a singleton returns the same object twice, a transient returns different ones; a missing registration raises a clear error naming the type. Tests with plain pytest.
- [ ] **B14.E2 Repository with a fake** — define `Repository[T]` as a `Protocol` (`add`, `get`, `list`), implement `SqlAlchemyProductRepository` and `InMemoryProductRepository`. Acceptance: the same service-layer test suite runs green against both implementations (parametrized fixture), and `mypy --strict` passes.
- [ ] **B14.E3 Unit of Work across two repositories** — `SqlAlchemyUnitOfWork` exposing `.orders` and `.stock` repositories, used as `with uow: ...; uow.commit()`. Acceptance: a test where the second write raises proves the first write is rolled back; leaving the `with` block without `commit()` rolls back; a `FakeUnitOfWork` records `committed=True` for unit tests.
- [ ] **B14.E4 Identity map experiment** — in one `Session`, load the same row twice and compare with `is`; modify an attribute and observe (with SQL echo on) when the `UPDATE` is actually emitted (autoflush before a query vs at commit). Write `notes.md`: 5 bullet points on what you saw.
- [ ] **B14.E5 Aggregate invariant** — model an `Order` aggregate root that owns `OrderLine`s and refuses (domain exception) to exceed a max total or add a line after `status="paid"`. `Money` is a frozen value object. Acceptance: the invariant is impossible to bypass through the public API of the aggregate; value objects compare by value.
- [ ] **B14.E6 Events after commit** — aggregates append events to `.events`; the UoW collects them and hands them to a `publish` callable **only after** a successful commit. Acceptance: on rollback nothing is published; on commit each event is published exactly once.

**Must be able to do/explain**
- [ ] Draw API → application service → domain → repository → UoW → DB and say what each layer may import.
- [ ] Explain the difference between a Repository and a Unit of Work precisely.
- [ ] Explain what SQLAlchemy's identity map and autoflush do, and how they relate to N+1.
- [ ] Define aggregate, aggregate root, entity, value object — with an example from your own code.
- [ ] Explain why domain events are published after commit and what can still go wrong (the gap B16/B25 deal with).
- [ ] Identify a type leak between two bounded contexts in a code review.

**Estimated hours:** ~10h (theory 5h, exercises 5h)

### Self-check interview questions
1. What problem does dependency injection solve, and how is it different from a service locator?
2. Repository vs Unit of Work — what does each own?
3. Why keep an in-memory fake repository if you have a real database in tests?
4. What is an aggregate and why should a transaction usually modify only one?
5. Entity vs value object — how do you decide, and how do they compare for equality?
6. What is the identity map, and what surprising behavior can it cause?
7. What is a bounded context? Give an example where the same word means different things in two contexts.
8. Why must events be published after the commit, not inside the transaction?

---

**Answers**
1. DI passes collaborators in from outside (usually via the constructor), so code depends on abstractions and tests can pass fakes. A service locator lets code *pull* dependencies from a global registry — dependencies become hidden, and tests must configure global state.
2. A repository owns access to one aggregate type as if it were an in-memory collection (add/get/list). The UoW owns the transaction and the session: it gives out repositories bound to the same transaction and decides commit or rollback for all of them together.
3. Fast unit tests of business logic without I/O, and it forces the repository interface to stay small and honest. The real DB is still covered by integration tests.
4. An aggregate is a cluster of objects treated as one consistency unit, accessed only through its root, which guards the invariants. Modifying one aggregate per transaction keeps lock scope small and makes consistency rules local; cross-aggregate consistency becomes eventual, via events.
5. An entity has an identity that persists through changes (an Order with id 42). A value object is defined only by its values and is immutable (`Money(100, "UZS")`). Entities compare by id, value objects by all fields.
6. Within one session, each database row maps to exactly one Python object. Loading the same row twice returns the same object; changes made in memory may be flushed automatically before a later query (autoflush), which can surprise you with an `UPDATE` you did not expect yet — or hide a stale read.
7. A boundary within which a model and its language are consistent. "Reservation" in Fulfillment is a hold of stock for an order; in a hotel-booking context it would be a room booking — each context has its own model and they talk through explicit contracts/events.
8. If you publish inside the transaction and the transaction then rolls back, consumers react to something that never happened. Publishing after commit avoids that, but opens the opposite gap: commit succeeds, publish fails — the event is lost. The outbox pattern (B25) closes it.

---

## Module B15 — RabbitMQ (~12h)

**Why now:** WareFlow's transfer spans two transactions hours apart. A work
queue with per-message ack, redelivery and a dead-letter queue is the felt need.

**Topics**
- Why a message broker: temporal decoupling, load levelling, work distribution
- AMQP 0-9-1 model: producer → exchange → binding → queue → consumer; channels vs connections; virtual hosts
- Exchange types: direct, topic (routing-key patterns `*` / `#`), fanout, headers (named)
- Queues: durable vs transient, exclusive, auto-delete; quorum queues vs classic queues (named)
- Messages: persistent (`delivery_mode=2`), headers, `message_id`, `correlation_id`, content type
- Consumers: manual ack, nack/reject with and without requeue, **ack after processing**, prefetch / QoS and fair dispatch
- Publisher confirms: what they guarantee and what they don't; mandatory flag and returned messages
- Heartbeats and connection recovery
- Dead-letter exchanges (DLX), retry with delay queues / TTL, poison messages, max delivery count
- Delivery semantics: at-most-once vs at-least-once; **idempotent consumers** (dedupe by message id / business key, unique constraints)
- Python clients: `pika` (blocking) and `aio-pika` (asyncio); running a consumer as its own process
- Management UI and `rabbitmqctl` for visibility
- Consumer-driven contract testing: Pact **message pacts** (consumer writes the expectation, provider verifies)

**Theory**
- [ ] **B15.T1 AMQP concepts** — rabbitmq.com docs "AMQP 0-9-1 Model Explained".
- [ ] **B15.T2 Tutorials 1–3** — rabbitmq.com "Get Started" → Python tutorials 1 "Hello World", 2 "Work Queues", 3 "Publish/Subscribe".
- [ ] **B15.T3 Tutorials 4–6** — tutorials 4 "Routing", 5 "Topics", 6 "RPC" (read RPC to understand why you usually *don't* do it over a broker).
- [ ] **B15.T4 Reliability** — rabbitmq.com docs "Consumer Acknowledgements and Publisher Confirms" and "Reliability Guide".
- [ ] **B15.T5 Durability, QoS and heartbeats** — docs "Queues" (durability section), "Consumer Prefetch", "Detecting Dead TCP Connections with Heartbeats and TCP Keepalives".
- [ ] **B15.T6 Dead lettering and TTL** — docs "Dead Letter Exchanges" and "Time-To-Live and Expiration".
- [ ] **B15.T7 Python async client** — aio-pika docs "Quick start" and the "Patterns" section (master/worker).
- [ ] **B15.T8 Contract tests** — docs.pact.io "Introduction", "How Pact works" and "Message Pact" (non-HTTP messages); pact-python README (message consumer/provider).

**Exercises** (`backend/b15-rabbitmq/`, RabbitMQ `rabbitmq:3-management` in Compose)
- [ ] **B15.E1 Work queue** — a producer sends 100 tasks with random sleep times; run 3 consumers. Acceptance: with `prefetch_count=1` the fast consumers process more messages than the slow one (log counts per consumer); with no prefetch the distribution is round-robin regardless of speed. Record both results.
- [ ] **B15.E2 Topic routing** — exchange `events` (topic); bind `inventory.*` and `*.dispatched` queues. Publish `inventory.dispatched`, `inventory.received`, `fulfillment.dispatched`. Acceptance: a table in `notes.md` showing which queue got which message matches your prediction written *before* running.
- [ ] **B15.E3 Lose nothing on broker restart** — first with transient queue + non-persistent messages: publish 100, restart the broker, count (expect loss). Then durable queue + persistent messages + publisher confirms: repeat. Acceptance: second run shows 100/100; `notes.md` explains which setting protected what.
- [ ] **B15.E4 Kill the consumer mid-processing** — a consumer that sleeps 5s per message; kill it with `kill -9` during processing. Acceptance: with ack-after-processing the message is redelivered (`redelivered=True`); with auto-ack it is lost. Show both.
- [ ] **B15.E5 DLQ and poison message** — a queue with a DLX; the consumer rejects a message that fails validation; after 3 failed attempts (track attempts via a header or quorum-queue delivery limit) it lands in the DLQ. Acceptance: you find the poison message in the management UI and read its `x-death` header by hand; a `notes.md` screenshot/description.
- [ ] **B15.E6 Idempotent consumer + message pact** — consumer inserts into `processed_messages(message_id PRIMARY KEY)` in the same DB transaction as its side effect. Acceptance: delivering the same message twice results in one side effect; a pact-python message pact pins the payload (`event_type`, `transfer_id`, `items[]`), and changing a field name in the provider fails the verification.

**Must be able to do/explain**
- [ ] Draw the path of a message from `basic_publish` to `basic_ack`, naming exchange, binding, queue.
- [ ] Choose an exchange type for a given routing need.
- [ ] Explain what durable queue, persistent message and publisher confirm each protect against — and what is still not guaranteed.
- [ ] Explain why ack must come after processing, and what redelivery means for consumer design.
- [ ] Configure a DLX and explain what a DLQ gives you and what it does not.
- [ ] Make a consumer idempotent with a database constraint.
- [ ] Explain consumer-driven contract testing and when it fails CI.

**Estimated hours:** ~12h (theory 5h, exercises 7h)

### Self-check interview questions
1. What is the difference between an exchange and a queue?
2. When would you choose a topic exchange over a direct exchange?
3. What does `prefetch_count` do, and what goes wrong with unlimited prefetch?
4. Durable queue + persistent message + publisher confirm — is the message now guaranteed to be processed?
5. What is a poison message and how do you stop it from blocking a queue forever?
6. Why is at-least-once delivery the realistic default, and what does it demand of consumers?
7. What does a DLQ *not* give you?
8. What is a message pact, and who writes it — producer or consumer?

---

**Answers**
1. Producers publish to exchanges, never directly to queues. An exchange routes a copy of the message to zero or more queues according to bindings; the queue stores messages until a consumer acks them.
2. When consumers need to subscribe by pattern over a hierarchical key (`inventory.*`, `*.dispatched`) instead of exact keys. Direct exchange routes only on exact routing-key match.
3. It limits how many unacked messages a consumer holds at once. With unlimited prefetch, one consumer grabs everything in the queue, slow consumers hoard work that idle ones could do, and memory grows.
4. No. It is guaranteed that the broker persisted it. It can still be processed twice (redelivery after a crash between side effect and ack), be dead-lettered, or be stuck behind a failing consumer. Processing guarantees come from consumer design (idempotency, ack after work).
5. A message that always fails processing. With requeue-on-failure it loops forever. Limit delivery attempts (delivery count, retry header) and route it to a DLX/DLQ for human inspection.
6. Exactly-once across a network and a database is not achievable in general; brokers redeliver on crash or connection loss. Consumers must therefore be idempotent: processing the same message twice has the same effect as once.
7. It does not fix the message, retry it later automatically, alert anyone, or preserve ordering. It is a parking lot; you still need monitoring, a replay tool, and a decision about what to do with what lands there.
8. A contract describing the message shape the consumer relies on. The consumer writes it (consumer-driven); the provider's CI verifies it can still produce such messages, so a breaking payload change fails before release.

---

## Module B16 — Kafka (~10h)

**Why now:** before committing WareFlow to RabbitMQ you must be able to argue
why *not* Kafka — and FleetTrack/AtlasMarket, the Java track and the Data
Engineering Zoomcamp all assume you know how a partitioned log behaves.

**Topics**
- Log vs queue: an append-only, replayable, partitioned log vs messages deleted on ack
- Topics, partitions, offsets; brokers, replication factor, leaders and ISR (in-sync replicas); KRaft (no ZooKeeper) named
- Keys and ordering: ordering is per partition only; choosing a key (`order_id`, `delivery_id`); hot partitions
- Producers: `acks=0/1/all`, retries, idempotent producer, batching/linger, compression
- Consumers and consumer groups: partition assignment, max parallelism = partition count, rebalancing and its pauses
- Offsets and commits: auto-commit vs manual commit; commit-before-process (at-most-once) vs process-then-commit (at-least-once)
- Delivery semantics: at-most-once, at-least-once, exactly-once (transactions + idempotent producer inside Kafka; why "exactly-once" stops at the Kafka boundary)
- Retention (time/size) and log compaction; replaying from an earlier offset; consumer lag
- Schemas and evolution (Avro/Protobuf + schema registry, named)
- Kafka vs RabbitMQ decision criteria: replay, fan-out to many independent readers, throughput, per-message routing/ack, DLQ, operational weight
- **The commit-then-publish gap:** DB commit succeeds, publish fails (or vice versa) — named here, solved by the transactional outbox in B25
- Python clients: `confluent-kafka` (librdkafka) vs `aiokafka`; local Kafka in Compose (`apache/kafka` image in KRaft mode) or Redpanda as a Kafka-compatible alternative

**Theory**
- [ ] **B16.T1 Kafka in a nutshell** — Confluent blog/article "Kafka in a Nutshell" (or developer.confluent.io "Apache Kafka 101" course: "Introduction", "Topics", "Partitioning", "Brokers", "Replication", "Producers", "Consumers").
- [ ] **B16.T2 Design** — kafka.apache.org documentation §4 "Design" (sections "Persistence", "The Producer", "The Consumer", "Message Delivery Semantics", "Replication", "Log Compaction").
- [ ] **B16.T3 Producers and consumers in depth** — *Kafka: The Definitive Guide* 2nd ed. (Shapira, Palino, Sivaram, Petty) ch. 3 "Kafka Producers: Writing Messages to Kafka" and ch. 4 "Kafka Consumers: Reading Data from Kafka".
- [ ] **B16.T4 Reliability** — *Kafka: The Definitive Guide* ch. 7 "Reliable Data Delivery" and ch. 8 "Exactly-Once Semantics".
- [ ] **B16.T5 Python client** — confluent-kafka-python docs "Getting started" (Producer, Consumer, delivery reports, `commit`).
- [ ] **B16.T6 Choosing a broker** — re-read your B15 notes; *Designing Data-Intensive Applications* (Kleppmann) ch. 11 "Stream Processing", section "Transmitting Event Streams" (message brokers vs partitioned logs).

**Exercises** (`backend/b16-kafka/`, single-broker Kafka in Compose, KRaft mode)
- [ ] **B16.E1 Partitions and ordering** — topic `deliveries` with 3 partitions. Produce 30 events for 3 keys, 10 each, with a sequence number. Acceptance: a consumer shows each key's events are in order, while interleaving across keys is arbitrary; `notes.md` explains why.
- [ ] **B16.E2 Consumer group scaling** — run 1, then 2, then 4 consumers in one group on the 3-partition topic. Acceptance: you record which consumer got which partitions each time (4th consumer idle) and describe the pause during rebalance.
- [ ] **B16.E3 Offsets and semantics** — a consumer that crashes (raise after N messages). Version A: commit before processing; version B: process then commit. Acceptance: A loses messages on restart, B reprocesses some; `notes.md` names each as at-most-once / at-least-once with your evidence.
- [ ] **B16.E4 Replay** — reset a consumer group's offsets to the beginning (`kafka-consumer-groups.sh --reset-offsets`) and rebuild a derived count from scratch. Acceptance: the rebuilt count equals the original; explain why RabbitMQ cannot do this without re-publishing.
- [ ] **B16.E5 The dual-write gap** — a tiny FastAPI endpoint that inserts a row in Postgres and then produces to Kafka. Stop the broker between the two steps (or inject an exception). Acceptance: the DB has the row, the topic doesn't; write down the inconsistency in `notes.md` and **do not fix it** (B25 does).
- [ ] **B16.E6 Decision record** — `docs/rabbitmq-vs-kafka.md` template for a system of your choice: context, options, criteria table (ordering, replay, routing, DLQ, throughput, ops cost), decision, consequences. Acceptance: at least 6 criteria and one "we would switch if…" statement.

**Must be able to do/explain**
- [ ] Explain topic, partition, offset, consumer group and the relationship between partitions and parallelism.
- [ ] Choose a partition key for a given ordering requirement and name the hot-partition risk.
- [ ] Explain `acks=all` + idempotent producer and what they protect.
- [ ] Explain at-most-once vs at-least-once in terms of *when* the offset is committed.
- [ ] Explain why Kafka's exactly-once does not extend to your Postgres writes.
- [ ] Describe the commit-then-publish gap and name the pattern that solves it.
- [ ] Argue RabbitMQ vs Kafka for a concrete system.

**Estimated hours:** ~10h (theory 5h, exercises 5h)

### Self-check interview questions
1. How is a Kafka topic different from a RabbitMQ queue?
2. You need all events for one order processed in order. How do you guarantee it?
3. You have 6 partitions and 10 consumers in one group. What happens?
4. When exactly do you commit the offset for at-least-once processing?
5. What does `acks=all` mean, and when can data still be lost?
6. What is log compaction and when would you use it?
7. What is consumer lag and why do you monitor it?
8. Your service writes to Postgres and then to Kafka. What can go wrong?

---

**Answers**
1. A queue removes messages when a consumer acks them; each message goes to one consumer. A topic is a retained, append-only log: consumers track their own offsets, many independent groups can read the same data, and old data can be replayed until retention deletes it.
2. Use the order id as the message key so all its events go to the same partition, and process each partition sequentially in one consumer. Ordering is only guaranteed within a partition.
3. Only 6 consumers get a partition each; 4 sit idle. Max parallelism of a group equals the number of partitions.
4. After the message has been fully processed (side effects done). If you crash before committing, the message is re-read — duplicates are possible, loss is not.
5. The leader waits until all in-sync replicas have the write before acknowledging. Data can still be lost if `min.insync.replicas` is 1 (ISR shrinks to the leader alone and the leader dies), or with unclean leader election enabled.
6. Kafka keeps at least the latest record per key instead of deleting by time. Useful for "current state" topics (latest price per product, latest config) where consumers need the final value per key, not the full history.
7. The difference between the latest offset in a partition and the group's committed offset — how far behind consumers are. Growing lag means consumers can't keep up and data freshness is degrading.
8. Dual write: DB commit succeeds and the publish fails (event lost), or publish succeeds and the DB transaction rolls back (event about something that never happened). Retries don't fix it atomically — the transactional outbox (or CDC) does.

---

## Project P4 — WareFlow · Middle (~60h)

**Multi-warehouse management system (WMS) with pick/pack workflows.**

### Goal
A retailer runs 3 warehouses. Stock is received, transferred between
warehouses and reserved/picked for outbound orders — and a transfer or pick
that fails partway must never leave inventory numbers lying. The core insight:
**a warehouse transfer is not one transaction.** Stock leaves warehouse A today
and arrives at B hours or days later, so the process spans multiple
transactions connected by events. This is the project where transactions and
locking stop being an exercise and become the whole point.

### Features
- [ ] Receive stock at a warehouse (`POST /warehouses/{id}/stock/receive`)
- [ ] Two-phase transfer: dispatch (tx1: decrement source, `transfers.status=dispatched`, publish `StockDispatched` after commit) → receive (tx2: increment destination, `received`, publish `StockReceived`)
- [ ] Reservations created by a Fulfillment consumer reacting to `StockDispatched`; confirmed/released on `StockReceived`
- [ ] Pick/pack workflow (`pick_lists`, `POST /pick-lists/{id}/complete`)
- [ ] `GET /warehouses/{id}/stock` with **keyset** pagination served from a covering index
- [ ] Resource-scoped permissions via `warehouse_assignments` (roles: `warehouse_worker`, `warehouse_manager`, `inventory_controller`, `fulfillment_operator`) — a worker at A dispatching from B is refused at the API
- [ ] Two bounded contexts (Inventory, Fulfillment) that talk only through events; no type leakage
- [ ] Unit of Work committing across multiple repositories as one unit
- [ ] RabbitMQ topic exchange, durable queues, persistent messages, publisher confirms, `prefetch_count`, heartbeat
- [ ] DLQ after 3 failed attempts; a poison message pushed through and inspected by hand
- [ ] Pact message contract pinning the `StockDispatched` payload
- [ ] `stock_movements` range-partitioned by month + maintenance job creating next month's partition + `DEFAULT` partition
- [ ] BRIN index on `stock_movements(created_at)`, covering index `stock_levels (warehouse_id, product_id) INCLUDE (qty)`
- [ ] Reservation isolation level chosen after building the `SERIALIZABLE` + retry-on-`40001` version and reproducing write skew under `REPEATABLE READ`
- [ ] Deadlock reproduced on purpose, fixed by consistent lock ordering
- [ ] `lock_timeout`, `statement_timeout`, `idle_in_transaction_session_timeout` set and demonstrated
- [ ] **The outbox gap:** "DB commit succeeded, publish failed" triggered on purpose, documented and deliberately left unfixed (FleetTrack fixes it)
- [ ] Deliberately **no cache** — written justification

**Domain model**
```
warehouses(id, name, location)
warehouse_assignments(user_id, warehouse_id, role)
stock_levels(id, warehouse_id, product_id, qty)          UNIQUE(warehouse_id, product_id)
stock_movements(id, warehouse_id, product_id, delta, reason, ref_id, created_at)  -- partitioned by month
transfers(id, from_warehouse_id, to_warehouse_id, status[dispatched|received|cancelled], created_at)
transfer_items(id, transfer_id, product_id, qty)
reservations(id, order_ref, warehouse_id, product_id, qty, status, created_at)
pick_lists(id, reservation_id, status, picked_by, picked_at)
```

### Tech stack
| Tool / concept | Taught in |
|---|---|
| FastAPI, Pydantic v2 | B4 |
| SQLAlchemy 2.0, Alembic, layered architecture | B5 |
| JWT auth, roles | B6 |
| Resource-scoped (record-level) authorization | B6, B11 (object permissions) |
| Repository, Unit of Work, DI container, bounded contexts, domain events | B14 |
| RabbitMQ (topic exchange, DLX, confirms, QoS), aio-pika / pika | B15 |
| Pact message contracts | B15 |
| Kafka (comparison only, decision record) | B16 |
| Row locks, deadlocks, lock ordering, timeouts | B7, 1C 2.8 |
| Isolation levels, MVCC, write skew, `SERIALIZABLE` retry | 1C 2.7 |
| Range partitioning, `DEFAULT` partition | 1C 2.9 |
| BRIN, covering `INCLUDE` index, index-only scans | 1C 2.5, 1C 2.6 |
| Keyset pagination | B1, 1C 2.6 |
| Partition-maintenance scheduled job (Celery Beat, or `pg_partman`) | B13 |
| Docker Compose (api, postgres, rabbitmq, consumer) | B3 |
| GitHub Actions with Postgres + RabbitMQ service containers | B9 |
| pytest, factories, concurrency tests | B8, 1A.8 |

### Required knowledge
- Track 2: B1–B9, B13, B14, B15, B16
- Track 1: 1A.7 typing (`Protocol`), 1A.8 pytest, 1A.12 asyncio (aio-pika consumer); 1C 2.5–2.9 (indexes, EXPLAIN, isolation/MVCC, locking, partitioning)
- Previous projects: StockPilot (`Repository[T]`, event-log/materialized-sum pattern for stock)

### Milestones
- [ ] **M1 — Contexts, UoW, repositories.** New repo `wareflow/`; `docs/architecture.md` defines the Inventory/Fulfillment boundary **before** code; `Warehouse`, `StockLevel` entities; `UnitOfWork` over the SQLAlchemy session; repositories conforming to `Repository[T]`; `receive_stock` and `dispatch_transfer` services; resource-scoped permissions; boundary review hunting for leaks. Tag `v0.1-contexts`.
- [ ] **M2 — Messaging.** RabbitMQ in Compose with the management UI; `event_bus.py` publishing after UoW commit; Fulfillment consumer creating reservations; idempotent consumer; Pact message contract in CI; DLQ configured, poison message inspected by hand; durability pass (durable, persistent, confirms, prefetch, heartbeat) with a broker-restart test; `POST /transfers/{id}/receive`; one event traced end to end in `docs/notes.md`; `docs/rabbitmq-ops-notes.md`. Tag `v0.2-messaging`.
- [ ] **M3 — Postgres deep dive.** Reservations with row locks; `SERIALIZABLE` + retry vs `REPEATABLE READ` with reproduced write skew → documented choice; deadlock reproduced and fixed by lock ordering; three timeouts set and demonstrated; `stock_movements` partitioned by month with a maintenance job and `DEFAULT` partition; BRIN vs B-tree size and plan; covering index with `Heap Fetches: 0`; `EXPLAIN ANALYZE` before/after in `docs/partitioning-notes.md`. Tag `v0.3-postgres`.
- [ ] **M4 — Decision record, outbox gap, wrap.** `docs/rabbitmq-vs-kafka.md`; the commit-then-publish failure triggered and documented, not fixed; keyset-paginated stock endpoint; CI green with Postgres + RabbitMQ; `docs/postmortem.md`; scaling notes (100M `stock_movements` rows, RabbitMQ clustering/quorum queues named, where Compose began to strain). Tag `v1.0-wareflow`.

### Definition of done
- [ ] Two bounded contexts, no type leakage, boundary documented
- [ ] UoW commits/rolls back across multiple repositories as one unit (integration test)
- [ ] Events published only after commit
- [ ] Resource-scoped permissions enforced and tested at the API
- [ ] Pact contract green in CI; a payload change fails it
- [ ] DLQ configured, poison message inspected by hand
- [ ] Killing the consumer mid-processing loses no message (ack after processing)
- [ ] Same event delivered twice → one reservation
- [ ] Broker restart with N messages queued → N messages after restart
- [ ] With `prefetch_count=1` a slow consumer does not starve a fast one
- [ ] Deadlock reproduced and fixed; isolation level chosen and justified in writing; write skew reproduced
- [ ] Timeouts set and demonstrated
- [ ] BRIN + covering index chosen from plans; keyset pagination stable while rows are inserted
- [ ] Partitions created ahead of time; `DEFAULT` partition as a safety net
- [ ] `docs/architecture.md`, `docs/rabbitmq-ops-notes.md`, `docs/rabbitmq-vs-kafka.md`, `docs/partitioning-notes.md`, `docs/postmortem.md`
- [ ] Outbox gap documented, **not** solved
- [ ] Tag `v1.0-wareflow`

### Estimated hours
~60h (M1 14h, M2 18h, M3 18h, M4 10h)

### OPTIONAL extensions
- [ ] **ML: anomaly detection on `stock_movements`** (~8h) — an `IsolationForest` (scikit-learn) over `delta` magnitude, time of day, warehouse, product, run as a batch script per monthly partition; review the top 20 flagged movements in `docs/anomaly-notes.md` and state explicitly that "anomalous ≠ fraudulent". *Requires:* Track 3 ML Zoomcamp modules 1–4 (plus scikit-learn basics).

### Interview questions
1. Why is a warehouse transfer modeled as two events and not one transaction?
2. Which isolation level did you use for reservations, what anomaly does it prevent, and what does your retry loop do?
3. Durable queue, persistent message, publisher confirm — what does each protect against, and what is still not guaranteed with all three?
4. You published after commit. What can still go wrong, and how would you fix it?
5. Why is caching the wrong answer in this system?

---

**Answers**
1. Stock leaves A and arrives at B hours or days later, and a database transaction cannot stay open that long (locks, connections, failures). So dispatch and receipt are two local transactions linked by events; the state in between (`dispatched`) is a real, visible business state.
2. Example answer: `SERIALIZABLE`, because two concurrent reservations reading the same available quantity can each pass the check and together oversell (write skew) under `REPEATABLE READ`. Under `SERIALIZABLE` Postgres aborts one with `40001`; the retry loop re-runs the whole transaction with backoff, and the second attempt sees the updated quantity. (An alternative is `READ COMMITTED` + `SELECT ... FOR UPDATE` on the stock row — you must say which you chose and why.)
3. Durable queue survives a broker restart; persistent message is written to disk so it survives with the queue; publisher confirm tells the publisher the broker actually has it. Still not guaranteed: that it is processed exactly once, in order, or at all if the consumer keeps failing — and not that the DB and the publish agree (the outbox gap).
4. The commit can succeed and the publish fail (crash, broker down): the DB says "dispatched" but Fulfillment never hears it. Fix: transactional outbox — write the event into an `outbox` table in the same transaction and let a relay publish it (FleetTrack, B25).
5. Stock levels change constantly and are read to make decisions (can we reserve?). A stale value causes overselling or false "out of stock". The correct answer is fast, indexed reads from the source of truth (covering index, index-only scan), not a cache.

---

## Module B17 — Networking Fundamentals + Nginx (~12h)

**Why now:** CarePoint is the first system with more than one service behind
one front door, the first browser client, and the first TLS certificate you
will own. You cannot debug any of that without knowing what is on the wire.

**Topics**
- TCP vs UDP: handshake, reliability, flow/congestion control, head-of-line blocking; why latency matters more than bandwidth
- HTTP/1.1 (keep-alive, pipelining limits), HTTP/2 (binary framing, streams, multiplexing, HPACK), HTTP/3 over QUIC (named: why UDP)
- TLS 1.2 vs 1.3 handshake, certificates and chains, SNI, ALPN, what a CA does; HTTPS ≠ "secure app"
- DNS: resolution path, record types (A, AAAA, CNAME, MX, TXT, NS), TTLs and caching; `dig`, `curl -v`, `openssl s_client`, `ss`/`netstat`
- Reverse proxy vs forward proxy vs API gateway
- Nginx config model: `http`/`server`/`location` blocks, matching order, `proxy_pass`, upstreams
- Load balancing: round-robin, `least_conn`, `ip_hash`; passive health checks (`max_fails`, `fail_timeout`); upstream `keepalive`
- Headers you forward: `Host`, `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Request-ID` via `$request_id`
- Timeouts and buffering: `proxy_connect_timeout`, `proxy_read_timeout`, `proxy_buffering`, `client_max_body_size`; gzip
- TLS termination in Nginx; Let's Encrypt with certbot (HTTP-01 challenge), renewal
- WebSocket proxying: `Upgrade`/`Connection` headers, long read timeouts (used again in B26)
- Rate limiting at the edge: `limit_req_zone` / `limit_req` (burst, nodelay), `limit_conn`
- Access/error logs and log format with request id and upstream timing

**Theory**
- [ ] **B17.T1 Latency, TCP and UDP** — *High Performance Browser Networking* (Ilya Grigorik, hpbn.co) ch. 1 "Primer on Latency and Bandwidth", ch. 2 "Building Blocks of TCP", ch. 3 "Building Blocks of UDP".
- [ ] **B17.T2 TLS** — hpbn.co ch. 4 "Transport Layer Security (TLS)"; Cloudflare Learning Center "What happens in a TLS handshake?".
- [ ] **B17.T3 HTTP/1.1, HTTP/2, HTTP/3** — hpbn.co ch. 11 "HTTP 1.X" and ch. 12 "HTTP/2"; Cloudflare Learning Center "What is HTTP/3?".
- [ ] **B17.T4 DNS** — Cloudflare Learning Center "What is DNS?" and "DNS records"; Julia Evans' "How DNS works" zine (howdns.works) as a quick pass.
- [ ] **B17.T5 Nginx basics** — nginx.org "Beginner's Guide"; nginx docs "How nginx processes a request"; `ngx_http_core_module` docs for `location` matching.
- [ ] **B17.T6 Reverse proxy and load balancing** — docs.nginx.com "NGINX Reverse Proxy" and "HTTP Load Balancing"; `ngx_http_proxy_module` (`proxy_pass`, `proxy_set_header`, timeouts, buffering) and `ngx_http_upstream_module` (`keepalive`, `max_fails`).
- [ ] **B17.T7 TLS in Nginx + Let's Encrypt** — nginx.org "Configuring HTTPS servers"; letsencrypt.org "How It Works"; certbot docs "User Guide" (webroot / nginx plugin, renewal).
- [ ] **B17.T8 WebSockets and rate limiting** — nginx.org "WebSocket proxying"; docs.nginx.com "Limiting Access to Proxied HTTP Resources" (`limit_req`, `limit_conn`); nginx blog "Rate Limiting with NGINX".

**Exercises** (`backend/b17-networking-nginx/`)
- [ ] **B17.E1 See the wire** — run `curl -v https://example.com`, `dig +trace example.com`, `openssl s_client -connect example.com:443 -servername example.com`. Acceptance: `notes.md` annotates each output: DNS path, TCP connect, TLS version, cipher, certificate chain, HTTP version negotiated via ALPN.
- [ ] **B17.E2 Two upstreams, one front door** — Compose with Nginx + two tiny FastAPI apps. Route `/a/*` to app A and everything else to app B; forward `Host`, `X-Forwarded-For`, `X-Forwarded-Proto` and `X-Request-ID`. Acceptance: each app logs the same request id Nginx logged; `curl` through Nginx shows the correct app answering.
- [ ] **B17.E3 Load balancing and failure** — run 3 replicas of app B behind an `upstream` block. Acceptance: requests spread across replicas (log counts); stop one replica and show Nginx stops sending to it after `max_fails`; compare round-robin vs `least_conn` with one deliberately slow replica.
- [ ] **B17.E4 Timeouts and body size** — an endpoint that sleeps 70s and an upload of 20MB. Acceptance: with defaults, record what the client gets (504 / 413); tune `proxy_read_timeout` and `client_max_body_size` deliberately and write *why* the values you chose are right for your app.
- [ ] **B17.E5 Local TLS** — generate a local CA and certificate with `mkcert` (or self-signed with `openssl`), terminate TLS in Nginx, redirect HTTP→HTTPS, enable HTTP/2. Acceptance: `curl -v --http2` shows `HTTP/2` and your certificate; `notes.md` explains how certbot would replace this in production.
- [ ] **B17.E6 Edge rate limit** — `limit_req_zone` of 5 r/s per IP with `burst=10`. Acceptance: a `hey` run shows 503/429 responses beyond the limit (configure `limit_req_status 429`); explain `burst` and `nodelay` with your numbers.

**Must be able to do/explain**
- [ ] Explain what happens from typing a URL to receiving the first byte (DNS, TCP, TLS, HTTP).
- [ ] Compare HTTP/1.1, HTTP/2 and HTTP/3 and say what problem each solves.
- [ ] Read and write an `nginx.conf` with upstreams, locations, forwarded headers and timeouts.
- [ ] Explain reverse proxy vs API gateway.
- [ ] Terminate TLS in Nginx and explain how Let's Encrypt issues and renews certificates.
- [ ] Configure WebSocket proxying and an edge rate limit.
- [ ] Debug a 502 vs 504 vs 413 from Nginx logs.

**Estimated hours:** ~12h (theory 6h, exercises 6h)

### Self-check interview questions
1. Why does latency matter more than bandwidth for most web requests?
2. What does HTTP/2 multiplexing solve, and what head-of-line blocking remains?
3. Walk through a TLS 1.3 handshake at a high level. What does the certificate prove?
4. What is the difference between a CNAME and an A record, and why can't the zone apex usually be a CNAME?
5. Reverse proxy vs load balancer vs API gateway — how do they differ?
6. Nginx returns 502. What does that mean, and how is it different from 504?
7. Why does the backend need `X-Forwarded-For` and `X-Forwarded-Proto`, and when can you trust them?
8. What do `burst` and `nodelay` change in `limit_req`?

---

**Answers**
1. Most requests transfer little data but need several round trips (DNS, TCP handshake, TLS handshake, request/response). Each round trip costs the full latency, which bandwidth cannot reduce.
2. Many requests share one TCP connection as independent streams, so a slow response no longer blocks others at the HTTP level. But TCP itself is still ordered: a lost packet stalls all streams until retransmitted — HTTP/3 over QUIC removes that.
3. Client sends supported ciphers and a key share; server replies with its key share, certificate and a signature; both derive session keys — one round trip. The certificate (signed by a trusted CA) proves the server controls the private key for that domain name; it says nothing about whether the app is safe.
4. An A record maps a name to an IPv4 address; a CNAME says "this name is an alias of another name". The apex must also carry SOA/NS records, and a CNAME may not coexist with other records — so providers offer ALIAS/flattening instead.
5. A reverse proxy forwards client requests to backend servers (TLS, headers, buffering). A load balancer distributes requests across several backends with health checks. An API gateway adds API-level concerns — auth, rate limiting per client, request transformation, routing per API version, analytics. Nginx can do the first two and parts of the third.
6. 502 Bad Gateway: Nginx could not get a valid response — upstream refused the connection, crashed or sent garbage. 504 Gateway Timeout: the upstream accepted but did not respond within `proxy_read_timeout`.
7. Behind a proxy the app sees the proxy's IP and plain HTTP. These headers carry the original client IP and scheme (for logging, rate limiting, building redirect URLs). Trust them only when set by *your* proxy — configure the app to accept them only from known proxy addresses, otherwise clients can spoof them.
8. `burst` lets up to N excess requests queue instead of being rejected immediately; without `nodelay` they are released at the configured rate (added latency); with `nodelay` burst requests are served immediately but still count against the limit, and requests beyond the burst are rejected.

---

## Module B18 — Auth II: OAuth2, OIDC, Asymmetric JWT, Token Lifecycle (~12h)

**Why now:** CarePoint splits auth into its own service. Other services must
validate tokens without calling it, patients log in through an external
identity provider, and "logout" must really log out.

**Topics**
- OAuth2 roles (resource owner, client, authorization server, resource server) and grant types: Authorization Code, Client Credentials, Device (named); why Implicit and Password grants are deprecated
- Authorization Code + **PKCE** (`code_verifier`, `code_challenge`, S256); `state` against CSRF on the callback
- OpenID Connect: ID token vs access token, standard claims (`iss`, `sub`, `aud`, `exp`, `iat`, `nonce`), discovery document (`/.well-known/openid-configuration`), userinfo endpoint
- JWT structure and validation checklist: signature, `alg` allow-list, `iss`, `aud`, `exp`/`nbf` with clock-skew leeway; `alg=none` and algorithm-confusion attacks
- HS256 vs RS256/ES256: who can mint tokens vs who can only verify
- JWKS: publishing public keys, `kid` in the header, caching JWKS, **zero-downtime key rotation** (publish new → sign with new → keep old until last token expires → retire)
- Access vs refresh tokens; short access TTL; **refresh-token rotation**, reuse detection and family revocation; storing refresh tokens hashed; logout that actually revokes
- Token storage in browsers: httpOnly cookies vs memory vs localStorage; SameSite
- Keycloak as a local IdP: realms, clients (public vs confidential), redirect URIs, users, roles
- Service-to-service authentication: validating first-party tokens locally, client-credentials tokens; mTLS named
- Python libraries: `PyJWT` (with `cryptography`) or `joserfc`/`authlib` for OAuth2 client + JWKS

**Theory**
- [ ] **B18.T1 OAuth2 overview** — oauth.net/2 (pages "Grant Types", "Authorization Code", "PKCE"); Aaron Parecki, *OAuth 2.0 Simplified* (oauth.com), chapters "Authorization Code", "PKCE".
- [ ] **B18.T2 The specs, read selectively** — RFC 6749 "The OAuth 2.0 Authorization Framework" §1 (Introduction), §4.1 (Authorization Code Grant), §10 (Security Considerations, skim); RFC 7636 "Proof Key for Code Exchange by OAuth Public Clients" §1, §4.
- [ ] **B18.T3 OpenID Connect** — openid.net "OpenID Connect Core 1.0" §2 (ID Token), §3.1 (Authorization Code Flow), §3.1.3.7 (ID Token Validation); Okta developer blog "An Illustrated Guide to OAuth and OpenID Connect".
- [ ] **B18.T4 JWT done right** — RFC 7519 "JSON Web Token (JWT)" §4 (claims); RFC 8725 "JSON Web Token Best Current Practices" §2 (threats) and §3 (best practices); RFC 7517 "JSON Web Key (JWK)" §4–5 (JWK and JWK Set).
- [ ] **B18.T5 Current OAuth security advice** — RFC 9700 "Best Current Practice for OAuth 2.0 Security" §2 (recommendations summary); OWASP Cheat Sheet "JSON Web Token for Java" (read for the concepts) and "OAuth 2.0 Protocol Cheatsheet".
- [ ] **B18.T6 Refresh-token rotation** — Auth0 docs "Refresh Token Rotation" (reuse detection); OWASP "Session Management Cheat Sheet" (logout, session expiry).
- [ ] **B18.T7 Keycloak** — keycloak.org "Getting Started → Docker"; Server Administration Guide sections "Realms", "Managing OpenID Connect clients", "Roles".
- [ ] **B18.T8 Libraries** — PyJWT docs "Usage Examples" (RS256, `PyJWKClient`, `leeway`, `audience`, `issuer`); Authlib docs "OAuth 2 Session / Client" (optional).

**Exercises** (`backend/b18-auth2/`)
- [ ] **B18.E1 RS256 issuer + JWKS** — a FastAPI "auth" app with a `signing_keys` table (kid, private, public, created_at, retired_at), `POST /token` issuing RS256 tokens with `kid` in the header, and `GET /.well-known/jwks.json`. Acceptance: jwt.io (or PyJWT) verifies a token using only the JWKS; `mypy` clean.
- [ ] **B18.E2 Local validation in another service** — a second app validating tokens using a cached JWKS (refresh on unknown `kid`), checking `iss`, `aud`, `exp` with a 30s leeway, `alg` allow-listed to RS256. Acceptance: tests reject wrong signature, wrong `aud`, expired token (beyond leeway), `alg=none`, and an HS256 token signed with the public key as secret.
- [ ] **B18.E3 Zero-downtime rotation** — while `hey` sends continuous requests with tokens, add key B, switch signing to B, keep A in the JWKS until A's tokens expire, then retire A. Acceptance: zero `401`s during the run; a token signed by A is rejected after retirement.
- [ ] **B18.E4 Refresh-token rotation with reuse detection** — `refresh_tokens(id, user_id, token_hash, family_id, issued_at, expires_at, revoked_at, replaced_by)`; `POST /token/refresh` rotates; `POST /logout` revokes the family. Acceptance: using a rotated refresh token twice revokes the whole family (both old and new stop working); tokens are stored hashed; logout on device A invalidates refresh on device B when "log out everywhere" is chosen.
- [ ] **B18.E5 OIDC Authorization Code + PKCE against Keycloak** — Keycloak in Compose with a realm and a public client; your app implements `/oidc/start` (generates `state`, `nonce`, `code_verifier`) and `/oidc/callback` (checks `state`, exchanges code with the verifier, validates the ID token: signature via Keycloak's JWKS, `iss`, `aud`, `nonce`). Acceptance: an automated test (or scripted `httpx` flow) shows the happy path works and that a wrong `state`, wrong `nonce` or wrong `aud` is rejected.
- [ ] **B18.E6 Token storage decision** — `notes.md`: for a SPA on a different origin, compare httpOnly+SameSite cookie vs in-memory token vs localStorage against XSS and CSRF. Acceptance: a table with your recommendation and what else must be in place (CSRF defense or CSP).

**Must be able to do/explain**
- [ ] Draw the Authorization Code + PKCE flow and say what `state`, `nonce` and PKCE each protect against.
- [ ] Explain ID token vs access token and who each is meant for.
- [ ] List every check needed to validate a JWT.
- [ ] Explain why RS256 is preferred across services and how JWKS + `kid` enable rotation.
- [ ] Rotate a signing key with zero downtime.
- [ ] Implement refresh-token rotation with reuse detection and real logout.
- [ ] Configure a Keycloak realm and client for local development.

**Estimated hours:** ~12h (theory 5h, exercises 7h)

### Self-check interview questions
1. Walk through the Authorization Code flow with PKCE. What would an attacker do without PKCE?
2. What do `state` and `nonce` each protect against?
3. ID token vs access token — which one does your API accept, and why?
4. Why RS256 instead of HS256 when several services verify tokens?
5. How do you rotate a signing key with no downtime?
6. What is refresh-token rotation and how does reuse detection catch a stolen token?
7. List the checks you perform when validating a JWT.
8. Why were the Implicit and Resource Owner Password grants deprecated?

---

**Answers**
1. The client redirects the user to the authorization server with a `code_challenge` (hash of a random `code_verifier`); the user logs in; the server redirects back with a one-time `code`; the client exchanges the code plus the `code_verifier` for tokens over a back channel. Without PKCE, an attacker who intercepts the code (malicious app on the same redirect URI, logs, referrer) can exchange it; with PKCE they lack the verifier.
2. `state` binds the callback to the browser session that started the flow — it blocks CSRF / login-injection on the redirect URI. `nonce` is put into the ID token by the IdP and checked by the client — it blocks replay of a previously issued ID token.
3. The API accepts access tokens: they are meant for resource servers and carry scopes/audience for the API. The ID token is meant for the client, to learn who the user is; APIs should not accept it as an authorization credential.
4. With HS256 every verifier holds the shared secret and can therefore mint tokens — one compromised service can forge an admin token. With RS256 only the issuer holds the private key; verifiers get public keys, and keys can be rotated via JWKS without redistributing secrets.
5. Publish the new public key in the JWKS (with a new `kid`) → wait for verifier caches to refresh → start signing with the new key → keep the old public key published until the longest-lived token signed with it has expired → remove it.
6. Each refresh returns a new refresh token and invalidates the old one; all tokens of one login share a family id. If an old (already rotated) token is presented again, someone else used it — the server revokes the entire family, forcing both the thief and the user to log in again.
7. Allowed `alg` (never `none`, no switching), signature with the right key (by `kid`), `iss` equals expected issuer, `aud` contains this API, `exp` in the future and `nbf`/`iat` sane within a small leeway, plus any required claims (scope/role) and, for refresh or revocable tokens, a server-side check.
8. Implicit returns tokens in the URL fragment (leaks via history, referrers, no refresh, no client authentication) — PKCE makes the code flow safe for public clients. Password grant gives the client the user's password, defeating the purpose of delegated authorization and blocking MFA/SSO.

---

## Module B19 — Web Security Basics (~8h)

**Why now:** CarePoint holds patient data and is the first app a browser on
another origin talks to. From here on, every service ships with a security
baseline.

**Topics**
- OWASP Top 10 (2021): A01 Broken Access Control … A10 SSRF — what each looks like in a Python API
- Broken access control in practice: IDOR, checking ownership on every object, authorization before minting links
- Injection: SQL injection and why parameterized queries/ORMs prevent it; command injection; template injection (named)
- Same-origin policy; **CORS**: simple vs preflighted requests, `Access-Control-Allow-Origin` allow-list, credentials, why `*` with credentials is refused
- **CSRF**: why cookies make it possible, SameSite, CSRF tokens (Django's middleware), why bearer tokens in headers avoid it; CORS is *not* a CSRF defense
- XSS basics and Content Security Policy
- Security headers: HSTS, `X-Content-Type-Options: nosniff`, `X-Frame-Options`/`frame-ancestors`, `Referrer-Policy`, CSP starter policy
- Login hardening: argon2id password hashing, per-IP and per-account rate limit, lockout/backoff, **no user enumeration** (same body and similar timing), MFA named
- Input validation at the boundary (Pydantic/DRF serializers), size limits, allow-lists
- SSRF: fetching user-supplied URLs, blocking internal addresses
- Secrets hygiene: no secrets in git, `.env` handling, gitleaks; dependency scanning intro (`pip-audit`), CVEs
- Logging security events without logging secrets or PII

**Theory**
- [ ] **B19.T1 OWASP Top 10** — owasp.org/Top10 (2021 edition): read A01, A02, A03, A05, A07, A10 in full, skim the rest.
- [ ] **B19.T2 CORS** — MDN "Cross-Origin Resource Sharing (CORS)" (simple requests, preflighted requests, requests with credentials); MDN "Same-origin policy".
- [ ] **B19.T3 CSRF** — OWASP "Cross-Site Request Forgery Prevention Cheat Sheet"; Django docs "Cross Site Request Forgery protection"; MDN "SameSite cookies".
- [ ] **B19.T4 XSS and headers** — OWASP "Cross Site Scripting Prevention Cheat Sheet" (sections 1–3); OWASP "HTTP Security Response Headers Cheat Sheet"; MDN "Content Security Policy (CSP)".
- [ ] **B19.T5 Authentication hardening** — OWASP "Authentication Cheat Sheet" (sections "Authentication and Error Messages", "Protect Against Automated Attacks"); OWASP "Password Storage Cheat Sheet" (Argon2id); `argon2-cffi` docs.
- [ ] **B19.T6 Injection and SSRF** — OWASP "SQL Injection Prevention Cheat Sheet" (Defense Option 1); OWASP "Server Side Request Forgery Prevention Cheat Sheet" (skim).
- [ ] **B19.T7 Dependencies and secrets** — pip-audit README; gitleaks README; OWASP "Secrets Management Cheat Sheet" (sections 1–2).

**Exercises** (`backend/b19-security/`)
- [ ] **B19.E1 IDOR hunt** — take one of your earlier APIs (StockPilot or QuickServe), write a test where user A requests user B's object by id. Acceptance: the test fails first if any endpoint leaks, then passes after the fix; list every endpoint you checked in `notes.md`.
- [ ] **B19.E2 CORS preflight lab** — a FastAPI API on :8000 and a static HTML page served on :5500 calling it with `fetch` + `credentials: "include"`. Acceptance: first observe the browser error; then configure `CORSMiddleware` with an explicit allow-list; show that another origin is still refused and that `*` + credentials is rejected by the browser. Screenshot/notes of the preflight `OPTIONS` exchange.
- [ ] **B19.E3 CSRF demo** — a Django view using session auth; build an "attacker" page on another origin that auto-submits a form. Acceptance: with CSRF middleware disabled the attack works, enabled it is blocked (403); with `SameSite=Lax` explain which request types are still sent.
- [ ] **B19.E4 Login hardening** — `POST /login` with argon2id hashes, per-IP and per-account limits (Redis counters from B12), backoff/lockout after 10 failures. Acceptance: tests show unknown email and wrong password return byte-identical bodies and status; timing difference below a threshold you choose (hash a dummy password for unknown users); lockout expires correctly.
- [ ] **B19.E5 Headers baseline** — add HSTS, `nosniff`, `X-Frame-Options: DENY` (or CSP `frame-ancestors 'none'`), `Referrer-Policy` and a starter CSP (in Nginx or middleware). Acceptance: a test asserts every response has them; check with securityheaders.com or `curl -I` and record the grade/list.
- [ ] **B19.E6 Supply chain quick scan** — run `pip-audit` and `gitleaks detect` on one of your repos. Acceptance: `notes.md` lists findings and what you did about each (upgrade, ignore with justification, rotate secret).

**Must be able to do/explain**
- [ ] Name the OWASP Top 10 categories and give a Python/API example of the top five.
- [ ] Explain the same-origin policy, a CORS preflight, and why CORS is not an auth or CSRF mechanism.
- [ ] Explain when CSRF is possible and the defenses (SameSite, tokens, not using cookies).
- [ ] Choose and explain each security header you set.
- [ ] Harden a login endpoint against brute force and user enumeration.
- [ ] Explain why parameterized queries stop SQL injection.

**Estimated hours:** ~8h (theory 4h, exercises 4h)

### Self-check interview questions
1. What is IDOR and how do you prevent it systematically?
2. Explain a CORS preflight. Why is `Access-Control-Allow-Origin: *` with credentials refused?
3. Does CORS protect your API from CSRF? Why or why not?
4. What does HSTS do, and what is its risk if misconfigured?
5. How do you prevent user enumeration on login and password-reset endpoints?
6. Why argon2id rather than SHA-256 for passwords?
7. What is SSRF, and where could it appear in a backend you've built?

---

**Answers**
1. Insecure Direct Object Reference: the API trusts an id from the client without checking the caller may access that object. Prevent it by scoping every query by the caller (`WHERE owner_id = :me` / object-level permission checks) in one central place, and test it per endpoint.
2. For non-simple requests (custom headers, JSON content type, PUT/DELETE) the browser first sends `OPTIONS` with `Origin` and requested method/headers; the server must answer with matching `Access-Control-Allow-*` headers before the real request is sent. With credentials, a wildcard would let any site read authenticated responses, so the spec requires an explicit origin.
3. No. CORS controls whether a page can *read* the response; many cross-site requests (form posts) are still *sent* with cookies. CSRF defenses are SameSite cookies, CSRF tokens, or not using ambient credentials (bearer tokens in headers).
4. It tells browsers to use HTTPS only for the domain for a period (`max-age`), preventing downgrade/SSL-stripping. If you set a long `max-age` (or `includeSubDomains`/preload) before every subdomain supports HTTPS, those sites become unreachable until it expires.
5. Return the same status, body and similar timing for "no such user" and "wrong password" (hash a dummy password when the user doesn't exist); for password reset always answer "if the account exists, we sent an email"; rate-limit both.
6. SHA-256 is fast by design, so attackers can try billions of guesses per second on GPUs. Argon2id is deliberately slow and memory-hard with a per-password salt, making offline cracking expensive.
7. Server-Side Request Forgery: the server fetches a URL the attacker controls, reaching internal services or cloud metadata (`169.254.169.254`). It can appear in webhook URLs, "import from URL", image fetchers, or PDF generators.

---

## Module B20 — Object Storage: S3, MinIO, Presigned URLs (~4h)

**Why now:** CarePoint stores lab results and scans. The bytes must not live
in Postgres and must not stream through your API workers.

**Topics**
- Object storage model: buckets, keys (no real folders), objects, metadata, versioning, eventual vs strong consistency (S3 is now strongly consistent for reads after writes)
- Why not in the database or on the app server's disk
- MinIO as a local S3-compatible server in Compose
- `boto3` client: creating buckets, `put_object`, `get_object`, listing with prefixes
- **Presigned URLs**: presigned PUT for upload, presigned GET for download; authorize *before* minting; expiry as a security window
- Content-type and size limits on uploads; checksums
- Bucket policies: private by default, no public buckets for sensitive data
- Lifecycle rules (expire/transition objects), server-side encryption (named)
- Keeping DB metadata and stored objects consistent (orphans, upload-confirmation step)

**Theory**
- [ ] **B20.T1 S3 concepts** — AWS S3 User Guide "What is Amazon S3?" (buckets, objects, keys) and "Amazon S3 data consistency model" section.
- [ ] **B20.T2 Presigned URLs** — AWS S3 User Guide "Working with presigned URLs" ("Sharing objects with presigned URLs", "Uploading objects with presigned URLs"); boto3 docs "Presigned URLs" guide (`generate_presigned_url`, `generate_presigned_post`).
- [ ] **B20.T3 MinIO locally** — min.io docs "Deploy MinIO: Single-Node Single-Drive" (container) and "MinIO Client (mc)" quickstart.
- [ ] **B20.T4 Lifecycle and security** — AWS S3 User Guide "Managing your storage lifecycle" and "Blocking public access to your Amazon S3 storage" (overview sections).

**Exercises** (`backend/b20-object-storage/`)
- [ ] **B20.E1 MinIO + boto3** — MinIO in Compose, a script that creates a private bucket, uploads and lists objects under two prefixes. Acceptance: anonymous `curl` to the object URL is denied (403).
- [ ] **B20.E2 Presigned upload** — FastAPI `POST /files/presigned-upload` that checks the caller may upload, records metadata (`files(id, owner_id, key, content_type, status='pending')`) and returns a presigned PUT URL valid for 5 minutes. Acceptance: the client uploads directly to MinIO; API process memory stays flat during a 50MB upload; an upload after expiry fails.
- [ ] **B20.E3 Presigned download with authorization** — `GET /files/{id}/download` returns a short-lived presigned GET only to the owner. Acceptance: tests show another user gets 403 *before* any URL is minted; an expired URL is refused by MinIO.
- [ ] **B20.E4 Consistency between DB and storage** — add `POST /files/{id}/confirm` that verifies the object exists (HEAD) before `status='uploaded'`, and a cleanup script for `pending` rows older than 1 hour. Acceptance: tests cover "row but no object" and "object but row never confirmed".

**Must be able to do/explain**
- [ ] Explain why file bytes go to object storage and not through the API or into Postgres.
- [ ] Implement presigned upload and download and justify the expiry you picked.
- [ ] Explain why authorization must happen before minting a presigned URL.
- [ ] Keep DB metadata and objects consistent.

**Estimated hours:** ~4h (theory 1.5h, exercises 2.5h)

### Self-check interview questions
1. Why use presigned URLs instead of uploading through your API?
2. How long should a presigned URL live, and what is the trade-off?
3. Once a presigned URL exists, who can use it?
4. What happens if the client gets a presigned URL but never uploads?
5. Why not store documents as `bytea` in Postgres?

---

**Answers**
1. The bytes go directly between client and storage, so API workers aren't tied up streaming large files, memory stays flat, and storage bandwidth scales independently. The API only authorizes and stores metadata.
2. Long enough for the client to start the transfer (minutes), short enough that a leaked URL is useless soon. Longer lifetimes improve UX on slow networks but widen the window for misuse.
3. Anyone who holds it, until it expires — it's a bearer credential. That's why authorization happens before minting, lifetimes are short, and URLs are never logged or shared.
4. You have an orphan metadata row in `pending`. Use a confirm step (HEAD the object, or a storage event) and a cleanup job for stale pending rows.
5. It bloats the database, backups and replication, puts large reads through DB connections, and costs more than object storage. Postgres should hold the metadata; object storage holds the blobs.

---

## Module B21 — Frontend for Backend Engineers: React + TypeScript · OPTIONAL (~25h)

**Why optional:** backend roles rarely require frontend depth, but being able to
build a small typed client for your own API makes you a much better API
designer (CORS, caching, pagination, error shapes become real). Every frontend
milestone in P5, P7, P8 and P10 depends on this module and is itself optional.

**Topics**
- TypeScript essentials: types vs interfaces, unions and narrowing, generics, `unknown` vs `any`, strict mode; typing API responses
- Tooling: Node + npm/pnpm, Vite project layout, ESLint + Prettier, env variables (`import.meta.env`)
- React fundamentals: components, JSX, props, state (`useState`), effects (`useEffect`) and their pitfalls, lists and keys, controlled forms
- Thinking in React: component hierarchy, lifting state, derived state
- Data fetching with **TanStack Query**: query keys, caching and staleness, `invalidateQueries` on mutation, polling (`refetchInterval`), pagination/infinite queries, error and loading states — and the parallel with server-side cache-aside
- A typed API client (hand-written `fetch` wrapper or generated from the backend's OpenAPI with `openapi-typescript`)
- React Router: routes, nested layouts, params, protected routes
- Auth in the browser: token handling decision from B18.E6, sending credentials, handling 401 → refresh
- Debouncing input (search boxes)
- Testing: Vitest + **React Testing Library** (query by role, user events); **Playwright** E2E basics (locators, auto-waiting, running against Compose)
- Building and serving the static bundle (Nginx or a bucket + CDN later)

**Theory**
- [ ] **B21.T1 TypeScript** — TypeScript Handbook (typescriptlang.org/docs/handbook): "The Basics", "Everyday Types", "Narrowing", "More on Functions", "Object Types", "Generics".
- [ ] **B21.T2 React basics** — react.dev "Learn": "Quick Start", "Tutorial: Tic-Tac-Toe", "Thinking in React".
- [ ] **B21.T3 State and effects** — react.dev "Learn → Adding Interactivity" (all), "Managing State" (all), "Escape Hatches → Synchronizing with Effects" and "You Might Not Need an Effect".
- [ ] **B21.T4 Vite** — vite.dev "Getting Started" and "Env Variables and Modes".
- [ ] **B21.T5 TanStack Query** — tanstack.com/query docs (React): "Overview", "Quick Start", "Guides → Queries", "Query Keys", "Mutations", "Query Invalidation", "Paginated Queries", "Important Defaults".
- [ ] **B21.T6 React Router** — reactrouter.com docs "Tutorial" (or "Start → Routing" for the current version).
- [ ] **B21.T7 Testing** — testing-library.com "React Testing Library → Introduction" and "Example"; "Guiding Principles"; Vitest "Getting Started".
- [ ] **B21.T8 Playwright** — playwright.dev "Installation", "Writing tests", "Locators", "Auto-waiting" (Node/TypeScript docs).

**Exercises** (`frontend/b21-react-ts/`)
- [ ] **B21.E1 TypeScript drills** — type 10 real JSON responses from one of your APIs (success and error shapes) with discriminated unions. Acceptance: `tsc --strict` passes; a function narrowing a `Result<T>` union has no `any`.
- [ ] **B21.E2 First component tree** — Vite + React + TS app listing products from StockPilot/QuickServe with a search box and a detail view. Acceptance: no `useEffect` for derived state; loading, empty and error states rendered; ESLint clean.
- [ ] **B21.E3 TanStack Query** — replace hand-written fetching with TanStack Query; add a mutation that creates an item and invalidates the list. Acceptance: React Query Devtools show cache hits on navigation; after the mutation only the affected query refetches; `notes.md` maps query keys to your server's cache keys.
- [ ] **B21.E4 Typed client from OpenAPI** — generate types from your FastAPI `openapi.json` with `openapi-typescript`. Acceptance: renaming a field in the backend makes `tsc` fail in the frontend.
- [ ] **B21.E5 Router + protected routes + auth** — login page, protected pages, 401 handling that triggers a refresh then retries once. Acceptance: expired access token is refreshed transparently; failing refresh redirects to login.
- [ ] **B21.E6 Tests** — 3 React Testing Library tests (render, user interaction, error state) and 1 Playwright test that logs in and performs one action against the app running in Compose. Acceptance: both suites run in CI (GitHub Actions job).

**Must be able to do/explain**
- [ ] Build a typed React + TS app with Vite that talks to your API.
- [ ] Explain props vs state, when an effect is needed and when it isn't.
- [ ] Use TanStack Query keys, invalidation and polling, and relate them to server caching.
- [ ] Handle auth tokens and 401/refresh in the browser.
- [ ] Write a React Testing Library test and a Playwright E2E test.

**Estimated hours:** ~25h (theory 10h, exercises 15h)

### Self-check interview questions
1. What does TypeScript's strict mode buy you when consuming an API?
2. Props vs state — what's the difference?
3. Why is "fetch in `useEffect` and store in state" usually replaced by a data-fetching library?
4. What is a query key in TanStack Query, and how does invalidation work?
5. How should a SPA handle an expired access token?
6. What does React Testing Library encourage you to test, and why?

---

**Answers**
1. Null/undefined checks, no implicit `any`, and compile-time errors when the response shape changes — bugs move from runtime to build time, especially with generated API types.
2. Props are inputs passed by the parent (read-only for the child); state is data owned by a component that changes over time and triggers re-render.
3. Hand-rolled fetching must re-implement caching, deduplication, retries, stale data, race conditions and loading/error states. A library like TanStack Query handles those consistently.
4. A serializable array identifying the data (`["products", {page: 2}]`). Cached results are stored under it; `invalidateQueries(["products"])` marks matching entries stale and refetches the active ones — like deleting cache-aside keys after a write.
5. Intercept the 401, call the refresh endpoint once (serialize concurrent refreshes), retry the original request with the new token; if refresh fails, clear auth state and redirect to login.
6. Behavior the user sees (query by role/label/text, simulate user events) instead of implementation details (state, internal methods). Tests then survive refactors and catch real regressions.

---

## Project P5 — CarePoint · Middle (~50h)

**Clinic appointment & patient records system — the first real service split.**

### Goal
A small clinic needs patients to book appointments online, staff to manage a
daily schedule per doctor, and doctors to attach documents (lab results, scans)
to a patient's record securely — today it is a paper diary and emailed PDFs.
Three structural lessons: (1) what a service split actually costs, learned with
two services rather than ten; (2) let the **database** enforce what must never
happen instead of hoping application code wins a race; (3) this is **the auth
project** — OAuth2/OIDC, asymmetric keys with rotation, and a browser-facing
security posture (CORS, headers, login protection) are built here and reused by
every later service.

### Features
- [ ] Two independently deployable services behind one Nginx entrypoint: `auth-service` (FastAPI) and `clinic-service` (Django/DRF)
- [ ] RS256 JWTs issued by `auth-service`, public keys at `/.well-known/jwks.json`, `kid` in the header; `clinic-service` validates **locally** with a cached JWKS
- [ ] **Live key rotation** under load with zero `401`s
- [ ] Staff password login: argon2, per-IP + per-account rate limit, lockout/backoff, identical response for unknown user / wrong password
- [ ] Patient login with **OAuth2 Authorization Code + PKCE** via Keycloak (in Compose) or Google; ID-token validation (`iss`, `aud`, `nonce`, signature via the IdP's JWKS); patient linking; first-party tokens issued
- [ ] Refresh-token rotation, family revocation, working `POST /auth/logout`
- [ ] Appointment booking where double-booking is refused **by a Postgres `EXCLUDE` constraint** (`btree_gist`, `tstzrange` overlap per doctor, ignoring cancelled appointments)
- [ ] `timestamptz` everywhere, clinic timezone `Asia/Tashkent`; DST change-over test
- [ ] Patient documents via presigned PUT/GET to MinIO — bytes never pass through the API; authorization before minting
- [ ] Redis-cached doctor daily schedule, invalidated on booking and cancel
- [ ] 24h reminder job on Celery Beat
- [ ] CORS allow-list (no `*` with credentials) and security headers (HSTS, `nosniff`, `X-Frame-Options`, starter CSP)
- [ ] `X-Request-ID` generated by Nginx and propagated through both services and Celery, visible in every log line
- [ ] `/health` per service checking real dependencies (DB, Redis)
- [ ] CI builds and pushes one image per service to GHCR
- [ ] OPTIONAL: `carepoint-web/` — React/TS page showing a doctor's daily schedule (needs B21)

**Roles:** `patient` (own appointments/documents), `receptionist` (all appointments, no clinical documents), `doctor` (own schedule; documents of own patients), `clinic_admin` (manage doctors/users/hours; state whether they may read clinical documents).

**Domain model**
```
doctors(id, name, specialty)
patients(id, name, dob, contact, oidc_subject NULL, oidc_issuer NULL)
appointments(id, doctor_id, patient_id, slot_start timestamptz, slot_end timestamptz, status)
    -- EXCLUDE constraint: no overlapping slots per doctor (non-cancelled)
documents(id, patient_id, s3_key, uploaded_by, uploaded_at)
-- auth-service
signing_keys(kid, private_pem, public_pem, created_at, retired_at NULL)
refresh_tokens(id, user_id, token_hash, family_id, issued_at, expires_at, revoked_at NULL, replaced_by NULL)
login_attempts(email, failed_count, locked_until NULL, updated_at)
```

**API**
| Method | Path | Service | Notes |
|---|---|---|---|
| POST | `/auth/login` | auth | staff login, rate-limited |
| GET | `/auth/oidc/start`, `/auth/oidc/callback` | auth | Authorization Code + PKCE |
| POST | `/auth/token/refresh`, `/auth/logout` | auth | rotation / family revocation |
| GET | `/.well-known/jwks.json` | auth | current + retiring keys |
| GET | `/appointments?doctor_id=&date=` | clinic | Redis-cached |
| POST | `/appointments` | clinic | DB constraint prevents double-booking |
| PATCH | `/appointments/{id}/cancel` | clinic | invalidates cache |
| POST | `/documents/presigned-upload` | clinic | doctor only |
| GET | `/documents/{id}/presigned-download` | clinic | doctor / owning patient, short-lived |
| GET | `/health` | both | real dependency checks |

### Tech stack
| Tool / concept                                                                            | Taught in                 |
| ----------------------------------------------------------------------------------------- | ------------------------- |
| FastAPI (auth-service)                                                                    | B4                        |
| Django + DRF (clinic-service), custom auth class/middleware                               | B10, B11                  |
| PostgreSQL, `btree_gist`, `EXCLUDE` constraint, `tstzrange`, `timestamptz`                | 1C 1.5, 1C 1.6, 1C 2.5    |
| SQLAlchemy/Alembic (auth-service persistence)                                             | B5                        |
| RS256, JWKS, `kid`, key rotation, refresh-token rotation (PyJWT/cryptography)             | B18                       |
| OAuth2 Authorization Code + PKCE, OIDC, Keycloak                                          | B18                       |
| argon2, login rate limit/lockout, no enumeration, CORS, security headers                  | B19 (+ B6 hashing basics) |
| Redis cache-aside + counters                                                              | B12                       |
| Celery + Beat, freezegun time travel                                                      | B13                       |
| Nginx: routing, `$request_id`, timeouts, keepalive, gzip, `client_max_body_size`, headers | B17                       |
| MinIO / S3, boto3, presigned URLs                                                         | B20                       |
| structlog with bound request id                                                           | 1A.9                      |
| Docker Compose (nginx, auth, clinic, postgres, redis, minio, worker, keycloak)            | B3                        |
| GitHub Actions build + push to GHCR                                                       | B9                        |
| `hey` load generation during key rotation                                                 | B8                        |
| React + TS + Vite + TanStack Query (OPTIONAL frontend)                                    | B21                       |

### Required knowledge
- Track 2: B1–B13, B17, B18, B19, B20 (B21 only for the optional frontend)
- Track 1: 1A.9 logging, 1A.8 pytest; 1C 1.5 date/time functions, 1C 1.6 constraints, 1C 2.5 index types (GiST/`btree_gist`)
- Previous projects: StockPilot (JWT basics), QuickServe (Django/DRF, Redis cache invalidation), PeopleOps (Celery Beat reminder pattern)

### Milestones
- [ ] **M1 — Service split & booking.** Repo `carepoint/`; `auth-service` with `signing_keys`, RS256, JWKS, `kid`; `clinic-service` JWT validation middleware with cached JWKS; staff login hardening; `appointments` with `timestamptz` and the `EXCLUDE` constraint; `POST /appointments` plus a concurrency test firing two identical bookings (exactly one wins, rejected by the DB); `nginx.conf` routing both services. Tag `v0.1-split`.
- [ ] **M2 — Rotation, OIDC, token lifecycle.** Live key rotation under `hey` load with zero `401`s; Keycloak in Compose; OIDC Authorization Code + PKCE for patients with full ID-token validation; refresh-token rotation, reuse detection, logout; `docs/auth-notes.md` (HS256→RS256, OIDC flow, rotation). Tag `v0.2-auth`.
- [ ] **M3 — Documents, cache, reminders, security posture.** MinIO in Compose; presigned upload/download with authorization before minting and an expiry test; Redis-cached schedule invalidated on booking/cancel; Celery Beat 24h reminder with a time-travel test; CORS allow-list and security headers; `X-Request-ID` end to end; `/health` per service; DST test. Tag `v0.3-records`.
- [ ] **M4 — CI/CD and wrap.** GitHub Actions builds and pushes both images to GHCR; OIDC flow test against Keycloak in CI; `docs/scaling-notes.md` — why `auth-service` might scale independently (if unconvincing, say so honestly); postmortem. Tag `v1.0-carepoint`.
- [ ] **M5 — OPTIONAL frontend.** `carepoint-web/` (Vite + React + TS + TanStack Query) showing a doctor's daily schedule; hit the CORS wall and fix it by understanding the preflight; query keys mirroring server cache keys; invalidate on mutation. *Requires B21.*

### Definition of done
- [ ] Two services behind Nginx, one entrypoint
- [ ] JWT issued by auth-service (RS256 + JWKS + `kid`), validated locally by clinic-service
- [ ] Live rotation with zero `401`s; token from a retired key rejected
- [ ] OIDC + PKCE tested against Keycloak in CI: wrong `state`, wrong `nonce`, wrong `aud` rejected; happy path links the patient
- [ ] Refresh-token rotation, family revocation, working logout
- [ ] Login rate limit + lockout; unknown email and wrong password give identical responses
- [ ] `EXCLUDE` constraint proven under concurrent booking
- [ ] Presigned upload/download working; bytes never touch the API; expired URL refused; a patient cannot mint a URL for another patient's document
- [ ] Schedule cache invalidated on booking and cancellation
- [ ] 24h reminder job on Beat, tested with time travel
- [ ] CORS allow-list and security headers tested
- [ ] `timestamptz` everywhere; DST test green
- [ ] `X-Request-ID` visible in Nginx, both services and Celery logs for one booking
- [ ] `/health` fails when Postgres or Redis is down
- [ ] Images built and pushed to GHCR by CI
- [ ] `docs/auth-notes.md`, `docs/scaling-notes.md`
- [ ] Tag `v1.0-carepoint`

### Estimated hours
~50h (M1 14h, M2 14h, M3 14h, M4 8h) + optional M5 ~8h

### OPTIONAL extensions
- [ ] **Frontend** — M5 above. *Requires:* B21.
- [ ] **LLM/RAG patient-FAQ "first touch"** (~10h) — a small static corpus of synthetic FAQ markdown files (never real patient data), chunked and embedded via a hosted embedding API into `pgvector` in the existing Postgres; `/faq/ask` embeds the question, retrieves top-k chunks and returns an LLM answer with cited source chunks; `docs/rag-notes.md` states why it's not production-safe (no evaluation, no guardrails). *Requires:* Track 3 LLM Zoomcamp modules 1–2.
- [ ] **Telegram reminder channel** (~4h) — patients link a Telegram chat with a one-time code; the existing reminder task also sends via the bot when a chat is linked (email branch unchanged). *Requires:* B-opt (aiogram).

### Interview questions
1. Why split auth into its own service here, and what did it cost you?
2. How does a database `EXCLUDE` constraint prevent double-booking better than an application check?
3. How do two services agree on JWT validity without calling each other on every request, and how do you rotate the signing key with zero downtime?
4. Walk through the Authorization Code flow with PKCE. What do `state` and `nonce` protect against?
5. Why presigned URLs, and how long should they live?

---

**Answers**
1. To feel the trade-off while the system is small: auth has a different security profile and may scale differently (login bursts). Costs: a second deployable, image, health check and log stream; key management and rotation; agreement on clock skew; more moving parts in local dev. Most real systems would not split this early.
2. An application "check then insert" has a gap — two concurrent requests both see a free slot and both insert. `SELECT ... FOR UPDATE` can close it but must be remembered on every code path. The constraint is enforced by the database for every writer, and the second concurrent insert fails with a constraint violation.
3. `auth-service` signs with a private RS256 key and publishes public keys in a JWKS; `clinic-service` caches the JWKS and verifies locally, picking the key by `kid`. Rotation: publish the new key, let caches refresh, sign with the new key, keep the old public key until its last token expires, then retire it.
4. Browser → IdP with `code_challenge`, `state`, `nonce`; user authenticates; IdP redirects back with a code; auth-service checks `state`, exchanges code + `code_verifier`, validates the ID token (signature, `iss`, `aud`, `nonce`) and issues its own tokens. `state` stops CSRF on the callback; `nonce` stops ID-token replay; PKCE stops a stolen code from being exchanged.
5. The file bytes go straight between the client and MinIO, so API workers never buffer or stream large files. Lifetime: a few minutes — enough to start the transfer; a leaked URL is usable by anyone until it expires, so keep it short and authorize before minting.

---

## Module B22 — Resilience Patterns (~8h)

**Why this module:** the first time one of your services makes a synchronous
call to another (LedgerBase: invoicing → ledger), "the network is reliable"
stops being true. This module teaches the patterns that keep one failing
dependency from taking the whole system down with it.

**Required knowledge:** B4 FastAPI, B8 Testing, B13 Celery (task retries), 1A.12 asyncio.

**Topics:**
- Failure modes of a remote call: refused, reset, slow, hung, partial success, "succeeded but the response was lost"
- **Timeouts everywhere**: connect vs read timeouts, per-call and total deadlines, why the default timeout of most HTTP clients is "forever"
- **Retry** with exponential backoff and **jitter** (full / equal / decorrelated); what is safe to retry (idempotent vs non-idempotent calls)
- **Retry budgets** and retry amplification across layers (3 layers × 3 retries = 27 calls)
- **Circuit breaker**: closed / open / half-open; failure thresholds, cooldown, trial calls; in-process vs shared state across replicas
- Libraries: `tenacity` (retries), `pybreaker` (circuit breaker) — and hand-rolling both once to understand them
- **Bulkhead**: isolating resource pools (connection pools, semaphores, worker pools) per dependency
- **Fallbacks** and graceful degradation: cached value, default, "feature temporarily unavailable" — and when a fallback is dangerous (money!)
- **Fault injection**: killing a container, adding latency, returning 500s — testing resilience on purpose
- **Slow vs dead dependency**: why a slow dependency is worse than a dead one (it holds your workers hostage)

### Lessons
- [ ] **B22.1 Why distributed calls fail** — *Release It!* 2nd ed. (Nygard), Part I "Create Stability", chapter "Stability Antipatterns" (sections "Integration Points", "Cascading Failures", "Slow Responses").
- [ ] **B22.2 Timeouts, retries, backoff, jitter** — AWS Builders' Library, "Timeouts, retries, and backoff with jitter" (aws.amazon.com/builders-library); AWS Architecture Blog, "Exponential Backoff And Jitter".
- [ ] **B22.3 Circuit breaker and bulkhead** — *Release It!* 2nd ed., chapter "Stability Patterns" (sections "Timeouts", "Circuit Breaker", "Bulkheads", "Fail Fast", "Let It Crash"); Martin Fowler, "CircuitBreaker" (martinfowler.com/bliki/CircuitBreaker.html).
- [ ] **B22.4 Libraries** — `tenacity` docs (tenacity.readthedocs.io): "Waiting before retrying", "Stopping", "Retrying code block"; `pybreaker` README (github.com/danielfm/pybreaker); `httpx` docs "Timeouts".
- [ ] **B22.5 Fault injection** — Toxiproxy README (github.com/Shopify/toxiproxy) — read only the "Toxics" section now (full use comes in B35); Principles of Chaos Engineering (principlesofchaos.org).

### Exercises
- [ ] **Ex B22.1 — Timeout audit.** Write a tiny FastAPI "slow service" with an endpoint that sleeps for a configurable time. Call it from a second script using `httpx` with (a) no timeout, (b) a 1s read timeout. **Acceptance:** you can show in the output that (a) hangs as long as the server wants, (b) fails in ~1s with a timeout exception; write 3 lines in `notes.md` on what "no timeout" means for a web worker.
- [ ] **Ex B22.2 — Hand-rolled retry with backoff + jitter.** Implement a `retry(max_attempts, base_delay, max_delay, jitter)` decorator (sync and async versions). It must only retry on exceptions you list. **Acceptance:** tests with a fake function that fails N times then succeeds; delays grow exponentially and never exceed `max_delay`; with jitter enabled two runs produce different delays; a non-listed exception is raised immediately.
- [ ] **Ex B22.3 — Hand-rolled circuit breaker.** Implement a `CircuitBreaker` class with the three states, a failure threshold, a cooldown, and one trial call in half-open. Inject a clock so tests don't sleep. **Acceptance:** tests prove: closed → open after N failures; open fails fast *without calling* the function; after the cooldown exactly one trial call is allowed; success → closed, failure → open again.
- [ ] **Ex B22.4 — Same thing with libraries.** Rewrite Ex B22.2 and B22.3 using `tenacity` and `pybreaker`. **Acceptance:** the same tests pass; in `notes.md`, list 2 things the libraries do that your version didn't.
- [ ] **Ex B22.5 — Bulkhead.** Service A calls two dependencies B (healthy) and C (slow: 5s). Limit concurrent calls to each with its own `asyncio.Semaphore`. **Acceptance:** under `hey` load, requests that only need B keep low latency while C is slow; without the bulkhead (one shared limit) they degrade — record both p95 numbers.
- [ ] **Ex B22.6 — Retry amplification.** Draw (in `notes.md`) a 3-layer call chain where each layer retries 3 times. Compute the worst-case number of calls to the bottom service, then propose where retries should live and where they should not.

### Must be able to do / explain
- [ ] Set connect/read timeouts on every outgoing HTTP call and explain the chosen values
- [ ] Explain why jitter matters (thundering herd) and draw backoff curves with and without it
- [ ] Say which operations are safe to retry and why a non-idempotent POST is not
- [ ] Draw the circuit breaker state machine and explain what moves it between states
- [ ] Explain why "retry alone" makes an outage worse
- [ ] Explain the bulkhead pattern with a concrete resource (pool, semaphore)
- [ ] Explain why a slow dependency is more dangerous than a dead one
- [ ] Explain the consequence of an in-process breaker with 3 replicas

**Estimated hours:** ~8h

### Self-check interview questions
1. What is the difference between a connect timeout and a read timeout?
2. Why add jitter to exponential backoff?
3. Which requests are safe to retry automatically?
4. Walk me through the three states of a circuit breaker.
5. Why is a circuit breaker that never half-opens worse than no breaker?
6. What is a bulkhead, and what resource would you isolate first?
7. Why is a slow dependency often worse than a dead one?
8. What is retry amplification and how do you prevent it?
9. When is a fallback value dangerous?

---

**Answers**
1. Connect timeout limits how long you wait to establish the TCP (and TLS) connection; read timeout limits how long you wait for data once connected. A dead host trips the first; a hung server trips the second.
2. Without jitter, all clients that failed together retry together, creating synchronized load spikes (thundering herd). Jitter spreads retries in time.
3. Idempotent ones: GET, PUT/DELETE designed idempotently, or a POST protected by an idempotency key. Also only on transient errors (timeouts, 502/503/504, connection reset) — never on 4xx validation errors.
4. Closed: calls pass; failures are counted. Open: calls fail immediately without touching the dependency. After a cooldown → half-open: one trial call; success → closed, failure → open.
5. Because after one incident it stays open forever and the system is permanently degraded until someone restarts the process; recovery must be automatic.
6. Isolating resources (connection pools, threads, semaphores) per dependency so that one exhausted dependency cannot consume all capacity. Usually the outgoing HTTP/DB connection pool per downstream service.
7. A dead dependency fails fast; a slow one holds your workers/connections waiting, so your own capacity is exhausted and you fail for everyone, including requests that don't need it.
8. Each layer retrying multiplies calls to the bottom layer (e.g. 3 × 3 × 3 = 27). Retry at one layer only (usually closest to the caller that knows the context), use retry budgets and circuit breakers.
9. When it produces a wrong answer that looks right — e.g. a stale balance or price in financial flows. There, failing clearly is better than a plausible wrong value.

---

## Module B23 — CI/CD II & Deploying to a VPS (~15h)

**Why this module:** B9 gave you CI (lint, type check, tests) and pushing an
image. This module turns that into **continuous delivery** to a real Linux
server: secure server setup, staged environments, security gates that fail
the build, zero-downtime rollouts with a tested rollback path, and database
changes that never take the site down.

**Required knowledge:** B2 Linux, B3 Docker/Compose, B5 Alembic, B9 GitHub Actions CI, B17 Nginx + certbot, 1C 2.5 indexes, 2.8 locking.

**Topics:**
- **VPS basics**: creating a non-root sudo user, SSH keys only (no passwords), `ufw` firewall, automatic security updates, `systemd` services and `journalctl`
- Deploy users and least-privilege SSH keys for CI
- **Image flow**: build once → tag with the git SHA → push to **GHCR** → the *same* image is promoted through environments
- **Environments**: staging → prod, GitHub Actions *environments* with required reviewers (manual approval), environment-scoped secrets
- **Secrets in GitHub Actions**: repository vs environment secrets, `GITHUB_TOKEN` permissions, never echoing secrets, OIDC mention
- **Supply-chain gates that fail the build**: `pip-audit` (dependency CVEs), `gitleaks` (committed secrets), Trivy (image vulnerabilities); pinned base images, multi-stage non-root Dockerfiles, `HEALTHCHECK`
- **SSH deploy with Compose**: pull, run the new version, switch, clean up
- **Zero-downtime rollover**: start new alongside old → health-gate → switch Nginx upstream → stop old; the **abort path**; rollback by redeploying the previous SHA
- **Graceful shutdown**: SIGTERM handling, `uvicorn --timeout-graceful-shutdown`, `gunicorn --graceful-timeout`, Celery warm shutdown, Compose `stop_grace_period`
- **Zero-downtime schema changes**: expand/contract across several deploys, batched backfills, `SET lock_timeout`, `CREATE INDEX CONCURRENTLY` (outside a transaction in Alembic), instant vs table-rewriting `ADD COLUMN ... DEFAULT`
- **API versioning**: URL vs header vs additive-only; `Deprecation` and `Sunset` headers; a written deprecation window

### Lessons
- [ ] **B23.1 Secure a fresh server** — DigitalOcean tutorial "Initial Server Setup with Ubuntu" (digitalocean.com/community/tutorials); Ubuntu Server docs "Firewall (ufw)"; `man systemd.service` (sections `[Service]`, `Restart=`); DigitalOcean "How To Use Journalctl to View and Manipulate Systemd Logs".
- [ ] **B23.2 GitHub Actions for delivery** — GitHub Docs: "Using environments for deployment", "Using secrets in GitHub Actions", "Automatic token authentication" (`GITHUB_TOKEN` permissions), "Publishing Docker images" (GHCR), "Reusing workflows".
- [ ] **B23.3 Supply-chain gates** — `pip-audit` README (github.com/pypa/pip-audit); `gitleaks` README (github.com/gitleaks/gitleaks); Trivy docs "Container Image" scanning and `--exit-code` / `--severity` flags (trivy.dev); Docker docs "Building best practices" (multi-stage, non-root user, pinning).
- [ ] **B23.4 Zero-downtime deploys and graceful shutdown** — Uvicorn docs "Settings" (`--timeout-graceful-shutdown`); Gunicorn docs "Settings" (`graceful_timeout`, `timeout`); Docker Compose file reference `stop_grace_period`, `healthcheck`; Nginx docs `ngx_http_upstream_module` + `nginx -s reload` behaviour ("Controlling nginx").
- [ ] **B23.5 Zero-downtime migrations** — PostgreSQL docs `CREATE INDEX` → section "Building Indexes Concurrently"; `ALTER TABLE` → Notes (which forms rewrite the table); runtime config `lock_timeout`; Alembic docs "Cookbook" (running operations outside a transaction / `autocommit_block`); Martin Fowler / Pramod Sadalage "Evolutionary Database Design" (martinfowler.com/articles/evodb.html); "Parallel Change" (martinfowler.com/bliki/ParallelChange.html).
- [ ] **B23.6 API versioning** — Microsoft REST API Guidelines, section "Versioning" (github.com/microsoft/api-guidelines); RFC 8594 "The Sunset HTTP Header Field"; IETF RFC 9745 "The Deprecation HTTP Header Field".

### Exercises
- [ ] **Ex B23.1 — Harden a VPS.** On a cheap VPS (or a local VM with Multipass/VirtualBox): create a sudo user, SSH-key-only login, disable root login, `ufw` allowing only 22/80/443, unattended upgrades. **Acceptance:** `ssh root@...` and password login both fail; `ufw status` shows exactly 3 ports; a checklist in `notes.md` of every step and why.
- [ ] **Ex B23.2 — systemd service.** Run a small FastAPI app as a `systemd` unit with `Restart=on-failure`. **Acceptance:** `kill -9` the process → it restarts automatically; you can find the crash in `journalctl -u <unit>`.
- [ ] **Ex B23.3 — Failing security gates.** Add `pip-audit`, `gitleaks` and Trivy to a CI workflow. **Acceptance:** three deliberately broken branches — one pins a package version with a known CVE, one commits a fake AWS key, one uses an old vulnerable base image — each fails CI at the right step; `main` stays green.
- [ ] **Ex B23.4 — Staging → prod promotion.** Workflow: push to `main` builds an image tagged with the git SHA, deploys it to *staging* automatically, then waits for manual approval on the *production* environment and deploys the **same SHA**. **Acceptance:** screenshot/notes showing the approval gate; the prod container runs the exact image digest staging ran.
- [ ] **Ex B23.5 — Zero-downtime rollover with an abort path.** Write a deploy script (bash or Python, run over SSH) that: starts the new container next to the old one, polls `/health` with a deadline, switches the Nginx upstream and reloads, stops the old container. **Acceptance:** (1) `hey` running during the deploy shows zero errors; (2) a build whose `/health` always fails makes the script abort with the old version still serving; (3) without graceful shutdown you can reproduce a burst of errors at the "stop old" step — record both numbers.
- [ ] **Ex B23.6 — Expand/contract.** On a table with ≥1M rows, rename a column in three deploys (add new column → backfill in batches + dual-write → switch reads → drop old). Every migration starts with `SET lock_timeout`; add one index with `CREATE INDEX CONCURRENTLY`. **Acceptance:** a load script hitting the API during each migration sees zero errors; a note explains why a single `ALTER TABLE ... RENAME` would break old code during the rollout.

### Must be able to do / explain
- [ ] Set up a fresh Linux server securely and explain each step
- [ ] Explain "build once, promote the same artifact" and why rebuilding per environment is wrong
- [ ] Configure environment-scoped secrets and a manual approval gate
- [ ] Explain what `pip-audit`, `gitleaks` and Trivy each catch, and why they must fail, not warn
- [ ] Describe each step of a zero-downtime deploy, including the abort path
- [ ] Explain graceful shutdown and what happens to in-flight requests without it
- [ ] Ship a schema change with expand/contract and explain why it takes several deploys
- [ ] Explain `lock_timeout` and `CREATE INDEX CONCURRENTLY`
- [ ] Choose and justify an API versioning strategy; use `Deprecation`/`Sunset` headers

**Estimated hours:** ~15h

### Self-check interview questions
1. Why should the image deployed to prod be the exact image tested on staging?
2. How do you give CI access to a server without giving it root?
3. What does each of `pip-audit`, `gitleaks` and Trivy catch?
4. Walk me through a zero-downtime deploy. What happens if the new version is broken?
5. What is graceful shutdown and what breaks without it?
6. How do you rename a column on a busy table without downtime?
7. Why set `lock_timeout` at the start of a migration?
8. Why can't `CREATE INDEX CONCURRENTLY` run inside a transaction, and how do you run it from Alembic?
9. URL versioning or header versioning — which would you pick for a public API and why?
10. What is the difference between `Deprecation` and `Sunset` headers?

---

**Answers**
1. Otherwise what you tested is not what you run: a rebuild can pull different dependency versions or base layers. Tag by git SHA and promote the same digest.
2. A dedicated deploy user with a restricted SSH key (only allowed to run the deploy command or member of the `docker` group, knowing that is root-equivalent), stored as an environment secret; never the root key.
3. `pip-audit`: known vulnerabilities in Python dependencies. `gitleaks`: secrets committed to the repo/history. Trivy: vulnerabilities (and misconfigurations) in the container image's OS packages and libraries.
4. Build & scan → push → on the server pull the new image → start it next to the old one → wait for health checks → switch the proxy upstream → stop the old one gracefully. If health never passes within the deadline, abort: the old version keeps serving, nothing was switched.
5. On SIGTERM the process stops accepting new connections and finishes in-flight requests before exiting. Without it, stopping the old container drops requests that were in progress (connection resets / 502s).
6. Expand/contract: add the new column (nullable, instant), dual-write and backfill in batches, switch reads to the new column, then in a later deploy drop the old one. At every point both the old and new code versions work.
7. DDL often needs an `ACCESS EXCLUSIVE` lock; while it waits, every query behind it queues too. `lock_timeout` makes the migration fail fast (and retry later) instead of freezing the table.
8. It performs multiple transactions internally (waits for existing transactions, scans twice). In Alembic you run it in an autocommit block / outside the migration transaction.
9. For a public API, URL versioning (`/v1`) is the most visible, cache-friendly and easy for clients; header versioning is cleaner but less discoverable. Additive-only changes avoid versioning entirely when possible.
10. `Deprecation` says "this endpoint is deprecated (since date X)"; `Sunset` says "it will stop working at date Y". Together they give clients a warning and a deadline.

---

## Module B24 — Logging & Monitoring (~15h)

**Why this module:** once you have several services, workers and a deploy
pipeline, "it works on my machine" becomes "why is prod slow at 3am?". This
module teaches the three pillars — **logs, metrics, traces** — plus error
tracking and alerting, so you can answer that question in minutes.

**Required knowledge:** B3 Docker Compose, B4 FastAPI, B10/B11 Django/DRF, B13 Celery, 1A.9 logging.

**Topics:**
- **Structured logging** with `structlog` (and JSON logs from Django): fields vs messages, log levels, never logging secrets/PII
- **Correlation**: `X-Request-ID` generated at the edge (Nginx) and propagated; `trace_id` in every log line
- **Prometheus**: pull model, `/metrics`, scrape config, the four metric types (counter, gauge, histogram, summary), naming conventions, labels and **cardinality** (why no `user_id` label)
- **RED** (rate, errors, duration) for services, **USE** (utilization, saturation, errors) for resources; the four golden signals
- Histograms: buckets, `histogram_quantile`, why summaries can't be aggregated across replicas
- Exporters: `postgres_exporter`, `redis_exporter`, RabbitMQ Prometheus plugin, cAdvisor/node_exporter (overview)
- **Grafana**: data sources, dashboards, variables, the "3am dashboard"
- **Alertmanager**: alerting rules with `for:`, routing, grouping, silences, a (mock) Slack receiver; symptom-based alerts
- **Loki** + Promtail / Grafana Alloy: shipping container logs, labels vs log content, LogQL basics
- **OpenTelemetry**: spans, traces, context propagation (`traceparent`), auto-instrumentation for FastAPI/Django/httpx/SQLAlchemy/psycopg/Celery; exporting to **Tempo** or **Jaeger**
- **Sentry**: error tracking, releases, environments, breadcrumbs, performance sampling
- **Health checks**: liveness vs readiness; checking real dependencies without making `/health` itself a DoS vector

### Lessons
- [ ] **B24.1 Why monitor, and what** — Google SRE Book, chapter 6 "Monitoring Distributed Systems" (sre.google/sre-book/monitoring-distributed-systems) — the four golden signals, symptoms vs causes; Tom Wilkie "The RED Method" (grafana.com/blog); Brendan Gregg "The USE Method" (brendangregg.com/usemethod.html).
- [ ] **B24.2 Structured logs and correlation** — `structlog` docs: "Getting Started", "Context Variables", "Standard Library Logging"; Django docs "Logging"; W3C Trace Context spec, section "traceparent header" (w3.org/TR/trace-context).
- [ ] **B24.3 Prometheus** — Prometheus docs: "Overview", "Getting started", "Metric types", "Histograms and summaries", "Metric and label naming", "Instrumentation" (best practices), "Querying basics" (PromQL); `prometheus_client` Python README.
- [ ] **B24.4 Grafana and Alertmanager** — Grafana docs "Get started with Grafana and Prometheus", "Dashboards → Variables"; Prometheus docs "Alerting rules", "Alertmanager" (routing, grouping, inhibition, silences); Rob Ewaschuk "My Philosophy on Alerting" (linked from the SRE book).
- [ ] **B24.5 Logs aggregation** — Grafana Loki docs "Get started", "LogQL: Log query language", "Label best practices"; Grafana Alloy docs (or Promtail docs) "Collect Docker container logs".
- [ ] **B24.6 Distributed tracing** — OpenTelemetry docs: "Observability primer", "Concepts → Signals → Traces", "Context propagation", "Language APIs & SDKs → Python → Getting Started" and "Automatic instrumentation"; Grafana Tempo "Get started" (or Jaeger "Getting Started").
- [ ] **B24.7 Error tracking** — Sentry Python docs: "Platforms → Python" (FastAPI and Django integrations), "Releases", "Environments", "Sampling".
- [ ] **B24.8 Health checks** — Kubernetes docs "Configure Liveness, Readiness and Startup Probes" (read for the concepts now; you'll use it in B30); Microsoft Azure Architecture "Health Endpoint Monitoring pattern".

### Exercises
- [ ] **Ex B24.1 — Structured logs with request IDs.** Add `structlog` JSON logging to a FastAPI app and a Django app. A middleware reads `X-Request-ID` (or generates one), binds it to the log context and returns it in the response. **Acceptance:** one request produces log lines in both apps (FastAPI calls Django) with the same `request_id`; no log line contains a password or token (add a test that checks it).
- [ ] **Ex B24.2 — RED metrics.** Expose `/metrics` with a request counter (labels: method, route template, status class) and a latency histogram with buckets you chose deliberately. **Acceptance:** Prometheus scrapes it; you can write PromQL for request rate, error ratio, and p95 latency per route; a note explains why the label is the *route template* (`/items/{id}`) and not the raw path.
- [ ] **Ex B24.3 — Dashboard + alert.** Build a Grafana dashboard (RED per service + one DB exporter panel) and two Alertmanager rules: `5xx ratio > 1% for 5m` and `p95 > 800ms for 10m`, routed to a mock webhook receiver (a tiny FastAPI app that logs what it receives). **Acceptance:** you make the app return errors on purpose and the alert *fires* and later *resolves*; the dashboard JSON is committed to the repo.
- [ ] **Ex B24.4 — Loki.** Ship all container logs to Loki with Alloy or Promtail. **Acceptance:** in Grafana Explore, one LogQL query finds every line for a given `request_id` across all services.
- [ ] **Ex B24.5 — One trace across two services.** Add OpenTelemetry to both apps (HTTP server, `httpx` client, SQLAlchemy/psycopg instrumentation) exporting to Tempo or Jaeger. **Acceptance:** one request shows a single waterfall: service A → HTTP call → service B → SQL query; the same `trace_id` appears in the logs of both services.
- [ ] **Ex B24.6 — Sentry + health checks.** Add Sentry to both apps with `release` = git SHA and an environment name. Add `/health/live` (process is up) and `/health/ready` (DB and Redis reachable, with short timeouts). **Acceptance:** a deliberate exception appears in Sentry with the request context and release; stopping Postgres makes *ready* fail while *live* stays OK.

### Must be able to do / explain
- [ ] Explain what logs, metrics and traces each answer that the others cannot
- [ ] Produce structured JSON logs with a request ID propagated across services
- [ ] Choose the right Prometheus metric type and explain histogram buckets
- [ ] Explain label cardinality and why `user_id` must never be a label
- [ ] Write PromQL for rate, error ratio and p95
- [ ] Write an alert rule with a justified threshold and `for:` window; explain symptom vs cause alerts
- [ ] Query logs by `request_id` in Loki
- [ ] Explain trace context propagation (`traceparent`) over HTTP and (later) message headers
- [ ] Explain liveness vs readiness

**Estimated hours:** ~15h

### Self-check interview questions
1. Metrics, logs, traces — what question does each answer best?
2. What are the four Prometheus metric types? When would you use a histogram?
3. Why can't you aggregate p95 from summaries across replicas?
4. What is label cardinality and why does it matter?
5. What is the RED method? The USE method?
6. What makes a good alert? Why alert on symptoms rather than causes?
7. How does a trace ID get from one service to another?
8. What does Sentry give you that logs don't?
9. What is the difference between a liveness and a readiness check?
10. Why should `/health/ready` checks use short timeouts?

---

**Answers**
1. Metrics: *is* something wrong, how much, trends (cheap, aggregated). Logs: *what exactly happened* in one event. Traces: *where* the time went across services for one request.
2. Counter (only goes up: requests, errors), gauge (goes up and down: queue depth, memory), histogram (distribution in buckets: latency, sizes — aggregatable, quantiles computed on the server), summary (client-side quantiles). Use histograms for latency.
3. A summary computes quantiles inside each process; quantiles are not additive, so averaging p95s of replicas is mathematically wrong. Histograms export bucket counts, which *can* be summed, then `histogram_quantile` is applied.
4. The number of unique label-value combinations = number of time series. High-cardinality labels (user IDs, raw URLs) explode memory and slow Prometheus down.
5. RED: Rate, Errors, Duration — per service/endpoint. USE: Utilization, Saturation, Errors — per resource (CPU, disk, pool).
6. Actionable, rare, tied to user impact, with a threshold and duration that avoid flapping. Symptom alerts (errors, latency) catch any cause, including ones you didn't predict; cause alerts are noisy and incomplete.
7. Via the W3C `traceparent` header (trace ID + parent span ID + flags), injected by the client instrumentation and extracted by the server instrumentation.
8. Grouping of identical errors, stack traces with local variables and request context, release/regression tracking and notifications — much faster than searching logs.
9. Liveness: "is the process alive / should it be restarted?". Readiness: "can it serve traffic right now (dependencies OK)?". A failed readiness removes it from load balancing; a failed liveness restarts it.
10. Otherwise a slow dependency makes the health check itself hang, piling up health requests and giving a false picture; the check must answer quickly.

---

## Project P6 — LedgerBase · Middle (~65h)

**Double-entry accounting & invoicing platform (FinTech).**

### Goal
A freelancer or small agency issues invoices, records payments, and sees a
real ledger where every transaction is a balanced debit/credit pair — and an
accountant can trace **every number to a specific journal entry**. Three
things make this project:
1. **Money as integer cents** — learned by building the float version first, *on purpose*, and watching the trial balance fail to reconcile.
2. The **first real synchronous service-to-service write** (invoicing → ledger), which therefore needs resilience patterns.
3. The deployment and observability work that four services finally justify — **HTTPS**, **zero-downtime deploys and migrations**, and **metrics + logs + traces** together.

It is also where Postgres stops being "a place to put rows": a **deferrable
constraint trigger** enforces the rule a `CHECK` cannot, a **window function**
produces the running balance, and a **materialized view** serves the trial balance.

### Roles
| Role | Can | Cannot |
|---|---|---|
| `bookkeeper` | Create invoices, record payments, view invoices and the ledger | Post manual journal entries; change the chart of accounts |
| `accountant` | Bookkeeper + manual journal entries + trial balance | Delete a posted entry — nobody can; corrections are reversing entries |
| `admin` | Manage chart of accounts and users | Bypass the balance rule — the DB refuses regardless of role |
| `service` (machine) | invoicing-service calling ledger-service | Anything beyond posting entries (scoped machine credential) |

Auth reuses **CarePoint's `auth-service`** (P5) with zero duplicated auth code.

### Features
- [ ] Chart of accounts typed asset / liability / equity / revenue / expense; the debit/credit direction per type encoded in one place
- [ ] Journal entries with ≥2 lines; each line is debit **or** credit, never both
- [ ] **Float version first**, a trial balance that does not reconcile, then conversion to integer cents + regression test
- [ ] Balance enforced in the service layer **and** in the DB by a `DEFERRABLE INITIALLY DEFERRED` constraint trigger; `CHECK` for one-sided lines
- [ ] Append-only ledger: triggers refuse `UPDATE`/`DELETE` on posted lines and entries; corrections by reversing entries
- [ ] `GET /accounts/{id}/ledger` with a **running balance** (window function), keyset paginated
- [ ] `GET /accounts/{id}/balance` — deliberately **not cached**
- [ ] `GET /reports/trial-balance` — live `GROUP BY` and `trial_balance_mv` (`?source=mv`, `REFRESH ... CONCURRENTLY`, `as_of` in the response), timed at 1M lines
- [ ] `GET /journal-lines/export.csv` — **streaming** export of 1M lines with a server-side cursor, flat memory
- [ ] Invoices and payments (invoicing-service, Django/DRF); each payment posts a journal entry through ledger-service
- [ ] invoicing → ledger call with **timeouts + retry with backoff + hand-rolled circuit breaker**; clean `503` when ledger is down
- [ ] Overdue-invoice reminders on Celery Beat
- [ ] Four services behind one Nginx gateway (auth, clinic from CarePoint, invoicing, ledger), **HTTPS** with Let's Encrypt, HTTP→HTTPS redirect, HSTS
- [ ] CI/CD: build → security gates → push to GHCR → **staging** → manual approval → **prod**, zero-downtime rollover, tested abort path, graceful shutdown
- [ ] Expand/contract rename `journal_entries.description → memo` across three deploys under load
- [ ] `/v1` → `/v2` journal-entries API with `Deprecation`/`Sunset` headers on `/v1`
- [ ] Observability: RED metrics on all services, Grafana dashboards, Alertmanager rules, Loki logs by `request_id`, one OpenTelemetry trace Nginx → invoicing → ledger → Postgres, Sentry everywhere

### Domain model
```
accounts(id, name, type[asset|liability|equity|revenue|expense])
journal_entries(id, description→memo, created_at)
journal_lines(id, journal_entry_id, account_id, debit_cents, credit_cents)
    -- CHECK: exactly one of debit/credit non-zero; both >= 0
    -- CONSTRAINT TRIGGER (DEFERRABLE INITIALLY DEFERRED): SUM(debit) = SUM(credit) per entry at commit
    -- TRIGGER BEFORE UPDATE OR DELETE → refuse (append-only)
invoices(id, client_name, total_cents, status, issued_at, due_at)
payments(id, invoice_id, amount_cents, journal_entry_id, received_at)
trial_balance_mv   -- materialized view, unique index on account_id
```

### Tech stack
| Tool | Used for | Taught in |
|---|---|---|
| FastAPI | ledger-service | B4 |
| Django + DRF | invoicing-service | B10, B11 |
| SQLAlchemy 2.0 + Alembic | ledger models, migrations (incl. autocommit block for `CONCURRENTLY`) | B5, B23 |
| PostgreSQL: CHECK, PL/pgSQL constraint triggers, window functions, matviews, server-side cursors | Invariants, running balance, trial balance, streaming | 1C 1.6, 2.2, 2.9, 2.11; B5 |
| `httpx` + timeouts, hand-rolled circuit breaker, `tenacity` | invoicing → ledger resilience | B22 |
| Redis + Celery Beat | Overdue reminders | B12, B13 |
| CarePoint `auth-service` (RS256/JWKS) | Auth for all services | B18, P5 |
| Nginx + certbot (TLS, HSTS) | Gateway, HTTPS | B17 |
| Docker multi-stage images, Compose | Packaging, local and server stack | B3, B23 |
| GitHub Actions, GHCR, environments, approvals | CI/CD staging → prod | B9, B23 |
| `pip-audit`, `gitleaks`, Trivy | Failing security gates | B23 |
| VPS (SSH, ufw, systemd) | Staging and prod hosts | B2, B23 |
| `structlog`, Prometheus, Grafana, Alertmanager, Loki + Alloy/Promtail, OpenTelemetry + Tempo/Jaeger, Sentry | Observability | B24 |
| pytest, factory_boy, `hey` | Tests, load during deploys | B8 |

### Required knowledge
- Track 2: B1–B24 (especially B22 Resilience, B23 CI/CD II, B24 Monitoring); **P5 CarePoint** (its auth-service and Nginx gateway are reused)
- Track 1: 1C 1.6 constraints, 2.2 window functions, 2.5 indexes, 2.8 locking, 2.9 materialized views, 2.11 PL/pgSQL triggers; 1A.8 pytest, 1A.4 generators (streaming export)

### Milestones
- [ ] **M1 — The float mistake, on purpose.** Repo `ledgerbase/`; `Account`, `JournalEntry`, `JournalLine` with **float** money; a trial balance that fails to reconcile; convert everything to integer cents; regression test that would have caught it; `CHECK` constraints + app-level balance validation; deferrable constraint trigger + append-only triggers, both proven from `psql`; `docs/triggers-notes.md` (when triggers are right, when they are a trap); running-balance ledger endpoint with window function and keyset pagination. *Tag:* `v0.1-ledger-core`
- [ ] **M2 — Invoicing & resilience.** `Invoice`, `Payment` in invoicing-service; payment → ledger call behind timeouts, retry with backoff + jitter and a hand-rolled circuit breaker; trial balance live vs `trial_balance_mv`, timed at 1M lines; streaming CSV export with measured memory (RSS with and without streaming); Nginx routing for both services; kill ledger-service mid-call → clean `503`, not a hang; overdue reminders on Beat. *Tag:* `v0.2-invoicing`
- [ ] **M3 — Full CI/CD & zero-downtime.** Multi-stage non-root Dockerfiles for all four services; CI builds/pushes all images; failing `pip-audit`/`gitleaks`/Trivy gates proven with planted problems; TLS with certbot, redirect + HSTS; staging stack + manual approval to prod with the same image SHA; health-gated rollover with Nginx upstream switch; graceful shutdown everywhere, rollover under `hey` with zero errors; broken health check → deploy aborts, old version stays live; expand/contract `description → memo` in three deploys with `lock_timeout` and `CREATE INDEX CONCURRENTLY`; `/v2/journal-entries` + `Deprecation`/`Sunset` on `/v1`; `docs/api-versioning.md`. *Tag:* `v0.3-delivery`
- [ ] **M4 — Observability.** `/metrics` (RED, histograms, no high-cardinality labels) on all services + Postgres exporter; Alertmanager rules (`5xx > 1% 5m`, `p95 > 800ms 10m`, `breaker open 2m`, `celery queue depth > N`) → mock Slack, one fired on purpose; Loki search by `request_id` across services; OpenTelemetry in both frameworks with `traceparent` across the sync call and into Celery, `trace_id` in logs, one payment traced end to end; Grafana with RED, queue depth, breaker state and Loki/Tempo data sources; Sentry in all four services; **inject an unbalanced-entry bug past app validation and find it via Sentry before reading the code**; `docs/postmortem.md` + "the moment Compose stopped being manageable" note + read-replica scaling note. *Tag:* `v1.0-ledgerbase`

### Definition of done
- [ ] Money is integer cents everywhere; float regression test in place
- [ ] Double-entry enforced in app and DB, proven by bypassing the app from `psql` (two unbalanced `INSERT`s + `COMMIT` → `check_violation`; `UPDATE` on a posted line refused)
- [ ] Trial balance reconciles; matview equals the live query after refresh; `as_of` exposed
- [ ] Running balance equals a Python fold over the same lines; `EXPLAIN` shows one ordered scan on `(account_id, created_at, id)`
- [ ] 1M-line CSV export with flat memory (measured)
- [ ] Circuit breaker verified against a killed dependency, including half-open recovery
- [ ] Security gates fail the build on a planted CVE, secret and vulnerable base image
- [ ] Staging → prod promotion with approval; zero-downtime deploy **including the abort path**; zero errors under load thanks to graceful shutdown
- [ ] Expand/contract migration shipped in three deploys under load with zero errors
- [ ] HTTPS with auto-renewing certificate and HSTS
- [ ] `/v2` live, `/v1` still served with deprecation headers
- [ ] Alerts fire and resolve; Loki searchable by `request_id`; one end-to-end trace; Sentry live; injected bug found via Sentry first
- [ ] `docs/triggers-notes.md`, `docs/api-versioning.md`, `docs/postmortem.md`, scaling note; CI green; tag `v1.0-ledgerbase`

**Deliberately NOT done (be ready to explain):** no Redis cache on balances (financial data — staleness = wrong answer; contrast with QuickServe's product cache); no broker between invoicing and ledger (it is a synchronous write the caller needs an answer to); no Kubernetes yet (feel the Compose strain first — P8); no distributed circuit breaker (in-process is right at this scale); no idempotency on payment posting (PayFlow, P9, does it properly).

### Estimated hours
~65h (M1 ~15h, M2 ~15h, M3 ~20h, M4 ~15h)

### OPTIONAL extensions
- [ ] **Cash-flow forecast + experiment tracking (~10h).** A simple time-series forecast (`statsmodels` or a lag-feature linear model) of next week's collections from `invoices` + `payments`; at least 3 training runs logged to a **local MLflow** and compared in its UI; no serving endpoint; `docs/mlops-notes.md`. *Requires:* Track 3 ML Zoomcamp modules 1–4 and MLOps Zoomcamp module 2 (experiment tracking).

### Interview questions
1. Why store money as integer cents — show me the concrete float bug you hit.
2. Why can't a `CHECK` constraint enforce "the entry balances", and what does `DEFERRABLE INITIALLY DEFERRED` change?
3. Walk me through your zero-downtime deploy — including what happens when the new version is broken and at the "stop old container" step.
4. Walk me through renaming a column with zero downtime. Why three deploys, and why `lock_timeout`?
5. You cached product search in QuickServe but not account balances here, and you use a materialized view for the trial balance. Why is one kind of staleness acceptable and the other not?

---

**Answers**
1. Floats are binary fractions: 0.1 + 0.2 ≠ 0.3, so summing thousands of amounts drifts by cents and the trial balance stops reconciling. Integer cents (or `Decimal`/`NUMERIC`) make arithmetic exact; I kept a regression test built from the failing case.
2. A `CHECK` sees one row; balance is a property of all lines of an entry, and after inserting the first line the entry is always unbalanced. A deferred constraint trigger runs the check at commit time, when all lines exist, so an unbalanced entry can never become durable.
3. Build/scan/push → pull on the server → start the new container next to the old → poll `/health` with a deadline → switch the Nginx upstream → stop the old one with SIGTERM and a grace period. Broken health → abort, old keeps serving. Without graceful shutdown the stop step drops in-flight requests; with it, zero errors under `hey`.
4. During a rollout old and new code run against the same schema, so each migration must work for both: add `memo` (expand), dual-write + batched backfill, switch reads, then drop `description` (contract). `lock_timeout` stops a DDL waiting for an exclusive lock from blocking all traffic behind it.
5. The matview is rebuilt from the source of truth with an explicit `as_of`, reports are read as "as of time X", and it can't be forgotten by a code path. A Redis balance cache is invalidated by application code that can miss a write, and a stale balance used for a decision is simply a wrong answer. Product search tolerates a few seconds of staleness; money decisions do not.

---

## Module B25 — Event-Driven Patterns (~12h)

**Why this module:** in WareFlow (P4) you saw the gap "the DB commit
succeeded but the broker publish failed". This module teaches the patterns
that close that gap and that shape real event-driven systems: the
**transactional outbox**, **CQRS read models**, **sagas** with compensations,
long-running operations over REST, and evolving event schemas safely.

**Required knowledge:** B14 Architecture patterns, B15 RabbitMQ (+ Pact), B16 Kafka, B13 Celery Beat, 1C 2.4 JSONB, 2.5 partial/GIN indexes, 2.8 `FOR UPDATE SKIP LOCKED`.

**Topics:**
- What "event-driven" can mean: event notification, event-carried state transfer, event sourcing, CQRS (Fowler's four)
- The **dual-write problem** (DB + broker) and why "publish after commit" still loses events
- **Transactional outbox**: outbox row in the *same* transaction as the state change; relay process poll → publish → mark sent; claiming rows with `FOR UPDATE SKIP LOCKED`; partial index `WHERE sent_at IS NULL`; at-least-once delivery
- **CDC / Debezium** as the log-tailing alternative to polling (concept only): what it buys and costs
- **Idempotent consumers and projections**: dedup by event ID, version checks, upserts
- **CQRS**: separate write model and read models; eventual consistency and the staleness trade-off; rebuilding a projection from events
- **Sagas**: why no distributed transaction (2PC) across services; choreography vs orchestration; compensating actions; failure of a compensation
- **Long-running operations over REST**: `202 Accepted` + `Location` to a status resource; polling the status
- **Event versioning**: additive changes, new event types, upcasters (v1 → v2), consumer-driven contracts (Pact) for message schemas
- **Outbox housekeeping**: cleanup/archiving of sent rows in batches; monitoring outbox lag
- Event sourcing (overview only): state as a fold over events; when it's worth it

### Lessons
- [ ] **B25.1 Meanings of event-driven** — Martin Fowler, "What do you mean by 'Event-Driven'?" (martinfowler.com/articles/201701-event-driven.html) (+ the GOTO 2017 talk "The Many Meanings of Event-Driven Architecture").
- [ ] **B25.2 Outbox and CDC** — microservices.io patterns: "Transactional outbox", "Polling publisher", "Transaction log tailing", "Idempotent Consumer" (microservices.io/patterns/data/transactional-outbox.html); Debezium docs "Outbox Event Router" (read for the concept); PostgreSQL docs `SELECT` → "The Locking Clause" (`SKIP LOCKED`).
- [ ] **B25.3 CQRS** — Martin Fowler, "CQRS" (martinfowler.com/bliki/CQRS.html); microservices.io "Command Query Responsibility Segregation (CQRS)"; *Building Microservices* 2nd ed. (Newman), chapter 6 "Workflow" (sagas) and the data-decomposition discussion in chapter 3 "Splitting the Monolith".
- [ ] **B25.4 Sagas** — microservices.io "Saga" (microservices.io/patterns/data/saga.html); *Building Microservices* 2nd ed., chapter 6 "Workflow" (sections on distributed transactions, sagas, choreographed vs orchestrated); Caitie McCaffrey talk "Distributed Sagas: A Protocol for Coordinating Microservices" (optional).
- [ ] **B25.5 Long-running operations** — Microsoft Azure Architecture Center, "Asynchronous Request-Reply pattern"; MDN "202 Accepted".
- [ ] **B25.6 Event versioning** — Greg Young, *Versioning in an Event Sourced System* (free on Leanpub) — chapters on "Simple Type Based Versioning", "Weak Schema" and upcasting; Pact docs "Message Pact" (recap from B15).
- [ ] **B25.7 Event sourcing (overview)** — Martin Fowler, "Event Sourcing" (martinfowler.com/eaaDev/EventSourcing.html).

### Exercises
- [ ] **Ex B25.1 — Reproduce the dual-write bug.** A tiny service updates an `orders` row, commits, then publishes to RabbitMQ. Kill the broker between the commit and the publish (or raise an exception there). **Acceptance:** the DB shows the new state and no message ever arrives; `notes.md` explains why moving the publish *before* the commit is just a different bug.
- [ ] **Ex B25.2 — Outbox + relay.** Add an `outbox(id, aggregate_type, aggregate_id, event_type, event_version, payload jsonb, created_at, sent_at)` table written in the same transaction as the state change, with a partial index on unsent rows. Write a relay that polls, publishes and marks rows sent. **Acceptance:** (1) a forced failure after the outbox insert leaves neither the state change nor the outbox row; (2) killing RabbitMQ mid-relay loses no event — it's published after the broker returns; (3) two relay processes never publish the same row (claim with `FOR UPDATE SKIP LOCKED`), proven by a test counting deliveries.
- [ ] **Ex B25.3 — Idempotent projection.** Build a consumer that maintains a denormalized read table from the events. **Acceptance:** replaying the whole event stream twice yields the same read table; delivering the same event twice changes nothing; you can drop the read table and rebuild it from events.
- [ ] **Ex B25.4 — Saga on paper, then in code.** Design a 3-step choreographed saga (e.g. reserve → charge → confirm, with compensations) in `saga.md` *before* coding: events, compensations, what happens if a compensation fails. Then implement it with RabbitMQ. **Acceptance:** happy path works; a failure injected in step 3 triggers compensations of steps 2 and 1; the API returns `202 Accepted` + `Location: /sagas/{id}` and the status resource moves `pending → compensating → failed`.
- [ ] **Ex B25.5 — Event v1 → v2 with an upcaster.** Change the event shape (add one field, rename one). Consumers accept both versions via an upcaster. **Acceptance:** a v1 message published by the "old" publisher is processed correctly by the new consumer; a Pact message contract fails CI if v2 removes a field a v1 consumer needs.
- [ ] **Ex B25.6 — Outbox cleanup & lag.** A scheduled job deletes (or archives) sent outbox rows older than N days in batches; expose `outbox_lag_seconds = now() - oldest unsent created_at` as a Prometheus gauge. **Acceptance:** unsent rows are never deleted; stopping the relay makes the gauge grow.

### Must be able to do / explain
- [ ] Explain the dual-write problem and why publish-after-commit loses events
- [ ] Implement a transactional outbox and a relay that is safe with multiple replicas
- [ ] Explain what the outbox guarantees (eventual, at-least-once) and what it doesn't (exactly-once, immediacy)
- [ ] Explain what CDC/Debezium changes versus a polling relay
- [ ] Build idempotent consumers and rebuildable projections
- [ ] Explain when CQRS is worth it and the staleness trade-off
- [ ] Design a saga with compensations; compare choreography and orchestration
- [ ] Use `202 Accepted` + a status resource for long-running operations
- [ ] Evolve an event schema without breaking consumers that haven't deployed yet

**Estimated hours:** ~12h

### Self-check interview questions
1. What is the dual-write problem?
2. How does the transactional outbox guarantee that a committed change is eventually published?
3. What does the outbox not guarantee?
4. How do you run two relay instances without double-publishing?
5. What would CDC (Debezium) change about the relay?
6. When is CQRS worth the complexity? When is it overkill?
7. Choreographed vs orchestrated saga — trade-offs?
8. Why not use a distributed transaction (2PC) across services?
9. Why return `202 Accepted` for a long-running operation?
10. How do you change an event's schema safely?

---

**Answers**
1. Writing to two systems (DB and broker) without a shared transaction: one can succeed and the other fail, leaving them inconsistent (state changed, event lost — or event sent, state rolled back).
2. The event is written as a row in the same DB transaction as the state change, so both commit or neither does. A relay publishes committed outbox rows and retries until the broker accepts them, then marks them sent.
3. Exactly-once delivery and immediacy: the relay may publish a row twice (crash after publish, before marking) and there is lag. Consumers must be idempotent and dashboards must tolerate staleness.
4. Each relay claims a batch with `SELECT ... FOR UPDATE SKIP LOCKED`, so rows locked by one relay are skipped by the other; mark them sent in the same transaction.
5. Instead of polling the table, Debezium reads the database's write-ahead log and publishes changes: lower latency and no polling load, but it needs WAL access (replication slot), Kafka Connect infrastructure and more operational care.
6. Worth it when read and write shapes differ a lot, reads dominate, or several read views are needed (dashboards, search). Overkill for simple CRUD where one model serves both — you pay with eventual consistency and extra moving parts.
7. Choreography: no coordinator, services react to each other's events — simple for few steps, but the flow is implicit and hard to observe. Orchestration: a coordinator tells each service what to do — explicit state, easier monitoring and error handling, but one more component and coupling to it.
8. 2PC needs all participants to support it, holds locks across services while waiting, and a coordinator failure can block everyone; it hurts availability. Sagas trade atomicity for availability with compensations.
9. Because the work isn't finished; `200` would lie. `202` + `Location` tells the client where to poll for the result.
10. Prefer additive changes; when breaking, publish a new version, keep consumers able to read both (upcaster), deploy consumers first, then publishers, and use contract tests (Pact) to catch breakage in CI.

---

## Module B26 — Real-Time: WebSockets, SSE & Redis Pub/Sub (~8h)

**Why this module:** dashboards and live status pages need updates pushed to
the browser. This module compares the options you'll build (polling, SSE,
WebSocket), and teaches the parts that break in production: authentication,
heartbeats, reconnects, backpressure and **fan-out across multiple replicas**.

**Required knowledge:** B4 FastAPI, B12 Redis, B17 Nginx (upgrade headers), 1A.12 asyncio.

**Topics:**
- Polling vs long-polling vs **Server-Sent Events** vs **WebSocket**: direction, latency, cost, failure modes
- The WebSocket handshake (HTTP `Upgrade`), frames, ping/pong, close codes
- FastAPI/Starlette WebSockets: accept, receive/send loops, handling disconnects
- **Authenticating a WebSocket**: short-lived ticket in the query string or token in the first message; why never the long-lived JWT in the URL
- **Heartbeats** and detecting dead connections; client reconnect with backoff; refetching state after reconnect
- **Backpressure**: a bounded per-client send queue; dropping or disconnecting slow clients so they don't stall the producer
- **SSE**: `text/event-stream`, `EventSource`, `id:` and `Last-Event-ID` resume, auto-reconnect; SSE limitations (server → client only, no custom headers in `EventSource`)
- **Scaling push**: stateful connections + multiple replicas → **Redis pub/sub** fan-out; sticky sessions vs pub/sub; Redis pub/sub is fire-and-forget (no persistence)
- Nginx for WebSockets/SSE: `proxy_http_version 1.1`, `Upgrade`/`Connection` headers, `proxy_read_timeout`, `proxy_buffering off` for SSE
- Python client for testing: the `websockets` library, `httpx` streaming for SSE

### Lessons
- [ ] **B26.1 The options** — MDN "The WebSocket API (WebSockets)" and "Writing WebSocket servers" (handshake section); MDN "Using server-sent events"; *High Performance Browser Networking* (Grigorik, hpbn.co), chapters "WebSocket" and "Server-Sent Events (SSE)".
- [ ] **B26.2 WebSockets in FastAPI** — FastAPI docs "Advanced User Guide → WebSockets" (incl. "Handling disconnections and multiple clients"); Starlette docs "WebSockets".
- [ ] **B26.3 Auth, heartbeats, backpressure** — Heroku Dev Center "WebSocket Security" (auth ticket pattern); `websockets` library docs "Keepalive and latency" and "Broadcasting" (backpressure discussion).
- [ ] **B26.4 SSE server side** — WHATWG HTML Living Standard, "Server-sent events" section (event stream format, `Last-Event-ID`); `sse-starlette` README (or FastAPI `StreamingResponse` with `text/event-stream`).
- [ ] **B26.5 Fan-out with Redis pub/sub** — Redis docs "Redis Pub/Sub" (delivery semantics: at-most-once); redis-py docs "Pub/Sub" (asyncio usage).
- [ ] **B26.6 Proxying** — Nginx blog/docs "WebSocket proxying" (nginx.org/en/docs/http/websocket.html); Nginx `proxy_buffering` / `proxy_read_timeout` directives.

### Exercises
- [ ] **Ex B26.1 — Three transports, one feed.** A FastAPI app emits a counter/event every second. Expose it as (a) a polling endpoint, (b) SSE, (c) WebSocket. Write a Python client for each (`httpx` for polling/SSE, `websockets` for WS). **Acceptance:** all three clients print the same events; a table in `notes.md` compares latency, requests per minute and behaviour when the server restarts.
- [ ] **Ex B26.2 — Ticket auth.** Add `POST /ws-ticket` (requires a normal JWT) that returns a single-use ticket valid for 30s, stored in Redis. The WebSocket accepts only a valid ticket. **Acceptance:** tests prove: no ticket → rejected; expired or reused ticket → rejected; valid ticket → connected; the JWT never appears in a URL.
- [ ] **Ex B26.3 — Heartbeat + reconnect.** Server pings every 20s and closes connections that miss 2 pongs; the client reconnects with exponential backoff and refetches current state on reconnect. **Acceptance:** killing the server for 10s and bringing it back → the client reconnects on its own and no update is missing after the refetch.
- [ ] **Ex B26.4 — Backpressure.** Give each connection a bounded `asyncio.Queue`; a deliberately slow client (reads once every 5s) must be disconnected (or have messages dropped, your choice — document it) without slowing other clients. **Acceptance:** with one slow and one fast client, the fast one still receives every event on time.
- [ ] **Ex B26.5 — Fan-out across two replicas.** Run two API replicas behind Nginx (with correct upgrade config). Events are published to a Redis channel; each replica forwards to its own sockets. **Acceptance:** an event produced by replica A reaches a client connected to replica B; `notes.md` lists what Nginx needed and compares sticky sessions vs pub/sub.
- [ ] **Ex B26.6 — SSE resume.** Give every SSE event an `id:`. On reconnect with `Last-Event-ID`, the server replays the missed events (keep the last N in a Redis list/stream). **Acceptance:** disconnect the client for a few events, reconnect → it receives exactly the missed events, no duplicates.

### Must be able to do / explain
- [ ] Compare polling, long-polling, SSE and WebSocket and pick one for a given feature
- [ ] Explain the WebSocket upgrade handshake
- [ ] Authenticate a WebSocket safely and explain why the JWT must not go in the URL
- [ ] Implement heartbeats, reconnect with backoff and state refetch
- [ ] Explain and implement backpressure for slow clients
- [ ] Fan out events to clients across replicas with Redis pub/sub
- [ ] Configure Nginx for WebSockets and SSE
- [ ] Explain `Last-Event-ID` resume for SSE

**Estimated hours:** ~8h

### Self-check interview questions
1. Polling, SSE or WebSocket for a dashboard that only receives updates — which and why?
2. How does a WebSocket connection start?
3. How do you authenticate a WebSocket, and why not put the JWT in the URL?
4. Why do you need heartbeats?
5. What is backpressure on a WebSocket, and what happens without handling it?
6. You have two API replicas. How does an event reach a client connected to the other one?
7. What delivery guarantee does Redis pub/sub give?
8. What does Nginx need to proxy WebSockets?
9. How does SSE resume after a disconnect?

---

**Answers**
1. Usually SSE: server → client only, plain HTTP, auto-reconnect and resume built in. WebSocket if you need client → server messages too; polling if updates are rare and simplicity matters most.
2. With an HTTP/1.1 `GET` carrying `Upgrade: websocket` and `Connection: Upgrade` (+ a key); the server replies `101 Switching Protocols` and the TCP connection then carries WebSocket frames.
3. With a short-lived, single-use ticket obtained via a normal authenticated request, or by sending the token in the first message. URLs end up in proxy and server access logs, browser history and referrers, so a long-lived token there leaks.
4. A dead TCP connection (NAT timeout, laptop sleep) can look alive for a long time; periodic ping/pong detects it so both sides can clean up and the client can reconnect.
5. The producer sends faster than a client reads; without a bound, messages pile up in memory or the producer blocks on the slow socket and stalls everyone. Use a bounded queue per client and drop or disconnect slow clients.
6. The replica that produces (or consumes) the event publishes it to a Redis channel; every replica subscribes and forwards it to its own connected clients.
7. At-most-once, fire-and-forget: subscribers that are disconnected at publish time miss the message; nothing is stored. For resumable history use Redis Streams or a DB.
8. `proxy_http_version 1.1`, passing `Upgrade` and `Connection "upgrade"` headers, and a long `proxy_read_timeout` so idle connections aren't cut.
9. Each event has an `id:`; the browser's `EventSource` reconnects automatically and sends `Last-Event-ID`; the server replays events after that ID.

---

## Project P7 — FleetTrack · Middle+ (~45h)

**Fleet & delivery logistics platform — event-driven: Outbox + CQRS + Saga.**

### Goal
A delivery company needs near-real-time tracking of deliveries through
several steps (assigned → picked up → in transit → delivered), **reliable
event publishing** to a downstream billing/analytics feed, and a dispatcher
view that never shows stale-forever or duplicated events even when the broker
retries. The stake: a lost `DeliveryStatusChanged` event silently breaks
billing — not a crash, but a wrong invoice weeks later that nobody can explain.

This project **closes the gap you deliberately left open in WareFlow (P4)**:
"the DB commit succeeded but the broker publish failed". Treat the outbox as
the answer to a bug you already watched happen. Its difficulty is **design,
not infrastructure** — no new services beyond what you already run.

### Roles
| Role | Can | Cannot |
|---|---|---|
| `driver` | See own deliveries; advance own delivery (picked up → in transit → delivered) | See others' deliveries; assign; cancel |
| `dispatcher` | Dashboard; create, assign/reassign; cancel (starts the saga) | Edit event history |
| `ops_manager` | Dispatcher + outbox/queue health views, replay a stuck event | Alter `delivery_events` (append-only) |
| `billing` (machine) | Consume `DeliveryStatusChanged` from the broker | Call the API |

### Features
- [ ] Deliveries moving through a validated state machine: `created → assigned → picked_up → in_transit → delivered`, plus `cancelled` from any pre-delivery state; illegal transitions refused
- [ ] Append-only `delivery_events`; current status = latest event
- [ ] **Transactional outbox**: every status change writes the state change and an outbox row in **one transaction**
- [ ] **Relay worker**: poll → publish to RabbitMQ → mark sent; claims rows with `FOR UPDATE SKIP LOCKED` (safe with 2 replicas); partial index `WHERE sent_at IS NULL`
- [ ] **CQRS read model** `delivery_view`, maintained idempotently by a consumer; `GET /dispatch/dashboard` reads **only** the read model
- [ ] **Choreographed 3-step cancellation saga** (reverse driver assignment → notify customer → credit back fee), designed on paper first; `POST /deliveries/{id}/cancel` → `202 Accepted` + `Location: /sagas/{id}`
- [ ] **WebSocket** dashboard push (`/ws/dispatch`): ticket auth, heartbeat, reconnect, bounded send queue, **Redis pub/sub fan-out across two API replicas** behind Nginx
- [ ] **SSE** variant (`/sse/dispatch`) with `Last-Event-ID` resume; the polling/SSE/WebSocket comparison written from having built all three
- [ ] `outbox.payload` as **JSONB** with a GIN index; `GET /ops/outbox?driver_id=` uses it
- [ ] **Outbox-lag** metric + Grafana panel + Alertmanager rule (`outbox_lag_seconds > 30 for 2m`), with a derived, justified threshold
- [ ] **Trace through the broker**: `traceparent` stored in `outbox.trace_context`, put in AMQP headers by the relay, continued by the consumer
- [ ] **Event schema v1 → v2** with an upcaster; Pact contract on `DeliveryStatusChanged` covering both
- [ ] Outbox **cleanup** job (sent rows older than 7 days, in batches)

### Domain model
```
drivers(id, name, status)
deliveries(id, driver_id, status, created_at)
delivery_events(id, delivery_id, from_status, to_status, created_at)      -- append-only
outbox(id, aggregate_type, aggregate_id, event_type, event_version,
       payload jsonb, trace_context jsonb, created_at, sent_at NULL)
    -- partial index WHERE sent_at IS NULL; GIN (payload jsonb_path_ops)
sagas(id, delivery_id, status, step, started_at, finished_at NULL, error NULL)
delivery_view(id, driver_name, status, last_updated)                      -- CQRS read model
```

### API
| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/deliveries` | dispatcher | |
| POST | `/deliveries/{id}/assign` | dispatcher | |
| PATCH | `/deliveries/{id}/status` | driver (own) / dispatcher | State machine; outbox row in the same tx |
| GET | `/dispatch/dashboard` | dispatcher+ | Reads `delivery_view` only |
| POST | `/deliveries/{id}/cancel` | dispatcher | `202` + `Location: /sagas/{id}` |
| GET | `/sagas/{id}` | dispatcher+ | `pending \| compensating \| completed \| failed` |
| WS | `/ws/dispatch` | dispatcher+ | Ticket auth, heartbeat |
| GET | `/sse/dispatch` | dispatcher+ | `Last-Event-ID` resume |
| GET | `/ops/outbox?driver_id=` | ops_manager | JSONB query via GIN |
| GET | `/ops/outbox-lag` | ops_manager | Also a Prometheus gauge |

### Tech stack
| Tool | Used for | Taught in |
|---|---|---|
| FastAPI | API, WebSocket and SSE endpoints | B4, B26 |
| SQLAlchemy 2.0 + Alembic | Models, migrations | B5 |
| PostgreSQL: JSONB + GIN, partial index, `FOR UPDATE SKIP LOCKED` | Outbox, relay claims, ops queries | 1C 2.4, 2.5, 2.8; B25 |
| RabbitMQ | Relay → read-model consumer, saga steps, billing | B15 |
| Pact (message pacts) | `DeliveryStatusChanged` contract, v1/v2 | B15, B25 |
| Redis pub/sub | WebSocket/SSE fan-out (not a cache) | B12, B26 |
| Celery Beat (or a dedicated loop) | Relay polling option, outbox cleanup | B13, B25 |
| Nginx | Two API replicas, WebSocket upgrade config | B17, B26 |
| `websockets` / `httpx` clients | Testing WS/SSE (and a minimal HTML page) | B26 |
| Prometheus, Grafana, Alertmanager | Outbox lag, queue depth, WS connections per replica | B24 |
| OpenTelemetry + Tempo/Jaeger | Trace through outbox and broker | B24, B25 |
| CarePoint `auth-service` (JWT) | Auth + WS tickets | B18, B26 |
| Docker Compose, GitHub Actions | Stack (no new services), CI with Pact | B3, B9 |
| pytest, fault injection | Broker kill, atomicity, concurrency tests | B8, B22 |

### Required knowledge
- Track 2: B1–B26 (especially B15 RabbitMQ, B22 Resilience, B24 Monitoring, B25 Event-driven patterns, B26 Real-time); P4 WareFlow (the outbox gap), P6 LedgerBase (observability stack reused)
- Track 1: 1C 2.4 JSONB, 2.5 partial/GIN indexes, 2.8 locking incl. `SKIP LOCKED`; 1A.12 asyncio

### Milestones
- [ ] **M1 — Outbox.** Repo `fleettrack/`: `Delivery`, `DeliveryEvent`, `outbox`; status-update service writing state change + outbox row in one transaction (proven by a forced failure); relay poll → publish → mark sent with `SKIP LOCKED`; fault injection — kill RabbitMQ mid-relay, zero events lost; two relay replicas never double-publish; JSONB payload + GIN + `GET /ops/outbox?driver_id=` (EXPLAIN shows the index); outbox cleanup job. *Tag:* `v0.1-outbox`
- [ ] **M2 — Observability through the broker.** Outbox-lag gauge on the existing Prometheus/Grafana stack; Alertmanager rule with a threshold derived from relay poll interval + tolerable dashboard staleness — stop the relay, watch it fire, restart, watch it resolve; `traceparent` → `outbox.trace_context` → AMQP headers → consumer; one trace API → relay → consumer → projection in Tempo/Jaeger. *Tag:* `v0.2-observable`
- [ ] **M3 — CQRS read model & saga.** `delivery_view` + idempotent consumer (replay twice = same result); `GET /dispatch/dashboard` reads only the read model; `docs/cqrs-staleness.md` with the WareFlow contrast (stale dashboard OK, stale stock reservation not); `docs/cancellation-saga.md` written **before** the code; 3-step choreographed saga with compensations and one deliberate mid-saga failure; `202 Accepted` + `/sagas/{id}`. *Tag:* `v0.3-cqrs-saga`
- [ ] **M4 — Real-time & event evolution.** WebSocket `/ws/dispatch` with ticket auth, heartbeat, client reconnect + refetch, bounded send queue; two API replicas behind Nginx with Redis pub/sub fan-out (a change consumed by replica A reaches a client on replica B); SSE variant with `Last-Event-ID`; `docs/realtime-comparison.md` (polling vs SSE vs WS, from having built all three); `DeliveryStatusChanged` v2 (adds a field, renames one) with an upcaster, Pact covering both shapes in CI. *Tag:* `v1.0-fleettrack`

### Definition of done
- [ ] Outbox row and state change committed atomically, proven by a forced failure
- [ ] Relay survives a broker kill with zero event loss; safe under two replicas
- [ ] Outbox-lag panel with a justified alert threshold; alert fired and resolved
- [ ] `delivery_view` is the only source for the dashboard; consumer proven idempotent
- [ ] Saga designed on paper first; happy path + compensations + a documented failure mode; `202` + saga status resource
- [ ] WebSocket: auth (expired/reused ticket refused), heartbeat, reconnect without lost updates, slow client disconnected without stalling the consumer, fan-out across two replicas
- [ ] SSE `Last-Event-ID` resume delivers exactly the missed events
- [ ] One trace continues through outbox and broker into the consumer
- [ ] JSONB ops query uses the GIN index
- [ ] v1 → v2 event upcast works; Pact green in CI and fails on a breaking change
- [ ] Cleanup removes old sent rows and never unsent ones
- [ ] Docs: `cqrs-staleness.md`, `cancellation-saga.md`, `realtime-comparison.md`; tag `v1.0-fleettrack`

**Deliberately NOT done (be ready to explain):** no Redis cache (a cache in front of a read model is a copy of a copy); no Kafka (you need a work queue with per-message ack, not a replayable log — say what would change your mind); no Debezium/CDC (named: lower lag, no polling, but WAL access and more ops); no saga orchestrator framework (you build choreography to feel why orchestrators exist); no exactly-once claims.

### Estimated hours
~45h (M1 ~12h, M2 ~8h, M3 ~12h, M4 ~13h)

### OPTIONAL extensions
- [ ] **Dispatcher web UI `fleettrack-web/` (~10h).** React + TypeScript + TanStack Query dispatcher table: polling first, then the WebSocket push with reconnect. *Requires:* B21 (React + TS, OPTIONAL module).
- [ ] **Delivery-duration (ETA) model (~8h).** A `scikit-learn` regression predicting delivery duration from driver, time of day, day of week and number of prior deliveries that day, on synthetic data; compared with a per-driver median baseline; no serving; `docs/eta-notes.md`. *Requires:* Track 3 ML Zoomcamp modules 1–2 (intro, regression) and 4 (evaluation).

### Interview questions
1. Walk me through how the outbox pattern guarantees at-least-once delivery — what failure from WareFlow does it close, and what does it *not* guarantee?
2. Two relay replicas — how do you stop them publishing the same row twice?
3. When is CQRS worth the complexity? Why was staleness acceptable for this dashboard but not for WareFlow's stock reservations?
4. Your dashboard has two API replicas. A driver updates a delivery — how does the update reach a WebSocket connected to the *other* replica, and what happens to a client that reads slowly?
5. Why does `cancel` return `202` and not `200`, and how did you choose between a choreographed and an orchestrated saga?

---

**Answers**
1. The event is inserted into the outbox in the same transaction as the status change, so a committed change always has its event row; the relay keeps retrying until the broker accepts it. This closes WareFlow's commit-then-publish gap. It doesn't guarantee exactly-once (a crash after publish but before marking sent republishes) or zero lag — so consumers are idempotent and lag is monitored.
2. Each relay claims unsent rows with `SELECT ... FOR UPDATE SKIP LOCKED LIMIT n` inside a transaction, publishes them and marks them sent before committing; the other relay skips locked rows. A test counts deliveries per event.
3. When read and write shapes differ and reads dominate — a dashboard joining drivers and statuses. A few seconds of staleness on a dashboard harms nobody; a stale stock number in WareFlow causes an oversell, so reservations must read the write model under locks.
4. The read-model consumer publishes each change to a Redis channel; every replica subscribes and forwards to its own connected sockets. Each socket has a bounded send queue — a slow client is dropped/disconnected so it can't stall the consumer; on reconnect it refetches state.
5. The saga finishes later, so `200` would be a lie; `202 Accepted` + `Location: /sagas/{id}` lets the client poll `pending → completed/failed`. I chose choreography because there are only three steps and I wanted to feel its weakness — no single place to ask "where is this saga?" — which is why larger flows usually use an orchestrator.

## Module B27 — Search: Postgres FTS → Elasticsearch (~12h)

**Topics:** why `LIKE '%term%'` cannot use a B-tree; `pg_trgm` (GIN `gin_trgm_ops`, `similarity()`,
`ILIKE`); `tsvector`/`tsquery` recap (`websearch_to_tsquery`, `ts_rank`, `setweight`, `ts_headline`);
where Postgres FTS stops (no typo tolerance, weak relevance tuning, one dictionary per column);
Elasticsearch/OpenSearch: documents, index, shards/replicas, the **inverted index**, analyzers
(character filters → tokenizer → token filters), mappings (`text` vs `keyword`), `match`, `multi_match`,
`bool` (must/should/filter), **fuzziness**, field **boosting**, filter context vs query context,
aggregations basics, the `_bulk` API, refresh interval; **derived index vs source of truth**; keeping the
index in sync via events; **reindex from source** as a long-running job; **backpressure** on `429`.

**Required before:** 1C 2.10 (FTS basics), 1C 2.5 (GIN), B15 (RabbitMQ), B25 (outbox relay), B3 (Compose).

### Lessons
- [ ] **B27.1 Substring & fuzzy search inside Postgres** — PostgreSQL docs: Appendix F "pg_trgm"
  (sections "Functions and Operators", "Index Support"); recap Chapter 12 "Full Text Search" §12.3
  "Controlling Text Search" (ranking, headline) and §12.9 "Preferred Index Types for Text Search".
- [ ] **B27.2 Inverted index & relevance basics** — Elasticsearch Guide: "What is Elasticsearch?" →
  "Data in: documents and indices" and "Information out: search and analyze"; "Query and filter context".
- [ ] **B27.3 Analyzers & mappings** — Elasticsearch Guide: "Text analysis" → "Anatomy of an analyzer",
  "Test an analyzer" (`_analyze` API); "Mapping" → "Explicit mapping", field types `text` and `keyword`.
- [ ] **B27.4 Queries: match, multi_match, bool, fuzziness, boosting** — Elasticsearch Guide: "Query DSL" →
  "Match query" (the `fuzziness` parameter), "Multi-match query" (field `^boost` syntax), "Boolean query".
- [ ] **B27.5 Bulk indexing & keeping an index in sync** — Elasticsearch Guide: "Bulk API"; "Tune for
  indexing speed"; `elasticsearch-py` docs "Helpers" (`streaming_bulk`). Re-read your B25 notes on the relay.
- [ ] **B27.6 Reindex & backpressure** — Elasticsearch Guide: "Common options" → HTTP `429
  es_rejected_execution_exception`; "Aliases" (zero-downtime reindex via alias swap).

### Exercises
- [ ] **Ex B27.1 Seq scan proof.** Load 100k synthetic documents (`title`, `body`) with `COPY`. Run
  `EXPLAIN ANALYZE` for `WHERE title LIKE '%contract%'` with and without a B-tree and then a
  `gin_trgm_ops` index. *Acceptance:* a table of plan type + execution time for all three; one sentence
  explaining why the B-tree is ignored.
- [ ] **Ex B27.2 FTS vs typo.** Add a generated `tsvector` column (title weight A, body weight B) with GIN.
  Run a fixed set of 8 queries including one typo (`documnet`). *Acceptance:* top-3 results recorded per
  query; the typo query demonstrably fails.
- [ ] **Ex B27.3 First ES index.** Run Elasticsearch (or OpenSearch) in Compose with security settings
  suitable for local dev. Create an index with an explicit mapping (`title` text + keyword subfield, `tags`
  keyword). Use `_analyze` to show how your analyzer tokenizes 3 sample titles. *Acceptance:* mapping JSON
  committed; `_analyze` output pasted in notes.
- [ ] **Ex B27.4 Relevance tuning against a fixed query set.** Same 8 queries: implement `multi_match` with
  a title boost, `fuzziness: AUTO`, and tags as a `filter` clause. *Acceptance:* before/after top-3
  relevance table; the typo query now passes.
- [ ] **Ex B27.5 Bulk loader with backpressure.** Write a script that streams rows from Postgres with a
  server-side cursor and sends `_bulk` batches of N. On `429`, it must wait and retry with backoff (reuse
  B22), never crash. *Acceptance:* memory stays flat for 100k docs (measure RSS); throughput for N = 500,
  2000, 5000 recorded; induced `429` (tiny thread pool/queue settings) handled.
- [ ] **Ex B27.6 Alias swap reindex.** Build `docs_v2` in the background and swap the alias atomically.
  *Acceptance:* a search loop running during the swap sees zero errors.

### Must be able to do / explain
- [ ] Why a leading-wildcard `LIKE` cannot use a B-tree and what `pg_trgm` changes.
- [ ] What Postgres FTS gives (stemming, ranking, weights, highlighting) and the exact query that made you add ES.
- [ ] How an inverted index works; what an analyzer does; `text` vs `keyword`.
- [ ] Query context vs filter context and why tags belong in a filter.
- [ ] Why the search index is derived and how to prove it can be rebuilt.
- [ ] What `429` from ES means and why the right answer is to slow down.

**Estimated hours:** ~12h

### Self-check interview questions
1. Why can't `LIKE '%term%'` use a B-tree index?
2. What does `pg_trgm` index, and what kind of queries does it speed up?
3. What does Elasticsearch give you that Postgres FTS does not?
4. Explain the inverted index in two sentences.
5. What is an analyzer made of?
6. Query context vs filter context — what is the practical difference?
7. How do you keep a search index consistent with the database, and how do you detect drift?
8. How do you reindex without downtime?
9. What does backpressure mean in a bulk indexing job?

---

**Answers**
1. A B-tree is ordered by the value's prefix; a leading wildcard has no fixed prefix, so the tree can't be
   used to narrow the range — the planner must scan every row.
2. It indexes 3-character trigrams of the text. With a GIN/GiST trigram index, `LIKE`/`ILIKE` with
   wildcards anywhere and `similarity()`/`%` fuzzy matches can use the index.
3. Typo tolerance (fuzziness), much finer relevance tuning (boosts, function scores), per-field analyzers
   and multilingual handling, fast aggregations/faceting, horizontal scaling of search.
4. A map from each term to the list of documents (and positions) containing it. A query looks up its
   terms and merges posting lists instead of scanning documents.
5. Zero or more character filters, exactly one tokenizer, zero or more token filters (lowercase, stemming,
   synonyms, stop words).
6. Query context computes a relevance score ("how well"); filter context is yes/no, not scored, and cacheable.
7. Project changes from the source of truth via events (outbox → consumer), make indexing idempotent,
   monitor index lag, and periodically compare counts/checksums; the ultimate fix is a full rebuild from source.
8. Build a new index in the background, then atomically move an alias from old to new; clients only use the alias.
9. The downstream (ES) signals it is overloaded (e.g. `429`); the producer reduces rate or batch size and
   waits instead of retrying harder, which would make the overload worse.

## Module B28 — Replication, Connection Pooling, Sharding (~10h)

**Topics:** WAL and streaming replication; synchronous vs asynchronous replicas; read replicas and
**replication lag**; read-your-own-writes and its mitigations (LSN wait, retry, read from primary);
failover basics; connection cost in Postgres (a process per backend); **PgBouncer** session vs transaction
vs statement pooling, pool sizing, the **asyncpg prepared-statement gotcha** in transaction mode;
Postgres ops recap (statistics and `ANALYZE`, autovacuum and bloat, `pg_stat_statements`, slow query log,
`pg_stat_activity` and `idle in transaction`); partitioning vs sharding; sharding strategies (range, hash,
directory), choosing a shard key, cross-shard queries; **consistent hashing** with virtual nodes vs
`hash % N`.

**Required before:** 1C 2.6 (EXPLAIN), 1C 2.7 (MVCC), 1C 2.9 (VACUUM, partitioning), B3, B5.

### Lessons
- [ ] **B28.1 Replication fundamentals** — *DDIA* (Kleppmann) Ch.5 "Replication": "Leaders and Followers",
  "Problems with Replication Lag" (reading your own writes, monotonic reads).
- [ ] **B28.2 Streaming replication in Postgres** — PostgreSQL docs: Chapter "High Availability, Load
  Balancing, and Replication" → "Log-Shipping Standby Servers" → "Streaming Replication"; "Hot Standby".
  Functions `pg_current_wal_lsn()`, `pg_last_wal_replay_lsn()` (section "System Administration Functions").
- [ ] **B28.3 Connection pooling** — PgBouncer docs (pgbouncer.org): "Usage" (pooling modes), "Config"
  (`pool_mode`, `default_pool_size`, `max_client_conn`, `max_prepared_statements`); asyncpg FAQ on
  "prepared statements and pgbouncer".
- [ ] **B28.4 Operating Postgres as a backend engineer** — PostgreSQL docs: "Routine Vacuuming",
  "Statistics Used by the Planner", Appendix F "pg_stat_statements", "The Cumulative Statistics System"
  (`pg_stat_user_tables`, `pg_stat_activity`).
- [ ] **B28.5 Partitioning & sharding** — *DDIA* Ch.6 "Partitioning": "Partitioning of Key-Value Data",
  "Rebalancing Partitions", "Request Routing".
- [ ] **B28.6 Consistent hashing** — Karger et al. idea as explained in *System Design Interview* Vol.1
  (Alex Xu) Ch.5 "Design Consistent Hashing".

### Exercises
- [ ] **Ex B28.1 Replica in Compose.** Add a streaming replica to a Postgres Compose setup. *Acceptance:* a
  write on the primary becomes visible on the replica; a write on the replica is refused; you can show the
  lag in bytes/LSN under a write burst.
- [ ] **Ex B28.2 Read-your-own-write.** Script: insert on the primary, immediately read on the replica, in a
  loop of 1000 with induced lag (e.g. a heavy write load). *Acceptance:* the "not found" rate is measured;
  then implement one mitigation (LSN wait or retry with backoff) and show the rate drops to 0; notes name all three options.
- [ ] **Ex B28.3 PgBouncer transaction mode.** Put PgBouncer in front of Postgres; connect an async
  SQLAlchemy/asyncpg app. *Acceptance:* reproduce the prepared-statement error, fix it, and show
  `SHOW POOLS;` under a `hey` load; explain the pool size you chose.
- [ ] **Ex B28.4 Postgres ops lab.** With autovacuum off on a scratch table: (a) stale statistics — compare
  estimated vs actual rows before and after `ANALYZE`; (b) bloat — update every row twice, record
  `n_dead_tup` and relation size before/after `VACUUM`; (c) enable `pg_stat_statements` and list top 5
  by `total_exec_time`. *Acceptance:* `postgres-ops-notes.md` with numbers for all three.
- [ ] **Ex B28.5 Consistent hashing ring.** Implement a ring with virtual nodes (`bisect`-based lookup) and
  a naive `hash % N` router. *Acceptance:* for 100k keys, measured % of keys moved when adding and removing
  one node for both; effect of 1 vs 100 virtual nodes on load balance (std-dev of keys per node).

### Must be able to do / explain
- [ ] How streaming replication works and what replication lag means for users.
- [ ] Three ways to get read-your-own-writes and their trade-offs.
- [ ] Why "just raise `max_connections`" is wrong; the three PgBouncer modes.
- [ ] Why asyncpg breaks under transaction pooling and how to fix it.
- [ ] How to find the slowest query without guessing.
- [ ] Partitioning vs sharding; how to pick a shard key; why consistent hashing moves ~1/N of keys.

**Estimated hours:** ~10h

### Self-check interview questions
1. Synchronous vs asynchronous replication — what do you trade?
2. A user updates their profile and the next page shows old data. Why, and how do you fix it?
3. Why is each Postgres connection expensive?
4. Session vs transaction pooling — what breaks in transaction mode?
5. A query plan went bad overnight with no code change. Where do you look?
6. Why doesn't `VACUUM` shrink the table file?
7. Partitioning vs sharding?
8. What makes a good shard key?
9. Why does `hash % N` reshuffle almost everything when N changes?

---

**Answers**
1. Sync: no data loss on primary failure, but every commit waits for the replica (latency, availability risk).
   Async: fast commits, but recent transactions can be lost on failover, and replicas lag.
2. The read went to an asynchronous replica that hasn't replayed the write yet. Read from the primary for
   a short window after a write, wait for the replica LSN, or route that user's reads to the primary.
3. Each connection is a separate OS process with its own memory; many idle connections waste RAM and
   increase contention; context switching grows.
4. Session pooling pins a server connection to a client for its whole session; transaction pooling returns
   it after each transaction, so session state (prepared statements, `SET`, advisory locks, temp tables) breaks.
5. Stale statistics (was `ANALYZE`/autovacuum running?), data growth, `pg_stat_statements` for the query,
   then `EXPLAIN (ANALYZE, BUFFERS)` and compare estimated vs actual rows.
6. `VACUUM` marks dead tuples as reusable space inside the file but doesn't return it to the OS (except
   trailing pages); `VACUUM FULL` or `pg_repack` rewrites the table.
7. Partitioning splits a table inside one database server; sharding splits data across multiple servers.
8. High cardinality, even distribution, present in most queries (so they hit one shard), stable over time,
   no hot keys.
9. The target of almost every key depends on N; changing N changes the remainder for ~(N-1)/N of keys.
   Consistent hashing only moves keys between the neighbours on the ring (~1/N).

## Module B29 — Consensus & Raft (~10h, + OPTIONAL Raft build ~40h)

**Topics:** why distributed agreement is hard (partial failure, unreliable clocks, network partitions);
CAP and PACELC (and their limits); linearizability basics; replicated state machines; **Raft**: terms,
leader election (randomized timeouts, RequestVote), log replication (AppendEntries, `nextIndex`,
`matchIndex`, commit index), safety (election restriction, log matching), membership changes (named);
where consensus lives in real systems (etcd for Kubernetes, RabbitMQ quorum queues, Kafka KRaft);
**etcd** as a 3-node cluster, failover.

**Required before:** B28, B16 (Kafka), B15 (RabbitMQ), 1A.12 (asyncio — for the optional build).

### Lessons
- [ ] **B29.1 The trouble with distributed systems** — *DDIA* Ch.8 "The Trouble with Distributed Systems"
  (faults and partial failures, unreliable networks, unreliable clocks).
- [ ] **B29.2 Consistency and consensus** — *DDIA* Ch.9: "Linearizability", "The Cost of Linearizability"
  (CAP), "Distributed Transactions and Consensus" (fault-tolerant consensus).
- [ ] **B29.3 Raft visually** — thesecretlivesofdata.com/raft (full walkthrough) and raft.github.io
  (interactive visualization).
- [ ] **B29.4 Raft paper** — Ongaro & Ousterhout, "In Search of an Understandable Consensus Algorithm
  (Extended Version)", raft.github.io/raft.pdf: §5.1 basics, §5.2 leader election, §5.3 log replication,
  §5.4 safety, Figure 2 (read it until you can redraw it).
- [ ] **B29.5 etcd in practice** — etcd docs (etcd.io/docs): "Quickstart", "Demo" (etcdctl put/get/watch),
  "FAQ" (why an odd number of members), "Failure modes"/"Understand failovers".

### Exercises
- [ ] **Ex B29.1 Three-node etcd.** Run a 3-node etcd cluster in Compose. *Acceptance:* `etcdctl endpoint
  status` shows the leader; kill the leader, a new one is elected, writes continue; kill a second node,
  writes stop — explain why in terms of quorum.
- [ ] **Ex B29.2 Redraw Figure 2.** From memory, write the state, RPCs and rules of Raft's Figure 2 in your
  notes. *Acceptance:* compare against the paper and list what you got wrong.
- [ ] **Ex B29.3 Trace a partition.** On paper: 5 nodes, the leader is partitioned with one follower. Trace
  terms, elections and which writes commit on each side; then heal. *Acceptance:* a step-by-step table
  showing why the minority side's writes are discarded.
- [ ] **Ex B29.4 consensus-notes.md.** Explain in your own words where consensus is used in Kubernetes
  (etcd), RabbitMQ (quorum queues) and Kafka (KRaft controller), and what happens when each loses quorum.

### OPTIONAL — Build Raft from scratch (~40h) · required by optional project O3 (Job Scheduler)
Repo `raft-impl/` (asyncio, in-process simulated network you control). Milestones only — no reference code.
- [ ] **M1 Simulated network** — nodes exchange messages through a network object that can delay, drop and
  partition messages; deterministic seeds for reproducible runs.
- [ ] **M2 Leader election** — terms, randomized election timeouts, RequestVote with the election
  restriction; test: exactly one leader per term across 1000 seeded runs.
- [ ] **M3 Heartbeats** — AppendEntries as heartbeat; followers reset timers; test: no spurious elections
  under a healthy network.
- [ ] **M4 Log replication** — `nextIndex`/`matchIndex`, commit index advanced by majority, apply to a
  key-value state machine; test: all nodes apply the same commands in the same order.
- [ ] **M5 Log repair** — a lagging/diverged follower is repaired by backtracking `nextIndex`.
- [ ] **M6 Partitions** — partition the leader into a minority; the majority elects a new leader; on heal the
  old leader steps down and its uncommitted entries are overwritten.
- [ ] **M7 Safety checks** — assert the five Raft safety properties (election safety, leader append-only,
  log matching, leader completeness, state machine safety) after every step of randomized torture runs.
- [ ] **M8 Write-up** — `docs/raft-lessons.md`: the three bugs that took the longest and what they taught you.

### Must be able to do / explain
- [ ] Why consensus needs a majority (quorum) and why clusters have odd sizes.
- [ ] Raft election: terms, randomized timeouts, why a stale log cannot win.
- [ ] Raft replication: when an entry is committed.
- [ ] What CAP actually says and why PACELC is more useful.
- [ ] Which systems you've used rely on consensus and what they do without quorum.

**Estimated hours:** ~10h (+ ~40h optional build)

### Self-check interview questions
1. What problem does consensus solve?
2. Why does a 3-node cluster tolerate 1 failure but a 4-node cluster still only tolerates 1?
3. How does Raft avoid two leaders in the same term?
4. When is a log entry committed in Raft?
5. What happens to writes accepted by an old leader in a minority partition?
6. Explain CAP in one sentence, and one criticism of it.
7. What does Kubernetes store in etcd, and what happens if etcd loses quorum?

---

**Answers**
1. Getting a group of nodes to agree on a single value/sequence of values despite crashes and message loss,
   so they can act as one reliable replicated state machine.
2. A majority is needed: 2 of 3 or 3 of 4. Both lose quorum after 2 failures, so the 4th node adds cost without extra fault tolerance.
3. Each node votes at most once per term, and a candidate needs a majority; two majorities always overlap.
4. When the leader has replicated it to a majority of nodes (and it is from the leader's current term); then it can be applied.
5. They were never replicated to a majority, so they are not committed; when the partition heals the old leader
   sees a higher term, steps down, and those entries are overwritten.
6. During a network partition a system must choose between consistency and availability. Criticism: it only
   talks about partitions and a narrow definition of availability; PACELC adds the latency vs consistency trade-off when there is no partition.
7. All cluster state (objects, specs, status). Without quorum the API server can't write: running pods keep
   running, but no scheduling, scaling or changes happen.

## Module B30 — Kubernetes (~20h)

**Topics:** why orchestration (when Compose stops coping); cluster architecture (control plane, etcd,
kubelet, kube-proxy); `kind` for local clusters; `kubectl` basics; Pods, ReplicaSets, **Deployments**,
**Services** (ClusterIP, NodePort), **Ingress** with the Nginx Ingress Controller; **ConfigMaps** and
**Secrets**; namespaces and labels/selectors; **requests/limits**, QoS classes, OOMKilled; **probes**
(liveness, readiness, startup); **`preStop` + `terminationGracePeriodSeconds`** and graceful shutdown;
**rolling updates**, `maxSurge`/`maxUnavailable`, `kubectl rollout undo`; **HPA** and metrics-server;
Jobs/CronJobs (named); declarative YAML and **GitOps** concepts (Argo CD, Flux); **Helm** basics (charts,
values, templating).

**Required before:** B3 (Docker), B17 (Nginx), B23 (graceful shutdown, zero-downtime concepts), B24 (metrics).

### Lessons
- [ ] **B30.1 Kubernetes basics** — kubernetes.io "Learn Kubernetes Basics" modules 1–6 (create a cluster,
  deploy an app, explore, expose, scale, update).
- [ ] **B30.2 Local cluster with kind** — kind docs (kind.sigs.k8s.io): "Quick Start" (creating a cluster,
  loading an image into the cluster), "Ingress" (ingress-nginx on kind).
- [ ] **B30.3 Workloads & networking** — kubernetes.io Concepts: "Deployments", "Service", "Ingress".
- [ ] **B30.4 Configuration** — kubernetes.io Concepts: "ConfigMaps", "Secrets", "Resource Management for
  Pods and Containers", "Pod Quality of Service Classes".
- [ ] **B30.5 Health & lifecycle** — kubernetes.io Tasks: "Configure Liveness, Readiness and Startup
  Probes"; Concepts: "Pod Lifecycle" → "Termination of Pods"; "Container Lifecycle Hooks".
- [ ] **B30.6 Scaling** — kubernetes.io Tasks: "HorizontalPodAutoscaler Walkthrough".
- [ ] **B30.7 GitOps & Helm** — Argo CD docs "Core Concepts"; Helm docs (helm.sh) "Quickstart Guide" and
  "Chart Template Guide → Getting Started".

### Exercises
- [ ] **Ex B30.1 First deployment.** Build a FastAPI image, load it into `kind`, deploy it as a Deployment
  with 2 replicas + a ClusterIP Service. *Acceptance:* `kubectl port-forward` reaches both pods (show pod
  names in responses); all YAML in `k8s/`, nothing created imperatively.
- [ ] **Ex B30.2 Ingress + config.** Install ingress-nginx, route a hostname to the Service; move settings
  into a ConfigMap and a DB password into a Secret. *Acceptance:* changing the ConfigMap and restarting the
  rollout changes app behaviour; the Secret is never committed in plain text (explain what base64 is not).
- [ ] **Ex B30.3 Resources & OOMKill.** Set requests/limits; then set the memory limit too low on purpose.
  *Acceptance:* `kubectl describe pod` shows `OOMKilled` and restarts; notes explain requests vs limits and QoS class.
- [ ] **Ex B30.4 Zero-downtime rolling update.** Run a `hey` load during a rolling update: first without
  `preStop`, then with `preStop` sleep + graceful shutdown + readiness probe. *Acceptance:* error counts
  for both runs recorded; the second run has 0 failed requests.
- [ ] **Ex B30.5 Probes & rollback.** Deploy an image whose readiness probe fails. *Acceptance:* it never
  receives traffic; `kubectl rollout undo` restores the previous version; explain liveness vs readiness.
- [ ] **Ex B30.6 HPA.** Install metrics-server, add a CPU-based HPA. *Acceptance:* under load replicas go
  2 → 4 and back to 2; screenshots or `kubectl get hpa -w` output saved.
- [ ] **Ex B30.7 Helm chart (small).** Turn your YAML into a minimal chart with `values.yaml` (image tag,
  replicas, resources). *Acceptance:* `helm install` and `helm upgrade --set image.tag=...` work.

### Must be able to do / explain
- [ ] What a Deployment gives you over `docker run`.
- [ ] Service vs Ingress; how traffic reaches a pod.
- [ ] Requests vs limits; what happens without them.
- [ ] Liveness vs readiness vs startup probes.
- [ ] Why rolling updates drop requests by default and how `preStop` + graceful shutdown fixes it.
- [ ] How HPA decides the replica count.
- [ ] What GitOps means and why all state belongs in YAML in git.

**Estimated hours:** ~20h

### Self-check interview questions
1. What does the Kubernetes control plane consist of?
2. What is the difference between a Pod and a Deployment?
3. Service vs Ingress?
4. What happens if a pod has no memory limit? If the limit is too low?
5. Liveness vs readiness — what breaks if you use the same endpoint and check?
6. Why can a rolling update drop requests even with readiness probes?
7. How does the HPA work?
8. Why are Kubernetes Secrets "not really secret" by default?
9. What is GitOps?
10. What problem does Helm solve?

---

**Answers**
1. API server, etcd (state), scheduler, controller manager (and cloud controller manager); nodes run kubelet,
   kube-proxy and a container runtime.
2. A Pod is one instance of one or more containers; a Deployment declares the desired number of identical
   pods and manages ReplicaSets for rolling updates and rollbacks.
3. A Service gives a stable virtual IP/DNS name load-balancing to pods inside the cluster; an Ingress is an
   HTTP(S) routing layer (hosts/paths, TLS) from outside the cluster to Services.
4. No limit: it can use all node memory and starve neighbours or trigger node pressure evictions. Too low: the
   kernel OOM-kills the container repeatedly (CrashLoopBackOff).
5. Liveness failing restarts the container; readiness failing removes it from Service endpoints. If a
   dependency outage fails liveness, all pods restart in a loop instead of just being taken out of rotation.
6. Endpoint removal and `SIGTERM` happen concurrently; kube-proxy/Ingress may still route to the terminating
   pod for a moment. A `preStop` sleep plus graceful shutdown of in-flight requests closes the gap.
7. It periodically reads metrics (e.g. average CPU vs the target from metrics-server) and computes
   desired replicas = ceil(current × current metric / target), within min/max bounds, with stabilization windows.
8. They're only base64-encoded and stored in etcd (unencrypted unless encryption at rest is configured);
   anyone with read access to the namespace can read them.
9. The desired cluster state lives declaratively in git; a controller (Argo CD/Flux) continuously reconciles
   the cluster to match git; changes happen through pull requests.
10. Packaging and templating of Kubernetes manifests with parameters (values), versioned releases, upgrades and rollbacks.

## Project P8 — DocuVault · Middle+ (~60h)

**Document management with full-text search, versioning, replication and Kubernetes.**
Repo: `docuvault/` (+ optional `docuvault-web/`).

### Goal
A mid-size company has thousands of internal documents (policies, contracts, reports) scattered across
drives with no real search. Build a system where every document is versioned, searchable with typo
tolerance, and where the search index is **derived and always rebuildable** from Postgres. Three lessons:
(1) a derived index is never the source of truth — prove it by rebuilding it; reach for Elasticsearch only
after Postgres FTS failed on a specific query; (2) Kubernetes only because Compose has genuinely stopped
coping — the written service list is the evidence; (3) this is where Postgres gets **operated**, not just
queried.

### Roles
| Role | Can | Cannot |
|---|---|---|
| `reader` | Search, view metadata and versions, download a version | Upload, create versions, delete |
| `contributor` | Reader + upload documents, add versions to own documents | Delete; edit tags on others' docs |
| `librarian` | Manage tags/taxonomy, edit metadata on any doc, trigger reindex | Delete a version (history is immutable) |
| `platform_admin` | Full reindex, manage cluster and index | — |

Known, documented gap: search results are **not access-filtered** in v1 — describe how you would close it
(index ACLs, filter at query time) and why it is harder than it sounds.

### Features
- [ ] Upload documents to MinIO/S3 via presigned URLs; every edit creates an immutable version;
      `current_version_id` is a pointer, nothing is overwritten
- [ ] `version_number` assigned under `SELECT … FOR UPDATE` on the parent row (UNIQUE as the backstop)
- [ ] Tags and tag filtering
- [ ] Search in stages on one corpus and one fixed query set: `LIKE` → `pg_trgm` → Postgres FTS
      (`tsvector` generated column, weights, `ts_rank`) → Elasticsearch (fuzziness, title boost, tag filter);
      `?engine=pg` keeps the Postgres path for comparison
- [ ] Elasticsearch kept current by an event consumer (outbox relay pattern from FleetTrack, via RabbitMQ)
- [ ] `POST /documents/reindex` → `202 Accepted` + `reindex_jobs` resource; server-side cursor → `_bulk`
      batches; batch size tuned; backpressure on `429`
- [ ] Postgres read replica serving the indexing consumer + a read-your-own-write mitigation (LSN wait or retry)
- [ ] PgBouncer in transaction mode, asyncpg prepared-statement gotcha solved
- [ ] Postgres ops demos: stale statistics, autovacuum/bloat, `pg_stat_statements` top-10, slow query log
- [ ] `kind` cluster: Deployment (2 replicas), Service, Ingress, ConfigMap, Secret, requests/limits
      (deliberate OOMKill), probes, `preStop`, HPA, `rollout undo`; YAML in `k8s/` GitOps-style
- [ ] 3-node etcd cluster explored
- [ ] Consistent-hashing ring benchmarked vs `hash % N`; sharding decision record (not implemented)
- [ ] Prometheus/Grafana: index lag, search latency, replica lag, pod restarts

### API
| Method | Path | Role | Notes |
|---|---|---|---|
| POST | `/documents` | contributor+ | First upload |
| POST | `/documents/{id}/versions` | contributor+ | New version; old ones retained |
| GET | `/documents/{id}` | reader+ | Metadata + current version |
| GET | `/documents/{id}/versions` | reader+ | Full history |
| GET | `/documents/{id}/versions/{n}/download` | reader+ | Presigned GET |
| GET | `/documents/search?q=&tags=` | reader+ | ES; `?engine=pg` for Postgres FTS |
| POST | `/documents/reindex` | platform_admin | `202` + `Location: /reindex-jobs/{id}` |
| GET | `/reindex-jobs/{id}` | platform_admin | `done/total`, status |

### Domain model (sketch)
`documents(id, title, current_version_id, created_by, body_excerpt, search_tsv GENERATED …)` with GIN on
`search_tsv` and `gin_trgm_ops` on `title`; `document_versions(id, document_id, s3_key, version_number,
created_at, UNIQUE(document_id, version_number))`; `tags`; `document_tags`; `reindex_jobs(id, status, total,
done, started_at, finished_at, error)`.

### Tech stack
| Tool | Taught in |
|---|---|
| FastAPI, Pydantic | B4 |
| SQLAlchemy 2.0 async, Alembic | B5 |
| Row locks (`FOR UPDATE`) | B7, 1C 2.8 |
| PostgreSQL FTS, `pg_trgm`, GIN, generated columns, `COPY` | 1C 2.10, 1C 2.5, 1C 2.4, 1C 1.6; B27 |
| Elasticsearch / OpenSearch, `_bulk` | B27 |
| MinIO / S3 presigned URLs | B20 |
| RabbitMQ | B15 |
| Outbox relay pattern | B25 |
| Streaming replica, PgBouncer, `pg_stat_statements` | B28 |
| Consistent hashing | B28 |
| etcd, Raft concepts | B29 |
| Kubernetes (`kind`), Ingress, HPA | B30 |
| Graceful shutdown | B23 |
| Prometheus, Grafana | B24 |
| `hey` load generator | B8 |
| Docker Compose | B3 |
| pytest, factory_boy | B8, 1A.8 |
| React + TS + TanStack Query (**OPTIONAL**) | B21 |

### Required knowledge
B3, B4, B5, B7, B8, B15, B20, B23, B24, B25, B27, B28, B29, B30; 1C Part 2 (2.4, 2.5, 2.6, 2.8, 2.9, 2.10);
1A.12 (asyncio). Reuses: presigned pattern from P5 CarePoint, relay pattern from P7 FleetTrack.

### Milestones
- [ ] **M1 Documents & versioning** — models + migrations, upload via presigned URL, versions, concurrency-safe
      `version_number` (20 concurrent uploads → 1..20, no gaps). Tag `v0.1-docs`
- [ ] **M2 Search in Postgres** — load 100k docs with `COPY`; `LIKE` → `pg_trgm` → FTS on the fixed query
      set; latency + top-3 relevance recorded; find the query FTS can't serve. Tag `v0.2-pg-search`
- [ ] **M3 Elasticsearch** — event consumer indexing into ES; `GET /documents/search` with analyzer,
      fuzziness, title boost, tag filter; `docs/search-decision-record.md`. Tag `v0.3-es-search`
- [ ] **M4 Reindex** — `202` + job; cursor → `_bulk`; batch size tuned; `429` handled; recovery test
      (drop an event → stale → reindex → correct). Tag `v0.4-reindex`
- [ ] **M5 Replica, pooling, Postgres ops** — replica for the consumer; read-your-own-write mitigation;
      PgBouncer transaction mode; stale-stats/bloat/`pg_stat_statements`/slow-log demos;
      `docs/postgres-ops-notes.md`. Tag `v0.5-pg-ops`
- [ ] **M6 Kubernetes** — write down the Compose service list (the justification); `kind` + Deployment,
      Service, Ingress, ConfigMap, Secret, requests/limits (OOMKill seen), probes; rolling update without
      then with `preStop` (count errors → 0); `rollout undo`; HPA 2→4→2; YAML in `k8s/`. Tag `v0.6-k8s`
- [ ] **M7 Consensus & sharding** — 3-node etcd; `docs/consensus-notes.md`; consistent-hashing benchmark;
      `docs/sharding-decision-record.md` with a measured number; Grafana index-lag panel. Tag `v1.0-docuvault`
- [ ] **M8 (OPTIONAL) Search UI** — `docuvault-web/`: debounced search box + tag chips (needs B21)

### Definition of done
- [ ] Upload → version → search → history all working
- [ ] ES synced by the consumer **and** fully rebuildable via `/reindex`; recovery test passes
- [ ] Source-of-truth boundary stated in code comments and docs
- [ ] Search tuned against a fixed query set with before/after relevance; typo query fails on FTS, passes on ES
- [ ] Reindex: `202` in <100ms, flat memory for 100k docs, `429` slows the loop instead of crashing it
- [ ] Replica serves the consumer; read-your-own-write exercised under induced lag
- [ ] PgBouncer works in transaction mode; `SHOW POOLS` observed under load
- [ ] Stale stats (>100× estimate error before `ANALYZE`), bloat before/after `VACUUM`, top-10 queries recorded
- [ ] `kind`: 2 replicas, Ingress, requests/limits, probes, rolling update with **zero** dropped requests, HPA, rollback
- [ ] etcd explored; consistent-hashing ring benchmarked; sharding decision record written
- [ ] Access-control-in-search gap documented honestly
- [ ] `docs/postmortem.md` — what went wrong, what you'd change

**Estimated hours:** ~60h (+ ~8h optional UI, + ~12h optional RAG extension)

### OPTIONAL extensions
- **Search UI** (B21): debounced search page with TanStack Query.
- **RAG "ask your documents"** (Track 3 → LLM Zoomcamp modules 1, 2, 4): chunk version text, embed, store in
  `pgvector` or an ES `dense_vector` field (`docs/rag-decision-record.md`), `GET /documents/ask?q=` citing
  document + version, re-embed triggered by the same indexing events, hit rate on 15–20 hand-written questions.

### Interview questions
1. Why is Elasticsearch never the source of truth here, and how do you prove the index is rebuildable?
2. Why not stop at Postgres full-text search — what exactly did Elasticsearch buy you?
3. How does a Kubernetes rolling update drop zero requests? What does `preStop` do that a readiness probe doesn't?
4. Your consumer reads its own write from a replica and gets "not found". Give three fixes.
5. Why PgBouncer, why transaction mode, and what broke with asyncpg?

---

**Short answers**
1. ES is fed from Postgres by events and can lose or miss updates; Postgres holds the transactional truth.
   Proof: the recovery test — drop an event, observe stale search, run `/reindex` from Postgres, observe
   correct results.
2. Typo tolerance (fuzziness) and tunable relevance (boosts) for the concrete typo query that FTS failed,
   plus better multilingual analysis and aggregations — at the cost of a second, derived store.
3. The new pod only receives traffic once ready; the old pod gets a `preStop` sleep so load balancers stop
   routing to it before `SIGTERM`, and graceful shutdown finishes in-flight requests. Readiness alone
   doesn't cover the race between endpoint removal and termination.
4. Wait until the replica's replay LSN ≥ the LSN captured at commit; retry with backoff on not-found; read
   that one row from the primary.
5. Each Postgres connection is a process; replicas × pool size would exceed what Postgres should hold.
   Transaction mode multiplexes many clients over few server connections. asyncpg's implicit prepared
   statements are per-connection session state, which breaks when the next transaction lands on another
   server connection — fix with `statement_cache_size=0` or PgBouncer's `max_prepared_statements`.

## Module B31 — Secrets Management with Vault (~8h)

**Topics:** why `.env` files are not secrets management (shell history, backups, git history, no audit,
no rotation); HashiCorp Vault concepts: seal/unseal, dev mode vs production, tokens and policies,
**AppRole** auth for machines; **KV v2** engine (versions, metadata); **dynamic database credentials**
(database secrets engine, roles, leases, TTL, renew, revoke); **transit** engine (encryption as a service,
key versions, rotate, rewrap) and **envelope encryption** (DEK encrypts data, KEK wraps DEK); secret
**rotation with a grace window**; **fail-closed** startup; audit devices.

**Required before:** B3 (Compose), B4, B5, B19 (security basics).

### Lessons
- [ ] **B31.1 Why Vault** — developer.hashicorp.com/vault: "What is Vault?" and tutorial "Getting Started"
  → "Starting the Server" (dev mode), "Your First Secret", "Secrets Engines".
- [ ] **B31.2 KV v2** — Vault docs "KV secrets engine – version 2" (versions, `kv rollback`, metadata);
  `hvac` Python client docs "KV v2".
- [ ] **B31.3 Auth & policies** — Vault tutorials "Policies" and "AppRole Pull Authentication".
- [ ] **B31.4 Dynamic database credentials** — Vault tutorial "Dynamic Secrets: Database Secrets Engine"
  (PostgreSQL); docs "Lease, Renew, and Revoke".
- [ ] **B31.5 Transit & envelope encryption** — Vault tutorial "Encryption as a Service: Transit Secrets
  Engine"; docs "Transit secrets engine" (datakey, rotate, rewrap).

### Exercises
- [ ] **Ex B31.1 Vault in Compose.** Run Vault (dev mode, then a file-backed non-dev mode once to see
  seal/unseal). Store an API signing secret in KV v2; a FastAPI app reads it at startup via AppRole.
  *Acceptance:* no secret in `.env` or in the image; app **refuses to start** if Vault is unreachable
  (fail-closed), with a clear log message.
- [ ] **Ex B31.2 Rotation with a grace window.** Rotate the signing secret (new KV version); the app accepts
  signatures from either the current or previous version for a configured window, then only the new one.
  *Acceptance:* a test sending messages signed with old/new secret across the window passes.
- [ ] **Ex B31.3 Dynamic DB credentials.** Configure the database secrets engine for Postgres with a role and
  a short TTL; the app obtains credentials at startup and renews the lease. *Acceptance:* `\du` shows the
  temporary role with `VALID UNTIL`; after revoking the lease the app gets fresh credentials without a restart.
- [ ] **Ex B31.4 Envelope encryption.** Encrypt a PII field in the application: generate a data key via
  transit, encrypt locally, store ciphertext + wrapped DEK + key version. Rotate the KEK and rewrap.
  *Acceptance:* the DB column contains only ciphertext; old rows still decrypt after rotation.

### Must be able to do / explain
- [ ] Why secrets don't belong in `.env`, images or git — and what Vault adds (audit, TTLs, rotation).
- [ ] KV vs dynamic secrets; what a lease is.
- [ ] How a machine authenticates to Vault (AppRole) and how policies limit it.
- [ ] Envelope encryption and why disk encryption is not "PII encryption".
- [ ] How to rotate a secret without downtime.

**Estimated hours:** ~8h

### Self-check interview questions
1. What problems do `.env` files have for production secrets?
2. What are dynamic database credentials and why are they safer?
3. What is a Vault lease?
4. Explain envelope encryption.
5. Why is full-disk encryption not enough for PII?
6. How do you rotate a webhook signing secret without dropping requests?
7. What should an app do if Vault is down at startup?

---

**Answers**
1. They leak into shell history, backups, images, logs and git; no audit trail; no automatic rotation or expiry;
   everyone with the file has the same long-lived secret.
2. Vault creates a unique, short-lived DB role per app instance on demand and revokes it on expiry, so a leaked
   credential expires quickly and each use is attributable.
3. A time-bound grant attached to a secret; it must be renewed before TTL or it expires and Vault revokes the secret.
4. A random data key (DEK) encrypts the data; the DEK is itself encrypted ("wrapped") by a key-encryption key (KEK)
   that never leaves the KMS/Vault. You store ciphertext + wrapped DEK; rotating the KEK only requires rewrapping DEKs.
5. It only protects against someone stealing the physical disk; anyone with DB access (SQL injection, a leaked
   dump, a curious admin) still reads plaintext.
6. Introduce the new secret, accept signatures under both old and new during a grace window, switch the signer to
   the new one, then remove the old after the window.
7. Fail closed: refuse to start (and fail readiness), rather than fall back to defaults or cached plaintext.

## Module B32 — gRPC + Protobuf (~8h)

**Topics:** RPC vs REST; Protocol Buffers proto3 (messages, scalar types, `repeated`, `oneof`, enums, field
numbers and backward compatibility, reserved fields); code generation with `grpcio-tools`; service types:
unary, server streaming, client streaming, bidirectional; **deadlines** and their propagation; **status
codes** (`INVALID_ARGUMENT`, `FAILED_PRECONDITION`, `DEADLINE_EXCEEDED`, `UNAVAILABLE`…); metadata;
interceptors (logging, auth); HTTP/2 multiplexing; grpc-web / gateways for browsers; **REST vs gRPC vs
GraphQL** trade-offs; measuring latency fairly.

**Required before:** B1 (API design), B4, B17 (HTTP/2), B22 (timeouts, circuit breaker).

### Lessons
- [ ] **B32.1 Concepts** — grpc.io docs "Introduction to gRPC" and "Core concepts, architecture and lifecycle"
  (service definition, RPC lifecycle, deadlines, cancellation, metadata).
- [ ] **B32.2 Protobuf** — protobuf.dev "Language Guide (proto 3)" (field numbers, "Updating A Message Type",
  reserved fields); "Proto Best Practices".
- [ ] **B32.3 Python quickstart** — grpc.io "Python → Quick start" and "Basics tutorial" (route guide, all four RPC types).
- [ ] **B32.4 Errors & deadlines** — grpc.io guides "Status codes and their use in gRPC", "Deadlines", "Interceptors".

### Exercises
- [ ] **Ex B32.1 Contract first.** Write a `.proto` for a small `Inventory` service (`GetItem`, `ListItems`
  server-streaming). Generate code. *Acceptance:* generated files are produced by a Makefile target, not committed by hand.
- [ ] **Ex B32.2 Server + client.** Implement the server with `grpcio` and a client with a **deadline**.
  *Acceptance:* a slow handler causes `DEADLINE_EXCEEDED` on the client quickly; domain errors map to proper status codes.
- [ ] **Ex B32.3 Interceptor.** Add a server interceptor that logs method, duration and status code with a
  request ID read from metadata. *Acceptance:* logs show the request ID propagated from the client.
- [ ] **Ex B32.4 Compatibility.** Add a field to the response and remove another (mark it `reserved`).
  *Acceptance:* an old client still works against the new server; notes explain why field numbers must never be reused.
- [ ] **Ex B32.5 REST vs gRPC measurement.** Same operation over FastAPI JSON and gRPC under identical load.
  *Acceptance:* p50/p95 for both recorded with methodology (warm-up, same machine, same payload).

### Must be able to do / explain
- [ ] Why `.proto` is a stronger contract than OpenAPI in practice; how to evolve it safely.
- [ ] The four RPC types and when streaming is useful.
- [ ] Deadlines vs timeouts; why deadlines propagate.
- [ ] How to map domain errors to gRPC status codes.
- [ ] When to choose REST, gRPC or GraphQL.

**Estimated hours:** ~8h

### Self-check interview questions
1. What does gRPC give you over REST/JSON?
2. Why must you never reuse a protobuf field number?
3. What is a deadline and how is it different from a client timeout?
4. What are the four gRPC call types?
5. Why is gRPC awkward for browsers?
6. REST vs gRPC vs GraphQL — when is each the right default?

---

**Answers**
1. A strict schema with generated clients/servers, compact binary encoding, HTTP/2 multiplexing and streaming,
   built-in deadlines, standardized status codes.
2. The wire format identifies fields by number; reusing one makes old data or old clients decode bytes as the
   wrong field. Mark removed numbers `reserved`.
3. A deadline is an absolute point in time sent with the call and propagated to downstream calls, so the whole
   chain stops working on a request nobody is waiting for; a local timeout only affects one hop.
4. Unary, server streaming, client streaming, bidirectional streaming.
5. Browsers don't expose the HTTP/2 framing/trailers gRPC needs; you need grpc-web plus a proxy or a REST/JSON gateway.
6. REST: public APIs, browsers, caching, simplicity. gRPC: internal service-to-service, latency-sensitive,
   strong contracts, streaming. GraphQL: client-driven aggregation of many resources for UIs (BFF).

## Module B33 — Cloud Basics + Terraform (~15h)

**Topics:** shared responsibility model; accounts/projects, regions/zones; **IAM**: users vs roles, policies,
least privilege, no wildcard actions, service accounts; **networking**: VPC, public/private subnets, route
tables, internet gateway, NAT gateway (and its cost), security groups/firewall rules; managed databases
(RDS/Cloud SQL) in private subnets; object storage + CDN; DNS and TLS certificates (ACM/managed certs, or
Let's Encrypt recap); cost awareness (tags, budgets, alerts, what is expensive when idle). **Terraform**:
HCL, providers, resources, data sources, variables, outputs, `plan`/`apply`/`destroy`, **state** (what it
is, why remote, locking), remote backends (S3 + DynamoDB/S3 lockfile, or GCS), modules, `terraform fmt`/
`validate`, drift detection, `plan` in CI.

**Required before:** B2 (Linux), B17 (networking, DNS, TLS), B23 (CI/CD). Pick **one** cloud (AWS or GCP) and stick to it.

### Lessons
- [ ] **B33.1 Cloud fundamentals** — AWS: "IAM best practices" and "How Amazon VPC works" (VPCs, subnets,
  route tables, gateways), "Control traffic to your resources using security groups". GCP alternative: "IAM
  overview", "VPC network overview", "VPC firewall rules".
- [ ] **B33.2 Managed databases & storage** — AWS "Amazon RDS: Working with a DB instance in a VPC"
  and "Amazon S3 → Blocking public access"; or GCP "Cloud SQL → Private IP" and "Cloud Storage → Public access prevention".
- [ ] **B33.3 Terraform basics** — developer.hashicorp.com/terraform tutorials: "Get Started" collection for
  your cloud (install, build, change, destroy infrastructure, define input variables, query data with outputs,
  store remote state).
- [ ] **B33.4 State & backends** — Terraform docs "State" (purpose, locking, sensitive data in state) and
  "Backend configuration" (`s3` or `gcs` backend).
- [ ] **B33.5 Modules & workflow** — Terraform tutorials "Modules" (use and build a module) and "Automate
  Terraform with GitHub Actions".
- [ ] **B33.6 Cost** — AWS "Cost Explorer" + "AWS Budgets" docs (or GCP "Billing budgets and alerts"); read the
  NAT gateway pricing page for your cloud.

### Exercises
- [ ] **Ex B33.1 Budget first.** Create a billing budget with an email alert at a small amount before
  creating anything else. *Acceptance:* screenshot/notes of the budget; cost-center tag strategy written down.
- [ ] **Ex B33.2 Network as code.** Terraform: VPC, one public and one private subnet, route tables, security
  groups (443 in to a "gateway" SG, 5432 only from the gateway SG). *Acceptance:* `terraform plan` is clean
  after `apply`; notes explain every resource; NAT gateway decision (and cost) written down.
- [ ] **Ex B33.3 Least-privilege IAM.** A role for a service that can only read one bucket prefix.
  *Acceptance:* a policy simulator/CLI test shows allowed vs denied actions; no `"*"` actions.
- [ ] **Ex B33.4 Remote state with locking.** Move state to a remote backend with locking. *Acceptance:* two
  concurrent `terraform apply` runs → the second waits/fails on the lock.
- [ ] **Ex B33.5 Destroy and recreate.** `terraform destroy` then `apply`. *Acceptance:* identical resources;
  nothing had to be clicked in the console.
- [ ] **Ex B33.6 Plan in CI.** GitHub Actions runs `fmt -check`, `validate` and `plan` on PRs touching
  `infra/`, `apply` only from `main`. *Acceptance:* a PR shows the plan output; cloud credentials via OIDC or
  repo secrets, never in code.

### Must be able to do / explain
- [ ] Shared responsibility; IAM users vs roles; least privilege.
- [ ] Public vs private subnets; what makes a subnet "public"; why the DB lives in a private subnet.
- [ ] Security groups vs network ACLs (or GCP firewall rules).
- [ ] What Terraform state is, why it must be remote and locked, and why it's sensitive.
- [ ] `plan` vs `apply`; what drift is and how to detect it.
- [ ] Which cloud resources cost money when idle.

**Estimated hours:** ~15h

### Self-check interview questions
1. What makes a subnet public?
2. Why should the database never be in a public subnet?
3. IAM role vs IAM user?
4. What is Terraform state and what goes wrong without locking?
5. What is drift?
6. Why Terraform instead of the console?
7. Name two resources that surprise people on the bill.

---

**Answers**
1. Its route table sends `0.0.0.0/0` to an internet gateway (and instances get public IPs).
2. It must only be reachable from the application; a public subnet exposes it to scanning and brute force and
   makes one misconfigured rule a breach.
3. A user has long-lived credentials for a person; a role is assumed temporarily (by services, instances or
   federated users) and issues short-lived credentials.
4. Terraform's record mapping config to real resource IDs and attributes. Without locking two applies can
   interleave and corrupt state or create duplicates.
5. Differences between real infrastructure and the Terraform config/state, usually from manual changes; `terraform plan` reveals it.
6. Reviewable diffs, reproducibility (destroy/recreate), documentation that is always true, no knowledge only in someone's memory.
7. NAT gateways (hourly + data processing), idle managed databases, load balancers, egress traffic, unattached IPs/volumes.

## Module B34 — Idempotency & Webhooks (~6h)

**Topics:** why retries create duplicates (timeouts, flaky networks, client retry logic); safe vs idempotent
HTTP methods; **`Idempotency-Key`** header, storing key + **request hash** + response; concurrency: two
identical requests at the same instant; **`INSERT … ON CONFLICT (key) DO NOTHING RETURNING`** vs catching
`IntegrityError` vs `DO UPDATE`; retention window for keys; **why Redis is the wrong source of truth** for
money idempotency (durability, not transactional with the payment row) vs where Redis is fine (rate limits);
**webhooks**: at-least-once delivery, duplicates, out-of-order and "arrives before your own commit";
**HMAC signatures over the raw body**, constant-time comparison, timestamps + replay protection; webhook
idempotency by `provider_event_id` (JSONB generated column + UNIQUE); **API keys** for server-to-server auth
(hashing, prefixes, rotation) vs JWT vs HMAC.

**Required before:** B4, B5, B7, B12 (Redis), 1C 2.3 (ON CONFLICT), 1C 2.4 (JSONB, generated columns).

### Lessons
- [ ] **B34.1 Idempotent requests** — Stripe API reference "Idempotent requests"; Stripe engineering blog
  "Designing robust and predictable APIs with idempotency"; IETF draft "The Idempotency-Key HTTP Header Field".
- [ ] **B34.2 Idempotent insert in Postgres** — PostgreSQL docs `INSERT` → "ON CONFLICT Clause" (and
  `RETURNING`); recap 1C 2.3.
- [ ] **B34.3 Webhooks done right** — Stripe docs "Receive Stripe events in your webhook endpoint" (verify
  signatures, handle duplicate events, event ordering) and "Check the webhook signatures" (raw body,
  timestamp tolerance); Python docs `hmac` (`hmac.compare_digest`).
- [ ] **B34.4 API keys** — OWASP "REST Security Cheat Sheet" → "API Keys"; Python docs `secrets`.

### Exercises
- [ ] **Ex B34.1 Idempotency middleware/service.** `POST /orders` requires `Idempotency-Key`; store key,
  request hash and response. *Acceptance:* same key + same body → identical response, one row; same key +
  different body → explicit `422`/`409` error.
- [ ] **Ex B34.2 The race.** Fire the same request twice concurrently (asyncio/threads, tight loop, 100
  iterations). *Acceptance:* always exactly one side effect; both callers get the same response; implemented
  with `ON CONFLICT DO NOTHING RETURNING`, not a check-then-insert.
- [ ] **Ex B34.3 HMAC webhook receiver.** Verify the signature over the **raw** body before parsing, with a
  timestamp tolerance. *Acceptance:* tests for valid, tampered body, wrong secret, stale timestamp; failures
  are logged as security events.
- [ ] **Ex B34.4 Duplicate & out-of-order events.** Store events with a UNIQUE generated column on
  `payload->>'id'`. *Acceptance:* the same event 3× → processed once; an event arriving before the related
  row exists is handled (retry or park), not crashed.
- [ ] **Ex B34.5 API keys.** Issue keys shown once, store only a hash + a lookup prefix, support two active keys
  per client for rotation. *Acceptance:* a leaked DB dump does not reveal usable keys.

### Must be able to do / explain
- [ ] Request idempotency vs webhook idempotency and why both are needed.
- [ ] Why the request hash matters.
- [ ] Why a unique constraint (not `if exists`) resolves the race.
- [ ] Why Redis is wrong for money idempotency but fine for rate limiting.
- [ ] How HMAC verification works and why you verify the raw body.
- [ ] API key vs JWT vs HMAC — when each applies.

**Estimated hours:** ~6h

### Self-check interview questions
1. What is an idempotency key and who generates it?
2. What breaks if you store the key without a request hash?
3. Two identical requests arrive in the same millisecond — what happens in your design?
4. Why `ON CONFLICT DO NOTHING RETURNING` instead of catching the integrity error?
5. Why verify the signature over the raw body?
6. How do you protect webhooks from replay?
7. Why isn't Redis a good idempotency store for payments?

---

**Answers**
1. A unique client-generated value (e.g. UUID) per logical operation, reused on retries, so the server can
   return the original result instead of repeating the side effect.
2. A different request reusing the key by mistake silently receives the cached response of another operation —
   a client bug becomes a silent correctness bug.
3. Both try to insert the key; the unique constraint lets exactly one win; the loser sees no returned row and
   reads/waits for the winner's stored response.
4. It's one atomic statement with no exception control flow, no aborted transaction to recover, and the
   returned row tells you directly whether you won.
5. Any re-serialization (whitespace, key order, number formats) changes the bytes and breaks the signature;
   parsing untrusted input before authenticating it is also risky.
6. Include a timestamp in the signed payload and reject old ones; store processed event IDs to reject duplicates.
7. Its durability depends on config (data can be lost on failover/restart), and the key can't be written in the
   same transaction as the payment row, so a crash between them leaves them inconsistent.

## Module B35 — Reliability & SRE (~12h)

**Topics:** backups: logical (`pg_dump`/`pg_restore`) vs physical (`pg_basebackup`); **WAL archiving** and
**PITR** (`recovery_target_time`); **RPO/RTO** with reasoning; restore drills — a backup you never restored is
a hope; **load testing** with locust (realistic scenarios, ramp-up, think time); **profiling**: `py-spy`
(record/top/dump, flame graphs), `pg_stat_statements`, `EXPLAIN (ANALYZE, BUFFERS)`; fixing with
before/after numbers; **chaos**: Toxiproxy (latency, timeouts, down) — slow-but-succeeding dependencies and
why circuit breakers miss them (motivates bulkheads, B22); **SLIs, SLOs, error budgets** derived from
measurements; **runbooks**; on-call basics; **incident drills** and **blameless postmortems**; **threat
modeling** (STRIDE, data-flow diagrams); compliance scoping basics (PCI DSS SAQ levels, HIPAA safeguards) —
named precisely, never oversold; **audit logs** (append-only).

**Required before:** B22 (resilience), B24 (monitoring), 1C 2.6 (EXPLAIN), 1C 2.11 (triggers), B28 (pg_stat_statements).

### Lessons
- [ ] **B35.1 Backups and PITR** — PostgreSQL docs Chapter "Backup and Restore": "SQL Dump", "Continuous
  Archiving and Point-in-Time Recovery (PITR)" (setting up WAL archiving, making a base backup, recovering);
  reference `pg_basebackup`.
- [ ] **B35.2 Load testing** — locust docs: "Quick start", "Writing a locustfile", "Running without the web UI",
  "Increase performance" (FastHttpUser).
- [ ] **B35.3 Profiling** — py-spy README (record, top, dump; `--native`, running against a container);
  recap PostgreSQL `EXPLAIN` docs (BUFFERS option) and `pg_stat_statements`.
- [ ] **B35.4 Chaos** — Toxiproxy README (proxies, toxics: latency, timeout, bandwidth, reset_peer) and its HTTP API.
- [ ] **B35.5 SLOs** — Google SRE Book (sre.google/books) Ch.4 "Service Level Objectives"; SRE Workbook
  "Implementing SLOs" (error budgets, choosing SLIs).
- [ ] **B35.6 On-call & postmortems** — SRE Book Ch.11 "Being On-Call" and Ch.15 "Postmortem Culture: Learning
  from Failure"; Ch.14 "Managing Incidents".
- [ ] **B35.7 Threat modeling & compliance scoping** — OWASP "Threat Modeling Cheat Sheet" (STRIDE); PCI SSC
  "PCI DSS Quick Reference Guide" (scope, SAQ types); HHS.gov "Summary of the HIPAA Security Rule".

### Exercises
- [ ] **Ex B35.1 Restore drill.** `pg_dump` a database, corrupt a scratch copy, restore, and verify a business
  invariant (e.g. a report total) matches exactly. *Acceptance:* `docs/backup-dr-plan.md` with RPO/RTO **and the reasoning**.
- [ ] **Ex B35.2 PITR.** Enable WAL archiving, take a base backup, write rows, note the time, write a "bad" row,
  restore with `recovery_target_time` just before it. *Acceptance:* good rows present, bad row absent; RPO achieved written down.
- [ ] **Ex B35.3 Find the real bottleneck.** locust scenario against one of your earlier projects; profile with
  `py-spy` and `pg_stat_statements`. *Acceptance:* flame graph or top query captured; one fix; before/after
  p95 and throughput on the same load profile.
- [ ] **Ex B35.4 Slow dependency.** Put Toxiproxy between a service and its dependency; add 2s latency, 0%
  errors. *Acceptance:* observe the circuit breaker staying closed while worker pools saturate and unrelated
  endpoints' p95 climbs; notes explain why and what a bulkhead would change.
- [ ] **Ex B35.5 SLO from numbers.** From Ex B35.3's data write an SLI, an SLO and the monthly error budget.
  *Acceptance:* every number traces back to a measurement; a Prometheus query computes the SLI.
- [ ] **Ex B35.6 Runbook + drill + postmortem.** Write a one-page runbook for "success rate dropped", break a
  dependency, follow the runbook **blind**, then write a blameless postmortem. *Acceptance:* the postmortem
  lists what the runbook missed.
- [ ] **Ex B35.7 Threat model.** STRIDE on one earlier project's data-flow diagram. *Acceptance:* at least 6
  threats, each with a mitigation and a status (done / planned / accepted).

### Must be able to do / explain
- [ ] `pg_dump` vs PITR; the RPO each gives; what WAL archiving costs.
- [ ] How to derive RPO/RTO from business impact.
- [ ] How to find a bottleneck with a profiler instead of guessing.
- [ ] Why a circuit breaker doesn't help against slow-but-successful calls.
- [ ] SLI vs SLO vs SLA; error budgets and how they guide release decisions.
- [ ] How to run an incident and write a blameless postmortem.
- [ ] STRIDE; what keeps a system out of the highest PCI scope.

**Estimated hours:** ~12h

### Self-check interview questions
1. `pg_dump` vs PITR — what RPO does each give?
2. What does "a backup you've never restored is a hope" mean in practice?
3. How did you find your last bottleneck?
4. Your circuit breaker was closed and the system was still dying. Explain.
5. SLI vs SLO vs SLA?
6. What is an error budget used for?
7. What makes a postmortem "blameless"?
8. What does STRIDE stand for?
9. How does tokenization reduce PCI scope?

---

**Answers**
1. `pg_dump`: everything since the last dump can be lost (hours). PITR: replay WAL to any point, so RPO is seconds
   to minutes, at the cost of storing WAL and base backups.
2. Backups fail silently (wrong DB, missing permissions, corrupt files); only a regular, verified restore proves recoverability and measures RTO.
3. Load test with a realistic scenario, then profile under load (`py-spy` flame graph, `pg_stat_statements`, `EXPLAIN (ANALYZE, BUFFERS)`), fix one thing, re-measure on the same profile.
4. The dependency was slow, not failing — calls succeeded, so the breaker's error rate stayed low, but threads/connections were held for seconds, exhausting shared pools. Timeouts and bulkheads address it.
5. SLI: the measured indicator (e.g. % of requests < 800ms). SLO: the internal target for it over a window. SLA: an external contract with consequences, usually looser than the SLO.
6. The allowed amount of unreliability (1 − SLO); when it's healthy you ship faster, when it's spent you prioritize reliability work.
7. It focuses on systems and conditions, not individuals; assumes people acted reasonably with the information they had; produces action items.
8. Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.
9. Card numbers never touch your systems — the provider stores them and you only handle tokens — so your environment qualifies for a much smaller SAQ.

## Project P9 — PayFlow · Middle+ (~60h)

**Payment processing platform: idempotency, webhooks, ledger reconciliation, and the operational discipline
a system holding money needs.** Repo: `payflow/`.

### Goal
A platform accepts payments, handles a provider's async webhook confirmations reliably — a webhook can arrive
twice, arrive late, or arrive *before your own request finishes* — and keeps a ledger that is provably correct
under retries and duplicates. **The whole point in one sentence: the same payment request retried by a flaky
client must never charge twice.** The second half of the project is operational: secrets management, a threat
model, an SLO derived from measurements, a runbook, a live incident drill, and a disaster-recovery test with a
verified restore. PayFlow builds **on P6 LedgerBase**: it posts journal entries through `ledger-service`
instead of tracking money itself.

### Roles
| Role | Can | Cannot |
|---|---|---|
| `merchant` (machine, API key) | Create payment intents, request refunds, read own payments | Read other merchants' payments; alter status |
| `provider` (machine, HMAC) | POST to the webhook endpoint only | Anything else |
| `support` | Read payments, event history, audit log | Create, refund, alter |
| `finance` | Read everything, reconcile with ledger, export | Alter a payment |
| `ops` | Metrics, dashboards, alerts, run the runbook | Read sensitive payload bodies (state your choice) |

**Nobody can change a payment's status by hand** — status is derived from the webhook. Three auth mechanisms on
purpose: API key (merchant servers), HMAC over the raw body (provider webhooks), JWT (humans, from `auth-service`).

### Features
- [ ] `POST /payments` with mandatory `Idempotency-Key` + stored **request hash** + stored response;
      `INSERT … ON CONFLICT (idempotency_key) DO NOTHING RETURNING`
- [ ] HMAC-verified webhook intake over the raw body; idempotent on `provider_event_id` (JSONB **generated
      column** + UNIQUE; GIN `jsonb_path_ops` for support queries); handles out-of-order and early arrival
- [ ] Payment status reconciled **only from the webhook**
- [ ] Refunds with matching ledger entries; a refund never exceeds the payment
- [ ] Per-merchant **token-bucket rate limit** in Redis (Lua), `429` + `Retry-After`
- [ ] Secrets in **Vault** (KV): webhook secret + API keys; webhook secret **rotated live** with a grace window;
      **dynamic DB credentials**; fail-closed startup
- [ ] **Envelope encryption** of `payout_account_ref` via Vault transit; KEK rotated and DEKs rewrapped
- [ ] Append-only audit log (`payment_audit`, trigger-protected as in LedgerBase)
- [ ] **gRPC** `PostJournalEntry` on `ledger-service` with a deadline + circuit breaker; REST vs gRPC measured
- [ ] **Terraform** cloud foundation for P10 AtlasMarket: remote state + lock, IAM role, VPC/subnets, security
      groups; `plan` in CI; `destroy` + re-`apply` once
- [ ] Backup/DR for LedgerBase: `pg_dump` restore **and** PITR, trial balance verified after both
- [ ] locust load test, bottleneck found with `py-spy` / `pg_stat_statements` / `EXPLAIN (ANALYZE, BUFFERS)`, fixed with before/after numbers
- [ ] Toxiproxy 2s latency into `ledger-service`: breaker stays closed, pools saturate — written down
- [ ] SLO + error budget from measured numbers; one-page runbook; live drill; blameless postmortem
- [ ] Docs: threat model, PCI scope note, HIPAA considerations note (for CarePoint), transport decision record,
      rate-limiting notes, backup/DR plan

### API
| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/payments` | API key | Requires `Idempotency-Key` |
| POST | `/webhooks/provider` | HMAC signature | Idempotent on `provider_event_id` |
| POST | `/payments/{id}/refund` | API key | |
| GET | `/payments/{id}` | API key / support | No cache (financial state) |
| GET | `/metrics` | internal | SLO metrics |

### Domain model (sketch)
`merchants(id, name, api_key_hash, rate_limit_per_min, payout_account_ref_enc bytea, payout_key_version)`;
`payment_intents(id, idempotency_key UNIQUE, request_hash, amount_cents, status, journal_entry_id, response_body
jsonb, created_at)`; `webhook_events(id, payload jsonb, provider_event_id GENERATED … STORED UNIQUE, event_type
GENERATED …, processed_at, received_at)`; `refunds(id, payment_intent_id, amount_cents, journal_entry_id,
created_at)`; `payment_audit(id, payment_intent_id, from_status, to_status, actor, source, occurred_at)` (append-only).

### Deliberately NOT used
Redis for idempotency (must be durable and transactional with the payment row — the most important "why not" in
the track); a queue in front of `/payments` (merchant needs a synchronous answer); cache on `GET /payments/{id}`;
GraphQL/gateway (one resource, machine clients); a real payment provider (the lesson is the protocol).

### Tech stack
| Tool | Taught in |
|---|---|
| FastAPI | B4 |
| SQLAlchemy 2.0, Alembic | B5 |
| `ON CONFLICT … RETURNING`, JSONB, generated columns, GIN | 1C 2.3, 1C 2.4, 1C 2.5; B34 |
| Append-only triggers | 1C 2.11 (used in P6) |
| Idempotency keys, HMAC webhooks, API keys | B34 |
| Redis + Lua token bucket | B12 |
| HashiCorp Vault (KV, database, transit) | B31 |
| gRPC, protobuf, grpcio-tools | B32 |
| Circuit breaker, retries, timeouts | B22 |
| Terraform, IAM, VPC, security groups | B33 |
| GitHub Actions (tests, `terraform plan`) | B9, B23, B33 |
| Prometheus, Grafana, Sentry | B24 |
| locust, py-spy, Toxiproxy, `pg_dump`, WAL archiving, `pg_basebackup`, PITR | B35 |
| SLOs, runbook, postmortem, STRIDE, PCI/HIPAA scoping | B35 |
| Docker Compose | B3 |
| pytest (concurrency tests) | B8, 1A.8, 1A.11 |

### Required knowledge
B3, B4, B5, B7, B8, B9, B12, B22, B23, B24, B31, B32, B33, B34, B35; 1C 2.3, 2.4, 2.5, 2.6, 2.11; 1A.11–1A.12.
Reuses: P6 LedgerBase `ledger-service`, circuit breaker and observability stack.

### Milestones
- [ ] **M1 Idempotent payments** — models, `POST /payments` with key + request hash, `ON CONFLICT DO NOTHING
      RETURNING`; concurrent-duplicate test (one charge, identical responses). Tag `v0.1-idempotency`
- [ ] **M2 Webhooks** — mock provider; HMAC over raw body; idempotent on `provider_event_id`; status from webhook;
      early/out-of-order arrival handled; ledger entry via `ledger-service`. Tag `v0.2-webhooks`
- [ ] **M3 Refunds, API keys, rate limits, audit** — refunds + ledger entries; hashed API keys; Redis Lua token
      bucket; `docs/rate-limiting-notes.md`; append-only audit. Tag `v0.3-refunds`
- [ ] **M4 Secrets & encryption** — Vault in Compose; KV secrets; live webhook-secret rotation with grace window;
      dynamic DB credentials; envelope encryption + KEK rotation. Tag `v0.4-vault`
- [ ] **M5 gRPC** — `PostJournalEntry` with deadline + breaker; status-code mapping; REST vs gRPC measured;
      `docs/transport-decision-record.md`. Tag `v0.5-grpc`
- [ ] **M6 Backup/DR** — `pg_dump` restore + PITR on LedgerBase, trial balance verified; `docs/backup-dr-plan.md`. Tag `v0.6-dr`
- [ ] **M7 Terraform foundation** — `infra/` (network, IAM, security groups, remote state); `plan` in CI;
      destroy + re-apply; budget alert set. Tag `v0.7-infra`
- [ ] **M8 Load, profile, chaos, SLO, drill** — locust; profiler-found bottleneck fixed; Toxiproxy latency run;
      SLO + error budget; runbook; live drill; blameless postmortem; threat model + PCI/HIPAA notes. Tag `v1.0-payflow`

### Definition of done
- [ ] Two concurrent identical requests → one charge, identical responses; key reused with a different body → explicit error
- [ ] Same `provider_event_id` 3× → exactly one ledger entry; invalid signature rejected and logged
- [ ] Webhook arriving before the API call commits is handled
- [ ] Refunds correct in the ledger; never exceed the original
- [ ] No secrets in `.env`; webhook secret rotated with zero dropped webhooks; DB creds expire and renew without restart
- [ ] PII column contains only ciphertext; old rows decrypt after KEK rotation
- [ ] Merchant at limit gets `429` + `Retry-After`; other merchants unaffected; Lua script atomic under concurrency
- [ ] gRPC: balanced entry posts; unbalanced → `INVALID_ARGUMENT`; 200ms deadline vs slow ledger → fast `DEADLINE_EXCEEDED`
- [ ] Restore from dump and PITR both verified by a reconciling trial balance
- [ ] Terraform: clean `plan` after `apply`; destroy/apply reproduces resources; DB SG admits only the gateway SG
- [ ] Bottleneck shown in a flame graph or `pg_stat_statements` row, with before/after on the same load profile
- [ ] Toxiproxy run documented; SLO derived from numbers; runbook used blind; postmortem lists what it missed
- [ ] All docs listed in Features exist

**Estimated hours:** ~60h (+ ~10h optional ML extension)

### OPTIONAL extensions
- **Fraud-signal model** (Track 3 → ML Zoomcamp modules 3–6, MLOps Zoomcamp modules 2 and 5): an unsupervised
  anomaly model (e.g. IsolationForest) on amount-vs-history, velocity and time-of-day features, tracked in MLflow;
  prediction-latency histogram and a drift signal (rolling mean score out of band) in Prometheus/Grafana;
  `docs/fraud-signal-notes.md` stating what it can and cannot detect. A signal for human review, never an automatic block.

### Interview questions
1. Walk me through your idempotency implementation end to end — and why the request hash?
2. Why must webhook processing be idempotent separately from the payment request?
3. Why is Redis the wrong place for idempotency records here, but fine for your rate limiter?
4. How do you rotate a webhook signing secret without dropping a single webhook?
5. Your circuit breaker was closed and the system was still dying. Explain what you saw with Toxiproxy.

---

**Short answers**
1. Client sends `Idempotency-Key`; the server hashes the request, inserts `(key, hash)` with `ON CONFLICT DO
   NOTHING RETURNING`; the winner processes and stores the response, losers/retries return the stored response;
   a matching key with a different hash is rejected, so a client bug can't silently receive another request's result.
2. They protect against different retriers: request idempotency against *your client* retrying, webhook
   idempotency against *the provider* redelivering events. Different keys, different tables; one doesn't cover the other.
3. Money idempotency must be durable and committed atomically with the payment row; Redis can lose writes and can't
   join the Postgres transaction. Rate-limit counters may be lost without harm, so Redis's speed is the right trade there.
4. Add the new secret version, verify signatures under both old and new during a grace window while the provider
   switches, then retire the old one; tests prove both verify inside the window and only the new one after.
5. With 2s latency and no errors, every call succeeded, so the breaker's failure rate stayed at zero; but each call
   held a worker for 2s, the pool filled, and unrelated endpoints' p95 rose. Fix: tight timeouts/deadlines and a
   bulkhead (separate pool) for the ledger dependency.


## Module B36 — GraphQL (~8h)

**Topics:** the GraphQL model (schema, types, queries, mutations, resolvers,
execution), schema-first vs code-first, Strawberry (code-first, type hints)
mounted in FastAPI, input types and typed errors, the N+1 problem in
resolvers and DataLoader batching, cursor-based (connection) pagination,
per-field authorization, query depth and complexity limits, and when a
GraphQL backend-for-frontend (BFF) beats REST or gRPC.

### Theory
- [ ] **36.1 The GraphQL model** — graphql.org/learn: "Introduction", "Queries", "Mutations", "Schemas and Types", "Execution".
- [ ] **36.2 Strawberry + FastAPI** — strawberry.rocks/docs: "Getting started", "Types → Object types", "Types → Input types", "Mutations", "Integrations → FastAPI".
- [ ] **36.3 N+1 and DataLoader** — strawberry.rocks/docs "Guides → DataLoaders"; the original `graphql/dataloader` README on GitHub (the "Batching" and "Caching" sections).
- [ ] **36.4 Pagination, errors, auth, limits** — graphql.org/learn "Pagination"; strawberry.rocks/docs "Guides → Permissions", "Guides → Errors", "Extensions → QueryDepthLimiter".
- [ ] **36.5 GraphQL vs REST vs gRPC, the BFF pattern** — Sam Newman, "Backends For Frontends" (samnewman.io/patterns/architectural/bff/); graphql.org/learn "Best Practices" (overview page).

### Exercises
- [ ] **Ex 36.1 — Read-only catalog schema.** Over a copy of the StockPilot
  catalog tables, expose `Product`, `Category`, `Supplier` types and the
  queries `product(id)` and `products`. Mount it at `/graphql` in a FastAPI
  app. **Acceptance:** GraphiQL loads; the printed SDL is committed as
  `schema.graphql`; a pytest test runs one query through the test client.
- [ ] **Ex 36.2 — Mutations and typed errors.** Add `createProduct(input:
  ProductInput!)`. Validation failures (negative price, unknown category) come
  back as a union result (`CreateProductSuccess | ValidationError`), not as a
  500. **Acceptance:** one test per error type, and one for success.
- [ ] **Ex 36.3 — Measure the N+1, then remove it.** Query 50 products with
  their nested `supplier { name }`. Count SQL statements with a SQLAlchemy
  event listener. Then add a DataLoader for suppliers. **Acceptance:** a test
  asserts 51 statements before and 2 after. Put both numbers in `notes.md`.
- [ ] **Ex 36.4 — Field-level authorization.** Only the `owner` role may call
  `createProduct`, and only `owner` may see `Product.costPriceCents`.
  **Acceptance:** tests for anonymous, `staff` and `owner` callers; a
  forbidden field returns a GraphQL error without leaking data.
- [ ] **Ex 36.5 — Cursor pagination and depth limit.** Change `products` into a
  connection (`first`, `after`, `edges`, `pageInfo`) backed by keyset
  pagination. Add a depth limit of 5. **Acceptance:** paging through 1,000 rows
  returns each row exactly once; a hand-crafted query nested 10 levels deep is
  rejected before any resolver runs.
- [ ] **Ex 36.6 — Transport decision record.** Write
  `docs/transport-decision-record.md` comparing REST, gRPC and GraphQL for
  three clients: a public partner API, an internal service-to-service call,
  and a product page that composes data from three services. Choose one
  transport per client and give a reason for each.

### Must be able to do / explain
- [ ] Explain how a GraphQL query is parsed, validated and executed resolver by resolver.
- [ ] Build a Strawberry schema with queries, mutations, input types and typed errors.
- [ ] Show the N+1 problem in a resolver tree and fix it with a DataLoader, with numbers.
- [ ] Implement cursor pagination and explain why offsets fit GraphQL connections badly.
- [ ] Protect a GraphQL API from expensive queries (depth/complexity limits, timeouts).
- [ ] Argue when to use GraphQL (BFF), REST (resources) or gRPC (internal RPC).

**Estimated time:** ~8h

### Self-check interview questions
1. What problem does GraphQL solve that REST does not, and what new problems does it create?
2. What is the N+1 problem in GraphQL, and how does DataLoader solve it?
3. Why is HTTP caching harder with GraphQL than with REST?
4. How would you stop a client sending a query that brings down your database?
5. Where should authorization live in a GraphQL API?
6. What is a backend-for-frontend, and why does GraphQL suit that role well?
7. Why do GraphQL APIs usually return HTTP 200 even when there are errors, and how do clients detect failure?

---

**Answers**
1. The client asks for exactly the fields it needs, in one round trip, across
   several resources, against a typed schema, so there is no over-fetching,
   under-fetching or chatty client. The costs: resolver-level N+1, harder
   caching, expensive queries that clients control, and error handling that is
   no longer expressed through status codes.
2. Each nested resolver runs once per parent object, so a list of N parents
   causes 1 + N backend calls. A DataLoader collects all the keys requested in
   one event-loop tick and resolves them in one batched call, caching results
   per request. That turns N + 1 calls into 2.
3. Most queries are POSTs to a single URL with different bodies, so URL-based
   CDN and browser caches cannot key on them. The usual workarounds are
   persisted queries sent as GET with a hash, response caching keyed on the
   query plus variables, or caching at the resolver or DataLoader level.
4. Depth limits, complexity/cost analysis, pagination with maximum page sizes,
   timeouts, rate limiting per client, and allow-listed persisted queries for
   first-party clients.
5. In the business or service layer the resolvers call, not in the transport
   layer, with per-field permission checks for sensitive fields. The same rules
   must apply whether data is reached through GraphQL, REST or a background job.
6. A BFF is an API layer owned by one client team that composes backend
   services into exactly the shape one UI needs. GraphQL fits because the
   client describes that shape itself, so the BFF does not need a new endpoint
   for every screen.
7. The HTTP request itself succeeded, and a response can contain partial data
   plus errors. Clients check the top-level `errors` array, or use typed error
   unions in the schema for expected business errors.

---

## Module B37 — Multi-tenancy & release engineering (~6h)

**Topics:** tenant isolation models (database-per-tenant, schema-per-tenant,
shared schema with a `tenant_id` column) and their trade-offs; PostgreSQL
Row-Level Security (policies, `USING` vs `WITH CHECK`, `FORCE ROW LEVEL
SECURITY`, `BYPASSRLS` roles); passing the tenant with `SET LOCAL` and
`current_setting()`; why `SET` without `LOCAL` leaks through a
transaction-mode pool; feature flags (release, ops, experiment and
permission toggles); stable per-user bucketing by hashing; dark launches;
canary releases watched per cohort, with abort rules.

### Theory
- [ ] **37.1 Tenant isolation models** — Microsoft Azure Architecture Center, "Multitenant SaaS database tenancy patterns" (the sections on standalone, database-per-tenant, and multi-tenant database patterns).
- [ ] **37.2 PostgreSQL Row-Level Security** — PostgreSQL docs, "Row Security Policies" (Chapter 5, Data Definition); SQL command reference pages `CREATE POLICY`, `ALTER TABLE … ENABLE/FORCE ROW LEVEL SECURITY`, `SET` (the `LOCAL` option); "System Administration Functions → `current_setting`".
- [ ] **37.3 RLS and connection pooling** — PgBouncer docs, "Features" page (the table of session features that are unsupported in transaction pooling mode).
- [ ] **37.4 Feature flags** — Pete Hodgson, "Feature Toggles (aka Feature Flags)" on martinfowler.com (read the categories of toggles and "Implementation Techniques").
- [ ] **37.5 Canary releases and dark launches** — martinfowler.com/bliki "CanaryRelease" and "DarkLaunching"; Google *The Site Reliability Workbook*, chapter "Canarying Releases" (sre.google/workbook).

### Exercises
- [ ] **Ex 37.1 — RLS lab in psql.** Create `products(id, vendor_id, name)`, an
  owner role that runs migrations and an `app` role. Enable and force RLS with
  a policy that reads `current_setting('app.vendor_id')`. **Acceptance:** a SQL
  script shows that (a) with `SET LOCAL app.vendor_id = 1`, a query with no
  `WHERE` returns only vendor 1's rows; (b) an `INSERT` for vendor 2 is
  rejected by `WITH CHECK`; (c) with the setting missing, the query returns 0
  rows and does not error.
- [ ] **Ex 37.2 — The pooled-connection leak.** Put PgBouncer in transaction
  mode in front of the database. Show that a plain `SET app.vendor_id` from
  request A is visible to request B on the same server connection, then fix it
  with `SET LOCAL` inside the transaction. **Acceptance:** a written repro
  (`notes.md`) and an automated test that fails with `SET` and passes with
  `SET LOCAL`.
- [ ] **Ex 37.3 — Hand-rolled feature flags.** Create a `feature_flags(name,
  enabled, rollout_percent)` table and an `is_enabled(flag, user_id)`
  function that hashes `flag + user_id` into 100 buckets. **Acceptance:**
  Hypothesis tests prove that (a) the same user gets the same answer on every
  call; (b) raising the rollout from 10% to 20% never switches an
  already-enabled user off; (c) across 10,000 users, 10% ± 1.5% are enabled.
- [ ] **Ex 37.4 — Canary by cohort.** Export `checkout_requests_total{cohort="new"|"old", outcome}`
  (two cohort values only, to keep cardinality bounded) and build a Grafana
  panel of success rate per cohort. Write a ramp runbook (0 → 10 → 50 → 100%)
  with an explicit abort rule, for example "new-cohort error rate greater than
  old-cohort rate + 1 point for 10 minutes". **Acceptance:** you run a ramp,
  inject a failure into the new path only, and show the dashboard catching it.
- [ ] **Ex 37.5 — Multi-tenancy decision record.** Write
  `docs/multi-tenancy-decision-record.md` comparing shared schema + RLS,
  schema-per-tenant and database-per-tenant. Cover isolation strength,
  migrations, noisy neighbours, per-tenant backup/restore, cost, and the
  number of tenants at which each model breaks.

### Must be able to do / explain
- [ ] Choose a tenant isolation model for a given product and defend it.
- [ ] Write RLS policies (`USING` and `WITH CHECK`) and test that a forgotten `WHERE` leaks nothing.
- [ ] Explain why `SET LOCAL` is safe behind a transaction-mode pool and `SET` is not.
- [ ] Explain which roles bypass RLS (table owner without `FORCE`, superuser, `BYPASSRLS`) and why that matters for migrations.
- [ ] Implement stable percentage rollout and explain why a random roll per request is wrong.
- [ ] Run a canary with per-cohort metrics and a pre-agreed abort rule.

**Estimated time:** ~6h

### Self-check interview questions
1. Compare shared-schema, schema-per-tenant and database-per-tenant multi-tenancy.
2. How does Postgres Row-Level Security work, and what is the difference between `USING` and `WITH CHECK`?
3. Why must you use `SET LOCAL` rather than `SET` when PgBouncer runs in transaction mode?
4. Which database roles are not subject to RLS, and how do you make sure the application role is?
5. How do you make a percentage rollout stable per user?
6. What is the difference between a dark launch, a canary release and an A/B test?
7. What metrics do you watch during a canary, and when do you roll back?
8. What is the cost of leaving feature flags in the code forever?

---

**Answers**
1. Shared schema is the cheapest and simplest to migrate, but isolation depends
   on every query (or RLS), and noisy neighbours share resources.
   Schema-per-tenant gives stronger logical isolation and easy per-tenant
   export, but migrations multiply and the catalog grows. Database-per-tenant
   gives the strongest isolation, per-tenant backup/restore and placement, and
   the highest operational cost. It suits a few large tenants, not thousands of
   small ones.
2. With RLS enabled, every row access by a role that is subject to RLS is
   filtered by the table's policies. `USING` filters which existing rows are
   visible to SELECT/UPDATE/DELETE. `WITH CHECK` validates rows being written by
   INSERT/UPDATE. With no policy at all, access defaults to deny.
3. In transaction mode, a server connection goes back to the pool at the end of
   each transaction and the next client may get it. `SET` lasts for the whole
   session, so the tenant id survives onto someone else's request. `SET LOCAL`
   is reset when the transaction ends.
4. Superusers, roles with `BYPASSRLS`, and the table owner unless `FORCE ROW
   LEVEL SECURITY` is set. The application should connect as a separate
   non-owner role with no `BYPASSRLS`. Migrations run as the owner.
5. Hash a stable key (flag name + user id) into buckets (for example 0–99) and
   enable the flag when the bucket is below the rollout percentage. Raising the
   percentage then only adds users.
6. A dark launch runs new code paths in production without users seeing the
   results, for example shadow traffic. A canary exposes a small, growing
   share of real users to the new version, to catch problems. An A/B test
   splits users on purpose, to measure a business metric with statistics.
7. Error rate, latency percentiles and saturation for the new cohort compared
   with the old one, plus key business metrics such as checkout success. Roll
   back when a threshold agreed before the ramp is crossed.
8. Every flag doubles the paths through the code. Old flags become dead code,
   confuse readers and can be switched by accident. Release flags should have
   an owner and an expiry date and be removed after the full rollout.

---

## Module B38 — System design fundamentals (~20h)

**Topics:** a repeatable interview framework (clarify requirements →
estimate → API → data model → high-level design → deep dive → trade-offs);
back-of-envelope numbers and latency numbers; vertical vs horizontal scaling;
load balancers, caches and CDNs; queues and asynchronous processing;
replication, partitioning/sharding and consistent hashing (recap from
B28); consistency models (strong, read-your-writes, eventual) and CAP/PACELC;
2PC vs saga for cross-service consistency; unique ID generation; rate limiting
at scale; behavioral interviews with the STAR method.

This module turns the whole of Track 2 into interview answers. Problems come
from `roadmap_plan/system-design-problems.md` (SD1–SD20). Behavioral practice
comes from `roadmap_plan/behavioral-interview-questions.md`. For every SD
problem use the 6-step skeleton at the top of that file, and point to a
system you actually built as evidence whenever one applies.

### Theory
- [ ] **38.1 The interview framework** — Alex Xu, *System Design Interview* Vol. 1, ch.3 "A Framework for System Design Interviews"; the 6-step skeleton at the top of `system-design-problems.md`.
- [ ] **38.2 Back-of-the-envelope estimation** — Xu Vol. 1, ch.2 "Back-of-the-envelope Estimation"; "Latency Numbers Every Programmer Should Know" (the table in *The System Design Primer*, "Appendix").
- [ ] **38.3 Scaling from one server** — Xu Vol. 1, ch.1 "Scale From Zero To Millions Of Users"; *The System Design Primer* (github.com/donnemartin/system-design-primer): "Performance vs scalability", "Latency vs throughput", "Availability vs consistency".
- [ ] **38.4 Data at scale** — Kleppmann, *Designing Data-Intensive Applications*: ch.5 "Replication", ch.6 "Partitioning", ch.9 "Consistency and Consensus" (the linearizability and ordering sections); Primer: "Consistency patterns", "Availability patterns", "Database".
- [ ] **38.5 Caches, CDNs, queues** — Primer: "Domain name system", "Content delivery network", "Load balancer", "Cache", "Asynchronism"; ByteByteGo (blog.bytebytego.com) articles on caching strategies.
- [ ] **38.6 Distributed transactions: 2PC vs saga** — DDIA ch.9 "Atomic Commit and Two-Phase Commit (2PC)" and "Distributed Transactions in Practice"; microservices.io "Pattern: Saga".
- [ ] **38.7 Classic building blocks** — Xu Vol. 1: ch.4 "Design a Rate Limiter", ch.5 "Design Consistent Hashing", ch.6 "Design a Key-Value Store", ch.7 "Design a Unique ID Generator in Distributed Systems".
- [ ] **38.8 Larger case studies** — Xu Vol. 2: "Proximity Service", "Nearby Friends", "Distributed Message Queue", "Payment System", "Hotel Reservation System" (read the chapters that match the SD problems below before attempting them).
- [ ] **38.9 Behavioral interviews** — the intro of `behavioral-interview-questions.md` (the STAR method, and why a real story beats a generic one).

### Exercises
Work each SD problem on paper or a whiteboard, **45 minutes, no notes**. Then
write it up in `docs/system-design/SDn.md` using the 6 steps and compare it
with Xu, the Primer or DDIA. Finish by writing down 2–3 things you would
defend differently next time.

- [ ] **Ex 38.1 — Warm-ups** (compare with what you built in B12 and O1/O2 if done):
  - [ ] SD1 — URL Shortener
  - [ ] SD2 — Rate Limiter
- [ ] **Ex 38.2 — Distributed primitives** (evidence: B28, B29, P8):
  - [ ] SD3 — Distributed Cache
  - [ ] SD4 — Key-Value Store (Dynamo-style)
  - [ ] SD6 — Unique ID Generator (Snowflake-style)
  - [ ] SD14 — Distributed Job Scheduler
- [ ] **Ex 38.3 — Real-time and fan-out** (evidence: P7 FleetTrack, B26):
  - [ ] SD7 — News Feed / Timeline
  - [ ] SD8 — Chat System
  - [ ] SD9 — Notification System
- [ ] **Ex 38.4 — Search-shaped systems** (evidence: P8 DocuVault, B27):
  - [ ] SD5 — Web Crawler
  - [ ] SD15 — Typeahead / Autocomplete
  - [ ] SD16 — Proximity / Nearby Search
- [ ] **Ex 38.5 — Correctness under concurrency** (evidence: P6 LedgerBase, P9 PayFlow, B7, B34):
  - [ ] SD12 — Ticket-Booking System
  - [ ] SD18 — Payment System
- [ ] **Ex 38.6 — Infrastructure and large scale** (evidence: P5, P6, P8):
  - [ ] SD10 — Video Streaming Platform
  - [ ] SD11 — Ride-Sharing Service
  - [ ] SD13 — Collaborative Document Editor
  - [ ] SD17 — Distributed File Storage
  - [ ] SD19 — Distributed Logging & Metrics Pipeline
- [ ] **Ex 38.7 — Estimation drill.** For 5 SD problems of your choice, write
  the numbers alone on one page each: daily active users, read/write QPS
  (average and peak), storage per year and bandwidth. Then have a friend (or
  yourself a week later) change one input by 10× and redo it in under 5
  minutes.
- [ ] **Ex 38.8 — Behavioral bank.** For every question in
  `behavioral-interview-questions.md`, write a 4–6 sentence STAR answer
  based on a real moment from P1–P9 (a postmortem, a decision record, a bug
  you found). **Acceptance:** you can answer any question out loud in under
  90 seconds without notes. Tick one category at a time:
  - [ ] Dealing with mistakes, bugs, and being wrong
  - [ ] Scope, prioritization, and saying no
  - [ ] Working under pressure / production incidents
  - [ ] Collaboration, communication, and technical disagreement
  - [ ] Ownership, growth, and reflection
  - [ ] System-level thinking and trade-offs
- [ ] **Ex 38.9 — Mock interviews.** Do 3 recorded mocks with a peer or on a
  mock-interview platform: one system design, one behavioral, one mixed. After
  each, write a one-paragraph self-review: what you missed, what you rambled
  about, and what you would say first next time.

(SD20 "Design AtlasMarket, From Scratch" is the closing milestone of P10.)

### Must be able to do / explain
- [ ] Run the 6-step framework on an unseen problem in 45 minutes.
- [ ] Produce back-of-envelope numbers quickly and use them to justify design choices.
- [ ] Explain replication vs partitioning, leader-based vs leaderless, and consistent hashing.
- [ ] Explain strong vs eventual consistency and CAP/PACELC with a concrete example.
- [ ] Explain why sagas plus an outbox are usually chosen over 2PC across services.
- [ ] Place caches, CDNs, queues and rate limiters in a design and say what each protects.
- [ ] Tell STAR stories from your own projects for each behavioral category.

**Estimated time:** ~20h

### Self-check interview questions
1. Walk me through how you approach a system design interview question.
2. Estimate storage for a URL shortener that creates 100M new links per month for 5 years.
3. What is the difference between replication and partitioning, and why do you usually need both?
4. Explain the CAP theorem. Why is PACELC often more useful in practice?
5. Why not use a distributed transaction (2PC) across microservices?
6. Where would you put a cache in a read-heavy system, and what could go wrong?
7. How would you generate unique, roughly time-ordered IDs across many servers?
8. How does a rate limiter stay correct when it runs on several gateway instances?
9. What is the STAR method, and what makes a behavioral answer convincing?

---

**Answers**
1. Clarify the functional and non-functional requirements and the scope,
   estimate scale, sketch the API and data model, draw a high-level design,
   deep-dive the hardest part with numbers, and finish with trade-offs and
   what you would measure. Keep checking in with the interviewer as you go.
2. 100M × 12 × 5 = 6B links. At roughly 500 bytes per record (code, URL,
   metadata) that is about 3 TB, before indexes and replication. Multiply by
   the replication factor (for example 3×, about 9 TB). It is the order of
   magnitude that matters, not the exact number.
3. Replication copies the same data to several nodes for availability and read
   scaling. Partitioning splits the data across nodes so that it fits and
   writes scale. Large systems partition for size and replicate each partition
   for fault tolerance.
4. During a network partition you must choose between consistency and
   availability. PACELC adds that even when there is no partition, you trade
   latency against consistency. That trade-off applies to every request, so it
   is the one you design for day to day.
5. 2PC blocks when the coordinator fails, holds locks across network calls,
   ties together the availability of every participant, and is poorly
   supported by brokers and many databases. Sagas made of local transactions
   plus an outbox and idempotent consumers give eventual consistency with
   explicit compensations.
6. Cache-aside in front of the database, a CDN for static and cacheable
   content, and possibly an in-process cache for hot configuration. Risks:
   stale data, invalidation bugs, cache stampedes on expiry, a cold cache after
   a restart, and caching data that must be exact, such as balances.
7. A Snowflake-style ID: timestamp bits + machine/worker id bits + a
   per-millisecond sequence. The IDs sort roughly by time, need no
   coordination per ID, and need clock-skew handling. The alternatives are
   database sequences with ranges handed out in blocks, or UUIDv7.
8. The counters live in shared state (for example Redis) rather than in each
   instance's memory, and they are updated atomically (a Lua script or
   INCR + EXPIRE). You accept a small inaccuracy, or use local token buckets
   with periodic synchronization when latency matters more.
9. Situation, Task, Action, Result. A convincing answer is specific and true,
   says what *you* did, includes what went wrong, and ends with a measurable
   result and what you learned.

---
## Project P10 — AtlasMarket · Middle+ (~70h)

**Multi-vendor e-commerce marketplace: the capstone of Track 2.**

> **This is an integration exercise, not a rewrite.** Import and adapt
> logic from P1–P9 wherever it already solves the problem. If you find
> yourself designing something from scratch, first check which earlier
> project already did it.

### Goal
Independent vendors list products, manage their own inventory and receive
payouts on a shared marketplace. Customers browse one unified catalog,
check out across several vendors in **one** order, and track fulfillment.
The project brings everything built so far together:

| Capability | Comes from |
|---|---|
| Catalog & inventory | P1 StockPilot |
| Checkout logic | P2 QuickServe POS |
| Fulfillment status | P4 WareFlow |
| Auth (`auth-service`) | P5 CarePoint |
| Per-vendor payout ledger | P6 LedgerBase |
| Event-driven order flow, outbox | P7 FleetTrack |
| Search | P8 DocuVault |
| Idempotent payments | P9 PayFlow |

**Architecture:** one Nginx gateway in front of five services: `auth-service`
(P5), `catalog-service` (P1 lineage, vendor-scoped, P8 ES search),
`order-service` (P2 checkout + P4-style fulfillment + P7 outbox),
`payment-service` (P9, idempotent) and `ledger-service` (P6, per-vendor
payouts). There is **one** PostgreSQL database, not one per service (you
write down why).

**Roles:** `customer`, `vendor_staff`, `vendor_owner`, `marketplace_ops`,
`finance`, `platform_admin`. The rule that defines the project is **vendor
isolation**: a vendor sees its own slice of an order and nothing else.
That fragmentation is a security boundary and is tested as one.

**Domain delta:** `vendors(id, name, payout_account_ref, status)`,
`vendor_staff(user_id, vendor_id, role)`, `products(..., vendor_id)`,
`orders(id, customer_id, status, created_at)`, `order_vendor_groups(id,
order_id, vendor_id, status, journal_entry_id)`, and one `payments` row per
order (via PayFlow). One payment, many vendor groups: that asymmetry is the
design problem.

**Checkout flow (be able to narrate it):**
1. The cart is submitted.
2. `order-service` validates stock per line, per vendor.
3. The order is created and split into `order_vendor_groups`, and outbox rows
   for `OrderPlaced` are written, all **in one transaction**.
4. `payment-service` charges **once**, idempotently (Idempotency-Key = the
   order id, generated by the client for a new order).
5. When the webhook confirms payment, `ledger-service` posts per-vendor ledger
   entries.
6. The outbox relay publishes the events, and each vendor's fulfillment view
   updates.
7. The customer sees one order; each vendor sees only its own group.

### Features
- [ ] Five services behind one Nginx gateway, each traced back to its origin project in `docs/architecture.md`
- [ ] Vendor onboarding; vendor-scoped product and stock management
- [ ] Unified catalog search across vendors (Elasticsearch, derived and rebuildable)
- [ ] **Multi-vendor checkout: one cart, one payment, N vendor groups, N ledger entries**
- [ ] Per-vendor fulfillment status on `order_vendor_groups`
- [ ] Vendor isolation enforced **twice**: a `vendor_id` filter in every query **and** Postgres RLS (`SET LOCAL app.vendor_id` per transaction)
- [ ] **Bulkhead**: one bounded connection pool per downstream service at the gateway, sized from `locust` numbers
- [ ] Nginx `limit_req` per IP and per API key, as the outermost of four protection layers (rate limit → bulkhead → breaker → retry)
- [ ] Hand-rolled feature flag with stable per-user bucketing; checkout shipped dark, then ramped 10% → 100% while watching Grafana by cohort
- [ ] One OpenTelemetry trace for one checkout across all five services, the outbox relay and the payment webhook
- [ ] Gateway + `catalog-service` on **real cloud** built only by Terraform: managed Postgres in a private subnet, least-privilege IAM, scoped security groups, HTTPS + HSTS, static assets on object storage + CDN
- [ ] GraphQL BFF (Strawberry + DataLoader) for the product page, with the N+1 measured (a stretch goal in the original spec; core here because B36 teaches it)
- [ ] Written artefacts: `docs/architecture.md`, `docs/multi-tenancy-decision-record.md`, `docs/distributed-transactions.md` (why not 2PC), `docs/cart-persistence.md` (the Redis hash design and when it becomes necessary), `docs/cloud-deployment-notes.md` (IAM, VPC, the real monthly bill), `docs/atlasmarket-roadmap-post-track2.md` (the deferred list)

**Explicitly NOT built (write this list first):** reviews/ratings,
recommendation engine, vendor analytics dashboard (see Track 3 DE Zoomcamp),
cross-vendor promotions, returns, vendor fraud systems, search relevance
tuning, Kubernetes in production, a service mesh, a managed flag service,
per-service databases, 2PC.

### Tech stack
| Tool / technique | Taught in |
|---|---|
| FastAPI services (+ Django/DRF where reused) | B4, B10, B11 |
| PostgreSQL, SQLAlchemy, Alembic | 1C Part 1–2, B5 |
| Postgres Row-Level Security, `SET LOCAL` | B37 |
| Nginx gateway, `limit_req`, TLS | B17 |
| Auth service (JWT RS256/JWKS) | B6, B18 |
| Elasticsearch (vendor-scoped index) | B27 |
| RabbitMQ + transactional outbox | B15, B25 |
| Idempotency keys, HMAC webhooks | B34 |
| Retry, circuit breaker, bulkhead | B22 |
| Feature flags, canary by cohort | B37 |
| Prometheus, Grafana, OpenTelemetry | B24 |
| `locust` load testing | B35 |
| Terraform, IAM, VPC, managed Postgres, CDN | B33 |
| Strawberry GraphQL + DataLoader | B36 |
| Docker Compose, GitHub Actions (`terraform plan` in CI) | B3, B9, B23 |
| pytest, factory_boy | 1A.8, B8 |

### Required knowledge
- P1–P9 finished (their code is reused, not rewritten).
- Track 2 modules B1–B38, especially B17, B22, B24, B25, B27, B33–B38.
- Track 1C Part 2 (transactions, locking, indexes).

### Milestones
- [ ] **M1 — Architecture map & catalog.** Write `docs/architecture.md` first,
  mapping every service to its origin project, and write the deferred list.
  Add `vendors`/`vendor_staff`, `products.vendor_id`, and the vendor
  onboarding endpoint. Add RLS policies on `products`, `order_vendor_groups`
  and the payout tables, and the "forgotten WHERE" test. Write
  `docs/multi-tenancy-decision-record.md`. Add a vendor-scoped ES index (the
  DocuVault sync pattern). Tag `v0.1-catalog`.
- [ ] **M2 — Multi-vendor checkout.** Split the order into vendor groups and
  write the outbox in one transaction. Charge once through PayFlow with an
  idempotency key. The webhook triggers per-vendor ledger entries. Add the
  per-vendor fulfillment status (WareFlow concepts). Add the end-to-end test:
  two vendors, one checkout, two groups, two ledger entries, one payment.
  Write `docs/distributed-transactions.md` and `docs/cart-persistence.md`.
  Tag `v0.2-checkout`.
- [ ] **M3 — Protection layers.** Run a `locust` checkout test. Add bulkhead
  pools per downstream service, sized from those numbers. Add a saturation
  test: `payment-service` slowed through Toxiproxy while `catalog-service`
  calls keep normal latency. Add Nginx `limit_req` per IP and per API key.
  Draw the four-layer table in `docs/architecture.md`. Tag `v0.3-protection`.
- [ ] **M4 — Observability & canary.** Add OTel to every service and pass
  `traceparent` through the gateway, the synchronous calls, the outbox relay
  and the webhook, so one checkout is one trace. Add metrics split by flag
  cohort. Ship checkout dark behind the flag, then ramp 10% → 100% using the
  B37 runbook. Tag `v0.4-canary`.
- [ ] **M5 — Real cloud.** Extend PayFlow's `infra/` Terraform with compute,
  managed Postgres in a private subnet, security groups, DNS, a certificate,
  and a bucket + CDN for static assets (the storefront build if you did the
  optional frontend, otherwise the API documentation site). Run `plan` in
  CI and `apply` from `main`, with remote locked state and no console
  clicks. After a week, read the bill and write
  `docs/cloud-deployment-notes.md`. Tag `v0.5-cloud`.
- [ ] **M6 — GraphQL BFF.** Build a product-page query (product + vendor +
  stock) in Strawberry, and measure 51 calls without DataLoader against 2 with
  it. Complete the transport decision record (REST / gRPC / GraphQL). Tag
  `v0.6-bff`.
- [ ] **M7 — Design practice & wrap.** Whiteboard multi-vendor checkout from
  scratch, then compare it with what you built. Work SD10 and SD16. Close
  with **SD20 "Design AtlasMarket, From Scratch"** (45 min, no notes, then
  compare with `docs/architecture.md`). Write
  `docs/atlasmarket-roadmap-post-track2.md`. Tag `v1.0-atlasmarket`.

### Definition of done
- [ ] `docs/architecture.md` maps every service to its origin project and documents the four protection layers
- [ ] Multi-vendor checkout end-to-end test green (two vendors → two groups, two ledger entries, one idempotent payment)
- [ ] Vendor isolation proven at the API with crafted requests, and by the RLS "forgotten WHERE" test (the app role is subject to the policy; only the migration role bypasses it)
- [ ] Bulkhead proven under saturation; pool sizes documented with the `locust` numbers
- [ ] `limit_req` returns 429 past the burst while other clients are unaffected
- [ ] Feature-flag bucketing stable per user (tested); canary ramped and watched by cohort
- [ ] One checkout shows as a single trace across all five services and the relay
- [ ] Cloud built by Terraform only; the DB is unreachable from the internet; HTTPS; CDN assets use `immutable` cache headers; `terraform plan` is clean after `apply`
- [ ] GraphQL DataLoader measurement recorded
- [ ] All `docs/*` artefacts written; SD10, SD16 and SD20 written up and compared

**Estimated time:** ~70h

### OPTIONAL extensions
- [ ] **Storefront** (needs B21, OPTIONAL): React Router routes for product list / cart / checkout, TanStack Query, cart kept in component state (write down why no global store yet), React Testing Library component tests, and one **Playwright** test through browse → cart → checkout in CI.
- [ ] **AI convergence** (needs Track 3: ML Zoomcamp + LLM Zoomcamp): a co-purchase recommender served from a precomputed table (`GET /products/{id}/recommendations`, refreshed nightly); a small RAG support assistant over product descriptions and vendor policies that cites its sources; a nightly per-vendor daily revenue aggregation table.
- [ ] **Telegram bot** (needs B-opt): `/order_status <order_id>` showing each vendor group's status, plus push notifications delivered through a new outbox consumer.

### Interview questions
1. Walk me through the checkout flow across the five services, including where idempotency and the ledger come in.
2. One payment, many vendor groups: how do you keep that consistent without a distributed transaction?
3. How do you make sure a vendor can never see another vendor's data?
4. Rate limit, bulkhead, circuit breaker, retry: which failure does each handle, and in what order do they sit?
5. Why one database rather than one per service, and what would make you split it?

---

**Answers**
1. Cart → stock validated per vendor line → one local transaction creates the
   order, its vendor groups and the outbox rows → the payment is charged once
   with the order id as idempotency key → the signed webhook confirms it →
   per-vendor journal entries are posted → the relay publishes events and the
   vendors' fulfillment views update. The retry points are idempotent, and the
   ledger balances per entry.
2. The split and the outbox commit atomically in one local transaction. The
   payment is idempotent, and the ledger entries are driven by events with
   idempotent consumers. Reconciliation queries (group totals = payment
   amount; debits = credits) catch any drift. This is an explicit saga, not
   2PC.
3. Two layers. Every query filters by `vendor_id`, which is resolved from the
   JWT. On top of that, Postgres RLS policies use `SET LOCAL app.vendor_id`
   inside each transaction, so a forgotten `WHERE` returns nothing. It is
   tested at the API with crafted requests, not by hiding things in the UI.
4. The rate limit (outermost, cheapest) sheds abusive or excess traffic. The
   bulkhead stops a *slow* dependency from using up all workers. The circuit
   breaker stops calls to a *failing* dependency. Retry with backoff and jitter
   handles *transient* errors. In that order from the outside in, with retries
   only inside the breaker.
5. At this scale, one database keeps checkout a local transaction and keeps
   operations simple. Separate databases would force distributed consistency
   you do not need yet. You would split when a service needs independent
   scaling, a different storage engine, or its own team and release cadence.
   You would do it with the outbox and events already in place.

---

## Module B39 — MongoDB (~8h)

**Topics:** the document model; embedding vs referencing; schema design
patterns (subset, extended reference, computed, bucket, outlier); CRUD and
update operators; indexes (single, compound, multikey, TTL, partial) and the
ESR rule (Equality → Sort → Range); `explain("executionStats")`; the
aggregation pipeline (`$match`, `$group`, `$lookup`, `$unwind`, `$project`,
`$facet`); multi-document transactions and when they are a smell; replica
sets, read/write concern and read preference; the Python drivers (PyMongo and
its async API; Motor is being replaced by PyMongo's async API [verify]); when
MongoDB beats PostgreSQL `JSONB`, and when it does not.

### Theory
- [ ] **39.1 Document model & data modeling** — MongoDB Manual: "Introduction to MongoDB", "Data Modeling" (embedded vs references, "Data Model Design"); MongoDB blog series "Building with Patterns".
- [ ] **39.2 CRUD** — MongoDB Manual: "MongoDB CRUD Operations" (Insert, Query, Update, Delete, and the update operators reference).
- [ ] **39.3 Indexes** — MongoDB Manual: "Indexes" (Compound, Multikey, TTL, Partial) and "Analyze Query Performance" (`explain`); MongoDB docs article on the ESR (Equality, Sort, Range) guideline.
- [ ] **39.4 Aggregation** — MongoDB Manual: "Aggregation Pipeline" and "Aggregation Pipeline Stages" reference.
- [ ] **39.5 Transactions & replication** — MongoDB Manual: "Transactions", "Replication" (Replica Set Members, Read Concern, Write Concern, Read Preference).
- [ ] **39.6 Python driver** — PyMongo documentation: "Get Started" and the async API guide; MongoDB University (learn.mongodb.com), "MongoDB Python Developer Path" (free).

### Exercises
- [ ] **Ex 39.1 — Local replica set.** Run MongoDB in Docker Compose as a
  single-node replica set (transactions need one). **Acceptance:**
  `rs.status()` shows PRIMARY, and a Python script connects and inserts one
  document.
- [ ] **Ex 39.2 — Model AtlasMarket product reviews.** Design a `reviews`
  collection twice: embedded in the product, and as a separate collection
  referencing `product_id`. Write down the decision, taking into account
  review counts per product (outliers with 50k reviews), the 16 MB document
  limit, and the most frequent queries. **Acceptance:** `notes.md` covers both
  designs with their read/write patterns, and the chosen one is implemented.
- [ ] **Ex 39.3 — Aggregations.** Load 100k generated reviews. Write
  pipelines for (a) average rating and review count per vendor, (b) the top 10
  products by rating with at least 50 reviews, and (c) a monthly histogram of
  ratings. **Acceptance:** each result is checked against a small hand-built
  dataset in a pytest test.
- [ ] **Ex 39.4 — Indexes with explain.** For the query "reviews of a product,
  newest first, rating ≥ 4", compare the plan with no index and with a
  compound index built following ESR. **Acceptance:** `docsExamined` and
  `executionTimeMillis` before and after are recorded in `notes.md`.
- [ ] **Ex 39.5 — Activity feed with TTL.** Build a `user_activity` collection
  that expires events after 30 days using a TTL index, and paginate it by
  `_id`/timestamp rather than by skip. **Acceptance:** a test inserts
  back-dated documents and confirms they are removed. Also document how
  quickly the TTL monitor actually deletes (it is not instant).
- [ ] **Ex 39.6 — Decision record.** Write `docs/mongo-vs-jsonb.md` for the
  reviews feature: what PostgreSQL `JSONB` + GIN would look like, and which
  one you would choose for AtlasMarket and why.

### Must be able to do / explain
- [ ] Choose between embedding and referencing from the access patterns.
- [ ] Build compound indexes using ESR and read `explain` output.
- [ ] Write aggregation pipelines including `$group`, `$lookup` and `$unwind`.
- [ ] Explain replica sets, write concern `majority` and read preference trade-offs.
- [ ] Explain when a multi-document transaction points to a modeling problem.
- [ ] Argue MongoDB vs PostgreSQL (`JSONB`) for a concrete feature.

**Estimated time:** ~8h

### Self-check interview questions
1. When do you embed documents and when do you reference them?
2. What is the ESR rule for compound indexes?
3. What does write concern `majority` guarantee?
4. Does MongoDB support transactions? When should you avoid relying on them?
5. How is `$lookup` different from a SQL JOIN in practice?
6. Why is `skip()`-based pagination slow on large collections, and what do you use instead?
7. When would you pick PostgreSQL `JSONB` over MongoDB?

---

**Answers**
1. Embed data that is read together with its parent, bounded in size and owned
   by the parent. Reference data that is unbounded (it would hit the 16 MB
   limit or grow forever), shared by many parents, or updated independently.
2. Put the fields used for Equality matches first, then the Sort fields, then
   the Range filters. That lets the index both filter and return documents in
   order without an in-memory sort.
3. The write is acknowledged only after a majority of voting replica-set
   members have it, so it will not be rolled back after a primary failover.
4. Yes, multi-document ACID transactions on replica sets and sharded clusters.
   Avoid designs that need them on every request. They cost performance and
   have time limits, and frequent need usually means the documents are
   modelled wrongly.
5. It is a pipeline stage, less optimized than a relational planner's join. It
   works best with an index on the foreign field and small inputs. Heavy
   cross-collection joins suggest a relational model fits better.
6. `skip(n)` still walks the n skipped index entries or documents. Use range
   (keyset) pagination on an indexed field such as `_id` or a timestamp, for
   example `{_id: {$gt: last}}`.
7. When the data is mostly relational and needs joins, constraints or
   multi-table transactions, and only part of it is semi-structured. You then
   keep one operational database and get SQL, constraints and JSONB + GIN
   indexing together.

---

## Module B40 — TimescaleDB (~5h)

**Topics:** time-series workloads (append-heavy writes, time-range queries);
the TimescaleDB extension on PostgreSQL; hypertables and chunks (chunk time
interval, chunk exclusion); `time_bucket()` and gap filling; continuous
aggregates with refresh policies; compression / columnstore; retention
policies; comparison with plain partitioning (1C Module 2.9) and BRIN
indexes. (Timescale the company was renamed TigerData in 2025, and the docs may
live under that name. [verify])

### Theory
- [ ] **40.1 Hypertables & chunks** — Timescale docs: "Hypertables" (create a hypertable, chunk time intervals, how chunks work).
- [ ] **40.2 Time buckets** — Timescale docs: API reference `time_bucket()` and `time_bucket_gapfill()`.
- [ ] **40.3 Continuous aggregates** — Timescale docs: "Continuous aggregates" (create, refresh policies, real-time aggregates).
- [ ] **40.4 Compression and retention** — Timescale docs: "Compression" (in newer versions "Hypercore / columnstore") and "Data retention" (`add_retention_policy`).

### Exercises
- [ ] **Ex 40.1 — FleetTrack GPS pings hypertable.** Run `timescale/timescaledb`
  in Compose. Create `gps_pings(time timestamptz, driver_id, lat, lon,
  speed_kmh)` as a hypertable with 1-day chunks, and generate 10M rows over
  30 days for 200 drivers. **Acceptance:** `timescaledb_information.chunks`
  lists the expected chunks.
- [ ] **Ex 40.2 — Time-bucket queries.** Write (a) average speed per driver in
  5-minute buckets for one day and (b) the drivers with no ping in the last 15
  minutes. **Acceptance:** `EXPLAIN ANALYZE` shows chunk exclusion (only the
  relevant chunks are scanned).
- [ ] **Ex 40.3 — Continuous aggregate.** Create an hourly per-driver
  aggregate with a refresh policy. **Acceptance:** querying the aggregate is at
  least 10× faster than the raw query (record both times), and fresh rows
  appear after a refresh.
- [ ] **Ex 40.4 — Compression and retention.** Compress chunks older than 7
  days and add a 30-day retention policy. **Acceptance:** table size before and
  after compression is recorded, and old chunks are dropped by the policy
  rather than by `DELETE`.
- [ ] **Ex 40.5 — Compare with plain Postgres.** Load the same data into a
  natively partitioned table with a BRIN index on `time` and run query (a)
  again. Write down in `notes.md` when you would reach for TimescaleDB and when
  plain partitioning is enough.

### Must be able to do / explain
- [ ] Create a hypertable and choose a chunk interval.
- [ ] Explain chunk exclusion and why dropping chunks beats `DELETE` for retention.
- [ ] Use `time_bucket` and continuous aggregates for dashboards.
- [ ] Explain the trade-offs of compressing old chunks (fast scans, slower updates).
- [ ] Compare TimescaleDB with native partitioning + BRIN.

**Estimated time:** ~5h

### Self-check interview questions
1. What is a hypertable, and how is it different from a normal table?
2. Why is dropping a chunk better than `DELETE ... WHERE time < now() - interval '30 days'`?
3. What is a continuous aggregate, and how is it different from a materialized view?
4. How do you pick a chunk time interval?
5. What do you lose when you compress a chunk?
6. When is plain PostgreSQL partitioning enough?

---

**Answers**
1. A hypertable is one logical table that is automatically partitioned by time
   (and optionally by space) into chunks. Queries and inserts target the
   parent, and TimescaleDB routes them to the right chunks.
2. Dropping a chunk is a metadata operation, like dropping a partition. It
   leaves no dead tuples, needs no vacuum and causes no heavy WAL or long
   locks. A mass `DELETE` does all of those.
3. It is an incrementally maintained aggregate over time buckets. Refreshes
   only recompute changed buckets, and real-time mode can combine the
   materialized data with the newest raw rows. A plain materialized view is
   recomputed fully on every refresh.
4. The recent chunks (plus their indexes) should fit comfortably in memory. A
   common starting point is that the most recent chunk is about a quarter of
   RAM. Then adjust based on ingest rate and query ranges.
5. Compressed chunks are stored in columns, so scans get fast and the data gets
   small. Updates and deletes on those chunks become slower or restricted, so
   you compress data only once it has stopped changing.
6. When volumes are moderate, retention can be done by dropping partitions
   yourself, and you do not need continuous aggregates, compression or gap
   filling. Native partitioning plus a BRIN index on time covers many cases.

---

## Optional Project O1 — URL Shortener · Middle · OPTIONAL (~15h)

### Goal
Build SD1 for real: a small, tested service instead of a paper design.
`POST /shorten {url} → {short_code}` and `GET /{short_code}` → **301**
redirect to the original URL.

### Features
- [ ] Base62 short codes generated from a **counter**, not random or hashed. The README argues why, tying back to SD1's "counter + base62 vs hash vs random" deep dive
- [ ] Deleted URLs return **404**, never a redirect to a dead link
- [ ] Redis **cache-aside** in front of the mapping table for hot redirects
- [ ] Rate limit on `POST /shorten`. If O2 is done, reuse the O2 service instead of an ad hoc limiter; otherwise use the B12 Redis limiter
- [ ] Load test of the redirect path with a cold vs a warm cache

### Tech stack
| Tool | Taught in |
|---|---|
| FastAPI, Pydantic | B4 |
| PostgreSQL, SQLAlchemy, Alembic | B5 |
| Redis cache-aside, rate limiting | B12 |
| Docker Compose | B3 |
| `locust` / `hey` | B35, B8 |
| pytest | 1A.8, B8 |

### Required knowledge
B1, B3–B5, B8, B12, B35; SD1 worked on paper (B38).

### Milestones
- [ ] **M1** — Mapping table, the counter-based base62 encoder, create and redirect endpoints, 404 on deleted codes. Tag `v0.1-shortener`.
- [ ] **M2** — Redis cache-aside on redirects, invalidated immediately on delete. Tag `v0.2-cache`.
- [ ] **M3** — Rate limiting on create; load test cold vs warm; README with the design argument. Tag `v1.0-shortener`.

### Definition of done
- [ ] Collision test: two `POST /shorten` calls for different URLs never get the same code
- [ ] Cache-invalidation test: a deleted URL's cached redirect stops working **immediately**, not after the TTL
- [ ] p95 redirect latency cold vs warm recorded in the README
- [ ] README compares the build with your paper SD1 design

**Estimated time:** ~15h

### Interview questions
1. Why generate codes from a counter rather than hashing the URL or picking random strings?
2. Why 301 and not 302, and what does that choice mean for analytics?
3. How do you invalidate a cached redirect when a URL is deleted?
4. How would you shard the counter when there are several app instances?
5. What did building it teach you that your paper SD1 design missed?

---

**Answers**
1. A counter gives no collisions by construction and the shortest possible
   codes. Hashing needs collision handling and truncation. Random codes need a
   uniqueness check and retries. The cost of a counter is that codes are
   predictable (mitigate by encoding with a shuffled alphabet or by
   rate-limiting enumeration) and that it needs coordination at scale.
2. 301 is permanent and cacheable by browsers, so repeat visits skip your
   server, which gives less load and less analytics. 302/307 sends every click
   through your server, which you need if you count clicks.
3. Delete the database row and the cache key in the same code path: delete
   from the DB first, then from the cache. For extra safety use short TTLs
   plus a delete event, so an entry that raced back in cannot live long.
4. Hand each instance a block of IDs (range allocation), or use a Snowflake-like
   ID with a worker id, so instances never coordinate for each code.
5. Your own answer. Typical ones: cache invalidation on delete, the
   predictability of a counter, and how much the cache really changes p95.

---

## Optional Project O2 — Rate Limiter Service · Middle · OPTIONAL (~15h)

### Goal
Build SD2 for real: a standalone rate-limiting **service** (not a library)
that any of your systems could call: `POST /check {key, limit, window} →
{allowed: bool, remaining: int}`.

### Features
- [ ] Two algorithms behind one interface: **token bucket** and **sliding-window counter**
- [ ] Atomic updates in Redis (Lua scripts)
- [ ] **Actually distributed:** 3 instances of the service behind Nginx, sharing one Redis
- [ ] Benchmark of memory and accuracy for both algorithms at 100k tracked keys

### Tech stack
| Tool | Taught in |
|---|---|
| FastAPI | B4 |
| Redis, Lua scripts, rate-limit algorithms | B12 |
| Nginx load balancing | B17 |
| Docker Compose | B3 |
| `locust` | B35 |
| pytest, Hypothesis | 1A.8, B8 |

### Required knowledge
B3, B4, B8, B12, B17, B35; SD2 worked on paper (B38).

### Milestones
- [ ] **M1** — `/check` API with the token bucket, plus correctness tests against a fixed request schedule. Tag `v0.1-limiter`.
- [ ] **M2** — Sliding-window counter behind the same interface, with the same tests. Tag `v0.2-sliding`.
- [ ] **M3** — 3 instances behind Nginx; the multi-instance test; the memory benchmark. Tag `v1.0-limiter`.

### Definition of done
- [ ] Per-algorithm correctness tests pass against a fixed schedule with known expected outcomes
- [ ] **The multi-instance test (the centrepiece):** a client hitting all 3 instances is limited to 1× the limit, not 3×
- [ ] Memory footprint of both algorithms at 100k keys recorded, plus the accuracy trade-off discussion
- [ ] README compares the build with your paper SD2 design

**Estimated time:** ~15h

### Interview questions
1. Token bucket vs sliding-window counter: what are the trade-offs?
2. What happens when 3 instances check the same key in the same millisecond?
3. Why use a Lua script instead of `GET` then `SET`?
4. What should the limiter do if Redis is down: fail open or fail closed?
5. How would you rate-limit across regions?

---

**Answers**
1. The token bucket allows controlled bursts, needs two values per key and
   is easy to reason about. The sliding-window counter approximates a true
   sliding window using two fixed-window counters. It uses little memory and
   is slightly inaccurate at window edges. A sliding log is exact but stores
   every timestamp.
2. Without atomicity, all of them read the same count and all of them allow
   the request, so the limit is exceeded. With a Lua script, Redis runs each
   check-and-update as one atomic operation, so the calls are serialized.
3. `GET` then `SET` is a read-modify-write race across clients. A Lua script
   runs atomically on the Redis server in one round trip.
4. It depends on what is protected. Public APIs usually fail open with an
   alert, so an outage of the limiter does not become an outage of the
   product. Expensive or abuse-sensitive endpoints (login, payments) may fail
   closed. Decide it and document it up front.
5. Run a local limiter per region with a share of the global budget, and
   synchronize asynchronously. You accept an approximate global limit in
   exchange for low latency, because a single global Redis adds cross-region
   round trips.

---

## Optional Project O3 — Distributed Job Scheduler · Middle+ · OPTIONAL (~25h)

### Goal
Build SD14 for real: `POST /jobs {cron_expr, payload} → {job_id}`. The
scheduler dispatches each job **exactly once per scheduled tick**, even
though the scheduler itself runs as several processes for availability.

### Features
- [ ] The scheduler processes form a **Raft cluster**, using your from-scratch Raft implementation from B29 (OPTIONAL build) hardened into a service; **only the leader dispatches**
- [ ] Real persistence of jobs and dispatch records; HTTP API in front
- [ ] Idempotent job handlers, so a job dispatched just before a crash is retried safely without running twice
- [ ] Cron expression parsing and next-tick calculation

### Tech stack
| Tool | Taught in |
|---|---|
| Raft (your implementation) | B29 (OPTIONAL Raft build) |
| FastAPI | B4 |
| PostgreSQL / SQLAlchemy | B5 |
| Idempotent consumers | B13, B15, B25 |
| `freezegun` time control | B13 |
| Docker Compose | B3 |
| pytest | 1A.8, B8 |

### Required knowledge
B29 including the OPTIONAL from-scratch Raft build; B13, B25; SD14 worked on
paper (B38).

### Milestones
- [ ] **M1** — Job API, cron parsing, persistence, single-node dispatcher with idempotent handlers. Tag `v0.1-scheduler`.
- [ ] **M2** — Run the dispatcher on the Raft cluster: leader-only dispatch, dispatch decisions replicated through the log. Tag `v0.2-raft`.
- [ ] **M3** — Fault tests and README. Tag `v1.0-scheduler`.

### Definition of done
- [ ] Kill the leader in the middle of a dispatch decision → **exactly one** execution results (never zero, never two)
- [ ] A simulated 24-hour run (compressed with `freezegun`) shows every scheduled tick fired exactly once
- [ ] README compares the build with your paper SD14 design, and `docs/sd-builds-vs-paper-designs.md` covers every O-project you finished

**Estimated time:** ~25h

### Interview questions
1. Why does leader-only dispatch matter, and what breaks when there are two leaders?
2. How do you get "exactly once" execution when dispatch and execution can each fail?
3. What happens to a tick that should have fired while there was no leader?
4. Why not use a database row lock or `SELECT … FOR UPDATE SKIP LOCKED` instead of Raft?
5. Of O1–O3, which needs the most work to become production-ready, and why?

---

**Answers**
1. With two leaders (split brain), both dispatch the same tick, so the job runs
   twice. Raft's term numbers and majority quorum ensure at most one leader
   can commit a dispatch decision in a given term.
2. You cannot get exactly-once delivery. You get at-least-once dispatch plus
   idempotent handlers keyed on (job_id, tick), which gives exactly-once
   *effects*.
3. The new leader looks at the committed log and the persisted "last fired
   tick", and then either catches up on the missed ticks or skips them,
   according to an explicit per-job misfire policy.
4. You often can, and for many systems a Postgres-backed lock or lease is the
   pragmatic choice. The trade-off is that the database becomes the single
   point of coordination. This project uses Raft on purpose, to exercise the
   consensus implementation.
5. Your own answer. The usual one is the scheduler, because of cluster
   membership changes, log compaction and snapshots, operability and
   monitoring.

---

## Tool coverage matrix

Every backend tool used by a core project is taught in an earlier module.
"(opt)" marks tools that are only used in OPTIONAL modules, projects or
extensions.

| Tool | Taught in | First used in |
|---|---|---|
| FastAPI | B4 | P1 StockPilot |
| Pydantic v2 / pydantic-settings | B4 | P1 |
| SQLAlchemy 2.0 (sync → async) | B5 | P1 |
| Alembic | B5 | P1 |
| Docker (multi-stage, non-root) | B3 | P1 |
| Docker Compose | B3 | P1 |
| GitHub Actions | B9 (CD in B23) | P1 |
| GHCR (image registry) | B9, B23 | P5 CarePoint |
| pytest | 1A.8, B8 | P1 |
| factory_boy | B8 | P1 |
| Hypothesis | 1A.8, B8 | P1 |
| `hey` (quick load test) | B8 | P1 |
| ruff, mypy, pre-commit | 1A.7, 1A.9 | P1 |
| structlog | 1A.9 (logging), B24 (in depth) | P1 |
| Django | B10 | P2 QuickServe POS |
| DRF | B11 | P2 |
| djangorestframework-simplejwt | B11 | P2 |
| Redis (cache, counters) | B12 | P2 |
| fakeredis | B12 | P2 |
| aiogram (opt) | B-opt | P2 extension (opt) |
| Celery | B13 | P3 PeopleOps |
| Celery Beat | B13 | P3 |
| freezegun | B13 | P3 |
| MailHog | B13 | P3 |
| RabbitMQ | B15 | P4 WareFlow |
| Pact (message contracts) | B15 | P4 |
| Kafka | B16 | P4 (comparison) |
| Nginx | B17 | P5 |
| Let's Encrypt / certbot | B17 | P6 LedgerBase |
| Keycloak (OIDC) | B18 | P5 |
| MinIO / S3 | B20 | P5 |
| React + TS + TanStack Query (opt) | B21 | P5 frontend (opt) |
| pip-audit, gitleaks, Trivy | B23 (gitleaks as a hook in 1A.9) | P6 (gitleaks: P1) |
| Prometheus | B24 | P6 |
| Grafana | B24 | P6 |
| Alertmanager | B24 | P6 |
| Loki | B24 | P6 |
| OpenTelemetry (Tempo/Jaeger) | B24 | P6 |
| Sentry | B24 | P6 |
| WebSockets | B26 | P7 FleetTrack |
| Server-Sent Events | B26 | P7 |
| Redis pub/sub | B26 | P7 |
| Elasticsearch | B27 | P8 DocuVault |
| PgBouncer | B28 | P8 |
| etcd | B29 | P8 |
| Kubernetes (kind), Ingress, HPA | B30 | P8 |
| HashiCorp Vault | B31 | P9 PayFlow |
| gRPC + Protobuf | B32 | P9 |
| Terraform | B33 | P9 |
| Cloud IAM / VPC / managed Postgres / CDN | B33 | P10 AtlasMarket |
| locust | B35 | P9 |
| py-spy | B35 | P9 |
| Toxiproxy | B35 (fault injection intro in B22) | P9 |
| Postgres Row-Level Security | B37 | P10 |
| Feature flags / canary | B37 | P10 |
| Strawberry GraphQL + DataLoader | B36 | P10 |
| Playwright (opt) | B21 | P10 storefront (opt) |
| React Router, React Testing Library (opt) | B21 | P10 storefront (opt) |
| MongoDB | B39 | B39 exercises (no core project) |
| TimescaleDB | B40 | B40 exercises (no core project) |
| Raft (own implementation) (opt) | B29 OPTIONAL build | O3 (opt) |
| scikit-learn, MLflow, pgvector, LLM APIs (opt) | Track 3 | project extensions (opt) |

---

## Track 2 progress summary

Tick **Done** when a module's checklist or a project's Definition of Done is
complete.

### Modules
| Module | Name | Hours | Done |
|---|---|---|---|
| B1 | HTTP & REST API design | 8 | [ ] |
| B2 | Linux & CLI basics | 8 | [ ] |
| B3 | Docker & Docker Compose | 12 | [ ] |
| B4 | FastAPI | 15 | [ ] |
| B5 | SQLAlchemy 2.0 (sync → async), Alembic, layered architecture | 18 | [ ] |
| B6 | Auth I | 8 | [ ] |
| B7 | Transactions & concurrency in apps | 8 | [ ] |
| B8 | Testing web apps | 10 | [ ] |
| B9 | CI with GitHub Actions | 6 | [ ] |
| B10 | Django | 18 | [ ] |
| B11 | DRF | 14 | [ ] |
| B12 | Redis I: caching & rate limiting | 12 | [ ] |
| B-opt | Telegram bots (aiogram) — OPTIONAL | 8 | [ ] |
| B13 | Celery | 12 | [ ] |
| B14 | Architecture patterns | 10 | [ ] |
| B15 | RabbitMQ | 12 | [ ] |
| B16 | Kafka | 10 | [ ] |
| B17 | Networking + Nginx | 12 | [ ] |
| B18 | Auth II: OAuth2/OIDC | 12 | [ ] |
| B19 | Web security basics | 8 | [ ] |
| B20 | Object storage | 4 | [ ] |
| B21 | React + TypeScript for backend engineers — OPTIONAL | 25 | [ ] |
| B22 | Resilience patterns | 8 | [ ] |
| B23 | CI/CD II & VPS deployment | 15 | [ ] |
| B24 | Logging & monitoring | 15 | [ ] |
| B25 | Event-driven patterns | 12 | [ ] |
| B26 | Real-time: WebSocket, SSE, pub/sub | 8 | [ ] |
| B27 | Search: Postgres FTS → Elasticsearch | 12 | [ ] |
| B28 | Replication, pooling, sharding, consistent hashing | 10 | [ ] |
| B29 | Consensus & Raft (+ OPTIONAL from-scratch build, 40h) | 10 | [ ] |
| B30 | Kubernetes | 20 | [ ] |
| B31 | Secrets management (Vault) | 8 | [ ] |
| B32 | gRPC + Protobuf | 8 | [ ] |
| B33 | Cloud basics + Terraform | 15 | [ ] |
| B34 | Idempotency & webhooks | 6 | [ ] |
| B35 | Reliability & SRE | 12 | [ ] |
| B36 | GraphQL | 8 | [ ] |
| B37 | Multi-tenancy & release engineering | 6 | [ ] |
| B38 | System design fundamentals | 20 | [ ] |
| B39 | MongoDB | 8 | [ ] |
| B40 | TimescaleDB | 5 | [ ] |
| | **Core modules total** | **~423** | |

### Core projects
| Project | Name | Level | Hours | Done |
|---|---|---|---|---|
| P1 | StockPilot | Junior | 60 | [ ] |
| P2 | QuickServe POS | Junior | 45 | [ ] |
| P3 | PeopleOps | Middle | 45 | [ ] |
| P4 | WareFlow | Middle | 60 | [ ] |
| P5 | CarePoint | Middle | 50 | [ ] |
| P6 | LedgerBase | Middle | 65 | [ ] |
| P7 | FleetTrack | Middle+ | 45 | [ ] |
| P8 | DocuVault | Middle+ | 60 | [ ] |
| P9 | PayFlow | Middle+ | 60 | [ ] |
| P10 | AtlasMarket | Middle+ | 70 | [ ] |
| | **Core projects total** | | **~560** | |

### Optional
| Item | Hours | Done |
|---|---|---|
| B21 React + TypeScript | 25 | [ ] |
| B-opt Telegram bots (aiogram) | 8 | [ ] |
| B29 from-scratch Raft build | 40 | [ ] |
| O1 URL Shortener · Middle | 15 | [ ] |
| O2 Rate Limiter Service · Middle | 15 | [ ] |
| O3 Distributed Job Scheduler · Middle+ | 25 | [ ] |
| **Optional total** | **~128** | |

**Track 2 core total: ~983h** (423h modules + 560h projects), plus ~128h optional.

