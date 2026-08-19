#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, unicodedata, sys

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'

def keep_sep(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower()

patterns = {
    'kaipu': 'kaipu',
    'vio300s': 'vio300s',
    'vio300d': 'vio300d',
    'pharung': 'pharungtim|pha rung|defibril',
    'huyetap': 'huyetapke|huyet ap',
    'nhietam': 'nhietamke|nhiet am',
    'a07coat': 'a07coat',
}
hits = {}
for dp, dn, fn in os.walk(G_ROOT):
    for f in fn:
        if f.lower().endswith('.pdf'):
            lf = keep_sep(f)
            for label, pat in patterns.items():
                if re.search(pat, lf):
                    hits.setdefault(label, []).append(os.path.join(dp, f))

out = []
for label, pat in patterns.items():
    lst = hits.get(label, [])
    out.append(f'{label}: {len(lst)}')
    for p in lst[:10]:
        out.append(f'    {p}')
sys.stdout.write('\n'.join(out))