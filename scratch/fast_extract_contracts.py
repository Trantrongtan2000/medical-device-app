import os
import sys
import re
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

md_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md")

print(f"⚡ BẮT ĐẦU TRÍCH XUẤT SIÊU TỐC HỢP ĐỒNG & KHOA PHÒNG:\n")

total_parsed = 0
contract_map = defaultdict(list)
dept_map = defaultdict(list)
serial_to_metadata = {}

# Fast line-by-line frontmatter parser
for dirpath, dirnames, filenames in os.walk(md_root):
    for f in filenames:
        if not f.endswith('.md'):
            continue
        fp = os.path.join(dirpath, f)
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                lines = [file.readline() for _ in range(35)]
        except Exception:
            continue
            
        if not lines or not lines[0].startswith('---'):
            continue
            
        total_parsed += 1
        meta = {}
        for l in lines[1:]:
            if l.startswith('---'):
                break
            if ':' in l:
                k, v = l.split(':', 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
                
        contract_no = meta.get('contract_no', '').strip()
        dept = meta.get('department', '').strip()
        sn = meta.get('serial_no', '').strip().upper()
        model = meta.get('model', '').strip()
        eq_name = meta.get('equipment_name', '').strip()
        handover_date = meta.get('handover_date', '').strip()
        giver = meta.get('party_giver', '').strip()
        receiver = meta.get('party_receiver', '').strip()
        
        data = {
            "file": f,
            "contract_no": contract_no,
            "department": dept,
            "serial_no": sn,
            "model": model,
            "equipment_name": eq_name,
            "handover_date": handover_date,
            "party_giver": giver,
            "party_receiver": receiver
        }
        
        if contract_no and contract_no not in ['None', 'N/A', '']:
            contract_map[contract_no].append(data)
            
        if dept and dept not in ['None', 'N/A', '']:
            dept_map[dept].append(data)
            
        if sn and sn not in ['None', 'N/A', '-', '']:
            serial_to_metadata[sn] = data

print(f"📊 Đã phân tích {total_parsed:,} file Markdown")
print(f"📊 Tìm thấy {len(contract_map):,} Hợp Đồng mua sắm duy nhất")
print(f"📊 Tìm thấy {len(dept_map):,} Tên Khoa Phòng duy nhất")
print(f"📊 Tìm thấy {len(serial_to_metadata):,} Thiết Bị có Serial định danh")

print("\n📑 TOP 15 HỢP ĐỒNG / BIÊN BẢN MUA SẮM TIÊU BIỂU:")
for c_no, items in sorted(contract_map.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    sample_eq = items[0]['equipment_name'][:30] if items[0]['equipment_name'] else items[0]['file'][:30]
    print(f"  • HĐ [{c_no}]: {len(items)} thiết bị | Khoa: {items[0]['department']} | Mẫu: {sample_eq}...")

print("\n🏥 PHÂN BỔ THIẾT BỊ THEO KHOA PHÒNG BÀN GIAO:")
for d_name, items in sorted(dept_map.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
    print(f"  • [{d_name}]: {len(items):,} thiết bị")
