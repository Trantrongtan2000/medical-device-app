# 📉 BÁO CÁO NỢ KỸ THUẬT (TECHNICAL DEBT REGISTER)
## MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3) — BV QUẬN 7

> **Nguyên tắc phân tích:** Nhận diện trung thực mọi điểm nghẽn, cấu trúc kém tối ưu, mã nguồn trùng lặp và rủi ro kiến trúc tích tụ trong quá trình phát triển để lên kế hoạch xử lý dứt điểm.

---

## 1. DANH MỤC NỢ KỸ THUẬT CHI TIẾT (TECHNICAL DEBT REGISTER)

| Mã Nợ | Phân Loại | Vị Trí & Tệp Liên Quan | Mô Tả Thực Tế (Evidence) | Tác Động & Rủi Ro (Impact) | Mức Độ | Ước Tính Công Sức |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **TD-01** | Backend Monolith | [`app/routes.py`](file:///C:/Users/tantt/Downloads/medical-device-app/app/routes.py) (2.016 dòng) | Gộp 85 endpoints, raw SQL, file I/O, AI calls trong 1 file. | Khó bảo trì, dễ merge conflict, khó viết unit tests. | **CRITICAL** | 2.5 Ngày |
| **TD-02** | Frontend Monolith | [`web/js/app.js`](file:///C:/Users/tantt/Downloads/medical-device-app/web/js/app.js) (3.776 dòng) | 1 file class JS gánh toàn bộ DOM (434 `getElementById`), 59 `fetch()`. | Rò rỉ bộ nhớ, khó mở rộng tính năng mới, tải trang nặng. | **HIGH** | 3.0 Ngày |
| **TD-03** | Dead Code | [`web/js/api.js`](file:///C:/Users/tantt/Downloads/medical-device-app/web/js/api.js) (195 dòng) | Tệp API client được viết sẵn nhưng bị bỏ qua 100% (0 lượt gọi). | Gây hiểu nhầm trong codebase, lặp lại logic gọi HTTP 59 lần. | **MEDIUM** | 0.5 Ngày |
| **TD-04** | Duplicate Large File | [`web/quy_trinh_ttbyt.html`](file:///C:/Users/tantt/Downloads/medical-device-app/web/quy_trinh_ttbyt.html) vs [`web/sops.html`](file:///C:/Users/tantt/Downloads/medical-device-app/web/sops.html) | 2 tệp HTML giống hệt nhau (14.765 dòng / 549.8 KB mỗi tệp). | Lãng phí dung lượng lưu trữ, cập nhật 1 bên dễ lệch bên kia. | **LOW** | 0.2 Ngày |
| **TD-05** | Script Sprawl | Thư mục [`scripts/`](file:///C:/Users/tantt/Downloads/medical-device-app/scripts/) (101 file) | 18 script monkey-patch sửa regex UI, 21 script ad-hoc SQL, 2 tệp log JSON nặng 60MB. | Làm loãng repository, che giấu logic nghiệp vụ thực sự. | **HIGH** | 1.0 Ngày |
| **TD-06** | Hardcoded Paths | [`app/routes.py`](file:///C:/Users/tantt/Downloads/medical-device-app/app/routes.py#L28-L33) | Hardcode ổ đĩa `G:\BV QUẬN 7` và đường dẫn cá nhân `C:\Users\tantt\...`. | Không chạy được trên Linux / Docker container / Cloud. | **HIGH** | 0.5 Ngày |
| **TD-07** | Missing Table | Database [`database/devices.db`](file:///C:/Users/tantt/Downloads/medical-device-app/database/devices.db) | Bảng `work_orders` được định nghĩa trong routes nhưng không tồn tại trong DB. | Gây lỗi `500 Internal Server Error` khi người dùng gọi API phiếu sửa chữa. | **HIGH** | 0.5 Ngày |
| **TD-08** | Duplicate Database | [`app/medical_devices.db`](file:///C:/Users/tantt/Downloads/medical-device-app/app/medical_devices.db) | Tệp SQLite cũ (2 bảng) nằm cạnh database chính `database/devices.db`. | Gây nhầm lẫn khi inspect database hoặc backup. | **LOW** | 0.1 Ngày |
| **TD-09** | Zero Auth / RBAC | Toàn bộ backend [`app/`](file:///C:/Users/tantt/Downloads/medical-device-app/app/) | Không có xác thực danh tính, không có token JWT, không phân quyền. | Bất kỳ ai trên mạng LAN đều có thể sửa/xóa thiết bị, hợp đồng. | **CRITICAL** | 2.0 Ngày |
| **TD-10** | Zero Automated Tests| Thư mục gốc dự án | Không có thư mục `tests/`, không có `pytest` suite, không có CI testing. | Nguy cơ hồi quy lỗi (regression bugs) cực cao khi sửa code. | **HIGH** | 2.0 Ngày |
| **TD-11** | Static Device Status | [`devices.status`](file:///C:/Users/tantt/Downloads/medical-device-app/database/schema.sql) | 100% (1.211/1.211) thiết bị ghi cứng `IN_SERVICE`, không phản ánh thực tế. | Báo cáo KPI thiết bị hỏng/đang sửa chữa bị sai lệch. | **MEDIUM** | 1.0 Ngày |
| **TD-12** | Unlinked Documents | Bảng `devices` | Các cột `pdf_path`, `md_path` để trống (0/1.211), đường dẫn lưu trong text `notes`. | Không thể tìm kiếm hoặc tải tài liệu một cách có cấu trúc. | **MEDIUM** | 1.0 Ngày |

---

## 2. PHÂN TÍCH CHI PHÍ NỢ (DEBT INTEREST & REMEDIATION MATRIX)

```
Mức độ rủi ro (Risk) vs Công sức xử lý (Effort):

     CAO ▲
         │ [TD-09: Auth & Security]     [TD-01: Backend Refactor]
         │                              [TD-02: Frontend Refactor]
 RỦI RO  │ [TD-07: Missing Table]       [TD-10: Automated Tests]
         │ [TD-06: Hardcoded Paths]     [TD-05: Script Sprawl]
         │                              [TD-11: Dynamic Status]
         │ [TD-08: Legacy DB]           [TD-12: Document Links]
         │ [TD-04: Duplicate HTML]      [TD-03: Activate api.js]
    THẤP ┼────────────────────────────────────────────────────►
         THẤP (< 0.5 Ngày)              CAO (> 2.0 Ngày)
                           CÔNG SỨC
```

---

## 3. CHIẾN LƯỢC TRẢ NỢ KỸ THUẬT THEO ĐỢT (REMEDIATION BATCHES)

1. **Đợt 1 — Quick Wins & Safe Cleanups (0.5 Ngày)**:
   * Xóa bỏ database rác `app/medical_devices.db`.
   * Gộp 2 tệp HTML giống hệt nhau (`web/sops.html` chuyển thành symbolic link hoặc redirect đến `web/quy_trinh_ttbyt.html`).
   * Chuyển các tệp JSON tạm nặng 60MB (`_link_fix_log.json`, `_link_fix_report.json`) ra khỏi git tracking vào `.gitignore`.
2. **Đợt 2 — Structural & Architectural Refactor (5.0 Ngày)**:
   * Tách `app/routes.py` thành các Sub-Routers, Services và Repositories.
   * Tách `web/js/app.js` thành các Modules ES6 và kích hoạt `web/js/api/client.js`.
   * Bổ sung bảng `work_orders` và cập nhật `database/schema.sql`.
   * Thay thế hardcoded paths bằng Pydantic Settings đọc từ `.env`.
3. **Đợt 3 — Security & Quality Gates (4.0 Ngày)**:
   * Thêm Authentication Middleware & JWT Token cho API.
   * Xây dựng bộ test suite chuẩn `pytest` phủ các nghiệp vụ cốt lõi.
   * Gom 101 scripts thành 4 thư mục tiêu chuẩn.
