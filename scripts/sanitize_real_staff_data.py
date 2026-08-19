import sys
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Update bme_staff to strictly remove any unverified/fabricated certificates
cur.execute("""
UPDATE bme_staff 
SET certificates = NULL
""")

# Also update specialty and roles to be strictly grounded without speculation
q7_verified_profiles = [
    (
        "BME-Q7-01",
        "Nguyễn Quốc Việt",
        "Trưởng Phòng TTBYT",
        "Quản Lý / Trưởng Phòng",
        "Phòng TTBYT Quận 7",
        "Phụ trách chung Phòng Trang Thiết Bị Y Tế Quận 7",
        "0902769710",
        "vietnq@tahospital.vn",
        "Toàn Viện PKĐK Tâm Anh Q7",
        None,
        "#0369a1"
    ),
    (
        "BME-Q7-02",
        "Nguyễn Tấn Lợi",
        "Phó Phòng TTBYT",
        "Quản Lý / Phó Phòng",
        "Phòng TTBYT Quận 7",
        "Phụ trách Kỹ thuật & Thiết bị y tế Quận 7",
        "0779798786",
        "loint@tahospital.vn",
        "Toàn Viện PKĐK Tâm Anh Q7",
        None,
        "#0d9488"
    ),
    (
        "BME-Q7-03",
        "Trần Đăng Hiếu",
        "Kỹ Sư",
        "Kỹ Sư Y Sinh",
        "Phòng TTBYT Quận 7",
        "Kỹ thuật thiết bị y tế",
        "0888536278",
        "hieutd@tahospital.vn",
        "Khối Lâm Sàng PKĐK Tâm Anh Q7",
        None,
        "#059669"
    ),
    (
        "BME-Q7-04",
        "Lê Minh Thiện",
        "Nhân Viên",
        "Kỹ Thuật Viên / Nhân Viên",
        "Phòng TTBYT Quận 7",
        "Kỹ thuật & Vận hành thiết bị y tế",
        "0378716561",
        "thienlm@tahospital.vn",
        "Khối Lâm Sàng PKĐK Tâm Anh Q7",
        None,
        "#d97706"
    ),
    (
        "BME-Q7-05",
        "Trần Thị Ngọc Châu",
        "Nhân Viên",
        "Chuyên Viên Quản Trị",
        "Phòng TTBYT Quận 7",
        "Quản lý hồ sơ & thiết bị y tế",
        "0335802380",
        "chauttn@tahospital.vn",
        "Kho Lưu Trữ & Phòng TTBYT Q7",
        None,
        "#ec4899"
    ),
    (
        "BME-Q7-06",
        "Trần Trọng Tấn",
        "Nhân Viên",
        "Kỹ Sư / Quản Trị Hệ Thống",
        "Phòng TTBYT Quận 7",
        "Kỹ thuật, phần mềm & quản trị dữ liệu TTBYT",
        "0334968114",
        "tantt@tahospital.vn",
        "Phòng TTBYT & Toàn Viện Q7",
        None,
        "#6366f1"
    )
]

for s in q7_verified_profiles:
    cur.execute("""
    UPDATE bme_staff
    SET full_name = ?, title = ?, role_level = ?, department_unit = ?, specialty = ?, phone = ?, email = ?, assigned_departments = ?, certificates = ?, avatar_color = ?
    WHERE staff_code = ?
    """, (s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[0]))

conn.commit()
print("✅ Đã làm sạch toàn bộ dữ liệu: Gỡ bỏ 100% chứng chỉ không có hồ sơ minh chứng gốc!")

conn.close()
