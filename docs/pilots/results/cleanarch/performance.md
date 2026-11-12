# Pilot Performance Review

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

Scope: static inspection of 5 backend source files. No tests or benchmarks were run.

- **Deep-page offset pagination plus a second `COUNT(*)` round trip on every list request.** `ListContributorsQueryService.ListAsync` issues the page query with `Skip((page - 1) * perPage).Take(perPage)` and then a separate `CountAsync()` for the total (`src/Clean.Architecture.Infrastructure/Data/Queries/ListContributorsQueryService.cs:21-27`). The `OFFSET` cost grows linearly with page depth even with the primary-key index, and the count is re-computed for every request (no caching), so each `GET /Contributors` is two DB round trips and a full-table count. The raw SQL projection is a good optimization (`ListContributorsQueryService.cs:19`), but pagination strategy is the dominant cost at scale.

- **`SaveChanges` interceptor scans the entire change tracker on every save.** `EventDispatchInterceptor.SavedChangesAsync` calls `ChangeTracker.Entries<HasDomainEventsBase>()` and then materializes/filters with `.Select(...).Where(e => e.DomainEvents.Any()).ToArray()` (`src/Clean.Architecture.Infrastructure/Data/EventDispatcherInterceptor.cs:21-24`) for every successful save. That is O(tracked entities) per write, and events are dispatched inside the save pipeline (`EventDispatcherInterceptor.cs:27`), extending request latency for any handler that writes while the context has many tracked entities. It also runs for writes unrelated to contributors.

- **Read endpoints return tracked-entity-friendly materialization upstream and no query caching.** The list query does use `AsNoTracking()` (`ListContributorsQueryService.cs:24`), but the mapper then allocates a second full list and re-projects every row (`src/Clean.Architecture.Web/Contributors/List.cs:126-128`), and the endpoint is anonymous with no output/response caching (`List.cs:15`). `ContributorConfiguration` defines no index beyond the primary key (`src/Clean.Architecture.Infrastructure/Data/Config/ContributorConfiguration.cs:9-24`), so any future filtering/sorting by name or status (`ContributorConfiguration.cs:14-24`) will degrade to scans; the repository wrapper adds no batching (`src/Clean.Architecture.Infrastructure/Data/EfRepository.cs:4-5`).

## Measurement plan

Run a read-only load test against `GET /Contributors` with `per_page=10` at page 1, 100, and 10,000, using a seeded table of at least 1M rows. Capture p50/p95/p99 latency per page depth and record DB metrics (query duration and rows examined) via EF Core command logging or OpenTelemetry spans. Acceptance target: p95 < 100 ms at page 1 and < 250 ms at page 10,000; investigate keyset pagination or a cached count if either threshold is exceeded. Separately, benchmark a bulk write of 1,000 entities with 100 already tracked to quantify the interceptor overhead.
