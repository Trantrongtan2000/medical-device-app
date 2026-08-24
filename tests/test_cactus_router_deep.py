"""
Deep Verification Tests for Cactus Hybrid Router & Policy Gate (HTM V3)
Covers Ambiguity Detection, Canonical Data Contracts, Provenance and Safety Policies.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cactus_router import CactusHybridRouter
from app.needle_agent import NeedleAgent
from app.needle_planner import CircuitBreaker

@pytest.fixture
def client():
    return TestClient(app)

# 1. 3-Layer Routing & Ambiguity Detection
def test_router_ambiguity_detection():
    decision = CactusHybridRouter.route("kiểm tra máy")
    assert decision.intent == "AMBIGUOUS_CLARIFICATION"
    assert decision.ambiguity_score > 0.5
    assert decision.clarification_prompt is not None

def test_router_exact_asset_tag():
    decision = CactusHybridRouter.route("Tra cứu máy BVQ7-TTB-00001")
    assert decision.route == "LOCAL_EDGE"
    assert decision.confidence >= 0.95
    assert decision.tool_call.tool_name == "get_device_by_asset_tag"

def test_router_mutation_gate():
    decision = CactusHybridRouter.route("Điều chuyển máy BVQ7-TTB-00002 sang khoa hồi sức")
    assert decision.route == "LOCAL_EDGE"
    assert decision.requires_confirmation is True
    assert "REQUIRES_HUMAN_CONFIRMATION" in decision.policy_flags

# 2. Tool Execution & Provenance Record
def test_agent_provenance_and_trust():
    agent = NeedleAgent()
    res = agent.process_query("Xem báo cáo tổng quan toàn viện")
    assert res.status == "SUCCESS"
    assert res.provenance is not None
    assert res.provenance.source_type == "sqlite"
    assert res.provenance.is_authoritative is True

# 3. Circuit Breaker Simulation
def test_circuit_breaker_trip():
    cb = CircuitBreaker(failure_threshold=2, reset_timeout_seconds=5)
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is False  # Tripped to OPEN

    cb.record_success()
    assert cb.can_execute() is True

# 4. HTTP API Telemetry & Clarification Endpoints
def test_api_agent_clarification_response(client):
    res = client.post("/api/agent/query", json={"query": "kiểm tra thiết bị"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CLARIFICATION_REQUIRED"
    assert "Bạn muốn" in data["response_text"]


def test_api_agent_telemetry_endpoint(client):
    res = client.get("/api/agent/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "recent_events" in data

