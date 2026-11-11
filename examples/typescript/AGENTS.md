# AGENTS.md — TypeScript example

## Commands

```bash
npm install
npm run build
npm run lint
npm test
```

Run `npm test` before declaring a task complete. It builds and runs `node --test dist`.

## Structure

- `src/validation.ts` — request validation
- `src/pricing.ts` — pricing rules (contains intentional duplication)
- `src/repository.ts` — order loading (contains an intentional N+1)
- `src/files.ts` — file resolution (contains an intentional traversal bug)
- `src/app.test.ts` — tests

## Conventions

- TypeScript strict mode; no `any` in new code.
- Use ESM imports with the `.js` extension in source.
- Keep functions pure where possible.
- Add a test for every behavior change.

## Safety

Do not read `.env` files. Do not add runtime dependencies without approval.
