"""数据库 ORM 模型定义"""
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PredictionHistory(Base):
    """预测历史记录表"""

    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    input_text: Mapped[str] = mapped_column(Text, nullable=False, comment="输入文本")
    label: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="预测标签（正/负面情绪）"
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, comment="置信度分数 (0~1)")
    source_ip: Mapped[str | None] = mapped_column(
        String(45), nullable=True, comment="请求来源 IP"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="客户端 User-Agent"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="记录创建时间",
    )

    __table_args__ = (
        # 按创建时间降序的索引，加速历史查询
        Index("ix_prediction_history_created_at", created_at.desc()),
        # 按标签过滤的索引
        Index("ix_prediction_history_label", label),
        # 按置信度范围查询的索引
        Index("ix_prediction_history_score", score),
    )

    def __repr__(self) -> str:
        return (
            f"<PredictionHistory(id={self.id}, label='{self.label}', "
            f"score={self.score:.4f}, created_at={self.created_at})>"
        )