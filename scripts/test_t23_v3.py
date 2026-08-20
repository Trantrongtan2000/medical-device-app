#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
print("=== T2.3 Transfers (raw body fix) ===\n")

# POST create
r = c.post("/api/transfers", json={"device_id": 1, "to_facility_id": 1, "giver_name": "BME Team", "transfer_reason": "Thay thế"})
print(f"[POST /api/transfers] → status={r.status_code}, {r.json()}")

if r.status_code == 200:
    tid = r.json()["id"]
    
    # PUT confirm
    r2 = c.put(f"/api/transfers/{tid}/confirm")
    print(f"[PUT /confirm] → {r2.json()}")
    
    # GET history
    r3 = c.get("/api/devices/1/transfers/history")
    print(f"[GET /history] → {r3.json()}")
    
    print("\n=== PASSED ===")
else:
    print(f"ERROR: {r.text[:200]}")