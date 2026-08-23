# System Design Practice — Full Problem Bank

19 classic system-design interview problems (SD1–SD19), worked one or two
at a time across Weeks 19–28 of the roadmap — Phase 5's scaling/
architecture weeks and Phase 6's capstone weeks — plus a 20th closing
exercise on the Saturday of Week 28 that isn't a bank problem: design
AtlasMarket itself, from a blank page, then compare your answer to the
actual system you spent 30 weeks building. Three of the nineteen (SD1,
SD2, SD14) don't stop at the paper design — Phase 6 Weeks 29-30 build
each one for real as Projects 26-28, the payoff for having designed them
carefully here first. Each phase file's "Weekly Interview Question Sets"
section names exactly which problems land in which week; this file is the
detail behind those pointers, the same relationship `dsa-problems.md` has
to the daily DSA column.

Each entry gives the ask and what to cover — not a reference solution.
System design doesn't have one correct answer the way a LeetCode problem
does; the point is defending a set of trade-offs out loud, the same way
the mock interviews in Phase 6 Week 28 already had you do once. For every
problem, work through the same skeleton before going deep on any one part:

1. **Clarify scope** — write down the 3-5 functional requirements you're
   actually solving for, and explicitly state what's out of scope.
2. **Estimate scale** — back-of-envelope numbers for read/write QPS,
   storage growth per year, and peak-to-average ratio. Wrong numbers are
   fine; no numbers is the mistake.
3. **High-level design** — boxes and arrows, one paragraph per box, before
   any deep dive. If you can't draw it in under 5 minutes, the design is
   still too vague to defend.
4. **Data model** — the 2-4 core tables/collections and their keys, not a
   full schema.
5. **Deep dive** — pick the ONE hardest part of the system (named per
   problem below) and actually solve it, with numbers.
6. **Trade-offs** — the 2-3 questions an interviewer would push on, and
   your honest answer, including "I'd need to measure this in production."

Where a problem clearly rhymes with something you already built earlier in
the roadmap, that's named explicitly — use the real system as evidence,
the same discipline Phase 6's mock interviews already established.

---

## Week 19 — Warm-Ups (Phase 5, Outbox Pattern week)

### SD1 — Design a URL Shortener
*Category: Warm-up · Deep-dive: ID generation & redirect latency*

Design a service like bit.ly: given a long URL, return a short one; given
the short one, redirect to the original. Cover: how you generate short
codes (counter + base62 vs hash-based vs random — and the collision
handling each implies), whether redirects are 301 or 302 and why that
matters for analytics, how you'd shard the mapping table at 100M URLs/day,
and how you'd cache hot redirects without serving a stale mapping after a
URL is deleted. **Built for real in Phase 6, Week 29 (Project 26)** — the
paper design here is a prediction you get to check against reality in
five weeks.

### SD2 — Design a Rate Limiter
*Category: Infra primitive · Deep-dive: algorithm choice under distribution*

Design a rate limiter that can sit in front of any API (think: the
`UserRateThrottle` you built in Phase 2's QuickServe checkout, generalized
to a standalone service). Cover: token bucket vs leaky bucket vs
fixed-window vs sliding-window-log vs sliding-window-counter — the actual
memory/accuracy trade-off of each — and how the limiter stays correct
when it's replicated across 5 API gateway instances instead of living in
one process's memory (this is where Redis-backed counters come in).
**Built for real in Phase 6, Week 29 (Project 27)** — including the
actual multi-instance race this paper design only gets to assert about.

---

## Week 20 — Real-Time & Fan-Out (Phase 5, CQRS/Saga/WebSocket week)

### SD7 — Design a News Feed / Timeline
*Category: Fan-out at scale · Deep-dive: push vs pull*

