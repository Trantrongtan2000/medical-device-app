import os
import re
import sys
import json
import sqlite3
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("🔍 BÓC TÁCH CHÍNH XÁC NHÀ CUNG CẤP & HỢP ĐỒNG TỪ KHO TỆP MARKDOWN GỐC")
print("="*90)

md_dir = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md")

# Store extracted contracts: contract_no -> {name, supplier, devices, source_files}
extracted_contracts = defaultdict(lambda: {
    "contract_no": "",
    "contract_name": "",
    "supplier_name": "",
    "devices": [],
    "source_files": []
})

# Let's scan all markdown files in 02_HOP DONG MUA SAM and 06_THAM DINH
contract_dirs = [
    md_dir / "02_HOP DONG MUA SAM",
    md_dir / "06_THAM DINH",
    md_dir / "Cấp cứu - Thận Nhân Tạo",
    md_dir / "Họp Ống nội soi"
]

all_md_files = []
for c_dir in contract_dirs:
    if c_dir.exists():
        all_md_files.extend(list(c_dir.rglob("*.md")))

print(f"Tổng số tệp Markdown Hợp đồng / Bàn giao / Thẩm định cần đọc: {len(all_md_files)}")

# Regex patterns for contract number, supplier name, buyer, equipment table
contract_patterns = [
    r'(?:HỢP ĐỒNG|Hợp đồng|HĐMB|HĐT|Số\s*HĐ|Số:\s*|HĐ\s*số)[\s\:\/]*([0-9A-Z\.\-\_\/]{4,40})',
    r'([0-9]{2,4}[\.\-\/][0-9]{2,4}[\.\-\/][A-Z0-9\.\-\_\/]{3,30})'
]

supplier_patterns = [
    r'(?:BÊN B|Bên B|BÊN BÁN|Bên Bán|BÊN CUNG CẤP|ĐƠN VỊ CUNG CẤP|NHÀ THẦU)[\s\S]{0,100}?(?:CÔNG TY|Công ty|Cty|CTY)\s+([A-ZÀ-Ỹ0-9\s\.\-_&]+?)(?=\n|\r|,|\.|\)|\||\t|MST|Mã số)',
    r'(?:CÔNG TY|Công ty|Cty|CTY)\s+(?:TNHH|CỔ PHẦN|CP|TNHH MTV|TNHH TM & DV|TNHH THƯƠNG MẠI)\s+([A-ZÀ-Ỹ0-9\s\.\-_&]+?)(?=\n|\r|,|\.|\)|\||\t|MST|Mã số)',
]

for p in all_md_files:
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        continue
    
    # 1. Search contract number from filename first, then content
    file_contract = None
    fn = p.stem
    
    # Check filename patterns like "..._20.052024HĐ.TAHCM-PV" or "..._HD 1605-2024..."
    fn_matches = re.findall(r'([0-9A-Z\.\-\_]{3,30}(?:HĐ|HD|PO|HĐT|HĐMB|HĐKT)[0-9A-Z\.\-\_]{0,25})', fn, re.IGNORECASE)
    if fn_matches:
        file_contract = fn_matches[0]
    
    # Search content for supplier
    supplier_found = None
    for sp in supplier_patterns:
        m = re.search(sp, text, re.IGNORECASE)
        if m:
            s_name = m.group(0).strip()
            # Clean up s_name
            s_name = re.sub(r'^(?:BÊN B|Bên B|BÊN BÁN|Bên Bán|BÊN CUNG CẤP|ĐƠN VỊ CUNG CẤP|NHÀ THẦU)[\s\:\-\_]*', '', s_name, flags=re.IGNORECASE).strip()
            if len(s_name) > 10 and "BỆNH VIỆN" not in s_name.upper() and "TÂM ANH" not in s_name.upper():
                supplier_found = s_name
                break
    
    # Extract equipment table if any
    table_matches = re.findall(r'\|([^\|\n]+)\|([^\|\n]+)\|([^\|\n]+)\|', text)
    # Check if table headers look like device list
    
    if file_contract or supplier_found:
        key = file_contract or p.parent.name
        extracted_contracts[key]["contract_no"] = file_contract or "N/A"
        if supplier_found and not extracted_contracts[key]["supplier_name"]:
            extracted_contracts[key]["supplier_name"] = supplier_found
        extracted_contracts[key]["source_files"].append(str(p.name))

print(f"\n✅ Đã bóc tách được {len(extracted_contracts)} gói thầu / hợp đồng / thư mục thực tế từ Markdown:")
for k, v in list(extracted_contracts.items())[:30]:
    print(f"  • Mã/Key: {k}")
    print(f"    - Nhà cung cấp: {v['supplier_name'] or 'N/A'}")
    print(f"    - Tệp đại diện: {v['source_files'][:2]}")
