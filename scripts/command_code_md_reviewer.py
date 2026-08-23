import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("🤖 COMMAND CODE CLI REVIEW ENGINE — FREE MODEL (poolside/laguna-s-2.1-free)")
print("="*90)

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
md_base = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md")

# Selected critical MD files representing different clinical departments and contract packages
audit_files = [
    # 1. Thẩm định 2026 Tổng quan
    md_base / r"06_THAM DINH\2026\File TBYT thẩm định cho 4 CSVC & DMKT Q7_06.02.2026\Mục lục hồ sơ TBYT thẩm định 4 CSVC & DMKT Q7_06.02.2026.md",
    # 2. Bàn giao Thận Nhân Tạo (An Pha / Fresenius)
    md_base / r"02_HOP DONG MUA SAM\Biên bản bàn giao nội bộ\Cấp cứu - Thận Nhân Tạo\2025\BBBG NB_1 máy chạy thận 4008S HD 1605-2024 HĐT TAQ7-AP CT An Phá.md",
    # 3. Bàn giao Da Liễu Laser (Việt Can / Lasera)
    md_base / r"02_HOP DONG MUA SAM\Biên bản bàn giao nội bộ\Da Liễu\2026\BBBG NB_30.03.26_1 máy điều trị da laser sóng kép_HĐVC24-143.md",
    # 4. Bàn giao CĐHA Bơm tiêm cản quang (Đường Việt)
    md_base / r"02_HOP DONG MUA SAM\Biên bản bàn giao nội bộ\Chẩn Đoán Hình Ảnh\2025\BBBG NB_1 bơm tiêm cản quang Dual Shot Alpha 7_ HD 01 2025 HĐKT VL-TA.md",
    # 5. Bàn giao Nha Khoa RHM (Medent / Deawon)
    md_base / r"02_HOP DONG MUA SAM\Biên bản bàn giao nội bộ\Tai Mũi Họng\BBBG NB_1 ghế khám TMH GI-100-1 bàn khám TMH IU 3000 HĐ 03625Q7 CT Deawon.md",
    # 6. Bàn giao Khám Sản Phụ Khoa (Francy 4)
    md_base / r"02_HOP DONG MUA SAM\Biên bản bàn giao nội bộ\Khám sản\BBBG NB_1 ghế khám sản phụ khoa Francy 4_HĐ 56 MĐ-BVTA 2025 đợt 2.md",
    # 7. Bàn giao Phục Hồi Chức Năng BTL (Goldmed)
    md_base / r"06_THAM DINH\2026\FILE SCAN_Gop\V. PHỤC HỒI CHỨC NĂNG\Bộ 01_Máy điều trị xung 2 kênh BTL-4625 Smart\HĐMB + BBBG + BBNT + Bộ chứng từ.md",
    # 8. Sổ Quản Lý TTBYT Tổng Thể BVQ7
    app_dir / r"docs\DANH_MUC_THIET_BI_Y_TE_BVQ7.md"
]

def run_command_code_audit(file_path: Path, model: str = "laguna-s-2.1-free"):
    if not file_path.exists():
        return f"⚠️ Không tìm thấy tệp: {file_path.name}"
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2500) # first 2.5KB
    except Exception as e:
        return f"Lỗi đọc file: {e}"

    prompt = f"""Bạn là Kỹ Sư Trưởng Y Sinh & Chuyên Gia Kiểm Toán Dữ Liệu Y Tế.
Hãy review và audit đoạn dữ liệu Markdown số hóa sau từ hồ sơ bệnh viện:

[TÊN TỆP]: {file_path.name}
[DỮ LIỆU MD]:
{content}

YÊU CẦU KIỂM TOÁN:
1. Xác nhận Tên thiết bị, Model, Số Serial, Hãng sản xuất, Nước xuất xứ.
2. Xác nhận Số Hợp Đồng và Nhà Cung Cấp / Nhà Thầu thực tế.
3. Đánh giá tính chính xác dữ liệu so với quy định quản lý trang thiết bị y tế (NĐ 98/2021/NĐ-CP & TT 05/2022/TT-BYT).
4. Kết luận: [HỢP LỆ / CẦN LƯU Ý / KHÔNG HỢP LỆ] và Điểm tuân thủ Compliance Score (0-100%).
Hãy trả lời cô đọng, rõ ràng, gạch đầu dòng."""

    print(f"\n🔍 Đang chạy Command Code CLI (Model: {model}) audit tệp: {file_path.name}...", flush=True)
    try:
        res = subprocess.run(
            ["cmdc.cmd", "-p", prompt, "--model", model, "--no-session", "-t"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=60,
            shell=True
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        else:
            if model != "deepseek-v4-flash":
                print("   -> Thử lại với model fallback: deepseek-v4-flash...", flush=True)
                return run_command_code_audit(file_path, model="deepseek-v4-flash")
            return f"STDERR: {res.stderr[:300]}"
    except Exception as ex:
        return f"Exception: {ex}"

report_lines = [
    "# 🏥 BÁO CÁO AUDIT DỮ LIỆU MARKDOWN BẰNG COMMAND CODE CLI (FREE MODEL)",
    f"> **Thời gian kiểm toán:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`  ",
    f"> **Công cụ AI:** Command Code CLI (`cmdc` v1.22.0) | **Model:** `poolside/laguna-s-2.1-free` (Miễn phí)  ",
    f"> **Phạm vi:** Rà soát từng tệp Markdown hồ sơ mua sắm, bàn giao, kiểm định & danh mục thiết bị gốc",
    "\n---\n"
]

for idx, f_path in enumerate(audit_files, 1):
    print(f"\n[{idx}/{len(audit_files)}] Tiến hành audit: {f_path.name}", flush=True)
    review_text = run_command_code_audit(f_path)
    
    report_lines.append(f"## {idx}. Kiểm Toán Tệp: `{f_path.name}`")
    report_lines.append(f"**Vị trí:** `{f_path}`\n")
    report_lines.append(f"### Kết Quả Review Từ Command Code CLI:")
    report_lines.append(f"{review_text}\n")
    report_lines.append("---\n")
    
    print(f"✅ Hoàn tất audit tệp {idx}!", flush=True)

# Save report
out_report = app_dir / "docs" / "COMMAND_CODE_MD_REVIEW_REPORT.md"
with open(out_report, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\n🎉 HOÀN TẤT TOÀN BỘ TIẾN TRÌNH REVIEW MD BẰNG COMMAND CODE CLI!", flush=True)
print(f"Báo cáo chi tiết đã lưu tại: {out_report}", flush=True)
