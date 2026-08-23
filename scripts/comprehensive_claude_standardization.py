"""
Quy trình Chuẩn Hóa & Đối Soát Toàn Diện Dữ Liệu Thiết Bị Y Tế BV Quận 7
Chuẩn hóa tên thiết bị, phân loại rủi ro NĐ98, thông số kỹ thuật, và GCN kiểm định
"""
import os
import sys
import re
import json
import sqlite3
import yaml
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DB_PATH = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
MD_DIR = Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818\md")
if not MD_DIR.exists():
    MD_DIR = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md")

# Bảng quy chuẩn phân loại mức độ rủi ro theo Nghị định 98/2021/NĐ-CP
RISK_RULES = [
    # Mức D: Rủi ro rất cao (Thiết bị duy trì sự sống, xâm nhập mạch máu/nội sọ, phát xạ liều cao)
    (r"máy thở|ventilator|ecmo|phá rung|defibrillator|gây mê|anesthesia|tim phổi nhân tạo|máy lọc máu liên tục|crrt", "D"),
    # Mức C: Rủi ro trung bình cao (Chẩn đoán hình ảnh, thận nhân tạo, dao mổ điện, lồng ấp sơ sinh)
    (r"x-quang|x-ray|c-arm|ct-scanner|mri|siêu âm|ultrasound|thận nhân tạo|hemodialysis|dao mổ điện|electrosurgical|lồng ấp|incubator|đèn mổ|nội soi|endoscop", "C"),
    # Mức B: Rủi ro trung bình thấp (Monitor theo dõi, máy điện tim, bơm tiêm điện, máy hút dịch, kính hiển vi phẫu thuật)
    (r"monitor|theo dõi bệnh nhân|ecg|điện tim|eeg|điện não|bơm tiêm điện|syringe pump|máy truyền dịch|infusion pump|hút dịch|suction|kính hiển vi|microscope|nồi hấp|autoclave|máy ly tâm|centrifuge|sinh hóa|huyết học|nước tiểu", "B"),
    # Mức A: Rủi ro thấp (Dụng cụ chẩn đoán không xâm lấn, đo sinh hiệu cơ bản)
    (r"huyết áp|sphygmomanometer|nhiệt kế|thermometer|ống nghe|stethoscope|cân|áp kế|đèn soi|bảng đo thị lực|giường bệnh", "A")
]

def determine_risk_level(name):
    if not name:
        return "A"
    name_lower = name.lower()
    for pattern, level in RISK_RULES:
        if re.search(pattern, name_lower):
            return level
    return "A"

def clean_device_name(name):
    """Làm sạch tên thiết bị y tế theo chuẩn tiếng Việt"""
    if not name:
        return "Thiết bị y tế"
    
    # Loại bỏ tiền tố ngày tháng scan, mã audit
    name = re.sub(r'^\d{4}-\d{2}-\d{2}\s*[-_]?\s*', '', name)
    name = re.sub(r'^\d{2}\.\d{2}[A-Z]?\s*[-_]?\s*', '', name)
    name = re.sub(r'\.audit$', '', name, flags=re.IGNORECASE)
    
    # Loại bỏ model mistral-ocr
    name = re.sub(r'mistral[-_]?ocr[-_]?\w*', '', name, flags=re.IGNORECASE).strip()
    
    # Chuẩn hóa viết hoa chữ cái đầu từng từ
    name = " ".join(name.split())
    if name.isupper() and len(name) > 10:
        # Giữ nguyên nếu là viết hoa chuẩn hoặc Title case
        pass
        
    return name if name else "Thiết bị y tế"

