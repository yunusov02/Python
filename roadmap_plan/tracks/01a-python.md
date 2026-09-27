# Track 1A — Python (Advanced Language + Tooling)

> Part of **Track 1 — Python, DSA, SQL**. Siblings: [`01b-dsa.md`](01b-dsa.md), [`01c-sql.md`](01c-sql.md).
> Overview: [`../00-overview.md`](../00-overview.md)

## Intro

**Goal.** Take solid Python fundamentals to a professional level: understand
*how* the language works (closures, the object model, memory management,
iterators, descriptors, the GIL, the event loop) and master the everyday
tooling a Middle+/Senior Python engineer is expected to use without thinking
(Git, virtual envs, `pyproject.toml`, pytest, mypy, ruff, packaging).

**Required knowledge.** Python fundamentals (syntax, functions, classes,
modules, exceptions, standard collections). Nothing from other tracks.

**Total estimated time: ~95 hours** (12 modules).

**Order.** Modules are in a logical learning order. 1A.1 first (your tools),
then 1A.2–1A.7 (the language), then 1A.8–1A.10 (tooling), then 1A.11–1A.12
(concurrency). 1A.8 (pytest) can be pulled earlier if you want tests for your
exercises from day one.

## How to use this file

- Every lesson, exercise and checklist item has a checkbox. Tick `[x]` when done.
- **No solutions anywhere.** You write every line of exercise code yourself.
  Your mentor (Claude) explains concepts, asks guiding questions and reviews
  your code — it does not hand over finished implementations.
- A lesson is "done" when you have read the resource **and** written short notes
  in your own words.
- An exercise is "done" when it runs, meets the acceptance criteria, and you can
  explain every line out loud.
- Self-check questions: answer out loud (or in writing) *before* opening the
  Answers section.

## Where your work goes

```
python/
  01-git-and-env/
    notes.md
    ex_<slug>.py
  02-functions-closures-decorators/
    notes.md
    ex_timer.py
    ...
```

- One folder per module: `python/<NN-module-slug>/`.
- Notes: `notes.md`. Exercises: `ex_<slug>.py` (small, self-contained, runnable
  with `python3 ex_<slug>.py`; from module 1A.8 onward add a `test_<slug>.py`).

---

## Module 1A.1 — Git Workflow & Development Environment

**Estimated time: 8 h**

### Topics
- Git internals at a useful level: blobs, trees, commits, refs, `HEAD`, the index (staging area)
- Branching, merging (fast-forward vs three-way), rebase, interactive rebase *concepts*, cherry-pick
- Resolving conflicts; `git log --graph`, `git diff --staged`, `git restore`, `git reset` (soft/mixed/hard), `git reflog`
- Workflow: feature branches, small commits, Conventional Commits, pull requests, code review etiquette
- `.gitignore`, never committing secrets; tags and releases
- Virtual environments: `venv`, why global installs are a trap, `pip` vs `uv`
- `pyproject.toml` as the single project config (PEP 518/621): `[project]`, dependencies, optional-dependencies, `[tool.*]` sections
- Lock files and reproducible installs (`uv.lock`, `requirements.txt` pinned output)

### Theory resources
- *Pro Git* (git-scm.com/book), Ch. 2 "Git Basics", Ch. 3 "Git Branching" (all of 3.1–3.6), Ch. 7.7 "Reset Demystified", Ch. 10.1–10.3 "Git Internals" (Plumbing and Porcelain, Git Objects, Git References)
- Conventional Commits spec — conventionalcommits.org
- Python docs — `venv` module (docs.python.org/3/library/venv.html)
- Python Packaging User Guide (packaging.python.org) — "Writing your pyproject.toml"
- uv docs (docs.astral.sh/uv) — "Getting started", "Concepts → Projects"

### Lessons
- [ ] Lesson 1.1 — Git object model, the index, commits and refs (*Pro Git* 2, 10.1–10.3)
- [ ] Lesson 1.2 — Branching, merging and rebasing (*Pro Git* 3.1–3.6)
- [ ] Lesson 1.3 — Undoing things safely: `restore`, `reset`, `revert`, `reflog` (*Pro Git* 7.7)
- [ ] Lesson 1.4 — Team workflow: feature branches, PRs, Conventional Commits, review
- [ ] Lesson 1.5 — Virtual environments, `pip` vs `uv`, lock files
- [ ] Lesson 1.6 — `pyproject.toml` anatomy

### Exercises
- [ ] Ex 1.1 — **Git object tour.** In a throwaway repo, make 3 commits, then use only plumbing commands (`git cat-file -t/-p`, `git rev-parse`) to walk from `HEAD` to a blob. Record every hash and type in `notes.md`. Acceptance: you can draw the commit → tree → blob graph from your notes.
- [ ] Ex 1.2 — **Conflict drill.** Create two branches that edit the same line differently; merge one into the other, resolve the conflict by hand, then repeat the scenario with `rebase` instead of `merge`. Acceptance: `notes.md` explains how the resulting histories differ (`git log --graph --oneline`).
- [ ] Ex 1.3 — **Recover the "lost" commit.** Make a commit, `git reset --hard HEAD~1`, then get the commit back using `reflog`. Acceptance: you can explain why the commit was never actually deleted.
- [ ] Ex 1.4 — **Project skeleton.** Create a new project with `uv init` (or `python -m venv` + `pip`), a `pyproject.toml` declaring one runtime dependency, one dev-only dependency group, and a `[tool.ruff]` section. Acceptance: deleting `.venv` and running one command restores an identical environment.
- [ ] Ex 1.5 — **.gitignore audit.** Write a `.gitignore` for a Python project (venv, caches, `.env`, IDE folders, build artefacts). Acceptance: `git status` stays clean after running your code, tests and a build.

### Must be able to do / explain
- [ ] Explain what a commit actually stores and what a branch actually is
- [ ] Choose merge vs rebase for a given situation and justify it
- [ ] Undo any local mistake without losing work (`reflog`)
- [ ] Explain why every project gets its own virtual environment
- [ ] Read and write a `pyproject.toml` from memory

### Self-check interview questions
1. What is the difference between `git merge` and `git rebase`? When is rebasing dangerous?
2. What does `git reset --soft`, `--mixed` and `--hard` each change?
3. What is the staging area for?
4. How do you recover a commit after a bad `reset --hard`?
5. Why use a virtual environment instead of installing packages globally?
6. What problem do lock files solve that a list of dependency names does not?
7. What belongs in `pyproject.toml`?

---

**Answers**
1. Merge joins two histories with a merge commit (or a fast-forward) and keeps history as it really happened. Rebase replays your commits on top of another base and rewrites their hashes, which gives a linear history. Rebasing is dangerous on branches other people have already pulled, because it rewrites commits they already have.
2. `--soft` moves only the branch pointer; the index and working tree are untouched. `--mixed` (the default) also resets the index, so your changes become unstaged. `--hard` also resets the working tree, so uncommitted changes are lost.
3. It lets you build the next commit precisely — stage only part of your changes and keep commits small and focused.
4. `git reflog` shows everywhere `HEAD` has pointed. Find the old hash, then `git reset --hard <hash>` or `git branch rescue <hash>`. Commits stay in the object store until garbage collection runs.
5. Isolation: each project gets its own dependency versions, nothing conflicts across projects, the setup is reproducible, and you never break the system Python.
6. Reproducibility. A lock file pins exact versions, including transitive dependencies (and usually hashes), so every machine and CI run installs the same thing.
7. Build-system requirements, project metadata (name, version, Python version), dependencies and optional dependency groups, entry points, and tool configuration (`[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`).

