import os
import sys
import json
import csv
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

print(f"🔍 TÌM KIẾM & ĐỌC TẤT CẢ CÁC TỆP MASTER TRONG: {root}\n")

# Find all files with 'master', 'registry', 'index', 'manifest', 'profile', 'danh_muc'
master_files = []
for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        fl = f.lower()
        if any(kw in fl for kw in ['master', 'registry', 'index', 'manifest', 'profile', 'danh_muc', 'summary']) or f.startswith('_ocr_'):
            full_p = Path(dirpath) / f
            master_files.append(full_p)

print(f"📊 Tìm thấy {len(master_files)} tệp master & chỉ mục:\n" + "=" * 70)
for idx, mf in enumerate(sorted(master_files), 1):
    rel = mf.relative_to(root)
    sz_kb = mf.stat().st_size / 1024
    print(f"{idx:02d}. [{mf.suffix.upper()}] {rel} ({sz_kb:.1f} KB)")
print("=" * 70)
