# Hono Performance Hotspot Assessment

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

**Repository:** `hono` @ `f6fbaf02` (package version `4.13.18`)
**Scope:** the server request path (`Hono#fetch` → routing → `Context` → middleware → `Response`) plus the shared utilities it calls.
**Method:** static review of the hot-path source, cross-checked against the repository's existing benchmark harnesses. No runtime measurements were executed for this assessment; the plan at the end defines how to confirm and quantify each item. Runtimes available locally: Node.js `24.18.0` (`.tool-versions` requests `24.21.0`), Bun is not installed in this clone.

## Hotspots at a glance

- **H1 — Per-request `Context` closure allocation (high, high confidence):** `Context` is built for every request (`src/hono-base.ts:437-446`) and initializes ~15 arrow-function fields per instance (`src/context.ts:448-798`), so tiny responses still pay ~15 function allocations. See [§1](#1-every-request-allocates-a-context-plus-15-bound-closures).
- **H2 — `compose()` rebuilt per request (high, high confidence):** every multi-handler route creates a fresh composer and a `next` closure plus an `await` hop per middleware layer (`src/hono-base.ts:449-469`, `src/compose.ts:20-71`). See [§2](#2-compose-is-created-per-request-and-adds-a-promise-hop-per-middleware).
- **H3 — Cold-start router build and path matching (high for cold start, medium steady state):** matchers are lazily built on first use, replaying all routes (`src/router/smart-router/router.ts:21-61`, `src/router/reg-exp-router/router.ts:86-139`); the repository's own harness notes a >500 µs first request (`benchmarks/fetch/bench.mts:83-84`). See [§3](#3-cold-start-routing-build-and-per-request-path-matching).
- **H4 — Response/header cloning after `next()` (medium-high):** the `res` setter and `header()` re-wrap `Response`/`Headers` when middleware decorates a finalized response (`src/context.ts:414-434`, `:519-524`, `:609-657`), as compress does (`src/middleware/compress/index.ts:122-126`). See [§4](#4-response-assembly-clones-responseheaders-when-middleware-touches-headers-after-next).
- **H5 — Body representations retained/rebuilt (medium-high, size-sensitive):** `json()` caches the full text and then parses it (`src/request.ts:217-244`, `:258-260`); form parsing buffers the whole body (`src/utils/body.ts:126-146`). See [§5](#5-request-body-caching-keeps-multiple-representations-and-buffers-whole-payloads).
- **H6 — Uncached query parsing (medium):** every `c.req.query()` call re-scans the URL, runs regex tests, and allocates a result object (`src/request.ts:145-149`, `src/utils/url.ts:248-343`). See [§6](#6-query-parsing-is-uncached-every-call-re-scans-the-url).
- **H7 — Small helper allocations (low-medium):** `c.var` calls `Object.fromEntries` per access and route helpers remap the match array per call (`src/context.ts:598-607`, `src/helper/route/index.ts:32-59`, `src/request.ts:445-447`). See [§7](#7-lower-priority-per-call-allocations-in-helpers).

---

## Hotspots

### 1. Every request allocates a `Context` plus ~15 bound closures

`Context` is constructed unconditionally for each request in `Hono#dispatch` (`src/hono-base.ts:437-446`). Its constructor only assigns options (`src/context.ts:352-363`), but the class declares many arrow-function fields. Because TypeScript targets ES2022 (`tsconfig.base.json:4`), these are instance fields initialized for **every** `new Context(...)`:

- `render` (`src/context.ts:448`), `setLayout` (`:459`), `getLayout` (`:472`), `setRenderer` (`:495`)
- `header` (`:519`), `status` (`:534`), `set` (`:551`), `get` (`:576`)
- `newResponse` (`:659`), `body` (`:682`), `text` (`:700`), `json` (`:726`), `html` (`:741`), `redirect` (`:768`), `notFound` (`:794`)

**Why it matters:** a minimal `GET /` that returns `c.text('Hi')` still pays for one `Context` object plus approximately 15 function objects before the handler runs. That is pure allocation/GC pressure that grows linearly with RPS and is disproportionate for the small responses Hono is optimized for. It also raises per-request memory on edge runtimes.

**Counter-evidence / do not over-correct:** `c.text()` deliberately avoids building `Headers` and uses a direct `new Response(text)` fast path when nothing has been prepared (`src/context.ts:700-712`). Any optimization must preserve that path.

**Evidence to collect:** allocation profile of `ping GET /`; objects/request and GC cycles at steady state; compare against a build where these methods live on the prototype and bind `this` only when needed.

### 2. `compose()` is created per request and adds a promise hop per middleware

The single-handler fast path avoids composing (`src/hono-base.ts:449-467`), but as soon as a route matches more than one handler — i.e. any app with global middleware — `compose()` is invoked on every request (`src/hono-base.ts:469`). `compose()` returns a fresh closure and a fresh `dispatch` function per call (`src/compose.ts:20-23`), and for each layer it allocates another `() => dispatch(i + 1)` closure (`src/compose.ts:51`). Each layer is `await`ed (`:51`), so even synchronous middleware adds microtask scheduling.

Additional per-dispatch work: `middleware[i][0][0]` nested indexing (`src/compose.ts:42-44`) and the `res`/`isError`/`handler` locals (`:38-47`).

**Why it matters:** `app.use('*', logger)`, auth, CORS, request IDs, etc. are common; a 5-middleware chain allocates at least 6 closures and 6 promises per request in addition to the handler's own work. This is likely the largest fixed overhead for real applications.

**Evidence to collect:** the existing `middleware GET /mw/hello` case in `benchmarks/fetch/bench.mts`; extend it to 0/1/5/10 middleware and compare against a pre-composed dispatch per route.

### 3. Cold-start routing build and per-request path matching

**Cold start.** `RegExpRouter.match` builds all matchers lazily on first use and then replaces itself (`src/router/reg-exp-router/matcher.ts:10-32`). Building is proportional to registered routes: it iterates every method and path, runs `path.match(regexp)` for static entries, and sorts handler indexes (`src/router/reg-exp-router/router.ts:86-139`). Static registration also splits each path into characters (`src/router/reg-exp-router/trie.ts:12-19`). `SmartRouter` adds another replay of every route into each candidate router before binding the winner (`src/router/smart-router/router.ts:21-61`).

The repository itself documents the size of this: `benchmarks/fetch/bench.mts:83-85` says *“the first fetch builds the router lazily (>500µs)”*. `PreparedRegExpRouter` exists specifically to move this cost out of the request (`src/router/reg-exp-router/prepared-router.ts:9-17`), which confirms the concern.

**Steady state.** Static routes hit an O(1) null-prototype object lookup (`src/router/reg-exp-router/matcher.ts:17-20`) — already good. Dynamic routes run the router's combined regex and then `match.indexOf('', 1)` (`:22-28`), cost growing with route-table complexity. Before matching, `getPath` scans the URL character by character (`src/utils/url.ts:109-150`); any `%` sends it into a slower branch with extra `indexOf`/regex work (`:115-143`).

**Why it matters:** serverless/edge cold starts and first-request latency are product-visible; percent-encoded paths and dynamic routes are common in APIs. Optimizing static-route matching would be wasted effort.

**Evidence to collect:** first-request vs warm latency; `bench-includes-init:*` for construction cost; `benchmarks/utils/src/get-path.ts` plus a path-length/encoding sweep.

### 4. Response assembly clones `Response`/`Headers` when middleware touches headers after `next()`

- The `res` setter wraps the incoming response and re-copies every existing header, including a special `set-cookie` loop (`src/context.ts:414-434`).
- `header()` clones the current `Response` whenever the context is already finalized and its body is unused (`src/context.ts:519-524`).
- `#newResponse` copies `new Headers(this.#res.headers)` if a response already exists, then merges header records (`src/context.ts:609-657`).
- Built-in middleware does exactly this after `next()`: compress reads `ctx.res` several times and assigns `new Response(ctx.res.body.pipeThrough(stream), ctx.res)` (`src/middleware/compress/index.ts:122-126`).

**Why it matters:** CORS, secure-headers, compress, etag, and user middleware that decorate a response after `next()` can each trigger one or more full `Response`/`Headers` constructions per request. Cost scales with header count and can turn a cheap handler into a multi-allocation response path. The `c.text` fast path (`src/context.ts:700-712`) currently sidesteps most of this when unused, so regressions here are easy to miss.

**Evidence to collect:** response-decorating middleware benchmark; count `new Response`/`new Headers` constructions; sweep header counts 1/10/50.

### 5. Request-body caching keeps multiple representations and buffers whole payloads

`HonoRequest.#cachedBody` stores the first representation in `bodyCache` for the request lifetime (`src/request.ts:217-244`). If a different representation is requested, it rebuilds a `Response` from the cached body and re-decodes (`:225-241`).

Notably:

- `json()` is implemented as `this.#cachedBody('text').then(JSON.parse)` (`src/request.ts:258-260`), so the full UTF-8 string **and** the parsed object coexist (the string stays in `bodyCache`).
- `arrayBuffer()` materializes the entire body (`src/request.ts:290-292`); `bytes()` then creates a `Uint8Array` view over that buffer (`:306-308`).
- `parseBody` for form data reads the whole `arrayBuffer()` and converts it in memory (`src/utils/body.ts:126-146`), with separate parsing/all-values/nested passes (`:160-199`).

**Why it matters:** for 1–10 MB uploads or JSON payloads, peak memory is a multiple of the payload, and the retained text representation extends the lifetime of the largest allocation. This is the hotspot most sensitive to payload size rather than request count.

**Evidence to collect:** payload-size sweep (1 KB / 100 KB / 1 MB / 10 MB) measuring p50 latency, peak RSS, and time in GC; compare `c.req.json()` against `text()` + one-shot parse.

### 6. Query parsing is uncached; every call re-scans the URL

`HonoRequest.query()`/`queries()` call `getQueryParam`/`getQueryParams` directly on every invocation (`src/request.ts:145-149`, `:166-168`). `_getQueryParam` has a fast path for an unencoded single key, but it still re-scans from the hash check (`src/utils/url.ts:253`) through the query string, runs `/[%+&=]/` / `/[%+]/` regex tests (`:260`, `:291`, `:299`), slices values, and allocates a null-prototype result object (`:298`). The no-key form decodes every key and value (`:308-339`).

**Why it matters:** a handler that reads `limit`, `offset`, and `sort` separately re-parses the same URL three times. Handlers that call `c.req.query()` allocate a complete object per call. This is avoidable with a per-request parsed cache.

**Evidence to collect:** `benchmarks/query-param` with 1/5/20 parameters; add a repeated-call scenario (`query('a')`, `query('b')`, …) and a `query()`-all scenario.

### 7. Lower-priority per-call allocations in helpers

- `c.var` returns `Object.fromEntries(this.#var)` on every property access (`src/context.ts:598-607`), allocating a new object even when only one variable is read.
- `matchedRoutes` maps the entire match result on every call (`src/helper/route/index.ts:32`); `routePath`/`baseRoutePath` call it and then `.at(...)` (`:58-59`, `:82-83`); the deprecated `HonoRequest.routePath` maps again (`src/request.ts:445-447`). `Hono#mount` calls `routePath(c)` per request (`src/hono-base.ts:387`).
- `#getAllDecodedParams` allocates `Object.keys(...)` plus a result object each call (`src/request.ts:109-121`).

**Why it matters:** noticeable mainly with request logging/tracing, mounted sub-apps, or repeated `c.var.x` access, not on the bare path. Worth fixing alongside the higher-priority items, not before them.

**Counter-evidence:** `getPattern` already caches compiled patterns (`src/utils/url.ts:50-78`), and `Route`/`mount` are not on every request unless used. Do not attribute framework-wide cost to these helpers.

---

## Measurement plan

### 0. Establish a trustworthy baseline

1. Pin the environment: record CPU model, OS, Node/Bun versions, commit SHA, and whether the machine is on battery. Prefer the repository's `.tool-versions` (`Node 24.21.0`, `Bun 1.2.19`); install Bun or record that results are Node-only.
2. Run each variant in a **fresh process** so JIT tier-up and GC state do not leak between cases. The existing `benchmarks/fetch/compare.sh` already does this and reverses variant order every round.
3. Warm up, then collect at least 5 independent rounds. Report median of per-round p50/p75 plus the raw range; treat changes smaller than run-to-run noise as inconclusive.
4. Capture a baseline of both throughput and allocation behavior (heap/RSS), because several hotspots are allocation-bound rather than CPU-bound.

### 1. Use the existing harnesses first

| Harness | Command | What it covers |
|---|---|---|
| Core fetch | `cd benchmarks/fetch && node bench.mts` (or `bun bench.mts`) | `ping`, dynamic+query, JSON response, middleware, JSON body |
| A/B vs a ref | `cd benchmarks/fetch && ./compare.sh <ref>` | Isolates a change from machine drift; `ROUNDS=5` |
| Single case | `HONO_CASE='middleware' node bench.mts` | Focused iteration |
| JSON output | `HONO_JSON=1 node bench.mts` | Machine-readable p50/min/p75 for CI |
| Routers | `cd benchmarks/routers && pnpm install && pnpm run bench:node` | Static/dynamic/wildcard matching vs other routers |
| Router init | `cd benchmarks/routers && pnpm run bench-includes-init:node` | Construction/first-match cost |
| Query params | `cd benchmarks/query-param && pnpm install && pnpm run bench:node` | Query parsing vs `qs`/`fast-querystring`/`URLSearchParams` |
| getPath | `cd benchmarks/utils && pnpm install && node --experimental-strip-types src/get-path.ts` (or `tsx`) | Path extraction variants |
| HTTP end-to-end | `cd benchmarks/http-server && bun run benchmark.ts` | Server-level throughput/latency via bombardier (CI workflow `ci.yml:219-288`) |
| Bundle/type budget | `perf-measures/bundle-check` and `perf-measures/type-check` (CI `ci.yml:206-217`) | Code-size and type-instantiation regressions |

### 2. Add targeted scenarios (in benchmark files only, not production code)

1. **Context/allocation:** `ping GET /` with `--trace-gc` and a heap profile; report bytes/request and GC per 100k requests. Compare the current build with a branch that moves `Context` methods to the prototype.
2. **Middleware scaling:** routes with 0, 1, 5, 10 middleware, each both sync and async; report ns/request and allocations/request. This quantifies hotspot 2.
3. **Routing:** static vs `:param` vs regex-constrained vs wildcard, path lengths 10/100/1000 chars, and `%20`-encoded paths. Measure first request separately from warm requests. This quantifies hotspot 3.
4. **Response decoration:** handler plus one middleware that sets headers before `next()` and one that sets them after `next()`; sweep 1/10/50 response headers. This quantifies hotspot 4.
5. **Body sizes:** JSON and form bodies at 1 KB/100 KB/1 MB/10 MB; measure p50, peak RSS, and retained heap after the request. This quantifies hotspot 5.
6. **Query keys:** 1/5/20 params, single-key repeated calls vs one all-params call, plain vs percent-encoded values. This quantifies hotspot 6.

Use `mitata` (already the repository standard) with `measure()` and forced batching where needed, as `benchmarks/fetch/bench.mts` does for sub-microsecond cases. Keep benchmark payloads deterministic and allocate request objects outside the timed loop where possible; for body cases, create a fresh `Request` per iteration because bodies are consumed.

### 3. Profile before optimizing

1. CPU: `node --cpu-prof` (or `bun --profile`) on the middleware, dynamic-route, and large-body cases; attribute samples to `Context`, `compose.dispatch`, `match`, `getPath`, `_getQueryParam`, `JSON.parse`.
2. Allocation: `node --heap-prof` and `--trace-gc`; confirm the expected closure-per-request pattern and identify the largest allocation sites.
3. Memory retention: `--expose-gc`, force GC after each measured batch, and sample `process.memoryUsage()` to detect retained body text/caches.
4. For end-to-end effects, run the HTTP benchmark under `bombardier` with fixed connections/duration and compare p50/p99 and RPS; profile the server process concurrently with `--cpu-prof` if supported.

### 4. Acceptance and guardrails

- Only pursue a hotspot once a profile shows it is a meaningful share of a realistic case; do not optimize based on static reading alone.
- Target: no regression >3% on the `ping` and static-route cases; measurable improvement on whichever case motivated the change (middleware chain, dynamic route, large body, or query-heavy handler).
- Bundle size and type-instantiation budgets must stay within the existing `perf-measures` checks.
- Land one hotspot per change, with before/after numbers from the same machine and a fresh-process A/B run (`compare.sh`). Revert if p50 moves less than the observed noise floor.

### 5. Known limitations of this assessment

- No benchmark dependencies are installed in this clone, so no numbers are reported here; the plan above is the next step.
- Results on Node/V8 and Bun/JavaScriptCore can differ, especially for class-field closures and regex matching. Validate on both, and validate on at least one Workers-compatible runtime if the change targets edge deployments.
- Lazy router construction is a one-time cost per app instance; it is critical for cold start but invisible in steady-state throughput benchmarks. Keep the two measurements separate.
