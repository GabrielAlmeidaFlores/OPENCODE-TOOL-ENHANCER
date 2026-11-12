# PILOT Security Review — Input Handling & Authentication-Adjacent Code

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

**Repository:** `hono` v4.13.18
**Commit reviewed:** `f6fbaf02`
**Review date:** 2026-11-12
**Scope:** request/query/path/body parsing, URL decoding, cookie handling, and the middleware that sits next to authentication (basic/bearer/JWT/JWK auth, CORS, CSRF, body-limit, cache, method-override).

---

## 1. Method and severity scale

**Method**

- Static review of the input-parsing and auth-adjacent modules, following data from the wire (`Request` → `HonoRequest` → middleware → handler).
- Targeted runtime checks of the CSRF media-type regex and of URL decoding semantics (Node) to confirm the behavior described below.
- No application code was reviewed. Several findings are *risky defaults / footguns* that become exploitable under stated preconditions. Those preconditions are called out explicitly.

**Severity scale**

| Severity | Meaning |
| --- | --- |
| **Critical** | Direct, unauthenticated compromise of the framework or its users with no special preconditions. |
| **High** | Serious impact (data disclosure, auth bypass) with realistic preconditions. |
| **Medium** | Meaningful impact under a common configuration, or a defense-in-depth gap that removes a layer of protection. |
| **Low** | Limited impact, unusual preconditions, or hardening opportunity. |
| **Info** | Observation with no direct security impact. |

---

## 2. Summary

| ID | Risk | Severity | Primary location |
| --- | --- | --- | --- |
| SEC-01 | Cache middleware can cache and serve cookie-authenticated, personalized responses to other users | **High** | `src/middleware/cache/index.ts:266-273`, `:72-80`, `:301-304` |
| SEC-02 | CSRF middleware silently skips every non-"simple" content type (notably `application/json`) | **Medium** | `src/middleware/csrf/index.ts:28-30`, `:138-147` |
| SEC-03 | Cookie helper defaults omit `HttpOnly`, `Secure`, and `SameSite` | **Medium** | `src/helper/cookie/index.ts:78-102`, `src/utils/cookie.ts:174-260` |
| SEC-04 | Body parsing is unbounded by default; `bodyLimit` trusts `Content-Length` and ignores compressed size | **Medium** | `src/utils/body.ts:136-143`, `src/request.ts:258-260`, `:334-336`, `src/middleware/body-limit/index.ts:67-74`, `:82-101` |
| SEC-05 | `methodOverride` forwards an unvalidated method token and re-dispatches through `app.fetch` | **Low** | `src/middleware/method-override/index.ts:74-104`, `:107-135` |
| SEC-06 | `c.redirect()` performs no target validation and relies on the runtime to reject CR/LF | **Low** | `src/context.ts:768-780`, `:519-532` |

The six items below are independent; SEC-01 and SEC-02 are the ones most worth acting on for an app that uses cookie sessions.

---

## 3. Findings

### SEC-01 — Cache middleware can store and serve cookie-authenticated responses to other users

**Severity:** High (conditional on cookie-based auth + personalized responses + `cache()` on those routes)

**Locations**
- `src/middleware/cache/index.ts:266-273` — bypass condition
- `src/middleware/cache/index.ts:72-80` — `shouldSkipCache`
- `src/middleware/cache/index.ts:301-304` — serving from cache
- `src/middleware/cache/index.ts:313-322` — storing in cache

**What the code does**

The middleware bypasses the cache only when the request method is not `GET`/`QUERY`, or when the request carries an `Authorization` header:

```ts
// src/middleware/cache/index.ts:266-273
if (
  (c.req.method !== 'GET' && c.req.method !== 'QUERY') ||
  c.req.raw.headers.has('Authorization')
) {
  await next()
  return
}
```

On the response side, `shouldSkipCache` refuses to store responses that set `Set-Cookie`, are `private`/`no-store`/`no-cache`, or vary on headers the middleware does not key on:

