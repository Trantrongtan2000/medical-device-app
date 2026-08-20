#!/usr/bin/env python3
import subprocess, json, sys, os
os.chdir(r'C:\Users\tantt\Downloads\medical-device-app')

# Test bằng cách chạy FastAPI server nhanh
code = '''
import sys
sys.path.insert(0, r"C:\\Users\\tantt\\Downloads\\medical-device-app")
from app.main import app
from fastapi.testclient import TestClient
c = TestClient(app)

# 1. GET list
r = c.get("/api/transfers?limit=5")
print(f"OK: GET transfers → {r.status_code}, {len(r.json())} items")

# 2. POST create
r = c.post("/api/transfers", json={"device_id": 1, "to_facility_id": 1, "transfer_reason": "Test"})
print(f"OK: POST transfer → {r.status_code} {r.json()}")

tid = r.json()["id"]

# 3. PUT confirm  
r2 = c.put(f"/api/transfers/{tid}/confirm")
print(f"OK: PUT confirm → {r2.status_code} {r2.json()}")

# 4. GET device history
r3 = c.get("/api/devices/1/transfers/history")  
print(f"OK: GET device history → {len(r3.json())} records")

print("ALL PASS")
'''
result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=30, cwd=r'C:\Users\tantt\Downloads\medical-device-app')
print(result.stdout)
if result.stderr:
    for line in result.stderr.split('\n')[:5]:
        if line.strip():
            print("ERR:", line)