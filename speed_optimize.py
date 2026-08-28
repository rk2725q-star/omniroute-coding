import sqlite3, json, sys, os, uuid, time, urllib.request, urllib.error
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8')

OMNIROUTE = "http://localhost:20128"
AUTH = "omniroute"
DB_PATH = r"C:\Users\manit\.omniroute\storage.sqlite"
NOW = datetime.now(timezone.utc).isoformat()
EXPIRES = "2099-12-31T00:00:00+00:00"

SETTINGS = [
    r"c:\Users\manit\OneDrive\Desktop\omniroute\.claude\settings.json",
    r"c:\Users\manit\OneDrive\Desktop\omniroute\.claude\settings.example.json",
    os.path.expanduser(r"~\.claude\settings.json"),
]

def ping(model, timeout=5):
    body = {"model": model, "max_tokens": 1, "messages": [{"role": "user", "content": "1"}]}
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
            json.loads(resp.read().decode())
            return True, round(time.time()-t0, 3)
    except:
        return False, round(time.time()-t0, 3)

def make_entry(model, provider):
    return {"kind": "model", "model": model, "providerId": provider}

print("=" * 65)
print("  OmniRoute Speed Optimizer — Auto Live Detection + Fix")
print("=" * 65)

# ─── STEP 1: Live Speed Test All Models ──────────────────────────
print("\n[1/4] Live speed test (5s timeout per model)...")

ALL_MODELS = [
    # Fast nvidia models first (most likely to be up)
    ("nvidia/moonshotai/kimi-k3",                    "nvidia"),
    ("nvidia/minimaxai/minimax-m3",                   "nvidia"),
    ("nvidia/nvidia/nemotron-3.5-lightning-30b-a3b",  "nvidia"),
    ("nvidia/nvidia/nemotron-3-super-120b-a12b",      "nvidia"),
    ("nvidia/nvidia/nemotron-3-ultra-550b-a55b",      "nvidia"),
    # Gemini
    ("gemini/gemini-3.5-flash-lite",                  "gemini"),
    ("gemini/gemini-3.1-flash-lite",                  "gemini"),
    ("gemini/gemini-3.5-flash",                       "gemini"),
    ("gemini/gemini-3.6-flash",                       "gemini"),
    ("gemini/gemini-3.7-flash",                       "gemini"),
    ("gemini/gemini-3.1-pro-preview",                 "gemini"),
    # OpenCode/OpenRouter
    ("oc/nemotron-3-ultra-free",                      "opencode"),
    ("openrouter/nvidia/nemotron-3-ultra-550b-a55b:free-high", "openrouter"),
]

working = []   # (model, provider, latency)
dead    = []

for model, provider in ALL_MODELS:
    ok, ms = ping(model)
    tag = "✅" if ok else "❌"
    print(f"  {tag} {model:55s} {ms:.2f}s")
    if ok:
        working.append((model, provider, ms))
    else:
        dead.append((model, provider))

if not working:
    print("\n⚠️  ALL models down — check OmniRoute server. Cannot optimize.")
    sys.exit(1)

# Sort by speed (fastest first)
working.sort(key=lambda x: x[2])
print(f"\n  🏆 Fastest: {working[0][0]} ({working[0][2]}s)")
print(f"  Working: {len(working)}  |  Down: {len(dead)}")

# ─── STEP 2: Build Optimized Combos ──────────────────────────────
print("\n[2/4] Building speed-optimized combos in DB...")
db = sqlite3.connect(DB_PATH)
cur = db.cursor()

# Categorize working models
nvidia_working  = [(m, p, ms) for m, p, ms in working if p == "nvidia"]
gemini_working  = [(m, p, ms) for m, p, ms in working if p == "gemini"]
oc_working      = [(m, p, ms) for m, p, ms in working if p in ("opencode", "openrouter")]

# dead models as last-resort fallbacks (keep them in chains)
nvidia_dead   = [(m, p) for m, p in dead if p == "nvidia"]
gemini_dead   = [(m, p) for m, p in dead if p == "gemini"]
oc_dead       = [(m, p) for m, p in dead if p in ("opencode", "openrouter")]

def build_models(working_list, dead_list):
    """Working first (sorted by speed), dead last"""
    return (
        [make_entry(m, p) for m, p, _ in working_list] +
        [make_entry(m, p) for m, p in dead_list]
    )

