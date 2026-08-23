import re
import sys
import sqlite3
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

backup_md_dir = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md")
print(f"Scanning Markdown files in: {backup_md_dir}")

# Map of extracted equipment and supplier mappings from MD files
extracted_records = []

# Pattern to search for suppliers, contracts, models, serial numbers in Markdown tables and text
supplier_patterns = [
    r'(?:Công ty|CÔNG TY|Cty|CTY)\s+(?:TNHH|CỔ PHẦN|CP|TNHH MTV)\s+([A-ZÀ-Ỹ0-9\s\.\-_]+?)(?=\n|,|\.|\)|\||\t)',
    r'BÊN B[\s\S]*?(?:Công ty|Cty)\s+([^\n\r]+)',
    r'Đơn vị cung cấp[\s\:]+([^\n\r\|]+)',
    r'Nhà thầu[\s\:]+([^\n\r\|]+)',
    r'Hãng sản xuất[\s\:]+([^\n\r\|]+)',
    r'Hợp đồng số[\s\:]+([^\n\r\|]+)'
]

md_files = list(backup_md_dir.rglob("*.md"))
print(f"Found {len(md_files)} markdown files.")

# Let's inspect known contract directories
contracts_found = defaultdict(list)

for md_path in md_files:
    # Look at folder path names for clues
    folder_str = str(md_path)
    
    # Read content
    try:
        with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(5000) # first 5KB
    except Exception:
        continue
    
    # Search for contract numbers
    contract_matches = re.findall(r'(?:HĐ|HĐMB|HĐT|Số\s*HĐ|Hợp\s*đồng\s*số)[\s\:\/]*([0-9A-Z\.\-\_\/]{3,35})', content, re.IGNORECASE)
    
    # Search for suppliers
    supplier_matches = re.findall(r'(?:Công\s*ty\s*(?:TNHH|Cổ\s*Phần|CP|TNHH\s*MTV)|Cty)\s+([A-ZÀ-Ỹ0-9\s\.\-_]{3,50})', content, re.IGNORECASE)
    
    if contract_matches or supplier_matches:
        contracts_found[md_path.parent.name].append({
            "file": md_path.name,
            "contracts": contract_matches[:2],
            "suppliers": supplier_matches[:2]
        })

print(f"\nExtracted data from {len(contracts_found)} folders.")

# Sample top folders with contracts and suppliers
for folder, items in list(contracts_found.items())[:20]:
    print(f"\n📁 Thư mục: {folder} ({len(items)} files)")
    for it in items[:3]:
        print(f"   📄 {it['file']}: HĐ={it['contracts']} | NCC={it['suppliers']}")
