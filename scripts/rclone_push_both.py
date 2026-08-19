import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("☁️ RCLONE PUSH: ĐỒNG BỘ 2 THƯ MỤC DỰ ÁN LÊN GOOGLE DRIVE (gdrive:QLTB/)")
print("="*90)

rclone_exe = Path(r"C:\Users\tantt\Downloads\rclone-v1.75.0-windows-amd64\rclone-v1.75.0-windows-amd64\rclone.exe")
if not rclone_exe.exists():
    print(f"❌ Không tìm thấy rclone.exe tại: {rclone_exe}")
    sys.exit(1)

# 1. PUSH medical-device-app (Codebase & App Data)
print("\n" + "="*50)
print("🚀 [1/2] Đang đồng bộ thư mục: C:\\Users\\tantt\\Downloads\\medical-device-app")
print("="*50)
cmd1 = [
    str(rclone_exe), "copy",
    r"C:\Users\tantt\Downloads\medical-device-app",
    "gdrive:QLTB/medical-device-app",
    "--exclude", ".git/**",
    "--exclude", "node_modules/**",
    "--exclude", "__pycache__/**",
    "--exclude", "*.zip",
    "--progress", "--stats", "5s"
]
print("Running command:", " ".join(cmd1))
subprocess.run(cmd1, check=True)
print("✅ [1/2] Hoàn tất đồng bộ medical-device-app lên gdrive:QLTB/medical-device-app!")

# 2. PUSH G:\BV QUẬN 7_OCR_WORK_20260712 (Chỉ file văn bản/MD/Data, loại trừ PDF/Video)
print("\n" + "="*50)
print("🚀 [2/2] Đang đồng bộ thư mục: G:\\BV QUẬN 7_OCR_WORK_20260712 (MD, JSON, XLSX, DOCX, TXT)")
print("="*50)
cmd2 = [
    str(rclone_exe), "copy",
    r"G:\BV QUẬN 7_OCR_WORK_20260712",
    "gdrive:QLTB/BV_QUAN_7_OCR_WORK_20260712",
    "--include", "*.md",
    "--include", "*.markdown",
    "--include", "*.json",
    "--include", "*.xlsx",
    "--include", "*.xlsm",
    "--include", "*.docx",
    "--include", "*.csv",
    "--include", "*.txt",
    "--progress", "--stats", "5s"
]
print("Running command:", " ".join(cmd2))
subprocess.run(cmd2, check=True)
print("✅ [2/2] Hoàn tất đồng bộ G:\\BV QUẬN 7_OCR_WORK_20260712 lên gdrive:QLTB/BV_QUAN_7_OCR_WORK_20260712!")

print("\n" + "="*90)
print("🎉 TOÀN BỘ 2 THƯ MỤC ĐÃ ĐƯỢC PUSH LÊN RCLONE GOOGLE DRIVE THÀNH CÔNG!")
print("="*90)
