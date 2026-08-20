"""
T2.3 Transfers Upgrade API — workflow điều chuyển thiết bị.
PUT /api/transfers/{id}/confirm — xác nhận chuyển, cập nhật device.facility_id transaction-safe.
"""
from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from app.database import get_db

router = APIRouter()

@router.get("/api/transfers")
async def list_transfers(status: str | None = None, device_id: int | None = None, limit: int = 100, db = Depends(get_db)):
    q = """SELECT t.*, d.device_name, d.serial_no, f1.name as from_facility_name, f2.name as to_facility_name
           FROM device_transfers t JOIN devices d ON d.id = t.device_id
           LEFT JOIN facilities f1 ON f1.id = t.from_facility_id
           LEFT JOIN facilities f2 ON f2.id = t.to_facility_id
           WHERE 1=1"""
    params = []
    if status:
        q += " AND t.status = ?"; params.append(status)
    if device_id:
        q += " AND t.device_id = ?"; params.append(device_id)
    q += " ORDER BY t.created_at DESC LIMIT ?"; params.append(limit)
    return [dict(r) for r in db.execute(q, params).fetchall()]

@router.post("/api/transfers")
async def create_transfer(request: Request, db = Depends(get_db)):
    """Tạo transfer — raw JSON body cho Pydantic v2 null handling"""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON body")
    
    device_id = body.get("device_id")
    to_facility_id = body.get("to_facility_id")
    giver_name = body.get("giver_name", "")
    receiver_name = body.get("receiver_name", "")
    transfer_reason = body.get("transfer_reason", "")
    from_facility_id = body.get("from_facility_id")
    transfer_date = body.get("transfer_date")
    form_code = body.get("form_code")
    
    if not device_id or not to_facility_id:
        raise HTTPException(422, "device_id và to_facility_id bắt buộc")
    
    if not db.execute("SELECT id FROM devices WHERE id = ?", (device_id,)).fetchone():
        raise HTTPException(404, f"Device {device_id} không tồn tại")
    
    if not db.execute("SELECT id FROM facilities WHERE id = ?", (to_facility_id,)).fetchone():
        raise HTTPException(404, f"Facility {to_facility_id} không tồn tại")
    
    cur = db.execute("""INSERT INTO device_transfers 
        (device_id, to_facility_id, from_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, status, form_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)""",
        (device_id, to_facility_id, from_facility_id, giver_name, receiver_name, 
         transfer_reason, transfer_date or datetime.now().strftime('%Y-%m-%d'), form_code))
    db.commit()
    return {"id": cur.lastrowid, "status": "created"}

@router.put("/api/transfers/{transfer_id}/confirm")
async def confirm_transfer(transfer_id: int, db = Depends(get_db)):
    """Xác nhận transfer — update device.facility_id transaction-safe"""
    row = db.execute("SELECT * FROM device_transfers WHERE id = ?", (transfer_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Transfer {transfer_id} không tồn tại")
    if row["status"] == "CONFIRMED":
        return {"id": transfer_id, "status": "already_confirmed"}
    
    db.execute("BEGIN")
    db.execute("UPDATE devices SET facility_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
               (row["to_facility_id"], row["device_id"]))
    db.execute("UPDATE device_transfers SET status = 'CONFIRMED' WHERE id = ?", (transfer_id,))
    db.commit()
    return {"id": transfer_id, "status": "CONFIRMED"}

@router.delete("/api/transfers/{transfer_id}")
async def cancel_transfer(transfer_id: int, db = Depends(get_db)):
    row = db.execute("SELECT id, status FROM device_transfers WHERE id = ?", (transfer_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Transfer không tồn tại")
    if row["status"] == "CONFIRMED":
        raise HTTPException(400, "Không thể hủy transfer đã xác nhận")
    db.execute("DELETE FROM device_transfers WHERE id = ?", (transfer_id,))
    db.commit()
    return {"id": transfer_id, "status": "cancelled"}

@router.get("/api/devices/{device_id}/transfers/history")
async def device_transfer_history(device_id: int, db = Depends(get_db)):
    rows = db.execute("""SELECT t.*, f.name as facility_name
                         FROM device_transfers t LEFT JOIN facilities f ON f.id = t.to_facility_id
                         WHERE t.device_id = ? ORDER BY t.created_at DESC""", (device_id,)).fetchall()
    return [dict(r) for r in rows]