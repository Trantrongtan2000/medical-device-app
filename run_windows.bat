@echo off
chcp 65001 > nul
title MEDICAL DEVICE MANAGEMENT SYSTEM - BV QUAN 7 (HTM v3)

echo ==============================================================================
echo  🏥 BỆNH VIỆN ĐA KHOA QUẬN 7 — HỆ THỐNG QUẢN TRỊ TRANG THIẾT BỊ Y TẾ (HTM v3)
echo ==============================================================================
echo.

cd /d "%~dp0"

REM Kiểm tra Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Không tìm thấy Python trên hệ thống! Vui lòng cài đặt Python 3.10+
    pause
    exit /b 1
)

REM Thiết lập biến môi trường mặc định nếu chưa có
if "%MEDICAL_DEVICE_DOCUMENTS_ROOT%"=="" (
    set "MEDICAL_DEVICE_DOCUMENTS_ROOT=G:\BV QUẬN 7_OCR_WORK_20260712"
)
if "%PORT%"=="" (
    set "PORT=8000"
)

echo [INFO] Kho tài liệu: %MEDICAL_DEVICE_DOCUMENTS_ROOT%
echo [INFO] Cổng mạng: %PORT%
echo [INFO] Khởi động máy chủ ứng dụng...
echo.

python start_server.py

pause
