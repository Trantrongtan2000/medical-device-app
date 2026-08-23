#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify tổng thể sau khi sửa liên kết: đếm md có source_pdf resolve được."""
import os, re, unicodedata, collections, sys

MD = r'G:\BV QUẬN 7_OCR_WORK_20260712\md'
G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'
OUT = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_verify_total.txt'
lines = []

def norm2(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower().replace('_1', '').strip()

YEAR = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)

# index pdf tên (norm2) trên G_ROOT (kể cả kho) — chỉ lưu tên
pdf_names = set()
for dp, dn, fn in os.walk(G_ROOT):
    for f in fn:
        if f.lower().endswith('.pdf'):
            pdf_names.add(norm2(f))
        if len(pdf_names) > 40000:
            break
    if len(pdf_names) > 40000:
        break

have_src = 0
resolved = 0
broken = []
total_md = 0
for base in [MD, os.path.join(G_ROOT, '04_KIEM_DINH_VA_HIEU_CHUAN')]:
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if not f.lower().endswith('.md'):
                continue
            total_md += 1
            p = os.path.join(dp, f)
            try:
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    head = fh.read(3000)
            except Exception:
                continue
            m = YEAR.search(head)
            if not m:
                continue
            have_src += 1
            src = m.group(1).strip().strip('"\'')
            if norm2(os.path.basename(src)) in pdf_names:
                resolved += 1
            else:
                broken.append((p, src))

lines.append(f'Tổng md: {total_md}')
lines.append(f'Có source_pdf: {have_src}')
lines.append(f'Resolve được (tên khớp PDF trên G:): {resolved}')
lines.append(f'Vẫn CHƯA resolve được: {len(broken)}')
lines.append('')
lines.append('--- Danh sách còn lỗi (toàn bộ) ---')
for p, s in broken:
    lines.append(f'{p}  |  src={s}')

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
sys.stdout.write(f'total={total_md} have_src={have_src} resolved={resolved} broken={len(broken)}')