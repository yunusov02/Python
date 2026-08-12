# PHASE 9 — LLM Zoomcamp
### Weeks 27–32 (6 weeks) · ~4h weekdays, ~2–3h Saturdays · 36 working days

---

## 1. Learning Goals

By the end of Phase 7 you can:

- Explain the RAG pattern well enough to design one from a blank page:
  chunk → embed → index → retrieve → (rewrite/rerank) → prompt → generate,
  and say *why* each step exists, not just that it does.
- Stand up a vector database (Qdrant) from scratch — collections, points,
  distance metrics, HNSW — and know when a dense vector index beats, loses
  to, or should be combined with the Elasticsearch keyword search you built
  in Phase 5.
- Build an agent that reasons in a ReAct-style loop and calls a real tool
  (your own API), with enough guardrails that it fails safely instead of
  silently doing the wrong thing.
- Evaluate a RAG system the way a team actually would: offline retrieval
  metrics (hit rate, MRR), LLM-as-judge faithfulness scoring, and cost/
  latency telemetry — before touching the prompt to "make it better."
- Apply query rewriting, hybrid search, and re-ranking to materially improve
  retrieval quality, and measure that improvement instead of assuming it.
- Tell the difference between a real A/B-test win and noise: compute a
  confidence interval on a metric delta by hand and explain, in one
  sentence, why "variant B scored higher" is meaningless without one.
- Recognize and defend against the two RAG failure modes that actually
  matter in production: hallucinated/fabricated claims and prompt
  injection — with a guardrail you built and tested, not just a prompt
  instruction you hoped would hold.
- Ship three real RAG features into three existing systems (CarePoint,
  DocuVault, AtlasMarket) end-to-end: retrieval, generation, evaluation,
  monitoring, and deployment — not a notebook demo.

---

## 2. Technologies Introduced This Phase

LLM APIs (OpenAI and/or Anthropic chat completions, function/tool calling)
· Ollama (running an open-weight model locally, for cost-free experimentation
and as an explicit "open vs closed" comparison point) · text embedding
models (OpenAI `text-embedding-3-small` or a `sentence-transformers` model)
· Qdrant (vector database: collections, points, payload filters, HNSW) ·
Elasticsearch dense-vector / hybrid search (reusing the Phase 5 ES cluster,
now combined with keyword search via score fusion) · prompt-engineering
patterns (zero/few-shot, system prompts, query rewriting) · agentic
patterns (tool calling, ReAct reasoning loops, conversation memory) · RAG
evaluation tooling (hit rate, MRR, LLM-as-judge faithfulness scoring,
golden eval sets) · cost/latency/session telemetry for LLM calls · hand-
rolled guardrails (prompt-injection detection, output validation, scope
checks on tool calls) · hypothesis-testing fundamentals (null hypothesis,
p-values, confidence intervals) applied to A/B-testing prompt/model
variants — the statistics layer under the "A/B test it" instinct the
plan otherwise leaves unexamined.

Deliberately **not yet introduced**: building your own agent orchestration
framework or MCP servers (that's Phase 8's territory — this phase teaches
you what such a framework would be doing for you, by hand, first);
fine-tuning or training your own models; production-grade third-party
guardrail frameworks (Guardrails AI, NeMo Guardrails) beyond the hand-
rolled checks you write here; self-hosted GPU inference infrastructure at
scale; adopting LangChain/LlamaIndex as an abstraction layer — you build
the pipeline by hand so you can say exactly what it does, then evaluate
such a framework honestly later, on your own terms.

This phase is the applied, hands-on counterpart to DataTalksClub's **LLM
Zoomcamp** curriculum (github.com/DataTalksClub/llm-zoomcamp) — its module
sequence (Intro, Vector Search, Agents, Evaluation, Monitoring, Best
Practices, Project examples) maps directly onto Weeks 27–32 below, applied
to CarePoint, PeopleOps, DocuVault, and AtlasMarket instead of the
Zoomcamp's own sample dataset.

---

## 3. PROJECT 1 — CarePoint Patient-FAQ Assistant

### Business Problem
CarePoint's front-desk staff field the same dozen questions dozens of times
a day — visiting hours, insurance accepted, what to bring to a first
appointment, prescription-refill policy, cancellation windows — answered
today from a static FAQ page and a policy PDF nobody actually reads. Phone
lines get tied up on questions that don't need a human, while staff have
less time for patients who do. CarePoint needs an assistant that answers
routine questions instantly, grounded strictly in approved clinic content,
and that knows the difference between "what are your hours" and "should I
be worried about this symptom" — refusing/escalating the latter instead of
guessing.

### Requirements
**Functional**
- Ingest CarePoint's FAQ + policy documents into a hybrid retrieval index
  (Elasticsearch keyword + Qdrant vector, built in Week 30).
- `POST /patient-faq/ask`: multi-turn chat, grounded answers with source
  citations back to the specific FAQ/policy chunk.
- Query rewriting for conversational follow-ups ("what about weekends?").
- Guardrails: refuse/escalate medical-advice-seeking questions and anything
  not grounded in retrieved context; reject prompt-injection attempts.
- Reindex endpoint that rebuilds both indexes from source documents.

**Non-functional**
- Every answer must be traceable to a specific source chunk — no
  ungrounded claims, ever.
