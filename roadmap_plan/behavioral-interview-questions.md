# Behavioral Interview Questions — Full Bank

Every technical section of this roadmap builds you a bank of real,
specific interview answers by making you actually do the thing. Nothing
equivalent exists for behavioral questions — the roadmap has built you
dozens of genuine "tell me about a time" stories along the way (a bug
found via Sentry, a deadlock reproduced on purpose, a scope cut under
pressure) but never once asks you to write them up as answers. This file
closes that gap the same way `dsa-problems.md` and
`system-design-problems.md` do for their domains: a bank of questions,
each with a pointer to the *real* moment in your own 30 weeks that answers
it, using the STAR method (Situation, Task, Action, Result).

**How to use this file:** for each question, don't write a generic answer.
Open the actual project/postmortem/decision-record named next to it, and
write 4-6 sentences — Situation, Task, Action, Result — grounded in what
actually happened, including the part where it wasn't smooth. An
interviewer can tell a rehearsed-but-real story from a generic one in the
first two sentences. Phase 6's Weekly Interview Question Sets (Weeks 25-28,
see `phase-6-capstone.md`) point to 2 questions per week from this bank,
building toward a full pass on the Saturday of Week 28 — the rest are
yours to keep drafting and refreshing throughout the program, the same way
DSA problems got a Saturday "redo from memory" pass.

---

## Dealing with mistakes, bugs, and being wrong

1. **Tell me about a bug that made it further than it should have before
   you caught it.** → LedgerBase's unbalanced journal entry that slipped
   past app-level validation and was caught via Sentry, not code review
   (Phase 4, Week 18).
2. **Tell me about a time your first solution to a problem was wrong.**
   → The float-based ledger math in LedgerBase, built wrong on purpose to
   feel the bug, then fixed with integer cents (Phase 4, Week 16).
3. **Describe a time you had to debug something without a clear
   reproduction case at first.** → Reproducing a real deadlock in WareFlow
   under concurrent transfers across two warehouses (Phase 3, Week 12).
4. **Tell me about a time you shipped something and it broke in a way you
   didn't anticipate.** → Any deliberately-injected-bug day across the
   roadmap where the fix came from monitoring, not foresight (Sentry catch
   in Phase 4; the outbox-gap you left open on purpose in Phase 3 Week 13
   and only closed two phases later in Phase 5).
5. **Tell me about a time you had to admit a design decision you made
   earlier was wrong, or at least incomplete.** → The outbox-pattern gap:
   you *deliberately* shipped WareFlow (Phase 3) knowing "commit then
   publish" wasn't atomic, documented it as a known gap, and closed it two
   phases later — an unusually honest, well-documented version of this
   story.

## Scope, prioritization, and saying no

6. **Tell me about a time you had to cut scope under a deadline.** →
   AtlasMarket's two-week v1 scope (Phase 6): what you explicitly deferred
   in `docs/atlasmarket-roadmap-post-bootcamp.md` and why that was the
   right call, not a failure.
7. **Describe a time you pushed back on doing something because it wasn't
   worth the complexity.** → Choosing *not* to cache LedgerBase account
   balances (Phase 4) or WareFlow stock levels (Phase 3) — both explicit,
   documented "no" decisions with reasoning, not just omissions.
8. **Tell me about a time you deliberately built something simpler than
   the "correct" version, and why.** → Sharding named-but-not-built for
   DocuVault (Phase 5) — a documented decision record, later backed by a
   real consistent-hashing benchmark, instead of premature complexity.
9. **How do you decide what NOT to build?** → The explicit deferred-scope
   lists that appear across nearly every capstone (AtlasMarket's Phase 6
   roadmap doc, the Year-2 Analytics Platform's `platform-roadmap.md` in
   Phase 11 naming CDC/Iceberg/managed-Airflow as deliberately out of
   scope).
10. **Tell me about a time you had to choose between two reasonable
    technical approaches with no obviously correct answer.** → RabbitMQ
    vs Kafka for WareFlow (Phase 3, `docs/rabbitmq-vs-kafka.md`), or
    Spark vs warehouse SQL for the Year-2 platform (Phase 11,
    `docs/spark-vs-warehouse-sql.md`) — both written decision records with
    a stated, defensible choice.

## Working under pressure / production incidents

11. **Tell me about a time something failed in production (or a
    production-like environment) and you had to respond.** → The Phase 6
    Week 26 incident drill: injecting a real failure into PayFlow,
    following your own on-call runbook blind, and resolving it.
12. **Walk me through how you approach an incident you don't immediately
    understand.** → Same drill — what you checked first, in what order,
    and why (this is literally what the runbook you wrote encodes).
13. **Tell me about a time you had to restore something from a backup, or
    plan for the possibility.** → The Phase 6 Week 26 backup/DR drill
    against LedgerBase: real `pg_dump`, deliberate data corruption in a
    scratch copy, real restore, verified against the trial-balance report.
