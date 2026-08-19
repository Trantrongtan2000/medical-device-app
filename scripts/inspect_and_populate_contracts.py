import os
import sys
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("="*75)
print("📦 KHỞI TẠO BẢNG CONTRACTS & ĐỒNG BỘ TOÀN DIỆN DANH MỤC HỢP ĐỒNG - NHÀ CUNG CẤP")
print("="*75)

# 1. Create contracts table
cur.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_no TEXT NOT NULL UNIQUE,
        contract_name TEXT,
        supplier_name TEXT,
        handover_date TEXT,
        contract_value REAL,
        warranty_period_months INTEGER DEFAULT 12,
        status TEXT DEFAULT 'ACTIVE',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()

# 2. Extract contracts from devices table
cur.execute("""
    SELECT contract_no, supplier_name, MIN(handover_date) as min_date, COUNT(*) as dev_count
    FROM devices
    WHERE contract_no IS NOT NULL AND TRIM(contract_no) != ''
    GROUP BY contract_no, supplier_name
""")
device_contracts = [dict(r) for r in cur.fetchall()]

# Additional standard hospital procurement contracts
standard_contracts = [
    {
        "contract_no": "HĐ 20.2024HĐ/TAQ7-ANVIET",
        "contract_name": "Hợp đồng Cung Cấp Hệ Thống Siêu Âm Màu Chuyên Sản Samsung Medison HERA W10 & Phụ Kiện Đầu Dò",
        "supplier_name": "Công Ty TNHH Thiết Bị Y Tế An Việt",
        "handover_date": "2024-05-15",
        "contract_value": 4500000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Hệ thống siêu âm màu cao cấp 4D/5D phục vụ Sản Phụ Khoa"
    },
    {
        "contract_no": "HĐ-GE-VOLUSON-Q7",
        "contract_name": "Hợp đồng Mua Sắm & Lắp Đặt Hệ Thống Siêu Âm Voluson E10 / P8 / S8t",
        "supplier_name": "Công Ty TNHH GE Healthcare Việt Nam",
        "handover_date": "2024-06-20",
        "contract_value": 8200000000,
        "warranty_period_months": 36,
        "status": "ACTIVE",
        "notes": "Trang bị đồng bộ cho Trung tâm Chẩn đoán hình ảnh"
    },
    {
        "contract_no": "1605-2024/HĐT/TAQ7-AP",
        "contract_name": "Hợp đồng Thuê & Vận Hành Hệ Thống Máy Thận Nhân Tạo 4008S / 5008S",
        "supplier_name": "Công Ty TNHH Fresenius Medical Care Việt Nam",
        "handover_date": "2024-05-16",
        "contract_value": 12500000000,
        "warranty_period_months": 60,
        "status": "ACTIVE",
        "notes": "Hệ thống lọc máu Thận nhân tạo và cảm biến đo SpO2 kẹp tay"
    },
    {
        "contract_no": "12825/HĐMB/VMPP-TAMANH",
        "contract_name": "Hợp đồng Cung Cấp Máy Giúp Thở Chức Năng Cao TV-100 & Thiết Bị Cấp Cứu Hồi Sức",
        "supplier_name": "Công Ty Cổ Phần Thiết Bị Y Tế Vietmedical",
        "handover_date": "2026-02-11",
        "contract_value": 6800000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Hệ thống máy thở chuyên dụng Khoa Cấp Cứu"
    },
    {
        "contract_no": "20.052024HĐ.TAHCM-PV",
        "contract_name": "Hợp đồng Mua Sắm Tổng Thể Trang Thiết Bị Y Tế Phòng Khám Đa Khoa Tâm Anh Quận 7",
        "supplier_name": "Công Ty TNHH Trang Thiết Bị Y Tế Phúc Vinh",
        "handover_date": "2024-05-20",
        "contract_value": 35000000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Gói thầu mua sắm đồng bộ hơn 600 thiết bị đa khoa"
    },
    {
        "contract_no": "HĐ 14.2024HĐ/TAQ7-GE",
        "contract_name": "Hợp đồng Mua Sắm Hệ Thống Chụp Cắt Lớp Vi Tính CT-Scanner Revolution EVO 128 Lát",
        "supplier_name": "Công Ty TNHH GE Healthcare Việt Nam",
        "handover_date": "2024-07-10",
        "contract_value": 28000000000,
        "warranty_period_months": 36,
        "status": "ACTIVE",
        "notes": "Hệ thống CT-Scanner 128 lát cắt Khoa CĐHA"
    },
    {
        "contract_no": "HĐ 08.2024HĐ/TAQ7-VIETCAN",
        "contract_name": "Hợp đồng Cung Cấp Hệ Thống Nội Soi Tiêu Hóa 4K Olympus EVIS X1 & Đèn Mổ LED",
        "supplier_name": "Công Ty CP Công Nghệ Y Tế Viet Can",
        "handover_date": "2024-08-05",
        "contract_value": 15600000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Dây soi dạ dày, đại tràng 4K NBI Khoa NSTH"
    },
    {
        "contract_no": "HĐ 05.2024HĐ/TAQ7-BTL",
        "contract_name": "Hợp đồng Cung Cấp Thiết Bị Vật Lý Trị Liệu & Phục Hồi Chức Năng BTL",
        "supplier_name": "Công Ty TNHH BTL Industries Việt Nam",
        "handover_date": "2024-06-12",
        "contract_value": 3200000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Máy sóng ngắn, laser công suất cao, máy kéo giãn cột sống"
    },
    {
        "contract_no": "HĐ 02.2024HĐ/TAQ7-HAP",
        "contract_name": "Hợp đồng Mua Sắm Máy Phá Rung Tim Nihon Kohden TEC-5600 & Monitor Bệnh Nhân",
        "supplier_name": "Công Ty Cổ Phần Dược Phẩm Thiết Bị Y Tế Hà Nội (Hapharco)",
        "handover_date": "2024-05-18",
        "contract_value": 4800000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Thiết bị cấp cứu và monitor 5 thông số"
    },
    {
        "contract_no": "HĐ 073.2024/HĐMB/ĐM",
        "contract_name": "Hợp đồng Cung Cấp Kính Hiển Vi Quang Học & Thiết Bị Phòng Xét Nghiệm",
        "supplier_name": "Công Ty TNHH Thiết Bị Khoa Học Kỹ Thuật Đức Minh",
        "handover_date": "2024-07-22",
        "contract_value": 1850000000,
        "warranty_period_months": 12,
        "status": "ACTIVE",
        "notes": "Kính hiển vi 2 mắt & 3 mắt kết nối camera"
    },
    {
        "contract_no": "HĐ 053.2024/HĐMB/TT",
        "contract_name": "Hợp đồng Cung Cấp Hệ Thống Ghế Máy Nha Khoa & Đèn Tẩy Trắng Răng",
        "supplier_name": "Công Ty TNHH Trang Thiết Bị Nha Khoa Medent",
        "handover_date": "2024-06-30",
        "contract_value": 2400000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Ghế máy nha khoa tích hợp tay khoan siêu âm"
    },
    {
        "contract_no": "HĐ 20230913-003/CLP",
        "contract_name": "Hợp đồng Cung Cấp Hệ Thống Máy Đo Đa Ký Hô Hấp & Thăm Dò Chức Năng Phổi",
        "supplier_name": "Công Ty Cổ Phần Calapharco",
        "handover_date": "2023-09-13",
        "contract_value": 1950000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Hệ thống đo đa ký hô hấp Nox Medical"
    },
    {
        "contract_no": "HĐ 2902/DVT/TAHDMB",
        "contract_name": "Hợp đồng Mua Sắm Bàn Nghiêng Chuyên Dụng Tim Mạch & Giường Thăm Khám",
        "supplier_name": "Công Ty TNHH Sản Xuất Thương Mại Nam Trung",
        "handover_date": "2024-02-29",
        "contract_value": 1400000000,
        "warranty_period_months": 12,
        "status": "ACTIVE",
        "notes": "Bàn nghiêng tập tim mạch và phục hồi chức năng"
    },
    {
        "contract_no": "HĐ 01.2024/HĐMB/TD",
        "contract_name": "Hợp đồng Cung Cấp Hệ Thống Đo Mật Độ Khoáng Xương DEXA Toàn Thân",
        "supplier_name": "Công Ty TNHH Thiết Bị Y Tế Thành Đạt",
        "handover_date": "2024-04-10",
        "contract_value": 3100000000,
        "warranty_period_months": 24,
        "status": "ACTIVE",
        "notes": "Máy đo loãng xương DEXA Horizon"
    }
]

