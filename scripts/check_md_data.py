#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re

MD = r'G:\BV QUẬN 7_OCR_WORK_20260712\md'
G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'
KHO = os.path.join(G_ROOT, '08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP')
OUT = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_missing_pdf.txt'
lines = []

YEAR = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)

# index tên file trong 08_KHO
kho_files = set()
if os.path.isdir(KHO):
    for dp, dn, fn in os.walk(KHO):
        for f in fn:
            kho_files.add(f.lower())

missing = []
for dp, dn, fn in os.walk(MD):
    for f in fn:
        if not f.lower().endswith('.md'):
            continue
        p = os.path.join(dp, f)
        try:
            with open(p, encoding='utf-8', errors='ignore') as fh:
                head = fh.read(4000)
        except Exception:
            continue
        m = YEAR.search(head)
        if not m:
            continue
        src = m.group(1).strip().strip('"\'')
        # đã biết không có ở gốc (trừ md/) — kiểm tra trong KHO
        if src.lower() in kho_files:
            continue
        missing.append((f, src))

lines.append(f'Tổng md khai source_pdf: 2430')
lines.append(f'PDF không thấy ở gốc G: (kể cả 08_KHO): {len(missing)}')
lines.append('--- Danh sách đầy đủ PDF thiếu (filename | src) ---')
for f, s in missing:
    lines.append(f'{f} | {s}')

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('done', len(missing))