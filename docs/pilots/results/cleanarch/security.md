# PILOT Security Review: Input Handling & Authentication-Adjacent Code

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

- **Repository:** Clean Architecture template (`clone`)
- **Revision reviewed:** `302e8ac` (working tree)
- **Review type:** Static review of HTTP input handling, validation, endpoint security configuration, middleware order, and authentication-adjacent configuration
- **Files created:** this report only (`PILOT_SECURITY.md`); no application code was changed

## Scope

Reviewed:

- `src/Clean.Architecture.Web` (Program, middleware/service configuration, all contributor endpoints, validators, result mapping)
- `src/Clean.Architecture.Core` (domain value objects and aggregate input constraints)
- `src/Clean.Architecture.Infrastructure` (persistence configuration, seed data, list query, email sender)
- ASP.NET Core configuration files (`appsettings*.json`, `Properties/launchSettings.json`)

The `sample/` and `MinimalClean/` trees contain near-duplicates of the same patterns. Findings below reference the primary `src/` tree; the same issues generally apply to the copies.

## Severity scale

| Severity | Meaning |
|---|---|
| Critical | Directly exploitable by an unauthenticated network attacker with high impact (data destruction/exfiltration, full bypass of a security control). |
| High | Exploitable misconfiguration that undermines a core security property (transport security, access control) or enables broad abuse. |
| Medium | Requires specific conditions or has limited impact, but is a concrete weakness that should be fixed before production use. |
| Low | Defense-in-depth or hygiene issue with limited direct exploitability. |

## Risk summary

| # | Risk | Severity |
|---|---|---|
| 1 | Every contributor endpoint is anonymous; no authentication/authorization is configured at all | **Critical** |
| 2 | HTTPS redirection is registered after endpoint execution, so plaintext requests can be served | **High** |
| 3 | No rate limiting or request throttling on anonymous write endpoints | **Medium** |
| 4 | `Update` accepts `ContributorId <= 0`; `ContributorId.From` then throws an unhandled exception | **Medium** |
| 5 | Unbounded `page` value overflows pagination offset arithmetic and produces a 500 | **Medium** |
| 6 | `PhoneNumber` is unvalidated, unbounded, and persisted into an unconstrained owned column | **Medium** |
| 7 | Attacker-controlled `Host` header is reflected into the `Link` response header | **Medium** |
| 8 | SMTP client connects with TLS disabled in all environments | **Medium** |
| 9 | Global cookie policy sets `SameSite=None`, an unsafe baseline for future auth cookies | **Low** |
| 10 | Internal error strings are returned in problem details | **Low** |

---

## 1. All contributor endpoints are anonymous; no authentication or authorization exists

**Severity: Critical**  
**CWE-306 (Missing Authentication for Critical Function), CWE-862 (Missing Authorization)**

### Evidence

All five endpoints explicitly opt out of any access control:

- `src/Clean.Architecture.Web/Contributors/Create.cs:26` — `AllowAnonymous();`
- `src/Clean.Architecture.Web/Contributors/Update.cs:21` — `AllowAnonymous();`
- `src/Clean.Architecture.Web/Contributors/Delete.cs:20` — `AllowAnonymous();`
- `src/Clean.Architecture.Web/Contributors/List.cs:15` — `AllowAnonymous();`
- `src/Clean.Architecture.Web/Contributors/GetById.cs:19` — `AllowAnonymous();`

No authentication scheme or authorization policy is registered anywhere in the host:

- `src/Clean.Architecture.Web/Program.cs:28-34` builds and runs the app without `UseAuthentication()` / `UseAuthorization()`.
- `src/Clean.Architecture.Web/Configurations/ServiceConfigs.cs:9-30` registers infrastructure, mediator, and email sender only — no `AddAuthentication`, `AddAuthorization`, JWT, API-key, or identity provider.
- A repository-wide search for `AddAuthentication`, `AddAuthorization`, `RequireAuthorization`, `AddJwtBearer`, `ApiKey`, and `Identity` returns no matches in application code.

### Impact

Anyone who can reach the service can list all contributors (including phone numbers), read any record by sequential integer ID, create records, overwrite any record, and delete any record. There is no concept of a caller identity, role, tenant, or record ownership. The `Delete` and `Update` endpoints are destructive and require no credentials. Sequential integer IDs (`GetContributorByIdRequest.Route` at `src/Clean.Architecture.Web/Contributors/GetById.GetContributorByIdRequest.cs:5`) make full enumeration and mass modification trivial.

