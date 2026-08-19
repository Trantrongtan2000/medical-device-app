# 📊 BÁO CÁO NGUỒN CHÂN LÝ DỮ LIỆU (DATA SOURCE OF TRUTH)
## MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3) — BV QUẬN 7

> **Nguyên tắc thẩm quyền:** Không được giả định tài liệu tĩnh hay báo cáo cũ là đúng. Nguồn chân lý tối cao về dữ liệu lâm sàng là **MasterData V6** được lưu trữ chuẩn hóa trong CSDL quan hệ `database/devices.db`. Mọi số liệu thống kê phải được truy vấn động từ CSDL này.

---

## 1. BẢNG ĐỐI CHIẾU NGUỒN CHÂN LÝ & PHÂN TÍCH XUNG ĐỘT SỐ LIỆU

| Thực Thể (Entity) | Nguồn Dữ Liệu (Source) | Số Lượng (Count) | Thời Điểm (Timestamp) | Có Thẩm Quyền? (Authoritative?) | Phân Tích Nguyên Nhân & Vấn Đề (Issue & Root Cause) |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Thiết bị (Devices)** | `database/devices.db` (bảng `devices`) | **1.211** | 19/08/2026 | **CHÍNH THỨC (YES)** | Tổng hợp đầy đủ từ MasterData V6 (đã bao gồm toàn bộ trang thiết bị 39 khoa phòng). |
| | `MasterData_V6_V1.0.xlsm` | 1.211 | 18/08/2026 | **NGUỒN GỐC (YES)** | Tệp Excel nguồn của Bệnh viện được chuẩn hóa và import vào CSDL. |
| | `docs/DANH_MUC_THIET_BI_Y_TE_BVQ7.md` | 1.049 | 15/08/2026 | **KHÔNG (NO - STALE)** | Bản snapshot cũ tạo ở giai đoạn đầu, chưa bao gồm các thiết bị bổ sung của phòng khám. |
| | `README.md` | 1.049 | 15/08/2026 | **KHÔNG (NO - STALE)** | Tài liệu chưa được cập nhật sau đợt nạp dữ liệu MasterData V6. |
| | Các báo cáo cũ (`CODE_AUDIT_REPORT.md`) | 1.052 / 1.073 | 16-17/08/2026 | **KHÔNG (NO - STALE)** | Các mốc snapshot trung gian trong quá trình lọc trùng lặp dữ liệu OCR. |
| | UI Counters (`web/index.html`) | 1.211 | 19/08/2026 | **ĐỒNG BỘ (YES)** | Badge hiển thị đã được cập nhật khớp với số lượng thực tế trong CSDL. |
| **Hợp đồng (Contracts)** | `database/devices.db` (bảng `contracts`) | **198** | 19/08/2026 | **CHÍNH THỨC (YES)** | Danh mục 198 Hợp đồng mua sắm thực tế ký kết với các hãng và nhà thầu y tế. |
| | Báo cáo kiểm toán cũ (`docs/`) | 24 | 16/08/2026 | **KHÔNG (NO - STALE)** | Chỉ thống kê 24 hợp đồng trọng điểm có hồ sơ scan OCR chi tiết ở giai đoạn 1. |
| **Nhà cung cấp (Suppliers)** | `database/devices.db` (bảng `supplier_contacts`) | **102** | 19/08/2026 | **CHÍNH THỨC (YES)** | Danh bạ 102 nhà cung cấp, đại diện phân phối chính thức tại Việt Nam. |
| | Báo cáo kiểm toán cũ (`docs/`) | 45 | 16/08/2026 | **KHÔNG (NO - STALE)** | Danh sách rút gọn 45 nhà cung cấp có thông tin liên hệ khẩn cấp ở giai đoạn 1. |
| **Khoa / Phòng ban (Facilities)**| `database/devices.db` (bảng `facilities`) | **39** | 19/08/2026 | **CHÍNH THỨC (YES)** | Toàn bộ 39 Khoa, Phòng chức năng, Khu cận lâm sàng và Phòng khám tại cơ sở Q7. |
| | `docs/DANH_MUC_THIET_BI_Y_TE_BVQ7.md` | 22 | 15/08/2026 | **KHÔNG (NO - STALE)** | Chỉ tính 22 khoa lâm sàng chính, bỏ sót các phòng ban phụ trợ và kho lưu trữ. |
| **Kiểm định / Hiệu chuẩn** | `database/devices.db` (`calibration_certificates`) | **107** | 19/08/2026 | **CHÍNH THỨC (YES)** | 107 giấy chứng nhận kiểm định an toàn bức xạ & TT 05/2022/TT-BYT thực tế có scan. |
| | `docs/DANH_MUC_THIET_BI_Y_TE_BVQ7.md` | 104 | 15/08/2026 | **KHÔNG (NO - STALE)** | Thiếu 3 chứng chỉ bổ sung mới quét đợt sau. |
| | Một số ghi chú OCR scan | 329 | 17/08/2026 | **KHÔNG (NO - UNVERIFIED)**| Tính gộp cả các trang phụ lục biên bản kiểm tra kỹ thuật không phải GCN chính thức. |
| **Bảo trì / Sửa chữa** | `database/devices.db` (`maintenance_logs`) | **48** | 19/08/2026 | **CHÍNH THỨC (YES)** | Nhật ký bảo dưỡng định kỳ PM (theo quy trình QT.06). |
| | Bảng `work_orders` (Phiếu sửa chữa) | 0 (Bảng chưa tạo) | 19/08/2026 | **LỖI THIẾU (MISSING)** | Bảng `work_orders` bị thiếu trong SQLite; dữ liệu phiếu sửa chữa chưa được lưu trữ. |
| **Tài liệu PDF & Markdown** | Cây thư mục `G:\BV QUẬN 7_OCR_WORK_20260712` | **10.937 file MD** | 19/08/2026 | **CHÍNH THỨC (YES)** | Kho văn bản số hóa OCR đã được đóng gói thành `BV_QUAN_7_OCR_MD_ONLY.zip`. |
| | Bảng `devices` (`pdf_path`, `md_path`) | 0 / 1.211 | 19/08/2026 | **LỖI LIÊN KẾT (BROKEN)**| Các trường `pdf_path` và `md_path` để trống; đường dẫn tài liệu nằm rải rác trong `notes`. |

