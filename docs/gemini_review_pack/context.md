# 🏥 HỆ THỐNG QUẢN TRỊ TRANG THIẾT BỊ Y TẾ (HTM v3) — BỆNH VIỆN ĐA KHOA QUẬN 7
## TÀI LIỆU BỐI CẢNH ĐỐI SOÁT CHUẨN XÁC & YÊU CẦU ĐÁNH GIÁ (GEMINI CLINICAL REVIEW CONTEXT)

---

### 📌 1. THÔNG TIN HỆ THỐNG & ĐỐI SOÁT CSDL THỰC TẾ (GROUND TRUTH METRICS):
* **Tên hệ thống:** Medical Device Management & Healthcare Technology Management (HTM v3).
* **Đơn vị áp dụng:** Bệnh viện Đa khoa Quận 7 (Phòng khám Đa khoa Tâm Anh Quận 7).
* **Quy mô quản trị xác thực từ CSDL (`database/devices.db`):**
  - **1.211 Thiết bị y tế** đang phân bổ tại **21 khoa/phòng lâm sàng** (thuộc **39 đơn vị/facilities** trong master data).
  - **Phân loại rủi ro (Nghị định 98/2021/NĐ-CP):** Loại A = **900**, Loại B = **140**, Loại C = **158**, Loại D = **13**.
  - **Hồ sơ số hóa thiết bị:** **6.330 liên kết chứng từ sạch** (đã thanh lọc triệt để 1.249 liên kết gán nhầm S/N hoặc biên bản cá thể theo Model), tương ứng **1.091 đường dẫn tệp PDF duy nhất**. **100.0% thiết bị (1.211/1.211 máy)** đều có chứng từ pháp lý chuẩn xác.
  - **Kho dữ liệu số hóa toàn viện (`/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712`):** **20.806 tệp PDF scan thật** (Hợp đồng: 1.594, Bàn giao: 5.511, Kiểm định & Pháp lý: 10.161, Lưu trữ: 3.462 tệp).
  - **Thực trạng kiểm định (Thông tư 05/2022/TT-BYT):**
    * **529 bản ghi GCN hết hạn** (thuộc 277 thiết bị), trong đó có **262 thiết bị có lần kiểm định mới nhất đã hết hạn**.
    * **16 thiết bị có lần kiểm định mới nhất sắp hết hạn trong 90 ngày** (tương ứng 17 bản ghi GCN).
    * **0 thiết bị bảo trì quá hạn** (tiến độ PM đạt 100%).
  - **Phân bố phương thức đối chiếu nguồn gốc (Match Provenance):**
    * 🟢 **SERIAL (Khớp S/N):** 345 tài liệu (Độ tin cậy rất cao).
    * 🔵 **CALIBRATION_CERT (Khớp Tem KĐ):** 500 tài liệu (Độ tin cậy cao).
    * ℹ️ **CONTRACT (Khớp HĐ & Bàn giao NCC):** 2.204 tài liệu (Độ tin cậy trung bình).
    * ⚪ **MODEL (HDSD tham khảo theo dòng máy):** 3.281 tài liệu (Đã chuẩn hóa nhãn, không chứa tài liệu có S/N máy khác).
* **Kho mã nguồn GitHub:** `https://github.com/Trantrongtan2000/medical-device-app.git` (Nhánh `main`).
* **Đại diện kỹ thuật & BME:** **Trần Trọng Tấn** (Trưởng/Kỹ sư phụ trách TTBYT).

---

### 🛠️ 2. GIẢI THÍCH NGHIỆP VỤ: "BẢO TRÌ SPEEDMAINT" & "FEEDBACK LOOP":

#### 🔧 A. Tag / Phân Hệ "Bảo Trì SpeedMaint" Là Gì?
1. **Bản chất nghiệp vụ:**
   * **SpeedMaint** là định danh phân hệ **CMMS (Computerized Maintenance Management System)** chuyên trách quản lý quy trình bảo trì, bảo dưỡng và xử lý sự cố thiết bị y tế của bệnh viện theo **Quy trình QT.06** và **Biểu mẫu BM05 (Phiếu lý lịch & bảo trì TTBYT)**.
