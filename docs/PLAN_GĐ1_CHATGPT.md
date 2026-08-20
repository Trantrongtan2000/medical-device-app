Kế hoạch thực hiện Giai đoạn 1 (Tuần 0–2)
0. Mục tiêu của Giai đoạn 1

Với hệ thống hiện có:

Backend: FastAPI

Database: SQLite

Frontend: Vanilla JavaScript

Hiện trạng: 87 endpoints, 16 bảng, 1.211 thiết bị, kho OCR khoảng 90 GB

Mục tiêu 2 tuần đầu không phải hoàn thiện toàn bộ hệ thống, mà là tạo một vertical slice chạy end-to-end để demo sớm:

Dashboard → Danh sách thiết bị → Chi tiết thiết bị → Tìm kiếm/Lọc → Lịch sử → Import/OCR mẫu

MVP nhỏ nhất có thể demo cuối Tuần 1

Server FastAPI chạy ổn định.

SQLite schema được kiểm tra và migration có kiểm soát.

Xem danh sách 1.211 thiết bị.

Search theo mã/tên/model/serial.

Xem trang chi tiết một thiết bị.

Hiển thị thống kê dashboard.

Có ít nhất một luồng cập nhật/lịch sử được ghi transactionally.

MVP cuối Giai đoạn 1
┌───────────────────┐
│ Dashboard         │
│ - Tổng thiết bị   │
│ - Theo trạng thái │
│ - Cảnh báo        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Device List       │
│ Search / Filter   │
│ Pagination        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Device Detail     │
│ Metadata          │
│ Lịch sử           │
│ Hồ sơ/OCR sample  │
└───────────────────┘
1. Thứ tự phụ thuộc tổng thể
T0. Khảo sát codebase + DB
        │
        ▼
T1. Chuẩn hóa môi trường + backup DB
        │
        ▼
T2. Audit schema + migration framework
        │
        ├──────────────┐
        ▼              ▼
T3. Repository/DB     T4. Chuẩn hóa API contract
        │              │
        └──────┬───────┘
               ▼
        T5. Device List API
               │
               ▼
        T6. Device List Frontend
               │
               ▼
        T7. Device Detail API
               │
               ▼
        T8. Device Detail Frontend
               │
               ├──────────────┐
               ▼              ▼
        T9. Dashboard API    T10. History/Audit
               │              │
               └──────┬───────┘
                      ▼
               T11. Dashboard UI
                      │
                      ▼
               T12. OCR/File sample integration
                      │
2. Tuần 0 — Audit và dựng nền móng
T0 — Khảo sát codebase và chụp snapshot hiện trạng

Ưu tiên: P0
Phụ thuộc: Không
Ước lượng: 4–6 giờ

Mục tiêu

Không code chức năng mới ngay. Phải xác định chính xác:

16 bảng hiện tại.

Quan hệ giữa các bảng.

87 endpoint đang hoạt động/thừa/trùng.

Cấu trúc thư mục FastAPI.

Cách frontend gọi API.

Dữ liệu 1.211 thiết bị đang nằm ở bảng nào.

OCR 90 GB đang được lưu và index như thế nào.

DB/schema

Chưa migrate.

Tạo tài liệu:

docs/
├── CURRENT_ARCHITECTURE.md
├── DB_SCHEMA.md
├── API_INVENTORY.md
└── MVP_SCOPE.md
FastAPI cần kiểm tra

Ví dụ:

app/
├── main.py
├── routers/
├── services/
├── models/
├── schemas/
├── database.py
└── dependencies.py

Nếu code hiện tại chưa chia như vậy thì không refactor lớn ngay. Chỉ ghi nhận hiện trạng.

Acceptance criteria

 Có danh sách đầy đủ 16 bảng.

 Có số record của từng bảng.

 Xác định bảng nguồn của 1.211 thiết bị.

 Export danh sách 87 endpoints.

 Ghi rõ endpoint nào phục vụ MVP.

 Server chạy được từ môi trường sạch.

Rủi ro

Không được refactor toàn bộ ở bước này.

Sai lầm phổ biến:

"Code hơi lộn xộn → viết lại architecture trước."

