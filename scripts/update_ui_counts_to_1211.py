import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")

# 1. Update web/index.html
index_path = app_dir / "web" / "index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("1.046", "1.211")
html = html.replace("1.073", "1.211")
html = html.replace("24 HĐ", "198 HĐ")
html = html.replace("24 NCC", "102 NCC")
html = html.replace("45 NCC", "102 NCC")
html = html.replace("45 Nhà Cung Cấp", "102 Nhà Cung Cấp")
html = html.replace("24 Hợp Đồng", "198 Hợp Đồng")

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

# 2. Update DESIGN.md
design_path = app_dir / "DESIGN.md"
if design_path.exists():
    with open(design_path, "r", encoding="utf-8") as f:
        design = f.read()
    design = design.replace("1.046", "1.211")
    design = design.replace("1.073", "1.211")
    with open(design_path, "w", encoding="utf-8") as f:
        f.write(design)

print("✅ Đã cập nhật chỉ số hiển thị chuẩn xác 1.211 thiết bị, 198 Hợp đồng, 102 Nhà cung cấp!")
