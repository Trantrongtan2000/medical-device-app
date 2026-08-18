#!/usr/bin/env python3
"""
Script Nâng Cao: Chuẩn Hóa 100% Tên Thiết Bị Y Tế Từ Đường Dẫn Thư Mục & Nội Dung OCR
"""

import sqlite3
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
MD_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md")


def extract_refined_device_name(raw_name: str, raw_model: str, pdf_path_str: str, md_path_str: str):
    name = raw_name or ''
    model = raw_model or ''
    
    if 'mistral-ocr' in model.lower():
        model = 'N/A'

    full_path_str = f"{pdf_path_str} {md_path_str}"
    
    # 1. Tra cứu theo từ khóa chuyên ngành trong toàn bộ chuỗi đường dẫn (gồm cả thư mục cha)
    keyword_map = [
        ('máy đo đa ký hô hấp', 'Máy đo đa ký hô hấp'),
        ('máy chạy thận hdf online', 'Máy chạy thận HDF Online'),
        ('máy chạy thận', 'Máy thận nhân tạo'),
        ('thận nhân tạo', 'Máy thận nhân tạo'),
        ('máy chụp x-quang nha khoa', 'Máy chụp X-Quang nha khoa'),
        ('máy x-quang nha khoa', 'Máy chụp X-Quang nha khoa'),
        ('x-quang nhũ', 'Máy chụp X-Quang nhũ ảnh'),
        ('x-quang', 'Máy chụp X-Quang kỹ thuật số'),
        ('máy thở vận chuyển', 'Máy thở vận chuyển bệnh nhân'),
        ('máy thở', 'Máy thở chuyên dụng'),
        ('dao mổ điện', 'Dao mổ điện cao tần'),
        ('dao mổ', 'Dao mổ điện cao tần'),
        ('máy phá rung tim', 'Máy phá rung tim'),
        ('phá rung tim', 'Máy phá rung tim'),
        ('nồi hấp tiệt trùng', 'Nồi hấp tiệt trùng'),
        ('nồi hấp', 'Nồi hấp tiệt trùng'),
        ('máy bơm khí', 'Máy bơm khí kiểm tra rò rỉ'),
        ('chẩn đoán xơ vữa mạch máu', 'Máy chẩn đoán xơ vữa mạch máu'),
        ('máy rửa bô', 'Máy rửa bô và khử khuẩn'),
        ('máy cạo vôi răng', 'Máy cạo vôi răng siêu âm'),
        ('ghế máy nha khoa', 'Ghế máy nha khoa'),
        ('ghế nha khoa', 'Ghế máy nha khoa'),
        ('máy đo loãng xương', 'Máy đo loãng xương'),
        ('ống nội soi', 'Ống nội soi mềm'),
        ('ống soi', 'Ống nội soi mềm'),
        ('máy siêu âm', 'Máy siêu âm chẩn đoán'),
        ('mays sa', 'Máy siêu âm chẩn đoán'),
        ('máy điện tim', 'Máy điện tim (ECG)'),
        ('điện tim', 'Máy điện tim (ECG)'),
        ('ecg', 'Máy điện tim (ECG)'),
        ('máy theo dõi bệnh nhân', 'Máy theo dõi bệnh nhân (Monitor)'),
        ('monitor', 'Máy theo dõi bệnh nhân (Monitor)'),
        ('bơm tiêm điện', 'Bơm tiêm điện'),
        ('máy ly tâm', 'Máy ly tâm phòng xét nghiệm'),
        ('kính hiển vi', 'Kính hiển vi quang học'),
        ('tủ an toàn sinh học', 'Tủ an toàn sinh học'),
        ('tủ mát', 'Tủ mát bảo quản dược phẩm'),
        ('tủ lạnh', 'Tủ lạnh bảo quản mẫu y tế'),
        ('đèn tẩy trắng', 'Đèn tẩy trắng răng'),
        ('khoan xương', 'Máy khoan cưa xương'),
        ('oct', 'Hệ thống chụp cắt lớp võng mạc (OCT)'),
        ('xung kích', 'Máy điều trị sóng xung kích'),
        ('bàn nghiêng', 'Bàn nghiêng tập phục hồi chức năng'),
        ('thị trường', 'Máy đo thị trường kế tự động'),
        ('nhiệt ẩm kế', 'Nhiệt ẩm kế tự ghi'),
        ('nhiệt kế bấm trán', 'Nhiệt kế hồng ngoại đo trán'),
        ('nhiệt kế điện tử', 'Nhiệt kế điện tử y tế'),
        ('nhiệt kế y học', 'Nhiệt kế điện tử y tế'),
        ('nhiệt kế', 'Nhiệt kế y tế'),
        ('huyết áp kế', 'Huyết áp kế lò xo / Áp kế y tế'),
        ('áp kế', 'Áp kế y tế / Huyết áp kế'),
        ('cân bàn', 'Cân sức khỏe y tế'),
        ('cân đĩa', 'Cân sức khỏe y tế'),
        ('c-arm', 'Hệ thống X-quang C-Arm'),
        ('breathid', 'Máy chẩn đoán vi khuẩn HP (BreathID)'),
        ('laser', 'Máy điều trị Laser y học')
    ]

    # Kiểm tra nếu tên hiện tại còn generic / lỗi
    if name in ('Thiết bị y tế', 'N/A', 'Unknown', 'BBBG', 'BBNT', 'Giấy kiểm định') or name.isdigit() or len(name) <= 3 or 'kiểm xạ' in name.lower() or 'kiểm định' in name.lower() or 'thời gian' in name.lower():
        for kw, std_name in keyword_map:
            if kw in full_path_str.lower():
                name = std_name
                break

    # Dọn dẹp các tiền tố/hậu tố thừa
    name = re.sub(r'^\d{2}[\.\/]\d{2}[\.\/]\d{2,4}\s*', '', name)
    name = re.sub(r'^\d{4}\s*Scan\s*(?:kiểm\s*định\s*)?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d{4}\.audit$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\.audit$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d{4}$', '', name)
    name = re.sub(r'^[_\s\-\.\,\d]+', '', name)
    name = re.sub(r'[_\s\-\.\,]+$', '', name)

    # Standardize names
    lower = name.lower()
    for kw, std_name in keyword_map:
        if kw in lower:
            name = std_name
            break

    if not name or len(name) < 2 or name in ('Thiết bị y tế', 'N/A', 'Unknown', 'BBBG', 'BBNT', 'Giấy kiểm định') or 'thời gian' in name.lower():
        name = 'Thiết bị chẩn đoán & điều trị y tế'

    if name.islower():
        name = name.capitalize()

    return name.strip(), model.strip()


