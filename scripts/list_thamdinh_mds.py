import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

thamdinh_dir = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md\06_THAM DINH")
print(f"Listing directories and markdown files in: {thamdinh_dir}")

for p in sorted(thamdinh_dir.rglob("*.md")):
    rel = p.relative_to(thamdinh_dir)
    print(f"  • {rel}")