```ts
// src/middleware/cache/index.ts:72-80
const shouldSkipCache = (...) =>
  (responseVary.length && (...)) ||
  shouldSkipCacheControl(res.headers.get('Cache-Control')) ||
  res.headers.has('Set-Cookie')
```

The **request** `Cookie` header is never consulted — neither as a bypass condition nor as part of the cache key (`key = c.req.url`, `src/middleware/cache/index.ts:285`). When a cache hit occurs, the stored response is returned verbatim to the new requester (`:301-304`).

The existing tests confirm the intended auth behavior for the header case (`src/middleware/cache/index.test.ts:732-745`) and the response `Set-Cookie` case (`:512-518`), but there is no corresponding request-`Cookie` case.

**Why it matters**

Browser sessions are usually cookie-based, and a personalized handler commonly returns user-specific data **without** setting a new cookie on every response. In that configuration:

1. User A requests `GET /dashboard`; the handler returns A's data with `Cache-Control` compatible with caching and no `Set-Cookie`.
2. The middleware stores it under the URL key (`:313-322`).
3. User B requests the same URL and receives A's cached response (`:301-304`).

That is cross-user data disclosure (and potentially privilege confusion) rather than a theoretical issue. The explicit `Authorization` guard shows the middleware intends to avoid caching authenticated responses; the omission of `Cookie` leaves the far more common browser-auth path uncovered.

**Preconditions**

- `cache()` mounted on a route whose response depends on a session cookie.
- The handler does not set `Set-Cookie` on every response and does not explicitly set `Vary: Cookie` (a handler-set `Vary` that the middleware was not configured for does cause a skip, `:72-78`, but this is not the default).
- `Cache-Control` does not already contain `private`/`no-store`/`no-cache`.

**Recommendation**

- Treat a request `Cookie` header as a bypass by default (like `Authorization`), or include it in the cache key/vary list. The conservative behavior is to skip caching whenever `Cookie` is present unless the caller explicitly opts in.
- Document that `cache()` must not be placed in front of personalized routes without an explicit `vary`/`keyGenerator`.
- Add a regression test mirroring `src/middleware/cache/index.test.ts:732` for `Cookie`.

---

### SEC-02 — CSRF middleware silently skips every non-"simple" content type (notably `application/json`)

**Severity:** Medium (conditional on a permissive CORS policy or a same-site attacker)

**Locations**
- `src/middleware/csrf/index.ts:28-30` — the media-type gate
- `src/middleware/csrf/index.ts:138-147` — the only enforcement point
- `src/middleware/csrf/index.ts:95-112`, `:114-136` — default origin / `Sec-Fetch-Site` checks

**What the code does**

CSRF validation is performed only when the request media type matches a small regex:

```ts
// src/middleware/csrf/index.ts:28-30
const isSafeMethodRe = /^(GET|HEAD|OPTIONS)$/
const isCsrfContentTypeRe =
  /^\b(application\/x-www-form-urlencoded|multipart\/form-data|text\/(?:plain|ping))\b/i
```

```ts
// src/middleware/csrf/index.ts:138-147
if (
  !isSafeMethodRe.test(c.req.method) &&
  isCsrfContentTypeRe.test(c.req.header('content-type') || 'text/plain') &&
  !(await isAllowedSecFetchSite(...)) &&
  !(await isAllowedOrigin(...))
) { /* 403 */ }
```

A request with `Content-Type: application/json` (or `application/xml`, `text/xml`, `application/graphql`, etc.) fails `isCsrfContentTypeRe` and therefore never reaches the origin/`Sec-Fetch-Site` checks. Confirmed with a direct check of the regex:

```
"application/json"             => false
"application/json; charset=…"  => false
"application/x-www-form-urlencoded" => true
"multipart/form-data; boundary=…"   => true
"text/plain"                   => true
```

**Why it matters**

Classic HTML-form CSRF is covered (form, multipart, `text/plain`). JSON CSRF is not. A cross-origin `fetch` with `Content-Type: application/json` normally triggers a CORS preflight, so a correctly restrictive CORS policy is the actual control. But:

