"""
任务状态 API 路由

功能：
1. 查询 Celery 任务状态
2. 获取任务结果
3. 撤销任务
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import User
from ...db.session import get_async_session
from ...services.auth import get_current_user_required
from ...services.celery_tasks import celery_task_service
from ...utils.logger import logger

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[dict] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class TaskListResponse(BaseModel):
    active_tasks: list


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user_required),
):
    """查询任务状态"""
    status_info = celery_task_service.get_task_status(task_id)

    return TaskStatusResponse(
        task_id=task_id,
        status=status_info.get("status", "UNKNOWN"),
        progress=status_info.get("progress"),
        result=status_info.get("result"),
        error=status_info.get("error"),
    )


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    terminate: bool = Query(False, description="是否强制终止"),
    current_user: User = Depends(get_current_user_required),
):
    """取消/撤销任务"""
    success = celery_task_service.revoke_task(task_id, terminate=terminate)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel task")

    return {"msg": "Task cancelled successfully", "task_id": task_id}


@router.get("/", response_model=TaskListResponse)
async def list_active_tasks(
    current_user: User = Depends(get_current_user_required),
):
    """获取当前活跃任务列表"""
    tasks = celery_task_service.get_active_tasks()

    return TaskListResponse(active_tasks=tasks)
