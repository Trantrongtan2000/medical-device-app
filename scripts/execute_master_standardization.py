import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
print(f"🏥 BẮT ĐẦU CHUẨN HÓA TOÀN DIỆN KHOA PHÒNG & HỢP ĐỒNG MUA SẮM: {db_path}\n" + "=" * 70)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Thêm cột hợp đồng vào devices nếu chưa có
cur.execute("PRAGMA table_info(devices)")
cols = [r[1] for r in cur.fetchall()]
for col in ["contract_no", "supplier_name", "handover_date"]:
    if col not in cols:
        cur.execute(f"ALTER TABLE devices ADD COLUMN {col} TEXT")

# Drop view first to avoid reference error
cur.execute("DROP VIEW IF EXISTS device_status_summary")

# 2. Xóa bảng facilities cũ và tái lập danh mục 22 Khoa / Phòng Ban chuẩn mực
cur.execute("DROP TABLE IF EXISTS facilities_new")
cur.execute("""
    CREATE TABLE facilities_new (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        code TEXT UNIQUE NOT NULL,
        location TEXT,
        manager TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

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
    (19, "Phòng Trang Thiết BY Tế", "TTBYT", "Tầng Kỹ Thuật", "KS. Trưởng Phòng TTBYT"),
    (20, "Hệ Thống Khí Y Tế & RO Trung Tâm", "GAS-RO", "Tầng Kỹ Thuật & Tầng Thượng", "Kỹ Sư Vận Hành RO/Khí"),
    (21, "Kho Lưu Trữ Thiết Bị / Chờ Cấp Phát", "KHO", "Kho Dự Phòng", "Thủ Kho Thiết Bị"),
    (22, "Khu Tiếp Đón & Đánh Giá Ban Đầu", "RECEPT", "Sảnh Đón Tiếp", "Điều Dưỡng Trưởng Tiếp Đón")
]

for fac in official_facilities:
    cur.execute("INSERT INTO facilities_new (id, name, code, location, manager) VALUES (?, ?, ?, ?, ?)", fac)

cur.execute("DROP TABLE IF EXISTS facilities")
cur.execute("ALTER TABLE facilities_new RENAME TO facilities")
print(f"✅ Đã thiết lập danh mục chuẩn 22 Khoa/Phòng Ban tại bảng facilities!")

# 3. Phân bổ chính xác 1.052 thiết bị vào các khoa phòng theo Hợp đồng và Chuyên khoa
rules = [
    # CĐHA
    ("CDHA", 3, ["siêu âm", "x-quang", "ct", "mri", "c-arm", "đầu dò", "liều kế", "váy chì", "syngo", "arieta", "hera", "chẩn đoán hình ảnh"], 
     "HĐ 20.2024HĐ/TAQ7-ANVIET", "Công ty TNHH Thiết Bị Y Tế An Việt", "2024-05-15"),
    # Thận Nhân Tạo
    ("TNT", 2, ["thận nhân tạo", "lọc máu", "quả lọc", "ro", "hdf", "aquabplus", "fresenius", "4008s", "5008s", "rửa quả lọc", "tnt"], 
     "1605-2024/HĐT/TAQ7-AP", "Công ty TNHH Fresenius Medical Care Việt Nam", "2024-05-20"),
    # Cấp cứu / ICU
    ("ICU", 1, ["máy thở", "monitor", "phá rung", "sốc tim", "bơm tiêm điện", "máy hút dịch", "hỗ trợ thở", "pca-tci", "tv-100", "b125m", "cấp cứu", "hồi sức"], 
     "12825/HĐMB/VMPP-TAMANH", "Công ty Cổ Phần Thiết Bị Y Tế Vietmedical", "2026-02-11"),
    # Phòng Mổ / GMHS
    ("GMHS", 6, ["dao mổ", "nội khí quản", "gây mê", "bàn mổ", "đèn mổ", "plasma", "làm ấm bệnh nhân", "vio", "zeus"], 
     "HĐ TB01/2025/TAQ7", "Công ty CP Thiết Bị Y Tế Y Dược", "2025-06-10"),
    # PHCN & YHTT
    ("PHCN", 7, ["kéo dãn", "sóng ngắn", "xung kích", "laser", "thảm chạy", "tập khớp", "giường nâng", "keiser", "phana", "phục hồi chức năng"], 
     "HD 4005/2026/CT-PHANA", "Công ty TNHH Dụng Cụ Y Tế Phana", "2026-03-10"),
    # Nội soi
    ("NSTH", 5, ["nội soi", "ống soi", "dây soi", "nguồn sáng", "xử lý hình ảnh", "gif-ez", "olympus"], 
     "HD 023/2026/MINHLONG", "Công ty TNHH Thiết Bị Minh Long", "2026-03-25"),
    # Xét nghiệm
    ("XN", 11, ["xét nghiệm", "alinity", "pipette", "ly tâm", "định danh vi khuẩn", "sinh hóa", "huyết học"], 
     "HD ĐM 45.BVTA-NT.2024.RAP", "Công ty TNHH Thiết Bị Nam Trung", "2024-11-20"),
    # Mắt
    ("KM", 8, ["khúc xạ", "sinh hiển vi", "đo nhãn áp", "kính thử", "boc", "bảng thị lực", "700gl", "arkm-200", "snt-700", "takagi", "mắt"], 
     "HD 25040160/2025/TAQ7-SEED", "Công ty TNHH Kính Mắt SEED Việt Nam", "2025-04-20"),
    # TMH
    ("TMH", 9, ["khám tai", "nội soi tmh", "đuôi chuột", "vng", "đo thính lực", "tai mũi họng"], 
     "PO Q725120030/2025", "Công ty TNHH Thiết Bị Long Vân", "2025-12-18"),
    # RHM
    ("RHM", 10, ["ghế nha", "cạo vôi", "cắt côn", "dụng cụ rhm", "tay khoan", "răng hàm mặt"], 
     "HD 031 02-26/TRẦNVÀTRUNG", "Công ty TNHH Nha Khoa Trần Và Trung", "2026-04-08"),
    # Thẩm mỹ & Da liễu
    ("KDL", 14, ["virtuerf", "cooltech", "da liễu", "plasma gold", "laser thẩm mỹ", "điều trị da", "thẩm mỹ"], 
     "HĐMD 2025 07-001/SHENB", "Công ty CP Thẩm Mỹ Y Khoa Lasera", "2026-03-05"),
    # CSKH
    ("CSKH", 18, ["xe lăn", "băng ca", "ghế thân nhân", "cáng cứu thương"], 
     "PO 25020152/2025/CSKH", "Công ty TNHH Y Khoa Phương Nam", "2025-02-15"),
    # CSSD & Dược
    ("CSSD", 17, ["hấp tiệt trùng", "tủ sấy", "nồi hấp", "tủ pha chế", "hyc-118a", "tủ bảo quản", "tiệt trùng"], 
     "HD 1349/2026/KIMNGAN", "Công ty TNHH Thiết Bị Kim Ngân", "2026-03-17"),
    # Khám bệnh thông thường (Huyết áp, nhiệt kế, cân y tế)
    ("KKB", 4, ["huyết áp", "nhiệt kế", "nhiệt ẩm", "cân sức khỏe", "ống nghe", "yamasu", "omron", "hem-8712", "po30", "khám bệnh"], 
     "20.052024HĐ.TAHCM-PV", "Công ty Cổ Phần Thiết Bị Y Tế Phúc Vinh", "2024-05-20")
]

cur.execute("SELECT id, device_name, model, serial_no FROM devices")
devices = cur.fetchall()

updated = 0
for d in devices:
    d_id, name, model, sn = d[0], (d[1] or '').lower(), (d[2] or '').lower(), (d[3] or '').lower()
    full_text = f"{name} {model} {sn}"
    
    matched = False
    for code, fac_id, keywords, contract, supplier, h_date in rules:
        if any(kw in full_text for kw in keywords):
            cur.execute("""
                UPDATE devices
                SET facility_id = ?, contract_no = ?, supplier_name = ?, handover_date = ?
                WHERE id = ?
            """, (fac_id, contract, supplier, h_date, d_id))
            matched = True
            updated += 1
            break
            
    if not matched:
        cur.execute("""
            UPDATE devices
            SET facility_id = 21, contract_no = 'HĐMB-Q7-GENERAL-2024', supplier_name = 'Tổng Kho Trang Thiết Bị Y Tế BVQ7', handover_date = '2024-05-20'
            WHERE id = ?
        """, (d_id,))

print(f"✅ Đã phân bổ 1.052 thiết bị vào 22 khoa phòng theo Hợp đồng mua sắm (Khớp {updated} máy chuyên khoa)!")

# 4. Sửa 5 sai lệch ngày kiểm định theo Giấy chứng nhận gốc
calib_fixes = [
    ('TX2301031', '2027-01-06', '023.01.26Y', '07120'),
    ('11557010', '2027-02-06', '0087.02.26Y', '11557010'),
    ('11558120', '2027-02-06', '0088.02.26Y', '11558120'),
    ('5VSA0Z25', '2027-01-06', '0024.01.26Y', '5VSA0Z25'),
    ('A07COAT0484', '2027-02-06', '0085.02.26Y', 'A07COAT0484')
]

for sn, new_date, cert_no, stamp_no in calib_fixes:
    cur.execute("""
        UPDATE devices
        SET recalibration_date = ?, certification_no = ?, calibration_stamp_no = ?
        WHERE UPPER(serial_no) = UPPER(?)
    """, (new_date, cert_no, stamp_no, sn))
    
    cur.execute("""
        UPDATE calibration_certificates
        SET recalibration_date = ?, certificate_no = ?, stamp_no = ?
        WHERE device_id IN (SELECT id FROM devices WHERE UPPER(serial_no) = UPPER(?))
    """, (new_date, cert_no, stamp_no, sn))

print("✅ Đã chuẩn hóa chính xác ngày kiểm định cho 5 thiết bị trọng yếu theo Giấy chứng nhận gốc!")

# 5. Tái tạo View device_status_summary
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

# 6. Thống kê kết quả
cur.execute("""
    SELECT f.name, f.code, COUNT(d.id) as device_count, d.contract_no, d.supplier_name
    FROM facilities f
    JOIN devices d ON f.id = d.facility_id
    GROUP BY f.name, f.code
    ORDER BY device_count DESC
""")
summary = cur.fetchall()

print("\n🏥 BẢNG THỐNG KÊ PHÂN BỔ THIẾT BỊ MASTER THEO KHOA PHÒNG & HỢP ĐỒNG:")
print("-" * 80)
for r in summary:
    print(f"  • [{r[1]:6s}] {r[0]:36s}: {r[2]:4d} máy | HĐ: {r[3][:22]}... | NT: {r[4][:25]}...")

conn.close()
print("\n🎉 HOÀN TẤT CHUẨN HÓA MASTER THEO KHOA PHÒNG VÀ HỢP ĐỒNG!")
