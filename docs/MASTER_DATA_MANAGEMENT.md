# 🏛️ HỒ SƠ HỆ THỐNG DỮ LIỆU MASTER (MASTER DATA MANAGEMENT)
**BỆNH VIỆN QUẬN 7 / PHÒNG KHÁM ĐA KHOA TÂM ANH QUẬN 7**

> **Phiên bản:** 2.0.0 (Snipe-IT & SpeedMaint Cloud CMMS Edition)  
> **Thời điểm cập nhật:** 19/08/2026 07:23:28  
> **Cơ sở pháp lý:** Nghị định 98/2021/NĐ-CP, Thông tư 05/2022/TT-BYT, Tiêu chuẩn ISO 13485, Sổ tay Quy trình TTBYT.

---

## 1. TỔNG QUAN CƠ CẤU DỮ LIỆU MASTER

| Thực Thể Master | Tổng Bản Ghi | Khóa Chính (PK) | Mã Nhận Diện Chuẩn Hóa | Ràng Buộc Tính Toàn Vẹn |
| :--- | :---: | :--- | :--- | :--- |
| **Thiết Bị Y Tế (`devices`)** | **1,052** | `id` (INTEGER) | `BVQ7-TTB-XXXXX` & `BM/BVQ7/XXXXX` | `serial_no UNIQUE NOT NULL`, `risk_level IN ('A','B','C','D')` |
| **Khoa / Phòng Ban (`facilities`)** | **22** | `id` (INTEGER) | `code` (VARCHAR) | Quan hệ 1-N với `devices.facility_id` |
| **Nhóm Thiết Bị (`device_categories`)** | **10** | `id` (INTEGER) | `name` (TEXT) | Quan hệ 1-N với `devices.category_id` |
| **Giấy Chứng Nhận KĐ (`calibration_certificates`)** | **107** | `id` (INTEGER) | `certificate_no` | Khóa ngoại `device_id`, Cảnh báo 3 cấp độ KĐ |
| **Nhật Ký & Work Orders (`maintenance_logs`)** | **9** | `id` (INTEGER) | `#2607XX` (SpeedMaint Task) | Audit Trail `INSPECTION`, `HANDOVER`, `PREVENTIVE`, `REPAIR` |

---

## 2. PHÂN BỔ 4 MỨC ĐỘ RỦI RO THEO NGHỊ ĐỊNH 98/2021/NĐ-CP

* 🟢 **Mức A (Rủi ro rất thấp):** 851 thiết bị (80.9%) — Huyết áp kế, nhiệt ẩm kế, cân y tế, ống nghe.
* 🟡 **Mức B (Rủi ro trung bình thấp):** 71 thiết bị (6.7%) — Monitor 5 thông số, máy điện tim ECG, bơm tiêm điện.
* 🟠 **Mức C (Rủi ro trung bình cao):** 90 thiết bị (8.6%) — Máy siêu âm màu Doppler, máy chạy thận nhân tạo Fresenius, dao mổ điện cao tần.
* 🔴 **Mức D (Rủi ro đặc biệt cao):** 40 thiết bị (3.8%) — Máy thở chức năng cao ICU, máy phá rung tim, hệ thống gây mê kèm thở.

---

## 3. DANH SÁCH 22 KHOA / PHÒNG BAN VÀ QUY MÔ TÀI SẢN

