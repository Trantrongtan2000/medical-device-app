import sqlite3
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")

print("🏥 THIẾT LẬP CÁC BẢNG CƠ SỞ DỮ LIỆU CHUYÊN SÂU LÂM SÀNG (HTM V3):\n" + "=" * 70)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Bảng Phụ Kiện / Cấu Kiện Đi Kèm (Parent-Child Device Accessories)
cur.execute("""
    CREATE TABLE IF NOT EXISTS device_accessories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_device_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        model TEXT,
        serial_no TEXT,
        accessory_type TEXT, -- Probe, Cable, Electrode, Blade, Battery, Cart, Adapter
        status TEXT DEFAULT 'Sẵn sàng sử dụng',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_device_id) REFERENCES devices (id) ON DELETE CASCADE
    );
""")

# 2. Bảng Bảng Kiểm Tra An Toàn Đầu Ngày (Daily Pre-use Clinical Safety Checklists)
cur.execute("""
    CREATE TABLE IF NOT EXISTS pre_use_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        inspector_name TEXT NOT NULL,
        department TEXT NOT NULL,
        power_ok BOOLEAN DEFAULT 1,
        physical_ok BOOLEAN DEFAULT 1,
        gas_pressure_ok BOOLEAN DEFAULT 1,
        selftest_ok BOOLEAN DEFAULT 1,
        overall_status TEXT DEFAULT 'PASSED', -- PASSED, FAILED, WARNING
        notes TEXT,
        inspection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
    );
""")

# 3. Bảng Điều Chuyển Thiết Bị Giữa Các Khoa Phòng (Device Transfers - QT.08)
cur.execute("""
    CREATE TABLE IF NOT EXISTS device_transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        from_facility_id INTEGER NOT NULL,
        to_facility_id INTEGER NOT NULL,
        giver_name TEXT NOT NULL,
        receiver_name TEXT NOT NULL,
        transfer_reason TEXT,
        transfer_date DATE NOT NULL,
        form_code TEXT DEFAULT 'BM08_TA5.TTBYT.QT.08',
        status TEXT DEFAULT 'COMPLETED', -- PENDING, COMPLETED, CANCELLED
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (id),
        FOREIGN KEY (from_facility_id) REFERENCES facilities (id),
        FOREIGN KEY (to_facility_id) REFERENCES facilities (id)
    );
""")

conn.commit()
print("✅ Đã khởi tạo 3 bảng: `device_accessories`, `pre_use_inspections`, `device_transfers`")

# 4. Nạp dữ liệu thực tế cho các phụ kiện từ hồ sơ giao nhận đã đọc
# Find parent device IDs
cur.execute("SELECT id, model, device_name, serial_no FROM devices")
devices_dict = {f"{r[1]}_{r[3]}": r[0] for r in cur.fetchall()}

# Add Voluson P8 probes
p8_id = None
for k, v in devices_dict.items():
    if "Voluson" in k or "VP8206119" in k:
        p8_id = v
        break

if not p8_id:
    # If not found by serial, find by model
    cur.execute("SELECT id FROM devices WHERE model LIKE '%Voluson%' LIMIT 1")
    row = cur.fetchone()
    if row:
        p8_id = row[0]

if p8_id:
    cur.execute("DELETE FROM device_accessories WHERE parent_device_id = ?", (p8_id,))
    probes = [
        (p8_id, "Đầu dò Convex 2D", "4C-RS", "1352048WX1", "Probe", "Sẵn sàng sử dụng", "Đầu dò siêu âm bụng tổng quát"),
        (p8_id, "Đầu dò Khối 3D/4D Real-time", "RAB2-6-RS", "1349109WX9", "Probe", "Sẵn sàng sử dụng", "Đầu dò siêu âm 4D chuyên sản khoa"),
        (p8_id, "Đầu dò Âm đạo / Sản phụ khoa", "IC9-RS", "1348559WX4", "Probe", "Sẵn sàng sử dụng", "Đầu dò siêu âm đầu dò ngả âm đạo"),
        (p8_id, "Đầu dò Linear Mạch máu / Tuyến giáp", "12L-RS", "1353969WX7", "Probe", "Sẵn sàng sử dụng", "Đầu dò tần số cao mạch máu")
    ]
    cur.executemany("INSERT INTO device_accessories (parent_device_id, name, model, serial_no, accessory_type, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", probes)
    print(f"✅ Đã nạp 4 đầu dò chuyên dụng cho Máy siêu âm Voluson P8 (ID: {p8_id})")