---

## Module 1A.2 — Functions, Closures & Decorators

**Estimated time: 8 h**

### Topics
- Functions as first-class objects; higher-order functions
- Scope rules (LEGB), `global` vs `nonlocal`, closures and free variables (`__closure__`, cell objects)
- Decorators: syntax sugar, decoration time vs call time
- `functools.wraps` and why metadata matters
- Decorators with arguments (decorator factories — three levels of nesting)
- Class-based decorators (`__call__`), decorators that keep state
- Stacking order; decorating methods
- Standard-library decorators: `functools.cache`, `lru_cache`, `singledispatch`, `cached_property`

### Theory resources
- *Fluent Python* 2nd ed., Ch. 7 "Functions as First-Class Objects"
- *Fluent Python* 2nd ed., Ch. 9 "Decorators and Closures" (all sections, including "Parameterized Decorators")
- Python docs — `functools` module (docs.python.org/3/library/functools.html): `wraps`, `cache`, `lru_cache`, `singledispatch`, `cached_property`
- Python docs — Language Reference, "Execution model → Naming and binding"

### Lessons
- [ ] Lesson 2.1 — Functions as objects, scope rules, closures
- [ ] Lesson 2.2 — Decorators with arguments, `functools.wraps`
- [ ] Lesson 2.3 — Class-based decorators and stacking order
- [ ] Lesson 2.4 — Standard-library decorators: `cache`/`lru_cache`, `singledispatch`, `cached_property`

### Exercises
- [ ] Ex 2.1 — **`@timer`.** Decorator that prints (or logs) a function's wall-clock run time. Acceptance: the decorated function keeps its `__name__` and docstring, and its return value is passed through unchanged.
- [ ] Ex 2.2 — **`@retry(times=3)`.** Decorator factory that retries a failing call up to `times` times. Acceptance: it re-raises the last exception after the final attempt, and a function that succeeds on attempt 2 is called exactly twice.
- [ ] Ex 2.3 — **Stacking.** Combine `@timer` and `@retry`, in both orders. Acceptance: `notes.md` explains why one order times each attempt and the other times the whole retry loop.
- [ ] Ex 2.4 — **Retry v2 (from memory, no notes).** Extend `@retry` with `exceptions=(...)` (only retry these), `backoff` (exponential delay with jitter) and an `on_retry` callback. Acceptance: non-listed exceptions propagate immediately; the delays are observable in logs.
- [ ] Ex 2.5 — **Class-based `@count_calls`.** A stateful decorator class exposing `.calls` on the wrapped function. Acceptance: it works on plain functions **and** on instance methods (think about the descriptor protocol — you will meet it again in 1A.6).
- [ ] Ex 2.6 — **`@ttl_cache(seconds=...)`.** Memoizing decorator whose entries expire. Acceptance: arguments must be hashable (raise a clear error otherwise); after expiry the function is called again; compare with `functools.lru_cache` in `notes.md`.

### Must be able to do / explain
- [ ] Explain what a closure captures and where it is stored (`__closure__`)
- [ ] Write a decorator with and without arguments from memory
- [ ] Explain why `functools.wraps` matters (introspection, debugging, stacked decorators)
- [ ] Explain decoration time vs call time and predict the order of print statements in stacked decorators
- [ ] Pick the right stdlib decorator instead of writing one

### Self-check interview questions
1. What is a closure? Give a real use case.
2. Why do you need `nonlocal`? What error do you get without it?
3. When does a decorator's body run?
4. What does `functools.wraps` copy, and what breaks without it?
5. How does a decorator with arguments work structurally?
6. In `@a @b def f`, which decorator is applied first, and which wrapper runs first at call time?
7. Why is decorating a method with a class-based decorator tricky?
8. What is the difference between `lru_cache` and `cache`? What are the risks of caching?

---

**Answers**
1. A closure is a function that keeps references to variables from its enclosing scope after that scope has returned. Use cases: decorators, callback factories, simple counters or configuration captured once.
2. Assigning to a name inside a function makes it local by default. Without `nonlocal`, `count += 1` on an enclosing variable raises `UnboundLocalError`.
3. At definition time, i.e. when the module is imported. The wrapper runs at call time.
4. It copies `__name__`, `__qualname__`, `__doc__`, `__module__` and `__annotations__`, updates `__dict__`, and sets `__wrapped__`. Without it, logs, tracebacks, docs, pytest output and `inspect.signature` all show the wrapper instead of the real function.
5. It is a function that returns a decorator (factory → decorator → wrapper). `@retry(3)` first calls `retry(3)`, and the returned decorator is then applied to the function.
6. `b` is applied first because it is closest to the function; `a` wraps the result. At call time `a`'s wrapper runs first (outermost).
7. A class instance used as a decorator is not a function, so it does not bind `self` automatically — plain functions do because they are descriptors (`__get__`). You need to implement `__get__` or use a function-based decorator.
8. `cache` is `lru_cache(maxsize=None)`: unbounded, no eviction. Risks: memory growth, stale data, arguments must be hashable, and caching methods keeps `self` alive (a leak).

---

## Module 1A.3 — Memory Model: Reference Counting, GC, weakref

**Estimated time: 5 h**

### Topics
- Names vs objects; identity (`is`, `id`) vs equality (`==`)
- Mutable vs immutable; aliasing; shallow vs deep copy
- Reference counting in CPython; `sys.getrefcount` and its off-by-one
- Reference cycles; the generational cyclic garbage collector (`gc` module, generations, thresholds)
- `__del__` pitfalls
- `weakref`: `ref`, `WeakValueDictionary`, `WeakKeyDictionary`, `finalize`
- Finding memory problems: `tracemalloc`, `gc.get_referrers`
- Small-integer caching and string interning (and why you never rely on them)

### Theory resources
- *Fluent Python* 2nd ed., Ch. 6 "Object References, Mutability, and Recycling" (all sections, incl. "del and Garbage Collection", "Tricks Python Plays with Immutables")
- Python docs — `gc` module (docs.python.org/3/library/gc.html)
- Python docs — `weakref` module (docs.python.org/3/library/weakref.html)
- Python docs — `tracemalloc` module
- Python docs — `copy` module

### Lessons
- [ ] Lesson 3.1 — Reference counting basics (*Fluent Python* Ch. 6)
- [ ] Lesson 3.2 — Reference cycles and the `gc` module
- [ ] Lesson 3.3 — `weakref` and caches that don't leak
- [ ] Lesson 3.4 — Copies, aliasing, and hunting leaks with `tracemalloc`

### Exercises
- [ ] Ex 3.1 — **`sys.getrefcount` experiment.** Script showing how the count changes when you assign, pass to a function, put in a list, and `del`. Acceptance: you can explain the "+1" that `getrefcount` itself adds.
- [ ] Ex 3.2 — **Create and detect a reference cycle.** Build two objects that reference each other, drop all external references, and prove with `gc` that they are only freed by the cyclic collector. Acceptance: `gc.collect()` return value / `gc.DEBUG_*` output shown in your notes.
- [ ] Ex 3.3 — **Weak cache.** A registry of expensive objects built on `weakref.WeakValueDictionary`. Acceptance: once the last strong reference goes away, the entry disappears from the registry; `weakref.finalize` logs the cleanup.
- [ ] Ex 3.4 — **Leak hunt.** Write a small program that leaks on purpose (e.g. an unbounded module-level list, or `lru_cache` on a method). Use `tracemalloc` snapshots to find the leaking line. Acceptance: `notes.md` shows the top-10 diff and your explanation.
- [ ] Ex 3.5 — **Copy semantics.** Demonstrate a bug caused by a shallow copy of nested lists and a bug caused by a mutable default argument; fix both. Acceptance: tests or asserts prove the bug and the fix.

