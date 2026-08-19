import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

src_dir = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\04_KIEM_DINH_VA_HIEU_CHUAN\2024\LOGO TA5")
dest_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\img")
dest_dir.mkdir(parents=True, exist_ok=True)

logo1 = src_dir / "Logo Phòng khám đa khoa Tâm Anh.jpg"
logo2 = src_dir / "Logo PKTA Q7.jpg"

if logo1.exists():
    shutil.copy2(logo1, dest_dir / "logo_tamanh.jpg")
    print(f"✅ Copied {logo1.name} -> {dest_dir / 'logo_tamanh.jpg'}")

if logo2.exists():
    shutil.copy2(logo2, dest_dir / "logo_pkta_q7.jpg")
    print(f"✅ Copied {logo2.name} -> {dest_dir / 'logo_pkta_q7.jpg'}")
