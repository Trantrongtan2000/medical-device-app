# Mapping Tính Năng - TLHD_QLTTBYT_V1.2.md

## Feature Mapping Table

| TLHD Chapter | Trang | Chức năng | Trạng thái | API Endpoints cần tạo |
|-------------|-------|------------|------------|----------------------|
| **1. Đăng nhập** | 4 | Xác thực người dùng | ⚠️ Cần thêm | POST /auth/login |
| **2. Danh mục** | 4 | Quản lý TTBYT | ✅ Có sẵn | GET/POST/PUT/DELETE /api/devices |
| | 6 | Quản lý Hãng sản xuất | ⚠️ Cần thêm | GET/POST/PUT/DELETE /api/manufacturers |
| | 8 | Quản lý Xuất xứ | ⚠️ Cần thêm | GET/POST/PUT/DELETE /api/countries |
| | 9 | Quản lý Nhà cung cấp | ⚠️ Cần thêm | GET/POST/PUT/DELETE /api/providers |
| **3. Nhập – Tồn** | 12 | Phiếu nhập | ❌ Chưa có | GET/POST/PUT/DELETE /api/inventory/entries |
| | 15 | Danh sách tồn | ❌ Chưa có | GET /api/inventory/stock |
| **4. Điều chuyển** | 15 | Điều chuyển kho | ❌ Chưa có | GET/POST/PUT/DELETE /api/transfers |
| | 17 | Nhận điều chuyển | ❌ Chưa có | POST /api/transfers/receive |
| **5. Hoàn trả** | 18 | Phiếu hoàn trả | ❌ Chưa có | GET/POST/PUT/DELETE /api/returns |
| | 21 | Nhận hoàn trả | ❌ Chưa có | POST /api/returns/receive |
| | 22 | Xác nhận hoàn thành | ❌ Chưa có | POST /api/returns/confirm |
| **6. Sửa chữa** | 25 | Yêu cầu sửa chữa | ❌ Chưa có | GET/POST/PUT/DELETE /api/repairs |
| | 28 | Nhận yêu cầu sửa chữa | ❌ Chưa có | POST /api/repairs/accept |
| | 29 | Xác nhận sửa chữa | ❌ Chưa có | POST /api/repairs/confirm |
| **7. Kiểm tra vận hành** | 33 | Phiếu kiểm tra | ❌ Chưa có | GET/POST/PUT/DELETE /api/inspections |
| | 37 | Xác nhận hoàn thành | ❌ Chưa có | POST /api/inspections/confirm |
| **8. Kiểm định** | 42 | Phiếu kiểm định | ✅ Có sẵn (calibration) | GET/POST/PUT/DELETE /api/certificates |
| | 46 | Xác nhận hoàn thành | ❌ Chưa có | POST /api/certificates/confirm |
| **9. Bảo trì** | 50 | Phiếu bảo trì | ❌ Chưa có | GET/POST/PUT/DELETE /api/maintenance |
| | 54 | Xác nhận hoàn thành | ❌ Chưa có | POST /api/maintenance/confirm |

---

## 🎯 **Gợi ý triển khai tính năng (Theo thứ tự ưu tiên)**

### **Giai đoạn 1: Cơ bản (Đã có)**
- ✅ Quản lý thiết bị y tế
- ✅ Theo dõi hiệu chuẩn kiểm định
- ✅ Dashboard thống kê

### **Giai đoạn 2: Quản lý kho (Cần phát triển)**
- Thêm bảng `inventory_entries` cho phiếu nhập
- Thêm bảng `transfers` cho điều chuyển
- Thêm bảng `returns` cho hoàn trả
- Thêm trường `location` cho thiết bị

### **Giai đoạn 3: Quản lý dịch vụ**
- Thêm bảng `repairs` cho sửa chữa
- Thêm bảng `inspections` cho kiểm tra
- Thêm bảng `maintenance_schedules` (da có)

### **Giai đoạn 4: Quản lý danh mục**
- Thêm Manufacturers, Countries, Providers

---

## 🚨 **Lỗi đã phát hiện trong audit**

| Bug | Vị trí | Trạng thái |
|-----|--------|------------|
| SQL Parameter bind | routes.py:38-44 | ✅ Đã sửa |
| CSS Class mismatch | style.css vs app.js | ⚠️ Cần sửa |
| CORS | main.py:28 | ⚠️ Cần thu hẹp |
| Endpoint paths | api.js | ✅ Đã sửa |

---

## 📊 **Thống kê hiện tại**

- **Devices:** 18 records
- **Facilities:** 7 records  
- **Categories:** 4 records
- **Certificates:** 18 records
- **Overdue devices:** 3 records