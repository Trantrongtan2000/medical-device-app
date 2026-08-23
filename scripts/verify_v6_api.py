import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

res1 = urllib.request.urlopen('http://10.30.32.201:8000/api/contracts')
d1 = json.loads(res1.read().decode('utf-8'))

res2 = urllib.request.urlopen('http://10.30.32.201:8000/api/directory/suppliers')
d2 = json.loads(res2.read().decode('utf-8'))

res3 = urllib.request.urlopen('http://10.30.32.201:8000/api/stats')
d3 = json.loads(res3.read().decode('utf-8'))

print(f"✅ Total Contracts in API: {len(d1)}")
print(f"✅ Total Suppliers in API: {len(d2)}")
print(f"✅ Total Devices in API Stats: {d3.get('total_devices')}")

print("\n--- SAMPLE CONTRACTS FROM MASTERDATA V6 ---")
for c in d1[:5]:
    print(f"  • HĐ {c['contract_no']}: {c['contract_name']} | NCC: {c['supplier_name']}")

print("\n--- SAMPLE SUPPLIERS FROM MASTERDATA V6 ---")
for s in d2[:5]:
    print(f"  • {s['supplier_name']} | LH: {s['contact_person']} ({s['phone']})")
