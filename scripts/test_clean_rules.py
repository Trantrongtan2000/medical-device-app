import sqlite3
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute("SELECT * FROM devices").fetchall()

print(f"Analyzing {len(rows)} devices for name & model cleaning...")

def clean_device_record(row):
    raw_name = row['device_name'] or ''
    raw_model = row['model'] or ''
    source_pdf = row['source_pdf'] or ''
    pdf_path = row['pdf_path'] or ''
    
    clean_name = raw_name
    clean_model = raw_model
    
    # 1. Clean OCR model mistaken as device model
    if 'mistral-ocr' in clean_model.lower():
        clean_model = 'N/A'
        
    # 2. Clean numeric or generic names from PDF/path
    filename_to_check = Path(source_pdf or pdf_path).stem
    
    # Pattern: "25_Máy ly tâm_240425_BCE" -> "Máy ly tâm"
    m_prefix_num = re.match(r'^\d{1,3}[_\s-]+([A-Za-zÀ-ỹ\s\(\)]+?)(?:[_\s-]\d+|[_\s-][A-Z]+|$)', filename_to_check)
    if (clean_name.isdigit() or len(clean_name) <= 3 or clean_name in ['Thiết bị y tế', 'N/A', 'BBBG', 'BBNT']) and m_prefix_num:
        extracted = m_prefix_num.group(1).strip()
        if len(extracted) > 3 and not extracted.isdigit():
            clean_name = extracted

    # Pattern: "BBBG_..._1 máy chẩn đoán xơ vữa mạch máu BP-203RPE III SN 03000417"
    if clean_name in ['Thiết bị y tế', 'N/A', 'BBBG', 'BBNT', 'Giấy kiểm định'] or len(clean_name) <= 3:
        # Search for device keywords in filename
        for kw in [
            'máy chẩn đoán xơ vữa mạch máu', 'máy rửa bô', 'nồi hấp', 'máy cạo vôi răng',
            'máy đo đa ký hô hấp', 'máy ghế nha khoa', 'máy đo loãng xương', 'ống nội soi',
            'máy siêu âm', 'máy điện tim', 'máy theo dõi bệnh nhân', 'bơm tiêm điện',
            'máy thở', 'dao mổ điện', 'máy phá rung tim', 'máy ly tâm', 'kính hiển vi',
            'tủ an toàn sinh học', 'tủ mát bảo quản', 'đèn tẩy trắng', 'máy khoan xương',
            'máy oct', 'máy xung kích', 'bàn nghiêng', 'máy đo thị trường', 'nhiệt ẩm kế',
            'nhiệt kế', 'huyết áp kế', 'áp kế'
        ]:
            if kw in filename_to_check.lower():
                clean_name = kw.title()
                break

    # 3. Clean date prefixes: "08.09.24 nhiệt kế điện tử0001" -> "Nhiệt kế điện tử"
    clean_name = re.sub(r'^\d{2}[\.\/]\d{2}[\.\/]\d{2,4}\s*', '', clean_name)
    clean_name = re.sub(r'^\d{4}\s*Scan\s*(?:kiểm\s*định\s*)?', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\d{4}\.audit$', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\.audit$', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\d{4}$', '', clean_name) # Remove trailing 0001
    clean_name = re.sub(r'^[_\s\-\.]+', '', clean_name)
    clean_name = re.sub(r'[_\s\-\.]+$', '', clean_name)

    # 4. Standardize common equipment names
    lower = clean_name.lower()
    if 'nhiệt kế điện tử' in lower or 'nhiệt kế y học' in lower:
        clean_name = 'Nhiệt kế điện tử y tế'
    elif 'nhiệt kế bấm trán' in lower or 'nhiệt kế hồng ngoại' in lower:
        clean_name = 'Nhiệt kế hồng ngoại đo trán'
    elif 'nhiệt ẩm kế' in lower:
        clean_name = 'Nhiệt ẩm kế tự ghi'
    elif 'huyết áp kế' in lower or 'áp kế lò xo' in lower or 'áp kế' in lower:
        clean_name = 'Huyết áp kế lò xo / Áp kế y tế'
    elif 'phương tiện đo điện não' in lower or 'điện não' in lower:
        clean_name = 'Máy đo điện não (EEG)'
    elif 'điện tim' in lower or 'ecg' in lower:
        clean_name = 'Máy điện tim (ECG)'
    elif 'theo dõi bệnh nhân' in lower or 'monitor' in lower:
        clean_name = 'Máy theo dõi bệnh nhân (Monitor)'
    elif 'tủ an toàn sinh học' in lower:
        clean_name = 'Tủ an toàn sinh học'
    elif 'cân bàn' in lower or 'cân đĩa' in lower:
        clean_name = 'Cân y tế'
    elif 'máy thở' in lower:
        clean_name = 'Máy thở'
    elif 'máy ly tâm' in lower:
        clean_name = 'Máy ly tâm'
    elif 'kính hiển vi' in lower:
        clean_name = 'Kính hiển vi quang học'
    elif 'nồi hấp' in lower:
        clean_name = 'Nồi hấp tiệt trùng'
    elif 'ống nội soi' in lower or 'ống soi' in lower:
        clean_name = 'Ống nội soi mềm'
    elif 'ghế nha khoa' in lower:
        clean_name = 'Ghế máy nha khoa'
    elif 'đo loãng xương' in lower:
        clean_name = 'Máy đo loãng xương'

    # Title casing if plain lowercase
    if clean_name.islower():
        clean_name = clean_name.capitalize()
        
    return clean_name.strip(), clean_model.strip()

changed = 0
for r in rows[:30]:
    c_name, c_model = clean_device_record(r)
    if c_name != r['device_name'] or c_model != r['model']:
        changed += 1
        print(f"[{r['id']}] '{r['device_name']}' -> '{c_name}' | Model: '{r['model']}' -> '{c_model}'")

print(f"\nSample check finished. Ready to batch update.")
conn.close()
