import os
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

src_root = Path(r"G:\BV QUẬN 7")
dest_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

# Long path copy with Windows extended path prefix \\?\
fixed_count = 0
for dirpath, dirnames, filenames in os.walk(src_root):
    for f in filenames:
        if f.lower().endswith('.pdf'):
            src_f = Path(dirpath) / f
            dest_dir = dest_root / "03_BAN_GIAO_VA_NGHIEM_THU" / "docs_raw"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_f = dest_dir / f
            
            if not dest_f.exists():
                try:
                    src_long = "\\\\?\\" + str(src_f.resolve())
                    dest_long = "\\\\?\\" + str(dest_f.resolve())
                    shutil.copy2(src_long, dest_long)
                    fixed_count += 1
                    print(f"✅ Hồi phục file tên dài: {f[:60]}...")
                except Exception as e:
                    print(f"⚠️ Không thể copy: {f[:40]} -> {e}")

print(f"\n🎉 Đã hồi phục thêm {fixed_count} file PDF tên dài còn lại!")
