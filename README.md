# 🏥 Hệ Thống Quản Lý Trang Thiết Bị Y Tế - BV Quận 7 (SpeedMaint & Snipe-IT Edition)

Hệ thống quản lý trang thiết bị y tế toàn diện cho **Bệnh viện Quận 7**, số hóa toàn bộ 1.049 thiết bị y tế, kết hợp kiến trúc quản lý tài sản **Snipe-IT** và quy trình CMMS **SpeedMaint Cloud (Hoàn Mỹ Sài Gòn)**, tích hợp **Trợ lý Gemini AI**, **Mistral OCR Engine** và **Cơ chế Xoay Key Tự Động (Key Rotation Pool)**.

---

## 🌟 Tính Năng Cốt Lõi

1. **Giao Diện Tinh Gọn ("Less, but better"):**
   - Bố cục Sidebar 5 phân hệ cốt lõi: *Thiết Bị, Kiểm Kê, Bảo Trì & Báo Hỏng, In Nhãn QR, Trợ Lý AI & OCR*.
   - Bảng tài sản 6 cột thiết yếu, dễ nhìn, hỗ trợ tra cứu và lọc theo 22 khoa phòng & 10 nhóm thiết bị.
2. **Quy Trình Nhập Mới Thiết Bị (TLHD Mục 2a, 3 & Nghị Định 98/2021):**
   - Tự động cấp mã kép: Snipe-IT Asset Tag (`BVQ7-TTB-XXXXX`) & SpeedMaint Code (`BM/BVQ7/XXXXX`).
   - Kiểm tra chống trùng Serial trên toàn viện, phân loại rủi ro A/B/C/D theo Cổng IMDA Bộ Y Tế.
   - Tự động sinh hồ sơ kiểm định ban đầu và nhật ký nghiệm thu đưa vào sử dụng.
3. **Cơ Chế Xoay API Key Tự Động (Multi-Key Rotation Pool):**
   - Quản lý danh sách nhiều API Keys cho Google Gemini & Mistral OCR.
   - Tự động chia tải Round-Robin và tự động chuyển tiếp (Failover) khi gặp lỗi Rate-Limit (`429`) hoặc hết Quota.
4. **Trợ Lý Gemini AI (Google GenAI Interactions API):**
   - Trợ lý Kỹ sư Y sinh (BME) tra cứu thông số 1.049 máy và tư vấn quy trình KĐ / PM theo Thông tư 05/2022/TT-BYT.
5. **Mistral OCR Engine Studio (Mistral-OCR-4):**
   - Bóc tách tự động tài liệu scan PDF / Hình ảnh Giấy chứng nhận kiểm định sang Markdown & JSON Schema y tế.
6. **Phiếu Công Việc SpeedMaint CMMS & Kiểm Kê Hiện Trường:**
   - Quản lý phiếu công việc bảo dưỡng `#2607XX`, phụ tùng thay thế và tem in mã QR decal dán máy.

---

## 🚀 Khởi Chạy Ứng Dụng

```bash
# 1. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 2. Khởi chạy máy chủ Web & API
python start_server.py
```

* 🏠 **Giao diện Web:** `http://127.0.0.1:8000`
* 📚 **API Swagger Docs:** `http://127.0.0.1:8000/docs`

---

## 📊 Cấu Trúc Spec Kit (`specs/`)
* `specs/001-medical-device-management/`: Đặc tả nền tảng quản lý TTBYT & số hóa 7.700+ tệp OCR.
* `specs/002-data-deduplication/`: Kế hoạch chuẩn hóa & lọc dữ liệu 1.049 máy từ 36 nhóm thiết bị.
* `specs/003-speedmaint-snipeit-ai-integration/`: Đặc tả tích hợp SpeedMaint, Snipe-IT, Gemini AI, Mistral OCR & Key Rotation.