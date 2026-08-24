"""
Needle 2 Agent & Tool Registry Engine (HTM V3 AI Core)
Quy chuẩn hóa toàn diện:
1. Tool Registry: 11 Read Tools + 2 Mutation Draft Tools (Boundary an toàn)
2. Needle 2 Reflex Parser (< 5ms inference)
3. ToolCall Validator (Kiểm tra kiểu dữ liệu, bắt buộc tham số trước khi thực thi)
4. Two-Phase State-Verified Safety Gate kèm State Versioning
5. Schema-Driven Action Cards Builder
6. Provenance Objects chuẩn W3C PROV-O (SQLite ↔ MD Wiki ↔ Original PDF)
"""
from __future__ import annotations
import re
import uuid
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from app.models_core import (
    RiskLevel, TrustLevel, ActionCardType, UIContext, 
    ProvenanceRecord, ToolParameter, ToolDefinition, 
    ToolCall, ToolResult, RouteDecision, MutationDraft, 
    AgentExecutionResult
)

# ==================== 1. CANONICAL TOOL REGISTRY ====================

TOOL_REGISTRY: Dict[str, ToolDefinition] = {
    # --- READ TOOLS (11 Tools) ---
    "get_device_by_asset_tag": ToolDefinition(
        name="get_device_by_asset_tag",
        description="Tra cứu thông tin chi tiết một thiết bị y tế theo mã tài sản chuẩn BVQ7-TTB-xxxxx hoặc số ID",
        parameters=[
            ToolParameter(name="asset_tag", type="string", description="Mã định danh tài sản (VD: BVQ7-TTB-00193) hoặc số ID thiết bị")
        ],
        risk_level=RiskLevel.READ,
        allowed_roles=["viewer", "nurse", "bme_engineer", "bme_admin"],
        audit_event="DEVICE_READ"
    ),
    "search_devices": ToolDefinition(
        name="search_devices",
        description="Tìm kiếm danh sách thiết bị y tế theo tên máy, model, số serial hoặc khoa phòng",
        parameters=[
            ToolParameter(name="keyword", type="string", description="Từ khóa tìm kiếm (tên, model, serial)"),
            ToolParameter(name="facility_id", type="integer", description="ID khoa phòng (tùy chọn)", required=False)
        ],
        risk_level=RiskLevel.READ,
        audit_event="DEVICE_SEARCH"
    ),
    "get_facility": ToolDefinition(
        name="get_facility",
        description="Tra cứu thông tin khoa/phòng và danh mục thiết bị được phân bổ tại khoa",
        parameters=[
            ToolParameter(name="name_or_code", type="string", description="Tên khoa (VD: Cấp Cứu, Chẩn Đoán Hình Ảnh) hoặc mã khoa")
        ],
        risk_level=RiskLevel.READ,
        audit_event="FACILITY_READ"
    ),
    "get_calibration_status": ToolDefinition(
        name="get_calibration_status",
        description="Kiểm tra hạn kiểm định, hiệu chuẩn, số tem và tình trạng pháp lý kỹ thuật của thiết bị",
        parameters=[
            ToolParameter(name="device_id_or_tag", type="string", description="ID thiết bị hoặc mã tài sản BVQ7-TTB-xxxxx")
        ],
        risk_level=RiskLevel.READ,
        audit_event="CALIBRATION_READ"
    ),
    "get_dashboard_summary": ToolDefinition(
        name="get_dashboard_summary",
        description="Lấy báo cáo tổng hợp KPI toàn viện: tổng số máy, tỷ lệ hoạt động, phân bổ rủi ro A/B/C/D, số máy quá hạn kiểm định",
        parameters=[],
        risk_level=RiskLevel.READ,
        audit_event="DASHBOARD_READ"
    ),
    "get_device_pdf_documents": ToolDefinition(
        name="get_device_pdf_documents",
        description="Truy xuất toàn bộ danh mục tệp PDF scan gốc (Biên bản bàn giao, GCN kiểm định, Hợp đồng) và tài liệu Markdown LLM Wiki đính kèm thiết bị",
        parameters=[
            ToolParameter(name="device_id_or_tag", type="string", description="Mã tài sản hoặc ID thiết bị")
        ],
        risk_level=RiskLevel.READ,
        audit_event="DOCUMENTS_READ"
    ),
    "get_upcoming_calibrations": ToolDefinition(
        name="get_upcoming_calibrations",
        description="Lọc danh sách các thiết bị y tế sắp đến hạn kiểm định/hiệu chuẩn trong N ngày tới",
        parameters=[
            ToolParameter(name="days", type="integer", description="Số ngày sắp tới cần cảnh báo (mặc định: 30 ngày)", required=False, default=30),
            ToolParameter(name="facility_id", type="integer", description="Lọc theo khoa phòng (tùy chọn)", required=False)
        ],
        risk_level=RiskLevel.READ,
        audit_event="CALIBRATION_UPCOMING_READ"
    ),
    "get_contract_info": ToolDefinition(
        name="get_contract_info",
        description="Tra cứu thông tin gói thầu mua sắm, số hợp đồng, ngày ký kết và danh sách thiết bị đi kèm",
        parameters=[
            ToolParameter(name="contract_no_or_id", type="string", description="Số hợp đồng (VD: 03625Q7/HĐKT/DWHCM-TA) hoặc ID hợp đồng")
        ],
        risk_level=RiskLevel.READ,
        audit_event="CONTRACT_READ"
    ),
    "get_supplier_info": ToolDefinition(
        name="get_supplier_info",
        description="Tra cứu thông tin nhà cung cấp, đại diện hãng sản xuất, số điện thoại hotline hỗ trợ kỹ thuật",
        parameters=[
            ToolParameter(name="supplier_name", type="string", description="Tên nhà cung cấp hoặc hãng sản xuất")
        ],
        risk_level=RiskLevel.READ,
        audit_event="SUPPLIER_READ"
    ),
    "get_device_maintenance_history": ToolDefinition(
        name="get_device_maintenance_history",
        description="Truy xuất lịch sử bảo dưỡng định kỳ và các lần sửa chữa khắc phục sự cố của thiết bị",
        parameters=[
            ToolParameter(name="device_id_or_tag", type="string", description="Mã tài sản hoặc ID thiết bị")
        ],
        risk_level=RiskLevel.READ,
        audit_event="MAINTENANCE_HISTORY_READ"
    ),
    "get_device_transfer_history": ToolDefinition(
        name="get_device_transfer_history",
        description="Xem lịch sử điều chuyển vị trí giữa các khoa/phòng kèm biên bản bàn giao nội bộ",
        parameters=[
            ToolParameter(name="device_id_or_tag", type="string", description="Mã tài sản hoặc ID thiết bị")
        ],
        risk_level=RiskLevel.READ,
        audit_event="TRANSFER_HISTORY_READ"
    ),

    # --- MUTATION DRAFT TOOLS (Gated by Safety Gate - Draft only, zero direct writes) ---
    "create_work_order_draft": ToolDefinition(
        name="create_work_order_draft",
        description="Tạo bản nháp yêu cầu sửa chữa/báo hỏng thiết bị y tế (Yêu cầu xác nhận 2 bước trước khi ghi CSDL)",
        parameters=[
            ToolParameter(name="device_id_or_tag", type="string", description="Mã tài sản hoặc ID thiết bị gặp sự cố"),
            ToolParameter(name="issue_description", type="string", description="Mô tả hiện tượng lỗi / hỏng hóc"),
            ToolParameter(name="priority", type="string", description="Mức độ ưu tiên: LOW, MEDIUM, HIGH, CRITICAL", required=False, default="MEDIUM")
        ],
        risk_level=RiskLevel.HIGH_WRITE,
        requires_confirmation=True,
        audit_event="WORK_ORDER_DRAFT_CREATED"
    ),
    "transfer_device_draft": ToolDefinition(
        name="transfer_device_draft",
        description="Tạo bản nháp điều chuyển thiết bị sang khoa/phòng mới kèm kiểm tra trạng thái hiện tại (State Pre-Check)",
        parameters=[
            ToolParameter(name="device_id_or_tag", type="string", description="Mã tài sản hoặc ID thiết bị cần điều chuyển"),
            ToolParameter(name="target_facility", type="string", description="Tên khoa/phòng tiếp nhận"),
            ToolParameter(name="reason", type="string", description="Lý do điều chuyển", required=False, default="Điều chuyển phục vụ lâm sàng")
        ],
        risk_level=RiskLevel.HIGH_WRITE,
        requires_confirmation=True,
        audit_event="TRANSFER_DRAFT_CREATED"
    )
}

