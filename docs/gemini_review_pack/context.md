# 🏥 HỆ THỐNG QUẢN TRỊ TRANG THIẾT BỊ Y TẾ (HTM v3) — BỆNH VIỆN ĐA KHOA QUẬN 7
## TÀI LIỆU BỐI CẢNH TOÀN DIỆN & YÊU CẦU ĐÁNH GIÁ (GEMINI CLINICAL REVIEW CONTEXT)

---

### 📌 1. THÔNG TIN CHUNG DỰ ÁN (PROJECT OVERVIEW):
* **Tên hệ thống:** Medical Device Management & Healthcare Technology Management (HTM v3).
* **Đơn vị áp dụng:** Bệnh viện Đa khoa Quận 7 (Phòng khám Đa khoa Tâm Anh Quận 7).
* **Quy mô quản trị:**
  - **1.211 Thiết bị y tế** đang hoạt động tại 21 Khoa/Phòng/Khu điều trị chuyên môn.
  - **8.011 Tệp tài liệu số hóa OCR** (~75 GB tài liệu PDF scan thật).
  - **1.156 Phân đoạn chứng từ** (`document_segments`) được trích xuất bằng mô hình Chandra OCR.
* **Kho mã nguồn GitHub:** `https://github.com/Trantrongtan2000/medical-device-app.git` (Nhánh `main`).
* **Đại diện kỹ thuật & BME:** **Trần Trọng Tấn** (Trưởng/Kỹ sư phụ trách TTBYT).

---

### 🖼️ 2. DANH MỤC 9 ẢNH CHỤP GIAO DIỆN ĐÍNH KÈM TRONG THƯ MỤC:

| STT | Tên Tệp Ảnh | Màn Hình / Chức Năng Chính |
| :---: | :--- | :--- |
| **01** | `01_dashboard_full.png` | **Dashboard Toàn Viện:** 3 thẻ KPI lớn, Thanh cảnh báo an toàn pháp lý thời gian thực, Cơ cấu 4 Khoa Chuyên Môn + Phòng TTBYT, Bảng Kanban điều hành 4 cột, Biểu đồ phân bổ khoa/phòng và Cơ cấu rủi ro Nghị định 98. |
| **02** | `02_devices_catalog.png` | **Danh Mục 1.211 Thiết Bị:** Bảng Master Catalog, bộ lọc đa tầng (Từ khóa, 21 Khoa, 4 cấp rủi ro A/B/C/D), phím tắt `Ctrl+K`, các nút Thao tác (Xem/Sửa/Điều chuyển). |
| **03** | `03_staff_management.png` | **Quản Lý Nhân Sự BME & Lịch Trực:** Danh sách kỹ sư lâm sàng, phân công phụ trách máy, quản lý bằng cấp đào tạo trang thiết bị y tế. |
| **04** | `04_vendors_contracts.png` | **Nhà Cung Cấp & Hợp Đồng Thầu (102 NCC):** Hồ sơ các hãng GE, Siemens, Toshiba, Nihon Kohden, Mindray, Olympus; tra cứu theo số hợp đồng. |
| **05** | `05_inspections_preuse.png` | **Kiểm Tra An Toàn Đầu Ngày (QT.05):** Bảng kiểm an toàn trước ca mổ/ca trực lâm sàng, nhật ký kiểm tra hàng ngày. |
| **06** | `06_schedules_calibration.png` | **Lịch Kiểm Định & Hiệu Chuẩn (TT 05):** Ma trận theo dõi thời hạn kiểm định, cảnh báo máy đến hạn tái kiểm định. |
| **07** | `07_speedmaint_maintenance.png` | **Bảo Trì SpeedMaint CMMS & Nhật Ký BM05:** Lịch sử sửa chữa, thay thế linh kiện, bảo trì dự phòng (PM) và xử lý sự cố. |
| **08** | `08_semantica_graph.png` | **Semantica Context Graph & AI Hub:** Đồ thị tri thức liên kết ngữ nghĩa giữa Thiết bị $\leftrightarrow$ Khoa $\leftrightarrow$ Hợp đồng $\leftrightarrow$ Nhân sự $\leftrightarrow$ Tài liệu PDF scan. |
| **09** | `09_pdfjs_scanned_document.png` | **Trình Đọc PDF Scan Thật (Mozilla PDF.js):** Đọc biên bản bàn giao, phiếu kiểm định có dấu đỏ và chữ ký BME **Trần Trọng Tấn**, tự động nhảy đúng trang `#page=N`. |

---

