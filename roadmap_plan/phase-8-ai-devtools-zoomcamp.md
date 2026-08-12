# PHASE 10 — AI Dev Tools Zoomcamp
### Weeks 33–37 (5 weeks) · ~3.5h weekdays, ~2.5h Saturdays · 30 working days

---

## 1. Learning Goals

By the end of Phase 8 you can:

- Explain how Claude Code, GitHub Copilot, and Cursor actually differ
  architecturally (agentic CLI/SDK vs IDE-integrated autocomplete vs IDE
  fork) and pick the right one for a given task instead of treating "AI
  coding tool" as one undifferentiated category.
- Run a full AI-assisted feature workflow — spec → prompt/context → code →
  test → PR — on a real repo, and produce artifacts (the spec, the prompts,
  the diffs, your review notes) that prove the process happened, not just
  ship the final diff and call it done.
- Explain the Model Context Protocol precisely enough to write a custom MCP
  server from the spec (resources, tools, prompts, transports), not from a
  copy-pasted example you don't fully understand.
- Build a minimal coding agent's tool loop by hand, no framework: read a
  plan, call a tool, observe the result, decide the next step, know your own
  stop condition — and explain exactly what a framework like LangChain would
  have abstracted away for you, and why you built it once without one.
- Wire AI into a CI/CD pipeline (a PR-review bot, log-triage summaries)
  while stating precisely, in writing, what it's allowed to do autonomously
  and what always needs a human.
- Build a low-code automation (n8n-style) workflow connecting two of your
  own systems end to end, including a distinct, tested failure path.
- Design and enforce guardrails for an autonomous, code-changing agent:
  scoped file/API permissions, mandatory test gates, a human-approval-
  before-merge step — and defend, specifically, why each guardrail exists
  and what breaks if you remove it.
- Ship three small, real AI-dev-tool systems end to end (a bug-fix agent, a
  cross-system automation pipeline, a freeform capstone), each with a
  documented safety story you could hand to a reviewer.

---

## 2. Technologies Introduced This Phase

Claude Code (CLI + SDK, headless mode, subagents, hooks, permissions,
`CLAUDE.md` memory) · GitHub Copilot (comparison only, not built on) ·
Model Context Protocol — MCP (Python SDK: resources, tools, prompts,
stdio/SSE transports, writing a custom server) · hand-rolled coding-agent
tool-loop architecture (plan → act → observe → decide, no agent framework)
· AI-assisted CI/CD (PR-review bots and log-triage scripts wired into
GitHub Actions, reusing the CI/CD foundation from Phase 4) · n8n (low-code
workflow automation: triggers, nodes, webhooks, credentials) · guardrail
patterns for autonomous agents (scoped permissions, reject-by-default
classifiers, human-approval gates, run logging/auditability).

Deliberately **not yet introduced**: full data-platform / ML-pipeline
tooling (Airflow, dbt, Spark, feature stores, data warehousing) — that's
Phase 11's territory. Also deliberately deferred: model fine-tuning,
running open-weight local models, and multi-agent orchestration frameworks
(CrewAI, AutoGen) beyond the single hand-rolled loop you build this phase —
you build the primitive once by hand specifically so a framework, if you
reach for one later, is a shortcut you understand rather than a black box.
This phase assumes Phase 7's LLM API basics, embeddings, and simple
tool-calling agents as background and builds developer-tooling skill on
top of them, rather than re-teaching them.

---

## 3. PROJECT — StockPilot Bug-Fix Coding Agent (Week 36)

### Business Problem
StockPilot (Phase 1) has, like any live-ish service, accumulated a small
backlog of low-risk maintenance tickets — a missing unit test, a lint/type
failure, an index a query would benefit from per an `EXPLAIN ANALYZE` note
left in Phase 1, a Pydantic validator that's slightly too loose. Each is
tedious for a human and narrow enough that an agent could plausibly close
it — *if* watched. You want a repeatable, safe way to let an agent close a
defined slice of this backlog without becoming the cautionary tale
(autonomous agent merges a bad diff at 2am and breaks prod).

### Requirements
**Functional**
- Given a ticket (a short markdown file), the agent produces a plan, a
  diff, and a full test run — never a diff alone.
- Ticket scope is a declared, narrow class: missing tests, lint/type
  fixes, a documented index migration, tightening an existing validator.
  Explicitly **not** in scope: schema redesigns, auth changes, anything
  touching the stock-decrement transaction logic from Phase 1.