### Must be able to do / explain
- [ ] Explain how CPython decides an object can be freed
- [ ] Explain why reference cycles need a separate collector
- [ ] Explain when to use `weakref` and give a real example
- [ ] Find a memory leak with `tracemalloc`
- [ ] Explain the mutable-default-argument bug

### Self-check interview questions
1. How does CPython manage memory?
2. What is a reference cycle, and how is it collected?
3. Why is `__del__` risky?
4. What is a weak reference? Give a use case.
5. `a is b` vs `a == b`?
6. Why is `def f(x=[])` a bug?
7. Why does `sys.getrefcount(x)` return one more than you expect?

---

**Answers**
1. Primarily reference counting: an object is freed immediately when its count drops to 0. A generational cyclic GC handles cycles. Small objects come from the pymalloc allocator.
2. Objects that reference each other (directly or indirectly), so their counts never reach 0. The cyclic GC periodically finds unreachable groups of container objects and frees them; it runs by generation, based on allocation thresholds.
3. It runs at a non-deterministic time (or not at all at interpreter shutdown). Exceptions inside it are ignored, it can resurrect objects, and it complicates cycle collection. Prefer context managers or `weakref.finalize`.
4. A reference that doesn't increase the refcount, so it doesn't keep the object alive. Use cases: caches and registries, observer lists, parent back-pointers in trees.
5. `is` compares identity (same object); `==` compares values via `__eq__`. Use `is` only for singletons such as `None`.
6. The default is evaluated once, at definition time, so all calls share the same list. Use `None` and create the list inside the function.
7. Passing `x` as an argument creates a temporary extra reference for the duration of the call.

---

## Module 1A.4 — Iterators & Generators

**Estimated time: 8 h**

### Topics
- Iterable vs iterator; the iterator protocol (`__iter__`, `__next__`, `StopIteration`)
- How `for` works under the hood; `iter()` with a sentinel
- Generator functions, `yield`, generator objects and their state
- Generator expressions; lazy evaluation and memory behaviour
- `yield from` and delegating generators
- `itertools` essentials: `islice`, `chain`, `groupby`, `tee`, `accumulate`, `batched` (3.12+)
- Generator-based pipelines (processing huge files in constant memory)
- `send()`, `throw()`, `close()` — classic coroutines (just enough to understand where `async` came from)

### Theory resources
- *Fluent Python* 2nd ed., Ch. 17 "Iterators, Generators, and Classic Coroutines" (§ "A Sequence of Words" → "Generator Expressions", then "An Arithmetic Progression Generator", "Generator Functions in the Standard Library", "Subgenerators with yield from", "Classic Coroutines")
- Python docs — Glossary: "iterable", "iterator", "generator"
- Python docs — `itertools` module (recipes section too)

### Lessons
- [ ] Lesson 4.1 — Iterator protocol (*Fluent Python* Ch. 17, first half)
- [ ] Lesson 4.2 — Generator functions and `yield`
- [ ] Lesson 4.3 — Generator expressions, `yield from`, `itertools`
- [ ] Lesson 4.4 — Classic coroutines: `send`/`throw`/`close` (conceptual bridge to asyncio)

### Exercises
- [ ] Ex 4.1 — **`Countdown` iterator class.** Implement `__iter__`/`__next__` by hand. Acceptance: it works in `for`, `list()`, and a second `iter()` call behaves as you decided (document: iterable vs one-shot iterator).
- [ ] Ex 4.2 — **Lazy CSV reader for 1M rows.** Generate a fake 1M-row product CSV, then write a generator that yields parsed rows. Acceptance: `tracemalloc` peak stays flat (compare with `list(csv.reader(...))`).
- [ ] Ex 4.3 — **Pipeline with `yield from`.** Chain three generators (read → filter → transform) and a fourth that delegates with `yield from`. Acceptance: nothing is read before iteration starts (prove with prints).
- [ ] Ex 4.4 — **`chunked(iterable, n)`.** Yield lists of size `n` (last may be shorter) from any iterable, including infinite ones. Acceptance: works with a generator input; compare with `itertools.batched`.
- [ ] Ex 4.5 — **Running-average coroutine.** Classic coroutine driven with `send()`. Acceptance: priming is handled; `close()` ends it cleanly.

### Must be able to do / explain
- [ ] Explain iterable vs iterator and why a generator can only be consumed once
- [ ] Rewrite a list-building function as a generator and justify the memory win
- [ ] Explain what `yield from` does beyond a `for` loop
- [ ] Use the right `itertools` function instead of hand-written loops

### Self-check interview questions
1. What is the difference between an iterable and an iterator?
2. How does a `for` loop work internally?
3. What happens to local state between `yield`s?
4. List comprehension vs generator expression — when to use each?
5. What does `yield from` add beyond iterating a sub-generator?
6. How would you process a 50 GB log file in Python?
7. What does `itertools.groupby` require from its input?

---

**Answers**
1. An iterable has `__iter__` that returns an iterator. An iterator has `__next__` (and an `__iter__` that returns itself) and is consumed as you go.
2. It calls `iter(obj)`, then calls `next()` repeatedly until `StopIteration` is raised, which it handles silently.
3. The frame (local variables and instruction pointer) is suspended and kept inside the generator object, then resumed on the next `next()`.
4. Use a list comprehension when you need the whole list, random access or several passes. Use a generator expression for single-pass, lazy, large or infinite data.
5. It passes `send`, `throw` and `close` through to the sub-generator and returns the sub-generator's `return` value. It is the foundation that `await` evolved from.
6. Stream it: iterate the file line by line with generators in a pipeline, aggregate as you go, never load it all; parallelize by chunks if needed.
7. Input sorted (or at least grouped) by the key, because it only groups consecutive equal keys.

---

## Module 1A.5 — Context Managers

**Estimated time: 5 h**

### Topics
- The `with` statement; `__enter__` / `__exit__` and its three arguments
- Suppressing vs propagating exceptions (the return value of `__exit__`)
- `contextlib.contextmanager` (generator-based), `closing`, `suppress`, `nullcontext`, `redirect_stdout`
- `ExitStack` for a dynamic number of resources
- Async context managers (`__aenter__`/`__aexit__`, `asynccontextmanager`) — preview for 1A.12
- Real uses: transactions (commit/rollback), locks, temporary state, timing, files and sockets

### Theory resources
- *Fluent Python* 2nd ed., Ch. 18 "with, match, and else Blocks" (§ "Context Managers and with Blocks", "The contextlib Utilities", "Using @contextmanager")
- Python docs — `contextlib` module (docs.python.org/3/library/contextlib.html)
- Python docs — Language Reference, "The with statement"

### Lessons
- [ ] Lesson 5.1 — Context manager protocol (*Fluent Python* Ch. 18)
- [ ] Lesson 5.2 — `@contextmanager` and the `contextlib` toolbox
- [ ] Lesson 5.3 — `ExitStack` and async context managers

### Exercises
- [ ] Ex 5.1 — **Transactional context manager (class).** Wrap a `sqlite3` connection: commit on success, roll back on exception, always close. Acceptance: a test shows partial writes are rolled back when an exception occurs mid-block, and the exception still propagates.
- [ ] Ex 5.2 — **Same thing with `@contextmanager`.** Rewrite Ex 5.1 as a generator-based context manager. Acceptance: identical behaviour; `notes.md` compares the two styles.
- [ ] Ex 5.3 — **Config loader with auto-rollback.** A context manager that temporarily overrides settings (e.g. environment variables) and restores the originals even if the body raises. Acceptance: nesting two overrides works.
- [ ] Ex 5.4 — **`ExitStack` of N files.** Open a variable-length list of files; if opening file k fails, files 0..k-1 must still be closed. Acceptance: prove with a deliberately missing file.

