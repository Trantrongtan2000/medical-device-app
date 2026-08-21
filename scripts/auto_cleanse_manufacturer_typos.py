"""
Auto Cleanse Manufacturer & Model Typos based on Web Cross-Reference
"""
import sys
import io
import sqlite3

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

conn = sqlite3.connect('database/devices.db')
cur = conn.cursor()

corrections = [
    # (Condition model/id, correct manufacturer, note)
    ("UPDATE devices SET manufacturer = 'Aolike' WHERE model LIKE '%ALK06%' AND manufacturer = 'Aloka'", "Sửa hãng ALK06-H800 từ Aloka -> Aolike"),
    ("UPDATE devices SET manufacturer = 'Carestream Health' WHERE manufacturer LIKE '%CARETREAMS%' OR manufacturer LIKE '%Carestream%'", "Chuẩn hóa hãng Carestream Health"),
    ("UPDATE devices SET manufacturer = 'Karl Storz' WHERE manufacturer LIKE '%Karl Stoz%'", "Sửa chính tả Karl Storz"),
    ("UPDATE devices SET manufacturer = 'Huntleigh' WHERE model LIKE '%Team3A%' AND (manufacturer IS NULL OR manufacturer = '')", "Gán hãng Huntleigh cho Monitor sản khoa Team3A-B"),
    ("UPDATE devices SET manufacturer = 'Zerone' WHERE model LIKE '%Zeus%' AND (manufacturer IS NULL OR manufacturer = '')", "Gán hãng Zerone cho Dao mổ điện Zeus-150")
]

print("=== BẮT ĐẦU CHUẨN HÓA DỮ LIỆU SAU ĐỐI CHỨNG ONLINE ===")
for sql, desc in corrections:
    cur.execute(sql)
    print(f"✓ {desc} (Số dòng ảnh hưởng: {cur.rowcount})")

conn.commit()
conn.close()
print("🎉 Hoàn tất chuẩn hóa dữ liệu!")
