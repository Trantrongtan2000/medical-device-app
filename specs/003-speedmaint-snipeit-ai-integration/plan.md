# Implementation Plan: 003 - SpeedMaint CMMS, Snipe-IT, Gemini AI & Mistral OCR Integration

## 1. Architecture Overview
- **Backend:** FastAPI (Python 3.14 / 3.12), SQLite với WAL mode & Foreign Keys enabled.
- **Frontend:** HTML5, Vanilla CSS Design System ("Less, but better" Minimalist WCAG 2.1 AAA), Bootstrap 5, Bootstrap Icons.
- **AI & OCR Services:** `google-genai` (Gemini 2.5 Flash), `mistralai` (Mistral-OCR-4).
- **Key Manager:** `KeyPool` Singleton với SQLite persistence & Round-Robin / Auto-Failover.

## 2. API Endpoints Matrix
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/dashboard/summary` | Trả về 4 KPI chỉ số vận hành bệnh viện |
| `GET` | `/api/dashboard/facilities` | Danh sách 22 khoa phòng và số lượng thiết bị |
| `GET` | `/api/dashboard/categories` | Danh sách 10 nhóm phân loại thiết bị y tế |
| `GET` | `/api/devices` | Danh sách tài sản thiết bị y tế kèm Asset Tag & SpeedMaint Code |
| `POST` | `/api/devices` | Nhập mới thiết bị theo quy trình TLHD Mục 2a, 3 & NĐ 98 |
| `GET` | `/api/devices/{id}` | Chi tiết hồ sơ lý lịch máy, giấy kiểm định và nhật ký |
| `POST` | `/api/devices/transfer` | Điều chuyển & bàn giao máy giữa các khoa phòng |
| `GET` | `/api/audits` | Lịch sử kiểm kê tài sản hiện trường (Audit Trail) |
| `POST` | `/api/devices/audit` | Ghi nhận kết quả kiểm kê thực tế theo máy |
| `GET` | `/api/work-orders` | Danh sách phiếu công việc bảo trì chuẩn SpeedMaint |
| `POST` | `/api/work-orders` | Tạo phiếu công việc bảo trì SpeedMaint mới |
| `GET` | `/api/accessories` | Quản lý kho linh kiện & phụ tùng tiêu hao |
| `GET` | `/api/schedules` | Lịch kiểm định & bảo trì phòng ngừa (PM) |
| `GET` | `/api/export/csv` | Xuất danh mục tài sản ra tệp Excel CSV |
| `POST` | `/api/ai/chat` | Hội thoại với Trợ lý Gemini AI (có xoay key) |
| `POST` | `/api/ocr/process` | Bóc tách tài liệu với Mistral OCR (có xoay key) |
| `GET` | `/api/keys/config` | Lấy danh sách API keys và trạng thái xoay vòng |
| `POST` | `/api/keys/add` | Nhập thêm API keys vào danh sách xoay vòng |
| `POST` | `/api/keys/remove` | Xóa API key khỏi danh sách xoay vòng |
