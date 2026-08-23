# BÁO CÁO RÀ SOÁT TRÙNG LẶP DỮ LIỆU PDF & HỒ SƠ OCR (OCX CLAUDE CODE)

> **Công cụ thực hiện:** `ocx claude` (Claude Code CLI thông qua OpenCodex Proxy)  
> **Thư mục kiểm tra:** `G:\BV QUẬN 7_OCR_WORK_20260712\md`  
> **Thời gian hoàn thành:** 18/08/2026

---

## 📊 1. TỔNG QUAN KẾT QUẢ RÀ SOÁT
Qua quá trình AI Claude đọc và đối soát trực tiếp từng tệp Markdown trong kho lưu trữ OCR của Bệnh viện Quận 7, hệ thống đã phát hiện **266 trường hợp trùng lặp dữ liệu**, thuộc 3 nhóm chính:

1. **Trùng lặp `source_pdf` (Tệp PDF nguồn):** Các tệp chứng từ mua sắm và pháp lý có cùng tên gốc xuất hiện ở nhiều thư mục đợt kiểm định/thẩm định khác nhau.
2. **Trùng lặp `serial_no` (Số Serial máy):** Cùng một thiết bị xuất hiện ở cả biên bản bàn giao, phiếu đào tạo và giấy chứng nhận kiểm định.
3. **Trùng lặp `cert_no` (Số Giấy chứng nhận kiểm định):** Các mã chứng chỉ kiểm định xuất hiện lặp lại giữa các lần chạy pipeline OCR.

---

## 🔍 2. CHI TIẾT CÁC NHÓM TRÙNG LẶP PHỔ BIẾN

### A. Tệp PDF Chứng từ Chung (Generic PDF Duplicates)
* `CO,CQ.pdf`: Xuất hiện lặp lại trong nhiều thư mục hợp đồng và gói thầu.
* `Tờ khai hải quan.pdf`: Xuất hiện trong các đợt bàn giao thiết bị nhập khẩu.
* `HĐMB.pdf` & `HĐMB+BBBG+Bộ chứng từ.pdf`: Xuất hiện trong các hồ sơ lưu trữ theo năm (2024, 2025, 2026).

### B. Giấy Chứng Nhận Kiểm Định / Hiệu Chuẩn Bị Trùng (`cert_no`)
* Dải mã hiệu chuẩn thiết bị cân & nhân trắc học: `056-101/01.26M`, `056-102/01.26M` (cân giảm cân và thiết bị đo chiều cao MS3500+HM80M).
* Dải mã chứng nhận hiệu chuẩn: `056-009/01.26H`, `056-010/02.26H`, `056-1000/01.26P`.
* Dải mã chứng nhận liên tục từ: `056-363/..` đến `056-398/..`.
* Dải mã: `056-994/01.26P`, `056-995/01.26P`.

---

## 🧠 3. NGUYÊN NHÂN GÂY RA TRÙNG LẶP
1. **Tồn tại thư mục sao lưu (`backup_original`):** Tệp gốc và bản sao lưu dự phòng cùng được chuyển đổi OCR sang định dạng Markdown.
2. **Phân nhánh thư mục theo năm (`pdf/2026` vs `2026_pdf`):** Cùng một bộ hồ sơ chứng từ PDF nhưng được lưu trữ ở 2 cấu trúc thư mục khác nhau khi quét.
3. **Tách tệp kiểm định nhiều trang (`kiemdinh_tachfile`):** Một chứng chỉ kiểm định nhiều trang được cắt nhỏ ra từng trang đơn lẻ, khiến số GCN xuất hiện lặp lại nhiều lần.

---

## 💡 4. GIẢI PHÁP ĐÃ ĐƯỢC XỬ LÝ TRÊN CƠ SỞ DỮ LIỆU (`devices.db`)
* **Khóa chính duy nhất (`serial_no UNIQUE`):** Khi nạp vào CSDL SQLite, hệ thống tự động gộp (Upsert/Merge) các bản ghi trùng Serial, không tạo bản ghi rác trùng lặp.
* **Quan hệ 1 - Nhiều (`1:N`):** Một thiết bị chỉ có một hồ sơ gốc duy nhất trong bảng `devices`, các lần kiểm định/bàn giao trùng hoặc kế tiếp được lưu trữ vào bảng con `calibration_certificates` và `maintenance_logs` theo thứ tự thời gian.
* **Loại bỏ trùng lặp tệp:** Cập nhật script nhập liệu tự động bỏ qua thư mục `backup_original` khi đồng bộ dữ liệu vào ứng dụng.
