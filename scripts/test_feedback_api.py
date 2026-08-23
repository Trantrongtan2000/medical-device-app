import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

payload = {
    'category': 'Đính chính dữ liệu thiết bị',
    'sender_name': 'KS. Trần Trọng Tấn',
    'sender_dept': 'Phòng TTBYT Quận 7',
    'priority': 'NORMAL',
    'content': 'Hệ thống đã chuẩn hóa 02 máy đo loãng xương DEXA và phân bổ chính xác 24 hợp đồng!'
}

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/feedback',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as res:
    print("Submit Status:", res.status)
    print("Response:", res.read().decode('utf-8'))

with urllib.request.urlopen('http://127.0.0.1:8000/api/feedback') as res:
    items = json.loads(res.read().decode('utf-8'))
    print(f"Total Feedback Items in DB: {len(items)}")
    for it in items:
        print(f"  • [{it['category']}] {it['sender_name']} ({it['priority']}): {it['content']}")
