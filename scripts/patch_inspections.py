#!/usr/bin/env python3
# Patch để thêm POST /api/inspections — chạy nhanh append
from pathlib import Path
f = Path(r'C:\Users\tantt\Downloads\medical-device-app\app\routes_inspections.py')
content = f.read_text()
add_code = '''

@router.post("/api/inspections")
async def record_pre_use_inspection(body: Request, db = Depends(get_db)):
    """Fallback API cho form submit pre-use inspection — nhận raw JSON body"""
    from datetime import datetime
    from fastapi import Request
    try:
        data = await body.json()
    except:
        raise HTTPException(400, "Invalid JSON")
    
    device_id = data.get("device_id")
    if not device_id:
        raise HTTPException(422, "device_id required")
    
    overall = calc_overall(
        data.get("power_ok", True),
        data.get("physical_ok", True),
        data.get("gas_pressure_ok", True),
        data.get("selftest_ok", True)
    )
    
    cur = db.execute("""INSERT INTO pre_use_inspections
        (device_id, inspector_name, department, power_ok, physical_ok, gas_pressure_ok, selftest_ok, overall_status, notes, inspection_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (device_id, data.get("inspector_name", ""), data.get("department", ""),
         data.get("power_ok", True), data.get("physical_ok", True),
         data.get("gas_pressure_ok", True), data.get("selftest_ok", True),
         overall, data.get("notes", ""), datetime.now().isoformat()))
    db.commit()
    return {"id": cur.lastrowid, "overall_status": overall}
'''
# Thêm import Request nếu chưa có
if 'from fastapi import' in content and 'Request' not in content.split('from fastapi import')[1].split('\n')[0]:
    content = content.replace('from fastapi import BaseModel', 'from fastapi import BaseModel, Request')
# Thêm đoạn code vào cuối file
f.write_text(content + add_code)
print("Patched routes_inspections.py")