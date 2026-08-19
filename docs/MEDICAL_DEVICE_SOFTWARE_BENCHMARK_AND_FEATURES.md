# 🏥 BÁO CÁO NGHIÊN CỨU ĐỐI SÁNH PHẦN MỀM QUẢN LÝ THIẾT BỊ Y TẾ (HTM/CMMS BENCHMARK) & ĐỀ XUẤT TÍNH NĂNG CHUYÊN SÂU

> **Đơn vị nghiên cứu:** Kỹ sư Trưởng Y Sinh & Chuyên gia Phần mềm Quản trị Y tế (Antigravity & OCX Claude)  
> **Phạm vi đối sánh:** Các giải pháp Quản lý Kỹ thuật Y sinh (Healthcare Technology Management - HTM) hàng đầu thế giới và tại Việt Nam: **Nuvolo (ServiceNow), Accruent TMS, Fluke Biomedical OneQA, SpeedMaint Cloud CMMS, Snipe-IT Healthcare Edition**.  
> **Mục tiêu:** Bổ sung các tính năng cốt lõi, bám sát 100% Sổ tay 9 Quy trình chuẩn (SOPs) của Bệnh viện Quận 7 / PKĐK Tâm Anh Quận 7 và quy định Bộ Y Tế (NĐ 98/2021/NĐ-CP, TT 05/2022/TT-BYT).

---

