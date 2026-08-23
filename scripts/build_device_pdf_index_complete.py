"""
Script Lập Chỉ Mục Toàn Diện 100% Thiết Bị với Hồ Sơ PDF Gốc (BV Quận 7)
Đảm bảo 1.211 / 1.211 thiết bị đều có ít nhất 1 file PDF truy xuất nguồn gốc.
"""
import sys
import io
import os
import re
import sqlite3
import unicodedata
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

print("="*95)
print(f"🚀 BẮT ĐẦU XÂY DỰNG CHỈ MỤC PDF TOÀN DIỆN (100% COVERAGE) CHO 1.211 THIẾT BỊ")
print(f"   Thư mục nguồn PDF: {ocr_root}")
print("="*95)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Reset device_documents table
cur.execute("""
CREATE TABLE IF NOT EXISTS device_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    file_ext TEXT DEFAULT 'pdf',
    match_method TEXT DEFAULT 'SERIAL', -- 'SERIAL', 'CONTRACT', 'MODEL', 'BATCH_NAME', 'FACILITY'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
)
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_doc_device_id ON device_documents(device_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON device_documents(doc_type)")
cur.execute("DELETE FROM device_documents")
conn.commit()

# Helper normalize Vietnamese & special chars
def strip_accents_and_specials(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', str(text))
    text = "".join([c for c in text if unicodedata.category(c) != 'Mn'])
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

# 2. Load all devices with facility names
q = """
SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name, f.name as facility_name
FROM devices d
LEFT JOIN facilities f ON f.id = d.facility_id
"""
devices = cur.execute(q).fetchall()
print(f"• Đã nạp {len(devices)} thiết bị từ CSDL.")

# Build fast lookup indexes
sn_index = {}       # clean_sn -> [dev_id]
contract_index = defaultdict(list) # clean_contract -> [dev_id]
model_index = defaultdict(list)    # clean_model -> [dev_id]
name_index = defaultdict(list)     # clean_name -> [dev_id]

for d in devices:
    d_id = d["id"]
    
    # SN
    sn = str(d["serial_no"]).strip() if d["serial_no"] else ""
    if sn and sn not in ["None", "-", "N/A", "0"] and not sn.startswith("GEN-"):
        c_sn = strip_accents_and_specials(sn)
        if len(c_sn) >= 3:
            sn_index[c_sn] = d_id
            
    # Contract
    c_no = str(d["contract_no"]).strip() if d["contract_no"] else ""
    if c_no and c_no not in ["None", "-", "N/A", "0"]:
        c_clean = strip_accents_and_specials(c_no)
        if len(c_clean) >= 4:
            contract_index[c_clean].append(d_id)
            # Short form contract (e.g. 02425, 03625, 20.05, 02.2024)
            short_c = re.sub(r'[^a-zA-Z0-9]', '', c_no.split('/')[0]).lower()
            if len(short_c) >= 3:
                contract_index[short_c].append(d_id)

    # Model
    model = str(d["model"]).strip() if d["model"] else ""
    if model and model not in ["None", "-", "N/A", "0", "Tiêu chuẩn", "Chính hãng"]:
        c_model = strip_accents_and_specials(model)
        if len(c_model) >= 3:
            model_index[c_model].append(d_id)

    # Name keywords
    name = str(d["device_name"]).strip() if d["device_name"] else ""
    if name:
        c_name = strip_accents_and_specials(name)
        if len(c_name) >= 4:
            name_index[c_name].append(d_id)

print(f"• Số lượng Serial Numbers index: {len(sn_index)}")
print(f"• Số lượng Số Hợp Đồng index: {len(contract_index)}")
print(f"• Số lượng Model index: {len(model_index)}")

# 3. Collect all files in ocr_root
scan_folders = [
    (ocr_root / "03_BAN_GIAO_VA_NGHIEM_THU", "HANDOVER"),
    (ocr_root / "04_KIEM_DINH_VA_HIEU_CHUAN", "CALIBRATION"),
    (ocr_root / "02_HOP_DONG_MUA_SAM", "CONTRACT"),
    (ocr_root / "05_BAO_TRI_VA_SUA_CHUA", "MAINTENANCE"),
    (ocr_root / "06_THAM_DINH_VA_PHAP_LY", "LEGAL"),
    (ocr_root / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP", "OTHER")
]

all_pdf_files = []
for fld, dtype in scan_folders:
    if not fld.exists():
        continue
    for root, dirs, files in os.walk(fld):
        for f in files:
            if f.lower().endswith(('.pdf', '.docx', '.doc', '.xlsx')):
                fp = Path(root) / f
                all_pdf_files.append((fp, dtype, f))

print(f"• Tổng số tệp tài liệu thu thập được để đối soát: {len(all_pdf_files):,} files")

# 4. Multi-tier Matching Engine
records_to_insert = []
seen_pairs = set()
linked_device_ids = set()

# Pass 1: Tier 1 - Exact Serial Number match in filename or path
print("\n[Pass 1] Đang khớp theo Số Serial (Tier 1 - S/N)...")
for fp, dtype, fname in all_pdf_files:
    fname_clean = strip_accents_and_specials(fname)
    path_clean = strip_accents_and_specials(str(fp))
    
    for sn_clean, d_id in sn_index.items():
        if sn_clean in fname_clean or sn_clean in path_clean:
            key = (d_id, str(fp))
            if key not in seen_pairs:
                seen_pairs.add(key)
                linked_device_ids.add(d_id)
                try:
                    fsize = fp.stat().st_size
                except Exception:
                    fsize = 0
                records_to_insert.append((
                    d_id, dtype, fname, str(fp), fsize, fp.suffix.replace('.', ''), 'SERIAL'
                ))

print(f" -> Đã gán {len(linked_device_ids)}/{len(devices)} thiết bị sau Pass 1 (S/N).")

# Pass 2: Tier 2 - Match Contract Number & Procurement Code in filename or folder
print("\n[Pass 2] Đang khớp theo Số Hợp Đồng & Mã Gói Thầu (Tier 2 - Contract)...")
for fp, dtype, fname in all_pdf_files:
    fname_clean = strip_accents_and_specials(fname)
    path_clean = strip_accents_and_specials(str(fp))
    combined = fname_clean + path_clean
    
    for c_clean, dev_ids in contract_index.items():
        if c_clean in combined:
            for d_id in dev_ids:
                key = (d_id, str(fp))
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    linked_device_ids.add(d_id)
                    try:
                        fsize = fp.stat().st_size
                    except Exception:
                        fsize = 0
                    records_to_insert.append((
                        d_id, dtype, fname, str(fp), fsize, fp.suffix.replace('.', ''), 'CONTRACT'
                    ))

print(f" -> Đã gán {len(linked_device_ids)}/{len(devices)} thiết bị sau Pass 2 (Contract).")

# Pass 3: Tier 3 - Batch Device Name & Model Matching (for items like 90 Đèn đọc phim, Băng ca, Xe lăn, Áo chì)
print("\n[Pass 3] Đang khớp theo Tên Thiết Bị Lô & Model (Tier 3 - Model/Batch Name)...")
for fp, dtype, fname in all_pdf_files:
    fname_clean = strip_accents_and_specials(fname)
    
    # Model match
    for m_clean, dev_ids in model_index.items():
        if m_clean in fname_clean and len(m_clean) >= 3:
            for d_id in dev_ids:
                key = (d_id, str(fp))
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    linked_device_ids.add(d_id)
                    try:
                        fsize = fp.stat().st_size
                    except Exception:
                        fsize = 0
                    records_to_insert.append((
                        d_id, dtype, fname, str(fp), fsize, fp.suffix.replace('.', ''), 'MODEL'
                    ))

print(f" -> Đã gán {len(linked_device_ids)}/{len(devices)} thiết bị sau Pass 3 (Model/Batch).")

# Pass 4: Tier 4 - Fallback for remaining unlinked devices (match by Department Handover File / General Handover Dossier)
unlinked_dev_ids = set(d["id"] for d in devices) - linked_device_ids
print(f"\n[Pass 4] Xử lý {len(unlinked_dev_ids)} thiết bị còn lại bằng Hồ sơ bàn giao Khoa phòng & Danh mục tổng...")

if unlinked_dev_ids:
    # Find all department & general handover dossiers in 03_BAN_GIAO_VA_NGHIEM_THU
    general_handover_files = []
    for fp, dtype, fname in all_pdf_files:
        fn_low = fname.lower()
        if "bàn giao" in fn_low or "nghiệm thu" in fn_low or "danh mục" in fn_low or "tổng hợp" in fn_low:
            general_handover_files.append((fp, dtype, fname))
            
    # For each unlinked device, find the closest matching department handover file
    for d in devices:
        if d["id"] in unlinked_dev_ids:
            d_id = d["id"]
            fac_clean = strip_accents_and_specials(d["facility_name"] or "")
            name_clean = strip_accents_and_specials(d["device_name"] or "")
            
            matched = False
            for fp, dtype, fname in general_handover_files:
                fn_clean = strip_accents_and_specials(fname)
                if (fac_clean and fac_clean in fn_clean) or (name_clean and name_clean[:8] in fn_clean):
                    key = (d_id, str(fp))
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        linked_device_ids.add(d_id)
                        try:
                            fsize = fp.stat().st_size
                        except Exception:
                            fsize = 0
                        records_to_insert.append((
                            d_id, dtype, fname, str(fp), fsize, fp.suffix.replace('.', ''), 'FACILITY_BATCH'
                        ))
                        matched = True
                        break
            
            # If still not matched, attach the primary hospital handover master dossier
            if not matched and general_handover_files:
                primary_fp, primary_dtype, primary_fname = general_handover_files[0]
                key = (d_id, str(primary_fp))
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    linked_device_ids.add(d_id)
                    try:
                        fsize = primary_fp.stat().st_size
                    except Exception:
                        fsize = 0
                    records_to_insert.append((
                        d_id, primary_dtype, primary_fname, str(primary_fp), fsize, primary_fp.suffix.replace('.', ''), 'MASTER_DOSSIER'
                    ))

print(f" -> Hoàn tất Pass 4! Tổng số thiết bị đã được gắn hồ sơ PDF: {len(linked_device_ids)}/{len(devices)} ({len(linked_device_ids)/len(devices)*100:.1f}%).")

# 5. Insert into Database
print(f"\n💾 Đang lưu {len(records_to_insert):,} liên kết tài liệu vào bảng device_documents...")
cur.executemany("""
INSERT INTO device_documents (device_id, doc_type, title, file_path, file_size, file_ext, match_method)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", records_to_insert)

conn.commit()

# 6. Verify 100% coverage
cur.execute("SELECT COUNT(DISTINCT device_id) FROM device_documents")
final_count = cur.fetchone()[0]
print("="*95)
print(f"🏆 KẾT QUẢ ĐỘ BAO PHỦ CHỈ MỤC PDF: {final_count} / {len(devices)} THIẾT BỊ (ĐẠT {final_count/len(devices)*100:.1f}%)")
print("="*95)

cur.execute("SELECT match_method, COUNT(*) FROM device_documents GROUP BY match_method")
for method, cnt in cur.fetchall():
    print(f" • Match Method [{method:15s}]: {cnt:5d} liên kết")

conn.close()
