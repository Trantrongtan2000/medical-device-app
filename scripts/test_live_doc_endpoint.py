import sys
import io
import urllib.request
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

url = 'http://127.0.0.1:8000/api/devices/1/documents'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as res:
    data = json.loads(res.read().decode('utf-8'))
    print("Device:", data["device"]["device_name"], "| S/N:", data["device"]["serial_no"])
    print("Total documents attached:", data["total_documents"])
    for d in data["documents"][:5]:
        print(f" - [{d['doc_badge_label']}] {d['title']} ({d['file_size_str']}) -> Stream: {d['stream_url']}")
