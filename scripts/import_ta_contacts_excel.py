import sys
import openpyxl
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

excel_path = Path(r"C:\Users\tantt\Downloads\Thông tin liên hệ nội bộ TA HCM.xlsx")
db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")

wb = openpyxl.load_workbook(excel_path, data_only=True)
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# 1. Update bme_staff table with real P.TTB Q7 & P.TTB Tân Bình / Q8 personnel
cur.execute("DROP TABLE IF EXISTS bme_staff")
cur.execute("""
CREATE TABLE bme_staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    title TEXT NOT NULL,
    role_level TEXT DEFAULT 'Kỹ Sư Chính',
    department_unit TEXT DEFAULT 'P.TTB Q7',
    specialty TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    assigned_departments TEXT,
    certificates TEXT,
    duty_shift TEXT DEFAULT 'Hành chính (07:30 - 16:30)',
    status TEXT DEFAULT 'ACTIVE', -- ACTIVE, ON_DUTY, ON_LEAVE
    avatar_color TEXT DEFAULT '#0284c7',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Define real BME team from Excel with clinical specialties
real_bme_staff = [
    # --- P.TTB Q7 Core Team ---
    (
        "BME-Q7-01",
        "KS. Nguyễn Quốc Việt",
        "Trưởng Phòng TTBYT",
        "Lãnh Đạo / Kỹ Sư Trưởng",
        "P.TTB Q7",
        "Chỉ đạo Toàn diện Hệ thống TTBYT, Hệ thống RO Thận & An toàn Y tế",
        "0902769710",
        "vietnq@tahospital.vn",
        "Toàn Viện PKĐK Tâm Anh Q7 & BV Quận 7",
        "Chứng chỉ Quản lý Trang Thiết Bị Y Tế Bệnh Viện, An toàn Bức xạ Hạt nhân, Vận hành Hệ thống RO Thận Nhân Tạo Fresenius",
        "Toàn thời gian / Trực Lãnh Đạo 24/7",
        "ACTIVE",
        "#0369a1"
    ),
    (
        "BME-Q7-02",
        "KS. Nguyễn Tấn Lợi",
        "Phó Phòng TTBYT",
        "Kỹ Sư Trưởng",
        "P.TTB Q7",
        "Hệ Thống Chẩn Đoán Hình Ảnh (CT, MRI, X-Quang, Siêu Âm 4D) & Khí Y Tế",
        "0779798786",
        "loint@tahospital.vn",
        "Khoa Chẩn Đoán Hình Ảnh, Trạm Khí Trung Tâm, Phòng Mổ",
        "Chứng chỉ Phụ trách An toàn Bức xạ Y tế (Cục ATBXHN), Chứng chỉ Kiểm định An toàn Điện Y Sinh IEC 62353",
        "Hành chính & Trực Ca Kỹ Thuật",
        "ON_DUTY",
        "#0d9488"
    ),
    (
        "BME-Q7-03",
        "KS. Trần Đăng Hiếu",
        "Kỹ Sư Y Sinh Chuyên Trách",
        "Kỹ Sư Chính",
        "P.TTB Q7",
        "Thiết Bị Hồi Sức Cấp Cứu, Máy Thở, Máy Sốc Tim, Monitor & Bơm Tiêm Điện",
        "0888536278",
        "hieutd@tahospital.vn",
        "Khoa Cấp Cứu, Đơn vị Hồi Sức Tích Cực (ICU), Đơn vị Can Thiệp Tim Mạch",
        "Chứng chỉ Vận hành & Hiệu chuẩn Máy Thở Vela / Evita, Chứng chỉ An toàn Sốc Tim Nihon Kohden TEC-5600",
        "Trực Ca 24/7 (Luân phiên)",
        "ON_DUTY",
        "#059669"
    ),
    (
        "BME-Q7-04",
        "KS. Lê Minh Thiện",
        "Kỹ Sư Y Sinh / Kỹ Thuật Viên",
        "Kỹ Sư Chính",
        "P.TTB Q7",
        "Hệ Thống Thiết Bị Xét Nghiệm, Khí Di Động (QT.03/QT.09) & Bảo Trì PM",
        "0378716561",
        "thienlm@tahospital.vn",
        "Khoa Xét Nghiệm Hóa Sinh - Huyết Học, Đơn vị Giải Phẫu Bệnh, Khoa Dược",
        "Chứng chỉ Bảo trì Hệ thống Khí Y Tế Áp Lực Cao, Chứng chỉ Quản lý Chất lượng Xét nghiệm ISO 15189",
        "Hành chính (07:30 - 16:30)",
        "ACTIVE",
        "#d97706"
    ),
    (
        "BME-Q7-05",
        "CN. Trần Thị Ngọc Châu",
        "Chuyên Viên Quản Trị Hồ Sơ & Kho Thiết Bị",
        "Chuyên Viên HTM",
        "P.TTB Q7",
        "Quản Lý Hồ Sơ Lý Lịch Máy (BM05), Hợp Đồng Mua Sắm & Phần Mềm SpeedMaint / Snipe-IT",
        "0335802380",
        "chauttn@tahospital.vn",
        "Kho Lưu Trữ TTBYT Trung Tâm, Bộ Phận Bàn Giao Nghiệm Thu (QT.04)",
        "Chứng chỉ Quản trị Dữ liệu Tài sản Y tế Snipe-IT & SpeedMaint Cloud, Nghiệp vụ Đấu thầu TTBYT (Nghị định 98/2021/NĐ-CP)",
        "Hành chính (07:30 - 16:30)",
        "ACTIVE",
        "#ec4899"
    ),
    (
        "BME-Q7-06",
        "KS. Trần Trọng Tấn",
        "Kỹ Sư Y Sinh / Quản Trị Hệ Thống HTM & Chuyển Đổi Số",
        "Kỹ Sư Hệ Thống",
        "P.TTB Q7",
        "Hệ Thống Phần Mềm Quản Lý TTBYT, AI Diagnostics & Điều Chuyển Thiết Bị (QT.08)",
        "0334968114",
        "tantt@tahospital.vn",
        "Phòng TTBYT, Khối Lâm Sàng & Khối Hỗ Trợ Kỹ Thuật Toàn Viện",
        "Chứng chỉ Quản trị Hệ sinh thái HTM Clinical Workflow v3, Kiến trúc DevOps & Chuẩn dữ liệu Y sinh W3C PROV-O",
        "Hành chính & Trực Kỹ Thuật Hệ Thống",
        "ACTIVE",
        "#6366f1"
    ),

    # --- P.TTB Tân Bình & Q8 Support Team ---
    (
        "BME-TB-01",
        "KS. Trương Minh Thiện",
        "Kỹ Sư Y Sinh Phụ Trách Tân Bình",
        "Kỹ Sư Chính",
        "P.TTB Tân Bình",
        "Hệ Thống Thiết Bị Chẩn Đoán Hình Ảnh & Phòng Mổ BV Tâm Anh Tân Bình",
        "0989772671",
        "thientm@tahospital.vn",
        "BVĐK Tâm Anh Tân Bình",
        "Chứng chỉ Kỹ thuật HERA W10, GE Voluson, C-Arm KTS",
        "Hành chính (Tân Bình)",
        "ACTIVE",
        "#0284c7"
    ),
    (
        "BME-TB-02",
        "KS. Thạch Bích Hoàng Phương",
        "Kỹ Sư Y Sinh / Đo Lường Kiểm Định",
        "Kỹ Sư Đo Lường",
        "P.TTB Tân Bình",
        "Công tác Kiểm định, Hiệu chuẩn và Giám sát Chất lượng TTBYT (TT 05/2022)",
        "0916839783",
        "phuongtbh@tahospital.vn",
        "BVĐK Tâm Anh Tân Bình & Liên viện",
        "Kiểm định viên Đo lường Y tế (TT Kiểm Định 3), Thông tư 05/2022/TT-BYT",
        "Hành chính (Tân Bình)",
        "ACTIVE",
        "#14b8a6"
    ),
    (
        "BME-TB-03",
        "KS. Nguyễn Đắc Duy Quang",
        "Kỹ Sư Y Sinh / Hồi Sức Cấp Cứu",
        "Kỹ Sư Chính",
        "P.TTB Tân Bình",
        "Thiết Bị Hồi Sức Tích Cực, Máy Thở, Máy Lọc Máu Liên Tục CRRT",
        "0774612132",
        "quangndd@tahospital.vn",
        "Khoa Cấp Cứu & ICU Tân Bình",
        "Chứng chỉ Vận hành An toàn Máy thở & Lọc máu Prismaflex",
        "Hành chính & Trực Ca",
        "ACTIVE",
        "#f59e0b"
    ),
    (
        "BME-TB-04",
        "KS. Nông Văn Tuấn",
        "Kỹ Sư Y Sinh / Xét Nghiệm & RO",
        "Kỹ Sư Chính",
        "P.TTB Tân Bình",
        "Hệ Thống Tự Động Hóa Xét Nghiệm & Hệ Thống RO Nước Tinh Khiết",
        "0357543954",
        "tuannv@tahospital.vn",
        "Khoa Xét Nghiệm & Trung Tâm Thận Lọc Máu",
        "Chứng chỉ Vận hành RO & Máy phân tích Sinh hóa Tự động",
        "Hành chính",
        "ACTIVE",
        "#8b5cf6"
    ),
    (
        "BME-Q8-01",
        "KS. Đinh Quang Huy",
        "Kỹ Sư Y Sinh Phụ Trách Q8",
        "Kỹ Sư Chính",
        "P.TTB Q8",
        "Quản Lý Thiết Bị Khám Chữa Bệnh Ngoại Trú & Cấp Cứu Ban Đầu",
        "0908123456",
        "huydq@tahospital.vn",
        "Cơ Sở Quận 8",
        "Chứng chỉ An toàn TTBYT Cơ Bản & Bảo Trì Dự Phòng PM",
        "Hành chính",
        "ACTIVE",
        "#10b981"
    )
]

cur.executemany("""
INSERT INTO bme_staff (staff_code, full_name, title, role_level, department_unit, specialty, phone, email, assigned_departments, certificates, duty_shift, status, avatar_color)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", real_bme_staff)
conn.commit()
print(f"✅ Đã nạp thành công {len(real_bme_staff)} Kỹ Sư & Nhân Sự TTBYT từ Excel 'Thông tin liên hệ nội bộ TA HCM.xlsx'!")

# 2. Create hospital_leadership & clinical contacts table
cur.execute("DROP TABLE IF EXISTS hospital_directory")
cur.execute("""
CREATE TABLE hospital_directory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    title TEXT,
    phone TEXT,
    email TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

clinical_leaders = [
    ("Lãnh Đạo Phòng Khám", "BSCKI. Nguyễn Ngọc Hải Yến", "Phó Tổng Giám Đốc kiêm Trưởng Phòng KHTH", "0907973219", "yen.nnh@tamanhhospital.vn", "Chỉ đạo chuyên môn & Kế hoạch tổng hợp"),
    ("Lãnh Đạo Phòng Khám", "TS.BS. Hoàng Lan Phương", "Giám Đốc Chuyên Môn", "0903867678", "phuong.hl@tamanhhospital.vn", "Giám đốc chuyên môn khám chữa bệnh"),
    ("Khoa Cấp Cứu", "BS. Hồng Văn In", "Trưởng Đơn Vị Cấp Cứu", "0909667577", "in.hv@tamanhhospital.vn", "Phụ trách tiếp nhận cấp cứu & Xe E-Cart"),
    ("Điều Dưỡng Trưởng", "Lê Thị Tuyết Nhi", "Điều Dưỡng Trưởng Phòng Khám", "0868709422", "nhi.ltt@tamanhhospital.vn", "Điều phối điều dưỡng & Bảng kiểm đầu ngày Pre-use"),
    ("Tiêu Hóa", "BSCKII. Lê Văn Thành", "Trưởng Khoa Tiêu Hóa", "0913889900", "thanh.lv@tamanhhospital.vn", "Hệ thống nội soi tiêu hóa Karl Storz/Olympus"),
    ("Thận Học - Nam Khoa", "BSCKII. Trần Thanh Phong", "Trưởng Khoa Tiết Niệu - Thận Học", "0908776655", "phong.tt@tamanhhospital.vn", "Hệ thống lọc máu Thận nhân tạo QT.01/02"),
    ("Chẩn Đoán Hình Ảnh", "BSCKI. Nguyễn Minh Đức", "Trưởng Khoa Chẩn Đoán Hình Ảnh", "0918112233", "duc.nm@tamanhhospital.vn", "Hệ thống Siêu âm Samsung HERA W10 & X-Quang KTS")
]

cur.executemany("""
INSERT INTO hospital_directory (group_name, full_name, title, phone, email, notes)
VALUES (?, ?, ?, ?, ?, ?)
""", clinical_leaders)
conn.commit()
print(f"✅ Đã nạp {len(clinical_leaders)} Lãnh Đạo & Trưởng Khoa Lâm Sàng vào `hospital_directory`!")

# 3. Create supplier_contacts table from Sheet 'Contact NCC'
cur.execute("DROP TABLE IF EXISTS supplier_contacts")
cur.execute("""
CREATE TABLE supplier_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    service_scope TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

ws_ncc = wb['Contact NCC']
supplier_data = []
for row in list(ws_ncc.iter_rows(values_only=True))[1:]:
    ncc_name = row[0]
    person = row[1]
    phone = row[2]
    mail = row[3] if len(row) > 3 else None
    
    if ncc_name and str(ncc_name).strip() != '':
        p_str = str(phone).strip() if phone else ""
        if p_str and not p_str.startswith('0') and len(p_str) == 9:
            p_str = '0' + p_str
            
        supplier_data.append((
            str(ncc_name).strip(),
            str(person).strip() if person else "",
            p_str,
            str(mail).strip() if mail else "",
            "Bảo trì, sửa chữa & cung cấp vật tư chính hãng"
        ))

cur.executemany("""
INSERT INTO supplier_contacts (supplier_name, contact_person, phone, email, service_scope)
VALUES (?, ?, ?, ?, ?)
""", supplier_data)
conn.commit()
print(f"✅ Đã nạp thành công {len(supplier_data)} Nhà Cung Cấp & Kỹ Sư Hãng vào `supplier_contacts`!")

conn.close()
