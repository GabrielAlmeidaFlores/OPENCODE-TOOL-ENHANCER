# PILOT_REFACTOR

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

## Refactor: extract the duplicated bearer-token / 401-challenge helpers shared by `jwt` and `jwk`

**Type:** behavior-preserving refactor (no API change, no runtime change)
**Scope:** create one internal utility module; update two middleware files
**Status:** plan only (this document does not modify source)

---

## 1. Summary

`src/middleware/jwt/jwt.ts` and `src/middleware/jwk/jwk.ts` each contain the same two
non-trivial pieces of logic:

1. **Bearer-token extraction** — read the configured `Authorization` header, validate its
   `Bearer <token>` structure, and otherwise fall back to a (optionally signed) cookie.
2. **`unauthorizedResponse`** — build the RFC 6750 `WWW-Authenticate` 401 response, including
   escaping of the `realm` and `error_description` values.

Both blocks are byte-for-byte identical between the two files. This pilot moves them into a
single internal module, `src/utils/bearer-auth.ts`, and has both middlewares import them.
The module is internal (not a package entry point), mirroring the existing
`src/utils/basic-auth.ts` helper used by the `basic-auth` middleware.

---

## 2. Evidence of duplication

The two duplicated regions were compared with `diff` and hashed:

| Region | jwt | jwk | Result |
| --- | --- | --- | --- |
| Token extraction (42 lines) | `src/middleware/jwt/jwt.ts:79-120` | `src/middleware/jwk/jwk.ts:79-120` | identical (`sha1 5203f80d…`) |
| `unauthorizedResponse` (21 lines) | `src/middleware/jwt/jwt.ts:165-185` | `src/middleware/jwk/jwk.ts:176-196` | identical (`sha1 bff072d6…`) |

Both files also duplicate the same cookie imports (`getCookie`, `getSignedCookie`) at
`src/middleware/jwt/jwt.ts:7` and `src/middleware/jwk/jwk.ts:7`.

There is an existing precedent for internal auth helpers:
`src/utils/basic-auth.ts:9` exports `auth(req)` and is imported by
`src/middleware/basic-auth/index.ts:9`; it is intentionally **not** listed in
`package.json` or `jsr.json`. The new module follows the same convention.

---

## 3. Before

### 3.1 Duplicated token extraction (`jwt.ts:79-120` == `jwk.ts:79-120`)

```ts
const headerName = options.headerName || 'Authorization'

const credentials = ctx.req.raw.headers.get(headerName)
let token
if (credentials) {
  const parts = credentials.split(/\s+/)
  if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer') {
    const errDescription = 'invalid credentials structure'
    throw new HTTPException(401, {
      message: errDescription,
      res: unauthorizedResponse({
        ctx,
        error: 'invalid_request',
        errDescription,
        realm: options.realm,
      }),
    })
  } else {
    token = parts[1]
  }
} else if (options.cookie) {
  if (typeof options.cookie == 'string') {
    token = getCookie(ctx, options.cookie)
  } else if (options.cookie.secret) {
    if (options.cookie.prefixOptions) {
      token = await getSignedCookie(
        ctx,
        options.cookie.secret,
        options.cookie.key,
        options.cookie.prefixOptions
      )
    } else {
      token = await getSignedCookie(ctx, options.cookie.secret, options.cookie.key)
    }
  } else {
    if (options.cookie.prefixOptions) {
      token = getCookie(ctx, options.cookie.key, options.cookie.prefixOptions)
    } else {
      token = getCookie(ctx, options.cookie.key)
    }
  }
}
```

### 3.2 Duplicated 401 challenge builder (`jwt.ts:165-185` == `jwk.ts:176-196`)

