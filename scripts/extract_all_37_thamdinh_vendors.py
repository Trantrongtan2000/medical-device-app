import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("🔍 BÓC TÁCH CHI TIẾT TỪNG TỆP HỒ SƠ THẨM ĐỊNH & HỢP ĐỒNG 2025-2026")
print("="*90)

base_dir = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md\06_THAM DINH")

all_folders = [
    base_dir / r"2026\File TBYT thẩm định cho 4 CSVC & DMKT Q7_06.02.2026",
    base_dir / r"2026\FILE SCAN_Gop",
    base_dir / r"2025\Đợt  tháng 12.2024\Hồ sơ TBYT Q7 (HĐ, CO, CQ, BBBG) - đợt 3 - 20250116"
]

results = []

for folder in all_folders:
    if not folder.exists():
        continue
    for p in folder.rglob("*.md"):
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        
        # Look for Bên B / Cty / Hợp đồng
        contract_m = re.findall(r'(?:HỢP ĐỒNG|Hợp đồng|HĐMB|HĐT|HĐKT|Số\s*HĐ|Số:\s*|HĐ\s*số)[\s\:\/]*([0-9A-Z\.\-\_\/]{4,40})', content, re.IGNORECASE)
        
        supplier_m = re.findall(r'(?:BÊN B|Bên B|BÊN BÁN|Bên Bán|BÊN CUNG CẤP|ĐƠN VỊ CUNG CẤP|NHÀ THẦU)[\s\S]{0,100}?(?:CÔNG TY|Công ty|Cty|CTY)\s+([A-ZÀ-Ỹ0-9\s\.\-_&]+?)(?=\n|\r|,|\.|\)|\||\t|MST|Mã số)', content, re.IGNORECASE)
        if not supplier_m:
            supplier_m = re.findall(r'(?:CÔNG TY|Công ty|Cty|CTY)\s+(?:TNHH|CỔ PHẦN|CP|TNHH MTV|TNHH TM & DV|TNHH THƯƠNG MẠI)\s+([A-ZÀ-Ỹ0-9\s\.\-_&]+?)(?=\n|\r|,|\.|\)|\||\t|MST|Mã số)', content, re.IGNORECASE)
        
        # Filter valid suppliers
        clean_suppliers = []
        for s in supplier_m:
            s_clean = s.strip()
            if len(s_clean) > 5 and "BỆNH VIỆN" not in s_clean.upper() and "TÂM ANH" not in s_clean.upper():
                clean_suppliers.append(s_clean)
        
        if contract_m or clean_suppliers:
            results.append({
                "parent": p.parent.name,
                "file": p.name,
                "contracts": list(set(contract_m)),
                "suppliers": list(set(clean_suppliers))[:2]
            })

print(f"Tổng số tệp trích xuất có chứng từ rõ ràng: {len(results)}\n")
for r in results[:40]:
    print(f"📁 {r['parent']} / {r['file']}")
    print(f"   • HĐ: {r['contracts']}")
    print(f"   • NCC: {r['suppliers']}\n")