### Must be able to do / explain
- [ ] Explain the three arguments of `__exit__` and what returning `True` does
- [ ] Write a context manager both as a class and with `@contextmanager`
- [ ] Explain why context managers beat `try/finally` scattered across code
- [ ] Know when `ExitStack` is the right tool

### Self-check interview questions
1. What does `__exit__` receive, and what does its return value mean?
2. How does `@contextmanager` turn a generator into a context manager?
3. What happens if the generator in `@contextmanager` doesn't wrap `yield` in `try/finally`?
4. What problem does `ExitStack` solve?
5. Give three real-world uses of context managers in backend code.

---

**Answers**
1. `exc_type`, `exc_value`, `traceback` (all `None` if there was no exception). Returning a truthy value suppresses the exception.
2. Code before `yield` is `__enter__`, the yielded value is bound by `as`, and code after `yield` is `__exit__`. An exception in the body is thrown into the generator at the `yield`.
3. The cleanup code after `yield` doesn't run when the body raises, so the resource leaks.
4. Managing a dynamic, runtime-determined number of context managers, with guaranteed cleanup in reverse order.
5. DB transactions/sessions, locks, temporary files/directories, HTTP client sessions, timing/tracing spans, temporarily patching config.

---

## Module 1A.6 — OOP Internals: Data Model, Dataclasses, Descriptors

**Estimated time: 10 h**

### Topics
- The Python data model: dunder methods (`__repr__`, `__str__`, `__eq__`, `__hash__`, `__lt__`, `__len__`, `__getitem__`, `__contains__`, `__bool__`)
- `__eq__`/`__hash__` contract; hashability of mutable objects
- Properties; `@classmethod` vs `@staticmethod`
- `dataclasses`: `field()`, `default_factory`, `frozen=True`, `order`, `slots=True`, `kw_only`, `__post_init__`
- Value objects (immutable, compared by value)
- Descriptors: `__get__`, `__set__`, `__set_name__`; data vs non-data descriptors; attribute lookup order
- How methods, `property` and `classmethod` are implemented with descriptors
- `__slots__`; MRO and `super()`; mixins; ABCs (`abc.ABC`) vs Protocols (preview for 1A.7)
- Metaclasses and `__init_subclass__` (awareness level)

### Theory resources
- *Fluent Python* 2nd ed., Ch. 1 "The Python Data Model"
- *Fluent Python* 2nd ed., Ch. 5 "Data Class Builders"
- *Fluent Python* 2nd ed., Ch. 11 "A Pythonic Object" and Ch. 14 "Inheritance: For Better or for Worse"
- *Fluent Python* 2nd ed., Ch. 22 "Dynamic Attributes and Properties" and Ch. 23 "Attribute Descriptors"
- Python docs — "Descriptor HowTo Guide" (docs.python.org/3/howto/descriptor.html)
- Python docs — `dataclasses` module

### Lessons
- [ ] Lesson 6.1 — The data model and dunder methods (*Fluent Python* Ch. 1, 11)
- [ ] Lesson 6.2 — Dataclasses and value objects (*Fluent Python* Ch. 5)
- [ ] Lesson 6.3 — Properties and attribute access (*Fluent Python* Ch. 22)
- [ ] Lesson 6.4 — Descriptors: data vs non-data, lookup order (*Fluent Python* Ch. 23, Descriptor HowTo)
- [ ] Lesson 6.5 — Inheritance, MRO, `super()`, mixins, `__slots__` (*Fluent Python* Ch. 14)
- [ ] Lesson 6.6 — `__init_subclass__` and metaclasses (awareness)

### Exercises
- [ ] Ex 6.1 — **`Money` value object.** Frozen dataclass storing integer minor units (cents) plus a currency. Support `+`, `-`, multiply by an int, comparison, and a readable `__repr__`. Acceptance: adding different currencies raises; no floats anywhere; instances are hashable and usable as dict keys.
- [ ] Ex 6.2 — **Sequence-like class.** A `Deck` (or `Playlist`) implementing only `__len__` and `__getitem__`. Acceptance: slicing, iteration, `in`, `reversed()` and `random.choice` all work — explain why.
- [ ] Ex 6.3 — **`PositiveInt` descriptor.** Reusable validating descriptor using `__set_name__`. Acceptance: two classes use it; error messages include the attribute name; class-level access returns the descriptor itself.
- [ ] Ex 6.4 — **Mini ORM field.** A `Model` base class plus `IntegerField`/`StringField(max_length=...)` descriptors; `Model` collects its fields (via `__init_subclass__` or `__set_name__`) and exposes `to_dict()`. Acceptance: invalid assignment raises; field order is preserved.
- [ ] Ex 6.5 — **MRO puzzle.** Build a diamond hierarchy with cooperative `super().__init__` calls. Acceptance: predict the `__mro__` on paper first, then verify.

### Must be able to do / explain
- [ ] Implement the `__eq__`/`__hash__` contract correctly
- [ ] Choose between dataclass, NamedTuple, TypedDict, Pydantic model
- [ ] Explain the attribute lookup order (data descriptor → instance `__dict__` → non-data descriptor → class)
- [ ] Explain how a plain function becomes a bound method
- [ ] Explain what `__slots__` buys and costs

### Self-check interview questions
1. Why should `__hash__` be consistent with `__eq__`? What does a dataclass do by default?
2. What is the difference between a data and a non-data descriptor?
3. How does `property` work under the hood?
4. How does a function become a bound method when accessed through an instance?
5. What does `frozen=True` guarantee, and what doesn't it?
6. What is the MRO, and how does `super()` use it?
7. When would you use `__slots__`?
8. `@classmethod` vs `@staticmethod` — give a real use for each.
9. Why is a value object useful for money?

---

**Answers**
1. Equal objects must have equal hashes, or dicts and sets break. A dataclass with `eq=True` (the default) sets `__hash__ = None` (unhashable) unless `frozen=True` or `unsafe_hash=True`.
2. A data descriptor defines `__set__` or `__delete__` and takes precedence over the instance `__dict__`. A non-data descriptor defines only `__get__`, so an instance attribute shadows it.
3. `property` is a data descriptor whose `__get__`/`__set__`/`__delete__` call the functions you passed in.
4. Functions are non-data descriptors. `instance.method` calls `function.__get__(instance, cls)`, which returns a bound method object that has `self` bound.
5. Assigning attributes after `__init__` raises `FrozenInstanceError`. It is shallow: mutable fields (like a list) can still be mutated, and `object.__setattr__` can bypass it.
6. The C3-linearised order in which classes are searched for attributes. `super()` delegates to the *next* class in the MRO of the instance's type, not simply the parent.
7. For many small instances (memory savings, slightly faster attribute access). The costs: no `__dict__` (no ad-hoc attributes), trickier multiple inheritance, and weakref needs `__weakref__` listed.
8. `classmethod`: alternative constructors (`Money.from_str("12.50 USD")`). `staticmethod`: a helper that belongs in the class's namespace but needs neither `cls` nor `self`.
9. Integer minor units avoid float rounding errors, the currency is part of the value, operations are validated, and immutability means it can be shared and hashed safely.

---

