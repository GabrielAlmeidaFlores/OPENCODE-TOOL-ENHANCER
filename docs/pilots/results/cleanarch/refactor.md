# PILOT_REFACTOR

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

**Status:** Proposal only — no production code has been changed.
**Deliverable of this pilot:** this document (`PILOT_REFACTOR.md`). Per the task, no other file is modified.
**Selected refactor:** Extract the duplicated contributor route template + `BuildRoute` implementation into a single source of truth (`ContributorRoutes`), while keeping every public member and every produced URL byte-for-byte identical.

---

## 1. Why this candidate

The full Clean Architecture variant registers three endpoints that all target the same resource shape — `/Contributors/{ContributorId:int}` — with one request DTO per endpoint. Each DTO independently re-declares both the route template and a byte-identical route builder.

Evidence of duplication (all in `src/Clean.Architecture.Web/Contributors`):

- `src/Clean.Architecture.Web/Contributors/Delete.DeleteContributorRequest.cs:5` — `public const string Route = "/Contributors/{ContributorId:int}";`
- `src/Clean.Architecture.Web/Contributors/GetById.GetContributorByIdRequest.cs:5` — same literal, declared again.
- `src/Clean.Architecture.Web/Contributors/Update.UpdateContributorRequest.cs:7` — same literal, declared a third time.
- `src/Clean.Architecture.Web/Contributors/Delete.DeleteContributorRequest.cs:6` — `BuildRoute` body: `Route.Replace("{ContributorId:int}", contributorId.ToString())`
- `src/Clean.Architecture.Web/Contributors/GetById.GetContributorByIdRequest.cs:6` — identical `BuildRoute` body.
- `src/Clean.Architecture.Web/Contributors/Update.UpdateContributorRequest.cs:8` — identical `BuildRoute` body (third copy).
- The placeholder token `{ContributorId:int}` is also re-typed inside each `BuildRoute` body at the three lines above, for six occurrences of the same token across the three files — every one of them must stay in sync with the template.
- Consumers bind routes through each DTO's own constant, so a change to one copy would not be caught by the other two: `src/Clean.Architecture.Web/Contributors/Delete.cs:19` (`Delete(DeleteContributorRequest.Route)`), `src/Clean.Architecture.Web/Contributors/GetById.cs:18` (`Get(GetContributorByIdRequest.Route)`), `src/Clean.Architecture.Web/Contributors/Update.cs:20` (`Put(UpdateContributorRequest.Route)`).

Why it is worth doing (low risk, real payoff):

- **Three diverging sources of truth for one contract.** Endpoint routing uses `Route`, while tests and HTTP clients use `BuildRoute`. If the template changes (e.g. a prefix, version segment, or a renamed `{ContributorId:int}` token), the endpoint would silently route to the new path while `BuildRoute` in a not-yet-updated DTO still hands tests/clients the old path — a failure mode that only shows up as a 404 in functional tests, not as a compile error.
- **Magic string duplicated at the point of use.** `"{ContributorId:int}"` is repeated inside each `BuildRoute` body, so the placeholder must be edited in 3 places even after the template is centralized.
- **Public surface is preserved**, so the refactor is verifiable by compilation alone for all internal call sites and by unchanged functional tests for external behavior: `tests/Clean.Architecture.FunctionalTests/ApiEndpoints/ContributorGetById.cs:15`, `:24`, `tests/Clean.Architecture.FunctionalTests/SqliteFallbackTests.cs:21`, `:81`, `tests/Clean.Architecture.FunctionalTests/SqlServerOnLinuxTests.cs:45`.
- **No behavior-bearing logic moves.** Unlike extracting the `ContributorDto` → `ContributorRecord` mapping (which differs between `Update.cs:65` — empty phone — and `GetById.cs:56` / `List.cs:127` — `PhoneNumber.ToString()`), route construction is provably identical at all three sites, so equivalence is easy to argue and review.

---

## 2. Behavior contract (must not change)

| Observable | Current behavior | Invariant for the refactor |
|---|---|---|
| `DeleteContributorRequest.Route`, `GetContributorByIdRequest.Route`, `UpdateContributorRequest.Route` | compile-time `const` values, all `/Contributors/{ContributorId:int}` | keep `const`, keep same value |
| `BuildRoute(int)` for each DTO | `/Contributors/` + `contributorId.ToString()` | identical string, same culture-sensitive `int.ToString()` |
| Route parameter name `ContributorId` | bound to `ContributorId` property on each request | unchanged |
| FastEndpoints registration / OpenAPI metadata | built from `Route` at `Configure()` | unchanged (same template string) |
| Public API used by tests | `GetContributorByIdRequest.BuildRoute(...)` etc. | member names and signatures unchanged |
| Validation | `DeleteContributorValidator` / `GetContributorValidator` / `UpdateContributorValidator` | untouched |

Explicit non-goals: no change to route semantics, no new route segments, no change to `Create.cs:64` (`"/Contributors"`) or `List.cs:14` (bare `"/Contributors"` literal), no mapping refactors, no dependency changes.