2. **Các chức năng chính của SpeedMaint trong HTM v3:**
   * **Quản lý Phiếu Công Việc (Work Orders):** Lập phiếu bảo trì dự phòng (PM - Preventive Maintenance) định kỳ theo tuần/tháng/quý và phiếu sửa chữa sự cố (CM - Corrective Maintenance).
   * **Mã định danh SpeedMaint:** Mỗi thiết bị được gán một mã quản lý bảo trì duy nhất theo cấu trúc `BM/BVQ7/xxxxx` (đồng bộ với tem dán trên thân máy).
   * **Theo dõi tiến độ & phân công kỹ sư:** Phân công kỹ sư BME thực hiện, theo dõi vật tư linh kiện thay thế, thời gian phản hồi (MTTR) và nghiệm thu hoàn thành.

#### 💡 B. Ý Nghĩa Của Tính Năng "Góp Ý Chỉnh Sửa" (User Feedback Loop for Continuous AI Improvement)
1. **Mục đích:**
   * Là kênh tương tác trực tiếp (nút nổi góc phải màn hình `#feedbackModal`) dành cho Bác sĩ, Điều dưỡng, Kỹ sư lâm sàng và Lãnh đạo khoa gửi ý kiến phản hồi về: sai lệch thông tin máy, đề xuất thêm trường dữ liệu, góp ý quy trình SOPs hoặc báo lỗi giao diện.
2. **Cơ chế lưu trữ & Xử lý:**
   * Toàn bộ dữ liệu được ghi vào bảng CSDL `system_feedback` (gồm: Danh mục, Người gửi, Khoa phòng, Mức độ ưu tiên, Nội dung chi tiết, Trạng thái `PENDING / RESOLVED`, Ghi chú xử lý).
3. **Giá trị với việc phát triển ứng dụng bằng AI:**
   * Các phản hồi này đóng vai trò là **Dữ liệu thực tế từ người dùng (Human-in-the-loop Ground Truth)**, giúp mô hình AI phân tích, đối soát và tự động đề xuất phương án tối ưu hóa codebase, giao diện và luồng nghiệp vụ trong các lần nâng cấp tiếp theo.

---

### 🖼️ 3. DANH MỤC 11 ẢNH CHỤP GIAO DIỆN HỆ THỐNG ĐÍNH KÈM:

| STT | Tên Tệp Ảnh | Màn Hình / Chức Năng Chính |
| :---: | :--- | :--- |
| **01** | `01_dashboard_full.png` | **Dashboard Toàn Viện:** 3 thẻ KPI lớn, Thanh cảnh báo an toàn pháp lý thời gian thực, Cơ cấu 4 Khoa Chuyên Môn + Phòng TTBYT, Bảng Kanban điều hành 4 cột, Biểu đồ phân bổ 21 khoa lâm sàng và Cơ cấu rủi ro A/B/C/D. |
| **02** | `02_devices_catalog.png` | **Danh Mục 1.211 Thiết Bị:** Bảng Master Catalog, bộ lọc đa tầng (Từ khóa, Khoa, Rủi ro A/B/C/D), phím tắt `Ctrl+K`, các nút Thao tác (Xem/Sửa/Điều chuyển). |
| **03** | `03_staff_management.png` | **Quản Lý Nhân Sự BME & Lịch Trực 24/7:** Danh sách kỹ sư lâm sàng, lãnh đạo trực, backup, hotline cấp cứu. |
| **04** | `04_vendors_contracts.png` | **Nhà Cung Cấp & Hợp Đồng Thầu (102 NCC):** Hồ sơ các hãng GE, Siemens, Toshiba, Nihon Kohden, Mindray, Olympus; tra cứu theo số hợp đồng. |
| **05** | `05_inspections_preuse.png` | **Kiểm Tra An Toàn Đầu Ngày (QT.05):** Bố cục 2 cột: bên trái nhập checklist, bên phải đối chiếu lịch sử kiểm tra gần nhất. |
| **06** | `06_schedules_calibration.png` | **Lịch Kiểm Định & Hiệu Chuẩn (TT 05):** Ma trận theo dõi thời hạn kiểm định, cảnh báo máy đến hạn tái kiểm định. |
| **07** | `07_speedmaint_maintenance.png` | **Bảo Trì SpeedMaint CMMS & Nhật Ký BM05:** Lịch sử sửa chữa, thay thế linh kiện, bảo trì dự phòng (PM) và xử lý sự cố. |
| **08** | `08_semantica_graph.png` | **Semantica Provenance Query & AI Hub:** Truy vấn bằng chứng nguồn gốc và đồ thị tri thức đa chiều. |
| **09** | `09_pdfjs_scanned_document.png` | **Trình Đọc PDF Scan Thật (Mozilla PDF.js):** Đọc biên bản bàn giao, phiếu kiểm định có dấu đỏ và chữ ký BME **Trần Trọng Tấn**, tự động nhảy đúng trang `#page=N`. |
| **10** | `10_documents_hub.png` | **Kho Hồ Sơ & Dữ Liệu Số Hóa Toàn Viện (20.806 PDF):** Quản lý toàn bộ văn bản Hợp đồng thầu, Bàn giao vật tư, Kiểm định gộp, Pháp lý Sở Y Tế và HDSD chung. |
| **11** | `11_suppliers_contracts.png` | **Tương Tác Hồ Sơ Hợp Đồng & Thiết Bị:** Click vào bất kỳ số HĐ nào để xem chi tiết gói thầu và toàn bộ danh mục máy kèm theo. |

