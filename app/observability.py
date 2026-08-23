"""
Structured Observability & Audit Trail Engine
Theo dõi độ trễ, lưu lượng token, quyết định phân luồng và truy vết lỗi chuẩn JSON.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from collections import deque
from app.models_core import TelemetryEvent

LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TELEMETRY_LOG_FILE = LOGS_DIR / "telemetry.jsonl"

class TelemetryCollector:
    """Thu thập và quản lý nhật ký hoạt động của Agent Runtime"""
    
    def __init__(self, max_in_memory: int = 200):
        self.buffer = deque(maxlen=max_in_memory)
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger("NOOA_TELEMETRY")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(str(TELEMETRY_LOG_FILE), encoding="utf-8")
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_event(self, event: TelemetryEvent):
        """Ghi nhận sự kiện telemetry chuẩn hóa"""
        event_dict = event.model_dump()
        
        # Lưu in-memory buffer
        self.buffer.append(event_dict)
        
        # Ghi file JSONL
        try:
            self.logger.info(json.dumps(event_dict, ensure_ascii=False))
        except Exception as e:
            print(f"[WARN] Không thể ghi telemetry log: {e}")

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy danh sách các sự kiện telemetry gần nhất cho Dashboard/Admin"""
        items = list(self.buffer)
        items.reverse()
        return items[:limit]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Tổng hợp chỉ số KPI P50/P95, tỷ lệ định tuyến và lỗi"""
        if not self.buffer:
            return {
                "total_events": 0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "edge_route_rate": 0.0,
                "success_rate": 100.0
            }

        latencies = sorted([e.get("total_latency_ms", 0.0) for e in self.buffer])
        edge_count = sum(1 for e in self.buffer if (e.get("route_decision") or {}).get("route") == "LOCAL_EDGE")
        success_count = sum(1 for e in self.buffer if (e.get("tool_result") or {}).get("success", True))
        
        n = len(latencies)
        p50 = latencies[int(n * 0.50)] if n > 0 else 0.0
        p95 = latencies[int(n * 0.95)] if n > 0 else 0.0

        return {
            "total_events": n,
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "edge_route_rate": round(edge_count / n * 100, 1),
            "success_rate": round(success_count / n * 100, 1)
        }

telemetry_collector = TelemetryCollector()
