"""
API Routes cho Medical Device Management System
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional, List
from .database import get_db
from .models import (
    Device, DeviceCreate, DeviceUpdate,
    CalibrationCertificate, CalibrationCertificateCreate,
    DeviceSummary, DeviceStatus
)

router = APIRouter()

PDF_ROOT_DIRS = [
    Path(r"G:\BV QUẬN 7_OCR_WORK_20260712"),
    Path(r"C:\Users\tantt\Downloads\asset-management-tools\36. TRANG THIẾT BỊ Y TẾ")
]


# ==================== DEVICE ENDPOINTS ====================

@router.get("/api/devices")
async def get_devices(
    facility_id: Optional[int] = Query(None, description="Lọc theo khoa"),
    category_id: Optional[int] = Query(None, description="Lọc theo loại thiết bị"),
    alert_status: Optional[str] = Query(None, description="Lọc trạng thái cảnh báo (OVERDUE, WARNING, OK, NO_DATA)"),
    status: Optional[str] = Query(None, description="Lọc trạng thái hoạt động"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên, model, serial, hãng sản xuất"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db = Depends(get_db)
):
    """Liệt kê danh sách thiết bị với bộ lọc đa tiêu chí"""
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
    """Chi tiết hồ sơ lý lịch thiết bị"""
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
    
    # Lấy lịch sử chứng chỉ hiệu chuẩn
    certs = db.execute("""
        SELECT * FROM calibration_certificates 
        WHERE device_id = ? 
        ORDER BY calibration_date DESC
    """, (device_id,)).fetchall()
    device_data['certificates'] = [dict(c) for c in certs]
    
    # Lấy nhật ký bảo trì
    logs = db.execute("""
        SELECT * FROM maintenance_logs 
        WHERE device_id = ? 
        ORDER BY maintenance_date DESC
    """, (device_id,)).fetchall()
    device_data['maintenance_logs'] = [dict(m) for m in logs]
    
    return device_data


# ==================== DASHBOARD ENDPOINTS ====================

@router.get("/api/dashboard/summary", response_model=DeviceSummary)
async def get_dashboard_summary(db = Depends(get_db)):
    """Tổng hợp KPI thống kê cho dashboard"""
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
    
    return DeviceSummary(
        total_devices=total,
        overdue_count=overdue,
        warning_count=warning,
        ok_count=ok,
        in_service_count=in_service,
        repair_count=repair
    )


@router.get("/api/dashboard/devices")
async def get_dashboard_devices(
    limit: int = Query(200, ge=1, le=1000),
    db = Depends(get_db)
):
    """Danh sách thiết bị kèm trạng thái cảnh báo"""
    query = """
        SELECT * FROM device_status_summary
        ORDER BY CASE alert_status WHEN 'OVERDUE' THEN 1 WHEN 'WARNING' THEN 2 WHEN 'OK' THEN 3 ELSE 4 END, device_name
        LIMIT ?
    """
    result = db.execute(query, (limit,)).fetchall()
    return [dict(row) for row in result]


@router.get("/api/dashboard/facilities")
async def get_facilities(db = Depends(get_db)):
    """Danh sách khoa/phòng ban"""
    query = """
        SELECT f.id, f.name, f.code, COUNT(d.id) as device_count
        FROM facilities f
        LEFT JOIN devices d ON f.id = d.facility_id
        GROUP BY f.id, f.name, f.code
        ORDER BY f.name
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


# ==================== PDF FILE VIEWER ENDPOINT ====================

@router.get("/api/pdf/view")
async def view_pdf(filename: str = Query(..., description="Tên file hoặc đường dẫn file PDF")):
    """Mở và xem trực tiếp tệp PDF gốc từ ổ G: hoặc thư mục dự án"""
    # Tìm kiếm file
    target_path = Path(filename)
    if target_path.exists() and target_path.is_file():
        return FileResponse(target_path, media_type="application/pdf")
        
    for root_dir in PDF_ROOT_DIRS:
        if not root_dir.exists():
            continue
        # Check direct or recursive
        candidate = root_dir / filename
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate, media_type="application/pdf")
        
        # Search by file name
        matches = list(root_dir.rglob(Path(filename).name))
        if matches:
            return FileResponse(matches[0], media_type="application/pdf")
            
    raise HTTPException(status_code=404, detail=f"Không tìm thấy file PDF: {filename}")