# Track 4C — Spring Framework, Spring Boot & Production (Parts 6–9)

**Goal:** go from "I can write Java and talk to a database with JDBC/JPA" to
"I can design, build, secure, test, ship and operate Spring Boot services —
including ones where Oracle PL/SQL owns the business rules and Spring owns the
boundary."

**Required knowledge:**
- [Track 4A — Java Core (Parts 1–4)](04a-java-core.md), all of it.
- [Track 4B — Databases from Java (Part 5)](04b-java-databases.md), all of it.
- Track 1C Part 3 (Oracle SQL + PL/SQL) for the Oracle projects (JM2, JM3, JMP3).
- Backend *concepts* (HTTP/REST, auth, caching, messaging, event-driven
  patterns, Kubernetes) are taught with Python in Track 2. This file teaches
  the **Java/Spring way** of doing them and names the Track 2 module where the
  concept itself lives.

**Estimated hours in this file:** ~145 h of modules + ~440 h of core projects
(JP3, JM1, JM2, JM3, JMP1, JMP2, JMP3), plus OPTIONAL projects JO1 and JO2
(~110 h).

**How to use this file**
- Tick every lesson, exercise, checklist item and milestone as you finish it.
- **No solutions here.** Specs, acceptance criteria and checklists only — you
  write every line of code. Ask your mentor for reviews and concepts, not for
  finished implementations.
- Every tool a project uses is taught in an earlier module of Track 4
  (4A/4B/4C). Concepts may come from other tracks; they are listed under
  "Required knowledge".
- Module exercises live in this repo under `java/<Jx.y-slug>/` (one Maven or
  Gradle project per module is fine). Each project gets **its own GitHub repo**.
- Self-check questions close every module: answer out loud first, then read the
  answers below the `---` separator.

> **Python ↔ Spring cheat line.** FastAPI `Depends()` ≈ Spring constructor
> injection; Django `settings.py` + env ≈ `application.yml` + profiles; Django
> middleware ≈ servlet filters / Spring Security filter chain; SQLAlchemy
> `Session` ≈ JPA `EntityManager` (persistence context); `transaction.atomic`
> ≈ `@Transactional` (but proxy-based — see J6.3).

---

# Part 6 — Spring Framework Core

## Module J6.1 — IoC Container & Dependency Injection (~6h)

**Topics:** Inversion of Control vs "new-ing" dependencies; the
`ApplicationContext` and `BeanFactory`; bean definitions; constructor vs setter
vs field injection (and why constructor injection wins: immutability,
testability, no hidden dependencies); `@Component`, `@Service`, `@Repository`,
`@Controller` stereotypes; component scanning and its base packages;
`@Configuration` + `@Bean` (full vs lite mode, CGLIB-enhanced configuration
classes); `@Primary`, `@Qualifier`, injecting `List<T>`/`Map<String,T>`;
`ObjectProvider` and lazy lookup; bean scopes (singleton, prototype, request,
session) and the "prototype inside singleton" trap; bean lifecycle
(`@PostConstruct`, `@PreDestroy`, `InitializingBean`), `BeanPostProcessor`
as the hook that makes proxies possible; circular dependencies and why Spring
Boot forbids them by default.

*Python comparison:* FastAPI's `Depends()` resolves per request and you wire it
yourself; Spring builds one object graph at startup and fails fast if it
cannot.

### Lessons
- [ ] **J6.1.L1 The container.** Spring Framework Reference → Core Technologies → "The IoC Container": §"Introduction to the Spring IoC Container and Beans", §"Container Overview", §"Bean Overview".
- [ ] **J6.1.L2 Dependencies.** Same chapter → §"Dependencies" → "Dependency Injection" (constructor-based vs setter-based) and "Dependencies and Configuration in Detail".
- [ ] **J6.1.L3 Java config & scanning.** Same chapter → §"Java-based Container Configuration" (`@Bean`, `@Configuration`, full vs lite mode) and §"Classpath Scanning and Managed Components".
- [ ] **J6.1.L4 Scopes & lifecycle.** Same chapter → §"Bean Scopes" (incl. "Singleton Beans with Prototype-bean Dependencies") and §"Customizing the Nature of a Bean" (lifecycle callbacks).
- [ ] **J6.1.L5 Book view.** *Spring in Action*, 6th ed., Ch. 1 "Getting started with Spring" (§1.1 "What is Spring?"). Baeldung: "Why Constructor Injection Is Preferred" / "Constructor Dependency Injection in Spring".

### Exercises (`java/J6.1-ioc/`)
- [ ] **Ex J6.1.1 Container without Boot.** Plain `spring-context` dependency, no Spring Boot. Build an `AnnotationConfigApplicationContext` for a tiny "notification" app: `NotificationService` depends on a `MessageSender` interface with two implementations (`EmailSender`, `SmsSender`). *Acceptance:* startup fails with a clear `NoUniqueBeanDefinitionException` until you resolve it with `@Primary`; then switch to `@Qualifier` and show both approaches in two commits.
- [ ] **Ex J6.1.2 `@Bean` vs scanning.** Register the same beans once via component scanning and once via a `@Configuration` class with `@Bean` methods. *Acceptance:* a test proves that calling one `@Bean` method from another inside a `@Configuration` class returns the **same** singleton, and that it does **not** when the class is not annotated with `@Configuration` (lite mode). Write one paragraph explaining why.
- [ ] **Ex J6.1.3 Scope trap.** A singleton `ReportService` holds a prototype `ReportBuilder`. *Acceptance:* a test shows the builder is the same instance across calls (the trap), then fix it with `ObjectProvider<ReportBuilder>` and prove each call gets a new instance.
- [ ] **Ex J6.1.4 Lifecycle log.** Log every lifecycle phase (constructor, dependency set, `@PostConstruct`, context refreshed, `@PreDestroy`) for one bean, plus a custom `BeanPostProcessor` that logs `before/afterInitialization`. *Acceptance:* the log order matches the reference documentation; commit the log output in `notes.md`.
- [ ] **Ex J6.1.5 Unit test without Spring.** Write a JUnit 5 + Mockito test for `NotificationService` that does **not** start any Spring context. *Acceptance:* test runs in < 100 ms; explain in `notes.md` why constructor injection made this trivial and field injection would not.

### Must be able to do / explain
- [ ] Explain IoC and DI and what the container does at startup.
- [ ] Justify constructor injection over field injection with three reasons.
- [ ] Resolve "more than one bean of type X" three different ways.
- [ ] Explain full vs lite `@Configuration` mode and inter-bean method calls.
- [ ] Explain singleton vs prototype scope and the prototype-in-singleton problem.
- [ ] Describe the bean lifecycle and where `BeanPostProcessor` fits.

**Estimated hours:** ~6 h

### Self-check interview questions
1. What is Inversion of Control, and how is DI one form of it?
2. Why is constructor injection recommended over field injection?
3. What is the difference between `@Component` and `@Bean`?
4. What happens when two beans implement the same interface and you inject the interface?
5. What is the default bean scope, and is a singleton bean thread-safe by default?
6. What does a `BeanPostProcessor` do, and which Spring features depend on it?
7. Why does Spring Boot fail on circular dependencies by default, and what is the right fix?

---

**Answers**
1. IoC means the framework, not your code, controls object creation and wiring. DI is the concrete mechanism: dependencies are passed in (constructor/setter) instead of the object looking them up or constructing them.
2. Dependencies become `final` (immutable), mandatory dependencies are explicit in the signature, the object can be constructed in a plain unit test without reflection, and too many constructor params make a design smell visible.
3. `@Component` marks a class for component scanning — Spring instantiates it. `@Bean` is a factory method in a `@Configuration` class — you control instantiation, useful for third-party classes you cannot annotate.
4. Startup fails with `NoUniqueBeanDefinitionException` unless one is `@Primary`, the injection point uses `@Qualifier`, the parameter name matches a bean name, or you inject a `List`/`Map` of all implementations.
5. Singleton (one instance per container). No — Spring does not synchronise anything; a singleton must be stateless or guard its mutable state itself.
6. It gets a hook before and after each bean's initialisation and can return a different object (e.g. a proxy). AOP, `@Transactional`, `@Async`, `@Cacheable`, and `@Validated` method validation rely on it.
7. Circular dependencies usually signal two classes that should be split or merged; with constructor injection they cannot be constructed at all. Fix the design: extract the shared part into a third bean, or invert one dependency with an event.

---

## Module J6.2 — Profiles & Properties (~2h)

**Topics:** `Environment` and `PropertySource`s; `@Value` and its limits;
property placeholders and defaults; `@PropertySource`; profiles (`@Profile`,
`spring.profiles.active`, profile groups); environment-specific beans (e.g. a
fake payment client in `dev`); why secrets never go in committed property files.

*Python comparison:* like `pydantic-settings` reading env vars + `.env`, with
profiles playing the role of `settings/dev.py` vs `settings/prod.py`.

### Lessons
- [ ] **J6.2.L1 Environment abstraction.** Spring Framework Reference → "The IoC Container" → §"Environment Abstraction" (Bean Definition Profiles, `PropertySource` Abstraction, `@PropertySource`).
- [ ] **J6.2.L2 `@Value`.** Same chapter → §"Annotation-based Container Configuration" → "Using `@Value`".
- [ ] **J6.2.L3 Baeldung.** "Spring Profiles" and "A Quick Guide to Spring @Value".

### Exercises (`java/J6.2-profiles/`)
- [ ] **Ex J6.2.1 Two environments.** A `ExchangeRateClient` interface with `FakeExchangeRateClient` (`@Profile("dev")`) and `HttpExchangeRateClient` (`@Profile("prod")`). *Acceptance:* a test starts the context with each profile and asserts the right implementation is injected; with no profile, startup fails with a clear message (not a silent default).
- [ ] **Ex J6.2.2 Property precedence.** Define `app.greeting` in a properties file, override it with a JVM system property, then with an OS environment variable. *Acceptance:* `notes.md` records which value won each time and matches the documented order.
- [ ] **Ex J6.2.3 Missing property.** Inject a required property with no default. *Acceptance:* the startup error message names the missing key; then add a sensible default only where a default is genuinely safe and explain why the DB password must never get one.

### Must be able to do / explain
- [ ] Activate a profile three ways (property, env var, test annotation).
- [ ] Explain property source precedence at a high level.
- [ ] Explain why `@Value` is fine for one value but not for a group of related settings (preview of `@ConfigurationProperties` in J7.1).

**Estimated hours:** ~2 h

### Self-check interview questions
1. What is a Spring profile and when would you use one?
2. How do you activate a profile in production vs in a test?
3. What is the difference between `@Value("${x}")` and `@Value("${x:default}")`?
4. Why should secrets not be in `application.properties`?
5. Can a bean belong to several profiles, or be excluded from one?

---

**Answers**
1. A named set of bean definitions/properties active only in some environments — e.g. fake external clients in `dev`, real ones in `prod`.
2. Production: `SPRING_PROFILES_ACTIVE` env var (or `--spring.profiles.active`). Tests: `@ActiveProfiles("...")`.
3. The first fails at startup if `x` is missing; the second silently uses `default`. Fail-fast is safer for anything environment-specific.
4. The file is committed to Git and baked into images; anyone with repo or image access gets the secret. Inject secrets from the environment or a secret manager.
5. Yes: `@Profile({"dev","test"})` for several, `@Profile("!prod")` to exclude one; profile expressions support `&`, `|`, `!`.

---

## Module J6.3 — AOP, Proxies & How `@Transactional` Really Works (~5h)

**Topics:** cross-cutting concerns; AOP vocabulary (aspect, join point, pointcut,
advice, weaving); Spring AOP is **proxy-based** — JDK dynamic proxies
(interfaces) vs CGLIB subclass proxies; `@Aspect`, `@Before`, `@Around`,
`@AfterThrowing`, pointcut expressions (`execution`, `@annotation`); advice
ordering (`@Order`); **declarative transactions**: `@Transactional` is an
around-advice on a proxy that asks the `PlatformTransactionManager` to
begin/commit/rollback; pitfalls: **self-invocation** (`this.method()` bypasses
the proxy), `private`/`final` methods are not proxied, **checked exceptions do
not roll back by default**, catching an exception inside the method hides it
from the proxy, `readOnly = true` semantics, `@Transactional` on the class vs
method; other proxy-based features (`@Async`, `@Cacheable`) share the same
pitfalls.

*Python comparison:* a decorator (Track 1A.2) wraps a function at definition
time; a Spring proxy wraps a **bean** at container startup, so calls from inside
the same object never go through the wrapper.

### Lessons
- [ ] **J6.3.L1 AOP concepts.** Spring Framework Reference → Core Technologies → "Aspect Oriented Programming with Spring": §"AOP Concepts", §"Spring AOP Capabilities and Goals", §"AOP Proxies".
- [ ] **J6.3.L2 @AspectJ style.** Same chapter → §"@AspectJ support" (Declaring an Aspect, Declaring a Pointcut, Declaring Advice, Advice Ordering).
- [ ] **J6.3.L3 Proxying mechanisms.** Same chapter → §"Proxying Mechanisms" → "Understanding AOP Proxies" (the self-invocation explanation with diagrams).
- [ ] **J6.3.L4 Declarative transactions.** Spring Framework Reference → Data Access → "Transaction Management": §"Understanding the Spring Framework's Declarative Transaction Implementation", §"Rolling Back a Declarative Transaction", §"Using `@Transactional`" (read the note on proxy mode and self-invocation).
- [ ] **J6.3.L5 Real-world pitfalls.** Vlad Mihalcea: "The best way to use the Spring Transactional annotation"; Baeldung: "Transactions with Spring and JPA" and "Spring AOP vs AspectJ".

### Exercises (`java/J6.3-aop/`)
- [ ] **Ex J6.3.1 Timing aspect.** Write a `@Timed` custom annotation and an `@Around` aspect that logs method name + duration via SLF4J (J4.4). *Acceptance:* annotated methods on two beans are logged; a method called via `this.` from inside the same bean is **not** logged — prove it with a test and explain it in `notes.md`.
- [ ] **Ex J6.3.2 See the proxy.** Print `bean.getClass()` for a bean with and without an interface, with and without `@Transactional`. *Acceptance:* you can point at `$Proxy…` vs `…$$SpringCGLIB$$…` and explain when each is used.
- [ ] **Ex J6.3.3 Rollback rules lab.** A `TransferService` on an H2 or Testcontainers Postgres DB (J4.3) inserts two rows in one `@Transactional` method, then throws. Run four variants: `RuntimeException`, checked `Exception`, checked with `rollbackFor = Exception.class`, and exception caught inside the method. *Acceptance:* a parameterized test (J4.2) asserts the row count after each variant; the results table goes in `notes.md`.
- [ ] **Ex J6.3.4 Self-invocation fix.** `OrderService.placeOrder()` (non-transactional) calls `this.saveOrder()` (`@Transactional`). *Acceptance:* a test proves no transaction was active inside `saveOrder` (`TransactionSynchronizationManager.isActualTransactionActive()`); fix it by moving `saveOrder` to another bean, and explain why this is better than self-injection.
- [ ] **Ex J6.3.5 Aspect ordering.** Two aspects (`@Timed` and an audit aspect) on the same method. *Acceptance:* control and test their order with `@Order`; document which runs "outside" whom.

### Must be able to do / explain
- [ ] Explain the proxy model and why self-invocation bypasses advice.
- [ ] Explain JDK dynamic proxy vs CGLIB proxy and when Spring Boot uses each.
- [ ] State the default rollback rules and how to change them.
- [ ] List five `@Transactional` pitfalls and how to avoid each.
- [ ] Write an `@Around` advice with a pointcut on a custom annotation.

**Estimated hours:** ~5 h

### Self-check interview questions
1. How does `@Transactional` work under the hood?
2. Why doesn't `@Transactional` work when a method calls another method of the same class?
3. Does a checked exception roll back a Spring transaction by default?
4. What is the difference between a JDK dynamic proxy and a CGLIB proxy?
5. What does `readOnly = true` actually do?
6. Why is `@Transactional` on a `private` method ignored?
7. You catch an exception inside a `@Transactional` method and log it. What happens to the transaction?
8. What is the difference between Spring AOP and AspectJ?

---

**Answers**
1. Spring wraps the bean in a proxy. On each call the proxy's transaction interceptor asks the `PlatformTransactionManager` to start (or join) a transaction, invokes the real method, then commits — or rolls back if a rollback-worthy exception escapes.
2. `this.method()` calls the target object directly, not the proxy, so no interceptor runs. Move the method to another bean (or use AspectJ weaving).
3. No. By default only unchecked exceptions (`RuntimeException`, `Error`) roll back; checked exceptions commit. Use `rollbackFor`.
4. JDK proxies implement the bean's interfaces and delegate; CGLIB generates a subclass at runtime. Spring Boot defaults to CGLIB (`proxyTargetClass=true`), which cannot proxy `final` classes/methods.
5. It is a hint: Spring sets the JDBC connection read-only and Hibernate skips dirty checking / flushes (`FlushMode.MANUAL`); some drivers/DBs optimise read-only transactions. It does not by itself block writes on every database.
6. Proxies can only intercept calls that go through the proxy's public (or, with CGLIB, non-private, non-final) methods; private methods are invisible to a subclass proxy.
7. The proxy sees a normal return and commits. If a nested component already marked the transaction rollback-only, you get `UnexpectedRollbackException` at commit instead. Either rethrow, or mark rollback explicitly.
8. Spring AOP is runtime, proxy-based and only advises Spring bean method calls. AspectJ weaves bytecode (compile/load time) and can advise field access, constructors, and self-invocation.

---

## Module J6.4 — Spring Events (~2h)

**Topics:** `ApplicationEventPublisher`; `@EventListener`; synchronous by
default (same thread, same transaction); `@Async` listeners; ordering;
**`@TransactionalEventListener`** and its phases (`AFTER_COMMIT`,
`AFTER_ROLLBACK`, `BEFORE_COMMIT`); why "send the email after commit" belongs in
`AFTER_COMMIT`; the gap that remains (process crash after commit, before the
listener) — the outbox pattern (Track 2 B25) closes it.

*Python comparison:* like Django's `transaction.on_commit()` (Track 2 B13).

### Lessons
- [ ] **J6.4.L1 Standard and custom events.** Spring Framework Reference → "The IoC Container" → §"Additional Capabilities of the ApplicationContext" → "Standard and Custom Events" (incl. "Annotation-based Event Listeners", "Asynchronous Listeners", "Ordering Listeners").
- [ ] **J6.4.L2 Transaction-bound events.** Spring Framework Reference → "Transaction Management" → §"Transaction-bound Events".
- [ ] **J6.4.L3 Baeldung.** "Spring Events" and "Transaction-bound Events in Spring".

### Exercises (`java/J6.4-events/`)
- [ ] **Ex J6.4.1 Sync listener.** `UserRegisteredEvent` published from a `@Transactional` service; an `@EventListener` writes a welcome row. *Acceptance:* a test shows the listener runs in the **same** transaction (it is rolled back if the service throws after publishing).
- [ ] **Ex J6.4.2 After-commit.** Replace it with `@TransactionalEventListener(phase = AFTER_COMMIT)` that "sends an email" (logs + records in a fake sender). *Acceptance:* tests prove no email on rollback and exactly one on commit.
- [ ] **Ex J6.4.3 Crash gap.** Write in `notes.md` a 5-line failure scenario where the after-commit email is lost, and name the pattern that fixes it (B25).

### Must be able to do / explain
- [ ] Publish and consume a custom event.
- [ ] Explain the transactional behaviour of a plain `@EventListener`.
- [ ] Choose the right `@TransactionalEventListener` phase and explain its crash gap.

**Estimated hours:** ~2 h

### Self-check interview questions
1. Are Spring application events synchronous or asynchronous by default?
2. What is `@TransactionalEventListener` for?
3. If a listener in `AFTER_COMMIT` throws, is the original transaction rolled back?
4. Why are events not a replacement for a message broker?
5. How would you guarantee the side effect happens even if the app crashes right after commit?

---

**Answers**
1. Synchronous — the listener runs on the publisher's thread, inside its transaction if one is active.
2. To run a listener at a specific transaction phase, typically after a successful commit, so side effects (emails, messages) never happen for rolled-back data.
3. No — the transaction is already committed; the exception is logged/propagated to the caller but cannot undo the commit.
4. They are in-memory and in-process: lost on crash, not visible to other services, no retries or persistence.
5. Transactional outbox: write the event to an outbox table in the same transaction, and have a relay publish it afterwards with retries (Track 2 B25; Java in J8.3).

---

# Part 7 — Spring Boot & Ecosystem

## Module J7.1 — Spring Boot Fundamentals (~4h)

**Topics:** what Boot adds on top of the Framework; `@SpringBootApplication` =
`@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`; starters as
curated dependency sets; **auto-configuration** and `@Conditional…` annotations
(`@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`);
the condition evaluation report (`--debug`); backing off when you define your
own bean; **externalized configuration**: `application.yml`, profile-specific
files, environment variables, relaxed binding, the precedence order;
**`@ConfigurationProperties`** with records and validation; the executable
(fat) JAR; Spring Initializr; DevTools; **Actuator basics** (`/actuator/health`,
`/actuator/metrics`, exposing endpoints — full observability comes in J7.12).

### Lessons
- [ ] **J7.1.L1 Getting started.** Spring Boot Reference → "Tutorials" → "Developing Your First Spring Boot Application"; spring.io/guides: "Building an Application with Spring Boot".
- [ ] **J7.1.L2 Auto-configuration.** Spring Boot Reference → "Developing with Spring Boot" → "Auto-configuration" (incl. "Gradually Replacing Auto-configuration", "Disabling Specific Auto-configuration Classes"); "Core Features" → "Creating Your Own Auto-configuration" → "Condition Annotations" (read only, do not build one yet).
- [ ] **J7.1.L3 Externalized configuration.** Spring Boot Reference → "Core Features" → "Externalized Configuration" (the ordered list of sources, "Type-safe Configuration Properties", "Relaxed Binding", "@ConfigurationProperties Validation").
- [ ] **J7.1.L4 Book view.** *Spring in Action*, 6th ed., Ch. 1 (§1.2 "Initializing a Spring application") and Ch. 6 "Working with configuration properties".
- [ ] **J7.1.L5 Actuator basics.** Spring Boot Reference → "Production-ready Features" → "Enabling Production-ready Features" and "Endpoints" (exposing, `health`, `metrics`).

### Exercises (`java/J7.1-boot-basics/`)
- [ ] **Ex J7.1.1 Initializr tour.** Generate a Boot 3.x project (Java 25, Maven) with `web` only. *Acceptance:* `notes.md` lists what the `spring-boot-starter-web` starter brought in (`mvn dependency:tree`), and which auto-configurations matched (`--debug` report, 5 examples explained).
- [ ] **Ex J7.1.2 Back-off.** Define your own `ObjectMapper` bean with a custom date format. *Acceptance:* the condition report shows `JacksonAutoConfiguration`'s mapper backed off (`@ConditionalOnMissingBean`); a test asserts the custom format is used.
- [ ] **Ex J7.1.3 Typed config.** Bind `app.loan.max-amount`, `app.loan.currencies` (list) and `app.loan.grace-period` (`Duration`) into a validated `@ConfigurationProperties` **record**. *Acceptance:* invalid values (negative amount, empty currency list) fail startup with a readable message; env var `APP_LOAN_MAXAMOUNT` overrides the YAML value.
- [ ] **Ex J7.1.4 Fat JAR.** Build the executable JAR and run it with `--spring.profiles.active=prod`. *Acceptance:* `notes.md` explains the JAR layout (`BOOT-INF/classes`, `BOOT-INF/lib`) and how it differs from a plain JAR (J4.1).

### Must be able to do / explain
- [ ] Explain what `@SpringBootApplication` expands to.
- [ ] Explain how auto-configuration decides what to create, and how to see why.
- [ ] Override an auto-configured bean correctly.
- [ ] Bind a group of settings with `@ConfigurationProperties` + validation.
- [ ] Explain the external config precedence at a high level (command line > env > profile file > default file).

**Estimated hours:** ~4 h

### Self-check interview questions
1. What does Spring Boot add on top of the Spring Framework?
2. How does auto-configuration work?
3. How do you find out why a certain bean was or was not auto-configured?
4. `@Value` vs `@ConfigurationProperties` — when do you use each?
5. What is a starter?
6. How do you override one property in production without rebuilding the JAR?

---

**Answers**
1. Opinionated defaults: auto-configuration, starters, embedded server, externalized configuration, executable JARs, Actuator, and test slices — so you write almost no wiring code.
2. Auto-configuration classes (listed in `META-INF/spring/…AutoConfiguration.imports`) are `@Configuration` classes guarded by `@Conditional…` annotations; they apply only if, e.g., a class is on the classpath and you have not defined the bean yourself.
3. Run with `--debug` (or `debug=true`) to print the condition evaluation report; Actuator's `/actuator/conditions` shows the same at runtime.
4. `@Value` for a single, simple value; `@ConfigurationProperties` for a related group — type-safe, validated, relaxed binding, IDE metadata, easy to test.
5. A dependency descriptor that pulls in a coherent set of libraries (and triggers the matching auto-configuration), e.g. `spring-boot-starter-data-jpa`.
6. Environment variable (`SPRING_DATASOURCE_URL`, relaxed binding) or a command-line argument; both outrank files inside the JAR.

---

## Module J7.2 — Spring MVC, REST, Validation & Error Handling (~8h)

**Topics:** `DispatcherServlet` request flow; `@RestController`,
`@RequestMapping` family, `@PathVariable`, `@RequestParam`, `@RequestBody`,
`ResponseEntity` and status codes; content negotiation and Jackson (records as
DTOs, `java.time` serialization, `BigDecimal` as string vs number); **DTOs vs
entities** (never expose JPA entities); **Jakarta Bean Validation**
(`@Valid`, `@NotNull`, `@Size`, `@Positive`, custom constraints, validation
groups, method validation with `@Validated`); **error handling**:
`@ExceptionHandler`, `@RestControllerAdvice`, **`ProblemDetail`** (RFC 9457,
`spring.mvc.problemdetails.enabled`), mapping domain exceptions to 404/409/422;
filters vs `HandlerInterceptor`; CORS basics (concept from Track 2 B19);
API documentation with **springdoc-openapi** (Swagger UI, `@Operation`,
`@Schema`); HTTP semantics recap from Track 2 B1 (idempotent methods,
pagination, versioning).

*Python comparison:* FastAPI gives you validation + OpenAPI from type hints;
in Spring you combine Bean Validation annotations + springdoc to get the same.

### Lessons
- [ ] **J7.2.L1 Spring MVC.** Spring Framework Reference → Web on Servlet Stack → "Spring Web MVC": §"DispatcherServlet", §"Annotated Controllers" (Declaration, Request Mapping, Handler Methods → Method Arguments / Return Values, `@RequestBody`, `ResponseEntity`).
- [ ] **J7.2.L2 REST guide.** spring.io/guides: "Building a RESTful Web Service" and "Building REST services with Spring" (tutorial).
- [ ] **J7.2.L3 Validation.** Spring Framework Reference → Core → "Validation, Data Binding, and Type Conversion" → "Java Bean Validation"; Hibernate Validator Reference → Ch. 2 "Declaring and validating bean constraints" and Ch. 6 "Creating custom constraints"; Spring Boot Reference → "Core Features" → "Validation".
- [ ] **J7.2.L4 Errors.** Spring Framework Reference → "Spring Web MVC" → §"Exceptions" and §"Error Responses" (`ProblemDetail`, `ErrorResponse`); RFC 9457 "Problem Details for HTTP APIs" §3 "The Problem Details JSON Object".
- [ ] **J7.2.L5 OpenAPI.** springdoc.org → "Getting Started" and "Springdoc-openapi Features" (annotations, grouping).
- [ ] **J7.2.L6 Book view.** *Spring in Action*, 6th ed., Ch. 2 "Developing web applications" (validation) and Ch. 7 "Creating REST services".

### Exercises (`java/J7.2-rest/`)
- [ ] **Ex J7.2.1 Customer API (in-memory).** CRUD for `Customer` (id, taxId, fullName, birthDate, phone) using a `ConcurrentHashMap` repository. *Acceptance:* correct status codes (201 + `Location` header on create, 204 on delete, 404 on missing); request/response are Java records, not the domain class.
- [ ] **Ex J7.2.2 Validation.** Add Bean Validation: required fields, `@Past` birth date, phone pattern, plus one **custom** constraint `@ValidTaxId` (e.g. exactly 9 digits). *Acceptance:* invalid requests return 400 `ProblemDetail` listing every invalid field with a message; a `@WebMvcTest` (preview of J7.4) covers three invalid cases.
- [ ] **Ex J7.2.3 Global error handling.** A `@RestControllerAdvice` maps `CustomerNotFoundException` → 404, `DuplicateTaxIdException` → 409, anything unexpected → 500 without leaking a stack trace. *Acceptance:* every error body is RFC 9457-shaped (`type`, `title`, `status`, `detail`, `instance`) plus a custom `code` property.
- [ ] **Ex J7.2.4 Money and dates on the wire.** Add `creditLimit` as `BigDecimal` and `createdAt` as `OffsetDateTime`. *Acceptance:* JSON shows the amount without floating-point artefacts and timestamps in ISO-8601; `notes.md` explains the choice of string vs number for money.
- [ ] **Ex J7.2.5 OpenAPI.** Add springdoc. *Acceptance:* Swagger UI shows all endpoints with example payloads and the 400/404/409 `ProblemDetail` responses documented; export `openapi.json` into the repo.
- [ ] **Ex J7.2.6 Filter vs interceptor.** Add a servlet `Filter` that sets an `X-Request-ID` (generate if missing, put in SLF4J MDC) and a `HandlerInterceptor` that logs handler + duration. *Acceptance:* `notes.md` explains which runs first and what each can see.