### Recommendation

- Register an authentication scheme and call `UseAuthentication()`/`UseAuthorization()` before `UseFastEndpoints()`.
- Replace the blanket `AllowAnonymous()` calls with authentication requirements; keep only the endpoints that must be public anonymous.
- Add record-level authorization (ownership/tenant checks) inside the handlers, not only at the route level.
- If the template is intentionally unauthenticated, add an explicit startup guard that refuses to run with write endpoints enabled in non-Development environments, and document the required integration point.

---

## 2. HTTPS redirection is registered after endpoint execution

**Severity: High**  
**CWE-319 (Cleartext Transmission of Sensitive Information)**

### Evidence

`src/Clean.Architecture.Web/Configurations/MiddlewareConfig.cs:22`:

```csharp
app.UseFastEndpoints();
```

`src/Clean.Architecture.Web/Configurations/MiddlewareConfig.cs:43`:

```csharp
app.UseHttpsRedirection(); // Note this will drop Authorization headers
```

`UseHttpsRedirection()` is placed **after** `UseFastEndpoints()`. With ASP.NET Core endpoint routing, the endpoint middleware executes the matched endpoint and does not continue down the pipeline, so requests are handled before the redirect middleware is reached. HSTS is also only emitted on HTTPS responses (`MiddlewareConfig.cs:19`), so it does not compensate.

The inline comment is also misleading: a 307 redirect preserves the method and headers, and the comment implies credentials are expected to flow through this pipeline even though no authentication is configured (see finding 1).

### Impact

An attacker on the network path can send requests over plain HTTP and have them processed as normal. Once authentication is added, bearer tokens, API keys, session cookies, and request/response bodies would be exposed to interception and request tampering. Even today, contributor PII is transmitted in cleartext if the client uses `http://`.

### Recommendation

- Move `UseHttpsRedirection()` (and HSTS) **before** `UseRouting`/`UseFastEndpoints`, ideally at the top of the pipeline.
- Remove the misleading comment and add a test asserting that an HTTP request is redirected (or rejected) before endpoint execution.
- In container/proxy deployments, configure `ForwardedHeaders` with a known proxy allow-list so the scheme is derived correctly.

---

## 3. No rate limiting or request throttling on anonymous write endpoints

**Severity: Medium**  
**CWE-770 (Allocation of Resources Without Limits or Throttling), CWE-799 (Improper Control of Interaction Frequency)**

### Evidence

- `src/Clean.Architecture.Web/Program.cs:28-34` and `src/Clean.Architecture.Web/Configurations/ServiceConfigs.cs:9-30` contain no `AddRateLimiter`/`UseRateLimiter` registration.
- `src/Clean.Architecture.Web/Contributors/Create.cs:62-69` accepts a caller-supplied `Name` and `PhoneNumber` and writes a row on every request.
- `src/Clean.Architecture.Web/Contributors/List.cs:49-63` executes a paged query plus a `COUNT(*)` (`src/Clean.Architecture.Infrastructure/Data/Queries/ListContributorsQueryService.cs:27`) on every request.

### Impact

Because the write endpoints are anonymous (finding 1), an unauthenticated attacker can flood `POST /Contributors` to exhaust database storage/connections and pollute application data, or flood `GET /Contributors` to drive repeated table scans and counts. The template is typically used as a starting point for real services, so this gap is likely to be inherited.

### Recommendation

- Add ASP.NET Core rate limiting with per-IP and per-identity partitions; apply a strict policy to `POST`/`PUT`/`DELETE`.
- Consider a global concurrency limit and a maximum request body size.
- Add query cost limits for list endpoints (cap page size already exists at `src/Clean.Architecture.UseCases/Constants.cs:6`, but request frequency is unbounded).

---

## 4. `Update` accepts non-positive IDs and throws an unhandled exception

**Severity: Medium**  
**CWE-20 (Improper Input Validation)**

### Evidence

