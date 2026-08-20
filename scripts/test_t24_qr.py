#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from app.main import app
from fastapi.testclient import TestClient
c = TestClient(app, raise_server_exceptions=False)

print("=== T2.4 QR Code ===\n")

r = c.get("/api/devices/1/qr-code")
print(f"[GET] /api/devices/1/qr-code → {r.status_code}")
j = r.json()
print(f"payload: {j.get('payload', 'N/A')}")
print(f"qr_base64 len: {len(j.get('qr_base64',''))}")
print(f"device: {j.get('device_name')}")

print("\n=== PASSED ===")