# Stage 11 — Realtime edge + GraphQL + React

| | |
|---|---|
| **Weeks** | W47–W49 (3 weeks) |
| **Hours** | 36 must + 4 stretch (40 total), including a 3.5 h React and TypeScript ramp |
| **Architecture at start → at end** | 6 production deployables (`market`, `atlaspay`, `auth`, `ai`, `bot`, `inventory`) plus `provider-sim`, on kind locally and k3s in the cloud. The storefront is S6's server-rendered pages with a status page that **polls** → the same, plus **`edge`** (FastAPI + Strawberry: GraphQL, WebSocket, SSE and the BFF cookie session) as the 7th production deployable, and a minimal **React SPA**. Redis pub/sub and Redis Streams carry the fan-out. |
| **New technologies** | Django Channels 4.3.2 (spike only), FastAPI WebSockets, Server-Sent Events, HTTP long polling, Redis pub/sub + Streams on Valkey 9.1, Strawberry 0.327 with DataLoader, the `graphql-transport-ws` subprotocol, React + Vite + TypeScript + TanStack Query (all new to you: see §4.0), React Testing Library, Playwright for the BFF login flow |
| **Portfolio tag** | `v0.11` |
| **Old-spec theory to read** | [P7 D115–D120](../python/07-fleettrack.md) (Stage 2: polling baseline, WebSocket ticket auth, heartbeat, bounded send queue, Redis pub/sub fan-out across two replicas, SSE with `Last-Event-ID`, the three-way comparison; daily plan in [phase-5 Week 20](../../phase-5-scaling-architecture.md)); [P10 D157–D161](../python/10-atlasmarket.md) (Stage 1: storefront scaffold, React Router, TanStack Query, cart state; daily plan in [phase-6 Week 27](../../phase-6-capstone.md)); [P10 D166–D168](../python/10-atlasmarket.md) (the GraphQL BFF stretch: 51 calls vs 2 with DataLoader, the transport decision record, Playwright); [P5 D85–D90](../python/05-carepoint.md) (Stage 2: the first React app, the CORS wall, security headers, OIDC Authorization Code + PKCE against Keycloak). **You never built the React days** (P5 D85–D90, P10 D157–D161): the old plan stopped at phase-1 Day 5. Read them for the backend and security parts, and treat React and TypeScript as new; that is what §4.0 is for. |

Version pins are as of 2026-09. Re-check them with `scripts/compat_check.sh` before you start (ADR-001). Channels 4.3.2 installs on Django 5.2 (it declares `Django>=4.2` with no upper bound), so the spike needs no framework change. `market` stays on Django 5.2 LTS for its security support to 2028-04, not because of Channels (E1, E8).

> **What this stage is really for.** Realtime is where "it works on my laptop" lies most convincingly: one process, one socket, no deploys. This stage makes you run live updates across several pods, through deploys, slow clients and dropped connections, and prove that nothing is lost. It also builds the storefront's backend-for-frontend, so the browser gets one well-shaped request instead of a waterfall and never holds a token. Every protocol choice (WS, SSE, long-poll, GraphQL) is made from a measurement, not from taste.

---

## 1. The problem this stage starts from

