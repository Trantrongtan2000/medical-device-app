KẾ HOẠCH THỰC HIỆN CHI TIẾT – GIAI ĐOẠN 1 (TUẦN 0–2)
Mục tiêu tổng thể

Xây dựng nền tảng cốt lõi cho vận hành thiết bị y tế:

Lập được lịch bảo trì định kỳ cho thiết bị

Ghi nhận được sửa chữa và điều chuyển (bàn giao cơ bản)

Có cảnh báo hết hạn kiểm định và pre‑use inspection đầu ca

Có thể demo quy trình khép kín cho 1 thiết bị

Thứ tự thực hiện tối ưu (MVP nhỏ nhất có giá trị trình diễn)

Mũi tên → thể hiện dependency: Task nào hoàn thành thì task sau mới bắt đầu được.

text
Copy
Download
Task

Ưu tiên demo sớm: Sau Task 1.4 đã có thể trình diễn "tạo lịch bảo trì tự động cho thiết bị". Đây là MVP nhỏ nhất có giá trị.

DANH SÁCH TASK CHI TIẾT
Task 1.1 – Migration: Tạo/ cập nhật bảng dữ liệu cho Giai đoạn 1
Thuộc tính	Nội dung
Tên task	Tạo migration cho maintenance_schedules, repairs, và bổ sung trạng thái cho transfers
Bảng / Schema	• maintenance_schedules (xem schema ở cuối roadmap)
• repairs (mới)
• transfers (ALTER TABLE thêm cột: handover_date, confirmed_by, status)
Endpoint mới	Chưa có – chỉ migration
File / Route	app/models.py (định nghĩa model SQLAlchemy hoặc raw SQL)
app/database.py (connection)
Script migration: migrations/001_giai_doan_1.sql
Frontend component	Không
Tiêu chí hoàn thành	• 3 bảng mới có thể SELECT từ SQLite
• transfers có đủ cột mới
• Không làm hỏng dữ liệu cũ
Ước lượng	2 giờ
Rủi ro cần kiểm tra	• SQLite không hỗ trợ ALTER TABLE với một số kiểu thay đổi – dùng thủ công (tạo bảng mới → copy dữ liệu → đổi tên)
• Kiểm tra khóa ngoại với devices và bme_staff
Task 1.2 – CRUD cơ bản cho Lịch bảo trì
Thuộc tính	Nội dung
Tên task	Xây dựng API CRUD cho maintenance_schedules
Bảng / Schema	maintenance_schedules (đã có ở Task 1.1)
Endpoint mới	POST /schedules – tạo mới
GET /schedules – danh sách (có filter device_id, status)
GET /schedules/{id} – chi tiết
PUT /schedules/{id} – cập nhật
DELETE /schedules/{id} – xóa (hoặc soft delete)
File / Route	app/routes/schedules.py (module mới)
Đăng ký router trong app/main.py
Frontend component	web/js/schedules.js
web/schedules.html (danh sách + form tạo/sửa)
Tiêu chí hoàn thành	• Có thể tạo 1 lịch bảo trì cho thiết bị có sẵn
• GET trả về đúng dữ liệu
• Cập nhật next_due hoạt động
Ước lượng	4 giờ (2h backend + 1.5h frontend + 0.5h test)
Rủi ro cần kiểm tra	• Validate device_id có tồn tại
• Kiểu dữ liệu ngày tháng (SQLite lưu TEXT) – dùng ISO format YYYY-MM-DD
• Phân trang cho danh sách (nếu nhiều)
Task 1.3 – Frontend: Xem danh sách và chi tiết lịch bảo trì
Thuộc tính	Nội dung
Tên task	Hiển thị danh sách lịch bảo trì và chi tiết trên giao diện
Bảng / Schema	Không (chỉ đọc dữ liệu từ API)
Endpoint mới	Không (dùng các endpoint từ Task 1.2)
File / Route	web/schedules.html
web/js/schedules.js (gọi API và render)
Frontend component	Bảng danh sách + modal chi tiết + form tạo/sửa
Tiêu chí hoàn thành	• Hiển thị danh sách lịch có sẵn (nếu có)
• Có thể tạo mới lịch từ form
• Xem được chi tiết 1 lịch
Ước lượng	3 giờ
Rủi ro cần kiểm tra	• CORS nếu frontend chạy khác port
• Xử lý lỗi từ API (hiển thị thông báo)
Task 1.4 – Tự động sinh lịch bảo trì từ template (tính năng cốt lõi)
Thuộc tính	Nội dung
Tên task	API sinh hàng loạt lịch bảo trì dựa trên loại thiết bị / chu kỳ
Bảng / Schema	Đọc từ devices (category, last_maintenance) và ghi vào maintenance_schedules
Endpoint mới	POST /schedules/generate
Body: { "category_id": 3, "frequency_days": 180, "start_date": "2026-09-01" }
File / Route	app/routes/schedules.py (thêm hàm generate_schedules)
Frontend component	Nút "Tạo lịch hàng loạt" trên trang danh sách, chọn loại thiết bị
Tiêu chí hoàn thành	• Với category có 10 thiết bị, gọi API tạo ra 10 lịch bảo trì
• Mỗi lịch có next_due = start_date + frequency_days (hoặc theo tháng)
• Có thể xem danh sách vừa tạo
Ước lượng	2 giờ
Rủi ro cần kiểm tra	• Tránh tạo trùng lặp (kiểm tra nếu đã có lịch active)
• Transaction: nếu 1 lịch lỗi thì rollback toàn bộ
• Xử lý số lượng lớn (>1000 thiết bị) – dùng batch insert
Task 1.5 – CRUD Sửa chữa (tách biệt với bảo trì)
Thuộc tính	Nội dung
Tên task	Xây dựng API CRUD cho repairs
Bảng / Schema	repairs (id, device_id, reported_by, reported_date, description, priority, status, cost, completed_date, notes)
Endpoint mới	POST /repairs
GET /repairs
GET /repairs/{id}
PUT /repairs/{id}
DELETE /repairs/{id}
File / Route	app/routes/repairs.py
Đăng ký router
Frontend component	web/repairs.html + web/js/repairs.js
Tiêu chí hoàn thành	• Tạo 1 phiếu sửa chữa cho thiết bị
• Cập nhật trạng thái (pending → in_progress → done)
• Xem danh sách sửa chữa theo thiết bị
Ước lượng	4 giờ (2.5h backend + 1.5h frontend)
Rủi ro cần kiểm tra	• Gắn với maintenance_logs hay tách riêng? Quyết định: tách riêng để dễ báo cáo
• Cost là số thập phân – dùng DECIMAL trong SQLite (lưu dạng REAL)
Task 1.6 – Frontend: Tích hợp sửa chữa và liên kết với thiết bị
Thuộc tính	Nội dung
Tên task	Hiển thị danh sách sửa chữa, form tạo, và tích hợp vào trang chi tiết thiết bị
Bảng / Schema	Không (đọc/ghi qua API)
Endpoint mới	Không (dùng Task 1.5)
File / Route	web/device_detail.html (thêm tab "Sửa chữa")
web/js/repairs.js
Frontend component	Tab danh sách sửa chữa + nút "Thêm phiếu sửa chữa"
Tiêu chí hoàn thành	• Trên trang chi tiết thiết bị, thấy được các phiếu sửa chữa của thiết bị đó
• Tạo phiếu mới từ trang chi tiết
Ước lượng	2 giờ
Rủi ro cần kiểm tra	• Refresh dữ liệu sau khi tạo mới
• Xử lý lỗi khi thiết bị không tồn tại
Task 1.7 – Cảnh báo hết hạn kiểm định (Backend + Scheduler)
Thuộc tính	Nội dung
Tên task	Xây dựng job kiểm tra certs và maintenance_schedules hết hạn, tạo thông báo
Bảng / Schema	notifications (id, user_id, related_entity, related_id, message, type, is_read, sent_at)
Endpoint mới	GET /alerts/expiring – danh sách cảnh báo hiện tại
POST /alerts/check – trigger chạy job thủ công
(tự động chạy mỗi ngày qua APScheduler)
File / Route	app/routes/alerts.py
app/services/scheduler.py (APScheduler)
app/main.py (khởi tạo scheduler)
Frontend component	web/js/alerts.js – hiển thị badge số lượng cảnh báo trên header
Tiêu chí hoàn thành	• Khi có cert hết hạn trong 30 ngày → tạo notification
• Khi có schedule quá hạn → tạo notification
• Gọi API /alerts/check tạo ra đúng cảnh báo
Ước lượng	5 giờ (2h scheduler + 2h API + 1h test)
Rủi ro cần kiểm tra	• TimeZone: Lưu ngày dạng DATE không có giờ, nhưng job chạy theo UTC – cần xác định rõ múi giờ cho phòng khám (UTC+7)
• Transaction: Khi tạo nhiều notification, đảm bảo all-or-nothing
• APScheduler trong FastAPI: khởi tạo đúng cách, tránh chạy 2 lần khi reload
• Job chạy lần đầu khi deploy – kiểm tra không bị trùng
Task 1.8 – Frontend: Hiển thị cảnh báo và badge
Thuộc tính	Nội dung
Tên task	Hiển thị số lượng cảnh báo trên thanh điều hướng, và trang danh sách cảnh báo
Bảng / Schema	Không
Endpoint mới	Không (dùng Task 1.7)
File / Route	web/index.html (thêm badge)
web/alerts.html
web/js/alerts.js
Frontend component	Badge số lượng + trang danh sách cảnh báo (có filter đã đọc/chưa đọc)
Tiêu chí hoàn thành	• Badge hiển thị số cảnh báo chưa đọc
• Có thể đánh dấu đã đọc
• Xem được chi tiết cảnh báo
Ước lượng	2 giờ
Rủi ro cần kiểm tra	• Gọi API định kỳ để cập nhật badge (polling mỗi 60s)
Task 1.9 – Mở rộng Transfers và Pre‑use Inspection
Thuộc tính	Nội dung
Tên task	Bổ sung API cho điều chuyển (bàn giao) và kiểm tra trước khi sử dụng
Bảng / Schema	transfers (đã thêm cột ở Task 1.1)
pre_use_inspection (giữ nguyên, thêm endpoint)
Endpoint mới	PUT /transfers/{id}/confirm – xác nhận bàn giao
POST /transfers/handover – tạo điều chuyển mới
POST /inspections/pre-use – tạo phiếu kiểm tra đầu ca
GET /inspections/pre-use/device/{device_id} – lấy phiếu mới nhất
File / Route	app/routes/transfers.py (mở rộng)
app/routes/inspections.py (mới)
Frontend component	web/transfers.html
web/js/transfers.js
web/inspections.html
Tiêu chí hoàn thành	• Tạo điều chuyển → xác nhận bàn giao → cập nhật facility_id của thiết bị
• Tạo phiếu pre‑use cho thiết bị, lưu kết quả (pass/fail, notes)
• Xem được lịch sử điều chuyển của thiết bị
Ước lượng	4 giờ (2h backend + 2h frontend)
Rủi ro cần kiểm tra	• Khi xác nhận điều chuyển, cần cập nhật devices.facility_id trong cùng transaction
• Pre‑use inspection có thể có checklist động – dùng JSON field để linh hoạt
Task 1.10 – Tích hợp demo toàn quy trình (End‑to‑end)
Thuộc tính	Nội dung
Tên task	Xây dựng 1 luồng demo khép kín cho 1 thiết bị: từ tạo lịch bảo trì → sửa chữa → điều chuyển → cảnh báo
Bảng / Schema	Không
Endpoint mới	Không (dùng tất cả các endpoint đã xây dựng)
File / Route	Viết script test demo/test_workflow.py hoặc hướng dẫn thao tác thủ công
Frontend component	Tạo 1 trang "Demo" hoặc video ghi hình các thao tác
Tiêu chí hoàn thành	• Có thể trình diễn trước ban lãnh đạo toàn bộ quy trình trong < 10 phút
• Không có lỗi 500 trong quá trình demo
Ước lượng	2 giờ
Rủi ro cần kiểm tra	• Dữ liệu demo sạch (không ảnh hưởng dữ liệu thật) – dùng bảng devices có is_demo = 1 hoặc database riêng
TỔNG HỢP THỜI GIAN
Task	Giờ
1.1 Migration	2
1.2 CRUD Schedules	4
1.3 FE Schedules	3
1.4 Generate schedules	2
1.5 CRUD Repairs	4
1.6 FE Repairs	2
1.7 Alerts + Scheduler	5
1.8 FE Alerts	2
1.9 Transfers + Pre‑use	4
1.10 Demo tích hợp	2
Tổng	30 giờ

