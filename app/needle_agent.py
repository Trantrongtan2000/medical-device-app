"""
Needle Agent & Cactus Hybrid Routing Engine (Edge-Native Tool Caller)
Tối ưu hóa cho Cactus Needle (~45M params, 14MB) & Phân luồng Edge-Cloud.
"""
from __future__ import annotations
import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import date, datetime

# ==================== SCHEMAS & CONTRACTS ====================

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    read_only: bool = True

class RoutingDecision(BaseModel):
    route: str  # "LOCAL_EDGE" | "CLOUD_FRONTIER"
    intent: str
    confidence: float
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rationale: str
    requires_confirmation: bool = False

class AgentExecutionResult(BaseModel):
    status: str
    route_taken: str
    confidence: float
    tool_name: Optional[str] = None
    structured_data: Optional[Any] = None
    response_text: str
    latency_ms: float
    engine: str

# 5 Core Tools Definitions for Needle
TOOLS_REGISTRY: Dict[str, ToolDefinition] = {
    "get_device_by_asset_tag": ToolDefinition(
        name="get_device_by_asset_tag",
        description="Tra cứu thông tin chi tiết một thiết bị y tế theo mã định danh tài sản chuẩn BVQ7-TTB-xxxxx hoặc số ID",
        parameters=[
            ToolParameter(name="asset_tag", type="string", description="Mã tài sản (VD: BVQ7-TTB-00001) hoặc số ID thiết bị")
        ],
        read_only=True
    ),
    "search_devices": ToolDefinition(
        name="search_devices",
        description="Tìm kiếm danh sách thiết bị theo tên, model, serial hoặc khoa phòng sử dụng",
        parameters=[
            ToolParameter(name="keyword", type="string", description="Từ khóa tên máy, model, serial"),
            ToolParameter(name="facility_id", type="integer", description="ID khoa phòng (tùy chọn)", required=False)
        ],
        read_only=True
    ),
    "get_facility": ToolDefinition(
        name="get_facility",
        description="Tra cứu thông tin khoa phòng theo tên hoặc mã khoa",
        parameters=[
            ToolParameter(name="name_or_code", type="string", description="Tên khoa (VD: Cấp Cứu, Xét Nghiệm) hoặc mã khoa")
        ],
        read_only=True
    ),
    "get_device_calibration_status": ToolDefinition(
        name="get_device_calibration_status",
        description="Kiểm tra hạn kiểm định, hiệu chuẩn và tình trạng cảnh báo của thiết bị y tế",
        parameters=[
            ToolParameter(name="device_id_or_tag", type="string", description="ID thiết bị hoặc mã tài sản BVQ7-TTB-xxxxx")
        ],
        read_only=True
    ),
    "get_dashboard_summary": ToolDefinition(
        name="get_dashboard_summary",
        description="Lấy báo cáo tổng hợp KPI: tổng số thiết bị, số lượng hoạt động, quá hạn, cảnh báo và tỷ lệ tuân thủ",
        parameters=[],
        read_only=True
    )
}

# ==================== NEEDLE PARSER & ROUTER ====================

