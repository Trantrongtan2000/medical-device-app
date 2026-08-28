"""
Canonical Data Contracts & Schemas cho HTM V3 Next-Gen BME Copilot Runtime
Quy chuẩn hóa toàn bộ:
- ToolDefinition, ToolCall, ToolResult (với request_id, tool_call_id, warnings, error_code)
- Two-Phase State-Verified MutationDraft kèm State Versioning
- UIContext Awareness
- Structured Provenance (W3C PROV-O)
- ActionCard Schema-Driven UI Contracts
"""
from __future__ import annotations
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone

class RiskLevel(str, Enum):
    READ = "READ"
    LOW_WRITE = "LOW_WRITE"
    HIGH_WRITE = "HIGH_WRITE"
    DESTRUCTIVE = "DESTRUCTIVE"
    PRIVILEGED = "PRIVILEGED"

class TrustLevel(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"        # Dữ liệu đối chiếu CSDL có chứng nhận/ID thực
    CALCULATED_DATA = "CALCULATED_DATA"    # Dữ liệu tính toán từ SQL aggregation (COUNT, SUM, AVG)
    RAW_OCR = "RAW_OCR"                    # Dữ liệu trích xuất OCR chưa qua kiểm chứng
    VERIFIED_EVIDENCE = "VERIFIED_EVIDENCE"# Bằng chứng trích xuất từ PDF gốc (Evidence Ledger)
    INFERRED = "INFERRED"                  # Suy luận logic từ LLM Frontier
    PROPOSAL = "PROPOSAL"                  # Đề xuất thay đổi (cần người dùng phê duyệt)
    UNVERIFIED = "UNVERIFIED"              # Dữ liệu chưa xác thực nguồn gốc

class AssetLifecycleState(str, Enum):
    """Trạng thái Vòng đời Thiết bị Y tế (HTM / CMMS Lifecycle)"""
    PROCUREMENT = "PROCUREMENT"             # Mua sắm
    RECEIPT = "RECEIPT"                     # Tiếp nhận kho
    ACCEPTANCE = "ACCEPTANCE"               # Nghiệm thu kỹ thuật ban đầu
    INSTALLATION = "INSTALLATION"           # Lắp đặt tại khoa phòng
    COMMISSIONING = "COMMISSIONING"         # Chạy thử nghiệm
    IN_SERVICE = "IN_SERVICE"               # Đang hoạt động khám chữa bệnh
    PREVENTIVE_MAINTENANCE = "PREVENTIVE_MAINTENANCE" # Đang bảo trì phòng ngừa (PM)
    CORRECTIVE_MAINTENANCE = "CORRECTIVE_MAINTENANCE" # Đang sửa chữa khắc phục (CM)
    CALIBRATION = "CALIBRATION"             # Đang kiểm định / hiệu chuẩn
    CALIBRATION_EXPIRED = "CALIBRATION_EXPIRED" # Quá hạn kiểm định (Khóa an toàn)
    QUARANTINED = "QUARANTINED"             # Cách ly / Tạm ngưng sử dụng
    RECALLED = "RECALLED"                   # Thu hồi kỹ thuật từ nhà sản xuất
    TRANSFER = "TRANSFER"                   # Đang điều chuyển khoa phòng
    DECOMMISSIONED = "DECOMMISSIONED"       # Ngừng hoạt động / Thanh lý

class ActionCardType(str, Enum):
    DEVICE_CARD = "DEVICE_CARD"
    DOCUMENT_CARD = "DOCUMENT_CARD"
    CALIBRATION_CARD = "CALIBRATION_CARD"
    EVIDENCE_CARD = "EVIDENCE_CARD"
    LIFECYCLE_CARD = "LIFECYCLE_CARD"
    MUTATION_CONFIRM_CARD = "MUTATION_CONFIRM_CARD"
    SUMMARY_METRICS_CARD = "SUMMARY_METRICS_CARD"
    CLARIFICATION_CARD = "CLARIFICATION_CARD"

class UIContext(BaseModel):
    """Ngữ cảnh giao diện người dùng đang tương tác (Contextual but Server-Verified)"""
    current_page: Optional[str] = "dashboard"    # dashboard | device_detail | transfers | inspections | reports
    current_device_id: Optional[int] = None
    current_asset_tag: Optional[str] = None
    current_facility_id: Optional[int] = None
    current_document_id: Optional[int] = None
    current_workflow: Optional[str] = "device_management"
    selected_items: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class ProvenanceRecord(BaseModel):
    """Cấu trúc nguồn gốc vết quyết định & Bằng chứng xác thực (W3C PROV-O Standard)"""
    source_type: str = "sqlite"            # sqlite | markdown | pdf | sop_doc | user_input
    source_id: str = "database/devices.db"
    record_table: Optional[str] = None
    record_id: Optional[str] = None
    field_name: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_snippet: Optional[str] = None
    evidence_pdf_url: Optional[str] = None
    evidence_md_url: Optional[str] = None
    is_authoritative: bool = False
    model_config = ConfigDict(from_attributes=True)

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None

class ToolDefinition(BaseModel):
    """Hợp đồng API của AI (AI Tool Contract)"""
    name: str
    description: str
    parameters: List[ToolParameter] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.READ
    requires_confirmation: bool = False
    allowed_roles: List[str] = Field(default_factory=lambda: ["viewer", "nurse", "bme_engineer", "bme_admin"])
    audit_event: Optional[str] = None
    timeout_ms: int = 2000
    model_config = ConfigDict(from_attributes=True)

class ToolCall(BaseModel):
    """Đề xuất gọi Tool chuẩn từ Needle 2 (ToolCall Contract)"""
    tool_call_id: str = Field(default_factory=lambda: f"CALL-{uuid.uuid4().hex[:8].upper()}")
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    risk_level: RiskLevel = RiskLevel.READ
    requires_confirmation: bool = False
    rationale: str = ""
    model_config = ConfigDict(from_attributes=True)

# Backward compatibility alias
ToolDecision = ToolCall

class ActionCardButton(BaseModel):
    id: str
    label: str
    action_type: str                       # CLIENT_MODAL | API_MUTATION_CONFIRM | API_MUTATION_CANCEL | NAVIGATE | STREAM_PDF
    endpoint_or_fn: str
    variant: str = "primary"               # primary | secondary | warning | danger | outline-secondary
    model_config = ConfigDict(from_attributes=True)

class ActionCard(BaseModel):
    """Schema-Driven Action Card (Backend API Contract cho UI)"""
    card_type: ActionCardType
    title: str
    subtitle: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    actions: List[ActionCardButton] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class ToolResult(BaseModel):
    """Kết quả thực thi Tool với đầy đủ audit fields"""
    request_id: Optional[str] = None
    tool_call_id: Optional[str] = None
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None       # NOT_FOUND | VALIDATION_ERROR | STALE_STATE | TIMEOUT | DB_ERROR
    warnings: List[str] = Field(default_factory=list)
    provenance: Optional[ProvenanceRecord] = None
    trust_level: TrustLevel = TrustLevel.UNVERIFIED
    action_card: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_config = ConfigDict(from_attributes=True)

class RouteDecision(BaseModel):
    route: str                             # LOCAL_EDGE | CLOUD_FRONTIER | SEMANTICA_GRAPH
    intent: str
    confidence: float
    ambiguity_score: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    strategy: str = "DETERMINISTIC_EXACT"  # DETERMINISTIC_EXACT | ONTOLOGY_KEYWORD | NEEDLE_TOOLCALL | LLM_FALLBACK
    policy_flags: List[str] = Field(default_factory=list)
    clarification_prompt: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    rationale: str = ""
    requires_confirmation: bool = False
    model_config = ConfigDict(from_attributes=True)

    @property
    def tool_name(self) -> Optional[str]:
        return self.tool_call.tool_name if self.tool_call else None

    @property
    def parameters(self) -> Dict[str, Any]:
        return self.tool_call.arguments if self.tool_call else {}

class MutationDraft(BaseModel):
    """Bản nháp thao tác ghi kèm State Versioning (Two-Phase State Check)"""
    draft_id: str
    action_type: str                       # TRANSFER_DEVICE | CREATE_WORK_ORDER | UPDATE_STATUS
    device_id: int
    asset_tag: str
    initial_state: Dict[str, Any]          # Snapshot trạng thái tại thời điểm tạo draft
    state_version: int = 1                 # Phiên bản trạng thái để chống stale confirmation
    proposed_payload: Dict[str, Any]       # Dữ liệu đề xuất thay đổi
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    owner_user_id: Optional[str] = None
    owner_session_id: Optional[str] = None
    status: str = "PENDING_CONFIRMATION"   # PENDING_CONFIRMATION | EXECUTING | EXECUTED | CANCELLED | EXPIRED | STALE_REJECTED
    model_config = ConfigDict(from_attributes=True)

class AgentExecutionResult(BaseModel):
    request_id: str = Field(default_factory=lambda: f"REQ-{uuid.uuid4().hex[:8].upper()}")
    status: str                            # SUCCESS | ERROR | CLARIFICATION_REQUIRED | ESCALATED_TO_CLOUD
    route_taken: str                       # LOCAL_EDGE | CLOUD_FRONTIER | SEMANTICA_GRAPH
    confidence: float
    tool_name: Optional[str] = None
    structured_data: Optional[Any] = None
    action_card: Optional[Dict[str, Any]] = None
    provenance: Optional[ProvenanceRecord] = None
    response_text: str
    latency_ms: float
    engine: str = "Needle-2-Cactus-Core"
    requires_confirmation: bool = False
    mutation_draft: Optional[MutationDraft] = None
    warnings: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class TelemetryEvent(BaseModel):
    request_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    query: str
    route_decision: RouteDecision
    tool_decision: Optional[ToolCall] = None
    tool_result: Optional[ToolResult] = None
    total_latency_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_config = ConfigDict(from_attributes=True)

class EvidenceRecord(BaseModel):
    """Bản ghi chứng cứ kiểm toán (Evidence Ledger Record)"""
    id: Optional[int] = None
    device_id: int
    field_name: str
    raw_ocr_value: Optional[str] = None
    verified_value: str
    source_pdf: str
    source_page: int = 1
    exact_text_snippet: Optional[str] = None
    pdf_sha256: Optional[str] = None
    verification_method: str = "GEMINI_3_7_FLASH_VISION"
    trust_level: TrustLevel = TrustLevel.VERIFIED_EVIDENCE
    verified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_config = ConfigDict(from_attributes=True)

class AssetLifecycleEvent(BaseModel):
    """Sự kiện Vòng đời Thiết bị (Append-Only Event Sourcing)"""
    id: Optional[int] = None
    idempotency_key: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:12].upper()}")
    device_id: int
    event_type: AssetLifecycleState
    event_date: str
    performed_by: Optional[str] = "Phòng TTBYT BME"
    certificate_or_doc_no: Optional[str] = None
    safety_check_passed: bool = True
    metadata_json: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_config = ConfigDict(from_attributes=True)