Tương đương 4–5 ngày làm việc cho 1 dev full‑time (hoặc 2 dev trong 2.5 ngày).

RỦI RO VÀ ĐIỂM CẦN KIỂM TRA KỸ KHI IMPLEMENT VỚI FASTAPI + SQLITE
Rủi ro	Cách kiểm tra / xử lý
Transaction không rollback khi lỗi	Dùng @db.transaction() decorator hoặc with db.connection: trong FastAPI; kiểm tra bằng cách cố tình tạo lỗi giữa chừng
Migration không an toàn	Chạy migration trên bản sao database trước; dùng Alembic nếu có thể
APScheduler khởi tạo 2 lần	Kiểm tra scheduler.running trước khi add_job; dùng lifespan context manager trong FastAPI
TimeZone không nhất quán	Lưu tất cả ngày tháng dạng DATE không giờ (YYYY-MM-DD). Khi so sánh next_due <= CURRENT_DATE, dùng DATE('now', 'localtime') để lấy ngày theo múi giờ hệ thống
SQLite không hỗ trợ ENUM	Dùng CHECK constraint hoặc lưu dạng TEXT và validate ở Pydantic
Hiệu năng khi query nhiều bảng	Tạo index trên device_id, status, next_due, expiry_date
Frontend gọi API sai CORS	Cấu hình allow_origins=["*"] trong FastAPI khi dev; chuyển sang whitelist khi production
Dữ liệu test ảnh hưởng production	Dùng database riêng cho dev/test (test.db), hoặc thêm flag is_test vào các bảng
TIÊU CHÍ KẾT THÚC GIAI ĐOẠN 1
□ 

