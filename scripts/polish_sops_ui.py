import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
file_1 = app_dir / "web" / "quy_trinh_ttbyt.html"
file_2 = app_dir / "web" / "sops.html"

back_btn_side = """    <a href="/" style="display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 12px; background: #0284c7; color: #ffffff !important; border-radius: 8px; font-weight: 700; font-size: 12px; margin-bottom: 14px; text-decoration: none; box-shadow: 0 2px 6px rgba(2,132,199,0.35);">
      <span>⬅️</span> Về Hệ Thống HTM V3
    </a>"""

for p in [file_1, file_2]:
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()

        # Insert back button inside .side-top right before .brand
        if "Về Hệ Thống HTM V3" not in content:
            content = content.replace('<div class="side-top">', '<div class="side-top">\n' + back_btn_side)
        
        # Update title and branding
        content = content.replace("PKĐK Tâm Anh Quận 7", "PKĐK Tâm Anh Quận 7 — Sổ Tay Chuẩn")

        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Đã tối ưu giao diện đồng bộ cho {p.name}!")