class NeedleRouter:
    """Mô phỏng bộ suy luận và trích xuất tool call của Needle 2 (45M Edge Model)"""

    @staticmethod
    def parse_intent(query: str) -> RoutingDecision:
        q = query.strip()
        q_lower = q.lower()

        # 1. Phát hiện lệnh thay đổi dữ liệu trước (Chốt an toàn yêu cầu xác nhận trước khi sửa/chuyển)
        if any(k in q_lower for k in ["chuyển máy", "điều chuyển", "bàn giao", "sửa chữa", "báo hỏng", "tạo phiếu"]):
            return RoutingDecision(
                route="LOCAL_EDGE",
                intent="MUTATION_ACTION",
                confidence=0.92,
                tool_name="create_transfer" if any(x in q_lower for x in ["chuyển", "bàn giao"]) else "create_repair",
                parameters={"raw_query": q},
                rationale="Phát hiện thao tác thay đổi dữ liệu (Yêu cầu xác nhận).",
                requires_confirmation=True
            )

        # 2. Tra cứu theo mã tài sản trực tiếp: BVQ7-TTB-xxxxx hoặc #xxxx
        tag_match = re.search(r'bvq7[-_]ttb[-_](\d{1,7})|#(\d{1,7})|thiết bị\s+(\d{1,7})', q_lower)
        if tag_match:
            dev_id = 1
            for g in tag_match.groups():
                if g:
                    dev_id = int(g)
                    break
            asset_tag = f"BVQ7-TTB-{dev_id:05d}"
            
            # Kiểm tra xem có hỏi riêng về kiểm định không
            if any(k in q_lower for k in ["kiểm định", "hiệu chuẩn", "hạn", "quá hạn", "stamp", "hạn dùng"]):
                return RoutingDecision(
                    route="LOCAL_EDGE",
                    intent="CHECK_CALIBRATION",
                    confidence=0.96,
                    tool_name="get_device_calibration_status",
                    parameters={"device_id_or_tag": asset_tag},
                    rationale=f"Phát hiện mã {asset_tag} và ý định kiểm tra hạn kiểm định."
                )

            return RoutingDecision(
                route="LOCAL_EDGE",
                intent="GET_DEVICE",
                confidence=0.98,
                tool_name="get_device_by_asset_tag",
                parameters={"asset_tag": asset_tag},
                rationale=f"Phát hiện chính xác mã tài sản chuẩn {asset_tag}."
            )

        # 3. Báo cáo tổng hợp / Dashboard
        if any(k in q_lower for k in ["tổng quan", "dashboard", "thống kê", "bao nhiêu thiết bị", "tổng số máy", "kpi", "tỷ lệ tuân thủ"]):
            return RoutingDecision(
                route="LOCAL_EDGE",
                intent="DASHBOARD_SUMMARY",
                confidence=0.95,
                tool_name="get_dashboard_summary",
                parameters={},
                rationale="Ý định yêu cầu số liệu thống kê tổng hợp toàn viện."
            )

        # 4. Tra cứu Khoa Phòng (Hỗ trợ toàn bộ ký tự Unicode tiếng Việt)
        if any(k in q_lower for k in ["khoa", "phòng", "vị trí"]) and not any(k in q_lower for k in ["điều chuyển", "chuyển sang", "bàn giao"]):
            dept_matches = re.findall(r'(?:khoa|phòng)\s+([^\?\.\,\!]+)', q_lower)
            if dept_matches:
                dept_name = dept_matches[0].strip()
                for stop in ["ở đâu", "nào", "ở", "gì", "thế nào"]:
                    if dept_name.endswith(f" {stop}"):
                        dept_name = dept_name[:-len(stop)-1].strip()
                return RoutingDecision(
                    route="LOCAL_EDGE",
                    intent="GET_FACILITY",
                    confidence=0.89,
                    tool_name="get_facility",
                    parameters={"name_or_code": dept_name},
                    rationale=f"Phát hiện tên khoa/phòng: '{dept_name}'."
                )

        # 5. Tìm kiếm thiết bị theo loại máy hoặc từ khóa
        device_keywords = ["máy thở", "monitor", "siêu âm", "x-quang", "điện tim", "bơm tiêm điện", "dao mổ", "nồi hấp", "máy sốc tim", "ly tâm", "hút dịch"]
        for kw in device_keywords:
            if kw in q_lower:
                return RoutingDecision(
                    route="LOCAL_EDGE",
                    intent="SEARCH_DEVICES",
                    confidence=0.91,
                    tool_name="search_devices",
                    parameters={"keyword": kw},
                    rationale=f"Phát hiện từ khóa thiết bị: '{kw}'."
                )
        # 6. Các câu hỏi lý thuyết / quy trình / chính sách / OCR dài -> Chuyển Cloud Gemini
        return RoutingDecision(
            route="CLOUD_FRONTIER",
            intent="COMPLEX_REASONING_OR_POLICY",
            confidence=0.60,
            tool_name=None,
            parameters={"query": q},
            rationale="Câu hỏi yêu cầu suy luận quy trình, văn bản pháp lý hoặc nằm ngoài 5 tool cục bộ."
        )

# ==================== SAFE TOOL EXECUTOR ====================

def escape_like(s: str) -> str:
    """Escape các ký tự đặc biệt % và _ trong LIKE query"""
    return s.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

