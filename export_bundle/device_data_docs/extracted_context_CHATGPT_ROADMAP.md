# Kế hoạch phát triển (ChatGPT roadmap)

Kế hoạch phát triển hệ thống quản lý thiết bị y tế
1. Đánh giá hiện trạng và mức độ hoàn thiện
1.1. Mức độ bao phủ nghiệp vụ
Nghiệp vụ	Hiện trạng	Mức độ
Danh mục thiết bị	1.211 thiết bị, 10 nhóm, 39 khoa/phòng	Tốt
Hồ sơ nhà cung cấp	102 liên hệ	Khá
Hợp đồng/mua sắm	198 hợp đồng	Khá
Kiểm định/chứng nhận	107 bản ghi cert	Có dữ liệu nhưng thiếu quản lý vòng đời
Bảo trì/sửa chữa	48 maintenance_logs	Yếu
Lập lịch bảo trì	maintenance_schedules = 0	Thiếu nghiêm trọng
Điều chuyển	3 bản ghi	Module chưa được vận hành thực tế
Kiểm tra trước sử dụng	1 bản ghi	Gần như chưa triển khai
Phản hồi/sự cố	2 bản ghi	Chưa trở thành quy trình vận hành
Nhân sự BME	6 nhân sự	Cơ bản
Trực/on-call	92 bản ghi	Tốt, có dữ liệu hoạt động
Thanh lý	Chưa thấy bảng chuyên biệt	Thiếu
Bàn giao/nghiệm thu	Chưa thấy module nghiệp vụ đầy đủ	Thiếu
Kho phụ tùng	Chưa có	Thiếu
Báo cáo KPI	Chưa thấy schema chuyên biệt	Thiếu/giới hạn
Quản lý tài liệu	OCR 37.385 file nhưng chưa gắn chặt entity	Rất có tiềm năng
Full-text search	Chưa mô tả index/search thống nhất	Cần triển khai
Kết luận kiến trúc

Hệ thống hiện tại không còn ở mức prototype: phần master data, thiết bị, hợp đồng, chứng chỉ, nhân sự và API đã có nền móng tốt.

Tuy nhiên, dữ liệu cho thấy hệ thống đang mất cân bằng:

Master Data mạnh, Operational Workflow yếu.

Có thể xem mức độ hoàn thiện hiện tại:

Quản lý hồ sơ tài sản: ~70–80%

Quản lý vòng đời thiết bị: ~45–55%

CMMS/bảo trì: ~25–35%

Compliance tự động: ~30–40%

Document Intelligence/OCR: nền tảng mạnh nhưng mới ~40% giá trị được khai thác.

Rủi ro lớn nhất không phải là thiếu thêm CRUD endpoint, mà là thiếu workflow bắt buộc biến dữ liệu thành quy trình vận hành hàng ngày.

2. Các lỗ hổng lớn nhất và ưu tiên
P0 — Phải xử lý ngay
2.1. maintenance_schedules = 0

Đây là lỗ hổng nghiêm trọng nhất.

Hiện có:

1.211 thiết bị
48 maintenance_logs
0 maintenance_schedules

Điều này cho thấy hệ thống chỉ đang ghi nhận sự kiện đã xảy ra, nhưng chưa quản lý được công việc phải xảy ra trong tương lai.

Thiếu:

Chu kỳ bảo trì.

Ngày bảo trì tiếp theo.

Sinh work order tự động.

Phân công BME.

SLA.

Trạng thái overdue.

Dashboard thiết bị sắp đến hạn.

Ưu tiên: P0

2.2. Kiểm định/chứng chỉ chưa có cơ chế vòng đời

107 bản ghi certs là một nền tảng tốt, nhưng cần kiểm tra:

cert
 ├── issue_date
 ├── expiry_date
 ├── certificate_no
 └── document

Nếu chưa có hệ thống:

cảnh báo 90 ngày,

cảnh báo 60 ngày,

cảnh báo 30 ngày,

quá hạn,

trạng thái compliance,

thì database chỉ đóng vai trò kho lưu chứng chỉ, chưa phải hệ thống compliance.

Ưu tiên: P0

2.3. pre_use_inspection = 1

