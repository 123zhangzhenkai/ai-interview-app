"""简历优化相关模型（3 张表）。"""
from decimal import Decimal

from sqlalchemy import BigInteger, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, IDMixin, TimestampMixin


class Resume(IDMixin, TimestampMixin, Base):
    __tablename__ = "resumes"
    __table_args__ = {"comment": "简历表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    file_name: Mapped[str] = mapped_column(String(255), comment="文件名")
    file_url: Mapped[str | None] = mapped_column(String(255), comment="对象存储URL")
    file_type: Mapped[str | None] = mapped_column(String(10), comment="类型：pdf / word")
    file_size: Mapped[int | None] = mapped_column(BigInteger, comment="文件大小（字节）")
    upload_status: Mapped[str] = mapped_column(String(20), default="uploaded", comment="上传状态：uploading / uploaded / failed")
    parse_status: Mapped[str] = mapped_column(String(20), default="pending", comment="解析状态：pending / parsing / done / failed")


class ResumeAnalysis(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "resume_analyses"
    __table_args__ = {"comment": "简历分析结果表"}

    resume_id: Mapped[int] = mapped_column(BigInteger, unique=True, comment="简历ID")
    total_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="综合评分")
    layout_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="排版分")
    expression_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="表达分")
    highlight_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="亮点分")
    match_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), comment="匹配度分")
    optimized_content: Mapped[str | None] = mapped_column(Text, comment="优化版简历内容")


class ResumeSuggestion(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "resume_suggestions"
    __table_args__ = {"comment": "简历优化建议表"}

    analysis_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="分析ID")
    category: Mapped[str] = mapped_column(String(20), comment="分类：layout / expression / highlight / match")
    title: Mapped[str | None] = mapped_column(String(255), comment="建议标题")
    description: Mapped[str | None] = mapped_column(Text, comment="建议内容")