- p95 latency budget documented and measured across the full pipeline
  (embed + hybrid retrieval + rerank + generation).
- Full cost/latency logging per request; low-confidence retrieval triggers
  a human-escalation path, never a guess.
- Auth required; rate-limited per patient account.

### Architecture
```
Patient question (+ short conversation history)
  → Input guardrail: medical-advice / out-of-scope classifier
  → Query rewrite (resolve follow-up pronouns/ellipsis using history)
  → Embed query
  → Hybrid retrieval: Elasticsearch keyword search + Qdrant vector search
    → merge via score fusion (RRF)
  → Re-rank top-20 → top-5
  → Prompt assembly: system prompt ("answer ONLY from context, cite chunk
    ids") + top-5 chunks + question
  → LLM generation
  → Output guardrail: citation present? claim supported by context?
    injection markers present?
  → Low-confidence or guardrail trip → escalate-to-staff response
    (never a fabricated answer)
  → Response + citations, logged to chat_logs (tokens, cost, latency,
    guardrail outcome)
```
Ingestion (offline/on-demand):
```
FAQ/policy docs → chunk (paragraph-based, ~300 tokens, overlap)
  → embed → upsert Qdrant (`carepoint_faq` collection)
           + index Elasticsearch (keyword)
```

### API Design
```
POST /patient-faq/ask            # {session_id, question} -> {answer, citations[], escalated: bool}
POST /patient-faq/reindex        # rebuild ES + Qdrant from source docs
GET  /patient-faq/sessions/{id}  # conversation history
POST /patient-faq/feedback       # thumbs up/down on an answer
```

### Testing Strategy
- Golden eval set (20–30 real-style questions → expected source doc) —
  hit rate@5 and MRR tracked in CI.
- LLM-as-judge faithfulness score on generated answers, threshold-gated
  in CI.
- Injection-attack regression suite (the strings from Week 30) must always
  be caught.
- Integration test proving low-confidence retrieval escalates instead of
  answering.
- Test that reindex-from-source fully recovers both indexes after a wipe
  (the DocuVault reindex pattern, reused).

### Monitoring
Grafana panel: cost per query, p95 latency, hit-rate/faithfulness trend
over time, escalation rate. Alert if faithfulness score or hit-rate drops
below threshold on the nightly eval run, or escalation rate spikes
(signals a knowledge-base gap, not a model problem).

### Deployment
Runs as an additional service inside CarePoint's existing Docker Compose /
Kubernetes deployment (Phase 4/5); Qdrant is added as a new service
alongside the existing Elasticsearch cluster.

### Common Interview Questions
1. How do you guarantee the assistant never answers from outside the
   approved knowledge base?
2. Walk through your hybrid-search fusion — why not vector-only or
   keyword-only?
3. What triggers escalation to a human, and why is that better than a
   low-confidence disclaimer?
4. How would you catch a prompt-injection attempt hidden inside a
   patient's message?
5. Why re-rank after hybrid retrieval instead of just taking the fused
   top-5 directly?
6. How do you evaluate "faithfulness" without a human reading every answer?
7. What's the cost/latency tradeoff of adding a re-ranking step?
8. If the FAQ content changes, how does that propagate to the assistant?

### Possible Improvements
Multi-language support, speech-to-text voice input, per-patient
personalization (referencing their own upcoming appointment), streaming
responses, an active-learning loop where escalated questions become new
FAQ entries.

### Common Mistakes
Letting the system prompt say "be helpful" without an explicit "only from
context" constraint; treating a citation as proof of faithfulness without
actually checking the claim is supported; caching answers keyed only on
raw question text (missing that context/permissions can differ); skipping
the escalation path and letting the model "confidently" answer a medical
question it shouldn't.

---

## 4. PROJECT 2 — DocuVault "Ask Your Documents" RAG Chatbot

### Business Problem
DocuVault's Week 27 semantic search returns chunks; employees still have
to read them and piece together an answer themselves. A genuinely useful
"ask your documents" experience lets employees have a conversation about
the corpus — "what's our refund policy?", "what changed in the vendor
contract's v3 vs v2?" — and get a synthesized, cited answer, without ever
exposing content from documents they don't have permission to read.

