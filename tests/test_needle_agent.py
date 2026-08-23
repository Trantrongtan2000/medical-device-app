"""
Comprehensive Tests for Needle Edge Agent & Cactus Hybrid Router POC
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.needle_agent import needle_agent, NeedleRouter, SafeToolExecutor
from app.database import get_db_connection

@pytest.fixture
def client():
    return TestClient(app)

# 1. Router Intent & Confidence Unit Tests
def test_router_asset_tag_lookup():
    decision = NeedleRouter.parse_intent("Tra cứu máy BVQ7-TTB-00001 đang ở đâu?")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_DEVICE"
    assert decision.confidence >= 0.95
    assert decision.tool_name == "get_device_by_asset_tag"
    assert decision.parameters["asset_tag"] == "BVQ7-TTB-00001"

def test_router_calibration_status():
    decision = NeedleRouter.parse_intent("Kiểm tra hạn kiểm định của máy #00002")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "CHECK_CALIBRATION"
    assert decision.confidence >= 0.95
    assert decision.tool_name == "get_device_calibration_status"
    assert decision.parameters["device_id_or_tag"] == "BVQ7-TTB-00002"

def test_router_dashboard_summary():
    decision = NeedleRouter.parse_intent("Cho tôi xem thống kê tổng quan toàn viện")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "DASHBOARD_SUMMARY"
    assert decision.tool_name == "get_dashboard_summary"
    assert decision.confidence >= 0.90

def test_router_search_device_by_keyword():
    decision = NeedleRouter.parse_intent("Tìm danh sách máy thở trong bệnh viện")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "SEARCH_DEVICES"
    assert decision.tool_name == "search_devices"
    assert decision.parameters["keyword"] == "máy thở"

def test_router_facility_lookup_unicode():
    decision = NeedleRouter.parse_intent("Tra cứu thông tin Khoa Cấp Cứu ở đâu?")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_FACILITY"
    assert decision.tool_name == "get_facility"
    assert decision.parameters["name_or_code"] == "cấp cứu"

def test_router_mutation_safety_gate():
    decision = NeedleRouter.parse_intent("Điều chuyển máy BVQ7-TTB-00001 sang Khoa Ngoại")
    assert decision.route == "LOCAL_EDGE"
    assert decision.requires_confirmation is True
    assert decision.intent == "MUTATION_ACTION"

def test_router_escalate_complex_to_cloud():
    decision = NeedleRouter.parse_intent("Giải thích nguyên lý hoạt động khối phát tia X theo Nghị định 98 và SOP QT.04")
    assert decision.route == "CLOUD_FRONTIER"
    assert decision.confidence < 0.85
    assert decision.tool_name is None

# 2. Integration Tests with SafeToolExecutor (All 5 Tools)
def test_executor_get_device():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_device_by_asset_tag", {"asset_tag": "BVQ7-TTB-00001"}, db)
        assert data is not None
        assert "BVQ7-TTB-00001" in text
        assert "Thông Tin Thiết Bị" in text

def test_executor_search_devices():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("search_devices", {"keyword": "máy"}, db)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Tìm thấy" in text

def test_executor_get_facility():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_facility", {"name_or_code": "Cấp Cứu"}, db)
        assert data is not None
        assert "Khoa/Phòng:" in text

def test_executor_calibration_status():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_device_calibration_status", {"device_id_or_tag": "BVQ7-TTB-00001"}, db)
        assert data is not None
        assert "Tình Trạng Kiểm Định" in text

def test_executor_dashboard_summary():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_dashboard_summary", {}, db)
        assert data["total_devices"] >= 1
        assert "Báo Cáo Tổng Hợp Thiết Bị Y Tế" in text

# 3. Async Agent Pipeline Test
@pytest.mark.asyncio
async def test_async_needle_agent_process_query():
    with get_db_connection() as db:
        result = await needle_agent.process_query("Kiểm tra hạn kiểm định của máy #00001", db)
        assert result.status == "SUCCESS"
        assert result.route_taken == "LOCAL_EDGE"
        assert result.confidence >= 0.85
        assert result.tool_name == "get_device_calibration_status"

# 4. HTTP API Endpoint Tests
def test_api_agent_tools_list(client):
    res = client.get("/api/agent/tools")
    assert res.status_code == 200
    data = res.json()
    assert data["tools_count"] == 5
    tool_names = [t["name"] for t in data["tools"]]
    assert "get_device_by_asset_tag" in tool_names
    assert "get_dashboard_summary" in tool_names

def test_api_agent_query_local_edge(client):
    payload = {"query": "Xem thông tin máy BVQ7-TTB-00001"}
    res = client.post("/api/agent/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["route_taken"] == "LOCAL_EDGE"
    assert data["tool_name"] == "get_device_by_asset_tag"
    assert data["confidence"] >= 0.85
    assert "BVQ7-TTB-00001" in data["response_text"]

def test_api_agent_query_confirmation_gate(client):
    payload = {"query": "Tạo phiếu điều chuyển máy sang phòng xét nghiệm"}
    res = client.post("/api/agent/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "AWAITING_CONFIRMATION"
    assert "xác nhận" in data["response_text"]
