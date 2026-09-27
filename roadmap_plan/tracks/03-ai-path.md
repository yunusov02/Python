# Track 3 — AI Path (DataTalks.Club Zoomcamps)

**Goal:** learn applied AI/ML/data engineering by completing the five free
DataTalks.Club Zoomcamps: LLM, AI Dev Tools, Machine Learning, MLOps and
Data Engineering. Each course runs on your own backend skills (FastAPI,
Docker, Postgres, CI) and adds its own layer on top.

**Required knowledge (summary):** confident Python (Track 1A), SQL (Track 1C
Part 1–2), Docker/Compose (B3), a web framework (B4 FastAPI), Git and CI
(1A.1, B9). Each course lists its exact prerequisites below.

**Total estimated hours:** ~500 h (LLM ~80 · AI Dev Tools ~60 · ML ~150 ·
MLOps ~90 · Data Engineering ~120).

**Source of truth:** only the official course content — modules, lessons,
workshops, homework and course projects from each course's GitHub repo.
Nothing here is invented on top of the courses. Syllabi were read from the
repos on 2026-09-27; anything not confirmed there is marked **[verify]**.

---

## You choose the order

The courses are independent except for one hard dependency. A suggested
logical order is **LLM → AI Dev Tools → ML → MLOps → Data Engineering**:

1. LLM and AI Dev Tools are the smallest step from backend work (APIs,
   retrieval, agents, AI-assisted development).
2. **MLOps really needs ML first** — it productionizes the kind of models ML
   Zoomcamp teaches you to build.
3. Data Engineering is independent; do it whenever you want (it pairs well
   with the SQL track).

### Cohorts (as of 2026-09-27)

| Course | Current / next cohort | Note |
|---|---|---|
| LLM | 2026: Aug 24 – Oct 12, 2026 | running now |
| AI Dev Tools | 2026: Aug 31 – Sep 28, 2026 | ending; 2026 materials are marked **draft** |
| ML | 2026: Sep 14, 2026 – Jan 25, 2027 | running now |
| MLOps | no live cohort in 2026 | self-paced only; last live cohort was 2025 |
| Data Engineering | 2027: starts Jan 11, 2027 [verify] | 2027 cohort page is still a draft |

**Self-paced is always possible.** All videos, code and homework stay
public. Certificates are only issued to people who submit the course
project (and do the peer reviews) during a **live cohort**.

---

## How to use this track

- **Checkboxes everywhere.** Tick a lesson when you watched it *and* ran the
  code yourself. Tick **Homework** when you finished it (and submitted it, if
  a cohort is live). Tick a project milestone when it is committed.
- **No homework solutions here.** Homework answers are yours to find. The
  self-check questions at the end of each module have answers below the
  `---` separator — those are for self-testing only.
- **Where the work goes:**
  - Notes and homework: this repo, `ai/<course>/<module>/`
    (e.g. `ai/llm/01-agentic-rag/notes.md`, `ai/llm/01-agentic-rag/homework.ipynb`).
  - Course projects: **one GitHub repo per project** (peer reviewers need a
    public repo).
- **Use your own systems for datasets when you can.** Course projects must
  not use the course's own datasets (FAQ, NYC taxi, car price, churn, etc.),
  so data from your Track 2 projects is a good source — but the project
  scope stays the official one.

---

## Course 3.1 — LLM Zoomcamp (~80h)

