# Kế hoạch phát triển — Đối chiếu 4 AI

_Báo cáo tổng hợp từ ChatGPT, Claude.ai, DeepSeek, Grok — cùng một prompt về dự án quản lý thiết bị y tế Tâm Anh Q7._

Tham khảo đầy đủ từng bài: `docs/CHATGPT_ROADMAP.md`, `docs/CHATGPT_AUX_CLAUDE.md`, `docs/CHATGPT_AUX_DEEPSEEK.md`, `docs/CHATGPT_AUX_GROK.md`

## 1. Độ dài mỗi bài

- **ChatGPT**: ~2090 từ
- **Claude**: ~2077 từ
- **DeepSeek**: ~1899 từ
- **Grok**: ~1008 từ

## 2. Điểm đồng thuận (cả 4 đồng ý)

1. **Lỗ hổng số 1: `maintenance_schedules = 0`** — không có lịch bảo trì định kỳ, toàn bộ 1.211 thiết bị không ai nhắc hạn bảo dưỡng; rủi ro pháp lý theo NĐ 98/2021 + TT 05/2022/TT-BYT.
2. **Hệ thống là "asset registry" chưa phải "asset lifecycle management"** — master data mạnh (~70-80%), workflow vận hành yếu (CMMS ~25-35%).
3. **Kiểm định (`certs` = 107) thiếu cơ chế nhắc hết hạn** — cần cảnh báo 90/60/30 ngày + hết hạn.
4. **`pre_use_inspection` (1), `transfers` (3), `feedback` (2) = module chưa vận hành** — cần workflow bắt buộc chứ không chỉ CRUD.
5. **Giai đoạn 1 (0-2 tuần) trùng nhau**: maintenance schedule engine + cảnh báo hết hạn + pre-use inspection + dashboard alerts.
6. **Bảng `work_orders`/`repairs` cần tách khỏi `maintenance_logs`** — để tính MTBF/MTTR sau này.
7. **Schema OCR đề xuất giống nhau**: bảng `documents` + liên kết polymorphic (device/contract/cert) + SQLite FTS5 full-text.
8. **Kho phụ tùng cần bảng `spare_parts` + giao dịch xuất/nhập/tồn tối thiểu.**
9. **Không nên copy toàn bộ 90 GB OCR vào DB** — chỉ lưu metadata + đường dẫn + nội dung text để search.

## 3. Điểm khác biệt / bổ sung riêng

- **ChatGPT**: Chi tiết nhất về endpoint (POST /devices/{id}/status-transition, /maintenance/plans/generate...). Đề xuất state machine 10 trạng thái thiết bị + bảng device_status_history. Nhấn mạnh dùng APScheduler + FastAPI. Khuyến nghị MVP 9 chức năng cụ thể.
- **Claude**: Định lượng mức độ hoàn thiện từng nghiệp vụ (danh mục 70-80%, CMMS 25-35%...). Nhắc rủi ro pháp lý TT 05 với nhóm C/D. Đề xuất bảng notifications + maintenance_parts_used. Giai đoạn 3 có TCO, đề xuất thay thế thiết bị theo tần suất hỏng, AI phân loại OCR.
- **DeepSeek**: Nhấn mạnh tách bảng repairs riêng ngay giai đoạn 1. Đề xuất VIEW động cho báo cáo (device_maintenance_cost, expiring_certs) thay vì bảng aggregate. Kế hoạch OCR 3 bước: upload->FTS5->ranking/highlight.
- **Grok**: Ước lượng ~65% hoàn thiện so với CMMS chuyên dụng. Nhấn mạnh import dữ liệu hiện có (198 contracts + 107 certs + 92 on-call) bằng bulk insert. Đề xuất Celery cho scheduler. Gợi ý tìm theo serial_number/contract_number khi search OCR.

## 4. Roadmap hợp nhất đề xuất (tổng hợp 4 AI)

### Giai đoạn 1 — 0-2 tuần (vá lỗ hổng pháp lý)
1. State machine vòng đời thiết bị + `device_status_history` (cấm sửa status tự do)
2. `maintenance_schedules` + engine sinh lịch định kỳ từ chu kỳ thiết bị + `work_orders`
3. Compliance: cảnh báo certs hết hạn 90/60/30 ngày (bảng `notifications`)
4. Pre-use inspection theo checklist nhóm rủi ro cao
5. Dashboard 6 chỉ số (total/active/maintenance due/overdue/certs expiring/out-of-service)
6. Kênh feedback/báo lỗi từ khoa phòng

### Giai đoạn 2 — 2-8 tuần (khép vòng đời + tích hợp OCR)
1. Incident/repair tách khỏi maintenance_logs (tính MTBF/MTTR sau này)
2. Bàn giao/nghiệm thu + thanh lý (disposal) + transfer workflow đầy đủ
3. Kho phụ tùng `spare_parts` + transactions
4. **Document Hub**: bảng `documents` + `document_links` (polymorphic) + SQLite FTS5
5. Import OCR theo serial/contract_number; search `/search?q=`
6. Báo cáo cơ bản: chi phí bảo trì, tỷ lệ quá hạn kiểm định

### Giai đoạn 3 — 8 tuần+ (tự động hóa + phân tích)
1. Nhắc lịch tự động qua email/Zalo + background scheduler (APScheduler/Celery)
2. Báo cáo KPI: MTBF, MTTR, PM compliance, chi phí vòng đời (TCO)
3. AI phân loại/tóm tắt OCR khi gắn vào thiết bị (Gemini)
4. QR code trên thiết bị -> mobile workflow cho kỹ thuật viên hiện trường
5. Phân quyền theo vai trò (BME/trưởng khoa/quản lý)

## 5. Khuyến nghị triển khai

- Bắt đầu ngay với **Giai đoạn 1**, ưu tiên P0: maintenance schedule + cảnh báo hết hạn + dashboard — đây là phần 4 AI đều xếp số 1.
- Trước khi code, audit 87 endpoint hiện có, map endpoint->module->bảng, tránh tạo endpoint trùng.
- Kho OCR 90 GB là "tài sản chưa khai thác" — làm Document Hub ở giai đoạn 2 để nâng giá trị trình diễn.
- Quy mô phòng khám (1.211 thiết bị): SQLite + APScheduler là đủ, chưa cần PostgreSQL/Celery. Giữ đơn giản.
