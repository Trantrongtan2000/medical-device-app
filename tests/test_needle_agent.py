"""
Comprehensive Tests for Needle 2 Agent & Cactus Policy Engine (HTM V3)
"""
import sqlite3

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


def test_parser_no_default_device_for_context_dependent_read_intents():
    """Thiếu mã máy/ngữ cảnh phải hỏi lại, không tự fallback BVQ7-TTB-00001."""
    for query in [
        "Cho tôi xem hồ sơ PDF gốc của máy này",
        "Máy này còn hạn kiểm định không?",
    ]:
        decision = NeedleParser.parse_intent(query)
        assert decision.intent == "AMBIGUOUS_CLARIFICATION"
        assert decision.tool_call is None
        assert "BVQ7-TTB-00001" not in str(decision.model_dump())


def test_parser_no_default_device_for_mutation_without_identity():
    """Mutation thiếu định danh thiết bị phải fail closed và vẫn đánh dấu cần xác nhận người dùng."""
    from app.cactus_router import CactusHybridRouter

    decision = CactusHybridRouter.route("Điều chuyển máy sang Khoa Cấp Cứu")
    assert decision.intent == "AMBIGUOUS_CLARIFICATION"
    assert decision.tool_call is None
    assert decision.requires_confirmation is True
    assert "REQUIRES_HUMAN_CONFIRMATION" in decision.policy_flags
    assert "BVQ7-TTB-00001" not in str(decision.model_dump())


def test_transfer_draft_rejects_unknown_target_facility():
    """Không tìm thấy khoa đích thì không được fallback sang facility_id=1."""
    from app.models_core import ToolCall

    MutationDraftManager._drafts.clear()
    executor = ToolExecutor()
    call = ToolCall(
        tool_name="transfer_device_draft",
        arguments={"device_id_or_tag": "BVQ7-TTB-00001", "target_facility": "Khoa Không Tồn Tại 999"},
        risk_level=RiskLevel.HIGH_WRITE,
        requires_confirmation=True,
    )
    res = executor.execute_tool(call)
    assert res.success is False
    assert res.error_code == "VALIDATION_ERROR"


def test_registry_read_tools_execute_without_unsupported_dispatch():
    """Các tool đã khai báo trong registry phải có executor dispatch thật."""
    from app.models_core import ToolCall

    executor = ToolExecutor()
    calls = [
        ToolCall(tool_name="get_contract_info", arguments={"contract_no_or_id": "03625Q7/HĐKT/DWHCM-TA"}),
        ToolCall(tool_name="get_supplier_info", arguments={"supplier_name": "GE Healthcare"}),
        ToolCall(tool_name="get_device_maintenance_history", arguments={"device_id_or_tag": "BVQ7-TTB-00001"}),
        ToolCall(tool_name="get_device_transfer_history", arguments={"device_id_or_tag": "BVQ7-TTB-00001"}),
    ]

    for call in calls:
        res = executor.execute_tool(call)
        assert res.error != f"Tool '{call.tool_name}' chưa được hỗ trợ trong Executor."
        assert res.error_code != "NOT_FOUND" or call.tool_name in {"get_contract_info", "get_supplier_info"}


def test_dashboard_summary_response_uses_dynamic_counts(tmp_path):
    """Dashboard summary phải lấy số liệu từ DB hiện tại, không hardcode 100%/583."""
    db_path = tmp_path / "devices.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE devices (id INTEGER PRIMARY KEY, risk_level TEXT, status TEXT);
        CREATE TABLE device_documents (id INTEGER PRIMARY KEY, device_id INTEGER);
        CREATE TABLE calibration_certificates (id INTEGER PRIMARY KEY, device_id INTEGER);
        INSERT INTO devices (id, risk_level, status) VALUES
          (1, 'A', 'IN_SERVICE'),
          (2, 'B', 'UNDER_MAINTENANCE'),
          (3, 'C', 'IN_SERVICE'),
          (4, 'D', 'RETIRED');
        INSERT INTO device_documents (device_id) VALUES (1), (3);
        INSERT INTO calibration_certificates (device_id) VALUES (1), (2), (3), (4), (1), (2), (3);
        """
    )
    conn.close()

    executor = ToolExecutor(str(db_path))
    from app.models_core import ToolCall

    res = executor.execute_tool(ToolCall(tool_name="get_dashboard_summary", arguments={}))
    text = NeedleAgent()._format_response_text("get_dashboard_summary", res)

    assert res.success is True
    assert res.data["total_devices"] == 4
    assert res.data["devices_with_pdf"] == 2
    assert res.data["pdf_coverage_pct"] == 50.0
    assert res.data["total_calibration_certificates"] == 7
    assert "50.0%" in text
    assert "**7** Giấy chứng nhận" in text
    assert "100%" not in text
    assert "583" not in text


def test_api_semantica_requires_device_identity(client):
    """Semantica explainability không được tự fallback sang device_id=1 khi thiếu ngữ cảnh."""
    res = client.post("/api/agent/query", json={"query": "Tại sao máy này được phân loại rủi ro cao?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CLARIFICATION_REQUIRED"
    assert data["route_taken"] == "SEMANTICA_GRAPH"
    assert "MISSING_DEVICE_IDENTITY" in data["warnings"]
    assert data.get("structured_data") is None


def test_api_agent_routes_require_auth_when_rbac_enforced(monkeypatch):
    """Khi bật HTM_ENFORCE_RBAC, /api/agent/* phải yêu cầu auth và role phù hợp."""
    from app.config import get_settings

    monkeypatch.setenv("HTM_ENFORCE_RBAC", "1")
    get_settings.cache_clear()
    try:
        with TestClient(app) as enforced_client:
            unauth_tools = enforced_client.get("/api/agent/tools")
            assert unauth_tools.status_code == 401

            unauth_query = enforced_client.post("/api/agent/query", json={"query": "kiểm tra thiết bị"})
            assert unauth_query.status_code == 401

            authed_tools = enforced_client.get("/api/agent/tools", headers={"X-API-Key": "BME_ENGINEER_KEY_2026"})
            assert authed_tools.status_code == 200

            underprivileged_confirm = enforced_client.post(
                "/api/agent/mutation/confirm",
                headers={"X-API-Key": "CLINICAL_KEY_2026"},
                json={"draft_id": "DRAFT-NOT-REAL"},
            )
            assert underprivileged_confirm.status_code == 403
    finally:
        monkeypatch.delenv("HTM_ENFORCE_RBAC", raising=False)
        get_settings.cache_clear()

