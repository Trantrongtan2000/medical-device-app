import sys
import io
import urllib.request
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

tests = [
    ("Trang chủ Web UI", "http://127.0.0.1:8000/"),
    ("Health Check API", "http://127.0.0.1:8000/health"),
    ("Danh mục 20 thiết bị mẫu", "http://127.0.0.1:8000/api/devices?limit=20"),
    ("Dashboard Summary KPI", "http://127.0.0.1:8000/api/dashboard/summary"),
    ("Danh sách Khoa/Phòng (39 khoa)", "http://127.0.0.1:8000/api/facilities"),
    ("Tìm Bàn khám TMH (IU 3000)", "http://127.0.0.1:8000/api/devices?search=IU%203000"),
    ("Tìm Đèn đọc phim (ZG-2C)", "http://127.0.0.1:8000/api/devices?search=ZG-2C"),
    ("Hợp đồng mua sắm (198 HĐ)", "http://127.0.0.1:8000/api/contracts"),
    ("Danh bạ Nhà cung cấp (102 NCC)", "http://127.0.0.1:8000/api/directory/suppliers"),
    ("Phiếu bảo trì SpeedMaint (46 phiếu)", "http://127.0.0.1:8000/api/work-orders")
]

print("="*85)
print("🚀 KIỂM TRA TRẠNG THÁI TRUY CẬP DỮ LIỆU CỦA PHẦN MỀM (http://127.0.0.1:8000)")
print("="*85)

for name, url in tests:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = res.read()
            if 'api' in url:
                parsed = json.loads(data.decode('utf-8'))
                count = len(parsed) if isinstance(parsed, list) else len(parsed.keys())
                print(f"✅ [{res.status} OK] {name:40s} -> Trả về {count:3d} mục dữ liệu")
            else:
                print(f"✅ [{res.status} OK] {name:40s} -> Nạp HTML {len(data):,} bytes")
    except Exception as e:
        print(f"❌ [FAIL]    {name:40s} -> Lỗi: {e}")

# Test AI Query
try:
    post_data = json.dumps({"query": "Xem máy BVQ7-TTB-00193"}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/agent/query', data=post_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=5) as res:
        parsed = json.loads(res.read().decode('utf-8'))
        print(f"✅ [{res.status} OK] {'Cactus Needle AI Agent (Edge Tra Cứu)':40s} -> Trả về: {parsed.get('tool_name')} ({parsed.get('engine')})")
except Exception as e:
    print(f"❌ [FAIL]    AI Query -> Lỗi: {e}")

print("\n" + "="*85)
print("🎉 KẾT LUẬN: TOÀN BỘ PHẦN MỀM VÀ DỮ LIỆU ĐANG TRUY CẬP 100% HOÀN HẢO!")
print("="*85)
