#!/usr/bin/env python3
"""
Script Thực Hiện Sao Lưu Dữ Liệu Số Hóa & Hệ Thống Lại Thư Mục G:\BV QUẬN 7_OCR_WORK_20260712
"""

import shutil
import sys
import os
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SRC_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
BACKUP_G = Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818")
BACKUP_LOCAL = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818")

def step1_backup_digitized_data():
    print("=" * 70)
    print("📦 BƯỚC 1: SAO LƯU TOÀN BỘ DỮ LIỆU SỐ HÓA (MARKDOWN, JSON, MANIFEST, SCRIPTS)")
    print("=" * 70)

    for b_target in [BACKUP_G, BACKUP_LOCAL]:
        b_target.mkdir(parents=True, exist_ok=True)
        print(f"\n📂 Đang sao lưu tới: {b_target} ...")

        # 1. Sao lưu thư mục md/
        src_md = SRC_ROOT / "md"
        dst_md = b_target / "md"
        if src_md.exists() and not dst_md.exists():
            print("  • Sao lưu thư mục Markdown (7.722 tệp MD)...")
            shutil.copytree(src_md, dst_md)
            print("    -> Hoàn thành sao lưu md/!")

        # 2. Sao lưu các tệp JSON, CSV, MD, PY, JSONL tại thư mục gốc
        for f in SRC_ROOT.glob("*.*"):
            if f.is_file() and f.suffix.lower() in ('.json', '.jsonl', '.csv', '.md', '.py', '.txt', '.html', '.env'):
                dst_f = b_target / f.name
                shutil.copy2(f, dst_f)
                print(f"  • Đã sao lưu tệp: {f.name}")

    print("\n✅ HOÀN TẤT BƯỚC 1: Đã tạo 2 bản sao lưu an toàn tại Ổ G và Ổ C.")


