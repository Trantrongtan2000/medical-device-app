#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Patch để thêm POST /api/inspections
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')

# Import và test API
from app.main import app
from fastapi.testclient import TestClient
c = TestClient(app)

print("=== Test /api/inspections endpoint ===\n")

# POST inspection
r = c.post("/api/inspections", json={
    "device_id": 1,
    "inspector_name": "BME-001",
    "department": "CĐHA",
    "power_ok": True,
    "physical_ok": True,
    "gas_pressure_ok": True,
    "selftest_ok": True,
    "notes": "Test từ FastAPI"
})
print(f"POST /api/inspections → status={r.status_code}")
print(f"Response: {r.text[:200]}")

if r.status_code == 200:
    inv_id = r.json()["id"]
    print(f"\n✅ Tạo inspection thành công ID={inv_id}")
    
    # GET history
    r2 = c.get("/api/inspections/pre-use?status=PASSED")
    print(f"GET /api/inspections/pre-use → {len(r2.json())} inspections PASSED")
    
    print("\n=== PASSED ===")
else:
    print(f"Lỗi: {r.text}")