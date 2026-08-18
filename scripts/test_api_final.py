#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final API test"""

import urllib.request
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url):
    print(f"\nTesting: {name}")
    print(f"  Endpoint: {url}")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"  Status: {response.status}")
            print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

print("\n" + "="*60)
print("API ENDPOINT TEST")
print("="*60)

results = []

# Test health
results.append(("Health Check", f"{BASE_URL}/health"))

# Test root
results.append(("Root Endpoint", f"{BASE_URL}/"))

# Test dashboard summary
results.append(("Dashboard Summary", f"{BASE_URL}/api/dashboard/summary"))

# Test devices
results.append(("Devices List", f"{BASE_URL}/api/devices"))

# Test facilities
results.append(("Facilities", f"{BASE_URL}/api/dashboard/facilities"))

# Test categories
results.append(("Categories", f"{BASE_URL}/api/dashboard/categories"))

passed = 0
failed = 0
for name, url in results:
    if test_endpoint(name, url):
        passed += 1
    else:
        failed += 1

print("\n" + "="*60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*60)