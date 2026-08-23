# Báo Cáo Nghiên Cứu & Thiết Kế Kiến Trúc DevOps Toàn Diện
## Hệ Thống Quản Lý Trang Thiết Bị Y Tế Lâm Sàng (BV Quận 7 / PKĐK Tâm Anh Q7)

---

## 1. Tổng Quan Triết Lý DevOps Y Tế (Clinical DevOps / DevSecOps)
Hệ thống quản lý trang thiết bị y tế đòi hỏi tính sẵn sàng cao (**99.9% High Availability**), tính toàn vẹn dữ liệu lâm sàng tuyệt đối (**Data Integrity**), và quy trình triển khai không gián đoạn (**Zero-Downtime Deployment**) theo chuẩn ISO 13485 và các quy định của Bộ Y Tế.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CLINICAL DEVOPS / DEVSECOPS PIPELINE                            │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┬────────────────┤
│ 1. CODE & PLAN  │ 2. CI & TEST    │ 3. SECURITY SCAN│ 4. DOCKER BUILD │ 5. GITOPS DEPLOY│
├─────────────────┼─────────────────┼─────────────────┼─────────────────┼────────────────┤
│ • Git Flow      │ • Pytest Unit   │ • Secret Scan   │ • Multi-Stage   │ • Docker Compose│
│ • GitHub SpecKit│ • API Endpoints │ • Dependency    │ • Non-Root User │ • Rolling Update│
│ • Conventional  │ • Fast Response │ • Trivy Scanner │ • Slim Image    │ • Auto Backup   │
│   Commits       │ • Code Quality  │ • OWASP Top 10  │ • Health Check  │ • Zero Downtime │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴────────────────┘
```

---

## 2. Các Thành Phần Trọng Yếu Trong Bộ Công Cụ DevOps

### 🐳 2.1. Đóng Gói Containerization (Docker Multi-Stage Build)
* **Tệp cấu hình:** `Dockerfile` & `docker-compose.yml`.
* **Multi-Stage Build:** Tách riêng môi trường `builder` (chứa gcc, build tools) và `runtime` (chỉ chứa `python:3.11-slim` và các binary cần thiết), giúp kích thước image giảm **>60%** và giảm bề mặt tấn công bảo mật.
* **Non-Root User:** Chạy ứng dụng dưới quyền người dùng `appuser:appgroup` (UID 1000) thay vì `root`.
* **Healthcheck Probe:** Tự động kiểm tra sức khỏe endpoint `/api/devices?limit=1` mỗi 30 giây.

### ⚙️ 2.2. Tự Động Hóa Tích Hợp & Kiểm Thử Liên Tục (CI/CD với GitHub Actions)
* **Tệp quy trình:** `.github/workflows/ci.yml`.
* **Quy trình kích hoạt:** Tự động chạy khi có `push` hoặc `pull request` lên nhánh `main` và các nhánh tính năng `feat/*`.
* **Các bước tự động:**
  1. *Checkout & Cài đặt môi trường Python 3.11*.
  2. *Kiểm tra chất lượng mã nguồn (Linting với Flake8)*.
  3. *Chạy toàn bộ bộ kiểm thử tự động (`pytest tests/ -v`)*.
  4. *Build và xác thực Docker container image*.

### 🛡️ 2.3. Quản Trị & Sao Lưu Dữ Liệu An Toàn (Database Disaster Recovery)
* **Tệp script:** `scripts/backup_db.py`.
* **Công nghệ:** Tận dụng tính năng `PRAGMA wal_checkpoint(TRUNCATE)` và `VACUUM INTO` của SQLite WAL mode để tạo bản sao lưu trực tiếp (Online Hot Backup) mà không cần ngắt kết nối của các khoa phòng.
* **Lịch sao lưu tự động:** Thiết lập Cron job chạy hàng ngày lúc 00:00.

### 🌐 2.4. Nginx Reverse Proxy & Tối Ưu Hóa Băng Thông
* **Tệp cấu hình:** `nginx.conf`.
* **Tính năng:**
  * Bật `gzip compression` cho JSON, CSS, JS giúp tăng tốc độ tải trang lên **3x**.
  * Hỗ trợ WebSocket Upgrade cho các kết nối thời gian thực.
  * Giới hạn `client_max_body_size 50M` cho việc tải lên hồ sơ PDF/hình ảnh kiểm định y tế.

---

## 3. Hướng Dẫn Vận Hành Triển Khai Thực Tế

### Cách 1: Chạy trực tiếp bằng Docker Compose (Khuyên dùng)
```bash
# 1. Build và khởi chạy toàn bộ hệ thống
docker-compose up -d --build

# 2. Xem log ứng dụng
docker-compose logs -f medical-device-app

# 3. Kiểm tra trạng thái sức khỏe container
docker-compose ps
```

### Cách 2: Chạy kiểm thử tự động
```bash
# Chạy bộ test tự động với pytest
pytest tests/ -v

# Chạy sao lưu CSDL thủ công
python scripts/backup_db.py
```
