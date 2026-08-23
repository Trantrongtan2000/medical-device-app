import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("="*90)
print("🔍 TỔNG KIỂM TOÁN CHUYÊN SÂU DỮ LIỆU THIẾT BỊ Y TẾ (DEEP CLINICAL DATA QUALITY AUDIT)")
print("="*90)

# 1. Total count
total_devices = cur.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
print(f"📌 Tổng số thiết bị trong CSDL hiện tại: {total_devices}")

# 2. Check for duplicate real serials (non-GEN serials or identical serials)
print("\n--- 1. KIỂM TRA TRÙNG LẶP SERIAL NUMBER THỰC TẾ ---")
cur.execute("""
    SELECT serial_no, COUNT(*) as cnt, GROUP_CONCAT(id) as ids, GROUP_CONCAT(device_name) as names
    FROM devices
    WHERE serial_no NOT LIKE 'GEN-%' AND serial_no != 'N/A' AND serial_no IS NOT NULL AND TRIM(serial_no) != ''
    GROUP BY serial_no
    HAVING cnt > 1
""")
duplicate_serials = cur.fetchall()
if duplicate_serials:
    print(f"⚠️ Phát hiện {len(duplicate_serials)} số serial thực tế bị trùng lặp:")
    for r in duplicate_serials:
        print(f"  • S/N: {r['serial_no']} (x{r['cnt']}) | IDs: {r['ids']} | Tên: {r['names']}")
else:
    print("✅ Không có số Serial thực tế nào bị trùng lặp!")

# 3. Check for exact duplicate devices by (device_name, model, source_pdf basename)
print("\n--- 2. KIỂM TRA CÁC BẢN GHI TRÙNG LẶP TÊN + MODEL + NGUỒN PDF ---")
cur.execute("""
    SELECT device_name, model, 
           COUNT(*) as cnt, 
           GROUP_CONCAT(id) as ids, 
           GROUP_CONCAT(DISTINCT contract_no) as contracts,
           GROUP_CONCAT(DISTINCT facility_id) as facilities,
           GROUP_CONCAT(DISTINCT source_pdf) as pdfs
    FROM devices
    WHERE model != 'N/A' AND model IS NOT NULL AND TRIM(model) != ''
    GROUP BY device_name, model
    HAVING cnt > 1
""")
duplicate_models = cur.fetchall()
print(f"Phát hiện {len(duplicate_models)} nhóm thiết bị có cùng Tên + Model:")
for r in duplicate_models:
    # Filter suspicious ones (like 1-2 machines that got duplicated vs actual multi-unit items like thermometers or monitors)
    if r['cnt'] <= 10:
        print(f"  • [{r['cnt']} bản ghi] {r['device_name']} (Model: {r['model']}) | IDs: {r['ids']} | HĐ: {r['contracts']} | PDFs: {r['pdfs']}")

# 4. Check for high-tech imaging devices not in CĐHA (MRI, CT, X-Quang, DEXA, C-Arm, Siêu Âm)
print("\n--- 3. KIỂM TRA THIẾT BỊ CHẨN ĐOÁN HÌNH ẢNH ĐẶT SAI KHOA PHÒNG ---")
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name, f.name as fac_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    WHERE (d.device_name LIKE '%mri%' 
        OR d.device_name LIKE '%cắt lớp%' 
        OR d.device_name LIKE '%ct-scanner%' 
        OR d.device_name LIKE '%x-quang%' 
        OR d.device_name LIKE '%dexa%'
        OR d.device_name LIKE '%c-arm%'
        OR d.device_name LIKE '%mammography%'
        OR d.device_name LIKE '%siêu âm 4d%'
        OR d.device_name LIKE '%siêu âm 5d%')
      AND f.name NOT LIKE '%Chẩn Đoán Hình Ảnh%'
      AND f.name NOT LIKE '%Kho Lưu Trữ%'
