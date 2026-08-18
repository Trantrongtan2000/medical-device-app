# Specification & Plan: 002 - Data Deduplication & Master Asset Consolidation

## 1. Mục Tiêu (Objective)
Lọc sạch và loại bỏ toàn bộ dữ liệu trùng lặp từ 7.715 tệp Markdown OCR (`G:\BV QUẬN 7_OCR_WORK_20260712\md`) và chuẩn hóa Cơ sở dữ liệu thiết bị y tế (`database/devices.db`).

---

## 2. Các Quy Tắc Lọc Trùng (Deduplication Rules)

### Quy tắc 1: Loại bỏ tệp sao lưu & phân nhánh thư mục trùng
- Bỏ qua các thư mục trùng nội dung: `backup_original`, `_debug`, `_sample`, `_feedback`.
- Hợp nhất các đường dẫn song song: `pdf/2026` và `2026_pdf`.

### Quy tắc 2: Chuẩn hóa Hồ sơ Thiết bị Duy nhất (Canonical Master Device)
- Định danh duy nhất: `serial_no` (kèm `model` và `facility_id`).
- Nếu cùng một số Serial xuất hiện ở nhiều biên bản (bàn giao, đào tạo, kiểm định), chỉ tạo **duy nhất 1 bản ghi** trong bảng `devices`.
- Tự động điền (enrich) thông tin bị thiếu từ các tệp con liên quan (hãng sản xuất, năm sản xuất, xuất xứ, khoa phòng).

### Quy tắc 3: Hợp nhất Lịch sử Kiểm định & Bảo trì (Certificates & Logs)
- Mỗi giấy chứng nhận (`certificate_no` + `device_id` + `calibration_date`) chỉ xuất hiện 1 lần duy nhất trong bảng `calibration_certificates`.
- Lưu trữ lịch sử theo chuỗi thời gian (Timeline: Lần KĐ 2024 $\rightarrow$ 2025 $\rightarrow$ 2026).

### Quy tắc 4: Chuẩn hóa Liên kết Tệp Gốc PDF
- Mỗi bản ghi chỉ trỏ tới 1 đường dẫn PDF canonical hợp lệ nhất trên ổ G:.

---

## 3. Phân Công Nhiệm Vụ Cho AI & Nghiệm Thu
- **Giao việc cho `ocx claude`:** Quét, lọc và kiểm tra chéo toàn bộ danh sách 266 trường hợp trùng lặp đã phát hiện, thực thi làm sạch và xác thực.
- **Nghiệm thu bởi Antigravity:** Kiểm tra tính toàn vẹn CSDL, đối soát số lượng thiết bị trước/sau, kiểm tra khóa ngoại và xuất báo cáo nghiệm thu.
