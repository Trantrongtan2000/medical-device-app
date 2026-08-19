import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("="*80)
print("🎯 CHUẨN HÓA CHÍNH XÁC: DUY NHẤT 2 MÁY ĐO MẬT ĐỘ XƯƠNG DEXA LUNAR PRODIGY TẠI KHOA CĐHA")
print("="*80)

# Get CDHA facility_id & category_id
cur.execute("SELECT id FROM facilities WHERE name LIKE '%Chẩn Đoán Hình Ảnh%' LIMIT 1")
cdha_fac_id = cur.fetchone()[0]

cur.execute("SELECT id FROM device_categories WHERE name LIKE '%Chẩn đoán hình ảnh%' LIMIT 1")
cdha_cat_row = cur.fetchone()
cdha_cat_id = cdha_cat_row[0] if cdha_cat_row else 3

primary_id_1 = 42
primary_id_2 = 170
duplicate_ids = [169, 201, 328, 329, 638, 639, 1122]

# 1. Re-link foreign keys before deleting duplicates
for dup_id in duplicate_ids:
    target_id = primary_id_1 if dup_id in (169, 328, 638, 1122) else primary_id_2
    
    cur.execute("UPDATE calibration_certificates SET device_id = ? WHERE device_id = ?", (target_id, dup_id))
    cur.execute("UPDATE maintenance_logs SET device_id = ? WHERE device_id = ?", (target_id, dup_id))
    cur.execute("UPDATE pre_use_inspections SET device_id = ? WHERE device_id = ?", (target_id, dup_id))
    cur.execute("UPDATE device_transfers SET device_id = ? WHERE device_id = ?", (target_id, dup_id))
    cur.execute("UPDATE device_accessories SET parent_device_id = ? WHERE parent_device_id = ?", (target_id, dup_id))
    
    # Delete duplicate device record
    cur.execute("DELETE FROM devices WHERE id = ?", (dup_id,))

# 2. Update Machine 1
cur.execute("""
    UPDATE devices
    SET device_name = 'Máy đo mật độ xương DEXA Prodigy #01',
        model = 'Lunar Prodigy',
        serial_no = '513804MA',
        facility_id = ?,
        category_id = ?,
        contract_no = 'HĐ 01.2024/HĐMB/TD',
        supplier_name = 'Công Ty TNHH Thiết Bị Y Tế Thành Đạt',
        manufacturer = 'GE Healthcare / Lunar',
        country_of_manufacturer = 'Mỹ',
        risk_level = 'C',
        status = 'IN_SERVICE',
        source_pdf = '05_KIEM DINH/2025/Loãng xương - 513804MA.pdf',
        notes = 'Hệ thống đo mật độ khoáng xương DEXA Lunar Prodigy toàn thân số 1'
    WHERE id = ?
""", (cdha_fac_id, cdha_cat_id, primary_id_1))

# 3. Update Machine 2
cur.execute("""
    UPDATE devices
    SET device_name = 'Máy đo mật độ xương DEXA Prodigy #02',
        model = 'Lunar Prodigy',
        serial_no = '513847MA',
        facility_id = ?,
        category_id = ?,
        contract_no = 'HĐ 01.2024/HĐMB/TD',
        supplier_name = 'Công Ty TNHH Thiết Bị Y Tế Thành Đạt',
        manufacturer = 'GE Healthcare / Lunar',
        country_of_manufacturer = 'Mỹ',
        risk_level = 'C',
        status = 'IN_SERVICE',
        source_pdf = '05_KIEM DINH/2025/Loãng xương - 513847MA.pdf',
        notes = 'Hệ thống đo mật độ khoáng xương DEXA Lunar Prodigy toàn thân số 2'
    WHERE id = ?
""", (cdha_fac_id, cdha_cat_id, primary_id_2))

# 4. Update Contract HĐ 01.2024/HĐMB/TD
cur.execute("""
    UPDATE contracts
    SET contract_name = 'Hợp đồng Cung Cấp 02 Hệ Thống Đo Mật Độ Khoáng Xương DEXA Lunar Prodigy Toàn Thân',
        supplier_name = 'Công Ty TNHH Thiết Bị Y Tế Thành Đạt',
        notes = 'Gói thầu 02 máy đo loãng xương DEXA Lunar Prodigy chuyên sâu Khoa CĐHA (S/N: 513804MA, 513847MA)'
    WHERE contract_no = 'HĐ 01.2024/HĐMB/TD'
""")

conn.commit()

# Check total devices in database
total_devs = cur.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
dexa_devs = cur.execute("SELECT id, device_name, model, serial_no, contract_no, supplier_name, facility_id FROM devices WHERE contract_no = 'HĐ 01.2024/HĐMB/TD'").fetchall()

print(f"\n✅ Tổng số thiết bị y tế trong toàn viện sau khi làm sạch: {total_devs} thiết bị")
print("✅ Danh sách chính thức CHÍNH XÁC 02 máy đo loãng xương DEXA tại Khoa CĐHA:")
for d in dexa_devs:
    print(f"  • ID {d[0]}: {d[1]} | Model: {d[2]} | S/N: {d[3]} | HĐ: {d[4]} | NCC: {d[5]}")

conn.close()
