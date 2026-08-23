"""
Module Audit Trail Bất Biến & Luồng Tự Động Hóa CAPA (Demo / Sandbox Mode)
Tuân thủ: 21 CFR Part 11, ALCOA+ & Tiêu chuẩn Quản trị rủi ro thiết bị JCI FMS.

GHI CHÚ HỆ THỐNG:
- Toàn bộ tính năng trong module này hiện ở chế độ DEMO / MÔ PHỎNG KIỂM TOÁN.
- Không khóa cứng quyền chỉnh sửa hoặc vận hành của người dùng trên thiết bị thực tế.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from .database import get_db

router = APIRouter(prefix="/api", tags=["Audit Trail & CAPA (Demo Sandbox)"])

# ----------------- PYDANTIC SCHEMAS -----------------

class AuditLogCreate(BaseModel):
    entity_type: str  # 'DEVICE', 'CERTIFICATE', 'INSPECTION', 'TRANSFER', 'DOCUMENT'
    entity_id: str
    action_type: str  # 'CREATE', 'UPDATE', 'DELETE', 'STATUS_OVERRIDE', 'PAGE_VERIFY'
    actor_id: str = "BME-DEMO-001"
    actor_name: str = "Trần Trọng Tấn"
    actor_role: str = "LEAD_BME"
    actor_ip: Optional[str] = "127.0.0.1"
    old_value_json: Optional[str] = None
    new_value_json: Optional[str] = None
    reason_for_change: str = "Cập nhật thông tin trong phiên làm việc demo"
    document_sha256: Optional[str] = None

class CapaCreate(BaseModel):
    device_id: str
    device_name: str
    facility_id: Optional[int] = None
    source_type: str = "PRE_USE_INSPECTION"  # 'PRE_USE_INSPECTION', 'INCIDENT_REPORT', 'CALIBRATION_FAIL'
    source_ref_id: Optional[int] = None
    severity_level: str = "MEDIUM"  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    issue_description: str
    reported_by: str = "Điều Dưỡng Trực Ca (Demo)"
    root_cause_analysis: Optional[str] = None
    assigned_bme_id: Optional[str] = "KS. Trần Trọng Tấn"
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None

class CapaResolve(BaseModel):
    root_cause_analysis: str
    corrective_action: str
    preventive_action: str
    verified_by_leader: str = "Trưởng Phòng TTBYT Trần Trọng Tấn"
    closure_notes: Optional[str] = "Đã kiểm tra vận hành an toàn đạt chuẩn."

# ----------------- API ENDPOINTS -----------------

@router.get("/audit/logs")
async def get_audit_logs(limit: int = 50, offset: int = 0, db = Depends(get_db)):
    """
    [DEMO MODE] Lấy danh sách nhật ký Audit Trail bất biến (Chain of Custody).
    Không hạn chế quyền truy cập của người dùng.
    """
    rows = db.execute(
        """SELECT id, entity_type, entity_id, action_type, actor_name, actor_role,
                  reason_for_change, record_hash, previous_log_hash, is_demo, created_at
           FROM audit_trail_logs
           ORDER BY id DESC LIMIT ? OFFSET ?""",
        (limit, offset)
    ).fetchall()
    
    total = db.execute("SELECT COUNT(*) FROM audit_trail_logs").fetchone()[0]
    
    logs = [
        {
            "id": r[0], "entity_type": r[1], "entity_id": r[2], "action_type": r[3],
            "actor_name": r[4], "actor_role": r[5], "reason_for_change": r[6],
            "record_hash": r[7], "previous_log_hash": r[8], "is_demo": bool(r[9]),
            "created_at": r[10],
            "_mode": "DEMO / SANDBOX (Non-blocking)"
        }
        for r in rows
    ]
    return {"total": total, "logs": logs, "demo_notice": "Audit Trail chạy chế độ mô phỏng kiểm toán"}

@router.post("/audit/log")
async def create_audit_log(payload: AuditLogCreate, db = Depends(get_db)):
    """
    [DEMO MODE] Ghi một bản ghi nhật ký kiểm toán mới với mã băm chuỗi nối tiếp SHA-256.
    """
    # Lấy hash bản ghi trước
    prev = db.execute("SELECT record_hash FROM audit_trail_logs ORDER BY id DESC LIMIT 1").fetchone()
    prev_hash = prev[0] if prev else "GENESIS_BLOCK_0000000000000000"
    
    now_str = datetime.now().isoformat()
    raw_sig = f"{payload.entity_type}:{payload.entity_id}:{payload.action_type}:{payload.actor_id}:{now_str}:{prev_hash}"
    rec_hash = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()
    
    db.execute(
        """INSERT INTO audit_trail_logs 
           (entity_type, entity_id, action_type, actor_id, actor_name, actor_role, actor_ip,
            old_value_json, new_value_json, reason_for_change, document_sha256, previous_log_hash, record_hash, is_demo)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
        (
            payload.entity_type, payload.entity_id, payload.action_type,
            payload.actor_id, payload.actor_name, payload.actor_role, payload.actor_ip,
            payload.old_value_json, payload.new_value_json, payload.reason_for_change,
            payload.document_sha256, prev_hash, rec_hash
        )
    )
    db.commit()
    return {
        "status": "success",
        "record_hash": rec_hash,
        "previous_hash": prev_hash,
        "demo_mode": True,
        "message": "Đã ghi nhật ký audit trail (Demo Sandbox)"
    }

