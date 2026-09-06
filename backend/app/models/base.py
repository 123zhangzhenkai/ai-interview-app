"""ORM 基类与通用 Mixin。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""
    pass


class IDMixin:
    """主键：MySQL BIGINT 自增。"""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )


class TimestampMixin(CreatedAtMixin):
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
