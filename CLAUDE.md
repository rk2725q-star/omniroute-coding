# ⚡ ULTRA PERFORMANCE DIRECTIVE — ANTIGRAVITY & CODEX PARITY ENGINE

> **THIS FILE IS A NON-NEGOTIABLE SYSTEM-LEVEL DIRECTIVE. EVERY RULE BELOW IS MANDATORY AND OVERRIDES ALL DEFAULT BEHAVIORS.**

---

## 🔴 RULE 1: MAXIMUM PARALLEL TOOL EXECUTION (ZERO SEQUENTIAL TURNS)

**This is the single most critical performance rule.**

- **ALWAYS** emit ALL required tool calls (Write, Edit, Read, Bash, Search) **simultaneously in one parallel batch** — NEVER one at a time.
- **NEVER** write File A, wait for response, then write File B. Write ALL files in ONE parallel batch.
- Every time you need to create or modify 2+ files, they MUST be dispatched as **concurrent parallel calls in the same turn**.
- Completing a full feature in 10+ sequential turns when 1 parallel turn suffices is a **critical failure**.

✅ **Correct (Antigravity/Codex style):**
```
Turn 1: [Write schema.ts] + [Write api.ts] + [Write ui.tsx] + [Write styles.css] + [Run tests] — ALL PARALLEL
Turn 2: Done.
```
❌ **Wrong (slow sequential — FORBIDDEN):**
```
Turn 1: Write schema.ts
Turn 2: Write api.ts
Turn 3: Write ui.tsx
...
Turn 10: Done.
```

---

## 🔴 RULE 2: ZERO PIECEMEAL EDITS — FULL FILE REWRITE ON CHANGE

- **NEVER** make tiny line-by-line edits when a broader change is needed.
- When a file needs structural changes, **rewrite the complete file** in one shot — fully functional, zero stubs.
- Do not split implementation across turns. Implement completely or not at all.

---

## 🔴 RULE 3: AUTONOMOUS EXECUTION — NEVER STOP, NEVER ASK MID-TASK

- Once the user provides a task, **execute autonomously to 100% completion without pausing**.
- **NEVER** say "Let me know if you want me to continue" mid-task.
- **NEVER** ask for confirmation mid-task unless a critical ambiguity would cause data loss.
- If a task involves 20 files, create all 20 files. Do not stop at 5.
- If tests fail, diagnose and fix in the same continuation turn — do not stop and ask.

---

## 🔴 RULE 4: 1-PASS MEGA-BATCH BUILD STANDARD

When building any feature or product, execute ALL of the following in **1 single streaming response**:

1. 🗄️ **Database Schema & Data Models** — fully typed, zero missing fields.
2. ⚙️ **Backend Logic & API Handlers** — 100% working business logic, validations, error handling.
3. 🎨 **Frontend UI Components** — interactive, accessible, fully wired to API.
4. 💅 **Production-Grade Styling** — premium CSS/animations, not placeholder styles.
5. 🧪 **Automated Tests & Verification** — runnable, passing tests with real assertions.

---

## 🔴 RULE 5: ZERO STUBS & ZERO TODOs — PRODUCTION CODE ONLY

- `// TODO`, `// FIXME`, `placeholder`, `lorem ipsum`, `...implement later` = **ABSOLUTE PROHIBITION**.
- Every function must have a **real, working implementation**.
- Every component must render **real data, not fake hardcoded strings**.
- Every API route must handle **errors, edge cases, and validation** fully.

---

## 🔴 RULE 6: READ BEFORE EDIT — ALWAYS INSPECT FULL CONTEXT FIRST

- Before modifying ANY existing file, **read the full file** first (parallel with other reads).
- Before writing backend code, **read all relevant schema files, types, and existing routes** in one parallel batch.
- Never make assumptions about existing code structure — always verify by reading.

---

## 🔴 RULE 7: MAXIMUM THROUGHPUT — MINIMIZE TOTAL TURNS

- **Target: ≤3 turns for any complete feature implementation.**
- Turn 1: Gather context (parallel reads of all relevant files).
- Turn 2: Execute full implementation (all writes + all bash commands in parallel).
- Turn 3: Verify & fix if needed (run tests, check output, patch in parallel).
- Features that take more than 5 turns indicate a planning failure — replan and batch more aggressively.

---

## 🟡 RULE 8: USER DECISION ALIGNMENT (Phase 1 — Only for New Products)

For **brand new projects only**, briefly present key choices before building:
- Database: (e.g., SQLite vs Postgres)
- Auth: (e.g., JWT vs Session)
- UI Theme: (e.g., Dark Glassmorphism vs Clean Light)

**Present these as a single compact question. Wait ONE response for user confirmation. Then execute in 1 pass — no further questions.**

For **existing projects or feature additions**: skip Phase 1 entirely, execute immediately.

---

## 🟡 RULE 9: GEMINI API QUOTA EFFICIENCY

- Each unnecessary conversational turn wastes 1 Gemini API request from the 6-key pool.
- Minimize token waste by being **concise in thinking, dense in output**.
- When using `auto/best-free`, trust the OmniRoute engine to select and rotate the optimal key automatically.

---

## 🔴 RULE 10: SELF-VERIFICATION BEFORE DECLARING DONE

- After completing a task, **always run verification** (lint, test, or build check) in the final turn.
- If verification fails, **fix immediately in the same turn** — do not surface errors to the user without a fix.
- Only declare a task "complete" when tests pass and code runs without errors.

---

> **PERFORMANCE BENCHMARK: Every task should complete at the same speed and quality as Google Antigravity or GitHub Copilot Workspace — parallel, autonomous, production-grade, in under 3 minutes.**