""")
misplaced_imaging = cur.fetchall()
if misplaced_imaging:
    print(f"⚠️ Phát hiện {len(misplaced_imaging)} thiết bị CĐHA đặt sai khoa phòng:")
    for r in misplaced_imaging:
        print(f"  • ID {r['id']}: {r['device_name']} ({r['model']}) -> Hiện ở: {r['fac_name']} (HĐ: {r['contract_no']})")
else:
    print("✅ 100% thiết bị CĐHA đặt đúng Khoa Chẩn Đoán Hình Ảnh!")

# 5. Check for Hemodialysis / RO devices not in Thận Nhân Tạo / Lọc Máu
print("\n--- 4. KIỂM TRA THIẾT BỊ THẬN NHÂN TẠO & LỌC MÁU ---")
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name, f.name as fac_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    WHERE (d.device_name LIKE '%thận nhân tạo%' 
        OR d.device_name LIKE '%lọc máu%' 
        OR d.device_name LIKE '%quả lọc%'
        OR d.device_name LIKE '%máy ro%'
        OR d.device_name LIKE '%aquabplus%'
        OR d.model LIKE '%4008%'
        OR d.model LIKE '%5008%')
      AND f.name NOT LIKE '%Thận Nhân Tạo%'
      AND f.name NOT LIKE '%Kho Lưu Trữ%'
""")
misplaced_dialysis = cur.fetchall()
if misplaced_dialysis:
    print(f"⚠️ Phát hiện {len(misplaced_dialysis)} thiết bị Thận nhân tạo đặt sai khoa phòng:")
    for r in misplaced_dialysis:
        print(f"  • ID {r['id']}: {r['device_name']} ({r['model']}) -> Hiện ở: {r['fac_name']}")
else:
    print("✅ 100% thiết bị Thận nhân tạo đặt đúng Đơn vị Thận Nhân Tạo / Lọc Máu!")

# 6. Check for Endoscopy devices not in NSTH
print("\n--- 5. KIỂM TRA HỆ THỐNG NỘI SOI TIÊU HÓA (NSTH) ---")
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name, f.name as fac_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    WHERE (d.device_name LIKE '%nội soi tiêu hóa%' 
        OR d.device_name LIKE '%dây soi dạ dày%' 
        OR d.device_name LIKE '%dây soi đại tràng%'
        OR d.device_name LIKE '%evis x1%'
        OR d.device_name LIKE '%eluxeo%'
        OR d.model LIKE '%gif-%'
        OR d.model LIKE '%cf-%')
      AND f.name NOT LIKE '%Nội Soi%'
      AND f.name NOT LIKE '%Kho Lưu Trữ%'
""")
misplaced_endo = cur.fetchall()
if misplaced_endo:
    print(f"⚠️ Phát hiện {len(misplaced_endo)} thiết bị Nội Soi Tiêu Hóa đặt ngoài Khoa NSTH:")
    for r in misplaced_endo:
        print(f"  • ID {r['id']}: {r['device_name']} ({r['model']}) -> Hiện ở: {r['fac_name']}")
else:
    print("✅ 100% thiết bị Nội Soi Tiêu Hóa đặt đúng Khoa Nội Soi Tiêu Hóa!")

# 7. Check for Dental Chairs and Eye Equipment
print("\n--- 6. KIỂM TRA THIẾT BỊ NHA KHOA & NHÃN KHOA ---")
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, f.name as fac_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    WHERE (d.device_name LIKE '%nha khoa%' OR d.device_name LIKE '%răng%' OR d.device_name LIKE '%ghế máy nha%')
      AND f.name NOT LIKE '%Răng%'
      AND f.name NOT LIKE '%Khám Bệnh%'
      AND f.name NOT LIKE '%Kho Lưu Trữ%'
""")
misplaced_dental = cur.fetchall()
if misplaced_dental:
    print(f"⚠️ Thiết bị Nha khoa đặt ngoài RHM/Khám Bệnh: {len(misplaced_dental)}")
    for r in misplaced_dental:
        print(f"  • ID {r['id']}: {r['device_name']} -> Hiện ở: {r['fac_name']}")
else:
    print("✅ 100% thiết bị Nha Khoa nằm trong Khoa Khám Bệnh / Răng Hàm Mặt!")

# 8. Check for devices with contract vs supplier mismatch
print("\n--- 7. KIỂM TRA TÍNH NHẤT QUÁN HỢP ĐỒNG & NHÀ CUNG CẤP ---")
cur.execute("""
    SELECT d.id, d.device_name, d.contract_no, d.supplier_name, c.supplier_name as contract_supplier
    FROM devices d
    JOIN contracts c ON d.contract_no = c.contract_no
    WHERE d.supplier_name IS NOT NULL 
      AND c.supplier_name IS NOT NULL 
      AND d.supplier_name != c.supplier_name
    LIMIT 10
""")
mismatched_contracts = cur.fetchall()
if mismatched_contracts:
    print(f"⚠️ Phát hiện {len(mismatched_contracts)} thiết bị có nhà cung cấp không khớp với nhà thầu trên hợp đồng:")
    for r in mismatched_contracts:
        print(f"  • ID {r['id']} ({r['device_name']}): Thiết bị ghi '{r['supplier_name']}' nhưng HĐ {r['contract_no']} ghi '{r['contract_supplier']}'")
else:
    print("✅ 100% Nhà cung cấp trên thiết bị khớp hoàn toàn với Nhà thầu trên Hợp đồng!")

conn.close()
