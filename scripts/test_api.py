"""
Script kiểm thử toàn bộ API endpoints của Medical Device Management App
Bao gồm cả Gemini AI Agent và Mistral OCR-4 Engine
"""
import sys
import json
import urllib.request

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(path, expected_status=200):
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            content_type = response.headers.get('Content-Type', '')
            print(f"[{status}] {path} ({content_type})")
            assert status == expected_status, f"Expected {expected_status}, got {status}"
            if "application/json" in content_type:
                data = json.loads(response.read().decode('utf-8'))
                if isinstance(data, list):
                    print(f"  Count: {len(data)}, First item: {data[0].get('device_name', data[0].get('name', 'N/A')) if data else 'Empty'}")
                elif isinstance(data, dict):
                    print(f"  Summary: {dict(list(data.items())[:3])}")
    except Exception as e:
        print(f"[FAIL] {path}: {e}")
        sys.exit(1)

def run_tests():
    print("=== RUNNING FULL API TESTS (WITH GEMINI AI & MISTRAL OCR) ===")
    test_endpoint("/")
    test_endpoint("/health")
    test_endpoint("/api/dashboard/summary")
    test_endpoint("/api/dashboard/facilities")
    test_endpoint("/api/dashboard/categories")
    test_endpoint("/api/devices?limit=5")
    test_endpoint("/api/audits")
    test_endpoint("/api/accessories")
    test_endpoint("/api/schedules")
    test_endpoint("/api/work-orders")

    # Test AI Chat
    print("\n--- Testing Gemini AI Agent ---")
    chat_payload = json.dumps({"message": "Quy trình kiểm định máy thở ICU?"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/ai/chat", data=chat_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[{resp.status}] /api/ai/chat")
        print(f"  Engine: {data.get('engine')}, Status: {data.get('status')}")

    # Test Mistral OCR
    print("\n--- Testing Mistral OCR Engine ---")
    ocr_payload = json.dumps({"filename": "GCN_Monitor_2026.pdf"}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/ocr/process", data=ocr_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[{resp.status}] /api/ocr/process")
        print(f"  OCR Engine: {data.get('engine')}, Extracted: {data.get('extracted_fields', {}).get('device_name')}")

    print("\n✨ All API endpoints passed verification successfully!")

if __name__ == "__main__":
    run_tests()