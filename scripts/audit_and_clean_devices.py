#!/usr/bin/env python3
"""
Script Audit & Chuẩn Hóa Danh Mục Tên Thiết Bị Y Tế (BV Quận 7)
"""

import sqlite3
import re
import sys
import yaml
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
MD_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md")
PDF_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")


def extract_real_device_info(md_file_path: Path, raw_name: str, raw_model: str, filename_stem: str):
    """Đọc tệp MD và tên file để trích xuất tên máy và model chuẩn nhất"""
    name = raw_name or ''
    model = raw_model or ''

    # Clean OCR engine name
    if 'mistral-ocr' in model.lower():
        model = 'N/A'

    # Nếu có tệp MD, đọc nội dung để tìm tên máy chính xác
    if md_file_path and md_file_path.exists():
        try:
            text = md_file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Tìm tên phương tiện đo / tên thiết bị trong nội dung văn bản OCR
            patterns = [
                r'Tên\s+phương\s+tiện\s+đo\s*[:\.]\s*([^\n\r\|]+)',
                r'Tên\s+thiết\s+bị\s*[:\.]\s*([^\n\r\|]+)',
                r'TÊN\s+THIẾT\s+BỊ\s*[:\.]\s*([^\n\r\|]+)',
                r'Thiết\s+bị\s*[:\.]\s*([^\n\r\|]+)',
                r'Tên\s+hàng\s+hóa\s*[:\.]\s*([^\n\r\|]+)',
                r'Đối\s+tượng\s+kiểm\s+định\s*[:\.]\s*([^\n\r\|]+)',
                r'Loại\s+phương\s+tiện\s+đo\s*[:\.]\s*([^\n\r\|]+)'
            ]
            
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    extracted = m.group(1).strip()
                    # Loại bỏ dấu kết thúc thừa
                    extracted = re.sub(r'[\*\_\#\:\;]+', '', extracted).strip()
                    if len(extracted) >= 3 and len(extracted) < 80 and not extracted.isdigit():
                        if name in ('Thiết bị y tế', 'N/A', 'Unknown', 'BBBG', 'BBNT', 'Giấy kiểm định') or name.isdigit() or 'kiểm xạ' in name.lower() or 'kiểm định' in name.lower():
                            name = extracted
                            break

            # Tìm Model trong văn bản nếu model đang là N/A
            if model in ('N/A', '', 'None'):
                model_match = re.search(r'(?:Kiểu\/Model|Ký hiệu\/Model|Model|Kiểu)\s*[:\.]\s*([A-Za-z0-9\-\/\.\s]+?)(?:[\n\r\|\,]|\s{2,})', text, re.IGNORECASE)
                if model_match:
                    found_mod = model_match.group(1).strip()
                    if 2 <= len(found_mod) <= 35 and not any(kw in found_mod.lower() for kw in ('tên', 'serial', 'nhà', 'hãng', 'ngày')):
                        model = found_mod

        except Exception:
            pass

    # Phân tích filename nếu tên vẫn còn dạng generic
    if name in ('Thiết bị y tế', 'N/A', 'Unknown', 'BBBG', 'BBNT', 'Giấy kiểm định') or name.isdigit() or len(name) <= 3 or 'kiểm xạ' in name.lower() or 'kiểm định' in name.lower():
        # Clean patterns like "25_Máy ly tâm_240425"
        m_num = re.match(r'^\d{1,3}[_\s-]+([A-Za-zÀ-ỹ\s\(\)]+?)(?:[_\s-]\d+|[_\s-][A-Z]+|$)', filename_stem)
        if m_num:
            name = m_num.group(1).strip()

        # Check keywords in filename
        for kw, std_name in [
            ('chẩn đoán xơ vữa mạch máu', 'Máy chẩn đoán xơ vữa mạch máu'),
            ('rửa bô', 'Máy rửa bô và khử khuẩn'),
            ('nồi hấp', 'Nồi hấp tiệt trùng'),
            ('cạo vôi răng', 'Máy cạo vôi răng siêu âm'),
            ('đa ký hô hấp', 'Máy đo đa ký hô hấp'),
            ('ghế nha khoa', 'Ghế máy nha khoa'),
            ('đo loãng xương', 'Máy đo loãng xương'),
            ('ống nội soi', 'Ống nội soi mềm'),
            ('ống soi', 'Ống nội soi mềm'),
            ('siêu âm', 'Máy siêu âm chẩn đoán'),
            ('điện tim', 'Máy điện tim (ECG)'),
            ('theo dõi bệnh nhân', 'Máy theo dõi bệnh nhân (Monitor)'),
            ('monitor', 'Máy theo dõi bệnh nhân (Monitor)'),
            ('bơm tiêm điện', 'Bơm tiêm điện'),
            ('máy thở', 'Máy thở y tế'),
            ('dao mổ', 'Dao mổ điện cao tần'),
            ('phá rung', 'Máy phá rung tim'),
            ('ly tâm', 'Máy ly tâm'),
            ('kính hiển vi', 'Kính hiển vi quang học'),
            ('an toàn sinh học', 'Tủ an toàn sinh học'),
            ('tủ mát', 'Tủ mát bảo quản dược phẩm'),
            ('tẩy trắng', 'Đèn tẩy trắng răng'),
            ('khoan xương', 'Máy khoan cưa xương'),
            ('oct', 'Hệ thống chụp cắt lớp võng mạc (OCT)'),
            ('xung kích', 'Máy điều trị sóng xung kích'),
            ('bàn nghiêng', 'Bàn nghiêng tập phục hồi chức năng'),
            ('thị trường', 'Máy đo thị trường kế tự động'),
            ('nhiệt ẩm kế', 'Nhiệt ẩm kế tự ghi'),
            ('nhiệt kế bấm trán', 'Nhiệt kế hồng ngoại đo trán'),
            ('nhiệt kế điện tử', 'Nhiệt kế điện tử y tế'),
            ('nhiệt kế', 'Nhiệt kế y học'),
            ('huyết áp kế', 'Huyết áp kế lò xo / Áp kế y tế'),
            ('áp kế', 'Áp kế y tế / Huyết áp kế'),
            ('x-quang', 'Máy chụp X-Quang'),
            ('c-arm', 'Hệ thống X-quang C-Arm'),
            ('thận nhân tạo', 'Máy thận nhân tạo'),
            ('khí y tế', 'Hệ thống cấp khí y tế'),
            ('lọc nước', 'Hệ thống lọc nước R.O thận nhân tạo')
        ]:
            if kw in filename_stem.lower():
                name = std_name
                break

    # Dọn dẹp tiền tố ngày / scan / hậu tố audit
    name = re.sub(r'^\d{2}[\.\/]\d{2}[\.\/]\d{2,4}\s*', '', name)
    name = re.sub(r'^\d{4}\s*Scan\s*(?:kiểm\s*định\s*)?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d{4}\.audit$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\.audit$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d{4}$', '', name) # remove trailing 0001
    name = re.sub(r'^[_\s\-\.\,\d]+', '', name)
    name = re.sub(r'[_\s\-\.\,]+$', '', name)

    # Chuẩn hóa tên viết chuẩn
    lower = name.lower()
    if 'nhiệt kế điện tử' in lower or 'nhiệt kế y học' in lower:
        name = 'Nhiệt kế điện tử y tế'
    elif 'nhiệt kế bấm trán' in lower or 'nhiệt kế hồng ngoại' in lower:
        name = 'Nhiệt kế hồng ngoại đo trán'
    elif 'nhiệt ẩm kế' in lower:
        name = 'Nhiệt ẩm kế tự ghi'
    elif 'huyết áp kế' in lower or 'áp kế lò xo' in lower or 'áp kế' in lower:
        name = 'Huyết áp kế lò xo / Áp kế y tế'
    elif 'phương tiện đo điện não' in lower or 'điện não' in lower:
        name = 'Máy đo điện não (EEG)'
    elif 'điện tim' in lower or 'ecg' in lower:
        name = 'Máy điện tim (ECG)'
    elif 'theo dõi bệnh nhân' in lower or 'monitor' in lower:
        name = 'Máy theo dõi bệnh nhân (Monitor)'
    elif 'tủ an toàn sinh học' in lower:
        name = 'Tủ an toàn sinh học'
    elif 'cân bàn' in lower or 'cân đĩa' in lower or 'cân' == lower:
        name = 'Cân sức khỏe y tế'
    elif 'máy thở' in lower:
        name = 'Máy thở chuyên dụng'
    elif 'máy ly tâm' in lower:
        name = 'Máy ly tâm phòng xét nghiệm'
    elif 'kính hiển vi' in lower:
        name = 'Kính hiển vi quang học'
    elif 'nồi hấp' in lower:
        name = 'Nồi hấp tiệt trùng'
    elif 'ống nội soi' in lower or 'ống soi' in lower:
        name = 'Ống nội soi mềm'
    elif 'ghế nha khoa' in lower or 'ghế máy nha khoa' in lower:
        name = 'Ghế máy nha khoa'
    elif 'đo loãng xương' in lower:
        name = 'Máy đo loãng xương'

    if not name or len(name) < 2:
        name = 'Thiết bị y tế'

    # Viết hoa chữ cái đầu nếu đang là chữ thường
    if name.islower():
        name = name.capitalize()

    return name.strip(), model.strip()


