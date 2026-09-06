"""商业化与后期规划模型（会员/订单/真人面试/问答墙，共 6 张表）。"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Numeric, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, IDMixin, TimestampMixin


class Membership(IDMixin, TimestampMixin, Base):
    __tablename__ = "memberships"
    __table_args__ = {"comment": "会员表"}

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, comment="用户ID")
    plan_type: Mapped[str] = mapped_column(String(20), comment="套餐：free / vip")
    start_date: Mapped[datetime | None] = mapped_column(DateTime, comment="生效时间")
    end_date: Mapped[datetime | None] = mapped_column(DateTime, comment="到期时间")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态：0失效 1生效")


class Order(IDMixin, TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = {"comment": "订单表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    order_no: Mapped[str] = mapped_column(String(64), unique=True, comment="订单号")
    plan_type: Mapped[str] = mapped_column(String(20), comment="套餐类型")
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), comment="金额（元）")
    pay_status: Mapped[int] = mapped_column(SmallInteger, default=0, comment="支付状态：0待支付 1已支付 2已取消")
    pay_channel: Mapped[str | None] = mapped_column(String(20), comment="支付渠道：wechat / alipay")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, comment="支付时间")


class RealInterview(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "real_interviews"
    __table_args__ = {"comment": "真人模拟面试预约表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    interviewer_id: Mapped[int | None] = mapped_column(BigInteger, comment="真人面试官ID")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, comment="预约时间")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="状态：pending / confirmed / cancelled / finished")


class WallQuestion(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "wall_questions"
    __table_args__ = {"comment": "真人问答墙问题表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="提问用户ID")
    title: Mapped[str] = mapped_column(String(255), comment="问题标题")
    content: Mapped[str | None] = mapped_column(Text, comment="问题详情")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="浏览数")


class WallAnswer(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "wall_answers"
    __table_args__ = {"comment": "真人问答墙回答表"}

    question_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="问题ID")
    answerer_id: Mapped[int | None] = mapped_column(BigInteger, comment="回答者ID")
    content: Mapped[str | None] = mapped_column(Text, comment="回答内容")
