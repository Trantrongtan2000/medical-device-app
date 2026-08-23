"""
Routes Giai đoạn 1 — Maintenance Schedules + Alerts (theo PLAN_GĐ1_TONG_HOP.md)
- CRUD maintenance_schedules (bảng đã migrate: +maintenance_type, frequency_days, last_completed_at, next_due_at, assigned_staff_id)
- POST /api/schedules/generate  — engine sinh lịch hàng loạt từ devices (tránh trùng lịch active)
- GET  /api/alerts/expiring    — cảnh báo kiểm định sắp hết hạn (90/60/30) + bảo trì quá hạn (tính live)
- POST /api/alerts/check       — ghi notifications snapshot
- GET  /api/notifications      — danh sách thông báo
- PUT  /api/notifications/{id}/read
constructor: FastAPI + SQLite thuần (pattern app/routes.py)
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import qrcode
import base64
from io import BytesIO

from .database import get_db

router = APIRouter()

# ------------------- SCHEMAS -------------------

class ScheduleCreate(BaseModel):
    device_id: int
    scheduled_date: date
    due_date: Optional[date] = None
    maintenance_type: str = "PREVENTIVE"
    frequency_days: Optional[int] = None
    notes: Optional[str] = None
    assigned_staff_id: Optional[int] = None

class ScheduleUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    maintenance_type: Optional[str] = None
    frequency_days: Optional[int] = None
    last_completed_at: Optional[date] = None
    next_due_at: Optional[date] = None
    assigned_staff_id: Optional[int] = None
    notes: Optional[str] = None

class GenerateRequest(BaseModel):
    maintenance_type: Optional[str] = "PREVENTIVE"
    frequency_days: int = 180
    start_date: Optional[date] = None
    due_days: Optional[int] = None
    category_id: Optional[int] = None
    device_ids: Optional[List[int]] = None
    overwrite: bool = False

VALID_TYPES = ("PREVENTIVE", "CALIBRATION", "REPAIR", "INSPECTION", "HANDOVER")
VALID_STATUS = ("PENDING", "IN_PROGRESS", "COMPLETED", "OVERDUE")


def check_device(db, device_id: int) -> None:
    row = db.execute("SELECT id FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Thiết bị {device_id} không tồn tại")


# ------------------- CRUD -------------------

@router.get("/api/schedules/list")
async def list_schedules(
    status: Optional[str] = None,
    device_id: Optional[int] = None,
    maintenance_type: Optional[str] = None,
    due_before: Optional[date] = None,
    limit: int = 300,
    db = Depends(get_db),
):
    """Danh sách lịch bảo trì (bảng maintenance_schedules) + tên thiết bị/khoa"""
    q = """
        SELECT ms.*, d.device_name, d.serial_no, d.model, f.name AS facility, s.full_name AS assigned_staff
        FROM maintenance_schedules ms
        JOIN devices d ON d.id = ms.device_id
        LEFT JOIN facilities f ON f.id = d.facility_id
        LEFT JOIN bme_staff s ON s.id = ms.assigned_staff_id
        WHERE 1=1
    """
    params = []
    if status:
        q += " AND ms.status = ?"; params.append(status)
    if device_id:
        q += " AND ms.device_id = ?"; params.append(device_id)
    if maintenance_type:
        q += " AND ms.maintenance_type = ?"; params.append(maintenance_type)
    if due_before:
        q += " AND ms.due_date <= ?"; params.append(due_before.isoformat())
    q += " ORDER BY ms.due_date ASC, ms.id DESC LIMIT ?"; params.append(limit)
    rows = db.execute(q, params).fetchall()
    return [dict(r) for r in rows]


@router.get("/api/schedules/list/{schedule_id}")
async def get_schedule(schedule_id: int, db = Depends(get_db)):
    row = db.execute(
        """SELECT ms.*, d.device_name, d.serial_no, f.name AS facility, s.full_name AS assigned_staff
           FROM maintenance_schedules ms
           JOIN devices d ON d.id = ms.device_id
           LEFT JOIN facilities f ON f.id = d.facility_id
           LEFT JOIN bme_staff s ON s.id = ms.assigned_staff_id
           WHERE ms.id = ?""", (schedule_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, f"Lịch {schedule_id} không tồn tại")
    return dict(row)


@router.post("/api/schedules")
async def create_schedule(req: ScheduleCreate, db = Depends(get_db)):
    check_device(db, req.device_id)
    if req.maintenance_type not in VALID_TYPES:
        raise HTTPException(422, f"maintenance_type phải thuộc {VALID_TYPES}")
    due = req.due_date or req.scheduled_date
    cur = db.execute(
        """INSERT INTO maintenance_schedules
           (device_id, scheduled_date, due_date, status, notes, maintenance_type, frequency_days, assigned_staff_id)
           VALUES (?, ?, ?, 'PENDING', ?, ?, ?, ?)""",
        (req.device_id, req.scheduled_date.isoformat(), due.isoformat(),
         req.notes, req.maintenance_type, req.frequency_days, req.assigned_staff_id),
    )
    db.commit()
    return {"id": cur.lastrowid, "status": "created"}


@router.put("/api/schedules/{schedule_id}")
async def update_schedule(schedule_id: int, req: ScheduleUpdate, db = Depends(get_db)):
    row = db.execute("SELECT * FROM maintenance_schedules WHERE id = ?", (schedule_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Lịch {schedule_id} không tồn tại")
    if req.maintenance_type is not None and req.maintenance_type not in VALID_TYPES:
        raise HTTPException(422, f"maintenance_type phải thuộc {VALID_TYPES}")
    if req.status is not None and req.status not in VALID_STATUS:
        raise HTTPException(422, f"status phải thuộc {VALID_STATUS}")
    fields, params = [], []
    for f in ("scheduled_date", "due_date", "status", "maintenance_type", "frequency_days",
              "last_completed_at", "next_due_at", "assigned_staff_id", "notes"):
        v = getattr(req, f, None)
        if v is not None:
            fields.append(f"{f} = ?")
            params.append(v.isoformat() if isinstance(v, date) else v)
    if not fields:
        raise HTTPException(422, "Không có trường cập nhật")
    params.append(schedule_id)
    db.execute(f"UPDATE maintenance_schedules SET {', '.join(fields)} WHERE id = ?", params)
    db.commit()
    return {"id": schedule_id, "status": "updated"}


@router.delete("/api/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int, db = Depends(get_db)):
    row = db.execute("SELECT id FROM maintenance_schedules WHERE id = ?", (schedule_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Lịch {schedule_id} không tồn tại")
    db.execute("DELETE FROM maintenance_schedules WHERE id = ?", (schedule_id,))
    db.commit()
    return {"id": schedule_id, "status": "deleted"}


# ------------------- ENGINE GENERATE -------------------

@router.post("/api/schedules/generate")
async def generate_schedules(req: GenerateRequest, db = Depends(get_db)):
    """Engine sinh lịch bảo trì hàng loạt: đọc danh sách thiết bị khớp filter, tạo lịch chu kỳ.
    - Tránh trùng: bỏ qua thiết bị đã có lịch PENDING/IN_PROGRESS (nếu overwrite=False)
    - Transaction: mọi insert trong 1 transaction, lỗi → rollback toàn bộ
    """
    if req.maintenance_type not in VALID_TYPES:
        raise HTTPException(422, f"maintenance_type phải thuộc {VALID_TYPES}")
    if req.frequency_days <= 0:
        raise HTTPException(422, "frequency_days phải > 0")

    q = "SELECT id, device_name FROM devices WHERE 1=1"
    params = []
    if req.category_id:
        q += " AND category_id = ?"; params.append(req.category_id)
    if req.device_ids:
        q += " AND id IN (%s)" % ",".join("?" * len(req.device_ids)); params.extend(req.device_ids)

    devices = db.execute(q, params).fetchall()
    if not devices:
        return {"generated": 0, "skipped": 0, "message": "Không có thiết bị khớp filter"}

    start = req.start_date or date.today()
    due = start + timedelta(days=req.due_days if req.due_days is not None else req.frequency_days)

    generated, skipped = 0, 0
    try:
        db.execute("BEGIN")
        for d in devices:
            if not req.overwrite:
                has_active = db.execute(
                    "SELECT 1 FROM maintenance_schedules WHERE device_id = ? AND status IN ('PENDING','IN_PROGRESS') LIMIT 1",
                    (d["id"],)
                ).fetchone()
                if has_active:
                    skipped += 1
                    continue
            db.execute(
                """INSERT INTO maintenance_schedules
                   (device_id, scheduled_date, due_date, status, maintenance_type, frequency_days)
                   VALUES (?, ?, ?, 'PENDING', ?, ?)""",
                (d["id"], start.isoformat(), due.isoformat(), req.maintenance_type, req.frequency_days),
            )
            generated += 1
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Generate lỗi, rollback toàn bộ: {e}")

    return {"generated": generated, "skipped": skipped,
            "start_date": start.isoformat(), "due_date": due.isoformat(),
            "maintenance_type": req.maintenance_type, "frequency_days": req.frequency_days}


# ------------------- ALERTS (tính live) -------------------

@router.get("/api/alerts/expiring")
async def alerts_expiring(days_90: int = 90, days_60: int = 60, days_30: int = 30, db = Depends(get_db)):
    """Cảnh báo: kiểm định hết hạn trong 90/60/30 ngày + bảo trì quá hạn. Tính live, không cần job nền."""
    today = date.today()

    certs = db.execute(
        """SELECT c.id AS cert_id, c.device_id, d.device_name, d.serial_no, c.certificate_no,
                  c.recalibration_date AS due_date, c.result_status
           FROM calibration_certificates c
           JOIN devices d ON d.id = c.device_id
           WHERE c.recalibration_date IS NOT NULL AND c.recalibration_date != ''
        """
    ).fetchall()

    schedules = db.execute(
        """SELECT ms.id, ms.device_id, d.device_name, d.serial_no, ms.maintenance_type,
                  ms.due_date, ms.status
           FROM maintenance_schedules ms
           JOIN devices d ON d.id = ms.device_id
           WHERE ms.status IN ('PENDING','IN_PROGRESS')
        """
    ).fetchall()

    def days_left(v):
        try:
            return (date.fromisoformat(str(v)) - today).days
        except Exception:
            return None

    items = []
    for c in certs:
        dl = days_left(c["due_date"])
        if dl is None:
            continue
        if dl < 0:
            items.append({"type": "CALIBRATION", "ref_id": c["cert_id"], "device_id": c["device_id"],
                          "device_name": c["device_name"], "serial_no": c["serial_no"],
                          "reference": c["certificate_no"], "due_date": c["due_date"],
                          "days_left": dl, "level": "CRITICAL", "status": "OVERDUE"})
        elif dl <= days_30:
            items.append({"type": "CALIBRATION", "ref_id": c["cert_id"], "device_id": c["device_id"],
                          "device_name": c["device_name"], "serial_no": c["serial_no"],
                          "reference": c["certificate_no"], "due_date": c["due_date"],
                          "days_left": dl, "level": "CRITICAL", "status": "CRITICAL"})
        elif dl <= days_60:
            items.append({"type": "CALIBRATION", "ref_id": c["cert_id"], "device_id": c["device_id"],
                          "device_name": c["device_name"], "serial_no": c["serial_no"],
                          "reference": c["certificate_no"], "due_date": c["due_date"],
                          "days_left": dl, "level": "WARNING", "status": "ALERT"})
        elif dl <= days_90:
            items.append({"type": "CALIBRATION", "ref_id": c["cert_id"], "device_id": c["device_id"],
                          "device_name": c["device_name"], "serial_no": c["serial_no"],
                          "reference": c["certificate_no"], "due_date": c["due_date"],
                          "days_left": dl, "level": "INFO", "status": "WARNING"})

    for s in schedules:
        dl = days_left(s["due_date"])
        if dl is None:
            continue
        if dl < 0:
            items.append({"type": "MAINTENANCE", "ref_id": s["id"], "device_id": s["device_id"],
                          "device_name": s["device_name"], "serial_no": s["serial_no"],
                          "reference": s["maintenance_type"], "due_date": s["due_date"],
                          "days_left": dl, "level": "CRITICAL", "status": "OVERDUE"})
        elif dl <= days_30:
            items.append({"type": "MAINTENANCE", "ref_id": s["id"], "device_id": s["device_id"],
                          "device_name": s["device_name"], "serial_no": s["serial_no"],
                          "reference": s["maintenance_type"], "due_date": s["due_date"],
                          "days_left": dl, "level": "WARNING", "status": "DUE_SOON"})

    items.sort(key=lambda x: x["days_left"])
    return {"generated_at": today.isoformat(), "count": len(items), "items": items}


@router.get("/api/alerts/summary")
async def alerts_summary(db = Depends(get_db)):
    """6 chỉ số dashboard: total/active/maintenance due/overdue/certs expiring/out-of-service + risk distribution"""
    today = date.today()
    total = db.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    active = db.execute("SELECT COUNT(*) FROM devices WHERE status = 'IN_SERVICE'").fetchone()[0]
    out_of_service = db.execute(
        "SELECT COUNT(*) FROM devices WHERE status IN ('MAINTENANCE','REPAIR','RETIRED')"
    ).fetchone()[0]
    
    # 1. Tổng số hàng GCN hết hạn (certificate records)
    overdue_certs_rows = db.execute(
        """SELECT COUNT(*) FROM calibration_certificates
           WHERE recalibration_date IS NOT NULL AND recalibration_date != ''
             AND date(recalibration_date) < date('now', 'localtime')"""
    ).fetchone()[0]
    
    # 2. Số thiết bị có GCN mới nhất đã hết hạn (262 thiết bị)
    devices_overdue_latest = db.execute(
        """WITH latest_certs AS (
            SELECT device_id, recalibration_date,
                   ROW_NUMBER() OVER (PARTITION BY device_id ORDER BY COALESCE(recalibration_date, calibration_date) DESC) as rn
            FROM calibration_certificates
            WHERE recalibration_date IS NOT NULL AND recalibration_date != ''
        )
        SELECT COUNT(*) FROM latest_certs WHERE rn = 1 AND date(recalibration_date) < date('now', 'localtime')"""
    ).fetchone()[0]

    # 3. Số hàng GCN sắp hết hạn trong 90 ngày (17 rows)
    expiring_certs_rows = db.execute(
        """SELECT COUNT(*) FROM calibration_certificates
           WHERE recalibration_date IS NOT NULL AND recalibration_date != ''
             AND date(recalibration_date) BETWEEN date('now', 'localtime')
                 AND date('now', 'localtime', '+90 day')"""
    ).fetchone()[0]

    # 4. Số thiết bị có GCN mới nhất sắp hết hạn trong 90 ngày (16 thiết bị)
    devices_expiring_90d_latest = db.execute(
        """WITH latest_certs AS (
            SELECT device_id, recalibration_date,
                   ROW_NUMBER() OVER (PARTITION BY device_id ORDER BY COALESCE(recalibration_date, calibration_date) DESC) as rn
            FROM calibration_certificates
            WHERE recalibration_date IS NOT NULL AND recalibration_date != ''
        )
        SELECT COUNT(*) FROM latest_certs WHERE rn = 1 
          AND date(recalibration_date) BETWEEN date('now', 'localtime') AND date('now', 'localtime', '+90 day')"""
    ).fetchone()[0]

    overdue_maint = db.execute(
        """SELECT COUNT(*) FROM maintenance_schedules
           WHERE status IN ('PENDING','IN_PROGRESS') AND due_date < date('now', 'localtime')"""
    ).fetchone()[0]
    due_maint = db.execute(
        """SELECT COUNT(*) FROM maintenance_schedules
           WHERE status IN ('PENDING','IN_PROGRESS')
             AND due_date BETWEEN date('now', 'localtime') AND date('now', 'localtime', '+30 day')"""
    ).fetchone()[0]

    # Phân bổ rủi ro A/B/C/D thực tế
    risk_rows = db.execute("SELECT risk_level, COUNT(*) FROM devices GROUP BY risk_level").fetchall()
    risk_dict = {r[0]: r[1] for r in risk_rows if r[0]}

    return {
        "total_devices": total, "active_devices": active, "out_of_service": out_of_service,
        "certs_overdue_rows": overdue_certs_rows,
        "devices_overdue_latest": devices_overdue_latest,
        "certs_expiring_90d_rows": expiring_certs_rows,
        "devices_expiring_90d_latest": devices_expiring_90d_latest,
        "certs_overdue": devices_overdue_latest,
        "certs_expiring_90d": devices_expiring_90d_latest,
        "maintenance_overdue": overdue_maint, "maintenance_due_30d": due_maint,
        "risk_distribution": risk_dict,
        "as_of": today.isoformat(),
    }


# ------------------- NOTIFICATIONS (snapshot) -------------------

@router.post("/api/alerts/check")
async def alerts_check(db = Depends(get_db)):
    """Ghi snapshot các cảnh báo hiện tại vào bảng notifications (idempotent: bỏ trùng ref chưa đọc)."""
    alerts = await alerts_expiring(db=db)
    inserted = 0
    for a in alerts["items"]:
        dup = db.execute(
            """SELECT id FROM notifications
               WHERE ref_type = ? AND ref_id = ? AND is_read = 0 LIMIT 1""",
            (a["type"], a["ref_id"]),
        ).fetchone()
        if dup:
            continue
        db.execute(
            """INSERT INTO notifications (ref_type, ref_id, message, level, days_left)
               VALUES (?, ?, ?, ?, ?)""",
            (a["type"], a["ref_id"],
             f"{a['device_name']} ({a['serial_no'] or 'N/A'}) — {a['reference']} hạn {a['due_date']}, còn {a['days_left']} ngày",
             a["level"], a["days_left"]),
        )
        inserted += 1
    db.commit()
    return {"inserted": inserted, "active_alerts": alerts["count"]}


@router.get("/api/notifications")
async def list_notifications(unread_only: bool = False, limit: int = 100, db = Depends(get_db)):
    q = "SELECT * FROM notifications"
    params = []
    if unread_only:
        q += " WHERE is_read = 0"
    q += " ORDER BY created_at DESC, id DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(q, params).fetchall()
    return [dict(r) for r in rows]


@router.put("/api/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: int, db = Depends(get_db)):
    row = db.execute("SELECT id FROM notifications WHERE id = ?", (notif_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Thông báo {notif_id} không tồn tại")
    db.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    db.commit()
    return {"id": notif_id, "status": "read"}


@router.get("/api/devices/{device_id}/qr-code")
async def generate_qr_code(device_id: int, db = Depends(get_db)):
    """Tạo QR code cho thiết bị — trả về base64 image + payload cho mobile scanning"""
    dev = db.execute("SELECT device_name, serial_no, certification_no FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not dev:
        raise HTTPException(404, "Thiết bị không tồn tại")
    
    payload = f"TTBYT-BV7|{device_id}|{dev['device_name']}|{dev['serial_no'] or 'N/A'}"
    if dev['certification_no']:
        payload += f"|CN:{dev['certification_no']}"
    
    try:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        b64 = base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        return {"device_id": device_id, "payload": payload, "error": str(e)}
    
    return {
        "device_id": device_id,
        "device_name": dev['device_name'],
        "serial_no": dev['serial_no'],
        "payload": payload,
        "qr_base64": b64,
        "format": "PNG 8-bit"
    }