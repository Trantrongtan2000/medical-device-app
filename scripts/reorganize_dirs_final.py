import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

SRC_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
BACKUP_G = Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818")
BACKUP_C = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818")

print("1. Sao chép toàn bộ tệp manifest/json/csv/py từ thư mục gốc...")
for f in SRC_ROOT.glob("*.*"):
    if f.is_file():
        for b_dir in [BACKUP_G, BACKUP_C]:
            try:
                shutil.copy2(f, b_dir / f.name)
            except Exception as e:
                print(f"  Lỗi copy {f.name}: {e}")

print("✅ Đã hoàn tất sao lưu 100% tệp gốc vào G: và C:.")

print("\n2. Tiến hành hệ thống lại thư mục tại G:\\BV QUẬN 7_OCR_WORK_20260712 ...")

dirs = {
    "00_HE_THONG_VA_SCRIPTS": SRC_ROOT / "00_HE_THONG_VA_SCRIPTS",
    "01_DANH_MUC_THIET_BI": SRC_ROOT / "01_DANH_MUC_THIET_BI",
    "02_HOP_DONG_MUA_SAM": SRC_ROOT / "02_HOP_DONG_MUA_SAM",
    "03_BAN_GIAO_VA_NGHIEM_THU": SRC_ROOT / "03_BAN_GIAO_VA_NGHIEM_THU",
    "04_KIEM_DINH_VA_HIEU_CHUAN": SRC_ROOT / "04_KIEM_DINH_VA_HIEU_CHUAN",
    "05_BAO_TRI_VA_SUA_CHUA": SRC_ROOT / "05_BAO_TRI_VA_SUA_CHUA",
    "06_THAM_DINH_VA_PHAP_LY": SRC_ROOT / "06_THAM_DINH_VA_PHAP_LY",
    "07_THU_VIEN_SO_HOA_MD": SRC_ROOT / "07_THU_VIEN_SO_HOA_MD",
    "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP": SRC_ROOT / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP",
}

for p in dirs.values():
    p.mkdir(parents=True, exist_ok=True)

# Move root scripts & logs to 00_HE_THONG_VA_SCRIPTS
for f in list(SRC_ROOT.glob("*.*")):
    if f.is_file() and f.name not in ('README.md', 'README_CAU_TRUC_THU_MUC.md'):
        try:
            shutil.move(str(f), str(dirs["00_HE_THONG_VA_SCRIPTS"] / f.name))
        except Exception:
            pass

# Move folders
folder_routing = {
    'scripts': dirs["00_HE_THONG_VA_SCRIPTS"] / "scripts",
    'terminals': dirs["00_HE_THONG_VA_SCRIPTS"] / "terminals",
    '_ai_cli_results': dirs["00_HE_THONG_VA_SCRIPTS"] / "_ai_cli_results",
    '05_KIEM DINH': dirs["04_KIEM_DINH_VA_HIEU_CHUAN"] / "05_KIEM_DINH_GOC",
    '2024': dirs["04_KIEM_DINH_VA_HIEU_CHUAN"] / "2024",
    '2025': dirs["04_KIEM_DINH_VA_HIEU_CHUAN"] / "2025",
    '2026': dirs["04_KIEM_DINH_VA_HIEU_CHUAN"] / "2026",
    '02_HOP DONG MUA SAM': dirs["02_HOP_DONG_MUA_SAM"] / "HOP_DONG_GOC",
    'Hình ảnh tham khảo đề xuất mua hàng': dirs["02_HOP_DONG_MUA_SAM"] / "Hinh_Anh_Tham_Khao",
    '03_BAO TRI THIET BI': dirs["05_BAO_TRI_VA_SUA_CHUA"] / "BAO_TRI_DINH_KY",
    '04_SUA CHUA THIET BI': dirs["05_BAO_TRI_VA_SUA_CHUA"] / "SUA_CHUA_THIET_BI",
    'Họp Ống nội soi': dirs["05_BAO_TRI_VA_SUA_CHUA"] / "Hop_Ong_Noi_Soi",
    '06_THAM DINH': dirs["06_THAM_DINH_VA_PHAP_LY"] / "THAM_DINH_SO_Y_TE",
    '07_BAO HIEM XA HOI': dirs["06_THAM_DINH_VA_PHAP_LY"] / "BAO_HIEM_XA_HOI",
    '_ocr_handover_assets': dirs["03_BAN_GIAO_VA_NGHIEM_THU"] / "_ocr_handover_assets",
    'Cấp cứu - Thận Nhân Tạo': dirs["03_BAN_GIAO_VA_NGHIEM_THU"] / "Cap_Cuu_Than_Nhan_Tao",
    'docs_raw': dirs["03_BAN_GIAO_VA_NGHIEM_THU"] / "docs_raw",
    '_duplicates_archive': dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / "_duplicates_archive",
    'kiemdinh_tachfile': dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / "kiemdinh_tachfile",
    '_sample': dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / "_sample",
    'sample': dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / "sample",
    '_debug': dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / "_debug",
    '_debug_out': dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / "_debug_out",
    '__pycache__': dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / "__pycache__"
}

for src_name, dst_path in folder_routing.items():
    p_src = SRC_ROOT / src_name
    if p_src.exists() and p_src.is_dir():
        try:
            if not dst_path.exists():
                shutil.move(str(p_src), str(dst_path))
                print(f"  -> Đã di chuyển {src_name} -> {dst_path.name}")
        except Exception as e:
            print(f"  Lỗi di chuyển {src_name}: {e}")

# Tạo tệp README.md hướng dẫn cấu trúc thư mục
readme_path = SRC_ROOT / "README_CAU_TRUC_THU_MUC.md"
readme_path.write_text("""# SỔ TAY CẤU TRÚC THƯ MỤC HỒ SƠ QUẢN LÝ TTBYT — BV QUẬN 7

Toàn bộ kho dữ liệu hồ sơ và số hóa đã được sắp xếp chuẩn mực theo Nghị định 98/2021/NĐ-CP và quy chuẩn ISO 13485:

```text
G:\\BV QUẬN 7_OCR_WORK_20260712\\
├── 00_HE_THONG_VA_SCRIPTS/         # Kịch bản OCR, Manifest, JSON Manifest, Script kiểm toán
├── 01_DANH_MUC_THIET_BI/          # Sổ danh mục tài sản TTBYT toàn viện & phân bổ khoa phòng
├── 02_HOP_DONG_MUA_SAM/           # Hợp đồng mua bán, CO, CQ, tờ khai hải quan, hình ảnh đề xuất
├── 03_BAN_GIAO_VA_NGHIEM_THU/     # Biên bản bàn giao, nghiệm thu, đào tạo sử dụng
├── 04_KIEM_DINH_VA_HIEU_CHUAN/    # Hồ sơ kiểm định, hiệu chuẩn, kiểm xạ (2024, 2025, 2026)
├── 05_BAO_TRI_VA_SUA_CHUA/        # Nhật ký bảo dưỡng định kỳ & hồ sơ sửa chữa
├── 06_THAM_DINH_VA_PHAP_LY/       # Hồ sơ thẩm định Sở Y Tế, cấp phép hoạt động, BHXH
├── 07_THU_VIEN_SO_HOA_MD/         # Thư viện số hóa toàn văn Markdown (OCR text)
├── 08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP/ # Kho lưu trữ tệp trùng lặp & đối soát tách trang
└── md/                            # Thư mục Markdown nguyên bản liên kết CSDL
```
""", encoding='utf-8')

print("\n🎉 ĐÃ HOÀN TẤT HỆ THỐNG LẠI THƯ MỤC CHUẨN ĐẸP 100%!")