- Uses the StockPilot MCP server (Week 34) as its *only* way to introspect
  the live API, plus scoped filesystem tools to read/write repo files.
- Every run leaves an auditable trail: ticket, plan, diff, test output —
  written to disk before anything is shown to a human.

**Non-functional**
- Every change must pass the full test suite + lint + type-check *before*
  a human ever sees it for approval.
- No run may merge to `main` without an explicit human approval step.
- The agent must refuse — visibly, not silently — any ticket outside its
  declared scope.

### Architecture (tool loop, textual)
```
Ticket (markdown)
  → Classifier step: in-scope vs out-of-scope (reject-by-default)
  → Planner step (LLM call: ticket + repo context → bounded plan)
  → Tool loop:
       read_file / list_dir      (scoped to an explicit path allow-list)
       mcp: stockpilot.get_low_stock / get_product   (read-only)
       write_file                (staged diff, never committed directly)
       run_tests                 (sandboxed subprocess: pytest+ruff+mypy)
  → Stop condition: tests green AND plan's declared scope fully addressed
  → diff + plan + verbatim test output → human-approval gate
  → on approval only: branch + PR opened (no merge/push-to-main tool exists)
```

### Guardrails / Safety
- Filesystem tool is wrapped by an explicit path allow-list (e.g.
  `tests/`, `app/services/`, one migration folder) that rejects any path
  outside it — enforced in code, not by prompt instruction.
- The classifier is a hard, reject-by-default gate run *before* planning
  starts, not a best-effort filter the agent can talk itself past.
- No `git push`/`git merge` tool is exposed at all — the only git-adjacent
  tool is "open a branch + PR"; merging is a human clicking a button.
- MCP tools against live StockPilot are read-only endpoints only — the
  agent can look at the system, never write to it.
- The full test/lint/type-check output is shown to the reviewer verbatim,
  never summarized by the agent itself.
- Every tool call, its arguments, and its result are logged to disk per
  run, so a bad outcome is debuggable from the trace, not just the diff.

### Testing Strategy
Unit test the classifier against in-scope and out-of-scope ticket
fixtures; integration test the full loop against a seeded fake ticket,
asserting it stops correctly and produces a PR-ready branch, never a
merge; a deliberately adversarial ticket ("also drop the orders table")
to prove both the classifier and the missing merge tool hold under a
direct attempt to misuse them.

### Deployment
Invoked manually per ticket from a local machine or scratch container
(`python run_agent.py ticket.md`) — no scheduled or autonomous triggering
yet; that's an explicit, stated possible improvement, not something
shipped this phase.

### Common Interview Questions
1. Where exactly is the human-approval gate, and why there and not earlier
   or later in the pipeline?
2. What happens if the agent's plan drifts outside its declared scope
   mid-run?
3. Why give the agent no merge/push-to-main tool at all, instead of just
   instructing it not to use one?
4. How do you know the test output shown to the reviewer wasn't massaged
   by the agent's own summary?
5. Walk through the tool loop's stop condition — how do you avoid an
   infinite loop?
6. Why MCP instead of hardcoding a couple of HTTP calls straight into the
   agent?
7. What's the failure mode you're most worried about, and which specific
   guardrail addresses it?

### Possible Improvements
Scheduled ticket intake (poll labeled GitHub issues), broader ticket
classes once the approval-gate track record earns trust, multi-file
refactor support, a Slack ping when a PR is ready for review.

### Common Mistakes
Exposing a write tool wider than the ticket strictly needs "just in
case"; trusting the agent's claim that tests pass instead of independently
re-running them before the human sees anything; a classifier that's a
soft suggestion instead of a hard reject; letting the plan and execution
steps share unchecked state so a subtly bad plan silently expands scope
during execution.

---

## 4. PROJECT — Cross-System Automation Pipeline: LedgerBase Weekly Reconciliation (Week 37, Mon–Wed)

### Business Problem
LedgerBase (Phase 4) can produce a trial-balance report on demand, but
nobody proactively checks it — reconciliation only happens when someone
remembers to ask. You want a recurring, unattended pipeline that generates
the weekly reconciliation report and puts it in front of a human
automatically, combining scheduled CI/CD with a low-code automation layer
instead of another bespoke script nobody remembers exists in six months.

### Requirements
**Functional**
- A weekly schedule (e.g. Monday 06:00) triggers a job that calls
  LedgerBase's `/reports/trial-balance` endpoint and runs a reconciliation
  check (does it sum to zero, are there unbalanced entries).