---

## 3. Before

Three files, each carrying its own copy of the contract:

`src/Clean.Architecture.Web/Contributors/Delete.DeleteContributorRequest.cs:3-9`
```csharp
public record DeleteContributorRequest
{
  public const string Route = "/Contributors/{ContributorId:int}";
  public static string BuildRoute(int contributorId) => Route.Replace("{ContributorId:int}", contributorId.ToString());

  public int ContributorId { get; set; }
}
```

`src/Clean.Architecture.Web/Contributors/GetById.GetContributorByIdRequest.cs:3-9`
```csharp
public class GetContributorByIdRequest
{
  public const string Route = "/Contributors/{ContributorId:int}";
  public static string BuildRoute(int contributorId) => Route.Replace("{ContributorId:int}", contributorId.ToString());

  public int ContributorId { get; set; }
}
```

`src/Clean.Architecture.Web/Contributors/Update.UpdateContributorRequest.cs:5-16`
```csharp
public class UpdateContributorRequest
{
  public const string Route = "/Contributors/{ContributorId:int}";
  public static string BuildRoute(int contributorId) => Route.Replace("{ContributorId:int}", contributorId.ToString());

  public int ContributorId { get; set; }

  [Required]
  public int Id { get; set; }
  [Required]
  public string? Name { get; set; }
}
```

Duplication count: 3 × template literal, 3 × placeholder literal, 3 × `BuildRoute` body (6 duplicated lines across 3 files).

---

## 4. After

### 4.1 New file — `src/Clean.Architecture.Web/Contributors/ContributorRoutes.cs`

Created with a UTF-8 BOM to satisfy `.editorconfig:21` (`charset = utf-8-bom`), 2-space indent (`.editorconfig:19`), file-scoped namespace (`.editorconfig:108`).

```csharp
namespace Clean.Architecture.Web.Contributors;

/// <summary>
/// Single source of truth for the contributor resource route template and
/// route construction. The per-endpoint request DTOs keep their existing
/// public <c>Route</c>/<c>BuildRoute</c> members, so endpoints, functional
/// tests and HTTP clients are unaffected by this refactor.
/// </summary>
public static class ContributorRoutes
{
  public const string ByIdTemplate = "/Contributors/{ContributorId:int}";

  private const string ContributorIdPlaceholder = "{ContributorId:int}";

  public static string BuildById(int contributorId)
    => ByIdTemplate.Replace(ContributorIdPlaceholder, contributorId.ToString());
}
```

### 4.2 `Delete.DeleteContributorRequest.cs:3-9` (after)

```csharp
public record DeleteContributorRequest
{
  public const string Route = ContributorRoutes.ByIdTemplate;
  public static string BuildRoute(int contributorId) => ContributorRoutes.BuildById(contributorId);

  public int ContributorId { get; set; }
}
```

### 4.3 `GetById.GetContributorByIdRequest.cs:3-9` (after)

```csharp
public class GetContributorByIdRequest
{
  public const string Route = ContributorRoutes.ByIdTemplate;
  public static string BuildRoute(int contributorId) => ContributorRoutes.BuildById(contributorId);

  public int ContributorId { get; set; }
}
```

### 4.4 `Update.UpdateContributorRequest.cs:5-16` (after)

```csharp
public class UpdateContributorRequest
{
  public const string Route = ContributorRoutes.ByIdTemplate;
  public static string BuildRoute(int contributorId) => ContributorRoutes.BuildById(contributorId);

  public int ContributorId { get; set; }

  [Required]
  public int Id { get; set; }
  [Required]
  public string? Name { get; set; }
}
```

### 4.5 Why this is behavior-preserving

- `Route` remains a compile-time `const`; C# allows a `const` to be initialized from another `const` in the same assembly, and the value `/Contributors/{ContributorId:int}` is copied verbatim. FastEndpoints therefore registers the exact same templates (`Delete.cs:19`, `GetById.cs:18`, `Update.cs:20`) and emits identical OpenAPI metadata.
- `BuildRoute` delegates to a helper whose body is character-for-character the old expression, including `contributorId.ToString()` **without** `CultureInfo.InvariantCulture`. This is deliberate: switching to invariant culture would change output for negative ids under cultures whose negative sign differs (e.g. `sv-SE` with ICU). Keeping `ToString()` preserves exact behavior; routes are positive-only in practice, but equivalence should not depend on that.
- `string.Replace(string, string)` replaces all occurrences; the placeholder occurs exactly once in the template, so the result equals the old value for every `int` input.
- Request types, property names, template parameter name (`ContributorId`), validators, endpoint base types, and response types are untouched; every test call site listed in §1 still compiles and still targets the same URLs.
- Net diff: 1 new file (~19 lines) + 6 changed lines in 3 existing files; **0** changed statements with runtime effect.

---

## 5. Step-by-step plan

1. **Baseline the duplication (read-only).**
   `rg -n 'Contributors/\{ContributorId:int\}' src` → expect exactly 3 hits (the three DTOs). `rg -n 'BuildRoute' src/Clean.Architecture.Web` → expect 3 definitions.
