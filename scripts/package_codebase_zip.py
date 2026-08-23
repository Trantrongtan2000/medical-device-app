import os
import sys
import zipfile
from pathlib import Path
import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("📦 ĐÓNG GÓI CODEBASE THÀNH FILE ZIP CHO AGENT PHÂN TÍCH")
print("="*90)

root_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
output_zip_downloads = Path(r"C:\Users\tantt\Downloads\medical-device-app.zip")
output_zip_bundle = Path(r"C:\Users\tantt\Downloads\medical-device-app\medical-device-app-full-bundle.zip")

# Exclude patterns
EXCLUDE_DIRS = {
    '.git', '__pycache__', '.pytest_cache', 'node_modules',
    '.playwright-mcp', '.mypy_cache', '.venv', 'venv'
}
EXCLUDE_EXTS = {'.pyc', '.pyo', '.pyd', '.tmp'}
EXCLUDE_FILES = {'medical-device-app.zip', 'medical-device-app-full-bundle.zip'}

def make_zip(out_path: Path):
    file_count = 0
    total_uncompressed_bytes = 0
    
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in-place to avoid descending into excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.temp')]
            
            for file in files:
                if file in EXCLUDE_FILES or any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                
                file_path = Path(root) / file
                arcname = file_path.relative_to(root_dir)
                
                try:
                    zipf.write(file_path, arcname)
                    file_count += 1
                    total_uncompressed_bytes += file_path.stat().st_size
                except Exception as e:
                    print(f"⚠️ Lỗi khi nén {file_path}: {e}")

    zip_size_mb = out_path.stat().st_size / (1024 * 1024)
    uncomp_size_mb = total_uncompressed_bytes / (1024 * 1024)
    print(f"✅ Đã tạo file: {out_path}")
    print(f"   • Số lượng files: {file_count:,}")
    print(f"   • Kích thước nén: {zip_size_mb:.2f} MB (Chưa nén: {uncomp_size_mb:.2f} MB)")

print("\n1. Đang nén file tại C:\\Users\\tantt\\Downloads\\medical-device-app.zip...")
make_zip(output_zip_downloads)

print("\n2. Đang tạo bản sao tại thư mục dự án...")
import shutil
shutil.copy2(output_zip_downloads, output_zip_bundle)
print(f"✅ Đã sao chép: {output_zip_bundle}")

print("\n🎉 HOÀN TẤT ĐÓNG GÓI TOÀN BỘ CODEBASE!")
