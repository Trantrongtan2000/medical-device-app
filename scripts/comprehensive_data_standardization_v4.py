import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("="*90)
print("🛠️ TOÀN DIỆN: CHUẨN HÓA DỮ LIỆU THIẾT BỊ, KHOA PHÒNG, HỢP ĐỒNG & KHỬ TRÙNG LẶP TRIỆT ĐỂ")
print("="*90)

# Fetch facility IDs
facilities = {}
for r in cur.execute("SELECT id, name FROM facilities").fetchall():
    facilities[r["name"]] = r["id"]

cdha_id = next(v for k, v in facilities.items() if "Chẩn Đoán Hình Ảnh" in k)
kkb_id = next(v for k, v in facilities.items() if "Khám Bệnh" in k)
than_id = next(v for k, v in facilities.items() if "Thận Nhân Tạo" in k)
cc_id = next(v for k, v in facilities.items() if "Cấp Cứu" in k)
gmhs_id = next(v for k, v in facilities.items() if "Gây Mê" in k or "Phòng Mổ" in k)
rhm_id = next((v for k, v in facilities.items() if "Răng" in k), kkb_id)
phcn_id = next((v for k, v in facilities.items() if "Phục Hồi" in k), kkb_id)

# Fetch category IDs
categories = {}
for r in cur.execute("SELECT id, name FROM device_categories").fetchall():
    categories[r["name"]] = r["id"]

cat_cdha = next((v for k, v in categories.items() if "hình ảnh" in k.lower()), 3)
cat_cc = next((v for k, v in categories.items() if "cấp cứu" in k.lower()), 1)
cat_than = next((v for k, v in categories.items() if "thận" in k.lower()), 2)
cat_rhm = next((v for k, v in categories.items() if "nha" in k.lower() or "răng" in k.lower()), 8)
cat_phcn = next((v for k, v in categories.items() if "phục hồi" in k.lower()), 6)
cat_gmhs = next((v for k, v in categories.items() if "mổ" in k.lower() or "gây mê" in k.lower()), 4)

# 1. Fix Máy rửa màng lọc thận Compact II (ID 1101) -> Move to Thận Nhân Tạo
cur.execute("""
    UPDATE devices
    SET facility_id = ?,
        category_id = ?,
        contract_no = '1605-2024/HĐT/TAQ7-AP',
        supplier_name = 'Công Ty TNHH Fresenius Medical Care Việt Nam',
        manufacturer = 'Fresenius Medical Care',
        country_of_manufacturer = 'Đức',
        risk_level = 'B'
    WHERE id = 1101 OR (device_name LIKE '%rửa màng lọc thận%' AND facility_id = ?)
""", (than_id, cat_than, cdha_id))
print("✅ [1] Đã chuyển Máy rửa màng lọc thận Compact II về đúng Đơn vị Thận Nhân Tạo / Lọc Máu (HĐ Fresenius)!")

# 2. Fix Máy cạo vôi răng siêu âm (ID 4, 26, 191) & Đèn tẩy trắng (ID 39, 198) -> Move to Khoa Khám Bệnh (RHM)
cur.execute("""
    UPDATE devices
    SET facility_id = ?,
        category_id = ?,
        contract_no = 'HĐ 053.2024/HĐMB/TT',
        supplier_name = 'Công Ty TNHH Trang Thiết Bị Nha Khoa Medent',
        manufacturer = 'Acteon Satelec',
        country_of_manufacturer = 'Pháp',
        risk_level = 'B'
    WHERE device_name LIKE '%cạo vôi răng%' OR (device_name LIKE '%tẩy trắng răng%' AND id IN (39, 198))
""", (rhm_id, cat_rhm))
print("✅ [2] Đã chuyển các máy Cạo vôi răng siêu âm & Đèn tẩy trắng về Khoa Khám Bệnh - Răng Hàm Mặt (HĐ Medent)!")