# NEW optimized combos:
# free coding 2 → fastest working models FIRST regardless of provider
all_working_entries = [make_entry(m, p) for m, p, _ in working]
all_dead_entries    = [make_entry(m, p) for m, p in dead]

COMBOS_CONFIG = {
    # Primary: fastest working models across ALL providers
    "free coding 2": {
        "strategy": "auto",
        "models": all_working_entries + all_dead_entries,
    },
    # Nvidia-optimized combo
    "nvidia free": {
        "strategy": "auto",
        "mode_pack": "Quality First",
        "router_strategy": "Rules (6-Factor Scoring)",
        "exploration_rate": 0.05,
        "budget_cap": None,
        "models": build_models(nvidia_working, nvidia_dead) or (all_working_entries[:3] + [make_entry(m, p) for m, p in nvidia_dead]),
    },
    # top code: nvidia intelligence combo
    "top code": {
        "strategy": "auto",
        "models": [
            make_entry("nvidia/moonshotai/kimi-k3", "nvidia"),
            make_entry("nvidia/minimaxai/minimax-m3", "nvidia"),
            make_entry("nvidia/nvidia/nemotron-3-ultra-550b-a55b", "nvidia"),
            make_entry("openrouter/nvidia/nemotron-3-ultra-550b-a55b:free-high", "openrouter"),
            make_entry("opencode/nemotron-3-ultra-free", "opencode"),
            make_entry("openrouter/nvidia/nemotron-3-ultra-550b-a55b:free-medium", "openrouter"),
        ],
    },
    # gemini-fallback: gemini-only
    "gemini-fallback": {
        "strategy": "fallback",
        "models": build_models(gemini_working, gemini_dead) or all_working_entries[:5],
    },
    # free code: opencode
    "free code": {
        "strategy": "fallback",
        "models": build_models(oc_working, oc_dead) or all_working_entries[:5],
    },
}

for name, cinfo in COMBOS_CONFIG.items():
    combo_data = {
        "name": name,
        "strategy": cinfo["strategy"],
        "models": cinfo["models"],
        "capabilities": {"multimodal": False, "reasoning": False, "caching": False}
    }
    if "mode_pack" in cinfo:
        combo_data.update({
            "mode_pack": cinfo["mode_pack"], "modePack": cinfo["mode_pack"],
            "router_strategy": cinfo["router_strategy"], "routerStrategy": cinfo["router_strategy"],
            "exploration_rate": cinfo["exploration_rate"], "explorationRate": cinfo["exploration_rate"],
            "budget_cap": cinfo["budget_cap"], "budgetCap": cinfo["budget_cap"],
            "candidate_pool": [], "candidatePool": [],
            "smart_routing": {
                "mode_pack": cinfo["mode_pack"], "modePack": cinfo["mode_pack"],
                "router_strategy": cinfo["router_strategy"], "routerStrategy": cinfo["router_strategy"],
                "exploration_rate": cinfo["exploration_rate"], "explorationRate": cinfo["exploration_rate"],
                "budget_cap": cinfo["budget_cap"], "budgetCap": cinfo["budget_cap"],
                "preset": "quality_first"
            }
        })
    cur.execute("DELETE FROM combos WHERE name=?", (name,))
    cur.execute("""
        INSERT INTO combos (id, name, data, sort_order, created_at, updated_at, system_message, tool_filter_regex, context_cache_protection)
        VALUES (?, ?, ?, 0, ?, ?, NULL, NULL, 0)
    """, (name, name, json.dumps(combo_data), NOW, NOW))
    top3 = ", ".join(c["model"].split("/")[-1] for c in cinfo["models"][:3])
    print(f"  ✅ {name:20s} → [{top3}...]")

