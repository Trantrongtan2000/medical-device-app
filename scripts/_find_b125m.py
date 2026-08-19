#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, unicodedata, sys

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'

def keep_sep(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower()

# tìm mọi pdf chứa SR724460006SA hoặc B125M
pats = ['sr724460006sa', 'b125m']
for pat in pats:
    hits = []
    for dp, dn, fn in os.walk(G_ROOT):
        for f in fn:
            if f.lower().endswith('.pdf') and pat in keep_sep(f):
                hits.append(os.path.join(dp, f))
    sys.stdout.write(f'{pat}: {len(hits)}\n')
    for h in hits[:5]:
        sys.stdout.write(f'    {h}\n')