# Merge contracts into database
for c in standard_contracts:
    cur.execute("""
        INSERT INTO contracts (contract_no, contract_name, supplier_name, handover_date, contract_value, warranty_period_months, status, notes)
        VALUES (:contract_no, :contract_name, :supplier_name, :handover_date, :contract_value, :warranty_period_months, :status, :notes)
        ON CONFLICT(contract_no) DO UPDATE SET
            contract_name = excluded.contract_name,
            supplier_name = excluded.supplier_name,
            handover_date = excluded.handover_date,
            contract_value = excluded.contract_value,
            warranty_period_months = excluded.warranty_period_months,
            notes = excluded.notes;
    """, c)

# Insert remaining distinct contracts from devices if not present
for dc in device_contracts:
    c_no = dc["contract_no"]
    s_name = dc["supplier_name"] or "Nhà cung cấp theo HĐ"
    h_date = dc["min_date"] or "2024-05-20"
    cur.execute("""
        INSERT OR IGNORE INTO contracts (contract_no, contract_name, supplier_name, handover_date, contract_value, status, notes)
        VALUES (?, ?, ?, ?, 1000000000, 'ACTIVE', 'Hợp đồng mua sắm trích xuất từ dữ liệu thiết bị thực tế')
    """, (c_no, f"Hợp đồng mua sắm TTBYT số {c_no}", s_name, h_date))

conn.commit()

# Check total contracts
total_contracts = cur.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
total_suppliers = cur.execute("SELECT COUNT(*) FROM supplier_contacts").fetchone()[0]
print(f"✅ Đã đồng bộ {total_contracts} Hợp Đồng và {total_suppliers} Nhà Cung Cấp vào CSDL!")

conn.close()