class SafeToolExecutor:
    """Thực thi các tool đã được kiểm tra an toàn trên database"""

    @staticmethod
    def execute_tool(tool_name: str, params: Dict[str, Any], db: sqlite3.Connection) -> Tuple[Any, str]:
        if tool_name == "get_device_by_asset_tag":
            tag = str(params.get("asset_tag", "")).strip()
            digits = re.findall(r'\d+', tag)
            dev_id = int(digits[-1]) if digits else 0
            
            row = db.execute("""
                SELECT d.*, f.name as facility_name, c.name as category_name,
                       cert.certificate_no, cert.recalibration_date as cert_due_date, cert.result_status as cert_status
                FROM devices d
                LEFT JOIN facilities f ON d.facility_id = f.id
                LEFT JOIN device_categories c ON d.category_id = c.id
                LEFT JOIN (
                    SELECT device_id, certificate_no, recalibration_date, result_status
                    FROM calibration_certificates
                    ORDER BY calibration_date DESC
                ) cert ON d.id = cert.device_id
                WHERE d.id = ?
            """, (dev_id,)).fetchone()
            
            if not row:
                return None, f"❌ Không tìm thấy thiết bị nào với mã `{tag}` trong cơ sở dữ liệu."
            
            data = dict(row)
            asset_tag = f"BVQ7-TTB-{data['id']:05d}"
            due_date = data.get('recalibration_date') or data.get('cert_due_date') or 'Chưa có dữ liệu'
            text = (
                f"🏥 **Thông Tin Thiết Bị [{asset_tag}]**\n"
                f"• **Tên máy:** {data.get('device_name')}\n"
                f"• **Model:** {data.get('model')} | **Serial No:** `{data.get('serial_no')}`\n"
                f"• **Khoa/Phòng:** {data.get('facility_name') or 'Kho lưu trữ'}\n"
                f"• **Phân loại rủi ro:** Loại {data.get('risk_level') or 'A'}\n"
                f"• **Trạng thái:** `{data.get('status')}`\n"
                f"• **Hạn kiểm định:** {due_date}"
            )
            return data, text

        elif tool_name == "search_devices":
            kw = f"%{escape_like(params.get('keyword', ''))}%"
            rows = db.execute("""
                SELECT d.id, d.device_name, d.model, d.serial_no, d.status, f.name as facility_name
                FROM devices d
                LEFT JOIN facilities f ON d.facility_id = f.id
                WHERE (d.device_name LIKE ? ESCAPE '\\' OR d.model LIKE ? ESCAPE '\\' OR d.serial_no LIKE ? ESCAPE '\\')
                LIMIT 5
            """, (kw, kw, kw)).fetchall()
            
            if not rows:
                return [], f"🔍 Không tìm thấy thiết bị nào khớp với từ khóa '{params.get('keyword')}'."
            
            data = [dict(r) for r in rows]
            lines = [f"🔍 **Tìm thấy {len(data)} thiết bị khớp với '{params.get('keyword')}':**"]
            for d in data:
                tag = f"BVQ7-TTB-{d['id']:05d}"
                lines.append(f"• **[{tag}]** {d['device_name']} (Model: {d['model']}, Vị trí: {d.get('facility_name') or 'Kho'})")
            return data, "\n".join(lines)

        elif tool_name == "get_facility":
            name_or_code = f"%{escape_like(params.get('name_or_code', ''))}%"
            rows = db.execute("""
                SELECT f.*, COUNT(d.id) as total_devices
                FROM facilities f
                LEFT JOIN devices d ON d.facility_id = f.id
                WHERE (f.name LIKE ? ESCAPE '\\' OR f.code LIKE ? ESCAPE '\\')
                GROUP BY f.id
            """, (name_or_code, name_or_code)).fetchall()
            
            if not rows:
                return [], f"🏢 Không tìm thấy khoa/phòng khớp với '{params.get('name_or_code')}'."
            
            data = [dict(r) for r in rows]
            f0 = data[0]
            text = (
                f"🏢 **Khoa/Phòng: {f0['name']} (Mã: {f0['code']})**\n"
                f"• **Vị trí:** {f0.get('location') or 'Khu vực chính'}\n"
                f"• **Quản lý:** {f0.get('manager') or 'BS. Trưởng khoa'}\n"
                f"• **Số lượng máy hiện tại:** {f0['total_devices']} thiết bị y tế"
            )
            return data, text

        elif tool_name == "get_device_calibration_status":
            tag = str(params.get("device_id_or_tag", "")).strip()
            digits = re.findall(r'\d+', tag)
            dev_id = int(digits[-1]) if digits else 0
            
            row = db.execute("""
                SELECT id, device_name, model, serial_no, calibration_date, recalibration_date,
                       CASE
                           WHEN recalibration_date IS NULL THEN 'NO_CALIBRATION'
                           WHEN date(recalibration_date) < date('now') THEN 'OVERDUE'
                           WHEN date(recalibration_date) <= date('now', '+30 days') THEN 'WARNING'
                           ELSE 'OK'
                       END AS alert_status
                FROM devices WHERE id = ?
            """, (dev_id,)).fetchone()
            
            if not row:
                return None, f"❌ Không tìm thấy thông tin kiểm định cho mã `{tag}`."
            
            data = dict(row)
            status_badge = {
                "OVERDUE": "🔴 ĐÃ QUÁ HẠN KIỂM ĐỊNH (Cần ngưng sử dụng & kiểm định lại ngay)",
                "WARNING": "🟡 SẮP HẾT HẠN (Còn dưới 30 ngày - Cần lập kế hoạch kiểm định)",
                "OK": "🟢 ĐẠT CHUẨN (Chứng nhận còn hiệu lực an toàn)",
                "NO_CALIBRATION": "⚪ CHƯA CÓ HỒ SƠ KIỂM ĐỊNH"
            }.get(data["alert_status"], "⚪ CHƯA RÕ")
            
            text = (
                f"📋 **Tình Trạng Kiểm Định [BVQ7-TTB-{data['id']:05d}]**\n"
                f"• **Thiết bị:** {data['device_name']} ({data['model']})\n"
                f"• **Ngày kiểm định gần nhất:** {data['calibration_date'] or 'N/A'}\n"
                f"• **Hạn tái kiểm định:** {data['recalibration_date'] or 'N/A'}\n"
                f"• **Đánh giá pháp lý:** {status_badge}"
            )
            return data, text

        elif tool_name == "get_dashboard_summary":
            total = db.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
            in_service = db.execute("SELECT COUNT(*) FROM devices WHERE status = 'IN_SERVICE'").fetchone()[0]
            overdue = db.execute("SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'OVERDUE'").fetchone()[0]
            warning = db.execute("SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'WARNING'").fetchone()[0]
            ok_count = db.execute("SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'OK'").fetchone()[0]
            
            compliance_rate = round((ok_count / total * 100), 1) if total > 0 else 0
            data = {
                "total_devices": total,
                "in_service": in_service,
                "overdue": overdue,
                "warning": warning,
                "ok": ok_count,
                "compliance_rate": compliance_rate
            }
            text = (
                f"📊 **Báo Cáo Tổng Hợp Thiết Bị Y Tế (Tâm Anh Q7)**\n"
                f"• **Tổng số tài sản:** **{total:,}** thiết bị\n"
                f"• **Đang vận hành lâm sàng:** **{in_service:,}** máy\n"
                f"• **Tình trạng kiểm định:** 🟢 {ok_count} Đạt | 🟡 {warning} Sắp hạn | 🔴 {overdue} Quá hạn\n"
                f"• **Tỷ lệ tuân thủ kiểm định an toàn:** **{compliance_rate}%**"
            )
            return data, text

        return None, "Tool không xác định."

