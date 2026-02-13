from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from src.config import settings
from src.api.routes import router
from src.dashboard.routes import dashboard_router
from src.utils.logging_config import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo các thư mục cần thiết
    settings.downloads_dir.mkdir(parents=True, exist_ok=True)
    settings.srt_dir.mkdir(parents=True, exist_ok=True)
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    setup_logging()
    
    yield
    
    # Cleanup khi shutdown (có thể xoá temp)
    # Tuỳ chọn: giữ lại hoặc xoá
    # import shutil
    # shutil.rmtree(settings.temp_dir, ignore_errors=True)

app = FastAPI(
    title="Video Dubbing API",
    description="Tự động tạo phụ đề và lồng tiếng video",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(dashboard_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )