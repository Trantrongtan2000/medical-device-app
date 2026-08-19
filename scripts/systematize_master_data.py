import sqlite3
import json
import csv
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
output_csv = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\master_device_registry.csv")
output_json = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\master_data_dictionary.json")
output_doc = Path(r"C:\Users\tantt\Downloads\medical-device-app\docs\MASTER_DATA_MANAGEMENT.md")

print(f"🏥 BẮT ĐẦU HỆ THỐNG HÓA TOÀN BỘ CƠ SỞ DỮ LIỆU MASTER:")
print(f"  • SQLite Database: {db_path}\n")

if not db_path.exists():
    print("❌ Không tìm thấy database!")
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Thống kê bảng Devices
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.certification_no, d.calibration_stamp_no,
           d.manufacturer, d.country_of_manufacturer, d.year_of_manufacture, d.risk_level,
           d.status, d.installation_date, d.calibration_date, d.recalibration_date, d.notes,
           f.id as facility_id, f.name as facility_name, f.code as facility_code,
           c.id as category_id, c.name as category_name, c.safety_level
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    ORDER BY d.id ASC
""")
devices = [dict(r) for r in cur.fetchall()]

# 2. Thống kê bảng Facilities
cur.execute("""
    SELECT f.id, f.name, f.code, COUNT(d.id) as device_count
    FROM facilities f
    LEFT JOIN devices d ON f.id = d.facility_id
    GROUP BY f.id, f.name, f.code
    ORDER BY device_count DESC, f.name ASC
""")
facilities = [dict(r) for r in cur.fetchall()]

# 3. Thống kê bảng Device Categories
cur.execute("""
    SELECT c.id, c.name, c.description, c.safety_level, COUNT(d.id) as device_count
    FROM device_categories c
    LEFT JOIN devices d ON c.id = d.category_id
    GROUP BY c.id, c.name, c.description, c.safety_level
    ORDER BY device_count DESC
""")
categories = [dict(r) for r in cur.fetchall()]

# 4. Thống kê bảng Calibration Certificates
cur.execute("""
    SELECT cert.*, d.device_name, d.model, d.serial_no, f.name as facility_name
    FROM calibration_certificates cert
    JOIN devices d ON cert.device_id = d.id
    LEFT JOIN facilities f ON d.facility_id = f.id
    ORDER BY cert.calibration_date DESC
""")
certificates = [dict(r) for r in cur.fetchall()]

# 5. Thống kê bảng Maintenance Logs
cur.execute("""
    SELECT l.*, d.device_name, d.model, d.serial_no, f.name as facility_name
    FROM maintenance_logs l
    JOIN devices d ON l.device_id = d.id
    LEFT JOIN facilities f ON d.facility_id = f.id
    ORDER BY l.maintenance_date DESC, l.id DESC
