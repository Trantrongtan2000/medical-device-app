import os
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("📦 ĐÓNG GÓI CHUYÊN BIỆT: CHỈ LƯU CÁC FILE MARKDOWN (.MD)")
print("="*90)

# Check source folders: G:\ or Downloads backup
src_dirs = [
    Path(r"G:\BV QUẬN 7_OCR_WORK_20260712"),
    Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md")
]

src_dir = None
for d in src_dirs:
    if d.exists():
        src_dir = d
        break

if not src_dir:
    print("❌ Không tìm thấy thư mục nguồn dữ liệu!")
    sys.exit(1)

print(f"📂 Thư mục nguồn: {src_dir}")

out_zip = Path(r"C:\Users\tantt\Downloads\BV_QUAN_7_OCR_MD_ONLY.zip")
out_zip_app = Path(r"C:\Users\tantt\Downloads\medical-device-app\BV_QUAN_7_OCR_MD_ONLY.zip")

md_files = []
total_bytes = 0

print("\n🔍 Đang quét toàn bộ các tệp Markdown (.md)...")
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.lower().endswith(('.md', '.markdown')):
            fp = Path(root) / f
            try:
                sz = fp.stat().st_size
                total_bytes += sz
                md_files.append((fp, sz))
            except Exception:
                pass

print(f"✅ Tìm thấy: {len(md_files):,} tệp Markdown (.md)")
print(f"📊 Tổng dung lượng văn bản gốc: {total_bytes / (1024*1024):.2f} MB")

print(f"\n🚀 Đang nén tệp zip chỉ chứa .MD tại: {out_zip}...")
with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
    for fp, sz in md_files:
        rel_path = fp.relative_to(src_dir)
        zipf.write(fp, rel_path)

# Copy to app directory
import shutil
shutil.copy2(out_zip, out_zip_app)

zip_sz_mb = out_zip.stat().st_size / (1024*1024)
orig_sz_mb = total_bytes / (1024*1024)

print("\n" + "="*90)
print("🎉 ĐÓNG GÓI HOÀN TẤT!")
print("="*90)
print(f"📁 File ZIP đã tạo: {out_zip}")
print(f"📦 Kích thước file nén: {zip_sz_mb:.2f} MB (Gốc: {orig_sz_mb:.2f} MB - Tỷ lệ nén: {((1 - zip_sz_mb/orig_sz_mb)*100):.1f}%)")
print(f"📄 Tổng số lượng file .MD: {len(md_files):,} tệp")
