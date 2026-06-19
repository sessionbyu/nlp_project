"""预测历史记录查询 API"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_async_session
from ...services.history import get_recent_history, get_stats, query_history

router = APIRouter()


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    records: list[dict]


class StatsResponse(BaseModel):
    total_predictions: int
    label_distribution: dict[str, int]
    average_score: float


class RecentResponse(BaseModel):
    records: list[dict]


@router.get("/history", response_model=PaginatedResponse)
async def list_history(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数 (1~100)"),
    label: Optional[str] = Query(None, description="按标签过滤"),
    min_score: Optional[float] = Query(None, ge=0, le=1, description="最低置信度"),
    max_score: Optional[float] = Query(None, ge=0, le=1, description="最高置信度"),
    keyword: Optional[str] = Query(None, description="输入文本关键词（模糊搜索）"),
    start_date: Optional[datetime] = Query(None, description="开始时间 (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="结束时间 (ISO 8601)"),
    session: AsyncSession = Depends(get_async_session),
):
    """分页查询预测历史记录，支持多条件过滤"""
    return await query_history(
        session=session,
        page=page,
        page_size=page_size,
        label=label,
        min_score=min_score,
        max_score=max_score,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/history/recent", response_model=RecentResponse)
async def recent_history(
    limit: int = Query(10, ge=1, le=100, description="返回最近 N 条记录"),
    session: AsyncSession = Depends(get_async_session),
):
    """获取最近 N 条预测记录"""
    records = await get_recent_history(session=session, limit=limit)
    return {"records": records}


@router.get("/history/stats", response_model=StatsResponse)
async def history_stats(
    session: AsyncSession = Depends(get_async_session),
):
    """获取预测历史统计信息"""
    return await get_stats(session=session)