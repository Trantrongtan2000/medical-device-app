"""
T2.2 Repairs API — tách khỏi maintenance_logs cho ghi nhận sửa chữa thiết bị.
Mục tiêu: Theo dõi chi phí, thời gian, nguyên nhân hỏng và trạng thái sửa chữa.
Endpoint: /api/repairs (CRUD), /api/repairs/stats/today
"""
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.database import get_db

router = APIRouter()

# Schema cho repairs (mở rộng từ maintenance_logs hoặc standalone)
# Cột: id, device_id, repair_type, description, actual_cost, parts_used, technician_name, reported_by, status, start_date, end_date, created_at, notes

class RepairCreate(BaseModel):
    device_id: int
    repair_type: str  # 'CALIBRATION', 'REPAIR', 'REPLACEMENT', 'PREVENTIVE'
    description: str
    actual_cost: Optional[float] = None
    parts_used: Optional[str] = None
    technician_name: Optional[str] = None
    reported_by: Optional[str] = None
    start_date: Optional[str] = None
    notes: Optional[str] = None

class RepairUpdate(BaseModel):
    repair_type: Optional[str] = None
    description: Optional[str] = None
    actual_cost: Optional[float] = None
    parts_used: Optional[str] = None
    technician_name: Optional[str] = None
    reported_by: Optional[str] = None
    status: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = None

class Repair(BaseModel):
    id: int
    device_id: int
    repair_type: str
    description: str
    actual_cost: Optional[float] = None
    parts_used: Optional[str] = None
    technician_name: Optional[str] = None
    reported_by: Optional[str] = None
    status: str  # 'REPORTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: Optional[str] = None
    notes: Optional[str] = None
    device_name: Optional[str] = None
    serial_no: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


VALID_STATUSES = ('REPORTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
VALID_REPAIR_TYPES = ('CALIBRATION', 'REPAIR', 'REPLACEMENT', 'PREVENTIVE', 'INSPECTION', 'HANDOVER')

@router.get("/api/repairs")
async def list_repairs(
    status: Optional[str] = None,
    device_id: Optional[int] = None,
    repair_type: Optional[str] = None,
    limit: int = 100,
    db = Depends(get_db)
):
    """Danh sách sửa chữa — gồm cả bảng maintenance_logs nếu chưa có bảng repairs"""
    # Kiểm tra có bảng repairs không, nếu chưa tạo thì query maintenance_logs
    tbl = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repairs'").fetchone()
    if not tbl:
        # fallback tới maintenance_logs nhưng filter repair-type
        q = "SELECT ml.*, d.device_name, d.serial_no, 'REPAIR' as repair_type FROM maintenance_logs ml JOIN devices d ON d.id = ml.device_id WHERE 1=1"
        params = []
        if status:
            q += " AND ml.maintenance_type = ? AND ml.status = ?"; params.extend(['REPAIR', status])
        if device_id:
            q += " AND ml.device_id = ?"; params.append(device_id)
        q += " LIMIT ?"; params.append(limit)
        rows = db.execute(q, params).fetchall()
        return [dict(r) for r in rows]
    
    # có bảng repairs
    q = "SELECT r.*, d.device_name, d.serial_no FROM repairs r JOIN devices d ON d.id = r.device_id WHERE 1=1"
    params = []
    if status:
        q += " AND r.status = ?"; params.append(status)
    if device_id:
        q += " AND r.device_id = ?"; params.append(device_id)
    if repair_type:
        q += " AND r.repair_type = ?"; params.append(repair_type)
    q += " ORDER BY r.start_date DESC, r.id DESC LIMIT ?"; params.append(limit)
    return [dict(r) for r in db.execute(q, params).fetchall()]

@router.post("/api/repairs")
async def create_repair(req: RepairCreate, db = Depends(get_db)):
    dev = db.execute("SELECT id FROM devices WHERE id = ?", (req.device_id,)).fetchone()
    if not dev:
        raise HTTPException(404, f"Device {req.device_id} not found")
    if req.repair_type not in VALID_REPAIR_TYPES:
        raise HTTPException(422, f"repair_type phải thuộc {VALID_REPAIR_TYPES}")
    now = datetime.now().isoformat()
    cur = db.execute("""INSERT INTO repairs
        (device_id, repair_type, description, actual_cost, parts_used, technician_name, reported_by, status, start_date, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'REPORTED', ?, ?, ?)""",
        (req.device_id, req.repair_type, req.description, req.actual_cost, req.parts_used,
         req.technician_name, req.reported_by, req.start_date or now, req.notes, now))
    db.commit()
    return {"id": cur.lastrowid, "status": "created"}

@router.put("/api/repairs/{repair_id}")
async def update_repair(repair_id: int, req: RepairUpdate, db = Depends(get_db)):
    tbl = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repairs'").fetchone()
    if not tbl:
        raise HTTPException(404, "Bảng repairs chưa tồn tại")
    row = db.execute("SELECT * FROM repairs WHERE id = ?", (repair_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Repair {repair_id} not found")
    fields, vals = [], []
    for f in ("repair_type", "description", "actual_cost", "parts_used", "technician_name", "reported_by", "status", "end_date", "notes"):
        v = getattr(req, f, None)
        if v is not None:
            if f in ('actual_cost',) and v is None: continue
            if f == 'status' and v not in VALID_STATUSES:
                raise HTTPException(422, f"status phải thuộc {VALID_STATUSES}")
            fields.append(f"{f} = ?")
            vals.append(v)
    if not fields:
        raise HTTPException(422, "No update fields")
    vals.append(repair_id)
    db.execute("UPDATE repairs SET " + ", ".join(fields) + " WHERE id = ?", vals)
    db.commit()
    return {"id": repair_id, "status": "updated"}

@router.get("/api/repairs/stats/today")
async def repairs_today(db = Depends(get_db)):
    """Thống kê sửa chữa hôm nay — dùng cho dashboard"""
    today = date.today().isoformat()
    tbl = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repairs'").fetchone()
    if not tbl:
        cnt = db.execute("SELECT COUNT(*) FROM maintenance_logs WHERE DATE(created_at) = ?", (today,)).fetchone()[0]
        return {"today": cnt, "table": "maintenance_logs (fallback)", "total": cnt}
    cnt = db.execute("SELECT COUNT(*) FROM repairs WHERE DATE(start_date) = ?", (today,)).fetchone()[0]
    return {"today": cnt, "table": "repairs", "total": cnt}