- `src/Clean.Architecture.Web/Contributors/Update.UpdateContributorRequest.cs:10-15` defines `ContributorId` and `Id` as plain `int` values; the `[Required]` attributes on `int` properties are no-ops.
- `src/Clean.Architecture.Web/Contributors/Update.UpdateContributorValidator.cs:19-21` validates only that the route ID equals the body ID:

  ```csharp
  RuleFor(x => x.ContributorId)
    .Must((args, contributorId) => args.Id == contributorId)
  ```

  There is no `GreaterThan(0)` rule, unlike the Get and Delete validators (`GetById.GetContributorValidator.cs:13-14`, `Delete.DeleteContributorValidator.cs:12-13`).
- `src/Clean.Architecture.Web/Contributors/Update.cs:51-53` then calls `ContributorId.From(request.Id)`.
- `src/Clean.Architecture.Core/ContributorAggregate/ContributorId.cs:12-13` declares that only positive values are valid; Vogen's `From` throws `ValueObjectValidationException` for invalid values.

A request such as `PUT /Contributors/0` with body `{ "id": 0, "name": "x" }` passes validation (both IDs match), then throws before the handler can return a `Result.NotFound()`.

### Impact

An unauthenticated caller can trigger unhandled exceptions (HTTP 500), producing noisy error responses and potentially exposing stack traces through the development exception page (`src/Clean.Architecture.Web/Configurations/MiddlewareConfig.cs:11-14`). It also creates inconsistent behavior between Get/Delete (400 for `0`) and Update (500 for `0`), which complicates client error handling and monitoring.

### Recommendation

- Add `RuleFor(x => x.ContributorId).GreaterThan(0)` and `RuleFor(x => x.Id).GreaterThan(0)` in `UpdateContributorValidator`.
- Use the route-bound `ContributorId` as the source of truth for the command instead of the body `Id`, or remove the body `Id` entirely.
- Remove meaningless `[Required]` attributes from non-nullable value types.
- Add a global exception handler even in Development, or at least map `ValueObjectValidationException` to a 400.

---

## 5. Unbounded `page` value overflows the pagination offset and returns a 500

**Severity: Medium**  
**CWE-190 (Integer Overflow or Wraparound), CWE-20 (Improper Input Validation)**

### Evidence

- `src/Clean.Architecture.Web/Contributors/List.cs:111-113` validates only `page >= 1`; there is no upper bound.
- `src/Clean.Architecture.Web/Contributors/List.cs:90-95` binds `page` as an `int`.
- `src/Clean.Architecture.Infrastructure/Data/Queries/ListContributorsQueryService.cs:21` computes:

  ```csharp
  .Skip((page - 1) * perPage)
  ```

  With `page = int.MaxValue` and `per_page = 100`, `(page - 1) * 100` overflows to a large negative number. EF Core/SQL Server/SQLite reject a negative `OFFSET`, producing an exception and a 500 response.

`per_page` is capped at 100 (`List.cs:115-117`, `Constants.cs:6`), but `page` is not.

### Impact

Unauthenticated callers can reliably generate 500s with a single query string, pollute logs and error telemetry, and potentially trigger different exception paths across database providers. It is a low-effort availability/robustness issue rather than data compromise.

### Recommendation

- Cap `page` to a sane maximum (for example, `int.MaxValue / MAX_PAGE_SIZE` or a business limit such as 10,000) in `ListContributorsValidator`.
- Compute the offset with `long`/checked arithmetic and return a 400 when it exceeds the provider limit.
- Add a functional test for `?page=2147483647&per_page=100`.

---

## 6. `PhoneNumber` is unvalidated, unbounded, and persisted without constraints

**Severity: Medium**  
**CWE-20 (Improper Input Validation), CWE-400 (Uncontrolled Resource Consumption)**

### Evidence

- `src/Clean.Architecture.Web/Contributors/Create.cs:66-69` exposes `PhoneNumber` as a free-form `string?` with no data-annotation constraint.
- `src/Clean.Architecture.Web/Contributors/Create.cs:71-81` validates only `Name`; there is no rule for `PhoneNumber`.
- `src/Clean.Architecture.UseCases/Contributors/Create/CreateContributorHandler.cs:12-15` wraps the raw string directly into `new PhoneNumber("+1", command.PhoneNumber, String.Empty)`.
- `src/Clean.Architecture.Core/ContributorAggregate/PhoneNumber.cs:3-8` has no validation in its constructor.
- `src/Clean.Architecture.Infrastructure/Data/Config/ContributorConfiguration.cs:19` maps the owned type with `OwnsOne(...)` and no `HasMaxLength`, so a relational provider will typically create an unbounded (`nvarchar(max)`/`TEXT`) column.
- `src/Clean.Architecture.Web/Contributors/List.cs:127` and `GetById.cs:55-56` return the stored value to clients.

