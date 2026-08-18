import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

dev_data = {
    'device_name': 'Máy Siêu Âm Màu Doppler 4D',
    'model': 'Voluson E10',
    'serial_no': 'GE-VOLUSON-2026-FINAL',
    'facility_id': 4,
    'category_id': 1,
    'manufacturer': 'GE Healthcare',
    'country_of_manufacturer': 'Mỹ',
    'year_of_manufacture': 2026,
    'risk_level': 'C',
    'status': 'IN_SERVICE',
    'certification_no': 'GCN-GE-2026-001',
    'calibration_date': '2026-08-18',
    'recalibration_date': '2027-08-18',
    'notes': 'Nhập mới theo Hợp đồng Mua sắm TTB 2026'
}

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/devices',
    data=json.dumps(dev_data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print("✅ Create Device Response:", res)
    
    device_id = res['device_id']
    detail_res = json.loads(urllib.request.urlopen(f'http://127.0.0.1:8000/api/devices/{device_id}').read().decode('utf-8'))
    print("✅ Verified Device in DB:")
    print(f"  - Tên máy: {detail_res['device_name']}")
    print(f"  - Snipe-IT Tag: {detail_res['asset_tag']}")
    print(f"  - SpeedMaint Code: {detail_res['speedmaint_code']}")
    print(f"  - Khoa tiếp nhận: {detail_res['facility']}")
    print(f"  - Mức rủi ro: Mức {detail_res['risk_level']}")
    print(f"  - Số chứng chỉ KĐ: {len(detail_res['certificates'])}")
    print(f"  - Nhật ký Audit Trail: {len(detail_res['maintenance_logs'])}")
except Exception as e:
    print("❌ Error:", e)
