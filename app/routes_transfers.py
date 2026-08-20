"""
T2.3 Transfers Upgrade API — hoàn thiện workflow điều chuyển thiết bị.
Endpoint: PUT /api/transfers/{id}/confirm — xác nhận chuyển, cập nhật device.facility_id
Constraint: transaction-safe (device + transfer sync)
"""
from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from app.database import get_db

router = APIRouter()

class TransferCreate(BaseModel):
    device_id: int
    to_facility_id: int
    # Optional fields with explicit defaults for Pydantic v2 JSON null handling
    from_facility_id: int | None = Field(default=None, description="Nơi đến trước đây")
    giver_name: str = Field(default="", description="Người cung cấp")
    receiver_name: str = Field(default="", description="Người nhận")
    transfer_reason: str = Field(default="", description="Lý do chuyển")
    transfer_date: str | None = Field(default=None, description="Ngày chuyển")
    form_code: str | None = Field(default=None, description="Mã phiếu")

class Transfer(BaseModel):
    id: int
    device_id: int
    from_facility_id: int | None = None
    to_facility_id: int
    giver_name: str | None = None
    receiver_name: str | None = None
    transfer_reason: str | None = None
    transfer_date: str | None = None
    form_code: str | None = None
    status: str  # PENDING, CONFIRMED, COMPLETED, CANCELLED
    created_at: str | None = None
    device_name: str | None = None
    serial_no: str | None = None
    from_facility_name: str | None = None
    to_facility_name: str | None = None

VALID_STATUSES = ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED')

@router.get("/api/transfers")
async def list_transfers(status: str | None = None, device_id: int | None = None, limit: int = 100, db = Depends(get_db)):
    q = """SELECT t.*, d.device_name, d.serial_no, f1.name as from_facility_name, f2.name as to_facility_name
           FROM device_transfers t
           JOIN devices d ON d.id = t.device_id
           LEFT JOIN facilities f1 ON f1.id = t.from_facility_id
           LEFT JOIN facilities f2 ON f2.id = t.to_facility_id
           WHERE 1=1"""
    params = []
    if status:
        q += " AND t.status = ?"; params.append(status)
    if device_id:
        q += " AND t.device_id = ?"; params.append(device_id)
    q += " ORDER BY t.created_at DESC LIMIT ?"; params.append(limit)
    rows = db.execute(q, params).fetchall()
    return [dict(r) for r in rows]

@router.get("/api/transfers/{transfer_id}")
async def get_transfer(transfer_id: int, db = Depends(get_db)):
    row = db.execute("""SELECT t.*, d.device_name, d.serial_no, f1.name as from_facility_name, f2.name as to_facility_name
                        FROM device_transfers t
                        JOIN devices d ON d.id = t.device_id
                        LEFT JOIN facilities f1 ON f1.id = t.from_facility_id
                        LEFT JOIN facilities f2 ON f2.id = t.to_facility_id
                        WHERE t.id = ?""", (transfer_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Transfer {transfer_id} not found")
    return dict(row)

@router.post("/api/transfers")
async def create_transfer(req: TransferCreate, db = Depends(get_db)):
    dev = db.execute("SELECT id FROM devices WHERE id = ?", (req.device_id,)).fetchone()
    if not dev:
        raise HTTPException(404, f"Device {req.device_id} not found")
    to_fac = db.execute("SELECT id FROM facilities WHERE id = ?", (req.to_facility_id,)).fetchone()
    if not to_fac:
        raise HTTPException(404, f"Facility {req.to_facility_id} not found")
    now = datetime.now().strftime('%Y-%m-%d')
    cur = db.execute("""INSERT INTO device_transfers 
        (device_id, to_facility_id, from_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, status, form_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)""",
        (req.device_id, req.to_facility_id, req.from_facility_id, req.giver_name, req.receiver_name, 
         req.transfer_reason, req.transfer_date or now, req.form_code))
    db.commit()
    return {"id": cur.lastrowid, "status": "created", "message": "Transfer đã tạo, chờ xác nhận"}

@router.put("/api/transfers/{transfer_id}/confirm")
async def confirm_transfer(transfer_id: int, db = Depends(get_db)):
    """Xác nhận transfer — cập nhật device.facility_id transaction-safe"""
    row = db.execute("SELECT * FROM device_transfers WHERE id = ?", (transfer_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Transfer {transfer_id} not found")
    if row["status"] == "CONFIRMED":
        return {"id": transfer_id, "status": "already_confirmed"}
    try:
        db.execute("BEGIN")
        db.execute("UPDATE devices SET facility_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                   (row["to_facility_id"], row["device_id"]))
        db.execute("UPDATE device_transfers SET status = 'CONFIRMED' WHERE id = ?", (transfer_id,))
        db.commit()
        return {"id": transfer_id, "status": "CONFIRMED", "device_facility_id": row["to_facility_id"]}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Transaction rollback: {e}")

@router.delete("/api/transfers/{transfer_id}")
async def cancel_transfer(transfer_id: int, db = Depends(get_db)):
    row = db.execute("SELECT id, status FROM device_transfers WHERE id = ?", (transfer_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Transfer {transfer_id} not found")
    if row["status"] == "CONFIRMED":
        raise HTTPException(400, "Không thể hủy transfer đã xác nhận")
    db.execute("DELETE FROM device_transfers WHERE id = ?", (transfer_id,))
    db.commit()
    return {"id": transfer_id, "status": "cancelled"}

@router.get("/api/devices/{device_id}/transfers/history")
async def device_transfer_history(device_id: int, db = Depends(get_db)):
    rows = db.execute("""SELECT t.*, f.name as facility_name
                         FROM device_transfers t
                         LEFT JOIN facilities f ON f.id = t.to_facility_id
                         WHERE t.device_id = ?
                         ORDER BY t.created_at DESC""", (device_id,)).fetchall()
    return [dict(r) for r in rows]