- The report is rendered into a readable artifact and delivered
  automatically: schedule trigger → HTTP request → format → notify.
- The failure path (nonzero trial balance, an unbalanced entry that slipped
  through) is routed to a distinct, urgent channel/tone — never the same
  quiet tone as the routine "all clear" message.

**Non-functional**
- Every run's outcome is logged somewhere durable — not fire-and-forget
  into a chat channel that scrolls away.
- The credential used to call LedgerBase from the automation layer is a
  scoped, read-only reporting token, never the owner/admin credential.

### Architecture (pipeline, textual)
```
GitHub Actions (cron schedule, weekly)
  → script: call LedgerBase /reports/trial-balance (read-only token)
  → write report artifact (json + rendered markdown)
  → POST report payload to an authenticated n8n webhook

n8n workflow:
  Webhook trigger (HMAC-authenticated)
    → Function node: reconciliation check, branch pass/fail
        pass → Slack/email node: "weekly reconciliation OK" + report
        fail → Slack/email node: distinct "finance-alerts" channel, urgent
```

### Guardrails / Safety
The automation's LedgerBase token is read-only at the permission level,
not merely "the workflow happens not to call write endpoints"; the n8n
webhook that receives the report requires an authenticated (HMAC/shared-
secret) header, so nothing else can post fake reconciliation results into
the channel; the GitHub Actions job carries no deploy/merge permissions —
it only runs a read-only report script on a schedule.

### Testing Strategy
Unit test the reconciliation-check function against balanced and
deliberately unbalanced fixture data, independent of scheduling; a manual
"fire the webhook with a fail-case payload" test proving the urgent
branch fires distinctly from the happy path; a dry-run mode on the GitHub
Actions job that skips the real webhook call so cron wiring can be tested
without spamming the channel.

### Deployment
GitHub Actions `schedule:` trigger in the LedgerBase repo calling an n8n
webhook URL (stored as a repo secret); the n8n workflow is exported to
JSON and versioned in the repo, so it isn't an automation that lives only
in someone's n8n UI.

### Common Interview Questions
1. Why split this into "GitHub Actions does the read + compute, n8n does
   the branching + notification" instead of one script doing everything?
2. How do you ensure the read-only reporting token can't quietly become a
   write credential later without anyone noticing?
3. How would you test the failure-path branch without waiting for a real
   unbalanced entry to occur?
4. What does "failure" look like end to end if LedgerBase is simply down
   when the weekly job runs?
5. Why version the n8n workflow as exported JSON in the repo instead of
   leaving it only in the n8n UI?
6. Where exactly did low-code automation earn its place here, versus just
   writing another script?

### Possible Improvements
Monthly rollups, escalation to a second recipient on repeated failures,
auto-opening a GitHub issue on reconciliation failure instead of only a
chat message, a small dashboard of historical run outcomes.

### Common Mistakes
Giving the automation's token more scope than the one endpoint it needs
"in case"; no distinct alerting path for failure, so people tune the
message out; building the whole thing in the n8n UI with zero version
control so nobody else can review or reproduce it; never testing the
failure branch until it fires for real for the first time.

---

## 5. PROJECT — Freeform AI Dev Tool Capstone (Week 37, Thu–Sat)

### Business Problem
An open brief: pick one real gap across your own systems (StockPilot,
LedgerBase, AtlasMarket, or others) that an AI dev tool built this phase's
way — an MCP server + tool loop, a CI/CD automation, or a low-code
pipeline — could close, and ship it fast by reusing this phase's patterns
rather than starting from a blank page. Example directions (pick one, or
propose your own): a natural-language-to-report agent for LedgerBase
("unpaid invoices over $500 last month," answered via MCP tools, never
raw SQL access); an MCP server + minimal agent giving AtlasMarket support
staff a query tool over orders/vendors; or a local "explain this failing
CI run" companion that reads GitHub Actions logs via MCP and proposes a
fix diff.

### Requirements
Functional scope is your choice, but must include: at least one MCP tool
exposing a real read from an existing system (not a mock); a bounded tool
loop or workflow reusing Week 34/36 patterns rather than one hardcoded
prompt call; an explicitly stated guardrail (what it cannot do
autonomously); and a written one-page design note — business problem,
scope, what's deliberately left out — written *before* you start
building, the same way every other project in this roadmap started from a
spec, not a prompt.