### Requirements
**Functional**
- Multi-turn chat endpoint over the full DocuVault corpus, hybrid
  retrieval + rerank (reusing Week 30's pattern).
- Citations back to specific document + version.
- Access-control-aware retrieval: filter by the requesting user's document
  permissions *before* chunks reach the prompt, not after generation.
- Feedback capture per answer, feeding the eval harness.

**Non-functional**
- Zero cross-permission leakage — even indirectly, via a synthesized
  answer that paraphrases restricted content.
- Answers traceable to a document + version, consistent with DocuVault's
  Phase 5 principle: Postgres is the source of truth, the search indexes
  are derived and always rebuildable.
- Reindex must rebuild both the keyword and vector indexes identically
  after a wipe.

### Architecture
```
Employee question (+ history) + user_id
  → Query rewrite using history
  → Embed query
  → Hybrid retrieval scoped to documents user_id can read
    (permission filter applied at the index-query level, not post-hoc)
  → Re-rank
  → Prompt assembly + generation (cite document_id + version_number)
  → Output guardrail: citation present, no fabricated document reference
  → Response + citations, logged
```
Ingestion reuses Phase 5's outbox-relay-style sync consumer, extended so
that every new document version also gets embedded and upserted into
Qdrant whenever it's indexed into Elasticsearch — one event, two derived
indexes kept in lockstep.

### API Design
```
POST /documents/chat              # {session_id, question} -> {answer, citations[{document_id, version, snippet}]}
POST /documents/chat/feedback
POST /documents/reindex           # rebuilds ES + Qdrant from Postgres (extends Phase 5's reindex)
```

### Testing Strategy
- Permission-leakage test: a user without access to Document X never sees
  its content in an answer, even when X is clearly the best semantic
  match for their question.
- Golden eval set for conversational (multi-turn) queries — hit rate, MRR,
  and faithfulness tracked in CI.
- Test that reindexing after a wipe restores identical chat behavior.
- Test that a citation always resolves to a real, current document
  version.

### Monitoring
Extends Phase 5's DocuVault dashboards with chat-specific panels: chat
sessions/day, feedback thumbs-down rate, permission-filter hit rate (how
often results get filtered out), cost/latency per chat turn.

### Deployment
Ships as an additional endpoint on the existing DocuVault service; Qdrant
runs alongside the existing Elasticsearch/Postgres/MinIO stack from
Phase 5, same Compose/K8s manifests, extended.

### Common Interview Questions
1. How do you guarantee permission filtering happens before generation,
   not after?
2. Why keep both Elasticsearch and Qdrant instead of picking one?
3. How do you keep two derived indexes (keyword + vector) consistent with
   each other and with Postgres?
4. What's different about evaluating a conversational RAG system versus a
   single-shot one?
5. How could a citation ever point to a stale document version, and how
   do you prevent it?
6. What's your rollback plan if the vector-index sync consumer falls
   behind?

### Possible Improvements
Cross-document synthesis with explicit multi-source citation,
summarize-this-whole-document on request, admin-facing analytics on which
documents get asked about most (a candidate list for better tagging).

### Common Mistakes
Filtering permissions in the API layer after retrieval instead of at the
index/query level (leaks via ranking signals even if content is
stripped); assuming the keyword and vector indexes will never drift out
of sync; forgetting that an older document version should still be
citable-but-marked-outdated, not silently excluded.

---

## 5. PROJECT 3 — AtlasMarket Product Q&A Support Assistant

### Business Problem
AtlasMarket buyers ask the same product questions before purchase —
sizing, materials, compatibility, a specific vendor's return policy — that
today go unanswered until a vendor manually replies, if ever, costing
sales. A support assistant that answers from each vendor's actual product
data (never inventing specs or prices) and escalates to the vendor when it
doesn't know, reduces pre-purchase drop-off without risking a fabricated
promise a vendor never made.

### Requirements
**Functional**
- Ingest product descriptions, specs, and buyer reviews into a vector
  store, scoped by `vendor_id`/`product_id`.
- `POST /support/ask`: answers a buyer's question about one specific
  product, grounded only in that product's data + relevant review
  excerpts.
- Escalation to vendor support when no matching data exists — never a
  fabricated price/spec/availability claim.
- Multi-vendor isolation: a question about vendor A's product must never
  retrieve or leak vendor B's data.

**Non-functional**
- Zero fabricated prices/specs — the one guardrail this project cannot
  ship without, given real purchase decisions ride on it.
- Retrieval strictly scoped per product/vendor at the index-filter level.
- Cost/latency tracked per vendor — a vendor-facing cost-attribution
  concern AtlasMarket's marketplace model requires.

### Architecture
```
Buyer question + product_id (vendor_id derived from the product)
  → Embed query
  → Vector retrieval filtered by product_id/vendor_id (metadata filter,
    not a post-filter)
  → Prompt assembly: system prompt ("answer ONLY about this product, from
    this data, no invented specs/prices") + product description/specs +
    top review excerpts + question
  → LLM generation
  → Output guardrail: no numeric claim (price/size/quantity) that isn't
    present in the retrieved context
  → No sufficiently relevant data retrieved → escalate to vendor support,
    no generated answer
  → Response + citation to spec/review source, logged with vendor_id for
    cost attribution
```
Ingestion:
```
Product catalog (reusing the StockPilot/AtlasMarket product model)
  + reviews → chunk per-product (specs block, description, review
  batches) → embed → upsert Qdrant with payload {vendor_id, product_id,
  source_type}
```

### API Design
```
POST /support/ask                 # {product_id, question} -> {answer|null, citations[], escalated: bool}
POST /support/products/{id}/reindex
GET  /support/vendors/{id}/usage  # cost/latency attribution per vendor
```

### Testing Strategy
- Cross-vendor leakage test: a question scoped to vendor A's product never
  returns vendor B's chunks, even under adversarial phrasing.
- Fabrication-guardrail test: a question with no matching product data
  must escalate, not invent an answer; a question with a nearby-but-wrong
  number in context must be caught by the guardrail as an unsupported
  claim.
- Golden eval set per product category — hit rate, MRR, faithfulness in
  CI.
- Load test proving cost-attribution logging adds no meaningful latency
  (reusing the Phase 6 `hey`/locust load-testing skill).

### Monitoring
Per-vendor dashboard: query volume, escalation rate (a proxy for
catalog-data gaps a vendor should fix), cost per vendor, faithfulness
score trend. Escalation-rate spikes are surfaced back to vendors as an
actionable "improve your product data" signal — a real product feature,
not just an internal metric.

### Deployment
New service alongside AtlasMarket's existing marketplace services
(Phase 6), sharing the single Qdrant instance introduced in Week 27/30
rather than deploying a separate one per feature.

### Common Interview Questions
1. How do you enforce vendor-level data isolation in a shared vector
   store?
2. What's your guardrail against the assistant inventing a price or spec,
   specifically?
3. Why escalate instead of returning a low-confidence disclaimer answer?
4. How do you attribute LLM cost per vendor in a multi-tenant marketplace?
5. How would you evaluate whether escalation is happening too often
   versus too rarely?
6. What's structurally different about scoping retrieval by
   product/vendor here versus scoping by user permission in DocuVault?

### Possible Improvements
Comparative Q&A across multiple products ("which of these is more
durable"), vendor-facing suggested-FAQ generation from the escalation
log, streaming answers, review-sentiment-aware ranking of which reviews
to cite.

### Common Mistakes
Relying on prompt instructions alone ("don't make up prices") without an
output-side numeric-claim guardrail; sharing one Qdrant collection across
vendors without a mandatory metadata filter on every single query;
treating "no results" the same as "shaky results" instead of escalating
both.

---

## 6. Books & Documentation for This Phase

- DataTalksClub **LLM Zoomcamp** (github.com/DataTalksClub/llm-zoomcamp) —
  the applied curriculum this phase's module sequence follows.
- OpenAI docs: "Prompt engineering," "Embeddings," and "Function calling"
  guides (platform.openai.com/docs/guides/...).
- Anthropic docs: "Tool use" and "Prompt engineering" (docs.anthropic.com/
  en/docs/build-with-claude/...).
- Qdrant docs: Concepts — Collections, Points, Search, Filtering
  (qdrant.tech/documentation).
- Elasticsearch docs: "Dense vector field type," "kNN search," "Hybrid
  search" (elastic.co/guide) — read as a direct continuation of Phase 5.
- Ollama docs (ollama.com) — running open-weight models locally, Week 27's
  open-vs-closed comparison.
- *Prompt Engineering Guide* (promptingguide.ai) — general reference,
  read alongside Weeks 27 and 43.
- "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et
  al., arXiv:2210.03629) — read Section 3 the same week you build the
  ReAct loop (Week 28).
- RAGAS docs (docs.ragas.io) — retrieval/generation evaluation metrics:
  hit rate, MRR, faithfulness, answer relevancy (Week 29).
- *Practical Statistics for Data Scientists* (Bruce, Bruce & Gedeck) Ch.3
  ("Statistical Experiments and Significance Testing") — read the Friday
  of Week 29, before computing the A/B-test confidence interval by hand.
- OWASP "Top 10 for Large Language Model Applications"
  (owasp.org/www-project-top-10-for-large-language-model-applications) —
  prompt injection and excessive-agency sections, read in Weeks 28 and 43.

---

## 7. Weekly Interview Question Sets

**Week 27 — Intro, Vector Search**
1. Explain RAG in one paragraph — what problem does it solve that a bigger
   context window or fine-tuning doesn't?
2. What's the difference between a dense embedding and a sparse
   (keyword/TF-IDF) representation?
3. How does cosine similarity work, and why is it preferred over Euclidean
   distance for text embeddings?
4. Walk through what an HNSW index is doing and why brute-force vector
   search doesn't scale.
5. Open-weight vs closed-API models — what are you actually trading off?

**Week 28 — Agents**
1. What is function/tool calling, mechanically, from the model's
   perspective?
2. Explain the ReAct loop (Reason → Act → Observe) and where it can fail.
3. How would you give an agent "memory" across turns without blowing the
   context window?
4. What guardrails prevent an agent from calling a tool it shouldn't?
5. Name one concrete failure mode of multi-step agents (looping,
   hallucinated tool args) and how you'd detect it.

**Week 29 — Evaluation, Monitoring**
1. Define hit rate and MRR for a RAG retrieval evaluation set.
2. What is "LLM-as-judge" and what's its biggest weakness?
3. How do you build a golden evaluation set without hand-labeling
   thousands of examples?
4. What would you log per LLM call to debug a cost or latency regression
   later?
5. How would you A/B test two prompts in production without users
   noticing?

**Week 30 — Best Practices, Project Example**
1. What is query rewriting solving, and what's a scenario it fails on?
2. Hybrid search: how do you combine sparse keyword and dense vector
   results?
3. Why does re-ranking help after retrieval, and what does it cost you?
4. What's a basic mitigation for prompt injection in a RAG system?
5. When is caching an LLM response safe versus unsafe?

**Week 31 — Project 1 (CarePoint Patient-FAQ Assistant)**
1. Walk through your CarePoint pipeline end-to-end, one request.
2. Where exactly could this system hallucinate, and what stops it?
3. How did you evaluate retrieval quality before touching the prompt?
4. What's your fallback when the LLM API is down or slow?
5. How do you know your guardrail catches a prompt-injection attempt, in
   your test suite specifically?

**Week 32 — Projects 2 & 3, Phase Wrap**
1. Compare DocuVault's document chatbot to CarePoint's FAQ assistant —
   what's structurally different?
2. Why is AtlasMarket's product Q&A assistant scoped per-vendor, and what
   would leak if it weren't?
3. Across all three RAG systems, what's the one component you'd invest in
   first if you had one more week?
4. How do you decide when a use case needs an agent rather than plain RAG?
5. What's your honest answer to "is this production-ready?" for each of
   the three assistants?

---

## 8. Daily Plan — Week 27: Intro, Vector Search, DocuVault Semantic Search

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D157)** | LLM basics & prompting fundamentals — tokens, context window, temperature, zero/few-shot; open vs closed models | OpenAI "Prompt engineering" guide + Ollama docs intro | Run the same question through a closed API model and a local Ollama model, compare answer/latency/cost | New `docuvault/rag/` module scaffold; `docs/llm-provider-decision.md` picking a primary API provider + Ollama as free dev fallback | Smoke-test both API clients return a response for a fixed prompt | `feat: rag module scaffold + llm provider decision` | Q1 | 3.5h |
| **Tue (D158)** | RAG architecture overview — why RAG over fine-tuning/bigger context; retrieval+generation pipeline shape | DataTalksClub llm-zoomcamp Module 1 README | Sketch the full pipeline diagram in `docs/rag-architecture.md` before writing any code | `docs/rag-architecture.md` for DocuVault: ingestion pipeline + query pipeline diagram | — | `docs: docuvault rag architecture diagram` | Q2 | 3.5h |
| **Wed (D159)** | Embeddings & vector representations — how text becomes a vector, cosine similarity, embedding model choice | OpenAI "Embeddings" guide | Embed 10 sample sentences, compute pairwise cosine similarity by hand with numpy, sanity-check similar pairs score higher | `rag/embeddings.py` wraps the chosen embedding model, batches DocuVault chunk text | Unit test: correct vector dimension, deterministic for same input | `feat: embedding client wrapper` | Q3 | 3.5h |
| **Thu (D160)** | Vector databases — Qdrant collections/points/payload, distance metrics, HNSW; brief comparison to Elasticsearch dense_vector | Qdrant docs "Collections" + "Points"; Elastic docs "Dense vector field type" (Phase 5 refresher) | Spin up local Qdrant via Docker, create a collection, upsert 20 fake vectors, run a `search` query | Add `qdrant` service to DocuVault's compose; create `documents_chunks` collection sized to the embedding model's dimension | Integration test: collection exists, dimension/distance metric match config | `feat: qdrant service + documents_chunks collection` | Q4 | 3.5h |
| **Fri (D161)** | Building a basic semantic search endpoint — chunking strategy, indexing pipeline, query-time retrieval | Qdrant docs "Search"; vector-DB vendor chunking-strategies guide | Chunk one long document 3 ways (fixed-size, fixed-size+overlap, paragraph-based), compare chunk counts/quality | `rag/ingest.py` (chunk existing documents → embed → upsert to Qdrant) + `GET /documents/semantic-search?q=` endpoint | Integration test: index 5 known documents, assert the semantically relevant one ranks top-1 for a paraphrase query | `feat: docuvault semantic search endpoint` | Q5 | 3.5h |
| **Sat (D162)** | **Review** | — | Redo Wednesday's cosine-similarity-by-hand exercise from memory | Re-read `rag/ingest.py` for anything hard-coded that shouldn't be | Full suite re-run | — | Answer all Week-40 questions unscripted | 2.5h |

