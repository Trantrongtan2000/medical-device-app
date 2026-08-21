#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from app.main import app
from fastapi.testclient import TestClient
c = TestClient(app)

print("=== T2.3 Transfers (fixed) ===\n")

# POST create với field bắt buộc
r = c.post("/api/transfers", json={"device_id": 1, "to_facility_id": 1, "giver_name": "A", "receiver_name": "B", "transfer_reason": "test"})
print(f"[POST] -> status={r.status_code} {r.json() if r.status_code==200 else r.text[:200]}")

if r.status_code == 200:
    tid = r.json()['id']
    r2 = c.put(f"/api/transfers/{tid}/confirm")
    print(f"[PUT confirm] -> {r2.json()}")
    
    r3 = c.get(f"/api/transfers/{tid}")
    print(f"[GET] -> status={r3.json()['status']}")
    
    print("\n=== PASSED ===")