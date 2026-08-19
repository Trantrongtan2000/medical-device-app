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
    Path(r"G:\BV QUẬN 7"),
    Path(r"G:\BV QUẬN 7_OCR_WORK_20260712"),
    Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818"),
    Path(r"C:\Users\tantt\Downloads\asset-management-tools\36. TRANG THIẾT BỊ Y TẾ")
]


WAREHOUSE_SQL = (
    "(facility_id IS NULL OR facility LIKE '%Kho Lưu%' "
    "OR facility LIKE '%Trang Thiết Bị Y Tế%' OR facility LIKE '%Chờ Cấp Phát%' "
    "OR facility LIKE '%Chưa%')"
)


def apply_snipe_status_type(conditions, status_type: Optional[str]):
    if not status_type:
        return
    st = status_type.strip().lower().replace(" ", "_")
    if st in ("rtd", "ready", "ready_to_deploy"):
        conditions.append(f"status = 'IN_SERVICE' AND {WAREHOUSE_SQL}")
    elif st in ("deployed", "assigned"):
        conditions.append(f"status = 'IN_SERVICE' AND NOT {WAREHOUSE_SQL}")
    elif st in ("pending", "in_service"):
        conditions.append("status = 'IN_SERVICE'")
    elif st in ("undeployable", "repair", "broken"):
        conditions.append("status IN ('MAINTENANCE', 'REPAIR')")
    elif st in ("archived", "disposed"):
        conditions.append("status = 'RETIRED'")
    elif st in ("overdue", "due", "calibration_overdue"):
        conditions.append("alert_status IN ('OVERDUE', 'WARNING')")


def resolve_warehouse_id(db) -> Optional[int]:
    row = db.execute(
        """
        SELECT id FROM facilities
        WHERE code IN ('KHO', 'TTBYT')
           OR name LIKE '%Kho Lưu%'
           OR name LIKE '%Trang Thiết Bị Y Tế%'
        ORDER BY CASE WHEN code = 'KHO' THEN 0 WHEN code = 'TTBYT' THEN 1 ELSE 2 END, id
        LIMIT 1
        """
    ).fetchone()
    return row[0] if row else None

class DeviceCheckoutRequest(BaseModel):
    target_type: str = "facility"  # "facility" or "user"
    facility_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    checkout_date: Optional[str] = None
    note: Optional[str] = None

class DeviceCheckinRequest(BaseModel):
    target_facility_id: Optional[int] = None  # None = central depot / unassigned
    checkin_date: Optional[str] = None
    note: Optional[str] = None

class BulkCheckoutRequest(BaseModel):
    device_ids: List[int]
    target_type: str = "facility"
    facility_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    checkout_date: Optional[str] = None
    note: Optional[str] = None

class BulkCheckinRequest(BaseModel):
    device_ids: List[int]
    target_facility_id: Optional[int] = None
    checkin_date: Optional[str] = None
    note: Optional[str] = None

# ==================== DEVICE ENDPOINTS (SNIPE-IT ASSET API) ====================

