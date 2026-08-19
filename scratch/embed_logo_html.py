import base64
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

logo_path = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\04_KIEM_DINH_VA_HIEU_CHUAN\2024\LOGO TA5\Logo PKTA Q7.jpg")
html_path = Path(r"C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html")

if logo_path.exists() and html_path.exists():
    with open(logo_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Replace <div aria-hidden="true" class="mark">TA</div> with the official logo image
    old_mark = '<div aria-hidden="true" class="mark">TA</div>'
    new_mark = f'<img src="data:image/jpeg;base64,{b64_string}" alt="Logo PKTA Q7" style="width:36px;height:36px;object-fit:contain;border-radius:8px;background:#fff;border:1px solid var(--line);padding:2px;">'
    
    if old_mark in html_content:
        html_content = html_content.replace(old_mark, new_mark)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✅ Successfully embedded official Tâm Anh Logo into quy_trinh_ttbyt.html!")
    else:
        print("ℹ️ old_mark not found or already replaced.")