---

### 📝 4. NỘI DUNG PROMPT GỬI GOOGLE GEMINI / MÔ HÌNH REVIEW:

```markdown
Chào Chuyên Gia Đánh Giá,

Hãy phân tích và đánh giá 11 ảnh giao diện của hệ thống HTM v3 (Bệnh viện Đa khoa Quận 7) theo 3 góc nhìn:
1. Healthcare UX/UI Lead (Trải nghiệm người dùng y tế lâm sàng).
2. Clinical Engineering/BME Reviewer (Quản trị kỹ thuật thiết bị y tế & bảo trì CMMS SpeedMaint).
3. Healthcare Data Governance Auditor (Tính toàn vẹn dữ liệu, kiểm toán pháp lý ALCOA+ và kho dữ liệu số hóa 20.806 PDF).

Bối cảnh hệ thống thực tế:
- 1.211 thiết bị y tế tại 21 khoa lâm sàng.
- Phân loại rủi ro: Loại A = 900, Loại B = 140, Loại C = 158, Loại D = 13.
- Kho dữ liệu: 20.806 tệp PDF scan thật, 6.330 liên kết chứng từ sạch gắn vào thiết bị.
- Phân hệ SpeedMaint CMMS: Quản lý bảo trì dự phòng PM, sửa chữa CM, mã định danh BM/BVQ7/xxxxx.
- Phân hệ Feedback Loop: Thu thập ý kiến lâm sàng và lưu vào CSDL làm Ground Truth cho AI tối ưu hóa.

Hãy đưa ra nhận xét chi tiết, chỉ rõ hình ảnh minh chứng và các khuyến nghị nâng cấp thực tiễn!
```

---

### 📌 5. KẾ HOẠCH BẢO MẬT & QUẢN TRỊ NÂNG CAO (PENDING ROADMAP - SẼ THỰC HIỆN SAU):

* [ ] **1. Mã hóa khoá API bảo mật (AI Key Encryption at Rest):**
  - Chuyển đổi lưu trữ `api_keys` từ plaintext sang mã hóa chuẩn **AES-256-GCM** với khóa dẫn xuất (PBKDF2/Argon2) từ `APP_SECRET_KEY` hoặc biến môi trường.
  - Che giấu khóa (Masking) trên giao diện cấu hình (chỉ hiển thị `sk-ant-***...`).
* [ ] **2. Luồng Đăng nhập & Xác thực Thực tế (Real Authentication & Session Management):**
  - Xây dựng luồng đăng nhập thực tế (JWT Token / HttpOnly Secure Cookies) trước khi bật chế độ cưỡng chế toàn diện `HTM_ENFORCE_RBAC=1` trên môi trường Production.
  - Phân quyền theo vai trò: `CLINICAL_STAFF` (chỉ xem & báo hỏng), `BME_ENGINEER` (nhập kiểm định, tạo phiếu bảo trì), `ADMIN` (cấu hình hệ thống, quản lý khoá API).
* [ ] **3. Phân Hệ Kiểm Toán Audit Trail & Nhật Ký CAPA / FMEA Chuẩn Y Tế:**
  - Nâng cấp từ chế độ log demo sang ghi nhận bất biến (Append-only Audit Log) mọi tác vụ thêm/sửa/xóa thiết bị và biên bản kỹ thuật theo tiêu chuẩn **FDA 21 CFR Part 11** và **ALCOA+**.
  - Quy trình xử lý hành động khắc phục & phòng ngừa sự cố (CAPA - Corrective and Preventive Action) liên kết trực tiếp với các phiếu sự cố CMMS SpeedMaint.
