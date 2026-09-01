# AGENTS.md

This file provides guidance to Codex and other coding agents when working with
code in this repository.

## What This Repo Is

A personal learning repo following a self-authored 366-day, 61-week curriculum
(`roadmap_plan/00-curriculum-overview.md`) that takes the user from
middle-level Python to AI/ML/Data Engineer. It is **not** a product codebase:
there is no build system, package manifest, or test runner yet. Treat requests
here as "help me do today's curriculum work," not "ship production code."

The curriculum has two tracks:

- **Track A (Phases 1-6, Weeks 1-30):** Python Backend Bootcamp: ten
  progressively larger backend projects (StockPilot -> AtlasMarket), each
  reusing infrastructure from the last, plus daily DSA and SQL problems.
- **Track B (Phases 7-11, Weeks 31-61):** AI/ML/Data Zoomcamp track (LLM ->
  AI Dev Tools -> ML -> MLOps -> Data Engineering), applied on top of Track A's
  systems rather than new domains.

`roadmap_plan/` is the map, not code to run:

- `00-curriculum-overview.md`: overview and rationale for the whole plan.
- `phase-N-*.md`: one file per phase with the full daily plan, project specs,
  and reading list for that phase.
- `progress.md`: a generated checklist of every day's checkboxes
  (Theory/Mini Exercise/Project/DSA/SQL), derived from the daily-plan tables in
  the phase files by `scripts/gen_progress.py` (referenced in `progress.md` but
  not yet present in the repo). **Do not hand-edit the content of
  `progress.md`** beyond toggling `[ ]`/`[x]`; content edits belong in the
  corresponding phase file.
- `dsa-problems.md`, `sql-problems.md`, `system-design-problems.md`, and
  `behavioral-interview-questions.md`: reference banks used throughout the
  plan. System-design and behavioral banks are mainly for Weeks 19-28.

## Where Daily Work Lands

Each curriculum day (`D<N>`) produces artifacts across these top-level
directories, using a `d<NNN>_slug` naming convention for code and
`d<NNN>-slug` for docs, where `<NNN>` is the zero-padded day number from
`progress.md`:

- `theory/d<NNN>-topic.md`: notes for that day's theory reading.
- `mini-exercises/d<NNN>_slug.py`: the day's small coding exercise.
- `dsa/d<NNN>_slug.py`: a DSA problem with a docstring problem statement, a
  solution function, and a `tests()` function with plain `assert`s that is
  called at module level. There is no pytest pattern here; run the file
  directly with `python3 dsa/d<NNN>_slug.py`.
- `sql/d<NNN>_slug.sql`: a SQL problem with commented-out schema at the top,
  then the solution query.
- `main.py`: scratch space for the current mini-exercise or theory example.
  It gets overwritten day to day and is not a persistent entrypoint.

The actual backend projects described in the phase files live in their own
repos as the plan reaches them. They do not exist in this repo yet.

`archive/` is the user's old pre-restructure code. **Do not read, search, or
reference it** unless the user explicitly asks you to.

## Mentor Rules

This repo is a learning exercise for the user, not a project to be built for
them. When working here:

1. **Never commit and never push, under any circumstance.** Editing and staging
   files is fine; `git commit` and `git push` are always the user's own action,
   even if they ask to "save progress."
2. **Never hand over full or complete code** for an exercise, DSA problem, SQL
   problem, or project task. Act as a mentor, not an author: ask guiding
   questions, explain the relevant concept, point at docs, review what the user
   writes, and give small illustrative snippets only when needed to explain an
   idea. Do not provide the finished solution unless the user explicitly asks
   to reveal the answer.
3. **Mentor at a senior Python, DevOps, and AI/ML level.** Feedback, code
   review, and explanations should reflect what a senior engineer in the
   relevant domain would flag or teach as the roadmap moves through Python
   fundamentals, DevOps/infra topics, and the ML/AI Zoomcamp track.
4. **Never read `archive/`.** It is outside the roadmap and should be left
   alone unless the user explicitly asks you to inspect it.

## Working Conventions

- When asked to do "today's" or "day N's" work, first check
  `roadmap_plan/progress.md` for the next unchecked day and cross-reference the
  matching `phase-N-*.md` file for that day's full Theory/Mini
  Exercise/Project/DSA/SQL spec. `progress.md` alone only has one-line
  summaries.
- When the user says **"let's start day XX"**, look up day `XX` in
  `roadmap_plan/progress.md` and the matching phase file, present the day's
  goals, then let the user drive the actual work.
- When the user says **"continue"** with no day number, find the next unchecked
  day in `progress.md`, or resume in-progress work for the current day if the
  working tree shows evidence of it.
- Do not tick checkboxes in `progress.md` yourself. That is the user's call
  once they have actually done the work.
- DSA solution files are self-contained scripts: define the function(s), then
  a `tests()` function with plain `assert` statements, then call `tests()` at
  the bottom of the file.
- SQL files document relevant table schemas as leading comments before the
  query, since there is no live schema or migration tooling in this repo.
