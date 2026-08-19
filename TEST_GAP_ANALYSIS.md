# 🧪 PHÂN TÍCH KHOẢNG TRỐNG KIỂM THỬ (TEST GAP ANALYSIS)
## AUTOMATED TESTING STRATEGY — MEDICAL DEVICE APP (HTM V3)

> **Hiện trạng thực tế:** Dự án **chưa có thư mục `tests/`** và không tích hợp bất kỳ test runner tự động nào (`pytest`). Các file `test_*.py` trong `scripts/` (16 file) chỉ là các đoạn mã chạy thử nghiệm thủ công một lần, không có assertions chuẩn và không thể chạy hồi quy trong CI/CD.

---

## 1. MA TRẬN KHOẢNG TRỐNG KIỂM THỬ (TEST GAP MATRIX)

| Module / Nghiệp Vụ | Hiện Trạng Test Hiện Có | Test Cần Bổ Sung (Missing Tests) | Mức Độ Rủi Ro (Risk) | Độ Ưu Tiên (Priority) |
| :--- | :--- | :--- | :---: | :---: |
| **Quản lý Thiết Bị (CRUD Device)** | Script `test_create_device.py` (chạy thủ công) | Unit test tính duy nhất của Serial, Asset Tag, kiểm tra ràng buộc khoa phòng, Pydantic validation. | **CRITICAL** | **P0** |
| **Điều Chuyển Khoa (QT.08 Transfer)** | Không có test | Transaction test: Chuyển thiết bị sang khoa mới, tự động ghi lịch sử `device_transfers`, rollback khi lỗi. | **HIGH** | **P0** |
| **Kiểm Định & Hiệu Chuẩn (TT 05)** | Script `test_clean_rules.py` | Unit test tính toán số ngày hết hạn (Overdue/Warning), logic gắn chứng chỉ với máy, chống orphan certs. | **HIGH** | **P0** |
| **Bảo Trì & Sửa Chữa (QT.06 PM)** | Không có test | Unit & API tests cho quy trình tạo phiếu bảo trì, cập nhật trạng thái máy, tính chỉ số MTBF/MTTR. | **HIGH** | **P1** |
| **Hợp Đồng & Nhà Thầu (Contracts)** | Không có test | Test ràng buộc khóa ngoại: Không cho xóa nhà thầu/hợp đồng khi đang có thiết bị liên kết active. | **MEDIUM** | **P1** |
| **Nhập Liệu Master Data V6** | Script `test_simple.py` | Integration test kiểm tra tính toàn vẹn 1.211 thiết bị, đối soát mã kép, kiểm tra trùng lặp serial. | **HIGH** | **P0** |
| **Xác Thực & Phân Quyền (Auth)** | Không có test | Test đăng nhập JWT, hash mật khẩu, kiểm tra chặn truy cập khi sai quyền (RBAC 403 Forbidden). | **CRITICAL** | **P0** |
| **Tích Hợp AI & Key Rotation** | Script `test_ai_ocr_features.py` | Mock test cho Gemini/Mistral API, kiểm tra tự động xoay key khi gặp lỗi 429/503, cơ chế cooldown timer. | **MEDIUM** | **P2** |
| **Xử Lý Tài Liệu & Path Resolution**| Script `test_pdf_resolution.py` | Test bảo mật chống Path Traversal (`../../`), kiểm tra tính đúng đắn của mã băm SHA-256. | **HIGH** | **P1** |
| **Giao Diện Lâm Sàng (Frontend E2E)**| Không có test | Playwright E2E tests: Tìm kiếm thời gian thực, mở modal 5 tabs, lọc theo khoa phòng, điều chuyển máy. | **MEDIUM** | **P2** |

---

## 2. THIẾT KẾ HẠ TẦNG KIỂM THỬ MỤC TIÊU (TARGET TEST ARCHITECTURE)

```
tests/
├── conftest.py                  # Fixtures: In-Memory SQLite DB, TestClient, Mock AI
├── unit/                        # Kiểm thử đơn vị các Services & Models
│   ├── test_device_service.py
│   ├── test_calibration_service.py
│   ├── test_transfer_service.py
│   └── test_key_rotator.py
├── integration/                 # Kiểm thử tích hợp Database & Repositories
│   ├── test_db_foreign_keys.py
│   ├── test_device_repository.py
│   └── test_contract_repository.py
├── api/                         # Kiểm thử RESTful API Endpoints (FastAPI TestClient)
│   ├── test_devices_api.py
│   ├── test_contracts_api.py
│   ├── test_maintenance_api.py
│   └── test_auth_api.py
└── e2e/                         # Kiểm thử tự động giao diện (Playwright)
    ├── test_dashboard_ui.py
    └── test_device_modal_ui.py
```

---

## 3. CÁC CA KIỂM THỬ BẮT BUỘC (CRITICAL TEST CASES)

### Test Case 1: Đảm bảo tính duy nhất của Serial Number
```python
def test_create_device_duplicate_serial_raises_error(device_service, sample_device_data):
    # Tạo thiết bị đầu tiên thành công
    device_service.create_device(sample_device_data)
    
    # Tạo thiết bị thứ 2 có cùng số Serial -> Phải ném lỗi DuplicateSerialException
    with pytest.raises(DuplicateSerialException):
        device_service.create_device(sample_device_data)
```

### Test Case 2: Đảm bảo tính toàn vẹn Transaction khi điều chuyển thiết bị (QT.08)
```python
def test_transfer_device_atomic_transaction(transfer_service, db_session):
    device_id = 1
    new_facility_id = 5
    
    # Thực hiện điều chuyển
    transfer_record = transfer_service.transfer_device(
        device_id=device_id,
        to_facility_id=new_facility_id,
        transferred_by="Kỹ sư Trọng Tấn",
        reason="Hỗ trợ cấp cứu"
    )
    
    # Kiểm tra cả 2 bảng đều được cập nhật đồng thời
    device = db_session.execute("SELECT facility_id FROM devices WHERE id = ?", (device_id,)).fetchone()
    assert device["facility_id"] == new_facility_id
    assert transfer_record.id is not None
```

---

## 4. CHỈ TIÊU CHẤT LƯỢNG (QUALITY GATES)

* **Code Coverage**: Đạt tối thiểu **85%** đối với tầng `app/services/` và `app/repositories/`.
* **CI Execution Time**: Bộ test suite chạy hoàn tất trong dưới **30 giây**.
* **Zero Failure Gate**: 100% pull requests phải pass tất cả test cases trước khi merge vào nhánh chính (`main`).