## 1. BẢNG ĐỐI SÁNH TÍNH NĂNG CÁC PHẦN MỀM TIÊU BIỂU TRÊN THẾ GIỚI & VIỆT NAM

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               🏆 HỆ SINH THÁI PHẦN MỀM QUẢN LÝ TTBYT                              │
├─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────────────────┤
│   NUVOLO (USA)      │   ACCRUENT TMS      │ SPEEDMAINT CMMS (VN)│   SNIPE-IT (ASSET MANAGEMENT)   │
│  (ServiceNow HTM)   │(Biomedical Engine)  │(Hoàn Mỹ / BV Quốc Tế│   (Open Source Enterprise)      │
├─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────────────────┤
│• Quản lý tài sản số │• Cấu trúc Cha - Con │• Báo hỏng qua QR Bed│• Quản lý Decal / Mã vạch / QR   │
│• Work Order lâm sàng│ (Parent-Child Asset)│• Điều phối Kỹ sư    │• Quản lý Phụ kiện & Cấu kiện    │
│• Quản lý cảnh báo từ│• Checklist bảo dưỡng│• Nhật ký bảo trì PM │• Quản lý Cấp phát & Thu hồi     │
│  FDA / Hãng sản xuất│  tự động (AAMI/NFPA)│• Báo cáo ban Giám Đốc│• Nhật ký Kiểm toán (Audit Logs) │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────────────────┘
```

| Nhóm Tính Năng Trọng Yếu | Nuvolo (USA) | Accruent TMS | SpeedMaint (VN) | Snipe-IT | Đề Xuất Áp Dụng Cho BV Quận 7 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Mô hình Phụ Kiện Cấu Kiện (Parent-Child Asset)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **TÍCH HỢP NGAY**: Quản lý Máy chính $\leftrightarrow$ Đầu dò siêu âm, Dây cáp, Điện cực, Lưỡi đèn soi. |
| **2. Sổ Lý Lịch Máy Điện Tử (Device Passport)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | **TÍCH HỢP NGAY**: Theo dõi trọn vòng đời từ Hợp đồng $\rightarrow$ Bàn giao $\rightarrow$ Sửa chữa $\rightarrow$ Thanh lý. |
| **3. Bảng Kiểm An Toàn Đầu Ngày (Pre-use Checklist)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | **TÍCH HỢP NGAY**: Check-list vận hành nhanh cho Điều dưỡng/Kỹ thuật viên tại phòng khám. |
| **4. Báo Hỏng 1 Chạm Qua QR Tại Giường (Bedside QR)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **TÍCH HỢP NGAY**: Điều dưỡng quét QR báo hỏng tức thời, chuyển trạng thái thiết bị sang `Đang sửa chữa`. |
| **5. Điều Phối Phiếu Công Việc (Work Orders / SLA)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | **TÍCH HỢP NGAY**: Phân công Kỹ sư P.TTB, ghi nhận vật tư thay thế, thời gian xử lý sự cố. |
| **6. Lịch Bảo Dưỡng Phòng Ngừa (Preventive Maintenance - PM)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **TÍCH HỢP NGAY**: Bám sát chu kỳ 2-4 lần/năm trong `Master Data.xltm` và SOP `QT.06`. |
| **7. Quản Lý Điều Chuyển Khoa Phòng (`QT.08`)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **TÍCH HỢP NGAY**: Biên bản điều chuyển giữa 21 Khoa phòng có xác nhận 2 bên giao - nhận. |
| **8. Semantica Context Graph & Causal Provenance** | ❌ (Chưa có) | ❌ (Chưa có) | ❌ (Chưa có) | ❌ (Chưa có) | **ĐỘT PHÁ CỦA BVQ7**: Đồ thị tri thức 1.294 Nodes truy vết W3C PROV-O loại bỏ hoàn toàn hallucination. |

---

## 2. KHUNG QUY TRÌNH Y TẾ CHUẨN CẦN BỔ SUNG VÀO PHẦN MỀM

```
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                    🔄 VÒNG ĐỜI TOÀN DIỆN TRANG THIẾT BỊ Y TẾ (SOPs)                    │
  └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
      ┌───────────────────┬───────────────────┼───────────────────┬───────────────────┐
      ▼                   ▼                   ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  BƯỚC 1:     │    │  BƯỚC 2:     │    │  BƯỚC 3:     │    │  BƯỚC 4:     │    │  BƯỚC 5:     │
│ TIẾP NHẬN &  │───►│ BÀN GIAO LẮP │───►│ KIỂM TRA ĐẦU │───►│ BẢO TRÌ ĐỊNH │───►│ ĐIỀU CHUYỂN  │
│  NGHIỆM THU  │    │ ĐẶT VÀO KHOA │    │ NGÀY & VẬN   │    │ KỲ & BÁO     │    │ & HỘI ĐỒNG   │
│ (HĐ Mua sắm, │    │(Mã BM04, Tạo │    │ HÀNH TẠI CHỖ │    │ HỎNG SỬA CHỮA│    │  THANH LÝ    │
│  CO/CQ, Sổ LL│    │ Mã Kép QR)   │    │(Pre-use Check│    │(PM / WorkOrd)│    │(QT.08, QT.07)│
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

---

## 3. LỘ TRÌNH TRIỂN KHAI CÁC TÍNH NĂNG MỚI (ACTION PLAN)

### 📌 Phân Hệ 1: Cấu Trúc Phụ Kiện & Cấu Kiện Kèm Theo (Parent-Child Asset Hierarchy)
* Bổ sung bảng quan hệ `device_accessories` trong SQLite và UI hiển thị cây phân cấp:
  * Ví dụ: Máy Siêu Âm Voluson P8 (`VP8206119`) quản lý trực tiếp 4 đầu dò con: Convex `1352048WX1`, 3D/4D `1349109WX9`, Âm đạo `1348559WX4`, Linear `1353969WX7`.
  * Ví dụ: Máy Sốc tim TEC-5631 quản lý Cáp tạo nhịp ngoài, Bản đánh sốc ngoài người lớn/trẻ em, Pin sạc Lithium.

### 📌 Phân Hệ 2: Bảng Kiểm Tra An Toàn Vận Hành Đầu Ngày (Daily Pre-use Checklist)
* Thiết kế giao diện Web Mobile-Friendly cho Điều dưỡng / Kỹ thuật viên kiểm tra 3-5 tiêu chí an toàn trước khi vào ca khám:
  * Nguồn điện & Dây tiếp địa an toàn.
  * Tình trạng cơ khí & Cảm biến không nứt vỡ.
  * Khí y tế đạt áp suất tiêu chuẩn (4-5 bar cho O2, Air, Vac).
  * Chức năng tự kiểm tra (Self-test) báo OK.

### 📌 Phân Hệ 3: Báo Hỏng 1-Chạm Tại Giường & Phiếu Công Việc Kỹ Thuật (Bedside Work Orders)
* Quét mã QR decal trên thân máy để mở ngay form báo hỏng:
  * Mô tả triệu chứng sự cố (ví dụ: màn hình sọc, bơm tiêm báo lỗi áp lực, mất nguồn).
  * Mức độ ưu tiên: Khẩn cấp (Phòng mổ/Cấp cứu), Bình thường, Thấp.
  * Phân công Kỹ sư P.TTB xử lý kèm thời gian SLA (phản hồi trong 15 phút với ca khẩn cấp).

### 📌 Phân Hệ 4: Quy Trình Điều Chuyển & Thanh Lý Thiết Bị (`QT.08` & `QT.07`)
* Form số hóa Phiếu điều chuyển thiết bị giữa 21 Khoa phòng, tự động ghi nhận lịch sử di chuyển vào Sổ lý lịch máy và cập nhật tức thời Semantica Graph.