Design a Twitter/Instagram-style home timeline. Cover: fan-out-on-write
(precompute each follower's feed when a post is made) vs fan-out-on-read
(compute the feed at request time by merging followees' posts) — and the
hybrid most real systems land on once a celebrity account with 50M
followers breaks pure fan-out-on-write. This is the deep-dive: walk
through exactly why the celebrity case forces the hybrid, with numbers.

### SD8 — Design a Chat System
*Category: Real-time · Deep-dive: message delivery & ordering*

Design a WhatsApp/Messenger-style 1:1 and group chat system. Cover:
WebSocket connection management at scale (a gateway layer routing a user
to whichever server holds their live connection — this is exactly what
this same week's FleetTrack WebSocket-push stretch mini-project has you
build a small, real version of), message ordering and at-least-once
delivery with client-side dedup (the same idempotent-consumer discipline
from Phase 3/6, applied to chat messages instead of events or webhooks),
and how you handle a recipient who's offline (store-and-forward + push
notification).

---

## Week 21 — Search-Shaped Systems (Phase 5, Elasticsearch week)

### SD5 — Design a Web Crawler
*Category: Batch/large-scale system · Deep-dive: politeness & dedup at scale*

Design a web crawler that can index a meaningful fraction of the web.
Cover: the URL frontier (a priority queue balancing freshness vs
politeness-per-domain), how you avoid re-crawling or double-processing the
same URL at billions-of-pages scale (a Bloom filter is the standard
answer — say why a plain hash set doesn't work at that size), and how you
respect `robots.txt` and rate-limit per domain without one slow domain
stalling the whole crawl.

### SD15 — Design a Typeahead/Autocomplete Service
*Category: Read-heavy, low-latency · Deep-dive: prefix matching at scale*

Design the search-box suggestions you see typing into Google or Amazon's
search bar. Cover: a Trie as the core data structure (you built one from
scratch in Track A's Week 11 DSA problems — this is that structure's real
job), how you rank suggestions by popularity/recency instead of just
alphabetically, how you keep p99 latency under ~50ms when every keystroke
fires a new request (client-side debouncing — the exact pattern DocuVault's
search page already uses from Phase 5 — plus server-side caching of hot
prefixes), and how the suggestion index gets refreshed without a full
rebuild every time.

---

## Week 22 — Distributed Systems Primitives (Phase 5, Kubernetes/Consensus/Sharding week)

### SD3 — Design a Distributed Cache
*Category: Infra primitive · Deep-dive: eviction & cache-instance failure*

Design something like Memcached: a distributed, in-memory key-value cache
sitting in front of a database. Cover: eviction policy (LRU vs LFU — you
already built an LRU by hand in Track A's Week 8 DSA problem, so ground
this in that), how clients pick which cache node owns a key (this is where
consistent hashing, built this same week, would replace naive
`hash(key) % N`), and what happens to your app's latency and DB load the
instant one cache node dies.

### SD4 — Design a Key-Value Store (Dynamo-Style)
*Category: Distributed storage · Deep-dive: replication & conflict resolution*

Design a distributed key-value store like DynamoDB/Cassandra/Riak — not a
cache, a system of record. Cover: partitioning (consistent hashing again —
you build the ring yourself this same week, Friday), N/W/R quorum-style
replication and what W+R > N actually buys you, and how you'd resolve two
replicas disagreeing on a value after a network partition heals (vector
clocks or last-write-wins — state which you'd pick and why).

### SD6 — Design a Unique ID Generator (Snowflake-Style)
*Category: Infra primitive · Deep-dive: clock skew & ordering guarantees*

Design a service generating unique, roughly-time-sortable IDs across many
machines with no central coordinator (Twitter's Snowflake is the canonical
reference). Cover: the bit layout (timestamp + machine ID + sequence),
why a central auto-increment counter doesn't scale here, what happens if a
machine's clock skews backward (this is the deep-dive — walk through the
failure and your mitigation), and where you'd actually use this vs. a
plain UUID (hint: index locality on the primary key — a callback to Phase
1's B-tree indexing work).

### SD14 — Design a Distributed Job Scheduler
*Category: Infra primitive · Deep-dive: exactly-once execution*

Design a system like a distributed cron: schedule a job to run once, or on
a recurring schedule, exactly once, even though the scheduler itself runs
on multiple machines for availability. Cover: leader election so only one
scheduler instance actually dispatches a given job at a time (a direct,
concrete application of this same week's Raft/etcd work, Tuesday — name
exactly how it applies here), how a dispatched-but-crashed job gets
retried without also double-running if it actually succeeded just before
crashing (idempotent job handlers, same discipline as every queue
consumer you've built since Phase 3), and how this compares to what Celery
Beat (Phase 3) and Prefect (Phase 10) already give you off the shelf.
**Built for real in Phase 6, Week 30 (Project 28)** — reusing Phase 5's
from-scratch Raft implementation as the actual leader-election mechanism,
not a paper hand-wave.

---

## Week 25 — Correctness Under Concurrency (Phase 6, PayFlow week)

### SD18 — Design a Payment System
*Category: Correctness-critical · Deep-dive: idempotency & reconciliation*

Design a Stripe-style payment processing system — the general version of
PayFlow, which you're building this same week. Cover: the same
idempotency-key mechanic you're implementing for real (state it precisely,
from memory, no notes), double-entry ledger accounting as the source of
truth for money movement (LedgerBase's model, generalized), and
reconciliation — how you'd detect and resolve a payment your system thinks
succeeded but the provider's records disagree with, days later. This is
the one problem in the whole bank where you have direct, shipped,
load-bearing experience — treat it as a rehearsal for an interviewer
saying "now design the thing you just told me you built."

### SD12 — Design a Ticket-Booking System
*Category: High-contention writes · Deep-dive: overselling prevention*

Design a Ticketmaster-style system for a high-demand on-sale event: 50,000
people trying to buy 20,000 seats for a popular show in the first minute.
Cover: how you prevent the same seat being sold twice under extreme
concurrency (this is CarePoint's `EXCLUDE`-constraint pattern from Phase 4
and StockPilot's row-locked stock decrement from Phase 1, both scaled up —
name which one generalizes better here and why), a short-lived seat "hold"
during checkout with an expiry (what happens to abandoned holds?), and a
virtual waiting room to shed load before it ever reaches the booking path.

---

## Week 26 — Infra From the Other Side (Phase 6, Security/Cloud/Reliability week)

### SD9 — Design a Notification System
*Category: Fan-out + multi-channel · Deep-dive: provider failure & retries*

Design a system that sends notifications (push, SMS, email) triggered by
events across many other services — the generalized version of the
Celery-based reminder jobs you've built for PeopleOps, CarePoint, and
LedgerBase all year. Cover: a queue-backed worker pool per channel so one
slow provider (SMS gateway down) doesn't block email, retry-with-backoff
per provider (a direct callback to Phase 4's resilience work), and how you
prevent duplicate notifications when the triggering event is delivered
more than once (idempotency keyed on event ID, same pattern as PayFlow's
webhook handling).

### SD17 — Design Distributed File Storage
*Category: Large-scale storage · Deep-dive: chunking, replication, metadata*

Design a Dropbox/S3-style object storage system. Cover: chunking large
files for storage and dedup (two users uploading the identical file should
ideally not double the storage), replication factor and placement across
failure domains (same "how many copies, spread how" reasoning as SD4's
Dynamo-style quorum, applied to bulk objects instead of small values), and
the split between a metadata service (small, fast, strongly consistent —
your own DocuVault Postgres layer from Phase 5 already plays exactly this
role) and the bulk data store (large, eventually-consistent-is-fine, S3/
MinIO — which you've already used since Phase 4).

### SD19 — Design a Distributed Logging & Metrics Pipeline
*Category: Observability infra · Deep-dive: high-volume ingestion*

Design the system underneath Prometheus/Grafana/Sentry — the tools you've
been using since Phase 4, from the other side. Cover: how logs/metrics get
shipped off a fleet of app servers without the shipping itself becoming a
bottleneck (local buffering + async batched send, sampling under extreme
volume), a time-series-optimized storage model and why it differs from a
row-store like Postgres (columnar, downsampling older data — ties back to
Phase 11's BigQuery partitioning/clustering reasoning), and how alerting
stays fast (seconds, not minutes) without every alert rule re-scanning raw
data from scratch.

---

## Week 27 — Geospatial & Collaborative Systems (Phase 6, AtlasMarket/Storefront week)

### SD11 — Design a Ride-Sharing Service
*Category: Geospatial + real-time matching · Deep-dive: driver-rider matching*

Design an Uber/Lyft-style service: riders request a trip, nearby drivers
get matched, both parties see live location updates. Cover: geospatial
indexing for "find nearby drivers" (geohashing or a quadtree — state
which and why), the matching algorithm's trade-off between "nearest
driver" (greedy, fast) and "best overall assignment" (batched, slower,
better utilization), and how driver-location updates stream to the rider
in near-real-time without polling (the same WebSocket-vs-polling decision
from FleetTrack's dispatcher dashboard, Phase 5 Week 22).

### SD13 — Design a Collaborative Document Editor
*Category: Real-time sync · Deep-dive: conflict-free concurrent edits*

Design a Google Docs-style system where multiple people edit the same
document simultaneously and see each other's changes in near-real-time.
Cover: Operational Transformation vs CRDTs as the two real approaches to
merging concurrent edits without a lock — explain in your own words why
"just lock the document while someone's editing" fails the actual
requirement, how changes propagate to other connected clients (WebSockets
again — by now this should feel like a recurring, load-bearing pattern,
not a one-off), and how a client that was offline for 10 minutes
reconciles its local edits against everyone else's on reconnect.

---

## Week 28 — Large-Scale Media & Closing Marathon (Phase 6, Mock Interviews/Wrap week)

### SD10 — Design a Video Streaming Platform
*Category: Large media + CDN · Deep-dive: adaptive bitrate & CDN placement*

Design a YouTube/Netflix-style platform: upload, transcode, and stream
video to millions of concurrent viewers. Cover: async transcoding into
multiple resolutions/bitrates after upload (a queue-driven pipeline, the
same shape as Phase 4's presigned-upload-then-process pattern, just with a
transcoding worker instead of a direct read), adaptive bitrate streaming
(the player switches quality based on measured bandwidth — explain the
manifest file's role), and why almost none of the actual video bytes
should ever touch your own servers at request time (CDN edge caching,
tying back to the "load balancers, CDN, CAP theorem" system-design
deep-dive named all the way back in Phase 5's Learning Goals).

### SD16 — Design a Proximity / Nearby-Search Service
*Category: Geospatial · Deep-dive: spatial indexing trade-offs*

Design a Yelp-style "find businesses near me" service. Cover: geohashing
vs quadtrees vs an R-tree for spatial indexing — the actual trade-off
between them for this access pattern, not just naming all three — how you
handle a dense urban area vs. a sparse rural one with the same index
without either becoming a hotspot, and how results get re-ranked by more
than pure distance (rating, open-now status) without breaking the spatial
index's efficiency.

---

## Week 28, Saturday — Closing Synthesis (not a bank problem)

### SD20 — Design AtlasMarket, From Scratch
Close the marathon the way Phase 6's Week 28 mock interviews previewed:
design AtlasMarket — a multi-vendor marketplace with vendor-scoped catalog
search, cross-vendor checkout, per-vendor payouts, and fulfillment
tracking — on a blank page, 45 minutes, no notes, no looking at your own
repo. Then, and only then, open `docs/architecture.md` from Phase 6 and
compare. Write down every place your fresh design differs from what you
actually shipped, and for each difference, decide honestly: was the real
system right, or would you build it differently today with everything
you've learned since Phase 6? This becomes the centerpiece answer for "walk
me through a system you built" in a real interview — not because it's
polished, but because you can defend every disagreement with your own past
self.
