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
wiki_dir = ocr_root / "md" / "05_KIEM DINH" / "wiki" / "ho-so-nguon"

print(f"📂 Kiểm tra thư mục: {wiki_dir}")
if wiki_dir.exists():
    wiki_files = list(wiki_dir.glob("*.md"))
    print(f"• Tìm thấy {len(wiki_files)} files Markdown.")
    for wf in wiki_files[:5]:
        print(f"\n--- FILE: {wf.name} ---")
        with open(wf, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read()[:600])

# Also check other calibration folders
print("\n=== QUÉT TẤT CẢ THƯ MỤC KIỂM ĐỊNH KHÁC ===")
for sub in (ocr_root / "md" / "05_KIEM DINH").iterdir():
    if sub.is_dir():
        cnt = sum(1 for _ in sub.rglob("*.md"))
        print(f" 📁 [md/05_KIEM DINH/{sub.name}]: {cnt} files MD")