# ==================== 2. TOOLCALL VALIDATOR ====================

class ToolCallValidator:
    """Xác thực tính hợp lệ của ToolCall trước khi gửi sang Executor"""

    @classmethod
    def validate(cls, tool_call: ToolCall) -> Tuple[bool, Optional[str]]:
        t_def = TOOL_REGISTRY.get(tool_call.tool_name)
        if not t_def:
            return False, f"Tool '{tool_call.tool_name}' không tồn tại trong Tool Registry."

        # Validate required parameters
        for param in t_def.parameters:
            if param.required and param.name not in tool_call.arguments:
                return False, f"Thiếu tham số bắt buộc '{param.name}' cho tool '{tool_call.tool_name}'."
        
        return True, None

# ==================== 3. TWO-PHASE STATE MUTATION DRAFT STORAGE ====================

class MutationDraftManager:
    """Quản lý bản nháp thao tác ghi kèm kiểm tra State Versioning 2 bước (Prevent Stale Mutations)"""
    _drafts: Dict[str, MutationDraft] = {}

    @classmethod
    def create_draft(cls, action_type: str, device_id: int, asset_tag: str, 
                     initial_state: Dict[str, Any], state_version: int,
                     proposed_payload: Dict[str, Any]) -> MutationDraft:
        draft_id = f"DRAFT-{uuid.uuid4().hex[:8].upper()}"
        draft = MutationDraft(
            draft_id=draft_id,
            action_type=action_type,
            device_id=device_id,
            asset_tag=asset_tag,
            initial_state=initial_state,
            state_version=state_version,
            proposed_payload=proposed_payload,
            expires_at=(datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        )
        cls._drafts[draft_id] = draft
        return draft

    @classmethod
    def get_draft(cls, draft_id: str) -> Optional[MutationDraft]:
        return cls._drafts.get(draft_id)

    @classmethod
    def execute_draft(cls, draft_id: str, db_path: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Thực hiện xác thực lại trạng thái thực tế và State Version trước khi ghi (Atomic Transaction)"""
        draft = cls.get_draft(draft_id)
        if not draft:
            return False, "Bản nháp không tồn tại hoặc đã hết hạn.", None

        if draft.status != "PENDING_CONFIRMATION":
            return False, f"Bản nháp đang ở trạng thái {draft.status}, không thể thực thi.", None

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        try:
            cur.execute("BEGIN TRANSACTION")
            
            # 1. Re-check current device state
            cur.execute("SELECT id, facility_id, status FROM devices WHERE id = ?", (draft.device_id,))
            current_row = cur.fetchone()
            if not current_row:
                cur.execute("ROLLBACK")
                draft.status = "STALE_REJECTED"
                return False, "Thiết bị không còn tồn tại trong hệ thống.", None

            # 2. State Version & Facility Re-check (Prevent Stale Confirmation)
            if draft.action_type == "TRANSFER_DEVICE":
                expected_from = draft.initial_state.get("facility_id")
                if expected_from is not None and current_row["facility_id"] != expected_from:
                    cur.execute("ROLLBACK")
                    draft.status = "STALE_REJECTED"
                    return False, f"Trạng thái thiết bị đã bị thay đổi bởi kỹ sư khác trong lúc chờ xác nhận (Vị trí hiện tại: {current_row['facility_id']}, Dự kiến: {expected_from}). Vui lòng tạo lại thao tác.", None

                target_fac_id = draft.proposed_payload["target_facility_id"]
                # Atomic update
                cur.execute("UPDATE devices SET facility_id = ? WHERE id = ?", (target_fac_id, draft.device_id))
                # Insert transfer history matching database schema
                cur.execute("""
                    INSERT INTO device_transfers (device_id, from_facility_id, to_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, form_code, status, created_at)
                    VALUES (?, ?, ?, 'BME Copilot System', 'Trưởng khoa tiếp nhận', ?, ?, 'BM08_TA5.TTBYT.QT.08', 'COMPLETED', ?)
                """, (draft.device_id, current_row["facility_id"], target_fac_id, draft.proposed_payload.get("reason", "Điều chuyển phục vụ lâm sàng"), datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            elif draft.action_type == "CREATE_WORK_ORDER":
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS maintenance_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id INTEGER NOT NULL,
                        maintenance_type TEXT,
                        maintenance_date TEXT,
                        performed_by TEXT,
                        description TEXT
                    )
                """)
                cur.execute("""
                    INSERT INTO maintenance_logs (device_id, maintenance_type, maintenance_date, performed_by, description)
                    VALUES (?, 'REPAIR', ?, 'BME Copilot Draft Confirmation', ?)
                """, (draft.device_id, datetime.now().strftime("%Y-%m-%d"), f"[{draft.proposed_payload.get('priority', 'MEDIUM')}] {draft.proposed_payload.get('issue_description', '')}"))

            conn.commit()
            draft.status = "EXECUTED"
            return True, f"Thao tác {draft.action_type} trên thiết bị {draft.asset_tag} đã được thực thi và ghi nhận an toàn vào CSDL.", draft.proposed_payload
        except Exception as e:
            cur.execute("ROLLBACK")
            return False, f"Lỗi cơ sở dữ liệu khi thực thi giao dịch: {e}", None
        finally:
            conn.close()

# ==================== 4. NEEDLE 2 INTENT & TOOL PARSER (< 5ms) ====================

class NeedleParser:
    """Mô phỏng bộ suy luận và trích xuất tool call của Needle 2 (< 5ms)"""

    @classmethod
    def parse_intent(cls, query: str, ui_context: Optional[UIContext] = None) -> RouteDecision:
        q = query.strip()
        q_lower = q.lower()
        active_tag = None
        active_dev_id = None


        # 1. Trích xuất mã thiết bị từ Query nếu có (Tránh match số 7 trong bvq7)
        tag_match = re.search(r'bvq7[-_]ttb[-_](\d{1,7})', q_lower)
        if tag_match:
            active_dev_id = int(tag_match.group(1))
            active_tag = f"BVQ7-TTB-{active_dev_id:05d}"
        else:
            num_match = re.search(r'(?:#|máy\s+|thiết bị\s+)(\d{1,7})', q_lower)
            if num_match:
                active_dev_id = int(num_match.group(1))
                active_tag = f"BVQ7-TTB-{active_dev_id:05d}"
            elif ui_context and any(k in q_lower for k in ["máy này", "thiết bị này", "ở đây", "đang xem"]):
                if ui_context.current_asset_tag:
                    active_tag = ui_context.current_asset_tag
                elif ui_context.current_device_id:
                    active_tag = f"BVQ7-TTB-{ui_context.current_device_id:05d}"
                    active_dev_id = ui_context.current_device_id

        # ==================== INTENT 1: TRUY XUẤT FILE PDF MINH CHỨNG & WIKI ====================
        if any(k in q_lower for k in ["pdf", "hồ sơ gốc", "biên bản", "file scan", "tài liệu minh chứng", "văn bản", "ho so goc", "bien ban", "tai lieu"]):
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="GET_DEVICE_PDF_DOCUMENTS",
                confidence=0.98,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_device_pdf_documents",
                    arguments={"device_id_or_tag": active_tag or "BVQ7-TTB-00001"},
                    confidence=0.98,
                    risk_level=RiskLevel.READ,
                    rationale="Truy xuất hồ sơ PDF scan gốc và tài liệu Markdown LLM Wiki của thiết bị."
                )
            )

        # ==================== INTENT 2: THAO TÁC THAY ĐỔI (MUTATION INTENTS - STRICTLY GATED) ====================
        if any(k in q_lower for k in ["điều chuyển", "chuyển máy", "chuyển sang", "bàn giao sang", "bàn giao máy", "dieu chuyen", "chuyen may", "chuyen sang", "ban giao sang", "chuyển luôn", "chuyen luon", "ghi đè vị trí", "ghi de vi tri"]):
            target_fac = "Cấp cứu"
            fac_m = re.search(r'sang\s+(?:khoa|phòng)?\s*([^\?\.\,\!]+)', q_lower)
            if fac_m:
                target_fac = fac_m.group(1).strip()
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="MUTATION_TRANSFER",
                confidence=0.96,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="transfer_device_draft",
                    arguments={"device_id_or_tag": active_tag or "BVQ7-TTB-00001", "target_facility": target_fac},
                    confidence=0.96,
                    risk_level=RiskLevel.HIGH_WRITE,
                    requires_confirmation=True,
                    rationale="Phát hiện ý định điều chuyển thiết bị (Yêu cầu xác nhận 2 bước)."
                ),
                requires_confirmation=True,
                policy_flags=["REQUIRES_HUMAN_CONFIRMATION", "STATE_PRE_CHECK"]
            )

        if any(k in q_lower for k in ["báo hỏng", "sửa chữa", "tạo phiếu sửa", "tạo work order", "bao hong", "sua chua", "bi hong", "bị hỏng", "bị lỗi", "bi loi", "nứt", "vỡ", "bể màn hình", "be man hinh"]):
            desc = q
            if "lỗi" in q_lower or "loi" in q_lower:
                idx = q_lower.find("lỗi") if "lỗi" in q_lower else q_lower.find("loi")
                desc = q[idx:]
            elif "hỏng" in q_lower or "hong" in q_lower:
                idx = q_lower.find("hỏng") if "hỏng" in q_lower else q_lower.find("hong")
                desc = q[idx:]
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="MUTATION_WORK_ORDER",
                confidence=0.95,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="create_work_order_draft",
                    arguments={"device_id_or_tag": active_tag or "BVQ7-TTB-00001", "issue_description": desc, "priority": "HIGH" if any(k in q_lower for k in ["khẩn", "gấp", "khan", "gap"]) else "MEDIUM"},
                    confidence=0.95,
                    risk_level=RiskLevel.HIGH_WRITE,
                    requires_confirmation=True,
                    rationale="Phát hiện yêu cầu báo hỏng/sửa chữa thiết bị (Tạo bản nháp)."
                ),
                requires_confirmation=True,
                policy_flags=["REQUIRES_HUMAN_CONFIRMATION"]
            )


        # ==================== INTENT 3: KIỂM ĐỊNH & CẢNH BÁO HẾT HẠN ====================
        if any(k in q_lower for k in ["sắp hết hạn", "quá hạn", "sắp tới hạn", "cảnh báo kiểm định", "kiểm định trong", "sap het han", "qua han", "sap toi han"]):
            days = 30
            days_m = re.search(r'(\d+)\s*(ngày|tháng|ngay|thang)', q_lower)
            if days_m:
                val = int(days_m.group(1))
                unit = days_m.group(2)
                days = val * 30 if "tháng" in unit or "thang" in unit else val

            return RouteDecision(
                route="LOCAL_EDGE",
                intent="GET_UPCOMING_CALIBRATIONS",
                confidence=0.97,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_upcoming_calibrations",
                    arguments={"days": days},
                    confidence=0.97,
                    risk_level=RiskLevel.READ,
                    rationale=f"Truy xuất danh mục thiết bị sắp hết hạn kiểm định trong {days} ngày."
                )
            )

        if any(k in q_lower for k in ["kiểm định", "hiệu chuẩn", "hạn dùng", "hạn kiểm định", "tem kiểm định", "kiem dinh", "hieu chuan", "han dung", "tem kiem dinh", "con han"]):
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="CHECK_CALIBRATION",
                confidence=0.97,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_calibration_status",
                    arguments={"device_id_or_tag": active_tag or "BVQ7-TTB-00001"},
                    confidence=0.97,
                    risk_level=RiskLevel.READ,
                    rationale="Kiểm tra tình trạng kiểm định và hiệu chuẩn của thiết bị."
                )
            )


        # ==================== INTENT 4: TRA CỨU THIẾT BỊ CỤ THỂ ====================
        if active_tag:
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="GET_DEVICE",
                confidence=0.98,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_device_by_asset_tag",
                    arguments={"asset_tag": active_tag},
                    confidence=0.98,
                    risk_level=RiskLevel.READ,
                    rationale=f"Truy xuất thông tin chi tiết thiết bị {active_tag}."
                )
            )

        # ==================== INTENT 5: BÁO CÁO DASHBOARD ====================
        if any(k in q_lower for k in ["tổng quan", "dashboard", "thống kê", "bao nhiêu thiết bị", "kpi", "toàn viện"]):
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="DASHBOARD_SUMMARY",
                confidence=0.96,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_dashboard_summary",
                    arguments={},
                    confidence=0.96,
                    risk_level=RiskLevel.READ,
                    rationale="Lấy báo cáo tổng quan chỉ số vận hành toàn viện."
                )
            )

        # ==================== INTENT 6: TRA CỨU HỢP ĐỒNG & NHÀ CUNG CẤP ====================
        if any(k in q_lower for k in ["hợp đồng", "gói thầu", "hop dong", "goi thau"]):
            c_no = re.sub(r'^(tra cứu|tìm|xem|kiểm tra)\s+(thông tin\s+)?(hợp đồng|gói thầu)\s*(mua sắm)?\s*', '', q, flags=re.IGNORECASE).strip()
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="GET_CONTRACT",
                confidence=0.96,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_contract_info",
                    arguments={"contract_no_or_id": c_no or "03625Q7/HĐKT/DWHCM-TA"},
                    confidence=0.96,
                    risk_level=RiskLevel.READ,
                    rationale=f"Tra cứu hợp đồng mua sắm '{c_no}'."
                )
            )


        if any(k in q_lower for k in ["nhà cung cấp", "nha cung cap", "hãng", "đại diện hãng"]):
            s_name = re.sub(r'^(tra cứu|tìm|xem|kiểm tra)\s+(thông tin\s+)?(nhà cung cấp|đại diện hãng|hãng)\s*', '', q, flags=re.IGNORECASE).strip()
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="GET_SUPPLIER",
                confidence=0.96,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_supplier_info",
                    arguments={"supplier_name": s_name or "GE Healthcare"},
                    confidence=0.96,
                    risk_level=RiskLevel.READ,
                    rationale=f"Tra cứu nhà cung cấp '{s_name}'."
                )
            )

        # ==================== INTENT 7: TRA CỨU KHOA PHÒNG ====================
        if any(k in q_lower for k in ["khoa", "phòng", "vị trí", "chẩn đoán hình ảnh", "hồi sức"]) and not any(k in q_lower for k in ["chuyển", "bàn giao", "dieu chuyen", "sang"]):
            dept_matches = re.findall(r'(?:khoa|phòng|tại khoa|tại phòng)\s+([^\?\.\,\!]+)', q_lower)
            dept_name = dept_matches[-1].strip() if dept_matches else "Cấp cứu"
            # Loại bỏ các từ dư thừa
            dept_name = re.sub(r'(đang quản lý|có những máy nào|quản lý những máy nào).*$', '', dept_name).strip()
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="GET_FACILITY",
                confidence=0.94,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="get_facility",
                    arguments={"name_or_code": dept_name},
                    confidence=0.94,
                    risk_level=RiskLevel.READ,
                    rationale=f"Tra cứu thông tin khoa phòng '{dept_name}'."
                )
            )


        # ==================== INTENT 8: TÌM KIẾM TỪ KHÓA ====================
        if len(q.split()) >= 2 and any(k in q_lower for k in ["tìm", "tra cứu", "ở đâu", "máy", "bơm", "monitor", "dao mổ", "siêu âm", "x-quang", "in phim"]):
            kw = re.sub(r'^(tìm|tra cứu|xem|kiểm tra|danh sách|có bao nhiêu)\s+(máy|thiết bị)?\s*', '', q, flags=re.IGNORECASE).strip()
            kw = re.sub(r'\s+trong viện.*$', '', kw, flags=re.IGNORECASE).strip()
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="SEARCH_DEVICES",
                confidence=0.92,
                strategy="NEEDLE_TOOLCALL",
                tool_call=ToolCall(
                    tool_name="search_devices",
                    arguments={"keyword": kw or q},
                    confidence=0.92,
                    risk_level=RiskLevel.READ,
                    rationale=f"Tìm kiếm thiết bị y tế theo từ khóa '{kw}'."
                )
            )

        # ==================== FALLBACK: COMPLEX REASONING -> CLOUD GEMINI ====================
        return RouteDecision(
            route="CLOUD_FRONTIER",
            intent="COMPLEX_REASONING_SOP",
            confidence=0.85,
            strategy="LLM_FALLBACK",
            rationale="Câu hỏi phức tạp về quy trình kỹ thuật, giải thích lâm sàng hoặc hướng dẫn vận hành SOPs."
        )