### Impact

A caller can store arbitrary-length or malformed values, consuming storage and producing inconsistent output. Because the field is returned by list/get endpoints, downstream consumers may ingest malformed data. If the value is ever rendered in an HTML context by another application, the lack of format validation increases the risk of content-injection issues (though the JSON API itself encodes output safely).

### Recommendation

- Add length and format validation (`MaximumLength`, `[Phone]` or a dedicated phone parser) to `CreateContributorValidator`.
- Enforce the same constraint in the domain value object so all entry points share it.
- Configure `HasMaxLength` on the owned `PhoneNumber` properties in `ContributorConfiguration`.
- Define an explicit maximum request body size for write endpoints.

---

## 7. Attacker-controlled `Host` header is reflected into the `Link` response header

**Severity: Medium**  
**CWE-644 (Improper Neutralization of HTTP Headers for Scripting Syntax), CWE-346 (Origin Validation Error)**

### Evidence

`src/Clean.Architecture.Web/Contributors/List.cs:65-68`:

```csharp
var baseUrl = $"{HttpContext.Request.Scheme}://{HttpContext.Request.Host}{HttpContext.Request.Path}";
string Link(string rel, int p) => $"<{baseUrl}?page={p}&per_page={perPage}>; rel=\"{rel}\"";
```

`Request.Host` is taken directly from the incoming `Host` header. The application does not configure `AllowedHosts` in `src/Clean.Architecture.Web/appsettings.json:1-49`, and does not configure `ForwardedHeaders` anywhere in `src/Clean.Architecture.Web/Configurations/MiddlewareConfig.cs` or `Program.cs`.

### Impact

An attacker can send `Host: evil.example` and receive pagination links pointing at `evil.example`. If a cache, proxy, or API gateway caches or reuses the response, or if a client follows `Link` headers without validating the origin, users can be redirected to attacker-controlled hosts. Trusting a non-allow-listed `Host` header also breaks correct scheme/host handling behind proxies.

### Recommendation

- Build absolute links from a configured public base URL, not from `Request.Host`.
- If dynamic host handling is required, enable `HostFiltering` with an explicit `AllowedHosts` list and configure `ForwardedHeaders` with a trusted proxy list.
- Validate/sanitize values before writing them into response headers.

---

## 8. SMTP client connects with TLS disabled in every environment

**Severity: Medium**  
**CWE-319 (Cleartext Transmission of Sensitive Information)**

### Evidence

- `src/Clean.Architecture.Infrastructure/Email/MimeKitEmailSender.cs:16-17`:

  ```csharp
  await client.ConnectAsync(_mailserverConfiguration.Hostname,
    _mailserverConfiguration.Port, false);
  ```

  The third argument (`useSsl: false`) disables TLS/STARTTLS entirely.
- `src/Clean.Architecture.Infrastructure/Email/MailserverConfiguration.cs:3-7` exposes only `Hostname` and `Port`; there is no TLS or credential option.
- `src/Clean.Architecture.Web/Configurations/ServiceConfigs.cs:14-26` registers this sender in **both** Development and non-Development environments (the `FakeEmailSender` alternative is commented out).
- `src/Clean.Architecture.Infrastructure/Email/MimeKitEmailSender.cs:13` logs the recipient, sender, and subject at `Warning` level on every send.

### Impact

If the configured mail server is remote, message contents and metadata (including contributor names and email addresses) are sent in plaintext and can be read or modified in transit. There is also no authentication path, so a production relay requiring auth cannot be used safely. Logging recipient/subject data is a PII retention issue.

### Recommendation

- Make TLS configurable and default to `SecureSocketOptions.StartTls` (or `SslOnConnect` for implicit TLS) instead of `false`.
- Add username/password or OAuth2 configuration and never hard-code credentials in `appsettings.json` (use a secret store).
- Add an explicit `FakeEmailSender` registration for non-production environments, or require an environment-specific sender.
- Lower the log level and redact recipient/subject in production.

---

## 9. Global cookie policy sets `SameSite=None`

**Severity: Low**  
**CWE-1275 (Sensitive Cookie with Improper SameSite Attribute), CWE-352 (Cross-Site Request Forgery)**

### Evidence