Đây có thể là module bị bỏ quên hoặc chưa tích hợp vào UI/workflow.

Với thiết bị y tế, cần phân biệt:

Kiểm tra trước khi đưa vào sử dụng lần đầu.

Kiểm tra sau sửa chữa.

Kiểm tra sau điều chuyển.

Kiểm tra trước khi vận hành.

Kiểm tra an toàn định kỳ.

Nên thiết kế lại thành một workflow thống nhất:

Thiết bị mới
      ↓
Bàn giao
      ↓
Nghiệm thu kỹ thuật
      ↓
Pre-use inspection
      ↓
ACTIVE

Nếu không đạt:

QUARANTINE / OUT_OF_SERVICE

Ưu tiên: P0

2.4. transfers = 3

Với 1.211 thiết bị và 39 facilities, chỉ 3 lần điều chuyển là dấu hiệu:

Module chưa tiện sử dụng.

Hoặc quy trình thực tế chưa được số hóa.

Hoặc dữ liệu đang nằm trong Excel/PDF.

Cần biến điều chuyển thành một workflow có QR/barcode:

Yêu cầu điều chuyển
        ↓
Phê duyệt
        ↓
Bàn giao bên gửi
        ↓
Xác nhận bên nhận
        ↓
Kiểm tra sau điều chuyển
        ↓
Cập nhật location

Ưu tiên: P1, nhưng nên làm sau maintenance/compliance.

2.5. Thiếu Repair/Incident workflow độc lập

maintenance_logs có thể đang gộp:

bảo trì,

sửa chữa,

hiệu chuẩn,

kiểm tra.

Nên tách khái niệm:

Preventive Maintenance
Corrective Maintenance
Calibration
Inspection
Incident / Failure

Nếu không tách, sau này rất khó tính:

MTBF,

MTTR,

downtime,

failure rate,

repair cost,

vendor performance.

Ưu tiên: P0/P1

3. Roadmap 3 giai đoạn
Giai đoạn 1 — 0 đến 2 tuần
Mục tiêu

Biến hệ thống từ “Asset Registry” thành “Operational Medical Equipment Management”.

Ưu tiên:

P0.1 — Chuẩn hóa trạng thái vòng đời thiết bị

Thêm state machine:

DRAFT
RECEIVED
ACCEPTED
PRE_USE_INSPECTION
ACTIVE
MAINTENANCE
OUT_OF_SERVICE
REPAIR
TRANSFER_PENDING
RETIRED
DISPOSED

Không nên cho phép frontend cập nhật status tự do.

Endpoint:

http
POST /devices/{id}/status-transition
GET  /devices/{id}/timeline

Tạo bảng:

SQL
device_status_history

Schema:

SQL
id
device_id
from_status
to_status
reason
reference_type
reference_id
changed_by
changed_at
P0.2 — Triển khai Maintenance Schedule
Bảng
SQL
maintenance_plans
id
device_id
maintenance_type
frequency_days
last_completed_at
next_due_at
assigned_staff_id
vendor_id
estimated_duration
checklist_template_id
is_active
created_at
updated_at

Nên hỗ trợ:

TIME_BASED
USAGE_BASED
MANUFACTURER_REQUIRED
REGULATORY_REQUIRED

Endpoint:

http
GET    /maintenance/plans
POST   /maintenance/plans
GET    /maintenance/plans/{id}
PUT    /maintenance/plans/{id}
DELETE /maintenance/plans/{id}


POST   /maintenance/plans/generate
GET    /maintenance/due
GET    /maintenance/overdue
Work Order

Không nên chỉ dùng maintenance_logs.

Tạo:

SQL
work_orders
id
code
device_id
type
priority
status
scheduled_at
due_at
assigned_to
vendor_id
description
created_at
completed_at

Trạng thái:

OPEN
ASSIGNED
IN_PROGRESS
WAITING_PARTS
WAITING_VENDOR
COMPLETED
CANCELLED
OVERDUE

Endpoint:

http
POST /work-orders
GET /work-orders
GET /work-orders/{id}
PATCH /work-orders/{id}
POST /work-orders/{id}/start
POST /work-orders/{id}/complete
P0.3 — Compliance Engine

