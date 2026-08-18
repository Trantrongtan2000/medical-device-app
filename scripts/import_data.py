#!/usr/bin/env python3
"""Import du lieu tu file MD"""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))

from import_md_data import MedicalDeviceImporter

importer = MedicalDeviceImporter(
    db_path="C:/Users/tantt/Downloads/medical-device-app/database/devices.db",
    data_source="G:/BV QUAN 7_OCR_WORK_20260712/md"
)
importer.run()