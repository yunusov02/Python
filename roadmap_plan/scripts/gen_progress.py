#!/usr/bin/env python3
"""Regenerate progress.md from the daily-plan tables in phase-*.md.

This makes progress.md a *derived* artifact instead of a hand-maintained
duplicate: edit a phase file's daily plan table, rerun this script, and
progress.md stays in sync automatically. Fixes the two-sources-of-truth
problem where progress.md could silently drift from the phase files.

Usage: python3 scripts/gen_progress.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PHASES = [
    (1, "phase-1-foundations.md", "## Phase 1 — Foundations (Weeks 1-4)", True),
    (2, "phase-2-concurrency-django-caching.md", "## Phase 2 — Concurrency, Django/DRF, Caching (Weeks 5-8)", True),
    (3, "phase-3-distributed-systems.md", "## Phase 3 — Distributed Systems (Weeks 9-13)", True),
    (4, "phase-4-microservices-infra.md", "## Phase 4 — Microservices & Infrastructure (Weeks 14-18)", True),
    (5, "phase-5-scaling-architecture.md", "## Phase 5 — Scaling & Advanced Architecture (Weeks 19-22)", True),
    (6, "phase-6-capstone.md", "## Phase 6 — Senior-Track Capstone (Weeks 23-26)", True),
    (7, "phase-7-llm-zoomcamp.md", "## Phase 7 — LLM Zoomcamp (Weeks 27-32)", False),
    (8, "phase-8-ai-devtools-zoomcamp.md", "## Phase 8 — AI Dev Tools Zoomcamp (Weeks 33-37)", False),
    (9, "phase-9-ml-zoomcamp.md", "## Phase 9 — Machine Learning Zoomcamp (Weeks 38-44)", False),
    (10, "phase-10-mlops-zoomcamp.md", "## Phase 10 — MLOps Engineering Zoomcamp (Weeks 45-50)", False),
    (11, "phase-11-data-engineering-zoomcamp.md", "## Phase 11 — Data Engineering Zoomcamp (Weeks 51-56)", False),
]

WEEK_HEADER_RE = re.compile(r"^## \d+\. Daily Plan — Week (\d+): (.*)$")
DAY_CELL_RE = re.compile(r"\**(\w+) \(D(\d+)\)\**")

HEADER = """# Roadmap Progress Tracker

Check off each item as you finish it. **336 days total across 56 weeks / 11 phases** (~12-13 months), split into two tracks:

- **Phases 1-6 (Weeks 1-26, D1-D156) — Python Backend Bootcamp.** Every day has 5 independent checkboxes — Theory, Mini Exercise, Project, DSA, SQL.
- **Phases 7-11 (Weeks 27-56, D157-D336) — AI/ML/Data Zoomcamp Track** (LLM Zoomcamp → AI Dev Tools Zoomcamp → ML Zoomcamp → MLOps Zoomcamp → Data Engineering Zoomcamp). DSA/SQL grind is deliberately dropped here (already covered in Phases 1-6) — every day has 3 independent checkboxes: Theory, Mini Exercise, Project.

Order rationale for the Zoomcamp track: LLM Zoomcamp comes first because it's the most directly transferable skill for a backend engineer (you're wrapping API calls into services, not training models) — a low-friction on-ramp right after 6 months of backend work. AI Dev Tools follows immediately since it builds on LLM's agent/tool-calling fundamentals. Then ML Zoomcamp shifts into more theory/math-heavy classical ML, with MLOps following directly since it's literally productionizing the models just built. Data Engineering closes the program as a capstone unifying data from every system built across the year.

> **Generated file — do not hand-edit.** This is derived from the daily-plan
> tables in `phase-1-foundations.md` … `phase-11-data-engineering-zoomcamp.md`
> by `scripts/gen_progress.py`. To change a day's content, edit the phase
> file and rerun the generator. Checkbox state (`[ ]`/`[x]`) is preserved
> across runs.

---
"""

FOOTER = """

