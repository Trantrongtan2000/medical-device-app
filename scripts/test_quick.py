#!/usr/bin/env python3
import urllib.request
import json

try:
    with urllib.request.urlopen("http://localhost:8001/health", timeout=5) as response:
        print("Server Status:", response.status)
        print(json.loads(response.read()))
except Exception as e:
    print("Error:", e)