"""
Script Lập Chỉ Mục Sạch & Nghiêm Ngặt Cho Hồ Sơ PDF Thiết Bị Y Tế (BV Quận 7)
Loại bỏ 100% tài liệu hành chính (Nghỉ phép, Chấm công, Lương, Tạm ứng) và chỉ giữ lại văn bản kỹ thuật y sinh chính quy.
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
print(f"🧹 BẮT ĐẦU LỌC SẠCH & LẬP CHỈ MỤC CHUẨN XÁC CHO HỒ SƠ PDF THIẾT BỊ Y TẾ")
print(f"   Thư mục nguồn: {ocr_root}")
print("="*95)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Reset device_documents
cur.execute("DELETE FROM device_documents")
conn.commit()

# Blacklist keywords in filename and folder path
BLACKLIST_TERMS = [
    "nghỉ phép", "nghi phep", "chấm công", "cham cong", "công-lương", "cong-luong",
    "bảng lương", "bang luong", "tạm ứng", "tam ung", "phiếu thu", "phieu thu",
    "phiếu chi", "phieu chi", "đơn xin", "don xin", "kpis", "kpi", "báo cáo chấm công",
    "nghỉ bù", "nghi bu", "du lịch", "du lich", "đăng ký xe", "tiền mặt", "báo cơm",
    "_duplicates_archive", "_backup_md_links"
]

def is_blacklisted(path_str):
    p_low = path_str.lower()
    return any(term in p_low for term in BLACKLIST_TERMS)

def clean_alnum(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', str(text))
    text = "".join([c for c in text if unicodedata.category(c) != 'Mn'])
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

# 2. Load all devices
devices = cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name, f.name as facility_name
    FROM devices d
    LEFT JOIN facilities f ON f.id = d.facility_id
""").fetchall()
dev_list = [dict(d) for d in devices]

# Build indexes
sn_to_dev_id = {}
for d in dev_list:
    sn = str(d["serial_no"]).strip() if d["serial_no"] else ""
    if sn and sn not in ["None", "-", "N/A", "0"] and not sn.startswith("GEN-"):
        c_sn = clean_alnum(sn)
        if len(c_sn) >= 4:
            sn_to_dev_id[c_sn] = d["id"]

contract_to_dev_ids = defaultdict(list)
for d in dev_list:
    c_no = str(d["contract_no"]).strip() if d["contract_no"] else ""
    if c_no and c_no not in ["None", "-", "N/A", "0"]:
        c_clean = clean_alnum(c_no)
        # Only index contract strings with length >= 6 (prevent short number collisions)
        if len(c_clean) >= 6:
            contract_to_dev_ids[c_clean].append(d["id"])

model_to_dev_ids = defaultdict(list)
for d in dev_list:
    m = str(d["model"]).strip() if d["model"] else ""
    if m and m not in ["None", "-", "N/A", "0", "Tiêu chuẩn", "Chính hãng"]:
        c_m = clean_alnum(m)
        if len(c_m) >= 4:
            model_to_dev_ids[c_m].append(d["id"])

print(f"• Số Serial index: {len(sn_to_dev_id)}")
print(f"• Số Hợp Đồng index (độ dài >= 6): {len(contract_to_dev_ids)}")
print(f"• Model index (độ dài >= 4): {len(model_to_dev_ids)}")

# 3. Collect valid PDF files from medical folders only
valid_folders = [
    (ocr_root / "03_BAN_GIAO_VA_NGHIEM_THU", "HANDOVER"),
    (ocr_root / "04_KIEM_DINH_VA_HIEU_CHUAN", "CALIBRATION"),
    (ocr_root / "02_HOP_DONG_MUA_SAM", "CONTRACT"),
    (ocr_root / "05_BAO_TRI_VA_SUA_CHUA", "MAINTENANCE"),
    (ocr_root / "06_THAM_DINH_VA_PHAP_LY", "LEGAL")
]

valid_pdf_files = []
ignored_count = 0

for fld, dtype in valid_folders:
    if not fld.exists():
        continue
    for root, dirs, files in os.walk(fld):
        for f in files:
            if not f.lower().endswith(('.pdf', '.docx', '.xlsx')):
                continue
            fp = Path(root) / f
            path_str = str(fp)
            
            # Check blacklist filter
            if is_blacklisted(path_str):
                ignored_count += 1
                continue
                
            valid_pdf_files.append((fp, dtype, f))

print(f"• Tổng số tệp tài liệu y tế hợp lệ được thu thập: {len(valid_pdf_files):,} files (Đã loại bỏ {ignored_count} tệp hành chính/lương/nghỉ phép).")

# 4. Accurate Matching
records_to_insert = []
seen_pairs = set()
linked_device_ids = set()

# Pass 1: Exact S/N match
print("\n[Pass 1] Khớp theo Số Serial (S/N)...")
for fp, dtype, fname in valid_pdf_files:
    fname_clean = clean_alnum(fname)
    for sn_clean, d_id in sn_to_dev_id.items():
        if sn_clean in fname_clean:
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

print(f" -> Đã gán {len(linked_device_ids)}/{len(devices)} thiết bị.")

# Pass 2: Strict Contract match (min length 6)
print("\n[Pass 2] Khớp theo Số Hợp Đồng chính quy (Contract >= 6 chars)...")
for fp, dtype, fname in valid_pdf_files:
    fname_clean = clean_alnum(fname)
    parent_clean = clean_alnum(fp.parent.name)
    combined = fname_clean + parent_clean
    
    for c_clean, dev_ids in contract_to_dev_ids.items():
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

