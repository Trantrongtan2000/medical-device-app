# Tasks Checklist: HTM Clinical Workflow v3

- **Feature ID:** `004-htm-clinical-workflow-v3`
- **Status:** 100% Completed

---

## Task List

- [x] **Task 1: Cập nhật Bảng màu & Accessibility WCAG AAA (`taste-skill`)**
  - [x] Tạo CSS classes siêu tương phản cho huy hiệu phân loại rủi ro A, B, C, D (Nền Solid đậm, chữ trắng tinh `#ffffff`).
  - [x] Khắc phục tình trạng chữ mờ trong Sidebar KPI Banner (chuyển sang nhãn sáng Slate-200 và số liệu Neon Green/White).
  - [x] Cập nhật phông chữ Plus Jakarta Sans và JetBrains Mono với `tabular-nums`.

- [x] **Task 2: Bổ sung Nhãn Thẻ Nhà Cung Cấp & Khoa Phòng**
  - [x] Thêm Tag Nhà Cung Cấp (`🏢 [Tên NCC / Hãng]`) trên từng hàng thiết bị trong Bảng.
  - [x] Thêm Tag Khoa Phòng (`📍 [Tên Khoa/Phòng]`) trên từng hàng thiết bị trong Bảng.
  - [x] Thêm cụm Tag đôi Khoa Phòng & Nhà Cung Cấp vào Header của Device Passport Modal.

- [x] **Task 3: Tính năng Điều Chỉnh Thông Tin Thiết Bị (Asset Edit)**
  - [x] Bổ sung nút `Sửa` trực tiếp trên từng hàng thiết bị trong Bảng.
  - [x] Bổ sung nút `Điều Chỉnh Thông Tin` trong Device Passport Modal.
  - [x] Tạo `#editDeviceModal` với form điền đầy đủ metadata kỹ thuật và dropdown 21 khoa phòng.
  - [x] Kết nối `PUT /api/devices/{id}` với xác thực trùng số Serial và ghi nhật ký Audit Trail.

- [x] **Task 4: Tái Cấu Trúc Sidebar Điều Hướng Thành 4 Nhóm Chức Năng**
  - [x] Nhóm 1: Điều Hành Tổng Thể (`Dashboard & Kanban`).
  - [x] Nhóm 2: Danh Mục & Đối Tác (`Thiết Bị & Phụ Kiện`, `Nhà Cung Cấp & HĐ`).
  - [x] Nhóm 3: Quy Trình Lâm Sàng (`Kiểm Tra Đầu Ngày`, `Lịch Bảo Trì & Kiểm Định`, `Điều Chuyển Máy QT.08`, `Xe Cấp Cứu E-Cart`).
  - [x] Nhóm 4: CMMS & Trí Tuệ Nhân Tạo (`Sơ Đồ Quy Trình SVG`, `Bảo Trì SpeedMaint`, `Semantica Context Graph`, `Trợ Lý AI & OCR Hub`).

- [x] **Task 5: Xây Dựng Trang Dashboard Tổng Quan & Bảng Kanban 4 Cột**
  - [x] Bổ sung 4 Thẻ KPI Scorecards cấp cao trên `#tab-overview`.
  - [x] Tích hợp Chart.js với Biểu đồ phân bổ 21 khoa phòng và Biểu đồ donut cơ cấu rủi ro A/B/C/D.
  - [x] Xây dựng Bảng Kanban 4 Cột điều phối tiến độ lâm sàng (Chờ tiếp nhận, Đang xử lý, Chờ nghiệm thu, Đã hoàn tất).
  - [x] Tích hợp Nhật ký nghiệp vụ thực tế (Live Audit Trail) và Danh bạ Hotline khẩn cấp 24/7.
