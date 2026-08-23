#!/usr/bin/env python3
"""
🏥 HTM v3 — Batch Page Segmentation Pipeline
Tự động quét kho 8.011 tệp Markdown OCR để bóc tách phân đoạn chứng từ (document_segments)
và nạp trực tiếp vào CSDL devices.db.
"""

import os
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "devices.db"
MD_ROOT = Path("/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712/md")

FORM_PATTERNS = [
    # Mua sắm & Hợp đồng
    (re.compile(r"(BM\.?01[/\w\.]+|HỢP ĐỒNG|HĐ\s*\d+|BÁO GIÁ|XUẤT XƯỞNG)", re.IGNORECASE), "CONTRACT", "BM.01", "Hồ sơ Mua sắm & Hợp đồng"),
    # Bàn giao & Nghiệm thu
    (re.compile(r"(BM\.?04[/\w\.\-_]+|BM\.?02[/\w\.\-_]+|BIÊN BẢN (?:BÀN GIAO|NGHIỆM THU))", re.IGNORECASE), "HANDOVER", "BM04_TA5", "Biên bản Bàn giao & Nghiệm thu"),
    # Kiểm định & Hiệu chuẩn
    (re.compile(r"(\d{2}[A-Z]-KD[-\w]+|GIẤY CHỨNG NHẬN (?:KIỂM ĐỊNH|HIỆU CHUẨN)|KẾT QUẢ KIỂM ĐỊNH)", re.IGNORECASE), "CALIBRATION", "24A-KD", "Giấy chứng nhận Kiểm định & Hiệu chuẩn"),
    # Bảo trì & Sửa chữa
    (re.compile(r"(NHẬT KÝ BẢO TRÌ|PHIẾU SỬA CHỮA|BÁO CÁO KỸ THUẬT)", re.IGNORECASE), "MAINTENANCE", "BM.BT.01", "Nhật ký Bảo trì & Kỹ thuật"),
    # Pháp lý & CO/CQ
    (re.compile(r"(CERTIFICATE OF ORIGIN|CO/CQ|TỜ KHAI HẢI QUAN|ISO \d+)", re.IGNORECASE), "LEGAL", "CO_CQ", "Hồ sơ Pháp lý & Xuất xứ CO/CQ"),
]

def parse_frontmatter(content: str) -> Dict[str, Any]:
    meta = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    meta[k] = v
    return meta

def extract_serial(text: str) -> Optional[str]:
    m = re.search(r"(?:S/N|SN|Serial|Số seri|Số máy)[:\s]+([A-Za-z0-9\-_/]{4,25})", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None

def detect_doc_type_and_form(text: str) -> tuple[str, str, str]:
    for pattern, doc_type, default_form, default_title in FORM_PATTERNS:
        match = pattern.search(text)
        if match:
            found_code = match.group(1).strip()
            return doc_type, found_code, default_title
    return "HANDOVER", "BM04_TA5", "Hồ sơ Bàn giao Nghiệm thu"

def main():
    if not DB_PATH.exists():
        print(f"❌ Không tìm thấy CSDL tại {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Load mapping from PDF filename or path to document_id
    print("⏳ Nạp bản đồ tài liệu từ bảng device_documents...")
    cur.execute("SELECT id, file_path, doc_type, title FROM device_documents;")
    doc_map = {}
    for r in cur.fetchall():
        filename = Path(r["file_path"]).name
        doc_map[filename.lower()] = r["id"]
        doc_map[r["file_path"].lower()] = r["id"]

    print(f"✅ Đã nạp {len(doc_map):,} khóa tài liệu.")

    md_files = list(MD_ROOT.rglob("*.md")) if MD_ROOT.exists() else []
    print(f"🔍 Quét {len(md_files):,} tệp Markdown trong kho OCR...")

    inserted_count = 0
    skipped_count = 0

    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            page_start INTEGER NOT NULL CHECK (page_start >= 1),
            page_end INTEGER NOT NULL CHECK (page_end >= page_start),
            doc_type TEXT NOT NULL,
            form_code TEXT,
            title TEXT,
            extracted_serial TEXT,
            confidence REAL DEFAULT 0.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
            md_anchor TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES device_documents(id) ON DELETE CASCADE
        );
    """)

    # Batch scan
    batch_records = []
    
    for f in md_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        meta = parse_frontmatter(content)
        source_pdf = meta.get("source_pdf") or f.stem + ".pdf"
        pages_total = int(meta.get("pages") or 1)
        if pages_total < 1:
            pages_total = 1

        doc_id = doc_map.get(source_pdf.lower())
        if not doc_id and "pdf_path" in meta:
            doc_id = doc_map.get(meta["pdf_path"].lower())

        if not doc_id:
            skipped_count += 1
            continue

        # Check if already segmented
        cur.execute("SELECT COUNT(*) FROM document_segments WHERE document_id = ?", (doc_id,))
        if cur.fetchone()[0] > 0:
            continue

        doc_type, form_code, title = detect_doc_type_and_form(content)
        serial = extract_serial(content)

        batch_records.append((
            doc_id,
            1,
            pages_total,
            doc_type,
            form_code,
            title,
            serial,
            0.95,
            f.name,
            f"Auto-segmented via OCR Markdown {f.name}"
        ))

        if len(batch_records) >= 500:
            cur.executemany("""
                INSERT INTO document_segments (
                    document_id, page_start, page_end, doc_type, form_code, title, extracted_serial, confidence, md_anchor, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_records)
            conn.commit()
            inserted_count += len(batch_records)
            batch_records = []

    if batch_records:
        cur.executemany("""
            INSERT INTO document_segments (
                document_id, page_start, page_end, doc_type, form_code, title, extracted_serial, confidence, md_anchor, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch_records)
        conn.commit()
        inserted_count += len(batch_records)

    cur.execute("SELECT COUNT(*) FROM document_segments;")
    total_in_db = cur.fetchone()[0]

    conn.close()
    print("\n" + "="*50)
    print("🎉 KẾT QUẢ BATCH PAGE SEGMENTATION PIPELINE:")
    print(f"  - Phân đoạn mới đã nạp: {inserted_count:,}")
    print(f"  - Tệp Markdown bỏ qua (không khớp doc_id): {skipped_count:,}")
    print(f"  - Tổng số phân đoạn trong CSDL: {total_in_db:,}")
    print("="*50)

if __name__ == "__main__":
    main()
