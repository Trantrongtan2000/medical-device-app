import sys
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# 1. Recreate bme_staff with strictly 6 members of District 7
cur.execute("DROP TABLE IF EXISTS bme_staff")
cur.execute("""
CREATE TABLE bme_staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    title TEXT NOT NULL,
    role_level TEXT DEFAULT 'Kỹ Sư Chính',
    department_unit TEXT DEFAULT 'Phòng TTBYT Quận 7',
    specialty TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    assigned_departments TEXT,
    certificates TEXT,
    oncall_status TEXT DEFAULT 'AVAILABLE', -- ONCALL_TODAY, AVAILABLE, LEAVE
    avatar_color TEXT DEFAULT '#0284c7',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

q7_staff_6 = [
    (
        "BME-Q7-01",
        "Nguyễn Quốc Việt",
        "Trưởng Phòng TTBYT",
        "Lãnh Đạo / Kỹ Sư Trưởng",
        "Phòng TTBYT Quận 7",
        "Chỉ đạo Toàn diện Hệ thống TTBYT, Hệ thống RO Thận & An toàn Y tế",
        "0902769710",
        "vietnq@tahospital.vn",
        "Toàn Viện PKĐK Tâm Anh Q7 & BV Quận 7",
        "Chứng chỉ Quản lý Trang Thiết Bị Y Tế Bệnh Viện, An toàn Bức xạ Hạt nhân, Vận hành Hệ thống RO Thận Nhân Tạo Fresenius",
        "AVAILABLE",
        "#0369a1"
    ),
    (
        "BME-Q7-02",
        "Nguyễn Tấn Lợi",
        "Phó Phòng TTBYT",
        "Kỹ Sư Trưởng",
        "Phòng TTBYT Quận 7",
        "Hệ Thống Chẩn Đoán Hình Ảnh (CT, MRI, X-Quang, Siêu Âm 4D) & Khí Y Tế",
        "0779798786",
        "loint@tahospital.vn",
        "Khoa Chẩn Đoán Hình Ảnh, Trạm Khí Trung Tâm, Phòng Mổ",
        "Chứng chỉ Phụ trách An toàn Bức xạ Y tế (Cục ATBXHN), Chứng chỉ Kiểm định An toàn Điện Y Sinh IEC 62353",
        "AVAILABLE",
        "#0d9488"
    ),
    (
        "BME-Q7-03",
        "Trần Đăng Hiếu",
        "Kỹ Sư Y Sinh Chuyên Trách",
        "Kỹ Sư Chính",
        "Phòng TTBYT Quận 7",
        "Thiết Bị Hồi Sức Cấp Cứu, Máy Thở, Máy Sốc Tim, Monitor & Bơm Tiêm Điện",
        "0888536278",
        "hieutd@tahospital.vn",
        "Khoa Cấp Cứu, Đơn vị Hồi Sức Tích Cực (ICU), Đơn vị Can Thiệp Tim Mạch",
        "Chứng chỉ Vận hành & Hiệu chuẩn Máy Thở Vela / Evita, Chứng chỉ An toàn Sốc Tim Nihon Kohden TEC-5600",
        "ONCALL_TODAY",
        "#059669"
    ),
    (
        "BME-Q7-04",
        "Lê Minh Thiện",
        "Kỹ Sư Y Sinh / Kỹ Thuật Viên",
        "Kỹ Sư Chính",
        "Phòng TTBYT Quận 7",
        "Hệ Thống Thiết Bị Xét Nghiệm, Khí Di Động (QT.03/QT.09) & Bảo Trì PM",
        "0378716561",
        "thienlm@tahospital.vn",
        "Khoa Xét Nghiệm Hóa Sinh - Huyết Học, Đơn vị Giải Phẫu Bệnh, Khoa Dược",
        "Chứng chỉ Bảo trì Hệ thống Khí Y Tế Áp Lực Cao, Chứng chỉ Quản lý Chất lượng Xét nghiệm ISO 15189",
        "AVAILABLE",
        "#d97706"
    ),
    (
        "BME-Q7-05",
        "Trần Thị Ngọc Châu",
        "Chuyên Viên Quản Trị Hồ Sơ & Kho Thiết Bị",
        "Chuyên Viên HTM",
        "Phòng TTBYT Quận 7",
        "Quản Lý Hồ Sơ Lý Lịch Máy (BM05), Hợp Đồng Mua Sắm & CMMS SpeedMaint / Snipe-IT",
        "0335802380",
        "chauttn@tahospital.vn",
        "Kho Lưu Trữ TTBYT Trung Tâm, Bộ Phận Bàn Giao Nghiệm Thu (QT.04)",
        "Chứng chỉ Quản trị Dữ liệu Tài sản Y tế Snipe-IT & SpeedMaint Cloud, Nghiệp vụ Đấu thầu TTBYT (Nghị định 98/2021/NĐ-CP)",
        "AVAILABLE",
        "#ec4899"
    ),
    (
        "BME-Q7-06",
        "Trần Trọng Tấn",
        "Kỹ Sư Y Sinh / Quản Trị Hệ Thống HTM & Chuyển Đổi Số",
        "Kỹ Sư Hệ Thống",
        "Phòng TTBYT Quận 7",
        "Hệ Thống Phần Mềm Quản Lý TTBYT, AI Diagnostics & Điều Chuyển Thiết Bị (QT.08)",
        "0334968114",
        "tantt@tahospital.vn",
        "Phòng TTBYT, Khối Lâm Sàng & Khối Hỗ Trợ Kỹ Thuật Toàn Viện",
        "Chứng chỉ Quản trị Hệ sinh thái HTM Clinical Workflow v3, Kiến trúc DevOps & Chuẩn dữ liệu Y sinh W3C PROV-O",
        "ONCALL_TODAY",
        "#6366f1"
    )
]

cur.executemany("""
INSERT INTO bme_staff (staff_code, full_name, title, role_level, department_unit, specialty, phone, email, assigned_departments, certificates, oncall_status, avatar_color)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", q7_staff_6)
conn.commit()
print(f"✅ Đã chuẩn hóa danh sách đúng 6 nhân sự Quận 7: {[s[1] for s in q7_staff_6]}")

# 2. Create oncall_schedule table
cur.execute("DROP TABLE IF EXISTS oncall_schedule")
cur.execute("""
CREATE TABLE oncall_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_name TEXT NOT NULL,
    date_str TEXT NOT NULL,
    primary_engineer TEXT NOT NULL,
    primary_phone TEXT NOT NULL,
    backup_engineer TEXT NOT NULL,
    backup_phone TEXT NOT NULL,
    leader_oncall TEXT DEFAULT 'Nguyễn Quốc Việt (0902769710)',
    time_window TEXT DEFAULT '16:30 - 07:30 sáng hôm sau (24/24 ngày lễ & CN)',
    status TEXT DEFAULT 'SCHEDULED', -- TODAY, SCHEDULED, COMPLETED
    notes TEXT
)
""")

oncall_data = [
    ("Thứ Hai", "18/08/2026", "Trần Trọng Tấn", "0334968114", "Trần Đăng Hiếu", "0888536278", "Nguyễn Quốc Việt (0902769710)", "16:30 - 07:30", "COMPLETED", "Đã xử lý sự cố monitor Cấp cứu lúc 21:15"),
    ("Thứ Ba", "19/08/2026", "Trần Đăng Hiếu", "0888536278", "Trần Trọng Tấn", "0334968114", "Nguyễn Quốc Việt (0902769710)", "16:30 - 07:30", "TODAY", "On-call chính ca đêm hôm nay"),
    ("Thứ Tư", "20/08/2026", "Lê Minh Thiện", "0378716561", "Nguyễn Tấn Lợi", "0779798786", "Nguyễn Quốc Việt (0902769710)", "16:30 - 07:30", "SCHEDULED", "Trực hỗ trợ Khí y tế & Xét nghiệm"),
    ("Thứ Năm", "21/08/2026", "Nguyễn Tấn Lợi", "0779798786", "Trần Trọng Tấn", "0334968114", "Nguyễn Quốc Việt (0902769710)", "16:30 - 07:30", "SCHEDULED", "Trực hỗ trợ CĐHA & Phòng Mổ"),
    ("Thứ Sáu", "22/08/2026", "Trần Thị Ngọc Châu", "0335802380", "Trần Đăng Hiếu", "0888536278", "Nguyễn Quốc Việt (0902769710)", "16:30 - 07:30", "SCHEDULED", "Trực tiếp nhận hồ sơ & sự cố kho"),
    ("Thứ Bảy", "23/08/2026", "Trần Trọng Tấn", "0334968114", "Lê Minh Thiện", "0378716561", "Nguyễn Quốc Việt (0902769710)", "24/24 Giờ", "SCHEDULED", "Trực nguyên ngày Thứ Bảy"),
    ("Chủ Nhật", "24/08/2026", "Trần Đăng Hiếu", "0888536278", "Nguyễn Tấn Lợi", "0779798786", "Nguyễn Quốc Việt (0902769710)", "24/24 Giờ", "SCHEDULED", "Trực nguyên ngày Chủ Nhật")
]

cur.executemany("""
INSERT INTO oncall_schedule (day_name, date_str, primary_engineer, primary_phone, backup_engineer, backup_phone, leader_oncall, time_window, status, notes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", oncall_data)
conn.commit()
print(f"✅ Đã tạo bảng `oncall_schedule` và nạp lịch On-call 7 ngày trong tuần!")

conn.close()
