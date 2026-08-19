import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"\\?\G:\QLTB\Downloads\ttbyt văn bản\36. TRANG THIẾT BỊ Y TẾ"
items = os.listdir(base_dir)

print("📋 CHI TIẾT 10 QUY TRÌNH & CHÍNH SÁCH QUẢN TRỊ TTBYT (TA5 / BVQ7):\n" + "=" * 75)

for idx, item in enumerate(sorted(items)[:28], 1):
    full_p = os.path.join(base_dir, item)
    if os.path.isdir(full_p):
        sub_files = os.listdir(full_p)
        print(f"\n📂 {idx:02d}. THƯ MỤC: [{item}] ({len(sub_files)} tệp con):")
        for sf in sorted(sub_files):
            print(f"      ├── 📄 {sf}")
    else:
        sz = os.path.getsize(full_p)
        print(f"📄 {idx:02d}. [FILE]: {item} ({sz/1024:.1f} KB)")
