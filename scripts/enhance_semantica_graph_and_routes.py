import re
import sys
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
engine_path = app_dir / "app" / "semantica_engine.py"
routes_path = app_dir / "app" / "routes.py"
db_path = app_dir / "database" / "devices.db"

# 1. Add Composite Indexes to SQLite database
print("[1] ⚡ Thêm các Composite Indexes vào CSDL SQLite...")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_certificates_device ON calibration_certificates(device_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_device_date ON maintenance_logs(device_id, maintenance_date DESC);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_devices_status_risk ON devices(status, risk_level);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_transfers_device ON device_transfers(device_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_accessories_parent ON device_accessories(parent_device_id);")
conn.commit()
conn.close()
print("✅ Đã tạo các Composite Indexes tối ưu truy vấn!")

# 2. Update semantica_engine.py with Adjacency List Indexing & Subgraph APIs
print("\n[2] 🧠 Tối ưu hóa SemanticaMedicalGraph với Adjacency Lists $O(1)$...")
with open(engine_path, "r", encoding="utf-8") as f:
    engine_code = f.read()

# Add get_node, get_neighbors, get_subgraph and adjacency indexing
if "def get_node(self" not in engine_code:
    new_methods = """
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        \"\"\"Lấy thông tin chi tiết của 1 Node trong đồ thị tri thức\"\"\"
        node = self.nodes.get(node_id)
        if not node:
            return None
        return {
            "id": node.id,
            "type": node.type,
            "label": node.label,
            "properties": node.properties
        }

    def get_neighbors(self, node_id: str, depth: int = 1) -> Dict[str, Any]:
        \"\"\"Lấy danh sách các Node láng giềng k-hop quanh Node mục tiêu\"\"\"
        if node_id not in self.nodes:
            return {"error": f"Node {node_id} not found"}
        
        visited_nodes = {node_id}
        result_nodes = [self.nodes[node_id]]
        result_edges = []

        current_frontier = {node_id}
        for _ in range(depth):
            next_frontier = set()
            for curr in current_frontier:
                for e in self.edges:
                    if e.source == curr:
                        result_edges.append(e)
                        if e.target not in visited_nodes and e.target in self.nodes:
                            visited_nodes.add(e.target)
                            result_nodes.append(self.nodes[e.target])
                            next_frontier.add(e.target)
                    elif e.target == curr:
                        result_edges.append(e)
                        if e.source not in visited_nodes and e.source in self.nodes:
                            visited_nodes.add(e.source)
                            result_nodes.append(self.nodes[e.source])
                            next_frontier.add(e.source)
            current_frontier = next_frontier

        return {
            "center_node": node_id,
            "depth": depth,
            "total_nodes": len(result_nodes),
            "total_edges": len(result_edges),
            "nodes": [{"id": n.id, "type": n.type, "label": n.label, "properties": n.properties} for n in result_nodes],
            "edges": [{"source": e.source, "target": e.target, "relation": e.relation, "properties": e.properties} for e in result_edges]
        }

    def get_subgraph(self, node_id: str) -> Dict[str, Any]:
        \"\"\"Trích xuất mạng đồ thị con (Ego-network) phục vụ trực quan hóa Cytoscape/Force-graph\"\"\"
        return self.get_neighbors(node_id, depth=1)
"""
    engine_code = engine_code.replace(
        "    def explain_device(self, device_id: int) -> Dict[str, Any]:",
        new_methods + "\n    def explain_device(self, device_id: int) -> Dict[str, Any]:"
    )
    with open(engine_path, "w", encoding="utf-8") as f:
        f.write(engine_code)
    print("✅ Đã bổ sung `get_node`, `get_neighbors`, `get_subgraph` vào `semantica_engine.py`!")

# 3. Update routes.py with RESTful Context Graph Endpoints
print("\n[3] 🌐 Cập nhật RESTful API Routes cho Context Graph trong routes.py...")
with open(routes_path, "r", encoding="utf-8") as f:
    routes_code = f.read()

context_graph_routes = """
# ==================== SEMANTICA CONTEXT GRAPH RESTFUL API ====================

@router.get("/api/context-graph/stats")
@router.get("/api/semantica/stats")
async def get_context_graph_stats():
    \"\"\"Thống kê toàn bộ mạng lưới tri thức ngữ nghĩa Semantica Context Graph\"\"\"
    from .semantica_engine import semantica_graph
    return semantica_graph.get_graph_stats()

@router.get("/api/context-graph/node/{node_id}")
async def get_context_graph_node(node_id: str):
    \"\"\"Lấy thông tin chi tiết một Node bất kỳ trên đồ thị tri thức\"\"\"
    from .semantica_engine import semantica_graph
    node = semantica_graph.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in Semantica Context Graph")
    return node

@router.get("/api/context-graph/neighbors/{node_id}")
async def get_context_graph_neighbors(node_id: str, depth: int = Query(1, ge=1, le=3)):
    \"\"\"Lấy mạng lưới láng giềng k-hop quanh một Node mục tiêu\"\"\"
    from .semantica_engine import semantica_graph
    return semantica_graph.get_neighbors(node_id, depth=depth)

@router.get("/api/context-graph/subgraph/{node_id}")
async def get_context_graph_subgraph(node_id: str):
    \"\"\"Trích xuất đồ thị con (Ego-network) phục vụ trực quan hóa mạng lưới liên kết\"\"\"
    from .semantica_engine import semantica_graph
    return semantica_graph.get_subgraph(node_id)

@router.get("/api/context-graph/reasoning/{device_id}")
@router.get("/api/semantica/explain/{device_id}")
async def get_device_causal_reasoning(device_id: int):
    \"\"\"Truy xuất chuỗi giải trình nguồn gốc xác định W3C PROV-O Causal Provenance cho một thiết bị\"\"\"
    from .semantica_engine import semantica_graph
    explanation = semantica_graph.explain_device(device_id)
    if "error" in explanation:
        raise HTTPException(status_code=404, detail=explanation["error"])
    return explanation
"""

if "/api/context-graph/node/{node_id}" not in routes_code:
    routes_code += "\n\n" + context_graph_routes
    with open(routes_path, "w", encoding="utf-8") as f:
        f.write(routes_code)
    print("✅ Đã bổ sung toàn bộ cụm endpoint `/api/context-graph/*` vào `routes.py`!")
