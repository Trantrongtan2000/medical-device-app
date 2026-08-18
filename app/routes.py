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
from .ai_services import gemini_service, mistral_ocr_service
from .key_rotator import gemini_key_pool, mistral_key_pool

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


@router.post("/api/devices")
async def create_device(dev: DeviceCreate, db = Depends(get_db)):
    """
    Quy trình Nhập Mới Trang Thiết Bị Y Tế (Chuẩn TLHD_QLTTBYT Mục 2a & Mục 3 + NĐ 98/2021)
    - Tự động sinh mã Asset Tag chuẩn Snipe-IT (BVQ7-TTB-XXXXX) & SpeedMaint Code (BM/BVQ7/XXXXX)
    - Lưu thông tin kỹ thuật, phân loại rủi ro (A/B/C/D)
    - Tự động tạo hồ sơ kiểm định và nhật ký nghiệm thu đưa vào sử dụng
    """
    # 1. Kiểm tra trùng số Serial
    existing = db.execute("SELECT id FROM devices WHERE serial_no = ?", (dev.serial_no,)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail=f"Số Serial '{dev.serial_no}' đã tồn tại trên hệ thống thiết bị!")

    # 2. Thêm thiết bị vào bảng devices
    insert_sql = """
        INSERT INTO devices (
            device_name, model, serial_no, certification_no, calibration_stamp_no,
            facility_id, category_id, manufacturer, country_of_manufacturer,
            year_of_manufacture, risk_level, status, installation_date,
            calibration_date, recalibration_date, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = db.cursor()
    cursor.execute(insert_sql, (
        dev.device_name,
        dev.model,
        dev.serial_no,
        dev.certification_no,
        dev.calibration_stamp_no,
        dev.facility_id,
        dev.category_id,
        dev.manufacturer,
        dev.country_of_manufacturer,
        dev.year_of_manufacture,
        dev.risk_level or "A",
        dev.status or "IN_SERVICE",
        dev.installation_date or date.today(),
        dev.calibration_date,
        dev.recalibration_date,
        dev.notes
    ))
    device_id = cursor.lastrowid
    db.commit()

    # 3. Tạo chứng chỉ kiểm định ban đầu nếu có thông tin
    if dev.certification_no and dev.calibration_date:
        db.execute("""
            INSERT INTO calibration_certificates (
                device_id, certificate_no, calibration_date, recalibration_date,
                stamp_no, result_status, calibrated_by
            ) VALUES (?, ?, ?, ?, ?, 'OK', 'Đơn vị Kiểm Định Ban Đầu')
        """, (device_id, dev.certification_no, dev.calibration_date, dev.recalibration_date, dev.calibration_stamp_no))
        db.commit()

    # 4. Ghi nhận nhật ký nghiệm thu bàn giao đưa vào sử dụng (Audit Trail)
    facility_name = "Kho lưu trữ"
    if dev.facility_id:
        fac = db.execute("SELECT name FROM facilities WHERE id = ?", (dev.facility_id,)).fetchone()
        if fac:
            facility_name = fac["name"]

    db.execute("""
        INSERT INTO maintenance_logs (
            device_id, maintenance_type, maintenance_date, performed_by, description
        ) VALUES (?, 'HANDOVER', ?, 'Phòng Trang Thiết Bị Y Tế', ?)
    """, (device_id, date.today(), f"Nghiệm thu nhập kho và bàn giao ban đầu cho {facility_name} theo quy trình TLHD Mục 2a & Mục 3"))
    db.commit()

    return {
        "status": "success",
        "message": f"Đã nhập mới thành công thiết bị '{dev.device_name}' vào hệ thống!",
        "device_id": device_id,
        "asset_tag": f"BVQ7-TTB-{device_id:05d}",
        "speedmaint_code": f"BM/BVQ7/{device_id:05d}"
    }



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


@router.put("/api/devices/{device_id}")
async def update_device(device_id: int, dev: DeviceUpdate, db = Depends(get_db)):
    """Chỉnh sửa và cập nhật thông tin hồ sơ thiết bị y tế (TLHD Mục 2a & Snipe-IT Asset Edit)"""
    existing = db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")

    # Kiểm tra trùng Serial nếu thay đổi serial
    if dev.serial_no and dev.serial_no != existing["serial_no"]:
        dup = db.execute("SELECT id FROM devices WHERE serial_no = ? AND id != ?", (dev.serial_no, device_id)).fetchone()
        if dup:
            raise HTTPException(status_code=400, detail=f"Số Serial '{dev.serial_no}' đã tồn tại trên thiết bị khác!")

    update_fields = []
    params = []
    
    for field, val in dev.model_dump(exclude_unset=True).items():
        if val is not None:
            update_fields.append(f"{field} = ?")
            params.append(val)

    if update_fields:
        update_fields.append("updated_at = ?")
        params.append(datetime.now())
        params.append(device_id)
        
        sql = f"UPDATE devices SET {', '.join(update_fields)} WHERE id = ?"
        db.execute(sql, params)
        
        # Ghi nhận nhật ký Audit Trail chỉnh sửa
        db.execute("""
            INSERT INTO maintenance_logs (device_id, maintenance_type, maintenance_date, performed_by, description)
            VALUES (?, 'INSPECTION', ?, 'Phòng Trang Thiết Bị Y Tế', ?)
        """, (device_id, date.today(), "Chỉnh sửa & cập nhật thông tin hồ sơ thiết bị theo quy trình TLHD Mục 2a"))
        db.commit()

    return {
        "status": "success",
        "message": f"Đã cập nhật thông tin thiết bị '{existing['device_name']}' thành công!"
    }


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
    """, (ticket.device_id, ticket.start_date, ticket.assigned_to, normalize_work_type(ticket.work_type), full_desc))
    
    if ticket.priority in ("Khẩn cấp", "Cao"):
        cur.execute("UPDATE devices SET status = 'REPAIR' WHERE id = ?", (ticket.device_id,))
        
    db.commit()
    return {"status": "success", "message": "Đã tạo phiếu công việc SpeedMaint thành công!"}


class SpeedMaintWorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    work_type: Optional[str] = None
    assigned_to: Optional[str] = None
    progress: Optional[int] = None
    description: Optional[str] = None
    materials: Optional[str] = None
    status: Optional[str] = None

def normalize_work_type(val: str) -> str:
    if not val:
        return "PREVENTIVE"
    v = val.upper()
    if "SỬA" in v or "REPAIR" in v or "HỎNG" in v:
        return "REPAIR"
    if "KIỂM ĐỊNH" in v or "HIỆU CHUẨN" in v or "CALIBRATION" in v:
        return "CALIBRATION"
    if "ĐIỀU CHUYỂN" in v or "BÀN GIAO" in v or "HANDOVER" in v:
        return "HANDOVER"
    if "KIỂM TRA" in v or "INSPECTION" in v or "KIỂM KÊ" in v:
        return "INSPECTION"
    return "PREVENTIVE"

@router.put("/api/work-orders/{wo_id}")
async def update_work_order(wo_id: int, ticket: SpeedMaintWorkOrderUpdate, db = Depends(get_db)):
    """Chỉnh sửa phiếu công việc, nội dung sửa chữa và cập nhật tiến độ SpeedMaint (Ảnh 605c)"""
    existing = db.execute("SELECT * FROM maintenance_logs WHERE id = ?", (wo_id,)).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu công việc")

    new_desc = ticket.description or existing["description"]
    if ticket.materials and "Vật tư:" not in new_desc:
        new_desc += f" (Vật tư: {ticket.materials})"

    new_type = normalize_work_type(ticket.work_type) if ticket.work_type else existing["maintenance_type"]
    new_assignee = ticket.assigned_to or existing["performed_by"]

    db.execute("""
        UPDATE maintenance_logs
        SET maintenance_type = ?, performed_by = ?, description = ?
        WHERE id = ?
    """, (new_type, new_assignee, new_desc, wo_id))
    db.commit()

    return {"status": "success", "message": f"Đã cập nhật thành công phiếu công việc #{wo_id:03d}!"}


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


# ==================== GEMINI AI AGENT & MISTRAL OCR ENDPOINTS ====================

class AIChatRequest(BaseModel):
    message: str
    device_id: Optional[int] = None

@router.post("/api/ai/chat")
async def ai_chat(req: AIChatRequest, db = Depends(get_db)):
    """Trợ lý AI Gemini chuyên sâu quản lý TTBYT BV Quận 7"""
    context_devices = []
    if req.device_id:
        row = db.execute("SELECT * FROM device_status_summary WHERE id = ?", (req.device_id,)).fetchone()
        if row:
            context_devices.append(dict(row))
    else:
        # Lấy mẫu top thiết bị để làm context
        rows = db.execute("SELECT * FROM device_status_summary ORDER BY alert_status ASC LIMIT 10").fetchall()
        context_devices = [dict(r) for r in rows]
        
    ai_reply = await gemini_service.chat(
        user_message=req.message,
        context_devices=context_devices
    )
    return {
        "status": "success",
        "reply": ai_reply,
        "engine": "Google Gemini 2.5 Flash / Interactions Agent"
    }


class OCRProcessRequest(BaseModel):
    filename: Optional[str] = None
    file_path: Optional[str] = None

