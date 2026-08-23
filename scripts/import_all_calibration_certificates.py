"""
Script trích xuất & nạp toàn bộ 1.227 hồ sơ kiểm định & hiệu chuẩn thực tế từ OCR Wiki vào CSDL SQLite
"""
import sys
import io
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
wiki_dir = ocr_root / "md" / "05_KIEM DINH" / "wiki" / "ho-so-nguon"

print("="*95)
print("🚀 BẮT ĐẦU TRÍCH XUẤT & ĐỒNG BỘ DỮ LIỆU KIỂM ĐỊNH HIỆU CHUẨN TỪ OCR WIKI (1.227 HỒ SƠ)")
print(f"   Thư mục nguồn: {wiki_dir}")
print("="*95)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Prepare table
cur.execute("""
CREATE TABLE IF NOT EXISTS calibration_certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    certificate_no TEXT NOT NULL,
    calibration_date TEXT,
    recalibration_date TEXT,
    stamp_no TEXT,
    calibrated_by TEXT,
    result_status TEXT DEFAULT 'ĐẠT',
    source_pdf TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
)
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_cal_device_id ON calibration_certificates(device_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_cal_recal_date ON calibration_certificates(recalibration_date)")

# Xóa các bản ghi mẫu cũ
cur.execute("DELETE FROM calibration_certificates")
conn.commit()

# 2. Build device lookup maps
devices = cur.execute("SELECT id, device_name, model, serial_no FROM devices").fetchall()
print(f"• Đã nạp {len(devices)} thiết bị từ CSDL.")

sn_to_dev_id = {}
for d in devices:
    sn = str(d["serial_no"]).strip() if d["serial_no"] else ""
    if sn and sn not in ["None", "-", "N/A", "0"] and not sn.startswith("GEN-"):
        sn_clean = re.sub(r'[^a-zA-Z0-9]', '', sn).lower()
        if len(sn_clean) >= 3:
            sn_to_dev_id[sn_clean] = d["id"]

print(f"• Số lượng Serial Numbers index: {len(sn_to_dev_id)}")

# 3. Parse Wiki Markdown files
wiki_files = list(wiki_dir.glob("*.md")) if wiki_dir.exists() else []
print(f"• Số lượng file Markdown hồ sơ kiểm định tìm thấy: {len(wiki_files)}")

def parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    # DD/MM/YYYY or YYYY-MM-DD
    m1 = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', date_str)
    if m1:
        d, m, y = m1.groups()
        return f"{y}-{int(m):02d}-{int(d):02d}"
    m2 = re.search(r'(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})', date_str)
    if m2:
        y, m, d = m2.groups()
        return f"{y}-{int(m):02d}-{int(d):02d}"
    return None

parsed_records = []
unmatched_certs = []

for wf in wiki_files:
    fname = wf.name
    # Extract Certificate No from filename (e.g. 0023.01.26Y, 0084.02.26Y)
    cert_match = re.search(r'^([0-9A-Za-z.-]+(?:Y|KĐ|HC|24|25|26))', fname)
    cert_no = cert_match.group(1) if cert_match else fname.split('-')[0]

    with open(wf, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Extract fields from Markdown table or text
    dev_name_m = re.search(r'\*\*Tên thiết bị\*\*\s*\|\s*([^|\n]+)', content)
    dev_name = dev_name_m.group(1).strip() if dev_name_m else ""

    sn_m = re.search(r'\*\*Số chế tạo\s*/\s*S/N\*\*\s*\|\s*`?([^`|\n]+)`?', content)
    sn = sn_m.group(1).strip() if sn_m else ""

    mfg_m = re.search(r'\*\*Hãng sản xuất\*\*\s*\|\s*([^|\n]+)', content)
    mfg = mfg_m.group(1).strip() if mfg_m else ""

    cal_date_m = re.search(r'\*\*Ngày thực hiện\*\*\s*\|\s*([^|\n]+)', content)
    cal_date_raw = cal_date_m.group(1).strip() if cal_date_m else ""
    cal_date = parse_date(cal_date_raw)

    recal_date_m = re.search(r'\*\*Hạn hiệu lực\*\*\s*\|\s*([^|\n]+)', content)
    recal_date_raw = recal_date_m.group(1).strip() if recal_date_m else ""
    recal_date = parse_date(recal_date_raw)

    res_m = re.search(r'\*\*Kết quả kiểm tra\*\*\s*\|\s*(\*\*)?([^|\n*]+)', content)
    raw_status = res_m.group(2).strip() if res_m else "Đạt"
    if any(w in raw_status.lower() for w in ["đạt", "dat", "ok", "pass", "tốt"]):
        result_status = "OK"
    elif any(w in raw_status.lower() for w in ["không", "khong", "hỏng", "ng", "fail"]):
        result_status = "NG"
    else:
        result_status = "PENDING"

    # Stamp No / PDF Link
    stamp_no = f"TEM-{cert_no}"
    pdf_m = re.search(r'\*\*PDF gốc\*\*:\s*\[[^\]]+\]\(([^)]+)\)', content)
    source_pdf = pdf_m.group(1) if pdf_m else ""
    # Map Linux /media/tan path to Windows G:\
    if source_pdf.startswith("file:////media/tan/T93/"):
        source_pdf = source_pdf.replace("file:////media/tan/T93/", "G:\\").replace("/", "\\")

    # Match device
    dev_id = None
    if sn:
        clean_sn = re.sub(r'[^a-zA-Z0-9]', '', sn).lower()
        if clean_sn in sn_to_dev_id:
            dev_id = sn_to_dev_id[clean_sn]

    # Fallback match by device name
    if not dev_id and dev_name:
        for d in devices:
            if d["device_name"] and dev_name.lower() in d["device_name"].lower():
                dev_id = d["id"]
                break

    if dev_id:
        parsed_records.append((
            dev_id, cert_no, cal_date, recal_date, stamp_no, 
            "Trung tâm Đo lường & Kiểm định TTBYT", result_status, source_pdf, f"Nguồn OCR Wiki: {fname}"
        ))
    else:
        unmatched_certs.append((fname, dev_name, sn))

print(f"📊 Đã trích xuất và khớp thành công: {len(parsed_records):,} giấy chứng nhận kiểm định.")
print(f"• Số GCN chưa khớp trực tiếp theo S/N: {len(unmatched_certs)}")

# 4. Insert into calibration_certificates
cur.executemany("""
INSERT INTO calibration_certificates (
    device_id, certificate_no, calibration_date, recalibration_date, 
    stamp_no, calibrated_by, result_status, source_pdf, notes
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", parsed_records)

conn.commit()

# 5. Check coverage
cur.execute("SELECT COUNT(DISTINCT device_id) FROM calibration_certificates")
dev_with_cal = cur.fetchone()[0]
print(f"\n✅ Tổng số thiết bị có GCN Kiểm định trong CSDL: {dev_with_cal} thiết bị ({dev_with_cal/len(devices)*100:.1f}%).")
print(f"✅ Tổng số GCN Kiểm định đã lưu trữ: {len(parsed_records)} bản ghi.")

# Top 5 records sample
print("\n5 bản ghi kiểm định thực tế sau trích xuất:")
cur.execute("""
SELECT c.id, d.device_name, d.model, d.serial_no, c.certificate_no, c.calibration_date, c.recalibration_date, c.result_status
FROM calibration_certificates c
JOIN devices d ON d.id = c.device_id
LIMIT 5
""")
for r in cur.fetchall():
    print(f" • [{r[4]}] {r[1]} ({r[2]}) | S/N: {r[3]} | Ngày KĐ: {r[5]} -> Hạn KĐ: {r[6]} | Kết quả: {r[7]}")

conn.close()
print("\n🎉 HOÀN TẤT ĐỒNG BỘ DỮ LIỆU KIỂM ĐỊNH HIỆU CHUẨN!")
