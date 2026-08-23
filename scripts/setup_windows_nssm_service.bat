@echo off
chcp 65001 > nul
title CÀI ĐẶT WINDOWS SERVICE TỰ ĐỘNG - HTM v3

echo ==============================================================================
echo  🛠️ THIẾT LẬP DỊCH VỤ WINDOWS SERVICE (NSSM) — PHÒNG TTBYT BV QUẬN 7
echo ==============================================================================
echo.

set SERVICE_NAME=MedicalDeviceHTM3
set APP_DIR=%~dp0..

where nssm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Không tìm thấy công cụ nssm.exe trong PATH!
    echo Vui lòng tải NSSM từ https://nssm.cc/download và đặt vào C:\Windows\System32
    pause
    exit /b 1
)

echo [1/3] Đang đăng ký dịch vụ %SERVICE_NAME%...
nssm stop %SERVICE_NAME% >nul 2>&1
nssm remove %SERVICE_NAME% confirm >nul 2>&1

nssm install %SERVICE_NAME% "python.exe" "start_server.py"
nssm set %SERVICE_NAME% AppDirectory "%APP_DIR%"
nssm set %SERVICE_NAME% Description "Hệ thống Quản lý Trang thiết bị y tế Bệnh viện Quận 7 (HTM v3)"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppStdout "%APP_DIR%\logs\service_out.log"
nssm set %SERVICE_NAME% AppStderr "%APP_DIR%\logs\service_err.log"

echo [2/3] Cấu hình môi trường dịch vụ...
nssm set %SERVICE_NAME% AppEnvironmentExtra MEDICAL_DEVICE_DOCUMENTS_ROOT=G:\BV QUẬN 7_OCR_WORK_20260712 PORT=8000

echo [3/3] Khởi động dịch vụ...
nssm start %SERVICE_NAME%

echo.
echo ✅ Cài đặt dịch vụ thành công! Hệ thống sẽ tự động khởi chạy cùng Windows.
pause
