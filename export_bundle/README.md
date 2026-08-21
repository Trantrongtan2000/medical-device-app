# 📦 GÓI TỔNG HỢP TÀI LIỆU DỮ LIỆU THIẾT BỊ & CODEBASE MARKDOWN
**Hệ Thống Quản Lý Trang Thiết Bị Y Tế - Bệnh Viện Quận 7 (HTM V3)**
*Ngày xuất: 21/08/2026 15:02:55*

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
