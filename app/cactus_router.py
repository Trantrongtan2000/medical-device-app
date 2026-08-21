"""
6-Layer Cactus Hybrid Router with Ambiguity Detection
Kiến trúc phân luồng Edge-Cloud thông minh theo chuẩn NOOA Runtime.
"""
import re
from typing import Optional, List, Tuple
from app.models_core import RouteDecision, RiskLevel

# Clinical Ontology Dictionary for Hospital Q7
CLINICAL_ONTOLOGY = {
    "emergency": ["cấp cứu", "hồi sức", "icu", "cấp cứu ngoại", "chống sốc"],
    "imaging": ["x-quang", "ct scanner", "mri", "siêu âm", "c-arm", "nội soi"],
    "surgery": ["phòng mổ", "dao mổ điện", "bàn mổ", "đèn mổ", "nồi hấp"],
    "laboratory": ["xét nghiệm", "sinh hóa", "huyết học", "miễn dịch", "ly tâm"],
    "devices": {
        "máy thở": ("VENTILATOR", "Critical"),
        "máy sốc tim": ("DEFIBRILLATOR", "Critical"),
        "bơm tiêm điện": ("SYRINGE_PUMP", "Advanced"),
        "máy theo dõi bệnh nhân": ("MONITOR", "Advanced"),
        "monitor": ("MONITOR", "Advanced"),
        "máy siêu âm": ("ULTRASOUND", "Advanced"),
        "máy x-quang": ("XRAY", "Critical"),
        "dao mổ điện": ("ELECTROSURGICAL", "Critical")
    }
}

AMBIGUOUS_PATTERNS = [
    (r"^(kiểm tra|check)\s+(máy|thiết bị)$", "Bạn muốn: (1) Xem hạn kiểm định, (2) Kiểm tra an toàn trước khi dùng (Pre-use), hay (3) Xem lịch bảo dưỡng định kỳ?"),
    (r"^(báo cáo|thống kê)$", "Bạn muốn: (1) Báo cáo KPI toàn viện, (2) Danh sách máy quá hạn kiểm định, hay (3) Tình hình sửa chữa hôm nay?"),
    (r"^(xem hồ sơ|tra cứu)$", "Vui lòng cung cấp mã tài sản (VD: BVQ7-TTB-00001) hoặc tên khoa phòng cụ thể.")
]