Thay vì chỉ query trực tiếp certs, tạo một lớp kiểm tra:

http
GET /compliance/dashboard
GET /compliance/expiring
GET /compliance/expired

Logic:

expiry_date - today


<= 90 days → WARNING
<= 60 days → ALERT
<= 30 days → CRITICAL
< 0         → EXPIRED

Có thể dùng background scheduler:

APScheduler / Celery / cron

Với SQLite và quy mô phòng khám, giai đoạn đầu có thể dùng:

APScheduler + FastAPI
P0.4 — Dashboard vận hành

Dashboard đầu tiên chỉ cần 6 chỉ số:

Total Devices
Active Devices
Maintenance Due
Maintenance Overdue
Certificates Expiring
Devices Out of Service

Endpoint:

http
GET /dashboard/summary
GET /dashboard/alerts
Giai đoạn 2 — 2 đến 8 tuần
Mục tiêu

Hoàn thiện CMMS + Document Management + Asset Lifecycle.

P1.1 — Incident & Repair Management

Tạo:

SQL
incidents
id
code
device_id
reported_by
reported_at
symptom
severity
status
downtime_start
downtime_end
root_cause
resolution

Severity:

LOW
MEDIUM
HIGH
CRITICAL

Workflow:

USER REPORT
    ↓
TRIAGE
    ↓
BME ASSIGNED
    ↓
INTERNAL REPAIR
    ├── FIXED
    └── VENDOR REPAIR
              ↓
        POST_REPAIR_TEST
              ↓
           CLOSED

Endpoint:

http
POST /incidents
GET  /incidents
GET  /incidents/{id}
POST /incidents/{id}/assign
POST /incidents/{id}/repair
POST /incidents/{id}/close
P1.2 — Kho phụ tùng

Schema:

SQL
spare_parts
id
part_code
name
manufacturer
model
category_id
unit
minimum_stock
current_stock
storage_location
unit_cost
is_active
SQL
spare_part_transactions
id
part_id
transaction_type
quantity
work_order_id
reference_type
reference_id
performed_by
created_at

Loại giao dịch:

IN
OUT
RETURN
ADJUSTMENT
RESERVED

Nên thêm bảng liên kết:

SQL
device_spare_parts

Để biết:

Model X thường sử dụng phụ tùng nào?

Endpoint:

http
GET  /spare-parts
POST /spare-parts
GET  /spare-parts/low-stock
POST /spare-parts/transactions
GET  /spare-parts/transactions
P1.3 — Điều chuyển thiết bị

Nâng cấp transfers.

Schema nên có:

id
transfer_code
device_id
from_facility_id
to_facility_id
requested_by
approved_by
requested_at
approved_at
shipped_at
received_at
status
condition_before
condition_after
handover_document_id

Workflow:

DRAFT
 ↓
REQUESTED
 ↓
APPROVED
 ↓
IN_TRANSIT
 ↓
RECEIVED
 ↓
INSPECTED
 ↓
COMPLETED

Endpoint:

http
POST /transfers
POST /transfers/{id}/approve
POST /transfers/{id}/dispatch
POST /transfers/{id}/receive
POST /transfers/{id}/inspect
P1.4 — Bàn giao, nghiệm thu và pre-use inspection

Tạo:

SQL
acceptance_records
id
device_id
contract_id
supplier_id
acceptance_date
technical_result
clinical_result
accepted_by
status
notes

Checklist:

SQL
inspection_templates
inspection_template_items
inspection_records
inspection_results

Như vậy pre_use_inspection không còn là bảng đơn lẻ khó mở rộng.

Endpoint:

http
POST /devices/{id}/acceptance
POST /devices/{id}/inspection
GET  /devices/{id}/inspection-history
P1.5 — Tích hợp kho OCR thành Document Hub

Kho hiện có:

37.385 file
90 GB
20.717 PDF
9.682 Markdown

Đây là tài sản dữ liệu rất lớn. Không nên copy toàn bộ file vào database.

Tạo bảng documents
SQL
documents
id
document_code
file_name
file_path
file_hash
mime_type
source_type
ocr_status
created_at
updated_at
Metadata OCR
SQL
document_content
document_id
content_text
content_md
language
page_count
ocr_engine
processed_at
Gắn tài liệu với entity

