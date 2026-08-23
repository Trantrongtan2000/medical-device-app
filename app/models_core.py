"""
Canonical Data Contracts & Schemas cho NOOA Nanobot Runtime
Quy chuẩn hóa toàn bộ cấu trúc dữ liệu: Routing, Tool Execution, Risk & Provenance.
"""
from __future__ import annotations
from enum import Enum
from typing import Dict, Any, List, Optional
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
    INFERRED = "INFERRED"                  # Suy luận logic từ LLM Frontier
    PROPOSAL = "PROPOSAL"                  # Đề xuất thay đổi (cần người dùng phê duyệt)
    UNVERIFIED = "UNVERIFIED"              # Dữ liệu chưa xác thực nguồn gốc

class ProvenanceRecord(BaseModel):
    source_type: str = "SQLITE_MASTER"     # SQLITE_MASTER | MISTRAL_OCR | SOP_DOC | USER_INPUT
    source_id: str
    record_table: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_snippet: Optional[str] = None
    is_authoritative: bool = False
    model_config = ConfigDict(from_attributes=True)

class RouteDecision(BaseModel):
    route: str                             # LOCAL_EDGE | CLOUD_FRONTIER
    intent: str
    confidence: float
    ambiguity_score: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    strategy: str = "DETERMINISTIC_EXACT"  # DETERMINISTIC_EXACT | ONTOLOGY_KEYWORD | SEMANTIC_SIMILARITY | LLM_FALLBACK
    policy_flags: List[str] = Field(default_factory=list)
    clarification_prompt: Optional[str] = None
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""
    requires_confirmation: bool = False
    model_config = ConfigDict(from_attributes=True)

class ToolDecision(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    confidence: float
    risk_level: RiskLevel = RiskLevel.READ
    requires_confirmation: bool = False
    rationale: str = ""
    model_config = ConfigDict(from_attributes=True)

class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    provenance: Optional[ProvenanceRecord] = None
    trust_level: TrustLevel = TrustLevel.UNVERIFIED
    latency_ms: float = 0.0
    model_config = ConfigDict(from_attributes=True)

class TelemetryEvent(BaseModel):
    request_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    query: str
    route_decision: RouteDecision
    tool_decision: Optional[ToolDecision] = None
    tool_result: Optional[ToolResult] = None
    total_latency_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_config = ConfigDict(from_attributes=True)
