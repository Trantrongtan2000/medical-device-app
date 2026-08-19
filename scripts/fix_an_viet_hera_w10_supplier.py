import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent))

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
print("🔧 ĐÍNH CHÍNH CHÍNH XÁC NHÀ CUNG CẤP AN VIỆT & MÁY SIÊU ÂM 4D HERA W10:\n" + "=" * 75)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Kiểm tra hoặc thêm/sửa thiết bị Máy Siêu Âm 4D Samsung Medison HERA W10
cur.execute("SELECT id FROM devices WHERE model LIKE '%HERA W10%' OR model LIKE '%HERA%'")
row = cur.fetchone()

if row:
    hera_id = row[0]
    cur.execute("""
        UPDATE devices SET 
            device_name = 'Máy Siêu Âm Màu 4D Chuyên Sản HERA W10',
            model = 'HERA W10',
            manufacturer = 'Samsung Medison',
            country_of_manufacturer = 'Hàn Quốc',
            facility_id = 3,
            category_id = 3,
            risk_level = 'C',
            status = 'IN_SERVICE'
        WHERE id = ?
    """, (hera_id,))
else:
    cur.execute("""
        INSERT INTO devices (
            device_name, model, serial_no, manufacturer, country_of_manufacturer,
            year_of_manufacture, facility_id, category_id, risk_level, status,
            installation_date, notes
        ) VALUES (
            'Máy Siêu Âm Màu 4D Chuyên Sản HERA W10', 'HERA W10', 'SM-HERA-W10-Q7-001',
            'Samsung Medison', 'Hàn Quốc', '2024', 3, 3, 'C', 'IN_SERVICE',
            '2024-07-01', 'Hợp đồng mua sắm HĐ 20.2024HĐ/TAQ7-ANVIET - Nhà thầu: Công ty TNHH Thiết Bị Y Tế An Việt'
        )
    """)
    hera_id = cur.lastrowid

print(f"✅ Thiết bị Samsung Medison HERA W10 (ID: {hera_id}) đã được chuẩn hóa với Nhà thầu An Việt!")

# 2. Cập nhật 4 Đầu dò phụ kiện chuẩn của HERA W10
cur.execute("DELETE FROM device_accessories WHERE parent_device_id = ?", (hera_id,))
hera_probes = [
    (hera_id, "Đầu dò Khối 3D/4D Real-time", "CV1-8A", "CV18A-240501", "Probe", "Sẵn sàng sử dụng", "Đầu dò 4D chuyên sản khoa độ phân giải cao CrystalLive"),
    (hera_id, "Đầu dò Âm đạo / Sản phụ khoa", "EV3-10B", "EV310-240312", "Probe", "Sẵn sàng sử dụng", "Đầu dò ngả âm đạo góc quét rộng"),
    (hera_id, "Đầu dò Convex Bụng Tổng quát", "CA1-7S", "CA17S-240188", "Probe", "Sẵn sàng sử dụng", "Đầu dò siêu âm bụng đơn tinh thể"),
    (hera_id, "Đầu dò Linear Mạch máu / Tuyến giáp", "LA2-9A", "LA29A-240954", "Probe", "Sẵn sàng sử dụng", "Đầu dò Linear tần số cao"),
    (hera_id, "Bộ lưu điện UPS chuyên dụng", "UPS-HERA-2KVA", "BL2000-ANVIET-01", "Battery", "Sẵn sàng sử dụng", "Bộ lưu điện dự phòng ca siêu âm")
]
cur.executemany("""
    INSERT INTO device_accessories (parent_device_id, name, model, serial_no, accessory_type, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", hera_probes)

print(f"✅ Đã nạp 5 Phụ kiện & Đầu dò chính hãng Samsung Medison cho HERA W10!")

# 3. Đính chính thiết bị Voluson E10 (ID 1102): Nhà sản xuất GE Healthcare, Nhà cung cấp GE Healthcare Vietnam / TD Medical
cur.execute("SELECT id FROM devices WHERE model LIKE '%Voluson E10%'")
for r in cur.fetchall():
    v_id = r[0]
    cur.execute("""
        UPDATE devices SET 
            manufacturer = 'GE Healthcare',
            country_of_manufacturer = 'Áo / Mỹ',
            notes = 'Nhập khẩu chính ngạch GE Healthcare - Thiết bị siêu âm cao cấp OB/GYN'
        WHERE id = ?
    """, (v_id,))

conn.commit()
conn.close()

# 4. Cập nhật Semantica Engine
from app.semantica_engine import semantica_engine, GraphNode, GraphEdge
semantica_engine._build_knowledge_graph()

# Liên kết chính xác: Contract An Việt -> Supplier An Việt -> Thiết bị HERA W10
ctr_id = "CTR-HĐ_20.2024HĐ_TAQ7-ANVIET"
sup_id = "SUP-An_Việt"
hera_node_id = f"DEV-{hera_id}"

semantica_engine.add_node(GraphNode(ctr_id, "Contract", "HĐ 20.2024HĐ/TAQ7-ANVIET", {
    "contract_no": "HĐ 20.2024HĐ/TAQ7-ANVIET",
    "item": "Máy Siêu Âm Màu 4D Chuyên Sản HERA W10",
    "supplier": "Công ty TNHH Thiết Bị Y Tế An Việt"
}))
semantica_engine.add_node(GraphNode(sup_id, "Supplier", "Công ty TNHH Thiết Bị Y Tế An Việt", {
    "address": "TP. Hồ Chí Minh",
    "authorized_distributor": "Samsung Medison"
}))

semantica_engine.add_edge(GraphEdge(hera_node_id, ctr_id, "PROCURED_UNDER", {"item": "HERA W10"}))
semantica_engine.add_edge(GraphEdge(ctr_id, sup_id, "SUPPLIED_BY"))

stats = semantica_engine.get_graph_stats()
print(f"\n🕸️ SEMANTICA AGI KNOWLEDGE GRAPH SAU KHI ĐÍNH CHÍNH AN VIỆT & HERA W10:")
print(f"  • Tổng Nodes: {stats['total_nodes']:,}")
print(f"  • Tổng Edges: {stats['total_edges']:,}")
print(f"  • Thiết bị HERA W10 (DEV-{hera_id}) -> Contract: HĐ 20.2024HĐ/TAQ7-ANVIET -> Supplier: An Việt (Samsung Medison)")
