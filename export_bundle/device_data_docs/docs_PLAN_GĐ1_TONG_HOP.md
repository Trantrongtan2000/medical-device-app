# Kế hoạch thực hiện Giai đoạn 1 — Đối chiếu 5 AI

_Cùng prompt: "KẾ HOẠCH THỰC HIỆN TỪNG BƯỚC cho GIAI ĐOẠN 1 (tuần 0-2)", dựa trên roadmap trước. Bài đầy đủ trong `docs/PLAN_GĐ1_*.md`._

## 1. Độ dài mỗi bài

- **ChatGPT**: 19.148 ký tự (1261 dòng)
- **Claude**: 12.516 ký tự (211 dòng)
- **DeepSeek**: 14.191 ký tự (240 dòng)
- **Grok**: 6.667 ký tự (164 dòng)
- **AI Studio**: 7.568 ký tự (225 dòng)

## 2. Điểm đồng thuận (5 AI)

1. **Task đầu tiên bắt buộc: Migration schema Giai đoạn 1** — tạo `maintenance_schedules` + thêm cột vào `devices` (risk_level, pm_frequency, next_pm_date) + bảng `notifications`. Không endpoint nào làm trước migration.
2. **MVP demo sớm nhất = "tạo lịch bảo trì định kỳ tự động"** — maintenance_schedules + engine generate + UI danh sách. Demo được ngày 3-6.
3. **Cảnh báo hết hạn kiểm định (certs) là task P0 song song** — chỉ cần query certs.expiry_date, không cần bảng mới.
4. **Dùng APScheduler trong FastAPI** (không Celery) cho job cảnh báo hằng ngày.
5. **Rủi ro được cả 5 nhắc: SQLite ALTER TABLE hạn chế** (tạo bảng mới → copy → đổi tên), **transaction rollback khi generate hàng loạt**, **APScheduler khởi tạo 2 lần khi reload**, **timezone UTC+7** (lưu DATE không giờ).
6. **Mỗi task đều có endpoint REST + file route cụ thể + acceptance criteria** để self-test.

## 3. So sánh cấu trúc task theo từng AI

- **ChatGPT**: Vertical slice end-to-end: Dashboard → Device list → Detail → Search → History → Import/OCR mẫu. Tập trung demo 1 luồng hoàn chỉnh trước khi làm nhiều module.
- **Claude**: 8 task có sơ đồ phụ thuộc rõ (T1 migration → T2 seed → T3 CRUD → T4 generate → T5 certs/expiring → T6 pre-use → T7 APScheduler → T8 API test). Cảnh báo route conflict FastAPI khi có 87 endpoint cũ.
- **DeepSeek**: 10 task chi tiết nhất (1.1-1.10), tổng 30 giờ = 4-5 ngày 1 dev. Có bảng ước lượng giờ/task (T1.1=2h, T1.2=4h...). Nhấn mạnh tách repairs khỏi maintenance_logs + script test demo/test_workflow.py.
- **Grok**: Ngắn nhất nhưng thực dụng: MVP ngay tuần 1 "bảng schedules + 1 endpoint + 1 component FE", demo ngày 3-4, kèm script import_schedules.py. Cảnh báo backup database trước test.
- **AI Studio**: 8 task có sơ đồ dependency + 3 mốc DEMO cụ thể theo ngày (DEMO 1 ngày 3: cảnh báo kiểm định; DEMO 2 ngày 6: lịch PM; DEMO 3 ngày 8: QR code). Duy nhất đề xuất API QR code + tem in + mobile scan, risk_level A/B/C/D theo NĐ 98, WAL mode.

## 4. Kế hoạch hợp nhất đề xuất (tổng hợp 5 AI)

### Tuần 1 — Nền tảng + Lịch bảo trì (MVP demo ngày 3-6)
1. **T1.1 Migration (4h)**: `maintenance_schedules` + ALTER `devices` (risk_level A/B/C/D, pm_frequency_months, last_pm_date, next_pm_date) + bảng `notifications`. WAL mode trong `app/database.py`. SQLite: tạo bảng mới → copy → rename nếu cần.
2. **T1.2 CRUD maintenance_schedules (4h)**: `app/routes/schedules.py` + `web/schedules.html` + `web/js/schedules.js`. Validate device_id tồn tại, ngày ISO YYYY-MM-DD.
3. **T1.3 Engine generate lịch hàng loạt (2h)**: `POST /schedules/generate` đọc devices.category + chu kỳ → batch insert; transaction rollback nếu 1 fail; tránh trùng lịch active.
4. **T1.4 Cảnh báo kiểm định (5h)**: `GET /alerts/expiring` + APScheduler job hằng ngày quét certs.expiry_date (90/60/30 ngày → notifications). Khởi tạo scheduler qua lifespan, check scheduler.running tránh double.
5. **T1.5 Dashboard cảnh báo UI (2h)**: badge header + trang alerts (polling 60s), đánh dấu đã đọc.

### Tuần 2 — Mở rộng workflow
6. **T2.1 Pre-use inspection (4h)**: checklist JSON linh hoạt + `POST /inspections/pre-use` + `GET /inspections/pre-use/device/{id}`.
7. **T2.2 Repairs tách khỏi maintenance_logs (4h)**: bảng `repairs` + CRUD + tab "Sửa chữa" trong trang chi tiết thiết bị (ChatGPT/DeepSeek/Grok đồng ý tách).
8. **T2.3 Transfers nâng cấp (4h)**: thêm cột handover/confirmed + `PUT /transfers/{id}/confirm` cập nhật devices.facility_id trong cùng transaction.
9. **T2.4 QR code (2h, từ AI Studio)**: `GET /devices/{id}/qr-code` + tem in + mobile look-up.
10. **T2.5 E2E demo (2h)**: `scripts/demo_workflow.py` — 1 thiết bị: tạo lịch → sửa chữa → điều chuyển → cảnh báo; demo <10 phút không lỗi 500.

### Kiểm tra kỹ (5 AI đều nhắc)
- Transaction: generate hàng loạt all-or-nothing; confirm transfer cập nhật facility cùng transaction.
- Route conflict FastAPI: `/devices/{id}` vs `/devices/export` — khai báo route tĩnh TRƯỚC route động; smoke test 87 endpoint cũ sau khi thêm route mới.
- Timezone: lưu DATE thuần (không giờ), job chạy theo UTC+7.
- Backup database trước mọi migration.

## 5. Ước lượng tổng

- **DeepSeek**: 30 giờ (4-5 ngày, 1 dev) — chi tiết nhất từng task.
- **Các AI khác**: 25-35 giờ tương đương, phân bố 60% tuần 1 (nền tảng + lịch) / 40% tuần 2 (workflow).
- **Khuyến nghị**: bám DeepSeek 10 task + sơ đồ dependency Claude + mốc demo theo ngày của AI Studio (DEMO 1 ngày 3).
