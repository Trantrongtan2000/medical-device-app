import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

base_dir = Path(r"G:\QLTB\Downloads\ttbyt văn bản\36. TRANG THIẾT BỊ Y TẾ")

print(f"🔍 BẮT ĐẦU PHÂN TÍCH TẤT CẢ VĂN BẢN QUY TRÌNH TRONG:\n{base_dir}\n" + "=" * 75)

if not base_dir.exists():
    # Search for alternative paths
    parent_p = Path(r"G:\QLTB\Downloads")
    print(f"❌ Không tìm thấy chính xác đường dẫn! Đang quét trong {parent_p}:")
    for p in parent_p.rglob("*TRANG THIẾT BỊ*"):
        print(f"  • {p}")
    sys.exit(1)

all_files = []
for root, dirs, files in os.walk(base_dir):
    for f in files:
        fp = Path(root) / f
        all_files.append((fp, fp.relative_to(base_dir), fp.stat().st_size))

print(f"📊 Tổng số tài liệu quy trình & biểu mẫu tìm thấy: {len(all_files)} tệp\n")

# Group by category / folder
categories = {}
for full_p, rel_p, sz in all_files:
    folder = rel_p.parts[0] if len(rel_p.parts) > 1 else "GỐC"
    if folder not in categories:
        categories[folder] = []
    categories[folder].append((rel_p, sz))

for cat, flist in sorted(categories.items()):
    print(f"📁 NHÓM QUY TRÌNH: [{cat}] ({len(flist)} tệp):")
    for rel_p, sz in sorted(flist)[:15]:
        print(f"   • {rel_p.name:60s} ({sz/1024:.1f} KB)")
    if len(flist) > 15:
        print(f"   ... và {len(flist)-15} tệp khác")
    print()
