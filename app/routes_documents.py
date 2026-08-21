r"""
Router quản lý hồ sơ tài liệu PDF gốc đính kèm thiết bị y tế (BV Quận 7)
Hỗ trợ stream trực tiếp PDF từ kho lưu trữ số hóa G:\BV QUẬN 7_OCR_WORK_20260712
"""
import os
import urllib.parse
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from .database import get_db

router = APIRouter(tags=["Documents & PDF Management"])

DOC_TYPE_LABELS = {
    "HANDOVER": "Biên Bản Bàn Giao & Nghiệm Thu",
    "CALIBRATION": "Giấy Chứng Nhận Kiểm Định & Hiệu Chuẩn",
    "CONTRACT": "Hợp Đồng Mua Sắm & Xuất Xưởng",
    "MAINTENANCE": "Nhật Ký Bảo Trì & Sửa Chữa",
    "LEGAL": "Hồ Sơ Thẩm Định & Pháp Lý",
    "OTHER": "Tài Liệu Đính Kèm Khác"
}

DOC_TYPE_BADGES = {
    "HANDOVER": {"bg": "#0284c7", "label": "Bàn Giao Nghiệm Thu"},
    "CALIBRATION": {"bg": "#059669", "label": "Kiểm Định Hiệu Chuẩn"},
    "CONTRACT": {"bg": "#d97706", "label": "Hợp Đồng Mua Sắm"},
    "MAINTENANCE": {"bg": "#7c3aed", "label": "Bảo Trì Sửa Chữa"},
    "LEGAL": {"bg": "#dc2626", "label": "Pháp Lý & CO/CQ"},
    "OTHER": {"bg": "#64748b", "label": "Tài Liệu Khác"}
}


@router.get("/api/devices/{device_id}/documents")
async def get_device_documents(device_id: int, db = Depends(get_db)):
    """Lấy danh sách toàn bộ hồ sơ PDF/tài liệu gốc đính kèm của một thiết bị"""
    dev = db.execute("SELECT id, device_name, model, serial_no, contract_no FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not dev:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")

    rows = db.execute("""
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
    """, (device_id,)).fetchall()

    docs = []
    for r in rows:
        d_type = r["doc_type"]
        badge_info = DOC_TYPE_BADGES.get(d_type, {"bg": "#64748b", "label": d_type})
        f_size_kb = round((r["file_size"] or 0) / 1024, 1)
        f_size_str = f"{f_size_kb} KB" if f_size_kb < 1024 else f"{round(f_size_kb/1024, 2)} MB"
        
        # Check if file exists on disk
        exists = os.path.exists(r["file_path"])

        docs.append({
            "id": r["id"],
            "device_id": r["device_id"],
            "doc_type": d_type,
            "doc_type_label": DOC_TYPE_LABELS.get(d_type, d_type),
            "doc_badge_bg": badge_info["bg"],
            "doc_badge_label": badge_info["label"],
            "title": r["title"],
            "file_size": r["file_size"],
            "file_size_str": f_size_str,
            "file_ext": r["file_ext"],
            "match_method": r["match_method"],
            "file_exists": exists,
            "stream_url": f"/api/documents/stream/{r['id']}",
            "download_url": f"/api/documents/download/{r['id']}"
        })

    return {
        "device": {
            "id": dev["id"],
            "device_name": dev["device_name"],
            "model": dev["model"],
            "serial_no": dev["serial_no"],
            "contract_no": dev["contract_no"]
        },
        "total_documents": len(docs),
        "documents": docs
    }


@router.get("/api/documents/stream/{doc_id}")
async def stream_document(doc_id: int, db = Depends(get_db)):
    """Mở và xem trực tiếp file PDF / tài liệu trong trình duyệt"""
    row = db.execute("SELECT file_path, title, file_ext FROM device_documents WHERE id = ?", (doc_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu trong CSDL")

    file_path = row["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Tệp không tồn tại trên ổ đĩa lưu trữ: {file_path}")

    filename = row["title"] or Path(file_path).name
    ext = (row["file_ext"] or "pdf").lower()

    content_types = {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "md": "text/markdown; charset=utf-8",
        "txt": "text/plain; charset=utf-8"
    }
    media_type = content_types.get(ext, "application/octet-stream")

    # Encode UTF-8 filename for Content-Disposition header
    quoted_filename = urllib.parse.quote(filename)

    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{quoted_filename}",
            "Cache-Control": "public, max-age=3600"
        }
    )


@router.get("/api/documents/download/{doc_id}")
async def download_document(doc_id: int, db = Depends(get_db)):
    """Tải file tài liệu về máy tính"""
    row = db.execute("SELECT file_path, title, file_ext FROM device_documents WHERE id = ?", (doc_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu trong CSDL")

    file_path = row["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Tệp không tồn tại: {file_path}")

    filename = row["title"] or Path(file_path).name
    quoted_filename = urllib.parse.quote(filename)

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"
        }
    )


@router.get("/api/documents/search")
async def search_documents(
    q: str = Query(..., min_length=2, description="Từ khóa tra cứu S/N, mã tài liệu, tên file"),
    doc_type: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """Tìm kiếm nhanh hồ sơ PDF trong toàn bộ kho lưu trữ 6.045 tài liệu"""
    term = f"%{q.strip()}%"
    sql = """
        SELECT doc.id, doc.device_id, doc.doc_type, doc.title, doc.file_path, doc.file_size, doc.file_ext,
               d.device_name, d.model, d.serial_no, f.name as facility_name
        FROM device_documents doc
        LEFT JOIN devices d ON d.id = doc.device_id
        LEFT JOIN facilities f ON f.id = d.facility_id
        WHERE (doc.title LIKE ? OR doc.file_path LIKE ? OR d.serial_no LIKE ? OR d.model LIKE ?)
    """
    params = [term, term, term, term]
    if doc_type:
        sql += " AND doc.doc_type = ?"
        params.append(doc_type)

    sql += " LIMIT ?"
    params.append(limit)

    rows = db.execute(sql, params).fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "device_id": r["device_id"],
            "device_name": r["device_name"],
            "model": r["model"],
            "serial_no": r["serial_no"],
            "facility_name": r["facility_name"],
            "doc_type": r["doc_type"],
            "doc_badge": DOC_TYPE_BADGES.get(r["doc_type"], {"bg": "#64748b", "label": r["doc_type"]}),
            "title": r["title"],
            "stream_url": f"/api/documents/stream/{r['id']}"
        })

    return {"query": q, "total": len(results), "results": results}
