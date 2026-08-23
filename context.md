# 🏥 BỆNH VIỆN ĐA KHOA QUẬN 7 — BỐI CẢNH HỆ THỐNG & DỮ LIỆU (CONTEXT.MD)
## HỆ THỐNG QUẢN LÝ TRANG THIẾT BỊ Y TẾ (HTM v3) & KHO DỮ LIỆU SỐ HÓA OCR

* **Thời gian cập nhật:** 2026-08-22 14:22:00 (GMT+7)
* **Phiên làm việc:** `fe40e7ae-624b-4593-b6e4-7b826b881d2b`
* **Trạng thái chất lượng dữ liệu:** `100.0% VERIFIED & CLEANED`
* **Chuẩn thiết kế UI:** `Nutlope/hallmark` (Modern-Minimal / Clinical-Editorial)

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ thống gồm 2 thành phần gắn kết chặt chẽ:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TỔNG THỂ KIẾN TRÚC DỮ LIỆU & ỨNG DỤNG                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. KHO DỮ LIỆU NGUỒN (DATA BACKBONE & DOCUMENT LAKE)                                   │
│    Vị trí: G:\BV QUẬN 7_OCR_WORK_20260712                                             │
│    • 7.705 file Markdown bóc tách từ OCR chứng từ y tế.                               │
│    • 8.419 file PDF scan gốc (Hợp đồng, Bàn giao, Kiểm định, Bảo trì).                │
│    • 37.584 file toàn viện (91,06 GB) được định danh qua Google Magika AI.             │
│    • final_validated_entities.json & csv: Bảng dữ liệu chuẩn đã khóa sau kiểm toán.     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. HỆ THỐNG ỨNG DỤNG VẬN HÀNH (OPERATIONAL WEB APP - HTM v3)                           │
│    Vị trí: C:\Users\tantt\Downloads\medical-device-app                                │
│    • Backend: FastAPI (Python 3.10+), SQLAlchemy 2.0 ORM, Pydantic v2.                 │
│    • Database: SQLite (devices.db) với 1.211 thiết bị và 19.135 liên kết tài liệu.     │
│    • Frontend: Vanilla JS ES6 Modular, Bootstrap 5 + Apple UX, In mã QR decal.         │
│    • AI & OCR: Google Gemini Interactions API + Mistral OCR + Key Rotation Pool.       │
│    • Knowledge Graph: Semantica Engine liên kết Thiết bị - Khoa phòng - Hợp đồng.      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. KẾT QUẢ KIỂM TOÁN DỮ LIỆU TOÀN DIỆN (AUDIT FINDINGS & GROUND TRUTH)

* **Tổng quy mô thực thể đã kiểm toán:** **3.710 thực thể thiết bị y tế**.
* **Phân lớp tự động sạch (KEEP & OBSERVE):** **3.693 thực thể (99,54%)** nhất quán 100% qua hàng ngàn tài liệu.
* **17 Ca Bất Thường Đã Được Con Người & Vision Thẩm Định:** **17 thực thể (0,46%)** — Toàn bộ đã được phê duyệt qua bàn làm việc đối soát Hallmark và lưu tại `C:\Users\tantt\Downloads\audit_user_decisions_with_notes.csv`.

