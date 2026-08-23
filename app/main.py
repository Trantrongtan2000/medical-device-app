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

from fastapi import FastAPI
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
from .database import init_database
from .semantica_engine import semantica_engine

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(schedules_router)
app.include_router(inspections_router)
app.include_router(repairs_router)
app.include_router(transfers_router)
app.include_router(documents_router)

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
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Medical Device Management System (BVQ7)",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")