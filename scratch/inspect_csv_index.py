import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

csv_file = Path(r'G:\BV QUẬN 7_OCR_WORK_20260712\00_HE_THONG_VA_SCRIPTS\_ocr_device_index.csv')
if csv_file.exists():
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        valid_rows = [r for r in reader if any(r.values())]
        print(f"📊 TỔNG SỐ BẢN GHI HỢP LỆ TRONG _ocr_device_index.csv: {len(valid_rows):,} bản ghi")
        print("\n🔍 10 MẪU THIẾT BỊ BÓC TÁCH ĐIỂN HÌNH TỪ OCR:")
        for idx, r in enumerate(valid_rows[:10], 1):
            name = r.get('equipment_name') or 'N/A'
            model = r.get('model') or 'N/A'
            sn = r.get('serial_no') or 'N/A'
            dept = r.get('department') or 'N/A'
            doc = r.get('doc_type') or 'N/A'
            pdf = r.get('source_pdf') or 'N/A'
            print(f"  {idx:02d}. [{name}] | Model: {model} | SN: {sn} | Khoa: {dept} | Loại VB: {doc}")
            print(f"      File gốc: {pdf}")