- `cors()` defaults to `origin: '*'` (`src/middleware/cors/index.ts:65`), and many apps enable credentials/reflected origins without realizing the CSRF middleware is not covering JSON.
- Any endpoint reachable with a "simple" content type that is *not* in the list is also uncovered.
- The middleware's presence can create a false sense of protection: it is easy to assume "CSRF is on" covers all unsafe requests.

This is a defense-in-depth gap rather than an unconditional bypass, hence Medium.

**Preconditions**

- Cookie/session-authenticated state-changing endpoint that accepts a non-listed content type (most commonly JSON).
- CORS (or a same-site/compromised-origin scenario) permits the request to reach the handler.

**Recommendation**

- Make the content-type check an explicit allow/deny policy rather than a hard-coded "simple request" list: reject unsafe requests whose media type is not explicitly allowed, instead of skipping validation for unknown types.
- At minimum, include `application/json` and document the exact list of content types that are *not* covered.
- Keep the origin/`Sec-Fetch-Site` checks as a second layer and ensure CORS is restrictive for credentialed routes.

---

### SEC-03 — Cookie helper defaults omit `HttpOnly`, `Secure`, and `SameSite`

**Severity:** Medium

**Locations**
- `src/helper/cookie/index.ts:78-97` — `generateCookie`
- `src/helper/cookie/index.ts:99-102` — `setCookie`
- `src/utils/cookie.ts:174-260` — `_serialize` (attributes are all conditional)
- `src/utils/cookie.ts:235-245` — `HttpOnly` / `Secure` / `SameSite` are added only when set

**What the code does**

`setCookie` builds the cookie with only `path: '/'` by default:

```ts
// src/helper/cookie/index.ts:78-97 (abridged)
if (opt?.prefix === 'secure') {
  cookie = serialize('__Secure-' + name, value, { path: '/', ...opt, secure: true })
} else if (opt?.prefix === 'host') {
  cookie = serialize('__Host-' + name, value, { ...opt, path: '/', secure: true, domain: undefined })
} else {
  cookie = serialize(name, value, { path: '/', ...opt })
}
```

```ts
// src/utils/cookie.ts:235-245
if (opt.httpOnly) { cookie += '; HttpOnly' }
if (opt.secure)   { cookie += '; Secure' }
if (opt.sameSite) { cookie += `; SameSite=${...}` }
```

So `setCookie(c, 'session', token)` produces `session=…; Path=/` — script-readable, sendable over plain HTTP, and sent on cross-site navigations. The `__Host-`/`__Secure-` prefixes enforce `Secure` (`src/utils/cookie.ts:181-199`), but the plain helper does not.

**Why it matters**

- **XSS → session theft:** without `HttpOnly`, any script injection can read the session cookie.
- **CSRF:** without `SameSite`, the cookie is attached to cross-site requests (subject to browser defaults, which vary).
- **Network exposure:** without `Secure`, the cookie can be sent over HTTP and captured by a network attacker.

Frameworks that default to `HttpOnly` + `SameSite=Lax` reduce the chance that a correct application is still compromised by a single omitted option. This is a "secure-by-default" gap, not a bug in the serializer.

**Recommendation**

- Default `httpOnly: true` and `sameSite: 'Lax'` for cookies produced by `setCookie`/`generateCookie`, with an explicit opt-out for cookies that must be script-readable or cross-site.
- Default `secure: true` when the request is HTTPS (or require it for session-style cookies), and document the prefix helpers as the preferred path.
- At minimum, add a prominent warning in the helper docs and a lint/test that flags cookie writes without `httpOnly`.

---

### SEC-04 — Body parsing is unbounded by default; `bodyLimit` trusts `Content-Length` and ignores compressed size

**Severity:** Medium

**Locations**
- `src/utils/body.ts:136-143` — `parseFormData` reads the whole body with `arrayBuffer()`
- `src/request.ts:258-260` — `json()` reads the whole body with `text()`
- `src/request.ts:334-336` — `formData()`
- `src/middleware/body-limit/index.ts:67-74` — trusts `Content-Length`
- `src/middleware/body-limit/index.ts:82-101` — chunked path buffers up to `maxSize`

