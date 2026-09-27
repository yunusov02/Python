# Track 4A — Java Core (Parts 1–4)

**Track 4 goal:** go from zero Java to a **middle+ Java / Spring / Oracle
backend developer**. You should be able to write idiomatic modern Java, reason
about concurrency and the JVM, build and test with Maven/Gradle, talk to
PostgreSQL and Oracle (including PL/SQL) from Java, and ship Spring Boot
services and microservices to production.

**Required knowledge:**
- Python fundamentals (you have them). Java is explained from scratch here;
  short Python comparisons are only hints.
- Track 1C Part 3 (Oracle SQL + PL/SQL) **before the Oracle projects** (JP2,
  JM2, JM3, JMP3). SQL and PL/SQL are taught there, not here.
- Track 2 teaches the backend concepts (HTTP/REST, transactions, caching,
  messaging, outbox/saga, Docker, CI/CD, Kubernetes, observability) with
  Python. Track 4 teaches **the Java / Spring way** of doing the same things
  and points back to Track 2 modules where the concept lives.

**Track 4 total:** ~845 h core (~350 h modules + ~495 h projects) plus
~110 h OPTIONAL projects.
**This file (4A):** Parts 1–4, ~157 h modules + JP1 (~25 h).

**Track 4 files:**
- `04a-java-core.md` — Parts 1–4: fundamentals, modern Java, concurrency &
  JVM, build/test/tooling, project JP1. *(this file)*
- [`04b-java-databases.md`](04b-java-databases.md) — Part 5: JDBC, HikariCP,
  Oracle from Java, Flyway/Liquibase, PL/SQL from Java, JPA/Hibernate,
  project JP2.
- [`04c-spring.md`](04c-spring.md) — Parts 6–9: Spring core, Spring Boot and
  ecosystem, microservices & production, interview prep, projects JP3, JM1–JM3,
  JMP1–JMP3, JO1–JO2.

Back to the overview: [`../00-overview.md`](../00-overview.md)

---

## How to use this track

- **Checkboxes everywhere.** Tick a lesson when you can explain it without
  notes, an exercise when it meets its acceptance criteria, a project
  milestone when every deliverable in it is committed.
- **No solutions in these files.** Specs, acceptance criteria and checklists
  only. You write every line; the mentor reviews, asks questions and explains
  concepts, never hands over the finished code.
- **Python comparisons** (`🐍`) are one-line hints to anchor a concept, not a
  substitute for learning the Java rule.
- **Java version:** **Java 25 LTS** is the target. Java 21 LTS is fine too;
  where a feature is 25-only or still a *preview* feature, it is marked.
  Preview features need `--enable-preview` and can change between releases.
- **Where the work goes:**
  - Module exercises: this repo, `java/<Jx.y-slug>/`, each one a small Maven
    project (e.g. `java/J1.11-collections/`). Until J1.13 (Maven) you can use
    plain `javac`/`java` or a bare IntelliJ project.
  - Projects: **one GitHub repo per project** (`ledgerlite-cli`,
    `branchdesk`, …).
- **Self-check questions** close every module. Answer out loud first, then read
  the answers below the `---` separator.

---

## Track 4 roadmap

| # | Item | File | Level / type | Hours |
|---|---|---|---|---|
| **Part 1** | **Java fundamentals** | 4A | | **61** |
| J1.1 | JDK/JRE/JVM, IntelliJ IDEA, compilation & bytecode | 4A | Module | 4 |
| J1.2 | Primitive & reference types, operators, control flow, arrays | 4A | Module | 6 |
| J1.3 | Strings: immutability, StringBuilder, string pool | 4A | Module | 3 |
| J1.4 | Methods & packages | 4A | Module | 3 |
| J1.5 | OOP I: classes, constructors, encapsulation, static vs instance, final | 4A | Module | 6 |
| J1.6 | OOP II: inheritance, polymorphism, abstract classes, interfaces, default methods | 4A | Module | 6 |
| J1.7 | equals / hashCode / toString contracts | 4A | Module | 3 |
| J1.8 | Exceptions: checked vs unchecked, try-with-resources, custom | 4A | Module | 4 |
| J1.9 | Enums, wrapper classes & autoboxing | 4A | Module | 3 |
| J1.10 | Generics: bounded types, wildcards, type erasure | 4A | Module | 5 |
| J1.11 | Collections Framework + iterators | 4A | Module | 10 |
| J1.12 | I/O, NIO.2, java.time | 4A | Module | 5 |
| J1.13 | First build & tests: Maven basics + JUnit 5 basics | 4A | Module | 3 |
| **JP1** | **LedgerLite CLI** — expense & budget tracker console app | 4A | **Junior** | **25** |
| **Part 2** | **Modern & advanced Java** | 4A | | **37** |
| J2.1 | Lambdas, functional interfaces, method references | 4A | Module | 5 |
| J2.2 | Streams API & Optional | 4A | Module | 8 |
| J2.3 | Records, sealed classes, pattern matching, text blocks, var | 4A | Module | 5 |
| J2.4 | Annotations, reflection, JPMS basics | 4A | Module | 5 |
| J2.5 | Immutability & design patterns | 4A | Module | 8 |
| J2.6 | SOLID & key Effective Java items | 4A | Module | 6 |
| **Part 3** | **Concurrency & JVM internals** | 4A | | **40** |
| J3.1 | Threads, synchronized, volatile, Java Memory Model | 4A | Module | 8 |
| J3.2 | Locks, atomics, concurrent collections, synchronizers | 4A | Module | 6 |
| J3.3 | ExecutorService & CompletableFuture | 4A | Module | 6 |
| J3.4 | Deadlocks, virtual threads, structured concurrency | 4A | Module | 6 |
| J3.5 | JVM internals: memory, class loading, GC, JIT | 4A | Module | 8 |
| J3.6 | Diagnostics: jcmd, jstack, JFR, VisualVM, memory leaks | 4A | Module | 6 |
| **Part 4** | **Build, testing, tooling** | 4A | | **19** |
| J4.1 | Maven & Gradle: lifecycle, plugins, multi-module | 4A | Module | 6 |
| J4.2 | JUnit 5, AssertJ, parameterized tests, Mockito | 4A | Module | 7 |
| J4.3 | Testcontainers | 4A | Module | 3 |
| J4.4 | Checkstyle / SpotBugs / SonarLint + SLF4J / Logback | 4A | Module | 3 |
| **Part 5** | **Databases from Java** | 4B | | **47** |
| J5.1 | JDBC fundamentals: PreparedStatement, ResultSet, transactions, batch, SQL injection | 4B | Module | 6 |
| J5.2 | Connection pooling with HikariCP | 4B | Module | 2 |
| J5.3 | Oracle from Java: ojdbc, UCP, Oracle Free in Docker & Testcontainers, type mapping | 4B | Module | 5 |
| J5.4 | Schema migrations: Flyway & Liquibase | 4B | Module | 4 |
| **JP2** | **BranchDesk** — JDBC CRUD & transfers on Oracle | 4B | **Junior** | **30** |
| J5.5 | Calling PL/SQL from Java: CallableStatement, IN/OUT, REF CURSOR, packages, array/object types | 4B | Module | 7 |
| J5.6 | JPA & Hibernate I: entities, relationships, fetch types, N+1 | 4B | Module | 8 |
| J5.7 | JPA & Hibernate II: persistence context, dirty checking, caching, locking, Oracle sequences | 4B | Module | 7 |
| J5.8 | JPQL & Criteria API | 4B | Module | 4 |
| J5.9 | Oracle performance from Java: fetch size, statement caching, batching, plans | 4B | Module | 4 |
| **Part 6** | **Spring Framework core** | 4C | | **15** |
| J6.1 | IoC container, DI, beans & scopes, @Configuration/@Bean, component scanning | 4C | Module | 6 |
| J6.2 | Profiles & properties | 4C | Module | 2 |
| J6.3 | AOP, proxies, how @Transactional works & its pitfalls | 4C | Module | 5 |
| J6.4 | Spring events | 4C | Module | 2 |
| **Part 7** | **Spring Boot & ecosystem** | 4C | | **70** |
| J7.1 | Boot fundamentals: auto-configuration, starters, externalized config | 4C | Module | 4 |
| J7.2 | Spring MVC & REST, Bean Validation, @ControllerAdvice/ProblemDetail, springdoc OpenAPI | 4C | Module | 8 |
| J7.3 | Spring Data JPA | 4C | Module | 7 |
| J7.4 | Spring Boot testing | 4C | Module | 5 |
| **JP3** | **LoanProduct Catalog API** — Spring Boot + Spring Data JPA | 4C | **Junior** | **35** |
| J7.5 | Transactions in Spring, JdbcTemplate/JdbcClient, SimpleJdbcCall/@Procedure | 4C | Module | 6 |
| J7.6 | Spring Security: filter chain, JWT, OAuth2 Resource Server, method security | 4C | Module | 10 |
| J7.7 | Spring Cache with Redis | 4C | Module | 3 |
| **JM1** | **TeamBoard** — secure issue-tracker API | 4C | **Middle** | **50** |
| **JM2** | **CreditLine Reporting Service** — Oracle + PL/SQL packages | 4C | **Middle** | **55** |
| J7.8 | Spring Batch & scheduling | 4C | Module | 7 |
| **JM3** | **CreditLine Nightly Batch** — Spring Batch on Oracle + PL/SQL | 4C | **Middle** | **50** |
| J7.9 | Spring AMQP with RabbitMQ | 4C | Module | 4 |
| J7.10 | Spring for Apache Kafka | 4C | Module | 5 |
| J7.11 | WebFlux & Project Reactor (and when NOT to use them) | 4C | Module | 6 |
| J7.12 | Actuator, Micrometer, observability | 4C | Module | 5 |
| **Part 8** | **Microservices & production** | 4C | | **41** |
| J8.1 | Spring Cloud: Config Server, Gateway, OpenFeign, service discovery | 4C | Module | 8 |
| J8.2 | Resilience4j | 4C | Module | 4 |
| J8.3 | Inter-service communication: REST, messaging, gRPC in Java; saga & outbox | 4C | Module | 7 |
| J8.4 | Containerizing Spring Boot (layered JARs, Buildpacks, Jib) + Docker Compose | 4C | Module | 4 |
| J8.5 | CI/CD for Java with GitHub Actions | 4C | Module | 3 |
| **JMP1** | **PolisHub Microservices** — Gateway, Kafka, outbox | 4C | **Middle+** | **90** |
| J8.6 | Performance tuning & load testing | 4C | Module | 6 |
| **JMP2** | **TicketRush** — high-concurrency reservations with virtual threads | 4C | **Middle+** | **60** |
| J8.7 | Kubernetes deployment of Spring Boot | 4C | Module | 6 |
| J8.8 | GraalVM native images | 4C | Module | 3 |
| **JMP3** | **CreditLine Core on Kubernetes** — production-grade Oracle system | 4C | **Middle+** | **100** |
| **Part 9** | **Interview preparation** | 4C | | **20** |
| J9.1 | Core Java interview topics | 4C | Module | 8 |
| J9.2 | Spring & Hibernate interview topics | 4C | Module | 6 |
| J9.3 | Idiomatic Java for coding tasks | 4C | Module | 6 |
| JO1 | PolisHub Oracle Policy Core | 4C | Project · OPTIONAL | 80 |
| JO2 | Reactive Price Feed (WebFlux + SSE) | 4C | Project · OPTIONAL | 30 |

**Oracle projects:** JP2, JM2, JM3, JMP3. **Projects that call PL/SQL
packages/procedures from Java:** JM2, JM3, JMP3.

---

# Part 1 — Java fundamentals (~61 h)

**Main resources for Part 1:**
- dev.java → **Learn** (dev.java/learn) — the official Oracle tutorial.
- *Head First Java*, 3rd ed. (Sierra, Bates, Gee, 2022).
- *Effective Java*, 3rd ed. (Bloch) — item numbers are given where relevant.
- Baeldung (baeldung.com) — searchable by the article titles given.

---

## Module J1.1 — JDK/JRE/JVM, IntelliJ IDEA, compilation & bytecode (~4h)

**Topics:** what the JDK, JRE and JVM are; `javac` compiles `.java` →
`.class` (bytecode); the JVM loads and runs bytecode (interpreter + JIT);
"write once, run anywhere"; installing a JDK (Temurin / Oracle JDK / SDKMAN!);
`JAVA_HOME` and `PATH`; `java` launcher, single-file source launch
(`java Hello.java`), JShell; compact source files and instance `main` methods
(JEP 512, final in Java 25); IntelliJ IDEA: project SDK, run configurations,
debugger basics; reading bytecode with `javap -c`.

🐍 Python compiles to `.pyc` bytecode too, but CPython has no JIT by default and
checks types at run time; Java checks types at compile time.

### Lessons
- [ ] **J1.1.L1 The platform.** dev.java/learn → "Getting Started with Java" → "Running Your First Java Application"; Baeldung "Difference Between JVM, JRE, and JDK".
- [ ] **J1.1.L2 Tools.** dev.java/learn → "Learn the Java Tools" → "javac – the Compiler", "java – the Launcher", "JShell", "javap".
- [ ] **J1.1.L3 Modern entry points.** JEP 512 "Compact Source Files and Instance Main Methods" (openjdk.org/jeps/512) — read "Summary", "Goals", "Description".
- [ ] **J1.1.L4 First chapter.** *Head First Java* ch.1 "Breaking the Surface".
- [ ] **J1.1.L5 IDE.** IntelliJ IDEA docs → "Create your first Java application"; "Debug your first Java application".

### Exercises (`java/J1.1-platform/`)
- [ ] **Ex J1.1.1 Install and verify.** Install a JDK 25 (or 21) with SDKMAN! or a package manager. *Acceptance:* `java -version` and `javac -version` print the same version; you can switch versions and explain what `JAVA_HOME` is used for.
- [ ] **Ex J1.1.2 By hand.** Write `Hello.java` in a plain editor, compile with `javac`, run with `java`, then run the source directly with `java Hello.java`. *Acceptance:* you can explain which command produced which file and why the class name must match the file name.
- [ ] **Ex J1.1.3 Read bytecode.** Write a class with a method that adds two `int`s and one that concatenates two `String`s. Run `javap -c` on it. *Acceptance:* you point out the `iadd` instruction and explain what the string method compiles to (look for `invokedynamic`/`makeConcatWithConstants`).
- [ ] **Ex J1.1.4 JShell.** Use JShell to try 10 expressions (integer division, `%`, `Math.max`, string methods). *Acceptance:* you note two results that differ from Python (e.g. `7 / 2`, `-7 % 3`).
- [ ] **Ex J1.1.5 Debugger.** In IntelliJ, set a breakpoint in a loop, step over/into, inspect variables, add a watch. *Acceptance:* you can do it without looking up the shortcut names.

### Must be able to do / explain
- [ ] Explain JDK vs JRE vs JVM in one sentence each.
- [ ] Compile and run a program from the command line and from IntelliJ.
- [ ] Explain what bytecode is and why the JIT makes Java fast after warm-up.
- [ ] Use JShell and the IntelliJ debugger.

**Estimated hours:** ~4 h

### Self-check questions
1. What is the difference between the JDK, the JRE and the JVM?
2. What does `javac` produce, and what does the `java` launcher do with it?
3. Why does "write once, run anywhere" hold for Java bytecode?
4. What is the JIT compiler, and why does a Java program often get faster after it has run for a while?
5. What does `java Hello.java` do differently from `javac Hello.java && java Hello`?
6. Why must a public class `Foo` live in `Foo.java`?

---

**Answers**
1. The JDK is the development kit (compiler `javac`, tools, plus a runtime). The JRE is the runtime only (JVM + class libraries); since Java 11 it is not shipped separately. The JVM is the virtual machine that loads, verifies and executes bytecode.
2. `javac` produces `.class` files containing platform-independent bytecode. `java` starts a JVM, loads the main class through class loaders, verifies it and executes it (interpreting and JIT-compiling hot code).
3. Bytecode targets the JVM, not a CPU/OS. Any platform with a compliant JVM runs the same `.class` files.
4. The JIT (HotSpot C1/C2) compiles frequently executed ("hot") methods into optimized native code using runtime profiling (inlining, escape analysis). Early on, code is interpreted; after warm-up the hot paths run as native code.
5. Source-file mode compiles the file in memory and runs it immediately, without writing `.class` files; handy for scripts and learning, not for multi-file projects.
6. It is a compiler rule: a public top-level class must be declared in a file with the same name, so the compiler and tools can find classes by name.

---

## Module J1.2 — Primitive & reference types, operators, control flow, arrays (~6h)

**Topics:** static typing; the 8 primitives (`byte`, `short`, `int`, `long`,
`float`, `double`, `char`, `boolean`) with sizes and ranges; literals
(`10L`, `1_000_000`, `0x`, `'a'`); widening vs narrowing casts; integer
overflow (silent wrap-around); integer division and `%` with negatives;
floating-point imprecision (never for money — preview of `BigDecimal`);
reference types and `null`; stack vs heap (conceptually); operators and
precedence, `++`/`--`, compound assignment with hidden cast, `==` on
references; `if`/`else`, classic `switch` vs switch expressions (`->`,
`yield`), `while`, `do-while`, `for`, enhanced `for`, `break`/`continue`
with labels; arrays: declaration, fixed length, default values,
multi-dimensional arrays, `Arrays.toString/sort/fill/copyOf/equals`.

🐍 Python `int` never overflows; Java `int` wraps at 2³¹−1. Python lists grow;
Java arrays have a fixed length.

### Lessons
- [ ] **J1.2.L1 Variables and primitives.** dev.java/learn → "Language Basics" → "Creating Variables and Naming Them", "Creating Primitive Type Variables in Your Programs".
- [ ] **J1.2.L2 Operators.** dev.java/learn → "Language Basics" → "Using Operators in Your Programs", "Summary of Operators", "Expressions, Statements and Blocks".
- [ ] **J1.2.L3 Control flow.** dev.java/learn → "Language Basics" → "Control Flow Statements"; "Branching with Switch Expressions".
- [ ] **J1.2.L4 Arrays.** dev.java/learn → "Language Basics" → "Creating Arrays in Your Programs"; javadoc of `java.util.Arrays`.
- [ ] **J1.2.L5 Book.** *Head First Java* ch.3 "Know Your Variables" and ch.5 "Extra-Strength Methods" (loops, the `for` loop, casting).

### Exercises (`java/J1.2-basics/`)
- [ ] **Ex J1.2.1 Overflow lab.** Print `Integer.MAX_VALUE + 1`, `Long.MAX_VALUE + 1`, `(byte) 200`, `0.1 + 0.2`, `7 / 2`, `-7 / 2`, `-7 % 3`, `7.0 / 0`. *Acceptance:* a comment next to each line explains the result; you also use `Math.addExact` to make the first one throw.
- [ ] **Ex J1.2.2 FizzBuzz two ways.** Once with `if`/`else`, once with a switch expression on `i % 15` (or on a computed key). *Acceptance:* identical output for 1..100; the switch version has no fall-through.
- [ ] **Ex J1.2.3 Array utilities.** Without `java.util` helpers: reverse an `int[]` in place, find min/max, compute a running-sum array, and rotate right by k. Then compare with `Arrays` methods where they exist. *Acceptance:* a `main` prints before/after for 3 test arrays including an empty one.
- [ ] **Ex J1.2.4 Matrix.** Read a size n, build an n×n multiplication table as `int[][]` and print it aligned with `System.out.printf`. *Acceptance:* columns are aligned for n = 12.
- [ ] **Ex J1.2.5 Labels.** Search a 2-D array for a target and stop both loops as soon as it is found using a labeled `break`. *Acceptance:* you can explain when a labeled break is clearer than a flag.

### Must be able to do / explain
- [ ] Name all 8 primitives with their sizes.
- [ ] Predict overflow, integer division and `%` results.
- [ ] Explain why `double` is wrong for money.
- [ ] Write switch expressions and enhanced `for` loops.
- [ ] Explain that an array variable holds a reference, and what default values array elements get.

**Estimated hours:** ~6 h

### Self-check questions
1. What happens when an `int` exceeds `Integer.MAX_VALUE`?
2. What is the difference between widening and narrowing conversion? Which one needs an explicit cast?
3. Why does `short s = 1; s = s + 1;` not compile while `s += 1;` does?
4. What does `==` compare for primitives and for references?
5. What are the advantages of a switch expression over the classic switch statement?
6. What default value does an element of a new `int[]`, `boolean[]` and `String[]` have?
7. Why is `0.1 + 0.2 != 0.3` in Java (and Python)?

