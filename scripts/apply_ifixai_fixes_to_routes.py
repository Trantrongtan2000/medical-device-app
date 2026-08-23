import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
routes_path = app_dir / "app" / "routes.py"

with open(routes_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Enhance oncall_schedule to accept flexible month formats (int, '8', '2026-08', '08')
old_oncall_route = """@router.get("/api/oncall/schedule")
async def get_oncall_schedule(
    month: Optional[int] = Query(8, description="Tháng cần xem lịch"),
    year: Optional[int] = Query(2026, description="Năm cần xem lịch"),
    db = Depends(get_db)
):"""

new_oncall_route = """@router.get("/api/oncall/schedule")
async def get_oncall_schedule(
    month: Optional[Any] = Query(8, description="Tháng cần xem lịch (int hoặc YYYY-MM)"),
    year: Optional[int] = Query(2026, description="Năm cần xem lịch"),
    db = Depends(get_db)
):
    # Parse flexible month strings like '2026-08' or '08'
    parsed_month = 8
    parsed_year = year or 2026
    if month is not None:
        m_str = str(month).strip()
        if "-" in m_str:
            parts = m_str.split("-")
            try:
                parsed_year = int(parts[0])
                parsed_month = int(parts[1])
            except ValueError:
                parsed_month = 8
        else:
            try:
                parsed_month = int(m_str)
            except ValueError:
                parsed_month = 8"""

if old_oncall_route in code:
    code = code.replace(old_oncall_route, new_oncall_route)
    code = code.replace("rows = db.execute(query, (month, year)).fetchall()", "rows = db.execute(query, (parsed_month, parsed_year)).fetchall()")
    print("✅ Đã nâng cấp linh hoạt parse tháng cho `/api/oncall/schedule`!")

# 2. Add route aliases
aliases_block = """
# ==================== iFixAi ROBUST ALIAS ROUTES ====================
@router.get("/api/speedmaint/work-orders")
async def alias_speedmaint_work_orders(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db = Depends(get_db)
):
    return await get_work_orders(status=status, priority=priority, limit=limit, offset=offset, db=db)

@router.get("/api/inspections/daily")
async def alias_daily_inspections(db = Depends(get_db)):
    return await list_inspections(db=db)

@router.get("/api/calibrations")
async def alias_calibrations(db = Depends(get_db)):
    return await get_maintenance_schedules(db=db)

@router.get("/api/maintenance/logs")
async def alias_maintenance_logs(db = Depends(get_db)):
    return await get_maintenance_schedules(db=db)

@router.get("/api/semantica/graph")
async def alias_semantica_graph(db = Depends(get_db)):
    return await get_semantica_stats(db=db)
"""

if "alias_speedmaint_work_orders" not in code:
    code += "\n" + aliases_block
    print("✅ Đã bổ sung bộ định tuyến dự phòng Alias Routes cho iFixAi!")

with open(routes_path, "w", encoding="utf-8") as f:
    f.write(code)
