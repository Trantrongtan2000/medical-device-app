import sys
import io
import os
import re
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

queries = ["02/2024", "PA-BVTA", "ZG-2C", "AM-301", "JM-105", "Đèn đọc phim", "Micare", "HEM-8712", "NC150"]

print("=== TÌM KIẾM TỆP PDF THEO TỪ KHÓA TRONG G:\\BV QUẬN 7_OCR_WORK_20260712 ===")
for q in queries:
    matches = []
    for root, dirs, files in os.walk(ocr_root):
        for f in files:
            if f.lower().endswith('.pdf'):
                full_path = os.path.join(root, f)
                if q.lower() in f.lower() or q.lower() in full_path.lower():
                    matches.append(full_path)
                    if len(matches) >= 5:
                        break
        if len(matches) >= 5:
            break
    print(f"• Từ khóa [{q:15s}]: Tìm thấy {len(matches)} files mẫu:")
    for m in matches[:3]:
        rel = os.path.relpath(m, ocr_root)
        print(f"   -> {rel}")
