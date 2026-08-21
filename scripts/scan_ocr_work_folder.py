import sys
import io
import os
from pathlib import Path
from collections import Counter

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

ocr_dir = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

print("="*90)
print(f"📂 QUÉT THƯ MỤC: {ocr_dir}")
print("="*90)

files_by_ext = Counter()
total_size = 0
all_files = []

for root, dirs, files in os.walk(ocr_dir):
    for f in files:
        fp = Path(root) / f
        try:
            sz = fp.stat().st_size
            ext = fp.suffix.lower()
            files_by_ext[ext] += 1
            total_size += sz
            all_files.append((fp, sz, ext))
        except Exception:
            pass

print(f"Tổng số tệp: {len(all_files):,} | Tổng dung lượng: {total_size / (1024*1024):.2f} MB\n")
print("Phân bố định dạng tệp:")
for ext, count in files_by_ext.most_common():
    print(f" - [{ext or 'NO_EXT':10s}]: {count:4d} files")

print("\nCấu trúc các thư mục con chính:")
subdirs = [d for d in ocr_dir.iterdir() if d.is_dir()]
for d in subdirs[:20]:
    cnt = sum(1 for _ in d.rglob('*') if _.is_file())
    print(f" 📁 [{d.name:45s}] : {cnt:4d} files")

print("\nDanh sách 25 file mẫu tiêu biểu:")
for fp, sz, ext in all_files[:25]:
    rel = fp.relative_to(ocr_dir)
    print(f" • {str(rel):75s} ({sz/1024:.1f} KB)")
