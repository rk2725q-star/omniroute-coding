# 🚀 Cline Code Setup — Poolside Laguna S2.1 & MiniMax M3 Free

This branch (`cline-code`) is pre-configured with **100% Free Frontier Models** via OmniRoute:

---

## 👑 Model Priority Chain:
1. 🥇 **`cline/poolside/laguna-s-2.1:free`** — **Frontier Coding Weapon** (3.5s response, precision code generation)
2. 🥈 **`cline/minimax/minimax-m3:free`** — **1 Million Context Window** (Deep context reasoning)
3. 🥉 **`grok-cli/grok-4.6`** — **Grok Reasoning Coding Fallback**
4. 🛡️ **`nvidia/nvidia/nemotron-3-super-120b-a12b`** — **Nvidia Free MoE Fallback**

---

## ⚡ Multi-Account Round-Robin Load Balancing:
- All Cline accounts (`rk8246q@gmail.com`, `rk2725q@gmail.com`, `vibhashinimurugan@gmail.com`) operate on **Equal Priority (`Priority = 1`)**.
- Incoming coding requests are distributed evenly across accounts in a round-robin rotation.
- In the event of a 429 rate-limit on any account, OmniRoute performs an automatic **sub-second (750ms) failover** to the next available account with zero user disruption.

---

## 📋 Claude Code Settings (`.claude/settings.json`):
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_AUTH_TOKEN": "omniroute",
    "ANTHROPIC_MODEL": "coding king",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "coding king",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "coding king",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "coding king",
    "ANTHROPIC_SMALL_FAST_MODEL": "coding king",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
    "DISABLE_AUTOUPDATER": "1"
  }
}
```
