"""
API Key Rotation & Management System for Gemini AI and Mistral OCR
Hỗ trợ:
- Quản lý danh sách nhiều API Keys (Multi-Key Pool)
- Tự động xoay key (Round-Robin & Failover on Rate Limits / Quota Exhaustion)
- Lưu trữ cấu hình bền vững vào SQLite
- Theo dõi trạng thái hoạt động (Active, Rate-Limited, Cooldown, Invalid)
"""

import os
import time
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent / "medical_devices.db"

class KeyPool:
    def __init__(self, service_name: str, env_var_names: List[str]):
        self.service_name = service_name
        self.env_var_names = env_var_names
        self.keys: List[Dict[str, Any]] = [] # [{key: str, status: 'ACTIVE'|'RATE_LIMITED'|'INVALID', last_used: float, fail_count: int}]
        self.current_idx = 0
        self._init_db()
        self._load_keys()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_keys_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                api_key TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _load_keys(self):
        self.keys = []
        # 1. Load from Environment Variables first
        for var in self.env_var_names:
            val = os.environ.get(var)
            if val:
                for k in val.split(","):
                    k = k.strip()
                    if k and not any(item["key"] == k for item in self.keys):
                        self.keys.append({
                            "key": k,
                            "status": "ACTIVE",
                            "last_used": 0,
                            "fail_count": 0
                        })

        # 2. Load from Database
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            rows = cur.execute("SELECT api_key, status FROM api_keys_config WHERE service_name = ?", (self.service_name,)).fetchall()
            for r in rows:
                k, status = r[0].strip(), r[1]
                if k and not any(item["key"] == k for item in self.keys):
                    self.keys.append({
                        "key": k,
                        "status": status,
                        "last_used": 0,
                        "fail_count": 0
                    })
            conn.close()
        except Exception as e:
            print(f"[WARN] Không thể đọc keys từ DB: {e}")

    def add_keys(self, new_keys_str: str) -> int:
        """Thêm 1 hoặc nhiều API keys mới (ngăn cách bằng dấu phẩy hoặc xuống dòng)"""
        added_count = 0
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Split by comma or newlines
        raw_keys = [k.strip() for k in new_keys_str.replace("\n", ",").split(",") if k.strip()]
        for k in raw_keys:
            if not any(item["key"] == k for item in self.keys):
                self.keys.append({
                    "key": k,
                    "status": "ACTIVE",
                    "last_used": 0,
                    "fail_count": 0
                })
                try:
                    cur.execute("INSERT OR IGNORE INTO api_keys_config (service_name, api_key, status) VALUES (?, ?, 'ACTIVE')", (self.service_name, k))
                    added_count += 1
                except Exception:
                    pass
                    
        conn.commit()
        conn.close()
        return added_count

    def remove_key(self, api_key: str) -> bool:
        """Xóa 1 API key khỏi cấu hình"""
        self.keys = [k for k in self.keys if k["key"] != api_key]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM api_keys_config WHERE service_name = ? AND api_key = ?", (self.service_name, api_key))
        conn.commit()
        conn.close()
        return True

    def get_next_active_key(self) -> Optional[str]:
        """Lấy API Key hoạt động tiếp theo theo cơ chế Round-Robin & Auto-Failover"""
        if not self.keys:
            return None

        now = time.time()
        # Reset cooldown for rate-limited keys after 60 seconds
        for k in self.keys:
            if k["status"] == "RATE_LIMITED" and (now - k["last_used"]) > 60:
                k["status"] = "ACTIVE"
                k["fail_count"] = 0

        active_keys = [k for k in self.keys if k["status"] == "ACTIVE"]
        if not active_keys:
            # If all are exhausted, fallback to any non-invalid key
            active_keys = [k for k in self.keys if k["status"] != "INVALID"]

        if not active_keys:
            return None

        # Round Robin
        self.current_idx = self.current_idx % len(active_keys)
        chosen = active_keys[self.current_idx]
        chosen["last_used"] = now
        self.current_idx = (self.current_idx + 1) % len(active_keys)
        return chosen["key"]

    def mark_rate_limited(self, api_key: str):
        """Đánh dấu key bị quá tải (HTTP 429) để tạm ngưng 60 giây và xoay sang key khác"""
        for k in self.keys:
            if k["key"] == api_key:
                k["status"] = "RATE_LIMITED"
                k["last_used"] = time.time()
                k["fail_count"] += 1
                print(f"[KEY ROTATOR] Đã xoay key {self.service_name} do đạt giới hạn (Rate-Limited): {api_key[:8]}...****")

    def mark_invalid(self, api_key: str):
        """Đánh dấu key không hợp lệ (HTTP 401/403)"""
        for k in self.keys:
            if k["key"] == api_key:
                k["status"] = "INVALID"
                k["last_used"] = time.time()

    def get_status_summary(self) -> List[Dict[str, Any]]:
        """Trả về danh sách key đã che bớt để hiển thị lên UI an toàn"""
        res = []
        for i, k in enumerate(self.keys):
            raw = k["key"]
            masked = raw[:6] + "..." + raw[-4:] if len(raw) > 10 else "******"
            res.append({
                "id": i + 1,
                "masked_key": masked,
                "raw_key": raw,
                "status": k["status"],
                "fail_count": k["fail_count"],
                "last_used_seconds_ago": int(time.time() - k["last_used"]) if k["last_used"] > 0 else None
            })
        return res


# Singleton Key Pools
gemini_key_pool = KeyPool("gemini", ["GEMINI_API_KEY", "GOOGLE_API_KEY"])
mistral_key_pool = KeyPool("mistral", ["MISTRAL_API_KEY"])