**What the code does**

The framework body parsers materialize the entire request body in memory with no built-in cap:

```ts
// src/utils/body.ts:136-143
const arrayBuffer = await (request as Request).arrayBuffer()
const formDataPromise = bufferToFormData(arrayBuffer, headers.get('Content-Type') || '')
```

`c.req.json()` similarly does `#cachedBody('text').then(JSON.parse)` (`src/request.ts:258-260`), and `formData()` caches the full `FormData` (`:334-336`). The nesting limits in `utils/body.ts:9-10` (`MAX_NESTING_DEPTH`, `MAX_NESTED_OBJECTS`) protect against *structural* abuse but not against *size* abuse.

`bodyLimit` is opt-in and, when a `Content-Length` is present, trusts it without counting the actual stream:

```ts
// src/middleware/body-limit/index.ts:67-74
const hasTransferEncoding = c.req.raw.headers.has('transfer-encoding')
const hasContentLength = c.req.raw.headers.has('content-length')
if (hasContentLength && !hasTransferEncoding) {
  const contentLength = parseInt(c.req.raw.headers.get('content-length') || '0', 10)
  return contentLength > maxSize ? onError(c) : next()
}
```

The chunked path is bounded (`:82-101`), but it counts **wire bytes**, not decompressed bytes.

**Why it matters**

- **Memory-exhaustion DoS:** any endpoint calling `parseBody()`, `formData()`, or `json()` without `bodyLimit` can be driven to allocate arbitrarily large buffers. A handful of concurrent large requests can exhaust a worker/isolate.
- **Declared-length bypass:** if an upstream server or proxy tolerates a body larger than the declared `Content-Length` (request-smuggling class), `bodyLimit` accepts it because it never reads the stream on that path.
- **Compression bomb:** `bodyLimit` does not account for `Content-Encoding`; a small gzip body can expand far beyond `maxSize` when the runtime/handler decompresses it.

**Recommendation**

- Document that `bodyLimit` is mandatory for any route that parses a body, and consider a safe default limit at the framework level (opt-out rather than opt-in).
- In `bodyLimit`, always count the stream (or at least verify the observed length against the declared one) even when `Content-Length` is present.
- Account for `Content-Encoding` (reject or decompress-and-count) or cap decompressed size.
- Apply limits before `parseBody`/`json`/`formData` can buffer.

---

### SEC-05 — `methodOverride` forwards an unvalidated method token and re-dispatches through `app.fetch`

**Severity:** Low

**Locations**
- `src/middleware/method-override/index.ts:62-64` — only `GET` is skipped
- `src/middleware/method-override/index.ts:74-104` — form-based override
- `src/middleware/method-override/index.ts:107-118` — header-based override
- `src/middleware/method-override/index.ts:121-135` — query-based override
- `src/middleware/method-override/index.ts:88`, `:102`, `:117`, `:134` — `app.fetch(...)`

**What the code does**

The method value comes straight from the form field, header, or query parameter and is used as `RequestInit.method` without validation:

```ts
// src/middleware/method-override/index.ts:74-89 (abridged)
const method = form.get(methodFormName)
if (method) {
  ...
  const request = new Request(c.req.url, {
    body: newForm,
    headers: newHeaders,
    method: method as string,     // arbitrary attacker-controlled string
  })
  return app.fetch(request, c.env, getExecutionCtx(c))
}
```

The same pattern appears for the header (`:107-118`) and query (`:121-135`) variants.

**Why it matters**

