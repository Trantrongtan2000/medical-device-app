"""
T2.1 Pre-use Inspections API — cho phép nhân viên ghi nhận kiểm tra trước khi dùng thiết bị.
Endpoint: /api/inspections/pre-use/{device_id} GET/POST PUT
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db

router = APIRouter()

class PreUseInspectionCreate(BaseModel):
    device_id: int
    inspector_name: str
    department: Optional[str] = None
    power_ok: bool = True
    physical_ok: bool = True
    gas_pressure_ok: bool = True
    selftest_ok: bool = True
    notes: Optional[str] = None

class PreUseInspectionUpdate(BaseModel):
    inspector_name: Optional[str] = None
    department: Optional[str] = None
    power_ok: Optional[bool] = None
    physical_ok: Optional[bool] = None
    gas_pressure_ok: Optional[bool] = None
    selftest_ok: Optional[bool] = None
    notes: Optional[str] = None

class PreUseInspection(BaseModel):
    id: int
    device_id: int
    inspector_name: str
    department: Optional[str] = None
    power_ok: bool
    physical_ok: bool
    gas_pressure_ok: bool
    selftest_ok: bool
    overall_status: str
    notes: Optional[str] = None
    inspection_time: Optional[str] = None

    class Config:
        from_attributes = True

def calc_overall(p: bool, ph: bool, g: bool, s: bool) -> str:
    return "PASSED" if all([p, ph, g, s]) else "FAILED"

@router.get("/api/devices/{device_id}/pre-use-inspection")
async def get_pre_use_inspection(device_id: int, db = Depends(get_db)):
    row = db.execute("SELECT * FROM pre_use_inspections WHERE device_id = ? ORDER BY inspection_time DESC LIMIT 1", (device_id,)).fetchone()
    if not row:
        return {"device_id": device_id, "has_inspection": False}
    return {"device_id": device_id, "has_inspection": True, "inspection": dict(row)}

@router.post("/api/devices/{device_id}/pre-use-inspection")
async def create_pre_use_inspection(device_id: int, req: PreUseInspectionCreate, db = Depends(get_db)):
    dev = db.execute("SELECT id FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not dev:
        raise HTTPException(404, f"Device {device_id} not found")
    overall = calc_overall(req.power_ok, req.physical_ok, req.gas_pressure_ok, req.selftest_ok)
    cur = db.execute("""INSERT INTO pre_use_inspections
        (device_id, inspector_name, department, power_ok, physical_ok, gas_pressure_ok, selftest_ok, overall_status, notes, inspection_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (device_id, req.inspector_name, req.department, req.power_ok, req.physical_ok, req.gas_pressure_ok, req.selftest_ok, overall, req.notes, datetime.now().isoformat()))
    db.commit()
    return {"id": cur.lastrowid, "overall_status": overall}

@router.put("/api/devices/{device_id}/pre-use-inspection/{inspection_id}")
async def update_pre_use_inspection(device_id: int, inspection_id: int, req: PreUseInspectionUpdate, db = Depends(get_db)):
    row = db.execute("SELECT * FROM pre_use_inspections WHERE id = ? AND device_id = ?", (inspection_id, device_id)).fetchone()
    if not row:
        raise HTTPException(404, "Inspection not found")
    p = req.power_ok if req.power_ok is not None else row["power_ok"]
    ph = req.physical_ok if req.physical_ok is not None else row["physical_ok"]
    g = req.gas_pressure_ok if req.gas_pressure_ok is not None else row["gas_pressure_ok"]
    s = req.selftest_ok if req.selftest_ok is not None else row["selftest_ok"]
    overall = calc_overall(p, ph, g, s)
    now = datetime.now().isoformat()
    fields, vals = [], []
    for f in ("inspector_name", "department", "power_ok", "physical_ok", "gas_pressure_ok", "selftest_ok", "notes"):
        v = getattr(req, f, None)
        if v is not None:
            fields.append(f"{f} = ?")
            vals.append(1 if isinstance(v, bool) else v)
    vals.extend([overall, now, inspection_id])
    if not fields:
        raise HTTPException(422, "No update fields")
    sql = "UPDATE pre_use_inspections SET " + ", ".join(fields) + ", overall_status = ?, inspection_time = ? WHERE id = ?"
    db.execute(sql, vals)
    db.commit()
    return {"id": inspection_id, "overall_status": overall}

@router.get("/api/inspections/pre-use")
async def list_pre_use_inspections(device_id: Optional[int] = None, status: Optional[str] = None, limit: int = 100, db = Depends(get_db)):
    q = "SELECT pi.*, d.device_name, d.serial_no FROM pre_use_inspections pi JOIN devices d ON d.id = pi.device_id WHERE 1=1"
    params = []
    if device_id:
        q += " AND pi.device_id = ?"; params.append(device_id)
    if status:
        q += " AND pi.overall_status = ?"; params.append(status)
    q += " ORDER BY pi.inspection_time DESC LIMIT ?"; params.append(limit)
    return [dict(r) for r in db.execute(q, params).fetchall()]