"""
Comprehensive Tests for Needle 2 Agent & Cactus Policy Engine (HTM V3)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.needle_agent import NeedleAgent, NeedleParser, ToolExecutor, MutationDraftManager, TOOL_REGISTRY
from app.models_core import UIContext, RiskLevel

@pytest.fixture
def client():
    return TestClient(app)

# 1. Router Intent & Confidence Unit Tests
def test_router_asset_tag_lookup():
    decision = NeedleParser.parse_intent("Tra cứu máy BVQ7-TTB-00001 đang ở đâu?")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_DEVICE"
    assert decision.confidence >= 0.95
    assert decision.tool_call.tool_name == "get_device_by_asset_tag"
    assert decision.tool_call.arguments["asset_tag"] == "BVQ7-TTB-00001"

def test_router_calibration_status():
    decision = NeedleParser.parse_intent("Kiểm tra hạn kiểm định của máy #00002")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "CHECK_CALIBRATION"
    assert decision.confidence >= 0.95
    assert decision.tool_call.tool_name == "get_calibration_status"
    assert decision.tool_call.arguments["device_id_or_tag"] == "BVQ7-TTB-00002"

def test_router_pdf_documents():
    decision = NeedleParser.parse_intent("Cho tôi xem hồ sơ PDF gốc của máy BVQ7-TTB-00193")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_DEVICE_PDF_DOCUMENTS"
    assert decision.tool_call.tool_name == "get_device_pdf_documents"
    assert decision.tool_call.arguments["device_id_or_tag"] == "BVQ7-TTB-00193"

def test_router_upcoming_calibrations():
    decision = NeedleParser.parse_intent("Danh sách thiết bị sắp hết hạn kiểm định trong 60 ngày")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_UPCOMING_CALIBRATIONS"
    assert decision.tool_call.tool_name == "get_upcoming_calibrations"
    assert decision.tool_call.arguments["days"] == 60

def test_router_dashboard_summary():
    decision = NeedleParser.parse_intent("Cho tôi xem thống kê tổng quan toàn viện")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "DASHBOARD_SUMMARY"
    assert decision.tool_call.tool_name == "get_dashboard_summary"
    assert decision.confidence >= 0.90

def test_router_search_device_by_keyword():
    decision = NeedleParser.parse_intent("Tìm danh sách máy thở trong bệnh viện")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "SEARCH_DEVICES"
    assert decision.tool_call.tool_name == "search_devices"
    assert "máy thở" in decision.tool_call.arguments["keyword"]

def test_router_facility_lookup_unicode():
    decision = NeedleParser.parse_intent("Tra cứu thông tin Khoa Cấp Cứu ở đâu?")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_FACILITY"
    assert decision.tool_call.tool_name == "get_facility"
    assert "cấp cứu" in decision.tool_call.arguments["name_or_code"].lower()

def test_router_mutation_safety_gate():
    decision = NeedleParser.parse_intent("Điều chuyển máy BVQ7-TTB-00001 sang Khoa Ngoại")
    assert decision.route == "LOCAL_EDGE"
    assert decision.requires_confirmation is True
    assert decision.tool_call.tool_name == "transfer_device_draft"
    assert decision.tool_call.risk_level == RiskLevel.HIGH_WRITE

def test_ui_context_awareness():
    """Kiểm tra nhận thức ngữ cảnh màn hình khi người dùng không gõ lại mã máy"""
    ctx = UIContext(current_page="device_detail", current_asset_tag="BVQ7-TTB-00193", current_device_id=193)
    decision = NeedleParser.parse_intent("Máy này còn hạn kiểm định không?", ui_context=ctx)
    assert decision.tool_call.tool_name == "get_calibration_status"
    assert decision.tool_call.arguments["device_id_or_tag"] == "BVQ7-TTB-00193"

# 2. Tool Execution & Action Card Tests
def test_executor_get_device():
    executor = ToolExecutor()
    from app.models_core import ToolCall
    call = ToolCall(tool_name="get_device_by_asset_tag", arguments={"asset_tag": "BVQ7-TTB-00001"})
    res = executor.execute_tool(call)
    assert res.success is True
    assert res.data["id"] == 1
    assert res.action_card is not None
    assert res.action_card["card_type"] == "DEVICE_CARD"
    assert res.provenance.source_type == "sqlite"

def test_executor_get_pdf_documents():
    executor = ToolExecutor()
    from app.models_core import ToolCall
    call = ToolCall(tool_name="get_device_pdf_documents", arguments={"device_id_or_tag": "BVQ7-TTB-00193"})
    res = executor.execute_tool(call)
    assert res.success is True
    assert "documents" in res.data
    assert res.action_card["card_type"] == "DOCUMENT_CARD"

def test_two_phase_mutation_workflow():
    """Kiểm tra quy trình tạo bản nháp và thực thi xác nhận 2 bước kèm State Versioning"""
    executor = ToolExecutor()
    from app.models_core import ToolCall
    # 1. Create Draft
    call = ToolCall(tool_name="transfer_device_draft", arguments={"device_id_or_tag": "BVQ7-TTB-00001", "target_facility": "Cấp cứu"})
    res = executor.execute_tool(call)
    assert res.success is True
    draft_id = res.data["draft"]["draft_id"]
    assert draft_id.startswith("DRAFT-")
    assert res.action_card["card_type"] == "MUTATION_CONFIRM_CARD"

    # 2. Confirm Draft
    from pathlib import Path
    db_p = str(Path(__file__).parent.parent / "database" / "devices.db")
    success, msg, pld = MutationDraftManager.execute_draft(draft_id, db_p)
    assert success is True
    assert "thực thi" in msg.lower()

# 3. HTTP API Endpoint Tests
def test_api_agent_tools_list(client):
    res = client.get("/api/agent/tools")
    assert res.status_code == 200
    data = res.json()
    assert data["total_tools"] >= 10
    tool_names = [t["name"] for t in data["tools"]]
    assert "get_device_by_asset_tag" in tool_names
    assert "get_device_pdf_documents" in tool_names
    assert "get_upcoming_calibrations" in tool_names
    assert "transfer_device_draft" in tool_names

def test_api_agent_query_local_edge(client):
    res = client.post("/api/agent/query", json={"query": "Tra cứu máy BVQ7-TTB-00001"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["route_taken"] == "LOCAL_EDGE"
    assert data["tool_name"] == "get_device_by_asset_tag"
    assert data["action_card"] is not None
    assert data["latency_ms"] < 200.0

def test_api_agent_mutation_confirm_flow(client):
    # Step 1: Create draft via Query
    res1 = client.post("/api/agent/query", json={"query": "Báo hỏng máy BVQ7-TTB-00001 bị nứt màn hình"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["requires_confirmation"] is True
    assert data1["action_card"]["card_type"] == "MUTATION_CONFIRM_CARD"
    draft_id = data1["mutation_draft"]["draft_id"]

    # Step 2: Confirm Draft
    res2 = client.post("/api/agent/mutation/confirm", json={"draft_id": draft_id})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"

def test_api_agent_mutation_cancel_flow(client):
    # Step 1: Create draft
    res1 = client.post("/api/agent/query", json={"query": "Điều chuyển máy BVQ7-TTB-00001 sang Cấp cứu"})
    assert res1.status_code == 200
    draft_id = res1.json()["mutation_draft"]["draft_id"]

    # Step 2: Cancel Draft
    res2 = client.post("/api/agent/mutation/cancel", json={"draft_id": draft_id})
    assert res2.status_code == 200
    assert res2.json()["status"] == "success"

