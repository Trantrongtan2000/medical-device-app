import urllib.request
import json

endpoints = [
    '/health',
    '/api/devices?limit=20&offset=0',
    '/api/facilities',
    '/api/categories',
    '/api/dashboard/summary',
    '/api/dashboard/activity?limit=12',
    '/api/alerts/summary',
    '/api/inspections?limit=50',
    '/api/transfers?limit=50',
    '/api/work-orders?limit=50',
    '/api/contracts',
    '/api/directory/suppliers',
    '/api/staff',
    '/api/oncall/today',
    '/api/oncall/schedule',
    '/api/semantica/stats',
    '/api/keys/config',
    '/api/agent/tools',
    '/api/agent/telemetry'
]

print("=== KIEM TRA TOAN BO ENDPOINTS FRONTEND (CHINH XAC) ===")
all_pass = True
for ep in endpoints:
    url = f"http://127.0.0.1:8000{ep}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as res:
            body = res.read().decode('utf-8')
            data = json.loads(body)
            count = len(data) if isinstance(data, list) else (len(data.keys()) if isinstance(data, dict) else 'ok')
            print(f"[OK 200] {ep:38s} -> Items/Keys: {count}")
    except urllib.error.HTTPError as e:
        print(f"[FAIL HTTP {e.code}] {ep:30s} -> {e.reason}")
        all_pass = False
    except Exception as e:
        print(f"[FAIL ERR] {ep:30s} -> {e}")
        all_pass = False

if all_pass:
    print("\n🎉 TOAN BO 100% ENDPOINTS HOAT DONG HOAN HAO!")
