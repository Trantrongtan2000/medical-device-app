r"""
Router quản lý hồ sơ tài liệu PDF gốc đính kèm thiết bị y tế (BV Quận 7)

- Đường dẫn trong CSDL là POSIX tương đối (vd: 03_BAN_GIAO_VA_NGHIEM_THU/docs_raw/...).
- Phân đoạn chứng từ trong PDF gộp qua bảng document_segments (giữ nguyên file gốc).
- Phục vụ PDF an toàn theo document ID (chống path traversal).
"""
from __future__ import annotations

import os
import urllib.parse
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator

from .database import get_db

router = APIRouter(tags=["Documents & PDF Management"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOC_TYPE_LABELS = {
    "HANDOVER": "Biên Bản Bàn Giao & Nghiệm Thu",
    "CALIBRATION": "Giấy Chứng Nhận Kiểm Định & Hiệu Chuẩn",
    "CONTRACT": "Hợp Đồng Mua Sắm & Xuất Xưởng",
    "MAINTENANCE": "Nhật Ký Bảo Trì & Sửa Chữa",
    "LEGAL": "Hồ Sơ Thẩm Định & Pháp Lý",
    "OTHER": "Tài Liệu Đính Kèm Khác",
}

DOC_TYPE_BADGES = {
    "HANDOVER": {"bg": "#0284c7", "label": "Bàn Giao Nghiệm Thu"},
    "CALIBRATION": {"bg": "#059669", "label": "Kiểm Định Hiệu Chuẩn"},
    "CONTRACT": {"bg": "#d97706", "label": "Hợp Đồng Mua Sắm"},
    "MAINTENANCE": {"bg": "#7c3aed", "label": "Bảo Trì Sửa Chữa"},
    "LEGAL": {"bg": "#dc2626", "label": "Pháp Lý & CO/CQ"},
    "OTHER": {"bg": "#64748b", "label": "Tài Liệu Khác"},
}


def _documents_root_candidates() -> List[Path]:
    custom = os.getenv("MEDICAL_DEVICE_DOCUMENTS_ROOT") or os.getenv("MEDICAL_DEVICE_PDF_ROOT")
    roots = [
        Path(custom) if custom else None,
        Path("/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712"),
        PROJECT_ROOT.parent / "BV QUẬN 7_OCR_WORK_20260712",
        Path("/media/tan/T93/BACKUP_DU_LIEU_SO_HOA_20260818"),
        Path(r"G:\BV QUẬN 7_OCR_WORK_20260712"),
        Path(r"G:\BV QUẬN 7"),
        Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818"),
        PROJECT_ROOT / "docs_storage",
        PROJECT_ROOT / "docs",
    ]
    return [p.resolve() for p in roots if p is not None and p.exists()]


def normalize_stored_path(stored: str) -> str:
    """Chuẩn hóa path DB về POSIX tương đối, chặn traversal."""
    if stored is None:
        raise HTTPException(status_code=400, detail="file_path trống")
    raw = str(stored).strip().replace("\\", "/")
    if not raw:
        raise HTTPException(status_code=400, detail="file_path trống")
    # Windows absolute → lấy phần relative sau ổ đĩa nếu có thể
    if len(raw) >= 3 and raw[1] == ":" and raw[2] == "/":
        raw = raw[3:]
    while raw.startswith("./"):
        raw = raw[2:]
    if raw.startswith("/") or raw.startswith("~"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận đường dẫn tương đối POSIX trong kho tài liệu")
    parts = [p for p in raw.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise HTTPException(status_code=400, detail="Phát hiện path traversal không hợp lệ")
    return "/".join(parts)


def resolve_document_file(stored_path: str) -> Path:
    """
    Resolve file_path trong CSDL thành Path tuyệt đối nằm trong một documents root được phép.
    """
    rel = normalize_stored_path(stored_path)
    abs_candidate = Path(stored_path)
    # Cho phép absolute chỉ khi nằm trong root whitelist (máy Windows local)
    if abs_candidate.is_absolute() and abs_candidate.exists() and abs_candidate.is_file():
        resolved = abs_candidate.resolve()
        for root in _documents_root_candidates():
            try:
                if root.exists() and resolved.is_relative_to(root):
                    return resolved
            except (OSError, ValueError):
                continue
        raise HTTPException(status_code=403, detail="Đường dẫn tuyệt đối nằm ngoài kho tài liệu được phép")

    for root in _documents_root_candidates():
        if not root.exists():
            continue
        candidate = (root / rel).resolve()
        try:
            if not candidate.is_relative_to(root):
                continue
        except (OSError, ValueError):
            continue
        if candidate.exists() and candidate.is_file():
            return candidate

    raise HTTPException(
        status_code=404,
        detail=f"Tệp không tồn tại trong kho tài liệu: {rel}",
    )


def build_pdfjs_viewer_url(doc_id: int, page_start: int = 1) -> str:
    page = max(1, int(page_start or 1))
    pdf_api = f"/api/documents/{doc_id}/pdf"
    return (
        "/static/pdfjs/web/viewer.html?file="
        + urllib.parse.quote(pdf_api, safe="")
        + f"#page={page}"
    )


def _format_size(file_size: Optional[int]) -> str:
    f_size_kb = round((file_size or 0) / 1024, 1)
    return f"{f_size_kb} KB" if f_size_kb < 1024 else f"{round(f_size_kb / 1024, 2)} MB"


def _segment_row_to_dict(row, doc_id: int) -> dict:
    page_start = int(row["page_start"])
    return {
        "id": row["id"],
        "document_id": row["document_id"],
        "page_start": page_start,
        "page_end": int(row["page_end"]),
        "doc_type": row["doc_type"],
        "doc_type_label": DOC_TYPE_LABELS.get(row["doc_type"], row["doc_type"]),
        "doc_badge": DOC_TYPE_BADGES.get(row["doc_type"], {"bg": "#64748b", "label": row["doc_type"]}),
        "form_code": row["form_code"],
        "title": row["title"],
        "extracted_serial": row["extracted_serial"],
        "confidence": row["confidence"],
        "md_anchor": row["md_anchor"],
        "notes": row["notes"] if "notes" in row.keys() else None,
        "created_at": row["created_at"],
        "viewer_url": build_pdfjs_viewer_url(doc_id, page_start),
    }


class DocumentSegmentIn(BaseModel):
    page_start: int = Field(..., ge=1)
    page_end: int = Field(..., ge=1)
    doc_type: str
    form_code: Optional[str] = None
    title: Optional[str] = None
    extracted_serial: Optional[str] = None
    confidence: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    md_anchor: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_page_range(self):
        if self.page_end < self.page_start:
            raise ValueError("page_end phải >= page_start")
        return self


@router.get("/api/devices/{device_id}/documents")
async def get_device_documents(device_id: int, db=Depends(get_db)):
    """Lấy danh sách toàn bộ hồ sơ PDF/tài liệu gốc đính kèm của một thiết bị"""
    dev = db.execute(
        "SELECT id, device_name, model, serial_no, contract_no FROM devices WHERE id = ?",
        (device_id,),
    ).fetchone()
    if not dev:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")

    rows = db.execute(
        """
        SELECT id, device_id, doc_type, title, file_path, file_size, file_ext, match_method, created_at
        FROM device_documents
        WHERE device_id = ?
        ORDER BY
            CASE doc_type
                WHEN 'HANDOVER' THEN 1
                WHEN 'CALIBRATION' THEN 2
                WHEN 'CONTRACT' THEN 3
                WHEN 'MAINTENANCE' THEN 4
                ELSE 5
            END, id ASC
        """,
        (device_id,),
    ).fetchall()

    docs = []
    for r in rows:
        d_type = r["doc_type"]
        badge_info = DOC_TYPE_BADGES.get(d_type, {"bg": "#64748b", "label": d_type})
        try:
            resolve_document_file(r["file_path"])
            exists = True
        except HTTPException:
            exists = False

        seg_count = db.execute(
            "SELECT COUNT(*) AS c FROM document_segments WHERE document_id = ?",
            (r["id"],),
        ).fetchone()["c"]

        docs.append(
            {
                "id": r["id"],
                "device_id": r["device_id"],
                "doc_type": d_type,
                "doc_type_label": DOC_TYPE_LABELS.get(d_type, d_type),
                "doc_badge_bg": badge_info["bg"],
                "doc_badge_label": badge_info["label"],
                "title": r["title"],
                "file_path": r["file_path"],
                "file_size": r["file_size"],
                "file_size_str": _format_size(r["file_size"]),
                "file_ext": r["file_ext"],
                "match_method": r["match_method"],
                "file_exists": exists,
                "segment_count": seg_count,
                "stream_url": f"/api/documents/stream/{r['id']}",
                "download_url": f"/api/documents/download/{r['id']}",
                "pdf_url": f"/api/documents/{r['id']}/pdf",
                "segments_url": f"/api/documents/{r['id']}/segments",
                "viewer_url": build_pdfjs_viewer_url(r["id"], 1),
            }
        )

    return {
        "device": {
            "id": dev["id"],
            "device_name": dev["device_name"],
            "model": dev["model"],
            "serial_no": dev["serial_no"],
            "contract_no": dev["contract_no"],
        },
        "total_documents": len(docs),
        "documents": docs,
    }


def _get_document_or_404(db, doc_id: int):
    row = db.execute(
        "SELECT id, device_id, doc_type, title, file_path, file_size, file_ext FROM device_documents WHERE id = ?",
        (doc_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu trong CSDL")
    return row


@router.get("/api/documents/{doc_id}/pdf")
async def serve_document_pdf(doc_id: int, db=Depends(get_db)):
    """Phục vụ file PDF an toàn theo document ID (chống path traversal)."""
    row = _get_document_or_404(db, doc_id)
    file_path = resolve_document_file(row["file_path"])
    filename = row["title"] or file_path.name
    quoted_filename = urllib.parse.quote(filename)
    ext = (row["file_ext"] or file_path.suffix.lstrip(".") or "pdf").lower()
    media_type = "application/pdf" if ext == "pdf" else "application/octet-stream"
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{quoted_filename}",
            "Cache-Control": "private, max-age=300",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/api/documents/{doc_id}/segments")
async def list_document_segments(doc_id: int, db=Depends(get_db)):
    """Danh sách phân đoạn chứng từ trong một tài liệu PDF gộp."""
    doc = _get_document_or_404(db, doc_id)
    rows = db.execute(
        """
        SELECT id, document_id, page_start, page_end, doc_type, form_code, title,
               extracted_serial, confidence, md_anchor, notes, created_at
        FROM document_segments
        WHERE document_id = ?
        ORDER BY page_start ASC, id ASC
        """,
        (doc_id,),
    ).fetchall()
    segments = [_segment_row_to_dict(r, doc_id) for r in rows]
    return {
        "document": {
            "id": doc["id"],
            "device_id": doc["device_id"],
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "pdf_url": f"/api/documents/{doc_id}/pdf",
            "viewer_url": build_pdfjs_viewer_url(doc_id, 1),
        },
        "total_segments": len(segments),
        "segments": segments,
    }


@router.post("/api/documents/{doc_id}/segments")
async def create_document_segment(doc_id: int, payload: DocumentSegmentIn, db=Depends(get_db)):
    """Thêm một phân đoạn chứng từ cho PDF gộp (không tách file gốc)."""
    _get_document_or_404(db, doc_id)
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO document_segments (
            document_id, page_start, page_end, doc_type, form_code, title,
            extracted_serial, confidence, md_anchor, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            doc_id,
            payload.page_start,
            payload.page_end,
            payload.doc_type.upper(),
            payload.form_code,
            payload.title,
            payload.extracted_serial,
            payload.confidence if payload.confidence is not None else 0.0,
            payload.md_anchor,
            payload.notes,
        ),
    )
    db.commit()
    seg_id = cur.lastrowid
    row = db.execute("SELECT * FROM document_segments WHERE id = ?", (seg_id,)).fetchone()
    return {"status": "success", "segment": _segment_row_to_dict(row, doc_id)}


@router.get("/api/documents/stream/{doc_id}")
async def stream_document(doc_id: int, db=Depends(get_db)):
    """Mở và xem trực tiếp file PDF / tài liệu trong trình duyệt (legacy alias → /pdf)."""
    return await serve_document_pdf(doc_id, db)


@router.get("/api/documents/download/{doc_id}")
async def download_document(doc_id: int, db=Depends(get_db)):
    """Tải file tài liệu về máy tính"""
    row = _get_document_or_404(db, doc_id)
    file_path = resolve_document_file(row["file_path"])
    filename = row["title"] or file_path.name
    quoted_filename = urllib.parse.quote(filename)
    return FileResponse(
        path=str(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"},
    )


@router.get("/api/documents/search")
async def search_documents(
    q: str = Query(..., min_length=2, description="Từ khóa tra cứu S/N, mã tài liệu, tên file"),
    doc_type: Optional[str] = None,
    limit: int = 50,
    db=Depends(get_db),
):
    """Tìm kiếm nhanh hồ sơ PDF trong toàn bộ kho lưu trữ"""
    term = f"%{q.strip()}%"
    sql = """
        SELECT doc.id, doc.device_id, doc.doc_type, doc.title, doc.file_path, doc.file_size, doc.file_ext,
               d.device_name, d.model, d.serial_no, f.name as facility_name
        FROM device_documents doc
        LEFT JOIN devices d ON d.id = doc.device_id
        LEFT JOIN facilities f ON f.id = d.facility_id
        WHERE (doc.title LIKE ? OR doc.file_path LIKE ? OR d.serial_no LIKE ? OR d.model LIKE ?)
    """
    params: list = [term, term, term, term]
    if doc_type:
        sql += " AND doc.doc_type = ?"
        params.append(doc_type)

    sql += " LIMIT ?"
    params.append(limit)

    rows = db.execute(sql, params).fetchall()
    results = []
    for r in rows:
        results.append(
            {
                "id": r["id"],
                "device_id": r["device_id"],
                "device_name": r["device_name"],
                "model": r["model"],
                "serial_no": r["serial_no"],
                "facility_name": r["facility_name"],
                "doc_type": r["doc_type"],
                "doc_badge": DOC_TYPE_BADGES.get(r["doc_type"], {"bg": "#64748b", "label": r["doc_type"]}),
                "title": r["title"],
                "stream_url": f"/api/documents/stream/{r['id']}",
                "pdf_url": f"/api/documents/{r['id']}/pdf",
                "viewer_url": build_pdfjs_viewer_url(r["id"], 1),
                "segments_url": f"/api/documents/{r['id']}/segments",
            }
        )

    return {"query": q, "total": len(results), "results": results}


# ==================== PHÂN HỆ QUẢN LÝ KHO DỮ LIỆU SỐ HÓA & HỒ SƠ TOÀN VIỆN ====================
_REPO_CACHE = {"summary": None, "files": None, "last_scan": 0}


def _scan_repository_files():
    import time
    now = time.time()
    if _REPO_CACHE["files"] is not None and (now - _REPO_CACHE["last_scan"] < 300):
        return _REPO_CACHE["files"], _REPO_CACHE["summary"]

    ocr_root = Path("/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712")
    if not ocr_root.exists():
        for r in _documents_root_candidates():
            if r.exists() and "OCR_WORK" in r.name:
                ocr_root = r
                break

    file_list = []
    by_folder = {}
    by_cat = {
        "Hợp Đồng Mua Sắm & Báo Giá": 0,
        "Biên Bản Bàn Giao & Nghiệm Thu": 0,
        "Kiểm Định & Hiệu Chuẩn": 0,
        "Bảo Trì, Sửa Chữa & CMMS": 0,
        "Thẩm Định, Cấp Phép & Pháp Lý": 0,
        "HDSD, Quy Trình & Đào Tạo": 0,
        "Tài Liệu Kỹ Thuật Khác": 0
    }

    if ocr_root.exists():
        for root_dir, _, filenames in os.walk(ocr_root):
            for fn in filenames:
                if fn.lower().endswith(".pdf"):
                    full_p = os.path.join(root_dir, fn)
                    rel_p = os.path.relpath(full_p, ocr_root).replace("\\", "/")
                    fn_lower = fn.lower()
                    folder = rel_p.split("/")[0] if "/" in rel_p else "Thư mục gốc"
                    by_folder[folder] = by_folder.get(folder, 0) + 1

                    cat = "Tài Liệu Kỹ Thuật Khác"
                    if "hợp đồng" in fn_lower or "hop dong" in fn_lower or "hd " in fn_lower or folder == "02_HOP_DONG_MUA_SAM":
                        cat = "Hợp Đồng Mua Sắm & Báo Giá"
                    elif "kiểm định" in fn_lower or "hiệu chuẩn" in fn_lower or "gcn" in fn_lower or folder == "04_KIEM_DINH_VA_HIEU_CHUAN":
                        cat = "Kiểm Định & Hiệu Chuẩn"
                    elif "bàn giao" in fn_lower or "ban giao" in fn_lower or "bbbg" in fn_lower or "nghiệm thu" in fn_lower or folder == "03_BAN_GIAO_VA_NGHIEM_THU":
                        cat = "Biên Bản Bàn Giao & Nghiệm Thu"
                    elif "hướng dẫn" in fn_lower or "hdsd" in fn_lower or "manual" in fn_lower or "đào tạo" in fn_lower:
                        cat = "HDSD, Quy Trình & Đào Tạo"
                    elif "bảo trì" in fn_lower or "sửa chữa" in fn_lower or "service report" in fn_lower or folder == "05_BAO_TRI_VA_SUA_CHUA":
                        cat = "Bảo Trì, Sửa Chữa & CMMS"
                    elif "thanh lý" in fn_lower or "tờ trình" in fn_lower or "thẩm định" in fn_lower or folder == "06_THAM_DINH_VA_PHAP_LY":
                        cat = "Thẩm Định, Cấp Phép & Pháp Lý"

                    by_cat[cat] = by_cat.get(cat, 0) + 1

                    try:
                        sz = os.path.getsize(full_p)
                    except OSError:
                        sz = 0

                    file_list.append({
                        "filename": fn,
                        "rel_path": rel_p,
                        "folder": folder,
                        "category": cat,
                        "size_bytes": sz,
                        "size_formatted": f"{sz / 1024 / 1024:.2f} MB" if sz > 1048576 else f"{sz / 1024:.1f} KB",
                    })

    summary = {
        "total_files": len(file_list),
        "by_folder": by_folder,
        "by_category": by_cat,
        "root_path": str(ocr_root)
    }

    _REPO_CACHE["files"] = file_list
    _REPO_CACHE["summary"] = summary
    _REPO_CACHE["last_scan"] = now
    return file_list, summary


@router.get("/api/documents/repository/summary")
async def get_repository_summary():
    """Lấy thống kê tổng hợp kho dữ liệu số hóa toàn viện"""
    _, summary = _scan_repository_files()
    return summary


@router.get("/api/documents/repository/files")
async def list_repository_files(
    q: Optional[str] = Query(None, description="Từ khóa tra cứu tên tệp hoặc đường dẫn"),
    folder: Optional[str] = Query(None, description="Lọc theo thư mục"),
    category: Optional[str] = Query(None, description="Lọc theo phân loại"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=200),
    db=Depends(get_db)
):
    """Danh sách tệp trong kho tài liệu số hóa kèm thông tin đối chiếu thiết bị"""
    all_files, _ = _scan_repository_files()

    # Lấy danh sách map trong DB
    rows = db.execute("SELECT file_path, COUNT(device_id) as dev_cnt FROM device_documents GROUP BY file_path").fetchall()
    map_dict = {r["file_path"].replace("\\", "/"): r["dev_cnt"] for r in rows}

    filtered = all_files
    if folder and folder != "all":
        filtered = [f for f in filtered if f["folder"] == folder]
    if category and category != "all":
        filtered = [f for f in filtered if f["category"] == category]
    if q and q.strip():
        term = q.strip().lower()
        filtered = [f for f in filtered if term in f["filename"].lower() or term in f["rel_path"].lower()]

    total = len(filtered)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = filtered[start_idx:end_idx]

    results = []
    for item in page_items:
        rel_p = item["rel_path"]
        dev_cnt = map_dict.get(rel_p, 0)
        # thử match theo filename nếu relative path khác
        if dev_cnt == 0:
            fn = item["filename"].lower()
            for db_p, c in map_dict.items():
                if db_p.lower().endswith(fn):
                    dev_cnt = c
                    break

        quoted_path = urllib.parse.quote(rel_p)
        results.append({
            **item,
            "linked_device_count": dev_cnt,
            "stream_url": f"/api/documents/repository/stream?path={quoted_path}",
            "viewer_url": f"/static/pdfjs/web/viewer.html?file={urllib.parse.quote(f'/api/documents/repository/stream?path={quoted_path}')}"
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "items": results
    }


@router.get("/api/documents/repository/stream")
async def stream_repository_file(path: str = Query(..., description="Đường dẫn tương đối của tệp trong kho tài liệu")):
    """Stream an toàn tệp PDF từ kho lưu trữ toàn viện"""
    file_path = resolve_document_file(path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp trong kho tài liệu")

    quoted_filename = urllib.parse.quote(file_path.name)
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{quoted_filename}",
            "Cache-Control": "public, max-age=3600",
        },
    )
