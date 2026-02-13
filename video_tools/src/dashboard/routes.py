from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form, Depends
from pathlib import Path
import uuid
from fastapi.responses import HTMLResponse
from typing import List
from datetime import datetime
from typing import Dict
from src.config import settings
from src.services.whisper_service import generate_subtitles
from src.services.video_service import VideoDubbingService
from src.services.tts_service import TTSService
from src.schemas.tasks import TaskResponse, TaskStatus
from src.api.routes import tasks_db

dashboard_router = APIRouter(prefix="", tags=["dubbing"])

@dashboard_router.get("/tasks/{task_id}", response_model=dict)
async def get_task_status(task_id: uuid.UUID):
    """Kiểm tra trạng thái task"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def task_dashboard():
    """
    Trang HTML theo dõi tiến trình tất cả các task.
    Hiển thị bảng các task với trạng thái, thời gian, output/error.
    """
    # Sắp xếp task mới nhất lên đầu
    sorted_tasks = sorted(
        tasks_db.values(),
        key=lambda t: t["created_at"],
        reverse=True
    )

    # Tạo HTML table từ danh sách task
    rows = ""
    for task in sorted_tasks:
        task_id = task["task_id"]
        status = task["status"].value if hasattr(task["status"], "value") else task["status"]
        created = task["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        completed = task.get("completed_at", "")
        if completed:
            completed = completed.strftime("%Y-%m-%d %H:%M:%S")
        output = task.get("output_path", "")
        error = task.get("error", "")
        task_type = task.get("type", "unknown")

        # màu sắc cho trạng thái
        if status == "completed":
            status_color = "green"
        elif status == "failed":
            status_color = "red"
        elif status == "processing":
            status_color = "orange"
        else:
            status_color = "gray"

        rows += f"""
        <tr>
            <td><code>{task_id}</code></td>
            <td>{task_type}</td>
            <td><span style="color: {status_color}; font-weight: bold;">{status}</span></td>
            <td>{created}</td>
            <td>{completed}</td>
            <td style="max-width: 300px; word-break: break-all;">
                {f'<a href="{output}" target="_blank">{Path(output).name}</a>' if output else ''}
                {f'<span style="color:red;">{error}</span>' if error else ''}
            </td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Task Dashboard - Video Dubbing</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="5">  <!-- tự động refresh mỗi 5 giây -->
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 20px;
                background-color: #f9f9f9;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px 8px;
                text-align: left;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
                font-weight: 600;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #eaeaea;
            }}
            .status-badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                color: white;
                font-size: 0.85em;
            }}
            .footer {{
                margin-top: 20px;
                color: #666;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <h1>🎬 Task Monitoring Dashboard</h1>
        <p>Auto-refresh every 5 seconds. Total tasks: {len(sorted_tasks)}</p>
        <table>
            <thead>
                <tr>
                    <th>Task ID</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Created At</th>
                    <th>Completed At</th>
                    <th>Output / Error</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <div class="footer">
            ⚡ Video Dubbing Service · <a href="/dashboard">refresh</a>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content, status_code=200)