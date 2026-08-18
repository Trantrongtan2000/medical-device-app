"""
API Routes cho Medical Device Management System (BV Quận 7)
Tích hợp toàn diện chuẩn SpeedMaint Cloud CMMS (Bệnh viện Hoàn Mỹ) & Snipe-IT
"""
import io
import csv
from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel

from .database import get_db
from .models import (
    Device, DeviceCreate, DeviceUpdate,
    CalibrationCertificate, CalibrationCertificateCreate,
    DeviceSummary, DeviceStatus
)

router = APIRouter()

PDF_ROOT_DIRS = [
    Path(r"G:\BV QUẬN 7_OCR_WORK_20260712"),
    Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818"),
    Path(r"C:\Users\tantt\Downloads\asset-management-tools\36. TRANG THIẾT BỊ Y TẾ")
]


# ==================== DEVICE ENDPOINTS (SNIPE-IT ASSET API) ====================

@router.get("/api/devices")
async def get_devices(
    facility_id: Optional[int] = Query(None, description="Lọc theo khoa"),
    category_id: Optional[int] = Query(None, description="Lọc theo loại thiết bị"),
    alert_status: Optional[str] = Query(None, description="Lọc trạng thái cảnh báo (OVERDUE, WARNING, OK, NO_DATA)"),
    status: Optional[str] = Query(None, description="Lọc trạng thái hoạt động"),
    risk_level: Optional[str] = Query(None, description="Lọc mức độ rủi ro (A, B, C, D)"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên, model, serial, hãng sản xuất"),
    limit: int = Query(300, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db = Depends(get_db)
):
    """Liệt kê danh sách tài sản TTBYT với mã Asset Tag chuẩn Snipe-IT & SpeedMaint"""
    query = "SELECT * FROM device_status_summary"
    conditions = []
    params = []
    
    if facility_id:
        conditions.append("facility_id = ?")
        params.append(facility_id)
        
    if category_id:
        conditions.append("category_id = ?")
        params.append(category_id)
        
    if alert_status:
        conditions.append("alert_status = ?")
        params.append(alert_status.upper())
        
    if status:
        conditions.append("status = ?")
        params.append(status.upper())

    if risk_level:
        conditions.append("risk_level = ?")
        params.append(risk_level.upper())
    
    if search and search.strip():
        s = f"%{search.strip()}%"
        conditions.append("(device_name LIKE ? OR model LIKE ? OR serial_no LIKE ? OR manufacturer LIKE ?)")
        params.extend([s, s, s, s])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY CASE alert_status WHEN 'OVERDUE' THEN 1 WHEN 'WARNING' THEN 2 WHEN 'OK' THEN 3 ELSE 4 END, device_name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    result = db.execute(query, params).fetchall()
    
    devices_list = []
    for row in result:
        d = dict(row)
        d["asset_tag"] = f"BVQ7-TTB-{d['id']:05d}"
        d["speedmaint_code"] = f"BM/BVQ7/{d['id']:05d}"
        devices_list.append(d)
        
    return devices_list


@router.get("/api/devices/{device_id}")
async def get_device(device_id: int, db = Depends(get_db)):
    """Chi tiết hồ sơ lý lịch tài sản (Snipe-IT Asset Dossier & SpeedMaint CMMS)"""
    query = """
        SELECT d.*, f.name as facility, c.name as category
        FROM devices d
        LEFT JOIN facilities f ON d.facility_id = f.id
        LEFT JOIN device_categories c ON d.category_id = c.id
        WHERE d.id = ?
    """
    row = db.execute(query, (device_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")
    
    device_data = dict(row)
    device_data["asset_tag"] = f"BVQ7-TTB-{device_data['id']:05d}"
    device_data["speedmaint_code"] = f"BM/BVQ7/{device_data['id']:05d}"
    
    # Lịch sử kiểm định (Certificates)
    certs_query = """
        SELECT * FROM calibration_certificates
        WHERE device_id = ?
        ORDER BY calibration_date DESC
    """
    certs = db.execute(certs_query, (device_id,)).fetchall()
    device_data["certificates"] = [dict(c) for c in certs]
    
    # Nhật ký bàn giao, bảo trì & Audit Trail (SpeedMaint Work Orders)
    logs_query = """
        SELECT * FROM maintenance_logs
        WHERE device_id = ?
        ORDER BY maintenance_date DESC, id DESC
    """
    logs = db.execute(logs_query, (device_id,)).fetchall()
    device_data["maintenance_logs"] = [dict(l) for l in logs]
    
    return device_data


# ==================== SPEEDMAINT WORK ORDERS & TASKS (CHUẨN HOÀN MỸ SPEEDMAINT) ====================

class SpeedMaintWorkOrderCreate(BaseModel):
    device_id: int
    title: str
    work_type: str = "PM định kỳ"  # PM định kỳ, Sửa chữa, Điều chuyển, Kiểm định, Khác
    start_date: str
    end_date: str
    assigned_to: str
    co_workers: Optional[str] = None
    supervisor: Optional[str] = None
    reporter: str
    priority: str = "Trung bình"  # Khẩn cấp, Cao, Trung bình, Thấp
    progress: int = 100
    is_unplanned: bool = False
    location: Optional[str] = None
    description: str
    materials: Optional[str] = None

@router.get("/api/work-orders")
async def list_work_orders(db = Depends(get_db)):
    """Danh sách phiếu công việc chuẩn SpeedMaint CMMS"""
    query = """
        SELECT l.id, l.device_id, l.maintenance_date as start_date, l.performed_by as assigned_to, 
               l.maintenance_type as work_type, l.description, d.device_name, d.serial_no, d.model, 
               f.name as facility
        FROM maintenance_logs l
        JOIN devices d ON l.device_id = d.id
        LEFT JOIN facilities f ON d.facility_id = f.id
        WHERE l.maintenance_type != 'INSPECTION'
        ORDER BY l.maintenance_date DESC, l.id DESC
    """
    rows = db.execute(query).fetchall()
    
    work_orders = []
    for r in rows:
        item = dict(r)
        item["task_code"] = f"260{item['id']:03d}"
        item["speedmaint_device_code"] = f"BM/BVQ7/{item['device_id']:05d}"
        item["progress"] = 100
        item["status"] = "Hoàn thành"
        work_orders.append(item)
        
    return work_orders

@router.post("/api/work-orders")
async def create_work_order(ticket: SpeedMaintWorkOrderCreate, db = Depends(get_db)):
    """Tạo phiếu công việc chi tiết chuẩn SpeedMaint Cloud CMMS (Ảnh 01bc & 605c)"""
    cur = db.cursor()
    full_desc = f"[{ticket.work_type}] {ticket.title}. {ticket.description}"
    if ticket.materials:
        full_desc += f" (Vật tư: {ticket.materials})"
    if ticket.location:
        full_desc += f" (Địa điểm: {ticket.location})"
        
    cur.execute("""
        INSERT INTO maintenance_logs (device_id, maintenance_date, performed_by, maintenance_type, description)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket.device_id, ticket.start_date, ticket.assigned_to, ticket.work_type, full_desc))
    
    if ticket.priority in ("Khẩn cấp", "Cao"):
        cur.execute("UPDATE devices SET status = 'REPAIR' WHERE id = ?", (ticket.device_id,))
        
    db.commit()
    return {"status": "success", "message": "Đã tạo phiếu công việc SpeedMaint thành công!"}


# ==================== DEDICATED AUDIT MODULE (TRUNG TÂM KIỂM KÊ) ====================

class AuditConfirmRequest(BaseModel):
    device_id: int
    audited_by: str
    location_checked: Optional[str] = None
    condition: Optional[str] = "GOOD"
    notes: Optional[str] = "Đã kiểm kê hiện diện thực tế tại khoa phòng"

@router.get("/api/audits")
async def list_audits(db = Depends(get_db)):
    """Danh sách các lượt kiểm kê tài sản (Snipe-IT Physical Asset Audits)"""
    query = """
        SELECT l.id, l.device_id, l.maintenance_date as audit_date, l.performed_by as auditor,
               l.description, d.device_name, d.serial_no, d.model, f.name as facility
        FROM maintenance_logs l
        JOIN devices d ON l.device_id = d.id
        LEFT JOIN facilities f ON d.facility_id = f.id
        WHERE l.maintenance_type = 'INSPECTION' OR l.description LIKE '%KIỂM KÊ%'
        ORDER BY l.maintenance_date DESC, l.id DESC
    """
    rows = db.execute(query).fetchall()
    
    audits_list = []
    for r in rows:
        item = dict(r)
        item["asset_tag"] = f"BVQ7-TTB-{item['device_id']:05d}"
        audits_list.append(item)
        
    return audits_list

@router.post("/api/devices/audit")
async def audit_device(req: AuditConfirmRequest, db = Depends(get_db)):
    """Xác nhận kiểm kê tài sản thực tế"""
    today_str = date.today().isoformat()
    cur = db.cursor()
    desc = f"[KIỂM KÊ HIỆN TRƯỜNG] Tình trạng: {req.condition}. {req.notes}"
    if req.location_checked:
        desc += f" (Tại: {req.location_checked})"
        
    cur.execute("""
        INSERT INTO maintenance_logs (device_id, maintenance_date, performed_by, maintenance_type, description)
        VALUES (?, ?, ?, 'INSPECTION', ?)
    """, (req.device_id, today_str, req.audited_by, desc))
    
    db.commit()
    return {"status": "success", "message": "Đã ghi nhận kết quả kiểm kê tài sản thành công!"}


# ==================== CHECK-IN / CHECK-OUT ====================

class DeviceTransferRequest(BaseModel):
    device_id: int
    to_facility_id: int
    transferred_by: str
    reason: str

@router.post("/api/devices/transfer")
async def transfer_device(req: DeviceTransferRequest, db = Depends(get_db)):
    """Check-out / Bàn giao thiết bị sang khoa khác"""
    cur = db.cursor()
    
    old_fac = db.execute("""
        SELECT f.name FROM devices d
        LEFT JOIN facilities f ON d.facility_id = f.id
        WHERE d.id = ?
    """, (req.device_id,)).fetchone()
    old_fac_name = old_fac[0] if old_fac and old_fac[0] else "Kho lưu trữ"
    
    new_fac = db.execute("SELECT name FROM facilities WHERE id = ?", (req.to_facility_id,)).fetchone()
    if not new_fac:
        raise HTTPException(status_code=400, detail="Khoa phòng đích không tồn tại")
    new_fac_name = new_fac[0]
    
    cur.execute("UPDATE devices SET facility_id = ?, status = 'IN_SERVICE' WHERE id = ?", (req.to_facility_id, req.device_id))
    
    today_str = date.today().isoformat()
    desc = f"Bàn giao / Check-out từ [{old_fac_name}] -> [{new_fac_name}]. Lý do: {req.reason}"
    cur.execute("""
        INSERT INTO maintenance_logs (device_id, maintenance_date, performed_by, maintenance_type, description)
        VALUES (?, ?, ?, 'HANDOVER', ?)
    """, (req.device_id, today_str, req.transferred_by, desc))
    
    db.commit()
    return {
        "status": "success",
        "message": f"Đã bàn giao tài sản thành công sang {new_fac_name}!"
    }


# ==================== DASHBOARD KPI & SPEEDMAINT METRICS ====================

@router.get("/api/dashboard/summary")
async def get_dashboard_summary(db = Depends(get_db)):
    """Thống kê tổng quan KPI trang thiết bị y tế (SpeedMaint & Snipe-IT Dashboard)"""
    total = db.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    
    overdue = db.execute("""
        SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'OVERDUE'
    """).fetchone()[0]
    
    warning = db.execute("""
        SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'WARNING'
    """).fetchone()[0]
    
    ok = db.execute("""
        SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'OK'
    """).fetchone()[0]
    
    in_service = db.execute("""
        SELECT COUNT(*) FROM devices WHERE status = 'IN_SERVICE'
    """).fetchone()[0]
    
    repair = db.execute("""
        SELECT COUNT(*) FROM devices WHERE status = 'REPAIR'
    """).fetchone()[0]
    
    audited = db.execute("""
        SELECT COUNT(DISTINCT device_id) FROM maintenance_logs 
        WHERE maintenance_type = 'INSPECTION' OR description LIKE '%KIỂM KÊ%'
    """).fetchone()[0]
    
    avail_rate = round((in_service / total * 100), 1) if total > 0 else 100.0
    
    return {
        "total_devices": total,
        "overdue_count": overdue,
        "warning_count": warning,
        "ok_count": ok,
        "in_service_count": in_service,
        "repair_count": repair,
        "audited_count": audited,
        "availability_rate": avail_rate,
        "compliance_rate": round(((ok) / (ok + overdue + warning) * 100), 1) if (ok + overdue + warning) > 0 else 100.0
    }


@router.get("/api/dashboard/facilities")
async def get_facilities(db = Depends(get_db)):
    """Danh sách khoa/phòng ban và số lượng thiết bị"""
    query = """
        SELECT f.id, f.name, f.code, COUNT(d.id) as device_count
        FROM facilities f
        LEFT JOIN devices d ON f.id = d.facility_id
        GROUP BY f.id, f.name, f.code
        ORDER BY device_count DESC, f.name
    """
    result = db.execute(query).fetchall()
    return [dict(row) for row in result]


@router.get("/api/dashboard/categories")
async def get_categories(db = Depends(get_db)):
    """Danh sách loại thiết bị"""
    query = """
        SELECT c.id, c.name, c.description, c.safety_level, COUNT(d.id) as device_count
        FROM device_categories c
        LEFT JOIN devices d ON c.id = d.category_id
        GROUP BY c.id, c.name, c.description, c.safety_level
        ORDER BY c.name
    """
    result = db.execute(query).fetchall()
    return [dict(row) for row in result]


# ==================== ACCESSORIES & COMPONENTS ====================

@router.get("/api/accessories")
async def get_accessories():
    """Danh mục phụ tùng, linh kiện & phụ kiện đi kèm thiết bị y tế"""
    accessories_data = [
        {"id": 1, "name": "Bao đo huyết áp người lớn (Cuff Adult)", "category": "Vật tư Huyết áp", "model_no": "CUFF-AD-01", "location": "Kho VTYT", "total_qty": 150, "in_use_qty": 85, "unit_cost": "180.000 VNĐ"},
        {"id": 2, "name": "Cảm biến SpO2 dùng nhiều lần (SpO2 Reusable Sensor)", "category": "Cảm biến Monitor", "model_no": "SPO2-AD-Nellcor", "location": "Khoa Cấp Cứu", "total_qty": 60, "in_use_qty": 42, "unit_cost": "1.250.000 VNĐ"},
        {"id": 3, "name": "Dây cáp điện tim 5 chuyển đạo (ECG 5-Lead Cable)", "category": "Cáp tín hiệu", "model_no": "ECG-5L-TP", "location": "Khoa GMHS", "total_qty": 45, "in_use_qty": 30, "unit_cost": "950.000 VNĐ"},
        {"id": 4, "name": "Bộ dây thở silicon tiệt trùng dùng cho máy thở (Adult Breathing Circuit)", "category": "Phụ kiện Máy thở", "model_no": "BC-SIL-AD", "location": "Khoa Hồi Sức Tích Cực", "total_qty": 35, "in_use_qty": 20, "unit_cost": "2.400.000 VNĐ"},
        {"id": 5, "name": "Đầu dò siêu âm Convex (Convex Ultrasound Probe 3.5MHz)", "category": "Đầu dò Chẩn đoán", "model_no": "C35-PV", "location": "Khoa CĐHA", "total_qty": 8, "in_use_qty": 6, "unit_cost": "45.000.000 VNĐ"},
        {"id": 6, "name": "Bình tạo ẩm khí thở có gia nhiệt (Humidifier Chamber)", "category": "Phụ kiện Hỗ trợ thở", "model_no": "MR-850", "location": "Khoa Cấp Cứu", "total_qty": 25, "in_use_qty": 15, "unit_cost": "3.800.000 VNĐ"},
        {"id": 7, "name": "Điện cực bản dao mổ điện kèm cáp (Monopolar Grounding Plate)", "category": "Phụ kiện Phẫu thuật", "model_no": "ESU-PLT-02", "location": "Phòng Mổ", "total_qty": 80, "in_use_qty": 50, "unit_cost": "350.000 VNĐ"}
    ]
    return accessories_data


# ==================== CALENDAR & SCHEDULES ====================

@router.get("/api/schedules")
async def get_schedules(db = Depends(get_db)):
    """Lịch kiểm định và bảo dưỡng thiết bị y tế (PM Calendar)"""
    query = """
        SELECT d.id as device_id, d.device_name, d.serial_no, d.model, f.name as facility,
               c.recalibration_date as due_date, c.certificate_no, 'CALIBRATION' as schedule_type,
               s.alert_status
        FROM devices d
        JOIN calibration_certificates c ON d.id = c.device_id
        JOIN device_status_summary s ON d.id = s.id
        LEFT JOIN facilities f ON d.facility_id = f.id
        WHERE c.recalibration_date IS NOT NULL
        ORDER BY c.recalibration_date ASC
        LIMIT 300
    """
    rows = db.execute(query).fetchall()
    return [dict(r) for r in rows]


# ==================== CSV EXPORT ====================

@router.get("/api/export/csv")
async def export_devices_csv(
    facility_id: Optional[int] = None,
    category_id: Optional[int] = None,
    alert_status: Optional[str] = None,
    search: Optional[str] = None,
    db = Depends(get_db)
):
    """Xuất danh mục thiết bị y tế đã lọc ra tệp CSV UTF-8 BOM cho Excel"""
    query = "SELECT * FROM device_status_summary"
    conditions = []
    params = []
    
    if facility_id:
        conditions.append("facility_id = ?")
        params.append(facility_id)
    if category_id:
        conditions.append("category_id = ?")
        params.append(category_id)
    if alert_status:
        conditions.append("alert_status = ?")
        params.append(alert_status.upper())
    if search and search.strip():
        s = f"%{search.strip()}%"
        conditions.append("(device_name LIKE ? OR model LIKE ? OR serial_no LIKE ? OR manufacturer LIKE ?)")
        params.extend([s, s, s, s])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY device_name ASC"
    
    rows = db.execute(query, params).fetchall()
    
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    
    writer.writerow([
        "Mã Tài Sản (Asset Tag)", "Mã SpeedMaint", "Mã Serial (S/N)", "Tên Thiết Bị", "Model", 
        "Hãng Sản Xuất", "Nước Sản Xuất", "Mức Rủi Ro (NĐ98)", "Khoa / Vị Trí", "Ngày Kiểm Định",
        "Hạn Kiểm Định", "Trạng Thái KĐ", "Tệp PDF Gốc"
    ])
    
    for r in rows:
        writer.writerow([
            f"BVQ7-TTB-{r['id']:05d}",
            f"BM/BVQ7/{r['id']:05d}",
            r["serial_no"] or "",
            r["device_name"] or "",
            r["model"] or "",
            r["manufacturer"] or "",
            r["country_of_manufacturer"] or "",
            r["risk_level"] or "A",
            r["facility"] or "",
            r["calibration_date"] or "",
            r["recalibration_date"] or "",
            r["alert_status"] or "",
            r["source_pdf"] or ""
        ])
        
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=Danh_Muc_TTBYT_BVQ7.csv"}
    )


# ==================== PDF FILE VIEWER ENDPOINT ====================

@router.get("/api/pdf/view")
async def view_pdf(filename: str = Query(..., description="Tên file hoặc đường dẫn file PDF")):
    """Mở và xem trực tiếp tệp PDF gốc từ ổ G: hoặc thư mục dự án"""
    target_path = Path(filename)
    if target_path.exists() and target_path.is_file():
        return FileResponse(target_path, media_type="application/pdf")
        
    for root_dir in PDF_ROOT_DIRS:
        if not root_dir.exists():
            continue
        candidate = root_dir / filename
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate, media_type="application/pdf")
        
        matches = list(root_dir.rglob(Path(filename).name))
        if matches:
            return FileResponse(matches[0], media_type="application/pdf")
            
    raise HTTPException(status_code=404, detail=f"Không tìm thấy file PDF: {filename}")