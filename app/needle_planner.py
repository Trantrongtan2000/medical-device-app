"""
Needle 2 Execution Planner & Circuit Breaker Engine
Thực thi kế hoạch an toàn, chống cascade failure và tạo Provenance Traceability.
"""
import time
import sqlite3
from typing import Dict, Any, Optional, Tuple
from app.models_core import (
    RouteDecision, ToolDecision, ToolResult, ProvenanceRecord, TrustLevel, RiskLevel
)
from app.needle_agent import SafeToolExecutor

class CircuitBreaker:
    """Ngắt mạch tự động khi phát hiện lỗi hệ thống liên tiếp"""
    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout_seconds
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED | OPEN | HALF_OPEN

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN allows a trial call

class NeedleExecutionPlanner:
    """Bộ lập kế hoạch và thực thi công cụ Needle 2 chuẩn Production"""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.executor = SafeToolExecutor()

    def plan_and_execute(self, route_decision: RouteDecision, db: sqlite3.Connection) -> Tuple[ToolDecision, ToolResult]:
        start_time = time.time()

        # 1. Kiểm tra Circuit Breaker
        if not self.circuit_breaker.can_execute():
            latency = (time.time() - start_time) * 1000
            decision = ToolDecision(
                tool_name=route_decision.tool_name or "unknown",
                arguments=route_decision.parameters,
                confidence=0.0,
                risk_level=RiskLevel.READ,
                rationale="Circuit Breaker đang mở do lỗi hệ thống liên tiếp."
            )
            result = ToolResult(
                success=False,
                error="Hệ thống tạm thời ngắt mạch để bảo vệ CSDL. Vui lòng thử lại sau 30 giây.",
                trust_level=TrustLevel.UNVERIFIED,
                latency_ms=latency
            )
            return decision, result

        # 2. Xử lý Mutation Gate
        if route_decision.requires_confirmation:
            latency = (time.time() - start_time) * 1000
            decision = ToolDecision(
                tool_name=route_decision.tool_name or "mutation_gate",
                arguments=route_decision.parameters,
                confidence=route_decision.confidence,
                risk_level=RiskLevel.HIGH_WRITE,
                requires_confirmation=True,
                rationale="Yêu cầu xác nhận từ kỹ sư BME trước khi thực hiện ghi dữ liệu."
            )
            result = ToolResult(
                success=True,
                data={"status": "AWAITING_CONFIRMATION", "payload": route_decision.parameters},
                trust_level=TrustLevel.PROPOSAL,
                latency_ms=latency
            )
            return decision, result

        # 3. Thực thi Read-Only Tools
        tool_name = route_decision.tool_name or "search_devices"
        params = route_decision.parameters

        tool_decision = ToolDecision(
            tool_name=tool_name,
            arguments=params,
            confidence=route_decision.confidence,
            risk_level=RiskLevel.READ,
            rationale=route_decision.rationale
        )

        try:
            raw_data, formatted_text = self.executor.execute_tool(tool_name, params, db)
            latency = (time.time() - start_time) * 1000
            self.circuit_breaker.record_success()

            # Xác định Trust Level & Provenance Record
            if tool_name == "get_dashboard_summary":
                trust = TrustLevel.CALCULATED_DATA
                prov = ProvenanceRecord(
                    source_type="SQLITE_MASTER",
                    source_id="devices_and_status_summary",
                    record_table="device_status_summary",
                    evidence_snippet="COUNT aggregation trên 1.211 thiết bị",
                    is_authoritative=True
                )
            elif tool_name in ["get_device_by_asset_tag", "get_device_calibration_status"]:
                trust = TrustLevel.VERIFIED_FACT if raw_data else TrustLevel.UNVERIFIED
                dev_id = str(raw_data.get("id")) if isinstance(raw_data, dict) else "unknown"
                prov = ProvenanceRecord(
                    source_type="SQLITE_MASTER",
                    source_id=f"device_id_{dev_id}",
                    record_table="devices",
                    evidence_snippet=f"Serial: {raw_data.get('serial_no') if isinstance(raw_data, dict) else 'N/A'}",
                    is_authoritative=True
                )
            else:
                trust = TrustLevel.VERIFIED_FACT if raw_data else TrustLevel.UNVERIFIED
                prov = ProvenanceRecord(
                    source_type="SQLITE_MASTER",
                    source_id=tool_name,
                    is_authoritative=False
                )

            tool_result = ToolResult(
                success=True,
                data={"raw": raw_data, "formatted_text": formatted_text},
                provenance=prov,
                trust_level=trust,
                latency_ms=latency
            )
            return tool_decision, tool_result

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.circuit_breaker.record_failure()
            tool_result = ToolResult(
                success=False,
                error=f"Lỗi thực thi công cụ {tool_name}: {str(e)}",
                trust_level=TrustLevel.UNVERIFIED,
                latency_ms=latency
            )
            return tool_decision, tool_result

# Global Instance
needle_planner = NeedleExecutionPlanner()
