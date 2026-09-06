"""就业指导相关模型（3 张表）。"""
from sqlalchemy import BigInteger, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, IDMixin, TimestampMixin


class GuidanceChat(IDMixin, TimestampMixin, Base):
    __tablename__ = "guidance_chats"
    __table_args__ = {"comment": "就业指导会话表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    chat_type: Mapped[str] = mapped_column(String(20), comment="类型：companion / other")
    status: Mapped[str] = mapped_column(String(20), default="ongoing", comment="状态：ongoing / finished")


class GuidanceMessage(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "guidance_messages"
    __table_args__ = {"comment": "陪伴/指导消息表"}

    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="会话ID")
    role: Mapped[str] = mapped_column(String(10), comment="角色：ai / user")
    content: Mapped[str | None] = mapped_column(Text, comment="内容")


class GuidanceContent(IDMixin, TimestampMixin, Base):
    __tablename__ = "guidance_contents"
    __table_args__ = {"comment": "就业指导内容表"}

    title: Mapped[str] = mapped_column(String(255), comment="标题")
    content_type: Mapped[str] = mapped_column(String(20), comment="类型：article / music / video")
    category: Mapped[str] = mapped_column(String(20), comment="分类：psychology / positive / skill")
    cover_url: Mapped[str | None] = mapped_column(String(255), comment="封面图URL")
    content_url: Mapped[str | None] = mapped_column(String(255), comment="内容地址")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="上架状态：0下架 1上架")