### Architecture
Your choice, but diagram it textually in your own repo's `docs/`, the same
discipline every other project in this roadmap has followed — an
undiagrammed system is, by this point, a smell you should notice in
yourself.

### Testing Strategy
At minimum: one integration test proving the MCP tool call round-trips
correctly against the real system, and one test proving the stated
guardrail actually holds — an adversarial input that should be refused,
not merely discouraged.

### Guardrails / Safety
Stated up front, matching the "may/may not act autonomously" framing from
Week 35. A freeform capstone does not get to skip this section just
because the brief is open — if anything it's the part most worth writing
down precisely, since nobody else specified the scope for you.

### Deployment
Whatever's proportionate to the scope you chose — a local script, a small
FastAPI wrapper, or a scheduled GitHub Actions job. Document the choice
and why it's the right amount of infrastructure for what you built.

### Common Interview Questions
1. What specific gap did you choose to close, and why was an AI tool the
   right shape for it versus a regular script or endpoint?
2. What's the one guardrail you refused to skip, and what breaks if you
   remove it?
3. Where did you reuse Week 34/36 patterns versus build something new —
   and was reuse actually the right call here?
4. What would you build next if you had another week?
5. What did you deliberately scope out, and why?

### Possible Improvements
Whatever's next on your own backlog for it — the point of this project is
that you can answer this question yourself by now, without a prompt
telling you what's missing.

### Common Mistakes
Skipping the design note and going straight to prompting — "vibe-coding"
the capstone the exact way Week 33 taught you not to; picking a scope too
broad to finish in three days; dropping the guardrail because "it's just
a capstone, nobody's really going to run this in prod."

---

## 6. Mini-Projects (interleaved through the weeks, listed where they land)

| Mini-project | Week | Teaches |
|---|---|---|
| AI-assisted AtlasMarket feature (prompts + diffs + review-notes dossier) | 46 | End-to-end AI coding workflow, review discipline |
| Custom "hello tool" MCP server (single tool, stdio transport) | 47 | MCP fundamentals: server, tool schema, transport |
| StockPilot MCP server (read-only product/order tools) | 47 | Exposing a real API as MCP resources/tools |
| Hand-rolled minimal coding agent (no framework) | 47 | Tool-loop architecture: plan → act → observe → decide |
| AI PR-review bot (GitHub Action + LLM comment, comment-only) | 48 | AI-assisted CI/CD, scoped bot permissions |
| n8n cross-system notification workflow | 48 | Low-code automation, webhook triggers, branching |

---

## 7. Books & Documentation for This Phase

- Model Context Protocol documentation (modelcontextprotocol.io) —
  "Introduction," "Core architecture," "Build an MCP Server" (Python SDK
  quickstart), and the "Tools," "Resources," and "Prompts" spec pages.
  Read the matching section the same week you build against it (Week 34).
- Claude Code documentation — Quickstart, "Common workflows," "Manage
  Claude's memory" (`CLAUDE.md`), "Permissions," "Subagents," "Hooks,"
  "GitHub Actions integration," and "Headless mode"/SDK usage for scripted
  invocations. Spread across Weeks 33–36 as each topic comes up.
- Anthropic Engineering blog — "Claude Code: Best Practices for Agentic
  Coding" (Week 33, for review discipline) and "Building Effective Agents"
  (Week 34, for tool-loop and planning architecture).
- GitHub Copilot documentation — "What is GitHub Copilot" and its
  IDE/CLI overview pages, read once in Week 33 for landscape comparison
  only; not built on hands-on this phase.
- GitHub Actions documentation (reused from Phase 4) — "Security
  hardening for GitHub Actions" and "Events that trigger workflows:
  schedule," read in Weeks 35 and 50.
- n8n documentation (docs.n8n.io) — "Workflow basics," "Nodes," "Webhook
  trigger," "HTTP Request node," and "Credentials," read across Weeks 35
  and 50.

---

## 8. Weekly Interview Question Sets

**Week 33 — Landscape, end-to-end AI-assisted workflow**
1. What's the actual architectural difference between an agentic CLI tool
   (Claude Code), an IDE-integrated autocomplete (Copilot), and an IDE
   fork (Cursor)?
2. What goes in a spec before you ever open the AI tool, and why does
   skipping it hurt more with AI in the loop than without?
3. What is context engineering, concretely — give an example of a bad
   prompt and the context that fixes it.
