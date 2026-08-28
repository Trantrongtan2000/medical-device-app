"""
Agent & BME Copilot Router (HTM V3 AI Gateway)
Tích hợp:
1. POST /api/agent/query (Needle 2 Fast Reflex + Cactus Policy Router + Gemini Fallback)
2. POST /api/agent/mutation/confirm (Two-Phase State-Verified Mutation Confirmation)
3. POST /api/agent/mutation/cancel (Hủy bản nháp thao tác)
4. GET /api/agent/tools (Danh mục Tool Registry chuẩn)
"""
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path

from app.models_core import UIContext, AgentExecutionResult, RouteDecision, TelemetryEvent, ToolResult
from app.needle_agent import NeedleAgent, TOOL_REGISTRY, MutationDraftManager
from app.cactus_router import CactusHybridRouter
from app.ai_services import GeminiAgentService
from app.database import get_db
from app.auth import AuthenticatedUser, UserRole, require_role_enforced
from app.observability import telemetry_collector

router = APIRouter(prefix="/api/agent", tags=["AI Agent & BME Copilot"])

agent_service = NeedleAgent()
gemini_service = GeminiAgentService()


def _record_agent_telemetry(
    result: AgentExecutionResult,
    route_decision: RouteDecision,
    user: AuthenticatedUser,
    tool_result: Optional[ToolResult] = None,
) -> AgentExecutionResult:
    """Record safe route metrics without persisting user prompt contents."""
    telemetry_collector.log_event(
        TelemetryEvent(
            request_id=result.request_id,
            user_id=user.user_id,
            query="[REDACTED]",
            route_decision=route_decision,
            tool_decision=route_decision.tool_call,
            tool_result=tool_result,
            total_latency_ms=result.latency_ms,
        )
    )
    return result

class AgentQueryRequest(BaseModel):
    query: str
    ui_context: Optional[UIContext] = None

class MutationConfirmRequest(BaseModel):
    draft_id: str

@router.get("/tools")
async def list_agent_tools(
    _user: AuthenticatedUser = Depends(require_role_enforced(UserRole.VIEWER)),
):
    """Lấy danh mục Tool Registry chuẩn của Needle 2 (API của AI)"""
    tools_list = []
    for name, t_def in TOOL_REGISTRY.items():
        tools_list.append({
            "name": t_def.name,
            "description": t_def.description,
            "parameters": [p.model_dump() for p in t_def.parameters],
            "risk_level": t_def.risk_level.value,
            "requires_confirmation": t_def.requires_confirmation,
            "allowed_roles": t_def.allowed_roles,
            "timeout_ms": t_def.timeout_ms
        })
    return {
        "total_tools": len(tools_list),
        "tools": tools_list
    }