14. **Describe a time you found a performance problem under load that
    wasn't visible in normal testing.** → PayFlow's idempotency-key
    lookup bottleneck, found via a real `locust` load test in Phase 6,
    Week 26 — not guessed at, measured.

## Collaboration, communication, and technical disagreement

15. **Tell me about a technical decision you had to explain to a
    non-technical stakeholder.** → Explaining to "the shop owner" why
    `current_stock` is denormalized in StockPilot (Phase 1) or why
    account balances aren't cached in LedgerBase (Phase 4) — both written
    as if defending the choice to someone who'd ask "why not just do the
    simple thing?"
16. **Describe a time you had to document a decision so someone else
    (or future you) wouldn't repeat a mistake.** → Any of this roadmap's
    dozens of `docs/*-decision-record.md` files — pick the one you can
    defend best out loud, unscripted.
17. **Tell me about a time you built something specifically so a *future*
    version of a system could reuse it, even though it cost you more up
    front.** → The Repository/Service Layer/Unit-of-Work discipline
    established in Phase 1 and formalized in Phase 3 — paying off visibly
    every time a new project reuses it without re-deriving it (Phase 5,
    Phase 6, and again across every Phase 7-11 project).
18. **Tell me about a time you had to learn a new technology quickly to
    unblock yourself.** → Pick any "introduced the moment it solves a felt
    problem" moment — Redis in Phase 2, RabbitMQ in Phase 3, Kubernetes in
    Phase 5 — and describe what you actually needed to know versus what
    you initially assumed you'd need to know.

## Ownership, growth, and reflection

19. **Tell me about your biggest technical growth moment this year.**
    → Compare your own Day-1 decorator exercise to a late-program
    system — literally what Phase 11's Week 61 "Day 1 vs Day 366"
    retrospective question already asks you to write.
20. **Describe a time you built something you knew was imperfect but
    shipped it anyway, with a plan to improve it.** → Nearly every
    "Possible Improvements" section in this roadmap is a pre-written
    version of this answer — pick StockPilot's Phase-1 v0.1 backlog
    (Redis cache, refresh tokens, soft deletes) as the cleanest example.
21. **Tell me about a time you were the most senior/experienced person on
    a piece of work, or had to make a call with no one to check with.**
    → Any solo capstone decision — the AtlasMarket integration-vs-rebuild
    calls in Phase 6, or picking AWS vs GCP for AtlasMarket's Week 26
    cloud deployment with no second opinion available.
22. **What's a piece of feedback (from a code review, a test failure, a
    postmortem) that changed how you work?** → Any of the `docs/postmortem-
    *.md` files — pick the phase where the "what I'd do differently"
    section is most concrete, not the most flattering.
23. **Tell me about a time you had to balance moving fast against doing
    it right.** → The float-vs-cents LedgerBase story again (Phase 4) —
    but framed this time around the fact that you deliberately built the
    wrong version *first*, specifically to have this exact answer ready.

## System-level thinking and trade-offs

24. **Tell me about the most complex system you've designed and built.**
    → AtlasMarket (Phase 6) or the Year-2 Analytics Platform (Phase 11) —
    pick whichever you can defend in more depth, and be ready for the
    interviewer to ask you to whiteboard it live (this is exactly SD20 in
    `system-design-problems.md`).
25. **Tell me about a time you chose NOT to use the trendiest/most
    powerful tool for a job.** → Explicitly not adopting a GitOps
    controller in Phase 5 (named, not installed), not building CDC in
    Phase 11 (batch-polling instead, on purpose), or not adopting
    LangChain/LlamaIndex in Phase 7 (hand-rolled RAG pipeline instead, so
    you'd know exactly what the framework would have hidden from you).
26. **Describe a time you had to reconcile conflicting requirements
    (e.g. speed vs. correctness, or cost vs. reliability).** → The
    Demand Forecaster's batch-vs-web-service deployment choice in Phase
    10 (`docs/deployment-decision.md` for the No-Show Predictor is the
    single best-documented version of this exact trade-off in the whole
    roadmap).
27. **What's a guardrail or safety mechanism you insisted on even though
    it added friction?** → The StockPilot Bug-Fix Agent's hard,
    reject-by-default classifier and its complete absence of a merge/push
    tool (Phase 8, Week 40) — a guardrail you can explain the exact
    failure mode it prevents.

---

## Using this bank in Phase 6

Phase 6's Weekly Interview Question Sets (Weeks 25-28, see
`phase-6-capstone.md`) point to 2 questions per week from this bank,
answered out loud, the same "unscripted, back to back" discipline every
phase wrap in this roadmap already uses for technical questions. Week 28's
Saturday closes with a full pass through the whole bank. By then you
should be able to answer any question here in under 90 seconds without
notes, using a real project as evidence every time.
