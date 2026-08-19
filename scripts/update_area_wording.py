import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
files = [
    app_dir / "web" / "index.html",
    app_dir / "web" / "js" / "app.js",
    app_dir / "app" / "routes.py",
    app_dir / "scripts" / "setup_q7_staff_and_oncall.py",
    app_dir / "scripts" / "integrate_oncall_system.py"
]

total_changes = 0
for fpath in files:
    if fpath.exists():
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        orig = content
        content = content.replace("ĐỊA BÀN PHỤ TRÁCH", "KHU VỰC PHỤ TRÁCH")
        content = content.replace("Địa bàn phụ trách", "Khu vực phụ trách")
        content = content.replace("Địa bàn quản lý", "Khu vực quản lý")
        content = content.replace("địa bàn phụ trách", "khu vực phụ trách")
        content = content.replace("ĐỊA BÀN QUẢN TRỊ", "KHU VỰC QUẢN TRỊ")
        
        if content != orig:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Đã cập nhật văn phong 'Khu vực phụ trách' trong `{fpath.name}`")
            total_changes += 1

print(f"Hoàn tất cập nhật {total_changes} tệp!")