## Module 1A.7 — Type Hints & mypy

**Estimated time: 8 h**

### Topics
- Why type hints: documentation, tooling, catching bugs before runtime; gradual typing
- Built-in generics (`list[int]`, `dict[str, X]`), `Optional`/`X | None`, `Union`, `Literal`, `Final`, `Any` vs `object`
- `TypeVar`, generic functions and classes (PEP 695 syntax `class Stack[T]:` in 3.12+)
- Variance (invariant, covariant, contravariant) — why `list[Dog]` is not `list[Animal]`
- `Protocol` and structural typing vs ABC nominal typing; `runtime_checkable`
- `Callable`, `ParamSpec`, `Concatenate` (typing decorators correctly)
- `TypedDict`, `NamedTuple`, `NewType`, `Self`, `overload`, `TypeGuard`/`TypeIs`
- mypy: configuration in `pyproject.toml`, `--strict`, reading errors, `reveal_type`, stubs (`types-*`), `# type: ignore[code]` discipline

### Theory resources
- *Fluent Python* 2nd ed., Ch. 8 "Type Hints in Functions"
- *Fluent Python* 2nd ed., Ch. 13 "Interfaces, Protocols, and ABCs"
- *Fluent Python* 2nd ed., Ch. 15 "More About Type Hints"
- mypy docs (mypy.readthedocs.io): "Getting started", "Type hints cheat sheet", "Generics", "Protocols and structural subtyping", "The mypy configuration file"
- Python docs — `typing` module

### Lessons
- [ ] Lesson 7.1 — Type hint basics and gradual typing (*Fluent Python* Ch. 8)
- [ ] Lesson 7.2 — Generics, `TypeVar`, variance (*Fluent Python* Ch. 15; mypy "Generics")
- [ ] Lesson 7.3 — `Protocol` and structural typing (*Fluent Python* Ch. 13; mypy "Protocols")
- [ ] Lesson 7.4 — Typing callables and decorators: `Callable`, `ParamSpec`
- [ ] Lesson 7.5 — mypy in practice: config, `--strict`, stubs, ignores

### Exercises
- [ ] Ex 7.1 — **Generic `Stack[T]`.** `push`, `pop`, `peek`, `__len__`, `is_empty`. Acceptance: `mypy --strict` passes; pushing a `str` onto a `Stack[int]` is a mypy error (show it in notes).
- [ ] Ex 7.2 — **`Repository[T]` Protocol.** Define a protocol (`get`, `add`, `list`) and two unrelated implementations (in-memory and a JSON-file one) with **no** inheritance. Acceptance: a function typed to accept `Repository[Product]` accepts both; mypy rejects a class that is missing a method.
- [ ] Ex 7.3 — **Type your decorators.** Add full type hints to your `@timer` and `@retry` using `ParamSpec`/`TypeVar`. Acceptance: `reveal_type` on a decorated function shows the original signature.
- [ ] Ex 7.4 — **Strict-mode migration.** Take one of your earlier untyped exercises and make it pass `mypy --strict`. Acceptance: zero `Any` leaks and zero bare `# type: ignore`; list every fix in notes.
- [ ] Ex 7.5 — **Variance experiment.** Show with mypy why `list[Dog]` can't be passed where `list[Animal]` is expected but `Sequence[Dog]` can. Acceptance: notes explain it in your own words.

### Must be able to do / explain
- [ ] Type a generic function and a generic class
- [ ] Explain Protocol vs ABC and pick one for a given design
- [ ] Type a decorator without losing the signature
- [ ] Configure mypy strictly in `pyproject.toml` and run it in CI
- [ ] Explain variance with the `list` vs `Sequence` example

### Self-check interview questions
1. Do type hints affect runtime? What does?
2. What is the difference between `Any` and `object`?
3. Protocol vs ABC — what's the difference?
4. What is a `TypeVar` for? What does a bound `TypeVar` do?
5. Why is `list` invariant but `Sequence` covariant?
6. How do you type a decorator so the wrapped function keeps its signature?
7. What is `TypedDict` for, compared with a dataclass?
8. How do you introduce mypy into a large untyped codebase?

---

**Answers**
1. No — the interpreter ignores annotations (they are stored in `__annotations__`). Runtime validation needs libraries such as Pydantic, or explicit checks.
2. `Any` switches type checking off (it is compatible in both directions). `object` is the top type: anything can be assigned to it, but you can only use operations every object supports.
3. A Protocol is structural: any class with matching methods satisfies it, no inheritance needed. An ABC is nominal: you must subclass or register, and it can enforce implementation at instantiation time.
4. It links types across a signature (input type = output type). A bound restricts it to subtypes of a class, e.g. `T bound=Comparable`.
5. `list` is mutable. If `list[Dog]` were a `list[Animal]`, you could append a `Cat` to it. `Sequence` is read-only, so covariance is safe.
6. `P = ParamSpec("P")`, `R = TypeVar("R")`, then `def deco(fn: Callable[P, R]) -> Callable[P, R]` with the wrapper typed `(*args: P.args, **kwargs: P.kwargs) -> R`.
7. It types plain dicts with known keys, e.g. JSON payloads. There is no class instance or methods — just static checking of dict shapes.
8. Gradually: basic config first, check only typed modules, add `--strict` per package, prioritise boundaries (public APIs), use CI as a ratchet, and track the ignore count.

---

## Module 1A.8 — Testing with pytest

**Estimated time: 10 h**

### Topics
- Why test; test pyramid (unit / integration / end-to-end); what to test vs what not to
- pytest basics: discovery, plain `assert` and assertion rewriting, `pytest.raises`, `-k`, `-x`, `--lf`
- Fixtures: scopes, `yield` fixtures (setup/teardown), `conftest.py`, fixture composition, built-in fixtures (`tmp_path`, `capsys`, `monkeypatch`, `caplog`)
- `@pytest.mark.parametrize`, ids, markers, `skip`/`xfail`
- Mocking: `unittest.mock` (`Mock`, `MagicMock`, `patch`, `autospec`, `side_effect`), "patch where it is looked up", mocking philosophy (mock boundaries, not internals)
- Fakes vs mocks vs stubs; dependency injection makes testing easy
- Property-based testing with Hypothesis (strategies, invariants, shrinking)
- Coverage with `pytest-cov`: line vs branch coverage, what 100% doesn't prove
- Test data factories (`factory_boy` preview; used heavily in Track 2)

### Theory resources
- pytest docs (docs.pytest.org): "Get Started", "How to use fixtures", "Fixtures reference", "How to parametrize fixtures and test functions", "How to monkeypatch/mock modules and environments", "How to use temporary directories and files in tests"
- Python docs — `unittest.mock` ("unittest.mock — mock object library", and "unittest.mock — getting started")
- Hypothesis docs (hypothesis.readthedocs.io): "Quick start guide"
- pytest-cov docs; Coverage.py docs "Branch coverage measurement"
- Book (optional): Brian Okken, *Python Testing with pytest* 2nd ed.

### Lessons
- [ ] Lesson 8.1 — pytest basics, assertion rewriting, running and selecting tests
- [ ] Lesson 8.2 — Fixtures: scopes, teardown, `conftest.py`, built-ins
- [ ] Lesson 8.3 — Parametrization and markers
- [ ] Lesson 8.4 — Mocking and patching; fakes vs mocks
- [ ] Lesson 8.5 — Property-based testing with Hypothesis
- [ ] Lesson 8.6 — Coverage and test design

