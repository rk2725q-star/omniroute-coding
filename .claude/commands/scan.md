# /scan — Deep Codebase Analysis + Auto-Fix

Scan and improve: $ARGUMENTS (or entire project if blank)

## Scan Protocol (≤2 turns):

### Turn 1 — Parallel Full Scan
Read ALL source files, configs, package.json, tests simultaneously.

### Turn 2 — Report + Auto-Fix Criticals (same turn)
Generate structured report AND fix critical issues:

Report format:
CRITICAL (auto-fixing now): [list] 
PERFORMANCE ISSUES: [file:line — description]
CODE QUALITY: [file:line — description]
SECURITY RISKS: [file:line — description]
GOOD PATTERNS TO KEEP: [list]
NEXT RECOMMENDED ACTIONS: [prioritized]

Auto-fix in same turn:
- All security vulnerabilities
- Runtime errors and broken logic
- Exposed secrets or credentials
- Type errors causing crashes

Scan everything. Fix criticals immediately. Report clearly.