```ts
function unauthorizedResponse(opts: {
  ctx: Context
  error: string
  errDescription: string
  statusText?: string
  realm?: string
}) {
  // `realm` and `error_description` end up inside a quoted-string, so any `"`
  // they contain has to be escaped or the header is cut short. Same handling as
  // the bearer-auth middleware.
  const realm = (opts.realm ?? opts.ctx.req.url).replace(/[\\"]/g, '\\$&')
  const errDescription = opts.errDescription.replace(/[\\"]/g, '\\$&')

  return new Response('Unauthorized', {
    status: 401,
    statusText: opts.statusText,
    headers: {
      'WWW-Authenticate': `Bearer realm="${realm}",error="${opts.error}",error_description="${errDescription}"`,
    },
  })
}
```

---

## 4. After

### 4.1 New internal module — `src/utils/bearer-auth.ts`

```ts
import type { Context } from '../context'
import { getCookie, getSignedCookie } from '../helper/cookie'
import type { CookiePrefixOptions } from './cookie'

export type BearerTokenCookie =
  | string
  | { key: string; secret?: string | BufferSource; prefixOptions?: CookiePrefixOptions }

export type BearerTokenResult = {
  token: string | undefined
  invalidStructure: boolean
}

/**
 * Extract a bearer token from the Authorization header, falling back to a
 * (optionally signed) cookie. `invalidStructure` is true only when a header
 * is present but is not a valid `Bearer <token>` pair.
 */
export const extractBearerToken = async (
  ctx: Context,
  headerName: string,
  cookie?: BearerTokenCookie
): Promise<BearerTokenResult> => {
  const credentials = ctx.req.raw.headers.get(headerName)
  if (credentials) {
    const parts = credentials.split(/\s+/)
    if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer') {
      return { token: undefined, invalidStructure: true }
    }
    return { token: parts[1], invalidStructure: false }
  }

  if (!cookie) {
    return { token: undefined, invalidStructure: false }
  }

  if (typeof cookie === 'string') {
    return { token: getCookie(ctx, cookie), invalidStructure: false }
  }

  const token = cookie.secret
    ? cookie.prefixOptions
      ? await getSignedCookie(ctx, cookie.secret, cookie.key, cookie.prefixOptions)
      : await getSignedCookie(ctx, cookie.secret, cookie.key)
    : cookie.prefixOptions
      ? getCookie(ctx, cookie.key, cookie.prefixOptions)
      : getCookie(ctx, cookie.key)

  // `getSignedCookie` may return `false`; it is only consumed by truthiness
  // checks downstream, so normalise it to `undefined`.
  return { token: token || undefined, invalidStructure: false }
}

export const unauthorizedResponse = (opts: {
  ctx: Context
  error: string
  errDescription: string
  statusText?: string
  realm?: string
}): Response => {
  const realm = (opts.realm ?? opts.ctx.req.url).replace(/[\\"]/g, '\\$&')
  const errDescription = opts.errDescription.replace(/[\\"]/g, '\\$&')

  return new Response('Unauthorized', {
    status: 401,
    statusText: opts.statusText,
    headers: {
      'WWW-Authenticate': `Bearer realm="${realm}",error="${opts.error}",error_description="${errDescription}"`,
    },
  })
}
```

### 4.2 `src/middleware/jwt/jwt.ts` call site

Replace the block at lines 79-120 with:

```ts
const headerName = options.headerName || 'Authorization'
const { token, invalidStructure } = await extractBearerToken(ctx, headerName, options.cookie)

if (invalidStructure) {
  const errDescription = 'invalid credentials structure'
  throw new HTTPException(401, {
    message: errDescription,
    res: unauthorizedResponse({
      ctx,
      error: 'invalid_request',
      errDescription,
      realm: options.realm,
    }),
  })
}
```

Delete the local `unauthorizedResponse` definition at lines 165-185 and replace the
`getCookie`/`getSignedCookie` import at line 7 with:

```ts
import { extractBearerToken, unauthorizedResponse } from '../../utils/bearer-auth'
```

The `CookiePrefixOptions` import at line 10 stays (still used by the option type at line 58).

### 4.3 `src/middleware/jwk/jwk.ts` call site

Apply the same replacement at lines 79-120 and delete the local helper at lines 176-196.
The only intentional difference is preserved verbatim: the no-token branch keeps its
`allow_anon` short-circuit.

```ts
const headerName = options.headerName || 'Authorization'
const { token, invalidStructure } = await extractBearerToken(ctx, headerName, options.cookie)

if (invalidStructure) {
  const errDescription = 'invalid credentials structure'
  throw new HTTPException(401, {
    message: errDescription,
    res: unauthorizedResponse({
      ctx,
      error: 'invalid_request',
      errDescription,
      realm: options.realm,
    }),
  })
}

if (!token) {
  if (options.allow_anon) {
    return next()
  }
  // ... unchanged ...
}
```

`jwk.ts` keeps its own `CookiePrefixOptions` import (line 10, used at line 56).

---

## 5. Ordered implementation steps

1. Create `src/utils/bearer-auth.ts` with `extractBearerToken` and `unauthorizedResponse`
   exactly as in §4.1.
2. In `src/middleware/jwt/jwt.ts`: remove `getCookie, getSignedCookie` from the import at
   line 7; add the new import; replace lines 79-120 with the §4.2 call site; delete lines
   165-185.
3. In `src/middleware/jwk/jwk.ts`: remove `getCookie, getSignedCookie` from the import at
   line 7; add the new import; replace lines 79-120 with the §4.3 call site; delete lines
   176-196.
4. Do **not** touch `index.ts`, option types, `package.json`, or `jsr.json` — the new module
   is internal, exactly like `src/utils/basic-auth.ts`.

---

## 6. Why this is behavior-preserving

- **Same token precedence and parsing:** header is checked first, cookie second; the same
  `split(/\s+/)`, `parts.length !== 2`, and lowercase `bearer` checks are used
  (`jwt.ts:84-98`, `jwk.ts:84-98`).
- **Same cookie fallback:** identical branch order and identical `getCookie` /
  `getSignedCookie` calls, including `prefixOptions` handling (`jwt.ts:99-120`,
  `jwk.ts:99-120`).
- **Same challenge response:** identical status (`401`), body (`Unauthorized`), optional
  `statusText`, and identical `WWW-Authenticate` formatting/escaping
  (`jwt.ts:165-185`, `jwk.ts:176-196`).
- **Same control flow on malformed headers:** `invalidStructure` reproduces the original
  early throw, so the cookie fallback is still skipped for a malformed `Authorization`
  header.
- **Normalising `false`/`''` to `undefined`** is runtime-equivalent because the token is only
  consumed by `if (!token)` and by `Jwt.verify(...)`, which is reached only when the token
  is truthy.
- **`allow_anon` is untouched:** it remains only in the `jwk` no-token branch
  (`jwk.ts:122-125`).

---

## 7. Verification plan

Behavior is already pinned by the existing middleware tests, which assert exact challenge
headers:

```sh
pnpm exec vp test --run src/middleware/jwt/index.test.ts src/middleware/jwk/index.test.ts
pnpm check          # typecheck + lint + format
pnpm build          # ensure the new internal module bundles cleanly
```

Relevant behavior-pinning assertions:
`src/middleware/jwt/index.test.ts:98`, `src/middleware/jwk/index.test.ts:92`
(`invalid credentials structure`), and the realm-escaping cases at
`src/middleware/jwt/index.test.ts:798` and `src/middleware/jwt/index.test.ts:811`.

---

## 8. Files affected

| Action | File |
| --- | --- |
| Create | `src/utils/bearer-auth.ts` (internal, no export-map entry) |
| Modify | `src/middleware/jwt/jwt.ts` |
| Modify | `src/middleware/jwk/jwk.ts` |
| Unchanged | everything else |

---

## 9. Key references

- `src/middleware/jwt/jwt.ts:79-120` — duplicated bearer-token extraction block (first copy).
- `src/middleware/jwk/jwk.ts:79-120` — duplicated bearer-token extraction block (second copy, identical).
- `src/middleware/jwt/jwt.ts:165-185` — duplicated `unauthorizedResponse` helper (first copy).
- `src/middleware/jwk/jwk.ts:176-196` — duplicated `unauthorizedResponse` helper (second copy, identical).
- `src/middleware/jwt/jwt.ts:7` and `src/middleware/jwk/jwk.ts:7` — duplicated `getCookie` / `getSignedCookie` imports to be consolidated.
- `src/utils/basic-auth.ts:9` — existing precedent for an internal auth helper module that is not a package export.
- `src/middleware/jwt/index.test.ts:98` and `src/middleware/jwk/index.test.ts:92` — existing tests that pin the exact 401 challenge behavior.