@router.get("/capa/list")
async def get_capa_list(status: Optional[str] = None, limit: int = 50, db = Depends(get_db)):
    """
    [DEMO MODE] Lấy danh sách phiếu CAPA (Sự cố & Hành động khắc phục phòng ngừa).
    """
    query = """SELECT id, capa_code, device_id, device_name, severity_level, issue_description,
                      reported_by, reported_at, verification_status, assigned_bme_id, is_demo
               FROM capa_records"""
    params = []
    if status:
        query += " WHERE verification_status = ?"
        params.append(status)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    rows = db.execute(query, tuple(params)).fetchall()
    items = [
        {
            "id": r[0], "capa_code": r[1], "device_id": r[2], "device_name": r[3],
            "severity_level": r[4], "issue_description": r[5], "reported_by": r[6],
            "reported_at": r[7], "verification_status": r[8], "assigned_bme_id": r[9],
            "is_demo": bool(r[10]),
            "_quarantine_enforced": False  # DEMO: Không khóa quyền user
        }
        for r in rows
    ]
    return {"total": len(items), "capa_records": items, "demo_notice": "Luồng CAPA mô phỏng chuẩn JCI"}

@router.post("/capa/create")
async def create_capa_record(payload: CapaCreate, db = Depends(get_db)):
    """
    [DEMO MODE] Tạo phiếu sự cố CAPA mới mà không khóa cứng thiết bị thực tế.
    """
    # Sinh mã CAPA
    year_month = datetime.now().strftime("%Y-%m")
    count = db.execute("SELECT COUNT(*) FROM capa_records").fetchone()[0] + 1
    capa_code = f"CAPA-{year_month}-{count:03d}"
    
    db.execute(
        """INSERT INTO capa_records
           (capa_code, device_id, device_name, facility_id, source_type, source_ref_id,
            severity_level, issue_description, reported_by, assigned_bme_id, is_device_quarantined, is_demo)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1)""",
        (
            capa_code, payload.device_id, payload.device_name, payload.facility_id,
            payload.source_type, payload.source_ref_id, payload.severity_level,
            payload.issue_description, payload.reported_by, payload.assigned_bme_id
        )
    )
    db.commit()
    
    return {
        "status": "success",
        "capa_code": capa_code,
        "is_quarantined": False,
        "demo_mode": True,
        "message": f"Phiếu {capa_code} đã được tạo ở chế độ mô phỏng (không khóa thiết bị thực tế)."
    }

@router.post("/capa/{capa_id}/resolve")
async def resolve_capa_record(capa_id: int, payload: CapaResolve, db = Depends(get_db)):
    """
    [DEMO MODE] Đóng phiếu CAPA và ghi nhận nghiệm thu an toàn.
    """
    now_str = datetime.now().isoformat()
    db.execute(
        """UPDATE capa_records
           SET root_cause_analysis = ?,
               corrective_action = ?,
               preventive_action = ?,
               verified_by_leader = ?,
               verified_at = ?,
               closure_notes = ?,
               verification_status = 'CLOSED'
           WHERE id = ?""",
        (
            payload.root_cause_analysis, payload.corrective_action, payload.preventive_action,
            payload.verified_by_leader, now_str, payload.closure_notes, capa_id
        )
    )
    db.commit()
    return {
        "status": "success",
        "capa_id": capa_id,
        "verification_status": "CLOSED",
        "demo_mode": True,
        "message": "Đã nghiệm thu và đóng phiếu CAPA (Mô phỏng quy trình JCI)"
    }

@router.get("/capa/stats")
async def get_capa_stats(db = Depends(get_db)):
    """
    [DEMO MODE] Các chỉ số đo lường hiệu quả quản trị chất lượng BME (Chuẩn JCI FMS).
    """
    total = db.execute("SELECT COUNT(*) FROM capa_records").fetchone()[0]
    closed = db.execute("SELECT COUNT(*) FROM capa_records WHERE verification_status = 'CLOSED'").fetchone()[0]
    open_cnt = total - closed
    
    return {
        "total_capa": total,
        "open_capa": open_cnt,
        "closed_capa": closed,
        "mttr_hours_target": 4.0,
        "mttr_hours_actual": 2.5,
        "capa_closure_rate_percent": round((closed / total * 100), 1) if total > 0 else 100.0,
        "repeat_failure_rate_percent": 1.2,
        "demo_sandbox": True
    }
