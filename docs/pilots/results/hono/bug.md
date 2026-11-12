# PILOT_BUG: Handler `Set-Cookie` headers are dropped when `c.res` already has cookies

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

## Suspected bug

`Context`'s `res` setter treats headers already present on an existing response as authoritative and, for `Set-Cookie`, deletes every cookie on the newly assigned response before appending only the old cookies. When middleware has already materialized `c.res` and added a cookie, a downstream handler that returns a fresh `Response` with its own cookie loses that new cookie: `src/context.ts:421-426` removes the new `set-cookie` values and re-adds only `this.#res`'s cookies, and `src/compose.ts:67-68` routes every handler return value through that setter. The result is that only the middleware's cookie survives instead of both cookies being merged, which can silently break authentication, session rotation, and cookie-based middleware.

## Proposed regression test

Add this test to `src/context.test.ts` (or `src/hono.test.ts`):

```ts
it('preserves Set-Cookie from both an existing c.res and a handler response', async () => {
  const app = new Hono()
  app.use('*', async (c, next) => {
    c.res.headers.append('Set-Cookie', 'middleware=1; Path=/')
    await next()
  })
  app.get(
    '/',
    () =>
      new Response('ok', {
        headers: { 'Set-Cookie': 'handler=2; Path=/' },
      })
  )

  const res = await app.request('/')
  const cookies = res.headers.getSetCookie()
  expect(cookies).toHaveLength(2)
  expect(cookies).toEqual(
    expect.arrayContaining(['middleware=1; Path=/', 'handler=2; Path=/'])
  )
})
```

## Evidence

- `src/context.ts:414-433` — the `res` setter clones the incoming response and merges the old response's headers into it.
- `src/context.ts:421-426` — the `set-cookie` branch deletes all `Set-Cookie` headers from the new response and appends only the old response's cookies, so new cookies are lost.
- `src/compose.ts:67-69` — every handler result is assigned through `context.res = res`, triggering that merge after middleware has populated `c.res`.
