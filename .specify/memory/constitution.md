# Medical Device Management System (BV Quận 7) Constitution

## 1. Project Identity & Purpose
- **Mission:** Hệ thống Quản lý Trang Thiết Bị Y Tế cho Bệnh viện Quận 7 số hóa toàn diện 1.049 thiết bị y tế thực tế, kết hợp kiến trúc quản lý tài sản chuẩn **Snipe-IT** và quy trình CMMS **SpeedMaint Cloud (Hoàn Mỹ Sài Gòn)**, trợ lý **Gemini AI**, và công cụ **Mistral OCR-4**.
- **Target Organization:** Bệnh viện Quận 7, TP. Hồ Chí Minh.
- **Compliance Standards:**
  - Nghị định số 98/2021/NĐ-CP của Chính phủ về quản lý trang thiết bị y tế.
  - Thông tư số 05/2022/TT-BYT của Bộ Y Tế.
  - Cổng thông tin Công khai Phân loại TTBYT (IMDA MOH) - 4 mức rủi ro A, B, C, D.
  - Tài liệu hướng dẫn sử dụng phần mềm quản lý TTBYT BV Quận 7 (`TLHD_QLTTBYT_V1.2`).

## 2. Core Architectural Principles
- **Design Philosophy:** "Less, but better" - Tinh gọn, loại bỏ thông tin rườm rà, tập trung vào dữ liệu lâm sàng cốt lõi, độ tương phản cao đạt chuẩn WCAG 2.1 AAA.
- **Data Integrity & Dual Codes:**
  - Mã định danh tài sản Snipe-IT: `BVQ7-TTB-XXXXX`
  - Mã công việc CMMS SpeedMaint: `BM/BVQ7/XXXXX`
  - Số Serial (S/N) là duy nhất và bắt buộc chống trùng lặp trên toàn viện.
- **Multi-Key Rotation Pool:**
  - Toàn bộ các dịch vụ AI bên ngoài (Google Gemini, Mistral AI) bắt buộc phải đi qua lớp quản lý `KeyPool`.
  - Tự động luân chuyển Round-Robin và tự động chuyển tiếp (Failover) khi gặp lỗi Rate-Limit / Quota Exhaustion.
- **Offline & Fallback Safety:**
  - Hệ thống phải luôn luôn phản hồi và duy trì hoạt động thông qua Built-in Rule Engine ngay cả khi không có kết nối Internet hoặc chưa có API Key.

## 3. Technology Stack
- **Backend:** Python 3.14/3.12, FastAPI, SQLite (WAL mode, Foreign Keys ON), Uvicorn.
- **Frontend:** Vanilla HTML5 / CSS3 Design System, Bootstrap 5, Bootstrap Icons, Native JS (Fetch API).
- **AI / OCR Libraries:** `google-genai` (Gemini Interactions API), `mistralai` (Mistral-OCR-4).
