import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"\\?\G:\QLTB\Downloads\ttbyt văn bản\36. TRANG THIẾT BỊ Y TẾ"

print("🔍 DANH SÁCH TOÀN BỘ CÁC QUY TRÌNH & BIỂU MẪU GỐC TRONG '36. TRANG THIẾT BỊ Y TẾ':\n" + "=" * 75)

items = os.listdir(base_dir)
print(f"📊 Tìm thấy {len(items)} mục trực tiếp trong thư mục gốc:\n")

for idx, item in enumerate(sorted(items), 1):
    full_p = os.path.join(base_dir, item)
    if os.path.isdir(full_p):
        sub_files = os.listdir(full_p)
        print(f"📁 {idx:02d}. [QUY TRÌNH / THƯ MỤC]: {item} ({len(sub_files)} tệp con)")
        for sf in sorted(sub_files):
            print(f"      ├── 📄 {sf}")
    else:
        sz = os.path.getsize(full_p)
        print(f"📄 {idx:02d}. [TẬP TIN]: {item} ({sz/1024:.1f} KB)")
