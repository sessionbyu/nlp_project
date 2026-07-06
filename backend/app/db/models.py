"""
用户角色与权限模型

功能：
1. 角色权限管理 (RBAC)
2. 用户与 PredictionHistory 关联
3. 软删除支持
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True, comment="邮箱")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="哈希密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像URL")

    # 角色与状态
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", comment="角色: admin/user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否激活")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="是否已验证邮箱")

    # 软删除
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="软删除标记")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="删除时间")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="最后登录时间")

    # 关系
    predictions: Mapped[list["PredictionHistory"]] = relationship(
        "PredictionHistory", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class APIKey(Base):
    """API 密钥表（用于第三方调用认证）"""
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True, comment="关联用户ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="密钥名称")
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True, comment="密钥哈希")
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False, comment="密钥前缀（用于识别）")

    # 权限与限制
    permissions: Mapped[str] = mapped_column(String(500), nullable=False, default="predict,history", comment="权限列表（逗号分隔）")
    rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=100, comment="每小时请求限制")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否启用")

    # 使用统计
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="最后使用时间")
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="累计使用次数")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间"
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="过期时间")

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name='{self.name}', key_prefix='{self.key_prefix}')>"


class PredictionHistory(Base):
    """预测历史记录表（更新版，关联用户）"""
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True, comment="关联用户ID（未登录用户为NULL）")
    input_text: Mapped[str] = mapped_column(Text, nullable=False, comment="输入文本")
    label: Mapped[str] = mapped_column(String(50), nullable=False, comment="预测标签")
    score: Mapped[float] = mapped_column(Float, nullable=False, comment="置信度分数 (0~1)")
    model_key: Mapped[str] = mapped_column(String(50), nullable=False, default="bert", comment="使用的模型")
    source_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, comment="请求来源 IP")
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="客户端 User-Agent")

    # 软删除
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="软删除标记")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="删除时间")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="记录创建时间"
    )

    # 关系
    user: Mapped[Optional["User"]] = relationship("User", back_populates="predictions")

    __table_args__ = (
        Index("ix_prediction_history_user_created", user_id, created_at.desc()),
        Index("ix_prediction_history_label", label),
        Index("ix_prediction_history_score", score),
    )

    def __repr__(self) -> str:
        return (
            f"<PredictionHistory(id={self.id}, user_id={self.user_id}, "
            f"label='{self.label}', score={self.score:.4f})>"
        )
