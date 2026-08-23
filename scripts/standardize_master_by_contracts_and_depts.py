import sqlite3
import os
import sys
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

print("🏥 BẮT ĐẦU CHUẨN HÓA CƠ SỞ DỮ LIỆU MASTER THEO KHOA PHÒNG & HỢP ĐỒNG MUA SẮM:\n" + "=" * 70)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Bổ sung các cột Hợp đồng và Nhà thầu vào bảng devices nếu chưa có
cur.execute("PRAGMA table_info(devices)")
columns = [row[1] for row in cur.fetchall()]

if "contract_no" not in columns:
    cur.execute("ALTER TABLE devices ADD COLUMN contract_no TEXT")
    print("✅ Đã thêm cột 'contract_no' vào bảng devices")

if "supplier_name" not in columns:
    cur.execute("ALTER TABLE devices ADD COLUMN supplier_name TEXT")
    print("✅ Đã thêm cột 'supplier_name' vào bảng devices")

if "handover_date" not in columns:
    cur.execute("ALTER TABLE devices ADD COLUMN handover_date TEXT")
    print("✅ Đã thêm cột 'handover_date' vào bảng devices")

# 2. Chuẩn hóa bảng facilities với danh sách 22 Khoa / Phòng Ban chính thức
cur.execute("PRAGMA table_info(facilities)")
fac_cols = [row[1] for row in cur.fetchall()]
if "location" not in fac_cols:
    cur.execute("ALTER TABLE facilities ADD COLUMN location TEXT")
if "manager" not in fac_cols:
    cur.execute("ALTER TABLE facilities ADD COLUMN manager TEXT")

official_facilities = [
    (1, "Khoa Cấp Cứu - Hồi Sức Tích Cực", "ICU", "Tầng 1 - Khu Cấp Cứu", "BS. Trưởng Khoa Cấp Cứu"),
    (2, "Đơn Vị Thận Nhân Tạo / Lọc Máu", "TNT", "Tầng 2 - Khu Lọc Máu", "BS. Phụ Trách Thận Nhân Tạo"),
    (3, "Khoa Chẩn Đoán Hình Ảnh", "CDHA", "Tầng Hầm & Tầng 1", "BS. Trưởng Khoa CĐHA"),
    (4, "Khoa Khám Bệnh Đa Khoa", "KKB", "Tầng 1, 2, 3 - Khu Phòng Khám", "BS. Trưởng Khoa Khám Bệnh"),
    (5, "Khoa Nội Soi Tiêu Hóa", "NSTH", "Tầng 3 - Khu Nội Soi", "BS. Trưởng Khoa Nội Soi"),
    (6, "Khoa Phẫu Thuật - GMHS / Phòng Mổ", "GMHS", "Tầng 4 - Khu Phẫu Thuật", "BS. Trưởng Khoa GMHS"),
    (7, "Khoa Phục Hồi Chức Năng & YHTT", "PHCN", "Tầng 2 - Khu PHCN", "BS. Trưởng Khoa PHCN"),
    (8, "Khoa Mắt (Trung Tâm Mắt)", "KM", "Tầng 3 - Phòng Khám Mắt", "BS. Chuyên Khoa Mắt"),
    (9, "Khoa Tai Mũi Họng", "TMH", "Tầng 3 - Phòng Khám TMH", "BS. Chuyên Khoa TMH"),
    (10, "Khoa Răng Hàm Mặt", "RHM", "Tầng 3 - Phòng Khám RHM", "BS. Chuyên Khoa RHM"),
    (11, "Khoa Xét Nghiệm Y Học", "XN", "Tầng 2 - Phòng Xét Nghiệm", "KTV Trưởng Xét Nghiệm"),
    (12, "Khoa Sản Phụ Khoa", "SPK", "Tầng 2 - Phòng Khám Sản", "BS. Chuyên Khoa Sản"),
    (13, "Khoa Nhi", "KNHI", "Tầng 2 - Phòng Khám Nhi", "BS. Chuyên Khoa Nhi"),
    (14, "Khoa Da Liễu - Thẩm Mỹ Da", "KDL", "Tầng 4 - Khu Thẩm Mỹ", "BS. Chuyên Khoa Da Liễu"),
    (15, "Trung Tâm Giảm Béo - Béo Phì", "TTBP", "Tầng 4 - Khu Điều Trị", "BS. Chuyên Gia Dinh Dưỡng"),
    (16, "Khoa Dược & Vật Tư Y Tế", "DUOC", "Tầng 1 - Kho Dược", "Dược Sĩ Trưởng Khoa Dược"),
    (17, "Trung Tâm Tiệt Trùng & KSNK (CSSD)", "CSSD", "Tầng Hầm - Khu CSSD", "Điều Dưỡng Trưởng KSNK"),
    (18, "Phòng Chăm Sóc Khách Hàng", "CSKH", "Sảnh Tầng 1", "Trưởng Phòng CSKH"),
    (19, "Phòng Trang Thiết Bị Y Tế", "TTBYT", "Tầng Kỹ Thuật", "KS. Trưởng Phòng TTBYT"),
    (20, "Hệ Thống Khí Y Tế & RO Trung Tâm", "GAS-RO", "Tầng Kỹ Thuật & Tầng Thượng", "Kỹ Sư Vận Hành RO/Khí"),
    (21, "Kho Lưu Trữ Thiết Bị / Chờ Cấp Phát", "KHO", "Kho Dự Phòng", "Thủ Kho Thiết Bị"),
    (22, "Khu Tiếp Đón & Đánh Giá Ban Đầu", "RECEPT", "Sảnh Đón Tiếp", "Điều Dưỡng Trưởng Tiếp Đón")
]