@router.post("/api/ocr/process")
async def process_ocr(req: OCRProcessRequest):
    """Mistral OCR Engine (https://mistral.ai/news/ocr-4/) xử lý và bóc tách tài liệu y tế"""
    result = await mistral_ocr_service.process_document(
        file_path=req.file_path,
        filename=req.filename or "Tài liệu kiểm định TTBYT.pdf"
    )
    return result


# ==================== KEY ROTATION & MANAGEMENT ENDPOINTS ====================

class AddKeyRequest(BaseModel):
    service: str # 'gemini' | 'mistral'
    keys: str    # Comma or newline separated keys

class RemoveKeyRequest(BaseModel):
    service: str
    key: str

@router.get("/api/keys/config")
async def get_keys_config():
    """Lấy danh sách các API Key đã đăng ký và trạng thái xoay key"""
    return {
        "gemini": gemini_key_pool.get_status_summary(),
        "mistral": mistral_key_pool.get_status_summary()
    }

@router.post("/api/keys/add")
async def add_api_keys(req: AddKeyRequest):
    """Thêm 1 hoặc nhiều API keys vào danh sách xoay key"""
    if req.service == "gemini":
        count = gemini_key_pool.add_keys(req.keys)
    elif req.service == "mistral":
        count = mistral_key_pool.add_keys(req.keys)
    else:
        raise HTTPException(status_code=400, detail="Dịch vụ không hợp lệ (phải là 'gemini' hoặc 'mistral')")
        
    return {
        "status": "success",
        "message": f"Đã thêm thành công {count} API keys vào cơ chế xoay key của {req.service.upper()}!"
    }

@router.post("/api/keys/remove")
async def remove_api_key(req: RemoveKeyRequest):
    """Xóa API key khỏi danh sách xoay key"""
    if req.service == "gemini":
        gemini_key_pool.remove_key(req.key)
    elif req.service == "mistral":
        mistral_key_pool.remove_key(req.key)
    return {"status": "success", "message": f"Đã xóa API key khỏi {req.service.upper()}"}


# ==================== STANDARD OPERATING PROCEDURES (SOP HANDBOOK) ====================

SOP_HTML_PATH = Path(r"C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html")

@router.get("/sops")
async def view_sop_handbook():
    """Hiển thị trực tiếp Sổ tay Quy trình & Biểu mẫu Trang thiết bị y tế (quy_trinh_ttbyt.html)"""
    if SOP_HTML_PATH.exists():
        return FileResponse(SOP_HTML_PATH, media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="Không tìm thấy tệp sổ tay quy trình quy_trinh_ttbyt.html")

@router.get("/api/sops")
async def list_standard_sops():
    """Danh mục 9 Quy trình chuẩn (SOPs) & Chính sách quản lý TTBYT BV Quận 7"""
    return [
        {"code": "CS.TTBYT.04", "name": "Chính sách kiểm tra hiệu chuẩn & kiểm định thiết bị y tế", "type": "Chính sách", "ref": "/sops#cs-ttbyt-04"},
        {"code": "QT.01", "name": "Kiểm soát chất lượng nước R.O tại đơn vị Thận nhân tạo", "type": "Quy trình", "ref": "/sops#qt-01"},
        {"code": "QT.02", "name": "Vận hành hệ thống R.O tại đơn vị Thận nhân tạo", "type": "Quy trình", "ref": "/sops#qt-02"},
        {"code": "QT.03", "name": "Vận hành và bảng kiểm an toàn hệ thống khí y tế (O2, CO2, Vac, Air)", "type": "Quy trình", "ref": "/sops#qt-03"},
        {"code": "QT.04", "name": "Bàn giao, lắp đặt, nghiệm thu trang thiết bị y tế & Sổ lý lịch máy", "type": "Quy trình", "ref": "/sops#qt-04"},
        {"code": "QT.05", "name": "Vận hành và bảo quản trang thiết bị y tế tại khoa phòng", "type": "Quy trình", "ref": "/sops#qt-05"},
        {"code": "QT.06", "name": "Bảo trì, bảo dưỡng định kỳ (PM) và đào tạo hướng dẫn sử dụng", "type": "Quy trình", "ref": "/sops#qt-06"},
        {"code": "QT.07", "name": "Thanh lý đồ dùng, trang thiết bị hư hỏng / hết hạn / không sử dụng", "type": "Quy trình", "ref": "/sops#qt-07"},
        {"code": "QT.08", "name": "Điều chuyển trang thiết bị y tế giữa các đơn vị sử dụng", "type": "Quy trình", "ref": "/sops#qt-08"},
        {"code": "QT.09", "name": "Giao nhận bình khí y tế di động", "type": "Quy trình", "ref": "/sops#qt-09"}
    ]