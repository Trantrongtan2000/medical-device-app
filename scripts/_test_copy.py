#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, shutil
src = r'G:\BV QUẬN 7_OCR_WORK_20260712\md\05_KIEM DINH\backup_original\056-382_01.26-NHIỆT ẨM KẾ ĐIỆN TỬ-MH16-CĐHA2-23-01-2026.md'
dst = r'G:\BV QUẬN 7_OCR_WORK_20260712\08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP\_backup_md_links\test.md'
os.makedirs(os.path.dirname(dst), exist_ok=True)
print('src exists:', os.path.exists(src))
print('len src path:', len(src))
shutil.copy2(src, dst)
print('copied OK, len dst:', len(dst))