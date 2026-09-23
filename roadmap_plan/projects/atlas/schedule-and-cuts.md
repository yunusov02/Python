# Schedule, risks and the cut list

| | |
|---|---|
| **Season 1 length** | 53 weeks (W1–W53, about 12 months), including three buffer weeks: B1 (W18), B2 (W37), B3 (W50) |
| **Budget** | Must 600 h + stretch 66 h + buffers 36 h = **702 h**, which is about 13.2 h/week on average |
| **Floor** | The must tier is sized to 12 h/week: every stage's must tier is exactly 12 h × its weeks (600 h over 50 stage weeks) |
| **Checkpoints** | B1 (W18), B2 (W37), B3 (W50) |
| **Calibration** | Log actual hours per block from S0. At B1, compute actual ÷ budget and re-plan the rest of the season with that ratio ([section 4](#4-scenario-arithmetic)) |
| **Rule at a checkpoint** | More than one week behind: drop all remaining stretch, then apply the degrade list in order until the gap closes. If a spine block is what overran, the date moves; nothing on the spine is deferred silently |

> **What this document is for.** A plan that only works if nothing goes wrong is not a plan. This file shows where the hours go, how a normal week looks, what the arithmetic says at 12, 13.2 and 15 h/week once you know your own overrun ratio, what you check at each checkpoint, which risks are most likely, and exactly what you cut, in what order, when you fall behind. It also lists every stretch item with its hours, the spine you never cut, and how to run the whole thing on a 16 GB laptop.
>
> **Why the season is 53 weeks.** The first version of this plan fitted everything into 34 weeks (381 h of must). A bottom-up review of every block, for a learner who has done about 5 days of FastAPI and has not yet used Django, React, aiogram, Kubernetes, Mongo or scikit-learn, found the block budgets roughly 1.7× too small. The scope stayed; the hours became honest. Every block was re-budgeted from the work it lists, the ramps for new tools got their own blocks (Django in S0, aiogram in S3, ML in S7, React/TypeScript in S11), and a third buffer week was added before S12.

---

## 1. The budget

| # | Stage | Weeks | Calendar | Must | Stretch | Must = 12 × weeks | Tag |
|---|---|---|---|---|---|---|---|
| S0 | [Bootstrap (+ Django orientation)](stage-00-bootstrap.md) | 2 | W1–2 | 24 | 3 | 24 = 24 | v0.0 |
| S1 | [Layered monolith](stage-01-layered-monolith.md) | 4 | W3–6 | 48 | 6 | 48 = 48 | v0.1 |
| S2 | [Checkout correctness](stage-02-checkout-correctness.md) | 3 | W7–9 | 36 | 4 | 36 = 36 | v0.2 |
| S3 | [Redis, auth hardening, bot v1](stage-03-redis-auth-bot.md) | 3 | W10–12 | 36 | 5 | 36 = 36 | v0.3 |
| S4 | [Async, events, boundaries, search](stage-04-async-events-boundaries.md) | 5 | W13–17 | 60 | 7 | 60 = 60 | v0.4 |
| B1 | [Buffer + checkpoint + mock #1](buffers-and-job-sprint.md) | 1 | W18 | — | — | 12 h buffer | — |
| S5 | [AtlasPay v1 + provider-sim](stage-05-atlaspay-monolith.md) | 5 | W19–23 | 60 | 6 | 60 = 60 | v0.5 |
| S6 | [Ship & operate → slice 1](stage-06-ship-and-operate.md) | 5 | W24–28 | 60 | 5 | 60 = 60 | v0.6 |
| S7 | [Polyglot I: Mongo + Timescale + fraud v1](stage-07-polyglot-mongo-timescale.md) | 3 | W29–31 | 36 | 5 | 36 = 36 | v0.7 |
| S8 | [AI integration → slice 2](stage-08-ai-integration.md) | 5 | W32–36 | 60 | 6 | 60 = 60 | v0.8 |
| B2 | [Buffer + job sprint + mock #2](buffers-and-job-sprint.md) | 1 | W37 | — | — | 12 h buffer | — |
| S9 | [Strangler: AtlasPay + auth](stage-09-strangler-atlaspay-auth.md) | 5 | W38–42 | 60 | 6 | 60 = 60 | v0.9 |
| S10 | [Kubernetes + gRPC inventory + bot webhook](stage-10-kubernetes-grpc-inventory.md) | 4 | W43–46 | 48 | 6 | 48 = 48 | v0.10 |
| S11 | [Realtime edge + GraphQL + React](stage-11-realtime-edge-graphql.md) | 3 | W47–49 | 36 | 4 | 36 = 36 | v0.11 |
| B3 | [Buffer + checkpoint](buffers-and-job-sprint.md) | 1 | W50 | — | — | 12 h buffer | — |
| S12 | [Data at scale + fraud service + closing](stage-12-data-at-scale-fraud.md) | 3 | W51–53 | 36 | 3 | 36 = 36 | v1.0 |
| | **Total** | **53** | | **600** | **66** | + 36 buffer = **702** | |

Where the new hours went, in short: the ramps for tools you have not used are budgeted blocks (the Django tutorial and settings reading in S0; a 2 h aiogram ramp in S3; a 2.5 h ML ramp in S7, where the must model is a logistic regression and the gradient-boosted model, precision@k and calibration are stretch; a 3.5 h React/TypeScript ramp in S11); benchmark blocks include their unattended wall-clock time (configurations × runs × about 11 minutes, plus harness and ADR time); and every other block was re-sized from the work it lists. The review also moved a few items into the must tier: the Python concurrency exercise (GIL, threads vs processes) in S2, the vendor bot flow in S4, the bot payment link and Google OIDC in S9, and ADR-037 v2 with the GraphQL numbers in S11. S12 got a third week.

Four rules keep the budget honest:

1. **Must first, stretch only after must closes.** Stretch is not "nice to have if I feel like it"; it is time you have earned by finishing early.
2. **Block budgets are alarms, not guillotines.** Each block in a stage file has a must-tier bracket. When a block reaches its bracket, stop polishing: close it at "acceptance criteria met, tested", not "perfect". Non-spine leftovers go into `docs/deferred.md` with a date. **If the block carries a spine acceptance criterion ([section 8](#8-the-never-cut-spine)), you finish it and the date moves**; a spine item is never deferred silently.
3. **Track actual hours per block, from S0.** A simple CSV in `docs/` is enough: block, bracket, actual, date closed. Without it, a checkpoint is guesswork.
4. **Re-plan with your own ratio.** At B1, divide the actual hours of every closed block by their brackets. That ratio, not a guessed "typical overrun", scales the rest of the season (section 4). Recompute it at B2 and B3.

Every stage now has zero slack between must and capacity at 12 h/week. That is deliberate: the buffers, the measured-ratio re-plan and the degrade list absorb overruns, not padding hidden inside stages.

---

## 2. Weekly rhythm

**Shape of a week (12–15 h):** three 2 h weekday sessions plus one 5–6 h weekend block, with an optional fourth weekday session. That gives 11–12 h without the fourth session and 13–14 h with it.

| Slot | Length | What goes here |
|---|---|---|
| Weekday session 1 | 2 h | Read the old theory days the stage header cites; write the tests for the next block (red first) |
| Weekday session 2 | 2 h | Feature work against those tests |
| Weekday session 3 | 2 h | Feature work; **the drill hour** lives here (see below) |
| Optional weekday session 4 | 2 h | Catch-up, or stretch once must is closed |
| Weekend block | 5–6 h | Anything that needs uninterrupted state (see the list below) |

**The drill hour (1 h a week, always):** one SQL problem on the Atlas schema or one DSA problem from the banks (`../../sql-problems.md`, `../../dsa-problems.md`), plus the week's system-design or interview questions ([system-design-map.md](system-design-map.md)).

**The weekend block is always for work that cannot be split:** cutover rehearsals, deploys under load, PITR restores, chaos runs, resharding under load, `terraform apply`/`destroy`, split-gate runs, mock interviews. These tasks go wrong when interrupted halfway, and their evidence (a log, a CSV, a screenshot) only means something if the run was clean.

**Benchmark blocks contain unattended time.** A split-gate run is a 10-minute scenario plus a 60 s warm-up, so about 11 minutes. A block that compares configurations needs configurations × runs × 11 minutes of wall-clock time before any harness or ADR work: intermediate configurations use 3 runs, and only the final before/after pair uses 5 (ADR-023, ADR-002). Every such block says how many minutes it contains; schedule it in the weekend block and do reading or ADR drafting while it runs.

**Weekend-block candidates per stage** (the long-state tasks each stage contains):

| Stage | Weekend-block tasks |
|---|---|
| S0 | Clean-clone `compose up`; `bench/hello` with 3 runs; the Django tutorial parts 1–2 in one sitting |
| S1 | Seeding 1M products with COPY; OFFSET 400k vs keyset plans; UUIDv7 vs v4 at 1M rows |
| S2 | Barrier race and deadlock reproductions; the promo write-skew race |
| S3 | locust stampede; `kill -9` under RDB vs AOF; Valkey Cluster master failover under load |
| S4 | Broker and relay kill mid-flow; the 35-minute import against `consumer_timeout`; the 5,000-chat broadcast |
| S5 | The chaos run across all 12 provider scenarios; reconciliation with an injected drift |
| S6 | `terraform apply`/`destroy`; expand/contract across 3 deploys under load; PITR restore; the live drill; the split gate (about 11 minutes per run: 3 runs per intermediate configuration, 5 for the final before/after pair) |
| S7 | Loading 20M attempts; the JSONB vs Mongo benchmark; Mongo primary kill under `w:1` vs majority |
| S8 | Split gate plus chat load; HNSW vs IVFFlat builds and recall runs |
| S9 | Shadow cutover rehearsal; key rotation under locust; the Toxiproxy run |
| S10 | Rollouts under load; HPA 2→5→2; the flash sale; the split gate ported to kind; Terraform for k3s |
| S11 | Fan-out across pods on kind; socket drops per deploy |
| S12 | Seeding 50M (or 20M) ledger lines; `citus_rebalance_start()` under load; `reshardCollection` under writes; killing fraud mid-load; SD20 and mock #3 |

**Session habits that save hours:**
- Start by reading the last note you left yourself; end by writing the next step down. Twenty seconds each, and you never lose the first half hour of a session.
- Never end a weekday session in the middle of a migration or with a lab cluster half torn down.
- Tear down lab clusters after the weekend run, especially on 16 GB.

**From B2 (W37) on:** job search takes 2–4 h/week (applications, recruiter calls). It comes out of stretch time first, then out of the overrun cover, never out of the must tier; see [section 4](#4-scenario-arithmetic).

---

## 3. The 53-week calendar

| Week | Stage | Fixed points |
|---|---|---|
| W1 | S0 | Workspace, image, Compose, CI and hooks, decisions, the measurement harness |
| W2 | S0 | Django orientation (tutorial parts 1–2, the settings and deployment-checklist reading); tag v0.0 |
| W3 | S1 | The Django ramp continues inside S1 (budgeted) |
| W4 | S1 | SD6; SD17 part 1 (a five-line note) |
| W5 | S1 | |
| W6 | S1 | Tag v0.1 |
| W7 | S2 | |
| W8 | S2 | SD12 built |
| W9 | S2 | Tag v0.2 |
| W10 | S3 | The 2 h aiogram ramp comes right before bot v1 |
| W11 | S3 | SD2 |
| W12 | S3 | SD3; tag v0.3 |
| W13–W14 | S4 | |
| W15 | S4 | SD14 part 1 |
| W16 | S4 | SD15 paper design |
| W17 | S4 | SD9; SD15 compared with what you built; tag v0.4 |
| **W18** | **B1** | **Checkpoint 1: compute your actual/budget ratio and re-plan**; mock #1; SD5, SD16; README draft |
| W19–W22 | S5 | |
| W23 | S5 | SD18; tag v0.5 |
| W24–W25 | S6 | |
| W26 | S6 | SD19 |
| W27 | S6 | SD17 part 2 |
| W28 | S6 | **Portfolio slice 1** (deployed, observed, taking payments); tag v0.6 |
| W29–W30 | S7 | The 2.5 h ML ramp comes right before fraud v1 |
| W31 | S7 | SD8 storage half; SD19 Timescale part; tag v0.7 |
| W32–W35 | S8 | |
| W36 | S8 | LLM gateway for 50 teams; **portfolio slice 2** (AI features); tag v0.8 |
| **W37** | **B2** | **Checkpoint 2**; mock #2; SD10, SD11, SD13; CV, README, demo video; applications start |
| W38–W39 | S9 | |
| W40 | S9 | SD1 |
| W41 | S9 | |
| W42 | S9 | SD18 revisited; tag v0.9 |
| W43–W44 | S10 | |
| W45 | S10 | SD14 part 2 (Lease) |
| W46 | S10 | SD12 again (flash sale); tag v0.10 |
| W47 | S11 | The 3.5 h React/TypeScript ramp is budgeted in S11, before the SPA block |
| W48 | S11 | SD8 realtime half built |
| W49 | S11 | SD8 write-up; SD7; tag v0.11 |
| **W50** | **B3** | **Checkpoint 3**; the last catch-up before S12 |
| W51 | S12 | |
| W52 | S12 | SD4 |
| W53 | S12 | SD20; mock #3; tag v1.0 |

There is no hidden extension week. If a checkpoint's forward check says the must tier does not fit (section 5), you write the new end date down at that checkpoint, instead of discovering it in W52.

---

## 4. Scenario arithmetic

Season 1 is 53 weeks. Must = 600 h, stretch = 66 h, buffers = 36 h. The degrade list (section 7) can remove up to 49 h of must-tier work: 17.5 h from items that touch no named requirement, then 31.5 h of partial degrades of requested features.

| Weekly hours | Capacity | Left after must | Overrun cover without moving the date |
|---|---|---|---|
| 12 (the floor) | 636 | 36 (the buffers); no stretch | 36 + degrade list 49 = **85 h (14% of must)** |
| 13.2 (the plan's average) | 700 | 100 (buffers + ≈ 64 of stretch) | 100 + 49 = **149 h (25%)** if stretch is forgone |
| 15 | 795 | 195 (buffers + all stretch + 93 spare) | 195 + 49 = **244 h (41%)** |

How to read it:
- **Capacity** is weekly hours × 53.
- **Left after must** is capacity minus 600. It includes the three buffer weeks, because those hours are part of capacity.
- **Overrun cover** is how far the must tier can overrun before the date moves, if you give up all stretch and apply the whole degrade list.

**Job search.** Applications start in the B2 job sprint (W37, inside its 12 h). From W38 to W53 is 16 weeks; at 2–4 h/week that is 32–64 h. It comes out of stretch time first (at 13.2 h/week, the stretch time pays for 2 h/week), then out of the cover. At 12 h/week there is no stretch time: must plus buffers already use every hour (636 = 53 × 12), so every job-search hour comes from working above the floor, from the buffers' overrun cover, or from a later end date. 2 h/week from W38 to W53 is 32 h, close to three weeks at 12 h/week. The 12 h/week column below assumes a cap of 1 h/week (16 h), which the buffers absorb only if your ratio stays near 1.0. Whatever rate you choose, include it in every forward check.

**Why there is no fixed overrun percentage.** The first version of this plan assumed "a realistic 15% overrun". The review of every block estimated 80–120% against those old brackets. The re-baselined brackets absorb most of that, but nobody can know your ratio in advance, and a guessed percentage is exactly the kind of number ADR-002 forbids elsewhere. So the plan uses a measured one: your hours log from S0, divided at B1.

### 4.1 What your measured ratio means for the date

Let **r** = actual hours ÷ bracket hours over all closed blocks. The work still needed is (must hours ahead) × r, plus job-search hours. This table shows the whole season at a constant r, before any re-plan:

| r | 12 h/week (job search 1 h/week) | 13.2 h/week (2 h/week) | 15 h/week (3 h/week) |
|---|---|---|---|
| 1.0 | Needs 616 of 636 h: fits, 20 h spare | Needs 632 of 700 h: fits, with room for all 66 h of stretch | Needs 648 of 795 h: fits, all stretch and ≈ 81 h spare |
| 1.1 | Needs 676 of 636 h: 40 h short. The neutral degrades (≈ 19 h) plus ≈ 21 h of the partial ones, or the date moves ≈ 3.5 weeks | Needs 692 of 700 h: fits, no stretch | Needs 708 of 795 h: fits, all stretch still possible |
| 1.25 | Needs 766 of 636 h: 130 h short. Every degrade (≈ 61 h) still leaves ≈ 69 h: the date moves ≈ 6 weeks | Needs 782 of 700 h: 82 h short. The neutral degrades (≈ 22 h) and ≈ 4.5 more weeks, or every degrade (≈ 61 h) and ≈ 1.5 more weeks | Needs 798 of 795 h: 3 h short; the first neutral degrades close it |
| 1.5 | Needs 916 of 636 h: ≈ 17 weeks more even after every degrade. Re-plan the order of the remaining stages with the mentor; the spine and the two slices keep priority | Needs 932 of 700 h: every degrade (≈ 74 h) and ≈ 12 more weeks | Needs 948 of 795 h: every degrade (≈ 74 h) and ≈ 5.5 more weeks |

Degrade savings are in bracket hours, so they save r × their size in real hours; the table already multiplies them. In practice you learn r at B1, after S0–S4 have cost what they cost and after the S1–S4 degrade items have passed; section 4.3 works through that case.

### 4.2 The cover shrinks as the season goes on

The 49 h of the degrade list is only fully available at the start. An item for a stage you have already finished can no longer be cut. So the later you are behind, the less there is to cut:

| At | Buffer hours still ahead | Stretch hours still ahead | Degrade hours still available | Degrade items still available |
|---|---|---|---|---|
| Start (W1) | 36 | 66 | 49 | all |
| B1 (W18) | 36 (B1 itself, B2, B3) | 41 (S5–S12) | 44 (up to 49 while the S1–S4 work they shrink is still open) | all except 5, 11, 14, 16 (S1–S4), unless that work is still being caught up in B1 |
| B2 (W37) | 24 (B2 itself, B3) | 19 (S9–S12) | 33 | the S9–S12 items: 1', 2, 4' or 9, 7, 8, 17, 19, 21, 22, 23, 24, 25, 26, 27 |
| B3 (W50) | 12 (B3 itself) | 3 (S12) | 7 | the S12 items: 4' or 9, 23, 26 and the S12 half of 27 |

Two consequences:
1. Items for S1–S4 (5, 11, 14, 16) help only while that work is still open: during those stages, or in B1 if you are still catching it up. If a block runs over in S1–S4, apply its degrade item right then instead of waiting for B1.
2. Being behind at B3 is the most dangerous case: only 7 h of degrade and one buffer week remain. B2 is the last checkpoint with real choices; take it seriously.

### 4.3 Worked example: the B1 re-plan at 13.2 h/week with r = 1.2

This is an illustration, not a forecast. Assume S0–S4 took 20% longer than their brackets, no stretch was done, and job search will take 2 h/week from W38.

| Step | Numbers |
|---|---|
| S0–S4 at the end of B1 | 204 h of brackets took 244.8 h, so r = 1.20 |
| Capacity W1–W18 | 18 × 13.2 = 237.6 h |
| Gap at the end of B1 | 7.2 h behind: less than a week, so no mandatory cut; B1 absorbed the rest |
| Forward check: needed | S5–S12 must 396 h × 1.2 = 475.2 h, plus the 7.2 h carried, plus job search 2 h × 16 = 32 h: **514.4 h** |
| Forward check: capacity | W19–W53 = 35 weeks × 13.2 = **462 h** (B2 and B3 included) |
| Shortfall | **52.4 h** |
| Option A | The neutral degrades still ahead (14.5 h × 1.2 ≈ 17.4 h) and an end date about 3 weeks later (≈ W56) |
| Option B | Every degrade still ahead (44 h × 1.2 ≈ 52.8 h) closes the gap with nothing to spare: any further slip then moves the date |
| Option C | Raise the average to about 14.7 h/week for the rest of the season (514.4 ÷ 35), only if that is sustainable (risk 6) |

At 12 h/week with the same ratio, B1 already shows 28.8 h behind (244.8 − 216), which is more than a week, so the checkpoint rule applies at once. The forward check needs 475.2 + 28.8 + 16 = 520 h against 420 h: 100 h short. Every degrade still ahead (≈ 52.8 h) leaves ≈ 47 h, about 4 more weeks (≈ W57).

**Conclusion:** the 53 weeks assume a ratio near 1.0–1.1 at about 13.2 h/week. If yours is higher, B1 tells you by how much in W18, while 35 weeks remain to act. Decide then, in writing: which degrades, which new end date, or which extra weekly hours. Never trade a spine item for a date.

---

## 5. Checkpoints

**When:** B1 (W18), B2 (W37) and B3 (W50). The end of every other stage is a mini-check: run steps 1–4 with the hours log, without the forward check.

**The rule:** if you are more than one week behind at a checkpoint, drop all remaining stretch, then apply the degrade list (section 7) in order until the gap closes. If what overran is a spine block, finish it and move the date.

**The procedure (about 30 minutes, at the start of the checkpoint week).** Steps 1–4 are the "how to measure behind" rule of [buffers-and-job-sprint.md](buffers-and-job-sprint.md); steps 5 and 6 are the ratio and the forward check this file adds.

1. List every must block, from every stage that should have closed by now, whose acceptance criteria are not all met.
2. Add up their bracketed budgets. For a half-done block, count the hours you honestly still need.
3. Compare the sum with **one week of your real hours**: 12 h at the floor, or your actual average over the last four weeks if that is lower.
4. If the sum is larger, you are more than one week behind: remove all remaining stretch, then go down the degrade list in order until the saved hours cover the gap. Skip items whose work is already finished; items for past stages still apply if their work is undone. Remember that **a degrade item for a future stage frees hours only in that stage; it does not reduce today's backlog**. It keeps the end date, while you finish the late work now.
5. **Compute your ratio** (at B1, and again at B2 and B3): r = Σ actual hours ÷ Σ brackets over every closed block in the hours log. Use the last three stages if your early ratio no longer looks like you.
6. **Forward check:** multiply the must tiers of the stages still ahead (after the cuts) by r, add your planned job-search hours, and compare with your remaining capacity at your real weekly hours (section 4.3 shows the arithmetic). If it does not fit, choose now between more degrades, more weekly hours and a later end date, and write the new date down. Finding out in W52 is the failure this step prevents.
7. Write the result into `docs/deferred.md` (what you cut, when, why, the ratio, the date), even when you are on track. A written "on track, 3 h behind, r = 1.05" at W18 is useful evidence at W37.

**What else happens at each checkpoint:**

| Checkpoint | If behind | If on track |
|---|---|---|
| B1 (W18) | Catch up first; the ratio and the forward check decide the rest of the season | Mock #1 (backend deep dive on S1–S4 plus SD12), whiteboards SD5 and SD16, a first README draft, drills |
| B2 (W37) | Catch up first; this is the last checkpoint with real choices (section 4.2) | CV, README and a demo video covering slices 1 and 2; mock #2 (payments deep dive plus behavioural); whiteboards SD10, SD11, SD13; applications start |
| B3 (W50) | Catch up S9–S11 first; only the S12 degrade items remain (about 7 h), so confirm or move the end date now | Interview practice and applications; start S12 with a clean slate |

Details of B1, B2 and B3 are in [buffers-and-job-sprint.md](buffers-and-job-sprint.md).

---

## 6. Risks

| # | Risk | Early signal | Mitigation | If it happens |
|---|---|---|---|---|
| 1 | **Overrun beyond the brackets** | Your ratio after S0 and S1 is above 1.1; a block runs 50% over its bracket; a stage trends past its must tier | Brackets re-estimated bottom-up for a learner new to Django, aiogram, ML and React, with ramp blocks for each; hours logged from S0; checkpoints at W18, W37, W50 with a measured-ratio re-plan | Apply the checkpoint procedure; use degrade items in-stage for S1–S4; if a spine block overran, move the date and write it down |
| 2 | **Laptop RAM** | Swap use, OOM-killed containers, benchmark runs with a wide spread | Peak is about 30 containers, so 32 GB is recommended; on 16 GB use the tactics in section 9 | Move one heavy lab to a short-lived cloud VM (inside the cloud cap), or apply the 16 GB shapes |
| 3 | **Cloud and LLM spend** | The bill passes half the cap before B2 (W37) | Cap cloud at **$50** and LLM at **$30**; `terraform destroy` when idle; CI uses Ollama and the `llm` fake. The staging VPS now lives from W24 to W53 (about 30 weeks) and the k3s VMs join it in S10: in S6, check that the VM size × 30 weeks plus the S10 weekend clusters fits the cap, and record the arithmetic in ADR-021 | Stop the environment; run staging only in weekend blocks |
| 4 | **Provider [U] facts** | A protocol detail you cannot confirm | [U] facts are simulator settings, and the assumption is stated in the test | Keep the setting; note it in ADR-018 |
| 5 | **Tooling drift and [U] image tags** (Citus/pgvector on pg17, the S3-compatible store, the Kubernetes gateway, the MCP SDK) | A pinned image or tag disappears, or a new major version changes behaviour. It has already happened twice: MinIO's community images stopped in 2025 and its repository was archived in 2026, and ingress-nginx was retired (maintenance ended March 2026) | Run `scripts/compat_check.sh` at the start of each stage; versions are pinned as of 2026-09; a year-long season will see more of this | Use the fallbacks recorded in ADR-001 (SeaweedFS if Garage fails you; Traefik's Gateway provider or Envoy Gateway on Kubernetes; building FROM `postgres:17` for Citus) |
| 6 | **Burnout** (the season is now a year long) | Skipped sessions two weeks in a row; dreading the weekend block | Keep the weekly rhythm; long-block tasks only on weekends; three buffer weeks exist; the two portfolio slices (W28, W36) give visible wins halfway | Take the buffer week as a real rest; apply cuts or move the date instead of adding hours |
| 7 | **Scope creep** | "While I'm here, I'll also…" | Keep `docs/deferred.md` and re-read it at the start of every stage; every stage file has a "Deliberately not doing" section | Move the idea to `docs/deferred.md` with the stage where it would belong |

---

## 7. Cut order and the degrade list

**Step 1 — all stretch items (66 h).** Stop them as soon as any checkpoint is behind. The full list is in [section 10](#10-stretch-index).

**Step 2 — the degrade list.** These are must-tier items that shrink, applied in the order below (the first column). The item numbers are stable names, so the stage files can refer to them; they are not the order. Each item keeps the lesson but reduces the build. Items that touch no named requirement come first (group A). Items that touch a requirement you explicitly asked for come last (group B), and each of them is a **partial** degrade: the requested feature still exists in a smaller form.

Savings are in bracket hours. They were estimated from the blocks they shrink; where a stage file states the saving, the two agree. Multiply by your ratio r to get real hours (section 4.1).

**Group A — requirement-neutral (apply first)**

| Order | # | Degrade | Saves | Σ | Stage | What you keep |
|---|---|---|---|---|---|---|
| 1 | 11 | UUIDv7 benchmark → reading only | 1 | 1 | [S1](stage-01-layered-monolith.md) | ADR-005 reasoning, citing the literature and saying so |
| 2 | 16 | Capped discount dropped | 1 | 2 | [S2](stage-02-checkout-correctness.md) | Strategy pattern, rounding, Hypothesis |
| 3 | 18 | gthread comparison dropped | 0.5 | 2.5 | [S6](stage-06-ship-and-operate.md) | py-spy and pg_stat_statements bottleneck hunt |
| 4 | 14 | Rating aggregator consumer dropped; the rating is computed on read | 1 | 3.5 | [S4](stage-04-async-events-boundaries.md) | Verified-purchase reviews |
| 5 | 22 | Lease → the atlaspay scheduler as a single-replica Deployment with the Recreate strategy | 1.5 | 5 | [S10](stage-10-kubernetes-grpc-inventory.md) | UNIQUE run keys as the exactly-once guarantee |
| 6 | 12 | Agent trajectory tests dropped | 1 | 6 | [S8](stage-08-ai-integration.md) | Golden set, injection and leakage suites |
| 7 | 17 | Pact HTTP dropped (the acceptance suite and oasdiff remain) | 1 | 7 | [S9](stage-09-strangler-atlaspay-auth.md) | Pact message contracts |
| 8 | 25 | Google OIDC → Keycloak only | 1 | 8 | [S9](stage-09-strangler-atlaspay-auth.md) | OIDC federation with PKCE, and the "unverified email never auto-links" test, against Keycloak |
| 9 | 10 | Terraform VM → Terraform for DNS and bucket; the VM set up by hand and documented | 1.5 | 9.5 | [S6](stage-06-ship-and-operate.md) | Remote state, plan on PR |
| 10 | 15 | Click reversal client → a manual-refund runbook | 1 | 10.5 | [S5](stage-05-atlaspay-monolith.md) | Reconciliation still flags the case |
| 11 | 8 | Vault dynamic DB credentials → KV plus transit | 1.5 | 12 | [S9](stage-09-strangler-atlaspay-auth.md) | Secrets out of env files; crypto-shredding |
| 12 | 7 | MCP OAuth and the version transform → a static MCP token; header pin plus oasdiff | 2 | 14 | [S9](stage-09-strangler-atlaspay-auth.md) | Versioning gate in CI |
| 13 | 26 | Ledger REST-vs-gRPC benchmark → cite the P9 D151–D153 result and the S10 numbers; ledger restore-verify extension → a written, reviewed procedure | 1.5 | 15.5 | [S12](stage-12-data-at-scale-fraud.md) | ADR-037's REST vs gRPC numbers from S10; the S6 restore-verify job |
| 14 | 27 | The drill hour in S11 and S12 → real interviews and their retros, once the job search produces them (1 h per stage) | 2 | 17.5 | [S11](stage-11-realtime-edge-graphql.md), [S12](stage-12-data-at-scale-fraud.md) | SD20, mock #3 and the stage SD work |

**Group B — partial degrades of requested features (apply last)**

| Order | # | Degrade | Saves | Σ | Stage | What you keep |
|---|---|---|---|---|---|---|
| 15 | 3 | Review summaries dropped | 1 | 18.5 | [S8](stage-08-ai-integration.md) | The other AI features |
| 16 | 13 | Semantic product search → RAG only | 1.5 | 20 | [S8](stage-08-ai-integration.md) | Hybrid retrieval inside RAG |
| 17 | 9 | Citus rebalance under load → an idle rebalance. **Never together with 4'** | 1 | 21 | [S12](stage-12-data-at-scale-fraud.md) | The rebalancer and the identical trial balance; `reshardCollection` under writes stays the resharding-under-load run |
| 18 | 2 | Channels spike → the one-deploy socket-drop count only | 1 | 22 | [S11](stage-11-realtime-edge-graphql.md) | The key number for ADR-038 |
| 19 | 20 | Conversations stay in Postgres JSONB; Mongo only for transcripts plus the benchmark | 3 | 25 | [S7](stage-07-polyglot-mongo-timescale.md) | The honest comparison, the Mongo replica set and transactions on transcripts |
| 20 | 6' | Vendor-sales CAGG and the raw → matview → CAGG comparison dropped | 1.5 | 26.5 | [S7](stage-07-polyglot-mongo-timescale.md) | Compression (ratio recorded) and retention on `fraud_features.events`; the velocity CAGGs |
| 21 | 5 | Redis Cluster lab → the CROSSSLOT demo only; failover written up | 2 | 28.5 | [S3](stage-03-redis-auth-bot.md) | A real cluster, hash slots and hash tags; the failover table as a design |
| 22 | 1' | Persisted-query build tooling → a hand-maintained allow-list of the SPA's operations, still enforced in prod | 0.5 | 29 | [S11](stage-11-realtime-edge-graphql.md) | Subscriptions over WS, persisted queries, DataLoader, cost limits, field auth |
| 23 | 4' | Mongo sharded lab: drop one of the two bad shard keys. **Only if 9 was not applied** | 0.5 | (instead of 9) | [S12](stage-12-data-at-scale-fraud.md) | The 2-shard cluster, the unique-index step, one bad key, the reshard under writes from it, targeted vs scatter-gather `explain` |
| 24 | 19 | React SPA and the S11 React/TypeScript ramp → server-rendered pages plus a WS client script | 7 | 36 | [S11](stage-11-realtime-edge-graphql.md) | The BFF cookie session, live updates and the Playwright test |
| 25 | 21 | Real Kubernetes deploy → kind only; the cloud stays Compose-on-VPS | 5 | 41 | [S10](stage-10-kubernetes-grpc-inventory.md) | Probes, preStop, HPA on kind |
| 26 | 23 | Fraud service → in-process in atlaspay with the same fallback, versioning and latency test | 3.5 | 44.5 | [S12](stage-12-data-at-scale-fraud.md) | The fraud fallback (spine) |
| 27 | 24 | Inventory extraction → checkout Deployment plus Redis gate; ADR-036 records "not extracted" with numbers. The gRPC foundation (≈ 2.5 h) moves to S12, so the saving is net | 4.5 | **49** | [S10](stage-10-kubernetes-grpc-inventory.md) | The flash-sale numbers, ADR-036 as a decision not to split, gRPC on the ledger |

Group A totals 17.5 h; group B 31.5 h (item 4' is counted only in place of item 9). The last four items are the largest and take away the most visible form of a requested feature; if you are reaching them, the date question in section 4 should already have been answered at a checkpoint.

**Interactions to know before you cut:**
- **Items 4' and 9 are mutually exclusive.** Apply at most one, so one resharding run under load (the Citus rebalance or `reshardCollection` under writes) always survives. Item 9 comes first in the order; 4' is only for the case where the Citus rebalance under load is already done.
- **Item 24** saves 4.5 h net, not the whole gRPC-inventory block: the gRPC foundation built there (`libs/atlas-proto`, `buf lint`/`buf breaking` in CI, the interceptors, the status-code mapping and the HTTP/2 load-balancing exercise) moves to S12 §4.1 with its hours.
- **Items 23 and 24 together** leave gRPC on the ledger only. The HTTP/2 load-balancing exercise then happens on the ledger in S12; the spine requires "the gRPC ledger with the load-balancing fix".
- **Item 20** keeps conversations in Postgres. The S12 Mongo sharding lab is not blocked by it: that lab loads a worldgen copy of `atlas_conversations.messages` into the sharded cluster anyway, separate from the production chat path. Say in ADR-041 that the sharded collection is a lab copy.
- **Item 21** means S10's CD target stays the S6 VPS; `kind-e2e` in CI still runs. A real Telegram webhook then never runs in Kubernetes: the bot webhook is tested with the fake Bot API on kind only.
- **Item 19** already includes skipping the S11 React/TypeScript ramp.
- **Item 13** removes the product embeddings Season 2 uses for kNN recommendations; 2C then generates them first ([season-2.md](season-2.md)).
- **Item 6'** is covered for Season 2 by the 2A warehouse marts.
- **Item 27** applies only when real interviews exist; a drill hour you simply skip is not a degrade.
- **The OpenSearch stretch (S4):** if the judged set passes on Postgres, ADR-016 says "OpenSearch not adopted" and those 6 h never enter the plan.

For how each degrade item affects the requirement rows, see [coverage-matrix §5](coverage-matrix.md#5-rows-the-degrade-list-weakens).

---

## 8. The never-cut spine

These items are the portfolio. If you have to choose between one of these and a date, move the date, and write the new end week into `docs/deferred.md` at the next checkpoint (section 5). There is no hidden extension week to fall back on.

| Spine item | Where | Why interviewers probe it |
|---|---|---|
| The oversell, idempotency, outbox and ledger invariants, each shown red then green | [S2](stage-02-checkout-correctness.md), [S4](stage-04-async-events-boundaries.md), [S5](stage-05-atlaspay-monolith.md) | These are the correctness questions of every backend interview: races, money, duplicate delivery |
| The 12 provider scenarios | [S5](stage-05-atlaspay-monolith.md) | Proof you understand retries, timeouts and lost responses in a real protocol |
| Reconciliation | [S5](stage-05-atlaspay-monolith.md) | "How do you know your money is right?" |
| The S6 deploy, observability, PITR and drill | [S6](stage-06-ship-and-operate.md) | The difference between writing code and running a system |
| The split gate and every extraction ADR with its numbers | [S6](stage-06-ship-and-operate.md) onward | "Why did you split this?" is the question that separates middle+ from middle |
| The AtlasPay shadow cutover | [S9](stage-09-strangler-atlaspay-auth.md) | Migrating a live payment path without losing a payment |
| The Lua limiter path | [S3](stage-03-redis-auth-bot.md) | The classic distributed-counter race, shown and fixed |
| Kubernetes basics: probes, preStop, HPA | [S10](stage-10-kubernetes-grpc-inventory.md) | Zero-downtime on the platform most employers use |
| The gRPC ledger with the load-balancing fix | [S12](stage-12-data-at-scale-fraud.md) (and [S10](stage-10-kubernetes-grpc-inventory.md)) | The HTTP/2 pinning trap is a favourite follow-up |
| The Citus single-shard rule | [S12](stage-12-data-at-scale-fraud.md) | Choosing a shard key from your own access pattern |
| The RAG eval gate and the approval-gated agent | [S8](stage-08-ai-integration.md) | AI features built like production software |
| The fraud fallback | [S12](stage-12-data-at-scale-fraud.md) | How a model degrades safely in a payment path |
| SD20 and the mock interviews | [S12](stage-12-data-at-scale-fraud.md), [buffers](buffers-and-job-sprint.md) | The rehearsal for the real thing |

---

## 9. Laptop resources: 16 GB vs 32 GB

The heaviest moments of Season 1 run about 30 containers at once, so **32 GB is recommended**. Everything is still possible on 16 GB with the tactics below; the lessons do not change, only the sizes.

### 9.1 The 16 GB tactics

1. **Compose profiles per stage.** Start only what the current exercise needs. A stage file's architecture diagram tells you which services are involved.
2. **Lab clusters are ephemeral.** The Valkey 3+3 cluster (S3), the Mongo replica set and sharded cluster (S7, S12) and Citus (S12) are started for the weekend run and torn down afterwards.
3. **A 2-node kind cluster** in S10–S11.
4. **Citus with 1 coordinator + 2 workers.**
5. **Mongo with a config shard** (the 8.0 option that saves a separate config-server replica set).
6. **20M ledger lines instead of 50M** in S12.

### 9.2 Additional habits

- **Set memory limits on every container.** The ADR-002 benchmark protocol requires fixed CPU and memory limits anyway; on 16 GB they also stop one runaway service from killing the rest.
- **Size databases small on purpose.** Lower Postgres memory settings for lab clusters; you are measuring relative differences, not tuning for a server.
- **Cap JVM heaps** for Keycloak (S9) and OpenSearch (if S4 adopts it); in Season 2, Kafka too.
- **No swap during benchmarks.** Swap is a safety net for everyday work, but a benchmark that swaps measures your disk, not your design. If a benchmark run swaps, discard it.
- **Close the browser and the IDE's indexer during benchmark runs**, keep the laptop on power, and record the CPU model (ADR-002). Laptops throttle when hot; the "at least 3 runs, report median and min–max" rule exists partly for this.
- **You are on native Linux**, so containers run without a VM layer. That saves memory compared with Docker Desktop; keep it that way for benchmarks.

### 9.3 Disk

- Large datasets (1M products, 20M attempts, 20–50M ledger lines), the WAL archive and images add up. Check Docker disk use weekly and prune old images and volumes.
- **Run the replication-slot disk-fill exercise (S6) on a small, dedicated volume**, never on the laptop's main disk. The same applies to the CDC slot exercise in Season 2.

### 9.4 When the laptop is not enough

Rent a short-lived cloud VM for one weekend run (for example the Citus rebalance under load), created and destroyed with Terraform. It counts against the $50 cloud cap, so plan it.

| Stage | Heaviest moment | 16 GB shape |
|---|---|---|
| S3 | Valkey 3+3 cluster under locust with market | Stop everything except market, its Postgres and the cluster |
| S6 | Full observability stack plus replica plus split gate | Run the split gate against the VPS or with the observability stack reduced to Prometheus + Tempo |
| S7 | Mongo replica set plus Timescale plus 20M attempts | Load Timescale, run its exercises, stop it, then run the Mongo exercises |
| S9 | Keycloak, Vault, atlaspay, auth, market, provider-sim, Toxiproxy | Compose profile for the cutover path only; cap Keycloak's heap |
| S10 | kind with every service | 2-node kind; single replicas except where the exercise needs more (HPA, per-pod spread) |
| S12 | Citus plus the Mongo sharded cluster plus fraud | Never at the same time; Citus 1 + 2, Mongo with a config shard, 20M lines |

---

## 10. Stretch index

Every stretch item in Season 1, with hours, as the stage files' Stretch sections list them. Stretch is done only when a stage's must tier closes early. Total: **66 h**, all distinct exercises.

| Stage | Stretch item | Hours | Stage total |
|---|---|---|---|
| [S0](stage-00-bootstrap.md#14-stretch) | Renovate with pin groups | 1 | |
| | Harness calibration: a stub server with a known latency, coordinated omission with and without latency correction | 1 | |
| | Worldgen properties: a Hypothesis property test over seeds and specs | 1 | 3 |
| [S1](stage-01-layered-monolith.md#14-stretch) | Trigram GIN index for Admin search | 1 | |
| | ROLLUP report over the category tree | 1 | |
| | DRF serializer vs `values()` benchmark | 1 | |
| | COPY vs `bulk_create` vs `executemany` | 1.5 | |
| | Offset-vs-keyset note | 0.5 | |
| | Cycle guards side by side (`CYCLE` vs a `UNION` guard with a depth cap) | 0.5 | |
| | DRF `CursorPagination` vs your keyset | 0.5 | 6 |
| [S2](stage-02-checkout-correctness.md#14-stretch) | The foreign-key lock demo and a lock-mode matrix | 1.5 | |
| | `EXCLUDE` on promo validity windows | 1 | |
| | A stateful test for the fulfillment state machine | 1 | |
| | A "who blocks whom" query | 0.5 | 4 |
| [S3](stage-03-redis-auth-bot.md#14-stretch) | ETag/304 | 1 | |
| | Trending ZSET + HLL viewers | 1 | |
| | Slot reshard under load, MOVED/ASK | 1 | |
| | Sliding-log limiter | 1 | |
| | KEYS vs SCAN stall | 1 | 5 |
| [S4](stage-04-async-events-boundaries.md#14-stretch) | OpenSearch 3.x (only if the judged set fails on Postgres): ICU + transliteration, fuzziness, facets, completion suggester, derived index from `product.changed`, `_bulk` with 429 backoff, reindex with alias swap, wipe-and-rebuild test | 6 | |
| | Quorum-queue priority for password resets | 1 | 7 |
| [S5](stage-05-atlaspay-monolith.md#14-stretch) | Payme Subscribe API card tokens and test-card behaviours in the simulator | 2 | |
| | SetFiscalData | 1 | |
| | A design using Payme `receivers` / Click Split Shop | 1 | |
| | A promo-abuse rule | 1 | |
| | Disputes whiteboard | 1 | 6 |
| [S6](stage-06-ship-and-operate.md#14-stretch) | SLO burn-rate alerts | 1 | |
| | pg_repack demo | 1 | |
| | PG 17→18 upgrade rehearsal via logical replication | 2 | |
| | Find a bug through Sentry first | 1 | 5 |
| [S7](stage-07-polyglot-mongo-timescale.md#14-stretch) | Tree model (`HistGradientBoostingClassifier`) and precision@k | 1.5 | |
| | Calibration curve | 1 | |
| | IsolationForest baseline (P4 lineage) | 1 | |
| | Bucket pattern with pre-aggregated counters | 1 | |
| | Benchmark rows F9 and W4 | 0.5 | 5 |
| [S8](stage-08-ai-integration.md#14-stretch) | Prompt caching (verify cache-read tokens > 0; $ before/after) plus the batch API | 1.5 | |
| | Nightly LLM judge with a $ cap, calibrated on 15 hand-graded answers | 1 | |
| | Re-embedding via a dual column | 1 | |
| | Rerank experiment, only if evals show a gap | 1 | |
| | Checkout-variant A/B at a fixed 50/50 allocation, for Season 2 | 1 | |
| | IVFFlat tuning | 0.5 | 6 |
| [S9](stage-09-strangler-atlaspay-auth.md#14-stretch) | Crypto-shredding beyond atlaspay (event log, Mongo transcripts) | 1 | |
| | Keycloak SSO for Django Admin | 1 | |
| | IP allowlist per key | 0.5 | |
| | A second version transform | 1 | |
| | Webhook resend UI and endpoint | 1 | |
| | Payme `receivers` split | 1.5 | 6 |
| [S10](stage-10-kubernetes-grpc-inventory.md#14-stretch) | Linkerd mTLS | 2 | |
| | Managed Kubernetes via Terraform | 2 | |
| | Native Telegram Payments spike against the testkit fake Bot API (`sendInvoice`, `pre_checkout_query` within 10 s, import `successful_payment` as an external charge and reconcile) | 2 | 6 |
| [S11](stage-11-realtime-edge-graphql.md#14-stretch) | Telegram Mini App `initData` verification | 1 | |
| | Presence and unread badges | 1 | |
| | SSE fallback for the dashboard | 1 | |
| | Offline catch-up UI | 0.5 | |
| | A CDN for the SPA assets | 0.5 | 4 |
| [S12](stage-12-data-at-scale-fraud.md#14-stretch) | Isolate a whale vendor with `isolate_tenant_to_new_shard` | 1 | |
| | Mongo balancer window and a forced jumbo move under writes | 1 | |
| | Blind incident drill (kill `ledger`) | 1 | 3 |
| | | **Total** | **66** |

**Notes on the index:**
- **No duplicates.** The only Redis resharding item is the S3 slot reshard; the S12 slot of that size is now the Mongo balancer-window and jumbo-move exercise, a different lesson.
- **Moved by the re-baseline.** Into the must tier: Google OIDC (S9) and the threads-vs-processes exercise (now the S2 Python concurrency block). Out of the must tier into stretch: the KEYS vs SCAN stall (S3; the lint rule banning `KEYS` stays must), the tree model and precision@k (S7), "find a bug through Sentry first" (S6), crypto-shredding beyond atlaspay (S9), the S1 cycle-guard and `CursorPagination` comparisons, and the S2 foreign-key lock demo. S6 also lists `auto_explain` sampling and Nginx microcaching with no budgeted hours; they are not counted here.
- **Conditional:** the S4 OpenSearch item exists only if the Postgres judged set fails (ADR-016). If it never enters, the season's stretch is 60 h.
- **Season 2 dependency:** the S8 checkout-variant A/B feeds Season 2's 2B analysis. If you skip it, 2B generates the variant as a worldgen cohort instead ([season-2.md §2](season-2.md#2-entry-conditions-what-season-1-must-have-left-behind)).
- **If you have spare hours and must choose**, take the native Telegram Payments spike first (S10: it runs fully against the fake Bot API, needs no provider token, and the 10-second `pre_checkout_query` deadline is a common aiogram interview topic). After that, prefer items that produce an interview story with a number: SLO burn-rate alerts (S6), the calibration curve (S7), prompt caching with $ before/after (S8), the PG 17→18 upgrade rehearsal (S6), the blind incident drill (S12).

---

## 11. Playbooks

### If you are ahead

1. Close the stage properly first: evidence, ADRs, postmortem, STAR stories, tag. Early finish is often a sign that one of these was skipped.
2. Pick stretch items from the current stage (section 10), preferring the ones in the "if you have spare hours" note.
3. Do not pull the next stage forward. Its pain-first exercises depend on the previous stage's state; starting them half-ready removes the lesson.

### If you are behind between checkpoints

1. Stop all stretch immediately.
2. Close the current block at "works and tested", not "polished".
3. If you are in S1–S4, apply that stage's degrade item now (items 5, 11, 14, 16); once the work is finished there is nothing left for it to save.
4. Use the optional fourth weekday session for two weeks rather than lengthening the weekend block.
5. Never cut a spine item to save time; move the date instead.