### 🌟 3. CÁC TÍNH NĂNG CỐT LÕI ĐỘT PHÁ CỦA HỆ THỐNG:

1. **Chuỗi Bằng Chứng Đối Chiếu Nguồn Gốc (Provenance Verification Chain):**
   - Giải quyết bài toán lớn nhất của bệnh viện: *"Làm sao biết tài liệu scan này đúng 100% của máy này?"*
   - Hệ thống gắn nhãn đối chiếu minh bạch:
     * 🟢 **Khớp S/N (Serial Number):** Hồ sơ scan có chứa chính xác số seri của máy.
     * 🔵 **Khớp Tem KĐ (Calibration Cert):** Biên bản kiểm định có mã tem dán trùng khớp.
     * ℹ️ **Khớp HĐ (Contract Number):** Hồ sơ mua sắm/bàn giao theo số Hợp đồng thầu.
     * ⚪ **Khớp Model (Device Model):** Tài liệu hướng dẫn sử dụng cùng dòng máy.
   - **Khử trùng lặp 100%:** 1 file scan dù xuất hiện ở nhiều folder trên ổ cứng chỉ hiển thị duy nhất 1 lần trong hồ sơ máy.

2. **Trình Đọc Mozilla PDF.js Tích Hợp Nhảy Phân Đoạn (#page=N):**
   - Đã nhúng trọn bộ Mozilla PDF.js Core (`pdf.mjs`, `pdf.worker.mjs`, `viewer.html`).
   - Mở trực tiếp các tệp PDF scan dung lượng lớn, nhảy tức thì đến trang chứng từ cần xem (`document_segments`).

3. **Thanh Cảnh Báo An Toàn Thời Gian Thực (Top Alerts Bar):**
   - 🔴 **529 Hết hạn kiểm định:** Cảnh báo các thiết bị quá hạn kiểm định theo Thông tư 05/2022/TT-BYT.
   - 🟡 **17 Sắp hết hạn (90 ngày):** Cảnh báo máy cần lập kế hoạch tái kiểm định trong quý tới.
   - 🔵 **0 Bảo trì quá hạn:** Tiến độ hoàn thành bảo dưỡng định kỳ đạt chuẩn tối đa.

4. **Tuân Thủ Tiêu Chuẩn Y Tế Việt Nam & Quốc Tế:**
   - Phân loại rủi ro theo **Nghị định 98/2021/NĐ-CP** (Loại A: 851, Loại B: 71, Loại C: 106, Loại D: 45).
   - Quy trình biểu mẫu: **QT.01** (Tiếp nhận bàn giao), **QT.05** (Kiểm tra đầu ngày), **QT.08** (Điều chuyển máy), **BM05** (Sổ lý lịch máy).

---

### 📝 4. CÂU HỎI GỢI Ý ĐỂ GỬI GOOGLE GEMINI ĐÁNH GIÁ (PROMPT TEMPLATE):

```markdown
Chào Google Gemini,

Dưới đây là tài liệu bối cảnh (context.md) và trọn bộ 9 ảnh chụp màn hình giao diện thực tế của Hệ thống Quản trị Trang Thiết Bị Y Tế (HTM v3) tại Bệnh viện Đa khoa Quận 7.

Nhờ Gemini thẩm định và đánh giá chuyên sâu giúp tôi theo 3 khía cạnh:
1. Đánh giá Trải nghiệm Người dùng Y tế (Healthcare UX/UI):
   - Đánh giá tính trực quan, công thái học (ergonomics), độ tương phản và tốc độ thao tác cho Bác sĩ, Điều dưỡng và Kỹ sư BME.
   - Đánh giá bố cục Dashboard, thanh Cảnh báo thời gian thực và Bảng điều phối Kanban 4 cột.
2. Đánh giá Tính năng Đối chiếu Nguồn gốc (Provenance Badges) & Trình đọc PDF.js phân đoạn:
   - Mô hình chuỗi bằng chứng (Khớp S/N, Khớp Tem KĐ, Khớp HĐ) và khả năng nhảy đúng số trang PDF scan thật giải quyết được những bài toán gì trong quản lý thiết bị bệnh viện?
3. Đề xuất Lộ trình Nâng cấp Chuẩn Quốc tế (JCI / FDA Ready):
   - Cần bổ sung thêm những tính năng hoặc quy trình nào (ví dụ: AI Co-pilot phát hiện sai lệch dữ liệu, quản lý rủi ro FMEA, bảo trì dự đoán Predictive Maintenance) để đạt chuẩn JCI?
```
