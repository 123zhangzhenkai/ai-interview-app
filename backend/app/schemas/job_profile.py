"""求职信息登记（求职档案）聚合 schema。

复用现有 profile 系列表：profiles / educations / work_experiences /
user_skills / user_certificates / job_preferences / profile_extras。
一个用户一份档案，子表按 user_id 归属。
"""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.profile import ProfileRead, ProfileUpdate


# ---------- 教育经历 ----------
class EducationIn(BaseModel):
    degree: str | None = Field(None, max_length=20, description="最高学历")
    school: str | None = Field(None, max_length=100, description="毕业院校")
    major: str | None = Field(None, max_length=100, description="专业")
    start_date: date | None = Field(None, description="入学时间")
    end_date: date | None = Field(None, description="毕业时间")
    main_courses: str | None = Field(None, description="核心课程")
    honors: str | None = Field(None, description="在校荣誉/奖学金")
    gpa: str | None = Field(None, max_length=20, description="成绩")
    campus_projects: str | None = Field(None, description="校园项目/竞赛/社团任职")


class EducationRead(EducationIn, ORMModel):
    id: int


# ---------- 实习/工作经历 ----------
class WorkIn(BaseModel):
    company_name: str | None = Field(None, max_length=100, description="公司名称")
    position: str | None = Field(None, max_length=100, description="岗位")
    start_date: date | None = Field(None, description="开始时间")
    end_date: date | None = Field(None, description="结束时间")
    job_content: str | None = Field(None, description="工作内容")
    responsible_area: str | None = Field(None, description="负责板块")
    skills: str | None = Field(None, description="实操技能")
    tools: str | None = Field(None, description="常用工具")
    achievements: str | None = Field(None, description="工作成果/业绩案例")
    leave_reason: str | None = Field(None, description="离职原因（选填）")


class WorkRead(WorkIn, ORMModel):
    id: int


# ---------- 技能（professional/office/language） ----------
class SkillIn(BaseModel):
    skill_type: str = Field(..., description="类型：professional / office / language")
    skill_name: str = Field(..., max_length=50, description="技能名称")
    level: str | None = Field(None, max_length=20, description="熟练程度")


class SkillRead(SkillIn, ORMModel):
    id: int


# ---------- 证书（english/computer/vocational） ----------
class CertificateIn(BaseModel):
    cert_type: str = Field(..., description="类型：english / computer / vocational")
    cert_name: str = Field(..., max_length=100, description="证书名称")
    issue_date: date | None = Field(None, description="获取时间")


class CertificateRead(CertificateIn, ORMModel):
    id: int


# ---------- 求职偏好 ----------
class PreferenceIn(BaseModel):
    target_industry: str | None = Field(None, max_length=100, description="意向行业")
    company_type: str | None = Field(None, max_length=50, description="企业类型")
    accept_overtime: bool | None = Field(None, description="是否接受加班")
    accept_business_trip: bool | None = Field(None, description="是否接受出差")
    accept_relocation: bool | None = Field(None, description="是否接受异地工作")
    interview_round_pref: str | None = Field(None, max_length=50, description="面试轮次偏好：hr / tech / final")
    interview_style: str | None = Field(None, max_length=20, description="面试风格：formal / casual")


class PreferenceRead(PreferenceIn, ORMModel):
    id: int


# ---------- 求职补充信息 ----------
class ExtraIn(BaseModel):
    self_assessment: str | None = Field(None, description="个人优缺点自评")
    career_plan: str | None = Field(None, description="职业规划")
    hobbies: str | None = Field(None, description="兴趣特长")


class ExtraRead(ExtraIn, ORMModel):
    id: int


# ---------- 聚合 ----------
class JobProfileUpsert(BaseModel):
    """整份档案保存入参（子表全量替换）。"""

    profile: ProfileUpdate | None = None
    educations: list[EducationIn] = []
    work_experiences: list[WorkIn] = []
    skills: list[SkillIn] = []
    certificates: list[CertificateIn] = []
    preferences: PreferenceIn | None = None
    extras: ExtraIn | None = None


class JobProfileRead(BaseModel):
    """整份档案读取出参。"""

    profile: ProfileRead | None = None
    educations: list[EducationRead] = []
    work_experiences: list[WorkRead] = []
    skills: list[SkillRead] = []
    certificates: list[CertificateRead] = []
    preferences: PreferenceRead | None = None
    extras: ExtraRead | None = None