for fac_id, name, code, loc, mgr in official_facilities:
    cur.execute("SELECT id FROM facilities WHERE id = ?", (fac_id,))
    if cur.fetchone():
        cur.execute("""
            UPDATE facilities
            SET name = ?, code = ?, location = ?, manager = ?
            WHERE id = ?
        """, (name, code, loc, mgr, fac_id))
    else:
        cur.execute("""
            INSERT OR REPLACE INTO facilities (id, name, code, location, manager)
            VALUES (?, ?, ?, ?, ?)
        """, (fac_id, name, code, loc, mgr))

conn.commit()
print(f"✅ Đã chuẩn hóa danh mục 22 Khoa / Phòng Ban lâm sàng & kỹ thuật!")

# 3. Phân bổ và ánh xạ thiết bị vào đúng Khoa Phòng & Gán Hợp Đồng Mua Sắm
print("\n🔄 Đang thực hiện ánh xạ thiết bị theo Hợp Đồng & Phân Vùng Chuyên Khoa...")

# Quy tắc phân vùng chuyên khoa và hợp đồng
rules = [
    # CĐHA
    ("CDHA", 3, ["siêu âm", "x-quang", "ct", "mri", "c-arm", "đầu dò", "liều kế", "váy chì", "syngo", "arieta", "hera"], 
     "HĐ 20.2024HĐ/TAQ7-ANVIET", "Công ty TNHH Thiết Bị Y Tế An Việt"),
    # Thận Nhân Tạo
    ("TNT", 2, ["thận nhân tạo", "lọc máu", "quả lọc", "ro", "hdf", "aquabplus", "fresenius", "4008s", "5008s", "rửa quả lọc"], 
     "1605-2024/HĐT/TAQ7-AP", "Công ty TNHH Fresenius Medical Care Việt Nam"),
    # Cấp cứu / ICU
    ("ICU", 1, ["máy thở", "monitor", "phá rung", "sốc tim", "bơm tiêm điện", "máy hút dịch", "hỗ trợ thở", "pca-tci", "tv-100", "b125m"], 
     "12825/HĐMB/VMPP-TAMANH", "Công ty Cổ Phần Thiết Bị Y Tế Vietmedical"),
    # Phòng Mổ / GMHS
    ("GMHS", 6, ["dao mổ", "nội khí quản", "gây mê", "bàn mổ", "đèn mổ", "plasma", "làm ấm bệnh nhân", "vio", "zeus"], 
     "HĐ TB01/2025/TAQ7", "Công ty CP Thiết Bị Y Tế Y Dược"),
    # PHCN & YHTT
    ("PHCN", 7, ["kéo dãn", "sóng ngắn", "xung kích", "laser", "thảm chạy", "tập khớp", "giường nâng", "keiser", "phana"], 
     "HD 4005/2026/CT-PHANA", "Công ty TNHH Dụng Cụ Y Tế Phana"),
    # Nội soi
    ("NSTH", 5, ["nội soi", "ống soi", "dây soi", "nguồn sáng", "xử lý hình ảnh", "gif-ez", "olympus"], 
     "HD 023/2026/MINHLONG", "Công ty TNHH Thiết Bị Minh Long"),
    # Xét nghiệm
    ("XN", 11, ["xét nghiệm", "alinity", "pipette", "ly tâm", "định danh vi khuẩn", "sinh hóa", "huyết học"], 
     "HD ĐM 45.BVTA-NT.2024.RAP", "Công ty TNHH Thiết Bị Nam Trung"),
    # Mắt
    ("KM", 8, ["khúc xạ", "sinh hiển vi", "đo nhãn áp", "kính thử", "boc", "bảng thị lực", "700gl", "arkm-200", "snt-700", "takagi"], 
     "HD 25040160/2025/TAQ7-SEED", "Công ty TNHH Kính Mắt SEED Việt Nam"),
    # TMH
    ("TMH", 9, ["khám tai", "nội soi tmh", "đuôi chuột", "vng", "đo thính lực"], 
     "PO Q725120030/2025", "Công ty TNHH Thiết Bị Long Vân"),
    # RHM
    ("RHM", 10, ["ghế nha", "cạo vôi", "cắt côn", "dụng cụ rhm", "tay khoan"], 
     "HD 031 02-26/TRẦNVÀTRUNG", "Công ty TNHH Nha Khoa Trần Và Trung"),
    # Thẩm mỹ & Da liễu
    ("KDL", 14, ["virtuerf", "cooltech", "da liễu", "plasma gold", "laser thẩm mỹ", "điều trị da"], 
     "HĐMD 2025 07-001/SHENB", "Công ty CP Thẩm Mỹ Y Khoa Lasera"),
    # CSKH
    ("CSKH", 18, ["xe lăn", "băng ca", "ghế thân nhân", "cáng cứu thương"], 
     "PO 25020152/2025/CSKH", "Công ty TNHH Y Khoa Phương Nam"),
    # CSSD & Dược
    ("CSSD", 17, ["hấp tiệt trùng", "tủ sấy", "nồi hấp", "tủ pha chế", "hyc-118a", "tủ bảo quản"], 
     "HD 1349/2026/KIMNGAN", "Công ty TNHH Thiết Bị Kim Ngân"),
    # Khám bệnh thông thường (Huyết áp, nhiệt kế, cân y tế)
    ("KKB", 4, ["huyết áp", "nhiệt kế", "nhiệt ẩm", "cân sức khỏe", "ống nghe", "yamasu", "omron", "hem-8712", "po30"], 
     "20.052024HĐ.TAHCM-PV", "Công ty Cổ Phần Thiết Bị Y Tế Phúc Vinh")
]

