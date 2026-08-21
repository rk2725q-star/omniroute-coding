# /fix — Root Cause Bug Fix

Fix this issue: $ARGUMENTS

## Fix Protocol (≤2 turns):

### Turn 1 — Parallel Diagnosis
Read simultaneously:
- File where error occurs + its imports
- Related test files
- Config/env files that affect this code
- Stack trace / error logs

### Turn 2 — Fix + Verify
- Fix ROOT CAUSE (never suppress errors)
- Fix all related issues found during diagnosis
- Update tests if behavior changes
- Run the failing command — confirm it PASSES

## Rules:
- Fix in as many files as needed, all in 1 parallel write batch
- Never say "try this" — verify it actually works
- If first fix attempt fails, try alternative in same turn
- No partial fixes — complete the fix end-to-end