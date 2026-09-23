# Projects

Consolidated, build-ready project specifications.

| Folder | What's in it |
|---|---|
| [`atlas/`](atlas/README.md) | **The active plan.** One project, **Atlas** (AtlasMarket marketplace + AtlasPay, a Stripe-like payment operator with Payme/Click), that grows from a Django monolith into 9 services on Kubernetes over Season 1 (34 weeks, backend + AI), then carries Season 2 (DS/ML/MLOps/DE) on the same data. It replaces the ten separate projects below and cites them as theory reading |
| [`python/`](python/) | The **10 Track A projects** (StockPilot → AtlasMarket), kept as **reference**: pulled out of the day-by-day phase plans and presented whole: domain model, API, invariants, architecture, merged build stages, testing, definition of done. Atlas stage files cite them as "P# D##" |
| [`oracle-apex/`](oracle-apex/README.md) | **2 Oracle + APEX projects** — CreditLine (FinTech lending) and PolisHub (insurance policy & claims) — designed to exercise advanced SQL and PL/SQL |

The phase files (`../phase-1-foundations.md` …) stay the reference for theory,
mini-exercises, DSA, SQL and interview questions. These files are the project
track only.

Each Python project's build stages cite the day numbers they were merged from,
so when you get stuck you can open the matching phase file and read only the
theory entry for that day.
