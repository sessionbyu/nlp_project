"""
文件上传 API 路由

功能：
1. CSV/Excel 文件上传
2. 批量文本提取
3. 批量预测
4. 结果导出
"""
import uuid
from typing import List, Optional
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import User, PredictionHistory
from ...db.session import get_async_session
from ...services.auth import get_current_user_required
from ...services.file_upload import file_upload_service
from ...services.inference import predict_batch
from ...utils.logger import logger

router = APIRouter(prefix="/upload", tags=["File Upload"])


# ========== Pydantic Schemas ==========

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    texts_count: int


class BatchAnalysisRequest(BaseModel):
    text_column: Optional[str] = Field(None, description="文本列名（自动检测）")
    model_key: Optional[str] = Field(None, description="使用的模型")


class BatchAnalysisResponse(BaseModel):
    task_id: str
    file_id: str
    status: str
    total: int
    success: int
    failed: int
    results: List[dict]


class AsyncTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


# ========== API Endpoints ==========

@router.post("/file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="上传的CSV/Excel/TXT文件"),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """
    上传文件并提取文本

    - 支持 CSV, Excel (.xlsx, .xls), TXT, JSON 格式
    - 自动检测文本列
    - 返回提取的文本数量
    """
    # 验证文件
    await file_upload_service.validate_file(file)

    # 保存文件
    file_path = await file_upload_service.save_uploaded_file(file)
    file_id = os.path.basename(file_path)

    # 提取文本
    texts = await file_upload_service.extract_texts_from_file(file)

    # 获取文件大小
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    logger.info(f"File uploaded: {file.filename}, texts_count={len(texts)}, user={current_user.username}")

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        size=size,
        texts_count=len(texts),
    )


@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze(
    file: UploadFile = File(..., description="CSV/Excel文件"),
    request: BatchAnalysisRequest = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """
    批量分析文件中的文本

    - 上传文件并自动提取文本
    - 使用指定模型进行批量预测
    - 保存结果到数据库
    - 返回详细的分析结果
    """
    # 验证文件
    await file_upload_service.validate_file(file)

    # 提取文本
    texts = await file_upload_service.extract_texts_from_file(file, request.text_column)

    # 确定模型
    from ...core.config import settings
    model_key = request.model_key or settings.DEFAULT_MODEL

    # 批量预测
    batch_results = await predict_batch(texts, model_key=model_key)

    # 保存到数据库
    results = []
    success_count = 0
    failed_count = 0

    for text, result in zip(texts, batch_results):
        if "error" in result:
            results.append({
                "text": text,
                "success": False,
                "error": result["error"],
            })
            failed_count += 1
        else:
            try:
                # 保存预测记录
                record = PredictionHistory(
                    user_id=current_user.id,
                    input_text=text,
                    label=result["label"],
                    score=result["score"],
                    model_key=model_key,
                )
                session.add(record)
                results.append({
                    "text": text,
                    "success": True,
                    "label": result["label"],
                    "score": result["score"],
                })
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to save prediction: {e}")
                results.append({
                    "text": text,
                    "success": False,
                    "error": str(e),
                })
                failed_count += 1

    await session.commit()

    logger.info(
        f"Batch analysis completed: file={file.filename}, "
        f"total={len(texts)}, success={success_count}, failed={failed_count}"
    )

    return BatchAnalysisResponse(
        task_id=str(uuid.uuid4()),
        file_id=os.path.basename(file_path),
        status="completed",
        total=len(texts),
        success=success_count,
        failed=failed_count,
        results=results,
    )


@router.post("/async-analyze", response_model=AsyncTaskResponse)
async def async_analyze_file(
    file: UploadFile = File(..., description="CSV/Excel文件"),
    request: BatchAnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user_required),
):
    """
    异步分析文件（使用 Celery）

    - 上传文件后立即返回 task_id
    - 后台 Celery 任务执行分析
    - 通过 WebSocket 或轮询 /api/v1/tasks/{task_id} 获取进度
    """
    # 验证文件
    await file_upload_service.validate_file(file)

    # 保存文件
    file_path = await file_upload_service.save_uploaded_file(file)

    # 提交 Celery 任务
    from ...services.celery_tasks import celery_app, analyze_file_task

    model_key = request.model_key or "bert"

    task = analyze_file_task.delay(
        file_path=file_path,
        model_key=model_key,
        text_column=request.text_column,
    )

    logger.info(f"Async analysis task started: {task.id}, user={current_user.username}")

    return AsyncTaskResponse(
        task_id=task.id,
        status="queued",
        message="Task queued successfully",
    )


@router.get("/export/{file_id}")
async def download_results(
    file_id: str,
    format: str = Query("csv", description="导出格式 (csv/excel/json)"),
    current_user: User = Depends(get_current_user_required),
):
    """下载分析结果文件"""
    # 这里应该从数据库或存储中获取结果
    # 简化版本：返回一个占位符
    raise HTTPException(
        status_code=501,
        detail="File download not implemented yet. Use export API instead.",
    )