`src/Clean.Architecture.Web/Configurations/OptionConfigs.cs:15-19`:

```csharp
.Configure<CookiePolicyOptions>(options =>
{
  options.CheckConsentNeeded = context => true;
  options.MinimumSameSitePolicy = SameSiteMode.None;
});
```

No cookies are currently issued by the application, and `UseCookiePolicy()` is not called, so this is not exploitable today. However, the template establishes `SameSite=None` as the default for any cookie added later (for example, an auth/session cookie).

### Impact

If cookie-based authentication is added without overriding this policy, session cookies would be sent on cross-site requests, weakening CSRF defenses. Modern browsers also require `Secure` with `SameSite=None`, which can cause subtle behavior differences.

### Recommendation

- Default to `SameSiteMode.Lax` (or `Strict` where feasible).
- If `None` is required for a specific cross-site flow, scope it to that cookie and require `Secure`, plus an anti-forgery mechanism for state-changing endpoints.

---

## 10. Internal error strings are returned in problem details

**Severity: Low**  
**CWE-209 (Generation of Error Message Containing Sensitive Information)**

### Evidence

`src/Clean.Architecture.Web/Extensions/ResultExtensions.cs:26-29` (create), `63-66` (delete), and `82-86` (get/update) build `ProblemDetails.detail` from `string.Join("; ", result.Errors)`:

```csharp
_ => TypedResults.Problem(
  title: "Create failed",
  detail: string.Join("; ", result.Errors),
  statusCode: StatusCodes.Status400BadRequest)
```

In Development, unhandled exceptions are rendered by `UseDeveloperExceptionPage()` (`src/Clean.Architecture.Web/Configurations/MiddlewareConfig.cs:11-14`).

### Impact

Today the `Result.Errors` collection is populated with validation/business messages, so exposure is limited. If a handler later adds exception text, SQL errors, or infrastructure messages to `Errors`, those internals would be returned directly to callers. The development exception page similarly exposes stack traces and configuration details when `ASPNETCORE_ENVIRONMENT=Development` is accidentally used in a shared environment.

### Recommendation

- Map unexpected failures to a generic public message and log the detailed error server-side with a correlation ID.
- Never place raw exception messages into `Result.Errors` returned to clients.
- Ensure the developer exception page and `/listservices` (`src/Clean.Architecture.Web/Configurations/OptionConfigs.cs:21-31`) are unreachable outside Development.

---

## Checks that did not produce a finding

These were reviewed and appeared safe in the primary `src/` tree:

- **SQL injection in contributor queries:** `ListContributorsQueryService.cs:19` uses a constant `FromSqlRaw` statement, and `SeedData.cs:21-27` uses parameterized `ExecuteSqlAsync` interpolated strings. No user input is concatenated into SQL.
- **Mass assignment on update:** `UpdateContributorValidator.cs:19-21` enforces route/body ID equality, and the handler updates only `Name` (`UpdateContributorHandler.cs:17`). The residual issue is the non-positive-ID gap in finding 4.
- **Pagination size abuse:** `per_page` is capped at 100 (`Constants.cs:6`, `List.cs:115-117`). The residual issue is the unbounded `page` value in finding 5.
- **Committed credentials:** `appsettings.json` contains a LocalDB connection string with integrated authentication and a `database.sqlite` path; no passwords, API keys, or tokens are committed. Test-only passwords exist in `tests/Clean.Architecture.FunctionalTests/CustomWebApplicationFactory.cs:75` and `DockerAvailabilityTests.cs:17` for throwaway containers.
- **Health checks:** `/health` and `/alive` are mapped only in Development (`src/Clean.Architecture.ServiceDefaults/Extensions.cs:109-126`), matching the upstream guidance.
- **Swagger/Scalar:** `UseSwaggerGen`/`MapScalarApiReference` are gated to Development (`MiddlewareConfig.cs:24-41`).

## Recommended remediation order

1. Add authentication/authorization and remove blanket `AllowAnonymous()` (finding 1).
2. Fix HTTPS middleware order and add `ForwardedHeaders`/`AllowedHosts` (findings 2 and 7).
3. Add rate limiting and request-size limits (finding 3).
4. Fix ID and pagination validation gaps (findings 4 and 5).
5. Add phone-number validation and persistence constraints (finding 6).
6. Harden email transport and logging (finding 8).
7. Normalize cookie defaults and error responses (findings 9 and 10).
