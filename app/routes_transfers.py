"""
T2.3 Transfers Upgrade API — workflow điều chuyển thiết bị.
PUT /api/transfers/{id}/confirm — xác nhận chuyển, cập nhật device.facility_id transaction-safe.
"""
from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models import DeviceTransferCreate

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
    
    rows = db.execute(q, params).fetchall()
    transfers_list = []
    for r in rows:
        item = dict(r)
        item["asset_tag"] = f"BVQ7-TTB-{item['device_id']:05d}"
        transfers_list.append(item)
    return transfers_list

@router.post("/api/transfers")
async def create_transfer(req: DeviceTransferCreate, db = Depends(get_db)):
    """Tạo biên bản điều chuyển thiết bị (QT.08) — Pydantic v2 validated"""
    dev_row = db.execute("SELECT id, facility_id FROM devices WHERE id = ?", (req.device_id,)).fetchone()
    if not dev_row:
        raise HTTPException(404, f"Thiết bị #{req.device_id} không tồn tại trên hệ thống")
    
    if not db.execute("SELECT id FROM facilities WHERE id = ?", (req.to_facility_id,)).fetchone():
        raise HTTPException(404, f"Khoa/Phòng nhận #{req.to_facility_id} không tồn tại")
    
    from_fac = req.from_facility_id or dev_row["facility_id"] or 1
    if req.from_facility_id and not db.execute("SELECT id FROM facilities WHERE id = ?", (req.from_facility_id,)).fetchone():
        raise HTTPException(404, f"Khoa/Phòng giao #{req.from_facility_id} không tồn tại")

    transfer_date = req.transfer_date or datetime.now().strftime('%Y-%m-%d')
    cur = db.execute("""INSERT INTO device_transfers 
        (device_id, to_facility_id, from_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, status, form_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)""",
        (req.device_id, req.to_facility_id, from_fac, req.giver_name or "", req.receiver_name or "", 
         req.transfer_reason or "", transfer_date, req.form_code or "BM08_TA5.TTBYT.QT.08"))
    db.commit()
    return {
        "id": cur.lastrowid,
        "status": "PENDING",
        "message": f"Đã tạo biên bản điều chuyển #{cur.lastrowid:04d} (Chờ xác nhận giao nhận)"
    }


@router.put("/api/transfers/{transfer_id}/confirm")
async def confirm_transfer(transfer_id: int, db = Depends(get_db)):
    """Xác nhận transfer — update device.facility_id transaction-safe with rollback"""
    row = db.execute("SELECT * FROM device_transfers WHERE id = ?", (transfer_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Transfer {transfer_id} không tồn tại")
    if row["status"] == "CONFIRMED":
        return {"id": transfer_id, "status": "already_confirmed"}
    
    try:
        with db:
            db.execute("UPDATE devices SET facility_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                       (row["to_facility_id"], row["device_id"]))
            db.execute("UPDATE device_transfers SET status = 'CONFIRMED' WHERE id = ?", (transfer_id,))
            
            # Ghi nhận notification audit
            db.execute("""
                INSERT INTO notifications (ref_type, ref_id, message, level, is_read)
                VALUES ('TRANSFER', ?, ?, 'INFO', 0)
            """, (transfer_id, f"Thiết bị #{row['device_id']} đã được bàn giao sang Khoa/Phòng ID #{row['to_facility_id']}"))
    except Exception as e:
        raise HTTPException(500, f"Lỗi giao dịch điều chuyển: {str(e)}")
        
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