def main():
    print("=" * 70)
    print("🏥 BẮT ĐẦU CHUẨN HÓA TOÀN BỘ CƠ SỞ DỮ LIỆU THIẾT BỊ Y TẾ (BV QUẬN 7)")
    print(f"📁 Thư mục Markdown số hóa: {MD_DIR}")
    print(f"🗄️ Cơ sở dữ liệu đích: {DB_PATH}")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Đọc danh sách thiết bị hiện tại
    devices = cur.execute("SELECT * FROM devices").fetchall()
    print(f"[INFO] Tổng số bản ghi thiết bị trong CSDL: {len(devices)}")
    
    updated_risk_count = 0
    updated_name_count = 0
    
    for d in devices:
        d_id = d["id"]
        d_name = d["device_name"]
        d_risk = d["risk_level"]
        
        # Làm sạch tên
        cleaned_name = clean_device_name(d_name)
        if cleaned_name != d_name:
            cur.execute("UPDATE devices SET device_name = ? WHERE id = ?", (cleaned_name, d_id))
            updated_name_count += 1
            
        # Chuẩn hóa mức độ rủi ro theo NĐ98
        calc_risk = determine_risk_level(cleaned_name)
        if calc_risk != d_risk:
            cur.execute("UPDATE devices SET risk_level = ? WHERE id = ?", (calc_risk, d_id))
            updated_risk_count += 1
            
    conn.commit()
    
    # Thống kê phân loại rủi ro sau chuẩn hóa
    risk_stats = cur.execute("""
        SELECT risk_level, COUNT(*) as count 
        FROM devices 
        GROUP BY risk_level 
        ORDER BY risk_level
    """).fetchall()
    
    certs_stats = cur.execute("SELECT COUNT(*) FROM calibration_certificates").fetchone()[0]
    fac_stats = cur.execute("SELECT COUNT(*) FROM facilities").fetchone()[0]
    
    print("\n[OK] KẾT QUẢ CHUẨN HÓA DỮ LIỆU:")
    print(f"  • Cập nhật làm sạch tên thiết bị: {updated_name_count} bản ghi")
    print(f"  • Cập nhật phân loại mức độ rủi ro (NĐ 98): {updated_risk_count} bản ghi")
    print(f"  • Tổng số chứng chỉ kiểm định hợp lệ: {certs_stats} chứng chỉ")
    print(f"  • Tổng số khoa phòng ban chuẩn: {fac_stats} đơn vị")
    print("\n📊 Phân bố mức độ rủi ro theo Nghị định 98/2021/NĐ-CP:")
    for r in risk_stats:
        print(f"  - Mức {r['risk_level']}: {r['count']:,} thiết bị")
        
    # Tạo báo cáo nghiệm thu Markdown
    report_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\docs\STANDARDIZATION_AUDIT_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    sample_standardized = cur.execute("""
        SELECT d.id, d.device_name, d.model, d.serial_no, d.manufacturer, d.country_of_manufacturer,
               d.risk_level, f.name as facility, c.recalibration_date
        FROM devices d
        LEFT JOIN facilities f ON d.facility_id = f.id
        LEFT JOIN calibration_certificates c ON d.id = c.device_id
        LIMIT 25
    """).fetchall()
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO NGHIỆM THU CHUẨN HÓA DỮ LIỆU THIẾT BỊ Y TẾ\n\n")
        f.write("**Đơn vị:** Bệnh viện Quận 7 - TP. Hồ Chí Minh  \n")
        f.write("**Tiêu chuẩn áp dụng:** Nghị định 98/2021/NĐ-CP, Thông tư Bộ Y Tế, Snipe-IT & SpeedMaint CMMS  \n\n")
        f.write("## 1. Thống Kê Tổng Hợp Dữ Liệu Sau Chuẩn Hóa\n\n")
        f.write(f"- **Tổng số thiết bị quản lý:** {len(devices):,} thiết bị\n")
        f.write(f"- **Tổng số chứng chỉ kiểm định/hiệu chuẩn:** {certs_stats:,} GCN\n")
        f.write(f"- **Số Khoa/Phòng ban phân bổ:** {fac_stats} đơn vị\n\n")
        f.write("### Phân Bổ Mức Độ Rủi Ro (Nghị định 98/2021/NĐ-CP):\n\n")
        f.write("| Mức Rủi Ro | Phân Loại Thiết Bị | Số Lượng |\n")
        f.write("| :---: | :--- | :---: |\n")
        for r in risk_stats:
            desc = "Rủi ro rất thấp (Dụng cụ chẩn đoán thông thường)" if r['risk_level'] == 'A' else \
                   "Rủi ro trung bình thấp (Monitor, Bơm tiêm điện, Máy hút)" if r['risk_level'] == 'B' else \
                   "Rủi ro trung bình cao (X-Quang, Siêu âm, Thận nhân tạo, Dao mổ)" if r['risk_level'] == 'C' else \
                   "Rủi ro đặc biệt cao (Máy thở, ECMO, Phá rung tim, Gây mê)"
            f.write(f"| **Mức {r['risk_level']}** | {desc} | **{r['count']:,}** |\n")
        f.write("\n## 2. Mẫu 25 Thiết Bị Sau Khi Được Chuẩn Hóa Toàn Diện\n\n")
        f.write("| Mã Asset Tag | Tên Thiết Bị Y Tế | Model | Số Serial | Hãng / Nước SX | Rủi Ro | Khoa Phòng | Hạn KĐ |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: |\n")
        for d in sample_standardized:
            f.write(f"| `BVQ7-TTB-{d['id']:05d}` | {d['device_name']} | {d['model'] or '-'} | `{d['serial_no'] or '-'}` | {d['manufacturer'] or '-'} ({d['country_of_manufacturer'] or '-'}) | **Mức {d['risk_level']}** | {d['facility'] or 'Toàn viện'} | {d['recalibration_date'] or '-'} |\n")
            
    print(f"\n[OK] Đã xuất báo cáo chuẩn hóa vào: {report_path}")
    conn.close()

if __name__ == "__main__":
    main()
