import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r'G:\BV QUẬN 7_OCR_WORK_20260712')

print("🔍 CHI TIẾT TỪNG PHÂN HỆ TRONG KHO DỮ LIỆU G:\\BV QUẬN 7_OCR_WORK_20260712:\n")

for folder_name in sorted(os.listdir(root)):
    folder_path = root / folder_name
    if not folder_path.is_dir():
        continue
        
    items = list(folder_path.iterdir())
    subdirs = [i for i in items if i.is_dir()]
    files = [i for i in items if i.is_file()]
    
    print(f"📁 [{folder_name}] (Tổng {len(items)} mục: {len(subdirs)} thư mục con, {len(files)} tệp)")
    
    # Print subdirs or sample files
    if subdirs:
        print(f"   ├─ Thư mục con tiêu biểu ({len(subdirs)}):")
        for sd in subdirs[:8]:
            sd_files = len(list(sd.glob('*')))
            print(f"   │   • {sd.name} ({sd_files} mục)")
    if files:
        print(f"   ├─ Tệp tiêu biểu ({len(files)}):")
        for fl in files[:5]:
            print(f"   │   - {fl.name} ({fl.stat().st_size/1024:.1f} KB)")
    print()
