"""预测历史记录 CRUD 服务"""
from datetime import datetime
from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import PredictionHistory
from ..utils.logger import logger


async def save_prediction(
    session: AsyncSession,
    input_text: str,
    label: str,
    score: float,
    source_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> PredictionHistory:
    """保存一条预测记录到数据库"""
    record = PredictionHistory(
        input_text=input_text,
        label=label,
        score=score,
        source_ip=source_ip,
        user_agent=user_agent,
    )
    session.add(record)
    await session.flush()  # 刷新以获取自增 ID
    logger.info(f"Saved prediction history: id={record.id}, label='{label}'")
    return record


async def query_history(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    label: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """分页查询预测历史记录，支持多条件过滤"""
    base_query = select(PredictionHistory)
    count_query = select(func.count(PredictionHistory.id))

    # ---- 构建过滤条件 ----
    filters = []

    if label:
        filters.append(PredictionHistory.label == label)
    if min_score is not None:
        filters.append(PredictionHistory.score >= min_score)
    if max_score is not None:
        filters.append(PredictionHistory.score <= max_score)
    if keyword:
        filters.append(PredictionHistory.input_text.ilike(f"%{keyword}%"))
    if start_date:
        filters.append(PredictionHistory.created_at >= start_date)
    if end_date:
        filters.append(PredictionHistory.created_at <= end_date)

    for f in filters:
        base_query = base_query.where(f)
        count_query = count_query.where(f)

    # ---- 查询总数 ----
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # ---- 分页排序查询 ----
    offset = (page - 1) * page_size
    base_query = base_query.order_by(desc(PredictionHistory.created_at))
    base_query = base_query.offset(offset).limit(page_size)

    result = await session.execute(base_query)
    records = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max((total + page_size - 1) // page_size, 1),
        "records": [
            {
                "id": r.id,
                "input_text": r.input_text,
                "label": r.label,
                "score": r.score,
                "source_ip": r.source_ip,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
    }


async def get_recent_history(
    session: AsyncSession,
    limit: int = 10,
) -> list[dict]:
    """获取最近的 N 条预测记录"""
    query = (
        select(PredictionHistory)
        .order_by(desc(PredictionHistory.created_at))
        .limit(limit)
    )
    result = await session.execute(query)
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "input_text": r.input_text,
            "label": r.label,
            "score": r.score,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


async def get_stats(session: AsyncSession) -> dict:
    """获取预测统计信息"""
    # 总数
    total_result = await session.execute(select(func.count(PredictionHistory.id)))
    total = total_result.scalar() or 0

    # 按标签分组统计
    label_query = select(
        PredictionHistory.label, func.count(PredictionHistory.id)
    ).group_by(PredictionHistory.label)
    label_result = await session.execute(label_query)
    label_stats = {row[0]: row[1] for row in label_result.fetchall()}

    # 平均置信度
    avg_result = await session.execute(select(func.avg(PredictionHistory.score)))
    avg_score = avg_result.scalar()

    return {
        "total_predictions": total,
        "label_distribution": label_stats,
        "average_score": round(avg_score, 4) if avg_score else 0.0,
    }