4. What do you check in an AI-generated diff that you wouldn't bother
   checking in a human's?
5. Why document prompts and review notes, not just the final diff?

**Week 34 — MCP, coding-agent architectures**
1. What are the three MCP primitives, and what's each one actually for
   (resources vs. tools vs. prompts)?
2. What transport did your MCP server use, and why that one?
3. Walk through your agent's tool loop step by step — what decides when
   it stops?
4. Why build the tool loop by hand once instead of reaching for a
   framework immediately?
5. What's the blast radius if your MCP server exposed a write endpoint by
   mistake?

**Week 35 — AI-assisted CI/CD, low-code automation, guardrails**
1. What can your PR-review bot comment on versus what it's not allowed to
   do (approve/merge)?
2. How would an LLM-based log-triage tool fail silently, and how would
   you catch that?
3. What's a trigger, a node, and a credential, in n8n terms?
4. Walk through your two-system automation end to end, failure paths
   included.
5. Name one guardrail you'd insist on before ever letting a CI bot
   auto-merge anything.

**Week 36 — StockPilot Bug-Fix Agent**
1. Where's the human-approval gate in your agent, exactly?
2. How does your ticket classifier decide in-scope versus out-of-scope,
   and what does it do with an ambiguous ticket?
3. What tools does the agent *not* have access to, and why is that list as
   important as the list it does have?
4. How do you independently verify the agent's test run instead of
   trusting its own summary?
5. What's your adversarial test case, and what does it prove?

**Week 37 — Automation pipeline, freeform capstone, phase retrospective**
1. Why split the reconciliation pipeline between GitHub Actions and n8n
   instead of one script?
2. How do you test a failure-notification path before it happens for
   real?
3. What's the one guardrail you refused to skip in your freeform
   capstone?
4. Across all three Phase 8 projects, what's the common guardrail
   pattern you kept reusing?
5. What would you still *not* trust an autonomous agent to do, even after
   this phase?

---

## 9. Daily Plan — Week 33: AI Dev Tools Overview, End-to-End Workflow, AtlasMarket Feature

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D193)** | Landscape of AI dev tools: Claude Code vs. GitHub Copilot vs. Cursor, how they differ architecturally | Claude Code docs Quickstart/Overview; GitHub Copilot docs "What is Copilot" | Install/configure Claude Code CLI on the AtlasMarket repo, run one trivial prompt end to end | Write `docs/ai-tools-landscape.md` comparison notes; pick the AtlasMarket feature to build this week | Smoke test: confirm the CLI runs and can read the repo | `docs: ai dev tools landscape notes + week46 feature pick` | Q1 from Week46 set — write answer | 3.5h |
| **Tue (D194)** | End-to-end AI-assisted workflow: spec → code → test → PR | Claude Code docs "Common workflows" | Write a one-page feature spec (business problem, requirements, acceptance criteria) | Commit the spec to AtlasMarket: `docs/features/<feature>.md` | Peer-review your own spec against a phase-1-style spec checklist | `docs: spec for <feature>` | Q2 | 3.5h |
| **Wed (D195)** | Prompt/context engineering for coding tasks: `CLAUDE.md`, repo context, scoping the ask | Claude Code docs "Manage Claude's memory" (`CLAUDE.md`); Anthropic prompt engineering guide | Write a `CLAUDE.md` for AtlasMarket capturing architecture + conventions | Prompt the agent with spec + `CLAUDE.md` context to implement the feature; capture the first diff (do not merge) | Run AtlasMarket's existing test suite against the draft diff, note every failure | `wip: first ai-generated draft of <feature> (not reviewed)` | Q3 | 3.5h |
| **Thu (D196)** | Evaluating AI-generated code: review checklist, common failure modes (over-broad diffs, silently wrong edge cases, missing tests) | Anthropic Engineering blog "Claude Code: Best Practices for Agentic Coding" | Build your own AI-diff review checklist (5-8 items) | Apply the checklist to yesterday's diff, write review notes, request specific revisions from the agent | Run full suite + lint/type-check against the revised diff | `review: apply ai-diff checklist, request revisions on <feature>` | Q4 | 3.5h |
| **Fri (D197)** | Shipping the workflow: reviewed diff → merged PR; retro on the process itself | Claude Code docs on PR/GitHub Actions workflow | — | Merge the revised diff, open/land the PR on AtlasMarket; write `docs/features/<feature>-retro.md` documenting prompts + diffs + review notes end to end | Full CI green on the PR | `feat: <feature> — ai-assisted, reviewed, merged` | Q5 | 3.5h |
| **Sat (D198)** | **Review** | — | Redo Wednesday's `CLAUDE.md` from memory, compare against the real one | Re-read your own retro doc, note one thing you'd do differently next time | Full suite re-run | — | Answer all Week-46 questions out loud, unscripted | 2.5h |

