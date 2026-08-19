import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

search_dirs = [
    Path(r"G:\BV QUẬN 7_OCR_WORK_20260712"),
    Path(r"G:\QLTB"),
    Path(r"C:\Users\tantt\Downloads")
]

print("🔍 TÌM KIẾM TOÀN DIỆN 'AN VIỆT' VÀ 'HERA W10' TRONG TẤT CẢ THƯ MỤC:\n" + "=" * 75)

for s_dir in search_dirs:
    if not s_dir.exists():
        continue
    safe_base = r"\\?\\" + str(s_dir.resolve())
    for root, dirs, files in os.walk(safe_base):
        for f in files:
            if f.endswith(('.md', '.txt', '.json', '.xlsx', '.docx')):
                full_p = os.path.join(root, f)
                rel_p = full_p.replace(safe_base, str(s_dir))
                if f.endswith(('.md', '.txt', '.json')):
                    try:
                        with open(full_p, 'r', encoding='utf-8', errors='ignore') as fp:
                            content = fp.read()
                            if "HERA" in content.upper() or "AN VIỆT" in content.upper() or "AN VIET" in content.upper():
                                print(f"📄 Tìm thấy trong: {rel_p}")
                                for line in content.splitlines():
                                    if any(k in line.upper() for k in ["HERA", "AN VIỆT", "AN VIET", "W10"]):
                                        print(f"   └── {line.strip()[:120]}")
                    except Exception:
                        pass