| STT | Tên Khoa / Phòng Ban | Mã Khoa | Số Lượng Thiết Bị | Tỷ Lệ Toàn Viện |
| :---: | :--- | :---: | :---: | :---: |
| 01 | **Khoa/Phòng Chưa Phân Loại** | `KHOAPH` | 952 máy | 90.5% |
| 02 | **Khoa Khám Bệnh** | `KHOAKH` | 31 máy | 2.9% |
| 03 | **Khoa Chẩn Đoán Hình Ảnh** | `KHOACH` | 22 máy | 2.1% |
| 04 | **KHOA CẤP CỨU** | `KHOACP` | 20 máy | 1.9% |
| 05 | **KHOA NỘI SOI TIÊU HOÁ** | `KHOANI` | 4 máy | 0.4% |
| 06 | **CẤP CỨU-ĐƠN VỊ LỌC MÁU** | `CPCUNV` | 3 máy | 0.3% |
| 07 | **PHÒNG KHÁM ĐA KHOA** | `PHNGKH` | 3 máy | 0.3% |
| 08 | **CHẨN ĐOÁN HÌNH ẢNH** | `CHNONH` | 2 máy | 0.2% |
| 09 | **Phòng 3002 khu da liễu** | `PHNG30` | 2 máy | 0.2% |
| 10 | **KHOA LỌC MÁU** | `KHOALC` | 1 máy | 0.1% |
| 11 | **KHOA MẮT** | `KHOAMT` | 1 máy | 0.1% |
| 12 | **KHOA UNG BƯỚU** | `KHOAUN` | 1 máy | 0.1% |
| 13 | **KIỂM SOÁT NHIỄM KHUẨN** | `KIMSOT` | 1 máy | 0.1% |
| 14 | **Khoa Kiểm Soát Nhiễm Khuẩn** | `KHOAKI` | 1 máy | 0.1% |
| 15 | **NHÀ THUỐC** | `NHTHUC` | 1 máy | 0.1% |
| 16 | **NỘI SOI TIÊU HÓA** | `NISOIT` | 1 máy | 0.1% |
| 17 | **P.TTB Q7** | `PTTBQ7` | 1 máy | 0.1% |
| 18 | **Phòng Trang Thiết Bị Y Tế** | `PHNGTR` | 1 máy | 0.1% |
| 19 | **Quầy đánh giá ban đầu – Trung tâm thẩm mỹ** | `QUYNHG` | 1 máy | 0.1% |
| 20 | **XÉT NGHIỆM** | `XTNGHI` | 1 máy | 0.1% |
| 21 | **CẤP CỨU** | `CPCU` | 0 máy | 0.0% |
| 22 | **KHÁM BỆNH - MẮT** | `KHMBNH` | 0 máy | 0.0% |

---

## 4. DANH SÁCH 10 NHÓM THIẾT BỊ Y TẾ CHUYÊN KHOA

| STT | Nhóm Danh Mục Thiết Bị | Cấp Độ An Toàn | Số Lượng Thiết Bị |
| :---: | :--- | :---: | :---: |
| 01 | **Thiết bị y tế khác** | Mức Basic | 478 máy |
| 02 | **Dụng cụ đo lường y tế** | Mức Basic | 431 máy |
| 03 | **Thận nhân tạo & Lọc máu** | Mức Critical | 43 máy |
| 04 | **Theo dõi bệnh nhân & Điện tim** | Mức Advanced | 21 máy |
| 05 | **Thiết bị xét nghiệm & lab** | Mức Advanced | 19 máy |
| 06 | **Cấp cứu & Máy phá rung tim** | Mức Critical | 17 máy |
| 07 | **Thiết bị tiệt trùng & khử khuẩn** | Mức Advanced | 16 máy |
| 08 | **Máy thở & Hô hấp** | Mức Critical | 14 máy |
| 09 | **Phẫu thuật & Dao mổ điện** | Mức Critical | 13 máy |
| 10 | **Chẩn đoán hình ảnh** | Mức Critical | 0 máy |

---

## 5. CÁC TỆP DỮ LIỆU MASTER ĐÃ XUẤT BẢN:
* 📄 **Master Device CSV:** `database/master_device_registry.csv` (1.052 dòng có UTF-8 BOM mở bằng Excel không lỗi font).
* 📑 **Data Dictionary JSON:** `database/master_data_dictionary.json`.
* 🗄️ **Primary SQLite DB:** `database/devices.db` (WAL mode enabled).