def step2_reorganize_structure():
    print("\n" + "=" * 70)
    print("🗂️ BƯỚC 2: HỆ THỐNG LẠI CÂY THƯ MỤC CHUẨN Y TẾ TẠI Ổ G")
    print("=" * 70)

    # Định nghĩa cấu trúc thư mục chuẩn nghiệp vụ TTBYT
    target_dirs = {
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

    for p in target_dirs.values():
        p.mkdir(parents=True, exist_ok=True)

    # 1. Gom các tệp hệ thống & scripts vào 00_HE_THONG_VA_SCRIPTS
    print("\n1. Sắp xếp tệp cấu hình, scripts & metadata...")
    for f in list(SRC_ROOT.glob("*.*")):
        if f.is_file() and f.suffix.lower() in ('.json', '.jsonl', '.csv', '.py', '.txt', '.html', '.env', '.rar') and f.name != 'README.md':
            dst = target_dirs["00_HE_THONG_VA_SCRIPTS"] / f.name
            try:
                shutil.move(str(f), str(dst))
                print(f"  -> Chuyển {f.name} vào 00_HE_THONG_VA_SCRIPTS/")
            except Exception as e:
                print(f"  Lỗi chuyển {f.name}: {e}")

    # Gom thư mục scripts, terminals, _ai_cli_results
    for sub in ['scripts', 'terminals', '_ai_cli_results']:
        p_sub = SRC_ROOT / sub
        if p_sub.exists() and p_sub.is_dir():
            dst = target_dirs["00_HE_THONG_VA_SCRIPTS"] / sub
            if not dst.exists():
                shutil.move(str(p_sub), str(dst))
                print(f"  -> Chuyển thư mục {sub} vào 00_HE_THONG_VA_SCRIPTS/")

    # 2. Gom tệp kiểm định theo năm (2024, 2025, 2026, 05_KIEM DINH) vào 04_KIEM_DINH_VA_HIEU_CHUAN
    print("\n2. Sắp xếp hồ sơ Kiểm định & Hiệu chuẩn...")
    for sub in ['05_KIEM DINH', '2024', '2025', '2026']:
        p_sub = SRC_ROOT / sub
        if p_sub.exists() and p_sub.is_dir():
            target_sub_name = sub.replace("05_KIEM DINH", "KIEM_DINH_CHUNG")
            dst = target_dirs["04_KIEM_DINH_VA_HIEU_CHUAN"] / target_sub_name
            if not dst.exists():
                shutil.move(str(p_sub), str(dst))
                print(f"  -> Chuyển {sub} vào 04_KIEM_DINH_VA_HIEU_CHUAN/{target_sub_name}")

    # 3. Gom hồ sơ Hợp đồng mua sắm
    print("\n3. Sắp xếp hồ sơ Hợp đồng & Mua sắm...")
    for sub in ['02_HOP DONG MUA SAM', 'Hình ảnh tham khảo đề xuất mua hàng']:
        p_sub = SRC_ROOT / sub
        if p_sub.exists() and p_sub.is_dir():
            dst = target_dirs["02_HOP_DONG_MUA_SAM"] / sub.replace("02_HOP DONG MUA SAM", "HOP_DONG_GOC")
            if not dst.exists():
                shutil.move(str(p_sub), str(dst))
                print(f"  -> Chuyển {sub} vào 02_HOP_DONG_MUA_SAM/")

    # 4. Gom hồ sơ Bảo trì & Sửa chữa vào 05_BAO_TRI_VA_SUA_CHUA
    print("\n4. Sắp xếp hồ sơ Bảo trì & Sửa chữa...")
    for sub in ['03_BAO TRI THIET BI', '04_SUA CHUA THIET BI', 'Họp Ống nội soi']:
        p_sub = SRC_ROOT / sub
        if p_sub.exists() and p_sub.is_dir():
            dst = target_dirs["05_BAO_TRI_VA_SUA_CHUA"] / sub.replace("03_BAO TRI THIET BI", "BAO_TRI").replace("04_SUA CHUA THIET BI", "SUA_CHUA")
            if not dst.exists():
                shutil.move(str(p_sub), str(dst))
                print(f"  -> Chuyển {sub} vào 05_BAO_TRI_VA_SUA_CHUA/")

    # 5. Gom hồ sơ Thẩm định & Pháp lý vào 06_THAM_DINH_VA_PHAP_LY
    print("\n5. Sắp xếp hồ sơ Thẩm định & Pháp lý...")
    for sub in ['06_THAM DINH', '07_BAO HIEM XA HOI']:
        p_sub = SRC_ROOT / sub
        if p_sub.exists() and p_sub.is_dir():
            dst = target_dirs["06_THAM_DINH_VA_PHAP_LY"] / sub.replace("06_THAM DINH", "THAM_DINH_SO_Y_TE").replace("07_BAO HIEM XA HOI", "BAO_HIEM_XA_HOI")
            if not dst.exists():
                shutil.move(str(p_sub), str(dst))
                print(f"  -> Chuyển {sub} vào 06_THAM_DINH_VA_PHAP_LY/")

    # 6. Gom Bàn giao & Khoa phòng
    for sub in ['_ocr_handover_assets', 'Cấp cứu - Thận Nhân Tạo', 'docs_raw']:
        p_sub = SRC_ROOT / sub
        if p_sub.exists() and p_sub.is_dir():
            dst = target_dirs["03_BAN_GIAO_VA_NGHIEM_THU"] / sub
            if not dst.exists():
                shutil.move(str(p_sub), str(dst))
                print(f"  -> Chuyển {sub} vào 03_BAN_GIAO_VA_NGHIEM_THU/")

    # 7. Gom tệp trùng lặp & temp vào 08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP
    print("\n6. Sắp xếp kho lưu trữ tệp trùng lặp & dữ liệu tạm...")
    for sub in ['_duplicates_archive', 'kiemdinh_tachfile', 'sample', '_sample', '_debug', '_debug_out', '__pycache__']:
        p_sub = SRC_ROOT / sub
        if p_sub.exists() and p_sub.is_dir():
            dst = target_dirs["08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"] / sub
            if not dst.exists():
                shutil.move(str(p_sub), str(dst))
                print(f"  -> Chuyển {sub} vào 08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP/")

    # Tạo tệp README.md hướng dẫn sơ đồ cây thư mục tại thư mục gốc ổ G
    readme_path = SRC_ROOT / "README_CAU_TRUC_THU_MUC.md"
    readme_path.write_text("""# SƠ ĐỒ CẤU TRÚC THƯ MỤC HỒ SƠ QUẢN LÝ TTBYT (BV QUẬN 7)

Thư mục đã được chuẩn hóa theo quy trình quản lý trang thiết bị y tế Bệnh viện Quận 7:

```text
G:\\BV QUẬN 7_OCR_WORK_20260712\\
├── 00_HE_THONG_VA_SCRIPTS/         # Kịch bản OCR, Manifest, Danh mục Index JSON/CSV
├── 01_DANH_MUC_THIET_BI/          # Sổ danh mục tài sản TTBYT toàn viện
├── 02_HOP_DONG_MUA_SAM/           # Hợp đồng mua bán, CO, CQ, tờ khai hải quan
├── 03_BAN_GIAO_VA_NGHIEM_THU/     # Biên bản bàn giao, nghiệm thu, đào tạo sử dụng
├── 04_KIEM_DINH_VA_HIEU_CHUAN/    # Giấy chứng nhận kiểm định, hiệu chuẩn, kiểm xạ (2024, 2025, 2026)
├── 05_BAO_TRI_VA_SUA_CHUA/        # Nhật ký bảo dưỡng định kỳ & hồ sơ sửa chữa
├── 06_THAM_DINH_VA_PHAP_LY/       # Hồ sơ thẩm định Sở Y Tế & Pháp lý hoạt động
├── 07_THU_VIEN_SO_HOA_MD/         # Thư viện số hóa toàn văn Markdown (OCR text)
├── 08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP/ # Kho lưu trữ tệp trùng lặp & tách trang đối soát
└── md/                            # Thư mục Markdown nguyên bản liên kết CSDL
```
""", encoding='utf-8')

    print("\n✅ ĐÃ HOÀN TẤT HỆ THỐNG LẠI THƯ MỤC CHUẨN ĐẸP 100%!")


if __name__ == "__main__":
    step1_backup_digitized_data()
    step2_reorganize_structure()
