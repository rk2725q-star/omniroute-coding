#!/usr/bin/env python3
"""
OmniRoute + Claude Code Master Setup & Bootstrap Script
Run this script anytime to initialize or repair:
1. SQLite Database Middleware Hooks (Fix tool casing + Fix thought_signature)
2. All 4 Preconfigured Combos (gemini-fallback, nvidia free, free coding 2, free code)
3. Cross-Combo Fallback Chains
4. Global and Workspace settings.json files for Claude Code
5. Model intelligence & Capability overrides
"""

import sqlite3
import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

# Constants & Paths
OMNIROUTE_URL = "http://localhost:20128"
AUTH_TOKEN = "omniroute"
APPDATA_DIR = os.environ.get("APPDATA", "")
USER_HOME = os.path.expanduser("~")
DB_PATH = os.path.join(USER_HOME, ".omniroute", "storage.sqlite")

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_SETTINGS = os.path.join(WORKSPACE_DIR, ".claude", "settings.json")
WORKSPACE_EXAMPLE = os.path.join(WORKSPACE_DIR, ".claude", "settings.example.json")
GLOBAL_SETTINGS = os.path.join(USER_HOME, ".claude", "settings.json")

NOW = datetime.now(timezone.utc).isoformat()
EXPIRES = "2099-12-31T00:00:00+00:00"

def log(msg, symbol="ℹ️"):
    print(f"[{symbol}] {msg}")

def ensure_dirs():
    os.makedirs(os.path.join(WORKSPACE_DIR, ".claude"), exist_ok=True)
    os.makedirs(os.path.join(USER_HOME, ".claude"), exist_ok=True)
    os.makedirs(os.path.join(USER_HOME, ".omniroute"), exist_ok=True)

