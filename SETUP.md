# 🌐 OMNIROUTE & CLAUDE CODE — A to Z MASTER SETUP & ARCHITECTURE GUIDE

> **Documentation Version:** 2.0 (Production Stable — Full A to Z Specification)  
> **Target Environment:** Windows / macOS / Linux  
> **Default Proxy Port:** `http://localhost:20128`  
> **Auth Token:** `omniroute`

---

## 📌 TABLE OF CONTENTS
1. [⚡ Quick Start (1-Click Setup)](#-quick-start-1-click-setup)
2. [🏛️ Configured AI Providers & Accounts](#️-configured-ai-providers--accounts)
3. [📦 The 4 Production Combos & Model Roles](#-the-4-production-combos--model-roles)
4. [🔧 Critical Middleware Hooks (Root-Cause Fixes)](#-critical-middleware-hooks-root-cause-fixes)
   - [Hook 1: `disable-thinking` (400 thought_signature Fix)](#hook-1-disable-thinking-400-thought_signature-fix)
   - [Hook 2: `fix-tool-names` (Tool Not Found Fix)](#hook-2-fix-tool-names-tool-not-found-fix)
5. [🔀 Cross-Combo Fallback Routing](#-cross-combo-fallback-routing)
6. [⚙️ Claude Code Environment Configuration (`settings.json`)](#️-claude-code-environment-configuration-settingsjson)
7. [🩺 Automation Scripts (`setup_omniroute.py` & `refresh.py`)](#-automation-scripts-setup_omniroutepy--refreshpy)
8. [🚀 8 Custom Claude Code Skills & Commands](#-8-custom-claude-code-skills--commands)
9. [🚨 Comprehensive Error Troubleshooting Matrix](#-comprehensive-error-troubleshooting-matrix)
10. [🧠 Architecture & Request Flow Mental Model](#-architecture--request-flow-mental-model)

---

## ⚡ QUICK START (1-CLICK SETUP)

புதிய machine அல்லது workspace-ல் இந்த repository-ஐ clone செய்தால், கீழ்கண்ட 3 படிகளில் முழு setup-ஐயும் முடிக்கலாம்:

### Step 1: Start OmniRoute
Start OmniRoute desktop application or background service. Verify that the proxy is active on `http://localhost:20128`.

### Step 2: Run the Master Setup Script
```bash
python setup_omniroute.py
```
This script automatically:
- Injects both critical middleware hooks (`disable-thinking` and `fix-tool-names`) into `storage.sqlite`.
- Configures all 4 resilient model combos with the proper object array format (`{kind: "model", model: "...", providerId: "..."}`).
- Sets up cross-combo fallback chains in SQLite.
- Synchronizes workspace and global `.claude/settings.json` files.

### Step 3: Restart OmniRoute & Launch Claude Code
1. **Completely restart OmniRoute** (Close and reopen so SQLite middleware hooks are loaded into active memory).
2. Open your terminal in this repository and launch:
```bash
claude
```

---

## 🏛️ CONFIGURED AI PROVIDERS & ACCOUNTS

OmniRoute-ல் நாம் சேர்த்துள்ள AI Providers மற்றும் அவற்றின் Key Management விவரங்கள்:

| Provider | Accounts / Keys | முக்கிய நோக்கம் | சிறப்பு அம்சம் & பலன் |
|---|---|---|---|
| **Google Gemini** | **6 API Keys** (Key 1 to Key 6) | Primary Coding & Fast Fallback | 6 Keys-ஐ Round-Robin முறையில் சுழற்றுவதால் **Rate Limits (429) முற்றிலும் தவிர்க்கப்படுகிறது**. |
| **NVIDIA NIM** | **3 Connections** (`v4flash`, `main-2`, `main-3`) | Heavy Reasoning & Architecture (Opus Level) | **Nemotron 550B Ultra**, **Nemotron 30B Lightning**, **MiniMax M3** போன்ற massive open models. |
| **OpenCode / OpenRouter** | **2 Connections** (`OpenCode Account 1`, `main`) | Auxiliary Free Coding Fallback | DeepSeek V4 Flash, Mimo, Nemotron Ultra Free models. |
| **Ollama Local** | `qwen 2.5 coder 3b` | Offline / Local Backup | Internet இல்லாத போதும் local-ஆக இயங்கும் backup. |
| **Cline / ClinePass** | `Ranjith Kumar 2` | Auxiliary Token Routing | Secondary routing bridge. |

---

## 📦 THE 4 PRODUCTION COMBOS & MODEL ROLES

OmniRoute-ல் நாம் 4 பிரத்யேக Combos உருவாக்கியுள்ளோம். இவை ஒவ்வொன்றும் குறிப்பிட்ட பணிக்கு உகந்ததாக வடிவமைக்கப்பட்டுள்ளன:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        4 ACTIVE COMBOS                                 │
├──────────────────────┬──────────────────────┬──────────────────────────┤
│ 1. free coding 2     │ 2. nvidia free       │ 3. gemini-fallback       │
│ (Primary / Sonnet)   │ (Reasoning / Opus)   │ (Ultra-Fast / Haiku)     │
├──────────────────────┴──────────────────────┴──────────────────────────┤
│ 4. free code (OpenCode Suite Backup)                                   │
└────────────────────────────────────────────────────────────────────────┘
```

### 1️⃣ Combo: `free coding 2` (Primary Sonnet Equivalent)
* **Strategy:** `Intelligent Auto / Fallback`
* **Models வரிசை (Non-Thinking Models First for Safety):**
  1. `gemini/gemini-3.5-flash-lite` *(Ultra Fast, No Thinking overhead)*
  2. `gemini/gemini-3.1-flash-lite` *(High Reliability backup)*
  3. `gemini/gemini-3.5-flash` *(Standard Flash)*
  4. `gemini/gemini-3.6-flash` *(Deep logic backup)*
  5. `gemini/gemini-3.7-flash` *(High capability)*
  6. `gemini/gemini-3.1-pro-preview` *(Pro model backup)*
* **Role in Claude Code:** `ANTHROPIC_MODEL` & `ANTHROPIC_DEFAULT_SONNET_MODEL`
* **பயன்பாடு:** தினசரி Code Writing, Multi-file edits, Fullstack development, மற்றும் Bash commands.

---

### 2️⃣ Combo: `nvidia free` (Opus Reasoning Equivalent)
* **Strategy:** `Intelligent Auto`
* **Smart Routing Configuration:**
  - **Mode Pack:** `Quality First`
  - **Router Strategy:** `Rules (6-Factor Scoring)`
  - **Exploration Rate:** `5%`
  - **Budget Cap:** `No limit`
* **Models வரிசை (Confirmed Live & Working):**
  1. `nvidia/nvidia/nemotron-3-ultra-550b-a55b` *(550 Billion Parameter Ultra Beast 🔥)*
  2. `nvidia/moonshotai/kimi-k3` *(Moonshot Kimi K3 High Intelligence)*
  3. `nvidia/nvidia/nemotron-3.5-lightning-30b-a3b` *(2.9s Lightning Fast ⚡)*
  4. `nvidia/minimaxai/minimax-m3` *(High Quality Context reasoning)*
  5. `nvidia/nvidia/nemotron-3-super-120b-a12b` *(120 Billion Parameter Model)*
* **Role in Claude Code:** `ANTHROPIC_DEFAULT_OPUS_MODEL`
* **பயன்பாடு:** Deep Architecture planning, Security audits, Complex Refactoring, மற்றும் System Design.

---

### 3️⃣ Combo: `gemini-fallback` (Haiku / Fast Tasks)
* **Strategy:** `Sequential Fallback`
* **Models வரிசை:**
  1. `gemini/gemini-3.5-flash-lite` *(2-3s Instant response)*
  2. `gemini/gemini-3.1-flash-lite`
  3. `gemini/gemini-3.5-flash`
  4. `gemini/gemini-3.6-flash`
  5. `gemini/gemini-3.7-flash`
* **Role in Claude Code:** `ANTHROPIC_DEFAULT_HAIKU_MODEL` & `ANTHROPIC_SMALL_FAST_MODEL`
* **பயன்பாடு:** Quick lookups, Syntax checking, File searching, மற்றும் Small tool operations.

---

### 4️⃣ Combo: `free code` (OpenCode Backup Suite)
* **Strategy:** `Sequential Fallback`
* **Models வரிசை:**
  1. `oc/nemotron-3-ultra-free`
  2. `oc/deepseek-v4-flash-free`
  3. `oc/mimo-v2.5-free`
  4. `oc/hy3-free`
  5. `oc/north-mini-code-free`
* **பயன்பாடு:** Gemini & NVIDIA இரண்டுமே rate limit ஆகும் பட்சத்தில் secondary free cloud routing.

---

## 🔧 CRITICAL MIDDLEWARE HOOKS (ROOT-CAUSE FIXES)

OmniRoute features an internal JavaScript middleware engine stored in SQLite table `middleware_hooks`. These two hooks resolve 100% of proxy-translation errors.

### Hook 1: `disable-thinking` (Priority 0 — Runs First)
* **Root Problem:** Gemini 3.7 / 3.6 / Thinking models output internal `<thought>` tokens during tool calls. When OmniRoute converts Gemini format to Anthropic format, `thought_signature` is omitted, causing Google Gemini API to reject subsequent tool turns with:
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

### Hook 2: `fix-tool-names` (Priority 1 — Runs Second)
* **Root Problem:** Non-Anthropic models (Gemini, OpenCode, NVIDIA) return tool names in lowercase (e.g. `glob`, `read`, `write`, `edit`, `bash`). Claude Code expects exact TitleCase (`Glob`, `Read`, `Write`, `Edit`, `Bash`), otherwise throwing:
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

## 🔀 CROSS-COMBO FALLBACK ROUTING

`domain_fallback_chains` table மூலம் ஒரு Combo-ல் உள்ள அனைத்து models-உம் fail அல்லது rate limit ஆனால், அடுத்த Combo-க்கு தானாக cascade ஆகும்:

```
[nvidia free fails]    ──▶ [free coding 2] ──▶ [gemini-fallback] ──▶ [gemini-3.5-flash-lite]
[free coding 2 fails]  ──▶ [gemini-fallback] ──▶ [nvidia free] ──▶ [gemini-3.5-flash-lite]
[free code fails]      ──▶ [free coding 2] ──▶ [gemini-fallback] ──▶ [gemini-3.5-flash-lite]
```

---

## ⚙️ CLAUDE CODE ENVIRONMENT CONFIGURATION (`settings.json`)

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

## 🩺 AUTOMATION SCRIPTS (`setup_omniroute.py` & `refresh.py`)

| Script | When to Run | What it Does |
|---|---|---|
| **[`setup_omniroute.py`](setup_omniroute.py)** | Initial clone / Setup on a new PC | Injects middleware hooks, configures all 4 combos, sets fallback chains, and syncs settings files. |
| **[`refresh.py`](refresh.py)** | Anytime upstream API has outages / 502 errors | Runs real-time latency ping tests against all models, updates ELO rankings, and dynamically promotes the best live models. |

---

## 🚀 8 CUSTOM CLAUDE CODE SKILLS & COMMANDS

Located in `.claude/commands/`:

| Command | Usage | Description |
|---|---|---|
| `/mega-build` | `/mega-build <app idea>` | Fullstack single-request autonomous application builder. |
| `/sprint` | `/sprint <features>` | Rapid multi-feature batch development in parallel. |
| `/fullstack` | `/fullstack <spec>` | Generates schema, backend API, frontend UI, and tests in one turn. |
| `/fix` | `/fix <bug description>` | Systematic root-cause debugging and bug repair. |
| `/refactor` | `/refactor <target>` | Architecture cleanup, DRY/SOLID enforcement, and optimization. |
| `/scan` | `/scan` | Full repo architecture and security audit. |
| `/feature` | `/feature <name>` | End-to-end new feature development and integration. |
| `/turbo` | `/turbo <task>` | Ultra-fast single-turn code transformation. |

---

## 🚨 COMPREHENSIVE ERROR TROUBLESHOOTING MATRIX

| Error Message | Root Cause | Instant Resolution |
|---|---|---|
| `API Error: 400 [400]: Function call is missing a thought_signature` | Thinking tokens generated without signature during tool turns | Run `python setup_omniroute.py` and restart OmniRoute to apply `disable-thinking` hook (`thinkingBudget=0`). |
| `<tool_use_error>Error: No such tool available: glob` | Model outputted lowercase tool name (`glob`, `read`, etc.) | Restart OmniRoute so `fix-tool-names` hook normalizes `glob -> Glob`. |
| `Combo Control Center unavailable / Combo not found` | Combos table `data` field used string array instead of object array | Run `python setup_omniroute.py` to regenerate combos with `{kind: "model", model: "...", providerId: "..."}`. |
| `HTTP 502 / 503 Bad Gateway on Gemini` | Google Gemini upstream server overload on non-lite models | Run `python refresh.py` to automatically switch primary to `gemini-3.5-flash-lite`. |
| `HTTP 410 Gone on NVIDIA models` | Old model names deprecated by NVIDIA (e.g. date suffix added) | Use updated model IDs: `nemotron-3-ultra-550b-a55b` and `nemotron-3.5-lightning-30b-a3b`. |
| `HTTP 403 on OpenCode models` | OpenCode API token expired | Update API key in OmniRoute UI -> Connections -> OpenCode. |

---

## 🧠 ARCHITECTURE & REQUEST FLOW MENTAL MODEL

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
   (6-Key Pool Rotation)  (Nemotron 550B/30B) (DeepSeek / Free)
```
