#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, unicodedata, sys

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'

def norm3(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'[\s_.\-]+', '', s)
    return s

# các token 056-388..392 trong tên md
targets = ['056388', '056389', '056390', '056391', '056392', '056393', '056394', '056387']
found = {}
for dp, dn, fn in os.walk(G_ROOT):
    for f in fn:
        if f.lower().endswith('.pdf'):
            n3 = norm3(f)
            for t in targets:
                if t in n3:
                    found.setdefault(t, []).append(os.path.join(dp, f))

out = []
for t in sorted(found):
    out.append(f'{t}:')
    for p in found[t][:5]:
        out.append(f'    {p}')
sys.stdout.write('\n'.join(out) if out else 'NO MATCHES AT ALL')