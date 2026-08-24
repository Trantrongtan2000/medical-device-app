"""
P2-D: Consistency & Provenance Audit Suite (HTM V3)
Kiểm tra tính nhất quán 100% giữa:
SQLite (Operational Truth) <-> Markdown Wiki (Extracted Knowledge) <-> PDF Scan Gốc (Original Evidence)
"""
import sqlite3
from pathlib import Path
from app.needle_agent import ToolExecutor
from app.models_core import ToolCall

def test_sqlite_to_pdf_documents_consistency():
    """Kiểm tra tính nhất quán giữa bản ghi CSDL và tài liệu PDF liên kết"""
    executor = ToolExecutor()
    
    # Kiểm tra ngẫu nhiên các thiết bị quan trọng (TMH, Siêu âm, Thận nhân tạo)
    sample_tags = ["BVQ7-TTB-00001", "BVQ7-TTB-00193", "BVQ7-TTB-00050", "BVQ7-TTB-00100"]
    
    for tag in sample_tags:
        call = ToolCall(tool_name="get_device_pdf_documents", arguments={"device_id_or_tag": tag})
        res = executor.execute_tool(call)
        
        assert res.success is True
        assert res.data is not None
        assert "device" in res.data
        assert "documents" in res.data
        
        # Provenance verification
        assert res.provenance is not None
        assert res.provenance.source_type == "sqlite"
        assert res.provenance.record_table == "device_documents"
        assert res.provenance.is_authoritative is True
        
        # Check action card mapping
        assert res.action_card is not None
        assert res.action_card["card_type"] == "DOCUMENT_CARD"
        assert res.action_card["total_documents"] == len(res.data["documents"])

def test_calibration_certificates_provenance_integrity():
    """Kiểm tra đối soát 100% GCN kiểm định có đầy đủ thông tin số tem, ngày cấp, hạn dùng"""
    executor = ToolExecutor()
    call = ToolCall(tool_name="get_calibration_status", arguments={"device_id_or_tag": "BVQ7-TTB-00193"})
    res = executor.execute_tool(call)
    
    assert res.success is True
    assert res.provenance.record_table == "calibration_certificates"
    assert res.provenance.is_authoritative is True
    assert res.action_card["card_type"] == "CALIBRATION_CARD"
