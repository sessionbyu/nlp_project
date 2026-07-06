"""
统计分析 API 路由

功能：
1. 预测统计
2. 趋势分析
3. 数据可视化
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import PredictionHistory, User
from ...db.session import get_async_session
from ...services.auth import get_current_user_required
from ...utils.logger import logger

router = APIRouter(prefix="/stats", tags=["Statistics"])


# ========== Pydantic Schemas ==========

class DailyStats(BaseModel):
    date: str
    total: int
    positive: int
    negative: int
    neutral: int


class TrendStats(BaseModel):
    period: str
    data: List[Dict[str, any]]


class LabelDistribution(BaseModel):
    positive: int
    negative: int
    neutral: int
    total: int


class ScoreDistribution(BaseModel):
    range: str
    count: int
    percentage: float


class UserStats(BaseModel):
    user_id: int
    username: str
    total_predictions: int
    avg_score: float
    label_distribution: Dict[str, int]


# ========== 统计接口 ==========

@router.get("/overview")
async def get_overview_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """获取概览统计"""
    user_id = current_user.id

    # 总预测数
    total_result = await session.execute(
        select(func.count(PredictionHistory.id)).where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
        )
    )
    total = total_result.scalar() or 0

    # 标签分布
    label_query = (
        select(PredictionHistory.label, func.count(PredictionHistory.id))
        .where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
        )
        .group_by(PredictionHistory.label)
    )
    label_result = await session.execute(label_query)
    label_distribution = {row[0]: row[1] for row in label_result.fetchall()}

    # 平均分数
    avg_result = await session.execute(
        select(func.avg(PredictionHistory.score)).where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
        )
    )
    avg_score = avg_result.scalar() or 0.0

    # 最近7天预测数
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_result = await session.execute(
        select(func.count(PredictionHistory.id)).where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
            PredictionHistory.created_at >= week_ago,
        )
    )
    recent_7d = week_result.scalar() or 0

    # 最近30天预测数
    month_ago = datetime.utcnow() - timedelta(days=30)
    month_result = await session.execute(
        select(func.count(PredictionHistory.id)).where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
            PredictionHistory.created_at >= month_ago,
        )
    )
    recent_30d = month_result.scalar() or 0

    return {
        "total_predictions": total,
        "recent_7d": recent_7d,
        "recent_30d": recent_30d,
        "label_distribution": label_distribution,
        "average_score": round(float(avg_score), 4),
    }


@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats(
    days: int = Query(7, ge=1, le=30, description="天数"),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """获取每日预测统计"""
    user_id = current_user.id
    start_date = datetime.utcnow() - timedelta(days=days)

    # 按日期分组统计
    query = (
        select(
            func.date(PredictionHistory.created_at).label("date"),
            PredictionHistory.label,
            func.count(PredictionHistory.id).label("count"),
        )
        .where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
            PredictionHistory.created_at >= start_date,
        )
        .group_by(func.date(PredictionHistory.created_at), PredictionHistory.label)
        .order_by(func.date(PredictionHistory.created_at))
    )

    result = await session.execute(query)
    rows = result.fetchall()

    # 组织数据
    stats_by_date: Dict[str, Dict[str, int]] = {}
    for date, label, count in rows:
        date_str = str(date)
        if date_str not in stats_by_date:
            stats_by_date[date_str] = {"positive": 0, "negative": 0, "neutral": 0}
        stats_by_date[date_str][label] = count

    # 转换为响应格式
    daily_stats = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
        stats = stats_by_date.get(date, {"positive": 0, "negative": 0, "neutral": 0})
        daily_stats.append(DailyStats(
            date=date,
            total=sum(stats.values()),
            positive=stats.get("positive", 0),
            negative=stats.get("negative", 0),
            neutral=stats.get("neutral", 0),
        ))

    return daily_stats


@router.get("/trends")
async def get_trend_stats(
    period: str = Query("daily", description="时间周期 (daily/weekly/monthly)"),
    limit: int = Query(30, ge=1, le=100, description="数据点数量"),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """获取趋势数据"""
    user_id = current_user.id

    # 根据周期确定开始日期
    if period == "daily":
        start_date = datetime.utcnow() - timedelta(days=limit)
        date_format = "YYYY-MM-DD"
        date_trunc = func.date_trunc("day", PredictionHistory.created_at)
    elif period == "weekly":
        start_date = datetime.utcnow() - timedelta(weeks=limit)
        date_format = "YYYY-WW"
        date_trunc = func.date_trunc("week", PredictionHistory.created_at)
    elif period == "monthly":
        start_date = datetime.utcnow() - timedelta(days=limit * 30)
        date_format = "YYYY-MM"
        date_trunc = func.date_trunc("month", PredictionHistory.created_at)
    else:
        raise HTTPException(status_code=400, detail="Invalid period")

    # 按时间和标签分组
    query = (
        select(
            date_trunc.label("period"),
            PredictionHistory.label,
            func.count(PredictionHistory.id).label("count"),
            func.avg(PredictionHistory.score).label("avg_score"),
        )
        .where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
            PredictionHistory.created_at >= start_date,
        )
        .group_by(date_trunc, PredictionHistory.label)
        .order_by(date_trunc)
    )

    result = await session.execute(query)
    rows = result.fetchall()

    # 组织数据
    trends: Dict[str, Dict[str, any]] = {}
    for period_dt, label, count, avg_score in rows:
        period_str = str(period_dt)[:10] if period == "daily" else str(period_dt)[:7]
        if period_str not in trends:
            trends[period_str] = {
                "period": period_str,
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "avg_score": 0.0,
                "scores": [],
            }
        trends[period_str]["total"] += count
        trends[period_str][label] = trends[period_str].get(label, 0) + count
        if avg_score:
            trends[period_str]["scores"].append(float(avg_score))

    # 计算平均分数
    for period_data in trends.values():
        if period_data["scores"]:
            period_data["avg_score"] = round(
                sum(period_data["scores"]) / len(period_data["scores"]), 4
            )
        del period_data["scores"]

    return {
        "period": period,
        "data": sorted(trends.values(), key=lambda x: x["period"]),
    }


@router.get("/label-distribution")
async def get_label_distribution(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """获取标签分布"""
    user_id = current_user.id

    query = (
        select(PredictionHistory.label, func.count(PredictionHistory.id))
        .where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
        )
        .group_by(PredictionHistory.label)
    )

    result = await session.execute(query)
    rows = result.fetchall()

    distribution = {row[0]: row[1] for row in rows}
    total = sum(distribution.values())

    # 计算百分比
    percentages = {}
    for label, count in distribution.items():
        percentages[label] = round(count / total * 100, 2) if total > 0 else 0

    return {
        "distribution": distribution,
        "percentages": percentages,
        "total": total,
    }


@router.get("/score-distribution")
async def get_score_distribution(
    bins: int = Query(10, ge=2, le=20, description="分桶数量"),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """获取分数分布"""
    user_id = current_user.id

    # 查询所有分数
    query = (
        select(PredictionHistory.score)
        .where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
        )
    )
    result = await session.execute(query)
    scores = [row[0] for row in result.fetchall()]

    if not scores:
        return {"bins": [], "total": 0}

    # 分桶统计
    min_score = 0.0
    max_score = 1.0
    bin_width = (max_score - min_score) / bins

    distribution = []
    for i in range(bins):
        lower = min_score + i * bin_width
        upper = lower + bin_width
        count = sum(1 for s in scores if lower <= s < upper)
        distribution.append({
            "range": f"{lower:.2f} - {upper:.2f}",
            "count": count,
            "percentage": round(count / len(scores) * 100, 2),
        })

    # 最后一个桶包含上限
    distribution[-1]["range"] = f"{min_score + (bins-1) * bin_width:.2f} - {max_score:.2f}"

    return {
        "bins": distribution,
        "total": len(scores),
    }


@router.get("/model-usage")
async def get_model_usage(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_required),
):
    """获取模型使用统计"""
    user_id = current_user.id

    query = (
        select(
            PredictionHistory.model_key,
            func.count(PredictionHistory.id).label("count"),
            func.avg(PredictionHistory.score).label("avg_score"),
        )
        .where(
            PredictionHistory.user_id == user_id,
            PredictionHistory.is_deleted == False,
        )
        .group_by(PredictionHistory.model_key)
    )

    result = await session.execute(query)
    rows = result.fetchall()

    usage = []
    for model_key, count, avg_score in rows:
        usage.append({
            "model_key": model_key,
            "count": count,
            "avg_score": round(float(avg_score), 4) if avg_score else 0.0,
        })

    return {"model_usage": usage}