def run():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    devices = conn.execute("SELECT * FROM devices").fetchall()
    cur = conn.cursor()

    updated = 0
    for d in devices:
        new_name, new_model = extract_refined_device_name(
            raw_name=d['device_name'],
            raw_model=d['model'],
            pdf_path_str=d['pdf_path'] or d['source_pdf'] or '',
            md_path_str=d['md_path'] or ''
        )

        if new_name != d['device_name'] or new_model != d['model']:
            cur.execute("UPDATE devices SET device_name = ?, model = ? WHERE id = ?", (new_name, new_model, d['id']))
            updated += 1

    conn.commit()

    # Thống kê kết quả
    counts = {}
    for r in conn.execute("SELECT device_name FROM devices").fetchall():
        nm = r['device_name']
        counts[nm] = counts.get(nm, 0) + 1

    conn.close()

    print(f"✅ Hoàn tất chuẩn hóa: {updated}/{len(devices)} thiết bị.")
    print(f"📊 Tổng số nhóm danh mục chuẩn: {len(counts)}")
    print("\n--- TOP 25 DANH MỤC THIẾT BỊ SAU KHI CHUẨN HÓA TOÀN DIỆN: ---")
    for name, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:25]:
        print(f"  • {name}: {cnt} máy")


if __name__ == "__main__":
    run()
