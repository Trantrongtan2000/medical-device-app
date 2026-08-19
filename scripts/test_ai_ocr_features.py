import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base = 'http://127.0.0.1:8000'

print("=" * 70)
print("  KIỂM TRA CÁC TÍNH NĂNG AI GEMINI & MISTRAL OCR ENGINE")
print("=" * 70)

# 1. Test Gemini AI Chat
try:
    chat_payload = json.dumps({"message": "Quy trình bảo dưỡng máy thở Vela Khoa Cấp Cứu theo QT.06"}).encode('utf-8')
    req = urllib.request.Request(f"{base}/api/ai/chat", data=chat_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        print(f"✅ Gemini AI Chat API: {data['status'].upper()} (Engine: {data.get('engine', 'N/A')})")
        print(f"   Trích dẫn phản hồi: {data['reply'][:120]}...\n")
except Exception as e:
    print(f"❌ Lỗi Gemini AI Chat: {e}\n")

# 2. Test Mistral OCR Process
try:
    ocr_payload = json.dumps({"filename": "GCN_KiemDinh_MaySocTim.pdf"}).encode('utf-8')
    req = urllib.request.Request(f"{base}/api/ocr/process", data=ocr_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        print(f"✅ Mistral OCR Engine API: {data['status'].upper()} (Engine: {data.get('engine', 'N/A')})")
        print(f"   Thiết bị bóc tách: {data.get('extracted_fields', {}).get('device_name')} (Model: {data.get('extracted_fields', {}).get('model')}, S/N: {data.get('extracted_fields', {}).get('serial_no')})\n")
except Exception as e:
    print(f"❌ Lỗi Mistral OCR: {e}\n")

# 3. Test API Keys Config
try:
    req = urllib.request.Request(f"{base}/api/keys/config")
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        print(f"✅ API Keys Pool Config: Gemini Keys={data.get('gemini', {}).get('total_keys', 0)}, Mistral Keys={data.get('mistral', {}).get('total_keys', 0)}")
except Exception as e:
    print(f"❌ Lỗi API Keys Config: {e}")

print("=" * 70)