class ClinicalSafetyValidator:
    """Khóa an toàn lâm sàng (Clinical Safety Interlock & State Transition Rules)"""
    
    ALLOWED_TRANSITIONS: Dict[AssetLifecycleState, List[AssetLifecycleState]] = {
        AssetLifecycleState.PROCUREMENT: [AssetLifecycleState.RECEIPT, AssetLifecycleState.DECOMMISSIONED],
        AssetLifecycleState.RECEIPT: [AssetLifecycleState.ACCEPTANCE, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.ACCEPTANCE: [AssetLifecycleState.INSTALLATION, AssetLifecycleState.CALIBRATION, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.INSTALLATION: [AssetLifecycleState.COMMISSIONING, AssetLifecycleState.CALIBRATION, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.COMMISSIONING: [AssetLifecycleState.CALIBRATION, AssetLifecycleState.IN_SERVICE, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.CALIBRATION: [AssetLifecycleState.IN_SERVICE, AssetLifecycleState.CALIBRATION_EXPIRED, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.IN_SERVICE: [
            AssetLifecycleState.PREVENTIVE_MAINTENANCE, 
            AssetLifecycleState.CORRECTIVE_MAINTENANCE, 
            AssetLifecycleState.CALIBRATION, 
            AssetLifecycleState.CALIBRATION_EXPIRED, 
            AssetLifecycleState.QUARANTINED, 
            AssetLifecycleState.RECALLED, 
            AssetLifecycleState.TRANSFER
        ],
        AssetLifecycleState.PREVENTIVE_MAINTENANCE: [AssetLifecycleState.IN_SERVICE, AssetLifecycleState.CALIBRATION, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.CORRECTIVE_MAINTENANCE: [AssetLifecycleState.CALIBRATION, AssetLifecycleState.IN_SERVICE, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.CALIBRATION_EXPIRED: [AssetLifecycleState.CALIBRATION, AssetLifecycleState.QUARANTINED],
        AssetLifecycleState.QUARANTINED: [AssetLifecycleState.CORRECTIVE_MAINTENANCE, AssetLifecycleState.CALIBRATION, AssetLifecycleState.DECOMMISSIONED],
        AssetLifecycleState.RECALLED: [AssetLifecycleState.QUARANTINED, AssetLifecycleState.DECOMMISSIONED],
        AssetLifecycleState.TRANSFER: [AssetLifecycleState.ACCEPTANCE, AssetLifecycleState.IN_SERVICE],
        AssetLifecycleState.DECOMMISSIONED: []
    }

    @classmethod
    def can_transition(cls, from_state: AssetLifecycleState, to_state: AssetLifecycleState) -> Tuple[bool, Optional[str]]:
        """Kiểm tra tính hợp lệ và an toàn của bước chuyển trạng thái"""
        if to_state == from_state:
            return True, None
            
        allowed = cls.ALLOWED_TRANSITIONS.get(from_state, [])
        if to_state not in allowed:
            return False, f"Chặn chuyển trạng thái phi logic: Không thể chuyển từ {from_state.value} -> {to_state.value}"
            
        # Hard-lock rule: Chặn chuyển sang IN_SERVICE nếu quá hạn hoặc cách ly
        if to_state == AssetLifecycleState.IN_SERVICE:
            if from_state in (AssetLifecycleState.CALIBRATION_EXPIRED, AssetLifecycleState.QUARANTINED, AssetLifecycleState.RECALLED):
                return False, f"Khóa an toàn lâm sàng (Safety Interlock): Thiết bị đang ở trạng thái {from_state.value}, bắt buộc phải qua Kiểm định/Đánh giá kỹ thuật trước khi đưa vào khám chữa bệnh!"
                
        return True, None