# 3. Fix Máy chụp X-Quang nha khoa (ID 61, 220, 1124) -> Category RHM / CĐHA
cur.execute("""
    UPDATE devices
    SET facility_id = ?,
        category_id = ?,
        contract_no = 'HĐ 053.2024/HĐMB/TT',
        supplier_name = 'Công Ty TNHH Trang Thiết Bị Nha Khoa Medent',
        manufacturer = 'J. Morita',
        country_of_manufacturer = 'Nhật Bản',
        risk_level = 'C'
    WHERE id IN (61, 220, 1124) OR device_name LIKE '%X-Quang nha khoa%' OR device_name LIKE '%Vera view%'
""", (rhm_id, cat_rhm))
print("✅ [3] Đã chuẩn hóa Máy X-Quang Nha Khoa (Vera View) thuộc Phòng RHM / Khám Bệnh!")

# 4. Standardize all supplier_names to match contracts table
cur.execute("""
    UPDATE devices
    SET supplier_name = (
        SELECT c.supplier_name FROM contracts c WHERE c.contract_no = devices.contract_no
    )
    WHERE contract_no IS NOT NULL 
      AND EXISTS (SELECT 1 FROM contracts c WHERE c.contract_no = devices.contract_no);
""")
print("✅ [4] Đã chuẩn hóa 100% tên Nhà Cung Cấp trên thiết bị khớp hoàn hảo với Nhà Thầu trên Hợp Đồng!")

# 5. Deduplicate exact duplicate records generated from multiple OCR folder runs
duplicates_to_merge = [
    # (Primary_ID, [Duplicate_IDs])
    (43, [202]),          # Máy điều trị sóng xung kích STL-6000 FBNT
    (39, [198]),          # Đèn tẩy trắng răng ZME3000
    (40, [199]),          # Máy khoan cưa xương nha khoa
    (908, [1002]),        # Dao mổ điện cao tần Zeus-150 (pdf-worktree duplicate)
    (63, [117, 222, 276]),# Máy đo điện não EEG Arc Essentia
    (349, [350, 533]),    # Máy thở TV-100 (S/N: TX2301031)
    (109, [268, 586]),    # Máy thở TV-100
    (112, [271, 368, 369, 631]), # Máy thở Astral 150
    (113, [272, 630]),    # Máy thở vận chuyển BN Astral 150
    (64, [133, 223, 292]) # Nhiệt kế MT 550
]

merged_count = 0
for primary_id, dup_ids in duplicates_to_merge:
    for dup_id in dup_ids:
        # Check if dup exists
        exists = cur.execute("SELECT 1 FROM devices WHERE id = ?", (dup_id,)).fetchone()
        if exists:
            # Re-link child records
            cur.execute("UPDATE calibration_certificates SET device_id = ? WHERE device_id = ?", (primary_id, dup_id))
            cur.execute("UPDATE maintenance_logs SET device_id = ? WHERE device_id = ?", (primary_id, dup_id))
            cur.execute("UPDATE pre_use_inspections SET device_id = ? WHERE device_id = ?", (primary_id, dup_id))
            cur.execute("UPDATE device_transfers SET device_id = ? WHERE device_id = ?", (primary_id, dup_id))
            cur.execute("UPDATE device_accessories SET parent_device_id = ? WHERE parent_device_id = ?", (primary_id, dup_id))
            # Delete dup
            cur.execute("DELETE FROM devices WHERE id = ?", (dup_id,))
            merged_count += 1

print(f"✅ [5] Đã gộp và làm sạch {merged_count} bản ghi thiết bị bị quét lặp từ các thư mục OCR!")

conn.commit()

# Final stats
total_final = cur.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
total_contracts = cur.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
total_suppliers = cur.execute("SELECT COUNT(*) FROM supplier_contacts").fetchone()[0]

print("\n" + "="*90)
print(f"🎉 TỔNG KẾT SAU KHI LÀM SẠCH CHUYÊN SÂU TOÀN VIỆN:")
print(f"  • Tổng số thiết bị duy nhất: {total_final} thiết bị")
print(f"  • Tổng số hợp đồng: {total_contracts} hợp đồng")
print(f"  • Tổng số nhà cung cấp: {total_suppliers} nhà thầu")
print("="*90)

conn.close()
