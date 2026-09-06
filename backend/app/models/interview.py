"""模拟面试相关模型（4 张表）。"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, IDMixin, TimestampMixin


class Interview(IDMixin, TimestampMixin, Base):
    __tablename__ = "interviews"
    __table_args__ = {"comment": "面试会话表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    interview_mode: Mapped[str] = mapped_column(String(20), comment="模式：one_to_one / group")
    target_position: Mapped[str | None] = mapped_column(String(100), comment="面试岗位")
    interview_round: Mapped[str | None] = mapped_column(String(20), comment="轮次：hr / tech / final")
    interview_style: Mapped[str | None] = mapped_column(String(20), comment="风格：formal / casual")
    status: Mapped[str] = mapped_column(String(20), default="ongoing", comment="状态：ongoing / finished / cancelled")
    total_questions: Mapped[int] = mapped_column(Integer, default=0, comment="题目总数")
    current_question: Mapped[int] = mapped_column(Integer, default=0, comment="当前题号")
    total_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), comment="总分")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, comment="开始时间")
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, comment="结束时间")


class InterviewMessage(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "interview_messages"
    __table_args__ = {"comment": "面试对话记录表"}

    interview_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="面试ID")
    role: Mapped[str] = mapped_column(String(10), comment="角色：ai / user")
    interviewer_name: Mapped[str | None] = mapped_column(String(50), comment="面试官标识（群面：A/B/C）")
    question_index: Mapped[int | None] = mapped_column(Integer, comment="所属题号")
    message_type: Mapped[str | None] = mapped_column(String(20), comment="类型：question / answer / followup / score")
    content: Mapped[str | None] = mapped_column(Text, comment="内容")
    asr_text: Mapped[str | None] = mapped_column(Text, comment="语音转文字原文")


class InterviewFeedback(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "interview_feedbacks"
    __table_args__ = {"comment": "面试逐题点评表"}

    interview_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="面试ID")
    question_index: Mapped[int] = mapped_column(Integer, comment="题号")
    question_text: Mapped[str | None] = mapped_column(Text, comment="题目内容")
    user_answer_summary: Mapped[str | None] = mapped_column(Text, comment="用户回答摘要")
    total_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="本题总分")
    content_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="内容质量分")
    logic_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="逻辑结构分")
    expression_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="表达沟通分")
    professional_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="专业匹配分")
    highlights: Mapped[str | None] = mapped_column(Text, comment="亮点")
    issues: Mapped[str | None] = mapped_column(Text, comment="主要问题")
    suggestions: Mapped[str | None] = mapped_column(Text, comment="改进建议")
    sample_answer: Mapped[str | None] = mapped_column(Text, comment="示范回答")


class InterviewReport(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "interview_reports"
    __table_args__ = {"comment": "面试报告表"}

    interview_id: Mapped[int] = mapped_column(BigInteger, unique=True, comment="面试ID")
    total_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), comment="总分")
    overall_comment: Mapped[str | None] = mapped_column(Text, comment="整体评价")
    core_suggestions: Mapped[str | None] = mapped_column(Text, comment="3条核心改进建议")
    next_practice_suggestions: Mapped[str | None] = mapped_column(Text, comment="下次练习建议")
