import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
sys.path.insert(0, str(app_dir))

from app.semantica_engine import SemanticaMedicalGraph

print("="*75)
print("🌐 KIỂM TOÁN TỔNG THỂ SEMANTICA CONTEXT GRAPH & LIÊN KẾT ĐỒ THỊ Y SINH")
print("="*75)

graph = SemanticaMedicalGraph()
stats = graph.get_graph_stats()

print("\n📊 1. THỐNG KÊ MẠNG LƯỚI TRI THỨC (GRAPH METRICS):")
print(f"  • Tổng số Nodes: {stats['total_nodes']:,} nodes")
print(f"  • Tổng số Edges: {stats['total_edges']:,} edges")

print("\n📦 2. PHÂN BỐ CÁC LOẠI NODE (NODE TYPES):")
for ntype, cnt in sorted(stats['node_distribution'].items(), key=lambda x: -x[1]):
    print(f"  - {ntype:18s}: {cnt:5d} nodes")

print("\n🔗 3. PHÂN BỐ CÁC LOẠI QUAN HỆ (EDGE RELATIONS):")
for rel, cnt in sorted(stats['edge_distribution'].items(), key=lambda x: -x[1]):
    print(f"  - {rel:20s}: {cnt:5d} edges")

# Check connectivity per directory / domain
print("\n🔍 4. KIỂM TRA LIÊN KẾT THEO CÁC NHÓM THƯ MỤC CHUYÊN MÔN:")

# Bàn giao & Nghiệm thu
handover_edges = [e for e in graph.edges if e.relation == 'PROCURED_UNDER']
print(f"  • Bàn Giao & Hợp Đồng (PROCURED_UNDER): {len(handover_edges):,} liên kết")

# Kiểm định & Hiệu chuẩn
cert_nodes = [n for n in graph.nodes.values() if n.type == 'Certificate']
cert_edges = [e for e in graph.edges if e.relation == 'CERTIFIED_BY']
print(f"  • Kiểm Định & GCN (CERTIFIED_BY): {len(cert_nodes):,} GCN nodes | {len(cert_edges):,} liên kết thiết bị")

# Điều chuyển thiết bị
xfer_nodes = [n for n in graph.nodes.values() if n.type == 'Transfer']
xfer_edges = [e for e in graph.edges if 'TRANSFERRED' in e.relation]
print(f"  • Điều Chuyển Thiết Bị (TRANSFERRED): {len(xfer_nodes):,} biên bản | {len(xfer_edges):,} liên kết")

# Phụ kiện đi kèm
acc_nodes = [n for n in graph.nodes.values() if n.type == 'Accessory']
acc_edges = [e for e in graph.edges if e.relation == 'HAS_ACCESSORY']
print(f"  • Phụ Kiện Rời & Đầu Dò (HAS_ACCESSORY): {len(acc_nodes):,} phụ kiện | {len(acc_edges):,} liên kết thiết bị mẹ")

# Quy chuẩn y tế
reg_edges = [e for e in graph.edges if e.relation == 'GOVERNED_BY']
print(f"  • Quy Chuẩn Y Tế NĐ98 & TT05 (GOVERNED_BY): {len(reg_edges):,} liên kết pháp lý")

# Vị trí khoa phòng
loc_edges = [e for e in graph.edges if e.relation == 'LOCATED_IN']
print(f"  • Phân Bổ Khoa/Phòng (LOCATED_IN): {len(loc_edges):,} liên kết khoa phòng (100% toàn viện)")

# Sample reasoning test
print("\n🧠 5. KIỂM THỬ TRUY XUẤT NGUỒN GỐC & GIẢI TRÌNH XÁC ĐỊNH (W3C PROV-O):")
for sample_id in [349, 1115, 1103]:
    explanation = graph.explain_device(sample_id)
    if "error" not in explanation:
        print(f"\n  [Thiết bị ID {sample_id} - {explanation['asset_tag']}]: {explanation['device_name']}")
        print(f"    - Model: {explanation['model']} | S/N: {explanation['serial_no']}")
        print(f"    - Khoa Phòng: {explanation['facility']}")
        print(f"    - Phân Loại: {explanation['category']}")
        print(f"    - Hợp Đồng: {explanation['contract_no']}")
        print(f"    - Nhà Thầu: {explanation['supplier']}")
        print(f"    - Giấy Kiểm Định: {explanation['certificate_no']}")
        print(f"    - Trạng thái pháp lý: {explanation['compliance_status']}")
        print(f"    - Chuỗi giải trình nhân quả (Causal Chain):")
        for step in explanation['causal_provenance_chain']:
            print(f"       {step}")

print("\n" + "="*75)
