"""
Deep Verification Tests for 6-Layer Cactus Hybrid Router & Needle Planner
Covers Ambiguity Detection, Canonical Data Contracts, Provenance and Telemetry.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cactus_router import CactusHybridRouter
from app.needle_planner import needle_planner, CircuitBreaker
from app.database import get_db_connection
from app.observability import telemetry_collector

@pytest.fixture
def client():
    return TestClient(app)

# 1. 6-Layer Routing & Ambiguity Detection
def test_router_ambiguity_detection():
    decision = CactusHybridRouter.route("kiểm tra máy")
    assert decision.intent == "AMBIGUOUS_CLARIFICATION_REQUIRED"
    assert decision.ambiguity_score > 0.5
    assert decision.clarification_prompt is not None

def test_router_exact_asset_tag():
    decision = CactusHybridRouter.route("Tra cứu máy BVQ7-TTB-00001")
    assert decision.route == "LOCAL_EDGE"
    assert decision.strategy == "DETERMINISTIC_EXACT"
    assert decision.confidence >= 0.95
    assert decision.tool_name == "get_device_by_asset_tag"

def test_router_mutation_gate():
    decision = CactusHybridRouter.route("Bàn giao máy BVQ7-TTB-00002 sang khoa hồi sức")
    assert decision.route == "LOCAL_EDGE"
    assert decision.requires_confirmation is True
    assert "REQUIRES_HUMAN_CONFIRMATION" in decision.policy_flags

# 2. Planner & Provenance Record
def test_planner_provenance_and_trust():
    with get_db_connection() as db:
        route_decision = CactusHybridRouter.route("Xem báo cáo tổng quan")
        tool_dec, tool_res = needle_planner.plan_and_execute(route_decision, db)
        
        assert tool_res.success is True
        assert tool_res.provenance is not None
        assert tool_res.provenance.source_type == "SQLITE_MASTER"
        assert tool_res.provenance.is_authoritative is True
        assert tool_res.trust_level.value == "CALCULATED_DATA"

# 3. Circuit Breaker Simulation
def test_circuit_breaker_trip():
    cb = CircuitBreaker(failure_threshold=2, reset_timeout_seconds=5)
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is False  # Tripped to OPEN

    cb.record_success()
    assert cb.can_execute() is True  # Reset to CLOSED

# 4. HTTP API Telemetry & Clarification Endpoints
def test_api_agent_clarification_response(client):
    res = client.post("/api/agent/query", json={"query": "kiểm tra thiết bị"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CLARIFICATION_REQUIRED"
    assert "ambiguity_score" in data
    assert "❓" in data["response_text"]

def test_api_agent_telemetry_endpoint(client):
    # Send a valid query to populate telemetry
    client.post("/api/agent/query", json={"query": "Xem máy BVQ7-TTB-00001"})
    
    res = client.get("/api/agent/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "recent_events" in data
    assert data["metrics"]["total_events"] > 0
