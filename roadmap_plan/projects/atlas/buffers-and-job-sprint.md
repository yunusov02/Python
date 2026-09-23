# Buffers, checkpoints and the job sprint

| | |
|---|---|
| **What this file covers** | The three buffer weeks (B1 in W18, B2 in W37, B3 in W50), which are also the three checkpoints, the three mock interviews, the whiteboard sessions attached to the buffers, the STAR story bank, the CV/README/demo checklists, how to present Atlas in an interview, and the job-application plan from W37 |
| **Hours** | B1 = B2 = B3 = 12 h. These are the **36 buffer hours** in the 702 h Season 1 total (600 must + 66 stretch + 36 buffer, about 13.2 h/week over 53 weeks). The job-search setup and the first batch of applications are inside B2's 12 h. From W38, job-search hours (2–4 h/week) are **not** part of any stage or buffer budget: they come from stretch time first ([the job-application plan](#the-job-application-plan-w37-onward)). |
| **Checkpoints** | B1 (W18), B2 (W37) and B3 (W50). At each one you re-plan with the actual/budget ratio from your hours log (`docs/hours.csv`). |
| **Mock interviews** | #1 in B1 (backend deep dive on S1–S4 plus SD12) · #2 in B2 (payments deep dive plus behavioral) · #3 in [S12](stage-12-data-at-scale-fraud.md) (system design plus backend deep dive) |
| **Whiteboards** | B1: SD5, SD16 · B2: SD10, SD11, SD13 · B3: no new problem, a timed re-run of your weakest one ([system-design-problems.md](../../system-design-problems.md); timing in [system-design-map.md](system-design-map.md)) |
| **Old-spec reading** | [phase-6 D166–D168](../../phase-6-capstone.md) (P10 Stage 3 in [10-atlasmarket.md](../python/10-atlasmarket.md): three timed mock system-design interviews, SD10, SD16, SD20 and a full behavioral pass); [phase-6 §8 "Weekly Interview Question Sets"](../../phase-6-capstone.md) (Weeks 25–28: two behavioral questions per week, answered out loud); [behavioral-interview-questions.md](../../behavioral-interview-questions.md); [system-design-problems.md](../../system-design-problems.md) (the six-step skeleton at the top) |

> **What the buffers are really for.** A plan sized to your weakest week will still slip, because estimates are wrong in one direction. The buffers are where you find out by how much, decide calmly what to cut or how far the date moves, and practise the part of job-hunting that code cannot do for you: saying out loud, under a timer, what you built and why. From W37 the goal shifts from "build Atlas" to "get hired because of Atlas", and this file is the plan for that shift.

---

## Why the buffers exist: the arithmetic

The must tier (600 h) is sized bottom-up, block by block, to the 12 h/week floor: each stage's must hours are exactly 12 × its weeks. Stretch (66 h) happens only when must closes early. The three buffer weeks (36 h) are the planned catch-up time. The degrade list ([schedule-and-cuts.md](schedule-and-cuts.md) §7) shrinks must items when the buffers are not enough.