### Must be able to do / explain
- [ ] Trace a request through `DispatcherServlet` → handler mapping → controller → message converter.
- [ ] Design request/response DTOs and explain why entities are not exposed.
- [ ] Validate input with standard and custom constraints.
- [ ] Centralise error handling with `@RestControllerAdvice` returning `ProblemDetail`.
- [ ] Publish an OpenAPI contract with springdoc.

**Estimated hours:** ~8 h

### Self-check interview questions
1. What is the role of `DispatcherServlet`?
2. `@Controller` vs `@RestController`?
3. Why should you not return JPA entities from controllers?
4. How does `@Valid` on a `@RequestBody` produce a 400 response?
5. What is `ProblemDetail`, and why use it?
6. `@ExceptionHandler` in a controller vs in a `@RestControllerAdvice` — what is the difference?
7. What is the difference between a servlet `Filter` and a `HandlerInterceptor`?
8. How do you serialize `BigDecimal` money safely in JSON?

---

**Answers**
1. The front controller: receives every request, finds the handler via `HandlerMapping`, invokes it through a `HandlerAdapter`, converts the return value (`HttpMessageConverter`), and delegates errors to exception resolvers.
2. `@RestController` = `@Controller` + `@ResponseBody` on every method: return values are written to the body instead of being treated as view names.
3. It couples your API contract to your schema, risks lazy-loading exceptions / N+1 during serialization, can leak internal fields, and makes mass-assignment bugs easy.
4. The argument resolver validates the object; a failure throws `MethodArgumentNotValidException`, which Spring's default handling (or your advice) turns into 400.
5. A standard (RFC 9457) JSON error format — `type`, `title`, `status`, `detail`, `instance` + extensions. Clients get one predictable shape for every error.
6. Controller-local handlers apply only to that controller; advice applies globally (or to selected packages/annotations).
7. A `Filter` is servlet-level and runs before Spring MVC (sees raw request/response, e.g. for request IDs, security); an interceptor runs inside MVC around a resolved handler and knows which controller method is called.
8. Keep it `BigDecimal` in Java with an explicit scale, and serialize either as a JSON string or as a number with `WRITE_BIGDECIMAL_AS_PLAIN`; never pass through `double`.

---

## Module J7.3 — Spring Data JPA (~7h)

**Topics:** repository abstraction (`Repository`, `CrudRepository`,
`JpaRepository`, `ListCrudRepository`); **derived query methods** and their
limits; `@Query` with JPQL and native SQL; `@Modifying` queries and why they
bypass the persistence context; **projections** (interface, DTO/record,
dynamic); **pagination & sorting** (`Pageable`, `Page` vs `Slice`, the count
query cost, keyset/scroll API `ScrollPosition`); **Specifications** and
`JpaSpecificationExecutor` for dynamic filters; `@EntityGraph` against N+1
(recap of J5.6); auditing (`@CreatedDate`, `@LastModifiedBy`,
`@EnableJpaAuditing`); `@Version` optimistic locking recap (J5.7) and
`@Lock` for pessimistic locking; Open Session in View and why to turn it off
(`spring.jpa.open-in-view=false`).

*Python comparison:* derived queries feel like Django's `filter(name__startswith=...)`
generated from method names; Specifications ≈ composing `Q()` objects.

### Lessons
- [ ] **J7.3.L1 Getting started.** spring.io/guides: "Accessing Data with JPA"; Spring Data JPA Reference → "Core concepts" and "Defining Repository Interfaces".
- [ ] **J7.3.L2 Queries.** Spring Data JPA Reference → "JPA Query Methods" (query creation from method names, `@Query`, native queries, `@Modifying`).
- [ ] **J7.3.L3 Projections.** Spring Data JPA Reference → "Projections" (interface-based, class-based/DTO, dynamic).
- [ ] **J7.3.L4 Paging, sorting, scrolling.** Spring Data JPA Reference → "Paging, Iterating Large Results, Sorting & Limiting" and "Scrolling".
- [ ] **J7.3.L5 Specifications & auditing.** Spring Data JPA Reference → "Specifications" and "Auditing"; Spring Boot Reference → "Data" → "SQL Databases" → "Open EntityManager in View".
- [ ] **J7.3.L6 Performance view.** Vlad Mihalcea: "The Open Session in View Anti-Pattern" and "The best way to use Spring Data JPA Specifications" (or "The Spring Data JPA findAll Anti-Pattern").

### Exercises (`java/J7.3-data-jpa/`) — PostgreSQL via Testcontainers (J4.3), schema by Flyway (J5.4)
- [ ] **Ex J7.3.1 Repository basics.** Entities `Customer` and `Loan` (many loans per customer). *Acceptance:* `JpaRepository` CRUD works; five derived queries (`findByStatus`, `findByCustomerTaxId`, `countByStatus`, `existsByTaxId`, `findTop5ByOrderByPrincipalDesc`) each covered by a test; `notes.md` shows the SQL each one generated.
- [ ] **Ex J7.3.2 Projections.** An endpoint needs only `loanId, customerName, principal`. *Acceptance:* implement it once with an interface projection and once with a record DTO projection; the logged SQL selects only the needed columns.
- [ ] **Ex J7.3.3 Pagination.** `GET /loans?page=&size=&sort=` returning a page DTO (not Spring's `Page` JSON directly). *Acceptance:* sort whitelist (reject unknown sort fields with 400); compare `Page` vs `Slice` SQL (extra `count(*)`) in `notes.md`; add a keyset variant with the scroll API.
- [ ] **Ex J7.3.4 Dynamic search.** Filters `status`, `minPrincipal`, `maxPrincipal`, `customerName` (contains, case-insensitive), all optional. *Acceptance:* built with Specifications composed with `and`; no string concatenation; a parameterized test covers 6 filter combinations.
- [ ] **Ex J7.3.5 N+1 hunt.** List customers with their loans. *Acceptance:* first show the N+1 in the SQL log with a test that counts statements (e.g. Hibernate `Statistics` or datasource-proxy), then fix it with `@EntityGraph` or a fetch-join query and prove the count dropped to 1–2.
- [ ] **Ex J7.3.6 Auditing + OSIV.** Enable auditing for `createdAt/updatedAt`; turn `open-in-view` off. *Acceptance:* a controller that touches a lazy collection now fails with `LazyInitializationException` in a test; fix it properly (DTO projection or fetch in the service), not by turning OSIV back on.

### Must be able to do / explain
- [ ] Choose between derived query, `@Query` JPQL, native query and Specification.
- [ ] Return projections instead of entities for read endpoints.
- [ ] Paginate efficiently and explain the cost of `Page` vs `Slice` vs keyset.
- [ ] Detect and fix N+1 with Spring Data tools.
- [ ] Explain Open Session in View and why it is disabled in serious apps.

**Estimated hours:** ~7 h

### Self-check interview questions
1. How does Spring Data create an implementation for an interface you never implemented?
2. When do derived query methods become a bad idea?
3. What does `@Modifying` do, and what is the persistence-context pitfall?
4. `Page` vs `Slice` — what is the difference in SQL?
5. What is a projection and why use one?
6. What is Open Session in View and why is it considered an anti-pattern?
7. How do you solve N+1 in Spring Data JPA?
8. How do Specifications help with dynamic search?

---

**Answers**
1. At startup Spring creates a proxy for each repository interface; `SimpleJpaRepository` implements CRUD, and query methods are parsed from names or annotations into JPQL/SQL.
2. When the name gets long (more than ~2–3 conditions), needs joins/aggregates, or must be tuned — use `@Query` or a Specification instead.
3. It marks an update/delete `@Query` as a modifying statement. It bypasses the persistence context, so already-loaded entities are stale; use `clearAutomatically`/`flushAutomatically` or reload.
4. `Page` runs an extra `count(*)` query to know the total; `Slice` fetches `size + 1` rows only to know if a next page exists.
5. A read model with only the needed fields (interface or DTO). Less data, fewer joins, no accidental lazy loading, no entity leaking.
6. It keeps the `EntityManager` open for the whole web request so lazy loading works in views/serialisation. It hides N+1 problems, holds DB connections longer, and moves data access out of the service layer.
7. Fetch joins in `@Query`, `@EntityGraph`, DTO projections, or batch fetching (`hibernate.default_batch_fetch_size`).
8. Each filter is a small composable predicate; you combine only the ones the request actually uses, type-safely, without building query strings.

---

## Module J7.4 — Testing Spring Boot Applications (~5h)

**Topics:** test pyramid for Spring apps; `@SpringBootTest` (full context,
`webEnvironment` modes) and its cost; **test slices**: `@WebMvcTest` (controller
+ MVC only, `@MockitoBean` for collaborators), `@DataJpaTest` (JPA only,
transactional by default, `replace = NONE` to use a real DB), `@JsonTest`;
**MockMvc** and `MockMvcTester`/AssertJ integration; `TestRestTemplate` /
`RestClient` against a random port; **Testcontainers with `@ServiceConnection`**
(no manual datasource properties), reusable containers, `@DynamicPropertySource`
for non-supported services; **WireMock** for stubbing downstream HTTP services
(stubs, delays, faults); context caching and why many different
`@MockitoBean` combinations make suites slow; test data builders; `@Sql`.

*Python comparison:* `@WebMvcTest` ≈ FastAPI `TestClient` with overridden
dependencies; Testcontainers ≈ the real-Postgres pytest fixtures from Track 2 B8.

### Lessons
- [ ] **J7.4.L1 Boot testing overview.** Spring Boot Reference → "Testing" → "Testing Spring Boot Applications" (Detecting Test Configuration, Using Application Arguments, Testing With a Mock Environment / Running Server).
- [ ] **J7.4.L2 Test slices.** Same chapter → "Auto-configured Spring MVC Tests", "Auto-configured Data JPA Tests", "Auto-configured JSON Tests"; Spring Framework Reference → Testing → "MockMvc".
- [ ] **J7.4.L3 Testcontainers.** Spring Boot Reference → "Testing" → "Testcontainers" (Service Connections, Dynamic Properties); testcontainers.com guide: "Testing Spring Boot REST API using Testcontainers".
- [ ] **J7.4.L4 Mocking beans.** Spring Framework Reference → Testing → "Bean Overriding in Tests" (`@MockitoBean`, `@MockitoSpyBean`); Baeldung: "Guide to Spring Boot Testing" (sections on slices).
- [ ] **J7.4.L5 Context caching.** Spring Framework Reference → Testing → "Context Caching".
- [ ] **J7.4.L6 WireMock.** wiremock.org docs → "Stubbing", "Simulating Faults" and "Spring Boot integration"; Baeldung: "Introduction to WireMock".

### Exercises (`java/J7.4-boot-testing/`) — use the J7.2/J7.3 code
- [ ] **Ex J7.4.1 Controller slice.** `@WebMvcTest` for the customer controller with the service mocked. *Acceptance:* covers 201/400/404/409 paths and asserts `ProblemDetail` fields with JSON path; runs without a DB.
- [ ] **Ex J7.4.2 Repository slice.** `@DataJpaTest` against **real PostgreSQL** via Testcontainers + `@ServiceConnection` with Flyway migrations applied. *Acceptance:* the specification search from Ex J7.3.4 is tested against real SQL; no H2 anywhere.
- [ ] **Ex J7.4.3 Full-stack test.** One `@SpringBootTest(webEnvironment = RANDOM_PORT)` test that creates a customer and a loan over HTTP and reads them back. *Acceptance:* uses the same container definition as Ex 2 (shared `@TestConfiguration` / `@ImportTestcontainers`).
- [ ] **Ex J7.4.4 Suite speed.** Measure total test time; then make the context cacheable (same config across classes) and container reuse where sensible. *Acceptance:* `notes.md` shows before/after timings and how many contexts were created (enable context cache logging).

### Must be able to do / explain
- [ ] Pick the right slice for a test and explain what it loads.
- [ ] Write MockMvc tests that assert status, headers and JSON bodies.
- [ ] Run integration tests against real PostgreSQL with `@ServiceConnection`.
- [ ] Explain context caching and what breaks it.

**Estimated hours:** ~5 h

### Self-check interview questions
1. `@SpringBootTest` vs `@WebMvcTest` vs `@DataJpaTest` — what does each load?
2. Why prefer Testcontainers over H2 for repository tests?
3. What does `@ServiceConnection` do?
4. Why can a large Spring test suite become slow, and how do you fix it?
5. What is the difference between `@MockitoBean` and a plain Mockito `@Mock`?
6. Is a `@DataJpaTest` transactional? What does that hide?

---

**Answers**
1. `@SpringBootTest`: the whole application context (optionally a real server). `@WebMvcTest`: MVC infrastructure + the chosen controllers, advice, filters, converters — no services/repositories. `@DataJpaTest`: JPA, repositories, a datasource, Flyway/Liquibase — no web layer.
2. H2 behaves differently (SQL dialect, locking, types, functions); tests pass on H2 and fail on Postgres/Oracle. Testcontainers tests the real engine and your real migrations.
3. It lets Boot derive connection details (URL, user, password) from a Testcontainers container bean automatically — no `@DynamicPropertySource` boilerplate.
4. Each distinct configuration (different mocks, profiles, properties) creates a new context and new containers. Standardise test configuration, share containers, prefer slices and plain unit tests.
5. `@MockitoBean` replaces (or adds) a bean **inside the Spring context**, so Spring-injected collaborators get the mock; `@Mock` is a standalone Mockito mock for tests without Spring.
6. Yes, each test rolls back at the end. It can hide problems that appear only on commit (deferred constraints, flush-time errors, triggers, lazy loading outside a transaction); add some tests that commit for real.

---

## Project JP3 — LoanProduct Catalog API · Junior (~35h)

**Goal:** build your first real Spring Boot service end to end: a catalog of
loan products that other systems (and later projects JM2/JMP3) read. Small
domain, done properly — layered design, validation, ProblemDetail errors,
pagination, OpenAPI, Flyway migrations and Testcontainers tests on PostgreSQL.
Domain ideas come from the setup tables of the CreditLine design (loan
products, date-effective rates, fee definitions).

### Features
- [ ] **Products:** create, update, deactivate (no hard delete), get, list. Fields: `code` (unique), `name`, `interestMethod` (`FLAT` | `DECLINING` | `ANNUITY`), `minAmount`, `maxAmount`, `minTermMonths`, `maxTermMonths`, `graceDays`, `penaltyRate`, `validFrom`, `validTo`, `status`.
- [ ] **Rate history (effective-dated):** add a new rate with `effectiveFrom`; the previous rate's `effectiveTo` is closed automatically; periods never overlap and never leave gaps. `GET /products/{code}/rate?asOf=2026-03-01` returns the rate valid on that date.
- [ ] **Fee definitions:** per product — `feeType` (`ORIGINATION` | `SERVICE` | `LATE`), `calcMethod` (`FIXED` | `PERCENT`), `value`, `upfront` flag.
- [ ] **Search:** filter by status, interest method, amount range (a product matches if the requested amount fits `[minAmount, maxAmount]`), code prefix; paginated and sortable (whitelisted sort fields).
- [ ] **Quote preview (no persistence):** `POST /products/{code}/quote` with `amount`, `termMonths` → validates against product limits and returns the applicable rate and the list of fees in money (`BigDecimal`, scale 2, `HALF_EVEN`). No amortization schedule — that is PL/SQL's job in JM2.
- [ ] **Errors:** validation → 400, unknown code → 404, duplicate code / overlapping rate period → 409, amount/term outside limits → 422; all as `ProblemDetail` with a stable `code` property.
- [ ] **API docs:** OpenAPI via springdoc, with examples.
- [ ] **Optimistic locking** on products (`@Version`) → 409 on concurrent update.

### Tech stack
| Tool / library | Taught in |
|---|---|
| Java 25, records, `java.time`, `BigDecimal` | J1.x, J2.3 |
| Maven (or Gradle), multi-module not needed | J4.1 |
| Spring Boot 3.x, starters, `@ConfigurationProperties` | J7.1 |
| Spring MVC, Bean Validation, `ProblemDetail` | J7.2 |
| springdoc-openapi | J7.2 |
| Spring Data JPA, projections, pagination, Specifications | J7.3 |
| Hibernate, `@Version` | J5.6, J5.7 |
| PostgreSQL | Track 1C Part 1–2 (SQL), J5.1–J5.2 (from Java) |
| Flyway | J5.4 |
| JUnit 5, AssertJ, Mockito | J4.2 |
| Testcontainers + `@ServiceConnection`, MockMvc, test slices | J4.3, J7.4 |
| SLF4J + Logback | J4.4 |
| Docker (to run Postgres locally) | Track 2 B3 (concept) — only `docker run`/Compose for the DB |

### Required knowledge
- Track 4: J1.1–J1.13, J2.1–J2.6, J4.1–J4.4, J5.1–J5.8, J6.1–J6.4, J7.1–J7.4.
- Track 1C: 1.6 (constraints), 2.5 (indexes), 2.7 (transactions) — for the rate-period rules.
- Track 2 B1 (REST design) as a concept reference.

### Milestones
- [ ] **M1 — Skeleton (~5 h):** Initializr project, layered packages (`api`, `service`, `domain`, `persistence`), Flyway `V1__products.sql`, `docker compose` for Postgres, health of the app verified by one `@SpringBootTest`. Tag `v0.1-skeleton`.
- [ ] **M2 — Products CRUD (~8 h):** entities, repositories, DTO records, validation, `@RestControllerAdvice` + ProblemDetail, `@WebMvcTest` + `@DataJpaTest` (Testcontainers). Tag `v0.2-products`.
- [ ] **M3 — Rates & fees (~9 h):** rate history with no-overlap/no-gap rules enforced in the service **and** by a DB constraint (your choice: exclusion constraint with `btree_gist`, or a unique + check design — justify it in `docs/decisions.md`); `asOf` lookup; fee definitions. Tag `v0.3-rates-fees`.
- [ ] **M4 — Search & quote (~7 h):** Specifications-based search with pagination and sort whitelist; quote preview with correct money rounding; optimistic locking test (two concurrent updates → one 409). Tag `v0.4-search-quote`.
- [ ] **M5 — Docs & polish (~6 h):** springdoc with examples and documented error responses; README (how to run, API overview, design decisions); test coverage of every error code. Tag `v1.0-jp3`.

### Definition of done
- [ ] `./mvnw verify` runs all tests (unit + slices + one full-stack) against a real PostgreSQL container; no H2.
- [ ] Every endpoint returns DTOs, never entities; `open-in-view` is disabled.
- [ ] Every error path has a test asserting status + `ProblemDetail.code`.
- [ ] Rate periods cannot overlap even if two requests race (DB constraint proves it).
- [ ] Money is `BigDecimal` end to end with an explicit rounding mode; no `double` anywhere.
- [ ] OpenAPI JSON committed and matching the running API.
- [ ] README explains how to run in one command and lists three design decisions.

**Estimated hours:** ~35 h

### Interview questions about this project
1. How did you make sure two rate periods for the same product can never overlap, even under concurrent requests?
2. Why does your API return records/DTOs instead of JPA entities?
3. How did you design your error contract, and why `ProblemDetail`?
4. What happens when two users update the same product at the same time?
5. Why did you test against PostgreSQL in a container instead of H2?

---

**Answers**
1. Application-level validation gives a nice 409 message, but the real guarantee is a database constraint (an exclusion constraint on a date range per product, or an equivalent design); under a race the second insert fails at the DB and is mapped to 409.
2. The API contract stays stable when the schema changes, no lazy-loading or N+1 during serialization, no leaking internal fields, and input DTOs prevent mass assignment.
3. One predictable, standard (RFC 9457) shape for every error, with a stable machine-readable `code` extension so clients do not parse messages; mapping lives in one `@RestControllerAdvice`.
4. `@Version` optimistic locking: the second commit's `UPDATE … WHERE version = ?` touches 0 rows, Hibernate throws `OptimisticLockException`, and the advice returns 409 so the client can reload and retry.
5. Constraints like exclusion constraints, SQL dialect, locking and types behave differently in H2; testing on the real engine with the real Flyway migrations catches bugs H2 would hide.

---

## Module J7.5 — Data Access the Spring Way: Transactions, JDBC & Stored Procedures (~6h)

**Topics:** `PlatformTransactionManager` (`JpaTransactionManager`,
`DataSourceTransactionManager`); `@Transactional` attributes in depth:
**propagation** (`REQUIRED`, `REQUIRES_NEW`, `NESTED`, `MANDATORY`,
`SUPPORTS`, `NOT_SUPPORTED`, `NEVER`), **isolation** (maps to Track 1C 2.7),
**rollback rules**, `timeout`, `readOnly`; `TransactionTemplate` for
programmatic transactions; long transactions and connection-pool exhaustion;
**`JdbcTemplate`**, `NamedParameterJdbcTemplate`, the fluent **`JdbcClient`**
(Spring 6.1+), `RowMapper`, batch updates; mixing JPA and JDBC in one
transaction; **calling stored procedures**: `SimpleJdbcCall` (IN/OUT params,
`OracleTypes.CURSOR` REF CURSOR with a `RowMapper`, catalog = package name),
`StoredProcedure` class, Spring Data JPA **`@Procedure`** and JPA
`StoredProcedureQuery` / `@NamedStoredProcedureQuery` — and when to use each;
**exception translation**: `DataAccessException` hierarchy,
`SQLErrorCodeSQLExceptionTranslator`, custom `SQLExceptionTranslator` mapping
Oracle `ORA-20000..20999` (`RAISE_APPLICATION_ERROR`) codes to domain
exceptions; the rule "packages never `COMMIT` — the Spring service owns the
transaction" (why a `COMMIT` inside a package silently breaks
`@Transactional`).

### Lessons
- [ ] **J7.5.L1 Transaction management.** Spring Framework Reference → Data Access → "Transaction Management": §"Advantages of the Spring Framework's Transaction Support Model", §"Understanding the Spring Framework Transaction Abstraction", §"Transaction Propagation", §"Programmatic Transaction Management".
- [ ] **J7.5.L2 JDBC support.** Spring Framework Reference → Data Access → "Data Access with JDBC": §"Using the JDBC Core Classes to Control Basic JDBC Processing and Error Handling" (`JdbcTemplate`, `NamedParameterJdbcTemplate`, `JdbcClient`, `SQLExceptionTranslator`), §"JDBC Batch Operations".
- [ ] **J7.5.L3 Stored procedures.** Same chapter → §"Simplifying JDBC Operations with the `SimpleJdbc` Classes" (`SimpleJdbcCall`, "Declaring Parameters", "Returning ResultSet or REF Cursor from a SimpleJdbcCall") and §"Modeling JDBC Operations as Java Objects" → `StoredProcedure`.
- [ ] **J7.5.L4 JPA procedures.** Spring Data JPA Reference → "JPA Query Methods" → "Stored Procedures" (`@Procedure`); Jakarta Persistence spec / Hibernate User Guide → "Stored procedures" (`StoredProcedureQuery`, REF_CURSOR parameter mode).
- [ ] **J7.5.L5 Practitioner view.** Vlad Mihalcea: "A beginner's guide to transaction isolation levels…", "Spring Transaction and Connection Management", "How to call Oracle stored procedures and functions with JPA and Hibernate"; Baeldung: "Transaction Propagation and Isolation in Spring @Transactional", "A Guide to the JdbcClient", "Calling Stored Procedures from Spring Data JPA Repositories".

### Exercises (`java/J7.5-data-access/`)
- [ ] **Ex J7.5.1 Propagation lab.** A service with an outer `REQUIRED` method calling an inner method on **another bean** with `REQUIRED`, then `REQUIRES_NEW`, then `NESTED`; the outer method throws after the inner call. *Acceptance:* a parameterized test records which rows survive for each propagation; the result table + explanation goes in `notes.md`. Include the `UnexpectedRollbackException` case (inner `REQUIRED` marks rollback-only, outer catches and continues).
- [ ] **Ex J7.5.2 Audit that survives rollback.** Implement an `AuditWriter` whose writes survive a business rollback. *Acceptance:* test proves the audit row persists when the business transaction fails; `notes.md` compares `REQUIRES_NEW` in Spring with `PRAGMA AUTONOMOUS_TRANSACTION` in PL/SQL (1C 3.9) and names one danger of each (pool exhaustion / deadlocks with the outer transaction).
- [ ] **Ex J7.5.3 JdbcClient report.** Rewrite one read endpoint from J7.3 using `JdbcClient` with a record `RowMapper`, and a batch insert of 10 000 rows with `JdbcTemplate.batchUpdate`. *Acceptance:* timing comparison with JPA `saveAll` (with and without `hibernate.jdbc.batch_size`) recorded in `notes.md`.
- [ ] **Ex J7.5.4 Calling an Oracle package (Testcontainers `gvenzl/oracle-free`).** Write a tiny package `pkg_customer` with `procedure create_customer(p_tax_id in varchar2, p_name in varchar2, p_id out number)` and `procedure list_by_prefix(p_prefix in varchar2, p_rc out sys_refcursor)`; both raise `RAISE_APPLICATION_ERROR(-20001, 'DUPLICATE_TAX_ID')` / `(-20002, 'INVALID_PREFIX')` on bad input and **never commit**. Call them via `SimpleJdbcCall` (one IN/OUT, one REF CURSOR mapped to records). *Acceptance:* integration tests on the Oracle container pass; the package is deployed by a Flyway **repeatable** migration (`R__pkg_customer.sql`).
- [ ] **Ex J7.5.5 Error-code translation.** A custom `SQLExceptionTranslator` (or a translator in the gateway) maps `-20001` → `DuplicateTaxIdException`, `-20002` → `InvalidRequestException`, everything else → Spring's default. *Acceptance:* a `@RestControllerAdvice` turns them into 409/422 `ProblemDetail`s; a table "error code → exception → HTTP status" lives in `docs/error-contract.md` and a test iterates over it.
- [ ] **Ex J7.5.6 Same call, three ways.** Call `pkg_customer.create_customer` also via Spring Data `@Procedure` and JPA `StoredProcedureQuery`. *Acceptance:* `notes.md` recommends one approach for a JDBC-first codebase and one for a JPA-first codebase, with reasons.

### Must be able to do / explain
- [ ] Explain every propagation type and give a real use case for `REQUIRES_NEW`.
- [ ] Explain why a long transaction hurts the connection pool.
- [ ] Use `JdbcClient`/`JdbcTemplate` with row mappers and batch updates.
- [ ] Call a PL/SQL package procedure with IN/OUT params and a REF CURSOR from Spring.
- [ ] Map Oracle application error codes to domain exceptions and HTTP statuses.
- [ ] Explain why the database package must not `COMMIT` when Spring owns the transaction.

**Estimated hours:** ~6 h

### Self-check interview questions
1. Explain `REQUIRED` vs `REQUIRES_NEW` vs `NESTED`.
2. When does `UnexpectedRollbackException` happen?
3. What is the difference between `JdbcTemplate` and `JdbcClient`?
4. How do you read a REF CURSOR returned by a PL/SQL procedure in Spring?
5. How does Spring translate `SQLException`s, and how do you plug in your own mapping?
6. A PL/SQL procedure does `COMMIT` at the end, and it is called from a `@Transactional` Spring method that later throws. What happens?
7. Why can `REQUIRES_NEW` deadlock or exhaust the connection pool?
8. When would you choose JDBC over JPA in a Spring application?

---

**Answers**
1. `REQUIRED` joins the current transaction or starts one. `REQUIRES_NEW` suspends the current transaction and starts an independent one (separate connection, commits on its own). `NESTED` runs inside the same transaction using a savepoint, so it can roll back partially (JDBC `DataSourceTransactionManager` only).
2. When an inner participant marked the shared transaction rollback-only (an exception passed through it) but the outer code caught the exception and tried to commit; Spring rolls back and throws `UnexpectedRollbackException` to tell you the commit did not happen.
3. Same engine; `JdbcClient` (6.1+) is a fluent, unified API for positional and named parameters with concise mapping (`.query(Record.class)`), replacing most `JdbcTemplate`/`NamedParameterJdbcTemplate` boilerplate.
4. `SimpleJdbcCall` with `SqlOutParameter("p_rc", OracleTypes.CURSOR, rowMapper)` (or `returningResultSet`); the result map contains a `List<T>`. Plain JDBC: `registerOutParameter(i, OracleTypes.CURSOR)` then `getObject(i, ResultSet.class)`.
5. `JdbcTemplate` catches `SQLException` and asks its `SQLExceptionTranslator` (error codes by vendor, then SQLState) to produce a `DataAccessException` subclass. Plug in a custom translator via `setExceptionTranslator` (or `SQLErrorCodes` custom translations) for vendor/app-specific codes like `-20007`.
6. The package's `COMMIT` commits everything done so far on that connection — including earlier Spring work — so the later rollback cannot undo it. Data ends up half-written; the transaction boundary must belong to one owner.
7. It needs a second connection while the first one is held; under load all connections can be held by outer transactions waiting for inner ones (pool deadlock), and inner/outer can lock the same rows.
8. Set-based reports, bulk operations, calling stored procedures, complex SQL (window functions, CTEs), or when the database (PL/SQL) owns the rules and Java is just the boundary.

