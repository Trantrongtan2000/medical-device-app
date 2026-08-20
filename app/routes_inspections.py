"""
T2.1 Pre-use Inspections API — cho phép nhân viên ghi nhận kiểm tra trước khi dùng thiết bị.
Endpoint: POST /api/inspections — tạo bản ghi kiểm tra
"""
from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db

router = APIRouter()

def calc_overall(p: bool, ph: bool, g: bool, s: bool) -> str:
    return "PASSED" if all([p, ph, g, s]) else "FAILED"

@router.get("/api/devices/{device_id}/pre-use-inspection")
async def get_pre_use_inspection(device_id: int, db = Depends(get_db)):
    row = db.execute("SELECT * FROM pre_use_inspections WHERE device_id = ? ORDER BY inspection_time DESC LIMIT 1", (device_id,)).fetchone()
    if not row:
        return {"device_id": device_id, "has_inspection": False}
    return {"device_id": device_id, "has_inspection": True, "inspection": dict(row)}

@router.post("/api/inspections")
async def record_pre_use_inspection(body: Request, db = Depends(get_db)):
    """Fallback API cho form submit pre-use inspection — nhận raw JSON body"""
    try:
        data = await body.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
    
    device_id = data.get("device_id")
    if not device_id:
        raise HTTPException(422, "device_id required")
    
    overall = calc_overall(
        data.get("power_ok", True),
        data.get("physical_ok", True),
        data.get("gas_pressure_ok", True),
        data.get("selftest_ok", True)
    )
    
    cur = db.execute("""INSERT INTO pre_use_inspections
        (device_id, inspector_name, department, power_ok, physical_ok, gas_pressure_ok, selftest_ok, overall_status, notes, inspection_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (device_id, data.get("inspector_name", ""), data.get("department", ""),
         data.get("power_ok", True), data.get("physical_ok", True),
         data.get("gas_pressure_ok", True), data.get("selftest_ok", True),
         overall, data.get("notes", ""), datetime.now().isoformat()))
    db.commit()
    return {"id": cur.lastrowid, "overall_status": overall}

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

@router.get("/api/inspections")
async def list_all_pre_use_inspections(limit: int = 50, db = Depends(get_db)):
    rows = db.execute("SELECT * FROM pre_use_inspections ORDER BY inspection_time DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]