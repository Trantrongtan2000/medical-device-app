import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

total_size = 0
total_files = 0
folder_sizes = {}

for entry in root.iterdir():
    if entry.is_dir():
        f_size = 0
        f_count = 0
        for p in entry.rglob('*'):
            if p.is_file():
                try:
                    sz = p.stat().st_size
                    f_size += sz
                    f_count += 1
                except Exception:
                    pass
        folder_sizes[entry.name] = (f_size, f_count)
        total_size += f_size
        total_files += f_count
    elif entry.is_file():
        try:
            sz = entry.stat().st_size
            total_size += sz
            total_files += 1
        except Exception:
            pass

print(f"=== THỐNG KÊ DUNG LƯỢNG THƯ MỤC 'G:\\BV QUẬN 7_OCR_WORK_20260712' ===")
print(f"Tổng dung lượng: {total_size / (1024*1024*1024):.2f} GB ({total_size / (1024*1024):.1f} MB)")
print(f"Tổng số tệp tin: {total_files:,} files")
print("\n--- Chi tiết từng thư mục con: ---")
for name, (sz, cnt) in sorted(folder_sizes.items(), key=lambda x: x[1][0], reverse=True):
    print(f"  • {name:<35}: {sz / (1024*1024):>9.2f} MB ({cnt:,} files)")

