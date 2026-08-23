import sys
import io
import sqlite3

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

conn = sqlite3.connect('database/devices.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT id, device_name, model, manufacturer, country_of_manufacturer
    FROM devices
    ORDER BY id ASC
""").fetchall()

print(f"=== RÀ SOÁT DANH PHÁP 1.211 THIẾT BỊ TÌM TÊN LỖI/CHUNG CHUNG ===")
anomalies = []
for r in rows:
    name = r["device_name"] or ""
    model = r["model"] or ""
    mfg = r["manufacturer"] or ""
    
    reasons = []
    if "chuyên dùng" in name.lower():
        reasons.append("Tên chung chung ('chuyên dùng')")
    if name.lower() in ["thiết bị", "máy", "dụng cụ", "bàn", "ghế"]:
        reasons.append("Tên quá ngắn/không rõ chủng loại")
    if any(typo in name.lower() for typo in ["abn", "banf", "bafn", "ghex", "mayy"]):
        reasons.append("Lỗi gõ Telex")
    if mfg in ["Chính hãng", "0", "None", ""] and model not in ["-", "", "None"]:
        reasons.append("Hãng chưa định danh cụ thể ('Chính hãng')")

    if reasons:
        anomalies.append((r, reasons))

print(f"Phát hiện {len(anomalies)} thiết bị cần chuẩn hóa danh pháp:")
for r, reasons in anomalies:
    print(f" • [ID {r['id']:4d}] {r['device_name']:35s} | Model: {r['model']:15s} | Hãng: {r['manufacturer']:20s} | Lý do: {', '.join(reasons)}")
