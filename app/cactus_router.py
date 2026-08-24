"""
Cactus Policy Router & Safety Gate Engine (HTM V3 Policy Layer)
Quy chuẩn hóa:
1. Đánh giá chính sách an toàn (Policy Enforcement & Risk Level Validation)
2. Phân luồng 3 mức (Local Edge Tool -> Semantica Graph/Wiki -> Cloud Gemini)
3. Hàng rào xác nhận thao tác ghi dữ liệu (Two-Phase State-Verified Safety Gate)
"""
from __future__ import annotations
import re
from typing import Optional, List, Tuple, Dict, Any
from app.models_core import RouteDecision, RiskLevel, UIContext, ToolCall
from app.needle_agent import NeedleParser, TOOL_REGISTRY, MutationDraftManager

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
    (r"^(kiểm tra|check)\s+(máy|thiết bị)$", "Bạn muốn: (1) Xem hạn kiểm định, (2) Xem tệp PDF minh chứng gốc, hay (3) Xem thông số kỹ thuật chi tiết?"),
    (r"^(báo cáo|thống kê)$", "Bạn muốn: (1) Báo cáo KPI toàn viện, (2) Danh sách máy sắp đến hạn kiểm định, hay (3) Thống kê phân bổ rủi ro A/B/C/D?"),
    (r"^(xem hồ sơ|tra cứu)$", "Vui lòng cung cấp mã tài sản (VD: BVQ7-TTB-00193) hoặc chọn thiết bị đang hiển thị trên màn hình.")
]

class CactusHybridRouter:
    """Cactus Policy Router với 3 Tầng Phân Luồng & Hàng Rào An Toàn"""

    @classmethod
    def route(cls, query: str, ui_context: Optional[UIContext] = None) -> RouteDecision:
        q = query.strip()
        q_lower = q.lower()

        # ==================== LAYER 1: AMBIGUITY CLARIFICATION GATE ====================
        for pattern, clarification in AMBIGUOUS_PATTERNS:
            if re.match(pattern, q_lower):
                return RouteDecision(
                    route="LOCAL_EDGE",
                    intent="AMBIGUOUS_CLARIFICATION",
                    confidence=0.99,
                    ambiguity_score=0.95,
                    strategy="DETERMINISTIC_EXACT",
                    clarification_prompt=clarification,
                    rationale="Câu hỏi quá ngắn hoặc thiếu đối tượng cụ thể. Cần làm rõ ý định trước khi xử lý."
                )

        # ==================== LAYER 2: NEEDLE INTENT & TOOLCALL GENERATION ====================
        needle_decision = NeedleParser.parse_intent(query, ui_context)

        # ==================== LAYER 3: CACTUS POLICY & SAFETY GATE ENFORCEMENT ====================
        if needle_decision.tool_call:
            tool_name = needle_decision.tool_call.tool_name
            tool_def = TOOL_REGISTRY.get(tool_name)

            if tool_def:
                # Enforce Risk Level & Confirmation Policy
                needle_decision.tool_call.risk_level = tool_def.risk_level
                needle_decision.tool_call.requires_confirmation = tool_def.requires_confirmation
                needle_decision.requires_confirmation = tool_def.requires_confirmation

                # Mutation verbs strict safety policy
                if tool_def.risk_level in [RiskLevel.HIGH_WRITE, RiskLevel.DESTRUCTIVE]:
                    needle_decision.policy_flags.append("POLICY_MUTATION_GATED")
                    needle_decision.policy_flags.append("REQUIRES_HUMAN_CONFIRMATION")
                    needle_decision.policy_flags.append(f"RISK_{tool_def.risk_level.value}")

        # Check for Semantic Explainability Queries (Route to Semantica Graph)
        if any(k in q_lower for k in ["tại sao", "căn cứ", "nguyên nhân", "phân loại theo quy định nào", "luật", "thông tư"]):
            needle_decision.route = "SEMANTICA_GRAPH"
            needle_decision.strategy = "ONTOLOGY_KEYWORD"
            needle_decision.rationale = "Yêu cầu giải trình căn cứ pháp lý và đồ thị tri thức ngữ nghĩa (Semantica Engine)."

        return needle_decision
