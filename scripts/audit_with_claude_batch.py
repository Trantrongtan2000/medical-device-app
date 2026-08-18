"""
Script chia lô (batching) giao cho ocx claude đọc và chuẩn hóa từng file Markdown
"""
import os
import sys
import glob
import json
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

POSSIBLE_DIRS = [
    Path(r"G:\BACKUP_DU_LIEU_SO_HOA_20260818\md"),
    Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\md"),
    Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md"),
    Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\07_THU_VIEN_SO_HOA_MD")
]

MD_DIR = None
for p in POSSIBLE_DIRS:
    if p.exists():
        count = len(list(p.glob("**/*.md")))
        if count > 0:
            MD_DIR = p
            break

if not MD_DIR:
    MD_DIR = POSSIBLE_DIRS[0]


def run_claude_on_md_batch(md_files):
    """Gửi danh sách file MD cho ocx claude đọc và chuẩn hóa"""
    file_list_str = "\n".join([f"- {f.as_posix()}" for f in md_files])
    
    prompt = f"""
Bạn là Chuyên gia Kỹ sư Y sinh (BME). Hãy đọc nội dung các file Markdown số hóa thiết bị y tế sau:
{file_list_str}

Hãy trích xuất và chuẩn hóa theo JSON schema sau cho mỗi thiết bị tìm thấy:
[
  {{
    "device_name": "Tên chuẩn tiếng Việt y tế",
    "model": "Model thiết bị",
    "serial_no": "Số Serial (S/N)",
    "manufacturer": "Hãng sản xuất",
    "country_of_origin": "Nước sản xuất",
    "risk_level": "A | B | C | D (theo Nghị định 98)",
    "facility": "Khoa/Phòng phụ trách",
    "calibration_date": "YYYY-MM-DD",
    "recalibration_date": "YYYY-MM-DD",
    "certificate_no": "Số GCN kiểm định",
    "source_file": "Đường dẫn file MD"
  }}
]
Chỉ trả về chuỗi JSON thuần túy (không kèm markdown format).
"""
    
    cmd = ["ocx.cmd", "claude", "--dangerously-skip-permissions", "-p", prompt]
    try:
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
        return res.stdout
    except Exception as e:
        return str(e)

def main():
    print(f"[INFO] Quét thư mục Markdown: {MD_DIR}")
    all_mds = list(MD_DIR.glob("**/*.md"))
    print(f"[INFO] Tổng số file Markdown tìm thấy: {len(all_mds)}")
    
    # Lấy mẫu 10 file đại diện từ các nhóm thiết bị khác nhau
    sample_files = all_mds[:10]
    print(f"[INFO] Đang giao cho ocx claude đọc {len(sample_files)} file Markdown đầu tiên...")
    
    output = run_claude_on_md_batch(sample_files)
    print("=== KẾT QUẢ TRÍCH XUẤT TỪ OCX CLAUDE ===")
    print(output[:1500])
    
    # Lưu vào báo cáo
    report_file = Path("docs/STANDARDIZATION_AUDIT_REPORT.md")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO CHUẨN HÓA DỮ LIỆU THIẾT BỊ Y TẾ (OCX CLAUDE AUDIT)\n\n")
        f.write(f"- **Thư mục nguồn:** `{MD_DIR}`\n")
        f.write(f"- **Tổng số tệp MD:** {len(all_mds):,} tệp\n\n")
        f.write("## Kết quả phân tích và trích xuất mẫu từ `ocx claude`:\n\n")
        f.write("```json\n")
        f.write(output)
        f.write("\n```\n")
    print(f"[OK] Đã lưu báo cáo nghiệm thu vào: {report_file}")

if __name__ == "__main__":
    main()
