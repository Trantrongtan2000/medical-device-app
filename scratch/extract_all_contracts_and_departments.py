import os
import sys
import yaml
import re
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

md_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md")

print(f"🔍 QUÉT TOÀN BỘ {md_root} ĐỂ TRÍCH XUẤT HỢP ĐỒNG & KHOA PHÒNG:\n")

total_parsed = 0
contract_map = defaultdict(list)
dept_map = defaultdict(list)
serial_to_metadata = {}

# Regex for YAML frontmatter
yaml_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

for md_file in md_root.rglob("*.md"):
    try:
        content = md_file.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
        
    m = yaml_pattern.match(content)
    if not m:
        continue
        
    yaml_str = m.group(1)
    try:
        meta = yaml.safe_load(yaml_str)
        if not isinstance(meta, dict):
            continue
    except Exception:
        continue
        
    total_parsed += 1
    
    contract_no = str(meta.get('contract_no') or '').strip()
    dept = str(meta.get('department') or '').strip()
    sn = str(meta.get('serial_no') or '').strip().upper()
    model = str(meta.get('model') or '').strip()
    eq_name = str(meta.get('equipment_name') or '').strip()
    handover_date = str(meta.get('handover_date') or '').strip()
    giver = str(meta.get('party_giver') or '').strip()
    receiver = str(meta.get('party_receiver') or '').strip()
    
    data = {
        "file": md_file.name,
        "contract_no": contract_no,
        "department": dept,
        "serial_no": sn,
        "model": model,
        "equipment_name": eq_name,
        "handover_date": handover_date,
        "party_giver": giver,
        "party_receiver": receiver
    }
    
    if contract_no and contract_no != 'None' and contract_no != 'N/A':
        contract_map[contract_no].append(data)
        
    if dept and dept != 'None' and dept != 'N/A':
        dept_map[dept].append(data)
        
    if sn and sn != 'None' and sn != 'N/A' and sn != '-':
        serial_to_metadata[sn] = data

print(f"📊 Đã phân tích {total_parsed:,} file Markdown có YAML frontmatter")
print(f"📊 Tìm thấy {len(contract_map):,} Hợp Đồng mua sắm duy nhất")
print(f"📊 Tìm thấy {len(dept_map):,} Tên Khoa Phòng duy nhất")
print(f"📊 Tìm thấy {len(serial_to_metadata):,} Thiết Bị có Serial định danh chính xác")

print("\n📑 TOP 15 HỢP ĐỒNG / BIÊN BẢN MUA SẮM PHỔ BIẾN:")
for c_no, items in sorted(contract_map.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    sample_eq = items[0]['equipment_name'][:35] if items[0]['equipment_name'] else items[0]['file'][:35]
    print(f"  • HĐ [{c_no}]: {len(items)} thiết bị | Khoa: {items[0]['department']} | Mẫu: {sample_eq}...")

print("\n🏥 PHÂN BỔ THIẾT BỊ THEO KHOA PHÒNG TIẾP NHẬN:")
for d_name, items in sorted(dept_map.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
    print(f"  • [{d_name}]: {len(items):,} thiết bị")
