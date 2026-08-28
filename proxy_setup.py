"""
Auto Free Proxy Fetcher for OmniRoute OpenCode Accounts
Fetches free SOCKS5/HTTP proxies and assigns them to OpenCode accounts
"""
import urllib.request, json, sys, sqlite3, time, socket
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"C:\Users\manit\.omniroute\storage.sqlite"
OC_CONN_ID = "fbbfa2c6-74b7-4b02-bee6-70735a16e4cc"  # OpenCode Account 1

def fetch_proxies():
    """Fetch free proxies from multiple sources"""
    proxies = []
    
    # Source 1: ProxyScrape SOCKS5
    sources = [
        ("https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5&timeout=5000&country=all&ssl=all&anonymity=all&simplified=true", "socks5"),
        ("https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite&simplified=true", "http"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt", "socks5"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", "http"),
    ]
    
    for url, ptype in sources:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode('utf-8', errors='ignore')
                for line in text.strip().split('\n'):
                    line = line.strip()
                    if ':' in line and line:
                        parts = line.split(':')
                        if len(parts) == 2:
                            host, port = parts
                            try:
                                proxies.append({"host": host.strip(), "port": int(port.strip()), "type": ptype})
                            except:
                                pass
            print(f"  Fetched from {url.split('/')[2]}: {len([p for p in proxies if p['type']==ptype])} {ptype} proxies")
        except Exception as e:
            print(f"  Failed {url.split('/')[2]}: {e}")
    
    return proxies

def test_proxy(host, port, timeout=3):
    """Quick connectivity test"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except:
        return False

print("=" * 55)
print("  OmniRoute OpenCode Proxy Auto-Setup")
print("=" * 55)

# Fetch proxies
print("\n[1/3] Fetching free proxies...")
all_proxies = fetch_proxies()
print(f"\n  Total fetched: {len(all_proxies)} proxies")

# Read current OpenCode fingerprints (27 accounts)
db = sqlite3.connect(DB_PATH)
cur = db.cursor()
cur.execute("SELECT provider_specific_data FROM provider_connections WHERE id=?", (OC_CONN_ID,))
row = cur.fetchone()
specific_data = json.loads(row[0]) if row else {}
fingerprints = specific_data.get("fingerprints", [])
print(f"\n[2/3] OpenCode accounts (fingerprints): {len(fingerprints)}")

# Test proxies and pick working ones
print(f"\n[3/3] Testing proxies (need {len(fingerprints)} working ones)...")
working_proxies = []
tested = 0
for p in all_proxies:
    if len(working_proxies) >= len(fingerprints):
        break
    tested += 1
    if tested % 20 == 0:
        print(f"  Tested {tested}/{min(200, len(all_proxies))}... Found {len(working_proxies)} working")
    if tested > 200:  # Max test 200
        break
    if test_proxy(p["host"], p["port"]):
        working_proxies.append(p)
        print(f"  LIVE: {p['type']}://{p['host']}:{p['port']}")

print(f"\n  Working proxies found: {len(working_proxies)}/{len(fingerprints)} needed")

if not working_proxies:
    print("\n  No working proxies found from free sources!")
    print("  Alternatives:")
    print("  1. Try again later (proxy lists refresh)")
    print("  2. Use a paid proxy service")  
    print("  3. Accept OpenCode rate limits (use as backup only)")
    db.close()
    exit(0)

# Assign proxies to fingerprints
account_proxies = []
for i, fp in enumerate(fingerprints):
    if i < len(working_proxies):
        p = working_proxies[i]
        account_proxies.append({
            "fingerprint": fp,
            "proxy": {
                "type": p["type"].upper(),
                "host": p["host"],
                "port": p["port"],
                "username": "",
                "password": ""
            }
        })

# Update DB
specific_data["accountProxies"] = account_proxies
cur.execute(
    "UPDATE provider_connections SET provider_specific_data=?, updated_at=? WHERE id=?",
    (json.dumps(specific_data), datetime.now(timezone.utc).isoformat(), OC_CONN_ID)
)
db.commit()
db.close()

print(f"\n  Assigned {len(account_proxies)} proxies to OpenCode accounts")
print(f"\n========================================")
print(f"  DONE! {len(account_proxies)} accounts now have unique proxy IPs")
print(f"  Each account = different IP = independent rate limit!")
print(f"  Refresh OmniRoute UI to see proxy assignments.")
print(f"========================================\n")
