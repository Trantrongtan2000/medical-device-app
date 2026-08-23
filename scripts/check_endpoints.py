import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base = 'http://127.0.0.1:8000'

endpoints = [
    ('/', 'Root Web App (HTML)'),
    ('/api/devices?limit=5', 'Danh Sách Thiết Bị Y Tế'),
    ('/api/staff', 'Nhân Sự BME Q7 (6 Kỹ Sư)'),
    ('/api/oncall/today', 'Lịch On-Call Hôm Nay 24h'),
    ('/api/oncall/schedule?month=8&year=2026', 'Kế Hoạch On-Call Tháng 8/2026'),
    ('/api/directory/leaders', 'Lãnh Đạo & Trưởng Khoa'),
    ('/api/directory/suppliers', 'Đối Tác & Kỹ Sư Hãng NCC'),
    ('/api/semantica/stats', 'Đồ Thị Tri Thức Semantica')
]

print('=' * 65)
print('  KIỂM TRA TRẠNG THÁI SERVER & ENDPOINTS SAU KHI PULL MỚI NHẤT')
print('=' * 65)

for path, label in endpoints:
    try:
        req = urllib.request.Request(base + path, headers={'User-Agent': 'HealthCheck/1.0'})
        with urllib.request.urlopen(req, timeout=3) as res:
            code = res.getcode()
            print(f'✅ {label:<35} : HTTP {code} OK')
    except Exception as e:
        print(f'❌ {label:<35} : LỖI ({e})')

print('=' * 65)