- **Unhandled exceptions / 500s:** `_method=GET` or `_method=HEAD` with a body makes `new Request(..., { method: 'GET', body })` throw `TypeError` (forbidden method/body combination). `_method=CONNECT`/`TRACE`/`TRACK` are also rejected by the Fetch standard. An attacker can use this to generate unhandled errors; whether it leaks anything depends on the app's `onError`.
- **Method allow-list bypass:** if an app makes authorization decisions on the *original* method (e.g., only `POST` is CSRF-checked or logged), the re-dispatched request presents a different method to downstream middleware. Whether this is exploitable depends on middleware ordering and route design, but the framework does not constrain it.
- **Context reset:** the re-dispatch calls `app.fetch()` and therefore creates a **new `Context`**. Values set earlier (`c.set('user', …)`, request IDs, tenancy, etc.) are not carried over; anything that relies on them must re-derive them. This is easy to get wrong.
- **Query-based override** is reachable from a plain cross-site form POST (`?_method=DELETE`), widening the CSRF surface for apps that rely on method-based checks.

**Recommendation**

- Validate the override against an explicit allow-list (e.g., `PUT`/`PATCH`/`DELETE`) and reject anything else with a 400 before constructing a `Request`.
- Do not mount `methodOverride` globally; scope it to the routes that need it.
- Prefer the header form over the query form, and ensure CSRF/auth middleware run on the overridden request.
- Document the context-reset behavior and preserve/recompute required state.

---

### SEC-06 — `c.redirect()` performs no target validation and relies on the runtime to reject CR/LF

**Severity:** Low

**Locations**
- `src/context.ts:768-780` — `redirect`
- `src/context.ts:519-532` — `c.header` (delegates to `Headers.set`)

**What the code does**

```ts
// src/context.ts:768-780
redirect = <T extends RedirectStatusCode = 302>(location: string | URL, status?: T) => {
  const locationString = String(location)
  this.header(
    'Location',
    // Multibytes should be encoded
    // eslint-disable-next-line no-control-regex
    !/[^\x00-\xFF]/.test(locationString) ? locationString : encodeURI(locationString)
  )
  return this.newResponse(null, status ?? 302) as any
}
```

The only transformation is `encodeURI` for non-Latin-1 characters. ASCII control characters — including `\r` (0x0D) and `\n` (0x0A) — pass through untouched. The value is then handed to `Headers.set` (`src/context.ts:530`), which is expected by the Fetch standard to throw on invalid header values; safety therefore depends on the runtime implementation.

**Why it matters**

- **Open redirect:** `c.redirect(c.req.query('next') ?? '/')` is a common pattern. Hono does not restrict the target to a relative path or same origin, so an attacker-supplied `//evil.example` or `https://evil.example` produces a redirect to an external site (phishing, OAuth token leakage).
- **Header injection (defense-in-depth):** in a runtime or adapter whose `Headers` implementation does not fully enforce the CR/LF restriction, an attacker-controlled `location` containing `\r\n` could inject additional headers. Most conforming runtimes reject this, so the practical risk is low, but the framework itself provides no normalization.

**Recommendation**

- Strip/reject `\r`, `\n`, and other control characters before setting `Location`.
- Provide a safe-redirect helper (or an option) that only allows same-origin/relative targets, and document the open-redirect risk when passing user input.
- Where absolute redirects are required, validate against an allow-list of origins.

---

## 4. Lower-priority observations

These are worth noting but did not meet the bar for a standalone finding.

