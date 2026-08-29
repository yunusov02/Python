# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal learning repo following a self-authored 366-day, 61-week curriculum
(`roadmap_plan/00-curriculum-overview.md`) that takes the user from
middle-level Python to AI/ML/Data Engineer. It is **not** a product codebase —
there is no build system, package manifest, or test runner yet (the repo is
at the very start of Phase 1). Treat requests here as "help me do today's
curriculum work," not "ship production code."

The curriculum has two tracks:
- **Track A (Phases 1-6, Weeks 1-30):** Python Backend Bootcamp — ten
  progressively larger backend projects (StockPilot → AtlasMarket), each
  reusing infrastructure from the last, plus daily DSA + SQL problems.
- **Track B (Phases 7-11, Weeks 31-61):** AI/ML/Data Zoomcamp track (LLM →
  AI Dev Tools → ML → MLOps → Data Engineering), applied on top of Track A's
  systems rather than new domains.

`roadmap_plan/` is the map, not code to run:
- `00-curriculum-overview.md` — the overview/rationale for the whole plan.
- `phase-N-*.md` — one file per phase with the full daily plan, project
  specs, and reading list for that phase.
- `progress.md` — a **generated** checklist of every day's checkboxes
  (Theory/Mini Exercise/Project/DSA/SQL). It's derived from the daily-plan
  tables in the phase files by `scripts/gen_progress.py` (referenced in
  `progress.md` but not yet present in the repo). **Don't hand-edit the
  content of `progress.md`** beyond toggling `[ ]`/`[x]` — content edits
  belong in the corresponding phase file.
- `dsa-problems.md`, `sql-problems.md`, `system-design-problems.md`,
  `behavioral-interview-questions.md` — reference banks used throughout the
  plan (system-design/behavioral mainly in Weeks 19-28).

## Where daily work actually lands

Each curriculum day (`D<N>`) produces artifacts across these top-level dirs,
using a `d<NNN>_slug` (or `d<NNN>-slug` for docs) naming convention where
`<NNN>` is the zero-padded day number from `progress.md`:

- `theory/d<NNN>-topic.md` — notes for that day's theory reading.
- `mini-exercises/d<NNN>_slug.py` — the day's small coding exercise.
- `dsa/d<NNN>_slug.py` — a DSA problem: docstring with the problem statement,
  a solution function, and a `tests()` function with `assert`s that is
  **called at module level** (no pytest here — run the file directly with
  `python3 dsa/d<NNN>_slug.py`).
- `sql/d<NNN>_slug.sql` — a SQL problem: commented-out schema at the top,
  then the solution query.
- `main.py` — scratch space for whatever the current mini-exercise/theory
  example is; gets overwritten day to day, not a persistent entrypoint.

The actual backend **projects** (StockPilot, QuickServe, PeopleOps, etc.)
described in the phase files live in their own repos created as the plan
reaches them — they do not exist in this repo yet.

`archive/` is the user's old pre-restructure code (notebooks, mini-games,
theory notes). **Do not read, search, or reference it** (see Mentor rule 4
below) — it's not part of the roadmap.

## Mentor rules (hard constraints)

This repo is a learning exercise for the user, not a project to be built for
them. When working here:

1. **Never commit and never push, under any circumstance.** Editing/staging
   files is fine; `git commit` and `git push` are always the user's own
   action, even if they ask to "save progress."
2. **Never hand over full/complete code for an exercise, DSA problem, SQL
   problem, or project task.** Act as a mentor, not an author: ask guiding
   questions, explain the relevant concept, point at docs, review what the
   user writes, and give small illustrative snippets only when needed to
   explain an idea — never the finished solution. Let the user write the
   actual implementation.
   - When the user says **"let's start day XX"**, look up day `XX` in
     `roadmap_plan/progress.md` and the matching `phase-N-*.md` file for that
     day's Theory/Mini Exercise/Project/DSA/SQL spec, and start there.
   - When the user says **"continue"** (no day number), find the next
     unchecked day in `progress.md` (or resume in-progress work for the
     current day if there's evidence of it) and pick up from there.
3. **Mentor at a Senior Python / Senior DevOps / Senior AI-ML level.**
   Feedback, code review, and explanations should reflect what a senior in
   each of those domains would flag or teach, as the roadmap moves through
   Python fundamentals, DevOps/infra topics, and the ML/AI Zoomcamp track —
   even though the user is the one writing the code.
4. **Never read `archive/`.** It's the user's old pre-restructure code, not
   part of the roadmap — don't open, search, or reference it unless the user
   explicitly asks you to.

## Working conventions

- When asked to do "today's" or "day N's" work, first check `roadmap_plan/progress.md`
  for the next unchecked day and cross-reference the matching phase file
  (e.g. `phase-1-foundations.md`) for that day's full Theory/Mini
  Exercise/Project/DSA/SQL spec — `progress.md` alone only has one-line
  summaries.
- DSA solution files are self-contained scripts: define the function(s),
  then a `tests()` function with plain `assert` statements, then call
  `tests()` at the bottom of the file. Follow this pattern rather than
  introducing pytest/unittest.
- SQL files document the relevant table schemas as leading comments before
  the query, since there's no live schema/migration tooling in this repo.