# ─── STEP 3: Model mappings & fallback chains ─────────────────────
print("\n[3/4] Updating mappings & fallback chains...")
cur.execute("DELETE FROM model_combo_mappings")
mapping_rules = [
    ("auto/best-free",  "free coding 2", 100),
    ("auto",            "free coding 2", 100),
    ("claude-sonnet-4-6", "free coding 2", 100),
    ("claude-opus-4-5", "nvidia free",   90),
    ("claude-haiku-4-5", "top code",     90),
]
for pattern, combo_name, priority in mapping_rules:
    mid = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO model_combo_mappings
        (id, pattern, combo_id, priority, enabled, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, 1, 'Speed-optimized', ?, ?)
    """, (mid, pattern, combo_name, priority, NOW, NOW))

# Dynamic fallback chains (working combos first)
working_combos = []
if nvidia_working:     working_combos.append("top code")
if gemini_working:     working_combos.append("gemini-fallback")
if oc_working:         working_combos.append("free code")

primary_chain = ["free coding 2"] + [c for c in working_combos if c != "free coding 2"] + [
    "top code", "nvidia free", "gemini-fallback", "free code"
]
# deduplicate keeping order
seen = set()
primary_chain = [x for x in primary_chain if not (x in seen or seen.add(x))]

CROSS_CHAINS = {
    "free coding 2":  primary_chain,
    "nvidia free":    ["nvidia free", "top code"] + primary_chain,
    "top code":       ["top code", "free coding 2"] + primary_chain,
    "gemini-fallback":["gemini-fallback", "free coding 2", "top code"] + primary_chain,
    "free code":      ["free code", "top code", "free coding 2"] + primary_chain,
    "auto":           primary_chain,
    "auto/best-free": primary_chain,
}
cur.execute("DELETE FROM domain_fallback_chains")
for model_key, chain in CROSS_CHAINS.items():
    seen2 = set(); chain = [x for x in chain if not (x in seen2 or seen2.add(x))]
    cur.execute("INSERT OR REPLACE INTO domain_fallback_chains (model, chain) VALUES (?, ?)",
                (model_key, json.dumps(chain)))
    print(f"  ✅ chain: {model_key:20s} → {chain[:3]}...")

# ELO: working models get top scores
cur.execute("DELETE FROM model_intelligence WHERE source='manual'")
for i, (m, p, ms) in enumerate(working):
    elo = max(2800 - i * 100, 1000)
    cat = "best" if i < 2 else ("good" if i < 5 else "fast")
    for key in [m, m.split("/")[-1]]:
        cur.execute("""
            INSERT OR REPLACE INTO model_intelligence
            (model, source, category, score, elo_raw, confidence, synced_at, expires_at)
            VALUES (?, 'manual', ?, ?, ?, 1.0, ?, ?)
        """, (key, cat, round(elo/2800, 3), elo, NOW, EXPIRES))
for m, p in dead:
    for key in [m, m.split("/")[-1]]:
        cur.execute("""
            INSERT OR REPLACE INTO model_intelligence
            (model, source, category, score, elo_raw, confidence, synced_at, expires_at)
            VALUES (?, 'manual', 'fast', 0.3, 800, 0.1, ?, ?)
        """, (key, NOW, EXPIRES))

db.commit()
db.close()

# ─── STEP 4: Update settings.json ─────────────────────────────────
print("\n[4/4] Updating settings.json with fastest live models...")

# Pick primary model (fastest working)
primary = working[0][0]  # fastest overall
# Sonnet = fastest
# Opus   = fastest nvidia (for heavy tasks)  
opus_model = nvidia_working[0][0] if nvidia_working else primary
# Haiku  = top code combo (nvidia intelligence)
haiku_model = "top code"

# If Gemini is down, use nvidia as primary for speed
if not gemini_working and nvidia_working:
    sonnet_combo = "top code"   # fastest working
else:
    sonnet_combo = "free coding 2"

settings = {"env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_AUTH_TOKEN": "omniroute",
    "ANTHROPIC_MODEL":               sonnet_combo,
    "ANTHROPIC_DEFAULT_SONNET_MODEL": sonnet_combo,
    "ANTHROPIC_DEFAULT_OPUS_MODEL":  "nvidia free",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": haiku_model,
    "ANTHROPIC_SMALL_FAST_MODEL":    haiku_model,
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

# ─── Summary ──────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  ⚡ SPEED OPTIMIZATION COMPLETE")
print("=" * 65)
print(f"\n  Primary model (ANTHROPIC_MODEL): {sonnet_combo}")
print(f"  Sonnet:  {sonnet_combo}")
print(f"  Opus:    nvidia free")
print(f"  Haiku:   {haiku_model}")
print(f"\n  🏎️  Fastest live model: {working[0][0]} ({working[0][2]}s)")
print(f"  Working: {len(working)} models  |  Down: {len(dead)} models")
print(f"\n  Live ranking:")
for i, (m, p, ms) in enumerate(working[:5]):
    print(f"    #{i+1} {m:50s} {ms:.2f}s")
print(f"\n  ✅ Restart Claude Code to apply changes!\n")
