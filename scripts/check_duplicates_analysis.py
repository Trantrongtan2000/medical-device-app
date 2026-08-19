import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*70)
print("📊 BÁO CÁO PHÂN TÍCH DỮ LIỆU THIẾT BỊ TRÙNG LẶP TẠI BV QUẬN 7")
print("="*70)

# Total devices
total = c.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
print(f"Tổng số bản ghi trong bảng `devices`: {total}")

# 1. Trùng theo Serial No (khác rỗng, N/A, -)
dup_serial = c.execute("""
    SELECT serial_no, COUNT(*) as cnt, GROUP_CONCAT(id) as ids, GROUP_CONCAT(device_name, ' | ') as names 
    FROM devices 
    WHERE serial_no IS NOT NULL AND TRIM(serial_no) != '' AND TRIM(serial_no) != 'N/A' AND TRIM(serial_no) != '-'
    GROUP BY LOWER(TRIM(serial_no))
    HAVING cnt > 1
""").fetchall()

print(f"\n1. Trùng lặp theo Số Serial (S/N): {len(dup_serial)} nhóm trùng")
for row in dup_serial:
    print(f"   - S/N: [{row[0]}] | {row[1]} bản ghi | IDs: [{row[2]}] | Tên: {row[3][:80]}...")

# 2. Trùng lặp hoàn toàn theo (Tên thiết bị + Model + Serial No)
dup_exact = c.execute("""
    SELECT device_name, model, serial_no, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
    FROM devices
    WHERE serial_no IS NOT NULL AND TRIM(serial_no) != '' AND TRIM(serial_no) != 'N/A' AND TRIM(serial_no) != '-'
    GROUP BY LOWER(TRIM(device_name)), LOWER(TRIM(model)), LOWER(TRIM(serial_no))
    HAVING cnt > 1
""").fetchall()
print(f"\n2. Trùng hoàn toàn (Tên + Model + Serial S/N): {len(dup_exact)} nhóm trùng")
for row in dup_exact:
    print(f"   - Tên: {row[0]} | Model: {row[1]} | S/N: {row[2]} | {row[3]} bản ghi | IDs: [{row[4]}]")

# 3. Trùng lặp theo (Tên thiết bị + Model + Khoa phòng) khi không có serial
dup_no_serial = c.execute("""
    SELECT device_name, model, facility_id, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
    FROM devices
    WHERE serial_no IS NULL OR TRIM(serial_no) = '' OR TRIM(serial_no) = 'N/A' OR TRIM(serial_no) = '-'
    GROUP BY LOWER(TRIM(device_name)), LOWER(TRIM(model)), facility_id
    HAVING cnt > 1
""").fetchall()
print(f"\n3. Nhóm cùng tên + model + khoa phòng (Thiết bị thông thường/dụng cụ không serial): {len(dup_no_serial)} nhóm")
for row in dup_no_serial[:8]:
    print(f"   - Tên: {row[0]} | Model: {row[1]} | Khoa ID: {row[2]} | {row[3]} bản ghi | IDs: [{row[4]}]")

# 4. Trùng theo Số Giấy Chứng Nhận Kiểm Định (certification_no)
dup_cert = c.execute("""
    SELECT certification_no, COUNT(*) as cnt, GROUP_CONCAT(id) as ids, GROUP_CONCAT(device_name, ' | ') as names
    FROM devices
    WHERE certification_no IS NOT NULL AND TRIM(certification_no) != '' AND TRIM(certification_no) != 'N/A'
    GROUP BY LOWER(TRIM(certification_no))
    HAVING cnt > 1
""").fetchall()
print(f"\n4. Trùng theo Số GCN Kiểm Định (certification_no): {len(dup_cert)} nhóm trùng")
for row in dup_cert:
    print(f"   - GCN: {row[0]} | {row[1]} bản ghi | IDs: [{row[2]}] | Tên: {row[3][:80]}...")

conn.close()
print("\n" + "="*70)
