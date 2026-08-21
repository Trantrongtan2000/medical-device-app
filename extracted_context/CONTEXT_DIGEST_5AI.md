[CẬP NHẬT NGỮ CẢNH — ĐỌC KỸ, DÙNG CHO MỌI CÂU TRẢ LỜI TIẾP THEO]

Đây là CONTEXT CHÍNH XÁC từ codebase thực tế (dự án quản lý TBYT Tâm Anh Q7, FastAPI + SQLite + vanilla JS). Roadmap bạn đã lập vẫn giữ nguyên, NHƯNG một số tên bảng/giả định schema trong các bài trước KHÔNG khớp hiện trạng. Dùng bảng dưới đây làm chuẩn khi đề xuất endpoint/schema/migration từ giờ.

## SCHEMA THỰC TẾ database/devices.db (17 bảng, 1.211 devices)
- devices (n=1211): device_name, model, serial_no, certification_no, calibration_stamp_no, facility_id, category_id, manufacturer, country_of_manufacturer, year_of_manufacture, risk_level, status, installation_date, calibration_date, recalibration_date, source_pdf, pdf_path, md_path, notes, created_at, updated_at, contract_no, supplier_name, handover_date, form_code, party_giver, party_receiver, md_source_path
  → ĐÃ CÓ sẵn: risk_level, certification_no, calibration_stamp_no, source_pdf, pdf_path, md_path, contract_no, party_giver/party_receiver.
- facilities (n=39): id, name, code, location, manager
- device_categories (n=10): id, name, description, safety_level
- contracts (n=198): id, contract_no, contract_name, supplier_name, handover_date, contract_value, warranty_period_months, status, notes
- supplier_contacts (n=102): id, supplier_name, contact_person, phone, email, service_scope
- calibration_certificates (n=107) [= bảng "certs" các bài trước gọi]: id, device_id, certificate_no, calibration_date, recalibration_date, stamp_no, result_status, uncertainty, standard_reference, calibrated_by, source_pdf, pdf_path, notes
  → ĐÃ CÓ recalibration_date (dùng làm hạn tới), source_pdf, pdf_path.
- maintenance_logs (n=48): id, device_id, maintenance_date, performed_by, maintenance_type, description, source_pdf, pdf_path, next_due_date
- maintenance_schedules (n=0) — BẢNG ĐÃ TỒN TẠI: id, device_id, scheduled_date, due_date, status, notes, created_at
  → KHÔNG tạo mới; chỉ cần thêm cột/phần mềm. Task GĐ1 vì thế là nâng cấp bảng này, không phải CREATE.
- device_transfers (n=3) [= "transfers"]: id, device_id, from_facility_id, to_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, form_code, status
- pre_use_inspections (n=1) [= "pre_use_inspection"]: id, device_id, inspector_name, department, power_ok, physical_ok, gas_pressure_ok, selftest_ok, overall_status, notes, inspection_time
- system_feedback (n=2) [= "feedback"]: id, category, sender_name, sender_dept, priority, content, status, resolution_notes
- device_accessories (n=49): id, parent_device_id, name, model, serial_no, accessory_type, status, notes
- oncall_schedule (n=92): id, year, month, day_num, day_name, date_str, primary_engineer, primary_phone, backup_engineer, backup_phone, leader_oncall, time_window, status, notes
- bme_staff (n=6): id, staff_code, full_name, title, role_level, department_unit, specialty, phone, email, assigned_departments, certificates, status, oncall_status, avatar_color
- api_keys_config (n=5): id, service_name, api_key, status, created_at
- hospital_directory (n=7)

## KẾT LUẬN ĐIỀU CHỈNH
1. maintenance_schedules: đã có 7 cột — task GĐ1 = ALTER thêm (maintenance_type, frequency_days, last_completed_at, next_due_at, assigned_staff_id) + engine generate + CRUD.
2. Certificates: dùng calibration_certificates.recalibration_date làm hạn cảnh báo (not cần tạo bảng certs).
3. devices đã có source_pdf/pdf_path/md_path — schema documents/OCR chỉ cần bảng references mới nếu cần liên kết nhiều file/entity, không đổi devices.
4. pre_use_inspections đã có 4 trường check riêng — mở rộng checklist động nếu cần.

## QUYẾT ĐỊNH GĐ1 ĐÃ THỐNG NHẤT (5 AI)
a) Migration nâng cấp maintenance_schedules + notifications (bảng mới) + WAL mode
b) CRUD+generate lịch bảo trì (POST /schedules/generate) — MVP demo ngày 3-6
c) Cảnh báo hết hạn calibration_certificates.recalibration_date 90/60/30 ngày + APScheduler job hằng ngày
d) Dashboard cảnh báo + badge
e) Pre-use inspections + repairs (tách khỏi maintenance_logs) + device_transfers confirm (cập nhật facility cùng transaction)
f) QR code device + demo E2E

Trả lời ngắn "ĐÃ NẮM CONTEXT. Tiếp tục câu hỏi." rồi chờ. Không lặp lại yêu cầu cũ.