import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("1. Testing GET /api/sops ...")
res = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/sops').read().decode('utf-8'))
print(f"✅ Found {len(res)} Standard SOPs & Policies:")
for s in res:
    print(f"   [{s['code']}] {s['name']} -> {s['ref']}")

print("\n2. Testing GET /sops (SOP Handbook HTML) ...")
html_bytes = urllib.request.urlopen('http://127.0.0.1:8000/sops').read()
print(f"✅ Served quy_trinh_ttbyt.html successfully! Size: {len(html_bytes)} bytes")
