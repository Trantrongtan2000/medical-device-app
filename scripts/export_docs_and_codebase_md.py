"""
Script đóng gói toàn bộ tài liệu Markdown tổng hợp dữ liệu thiết bị
và chuyển đổi toàn bộ Codebase dự án thành định dạng Markdown (.md)
sau đó nén tất cả vào 1 file ZIP duy nhất.
"""
import os
import sys
import io
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# UTF-8 handling for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent
BUNDLE_DIR = ROOT_DIR / "export_bundle"
ZIP_OUTPUT_NAME = "medical_device_docs_and_codebase_md.zip"
ZIP_OUTPUT_PATH = ROOT_DIR / ZIP_OUTPUT_NAME
DOWNLOADS_ZIP_PATH = Path(os.path.expanduser("~")) / "Downloads" / ZIP_OUTPUT_NAME

def get_file_content(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[Lỗi đọc file: {e}]"

def file_to_markdown_section(file_path: Path, rel_to: Path) -> str:
    rel_path = file_path.relative_to(rel_to).as_posix()
    ext = file_path.suffix.lstrip(".").lower()
    
    lang_map = {
        "py": "python",
        "js": "javascript",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "json": "json",
        "yml": "yaml",
        "yaml": "yaml",
        "sh": "bash",
        "ps1": "powershell",
        "txt": "text",
        "md": "markdown"
    }
    lang = lang_map.get(ext, "")
    
    content = get_file_content(file_path)
    size_bytes = file_path.stat().st_size
    lines_count = len(content.splitlines())
    
    return (
        f"\n\n---\n\n"
        f"## 📄 File: `{rel_path}`\n"
        f"- **Dung lượng:** {size_bytes:,} bytes | **Số dòng:** {lines_count:,} dòng\n"
        f"- **Đường dẫn:** `{file_path}`\n\n"
        f"```{lang}\n"
        f"{content}\n"
        f"```\n"
    )

def main():
    print(f"🚀 Bắt đầu quá trình đóng gói và xuất tài liệu Markdown...")
    
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    
    docs_target_dir = BUNDLE_DIR / "device_data_docs"
    codebase_target_dir = BUNDLE_DIR / "codebase_md"
    consolidated_dir = BUNDLE_DIR / "consolidated_md"
    
    docs_target_dir.mkdir(parents=True, exist_ok=True)
    codebase_target_dir.mkdir(parents=True, exist_ok=True)
    consolidated_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== 1. GOM CÁC FILE MD TỔNG HỢP DỮ LIỆU THIẾT BỊ ====================
    print("📁 1. Gom các file MD tổng hợp dữ liệu thiết bị...")
    collected_md_files = []
    
    search_dirs = [
        ROOT_DIR / "docs",
        ROOT_DIR / "extracted_context",
        ROOT_DIR / ".agent"
    ]
    
    for sdir in search_dirs:
        if sdir.exists():
            for md_file in sdir.rglob("*.md"):
                # Bỏ qua các file transcript quá lớn (> 3MB) nếu có để tránh phình zip
                if md_file.stat().st_size > 4 * 1024 * 1024 and "transcript" in md_file.name.lower():
                    continue
                rel_name = f"{sdir.name}_{md_file.name}"
                target_file = docs_target_dir / rel_name
                shutil.copy2(md_file, target_file)
                collected_md_files.append((md_file, target_file))
                
    # Copy root README và AGENTS nếu có
    for root_md in [ROOT_DIR / "README.md", ROOT_DIR / "AGENTS.md"]:
        if root_md.exists():
            shutil.copy2(root_md, docs_target_dir / f"root_{root_md.name}")
            
    print(f"   ✓ Đã gom {len(collected_md_files)} file Markdown tổng hợp dữ liệu.")
    
    # ==================== 2. CHUYỂN ĐỔI CODEBASE THÀNH ĐỊNH DẠNG MD ====================
    print("💻 2. Chuyển đổi Codebase dự án sang định dạng Markdown...")
    
    # 2.1 Backend App
    app_files = sorted([f for f in (ROOT_DIR / "app").rglob("*.py") if "__pycache__" not in str(f)])
    app_md_content = [
        "# 🐍 CODEBASE BACKEND: FASTAPI APPLICATION (`app/`)\n",
        f"> **Thời điểm xuất:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"> **Tổng số modules:** {len(app_files)} files Python\n"
    ]
    for af in app_files:
        app_md_content.append(file_to_markdown_section(af, ROOT_DIR))
    
    (codebase_target_dir / "01_APP_BACKEND.md").write_text("".join(app_md_content), encoding="utf-8")
    print(f"   ✓ Đã xuất 01_APP_BACKEND.md ({len(app_files)} files)")

    # 2.2 Web Frontend
    web_files = sorted([f for f in (ROOT_DIR / "web").rglob("*") if f.is_file() and not f.name.endswith(('.png', '.jpg', '.jpeg', '.ico', '.svg', '.gif'))])
    web_md_content = [
        "# 🌐 CODEBASE FRONTEND: HTML / JS / CSS (`web/`)\n",
        f"> **Thời điểm xuất:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"> **Tổng số files:** {len(web_files)} files\n"
    ]
    for wf in web_files:
        web_md_content.append(file_to_markdown_section(wf, ROOT_DIR))
        
    (codebase_target_dir / "02_WEB_FRONTEND.md").write_text("".join(web_md_content), encoding="utf-8")
    print(f"   ✓ Đã xuất 02_WEB_FRONTEND.md ({len(web_files)} files)")

    # 2.3 Database & Tests
    db_schema = ROOT_DIR / "database" / "schema.sql"
    test_files = sorted([f for f in (ROOT_DIR / "tests").rglob("*.py") if "__pycache__" not in str(f)])
    db_test_md_content = [
        "# 🗄️ CODEBASE DATABASE SCHEMA & PYTEST TEST SUITES\n",
        f"> **Thời điểm xuất:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"> **Tổng số tests:** {len(test_files)} files test\n"
    ]
    if db_schema.exists():
        db_test_md_content.append(file_to_markdown_section(db_schema, ROOT_DIR))
    for tf in test_files:
        db_test_md_content.append(file_to_markdown_section(tf, ROOT_DIR))
        
    (codebase_target_dir / "03_DATABASE_AND_TESTS.md").write_text("".join(db_test_md_content), encoding="utf-8")
    print(f"   ✓ Đã xuất 03_DATABASE_AND_TESTS.md ({len(test_files) + 1} files)")

    # 2.4 CI/CD, Scripts & Configuration
    config_files = []
    for cf in [ROOT_DIR / "requirements.txt", ROOT_DIR / ".github" / "workflows" / "python-tests.yml"]:
        if cf.exists():
            config_files.append(cf)
    
    script_files = sorted([f for f in (ROOT_DIR / "scripts").glob("*.py") if not f.name.startswith("_")])[:15]
    config_files.extend(script_files)
    
    config_md_content = [
        "# ⚙️ CONFIGURATION, CI/CD & UTILITY SCRIPTS\n",
        f"> **Thời điểm xuất:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"> **Tổng số files:** {len(config_files)} files\n"
    ]
    for cfg in config_files:
        config_md_content.append(file_to_markdown_section(cfg, ROOT_DIR))
        
    (codebase_target_dir / "04_CONFIG_AND_SCRIPTS.md").write_text("".join(config_md_content), encoding="utf-8")
    print(f"   ✓ Đã xuất 04_CONFIG_AND_SCRIPTS.md ({len(config_files)} files)")

    # 2.5 ALL-IN-ONE Consolidated Codebase Markdown
    print("📦 3. Tạo file tổng hợp toàn bộ All-in-One Consolidated...")
    all_in_one_content = [
        "# 🏥 TOÀN BỘ CODEBASE & TÀI LIỆU HỆ THỐNG QUẢN LÝ TRANG THIẾT BỊ Y TẾ (BV QUẬN 7)\n",
        f"> **Phiên bản:** HTM Clinical Workflow V3 (SpeedMaint Cloud / Snipe-IT / Semantica)\n",
        f"> **Thời điểm đóng gói:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"> **Quy mô CSDL:** 1.211 thiết bị y tế | 21 khoa phòng lâm sàng\n\n",
        "## MỤC LỤC TỔNG QUAN\n",
        "- [1. Backend Application (app/)](#-file-appmainpy)\n",
        "- [2. Database Schema (database/schema.sql)](#-file-databaseschemasql)\n",
        "- [3. Frontend Web Interface (web/)](#-file-webindexhtml)\n",
        "- [4. Test Suite (tests/)](#-file-teststest_baseline_smokepy)\n",
        "- [5. CI/CD & Configurations](#-file-requirementstxt)\n\n"
    ]
    
    all_in_one_content.extend(app_md_content[3:])
    all_in_one_content.extend(db_test_md_content[3:])
    all_in_one_content.extend(web_md_content[3:])
    all_in_one_content.extend(config_md_content[3:])
    
    (consolidated_dir / "FULL_CODEBASE_CONSOLIDATED.md").write_text("".join(all_in_one_content), encoding="utf-8")
    print(f"   ✓ Đã tạo FULL_CODEBASE_CONSOLIDATED.md ({len(all_in_one_content):,} sections)")

    # ==================== 3. TẠO INDEX / README CHO BUNDLE ====================
    readme_bundle = f"""# 📦 GÓI TỔNG HỢP TÀI LIỆU DỮ LIỆU THIẾT BỊ & CODEBASE MARKDOWN
**Hệ Thống Quản Lý Trang Thiết Bị Y Tế - Bệnh Viện Quận 7 (HTM V3)**
*Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*

---

## 📂 CẤU TRÚC GÓI TÀI LIỆU TRONG ZIP:

### 1. `device_data_docs/` (Tài liệu tổng hợp dữ liệu thiết bị & quy chế BME)
- Danh mục chuẩn hóa 1.211 thiết bị y tế (`DANH_MUC_THIET_BI_Y_TE_BVQ7.md`).
- Báo cáo phân tích SOP quy trình quản lý trang thiết bị (`TA5_SOP_REGULATORY_WORKFLOW_ANALYSIS.md`).
- Tổng hợp kiến trúc, roadmap và đánh giá AI (`ROADMAP_TONG_HOP_4AI.md`, `CONTEXT_DIGEST_5AI.md`).
- Master data management, báo cáo rà soát trùng lặp PDF (`MASTER_DATA_MANAGEMENT.md`).
- Đặc tả Cactus Hybrid Routing & Needle Agent (`ROUTING_SPEC.md`, `ROUTING_BENCHMARK.md`).

### 2. `codebase_md/` (Toàn bộ mã nguồn dự án định dạng Markdown)
- `01_APP_BACKEND.md`: Toàn bộ source code Python FastAPI backend (`app/main.py`, `routes.py`, `needle_agent.py`, `semantica_engine.py`, `key_rotator.py`, `models.py`, `database.py`, `ai_services.py`, `routes_repairs.py`, `routes_transfers.py`, `routes_schedules.py`, v.v.).
- `02_WEB_FRONTEND.md`: Toàn bộ giao diện người dùng web (`index.html`, `app.js`, `api.js`, `semantica_explorer.js`, `styles.css`).
- `03_DATABASE_AND_TESTS.md`: Cấu trúc CSDL `schema.sql` và bộ 35 unit/integration tests (`tests/`).
- `04_CONFIG_AND_SCRIPTS.md`: `requirements.txt`, GitHub Actions CI workflow, và các script công cụ.

### 3. `consolidated_md/` (Bản hợp nhất hoàn chỉnh)
- `FULL_CODEBASE_CONSOLIDATED.md`: Một file Markdown duy nhất chứa toàn bộ source code của cả dự án kèm mục lục liên kết.

---
*Tài liệu được xuất tự động phục vụ lưu trữ, chuyển giao và nạp tri thức cho các hệ thống AI Agents.*
"""
    (BUNDLE_DIR / "README.md").write_text(readme_bundle, encoding="utf-8")

    # ==================== 4. NÉN THÀNH FILE ZIP ====================
    print(f"🗜️ 4. Nén toàn bộ bundle vào file ZIP: {ZIP_OUTPUT_NAME}...")
    with zipfile.ZipFile(ZIP_OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BUNDLE_DIR):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(BUNDLE_DIR)
                zipf.write(file_path, arcname=str(rel_path))
                
    # Copy sang Downloads nếu có thể
    try:
        shutil.copy2(ZIP_OUTPUT_PATH, DOWNLOADS_ZIP_PATH)
        print(f"   ✓ Đã sao chép file ZIP vào thư mục Downloads: {DOWNLOADS_ZIP_PATH}")
    except Exception as e:
        print(f"   ⚠️ Không thể sao chép sang Downloads: {e}")
        
    zip_size_mb = ZIP_OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"\n🎉 HOÀN TẤT!")
    print(f"📦 File ZIP: {ZIP_OUTPUT_PATH} ({zip_size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