**PROGRAM COMPLETE — 336 days, 56 weeks, 11 phases, 25 projects. Tag `v2.0-year-plan-complete`.**
"""


def split_row(line: str) -> list[str]:
    line = line.strip()
    assert line.startswith("|") and line.endswith("|"), line
    cells = line[1:-1].split("|")
    return [c.strip() for c in cells]


def parse_phase_file(path: Path, has_dsa_sql: bool):
    text = path.read_text().splitlines()
    weeks = []  # list of (week_num, title, [day_blocks])
    i = 0
    n = len(text)
    while i < n:
        m = WEEK_HEADER_RE.match(text[i])
        if not m:
            i += 1
            continue
        week_num, title = int(m.group(1)), m.group(2).strip()

        def is_header_row(line: str) -> bool:
            # tolerate column-aligned padding (e.g. from an external
            # markdown formatter) — match on content, not literal spacing
            stripped = line.strip()
            return stripped.startswith("|") and stripped.endswith("|") and split_row(stripped)[0] == "Day"

        # find the table: the header row starting a "| Day | ... |" table
        j = i + 1
        while j < n and not is_header_row(text[j]):
            if WEEK_HEADER_RE.match(text[j]):
                break
            j += 1
        if j >= n or not is_header_row(text[j]):
            i += 1
            continue
        header_cells = split_row(text[j])
        j += 2  # skip header + separator row
        days = []
        while j < n and text[j].startswith("|"):
            cells = split_row(text[j])
            row = dict(zip(header_cells, cells))
            day_cell = row["Day"]
            dm = DAY_CELL_RE.search(day_cell)
            if not dm:
                j += 1
                continue
            weekday, daynum = dm.group(1), int(dm.group(2))
            topics = row.get("Topics", "").strip()
            reading = row.get("Reading", "").strip()
            mini = row.get("Mini Exercise", "").strip()
            project = row.get("Project Task", row.get("StockPilot Task", "")).strip()
            dsa = row.get("DSA Problem", "").strip()
            sql = row.get("SQL Problem", "").strip()

            if reading and reading != "—":
                theory = f"{topics} — *{reading}*"
            else:
                theory = topics

            days.append({
                "daynum": daynum,
                "weekday": weekday,
                "theory": theory,
                "mini": mini if mini else "—",
                "project": project if project else "—",
                "dsa": dsa,
                "sql": sql,
            })
            j += 1
        weeks.append((week_num, title, days))
        i = j
    return weeks


def parse_existing_checkstate(path: Path) -> dict:
    """Map (daynum, field) -> True if previously checked, so regeneration
    doesn't wipe out progress the user has already ticked off."""
    state = {}
    if not path.exists():
        return state
    cur_day = None
    field_re = re.compile(r"^- \[(x| )\] (Theory|Mini Exercise|Project|DSA|SQL):")
    for line in path.read_text().splitlines():
        dm = DAY_CELL_RE.search(line)
        if dm and line.startswith("**D"):
            cur_day = int(dm.group(2))
            continue
        fm = field_re.match(line.strip())
        if fm and cur_day is not None:
            checked = fm.group(1) == "x"
            state[(cur_day, fm.group(2))] = checked
    return state


def render_day(day: dict, has_dsa_sql: bool, checkstate: dict) -> str:
    def box(field: str) -> str:
        return "x" if checkstate.get((day["daynum"], field)) else " "

    lines = [f"**D{day['daynum']} ({day['weekday']})**"]
    lines.append(f"- [{box('Theory')}] Theory: {day['theory']}")
    lines.append(f"- [{box('Mini Exercise')}] Mini Exercise: {day['mini']}")
    lines.append(f"- [{box('Project')}] Project: {day['project']}")
    if has_dsa_sql:
        lines.append(f"- [{box('DSA')}] DSA: {day['dsa']}")
        lines.append(f"- [{box('SQL')}] SQL: {day['sql']}")
    return "\n".join(lines)


def render_phase(header_line: str, weeks: list, has_dsa_sql: bool, checkstate: dict) -> str:
    parts = [header_line, ""]
    for week_num, title, days in weeks:
        parts.append(f"### Week {week_num} — {title}")
        parts.append("")
        for day in days:
            parts.append(render_day(day, has_dsa_sql, checkstate))
            parts.append("")
    out = "\n".join(parts)
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out.rstrip("\n")


def main():
    out_path = ROOT / "progress.md"
    checkstate = parse_existing_checkstate(out_path)
    chunks = [HEADER.rstrip("\n")]
    total_days = 0
    for num, fname, header_line, has_dsa_sql in PHASES:
        path = ROOT / fname
        weeks = parse_phase_file(path, has_dsa_sql)
        day_count = sum(len(d) for _, _, d in weeks)
        total_days += day_count
        chunks.append(render_phase(header_line, weeks, has_dsa_sql, checkstate))
        chunks.append("---")
    body = "\n\n".join(chunks)
    body += FOOTER
    out_path.write_text(body)
    print(f"Wrote {out_path} — {total_days} days parsed across {len(PHASES)} phases", file=sys.stderr)


if __name__ == "__main__":
    main()
