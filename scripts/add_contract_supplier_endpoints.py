import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
routes_path = app_dir / "app" / "routes.py"

with open(routes_path, "r", encoding="utf-8") as f:
    routes_code = f.read()

# Add Contract Models and Routes to routes.py
contract_supplier_routes = """
# ==================== CONTRACTS & PROCUREMENT MANAGEMENT ====================

class ContractCreate(BaseModel):
    contract_no: str
    contract_name: str
    supplier_name: Optional[str] = None
    handover_date: Optional[str] = None
    contract_value: Optional[float] = 0
    warranty_period_months: Optional[int] = 12
    status: Optional[str] = "ACTIVE"
    notes: Optional[str] = None

class ContractUpdate(BaseModel):
    contract_no: Optional[str] = None
    contract_name: Optional[str] = None
    supplier_name: Optional[str] = None
    handover_date: Optional[str] = None
    contract_value: Optional[float] = None
    warranty_period_months: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class SupplierContactCreate(BaseModel):
    supplier_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    service_scope: Optional[str] = None

@router.get("/api/contracts")
async def list_contracts(search: Optional[str] = Query(None), db = Depends(get_db)):
    \"\"\"Danh sách đầy đủ tất cả Hợp đồng mua sắm & Gói thầu TTBYT kèm số lượng thiết bị\"\"\"
    query = \"\"\"
        SELECT c.*,
               COUNT(d.id) as device_count,
               GROUP_CONCAT(DISTINCT d.device_name) as sample_device_names
        FROM contracts c
        LEFT JOIN devices d ON d.contract_no = c.contract_no
    \"\"\"
    params = []
    if search and search.strip():
        s = f"%{search.strip()}%"
        query += " WHERE c.contract_no LIKE ? OR c.contract_name LIKE ? OR c.supplier_name LIKE ?"
        params.extend([s, s, s])
    query += " GROUP BY c.id ORDER BY c.id ASC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]

@router.post("/api/contracts")
async def create_contract(req: ContractCreate, db = Depends(get_db)):
    \"\"\"Tạo mới Hợp đồng mua sắm / Gói thầu TTBYT\"\"\"
    try:
        cur = db.execute(\"\"\"
            INSERT INTO contracts (contract_no, contract_name, supplier_name, handover_date, contract_value, warranty_period_months, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (req.contract_no, req.contract_name, req.supplier_name, req.handover_date, req.contract_value, req.warranty_period_months, req.status, req.notes))
        db.commit()
        return {"status": "success", "id": cur.lastrowid, "message": f"Đã tạo thành công hợp đồng {req.contract_no}!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Số hợp đồng '{req.contract_no}' đã tồn tại!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/contracts/{contract_id}")
async def update_contract(contract_id: int, req: ContractUpdate, db = Depends(get_db)):
    \"\"\"Chỉnh sửa thông tin Hợp đồng mua sắm TTBYT\"\"\"
    row = db.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy hợp đồng")

    old_contract_no = row["contract_no"]
    fields = []
    params = []
    if req.contract_no is not None:
        fields.append("contract_no = ?")
        params.append(req.contract_no)
    if req.contract_name is not None:
        fields.append("contract_name = ?")
        params.append(req.contract_name)
    if req.supplier_name is not None:
        fields.append("supplier_name = ?")
        params.append(req.supplier_name)
    if req.handover_date is not None:
        fields.append("handover_date = ?")
        params.append(req.handover_date)
    if req.contract_value is not None:
        fields.append("contract_value = ?")
        params.append(req.contract_value)
    if req.warranty_period_months is not None:
        fields.append("warranty_period_months = ?")
        params.append(req.warranty_period_months)
    if req.status is not None:
        fields.append("status = ?")
        params.append(req.status)
    if req.notes is not None:
        fields.append("notes = ?")
        params.append(req.notes)

    if fields:
        params.append(contract_id)
        db.execute(f"UPDATE contracts SET {', '.join(fields)} WHERE id = ?", params)
        # Update devices if contract_no changed
        if req.contract_no and req.contract_no != old_contract_no:
            db.execute("UPDATE devices SET contract_no = ? WHERE contract_no = ?", (req.contract_no, old_contract_no))
        db.commit()

    return {"status": "success", "message": "Đã cập nhật thông tin hợp đồng thành công!"}

@router.delete("/api/contracts/{contract_id}")
async def delete_contract(contract_id: int, db = Depends(get_db)):
    \"\"\"Xóa hợp đồng mua sắm\"\"\"
    row = db.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy hợp đồng")
    
    db.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
    db.commit()
    return {"status": "success", "message": "Đã xóa hợp đồng thành công!"}

@router.get("/api/contracts/{contract_id}/devices")
async def get_contract_devices(contract_id: int, db = Depends(get_db)):
    \"\"\"Lấy danh sách các thiết bị thuộc một Hợp đồng mua sắm\"\"\"
    row = db.execute("SELECT contract_no, contract_name FROM contracts WHERE id = ?", (contract_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy hợp đồng")
    
    devs = db.execute(\"\"\"
        SELECT d.id, d.device_name, d.model, d.serial_no, d.risk_level, d.status,
               f.name as facility_name
        FROM devices d
        LEFT JOIN facilities f ON d.facility_id = f.id
        WHERE d.contract_no = ?
        ORDER BY d.id ASC
    \"\"\", (row["contract_no"],)).fetchall()
    
    return {
        "contract": dict(row),
        "total_devices": len(devs),
        "devices": [dict(d) for d in devs]
    }

@router.post("/api/directory/suppliers")
async def create_supplier_contact(req: SupplierContactCreate, db = Depends(get_db)):
    \"\"\"Thêm mới Nhà Cung Cấp / Đại Diện Hãng Kỹ Thuật\"\"\"
    cur = db.execute(\"\"\"
        INSERT INTO supplier_contacts (supplier_name, contact_person, phone, email, service_scope)
        VALUES (?, ?, ?, ?, ?)
    \"\"\", (req.supplier_name, req.contact_person, req.phone, req.email, req.service_scope))
    db.commit()
    return {"status": "success", "id": cur.lastrowid, "message": f"Đã thêm nhà cung cấp {req.supplier_name}!"}

@router.delete("/api/directory/suppliers/{sup_id}")
async def delete_supplier_contact(sup_id: int, db = Depends(get_db)):
    \"\"\"Xóa nhà cung cấp khỏi danh bạ\"\"\"
    db.execute("DELETE FROM supplier_contacts WHERE id = ?", (sup_id,))
    db.commit()
    return {"status": "success", "message": "Đã xóa nhà cung cấp thành công!"}

@router.get("/api/directory/suppliers/{sup_id}/devices")
async def get_supplier_devices(sup_id: int, db = Depends(get_db)):
    \"\"\"Lấy danh sách thiết bị do một Nhà Cung Cấp phụ trách/cung cấp\"\"\"
    row = db.execute("SELECT * FROM supplier_contacts WHERE id = ?", (sup_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")
    
    sup_name = row["supplier_name"]
    devs = db.execute(\"\"\"
        SELECT d.id, d.device_name, d.model, d.serial_no, d.risk_level, d.status,
               f.name as facility_name, d.contract_no
        FROM devices d
        LEFT JOIN facilities f ON d.facility_id = f.id
        WHERE d.supplier_name LIKE ? OR d.manufacturer LIKE ?
        ORDER BY d.id ASC
    \"\"\", (f"%{sup_name[:15]}%", f"%{sup_name[:15]}%")).fetchall()
    
    return {
        "supplier": dict(row),
        "total_devices": len(devs),
        "devices": [dict(d) for d in devs]
    }
"""

if "/api/contracts" not in routes_code:
    routes_code += "\n\n" + contract_supplier_routes
    with open(routes_path, "w", encoding="utf-8") as f:
        f.write(routes_code)
    print("✅ Đã thêm toàn bộ CRUD API cho Contracts và Suppliers vào `app/routes.py`!")
