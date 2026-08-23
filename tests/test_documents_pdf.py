import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_device_documents_valid():
    """Kiểm tra API lấy danh sách tài liệu PDF của một thiết bị"""
    # Lấy thử 1 thiết bị đầu tiên
    res = client.get("/api/devices/1/documents")
    assert res.status_code == 200
    data = res.json()
    assert "device" in data
    assert "documents" in data
    assert "total_documents" in data
    assert isinstance(data["documents"], list)

def test_get_device_documents_not_found():
    """Kiểm tra khi device_id không tồn tại"""
    res = client.get("/api/devices/999999/documents")
    assert res.status_code == 404

def test_search_documents():
    """Kiểm tra tìm kiếm nhanh tài liệu PDF"""
    res = client.get("/api/documents/search?q=2024")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "total" in data

def test_stream_document_not_found():
    """Kiểm tra stream tài liệu khi doc_id không tồn tại"""
    res = client.get("/api/documents/stream/999999")
    assert res.status_code == 404
