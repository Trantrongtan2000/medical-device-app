import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
md_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT d.*, f.name as facility_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    WHERE d.device_name LIKE '%Object%' 
       OR d.model LIKE '%Object%'
""").fetchall()

print(f"=== TÌM THẤY {len(rows)} BẢN GHI CÓ TÊN HOẶC MODEL CHỨA 'Object' ===\n")

for r in rows:
    print(f"ID: {r['id']}")
    print(f"  • Tên thiết bị (device_name): {r['device_name']}")
    print(f"  • Model: {r['model']}")
    print(f"  • Serial (S/N): {r['serial_no']}")
    print(f"  • Hãng SX: {r['manufacturer']}")
    print(f"  • Nước SX: {r['country_of_manufacturer']}")
    print(f"  • Khoa phòng: {r['facility_name']}")
    print(f"  • Tệp PDF gốc: {r['source_pdf']}")
    print(f"  • Đường dẫn PDF: {r['pdf_path']}")
    print(f"  • Đường dẫn MD: {r['md_path']}")
    
    # Kiểm tra nội dung tệp MD nếu có
    md_file = None
    if r['md_path']:
        md_file = md_root / r['md_path']
    elif r['source_pdf']:
        cand = md_root / (Path(r['source_pdf']).stem + '.md')
        if cand.exists():
            md_file = cand

    if md_file and md_file.exists():
        print(f"  --- Nội dung trích xuất từ tệp MD ({md_file.name}): ---")
        try:
            lines = md_file.read_text(encoding='utf-8', errors='ignore').splitlines()
            for line in lines[:25]:
                print(f"    | {line}")
        except Exception as e:
            print(f"    Lỗi đọc MD: {e}")
    print("-" * 60)

conn.close()
