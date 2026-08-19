import os
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r"G:\BV QUẬN 7")

print(f"🔍 PHÂN TÍCH THƯ MỤC G:\\BV QUẬN 7:\n")

pdf_files = []
md_files = []
other_files = []

for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        ext = os.path.splitext(f)[1].lower()
        full_path = Path(dirpath) / f
        if ext == '.pdf':
            pdf_files.append(full_path)
        elif ext == '.md':
            md_files.append(full_path)
        else:
            other_files.append(full_path)

print(f"📊 Tổng số file PDF trong 'G:\\BV QUẬN 7': {len(pdf_files):,} files")
print(f"📊 Tổng số file Markdown trong 'G:\\BV QUẬN 7': {len(md_files):,} files")
print(f"📊 Tổng số file khác trong 'G:\\BV QUẬN 7': {len(other_files):,} files")

# Sample PDF files
print("\n📄 10 FILE PDF TIÊU BIỂU TRONG G:\\BV QUẬN 7:")
for p in pdf_files[:10]:
    rel = p.relative_to(root)
    print(f"  - {rel} ({p.stat().st_size / 1024:.1f} KB)")