---

## Module J7.6 — Spring Security (~10h)

**Topics:** servlet filter chain and `DelegatingFilterProxy` →
`FilterChainProxy` → `SecurityFilterChain`s; `SecurityContextHolder` and
`Authentication`; `AuthenticationManager`/`AuthenticationProvider`,
`UserDetailsService`; **password storage** with `DelegatingPasswordEncoder`
(bcrypt/argon2 — concept from Track 2 B6); configuring `HttpSecurity` with the
lambda DSL (`authorizeHttpRequests`, `requestMatchers`); **stateless JWT APIs**:
issuing tokens with `JwtEncoder` (Nimbus, RSA key pair) on a login endpoint,
validating them with the **OAuth2 Resource Server** (`JwtDecoder`, issuer/audience
validation, clock skew, mapping claims to authorities with
`JwtAuthenticationConverter`); concept of external IdPs (Keycloak, Track 2 B18)
— switching the resource server to an external issuer is only configuration;
**method security** (`@EnableMethodSecurity`, `@PreAuthorize` with SpEL,
object-level checks via a bean `@ownership.canEdit(#id, authentication)`);
CORS (`CorsConfigurationSource`) vs CSRF (disable only for stateless token
APIs — know why); security headers; exception handling (401 vs 403,
`AuthenticationEntryPoint`, `AccessDeniedHandler` returning `ProblemDetail`);
**testing security** (`spring-security-test`, `@WithMockUser`,
`SecurityMockMvcRequestPostProcessors.jwt()`).

*Python comparison:* FastAPI security is a dependency per route; Spring
Security is a filter chain in front of everything plus annotations on methods.

### Lessons
- [ ] **J7.6.L1 Architecture.** Spring Security Reference → Servlet Applications → "Architecture" (DelegatingFilterProxy, FilterChainProxy, SecurityFilterChain, Security Filters, Handling Security Exceptions).
- [ ] **J7.6.L2 Authentication.** Spring Security Reference → "Authentication" → "Authentication Architecture" and "Username/Password" → "Password Storage"; spring.io/guides: "Securing a Web Application".
- [ ] **J7.6.L3 Authorization.** Spring Security Reference → "Authorization" → "Authorize HttpServletRequests" and "Method Security" (`@PreAuthorize`, SpEL, custom beans in expressions).
- [ ] **J7.6.L4 JWT resource server.** Spring Security Reference → "OAuth2" → "OAuth 2.0 Resource Server" → "JWT" (minimal configuration, specifying the authorization server / public key, `JwtAuthenticationConverter`, validators, clock skew); Spring Security Reference → "OAuth2" → "Core" / JOSE: `JwtEncoder` (`NimbusJwtEncoder`).
- [ ] **J7.6.L5 CORS, CSRF, headers.** Spring Security Reference → "Exploits" → "Cross Site Request Forgery (CSRF)" ("When to use CSRF protection"), "Security HTTP Response Headers"; → "Integrations" → "CORS".
- [ ] **J7.6.L6 Testing.** Spring Security Reference → "Testing" → "Method Security" (`@WithMockUser`) and "Testing with MockMvc" → "Testing OAuth 2.0" (`jwt()` post-processor).
- [ ] **J7.6.L7 Book view.** *Spring in Action*, 6th ed., Ch. 5 "Securing Spring" and Ch. 8 "Securing REST" (resource server part); Baeldung: "Spring Security – Roles and Privileges" / "Introduction to Spring Method Security".

