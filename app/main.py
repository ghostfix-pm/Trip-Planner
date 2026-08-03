# main.py
import contextlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.planner import router as planner_router

# Import routes đúng theo cấu trúc v1 của bạn
from app.api.v1.routers import auth, config
from app.config import get_settings
from app.db.database import init_db

settings = get_settings()

def _parse_cors_origins(raw: str) -> list[str]:
    """Split a comma-separated CORS origins string into a list."""
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

# 1. LIFESPAN: Khởi tạo Database khi bật server
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB khi chạy server
    await init_db()
    yield
    # Dọn dẹp tài nguyên ở đây nếu cần

# 2. KHỞI TẠO APP (Đảm bảo chỉ có 1 biến app duy nhất trong toàn file)
app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 3. CẤU HÌNH CORS - origins lấy từ settings (CORS_ORIGINS trong .env)
cors_origins = _parse_cors_origins(settings.CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Trip-Id"]
)

# 4. GẮN ROUTERS
app.include_router(auth.router, prefix="/api/v1")
app.include_router(planner_router, prefix="/api/v1")
app.include_router(config.router, prefix="/api/v1")

# 5. CẤU HÌNH GIAO DIỆN & HEALTH CHECK
frontend_dir = Path(__file__).resolve().parent / "frontend"

# Bọc trong try-except phòng trường hợp bạn chưa tạo thư mục frontend/static
try:
    app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")
except RuntimeError:
    print("⚠️ Cảnh báo: Thư mục frontend/static chưa tồn tại, bỏ qua mount static files.")

@app.get("/", include_in_schema=False)
def index():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend chưa được cài đặt."}

@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
