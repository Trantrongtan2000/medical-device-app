# 🏥 BÁO CÁO NGHIÊN CỨU ĐỐI SÁNH PHẦN MỀM QUẢN LÝ THIẾT BỊ Y TẾ (HTM BENCHMARK) & KHUNG TÍNH NĂNG CHUYÊN SÂU

> **Đơn vị nghiên cứu:** Kỹ sư Trưởng Y Sinh & Chuyên gia Phần mềm Quản trị Y tế (Antigravity & OCX Claude)  
> **Nhánh phát triển:** `feat/htm-clinical-workflow-v3`  
> **Phạm vi đối sánh:** Nuvolo (ServiceNow HTM), Accruent TMS, Fluke Biomedical OneQA, SpeedMaint Cloud CMMS, Snipe-IT Healthcare Edition.  
> **Mục tiêu:** Bổ sung các tính năng cốt lõi, bám sát 100% Sổ tay 9 Quy trình chuẩn (SOPs) của Bệnh viện Quận 7 / PKĐK Tâm Anh Quận 7 và quy định Bộ Y Tế (NĐ 98/2021/NĐ-CP, TT 05/2022/TT-BYT).

---

## 1. KHUNG 4 PHÂN HỆ LÂM SÀNG CỐT LÕI ĐƯỢC CHỌN LỌC TRIỂN KHAI

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     🏆 KHUNG TÍNH NĂNG CHUYÊN SÂU PHẦN MỀM QUẢN LÝ TTBYT (V3)                     │
├─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────────────────┤
│     PHÂN HỆ 1       │     PHÂN HỆ 2       │     PHÂN HỆ 3       │           PHÂN HỆ 4             │
│   CÂY PHỤ KIỆN      │  BẢNG KIỂM AN TOÀN  │   ĐIỀU CHUYỂN MÁY   │      SEMANTICA CONTEXT GRAPH    │
│(Parent-Child Asset) │  ĐẦU NGÀY PRE-USE   │  KHOA PHÒNG (QT.08) │     (1.356 Nodes / 4.734 Edges) │
├─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────────────────┤
│• Quản lý Máy chính  │• Bảng kiểm 4 tiêu   │• Số hóa Biên bản    │• Đồ thị tri thức định hướng     │
│  $\leftrightarrow$  │  chí trước ca khám: │  điều chuyển giữa   │• Suy luận xác định không ảo     │
│  Đầu dò, Điện cực,  │  Nguồn điện/tiếp    │  21 Khoa phòng theo │  tưởng (Zero-Hallucination)     │
│  Lưỡi soi, Bộ UPS   │  địa, cơ khí, áp    │  Biểu mẫu BM08      │• Truy vết nguồn gốc W3C PROV-O  │
│• Serial độc lập     │  suất khí, Self-test│• Ghi vết Sổ lý lịch │  chỉ rõ PDF scan gốc            │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────────────────┘
```

---

## 2. CHI TIẾT TỪNG PHÂN HỆ LÂM SÀNG

### 📌 Phân Hệ 1: Cấu Trúc Phụ Kiện & Cấu Kiện Kèm Theo (Parent-Child Asset Hierarchy)
* **Cơ sở dữ liệu:** Bảng `device_accessories` trong SQLite.
* **Quy mô nạp thực tế:**
  * **24 Máy Siêu Âm CĐHA Q7:** Quản lý độc lập 90 đầu dò siêu âm (Convex 5C1/C252/C1-6-D, Linear 10L4/L442/L3-12-D/12L-RS, Phụ khoa 9EC4/IC9-RS/C41V1, Khối 3D/4D RAB6-RS/RAB2-6-RS) và 24 Bộ lưu điện UPS kèm số Serial.
  * **Máy Điện Trị Liệu BTL-4625:** Đầu phát rảnh tay `HandsFree Sono 4` (SN: `4474B05653`), điện cực cao su 5x7cm.
  * **Bộ Đặt Nội Khí Quản Video ClearVue VL3R:** Lưỡi soi MAC 2, MAC 3, MAC 4.

---

### 📌 Phân Hệ 2: Bảng Kiểm Tra An Toàn Vận Hành Đầu Ngày (Daily Pre-use Checklist)
* **Cơ sở dữ liệu:** Bảng `pre_use_inspections`.
* **Tiêu chuẩn an toàn:** Cho phép Điều dưỡng / Kỹ thuật viên xác nhận 4 thông số an toàn đầu ngày trước khi tiếp nhận bệnh nhân:
  1. `power_ok`: Nguồn điện lưới & Bộ lưu điện UPS ổn định.
  2. `physical_ok`: Vỏ máy, dây dẫn, đầu dò không nứt gãy.
  3. `gas_pressure_ok`: Áp suất khí y tế trung tâm đạt chuẩn 4-5 bar (O2, Air, Vac).
  4. `selftest_ok`: Chương trình tự kiểm tra khởi động của máy báo `PASS`.

---

### 📌 Phân Hệ 3: Quy Trình Điều Chuyển Thiết Bị Giữa Các Khoa Phòng (`QT.08`)
* **Cơ sở dữ liệu:** Bảng `device_transfers`.
* **Biểu mẫu chuẩn:** `BM08_TA5.TTBYT.QT.08` *(Biên bản điều chuyển thiết bị nội bộ)*.
* **Cơ chế hoạt động:** Ghi nhận bên giao, bên nhận, lý do điều chuyển và tự động cập nhật vị trí khoa phòng mới của thiết bị trong Master Registry và Semantica Graph.

---

### 📌 Phân Hệ 4: Đồ Thị Tri Thức Ngữ Nghĩa Semantica AGI & W3C PROV-O
* **Quy mô:** **1.356 Nodes & 4.734 Edges**.
* **Đặc tính:** Cung cấp chuỗi giải trình nguyên nhân - kết quả (Causal Provenance Chain) cho từng tài sản kỹ thuật lâm sàng.
