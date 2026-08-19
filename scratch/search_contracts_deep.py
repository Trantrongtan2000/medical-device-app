import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

hd_dir = r"\\?\G:\BV QUẬN 7_OCR_WORK_20260712\md\02_HOP DONG MUA SAM"

print("🔍 TÌM KIẾM TRONG THƯ MỤC HỢP ĐỒNG MUA SẮM:\n" + "=" * 75)

for root, dirs, files in os.walk(hd_dir):
    for f in files:
        if f.endswith('.md'):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fp_in:
                    txt = fp_in.read()
                    if any(k in txt.upper() for k in ["HERA", "AN VIỆT", "AN VIET", "SAMSUNG", "MEDISON"]):
                        print(f"\n📄 TỆP: {f}")
                        for line in txt.splitlines():
                            if any(k in line.upper() for k in ["HERA", "AN VIỆT", "AN VIET", "SAMSUNG", "MEDISON", "HỢP ĐỒNG", "NHÀ THẦU"]):
                                print(f"   └── {line.strip()[:120]}")
            except Exception:
                pass
