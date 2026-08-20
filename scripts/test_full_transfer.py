#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from app.main import app
from fastapi.testclient import TestClient
c = TestClient(app)

# POST đầy đủ
r = c.post("/api/transfers", json={
    "device_id": 1,
    "to_facility_id": 1, 
    "giver_name": "Test User",
    "receiver_name": "BME Team",
    "transfer_reason": "Thay thế máy"
})
print(f"POST status: {r.status_code}")
if r.status_code == 200:
    tid = r.json()['id']
    r2 = c.put(f"/api/transfers/{tid}/confirm")
    print(f"CONFIRM: {r2.json()}")
else:
    print(f"ERROR: {r.text[:500]}")