# Add BTL-4625 accessories
btl_id = None
cur.execute("SELECT id FROM devices WHERE model LIKE '%4625%' LIMIT 1")
r_btl = cur.fetchone()
if r_btl:
    btl_id = r_btl[0]
    cur.execute("DELETE FROM device_accessories WHERE parent_device_id = ?", (btl_id,))
    btl_accs = [
        (btl_id, "Đầu phát siêu âm rảnh tay HandsFree Sono 4", "HandsFree Sono 4", "4474B05653", "Electrode", "Sẵn sàng sử dụng", "Kèm giá đỡ Lot: P0PB021385"),
        (btl_id, "Bộ 4 điện cực cao su 5x7cm kèm bao xốp", "BTL-Rubber5x7", "BTL-EL-01", "Electrode", "Sẵn sàng sử dụng", "Kèm cáp nối 2 kênh xám trắng / xám đậm"),
        (btl_id, "Xe đẩy chuyên dụng chính hãng BTL", "Smart/Premium Cart", "CART-BTL-991", "Cart", "Sẵn sàng sử dụng", "Xe đẩy 4 bánh có khóa")
    ]
    cur.executemany("INSERT INTO device_accessories (parent_device_id, name, model, serial_no, accessory_type, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", btl_accs)
    print(f"✅ Đã nạp 3 phụ kiện chính hãng cho Máy điện trị liệu BTL-4625 (ID: {btl_id})")

# Add Video Laryngoscope blades
cur.execute("SELECT id FROM devices WHERE model LIKE '%ClearVue%' OR device_name LIKE '%nội khí quản%' LIMIT 1")
r_vl = cur.fetchone()
if r_vl:
    vl_id = r_vl[0]
    cur.execute("DELETE FROM device_accessories WHERE parent_device_id = ?", (vl_id,))
    vl_accs = [
        (vl_id, "Lưỡi soi thanh quản MAC 2 (Nhi)", "MAC 2", "BL-MAC2-01", "Blade", "Sẵn sàng sử dụng", "Thép không gỉ y tế tiệt trùng"),
        (vl_id, "Lưỡi soi thanh quản MAC 3 (Người lớn)", "MAC 3", "BL-MAC3-01", "Blade", "Sẵn sàng sử dụng", "Tiêu chuẩn phòng mổ GMHS"),
        (vl_id, "Lưỡi soi thanh quản MAC 4 (Thể trạng lớn)", "MAC 4", "BL-MAC4-01", "Blade", "Sẵn sàng sử dụng", "Dành cho bệnh nhân đặt NKQ khó"),
        (vl_id, "Bộ cáp sạc và nguồn y tế", "Infinium Power", "PWR-VL3R-01", "Adapter", "Sẵn sàng sử dụng", "Sạc nhanh an toàn")
    ]
    cur.executemany("INSERT INTO device_accessories (parent_device_id, name, model, serial_no, accessory_type, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", vl_accs)
    print(f"✅ Đã nạp 4 phụ kiện cho Bộ đặt nội khí quản Video ClearVue VL3R (ID: {vl_id})")

# Add sample Pre-use Inspection
cur.execute("SELECT id FROM devices WHERE model LIKE '%TV-100%' LIMIT 1")
r_tv = cur.fetchone()
if r_tv:
    cur.execute("""
        INSERT INTO pre_use_inspections (device_id, inspector_name, department, power_ok, physical_ok, gas_pressure_ok, selftest_ok, overall_status, notes)
        VALUES (?, 'ĐD. Lê Thị Mai', 'Khoa Cấp Cứu', 1, 1, 1, 1, 'PASSED', 'Kiểm tra đầu ca sáng: Nguồn điện UPS ổn định, Áp suất O2 4.2 bar, Self-test máy thở TV-100 báo PASS 100%.')
    """, (r_tv[0],))
    print(f"✅ Đã tạo Bảng kiểm an toàn đầu ngày cho Máy thở TV-100 (Khoa Cấp Cứu)")

# Add sample Device Transfer
if btl_id:
    cur.execute("""
        INSERT INTO device_transfers (device_id, from_facility_id, to_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, status)
        VALUES (?, 21, 7, 'Trần Trọng Cẩn (Kho TTB)', 'BS. Trưởng Khoa PHCN', 'Cấp phát đưa vào phục vụ bệnh nhân Phục Hồi Chức Năng theo HĐ 26022026/GM-BVĐKTA', '2026-04-18', 'COMPLETED')
    """, (btl_id,))
    print("✅ Đã tạo Phiếu điều chuyển mẫu QT.08 từ Kho TTB sang Khoa PHCN")

conn.commit()
conn.close()