def run_audit_and_update():
    print("=" * 70)
    print("🏥 BẮT ĐẦU AUDIT & CHUẨN HÓA TOÀN DIỆN TÊN THIẾT BỊ Y TẾ (BV QUẬN 7)")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    devices = conn.execute("SELECT * FROM devices").fetchall()
    print(f"🔍 Đang rà soát {len(devices)} thiết bị...")

    updated_count = 0
    cur = conn.cursor()

    for d in devices:
        md_file = None
        if d['md_path']:
            md_file = MD_ROOT / d['md_path']
        elif d['source_pdf']:
            candidate_md = MD_ROOT / (Path(d['source_pdf']).stem + '.md')
            if candidate_md.exists():
                md_file = candidate_md

        stem = Path(d['source_pdf'] or d['pdf_path'] or '').stem

        new_name, new_model = extract_real_device_info(
            md_file_path=md_file,
            raw_name=d['device_name'],
            raw_model=d['model'],
            filename_stem=stem
        )

        if new_name != d['device_name'] or new_model != d['model']:
            cur.execute("""
                UPDATE devices SET
                    device_name = ?,
                    model = ?
                WHERE id = ?
            """, (new_name, new_model, d['id']))
            updated_count += 1

    conn.commit()

    # Thống kê sau khi chuẩn hóa
    new_rows = conn.execute("SELECT device_name FROM devices").fetchall()
    new_counts = {}
    for r in new_rows:
        nm = r['device_name']
        new_counts[nm] = new_counts.get(nm, 0) + 1

    conn.close()

    print("\n" + "=" * 70)
    print("✅ KẾT QUẢ AUDIT & CHUẨN HÓA:")
    print(f"  • Số lượng thiết bị đã được chuẩn hóa tên/model: {updated_count}/{len(devices)} máy")
    print(f"  • Số danh mục tên chuẩn: {len(new_counts)} nhóm danh mục")
    print("\n--- TOP 20 DANH MỤC THIẾT BỊ ĐÃ ĐƯỢC CHUẨN HÓA ĐẸP: ---")
    for name, cnt in sorted(new_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  • {name}: {cnt} máy")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_audit_and_update()
