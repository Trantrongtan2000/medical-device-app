import sys
import io
import os
import json
import csv
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

scripts_dir = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\00_HE_THONG_VA_SCRIPTS")

# Check _ocr_device_index.csv
dev_index_csv = scripts_dir / "_ocr_device_index.csv"
if dev_index_csv.exists():
    print(f"=== {dev_index_csv.name} ({dev_index_csv.stat().st_size:,} bytes) ===")
    with open(dev_index_csv, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 10:
                print(f" Row {i}: {row}")
            if i == 10:
                print(" ...")

# Check _ocr_manifest.jsonl
manifest_jsonl = scripts_dir / "_ocr_manifest.jsonl"
if manifest_jsonl.exists():
    print(f"\n=== {manifest_jsonl.name} ({manifest_jsonl.stat().st_size:,} bytes) ===")
    with open(manifest_jsonl, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if i < 5:
                print(f" Line {i}: {line[:150]}")
            if i == 5:
                break
