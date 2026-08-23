"""
Script xuất tài liệu Markdown tổng hợp: Danh mục Thiết Bị & Danh Sách Tệp PDF Minh Chứng Đính Kèm
"""
import sys
import io
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
output_md = Path(r"C:\Users\tantt\Downloads\medical-device-app\docs\DANH_SACH_THIET_BI_VA_FILE_PDF_MINH_CHUNG.md")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Fetch devices with facility
q_dev = """
SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.manufacturer, 
       d.country_of_manufacturer, d.risk_level, f.name as facility_name
FROM devices d
LEFT JOIN facilities f ON f.id = d.facility_id
ORDER BY f.name ASC, d.id ASC
"""
devices = cur.execute(q_dev).fetchall()

# 2. Fetch all documents grouped by device_id
q_docs = """
SELECT device_id, doc_type, title, file_size, match_method
FROM device_documents
ORDER BY id ASC
"""
all_docs = cur.execute(q_docs).fetchall()

doc_map = defaultdict(list)
seen_titles_per_dev = defaultdict(set)

for doc in all_docs:
    dev_id = doc["device_id"]
    title = doc["title"]
    # Deduplicate same title for same device to keep markdown clean & readable
    if title not in seen_titles_per_dev[dev_id]:
        seen_titles_per_dev[dev_id].add(title)
        doc_map[dev_id].append(doc)

# 3. Format file size helper
def fmt_size(bytes_sz):
    if not bytes_sz or bytes_sz == 0:
        return "0 KB"
    if bytes_sz < 1024 * 1024:
        return f"{bytes_sz / 1024:.1f} KB"
    return f"{bytes_sz / (1024 * 1024):.1f} MB"

DOC_TYPE_LABELS = {
    "HANDOVER": "Biên Bản Bàn Giao",
    "CALIBRATION": "Kiểm Định & Hiệu Chuẩn",
    "CONTRACT": "Hợp Đồng Mua Sắm",
    "MAINTENANCE": "Bảo Trì & Sửa Chữa",
    "LEGAL": "Hồ Sơ Pháp Lý / CO-CQ",
    "OTHER": "Tài Liệu Kỹ Thuật"
}

# Group devices by facility
fac_devices = defaultdict(list)
for d in devices:
    fac_name = d["facility_name"] or "Kho TTBYT Tổng Hợp"
    fac_devices[fac_name].append(d)

print(f"📊 Bắt đầu xuất file Markdown cho {len(devices)} thiết bị tại {len(fac_devices)} khoa/phòng...")

lines = []
lines.append("# 🏥 BẢNG ĐỐI SOÁT DANH MỤC TRANG THIẾT BỊ Y TẾ & TỆP PDF MINH CHỨNG NGUỒN GỐC")
lines.append(f"*Bệnh viện Đa khoa Tâm Anh TP.HCM — Chi nhánh PKĐK Quận 7*")
lines.append(f"*Thời gian xuất báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")
lines.append(f"*Nguồn dữ liệu: CSDL SQLite `devices.db` & Kho số hóa `G:\\BV QUẬN 7_OCR_WORK_20260712`*")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 📌 1. TỔNG QUAN HỒ SƠ MINH CHỨNG")
lines.append(f"- **Tổng số thiết bị y tế trong hệ thống:** **{len(devices):,} thiết bị**")
lines.append(f"- **Tổng số khoa / phòng quản lý:** **{len(fac_devices)} khoa phòng**")
lines.append(f"- **Tổng số liên kết tài liệu PDF đã lập chỉ mục:** **{len(all_docs):,} tài liệu**")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 📋 2. CHI TIẾT THIẾT BỊ VÀ TỆP PDF MINH CHỨNG THEO KHOA/PHÒNG")
lines.append("")

total_listed_docs = 0

for fac_idx, (fac_name, dev_list) in enumerate(fac_devices.items(), 1):
    lines.append(f"### 🏢 {fac_idx}. Khoa / Phòng: {fac_name} ({len(dev_list)} thiết bị)")
    lines.append("")
    
    for d in dev_list:
        dev_id = d["id"]
        dev_code = f"BVQ7-TTB-{dev_id:05d}"
        d_name = d["device_name"]
        d_model = d["model"] or "Tiêu chuẩn"
        d_sn = d["serial_no"] or "Chưa có"
        d_mfg = d["manufacturer"] or "Chính hãng"
        d_country = d["country_of_manufacturer"] or "Đang cập nhật"
        d_contract = d["contract_no"] or "Đang cập nhật"
        d_risk = d["risk_level"] or "A"
        
        docs = doc_map[dev_id]
        total_listed_docs += len(docs)
        
        lines.append(f"#### 🔹 `{dev_code}` — **{d_name}**")
        lines.append(f"- **Model:** `{d_model}` | **Serial (S/N):** `{d_sn}` | **Mức độ rủi ro:** Phân loại `{d_risk}`")
        lines.append(f"- **Hãng sản xuất:** {d_mfg} ({d_country}) | **Số HĐ:** `{d_contract}`")
        
        if not docs:
            lines.append(f"- *Tài liệu minh chứng:* Chưa có tệp đính kèm trực tiếp.")
        else:
            lines.append(f"- **Danh sách tệp PDF minh chứng ({len(docs)} tệp):**")
            lines.append("")
            lines.append("| STT | Phân loại hồ sơ | Tên tệp PDF minh chứng | Dung lượng | Phương thức khớp |")
            lines.append("|:---:|:---|:---|:---:|:---:|")
            for doc_idx, doc in enumerate(docs, 1):
                type_label = DOC_TYPE_LABELS.get(doc["doc_type"], doc["doc_type"])
                title = doc["title"].replace("|", "/")
                sz = fmt_size(doc["file_size"])
                method = doc["match_method"]
                method_label = {
                    "SERIAL": "Khớp Số Serial (S/N)",
                    "CONTRACT": "Khớp Số Hợp Đồng",
                    "MODEL": "Khớp Theo Model / Lô",
                    "CALIBRATION_CERT": "Giấy Chứng Nhận Kiểm Định",
                    "FACILITY_HANDOVER": "Biên Bản Khoa Phòng"
                }.get(method, method)
                lines.append(f"| {doc_idx} | {type_label} | `{title}` | {sz} | {method_label} |")
        
        lines.append("")
    lines.append("---")
    lines.append("")

output_md.parent.mkdir(parents=True, exist_ok=True)
with open(output_md, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ Đã ghi thành công file Markdown: {output_md} ({output_md.stat().st_size:,} bytes)")
conn.close()
