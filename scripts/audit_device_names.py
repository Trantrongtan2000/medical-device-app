import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT id, device_name, model, serial_no, manufacturer, facility_id, source_pdf, md_path
    FROM devices
""").fetchall()

print(f"=== AUDIT TÊN THIẾT BỊ (TỔNG SỐ: {len(rows)}) ===")

name_counts = Counter([r['device_name'] for r in rows])

# Check generic / suspicious names
suspicious = []
for r in rows:
    name = r['device_name']
    if not name or name in ['Thiết bị y tế', 'N/A', 'Unknown', 'Khác'] or name.startswith('BBBG') or name.startswith('0') or len(name) < 3 or '_' in name:
        suspicious.append(r)

print(f"\n1. Số lượng tên thiết bị trùng/nhóm: {len(name_counts)} loại tên khác nhau")
print(f"2. Top 20 tên thiết bị phổ biến nhất:")
for name, cnt in name_counts.most_common(20):
    print(f"   • {name}: {cnt} máy")

print(f"\n3. Số lượng thiết bị có tên nghi ngờ / chưa chuẩn hóa (generic/tên file): {len(suspicious)}")
print("\n--- Mẫu 25 thiết bị có tên cần chuẩn hóa: ---")
for s in suspicious[:25]:
    print(f"   [ID {s['id']}] Name: '{s['device_name']}' | Model: '{s['model']}' | SN: '{s['serial_no']}' | PDF: '{s['source_pdf']}'")

conn.close()