### Exercises
- [ ] Ex 8.1 — **Test suite for `Money`.** Tests for your Ex 6.1 value object. Acceptance: at least one parametrized table of cases, a `pytest.raises` test for the currency mismatch, and branch coverage ≥ 95%.
- [ ] Ex 8.2 — **Fixtures with teardown.** A `yield` fixture that creates a temporary SQLite DB with a schema, used by tests for your Ex 5.1 transactional context manager. Acceptance: each test gets a clean DB; a session-scoped fixture is used where it makes sense and you explain why.
- [ ] Ex 8.3 — **Mock an HTTP boundary.** Write a `fetch_exchange_rate()` function that calls an external API (e.g. `urllib`/`httpx`), and a service that uses it. Test the service with `patch(..., autospec=True)` and with a hand-written fake injected via a parameter. Acceptance: no network in tests; notes compare the two approaches.
- [ ] Ex 8.4 — **`monkeypatch` and time.** Test a function that depends on `os.environ` and on the current time. Acceptance: deterministic tests, no real sleep.
- [ ] Ex 8.5 — **Hypothesis invariants.** Property tests for (a) your `chunked()` from Ex 4.4 — flattening the chunks gives back the input, and every chunk except the last has length `n`; and (b) `Money` — addition is commutative and `a + b - b == a`. Acceptance: introduce a bug on purpose and watch Hypothesis shrink a counterexample.
- [ ] Ex 8.6 — **Retrofit tests.** Add tests to your Module 1A.2 decorators (`@retry` call counts, stacking order, `wraps` metadata). Acceptance: `pytest -q` green, no `sleep` actually waits (patch it).

### Must be able to do / explain
- [ ] Write fixtures with the right scope and clean teardown
- [ ] Parametrize instead of copy-pasting tests
- [ ] Mock at boundaries and explain "patch where it's looked up"
- [ ] Explain when a fake is better than a mock
- [ ] Write a property-based test and explain what an invariant is
- [ ] Explain why 100% coverage doesn't mean correct code

### Self-check interview questions
1. What are fixture scopes, and when would you use `session` scope?
2. How does a `yield` fixture handle teardown if the test fails?
3. Why must you patch "where it's looked up"? Give an example.
4. What is `autospec`, and why use it?
5. Mock vs fake vs stub?
6. What is property-based testing? When is it better than example-based tests?
7. Unit vs integration test — where do you draw the line in a web app?
8. What does coverage tell you, and what doesn't it?

---

**Answers**
1. `function` (the default), `class`, `module`, `package`, `session`. Use `session` for expensive, safe-to-share resources such as starting a DB container, and isolate per-test state with transactions or cleanup.
2. The code after `yield` runs as teardown regardless of the test's result (as long as setup succeeded).
3. `patch` replaces a name in a namespace. If `service.py` does `from api import fetch`, you must patch `service.fetch`, not `api.fetch`, because the service holds its own reference.
4. It makes the mock mirror the real object's signature and attributes, so calls with wrong arguments or misspelled methods fail instead of silently passing.
5. A stub returns canned answers. A mock records calls so you can assert interactions. A fake is a working lightweight implementation, such as an in-memory repository.
6. You state properties that must hold for all inputs, and the framework generates many (including edge cases) and shrinks failures. It is better for parsers, serializers, math/money logic and data transformations.
7. A unit test checks one component in isolation with its dependencies replaced. An integration test involves real infrastructure (DB, HTTP stack). In web apps: services with fake repositories are unit tests; repositories against a real Postgres and API endpoints through the full stack are integration tests.
8. Which lines and branches were executed. It doesn't tell you whether the assertions are meaningful or the behaviour is correct — it is a floor, not proof.

---

## Module 1A.9 — Code Quality: ruff, pre-commit, logging

**Estimated time: 4 h**

### Topics
- Linters vs formatters; ruff as linter **and** formatter (replaces flake8, isort, black, pyupgrade…)
- Choosing rule sets (`E`, `F`, `I`, `B`, `UP`, `SIM`, `N`, `S`), per-file ignores, `noqa` discipline
- pre-commit: hooks, `.pre-commit-config.yaml`, running in CI, secret scanning (e.g. gitleaks/detect-secrets)
- The `logging` module: loggers, handlers, formatters, levels, hierarchy, `logger = logging.getLogger(__name__)`, why never `print` in libraries
- Structured (JSON) logging concept; `extra=` context; preview of `structlog` (used in Track 2)

### Theory resources
- ruff docs (docs.astral.sh/ruff): "Tutorial", "Configuring Ruff", "Rules"
- pre-commit docs (pre-commit.com): "Quick start"
- Python docs — "Logging HOWTO" and "Logging Cookbook" (docs.python.org/3/howto/logging.html)

### Lessons
- [ ] Lesson 9.1 — ruff as linter and formatter
- [ ] Lesson 9.2 — pre-commit hooks
- [ ] Lesson 9.3 — `logging` done right

