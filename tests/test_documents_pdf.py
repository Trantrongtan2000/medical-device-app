"""Tests for document segments + secure PDF serving + PDF.js viewer URLs."""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Point resolver at local fixture storage before app import side-effects
ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = ROOT / "docs_storage"
FIXTURE_PDF = FIXTURE_ROOT / "03_BAN_GIAO_VA_NGHIEM_THU" / "docs_raw" / "BBBG NB_VirtueRF_CT Lasera_SN 26003.pdf"
os.environ["MEDICAL_DEVICE_DOCUMENTS_ROOT"] = str(FIXTURE_ROOT)

from app.main import app
from app.database import init_database, get_db_connection

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def _prepare_fixture_and_segments():
    FIXTURE_PDF.parent.mkdir(parents=True, exist_ok=True)
    if not FIXTURE_PDF.exists():
        FIXTURE_PDF.write_bytes(
            b"%PDF-1.1\n"
            b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
            b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF\n"
        )
    init_database()
    with get_db_connection() as db:
        row = db.execute(
            "SELECT id FROM device_documents WHERE file_path LIKE ? LIMIT 1",
            ("%VirtueRF%",),
        ).fetchone()
        assert row, "Expected VirtueRF sample document in device_documents"
        doc_id = row["id"]
        db.execute("DELETE FROM document_segments WHERE document_id = ?", (doc_id,))
        db.execute(
            """
            INSERT INTO document_segments
                (document_id, page_start, page_end, doc_type, form_code, title, extracted_serial, confidence, md_anchor)
            VALUES
                (?, 1, 4, 'CONTRACT', 'HĐMB', 'Hợp đồng mua bán VirtueRF', '26003', 0.92, 'md/01_MUA_SAM#virtuerf'),
                (?, 5, 8, 'HANDOVER', 'BM04', 'Biên bản bàn giao nghiệm thu BM04', '26003', 0.88, 'md/03_BAN_GIAO#bm04'),
                (?, 9, 11, 'CALIBRATION', '24A', 'GCN Kiểm định & Tem 24A', '26003', 0.85, 'md/05_KIEM_DINH#gcn')
            """,
            (doc_id, doc_id, doc_id),
        )
        db.commit()
        yield doc_id


def test_get_device_documents_valid():
    res = client.get("/api/devices/1/documents")
    assert res.status_code == 200
    data = res.json()
    assert "device" in data
    assert "documents" in data
    assert "total_documents" in data
    assert isinstance(data["documents"], list)


def test_get_device_documents_not_found():
    res = client.get("/api/devices/999999/documents")
    assert res.status_code == 404


def test_search_documents():
    res = client.get("/api/documents/search?q=2024")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "total" in data


def test_stream_document_not_found():
    res = client.get("/api/documents/stream/999999")
    assert res.status_code == 404


def test_pdf_endpoint_and_segments(_prepare_fixture_and_segments):
    doc_id = _prepare_fixture_and_segments
    pdf = client.get(f"/api/documents/{doc_id}/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content[:4] == b"%PDF"

    segs = client.get(f"/api/documents/{doc_id}/segments")
    assert segs.status_code == 200
    body = segs.json()
    assert body["total_segments"] == 3
    assert body["segments"][0]["page_start"] == 1
    assert body["segments"][0]["page_end"] == 4
    assert "viewer_url" in body["segments"][0]
    from urllib.parse import unquote
    v0 = unquote(body["segments"][0]["viewer_url"])
    v1 = unquote(body["segments"][1]["viewer_url"])
    v2 = unquote(body["segments"][2]["viewer_url"])
    assert f"/api/documents/{doc_id}/pdf" in v0
    assert "#page=1" in v0
    assert "#page=5" in v1
    assert "#page=9" in v2
    assert v0.startswith("/static/pdfjs/web/viewer.html?file=")


def test_path_traversal_rejected(_prepare_fixture_and_segments):
    from app.routes_documents import normalize_stored_path
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        normalize_stored_path("../etc/passwd")
    assert exc.value.status_code == 400


def test_create_segment_validation(_prepare_fixture_and_segments):
    doc_id = _prepare_fixture_and_segments
    bad = client.post(
        f"/api/documents/{doc_id}/segments",
        json={"page_start": 5, "page_end": 3, "doc_type": "LEGAL", "title": "bad"},
    )
    assert bad.status_code == 422

    ok = client.post(
        f"/api/documents/{doc_id}/segments",
        json={
            "page_start": 12,
            "page_end": 12,
            "doc_type": "OTHER",
            "form_code": "PHU_LUC",
            "title": "Phụ lục cuối",
            "confidence": 0.7,
        },
    )
    assert ok.status_code == 200
    assert ok.json()["segment"]["page_start"] == 12


def test_pdfjs_viewer_static_available():
    res = client.get("/static/pdfjs/web/viewer.html")
    assert res.status_code == 200
    assert b"pdf.js" in res.content.lower() or b"viewer" in res.content.lower()
