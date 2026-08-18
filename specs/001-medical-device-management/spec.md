# Specification: 001 - Medical Device Management System (BV Quận 7)

## 1. Overview
Hệ thống Quản lý Trang Thiết Bị Y Tế cho Bệnh viện Quận 7, số hóa toàn bộ hồ sơ thiết bị, giấy chứng nhận kiểm định, hiệu chuẩn, biên bản bàn giao từ hơn 7.700 tệp Markdown OCR kết hợp các tính năng chuẩn từ Snipe-IT và SpeedMaint CMMS.

---

## 2. User Stories & Acceptance Criteria

### User Story 1: Dashboard & Cảnh báo Kiểm định / Hiệu chuẩn (SpeedMaint style)
- **As a** Trưởng phòng Trang thiết bị Y tế / Kỹ sư y sinh (BME),
- **I want** xem tức thì tổng quan thiết bị, số lượng thiết bị đạt chuẩn, số lượng sắp đến hạn kiểm định (30 ngày) và số lượng đã quá hạn,
- **So that** tôi kịp thời lập kế hoạch kiểm định/hiệu chuẩn định kỳ, đảm bảo an toàn khám chữa bệnh và đáp ứng tiêu chí chất lượng bệnh viện.

**Acceptance Criteria:**
- 4 KPI cards hiển thị dữ liệu thời gian thực: Tổng thiết bị, Đạt chuẩn (OK), Cảnh báo (WARNING - 30 ngày), Quá hạn (OVERDUE).
- Phân loại màu sắc rõ ràng (Xanh lá: Đạt, Vàng: Cảnh báo, Đỏ: Quá hạn).

---

### User Story 2: Tra cứu & Quản lý Danh mục Thiết bị (Snipe-IT style)
- **As a** Nhân viên quản lý tài sản / Kỹ thuật viên,
- **I want** tra cứu, lọc và xem thông tin chi tiết của từng máy theo Serial, Model, Hãng, Khoa/Phòng, Mức độ rủi ro A/B/C/D,
- **So that** tôi nhanh chóng nắm bắt vị trí, tình trạng vận hành và lịch sử bảo trì.

**Acceptance Criteria:**
- Tìm kiếm tức thì theo từ khóa (debounce search).
- Bộ lọc đa tiêu chí: Khoa/Phòng ban (22 khoa), Phân loại nhóm thiết bị, Trạng thái kiểm định.
- Bảng dữ liệu hiển thị rõ ràng thông tin: Serial, Tên thiết bị, Hãng SX, Model, Mức rủi ro, Khoa/Phòng, Ngày KĐ, Hạn KĐ, Trạng thái.

---

### User Story 3: Xem Hồ sơ Lý lịch & Tệp Chứng từ Gốc (PDF / OCR)
- **As a** Bác sĩ lâm sàng hoặc Kiểm toán viên y tế,
- **I want** xem chi tiết lý lịch máy và mở trực tiếp tệp PDF gốc (chứng chỉ kiểm định, biên bản bàn giao) từ ổ đĩa lưu trữ,
- **So that** tôi có đầy đủ bằng chứng pháp lý khi cơ quan quản lý kiểm tra.

**Acceptance Criteria:**
- Modal hiển thị chi tiết lý lịch máy: thông số, xuất xứ, năm SX, trạng thái.
- Lịch sử đầy đủ các lần kiểm định/hiệu chuẩn (Số GCN, số tem, đơn vị thực hiện, ngày hiệu lực).
- Nút "Xem PDF gốc" mở trực tiếp tệp PDF liên kết từ `G:\BV QUẬN 7_OCR_WORK_20260712`.
- Tự động sinh mã QR Code cho từng thiết bị để in nhãn dán.

---

## 3. Data Integration Requirements
- Nguồn dữ liệu: `G:\BV QUẬN 7_OCR_WORK_20260712\md` (7.715 tệp MD có YAML frontmatter).
- Nguồn tài liệu PDF: `G:\BV QUẬN 7_OCR_WORK_20260712` (PDF gốc tương ứng `source_pdf`).
- Quy trình chuẩn: Bám sát các quy trình `TA5.TTBYT.QT.01 -> QT.09` và `TLHD_QLTTBYT_V1.2.md`.