@router.post("/query", response_model=AgentExecutionResult)
async def process_agent_query(
    req: AgentQueryRequest,
    db = Depends(get_db),
    _user: AuthenticatedUser = Depends(require_role_enforced(UserRole.VIEWER)),
):
    """
    Xử lý câu hỏi / câu lệnh ngôn ngữ tự nhiên:
    1. Cactus Router & Ambiguity Gate
    2. Needle 2 Tool Calling & Execution (< 5ms)
    3. Gemini BME Assistant Fallback khi gặp câu hỏi phức tạp về SOPs/Lâm sàng
    """
    t0 = time.perf_counter()
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Nội dung câu hỏi không được để trống")

    # 1. Evaluate via Cactus Hybrid Router
    route_decision = CactusHybridRouter.route(query, req.ui_context)

    # 2. Ambiguity Prompt
    if route_decision.intent == "AMBIGUOUS_CLARIFICATION":
        latency = (time.perf_counter() - t0) * 1000
        return _record_agent_telemetry(AgentExecutionResult(
            status="CLARIFICATION_REQUIRED",
            route_taken="LOCAL_EDGE",
            confidence=route_decision.confidence,
            response_text=route_decision.clarification_prompt or "Vui lòng làm rõ câu hỏi của bạn.",
            latency_ms=round(latency, 2)
        ), route_decision, _user)

    # 3. Local Edge Tool Calling via Needle
    if route_decision.route == "LOCAL_EDGE" and route_decision.tool_call:
        tool_res = agent_service.executor.execute_tool(route_decision.tool_call)
        latency = (time.perf_counter() - t0) * 1000
        resp_text = agent_service._format_response_text(route_decision.tool_call.tool_name, tool_res)

        draft = None
        if tool_res.data and "draft" in tool_res.data:
            draft_id = tool_res.data["draft"].get("draft_id")
            draft = MutationDraftManager.get_draft(draft_id)
            if draft and draft.owner_user_id is None:
                draft.owner_user_id = _user.user_id

        return _record_agent_telemetry(AgentExecutionResult(
            status="SUCCESS" if tool_res.success else "ERROR",
            route_taken="LOCAL_EDGE",
            confidence=route_decision.confidence,
            tool_name=route_decision.tool_call.tool_name,
            structured_data=tool_res.data,
            action_card=tool_res.action_card,
            provenance=tool_res.provenance,
            response_text=resp_text,
            latency_ms=round(latency, 2),
            requires_confirmation=route_decision.requires_confirmation,
            mutation_draft=draft,
            warnings=tool_res.warnings
        ), route_decision, _user, tool_res)

    # 4. Semantica Graph Reasoning
    if route_decision.route == "SEMANTICA_GRAPH":
        dev_id = req.ui_context.current_device_id if req.ui_context and req.ui_context.current_device_id else None
        if dev_id is None and route_decision.tool_call:
            args = route_decision.tool_call.arguments
            dev_id = agent_service.executor._parse_dev_id(args.get("asset_tag") or args.get("device_id_or_tag") or "")
        if dev_id is None:
            latency = (time.perf_counter() - t0) * 1000
            return _record_agent_telemetry(AgentExecutionResult(
                status="CLARIFICATION_REQUIRED",
                route_taken="SEMANTICA_GRAPH",
                confidence=route_decision.confidence,
                response_text="Vui lòng cung cấp mã tài sản/ID thiết bị hoặc mở chi tiết thiết bị trước khi yêu cầu giải trình Semantica.",
                latency_ms=round(latency, 2),
                warnings=["MISSING_DEVICE_IDENTITY"]
            ), route_decision, _user)
        from app.semantica_engine import semantica_engine
        explain_data = semantica_engine.explain_device(dev_id)
        latency = (time.perf_counter() - t0) * 1000
        return _record_agent_telemetry(AgentExecutionResult(
            status="SUCCESS",
            route_taken="SEMANTICA_GRAPH",
            confidence=0.95,
            structured_data=explain_data,
            response_text=explain_data.get("clinical_summary", "Đã truy xuất mạng tri thức ngữ nghĩa Semantica."),
            latency_ms=round(latency, 2)
        ), route_decision, _user)

    # 5. Cloud Frontier LLM (Gemini BME Assistant with Key Rotation)
    try:
        context_devices = []
        if req.ui_context and req.ui_context.current_device_id:
            row = db.execute("SELECT * FROM devices WHERE id = ?", (req.ui_context.current_device_id,)).fetchone()
            if row:
                context_devices.append(dict(row))

        llm_response = await gemini_service.chat(query, context_devices=context_devices)
        latency = (time.perf_counter() - t0) * 1000
        return _record_agent_telemetry(AgentExecutionResult(
            status="SUCCESS",
            route_taken="CLOUD_FRONTIER",
            confidence=route_decision.confidence,
            response_text=llm_response,
            latency_ms=round(latency, 2),
            engine="Gemini-3.7-Flash-BME"
        ), route_decision, _user)
    except Exception as e:
        latency = (time.perf_counter() - t0) * 1000
        return _record_agent_telemetry(AgentExecutionResult(
            status="FALLBACK",
            route_taken="LOCAL_EDGE",
            confidence=0.7,
            response_text=f"Trợ lý AI BME: Đã ghi nhận câu hỏi '{query}'. Vui lòng tham khảo sổ tay quy trình QT.04/QT.06.",
            latency_ms=round(latency, 2)
        ), route_decision, _user)

@router.post("/mutation/confirm")
async def confirm_mutation(
    req: MutationConfirmRequest,
    _user: AuthenticatedUser = Depends(require_role_enforced(UserRole.BME_ENGINEER)),
):
    """
    Xác nhận thực thi bản nháp thao tác ghi dữ liệu:
    - Re-check trạng thái CSDL thực tế ngay trước khi ghi (Prevent Stale Mutation)
    - Thực thi Atomic Transaction
    - Ghi nhận Audit Event
    """
    db_path = str(Path(__file__).parent.parent / "database" / "devices.db")
    success, message, result_data = MutationDraftManager.execute_draft(
        req.draft_id, db_path, actor_user_id=_user.user_id
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "status": "success",
        "draft_id": req.draft_id,
        "message": message,
        "result": result_data
    }

@router.post("/mutation/cancel")
async def cancel_mutation(
    req: MutationConfirmRequest,
    _user: AuthenticatedUser = Depends(require_role_enforced(UserRole.BME_ENGINEER)),
):
    """Hủy bản nháp thao tác ghi dữ liệu"""
    draft = MutationDraftManager.get_draft(req.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản nháp")
    if draft.owner_user_id and draft.owner_user_id != _user.user_id:
        raise HTTPException(status_code=403, detail="Bản nháp thuộc về người dùng khác")
    if draft.expires_at:
        try:
            expires_at = datetime.fromisoformat(draft.expires_at.replace("Z", "+00:00"))
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) >= expires_at:
                draft.status = "EXPIRED"
                raise HTTPException(status_code=400, detail="Bản nháp đã hết hạn")
        except ValueError:
            draft.status = "EXPIRED"
            raise HTTPException(status_code=400, detail="Bản nháp có thời điểm hết hạn không hợp lệ")
    if draft.status != "PENDING_CONFIRMATION":
        raise HTTPException(status_code=400, detail=f"Bản nháp đang ở trạng thái {draft.status}")
    draft.status = "CANCELLED"
    return {
        "status": "success",
        "draft_id": req.draft_id,
        "message": "Đã hủy bỏ thao tác thành công."
    }
