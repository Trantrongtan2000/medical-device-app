#!/usr/bin/env python3
import sys, importlib
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')

# Clear module cache
mod_names = [k for k in sys.modules.keys() if 'app' in k or 'routes' in k or 'main' in k]
for m in mod_names:
    del sys.modules[m]

from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
print("=== T2.3 Transfers (fresh) ===\n")

# POST create transfer
r = c.post("/api/transfers", json={"device_id": 1, "to_facility_id": 1, "giver_name": "Test User", "receiver_name": "BME Team", "transfer_reason": "Thay thế", "form_code": "TTX-2026-001"})
print(f"[POST] /api/transfers → status={r.status_code}, body={r.text}")

if r.status_code == 200:
    tid = r.json()["id"]
    # PUT confirm
    r2 = c.put(f"/api/transfers/{tid}/confirm")
    print(f"[PUT] /confirm → {r2.json()}")
    print("\n=== DONE ===")
else:
    # Debug
    from pydantic import ValidationError
    print(r.text)