| Weekly hours | Capacity over 53 weeks | Left after must | What that buys |
|---|---|---|---|
| 12 (the floor) | 636 h | 36 h: exactly the buffers | No stretch and no slack. Any overrun beyond the buffers uses the degrade list or moves the date. |
| ≈ 13.2 (the plan's average) | 702 h | 102 h | The buffers plus all 66 h of stretch |
| 15 | 795 h | 195 h | The buffers, all stretch, and about 93 h spare (job search, or overrun) |

Three consequences to keep in mind all season:
- **There is no fixed overrun allowance.** The block budgets are honest estimates for someone doing this work for the first time, and they are still estimates. Log your actual hours per block in `docs/hours.csv` from S0. At B1, compute the ratio actual ÷ budget over every closed block and re-plan the rest with it: remaining must hours × ratio, against the weeks left to W53 × your real weekly hours. Re-check the ratio at B2 and B3. Example: a ratio of 1.2 at B1, at 13.2 h/week, means S5–S12 (396 h of must) need about 475 h; W19–W53 give 35 × 13.2 ≈ 462 h. You are about 13 h (one week) short before any stretch and before job search, so you drop stretch, apply the first degrade items, and expect the end to move by about a week if the ratio holds. Add 2 h/week of job search from W38 (32 h) and the hours already behind at B1, and the shortfall grows to about 52 h; [schedule-and-cuts.md §4.3](schedule-and-cuts.md#43-worked-example-the-b1-re-plan-at-132-hweek-with-r--12) works that case through.
- **A spine block that overruns moves the date.** Finish it; do not defer it silently. Only non-spine work is degraded.
- **Job search from W38 is not in any budget** (the W37 setup is inside B2). It comes from stretch time first. At the 12 h/week floor there is no stretch time, so every job-search hour moves the end date: 2 h/week from W38 to W53 is 32 h, close to three weeks at 12 h/week. The cadence table in [the job-application plan](#the-job-application-plan-w37-onward) shows what 2 h and 4 h a week buy. Do not cut the spine to make room.

---

## The checkpoint rule

**At B1 (W18), B2 (W37) and B3 (W50):** first re-plan with the measured ratio (below). If you are more than one week behind, **drop all remaining stretch**, then **apply the degrade list in order** until the gap closes. If the gap is still open, **the date moves**; write the new end week in `docs/deferred.md`.

### How to measure "behind"

Measure it in must-tier hours, not in feelings.
1. List every must block, from every stage that should have closed by now, whose acceptance criteria are not all met.
2. Add up their bracketed budgets. For a block that is half done, count the budget you honestly still need.
3. Compare the sum with **one week of your real weekly hours** (12 h at the floor; use your actual average from the last four weeks if it is lower).
4. If the sum is larger, you are more than one week behind and the rule applies.
5. **Re-plan the future with the measured ratio.** From `docs/hours.csv`, compute actual ÷ budget over every block closed so far. Multiply the must hours of the stages still ahead by it, and compare the result with the weeks left to W53 × your real weekly hours. A shortfall there is future lateness: plan the cuts (or the date move) now, in the stages they belong to.

Write the calculation into `docs/deferred.md` at every checkpoint, even when you are on track. A written "on track, 3 h behind, ratio 1.1" at W18 is useful evidence at W37.

### The order of cuts

1. **All stretch items** (66 h across the season). Stop them the moment any checkpoint is behind.
2. **The degrade list**, strictly in its order. Each item shrinks a must item to a cheaper version. The list, its order, each item's hours and the running total live only in [schedule-and-cuts.md](schedule-and-cuts.md) §7; the item numbers there are fixed IDs that the stage files use. What to remember here is the shape of the order:
   - **Requirement-neutral items first**: items that touch no requirement the plan was asked to cover, for example #11 (the UUIDv7 benchmark → reading only), #16 (the capped discount dropped), #18 (the gthread comparison dropped), #14 (the rating aggregator consumer dropped), and #22 (the Lease → the atlaspay scheduler as a single-replica Deployment with the Recreate strategy; the UNIQUE run keys stay).
   - **Items that touch an explicit requirement last, and only as partial degrades** (the prime marks the partial version): for example #1' keeps GraphQL subscriptions and persisted queries and drops only the persisted-query build tooling; #4' keeps a 2-shard Mongo cluster with one bad shard key and the reshard; #6' keeps compression and retention on one hypertable.
   - **#4' and #9 are mutually exclusive**: never apply both, so one resharding run under load always survives.
   - **#24** (the inventory extraction → a checkout Deployment plus the Redis gate, not extracted, with numbers) saves 4.5 h net, less than it seems, because the gRPC foundation (about 2.5 h) then moves to S12 with its hours. Together with #23 it leaves 7 production deployables and gRPC on the ledger only.

3. **If the gap is still open, move the date.** Write the new end week in `docs/deferred.md` with the calculation behind it.

4. **Never cut the spine:** the oversell, idempotency, outbox and ledger invariants, each shown red then green; the 12 provider scenarios; reconciliation; the S6 deploy, observability, PITR and drill; the split gate and every extraction ADR with its numbers; the AtlasPay shadow cutover; the Lua limiter path; Kubernetes basics (probes, preStop, HPA); the gRPC ledger with the load-balancing fix; the Citus single-shard rule; the RAG eval gate and the approval-gated agent; the fraud fallback; SD20 and the mock interviews.

**A subtlety about degrading future items.** Most degrade items belong to stages you have not reached yet. Applying one at W18 does not finish today's late work and does not reduce today's backlog; it frees hours only in its own stage, so the season can still close on time while you finish the late work now. Items for past stages (for example #5 for S3, #11 for S1, #14 for S4, #16 for S2) apply directly if that work is still undone. Record each applied item in `docs/deferred.md`: the item number, the hours saved, the date, and what evidence still exists.

---

## Catch-up rules

These apply in every buffer week and whenever you are behind.

1. **Catch up first.** A buffer week starts with the checkpoint calculation. If anything is behind, the buffer hours go to it before anything in this file.
2. **Spine first.** Within late work, finish never-cut items before other must items.
3. **Budgets still apply.** A late block gets its bracketed budget, not unlimited time. If it overruns again, stop polishing, record what is missing, and move on (the stage convention).
4. **No stretch while behind.** Not even "just one hour".
5. **Do not start the next stage early** if you finish catching up with hours left. Use them for the buffer's own content (the mock, the whiteboards, the README), then for past-stage stretch with interview value.
6. **Long-state tasks on the weekend block** (a PITR restore, a split-gate run, a mock interview), as always.
7. **Keep the rhythm:** three 2 h weekday sessions plus one 5–6 h weekend block. A buffer week is not a sprint week. Burnout is risk 6 in the schedule for a reason.
8. **Re-read `docs/deferred.md`** and run `scripts/compat_check.sh` before planning the next stage.

---

## B1 — buffer, checkpoint and mock #1 (W18, 12 h)

**Where you are:** S0–S4 are closed and `v0.4` is tagged. Atlas is a modular monolith with Celery, RabbitMQ, the outbox, enforced module boundaries, search and a Telegram bot. The first real payment work (S5) starts next week. This is also the first moment you have enough logged hours (about 204 h of must work across S0–S4) to measure how good the estimates are.

### Entry check (1 h, inside the 12 h)

- Run the "behind" calculation above and write it in `docs/deferred.md`.
- **Recalibrate.** From `docs/hours.csv`, compute actual ÷ budget for S0–S4, per stage and overall. Multiply the must hours of S5–S12 (396 h) by the overall ratio and compare with W19–W53 at your real weekly hours. Write the ratio, the projected end week and any planned cuts in `docs/deferred.md`. From S5 on, each stage starts by multiplying its budget by this ratio.
- Check that each of S0–S4 has its tag, its postmortem paragraph and its STAR stories (1 for S0, 2 each for S1–S4: 9 in total).
- If behind: apply the catch-up rules and stop reading this section until you are caught up. What remains of the 12 h goes to mock #1 first, because it is on the spine.

### The hour plan if you are on track

| Item | Hours |
|---|---|
| Entry check and recalibration (above), `compat_check.sh`, S5 plan | 1.5 |
| Mock #1 preparation: reread the S1–S4 interview questions, draft your 3-minute tour of `v0.4` | 1.5 |
| Mock #1: run (60 min) and retro (30 min) | 1.5 |
| SD5 whiteboard | 1.5 |
| SD16 whiteboard | 1.5 |
| README first draft | 2 |
| STAR bank checkpoint: bring the 9 stories to the quality bar | 1.5 |
| Drills (SQL on the Atlas schema, DSA) | 1 |
| **Total** | **12** |

### Mock interview #1: backend deep dive on S1–S4 plus SD12

**Format (60 min, timed):**

| Minutes | Part | What the interviewer does |
|---|---|---|
| 0–5 | Warm-up | "Tell me about a project you are proud of." You give the 3-minute tour of `v0.4`. |
| 5–35 | Deep dive | Picks three topics from the list below and pushes two "why"s down on each. Asks for the evidence ("show me the plan", "how did you prove it"). |
| 35–55 | SD12 Ticket booking | 50,000 people, 20,000 seats, the first minute. You built the core of it in S2 (locked decrement vs EXCLUDE). The interviewer pushes on hold expiry and the waiting room, which you have not built. |
| 55–60 | Feedback | The interviewer scores the rubric out loud. |

**Deep-dive topics (the interviewer picks three):**
- how lazy FK access causes N+1, and how you proved the fix (S1);
- OFFSET vs keyset, and when OFFSET is still right (S1);
- what `FOR UPDATE` locks, and the conditional UPDATE alternative (S2);
- the deadlock you produced and the lock-ordering fix (S2);
- why REPEATABLE READ does not stop write skew (S2);
- why idempotency lives in Postgres, not Redis (S2);
- RLS and pooled connections: the `SET` leak (S2);
- cache stampede, and how you know you found every invalidation path (S3);
- the limiter path from 4× to Lua, and fail-open vs fail-closed per class (S3);
- what the outbox guarantees and what it does not; two relays without double publishing (S4);
- `visibility_timeout` vs `consumer_timeout` (S4).

The full lists are §10 of [Stage 01](stage-01-layered-monolith.md), [Stage 02](stage-02-checkout-correctness.md), [Stage 03](stage-03-redis-auth-bot.md) and [Stage 04](stage-04-async-events-boundaries.md).

**Scored with:** the deep-dive rubric and the system-design rubric (see [Rubrics](#rubrics)). Retro in `docs/sd/mock-01-retro.md`.

### Whiteboards SD5 and SD16

Run each as a 45-minute session using the bank's six-step skeleton (clarify scope, estimate scale, high-level design, data model, one deep dive, trade-offs), then spend 15 minutes writing `docs/sd/sd05-web-crawler.md` and `docs/sd/sd16-proximity.md`: the diagram (photo or export), your numbers, and a short "where Atlas agrees or disagrees" section.

| SD | Atlas anchor | Tie-ins to use as evidence |
|---|---|---|
| SD5 Web crawler | None (whiteboard only) | The URL frontier as a priority queue (your S4 RabbitMQ queues); per-domain politeness as a rate limiter keyed by domain (S3, E10); a Bloom filter for "seen URL" at billions of pages and why a plain hash set does not fit; one slow domain not stalling the crawl (one queue per task class, S4) |
| SD16 Proximity | PostGIS pickup points (whiteboard) | Geohash vs quadtree vs R-tree for "near me"; PostGIS indexes are GiST, the same index family as your S1 `EXCLUDE` constraint; dense Tashkent vs sparse regions without hotspots; re-ranking by rating and "open now" without breaking the spatial index |

### README first draft

At W18 the README describes `v0.4`. It does not need a live URL yet (that arrives with slice 1 in S6). Use the [README checklist](#readme-checklist) and fill in at least:
- the pitch in three sentences;
- the architecture diagram of the modular monolith (with Celery, RabbitMQ, the outbox relay and the bot);
- a "what this proves so far" table covering S1–S4, each row linking to evidence;
- the quickstart;
- the ADR index so far (ADR-000 to ADR-016);
- an honest "limits" section.

### STAR bank checkpoint

Bring the 9 stories from S0–S4 to the quality bar in [The STAR story bank](#the-star-story-bank). Say each one out loud once with a timer. If one runs over two minutes, cut the Situation, not the Result.

### B1 definition of done

- [ ] The checkpoint calculation and the measured actual/budget ratio are in `docs/deferred.md`, with the projected end week; any cuts are recorded with their degrade numbers.
- [ ] Mock #1 done, scored and retro written (`docs/sd/mock-01-retro.md`); every rubric row scored 1 or 2 has a drill item in the next two weeks.
- [ ] `docs/sd/sd05-web-crawler.md` and `docs/sd/sd16-proximity.md` written.
- [ ] README first draft committed.
- [ ] The 9 STAR stories meet the quality bar.

---

## B2 — buffer, job sprint and mock #2 (W37, 12 h)

**Where you are:** S5–S8 are closed and `v0.8` is tagged. Two portfolio slices exist: **slice 1** (W28: the marketplace deployed on a public HTTPS URL, observed and taking simulated payments) and **slice 2** (W36: the AI features). This is the first moment Atlas is worth showing to an employer, so this week turns it into a CV, a README and a demo, and the job search starts.

### Entry check (30 min, inside the 12 h)

As in B1: the "behind" calculation, the actual/budget ratio re-checked over S0–S8 (and the projected end week), tags, postmortems and STAR stories for S5–S8 (8 more, 17 in total). If behind, catch up first. Mock #2 and the CV are the two items you protect.

### The hour plan if you are on track

| Item | Hours |
|---|---|
| Entry check, the ratio re-check and planning for S9 | 0.5 |
| CV v1 | 1.5 |
| README v2 (slices 1 and 2; the README has been kept current since S6, so this is an update) | 1 |
| Demo video: script, record, cut (about 5 minutes) | 2 |
| Mock #2: preparation (including bringing the S5–S8 STAR stories to the bar), run (60 min) and retro | 2.5 |
| SD10, SD11 and SD13 whiteboards (1 h each) | 3 |
| Job-search setup (target list, tracker, CV variants) and the first batch of applications | 1.5 |
| **Total** | **12** |

The setup and the first batch fit inside these 12 h only because CV v1, README v2 and the demo are kept to their budgets. From W38 the job search costs 2–4 h/week on top of the stage hours, from stretch time first (see [The job-application plan](#the-job-application-plan-w37-onward)).

### CV v1

Use the [CV checklist](#cv-checklist). At W37 the Atlas bullets draw on S1–S8 only. Every number on the CV must exist in `docs/evidence/`. If you cannot link it, it does not go on the CV.

### README v2 and the demo video

The README gets the live URL, the slice-1 and slice-2 diagrams, the updated "what this proves" table and the demo video link. The demo covers both slices; see the [demo video checklist](#demo-video-checklist).

### Mock interview #2: payments deep dive plus behavioral

**Format (60 min, timed):**

| Minutes | Part | What the interviewer does |
|---|---|---|
| 0–30 | Payments deep dive, framed as SD18: "design the payment system you built" | Asks you to walk a Payme payment end to end, then injects failures one at a time from S5's 12 scenarios and chaos switches (for example "Payme and Click both paid for one order", "the ×100 amount bug", "Cancel arrives after the order shipped", "reconciliation shows drift", "your Perform response was lost after commit", "Payme retries with a new JSON-RPC `id`"). Asks where the idempotency record is stored and when, why the trigger is deferred, and how a partial refund reverses transfers. |
| 30–55 | Behavioral | Four questions from [behavioral-interview-questions.md](../../behavioral-interview-questions.md), one from each of four different categories. Each answer is at most two minutes, followed by one follow-up ("what would you do differently?", "what did you measure?"). |
| 55–60 | Feedback | Rubric scores out loud. |

**Bring:** the S5 interview questions (§10 of [Stage 05](stage-05-atlaspay-monolith.md)), the S6 operations questions (§10 of [Stage 06](stage-06-ship-and-operate.md)), and your 17 STAR stories. Retro in `docs/sd/mock-02-retro.md`.

### Whiteboards SD10, SD11 and SD13

One hour each: 40 minutes on the skeleton, 20 minutes writing `docs/sd/sd10-video-streaming.md`, `docs/sd/sd11-ride-sharing.md` and `docs/sd/sd13-collaborative-editor.md`.

| SD | Atlas anchor | Tie-ins |
|---|---|---|
| SD10 Video streaming | Media (the CDN stays on the whiteboard for now) | Presigned uploads straight to object storage (S1); an async processing pipeline on a dedicated queue (the S4 `media` queue and thumbnails are the same shape as transcoding); why the bytes never touch your servers at request time; the role of the adaptive-bitrate manifest; CDN placement and cache keys. Atlas meets a CDN only later, as an optional S11 stretch step for the SPA's hashed assets. |
| SD11 Ride sharing | Courier tracking | Geospatial indexing (from SD16); greedy "nearest driver" vs batched assignment; live location to the rider without polling. This previews the fan-out problem you will build in S11. |
| SD13 Collaborative editor | None (whiteboard only) | OT vs CRDTs; why locking the document fails the requirement; propagation over WebSockets; an offline client reconciling on reconnect, which is resume by id (S11) plus idempotent operations |

### B2 definition of done

- [ ] The checkpoint calculation and the re-checked ratio are in `docs/deferred.md`, with the projected end week and your weekly job-search hours.
- [ ] CV v1 exists (outside the public repo), with every number traceable to evidence.
- [ ] README v2 is live with the demo video link.
- [ ] The demo video is recorded and linked.
- [ ] Mock #2 done, scored and retro written (`docs/sd/mock-02-retro.md`).
- [ ] The SD10, SD11 and SD13 notes written.
- [ ] The application tracker exists and the first batch of applications is out.

---

## B3 — buffer and checkpoint (W50, 12 h)

**Where you are:** S9–S11 are closed and `v0.11` is tagged. AtlasPay and `auth` are separate services, everything runs on Kubernetes, `inventory` speaks gRPC, and `edge` serves GraphQL and live updates to a React SPA. S12 comes next and is the heaviest data work of the season: the Citus ledger, the Mongo sharded lab and the fraud service, all with long runs in the weekend blocks. This is the last catch-up week before it, and the last moment a cut can still be planned calmly.

### Entry check (1 h, inside the 12 h)

- Run the "behind" calculation and re-check the ratio over every closed block. Multiply S12's 36 must hours by it and compare with W51–W53 at your real weekly hours, **including your job-search hours**. Write the projected end week in `docs/deferred.md`.
- Check that S9–S11 each have their tag, postmortem paragraph and 2 STAR stories (6 more, 23 in total).
- If behind: apply the catch-up rules first. What remains of the 12 h goes to the S12 de-risk item, because S12's spine items (the gRPC ledger with the load-balancing fix, the Citus single-shard rule, the fraud fallback, SD20) cannot be degraded.

### The hour plan if you are on track

| Item | Hours |
|---|---|
| Entry check and ratio re-check (above), `compat_check.sh` | 1 |
| S12 de-risk, no building: confirm the Citus 14.2 image for PG17 (or plan the `FROM postgres:17` fallback), check that the Mongo sharded lab and a 3-worker Citus cluster fit your RAM, and book the S12 weekend blocks (baseline runs, rebalance, reshard, fraud chaos, SD20, mock #3 with its interviewer) | 1 |
| STAR bank checkpoint: bring the 6 S9–S11 stories to the quality bar | 1.5 |
| CV v2 and README v3: add the strangler cutover, Kubernetes with the gRPC load-balancing fix, and realtime fan-out, each with its evidence link | 2 |
| A 45-minute deep-dive drill on S9–S11 with the technical rubric (a peer, the mentor or a recorded self-mock), plus a 15-minute retro | 1 |
| A timed re-run of the SD problem you scored lowest on in mocks #1–#2, with the six-step skeleton | 1.5 |
| The §10 interview questions of S9–S11, answered out loud | 1.5 |
| Drills (SQL on the Atlas schema, DSA) | 1.5 |
| Slack: rest, or preparation for a scheduled real interview | 1 |
| **Total** | **12** |

This week's job-search hours are on top of these 12 h, like every week from W38.

### B3 definition of done

- [ ] The checkpoint calculation, the re-checked ratio and the projected end week are in `docs/deferred.md`.
- [ ] The S12 de-risk notes are written (image tag or fallback, RAM plan, booked weekend blocks, mock #3 interviewer).
- [ ] The 23 STAR stories meet the quality bar.
- [ ] CV v2 and README v3 committed (the CV outside the public repo).
- [ ] The deep-dive drill and the SD re-run are scored; every rubric row at 1 or 2 has a drill item for S12's drill hours.

---

## Mock interview #3 (S12, W53)

Part of S12's Closing block ([Stage 12](stage-12-data-at-scale-fraud.md), §4.4). It is separate from SD20: SD20 is a solo exercise about Atlas itself; mock #3 is with an interviewer, on a problem you did not build.

**Format (60 min, timed):**

| Minutes | Part | What the interviewer does |
|---|---|---|
| 0–35 | System design | Picks a bank problem you have only whiteboarded (SD4, SD5, SD7, SD10, SD11, SD13 or SD16), at a scale you have not rehearsed. Pushes on the numbers and on one deep dive. |
| 35–55 | Backend deep dive on S9–S12 | Picks three: the shadow cutover and "diff = 0"; the closed-breaker outage and the bulkhead; PKCE, `state` and `nonce`; the gRPC load-balancing trap; fencing tokens; PgBouncer transaction mode; fan-out across pods and resume; DataLoader and cost limits; the Citus shard key and the 2PC cost; the fraud fallback. |
| 55–60 | Feedback | Rubric scores out loud. |

**Bring:** §10 of Stages [09](stage-09-strangler-atlaspay-auth.md), [10](stage-10-kubernetes-grpc-inventory.md), [11](stage-11-realtime-edge-graphql.md) and [12](stage-12-data-at-scale-fraud.md). Retro in `docs/sd/mock-03-retro.md`.

---

## How to run a mock interview

**Who plays the interviewer**, in order of preference:
1. A person: a colleague from your job (preferably not your own manager), someone from a local Python or backend community, or a partner from a peer mock-interview platform. Give them the format table, the topic list and the rubric beforehand.
2. The mentor. Say "mock interview" and it runs the planned mock from this file, asks the questions, pushes back, and scores the rubric (see [README](README.md), "Working with the mentor").
3. A recorded self-mock, as a last resort: shuffle the question list, record screen and voice, answer under the timer, and score the recording with the rubric **24 hours later**. The delay makes you a harsher and fairer judge.

**Conditions:**
- Camera on, a timer visible, no notes. For system design you get a blank page or a whiteboard tool (Excalidraw or similar).
- Speak your reasoning out loud all the time. Silence scores lower than a wrong idea said out loud and then corrected.
- Stop at the time limit even if you are mid-sentence. Real interviews do.
- Record it if the interviewer agrees. Watching yourself explain the outbox is uncomfortable and extremely useful.

**Retro template** (`docs/sd/mock-NN-retro.md`, 30 minutes, the same day):

- date, format and interviewer;
- scores for every rubric row (1–4);
- the top 3 gaps, each as "the answer I gave → the answer I should have given";
- drill items for the next two weeks' drill hours;
- STAR stories or README claims to fix;
- what went well (keep doing it).

---

## Rubrics

Score each row from 1 to 4. **Pass bar:** an average of at least 3 with no row at 1. Every row scored 1 or 2 becomes a drill item for the next two weeks' drill hours.

**Anchors used by every row:** 1 = vague or wrong · 2 = correct textbook answer, no evidence · 3 = correct, with your own evidence and one trade-off · 4 = evidence, trade-off, its limit, and what you would measure next.

### Technical deep dive

| Row | What a 4 looks like |
|---|---|
| Accuracy | No factual errors; corrects the interviewer politely when needed |
| Depth | Goes two "why"s down without hand-waving ("because Postgres takes a row lock, which …") |
| Evidence | Cites a number, a plan or a test from Atlas unprompted, and knows where it lives |
| Trade-offs | Names the alternative and the conditions under which it would win |
| Failure thinking | Says what breaks, how you would detect it, and what the system does meanwhile |
| Communication | Answers the question asked first, then elaborates; checks in ("want me to go deeper on the lock or the retry?") |

### System design

| Row | What a 4 looks like |
|---|---|
| Scope | 3–5 functional requirements and explicit out-of-scope, agreed in the first 5 minutes |
| Estimates | Back-of-envelope QPS, storage and peak-to-average, used later to justify a decision |
| High-level design | Boxes and arrows in under 5 minutes, one sentence per box |
| Data model | The 2–4 core tables or collections with their keys, including the shard key if any |
| Deep dive | One hard part solved with numbers (the bank names the deep dive for each problem) |
| Trade-offs and pushback | Defends choices, concedes gracefully, and says "I would measure this" where true |
| Time management | Covers all six steps; does not spend 20 minutes on one box |
| Use of real experience | Uses Atlas as evidence in short references, never as a monologue |

### Behavioral

| Row | What a 4 looks like |
|---|---|
| Structure | Clear Situation, Task, Action, Result, in about 90 seconds to 2 minutes |
| Specificity | Names the system, the date or stage, and at least one number |
| Ownership | "I" for what you did; honest about a solo project; no blame |
| Difficulty | Includes the part that went wrong, or the wrong first attempt |
| Result | A measurable outcome, linked to evidence you could show |
| Reflection | What you would do differently, stated concretely |

---

## The STAR story bank

A *STAR story* is a behavioral answer in four parts: **S**ituation, **T**ask, **A**ction, **R**esult. Atlas produces about 25 of them as a side effect of building it (1 in S0, 2 in each of S1–S12). S12 picks the best 8.

### The process

1. **Write each story at stage close, while it is fresh**, in `docs/star/sNN-<slug>.md`: under 250 words, with **one number in the Result** that links to its evidence (README conventions).
2. **Review at each buffer:** B1 brings S0–S4 (9 stories) to the quality bar; B2 brings S5–S8 (17 in total); B3 brings S9–S11 (23 in total).
3. **Say them out loud.** Phase 6's old habit still applies: two questions per week from the behavioral bank, answered out loud, unscripted. Use your drill hour.
4. **Map them to questions** with the table below, so every question in [behavioral-interview-questions.md](../../behavioral-interview-questions.md) has at least one Atlas answer. The bank's own pointers name the old Track A projects; replace them with your Atlas stories.
5. **At S12, choose the final 8** using the selection rules.

### The template

- **Title**, stage and tag (for example `S06 · v0.6`).
- **Situation:** 1–2 sentences of business context.
- **Task:** what had to be guaranteed or decided.
- **Action:** what you did, including the wrong first attempt.
- **Result:** one number, linked to `docs/evidence/sNN/…`.
- **Reflection:** what you would do differently.
- **Answers:** the bank question numbers it answers, and the follow-ups you expect.

**Quality bar:** it contains a number from `docs/evidence/`; the wrong turn is in it; an outsider can follow it without knowing Atlas; the spoken version fits in two minutes.

### The stories each stage produces

| Stage | Story 1 | Story 2 |
|---|---|---|
| S0 | Choosing Django despite the sunk FastAPI work | — |
| S1 | The N+1 you found by counting | Discovering the 4× limiter |
| S2 | The deadlock | The Redis idempotency mistake |
| S3 | The stampede | The silent limiter reset caused by eviction |
| S4 | The lost event | The `consumer_timeout` surprise |
| S5 | The lost Perform response | The float drift |
| S6 | The lock-queue stall | The rollback nobody had ever exercised |
| S7 | The writes `w:1` lost | The `-oss` trap |
| S8 | The semantic-cache leak | The gateway retry storm |
| S9 | The shadow diff you caught | The closed-breaker outage |
| S10 | gRPC pinning to one pod | Two holders without fencing |
| S11 | The half-missing updates | The Channels socket drop |
| S12 | The 2PC surprise | Fraud-down with payments still flowing |

### Mapping the behavioral bank to Atlas

The numbers are the questions in [behavioral-interview-questions.md](../../behavioral-interview-questions.md). The candidates are suggestions; the best answer is the one you can defend most concretely.

| # | Question (short) | Atlas candidates |
|---|---|---|
| 1 | A bug that got further than it should have | S5 float drift; S9 the shadow diff you caught |
| 2 | Your first solution was wrong | S2 the Redis idempotency mistake |
| 3 | Debugging without a clear reproduction | S10 gRPC pinning to one pod; S2 the deadlock |
| 4 | Shipped, and it broke unexpectedly | S3 the eviction-driven limiter reset; S4 the `consumer_timeout` surprise |
| 5 | Admitting an earlier design was wrong or incomplete | S12 the 2PC surprise (the naive distribution key); the S8 HS256 minting risk, recorded and fixed in S9 |
| 6 | Cutting scope under a deadline | A checkpoint where you applied degrade items (`docs/deferred.md`) |
| 7 | Pushing back on complexity | ADR-016 if OpenSearch was not adopted; ADR-040's "numbers don't hurt" clause |
| 8 | Deliberately building the simpler version | S7 attributes stayed in JSONB (ADR-024); S6 the cheap fix (a separate gunicorn pool) measured before any extraction |
| 9 | Deciding what not to build | `docs/deferred.md` and any stage's "Deliberately not doing" table |
| 10 | Two reasonable approaches, no obvious winner | ADR-024 JSONB vs Mongo; ADR-038 Channels vs FastAPI; ADR-013 the broker |
| 11 | Something failed in (production-like) operation | The S6 drill (kill the relay) and its postmortem; S12 fraud-down |
| 12 | An incident you did not immediately understand | S6 the lock-queue stall, found with `pg_blocking_pids` |
| 13 | Restoring from a backup | S6 PITR to 1 second before a bad UPDATE, trial balance identical |
| 14 | A performance problem visible only under load | S3 the stampede; S9 the closed-breaker outage; S6 the py-spy bottleneck |
| 15 | Explaining a technical decision to a non-technical person | ADR-020 (a 30-minute stock hold vs Payme's 12-hour window); the ADR-017 legal note |
| 16 | Documenting a decision so it is not repeated | ADR-030 with its split-gate numbers |
| 17 | Building for future reuse at extra cost | `libs/atlaspay-domain` kept framework-free in S5, so S9 rewrote only adapters |
| 18 | Learning a technology quickly | S1 the Django ramp from FastAPI (`docs/learning/fastapi-to-django.md`); S10 Kubernetes |
| 19 | Your biggest growth moment | `docs/sd20-retro.md`: your blank-page design against your shipped system |
| 20 | Shipping something imperfect with a plan | S2 the synchronous email left painful on purpose, fixed in S4; S1 HS256 without rotation, recorded as a gap |
| 21 | Making a call with no one to check with | ADR-000 (Django despite the sunk work); ADR-021 (region) |
| 22 | Feedback that changed how you work | A mock retro; the S6 drill postmortem's "what the runbook missed" |
| 23 | Moving fast vs doing it right | S5 the float commission built wrong first, on purpose |
| 24 | The most complex system you designed and built | Atlas: the 15-minute tour, then SD20 |
| 25 | Not using the trendiest tool | No Kafka in Season 1 (ADR-013); no LangChain (S8); no service mesh (S9) |
| 26 | Reconciling conflicting requirements | E10 fail-open vs fail-closed per limiter class; the fraud fallback (ADR-042) |
| 27 | A guardrail you insisted on despite friction | The S8 agent that proposes but never executes money actions (ADR-029) |

### Choosing the final 8 (S12)

Pick 8 from the ~25 so that together they satisfy all of these:
1. Each of the bank's six categories (mistakes and being wrong; scope and saying no; pressure and incidents; collaboration and communication; ownership and reflection; system-level thinking) has at least one story.
2. At least one story where **you were wrong** (questions 1, 2, 5).
3. At least one **incident** (11–14).
4. At least one **"I said no" or "I built less"** (7–9, 25).
5. At least one **architecture decision backed by split-gate numbers**.
6. At least one **payments** story (S5 or S9), because AtlasPay is your differentiator.
7. At least one **AI** story (S8), because the profile is "backend with AI integration".
8. No two stories with the same lesson.

Record the choice as a coverage table in `docs/star/README.md` (story × category), and write a 90-second version of each of the 8.

**Teamwork questions need your day job.** The bank's collaboration section can be answered from Atlas (explaining a decision, documenting it, building for reuse, learning fast). But interviewers also ask questions the bank does not contain, such as "tell me about a disagreement with a teammate" or "a time you had to convince your team". Atlas is a solo project and cannot honestly answer those. Prepare 2–3 stories from your full-time job for them (without confidential details), and use Atlas for technical depth.

---

## CV checklist

- [ ] **One page** (two at most), a PDF with selectable text and a simple one-column layout, so automatic screening tools can read it.
- [ ] **Headline:** for example "Backend engineer: Python (Django, FastAPI), PostgreSQL, payments, distributed systems, AI integration". Location (Tashkent, UTC+5) and whether you are open to remote work.
- [ ] **Links:** the Atlas repository, the live URL, the demo video, LinkedIn.
- [ ] **Experience first.** Your real job is the strongest line on the CV. 3–5 bullets with outcomes.
- [ ] **Atlas as a project with 4–6 bullets**, each shaped "built X with Y, proven by Z", with your own numbers. For example, at B2 (W37):
  - a multi-vendor checkout that cannot oversell, proven by a two-buyer barrier race repeated ×20 in CI;
  - a Stripe-style payment module with Payme and Click adapters, verified against a protocol-faithful simulator across 12 failure scenarios, with a ledger that reconciles to 0;
  - deployed on Terraform-provisioned infrastructure with CD, zero-downtime migrations, OpenTelemetry traces and a PITR restore verified at your measured RPO/RTO;
  - a RAG assistant on pgvector gated by an eval suite in CI, with PII redaction and an agent that cannot execute refunds without approval.
  At B3 (CV v2), add the strangler cutover, Kubernetes with the gRPC load-balancing fix and realtime fan-out; at S12, the Citus ledger and the fraud fallback.
- [ ] **Never invent a number.** Every number on the CV links to `docs/evidence/`.
- [ ] **Honest wording:** "simulated provider integration (no merchant contract)", "synthetic data", "deployed portfolio system". Never "production traffic", "processed payments" or "users".
- [ ] **Skills:** only what you can defend in a deep dive. That is the confidence rule this plan is built on.
- [ ] **Tailor per application:** reorder the Atlas bullets to match the job's stack. Keep 2–3 variants (payments-focused, platform-focused, AI-focused).
- [ ] If you apply to local companies, a Russian version with identical facts may help. Check what each posting uses.
- [ ] The CV and the tracker live **outside** the public Atlas repository.

---

## README checklist

The README evolves: a first draft in B1 (W18), v1 with a diagram and a 5-minute demo at slice 1 (end of S6, W28), v2 in B2 (W37), v3 in B3 (W50), and the final version in S12 (W53).

- [ ] **Pitch in three sentences:** what Atlas is, what is hard about it, and what it proves.
- [ ] **Architecture diagram of the current tag**, plus the evolution story in one short line per step (monolith → modular → split gate → strangler → Kubernetes → edge → sharded ledger).
- [ ] **"What this proves" table:** claim → evidence link → test or CI job. For example "cannot oversell → `docs/evidence/s02/…` → `concurrency` job".
- [ ] **A numbers table:** the handful of numbers you would quote in an interview, each linked.
- [ ] **Live URL** (from S6) and **demo video** link.
- [ ] **Quickstart:** a clean clone runs with a few commands and seeds data with worldgen.
- [ ] **Repository map** and the **ADR index** with one line per ADR.
- [ ] **Testing and CI overview**, with status badges.
- [ ] **Honest limits:** synthetic data; providers simulated with `provider-sim`, which follows each provider's documented protocol; no real money; a real AtlasPay would need a Central Bank licence (ADR-017); Citus and Mongo HA exist only locally; Kafka/CDC arrive in Season 2.
- [ ] **What's next** (Season 2, briefly).
- [ ] No secrets, tokens or real personal data anywhere, including screenshots.

---

## Demo video checklist

The S6 README has a 5-minute demo. The B2 video covers slices 1 and 2. If both do not fit in about 5 minutes, record two short videos rather than one long one.

**Storyline for B2:**
1. 0:00–0:30 — the pitch and the architecture diagram.
2. Slice 1: browse → cart → checkout → the simulated Payme checkout → the order turns paid → transfers and fees posted → the trial balance is 0.
3. A failure, shown live: a duplicate Payme callback gets the same stored result, wrapped with the current request's JSON-RPC `id`; or kill the relay and show that no event is lost.
4. Observability: the same checkout as one trace in Tempo, and the Grafana dashboard.
5. Slice 2: a streamed answer with citations; a cross-vendor leakage attempt refused; an agent-proposed refund approved by ops and executed exactly once.
6. The last 15 seconds: where the code, the ADRs and the evidence live.

**Recording hygiene:**
- [ ] Synthetic data only. No secrets, tokens or terminal history on screen.
- [ ] A large terminal font and a zoomed browser; 1080p.
- [ ] A clear microphone; a script, but spoken naturally.
- [ ] Chapters or timestamps in the description; captions if possible.
- [ ] Uploaded as unlisted, linked from the README and the CV.
- [ ] Re-cut at S12 if the story changed (the final demo).

---

## Presenting Atlas in interviews

Always start with the business problem, not the technology. Interviewers remember "a marketplace that runs its own payment operator" much better than a list of tools.

### The 3-minute tour

Use it when asked "tell me about a project" or "walk me through your portfolio". Time it until it fits.

| Time | Content |
|---|---|
| 0:00–0:20 | **What:** "Atlas is a multi-vendor marketplace with its own Stripe-like payment operator, integrated with Payme and Click through a simulator that follows their real protocols." |
| 0:20–0:50 | **Shape:** it started as a Django modular monolith, and a service left only when a scripted measurement (the split gate) showed a problem. Give one example with its number. |
| 0:50–1:50 | **One hard problem**, told as a mini-STAR: for example a lost Payme Perform response and the retries it causes, solved by storing the first result and replaying it byte for byte inside an envelope that carries the retry's own JSON-RPC `id`; or the oversell race. Include the number and the test. |
| 1:50–2:30 | **One decision with its counter-argument:** for example the ledger on Citus, labelled "most debatable, revertible", or keeping the back office in Django. |
| 2:30–3:00 | **What you would do differently, and an offer:** "I can go deeper into payments, Postgres, or the Kubernetes and gRPC side, whichever is most useful." |

### The 15-minute tour

Use it when the interviewer says "let's go through your project in detail" or in a system-design round about your own system.

| Minutes | Content |
|---|---|
| 0–2 | The business and the constraints: solo, 12–15 h/week, synthetic data, simulated providers, one monorepo. |
| 2–5 | The architecture evolution (the [README §5.1 evolution table](README.md#51-the-evolution-table)): monolith → modular monolith → split gate → strangler → Kubernetes → edge → sharded ledger. For each service, the reason it left: async and I/O-heavy, long-lived connections, a trust boundary, or a natural shard key. Name what deliberately stayed in Django. |
| 5–12 | **Three deep dives of 2–3 minutes each, chosen for the role:** backend correctness (the checkout race and the outbox); payments (AtlasPay, the Payme protocol, the ledger and reconciliation); platform (the split gate and the shadow cutover, or Kubernetes and the gRPC load-balancing trap); AI (the gateway, the evals and the approval-gated agent). |
| 12–14 | Operations: SLOs, the drill, PITR, what is measured and alerted. |
| 14–15 | Limits and next steps (Season 2), then stop and invite questions. |

**Tailor by role:** a product backend company hears correctness and payments first; a platform or DevOps-leaning team hears the split gate, Kubernetes and observability first; an AI-integration role hears S8 first.

**Have these open in browser tabs:** the demo video, the architecture diagram, one ADR with its numbers (ADR-030 is a good choice), and one Grafana dashboard screenshot.

### Hard questions to prepare

- **"Isn't nine services over-engineered for a solo project?"** "Yes, if they had existed on day one. Each one left only after a measurement, the ledger ADR says its split is marginal and revertible, and the plan has a degrade path that ends with seven. The point was to learn when a split is justified, and I can show you the numbers for each."
- **"Is this real money?"** "No. The providers are simulated by a service that follows their documented protocols, including their failure modes. The same acceptance suite can run against Payme's and Click's sandboxes once there is a merchant contract. A real operator would also need a licence; the ADR notes it."
- **"How much of this did an AI write?"** Answer honestly, then prove it: pick any file and explain every line and every decision in it.
- **"What would you do differently?"** Use your `docs/sd20-retro.md`. It exists for this question.

---

## The job-application plan (W37 onward)

**Budget:** the setup and the first batch are inside B2's 12 h (W37). From W38 to W53 (16 weeks) the job search costs 2–4 h/week, 32–64 h. It is in no stage or buffer budget and comes from stretch time first; put your planned rate into the forward check at B2 and B3 ([schedule-and-cuts.md](schedule-and-cuts.md) §5 step 6; its §4.1 shows the season at each weekly rate). **At the 12 h/week floor there is no stretch time**, so every job-search hour moves the end date unless you work above the floor: 2 h/week from W38 to W53 is 32 h, close to three weeks at 12 h/week. Decide at B2, in writing, which of the two you accept (1 h/week halves the cost). Never cut the spine to make room.

### Setup (W37, in the first job-search hours)

- **A target list** of 30–50 roles in three tiers: dream, realistic, practice. Look for middle+ Python backend roles (Django or FastAPI), fintech and payments, e-commerce and marketplaces, and platform-adjacent roles. Local companies that integrate Payme or Click will recognise what AtlasPay does. For remote roles, note the time-zone overlap from UTC+5.
- **A tracker, kept private** (a spreadsheet outside the repo), with columns: company, role, source, date applied, CV variant, contact or referral, stage, next action and date, notes, outcome.
- **CV variants** (payments, platform, AI) from the CV checklist.

### Weekly cadence

| At 2 h/week | At 4 h/week |
|---|---|
| 1 h: 3–5 tailored applications (reorder the CV bullets; one sentence in the cover note that links the job to a specific Atlas piece) | the same, plus: |
| 30 min: one referral or outreach message, or one useful contribution in a community | 1 h: preparation for any scheduled interview (the company's stack mapped to Atlas; their likely questions) |
| 30 min: update the tracker; a retro on any interview that happened | 1 h: one short public write-up of an ADR or a pain-first result, if you want visibility |

### Review the funnel every two weeks

Count applications → replies → screens → technical rounds → offers. Diagnose the first stage that leaks:
- **Few replies** after about 20 targeted applications: the CV or the targeting is the problem, not the market. Fix it before sending more.
- **Screens that go nowhere:** the 3-minute tour is too long or too technical. Rehearse it with a timer.
- **Technical rounds that fail:** find the rubric row that failed and give it the next two weeks of drill hours.

### The interview loop

After every real interview, spend 15 minutes on a retro, using the mock retro template. Every question you answered badly goes into the drill queue. Every claim you struggled to defend goes back into the README or the CV, either fixed or removed.

### Timeline

| Weeks | Focus |
|---|---|
| W37 (B2) | Setup; the first batch of applications with CV v1 |
| W38–W49 | A steady trickle at the rate you chose at B2; slices 1 and 2 are your talking points, joined by the strangler (S9), Kubernetes (S10) and realtime (S11) stories as those stages close |
| W50 (B3) | The checkpoint: CV v2, and re-balance the job-search hours for W51–W53 against S12's spine items |
| W51–W53 | Keep the rate unless B3 said otherwise; S12 adds the sharding and fraud-fallback stories |
| After W53 | Decide explicitly, in writing, how to split your time between Season 2 and interviewing |

**Protect your current job.** Do not use your employer's time, code or confidential information in Atlas, in the demo or in interview stories.

---

## If you get stuck

**The checkpoint says you are behind, and you do not want to cut anything.**
- Which spine items are late? Finish those first.
- Is the item you want to keep on the degrade list? If yes, is it because it matters for interviews, or because you enjoy it? Only the first is a reason.
- Reread the arithmetic at the top of this file.

**The mock went badly.**
- Which rubric rows scored 1 or 2? Pick the two lowest; nothing else for two weeks.
- Did you answer the question asked, or the one you had prepared? Replay the recording at the moment the answer started.
- Reread: [phase-6 D166–D168](../../phase-6-capstone.md) (the old mock format) and the six-step skeleton at the top of [system-design-problems.md](../../system-design-problems.md).

**The STAR stories sound generic.**
- Does each Result have a number you can link? Does each Action include the wrong first attempt?
- Would a stranger understand the Situation without knowing what Atlas is?
- Reread the "How to use this file" paragraph of [behavioral-interview-questions.md](../../behavioral-interview-questions.md).

**The CV gets no replies.**
- Does the first third of the page say what you do and link Atlas?
- Are the bullets outcomes with numbers, or lists of tools?
- Is the CV tailored to the posting, or the same for every application?

**You cannot find time for applications.**
- Are you at 12 h/week? Then every job-search hour moves the end date (2 h/week is close to three weeks by W53). 1 h/week is a fine rate at the floor; write your choice down at B2 and re-check it at B3.
- Can one weekday session per week become the application session, with the stage work moved to the weekend block?
