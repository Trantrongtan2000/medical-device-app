# -*- coding: utf-8 -*-
"""T1.2/T1.3/T1.4 smoke test: schedules CRUD + generate + alerts + notifications (TestClient trên DB thật)"""
import sys
sys.path.insert(0, r'C:\Users\tantt\Downloads\medical-device-app')
from datetime import date, timedelta
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ok = 0
def check(name, cond, detail=''):
    global ok
    assert cond, f"FAIL: {name} — {detail}"
    ok += 1
    print(f"[PASS] {name}")

# 0. Dọn lịch test còn sót từ lần chạy trước (PREVENTIVE scheduled 2026-09-01, do generate)
from app.database import get_db_connection
with get_db_connection() as c:
    c.execute("DELETE FROM maintenance_schedules WHERE maintenance_type='PREVENTIVE' AND scheduled_date='2026-09-01' AND notes IS NULL")
    c.commit()
print("[CLEAN] lịch test cũ đã xóa")

# 1. Generate: tạo lịch cho 3 thiết bị đầu
r = client.post("/api/schedules/generate", json={
    "maintenance_type": "PREVENTIVE", "frequency_days": 180,
    "start_date": "2026-09-01", "due_days": 180, "limit_devices": None
})
print("generate1:", r.status_code, r.json() if r.status_code != 200 else r.json()["generated"])
check("generate trả 200", r.status_code == 200, r.text[:300])
g1 = r.json()
check("generate > 0", g1["generated"] > 0, str(g1))

# 2. Chạy lại → phải skip toàn bộ (tránh trùng)
r2 = client.post("/api/schedules/generate", json={
    "maintenance_type": "PREVENTIVE", "frequency_days": 180, "start_date": "2026-09-01"
})
g2 = r2.json()
check("generate lần 2 skip hết (tránh trùng)", g2["generated"] == 0 and g2["skipped"] == g1["generated"], str(g2))

# 3. Danh sách
r3 = client.get("/api/schedules/list")
check("list trả 200 + có dữ liệu", r3.status_code == 200 and len(r3.json()) > 0, str(r3.text[:200]))
first = r3.json()[0]
sid = first["id"]
check("list có tên thiết bị", bool(first.get("device_name")), str(first)[:200])

# 4. Chi tiết
r4 = client.get(f"/api/schedules/list/{sid}")
check("detail trả đúng id", r4.status_code == 200 and r4.json()["id"] == sid)

# 5. Update status + maintenance_type
r5 = client.put(f"/api/schedules/{sid}", json={"status": "IN_PROGRESS", "maintenance_type": "CALIBRATION"})
check("update status", r5.status_code == 200, r5.text)

# 6. Tạo mới thủ công
r6 = client.post("/api/schedules", json={
    "device_id": 1, "scheduled_date": "2026-10-01", "due_date": "2026-10-15",
    "maintenance_type": "REPAIR", "notes": "smoke test"
})
check("create thủ công", r6.status_code == 200, r6.text)
new_id = r6.json()["id"]

# 7. Delete
r7 = client.delete(f"/api/schedules/{new_id}")
check("delete", r7.status_code == 200, r7.text)
r7b = client.get(f"/api/schedules/list/{new_id}")
check("sau delete → 404", r7b.status_code == 404)

# 8. alerts/expiring
r8 = client.get("/api/alerts/expiring")
check("alerts expiring 200", r8.status_code == 200, r8.text[:200])
j8 = r8.json()
check("alerts có count", "count" in j8, str(j8)[:200])

# 9. alerts/summary — 6 chỉ số
r9 = client.get("/api/alerts/summary")
check("summary 200", r9.status_code == 200, r9.text[:200])
j9 = r9.json()
for k in ("total_devices", "active_devices", "certs_expiring_90d", "maintenance_overdue"):
    check(f"summary có {k}", k in j9, str(j9)[:300])

# 10. alerts/check → notifications
r10 = client.post("/api/alerts/check")
check("alerts check 200", r10.status_code == 200, r10.text[:200])

# 11. notifications list + mark read
r11 = client.get("/api/notifications")
check("notifications list 200", r11.status_code == 200, r11.text[:200])
if r11.json():
    nid = r11.json()[0]["id"]
    r12 = client.put(f"/api/notifications/{nid}/read")
    check("mark read", r12.status_code == 200, r12.text)

# 12. validate lỗi: device không tồn tại
r13 = client.post("/api/schedules", json={"device_id": 999999, "scheduled_date": "2026-10-01"})
check("create device ảo → 404", r13.status_code == 404, r13.text[:100])

# 13. validate lỗi: maintenance_type sai
r14 = client.post("/api/schedules/generate", json={"maintenance_type": "XYZ", "frequency_days": 30})
check("maintenance_type sai → 422", r14.status_code == 422, r14.text[:100])

print(f"\n==== ALL {ok} CHECKS PASSED ====")