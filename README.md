# Medical Device Management System

Hệ thống quản lý thiết bị y tế cho Quận 7 - TP.HCM

## 🚀 Cài đặt nhanh

```bash
# Cài đặt Python dependencies
pip install -r requirements.txt

# Khởi chạy server
python app/main.py
```

## 📁 Cấu trúc thư mục

```
medical-device-app/
├── app/           # Backend API (FastAPI)
├── web/           # Frontend Dashboard
├── database/      # SQLite database
├── cli/           # Command-line tools
├── scripts/       # Utility scripts
└── docs/          # Documentation
```

## 🏥 Tính năng chính

- Quản lý thiết bị y tế theo khoa
- Theo dõi lịch hiệu chuẩn kiểm định
- Nhập dữ liệu tự động từ file PDF/MD
- Báo cáo thống kê thiết bị sắp hết hạn
- Hỗ trợ offline (SQLite)

## 📚 API Endpoints

- `GET /api/devices` - Liệt kê thiết bị
- `GET /api/devices/{id}` - Chi tiết thiết bị
- `GET /api/certificates` - Lịch kiểm định
- `GET /api/dashboard` - Thống kê tổng quan
- `POST /api/import` - Nhập dữ liệu từ file

---
*Phiên bản 1.0 - Quận 7, TP.HCM*