@router.get("/api/devices")
async def get_devices(
    facility_id: Optional[int] = Query(None, description="Lọc theo khoa"),
    category_id: Optional[int] = Query(None, description="Lọc theo loại thiết bị"),
    alert_status: Optional[str] = Query(None, description="Lọc trạng thái cảnh báo (OVERDUE, WARNING, OK, NO_DATA)"),
    status: Optional[str] = Query(None, description="Lọc trạng thái hoạt động"),
    status_type: Optional[str] = Query(None, description="Lọc nhóm trạng thái Snipe-IT (rtd, deployed, pending, undeployable, archived, overdue)"),
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

    apply_snipe_status_type(conditions, status_type)

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
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    assigned_to: Optional[str] = "Kỹ Sư Trực P.TTBYT"
    co_workers: Optional[str] = None
    supervisor: Optional[str] = None
    reporter: Optional[str] = "P.TTBYT"
    priority: str = "Trung bình"  # Khẩn cấp, Cao, Trung bình, Thấp / URGENT, HIGH, NORMAL
    progress: int = 0
    is_unplanned: bool = False
    location: Optional[str] = None
    description: Optional[str] = ""
    materials: Optional[str] = None
    status: Optional[str] = "PENDING"

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
        desc = item.get("description") or ""
        # Extract bracketed work type / title prefix when present: "[PM] Title. rest"
        title = desc
        if desc.startswith("[") and "]" in desc:
            title = desc.split("]", 1)[1].strip()
        if ". " in title:
            title = title.split(". ", 1)[0].strip()
        item["title"] = title or item.get("work_type") or "Phiếu công việc"
        item["task_code"] = f"260{item['id']:03d}"
        item["asset_tag"] = f"BVQ7-TTB-{item['device_id']:05d}"
        item["speedmaint_device_code"] = f"BM/BVQ7/{item['device_id']:05d}"
        item["progress"] = 100
        item["priority"] = "NORMAL"
        item["status"] = "COMPLETED"
        item["created_at"] = item.get("start_date")
        work_orders.append(item)
        
    return work_orders

@router.post("/api/work-orders")
async def create_work_order(ticket: SpeedMaintWorkOrderCreate, db = Depends(get_db)):
    """Tạo phiếu công việc chi tiết chuẩn SpeedMaint Cloud CMMS (Ảnh 01bc & 605c)"""
    cur = db.cursor()
    start = ticket.start_date or date.today().isoformat()
    full_desc = f"[{ticket.work_type}] {ticket.title}. {ticket.description or ''}".strip()
    if ticket.materials:
        full_desc += f" (Vật tư: {ticket.materials})"
    if ticket.location:
        full_desc += f" (Địa điểm: {ticket.location})"
    if ticket.priority:
        full_desc += f" [Ưu tiên: {ticket.priority}]"
        
    cur.execute("""
        INSERT INTO maintenance_logs (device_id, maintenance_date, performed_by, maintenance_type, description)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket.device_id, start, ticket.assigned_to or "Kỹ Sư Trực P.TTBYT", normalize_work_type(ticket.work_type), full_desc))
    
    priority_urgent = str(ticket.priority or "").upper() in ("KHẨN CẤP", "CAO", "URGENT", "HIGH")
    if priority_urgent:
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


@router.get("/api/facilities")
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


@router.get("/api/categories")
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

# Prefer in-repo handbook; fall back to legacy Windows path for local developer machines
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOP_HTML_CANDIDATES = [
    _PROJECT_ROOT / "web" / "sops" / "quy_trinh_ttbyt.html",
    Path(r"C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html"),
]

@router.get("/sops")
async def view_sop_handbook():
    """Hiển thị trực tiếp Sổ tay Quy trình & Biểu mẫu Trang thiết bị y tế (quy_trinh_ttbyt.html)"""
    for sop_path in SOP_HTML_CANDIDATES:
        if sop_path.exists():
            return FileResponse(sop_path, media_type="text/html; charset=utf-8")
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


# ==================== SEMANTICA AGI KNOWLEDGE GRAPH & PROVENANCE ====================

from .semantica_engine import semantica_engine

@router.get("/api/semantica/stats")
async def get_semantica_stats():
    """Lấy số liệu thống kê Context Graph của Semantica Engine"""
    return semantica_engine.get_graph_stats()

@router.get("/api/semantica/explain/{device_id}")
async def explain_device_with_semantica(device_id: int):
    """Giải trình chuỗi nguyên nhân và nguồn gốc (Causal Provenance & Zero-Hallucination Reasoning)"""
    return semantica_engine.explain_device(device_id)


# ==================== HTM CLINICAL WORKFLOWS (V3 LIFECYCLE EXTENSIONS) ====================

class AccessoryCreateRequest(BaseModel):
    parent_device_id: int
    name: str
    model: Optional[str] = None
    serial_no: Optional[str] = None
    accessory_type: Optional[str] = "Probe"
    status: Optional[str] = "Sẵn sàng sử dụng"
    notes: Optional[str] = None

class PreUseInspectionRequest(BaseModel):
    device_id: int
    inspector_name: str
    department: str
    power_ok: bool = True
    physical_ok: bool = True
    gas_pressure_ok: bool = True
    selftest_ok: bool = True
    notes: Optional[str] = None

class DeviceTransferRequest(BaseModel):
    device_id: int
    from_facility_id: int
    to_facility_id: int
    giver_name: str
    receiver_name: str
    transfer_reason: str
    transfer_date: str

@router.get("/api/devices/{device_id}/accessories")
async def get_device_accessories(device_id: int, db = Depends(get_db)):
    """Lấy danh sách phụ kiện và cấu kiện đi kèm (Parent-Child Hierarchy)"""
    cur = db.cursor()
    cur.execute("SELECT * FROM device_accessories WHERE parent_device_id = ? ORDER BY id ASC", (device_id,))
    rows = [dict(r) for r in cur.fetchall()]
    return rows

@router.post("/api/devices/{device_id}/accessories")
async def add_device_accessory(device_id: int, req: AccessoryCreateRequest, db = Depends(get_db)):
    """Thêm phụ kiện mới gắn với thiết bị chính"""
    cur = db.cursor()
    cur.execute("""
        INSERT INTO device_accessories (parent_device_id, name, model, serial_no, accessory_type, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (device_id, req.name, req.model, req.serial_no, req.accessory_type, req.status, req.notes))
    db.commit()
    new_id = cur.lastrowid
    return {"status": "success", "id": new_id, "message": "Đã thêm phụ kiện thành công"}

@router.delete("/api/accessories/{accessory_id}")
async def delete_device_accessory(accessory_id: int, db = Depends(get_db)):
    """Xóa phụ kiện"""
    cur = db.cursor()
    cur.execute("DELETE FROM device_accessories WHERE id = ?", (accessory_id,))
    db.commit()
    return {"status": "success", "message": "Đã xóa phụ kiện"}

@router.get("/api/inspections")
async def get_pre_use_inspections(limit: int = 50, db = Depends(get_db)):
    """Lấy danh sách bảng kiểm an toàn vận hành đầu ngày"""
    cur = db.cursor()
    cur.execute("""
        SELECT p.*, d.device_name, d.model, d.serial_no,
               'BVQ7-TTB-' || substr('00000' || d.id, -5) AS asset_tag
        FROM pre_use_inspections p
        JOIN devices d ON p.device_id = d.id
        ORDER BY p.inspection_time DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    return rows

@router.post("/api/inspections")
async def create_pre_use_inspection(req: PreUseInspectionRequest, db = Depends(get_db)):
    """Ghi nhận Bảng kiểm tra an toàn đầu ngày (Pre-use Checklist)"""
    cur = db.cursor()
    overall = "PASSED" if (req.power_ok and req.physical_ok and req.gas_pressure_ok and req.selftest_ok) else "WARNING"
    cur.execute("""
        INSERT INTO pre_use_inspections (device_id, inspector_name, department, power_ok, physical_ok, gas_pressure_ok, selftest_ok, overall_status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (req.device_id, req.inspector_name, req.department, req.power_ok, req.physical_ok, req.gas_pressure_ok, req.selftest_ok, overall, req.notes))
    db.commit()
    ins_id = cur.lastrowid
    return {"status": "success", "id": ins_id, "overall_status": overall, "message": "Đã lưu bảng kiểm tra an toàn đầu ngày"}

@router.get("/api/transfers")
async def get_device_transfers(limit: int = 50, db = Depends(get_db)):
    """Lấy danh sách biên bản điều chuyển thiết bị (QT.08)"""
    cur = db.cursor()
    cur.execute("""
        SELECT t.*, d.device_name, d.model, d.serial_no,
               'BVQ7-TTB-' || substr('00000' || d.id, -5) AS asset_tag,
               f1.name AS from_facility_name, f2.name AS to_facility_name
        FROM device_transfers t
        JOIN devices d ON t.device_id = d.id
        LEFT JOIN facilities f1 ON t.from_facility_id = f1.id
        LEFT JOIN facilities f2 ON t.to_facility_id = f2.id
        ORDER BY t.transfer_date DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    return rows

@router.post("/api/transfers")
async def create_device_transfer(req: DeviceTransferRequest, db = Depends(get_db)):
    """Thực hiện điều chuyển thiết bị giữa các khoa phòng (QT.08)"""
    cur = db.cursor()
    
    # 1. Cập nhật vị trí khoa phòng mới của thiết bị
    cur.execute("UPDATE devices SET facility_id = ? WHERE id = ?", (req.to_facility_id, req.device_id))
    
    # 2. Ghi nhận biên bản điều chuyển
    cur.execute("""
        INSERT INTO device_transfers (device_id, from_facility_id, to_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'COMPLETED')
    """, (req.device_id, req.from_facility_id, req.to_facility_id, req.giver_name, req.receiver_name, req.transfer_reason, req.transfer_date))
    
    trans_id = cur.lastrowid
    db.commit()
    return {
        "status": "success",
        "transfer_id": trans_id,
        "message": f"Đã thực hiện điều chuyển thiết bị thành công theo Quy trình QT.08"
    }



@router.post("/api/devices/{device_id}/checkout")
async def checkout_single_device(device_id: int, req: DeviceCheckoutRequest, db = Depends(get_db)):
    """Bàn giao thiết bị cho Bác sĩ / Điều dưỡng / Khoa phòng (Snipe-IT Checkout Pattern)"""
    dev = db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not dev:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")

    checkout_date = req.checkout_date or date.today().isoformat()
    dest_facility_id = req.facility_id if req.facility_id is not None else dev["facility_id"]
    actor = (req.assigned_to_name or "").strip() or "Bàn giao lâm sàng"

    db.execute(
        "UPDATE devices SET facility_id = ?, status = 'IN_SERVICE' WHERE id = ?",
        (dest_facility_id, device_id),
    )

    fac_row = db.execute("SELECT name FROM facilities WHERE id = ?", (dest_facility_id,)).fetchone() if dest_facility_id else None
    fac_name = fac_row["name"] if fac_row else "Kho trung tâm"

    db.execute(
        """
        INSERT INTO maintenance_logs (device_id, maintenance_type, maintenance_date, performed_by, description)
        VALUES (?, 'HANDOVER', ?, ?, ?)
        """,
        (device_id, checkout_date, actor, f"Checkout / bàn giao tới: {fac_name}. Ghi chú: {req.note or 'Sử dụng tại khoa'}")
    )
    db.commit()

    return {"status": "success", "message": f"Đã bàn giao {dev['device_name']} thành công tới {fac_name}"}


@router.post("/api/devices/{device_id}/checkin")
async def checkin_single_device(device_id: int, req: DeviceCheckinRequest, db = Depends(get_db)):
    """Thu hồi thiết bị về Kho thiết bị trung tâm (Snipe-IT Checkin Pattern)"""
    dev = db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not dev:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")

    checkin_date = req.checkin_date or date.today().isoformat()
    dest_fac = req.target_facility_id or resolve_warehouse_id(db)

    db.execute(
        "UPDATE devices SET facility_id = ?, status = 'IN_SERVICE' WHERE id = ?",
        (dest_fac, device_id),
    )

    dest_name = "Kho dự phòng"
    if dest_fac:
        fac_row = db.execute("SELECT name FROM facilities WHERE id = ?", (dest_fac,)).fetchone()
        if fac_row:
            dest_name = fac_row["name"]

    db.execute(
        """
        INSERT INTO maintenance_logs (device_id, maintenance_type, maintenance_date, performed_by, description)
        VALUES (?, 'HANDOVER', ?, 'Phòng TTBYT', ?)
        """,
        (device_id, checkin_date, f"Check-in / thu hồi về {dest_name}. Ghi chú: {req.note or 'Nhập kho dự phòng'}")
    )
    db.commit()

    return {"status": "success", "message": f"Đã thu hồi {dev['device_name']} về {dest_name}"}


@router.post("/api/devices/bulk-checkout")
async def bulk_checkout_devices(req: BulkCheckoutRequest, db = Depends(get_db)):
    """Bàn giao hàng loạt thiết bị (Snipe-IT Bulk Checkout)"""
    if not req.device_ids:
        raise HTTPException(status_code=400, detail="Danh sách thiết bị trống")

    count = 0
    checkout_date = req.checkout_date or date.today().isoformat()
    actor = (req.assigned_to_name or "").strip() or "Bàn giao hàng loạt"

    for did in req.device_ids:
        db.execute(
            "UPDATE devices SET facility_id = ?, status = 'IN_SERVICE' WHERE id = ?",
            (req.facility_id, did),
        )
        db.execute(
            """
            INSERT INTO maintenance_logs (device_id, maintenance_type, maintenance_date, performed_by, description)
            VALUES (?, 'HANDOVER', ?, ?, ?)
            """,
            (did, checkout_date, actor, f"Bulk checkout. Ghi chú: {req.note or 'Phân bổ theo kế hoạch'}")
        )
        count += 1

    db.commit()
    return {"status": "success", "updated_count": count, "message": f"Đã bàn giao {count} thiết bị thành công"}


@router.post("/api/devices/bulk-checkin")
async def bulk_checkin_devices(req: BulkCheckinRequest, db = Depends(get_db)):
    """Thu hồi hàng loạt thiết bị về kho (Snipe-IT Bulk Checkin)"""
    if not req.device_ids:
        raise HTTPException(status_code=400, detail="Danh sách thiết bị trống")

    dest_fac = req.target_facility_id or resolve_warehouse_id(db)
    count = 0
    checkin_date = req.checkin_date or date.today().isoformat()

    for did in req.device_ids:
        db.execute(
            "UPDATE devices SET facility_id = ?, status = 'IN_SERVICE' WHERE id = ?",
            (dest_fac, did),
        )
        db.execute(
            """
            INSERT INTO maintenance_logs (device_id, maintenance_type, maintenance_date, performed_by, description)
            VALUES (?, 'HANDOVER', ?, 'Phòng TTBYT', ?)
            """,
            (did, checkin_date, f"Bulk check-in. Ghi chú: {req.note or 'Nhập kho'}")
        )
        count += 1

    db.commit()
    return {"status": "success", "updated_count": count, "message": f"Đã thu hồi {count} thiết bị về kho thành công"}


@router.get("/api/dashboard/activity")
async def get_dashboard_activity(limit: int = Query(20, ge=1, le=100), db = Depends(get_db)):
    """Bảng Feed hoạt động thời gian thực (Snipe-IT Activity Feed: Checkout, Checkin, Pre-use, PM)"""
    events = []

    def tag(device_id):
        return f"BVQ7-TTB-{int(device_id):05d}"

    try:
        rows = db.execute(
            """
            SELECT t.id, t.transfer_date AS occurred_at, t.giver_name AS actor, t.transfer_reason AS detail,
                   t.device_id, d.device_name, f1.name AS from_name, f2.name AS to_name
            FROM device_transfers t
            JOIN devices d ON t.device_id = d.id
            LEFT JOIN facilities f1 ON t.from_facility_id = f1.id
            LEFT JOIN facilities f2 ON t.to_facility_id = f2.id
            ORDER BY t.id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        for r in rows:
            events.append({
                "type": "checkout",
                "title": f"Điều chuyển: {r['device_name']}",
                "detail": f"{r['from_name'] or 'Kho'} → {r['to_name'] or 'Phòng ban'}",
                "actor": r["actor"] or "P.TTBYT",
                "occurred_at": r["occurred_at"],
                "device_id": r["device_id"],
                "asset_tag": tag(r["device_id"]),
            })
    except Exception:
        pass

    try:
        rows = db.execute(
            """
            SELECT p.id, p.inspection_time AS occurred_at, p.inspector_name AS actor,
                   p.overall_status AS detail, p.device_id, d.device_name
            FROM pre_use_inspections p
            JOIN devices d ON p.device_id = d.id
            ORDER BY p.id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        for r in rows:
            events.append({
                "type": "inspection",
                "title": f"Kiểm tra đầu ngày: {r['device_name']}",
                "detail": r["detail"] or "PASSED",
                "actor": r["actor"] or "Điều dưỡng ca trực",
                "occurred_at": r["occurred_at"],
                "device_id": r["device_id"],
                "asset_tag": tag(r["device_id"]),
            })
    except Exception:
        pass

    try:
        rows = db.execute(
            """
            SELECT l.id, l.maintenance_date AS occurred_at, l.performed_by AS actor,
                   l.maintenance_type AS work_type, l.description AS detail,
                   l.device_id, d.device_name
            FROM maintenance_logs l
            JOIN devices d ON l.device_id = d.id
            ORDER BY l.id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        for r in rows:
            events.append({
                "type": (r["work_type"] or "maintenance").lower(),
                "title": f"{r['work_type'] or 'Bảo trì'} · {r['device_name']}",
                "detail": (r["detail"] or "")[:140],
                "actor": r["actor"] or "KS. Kỹ thuật",
                "occurred_at": r["occurred_at"],
                "device_id": r["device_id"],
                "asset_tag": tag(r["device_id"]),
            })
    except Exception:
        pass

    events.sort(key=lambda e: str(e.get("occurred_at") or ""), reverse=True)
    return events[:limit]



# ==================== BME STAFF & PERSONNEL MANAGEMENT ENDPOINTS ====================

class BMEStaffCreate(BaseModel):
    staff_code: str
    full_name: str
    title: str
    role_level: Optional[str] = "Kỹ Sư Chính"
    specialty: str
    phone: Optional[str] = None
    email: Optional[str] = None
    assigned_departments: Optional[str] = None
    certificates: Optional[str] = None
    duty_shift: Optional[str] = "Hành chính (07:30 - 16:30)"
    status: Optional[str] = "ACTIVE"
    avatar_color: Optional[str] = "#0284c7"

class BMEStaffUpdate(BaseModel):
    staff_code: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    role_level: Optional[str] = None
    department_unit: Optional[str] = None
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    assigned_departments: Optional[str] = None
    certificates: Optional[str] = None
    duty_shift: Optional[str] = None
    status: Optional[str] = None
    avatar_color: Optional[str] = None

@router.get("/api/staff")
async def list_bme_staff(
    status: Optional[str] = Query(None, description="Lọc theo trạng thái trực: ACTIVE, ON_DUTY, ON_LEAVE"),
    search: Optional[str] = Query(None, description="Tìm theo tên, mã NV, chuyên môn"),
    db = Depends(get_db)
):
    """Danh sách nhân sự và kỹ sư phòng Trang Thiết Bị Y Tế (BME Staff)"""
    query = "SELECT * FROM bme_staff"
    conditions = []
    params = []
    
    if status:
        conditions.append("status = ?")
        params.append(status.upper())
        
    if search and search.strip():
        s = f"%{search.strip()}%"
        conditions.append("(full_name LIKE ? OR staff_code LIKE ? OR specialty LIKE ? OR title LIKE ?)")
        params.extend([s, s, s, s])
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY CASE status WHEN 'ON_DUTY' THEN 1 WHEN 'ACTIVE' THEN 2 ELSE 3 END, id ASC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]

@router.get("/api/staff/{staff_id}")
async def get_bme_staff_detail(staff_id: int, db = Depends(get_db)):
    """Hồ sơ chi tiết và phân công nhiệm vụ của nhân sự TTBYT"""
    row = db.execute("SELECT * FROM bme_staff WHERE id = ?", (staff_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân sự TTBYT")
    
    staff = dict(row)
    
    # Lấy lịch sử công việc và bảo trì do nhân sự thực hiện
    name_like = f"%{staff['full_name'].replace('KS. ', '').replace('CN. ', '').strip()}%"
    logs = db.execute("""
        SELECT l.*, d.device_name, d.model, 'BVQ7-TTB-' || substr('00000' || d.id, -5) AS asset_tag
        FROM maintenance_logs l
        JOIN devices d ON l.device_id = d.id
        WHERE l.performed_by LIKE ?
        ORDER BY l.maintenance_date DESC LIMIT 10
    """, (name_like,)).fetchall()
    
    staff["recent_tasks"] = [dict(log) for log in logs]
    staff["total_tasks_completed"] = len(logs)
    
    return staff

@router.post("/api/staff")
async def create_bme_staff(staff: BMEStaffCreate, db = Depends(get_db)):
    """Thêm nhân sự / kỹ sư mới vào Phòng Trang Thiết Bị Y Tế"""
    cur = db.cursor()
    
    # Kiểm tra mã nhân sự trùng
    existing = cur.execute("SELECT id FROM bme_staff WHERE staff_code = ?", (staff.staff_code.strip(),)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mã nhân sự {staff.staff_code} đã tồn tại!")
        
    cur.execute("""
        INSERT INTO bme_staff (staff_code, full_name, title, role_level, specialty, phone, email, assigned_departments, certificates, duty_shift, status, avatar_color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        staff.staff_code.strip().upper(),
        staff.full_name.strip(),
        staff.title.strip(),
        staff.role_level or "Kỹ Sư Chính",
        staff.specialty.strip(),
        staff.phone,
        staff.email,
        staff.assigned_departments,
        staff.certificates,
        staff.duty_shift or "Hành chính (07:30 - 16:30)",
        staff.status or "ACTIVE",
        staff.avatar_color or "#0284c7"
    ))
    db.commit()
    new_id = cur.lastrowid
    return {"status": "success", "id": new_id, "message": f"Đã thêm nhân sự {staff.full_name} ({staff.staff_code}) thành công!"}

@router.put("/api/staff/{staff_id}")
async def update_bme_staff(staff_id: int, req: BMEStaffUpdate, db = Depends(get_db)):
    """Cập nhật thông tin nhân sự, ca trực hoặc phân công chuyên môn"""
    cur = db.cursor()
    row = cur.execute("SELECT * FROM bme_staff WHERE id = ?", (staff_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân sự TTBYT")
        
    fields = []
    params = []
    
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k} = ?")
            params.append(v)
            
    if not fields:
        return {"status": "no_change", "message": "Không có thay đổi nào"}
        
    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(staff_id)
    
    sql = f"UPDATE bme_staff SET {', '.join(fields)} WHERE id = ?"
    cur.execute(sql, params)
    db.commit()
    
    return {"status": "success", "message": "Đã cập nhật thông tin nhân sự thành công!"}

@router.delete("/api/staff/{staff_id}")
async def delete_bme_staff(staff_id: int, db = Depends(get_db)):
    """Xóa hoặc chuyển trạng thái nhân sự"""
    cur = db.cursor()
    row = cur.execute("SELECT full_name FROM bme_staff WHERE id = ?", (staff_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân sự")
        
    cur.execute("DELETE FROM bme_staff WHERE id = ?", (staff_id,))
    db.commit()
    return {"status": "success", "message": f"Đã xóa hồ sơ nhân sự {row['full_name']} khỏi hệ thống"}



@router.get("/api/directory/leaders")
async def list_hospital_leaders(db = Depends(get_db)):
    """Danh bạ Ban Giám Đốc, Lãnh Đạo Phòng Ban & Trưởng Khoa Lâm Sàng"""
    rows = db.execute("SELECT * FROM hospital_directory ORDER BY id ASC").fetchall()
    return [dict(r) for r in rows]

@router.get("/api/directory/suppliers")
async def list_supplier_contacts(search: Optional[str] = Query(None), db = Depends(get_db)):
    """Danh bạ Đối Tác Nhà Cung Cấp & Kỹ Sư Hãng Chính Thức (45 Hãng)"""
    query = "SELECT * FROM supplier_contacts"
    params = []
    if search and search.strip():
        s = f"%{search.strip()}%"
        query += " WHERE supplier_name LIKE ? OR contact_person LIKE ?"
        params.extend([s, s])
    query += " ORDER BY supplier_name ASC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]



class HospitalLeaderUpdate(BaseModel):
    group_name: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

@router.put("/api/directory/leaders/{leader_id}")
async def update_hospital_leader(leader_id: int, req: HospitalLeaderUpdate, db = Depends(get_db)):
    """Chỉnh sửa thông tin lãnh đạo / trưởng khoa lâm sàng"""
    row = db.execute("SELECT * FROM hospital_directory WHERE id = ?", (leader_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy lãnh đạo")
    fields = []
    params = []
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k} = ?")
            params.append(v)
    if fields:
        params.append(leader_id)
        db.execute(f"UPDATE hospital_directory SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()
    return {"status": "success", "message": "Đã cập nhật thông tin lãnh đạo thành công!"}

class SupplierContactUpdate(BaseModel):
    supplier_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    service_scope: Optional[str] = None

@router.put("/api/directory/suppliers/{sup_id}")
async def update_supplier_contact(sup_id: int, req: SupplierContactUpdate, db = Depends(get_db)):
    """Chỉnh sửa thông tin đối tác / đại diện hãng kỹ thuật"""
    row = db.execute("SELECT * FROM supplier_contacts WHERE id = ?", (sup_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")
    fields = []
    params = []
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k} = ?")
            params.append(v)
    if fields:
        params.append(sup_id)
        db.execute(f"UPDATE supplier_contacts SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()
    return {"status": "success", "message": "Đã cập nhật thông tin đối tác NCC thành công!"}



# ==================== ON-CALL SCHEDULE MANAGEMENT ====================

class OncallScheduleUpdate(BaseModel):
    primary_engineer: Optional[str] = None
    primary_phone: Optional[str] = None
    backup_engineer: Optional[str] = None
    backup_phone: Optional[str] = None
    leader_oncall: Optional[str] = None
    time_window: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@router.get("/api/oncall/schedule")
async def get_oncall_schedule(
    month: Optional[int] = Query(8, description="Tháng cần xem lịch"),
    year: Optional[int] = Query(2026, description="Năm cần xem lịch"),
    db = Depends(get_db)
):
    """Danh sách Lịch On-call TTBYT 24 giờ xếp theo tháng để sắp xếp trước"""
    query = "SELECT * FROM oncall_schedule WHERE month = ? AND year = ? ORDER BY day_num ASC"
    rows = db.execute(query, (month, year)).fetchall()
    if not rows:
        # Fallback to all if specific month not generated
        rows = db.execute("SELECT * FROM oncall_schedule ORDER BY year ASC, month ASC, day_num ASC LIMIT 31").fetchall()
    return [dict(r) for r in rows]

@router.get("/api/oncall/today")
async def get_today_oncall(db = Depends(get_db)):
    """Kỹ sư và Lãnh đạo On-call 24 giờ trực chính hôm nay"""
    row = db.execute("SELECT * FROM oncall_schedule WHERE status = 'TODAY' LIMIT 1").fetchone()
    if not row:
        row = db.execute("SELECT * FROM oncall_schedule WHERE day_num = 19 AND month = 8 AND year = 2026 LIMIT 1").fetchone()
    if not row:
        row = db.execute("SELECT * FROM oncall_schedule ORDER BY id ASC LIMIT 1").fetchone()
    return dict(row) if row else {}

@router.put("/api/oncall/schedule/{sched_id}")
async def update_oncall_schedule(sched_id: int, req: OncallScheduleUpdate, db = Depends(get_db)):
    """Chỉnh sửa phân công ca trực On-call TTBYT"""
    row = db.execute("SELECT * FROM oncall_schedule WHERE id = ?", (sched_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch on-call")
    fields = []
    params = []
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k} = ?")
            params.append(v)
    if fields:
        params.append(sched_id)
        db.execute(f"UPDATE oncall_schedule SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()
    return {"status": "success", "message": f"Đã cập nhật lịch On-call cho {row['day_name']} thành công!"}



class QuickAssignWeeklyRequest(BaseModel):
    month: int
    year: int
    assign_mode: str = "AUTO_MONTH" # "AUTO_MONTH", "SPECIFIC_WEEK", "CUSTOM_RANGE"
    start_engineer: str = "Trần Trọng Tấn" # "Trần Trọng Tấn", "Lê Minh Thiện", "Trần Đăng Hiếu"
    start_day: Optional[int] = None
    end_day: Optional[int] = None
    target_engineer: Optional[str] = None
    backup_engineer: Optional[str] = None

@router.post("/api/oncall/quick-assign-weekly")
async def quick_assign_weekly_oncall(req: QuickAssignWeeklyRequest, db = Depends(get_db)):
    """Chỉnh nhanh phân công lịch On-call 1 tuần cho 3 nhân sự chính: Tấn, Thiện, Hiếu"""
    engineers_map = {
        "Trần Trọng Tấn": "0334968114",
        "Lê Minh Thiện": "0378716561",
        "Trần Đăng Hiếu": "0888536278",
        "Nguyễn Tấn Lợi": "0779798786",
        "Nguyễn Quốc Việt": "0902769710",
        "Trần Thị Ngọc Châu": "0335802380"
    }
    
    order = ["Trần Trọng Tấn", "Lê Minh Thiện", "Trần Đăng Hiếu"]
    
    if req.assign_mode == "AUTO_MONTH":
        # Start rotating 3 engineers week-by-week
        rows = db.execute("SELECT id, day_num, day_name, date_str FROM oncall_schedule WHERE month = ? AND year = ? ORDER BY day_num ASC", (req.month, req.year)).fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Chưa có dữ liệu tháng này")
        
        # Start index
        start_idx = 0
        if req.start_engineer in order:
            start_idx = order.index(req.start_engineer)
            
        cur_idx = start_idx
        for r in rows:
            d_id = r["id"]
            d_name = r["day_name"]
            
            # Switch engineer every Monday
            if d_name == "Thứ Hai" and r["day_num"] > 1:
                cur_idx = (cur_idx + 1) % len(order)
                
            prim = order[cur_idx]
            back = order[(cur_idx + 1) % len(order)]
            
            db.execute("""
                UPDATE oncall_schedule
                SET primary_engineer = ?, primary_phone = ?, backup_engineer = ?, backup_phone = ?, notes = ?
                WHERE id = ?
            """, (prim, engineers_map.get(prim, ""), back, engineers_map.get(back, ""), f"Phân công nhanh tuần (On-call 24h {prim})", d_id))
            
        db.commit()
        return {"status": "success", "message": f"Đã tự động xếp lịch On-call 24h trọn Tháng {req.month}/{req.year} xoay vòng theo 3 kỹ sư: Tấn -> Thiện -> Hiếu!"}

    elif req.assign_mode == "CUSTOM_RANGE":
        if not req.start_day or not req.end_day or not req.target_engineer:
            raise HTTPException(status_code=400, detail="Thiếu thông tin khoảng ngày hoặc kỹ sư")
            
        prim = req.target_engineer
        back = req.backup_engineer or order[(order.index(prim) + 1) % len(order)] if prim in order else "Trần Đăng Hiếu"
        
        db.execute("""
            UPDATE oncall_schedule
            SET primary_engineer = ?, primary_phone = ?, backup_engineer = ?, backup_phone = ?, notes = ?
            WHERE month = ? AND year = ? AND day_num >= ? AND day_num <= ?
        """, (prim, engineers_map.get(prim, ""), back, engineers_map.get(back, ""), f"Chỉnh nhanh trọn tuần cho {prim}", req.month, req.year, req.start_day, req.end_day))
        
        db.commit()
        return {"status": "success", "message": f"Đã gán trọn ca (Ngày {req.start_day:02d} -> {req.end_day:02d}/{req.month:02d}) cho KS. {prim} thành công!"}

    return {"status": "success", "message": "Thao tác thành công"}
