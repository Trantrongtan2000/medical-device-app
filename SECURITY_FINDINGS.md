# 🔒 BÁO CÁO ĐÁNH GIÁ AN NINH & BẢO MẬT (SECURITY FINDINGS)
## MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3) — BV QUẬN 7

> **Phạm vi kiểm toán:** Toàn bộ API Endpoints, Cơ chế xác thực & phân quyền, Quản lý Secret Keys AI, Lưu trữ mật khẩu, Nguy cơ Path Traversal, SQL Injection, và Cấu hình CORS.

---

## 1. TỔNG HỢP LỖ HỔNG BẢO MẬT (SECURITY VULNERABILITY MATRIX)

| Mã Lỗ Hổng | Tên Lỗ Hổng (Vulnerability) | Mức Độ (Severity) | Vị Trí Phát Hiện (Location) | Bằng Chứng Thực Tế (Evidence) | Rủi Ro Khai Thác (Exploitation Risk) |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **SEC-01** | Missing Authentication & RBAC | **CRITICAL** | Toàn bộ 85 Endpoints trong [`app/routes.py`](file:///C:/Users/tantt/Downloads/medical-device-app/app/routes.py) | Không có dependency `Depends(get_current_user)`; các endpoint `DELETE /api/contracts/{id}`, `DELETE /api/staff/{id}` mở tự do. | Bất kỳ ai truy cập IP mạng LAN đều có thể xóa toàn bộ dữ liệu thiết bị và hợp đồng. |
| **SEC-02** | Path Traversal / Arbitrary File Read | **HIGH** | Endpoint `/api/pdf/view` trong [`app/routes.py`](file:///C:/Users/tantt/Downloads/medical-device-app/app/routes.py) | Nhận tham số đường dẫn trực tiếp mà không kiểm tra (whitelist) thư mục gốc an toàn. | Kẻ tấn công có thể truyền `path=../../` để đọc các tệp cấu hình nhạy cảm trên máy chủ. |
| **SEC-03** | Insecure API Key Storage | **HIGH** | Bảng `api_keys_config` & [`app/key_rotator.py`](file:///C:/Users/tantt/Downloads/medical-device-app/app/key_rotator.py) | API Keys của Gemini / Mistral được lưu dạng plain text trong SQLite và từng bị ghi vào file log transcript. | Rò rỉ token trả phí hoặc bị kẻ xấu lợi dụng quota API của bệnh viện. |
| **SEC-04** | Overly Permissive CORS Policy | **MEDIUM** | [`app/main.py`](file:///C:/Users/tantt/Downloads/medical-device-app/app/main.py) | `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`. | Cho phép bất kỳ website thứ 3 nào thực hiện Cross-Origin Requests đến API nội bộ bệnh viện. |
| **SEC-05** | Information Disclosure via Hardcoded Paths | **MEDIUM** | [`app/routes.py#L28-L33`](file:///C:/Users/tantt/Downloads/medical-device-app/app/routes.py#L28-L33) | Hardcode đường dẫn máy tính cá nhân `C:\Users\tantt\...` và ổ đĩa `G:\...`. | Lộ cấu trúc thư mục nội bộ; hệ thống bị sập khi triển khai lên máy chủ Linux/Docker. |
| **SEC-06** | Dynamic SQL Concatenation Risk | **MEDIUM** | Hàm `apply_snipe_status_type` trong [`app/routes.py#L43-L59`](file:///C:/Users/tantt/Downloads/medical-device-app/app/routes.py#L43-L59) | Ghép chuỗi SQL điều kiện động dạng `conditions.append(...)`. | Dễ phát sinh lỗi cú pháp SQL hoặc tiềm ẩn nguy cơ SQL Injection nếu tham số không được validate chặt. |

---

## 2. KẾ HOẠCH KHẮC PHỤC BẢO MẬT CHI TIẾT (SECURITY REMEDIATION)

### Giải pháp cho SEC-01: Triển khai JWT Authentication & Role-Based Access Control (RBAC)
* **Thiết kế 4 vai trò người dùng (Roles)**:
  1. `ADMIN` (Trưởng phòng TTBYT / Ban Giám Đốc): Toàn quyền quản trị, xóa, sửa, cấu hình hệ thống và API keys.
  2. `BME_ENGINEER` (Kỹ sư Y sinh): Tạo mới thiết bị, ghi nhật ký bảo trì PM, lập phiếu sửa chữa, điều chuyển thiết bị.
  3. `CLINICAL_STAFF` (Điều dưỡng / Bác sĩ các khoa): Xem thông tin thiết bị khoa mình, báo hỏng thiết bị, gửi góp ý.
  4. `AUDITOR` (Kiểm toán viên y tế): Quyền chỉ đọc (Read-Only) để tra cứu và xuất báo cáo.
* **Middleware bảo vệ**:
  ```python
  # app/core/security.py
  from fastapi import Depends, HTTPException, status
  from fastapi.security import OAuth2PasswordBearer
  
  oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
  
  def require_role(allowed_roles: list[str]):
      def role_checker(current_user: User = Depends(get_current_user)):
          if current_user.role not in allowed_roles:
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ thẩm quyền thao tác!")
          return current_user
      return role_checker
  ```

### Giải pháp cho SEC-02: Ngăn chặn triệt để lỗ hổng Path Traversal
* **Kiểm tra tính an toàn của đường dẫn tệp (Safe Path Whitelisting)**:
  ```python
  # app/services/document_service.py
  from pathlib import Path
  
  ALLOWED_STORAGE_ROOT = Path(os.environ.get("STORAGE_ROOT", "data/documents")).resolve()
  
  def resolve_safe_document_path(relative_path: str) -> Path:
      target_path = (ALLOWED_STORAGE_ROOT / relative_path).resolve()
      # Kiểm tra đường dẫn đích có nằm trong thư mục gốc cho phép hay không
      if not target_path.is_relative_to(ALLOWED_STORAGE_ROOT):
          raise HTTPException(status_code=400, detail="Truy cập đường dẫn không hợp lệ!")
      if not target_path.exists():
          raise HTTPException(status_code=404, detail="Không tìm thấy tệp tài liệu!")
      return target_path
  ```

### Giải pháp cho SEC-03: Cách ly và Mã hóa Secret Keys
1. **Lưu trữ qua biến môi trường (`.env`)**:
   * Khóa API mặc định chỉ đọc từ biến môi trường `GEMINI_API_KEY`, `MISTRAL_API_KEY`.
2. **Mã hóa Database Vault**:
   * Nếu người dùng nhập thêm API key qua giao diện quản trị, key phải được mã hóa AES-256 trước khi ghi vào SQLite và giải mã trong bộ nhớ lúc gọi API.
3. **Bộ lọc tự động (Output Sanitizer)**:
   * 100% phản hồi API và nhật ký hệ thống phải chạy qua bộ lọc regex để che giấu (mask) token: `ya29.***`, `AIzaSy***`.