Không nên thêm:

device_id
contract_id
cert_id

trực tiếp vào documents.

Dùng polymorphic relation:

SQL
document_links
id
document_id
entity_type
entity_id
relation_type
confidence
linked_by
created_at

Ví dụ:

DOCUMENT
    │
    ├── DEVICE 001
    │
    ├── CONTRACT 2024-001
    │
    └── CERTIFICATE 2025-002

relation_type:

MANUAL
SERVICE_MANUAL
CONTRACT
ACCEPTANCE
HANDOVER
MAINTENANCE
REPAIR
CALIBRATION
INSPECTION
CERTIFICATE
INVOICE
OTHER

Endpoint:

http
POST /documents
GET  /documents
GET  /documents/{id}
POST /documents/{id}/links
GET  /devices/{id}/documents
GET  /contracts/{id}/documents
Full-text search

Với SQLite, giai đoạn đầu dùng:

SQL
SQLite FTS5
SQL
CREATE VIRTUAL TABLE document_search
USING fts5(
    document_id UNINDEXED,
    content,
    tokenize='unicode61'
);

Endpoint:

http
GET /search?q=

Nên trả về:

JSON
{
  "query": "máy gây mê",
  "results": [
    {
      "document_id": 123,
      "document_type": "MAINTENANCE",
      "entity": {
        "type": "DEVICE",
        "id": 55
      },
      "snippet": "...máy gây mê..."
    }
  ]
}
Giai đoạn 3 — Sau 8 tuần
Mục tiêu

Xây dựng hệ thống quản lý vòng đời thiết bị hoàn chỉnh và nền tảng phân tích.

P2.1 — Reporting & Analytics

Tạo bảng aggregate nếu cần:

SQL
device_metrics_daily
date
device_id
downtime_hours
maintenance_count
repair_count
maintenance_cost
repair_cost
availability

Không nên ghi mọi metric bằng trigger phức tạp ngay từ đầu. Có thể tính từ:

incidents
work_orders
maintenance_logs
spare_part_transactions

sau đó materialize theo ngày.

KPI nên có
Reliability
MTBF
MTTR
Failure Rate
Availability
Downtime
Maintenance
PM Compliance
Overdue PM
Corrective vs Preventive Ratio
Maintenance Cost
Compliance
Expired Certificates
Certificates Expiring
Devices Without Inspection
Devices Without Maintenance Plan
Financial
Repair Cost / Device
Vendor Cost
Contract Utilization
Cost of Ownership

Endpoint:

http
GET /reports/dashboard
GET /reports/maintenance
GET /reports/reliability
GET /reports/compliance
GET /reports/cost
GET /reports/export
P2.2 — Thanh lý

Tạo:

SQL
disposal_records
id
device_id
reason
technical_assessment
book_value
disposal_method
approved_by
disposed_at
document_id
status

Workflow:

ACTIVE
 ↓
RETIRE_REQUESTED
 ↓
TECHNICAL_EVALUATION
 ↓
APPROVED
 ↓
DISPOSED
P2.3 — QR/Barcode Workflow

Mỗi thiết bị:

Asset Code
QR Code
Serial Number

QR dẫn tới:

/devices/{asset_code}

Mobile workflow:

Scan QR
   ↓
View Device
   ↓
Report Incident
   ↓
Create Work Order
   ↓
Perform Inspection

Đây là bước quan trọng để tăng dữ liệu thực tế cho:

transfers
pre_use_inspection
feedback
maintenance_logs
4. Schema bổ sung đề xuất
Core architecture
devices
 │
 ├── device_status_history
 ├── maintenance_plans
 │      └── work_orders
 │              └── work_order_parts
 │
 ├── incidents
 │
 ├── inspection_records
 │
 ├── transfers
 │
 ├── acceptance_records
 │
 ├── disposal_records
 │
 ├── certs
 │
 └── document_links
          │
          └── documents
                  └── document_content (FTS)
