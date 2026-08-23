# Constitution of Medical Device Management System (BV Quận 7 / PKĐK Tâm Anh Q7)

## 1. Mục Đích & Phạm Vi
Hệ thống Quản Lý Trang Thiết Bị Y Tế phục vụ công tác quản lý tài sản, kiểm soát an toàn người bệnh, điều chuyển lâm sàng, bảo trì phòng ngừa (PM), và tuân thủ các quy định y tế nghiêm ngặt của Bộ Y Tế Việt Nam.

## 2. Bộ Quy Chuẩn & Tiêu Chuẩn Y Tế Áp Dụng
1. **Nghị định 98/2021/NĐ-CP & Nghị định 07/2023/NĐ-CP:**
   - 4 mức phân loại rủi ro bắt buộc: **Loại A (Rủi ro rất thấp)**, **Loại B (Rủi ro thấp)**, **Loại C (Rủi ro trung bình cao)**, **Loại D (Rủi ro đặc biệt cao)**.
2. **Thông tư 05/2022/TT-BYT & Quyết định 2429/QĐ-BYT:**
   - Quy định bắt buộc về kiểm định, hiệu chuẩn định kỳ thiết bị y tế và cảnh báo hạn kiểm định trước 30 ngày.
3. **Quy trình Sổ Tay 10 SOPs Chuẩn (36. TRANG THIET BI Y TE):**
   - `QT.01` & `QT.02`: Vận hành, bảo dưỡng & hoàn nguyên hệ thống RO Thận nhân tạo.
   - `QT.03`: Vận hành & kiểm tra an toàn hệ thống Khí y tế trung tâm.
   - `QT.04`: Bàn giao, nghiệm thu đưa vào sử dụng (`BM04`) & Sổ lý lịch máy (`BM05`).
   - `QT.05`: Vận hành, sử dụng & bảo quản thiết bị y tế.
   - `QT.06`: Bảo trì định kỳ (PM) & Sửa chữa đột xuất (SpeedMaint CMMS).
   - `QT.07`: Quy trình đề xuất & hội đồng thanh lý thiết bị.
   - `QT.08`: Quy trình & biên bản điều chuyển thiết bị giữa các khoa phòng (`BM03`).
   - `QT.09`: Quy trình giao nhận, kiểm đếm bình khí y tế di động.
   - `CS.TTBYT.04`: Quy trình kiểm tra, hiệu chuẩn & kiểm định thiết bị y tế.

## 3. Kiến Trúc Dữ Liệu & Quy Tắc Định Danh
- **Mã Định Danh Kép Bắt Buộc:**
  - Asset Tag chuẩn Snipe-IT: `BVQ7-TTB-XXXXX` (5 chữ số)
  - SpeedMaint Code: `BM/BVQ7/XXXXX` (5 chữ số)
- **Tính Duy Nhất Của Số Serial (S/N):** Khóa `UNIQUE` trên toàn hệ thống viện; không cho phép 2 thiết bị khác nhau trùng số Serial.
- **Cấu Trúc Phụ Kiện / Cấu Kiện Rời (Parent-Child Hierarchy):** Đầu dò siêu âm (CV1-8A, CA1-7S, LA2-9A...), UPS dự phòng, sensor SPO2... được quản lý gắn liền với thiết bị chính.

## 4. Quy Chuẩn Thiết Kế Giao Diện (Taste-Skill & Google Stitch)
- **Anti-AI Slop:** Loại bỏ các gradient sặc sỡ, đổ bóng dày; tuân thủ sự tiết chế, thẩm mỹ xuất bản (Editorial Design).
- **Typography:** Plus Jakarta Sans cho giao diện chính, JetBrains Mono với `tabular-nums` cho các bảng số liệu, mã định danh và số Serial.
- **Accessibility:** Khóa cứng độ tương phản cao (WCAG AAA) cho huy hiệu rủi ro A, B, C, D (Solid Colors, chữ trắng `#ffffff`).
