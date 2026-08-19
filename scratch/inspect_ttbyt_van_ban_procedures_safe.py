import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

base_dir = Path(r"G:\QLTB\Downloads\ttbyt văn bản\36. TRANG THIẾT BỊ Y TẾ")
safe_base = r"\\?\\" + str(base_dir.resolve())

print(f"🔍 BẮT ĐẦU PHÂN TÍCH TẤT CẢ VĂN BẢN QUY TRÌNH TRONG:\n{base_dir}\n" + "=" * 75)

all_files = []
for root, dirs, files in os.walk(safe_base):
    rel_root = root.replace(safe_base, "").lstrip("\\/")
    for f in files:
        full_p = os.path.join(root, f)
        rel_p = os.path.join(rel_root, f)
        try:
            sz = os.path.getsize(full_p)
            all_files.append((rel_p, sz))
        except Exception:
            all_files.append((rel_p, 0))

print(f"📊 Tổng số tài liệu quy trình & biểu mẫu tìm thấy: {len(all_files)} tệp\n")

# Group by category / folder
categories = {}
for rel_p, sz in all_files:
    parts = rel_p.split("\\")
    folder = parts[0] if len(parts) > 1 else "GỐC"
    if folder not in categories:
        categories[folder] = []
    categories[folder].append((parts[-1], sz))

for cat, flist in sorted(categories.items()):
    print(f"📁 NHÓM QUY TRÌNH / THƯ MỤC: [{cat}] ({len(flist)} tệp):")
    for fname, sz in sorted(flist):
        print(f"   • {fname} ({sz/1024:.1f} KB)")
    print()