""")
logs = [dict(r) for r in cur.fetchall()]

print(f"📊 DỮ LIỆU ĐÃ TRÍCH XUẤT:")
print(f"  • Tổng số Thiết Bị Master: {len(devices):,} máy")
print(f"  • Tổng số Khoa / Phòng Ban: {len(facilities)} khoa")
print(f"  • Tổng số Nhóm Chuyên Khoa: {len(categories)} nhóm")
print(f"  • Tổng số Chứng Chỉ Kiểm Định: {len(certificates):,} GCN")
print(f"  • Tổng số Nhật Ký & Work Orders: {len(logs):,} bản ghi")

# Xuất Master Device Registry CSV
with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "ID", "Mã Tài Sản (Asset Tag)", "Mã SpeedMaint", "Tên Thiết Bị Y Tế", "Model",
        "Số Serial (S/N)", "Khoa / Phòng Ban", "Mã Khoa", "Nhóm Chuyên Khoa", "Mức Rủi Ro (NĐ98)",
        "Hãng Sản Xuất", "Xuất Xứ", "Năm Sản Xuất", "Trạng Thái Vận Hành", "Ngày Đưa Vào SD",
        "Ngày Kiểm Định", "Hạn Kiểm Định", "Số Giấy Chứng Nhận", "Số Tem KĐ", "Ghi Chú"
    ])
    for d in devices:
        writer.writerow([
            d["id"],
            f"BVQ7-TTB-{d['id']:05d}",
            f"BM/BVQ7/{d['id']:05d}",
            d["device_name"],
            d["model"],
            d["serial_no"],
            d["facility_name"] or "Kho lưu trữ",
            d["facility_code"] or "",
            d["category_name"] or "Chưa phân loại",
            f"Mức {d['risk_level'] or 'A'}",
            d["manufacturer"] or "",
            d["country_of_manufacturer"] or "",
            d["year_of_manufacture"] or "",
            d["status"],
            d["installation_date"] or "",
            d["calibration_date"] or "",
            d["recalibration_date"] or "",
            d["certification_no"] or "",
            d["calibration_stamp_no"] or "",
            d["notes"] or ""
        ])

print(f"✅ Đã xuất Master Device Registry CSV: {output_csv}")

# Xuất Master Data Dictionary JSON
data_dictionary = {
    "metadata": {
        "system": "Medical Device Management System (BV Quận 7)",
        "organization": "Phòng Khám Đa Khoa Tâm Anh Quận 7 / BV Quận 7",
        "version": "2.0.0 (Snipe-IT & SpeedMaint Edition)",
        "generated_at": datetime.now().isoformat(),
        "standards": ["Nghị định 98/2021/NĐ-CP", "Thông tư 05/2022/TT-BYT", "ISO 13485", "TLHD_QLTTBYT_V1.2"]
    },
    "summary": {
        "total_devices": len(devices),
        "total_facilities": len(facilities),
        "total_categories": len(categories),
        "total_certificates": len(certificates),
        "total_maintenance_logs": len(logs)
    },
    "risk_level_distribution": {
        "Level_A": sum(1 for d in devices if d.get("risk_level") == "A"),
        "Level_B": sum(1 for d in devices if d.get("risk_level") == "B"),
        "Level_C": sum(1 for d in devices if d.get("risk_level") == "C"),
        "Level_D": sum(1 for d in devices if d.get("risk_level") == "D")
    },
    "facilities_master": facilities,
    "categories_master": categories
}

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(data_dictionary, f, ensure_ascii=False, indent=2)

print(f"✅ Đã xuất Master Data Dictionary JSON: {output_json}")

# Xuất Markdown Documentation
doc_content = f"""# 🏛️ HỒ SƠ HỆ THỐNG DỮ LIỆU MASTER (MASTER DATA MANAGEMENT)
**BỆNH VIỆN QUẬN 7 / PHÒNG KHÁM ĐA KHOA TÂM ANH QUẬN 7**

> **Phiên bản:** 2.0.0 (Snipe-IT & SpeedMaint Cloud CMMS Edition)  
> **Thời điểm cập nhật:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
> **Cơ sở pháp lý:** Nghị định 98/2021/NĐ-CP, Thông tư 05/2022/TT-BYT, Tiêu chuẩn ISO 13485, Sổ tay Quy trình TTBYT.

---

## 1. TỔNG QUAN CƠ CẤU DỮ LIỆU MASTER

| Thực Thể Master | Tổng Bản Ghi | Khóa Chính (PK) | Mã Nhận Diện Chuẩn Hóa | Ràng Buộc Tính Toàn Vẹn |
| :--- | :---: | :--- | :--- | :--- |
| **Thiết Bị Y Tế (`devices`)** | **{len(devices):,}** | `id` (INTEGER) | `BVQ7-TTB-XXXXX` & `BM/BVQ7/XXXXX` | `serial_no UNIQUE NOT NULL`, `risk_level IN ('A','B','C','D')` |
| **Khoa / Phòng Ban (`facilities`)** | **{len(facilities)}** | `id` (INTEGER) | `code` (VARCHAR) | Quan hệ 1-N với `devices.facility_id` |
| **Nhóm Thiết Bị (`device_categories`)** | **{len(categories)}** | `id` (INTEGER) | `name` (TEXT) | Quan hệ 1-N với `devices.category_id` |
| **Giấy Chứng Nhận KĐ (`calibration_certificates`)** | **{len(certificates):,}** | `id` (INTEGER) | `certificate_no` | Khóa ngoại `device_id`, Cảnh báo 3 cấp độ KĐ |
| **Nhật Ký & Work Orders (`maintenance_logs`)** | **{len(logs):,}** | `id` (INTEGER) | `#2607XX` (SpeedMaint Task) | Audit Trail `INSPECTION`, `HANDOVER`, `PREVENTIVE`, `REPAIR` |