---

## 9. Daily Plan — Week 28: Agents, PeopleOps HR-Policy Agent

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D163)** | Agentic patterns — tool use / function calling, how a model decides to call a tool | OpenAI "Function calling" guide / Anthropic "Tool use" docs | Give a model one fake tool (`get_weather(city)`), confirm it emits a correctly structured tool call for an ambiguous prompt | New `peopleops/agent/` scaffold; tool schema for `get_leave_balance(employee_id)` wrapping PeopleOps' existing leave-balance API | Unit test: tool schema validates against the provider's function-calling spec | `feat: peopleops agent scaffold + leave-balance tool schema` | Q1 | 3.5h |
| **Tue (D164)** | ReAct-style reasoning loops — Reason → Act → Observe, why this beats a single forced tool call | ReAct paper (Yao et al., arXiv:2210.03629), abstract + §3 | Trace one ReAct loop by hand on paper for a 2-step question before writing code | `agent/loop.py` — basic ReAct loop: model reasons, optionally calls `get_leave_balance`, observes result, responds | Test: loop terminates within a max-steps bound on a scripted fake model response | `feat: react loop for hr agent` | Q2 | 3.5h |
| **Wed (D165)** | Multi-step agents with memory — carrying conversation + tool-result history without blowing the context window | OpenAI/Anthropic docs on context management | Simulate a 10-turn conversation, measure token growth, implement a sliding-window/summary trim | Add session memory (last N turns + running summary) to the HR agent | Test memory trims correctly at the configured limit without dropping the current turn | `feat: agent conversation memory with trimming` | Q3 | 3.5h |
| **Thu (D166)** | Agent guardrails & failure modes — looping, hallucinated tool args, calling tools it shouldn't | OWASP Top 10 for LLM Applications — excessive-agency section | Provoke the unguarded agent into calling `get_leave_balance` with a malformed/unauthorized `employee_id`, observe the failure | Add tool-arg validation + max-step limit + a scope check ("agent may only look up the requesting employee's own balance") | Test: agent refuses/errors cleanly on an out-of-scope employee_id instead of leaking data | `feat: agent guardrails — scope check, arg validation, step limit` | Q4 | 3.5h |
| **Fri (D167)** | Orchestrating an agent that calls an external API as a tool — end-to-end wiring, error handling on tool failure | PeopleOps' own API docs + provider tool-use error-handling docs | Simulate the leave-balance API returning a 500/timeout, confirm the agent surfaces a clean fallback instead of crashing | `POST /hr-assistant/ask` endpoint wiring the full agent (HR-policy Q&A + leave-balance tool) into PeopleOps | Integration test: policy-only question answers from docs (no tool call); balance question triggers the tool and returns correct data | `feat: hr-assistant ask endpoint` | Q5 | 3.5h |
| **Sat (D168)** | **Review** | — | Redo the ReAct loop trace from memory | Re-read `agent/loop.py` for the exact failure modes discussed this week | Full suite, all guardrail tests re-run | — | Answer all Week-41 questions unscripted | 2.5h |