S10 ended with three problems (the [README §5.1 evolution table](README.md#51-the-evolution-table), row S10). You already measured one of them: the product-page waterfall (call count and p95, `docs/evidence/s10/product-page-waterfall.csv`, from [Stage 10 §4.5 step 8](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must)). You measure the second yourself at the start of this stage, before anything is built: the Channels socket drop (§4.1).

**In business terms:**
- Customers pay and then stare at a page that refreshes every few seconds to learn whether the payment went through. Vendors have no live view of new orders. Buyers and vendors can exchange messages (the `conversations` module from S7), but only by reloading.
- The product page feels slow on mobile networks. Composed on the client, it needs several sequential backend calls (S10 counted them; the plan expects about six), so every call's latency adds up.
- The storefront needs real customer login through `auth` (S9), and the plan says the browser must never hold access or refresh tokens.

**In engineering terms:**
- The obvious realtime design is Django Channels inside `market`. But `market` is the most frequently deployed codebase in Atlas, and every deploy replaces its pods. A socket lives inside one pod, so a `market` deploy closes the sockets held by every pod it replaces, and the clients all try to come back at once. You will measure how bad this is before believing it.
- Kubernetes runs several replicas of everything. An event consumed by pod A must reach a socket held by pod B. Nothing in Atlas does that yet.
- REST composition in the browser produces waterfalls. gRPC (`inventory`) is not browser-native (E4). Something has to compose `market` REST, `inventory` gRPC and AtlasPay data for the client.
- S9 made `market`'s Django session the BFF (*backend-for-frontend*: a server-side layer that exists for one client and holds its session) for server-rendered pages. A single-page app needs its own server-side session holder, or it ends up keeping tokens in `localStorage`.

---

## 2. Outcomes — what exists when the stage is finished

1. **ADR-038 (edge / BFF)** with measured numbers: the share of sockets dropped by one `market` deploy under Channels, the reconnect storm, memory per 5,000 sockets for Channels vs FastAPI, the product-page waterfall (measured in S10) against the page through `edge`, and the BFF security model. It says plainly when Channels inside `market` would have been the better choice.
2. **`services/edge`**, a FastAPI service with no database of its own (`redis-state` only), serving `/graphql`, `/ws`, `/sse/*`, `/poll/*` and `/session/*`.
3. **Live updates across at least 2 edge pods**: order and payment status, the vendor live dashboard and buyer↔vendor chat. They survive reconnects (resume from Redis Streams ids), slow clients (a bounded queue per socket) and deploys (close code 1012 plus drain).
4. **SSE for payment status** with `Last-Event-ID` resume.
5. **A written comparison of short polling, long polling, SSE and WebSocket**, with numbers measured on one rig. The long-poll column comes from a small long-poll endpoint in `edge`; the bot's own `getUpdates` loop is the real-world anchor (and shows the limit of long polling with two consumers).
6. **A GraphQL BFF (Strawberry)**: DataLoaders created per request (51 → 2 downstream calls on the 50-item product list; ≤ 3 on the full product page, one per backend), a depth limiter, query-cost analysis feeding a cost-based rate limit, persisted queries enforced in prod, Relay-style cursors on keyset pagination, subscriptions over `graphql-transport-ws`, and field-level auth (payout fields for `vendor_owner` only).
7. **ADR-039 (GraphQL)**: Strawberry, not Graphene, plus the cost model and the persisted-query policy. **ADR-037 v2** (dated): the S10 REST vs gRPC vs GraphQL decision record, finished with the measured GraphQL numbers.
8. **A minimal React SPA** (Vite + TypeScript + TanStack Query), preceded by a ramp in `sandbox/react-ramp/`. `edge` holds a server-side cookie session and is the confidential OIDC client of `auth`, following the OAuth browser-apps BCP (RFC 10017). The SPA holds no tokens.
9. **Tests and CI**: WS auth, resume and backpressure; long-poll resume; a fan-out test on kind; GraphQL cost, persisted-only, field-auth and DataLoader-count tests; a schema-diff check; RTL smoke tests; a Playwright run of login → order → live "paid".
10. **SD8 (chat) built, SD7 (news feed) on the whiteboard.** Tag `v0.11`, a postmortem paragraph and 2 STAR stories.

---

## 3. Architecture at the end of the stage

```
            Browser: React SPA (static bundle)              Telegram
     cookie: __Host- session id only, HttpOnly, no tokens       |
                         |                                      |
            Gateway / Ingress (Traefik or Envoy Gateway; WS + SSE timeouts)
   /graphql   /ws   /sse/*   /poll/*   /session/*             bot webhook
            \       |      |      |      /                        |
             +------------------------+                     bot (aiogram)
             |  edge  (FastAPI +      |  x2+ pods
             |  Strawberry)           |<---- redis-state:  sess:*  (BFF sessions), wst:* (WS tickets)
             |  - BFF session         |                    ws:stream:{user}  (Streams, MAXLEN)
             |  - DataLoaders/request |                    pub/sub "new entry" pings
             |  - bounded queue/sock  |                    rl:*  (GraphQL cost points)
             +------------------------+
               | REST (user token)  | gRPC (service token)   | REST /v1 + rk_ key (read)
               v                    v                        v   (or via market: ADR-038)
             market             inventory                 atlaspay (pay.<domain>)
         (conversations,       (BatchGetStock,           (payment status,
          vendor_order_view)    WatchStock)               payouts: vendor_owner)
               |
               +-- outbox --> RabbitMQ atlas.events <-- outbox -- atlaspay (payment_intent.*)
                                     |
                                     +--> queue edge.fanout --> any edge pod
                                          (order.*, payment_intent.*, chat.*, vendor_group.*)
             auth  <-- OIDC Authorization Code + PKCE, edge = confidential client
```

**What changed and why:**
- **`edge` is new, and it exists because of numbers.** It holds long-lived connections, which is one of the four reasons a service may leave the monolith ([README §4](README.md#4-the-thesis), point 2). The Channels spike measures what staying would cost. Because sockets live in `edge`, a `market` deploy no longer touches them, and `edge` deploys rarely.
- **Fan-out uses two Redis mechanisms on purpose.** *Fan-out* here means delivering one event to every socket that should see it, whichever pod holds that socket. Redis Streams keep a short, replayable log per user (`ws:stream:{user}`), so a reconnecting client can resume by id. Pub/sub carries only ephemeral "there is something new" pings. E4 records this choice: "Redis Streams (resumable) + pub/sub (ephemeral pings)", not a queue per socket.
- **The browser talks to one origin.** The SPA, `/graphql`, `/ws`, `/sse/*`, `/poll/*` and `/session/*` all sit behind the same Gateway host. That removes most of the CORS work you did in P5 D85–D90 and lets a `SameSite` cookie authenticate everything.
- **`edge` owns no business rules and no database.** It composes, authenticates the browser and fans out. Chat messages are still written by `market` (Mongo `atlas_conversations`). The vendor dashboard still reads the S4 CQRS view (`vendor_order_view`). If a rule appears in `edge`, it is in the wrong place.
- **Not split:** `edge` is one deployable doing both BFF and realtime. Splitting it has a named trigger (§13).

---

## 4. Build plan

The stage has six blocks. The hours in brackets are must-tier budgets, sized bottom-up for someone who has never written Channels, Strawberry, React or TypeScript, and they include the unattended time of benchmark runs. Keep logging actual hours per block in `docs/hours.csv`, as you have since S0, and multiply this stage's budget by your actual/budget ratio (re-checked at B2, then updated with the S9–S10 hours at the S10 stage-end check): if the result does not fit in W47–W49, say so now and plan the cut or the date move at B3 (W50), the checkpoint right after this stage. If a block runs over, stop polishing and record what is missing in `docs/deferred.md`; do not silently defer must work. Long-state tasks (5,000-socket soaks, deploys under load, Playwright on kind) go to the weekend block.

| Block | Must hours |
|---|---|
| 4.0 React and TypeScript ramp | 3.5 |
| 4.1 ADR and Channels spike | 3.5 |
| 4.2 Realtime | 10.5 |
| 4.3 GraphQL | 8.5 |
| 4.4 React SPA | 8 |
| 4.5 Drills + SD8 build / SD7 | 2 |
| **Total** | **36** |

A suggested order across the three weeks:

| When | Work |
|---|---|
| W47 weekdays | 4.0 ramp; 4.1 Channels consumer, FastAPI endpoint and soak client |
| W47 weekend | 4.1 deploy-drop and memory runs, ADR-038 draft; 4.2 `edge` skeleton, tickets, heartbeat, the timeout table, fan-out steps a–d with their runs |
| W48 weekdays | 4.2 resume, backpressure, SSE, long poll, chat and dashboard; 4.3 the S10 baseline check, the schema and the naive resolver |
| W48 weekend | 4.2 `edge` rollout under the soak client and the four-way comparison run; 4.3 DataLoaders and the product-page "after" runs, cost limits, persisted queries, cursors, subscriptions |
| W49 weekdays | 4.3 field auth, schema diff, ADR-037 v2; 4.4 SPA pages and the BFF session |
| W49 weekend | 4.4 live pages, the persisted-query build step, RTL, Playwright on kind; 4.5 SD8 write-up, SD7 whiteboard, drill |

### 4.0 React and TypeScript ramp [3.5 h, must]

**Why this exists.** §4.4 is the first React and TypeScript code you will ever write. Learning them through Atlas's live pages would mix two unknowns with realtime and OAuth bugs, the same reason S1 had a Django ramp. The ramp happens in a throwaway `sandbox/react-ramp/` that nothing imports; it is not part of the Atlas build, CI or coverage. Do it any time before §4.4. The W47 weekday evenings, while the soak runs wait for the weekend, are a good slot.

**The reading and doing path (in order):**

| # | Resource (official docs) | What to take from it | Budget |
|---|---|---|---|
| 1 | React docs, [Quick Start](https://react.dev/learn) | Components, JSX, props, state with `useState`, rendering lists with keys, events | 0.75 h |
| 2 | React docs, [Thinking in React](https://react.dev/learn/thinking-in-react); build its example in the sandbox | Splitting a page into components; where state lives; data flowing down, events flowing up | 0.75 h |
| 3 | TypeScript handbook: [The Basics](https://www.typescriptlang.org/docs/handbook/2/basic-types.html), [Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html), [Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html); then React's [Using TypeScript](https://react.dev/learn/typescript) | Types for props and state; union types for "loading / error / data"; how this maps onto the Python type hints you already use | 0.75 h |
| 4 | Vite [Getting Started](https://vite.dev/guide/) with the `react-ts` template | What the dev server and the build produce; hashed asset names | 0.25 h |
| 5 | [TanStack Query docs](https://tanstack.com/query/latest/docs/framework/react/overview): Overview, Quick Start, Queries, Mutations, Query Invalidation | Query keys, `staleTime`, invalidation after a mutation | 0.5 h |
| 6 | A sandbox experiment (below) | Effects and cleanup, the part that bites realtime pages | 0.5 h |

**The sandbox experiment.** Open a WebSocket to any echo server inside a `useEffect`, and close it in the effect's cleanup. Run it in dev mode with `StrictMode` on. Predict how many sockets open when the page loads, then check the browser's network tab. Write one line on what you saw and why React does it in dev, then compare it with §16 ("Check your prediction").

**The concept mapping.** Write `docs/learning/react-for-backend.md` as a table: backend concept you know → React or TypeScript equivalent → where the analogy breaks. One row as an example; fill at least five more (state, props, effects, a query key, a mutation):

| Backend concept | React / TS equivalent | Where the analogy breaks |
|---|---|---|
| Redis cache-aside with a TTL (S3) | The TanStack Query cache with `staleTime` | The cache lives in one browser tab; invalidation is still your job, and in §4.4 live events drive it |

**Acceptance criteria:**
- The Thinking in React example runs in `sandbox/react-ramp/` with TypeScript and no `any`.
- The StrictMode observation and the mapping table are written.

*If you are behind:* do not skip this block to save time in §4.4; the §4.4 budget assumes it. If you apply degrade item 19 (server-rendered pages instead of the SPA), skip this block as well (see §4.4).

### 4.1 ADR and Channels spike [3.5 h, must]

**Why this exists.** The split rule applies to `edge` like any other service: nothing leaves the monolith until a measurement says staying hurts. The cheap alternative here is real. Channels lets `market` serve WebSockets in the same codebase, with the same auth and ORM. E1 even concedes that "Channels keeps one codebase and wins while deploys are rare." So you measure the cost of Channels first, then decide.

Suggested split of the 3.5 hours: the Channels consumer and its ASGI process type 1; the FastAPI endpoint 0.25; the soak client 0.75; the runs 1 (3 deploy-drop runs + 2 stacks × 3 memory runs = 9 runs; a socket run reaches steady state faster than the split gate's 11-minute scenario, about 6 minutes with ramp-up, so this is about 1 h of unattended time: schedule it in the weekend block); the ADR-038 draft 0.5.

**What to build:**
1. A Django Channels 4.3.2 consumer in `market` that pushes order status for one order to the order's buyer.
   - Channels needs an ASGI server (Daphne or uvicorn) as a separate `market` process type, because the web process is gunicorn (WSGI). Note that cost in the ADR: a new process type with a new failure mode.
   - Use a Redis channel layer. Which instance, `redis-cache` or `redis-state`, and why? Recall what `allkeys-lru` did to your Celery tasks in S4.
   - Any ORM access from an async consumer goes through `sync_to_async` (or `database_sync_to_async`). Django transactions still do not work in async mode (E8). Write down how this shapes the consumer.
2. A tiny FastAPI WebSocket endpoint with the same behaviour (the first line of `edge`), so the memory comparison is fair.
3. A socket-soak client in `bench/`: an asyncio script that opens N sockets, keeps them idle with heartbeats, reconnects with backoff, and logs close codes and reconnect times. Raise the file-descriptor limit (`ulimit -n`) first. This is the most common reason a soak test stops at about 1,000 sockets.

**Pain-first exercise:**

| Do this first | Observe | Record in |
|---|---|---|
| Open 5,000 sockets to the Channels consumer on kind (fewer on a 16 GB laptop; record N), then roll out a new `market` image. Before the run, write down the share of sockets you expect to drop and how long recovery will take. | Sockets connected before and after, close codes, reconnects per second over time, the load on the new pods and on `auth` | `docs/evidence/s11/channels-deploy-drop.csv`: sockets before, dropped, close codes seen, peak reconnects/s, seconds until 95% reconnected, errors during the storm |
| Measure memory with 5,000 idle sockets: Channels vs the FastAPI endpoint, same CPU/memory limits, ADR-002 protocol | RSS (resident memory) growth per socket for each stack. Predict the ratio before you run it. | `docs/evidence/s11/memory-5000-sockets.csv` (+ seed, SHA, image digests, limits) |

Compare the results with your predictions in §16 ("Check your prediction") only after both files are committed.

**ADR-038 draft.** Write these numbers down with a first paragraph on BFF security, and copy in the S10 product-page waterfall (call count and p95) as the "before" number for composition; the "after" number arrives in §4.3 step 3. §8 lists what the finished ADR must contain.

**Acceptance criteria:**
- Both CSV files are committed with ADR-002 metadata and at least 3 runs each.
- ADR-038 is drafted with the counter-argument ("Channels keeps one codebase; deploys could be made rare") and the "if the numbers don't hurt, say so" clause.
- The Channels consumer is **deleted or disabled** after the spike. It is evidence, not a second realtime path.

*If you are behind:* degrade item 2 cuts this block to the one-deploy socket-drop count only, dropping the memory runs (saves 1 h). Channels vs FastAPI is an explicit requirement, so this item sits late in the degrade order ([schedule-and-cuts.md](schedule-and-cuts.md) §7).

### 4.2 Realtime [10.5 h, must]

**Why this exists.** A live update has to survive four things a single-process demo never meets: a second pod, a reconnect, a client that reads slowly, and a deploy. Each one silently loses messages if you ignore it. FleetTrack (P7 D115–D120) met the first three with two replicas and pub/sub. Atlas adds resume by id, graceful shutdown and a Kubernetes Gateway in the path.

Suggested split of the 10.5 hours: skeleton and tickets 1.5; heartbeat and reconnect 0.5; fan-out, pain first, 2.25 (includes 2 designs × 3 runs of about 11 minutes, ≈ 1.1 h unattended); resume 1.5; backpressure and graceful shutdown with the rollout runs 1.5; timeouts 0.5; SSE 0.5; the long-poll endpoint and the four-way comparison 1.25 (one run set of 3 with all four transports connected at once, ≈ 0.5 h unattended); chat and dashboard 1. The fan-out runs, the rollout under the soak client and the comparison run go in the weekend blocks.

**What to build:**

1. **The `edge` skeleton.** `services/edge` on FastAPI, Python 3.13, with clients (Redis, HTTP, gRPC channel) created and closed in the lifespan, never per request.
   - It consumes the RabbitMQ queue `edge.fanout` (a quorum queue bound to `atlas.events` for `order.*`, `payment_intent.*`, `chat.*` and `vendor_group.*`).
   - It is a Deployment with at least 2 replicas from day one. A realtime feature tested on one pod is not tested.

2. **WebSocket tickets.** A *ticket* is a short-lived, single-use random string that lets a browser open a socket without putting a real credential in the URL.
   - The SPA calls a `/session/*` endpoint (for example `POST /session/ws-ticket`) with its cookie. `edge` stores the ticket in `redis-state` under the `wst:` prefix with a TTL of a few seconds (choose the TTL and write down why) and returns it.
   - The browser connects to `/ws?ticket=…`. `edge` consumes the ticket atomically, so a second use fails, and binds the socket to that user.
   - Check the `Origin` header on the handshake. Browsers send cookies on WebSocket handshakes, and WebSockets are not covered by CORS. Without an Origin check, any site can open a socket as your user. This attack is called cross-site WebSocket hijacking.
   - The JWT never appears in a URL. Proxies, Gateways and browsers log URLs.
   - Ask yourself: why use a ticket at all when the cookie already reaches `edge`? Write the answer in ADR-038. Think about CSRF-style attacks on the handshake and about clients that are not on your origin.

3. **Heartbeat and reconnect.**
   - A heartbeat every 20 s, application-level, so the browser can also detect a dead server. Browser JavaScript cannot see protocol-level ping frames.
   - The client treats two missed heartbeats as a dead socket.
   - The client reconnects with exponential backoff and **full jitter** (a random delay between 0 and the current backoff cap). Without jitter, every client that lost its socket in the same second comes back in the same second.

4. **Fan-out across pods, pain first.**

   Before each step, write your prediction for the "missing" count in the evidence file, then run it.

   | Step | Do this | Observe | Record in |
   |---|---|---|---|
   | a | Run 2 edge pods. Each pod consumes `edge.fanout` as a competing consumer and delivers only to its own sockets. Connect 50 clients spread over both pods and publish 1,000 events. | Events published vs frames received per client and per pod; for each missing event, which pod consumed it and which pod holds the socket | `docs/evidence/s11/fanout-missing.csv`: published, delivered per pod, missing |
   | b | Add Redis pub/sub: the consuming pod publishes, every pod subscribes and forwards to its own sockets. | The same counts, with every client connected throughout | same file, second row |
   | c | Disconnect one client for 30 s during a steady event rate, then reconnect. Then restart one edge pod. | What the reconnected client, and the clients of the restarted pod, received for the events sent while they were away | `docs/evidence/s11/pubsub-vs-streams.csv` |
   | d | Switch to Streams plus pings: the consuming pod appends the event to `ws:stream:{user}` (with `MAXLEN ~` trimming) and publishes a small ping. The pod holding the socket reads the stream from the last id it delivered. | The same gap and restart counts as step c | same file |

   Also record the fan-out delivery latency (event consumed → frame sent), p95 for each design (3 runs each, ADR-002), and the memory of the streams at your chosen `MAXLEN`. The expected results are in §16 ("Check your prediction"); open them only after your predictions are committed.

   Two questions to answer before you write code:
   - RabbitMQ delivers at least once. If the same event is appended to a stream twice, where do you deduplicate: before the append, or in the client using `event_id`?
   - `redis-state` runs with `noeviction` (S3). What happens to the limiter, the FSM and the sessions if streams grow without a `MAXLEN`?

5. **Resume from Redis Streams ids.** A stream id looks like `<milliseconds>-<sequence>` and only grows.
   - Every frame sent to a client carries its stream id. The client remembers the last id it processed.
   - On reconnect, the client sends that id in its first message. The server replays everything after it (an exclusive range) and then switches to live delivery. The seam must have **no gap and no duplicate**: think about whether to subscribe first and replay second, and how the client drops an id it has already seen.
   - If the id has already been trimmed away (the client was offline too long), the server must say so explicitly. The client then refetches a snapshot through GraphQL. A snapshot is only safe to combine with live updates if it carries the stream id it was taken at.
   - The envelope shape (illustrative):

     ```json
     {"stream_id": "1727000000000-3", "event_id": "0190c…", "type": "vendor_group.fulfilled", "data": {…}}
     ```

6. **Backpressure: a bounded queue per socket.** *Backpressure* is how a system pushes back when a consumer cannot keep up, instead of buffering without limit.
   - Pain first: give each socket an unbounded queue, then connect a client that stops reading. Predict what happens to the edge pod's memory and to the other clients' delivery latency, then watch both (and note whether your fan-out loop ever awaits a send on one particular socket).
   - Fix: each socket gets a bounded `asyncio.Queue` drained by its own sender task. The fan-out loop only ever does a non-blocking put. When a socket's queue is full, that client is closed with a close code you choose (write down which and why) and counted. Because of resume, the client loses nothing: it reconnects and replays.
   - Record in `docs/evidence/s11/backpressure.csv`: queue size, time until the slow client is dropped, consumer lag before and after, and the other clients' delivery p95.

7. **Graceful shutdown.**
   - On SIGTERM: stop accepting new sockets, send close code **1012** (Service Restart) to every client, let sender tasks flush for a bounded time, then exit.
   - Combine this with the preStop hook and grace period from S10. The pod must leave the Service endpoints before it closes sockets.
   - Pain first: roll out `edge` under the soak client without any of this and count lost messages and reconnect spikes. Then roll out with it. Target: 0 lost messages (resume makes this possible) and a reconnect curve spread out by jitter. Record in `docs/evidence/s11/edge-rollout.csv`.

8. **Timeouts on the path.**
   - Kubernetes path: find every idle or read timeout between the browser and `edge`: the Gateway (Traefik or Envoy Gateway; on k3s, Traefik's Gateway API provider is the one you enabled in S10), any load balancer in front of k3s, and uvicorn's own settings. Not ingress-nginx: it is retired (announced 2025-11-11; no releases or security fixes after March 2026) [C]. Put the timeouts in a table in `docs/design/realtime-transports.md`. The 20 s heartbeat, and the 25 s long-poll hold in item 10, must be shorter than all of them.
   - Compose path: Nginx needs `proxy_http_version 1.1`, the `Upgrade` and `Connection` headers passed through, and a `proxy_read_timeout` longer than the heartbeat interval. The default is 60 s. For SSE, Nginx must not buffer the response (`proxy_buffering off`, as in S8).

9. **SSE for payment status.** *Server-Sent Events* are a one-way stream over plain HTTP (`text/event-stream`). The browser's `EventSource` reconnects by itself and sends the last `id` it saw in the `Last-Event-ID` header.
   - An endpoint under `/sse/*` streams one order's payment status. Each event's `id:` is its stream id, so resume uses the same mechanism as the socket.
   - `EventSource` cannot set headers. Authentication therefore rides on the same-origin cookie session, which is one more reason for a single origin.
   - The wire format, for reference:

     ```
     id: 1727000000000-0
     event: payment_intent.succeeded
     data: {"order_id": "…", "status": "paid"}
     ```

   - Remember the HTTP/1.1 limit of about six connections per origin in browsers. Several SSE tabs over HTTP/1.1 can starve the page's other requests. Check which HTTP version your Gateway speaks to browsers.

10. **The four-way transport comparison, anchored on real Atlas traffic.**
    - Short polling: the S6 status page that polls (your baseline).
    - Long polling, built: a small endpoint in `edge`, `GET /poll/orders/{id}?after=<stream_id>`, on the same cookie session as SSE. It holds the request open until an event newer than `after` exists in the user's stream (Redis `XREAD` with `BLOCK` waits on the stream server-side), or until a 25 s hold ends and it returns an empty answer; the client immediately asks again with the last id it received. Keep the 25 s hold below every idle timeout in your item 8 table. Ask yourself: a blocking `XREAD` ties up one Redis connection per waiting request; how many can one pod hold, and would waiting on the pod's existing pub/sub ping be cheaper?
    - Long polling, the real-world anchor: the bot's own `getUpdates` loop in dev polling mode. The request waits on Telegram's side until an update arrives or the timeout ends, and an `offset` acknowledges what was processed, the same idea as your `after` id. It also shows long polling's scaling limit when the server hands out the work: a second consumer gets `409 Conflict`, which is why the bot moved to a webhook in S10. Use it qualitatively; its latency includes Telegram and the internet, so it is not comparable with your rig.
    - SSE and WebSocket: what you built here.
    - Measure all four on the same rig in one run set: clients on each transport connected to the same `edge` pods at once, one fixed event rate, 3 runs (ADR-002). Compare direction, idle cost (requests per minute per client), measured delivery p95, resume mechanism (`after`/`offset`, `Last-Event-ID`, stream id), what happens with 2+ server replicas, proxy configuration and authentication. Write it in `docs/design/realtime-transports.md`. The E4 choices (SSE for status and LLM tokens, WebSocket for chat, dashboard and subscriptions, polling kept as the baseline) should now read as conclusions from your table.

11. **Chat and the vendor live dashboard.**
    - Chat goes through `market`'s conversations API (Mongo `atlas_conversations`). A client sends a message with a `client_msg_id`. `edge` forwards it to `market` with the user's token. `market` assigns the per-conversation `seq` and writes the message and the outbox event `chat.message_sent` together. Then the event flows back through `edge.fanout` to every participant's stream.
    - A duplicate `client_msg_id` (a retry after a timeout) must produce one message, not two. Clients order messages by `seq`. A gap in `seq` means "fetch what is missing through the API", never "reorder by arrival time".
    - Only participants receive a conversation's events (the S7 invariant). Decide where this is enforced: does the event carry the participant list, or does `edge` ask `market`?
    - The vendor live dashboard reads the S4 CQRS view (`vendor_order_view`) through `market` for its snapshot and applies `vendor_group.*` events live on top.
    - Chat text now also sits in Redis Streams for a while. Add `ws:stream:*` to the PII inventory in `docs/privacy/data-governance.md`, with its retention (`MAXLEN` and key TTL).

**Acceptance criteria:**
- The fan-out table has all four steps with your predictions and the measured counts; after step d, 0 events are missing across a 30 s disconnect and a pod restart.
- An expired ticket, a reused ticket and a foreign `Origin` are each refused. No token appears in any URL in the Gateway or `edge` access logs after a full E2E run (scan them for it).
- A client that stops reading is dropped, and other clients' delivery p95 does not move.
- An `edge` rollout under the soak client loses 0 messages.
- SSE resume and long-poll resume (`after`) each deliver exactly the missed events.
- A duplicate `client_msg_id` produces one message; `seq` is gap-free per conversation.
- `docs/design/realtime-transports.md` has the four-way table with numbers from one rig and the timeout table.

### 4.3 GraphQL [8.5 h, must]

**Why this exists.** The product page needs data from three backends in a shape only the page knows. Doing that on the client produces a waterfall of sequential calls, which S10 already measured (call count and p95). A BFF composes it once, close to the backends, and returns exactly the fields the page asked for. GraphQL fits because the client drives the shape (E4). But a naive GraphQL server turns one query into hundreds of backend calls, and it lets anyone send an arbitrarily expensive query. Those two problems are the real lesson (P10 D166–D168). The syntax is not.

Suggested split of the 8.5 hours: the S10 baseline check 0.25 (one run of the S10 waterfall probe, about 11 minutes unattended); the Strawberry skeleton and the schema 1; N+1, DataLoaders and the product-page "after" runs 1.25 (3 runs, ≈ 0.5 h unattended); depth, cost and the cost-based rate limit 1.5; persisted-query enforcement 0.5 (the build-time extraction is in §4.4); cursors 0.5; one subscription 1.25; field auth and the parity matrix 1; the schema-diff job 0.5; ADR-037 v2 0.75.

**What to build:**

1. **Strawberry via `GraphQLRouter`** mounted at `/graphql`, with a `context_getter` that builds a fresh context per request: the session's user, downstream clients and **new DataLoader instances**.
   - A *DataLoader* collects every `load(key)` made during one tick of the event loop, calls a batch function once with all the keys, and memoizes results for the rest of that request.
   - Why per request and never global? A global loader's memo is shared between users (a data leak) and never expires (stale data). Write this sentence in ADR-039 in your own words.

2. **The schema** (requirements, not code): `Product`, `Offer`, `Vendor`, `Stock`, `Order`, `VendorGroup`, `PaymentStatus`, `Conversation`, `Message`, and `Payout` (visible only to the vendor's owner). Each type records which backend owns it:
   - `market` REST: products, offers, vendors, orders, vendor groups, review counts, conversations;
   - `inventory` gRPC: `BatchGetStock` for stock, and `WatchStock` if you want live stock;
   - AtlasPay data: payment status and payouts. Decide, and record in ADR-038, whether `edge` reads it directly from `atlaspay` or through `market`.
     - *Directly* means AtlasPay's public merchant API, the way the README E4 table says every merchant reaches it: REST `/v1/*` (on `pay.<domain>`, or the same API through its in-cluster Service), with a restricted `rk_` key that has read scopes only, sent as `Authorization: Bearer rk_…` (S9). AtlasPay knows merchants and their keys, not platform services, so the key is `market`'s.
     - *Through `market`* means `market`'s internal REST: since S9, `market` receives payment, refund and payout outcomes as signed AtlasPay webhooks, like any merchant.
     - Ask yourself: which service should hold a merchant credential, and what does a second holder add to the blast radius? Either way, `edge` must not become a second place where payout permissions are decided.

3. **The waterfall baseline, then N+1, pain first.**
   - **Start from the S10 waterfall.** `docs/evidence/s10/product-page-waterfall.csv` holds the call count and p95 of the product page composed with sequential REST calls ([Stage 10 §4.5 step 8](stage-10-kubernetes-grpc-inventory.md#45-grpc-inventory--13-h-must)). It is the "before" number for ADR-038 and ADR-037 v2; do not rebuild it. The rig has changed since W46 (new images, `edge` on the cluster), so first re-run the S10 probe once with the same settings. If the result falls inside the S10 run spread, the baseline stands; if not, re-measure it (3 runs, ADR-002) into `docs/evidence/s11/` before you compare anything with it.
   - Write the naive resolver next: the product list query for 50 products, each resolving `vendor` with its own call. Count downstream calls with a counter in your HTTP client and gRPC interceptor, exposed to tests. Predict the count before you run it.
   - Add DataLoaders for vendors and for stock (`BatchGetStock`). The target is **2** calls for products + vendors.
   - Then measure the whole product page through `edge`: the waterfall becomes one client round trip, with **≤ 3 downstream calls**, at most one per backend and each batched. Measure its p95 with the same constant-rate probe and ADR-002 settings as the S10 waterfall (3 runs), so the before and after numbers are comparable.
   - Record calls and p95 in `docs/evidence/s11/dataloader-calls.csv`.
   - Details to get right: the batch function must return results **in the same order as the keys**, with an explicit "not found" for missing keys; duplicate keys must be collapsed; and a failing batch must fail only the fields that depend on it.

4. **Depth limit, query cost and a cost-based rate limit.**
   - Pain first: a request-count limiter (S3 style) happily admits one query like `products(first: 100) { vendor { products(first: 100) { vendor { … } } } }`. Measure the downstream calls and time of that single request.
   - A depth limiter: Strawberry ships a query-depth extension. Choose the maximum depth from your real SPA queries plus a margin.
   - Query cost: compute a cost before execution by walking the parsed query. Give each field a cost, and multiply list fields by their `first`/`last` argument (a list field without a bound is itself an error). Strawberry does not decide your cost model for you: you define it, test it and document it in ADR-039. Check the current Strawberry extension list for alias and token limiters too.
   - Rate limit by cost: each client has a budget of cost points per minute in `redis-state` (reuse your S3 Lua machinery). The estimated cost is taken before execution. Per E10, this limiter fails open if Redis is down and returns an error **before execution**. Decide the HTTP status and headers so they match the rest of Atlas (`Retry-After`, `X-RateLimit-*`), and write the choice down.
   - The test that matters: a query over the limit is rejected, and a spy proves **no resolver ran**.

5. **Persisted queries, enforced in prod only.**
   - At SPA build time, extract every operation, hash it and register the hash in an allow-list that `edge` loads. The build step arrives with the SPA in §4.4; until then, register the handful of operations you test with by hand.
   - In prod, `edge` executes only registered hashes and rejects any other document. In dev, ad-hoc queries stay allowed so you can explore.
   - This closes the "arbitrary query" door entirely for the public, and it makes the cost limit a second wall rather than the only one.

6. **Relay-style cursors on keyset pagination.** A *connection* returns `edges`, each with an opaque `cursor`, plus `pageInfo`. The cursor encodes the keyset tuple from S1 (for example the sort key plus the id), never an OFFSET. Reuse the S1 tests for ties and for rows inserted mid-walk.

7. **Subscriptions over `graphql-transport-ws`.** This is the WebSocket subprotocol used by the `graphql-ws` library. Confusingly, the older and deprecated `subscriptions-transport-ws` library used the subprotocol *name* `graphql-ws`. Strawberry can speak both; enable only `graphql-transport-ws`, and make sure your SPA client library speaks the same one. Build one subscription, for example an order's status. It must reuse the same ticket authentication, the same Streams-based fan-out and the same bounded queue as `/ws`. A subscription is not allowed to be the one path without backpressure.

8. **Field-level auth.**
   - Payout fields resolve only for the `vendor_owner` of that vendor. Use Strawberry permission classes on the fields, backed by the same relationship rule `market` uses in REST (S1: staff act only for their own vendor).
   - Invariant: **GraphQL never exposes a field REST would refuse.** Prove it with a parity matrix test: for each role (customer, vendor_staff, vendor_owner, ops) × each sensitive field, call REST and GraphQL and compare allow/deny.
   - Watch the indirect paths. If `payouts` is protected on `Vendor`, can it be reached through `Order → vendorGroups → vendor`? Field auth protects the field on every path; top-level-only checks do not.

9. **Schema evolution.** Commit the exported schema. CI diffs the new schema against the committed one on `main` and fails on breaking changes (a removed field, a type change, a new required argument) unless the PR is labelled deliberately. graphql-core has breaking-change detection you can build this on.

10. **ADR-037 v2.** Finish the S10 transport decision record with GraphQL numbers (§8): the S10 waterfall against the product page through the GraphQL BFF.

**Acceptance criteria:**
- The S10 waterfall baseline is confirmed on today's rig (one run inside the S10 spread), or re-measured into `docs/evidence/s11/`.
- `dataloader-calls.csv` shows 51 → 2 on the product list and ≤ 3 downstream calls for the full product page.
- An over-cost query is rejected before execution (spy test), and the cost budget per client is enforced across 2 edge pods.
- In prod settings, an unregistered query document is rejected.
- Cursor pagination passes the S1 tie and mid-walk insert tests.
- A subscription over `graphql-transport-ws` receives an order-status event from another pod.
- The parity matrix passes, including one indirect path.
- The schema-diff job fails on a deliberately breaking change (try it once on a branch).
- ADR-037 v2 is dated and accepted, with the GraphQL numbers.

*If you are behind:* degrade item 1 is a partial degrade, because persisted queries and subscriptions are explicit requirements: both stay. It drops only the persisted-query build tooling in §4.4; you keep a hand-maintained allow-list of the SPA's operations, still enforced in prod (saves 0.5 h).

### 4.4 React SPA [8 h, must]

**Why this exists.** Two things in Atlas genuinely need a browser client: live pages (to prove the realtime work end to end) and the OAuth browser flow (to prove tokens stay out of the browser). The SPA is kept minimal on purpose. The old AtlasMarket spec named "treating the storefront as equally important as the backend" as a mistake (P10 D157–D161), and that still holds. The budget assumes the §4.0 ramp is done; the old plan alone gave 7 h to a scaffold, a product list and a cart ([phase-6](../../phase-6-capstone.md) D160–D161).

Suggested split of the 8 hours: the scaffold, routing and the product pages on GraphQL 2; the BFF cookie session (OIDC client, cookie, CSRF rules) 2; the live pages 1.5; the persisted-query extraction in the build 0.5; RTL smoke tests 0.5; Playwright on kind with the no-token assertions 1.5.

**What to build:**

1. **The SPA:** Vite + TypeScript + TanStack Query, with a handful of pages: product list and product page (GraphQL), order status (SSE or a subscription), the vendor live dashboard (WebSocket), and chat (WebSocket). Keep the source next to its BFF, in `services/edge/web/`. Serve the built bundle from the same host as `edge`, with long-lived cache headers on hashed asset names and a short one on `index.html`. The build extracts every GraphQL operation and registers its hash for §4.3 step 5 (`spa-build` in §7). A CDN in front of the hashed assets is optional stretch (§14).

2. **The BFF cookie session.**
   - `edge` is a **confidential OIDC client** of `auth` (S9): Authorization Code + PKCE, with `state` and `nonce` validated and a client secret that only `edge` knows. The flow starts and ends under `/session/*` (for example login, callback, logout, "who am I", and the WS ticket).
   - Tokens (access and refresh) stay in `redis-state` under `sess:`, keyed by a random session id. `edge` refreshes them server-side using the S9 refresh families.
   - The browser gets one cookie holding only the session id, with the `__Host-` prefix, `Secure`, `HttpOnly`, `SameSite` (choose Lax or Strict and write down why) and `Path=/`.
   - Downstream calls from `edge` carry the user's access token. The browser never sees it.
   - CSRF: with a cookie session, a malicious page can make the browser send requests with your cookie. Mutations go only over POST with a JSON content type, `edge` checks `Origin`, and GraphQL over GET never executes mutations.
   - This is the pattern the IETF *OAuth 2.0 for Browser-Based Applications* BCP describes as a backend-for-frontend (RFC 10017, [rfc-editor.org/info/rfc10017](https://www.rfc-editor.org/info/rfc10017/)) [verify]. ADR-038 compares it with the alternative, **a public PKCE client in the SPA**: no server session, but tokens in JavaScript memory, where any XSS can read them, and refresh-token handling in the browser.
   - `market`'s Django session stays the BFF for Admin and the back office (S9). `edge` is the BFF for the SPA.

3. **Live pages:** order status turns "paid" without a reload, the vendor dashboard shows a new vendor group as it arrives, and chat resumes after a reconnect. TanStack Query's cache is updated from live events, not refetched on every event. The phase-6 Week 27 question set (the P10 D157–D161 week) asked how TanStack Query's cache relates to your Redis cache-aside. Answer it again here, now that events drive invalidation.

4. **Tests:**
   - React Testing Library smoke tests: each page renders; a live event updates the status component.
   - Playwright (on kind in CI): log in through `auth` and Keycloak → place an order → pay through the `provider-sim` checkout → watch the order page turn **"paid"** live.
   - In the same Playwright run, assert that `localStorage`, `sessionStorage` and `document.cookie` contain no token, and that the session cookie is not readable from JavaScript.

**Acceptance criteria:**
- The Playwright flow is green on kind.
- No token is visible to JavaScript, and none appears in any logged URL.
- A cross-origin POST to `/graphql` is refused.
- ADR-038 contains the BFF vs public-client comparison.

*If you are behind:* degrade item 19 replaces the SPA with server-rendered pages plus a small WebSocket client script; the BFF session and the Playwright test stay. Minimal React is an explicit requirement, so this item is near the end of the degrade order ([schedule-and-cuts.md](schedule-and-cuts.md) §7). If you apply it, skip §4.0 too: together they save 7 h (the 3.5 h ramp and 3.5 h of this block).

### 4.5 Drills + SD8 build / SD7 [2 h, must]

- **SD8 Chat (built, write-up W49).** You built the storage half in S7 (W29–W31) and the realtime half now (W47–W48). Write `docs/sd/sd08-chat.md` against the bank's asks ([system-design-problems.md](../../system-design-problems.md)): connection management at scale (your fan-out plays the "gateway that routes to the server holding the connection"), ordering and at-least-once delivery with client dedup (`seq` + `client_msg_id`), and offline recipients (store-and-forward in Mongo plus a push through the bot's `bot.notifications`, S4). Add what you would change at 100× the connections.
- **SD7 News feed (whiteboard, W49).** The Atlas anchor is a "followed vendors" feed. Work fan-out-on-write vs fan-out-on-read, and the celebrity case: a whale vendor with a huge follower count is your version of it. Say which parts of today's Streams fan-out would survive and which would not.
- **Drill hour:** one SQL problem on the Atlas schema or one DSA problem from the banks, plus this stage's interview questions out loud. If real interviews are already happening (the job search started at B2), a real interview and its retro may replace the drill hour; this is a requirement-neutral degrade ([schedule-and-cuts.md](schedule-and-cuts.md) §7).

---

## 5. Invariants

| Invariant | How it is enforced | The test that proves it |
|---|---|---|
| No update is lost across a reconnect. | Every frame carries its stream id; resume replays after the last id; trimmed ids trigger an explicit snapshot refetch. | Disconnect mid-stream, reconnect, receive exactly the missed events in order with no duplicates; same across an `edge` pod restart and rollout. |
| The JWT never appears in a URL, and the SPA never holds tokens. | WS tickets (single-use, seconds of TTL) in URLs; tokens only in `redis-state` sessions; `HttpOnly` session cookie. | Access-log scan after the E2E run finds no token; Playwright finds no token in storage or `document.cookie`. |
| A query over the cost limit is rejected before it executes. | Cost computed from the parsed query; the budget is checked in `redis-state` before execution. | An over-cost query returns the limit error, and a resolver spy records zero calls. |
| GraphQL never exposes a field REST would refuse. | Field permissions use the same relationship rule as `market`'s REST. | Role × field parity matrix, including one indirect path to payouts. |
| The product page makes ≤ 3 downstream calls. | Per-request DataLoaders; batched `BatchGetStock`. | Call-count test on the product page and on the 50-item list (2 calls). |
| A slow client never stalls fan-out (from 4.2). | A bounded queue per socket; non-blocking puts; full queue → close. | A non-reading client is dropped; the other clients' delivery p95 is unchanged. |

---

## 6. Tests to write

**Realtime (`edge`):**
- WS auth: a valid ticket connects; expired, reused and missing tickets are refused; a foreign `Origin` is refused.
- Heartbeat: the server sends one every 20 s; a client that stops answering is closed after the documented number of misses.
- Resume: disconnect, publish N events, reconnect with the last id; exactly N arrive, in order. A trimmed id produces the explicit "snapshot needed" message.
- Fan-out on kind: a client on pod B receives an event consumed by pod A. Pin clients to pods (for example with a port-forward per pod) so the test cannot pass by luck.
- Backpressure: a client that stops reading is dropped within a bounded number of messages; consumer lag stays flat.
- Graceful shutdown: SIGTERM sends 1012 to every client; after reconnect and resume, 0 events are lost.
- SSE: `Last-Event-ID` resume delivers exactly the missed events; the cookie is required.
- Long poll: a held request returns as soon as a newer event exists; it returns empty at the 25 s hold; resuming with `after` delivers exactly the missed events; the cookie is required.
- Chat: a duplicate `client_msg_id` yields one message; `seq` is monotonic and gap-free; a non-participant receives nothing.
- At-least-once: the same `edge.fanout` message delivered twice produces one frame per client.

**GraphQL:**
- DataLoader call counts (51 → 2; ≤ 3 on the product page); batch order and missing-key behaviour.
- Depth limit and cost limit (resolver spy); cost budget shared across 2 pods; fail-open when `redis-state` is down (with the alert raised).
- Persisted-only in prod settings; ad-hoc allowed in dev settings.
- Cursor pagination: ties and mid-walk inserts (reused from S1).
- Subscription over `graphql-transport-ws` delivers an event consumed on another pod.
- Field-auth parity matrix against REST.

**BFF and SPA:**
- OIDC negative tests at `edge`'s callback: wrong `state`, wrong `nonce`, wrong `aud` (reuse the S9 cases).
- Cookie flags (`__Host-`, `Secure`, `HttpOnly`, `SameSite`); cross-origin POST refused; GET cannot mutate.
- RTL smoke tests; Playwright login → order → live "paid" with the no-token assertions.

The Channels and soak scripts are benchmarks under `bench/`, not tests.

---

## 7. CI changes

| Job | What it gates |
|---|---|
| `edge-tests` (path filter `services/edge/**`, `libs/atlas-events/**`) | Unit and integration tests for tickets, resume, backpressure, SSE, long poll, BFF session and GraphQL (cost, persisted-only, field auth, DataLoader counts), against real Valkey and RabbitMQ service containers |
| `edge-fanout-kind` | Deploys 2 edge replicas to a kind cluster (reusing S10's `kind-e2e` setup) and runs the cross-pod fan-out and rollout-resume tests |
| `graphql-schema-diff` | Exports the schema and fails on breaking changes against `main` |
| `playwright-bff` | The Playwright flow on kind: login → order → live "paid", plus the no-token assertions |
| `spa-build` | Type-checks and builds the SPA, extracts persisted-query hashes, and fails if an operation is missing from the allow-list |

Job names are suggestions; the gates are required. The E2E jobs are slow. Run them on PRs that touch `services/edge/**` or the SPA, and nightly on `main`.

---

## 8. ADRs and documents

### ADR-038 — Edge / BFF

ADR-038 follows the same rules as the extraction ADRs ([README §8.4](README.md#84-adrs)): numbers first, the "numbers don't hurt" clause, and a stated revert condition. Its gate is the Channels spike (at least 3 runs) instead of `bench/split-gate`, because `edge` is new code rather than a module moved out of `market`.

**Questions it must answer:**
- Why is realtime a new deployable instead of Channels inside `market`? What exactly does `edge` own (GraphQL, WS, SSE, `/session/*`), and what must it never own (business rules, a database)?
- Why FastAPI for `edge` (E1: thousands of sockets per pod, concurrent resolvers, holding the BFF session)?
- Why tickets for WebSockets when a cookie session exists?
- BFF cookie session vs a public PKCE SPA client: threat model (XSS, CSRF, token theft), refresh handling, operational cost.
- Does `edge` read AtlasPay data directly (REST `/v1/*` with `market`'s read-only `rk_` key) or through `market`, and why? Who holds the merchant credential in each option?
- What would revert the split? Name the numbers (for example, if `market` deploys became rare enough that the socket-drop cost fell below a stated budget).

**Numbers it must contain (ADR-002 protocol, at least 3 runs; 5 if you want them as strong as the split-gate ADRs):**
- the share of sockets dropped by one `market` deploy under Channels, the peak reconnects per second and the time to recover;
- memory per socket (from 5,000 idle sockets), Channels vs FastAPI;
- the product page before (the S10 waterfall, as confirmed in §4.3 step 3: call count and p95) and after (one round trip, ≤ 3 downstream calls, p95);
- fan-out delivery p95 and messages lost across a 30 s disconnect for pub/sub vs Streams.

**Counter-arguments to address:**
- "Channels keeps one codebase, one auth stack and one deploy. Make deploys rare and it wins" (E1). Answer with your deploy frequency and the drop numbers, or concede.
- "If the numbers don't hurt, say so." At synthetic load they may not. Then argue only from blast radius (a `market` deploy should not touch every live connection) or security scope (tokens and sessions live in one small service).

**Also record** the named future split, `edge` → BFF + realtime, and its trigger: BFF deploy churn dropping sockets beyond the budget.

### ADR-039 — GraphQL

**Questions it must answer:**
- Why Strawberry and not Graphene? Hint: compare release dates and declared framework support on each project's PyPI page ([graphene-django](https://pypi.org/project/graphene-django/), [strawberry-graphql](https://pypi.org/project/strawberry-graphql/)); when this plan was written, graphene-django's latest release was 3.2.3 (2024-07-10), declaring Django 3.2–4.2 only [verify]. Then look at how each library expresses types and how it mounts in FastAPI. You may add a schema-first library as a third column if you want.
- The DataLoader policy: per request, never global, and why.
- The cost model: how points are computed, list multipliers, the maximum depth, the per-client budget and the error returned.
- The persisted-query policy: prod only, how hashes are produced and deployed, what happens to an old SPA bundle after a deploy.
- Schema evolution: deprecate first, remove only after the diff check and a deprecation window.

**Numbers:** 51 → 2 calls; the cost and latency of the most expensive query the limits still allow; rejection counts during a hostile-query test.

**Counter-arguments:**
- "A REST BFF endpoint per page would do." It might. Answer with the number of page shapes you have and the field-selection argument, or concede.
- "GraphQL makes caching and idempotency awkward" (E4 says so for merchants). Explain why that does not apply to the storefront, and why AtlasPay stays REST.

### ADR-037 v2 — Transport decision record, finished (must)

S10 wrote ADR-037 v1 before GraphQL existed, with GraphQL as a placeholder. v2 is a dated update in the same file (v1 stays readable above it), and it completes the REST vs gRPC vs GraphQL comparison P9 and P10 started.

**It must contain:**
- the product page three ways: the REST waterfall measured in S10 (call count, p95; confirmed in §4.3 step 3), the GraphQL BFF (≤ 3 downstream calls, p95), and the "one REST BFF endpoint per page" alternative, argued from your page shapes rather than built;
- the decision per interaction, updated: browser ↔ `edge`, `edge` ↔ `market`, `edge` ↔ `inventory`, merchants ↔ AtlasPay, service ↔ service on the payment path;
- what number would change each decision.

### Documents

- `docs/design/realtime-transports.md`: the four-way comparison and the timeout table.
- `docs/learning/react-for-backend.md` (the §4.0 mapping table).
- `docs/sd/sd08-chat.md` and the SD7 whiteboard notes.
- `docs/privacy/data-governance.md`: add `ws:stream:*` and `sess:` to the PII inventory with their retention.
- Update the README architecture diagram to the S11 shape.

---

## 9. System design session

| SD | Built or whiteboard | When | What to reuse from Atlas |
|---|---|---|---|
| SD8 Chat | **Built** (storage S7, realtime here) | W49 (write-up) | Mongo `atlas_conversations` with per-conversation `seq`, `client_msg_id` dedup, Streams fan-out and resume, ticket auth, the bot as the offline push channel |
| SD7 News feed | Whiteboard | W49 | The "followed vendors" feed; whale vendors as the celebrity case; Streams per user as a small fan-out-on-write |

For SD8, the question to rehearse is the one the bank ends on: what happens to a recipient who is offline? You now have a concrete answer with evidence.

---

## 10. Interview questions this stage lets you answer

1. How does an update reach a socket on another pod?
2. SSE or WS for order status?
3. How do you authenticate a WS connection?
4. What is backpressure here?
5. How does DataLoader batch?
6. How do you rate-limit GraphQL fairly?
7. BFF session or a public SPA client?
8. Why did you not use Django Channels inside the monolith? What numbers would change your mind?
9. Redis pub/sub or Streams for fan-out: what does each lose, and when?
10. A client was offline for 10 minutes. How does it catch up without gaps or duplicates?
11. What happens to live connections during a deploy of `edge`? Of `market`?
12. Why must a DataLoader be per request?
13. How do you stop one GraphQL query from costing 10,000 backend calls?
14. Your GraphQL field is protected on one type. Can it leak through another path?
15. Why is long polling a poor fit for more than one consumer? (Anchor: the bot's `getUpdates` and the 409.)
16. What is cross-site WebSocket hijacking, and how does your handshake prevent it?

---

## 11. Common mistakes to watch for

1. **The long-lived JWT in the WebSocket URL.** Every proxy logs it (P7). Use a ticket.
2. **No heartbeat.** A dead socket looks like a quiet stream, and a Gateway idle timeout quietly cuts sockets at about a minute (P7).
3. **An unbounded buffer per socket.** One slow browser stalls the consumer or eats the pod's memory (P7).
4. **Treating pub/sub as durable.** It delivers only to whoever is connected at that instant. Reconnects and restarts lose messages.
5. **Streams without `MAXLEN` on a `noeviction` instance.** They grow until `redis-state` refuses writes, taking the limiter, FSM storage and sessions down with them.
6. **Reconnecting without jitter.** After a deploy, every client returns in the same second and the new pods and `auth` fall over.
7. **A global DataLoader.** It leaks one user's data to another and serves stale results.
8. **Rate-limiting GraphQL by request count.** One request can be one resolver call or ten thousand.
9. **Checking auth only at the top-level query.** Nested and alternative paths expose the field anyway.
10. **Tokens in `localStorage`.** Any XSS can read them. That is the whole reason for the BFF.

---

## 12. How real companies differ

- **Many teams buy realtime.** Managed services (Pusher- or Ably-style) or a Socket.IO cluster with a Redis adapter are common. At very large scale, chat products run a dedicated connection-gateway tier plus a presence service. Building it once by hand is still right here: you can now explain what those products do for you, and interviewers ask exactly that.
- **Fan-out at scale usually runs on a partitioned log** (Kafka or similar) with per-partition consumers, not Redis Streams per user. Redis Streams are the right size for Atlas and teach the same resume-by-offset idea.
- **Large organisations federate GraphQL** (Apollo Federation or schema stitching) so each team owns part of the graph. With one team and one BFF, federation would be ceremony (§13).
- **Many SPAs still use a public PKCE client** with tokens in memory, because it needs no server session. Security-sensitive products increasingly put a BFF or token-mediating backend in front. Atlas takes the stricter option because it holds payment data.
- **Sticky sessions at the load balancer** are sometimes used instead of cross-pod fan-out. They reduce cross-pod traffic, but they do not remove the problem: events are still produced on other pods.

---

## 13. Deliberately not doing

| Item | Why | When it arrives |
|---|---|---|
| Apollo Federation | One team, one BFF; federation solves an organisational problem Atlas does not have | Not in Season 1 |
| Mobile apps | The SPA and the Telegram bot cover the clients the lessons need | Not planned |
| End-to-end encryption of chat | `market` must read messages for dispute evidence in Admin (S7) | Not planned |
| Splitting `edge` into a BFF and a realtime service | No measured need yet | Trigger: BFF deploy churn dropping sockets beyond the budget (E2 named future splits) |
| A managed realtime service | The lesson is the mechanics | Named in ADR-038 as the "buy" option |
| Kafka for fan-out | Streams give replay by id at this scale | Season 2 (CDC and streaming) |
| Browser push notifications for offline users | The bot already notifies offline users | Not planned |

---

## 14. Stretch

Only when the must tier closes early.

| Item | Hours | Notes |
|---|---|---|
| Telegram Mini App `initData` verification | 1 | Verify the HMAC over the sorted data-check string. The secret key is derived by HMAC-SHA256 of the bot token keyed with the constant string `WebAppData`. Compare it with the S10 Login Widget check, which uses SHA256(bot_token) as the key, and write down why the two schemes differ. Add an `auth_date` freshness check. |
| Presence and unread badges | 1 | Presence with a TTL heartbeat key; unread counts from the S7 Mongo aggregation, updated live |
| SSE fallback for the dashboard | 1 | For networks that block WebSocket upgrades; same stream ids, so resume still works |
| Offline catch-up UI | 0.5 | What the user sees when the resume id has been trimmed: a snapshot refetch with a visible "catching up" state |
| A CDN for the SPA assets | 0.5 | Put the cloud provider's CDN in front of the hashed assets of the k3s deploy; `index.html` stays short-lived or uncached. Record the cache-hit ratio and what a deploy must do so no browser gets a new `index.html` pointing at assets the CDN cannot serve. This is the CDN that SD10 whiteboards; Atlas builds it only here and only as stretch. |

---

## 15. Definition of done

- [ ] The §4.0 ramp done in `sandbox/react-ramp/`; `docs/learning/react-for-backend.md` written.
- [ ] `docs/evidence/s11/channels-deploy-drop.csv` and `memory-5000-sockets.csv` committed (ADR-002 metadata).
- [ ] ADR-038 accepted, with all required numbers, the Channels counter-argument, the "numbers don't hurt" clause, the BFF vs public-client comparison and the revert condition.
- [ ] ADR-039 accepted, with the cost model and the persisted-query policy.
- [ ] ADR-037 v2 (dated) accepted: the product page as REST waterfall vs GraphQL BFF with measured numbers, and the per-interaction decision updated.
- [ ] The live dashboard works across pods: `fanout-missing.csv` and `pubsub-vs-streams.csv` show your predictions, the loss you reproduced, then 0.
- [ ] Chat resumes after a reconnect with no gap and no duplicate; a duplicate `client_msg_id` yields one message.
- [ ] A slow client is dropped without stalling others (`backpressure.csv`).
- [ ] An `edge` rollout under the soak client loses 0 messages (`edge-rollout.csv`).
- [ ] SSE payment status resumes with `Last-Event-ID`; the `/poll/*` endpoint resumes with `after`.
- [ ] `docs/design/realtime-transports.md` has the four-way comparison measured on one rig (short poll, long poll via `/poll/*` with `getUpdates` as the anchor, SSE, WS) and the timeout table.
- [ ] The S10 waterfall baseline is confirmed on today's rig (or re-measured); the product list takes 2 calls (51 → 2) and the full product page ≤ 3 downstream calls (`dataloader-calls.csv`).
- [ ] Over-cost queries are rejected before execution; persisted-only is enforced in prod; the field-auth parity matrix passes.
- [ ] The SPA holds no tokens; Playwright login → order → live "paid" is green on kind.
- [ ] CI: `edge-tests`, `edge-fanout-kind`, `graphql-schema-diff`, `playwright-bff` and `spa-build` (or your equivalents) required and green.
- [ ] `docs/privacy/data-governance.md` updated for `ws:stream:*` and `sess:`.
- [ ] `docs/sd/sd08-chat.md` and the SD7 notes written.
- [ ] Postmortem paragraph in `docs/postmortems/`: what you predicted for the Channels numbers and the fan-out loss, what happened, what went to `docs/deferred.md`, and this stage's actual hours against the 36 h budget (`docs/hours.csv`).
- [ ] STAR story 1 in `docs/star/`: **the updates that went missing across pods**.
- [ ] STAR story 2 in `docs/star/`: **the Channels socket drop**.
- [ ] Tag `v0.11` created by you.

---

## 16. If you get stuck

**4.0 React and TypeScript ramp**
- A component does not re-render when your data changes. Did you change the state through its setter, or mutate the object in place?
- TypeScript complains about a value that "might be undefined". Which union does it have, and where do you narrow it (a loading/error/data check before you use it)?
- The number of sockets in dev is not what you predicted. What does `StrictMode` do to effects on mount, and does your cleanup close every socket the effect opens?
- Reread: React's [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects) and [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect).

<details>
<summary>Check your prediction (open after your StrictMode line is written)</summary>

- In dev with `StrictMode`, React mounts each component, runs its cleanup, and mounts it again, so the effect runs twice and two sockets open. The first one closes only if your cleanup closes it. A production build runs the effect once. The lesson for §4.4: every effect that opens a live connection must be safe to run twice.

</details>

**4.1 Channels spike**
- The soak client stops at around 1,000 sockets. What does `ulimit -n` say inside the client's container, and inside the server's?
- The deploy did not drop sockets. Did the rollout actually replace pods? Were the sockets connected to the pods that were replaced?
- Why did you choose that Redis instance for the channel layer? What happens to an in-flight group message under `allkeys-lru`?
- Reread: [P7 D115–D120](../python/07-fleettrack.md) (the WebSocket build and what Nginx needed) and E1's `edge` row in the [README](README.md).

<details>
<summary>Check your prediction (open after both 4.1 CSV files are committed)</summary>

- **Deploy drop.** A socket lives in one process. Every socket on a pod that the rollout replaces is closed, and a normal rollout replaces every pod, so expect close to 100% of sockets to drop over the rollout. The clients then reconnect almost at once, so the new pods and `auth` (token checks on the handshake) see a spike. If your numbers differ, look at how many pods the rollout replaced and whether your clients reconnect with jitter.
- **Memory.** There is no fixed ratio to expect; the point is that you predicted one and measured it with the same limits for both stacks. If Channels is much heavier, check whether you counted the separate ASGI process type's baseline memory as well as the per-socket growth.

</details>

**4.2 Realtime**
- Updates are missing with two pods. Draw the path of one event from `edge.fanout` to a browser. Which pod consumed it? Which pod holds the socket?
- Resume produces duplicates at the seam. In which order do you (a) start listening for live pings and (b) read the backlog? What does the client do with an id it has already processed?
- Resume produces a gap. Is your range exclusive or inclusive of the last id? Is the snapshot tagged with the stream id it was taken at?
- The slow client still stalls others. Does the fan-out loop ever `await` a send on a particular socket?
- Sockets die every 60 s. Which timeout on the path is 60 s, and is your heartbeat shorter?
- A long poll returns a 504 before its 25 s hold ends. Which timeout in your table is shorter than 25 s?
- Reread: [P7 D115–D120](../python/07-fleettrack.md) (bounded send queue, `Last-Event-ID`, the comparison table); [phase-5 D117](../../phase-5-scaling-architecture.md) (the polling baseline).

<details>
<summary>Check your prediction (open after the fan-out and backpressure predictions are committed)</summary>

- **Step a.** With 2 competing consumers and sockets spread over both pods, about half of the updates never arrive: pod A consumes an event, and the user's socket is on pod B.
- **Step b.** 0 missing, as long as every client stays connected.
- **Step c.** With pub/sub alone, everything sent during the 30 s gap and during the pod restart is gone. Pub/sub is fire-and-forget: a message reaches only the subscribers connected at that instant.
- **Step d.** 0 missing across the same gap and restart: the stream keeps the events, and the client resumes from its last id.
- **Backpressure.** With an unbounded queue per socket, the pod's memory grows for as long as the slow client stays connected. If the fan-out loop ever awaits a send on that one socket, delivery to every other client stalls behind it too.

</details>

**4.3 GraphQL**
- The waterfall p95 is barely worse than the BFF's. Are the calls really sequential in the S10 probe, and does your rig add any network latency between client and backends? On one laptop, a round trip costs almost nothing; say so in ADR-037 v2 and argue from the call count and the mobile-network case.
- You still see 51 calls. Is the loader created per request and actually shared by all resolvers in that request, or created inside each resolver?
- The batch returns wrong vendors for some products. Does your batch function return results in the order of the keys it received?
- The cost limit rejects your own SPA queries. Did you size list multipliers from real `first` values? Is the budget per client or global?
- Field auth passes the direct test but the indirect path leaks. Where is the check attached: to the query root or to the field?
- Reread: [P10 D166–D168](../python/10-atlasmarket.md) (GraphQL BFF: "measure both"); [P9 D151–D153](../python/09-payflow.md) (the transport decision record it extends).

**4.4 React SPA and BFF**
- Login loops back to the login page. Is the cookie `Secure` on a plain-HTTP dev host? Does `SameSite` block the cookie on the redirect back from `auth`?
- The SPA works locally but not on kind. Is the SPA on the same origin as `/graphql`, or did CORS come back?
- Where exactly does the refresh token live? If you can find it in DevTools, it is in the wrong place.
- Reread: [P5 D85–D90](../python/05-carepoint.md) (CORS preflight, OIDC state/nonce/aud, PKCE); [P10 D157–D161](../python/10-atlasmarket.md) (storefront scaffold, TanStack Query).

**4.5 SD sessions**
- For SD8, which part of your build would break first at 100× connections: file descriptors, Redis Streams memory, or `market`'s write path for `seq`?
- For SD7, why does fan-out-on-write fail for a whale vendor? What number makes you switch to a hybrid?