Có ít nhất 1 lịch bảo trì được tạo tự động cho 1 thiết bị

□ 

Có ít nhất 1 phiếu sửa chữa được tạo và cập nhật trạng thái

□ 

Có ít nhất 1 cảnh báo hết hạn xuất hiện trên giao diện

□ 

Có thể điều chuyển 1 thiết bị từ khoa A sang khoa B và cập nhật vị trí

□ 

Toàn bộ quy trình trên có thể demo trong 10 phút mà không gặp lỗi

DeepThink
Search
AI-generated, for reference only
Báº¡n lÃ  kiáº¿n trÃºc sÆ° pháº§n má»m. Dá»±a trÃªn há»“ sÆ¡ dá»± Ã¡n vÃ  database dÆ°á»›i Ä‘Ã¢y, hÃ£y láº­p má»™t Káº¾ HOáº CH PHÃT TRIá»‚N (roadmap) chi tiáº¿t, Æ°u tiÃªn theo giÃ¡ trá»‹ vÃ  rá»§i ro. ## Dá»± Ã¡n Há»‡ thá»‘ng quáº£n lÃ½ trang thiáº¿t bá»‹ y táº¿ cho PhÃ²ng khÃ¡m Äa khoa TÃ¢m Anh Quáº­n 7 (TP.HCM), tuÃ¢n thá»§ Nghá»‹ Ä‘á»‹nh 98/2021/NÄ-CP vÃ  ThÃ´ng tÆ° 05/2022/TT-BYT. - Backend: FastAPI (Python), SQLite, 87 REST endpoints (`app/main.py`, `app/routes.py`) - Frontend: thuáº§n JS (khÃ´ng framework), thÆ° má»¥c `web/` - Chuáº©n tham chiáº¿u: Snipe-IT + SpeedMaint CMMS - OCR: Gemini AI + Mistral OCR; kho dá»¯ liá»‡u OCR ~37.385 file, 90 GB trÃªn á»• G: (20.717 PDF, 9.682 markdown) â€” Ä‘Ã£ xong viá»‡c sá»­a liÃªn káº¿t mdâ†”pdf (100% resolve) - Nguá»“n master: file Excel "Master Data" â†’ 1.211 thiáº¿t bá»‹ Ä‘Ã£ import ## Database hiá»‡n táº¡i (SQLite) | Báº£ng | Sá»‘ báº£n ghi | |---|---| | devices | 1.211 | | facilities | 39 | | categories | 10 | | contracts | 198 | | supplier_contacts | 102 | | certs (kiá»ƒm Ä‘á»‹nh) | 107 | | maintenance_logs | 48 | | maintenance_schedules | 0 | | oncall_schedule | 92 | | transfers (Ä‘iá»u chuyá»ƒn) | 3 | | pre_use_inspection | 1 | | feedback | 2 | | api_keys | 5 | | bme_staff | 6 | | hospital_directory | 7 | ## YÃªu cáº§u 1. ÄÃ¡nh giÃ¡ má»©c Ä‘á»™ hoÃ n thiá»‡n so vá»›i nghiá»‡p vá»¥ thiáº¿t bá»‹ y táº¿ bá»‡nh viá»‡n (danh má»¥c, kiá»ƒm Ä‘á»‹nh/hiá»‡u chuáº©n, báº£o trÃ¬ báº£o dÆ°á»¡ng, sá»­a chá»¯a, há»£p Ä‘á»“ng mua sáº¯m, bÃ n giao/nghiá»‡m thu, Ä‘iá»u chuyá»ƒn, thanh lÃ½, nhÃ  cung cáº¥p). 2. Chá»‰ ra lá»— há»•ng lá»›n nháº¥t hiá»‡n nay: báº£ng maintenance_schedules = 0, transfers = 3, pre_use_inspection = 1, feedback = 2 â€” cho tháº¥y module nÃ o Ä‘ang thiáº¿u hoáº·c chÆ°a dÃ¹ng. 3. Láº­p roadmap 3 giai Ä‘oáº¡n (0â€“2 tuáº§n, 2â€“8 tuáº§n, 8 tuáº§n+) vá»›i cÃ¡c module, endpoint cáº§n thÃªm, vÃ  Æ°u tiÃªn. 4. Äá» xuáº¥t kiáº¿n trÃºc dá»¯ liá»‡u bá»• sung (schema má»›i) cho: lá»‹ch báº£o trÃ¬ Ä‘á»‹nh ká»³, lá»‹ch kiá»ƒm Ä‘á»‹nh háº¿t háº¡n tá»± nháº¯c, kho phá»¥ tÃ¹ng, bÃ¡o cÃ¡o thá»‘ng kÃª. 5. Káº¿ hoáº¡ch tÃ­ch há»£p kho OCR: gáº¯n tÃ i liá»‡u PDF/md (biÃªn báº£n bÃ n giao, há»£p Ä‘á»“ng, phiáº¿u sá»­a chá»¯a, chá»©ng chá»‰ kiá»ƒm Ä‘á»‹nh) vÃ o tá»«ng thiáº¿t bá»‹/con sá»‘ há»£p Ä‘á»“ng, cÃ³ tÃ¬m kiáº¿m full-text. Tráº£ lá»i báº±ng tiáº¿ng Viá»‡t, Ä‘á»‹nh dáº¡ng Markdown, ngáº¯n gá»n nhÆ°ng Ä‘á»§ chi tiáº¿t Ä‘á»ƒ triá»ƒn khai.
Báº¡n lÃ  kiáº¿n trÃºc sÆ° pháº§n má»m. Dá»±a trÃªn roadmap 3 giai Ä‘oáº¡n báº¡n vá»«a láº­p cho há»‡ thá»‘ng quáº£n lÃ½ trang thiáº¿t bá»‹ y táº¿ TÃ¢m Anh Q7 (FastAPI + SQLite + vanilla JS frontend, 87 endpoints, 16 báº£ng, 1.211 thiáº¿t bá»‹, kho OCR 90 GB), hÃ£y láº­p Káº¾ HOáº CH THá»°C HIá»†N Tá»ªNG BÆ¯á»šC cho GIAI ÄOáº N 1 (tuáº§n 0-2). YÃªu cáº§u cá»¥ thá»ƒ: 1. Chia Giai Ä‘oáº¡n 1 thÃ nh cÃ¡c task nhá», cÃ³ thá»© tá»± phá»¥ thuá»™c rÃµ rÃ ng (task nÃ o lÃ m trÆ°á»›c, task nÃ o chá»). 2. Vá»›i Má»–I task ghi rÃµ: tÃªn, báº£ng/schema cáº§n migrate, endpoint REST cáº§n thÃªm, file/route cá»¥ thá»ƒ trong FastAPI, component frontend, tiÃªu chÃ­ hoÃ n thÃ nh (acceptance criteria) Ä‘á»ƒ tá»± kiá»ƒm tra. 3. Æ¯á»›c lÆ°á»£ng sá»‘ giá» cho má»—i task. 4. Äá» xuáº¥t thá»© tá»± thá»±c hiá»‡n tá»‘i Æ°u Ä‘á»ƒ demo Ä‘Æ°á»£c sá»›m nháº¥t (MVP nhá» nháº¥t cÃ³ giÃ¡ trá»‹ trÃ¬nh diá»…n). 5. Chá»‰ ra rá»§i ro/Ä‘iá»ƒm cáº§n kiá»ƒm tra ká»¹ khi implement báº±ng FastAPI + SQLite (transaction, migration, background scheduler, timezone). Tráº£ lá»i báº±ng tiáº¿ng Viá»‡t, Ä‘á»‹nh dáº¡ng Markdown, thá»±c táº¿ Ä‘á»ƒ code ngay.