---

## 10. Daily Plan — Week 29: Evaluation + Monitoring on DocuVault Semantic Search

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D169)** | RAG evaluation — offline metrics: hit rate, MRR | RAGAS docs "Metrics" | Compute hit rate and MRR by hand on a 5-query toy retrieval result set | Golden eval set for DocuVault semantic search (20–30 query→expected-doc pairs) in `eval/golden_set.json` | — | `feat: docuvault retrieval golden eval set` | Q1 | 3.5h |
| **Tue (D170)** | Implementing an offline eval harness — hit rate/MRR computed automatically against the golden set | — | — | `eval/retrieval_eval.py` runs the golden set through the semantic-search endpoint, reports hit rate@k and MRR | Test harness produces expected metric values on a hand-verified mini fixture | `feat: retrieval eval harness (hit rate, mrr)` | Q2 | 3.5h |
| **Wed (D171)** | LLM-as-judge evaluation — using a model to grade answer quality/faithfulness | RAGAS docs "faithfulness"/"answer relevancy" | Hand-grade 5 answers yourself, then have an LLM judge grade the same 5, compare agreement | `eval/llm_judge.py` scores a generated answer's faithfulness-to-context on a 1–5 scale, wired into the harness | Test: judge output always parses into a valid score, even on malformed judge text | `feat: llm-as-judge faithfulness scoring` | Q3 | 3.5h |
| **Thu (D172)** | Cost & latency tracking for LLM calls; logging chat sessions & feedback loops | OpenAI/Anthropic API docs — usage/token accounting | Log token counts + wall-clock latency for 10 sample calls, compute $ cost from published pricing | `rag/telemetry.py` wraps LLM + embedding calls, logs tokens/cost/latency (reusing Phase 1's structlog); `POST /documents/semantic-search/feedback` (thumbs up/down) | Test telemetry wrapper logs one entry per call with correct fields | `feat: llm cost/latency telemetry + feedback endpoint` | Q4 | 3.5h |
| **Fri (D173)** | A/B testing prompts/models — the statistics underneath: null hypothesis, p-values, confidence intervals, and why a hit-rate delta on 30 golden-set queries usually isn't statistically significant | OpenAI "Best practices for prompt engineering" + Practical Statistics for Data Scientists Ch.3 (or Khan Academy "Significance tests" as a free alternative) | Compute a 95% confidence interval by hand on the two prompt variants' hit rates from Thu's golden set; decide honestly whether the delta is real or noise | Prompt-variant flag on the search endpoint; log which variant served each request, feeding the eval harness; `docs/ab-test-readout.md` reporting the confidence interval, not just "variant B looked better" | Test both variants are exercised roughly evenly (basic split-assignment test) | `feat: prompt variant a/b flag + eval comparison + statistical readout` | Q5 | 3.5h |
| **Sat (D174)** | **Review** | — | Redo the hit-rate/MRR by-hand calculation from memory | Re-run the full eval harness + judge suite; review cost/latency numbers | Full suite re-run | — | Answer all Week-42 questions unscripted | 2.5h |

---

## 11. Daily Plan — Week 30: Best Practices, Project Example — CarePoint Prototype

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D175)** | Query rewriting — reformulating a user's raw question for better retrieval (resolving pronouns, expanding acronyms) | Qdrant docs: Q&A/RAG tutorial | Take 5 real conversational follow-ups ("what about the second one?") and hand-write the rewritten standalone version | New `carepoint/rag/` scaffold; query-rewrite step using conversation history before embedding | Test: a pronoun-referencing follow-up resolves correctly against a fixture history | `feat: carepoint rag scaffold + query rewriting` | Q1 | 3.5h |
| **Tue (D176)** | Hybrid search — combining sparse keyword (Elasticsearch) + dense vector (Qdrant) results | Elastic docs "Hybrid search"; Qdrant docs on combining with keyword search | Run the same query keyword-only, vector-only, and naively combined; compare top-5 results | Ingest CarePoint's FAQ/policy docs into both ES and Qdrant; implement hybrid retrieval (weighted score fusion / RRF) | Test: hybrid retrieval outperforms either single method on a small labeled query set | `feat: carepoint hybrid retrieval (elasticsearch + qdrant)` | Q2 | 3.5h |
| **Wed (D177)** | Re-ranking retrieved chunks before generation | Cross-encoder re-ranking overview | Re-rank Tuesday's hybrid top-20 down to top-5 using a simple cross-encoder or LLM-scored rerank, compare ordering | Add a re-ranking step to CarePoint's retrieval pipeline before prompt assembly | Test: re-ranked top-1 matches the golden answer more often than pre-rerank top-1 on the eval set | `feat: re-ranking step for carepoint retrieval` | Q3 | 3.5h |
| **Thu (D178)** | Caching LLM responses to cut cost; guardrails — prompt injection basics & output validation | OWASP Top 10 for LLM Applications — prompt injection section | Try 3 basic prompt-injection strings ("ignore previous instructions and...") against the unguarded pipeline, observe what breaks | Semantic response cache (normalized-query+context hash) + output validator rejecting injected instructions/unsupported claims | Test: the 3 injection strings are now caught by the validator; cache hit returns identical answer without a new LLM call | `feat: response cache + prompt-injection output guardrail` | Q4 | 3.5h |
| **Fri (D179)** | Reference end-to-end RAG project walkthrough mapped onto CarePoint; writing a short decision record for the chosen stack | DataTalksClub llm-zoomcamp "Project examples" module | — | Prototype the full CarePoint patient-FAQ assistant end-to-end (hybrid retrieval + rerank + generation + injection guardrail) behind `POST /patient-faq/ask`; `docs/carepoint-rag-decision-record.md` | End-to-end integration test: ask a real FAQ question, assert a grounded answer with citation and no guardrail trip | `feat: carepoint patient-faq prototype (end-to-end)` | Q5 | 3.5h |
| **Sat (D180)** | **Review** | — | Redo the RRF/hybrid fusion math from memory | Re-run all injection tests; re-read the decision record for gaps before next week's build | Full suite re-run | — | Answer all Week-43 questions unscripted | 2.5h |

