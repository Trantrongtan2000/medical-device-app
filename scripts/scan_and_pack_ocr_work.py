import os
import sys
import zipfile
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("📦 PHÂN TÍCH & ĐÓNG GÓI DỮ LIỆU G:\\BV QUẬN 7_OCR_WORK_20260712")
print("="*90)

src_dir = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
if not src_dir.exists():
    print(f"❌ Không tìm thấy thư mục: {src_dir}")
    sys.exit(1)

# Scan all files and extensions
ext_counts = Counter()
ext_sizes = Counter()
all_files = []

for root, dirs, files in os.walk(src_dir):
    for f in files:
        fp = Path(root) / f
        ext = fp.suffix.lower()
        try:
            sz = fp.stat().st_size
            ext_counts[ext] += 1
            ext_sizes[ext] += sz
            all_files.append((fp, ext, sz))
        except Exception as e:
            pass

print("\n📊 BẢNG THỐNG KÊ TOÀN BỘ ĐỊNH DẠNG TỆP TẠI NGUỒN G:\\:")
print(f"{'ĐỊNH DẠNG':15s} | {'SỐ LƯỢNG TỆP':15s} | {'DUNG LƯỢNG (MB)':18s}")
print("-" * 55)
total_src_size = sum(ext_sizes.values())
for ext, count in ext_counts.most_common():
    print(f"{ext or '(no-ext)':15s} | {count:15d} | {ext_sizes[ext]/(1024*1024):18.2f} MB")
print("-" * 55)
print(f"TỔNG CỘNG       | {len(all_files):15d} | {total_src_size/(1024*1024):18.2f} MB\n")

# Exclusion list: PDF, Videos, Audios, Heavy binaries/temp
EXCLUDED_EXTS = {
    # PDFs
    '.pdf',
    # Videos
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpeg', '.mpg',
    # Audios
    '.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma',
    # Temp / System
    '.tmp', '.crdownload', '.part', '.ds_store', '.thumbs.db'
}

# Output zip path
out_zip = Path(r"C:\Users\tantt\Downloads\BV_QUAN_7_OCR_WORK_DATA_TEXT_ONLY.zip")

print(f"🚀 Bắt đầu đóng gói loại trừ PDF, Video, Audio...")
print(f"Tệp đích: {out_zip}\n")

packed_count = 0
packed_uncompressed_bytes = 0
excluded_count = 0
excluded_bytes = 0

with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
    for fp, ext, sz in all_files:
        if ext in EXCLUDED_EXTS:
            excluded_count += 1
            excluded_bytes += sz
            continue
        
        rel_path = fp.relative_to(src_dir)
        try:
            zipf.write(fp, rel_path)
            packed_count += 1
            packed_uncompressed_bytes += sz
        except Exception as ex:
            print(f"⚠️ Lỗi nén {fp.name}: {ex}")

zip_file_size_mb = out_zip.stat().st_size / (1024 * 1024)
uncomp_size_mb = packed_uncompressed_bytes / (1024 * 1024)
excluded_size_mb = excluded_bytes / (1024 * 1024)

print("="*90)
print("🎉 KẾT QUẢ ĐÓNG GÓI THÀNH CÔNG!")
print("="*90)
print(f"📁 Tệp ZIP đã lưu tại : {out_zip}")
print(f"📦 Kích thước file nén : {zip_file_size_mb:.2f} MB (Chưa nén: {uncomp_size_mb:.2f} MB)")
print(f"📄 Số lượng tệp đóng gói : {packed_count:,} files (Gồm Markdown .md, Excel .xlsx/.xlsm, Word .docx, JSON, TXT, CSV...)")
print(f"🚫 Số lượng tệp đã loại trừ: {excluded_count:,} files (PDF/Video/Audio: {excluded_size_mb:.2f} MB)")
