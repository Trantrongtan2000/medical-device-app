import os
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r"G:\BV QUẬN 7\02_HOP DONG MUA SAM")

print(f"🔍 DANH SÁCH TOÀN BỘ PHÂN HỆ HỢP ĐỒNG & BÀN GIAO THEO KHOA TRONG: {root}\n")

dept_files = defaultdict(list)
contract_patterns = re.compile(r"(\d+[\.\-_/]\d+[\.\-_/]\d+.*|\d+HĐ.*|HĐ.*|BBBG.*|Q7\d+.*|\d{6,})", re.IGNORECASE)

for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        if f.lower().endswith('.pdf'):
            rel = Path(dirpath).relative_to(root)
            parts = rel.parts
            dept_name = parts[1] if len(parts) > 1 else (parts[0] if parts else 'CHUNG')
            dept_files[dept_name].append(f)

print(f"📊 Tìm thấy {len(dept_files)} Khoa / Phòng Ban có Hồ Sơ Hợp Đồng & Bàn Giao Cụ Thể:\n" + "=" * 70)

for dept, files in sorted(dept_files.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"🏥 [{dept}] ({len(files)} hồ sơ/thiết bị):")
    for f in files[:4]:
        print(f"   • {f}")
    if len(files) > 4:
        print(f"   ... và {len(files) - 4} hồ sơ khác")
    print()