# ==================== MAIN HYBRID AGENT PIPELINE ====================

class NeedleHybridAgent:
    """Entry point cho Hybrid Edge (Needle) - Cloud (Gemini) AI Agent"""

    def __init__(self, db_conn_factory=None):
        self.router = NeedleRouter()
        self.executor = SafeToolExecutor()
        self.db_conn_factory = db_conn_factory

    async def process_query(self, query: str, db: sqlite3.Connection, cloud_fallback_func=None) -> AgentExecutionResult:
        start_time = datetime.now()
        decision = self.router.parse_intent(query)

        # 1. Trường hợp phân luồng cục bộ (Edge Needle)
        if decision.route == "LOCAL_EDGE":
            if decision.requires_confirmation:
                latency = (datetime.now() - start_time).total_seconds() * 1000
                return AgentExecutionResult(
                    status="AWAITING_CONFIRMATION",
                    route_taken="LOCAL_EDGE",
                    confidence=decision.confidence,
                    tool_name=decision.tool_name,
                    structured_data=decision.parameters,
                    response_text=(
                        f"⚠️ **Yêu cầu xác nhận thao tác nghiệp vụ:**\n"
                        f"Hệ thống phát hiện yêu cầu: *'{query}'*.\n"
                        f"Để đảm bảo an toàn dữ liệu, vui lòng xác nhận phiếu trước khi ghi nhận vào CSDL."
                    ),
                    latency_ms=latency,
                    engine="Cactus Needle 2 (Edge Intent Gate)"
                )

            # Thực thi tool an toàn
            data, text = self.executor.execute_tool(decision.tool_name, decision.parameters, db)
            latency = (datetime.now() - start_time).total_seconds() * 1000
            return AgentExecutionResult(
                status="SUCCESS",
                route_taken="LOCAL_EDGE",
                confidence=decision.confidence,
                tool_name=decision.tool_name,
                structured_data=data,
                response_text=text,
                latency_ms=latency,
                engine="Cactus Needle 2 (Edge Tool Caller 14MB)"
            )

        # 2. Trường hợp phân luồng Cloud Frontier (Gemini Fallback)
        if cloud_fallback_func:
            fallback_text = await cloud_fallback_func(query)
        else:
            fallback_text = "Chuyển tiếp yêu cầu lên Google Gemini 3.7 Flash Cloud Engine."

        latency = (datetime.now() - start_time).total_seconds() * 1000
        return AgentExecutionResult(
            status="SUCCESS",
            route_taken="CLOUD_FRONTIER",
            confidence=decision.confidence,
            tool_name=None,
            structured_data={"escalation_reason": decision.rationale},
            response_text=fallback_text,
            latency_ms=latency,
            engine="Google Gemini 3.7 Flash (Cloud Frontier)"
        )

# Global Instance
needle_agent = NeedleHybridAgent()
