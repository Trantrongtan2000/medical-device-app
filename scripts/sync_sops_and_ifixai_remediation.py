import os
import sys
import re
import shutil
import sqlite3
import urllib.request
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("  iFixAi AUTOMATED DIAGNOSTIC & REMEDIATION SUITE")
print("  + ĐỒNG BỘ GIAO DIỆN SỔ TAY QUY TRÌNH CHUẨN (http://127.0.0.1:8000/sops)")
print("=" * 80)

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
web_dir = app_dir / "web"
source_sop = Path(r"C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html")
target_sop_1 = web_dir / "quy_trinh_ttbyt.html"
target_sop_2 = web_dir / "sops.html"

# ==================== 1. SYNC & HARMONIZE SOPS PAGE ====================
print("\n[BƯỚC 1] 📚 Đồng bộ hóa và nâng cấp giao diện Sổ tay Quy trình TTBYT...")

if source_sop.exists():
    with open(source_sop, "r", encoding="utf-8") as f:
        sop_content = f.read()

    # Enhance SOP page header with Tâm Anh Q7 HTM V3 Top Bar
    header_upgrade = """
<!-- Tâm Anh Q7 HTM V3 Global Sync Header -->
<div style="background: #090d16; color: #fff; padding: 10px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; position: sticky; top: 0; z-index: 1000; font-family: 'Segoe UI', system-ui, sans-serif;">
  <div style="display: flex; align-items: center; gap: 14px;">
    <a href="/" style="background: #0284c7; color: #fff; text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(2,132,199,0.4);">
      <span>⬅️</span> Về Hệ Thống HTM V3
    </a>
    <div style="display: flex; align-items: center; gap: 10px;">
      <span style="font-size: 1rem; font-weight: 800; letter-spacing: -0.01em; color: #f8fafc;">TÂM ANH Q7</span>
      <span style="background: #0369a1; color: #e0f2fe; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; font-family: monospace;">SỔ TAY QUY TRÌNH TTBYT CHUẨN</span>
    </div>
  </div>
  <div style="display: flex; align-items: center; gap: 12px; font-size: 0.82rem; color: #94a3b8;">
    <span>⚡ Tuân thủ <strong>CS.TTBYT.04 & QT.01 - QT.09</strong></span>
    <span style="color: #38bdf8; font-weight: 600;">Thông tư 05/2022/TT-BYT</span>
  </div>
</div>
"""

    if "Tâm Anh Q7 HTM V3 Global Sync Header" not in sop_content:
        sop_content = sop_content.replace("<body", "<body" + "\n" + header_upgrade)

    # Save to both target locations
    with open(target_sop_1, "w", encoding="utf-8") as f:
        f.write(sop_content)
    with open(target_sop_2, "w", encoding="utf-8") as f:
        f.write(sop_content)
    print(f"  ✅ Đã đồng bộ giao diện Sổ tay Quy trình vào {target_sop_1} & {target_sop_2}!")

# Update app/routes.py to use internal repo paths
routes_path = app_dir / "app" / "routes.py"
with open(routes_path, "r", encoding="utf-8") as f:
    routes_content = f.read()

routes_content = re.sub(
    r'SOP_HTML_PATH\s*=\s*Path\(.*?\)',
    'SOP_HTML_PATH = Path(__file__).parent.parent / "web" / "sops.html"\nif not SOP_HTML_PATH.exists():\n    SOP_HTML_PATH = Path(__file__).parent.parent / "web" / "quy_trinh_ttbyt.html"',
    routes_content
)

with open(routes_path, "w", encoding="utf-8") as f:
    f.write(routes_content)
print("  ✅ Đã cập nhật tuyến đường `/sops` trong `app/routes.py` trỏ vào tệp nội bộ!")

# ==================== 2. iFixAi OPERATIONAL AUDIT & REMEDIATION ====================
print("\n[BƯỚC 2] 🛡️ Chạy iFixAi Remediation & Health Checks...")

base_url = "http://127.0.0.1:8000"
test_endpoints = [
    ("/api/devices?limit=5", "Danh mục thiết bị y tế"),
    ("/api/facilities", "21 Khoa/Phòng ban lâm sàng"),
    ("/api/staff", "6 Nhân sự BME Quận 7"),
    ("/api/oncall/schedule?month=2026-08", "Lịch xếp On-Call 24/24h"),
    ("/api/maintenance/logs?limit=5", "Nhật ký bảo trì SpeedMaint CMMS"),
    ("/api/calibrations?limit=5", "Chứng chỉ kiểm định TT 05"),
    ("/api/transfers?limit=5", "Phiếu điều chuyển máy QT.08"),
    ("/api/inspections/daily", "Kiểm tra an toàn đầu ngày Pre-use"),
    ("/api/speedmaint/work-orders?limit=5", "Phiếu công việc SpeedMaint"),
    ("/api/semantica/graph", "Đồ thị tri thức Semantica Context Graph"),
    ("/api/keys/config", "Multi-Key API Pool Status"),
    ("/api/sops", "Danh mục 9 Quy trình chuẩn SOPs"),
    ("/sops", "Giao diện Sổ tay Quy trình HTML")
]

passed_tests = 0
for ep, desc in test_endpoints:
    try:
        req = urllib.request.Request(f"{base_url}{ep}")
        with urllib.request.urlopen(req, timeout=5) as res:
            if res.status == 200:
                print(f"  ✅ [HTTP 200 OK] {desc:<42} : {ep}")
                passed_tests += 1
            else:
                print(f"  ⚠️ [HTTP {res.status}] {desc:<42} : {ep}")
    except Exception as e:
        print(f"  ❌ [ERROR] {desc:<42} : {ep} -> {e}")

score = (passed_tests / len(test_endpoints)) * 100
print(f"\n🎯 Điểm kiểm định iFixAi: {score:.1f}% ({passed_tests}/{len(test_endpoints)} endpoints PASSED)")
print("=" * 80)
