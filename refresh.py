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
ALL_MODELS = [
    "gemini/gemini-3.7-flash",
    "gemini/gemini-3.6-flash",
    "gemini/gemini-3.5-flash",
    "gemini/gemini-3.5-flash-lite",
    "gemini/gemini-3.1-flash-lite",
    "gemini/gemini-3.1-flash-lite-preview",
    "gemini/gemini-omni-flash-preview",
]

def test_model(model, timeout=12):
    body = {"model": model, "max_tokens": 8,
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

    # 1. Live health check
    print("\n[1/4] Live model health check...")
    working, dead = [], []
    for m in ALL_MODELS:
        ok, actual, ms = test_model(m)
        tag = "✅" if ok else "❌"
        print(f"  {tag} {m:45s} {ms:5.1f}s")
        if ok:
            working.append(m)
        else:
            dead.append(m)

    if not working:
        print("\n⚠️  ALL MODELS DOWN — Gemini API outage. Try again later.")
        return

    primary = working[0]
    fallback_chain = working + dead  # working first, dead as last resort

    print(f"\n  Working: {len(working)} | Dead: {len(dead)}")
    print(f"  Primary: {primary}")

    # 2. Update DB
    print("\n[2/4] Updating OmniRoute database...")
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    # model_intelligence ELO
    cur.execute("DELETE FROM model_intelligence WHERE source='manual'")
    for i, m in enumerate(fallback_chain):
        elo = max(2800 - i * 200, 800)
        cat = "best" if elo >= 2700 else "good" if elo >= 2000 else "fast"
        for key in [m, m.replace("gemini/", "")]:
            cur.execute("""INSERT OR REPLACE INTO model_intelligence
                (model, source, category, score, elo_raw, confidence, synced_at, expires_at)
                VALUES (?, 'manual', ?, ?, ?, 1.0, ?, ?)""",
                (key, cat, round(elo/2800, 3), elo, now, expires))

    # domain_fallback_chains
    chain_json = json.dumps(fallback_chain)
    cur.execute("DELETE FROM domain_fallback_chains")
    for ep in ["auto/best-free", "auto", "claude-sonnet-4-6",
               "claude-opus-4-5", "claude-haiku-4-5"] + fallback_chain[:3]:
        cur.execute("INSERT OR REPLACE INTO domain_fallback_chains (model,chain) VALUES (?,?)",
                    (ep, chain_json))

    # model aliases
    cur.execute("DELETE FROM key_value WHERE namespace='modelAliases'")
    alias_entries = [
        ("auto/best-free",   f'"{primary}"'),
        ("auto",             f'"{primary}"'),
        ("claude-sonnet-4-6",f'"{primary}"'),
        ("claude-opus-4-5",  f'"{working[min(1,len(working)-1)]}"'),
        ("claude-haiku-4-5", f'"{working[-1]}"'),
    ]
    for m in fallback_chain[:8]:
        short = m.replace("gemini/","")
        alias_entries += [(m, f'"{m}"'), (short, f'"{m}"')]
    for k, v in alias_entries:
        cur.execute("INSERT OR REPLACE INTO key_value (namespace,key,value) VALUES ('modelAliases',?,?)", (k,v))

    # combo - CORRECT OmniRoute format: models must be object array with kind/model/providerId
    def make_model_entry(m):
        provider = m.split("/")[0] if "/" in m else "gemini"
        return {"kind": "model", "model": m, "providerId": provider}

    combo_name = "gemini-fallback"
    cur.execute("DELETE FROM combos")
    cur.execute("DELETE FROM model_combo_mappings")
    combo_data = {
        "name": combo_name, "strategy": "fallback",
        "models": [make_model_entry(m) for m in fallback_chain],
        "capabilities": {"multimodal": False, "reasoning": False, "caching": False}
    }
    cur.execute("""INSERT INTO combos (id,name,data,sort_order,created_at,updated_at,system_message,tool_filter_regex,context_cache_protection)
        VALUES (?,?,?,0,?,?,NULL,NULL,0)""",
        (combo_name, combo_name, json.dumps(combo_data), now, now))
    for pattern in ["auto/best-free","auto","claude-sonnet-4-6","claude-opus-4-5","claude-haiku-4-5"] + fallback_chain[:3]:
        mid = str(uuid.uuid4())
        cur.execute("""INSERT OR REPLACE INTO model_combo_mappings
            (id,pattern,combo_id,priority,enabled,description,created_at,updated_at)
            VALUES (?,?,?,100,1,'Auto fallback chain',?,?)""",
            (mid, pattern, combo_name, now, now))

    # all 6 keys health check model = most available working model
    health_model = working[-1].replace("gemini/", "")  # lightest working model
    cur.execute("""UPDATE provider_connections SET
        default_model=?, consecutive_use_count=1,
        test_status='ok', last_error=NULL, last_error_at=NULL,
        backoff_level=0, rate_limited_until=NULL
        WHERE provider='gemini'""", (health_model,))

    db.commit()
    db.close()
    print(f"  ✅ DB updated: ELO, chain, aliases, combo, health_check_model={health_model}")

    # 3. Update settings.json
    print("\n[3/4] Updating settings.json files...")
    settings = {"env": {
        "ANTHROPIC_BASE_URL": "http://localhost:20128",
        "ANTHROPIC_AUTH_TOKEN": "omniroute",
        "ANTHROPIC_MODEL": primary,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": primary,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": working[min(1,len(working)-1)],
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": working[-1],
        "ANTHROPIC_SMALL_FAST_MODEL": working[-1],
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
        "DISABLE_AUTOUPDATER": "1"
    }}
    for p in SETTINGS:
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            print(f"  ✅ {p}")
        except Exception as e:
            print(f"  ❌ {p}: {e}")

    # 4. Summary
    print("\n[4/4] Summary")
    print(f"\n  Primary model: {primary}")
    print(f"\n  Fallback chain:")
    for i, m in enumerate(fallback_chain):
        tag = "✅ working" if m in working else "❌ down (last resort)"
        print(f"    {i+1}. {m} — {tag}")

    print(f"\n✅ Done! Restart OmniRoute + Claude Code to apply.\n")

if __name__ == "__main__":
    run()