| # | Observation | Location | Severity |
| --- | --- | --- | --- |
| OBS-1 | `cors()` reflects the client's `Access-Control-Request-Headers` verbatim when `allowHeaders` is unset, effectively disabling header allow-listing for preflight. Combined with a permissive origin, this broadens the attack surface. Set an explicit `allowHeaders` list. | `src/middleware/cors/index.ts:132-145` | Low |
| OBS-2 | `jwt()` accepts tokens with no `exp`/`nbf` claim; the checks at `utils/jwt/jwt.ts:133-147` only run when the claim is present. A token minted without `exp` never expires unless the caller passes `verification` options or an upstream check. | `src/utils/jwt/jwt.ts:133-147`, `src/middleware/jwt/jwt.ts:138-141` | Low |
| OBS-3 | `jwk()` resolves `keys`/`jwks_uri` and calls `verifyWithJwks` on **every request**, and `verifyWithJwks` fetches `jwks_uri` with no caching. A request-derived `jwks_uri` (the API accepts a function of `c`) is an SSRF vector and a per-request latency/DoS amplifier. Cache JWKS and validate the URI/allow-list. | `src/middleware/jwk/jwk.ts:141-148`, `src/utils/jwt/jwt.ts:237-250` | Low |
| OBS-4 | The default CSRF origin check derives the expected origin from `c.req.url` (`new URL(c.req.url).origin`), which is `Host`-derived. Behind a proxy that forwards an attacker-influenced `Host`, or with a non-browser client, the check can be satisfied by matching `Origin` to a spoofed `Host`. Browsers normally send the real `Host`, so this is mostly a proxy-hardening concern; configure `origin` explicitly. | `src/middleware/csrf/index.ts:97` | Low |
| OBS-5 | `serve-static` validates the decoded request path (`..`, `//`, `\`) before applying `rewriteRequestPath`, but does not re-validate the rewritten output. A rewrite function that maps user input into a path can reintroduce traversal. | `src/middleware/serve-static/index.ts:72-92` | Low |
| OBS-6 | `basicAuth`/`bearerAuth` implement no rate limiting or lockout. Credential guessing is bounded only by the deployment. This is expected for middleware but should be paired with an edge control. | `src/middleware/basic-auth/index.ts:105-131`, `src/middleware/bearer-auth/index.ts:169-232` | Info |

---

## 5. Controls verified as working

To keep the report balanced, these input/auth controls were checked and look correct:

- **JWT algorithm confusion is prevented.** `verify` requires an explicit `alg`, rejects tokens whose header `alg` differs (`src/utils/jwt/jwt.ts:129-131`), and `verifyWithJwks` rejects symmetric algorithms and enforces `allowedAlgorithms` (`:225-233`). `isTokenHeader` rejects unknown `alg` values and `crit` (`:44-56`).
- **Constant-time credential comparison.** `timingSafeEqual` hashes both sides and compares both the hash and the original in constant time (`src/utils/buffer.ts:29-63`, `:76-96`); `basicAuth` uses it for username and password (`src/middleware/basic-auth/index.ts:118-121`), as does `bearerAuth` (`src/middleware/bearer-auth/index.ts:211-218`).
- **Prototype pollution is guarded in form parsing.** `parseBody` builds null-prototype objects (`src/utils/body.ts:164`), blocks `__proto__` as an intermediate segment (`:231-233`), and caps depth/count (`:9-10`, `:236-254`). Query parsing also uses `Object.create(null)` (`src/utils/url.ts:298`).
- **`serve-static` blocks traversal for the normal path.** It rejects `.`/`..` segments, doubled separators, and backslashes after decoding, and rejects percent-encoded paths unless `allowPercentInPath` is set (`src/middleware/serve-static/index.ts:72-86`).
- **CSRF defaults are deny-by-default when headers are missing.** Missing `Origin` and missing `Sec-Fetch-Site` are treated as denied (`src/middleware/csrf/index.ts:106-112`, `:126-136`).
- **Cache skips `Authorization` requests and responses that set `Set-Cookie`** (`src/middleware/cache/index.ts:269`, `:80`) — the gap is the request `Cookie` (SEC-01).
- **Cookie prefixes are enforced on serialization.** `__Secure-` requires `Secure`; `__Host-` requires `Secure`, `Path=/`, and no `Domain` (`src/utils/cookie.ts:181-199`).
- **`requestId` rejects unsafe characters and over-length values** (`src/middleware/request-id/request-id.ts:49`), preventing header injection through the request ID.
- **The default error handler does not leak exception details** (`src/hono-base.ts:37-43` returns `Internal Server Error`).

---

## 6. Assumptions and limitations

- This review is static and framework-level. It does not prove exploitability in a specific deployment; reverse proxies, runtime `Headers` implementations, and application middleware ordering materially affect several findings.
- Severity for SEC-01, SEC-02, and SEC-03 assumes a typical cookie-session web app. Apps that use only bearer tokens (no cookies) and strict CORS reduce or remove the impact of SEC-01/SEC-02.
- Line numbers refer to commit `f6fbaf02` and will drift with future changes.
- No files other than this report were modified.
