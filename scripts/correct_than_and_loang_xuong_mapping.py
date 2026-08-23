import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("="*80)
print("🛠️ ĐÍNH CHÍNH & CHUẨN HÓA DỮ LIỆU: MÁY ĐO LOÃNG XƯƠNG DEXA VS HỆ THỐNG THẬN NHÂN TẠO")
print("="*80)

# Get CDHA facility_id
cur.execute("SELECT id FROM facilities WHERE name LIKE '%Chẩn Đoán Hình Ảnh%' LIMIT 1")
cdha_fac_id = cur.fetchone()[0]

# Get CDHA category_id
cur.execute("SELECT id FROM device_categories WHERE name LIKE '%Chẩn đoán hình ảnh%' LIMIT 1")
cdha_cat_row = cur.fetchone()
cdha_cat_id = cdha_cat_row[0] if cdha_cat_row else 3

# Get Thận Nhân Tạo facility_id
cur.execute("SELECT id FROM facilities WHERE name LIKE '%Thận Nhân Tạo%' LIMIT 1")
than_fac_id = cur.fetchone()[0]

# 1. Update DEXA / Đo loãng xương devices
cur.execute("""
    UPDATE devices
    SET device_name = 'Máy đo mật độ xương DEXA Prodigy',
        model = 'Lunar Prodigy',
        facility_id = ?,
        category_id = ?,
        contract_no = 'HĐ 01.2024/HĐMB/TD',
        supplier_name = 'Công Ty TNHH Thiết Bị Y Tế Thành Đạt',
        manufacturer = 'GE Healthcare / Lunar',
        country_of_manufacturer = 'Mỹ',
        risk_level = 'C'
    WHERE id IN (42, 169, 170, 201, 328, 329, 638, 639, 1122)
       OR device_name LIKE '%loãng xương%'
       OR model LIKE '%prodigy%'
""", (cdha_fac_id, cdha_cat_id))
updated_dexa = cur.rowcount
print(f"✅ Đã đính chính {updated_dexa} máy đo loãng xương DEXA về Khoa CĐHA & HĐ 01.2024/HĐMB/TD (Thành Đạt / GE)!")

# 2. Update Contract 1605-2024/HĐT/TAQ7-AP in contracts table
cur.execute("""
    UPDATE contracts
    SET contract_name = 'Hợp đồng Thuê & Vận Hành Hệ Thống Máy Thận Nhân Tạo Fresenius 4008S / 5008S & Hệ Thống RO Lọc Máu',
        supplier_name = 'Công Ty TNHH Fresenius Medical Care Việt Nam',
        notes = 'Hệ thống máy thận nhân tạo 4008S, 5008S, máy rửa quả lọc, máy RO và cảm biến SpO2'
    WHERE contract_no = '1605-2024/HĐT/TAQ7-AP'
""")

# 3. Update Contract HĐ 01.2024/HĐMB/TD in contracts table
cur.execute("""
    UPDATE contracts
    SET contract_name = 'Hợp đồng Cung Cấp Hệ Thống Đo Mật Độ Khoáng Xương DEXA Lunar Prodigy Toàn Thân',
        supplier_name = 'Công Ty TNHH Thiết Bị Y Tế Thành Đạt',
        notes = 'Máy đo loãng xương DEXA Lunar Prodigy chuyên sâu Khoa CĐHA'
    WHERE contract_no = 'HĐ 01.2024/HĐMB/TD'
""")

# 4. Standardize Fresenius hemodialysis machines
cur.execute("""
    UPDATE devices
    SET manufacturer = 'Fresenius Medical Care',
        country_of_manufacturer = 'Đức',
        facility_id = ?,
        risk_level = 'C'
    WHERE contract_no = '1605-2024/HĐT/TAQ7-AP' 
      AND (device_name LIKE '%thận%' OR device_name LIKE '%tnt%' OR device_name LIKE '%ro%')
""", (than_fac_id,))
print(f"✅ Đã chuẩn hóa thiết bị Thận nhân tạo Fresenius theo HĐ 1605-2024/HĐT/TAQ7-AP!")

conn.commit()

# Re-verify counts
cur.execute("SELECT contract_no, COUNT(*) FROM devices WHERE contract_no IN ('1605-2024/HĐT/TAQ7-AP', 'HĐ 01.2024/HĐMB/TD') GROUP BY contract_no")
for r in cur.fetchall():
    print(f"  • HĐ {r[0]}: {r[1]} thiết bị")

conn.close()
print("\n🎉 HOÀN TẤT ĐÍNH CHÍNH DỮ LIỆU!")
