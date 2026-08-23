"""
Script tạo bảng và quét lập chỉ mục toàn bộ file PDF từ G:\BV QUẬN 7_OCR_WORK_20260712 liên kết tới 1.211 thiết bị
"""
import sys
import io
import os
import re
import sqlite3
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

print("="*90)
print(f"🚀 BẮT ĐẦU XÂY DỰNG CHỈ MỤC TÀI LIỆU PDF CHO 1.211 THIẾT BỊ Y TẾ")
print(f"   Thư mục nguồn PDF: {ocr_root}")
print("="*90)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Tạo bảng device_documents nếu chưa có
cur.execute("""
CREATE TABLE IF NOT EXISTS device_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,          -- 'HANDOVER', 'CALIBRATION', 'CONTRACT', 'MAINTENANCE', 'LEGAL', 'OTHER'
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    file_ext TEXT DEFAULT 'pdf',
    match_method TEXT DEFAULT 'SERIAL', -- 'SERIAL', 'CONTRACT', 'MODEL', 'MANUAL'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
)
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_doc_device_id ON device_documents(device_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON device_documents(doc_type)")

# Xóa chỉ mục cũ nếu cần làm mới
cur.execute("DELETE FROM device_documents")
conn.commit()

# 2. Lấy danh sách thiết bị
cur.execute("SELECT id, device_name, model, serial_no, contract_no FROM devices")
devices = cur.fetchall()
print(f"• Đã nạp {len(devices)} thiết bị từ CSDL.")

# Tạo từ điển tra cứu nhanh
# S/N -> device_id
sn_to_dev = {}
for d_id, d_name, d_model, d_sn, d_contract in devices:
    if d_sn and str(d_sn).strip() not in ["None", "-", "N/A", "", "0"]:
        sn_clean = re.sub(r'[^a-zA-Z0-9]', '', str(d_sn).lower())
        if len(sn_clean) >= 3:
            sn_to_dev[sn_clean] = d_id

# Contract -> list of device_ids
contract_to_devs = {}
for d_id, d_name, d_model, d_sn, d_contract in devices:
    if d_contract and str(d_contract).strip() not in ["None", "-", "N/A", "", "0"]:
        c_clean = re.sub(r'[^a-zA-Z0-9]', '', str(d_contract).lower())
        if len(c_clean) >= 4:
            contract_to_devs.setdefault(c_clean, []).append(d_id)

print(f"• Số lượng Serial Numbers hợp lệ lập chỉ mục: {len(sn_to_dev)}")
print(f"• Số lượng Số Hợp Đồng hợp lệ lập chỉ mục: {len(contract_to_devs)}")

# 3. Quét các thư mục PDF chính
scan_targets = [
    (ocr_root / "03_BAN_GIAO_VA_NGHIEM_THU", "HANDOVER"),
    (ocr_root / "04_KIEM_DINH_VA_HIEU_CHUAN", "CALIBRATION"),
    (ocr_root / "02_HOP_DONG_MUA_SAM", "CONTRACT"),
    (ocr_root / "05_BAO_TRI_VA_SUA_CHUA", "MAINTENANCE"),
    (ocr_root / "06_THAM_DINH_VA_PHAP_LY", "LEGAL")
]

records_to_insert = []
seen_pairs = set()

for target_dir, doc_type in scan_targets:
    if not target_dir.exists():
        continue
    print(f"📂 Đang quét: {target_dir.name}...")
    
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if not f.lower().endswith(('.pdf', '.docx', '.doc', '.xlsx')):
                continue
            fp = Path(root) / f
            fname_clean = re.sub(r'[^a-zA-Z0-9]', '', f.lower())
            
            # Match 1: Check Serial No in filename
            matched_by_sn = False
            for sn_clean, d_id in sn_to_dev.items():
                if sn_clean in fname_clean:
                    key = (d_id, str(fp))
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        try:
                            fsize = fp.stat().st_size
                        except Exception:
                            fsize = 0
                        records_to_insert.append((
                            d_id, doc_type, f, str(fp), fsize, fp.suffix.replace('.', ''), 'SERIAL'
                        ))
                        matched_by_sn = True

            # Match 2: Check Contract No in filename or parent folder
            if not matched_by_sn:
                root_clean = re.sub(r'[^a-zA-Z0-9]', '', str(root).lower())
                combined = fname_clean + root_clean
                for c_clean, dev_ids in contract_to_devs.items():
                    if c_clean in combined:
                        for d_id in dev_ids:
                            key = (d_id, str(fp))
                            if key not in seen_pairs:
                                seen_pairs.add(key)
                                try:
                                    fsize = fp.stat().st_size
                                except Exception:
                                    fsize = 0
                                records_to_insert.append((
                                    d_id, doc_type, f, str(fp), fsize, fp.suffix.replace('.', ''), 'CONTRACT'
                                ))

print(f"\n📊 Tổng số liên kết tài liệu PDF tìm thấy: {len(records_to_insert):,} tài liệu.")

# 4. Lưu vào CSDL
cur.executemany("""
INSERT INTO device_documents (device_id, doc_type, title, file_path, file_size, file_ext, match_method)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", records_to_insert)

conn.commit()

# 5. Thống kê kết quả
cur.execute("SELECT COUNT(DISTINCT device_id) FROM device_documents")
dev_with_docs = cur.fetchone()[0]
print(f"✅ Đã gán tài liệu thành công cho {dev_with_docs}/{len(devices)} thiết bị ({dev_with_docs/len(devices)*100:.1f}%).")

cur.execute("SELECT doc_type, COUNT(*) FROM device_documents GROUP BY doc_type")
for dtype, cnt in cur.fetchall():
    print(f" • [{dtype:12s}]: {cnt:5d} tài liệu")

conn.close()
print("🎉 Hoàn tất xây dựng chỉ mục PDF!")