Điều đó dễ làm mất 1 tuần mà chưa demo được gì.

T1 — Chuẩn hóa môi trường chạy và backup SQLite

Ưu tiên: P0
Phụ thuộc: T0
Ước lượng: 3–4 giờ

Mục tiêu

Tạo môi trường mà các CLI agent có thể chạy giống nhau.

File đề xuất
.env.example
requirements.txt / pyproject.toml
README_DEV.md


scripts/
├── backup_db.py
├── restore_db.py
├── inspect_db.py
└── smoke_test.py
SQLite

Trước migration:

data/
├── production.db
└── backups/

Backup phải là bản copy có kiểm soát.

Nếu database đang được truy cập khi backup, không nên chỉ copy file một cách mù quáng.

Ưu tiên dùng SQLite backup API.

Acceptance criteria

 Clone project mới chạy được.

 Có .env.example.

 Có script backup DB.

 Backup restore được.

 Có smoke test gọi /health.

 Không commit file database production.

T2 — Audit schema và thiết lập migration

Ưu tiên: P0
Phụ thuộc: T0, T1
Ước lượng: 5–8 giờ

Mục tiêu

Chuyển từ:

ALTER TABLE thủ công

sang migration có version.

Nếu phù hợp với codebase, dùng Alembic.

File đề xuất
alembic.ini


alembic/
├── env.py
├── script.py.mako
└── versions/
Bảng/schema cần kiểm tra

Chưa thêm bảng ngay. Audit các bảng liên quan:

devices
device_categories
departments
locations
maintenance
repair_history
documents
ocr_documents
users

Tên thực tế phải lấy từ T0.

Migration có thể cần trong Giai đoạn 1

Chỉ thêm khi schema hiện tại thiếu:

device_history

hoặc:

audit_logs

Ví dụ tối thiểu:

SQL
CREATE TABLE device_history (
    id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    note TEXT,
    created_at DATETIME NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(id)
);

Không nên tạo bảng mới nếu 16 bảng hiện có đã chứa dữ liệu lịch sử phù hợp.

Acceptance criteria

 Có thể tạo DB từ migration.

 Có thể upgrade schema.

 Có thể rollback migration test.

 Migration chạy được trên bản copy DB.

 Không mất 1.211 thiết bị sau migration.

3. Tuần 1 — Xây dựng vertical slice thiết bị
T3 — Chuẩn hóa tầng database/repository

Ưu tiên: P0
Phụ thuộc: T2
Ước lượng: 4–6 giờ

Mục tiêu

Không để router chứa SQL trực tiếp khắp nơi.

File
app/
├── database.py
├── repositories/
│   └── device_repository.py
├── services/
│   └── device_service.py
└── dependencies.py
Chức năng
DeviceRepository
├── list()
├── get_by_id()
├── search()
├── count_by_status()
└── update()
Acceptance criteria

 Router không chứa SQL business logic.

 Có một nơi quản lý connection/session.

 Có test query list 1.211 thiết bị.

 Không tạo connection mới vô kiểm soát cho từng hàm.

T4 — Chuẩn hóa API contract và response schema

Ưu tiên: P0
Phụ thuộc: T2
Ước lượng: 4–5 giờ

File
app/
└── schemas/
    ├── device.py
    ├── common.py
    └── dashboard.py
Chuẩn response

Ví dụ:

JSON
{
  "items": [],
  "total": 1211,
  "page": 1,
  "page_size": 50
}

Lỗi:

JSON
{
  "detail": "Device not found"
}
Endpoint chưa thêm logic lớn

Chuẩn bị contract cho:

GET /api/v1/devices
GET /api/v1/devices/{id}
GET /api/v1/dashboard/summary
Acceptance criteria

 OpenAPI /docs hiển thị schema rõ ràng.

 Pagination thống nhất.

 Naming thống nhất giữa backend/frontend.

 Không trả raw database row lung tung.

T5 — Device List API

Ưu tiên: P0
Phụ thuộc: T3, T4
Ước lượng: 6–8 giờ

Đây là task quan trọng nhất để có demo sớm.

Endpoint
http
GET /api/v1/devices

Query:

page
page_size
q
status
department_id
category_id
location_id

