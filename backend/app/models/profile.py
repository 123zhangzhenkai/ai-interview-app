"""求职档案相关模型（8 张表）。"""
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, Integer, Numeric, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, IDMixin, TimestampMixin


class Profile(IDMixin, TimestampMixin, Base):
    __tablename__ = "profiles"
    __table_args__ = {"comment": "基础个人信息表"}

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, comment="用户ID")
    real_name: Mapped[str | None] = mapped_column(String(50), comment="姓名")
    gender: Mapped[int | None] = mapped_column(SmallInteger, comment="性别：0未知 1男 2女")
    age: Mapped[int | None] = mapped_column(SmallInteger, comment="年龄")
    phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")
    email: Mapped[str | None] = mapped_column(String(100), comment="常用邮箱")
    target_position: Mapped[str | None] = mapped_column(String(100), comment="意向岗位")
    target_city: Mapped[str | None] = mapped_column(String(50), comment="期望工作城市")
    expected_salary_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), comment="期望薪资下限")
    expected_salary_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), comment="期望薪资上限")
    available_date: Mapped[str | None] = mapped_column(String(50), comment="可到岗时间")
    job_seeker_type: Mapped[str | None] = mapped_column(
        String(20), comment="求职身份：fresh / graduate / career_change / employed"
    )


class Education(IDMixin, TimestampMixin, Base):
    __tablename__ = "educations"
    __table_args__ = {"comment": "教育经历表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    degree: Mapped[str | None] = mapped_column(String(20), comment="最高学历")
    school: Mapped[str | None] = mapped_column(String(100), comment="毕业院校")
    major: Mapped[str | None] = mapped_column(String(100), comment="专业")
    start_date: Mapped[date | None] = mapped_column(Date, comment="入学时间")
    end_date: Mapped[date | None] = mapped_column(Date, comment="毕业时间")
    main_courses: Mapped[str | None] = mapped_column(Text, comment="主修核心课程")
    honors: Mapped[str | None] = mapped_column(Text, comment="荣誉/奖学金")
    gpa: Mapped[str | None] = mapped_column(String(20), comment="学业成绩")
    campus_projects: Mapped[str | None] = mapped_column(Text, comment="校园项目/竞赛/社团")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")


class WorkExperience(IDMixin, TimestampMixin, Base):
    __tablename__ = "work_experiences"
    __table_args__ = {"comment": "实习/工作经历表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    company_name: Mapped[str | None] = mapped_column(String(100), comment="公司名称")
    position: Mapped[str | None] = mapped_column(String(100), comment="岗位名称")
    start_date: Mapped[date | None] = mapped_column(Date, comment="入职时间")
    end_date: Mapped[date | None] = mapped_column(Date, comment="离职时间")
    job_content: Mapped[str | None] = mapped_column(Text, comment="工作内容")
    responsible_area: Mapped[str | None] = mapped_column(Text, comment="负责板块")
    skills: Mapped[str | None] = mapped_column(Text, comment="实操技能")
    tools: Mapped[str | None] = mapped_column(Text, comment="常用工具")
    achievements: Mapped[str | None] = mapped_column(Text, comment="工作成果/业绩/项目案例")
    leave_reason: Mapped[str | None] = mapped_column(Text, comment="离职原因（选填，供AI追问）")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")


class UserSkill(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "user_skills"
    __table_args__ = {"comment": "技能表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    skill_name: Mapped[str] = mapped_column(String(50), comment="技能名称")
    skill_type: Mapped[str] = mapped_column(String(20), comment="类型：professional / office / language")
    level: Mapped[str | None] = mapped_column(String(20), comment="熟练程度")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")


class UserCertificate(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "user_certificates"
    __table_args__ = {"comment": "证书表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    cert_name: Mapped[str] = mapped_column(String(100), comment="证书名称")
    cert_type: Mapped[str | None] = mapped_column(String(20), comment="类型：vocational / english / computer")
    issue_date: Mapped[date | None] = mapped_column(Date, comment="获取时间")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")


class JobPreference(IDMixin, TimestampMixin, Base):
    __tablename__ = "job_preferences"
    __table_args__ = {"comment": "求职偏好表"}

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, comment="用户ID")
    target_industry: Mapped[str | None] = mapped_column(String(100), comment="意向行业")
    company_type: Mapped[str | None] = mapped_column(String(50), comment="企业类型")
    accept_overtime: Mapped[bool | None] = mapped_column(Boolean, comment="是否接受加班")
    accept_business_trip: Mapped[bool | None] = mapped_column(Boolean, comment="是否接受出差")
    accept_relocation: Mapped[bool | None] = mapped_column(Boolean, comment="是否接受异地工作")
    interview_round_pref: Mapped[str | None] = mapped_column(String(50), comment="面试轮次偏好：hr / tech / final")
    interview_style: Mapped[str | None] = mapped_column(String(20), comment="面试风格：formal / casual")


class ProfileExtra(IDMixin, TimestampMixin, Base):
    __tablename__ = "profile_extras"
    __table_args__ = {"comment": "补充信息表"}

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, comment="用户ID")
    self_assessment: Mapped[str | None] = mapped_column(Text, comment="个人优缺点自评")
    career_plan: Mapped[str | None] = mapped_column(Text, comment="职业规划与发展方向")
    hobbies: Mapped[str | None] = mapped_column(Text, comment="兴趣爱好")
    specialties: Mapped[str | None] = mapped_column(Text, comment="个人特长")


class SelfIntroduction(IDMixin, TimestampMixin, Base):
    __tablename__ = "self_introductions"
    __table_args__ = {"comment": "智能自我介绍表"}

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    duration_type: Mapped[str] = mapped_column(String(20), comment="时长：1min / 3min")
    scenario: Mapped[str] = mapped_column(String(20), comment="场景：campus / social / career_change / english")
    content: Mapped[str | None] = mapped_column(Text, comment="自我介绍内容")
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否AI生成：0否 1是")
