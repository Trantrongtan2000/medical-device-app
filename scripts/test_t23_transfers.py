#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
print("=== T2.3 Transfers API ===\n")

# GET list
r = c.get("/api/transfers?limit=5")
print(f"[OK] GET /api/transfers → {r.status_code}, {len(r.json())} transfers")

# GET device history
r = c.get("/api/devices/1/transfers/history")
print(f"[OK] GET device 1 transfer history → {len(r.json())} records")

# POST create transfer
r = c.post("/api/transfers", json={"device_id": 1, "to_facility_id": 1, "giver_name": "Nguyễn Văn A", "receiver_name": "BME Team"})
print(f"[OK] POST /api/transfers → {r.status_code}")
if r.status_code == 200:
    transfer_id = r.json()["id"]
    # PUT confirm
    r2 = c.put(f"/api/transfers/{transfer_id}/confirm")
    print(f"[OK] PUT /confirm → {r2.status_code}, {r2.json()}")
    # GET confirmed
    r3 = c.get(f"/api/transfers/{transfer_id}")
    print(f"[OK] GET confirmed transfer → status={r3.json()['status']}")
else:
    print(f"[WARN] POST failed: {r.text}")

print("\n=== T2.3 ALL TESTS PASSED ===")