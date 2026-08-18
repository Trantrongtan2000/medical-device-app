"""
API Routes cho Medical Device Management System (BV Quận 7)
Chuẩn hóa theo TLHD_QLTTBYT_V1.2, SpeedMaint CMMS & Snipe-IT
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


# ==================== DEVICE ENDPOINTS ====================

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
    """Liệt kê danh sách thiết bị với bộ lọc đa tiêu chí (Snipe-IT / SpeedMaint)"""
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
    return [dict(row) for row in result]


@router.get("/api/devices/{device_id}")
async def get_device(device_id: int, db = Depends(get_db)):
    """Chi tiết hồ sơ lý lịch thiết bị y tế (Lý lịch máy chuẩn Bộ Y Tế & Snipe-IT Dossier)"""
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
    
    # Lấy lịch sử chứng chỉ kiểm định (1:N)
    certs_query = """
        SELECT * FROM calibration_certificates
        WHERE device_id = ?
        ORDER BY calibration_date DESC
    """
    certs = db.execute(certs_query, (device_id,)).fetchall()
    device_data["certificates"] = [dict(c) for c in certs]
    
    # Lấy nhật ký bảo trì & điều chuyển (Maintenance & Transfer History)
    logs_query = """
        SELECT * FROM maintenance_logs
        WHERE device_id = ?
        ORDER BY maintenance_date DESC, id DESC
    """
    logs = db.execute(logs_query, (device_id,)).fetchall()
    device_data["maintenance_logs"] = [dict(l) for l in logs]
    
    return device_data


# ==================== TRANSFER & CHECK-IN / CHECK-OUT ====================

class DeviceTransferRequest(BaseModel):
    device_id: int
    to_facility_id: int
    transferred_by: str
    reason: str

@router.post("/api/devices/transfer")
async def transfer_device(req: DeviceTransferRequest, db = Depends(get_db)):
    """Điều chuyển thiết bị giữa các khoa phòng (TLHD_QLTTBYT Mục 4 & Snipe-IT Check-out)"""
    cur = db.cursor()
    
    # Lấy tên khoa cũ và khoa mới
    old_fac = db.execute("""
        SELECT f.name FROM devices d
        LEFT JOIN facilities f ON d.facility_id = f.id
        WHERE d.id = ?
    """, (req.device_id,)).fetchone()
    old_fac_name = old_fac[0] if old_fac and old_fac[0] else "Chưa phân bổ"
    
    new_fac = db.execute("SELECT name FROM facilities WHERE id = ?", (req.to_facility_id,)).fetchone()
    if not new_fac:
        raise HTTPException(status_code=400, detail="Khoa phòng đích không tồn tại")
    new_fac_name = new_fac[0]
    
    # Cập nhật khoa mới
    cur.execute("UPDATE devices SET facility_id = ? WHERE id = ?", (req.to_facility_id, req.device_id))
    
    # Ghi nhận vào nhật ký điều chuyển
    today_str = date.today().isoformat()
    desc = f"Điều chuyển từ [{old_fac_name}] sang [{new_fac_name}]. Lý do: {req.reason}"
    cur.execute("""
        INSERT INTO maintenance_logs (device_id, maintenance_date, performed_by, maintenance_type, description)
        VALUES (?, ?, ?, 'HANDOVER', ?)
    """, (req.device_id, today_str, req.transferred_by, desc))
    
    db.commit()
    return {
        "status": "success",
        "message": f"Đã điều chuyển thiết bị thành công sang {new_fac_name}!"
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
    
    # Tính tỷ lệ sẵn sàng vận hành (Equipment Availability Rate)
    avail_rate = round((in_service / total * 100), 1) if total > 0 else 100.0
    
    return {
        "total_devices": total,
        "overdue_count": overdue,
        "warning_count": warning,
        "ok_count": ok,
        "in_service_count": in_service,
        "repair_count": repair,
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


# ==================== WORK ORDERS & INCIDENTS (SPEEDMAINT CMMS) ====================

class WorkOrderCreate(BaseModel):
    device_id: int
    reported_by: str
    priority: str = "NORMAL"  # URGENT, HIGH, NORMAL, LOW
    description: str
    issue_type: str = "REPAIR" # REPAIR, CALIBRATION, INSPECTION

@router.get("/api/work-orders")
async def list_work_orders(db = Depends(get_db)):
    """Danh sách phiếu báo hỏng & bảo dưỡng (SpeedMaint Work Orders)"""
    query = """
        SELECT l.id, l.device_id, l.maintenance_date, l.performed_by, l.maintenance_type, 
               l.description, d.device_name, d.serial_no, d.model, f.name as facility
        FROM maintenance_logs l
        JOIN devices d ON l.device_id = d.id
        LEFT JOIN facilities f ON d.facility_id = f.id
        ORDER BY l.maintenance_date DESC, l.id DESC
    """
    rows = db.execute(query).fetchall()
    return [dict(r) for r in rows]

@router.post("/api/work-orders")
async def create_work_order(ticket: WorkOrderCreate, db = Depends(get_db)):
    """Tạo phiếu báo hỏng / yêu cầu bảo dưỡng mới (TLHD_QLTTBYT Mục 6)"""
    today_str = date.today().isoformat()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO maintenance_logs (device_id, maintenance_date, performed_by, maintenance_type, description)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket.device_id, today_str, ticket.reported_by, ticket.issue_type, f"[{ticket.priority}] {ticket.description}"))
    
    if ticket.priority in ("URGENT", "HIGH"):
        cur.execute("UPDATE devices SET status = 'REPAIR' WHERE id = ?", (ticket.device_id,))
        
    db.commit()
    return {"status": "success", "message": "Phiếu yêu cầu đã được ghi nhận thành công!"}


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
        "STT", "Mã Serial (S/N)", "Tên Thiết Bị", "Model", "Hãng Sản Xuất",
        "Nước Sản Xuất", "Mức Rủi Ro (NĐ98)", "Khoa / Phòng Ban", "Ngày Kiểm Định",
        "Hạn Kiểm Định", "Trạng Thái KĐ", "Tệp PDF Gốc"
    ])
    
    for idx, r in enumerate(rows, 1):
        writer.writerow([
            idx,
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