---

## 2. QUY ĐỊNH NGUỒN CHÂN LÝ CHO TỪNG THUỘC TÍNH (CANONICAL ATTRIBUTES)

| Thuộc Tính | Nguồn Thẩm Quyền (Canonical Source) | Quy Chuẩn Định Dạng / Ràng Buộc |
| :--- | :--- | :--- |
| **Mã Định Danh (Asset Tag)** | CSDL `devices.asset_tag` | Định dạng chuẩn: `BVQ7-TTB-XXXXX` (Duy nhất toàn viện). |
| **Mã Quản Lý (SpeedMaint Code)**| CSDL `devices.speedmaint_code` | Định dạng: `BM/BVQ7/XXXXX` (Map trực tiếp với CMMS Hoàn Mỹ). |
| **Số Serial (S/N)** | CSDL `devices.serial_no` | Số Serial khắc trên thân máy vật lý; không được trùng lặp cho 2 thiết bị khác loại. |
| **Tên Thiết Bị & Model** | CSDL `devices.device_name`, `devices.model` | Chuẩn hóa theo danh mục Bộ Y Tế & nhãn hiệu nhà sản xuất. |
| **Phân Loại Rủi Ro** | CSDL `devices.risk_level` | Chỉ chấp nhận 4 giá trị: `A`, `B`, `C`, `D` (Nghị định 98/2021/NĐ-CP & TT 05/2022). |
| **Khoa / Vị Trí Lắp Đặt** | CSDL `devices.facility_id` $\rightarrow$ `facilities.id` | Ràng buộc khóa ngoại bắt buộc với bảng `facilities` (39 khoa phòng). |
| **Hợp Đồng & Nhà Thầu** | CSDL `devices.contract_no` $\rightarrow$ `contracts.contract_no` | Ràng buộc khóa ngoại với bảng `contracts` và `supplier_contacts`. |
| **Trạng Thái Vận Hành** | CSDL `devices.status` | Giá trị động: `IN_SERVICE`, `UNDER_MAINTENANCE`, `CALIBRATION_PENDING`, `RETIRED`. |

---

## 3. CƠ CHẾ BẢO ĐẢM TÍNH ĐỒNG BỘ NGUỒN CHÂN LÝ

1. **Cấm Hardcode Số Liệu Tĩnh Trong Code & Tài Liệu**:
   * Tuyệt đối không ghi cứng số lượng "1.049", "1.211", "198" vào các tệp giao diện HTML hoặc Markdown.
   * Mọi màn hình UI, Báo cáo Tổng quan và API xuất dữ liệu phải thực hiện câu truy vấn `SELECT COUNT(*) FROM table` tại thời gian thực.
2. **Cơ Chế Dynamic Markdown Generator**:
   * Xây dựng script trong `scripts/maintenance/generate_danh_muc_md.py` để tự động render lại `docs/DANH_MUC_THIET_BI_Y_TE_BVQ7.md` từ CSDL SQLite bất cứ khi nào có thay đổi dữ liệu master.
3. **Validation Khóa Ngoại Tự Động (Strict FK Enforcement)**:
   * Kích hoạt `PRAGMA foreign_keys = ON;` trên 100% kết nối database. Không cho phép tạo thiết bị có `facility_id` hoặc `contract_no` không tồn tại trong danh mục cha.
