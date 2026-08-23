#!/usr/bin/env python3
import sys, json
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
print("=== T2.1 Pre-use Inspections API ===\n")

# Test GET device inspection (no data)
r = c.get("/api/devices/1/pre-use-inspection")
j = r.json()
print(f"[OK] GET device 1 pre-use: has_inspection={j['has_inspection']}")

# Test POST create inspection
r = c.post("/api/devices/1/pre-use-inspection", json={
    "device_id": 1, "inspector_name": "BME-001", "department": "CĐHA",
    "power_ok": True, "physical_ok": True, "gas_pressure_ok": True, "selftest_ok": False, "notes": "sensor hiu hửa"
})
assert r.status_code == 200, r.text
j = r.json()
print(f"[OK] POST inspection created: id={j['id']}, overall={j['overall_status']}")

# Test GET list inspections
r = c.get("/api/inspections/pre-use?status=FAILED")
assert r.status_code == 200
lst = r.json()
print(f"[OK] GET inspections list: {len(lst)} items, status=FAILED")

# Test PUT update
inv_id = j['id']
r = c.put(f"/api/devices/1/pre-use-inspection/{inv_id}", json={
    "selftest_ok": True, "notes": "đã sửa sensor"
})
assert r.status_code == 200
print(f"[OK] PUT update inspection: id={inv_id}")

print("\n=== T2.1 ALL TESTS PASSED ===")