5. Thứ tự ưu tiên theo Giá trị × Rủi ro
Ưu tiên	Module	Giá trị	Rủi ro nếu thiếu
P0	Maintenance Plans	Rất cao	Rất cao
P0	Work Orders	Rất cao	Rất cao
P0	Certificate Expiry Alert	Rất cao	Rất cao
P0	Device Lifecycle/Status	Cao	Rất cao
P0	Incident/Repair Workflow	Rất cao	Cao
P1	OCR Document Hub	Rất cao	Trung bình
P1	Acceptance/Inspection	Cao	Cao
P1	Transfer Workflow	Cao	Trung bình
P1	Spare Parts	Cao	Trung bình
P1	Full-text Search	Cao	Thấp
P2	Reporting/Analytics	Cao	Thấp
P2	Disposal	Trung bình	Trung bình
P2	QR/Mobile Workflow	Cao	Thấp
6. Kế hoạch triển khai thực tế
Tuần 1
[ ] Audit 87 endpoint hiện có
[ ] Map endpoint → module → bảng database
[ ] Chuẩn hóa device status
[ ] Tạo device_status_history
[ ] Tạo maintenance_plans
[ ] Tạo work_orders
[ ] Migration SQLite
Tuần 2
[ ] Maintenance scheduler
[ ] Due/Overdue engine
[ ] Certificate expiry engine
[ ] Alert API
[ ] Dashboard summary
[ ] Test 1.211 thiết bị
Tuần 3–4
[ ] Incident management
[ ] Repair workflow
[ ] Acceptance records
[ ] Inspection templates
[ ] Pre-use inspection workflow
[ ] Transfer workflow
Tuần 5–6
[ ] Documents table
[ ] Document links
[ ] Import OCR metadata
[ ] SQLite FTS5
[ ] Search API
[ ] Device/Contract document UI
Tuần 7–8
[ ] Spare parts
[ ] Work order parts consumption
[ ] KPI engine
[ ] Maintenance reports
[ ] Compliance reports
[ ] Export Excel/PDF
Sau tuần 8
[ ] Disposal workflow
[ ] QR scanning
[ ] Mobile-first technician workflow
[ ] Predictive maintenance
[ ] OCR auto-classification
[ ] Semantic/RAG search
7. Khuyến nghị kiến trúc quan trọng nhất

Không nên tiếp tục phát triển theo kiểu:

“Thiếu bảng nào thì thêm bảng đó, thiếu API nào thì thêm endpoint đó.”

Nên chuyển hệ thống sang mô hình Asset Lifecycle + Workflow + Event History.

Kiến trúc mục tiêu:

                    ┌─────────────────┐
                    │   DEVICE CORE   │
                    │  1.211 devices  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
     MAINTENANCE        COMPLIANCE         LIFECYCLE
          │                  │                  │
     Work Orders         Certificates      Transfer
     Repair              Expiry Engine     Acceptance
     Spare Parts         Alerts            Inspection
                                              Disposal
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                      DOCUMENT HUB
                             │
                ┌────────────┴────────────┐
                │       OCR + FTS          │
                │    37.385 documents      │
                └────────────┬────────────┘
                             │
                        REPORTING
Mốc MVP nên nhắm tới

Với mục tiêu hoàn thành đồ án, tôi khuyến nghị không cố xây toàn bộ CMMS ngay.

MVP có giá trị trình diễn cao nhất là:

MVP-1

Quản lý 1.211 thiết bị.

Dashboard tổng quan.

Lịch bảo trì tự động.

Work Order.

Cảnh báo kiểm định sắp hết hạn.

Báo sự cố/sửa chữa.

Timeline vòng đời thiết bị.

Gắn PDF/Markdown OCR vào thiết bị.

Full-text search tài liệu.

Chỉ cần hoàn thiện 9 chức năng này theo workflow xuyên suốt, hệ thống sẽ thể hiện rõ:

Một nền tảng quản lý vòng đời thiết bị y tế tích hợp CMMS + Compliance + OCR Document Intelligence, thay vì chỉ là một website CRUD quản lý thiết bị.

Đó là hướng có giá trị nghiệp vụ cao nhất, rủi ro triển khai thấp nhất và phù hợp nhất để hoàn thành đồ án trong thời gian ngắn.