class CactusHybridRouter:
    """6-Layer Hybrid Intent Router với Ambiguity Clarification Gate"""

    @classmethod
    def route(cls, query: str) -> RouteDecision:
        q = query.strip()
        q_lower = q.lower()

        # ==================== LAYER 1: DETERMINISTIC EXACT MATCH ====================
        tag_match = re.search(r'bvq7[-_]ttb[-_](\d{1,7})|#(\d{1,7})|thiết bị\s+(\d{1,7})', q_lower)
        
        # Mutation verb check first (Safety Gate)
        mutation_verbs = ["chuyển máy", "điều chuyển", "bàn giao", "sửa chữa", "báo hỏng", "tạo phiếu", "hủy phiếu", "xóa máy"]
        if any(v in q_lower for v in mutation_verbs):
            is_transfer = any(x in q_lower for x in ["chuyển", "bàn giao"])
            is_delete = "xóa" in q_lower
            risk = RiskLevel.DESTRUCTIVE if is_delete else RiskLevel.HIGH_WRITE
            
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="MUTATION_ACTION",
                confidence=0.94,
                strategy="DETERMINISTIC_EXACT",
                tool_name="create_transfer" if is_transfer else ("delete_device" if is_delete else "create_repair"),
                parameters={"raw_query": q},
                rationale="Phát hiện thao tác thay đổi dữ liệu yêu cầu xác nhận 2 bước.",
                requires_confirmation=True,
                policy_flags=["REQUIRES_HUMAN_CONFIRMATION", f"RISK_{risk.value}"]
            )

        # Asset Tag Detection
        if tag_match:
            dev_id = 1
            for g in tag_match.groups():
                if g:
                    dev_id = int(g)
                    break
            asset_tag = f"BVQ7-TTB-{dev_id:05d}"

            # Check if calibration query
            if any(k in q_lower for k in ["kiểm định", "hiệu chuẩn", "hạn", "quá hạn", "stamp", "hạn dùng"]):
                return RouteDecision(
                    route="LOCAL_EDGE",
                    intent="CHECK_CALIBRATION",
                    confidence=0.98,
                    strategy="DETERMINISTIC_EXACT",
                    tool_name="get_device_calibration_status",
                    parameters={"device_id_or_tag": asset_tag},
                    evidence=[f"Mã tài sản: {asset_tag}", "Từ khóa: kiểm định/hiệu chuẩn"],
                    rationale=f"Khớp chính xác mã {asset_tag} và ý định kiểm tra pháp lý kiểm định."
                )

            return RouteDecision(
                route="LOCAL_EDGE",
                intent="GET_DEVICE",
                confidence=0.99,
                strategy="DETERMINISTIC_EXACT",
                tool_name="get_device_by_asset_tag",
                parameters={"asset_tag": asset_tag},
                evidence=[f"Mã tài sản: {asset_tag}"],
                rationale=f"Khớp chính xác mã định danh thiết bị y tế {asset_tag}."
            )

        # ==================== LAYER 2: AMBIGUITY DETECTION ENGINE ====================
        for pattern, prompt in AMBIGUOUS_PATTERNS:
            if re.search(pattern, q_lower):
                return RouteDecision(
                    route="LOCAL_EDGE",
                    intent="AMBIGUOUS_CLARIFICATION_REQUIRED",
                    confidence=0.50,
                    ambiguity_score=0.85,
                    strategy="AMBIGUITY_GATE",
                    clarification_prompt=prompt,
                    rationale="Câu hỏi ngắn đa nghĩa, yêu cầu làm rõ ý định trước khi chọn công cụ."
                )

        # ==================== LAYER 3: CLINICAL ONTOLOGY MATCH ====================
        # Dashboard / KPIs
        if any(k in q_lower for k in ["tổng quan", "dashboard", "thống kê", "bao nhiêu thiết bị", "tổng số máy", "kpi", "tỷ lệ tuân thủ"]):
            return RouteDecision(
                route="LOCAL_EDGE",
                intent="DASHBOARD_SUMMARY",
                confidence=0.96,
                strategy="ONTOLOGY_KEYWORD",
                tool_name="get_dashboard_summary",
                parameters={},
                evidence=["Từ khóa tổng hợp toàn viện"],
                rationale="Khớp ý định thống kê tổng hợp số liệu quản trị thiết bị."
            )

        # Facility Lookup
        if any(k in q_lower for k in ["khoa", "phòng", "vị trí"]):
            dept_matches = re.findall(r'(?:khoa|phòng)\s+([^\?\.\,\!]+)', q_lower)
            if dept_matches:
                dept_name = dept_matches[0].strip()
                for stop in ["ở đâu", "nào", "ở", "gì", "thế nào"]:
                    if dept_name.endswith(f" {stop}"):
                        dept_name = dept_name[:-len(stop)-1].strip()
                return RouteDecision(
                    route="LOCAL_EDGE",
                    intent="GET_FACILITY",
                    confidence=0.92,
                    strategy="ONTOLOGY_KEYWORD",
                    tool_name="get_facility",
                    parameters={"name_or_code": dept_name},
                    evidence=[f"Khoa phòng: {dept_name}"],
                    rationale=f"Khớp tên khoa phòng y tế: '{dept_name}'."
                )

        # Device Type Matching
        for dev_name in CLINICAL_ONTOLOGY["devices"]:
            if dev_name in q_lower:
                return RouteDecision(
                    route="LOCAL_EDGE",
                    intent="SEARCH_DEVICES",
                    confidence=0.93,
                    strategy="ONTOLOGY_KEYWORD",
                    tool_name="search_devices",
                    parameters={"keyword": dev_name},
                    evidence=[f"Chủng loại thiết bị: {dev_name}"],
                    rationale=f"Khớp danh mục thiết bị y tế: '{dev_name}'."
                )

        # ==================== LAYER 4 & 5: POLICY GATE & CLOUD FRONTIER ====================
        return RouteDecision(
            route="CLOUD_FRONTIER",
            intent="COMPLEX_REASONING_OR_POLICY",
            confidence=0.65,
            strategy="LLM_FALLBACK",
            tool_name=None,
            parameters={"query": q},
            rationale="Câu hỏi yêu cầu suy luận lâm sàng, quy chế SOP hoặc phân tích đa tài liệu."
        )
