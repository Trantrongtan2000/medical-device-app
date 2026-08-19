# Feature Specification: HTM Clinical Workflow v3 & Executive Overview Dashboard

- **Feature ID:** `004-htm-clinical-workflow-v3`
- **Created:** 2026-08-19
- **Status:** `COMPLETED`
- **Target Standards:** Bộ Y Tế (Nghị định 98/2021/NĐ-CP, Thông tư 05/2022/TT-BYT), SpeedMaint CMMS, Snipe-IT, Google Stitch, leonxlnx/taste-skill, cathrynlavery/diagram-design, W3C PROV-O.

---

## 1. Executive Summary & Goals
Xây dựng và nâng cấp hệ thống Quản lý Trang Thiết Bị Y Tế (BV Quận 7 / PKĐK Tâm Anh Q7) lên chuẩn **Clinical-Grade HTM Workflow v3**:
1. **Executive Overview Dashboard (Tab 0):** Bổ sung trang Dashboard tổng quan điều phối toàn viện với 4 KPI scorecards, biểu đồ phân bổ thiết bị 21 khoa phòng (Chart.js), biểu đồ cơ cấu rủi ro A/B/C/D, nhật ký lâm sàng thời gian thực và danh bạ khẩn cấp 24/7.
2. **Clinical Kanban Board:** Tích hợp bảng Kanban 4 cột trực quan theo dõi tiến độ công việc lâm sàng (*1. Chờ tiếp nhận, 2. Đang xử lý, 3. Chờ nghiệm thu, 4. Đã hoàn tất*).
3. **Taste-Skill Design System (Anti-AI Slop):** Thiết kế giao diện tiết chế, phông chữ Plus Jakarta Sans & JetBrains Mono (`tabular-nums`), nền Midnight Slate Navy (`#090d16`), viền sắc nét `1px solid #cbd5e1`.
4. **Solid High-Contrast Risk Badges (A, B, C, D):** Huy hiệu phân loại rủi ro nền màu đậm bão hòa với chữ trắng tinh (`#ffffff`, font-weight 800) loại bỏ hoàn toàn lỗi chìm/mờ chữ vào nền.
5. **Supplier & Facility Tags:** Bổ sung các nhãn thẻ Nhà Cung Cấp (24 nhà thầu) và Khoa/Phòng Ban tại từng dòng danh mục và Header của Bảng Hồ Sơ Lý Lịch (Device Passport Modal).
6. **Điều Chỉnh Thông Tin Thiết Bị (Edit Asset Modal & API):** Nút chỉnh sửa trực tiếp và Modal form cập nhật đầy đủ metadata kỹ thuật, tự động kiểm tra trùng số Serial và ghi nhật ký Audit Trail.
7. **Tổ chức lại Sidebar Menu:** Phân thành 4 nhóm chức năng logic (*Điều hành tổng thể, Danh mục & Đối tác, Quy trình lâm sàng, CMMS & Trí tuệ nhân tạo*), bổ sung 2 phân hệ *Nhà Cung Cấp & HĐ* và *Lịch Bảo Trì & Kiểm Định*.

---

## 2. Detailed Functional Requirements

### FR-01: Executive Overview Dashboard & Analytics
- **Top Scorecards:** 1.073 tài sản, 98.6% tỷ lệ sẵn sàng vận hành (1.058 máy Online), 94.2% kiểm định đạt chuẩn (8 máy cần tái kiểm trong 30 ngày), 8/8 xe cấp cứu E-Cart trực chiến 24/7.
- **Interactive Department Chart:** Biểu đồ thanh ngang/cột thể hiện phân bổ thiết bị trên 21 khoa phòng.
- **Risk Breakdown Donut Chart:** Tỷ lệ phần trăm 4 nhóm rủi ro A (35%), B (25%), C (30%), D (10%).
- **Live Audit Trail:** Nhật ký 5 sự kiện lâm sàng mới nhất.

### FR-02: 4-Column Clinical Kanban Board
- **Cột 1 (Chờ Tiếp Nhận):** Báo hỏng khẩn cấp, yêu cầu kiểm định định kỳ, đề xuất điều chuyển.
- **Cột 2 (Đang Xử Lý):** Kỹ sư đang thực hiện bảo dưỡng PM định kỳ, sửa chữa thay thế phụ kiện.
- **Cột 3 (Chờ Nghiệm Thu):** Biên bản nghiệm thu BM04 sau sửa chữa, giấy chứng nhận kiểm định mới chờ dán tem.
- **Cột 4 (Đã Hoàn Tất):** Thiết bị đã bàn giao và đưa vào sử dụng an toàn.

### FR-03: Device Passport Modal & Live Editing
- 5 Tab nghiệp vụ: Thông tin chung, Cây cấu kiện & đầu dò rời (Parent-Child), Giấy chứng nhận kiểm định, Sổ lý lịch máy BM05, và Semantica W3C PROV-O Causal Chain.
- Nút "Điều Chỉnh Thông Tin" mở Modal Form gọi `PUT /api/devices/{id}`.
- Nút "In Tem Nhãn QR Code" hỗ trợ in nhãn tài sản dán máy ngay tại khoa phòng.

### FR-04: High-Contrast Accessibility (WCAG AAA)
- Khóa cứng màu nền và màu chữ bằng Solid CSS Classes & Inline DOM Styles.
- Thẻ KPI Sidebar dùng nền kính tối với nhãn chữ sáng Slate-200 và số liệu Neon Green/White.
