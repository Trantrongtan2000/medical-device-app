"""
API Key Rotation & Management System for Gemini AI and Mistral OCR
Hỗ trợ:
- Quản lý danh sách nhiều API Keys (Multi-Key Pool)
- Tự động xoay key (Round-Robin & Failover on Rate Limits / Quota Exhaustion)
- Thêm, Sửa, Xóa, Bật/Tắt, Đặt ưu tiên (Full CRUD)
- Kiểm thử kết nối Live (Test API Connectivity & Latency ms)
- Lưu trữ cấu hình bền vững vào SQLite
- Theo dõi trạng thái hoạt động (Active, Inactive, Rate-Limited, Invalid)
"""

import os
import time
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "devices.db"
if not DB_PATH.parent.exists():
    DB_PATH = Path(__file__).parent / "medical_devices.db"

class KeyPool:
    def __init__(self, service_name: str, env_var_names: List[str]):
        self.service_name = service_name
        self.env_var_names = env_var_names
        self.keys: List[Dict[str, Any]] = []  # [{key, status, last_used, fail_count, last_latency_ms, created_at}]
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
                            "fail_count": 0,
                            "last_latency_ms": None,
                            "source": "ENV"
                        })

        # 2. Load from Database
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            rows = cur.execute("SELECT api_key, status FROM api_keys_config WHERE service_name = ?", (self.service_name,)).fetchall()
            for r in rows:
                k, status = r[0].strip(), r[1]
                existing = next((item for item in self.keys if item["key"] == k), None)
                if existing:
                    existing["status"] = status
                    existing["source"] = "DB+ENV"
                else:
                    self.keys.append({
                        "key": k,
                        "status": status,
                        "last_used": 0,
                        "fail_count": 0,
                        "last_latency_ms": None,
                        "source": "DB"
                    })
            conn.close()
        except Exception as e:
            print(f"[WARN] Không thể đọc keys từ DB: {e}")

    def add_keys(self, new_keys_str: str) -> int:
        """Thêm 1 hoặc nhiều API keys mới (ngăn cách bằng dấu phẩy hoặc xuống dòng)"""
        added_count = 0
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        raw_keys = [k.strip() for k in new_keys_str.replace("\n", ",").split(",") if k.strip()]
        for k in raw_keys:
            existing = next((item for item in self.keys if item["key"] == k), None)
            if not existing:
                self.keys.append({
                    "key": k,
                    "status": "ACTIVE",
                    "last_used": 0,
                    "fail_count": 0,
                    "last_latency_ms": None,
                    "source": "DB"
                })
            try:
                cur.execute("INSERT OR IGNORE INTO api_keys_config (service_name, api_key, status) VALUES (?, ?, 'ACTIVE')", (self.service_name, k))
                if cur.rowcount > 0:
                    added_count += 1
            except Exception:
                pass
                    
        conn.commit()
        conn.close()
        return added_count

    def update_key(self, old_key: str, new_key: str, status: Optional[str] = None) -> bool:
        """Chỉnh sửa thông tin và giá trị của một API Key"""
        old_key = old_key.strip()
        new_key = new_key.strip()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Update in-memory list
        for item in self.keys:
            if item["key"] == old_key:
                item["key"] = new_key
                if status:
                    item["status"] = status
                item["fail_count"] = 0
                break

        # Update SQLite
        try:
            if status:
                cur.execute(
                    "UPDATE api_keys_config SET api_key = ?, status = ? WHERE service_name = ? AND api_key = ?",
                    (new_key, status, self.service_name, old_key)
                )
            else:
                cur.execute(
                    "UPDATE api_keys_config SET api_key = ? WHERE service_name = ? AND api_key = ?",
                    (new_key, self.service_name, old_key)
                )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật key trong DB: {e}")
            conn.close()
            return False

    def set_key_status(self, api_key: str, status: str) -> bool:
        """Cập nhật trạng thái của API key: ACTIVE, INACTIVE, RATE_LIMITED, INVALID"""
        api_key = api_key.strip()
        for item in self.keys:
            if item["key"] == api_key:
                item["status"] = status
                break
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE api_keys_config SET status = ? WHERE service_name = ? AND api_key = ?", (status, self.service_name, api_key))
        conn.commit()
        conn.close()
        return True

    def set_primary_key(self, api_key: str) -> bool:
        """Đưa API key lên vị trí ưu tiên số 1 (Head of Pool)"""
        api_key = api_key.strip()
        target = next((item for item in self.keys if item["key"] == api_key), None)
        if target:
            self.keys.remove(target)
            self.keys.insert(0, target)
            self.current_idx = 0
            return True
        return False

    def remove_key(self, api_key: str) -> bool:
        """Xóa 1 API key khỏi cấu hình và CSDL"""
        api_key = api_key.strip()
        self.keys = [k for k in self.keys if k["key"] != api_key]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM api_keys_config WHERE service_name = ? AND api_key = ?", (self.service_name, api_key))
        conn.commit()
        conn.close()
        return True

    def test_key(self, api_key: str) -> Dict[str, Any]:
        """Kiểm thử kết nối API trực tiếp (Live Connectivity Test) & đo độ trễ ms"""
        api_key = api_key.strip()
        start_time = time.time()
        
        if self.service_name == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents="Ping test! Trả lời 'OK' 1 từ."
                )
                latency = int((time.time() - start_time) * 1000)
                # update memory
                for k in self.keys:
                    if k["key"] == api_key:
                        k["last_latency_ms"] = latency
                        k["status"] = "ACTIVE"
                        k["fail_count"] = 0
                return {
                    "valid": True,
                    "status": "SUCCESS",
                    "latency_ms": latency,
                    "message": f"Google Gemini API kết nối hoàn hảo (Độ trễ: {latency}ms)",
                    "response": response.text.strip() if response and response.text else "OK"
                }
            except Exception as e:
                latency = int((time.time() - start_time) * 1000)
                return {
                    "valid": False,
                    "status": "ERROR",
                    "latency_ms": latency,
                    "message": f"Lỗi xác thực Gemini API: {str(e)}"
                }

        elif self.service_name == "mistral":
            try:
                from mistralai import Mistral
                client = Mistral(api_key=api_key)
                # Lightweight call: list models or ping
                client.models.list()
                latency = int((time.time() - start_time) * 1000)
                for k in self.keys:
                    if k["key"] == api_key:
                        k["last_latency_ms"] = latency
                        k["status"] = "ACTIVE"
                        k["fail_count"] = 0
                return {
                    "valid": True,
                    "status": "SUCCESS",
                    "latency_ms": latency,
                    "message": f"Mistral OCR API kết nối hoàn hảo (Độ trễ: {latency}ms)"
                }
            except Exception as e:
                latency = int((time.time() - start_time) * 1000)
                return {
                    "valid": False,
                    "status": "ERROR",
                    "latency_ms": latency,
                    "message": f"Lỗi xác thực Mistral API: {str(e)}"
                }

        return {"valid": False, "status": "UNKNOWN", "message": "Dịch vụ không xác định"}

    def get_next_active_key(self) -> Optional[str]:
        """Lấy API Key hoạt động tiếp theo theo cơ chế Round-Robin & Auto-Failover"""
        if not self.keys:
            return None

        now = time.time()
        for k in self.keys:
            if k["status"] == "RATE_LIMITED" and (now - k["last_used"]) > 60:
                k["status"] = "ACTIVE"
                k["fail_count"] = 0

        active_keys = [k for k in self.keys if k["status"] == "ACTIVE"]
        if not active_keys:
            active_keys = [k for k in self.keys if k["status"] not in ["INVALID", "INACTIVE"]]

        if not active_keys:
            return None

        self.current_idx = self.current_idx % len(active_keys)
        chosen = active_keys[self.current_idx]
        chosen["last_used"] = now
        self.current_idx = (self.current_idx + 1) % len(active_keys)
        return chosen["key"]

    @staticmethod
    def mask_key(raw: str) -> str:
        """Định dạng che giấu API key chuẩn bảo mật (VD: AIzaSy...9aXy)"""
        if not raw:
            return "******"
        return raw[:6] + "..." + raw[-4:] if len(raw) > 10 else "******"

    def mark_rate_limited(self, api_key: str):
        """Đánh dấu key bị quá tải (HTTP 429) để tạm ngưng 60 giây và xoay sang key khác"""
        for k in self.keys:
            if k["key"] == api_key:
                k["status"] = "RATE_LIMITED"
                k["last_used"] = time.time()
                k["fail_count"] += 1
                print(f"[KEY ROTATOR] Đã xoay key {self.service_name} do Rate-Limited: {self.mask_key(api_key)}")

    def mark_invalid(self, api_key: str):
        """Đánh dấu key không hợp lệ (HTTP 401/403)"""
        for k in self.keys:
            if k["key"] == api_key:
                k["status"] = "INVALID"
                k["last_used"] = time.time()
                print(f"[KEY ROTATOR] Đã vô hiệu hóa key {self.service_name} không hợp lệ: {self.mask_key(api_key)}")

    def get_detailed_list(self) -> List[Dict[str, Any]]:
        """Trả về danh sách đầy đủ thông tin để người dùng quản lý & chỉnh sửa"""
        res = []
        for i, k in enumerate(self.keys):
            raw = k["key"]
            masked = self.mask_key(raw)
            res.append({
                "id": i + 1,
                "service": self.service_name,
                "masked_key": masked,
                "status": k["status"],
                "fail_count": k["fail_count"],
                "last_latency_ms": k.get("last_latency_ms"),
                "is_primary": (i == 0),
                "source": k.get("source", "DB"),
                "last_used_seconds_ago": int(time.time() - k["last_used"]) if k["last_used"] > 0 else None
            })
        return res

    def get_pool_stats(self) -> Dict[str, Any]:
        """Trả về thống kê tổng hợp số lượng key theo trạng thái"""
        return {
            "service": self.service_name,
            "total_keys": len(self.keys),
            "active_keys": len([k for k in self.keys if k["status"] == "ACTIVE"]),
            "inactive_keys": len([k for k in self.keys if k["status"] == "INACTIVE"]),
            "rate_limited_keys": len([k for k in self.keys if k["status"] == "RATE_LIMITED"]),
            "invalid_keys": len([k for k in self.keys if k["status"] == "INVALID"]),
            "keys_list": self.get_detailed_list()
        }


# Singleton Key Pools
gemini_key_pool = KeyPool("gemini", ["GEMINI_API_KEY", "GOOGLE_API_KEY"])
mistral_key_pool = KeyPool("mistral", ["MISTRAL_API_KEY"])