Ví dụ:

GET /api/v1/devices?q=monitor&page=1&page_size=50
File
app/routers/devices.py
app/services/device_service.py
app/repositories/device_repository.py
app/schemas/device.py
DB

Đọc từ:

devices
departments
categories
locations

Tên bảng phải map theo schema thực tế.

Index cần kiểm tra

Nếu search thường xuyên:

device_code
device_name
serial_number
model
status
department_id

Không tạo index bừa bãi trên mọi cột.

Acceptance criteria

 Trả đủ 1.211 thiết bị qua pagination.

 Search theo mã/tên/model/serial.

 Filter không gây crash khi parameter rỗng.

 page và page_size được validate.

 Query thời gian chấp nhận được trên SQLite local.

 Không load toàn bộ 1.211 record vào frontend mỗi lần.

T6 — Frontend danh sách thiết bị

Ưu tiên: P0
Phụ thuộc: T5
Ước lượng: 6–8 giờ

Route

Nếu dùng vanilla JS:

/
#/devices

hoặc:

devices.html
File
frontend/
├── pages/
│   └── devices.js
├── components/
│   ├── device-table.js
│   ├── search-bar.js
│   └── pagination.js
└── services/
    └── api.js
UI tối thiểu
[ Search________________ ] [Status ▼] [Department ▼]


---------------------------------------------------------
Code | Device | Model | Serial | Department | Status
---------------------------------------------------------
...
---------------------------------------------------------


              < Previous  1 2 3  Next >
Acceptance criteria

 Search hoạt động.

 Filter hoạt động.

 Pagination hoạt động.

 Click row → Device Detail.

 Loading state.

 Empty state.

 API lỗi không làm vỡ toàn trang.

T7 — Device Detail API

Ưu tiên: P0
Phụ thuộc: T5
Ước lượng: 4–6 giờ

Endpoint
http
GET /api/v1/devices/{device_id}

Tùy schema, trả:

JSON
{
  "id": 1,
  "code": "TA-Q7-001",
  "name": "...",
  "manufacturer": "...",
  "model": "...",
  "serial_number": "...",
  "department": {},
  "location": {},
  "status": "...",
  "maintenance_summary": {},
  "document_count": 0
}
Endpoint phụ trợ

Nếu cần:

http
GET /api/v1/devices/{id}/history
GET /api/v1/devices/{id}/documents
Acceptance criteria

 ID không tồn tại trả 404.

 Không tạo N+1 query.

 Metadata đầy đủ cho demo.

 Không trả dữ liệu OCR 90 GB trực tiếp.

T8 — Device Detail Frontend

Ưu tiên: P0
Phụ thuộc: T7
Ước lượng: 5–7 giờ

Route
#/devices/:id
Component
components/
├── device-info.js
├── device-history.js
└── device-documents.js
UI
← Danh sách thiết bị


THIẾT BỊ: Monitor ABC


[Mã]          [Trạng thái]
[Model]        [Serial]
[Hãng]         [Khoa/Phòng]


────────────────────────────


Tabs:
Thông tin | Lịch sử | Hồ sơ
Acceptance criteria

 Truy cập trực tiếp URL detail hoạt động.

 Refresh không mất route.

 Back về danh sách.

 Hiển thị loading/error/not-found.

4. Điểm demo đầu tiên

Sau T8, dừng lại và demo.

Demo script 3 phút
1. Mở Dashboard/List
2. Tìm "Monitor"
3. Filter theo khoa/phòng
4. Chọn một thiết bị
5. Xem đầy đủ thông tin
6. Xem lịch sử hoặc hồ sơ

Đây là MVP Demo #1.

Nếu deadline nguy hiểm, có thể dừng phát triển tính năng mới tại đây và chuyển sang:

Test
Fix bug
Seed data
Demo polish
5. Tuần 2 — Dashboard, lịch sử, OCR sample
T9 — Dashboard Summary API

Ưu tiên: P1
Phụ thuộc: T3, T4
Ước lượng: 4–6 giờ

Endpoint
http
GET /api/v1/dashboard/summary

Có thể trả:

JSON
{
  "total_devices": 1211,
  "by_status": [],
  "by_department": [],
  "maintenance_due": 0,
  "repairing": 0
}
DB

Đọc aggregate từ:

devices
maintenance
departments
Lưu ý

Không chạy nhiều query nhỏ từ frontend.

Tránh:

GET /devices
GET /devices/status
GET /devices/department
GET /maintenance
GET /repair

cho mỗi lần mở dashboard nếu có thể tổng hợp server-side.

Acceptance criteria

 Một endpoint trả summary chính.

 Số tổng thiết bị khớp DB.

 Thống kê status khớp tổng số.

 Không double count khi JOIN.

T10 — Device History / Audit Trail

Ưu tiên: P1
Phụ thuộc: T2, T3
Ước lượng: 5–7 giờ

Endpoint
http
GET /api/v1/devices/{id}/history

Nếu cần mutation:

http
PATCH /api/v1/devices/{id}
DB

Ưu tiên dùng bảng có sẵn.

Nếu chưa có:

device_history
Transaction

Khi update:

BEGIN


UPDATE devices
INSERT device_history


COMMIT

Nếu insert history thất bại:

ROLLBACK

Không được để:

Device updated
History failed
Acceptance criteria

 Update và history atomic.

 Lịch sử sort theo thời gian giảm dần.

 Không ghi history khi transaction rollback.

 Test update lỗi giữa transaction.

T11 — Dashboard Frontend

Ưu tiên: P1
Phụ thuộc: T9
Ước lượng: 5–7 giờ

File
frontend/
├── pages/dashboard.js
└── components/
    ├── stat-card.js
    └── status-summary.js
MVP UI
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 1,211    │ │ Working  │ │ Repair   │
│ Tổng TB  │ │ ...      │ │ ...      │
└──────────┘ └──────────┘ └──────────┘


Theo trạng thái
[Chart hoặc simple bars]


Thiết bị cần chú ý
[Table]

Không cần làm chart phức tạp nếu dữ liệu chưa ổn.

Acceptance criteria

 Số liệu khớp API.

 Không hardcode 1.211.

 Loading/error state.

 Click từ summary → filter danh sách.

T12 — OCR/Document integration: chỉ làm vertical slice

Ưu tiên: P1/P2
Phụ thuộc: T7
Ước lượng: 6–10 giờ

Nguyên tắc quan trọng

Không import 90 GB vào SQLite.

SQLite chỉ nên giữ:

document_id
device_id
file_path
file_name
file_hash
ocr_status
ocr_text_path / extracted_summary
created_at

Kho file:

storage/
└── ocr/

hoặc external storage.

Endpoint
http
GET /api/v1/devices/{id}/documents
GET /api/v1/documents/{id}

Nếu cần preview:

http
GET /api/v1/documents/{id}/preview
Không làm trong Giai đoạn 1
❌ OCR toàn bộ 90 GB
❌ Semantic search toàn bộ kho
❌ RAG hoàn chỉnh
❌ Reprocess hàng loạt
Acceptance criteria

 Một thiết bị có thể liên kết document.

 Xem metadata document.

 Không copy file OCR vào database.

 File missing không làm API crash.

6. Background scheduler và cảnh báo
T13 — Scheduler tối thiểu

Ưu tiên: P2
Phụ thuộc: T9, T10
Ước lượng: 4–6 giờ

Ví dụ nhiệm vụ:

Mỗi ngày:
    kiểm tra thiết bị gần hạn bảo trì
    cập nhật trạng thái cảnh báo
Endpoint
http
GET /api/v1/alerts

Hoặc dashboard trả:

JSON
{
  "maintenance_due": []
}
File
app/
├── scheduler.py
└── services/
    └── alert_service.py
Cảnh báo quan trọng về FastAPI + scheduler

Nếu chạy:

uvicorn --workers 4

và scheduler được start trong:

Python
Run
@app.on_event("startup")

thì có thể xảy ra:

Worker 1 → chạy scheduler
Worker 2 → chạy scheduler
Worker 3 → chạy scheduler
Worker 4 → chạy scheduler

Kết quả:

Một job chạy 4 lần.

Giai đoạn 1 nên chọn