---

## 10. Daily Plan — Week 34: MCP Fundamentals, Custom MCP Server, Minimal Coding Agent

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D199)** | MCP protocol fundamentals: resources, tools, prompts, transports (stdio/SSE) | MCP docs "Introduction" + "Core architecture" | Run the MCP Python SDK "hello tool" quickstart server locally, connect a client to it | Scaffold `stockpilot-mcp/` with the MCP SDK installed | Verify the hello-tool server responds via the SDK's test client | `chore: mcp sdk scaffold` | Q1 | 3.5h |
| **Tue (D200)** | Writing a custom MCP server: tool schema design, input validation, error handling | MCP docs "Build an MCP Server" (Python SDK); "Tools" spec | Extend the hello-tool server with a second tool taking structured args | Design tool schemas for StockPilot: `get_low_stock`, `get_product`, `list_orders` (read-only) | Unit test each tool's input validation | `feat: stockpilot mcp tool schemas (read-only)` | Q2 | 3.5h |
| **Wed (D201)** | Wiring an MCP server to a real API: auth, scoped read-only tokens | MCP docs "Resources" | — | Implement the 3 tools against the real StockPilot API with a read-only service token, expose as an MCP server | Integration test: connect an MCP client, call each tool, assert correct data against a seeded StockPilot test DB | `feat: stockpilot mcp server — live read-only tools` | Q3 | 3.5h |
| **Thu (D202)** | Coding-agent architectures: tool loops, planning, ReAct-style reasoning, stop conditions | Anthropic Engineering blog "Building Effective Agents" | On paper, design your own agent's loop (plan → act → observe → decide) before writing any code | Scaffold `mini-agent/`: LLM client + hand-rolled tool-loop skeleton, no framework | Unit test the loop's stop-condition logic against a fake tool | `feat: minimal agent tool-loop skeleton` | Q4 | 3.5h |
| **Fri (D203)** | Connecting the agent to the MCP server end-to-end; logging every tool call for observability | MCP docs "Prompts" spec | — | Wire `mini-agent` to call the StockPilot MCP server's tools; ask it "what products are low on stock right now?" end-to-end | Integration test: agent answers correctly against seeded data; every tool call + args + result logged to disk | `feat: mini-agent + stockpilot mcp — end-to-end query` | Q5 | 3.5h |
| **Sat (D204)** | **Review** | — | Redo the tool-loop stop-condition logic from memory, explain it out loud | Re-read the run log from Friday's session, note anything surprising | Full suite re-run | — | Answer all Week-47 questions unscripted | 2.5h |

---

## 11. Daily Plan — Week 35: AI-Assisted CI/CD, Low-Code Automation, Guardrails

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D205)** | AI-assisted CI/CD: automated PR-review bots | GitHub Actions docs "Building and testing" (reused from Phase 4); Claude Code docs "GitHub Actions integration" | Run a Claude-Code-based GitHub Action on a scratch PR in a test repo, read its comment | Add a PR-review-bot workflow to one real repo (comment-only, no approve/merge permission) | Open a deliberately flawed PR, verify the bot flags it | `ci: add ai pr-review bot (comment-only)` | Q1 | 3.5h |
| **Tue (D206)** | AI in incident response / log triage | Claude Code docs "Headless mode"/SDK for scripted use | Feed a sample log dump to a headless Claude Code invocation, ask for a triage summary | Script `triage_logs.py`: summarize a repo's latest CI failure logs via the LLM API, post a summary comment | Unit test log parsing/formatting; manual test against a real failing run | `feat: ai log-triage summary script` | Q2 | 3.5h |
| **Wed (D207)** | Low-code automation platforms: n8n fundamentals — triggers, nodes, workflow model | n8n docs "Workflow basics," "Nodes" | Stand up n8n locally (Docker), build a trivial workflow (webhook → log) | Environment setup only — no project code this day | Verify the webhook trigger fires and the workflow completes | `chore: local n8n setup` | Q3 | 3.5h |
| **Thu (D208)** | Building a cross-system automation workflow | n8n docs "HTTP Request node," "Webhooks" | — | Build an n8n workflow connecting two systems: StockPilot low-stock data → Slack/email notification | Trigger manually, verify the notification is delivered with correct data | `feat: n8n cross-system low-stock notification workflow` | Q4 | 3.5h |
| **Fri (D209)** | Guardrails for autonomous CI actions: what may/may not auto-merge, scoped permissions, branch protection | GitHub Actions docs "Security hardening for GitHub Actions" | Write a guardrails policy doc: bot may comment, may not approve, may not merge, may not push to `main`, tokens are read-only/scoped | Lock down the PR-review bot's GitHub token permissions explicitly; configure branch protection requiring human review regardless of bot output | Attempt (in a scratch repo) to have the bot approve/merge, confirm it's rejected by permissions | `security: scope pr-review bot permissions + branch protection` | Q5 | 3.5h |
| **Sat (D210)** | **Review** | — | Redo the guardrails policy doc from memory | Re-read both automations (PR bot + n8n workflow) for any scope creep | Full suite + workflow re-run | — | Answer all Week-48 questions unscripted | 2.5h |