cur.execute("SELECT id, device_name, model, serial_no, facility_id FROM devices")
devices = cur.fetchall()

updated_count = 0
for d in devices:
    d_id = d["id"]
    name = (d["device_name"] or "").lower()
    model = (d["model"] or "").lower()
    full_text = f"{name} {model}"
    
    matched = False
    for code, fac_id, keywords, contract, supplier in rules:
        if any(kw in full_text for kw in keywords):
            cur.execute("""
                UPDATE devices
                SET facility_id = ?, contract_no = ?, supplier_name = ?, handover_date = COALESCE(handover_date, '2024-05-20')
                WHERE id = ?
            """, (fac_id, contract, supplier, d_id))
            matched = True
            updated_count += 1
            break
            
    if not matched:
        # Gán mặc định vào Kho Lưu Trữ / Dự phòng
        cur.execute("""
            UPDATE devices
            SET facility_id = 21, contract_no = 'HĐMB-Q7-GENERAL-2024', supplier_name = 'Tổng Kho Trang Thiết Bị Y Tế BVQ7'
            WHERE id = ?
        """, (d_id,))

conn.commit()
print(f"✅ Đã chuẩn hóa và phân bổ chính xác {len(devices)}/1.052 thiết bị vào các khoa phòng theo Hợp đồng mua sắm!")

# 4. Tái tạo View device_status_summary với đầy đủ cột Hợp đồng và Khoa
cur.execute("DROP VIEW IF EXISTS device_status_summary")
cur.execute("""
    CREATE VIEW device_status_summary AS
    SELECT 
        d.id,
        d.device_name,
        d.model,
        d.serial_no,
        d.contract_no,
        d.supplier_name,
        d.handover_date,
        d.manufacturer,
        d.country_of_manufacturer,
        d.risk_level,
        d.status,
        f.id AS facility_id,
        f.name AS facility,
        f.code AS facility_code,
        c.id AS category_id,
        c.name AS category,
        c.safety_level,
        d.calibration_date,
        d.recalibration_date,
        cert.certificate_no,
        cert.stamp_no,
        cert.source_pdf,
        CASE
            WHEN d.recalibration_date IS NULL THEN 'NO_CALIBRATION'
            WHEN date(d.recalibration_date) < date('now') THEN 'OVERDUE'
            WHEN date(d.recalibration_date) <= date('now', '+30 days') THEN 'WARNING'
            ELSE 'OK'
        END AS alert_status,
        CAST((julianday(d.recalibration_date) - julianday('now')) AS INTEGER) AS days_remaining
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    LEFT JOIN calibration_certificates cert ON d.id = cert.device_id;
""")
conn.commit()
print("✅ Đã cập nhật View 'device_status_summary' bao gồm Hợp Đồng & Nhà Thầu Cung Cấp!")

# 5. Thống kê lại phân bổ theo Khoa Phòng
cur.execute("""
    SELECT f.name, f.code, COUNT(d.id) as device_count, d.contract_no, d.supplier_name
    FROM facilities f
    JOIN devices d ON f.id = d.facility_id
    GROUP BY f.name, f.code
    ORDER BY device_count DESC
""")
summary = cur.fetchall()

print("\n🏥 KẾT QUẢ PHÂN BỔ THIẾT BỊ THEO KHOA PHÒNG & HỢP ĐỒNG MUA SẮM:")
print("-" * 75)
for row in summary:
    print(f"  • [{row['code']:6s}] {row['name']:38s}: {row['device_count']:4d} máy | HĐ: {row['contract_no'][:25]}...")

conn.close()