Phương án đơn giản:

API process
+
1 scheduler process riêng

hoặc chỉ chạy scheduler ở:

development / single worker
Acceptance criteria

 Job không chạy trùng.

 Có log lần chạy.

 Có thể disable scheduler bằng ENV.

 Restart server không tạo nhiều scheduler vô hạn.

7. T14 — Integration Test, regression và chuẩn bị demo

Ưu tiên: P0
Phụ thuộc: T5–T13 tùy scope
Ước lượng: 8–12 giờ

Backend test tối thiểu
tests/
├── test_health.py
├── test_devices.py
├── test_device_detail.py
├── test_dashboard.py
└── test_transactions.py
Test case bắt buộc
GET /health
GET /devices
GET /devices?q=...
GET /devices?page=-1
GET /devices/invalid-id
GET /devices/{id}
PATCH /devices/{id}
GET /devices/{id}/history
GET /dashboard/summary
SQLite test

Không chạy test phá DB production.

Dùng:

test.db

hoặc temporary database.

Acceptance criteria

 Test DB độc lập production.

 Smoke test pass.

 Luồng demo end-to-end pass.

 Migration test pass.

 Backup/restore test pass.

 Không có endpoint MVP trả HTTP 500 với input hợp lệ.

8. Bảng tổng hợp task và giờ
ID	Task	Phụ thuộc	Giờ
T0	Audit codebase + DB	—	4–6
T1	Environment + backup	T0	3–4
T2	Migration + schema audit	T0, T1	5–8
T3	Repository/DB layer	T2	4–6
T4	API contract/schema	T2	4–5
T5	Device List API	T3, T4	6–8
T6	Device List Frontend	T5	6–8
T7	Device Detail API	T5	4–6
T8	Device Detail Frontend	T7	5–7
T9	Dashboard API	T3, T4	4–6
T10	History/Audit	T2, T3	5–7
T11	Dashboard Frontend	T9	5–7
T12	OCR document slice	T7	6–10
T13	Scheduler/alerts	T9, T10	4–6
T14	Integration test/demo	các task MVP	8–12
Tổng

Khoảng:

73–106 giờ công

Không nên coi đây là 2 tuần làm một mình theo kiểu tuần tự hoàn toàn. Nên chạy song song theo dependency.

9. Kế hoạch tối ưu để demo sớm
Ngày 1
T0 → T1

Output:

Biết chính xác code đang có gì.

Backup được DB.

Không đụng mạnh vào kiến trúc.

Ngày 2
T2

Output:

Schema ổn định.

Migration chạy được.

Ngày 3

Song song:

Agent A → T3 Database layer
Agent B → T4 API schemas/contracts
Ngày 4
T5 Device List API

Trong khi đó frontend có thể bắt đầu dựng UI mock.

Ngày 5
T6 Device List UI

Cuối ngày 5: có thể demo danh sách 1.211 thiết bị.

Ngày 6
T7 Device Detail API
Ngày 7
T8 Device Detail Frontend
Cuối Tuần 1: DEMO MVP #1
Search
↓
Filter
↓
Open Device
↓
View Details
Ngày 8–9

Song song:

T9 Dashboard API
T10 History/Audit
Ngày 10
T11 Dashboard Frontend
Ngày 11
T12 OCR/document sample
Ngày 12
T13 Scheduler/alert

Nếu scheduler chưa cần cho demo, có thể bỏ T13 và dành thời gian cho test.

Ngày 13–14
T14
+
Bug fixing
+
Demo data verification
+
Backup
+
Regression test
10. Phân công tối ưu cho các CLI agent

Với workflow nhiều agent CLI, nên chia theo ranh giới file/module, không chia kiểu "mọi agent cùng sửa backend".

Agent 1 — Architect / Lead
T0
T2
Review PR/code
Migration strategy
Architecture decisions

Không nên code nhiều feature song song.

Agent 2 — Backend Device
T3
T5
T7

File ownership:

repositories/device_repository.py
services/device_service.py
routers/devices.py
schemas/device.py
Agent 3 — Frontend
T6
T8
T11

File ownership:

frontend/pages/
frontend/components/
frontend/services/api.js
Agent 4 — Data/DB
T1
T2
T10

