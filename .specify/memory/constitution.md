# Constitution: Medical Device Management System (BV Quận 7)

## Core Principles

### 1. Medical Device Compliance & Regulatory Adherence
- Hệ thống phải tuân thủ nghiêm ngặt theo **Nghị định 98/2021/NĐ-CP** về Quản lý Trang thiết bị y tế (phân loại rủi ro A, B, C, D) và bộ 83 Tiêu chí Chất lượng Bệnh viện (Tiêu chí C7 - Quản lý Trang thiết bị y tế).
- Mọi dữ liệu về kiểm định, hiệu chuẩn, an toàn bức xạ, kiểm soát nước RO, khí y tế phải gắn liền với mã định danh thiết bị (Serial Number / Asset Tag) và trỏ trực tiếp đến tệp PDF gốc lưu trữ tại `G:\BV QUẬN 7_OCR_WORK_20260712`.

### 2. Spec-Driven Architecture & Source of Truth
- Mọi tính năng, luồng nghiệp vụ và cấu trúc CSDL đều phải xuất phát từ tài liệu đặc tả (`specs/`).
- Dữ liệu OCR từ `G:\BV QUẬN 7_OCR_WORK_20260712\md` và các quy trình chuẩn `TA5.TTBYT.QT.01 -> QT.09` tại `asset-management-tools/36. TRANG THIẾT BỊ Y TẾ` là nguồn dữ liệu chuẩn mực (Master Data).

### 3. User Experience & Standards Reference (Snipe-IT & SpeedMaint)
- **Snipe-IT Reference:** Quản lý vòng đời tài sản (Check-in/Check-out, in nhãn mã QR code, quản lý theo khoa phòng / người phụ trách, audit log).
- **SpeedMaint CMMS Reference:** Quản lý bảo trì phòng ngừa (PM), cảnh báo hạn kiểm định / hiệu chuẩn (mức cảnh báo 30 ngày, quá hạn đỏ), quản lý yêu cầu sửa chữa và downtime.

### 4. Code Quality & Security Standards
- **Backend:** FastAPI, SQLite (kích hoạt WAL mode & Foreign Keys), Pydantic v2 validation, parameterized queries chống SQL injection.
- **Frontend:** Vanilla JS & Modern CSS/Bootstrap, thiết kế responsive, không phụ thuộc build phức tạp, giao diện trực quan và phản hồi tức thì.
- **Data Integrity:** Xử lý lỗi ngoại lệ từng tệp, không để gián đoạn quá trình quét hàng nghìn tệp hồ sơ bệnh viện.
