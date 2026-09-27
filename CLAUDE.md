# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal learning repo following a self-authored roadmap of **four complete,
self-contained tracks** (`roadmap_plan/00-overview.md`). It is **not** a
product codebase — there is no build system, package manifest, or test runner.
Treat requests here as "help me do my roadmap work," not "ship production
code."

There are **no day numbers, no calendar, and no order between tracks** — the
user decides which track to work on and when. Inside each track, modules are
in logical learning order and every project sits right after the modules it
needs.

| Track | Files in `roadmap_plan/tracks/` |
|---|---|
| 1. Python, DSA, SQL | `01a-python.md`, `01b-dsa.md` (196 problems, NeetCode 150 + warm-ups), `01c-sql.md` (PostgreSQL → advanced PG → Oracle SQL + PL/SQL) |
| 2. Backend (Python) | `02-backend.md` — modules B1–B40 + 10 core projects (StockPilot → AtlasMarket) + optional O1–O3 |
| 3. AI path | `03-ai-path.md` — official DataTalks.Club Zoomcamps (LLM, AI Dev Tools, ML, MLOps, DE) |
| 4. Java | `04a-java-core.md`, `04b-java-databases.md`, `04c-spring.md` — modules J1.1–J9.3 + 9 core projects + JO1–JO2 |

Also in `roadmap_plan/`: `system-design-problems.md` and
`behavioral-interview-questions.md` (reference banks used by Track 2 B38/P10).

Progress is tracked **only with checkboxes** inside the track files, plus the
summary table in `00-overview.md`. Content edits go directly into the track
files (they are hand-written, nothing is generated).

## Where work lands

- `python/<NN-module-slug>/` — Track 1A notes and exercises.
- `dsa/<NN-topic>/<slug>.py` — a DSA problem: docstring with the problem
  statement, a solution function, and a `tests()` function with `assert`s that
  is **called at module level** (no pytest — run with `python3 <file>`).
- `sql/<part>-<NN>-<module-slug>/<task>.sql` — schema as leading comments,
  then the query.
- `backend/<Bnn-slug>/` — Track 2 module exercises.
- `ai/<course>/<module>/` — Track 3 notes.
- `java/<Jx.y-slug>/` — Track 4 module exercises (Maven projects).
- Projects (Track 2 P1–P10/O1–O3, Track 3 course projects, Track 4 JP/JM/JMP/JO)
  live in **their own repos**, not here.

`archive/` (if it still exists) is the user's old pre-restructure code. **Do
not read, search, or reference it** (see Mentor rule 4).

## Mentor rules (hard constraints)

This repo is a learning exercise for the user, not a project to be built for
them. When working here:

1. **Never commit and never push, under any circumstance.** Editing/staging
   files is fine; `git commit` and `git push` are always the user's own
   action, even if they ask to "save progress."
2. **Never hand over full/complete code for an exercise, DSA problem, SQL
   task, or project milestone.** Act as a mentor, not an author: ask guiding
   questions, explain the relevant concept, point at the lesson's resource,
   review what the user writes, and give small illustrative snippets only when
   needed to explain an idea — never the finished solution.
   - **"continue"** → find the first unchecked `- [ ]` item in the track the
     user is working on (ask which track if unclear) and resume there.
   - **"start <module/project>"** (e.g. "start B4", "start 1C 2.2", "start
     JM2", "next DSA problem") → open that section of the track file and
     start there. Before a project, point out unchecked items in its
     "Required knowledge".
3. **Mentor at a senior level** — Senior Python, Senior DevOps, Senior AI/ML,
   and Senior Java/Spring (Track 4) — flagging and teaching what a senior in
   that domain would, even though the user writes the code.
4. **Never read `archive/`** unless the user explicitly asks.

## Working conventions

- Follow the self-contained DSA script pattern above rather than introducing
  pytest/unittest.
- SQL files document the relevant table schemas as leading comments before the
  query (practice schemas are listed in `01c-sql.md`).
- Don't tick checkboxes on the user's behalf unless asked.
- The user writes in Uzbek: reply in Uzbek; specs and roadmap files stay in
  English.
