from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form, Depends
from pathlib import Path
import uuid
from datetime import datetime
from typing import Dict
from src.config import settings
from src.services.whisper_service import generate_subtitles
from src.services.video_service import VideoDubbingService
from src.services.tts_service import TTSService
from src.schemas.tasks import TaskResponse, TaskStatus

router = APIRouter(prefix="/api/v1", tags=["dubbing"])

# Lưu trữ trạng thái task trong memory (có thể thay bằng Redis)
tasks_db: Dict[uuid.UUID, dict] = {}

# Dependency để lấy service
def get_video_service():
    tts = TTSService()
    return VideoDubbingService(tts)

@router.post("/subtitles", response_model=TaskResponse)
async def create_subtitles_task(
    background_tasks: BackgroundTasks,
    video_name: str = Form(..., description="Tên file video (không bao gồm .mp4)"),
    # Có thể cho phép upload file thay vì dùng file có sẵn
):
    """
    Tạo phụ đề từ video có sẵn trong thư mục downloads.
    Trả về task ID để theo dõi tiến trình.
    """
    # Kiểm tra file video tồn tại
    video_path = settings.downloads_dir / f"{video_name}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    task_id = uuid.uuid4()
    output_srt = settings.srt_dir / f"{video_name}.srt"
    
    # Lưu task
    tasks_db[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "created_at": datetime.now(),
        "type": "subtitles"
    }
    
    # Chạy background task
    background_tasks.add_task(
        process_subtitles_task,
        task_id,
        video_path,
        output_srt,
        settings.whisper_model_size
    )
    
    return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)

async def process_subtitles_task(task_id: uuid.UUID, video_path: Path, output_srt: Path, model_size: str):
    """Xử lý nền"""
    tasks_db[task_id]["status"] = TaskStatus.PROCESSING
    try:
        await generate_subtitles(video_path, output_srt, model_size)
        tasks_db[task_id]["status"] = TaskStatus.COMPLETED
        tasks_db[task_id]["output_path"] = str(output_srt)
    except Exception as e:
        tasks_db[task_id]["status"] = TaskStatus.FAILED
        tasks_db[task_id]["error"] = str(e)
    finally:
        tasks_db[task_id]["completed_at"] = datetime.now()

@router.post("/dubbing", response_model=TaskResponse)
async def create_dubbing_task(
    background_tasks: BackgroundTasks,
    video_name: str = Form(...),
    srt_name: str = Form(...),
    service: VideoDubbingService = Depends(get_video_service)
):
    """
    Tạo video lồng tiếng từ file SRT (có thể là gốc hoặc đã dịch).
    """
    video_path = settings.downloads_dir / f"{video_name}.mp4"
    srt_path = settings.srt_dir / f"{srt_name}.srt"
    output_path = settings.export_dir / f"{video_name}_dubbed_{uuid.uuid4().hex[:8]}.mp4"
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    if not srt_path.exists():
        raise HTTPException(status_code=404, detail="SRT file not found")
    
    task_id = uuid.uuid4()
    tasks_db[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "created_at": datetime.now(),
        "type": "dubbing"
    }
    
    background_tasks.add_task(
        process_dubbing_task,
        task_id,
        service,
        video_path,
        srt_path,
        output_path
    )
    
    return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)

async def process_dubbing_task(task_id: uuid.UUID, service: VideoDubbingService,
                               video_path: Path, srt_path: Path, output_path: Path):
    tasks_db[task_id]["status"] = TaskStatus.PROCESSING
    try:
        await service.create_dubbed_video(video_path, srt_path, output_path)
        tasks_db[task_id]["status"] = TaskStatus.COMPLETED
        tasks_db[task_id]["output_path"] = str(output_path)
    except Exception as e:
        tasks_db[task_id]["status"] = TaskStatus.FAILED
        tasks_db[task_id]["error"] = str(e)
    finally:
        tasks_db[task_id]["completed_at"] = datetime.now()

@router.get("/tasks/{task_id}", response_model=dict)
async def get_task_status(task_id: uuid.UUID):
    """Kiểm tra trạng thái task"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Endpoint upload video (tuỳ chọn)
@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.endswith('.mp4'):
        raise HTTPException(400, "Only MP4 files are allowed")
    file_path = settings.downloads_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return {"filename": file.filename, "path": str(file_path)}