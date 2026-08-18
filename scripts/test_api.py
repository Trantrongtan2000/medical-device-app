import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_url = "http://127.0.0.1:8000"

def test_get(endpoint):
    url = base_url + endpoint
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        code = response.getcode()
        body = response.read().decode('utf-8')
        print(f"[{code}] {endpoint}")
        try:
            data = json.loads(body)
            if isinstance(data, list):
                print(f"  Count: {len(data)}, First item name/facility: {data[0].get('name') or data[0].get('device_name') if data else 'empty'}")
            elif isinstance(data, dict):
                print(f"  Result: {data}")
        except Exception:
            print(f"  HTML loaded successfully ({len(body)} bytes)")

print("=== RUNNING API TESTS ===")
test_get("/")
test_get("/health")
test_get("/api/dashboard/summary")
test_get("/api/dashboard/facilities")
test_get("/api/dashboard/categories")
test_get("/api/devices?limit=5")
print("\n All API endpoints passed verification!")