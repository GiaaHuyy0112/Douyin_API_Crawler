from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskResponse(BaseModel):
    task_id: UUID
    status: TaskStatus

class TaskResult(BaseModel):
    task_id: UUID
    status: TaskStatus
    output_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None