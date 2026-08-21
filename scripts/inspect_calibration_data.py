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

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("="*95)
print("🔍 KIỂM TRA DỮ LIỆU KIỂM ĐỊNH HIỆU CHUẨN HIỆN TẠI TRONG CSDL:")
print("="*95)

cur.execute("SELECT COUNT(*) FROM calibration_certificates")
print(f"• Số lượng bản ghi trong bảng [calibration_certificates]: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM inspections")
print(f"• Số lượng bản ghi trong bảng [inspections]: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM maintenance_schedules")
print(f"• Số lượng bản ghi trong bảng [maintenance_schedules]: {cur.fetchone()[0]}")

# Sample calibration records in DB
print("\n10 bản ghi mẫu trong calibration_certificates:")
rows = cur.execute("SELECT * FROM calibration_certificates LIMIT 10").fetchall()
for r in rows:
    print(f" • [ID {r['id']:3d}] DevID: {r['device_id']:4d} | Số GCN: {r['certificate_no']} | Ngày KĐ: {r['calibration_date']} | Hạn KĐ: {r['recalibration_date']} | Tem: {r['stamp_no']} | Đơn vị: {r['calibrated_by']} | Kết quả: {r['result_status']}")

# Check extracted files in G:\BV QUẬN 7_OCR_WORK_20260712\md\05_KIEM DINH\wiki\ho-so-nguon\
wiki_dir = ocr_root / "md" / "05_KIEM DINH" / "wiki" / "ho-so-nguon"
print(f"\n📂 Kiểm tra thư mục trích xuất OCR: {wiki_dir}")
if wiki_dir.exists():
    wiki_files = list(wiki_dir.glob("*.md"))
    print(f"• Tìm thấy {len(wiki_files)} files Markdown hồ sơ kiểm định.")
    print("5 file mẫu:")
    for wf in wiki_files[:5]:
        print(f" - {wf.name}")
        # Print first few lines of sample
        with open(wf, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline().strip() for _ in range(8)]
            for l in lines:
                if l: print(f"    {l}")