---

## 12. Daily Plan — Week 31: Project 1 — CarePoint Patient-FAQ Assistant (Full Build)

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D181)** | Formalizing the ingestion pipeline for production — versioned re-index, source-doc tracking | Revisit Phase 5 DocuVault reindex notes | — | Production-grade ingestion: `POST /patient-faq/reindex` (rebuild ES + Qdrant from source docs, DocuVault-style recovery), chunk versioning metadata | Test: wiping Qdrant/ES and reindexing fully restores search | `feat: carepoint faq reindex endpoint` | Q1 | 3.5h |
| **Tue (D182)** | Hardening the retrieval+generation API — auth, rate limiting, per-session conversation state | Revisit Phase 1/4 auth & rate-limiting notes | — | Add auth to `/patient-faq/ask`, per-session short conversation memory, rate limiting per patient account | Test: unauthenticated request rejected; rate limit triggers after N requests | `feat: auth, session memory, rate limiting on patient-faq api` | Q2 | 3.5h |
| **Wed (D183)** | Full evaluation suite wired to CI — hit rate, MRR, LLM-judge faithfulness, injection-guardrail regression | — | — | Wire Week 29's eval harness + Week 30's injection tests into CI as a required check on every PR | CI fails if hit-rate/MRR/faithfulness regress below a set threshold | `ci: wire rag eval + guardrail regression suite` | Q3 | 3.5h |
| **Thu (D184)** | Monitoring — cost/latency dashboards, escalation logging (when the assistant hands off to a human) | Revisit Phase 4 Grafana/Prometheus stack docs | — | Grafana panel for cost/latency/hit-rate over time; explicit "escalate to staff" path logged separately on low confidence | Test: a low-retrieval-confidence question triggers escalation, not a guessed answer | `feat: monitoring dashboard + escalation path` | Q4 | 3.5h |
| **Fri (D185)** | Deployment — containerize and ship the assistant inside CarePoint's existing service mesh | Revisit Phase 4/5 deployment notes (Compose/K8s) | — | Add `patient-faq` service to CarePoint's compose/K8s manifests; deploy and smoke-test in the local cluster | End-to-end smoke test against the deployed service | `feat: deploy carepoint patient-faq assistant` | Q5 | 3.5h |
| **Sat (D186)** | **Review/retrospective** | — | Mock-answer all Week-44 questions timed | `docs/postmortem-carepoint-faq.md`, tag `v0.1-carepoint-faq` | Full suite, full CI, deployed smoke test | `docs: carepoint patient-faq postmortem` | Mock-answer all Week-44 questions timed | 2.5h |

