# 🌐 OMNIROUTE & CLAUDE CODE — COMPLETE SETUP & ARCHITECTURE GUIDE

> **Documentation Version:** 2.0 (Production Stable)  
> **Target Environment:** Windows / macOS / Linux  
> **Default Proxy Port:** `http://localhost:20128`  
> **Auth Token:** `omniroute`

---

## 📌 TABLE OF CONTENTS
1. [⚡ Quick Start (1-Click Setup)](#-quick-start-1-click-setup)
2. [🏗️ System Architecture](#️-system-architecture)
3. [🔧 Critical Middleware Hooks (Root-Cause Fixes)](#-critical-middleware-hooks-root-cause-fixes)
   - [Hook 1: `disable-thinking` (400 thought_signature Fix)](#hook-1-disable-thinking-400-thought_signature-fix)
   - [Hook 2: `fix-tool-names` (Tool Not Found Fix)](#hook-2-fix-tool-names-tool-not-found-fix)
4. [📦 Combo Configurations & DB Schema](#-combo-configurations--db-schema)
5. [🔄 Cross-Combo Fallback Chains](#-cross-combo-fallback-chains)
6. [⚙️ Claude Code Configuration (`settings.json`)](#️-claude-code-configuration-settingsjson)
7. [🩺 Dynamic Health Check & Auto-Healing (`refresh.py`)](#-dynamic-health-check--auto-healing-refreshpy)
8. [🚀 Custom Claude Code Skills & Commands](#-custom-claude-code-skills--commands)
9. [🚨 Troubleshooting & Error Resolution Matrix](#-troubleshooting--error-resolution-matrix)

---

## ⚡ QUICK START (1-CLICK SETUP)

If you have cloned this repository on a new machine, follow these 3 steps:

### Step 1: Start OmniRoute
Launch OmniRoute desktop or background service. Ensure it is running on `http://localhost:20128`.

### Step 2: Run the Master Setup Script
```bash
python setup_omniroute.py
```
This script automatically:
- Injects both critical middleware hooks (`disable-thinking` and `fix-tool-names`) into `storage.sqlite`.
- Configures all 4 resilient model combos with the proper object array format.
- Sets up cross-combo fallback chains in SQLite.
- Synchronizes workspace and global `.claude/settings.json` files.

### Step 3: Restart OmniRoute & Launch Claude Code
1. **Completely restart OmniRoute** (Quit and Reopen so DB middleware hooks load into memory).
2. Open terminal in this repository and launch:
```bash
claude
```

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌────────────────────────────────────────────────────────┐
│                   Claude Code CLI                      │
│      (ANTHROPIC_BASE_URL: http://localhost:20128)      │
└──────────────────────────┬─────────────────────────────┘
                           │ Anthropic Messages API
                           ▼
┌────────────────────────────────────────────────────────┐
│                   OmniRoute Proxy                      │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Middleware Hook 0: disable-thinking              │  │
│  │ (Forces thinkingBudget=0; strips thought blocks) │  │
│  └──────────────────────┬───────────────────────────┘  │
│                         ▼                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Combos & Cross-Combo Fallback Engine             │  │
│  │ (Intelligent routing across 4 multi-model combos)│  │
│  └──────────────────────┬───────────────────────────┘  │
│                         ▼                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Middleware Hook 1: fix-tool-names                │  │
│  │ (Maps lowercase model tools -> Claude TitleCase) │  │
│  └──────────────────────────────────────────────────┘  │
└──────────┬──────────────────┬──────────────────┬───────┘
           │                  │                  │
           ▼                  ▼                  ▼
   Google Gemini API     NVIDIA NIM API     OpenCode / Router
   (6-Key Rotation)    (Nemotron 550B/30B)  (DeepSeek / Free)
```

---

## 🔧 CRITICAL MIDDLEWARE HOOKS (ROOT-CAUSE FIXES)

OmniRoute features an internal JavaScript middleware engine stored in SQLite table `middleware_hooks`.

### Hook 1: `disable-thinking` (Priority 0)
* **Problem:** Gemini 3.7 / 3.6 / Thinking models output internal `<thought>` tokens during tool calls. When OmniRoute converts Gemini format to Anthropic format, `thought_signature` is omitted, causing Google Gemini API to reject subsequent tool turns with:
  `API Error: 400 Function call is missing a thought_signature in functionCall parts`.
* **Solution:** Intercept the request before transmission, inject `generationConfig.thinkingConfig = { thinkingBudget: 0 }`, and strip raw thought blocks from history.

```javascript
if (request && request.body) {
  let body = request.body;
  if (!body.generationConfig) body.generationConfig = {};
  body.generationConfig.thinkingConfig = { thinkingBudget: 0 };
  
  if (body.contents && Array.isArray(body.contents)) {
    body.contents = body.contents.map(content => {
      if (content.parts && Array.isArray(content.parts)) {
        content.parts = content.parts.map(part => {
          if (part.functionCall) {
            delete part.functionCall.thought;
            delete part.functionCall.thoughtSignature;
            delete part.functionCall.thought_signature;
          }
          return part;
        }).filter(part => part.thought !== true);
      }
      return content;
    });
  }
  request.body = body;
}
return request;
```

---

### Hook 2: `fix-tool-names` (Priority 1)
* **Problem:** Non-Anthropic models (Gemini, OpenCode, NVIDIA) return tool names in lowercase (e.g. `glob`, `read`, `write`, `edit`, `bash`). Claude Code expects exact TitleCase (`Glob`, `Read`, `Write`, `Edit`, `Bash`), otherwise throwing:
  `<tool_use_error>Error: No such tool available: glob</tool_use_error>`.
* **Solution:** Intercept response stream and payload, normalizing tool names to TitleCase.

```javascript
const MAP = {
  'read': 'Read', 'write': 'Write', 'edit': 'Edit', 'multiedit': 'MultiEdit',
  'multi_edit': 'MultiEdit', 'bash': 'Bash', 'glob': 'Glob', 'grep': 'Grep',
  'task': 'Task', 'webfetch': 'WebFetch', 'web_fetch': 'WebFetch',
  'todoread': 'TodoRead', 'todowrite': 'TodoWrite'
};
if (response && response.content) {
  response.content = response.content.map(b => {
    if (b.type === 'tool_use' && b.name) {
      const l = b.name.toLowerCase().replace(/-/g, '_');
      if (MAP[l]) b.name = MAP[l];
    }
    return b;
  });
}
if (response && response.choices) {
  response.choices = response.choices.map(c => {
    if (c.message && c.message.tool_calls) {
      c.message.tool_calls = c.message.tool_calls.map(tc => {
        if (tc.function && tc.function.name) {
          const l = tc.function.name.toLowerCase().replace(/-/g, '_');
          if (MAP[l]) tc.function.name = MAP[l];
        }
        return tc;
      });
    }
    return c;
  });
}
return response;
```

---

## 📦 COMBO CONFIGURATIONS & DB SCHEMA

OmniRoute requires combos in the `combos` table to use an **Array of Objects** format rather than plain string arrays. Storing raw string arrays will cause UI errors (`Combo Control Center unavailable / Combo not found`).

### Correct Combo JSON Format:
```json
{
  "name": "gemini-fallback",
  "strategy": "fallback",
  "models": [
    { "kind": "model", "model": "gemini/gemini-3.5-flash-lite", "providerId": "gemini" },
    { "kind": "model", "model": "gemini/gemini-3.1-flash-lite", "providerId": "gemini" }
  ],
  "capabilities": {
    "multimodal": false,
    "reasoning": false,
    "caching": false
  }
}
```

### The 4 Configured Combos:

| Combo Name | Primary Provider | Included Models | Best Use |
|---|---|---|---|
| **`free coding 2`** | Google Gemini | `gemini-3.5-flash-lite` (safe/fast), `3.1-flash-lite`, `3.5-flash`, `3.6-flash`, `3.7-flash` | Default coding & Sonnet equivalent |
| **`nvidia free`** | NVIDIA NIM | `nemotron-3-ultra-550b-a55b`, `nemotron-3.5-lightning-30b-a3b`, `minimax-m3`, `nemotron-3-super-120b-a12b` | Heavy reasoning & Opus equivalent |
| **`gemini-fallback`** | Google Gemini | `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite` | Ultra-fast Haiku / Small-fast tasks |
| **`free code`** | OpenCode | `oc/nemotron-3-ultra-free`, `oc/deepseek-v4-flash-free`, `oc/mimo-v2.5-free` | Free OpenCode backup |

---

## 🔄 CROSS-COMBO FALLBACK CHAINS

Configured in `domain_fallback_chains` table. If every model inside a combo encounters rate limits or upstream 502/503 errors, OmniRoute immediately falls back to the next combo in sequence:

```
[nvidia free fails] ──> [free coding 2] ──> [gemini-fallback] ──> [gemini-3.5-flash-lite]
[free coding 2 fails] ──> [gemini-fallback] ──> [nvidia free] ──> [gemini-3.5-flash-lite]
[free code fails] ──> [free coding 2] ──> [gemini-fallback] ──> [gemini-3.5-flash-lite]
```

---

## ⚙️ CLAUDE CODE CONFIGURATION (`settings.json`)

Located at `.claude/settings.json` (Workspace) and `~/.claude/settings.json` (Global User):

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_AUTH_TOKEN": "omniroute",
    "ANTHROPIC_MODEL": "free coding 2",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "free coding 2",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "nvidia free",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "gemini-fallback",
    "ANTHROPIC_SMALL_FAST_MODEL": "gemini-fallback",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

---

## 🩺 DYNAMIC HEALTH CHECK & AUTO-HEALING (`refresh.py`)

Run this script anytime Gemini or upstream providers experience temporary outages:

```bash
python refresh.py
```

### What `refresh.py` does:
1. Dispatches real-time ping requests to all Gemini and provider models.
2. Identifies live vs. dead models.
3. Automatically updates SQLite `model_intelligence` ELO ratings so working models take top priority.
4. Rebuilds combo chains and syncs `settings.json` with the best responsive model.

---

## 🚀 CUSTOM CLAUDE CODE SKILLS & COMMANDS

Located in `.claude/commands/`:

| Command | Purpose |
|---|---|
| `/mega-build` | Fullstack single-request autonomous application builder. |
| `/sprint` | Fast multi-feature batch builder. |
| `/fullstack` | Generates schema, backend, frontend, and tests in one turn. |
| `/fix` | Systematic root-cause debugging and bug repair. |
| `/refactor` | Architecture cleanup, DRY/SOLID enforcement, and optimization. |
| `/scan` | Full repo architecture and security audit. |
| `/feature` | End-to-end new feature development. |
| `/turbo` | Ultra-fast single-turn code transformation. |

---

## 🚨 TROUBLESHOOTING & ERROR MATRIX

| Error Message | Root Cause | Instant Fix |
|---|---|---|
| `API Error: 400 [400]: Function call is missing a thought_signature` | Thinking tokens generated without signature during tool turns | Run `python setup_omniroute.py` and restart OmniRoute to apply `disable-thinking` hook (`thinkingBudget=0`). |
| `<tool_use_error>Error: No such tool available: glob` | Model outputted lowercase tool name | Restart OmniRoute so `fix-tool-names` hook normalizes `glob -> Glob`. |
| `Combo Control Center unavailable / Combo not found` | Combos table `data` field used string array instead of object array | Run `python setup_omniroute.py` to regenerate combos with `{kind: "model", model: "...", providerId: "..."}`. |
| `HTTP 502 / 503 Bad Gateway on Gemini` | Google Gemini upstream server overload on non-lite models | Run `python refresh.py` to automatically switch primary to `gemini-3.5-flash-lite`. |
| `HTTP 410 Gone on NVIDIA models` | Old model names deprecated by NVIDIA (e.g. date suffix added) | Use updated model IDs: `nemotron-3-ultra-550b-a55b` and `nemotron-3.5-lightning-30b-a3b`. |
| `HTTP 403 on OpenCode models` | OpenCode API token expired | Update API key in OmniRoute UI -> Connections -> OpenCode. |
