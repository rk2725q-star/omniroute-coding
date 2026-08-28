#!/usr/bin/env python3
"""
OmniRoute Auto Health Refresh
Run anytime: python refresh.py
Detects working Gemini models live and updates all configs automatically.
"""
import sqlite3, json, sys, os, time, uuid, urllib.request, urllib.error
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8')

OMNIROUTE  = "http://localhost:20128"
AUTH       = "omniroute"
DB_PATH    = r"C:\Users\manit\.omniroute\storage.sqlite"
SETTINGS   = [
    r"c:\Users\manit\OneDrive\Desktop\omniroute\.claude\settings.json",
    r"c:\Users\manit\OneDrive\Desktop\omniroute\.claude\settings.example.json",
    os.path.expanduser(r"~\.claude\settings.json"),
]

# All models across all providers — ordered by expected speed
ALL_MODELS = [
    # Nvidia (usually fast when up)
    ("nvidia/moonshotai/kimi-k3",                   "nvidia"),
    ("nvidia/nvidia/nemotron-3.5-lightning-30b-a3b", "nvidia"),
    ("nvidia/minimaxai/minimax-m3",                  "nvidia"),
    ("nvidia/nvidia/nemotron-3-super-120b-a12b",     "nvidia"),
    ("nvidia/nvidia/nemotron-3-ultra-550b-a55b",     "nvidia"),
    # Gemini
    ("gemini/gemini-3.5-flash-lite",                 "gemini"),
    ("gemini/gemini-3.1-flash-lite",                 "gemini"),
    ("gemini/gemini-3.5-flash",                      "gemini"),
    ("gemini/gemini-3.6-flash",                      "gemini"),
    ("gemini/gemini-3.7-flash",                      "gemini"),
    ("gemini/gemini-3.1-flash-lite-preview",         "gemini"),
    ("gemini/gemini-omni-flash-preview",             "gemini"),
    # OpenCode
    ("oc/nemotron-3-ultra-free",                     "opencode"),
]


def test_model(model, timeout=8):
    body = {"model": model, "max_tokens": 1,
            "messages": [{"role": "user", "content": "Say: OK"}]}
    req = urllib.request.Request(
        f"{OMNIROUTE}/v1/messages",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {AUTH}", "Content-Type": "application/json",
                 "x-api-key": AUTH, "anthropic-version": "2023-06-01"},
        method="POST"
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            actual = data.get("model", "?")
            return True, actual, round(time.time()-t0, 2)
    except urllib.error.HTTPError as e:
        code = e.code
        return False, f"HTTP {code}", round(time.time()-t0, 2)
    except Exception as e:
        return False, str(e)[:30], round(time.time()-t0, 2)