Phụ trách:

backup
migration
transaction
audit/history
Agent 5 — QA/Integration

Bắt đầu từ ngày đầu:

API inventory
smoke tests
regression tests
test data
T14

Không để QA đến ngày cuối mới bắt đầu.

11. Rủi ro kỹ thuật cần kiểm tra kỹ
11.1 SQLite transaction

Đây là điểm quan trọng nhất.

Sai:

Python
Run
update_device()


try:
    insert_history()
except:
    pass

Có thể tạo dữ liệu:

Device = updated
History = missing

Nên đảm bảo các thao tác liên quan nằm trong cùng transaction.

Đặc biệt:

UPDATE thiết bị
+
INSERT lịch sử
+
UPDATE trạng thái bảo trì

phải có chiến lược commit rõ ràng.

11.2 SQLite concurrency

SQLite phù hợp cho MVP và dữ liệu 1.211 thiết bị, nhưng cần chú ý:

Nhiều request đọc → ổn
Nhiều request ghi đồng thời → dễ lock

Nên kiểm tra:

busy_timeout

WAL mode nếu phù hợp

connection lifecycle

write transaction ngắn

Không giữ transaction mở trong khi:

OCR
đọc file 90 GB
HTTP request external
AI processing
11.3 Migration

Không chạy migration trực tiếp lên DB duy nhất.

Quy trình:

production.db
      │
      ▼
backup
      │
      ▼
staging copy
      │
      ▼
migration test
      │
      ▼
verification
      │
      ▼
production

Sau mỗi migration kiểm tra:

SQL
SELECT COUNT(*) FROM devices;

và các bảng quan trọng.

11.4 Timezone

Không dùng lẫn:

datetime.now()
datetime.utcnow()

khắp codebase.

Nên thống nhất:

Lưu UTC hoặc timestamp có timezone → convert khi hiển thị.

Ví dụ:

Backend storage: UTC
Frontend display: Asia/Ho_Chi_Minh

Đặc biệt kiểm tra:

ngày bảo trì

lịch sử sửa chữa

scheduler chạy theo ngày

cảnh báo gần hạn

Nếu scheduler chạy lúc:

00:00 UTC

thì ở Việt Nam là:

07:00 ICT
11.5 Background task không nên xử lý OCR nặng

Không nên:

POST /upload
→ BackgroundTasks
→ OCR file hàng GB
→ Server restart
→ mất job

Giai đoạn 1 chỉ nên:

Upload/Register document
→ DB tạo trạng thái PENDING
→ worker/scheduler riêng xử lý

Cho MVP, thậm chí chỉ cần:

OCR metadata + existing file
12. Definition of Done cho Giai đoạn 1

Giai đoạn 1 được coi là hoàn thành khi chạy được demo:

1. Khởi động FastAPI.
2. Migration DB thành công.
3. Dashboard hiển thị số liệu từ DB.
4. Danh sách 1.211 thiết bị có pagination.
5. Search/filter hoạt động.
6. Click thiết bị → trang detail.
7. Có lịch sử thay đổi hoặc maintenance history.
8. Có ít nhất một document/OCR sample liên kết với thiết bị.
9. Update + history đảm bảo transaction.
10. Test không phá production DB.
Thứ tự ưu tiên cuối cùng
P0 — PHẢI CÓ
T0 → T1 → T2 → T3/T4 → T5 → T6 → T7 → T8 → T14


P1 — NÊN CÓ
T9 → T10 → T11 → T12


P2 — NẾU CÒN THỜI GIAN
T13
Khuyến nghị kiến trúc thực tế

Để demo sớm và tránh sa đà, tôi sẽ khóa phạm vi Giai đoạn 1 vào luồng:

Dashboard → 1.211 thiết bị → Search/Filter → Chi tiết → History → Document sample

Chưa làm OCR toàn kho 90 GB, chưa refactor toàn bộ 87 endpoint, chưa thêm tính năng AI/RAG lớn. Sau khi vertical slice này ổn định mới chuyển sang Giai đoạn 2.

Sources
Convert to PDF
ChatGPT can make mistakes. Check important info.

Think