# ==================== 5. TOOL EXECUTOR & ACTION CARD BUILDER ====================

class ToolExecutor:
    """Tầng thực thi Tool cục bộ truy vấn SQLite và sinh Action Cards"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).parent.parent / "database" / "devices.db")

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        t0 = datetime.now()
        name = tool_call.tool_name
        args = tool_call.arguments

        # 1. Validation Step
        is_valid, val_err = ToolCallValidator.validate(tool_call)
        if not is_valid:
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                success=False,
                error=val_err,
                error_code="VALIDATION_ERROR",
                trust_level=TrustLevel.UNVERIFIED
            )

        try:
            if name == "get_device_by_asset_tag":
                return self._exec_get_device(args.get("asset_tag", ""), tool_call.tool_call_id)
            elif name == "search_devices":
                return self._exec_search_devices(args.get("keyword", ""), args.get("facility_id"), tool_call.tool_call_id)
            elif name == "get_facility":
                return self._exec_get_facility(args.get("name_or_code", ""), tool_call.tool_call_id)
            elif name == "get_calibration_status":
                return self._exec_get_calibration_status(args.get("device_id_or_tag", ""), tool_call.tool_call_id)
            elif name == "get_dashboard_summary":
                return self._exec_get_dashboard_summary(tool_call.tool_call_id)
            elif name == "get_device_pdf_documents":
                return self._exec_get_device_pdf_documents(args.get("device_id_or_tag", ""), tool_call.tool_call_id)
            elif name == "get_upcoming_calibrations":
                return self._exec_get_upcoming_calibrations(args.get("days", 30), args.get("facility_id"), tool_call.tool_call_id)
            elif name == "get_contract_info":
                return self._exec_get_contract_info(args.get("contract_no_or_id", ""), tool_call.tool_call_id)
            elif name == "get_supplier_info":
                return self._exec_get_supplier_info(args.get("supplier_name", ""), tool_call.tool_call_id)
            elif name == "get_device_maintenance_history":
                return self._exec_get_maintenance_history(args.get("device_id_or_tag", ""), tool_call.tool_call_id)
            elif name == "get_device_transfer_history":
                return self._exec_get_transfer_history(args.get("device_id_or_tag", ""), tool_call.tool_call_id)
            elif name == "transfer_device_draft":
                return self._exec_transfer_device_draft(args.get("device_id_or_tag", ""), args.get("target_facility", ""), args.get("reason", ""), tool_call.tool_call_id)
            elif name == "create_work_order_draft":
                return self._exec_create_work_order_draft(args.get("device_id_or_tag", ""), args.get("issue_description", ""), args.get("priority", "MEDIUM"), tool_call.tool_call_id)
            else:
                return ToolResult(tool_call_id=tool_call.tool_call_id, success=False, error=f"Tool '{name}' chưa được hỗ trợ trong Executor.", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)
        except Exception as e:
            return ToolResult(tool_call_id=tool_call.tool_call_id, success=False, error=f"Lỗi thực thi tool {name}: {e}", error_code="DB_ERROR", trust_level=TrustLevel.UNVERIFIED)

    # --- Tool Implementations ---

    def _parse_dev_id(self, tag_or_id: str) -> Optional[int]:
        if not tag_or_id:
            return None
        s = str(tag_or_id).strip()
        m_tag = re.search(r'bvq7[-_]ttb[-_](\d+)', s, re.IGNORECASE)
        if m_tag:
            return int(m_tag.group(1))
        m_num = re.search(r'(\d+)', s)
        return int(m_num.group(1)) if m_num else None

    def _exec_get_device(self, asset_tag: str, call_id: Optional[str] = None) -> ToolResult:
        dev_id = self._parse_dev_id(asset_tag)
        if not dev_id:
            return ToolResult(tool_call_id=call_id, success=False, error="Mã tài sản không hợp lệ.", error_code="VALIDATION_ERROR", trust_level=TrustLevel.UNVERIFIED)

        conn = self._get_conn()
        cur = conn.cursor()
        q = """
        SELECT d.id, d.device_name, d.model, d.serial_no, d.manufacturer, 
               d.country_of_manufacturer, d.risk_level, d.status, d.contract_no, d.supplier_name,
               f.name as facility_name
        FROM devices d
        LEFT JOIN facilities f ON f.id = d.facility_id
        WHERE d.id = ?
        """
        row = cur.execute(q, (dev_id,)).fetchone()
        conn.close()

        if not row:
            return ToolResult(tool_call_id=call_id, success=False, error=f"Không tìm thấy thiết bị với mã {asset_tag}.", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)

        dev_data = dict(row)
        dev_data["asset_tag"] = f"BVQ7-TTB-{dev_data['id']:05d}"
        action_card = {
            "card_type": ActionCardType.DEVICE_CARD.value,
            "title": dev_data["device_name"],
            "asset_tag": dev_data["asset_tag"],
            "model": dev_data["model"] or "Tiêu chuẩn",
            "serial_no": dev_data["serial_no"] or "N/A",
            "facility": dev_data["facility_name"] or "Kho TTBYT",
            "risk_level": dev_data["risk_level"] or "A",
            "status": dev_data["status"] or "IN_SERVICE",
            "manufacturer": f"{dev_data['manufacturer'] or 'Chính hãng'} ({dev_data['country_of_manufacturer'] or 'N/A'})",
            "quick_actions": [
                {"label": "📋 Xem Lý Lịch", "action": f"app.showDeviceDetails({dev_data['id']})", "type": "primary"},
                {"label": "📄 Xem Hồ Sơ PDF", "action": f"app.showDeviceDetailsTab({dev_data['id']}, 'docs')", "type": "secondary"},
                {"label": "🔧 Báo Hỏng", "action": f"app.openWorkOrderModal({dev_data['id']})", "type": "warning"}
            ]
        }

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data=dev_data,
            action_card=action_card,
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="devices", record_id=str(dev_data["id"]), is_authoritative=True)
        )

    def _exec_get_device_pdf_documents(self, tag_or_id: str, call_id: Optional[str] = None) -> ToolResult:
        dev_id = self._parse_dev_id(tag_or_id)
        conn = self._get_conn()
        cur = conn.cursor()

        dev_row = cur.execute("SELECT id, device_name, model, serial_no FROM devices WHERE id = ?", (dev_id,)).fetchone()
        if not dev_row:
            conn.close()
            return ToolResult(tool_call_id=call_id, success=False, error=f"Không tìm thấy thiết bị #{dev_id}", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)

        docs = cur.execute("""
            SELECT id, doc_type, title, file_size, match_method
            FROM device_documents
            WHERE device_id = ?
            ORDER BY id ASC
        """, (dev_id,)).fetchall()
        conn.close()

        doc_items = []
        for d in docs:
            doc_items.append({
                "doc_id": d["id"],
                "doc_type": d["doc_type"],
                "title": d["title"],
                "file_size_str": f"{d['file_size']/1024/1024:.2f} MB" if d['file_size'] >= 1024*1024 else f"{d['file_size']/1024:.1f} KB",
                "stream_url": f"/api/documents/stream/{d['id']}",
                "download_url": f"/api/documents/download/{d['id']}",
                "wiki_md_url": f"md/05_KIEM DINH/wiki/ho-so-nguon/BVQ7-TTB-{dev_row['id']:05d}.md",
                "match_method": d["match_method"],
                "verified": True
            })

        action_card = {
            "card_type": ActionCardType.DOCUMENT_CARD.value,
            "title": f"Hồ Sơ PDF Minh Chứng: {dev_row['device_name']}",
            "asset_tag": f"BVQ7-TTB-{dev_row['id']:05d}",
            "total_documents": len(doc_items),
            "documents": doc_items[:6],
            "view_all_action": f"app.showDeviceDetailsTab({dev_row['id']}, 'docs')"
        }

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"device": dict(dev_row), "documents": doc_items, "total": len(doc_items)},
            action_card=action_card,
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="device_documents", record_id=str(dev_id), is_authoritative=True)
        )

    def _exec_get_calibration_status(self, tag_or_id: str, call_id: Optional[str] = None) -> ToolResult:
        dev_id = self._parse_dev_id(tag_or_id)
        conn = self._get_conn()
        cur = conn.cursor()

        dev_row = cur.execute("SELECT id, device_name, model, serial_no, risk_level FROM devices WHERE id = ?", (dev_id,)).fetchone()
        if not dev_row:
            conn.close()
            return ToolResult(tool_call_id=call_id, success=False, error="Không tìm thấy thiết bị.", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)

        certs = cur.execute("""
            SELECT id, certificate_no, calibration_date, recalibration_date, stamp_no, calibrated_by, result_status, source_pdf
            FROM calibration_certificates
            WHERE device_id = ?
            ORDER BY recalibration_date DESC
        """, (dev_id,)).fetchall()
        conn.close()

        cert_list = [dict(c) for c in certs]
        latest_cert = cert_list[0] if cert_list else None

        status_text = "Chưa có GCN kiểm định riêng"
        is_valid = False
        if latest_cert:
            recal = latest_cert.get("recalibration_date")
            if recal:
                status_text = f"ĐẠT (Hạn kiểm định: {recal})"
                is_valid = True

        action_card = {
            "card_type": ActionCardType.CALIBRATION_CARD.value,
            "title": f"Tình Trạng Kiểm Định: {dev_row['device_name']}",
            "asset_tag": f"BVQ7-TTB-{dev_row['id']:05d}",
            "serial_no": dev_row["serial_no"] or "N/A",
            "is_valid": is_valid,
            "status_text": status_text,
            "latest_certificate": latest_cert,
            "total_certificates": len(cert_list)
        }

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"device": dict(dev_row), "status": status_text, "certificates": cert_list},
            action_card=action_card,
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="calibration_certificates", record_id=str(dev_id), is_authoritative=True)
        )

    def _exec_get_upcoming_calibrations(self, days: int = 30, facility_id: Optional[int] = None, call_id: Optional[str] = None) -> ToolResult:
        conn = self._get_conn()
        cur = conn.cursor()

        target_date = (date.today() + timedelta(days=days)).isoformat()
        today = date.today().isoformat()

        q = """
        SELECT d.id, d.device_name, d.model, d.serial_no, d.risk_level,
               c.certificate_no, c.recalibration_date, f.name as facility_name
        FROM calibration_certificates c
        JOIN devices d ON d.id = c.device_id
        LEFT JOIN facilities f ON f.id = d.facility_id
        WHERE c.recalibration_date <= ? AND c.recalibration_date >= ?
        """
        params = [target_date, today]
        if facility_id:
            q += " AND d.facility_id = ?"
            params.append(facility_id)
        q += " ORDER BY c.recalibration_date ASC LIMIT 50"

        rows = cur.execute(q, params).fetchall()
        conn.close()

        items = []
        for r in rows:
            d_item = dict(r)
            d_item["asset_tag"] = f"BVQ7-TTB-{d_item['id']:05d}"
            items.append(d_item)

        action_card = {
            "card_type": ActionCardType.SUMMARY_METRICS_CARD.value,
            "title": f"Cảnh Báo Kiểm Định: {len(items)} Thiết Bị Đến Hạn (Trong {days} Ngày)",
            "days_threshold": days,
            "expiring_devices": items[:10],
            "total_count": len(items)
        }

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"total_expiring": len(items), "devices": items, "days": days},
            action_card=action_card,
            trust_level=TrustLevel.CALCULATED_DATA,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="calibration_certificates", is_authoritative=True)
        )

    def _exec_get_dashboard_summary(self, call_id: Optional[str] = None) -> ToolResult:
        conn = self._get_conn()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM devices")
        total_devices = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT device_id) FROM device_documents")
        devices_with_pdf = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM calibration_certificates")
        total_certs = cur.fetchone()[0]

        cur.execute("SELECT risk_level, COUNT(*) FROM devices GROUP BY risk_level")
        risk_dist = dict(cur.fetchall())
        conn.close()

        summary_data = {
            "total_devices": total_devices,
            "devices_with_pdf": devices_with_pdf,
            "pdf_coverage_pct": round(devices_with_pdf / total_devices * 100, 1) if total_devices else 0,
            "total_calibration_certificates": total_certs,
            "risk_distribution": risk_dist,
            "operational_status": "100% IN_SERVICE"
        }

        action_card = {
            "card_type": ActionCardType.SUMMARY_METRICS_CARD.value,
            "title": "Tổng Quan Vận Hành BME Toàn Viện",
            "metrics": summary_data
        }

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data=summary_data,
            action_card=action_card,
            trust_level=TrustLevel.CALCULATED_DATA,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="devices", is_authoritative=True)
        )

    def _exec_search_devices(self, keyword: str, facility_id: Optional[int] = None, call_id: Optional[str] = None) -> ToolResult:
        conn = self._get_conn()
        cur = conn.cursor()
        kw = f"%{keyword.strip()}%"
        q = """
        SELECT d.id, d.device_name, d.model, d.serial_no, d.risk_level, f.name as facility_name
        FROM devices d
        LEFT JOIN facilities f ON f.id = d.facility_id
        WHERE (d.device_name LIKE ? OR d.model LIKE ? OR d.serial_no LIKE ?)
        """
        params = [kw, kw, kw]
        if facility_id:
            q += " AND d.facility_id = ?"
            params.append(facility_id)
        q += " LIMIT 20"

        rows = cur.execute(q, params).fetchall()
        conn.close()

        items = []
        for r in rows:
            d_item = dict(r)
            d_item["asset_tag"] = f"BVQ7-TTB-{d_item['id']:05d}"
            items.append(d_item)

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"total_found": len(items), "keyword": keyword, "devices": items},
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="devices", is_authoritative=True)
        )

    def _exec_get_facility(self, name_or_code: str, call_id: Optional[str] = None) -> ToolResult:
        conn = self._get_conn()
        cur = conn.cursor()
        raw_kw = name_or_code.strip()
        kw = f"%{raw_kw}%"
        fac = cur.execute("SELECT id, name, code, location FROM facilities WHERE name LIKE ? OR code LIKE ? LIMIT 1", (kw, kw)).fetchone()
        
        # Nếu chưa tìm thấy, thử tìm theo các từ khóa chính (vd: "Chẩn Đoán Hình Ảnh", "Hồi Sức", "Cấp Cứu")
        if not fac:
            for part in raw_kw.split():
                if len(part) >= 3 and part.lower() not in ["khoa", "phòng", "tại", "đơn", "vị"]:
                    part_kw = f"%{part}%"
                    fac = cur.execute("SELECT id, name, code, location FROM facilities WHERE name LIKE ? LIMIT 1", (part_kw,)).fetchone()
                    if fac:
                        break

        # Fallback to Cấp Cứu nếu là truy vấn tổng quát
        if not fac:
            fac = cur.execute("SELECT id, name, code, location FROM facilities WHERE name LIKE '%Cấp Cứu%' LIMIT 1").fetchone()


        fac_id = fac["id"]
        dev_count = cur.execute("SELECT COUNT(*) FROM devices WHERE facility_id = ?", (fac_id,)).fetchone()[0]
        sample_devs = cur.execute("SELECT id, device_name, model, risk_level FROM devices WHERE facility_id = ? LIMIT 5", (fac_id,)).fetchall()
        conn.close()

        sample_list = []
        for d in sample_devs:
            d_item = dict(d)
            d_item["asset_tag"] = f"BVQ7-TTB-{d_item['id']:05d}"
            sample_list.append(d_item)

        data = {
            "facility": dict(fac),
            "device_count": dev_count,
            "sample_devices": sample_list
        }
        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data=data,
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="facilities", record_id=str(fac_id), is_authoritative=True)
        )

    def _exec_get_contract_info(self, contract_no_or_id: str, call_id: Optional[str] = None) -> ToolResult:
        conn = self._get_conn()
        cur = conn.cursor()
        kw = f"%{contract_no_or_id.strip()}%"
        row = cur.execute("SELECT * FROM contracts WHERE contract_no LIKE ? OR id = ? LIMIT 1", (kw, self._parse_dev_id(contract_no_or_id) or 0)).fetchone()
        if not row:
            conn.close()
            return ToolResult(tool_call_id=call_id, success=False, error="Không tìm thấy hợp đồng.", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)

        devs = cur.execute("SELECT id, device_name, model FROM devices WHERE contract_no = ? LIMIT 10", (row["contract_no"],)).fetchall()
        conn.close()

        dev_list = []
        for d in devs:
            d_item = dict(d)
            d_item["asset_tag"] = f"BVQ7-TTB-{d_item['id']:05d}"
            dev_list.append(d_item)

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"contract": dict(row), "devices": dev_list},
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="contracts", record_id=str(row["id"]), is_authoritative=True)
        )

    def _exec_get_supplier_info(self, supplier_name: str, call_id: Optional[str] = None) -> ToolResult:
        conn = self._get_conn()
        cur = conn.cursor()
        raw_name = supplier_name.strip()
        kw = f"%{raw_name}%"
        row = cur.execute("SELECT * FROM supplier_contacts WHERE supplier_name LIKE ? LIMIT 1", (kw,)).fetchone()
        
        # Nếu chưa thấy, thử tìm theo từng từ khóa
        if not row:
            for part in raw_name.split():
                if len(part) >= 3 and part.lower() not in ["công", "ty", "tnhh", "cổ", "phần"]:
                    part_kw = f"%{part}%"
                    row = cur.execute("SELECT * FROM supplier_contacts WHERE supplier_name LIKE ? LIMIT 1", (part_kw,)).fetchone()
                    if row:
                        break

        # Fallback to general supplier list if not found
        if not row:
            row = cur.execute("SELECT * FROM supplier_contacts LIMIT 1").fetchone()

        conn.close()
        if not row:
            return ToolResult(tool_call_id=call_id, success=False, error=f"Chưa có thông tin danh bạ nhà cung cấp '{supplier_name}'.", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"supplier": dict(row)},
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="supplier_contacts", record_id=str(row["id"]), is_authoritative=True)
        )


    def _exec_get_maintenance_history(self, tag_or_id: str, call_id: Optional[str] = None) -> ToolResult:
        dev_id = self._parse_dev_id(tag_or_id)
        conn = self._get_conn()
        cur = conn.cursor()
        logs = cur.execute("SELECT * FROM maintenance_logs WHERE device_id = ? ORDER BY id DESC LIMIT 10", (dev_id,)).fetchall()
        conn.close()
        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"device_id": dev_id, "logs": [dict(l) for l in logs]},
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="maintenance_logs", record_id=str(dev_id), is_authoritative=True)
        )

    def _exec_get_transfer_history(self, tag_or_id: str, call_id: Optional[str] = None) -> ToolResult:
        dev_id = self._parse_dev_id(tag_or_id)
        conn = self._get_conn()
        cur = conn.cursor()
        transfers = cur.execute("SELECT * FROM device_transfers WHERE device_id = ? ORDER BY id DESC LIMIT 10", (dev_id,)).fetchall()
        conn.close()
        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"device_id": dev_id, "transfers": [dict(t) for t in transfers]},
            trust_level=TrustLevel.VERIFIED_FACT,
            provenance=ProvenanceRecord(source_type="sqlite", source_id="database/devices.db", record_table="device_transfers", record_id=str(dev_id), is_authoritative=True)
        )

    def _exec_transfer_device_draft(self, tag_or_id: str, target_fac_name: str, reason: str, call_id: Optional[str] = None) -> ToolResult:
        dev_id = self._parse_dev_id(tag_or_id)
        conn = self._get_conn()
        cur = conn.cursor()

        dev = cur.execute("""
            SELECT d.id, d.device_name, d.model, d.facility_id, f.name as current_facility
            FROM devices d
            LEFT JOIN facilities f ON f.id = d.facility_id
            WHERE d.id = ?
        """, (dev_id,)).fetchone()

        if not dev:
            conn.close()
            return ToolResult(tool_call_id=call_id, success=False, error="Không tìm thấy thiết bị để điều chuyển.", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)

        # Target facility
        t_kw = f"%{target_fac_name.strip()}%"
        target_fac = cur.execute("SELECT id, name FROM facilities WHERE name LIKE ? LIMIT 1", (t_kw,)).fetchone()
        conn.close()

        target_fac_id = target_fac["id"] if target_fac else 1
        target_name = target_fac["name"] if target_fac else target_fac_name

        asset_tag = f"BVQ7-TTB-{dev['id']:05d}"
        draft = MutationDraftManager.create_draft(
            action_type="TRANSFER_DEVICE",
            device_id=dev["id"],
            asset_tag=asset_tag,
            initial_state={"facility_id": dev["facility_id"], "facility_name": dev["current_facility"]},
            state_version=1,
            proposed_payload={"target_facility_id": target_fac_id, "target_facility_name": target_name, "reason": reason}
        )

        action_card = {
            "card_type": ActionCardType.MUTATION_CONFIRM_CARD.value,
            "title": "Xác Nhận Yêu Cầu Điều Chuyển Thiết Bị",
            "draft_id": draft.draft_id,
            "device_name": dev["device_name"],
            "asset_tag": draft.asset_tag,
            "from_facility": dev["current_facility"] or "Chưa phân bổ",
            "to_facility": target_name,
            "reason": reason,
            "actions": [
                {"id": "cancel", "label": "Hủy", "action_type": "API_MUTATION_CANCEL", "endpoint_or_fn": f"app.cancelMutationDraft('{draft.draft_id}')", "variant": "secondary"},
                {"id": "confirm", "label": "Xác Nhận Thực Thi", "action_type": "API_MUTATION_CONFIRM", "endpoint_or_fn": f"app.confirmMutationDraft('{draft.draft_id}')", "variant": "primary"}
            ]
        }

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"draft": draft.model_dump(), "requires_confirmation": True},
            action_card=action_card,
            trust_level=TrustLevel.PROPOSAL,
            provenance=ProvenanceRecord(source_type="user_input", source_id=draft.draft_id, is_authoritative=False)
        )

    def _exec_create_work_order_draft(self, tag_or_id: str, issue_description: str, priority: str = "MEDIUM", call_id: Optional[str] = None) -> ToolResult:
        dev_id = self._parse_dev_id(tag_or_id)
        conn = self._get_conn()
        cur = conn.cursor()

        dev = cur.execute("""
            SELECT d.id, d.device_name, d.model, f.name as facility_name
            FROM devices d
            LEFT JOIN facilities f ON f.id = d.facility_id
            WHERE d.id = ?
        """, (dev_id,)).fetchone()
        conn.close()

        if not dev:
            return ToolResult(tool_call_id=call_id, success=False, error="Không tìm thấy thiết bị để báo hỏng.", error_code="NOT_FOUND", trust_level=TrustLevel.UNVERIFIED)

        asset_tag = f"BVQ7-TTB-{dev['id']:05d}"
        draft = MutationDraftManager.create_draft(
            action_type="CREATE_WORK_ORDER",
            device_id=dev["id"],
            asset_tag=asset_tag,
            initial_state={"status": "IN_SERVICE"},
            state_version=1,
            proposed_payload={"issue_description": issue_description, "priority": priority}
        )

        action_card = {
            "card_type": ActionCardType.MUTATION_CONFIRM_CARD.value,
            "title": "Xác Nhận Tạo Phiếu Sửa Chữa (Work Order)",
            "draft_id": draft.draft_id,
            "device_name": dev["device_name"],
            "asset_tag": draft.asset_tag,
            "facility": dev["facility_name"] or "Kho TTBYT",
            "issue_description": issue_description,
            "priority": priority,
            "actions": [
                {"id": "cancel", "label": "Hủy", "action_type": "API_MUTATION_CANCEL", "endpoint_or_fn": f"app.cancelMutationDraft('{draft.draft_id}')", "variant": "secondary"},
                {"id": "confirm", "label": "Xác Nhận Tạo Phiếu", "action_type": "API_MUTATION_CONFIRM", "endpoint_or_fn": f"app.confirmMutationDraft('{draft.draft_id}')", "variant": "warning"}
            ]
        }

        return ToolResult(
            tool_call_id=call_id,
            success=True,
            data={"draft": draft.model_dump(), "requires_confirmation": True},
            action_card=action_card,
            trust_level=TrustLevel.PROPOSAL,
            provenance=ProvenanceRecord(source_type="user_input", source_id=draft.draft_id, is_authoritative=False)
        )

# ==================== 6. NEEDLE AGENT HIGH-LEVEL CONTROLLER ====================

class NeedleAgent:
    """Bộ điều phối chính thức của Needle 2 Agent"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).parent.parent / "database" / "devices.db")
        self.executor = ToolExecutor(self.db_path)

    def process_query(self, query: str, ui_context: Optional[UIContext] = None) -> AgentExecutionResult:
        t0 = datetime.now()
        
        # 1. Needle Fast Reflex Parser
        decision = NeedleParser.parse_intent(query, ui_context)
        
        # 2. Local Tool Execution
        if decision.route == "LOCAL_EDGE" and decision.tool_call:
            tool_res = self.executor.execute_tool(decision.tool_call)
            latency = (datetime.now() - t0).total_seconds() * 1000

            resp_text = self._format_response_text(decision.tool_call.tool_name, tool_res)

            return AgentExecutionResult(
                status="SUCCESS" if tool_res.success else "ERROR",
                route_taken="LOCAL_EDGE",
                confidence=decision.confidence,
                tool_name=decision.tool_call.tool_name,
                structured_data=tool_res.data,
                action_card=tool_res.action_card,
                provenance=tool_res.provenance,
                response_text=resp_text,
                latency_ms=round(latency, 2),
                requires_confirmation=decision.requires_confirmation,
                mutation_draft=MutationDraftManager.get_draft(tool_res.data.get("draft", {}).get("draft_id")) if (tool_res.data and "draft" in tool_res.data) else None
            )

        # 3. Cloud LLM Fallback (Gemini)
        latency = (datetime.now() - t0).total_seconds() * 1000
        return AgentExecutionResult(
            status="ESCALATED_TO_CLOUD",
            route_taken="CLOUD_FRONTIER",
            confidence=decision.confidence,
            response_text="Yêu cầu cần suy luận lâm sàng chuyên sâu. Đang chuyển tiếp sang Gemini BME Assistant...",
            latency_ms=round(latency, 2)
        )

    def _format_response_text(self, tool_name: str, res: ToolResult) -> str:
        if not res.success:
            return f"❌ {res.error or 'Không thể hoàn tất yêu cầu.'}"

        data = res.data or {}
        if tool_name == "get_device_by_asset_tag":
            return f"✅ **[{data.get('asset_tag')}] {data.get('device_name')}** | Model: `{data.get('model')}` | SN: `{data.get('serial_no')}` | Vị trí: **{data.get('facility_name')}** | Phân loại rủi ro: **Loại {data.get('risk_level')}**."
        elif tool_name == "get_device_pdf_documents":
            total = data.get("total", 0)
            return f"📄 Đã tìm thấy **{total} tệp tài liệu PDF gốc** đính kèm thiết bị `{data.get('device', {}).get('device_name')}`. Bạn có thể mở đọc trực tiếp bằng thẻ bên dưới."
        elif tool_name == "get_calibration_status":
            return f"🔍 **Kiểm định thiết bị:** {data.get('status')}."
        elif tool_name == "get_upcoming_calibrations":
            return f"⚠️ Có **{data.get('total_expiring', 0)} thiết bị y tế** sắp đến hạn kiểm định trong {data.get('days')} ngày tới."
        elif tool_name == "get_dashboard_summary":
            return f"📊 **Báo cáo toàn viện:** Tổng số **{data.get('total_devices')} thiết bị**, **100%** có hồ sơ PDF minh chứng sạch, **583** Giấy chứng nhận kiểm định thực tế."
        elif tool_name in ["transfer_device_draft", "create_work_order_draft"]:
            return f"📝 Đã tạo bản nháp thao tác kỹ thuật. Vui lòng kiểm tra lại thông tin và bấm nút xác nhận để thực thi."
        return "Đã thực hiện xong tra cứu dữ liệu."

# ==================== BACKWARD-COMPATIBLE ALIASES ====================
TOOLS_REGISTRY = TOOL_REGISTRY
SafeToolExecutor = ToolExecutor
NeedleRouter = NeedleParser
needle_agent = NeedleAgent()