---

## 13. Daily Plan — Week 32: Project 2 (DocuVault Chat) + Project 3 (AtlasMarket Assistant), Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D187)** | Formalizing Weeks 27/29's DocuVault prototype into a conversational "ask your documents" chatbot (multi-turn, citations) | Revisit own Week 27/29 notes + provider multi-turn chat docs | — | `POST /documents/chat` — multi-turn RAG chat over the DocuVault corpus, reusing Week 30's hybrid+rerank pipeline, with per-document citation | Integration test: a multi-turn conversation with a follow-up question resolves correctly via query rewriting | `feat: docuvault ask-your-documents chat endpoint` | Q1 | 3.5h |
| **Tue (D188)** | Access-control-aware retrieval — never answer from a document the requester can't read (the Phase 5 deferred concern, solved now) | Revisit Phase 5 DocuVault "Possible Improvements" note | — | Filter Qdrant/ES retrieval results by the requesting user's document permissions before they ever reach the prompt | Test: a user without access to Document X never receives its content, even indirectly, via the chat answer | `feat: access-control-aware retrieval filter` | Q2 | 3.5h |
| **Wed (D189)** | Evaluation + deployment for the DocuVault chatbot | — | — | Wire DocuVault chat into Week 29's eval harness (new golden set for conversational queries); deploy alongside existing DocuVault services | CI eval check + end-to-end deployment smoke test | `feat: docuvault chat eval + deploy`, tag `v0.1-docuvault-chat` | Q3 | 3.5h |
| **Thu (D190)** | AtlasMarket product Q&A — scoping retrieval per-vendor, ingesting product catalog + reviews as the knowledge base | Revisit Phase 6 AtlasMarket vendor-scoping notes + Qdrant/ES metadata-filtering docs | — | Ingest AtlasMarket product descriptions/specs/reviews with `vendor_id`/`product_id` payload; vendor/product-scoped retrieval | Test: a question about vendor A's product never retrieves vendor B's chunks | `feat: atlasmarket product qa ingestion + scoped retrieval` | Q4 | 3.5h |
| **Fri (D191)** | Generation + guardrails + API for the buyer-facing support assistant — no invented specs/prices, escalate to vendor when unsure | — | — | `POST /support/ask` — generation with a strict "answer only from retrieved product data" system prompt + output guardrail rejecting invented prices/specs; escalation path to vendor support | Test: a question with no matching product data triggers escalation, not a fabricated answer | `feat: atlasmarket support assistant api + no-fabrication guardrail` | Q5 | 3.5h |
| **Sat (D192)** | **Phase 7 wrap review** | — | Mock-answer all Phase-7 questions timed, no notes | `docs/postmortem-phase7.md` comparing all three assistants; tag `v0.7-phase7` | Full suite, full CI, all three services deployed and smoke-tested | `docs: phase 7 postmortem + retrospective` | Mock-answer all Phase-7 questions timed | 2.5h |

