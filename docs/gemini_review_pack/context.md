# 🏥 HỆ THỐNG QUẢN TRỊ TRANG THIẾT BỊ Y TẾ (HTM v3) — BỆNH VIỆN ĐA KHOA QUẬN 7
## TÀI LIỆU BỐI CẢNH ĐỐI SOÁT CHUẨN XÁC & YÊU CẦU ĐÁNH GIÁ (GEMINI CLINICAL REVIEW CONTEXT)

---

### 📌 1. THÔNG TIN HỆ THỐNG & ĐỐI SOÁT CSDL THỰC TẾ (GROUND TRUTH METRICS):
* **Tên hệ thống:** Medical Device Management & Healthcare Technology Management (HTM v3).
* **Đơn vị áp dụng:** Bệnh viện Đa khoa Quận 7 (Phòng khám Đa khoa Tâm Anh Quận 7).
* **Quy mô quản trị xác thực từ CSDL (`database/devices.db`):**
  - **1.211 Thiết bị y tế** đang phân bổ tại **21 khoa/phòng lâm sàng** (thuộc **39 đơn vị/facilities** trong master data).
  - **Phân loại rủi ro (Nghị định 98/2021/NĐ-CP):** Loại A = **900**, Loại B = **140**, Loại C = **158**, Loại D = **13**.
  - **Hồ sơ số hóa:** **7.330 liên kết thiết bị - tài liệu** sau quy trình dedup theo canonical path, tương ứng **1.164 đường dẫn tệp PDF duy nhất**.
  - **Phân đoạn chứng từ OCR:** **1.156 phân đoạn** (`document_segments`) thuộc **1.071 tài liệu**.
  - **Thực trạng kiểm định (Thông tư 05/2022/TT-BYT):**
    * **529 bản ghi GCN hết hạn** (thuộc 277 thiết bị), trong đó có **262 thiết bị có lần kiểm định mới nhất đã hết hạn**.
    * **16 thiết bị có lần kiểm định mới nhất sắp hết hạn trong 90 ngày** (tương ứng 17 bản ghi GCN).
    * **0 thiết bị bảo trì quá hạn** (tiến độ PM đạt 100%).
  - **Phân bố phương thức đối chiếu nguồn gốc (Match Provenance):**
    * 🟢 **SERIAL (Khớp S/N):** 345 tài liệu (Độ tin cậy rất cao).
    * 🔵 **CALIBRATION_CERT (Khớp Tem KĐ):** 500 tài liệu (Độ tin cậy cao).
    * ℹ️ **CONTRACT (Khớp HĐ):** 1.955 tài liệu (Độ tin cậy trung bình).
    * ⚪ **MODEL (Khớp Model):** 4.530 tài liệu (Tài liệu tham khảo theo dòng máy, không chứng minh tài liệu thuộc đúng tài sản vật lý).
* **Kho mã nguồn GitHub:** `https://github.com/Trantrongtan2000/medical-device-app.git` (Nhánh `main`).
* **Đại diện kỹ thuật & BME:** **Trần Trọng Tấn** (Trưởng/Kỹ sư phụ trách TTBYT).

---

### 🖼️ 2. DANH MỤC 9 ẢNH CHỤP GIAO DIỆN ĐÍNH KÈM TRONG THƯ MỤC:

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

---

### 📝 3. NỘI DUNG PROMPT CHUẨN XÁC GỬI GOOGLE GEMINI:

```markdown
Chào Google Gemini,

Hãy đánh giá 9 ảnh giao diện của hệ thống HTM v3 (Bệnh viện Đa khoa Quận 7) theo 3 vai trò:
- Healthcare UX Lead
- Clinical Engineering/BME Reviewer
- Healthcare Data Governance Auditor

Bối cảnh đã xác minh từ CSDL thực tế:
- 1.211 thiết bị y tế.
- 39 đơn vị trong master data; UI hiển thị 21 khoa/phòng lâm sàng trọng điểm.
- 7.330 liên kết device-document sau dedup, tương ứng 1.164 đường dẫn tài liệu PDF duy nhất.
- 1.156 document segments thuộc 1.071 tài liệu.
- Phân bổ mức độ rủi ro (Nghị định 98): Loại A = 900, Loại B = 140, Loại C = 158, Loại D = 13.
- Thực trạng kiểm định: 529 bản ghi GCN hết hạn (thuộc 277 thiết bị), trong đó có 262 thiết bị có lần kiểm định mới nhất đã hết hạn.
- 16 thiết bị có lần kiểm định mới nhất sẽ hết hạn trong 90 ngày tới.
- Phân bố đối chiếu nguồn gốc (Provenance): MODEL = 4.530, CONTRACT = 1.955, CALIBRATION_CERT = 500, SERIAL = 345.
- Lưu ý: "MODEL match" chỉ là tài liệu tham khảo theo dòng máy, không chứng minh tài liệu thuộc đúng tài sản vật lý.

Hãy phân tích chi tiết:

1. Healthcare UX/UI:
- Tính trực quan cho Bác sĩ, Điều dưỡng, Kỹ sư BME.
- Readability, contrast, keyboard navigation, touch targets.
- Dashboard alerts, Kanban, device catalog, on-call, inspection pre-use.
- Các rủi ro do default state, icon-only actions, hoặc màu sắc tín hiệu.

2. Provenance và PDF.js:
- Giá trị của Serial/Certificate/Contract/Model matching.
- Đề xuất phân cấp độ tin cậy (Confidence tiers) và human-review workflow.
- Khả năng nhảy đúng trang PDF (#page=N) hỗ trợ audit như thế nào.
- Những bằng chứng còn thiếu để được coi là legally/audit defensible.

3. JCI / FDA Readiness Roadmap:
- Không khẳng định certification/compliance vượt quá thực tế.
- Xác định các khoảng trống (gaps) về audit trail, data integrity, CAPA, FMEA, maintenance quality traceability, cybersecurity và AI governance.
- Lập roadmap P0 / P1 / P2 với acceptance criteria đo lường được.

4. Với mỗi nhận xét:
- Chỉ rõ ảnh/màn hình liên quan (từ 01 đến 09).
- Phân biệt rõ: observed fact (thực tế quan sát), inference (suy luận), recommendation (khuyến nghị).
- Không suy diễn tính năng backend chỉ từ ảnh chụp.
```
