"""
Main Application cho Medical Device Management System (BV Quận 7)
FastAPI Backend Server
"""
import sys
import io
from pathlib import Path
from datetime import datetime

# UTF-8 handling for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .routes import router
from .routes_schedules import router as schedules_router
from contextlib import asynccontextmanager
from .routes_inspections import router as inspections_router
from .routes_repairs import router as repairs_router
from .routes_transfers import router as transfers_router
from .routes_documents import router as documents_router
from .routes_audit_capa import router as audit_capa_router
from .routes_agent import router as agent_router
from .database import init_database, get_db_connection
from .config import get_settings
from .semantica_engine import semantica_engine

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler: Khởi tạo database và nạp graph engine an toàn"""
    print("[INFO] Khởi tạo cơ sở dữ liệu SQLite...")
    init_database()
    print("[INFO] Khởi tạo mạng tri thức Semantica Graph Engine...")
    try:
        semantica_engine.reload()
        print("[OK] Semantica Engine sẵn sàng hoạt động!")
    except Exception as e:
        print(f"[WARN] Semantica reload deferred: {e}")
    print("[OK] Database & Services sẵn sàng hoạt động!")
    yield

app = FastAPI(
    title="Hệ Thống Quản Lý Trang Thiết Bị Y Tế - BV Quận 7",
    description="Ứng dụng quản lý tài sản, kiểm định, hiệu chuẩn & bảo trì thiết bị y tế",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (an toàn theo cấu hình môi trường, tránh '*' + credentials)
app.add_middleware(CORSMiddleware, **settings.cors_config())


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Thêm security headers cơ bản cho mọi response."""
    response = await call_next(request)
    if settings.security_headers:
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        # CSP nhẹ: cho phép self + CDN đang dùng (Bootstrap/Chart.js) và inline hiện có.
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: blob:; "
            "frame-ancestors 'self'",
        )
    return response

# Include API routes
app.include_router(router)
app.include_router(schedules_router)
app.include_router(inspections_router)
app.include_router(repairs_router)
app.include_router(transfers_router)
app.include_router(documents_router)
app.include_router(audit_capa_router)
app.include_router(agent_router)

# Mount static directories
web_dir = Path(__file__).parent.parent / "web"
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

if (web_dir / "css").exists():
    app.mount("/css", StaticFiles(directory=str(web_dir / "css")), name="css")

if (web_dir / "js").exists():
    app.mount("/js", StaticFiles(directory=str(web_dir / "js")), name="js")

if (web_dir / "img").exists():
    app.mount("/img", StaticFiles(directory=str(web_dir / "img")), name="img")

diagrams_dir = Path(__file__).parent.parent / "docs" / "diagrams"
if diagrams_dir.exists():
    app.mount("/diagrams", StaticFiles(directory=str(diagrams_dir)), name="diagrams")



@app.get("/")
async def root():
    """Root endpoint - phục vụ trang chủ dashboard"""
    index_file = web_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
@app.get("/health/live")
async def health_check():
    """Liveness probe: tiến trình còn sống."""
    return {
        "status": "healthy",
        "app": "Medical Device Management System (BVQ7)",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/ready")
async def health_ready():
    """Readiness probe: kiểm tra kết nối và tính toàn vẹn CSDL."""
    checks = {"database": False, "devices_table": False}
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1").fetchone()
            checks["database"] = True
            conn.execute("SELECT COUNT(*) FROM devices").fetchone()
            checks["devices_table"] = True
    except Exception as exc:  # pragma: no cover - đường lỗi hạ tầng
        return {
            "status": "not_ready",
            "checks": checks,
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        }
    return {
        "status": "ready",
        "checks": checks,
        "environment": settings.environment,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")