2. **Add** `src/Clean.Architecture.Web/Contributors/ContributorRoutes.cs` exactly as in §4.1 (UTF-8 BOM, file-scoped namespace).
3. **Edit the three DTOs** (§4.2–§4.4): replace the template literal with `ContributorRoutes.ByIdTemplate` and the `BuildRoute` body with the delegating call. Leave every other member and attribute alone.
4. **Prove no literal copies remain.**
   `rg -n '"/Contributors/\{ContributorId:int\}"' src` → expect 1 hit (`ContributorRoutes.cs`).
   `rg -n 'Route\.Replace\("\{ContributorId:int\}"' src` → expect 0 hits.
5. **Build:** `dotnet build src/Clean.Architecture.Web/Clean.Architecture.Web.csproj`
6. **Test (behavioral proof):**
   - `dotnet test tests/Clean.Architecture.FunctionalTests` — exercises the by-id URL end to end: seed hit and 404 via `GetContributorByIdRequest.BuildRoute` (`tests/Clean.Architecture.FunctionalTests/ApiEndpoints/ContributorGetById.cs:15`, `:24`), the SQLite fallback paths (`tests/Clean.Architecture.FunctionalTests/SqliteFallbackTests.cs:21`, `:81`), and the SQL Server path (`tests/Clean.Architecture.FunctionalTests/SqlServerOnLinuxTests.cs:45`). Note that the main test project does not currently call `UpdateContributorRequest.BuildRoute` or `DeleteContributorRequest.BuildRoute`; for those two the step-1/step-4 `rg` audits plus code review are the guard.
   - `dotnet test tests/Clean.Architecture.UnitTests` — regression safety for the surrounding code (the route change should be inert here).
7. **Review the diff** and confirm it is limited to the 4 files above. Do not stage or commit; leave changes unstaged for human review.

### Verification caveat for this environment

`global.json` pins `11.0.100` and `Directory.Build.props:6` targets `net11.0`, but only SDK `10.0.403` is installed here, so any `dotnet build`/`dotnet test` fails before compilation:

```
Requested SDK version: 11.0.100
Installed SDKs: 10.0.403
```

Steps 5–6 must therefore run on a machine/CI image with the .NET 11 SDK. Until then, equivalence rests on §4.5 plus the `rg` audits in steps 1 and 4.

---

## 6. Risks and guardrails

- **Do not add `CultureInfo.InvariantCulture`** to `ToString()` in the new helper — that would be a real (if unlikely) behavior change, turning this from a refactor into a bugfix.
- **Keep `Route` a `const`, not `static readonly`.** FastEndpoints' `Get`/`Put`/`Delete` calls are runtime calls so `static readonly` would compile, but `const` preserves compile-time inlining, metadata shape, and any consumer that uses the member in a constant context.
- **Keep the parameter name `ContributorId`** in the template; renaming it would break request binding.
- **Do not touch `sample/`.** It contains a parallel, independently built app with its own copies, e.g. `sample/src/NimblePros.SampleToDo.Web/Contributors/Delete.DeleteContributorRequest.cs:5-6`, `sample/src/NimblePros.SampleToDo.Web/Contributors/GetById.GetContributorByIdRequest.cs:5-6`, `sample/src/NimblePros.SampleToDo.Web/Contributors/Update.UpdateContributorRequest.cs:7-8`. It is a different assembly and not covered by `tests/Clean.Architecture.FunctionalTests`.
- **Do not touch `MinimalClean/`** — a separate template variant (`ProductFeatures`/`CartFeatures`) that never routes contributor ids.
- **File encoding:** new `.cs` file must be saved as UTF-8 with BOM to match `.editorconfig:21`; a plain UTF-8 file would produce a formatting diff on the next editor pass.

---

## 7. Out of scope (candidates deliberately deferred)

- Same-shape cleanup of the collection route: `Create.cs:64` (`Route = "/Contributors"`) vs the bare literal at `List.cs:14` (`Get("/Contributors")`). Folding both into `ContributorRoutes` would be consistent, but it enlarges the diff beyond the by-id contract and is not needed to remove the duplication identified here.
- Extracting the `ContributorDto` → `ContributorRecord` mapping duplicated at `GetById.cs:56`, `List.cs:127`, and `Update.cs:65`. Deferred because `Update.cs:65` intentionally (or accidentally) passes `""` for the phone number while the others pass `PhoneNumber.ToString()`; a behavior-preserving extraction would need a parameter to encode that difference, and normalizing it would be a behavior change requiring its own review.
- `ResultExtensions.ToGetByIdResult` / `ToUpdateResult` (`src/Clean.Architecture.Web/Extensions/ResultExtensions.cs:36-51`) are thin wrappers over `ToOkOrNotFoundResult` (`:73`). Already factored; collapsing them would only shorten the API, not remove duplication.

---

## 8. Rollback

Revert the 4-file change set (delete `ContributorRoutes.cs`, restore the three literal constants/methods). No migration, configuration, or data changes are involved, so rollback is a plain source revert.