---

## 12. Daily Plan — Week 36: Project 1 — StockPilot Bug-Fix Coding Agent

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D211)** | Designing the agent: ticket scope, classifier rules, guardrails plan | Claude Code docs "Subagents"/"Hooks" | Draft the ticket classifier's decision rules on paper (in-scope vs. out-of-scope examples) | Write `docs/bugfix-agent-design.md` (business problem, scope, guardrails); scaffold `bugfix-agent/` | — | `docs: bugfix agent design + scaffold` | Q1 | 3.5h |
| **Tue (D212)** | Building the planner + tool loop wired to StockPilot MCP + repo file tools | MCP Python SDK docs (tool implementation, recap) | — | Implement the planner (ticket + repo context → bounded plan); wire `read_file`/`list_dir`/`write_file` scoped to a path allow-list | Unit test that the path allow-list rejects out-of-scope paths | `feat: bugfix agent planner + scoped file tools` | Q2 | 3.5h |
| **Wed (D213)** | Implementing the human-approval gate | Claude Code docs "Permissions" | — | Add the approval gate (agent stops after diff+test output, requires explicit "approve"); add an "open PR" tool only — no merge/push-to-main tool exists | Test that no PR is created without explicit approval; test the tool registry has no merge/push-to-main tool at all | `feat: human-approval gate + pr-only git tool` | Q3 | 3.5h |
| **Thu (D214)** | Guardrails: reject-by-default classifier, scoped permission enforcement, adversarial testing | GitHub Actions docs "Security hardening" (recap) | — | Make the classifier a mandatory first step (reject-by-default); run full test/lint/type-check gate before showing the diff to a human, verbatim | Adversarial ticket ("also drop the orders table") — assert refusal; test the per-run log-to-disk trace | `feat: ticket classifier reject-by-default + run logging` | Q4 | 3.5h |
| **Fri (D215)** | End-to-end real run | — (application day) | — | Feed the agent one real, defined StockPilot ticket end-to-end: ticket → plan → diff → tests → human approval → PR opened; verify it declines a second, out-of-scope ticket | Full pipeline integration test, recorded as the run-log artifact | `feat: bugfix agent — first real ticket closed end-to-end` | Q5 | 3.5h |
| **Sat (D216)** | **Review / retrospective** | — | Redo the classifier's decision rules from memory | Write `docs/bugfix-agent-retro.md` — what worked, what you'd tighten | Full suite + adversarial-ticket re-run | `docs: bugfix agent retrospective` | Answer all Week-49 questions unscripted | 2.5h |

---

## 13. Daily Plan — Week 37: Project 2 — Reconciliation Pipeline; Project 3 — Freeform Capstone; Phase Wrap

