# Specification: 003 - SpeedMaint CMMS, Snipe-IT, Gemini AI & Mistral OCR Integration

## 1. Overview
Phiên bản 2.0 mở rộng của Hệ thống Quản lý Trang Thiết Bị Y Tế Bệnh viện Quận 7, tích hợp kiến trúc quản lý tài sản chuẩn **Snipe-IT** và quy trình quản lý bảo trì bảo dưỡng theo chuẩn **SpeedMaint Cloud CMMS (Bệnh viện Đa Khoa Hoàn Mỹ Sài Gòn)**, kết hợp **Google Gemini Interactions AI Agent**, **Mistral OCR Engine**, và **Cơ chế Xoay Key Tự Động (Multi-Key Rotation Pool)**.

---

## 2. Core Capabilities & Specifications

### 2.1 Minimalist Clinical UI (Triết lý "Less, but better")
- Bố cục Sidebar trái cố định 240px với 5 phân hệ cốt lõi:
  1. **Thiết Bị (Assets Matrix)**: Bảng dữ liệu 6 cột thiết yếu (*Mã tài sản, Tên thiết bị, Khoa phòng, Hạn kiểm định, Trạng thái, Chi tiết*).
  2. **Kiểm Kê (Audits Center)**: Phân hệ kiểm kê hiện trường chuyên trách, ghi nhận Audit Trail theo thời gian thực.
  3. **Bảo Trì & Báo Hỏng (Work Orders)**: Phiếu công việc SpeedMaint chuẩn `#2607XX`, theo dõi tiến độ và vật tư.
  4. **In Nhãn QR (QR Studio)**: Trạm sinh tem mã QR decal dán thân máy khổ chuẩn, hỗ trợ `@media print`.
  5. **Trợ Lý AI & OCR (AI Hub)**: Trung tâm điều khiển hội thoại kỹ sư y sinh và bóc tách tài liệu thông minh.

### 2.2 Quy trình Nhập Mới Thiết Bị (TLHD_QLTTBYT Mục 2a & Mục 3 + NĐ 98/2021)
- Tự động sinh mã kép:
  - Mã định danh tài sản Snipe-IT: `BVQ7-TTB-XXXXX`
  - Mã công việc CMMS SpeedMaint: `BM/BVQ7/XXXXX`
- Tự động kiểm tra trùng số Serial trên toàn viện.
- Phân loại 4 mức rủi ro theo Cổng IMDA Bộ Y Tế: Mức A, B, C, D.
- Tự động khởi tạo chứng chỉ kiểm định ban đầu và nhật ký nghiệm thu đưa vào sử dụng (Audit Trail).

### 2.3 Cơ chế Xoay API Key Tự Động (Multi-Key Rotation Pool)
- Quản lý danh sách nhiều API Keys cho Google Gemini và Mistral OCR.
- **Thuật toán Round-Robin**: Chia tải luân chuyển giữa các key hoạt động (`🟢 ACTIVE`).
- **Auto-Failover**: Khi gặp lỗi `429 Too Many Requests`, `ResourceExhausted` hoặc hết hạn mức quota, tự động chuyển key đó sang `🟡 RATE_LIMITED` (cooldown 60s) và xoay sang key kế tiếp ngay lập tức mà không làm gián đoạn người dùng.
- Lưu trữ cấu hình bền vững vào SQLite (`api_keys_config`).

### 2.4 Trợ lý Y sinh Gemini AI (Google GenAI Interactions API)
- Phân tích và tra cứu hồ sơ 1.049 thiết bị y tế thực tế tại BV Quận 7.
- Tư vấn quy trình kiểm định, bảo trì phòng ngừa (PM) và an toàn điện y tế theo Thông tư 05/2022/TT-BYT & Nghị định 98/2021/NĐ-CP.
- Cơ chế Fallback Rule Engine thông minh khi offline hoặc chưa nhập key.

### 2.5 Mistral OCR Document Understanding Engine (Mistral-OCR-4)
- Bóc tách tự động tài liệu scan PDF / Hình ảnh Giấy chứng nhận kiểm định sang Markdown & JSON Schema y tế (`device_name`, `model`, `serial_no`, `certificate_no`, `calibration_date`, `recalibration_date`).
- Đồng bộ một chạm kết quả OCR vào cơ sở dữ liệu bệnh viện.

---

## 3. Data Schema & Models

### Devices (`devices`):
- `id` (INTEGER PK)
- `device_name` (TEXT NOT NULL)
- `model` (TEXT NOT NULL)
- `serial_no` (TEXT UNIQUE NOT NULL)
- `facility_id` (FK `facilities.id`)
- `category_id` (FK `device_categories.id`)
- `manufacturer` (TEXT)
- `country_of_manufacturer` (TEXT)
- `year_of_manufacture` (INTEGER)
- `risk_level` (TEXT CHECK in 'A', 'B', 'C', 'D')
- `status` (TEXT CHECK in 'IN_SERVICE', 'CALIBRATION_DUE', 'MAINTENANCE', 'REPAIR', 'RETIRED')
- `calibration_date` (DATE)
- `recalibration_date` (DATE)
- `notes` (TEXT)

### API Keys Configuration (`api_keys_config`):
- `id` (INTEGER PK)
- `service_name` (TEXT NOT NULL - 'gemini' | 'mistral')
- `api_key` (TEXT UNIQUE NOT NULL)
- `status` (TEXT DEFAULT 'ACTIVE' - 'ACTIVE' | 'RATE_LIMITED' | 'INVALID')
- `created_at` (TIMESTAMP)
