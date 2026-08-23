# -*- coding: utf-8 -*-
"""Test Phase 1 frontend-backend integration"""
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)

print("=== TEST T1.2-T1.4 APIs ===\n")

# 1. alerts/summary
r = c.get("/api/alerts/summary")
assert r.status_code == 200, f"alerts/summary fail: {r.status_code}"
s = r.json()
for k in ("total_devices", "active_devices", "certs_overdue", "certs_expiring_90d", "maintenance_overdue"):
    assert k in s, f"missing {k}"
print(f"[OK] /api/alerts/summary → total={s['total_devices']}, overdue={s['certs_overdue']}, maint_overdue={s['maintenance_overdue']}")

# 2. schedules/list
r = c.get("/api/schedules/list?limit=10")
assert r.status_code == 200, f"schedules/list fail: {r.status_code}"
lst = r.json()
print(f"[OK] /api/schedules/list → {len(lst)} schedules")

# 3. alerts/expiring
r = c.get("/api/alerts/expiring")
assert r.status_code == 200, f"alerts/expiring fail: {r.status_code}"
a = r.json()
print(f"[OK] /api/alerts/expiring → {a['count']} alerts, items={len(a['items'])}")

# 4. notifications
r = c.post("/api/alerts/check")
assert r.status_code == 200
n = r.json()
print(f"[OK] POST /api/alerts/check → inserted={n['inserted']}")

r = c.get("/api/notifications?limit=5")
assert r.status_code == 200
print(f"[OK] /api/notifications → {len(r.json())} notifications")

print("\n=== ALL T1.2-T1.4 TESTS PASSED ===")