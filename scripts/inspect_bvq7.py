# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'C:\Users\tantt\Downloads\asset-management-tools\36. TRANG THIẾT BỊ Y TẾ\real_devices_bvq7.json'
with open(p, encoding='utf-8') as f:
    data = json.load(f)
print('type:', type(data).__name__)
if isinstance(data, list):
    print('count:', len(data))
    if data:
        print('keys:', list(data[0].keys())[:30])
        print('sample:', json.dumps(data[0], ensure_ascii=False)[:800])
elif isinstance(data, dict):
    print('top keys:', list(data.keys())[:30])