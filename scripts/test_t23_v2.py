#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from app.main import app
from fastapi.testclient import TestClient
c = TestClient(app)

print("=== T2.3 Transfers (raw body) ===\n")

# POST create
r = c.post("/api/transfers", json={"device_id": 1, "to_facility_id": 1, "giver_name": "A", "receiver_name": "B"})
print(f"[POST /api/transfers] → status={r.status_code}")
print(f"  response: {r.json()}")

if r.status_code == 200:
    tid = r.json()['id']
    
    # PUT confirm
    r2 = c.put(f"/api/transfers/{tid}/confirm")
    print(f"[PUT /api/transfers/{tid}/confirm] → {r2.json()}")
    
    # GET device history
    r3 = c.get("/api/devices/1/transfers/history")
    print(f"[GET /api/devices/1/transfers/history] → {len(r3.json())} records")
    
    print("\n=== PASSED ===")
else:
    print(f"ERROR: {r.text[:300]}")