**Repo:** https://github.com/DataTalksClub/llm-zoomcamp
**Official length:** ~10 weeks, once a year.
**Official prerequisites:** confident Python, comfortable with the command
line, basic Docker. No ML/LLM knowledge or GPU needed. API credits cost
about $1–5.
**Required knowledge from other tracks:** 1A (Python, esp. 1A.8 pytest,
1A.12 asyncio), B3 Docker & Compose, B4 FastAPI, 1C 2.4 JSONB/arrays and
2.5 indexes (for pgvector). Helpful: B27 Search (Elasticsearch is used in
Module 6), B24 monitoring (Grafana in Module 5).
**Homework location:** `cohorts/2026/homework/<module>/homework.md`
(https://github.com/DataTalksClub/llm-zoomcamp/tree/main/cohorts/2026).

### Module 1 — Agentic RAG (`01-agentic-rag`)

**Topics:** what RAG is, keyword search with minsearch, building prompts,
the RAG pipeline, persistence with sqlitesearch; agents, function calling,
the agentic loop, ToyAIKit and production frameworks.

**Part 1 — RAG**
- [ ] 1.1 Introduction
- [ ] 1.2 Environment setup (Python, uv, OpenAI API)
- [ ] 1.3 What is RAG
- [ ] 1.4 The course FAQ dataset
- [ ] 1.5 Search (minsearch)
- [ ] 1.6 Building a prompt
- [ ] 1.7 RAG pipeline
- [ ] 1.8 RAG helper (RAGBase class)
- [ ] 1.9 Data ingestion (sqlitesearch)
- [ ] 1.10 Wrap-up of Part 1

**Part 2 — Agents**
- [ ] 1.11 Agents (limits of a fixed pipeline)
- [ ] 1.12 Quick RAG revision (optional)
- [ ] 1.13 Function calling
- [ ] 1.14 The agentic loop
- [ ] 1.15 ToyAIKit
- [ ] 1.16 Other frameworks
- [ ] (Optional) Build a search engine — video + code

- [ ] **Homework** — `cohorts/2026/homework/01-agentic-rag/homework.md` [verify folder name]

**Must be able to do/explain:**
- [ ] Draw the RAG flow: query → retrieve → build prompt → LLM → answer.
- [ ] Explain why retrieval quality limits answer quality.
- [ ] Explain function calling: the model returns a tool call, *your code* runs it.
- [ ] Explain the agentic loop and why it needs a stop condition.
- [ ] Build a working RAG over a small document set from scratch (no framework).

**Estimated hours:** ~10 h

**Self-check questions**
1. What problem does RAG solve that fine-tuning does not?
2. Why is the prompt template part of the system, not a detail?
3. What is the difference between a fixed RAG pipeline and an agent?
4. In function calling, who executes the function?
5. Why must an agent loop have a maximum number of iterations?
6. What is persisted by the ingestion step, and why?

---
**Answers**
1. It gives the model fresh/private knowledge at query time without retraining; you can update documents instantly and cite sources.
2. It decides what context the model sees and how it must answer (grounding, format, "say you don't know"); changing it changes behaviour as much as changing the model.
3. A fixed pipeline always does retrieve-then-answer once; an agent decides at runtime which tools to call, how many times and in what order.
4. Your application. The model only returns the function name and arguments; your code runs it and sends the result back.
5. To bound cost/latency and avoid infinite tool-call loops when the model never reaches a final answer.
6. The documents (and later their index/embeddings), so you don't re-fetch and re-index on every query and the search works across restarts.

### Module 2 — Vector Search (`02-vector-search`)

**Topics:** embeddings, vector similarity, embedding a dataset, vector
search with minsearch and sqlitesearch, pgvector, ONNX embedder.

- [ ] 2.1 What is vector search
- [ ] 2.2 Embeddings
- [ ] 2.3 Embedding our dataset
- [ ] 2.4 Vector search
- [ ] 2.5 Vector search with minsearch
- [ ] 2.6 RAG with vector search
- [ ] 2.7 Vector search with sqlitesearch
- [ ] 2.8 Vector search with PGVector
- [ ] 2.9 ONNX embedder (optional)
- [ ] 2.10 Next steps
- [ ] (Optional) Workshop recording "Vector Databases: Embeddings, Semantic Search, and Hybrid Retrieval"

- [ ] **Homework** — `cohorts/2026/homework/02-vector-search/homework.md` [verify folder name]

**Must be able to do/explain:**
- [ ] Explain what an embedding is and what cosine similarity measures.
- [ ] Embed a dataset with sentence-transformers and search it.
- [ ] Store and query vectors in Postgres with pgvector.
- [ ] Compare keyword search and vector search: when each wins.

**Estimated hours:** ~8 h

**Self-check questions**
1. What does an embedding model output for a piece of text?
2. Why is cosine similarity preferred over raw dot product for unnormalized vectors?
3. When does keyword search beat vector search?
4. Why do vector databases use approximate nearest neighbour indexes?
5. What changes in your data pipeline if you switch embedding models?

---
**Answers**
1. A fixed-length vector of floats that places semantically similar texts close together.
2. It measures the angle only, so vector length (often tied to text length) does not dominate the score; for normalized vectors both are equal.
3. For exact terms: IDs, codes, rare names, error messages — things embeddings blur.
4. Exact search is O(n) per query; ANN indexes (IVF, HNSW) trade a little recall for much faster search at scale.
5. All documents must be re-embedded and re-indexed; vectors from different models are not comparable, and dimensions may differ.

### Module 3 — AI Orchestration with Kestra (`03-orchestration`)

**Topics:** AI in workflows, context engineering, Kestra setup, AI Copilot,
RAG inside Kestra flows, AI agents and multi-agent systems, best practices.

- [ ] 3.1 Introduction
- [ ] 3.2 Context engineering
- [ ] 3.3 Setting up Kestra
- [ ] 3.4 AI Copilot
- [ ] 3.5 Retrieval Augmented Generation
- [ ] 3.6 AI agents
- [ ] 3.7 Multi-agent systems
- [ ] 3.8 Best practices (cost, security, observability)
- [ ] 3.9 Next steps

- [ ] **Homework** — `cohorts/2026/homework/03-orchestration/homework.md` [verify folder name]

**Must be able to do/explain:**
- [ ] Run Kestra locally with Docker and import example flows.
- [ ] Build a flow that ingests documents, embeds them and answers a question.
- [ ] Explain why generic AI assistants write wrong flows without context.
- [ ] Explain the cost/security risks of agents inside scheduled workflows.

**Estimated hours:** ~6 h

**Self-check questions**
1. What is an orchestrator responsible for that a cron script is not?
2. What is "context engineering"?
3. Why run RAG ingestion as an orchestrated flow instead of inside the API?
4. What can go wrong with an autonomous agent running on a schedule?
5. What does a multi-agent setup give you over one big agent?

---
**Answers**
1. Dependencies between steps, retries, backfills, scheduling, visibility of each run, inputs/outputs and alerting.
2. Deliberately giving the model the right information (docs, schemas, examples, constraints) so its output is correct for your system.
3. Ingestion is slow, batch and retryable; separating it keeps the API fast and lets you rerun/backfill ingestion safely.
4. Unbounded cost, wrong actions with no human review, prompt injection from ingested data, silent failures.
5. Smaller, focused prompts and tools per agent, clearer permissions, easier testing — at the cost of coordination overhead.

### Workshop — dlt: ingesting LLM traces (`cohorts/2026/workshops/dlt.md`)

**Topics:** dlt pipelines, filesystem and REST API sources, loading into
DuckDB, marimo dashboards over LLM traces.

- [ ] Watch the workshop / read `cohorts/2026/workshops/dlt.md`
- [ ] Run the workshop pipeline end to end
- [ ] **Homework** — `cohorts/2026/workshops/dlt/homework.md` [verify path]

**Must be able to do/explain:**
- [ ] Build a dlt pipeline from a REST API into DuckDB.
- [ ] Explain schema inference/normalization and incremental loading in dlt.

**Estimated hours:** ~5 h

**Self-check questions**
1. What does dlt do that a hand-written `requests` + `INSERT` script does not?
2. Why store LLM traces at all?
3. What is incremental loading?

---
**Answers**
1. Schema inference and evolution, normalization of nested JSON into tables, incremental state, retries and destination adapters.
2. To debug, evaluate and monitor the system: cost, latency, bad answers and user feedback all need the raw traces.
3. Only loading records that are new or changed since the last run, tracked by a cursor (e.g. timestamp or id).

### Module 4 — Evaluation (`04-evaluation`)

**Topics:** offline vs online evaluation, generating ground truth with an
LLM, search evaluation (hit rate, MRR), tuning search parameters, RAG and
agent evaluation, LLM-as-a-judge, tool-call trajectories.

**Part 1 — Search evaluation**
- [ ] 4.1 Intro (offline vs online)
- [ ] 4.2 Generating ground truth (one document)
- [ ] 4.3 Generating ground truth for all documents
- [ ] 4.4 Search evaluation
- [ ] 4.5 Search evaluation metrics (hit rate, MRR)
- [ ] 4.6 Search parameter tuning

**Part 2 — RAG and agent evaluation**
- [ ] 4.11 RAG and agent evaluation
- [ ] 4.12 Generating RAG answers
- [ ] 4.13 LLM as a judge
- [ ] 4.14 Agent evaluation (answers + tool-call trajectories)
- [ ] 4.15 Next steps
- [ ] (Optional) Workshop recording "RAG and Agents Evaluation"

- [ ] **Homework** — `cohorts/2026/homework/04-evaluation/homework.md` [verify folder name]

**Must be able to do/explain:**
- [ ] Build a ground-truth set and compute hit rate and MRR.
- [ ] Use the metrics to choose search parameters (e.g. boosts).
- [ ] Set up LLM-as-a-judge and explain its biases.
- [ ] Explain offline vs online evaluation.

**Estimated hours:** ~8 h

**Self-check questions**
1. Define hit rate@k and MRR.
2. Why generate ground truth with an LLM, and what is the risk?
3. What does LLM-as-a-judge measure, and what are its weaknesses?
4. How do you evaluate an agent differently from a RAG pipeline?
5. What is online evaluation?

---
**Answers**
1. Hit rate@k: share of queries whose relevant document is in the top k. MRR: average of 1/rank of the first relevant result (0 if missing).
2. It is cheap and fast at scale; the risk is questions that are too easy or too close to the document's wording, which inflates scores.
3. Answer relevance/faithfulness as judged by another model; it can be biased (toward long answers, its own style), inconsistent and costly.
4. You also check the trajectory: which tools were called, in what order, with what arguments, not just the final answer.
5. Measuring quality on real traffic: user feedback, A/B tests, judged samples of live answers.

### Module 5 — Monitoring (`05-monitoring`)

**Topics:** a RAG chat app in Streamlit, capturing metrics and cost,
storing conversations in Postgres, dashboards, user feedback, built-in
judge, synthetic data, Grafana, Docker Compose.

- [ ] 5.1 Intro
- [ ] 5.2 Assistant setup
- [ ] 5.3 Chat app (Streamlit)
- [ ] 5.4 Capturing metrics (LLMCallRecord, cost)
- [ ] 5.5 Database (Postgres in Docker)
- [ ] 5.6 Querying data
- [ ] 5.7 Streamlit dashboard
- [ ] 5.8 User feedback
- [ ] 5.9 Built-in judge
- [ ] 5.10 Feedback dashboard
- [ ] 5.11 Synthetic data
- [ ] 5.12 Grafana dashboards
- [ ] 5.13 Docker Compose
- [ ] 5.14 Next steps (OpenTelemetry, alerting)

- [ ] **Homework** — `cohorts/2026/homework/05-monitoring/homework.md` [verify folder name]

**Must be able to do/explain:**
- [ ] Log every LLM call with tokens, cost, latency and model.
- [ ] Collect thumbs up/down feedback and show it on a dashboard.
- [ ] Build a Grafana dashboard over the Postgres tables.
- [ ] Run the whole app with Docker Compose.

**Estimated hours:** ~8 h

**Self-check questions**
1. Which fields must you record for every LLM call?
2. Why is user feedback not enough on its own?
3. What does an automatic judge add to monitoring?
4. Why generate synthetic traffic?
5. What would you alert on in an LLM app?

---
**Answers**
1. Timestamp, conversation/request id, model, prompt and completion tokens, cost, latency, the answer, and later the feedback/judge verdict.
2. Few users give it and it is biased toward extremes; you need automatic signals too.
3. A quality signal on every (or a sample of) answers, without waiting for users.
4. To test dashboards and pipelines before real users arrive.
5. Error rate, latency p95, cost per hour/day, drop in positive feedback or judge relevance.

### Module 6 — Best Practices (`06-best-practices`)

**Topics:** hybrid search (vector + keyword) in Elasticsearch, reranking
with Reciprocal Rank Fusion, hybrid search with LangChain.

- [ ] 6.1 Intro — five techniques for improving RAG
- [ ] 6.2 Hybrid search (Elasticsearch)
- [ ] 6.3 Document reranking (RRF)
- [ ] 6.4 Hybrid search with LangChain (`ElasticsearchRetriever`)
- [ ] 6.5 Next steps
- [ ] Notebooks: hybrid search & reranking with Elasticsearch; hybrid search with LangChain

(The 2026 cohort README does not link a homework for this module [verify].)

**Must be able to do/explain:**
- [ ] Combine keyword and vector results and explain why that helps.
- [ ] Compute RRF by hand for two ranked lists.
- [ ] Measure the effect of hybrid search with Module 4 metrics.

**Estimated hours:** ~4 h

**Self-check questions**
1. What is hybrid search?
2. How does Reciprocal Rank Fusion score a document?
3. Why rerank at all?
4. Name one query rewriting technique.

---
**Answers**
1. Running keyword (BM25) and vector search and merging their results.
2. Sum over lists of 1/(k + rank) — documents ranked high in several lists win; raw scores are not needed.
3. First-stage retrieval is tuned for recall; reranking improves precision in the few documents that go into the prompt.
4. Asking the LLM to rephrase or expand the user question (e.g. add synonyms, split multi-part questions) before retrieval.

### Module 7 — End-to-End Project Example (`07-project-example`)

**Topics:** a full RAG project (fitness assistant): data generation,
retrieval and RAG evaluation, Flask API, ingestion, monitoring,
containerization, chunking.

- [ ] 7.1 Intro — data generation, setup, first RAG
- [ ] 7.2 Evaluating retrieval
- [ ] 7.3 Evaluating RAG
- [ ] 7.4 Interface and ingestion (Flask API)
- [ ] 7.5 Monitoring and containerization (Compose, Postgres, Grafana)
- [ ] 7.6 Summary
- [ ] 7.7 Chunking for longer texts

**Must be able to do/explain:**
- [ ] Map every course-project criterion to a part of this example.
- [ ] Explain at least two chunking strategies and when to use them.

**Estimated hours:** ~6 h

**Self-check questions**
1. Why chunk long documents?
2. What is a sensible first chunking strategy?
3. What makes a project reproducible for a peer reviewer?

---
**Answers**
1. Long texts dilute embeddings and do not fit (or waste) the context window; smaller chunks retrieve more precisely.
2. Fixed-size chunks with overlap, or splitting by document structure (headings, paragraphs, slides).
3. Clear README, pinned dependencies, data included or downloadable, one command (e.g. `docker compose up`) to run it.

### Course project — LLM Zoomcamp

**Official requirements** (`project.md`): one end-to-end RAG and/or agent
application; **2 attempts**; you must not use the course FAQ dataset; peer
review 3 other projects (+3 points each). Certificate: project + 3 peer
reviews in a live cohort.

**Evaluation criteria** (0–2 points each unless stated):
problem description · retrieval flow · retrieval evaluation · LLM
evaluation · interface · ingestion pipeline (automated, e.g. Kestra/dlt/
Airflow) · monitoring (user feedback + a dashboard with ≥5 charts) ·
containerization (everything in docker-compose) · reproducibility.
Best practices (1 point each): hybrid search · document re-ranking · user
query rewriting. Bonus: cloud deployment (2) + up to 3 extra points.

**Milestones**
- [ ] Problem and dataset chosen (not the course FAQ), written in the README
- [ ] Ingestion pipeline automated
- [ ] Retrieval flow working; retrieval evaluated (hit rate / MRR) and the best approach chosen
- [ ] RAG answers evaluated (LLM-as-a-judge), best prompt/model chosen
- [ ] Interface (API or UI) working
- [ ] Monitoring: feedback collected + dashboard with ≥5 charts
- [ ] Everything runs with docker-compose; reproducibility checked on a clean machine
- [ ] Best practices: hybrid search / re-ranking / query rewriting (optional points)
- [ ] (Bonus) Cloud deployment
- [ ] Submitted
- [ ] 3 peer reviews done

**Estimated hours:** ~25 h

---

## Course 3.2 — AI Dev Tools Zoomcamp (~60h)

**Repo:** https://github.com/DataTalksClub/ai-dev-tools-zoomcamp
**Official length:** 2026 cohort ran ~4–5 weeks (Aug 31 – Sep 28, 2026). The
README warns the 2026 materials, homework and project "are being
finalized" and may change — re-check each module README before you start.
**Official prerequisites:** basic programming (Python/JS/TS or similar),
command line, Git/GitHub. Web development and Docker are helpful but not
required. No prior AI-tools experience or GPU needed.
**Required knowledge from other tracks:** 1A.1 Git, B3 Docker & Compose,
B4 FastAPI, B9 GitHub Actions. Helpful: B21 React + TS (frontend
prototype), B24 logging & monitoring (Module 4), B19 web security.
**Homework location:** `cohorts/2026/homework/<module>/homework.md`
(https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/tree/main/cohorts/2026).

> The module READMEs are short unit pages; the lesson list below is the
> unit's section/deliverable list. Watch the linked video for each unit.

### Module 1 — AI-Native Developer Workflow (`01-ai-native-workflow`)

**Topics:** spec-driven development (idea → spec → backlog), context
engineering, `AGENTS.md`, PM / engineer / QA agent roles, loop engineering,
graph engineering. Examples: `weekly-feedback` (no spec — cautionary) vs
`retroloop` (Django app built after a spec).

- [ ] Unit video: AI-Native Developer Workflow
- [ ] Companion article on specifications and engineering approaches
- [ ] Study the two example projects (weekly-feedback vs retroloop)
- [ ] (Optional) 2025 archived module materials
- [ ] **Homework** — `cohorts/2026/homework/01-ai-native-workflow/homework.md` (deadline was 2026-09-07) [verify folder name]

**Must be able to do/explain:**
- [ ] Turn an idea into a product spec, user stories and a backlog before asking an agent for code.
- [ ] Write an `AGENTS.md`/`CLAUDE.md` for a project.
- [ ] Explain why "one-sentence" implementations go wrong.

**Estimated hours:** ~6 h

**Self-check questions**
1. What is spec-driven development?
2. What belongs in `AGENTS.md`?
3. Why separate PM, engineer and QA roles when working with agents?
4. What does "context engineering" mean for a coding agent?
5. What went wrong in the no-spec example?

---
**Answers**
1. Writing the product spec and acceptance criteria first, then letting the agent implement against it, instead of prompting code directly.
2. Architecture, commands to build/test/run, conventions, constraints and security rules — what a new engineer needs to work safely.
3. Each role checks a different thing (what to build, how to build it, whether it works); mixing them lets errors pass unchecked.
4. Giving the agent the right files, docs, conventions and constraints so it changes the right code in the right way.
5. Without requirements the agent guessed; the result did not match intent and was hard to evolve.

### Module 2 — Build and Ship an AI-Assisted Full-Stack App (`02-development`)

**Topics:** product spec with user stories, AI frontend prototype (Lovable,
Bolt, Cursor, Claude Code, Codex), OpenAPI contract as the source of truth,
FastAPI backend with mock DB and tests, migrating to SQLite, unit and
frontend tests, AI-usage report. Reference app: Snake Arena
(https://github.com/alexeygrigorev/interview-canvas-share).

- [ ] Unit video: Build and Ship an AI-Assisted Full-Stack App
- [ ] Companion article (AI Shipping blog)
- [ ] Deliverables in your repo: `product-spec.md`, `AGENTS.md`, `frontend/`, `backend/`, `openapi.yaml`, `tests/`, `docs/ai-usage-report.md`
- [ ] App runs locally, persists data in SQLite and passes all tests
- [ ] **Homework** — `cohorts/2026/homework/02-development/homework.md` (deadline was 2026-09-14) [verify folder name]

**Must be able to do/explain:**
- [ ] Define an OpenAPI contract first and keep frontend and backend to it.
- [ ] Review AI-generated code instead of accepting it blindly.
- [ ] Explain what you measured/recorded in the AI-usage report.

**Estimated hours:** ~12 h

**Self-check questions**
1. Why make the OpenAPI file the source of truth?
2. Why start with a mock database?
3. How do you check AI-generated backend code?
4. What goes into an AI-usage report?
5. What risk does a fast AI prototype create?

---
**Answers**
1. Frontend and backend can be built (and generated) independently and still fit; contract tests catch drift.
2. It lets you shape the API and tests before committing to storage details; swapping to SQLite later tests your layering.
3. Read the diff, run tests, add tests for edge cases, run linters/type checks, check for secrets and injection.
4. Which tools/prompts were used for what, what worked, what had to be fixed by hand, time spent.
5. Code nobody fully understands; hidden bugs and security holes that surface later.

### Module 3 — Test, Containerize, and Deploy an AI-Assisted App (`03-deployment`)

**Topics:** integration tests (real DB, migrations, auth, frontend-backend
flows), multi-stage Dockerfile, Docker Compose with PostgreSQL, GitHub
Actions CI (lint, unit, integration, image build), deploy to a public
platform (AWS, Render, Fly.io, Railway or Cloud Run) with a managed DB,
CD with staging/production and rollback docs; Playwright E2E tests.

- [ ] Unit video: Test, Containerize, and Deploy an AI-Assisted App
- [ ] Integration tests: `tests/integration/`
- [ ] `Dockerfile` (multi-stage) + `docker-compose.yml` with PostgreSQL
- [ ] `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`
- [ ] Docs: `docs/testing.md`, `docs/deployment.md`, `docs/release-process.md`
- [ ] **Homework** — `cohorts/2026/homework/03-deployment/homework.md` (marked DRAFT; deadline was 2026-09-21) [verify folder name]

**Must be able to do/explain:**
- [ ] Run integration tests against a real Postgres in CI.
- [ ] Deploy with automated migrations and a documented rollback.
- [ ] Explain the path: integration tests → container → CI → deploy → CD.

**Estimated hours:** ~10 h

**Self-check questions**
1. What do integration tests catch that unit tests miss?
2. Why switch from SQLite to PostgreSQL before deploying?
3. What must the CD pipeline do before a production deploy?
4. How do you roll back a bad release with a migration in it?
5. Why run migrations automatically?

---
**Answers**
1. Real wiring: DB schema and migrations, auth, serialization, and how frontend and backend actually talk.
2. Production uses Postgres; dialect, locking and concurrency differ, so you want to test what you ship.
3. Build and test the image, deploy to staging, verify health/smoke tests, then promote the same image.
4. Keep migrations backward-compatible (expand/contract) so the previous image still works; roll back the image, not the schema.
5. Manual steps get forgotten or run in the wrong order; automation makes every environment consistent.

### Module 4 — DevOps and Observability for AI-Built Apps (`04-devops`)

**Topics:** dev/prod split, versioned releases, OpenTelemetry →
Prometheus / Loki / Tempo / Grafana, alerts that represent user impact,
bounded evidence packets, a read-only AI "first responder" agent (Codex or
Claude Code headless), allowlists for automated actions, security audits
(Semgrep, Snyk Agent Scan). Related tools mentioned: HolmesGPT, K8sGPT,
PR-Agent, LiteLLM, Ollama, garak.

- [ ] Unit video: DevOps and Observability for AI-Built Apps
- [ ] Section: Where the other tools fit
- [ ] Section: Non-goals
- [ ] `observability/` — collector, compose, dashboard, alerts
- [ ] `incident-response/` — evidence collection, responder task, schema, policy, runbooks, incidents
- [ ] `security-audit/` — brief, findings schema, capability table, audit runs
- [ ] `docs/operations-and-security-report.md`
- [ ] **Homework** — `cohorts/2026/homework/04-devops/homework.md` (marked DRAFT; deadline was 2026-09-28) [verify folder name]

**Must be able to do/explain:**
- [ ] Instrument endpoints with metrics, traces and logs via OpenTelemetry.
- [ ] Write an alert that reflects user impact, not just CPU.
- [ ] Run a read-only responder agent and explain why it is read-only.
- [ ] Reconstruct an incident from your report (version, impact, evidence, recovery).

**Estimated hours:** ~8 h

**Self-check questions**
1. Why should the first AI responder be read-only?
2. What is an "evidence packet" and why bound it?
3. Give an example of a user-impact alert.
4. Metrics, logs, traces: what is each best for?
5. Why gate automated actions behind an allowlist?

---
**Answers**
1. A wrong diagnosis must not become a wrong action in production; humans approve changes.
2. A limited, structured set of logs/metrics/traces around an incident; bounding it controls cost, leaks and prompt-injection surface.
3. "Error rate of `/checkout` > 2% for 5 minutes" or "p95 latency > 1 s" rather than "CPU > 80%".
4. Metrics: trends and alerting; logs: details of individual events; traces: where time goes across services for one request.
5. So an agent can only perform known-safe operations; anything else needs a human.

### Module 5 — Agent Capabilities (`05-agent-capabilities`)

**Topics:** mental model (instructions, context, tools, permissions,
workflows, agents, packaging, loops, audit trails), the agent loop,
portable project instructions, MCP for scoped tool access, reusable
workflows (skills, commands, rules, recipes), hooks and guardrails,
specialized subagents, plugins/extensions, custom agents in CI/CD and
scheduled jobs, parallel work in Git worktrees. Tools: Claude Code, Codex,
OpenCode, Cursor, GitHub Copilot, Aider, Windsurf.

- [ ] 5.1 Overview
- [ ] 5.2 Mental model
- [ ] 5.3 Understanding the agent loop
- [ ] 5.4 Portable project instructions
- [ ] 5.5 MCP for scoped tool access
- [ ] 5.6 Reusable workflows (skills, commands, rules, recipes)
- [ ] 5.7 Hooks and guardrails
- [ ] 5.8 Specialized subagents
- [ ] 5.9 Plugins and extensions
- [ ] 5.10 Custom agents (CI/CD, scheduled jobs, pipelines)
- [ ] 5.11 Companion article: "Reusable Skills and Specialized Subagents"
- [ ] **Deliverable (no graded homework): Agent Extension Pack** — project instructions file, one reusable workflow/skill/command, one specialized subagent, one MCP tool/server, one hook or guardrail, one plugin/extension or custom agent, and a permission/security note
- [ ] Demo: instructions → reusable workflow → subagent reviews an API change → MCP tool call → hook/guardrail action → diff review

**Must be able to do/explain:**
- [ ] Build a small MCP server that exposes one scoped tool.
- [ ] Write a hook that blocks an unsafe action.
- [ ] Explain when a subagent is better than a bigger prompt.

**Estimated hours:** ~6 h

**Self-check questions**
1. What is MCP and why "scoped" tool access?
2. What is the difference between a skill and a subagent?
3. What is a hook good for?
4. Why use Git worktrees for parallel agents?
5. What belongs in the permission/security note?

---
**Answers**
1. Model Context Protocol: a standard way to expose tools/resources to agents; scoping limits what the agent can touch (e.g. read-only DB).
2. A skill is reusable instructions/workflow loaded into the current context; a subagent runs with its own isolated context and permissions.
3. Deterministic checks around agent actions: formatting, linting, blocking dangerous commands.
4. Each agent works on its own checkout/branch, so parallel edits don't collide.
5. Which tools/commands each component may use, what is forbidden, and how secrets and data are protected.

### Course project — AI Dev Tools Zoomcamp

**Official requirements** (`project/README.md`, marked **DRAFT**): one final
project — a full-stack app built with AI assistance and deployed. Expected
repo contents: `product-spec.md`, `AGENTS.md`, `frontend/`, `backend/`,
`openapi.yaml`, `docker-compose.yml`, `.github/workflows/`, `security/`,
`ops/`, plus optional agent-extension folders (`mcp-server/`,
`agent-hooks/`, …). Peer review is required; the exact 2026 count is not
set yet [verify].

**Evaluation criteria** (14; mostly 0–2 points, frontend and backend up to
3): problem · AI workflow documentation · architecture · frontend · API
contract · backend · database · containerization · integration tests ·
deployment · CI/CD · agent extension pack · security/audit hardening ·
reproducibility.

**Milestones**
- [ ] Idea chosen; `product-spec.md` and `AGENTS.md` written
- [ ] `openapi.yaml` contract defined
- [ ] Frontend and backend implemented against the contract
- [ ] Database wired; integration tests pass
- [ ] Containerized (`docker-compose.yml`)
- [ ] CI/CD workflows; app deployed publicly
- [ ] Agent extension pack added
- [ ] Security/audit and ops folders filled
- [ ] Reproducibility checked from a clean clone
- [ ] Submitted
- [ ] Peer reviews done

**Estimated hours:** ~18 h

---

## Course 3.3 — Machine Learning Zoomcamp (~150h)

**Repo:** https://github.com/DataTalksClub/machine-learning-zoomcamp
**Official length:** 2026 cohort Sep 14, 2026 – Jan 25, 2027 (modules
Sep–Dec, projects in Nov–Jan).
**Official prerequisites:** at least 1 year of programming, command line.
Python and Git helpful. No prior ML, cloud, Kubernetes or GPU needed.
**Required knowledge from other tracks:** 1A (Python), B3 Docker, B4
FastAPI (Module 5 now serves models with FastAPI). Helpful: B30
Kubernetes (Module 10), B33 cloud basics (Modules 5, 9, 10).
**Homework location:** `cohorts/2026/homework/<module>/`
(https://github.com/DataTalksClub/machine-learning-zoomcamp/tree/master/cohorts/2026);
2026 datasets are in `cohorts/2026/data/`. Homework deadlines are Mondays
23:00 UTC.

> Several module READMEs say parts of the videos are **partly outdated**
> and point to the updated **workshop** materials in the module folder —
> follow the workshop when the README says so.

### Module 1 — Introduction to Machine Learning (`01-intro`)

**Topics:** ML vs rule-based systems, supervised learning, CRISP-DM, model
selection, environment setup, NumPy, linear algebra refresher, Pandas.

- [ ] 1.1 Introduction to machine learning
- [ ] 1.2 ML vs rule-based systems
- [ ] 1.3 Supervised machine learning
- [ ] 1.4 CRISP-DM
- [ ] 1.5 The modelling step (model selection process)
- [ ] 1.6 Setting up the environment
- [ ] 1.7 Introduction to NumPy
- [ ] 1.8 Linear algebra refresher
- [ ] 1.9 Introduction to Pandas
- [ ] 1.10 Summary
- [ ] **Homework** — `cohorts/2026/homework/01-intro/` (deadline 2026-09-21)

**Must be able to do/explain:**
- [ ] Explain features, target, model, training vs prediction.
- [ ] Explain train/validation/test and why the test set is touched last.
- [ ] Do basic NumPy (vector/matrix ops) and Pandas (filter, group, describe).

**Estimated hours:** ~8 h

**Self-check questions**
1. When is ML better than hand-written rules?
2. What is supervised learning?
3. Name the CRISP-DM steps.
4. Why do we need a validation set as well as a test set?
5. What does matrix–vector multiplication compute in a linear model?

---
**Answers**
1. When rules are too many, change often or can't be written down, but labelled examples exist (e.g. spam).
2. Learning a function from input features to a known target using labelled examples.
3. Business understanding, data understanding, data preparation, modelling, evaluation, deployment.
4. You tune and select models on validation; the test set gives an unbiased final estimate only if you never tuned on it.
5. One prediction per row: each is the dot product of the row's features with the weight vector.

### Module 2 — Machine Learning for Regression (`02-regression`)

**Topics:** car price prediction project, data preparation, EDA,
validation framework, linear regression (vector form, normal equation),
baseline, RMSE, feature engineering, categorical variables,
regularization, tuning, using the model.

- [ ] 2.1 Car price prediction project
- [ ] 2.2 Data preparation
- [ ] 2.3 Exploratory data analysis
- [ ] 2.4 Setting up the validation framework
- [ ] 2.5 Linear regression
- [ ] 2.6 Linear regression: vector form
- [ ] 2.7 Training linear regression: normal equation
- [ ] 2.8 Baseline model
- [ ] 2.9 Root mean squared error
- [ ] 2.10 Using RMSE on validation data
- [ ] 2.11 Feature engineering
- [ ] 2.12 Categorical variables
- [ ] 2.13 Regularization
- [ ] 2.14 Tuning the model
- [ ] 2.15 Using the model
- [ ] 2.16 Project summary
- [ ] 2.17 Explore more
- [ ] **Homework** — `cohorts/2026/homework/02-regression/` (deadline 2026-09-28)

**Must be able to do/explain:**
- [ ] Implement linear regression with the normal equation in NumPy.
- [ ] Explain RMSE and compare a model with a baseline.
- [ ] Explain why and how regularization helps.
- [ ] One-hot encode categorical features.

**Estimated hours:** ~12 h

**Self-check questions**
1. Why log-transform a skewed target like price?
2. What is the normal equation and when does it fail?
3. What does RMSE measure?
4. What does regularization do to the weights?
5. Why build a baseline first?

---
**Answers**
1. It reduces the effect of huge values and makes errors relative, which usually fits linear models better.
2. w = (XᵀX)⁻¹Xᵀy; it fails or is unstable when XᵀX is singular/ill-conditioned (e.g. duplicate or highly correlated features).
3. The typical size of prediction errors, in the target's units, penalizing large errors more.
4. Adds a penalty that keeps weights small, making XᵀX invertible and reducing overfitting.
5. To know whether a complex model is actually better than something trivial.

### Module 3 — Machine Learning for Classification (`03-classification`)

**Topics:** churn prediction project, validation framework, EDA, feature
importance (churn rate, risk ratio, mutual information, correlation),
one-hot encoding, logistic regression with scikit-learn, model
interpretation.

- [ ] 3.1 Churn prediction project
- [ ] 3.2 Data preparation
- [ ] 3.3 Setting up the validation framework
- [ ] 3.4 EDA
- [ ] 3.5 Feature importance: churn rate and risk ratio
- [ ] 3.6 Feature importance: mutual information
- [ ] 3.7 Feature importance: correlation
- [ ] 3.8 One-hot encoding
- [ ] 3.9 Logistic regression
- [ ] 3.10 Training logistic regression with scikit-learn
- [ ] 3.11 Model interpretation
- [ ] 3.12 Using the model
- [ ] 3.13 Summary
- [ ] 3.14 Explore more
- [ ] **Homework** — `cohorts/2026/homework/03-classification/` (deadline 2026-10-05)

**Must be able to do/explain:**
- [ ] Train and interpret a logistic regression.
- [ ] Rank features by risk ratio and mutual information.
- [ ] Explain what the sigmoid output means.

**Estimated hours:** ~10 h

**Self-check questions**
1. What does logistic regression output?
2. What is a risk ratio?
3. When use mutual information vs correlation?
4. Why fit the one-hot encoder on training data only?
5. How do you read a logistic regression coefficient?

---
**Answers**
1. A probability between 0 and 1 via the sigmoid of a linear score.
2. Group churn rate divided by global churn rate; >1 means higher risk than average.
3. Mutual information for categorical features; correlation for numerical ones.
4. To avoid leaking information from validation/test data into training.
5. Positive pushes the probability up, negative down; the size is the change in log-odds per unit of the feature.

### Module 4 — Evaluation Metrics for Classification (`04-evaluation`)

**Topics:** accuracy and dummy model, confusion table, precision and
recall, ROC curves, ROC AUC, cross-validation.

- [ ] 4.1 Session overview
- [ ] 4.2 Accuracy and dummy model
- [ ] 4.3 Confusion table
- [ ] 4.4 Precision and recall
- [ ] 4.5 ROC curves
- [ ] 4.6 ROC AUC
- [ ] 4.7 Cross-validation
- [ ] 4.8 Summary
- [ ] 4.9 Explore more
- [ ] **Homework** — `cohorts/2026/homework/04-evaluation/` (deadline 2026-10-12)

**Must be able to do/explain:**
- [ ] Build a confusion table and compute precision, recall, F1.
- [ ] Draw and read a ROC curve; explain AUC.
- [ ] Use k-fold cross-validation to compare models.

**Estimated hours:** ~8 h

**Self-check questions**
1. Why can accuracy mislead on imbalanced data?
2. Define precision and recall.
3. What does ROC AUC mean intuitively?
4. When do you prefer recall over precision?
5. Why use k-fold cross-validation?

---
**Answers**
1. A dummy model predicting the majority class can score high while being useless.
2. Precision = TP/(TP+FP): how many predicted positives are right. Recall = TP/(TP+FN): how many real positives are found.
3. The probability that a random positive is scored higher than a random negative.
4. When missing a positive is expensive (fraud, disease, churn you could prevent).
5. It gives a more stable estimate with a spread, using all data for both training and validation.

### Module 5 — Deploying Machine Learning Models (`05-deployment`)

**Topics:** saving/loading models (pickle), web services, serving the churn
model, environment management, Docker, cloud deployment. The 2026 cohort
uses **FastAPI** (videos show Flask/Pipenv and are partly outdated — use
the workshop materials).

- [ ] 5.1 Intro / session overview
- [ ] 5.2 Saving and loading the model
- [ ] 5.3 Web services: introduction (Flask in the videos)
- [ ] 5.4 Serving the churn model
- [ ] 5.5 Python virtual environment (Pipenv in the videos)
- [ ] 5.6 Environment management: Docker
- [ ] 5.7 Deployment to the cloud: AWS Elastic Beanstalk (optional)
- [ ] 5.8 Summary
- [ ] Updated workshop in the module folder
- [ ] **Homework** — `cohorts/2026/homework/05-deployment/` (deadline 2026-10-19)

**Must be able to do/explain:**
- [ ] Wrap a trained model in an HTTP service and containerize it.
- [ ] Explain why preprocessing must be saved with the model.
- [ ] Deploy the container somewhere public.

**Estimated hours:** ~10 h

**Self-check questions**
1. What exactly must you save besides the model weights?
2. Why load the model once at startup, not per request?
3. What goes into the Docker image for a model service?
4. Why pin dependency versions?

---
**Answers**
1. The whole preprocessing pipeline (e.g. DictVectorizer/encoder) and any thresholds, so inputs are transformed exactly as in training.
2. Loading is slow; per-request loading kills latency and wastes memory.
3. Pinned Python deps, the model file, the service code, and a command to start the server.
4. A different library version can change behaviour or fail to unpickle the model.

### Module 6 — Decision Trees and Ensemble Learning (`06-trees`)

**Topics:** credit risk scoring project, data cleaning, decision trees and
their learning algorithm, parameter tuning, random forest, gradient
boosting and XGBoost, XGBoost tuning, model selection.

- [ ] 6.1 Credit risk scoring project
- [ ] 6.2 Data cleaning and preparation
- [ ] 6.3 Decision trees
- [ ] 6.4 Decision tree learning algorithm
- [ ] 6.5 Decision trees parameter tuning
- [ ] 6.6 Ensemble learning and random forest
- [ ] 6.7 Gradient boosting and XGBoost
- [ ] 6.8 XGBoost parameter tuning
- [ ] 6.9 Selecting the best model
- [ ] 6.10 Summary
- [ ] 6.11 Explore more
- [ ] **Homework** — `cohorts/2026/homework/06-trees/` (deadline 2026-10-26)

**Must be able to do/explain:**
- [ ] Explain how a tree chooses a split (impurity).
- [ ] Explain bagging vs boosting.
- [ ] Tune max_depth / min_samples_leaf / eta / n_estimators with validation.

**Estimated hours:** ~12 h

**Self-check questions**
1. Why do deep decision trees overfit?
2. How does a random forest reduce variance?
3. How does gradient boosting differ from random forest?
4. What does the learning rate (eta) control in XGBoost?
5. Why use early stopping?

---
**Answers**
1. They can keep splitting until each leaf fits a few training rows, memorizing noise.
2. It averages many trees trained on bootstrap samples and random feature subsets, so their errors partly cancel.
3. Boosting builds trees sequentially, each fixing the previous errors; a forest builds independent trees in parallel.
4. How much each new tree contributes; smaller eta needs more trees but usually generalizes better.
5. To stop adding trees once validation performance stops improving, avoiding overfitting and wasted time.

### Midterm project (Module 7 — no module folder)

See **Course projects** below. Submission 2026-11-09, peer review
2026-11-16.

- [ ] Midterm project submitted
- [ ] 3 peer reviews done

### Module 8 — Neural Networks and Deep Learning (`08-deep-learning`)

**Topics:** fashion classification, TensorFlow and Keras, pre-trained CNNs,
convolutional networks, transfer learning, learning rate, checkpointing,
more layers, dropout, data augmentation, larger models. A **PyTorch**
re-recording lives in `08-deep-learning/pytorch/` (implementation only;
the theory is in the Keras videos). You may do either framework or both.

- [ ] 8.1 Fashion classification
- [ ] 8.2 TensorFlow and Keras (or the PyTorch setup)
- [ ] 8.3 Pre-trained convolutional neural networks
- [ ] 8.4 Convolutional neural networks
- [ ] 8.5 Transfer learning
- [ ] 8.6 Adjusting the learning rate
- [ ] 8.7 Checkpointing
- [ ] 8.8 Adding more layers
- [ ] 8.9 Regularization and dropout
- [ ] 8.10 Data augmentation
- [ ] 8.11 Training a larger model
- [ ] 8.12 Using the model
- [ ] 8.13 Summary
- [ ] 8.14 Explore more
- [ ] **Homework** — `cohorts/2026/homework/08-deep-learning/` (deadline 2026-11-23)

**Must be able to do/explain:**
- [ ] Explain convolution, pooling and dense layers.
- [ ] Do transfer learning from a pre-trained model.
- [ ] Use dropout, augmentation and checkpoints to fight overfitting.

**Estimated hours:** ~16 h

**Self-check questions**
1. Why do CNNs work well on images?
2. What is transfer learning?
3. What does dropout do during training?
4. Why augment data?
5. What happens if the learning rate is too high?

---
**Answers**
1. Convolutions reuse the same small filters across the image, detecting local patterns regardless of position with few parameters.
2. Reusing a model trained on a big dataset as a feature extractor and training only a new head (then optionally fine-tuning).
3. Randomly zeroes activations so the network can't rely on single units; it reduces overfitting.
4. To create more varied training examples (flips, shifts, zoom) so the model generalizes better.
5. Training becomes unstable or diverges; loss jumps around instead of decreasing.

### Module 9 — Serverless Deep Learning (`09-serverless`)

**Topics:** serverless, AWS Lambda, TensorFlow Lite, Docker images for
Lambda, API Gateway. **Lessons 9.3–9.6 are marked outdated** (don't work
with newer Python) — use the workshop materials for them.

- [ ] 9.1 Introduction to serverless
- [ ] 9.2 AWS Lambda
- [ ] 9.3 TensorFlow Lite (outdated → workshop)
- [ ] 9.4 Preparing the code for Lambda (outdated → workshop)
- [ ] 9.5 Preparing a Docker image (outdated → workshop)
- [ ] 9.6 Creating the Lambda function (outdated → workshop)
- [ ] 9.7 API Gateway: exposing the Lambda function
- [ ] 9.8 Summary
- [ ] **Homework** — `cohorts/2026/homework/09-serverless/` (deadline 2026-11-30)

**Must be able to do/explain:**
- [ ] Package a model as a container image for Lambda.
- [ ] Expose it through API Gateway.
- [ ] Explain cold starts and when serverless is a bad fit.

**Estimated hours:** ~8 h

**Self-check questions**
1. What is a cold start?
2. Why use a lighter runtime (e.g. TF Lite / ONNX) on Lambda?
3. When is serverless a poor choice for model serving?

---
**Answers**
1. The delay when the platform must start a new container and load the model before handling the first request.
2. Smaller images and faster load/inference fit Lambda's size, memory and time limits.
3. Steady high traffic, big models/GPUs, or strict low-latency needs where cold starts hurt.

### Module 10 — Kubernetes and TensorFlow Serving (`10-kubernetes`)

**Topics:** TensorFlow Serving, a pre-processing gateway service, Docker
Compose locally, Kubernetes intro, deploying services and models to
Kubernetes, EKS. Materials are **partly outdated**; a workshop has the
updated content (10.5 and 10.8 still useful).

- [ ] 10.1 Overview
- [ ] 10.2 TensorFlow Serving
- [ ] 10.3 Creating a pre-processing service
- [ ] 10.4 Running everything locally with docker-compose
- [ ] 10.5 Introduction to Kubernetes
- [ ] 10.6 Deploying a simple service to Kubernetes
- [ ] 10.7 Deploying TensorFlow models to Kubernetes
- [ ] 10.8 Deploying to EKS
- [ ] 10.9 Summary
- [ ] Updated workshop in the module folder
- [ ] **Homework** — `cohorts/2026/homework/10-kubernetes/` (deadline 2026-12-07)

**Must be able to do/explain:**
- [ ] Split model serving from pre-processing and explain why.
- [ ] Deploy both to a local cluster (kind) with Deployments and Services.
- [ ] Scale the model deployment and explain HPA.

**Estimated hours:** ~10 h

**Self-check questions**
1. Why separate a gateway (pre-processing) from the model server?
2. What do a Deployment and a Service do?
3. How does the gateway find the model server in Kubernetes?
4. What would you autoscale on?

---
**Answers**
1. They scale differently (CPU vs GPU/memory) and change at different speeds; the model server stays generic.
2. A Deployment keeps N pod replicas running and handles rollouts; a Service gives them a stable name/IP and load-balances.
3. Through the Service DNS name (e.g. `tf-serving.default.svc.cluster.local`).
4. CPU or request rate/latency per pod, via a HorizontalPodAutoscaler.

### Module 11 — KServe (`11-kserve`) · OPTIONAL

Marked by the course as **optional and possibly outdated**; not part of the
README syllabus. No homework.

- [ ] 11.1 Overview
- [ ] 11.2 Running KServe locally
- [ ] 11.3 Deploying a scikit-learn model with KServe
- [ ] 11.4 Deploying custom scikit-learn images with KServe
- [ ] 11.5 Serving TensorFlow models with KServe
- [ ] 11.6 KServe transformers
- [ ] 11.7 Deploying with KServe and EKS
- [ ] 11.8 Summary

**Estimated hours:** ~6 h (optional, not in the course total)

### Course projects — ML Zoomcamp

**Official requirements** (`projects/README.md`): three chances — the
**midterm** (submit 2026-11-09, review 11-16), **Capstone 1** (submit
2027-01-04, review 01-11) and **Capstone 2** (submit 01-18, review 01-25).
**Certificate: 2 passing projects** (midterm + one capstone, or both
capstones). Each project needs **3 peer reviews** — skipping them fails the
project. Course datasets (car price, telco churn, credit risk, clothing)
are not allowed.

**Deliverables:** README with the problem, data (or instructions to get
it), `notebook.ipynb` (EDA, training, tuning), `train.py`, `predict.py`
(service), dependency file (e.g. Pipfile/uv lock/requirements), Dockerfile,
proof of deployment.

**Evaluation criteria (16 points max):** problem description 2 · EDA 2 ·
model training 3 · exporting notebook to script 1 · reproducibility 1 ·
model deployment 1 · dependency & environment management 2 ·
containerization 2 · cloud deployment 2.

**Milestones — Project 1 (midterm)**
- [ ] Problem and dataset chosen (not a course dataset)
- [ ] EDA done in `notebook.ipynb`
- [ ] Several models trained and tuned; best one selected
- [ ] `train.py` and `predict.py` exported
- [ ] Dependencies pinned; Dockerfile builds
- [ ] Deployed (locally with proof, or to the cloud for full points)
- [ ] Submitted
- [ ] 3 peer reviews done

**Milestones — Project 2 (capstone)**
- [ ] Problem and dataset chosen
- [ ] EDA done
- [ ] Models trained and tuned (consider trees or deep learning)
- [ ] Scripts exported
- [ ] Dependencies + Dockerfile
- [ ] Deployed to the cloud
- [ ] Submitted
- [ ] 3 peer reviews done

**Estimated hours:** midterm ~20 h (listed above in the module flow) + capstone ~36 h

---

## Course 3.4 — MLOps Zoomcamp (~90h)

**Repo:** https://github.com/DataTalksClub/mlops-zoomcamp
**Official length:** 9 weeks. **No live cohort in 2026** — self-paced only
(`cohorts/self-paced/`). Last live cohort: 2025 (May 9 – Aug 29, 2025).
**Official prerequisites:** Python, Docker, command line, ML basics (e.g.
ML Zoomcamp), 1+ year of programming.
**Required knowledge from other tracks:** **Course 3.3 ML Zoomcamp**
(at least Modules 1–6), B3 Docker & Compose, B9 GitHub Actions, 1A.8
pytest, 1A.9 ruff/pre-commit. Helpful: B24 monitoring (Grafana), B33 cloud
+ Terraform (Module 6), B16 Kafka concepts (streaming deployment).
**Homework location:** latest set is `cohorts/2025/<module>/homework.md`
(https://github.com/DataTalksClub/mlops-zoomcamp/tree/main/cohorts/2025).

### Module 1 — Introduction (`01-intro`)

**Topics:** what MLOps is, dev environment (GitHub Codespaces or an AWS
VM), reading Parquet, training a ride-duration model on NYC taxi data,
course overview, MLOps maturity model.

- [ ] 1.1 Introduction
- [ ] 1.2 GitHub Codespaces
- [ ] 1.3 VM in AWS
- [ ] 1.4 Reading Parquet data
- [ ] 1.5 Training a ride duration prediction model
- [ ] 1.6 Course overview
- [ ] 1.7 MLOps maturity model
- [ ] **Homework** — `cohorts/2025/01-intro/homework.md`

**Must be able to do/explain:**
- [ ] Explain what MLOps adds after "the model works in a notebook".
- [ ] Place a team on the MLOps maturity model (levels 0–4).

**Estimated hours:** ~6 h

**Self-check questions**
1. What problems does MLOps solve?
2. What is level 0 of the maturity model?
3. Why is a notebook not a production artifact?

---
**Answers**
1. Reproducible training, tracked experiments, automated pipelines, reliable deployment and monitoring of models in production.
2. No MLOps: manual notebooks, no automation, no tracking.
3. Hidden state, run order issues, no tests, hard to parameterize and schedule.

### Module 2 — Experiment Tracking and Model Management (`02-experiment-tracking`)

**Topics:** experiment tracking, MLflow (tracking server, backend store,
artifacts), model management, model registry, MLflow in practice,
limitations and alternatives.

- [ ] 2.1 Experiment tracking intro
- [ ] 2.2 Getting started with MLflow
- [ ] 2.3 Experiment tracking with MLflow
- [ ] 2.4 Model management
- [ ] 2.5 Model registry
- [ ] 2.6 MLflow in practice
- [ ] 2.7 MLflow: benefits, limitations and alternatives
- [ ] **Homework** — `cohorts/2025/02-experiment-tracking/homework.md`

**Must be able to do/explain:**
- [ ] Log params, metrics and artifacts for every run.
- [ ] Register a model and move versions between stages/aliases.
- [ ] Choose an MLflow setup (local, remote server, cloud artifact store).

**Estimated hours:** ~10 h

**Self-check questions**
1. What should an experiment run record?
2. What is the model registry for?
3. What is the difference between the backend store and the artifact store?
4. When do you need a remote tracking server?

---
**Answers**
1. Code version, parameters, data version, metrics, artifacts (model, plots) and environment.
2. A single place to version models and mark which version is staging/production, with history and approvals.
3. The backend store keeps run metadata (params, metrics); the artifact store keeps files (models, plots).
4. When several people or machines (CI, orchestrator) must log to and read from the same place.

### Module 3 — Orchestration and ML Pipelines (`03-orchestration`)

**Topics:** ML pipelines, turning a notebook into a parameterized script,
using an orchestrator. The orchestrator is **your choice** (Airflow or
Prefect suggested; Dagster, Kestra, Mage also mentioned).

- [ ] 3.1 Introduction to ML pipelines
- [ ] 3.2 Turning the notebook into a Python script
- [ ] 3.3 Using an orchestrator
- [ ] **Homework** — `cohorts/2025/03-orchestration/homework.md`

**Must be able to do/explain:**
- [ ] Turn a notebook into a parameterized, repeatable training script.
- [ ] Run it as a scheduled pipeline with retries in one orchestrator.

**Estimated hours:** ~10 h

**Self-check questions**
1. What makes a training script "repeatable"?
2. What does an orchestrator add over cron?
3. Which steps belong in a training pipeline?

---
**Answers**
1. Parameters instead of hard-coded values, fixed seeds, versioned data inputs, no manual steps.
2. Dependencies between tasks, retries, backfills, run history, parameters and alerts.
3. Ingest → prepare features → train → evaluate → register (if better).

### Module 4 — Model Deployment (`04-deployment`)

**Topics:** three ways to deploy (web service, streaming, batch), Flask +
Docker web service, getting models from the registry, streaming with AWS
Kinesis + Lambda, batch scoring script, batch scoring with Mage.

- [ ] 4.1 Three ways of deploying a model
- [ ] 4.2 Web services: deploying models with Flask and Docker
- [ ] 4.3 Web services: getting models from the model registry
- [ ] 4.4 Streaming: deploying models with Kinesis and Lambda
- [ ] 4.5 Batch: preparing a scoring script
- [ ] 4.6 Batch scoring with Mage
- [ ] **Homework** — `cohorts/2025/04-deployment/homework.md`

**Must be able to do/explain:**
- [ ] Choose between online, streaming and batch deployment for a use case.
- [ ] Load a specific model version from the registry in a service.
- [ ] Write a batch scoring job.

**Estimated hours:** ~12 h

**Self-check questions**
1. When is batch scoring the right choice?
2. When do you need streaming deployment?
3. Why load the model from the registry instead of baking a file into the image?
4. What must a scoring service return besides the prediction?

---
**Answers**
1. When predictions are not needed instantly (e.g. nightly forecasts, weekly churn lists).
2. When events arrive continuously and each must be scored within seconds, without a request/response caller.
3. You can promote/roll back a model version without rebuilding the service.
4. At least the model version used, so predictions are traceable.

### Module 5 — Model Monitoring (`05-monitoring`)

**Topics:** ML monitoring, environment (Docker Compose, Postgres, Adminer,
Grafana), reference data, Evidently metrics, monitoring dashboards,
data-quality monitoring, saving Grafana dashboards, test suites and
reports, a monitoring example (batch monitoring with Prefect/MongoDB is
also mentioned in the syllabus).

- [ ] 5.1 Intro to ML monitoring
- [ ] 5.2 Environment setup
- [ ] 5.3 Prepare reference and model
- [ ] 5.4 Evidently metrics calculation
- [ ] 5.5 Evidently monitoring dashboard
- [ ] 5.6 Dummy monitoring
- [ ] 5.7 Data quality monitoring
- [ ] 5.8 Save Grafana dashboard
- [ ] 5.9 Debugging with test suites and reports
- [ ] 5.10 Monitoring example
- [ ] **Homework** — `cohorts/2025/05-monitoring/homework.md`

**Must be able to do/explain:**
- [ ] Compute data drift against a reference dataset with Evidently.
- [ ] Show drift and data-quality metrics in Grafana.
- [ ] Explain data drift vs concept drift.

**Estimated hours:** ~10 h

**Self-check questions**
1. What is data drift? Concept drift?
2. Why monitor inputs when you don't have labels yet?
3. What is the reference dataset?
4. What should happen when drift is detected?

---
**Answers**
1. Data drift: input distribution changes. Concept drift: the relation between inputs and target changes.
2. Labels often arrive late; input drift is an early warning that quality may drop.
3. A dataset representing what the model was trained/validated on, used as the baseline for comparison.
4. Alert, investigate, and if confirmed retrain or roll back (possibly automatically).

### Module 6 — Best Practices (`06-best-practices`)

**Topics:** unit tests with pytest, integration tests with docker-compose,
testing cloud services with LocalStack, linting and formatting, pre-commit
hooks, Makefiles, Terraform (intro, modules, outputs), an end-to-end ride
prediction workflow, CI/CD with GitHub Actions.

- [ ] 6.1 Testing Python code with pytest
- [ ] 6.2 Integration tests with docker-compose
- [ ] 6.3 Testing cloud services with LocalStack
- [ ] 6.4 Code quality: linting and formatting
- [ ] 6.5 Git pre-commit hooks
- [ ] 6.6 Makefiles and make
- [ ] 6.7 Terraform: introduction
- [ ] 6.8 Terraform: modules and output variables
- [ ] 6.9 Build an end-to-end ride prediction workflow
- [ ] 6.10 Test the pipeline end to end
- [ ] 6.11 CI/CD: introduction
- [ ] 6.12 Continuous integration
- [ ] 6.13 Continuous delivery
- [ ] **Homework** — `cohorts/2025/06-best-practices/homework.md`

**Must be able to do/explain:**
- [ ] Unit-test feature code and integration-test the service with Compose.
- [ ] Test AWS-dependent code locally with LocalStack.
- [ ] Provision the stream/bucket/registry with Terraform.
- [ ] Run tests and deploy from GitHub Actions.

**Estimated hours:** ~14 h

**Self-check questions**
1. What is LocalStack for?
2. Why use a Makefile in an ML project?
3. What does Terraform state store?
4. What does CI run for an ML service?

---
**Answers**
1. Emulating AWS services (S3, Kinesis, Lambda) locally so integration tests don't need a real account.
2. One consistent entry point for common commands (test, lint, build, deploy) for people and CI.
3. The mapping between your config and the real resources, so Terraform knows what to create, change or destroy.
4. Lint/format checks, unit tests, integration tests, image build — and CD deploys if all pass.

### Course project — MLOps Zoomcamp

**Official requirements** (`07-project/README.md`): one end-to-end ML
project with tracking, orchestration, deployment and monitoring; NYC taxi
data is not allowed; peer review 3 projects (+3 points each). (No 2026
cohort → no certificate this year; the project is still worth doing.)

**Evaluation criteria:** problem description 0–2 · cloud 0–4 (4 needs
IaC) · experiment tracking & model registry 0–4 · workflow orchestration
0–4 · model deployment 0–4 · model monitoring 0–4 (4 needs alerts or
conditional retraining) · reproducibility 0–4. Best practices: unit tests
1 · integration test 1 · linter/formatter 1 · Makefile 1 · pre-commit
hooks 1 · CI/CD pipeline 2.

**Milestones**
- [ ] Problem and dataset chosen (not NYC taxi)
- [ ] Experiment tracking + model registry
- [ ] Training pipeline orchestrated
- [ ] Model deployed (batch / web service / streaming)
- [ ] Monitoring with alerts or conditional retraining
- [ ] Cloud resources provisioned with IaC
- [ ] Tests, linter, Makefile, pre-commit, CI/CD
- [ ] Reproducibility checked from a clean clone
- [ ] Submitted (self-paced: publish the repo)
- [ ] 3 peer reviews done (when a cohort runs)

**Estimated hours:** ~28 h

---

## Course 3.5 — Data Engineering Zoomcamp (~120h)

**Repo:** https://github.com/DataTalksClub/data-engineering-zoomcamp
**Official length:** 9 weeks. Last finished cohort: 2026 (Jan 12 – May 11,
2026). Next: **2027**, starting Jan 11, 2027 — its cohort page and
homework are still drafts [verify].
**Official prerequisites:** basic coding and SQL; Python helpful; no prior
data engineering experience needed.
**Required knowledge from other tracks:** 1C Part 1–2 (SQL, window
functions, partitioning), B3 Docker & Compose, 1A (Python). Helpful: B16
Kafka (Module 7), B33 cloud + Terraform (Module 1).
**Homework location:** 2026 set in `cohorts/2026/<module>/homework.md`;
2027 drafts in `cohorts/2027/homework/<module>/homework.md`
(https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts).

### Module 1 — Containerization and Infrastructure as Code (`01-docker-terraform`)

**Topics:** Docker, virtual environments and pipelines, Dockerizing an
ingestion pipeline, PostgreSQL + pgAdmin in Docker, NY taxi ingestion,
Docker Compose, SQL refresher, Terraform, GCP.

- [ ] 1.1 Introduction to Docker
- [ ] 1.2 Virtual environments and data pipelines
- [ ] 1.3 Dockerizing the pipeline
- [ ] 1.4 Running PostgreSQL with Docker
- [ ] 1.5 NY taxi dataset and data ingestion
- [ ] 1.6 Creating the data ingestion script
- [ ] 1.7 pgAdmin
- [ ] 1.8 Dockerizing the ingestion script
- [ ] 1.9 Docker Compose
- [ ] 1.10 SQL refresher
- [ ] 1.11 Cleanup
- [ ] 1.12 Terraform overview
- [ ] 1.13 GCP overview
- [ ] Setup guide: Terraform and GCP
- [ ] **Homework** — `cohorts/2026/01-docker-terraform/homework.md` (or the 2027 draft)

**Must be able to do/explain:**
- [ ] Build a Dockerized ingestion script that loads CSV/Parquet into Postgres in chunks.
- [ ] Run Postgres + pgAdmin + the pipeline with Compose.
- [ ] Create a GCS bucket and BigQuery dataset with Terraform.

**Estimated hours:** ~14 h

**Self-check questions**
1. Why load large files in chunks?
2. How do two containers in the same Compose project reach each other?
3. What do `terraform plan` and `terraform apply` do?
4. Why use a service account for GCP access?

---
**Answers**
1. To keep memory bounded and to resume/observe progress instead of one huge transaction.
2. Through the Compose network, using the service name as the hostname.
3. `plan` shows the changes needed to reach the desired state; `apply` performs them.
4. It gives the pipeline its own least-privilege identity, separate from your personal account.

### Module 2 — Workflow Orchestration (`02-workflow-orchestration`)

**Topics:** workflow orchestration, **Kestra** (install, concepts), running
Python code, a first pipeline, loading taxi data into Postgres, scheduling
and backfills, ETL vs ELT, GCP setup, loading to BigQuery, scheduling the
full dataset, AI for workflows (context engineering, Kestra AI Copilot),
bonus RAG and cloud deploy. (The course uses Kestra, not Airflow.)

- [ ] 2.1 What is workflow orchestration?
- [ ] 2.2 What is Kestra?
- [ ] 2.3 Installing Kestra
- [ ] 2.4 Kestra concepts
- [ ] 2.5 Orchestrate Python code
- [ ] 2.6 Getting started pipeline
- [ ] 2.7 Local DB: load taxi data to Postgres
- [ ] 2.8 Local DB: scheduling and backfills
- [ ] 2.9 ETL vs ELT
- [ ] 2.10 Setup Google Cloud Platform
- [ ] 2.11 GCP workflow: load taxi data to BigQuery
- [ ] 2.12 GCP workflow: schedule and backfill the full dataset
- [ ] 2.13 Introduction: why AI for workflows?
- [ ] 2.14 Context engineering with ChatGPT
- [ ] 2.15 AI Copilot in Kestra
- [ ] 2.16 Bonus: Retrieval Augmented Generation (RAG)
- [ ] 2.17 Bonus: deploy to the cloud (optional)
- [ ] **Homework** — `cohorts/2026/02-workflow-orchestration/homework.md` (or the 2027 draft)

**Must be able to do/explain:**
- [ ] Build a scheduled Kestra flow that loads a month of data and can be backfilled.
- [ ] Explain ETL vs ELT and why warehouses made ELT common.
- [ ] Make a load idempotent (rerun without duplicates).

**Estimated hours:** ~14 h

**Self-check questions**
1. What is a backfill?
2. ETL vs ELT?
3. How do you make a monthly load safe to rerun?
4. What does the orchestrator give you that a script doesn't?

---
**Answers**
1. Running a pipeline for past periods (e.g. every month of 2021) using the same logic as the scheduled run.
2. ETL transforms before loading; ELT loads raw data first and transforms inside the warehouse.
3. Load into a staging table and MERGE, or delete/replace the partition for that month before inserting.
4. Scheduling, dependencies, retries, parameters per run, logs and a history of every run.

### Workshop — dlt: data ingestion (`cohorts/2026/workshops/dlt.md`)

**Topics:** ingesting from APIs, normalization, incremental loading; the
2026 version is "AI-assisted" and uses the dlt dashboard and dlt MCP.

- [ ] Watch the workshop / read `cohorts/2026/workshops/dlt.md`
- [ ] Build the workshop pipeline end to end
- [ ] **Homework** — dlt workshop homework (2026 cohort folder) [verify path]

**Must be able to do/explain:**
- [ ] Build a paginated REST API source with dlt and load it incrementally.
- [ ] Explain how dlt normalizes nested JSON into child tables.

**Estimated hours:** ~6 h

**Self-check questions**
1. How does dlt handle nested JSON?
2. How does incremental loading know where to continue?

---
**Answers**
1. It flattens nested objects into columns and turns nested lists into child tables linked by keys.
2. It stores state (e.g. the last seen cursor value) between runs and requests only newer records.

### Module 3 — Data Warehouse (`03-data-warehouse`)

**Topics:** data warehouses and BigQuery, partitioning vs clustering,
BigQuery best practices and internals, BigQuery ML, deploying a BigQuery
ML model.

- [ ] 3.1 Data warehouse and BigQuery
- [ ] 3.2 Partitioning vs clustering
- [ ] 3.3 BigQuery best practices
- [ ] 3.4 Internals of BigQuery
- [ ] 3.5 Machine learning in BigQuery
- [ ] 3.6 Deploying a machine learning model from BigQuery
- [ ] **Homework** — `cohorts/2026/03-data-warehouse/homework.md` (or the 2027 draft)

**Must be able to do/explain:**
- [ ] Create external and native tables, partitioned and clustered.
- [ ] Show the bytes-scanned difference a partition filter makes.
- [ ] Explain OLTP vs OLAP and columnar storage.

**Estimated hours:** ~10 h

**Self-check questions**
1. OLTP vs OLAP?
2. When partition, when cluster?
3. Why is `SELECT *` expensive in BigQuery?
4. What is an external table?

---
**Answers**
1. OLTP: many small transactional reads/writes (apps). OLAP: large analytical scans and aggregations (reporting).
2. Partition on a column you filter by with low cardinality (usually date); cluster on columns you filter/sort by with higher cardinality.
3. Storage is columnar and you pay per bytes scanned; `*` reads every column.
4. A table whose data stays in object storage (e.g. GCS Parquet) and is read at query time.

### Module 4 — Analytics Engineering (`04-analytics-engineering`)

**Topics:** analytics engineering, dbt (Core vs Cloud), project structure,
sources, models, seeds and macros, documentation, tests, packages,
commands; local setup (DuckDB + dbt Core) or cloud (BigQuery + dbt Cloud).

- [ ] 4.1 Analytics engineering basics
- [ ] 4.2 What is dbt?
- [ ] 4.3 dbt Core vs dbt Cloud
- [ ] 4.4 dbt project structure
- [ ] 4.5 dbt sources
- [ ] 4.6 dbt models
- [ ] 4.7 dbt seeds and macros
- [ ] 4.8 Documentation
- [ ] 4.9 dbt tests
- [ ] 4.10 dbt packages
- [ ] 4.11 dbt commands
- [ ] **Homework** — `cohorts/2026/04-analytics-engineering/homework.md` (or the 2027 draft)

**Must be able to do/explain:**
- [ ] Build staging → core models with sources, refs and tests.
- [ ] Explain dimensional modelling (facts vs dimensions).
- [ ] Generate and read dbt docs and lineage.

**Estimated hours:** ~14 h

**Self-check questions**
1. What does dbt do and not do?
2. Fact vs dimension table?
3. What is `ref()` for?
4. Name two built-in dbt tests.

---
**Answers**
1. It runs versioned, tested SQL transformations inside the warehouse; it does not extract or load data.
2. Facts hold measurable events (trips, orders); dimensions hold descriptive attributes (zones, customers).
3. Referencing another model so dbt builds the dependency graph and resolves the right schema/table name.
4. `unique`, `not_null` (also `accepted_values`, `relationships`).

### Module 5 — Data Platforms (`05-data-platforms`)

**Topics:** **Bruin** — getting started, an end-to-end NYC taxi pipeline,
Bruin MCP with AI agents, Bruin Cloud; core concepts: projects,
pipelines, assets, variables, commands; quality checks; deploy to
BigQuery.

- [ ] 5.1 Introduction to Bruin
- [ ] 5.2 Getting started with Bruin
- [ ] 5.3 Building an end-to-end pipeline with NYC taxi data
- [ ] 5.4 Using Bruin MCP with AI agents
- [ ] 5.5 Deploying to Bruin Cloud
- [ ] 5.6 Core concepts: projects
- [ ] 5.7 Core concepts: pipelines
- [ ] 5.8 Core concepts: assets
- [ ] 5.9 Core concepts: variables
- [ ] 5.10 Core concepts: commands
- [ ] **Homework** — `cohorts/2026/05-data-platforms/homework.md` (or the 2027 draft) [verify]

**Must be able to do/explain:**
- [ ] Build one pipeline that does ingestion, transformation and quality checks in Bruin.
- [ ] Explain what an integrated data platform replaces (separate orchestrator + dbt + ingestion tool).

**Estimated hours:** ~8 h

**Self-check questions**
1. What is an "asset" in Bruin?
2. Why add data-quality checks inside the pipeline?
3. Trade-off of an all-in-one platform vs separate tools?

---
**Answers**
1. A unit of data the pipeline produces (a table/file) with its code, dependencies and checks.
2. So bad data fails the run early instead of reaching dashboards.
3. Less glue and one place to operate, but more lock-in and less flexibility per layer.

### Module 6 — Batch Processing (`06-batch`)

**Topics:** batch processing, Spark and PySpark, DataFrames, Spark SQL,
cluster anatomy, GroupBy and joins internals, RDDs, GCS, local cluster,
Dataproc, Spark → BigQuery. Units 3 (Linux install), 6 (taxi data) and
11–12 (RDDs) are optional.

- [ ] 6.1 Introduction to batch processing
- [ ] 6.2 Introduction to Spark
- [ ] 6.3 Installing Spark (optional per OS)
- [ ] 6.4 First look at Spark/PySpark
- [ ] 6.5 Spark DataFrames
- [ ] 6.6 Preparing yellow and green taxi data (optional)
- [ ] 6.7 SQL with Spark
- [ ] 6.8 Anatomy of a Spark cluster
- [ ] 6.9 GroupBy in Spark
- [ ] 6.10 Joins in Spark
- [ ] 6.11 Operations on Spark RDDs (optional)
- [ ] 6.12 Spark RDD mapPartitions (optional)
- [ ] 6.13 Connecting to Google Cloud Storage
- [ ] 6.14 Creating a local Spark cluster
- [ ] 6.15 Setting up a Dataproc cluster
- [ ] 6.16 Connecting Spark to BigQuery
- [ ] **Homework** — `cohorts/2026/06-batch/homework.md` (or the 2027 draft)

**Must be able to do/explain:**
- [ ] Explain driver, executors, partitions, stages and shuffles.
- [ ] Explain how GroupBy and joins shuffle data; when a broadcast join helps.
- [ ] Run a PySpark job on a cluster reading from GCS and writing to BigQuery.

**Estimated hours:** ~14 h

**Self-check questions**
1. What is a shuffle and why is it expensive?
2. When is a broadcast join better?
3. What are transformations vs actions (lazy evaluation)?
4. Why repartition before writing?

---
**Answers**
1. Moving data between executors so rows with the same key end up together; it costs network, disk and time.
2. When one side is small enough to copy to every executor, avoiding a shuffle of the big side.
3. Transformations build a plan and run nothing; actions (count, write, collect) trigger execution.
4. To control the number and size of output files and balance work.

### Module 7 — Streaming (`07-streaming`)

**Topics:** stream processing with **PyFlink** and **Redpanda**
(Kafka-compatible), producing and consuming messages in Python, saving
events to PostgreSQL, Flink jobs, offsets (earliest vs latest), tumbling
windows, late events and upserts, window types. (The README still mentions
Kafka Streams/KSQL/Avro; the current module uses PyFlink + Redpanda. The
old Kafka theory with Java examples is kept as optional material.)

- [ ] 7.1 PyFlink: stream processing workshop
- [ ] 7.2 Redpanda — a Kafka-compatible broker
- [ ] 7.3 Produce messages to Kafka
- [ ] 7.4 Consume messages with Python
- [ ] 7.5 Save events to PostgreSQL
- [ ] 7.6 Why Flink?
- [ ] 7.7 The Flink image and services
- [ ] 7.8 The pass-through Flink job
- [ ] 7.9 Offsets — earliest vs latest
- [ ] 7.10 Aggregation with tumbling windows
- [ ] 7.11 Late events and upserts
- [ ] 7.12 Understanding window types
- [ ] 7.13 Cleanup
- [ ] (Optional) Kafka theory videos (Java examples)
- [ ] **Homework** — `cohorts/2026/07-streaming/homework.md` (or the 2027 draft)

**Must be able to do/explain:**
- [ ] Produce and consume events with Python against Redpanda.
- [ ] Write a Flink job with a tumbling window that upserts into Postgres.
- [ ] Explain event time vs processing time and how late events are handled.

**Estimated hours:** ~10 h

**Self-check questions**
1. Tumbling vs sliding vs session windows?
2. Event time vs processing time?
3. What is a watermark?
4. Why upsert window results instead of inserting?

---
**Answers**
1. Tumbling: fixed, non-overlapping; sliding: fixed size, overlapping by a slide step; session: closed after a gap of inactivity.
2. Event time is when the event happened; processing time is when the system sees it.
3. A moving threshold saying "events older than this are assumed to have arrived", which lets windows close while allowing some lateness.
4. Late events can update an already-emitted window; upserting keeps one correct row per window key.

### Course project — Data Engineering Zoomcamp

**Official requirements** (`projects/README.md`, `cohorts/<year>/project.md`):
one end-to-end pipeline (batch or streaming): data lake → data warehouse →
transformations → a dashboard with **2 or more tiles**. **2 attempts.** NYC
taxi data is not allowed. You must review 3 peers (+3 points each) or the
project doesn't count. Certificate needs the project in a live cohort.

**Evaluation criteria** (0/2/4 each): problem description · cloud (4 needs
IaC) · data ingestion (batch: orchestrated end-to-end; or stream) · data
warehouse (4 needs sensible partitioning and clustering) · transformations
(dbt, Spark, etc.) · dashboard · reproducibility. Tests, make and CI/CD are
optional and ungraded.

**Milestones**
- [ ] Problem and dataset chosen (not NYC taxi)
- [ ] Cloud resources created with Terraform
- [ ] Ingestion into the data lake (orchestrated batch, or streaming)
- [ ] Warehouse tables with partitioning and clustering
- [ ] Transformations (dbt/Spark) with tests
- [ ] Dashboard with ≥2 tiles
- [ ] Reproducibility checked from a clean clone
- [ ] Submitted
- [ ] 3 peer reviews done

**Estimated hours:** ~30 h

---

## Track 3 progress summary

| Course | Modules done / total | Homework done / total | Project | Hours |
|---|---|---|---|---|
| 3.1 LLM Zoomcamp | 0 / 7 (+1 workshop) | 0 / 6 (5 modules + dlt workshop) [verify count] | [ ] | ~80 |
| 3.2 AI Dev Tools Zoomcamp | 0 / 5 | 0 / 4 (+ extension pack) | [ ] | ~60 |
| 3.3 ML Zoomcamp | 0 / 9 (+ optional KServe) | 0 / 9 | [ ] midterm · [ ] capstone | ~150 |
| 3.4 MLOps Zoomcamp | 0 / 6 | 0 / 6 | [ ] | ~90 |
| 3.5 Data Engineering Zoomcamp | 0 / 7 (+1 workshop) | 0 / 8 (7 modules + dlt workshop) | [ ] | ~120 |
| **Total** | | | | **~500** |
