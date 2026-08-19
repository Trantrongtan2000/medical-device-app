import os
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

folders_to_check = {
    "G:\\BV QUẬN 7_OCR_WORK_20260712": Path(r"G:\BV QUẬN 7_OCR_WORK_20260712"),
    "G:\\BV QUẬN 7": Path(r"G:\BV QUẬN 7"),
    "C:\\Users\\tantt\\Downloads\\medical-device-app": Path(r"C:\Users\tantt\Downloads\medical-device-app"),
    "C:\\Users\\tantt\\Downloads\\asset-management-tools": Path(r"C:\Users\tantt\Downloads\asset-management-tools"),
    "G:\\BACKUP_DU_LIEU_SO_HOA_20260818": Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818")
}

print("📊 THỐNG KÊ CHI TIẾT SỐ LƯỢNG FILE MARKDOWN (.MD):\n" + "=" * 65)

for label, p in folders_to_check.items():
    if not p.exists():
        print(f"📁 {label}: [Không tồn tại]")
        continue
        
    md_files = list(p.rglob("*.md"))
    print(f"\n📁 [{label}]: Tổng cộng {len(md_files):,} files .md")
    
    # Breakdown by top subdirectories
    sub_counts = defaultdict(int)
    for f in md_files:
        try:
            rel = f.relative_to(p)
            top = rel.parts[0] if len(rel.parts) > 1 else 'ROOT'
            sub_counts[top] += 1
        except Exception:
            sub_counts['OTHER'] += 1
            
    for sub, c in sorted(sub_counts.items(), key=lambda x: x[1], reverse=True)[:6]:
        print(f"   ├─ {sub}: {c:,} files .md")

print("\n" + "=" * 65)