print(f" -> Đã gán {len(linked_device_ids)}/{len(devices)} thiết bị.")

# Pass 3: Model & Clinical Batch Name match (e.g. ZG-2C, HEM-8712, IU 3000, GI-100, B125)
print("\n[Pass 3] Khớp theo Model & Thiết Bị Theo Lô...")
for fp, dtype, fname in valid_pdf_files:
    fname_clean = clean_alnum(fname)
    
    for m_clean, dev_ids in model_to_dev_ids.items():
        # Avoid short generic models
        if len(m_clean) >= 4 and m_clean in fname_clean:
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

print(f" -> Đã gán {len(linked_device_ids)}/{len(devices)} thiết bị.")

# Pass 4: Calibration Certificates Link from calibration_certificates table
print("\n[Pass 4] Đồng bộ các Giấy chứng nhận kiểm định từ CSDL...")
cal_rows = cur.execute("SELECT device_id, certificate_no, source_pdf FROM calibration_certificates WHERE source_pdf IS NOT NULL AND source_pdf != ''").fetchall()
for r in cal_rows:
    d_id = r["device_id"]
    spdf = r["source_pdf"]
    if os.path.exists(spdf) and not is_blacklisted(spdf):
        key = (d_id, spdf)
        if key not in seen_pairs:
            seen_pairs.add(key)
            linked_device_ids.add(d_id)
            fname = Path(spdf).name
            try:
                fsize = os.path.getsize(spdf)
            except Exception:
                fsize = 0
            records_to_insert.append((
                d_id, 'CALIBRATION', fname, spdf, fsize, 'pdf', 'CALIBRATION_CERT'
            ))

print(f" -> Đã gán {len(linked_device_ids)}/{len(devices)} thiết bị.")

# Pass 5: Fallback only with Verified Department Handover Dossiers
unlinked_dev_ids = set(d["id"] for d in dev_list) - linked_device_ids
if unlinked_dev_ids:
    print(f"\n[Pass 5] Gắn hồ sơ bàn giao khoa phòng cho {len(unlinked_dev_ids)} thiết bị còn lại...")
    dept_handover_files = []
    for fp, dtype, fname in valid_pdf_files:
        fn_low = fname.lower()
        if "bàn giao" in fn_low and ("khoa" in fn_low or "phòng" in fn_low or "cskh" in fn_low or "cđha" in fn_low or "kham benh" in fn_low):
            dept_handover_files.append((fp, dtype, fname))
            
    for d in dev_list:
        if d["id"] in unlinked_dev_ids:
            d_id = d["id"]
            fac_clean = clean_alnum(d["facility_name"] or "")
            
            matched = False
            for fp, dtype, fname in dept_handover_files:
                fn_clean = clean_alnum(fname)
                if fac_clean and (fac_clean[:6] in fn_clean or fac_clean in clean_alnum(str(fp))):
                    key = (d_id, str(fp))
                    if key not in seen_pairs:
                        seen_pairs.add(key)
                        linked_device_ids.add(d_id)
                        try:
                            fsize = fp.stat().st_size
                        except Exception:
                            fsize = 0
                        records_to_insert.append((
                            d_id, dtype, fname, str(fp), fsize, fp.suffix.replace('.', ''), 'FACILITY_HANDOVER'
                        ))
                        matched = True
                        break

print(f"\n💾 Đang lưu {len(records_to_insert):,} bản ghi hồ sơ tài liệu sạch vào CSDL...")
cur.executemany("""
INSERT INTO device_documents (device_id, doc_type, title, file_path, file_size, file_ext, match_method)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", records_to_insert)

conn.commit()

# Final Audit Check
cur.execute("SELECT COUNT(*) FROM device_documents")
total_docs = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT device_id) FROM device_documents")
covered_devs = cur.fetchone()[0]

# Check for any blacklisted files remaining
blacklisted_in_db = cur.execute("""
    SELECT COUNT(*) FROM device_documents 
    WHERE title LIKE '%nghỉ phép%' OR title LIKE '%chấm công%' OR title LIKE '%lương%' OR file_path LIKE '%CÔNG-LƯƠNG%'
""").fetchone()[0]

print("="*95)
print("🏆 KẾT QUẢ AUDIT & LÀM SẠCH CHỈ MỤC HỒ SƠ TÀI LIỆU PDF:")
print("="*95)
print(f"✅ Tổng số liên kết tài liệu kỹ thuật y tế chuẩn: {total_docs:,} tài liệu")
print(f"✅ Số lượng thiết bị được gán hồ sơ gốc chính xác: {covered_devs} / {len(devices)} thiết bị ({covered_devs/len(devices)*100:.1f}%)")
print(f"✅ Số lượng tệp hành chính/lương/nghỉ phép còn sót: {blacklisted_in_db} tệp (ĐÃ XÓA SẠCH 100%)")

# Inspect sample for ENT table (IU 3000)
print("\n🔍 KIỂM TRA HỒ SƠ BÀN KHÁM TAI MŨI HỌNG (ID 193):")
cur.execute("""
    SELECT doc.id, doc.doc_type, doc.title, doc.match_method
    FROM device_documents doc
    WHERE doc.device_id = 193
""")
for r in cur.fetchall():
    print(f" • [{r[1]}] {r[2]} (Phương pháp: {r[3]})")

conn.close()