---

**Answers**
1. It silently wraps around to `Integer.MIN_VALUE` (two's-complement overflow). Use `Math.addExact` etc. to get an `ArithmeticException` instead, or use `long`/`BigInteger`.
2. Widening (e.g. `int` → `long`) never loses magnitude and is implicit. Narrowing (e.g. `long` → `int`, `double` → `int`) can lose information and requires an explicit cast.
3. `s + 1` is promoted to `int`, and assigning `int` to `short` is narrowing. Compound assignment includes an implicit cast back to the left-hand type.
4. For primitives, it compares values. For references, it compares identity (same object), not content — use `equals` for content.
5. It returns a value, uses `->` so there is no fall-through, must be exhaustive (for enums/sealed types), and supports multiple labels per case and pattern matching.
6. `0`, `false` and `null`.
7. `0.1` and `0.2` have no exact binary representation in IEEE 754, so their sum is `0.30000000000000004`. Use `BigDecimal` for exact decimal arithmetic.

---

## Module J1.3 — Strings: immutability, StringBuilder, string pool (~3h)

**Topics:** `String` is an immutable object; string literals and the string
pool; `new String("x")` vs `"x"`; `intern()`; `==` vs `equals` vs
`equalsIgnoreCase`; common methods (`length`, `charAt`, `substring`,
`indexOf`, `split`, `strip`, `isBlank`, `repeat`, `chars`, `formatted`,
`String.join`); `char` vs code points (Unicode, emoji); concatenation cost in
loops; `StringBuilder` (mutable, not thread-safe) vs `StringBuffer`;
`String.format` / `printf`.

🐍 Python strings are immutable too, and `is` vs `==` is the same trap as Java's
`==` vs `equals`.

### Lessons
- [ ] **J1.3.L1 Strings.** dev.java/learn → "Numbers and Strings" → "Strings", "Manipulating Characters in a String", "Comparing Strings and Portions of Strings".
- [ ] **J1.3.L2 StringBuilder.** dev.java/learn → "Numbers and Strings" → "The StringBuilder Class".
- [ ] **J1.3.L3 The pool.** Baeldung "Guide to Java String Pool".
- [ ] **J1.3.L4 Effective Java.** Item 63 "Beware the performance of string concatenation".

### Exercises (`java/J1.3-strings/`)
- [ ] **Ex J1.3.1 Identity vs equality.** Create strings via literal, `new String`, concatenation of literals, concatenation with a variable, and `intern()`. Print `==` and `equals` for each pair. *Acceptance:* every `true`/`false` is explained in a comment.
- [ ] **Ex J1.3.2 Text utilities.** Implement `isPalindrome` (ignore case and non-letters), `countWords`, `capitalizeEachWord`, and `compress("aaabcc") → "a3b1c2"` using `StringBuilder`. *Acceptance:* `main` shows 3 inputs each, including empty and blank strings.
- [ ] **Ex J1.3.3 Concatenation benchmark.** Build a string of 100 000 numbers with `+=` in a loop vs `StringBuilder`. Time both with `System.nanoTime()`. *Acceptance:* you record the numbers and explain the difference (and why a micro-benchmark like this is only indicative — JMH comes later in J8.6).
- [ ] **Ex J1.3.4 Unicode.** Take a string with an emoji; compare `length()` with `codePointCount`. *Acceptance:* you can explain surrogate pairs in two sentences.

### Must be able to do / explain
- [ ] Explain why `String` is immutable and the benefits (pool, safe keys, thread safety).
- [ ] Always compare strings with `equals`.
- [ ] Choose `StringBuilder` for building strings in loops.
- [ ] Explain the string pool and when `new String` creates a new object.

**Estimated hours:** ~3 h

### Self-check questions
1. Why is `String` immutable in Java? Name three benefits.
2. What is the string pool, and which strings end up in it automatically?
3. Why can `"a" + "b" == "ab"` be `true` but `s + "b" == "ab"` be `false`?
4. `StringBuilder` vs `StringBuffer` — what is the difference?
5. Why is `+=` in a loop slow?

---

**Answers**
1. Immutability allows the string pool (sharing), makes strings safe as `HashMap` keys (hash can be cached), makes them inherently thread-safe, and makes security checks (e.g. file names) reliable because the value can't change after validation.
2. A JVM-managed table of unique string instances. All string literals and compile-time constant expressions are pooled automatically; others can be added with `intern()`.
3. `"a" + "b"` is a compile-time constant folded into the literal `"ab"`, so both refer to the pooled instance. `s + "b"` is computed at run time and creates a new object.
4. Same API; `StringBuffer` methods are synchronized (thread-safe, slower), `StringBuilder` is not. Use `StringBuilder` unless you really share it across threads (almost never).
5. Each `+=` creates a new `String` and copies all previous characters, so building n pieces is O(n²). A `StringBuilder` appends into a growable buffer, amortized O(n).

---

## Module J1.4 — Methods & packages (~3h)

**Topics:** method signature (name + parameter types); return types and
`void`; **pass-by-value** (including references: the reference is copied);
overloading and how the compiler picks an overload; varargs; `static`
methods; recursion and `StackOverflowError`; packages and the directory
layout; `import`, static import, the default package (avoid it); access
modifiers overview (`public`, `protected`, package-private, `private`);
naming conventions.

🐍 Python passes object references by value as well ("pass by assignment");
Java has no keyword or default arguments — overloading replaces them.

### Lessons
- [ ] **J1.4.L1 Methods.** dev.java/learn → "Classes and Objects" → "Defining Methods", "Passing Information to a Method or a Constructor".
- [ ] **J1.4.L2 Packages.** dev.java/learn → "Packages" → "Understanding Packages", "Creating and Using Packages", "Managing Source and Class Files".
- [ ] **J1.4.L3 Book.** *Head First Java* ch.4 "How Objects Behave" (parameters, return types, pass-by-value).
- [ ] **J1.4.L4 Effective Java.** Item 51 "Design method signatures carefully", Item 52 "Use overloading judiciously", Item 53 "Use varargs judiciously".

### Exercises (`java/J1.4-methods/`)
- [ ] **Ex J1.4.1 Pass-by-value proof.** Write `swap(int a, int b)`, `swap(int[] arr, int i, int j)`, `reassign(StringBuilder sb)` and `mutate(StringBuilder sb)`. *Acceptance:* `main` shows which ones change the caller's data, with a comment explaining each.
- [ ] **Ex J1.4.2 Overloading.** Write `area(double r)`, `area(double w, double h)`, `area(int side)`. Call `area(5)`, `area(5.0)`, `area(5, 3)`. *Acceptance:* you predict each chosen overload before running.
- [ ] **Ex J1.4.3 Varargs stats.** `static double average(int... xs)` that throws `IllegalArgumentException` for zero args. *Acceptance:* callable with 0 (throws), 1, many args and with an `int[]`.
- [ ] **Ex J1.4.4 Packages.** Create packages `com.yourname.geometry` and `com.yourname.app`; call a package-private method across packages and see it fail, then fix the design. *Acceptance:* folder structure matches packages; you compile from the command line with `-d out`.

### Must be able to do / explain
- [ ] Explain Java's pass-by-value with a reference example.
- [ ] Explain how overload resolution chooses a method.
- [ ] Organise code into packages and use the four access levels.

**Estimated hours:** ~3 h

### Self-check questions
1. Is Java pass-by-value or pass-by-reference? Prove it with an example.
2. What is part of a method signature, and is the return type part of it?
3. How do you emulate Python default arguments in Java?
4. What is package-private access?
5. Why avoid the default (unnamed) package?

---

**Answers**
1. Always pass-by-value. For objects, the value passed is a copy of the reference: the method can mutate the object, but reassigning the parameter does not change the caller's variable (e.g. `swap(Integer a, Integer b)` can't swap the caller's variables).
2. The name and the parameter types (in order). The return type is not part of the signature, so you can't overload by return type alone.
3. Overloads that delegate to the fullest version, the builder pattern for many optional parameters, or passing a parameter object.
4. No modifier: visible to all classes in the same package, invisible outside it.
5. Classes in the unnamed package cannot be imported from named packages, names can clash, and build tools and modules expect proper packages.

---

## Module J1.5 — OOP I: classes, constructors, encapsulation, static vs instance, final (~6h)

**Topics:** class vs object; fields, methods, constructors (default,
overloaded, `this(...)` chaining); `this`; object creation and
initialization order (static init, instance init, constructor); encapsulation
(private fields + getters/setters, invariants in constructors); `static`
fields/methods vs instance members; `final` variables, fields, methods and
classes; constants (`static final`); nested classes: static nested, inner,
local, anonymous; garbage collection of unreachable objects (intro); flexible
constructor bodies (JEP 513, final in Java 25) — statements before `super(...)`.

🐍 Python's `self` is explicit and all attributes are public by convention;
Java uses `private` and the compiler enforces it.

### Lessons
- [ ] **J1.5.L1 Classes.** dev.java/learn → "Classes and Objects" → "Creating Classes", "Providing Constructors for your Classes", "Creating and Using Objects", "More on Classes" (returning values, `this`, access control, class members, initializing fields).
- [ ] **J1.5.L2 Nested classes.** dev.java/learn → "Classes and Objects" → "Nested Classes".
- [ ] **J1.5.L3 Book.** *Head First Java* ch.2 "A Trip to Objectville", ch.9 "Life and Death of an Object", ch.10 "Numbers Matter" (the `static` and `final` parts).
- [ ] **J1.5.L4 Effective Java.** Item 1 "Consider static factory methods instead of constructors", Item 4 "Enforce noninstantiability with a private constructor", Item 15 "Minimize the accessibility of classes and members", Item 16 "In public classes, use accessor methods, not public fields", Item 24 "Favor static member classes over nonstatic".
- [ ] **J1.5.L5 New in 25.** JEP 513 "Flexible Constructor Bodies" — "Motivation" and "Description".

### Exercises (`java/J1.5-oop1/`)
- [ ] **Ex J1.5.1 BankAccount.** Class with private `id`, `owner`, `balanceCents` (`long`); constructor validates inputs; `deposit`, `withdraw` (reject overdraft), `getBalanceCents`. A `static` counter generates ids. *Acceptance:* the balance can't go negative through any public method; invalid constructor args throw `IllegalArgumentException`.
- [ ] **Ex J1.5.2 Init order.** A class with a static block, an instance block, a field initializer and two chained constructors that each print a line. *Acceptance:* you predict the print order for `new X()` twice before running.
- [ ] **Ex J1.5.3 Static factory.** Give a `Temperature` class a private constructor and static factories `ofCelsius`, `ofFahrenheit`. *Acceptance:* you can explain two advantages over public constructors.
- [ ] **Ex J1.5.4 Nested classes.** Implement a `LinkedStack` with a private static nested `Node` class, and an iterator as an inner class. *Acceptance:* you explain why `Node` should be static and the iterator can't be.
- [ ] **Ex J1.5.5 Utility class.** `MathUtils` with a private constructor and static methods. *Acceptance:* `new MathUtils()` does not compile outside the class.

### Must be able to do / explain
- [ ] Design a class that protects its invariants.
- [ ] Explain static vs instance members and when to use each.
- [ ] Explain all four uses of `final`.
- [ ] Explain the initialization order of a class and an object.
- [ ] Choose between static nested and inner classes.

**Estimated hours:** ~6 h

### Self-check questions
1. What is encapsulation and why use private fields with methods instead of public fields?
2. What is the difference between a static and an instance method? Can a static method use `this`?
3. What does `final` mean on a variable, a method and a class?
4. Does a `final` reference make the object immutable?
5. What happens if you write no constructor? What if you write one with parameters?
6. Static nested class vs inner class — what is the difference?
7. What is the order of initialization when you create the first instance of a class?

---

**Answers**
1. Hiding state behind methods so the class controls how it changes. It lets you enforce invariants (no negative balance), change the internal representation without breaking callers, and add validation/logging later.
2. A static method belongs to the class and has no instance; it can't use `this` or instance fields directly. Instance methods operate on a specific object.
3. Variable: can be assigned only once. Method: can't be overridden. Class: can't be subclassed.
4. No. The reference can't be reassigned, but the object it points to can still be mutated unless the class itself is immutable.
5. With no constructor, the compiler adds a public no-arg default constructor. Once you declare any constructor, no default is generated.
6. A static nested class has no link to an enclosing instance (like a top-level class scoped inside another). An inner class holds a hidden reference to an instance of the outer class, can access its fields, and can cause memory leaks if it outlives the outer object.
7. Static field initializers and static blocks (in textual order, once, when the class is initialized); then for each instance: superclass constructor chain, instance field initializers and instance blocks (textual order), then the constructor body.

---

## Module J1.6 — OOP II: inheritance, polymorphism, abstract classes, interfaces, default methods (~6h)

**Topics:** `extends`, single class inheritance; `super` calls; method
overriding rules (same signature, covariant return, can't reduce
visibility, `@Override`); dynamic dispatch / runtime polymorphism; upcasting,
downcasting, `instanceof`; `protected`; `Object` as the root; abstract classes
and abstract methods; interfaces, multiple interface inheritance, `default`,
`static` and `private` interface methods; the diamond problem with default
methods; composition over inheritance; fragile base class problem.

🐍 Python has multiple inheritance with MRO; Java has single class inheritance
+ multiple interfaces. Java interfaces ≈ `typing.Protocol`/ABCs, but nominal.

### Lessons
- [ ] **J1.6.L1 Inheritance.** dev.java/learn → "Inheritance" → "Inheritance", "Overriding and Hiding Methods", "Polymorphism", "Using the Keyword super", "Object as a Superclass", "Writing Final Classes and Methods", "Abstract Methods and Classes".
- [ ] **J1.6.L2 Interfaces.** dev.java/learn → "Interfaces" → "Interfaces", "Implementing an Interface", "Using an Interface as a Type", "Evolving Existing Interfaces" (default methods).
- [ ] **J1.6.L3 Book.** *Head First Java* ch.7 "Better Living in Objectville", ch.8 "Serious Polymorphism".
- [ ] **J1.6.L4 Effective Java.** Item 18 "Favor composition over inheritance", Item 19 "Design and document for inheritance or else prohibit it", Item 20 "Prefer interfaces to abstract classes", Item 21 "Design interfaces for posterity", Item 23 "Prefer class hierarchies to tagged classes".

### Exercises (`java/J1.6-oop2/`)
- [ ] **Ex J1.6.1 Shapes.** Abstract class `Shape` with abstract `area()` and `perimeter()`, subclasses `Circle`, `Rectangle`, `Square`. Store them in a `Shape[]` and print totals. *Acceptance:* no `instanceof` in the totals loop; `@Override` everywhere.
- [ ] **Ex J1.6.2 Interfaces.** Interfaces `Payable` (`amountDueCents()`) and `Printable`; `Invoice` implements both, `Employee` implements `Payable`. A payroll method takes `Payable[]`. *Acceptance:* you can explain why the method takes the interface type, not a class.
- [ ] **Ex J1.6.3 Default-method diamond.** Two interfaces with the same `default` method; a class implementing both. *Acceptance:* you resolve the compile error with `A.super.method()` and explain the rule.
- [ ] **Ex J1.6.4 Composition refactor.** Write `InstrumentedHashSet extends HashSet` that counts added elements (the classic Effective Java example), observe the wrong count with `addAll`, then rewrite it with composition/forwarding. *Acceptance:* the composition version counts correctly; you explain why inheritance broke.
- [ ] **Ex J1.6.5 Override rules.** Try to: reduce visibility of an overridden method, override a `static` method, override a `final` method, return a subtype. *Acceptance:* you note which compile and the rule behind each.

### Must be able to do / explain
- [ ] Explain dynamic dispatch and what "program to an interface" means.
- [ ] Choose between an abstract class and an interface.
- [ ] Explain overriding vs overloading vs hiding.
- [ ] Explain why composition is often better than inheritance.

**Estimated hours:** ~6 h

### Self-check questions
1. What is polymorphism in Java, and how does the JVM choose which method to run?
2. Overriding vs overloading — what is the difference?
3. Abstract class vs interface: when would you use each?
4. Why were default methods added to interfaces?
5. What happens when a class implements two interfaces with the same default method?
6. Why does Effective Java say "favor composition over inheritance"?
7. Can you override a static method?

---

**Answers**
1. The ability to use a subtype wherever a supertype is expected, with the actual object's overriding method called at run time (dynamic dispatch via the virtual method table), based on the object's runtime class, not the variable's declared type.
2. Overriding: same signature in a subclass, chosen at run time. Overloading: same name, different parameter lists, chosen at compile time from the static argument types.
3. Interface: define a capability/type that unrelated classes can implement; supports multiple inheritance of type. Abstract class: share state (fields) and implementation among closely related classes, with constructors; single inheritance only.
4. To evolve interfaces (e.g. add `Collection.stream()` in Java 8) without breaking every existing implementation.
5. Compile error: the class must override the method, optionally delegating to one of them with `InterfaceName.super.method()`.
6. Inheritance breaks encapsulation: the subclass depends on the superclass's implementation details (self-use of methods), so changes in the parent can silently break it. Composition + forwarding depends only on the public API.
7. No. A static method with the same signature in a subclass *hides* the parent's; which one runs depends on the declared type, not the object.

---

## Module J1.7 — equals / hashCode / toString contracts (~3h)

**Topics:** `Object` methods; the `equals` contract (reflexive, symmetric,
transitive, consistent, non-null); `hashCode` contract (equal objects ⇒ equal
hash codes); why breaking it breaks `HashMap`/`HashSet`; `Objects.equals`,
`Objects.hash`; `getClass()` vs `instanceof` in equals and the Liskov
problem; mutable fields in hash keys; `toString` for debugging; IDE and
record generation; `Comparable` consistency with equals (preview for J1.11).

🐍 Same idea as `__eq__` + `__hash__` in Python: define both or neither.

### Lessons
- [ ] **J1.7.L1 Effective Java.** Item 10 "Obey the general contract when overriding equals", Item 11 "Always override hashCode when you override equals", Item 12 "Always override toString".
- [ ] **J1.7.L2 Baeldung.** "Java equals() and hashCode() Contracts"; "Guide to hashCode() in Java".
- [ ] **J1.7.L3 dev.java.** dev.java/learn → "Inheritance" → "Object as a Superclass" (equals, hashCode, toString sections).

### Exercises (`java/J1.7-contracts/`)
- [ ] **Ex J1.7.1 Broken on purpose.** A `Point(x, y)` class that overrides `equals` but not `hashCode`. Put two equal points in a `HashSet`. *Acceptance:* you show the set contains both, then fix it and show it contains one.
- [ ] **Ex J1.7.2 Mutable key bug.** Use a mutable object as a `HashMap` key, mutate a field used in `hashCode`, then try `get`. *Acceptance:* you show the entry "disappears" and write down the rule you learned.
- [ ] **Ex J1.7.3 Symmetry trap.** `ColorPoint extends Point` with an extra `color` and `equals` using `instanceof`. *Acceptance:* you demonstrate the symmetry or transitivity violation and describe the two ways out (composition, or `getClass()` with its trade-off).
- [ ] **Ex J1.7.4 Contract tests.** Write a small `assertEqualsContract(a, b, c)` helper (plain `main` or JUnit later) checking reflexive, symmetric, transitive, null and hashCode rules for a `Money(amountCents, currency)` class. *Acceptance:* the helper catches a deliberately broken implementation.

### Must be able to do / explain
- [ ] State the equals and hashCode contracts from memory.
- [ ] Implement equals/hashCode correctly by hand and with `Objects`.
- [ ] Explain why hash keys should be immutable.

**Estimated hours:** ~3 h

### Self-check questions
1. What are the five properties of the `equals` contract?
2. What is the `hashCode` contract?
3. What goes wrong if you override `equals` but not `hashCode`?
4. Is it OK for two unequal objects to have the same hash code?
5. `instanceof` vs `getClass()` in `equals` — trade-offs?
6. Why is a mutable object a dangerous map key?

---

**Answers**
1. Reflexive (`x.equals(x)`), symmetric (`x.equals(y)` ⇔ `y.equals(x)`), transitive, consistent (same result while unchanged), and `x.equals(null)` is `false`.
2. Equal objects must have equal hash codes; the hash must stay the same while the fields used in equals don't change. Unequal objects *may* share a hash code.
3. Hash-based collections look in the bucket of the hash code first, so two "equal" objects with different hashes are treated as different: duplicates in a `HashSet`, failed `get` in a `HashMap`.
4. Yes, it's a collision. It is legal but hurts performance if frequent.
5. `instanceof` allows subclasses to be equal to the parent (Liskov-friendly) but makes symmetry hard when subclasses add fields. `getClass()` keeps symmetry but means a subclass is never equal to its parent, which breaks substitutability. Often the best answer: make the class `final` or use composition.
6. If a field used in `hashCode` changes after insertion, the entry sits in the wrong bucket and can't be found or removed.

---

## Module J1.8 — Exceptions: checked vs unchecked, try-with-resources, custom (~4h)

**Topics:** the `Throwable` hierarchy (`Error`, `Exception`,
`RuntimeException`); checked vs unchecked and the compiler's "catch or
declare" rule; `try`/`catch`/`finally`; multi-catch; `throw` vs `throws`;
exception chaining (`cause`); try-with-resources and `AutoCloseable`;
suppressed exceptions; custom exceptions; translating exceptions between
layers; anti-patterns (swallowing, catching `Exception` everywhere, using
exceptions for control flow); stack traces.

🐍 Python has only unchecked exceptions; `with` ≈ try-with-resources.

### Lessons
- [ ] **J1.8.L1 Exceptions.** dev.java/learn → "Exceptions" → "What Is an Exception?", "Catching and Handling Exceptions", "The try-with-resources Statement", "Specifying the Exceptions Thrown by a Method", "How to Throw Exceptions", "Unchecked Exceptions — The Controversy".
- [ ] **J1.8.L2 Book.** *Head First Java* ch.13 "Risky Behavior".
- [ ] **J1.8.L3 Effective Java.** Items 9 ("Prefer try-with-resources to try-finally"), 69–77 (use exceptions only for exceptional conditions; checked for recoverable, runtime for programming errors; avoid unnecessary checked exceptions; favor standard exceptions; throw exceptions appropriate to the abstraction; document; failure-capture information; failure atomicity; don't ignore exceptions).
- [ ] **J1.8.L4 Baeldung.** "Checked and Unchecked Exceptions in Java"; "Java – Try with Resources".

### Exercises (`java/J1.8-exceptions/`)
- [ ] **Ex J1.8.1 Hierarchy map.** Draw (ASCII in `notes.md`) the hierarchy with 3 examples in each branch: `Error`, checked, unchecked. *Acceptance:* includes `IOException`, `SQLException`, `NullPointerException`, `IllegalArgumentException`, `IllegalStateException`, `OutOfMemoryError`.
- [ ] **Ex J1.8.2 Custom exceptions.** For the `BankAccount` from J1.5, add `InsufficientFundsException`. Decide checked or unchecked and justify it in a comment. *Acceptance:* the message includes the balance and requested amount (failure-capture info).
- [ ] **Ex J1.8.3 try-with-resources.** Write a `Resource implements AutoCloseable` that prints on open/close and can throw in both the body and `close()`. *Acceptance:* you show the close order for two resources and how the `close()` exception appears as suppressed.
- [ ] **Ex J1.8.4 Exception translation.** A `ConfigLoader` that reads a file and throws your own `ConfigException` (with the `IOException` as cause). *Acceptance:* the printed stack trace shows "Caused by:".
- [ ] **Ex J1.8.5 finally surprises.** Methods where `finally` contains `return`, and where `try` returns a value that `finally` modifies. *Acceptance:* you predict and explain the results — and add a note why `return` in `finally` is banned in good code.

### Must be able to do / explain
- [ ] Explain checked vs unchecked and when to use each.
- [ ] Use try-with-resources for anything that must be closed.
- [ ] Wrap low-level exceptions with a meaningful cause.
- [ ] Recognise the main exception anti-patterns.

**Estimated hours:** ~4 h

### Self-check questions
1. What is the difference between checked and unchecked exceptions?
2. When should you use a checked exception, according to Effective Java?
3. How does try-with-resources work, and what are suppressed exceptions?
4. What is exception chaining and why is it useful?
5. Why is `catch (Exception e) {}` bad?
6. Should you catch `Error`s like `OutOfMemoryError`?

---

**Answers**
1. Checked exceptions (subclasses of `Exception` but not `RuntimeException`) must be caught or declared with `throws`; the compiler enforces it. Unchecked (`RuntimeException`, `Error`) need not be declared.
2. For conditions the caller can reasonably recover from (e.g. file not found, retryable failure). Programming errors (bad arguments, illegal state) should be unchecked.
3. Resources declared in the `try(...)` header must implement `AutoCloseable`; they are closed automatically in reverse order, even on exceptions. If both the body and `close()` throw, the body's exception propagates and the `close()` exceptions are attached as suppressed (`getSuppressed()`).
4. Wrapping a low-level exception as the `cause` of a higher-level one, so the API speaks its own abstraction but the root cause is preserved in the stack trace.
5. It swallows every failure silently, hides bugs, and leaves the program in an unknown state. Catch specific exceptions and handle, rethrow or at least log them.
6. Generally no. Errors signal problems the application usually can't recover from; let them propagate (maybe log at the top level).

---

## Module J1.9 — Enums, wrapper classes & autoboxing (~3h)

**Topics:** `enum` as a full class: fields, constructors, methods, abstract
methods per constant; `values()`, `valueOf()`, `ordinal()` (don't persist
it); `EnumSet`, `EnumMap`; enums in switch; enum singleton; wrapper classes
(`Integer`, `Long`, `Double`, …), autoboxing/unboxing; the `Integer` cache
(−128..127) and `==` trap; `NullPointerException` on unboxing; parsing
(`Integer.parseInt`, `valueOf`); `BigDecimal` and `BigInteger` basics
(rounding modes, `compareTo` vs `equals`).

🐍 Python's `enum.Enum` is similar; Python has no primitive/boxed split.

### Lessons
- [ ] **J1.9.L1 Enums.** dev.java/learn → "Enums"; javadoc of `EnumSet`, `EnumMap`.
- [ ] **J1.9.L2 Numbers.** dev.java/learn → "Numbers and Strings" → "Numbers", "Autoboxing and Unboxing".
- [ ] **J1.9.L3 Effective Java.** Items 34 ("Use enums instead of int constants"), 35 ("Use instance fields instead of ordinals"), 36 ("Use EnumSet instead of bit fields"), 37 ("Use EnumMap instead of ordinal indexing"), 61 ("Prefer primitive types to boxed primitives"), 60 ("Avoid float and double if exact answers are required").
- [ ] **J1.9.L4 BigDecimal.** Baeldung "BigDecimal and BigInteger in Java".

### Exercises (`java/J1.9-enums-wrappers/`)
- [ ] **Ex J1.9.1 Rich enum.** `enum Operation { PLUS("+"), MINUS("-"), TIMES("*"), DIVIDE("/") }` with a symbol field and an abstract `apply(double, double)` per constant. *Acceptance:* a loop over `values()` prints a table for two numbers; no switch on the enum needed.
- [ ] **Ex J1.9.2 State machine.** `enum OrderStatus` with allowed transitions (`canTransitionTo`) stored in an `EnumMap<OrderStatus, EnumSet<OrderStatus>>`. *Acceptance:* invalid transitions are rejected; you can explain why not to store `ordinal()` in a database.
- [ ] **Ex J1.9.3 Boxing traps.** Show `Integer a = 127, b = 127` vs `128` with `==`; unboxing a `null` `Integer`; a `Long` sum loop vs `long`. *Acceptance:* each result is explained; the loop is timed.
- [ ] **Ex J1.9.4 Money with BigDecimal.** Split 100.00 into 3 parts with `BigDecimal` so the parts sum exactly to 100.00. *Acceptance:* you use an explicit `RoundingMode` and explain why `new BigDecimal(0.1)` is wrong vs `new BigDecimal("0.1")`.

### Must be able to do / explain
- [ ] Use enums with fields, behavior, `EnumSet` and `EnumMap`.
- [ ] Explain autoboxing, the Integer cache and unboxing NPEs.
- [ ] Use `BigDecimal` correctly for money.

**Estimated hours:** ~3 h

### Self-check questions
1. Why are Java enums better than `int` constants?
2. Why shouldn't you persist `ordinal()`?
3. Why can `Integer a = 1000, b = 1000; a == b` be `false`?
4. When does autounboxing throw a `NullPointerException`?
5. Why is `new BigDecimal("2.0").equals(new BigDecimal("2.00"))` `false`?
6. What is an `EnumMap` and why is it fast?

---

**Answers**
1. Type safety (can't pass a random int), a namespace, printable names, the ability to add fields/methods/behavior, and use in switch with exhaustiveness checks.
2. It depends on declaration order; reordering or inserting a constant silently changes every stored value. Store the name or an explicit code field.
3. `==` compares references. Autoboxing uses `Integer.valueOf`, which caches −128..127; 1000 creates two different objects.
4. When a `null` wrapper is used where a primitive is needed: arithmetic, assignment to a primitive, a map value unboxed to `int`, etc.
5. `BigDecimal.equals` compares value **and** scale. Use `compareTo(...) == 0` to compare numeric value.
6. A map specialized for enum keys, backed by an array indexed by ordinal: compact, very fast, and iterates in declaration order.

---

## Module J1.10 — Generics: bounded types, wildcards, type erasure (~5h)

**Topics:** why generics (type safety, no casts); generic classes, interfaces
and methods; the diamond `<>`; bounded type parameters (`<T extends
Comparable<T>>`); wildcards `?`, `? extends T`, `? super T`; **PECS**
(producer-extends, consumer-super); invariance of generics vs covariance of
arrays; raw types (never); **type erasure** and its consequences (no `new T()`,
no `instanceof List<String>`, no primitive type args, bridge methods);
unchecked warnings; generic methods with type inference.

🐍 Like `typing.TypeVar` + `Generic`, except Java checks at compile time and
erases at run time (Python never enforces).

### Lessons
- [ ] **J1.10.L1 Generics.** dev.java/learn → "Generics" → "Introducing Generics", "Generic Types", "Generic Methods", "Bounded Type Parameters", "Generics, Inheritance, and Subtypes", "Wildcards", "Type Erasure", "Restriction on Generics".
- [ ] **J1.10.L2 Effective Java.** Items 26 ("Don't use raw types"), 27 ("Eliminate unchecked warnings"), 28 ("Prefer lists to arrays"), 29 ("Favor generic types"), 30 ("Favor generic methods"), 31 ("Use bounded wildcards to increase API flexibility").
- [ ] **J1.10.L3 Baeldung.** "Type Erasure in Java Explained"; "Generics in Java" (wildcards section).

### Exercises (`java/J1.10-generics/`)
- [ ] **Ex J1.10.1 Generic container.** `Pair<A, B>` and `Box<T>` with a `map(Function<T,R>)` method (you may write your own tiny functional interface until J2.1). *Acceptance:* no casts in client code; `Box<int>` is rejected and you explain why.
- [ ] **Ex J1.10.2 Bounded max.** `static <T extends Comparable<? super T>> T max(List<? extends T> list)`. *Acceptance:* works for `List<Integer>`, `List<String>`, and a subclass whose parent implements `Comparable`; you explain each wildcard.
- [ ] **Ex J1.10.3 PECS copy.** `static <T> void copy(List<? super T> dst, List<? extends T> src)`. *Acceptance:* copying `List<Integer>` into `List<Number>` compiles; the reverse doesn't; comment explains PECS.
- [ ] **Ex J1.10.4 Erasure evidence.** Show that `new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass()`; try `instanceof List<String>` and `new T[]`. *Acceptance:* the compile errors are recorded and explained.
- [ ] **Ex J1.10.5 Arrays vs generics.** Store an `Integer` into an `Object[]` that is really a `String[]` (runtime `ArrayStoreException`), and try the same with `List<Object>`/`List<String>` (compile error). *Acceptance:* you explain covariant arrays vs invariant generics.

### Must be able to do / explain
- [ ] Write generic classes and methods with bounds.
- [ ] Apply PECS to choose `extends` vs `super`.
- [ ] Explain type erasure and three things it forbids.

**Estimated hours:** ~5 h

### Self-check questions
1. Why is `List<Integer>` not a subtype of `List<Number>`?
2. What does PECS mean? Give an example from the JDK.
3. What is type erasure?
4. Why can't you create `new T()` or `new T[10]`?
5. Why are raw types dangerous?
6. `List<?>` vs `List<Object>` — what is the difference?

---

**Answers**
1. Generics are invariant. If it were a subtype, you could add a `Double` to a `List<Number>` view of a `List<Integer>` and corrupt it.
2. Producer-Extends, Consumer-Super: use `? extends T` when the structure only produces (you read T), `? super T` when it only consumes (you write T). Example: `Collections.copy(List<? super T> dest, List<? extends T> src)`, `Comparator<? super T>`.
3. The compiler checks generic types and then removes them, replacing type parameters with their bounds (or `Object`) and inserting casts; at run time `List<String>` and `List<Integer>` are the same class.
4. Because `T` is erased, the runtime doesn't know which class to instantiate. Workarounds: pass a `Class<T>`, a `Supplier<T>`, or use `List<T>`.
5. They switch off generic type checking: you can put anything in and get a `ClassCastException` far away from the bug.
6. `List<?>` is a list of some unknown type — you can read `Object`s but can't add anything but `null`. `List<Object>` is a list of exactly Objects — you can add anything, but a `List<String>` is not assignable to it.

---

## Module J1.11 — Collections Framework + iterators (~10h)

**Topics:** the interface hierarchy (`Iterable` → `Collection` → `List`,
`Set`, `Queue`/`Deque`; separate `Map`); sequenced collections (JEP 431, Java
21: `SequencedCollection`, `getFirst/getLast/reversed`); implementations:
`ArrayList` vs `LinkedList` (and why `ArrayList`/`ArrayDeque` almost always
win), `HashSet`/`LinkedHashSet`/`TreeSet`, `HashMap`/`LinkedHashMap`/`TreeMap`,
`ArrayDeque`, `PriorityQueue`; **HashMap internals** (array of buckets,
hash spreading, load factor 0.75, resize, treeification of long buckets to
red-black trees in Java 8+); `TreeMap` (red-black tree, `NavigableMap`:
`floorKey`, `ceilingKey`, `headMap`, `subMap`); `Comparable` vs `Comparator`
(`comparing`, `thenComparing`, `reversed`, `nullsFirst`); `Iterator`,
`ListIterator`, fail-fast iterators and `ConcurrentModificationException`,
`removeIf`; immutable collections (`List.of`, `Map.of`, `copyOf`) vs
unmodifiable views; `Collections` utilities; big-O of each operation.

🐍 `list` ≈ `ArrayList`, `dict` ≈ `LinkedHashMap` (insertion-ordered),
`set` ≈ `HashSet`, `collections.deque` ≈ `ArrayDeque`, `heapq` ≈
`PriorityQueue`.

### Lessons
- [ ] **J1.11.L1 Overview.** dev.java/learn → "The Collections Framework" → "Getting to Know the Collection Hierarchy", "Storing Elements in a Collection", "Iterating over the Elements of a Collection", "Extending Collection with List", "Extending Collection with Set, SortedSet and NavigableSet", "Storing Elements in Stacks and Queues", "Using Maps to Store Key Value Pairs", "Managing the Content of a Map", "Keeping Keys Sorted with SortedMap and NavigableMap", "Choosing Immutable Types for Your Key".
- [ ] **J1.11.L2 Book.** *Head First Java* ch.11 "Data Structures" (Collections and generics); ch.6 "Using the Java Library" (ArrayList).
- [ ] **J1.11.L3 HashMap internals.** Baeldung "A Guide to Java HashMap" (internals section); read the implementation notes at the top of the `java.util.HashMap` source (JDK on GitHub: openjdk/jdk).
- [ ] **J1.11.L4 Sorting and ordering.** dev.java/learn → "The Collections Framework" → "Sorting and Ordering" (or Baeldung "Comparator and Comparable in Java"); Effective Java Item 14 "Consider implementing Comparable".
- [ ] **J1.11.L5 New in 21.** JEP 431 "Sequenced Collections".
- [ ] **J1.11.L6 Immutable collections.** Effective Java Item 54 "Return empty collections or arrays, not nulls"; javadoc "Unmodifiable Lists/Sets/Maps" sections of `List`, `Set`, `Map`.

### Exercises (`java/J1.11-collections/`)
- [ ] **Ex J1.11.1 Choose the right collection.** For 8 scenarios (unique tags, insertion-ordered cache, leaderboard sorted by score, FIFO job queue, LIFO undo stack, "next event after time t", counting words, top-k smallest) write down the interface + implementation and the big-O of the main operation. *Acceptance:* a table in `notes.md` and one small program per three scenarios.
- [ ] **Ex J1.11.2 Word frequency.** Read a text file (use `Files.readString` as a preview — or a hard-coded string), count words with a `HashMap`, then print the top 10 by count, ties alphabetically, with a `Comparator` chain. *Acceptance:* uses `merge` or `getOrDefault`; no manual sorting algorithm.
- [ ] **Ex J1.11.3 ArrayList vs LinkedList vs ArrayDeque.** Time 100 000 inserts at the head, at the tail, and random `get(i)` for each. *Acceptance:* results in a table; you explain them with the data structures (cache locality, node overhead).
- [ ] **Ex J1.11.4 Mini HashMap.** Implement a generic `SimpleHashMap<K, V>` with separate chaining, resize at 0.75, and `put/get/remove/size`. *Acceptance:* passes a test that inserts 10 000 keys and checks all of them; you can explain how the real `HashMap` differs (hash spreading, treeification).
- [ ] **Ex J1.11.5 Fail-fast.** Remove elements from a `List` inside an enhanced for loop and observe `ConcurrentModificationException`; fix it three ways (`Iterator.remove`, `removeIf`, collect-then-remove). *Acceptance:* all three fixes produce the same result.
- [ ] **Ex J1.11.6 NavigableMap.** Model a price list where prices change on dates: `TreeMap<LocalDate, BigDecimal>` (or `Integer` day numbers until J1.12) and answer "price on date X" with `floorEntry`. *Acceptance:* correct results for dates before the first entry, exactly on an entry, and between entries.

### Must be able to do / explain
- [ ] Pick the right collection for a problem and state its complexity.
- [ ] Explain how `HashMap` works internally, including resize and treeification.
- [ ] Explain `ArrayList` vs `LinkedList` and why `LinkedList` is rarely right.
- [ ] Write `Comparator` chains and explain `Comparable` vs `Comparator`.
- [ ] Explain fail-fast iterators and immutable vs unmodifiable collections.

**Estimated hours:** ~10 h

### Self-check questions
1. How does `HashMap.put` work internally?
2. What happens when a `HashMap` grows beyond its threshold?
3. What is treeification and why was it added in Java 8?
4. `ArrayList` vs `LinkedList`: complexity of `get(i)`, add at end, add at front?
5. `HashMap` vs `LinkedHashMap` vs `TreeMap` — when do you use each?
6. `Comparable` vs `Comparator`?
7. What causes `ConcurrentModificationException` in single-threaded code?
8. `List.of(...)` vs `Collections.unmodifiableList(list)`?
9. Why can't `HashMap` keys be relied on if they are mutable?
10. What is a `Deque`, and why prefer `ArrayDeque` over `Stack`?

---

**Answers**
1. It computes `key.hashCode()`, spreads the bits (`h ^ (h >>> 16)`), takes `hash & (n-1)` as the bucket index, then walks the bucket's nodes comparing hash and `equals`: replace the value if found, otherwise append a node. Null key goes to bucket 0.
2. When size exceeds capacity × load factor (default 16 × 0.75), the table doubles and entries are redistributed. Each entry either stays at the same index or moves to index + old capacity.
3. When a bucket holds more than 8 entries (and the table has ≥ 64 buckets), the linked list becomes a red-black tree, so worst-case lookup in that bucket is O(log n) instead of O(n) — protection against many collisions and hash-flooding attacks.
4. `ArrayList`: `get` O(1), add at end amortized O(1), add at front O(n). `LinkedList`: `get` O(n), add at both ends O(1). In practice `ArrayList`/`ArrayDeque` usually win because of memory locality and lower per-element overhead.
5. `HashMap` — fastest, no order. `LinkedHashMap` — insertion (or access) order, e.g. LRU caches. `TreeMap` — sorted keys and range/nearest queries, O(log n).
6. `Comparable` defines the class's natural order (`compareTo`, one per class). A `Comparator` is an external strategy; you can have many and build them with `Comparator.comparing(...).thenComparing(...)`.
7. Structurally modifying a collection while iterating over it with a fail-fast iterator (e.g. `list.remove` in a for-each loop). The iterator detects the changed `modCount`.
8. `List.of` creates a truly immutable list (and rejects nulls). `unmodifiableList` is a read-only *view*: changes to the underlying list are still visible through it.
9. The entry's bucket is chosen from the hash at insertion; if the key's hash changes, lookups go to a different bucket and the entry is lost.
10. A double-ended queue (add/remove at both ends); usable as a stack or queue. `Stack` extends the synchronized legacy `Vector`, which is slower and exposes random access that breaks the stack abstraction.

---

## Module J1.12 — I/O, NIO.2, java.time (~5h)

**Topics:** byte streams vs character streams; `InputStream`/`OutputStream`,
`Reader`/`Writer`, buffering; charsets (always specify UTF-8);
`BufferedReader.readLine`; NIO.2: `Path`, `Paths`/`Path.of`, `Files`
(`readString`, `readAllLines`, `lines`, `write`, `newBufferedReader`,
`walk`, `createDirectories`, `copy`, `move`, `delete`), exceptions
(`NoSuchFileException`); closing streams returned by `Files.lines`/`walk`;
serialization overview (and why to avoid Java serialization);
**java.time**: `LocalDate`, `LocalTime`, `LocalDateTime`, `Instant`,
`ZonedDateTime`, `OffsetDateTime`, `ZoneId`, `Duration` vs `Period`,
`DateTimeFormatter`, `YearMonth`, `TemporalAdjusters`; why
`java.util.Date`/`Calendar` are legacy; DST pitfalls; storing `Instant` (UTC)
vs local dates.

🐍 `pathlib.Path` ≈ `Path` + `Files`; `datetime` aware/naive ≈
`ZonedDateTime`/`LocalDateTime`.

### Lessons
- [ ] **J1.12.L1 Java I/O.** dev.java/learn → "Java I/O API" → "Accessing Resources using Paths", "Working with Paths", "Reading and Writing Small Files", "Reading and Writing Text Files", "Reading and Writing Binary Files", "Manipulating Files and Directories", "Walking the File Tree".
- [ ] **J1.12.L2 Date & time.** dev.java/learn → "The Date Time API" (all pages: overview, standard calendar, `DayOfWeek`/`Month`, date classes, date-time classes, time zone and offset classes, instant, parsing and formatting, temporal adjusters, period and duration).
- [ ] **J1.12.L3 Book.** *Modern Java in Action*, 2nd ed., ch.12 "New Date and Time API"; *Head First Java* ch.16 "Saving Objects (and Text)".
- [ ] **J1.12.L4 Effective Java.** Item 85 "Prefer alternatives to Java serialization" (read the argument only).

### Exercises (`java/J1.12-io-time/`)
- [ ] **Ex J1.12.1 CSV reader.** Read a CSV file of transactions (`date,category,amountCents,description`) with `Files.newBufferedReader(path, UTF_8)` into a list of objects; report and skip malformed lines with line numbers. *Acceptance:* a file with 2 bad lines out of 20 loads 18 records and prints 2 warnings.
- [ ] **Ex J1.12.2 Directory report.** Walk a directory tree with `Files.walk` and print the 10 largest files and total size per extension. *Acceptance:* the stream is closed with try-with-resources; symlink loops are not followed.
- [ ] **Ex J1.12.3 Safe write.** Write a report to a temp file in the same directory, then atomically move it over the target (`ATOMIC_MOVE`). *Acceptance:* you can explain why this prevents a half-written file.
- [ ] **Ex J1.12.4 Time zones.** Schedule a meeting at 09:00 in Tashkent and print it in UTC, New York and Berlin, for a date in January and one in July. *Acceptance:* DST differences are visible and explained.
- [ ] **Ex J1.12.5 Month boundaries.** Given a `YearMonth`, print the first/last day, the number of working days (Mon–Fri) and the last Friday. *Acceptance:* correct for February in a leap year.
- [ ] **Ex J1.12.6 Duration vs Period.** Compute the age in years/months/days between two dates (`Period`) and hours between two instants (`Duration`). *Acceptance:* you explain why "one day" is not always 24 hours in a zone with DST.

### Must be able to do / explain
- [ ] Read and write text files with NIO.2 and explicit charsets.
- [ ] Always close streams/readers with try-with-resources.
- [ ] Choose between `LocalDate`, `LocalDateTime`, `Instant` and `ZonedDateTime`.
- [ ] Format and parse dates; handle time zones and DST.

**Estimated hours:** ~5 h

### Self-check questions
1. Byte streams vs character streams — when do you use each?
2. Why should you always specify a charset?
3. Why must the stream from `Files.lines` be closed?
4. `LocalDateTime` vs `Instant` vs `ZonedDateTime`?
5. `Duration` vs `Period`?
6. What would you store in a database for "when did this payment happen"?
7. Why is `java.util.Date` considered legacy?

---

**Answers**
1. Byte streams for binary data (images, zip); character streams (Readers/Writers) for text, which involves decoding bytes into characters with a charset.
2. Otherwise the platform default is used, which can differ between machines and corrupt non-ASCII text. (Since Java 18 the default is UTF-8 — JEP 400 — but being explicit is still good practice for portability and clarity.)
3. It holds an open file handle and reads lazily; not closing it leaks file descriptors.
4. `LocalDateTime` has no time zone (a wall-clock time). `Instant` is a point on the UTC timeline. `ZonedDateTime` is a local date-time in a specific zone with its rules (DST).
5. `Duration` is time-based (seconds/nanos), `Period` is date-based (years/months/days). Adding `Period.ofDays(1)` keeps the wall-clock time across DST; `Duration.ofHours(24)` does not.
6. An `Instant` (e.g. `TIMESTAMP WITH TIME ZONE` / UTC), because it is unambiguous. Convert to a zone only for display.
7. It is mutable, not thread-safe, has confusing APIs (months from 0, years from 1900), mixes date and time, and is a timestamp pretending to be a date.

---

## Module J1.13 — First build & tests: Maven basics + JUnit 5 basics (~3h)

**Topics:** why a build tool; Maven coordinates (`groupId`, `artifactId`,
`version`); standard directory layout (`src/main/java`, `src/test/java`);
`pom.xml` basics; dependencies from Maven Central; `maven.compiler.release`;
`mvn compile`, `test`, `package`, `clean`; the Maven wrapper (`mvnw`);
JUnit 5 (Jupiter): `@Test`, `assertEquals`, `assertThrows`,
`@BeforeEach`, `@DisplayName`; running tests from IntelliJ and Maven
(Surefire). Deeper Maven/Gradle comes in J4.1, deeper testing in J4.2.

🐍 `pom.xml` ≈ `pyproject.toml`; Maven Central ≈ PyPI; `mvn test` ≈ `pytest`.

### Lessons
- [ ] **J1.13.L1 Maven.** maven.apache.org → "Maven in 5 Minutes"; "Introduction to the Standard Directory Layout".
- [ ] **J1.13.L2 Maven wrapper.** maven.apache.org → "Maven Wrapper" (mvnw).
- [ ] **J1.13.L3 JUnit 5.** JUnit 5 User Guide → "Writing Tests" → "Annotations", "Test Classes and Methods", "Assertions".
- [ ] **J1.13.L4 IDE.** IntelliJ IDEA docs → "Maven" (create/import a Maven project) and "Testing" → "JUnit".

### Exercises (`java/J1.13-maven-junit/`)
- [ ] **Ex J1.13.1 First Maven project.** Create a project with `mvn archetype:generate` (quickstart) or by hand; set `maven.compiler.release` to 25 (or 21); add the Maven wrapper. *Acceptance:* `./mvnw clean package` builds a jar and runs tests.
- [ ] **Ex J1.13.2 Port earlier code.** Move the `BankAccount` (J1.5/J1.8) and `SimpleHashMap` (J1.11) into the project. *Acceptance:* they compile under `src/main/java` with proper packages.
- [ ] **Ex J1.13.3 First tests.** Write JUnit 5 tests for `BankAccount` (happy path, overdraft throws, invalid constructor args) and `SimpleHashMap` (put/get/remove/resize). *Acceptance:* at least 10 tests, all green with `./mvnw test`; one test deliberately failing first, then fixed.
- [ ] **Ex J1.13.4 Runnable jar.** Configure the main class so `java -jar target/*.jar` runs your `main`. *Acceptance:* works from the command line, not just from the IDE.

### Must be able to do / explain
- [ ] Create a Maven project with the standard layout and wrapper.
- [ ] Add a dependency and run `mvn test`/`package`.
- [ ] Write basic JUnit 5 tests with `assertThrows`.

**Estimated hours:** ~3 h

### Self-check questions
1. What are Maven coordinates?
2. What is the standard Maven directory layout?
3. What does `mvn package` do, in terms of phases?
4. Why commit the Maven wrapper?
5. How do you test that a method throws an exception in JUnit 5?

---

**Answers**
1. `groupId:artifactId:version` (plus optional packaging/classifier), which uniquely identify an artifact in a repository.
2. Production code in `src/main/java`, resources in `src/main/resources`, tests in `src/test/java`, test resources in `src/test/resources`, output in `target/`.
3. It runs the lifecycle phases up to `package`: validate, compile, test (after compiling tests), then package (jar).
4. Everyone (and CI) uses the same Maven version without installing it; `./mvnw` downloads it.
5. `assertThrows(ExpectedException.class, () -> code())`, which returns the exception so you can assert on its message.

---

## Project JP1 — LedgerLite CLI · Junior (~25h)

### Goal
Build a **command-line personal expense and budget tracker** in plain Java —
no frameworks. It proves you can model a small domain with classes, enums and
records-free "classic" Java (records come in Part 2), use the Collections
Framework well, read/write files with NIO.2, handle dates correctly with
`java.time`, and test your code with JUnit.

### Features
- [ ] Add a transaction: date, amount (integer minor units or `BigDecimal`), type (`EXPENSE`/`INCOME` enum), category, optional note.
- [ ] Categories are managed in the app (add/rename/list); renaming updates existing transactions.
- [ ] List transactions with filters: date range, category, type; sorted by date or amount (Comparator chains).
- [ ] Monthly budget per category (`YearMonth` → category → limit).
- [ ] Monthly report: income, expenses, net, per-category totals, % of budget used, over-budget categories highlighted.
- [ ] Yearly summary: 12 months × totals, best and worst month.
- [ ] Recurring transactions (monthly on day N; if the month is shorter, use its last day).
- [ ] Persistence in CSV files under a data directory (`transactions.csv`, `budgets.csv`, `categories.csv`), loaded on start and saved on change with an atomic temp-file-and-move.
- [ ] Import a bank-style CSV with a different column order and date format; bad rows are reported, not fatal.
- [ ] Undo the last command (a `Deque` of commands).
- [ ] Simple interactive menu **or** subcommands (`ledgerlite add …`, `ledgerlite report 2026-09`).

### Tech stack
| Tool / concept | Taught in |
|---|---|
| Java 25 (or 21), `javac`/`java`, IntelliJ | J1.1 |
| Types, control flow, arrays, `printf` | J1.2 |
| Strings, `StringBuilder`, parsing input | J1.3 |
| Packages, access modifiers | J1.4 |
| Classes, encapsulation, static factories | J1.5 |
| Interfaces (e.g. `Command`, `Report`), polymorphism | J1.6 |
| `equals`/`hashCode` for value classes (Money, Category) | J1.7 |
| Custom exceptions, try-with-resources | J1.8 |
| Enums (`TransactionType`, command names), `BigDecimal` or `long` cents | J1.9 |
| Generics (e.g. a generic `Repository<T, ID>` interface) | J1.10 |
| `ArrayList`, `HashMap`, `TreeMap`, `EnumMap`, `ArrayDeque`, Comparators | J1.11 |
| NIO.2 (`Path`, `Files`), UTF-8, atomic move; `java.time` (`LocalDate`, `YearMonth`, `DateTimeFormatter`) | J1.12 |
| Maven + wrapper, JUnit 5 | J1.13 |

### Required knowledge
J1.1–J1.13. Optional but helpful: Track 1A.8 (you already know *why* tests
matter), 1B Module 1 (hashing).

### Milestones
- [ ] **M1 — Domain model (≈5 h).** Packages (`domain`, `storage`, `cli`, `report`); `Money`/amount handling, `Category`, `Transaction`, `TransactionType`, `Budget`; invariants validated in constructors; `equals`/`hashCode` where needed. Unit tests for the domain. *Tag:* `v0.1-domain`.
- [ ] **M2 — Storage (≈5 h).** CSV read/write for all three files; atomic save; malformed-line reporting; a `Repository` interface with an in-memory and a CSV implementation. Tests use a temp directory (`@TempDir`). *Tag:* `v0.2-storage`.
- [ ] **M3 — Commands & CLI (≈5 h).** Add/list/filter/sort, category management, budgets; command objects with undo via `Deque`. *Tag:* `v0.3-cli`.
- [ ] **M4 — Reports & dates (≈6 h).** Monthly and yearly reports, over-budget detection, recurring transactions with the "short month" rule, bank CSV import with another date format. Tests for month boundaries and leap years. *Tag:* `v0.4-reports`.
- [ ] **M5 — Polish (≈4 h).** README (how to run, file format, design decisions), runnable jar, error messages for every bad input, at least 40 tests. *Tag:* `v1.0-ledgerlite`.

### Definition of done
- [ ] `./mvnw clean package` builds a runnable jar; `java -jar` runs it.
- [ ] No `double`/`float` for money anywhere.
- [ ] All file access uses NIO.2 with explicit UTF-8 and try-with-resources.
- [ ] Saving is atomic (a crash never leaves a half-written file).
- [ ] At least 40 JUnit tests, including month-boundary, leap-year and malformed-CSV cases; all green.
- [ ] No `static` mutable global state except constants; no `catch (Exception e) {}`.
- [ ] README explains the collection choices (why `TreeMap` here, `EnumMap` there).

**Estimated hours:** ~25 h

### Interview questions about this project
1. Why did you store money as `long` cents (or `BigDecimal`) and not `double`?
2. Which collections did you use for transactions, budgets and undo, and why?
3. How do you make saving to a file crash-safe?
4. How did you handle a recurring transaction on the 31st in a 30-day month?
5. How would you change the design if the data moved from CSV to a database?

---

**Answers (short)**
1. `double` can't represent most decimal fractions exactly, so sums drift (e.g. 0.1 + 0.2). Integer cents or `BigDecimal` with explicit rounding give exact results.
2. Example answer: `ArrayList` for the transaction list (ordered, fast iteration), `TreeMap<LocalDate, …>` or sorting with Comparators for date queries, `Map<YearMonth, EnumMap/Map<Category, Money>>` for budgets, `ArrayDeque` as the undo stack.
3. Write to a temp file in the same directory, flush/close it, then `Files.move` with `ATOMIC_MOVE` (and `REPLACE_EXISTING`). The target is either the old or the new complete file.
4. Clamp to the month's last day: `yearMonth.atDay(Math.min(day, yearMonth.lengthOfMonth()))`, with tests for February and leap years.
5. The `Repository` interface stays; add a JDBC implementation (Part 5). CLI and reports don't change because they depend on the interface, not on CSV.

---

# Part 2 — Modern & advanced Java (~37 h)

**Main resources for Part 2:**
- *Modern Java in Action*, 2nd ed. (Urma, Fusco, Mycroft).
- *Effective Java*, 3rd ed.
- dev.java/learn and the JEP pages on openjdk.org/jeps.

---

## Module J2.1 — Lambdas, functional interfaces, method references (~5h)

**Topics:** behavior parameterization; anonymous classes vs lambdas; lambda
syntax; target typing; functional interfaces and `@FunctionalInterface`; the
`java.util.function` family (`Function`, `BiFunction`, `Supplier`,
`Consumer`, `Predicate`, `UnaryOperator`, `BinaryOperator`, primitive
specializations like `IntPredicate`); composing (`andThen`, `compose`,
`Predicate.and/or/negate`, `Comparator.comparing`); effectively final
captured variables; four kinds of method references (static, bound,
unbound, constructor); `this` inside a lambda vs anonymous class.

🐍 Python lambdas are single expressions and functions are objects; Java
lambdas are instances of a functional interface.

### Lessons
- [ ] **J2.1.L1 Book.** *Modern Java in Action* ch.2 "Passing code with behavior parameterization", ch.3 "Lambda expressions".
- [ ] **J2.1.L2 dev.java.** dev.java/learn → "Lambda Expressions" → "Writing Your First Lambda Expression", "Using Lambdas Expressions in Your Application", "Writing Lambda Expressions as Method References", "Combining Lambda Expressions", "Writing and Combining Comparators".
- [ ] **J2.1.L3 Effective Java.** Item 42 "Prefer lambdas to anonymous classes", Item 43 "Prefer method references to lambdas", Item 44 "Favor the use of standard functional interfaces".
- [ ] **J2.1.L4 Book.** *Head First Java* ch.12 "Lambdas and Streams: What, Not How" (first half).

### Exercises (`java/J2.1-lambdas/`)
- [ ] **Ex J2.1.1 Anonymous → lambda → method ref.** Sort a list of `Person` by age three ways: anonymous `Comparator`, lambda, `Comparator.comparing(Person::getAge)`. *Acceptance:* all three sort identically; you explain what the compiler infers.
- [ ] **Ex J2.1.2 Custom filter.** Write `static <T> List<T> filter(List<T> xs, Predicate<? super T> p)` and use it with composed predicates (`and`, `negate`). *Acceptance:* no loops in client code; one predicate built from two others.
- [ ] **Ex J2.1.3 Validation pipeline.** A `Validator<T>` functional interface returning a list of errors; combine several with a default method `and`. *Acceptance:* validates a `SignupForm` (email, password length, age) and reports all errors at once.
- [ ] **Ex J2.1.4 Method reference kinds.** Write one example of each of the four kinds and label it. *Acceptance:* `notes.md` explains the difference between `String::length` (unbound) and `str::length` (bound).
- [ ] **Ex J2.1.5 Capture rules.** Try to modify a local variable inside a lambda; then use an `AtomicInteger` or a better design. *Acceptance:* you explain "effectively final" and why mutation from lambdas is a smell.

### Must be able to do / explain
- [ ] Write lambdas and method references for standard functional interfaces.
- [ ] Explain what a functional interface is and target typing.
- [ ] Compose functions, predicates and comparators.
- [ ] Explain the effectively-final rule.

**Estimated hours:** ~5 h

### Self-check questions
1. What is a functional interface? Give four from `java.util.function`.
2. Why must captured local variables be effectively final?
3. What are the four kinds of method references?
4. How does `this` differ inside a lambda and inside an anonymous class?
5. Why do primitive specializations like `IntPredicate` exist?
6. When is a lambda better than a method reference, and vice versa?

---

**Answers**
1. An interface with exactly one abstract method, so a lambda can implement it. `Function<T,R>`, `Supplier<T>`, `Consumer<T>`, `Predicate<T>` (also `BiFunction`, `UnaryOperator`, `BinaryOperator`).
2. Lambdas capture the *value* of local variables (locals live on the stack and may be gone when the lambda runs). Requiring effectively final avoids confusing semantics and data races.
3. Static (`Integer::parseInt`), bound instance (`str::length`), unbound instance of an arbitrary object (`String::length`), constructor (`ArrayList::new`).
4. In a lambda, `this` refers to the enclosing instance (lambdas don't introduce a new scope). In an anonymous class, `this` is the anonymous class instance.
5. To avoid boxing/unboxing overhead for `int`, `long`, `double`.
6. A method reference is clearer when it names an existing method directly. A lambda is clearer when the method name is long or needs extra arguments, or the logic is tiny and obvious inline (Item 43: use whichever is shorter and clearer).

---

## Module J2.2 — Streams API & Optional (~8h)

**Topics:** streams vs collections (lazy, single-use, internal iteration);
sources (`Collection.stream`, `Stream.of`, `IntStream.range`, `Files.lines`);
intermediate ops (`filter`, `map`, `flatMap`, `distinct`, `sorted`, `limit`,
`skip`, `peek`, `takeWhile`, `dropWhile`, `mapMulti`); terminal ops
(`collect`, `toList()`, `reduce`, `count`, `anyMatch`, `findFirst`,
`forEach`); primitive streams and `summaryStatistics`; **collectors**:
`toMap` (merge function, duplicate keys!), `groupingBy` with downstream
collectors (`counting`, `summingLong`, `mapping`, `toSet`), `partitioningBy`,
`joining`, `teeing`, `collectingAndThen`; stateful vs stateless ops;
side-effect-free lambdas; **parallel streams**: fork/join common pool, when
they help (large CPU-bound, splittable sources) and pitfalls (shared mutable
state, blocking I/O, `LinkedList` sources, ordering cost); **Optional**:
creation, `map`/`flatMap`/`filter`, `orElse` vs `orElseGet` vs
`orElseThrow`, don't use for fields/parameters/collections; Gatherers
(JEP 485, final in Java 24) — overview only.

🐍 Streams ≈ generator pipelines + `itertools`; `groupingBy` ≈
`itertools.groupby`/`defaultdict(list)`; `Optional` ≈ `T | None` made explicit.

### Lessons
- [ ] **J2.2.L1 Book.** *Modern Java in Action* ch.4 "Introducing streams", ch.5 "Working with streams", ch.6 "Collecting data with streams", ch.7 "Parallel data processing and performance".
- [ ] **J2.2.L2 dev.java.** dev.java/learn → "The Stream API" (all pages: processing data in memory, intermediate operations, terminal operations, reducing, collectors, custom collectors, parallel streams, Optional).
- [ ] **J2.2.L3 Optional.** *Modern Java in Action* ch.11 "Using Optional as a better alternative to null"; Effective Java Item 55 "Return optionals judiciously".
- [ ] **J2.2.L4 Effective Java.** Item 45 "Use streams judiciously", Item 46 "Prefer side-effect-free functions in streams", Item 47 "Prefer Collection to Stream as a return type", Item 48 "Use caution when making streams parallel".
- [ ] **J2.2.L5 Gatherers (overview).** JEP 485 "Stream Gatherers" — "Summary" and "Motivation".

### Exercises (`java/J2.2-streams/`)
- [ ] **Ex J2.2.1 Loop → stream.** Rewrite 6 loop-based methods from LedgerLite (JP1) or J1.11 as streams. *Acceptance:* same output; for one of them you argue the loop was clearer and keep it (Item 45).
- [ ] **Ex J2.2.2 Report with collectors.** Given a list of `Order(customer, city, items, totalCents, date)`: revenue per city, top 3 customers, orders per month (`YearMonth`), average basket per city, cities partitioned by revenue > X, comma-joined customer names per city. *Acceptance:* each is a single stream pipeline; `toMap` with duplicates handled by a merge function.
- [ ] **Ex J2.2.3 flatMap.** From a list of orders with item lists, produce the distinct set of product SKUs and the 5 most-sold products. *Acceptance:* uses `flatMap` and `groupingBy(..., counting())`.
- [ ] **Ex J2.2.4 Parallel experiment.** Sum of squares of 1..50 000 000 with sequential and parallel `LongStream`, and a parallel stream that adds to a shared `ArrayList`. *Acceptance:* timings recorded; the shared-list version shows lost elements or an exception; you explain both.
- [ ] **Ex J2.2.5 Optional refactor.** Replace `null` returns in a `UserRepository.findByEmail` with `Optional`, and chain `map`/`filter`/`orElseThrow` in the caller. *Acceptance:* no `optional.get()` without a check; you explain `orElse(expensiveCall())` vs `orElseGet(...)`.
- [ ] **Ex J2.2.6 Laziness.** Use `peek` to print when elements are processed in `filter → map → findFirst` over 1 000 elements. *Acceptance:* you show that only a few elements are processed and explain why.

### Must be able to do / explain
- [ ] Write pipelines with `map`, `filter`, `flatMap`, `sorted`, `collect`.
- [ ] Use `groupingBy`/`partitioningBy`/`toMap` with downstream collectors.
- [ ] Explain laziness, short-circuiting and single-use streams.
- [ ] Explain when parallel streams help and when they hurt.
- [ ] Use `Optional` correctly as a return type only.

**Estimated hours:** ~8 h

### Self-check questions
1. How is a stream different from a collection?
2. What is the difference between intermediate and terminal operations?
3. What happens with `Collectors.toMap` when two elements have the same key?
4. `map` vs `flatMap`?
5. When does a parallel stream make things slower or wrong?
6. `orElse` vs `orElseGet`?
7. Why shouldn't `Optional` be used for fields or method parameters?
8. What is the problem with side effects in stream lambdas?

---

**Answers**
1. A collection stores elements; a stream describes a computation over a source, is lazy, can be infinite, doesn't store data, and can be consumed only once.
2. Intermediate ops (`map`, `filter`) return a new stream and are lazy; a terminal op (`collect`, `count`, `forEach`) triggers the pipeline and produces a result or side effect.
3. It throws `IllegalStateException` (duplicate key) unless you pass a merge function as the third argument.
4. `map` transforms each element into one element; `flatMap` transforms each element into a stream and flattens the result (one-to-many).
5. Small data, cheap per-element work, sources that split badly (`LinkedList`, `Stream.iterate`), ordered operations like `limit`/`findFirst`, blocking I/O on the shared common pool, and shared mutable state (races, wrong results).
6. `orElse(x)` always evaluates `x`, even if a value is present; `orElseGet(supplier)` calls the supplier only when empty — use it for expensive defaults.
7. It is designed as a return type to signal "maybe no result". As a field it adds overhead and isn't `Serializable`; as a parameter it forces callers to wrap values and still allows `null` Optionals. Use overloads or nullable parameters with clear docs instead.
8. It breaks with parallel execution (races), makes code order-dependent and hard to reason about. Use collectors/reduction to produce results instead of mutating external state.

---

## Module J2.3 — Records, sealed classes, pattern matching, text blocks, var (~5h)

**Topics:** `record` (JEP 395): canonical/compact constructors, validation,
generated `equals`/`hashCode`/`toString`/accessors, records as DTOs and value
objects, shallow immutability; **sealed** classes and interfaces (JEP 409),
`permits`, `final`/`sealed`/`non-sealed` subclasses; pattern matching for
`instanceof` (JEP 394); pattern matching for `switch` (JEP 441), guards with
`when`, exhaustiveness with sealed hierarchies; record patterns and
deconstruction (JEP 440); unnamed variables and patterns `_` (JEP 456, final
in 22); primitive types in patterns (JEP 507 — **preview** in 25); text blocks
(JEP 378); `var` for local variables (JEP 286) and when not to use it;
algebraic data types = sealed interface + records.

🐍 Records ≈ `@dataclass(frozen=True)`; pattern matching for switch ≈
`match`/`case` (PEP 634).

### Lessons
- [ ] **J2.3.L1 Records.** dev.java/learn → "Records" → "Using Record to Model Immutable Data"; JEP 395.
- [ ] **J2.3.L2 Sealed.** dev.java/learn → "Sealed Classes" (or "Inheritance" → "Sealed Classes and Interfaces"); JEP 409.
- [ ] **J2.3.L3 Pattern matching.** dev.java/learn → "Pattern Matching" (all pages: instanceof, switch, record patterns); JEP 441 "Pattern Matching for switch", JEP 440 "Record Patterns", JEP 456 "Unnamed Variables & Patterns".
- [ ] **J2.3.L4 Text blocks & var.** dev.java/learn → "Text Blocks"; "Using the Var Type Identifier"; JEP 378; OpenJDK "Local Variable Type Inference: Style Guidelines" (Stuart Marks).
- [ ] **J2.3.L5 Preview watch.** JEP 507 "Primitive Types in Patterns, instanceof, and switch (Third Preview)" — read "Summary" only.

### Exercises (`java/J2.3-modern-syntax/`)
- [ ] **Ex J2.3.1 Records as value objects.** `record Money(long cents, Currency currency)` with a compact constructor that rejects null currency; `plus`/`minus` return new records and reject mixed currencies. *Acceptance:* tests show equality and immutability; you explain "shallow" immutability with a `List` component.
- [ ] **Ex J2.3.2 Sealed ADT.** `sealed interface Shape permits Circle, Rectangle, Triangle` (all records) and `double area(Shape s)` using a pattern-matching `switch` with record patterns and no `default`. *Acceptance:* adding a new permitted record makes `area` fail to compile until handled.
- [ ] **Ex J2.3.3 Expression evaluator.** `sealed interface Expr` with `Num`, `Add`, `Mul`, `Neg` records; `eval` and `toString` via switch patterns; simplification rules with guards (`when`). *Acceptance:* `(0 + x) * 1` simplifies to `x`.
- [ ] **Ex J2.3.4 Payment results.** Model `PaymentResult` as `Success(txId)`, `Declined(reason)`, `Error(Exception)`; handle all cases in a switch. *Acceptance:* no `instanceof` chains; `_` used for an unused component.
- [ ] **Ex J2.3.5 Text blocks & var.** Build a JSON and an SQL string with text blocks and `formatted`; rewrite 5 declarations with `var` and 2 where `var` hurts readability, and keep those explicit. *Acceptance:* a comment explains each choice.

### Must be able to do / explain
- [ ] Model data with records and validate in compact constructors.
- [ ] Build closed hierarchies with sealed types and exhaustive switches.
- [ ] Use pattern matching (`instanceof`, switch, record patterns).
- [ ] Use text blocks and `var` judiciously; know what is preview.

**Estimated hours:** ~5 h

### Self-check questions
1. What does a record generate for you, and what can't a record do?
2. Are records immutable?
3. What problem do sealed classes solve?
4. Why can a switch over a sealed interface omit `default`?
5. What is a record pattern?
6. When should you not use `var`?

---

**Answers**
1. A private final field per component, a canonical constructor, accessors (`name()`), `equals`, `hashCode`, `toString`. A record can't extend another class (it extends `Record`), can't have extra instance fields, and its fields are final. It can implement interfaces and have static members and methods.
2. Shallowly: the fields are final, but a component referencing a mutable object (e.g. a `List`) can still be mutated. Defensive copies (`List.copyOf`) in the compact constructor fix it.
3. They restrict which classes can extend a type, so the hierarchy is closed and known to the compiler: good for domain modelling (ADTs) and exhaustive pattern matching.
4. The compiler knows all permitted subtypes and checks that every one is covered; if a new subtype is added, the switch stops compiling instead of silently falling into `default`.
5. A pattern that matches a record and deconstructs its components in one step: `case Point(int x, int y) -> ...`, nestable.
6. When the type isn't obvious from the right-hand side (e.g. `var x = service.load()`), when the exact type matters for understanding, or with literals where the inferred type may surprise you (`var n = 1;` is `int`, not `long`).

---

## Module J2.4 — Annotations, reflection, JPMS basics (~5h)

**Topics:** annotations: built-in (`@Override`, `@Deprecated`,
`@SuppressWarnings`, `@FunctionalInterface`, `@SafeVarargs`),
meta-annotations (`@Retention`, `@Target`, `@Inherited`, `@Repeatable`),
declaring custom annotations; runtime processing with reflection vs
compile-time annotation processors (overview — Lombok/MapStruct idea);
**reflection**: `Class`, `getDeclaredMethods/Fields`, `setAccessible`,
invoking methods, creating instances, cost and dangers; how frameworks (JUnit,
Spring, Hibernate) use annotations + reflection; dynamic proxies
(`java.lang.reflect.Proxy`) as the preview of Spring AOP (J6.3); **JPMS**:
`module-info.java`, `requires`, `exports`, `opens` (why reflection-heavy
frameworks need it), the class path vs module path, strong encapsulation of
JDK internals; module import declarations (JEP 511, final in 25).

🐍 Annotations ≈ decorators that only *mark* (no behavior by themselves);
reflection ≈ `getattr`/`inspect`.

### Lessons
- [ ] **J2.4.L1 Annotations.** dev.java/learn → "Annotations" (all pages: basics, predefined annotation types, declaring an annotation type, repeating annotations, type annotations).
- [ ] **J2.4.L2 Reflection.** dev.java/learn → "Java Reflection" (or Oracle "The Reflection API" trail); Baeldung "Guide to Java Reflection".
- [ ] **J2.4.L3 Proxies.** Baeldung "Dynamic Proxies in Java".
- [ ] **J2.4.L4 Modules.** dev.java/learn → "Modules" → "Introduction to Modules in Java", "Code for the Module System" and the pages on `requires`/`exports`/`opens`; *Modern Java in Action* ch.14 "The Java Module System"; JEP 511 "Module Import Declarations" (summary).
- [ ] **J2.4.L5 Effective Java.** Item 39 "Prefer annotations to naming patterns", Item 65 "Prefer interfaces to reflection".

### Exercises (`java/J2.4-annotations-reflection/`)
- [ ] **Ex J2.4.1 Mini test runner.** Define `@MyTest` (runtime retention, method target). Write a runner that finds annotated methods in a class by reflection, runs them, and reports pass/fail with the exception message. *Acceptance:* works on a class with 3 passing and 2 failing methods; you can explain how JUnit does the same at a high level.
- [ ] **Ex J2.4.2 Validation annotations.** `@NotBlank`, `@Min(value)` on record components or fields; a `Validator.validate(Object)` that reads them reflectively and returns violations. *Acceptance:* reports all violations for an invalid object (preview of Jakarta Bean Validation in J7.2).
- [ ] **Ex J2.4.3 Logging proxy.** Use `Proxy.newProxyInstance` to wrap a `PaymentService` interface and log method name, args and duration. *Acceptance:* you explain why this works only for interfaces and how CGLIB/ByteBuddy subclass proxies differ (important for `@Transactional` later).
- [ ] **Ex J2.4.4 Modules.** Split a small app into two modules (`com.x.core`, `com.x.app`) with `module-info.java`; try to use a non-exported package; then open a package for reflection. *Acceptance:* you show the compile/runtime errors and fix them with `exports`/`opens`.

### Must be able to do / explain
- [ ] Declare and process a custom runtime annotation.
- [ ] Use reflection to inspect and invoke members, and name its costs.
- [ ] Explain JDK dynamic proxies and why frameworks use proxies.
- [ ] Read a `module-info.java` and explain `requires`/`exports`/`opens`.

**Estimated hours:** ~5 h

### Self-check questions
1. What does `@Retention(RUNTIME)` mean and why do frameworks need it?
2. How do JUnit and Spring find your annotated methods/classes?
3. What are the downsides of reflection?
4. How does a JDK dynamic proxy work, and what is its main limitation?
5. `exports` vs `opens` in `module-info.java`?
6. Do you need JPMS for a typical Spring Boot app?

---

**Answers**
1. The annotation is stored in the class file and available via reflection at run time. Frameworks read annotations at run time to decide behavior (run this method as a test, inject this bean).
2. They scan the class path (or read an index), load classes and inspect annotations reflectively (Spring also uses ASM to read class metadata without loading classes during component scanning).
3. It's slower, bypasses compile-time checks (errors appear at run time), breaks encapsulation (`setAccessible`), makes refactoring and tools weaker, and needs `opens` under JPMS.
4. `Proxy.newProxyInstance` creates a class at run time that implements the given interfaces and forwards every call to an `InvocationHandler`. It can only proxy interfaces, not classes (for classes, libraries generate subclasses — CGLIB/ByteBuddy).
5. `exports` makes public types of a package accessible at compile and run time. `opens` additionally allows deep reflection (including private members) at run time, e.g. for Hibernate/Jackson.
6. No. Most Spring Boot apps run on the class path. It's still worth knowing JPMS for the JDK's strong encapsulation and for library design.

---

## Module J2.5 — Immutability & design patterns (~8h)

**Topics:** immutable classes (final class, private final fields, no
setters, defensive copies in and out, `List.copyOf`), benefits (thread
safety, caching, safe sharing); "wither" methods; patterns in modern Java:
**Builder** (telescoping constructors problem; builder for many optional
fields; records + builder), **Factory** (static factory method, factory
method pattern, abstract factory), **Strategy** (interfaces + lambdas),
**Observer** (listeners, `PropertyChangeSupport`, how Spring events relate),
**Singleton** (enum singleton, lazy holder idiom, why DI containers replace
most singletons), **Decorator** (I/O streams in the JDK, composition), plus
Template Method vs Strategy; anti-patterns (God class, overuse of patterns).

🐍 Many Python patterns are "just functions"; in Java the same idea often
becomes an interface + lambda.

### Lessons
- [ ] **J2.5.L1 Immutability.** Effective Java Item 17 "Minimize mutability", Item 50 "Make defensive copies when needed".
- [ ] **J2.5.L2 Builder, factory, singleton.** Effective Java Item 1 (static factories), Item 2 "Consider a builder when faced with many constructor parameters", Item 3 "Enforce the singleton property with a private constructor or an enum type".
- [ ] **J2.5.L3 Pattern catalogue.** refactoring.guru → "Design Patterns" → Builder, Factory Method, Abstract Factory, Singleton, Strategy, Observer, Decorator, Template Method (read "Problem", "Solution", "Applicability", "Pros and Cons"; look at the Java examples).
- [ ] **J2.5.L4 Patterns with lambdas.** *Modern Java in Action* ch.9 "Refactoring, testing, and debugging" → section 9.2 "Refactoring object-oriented design patterns with lambdas".
- [ ] **J2.5.L5 Optional book.** *Head First Design Patterns*, 2nd ed. — chapters on Strategy, Observer, Decorator, Factory, Singleton.

### Exercises (`java/J2.5-patterns/`)
- [ ] **Ex J2.5.1 Immutable class by hand.** `final class Period(start, end)` storing `LocalDate`s and a list of tags; defensive copies; `withEnd(...)` returns a new object. *Acceptance:* a test tries to mutate it via the constructor argument list and the getter — both fail.
- [ ] **Ex J2.5.2 Builder.** `HttpRequestSpec` with 2 required and 8 optional fields; a static nested `Builder` with validation in `build()`. *Acceptance:* invalid combinations throw at `build()`; the object is immutable.
- [ ] **Ex J2.5.3 Strategy.** Discount strategies (none, percent, fixed, capped) for a checkout: first as classes implementing `DiscountPolicy`, then as lambdas/static factories. *Acceptance:* the checkout code doesn't change when a new strategy is added.
- [ ] **Ex J2.5.4 Observer.** A `StockTicker` that notifies registered listeners; listeners are lambdas; unsubscribe works. *Acceptance:* you explain the memory-leak risk of never unsubscribing.
- [ ] **Ex J2.5.5 Decorator.** Wrap a `Notifier` interface: base email notifier + decorators for retry, logging and rate limiting, combined in any order. *Acceptance:* you can relate it to `new BufferedReader(new InputStreamReader(in))`.
- [ ] **Ex J2.5.6 Singleton options.** Implement a config registry as an enum singleton and as a lazy-holder class; then explain in `notes.md` why you'd rather inject it (J6.1). *Acceptance:* both are thread-safe without `synchronized`.

### Must be able to do / explain
- [ ] Write a fully immutable class and explain its benefits.
- [ ] Implement Builder, Factory, Strategy, Observer, Singleton, Decorator and say when each is appropriate.
- [ ] Replace class-heavy patterns with lambdas where it's clearer.

**Estimated hours:** ~8 h

### Self-check questions
1. What are the rules for making a class immutable?
2. When would you use a Builder instead of constructors?
3. What is the safest way to implement a singleton in Java?
4. Strategy vs Template Method?
5. Where does the JDK itself use the Decorator pattern?
6. Why do dependency injection containers reduce the need for the Singleton pattern?
7. What is the risk of the Observer pattern?

---

**Answers**
1. Don't provide mutators; make the class `final` (or constructors private); make all fields `private final`; make defensive copies of mutable inputs and never expose mutable internals (return copies or unmodifiable views).
2. When there are many parameters, especially optional ones or several of the same type, where telescoping constructors become unreadable and error-prone; a builder gives named, readable construction and validation in one place.
3. An enum with one constant (`enum Registry { INSTANCE; }`): thread-safe, serialization-safe and reflection-safe. The lazy holder idiom is fine for lazy initialization.
4. Strategy uses composition: the varying algorithm is an object/lambda passed in. Template Method uses inheritance: a base class defines the skeleton and subclasses override steps. Strategy is usually more flexible.
5. The I/O streams (`BufferedInputStream`, `DataInputStream` wrapping `InputStream`), `Collections.unmodifiableList`/`synchronizedList` wrappers.
6. The container creates one instance per bean (singleton scope) and injects it, so classes don't need global static access; it stays testable (you can inject a fake).
7. Listeners that are never removed keep objects alive (memory leaks); notification order and exceptions in one listener can affect others; hidden coupling makes flows hard to follow.

---

## Module J2.6 — SOLID & key Effective Java items (~6h)

**Topics:** Single Responsibility, Open/Closed, Liskov Substitution,
Interface Segregation, Dependency Inversion — each with a Java example and a
counter-example; coupling and cohesion; depending on abstractions; a curated
list of Effective Java items every middle developer should know: 1, 2, 3, 5
("Prefer dependency injection to hardwiring resources"), 6, 7, 9, 10, 11, 13
("Override clone judiciously" — i.e. avoid), 15, 17, 18, 20, 28, 31, 34, 42,
45, 49 ("Check parameters for validity"), 54, 55, 57, 59, 61, 64 ("Refer to
objects by their interfaces"), 67 ("Optimize judiciously"), 69, 72, 78
(preview for Part 3), 85.

🐍 SOLID applies equally in Python; Java's static types make violations easier
to see (e.g. LSP breaks show up as surprising overrides).

### Lessons
- [ ] **J2.6.L1 SOLID.** Baeldung "A Solid Guide to SOLID Principles"; Robert C. Martin, *Clean Architecture*, Part III "Design Principles" (ch.7–11).
- [ ] **J2.6.L2 Effective Java — creating objects.** Items 1, 2, 3, 5, 6, 7, 9.
- [ ] **J2.6.L3 Effective Java — classes & interfaces.** Items 15, 17, 18, 20, 64.
- [ ] **J2.6.L4 Effective Java — methods & general programming.** Items 49, 54, 55, 57, 59, 61, 67.
- [ ] **J2.6.L5 Effective Java — review.** Re-read Items 10, 11, 28, 31, 34, 42, 45, 69, 72 (already met in earlier modules) and write a one-line summary of each in `notes.md`.

### Exercises (`java/J2.6-solid/`)
- [ ] **Ex J2.6.1 SRP refactor.** Take a 200-line `ReportService` (write it deliberately bad: reads CSV, calculates, formats HTML, sends email) and split it by responsibility. *Acceptance:* each class has one reason to change; the email sender is behind an interface.
- [ ] **Ex J2.6.2 OCP.** Add a new export format (CSV → JSON → XML) without modifying the existing exporter classes. *Acceptance:* adding XML touches only new files and one registration point.
- [ ] **Ex J2.6.3 LSP violation.** The classic `Rectangle`/`Square` (or `ReadOnlyList.add` throwing). *Acceptance:* a test that works for the parent fails for the child; you describe a better design.
- [ ] **Ex J2.6.4 DIP with constructor injection.** `OrderService` depends on `PaymentGateway` and `OrderRepository` interfaces passed through the constructor; write a fake of each for tests. *Acceptance:* `OrderService` has no `new` of infrastructure classes (preview of Spring DI in J6.1).
- [ ] **Ex J2.6.5 Code review.** Review your JP1 LedgerLite code against 10 Effective Java items of your choice. *Acceptance:* `notes.md` lists each item, the violation found (or "none"), and the fix you applied.

### Must be able to do / explain
- [ ] Explain each SOLID principle with a Java example.
- [ ] Spot SRP, OCP, LSP and DIP violations in code review.
- [ ] Summarise ~30 Effective Java items in one sentence each.

**Estimated hours:** ~6 h

### Self-check questions
1. Explain the Liskov Substitution Principle with an example.
2. What is the Dependency Inversion Principle, and how does DI help?
3. What does Open/Closed mean in practice?
4. What is Interface Segregation?
5. Name five Effective Java items you apply most, and why.
6. What does "optimize judiciously" (Item 67) say?

---

**Answers**
1. Objects of a subtype must be usable wherever the supertype is expected without breaking correctness. A `Square extends Rectangle` whose `setWidth` also changes the height breaks code that expects width and height to be independent.
2. High-level modules should depend on abstractions, not on low-level details; details depend on abstractions too. DI supplies the concrete implementations from outside (constructor), so business logic depends only on interfaces and is easy to test.
3. You add new behavior by adding new code (new classes implementing an interface, new strategies) instead of editing existing, tested code.
4. Clients shouldn't be forced to depend on methods they don't use: prefer several small, focused interfaces over one fat interface.
5. Example: static factories (1), builder (2), minimize mutability (17), composition over inheritance (18), return empty collections not null (54) — each prevents a common class of bugs or makes APIs clearer. (Any well-argued five are fine.)
6. Write clear, correct code first; don't sacrifice good design for speculative performance; measure with a profiler before and after optimizing, and focus on architecture/algorithms rather than micro-tweaks.

---

# Part 3 — Concurrency & JVM internals (~40 h)

**Main resources for Part 3:**
- *Java Concurrency in Practice* (Goetz et al.) — still the concurrency bible;
  complement it with JEPs for virtual threads and structured concurrency.
- *Modern Java in Action* ch.15–16 for `CompletableFuture`.
- Oracle "Java Platform, Standard Edition HotSpot Virtual Machine Garbage
  Collection Tuning Guide" and "Troubleshooting Guide" for the JVM parts.

---

## Module J3.1 — Threads, Runnable/Callable, synchronized, volatile, Java Memory Model (~8h)

**Topics:** processes vs threads; `Thread`, `Runnable`, `Callable`; starting,
joining, interrupting (`interrupt`, `InterruptedException`, restoring the
interrupt flag); daemon threads; thread states; race conditions and
check-then-act / read-modify-write; `synchronized` methods and blocks,
intrinsic locks, reentrancy; `wait`/`notify` (know it, prefer
`java.util.concurrent`); **visibility** and the **Java Memory Model**:
happens-before rules (program order, monitor lock, volatile, thread start/join,
final fields), `volatile` (visibility + ordering, not atomicity), safe
publication, immutable objects and thread safety, thread confinement,
`ThreadLocal`; documenting thread safety.

🐍 CPython's GIL hides many races (but not all); Java threads run truly in
parallel, so memory visibility matters.

### Lessons
- [ ] **J3.1.L1 JCiP.** Ch.1 "Introduction", ch.2 "Thread Safety", ch.3 "Sharing Objects", ch.4 "Composing Objects".
- [ ] **J3.1.L2 JMM.** JCiP ch.16 "The Java Memory Model"; JLS §17.4 "Memory Model" (read 17.4.4–17.4.5 on synchronization order and happens-before).
- [ ] **J3.1.L3 dev.java.** dev.java/learn → "Concurrency" → "Processes and Threads", "Thread Objects", "Synchronization" (thread interference, memory consistency errors, synchronized methods, intrinsic locks, atomic access), "Liveness", "Guarded Blocks", "Immutable Objects".
- [ ] **J3.1.L4 Effective Java.** Item 78 "Synchronize access to shared mutable data", Item 79 "Avoid excessive synchronization", Item 82 "Document thread safety", Item 84 "Don't depend on the thread scheduler".
- [ ] **J3.1.L5 Baeldung.** "Guide to the Volatile Keyword in Java"; "How to Kill a Java Thread" (interruption).

### Exercises (`java/J3.1-threads-jmm/`)
- [ ] **Ex J3.1.1 Lost updates.** Two threads each increment a shared `int` counter 1 000 000 times. *Acceptance:* the result is below 2 000 000 most runs; fix it with `synchronized` and explain why `volatile` alone does **not** fix it.
- [ ] **Ex J3.1.2 Visibility bug.** A worker loops `while (!stopped)` on a non-volatile flag set by `main`. *Acceptance:* you reproduce a hang (try with `-server` and a tight loop), fix it with `volatile`, and explain via happens-before.
- [ ] **Ex J3.1.3 Interruption.** A worker that sleeps/waits in a loop and stops cleanly when interrupted, restoring the interrupt flag when it can't rethrow. *Acceptance:* `main` interrupts it and `join`s within 1 s.
- [ ] **Ex J3.1.4 Thread-safe class.** Make the `BankAccount` from J1.5 thread-safe; add `transfer(from, to, amount)` and document its thread-safety policy (`@ThreadSafe`-style comment). *Acceptance:* a stress test with 8 threads doing random transfers keeps the total balance constant.
- [ ] **Ex J3.1.5 Safe publication.** Write a class that publishes an object through a non-final, non-volatile field and explain why another thread might see a partially constructed object; fix it three ways (final fields, volatile, synchronized). *Acceptance:* written explanation in `notes.md` referencing JCiP ch.3.

### Must be able to do / explain
- [ ] Create, start, join and interrupt threads correctly.
- [ ] Explain race conditions, atomicity and visibility as separate problems.
- [ ] Explain happens-before and what `synchronized` and `volatile` guarantee.
- [ ] Make a class thread-safe and document its policy.

**Estimated hours:** ~8 h

### Self-check questions
1. What is a race condition? Give the two common forms.
2. What does `synchronized` guarantee?
3. What does `volatile` guarantee, and what doesn't it?
4. What is the happens-before relationship? Name four rules.
5. What is safe publication?
6. How should you handle `InterruptedException`?
7. Why are immutable objects automatically thread-safe?
8. `Runnable` vs `Callable`?

---

**Answers**
1. When correctness depends on the timing/interleaving of threads. Check-then-act (`if (!map.containsKey(k)) map.put(k, v)`) and read-modify-write (`count++`).
2. Mutual exclusion (only one thread holds the monitor) and visibility: everything a thread did before releasing a lock is visible to the next thread that acquires the same lock.
3. Visibility (reads see the latest write) and ordering (no reordering across the volatile access). Not atomicity of compound actions like `count++`.
4. A guarantee that the effects of one action are visible to another. Rules: program order within a thread; unlock of a monitor → later lock of the same monitor; write to a volatile → later read of it; `Thread.start()` → actions in the started thread; actions in a thread → another thread's successful `join()` on it; the end of a constructor (final fields) → use of the object.
5. Making an object and its state visible to other threads correctly: via a final field, a volatile field, a lock-protected field, a static initializer, or a thread-safe collection.
6. Don't swallow it. Either propagate it (declare `throws`) or, if you can't, restore the flag with `Thread.currentThread().interrupt()` and exit the task.
7. Their state can't change after construction, so there's nothing to race on; with final fields they are also safely published.
8. `Runnable.run()` returns nothing and can't throw checked exceptions; `Callable.call()` returns a value and can throw — used with `ExecutorService.submit` and `Future`.

---

## Module J3.2 — Locks, atomics, concurrent collections, synchronizers (~6h)

**Topics:** `java.util.concurrent.locks`: `ReentrantLock` (tryLock, timed
lock, interruptible lock, fairness), `ReadWriteLock`, `StampedLock`
(optimistic reads), `Condition`; always unlock in `finally`; atomics
(`AtomicInteger`, `AtomicLong`, `AtomicReference`, `compareAndSet`,
`LongAdder` for contended counters); CAS and the ABA problem (concept);
concurrent collections: `ConcurrentHashMap` (atomic `compute`/`merge`,
no null keys/values, weakly consistent iterators), `CopyOnWriteArrayList`,
`BlockingQueue` (`ArrayBlockingQueue`, `LinkedBlockingQueue`), `ConcurrentLinkedQueue`,
`ConcurrentSkipListMap`; synchronizers: `CountDownLatch`, `Semaphore`,
`CyclicBarrier`, `Phaser` (overview); producer–consumer.

🐍 `threading.Lock`/`RLock`/`Semaphore`/`Barrier` and `queue.Queue` have direct
Java counterparts.

### Lessons
- [ ] **J3.2.L1 JCiP.** Ch.5 "Building Blocks" (synchronized vs concurrent collections, blocking queues, synchronizers), ch.13 "Explicit Locks", ch.15 "Atomic Variables and Nonblocking Synchronization".
- [ ] **J3.2.L2 dev.java.** dev.java/learn → "Concurrency" → "High Level Concurrency Objects" → "Lock Objects", "Concurrent Collections", "Atomic Variables".
- [ ] **J3.2.L3 Baeldung.** "Guide to java.util.concurrent.Locks"; "A Guide to ConcurrentMap"; "Guide to CountDownLatch in Java"; "Semaphores in Java"; "CyclicBarrier in Java".
- [ ] **J3.2.L4 Effective Java.** Item 81 "Prefer concurrency utilities to wait and notify".

### Exercises (`java/J3.2-locks-atomics/`)
- [ ] **Ex J3.2.1 Counter shoot-out.** Compare `synchronized`, `ReentrantLock`, `AtomicLong` and `LongAdder` counters under 1, 4 and 16 threads. *Acceptance:* a timing table and an explanation of why `LongAdder` wins under contention.
- [ ] **Ex J3.2.2 Word count, concurrently.** Several threads count words from different files into one `ConcurrentHashMap<String, Long>` using `merge`. *Acceptance:* results match a single-threaded count; you explain why `get` + `put` would be wrong.
- [ ] **Ex J3.2.3 Bounded producer–consumer.** 2 producers, 3 consumers, an `ArrayBlockingQueue` of capacity 10, and a "poison pill" shutdown. *Acceptance:* every produced item is consumed exactly once; all threads terminate.
- [ ] **Ex J3.2.4 Connection limiter.** A `Semaphore`-based limiter allowing at most 5 concurrent "DB calls" out of 50 tasks. *Acceptance:* a counter proves concurrency never exceeds 5.
- [ ] **Ex J3.2.5 Start gate.** Use `CountDownLatch` to start 10 worker threads at the same moment and wait for all to finish; then redo the "rounds" version with `CyclicBarrier`. *Acceptance:* you explain one-shot latch vs reusable barrier.
- [ ] **Ex J3.2.6 tryLock transfer.** Implement `transfer` between two accounts with `tryLock` and a timeout to avoid deadlock. *Acceptance:* a stress test with opposite-direction transfers never hangs.

### Must be able to do / explain
- [ ] Use `ReentrantLock` safely (unlock in `finally`, tryLock with timeout).
- [ ] Choose between synchronized, locks and atomics.
- [ ] Use `ConcurrentHashMap` atomic operations correctly.
- [ ] Use blocking queues and the common synchronizers.

**Estimated hours:** ~6 h

### Self-check questions
1. `synchronized` vs `ReentrantLock` — when do you need the lock?
2. What is compare-and-set (CAS)?
3. `AtomicLong` vs `LongAdder`?
4. How is `ConcurrentHashMap` different from `Collections.synchronizedMap`?
5. Why doesn't `ConcurrentHashMap` allow null keys or values?
6. `CountDownLatch` vs `CyclicBarrier` vs `Semaphore`?
7. When would you use `CopyOnWriteArrayList`?

---

**Answers**
1. `synchronized` is simpler and automatically released. Use `ReentrantLock` when you need `tryLock`, timeouts, interruptible locking, fairness, or multiple `Condition`s.
2. An atomic CPU instruction: "if the value is still X, set it to Y", returning success/failure. Lock-free algorithms loop on CAS until they succeed.
3. `AtomicLong` is one variable updated with CAS; under high contention many CAS attempts fail and retry. `LongAdder` spreads updates over several cells and sums them on read — much faster for write-heavy counters, but `sum()` isn't an atomic snapshot.
4. A synchronized map locks the whole map for every operation. `ConcurrentHashMap` uses fine-grained locking/CAS per bin, allows concurrent reads and writes, offers atomic compound operations (`compute`, `merge`, `putIfAbsent`), and its iterators are weakly consistent (no CME).
5. Because `get` returning `null` would be ambiguous (absent or null value?) and you can't check `containsKey` atomically together with `get` in a concurrent map.
6. `CountDownLatch`: one-shot; threads wait until a count reaches zero. `CyclicBarrier`: reusable; a fixed number of threads wait for each other at a barrier point. `Semaphore`: limits how many threads access a resource at once.
7. When reads vastly outnumber writes and the list is small — e.g. listener lists. Every write copies the array.

---

## Module J3.3 — ExecutorService & CompletableFuture (~6h)

**Topics:** why not `new Thread` per task; the Executor framework:
`Executor`, `ExecutorService`, `Executors` factory methods and their
pitfalls (unbounded queues), `ThreadPoolExecutor` parameters (core/max size,
queue, keep-alive, rejection policy, thread factory with names), sizing
(CPU-bound ≈ cores, I/O-bound formula), `submit` vs `execute`, `Future`,
`invokeAll`/`invokeAny`, shutdown (`shutdown`, `awaitTermination`,
`shutdownNow`), `ExecutorService` is `AutoCloseable` since Java 19;
`ScheduledExecutorService`; `ForkJoinPool` and work stealing (overview);
**CompletableFuture**: `supplyAsync`, `thenApply`, `thenCompose`,
`thenCombine`, `allOf`/`anyOf`, `exceptionally`/`handle`/`whenComplete`,
timeouts (`orTimeout`, `completeOnTimeout`), choosing the executor (don't block
the common pool).

🐍 `concurrent.futures.ThreadPoolExecutor` ≈ `ExecutorService`;
`CompletableFuture` chains ≈ `asyncio` tasks + callbacks (but on threads).

### Lessons
- [ ] **J3.3.L1 JCiP.** Ch.6 "Task Execution", ch.7 "Cancellation and Shutdown", ch.8 "Applying Thread Pools".
- [ ] **J3.3.L2 Book.** *Modern Java in Action* ch.15 "Concepts behind CompletableFuture and reactive programming", ch.16 "CompletableFuture: composable asynchronous programming".
- [ ] **J3.3.L3 dev.java.** dev.java/learn → "Concurrency" → "Executors" (executor interfaces, thread pools, fork/join).
- [ ] **J3.3.L4 Baeldung.** "A Guide to the Java ExecutorService"; "Guide To CompletableFuture".
- [ ] **J3.3.L5 Effective Java.** Item 80 "Prefer executors, tasks, and streams to threads".

### Exercises (`java/J3.3-executors/`)
- [ ] **Ex J3.3.1 Custom pool.** Build a `ThreadPoolExecutor` with named threads, a bounded queue of 100 and `CallerRunsPolicy`; submit 1 000 short tasks. *Acceptance:* you observe back-pressure (the caller runs tasks) and shut the pool down cleanly.
- [ ] **Ex J3.3.2 Parallel downloads (simulated).** 20 "HTTP calls" (`Thread.sleep` 200–800 ms) run with `invokeAll` on pools of size 1, 4, 20. *Acceptance:* a timing table; one call throws and you handle it via `Future.get` → `ExecutionException`.
- [ ] **Ex J3.3.3 Price aggregator.** Query 5 fake shop services with `CompletableFuture.supplyAsync` on a dedicated executor, combine results with `allOf`, return the cheapest; a slow shop is cut off with `completeOnTimeout`, a failing one with `exceptionally`. *Acceptance:* total time ≈ the timeout, not the sum of calls.
- [ ] **Ex J3.3.4 thenApply vs thenCompose.** Chain "get user → get orders for user → compute total" where each step returns a `CompletableFuture`. *Acceptance:* you show the nested `CompletableFuture<CompletableFuture<…>>` with `thenApply` and fix it with `thenCompose`.
- [ ] **Ex J3.3.5 Scheduled job.** A `ScheduledExecutorService` that prints a heartbeat every second and a task that throws on the 3rd run. *Acceptance:* you explain why the periodic task silently stops after the exception and how to guard against it.

### Must be able to do / explain
- [ ] Configure and size a thread pool and shut it down correctly.
- [ ] Explain why `Executors.newFixedThreadPool`/`newCachedThreadPool` can be dangerous in production.
- [ ] Compose asynchronous work with `CompletableFuture`, including errors and timeouts.

**Estimated hours:** ~6 h

### Self-check questions
1. What are the parameters of `ThreadPoolExecutor`, and what happens when the queue is full?
2. How would you size a pool for CPU-bound vs I/O-bound tasks?
3. What's dangerous about `Executors.newCachedThreadPool()` and `newFixedThreadPool()`?
4. `submit` vs `execute`?
5. `thenApply` vs `thenCompose` vs `thenCombine`?
6. Why shouldn't you run blocking I/O in `CompletableFuture.supplyAsync` without an executor?
7. How do you shut down an executor gracefully?

---

**Answers**
1. Core pool size, maximum pool size, keep-alive time, work queue, thread factory, rejection handler. Tasks go to core threads, then the queue, then extra threads up to max; if all are full, the rejection policy runs (Abort, CallerRuns, Discard, DiscardOldest).
2. CPU-bound: about the number of cores (± 1). I/O-bound: more threads, roughly cores × (1 + wait time / compute time) — or use virtual threads (J3.4).
3. Cached: unbounded number of threads → can exhaust memory/OS threads under load. Fixed: unbounded `LinkedBlockingQueue` → tasks pile up and memory grows without back-pressure.
4. `execute(Runnable)` returns nothing; exceptions go to the thread's uncaught handler. `submit` returns a `Future`; exceptions are captured and rethrown as `ExecutionException` from `get()` — if you never call `get()`, they are silently lost.
5. `thenApply` maps the result with a plain function; `thenCompose` flat-maps with a function that returns another `CompletableFuture`; `thenCombine` combines the results of two independent futures.
6. It then runs on the shared `ForkJoinPool.commonPool()`, which is sized for CPU work; blocking calls starve it and slow down everything else using it (including parallel streams).
7. `shutdown()` (stop accepting new tasks), `awaitTermination(timeout)`, and if it times out, `shutdownNow()` (interrupts running tasks) — or use try-with-resources with `close()` (Java 19+), which does shutdown + await.

---

## Module J3.4 — Deadlocks, virtual threads, structured concurrency (~6h)

**Topics:** liveness hazards: deadlock (four Coffman conditions), lock
ordering, open calls, timed `tryLock`, livelock, starvation; detecting
deadlocks (`jstack`, `ThreadMXBean`); **virtual threads** (JEP 444, final in
21): cheap threads scheduled by the JVM on carrier threads,
thread-per-request again, `Executors.newVirtualThreadPerTaskExecutor()`,
`Thread.ofVirtual()`, don't pool virtual threads, limit concurrency with
semaphores, **pinning** (native frames; `synchronized` pinning removed by
JEP 491 in Java 24), `ThreadLocal` caution; when virtual threads help
(I/O-bound, high concurrency) and when not (CPU-bound); **structured
concurrency** (`StructuredTaskScope`, JEP 505 — **fifth preview in Java 25**,
API changed from earlier previews) and **scoped values** (JEP 506, final in
25).

🐍 Virtual threads give you "asyncio-like" scalability with plain blocking
code — no `async`/`await` colouring.

### Lessons
- [ ] **J3.4.L1 JCiP.** Ch.10 "Avoiding Liveness Hazards".
- [ ] **J3.4.L2 Virtual threads.** JEP 444 "Virtual Threads" — read "Motivation", "Description", "Pinning" and "Don't pool virtual threads"; Oracle docs "Core Libraries → Concurrency → Virtual Threads".
- [ ] **J3.4.L3 No more synchronized pinning.** JEP 491 "Synchronize Virtual Threads without Pinning" (summary).
- [ ] **J3.4.L4 Structured concurrency.** JEP 505 "Structured Concurrency (Fifth Preview)" — "Motivation", "Description"; JEP 506 "Scoped Values".
- [ ] **J3.4.L5 dev.java.** dev.java/learn → "Virtual Threads" pages (or the Inside Java articles on virtual threads).

### Exercises (`java/J3.4-virtual-threads/`)
- [ ] **Ex J3.4.1 Make a deadlock.** Two threads lock two accounts in opposite order. *Acceptance:* the program hangs; you capture it with `jstack` (or `jcmd <pid> Thread.print`) and point to the "Found one Java-level deadlock" section; then fix it with a global lock ordering (e.g. by account id).
- [ ] **Ex J3.4.2 10 000 sleepers.** Run 10 000 tasks that each sleep 1 s on (a) a fixed pool of 200 platform threads and (b) a virtual-thread-per-task executor. *Acceptance:* timings recorded (≈50 s vs ≈1 s); you explain why.
- [ ] **Ex J3.4.3 CPU-bound check.** Run a CPU-heavy task (e.g. hashing) on virtual vs platform threads. *Acceptance:* no speed-up from virtual threads; you explain why.
- [ ] **Ex J3.4.4 Limit concurrency.** With virtual threads, call a fake "downstream API" that allows only 20 concurrent calls; enforce it with a `Semaphore`. *Acceptance:* a counter proves ≤ 20 concurrent calls; you explain why a small pool is the wrong tool with virtual threads.
- [ ] **Ex J3.4.5 Structured concurrency (preview).** With `--enable-preview` on Java 25, fetch user and orders concurrently inside a `StructuredTaskScope`; when one subtask fails, the other is cancelled. *Acceptance:* the failure cancels the sibling (visible in logs); you note which API names are preview and may change.

### Must be able to do / explain
- [ ] State the four deadlock conditions and prevent deadlocks with lock ordering or timeouts.
- [ ] Explain what virtual threads are, how they differ from platform threads and when they help.
- [ ] Explain pinning and why you don't pool virtual threads.
- [ ] Explain the idea of structured concurrency and that it is still preview in Java 25.

**Estimated hours:** ~6 h

### Self-check questions
1. What four conditions are needed for a deadlock?
2. How do you find a deadlock in a running JVM?
3. What is a virtual thread, and how is it scheduled?
4. When do virtual threads not help?
5. What is pinning, and what changed in Java 24?
6. Why is pooling virtual threads an anti-pattern?
7. What problem does structured concurrency solve?

---

**Answers**
1. Mutual exclusion, hold and wait, no preemption, circular wait. Break any one (usually circular wait, via consistent lock ordering).
2. Take a thread dump (`jstack <pid>`, `jcmd <pid> Thread.print`, VisualVM, or `ThreadMXBean.findDeadlockedThreads()`); it reports Java-level deadlocks with the locks each thread holds and waits for.
3. A lightweight thread managed by the JVM, not the OS. It runs on a small pool of carrier (platform) threads; when it blocks on I/O or sleeps, it is unmounted and its stack is saved on the heap, freeing the carrier for another virtual thread.
4. For CPU-bound work (you're limited by cores), and when the bottleneck is a limited downstream resource (DB connections) — you still must limit concurrency there.
5. A virtual thread that can't be unmounted from its carrier while blocked (e.g. inside a native call, or — before Java 24 — inside a `synchronized` block), so it blocks the carrier. JEP 491 (Java 24) made `synchronized` no longer pin.
6. Virtual threads are cheap to create and meant to be one per task; pooling adds complexity and doesn't save anything. Use a semaphore to limit concurrency instead.
7. It treats a group of concurrent subtasks as one unit of work with a clear scope: they start and finish within a block, failures and cancellation propagate (if one fails, the others are cancelled), and no threads leak — like `asyncio.TaskGroup`.

---

## Module J3.5 — JVM internals: memory areas, class loading, GC, JIT (~8h)

**Topics:** runtime data areas: heap (young: eden/survivors; old),
metaspace, thread stacks, PC register, native memory, code cache; object
layout, compressed oops, compact object headers (JEP 519, product feature in
Java 25, opt-in); class loading: loading, linking (verify, prepare,
resolve), initialization; the class loader hierarchy (bootstrap, platform,
application) and parent delegation; **garbage collection**: reachability and
GC roots, generational hypothesis, minor/major/full GC, mark-sweep-compact,
stop-the-world pauses; collectors: Serial, Parallel, **G1** (default; regions,
pause-time goal), **ZGC** (generational only since Java 24; sub-millisecond
pauses), Shenandoah; choosing a collector; key flags (`-Xms`, `-Xmx`,
`-XX:MaxGCPauseMillis`, `-XX:+UseZGC`, `-Xlog:gc*`); containers and
`-XX:MaxRAMPercentage`; **JIT**: interpreter, C1/C2 tiered compilation,
inlining, escape analysis, deoptimization, warm-up; AOT cache / class data
sharing (JEP 483 overview).

🐍 CPython uses reference counting + a cycle collector (you saw it in 1A.3);
the JVM uses tracing, moving, generational collectors.

### Lessons
- [ ] **J3.5.L1 Memory areas.** JVM Specification (Java SE 25) §2.5 "Run-Time Data Areas"; Baeldung "Stack Memory and Heap Space in Java".
- [ ] **J3.5.L2 Class loading.** JVM Specification ch.5 "Loading, Linking, and Initializing" (read 5.1–5.5 overview); Baeldung "Class Loaders in Java".
- [ ] **J3.5.L3 GC tuning guide.** Oracle "HotSpot Virtual Machine Garbage Collection Tuning Guide" (Java SE 25) → "Introduction", "Ergonomics", "Garbage Collector Implementation", "Available Collectors", "Garbage-First (G1) Garbage Collector", "The Z Garbage Collector".
- [ ] **J3.5.L4 JIT.** Baeldung "The JIT Compiler in Java" (or Oracle "Java HotSpot VM" docs on tiered compilation); JEP 483 "Ahead-of-Time Class Loading & Linking" (summary).
- [ ] **J3.5.L5 Containers.** Baeldung "JVM Parameters for Containers" (or Oracle docs on `-XX:MaxRAMPercentage`); JEP 519 "Compact Object Headers" (summary).

### Exercises (`java/J3.5-jvm-internals/`)
- [ ] **Ex J3.5.1 GC logs.** Run an allocation-heavy program with `-Xmx256m -Xlog:gc*:file=gc.log` using G1, then Parallel, then ZGC. *Acceptance:* a table of pause counts/max pause from the logs; you explain the differences.
- [ ] **Ex J3.5.2 OutOfMemoryError types.** Trigger `java.lang.OutOfMemoryError: Java heap space`, a `StackOverflowError` and (optionally) `Metaspace` exhaustion by generating classes. *Acceptance:* each run documented with the flags used and what memory area was exhausted.
- [ ] **Ex J3.5.3 Class loading trace.** Run a small app with `-Xlog:class+load` and find when your classes load vs JDK classes; show that a class's static initializer runs on first active use. *Acceptance:* output excerpt + explanation in `notes.md`.
- [ ] **Ex J3.5.4 JIT warm-up.** Time the same method in 20 rounds and plot/print the per-round time; run with `-XX:+PrintCompilation` (or `-Xlog:jit+compilation`) to see methods being compiled. *Acceptance:* you explain the warm-up curve and why naive micro-benchmarks lie (link to JMH in J8.6).
- [ ] **Ex J3.5.5 Container memory.** Run a Java program in Docker with a 512 MB memory limit and print `Runtime.getRuntime().maxMemory()` with default flags and with `-XX:MaxRAMPercentage=75`. *Acceptance:* you explain what the JVM does by default inside a container.

### Must be able to do / explain
- [ ] Draw the JVM memory areas and what lives in each.
- [ ] Explain class loading, parent delegation and class initialization.
- [ ] Explain generational GC, G1 and ZGC, and choose flags for a service.
- [ ] Read a GC log at a basic level.
- [ ] Explain JIT tiered compilation and warm-up.

**Estimated hours:** ~8 h

### Self-check questions
1. What are the main JVM memory areas?
2. What is a GC root?
3. Explain the generational hypothesis and how a minor GC works.
4. G1 vs ZGC — when would you choose each?
5. What is parent delegation in class loading and why does it exist?
6. What is metaspace?
7. What does the JIT do, and what is deoptimization?
8. How does the JVM decide its heap size inside a container?

---

**Answers**
1. Heap (objects; young + old generations), metaspace (class metadata), per-thread stacks (frames, locals), PC registers, native method stacks, code cache (JIT-compiled code), plus other native memory (direct buffers, GC structures).
2. A starting point for reachability: local variables on thread stacks, static fields, JNI references, active threads, etc. Objects not reachable from any root are garbage.
3. Most objects die young. New objects are allocated in eden; a minor GC copies live objects from eden (and one survivor) into the other survivor space or promotes them to the old generation after surviving several cycles. It is cheap because it only touches live young objects.
4. G1 is the default: good throughput with pause-time goals (~tens to hundreds of ms) for most heaps. ZGC targets very low pauses (sub-ms) even with very large heaps, at some CPU/throughput cost — for latency-sensitive services.
5. A class loader first asks its parent to load a class, so core classes (e.g. `java.lang.String`) are always loaded by the bootstrap loader. This prevents duplicate or spoofed core classes and keeps a consistent type system.
6. Native memory (outside the heap) that stores class metadata since Java 8 (it replaced PermGen). It grows automatically unless capped with `-XX:MaxMetaspaceSize`; class-loader leaks show up here.
7. It compiles hot bytecode to optimized machine code at run time (C1 quickly, C2 with aggressive optimizations based on profiling like inlining and escape analysis). Deoptimization throws away compiled code when an optimistic assumption turns out wrong (e.g. a new subclass is loaded) and falls back to the interpreter.
8. Since JDK 10 the JVM is container-aware: it reads the cgroup memory limit and by default uses ~25% of it for max heap (`MaxRAMPercentage` default 25). Services usually set `-XX:MaxRAMPercentage=70-80` or an explicit `-Xmx`.

---

## Module J3.6 — Diagnostics: jcmd, jstack, JFR, VisualVM, memory leaks (~6h)

**Topics:** JDK tools: `jps`, `jcmd` (VM.flags, GC.heap_info, Thread.print,
GC.heap_dump, JFR.start/dump), `jstack`, `jmap`, `jstat`; heap dumps and
analysing them (Eclipse MAT or VisualVM: dominator tree, retained size, paths
to GC roots); **Java Flight Recorder** (low-overhead profiling and events)
and **JDK Mission Control**; VisualVM (monitor, threads, sampler, profiler);
async-profiler and flame graphs (overview); common memory leaks: static
collections, unbounded caches, listeners not removed, `ThreadLocal` in
pools, class-loader leaks, unclosed resources; high CPU triage (top →
thread → stack); `-XX:+HeapDumpOnOutOfMemoryError`.

🐍 Like `tracemalloc`, `py-spy` and `cProfile` — but the JVM ships far more
built-in tooling.

### Lessons
- [ ] **J3.6.L1 Troubleshooting guide.** Oracle "Java Platform, Standard Edition Troubleshooting Guide" (Java SE 25) → "Diagnostic Tools" → "The jcmd Utility", "The jstack Utility"/thread dumps, "Java Flight Recorder"; and "Troubleshoot Memory Leaks".
- [ ] **J3.6.L2 JFR.** dev.java/learn → "Java Flight Recorder" / "JDK Flight Recorder and JDK Mission Control" pages (or Oracle JDK Mission Control User Guide → "Getting Started").
- [ ] **J3.6.L3 VisualVM.** visualvm.github.io → "Getting Started" and "Documentation".
- [ ] **J3.6.L4 Heap analysis.** Eclipse Memory Analyzer (eclipse.dev/mat) → "Getting Started" / "Basic Tutorial"; Baeldung "Understanding Memory Leaks in Java".
- [ ] **J3.6.L5 Flame graphs (overview).** async-profiler README (github.com/async-profiler/async-profiler) — "Basic usage", "Flame graph visualization".

### Exercises (`java/J3.6-diagnostics/`)
- [ ] **Ex J3.6.1 jcmd tour.** Against a running app: list JVMs with `jcmd`, print flags, heap info, thread dump, and GC stats with `jstat -gcutil`. *Acceptance:* a cheat sheet in `notes.md` with the commands and what each output means.
- [ ] **Ex J3.6.2 Find the leak.** Write an app with a hidden leak (e.g. a static `Map` cache that is never evicted, filled per "request"). Run it with a small heap and `-XX:+HeapDumpOnOutOfMemoryError`. *Acceptance:* in MAT or VisualVM you find the leaking collection via the dominator tree and "path to GC roots"; you describe the fix.
- [ ] **Ex J3.6.3 JFR recording.** Record 60 s of a CPU-busy program with `-XX:StartFlightRecording` (or `jcmd JFR.start`) and open it in JDK Mission Control. *Acceptance:* you identify the hottest method and the top allocation site.
- [ ] **Ex J3.6.4 High-CPU triage.** A program with one thread in a busy loop among 20 idle threads. *Acceptance:* you find the busy thread from OS tools (`top -H`) and match it to the Java stack in a thread dump (native thread id in hex).
- [ ] **Ex J3.6.5 VisualVM.** Monitor the J3.3 thread-pool exercise live: threads view, sampler, heap graph during a GC. *Acceptance:* screenshots or notes of what you observed.

### Must be able to do / explain
- [ ] Take thread dumps and heap dumps from a running JVM.
- [ ] Record and read a JFR recording.
- [ ] Find a memory leak with a heap analyzer.
- [ ] Triage high CPU and deadlocks.

**Estimated hours:** ~6 h

### Self-check questions
1. How do you take a thread dump and a heap dump of a running JVM?
2. What is JFR and why can it run in production?
3. What are the most common causes of memory leaks in Java?
4. Shallow vs retained size in a heap dump?
5. A service is at 100% CPU. How do you find the cause?
6. What does `-XX:+HeapDumpOnOutOfMemoryError` do?

---

**Answers**
1. Thread dump: `jcmd <pid> Thread.print` or `jstack <pid>`. Heap dump: `jcmd <pid> GC.heap_dump /path/file.hprof` (or `jmap -dump`), or automatically on OOM.
2. Java Flight Recorder is a built-in event recorder (CPU samples, allocations, GC, locks, I/O) with very low overhead (~1–2%), so it can be left on in production and dumped when something goes wrong.
3. Objects kept reachable unintentionally: static collections and caches without eviction, listeners/callbacks never removed, `ThreadLocal` values in pooled threads, inner classes holding outer references, class-loader leaks in redeployments, unclosed resources.
4. Shallow size is the memory of the object itself. Retained size is the memory that would be freed if that object were collected (everything only reachable through it). Leaks show up as objects with large retained size.
5. Find the process, then the hot threads (`top -H -p <pid>`), convert the thread id to hex, take a thread dump and find that `nid`; or profile with JFR/async-profiler to see the hottest methods. Also check GC activity — constant GC can burn CPU.
6. When an `OutOfMemoryError` occurs, the JVM writes a heap dump (to `-XX:HeapDumpPath`) so you can analyse what filled the heap after the fact.

---

# Part 4 — Build, testing, tooling (~19 h)

**Main resources for Part 4:**
- maven.apache.org guides and docs.gradle.org.
- JUnit 5 User Guide (junit.org/junit5/docs/current/user-guide).
- AssertJ (assertj.github.io/doc), Mockito (javadoc.io/doc/org.mockito/mockito-core → `Mockito` class docs).
- Testcontainers (java.testcontainers.org and testcontainers.com/guides).

---

## Module J4.1 — Maven & Gradle: lifecycle, plugins, multi-module (~6h)

**Topics:** Maven: the three lifecycles (clean, default, site), phases vs
goals, plugins (compiler, surefire, failsafe, jar, shade), dependency scopes
(compile, provided, runtime, test), transitive dependencies and conflict
mediation ("nearest wins"), `dependency:tree`, `dependencyManagement` and
BOMs, properties, profiles, the `settings.xml` and repositories, reproducible
builds; multi-module projects (parent POM, aggregator, inter-module
dependencies); **Gradle**: Kotlin DSL, tasks and the task graph, the `java`
plugin, configurations (`implementation` vs `api` vs `testImplementation`),
version catalogs (`libs.versions.toml`), the Gradle wrapper, build cache;
Maven vs Gradle trade-offs.

🐍 Parent POM + BOM ≈ a constraints file/lock file shared across packages;
Gradle is closer to a programmable build like `nox`/`invoke`.

### Lessons
- [ ] **J4.1.L1 Maven lifecycle.** maven.apache.org → "Introduction to the Build Lifecycle"; "Introduction to the POM"; "Introduction to the Dependency Mechanism" (scopes, transitive deps, dependency management, importing BOMs).
- [ ] **J4.1.L2 Multi-module.** maven.apache.org → "Guide to Working with Multiple Modules"; "Introduction to Build Profiles".
- [ ] **J4.1.L3 Plugins.** Maven Surefire and Failsafe plugin docs (usage pages); Baeldung "Maven Surefire and Failsafe Plugins" (or "Integration Testing with the Maven Failsafe Plugin").
- [ ] **J4.1.L4 Gradle.** docs.gradle.org → "Building Java Applications Sample", "Gradle Kotlin DSL Primer", "Build Lifecycle", "Structuring Projects with Gradle" (multi-project builds), "Version Catalogs", "The Java Library Plugin" (`api` vs `implementation`).
- [ ] **J4.1.L5 Comparison.** Baeldung "Ant vs Maven vs Gradle".

### Exercises (`java/J4.1-build-tools/`)
- [ ] **Ex J4.1.1 Multi-module Maven.** A parent with modules `domain`, `storage`, `cli` (reuse LedgerLite code). The parent holds `dependencyManagement` and plugin versions; modules declare dependencies without versions. *Acceptance:* `./mvnw -pl cli -am package` builds only what `cli` needs.
- [ ] **Ex J4.1.2 Dependency conflict.** Add two libraries that pull different versions of the same transitive dependency (e.g. two versions of `jackson-databind` or `guava`). *Acceptance:* you show it with `mvn dependency:tree`, explain which version wins and pin it with `dependencyManagement`.
- [ ] **Ex J4.1.3 Unit vs integration tests.** Configure Surefire for `*Test` and Failsafe for `*IT`. *Acceptance:* `mvn test` runs only unit tests; `mvn verify` runs both.
- [ ] **Ex J4.1.4 Same project in Gradle.** Recreate the multi-module build with Gradle Kotlin DSL, a version catalog and the wrapper. *Acceptance:* `./gradlew build` passes; `notes.md` compares the two builds (lines, speed, readability).
- [ ] **Ex J4.1.5 Import a BOM.** Import the JUnit BOM (`junit-bom`) and drop versions from JUnit dependencies. *Acceptance:* versions come from one place.

### Must be able to do / explain
- [ ] Explain Maven lifecycles, phases, goals and scopes.
- [ ] Set up a multi-module build with a parent POM and BOMs.
- [ ] Diagnose dependency conflicts with `dependency:tree`.
- [ ] Read and write a basic Gradle Kotlin DSL build.

**Estimated hours:** ~6 h

### Self-check questions
1. Phase vs goal in Maven?
2. What are the Maven dependency scopes?
3. How does Maven resolve two versions of the same transitive dependency?
4. What is a BOM, and why use `dependencyManagement`?
5. Surefire vs Failsafe?
6. Gradle `implementation` vs `api`?
7. Maven vs Gradle — how would you choose?

---

**Answers**
1. A phase is a step in a lifecycle (`compile`, `test`, `package`); a goal is a concrete plugin task (`compiler:compile`). Phases are bound to goals; running a phase runs all earlier phases and their bound goals.
2. `compile` (default, everywhere), `provided` (compile only, supplied at run time by the container), `runtime` (run and test only, e.g. JDBC drivers), `test` (tests only), `system` and `import` (BOMs in `dependencyManagement`).
3. "Nearest definition wins" in the dependency tree; for equal depth, the first declared wins. Override with an explicit dependency or `dependencyManagement`.
4. A Bill of Materials is a POM listing consistent versions of related artifacts. `dependencyManagement` centralizes versions so modules don't repeat them and all use the same versions.
5. Surefire runs unit tests in the `test` phase and fails the build immediately. Failsafe runs integration tests in `integration-test`/`verify`, so `post-integration-test` cleanup still runs before the build fails.
6. `api` dependencies are exposed to consumers of your library (they become part of its compile classpath); `implementation` dependencies are internal, which gives faster, better-isolated builds.
7. Maven: convention-heavy, declarative, very common in enterprises and Spring examples. Gradle: faster (incremental builds, build cache), flexible, used by Spring Boot itself and Android. Follow the team's standard; both work well.

---

## Module J4.2 — JUnit 5, AssertJ, parameterized tests, Mockito (~7h)

**Topics:** JUnit 5 architecture (Platform, Jupiter, Vintage); lifecycle
annotations (`@BeforeAll/@BeforeEach/@AfterEach/@AfterAll`), test instance
lifecycle, `@Nested`, `@DisplayName`, `@Tag`, `@Disabled`, `@Timeout`,
`@TempDir`, assumptions; **parameterized tests** (`@ValueSource`,
`@CsvSource`, `@MethodSource`, `@EnumSource`); dynamic tests; extensions
(`@ExtendWith`); **AssertJ** fluent assertions (collections,
exceptions with `assertThatThrownBy`, soft assertions, `extracting`);
**Mockito**: mocks vs stubs vs spies vs fakes, `when/thenReturn`,
`verify`, argument matchers, `ArgumentCaptor`, `@Mock`/`@InjectMocks` with
`MockitoExtension`, strict stubs, why not to mock what you don't own and not
to mock value objects; test naming and the Arrange–Act–Assert structure;
coverage with JaCoCo.

🐍 JUnit ≈ pytest (fixtures ≈ lifecycle methods/extensions, `parametrize` ≈
`@ParameterizedTest`); Mockito ≈ `unittest.mock`.

### Lessons
- [ ] **J4.2.L1 JUnit 5.** JUnit 5 User Guide → "Writing Tests": "Annotations", "Display Names", "Assertions", "Assumptions", "Disabling Tests", "Tagging and Filtering", "Test Instance Lifecycle", "Nested Tests", "Parameterized Tests", "Dynamic Tests", "Timeouts", "Built-in Extensions" (`@TempDir`).
- [ ] **J4.2.L2 AssertJ.** AssertJ docs → "AssertJ Core" → "Getting started", "Assertions guide" (common, collections, exceptions, soft assertions).
- [ ] **J4.2.L3 Mockito.** Mockito javadoc (`org.mockito.Mockito`) sections 1–10 and 30s on strictness; Baeldung "Mockito Tutorial" series ("Mockito – Using Spies", "Mockito ArgumentCaptor").
- [ ] **J4.2.L4 Test design.** Martin Fowler "Mocks Aren't Stubs"; Fowler "The Practical Test Pyramid" (Ham Vocke).
- [ ] **J4.2.L5 Coverage.** JaCoCo Maven plugin docs → "Maven Plug-in" usage.

### Exercises (`java/J4.2-testing/`)
- [ ] **Ex J4.2.1 Parameterized money tests.** For the `Money` record (J2.3): arithmetic, rounding and currency mismatch with `@CsvSource` and `@MethodSource`. *Acceptance:* ≥ 20 cases in ≤ 4 test methods; readable display names.
- [ ] **Ex J4.2.2 AssertJ everywhere.** Rewrite 10 JUnit assertions from LedgerLite with AssertJ, including one collection assertion with `extracting` and one exception assertion. *Acceptance:* failure messages are clearer (break one test on purpose to compare).
- [ ] **Ex J4.2.3 Mock a dependency.** `OrderService` (J2.6) with mocked `PaymentGateway` and `OrderRepository`: success, payment declined, repository throws. Use `ArgumentCaptor` to check the saved order. *Acceptance:* no real I/O; `verify` used only where the interaction is the behavior being tested.
- [ ] **Ex J4.2.4 Fake vs mock.** Implement an in-memory `FakeOrderRepository` and rewrite one test with it. *Acceptance:* `notes.md` compares both approaches and when you'd choose each.
- [ ] **Ex J4.2.5 Nested structure & coverage.** Organise `BankAccount` tests with `@Nested` classes per scenario ("when balance is zero", "when account is closed"); add JaCoCo. *Acceptance:* coverage report generated; ≥ 85% line coverage on the domain package; you name one thing coverage doesn't tell you.

### Must be able to do / explain
- [ ] Write clear JUnit 5 tests with lifecycle hooks, nesting and parameterization.
- [ ] Use AssertJ fluently, including exceptions and collections.
- [ ] Use Mockito correctly and explain mocks vs stubs vs fakes vs spies.
- [ ] Explain the test pyramid.

**Estimated hours:** ~7 h

### Self-check questions
1. What are the parts of JUnit 5 (Platform, Jupiter, Vintage)?
2. `@BeforeEach` vs `@BeforeAll`?
3. What are the parameter sources for `@ParameterizedTest`?
4. Mock vs stub vs spy vs fake?
5. Why "don't mock what you don't own"?
6. What is the test pyramid?
7. Is 100% coverage a good goal?

---

**Answers**
1. Platform: launches test frameworks on the JVM (used by IDEs/Maven). Jupiter: the JUnit 5 programming and extension model. Vintage: runs JUnit 3/4 tests on the platform.
2. `@BeforeEach` runs before every test method (fresh state). `@BeforeAll` runs once per class (static by default) for expensive shared setup.
3. `@ValueSource`, `@CsvSource`, `@CsvFileSource`, `@MethodSource`, `@EnumSource`, `@ArgumentsSource`, plus `@NullSource`/`@EmptySource`.
4. Stub: returns canned answers. Mock: also verifies interactions. Spy: wraps a real object, calling real methods unless stubbed. Fake: a working lightweight implementation (in-memory repository).
5. Third-party APIs can behave differently from your mock, so tests pass while production breaks. Wrap them behind your own interface (adapter) and test the adapter with integration tests (e.g. Testcontainers).
6. Many fast unit tests at the base, fewer integration tests in the middle, and few slow end-to-end tests at the top.
7. No. Coverage shows what code ran, not whether the assertions are meaningful. Aim for high coverage of important logic and meaningful tests; chasing 100% leads to brittle, low-value tests.

---

## Module J4.3 — Testcontainers (~3h)

**Topics:** why real dependencies in tests (H2 is not PostgreSQL/Oracle);
Testcontainers architecture (Docker API, Ryuk cleanup); `@Testcontainers`
and `@Container` with JUnit 5; `GenericContainer`, module containers
(`PostgreSQLContainer`, `OracleContainer` (`gvenzl/oracle-free`), Redis via
`GenericContainer`); wait strategies; mapped ports and dynamic config;
singleton containers shared across test classes; reusing containers locally;
init scripts; running in CI (GitHub Actions has Docker). Spring Boot
`@ServiceConnection` comes later in J7.4.

🐍 Same idea as `testcontainers-python` or the Docker-backed Postgres you used
in Track 2 B8.

### Lessons
- [ ] **J4.3.L1 Guide.** testcontainers.com/guides → "Getting started with Testcontainers for Java".
- [ ] **J4.3.L2 JUnit 5 integration.** java.testcontainers.org → "Quickstart" → "JUnit 5 Quickstart"; "Test framework integration" → "JUnit 5".
- [ ] **J4.3.L3 Features.** java.testcontainers.org → "Features" → "Networking and communicating with containers", "Waiting for containers to start or be ready", "Manual container lifecycle control" (singleton containers).
- [ ] **J4.3.L4 Modules.** java.testcontainers.org → "Modules" → "Databases" → "Postgres Module", "Oracle Free Module".

### Exercises (`java/J4.3-testcontainers/`)
- [ ] **Ex J4.3.1 Postgres container.** A JUnit 5 test that starts `postgres:17`, creates a table with plain JDBC (`DriverManager` is enough here — JDBC is taught properly in J5.1), inserts and reads a row. *Acceptance:* the test passes on a machine with only Docker installed.
- [ ] **Ex J4.3.2 Redis container.** A `GenericContainer("redis:7")` with an exposed port and a wait strategy; `PING` it with a tiny client (e.g. Jedis/Lettuce) or a raw socket. *Acceptance:* you explain why you must use the mapped port, not 6379.
- [ ] **Ex J4.3.3 Singleton container.** Share one Postgres container across three test classes. *Acceptance:* the container starts once (visible in logs); the total test time is measured before/after.
- [ ] **Ex J4.3.4 Oracle Free.** Start `gvenzl/oracle-free:23-slim` via the Oracle Free module and run `SELECT 1 FROM dual`. *Acceptance:* note the startup time and how you would speed it up locally (reuse, faster image tag).

### Must be able to do / explain
- [ ] Write integration tests with Testcontainers and JUnit 5.
- [ ] Explain wait strategies, mapped ports and container lifecycle options.
- [ ] Explain why Testcontainers beats H2/in-memory substitutes.

**Estimated hours:** ~3 h

### Self-check questions
1. Why not use H2 instead of a real database in tests?
2. How does Testcontainers make sure containers are cleaned up?
3. Why can't you hard-code the container port?
4. What is a wait strategy?
5. How do you speed up Testcontainers-based test suites?

---

**Answers**
1. H2 has a different SQL dialect, types, locking and features (no `SKIP LOCKED` semantics, JSONB, PL/SQL…). Tests pass on H2 and fail in production; Testcontainers tests against the same database engine and version you run.
2. A sidecar container (Ryuk) watches the test JVM's connection and removes containers, networks and volumes when the JVM exits, even if it crashes.
3. Testcontainers maps the container port to a random free host port to avoid conflicts; ask it with `getMappedPort()`/`getJdbcUrl()`.
4. A rule for when the container is "ready" (a log line, an open port, an HTTP health check, a successful DB query), so tests don't start before the service accepts connections.
5. Singleton containers shared across classes, container reuse in local dev, smaller/faster images, running test classes in parallel with separate schemas, and keeping the number of distinct containers small.

---

## Module J4.4 — Checkstyle / SpotBugs / SonarLint + SLF4J / Logback (~3h)

**Topics:** code style and static analysis: **Checkstyle** (style rules,
Google/Sun configs, failing the build), **SpotBugs** (bytecode analysis for
real bugs: null dereferences, bad equals, concurrency issues) and its Maven
plugin, **SonarLint/SonarQube for IDE** (in-IDE analysis), Error Prone and
PMD (overview); formatting (Spotless / google-java-format, overview);
**logging**: SLF4J as the facade, Logback as the implementation, log levels,
parameterized messages (`log.info("x={}", x)`), logging exceptions, MDC for
request ids, `logback.xml` (appenders, patterns, rolling files, JSON
encoders overview), don't log secrets; `System.out` vs logging.

🐍 Checkstyle/SpotBugs ≈ ruff + mypy's bug-finding side; SLF4J/Logback ≈
`logging` + `structlog` (MDC ≈ contextvars-bound log context).

### Lessons
- [ ] **J4.4.L1 Checkstyle.** checkstyle.org → "Getting started"; Maven Checkstyle Plugin → "Usage".
- [ ] **J4.4.L2 SpotBugs.** spotbugs.readthedocs.io → "Introduction", "Using the SpotBugs Maven Plugin", "Bug descriptions" (skim the categories).
- [ ] **J4.4.L3 SonarLint.** SonarQube for IDE (formerly SonarLint) docs → IntelliJ "Getting started".
- [ ] **J4.4.L4 SLF4J.** slf4j.org → "SLF4J user manual" (Hello World, typical usage pattern, binding with a logging framework at deployment time, MDC).
- [ ] **J4.4.L5 Logback.** logback.qos.ch → "Logback documentation" → "Chapter 3: Configuration", "Chapter 4: Appenders" (ConsoleAppender, RollingFileAppender), "Chapter 6: Layouts", "Chapter 8: Mapped Diagnostic Context".

### Exercises (`java/J4.4-quality-logging/`)
- [ ] **Ex J4.4.1 Quality gates.** Add Checkstyle (Google config, adjusted indentation if you like) and SpotBugs to the multi-module build from J4.1 so that `mvn verify` fails on violations. *Acceptance:* you fix all findings or justify suppressions in a comment.
- [ ] **Ex J4.4.2 SpotBugs finds bugs.** Write 4 deliberate bugs (equals without hashCode, ignored return value of `String.trim`, possible null dereference, inconsistent synchronization) and see which ones SpotBugs reports. *Acceptance:* results table in `notes.md`.
- [ ] **Ex J4.4.3 Logging setup.** Replace all `System.out.println` in LedgerLite (except the CLI output itself) with SLF4J + Logback; configure console + rolling file appenders and a pattern with timestamp, level, logger and thread. *Acceptance:* `DEBUG` logs appear only when you change the level in `logback.xml`.
- [ ] **Ex J4.4.4 MDC.** Put a generated `commandId` into the MDC at the start of each CLI command and print it in every log line; clear it in `finally`. *Acceptance:* two commands show different ids; you explain why clearing matters with thread pools.
- [ ] **Ex J4.4.5 Logging hygiene.** Show the difference between `log.debug("x=" + expensive())` and `log.debug("x={}", value)`, and log an exception with its stack trace correctly. *Acceptance:* you explain why string concatenation in log calls is wasteful and how to pass the exception as the last argument.

### Must be able to do / explain
- [ ] Add Checkstyle and SpotBugs to a Maven build and fail on violations.
- [ ] Explain SLF4J (facade) vs Logback (implementation).
- [ ] Configure Logback appenders and patterns, and use MDC.
- [ ] Follow logging best practices (levels, parameters, exceptions, no secrets).

**Estimated hours:** ~3 h

### Self-check questions
1. Checkstyle vs SpotBugs — what does each catch?
2. Why use SLF4J instead of Logback directly?
3. Why use `{}` placeholders instead of string concatenation?
4. How do you log an exception with its stack trace in SLF4J?
5. What is MDC and what is the pitfall with thread pools?
6. Name three things you must never log.

---

**Answers**
1. Checkstyle checks source style and conventions (naming, formatting, Javadoc). SpotBugs analyses bytecode for probable bugs (null dereferences, bad equals/hashCode, concurrency mistakes, resource leaks).
2. SLF4J is a facade: libraries and your code log against one API, and the actual backend (Logback, Log4j2) is chosen at deployment. It also unifies logs from libraries using different frameworks via bridges.
3. The message is only formatted if the level is enabled, avoiding wasted string building; it's also cleaner.
4. Pass it as the last argument: `log.error("Payment {} failed", id, e)` — SLF4J treats a trailing `Throwable` as the exception to print with its stack trace.
5. Mapped Diagnostic Context: a per-thread map of values (request id, user id) that the log pattern can print. With thread pools, threads are reused, so values leak into other tasks unless you clear them in `finally` (and you must copy MDC into tasks you hand off to other threads).
6. Passwords and secrets/tokens/API keys, full card numbers or other payment data, and sensitive personal data (e.g. national ids, health data) — mask or omit them.

---

## Track 4A progress summary

Tick **Done** when the module's "Must be able to" checklist (or the project's
Definition of Done) is complete.

| Item | Name | Hours | Lessons | Exercises | Done |
|---|---|---|---|---|---|
| J1.1 | JDK/JRE/JVM, IntelliJ, bytecode | 4 | 5 | 5 | [ ] |
| J1.2 | Types, operators, control flow, arrays | 6 | 5 | 5 | [ ] |
| J1.3 | Strings | 3 | 4 | 4 | [ ] |
| J1.4 | Methods & packages | 3 | 4 | 4 | [ ] |
| J1.5 | OOP I | 6 | 5 | 5 | [ ] |
| J1.6 | OOP II | 6 | 4 | 5 | [ ] |
| J1.7 | equals/hashCode/toString | 3 | 3 | 4 | [ ] |
| J1.8 | Exceptions | 4 | 4 | 5 | [ ] |
| J1.9 | Enums, wrappers, autoboxing | 3 | 4 | 4 | [ ] |
| J1.10 | Generics | 5 | 3 | 5 | [ ] |
| J1.11 | Collections Framework | 10 | 6 | 6 | [ ] |
| J1.12 | I/O, NIO.2, java.time | 5 | 4 | 6 | [ ] |
| J1.13 | Maven + JUnit basics | 3 | 4 | 4 | [ ] |
| **JP1** | **LedgerLite CLI · Junior** | **25** | — | 5 milestones | [ ] |
| J2.1 | Lambdas & functional interfaces | 5 | 4 | 5 | [ ] |
| J2.2 | Streams & Optional | 8 | 5 | 6 | [ ] |
| J2.3 | Records, sealed, patterns, text blocks, var | 5 | 5 | 5 | [ ] |
| J2.4 | Annotations, reflection, JPMS | 5 | 5 | 4 | [ ] |
| J2.5 | Immutability & design patterns | 8 | 5 | 6 | [ ] |
| J2.6 | SOLID & Effective Java | 6 | 5 | 5 | [ ] |
| J3.1 | Threads, synchronized, volatile, JMM | 8 | 5 | 5 | [ ] |
| J3.2 | Locks, atomics, concurrent collections | 6 | 4 | 6 | [ ] |
| J3.3 | ExecutorService & CompletableFuture | 6 | 5 | 5 | [ ] |
| J3.4 | Deadlocks, virtual threads, structured concurrency | 6 | 5 | 5 | [ ] |
| J3.5 | JVM internals | 8 | 5 | 5 | [ ] |
| J3.6 | Diagnostics | 6 | 5 | 5 | [ ] |
| J4.1 | Maven & Gradle | 6 | 5 | 5 | [ ] |
| J4.2 | JUnit 5, AssertJ, Mockito | 7 | 5 | 5 | [ ] |
| J4.3 | Testcontainers | 3 | 4 | 4 | [ ] |
| J4.4 | Static analysis & logging | 3 | 5 | 5 | [ ] |
| | **Modules total (Parts 1–4)** | **~157** | **132** | **143** | |
| | **With JP1** | **~182** | | | |

Next: [`04b-java-databases.md`](04b-java-databases.md) — Part 5, databases
from Java.
