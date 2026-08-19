#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, unicodedata, sys
from difflib import SequenceMatcher

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'

def norm3(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'[\s_.\-]+', '', s)
    return s

src = '056-995_01.26P-ÁP KẾ LÒ XO-Nơi sản xuất_ Kaipu-unknown-date.pdf'
n3 = norm3(src)
sys.stdout.write(f'src n3 = {n3}\n')
for dp, dn, fn in os.walk(G_ROOT):
    for f in fn:
        if f.lower().endswith('.pdf') and '056-995' in f:
            r = SequenceMatcher(None, n3, norm3(f)).ratio()
            sys.stdout.write(f'r={r:.3f}  {os.path.join(dp, f)}\n')