### Bảng Giá Trị Chuẩn 17 Ca Đã Khóa:
1. `VirtueRF` (Máy điều trị da): `serial_no = 26003` (Bảo vệ máy thứ 3 trong lô, đúng Master dòng 619).
2. `JR913` (Nhiệt ẩm kế): `serial_no = JR913-CC1` (Phân bổ khoa Cấp cứu 1).
3. `HTC-2` (Nhiệt ẩm kế): `serial_no = HTC-2-CC1` (Phân bổ khoa Cấp cứu 1).
4. `Zeus - 150` (Dao mổ điện): `serial_no = A07COAP0248` (Lô 7 dao mổ; cả A07COAP0248 và A07COAP0251 đều tồn tại).
5. `CX23` (Kính hiển vi): `contract_no = 077.2023/DM-TA` (Hợp đồng mua sắm năm 2023 Cty Đức Minh).
6. `ZG-2C` (Máy điện tim): `contract_no = 02/2024/PA-BVTAHCM` (Chuẩn hóa lỗi OCR ký tự PICM $ightarrow$ BVTAHCM).
7. `BLUEEVA` (Máy thẩm mỹ): `contract_no = V15HCM-13052024/ERADA/TAMANH` (Chuẩn hóa lỗi OCR 1I $ightarrow$ HCM).
8. `Vivid S70N H` (Máy siêu âm): `contract_no = 07/HĐMB/TDMED-TAHCM/2024` (Khôi phục toàn bộ số HĐ TDMED).
9. `LOGIQ FORTIS` (Máy siêu âm): `contract_no = HĐ-24/02241` (Khóa theo bản in trên trang bìa PDF gốc).
10. `12L-RS` (Đầu dò siêu âm): `contract_no = 0506/2023/HĐMB/TAHCM-VT` (Khôi phục số HĐ Việt Tiến đầy đủ).
11. `Solarmax LED 160` (Đèn mổ): `contract_no = 07/2023/PA-BVTATPHCM` (Xác nhận số HĐ Phúc Anh 2023).
12. `Prodigy` (Máy đo loãng xương): `contract_no = 02/HĐMB/TD-TAHCM/2023` (Khôi phục đầy đủ số HĐ Cty T.D 2023).
13. `SIERRA SUMMIT H` (Máy điện cơ): `contract_no = 42/2023/HĐMB/VV-TA` (Khôi phục đầy đủ số HĐ Vavi 2023).
14. `Prodigy` (Máy đo loãng xương): `contract_no = 02/HĐMB/TD-TAHCM/2023` (Khôi phục đầy đủ số HĐ Cty T.D 2023).
15. `DigiRad-FP` (Máy X-Quang): `contract_no = 04-06/2023/TAHCM-GNT` (Xác nhận số HĐ GNT 2023).
16. `AquaBplus 2000 H` (Hệ lọc nước RO): `contract_no = 1508-2023/HĐT/TA-AP` (Khôi phục đầy đủ số HĐ An Pha 2023).
17. `ZEUS-150 H` (Dao mổ điện): `contract_no = 08/2024/HDMB/CMC-TA` và `serial_no = A07COAS0429`.

---

## 3. CÔNG CỤ ĐỐI SOÁT TRỰC QUAN HALLMARK (AUDIT WORKBENCH)

* **Tệp triển khai:** `audit_workbench.html` (Đã lưu tại Desktop và `00_HE_THONG_VA_SCRIPTS/workbench/`).
* **Đặc tính kỹ thuật:**
  - Áp dụng triệt để bộ nhận diện và token thiết kế từ skill `Nutlope/hallmark`.
  - Nhúng trước toàn bộ **208 trang scan PDF** độ phân giải cao (`dpi=115`) của 16 hồ sơ liên quan.
  - Hỗ trợ cuộn liên tục, phóng to/thu nhỏ, mở rộng 100% toàn cảnh (`⛶`).
  - Tích hợp ô nhập chỉ đạo nghiệp vụ người dùng (tự động lưu `localStorage` và xuất CSV).

---

## 4. CẤU TRÚC THƯ MỤC CHUẨN HÓA KHO DỮ LIỆU (`G:\BV QUẬN 7_OCR_WORK_20260712`)

```text
G:\BV QUẬN 7_OCR_WORK_20260712│
├── 📂 md/                                 (Kho 7.705 file Markdown số hóa)
├── 📂 00_HE_THONG_VA_SCRIPTS/             (Mã nguồn kiểm toán, tools, workbench)
├── 📂 01_DANH_MUC_THIET_BI/               (Báo cáo tổng kết kiểm toán chi tiết)
├── 📂 08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP/   (Kho lưu trữ bản backup cũ & snapshot)
│
├── 📄 final_validated_entities.csv        (BẢNG DỮ LIỆU ĐÃ THẨM ĐỊNH 100% - CSV)
├── 📄 final_validated_entities.json       (BẢNG DỮ LIỆU ĐÃ THẨM ĐỊNH 100% - JSON)
├── 📄 REPORT.md                           (Báo cáo đồng bộ hệ thống)
├── 📄 session.md                          (Nhật ký phiên làm việc tổng hợp)
├── 📄 context.md                          (Bản đặc tả bối cảnh hiện tại)
├── 📄 file_map.json                       (Chỉ mục 37.584 tệp được quét qua Magika AI)
└── 📄 Master Data.xltm                    (Master Data bảng tính gốc)
```

---

## 5. BƯỚC TIẾP THEO (NEXT MILESTONES)

1. **Đồng bộ cơ sở dữ liệu `devices.db`:** Nạp các giá trị đã chuẩn hóa từ `final_validated_entities.json` vào database của `medical-device-app`.
2. **Tái cấu trúc thư mục `md/`:** Gom các file Markdown về 6 phân hệ vòng đời thiết bị y tế (Mua sắm $ightarrow$ Bàn giao $ightarrow$ Kiểm định $ightarrow$ Bảo trì $ightarrow$ Sửa chữa $ightarrow$ Pháp lý).
3. **Khởi chạy máy chủ Web App:** Thực thi `python start_server.py` tại `medical-device-app` để vận hành thực tế hệ thống.
