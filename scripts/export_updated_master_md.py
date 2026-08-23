"""
Script export toàn bộ danh mục 1.211 thiết bị y tế chuẩn hóa từ SQLite ra Markdown & CSV
"""
import sys
import io
import csv
import sqlite3
from pathlib import Path
from datetime import datetime

# UTF-8 handling for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent
DB_PATH = ROOT_DIR / "database" / "devices.db"
DOCS_DIR = ROOT_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
MD_OUTPUT = DOCS_DIR / "DANH_MUC_THIET_BI_Y_TE_BVQ7.md"
CSV_OUTPUT = ROOT_DIR / "database" / "master_device_registry.csv"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Fetch devices with facility & category names
q = """
SELECT 
    d.id,
    d.device_name,
    d.model,
    d.serial_no,
    d.manufacturer,
    d.country_of_manufacturer,
    d.risk_level,
    d.status,
    d.contract_no,
    d.supplier_name,
    f.name as facility_name,
    c.name as category_name,
    d.created_at,
    d.updated_at
FROM devices d
LEFT JOIN facilities f ON f.id = d.facility_id
LEFT JOIN device_categories c ON c.id = d.category_id
ORDER BY d.id ASC
"""
devices = cur.execute(q).fetchall()
print(f"📊 Đang xuất {len(devices)} thiết bị ra file Markdown...")

# 2. Build Markdown content
md_lines = [
    "# DANH MỤC TRANG THIẾT BỊ Y TẾ CHUẨN HÓA — PKĐK TÂM ANH QUẬN 7 (BVQ7)",
    f"> **Phiên bản:** MasterData V6.1 (Đã đối soát & chuẩn hóa sau Audit)"
    f"> **Cập nhật ngày:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
    f"> **Tổng số thiết bị:** {len(devices):,} thiết bị y tế",
    "",
    "---",
    "",
    "## 1. BẢNG TỔNG HỢP THEO PHÂN LOẠI RỦI RO (THÔNG TƯ 05/2022/TT-BYT)",
    "",
    "| Mức độ rủi ro | Định nghĩa lâm sàng | Số lượng thiết bị | Tỷ lệ (%) |",
    "|:---:|:---|:---:|:---:|",
]

# Calculate stats
risk_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
for d in devices:
    r = d["risk_level"] or "A"
    risk_counts[r] = risk_counts.get(r, 0) + 1

tot = len(devices)
md_lines.append(f"| **Loại A** | Rủi ro thấp (Đèn đọc phim, giường bệnh, nhiệt kế, cân đo) | **{risk_counts.get('A',0):,}** | {risk_counts.get('A',0)/tot*100:.1f}% |")
md_lines.append(f"| **Loại B** | Rủi ro trung bình thấp (Monitor, bơm tiêm điện, máy truyền dịch) | **{risk_counts.get('B',0):,}** | {risk_counts.get('B',0)/tot*100:.1f}% |")
md_lines.append(f"| **Loại C** | Rủi ro trung bình cao (Siêu âm, X-quang, Dao mổ điện, Nội soi) | **{risk_counts.get('C',0):,}** | {risk_counts.get('C',0)/tot*100:.1f}% |")
md_lines.append(f"| **Loại D** | Rủi ro đặc biệt cao (Máy thở, Sốc tim, Gây mê kèm thở, RO Thận) | **{risk_counts.get('D',0):,}** | {risk_counts.get('D',0)/tot*100:.1f}% |")
md_lines.append(f"| **TỔNG CỘNG** | **Toàn bộ trang thiết bị y tế tại PKĐK Tâm Anh Q7** | **{tot:,}** | **100.0%** |")

md_lines.extend([
    "",
    "---",
    "",
    "## 2. DANH SÁCH CHI TIẾT 1.211 THIẾT BỊ Y TẾ",
    "",
    "| STT | Mã tài sản | Tên thiết bị | Model | Serial No (S/N) | Hãng SX | Nước SX | Khoa/Phòng quản lý | Rủi ro | Trạng thái |",
    "|:---:|:---|:---|:---|:---|:---|:---|:---|:---:|:---:|"
])

for i, d in enumerate(devices, 1):
    asset_tag = f"BVQ7-TTB-{d['id']:05d}"
    name = (d["device_name"] or "N/A").replace("|", "/")
    model = (d["model"] or "-").replace("|", "/")
    sn = f"`{d['serial_no']}`" if d["serial_no"] and d["serial_no"] != "None" and d["serial_no"] != "-" else "-"
    mfg = (d["manufacturer"] or "-").replace("|", "/")
    origin = (d["country_of_manufacturer"] or "-").replace("|", "/")
    fac = (d["facility_name"] or "Chưa phân bổ").replace("|", "/")
    risk = d["risk_level"] or "A"
    status = d["status"] or "IN_SERVICE"
    
    md_lines.append(f"| {i} | `{asset_tag}` | {name} | {model} | {sn} | {mfg} | {origin} | {fac} | **{risk}** | `{status}` |")

with open(MD_OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")
print(f"✅ Đã ghi thành công: {MD_OUTPUT} ({MD_OUTPUT.stat().st_size:,} bytes)")

# 3. Export CSV for Master Registry
with open(CSV_OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "STT", "AssetTag", "DeviceName", "Model", "SerialNo", "Manufacturer", 
        "CountryOfOrigin", "FacilityName", "CategoryName", "RiskLevel", "Status", "ContractNo", "SupplierName"
    ])
    for i, d in enumerate(devices, 1):
        asset_tag = f"BVQ7-TTB-{d['id']:05d}"
        writer.writerow([
            i,
            asset_tag,
            d["device_name"] or "",
            d["model"] or "",
            d["serial_no"] or "",
            d["manufacturer"] or "",
            d["country_of_manufacturer"] or "",
            d["facility_name"] or "",
            d["category_name"] or "",
            d["risk_level"] or "A",
            d["status"] or "IN_SERVICE",
            d["contract_no"] or "",
            d["supplier_name"] or ""
        ])
print(f"✅ Đã ghi thành công: {CSV_OUTPUT} ({CSV_OUTPUT.stat().st_size:,} bytes)")