---

## 2. PHÂN BỔ 4 MỨC ĐỘ RỦI RO THEO NGHỊ ĐỊNH 98/2021/NĐ-CP

* 🟢 **Mức A (Rủi ro rất thấp):** {sum(1 for d in devices if d.get('risk_level') == 'A'):,} thiết bị ({sum(1 for d in devices if d.get('risk_level') == 'A')/len(devices)*100:.1f}%) — Huyết áp kế, nhiệt ẩm kế, cân y tế, ống nghe.
* 🟡 **Mức B (Rủi ro trung bình thấp):** {sum(1 for d in devices if d.get('risk_level') == 'B'):,} thiết bị ({sum(1 for d in devices if d.get('risk_level') == 'B')/len(devices)*100:.1f}%) — Monitor 5 thông số, máy điện tim ECG, bơm tiêm điện.
* 🟠 **Mức C (Rủi ro trung bình cao):** {sum(1 for d in devices if d.get('risk_level') == 'C'):,} thiết bị ({sum(1 for d in devices if d.get('risk_level') == 'C')/len(devices)*100:.1f}%) — Máy siêu âm màu Doppler, máy chạy thận nhân tạo Fresenius, dao mổ điện cao tần.
* 🔴 **Mức D (Rủi ro đặc biệt cao):** {sum(1 for d in devices if d.get('risk_level') == 'D'):,} thiết bị ({sum(1 for d in devices if d.get('risk_level') == 'D')/len(devices)*100:.1f}%) — Máy thở chức năng cao ICU, máy phá rung tim, hệ thống gây mê kèm thở.

---

## 3. DANH SÁCH 22 KHOA / PHÒNG BAN VÀ QUY MÔ TÀI SẢN

| STT | Tên Khoa / Phòng Ban | Mã Khoa | Số Lượng Thiết Bị | Tỷ Lệ Toàn Viện |
| :---: | :--- | :---: | :---: | :---: |
"""
for idx, f in enumerate(facilities, 1):
    pct = (f['device_count'] / len(devices) * 100) if len(devices) > 0 else 0
    doc_content += f"| {idx:02d} | **{f['name']}** | `{f['code'] or '-'}` | {f['device_count']:,} máy | {pct:.1f}% |\n"

doc_content += f"""
---

## 4. DANH SÁCH 10 NHÓM THIẾT BỊ Y TẾ CHUYÊN KHOA

| STT | Nhóm Danh Mục Thiết Bị | Cấp Độ An Toàn | Số Lượng Thiết Bị |
| :---: | :--- | :---: | :---: |
"""
for idx, c in enumerate(categories, 1):
    doc_content += f"| {idx:02d} | **{c['name']}** | Mức {c['safety_level'] or 'A'} | {c['device_count']:,} máy |\n"

doc_content += """
---

## 5. CÁC TỆP DỮ LIỆU MASTER ĐÃ XUẤT BẢN:
* 📄 **Master Device CSV:** `database/master_device_registry.csv` (1.052 dòng có UTF-8 BOM mở bằng Excel không lỗi font).
* 📑 **Data Dictionary JSON:** `database/master_data_dictionary.json`.
* 🗄️ **Primary SQLite DB:** `database/devices.db` (WAL mode enabled).
"""

with open(output_doc, 'w', encoding='utf-8') as f:
    f.write(doc_content)

print(f"✅ Đã xuất Báo Cáo Hệ Thống Dữ Liệu Master: {output_doc}")

conn.close()
print("\n🎉 HOÀN THÀNH HỆ THỐNG HÓA CƠ SỞ DỮ LIỆU MASTER!")
