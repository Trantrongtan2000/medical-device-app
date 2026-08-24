"""
Agent & BME Copilot Router (HTM V3 AI Gateway)
Tích hợp:
1. POST /api/agent/query (Needle 2 Fast Reflex + Cactus Policy Router + Gemini Fallback)
2. POST /api/agent/mutation/confirm (Two-Phase State-Verified Mutation Confirmation)
3. POST /api/agent/mutation/cancel (Hủy bản nháp thao tác)
4. GET /api/agent/tools (Danh mục Tool Registry chuẩn)
"""
import time
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path

from app.models_core import UIContext, AgentExecutionResult, RouteDecision
from app.needle_agent import NeedleAgent, TOOL_REGISTRY, MutationDraftManager
from app.cactus_router import CactusHybridRouter
from app.ai_services import GeminiAgentService
from app.database import get_db

router = APIRouter(prefix="/api/agent", tags=["AI Agent & BME Copilot"])

agent_service = NeedleAgent()
gemini_service = GeminiAgentService()

class AgentQueryRequest(BaseModel):
    query: str
    ui_context: Optional[UIContext] = None

class MutationConfirmRequest(BaseModel):
    draft_id: str

@router.get("/tools")
async def list_agent_tools():
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
async def process_agent_query(req: AgentQueryRequest, db = Depends(get_db)):
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
        return AgentExecutionResult(
            status="CLARIFICATION_REQUIRED",
            route_taken="LOCAL_EDGE",
            confidence=route_decision.confidence,
            response_text=route_decision.clarification_prompt or "Vui lòng làm rõ câu hỏi của bạn.",
            latency_ms=round(latency, 2)
        )

    # 3. Local Edge Tool Calling via Needle
    if route_decision.route == "LOCAL_EDGE" and route_decision.tool_call:
        tool_res = agent_service.executor.execute_tool(route_decision.tool_call)
        latency = (time.perf_counter() - t0) * 1000
        resp_text = agent_service._format_response_text(route_decision.tool_call.tool_name, tool_res)

        draft = None
        if tool_res.data and "draft" in tool_res.data:
            draft_id = tool_res.data["draft"].get("draft_id")
            draft = MutationDraftManager.get_draft(draft_id)

        return AgentExecutionResult(
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
        )

    # 4. Semantica Graph Reasoning
    if route_decision.route == "SEMANTICA_GRAPH":
        dev_id = 1
        if req.ui_context and req.ui_context.current_device_id:
            dev_id = req.ui_context.current_device_id
        from app.semantica_engine import semantica_engine
        explain_data = semantica_engine.explain_device_status(dev_id)
        latency = (time.perf_counter() - t0) * 1000
        return AgentExecutionResult(
            status="SUCCESS",
            route_taken="SEMANTICA_GRAPH",
            confidence=0.95,
            structured_data=explain_data,
            response_text=explain_data.get("clinical_summary", "Đã truy xuất mạng tri thức ngữ nghĩa Semantica."),
            latency_ms=round(latency, 2)
        )

    # 5. Cloud Frontier LLM (Gemini BME Assistant with Key Rotation)
    try:
        context_devices = []
        if req.ui_context and req.ui_context.current_device_id:
            row = db.execute("SELECT * FROM devices WHERE id = ?", (req.ui_context.current_device_id,)).fetchone()
            if row:
                context_devices.append(dict(row))

        llm_response = await gemini_service.chat(query, context_devices=context_devices)
        latency = (time.perf_counter() - t0) * 1000
        return AgentExecutionResult(
            status="SUCCESS",
            route_taken="CLOUD_FRONTIER",
            confidence=route_decision.confidence,
            response_text=llm_response,
            latency_ms=round(latency, 2),
            engine="Gemini-3.7-Flash-BME"
        )
    except Exception as e:
        latency = (time.perf_counter() - t0) * 1000
        return AgentExecutionResult(
            status="FALLBACK",
            route_taken="LOCAL_EDGE",
            confidence=0.7,
            response_text=f"Trợ lý AI BME: Đã ghi nhận câu hỏi '{query}'. Vui lòng tham khảo sổ tay quy trình QT.04/QT.06.",
            latency_ms=round(latency, 2)
        )

@router.post("/mutation/confirm")
async def confirm_mutation(req: MutationConfirmRequest):
    """
    Xác nhận thực thi bản nháp thao tác ghi dữ liệu:
    - Re-check trạng thái CSDL thực tế ngay trước khi ghi (Prevent Stale Mutation)
    - Thực thi Atomic Transaction
    - Ghi nhận Audit Event
    """
    db_path = str(Path(__file__).parent.parent / "database" / "devices.db")
    success, message, result_data = MutationDraftManager.execute_draft(req.draft_id, db_path)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "status": "success",
        "draft_id": req.draft_id,
        "message": message,
        "result": result_data
    }

@router.post("/mutation/cancel")
async def cancel_mutation(req: MutationConfirmRequest):
    """Hủy bản nháp thao tác ghi dữ liệu"""
    draft = MutationDraftManager.get_draft(req.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản nháp")
    draft.status = "CANCELLED"
    return {
        "status": "success",
        "draft_id": req.draft_id,
        "message": "Đã hủy bỏ thao tác thành công."
    }