def setup_database():
    log(f"Connecting to SQLite: {DB_PATH}", "📂")
    if not os.path.exists(DB_PATH):
        log(f"Database not found at {DB_PATH}. OmniRoute will create it on first launch.", "⚠️")
        return False

    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    # 1. MIDDLEWARE HOOK 0: disable-thinking (Fixes 400 thought_signature missing)
    HOOK_DISABLE_THINKING = """// Disable Gemini thinking mode to prevent thought_signature errors
// Error: "Function call is missing a thought_signature in functionCall parts"
// Fix: Set thinkingBudget=0 for all Gemini requests with tool calls

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
        }).filter(part => {
          if (part.thought === true) return false;
          return true;
        });
      }
      return content;
    });
  }
  request.body = body;
}
return request;
"""

    # 2. MIDDLEWARE HOOK 1: fix-tool-names (Fixes lowercase tools like glob, read, bash)
    HOOK_FIX_TOOL_NAMES = """const MAP = {
  'read':'Read','write':'Write','edit':'Edit','multiedit':'MultiEdit',
  'multi_edit':'MultiEdit','bash':'Bash','glob':'Glob','grep':'Grep','task':'Task',
  'webfetch':'WebFetch','web_fetch':'WebFetch','todoread':'TodoRead','todowrite':'TodoWrite'
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
"""

    cur.execute("DELETE FROM middleware_hooks WHERE name IN ('disable-thinking', 'fix-tool-names')")
    cur.execute("""
        INSERT INTO middleware_hooks
        (name, description, priority, scope_type, combo_id, enabled, code, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'disable-thinking',
        'Disable Gemini thinking mode (thinkingBudget=0) to prevent thought_signature errors',
        0, 'global', None, 1, HOOK_DISABLE_THINKING, NOW, NOW
    ))
    cur.execute("""
        INSERT INTO middleware_hooks
        (name, description, priority, scope_type, combo_id, enabled, code, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'fix-tool-names',
        'Fix tool name casing: Gemini lowercase -> Claude Code TitleCase',
        1, 'global', None, 1, HOOK_FIX_TOOL_NAMES, NOW, NOW
    ))
    log("Middleware hooks installed (disable-thinking + fix-tool-names)", "✅")

    # 3. Model Capability Overrides for Thinking Models
    THINKING_MODELS = [
        "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-pro-preview",
        "gemini-3.1-pro", "gemini-3.5-flash", "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite", "gemini-2.5-pro", "gemini-2.5-flash"
    ]
    for model in THINKING_MODELS:
        for prefix in [f"gemini/{model}", model]:
            for key, val in [("reasoning", "false"), ("thinking", "false"), ("thinkingBudget", "0"), ("includeThoughts", "false")]:
                cur.execute("""
                    INSERT OR REPLACE INTO model_capability_overrides
                    (provider, model_id, override_key, override_value, refreshed_at)
                    VALUES ('gemini', ?, ?, ?, ?)
                """, (prefix, key, val, NOW))
    log("Model capability overrides set (reasoning=false, thinkingBudget=0)", "✅")

    # 4. Helper for OmniRoute Combos Format
    def make_entry(model_id, provider=None):
        if not provider:
            provider = model_id.split("/")[0] if "/" in model_id else "gemini"
        return {"kind": "model", "model": model_id, "providerId": provider}

    # 5. Define All Combos
    COMBOS_CONFIG = {
        "gemini-fallback": {
            "strategy": "fallback",
            "models": [
                make_entry("gemini/gemini-3.5-flash-lite", "gemini"),
                make_entry("gemini/gemini-3.1-flash-lite", "gemini"),
                make_entry("gemini/gemini-3.5-flash", "gemini"),
                make_entry("gemini/gemini-3.6-flash", "gemini"),
                make_entry("gemini/gemini-3.7-flash", "gemini"),
            ]
        },
        "free coding 2": {
            "strategy": "auto",
            "models": [
                make_entry("gemini/gemini-3.5-flash-lite", "gemini"),
                make_entry("gemini/gemini-3.1-flash-lite", "gemini"),
                make_entry("gemini/gemini-3.5-flash", "gemini"),
                make_entry("gemini/gemini-3.6-flash", "gemini"),
                make_entry("gemini/gemini-3.7-flash", "gemini"),
                make_entry("gemini/gemini-3.1-pro-preview", "gemini"),
            ]
        },
        "nvidia free": {
            "strategy": "auto",
            "mode_pack": "Quality First",
            "router_strategy": "Rules (6-Factor Scoring)",
            "exploration_rate": 0.05,
            "budget_cap": None,
            "models": [
                make_entry("nvidia/nvidia/nemotron-3-ultra-550b-a55b", "nvidia"),
                make_entry("nvidia/moonshotai/kimi-k3", "nvidia"),
                make_entry("nvidia/nvidia/nemotron-3.5-lightning-30b-a3b", "nvidia"),
                make_entry("nvidia/minimaxai/minimax-m3", "nvidia"),
                make_entry("nvidia/nvidia/nemotron-3-super-120b-a12b", "nvidia"),
            ]
        },
        "top code": {
            "strategy": "auto",
            "models": [
                make_entry("nvidia/moonshotai/kimi-k3", "nvidia"),
                make_entry("nvidia/minimaxai/minimax-m3", "nvidia"),
                make_entry("nvidia/nvidia/nemotron-3-ultra-550b-a55b", "nvidia"),
                make_entry("openrouter/nvidia/nemotron-3-ultra-550b-a55b:free-high", "openrouter"),
                make_entry("opencode/nemotron-3-ultra-free", "opencode"),
                make_entry("openrouter/nvidia/nemotron-3-ultra-550b-a55b:free-medium", "openrouter"),
            ]
        },
        "free code": {
            "strategy": "fallback",
            "models": [
                make_entry("oc/nemotron-3-ultra-free", "opencode"),
                make_entry("oc/deepseek-v4-flash-free", "opencode"),
                make_entry("oc/mimo-v2.5-free", "opencode"),
                make_entry("oc/hy3-free", "opencode"),
                make_entry("oc/north-mini-code-free", "opencode"),
            ]
        }
    }

    # Insert or update combos
    for name, cinfo in COMBOS_CONFIG.items():
        combo_data = {
            "name": name,
            "strategy": cinfo["strategy"],
            "models": cinfo["models"],
            "capabilities": {"multimodal": False, "reasoning": False, "caching": False}
        }
        if "mode_pack" in cinfo:
            combo_data["mode_pack"] = cinfo["mode_pack"]
            combo_data["modePack"] = cinfo["mode_pack"]
            combo_data["router_strategy"] = cinfo.get("router_strategy", "Rules (6-Factor Scoring)")
            combo_data["routerStrategy"] = cinfo.get("router_strategy", "Rules (6-Factor Scoring)")
            combo_data["exploration_rate"] = cinfo.get("exploration_rate", 0.05)
            combo_data["explorationRate"] = cinfo.get("exploration_rate", 0.05)
            combo_data["budget_cap"] = cinfo.get("budget_cap", None)
            combo_data["budgetCap"] = cinfo.get("budget_cap", None)
            combo_data["candidate_pool"] = []
            combo_data["candidatePool"] = []
            combo_data["smart_routing"] = {
                "mode_pack": cinfo["mode_pack"],
                "modePack": cinfo["mode_pack"],
                "router_strategy": cinfo.get("router_strategy", "Rules (6-Factor Scoring)"),
                "routerStrategy": cinfo.get("router_strategy", "Rules (6-Factor Scoring)"),
                "exploration_rate": cinfo.get("exploration_rate", 0.05),
                "explorationRate": cinfo.get("exploration_rate", 0.05),
                "budget_cap": cinfo.get("budget_cap", None),
                "budgetCap": cinfo.get("budget_cap", None),
                "candidate_pool": [],
                "candidatePool": [],
                "preset": "quality_first"
            }
        cur.execute("DELETE FROM combos WHERE name=?", (name,))
        cur.execute("""
            INSERT INTO combos (id, name, data, sort_order, created_at, updated_at, system_message, tool_filter_regex, context_cache_protection)
            VALUES (?, ?, ?, 0, ?, ?, NULL, NULL, 0)
        """, (name, name, json.dumps(combo_data), NOW, NOW))
    log("All 5 combos created with correct Object Array schema", "✅")

    # 6. Model Combo Mappings
    cur.execute("DELETE FROM model_combo_mappings")
    mapping_rules = [
        ("auto/best-free", "free coding 2", 100),
        ("auto", "free coding 2", 100),
        ("claude-sonnet-4-6", "free coding 2", 100),
        ("claude-opus-4-5", "nvidia free", 90),
        ("claude-haiku-4-5", "top code", 80),
    ]
    for pattern, combo_name, priority in mapping_rules:
        mid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO model_combo_mappings
            (id, pattern, combo_id, priority, enabled, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, 'Auto-mapped rule', ?, ?)
        """, (mid, pattern, combo_name, priority, NOW, NOW))
    log("Model combo mappings registered", "✅")

    # 7. Cross-Combo Fallback Chains
    CROSS_CHAINS = {
        "free coding 2": ["free coding 2", "top code", "nvidia free", "gemini-fallback", "free code", "gemini/gemini-3.5-flash-lite"],
        "nvidia free": ["nvidia free", "top code", "free coding 2", "gemini-fallback", "free code", "gemini/gemini-3.5-flash-lite"],
        "top code": ["top code", "free coding 2", "nvidia free", "gemini-fallback", "free code", "gemini/gemini-3.5-flash-lite"],
        "gemini-fallback": ["gemini-fallback", "top code", "free coding 2", "nvidia free", "free code", "gemini/gemini-3.5-flash-lite"],
        "free code": ["free code", "top code", "free coding 2", "gemini-fallback", "nvidia free", "gemini/gemini-3.5-flash-lite"],
        "auto/best-free": ["free coding 2", "top code", "nvidia free", "gemini/gemini-3.5-flash-lite"],
        "auto": ["free coding 2", "top code", "nvidia free", "gemini/gemini-3.5-flash-lite"],
    }
    cur.execute("DELETE FROM domain_fallback_chains")
    for model_key, chain in CROSS_CHAINS.items():
        cur.execute("INSERT OR REPLACE INTO domain_fallback_chains (model, chain) VALUES (?, ?)", (model_key, json.dumps(chain)))
    log("Cross-combo fallback chains established", "✅")

    # 8. Model Intelligence ELO Ratings
    cur.execute("DELETE FROM model_intelligence WHERE source='manual'")
    models_elo = [
        ("gemini/gemini-3.5-flash-lite", 2800, "best"),
        ("gemini/gemini-3.1-flash-lite", 2700, "best"),
        ("nvidia/nvidia/nemotron-3-ultra-550b-a55b", 2650, "best"),
        ("nvidia/moonshotai/kimi-k3", 2600, "best"),
        ("gemini/gemini-3.5-flash", 2500, "good"),
        ("nvidia/nvidia/nemotron-3.5-lightning-30b-a3b", 2400, "good"),
        ("gemini/gemini-3.6-flash", 2200, "good"),
        ("gemini/gemini-3.7-flash", 2100, "good"),
        ("gemini/gemini-3.1-pro-preview", 2000, "good"),
    ]
    for m, elo, cat in models_elo:
        for k in [m, m.replace("gemini/", "").replace("nvidia/", "").replace("moonshotai/", "")]:
            cur.execute("""
                INSERT OR REPLACE INTO model_intelligence
                (model, source, category, score, elo_raw, confidence, synced_at, expires_at)
                VALUES (?, 'manual', ?, ?, ?, 1.0, ?, ?)
            """, (k, cat, round(elo/2800, 3), elo, NOW, EXPIRES))
    log("Model Intelligence ELO ratings updated", "✅")

    db.commit()
    db.close()
    return True

def sync_settings_files():
    settings_payload = {
        "env": {
            "ANTHROPIC_BASE_URL": "http://localhost:20128",
            "ANTHROPIC_AUTH_TOKEN": "omniroute",
            "ANTHROPIC_MODEL": "free coding 2",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "free coding 2",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "nvidia free",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "top code",
            "ANTHROPIC_SMALL_FAST_MODEL": "top code",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
            "DISABLE_AUTOUPDATER": "1"
        }
    }

    targets = [WORKSPACE_SETTINGS, WORKSPACE_EXAMPLE, GLOBAL_SETTINGS]
    for target in targets:
        try:
            with open(target, "w", encoding="utf-8") as f:
                json.dump(settings_payload, f, indent=2)
            log(f"Synced settings -> {target}", "📄")
        except Exception as e:
            log(f"Failed writing {target}: {e}", "❌")

def main():
    print("=" * 65)
    print("🚀 OMNIROUTE & CLAUDE CODE AUTOMATED SETUP")
    print("=" * 65)
    ensure_dirs()
    db_ok = setup_database()
    sync_settings_files()
    print("=" * 65)
    if db_ok:
        print("🎉 SUCCESS! OmniRoute DB & Claude Code settings fully configured.")
        print("👉 ACTION REQUIRED: Restart OmniRoute and Claude Code.")
    else:
        print("⚠️  OmniRoute DB was not found. Please start OmniRoute first, then rerun this script.")
    print("=" * 65)

if __name__ == "__main__":
    main()