### Exercises
- [ ] Ex 9.1 — **Lint your history.** Enable ruff with `E,F,I,B,UP,SIM` on all your 1A exercises; fix every finding (don't `noqa` unless you can justify it in notes). Acceptance: `ruff check` and `ruff format --check` are clean.
- [ ] Ex 9.2 — **pre-commit setup.** Hooks: ruff (lint+format), mypy, end-of-file/trailing-whitespace, a secret scanner. Acceptance: committing a file containing a fake AWS key is blocked.
- [ ] Ex 9.3 — **Logging config.** Replace `print` in your `@retry` with a module logger; configure one text handler for dev and one JSON handler for "prod" via `logging.config.dictConfig`. Acceptance: each retry log line includes the attempt number and function name as structured fields.

### Must be able to do / explain
- [ ] Configure ruff and pre-commit for a new project in 10 minutes
- [ ] Explain the logger hierarchy and why libraries shouldn't configure logging
- [ ] Explain why structured logs matter in production

### Self-check interview questions
1. Linter vs formatter?
2. Why run hooks both locally (pre-commit) and in CI?
3. Why use `logging.getLogger(__name__)`?
4. Why shouldn't a library call `logging.basicConfig()`?
5. What makes structured logging better than free text?

---

**Answers**
1. A linter finds likely bugs and style or complexity problems. A formatter rewrites code layout deterministically. ruff does both.
2. Locally: fast feedback before a commit. CI: enforcement, because local hooks can be skipped (`--no-verify`) or not installed.
3. It creates a hierarchy that mirrors your packages, so you can configure levels and handlers per package, and log records show where they came from.
4. Logging configuration belongs to the application. A library configuring handlers causes duplicate or unwanted output; libraries should only create loggers (and at most add a `NullHandler`).
5. Machine-parsable fields (request_id, user_id, latency) can be searched, filtered and aggregated in log systems without fragile regexes.

---

## Module 1A.10 — Packaging

**Estimated time: 5 h**

### Topics
- Modules, packages, `__init__.py`, namespace packages; how `import` resolves (`sys.path`, `sys.modules`)
- Absolute vs relative imports; circular imports and how to break them
- `src/` layout vs flat layout
- Build backends (hatchling, setuptools, uv_build), sdist vs wheel, `python -m build` / `uv build`
- Versioning (SemVer), entry points / console scripts (`[project.scripts]`)
- Editable installs; publishing to TestPyPI; including data files
- Dependency specifiers and version constraints

### Theory resources
- Python Packaging User Guide (packaging.python.org): "Packaging Python Projects" tutorial, "Writing your pyproject.toml", "src layout vs flat layout"
- Python docs — Tutorial §6 "Modules"; Language Reference §5 "The import system"
- uv docs — "Concepts → Projects → Building distributions"

### Lessons
- [ ] Lesson 10.1 — The import system; packages; circular imports
- [ ] Lesson 10.2 — `src/` layout, build backends, sdist vs wheel
- [ ] Lesson 10.3 — Entry points, versioning, publishing

### Exercises
- [ ] Ex 10.1 — **Package your decorators.** Turn your decorators (`timer`, `retry`, `ttl_cache`) into an installable package `<yourname>-decorators` with `src/` layout, tests and type hints (include `py.typed`). Acceptance: `pip install dist/*.whl` into a fresh venv works and mypy sees the types.
- [ ] Ex 10.2 — **Console script.** Add a CLI entry point (e.g. `csvstats <file>` that uses your Ex 4.2 generator). Acceptance: after installing, the command is on `PATH`.
- [ ] Ex 10.3 — **Publish to TestPyPI.** Upload the package and install it back from TestPyPI in a fresh venv. Acceptance: the version is bumped with a SemVer rationale in the changelog.
- [ ] Ex 10.4 — **Break a circular import.** Create two modules that import each other and fail; fix it two different ways. Acceptance: notes explain both fixes.

### Must be able to do / explain
- [ ] Build and install a wheel from a `pyproject.toml` project
- [ ] Explain why `src/` layout catches packaging bugs
- [ ] Explain how Python finds a module when you `import` it
- [ ] Fix a circular import

### Self-check interview questions
1. What happens when you `import foo`?
2. sdist vs wheel?
3. Why is the `src/` layout recommended?
4. What is an editable install?
5. How do you break a circular import?
6. What does `py.typed` do?

---

**Answers**
1. Python checks `sys.modules`. If `foo` isn't there, finders search `sys.path` and a loader executes the module, stores it in `sys.modules` and binds the name.
2. An sdist is a source archive that may need building at install time. A wheel is a pre-built archive that installs by unpacking — faster and deterministic.
3. The package can't be imported by accident from the project root, so tests run against the *installed* package, which catches missing files and wrong configuration.
4. The project is installed as a link to your source, so code changes take effect without reinstalling.
5. Move the shared code into a third module, import inside the function where it's needed, import the module rather than names, or restructure the dependency direction.
6. It marks a package as shipping inline type hints (PEP 561), so type checkers use them.

---

## Module 1A.11 — Concurrency: GIL, Threads, Processes

**Estimated time: 12 h**

### Topics
- Concurrency vs parallelism; I/O-bound vs CPU-bound workloads
- The GIL: what it protects, when it is released (blocking I/O, many C extensions), why CPU-bound threads don't speed up; free-threaded CPython (PEP 703, 3.13+) awareness
- `threading`: `Thread`, daemon threads, `join`, thread-local data
- Race conditions and the read-modify-write problem; why `x += 1` is not atomic
- Synchronization: `Lock`, `RLock`, `Semaphore`, `Event`, `Condition`
- Deadlocks: the four Coffman conditions; lock ordering; timeouts
- `queue.Queue` and producer/consumer; poison-pill shutdown
- `multiprocessing`: processes, pickling costs, `Pool`, shared memory vs message passing, start methods (`fork`/`spawn`)
- `concurrent.futures`: `ThreadPoolExecutor`, `ProcessPoolExecutor`, `submit`/`map`/`as_completed`, exceptions in futures
- Choosing the right tool: threads vs processes vs asyncio

### Theory resources
- *Fluent Python* 2nd ed., Ch. 19 "Concurrency Models in Python" and Ch. 20 "Concurrent Executors"
- David Beazley — "Understanding the Python GIL" (PyCon 2010 talk; slides on dabeaz.com)
- Python docs — `threading`, `queue`, `multiprocessing`, `concurrent.futures`
- Python docs — "What's New in Python 3.13" → free-threaded CPython (awareness only)

### Lessons
- [ ] Lesson 11.1 — Concurrency vs parallelism; the GIL (*Fluent Python* Ch. 19; Beazley talk)
- [ ] Lesson 11.2 — Threads for I/O-bound work
- [ ] Lesson 11.3 — Race conditions, locks and other primitives
- [ ] Lesson 11.4 — Deadlocks: conditions and prevention
- [ ] Lesson 11.5 — Queues and producer/consumer
- [ ] Lesson 11.6 — `multiprocessing` and `concurrent.futures` (*Fluent Python* Ch. 20)

### Exercises
- [ ] Ex 11.1 — **GIL benchmark.** Run a CPU-bound function (e.g. count primes) sequentially, with 4 threads and with 4 processes; then an I/O-bound task (e.g. `time.sleep` or HTTP to a local server) the same three ways. Acceptance: a timing table in notes plus your explanation of every number.
- [ ] Ex 11.2 — **Race condition repro.** Shared counter incremented by N threads without a lock (show a lost update; use `sys.setswitchinterval` to make it reproducible), then fix it with a `Lock`. Acceptance: the final count is correct every run after the fix.
- [ ] Ex 11.3 — **Deadlock repro and fix.** Two threads acquiring two locks in opposite order → deadlock. Fix it with consistent lock ordering, then separately with `acquire(timeout=...)`. Acceptance: notes map the scenario onto the four Coffman conditions.
- [ ] Ex 11.4 — **Producer/consumer pipeline.** One producer reads the 1M-row CSV (Ex 4.2), three consumers validate rows via a bounded `queue.Queue`; clean shutdown with poison pills. Acceptance: no lost or duplicated rows; memory stays bounded.
- [ ] Ex 11.5 — **Parallel image/number crunching.** Use `ProcessPoolExecutor.map` for a CPU-bound batch and `ThreadPoolExecutor` + `as_completed` for concurrent downloads (from a local test server). Acceptance: exceptions in workers are caught and reported, not swallowed.

### Must be able to do / explain
- [ ] Explain exactly when the GIL hurts and when it doesn't
- [ ] Reproduce and fix a race condition
- [ ] Name the four deadlock conditions and a prevention for each
- [ ] Choose threads vs processes vs asyncio for a given workload and justify it
- [ ] Explain the cost of pickling in multiprocessing

### Self-check interview questions
1. What is the GIL, and why does CPython have it?
2. Does the GIL make Python code thread-safe?
3. Why is `counter += 1` not atomic?
4. What are the four conditions for deadlock?
5. When would you use multiprocessing over threading?
6. What are the costs of multiprocessing?
7. How does `queue.Queue` help avoid races?
8. `ThreadPoolExecutor.map` vs `submit` + `as_completed`?
9. What changes with free-threaded Python 3.13+?

---

**Answers**
1. A global mutex that lets only one thread execute Python bytecode at a time. It keeps CPython's reference counting and internals simple and fast in the single-threaded case, and makes C extensions easier to write.
2. No. It protects interpreter internals, not your logic. Threads can switch between bytecodes, so compound operations still race.
3. It is load, add, store — several bytecodes. A thread switch between them causes lost updates.
4. Mutual exclusion, hold-and-wait, no preemption, circular wait. Breaking any one prevents deadlock; lock ordering breaks circular wait.
5. For CPU-bound work in pure Python that needs real parallelism across cores.
6. Process start-up time, memory per process, and pickling data between processes (serialization overhead, some objects can't be pickled), plus harder shared state.
7. It is internally synchronized, so threads hand work over through it instead of sharing mutable state; a bounded size gives backpressure.
8. `map` returns results in input order (lazily) and raises on iteration. `submit` + `as_completed` gives futures as they finish, with per-task exception handling and cancellation.
9. An optional build without the GIL allows true parallel threads for CPU-bound code. It is still experimental, C extensions need to support it, and correct locking matters even more.

---

## Module 1A.12 — asyncio Internals

**Estimated time: 12 h**

### Topics
- Why async: many concurrent I/O waits on one thread; cooperative multitasking
- Coroutines vs tasks vs futures; `async def`, `await`, awaitables
- The event loop: ready queue, selectors (epoll/kqueue), callbacks, what "one loop iteration" means
- `asyncio.run`, `create_task`, `gather`, `TaskGroup` (3.11+), `wait_for`/`timeout`, `as_completed`
- Cancellation: `CancelledError`, cleanup in `finally`, shielding
- Blocking vs non-blocking: what happens when you call `time.sleep`/`requests.get`/CPU-heavy code inside a coroutine; `asyncio.to_thread` and `run_in_executor`
- Synchronization and backpressure: `asyncio.Lock`, `Semaphore` (limiting concurrency), `asyncio.Queue`
- Async context managers and async iterators/generators
- Debug mode (`PYTHONASYNCIODEBUG`, slow callback warnings)
- **When async helps and when it does not**: I/O-bound fan-out (yes), CPU-bound work (no), a single sequential DB call per request (little), mixing sync libraries (danger)

### Theory resources
- *Fluent Python* 2nd ed., Ch. 21 "Asynchronous Programming"
- Python docs — `asyncio` (docs.python.org/3/library/asyncio.html): "Coroutines and Tasks", "Event Loop", "Synchronization Primitives", "Queues", "Developing with asyncio"
- Real Python — "Async IO in Python: A Complete Walkthrough"
- Optional: David Beazley — "Build Your Own Async" (PyCon 2019 workshop, YouTube)

### Lessons
- [ ] Lesson 12.1 — Coroutines, tasks, futures and `await` (*Fluent Python* Ch. 21; asyncio docs "Coroutines and Tasks")
- [ ] Lesson 12.2 — How the event loop works (selectors, ready queue)
- [ ] Lesson 12.3 — Structured concurrency: `gather` vs `TaskGroup`, timeouts, cancellation
- [ ] Lesson 12.4 — Blocking vs non-blocking; `to_thread`/executors; debug mode
- [ ] Lesson 12.5 — Limiting concurrency and backpressure: `Semaphore`, `Queue`
- [ ] Lesson 12.6 — When async helps and when it doesn't

### Exercises
- [ ] Ex 12.1 — **Concurrent supplier-price fetcher.** Five fake "supplier endpoints" (coroutines with random `asyncio.sleep` latency and occasional failures); fetch all concurrently with `gather`, then rewrite with `TaskGroup`. Acceptance: total time ≈ slowest call, not the sum; notes compare how each handles one failure.
- [ ] Ex 12.2 — **Timeouts and cancellation.** Add a per-call timeout and a global deadline; ensure cancelled tasks run their cleanup (`finally`). Acceptance: logs prove cleanup ran; no "Task was destroyed but it is pending" warnings.
- [ ] Ex 12.3 — **Block the loop on purpose.** Add a `time.sleep(1)` (and separately a CPU-heavy loop) inside one coroutine; measure the effect on all others; enable debug mode to catch it; fix with `asyncio.to_thread` or a process pool. Acceptance: a before/after timing table.
- [ ] Ex 12.4 — **Bounded crawler.** Crawl 200 URLs from a local test server with at most 10 in flight (`Semaphore`), plus a worker-pool version with `asyncio.Queue`. Acceptance: peak concurrency never exceeds 10 (measure it).
- [ ] Ex 12.5 — **Toy event loop.** Implement a tiny scheduler for generator-based tasks (round-robin with a `deque`, plus a `sleep` that re-queues). No `asyncio` import. Acceptance: three tasks interleave correctly; notes map your design onto asyncio's.
- [ ] Ex 12.6 — **Decision memo.** In `notes.md`, for 5 scenarios (web scraper, image resize service, CRUD API with one DB query per request, chat server with 10k websockets, ETL of CSV files), choose sync/threads/processes/async and justify each.

### Must be able to do / explain
- [ ] Explain what the event loop does in one iteration
- [ ] Explain coroutine vs task vs future
- [ ] Spot blocking calls in async code and fix them
- [ ] Use `TaskGroup`, timeouts and cancellation correctly
- [ ] Limit concurrency with a `Semaphore`
- [ ] Argue when async is the wrong choice

### Self-check interview questions
1. What happens when you call a coroutine function without `await`?
2. Coroutine vs Task vs Future?
3. How does the event loop know when a socket is ready?
4. What happens if you call `time.sleep(5)` inside a coroutine?
5. `gather` vs `TaskGroup` — how do they differ on errors?
6. How does cancellation work in asyncio?
7. How do you call blocking library code from async code?
8. Is async faster than threads? When does async not help?
9. How do you limit concurrent outgoing requests to 10?
10. Why can a single slow synchronous DB driver ruin an async web server?

---

**Answers**
1. You get a coroutine object, but nothing runs (and you get a "never awaited" warning).
2. A coroutine is the suspended computation. A Task wraps a coroutine and schedules it on the loop. A Future is a low-level placeholder for a result; Task is a subclass of Future.
3. It registers file descriptors with the OS selector (epoll/kqueue/IOCP) and blocks in `select` until an FD is ready or the next timer is due, then runs the callbacks.
4. The whole event loop thread blocks for 5 s, and every other coroutine stalls. Use `await asyncio.sleep(5)`.
5. By default, `gather` propagates the first exception but leaves the other tasks running (unless you handle it). `TaskGroup` cancels the remaining tasks when one fails and raises an `ExceptionGroup` — structured concurrency.
6. `task.cancel()` injects `CancelledError` at the next `await`. The coroutine can clean up in `finally` and should re-raise. `shield` protects an inner awaitable.
7. `await asyncio.to_thread(fn, ...)` or `loop.run_in_executor(pool, fn, ...)` (a process pool for CPU-bound work).
8. Not faster per operation. It scales better for many concurrent I/O waits (less memory than threads, no context-switch overhead). It doesn't help CPU-bound work, sequential dependent calls, or code built on blocking libraries.
9. An `asyncio.Semaphore(10)` around each request, or a pool of 10 worker coroutines consuming from an `asyncio.Queue`.
10. Each blocking call freezes the single loop thread, so the throughput of all concurrent requests collapses to one-at-a-time.

---

## Track 1A Progress Summary

| Module | Lessons done / total | Exercises done / total |
|---|---|---|
| 1A.1 Git & Environment | 0 / 6 | 0 / 5 |
| 1A.2 Functions, Closures, Decorators | 3 / 4 | 3 / 6 |
| 1A.3 Memory Model | 2 / 4 | 2 / 5 |
| 1A.4 Iterators & Generators | 0 / 4 | 0 / 5 |
| 1A.5 Context Managers | 0 / 3 | 0 / 4 |
| 1A.6 OOP Internals | 0 / 6 | 0 / 5 |
| 1A.7 Type Hints & mypy | 0 / 5 | 0 / 5 |
| 1A.8 pytest | 0 / 6 | 0 / 6 |
| 1A.9 ruff, pre-commit, logging | 0 / 3 | 0 / 3 |
| 1A.10 Packaging | 0 / 3 | 0 / 4 |
| 1A.11 Concurrency | 0 / 6 | 0 / 5 |
| 1A.12 asyncio Internals | 0 / 6 | 0 / 6 |
| **Total** | **5 / 56** | **5 / 59** |

Total estimated time: **~95 h** (8 + 8 + 5 + 8 + 5 + 10 + 8 + 10 + 4 + 5 + 12 + 12).