| Day | Topics | Reading | Mini Exercise | Project Task | Testing | Git Commit | Interview Prep | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Mon (D217)** | Designing the reconciliation pipeline: schedule trigger, read-only token scoping | GitHub Actions docs "Events that trigger workflows: schedule" | — | Write `docs/reconciliation-pipeline-design.md`; scaffold the GitHub Actions cron job in LedgerBase calling `/reports/trial-balance` with a read-only token | Manual `workflow_dispatch` trigger verifies the script runs and prints the report | `feat: reconciliation pipeline — scheduled report job scaffold` | Q1 | 3.5h |
| **Tue (D218)** | Building the reconciliation-check + report artifact | — (application day) | — | Implement the reconciliation-check function; render markdown/JSON report artifact; upload as workflow artifact and POST to an n8n webhook | Unit test reconciliation-check against balanced + deliberately unbalanced fixtures | `feat: reconciliation-check + report artifact + webhook post` | Q2 | 3.5h |
| **Wed (D219)** | n8n branch + notify workflow, failure-path testing | n8n docs "Credentials" (webhook auth/HMAC) | — | Build the n8n workflow: authenticated webhook → branch on pass/fail → distinct Slack/email node per outcome; export workflow JSON into the repo | Fire the webhook with a fail-case payload, confirm the urgent branch fires distinctly from a pass-case payload | `feat: n8n reconciliation notify workflow + exported json` | Q3 | 3.5h |
| **Thu (D220)** | Project 3 kickoff: scoping the freeform capstone | Recap of MCP docs + Claude Code "Best practices," as needed for your chosen direction | — | Write the one-page design note (business problem, scope, guardrail, what's left out); scaffold its repo/dir | — | `docs: freeform capstone design note + scaffold` | Q4 | 3.5h |
| **Fri (D221)** | Building the capstone, reusing Phase 8 patterns fast | — (application day) | — | Implement the MCP tool(s) + tool loop/workflow + the stated guardrail; get one real end-to-end path working | Integration test: MCP tool round-trips against the real system; adversarial test proving the guardrail holds | `feat: freeform capstone — end-to-end path working` | Q5 | 3.5h |
| **Sat (D222)** | **Phase 8 wrap review** | — | Explain your bug-fix agent's full pipeline out loud, start to finish, from memory | Write `docs/postmortem-phase8.md` (what's deferred to Phase 11, what you'd harden first); tag `v0.8-phase8` | Full suite across all three Phase-8 projects, all green | `docs: phase 8 postmortem + retrospective` | Mock-answer all Phase-8 interview questions back to back, timed | 2.5h |

---

## 14. Deliverables & GitHub Milestones

**Milestone: `Phase 8 — AI Dev Tools v0.1`**
- [ ] AtlasMarket feature shipped via a documented AI-assisted workflow
      (spec, prompts, diffs, review notes all committed)
- [ ] StockPilot MCP server exposing read-only `get_low_stock`,
      `get_product`, `list_orders` tools
- [ ] Hand-rolled minimal coding agent (`mini-agent/`) answering a
      real natural-language query end-to-end via the MCP server
- [ ] AI PR-review bot live in CI, scoped to comment-only permissions,
      with branch protection requiring human review regardless of its
      output
- [ ] n8n cross-system notification workflow, exported and versioned as
      JSON in a repo
- [ ] StockPilot Bug-Fix Agent: classifier, scoped tools, human-approval
      gate, adversarial test, one real ticket closed end-to-end
- [ ] Cross-system reconciliation pipeline (GitHub Actions + n8n) with a
      tested, distinct failure-notification path
- [ ] Freeform AI dev tool capstone: design note, one working MCP tool
      against a real system, one guardrail with an adversarial test
      proving it holds
- [ ] `docs/postmortem-phase8.md` written
- [ ] Tag: `v0.8-phase8`

---

## 15. Skills Acquired Checklist

- [ ] Comparative fluency across Claude Code, GitHub Copilot, and Cursor —
      architecture, not just feature lists
- [ ] A documented, repeatable AI-assisted feature workflow (spec → prompt
      → code → test → PR) with review discipline
- [ ] Context engineering for coding tasks (`CLAUDE.md`, scoped prompts)
- [ ] MCP fundamentals: resources, tools, prompts, transports — built a
      custom server from the spec, not a tutorial copy-paste
- [ ] A hand-rolled coding-agent tool loop (plan → act → observe → decide),
      with an explicit, tested stop condition
- [ ] AI-assisted CI/CD: a scoped, comment-only PR-review bot; a
      log-triage script
- [ ] Low-code automation (n8n): triggers, nodes, webhooks, credentials,
      branch-on-outcome workflows, versioned as JSON
- [ ] Guardrail design for autonomous, code-changing agents: reject-by-
      default classifiers, scoped file/API permissions, human-approval
      gates, run-level auditability — applied, not just described
- [ ] Three shipped AI-dev-tool systems, each with a written safety story

---

**Next:** say "start Phase 9" when you're ready, or tell me what to adjust