### Exercises (`java/J7.6-security/`) — use the J7.2 customer API
- [ ] **Ex J7.6.1 Walk the chain.** Enable `logging.level.org.springframework.security=TRACE` and make one request. *Acceptance:* `notes.md` lists the filters in order for your chain and names the one that produced the 401.
- [ ] **Ex J7.6.2 Users & passwords.** A `users` table (Flyway), `UserDetailsService` over it, `DelegatingPasswordEncoder` with bcrypt. *Acceptance:* stored hashes start with `{bcrypt}`; a test proves re-hashing on upgrade works (`UserDetailsPasswordService`) or explain in `notes.md` how it would.
- [ ] **Ex J7.6.3 Issue and validate JWTs.** `POST /auth/token` checks credentials and returns an RS256 JWT (`sub`, `roles`, `iat`, `exp` 15 min, `iss`, `aud`) signed with a key pair loaded from config (not committed private key). The rest of the API is an OAuth2 **resource server** validating those tokens. *Acceptance:* expired, wrong-audience, wrong-signature and missing tokens each get 401 with `ProblemDetail` and a `WWW-Authenticate` header; tests cover all four.
- [ ] **Ex J7.6.4 Roles and object-level rules.** Roles `ADMIN`, `OFFICER`, `VIEWER`; officers may edit only customers of their own branch (`branchId` claim vs customer's branch) via `@PreAuthorize("@customerAccess.canEdit(#id, authentication)")`. *Acceptance:* tests with `jwt()` post-processor cover allowed, wrong-role (403) and wrong-branch (403) cases.
- [ ] **Ex J7.6.5 CORS & CSRF decision.** Configure CORS for one allowed origin; disable CSRF only for the stateless API chain. *Acceptance:* `notes.md` explains in 5 lines why CSRF is not needed for a bearer-token API and when it would be needed again (cookie-based session).
- [ ] **Ex J7.6.6 Two chains.** Add a second `SecurityFilterChain` for `/actuator/**`-style internal endpoints (or `/internal/**`) with HTTP Basic and a separate role, ordered before the API chain. *Acceptance:* tests prove each path uses the right chain.

### Must be able to do / explain
- [ ] Draw the filter chain and explain where authentication and authorization happen.
- [ ] Store passwords correctly and explain `DelegatingPasswordEncoder`.
- [ ] Build a stateless JWT resource server and validate issuer, audience and expiry.
- [ ] Map JWT claims to authorities.
- [ ] Enforce object-level authorization with method security.
- [ ] Explain 401 vs 403, CORS vs CSRF, and when CSRF can be disabled.
- [ ] Test secured endpoints without a real IdP.

**Estimated hours:** ~10 h

### Self-check interview questions
1. How does a request pass through Spring Security?
2. What is `SecurityContextHolder`, and how does it work with virtual threads or `@Async`?
3. What does the OAuth2 Resource Server do with a JWT?
4. Why is CSRF protection usually disabled for stateless JWT APIs, and when is that wrong?
5. `hasRole('ADMIN')` vs `hasAuthority('ROLE_ADMIN')`?
6. How do you implement "a user can only edit their own resources"?
7. 401 vs 403 — who returns which in Spring Security?
8. How would you rotate the JWT signing key without logging everyone out?

---

**Answers**
1. The servlet container calls `DelegatingFilterProxy` → `FilterChainProxy`, which picks the first matching `SecurityFilterChain`; its filters authenticate (e.g. `BearerTokenAuthenticationFilter`), store the `Authentication` in the `SecurityContext`, then `AuthorizationFilter` checks access before the request reaches `DispatcherServlet`.
2. A holder for the current `SecurityContext`, by default in a `ThreadLocal`. It is not automatically copied to other threads — use `DelegatingSecurityContextExecutor`/task decorators for `@Async`; with virtual threads the per-request thread still works, but work handed to other threads needs explicit propagation.
3. Extracts it from the `Authorization: Bearer` header, verifies the signature with the configured key/JWKs, validates `exp`/`nbf`/`iss`/`aud`, converts claims into an `Authentication` with authorities, and stores it in the security context.
4. CSRF exploits the browser sending cookies automatically; a bearer token in a header is not sent automatically, so the attack does not apply. It becomes wrong the moment you put the token (or a session) in a cookie.
5. Equivalent: `hasRole('ADMIN')` adds the `ROLE_` prefix and checks the authority `ROLE_ADMIN`.
6. Method security with an expression calling a bean that checks ownership (`@PreAuthorize("@access.canEdit(#id, authentication)")`), or check inside the service; plus queries scoped by owner so lists cannot leak others' data.
7. 401 (unauthenticated) comes from the `AuthenticationEntryPoint` when no/invalid credentials; 403 (authenticated but not allowed) comes from the `AccessDeniedHandler`.
8. Publish the new public key alongside the old one (JWKS with `kid`), start signing with the new key, keep accepting the old one until all old tokens expire, then remove it.

---

## Module J7.7 — Spring Cache with Redis (~3h)

**Topics:** cache abstraction (`@EnableCaching`, `@Cacheable`, `@CachePut`,
`@CacheEvict`, `@Caching`, `CacheManager`); key generation and **explicit key
design** (include every input that changes the result — e.g. the `asOf` date
for date-effective data); `RedisCacheManager` with per-cache TTLs and JSON
serialization (not JDK serialization); `sync = true` as a local stampede guard;
cache-aside semantics and invalidation (concepts from Track 2 B12); what never
to cache (balances, anything that must be strongly consistent); proxy pitfalls
again (self-invocation, J6.3); Spring Data Redis `RedisTemplate`/
`StringRedisTemplate` for non-cache uses (idempotency keys, simple counters);
**atomic Lua scripts** via `DefaultRedisScript` + `RedisTemplate.execute`;
`ReactiveRedisTemplate` (used later with WebFlux).

### Lessons
- [ ] **J7.7.L1 Cache abstraction.** Spring Framework Reference → Integration → "Cache Abstraction" (Declarative Annotation-based Caching: `@Cacheable`, `@CachePut`, `@CacheEvict`, default key generation, synchronized caching).
- [ ] **J7.7.L2 Boot + Redis.** Spring Boot Reference → "IO" → "Caching" → "Supported Cache Providers" → "Redis"; spring.io/guides: "Caching Data with Spring"; Spring Data Redis Reference → "Redis Cache" and "Working with Objects through RedisTemplate".
- [ ] **J7.7.L3 Baeldung.** "Spring Boot Cache with Redis" and "A Guide To Caching in Spring".
- [ ] **J7.7.L4 Scripting & reactive.** Spring Data Redis Reference → "Scripting" and "Reactive Redis Support"; redis.io docs → "Scripting with Lua" (recap of Track 2 B12).

### Exercises (`java/J7.7-cache/`) — Redis via Testcontainers (`@ServiceConnection` supports Redis)
- [ ] **Ex J7.7.1 Cache a slow read.** Cache `GET /products/{code}` from JP3-style code with `@Cacheable`, JSON serialization, TTL 10 min. *Acceptance:* a test shows the repository is called once for two identical requests; Redis contains a readable JSON value (inspect with `redis-cli`).
- [ ] **Ex J7.7.2 Keys that include time.** Cache `rate(code, asOf)`. *Acceptance:* a test proves two different `asOf` dates never return each other's value; `notes.md` explains the bug you would get with a key of `code` only.
- [ ] **Ex J7.7.3 Invalidation.** Updating a product evicts exactly the affected entries (`@CacheEvict` / `@CachePut`). *Acceptance:* test: update → next read returns fresh data; list which write paths must evict (write it down before coding — the Track 2 B12 "invalidation audit").
- [ ] **Ex J7.7.4 Stampede.** Simulate 50 concurrent requests on a cold key with a 200 ms slow loader. *Acceptance:* measure loader calls with and without `sync = true`; `notes.md` explains why `sync` only protects one JVM instance.

### Must be able to do / explain
- [ ] Configure `RedisCacheManager` with TTLs and JSON serialization.
- [ ] Design cache keys that include every result-changing input.
- [ ] Keep caches consistent with explicit eviction on every write path.
- [ ] Explain what should never be cached and why.

**Estimated hours:** ~3 h

### Self-check interview questions
1. How does `@Cacheable` work, and what pitfall does it share with `@Transactional`?
2. `@CachePut` vs `@CacheEvict`?
3. Why configure JSON serialization instead of JDK serialization for Redis caches?
4. What does `sync = true` do, and what does it not do?
5. Give an example of data you must not cache.

---

**Answers**
1. A proxy checks the cache with the computed key before invoking the method and stores the result after. Like `@Transactional`, it does not apply on self-invocation or on non-proxied methods.
2. `@CachePut` always runs the method and writes the result to the cache; `@CacheEvict` removes entries (optionally all, before or after invocation).
3. JSON is readable, language-neutral, and does not break on class changes the way JDK serialization does; JDK serialization also has security issues.
4. Only one thread per JVM computes a missing value for a key while others wait; it does not coordinate between multiple instances (you need a distributed lock or early refresh for that).
5. Account/loan balances, anything used to authorize money movement, or data that must reflect the latest committed state; also per-user sensitive data under a shared key.

---

## Project JM1 — TeamBoard · Middle (~50h)

**Goal:** a secure, production-shaped issue-tracker API. The domain is simple on
purpose; the difficulty is in doing security, concurrency, migrations,
caching and testing the way a middle Spring engineer is expected to.

### Features
- [ ] **Accounts & auth:** registration (admin-only in prod profile), login returning an RS256 JWT (15-min access token) plus a refresh token stored hashed in the DB with rotation (reuse of an old refresh token revokes the whole family); logout revokes the refresh family.
- [ ] **Projects:** create/archive; members with a project role (`OWNER`, `MAINTAINER`, `REPORTER`).
- [ ] **Issues:** create, edit, assign, change status through a state machine (`OPEN → IN_PROGRESS → IN_REVIEW → DONE`, `→ CLOSED` from any state by maintainers), labels, priority.
- [ ] **Comments:** add/edit own comment within 15 minutes; maintainers can delete any.
- [ ] **Authorization:** global role `ADMIN`; everything else by **project membership** (object-level rules with method security). A non-member gets 404 (not 403) for a project's issues — explain why.
- [ ] **Concurrency:** optimistic locking on issues (`@Version` + `If-Match`/ETag header on `PATCH`); two concurrent edits → one 409/412.
- [ ] **Search:** issues by project, status, assignee, label, text in title; paginated (keyset for the default "newest first" listing).
- [ ] **Caching:** project board summary (`counts by status`) cached in Redis with explicit eviction on every issue status change.
- [ ] **Audit:** every issue change writes an `issue_events` row (who, what, old → new) in the same transaction; `GET /issues/{id}/history`.
- [ ] **API docs:** springdoc, secured endpoints marked with the bearer scheme.
- [ ] **OPTIONAL:** switch the resource server to an external issuer (Keycloak — concept in Track 2 B18) by configuration only, and document the difference.

### Tech stack
| Tool / library | Taught in |
|---|---|
| Spring Boot, MVC, Bean Validation, ProblemDetail, springdoc | J7.1, J7.2 |
| Spring Data JPA, Specifications, keyset scrolling, auditing | J7.3 |
| Hibernate, `@Version`, fetch strategies | J5.6, J5.7 |
| Spring Security, JWT (`JwtEncoder`/Resource Server), method security | J7.6 |
| Spring Cache + Spring Data Redis | J7.7 |
| Transactions (propagation, rollback rules) | J6.3, J7.5 |
| Spring events (`@TransactionalEventListener` for cache eviction after commit) | J6.4 |
| PostgreSQL | 1C Parts 1–2; J5.1–J5.2 |
| Flyway | J5.4 |
| JUnit 5, AssertJ, Mockito, Testcontainers (Postgres + Redis), MockMvc, `spring-security-test` | J4.2, J4.3, J7.4, J7.6 |
| Checkstyle/SpotBugs, SLF4J/Logback | J4.4 |

### Required knowledge
- Track 4: everything up to and including J7.7.
- Track 1C: 2.7 (isolation), 2.8 (locking) for the concurrency part.
- Track 2 concepts: B6 (hashing, JWT), B7 (race conditions, optimistic locking), B12 (cache invalidation), B18 (refresh-token rotation) — read the concept, implement it the Spring way.

### Milestones
- [ ] **M1 — Skeleton & schema (~6 h):** modules/packages by feature (`auth`, `project`, `issue`, `comment`), Flyway V1–V3, Compose with Postgres + Redis, Checkstyle + SpotBugs in the build. Tag `v0.1-skeleton`.
- [ ] **M2 — Auth (~10 h):** users, password encoding, login → JWT, resource server, refresh rotation with family revocation, logout; security tests for every 401 path. Tag `v0.2-auth`.
- [ ] **M3 — Projects & issues (~12 h):** CRUD, membership, state machine (illegal transition → 422), object-level `@PreAuthorize` rules, 404-for-non-members, audit events in the same transaction. Tag `v0.3-issues`.
- [ ] **M4 — Concurrency & search (~9 h):** `@Version` + ETag/`If-Match`, a race test with two threads proving one update wins; Specifications search; keyset listing. Tag `v0.4-concurrency-search`.
- [ ] **M5 — Cache & comments (~7 h):** board summary cache with after-commit eviction; comments with the 15-minute edit rule (use an injectable `Clock` so tests control time). Tag `v0.5-cache-comments`.
- [ ] **M6 — Hardening & docs (~6 h):** springdoc with security scheme; README with architecture sketch, auth flow diagram, and error contract table; CI-ready `./mvnw verify`. Tag `v1.0-jm1`.

### Definition of done
- [ ] `./mvnw verify` passes with Testcontainers Postgres + Redis; zero H2; Checkstyle/SpotBugs clean.
- [ ] Every endpoint has at least one allowed and one forbidden security test.
- [ ] Refresh-token reuse detection is covered by a test.
- [ ] A concurrency test proves lost updates are impossible on issues.
- [ ] The board cache can never show a status count that disagrees with the DB after a committed change (test).
- [ ] No private key or secret committed; config via environment/profiles.
- [ ] README explains design decisions (why 404 for non-members, why after-commit eviction, why keyset listing).

**Estimated hours:** ~50 h

### Interview questions about this project
1. Walk me through what happens from login to an authorized `PATCH /issues/{id}` request.
2. How does refresh-token rotation detect a stolen token?
3. Why do non-members get 404 instead of 403?
4. How do you prevent lost updates when two people edit the same issue?
5. Why do you evict the cache after commit and not inside the transaction?

---

**Answers**
1. Login verifies the password hash and issues a signed JWT (+ refresh token). On `PATCH`, the bearer filter validates signature/expiry/issuer/audience and builds an `Authentication`; `AuthorizationFilter` checks the URL rule; `@PreAuthorize` calls the membership bean for the object-level check; the service loads the issue, checks `If-Match` against `@Version`, applies the change and writes the audit event in one transaction.
2. Each refresh returns a new refresh token and invalidates the old one; all tokens from one login share a family ID. If an already-used token is presented again, someone replayed it — revoke the whole family so both the thief and the user must log in again.
3. 403 confirms the resource exists; 404 avoids leaking the existence of private projects/issues to non-members.
4. Optimistic locking: the client sends the ETag (version) it read; the update includes `WHERE version = ?`; if another update won first, 0 rows change and the API returns 409/412 so the client re-reads.
5. If you evict inside the transaction and it rolls back, or another request re-reads before the commit, the cache can be refilled with stale data. After commit, the new state is visible, so the next read caches the correct value.

---

## Project JM2 — CreditLine Reporting Service · Middle (~55h)

**Goal:** build the outward-facing Spring Boot service of a loan system in which
**Oracle owns the rules and Spring owns the boundary.** You write a small set of
PL/SQL packages (amortization schedule and reporting) on Oracle Database Free,
and a Spring Boot API that calls them — never re-implementing the rules in
Java. Based on the CreditLine design (loan products, schedules, delinquency
aging, portfolio reports).

### Features
- [ ] **Schema (Oracle):** a reduced CreditLine model — `branches`, `app_users`, `customers`, `loan_products`, `rate_history`, `holiday_calendar`, `loans`, `schedules` (versioned, exactly one active per loan via a function-based unique index), `schedule_lines`, `loan_transactions` (range-partitioned by month), `delinquency_snapshots`, `period_status`, `audit_log`. Seed data generator for ~10 000 loans (PL/SQL or SQL script).
- [ ] **`pkg_schedule` (you write it):** `preview_schedule(p_product_id, p_amount, p_term_m, p_first_due_date, p_rc out sys_refcursor)` for annuity, declining-balance and flat methods with business-day adjustment against `holiday_calendar`; `generate_schedule(p_loan_id, p_reason, p_schedule_id out)` that versions schedules (old one deactivated, new one active). No `COMMIT` inside.
- [ ] **`pkg_report` (you write it):** REF CURSOR procedures for **portfolio at risk** by branch (PAR30/PAR90), **aging buckets** (1–30, 31–60, 61–90, 90+ as columns via `PIVOT`), and **cash position** by date range (disbursed vs repaid, `GROUPING SETS`/`ROLLUP` subtotals).
- [ ] **Error codes:** each package spec declares constants; `RAISE_APPLICATION_ERROR` with `-20001 INVALID_AMOUNT`, `-20002 TERM_OUT_OF_RANGE`, `-20005 LOAN_NOT_FOUND`, `-20007 PERIOD_CLOSED`, `-20010 ACTIVE_SCHEDULE_CONFLICT`.
- [ ] **Spring API:**
  - `POST /schedules/preview` → calls `pkg_schedule.preview_schedule`, returns lines with `BigDecimal` amounts.
  - `POST /loans/{id}/schedules` → calls `generate_schedule` inside a Spring `@Transactional` method; returns 201 with the new version.
  - `GET /reports/par?branch=&asOf=`, `GET /reports/aging?asOf=`, `GET /reports/cash-position?from=&to=` → REF CURSOR results mapped to records; CSV download option for aging (`Accept: text/csv`), streamed.
- [ ] **Error contract:** custom `SQLExceptionTranslator` → domain exceptions → `ProblemDetail` (`-20007 PERIOD_CLOSED` → 409, `-20001/-20002` → 422, `-20005` → 404, `-20010` → 409); one table in `docs/error-contract.md` and a test that iterates over it.
- [ ] **Identity bridge:** before each package call, set `DBMS_SESSION.SET_IDENTIFIER` (and clear it after) with the authenticated username so `audit_log` (written by an autonomous-transaction `pkg_audit`) shows the real user, not the pool user.
- [ ] **Security:** JWT resource server (reuse your JM1 issuer or a simple dev issuer); roles `ANALYST` (reports), `OFFICER` (schedules), branch-scoped PAR for non-admins.
- [ ] **Reference-data cache:** products, branches and holiday calendar cached in Redis (TTL + eviction endpoint for admins). Never cache report results that include balances.
- [ ] **Performance notes:** `DBMS_XPLAN` plans for the aging and PAR queries before and after adding the right indexes / partition pruning, recorded in `docs/tuning.md`; JDBC fetch size tuned for the CSV export.

### Tech stack
| Tool / library | Taught in |
|---|---|
| Oracle Database Free (`gvenzl/oracle-free`), SQL, PL/SQL packages, partitioning, `PIVOT`, `GROUPING SETS`, autonomous transactions | 1C Part 3 (3.1–3.10) |
| utPLSQL (package tests) | 1C 3.11 |
| ojdbc, UCP or HikariCP, Oracle type mapping (`NUMBER`→`BigDecimal`, `DATE`→`LocalDateTime`) | J5.2, J5.3 |
| Calling PL/SQL from Java (`CallableStatement`, REF CURSOR) | J5.5 |
| Oracle performance from Java (fetch size, statement caching) | J5.9 |
| Flyway (versioned tables + repeatable `R__` packages) | J5.4 |
| Spring Boot, MVC, ProblemDetail, springdoc | J7.1, J7.2 |
| `SimpleJdbcCall`, `JdbcClient`, `@Transactional`, exception translation | J7.5 |
| Spring Security resource server, method security | J7.6 |
| Spring Cache + Redis | J7.7 |
| Testcontainers (`oracle-free` module, Redis) | J4.3, J7.4 |
| JUnit 5, AssertJ, parameterized tests | J4.2 |

### Required knowledge
- Track 1C Part 3 completely (you write the packages, triggers-free design, autonomous audit, partitioning, analytic SQL, `DBMS_XPLAN`, utPLSQL).
- Track 4: J5.1–J5.9, J6.x, J7.1–J7.7.
- Track 2 concepts: B7 (transaction ownership), B12 (what not to cache).

### Milestones
- [ ] **M1 — Oracle foundation (~8 h):** Oracle Free container + Compose; Flyway V1..Vn for the schema (incl. monthly partitioning and the one-active-schedule function-based unique index); seed generator; `docs/data-model.md`. Tag `v0.1-oracle-schema`.
- [ ] **M2 — `pkg_schedule` (~12 h):** three interest methods, business-day adjustment, versioned generation; utPLSQL tests against **hand-computed** schedules (put the spreadsheet or calculation in `docs/`), including the rounding of the last instalment. Tag `v0.2-pkg-schedule`.
- [ ] **M3 — Spring boundary for schedules (~10 h):** `SimpleJdbcCall` gateways, record mappers, `@Transactional` ownership (prove with a test that a Java exception after the call rolls back the new schedule), error-code translation table + tests. Tag `v0.3-schedule-api`.
- [ ] **M4 — `pkg_report` + report endpoints (~12 h):** PAR, aging (`PIVOT`), cash position (`GROUPING SETS`); REF CURSOR → records; streamed CSV with tuned fetch size. Tag `v0.4-reports`.
- [ ] **M5 — Security, identity bridge, cache (~7 h):** resource server + branch scoping; `SET_IDENTIFIER` around calls (test that `audit_log.changed_by` equals the API user); Redis reference-data cache. Tag `v0.5-security-cache`.
- [ ] **M6 — Tuning & docs (~6 h):** before/after `DBMS_XPLAN` for two reports at 10 000+ loans; README "Oracle owns the rules, Spring owns the boundary" with a sequence diagram of one call. Tag `v1.0-jm2`.

### Definition of done
- [ ] No business rule (interest math, aging buckets, period checks) exists in Java — code review against this rule is written in the README.
- [ ] No PL/SQL package issues `COMMIT`/`ROLLBACK` (except autonomous `pkg_audit`); a test proves Spring owns the transaction.
- [ ] utPLSQL suite and the Spring integration suite both run in `./mvnw verify` (or CI script) against `gvenzl/oracle-free` Testcontainers.
- [ ] Every error code in the contract table has a test from HTTP down to the package.
- [ ] Money is `BigDecimal` from `NUMBER` to JSON; Oracle `DATE` mapped to `LocalDateTime` where time matters.
- [ ] `audit_log` shows the real API user for every write.
- [ ] Tuning doc shows at least one plan improvement with numbers.

**Estimated hours:** ~55 h

### Interview questions about this project
1. Why did you keep the amortization logic in PL/SQL instead of Java?
2. How does an Oracle error raised in a package become an HTTP 409?
3. Who owns the transaction when Spring calls a PL/SQL procedure, and what breaks if the package commits?
4. How does the audit log know the real user when every call uses the same pooled DB user?
5. How did you return a report from PL/SQL to Java, and how did you keep large exports memory-safe?

---

**Answers**
1. The database is the single place the rules live, so every client (APEX, batch, API) gets the same result; set-based logic runs next to the data; Java stays a thin boundary. The cost is PL/SQL skills and testing (utPLSQL) — accepted and covered.
2. The package raises `RAISE_APPLICATION_ERROR(-20007, ...)`; the driver throws `SQLException` with error code 20007; a custom `SQLExceptionTranslator` converts it to `PeriodClosedException`; `@RestControllerAdvice` maps that to a 409 `ProblemDetail` with `code = PERIOD_CLOSED`. The mapping table is documented and tested.
3. The Spring service method (`@Transactional`) owns it. If the package commits, it also commits earlier work on the same connection and Spring can no longer roll it back — partial writes. Only autonomous-transaction audit/error logging may commit independently.
4. Before the call the gateway sets `DBMS_SESSION.SET_IDENTIFIER(username)` on the borrowed connection (and clears it afterwards so the next borrower does not inherit it); `pkg_audit` reads `SYS_CONTEXT('USERENV','CLIENT_IDENTIFIER')`.
5. A `SYS_REFCURSOR` OUT parameter read with `SimpleJdbcCall` and a `RowMapper`; for the CSV export, rows are streamed to the response with a tuned fetch size (e.g. 500–1000) instead of materialising a `List`, so memory stays flat regardless of row count.

---

## Module J7.8 — Spring Batch & Scheduling (~7h)

**Topics:** batch vs online processing; Spring Batch domain model (`Job`,
`Step`, `JobInstance`, `JobExecution`, `StepExecution`, `JobParameters`,
`ExecutionContext`); the `JobRepository` and its metadata tables (created on
Oracle with the vendor schema script); tasklet steps vs **chunk-oriented**
steps (read → process → write, commit interval); readers and writers
(`FlatFileItemReader` for delimited and fixed-length files, `JdbcPagingItemReader`,
`JdbcCursorItemReader`, `JdbcBatchItemWriter`, `ItemProcessor` for validation
and mapping); fault tolerance (**skip** and **retry** policies, skip limits,
`SkipListener` to log bad rows); **restartability** (what "restart from where it
failed" really means, `saveState`, why a reader must be restartable);
identifying parameters and why the same parameters cannot run twice once they
completed; job flow (conditional steps, `JobExecutionDecider`); scaling basics
(multi-threaded step vs **partitioning** vs remote chunking — only the first two
here); launching jobs (`JobLauncher`, `JobOperator`, running on startup vs on
demand); `@Scheduled` (cron, fixed rate/delay, time zones) and why it runs on
**every** instance; **ShedLock** for single-instance scheduling; Spring Batch
vs PL/SQL `BULK COLLECT`/`FORALL` vs `DBMS_SCHEDULER` — where each belongs.

### Lessons
- [ ] **J7.8.L1 Domain language.** Spring Batch Reference → "The Domain Language of Batch" (Job, JobInstance, JobParameters, JobExecution, Step, StepExecution, ExecutionContext, JobRepository, JobLauncher).
- [ ] **J7.8.L2 Configuring a job and the repository.** Spring Batch Reference → "Configuring and Running a Job" (configuring a JobRepository, database type, table prefix, running a job from the command line and from a web container). Spring Boot Reference → "Batch Applications" (how-to section: running jobs on startup, `spring.batch.job.name`, schema initialization).
- [ ] **J7.8.L3 Chunk-oriented steps.** Spring Batch Reference → "Configuring a Step" → "Chunk-oriented Processing", "Configuring the Commit Interval", "Configuring a Step for Restart", "Configuring Skip Logic", "Configuring Retry Logic", "Controlling Rollback", "Intercepting Step Execution" (listeners).
- [ ] **J7.8.L4 Readers and writers.** Spring Batch Reference → "ItemReaders and ItemWriters" → "Flat Files" (`FlatFileItemReader`, `DelimitedLineTokenizer`, `FixedLengthTokenizer`, `FieldSetMapper`), "Database" (cursor-based vs paging `ItemReader`s, `JdbcBatchItemWriter`), "Making ItemReaders and ItemWriters Restartable".
- [ ] **J7.8.L5 Processing and validation.** Spring Batch Reference → "Item processing" (chaining processors, filtering records, validating input with `BeanValidatingItemProcessor`, fault tolerance).
- [ ] **J7.8.L6 Scaling.** Spring Batch Reference → "Scaling and Parallel Processing" → "Multi-threaded Step", "Partitioning". Read "Remote Chunking" only for the vocabulary.
- [ ] **J7.8.L7 Scheduling.** Spring Framework Reference → "Task Execution and Scheduling" → "Annotation Support for Scheduling and Asynchronous Execution" (`@Scheduled`, cron expressions, `zone`). ShedLock README (github.com/lukas-krecan/ShedLock): "Usage", "Configure LockProvider" → "JdbcTemplate", "Lock assert", the section on `lockAtMostFor` / `lockAtLeastFor`.
- [ ] **J7.8.L8 Where batch belongs.** Re-read your Track 1C notes for 3.7 (BULK COLLECT/FORALL, SAVE EXCEPTIONS) and 3.9 (DBMS_SCHEDULER chains). Baeldung: "Introduction to Spring Batch", "Spring Batch – Tasklets vs Chunks", "Configuring Skip Logic in Spring Batch", "Configuring Retry Logic in Spring Batch".

### Exercises (`java/J07-08-batch/`)
- [ ] **Ex J7.8.1 First chunk job.** A job with one chunk step that reads a 10 000-line CSV of `customer_id,email,signup_date` with `FlatFileItemReader`, uppercases nothing, validates the email in an `ItemProcessor` (invalid → filtered, not failed) and writes with `JdbcBatchItemWriter` into PostgreSQL (Testcontainers). *Acceptance:* a test asserts written rows = valid lines, and `BATCH_STEP_EXECUTION` shows the right read/write/filter counts.
- [ ] **Ex J7.8.2 Skip and log.** Extend Ex 1 with lines that have the wrong number of columns. Configure a skip policy for `FlatFileParseException` with a skip limit of 50 and a `SkipListener` that writes the line number and raw line to an `import_errors` table. *Acceptance:* a file with 7 broken lines finishes `COMPLETED` with 7 rows in `import_errors`; a file with 60 broken lines ends `FAILED`.
- [ ] **Ex J7.8.3 Restart for real.** Make the writer throw on record 6 500 (a test flag). Run the job: it fails. Remove the flag and restart the *same* `JobInstance`. *Acceptance:* the restart processes only the records after the last committed chunk (prove it with counts), and no row is written twice (unique key in the target table).
- [ ] **Ex J7.8.4 JobRepository on Oracle.** Point the JobRepository at Oracle Database Free (`gvenzl/oracle-free` Testcontainers) with the Oracle schema script shipped in the Spring Batch jar, and run Ex 1 against it. *Acceptance:* the `BATCH_*` tables exist in Oracle and a second run with the same identifying parameters is rejected with `JobInstanceAlreadyCompleteException`; explain why in `NOTES.md`.
- [ ] **Ex J7.8.5 Single-instance schedule.** Trigger the job from `@Scheduled(cron = …)` and start two instances of the app against the same database. Add ShedLock with the JDBC lock provider. *Acceptance:* without ShedLock, logs show two runs per tick; with ShedLock, exactly one; `NOTES.md` explains how you chose `lockAtMostFor`.
- [ ] **Ex J7.8.6 Partitioned step.** Partition Ex 1 by `customer_id` range into 4 partitions with a `TaskExecutorPartitionHandler`. *Acceptance:* timing before/after recorded in `NOTES.md`, plus one paragraph on why partitioning is safer than a multi-threaded step with a non-thread-safe reader.

### Must be able to do / explain
- [ ] Draw the Spring Batch domain model and say which object is persisted where.
- [ ] Explain chunk processing, the commit interval and what is rolled back when a write fails.
- [ ] Configure skip vs retry and say which exceptions deserve which.
- [ ] Explain exactly what restart resumes from and why the reader must keep state.
- [ ] Explain identifying job parameters and `JobInstanceAlreadyCompleteException`.
- [ ] Explain why `@Scheduled` runs on every replica and how ShedLock prevents it.
- [ ] Decide between Spring Batch, PL/SQL bulk processing and `DBMS_SCHEDULER` for a given job, and defend it.

**Estimated hours:** ~7h

### Self-check interview questions
1. What is the difference between a `JobInstance` and a `JobExecution`?
2. What happens inside one chunk when the writer throws halfway?
3. When would you choose a tasklet step over a chunk step?
4. Skip vs retry: give one exception type that fits each.
5. What makes a Spring Batch job restartable, and what breaks restartability?
6. Why does a paging reader need a deterministic sort key?
7. Your app runs 3 replicas; a `@Scheduled` job sends invoices twice. Why, and how do you fix it?
8. A nightly accrual over 2 million loans: Spring Batch or PL/SQL? Why?

---

**Answers**
1. A `JobInstance` is the logical run identified by job name + identifying parameters (e.g. "import for 2026-09-27"). A `JobExecution` is one attempt at it; a failed instance can have several executions until one completes.
2. The chunk's transaction rolls back. With a skip policy, Spring Batch re-processes the chunk item by item ("scan") to find and skip the failing item, then commits the rest; without one, the step fails and the last committed chunk is the restart point.
3. For a single action that is not naturally a stream of items: deleting a staging table, calling one PL/SQL procedure, moving a file, sending a summary.
4. Skip: a parse/validation error in one input line (retrying will not fix bad data). Retry: a transient `DeadlockLoserDataAccessException` or a timeout to a downstream (the same item may succeed on the next attempt).
5. State stored in the `ExecutionContext` (reader position, counts) after each commit, plus a `JobRepository` that persists it. Readers that do not save state, non-deterministic input order, or side effects outside the chunk transaction break it.
6. Each page is a separate query; without a stable, unique ORDER BY, rows can move between pages as data changes, so items are skipped or read twice, and restart positions become meaningless.
7. `@Scheduled` is local to each JVM, so every replica fires. Use a distributed lock (ShedLock on a DB table), a single dedicated scheduler instance, or an external scheduler (Kubernetes CronJob), and make the job idempotent anyway.
8. Usually PL/SQL: it is set-based, the data never leaves the database, and `BULK COLLECT`/`FORALL` with `SAVE EXCEPTIONS` gives chunked, error-tolerant processing. Spring Batch wins when input comes from outside (files, APIs), when you need rich restart/monitoring outside the DB, or when logic lives in Java.

---

## Project JM3 — CreditLine Nightly Batch · Middle (~50h)

**Goal:** build the batch side of a loan-servicing system on **Oracle**: a
restartable, idempotent **Spring Batch** import of a bank payment file where
every valid payment is posted by the existing PL/SQL package
`pkg_payment.post_payment`, plus a scheduled job that triggers the daily
accrual package. Then build the same file import in pure PL/SQL and compare
them with numbers. This is exactly the "Java + Oracle shop" question: *when do
you move work out of the database, and when do you leave it there?*

**Domain (from CreditLine):** loans with active repayment schedules; payments
arrive in a daily bank file; `pkg_payment` owns the **allocation waterfall**
(penalties → fees → overdue interest → current interest → principal) and
returns the allocation lines; `pkg_accrual` accrues daily interest; the batch
is recorded in `batch_runs` and per-row failures in `batch_errors`. **Oracle owns
the rules, Spring owns the boundary:** Java never computes an allocation.

### Features
- [ ] Oracle schema (Flyway, `V__` for tables, `R__` for packages): `customers`, `loans`, `schedule_lines`, `loan_transactions`, `payment_allocations`, `bank_files`, `bank_file_lines`, `batch_runs`, `batch_errors`, `audit_log`.
- [ ] PL/SQL (written by you, Track 1C Part 3 skills): `pkg_payment.post_payment(p_loan_id, p_amount, p_value_date, p_external_ref, p_txn_id OUT, p_allocations OUT SYS_REFCURSOR)` with the waterfall and domain errors as codes (`-20007 PERIOD_CLOSED`, `-20010 LOAN_NOT_ACTIVE`, `-20011 DUPLICATE_PAYMENT`); `pkg_accrual.accrue(p_business_date)` with `BULK COLLECT … LIMIT` + `FORALL … SAVE EXCEPTIONS`; **no COMMIT inside packages**; `pkg_audit` via autonomous transaction.
- [ ] Bank file format: both CSV and fixed-width variants (`FlatFileItemReader` with `DelimitedLineTokenizer` / `FixedLengthTokenizer`), a header line with file date and control totals, a trailer with line count and sum.
- [ ] Job `paymentFileImportJob(fileName, businessDate)`: step 1 validates header/trailer control totals (tasklet); step 2 chunk step: parse → validate (loan exists, amount > 0, value date not in a closed period) → post via `SimpleJdbcCall` to `pkg_payment.post_payment`; step 3 writes a summary to `batch_runs`.
- [ ] Skip and log: parse errors and domain errors (`LOAN_NOT_ACTIVE`, `PERIOD_CLOSED`) are skipped and written to `batch_errors` with line number, error code and raw line; infrastructure errors (connection loss, deadlock) are retried then fail the step.
- [ ] **Idempotent re-run:** a second import of the same file (same file hash) does not post anything twice — enforced by a unique constraint on `(external_ref)` in `loan_transactions`, not only by a Java check; `DUPLICATE_PAYMENT` is counted, not treated as a failure.
- [ ] **Restart from failure:** kill the app mid-file; restarting the same `JobInstance` continues from the last committed chunk.
- [ ] Job `dailyAccrualJob(businessDate)`: a tasklet that calls `pkg_accrual.accrue`, scheduled with `@Scheduled` + **ShedLock** so only one instance runs it; a re-run for the same business date is a no-op (unique constraint on `(loan_id, accrual_date)`).
- [ ] Oracle error codes translated by a custom `SQLExceptionTranslator` into domain exceptions (J7.5).
- [ ] `GET /batch-runs` and `GET /batch-runs/{id}/errors` (paginated) monitoring endpoints; `POST /batch-runs/payment-import` to launch a job on demand (admin role, Spring Security from J7.6).
- [ ] Pure-PL/SQL version of the same import (external table or `UTL_FILE` → `bank_file_lines` → `FORALL … SAVE EXCEPTIONS` calling the same package logic) and **`docs/batch-comparison.md`**: throughput on the same 100 000-line file, restartability, error visibility, testability, operational cost — with numbers and your recommendation.
- [ ] Micrometer counters for lines read/posted/skipped and a timer per step exposed through Actuator (only the basics taught so far: `/actuator/health`, `/actuator/metrics` from J7.1; full observability comes in J7.12).

### Tech stack
| Tool / library | Taught in |
|---|---|
| Java 25, records, Streams | J1, J2 |
| Maven or Gradle (multi-module optional) | J4.1 |
| JUnit 5, AssertJ, Mockito, Testcontainers (`gvenzl/oracle-free`) | J4.2, J4.3, J5.3 |
| SLF4J + Logback | J4.4 |
| ojdbc, UCP / HikariCP | J5.2, J5.3 |
| Flyway (versioned + repeatable migrations) | J5.4 |
| CallableStatement, REF CURSOR, PL/SQL packages from Java | J5.5 |
| Oracle performance: fetch size, batching | J5.9 |
| Spring Boot, configuration properties, profiles | J6.2, J7.1 |
| `@Transactional`, transaction ownership, `SimpleJdbcCall`, `SQLExceptionTranslator` | J6.3, J7.5 |
| Spring MVC + ProblemDetail for monitoring endpoints | J7.2 |
| Spring Security (admin-only launch endpoint) | J7.6 |
| Spring Batch, `@Scheduled`, ShedLock | J7.8 |
| PL/SQL packages, BULK COLLECT/FORALL, SAVE EXCEPTIONS, external tables/UTL_FILE, autonomous transactions | Track 1C 3.5, 3.7, 3.9 |
| utPLSQL for package tests | Track 1C 3.11 |

### Required knowledge
J1–J4, J5.1–J5.9, J6.1–J6.4, J7.1–J7.8; Track 1C Part 3 (3.1–3.11). JM2 CreditLine Reporting Service is recommended first (it builds the same schema and the `SimpleJdbcCall` + REF CURSOR pattern).

### Milestones
**M1 — Schema and packages** (`v0.1-schema`)
- [ ] Flyway migrations for all tables, unique constraints for idempotency (`external_ref`, `(loan_id, accrual_date)`).
- [ ] `pkg_payment.post_payment` with the waterfall, domain error codes, no COMMIT.
- [ ] `pkg_accrual.accrue` with `BULK COLLECT … LIMIT` + `FORALL … SAVE EXCEPTIONS` into `batch_errors`.
- [ ] utPLSQL tests: waterfall order, overpayment, closed period, duplicate reference.

**M2 — Posting boundary in Java** (`v0.2-posting`)
- [ ] `PaymentPostingGateway` using `SimpleJdbcCall` with IN/OUT params and REF CURSOR mapped to records.
- [ ] Custom `SQLExceptionTranslator`: `-20007/-20010/-20011` → domain exceptions.
- [ ] Integration tests on Testcontainers Oracle proving the Java side never computes allocations.

**M3 — Import job** (`v0.3-import`)
- [ ] Header/trailer control-total validation tasklet.
- [ ] Chunk step with CSV and fixed-width readers, validation processor, posting writer.
- [ ] Skip policy + `SkipListener` → `batch_errors`; retry policy for transient errors.
- [ ] JobRepository on Oracle.

**M4 — Restart, idempotency, scheduling** (`v0.4-resilient`)
- [ ] Test: kill mid-file, restart, no duplicates, counts match the trailer.
- [ ] Test: import the same file twice → second run posts 0, reports N duplicates.
- [ ] `dailyAccrualJob` with `@Scheduled` + ShedLock; test with two app instances.
- [ ] Monitoring and launch endpoints secured with the admin role.

**M5 — Comparison** (`v1.0-creditline-batch`)
- [ ] Pure-PL/SQL import path.
- [ ] 100 000-line benchmark file generator; timings for both paths with 3 chunk/`LIMIT` sizes each.
- [ ] `docs/batch-comparison.md` with the numbers, failure-mode comparison and a recommendation.
- [ ] README with architecture diagram and how to run.

### Definition of done
- [ ] `./mvnw verify` (or `./gradlew check`) runs all unit, utPLSQL and Testcontainers tests green.
- [ ] Re-running any job for the same inputs changes nothing (proved by tests).
- [ ] A restarted import posts exactly the missing payments.
- [ ] No COMMIT/ROLLBACK in any package except the autonomous audit/error writers.
- [ ] One bad line never aborts the file; every skipped line is visible in `batch_errors`.
- [ ] `docs/batch-comparison.md` contains measured numbers, not opinions only.

**Estimated hours:** ~50h (M1 12h · M2 8h · M3 12h · M4 10h · M5 8h)

### Interview questions about this project
1. Why does the allocation waterfall live in PL/SQL and not in Java?
2. How do you guarantee a payment file imported twice does not double-post?
3. What happens if `pkg_payment` issues a COMMIT inside your Spring transaction?
4. Walk through what happens when the app dies at line 60 000 of 100 000.
5. Which was faster, Spring Batch or PL/SQL, and would you still choose the slower one?

---

**Answers**
1. The rules must be identical for every channel (APEX screens, API, batch) and must run next to the data inside one transaction; putting them in the package gives one source of truth, and Java only passes inputs and maps outputs.
2. A unique constraint on the payment's external reference in `loan_transactions`; the package raises `DUPLICATE_PAYMENT` which the job counts as a duplicate instead of failing. Spring Batch's identifying parameters and file hash are a second, weaker guard.
3. The commit ends the transaction Spring started; later work runs in a new implicit transaction, so a subsequent rollback cannot undo what was already committed — partial chunks become durable. Hence the rule: callers own transaction boundaries.
4. The last committed chunk is recorded in the `ExecutionContext`; on restart of the same `JobInstance` the reader skips to that position and continues. Anything after the last commit was rolled back, and the unique constraint protects against any payment that did get posted twice by an in-flight retry.
5. Answer with your numbers. Typically PL/SQL is faster (no network round trip per chunk), while Spring Batch gives better file handling, restart metadata and testing; the defensible choice depends on where the input comes from and who operates it.

---

## Module J7.9 — Spring AMQP with RabbitMQ (~4h)

**Topics:** the AMQP model recap (from Track 2 B15) in Spring terms;
`spring-boot-starter-amqp`; `ConnectionFactory`, `RabbitTemplate`,
`RabbitAdmin`; declaring `Exchange`, `Queue`, `Binding` as beans; message
converters (`Jackson2JsonMessageConverter`) and message properties;
`@RabbitListener` and listener containers (`SimpleMessageListenerContainer`
vs `DirectMessageListenerContainer`), concurrency and prefetch; acknowledge
modes (AUTO vs MANUAL), what AUTO really does on exception, requeue vs reject;
**retries** with a stateless retry interceptor and a dead-letter exchange
(DLX/DLQ); publisher confirms and returns; **idempotent consumers** (processed-
message table keyed by message id); testing with Testcontainers RabbitMQ.

### Lessons
- [ ] **J7.9.L1 Getting started.** spring.io/guides "Messaging with RabbitMQ". Spring Boot Reference → "Messaging" → "AMQP" (RabbitMQ support, sending a message, receiving a message).
- [ ] **J7.9.L2 Template and conversion.** Spring AMQP Reference → "Using Spring AMQP" → "AmqpTemplate", "Message Converters" (`Jackson2JsonMessageConverter`), "Publisher Confirms and Returns".
- [ ] **J7.9.L3 Configuring the broker.** Spring AMQP Reference → "Configuring the Broker" (declaring exchanges, queues, bindings; `RabbitAdmin`; conditional declaration).
- [ ] **J7.9.L4 Receiving messages.** Spring AMQP Reference → "Receiving Messages" → "Annotation-driven Listener Endpoints", "Message Listener Container Configuration" (concurrency, prefetch, acknowledge mode), "Choosing a Container".
- [ ] **J7.9.L5 Failures.** Spring AMQP Reference → "Exception Handling", "Message Listeners and the Asynchronous Case", "Resilience: Recovering from Errors and Broker Failures" → "Stateless retry", `RejectAndDontRequeueRecoverer`, `RepublishMessageRecoverer`. RabbitMQ docs "Dead Letter Exchanges" (recap from B15).
- [ ] **J7.9.L6 Testing.** Testcontainers docs → "RabbitMQ Module"; Spring Boot Reference → "Testcontainers" → "Service Connections". Baeldung: "Spring AMQP in Reactive Applications" (skim), "Error Handling with Spring AMQP".

### Exercises (`java/J07-09-amqp/`)
- [ ] **Ex J7.9.1 Topic routing.** Declare a topic exchange `loan.events` with queues `notifications` (bound to `loan.*.approved`) and `audit` (bound to `loan.#`). Publish 3 event types as JSON records. *Acceptance:* a Testcontainers test asserts which queue receives which events.
- [ ] **Ex J7.9.2 Poison message to DLQ.** A listener throws on a message with `amount < 0`. Configure 3 stateless retries with backoff, then dead-letter to `notifications.dlq`. *Acceptance:* the bad message ends in the DLQ after exactly 3 attempts (count them in logs); good messages are unaffected.
- [ ] **Ex J7.9.3 Idempotent consumer.** Deliver the same message (same `messageId`) twice. Make the consumer record processed ids in a `processed_messages` table with a unique key in the same transaction as the side effect. *Acceptance:* the side effect happens once; the duplicate is acknowledged and logged.
- [ ] **Ex J7.9.4 Publisher confirms.** Enable correlated publisher confirms and returns; publish to a routing key with no binding. *Acceptance:* your code logs the returned message and a test proves a confirm arrives for routed messages.
- [ ] **Ex J7.9.5 Manual ack experiment.** Switch the listener to MANUAL ack, kill the app before acking, restart. *Acceptance:* `NOTES.md` explains what you saw and why at-least-once implies duplicates.

### Must be able to do / explain
- [ ] Declare exchanges, queues and bindings as beans and explain when they are created.
- [ ] Explain AUTO vs MANUAL ack and what happens on a listener exception in each.
- [ ] Configure retry + DLQ and explain why infinite requeue is dangerous.
- [ ] Build an idempotent consumer and explain why it is required.
- [ ] Explain publisher confirms vs returns.

**Estimated hours:** ~4h

### Self-check interview questions
1. What does `@RabbitListener` do when the method throws, with default settings?
2. Why do you need both retries and a DLQ?
3. How do you make a consumer idempotent?
4. What is prefetch and how does it affect fairness and throughput?
5. Confirms vs returns — what does each tell you?
6. Where should the publish happen relative to the database commit?

---

**Answers**
1. With AUTO ack and default `requeue-rejected=true`, the message is rejected and requeued, which can create a tight redelivery loop; set `defaultRequeueRejected=false` or use a retry interceptor with a recoverer.
2. Retries handle transient failures; after they are exhausted a DLQ parks the message for inspection instead of losing it or blocking the queue.
3. Give messages a stable id and record processed ids (unique constraint) in the same transaction as the side effect, or make the side effect naturally idempotent (upsert by business key).
4. The number of unacknowledged messages the broker pushes to one consumer. High prefetch raises throughput but lets one slow consumer hoard messages; low prefetch improves fairness.
5. A confirm says the broker accepted (persisted/routed) the message; a return says the message was unroutable (mandatory flag) — a message can be returned and still confirmed.
6. After commit — ideally via the transactional outbox (J8.3); publishing inside the transaction risks sending events for rolled-back data, publishing after commit without an outbox risks losing the event if the app dies in between.

---

## Module J7.10 — Spring for Apache Kafka (~5h)

**Topics:** Kafka recap (Track 2 B16) in Spring terms; `spring-kafka`
auto-configuration; producer config (acks, idempotence, retries, linger,
keys and partitioning); `KafkaTemplate` and send results; serializers (JSON,
and why schemas/Avro matter — mention only); `@KafkaListener`, consumer groups,
`concurrency` vs partition count, manual vs batch acks, offset commit
strategies; **error handling**: `DefaultErrorHandler`, backoff, non-retryable
exceptions, `DeadLetterPublishingRecoverer` and dead-letter topics (DLT),
`@RetryableTopic` non-blocking retries; **transactions**: Kafka transactions,
`read_committed`, and why "exactly-once" does not extend to your database
(use outbox/idempotent consumers instead); rebalancing and graceful shutdown;
testing with Testcontainers Kafka (or `@EmbeddedKafka`).

### Lessons
- [ ] **J7.10.L1 Quick tour.** Spring for Apache Kafka Reference → "Quick Tour"; Spring Boot Reference → "Messaging" → "Apache Kafka Support".
- [ ] **J7.10.L2 Sending.** Spring for Apache Kafka Reference → "Using Spring for Apache Kafka" → "Sending Messages" (`KafkaTemplate`, `CompletableFuture` results, `ProducerFactory`). Kafka docs → "Producer Configs" (`acks`, `enable.idempotence`, `linger.ms`).
- [ ] **J7.10.L3 Receiving.** Spring for Apache Kafka Reference → "Receiving Messages" → "@KafkaListener Annotation", "Message Listener Containers" (concurrency, `AckMode`), "Committing Offsets".
- [ ] **J7.10.L4 Errors.** Spring for Apache Kafka Reference → "Handling Exceptions" → "DefaultErrorHandler", "Publishing Dead-letter Records"; "Non-Blocking Retries" (`@RetryableTopic`).
- [ ] **J7.10.L5 Transactions.** Spring for Apache Kafka Reference → "Transactions" (`KafkaTransactionManager`, `read_committed`); Confluent blog "Exactly-Once Semantics Are Possible: Here's How Kafka Does It" (read for limits).
- [ ] **J7.10.L6 Testing.** Testcontainers docs → "Kafka Module"; Spring for Apache Kafka Reference → "Testing Applications" (`@EmbeddedKafka`). Baeldung: "Intro to Apache Kafka with Spring", "Implementing Retry in Kafka Consumer", "Dead Letter Queue for Kafka With Spring".

### Exercises (`java/J07-10-kafka/`)
- [ ] **Ex J7.10.1 Keyed ordering.** Produce 1 000 `ClaimEvent`s for 10 claim ids to a 6-partition topic, keyed by claim id. *Acceptance:* a consumer test proves events for each claim arrive in order, and `NOTES.md` explains why ordering is per partition only.
- [ ] **Ex J7.10.2 Scaling a group.** Run a listener with `concurrency=3`, then 8, on the 6-partition topic. *Acceptance:* logs show partition assignment; explain why 2 threads were idle with 8.
- [ ] **Ex J7.10.3 DLT.** Configure `DefaultErrorHandler` with a fixed backoff of 3 attempts and `DeadLetterPublishingRecoverer`; mark `ValidationException` as not retryable. *Acceptance:* invalid records go to `claims.DLT` immediately, transient failures after 3 attempts; headers on the DLT record show the original exception.
- [ ] **Ex J7.10.4 Non-blocking retry.** Replace Ex 3 with `@RetryableTopic` (3 attempts, exponential backoff). *Acceptance:* a failing record does not block later records on the same partition; describe the ordering trade-off you just accepted.
- [ ] **Ex J7.10.5 Idempotent consumer on Postgres.** The consumer writes to Postgres; replay the topic from offset 0. *Acceptance:* no duplicate rows (unique event id); `NOTES.md` explains why Kafka transactions alone would not have guaranteed this.

### Must be able to do / explain
- [ ] Configure a safe producer (acks=all, idempotence) and explain each setting.
- [ ] Explain consumer groups, partition assignment and why concurrency > partitions is wasted.
- [ ] Choose between blocking retries + DLT and non-blocking retry topics.
- [ ] Explain what Kafka exactly-once covers and what it does not.
- [ ] Test Kafka code with Testcontainers.

**Estimated hours:** ~5h

### Self-check interview questions
1. How does Kafka guarantee ordering, and at what scope?
2. What happens when a consumer in a group dies?
3. Blocking retry vs `@RetryableTopic`: what do you gain and lose?
4. What does `enable.idempotence=true` protect against?
5. Can Kafka give exactly-once from topic to your Postgres table? How do you get the same effect?
6. When does offset commit happen with the default `AckMode.BATCH`, and what does that mean on a crash?
7. Why would you key events by aggregate id?

---

**Answers**
1. Per partition: records with the same key go to the same partition and are read in order by one consumer in the group.
2. The group rebalances; its partitions are reassigned to remaining consumers, which resume from the last committed offsets — uncommitted records are redelivered.
3. Blocking retry keeps per-partition order but stalls the partition; retry topics keep the partition flowing but break ordering for the retried record.
4. Duplicate writes caused by producer retries (it adds producer id + sequence numbers so the broker drops duplicates within a session).
5. Not end-to-end; Kafka transactions cover Kafka reads/writes. Use idempotent consumers (unique event id / upsert) or store offsets in the same DB transaction.
6. After the records returned by a poll are processed; a crash before the commit redelivers that batch — at-least-once, so consumers must be idempotent.
7. So all events of one aggregate land in one partition and are processed in order, and state per aggregate can be kept consistently.

---

## Module J7.11 — WebFlux & Project Reactor (~6h)

**Topics:** why reactive exists (non-blocking I/O, few threads, backpressure);
Reactive Streams interfaces (`Publisher`, `Subscriber`, `Subscription`,
`request(n)`); `Mono` and `Flux`; assembly vs subscription ("nothing happens
until you subscribe"); core operators (`map`, `flatMap`, `concatMap`,
`filter`, `zip`, `merge`, `switchIfEmpty`, `onErrorResume`, `retryWhen`,
`timeout`); schedulers (`boundedElastic`, `parallel`) and the rule "never
block on an event-loop thread"; **backpressure** strategies (`limitRate`,
`onBackpressureBuffer/Drop`); cold vs hot publishers; testing with
`StepVerifier`; Spring **WebFlux** (annotated controllers and functional
routes), **WebClient** (and why it is useful even in MVC apps), Server-Sent
Events with `Flux`; R2DBC (mention: reactive SQL drivers, not JPA);
debugging reactive code (checkpoints, `Hooks.onOperatorDebug`); **when NOT to
use reactive**: blocking drivers (JDBC, JPA), team skills, stack traces — and
why **virtual threads** (J3.4) now cover most "many concurrent I/O calls"
cases with plain imperative code.

### Lessons
- [ ] **J7.11.L1 Reactive Streams and Reactor basics.** Project Reactor Reference Guide → "Introduction to Reactive Programming" (blocking can be wasteful, from imperative to reactive), "Reactor Core Features" (`Flux`, `Mono`, simple ways to create and subscribe).
- [ ] **J7.11.L2 Operators.** Reactor Reference → "Which operator do I need?" (appendix) — work through "Creating a new sequence", "Transforming an existing sequence", "Handling errors", "Working with time". Reactor Reference → "Handling Errors" (`onErrorReturn`, `onErrorResume`, `retryWhen`).
- [ ] **J7.11.L3 Threading.** Reactor Reference → "Threading and Schedulers"; "How Do I Wrap a Synchronous, Blocking Call?" (FAQ).
- [ ] **J7.11.L4 Backpressure and testing.** Reactor Reference → "On Backpressure and Ways to Reshape Requests"; "Testing" (`StepVerifier`, virtual time).
- [ ] **J7.11.L5 WebFlux.** Spring Framework Reference → "Web on Reactive Stack" → "Spring WebFlux" → "Overview" (read "Applicability" and "Concurrency Model" carefully), "Annotated Controllers", "Functional Endpoints".
- [ ] **J7.11.L6 WebClient.** Spring Framework Reference → "Web on Reactive Stack" → "WebClient" (configuration, retrieve, exchange, timeouts). Baeldung: "Spring 5 WebClient", "Guide to Spring 5 WebFlux".
- [ ] **J7.11.L7 When not to.** Spring Boot Reference → "Virtual Threads" (`spring.threads.virtual.enabled`); re-read your J3.4 notes. Read the "Applicability" section of the WebFlux overview again and write your own decision checklist.

### Exercises (`java/J07-11-reactive/`)
- [ ] **Ex J7.11.1 Operator drills.** Write 10 `StepVerifier` tests that each pin down one operator's behaviour (e.g. `flatMap` vs `concatMap` ordering, `switchIfEmpty`, `onErrorResume`, `zip` with different lengths). *Acceptance:* each test name states the behaviour it proves.
- [ ] **Ex J7.11.2 Fan-out aggregator.** A WebFlux endpoint `GET /quotes/{id}/offers` calls 3 slow downstream stubs (WireMock or a local stub server, 200–800 ms each) with `WebClient`, combines results, applies a 1 s total timeout and a fallback for any failed call. *Acceptance:* p50 latency ≈ slowest call, not the sum; a failing stub yields a partial response.
- [ ] **Ex J7.11.3 Block the loop on purpose.** Add a `Thread.sleep(500)` inside a handler and load it with 200 concurrent requests. *Acceptance:* `NOTES.md` shows the throughput collapse and the fix (`boundedElastic`) with numbers, and explains why this is dangerous.
- [ ] **Ex J7.11.4 SSE price feed.** `GET /prices/stream` returns a `Flux<ServerSentEvent<Price>>` ticking every 200 ms; a slow client must not make the server buffer unbounded. *Acceptance:* a test with `StepVerifier` and virtual time; explain the backpressure strategy you chose.
- [ ] **Ex J7.11.5 Same thing, virtual threads.** Implement Ex 2 again in Spring MVC with `RestClient` and virtual threads. *Acceptance:* both versions load-tested with the same tool (plain loop or Gatling after J8.6); `NOTES.md` compares code complexity and results, and states when you would pick each.

### Must be able to do / explain
- [ ] Explain Reactive Streams and backpressure with `request(n)`.
- [ ] Choose the right operator for sequencing, merging, error handling and timeouts.
- [ ] Explain why blocking on an event-loop thread is fatal and how to isolate blocking calls.
- [ ] Test reactive code with `StepVerifier`, including virtual time.
- [ ] Argue when WebFlux is the right choice and when MVC + virtual threads is better.

**Estimated hours:** ~6h

### Self-check interview questions
1. What does "nothing happens until you subscribe" mean in practice?
2. `flatMap` vs `concatMap` vs `switchMap`?
3. What is backpressure and how does Reactor implement it?
4. How do you call a blocking JDBC method from WebFlux, and why is it still a smell?
5. Why would you use `WebClient` in a Spring MVC application?
6. When would you *not* choose WebFlux for a new service?
7. How do virtual threads change the reactive vs imperative trade-off?

---

**Answers**
1. Building a `Mono`/`Flux` only describes a pipeline; no I/O or computation runs until a subscriber subscribes (in WebFlux, the framework subscribes to what you return).
2. `flatMap` subscribes to inner publishers eagerly and interleaves results (no order); `concatMap` subscribes one at a time and keeps order; `switchMap` cancels the previous inner publisher when a new element arrives.
3. The subscriber tells the publisher how many items it can take (`request(n)`); operators propagate demand upstream, and strategies like buffer/drop/latest handle producers that cannot slow down.
4. Wrap it with `Mono.fromCallable(...).subscribeOn(Schedulers.boundedElastic())`; it works but reintroduces thread-per-call behaviour, so the reactive benefit is lost for that path.
5. For non-blocking parallel calls and streaming responses; although in new MVC code `RestClient` + virtual threads often covers the same need more simply.
6. When the stack is blocking (JDBC/JPA/Oracle PL/SQL calls), the team is not fluent in reactive, or the service is CRUD with modest concurrency — debugging and maintenance cost outweigh gains.
7. Virtual threads make blocking cheap, so imperative code can handle many concurrent I/O waits; reactive remains useful for streaming, backpressure and composition of many async sources.

---

## Module J7.12 — Actuator, Micrometer & Observability (~5h)

**Topics:** the three signals recap (Track 2 B24) in Spring terms; **Actuator**
endpoints (`health`, `info`, `metrics`, `prometheus`, `loggers`, `env`,
`threaddump`) and securing/exposing them; health indicators, **health groups**
and Kubernetes **liveness/readiness** probes; **Micrometer** concepts
(`MeterRegistry`, counters, gauges, timers, distribution summaries, tags and
cardinality), the Prometheus registry, histograms and SLO buckets; the
**Observation API** (`@Observed`, `ObservationRegistry`) and **Micrometer
Tracing** with the OpenTelemetry bridge (trace/span ids in logs, context
propagation over HTTP and messaging); **structured logging** in Spring Boot
(ECS/Logstash formats, `logging.structured.format.console`); custom business
metrics; dashboards in Grafana, alerts on RED metrics.

### Lessons
- [ ] **J7.12.L1 Actuator.** Spring Boot Reference → "Production-ready Features" → "Enabling Production-ready Features", "Endpoints" (exposing, security, health — "Auto-configured HealthIndicators", "Health Groups", "Kubernetes Probes").
- [ ] **J7.12.L2 Metrics.** Spring Boot Reference → "Production-ready Features" → "Metrics" (getting started, supported monitoring systems → Prometheus, supported metrics, registering custom metrics). Micrometer docs → "Concepts" (registry, meters, naming, tags, counters, gauges, timers, distribution summaries, histograms and percentiles).
- [ ] **J7.12.L3 Observations and tracing.** Spring Boot Reference → "Production-ready Features" → "Observability" and "Tracing" (OpenTelemetry bridge, propagating traces, logging correlation IDs). Micrometer docs → "Observation" (introduction, `@Observed`).
- [ ] **J7.12.L4 Structured logging.** Spring Boot Reference → "Core Features" → "Logging" → "Structured Logging".
- [ ] **J7.12.L5 Dashboards.** Grafana docs "Get started with Grafana and Prometheus"; Prometheus docs "Histograms and summaries" (recap). Baeldung: "Spring Boot Actuator", "Observability with Spring Boot 3".

### Exercises (`java/J07-12-observability/`)
- [ ] **Ex J7.12.1 Health that means something.** Add a custom `HealthIndicator` for an Oracle (or Postgres) connection and a downstream HTTP dependency; put the DB in the readiness group only. *Acceptance:* stopping the DB container flips `/actuator/health/readiness` to DOWN while liveness stays UP; `NOTES.md` explains why liveness must not depend on the DB.
- [ ] **Ex J7.12.2 RED metrics.** Expose `/actuator/prometheus`, run Prometheus + Grafana with Docker Compose, and build a dashboard with rate, error ratio and p95/p99 of `http.server.requests` per URI. *Acceptance:* screenshot in the repo and one PromQL query per panel in `NOTES.md`.
- [ ] **Ex J7.12.3 Business metric.** Add a counter `payments.posted` tagged by `channel` and a timer around the posting call; deliberately add a `loanId` tag, observe cardinality in Prometheus, then remove it. *Acceptance:* `NOTES.md` explains the cardinality problem with the series count you saw.
- [ ] **Ex J7.12.4 Distributed trace.** Two Boot apps: A calls B over `RestClient`, B publishes to RabbitMQ, a listener in A consumes. Export traces via OTLP to Jaeger or Tempo. *Acceptance:* one trace shows all three hops; log lines carry the same trace id.
- [ ] **Ex J7.12.5 Structured logs.** Switch console logging to ECS JSON and ship it (optionally) to Loki. *Acceptance:* a log line contains `trace.id`, `span.id`, and a custom MDC field.

### Must be able to do / explain
- [ ] Expose and secure Actuator endpoints safely.
- [ ] Design liveness vs readiness correctly.
- [ ] Pick the right Micrometer meter type and avoid high-cardinality tags.
- [ ] Wire Micrometer Tracing with OpenTelemetry and correlate logs with traces.
- [ ] Build a RED dashboard from Prometheus metrics.

**Estimated hours:** ~5h

### Self-check interview questions
1. Liveness vs readiness: what should each check?
2. Counter vs gauge vs timer — give an example of each.
3. Why is a user id a terrible metric tag?
4. How does a trace id travel from one service to the next over HTTP and over a message broker?
5. Which Actuator endpoints are dangerous to expose publicly and why?
6. What does `@Observed` give you compared with a hand-written timer?

---

**Answers**
1. Liveness: "is this process stuck?" (restart me) — only in-process checks. Readiness: "can I serve traffic now?" — includes dependencies like the DB; failing readiness removes the pod from load balancing without restarting it.
2. Counter: payments posted (only goes up). Gauge: current queue depth or pool active connections. Timer: request latency with count, sum and histogram.
3. Each distinct tag value creates a new time series; millions of users → millions of series, exhausting Prometheus memory and making queries slow.
4. Over HTTP in the W3C `traceparent` header; over messaging in message headers — Micrometer Tracing/OpenTelemetry instrumentation injects and extracts them.
5. `env`, `configprops`, `heapdump`, `threaddump`, `loggers` (write), `shutdown`: they leak secrets or allow changing behaviour; expose only `health`, `info`, `prometheus` and protect the rest.
6. One annotation produces both a metric (timer) and a span, with consistent naming and low-cardinality tags, instead of separate manual metric and tracing code.

---

# Part 8 — Microservices & Production

## Module J8.1 — Spring Cloud: Config, Gateway, OpenFeign, Discovery (~8h)

**Topics:** when microservices are worth it (recap: modular monolith first);
the Spring Cloud release train and BOM; **Config Server** (Git/native
backends, profiles and labels, encryption of properties, refresh and its
limits, `spring.config.import=configserver:`) vs Kubernetes ConfigMaps;
**Spring Cloud Gateway** (routes, predicates, filters, rewriting paths, rate
limiting with Redis, JWT validation at the edge with Spring Security, CORS at
the edge, the WebFlux-based vs server-MVC variants); **OpenFeign** declarative
HTTP clients (configuration, timeouts, error decoders, interceptors for auth
headers) vs `RestClient` with `@HttpExchange` interfaces; **service discovery**
(Eureka client/server, load-balanced clients with Spring Cloud LoadBalancer)
vs Kubernetes-native discovery via Services/DNS — and why most teams on
Kubernetes skip Eureka.

### Lessons
- [ ] **J8.1.L1 Overview.** spring.io/projects/spring-cloud (release trains, supported Boot versions). "Spring in Action" 6th ed. — read the chapters on configuration and the microservices-related material you find there as background; Baeldung "Spring Cloud – Bootstrapping".
- [ ] **J8.1.L2 Config Server.** Spring Cloud Config Reference → "Spring Cloud Config Server" (environment repository → Git backend, file system backend, security, encryption and decryption) and "Spring Cloud Config Client" (config data import, fail fast, retry). spring.io/guides "Centralized Configuration".
- [ ] **J8.1.L3 Gateway.** Spring Cloud Gateway Reference → "Glossary", "How It Works", "Configuring Route Predicate Factories and Gateway Filter Factories", "Route Predicate Factories" (Path, Method, Header), "GatewayFilter Factories" (RewritePath, AddRequestHeader, RequestRateLimiter, Retry, CircuitBreaker), "Global Filters". spring.io/guides "Building a Gateway".
- [ ] **J8.1.L4 OpenFeign.** Spring Cloud OpenFeign Reference → "Declarative REST Client: Feign" (how to include, overriding defaults, timeouts, `RequestInterceptor`, `ErrorDecoder`, Feign and Spring Cloud CircuitBreaker). Spring Framework Reference → "REST Clients" → "HTTP Interface" (`@HttpExchange`) for the modern alternative.
- [ ] **J8.1.L5 Discovery.** Spring Cloud Netflix Reference → "Service Discovery: Eureka Clients" and "Eureka Server" (just enough to run it); Spring Cloud Commons → "Spring Cloud LoadBalancer". Spring Cloud Kubernetes Reference → "DiscoveryClient for Kubernetes" (read the intro and when to use it). spring.io/guides "Service Registration and Discovery".

### Exercises (`java/J08-01-cloud/`)
- [ ] **Ex J8.1.1 Central config.** Run Config Server backed by a local Git repo with `application.yml`, `quote-service.yml` and `quote-service-prod.yml`; a client reads a property per profile. *Acceptance:* changing a value in Git + refresh endpoint updates a `@RefreshScope` bean; `NOTES.md` lists what refresh can and cannot change.
- [ ] **Ex J8.1.2 Encrypted secret.** Store a DB password encrypted (`{cipher}`) in the config repo. *Acceptance:* the client receives the decrypted value; the Git repo never contains plaintext; explain why Vault/K8s Secrets are still better for production.
- [ ] **Ex J8.1.3 Gateway routing.** Route `/api/quotes/**` → quote-service, `/api/policies/**` → policy-service with path rewriting, add a correlation-id header filter and Redis-backed `RequestRateLimiter` (10 req/s per user). *Acceptance:* a test shows 429 above the limit and headers propagated downstream.
- [ ] **Ex J8.1.4 JWT at the edge.** Validate JWTs at the gateway (Resource Server config from J7.6) and forward the token downstream; downstream services still validate. *Acceptance:* requests without a token get 401 at the gateway; explain in `NOTES.md` why downstream validation is kept (zero trust).
- [ ] **Ex J8.1.5 Feign client with errors.** policy-service calls quote-service via OpenFeign with 500 ms connect/read timeouts and an `ErrorDecoder` mapping 404 → `QuoteNotFoundException`, 409 → `QuoteExpiredException`. *Acceptance:* WireMock tests for each mapping and the timeout.
- [ ] **Ex J8.1.6 Discovery two ways.** Register two quote-service instances in Eureka and call them via a load-balanced client; then remove Eureka and use a static DNS name (as Kubernetes would). *Acceptance:* `NOTES.md` compares the two with a recommendation for a Kubernetes deployment.

### Must be able to do / explain
- [ ] Run Config Server and explain profiles, labels, refresh and encryption.
- [ ] Configure Gateway routes, predicates and filters including rate limiting and auth.
- [ ] Build Feign (or `@HttpExchange`) clients with timeouts and error mapping.
- [ ] Explain client-side discovery vs Kubernetes service discovery.

**Estimated hours:** ~8h

### Self-check interview questions
1. What problem does Config Server solve, and what does it not solve?
2. Why put JWT validation at the gateway if every service validates too?
3. What is the difference between a predicate and a filter in Spring Cloud Gateway?
4. How does a Feign client decide which instance to call when discovery is enabled?
5. Why is Eureka usually unnecessary on Kubernetes?
6. What is the risk of `@RefreshScope` beans?
7. OpenFeign vs `RestClient` + `@HttpExchange` — which would you pick today?

---

**Answers**
1. Central, versioned, per-environment configuration for many services. It does not replace a real secret store or make runtime changes safe by itself (many beans need restarts).
2. To reject bad traffic early and apply edge policies (rate limits per user), while downstream validation keeps services safe from internal callers and misrouting (defence in depth).
3. Predicates decide whether a route matches a request (path, header, method); filters modify the request/response or behaviour (rewrite path, add headers, rate limit, retry).
4. Spring Cloud LoadBalancer asks the `DiscoveryClient` for instances of the service id and picks one (round-robin by default).
5. Kubernetes Services already provide stable DNS names and load balancing across healthy pods; a second registry adds moving parts without benefit.
6. Beans are recreated on refresh; in-flight state is lost, and partially refreshed config can leave the system inconsistent — prefer restart/rollout for significant changes.
7. For new code, usually `RestClient`/`@HttpExchange` (part of Spring Framework, no extra dependency); OpenFeign remains fine in existing Spring Cloud codebases.

---

## Module J8.2 — Resilience4j (~4h)

**Topics:** resilience recap (Track 2 B22) in Java; Resilience4j modules:
**CircuitBreaker** (count vs time sliding windows, failure-rate and slow-call
thresholds, half-open probes), **Retry** (max attempts, exponential backoff
with jitter, retry-on predicates, idempotency requirement), **Bulkhead**
(semaphore vs thread-pool), **RateLimiter**, **TimeLimiter**; decorator order
and why it matters; Spring Boot integration (`resilience4j-spring-boot3`,
annotations, `application.yml` config instances) and Spring Cloud
CircuitBreaker abstraction; fallbacks that do not lie; metrics via Micrometer
and Actuator endpoints; testing resilience with WireMock fault injection.

### Lessons
- [ ] **J8.2.L1 Concepts.** Resilience4j docs (resilience4j.readme.io) → "Getting Started", "CircuitBreaker" (state machine, sliding window, configuration), "Retry", "Bulkhead", "RateLimiter", "TimeLimiter".
- [ ] **J8.2.L2 Spring Boot integration.** Resilience4j docs → "Getting Started" → "Spring Boot 3" (annotations, configuration properties, aspect order), "Micrometer" add-on.
- [ ] **J8.2.L3 Spring Cloud CircuitBreaker.** Spring Cloud Circuit Breaker Reference → "Configuring Resilience4J Circuit Breakers".
- [ ] **J8.2.L4 Background.** Re-read your B22 notes (Release It! stability patterns; AWS Builders' Library "Timeouts, retries, and backoff with jitter"). Baeldung: "Guide to Resilience4j With Spring Boot".

### Exercises (`java/J08-02-resilience4j/`)
- [ ] **Ex J8.2.1 Circuit breaker states.** Wrap a Feign/RestClient call to a WireMock stub with a circuit breaker (window 10, failure rate 50%, wait 5 s, 3 half-open calls). *Acceptance:* a test drives CLOSED → OPEN → HALF_OPEN → CLOSED and asserts state via the `CircuitBreakerRegistry`.
- [ ] **Ex J8.2.2 Retry that respects idempotency.** Retry GETs 3 times with exponential backoff + jitter on `IOException`/5xx; do NOT retry a non-idempotent POST unless it carries an Idempotency-Key. *Acceptance:* tests prove both rules.
- [ ] **Ex J8.2.3 Decorator order.** Combine TimeLimiter, CircuitBreaker, Retry and Bulkhead on one call; change the order and observe the difference. *Acceptance:* `NOTES.md` documents the order you chose (outer → inner) and why.
- [ ] **Ex J8.2.4 Bulkhead under a slow dependency.** Make one downstream stub respond in 5 s; without a bulkhead, show it exhausting the Tomcat/virtual-thread capacity for unrelated endpoints; add a semaphore bulkhead. *Acceptance:* unrelated endpoints stay fast; numbers in `NOTES.md`.
- [ ] **Ex J8.2.5 Observe it.** Expose Resilience4j metrics to Prometheus and add circuit-breaker state and retry counts to your Grafana dashboard. *Acceptance:* screenshot showing a breaker opening during a fault.

### Must be able to do / explain
- [ ] Configure and tune each Resilience4j module and explain its parameters.
- [ ] Explain the circuit-breaker state machine and slow-call detection.
- [ ] Explain why retries need idempotency and jitter, and why retries + no timeout is a bug.
- [ ] Choose a decorator order and defend it.

**Estimated hours:** ~4h

### Self-check interview questions
1. Walk through the circuit breaker states and transitions.
2. Why add jitter to backoff?
3. Semaphore vs thread-pool bulkhead?
4. What is a good and a bad fallback for "price service is down"?
5. Retry inside or outside the circuit breaker?
6. What happens if you retry every layer of a 4-service call chain 3 times?

---

**Answers**
1. CLOSED counts outcomes in a sliding window; if failure or slow-call rate exceeds the threshold it goes OPEN and rejects calls; after the wait duration it goes HALF_OPEN and allows a few trial calls — success closes it, failure reopens it.
2. To stop synchronized clients retrying at the same moments and hammering a recovering service (thundering herd).
3. Semaphore limits concurrent calls on the caller's thread (cheap, works with virtual threads); thread-pool isolates calls on a separate pool with a queue (stronger isolation, extra threads, needed for timeouts on blocking code in older setups).
4. Good: serve a clearly marked cached price or "price unavailable, try later". Bad: return 0 or a guessed price that looks real.
5. Commonly Retry outside CircuitBreaker so each retry is counted by the breaker and stops once it opens; the important part is to decide deliberately and keep total time bounded by a TimeLimiter.
6. Retry amplification: up to 3⁴ = 81 calls to the deepest service per user request, turning a small failure into an outage; retry at one layer only and use budgets.

---

## Module J8.3 — Inter-Service Communication, Sagas & Outbox in Spring (~7h)

**Topics:** synchronous vs asynchronous communication and coupling; REST
with `RestClient` (timeouts, error handling, `@HttpExchange`), API contracts
and versioning; **gRPC in Java** (proto3 recap from B32, `protobuf-maven-plugin`
/ Gradle protobuf plugin, grpc-java stubs, deadlines, status codes,
interceptors; Spring gRPC project for Boot integration); messaging (AMQP/Kafka
from J7.9/J7.10) and event design (event-carried state vs notification,
schemas, versioning); **transactional outbox** in Spring (outbox table written
in the same `@Transactional` method, relay with `FOR UPDATE SKIP LOCKED`
polling or Debezium CDC as a concept), idempotent consumers; **sagas**
(choreography vs orchestration, compensations, saga state, timeouts) in Spring;
distributed tracing across async hops (J7.12).

### Lessons
- [ ] **J8.3.L1 REST clients.** Spring Framework Reference → "REST Clients" → "RestClient" (creating, retrieve, error handling, timeouts via `ClientHttpRequestFactory`) and "HTTP Interface".
- [ ] **J8.3.L2 gRPC in Java.** grpc.io → "Java" → "Quick start" and "Basics tutorial" (defining the service, generating code, creating the server and the client, streaming RPCs); grpc.io "Deadlines", "Status codes". Spring gRPC reference (docs.spring.io/spring-grpc) → "Getting Started" and "gRPC Server"/"gRPC Clients".
- [ ] **J8.3.L3 Outbox and sagas.** microservices.io "Pattern: Transactional outbox", "Pattern: Saga", "Pattern: Idempotent Consumer"; re-read your B25 notes. Chris Richardson, "Microservices Patterns" — Chapter 4 "Managing transactions with sagas" (if available).
- [ ] **J8.3.L4 Spring implementation details.** Spring Framework Reference → "Transaction Management" → "Transaction-bound Events" (`@TransactionalEventListener` and why it is NOT an outbox); Spring Modulith Reference → "Working with Application Events" → "Event Publication Registry" (a ready-made outbox-like mechanism — read to compare, build your own first).
- [ ] **J8.3.L5 Debezium (concept).** debezium.io docs → "Outbox Event Router" (read only; understand CDC-based relay vs polling).

### Exercises (`java/J08-03-communication/`)
- [ ] **Ex J8.3.1 gRPC service.** Define `RatingService.RateQuote(QuoteRequest) returns (QuoteResult)` in proto3, generate stubs with the build plugin, implement server and client in Boot with a 300 ms deadline. *Acceptance:* a test shows `DEADLINE_EXCEEDED` when the server sleeps 500 ms; a status-code → exception mapping exists on the client.
- [ ] **Ex J8.3.2 REST vs gRPC measurement.** Expose the same rating logic over REST (JSON) and gRPC; call each 10 000 times. *Acceptance:* latency and payload size compared in `NOTES.md` with a sentence on when the difference matters.
- [ ] **Ex J8.3.3 Outbox by hand.** In one `@Transactional` method, insert a `policy` row and an `outbox` row; a `@Scheduled` relay polls with `SELECT … FOR UPDATE SKIP LOCKED LIMIT 100`, publishes to Kafka, and marks rows sent. *Acceptance:* killing the app between commit and publish loses no event; running 2 relay instances never publishes a row twice concurrently (duplicates after crashes are tolerated by consumers).
- [ ] **Ex J8.3.4 `@TransactionalEventListener` trap.** Publish the Kafka message from an `AFTER_COMMIT` listener instead of the outbox and kill the app right after commit. *Acceptance:* `NOTES.md` shows the lost event and explains why the outbox fixes it.
- [ ] **Ex J8.3.5 Choreographed saga.** policy-service emits `PolicyCancelled`; billing-service computes a pro-rata refund and emits `RefundIssued` or `RefundFailed`; policy-service marks the cancellation complete or compensates (re-activates and flags for manual review). *Acceptance:* tests for the happy path, the failure path and a duplicate event; a sequence diagram in `NOTES.md`.
- [ ] **Ex J8.3.6 Orchestrated variant (design only).** Write a one-page design of the same flow as an orchestrated saga with an explicit state table. *Acceptance:* `NOTES.md` compares the two on coupling, visibility and failure handling.

### Must be able to do / explain
- [ ] Choose sync REST, gRPC or messaging for a given interaction and defend it.
- [ ] Build a gRPC service and client in Java with deadlines and error mapping.
- [ ] Implement a transactional outbox with a safe relay and idempotent consumers.
- [ ] Explain why `@TransactionalEventListener` is not a replacement for an outbox.
- [ ] Design choreographed and orchestrated sagas with compensations.

**Estimated hours:** ~7h

### Self-check interview questions
1. Why not use 2PC/XA between services?
2. Explain the dual-write problem and how the outbox solves it.
3. Why does the relay use `SKIP LOCKED`?
4. Choreography vs orchestration — when would you pick each?
5. What is a compensating action and why is it not a rollback?
6. When is gRPC a better choice than REST between services?
7. How does an idempotent consumer deal with outbox duplicates?

---

**Answers**
1. It couples availability of all participants, needs XA support in every resource (brokers rarely fit), holds locks across the network, and has blocking failure modes when the coordinator dies.
2. Writing to the DB and publishing to a broker are two separate systems; either can succeed alone. The outbox writes the event into the same DB transaction as the state change, and a separate relay publishes it later — at-least-once.
3. So several relay instances can poll concurrently without blocking on or double-processing the same rows.
4. Choreography for short flows with few participants and loose coupling; orchestration when the flow is long, has many steps/branches, or needs a clear place to see and control saga state.
5. A new business action that semantically undoes an earlier committed step (refund, re-activate); the original step already happened and may have been observed by others.
6. Internal, high-throughput or latency-sensitive calls with strict contracts, streaming needs, or polyglot clients generated from one proto; REST stays better for public/browser-facing APIs.
7. It stores processed event ids (or uses upserts keyed by business id) so a re-delivered event causes no second side effect.

---

## Module J8.4 — Containerizing Spring Boot (~4h)

**Topics:** fat JAR structure and why naive `COPY app.jar` images rebuild
slowly; **layered JARs** (`layertools`/`jarmode=tools` extract, layer order:
dependencies → spring-boot-loader → snapshot-dependencies → application);
writing an efficient multi-stage Dockerfile with a JRE base image, non-root
user and JVM container flags (`-XX:MaxRAMPercentage`); **Cloud Native
Buildpacks** (`spring-boot:build-image` / `bootBuildImage`, builder choice,
image configuration); **Jib** (daemonless builds, reproducibility); CDS/AOT
cache basics for faster startup; **Docker Compose support in Spring Boot**
(`spring-boot-docker-compose`) and Testcontainers at development time;
image scanning recap (Trivy from B23).

### Lessons
- [ ] **J8.4.L1 Efficient container images.** Spring Boot Reference → "Packaging Spring Boot Applications" → "Container Images" → "Efficient Container Images" (layering Docker images, Dockerfiles), and "Class Data Sharing".
- [ ] **J8.4.L2 Buildpacks.** Spring Boot Maven Plugin Reference → "Packaging OCI Images" (image customization, builder, publishing); Spring Boot Gradle Plugin Reference → "Packaging OCI Images" (for Gradle users). buildpacks.io docs "Concepts" (builder, buildpack, lifecycle).
- [ ] **J8.4.L3 Jib.** Jib README (github.com/GoogleContainerTools/jib) and the Jib Maven/Gradle plugin READMEs (quickstart, configuration, `jib:dockerBuild` vs `jib:build`).
- [ ] **J8.4.L4 Compose in development.** Spring Boot Reference → "Docker Compose Support" and "Testcontainers" → "Using Testcontainers at Development Time". Baeldung: "Reusing Docker Layers with Spring Boot", "Creating Docker Images with Spring Boot".

### Exercises (`java/J08-04-containers/`)
- [ ] **Ex J8.4.1 Naive vs layered.** Build the JM1 (or JP3) app image with a naive Dockerfile, then with a layered multi-stage Dockerfile (JRE base, non-root). *Acceptance:* `NOTES.md` records image size and rebuild time after a one-line code change for both.
- [ ] **Ex J8.4.2 Buildpacks.** Build the same app with `spring-boot:build-image`/`bootBuildImage`. *Acceptance:* compare size, startup time, user, and SBOM availability with your Dockerfile image.
- [ ] **Ex J8.4.3 Jib.** Build and push to a local registry with Jib without a Docker daemon. *Acceptance:* two builds from the same commit produce the same image digest; explain why.
- [ ] **Ex J8.4.4 Memory in containers.** Run the image with `--memory=512m` and different `MaxRAMPercentage` values under load. *Acceptance:* `NOTES.md` shows heap size chosen by the JVM and one OOM-kill you provoked on purpose.
- [ ] **Ex J8.4.5 Compose dev loop.** Add `compose.yaml` with Postgres/Redis and use Spring Boot Docker Compose support so `./mvnw spring-boot:run` starts dependencies automatically. *Acceptance:* no manual connection properties needed in dev.

### Must be able to do / explain
- [ ] Build small, layered, non-root images for Boot apps three ways and compare them.
- [ ] Configure the JVM for container memory limits.
- [ ] Use Docker Compose support and Testcontainers for local development.

**Estimated hours:** ~4h

### Self-check interview questions
1. Why do layered JARs speed up image builds?
2. Buildpacks vs Dockerfile vs Jib — pros and cons?
3. How does the JVM decide heap size inside a container?
4. Why run as non-root?
5. What does CDS give you and at what cost?

---

**Answers**
1. Dependencies change rarely and application classes often; separate layers let Docker cache the big dependency layer and rebuild only the small application layer.
2. Buildpacks: no Dockerfile, good defaults, SBOM, less control. Dockerfile: full control, you own security and caching. Jib: fast, daemonless, reproducible, Java-only, less control over OS layer.
3. Modern JVMs are container-aware and size the default heap as a percentage of the container memory limit (tunable with `MaxRAMPercentage`); non-heap memory must fit in the rest.
4. A compromised process as root in a container has far more ways to escape or damage the host and mounted volumes; least privilege.
5. Faster startup and lower memory by reusing a pre-computed class archive; costs an extra training run in the build and ties the archive to the exact JDK and classpath.

---

## Module J8.5 — CI/CD with GitHub Actions for Java (~3h)

**Topics:** workflow recap (Track 2 B9/B23); `actions/setup-java`
(distribution, version, **Maven/Gradle dependency caching**), Gradle's
`gradle/actions/setup-gradle`; running `verify`/`check` with Testcontainers in
CI (Docker available on `ubuntu-latest`); test reports and coverage (JaCoCo)
as artifacts; static analysis gates (Checkstyle, SpotBugs from J4.4);
building and pushing images to GHCR with Buildpacks or Jib; matrix builds
(JDK versions); caching pitfalls; dependency updates (Dependabot); multi-module
builds and running only affected modules (mention).

### Lessons
- [ ] **J8.5.L1 Java in Actions.** GitHub Docs → "Building and testing Java with Maven" and "Building and testing Java with Gradle"; `actions/setup-java` README → "Caching packages dependencies".
- [ ] **J8.5.L2 Publishing images.** GitHub Docs → "Publishing Docker images" and "Working with the Container registry"; re-read your B9/B23 notes on least-privilege `permissions:`.
- [ ] **J8.5.L3 Quality gates.** JaCoCo Maven plugin docs (`report`, `check` goals); Testcontainers docs → "Continuous Integration" → "GitHub Actions".

### Exercises (`java/J08-05-ci/`)
- [ ] **Ex J8.5.1 Build pipeline.** For the JM1 repo: checkout → setup-java with cache → `verify` (unit + Testcontainers) → upload test report and JaCoCo coverage. *Acceptance:* a second run is measurably faster due to caching (record both times).
- [ ] **Ex J8.5.2 Gates.** Fail the build on Checkstyle/SpotBugs violations and coverage below 70% on the domain module. *Acceptance:* a PR that breaks each rule shows a red check with a readable reason.
- [ ] **Ex J8.5.3 Image publish.** On `main`, build with Buildpacks or Jib and push to GHCR tagged with the commit SHA and `latest`. *Acceptance:* PR builds do not push; permissions are minimal.
- [ ] **Ex J8.5.4 Matrix.** Run tests on JDK 21 and 25. *Acceptance:* both pass, or you document the incompatibility you found.

### Must be able to do / explain
- [ ] Write a cached Maven/Gradle workflow with Testcontainers tests.
- [ ] Add quality gates and publish reports.
- [ ] Push images to GHCR securely from CI.

**Estimated hours:** ~3h

### Self-check interview questions
1. How do you cache Maven/Gradle dependencies in GitHub Actions and what invalidates the cache?
2. Why can Testcontainers run on GitHub-hosted runners?
3. Why push images only from `main`?
4. What does a coverage gate protect against, and what does it not?
5. How would you speed up CI for a 12-module build?

---

**Answers**
1. `setup-java` with `cache: maven|gradle` (or `setup-gradle`) caches the local repository keyed by a hash of the build files; changing `pom.xml`/`*.gradle*`/lockfiles invalidates it.
2. Ubuntu runners have a Docker daemon available, which Testcontainers uses to start containers.
3. Only reviewed, merged code should become deployable artifacts; PR images from forks would also need secrets that forks must not get.
4. It prevents large untested areas from sneaking in; it does not prove tests assert anything meaningful.
5. Build caching, parallel jobs per module, running only affected modules, splitting slow integration tests, and reusing Testcontainers where safe.

---

## Project JMP1 — PolisHub Microservices · Middle+ (~90h)

**Goal:** build a non-life insurance platform as a small set of Spring Boot
microservices on PostgreSQL, behind Spring Cloud Gateway, communicating
through REST, OpenFeign and **Kafka events published via a transactional
outbox**, with a **choreographed saga** for policy cancellation and refund.
The domain comes from PolisHub: quotes rated from effective-dated tariffs ×
factors, policies with **versions** (endorsements create a new version), and
claims registered through **FNOL** and judged against the policy version in
force on the loss date. The point is to experience real microservice problems
— consistency without 2PC, duplicate events, partial failures, tracing — and
defend each decision.

### Services
| Service | Owns | Talks to |
|---|---|---|
| `gateway` | Routing, JWT validation, rate limits, correlation id | all services |
| `config-server` | Central configuration (Git backend) | — |
| `quote-service` | Products, tariff versions, factors, quotes (`quote_factors` audit trail) | — |
| `policy-service` | Policies, `policy_versions` (valid_from/valid_to), endorsements, cancellations | quote-service (Feign, bind a quote), Kafka |
| `claims-service` | Claims, status machine, FNOL, reserves (append-only) | policy-service (Feign/gRPC: version in force on a date), Kafka |
| `billing-service` | Premium instalments, refunds | Kafka |
| `notification-service` | Emails/SMS (stub) | Kafka (consumer only) |

### Features
- [ ] Quote: `POST /quotes` rates a motor policy from tariff version by **effective date** (not today) × factors (vehicle age, engine power, driver age, bonus-malus); every applied factor stored in `quote_factors`; quote expires after 30 days.
- [ ] Bind: `POST /policies` from a valid quote (Feign call to quote-service with timeouts, error decoder, circuit breaker) → policy + version 1; emits `PolicyIssued` via outbox.
- [ ] Endorse: `POST /policies/{id}/endorsements` creates a new version from an effective date; versions never overlap and never leave gaps (DB constraint + tests); pro-rata premium delta emitted as `PolicyEndorsed`.
- [ ] Cancel (**saga**): `POST /policies/{id}/cancellations` → `202 Accepted` + status resource; policy-service emits `PolicyCancellationRequested`; billing-service computes the pro-rata refund and emits `RefundIssued` or `RefundFailed`; policy-service completes the cancellation or compensates (reinstate + flag for review); notification-service informs the customer.
- [ ] FNOL: `POST /claims` with a required `Idempotency-Key` (retries from a flaky mobile client never create two claims); claims-service asks policy-service for the version in force on the **loss date** and stores `policy_version_id`; rejected if no cover on that date.
- [ ] Claim status machine (REGISTERED → ASSESSED → APPROVED/REJECTED → PAID) with invalid transitions returning 409 ProblemDetail; reserve changes append-only.
- [ ] Transactional outbox in every producing service; relay with `FOR UPDATE SKIP LOCKED`; all consumers idempotent (processed-event table).
- [ ] Kafka error handling: DLT per consumer, non-retryable validation errors, replay tool for DLT records.
- [ ] Resilience4j on all synchronous calls (timeouts, circuit breaker, retries only for idempotent calls, bulkhead for claims → policy lookups).
- [ ] Gateway: routes, JWT validation (OAuth2 Resource Server; roles CUSTOMER, AGENT, CLAIMS_HANDLER, ADMIN), Redis rate limit on FNOL, correlation id header.
- [ ] Config Server with per-service and per-profile config; secrets never in Git plaintext.
- [ ] Observability: Actuator probes, Prometheus metrics (RED per service, outbox lag, consumer lag, DLT count), one distributed trace from gateway → policy → Kafka → billing → policy visible in Jaeger/Tempo; structured JSON logs with trace ids.
- [ ] Contract/API docs with springdoc per service; gRPC variant of the "version in force" lookup (optional within the project: implement both and compare).
- [ ] Docker Compose for the whole system (Kafka, Postgres per service, Redis, Config Server, observability stack); images built with Buildpacks or Jib; CI per service with Testcontainers.

### Tech stack
| Tool / library | Taught in |
|---|---|
| Java 25, records, sealed types for events, Streams | J1, J2 |
| Concurrency basics, virtual threads (optional) | J3 |
| Maven/Gradle multi-module, JUnit 5, Mockito, AssertJ, Testcontainers (Postgres, Kafka, Redis) | J4.1–J4.3 |
| SLF4J + Logback | J4.4 |
| JDBC/JPA/Hibernate, `@Version`, Flyway | J5.1–J5.8 |
| Spring core, AOP, `@Transactional` | J6.1–J6.4 |
| Spring Boot, MVC/REST, validation, ProblemDetail, springdoc | J7.1–J7.2 |
| Spring Data JPA, Boot testing | J7.3–J7.4 |
| Spring transactions, JdbcTemplate/JdbcClient (outbox relay) | J7.5 |
| Spring Security, OAuth2 Resource Server, JWT | J7.6 |
| Spring Cache + Redis (tariff cache keyed by effective date) | J7.7 |
| `@Scheduled` + ShedLock (relay, optional) | J7.8 |
| Spring for Apache Kafka, DLT, retry topics | J7.10 |
| Actuator, Micrometer, Tracing + OpenTelemetry, structured logging | J7.12 |
| Spring Cloud Config, Gateway, OpenFeign | J8.1 |
| Resilience4j | J8.2 |
| RestClient, gRPC in Java, outbox, sagas | J8.3 |
| Buildpacks/Jib, Docker Compose support | J8.4 |
| GitHub Actions for Java | J8.5 |
| Kafka, outbox/saga, resilience, monitoring concepts | Track 2 B16, B22, B24, B25 |
| PostgreSQL (constraints for non-overlapping versions, `SKIP LOCKED`) | Track 1C 2.5, 2.8 |

### Required knowledge
J1–J7.12 (J7.9 AMQP and J7.11 WebFlux not required), J8.1–J8.5; Track 2 concepts B15–B16, B22, B24–B25 (as theory); Track 1C Part 2. JM1 TeamBoard recommended first.

### Milestones
**M1 — Skeleton & platform** (`v0.1-platform`)
- [ ] Multi-module (or multi-repo) layout, shared BOM, Config Server, Gateway with two dummy routes, Compose with Postgres per service and Kafka.
- [ ] CI pipeline per service (J8.5) with Testcontainers.

**M2 — Quote & policy core** (`v0.2-quote-policy`)
- [ ] quote-service rating with effective-dated tariffs and `quote_factors`; Redis tariff cache keyed by effective date.
- [ ] policy-service bind via Feign (timeouts, error decoder, circuit breaker); policy versions with non-overlap constraint; endorsement endpoint.
- [ ] Tests: tariff chosen by effective date; version gaps/overlaps rejected.

**M3 — Outbox & events** (`v0.3-events`)
- [ ] Outbox tables and relay in policy-service and billing-service; `PolicyIssued`, `PolicyEndorsed` events.
- [ ] billing-service instalment plan from `PolicyIssued`; notification-service consumer.
- [ ] Idempotent consumers; DLT and replay tool; test: kill relay mid-batch → no lost events.

**M4 — Cancellation saga** (`v0.4-saga`)
- [ ] 202 + status resource; choreographed saga with refund and compensation.
- [ ] Tests: happy path, `RefundFailed` compensation, duplicate and out-of-order events.
- [ ] Sequence diagram and failure-mode table in `docs/saga.md`.

**M5 — Claims & FNOL** (`v0.5-claims`)
- [ ] FNOL with Idempotency-Key (DB-backed, request hash check); loss-date version lookup (Feign, then gRPC variant) with bulkhead.
- [ ] Claim status machine; append-only reserves; `ClaimRegistered` events.

**M6 — Security, resilience, observability** (`v0.6-hardening`)
- [ ] JWT at gateway + per-service validation; role rules per endpoint; rate limit on FNOL.
- [ ] Resilience4j everywhere sync; fault-injection tests with WireMock.
- [ ] Dashboards (RED, outbox lag, consumer lag, DLT count) and one end-to-end trace screenshot.

**M7 — Wrap** (`v1.0-polishub-ms`)
- [ ] Buildpacks/Jib images, full Compose up with one command.
- [ ] `docs/architecture.md` (C4 container diagram, why each service boundary, why no 2PC) and `docs/decisions/` ADRs (Kafka vs RabbitMQ, choreography vs orchestration, Feign vs gRPC).

### Definition of done
- [ ] `docker compose up` starts the whole system; a scripted scenario (quote → bind → endorse → FNOL → cancel) passes end to end.
- [ ] No event is lost when any service or relay is killed at any point in the scenario (tested).
- [ ] Every consumer is idempotent (tested with duplicated events).
- [ ] Every synchronous call has a timeout and a circuit breaker; retries only on idempotent calls.
- [ ] One distributed trace covers gateway → policy → Kafka → billing → policy.
- [ ] Each service has CI with Testcontainers tests green.

**Estimated hours:** ~90h (M1 10h · M2 16h · M3 16h · M4 14h · M5 14h · M6 12h · M7 8h)

### Interview questions about this project
1. Why did you split PolisHub into these services, and what would you merge back?
2. How do you keep policy and billing consistent during a cancellation without 2PC?
3. How does FNOL stay idempotent when the mobile client retries?
4. What happens if Kafka is down for 10 minutes?
5. How do you find where a slow cancellation request spends its time?

---

**Answers**
1. Boundaries follow ownership and change rate (rating, policy lifecycle, claims, billing); explain what you would merge (e.g. notification into billing, or everything into a modular monolith for a small team) — the honest answer names the costs you paid.
2. A choreographed saga: each service commits locally and publishes events via its outbox; failures trigger compensations (reinstate the policy) instead of rollbacks; consumers are idempotent.
3. The client sends an Idempotency-Key; the service stores key + request hash + response in the same transaction as the claim; a retry returns the stored response, a different body with the same key returns 422.
4. Local transactions keep succeeding and events accumulate in outbox tables; the relay retries and drains the backlog when Kafka returns; outbox-lag alerts fire; synchronous APIs keep working.
5. Open the trace for that request (trace id from the gateway log/response header) and inspect spans across services and the Kafka hop; correlate with RED metrics and consumer lag.

---

## Module J8.6 — Performance Tuning & Load Testing (~6h)

**Topics:** performance method (define SLOs, measure, change one thing,
measure again); load models (open vs closed workload, ramp-up, soak, spike);
**Gatling** (simulations in Java DSL, feeders, checks, injection profiles,
assertions on p95/p99, HTML reports) — k6 as an alternative; coordinated
omission; profiling a Boot app under load with **JFR** (J3.6 recap) and
**async-profiler** flame graphs; **HikariCP sizing** (why smaller pools are
often faster, `maximumPoolSize`, connection timeout, leak detection) and
thread-pool sizing (Tomcat threads vs virtual threads); **virtual threads in
Spring Boot** (`spring.threads.virtual.enabled=true`), what changes (Tomcat,
`@Async`, scheduling) and **pinning pitfalls** (`synchronized` around blocking
I/O on older JDKs, native frames; `jdk.tracePinnedThreads`/JFR events), and
why virtual threads do not fix a saturated DB pool; GC choice recap (G1 vs ZGC
for latency), heap sizing, allocation pressure; caching and query tuning as
the usual real fixes.

### Lessons
- [ ] **J8.6.L1 Gatling.** Gatling docs → "Tutorials" → "Introduction to scripting" (Java DSL), "Reference" → "Scenario", "Injection" (open vs closed models), "Checks", "Assertions", "Feeders"; Gatling Maven/Gradle plugin docs.
- [ ] **J8.6.L2 Measuring right.** Gil Tene talk "How NOT to Measure Latency" (coordinated omission); k6 docs "Open and closed models" (concept page — clear even if you use Gatling).
- [ ] **J8.6.L3 Profiling.** async-profiler README (github.com/async-profiler/async-profiler): "Basic usage", "Profiling modes" (cpu, alloc, lock, wall), "Flame graph visualization"; JDK Mission Control docs for JFR recordings (recap J3.6).
- [ ] **J8.6.L4 Pools.** HikariCP wiki "About Pool Sizing"; HikariCP README "Configuration (knobs, baby!)".
- [ ] **J8.6.L5 Virtual threads in Boot.** Spring Boot Reference → "Virtual Threads" (and the notes in "Task Execution and Scheduling"); JEP 444 "Virtual Threads" → sections on pinning and "Do not pool virtual threads"; JEP 491 "Synchronize Virtual Threads without Pinning" (what changed in JDK 24+).
- [ ] **J8.6.L6 GC recap.** Oracle "HotSpot Virtual Machine Garbage Collection Tuning Guide" → "Garbage-First (G1) Garbage Collector" and "The Z Garbage Collector" (tuning basics). Baeldung: "Gatling vs JMeter vs The Grinder", "Working with Virtual Threads in Spring".

### Exercises (`java/J08-06-performance/`)
- [ ] **Ex J8.6.1 First simulation.** Write a Gatling simulation for JM1 TeamBoard: login feeder, list issues, create issue; open model ramp 10 → 200 users/s over 2 minutes; assertions p95 < 200 ms and errors < 1%. *Acceptance:* HTML report committed (or screenshot) and a sentence on whether the assertions held.
- [ ] **Ex J8.6.2 Find the bottleneck.** Under the load from Ex 1, record JFR and an async-profiler CPU + wall flame graph. *Acceptance:* `NOTES.md` names the top 3 hotspots with evidence and one fix you applied with before/after numbers.
- [ ] **Ex J8.6.3 Pool size experiment.** Run the same load with Hikari `maximumPoolSize` = 5, 10, 20, 50. *Acceptance:* a table of throughput and p99 per size and your explanation of the curve.
- [ ] **Ex J8.6.4 Virtual threads on/off.** Add an endpoint that calls a 200 ms downstream stub; compare platform threads (Tomcat default) vs virtual threads at 1 000 concurrent users. *Acceptance:* numbers in `NOTES.md`; then add a DB call and show that the Hikari pool becomes the limit regardless.
- [ ] **Ex J8.6.5 Pinning.** Reproduce pinning with `synchronized` around blocking I/O on JDK 21 and observe it with JFR `jdk.VirtualThreadPinned`; re-run on JDK 25. *Acceptance:* `NOTES.md` explains the difference and which code patterns you still avoid.

### Must be able to do / explain
- [ ] Write Gatling simulations with realistic injection profiles and SLO assertions.
- [ ] Explain open vs closed workload models and coordinated omission.
- [ ] Profile a Spring Boot app under load and turn a flame graph into a fix.
- [ ] Size HikariCP and thread pools from measurements, not guesses.
- [ ] Explain what virtual threads improve, what they do not, and pinning.

**Estimated hours:** ~6h

### Self-check interview questions
1. Why is p99 more important than the average?
2. Open vs closed workload — which one hides overload, and why?
3. Why can a bigger connection pool make latency worse?
4. You enabled virtual threads and throughput did not change. What might be the reason?
5. What is pinning and when does it still happen?
6. How do you read a flame graph?
7. When would you switch from G1 to ZGC?

---

**Answers**
1. Users feel the tail; with many calls per page, most users hit at least one slow request, and averages hide bimodal or long-tail latency.
2. Closed models (fixed users waiting for responses) slow their request rate when the system slows, hiding overload; open models keep arrival rate constant like real traffic and expose queueing.
3. The database has limited CPU/IO; more concurrent connections add contention, context switching and lock waits — past a point throughput drops and latency grows.
4. The bottleneck is elsewhere: DB pool size, CPU-bound work, a synchronized hotspot, or a downstream limit; virtual threads only remove the cost of waiting threads.
5. A virtual thread cannot unmount from its carrier while blocked — historically inside `synchronized` blocks (fixed in JDK 24+ by JEP 491) and still in native frames/foreign calls; it reduces scalability to the carrier count.
6. Width is the share of samples (time) in a frame and its children; stacks grow upward; look for wide plateaus at the top — that is where time is actually spent.
7. When GC pause times violate latency SLOs with large heaps; ZGC keeps pauses sub-millisecond at the cost of some throughput and memory overhead.

---

## Project JMP2 — TicketRush · Middle+ (~60h)

**Goal:** build a flash-sale ticket reservation service that survives a
spike of thousands of concurrent buyers for a few hundred seats **without
overselling**, using PostgreSQL, Redis and virtual threads — and prove it
with load tests. The core of the project is comparing three oversell-
prevention strategies under real concurrency, measuring them with Gatling,
and writing a tuning report.

### Features
- [ ] Events and seats: `events`, `seats` (section/row/number, price tier), `holds`, `orders`, `order_items`, `idempotency_keys`; Flyway migrations.
- [ ] Browse: `GET /events/{id}/availability` cached in Redis (short TTL, stampede protection) — read path must stay fast during the sale.
- [ ] Hold: `POST /events/{id}/holds` for 1–6 specific seats (or "best available"); a hold expires after 5 minutes (TTL); expired holds release seats automatically.
- [ ] Oversell prevention implemented **three ways**, switchable by config: (A) pessimistic `SELECT … FOR UPDATE` on seat rows in a consistent order, (B) optimistic locking with JPA `@Version` + bounded retries, (C) Redis atomic Lua script reserving seats, with Postgres as the source of truth reconciled on purchase.
- [ ] Purchase: `POST /holds/{id}/purchase` with a required `Idempotency-Key`; payment is a stub with random latency and 5% failures; failure releases the hold; the same key returns the same result.
- [ ] Per-user and per-IP rate limiting on hold creation (Redis token bucket), and a max-holds-per-user rule.
- [ ] Virtual threads enabled; downstream payment stub called with `RestClient` + Resilience4j (timeout, circuit breaker).
- [ ] Hold-expiry job with `@Scheduled` + ShedLock (multiple instances) or Redis keyspace notifications — pick one and justify.
- [ ] Observability: RED metrics, custom metrics (holds created/expired, oversell attempts rejected, lock wait time), Hikari pool metrics, one Grafana dashboard.
- [ ] Gatling simulations: (1) spike — 5 000 users arrive in 30 s for 500 seats; (2) soak — 30 minutes of steady traffic; assertions on p95/p99 and zero oversell.
- [ ] Invariant checker: after every run a SQL check proves `sold seats ≤ capacity` and no seat is in two orders.
- [ ] `docs/tuning-report.md`: before/after results for pool size, virtual threads on/off, strategy A/B/C, index changes, with flame graphs.

### Tech stack
| Tool / library | Taught in |
|---|---|
| Java 25, records, Streams | J1, J2 |
| Concurrency, `ExecutorService`, virtual threads, JFR | J3.1–J3.6 |
| Maven/Gradle, JUnit 5, AssertJ, Testcontainers (Postgres, Redis) | J4.1–J4.3 |
| JDBC, HikariCP, JPA/Hibernate, `@Version`, pessimistic locks, Flyway | J5.1–J5.8 |
| Spring core, `@Transactional` pitfalls | J6.1–J6.4 |
| Spring Boot, MVC, validation, ProblemDetail | J7.1–J7.2 |
| Spring Data JPA, Boot testing | J7.3–J7.4 |
| Transactions (propagation, isolation), JdbcClient | J7.5 |
| Spring Security (JWT for buyers) | J7.6 |
| Spring Cache + Redis, Lua via `RedisTemplate` | J7.7 |
| `@Scheduled` + ShedLock | J7.8 |
| Actuator, Micrometer, Prometheus, Grafana | J7.12 |
| Resilience4j | J8.2 |
| RestClient | J8.3 |
| Buildpacks/Jib, Docker Compose | J8.4 |
| GitHub Actions for Java | J8.5 |
| Gatling, async-profiler, Hikari sizing, virtual threads in Boot | J8.6 |
| Redis token bucket / Lua concepts, idempotency keys | Track 2 B12, B34 |
| PostgreSQL locking, isolation, indexes | Track 1C 2.5, 2.7, 2.8 |

### Required knowledge
J1–J8.6 (J7.9–J7.11 and J8.1 not required); Track 1C Part 2 (2.5, 2.7, 2.8); Track 2 B12 and B34 as concepts.

### Milestones
**M1 — Domain and baseline** (`v0.1-baseline`)
- [ ] Schema, seat map seed (500 seats), availability endpoint, hold and purchase with **no** concurrency protection.
- [ ] A concurrency test (200 parallel holds on the same seats with an `ExecutorService`) that demonstrates overselling — keep it as a regression test.

**M2 — Strategy A: pessimistic** (`v0.2-pessimistic`)
- [ ] `FOR UPDATE` in a deterministic seat order; lock timeout; deadlock test.
- [ ] Concurrency test proves zero oversell.

**M3 — Strategy B and C** (`v0.3-optimistic-redis`)
- [ ] `@Version` with bounded retries and backoff.
- [ ] Redis Lua reservation + reconciliation with Postgres on purchase and on expiry.
- [ ] Same concurrency test suite passes for all three strategies.

**M4 — Purchase, idempotency, limits** (`v0.4-purchase`)
- [ ] Idempotency-Key storage with request hash; payment stub behind Resilience4j.
- [ ] Rate limiting and max-holds rule; hold-expiry job with ShedLock across 2 instances.

**M5 — Load, profile, tune** (`v1.0-ticketrush`)
- [ ] Gatling spike + soak simulations with assertions; invariant checker after each run.
- [ ] Profiling with JFR/async-profiler; at least 3 measured tuning changes.
- [ ] `docs/tuning-report.md` comparing strategies A/B/C, pool sizes, virtual threads on/off, with a recommendation.

### Definition of done
- [ ] Zero oversell in every test and every load run (invariant checker output committed).
- [ ] Spike simulation meets p95 < 300 ms and p99 < 800 ms for holds (or the report explains precisely why not and what would be needed).
- [ ] Purchases are idempotent under client retries (tested).
- [ ] Hold expiry works with two app instances and never releases a purchased seat.
- [ ] Tuning report contains before/after numbers and flame graphs, not just conclusions.

**Estimated hours:** ~60h (M1 8h · M2 10h · M3 14h · M4 12h · M5 16h)

### Interview questions about this project
1. Compare pessimistic locking, optimistic locking and Redis reservation for seat booking — which won and why?
2. How did you prevent deadlocks with `FOR UPDATE` on multiple seats?
3. Did virtual threads help? Where was the real bottleneck?
4. How do you keep Redis and Postgres consistent in strategy C?
5. How do you prove there is no oversell after a load test?

---

**Answers**
1. Answer with your numbers. Typically pessimistic is simplest and correct but serializes hot seats; optimistic works well at low contention but retries explode at a flash-sale hotspot; Redis is fastest for the hot path but adds a second source of truth that must be reconciled.
2. Always lock seats in the same order (sorted seat ids) in one statement, keep transactions short, and set a lock timeout; tests with overlapping seat sets confirm no deadlocks.
3. Virtual threads removed thread-pool limits for waiting on the payment stub, but throughput was bound by the DB connection pool and hot-row locks; tuning the pool and the locking strategy mattered more.
4. Postgres stays the source of truth: purchases are written in Postgres with a constraint that a seat can be sold once; Redis holds are reconciled on purchase and expiry, and a periodic job repairs drift.
5. Run the invariant SQL after each run (sold ≤ capacity per event, no seat id in two paid orders) and assert on it in CI and in the load-test script.

## Module J8.7 — Kubernetes Deployment of Spring Boot + Oracle VPD (~6h)

**Topics:** running a Boot app as a Kubernetes `Deployment` behind a
`Service` and an `Ingress`; mapping Actuator health groups to **liveness**
and **readiness** probes (and why the database must NOT be in the liveness
group); **graceful shutdown** (`server.shutdown=graceful`,
`spring.lifecycle.timeout-per-shutdown-phase`, `preStop` sleep vs endpoint
removal race); externalized configuration from ConfigMaps and Secrets
(env vars, mounted files, `spring.config.import=configtree:`); resource
requests/limits and **JVM container awareness** (`-XX:MaxRAMPercentage`,
why `-Xmx` equal to the limit gets you OOMKilled, CPU limits and GC/JIT
thread counts); HPA on CPU and on a custom Micrometer metric (concept);
rolling updates, `maxSurge`/`maxUnavailable`, rollback. **Oracle Virtual
Private Database** (row-level security with `DBMS_RLS` policy functions)
and how to carry the end-user identity through a shared connection pool
with `DBMS_SESSION.SET_IDENTIFIER` / `CLIENT_IDENTIFIER` and clear it on
return to the pool.

Required before this module: Track 2 **B30 Kubernetes** (pods, services,
ingress, probes, HPA on kind), J7.12 Actuator/Micrometer, J8.4
containerizing, Track 1C Part 3 (PL/SQL packages).

### Lessons
- [ ] **J8.7.L1 Boot on Kubernetes.** Spring Boot reference → "Deploying Spring Boot Applications" → "Deploying to the Cloud" → "Kubernetes" (incl. "Kubernetes Container Lifecycle"). kubernetes.io → Concepts → Workloads → "Deployments"; Tasks → "Configure Liveness, Readiness and Startup Probes".
- [ ] **J8.7.L2 Probes via Actuator.** Spring Boot reference → "Production-ready Features" → "Endpoints" → "Health" → "Kubernetes Probes" and "Checking External State With Kubernetes Probes"; "Application Availability" (`LivenessState`, `ReadinessState`).
- [ ] **J8.7.L3 Graceful shutdown.** Spring Boot reference → "Web" → "Graceful Shutdown". kubernetes.io → "Pod Lifecycle" → "Termination of Pods" (`preStop`, `terminationGracePeriodSeconds`).
- [ ] **J8.7.L4 Config and secrets.** Spring Boot reference → "Externalized Configuration" → "Using Configuration Trees". kubernetes.io → "ConfigMaps", "Secrets". (Recap Track 2 B31 for why K8s Secrets are only base64 and when to use Vault.)
- [ ] **J8.7.L5 JVM in containers.** Oracle "Java SE Virtual Machine Guide" / `java` command reference → `-XX:MaxRAMPercentage`, `-XX:ActiveProcessorCount`. kubernetes.io → "Resource Management for Pods and Containers". Paketo Java buildpack docs → "Memory Calculator" (how Buildpacks images size the heap).
- [ ] **J8.7.L6 Scaling & rollouts.** kubernetes.io → "Horizontal Pod Autoscaling" and "HorizontalPodAutoscaler Walkthrough"; `kubectl rollout status/undo`.
- [ ] **J8.7.L7 Oracle VPD & identity propagation.** Oracle Database **Security Guide** → "Using Oracle Virtual Private Database to Control Data Access" (policy functions, policy types, `DBMS_RLS.ADD_POLICY`). **PL/SQL Packages and Types Reference** → `DBMS_RLS`, `DBMS_SESSION` (`SET_IDENTIFIER`, `CLEAR_IDENTIFIER`, `SET_CONTEXT`). Oracle JDBC Developer's Guide → "End-to-End Metrics" / `OracleConnection.setClientInfo` (`OCSID.CLIENTID`).

### Exercises (`java/J8.7-k8s/`)
- [ ] **Ex J8.7.1 Deploy a Boot service to kind.** Take the JP3 LoanProduct Catalog image, write Deployment + Service + Ingress manifests, 2 replicas. *Acceptance:* `curl` through the Ingress works; `kubectl get pods` shows both Ready.
- [ ] **Ex J8.7.2 Correct probes.** Configure liveness = `livenessState` only, readiness = `readinessState` + db. Stop the database. *Acceptance:* pods become NotReady (removed from Service endpoints) but are **not** restarted; write in `NOTES.md` why putting the DB in liveness would cause a restart storm.
- [ ] **Ex J8.7.3 Zero-error rollout.** Enable graceful shutdown + a `preStop` sleep. Run a Gatling (J8.6) constant load during `kubectl rollout restart`. *Acceptance:* 0 failed requests in the Gatling report; repeat without `preStop` and record the difference.
- [ ] **Ex J8.7.4 OOMKill on purpose.** Set memory limit 512Mi and `-Xmx512m`; generate load. Then switch to `-XX:MaxRAMPercentage=75`. *Acceptance:* `kubectl describe pod` shows `OOMKilled` in the first run and not in the second; explain non-heap memory (metaspace, thread stacks, direct buffers, code cache) in `NOTES.md`.
- [ ] **Ex J8.7.5 VPD branch scoping.** In Oracle Free create a `loans` table with `branch_id`, an application context, and a VPD policy function that returns `branch_id = SYS_CONTEXT(...)`. From a small Boot app, set the identifier/context per request from the authenticated user and clear it when the connection returns to HikariCP. *Acceptance:* a Testcontainers test proves user A (branch 1) never sees branch-2 rows, even when the same pooled connection is reused by user B right after.

### Must be able to do/explain
- [ ] Difference between liveness, readiness and startup probes, and which Actuator states feed each.
- [ ] The shutdown sequence of a pod and how to avoid dropped requests.
- [ ] How the JVM sizes its heap inside a container and why `limit == Xmx` is wrong.
- [ ] How Spring reads config from ConfigMaps/Secrets and how to reload it (restart vs refresh).
- [ ] What VPD does, where the predicate is added, and why identity must be set **and cleared** per request with a connection pool.

**Estimated hours:** ~6h

### Self-check questions
1. Why should a database outage not fail the liveness probe?
2. What does `server.shutdown=graceful` do, and why is a `preStop` hook still useful?
3. A pod with `limits.memory: 1Gi` and `-Xmx1g` gets OOMKilled. Why?
4. How does an HPA decide the replica count?
5. What is the difference between `maxSurge` and `maxUnavailable`?
6. What is an Oracle VPD policy function and what must it return?
7. Why is `DBMS_SESSION.SET_IDENTIFIER` needed when every request uses the same DB user from a pool?
8. What happens if you forget to clear the identifier before a connection goes back to the pool?

---

**Answers**
1. Liveness answers "is this process broken and must be restarted?". Restarting pods does not fix a database outage; it only causes a restart storm and cold JVMs when the DB returns. The DB belongs in readiness (stop sending traffic), not liveness.
2. It stops accepting new requests and lets in-flight ones finish within a timeout. `preStop` (e.g. a short sleep) gives the Service/Ingress time to remove the pod from endpoints before the app stops listening, closing the race where new requests still arrive.
3. The container limit covers the whole process: heap plus metaspace, thread stacks, code cache, direct buffers, GC structures. With heap = limit, non-heap memory pushes the process over the limit and the kernel kills it.
4. It periodically compares the observed metric (e.g. average CPU utilisation vs requests) to the target and computes `desired = ceil(current × observed / target)`, bounded by min/max replicas and stabilisation windows.
5. `maxSurge`: how many extra pods above the desired count may exist during a rollout. `maxUnavailable`: how many desired pods may be unavailable. Together they trade rollout speed vs spare capacity.
6. A PL/SQL function taking schema and object name and returning a predicate string (e.g. `branch_id = SYS_CONTEXT('app_ctx','branch')`) that Oracle appends to every statement on the protected object.
7. The database sees only the pool's technical user. The identifier/context carries the real end user (and branch) so VPD predicates and audit records can use it.
8. The next request that borrows that connection runs with the previous user's identity: it may see another branch's data and audit rows get the wrong user — a data leak.

---

## Module J8.8 — GraalVM Native Images (~3h)

**Topics:** what a native image is (closed-world assumption, ahead-of-time
compilation with SubstrateVM); Spring **AOT processing** (bean definitions
generated at build time); GraalVM Native Build Tools for Maven/Gradle;
reachability metadata and **runtime hints** (`RuntimeHintsRegistrar`,
`@RegisterReflectionForBinding`) for reflection, resources, proxies and
serialization; testing native (`nativeTest`); building native images with
Buildpacks; **trade-offs**: fast startup and low memory vs longer builds,
no JIT peak optimisations (lower peak throughput without PGO), harder
debugging, library compatibility; when it pays off (scale-to-zero,
serverless, CLIs) and when it does not (long-running high-throughput
services).

### Lessons
- [ ] **J8.8.L1 Native Image concepts.** GraalVM docs → "Native Image" → "Getting Started" and "Native Image Basics" (build time vs run time, closed world).
- [ ] **J8.8.L2 Spring AOT and native.** Spring Boot reference → "GraalVM Native Image Support" → "Introducing GraalVM Native Images", "Developing Your First GraalVM Native Application", "Testing GraalVM Native Images", "Advanced Native Images Topics".
- [ ] **J8.8.L3 Hints.** Spring Framework reference → "Ahead of Time Optimizations" → "Runtime Hints". GraalVM docs → "Reachability Metadata".

### Exercises (`java/J8.8-native/`)
- [ ] **Ex J8.8.1 Native build.** Build the JP3 catalog service as a native image (Buildpacks or native-maven-plugin). *Acceptance:* the native binary starts and serves requests; record startup time and RSS for JVM vs native in `NOTES.md`.
- [ ] **Ex J8.8.2 Break it, then hint it.** Add a class loaded only via reflection (e.g. by name from config). *Acceptance:* the native image fails at runtime; after adding a runtime hint it works; a `nativeTest` covers it.
- [ ] **Ex J8.8.3 Throughput comparison.** Run the same Gatling (J8.6) simulation for 5 minutes against the JVM and the native build. *Acceptance:* a table of p50/p95/p99 and throughput with a short conclusion on where native wins and loses.

### Must be able to do/explain
- [ ] The closed-world assumption and what breaks because of it.
- [ ] What Spring AOT generates at build time.
- [ ] How to register runtime hints and how to test a native image.
- [ ] When native images are the right choice and when they are not.

**Estimated hours:** ~3h

### Self-check questions
1. What is the closed-world assumption?
2. Why is reflection a problem for native images and how does Spring solve most of it?
3. Name two downsides of native images.
4. Why can a JIT-compiled JVM beat a native image on peak throughput?
5. Give a workload where native is a clear win.

---

**Answers**
1. At build time the analysis must see all code that can ever run; anything not reachable then (dynamic class loading, unregistered reflection) does not exist at runtime.
2. Reflection targets are not statically visible, so they are removed unless declared. Spring AOT precomputes bean definitions and emits hints for what it knows; you add hints for your own dynamic access.
3. Long build times and heavy build memory; lower peak throughput without profile-guided optimisation; library incompatibilities; harder debugging/profiling; configuration fixed at build time for some features (e.g. profiles/conditions evaluated at build).
4. The JIT optimises using real runtime profiles (inlining, speculative optimisation, deoptimisation) that an AOT compiler cannot know in advance.
5. Scale-to-zero/serverless functions, short-lived jobs and CLIs, or dense deployments where startup time and memory per instance dominate.

---

## Project JMP3 — CreditLine Core on Kubernetes · Middle+ (~100h)

**Goal:** build a production-grade **loan-servicing core on Oracle** where
PL/SQL packages own the business rules and Spring Boot owns the boundary
(APIs, security, messaging, observability), then run it on Kubernetes and
prove it is correct under concurrency and fast under load. Principle from
the CreditLine spec: *"Oracle owns the rules; Spring owns the boundary."*
Packages never `COMMIT` (the only exception is autonomous-transaction
audit/error logging); the Java transaction decides.

This project reuses and extends JM2 (Reporting) and JM3 (Nightly Batch) on
the same CreditLine schema.

### Features
- [ ] **Application workflow** (`pkg_application`): state machine DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED/REJECTED → DISBURSED; **separation of duties** enforced in the database (creator cannot approve; approver cannot disburse); approval limits per role from `approval_limits`.
- [ ] **Disbursement** (`pkg_disbursement`): full or tranche disbursement; the active repayment schedule is frozen at disbursement (versioned `schedules`, exactly one active per loan).
- [ ] **Payments** (`pkg_payment`): posting with the **waterfall** penalties → fees → overdue interest → current interest → principal; allocation preview; **same-day reversal** that reverses exactly one transaction exactly once.
- [ ] **General ledger** (`pkg_gl`): double-entry postings for every money movement; refuses unbalanced entries and postings into a closed period.
- [ ] **Delinquency** (`pkg_delinquency`): aging buckets 1–30 / 31–60 / 61–90 / 90+ via daily snapshots (MERGE).
- [ ] **Nightly batch orchestration** (`pkg_batch`, reused from JM3): open business date → accrue → penalties → age delinquency → close; idempotent per business date.
- [ ] **Audit** (`pkg_audit`): autonomous-transaction audit log of who did what, including failed attempts.
- [ ] **VPD branch scoping**: loan officers see only their branch's customers/loans; identity propagated from the JWT to Oracle with `DBMS_SESSION.SET_IDENTIFIER` + application context (J8.7.L7).
- [ ] **`loan-query-api`**: loan details, schedule, statement (REF CURSOR / JdbcClient), paginated search, Redis cache for reference data only (never balances).
- [ ] **`payment-api`**: `POST /payments` with **Idempotency-Key** — fast check in Redis, durable uniqueness in Oracle (unique constraint on key + request hash); calls `pkg_payment.post_payment` via `SimpleJdbcCall`; Oracle error codes (e.g. `-20007 PERIOD_CLOSED`) translated to RFC 7807 ProblemDetail (409/422).
- [ ] **`notification-worker`**: transactional **outbox** table written in the same Oracle transaction as the payment; relay publishes to RabbitMQ; idempotent consumer sends notifications.
- [ ] **Security**: OAuth2 Resource Server (JWT), roles Loan Officer / Underwriter / Cashier / Branch Manager / Finance / Admin, method security.
- [ ] **Kubernetes**: all services on kind with Ingress, liveness/readiness probes, graceful shutdown, ConfigMaps/Secrets, resource limits, HPA on `payment-api`.
- [ ] **Observability**: Micrometer → Prometheus → Grafana dashboard (RED metrics per endpoint, HikariCP pool usage, outbox lag, batch duration); OpenTelemetry traces across payment-api → RabbitMQ → notification-worker; `DBMS_APPLICATION_INFO` module/action set so DB sessions are traceable.
- [ ] **Performance report**: fetch size, statement caching, `DBMS_XPLAN` plans for the top 3 queries, HikariCP sizing, Gatling results before/after tuning.

### Invariants (must be enforced in the database and covered by tests)
- [ ] I1 Every GL entry balances: sum(debits) = sum(credits).
- [ ] I2 A loan's outstanding balance equals the replay of its transactions.
- [ ] I3 A payment allocation never exceeds what is due in each bucket.
- [ ] I4 Exactly one active schedule per loan (function-based unique index).
- [ ] I5 Nothing is posted into a closed period.
- [ ] I6 The creator of an application cannot approve it.
- [ ] I7 A reversal reverses exactly one transaction, once.
- [ ] I8 Accrual runs at most once per loan per business date.

### Tech stack
| Tool | Taught in |
|---|---|
| Java 25, records, sealed types | J1, J2.3 |
| Maven multi-module | J4.1 |
| JUnit 5, AssertJ, Mockito | J4.2 |
| Testcontainers (`gvenzl/oracle-free`, RabbitMQ, Redis) | J4.3, J5.3 |
| SLF4J + Logback | J4.4 |
| ojdbc + UCP/HikariCP | J5.2, J5.3 |
| Flyway (versioned + `R__` repeatable package migrations) | J5.4 |
| CallableStatement, REF CURSOR, PL/SQL packages from Java | J5.5 |
| Oracle performance (fetch size, statement cache, execution plans) | J5.9 |
| PL/SQL packages, triggers, autonomous transactions, BULK COLLECT/FORALL, MERGE | Track 1C Part 3 (3.2, 3.5, 3.6, 3.7, 3.9) |
| utPLSQL | Track 1C 3.11 |
| Spring Boot, MVC, Validation, ProblemDetail, springdoc | J7.1, J7.2 |
| Spring transactions, JdbcClient, SimpleJdbcCall, Oracle error translation | J7.5 |
| Spring Security, OAuth2 Resource Server, method security | J7.6 |
| Spring Cache + Redis | J7.7 |
| Spring Batch / scheduling (reused from JM3) | J7.8 |
| Spring AMQP + RabbitMQ | J7.9 |
| Actuator, Micrometer, OpenTelemetry | J7.12 |
| Outbox pattern | J8.3 (concepts: Track 2 B25) |
| Resilience4j (RabbitMQ/Redis calls) | J8.2 |
| Jib or Buildpacks, Docker Compose (local) | J8.4 |
| GitHub Actions | J8.5 |
| Gatling | J8.6 |
| Kubernetes (kind), probes, HPA | J8.7 (basics: Track 2 B30) |
| Oracle VPD, `DBMS_SESSION`, application contexts | J8.7.L7 |
| Prometheus + Grafana | J7.12 (stack: Track 2 B24) |

### Required knowledge
- Track 4: J1–J8.7 (all Parts 1–8 up to and including J8.7); JM2 and JM3 completed (schema, packages and batch reused).
- Track 1C Part 3 in full (PL/SQL packages, triggers, collections, autonomous transactions, DBMS_SCHEDULER, execution plans, utPLSQL).
- Track 2: B25 event-driven patterns (outbox), B30 Kubernetes, B24 monitoring, B34 idempotency keys (concepts).

### Milestones
- [ ] **M1 Schema & invariants** — Flyway migrations for the full CreditLine schema (monthly range partitioning on `loan_transactions`); constraints and the function-based unique index for I4; utPLSQL tests stubbed for I1–I8. *Tag:* `v0.1-schema`
- [ ] **M2 Rules in PL/SQL** — `pkg_application` (state machine + SoD), `pkg_disbursement`, `pkg_payment` (waterfall, preview, reversal), `pkg_gl`, `pkg_audit` as `R__` migrations; error codes via `RAISE_APPLICATION_ERROR`; utPLSQL green for I1–I7. *Tag:* `v0.2-packages`
- [ ] **M3 Boundary services** — `loan-query-api` and `payment-api` with Security, ProblemDetail error mapping, idempotency (Redis + Oracle), Testcontainers integration tests incl. a concurrent double-submit test (same key, 20 threads → exactly one posting). *Tag:* `v0.3-apis`
- [ ] **M4 VPD & audit** — branch-scoped VPD policies, identity propagation per request and cleanup on pool return, audit rows carry the real user; leak test across pooled connections. *Tag:* `v0.4-vpd`
- [ ] **M5 Outbox & notifications** — outbox table written in the payment transaction, relay + RabbitMQ + idempotent `notification-worker`; test: kill the relay mid-batch → no lost and no duplicate notifications. *Tag:* `v0.5-outbox`
- [ ] **M6 Batch & delinquency** — `pkg_delinquency` + JM3 batch integrated; I8 enforced; rerunning a business date is a no-op. *Tag:* `v0.6-batch`
- [ ] **M7 Kubernetes & observability** — all services on kind; probes, graceful shutdown, HPA; Grafana dashboard; end-to-end trace; rollout under load with 0 errors. *Tag:* `v0.7-k8s`
- [ ] **M8 Performance & hardening** — Gatling baseline → tuning (fetch size, statement cache, pool size, indexes from `DBMS_XPLAN`) → after; `docs/performance-report.md` and `docs/architecture.md` (why rules live in PL/SQL, trade-offs). *Tag:* `v1.0-creditline-core`

### Definition of done
- [ ] All eight invariants are enforced by the database and each has at least one utPLSQL test and one Java integration test.
- [ ] Double-submitting a payment with the same Idempotency-Key under concurrency posts exactly once; a different body with the same key returns 422.
- [ ] A branch-1 loan officer cannot read branch-2 data through any endpoint (automated test).
- [ ] Every Oracle business error maps to a documented HTTP status with a ProblemDetail body.
- [ ] `mvn verify` runs unit + Testcontainers + utPLSQL tests in GitHub Actions.
- [ ] `kubectl rollout restart` under Gatling load produces 0 failed requests.
- [ ] Grafana dashboard and a trace screenshot are in `docs/`.
- [ ] Performance report shows measured before/after numbers and explains every change.

**Estimated hours:** ~100h (M1 10 · M2 20 · M3 16 · M4 10 · M5 12 · M6 8 · M7 14 · M8 10)

### Interview questions
1. Why did you put the payment waterfall in PL/SQL instead of Java, and what did it cost you?
2. How do you guarantee a payment is posted exactly once when clients retry?
3. How does VPD work with a connection pool, and how did you prove there is no cross-branch leak?
4. Why do your packages never commit, and what is the one exception?
5. What did you change to make the top query faster, and how did you measure it?

---

**Answers**
1. The rules and invariants sit next to the data, so every client (APIs, batch, APEX, ad-hoc tools) goes through the same logic and the DB can enforce SoD, period close and balance checks atomically. Costs: harder unit testing (needed utPLSQL), deployment via repeatable migrations, less familiar tooling for Java developers, and a thicker Oracle dependency.
2. Two layers: a fast Redis check for obvious duplicates, and the durable guarantee in Oracle — a unique constraint on (idempotency key) with a stored request hash in the same transaction as the posting. A concurrent duplicate hits the constraint; the stored response is replayed; a different hash with the same key is rejected.
3. The policy function reads an application context set per request from the authenticated user (plus `SET_IDENTIFIER` for audit). A filter sets it after borrowing the connection and clears it before return. A Testcontainers test runs user A then user B on the same single-connection pool and asserts B never sees A's rows.
4. The caller's `@Transactional` boundary must decide commit/rollback so the Java side can combine several package calls and the outbox insert atomically. The exception is `pkg_audit`/error logging with `PRAGMA AUTONOMOUS_TRANSACTION`, so failed attempts are recorded even when the main transaction rolls back.
5. Example answer structure: captured the plan with `DBMS_XPLAN.DISPLAY_CURSOR` (actual rows), found a full scan / wrong join order, added a composite index matching the predicate + order, raised JDBC fetch size for the statement endpoint and enabled statement caching; Gatling p95 went from X to Y ms at the same throughput.

---

# Part 9 — Interview Preparation

Part 9 turns everything from Parts 1–8 into interview-ready answers. It adds
no new technology. DSA itself stays in **Track 1B**; here you only learn to
write those solutions in idiomatic Java.

## Module J9.1 — Core Java Interview Topics (~8h)

**Topics:** `HashMap` internals (hashing, buckets, treeification at 8,
resize, why capacity is a power of two), `ConcurrentHashMap` vs
`Collections.synchronizedMap`, `ArrayList` vs `LinkedList` vs `ArrayDeque`,
`TreeMap` (red-black tree) and `LinkedHashMap` (access order → LRU),
fail-fast vs fail-safe iterators; the `equals`/`hashCode` contract and
what breaks when it is violated; immutability (final fields, defensive
copies, records), `String` (immutability, pool, `intern`, compact strings,
concatenation vs `StringBuilder`); generics (erasure, wildcards and PECS,
why `List<Object>` is not a supertype of `List<String>`); exceptions
design; concurrency (thread states, `synchronized` vs `ReentrantLock`,
`volatile`, the Java Memory Model and happens-before, atomics/CAS,
executors, `CompletableFuture`, virtual threads and pinning); JVM memory
areas, class loading and delegation, GC generations and collectors
(G1, ZGC), common OOM types, reading a thread dump.

### Lessons
- [ ] **J9.1.L1 Collections internals.** OpenJDK source of `java.util.HashMap` (class comment "Implementation notes"). Baeldung: "A Guide to Java HashMap" → "HashMap Internals"; "Java Collections Interview Questions".
- [ ] **J9.1.L2 Object contracts & immutability.** *Effective Java* 3rd ed. Items 10 (equals), 11 (hashCode), 12 (toString), 17 (minimize mutability), 50 (defensive copies). Baeldung: "Java Type System Interview Questions".
- [ ] **J9.1.L3 Strings & generics.** *Effective Java* Items 26–31 (generics, PECS). Baeldung: "Java Generics Interview Questions (+Answers)", "Java String Interview Questions and Answers".
- [ ] **J9.1.L4 Concurrency.** *Java Concurrency in Practice* Ch. 2–3 (thread safety, sharing objects), Ch. 16 (JMM). JEP 444 (Virtual Threads) → "Pinning". Baeldung: "Java Concurrency Interview Questions (+ Answers)".
- [ ] **J9.1.L5 JVM & GC.** Oracle "HotSpot Virtual Machine Garbage Collection Tuning Guide" → "Garbage-First (G1) Garbage Collector" and "The Z Garbage Collector". Baeldung: "Memory Management in Java Interview Questions (+Answers)", "Class Loader Interview Questions".

### Exercises (`java/J9.1-interview/`)
- [ ] **Ex J9.1.1 Broken key.** Write a class with `equals` but no `hashCode`, put instances in a `HashSet`, observe the duplicates; then make the key mutable and mutate it after insertion. *Acceptance:* `NOTES.md` explains both failures in 5 sentences.
- [ ] **Ex J9.1.2 Explain-it-aloud drill.** Record yourself (or write) a 2-minute answer to each: HashMap `put` step by step; `volatile` vs `synchronized`; how G1 collects; what a virtual thread is and when it pins. *Acceptance:* each answer fits in 2 minutes and mentions complexity or trade-offs.
- [ ] **Ex J9.1.3 Thread dump reading.** Reproduce a deadlock (from J3.4), take a `jstack` dump and annotate which threads hold/wait on which locks. *Acceptance:* annotated dump in `NOTES.md`.
- [ ] **Ex J9.1.4 Flashcards.** Write 40 Q&A flashcards covering the topics list (10 collections, 10 concurrency, 10 JVM/GC, 10 language). *Acceptance:* you answer 36/40 correctly two days in a row.

### Must be able to do/explain
- [ ] HashMap put/get/resize and worst-case complexity.
- [ ] The equals/hashCode contract and consequences of breaking it.
- [ ] How to build an immutable class and why records help.
- [ ] Happens-before, `volatile`, CAS and when to use each concurrency tool.
- [ ] Heap vs stack vs metaspace; how G1 and ZGC differ; how to diagnose an OOM.

**Estimated hours:** ~8h

### Self-check questions
1. What happens when two keys land in the same `HashMap` bucket?
2. Why must equal objects have equal hash codes?
3. Why is `String` immutable?
4. What does PECS mean?
5. What guarantees does `volatile` give and what does it not give?
6. What is the difference between `synchronized` and `ReentrantLock`?
7. Name three types of `OutOfMemoryError`.
8. When does a virtual thread pin its carrier thread?

---

**Answers**
1. They are stored in the same bucket as a linked list; lookups compare hash then `equals`. When a bucket exceeds 8 entries (and the table is ≥ 64) it becomes a red-black tree, giving O(log n) instead of O(n).
2. Hash-based collections first pick the bucket by hash; if equal objects had different hashes they would land in different buckets and never be found as equal.
3. Safety (can be shared across threads and used as map keys), security (paths, URLs cannot change after checks), and it enables the string pool and cached hash codes.
4. "Producer extends, consumer super": use `? extends T` when you only read T from a structure, `? super T` when you only write T into it.
5. Visibility and ordering (a write happens-before subsequent reads of that variable); it does not make compound actions like `count++` atomic.
6. Both are reentrant mutual exclusion. `ReentrantLock` adds tryLock with timeout, interruptible locking, fairness and multiple `Condition`s, but must be unlocked in `finally`.
7. `Java heap space`, `Metaspace`, `GC overhead limit exceeded`, `unable to create native thread`, `Direct buffer memory`.
8. When it blocks inside a `synchronized` block/method (fixed for most cases in Java 24+ by JEP 491) or during a native/foreign call, so the carrier cannot be released.

---

## Module J9.2 — Spring & Hibernate Interview Topics (~6h)

**Topics:** bean lifecycle (instantiation → populate → `Aware` →
`BeanPostProcessor` → init → destroy), scopes and scoped proxies,
constructor vs field injection, circular dependencies; JDK dynamic proxies
vs CGLIB; how `@Transactional` works through a proxy and its pitfalls
(self-invocation, private methods, checked exceptions not rolling back,
`REQUIRES_NEW` on the same class, `readOnly`); propagation and isolation;
auto-configuration and `@Conditional`; Spring MVC request flow
(`DispatcherServlet`, handler mapping, argument resolvers, message
converters); Security filter chain, authentication vs authorization, JWT
validation; Hibernate: entity states, persistence context and first-level
cache, dirty checking and flush modes, lazy loading and
`LazyInitializationException`, the **N+1** problem and its fixes (fetch
join, `@EntityGraph`, batch size), second-level cache, optimistic
`@Version` vs pessimistic locks, `open-in-view`.

### Lessons
- [ ] **J9.2.L1 Container & proxies.** Spring Framework reference → "The IoC Container" → "Customizing the Nature of a Bean" (lifecycle callbacks); "AOP" → "Proxying Mechanisms". Baeldung: "Spring Interview Questions", "Spring Boot Interview Questions".
- [ ] **J9.2.L2 Transactions.** Spring Framework reference → "Transaction Management" → "Understanding the Spring Framework's Declarative Transaction Implementation", "Using @Transactional" (note on proxy mode and self-invocation), "Transaction Propagation".
- [ ] **J9.2.L3 Hibernate.** Vlad Mihalcea, *High-Performance Java Persistence*, chapters on the persistence context, fetching and the N+1 problem, and concurrency control; vladmihalcea.com articles "N+1 query problem with JPA and Hibernate" and "The best way to handle the LazyInitializationException". Baeldung: "Hibernate Interview Questions".
- [ ] **J9.2.L4 Security.** Spring Security reference → "Servlet Applications" → "Architecture" (`DelegatingFilterProxy`, `FilterChainProxy`, `SecurityFilterChain`). Baeldung: "Spring Security Interview Questions".

### Exercises (`java/J9.2-interview/`)
- [ ] **Ex J9.2.1 Self-invocation demo.** In a small Boot app, show a `@Transactional(propagation = REQUIRES_NEW)` method called from the same class not starting a new transaction; fix it two ways. *Acceptance:* a test asserts the behaviour before and after; `NOTES.md` explains why.
- [ ] **Ex J9.2.2 N+1 hunt.** Using the JP3 or JM1 codebase, write a test that counts SQL statements (e.g. with a datasource-proxy or Hibernate statistics) for a list endpoint, show N+1, then fix it. *Acceptance:* statement count goes from N+1 to 1–2 and the test fails if it regresses.
- [ ] **Ex J9.2.3 Rollback rules.** Show that a checked exception does not roll back by default; configure `rollbackFor`. *Acceptance:* two tests, one per behaviour.
- [ ] **Ex J9.2.4 Whiteboard answers.** Write 1-paragraph answers: request lifecycle in Spring MVC; how a JWT request is authenticated; entity states in Hibernate; optimistic vs pessimistic locking with an example from your projects. *Acceptance:* each uses a concrete example from JM1–JMP3.

### Must be able to do/explain
- [ ] Bean lifecycle and where proxies are created.
- [ ] Every common `@Transactional` pitfall and its fix.
- [ ] Persistence context, dirty checking, flush and lazy loading.
- [ ] How to detect and fix N+1.
- [ ] The Security filter chain for a JWT-protected endpoint.

**Estimated hours:** ~6h

### Self-check questions
1. Why does calling a `@Transactional` method from the same class not start a transaction?
2. When does Spring roll back a transaction by default?
3. What is dirty checking?
4. What causes `LazyInitializationException`?
5. Three ways to fix N+1 in JPA?
6. What is the difference between `@Version` locking and `SELECT … FOR UPDATE`?
7. Why is constructor injection preferred?

---

**Answers**
1. Transactions are applied by a proxy around the bean; an internal `this.method()` call bypasses the proxy, so no advice runs.
2. On unchecked exceptions (`RuntimeException`) and `Error`; checked exceptions commit unless `rollbackFor` is set.
3. At flush, Hibernate compares managed entities with their loaded snapshot and issues UPDATEs for changed ones, without explicit `save`.
4. Accessing an uninitialised lazy association after the persistence context (session) is closed.
5. `JOIN FETCH` in JPQL, `@EntityGraph`, `@BatchSize`/`hibernate.default_batch_fetch_size`, or a DTO projection query.
6. `@Version` is optimistic: no lock, the update checks the version and fails on conflict (retry). `FOR UPDATE` is pessimistic: the row is locked until commit, others wait.
7. Dependencies are explicit and final, the object is never half-built, it is easy to test without Spring, and circular dependencies surface immediately.

---

## Module J9.3 — Idiomatic Java for Coding Tasks (~6h)

**Topics:** choosing the right collection in an interview (`HashMap`,
`HashSet`, `ArrayDeque` as stack and queue, `PriorityQueue` with a
comparator, `TreeMap`/`TreeSet` with `floorKey`/`ceilingKey`,
`LinkedHashMap` access order); `Map.merge`, `computeIfAbsent`,
`getOrDefault`; `Comparator.comparing(...).thenComparing(...).reversed()`;
streams for counting and grouping (`groupingBy`, `counting`, `toMap` with a
merge function) and **when a plain loop is clearer/faster**; records as
tuples/keys; `int[]` vs `Integer` boxing costs; `char` arithmetic,
`StringBuilder`, `String.chars()`; avoiding `Stack`/`Vector`; overflow
(`Math.addExact`, `long`); writing quick tests with JUnit 5 parameterized
tests.

### Lessons
- [ ] **J9.3.L1 Collections for algorithms.** `java.util` Javadoc for `ArrayDeque`, `PriorityQueue`, `TreeMap` (`NavigableMap` methods), `Map` default methods. dev.java → "The Collections Framework".
- [ ] **J9.3.L2 Comparators & streams idioms.** *Modern Java in Action* 2nd ed. Ch. 6 "Collecting data with streams"; `Comparator` Javadoc (static and default methods).
- [ ] **J9.3.L3 Pitfalls.** *Effective Java* Items 45 (use streams judiciously), 61 (prefer primitives to boxed primitives), 63 (string concatenation performance).

### Exercises (`java/J9.3-idiomatic/`)
Re-solve these **20 Track 1B problems in Java** from a blank file (you
already solved them in Python). Rules: idiomatic collections, no `Stack`
class, JUnit 5 parameterized tests with the examples from Track 1B, state
time/space complexity in a comment. Tick when all tests pass.
- [ ] 1.6 Two Sum
- [ ] 1.7 Group Anagrams
- [ ] 1.8 Top K Frequent Elements
- [ ] 1.10 Product of Array Except Self
- [ ] 1.12 Longest Consecutive Sequence
- [ ] 3.4 Longest Substring Without Repeating Characters
- [ ] 4.3 Valid Parentheses
- [ ] 4.4 Min Stack
- [ ] 4.7 Daily Temperatures
- [ ] 5.3 Binary Search
- [ ] 6.3 Reverse Linked List
- [ ] 6.11 LRU Cache (once with `LinkedHashMap`, once with your own doubly linked list)
- [ ] 7.12 Binary Tree Level Order Traversal
- [ ] 8.2 Implement Trie (Prefix Tree)
- [ ] 9.6 Kth Largest Element in an Array
- [ ] 10.2 Subsets
- [ ] 11.3 Number of Islands
- [ ] 11.10 Course Schedule
- [ ] 13.10 Coin Change
- [ ] 14.4 Merge Intervals

Plus:
- [ ] **Ex J9.3.21 Loop vs stream.** For Group Anagrams and Top K, write both a stream and a loop version and benchmark with JMH or a simple timed harness on 10⁶ inputs. *Acceptance:* table + one-paragraph conclusion.

### Must be able to do/explain
- [ ] Pick the right JDK collection for stack, queue, heap, ordered map and LRU without thinking.
- [ ] Write comparator chains and `groupingBy`/`toMap` collectors fluently.
- [ ] Explain boxing overhead and integer overflow risks in Java solutions.
- [ ] Translate a Python solution to Java without changing its complexity.

**Estimated hours:** ~6h

### Self-check questions
1. Why use `ArrayDeque` instead of `Stack`?
2. How do you make a max-heap with `PriorityQueue`?
3. What does `TreeMap.floorKey(k)` return?
4. When is a stream worse than a loop in an interview solution?
5. How do you count frequencies in one line?
6. Why can `Integer == Integer` give wrong results?

---

**Answers**
1. `Stack` extends the synchronized legacy `Vector` (slower, exposes random access); `ArrayDeque` is faster and is the documented recommendation for stacks and queues.
2. `new PriorityQueue<>(Comparator.reverseOrder())` or a custom comparator such as `(a, b) -> Integer.compare(b, a)`.
3. The greatest key ≤ k, or `null` if none exists.
4. When you need early exit, index manipulation, mutable state across elements or primitive performance; streams can hide complexity and add boxing.
5. `Map<Character, Long> freq = s.chars().mapToObj(c -> (char) c).collect(groupingBy(identity(), counting()));` — or `map.merge(key, 1, Integer::sum)` in a loop.
6. `==` compares references; only values in the Integer cache (−128..127) share instances, so larger equal values compare false. Use `equals` or unbox.

---

## Optional Project JO1 — PolisHub Oracle Policy Core · Middle+ · OPTIONAL (~80h)

**Goal:** build the PL/SQL-heavy core of a non-life insurance policy
administration system on **Oracle**, with a thin Spring Boot boundary.
Java never chooses a policy version and never computes a premium — Oracle
does. Source idea: PolisHub (motor TPL/casco, property, travel).

### Features
- [ ] **Tariffs** (`pkg_tariff`): effective-dated base rates × factors (vehicle age, engine power, driver age/experience, territory, bonus-malus); tariff chosen by the **effective date**, never `SYSDATE`; `RESULT_CACHE` on lookups.
- [ ] **Rating & quotes** (`pkg_rating`, `pkg_quote`): premium calculation with a full factor audit trail in `quote_factors`; referral rules route risky quotes to an underwriter.
- [ ] **Policy issue & versioning** (`pkg_policy`): `policy_versions` with `valid_from`/`valid_to` that never overlap and never leave gaps; as-of-date retrieval.
- [ ] **Endorsements** (`pkg_endorsement`): a change creates a new version priced pro-rata from the change date.
- [ ] **Instalments** (`pkg_premium`): schedule, grace, lapse and reinstatement.
- [ ] **Claims / FNOL** (`pkg_claim`, `pkg_reserve`): a claim is assessed against the version in force on the **loss date** (returned to the caller as an OUT parameter); reserves are append-only; a claim cannot be paid while a required document is unverified; approval limits enforced in the DB.
- [ ] **Spring boundary**: `quote-api`, `policy-query-api` (as-of-date), `fnol-api` (Idempotency-Key); Oracle error codes mapped to 409/422/403 ProblemDetail; Redis tariff cache whose key **includes the effective date**.
- [ ] **Nightly batch** (DBMS_SCHEDULER): lapse overdue instalments, earn premium (MERGE), renewal notices at 45/30/15 days; refuses to rerun a closed period.

### Tech stack
| Tool | Taught in |
|---|---|
| PL/SQL packages, result cache, MERGE, triggers, collections, DBMS_SCHEDULER, utPLSQL | Track 1C Part 3 (3.2, 3.5–3.7, 3.9, 3.11) |
| ojdbc, CallableStatement, OUT params, REF CURSOR | J5.3, J5.5 |
| Flyway `R__` package migrations | J5.4 |
| Testcontainers + `gvenzl/oracle-free` | J4.3, J5.3 |
| Spring Boot MVC, Validation, ProblemDetail | J7.2 |
| SimpleJdbcCall, Spring transactions, error translation | J7.5 |
| Spring Security (JWT) | J7.6 |
| Spring Cache + Redis | J7.7 |

### Required knowledge
- Track 1C Part 3 in full; Track 4 J1–J7.7 and ideally JM2/JM3 (same Oracle ↔ Spring boundary patterns).

### Milestones
- [ ] **M1 Schema & temporal rules** — products, coverages, tariffs, parties, risk objects, policies/versions; constraints or triggers guaranteeing no overlaps/gaps; utPLSQL tests. *Tag:* `v0.1-schema`
- [ ] **M2 Rating** — `pkg_tariff` + `pkg_rating` + `pkg_quote` with factor audit trail; tests against hand-computed premiums. *Tag:* `v0.2-rating`
- [ ] **M3 Policy lifecycle** — issue, endorsement pro-rata, instalments, lapse/reinstatement. *Tag:* `v0.3-policy`
- [ ] **M4 Claims** — FNOL with loss-date version lookup, append-only reserves, document gating, approval limits. *Tag:* `v0.4-claims`
- [ ] **M5 Spring boundary** — three APIs, error mapping, idempotent FNOL, Redis tariff cache, Testcontainers tests. *Tag:* `v0.5-apis`
- [ ] **M6 Batch** — nightly chain with rerun protection. *Tag:* `v1.0-polishub-core`

### Definition of done
- [ ] Temporal invariants (no overlap/gap, effective-date tariff, loss-date version) are enforced in the DB and tested.
- [ ] Every quote's premium can be reconstructed from `quote_factors`.
- [ ] Java code contains no premium arithmetic and no version selection logic.
- [ ] FNOL retried with the same key creates exactly one claim.
- [ ] CI runs utPLSQL + Testcontainers tests.

**Estimated hours:** ~80h

### Interview questions
1. How do you guarantee policy versions never overlap or leave gaps?
2. Why must the tariff be chosen by effective date and not `SYSDATE`?
3. Why are reserves append-only?
4. How does the Java side learn which policy version was used for a claim?
5. Why must the Redis tariff cache key include the effective date?

---

**Answers**
1. All version changes go through `pkg_policy`/`pkg_endorsement`, which close the current version at the change date and open the next one in the same transaction under a lock on the policy row; a constraint/trigger check (or a validation query in utPLSQL) asserts `valid_to` of one equals `valid_from` of the next.
2. Quotes, endorsements and back-dated changes must be priced with the rules valid on the business date of the change; `SYSDATE` would reprice history whenever a tariff changes.
3. For audit and reporting: reserve history (and its development over time) must be reconstructable; corrections are new rows, never updates.
4. The package returns `p_version_used` as an OUT parameter read via `SimpleJdbcCall`/`CallableStatement`, and the API returns it to the client.
5. Several tariff versions are valid for different dates at the same time; a key without the date would serve a wrong (newer or older) tariff for a back-dated quote.

---

## Optional Project JO2 — Reactive Price Feed · Middle · OPTIONAL (~30h)

**Goal:** build a small reactive service that streams live FX/stock prices
to many clients, and measure whether WebFlux actually beats a
virtual-threads Spring MVC version for this workload (J7.11: "when NOT to
use reactive").

### Features
- [ ] **Upstream simulator**: a separate app emitting random-walk prices for 50 symbols at 10–100 ticks/s.
- [ ] **Price feed service (WebFlux)**: consumes the upstream with `WebClient` as a stream; fans out to clients over **SSE** (`/prices/stream?symbols=...`).
- [ ] **Backpressure**: slow clients get conflated latest prices (`onBackpressureLatest` or sampling) instead of unbounded buffering; show memory stays flat.
- [ ] **Snapshots**: latest price per symbol stored in Redis (Spring Data Redis reactive template; R2DBC is out of scope because Track 4 does not teach it); `GET /prices/{symbol}` returns the snapshot.
- [ ] **Resilience**: upstream disconnect → retry with backoff, clients see a heartbeat/stale flag.
- [ ] **Comparison build**: the same endpoints in Spring MVC with virtual threads (`SseEmitter`).
- [ ] **Load test**: Gatling with 5 000 concurrent SSE clients against both versions.

### Tech stack
| Tool | Taught in |
|---|---|
| WebFlux, Reactor, WebClient, SSE | J7.11 |
| Virtual threads | J3.4 |
| Spring MVC | J7.2 |
| Redis (Spring Data Redis) | J7.7 |
| Resilience4j / Reactor retry | J8.2, J7.11 |
| Actuator + Micrometer | J7.12 |
| Gatling | J8.6 |
| Testcontainers | J4.3 |

### Required knowledge
- Track 4 J1–J7.12, J8.2, J8.6.

### Milestones
- [ ] **M1 Simulator + reactive feed** — SSE stream end to end. *Tag:* `v0.1-feed`
- [ ] **M2 Backpressure & snapshots** — conflation for slow clients, Redis snapshots, reconnect logic. *Tag:* `v0.2-backpressure`
- [ ] **M3 MVC + virtual threads twin** — same API contract. *Tag:* `v0.3-mvc-twin`
- [ ] **M4 Load test & write-up** — `docs/reactive-vs-virtual-threads.md` with latency, memory and CPU numbers. *Tag:* `v1.0-price-feed`

### Definition of done
- [ ] 5 000 concurrent SSE clients sustained for 10 minutes without memory growth on the reactive version.
- [ ] A deliberately slow client does not slow others or grow the heap.
- [ ] Comparison doc gives a clear recommendation with numbers.

**Estimated hours:** ~30h

### Interview questions
1. What is backpressure and how did you handle slow consumers?
2. Why might virtual threads make WebFlux unnecessary for many apps?
3. What happens if you call a blocking API inside a Reactor pipeline?
4. Why SSE and not WebSocket here?
5. What did your load test show?

---

**Answers**
1. A consumer's ability to signal how much it can take. For price data the latest value is enough, so slow subscribers get conflated/latest-only prices instead of an unbounded buffer.
2. Virtual threads make blocking cheap, so the simple thread-per-request model scales to many concurrent I/O-bound requests without the reactive programming model's complexity.
3. It blocks one of the few event-loop threads, stalling all streams served by it; blocking work must go to `boundedElastic` or be avoided.
4. The flow is one-way server → client, SSE works over plain HTTP, reconnects automatically with `Last-Event-ID`, and passes proxies easily.
5. Answer with your own numbers: e.g. similar p95 latency, reactive using less memory per connection at high fan-out, virtual-threads version simpler to read and debug.

---

## Tool coverage matrix (Track 4)

Every tool used by a Track 4 project is taught in an earlier module
(or in Track 1C / Track 2 where noted).

| Tool | Taught in | First used in |
|---|---|---|
| JDK 25, IntelliJ IDEA | J1.1 | JP1 |
| Maven (basics) | J1.13 | JP1 |
| Maven multi-module, Gradle | J4.1 | JM1 |
| JUnit 5 (basics) | J1.13 | JP1 |
| JUnit 5 advanced, parameterized tests, AssertJ, Mockito | J4.2 | JP2 |
| Testcontainers | J4.3 | JP2 |
| SLF4J + Logback | J4.4 | JP2 |
| Checkstyle / SpotBugs / SonarLint | J4.4 | JP2 |
| JDBC (PreparedStatement, transactions, batch) | J5.1 | JP2 |
| HikariCP | J5.2 | JP2 |
| ojdbc, UCP, Oracle type mapping | J5.3 | JP2 |
| Oracle Database Free (`gvenzl/oracle-free`) | J5.3 (setup: Track 1C 3.1) | JP2 |
| Flyway, Liquibase | J5.4 | JP2 |
| CallableStatement, REF CURSOR, PL/SQL packages from Java | J5.5 | JM2 |
| utPLSQL | Track 1C 3.11 | JM2 |
| JPA / Hibernate | J5.6, J5.7 | JP3 |
| JPQL, Criteria API | J5.8 | JP3 |
| Oracle performance from Java (fetch size, statement cache, plans) | J5.9 | JM2 |
| Spring Framework core (IoC, AOP, `@Transactional`) | J6.1–J6.4 | JP3 |
| Spring Boot | J7.1 | JP3 |
| Spring MVC, Bean Validation, ProblemDetail, springdoc OpenAPI | J7.2 | JP3 |
| Spring Data JPA | J7.3 | JP3 |
| Spring Boot testing (MockMvc, slices) | J7.4 | JP3 |
| Spring transactions, JdbcTemplate/JdbcClient, SimpleJdbcCall | J7.5 | JM1 |
| Spring Security, JWT, OAuth2 Resource Server | J7.6 | JM1 |
| Redis + Spring Cache | J7.7 | JM1 |
| Spring Batch, scheduling, ShedLock | J7.8 | JM3 |
| Spring AMQP + RabbitMQ | J7.9 | JMP1 |
| Spring for Apache Kafka | J7.10 (concepts: Track 2 B16) | JMP1 |
| WebFlux / Reactor / WebClient | J7.11 | JO2 |
| Actuator, Micrometer, OpenTelemetry | J7.12 | JM1 |
| Spring Cloud Gateway / Config / OpenFeign / discovery | J8.1 | JMP1 |
| Resilience4j | J8.2 | JMP1 |
| gRPC in Java, saga, outbox | J8.3 (concepts: Track 2 B25, B32) | JMP1 |
| Layered JARs, Buildpacks, Jib | J8.4 | JMP1 |
| Docker Compose | J8.4 (basics: Track 2 B3) | JMP1 |
| GitHub Actions | J8.5 (basics: Track 2 B9) | JMP1 |
| Virtual threads | J3.4 | JMP2 |
| Gatling | J8.6 | JMP2 |
| JFR, jcmd, VisualVM | J3.6 | JMP2 |
| Kubernetes (kind), probes, HPA | J8.7 (basics: Track 2 B30) | JMP3 |
| Prometheus + Grafana | J7.12 (stack: Track 2 B24) | JMP3 |
| Oracle VPD, `DBMS_SESSION`, application contexts | J8.7.L7 | JMP3 |
| PL/SQL: packages, triggers, collections, autonomous tx, DBMS_SCHEDULER | Track 1C Part 3 | JM2 |
| GraalVM Native Image | J8.8 | (exercises only; optional in any project) |

---

## Track 4 progress summary

Tick **Done** when a module's checklist or a project's Definition of Done is
complete.

### Modules
| Module | Name | File | Hours | Done |
|---|---|---|---|---|
| J1.1 | JDK, JRE, JVM, IntelliJ, compilation & bytecode | 04a | 4 | [ ] |
| J1.2 | Types, operators, control flow, arrays | 04a | 6 | [ ] |
| J1.3 | Strings | 04a | 3 | [ ] |
| J1.4 | Methods & packages | 04a | 3 | [ ] |
| J1.5 | OOP I: classes, encapsulation, static, final | 04a | 6 | [ ] |
| J1.6 | OOP II: inheritance, polymorphism, interfaces | 04a | 6 | [ ] |
| J1.7 | equals / hashCode / toString contracts | 04a | 3 | [ ] |
| J1.8 | Exceptions | 04a | 4 | [ ] |
| J1.9 | Enums, wrappers & autoboxing | 04a | 3 | [ ] |
| J1.10 | Generics | 04a | 5 | [ ] |
| J1.11 | Collections Framework & iterators | 04a | 10 | [ ] |
| J1.12 | I/O, NIO.2, java.time | 04a | 5 | [ ] |
| J1.13 | First build & tests: Maven + JUnit 5 basics | 04a | 3 | [ ] |
| | **Part 1 total** | | **61** | |
| J2.1 | Lambdas, functional interfaces, method references | 04a | 5 | [ ] |
| J2.2 | Streams API & Optional | 04a | 8 | [ ] |
| J2.3 | Records, sealed classes, pattern matching, text blocks, var | 04a | 5 | [ ] |
| J2.4 | Annotations, reflection, JPMS basics | 04a | 5 | [ ] |
| J2.5 | Immutability & design patterns | 04a | 8 | [ ] |
| J2.6 | SOLID & Effective Java | 04a | 6 | [ ] |
| | **Part 2 total** | | **37** | |
| J3.1 | Threads, synchronized, volatile, JMM | 04a | 8 | [ ] |
| J3.2 | Locks, atomics, concurrent collections, synchronizers | 04a | 6 | [ ] |
| J3.3 | ExecutorService & CompletableFuture | 04a | 6 | [ ] |
| J3.4 | Deadlocks, virtual threads, structured concurrency | 04a | 6 | [ ] |
| J3.5 | JVM internals: memory, class loading, GC, JIT | 04a | 8 | [ ] |
| J3.6 | Diagnostics: jcmd, jstack, JFR, VisualVM, leaks | 04a | 6 | [ ] |
| | **Part 3 total** | | **40** | |
| J4.1 | Maven & Gradle (lifecycle, plugins, multi-module) | 04a | 6 | [ ] |
| J4.2 | JUnit 5, Mockito, AssertJ, parameterized tests | 04a | 7 | [ ] |
| J4.3 | Testcontainers | 04a | 3 | [ ] |
| J4.4 | Static analysis & logging | 04a | 3 | [ ] |
| | **Part 4 total** | | **19** | |
| J5.1 | JDBC fundamentals & SQL injection | 04b | 6 | [ ] |
| J5.2 | Connection pooling (HikariCP) | 04b | 2 | [ ] |
| J5.3 | Oracle from Java: ojdbc, UCP, Docker/Testcontainers, types | 04b | 5 | [ ] |
| J5.4 | Flyway & Liquibase | 04b | 4 | [ ] |
| J5.5 | Calling PL/SQL from Java | 04b | 7 | [ ] |
| J5.6 | JPA & Hibernate I | 04b | 8 | [ ] |
| J5.7 | JPA & Hibernate II | 04b | 7 | [ ] |
| J5.8 | JPQL & Criteria API | 04b | 4 | [ ] |
| J5.9 | Oracle performance from Java | 04b | 4 | [ ] |
| | **Part 5 total** | | **47** | |
| J6.1 | IoC, DI, beans & scopes, configuration | 04c | 6 | [ ] |
| J6.2 | Profiles & properties | 04c | 2 | [ ] |
| J6.3 | AOP & how `@Transactional` works | 04c | 5 | [ ] |
| J6.4 | Spring events | 04c | 2 | [ ] |
| | **Part 6 total** | | **15** | |
| J7.1 | Spring Boot fundamentals | 04c | 4 | [ ] |
| J7.2 | Spring MVC & REST, validation, errors, OpenAPI | 04c | 8 | [ ] |
| J7.3 | Spring Data JPA | 04c | 7 | [ ] |
| J7.4 | Spring Boot testing | 04c | 5 | [ ] |
| J7.5 | Transactions, JdbcTemplate/JdbcClient, PL/SQL from Spring | 04c | 6 | [ ] |
| J7.6 | Spring Security | 04c | 10 | [ ] |
| J7.7 | Spring Cache with Redis | 04c | 3 | [ ] |
| J7.8 | Spring Batch & scheduling | 04c | 7 | [ ] |
| J7.9 | Spring AMQP (RabbitMQ) | 04c | 4 | [ ] |
| J7.10 | Spring for Apache Kafka | 04c | 5 | [ ] |
| J7.11 | WebFlux & Project Reactor | 04c | 6 | [ ] |
| J7.12 | Actuator, Micrometer, observability | 04c | 5 | [ ] |
| | **Part 7 total** | | **70** | |
| J8.1 | Spring Cloud | 04c | 8 | [ ] |
| J8.2 | Resilience4j | 04c | 4 | [ ] |
| J8.3 | Inter-service communication, saga, outbox | 04c | 7 | [ ] |
| J8.4 | Containerizing Spring Boot + Compose | 04c | 4 | [ ] |
| J8.5 | CI/CD with GitHub Actions | 04c | 3 | [ ] |
| J8.6 | Performance tuning & load testing | 04c | 6 | [ ] |
| J8.7 | Kubernetes deployment + Oracle VPD | 04c | 6 | [ ] |
| J8.8 | GraalVM native images | 04c | 3 | [ ] |
| | **Part 8 total** | | **41** | |
| J9.1 | Core Java interview topics | 04c | 8 | [ ] |
| J9.2 | Spring & Hibernate interview topics | 04c | 6 | [ ] |
| J9.3 | Idiomatic Java for coding tasks | 04c | 6 | [ ] |
| | **Part 9 total** | | **20** | |
| | **All modules** | | **~350** | |

### Core projects
| Project | Name | Level | Database | PL/SQL from Java | File | Hours | Done |
|---|---|---|---|---|---|---|---|
| JP1 | LedgerLite CLI | Junior | files | — | 04a | 25 | [ ] |
| JP2 | BranchDesk | Junior | **Oracle** | — | 04b | 30 | [ ] |
| JP3 | LoanProduct Catalog API | Junior | PostgreSQL | — | 04c | 35 | [ ] |
| JM1 | TeamBoard | Middle | PostgreSQL | — | 04c | 50 | [ ] |
| JM2 | CreditLine Reporting Service | Middle | **Oracle** | ✅ | 04c | 55 | [ ] |
| JM3 | CreditLine Nightly Batch | Middle | **Oracle** | ✅ | 04c | 50 | [ ] |
| JMP1 | PolisHub Microservices | Middle+ | PostgreSQL | — | 04c | 90 | [ ] |
| JMP2 | TicketRush | Middle+ | PostgreSQL | — | 04c | 60 | [ ] |
| JMP3 | CreditLine Core on Kubernetes | Middle+ | **Oracle** | ✅ | 04c | 100 | [ ] |
| | **Core projects total** | | | | | **~495** | |

### Optional projects
| Project | Name | Level | Hours | Done |
|---|---|---|---|---|
| JO1 | PolisHub Oracle Policy Core | Middle+ | 80 | [ ] |
| JO2 | Reactive Price Feed | Middle | 30 | [ ] |
| | **Optional total** | | **~110** | |

**Track 4 core total: ~845h** (~350h modules + ~495h projects), plus ~110h optional.
