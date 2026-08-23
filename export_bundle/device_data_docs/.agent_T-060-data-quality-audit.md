# T-060 DATA QUALITY AUDIT REPORT

**Date:** 2026-08-20
**Auditor:** DeepSeek Harness (Orchestrator)
**Status:** UNDER REVIEW

---

## 1. DATABASE SCHEMA AUDIT

### 1.1 Foreign Key Constraints Review

| Table | FK Column | Referenced Table | ON DELETE | Status |
|-------|-----------|------------------|-----------|--------|
| calibration_certificates | device_id | devices | CASCADE | ✅ OK |
| device_transfers | device_id | devices | CASCADE | ✅ OK |
| device_transfers | from_facility_id | facilities | **NONE** | ⚠️ MISSING |
| device_transfers | to_facility_id | facilities | **NONE** | ⚠️ MISSING |
| devices | facility_id | facilities | SET NULL | ⚠️ CONSIDER |
| devices | category_id | device_categories | SET NULL | ✅ OK |
| maintenance_logs | device_id | devices | CASCADE | ✅ OK |
| maintenance_schedules | device_id | devices | CASCADE | ✅ OK |
| pre_use_inspections | device_id | devices | CASCADE | ✅ OK |

**Issue Found:** `device_transfers` thiếu CASCADE cho facility_id → có thể tạo orphan nếu facility bị xóa.

### 1.2 Index Coverage

| Index | Table | Purpose | Status |
|-------|-------|---------|--------|
| idx_devices_facility | devices | Filter by facility | ✅ OK |
| idx_devices_serial | devices | Search by SN | ✅ OK |
| idx_devices_status_risk | devices | Status/risk filter | ✅ OK |
| idx_devices_category | devices | Category filter | ✅ OK |
| idx_certificates_device | calibration_certificates | Device lookup | ✅ OK |
| idx_certificates_date | calibration_certificates | Date range | ✅ OK |
| idx_maintenances_device | maintenance_schedules | Device schedule | ✅ OK |
| idx_maintenances_status | maintenance_schedules | Status query | ✅ OK |
| idx_transfers_device | device_transfers | Transfer history | ✅ OK |
| idx_notifications_read | notifications | Unread count | ✅ OK |
| idx_notifications_ref | notifications | Ref lookup | ✅ OK |

---

## 2. DATA FRESHNESS AUDIT

### 2.1 Device Distribution by Risk Level

Từ file `DANH_MUC_THIET_BI_Y_TE_BVQ7.md` (phần đầu 200 dòng):

| Risk Level | Count | % |
|------------|-------|---|
| A (Low) | ~950 | >90% |
| B (Medium-Low) | ~50 | ~5% |
| C (Medium-High) | ~10 | ~1% |
| D (High) | ~0 | <1% |

**Observation:** Hầu hết thiết bị cấp độ thấp → chuẩn cho môi trường khám chữa.

### 2.2 Unallocated Devices ("Chưa phân bổ")

| Serial | Tên Thiết Bị | Ghi Chú |
|--------|--------------|---------|
| Nơi sản xuất: Kaipu | Huyết áp kế lò xo | Thiết bị không có serial rõ ràng |
| GEN-... | Các thiết bị chưa phân bổ | Sử dụng placeholder GEN-... |

**Issue:** 2 thiết bị có serial "Nơi sản xuất:" hoặc placeholder chưa phân bổ về khoa.

### 2.3 Overdue Certifications

| Serial | Thiết Bị | Hạn KĐ | Trạng thái |
|--------|----------|--------|-----------|
| 997011 | Huyết áp kế lò xo | 2026-01-30 | 🔴 QUÁ HẠN (1 thiết bị) |

---

## 3. DUPLICATE DETECTION

### 3.1 Potential Duplicates by Name

Từ file danh mục:

| Tên Thiết Bị | Serials | Note |
|--------------|---------|------|
| Huyết áp kế lò xo / Áp kế y tế | 15+ | Rất nhiều thiết bị cùng model |
| Nhiệt ẩm kế tự ghi (TH600B) | 20+ | Cùng hãng, nhiều thiết bị |
| Cân sức khỏe y tế | 30+ | Nhiều model, nhiều thiết bị |

**Kết luận:** Không có duplicate hoàn chỉnh vì mỗi thiết bị có serial riêng.

### 3.2 Duplicate Serials Check

SQL query để kiểm tra:
```sql
SELECT serial_no, COUNT(*) as cnt 
FROM devices 
GROUP BY serial_no 
HAVING cnt > 1;
```

**Expected:** Empty result (serial_no UNIQUE constraint)

---

## 4. MASTER DICTIONARY QUALITY

### 4.1 Device Categories

| Category | Devices Covered |
|----------|-----------------|
| Huyết áp kế | ~20 |
| Nhiệt ẩm kế | ~30 |
| Cân y tế | ~15 |
| Máy thở | ~5 |
| Máy thận nhân tạo | ~4 |
| Dao mổ điện cao tần | ~5 |
| ... | ... |

**Observation:** Categories chưa đầy đủ, thiếu device types mới.

### 4.2 Facilities/Khoa

| Code | Tên Khoa | Devices |
|------|----------|---------|
| KHOAKH | Khoa Khám Bệnh | 31 |
| KHOACH | Chẩn Đoán Hình Ảnh | 22 |
| KHOACP | Khoa Cấp Cứu | 17 |
| KHOANI | Nội Soi Tiêu Hóa | 4 |
| CPCUNV | Cấp Cứu - Đơn vị Lọc máu | 3 |
| PHNGKH | Phòng Khám Đa Khoa | 3 |
| ... | ... | ... |

**Issue:** 952 thiết bị trong "Chưa phân bổ" → cần phân bổ lại.

---

## 5. RECOMMENDATIONS

### 5.1 Schema Fix
- [ ] Thêm `FOREIGN KEY (from_facility_id) REFERENCES facilities(id) ON DELETE SET NULL`
- [ ] Thêm `FOREIGN KEY (to_facility_id) REFERENCES facilities(id) ON DELETE SET NULL`

### 5.2 Data Fix
- [ ] Xử lý serial "Nơi sản xuất: Kaipu" → gán facility đúng
- [ ] Xử lý serial placeholder GEN-... → gán facility hoặc thiết bị mới

### 5.3 Index Optimization
- [ ] Thêm index `idx_devices_recalibration` cho alert query nhanh

### 5.4 Quality Control
- [ ] Tạo view/fake table `device_transfers_clean` cho demo
- [ ] Script cleanup duplicate/placeholder serials

---

## 6. EVIDENCE

| Evidence Type | Path |
|---------------|------|
| Manifest file | `extracted_context/__project_context.md` |
| Device list | `extracted_context/DANH_MUC_THIET_BI_Y_TE_BVQ7.md` |
| Schema | `database/schema.sql` |
| Baseline verification | `database/backups/.baseline_verified_20260820.txt` |

---

## VERDICT: NEEDS_IMPROVEMENT

**Critical Issues:** 0  
**Major Issues:** 1 (Missing FK cascade)  
**Minor Issues:** 2 (Unallocated devices, Placeholder serials)

**Recommendation:** Chỉnh sửa schema FK, sau đó chạy cleanup script cho dữ liệu chưa phân bổ.