def run():
    now = datetime.now(timezone.utc).isoformat()
    expires = "2099-12-31T00:00:00+00:00"

    print("=" * 60)
    print("OmniRoute Auto Health Refresh")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Live health check (all providers)
    print("\n[1/4] Live model health check (all providers)...")
    working_tuples, dead_tuples = [], []
    for m, provider in ALL_MODELS:
        ok, actual, ms = test_model(m)
        tag = "✅" if ok else "❌"
        print(f"  {tag} {m:55s} {ms:5.2f}s")
        if ok:
            working_tuples.append((m, provider, ms))
        else:
            dead_tuples.append((m, provider))

    if not working_tuples:
        print("\n⚠️  ALL MODELS DOWN — check OmniRoute. Try again later.")
        return

    # Sort working models by speed (fastest first)
    working_tuples.sort(key=lambda x: x[2])
    working = [m for m, p, ms in working_tuples]
    dead    = [m for m, p in dead_tuples]
    primary = working[0]
    print(f"\n  Working: {len(working)} | Dead: {len(dead)}")
    print(f"  🏎️  Fastest: {primary} ({working_tuples[0][2]}s)")

    # 2. Update DB
    print("\n[2/4] Updating OmniRoute database...")
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    def make_model_entry(m, p=None):
        if p:
            return {"kind": "model", "model": m, "providerId": p}
        # Auto-detect provider from prefix
        provider = m.split("/")[0] if "/" in m else "gemini"
        if provider not in ("gemini", "nvidia", "openrouter", "opencode", "oc"):
            provider = "nvidia" if "nvidia" in m or "kimi" in m or "minimax" in m else "gemini"
        return {"kind": "model", "model": m, "providerId": provider}

    # model_intelligence ELO — working sorted by speed
    cur.execute("DELETE FROM model_intelligence WHERE source='manual'")
    for i, (m, p, ms) in enumerate(working_tuples):
        elo = max(2800 - i * 150, 1000)
        cat = "best" if i < 2 else "good" if i < 5 else "fast"
        for key in [m, m.split("/")[-1]]:
            cur.execute("""INSERT OR REPLACE INTO model_intelligence
                (model, source, category, score, elo_raw, confidence, synced_at, expires_at)
                VALUES (?, 'manual', ?, ?, ?, 1.0, ?, ?)""",
                (key, cat, round(elo/2800, 3), elo, now, expires))
    for m, p in dead_tuples:
        for key in [m, m.split("/")[-1]]:
            cur.execute("""INSERT OR REPLACE INTO model_intelligence
                (model, source, category, score, elo_raw, confidence, synced_at, expires_at)
                VALUES (?, 'manual', 'fast', 0.3, 800, 0.1, ?, ?)""",
                (key, now, expires))

    # Build combos with working models sorted by speed
    nvidia_w = [(m, p, ms) for m, p, ms in working_tuples if p == "nvidia"]
    gemini_w = [(m, p, ms) for m, p, ms in working_tuples if p == "gemini"]
    oc_w     = [(m, p, ms) for m, p, ms in working_tuples if p in ("opencode", "oc")]
    nvidia_d = [(m, p) for m, p in dead_tuples if p == "nvidia"]
    gemini_d = [(m, p) for m, p in dead_tuples if p == "gemini"]
    oc_d     = [(m, p) for m, p in dead_tuples if p in ("opencode", "oc", "openrouter")]

    all_working_entries = [make_model_entry(m, p) for m, p, ms in working_tuples]
    all_dead_entries    = [make_model_entry(m, p) for m, p in dead_tuples]

    combos_config = {
        "free coding 2": {
            "strategy": "auto",
            "models": all_working_entries + all_dead_entries,
        },
        "nvidia free": {
            "strategy": "auto",
            "models": ([make_model_entry(m, p) for m, p, ms in nvidia_w] +
                       [make_model_entry(m, p) for m, p in nvidia_d]) or (all_working_entries[:3]),
            "smart": True,
        },
        "top code": {
            "strategy": "auto",
            "models": [
                make_model_entry("nvidia/moonshotai/kimi-k3", "nvidia"),
                make_model_entry("nvidia/minimaxai/minimax-m3", "nvidia"),
                make_model_entry("nvidia/nvidia/nemotron-3-ultra-550b-a55b", "nvidia"),
                make_model_entry("openrouter/nvidia/nemotron-3-ultra-550b-a55b:free-high", "openrouter"),
                make_model_entry("opencode/nemotron-3-ultra-free", "opencode"),
                make_model_entry("openrouter/nvidia/nemotron-3-ultra-550b-a55b:free-medium", "openrouter"),
            ],
        },
        "gemini-fallback": {
            "strategy": "fallback",
            "models": ([make_model_entry(m, p) for m, p, ms in gemini_w] +
                       [make_model_entry(m, p) for m, p in gemini_d]) or (all_working_entries[:5]),
        },
        "free code": {
            "strategy": "fallback",
            "models": ([make_model_entry(m, p) for m, p, ms in oc_w] +
                       [make_model_entry(m, p) for m, p in oc_d]) or (all_working_entries[:5]),
        },
    }

    cur.execute("DELETE FROM combos")
    cur.execute("DELETE FROM model_combo_mappings")
    for cname, cinfo in combos_config.items():
        cdata = {
            "name": cname, "strategy": cinfo["strategy"],
            "models": cinfo["models"],
            "capabilities": {"multimodal": False, "reasoning": False, "caching": False}
        }
        if cinfo.get("smart"):
            cdata.update({
                "mode_pack": "Quality First", "modePack": "Quality First",
                "router_strategy": "Rules (6-Factor Scoring)", "routerStrategy": "Rules (6-Factor Scoring)",
                "exploration_rate": 0.05, "explorationRate": 0.05,
                "smart_routing": {"mode_pack": "Quality First", "modePack": "Quality First",
                                  "preset": "quality_first"}
            })
        cur.execute("""INSERT INTO combos (id,name,data,sort_order,created_at,updated_at,system_message,tool_filter_regex,context_cache_protection)
            VALUES (?,?,?,0,?,?,NULL,NULL,0)""",
            (cname, cname, json.dumps(cdata), now, now))

    # Mappings
    for pat, combo, pri in [
        ("auto/best-free", "free coding 2", 100),
        ("auto",           "free coding 2", 100),
        ("claude-sonnet-4-6", "free coding 2", 100),
        ("claude-opus-4-5",   "nvidia free", 90),
        ("claude-haiku-4-5",  "top code", 90),
    ]:
        mid = str(uuid.uuid4())
        cur.execute("""INSERT OR REPLACE INTO model_combo_mappings
            (id,pattern,combo_id,priority,enabled,description,created_at,updated_at)
            VALUES (?,?,?,?,1,'Speed-sorted auto',?,?)""",
            (mid, pat, combo, pri, now, now))

    # Fallback chains — working combos first
    chain = ["free coding 2", "top code", "nvidia free", "gemini-fallback", "free code"]
    cur.execute("DELETE FROM domain_fallback_chains")
    for key in chain + ["auto", "auto/best-free", "claude-sonnet-4-6", "claude-opus-4-5", "claude-haiku-4-5"]:
        cur.execute("INSERT OR REPLACE INTO domain_fallback_chains (model,chain) VALUES (?,?)",
                    (key, json.dumps(chain)))

    # Update gemini provider health
    if gemini_w:
        health_model = gemini_w[0][0].replace("gemini/", "")
        cur.execute("""UPDATE provider_connections SET
            default_model=?, consecutive_use_count=1,
            test_status='ok', last_error=NULL, last_error_at=NULL,
            backoff_level=0, rate_limited_until=NULL
            WHERE provider='gemini'""", (health_model,))

    db.commit()
    db.close()
    print(f"  ✅ DB updated: {len(working)} working models, speed-sorted")

    # 3. Update settings.json — use combos, not raw models
    print("\n[3/4] Updating settings.json files...")
    # Smart primary: use fastest working combo
    primary_combo = "top code" if nvidia_w and not gemini_w else "free coding 2"

    settings = {"env": {
        "ANTHROPIC_BASE_URL": "http://localhost:20128",
        "ANTHROPIC_AUTH_TOKEN": "omniroute",
        "ANTHROPIC_MODEL":                primary_combo,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": primary_combo,
        "ANTHROPIC_DEFAULT_OPUS_MODEL":   "nvidia free",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL":  "top code",
        "ANTHROPIC_SMALL_FAST_MODEL":     "top code",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
        "DISABLE_AUTOUPDATER": "1"
    }}
    for p in SETTINGS:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            print(f"  ✅ {p}")
        except Exception as e:
            print(f"  ❌ {p}: {e}")

    # 4. Summary
    print("\n[4/4] Summary")
    print(f"\n  🏎️  Primary combo:  {primary_combo}")
    print(f"  📊  Opus combo:     nvidia free")
    print(f"  ⚡  Haiku combo:    top code")
    print(f"\n  Live model ranking (fastest → slowest):")
    for i, (m, p, ms) in enumerate(working_tuples[:6]):
        print(f"    #{i+1} {m:55s} {ms:.2f}s")
    if dead:
        print(f"\n  Down ({len(dead)}): {', '.join(d.split('/')[-1] for d in dead[:4])}...")

    print(f"\n✅ Done! Restart Claude Code to apply changes.\n")

if __name__ == "__main__":
    run()
