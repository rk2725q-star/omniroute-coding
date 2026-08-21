# /refactor — Production-Grade Code Refactoring

Refactor: $ARGUMENTS

## Refactor Protocol (≤3 turns):

### Turn 1 — Full Read (Parallel)
Read target + all files that import/use it + tests + types

### Turn 2 — Refactor Everything (Parallel Writes)
Apply ALL improvements in 1 batch:

Code Quality:
- Remove ALL duplication (DRY)
- Extract reusable functions
- Fix naming inconsistencies
- Remove dead code + unused imports
- Add proper TypeScript types (ban `any`)

Performance:
- Fix N+1 patterns
- Add memoization where beneficial
- Optimize expensive loops

Maintainability:
- JSDoc for complex logic
- Break 200+ line files into focused modules
- Improve error messages

### Turn 3 — No Regressions Check
Run existing tests. Fix any breakage in same turn.

Clean code. No regressions. Done.