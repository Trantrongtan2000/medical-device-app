import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("1. Testing PUT /api/devices/1104 (Edit Device) ...")
update_payload = {
    "device_name": "Máy Siêu Âm Màu Doppler 4D (Đã Hiệu Chỉnh Kỹ Thuật)",
    "manufacturer": "GE Healthcare USA",
    "risk_level": "C",
    "status": "IN_SERVICE",
    "notes": "Đã nghiệm thu và cập nhật cấu hình đầu dò tim/mạch"
}

req_dev = urllib.request.Request(
    'http://127.0.0.1:8000/api/devices/1104',
    data=json.dumps(update_payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)

res_dev = json.loads(urllib.request.urlopen(req_dev).read().decode('utf-8'))
print("✅ Update Device Response:", res_dev)

dev_detail = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/devices/1104').read().decode('utf-8'))
print(f"   Verified New Name: {dev_detail['device_name']}")
print(f"   Verified New Notes: {dev_detail['notes']}")

print("\n2. Testing PUT /api/work-orders/1 (Edit Work Order) ...")
wo_update_payload = {
    "work_type": "Sửa chữa",
    "assigned_to": "KS. Trương Hoài Thương - Tổ Kỹ Thuật Y Sinh",
    "description": "Đã thay thế van áp lực và kiểm tra an toàn điện đạt chuẩn QT.06",
    "materials": "Van áp lực 2.5 bar, Gioăng cao su y tế"
}

req_wo = urllib.request.Request(
    'http://127.0.0.1:8000/api/work-orders/1',
    data=json.dumps(wo_update_payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)

res_wo = json.loads(urllib.request.urlopen(req_wo).read().decode('utf-8'))
print("✅ Update Work Order Response:", res_wo)

orders = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/work-orders').read().decode('utf-8'))
edited_wo = next((o for o in orders if o['id'] == 1), None)
if edited_wo:
    print(f"   Verified WO #{edited_wo['id']:03d}: {edited_wo['work_type']} - {edited_wo['description']}")
