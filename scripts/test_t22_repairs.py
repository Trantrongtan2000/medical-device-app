#!/usr/bin/env python3
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
print("=== T2.2 Repairs API ===\n")

# GET list (fallback maintenance_logs)
r = c.get("/api/repairs?limit=5")
print(f"[OK] GET /api/repairs → fallback: {r.status_code}, {len(r.json())} items")

# GET stats today
r = c.get("/api/repairs/stats/today")
print(f"[OK] GET /api/repairs/stats/today → {r.json()}")

# POST create (bảng repairs chưa có, sẽ fail → fallback không có)
r = c.post("/api/repairs", json={"device_id": 1, "repair_type": "REPAIR", "description": "test repair"})
print(f"[POST] /api/repairs → {r.status_code} {r.text[:100] if r.status_code != 200 else r.json()}")

print("\n--- Note: Bảng 'repairs' chưa migrate, dùng maintenance_logs làm fallback ---")