---

## 14. Deliverables & GitHub Milestones

**Milestone: `Phase 7 — CarePoint FAQ v0.1 + DocuVault Chat v0.1 + AtlasMarket Support v0.1`**
- [ ] DocuVault semantic search over Qdrant (Week 27) with a golden eval
      set and CI-gated hit rate/MRR
- [ ] LLM-as-judge faithfulness scoring wired into the eval harness
- [ ] Cost/latency telemetry + feedback logging on every LLM-backed
      endpoint
- [ ] PeopleOps HR-policy agent with a working leave-balance tool call,
      scope guardrail, and step limit
- [ ] Hybrid search (Elasticsearch + Qdrant) with re-ranking, proven to
      beat single-method retrieval on the eval set
- [ ] Prompt-injection guardrail suite passing on all three assistants
- [ ] CarePoint Patient-FAQ Assistant shipped: retrieval + generation +
      eval + monitoring + escalation path, deployed
- [ ] DocuVault "Ask Your Documents" chat shipped with access-control-aware
      retrieval, zero permission leakage proven by test
- [ ] AtlasMarket Product Q&A Support Assistant shipped with vendor-scoped
      retrieval, zero-fabrication guardrail, per-vendor cost attribution
- [ ] `docs/postmortem-phase7.md` written, comparing all three assistants
- [ ] Tag: `v0.7-phase7`

---

## 15. Skills Acquired Checklist

- [ ] Prompting fundamentals (zero/few-shot, system prompts) and
      open-vs-closed model tradeoffs
- [ ] Text embeddings and cosine similarity — conceptual and hands-on
- [ ] Vector databases (Qdrant): collections, points, HNSW, distance
      metrics
- [ ] Hybrid search: fusing keyword (Elasticsearch) and vector (Qdrant)
      retrieval
- [ ] Re-ranking retrieved results before generation
- [ ] RAG pipeline built by hand: chunk → embed → index → retrieve →
      prompt → generate
- [ ] Agentic tool/function calling and ReAct-style reasoning loops
- [ ] Agent memory management and agent guardrails (scope checks, step
      limits)
- [ ] RAG evaluation: hit rate, MRR, LLM-as-judge faithfulness scoring
- [ ] Cost/latency telemetry and A/B testing for LLM-backed endpoints
- [ ] Hypothesis testing fundamentals: confidence intervals, statistical
      significance — applied to a real metric delta, not just named
- [ ] Guardrails: prompt-injection defenses, output validation,
      no-fabrication checks
- [ ] Access-control-aware / multi-tenant-aware retrieval scoping
- [ ] Shipping a RAG feature end-to-end: retrieval + generation + eval +
      monitoring + deployment

---

**Next:** say "start Phase 8" when you're ready, or tell me what to adjust
in Phase 7 first (pacing, project domain, depth on any topic).
