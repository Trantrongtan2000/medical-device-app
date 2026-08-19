import os
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

src_root = Path(r"G:\BV QUẬN 7")
dest_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

print(f"🔍 BẮT ĐẦU ĐỐI SOÁT & HỒI PHỤC PDF:")
print(f"  • Nguồn (Source): {src_root}")
print(f"  • Đích (Destination): {dest_root}\n")

if not src_root.exists() or not dest_root.exists():
    print("❌ Thư mục nguồn hoặc đích không tồn tại!")
    sys.exit(1)

# Scan all PDFs in source
src_pdfs = []
for dirpath, dirnames, filenames in os.walk(src_root):
    for f in filenames:
        if f.lower().endswith('.pdf'):
            src_pdfs.append(Path(dirpath) / f)

print(f"📊 Tổng số file PDF tại nguồn: {len(src_pdfs):,} files")

# Build target destination directory mapping rules
def get_dest_folder(src_path: Path) -> Path:
    rel_path = src_path.relative_to(src_root)
    parts = rel_path.parts
    top = parts[0] if parts else ""
    
    if "02_HOP DONG" in top or "Hợp đồng" in top or "HOP_DONG" in top:
        return dest_root / "02_HOP_DONG_MUA_SAM" / "HOP_DONG_GOC"
    elif "Biên bản bàn giao" in str(rel_path) or "BBBG" in str(rel_path) or "03_BAN_GIAO" in top:
        return dest_root / "03_BAN_GIAO_VA_NGHIEM_THU" / "docs_raw"
    elif "05_KIEM DINH" in top or "KIEM_DINH" in top:
        return dest_root / "04_KIEM_DINH_VA_HIEU_CHUAN" / "05_KIEM_DINH_GOC"
    elif top == "2024":
        return dest_root / "04_KIEM_DINH_VA_HIEU_CHUAN" / "2024"
    elif top == "2025":
        return dest_root / "04_KIEM_DINH_VA_HIEU_CHUAN" / "2025"
    elif top == "2026":
        return dest_root / "04_KIEM_DINH_VA_HIEU_CHUAN" / "2026"
    elif "03_BAO TRI" in top:
        return dest_root / "05_BAO_TRI_VA_SUA_CHUA" / "BAO_TRI_DINH_KY"
    elif "04_SUA CHUA" in top:
        return dest_root / "05_BAO_TRI_VA_SUA_CHUA" / "SUA_CHUA_THIET_BI"
    elif "06_THAM DINH" in top or "THAM_DINH" in top:
        return dest_root / "06_THAM_DINH_VA_PHAP_LY" / "THAM_DINH_SO_Y_TE"
    elif "kiemdinh_tachfile" in top:
        return dest_root / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP" / "kiemdinh_tachfile"
    else:
        # Keep relative subfolder structure
        if len(parts) > 1:
            return dest_root / parts[0]
        return dest_root / "03_BAN_GIAO_VA_NGHIEM_THU" / "docs_raw"

copied_count = 0
skipped_count = 0

for src_pdf in src_pdfs:
    dest_dir = get_dest_folder(src_pdf)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / src_pdf.name
    
    if not dest_file.exists():
        try:
            shutil.copy2(src_pdf, dest_file)
            copied_count += 1
            if copied_count % 100 == 0:
                print(f"  ... Đã sao chép/hồi phục {copied_count:,} files PDF")
        except Exception as e:
            print(f"  ⚠️ Lỗi copy {src_pdf.name}: {e}")
    else:
        skipped_count += 1

print("\n" + "=" * 60)
print(f"🎉 KẾT QUẢ HỒI PHỤC DỮ LIỆU PDF:")
print(f"  • Số file PDF mới được hồi phục: {copied_count:,} files")
print(f"  • Số file PDF đã tồn tại sẵn (bỏ qua): {skipped_count:,} files")
print(f"  • Tổng số PDF đã đối soát: {len(src_pdfs):,} files")
print("=" * 60)
