"""模型统一入口：导入所有模型，确保 Base.metadata 完整，供 Alembic autogenerate 使用。"""
from app.models.base import Base
from app.models.biz import Membership, Order, RealInterview, WallAnswer, WallQuestion
from app.models.guidance import GuidanceChat, GuidanceContent, GuidanceMessage
from app.models.interview import Interview, InterviewFeedback, InterviewMessage, InterviewReport
from app.models.profile import (
    Education,
    JobPreference,
    Profile,
    ProfileExtra,
    SelfIntroduction,
    UserCertificate,
    UserSkill,
    WorkExperience,
)
from app.models.resume import Resume, ResumeAnalysis, ResumeSuggestion
from app.models.user import ThirdPartyAccount, User, VerificationCode

__all__ = [
    "Base",
    "User",
    "ThirdPartyAccount",
    "VerificationCode",
    "Profile",
    "Education",
    "WorkExperience",
    "UserSkill",
    "UserCertificate",
    "JobPreference",
    "ProfileExtra",
    "SelfIntroduction",
    "Interview",
    "InterviewMessage",
    "InterviewFeedback",
    "InterviewReport",
    "Resume",
    "ResumeAnalysis",
    "ResumeSuggestion",
    "GuidanceChat",
    "GuidanceMessage",
    "GuidanceContent",
    "Membership",
    "Order",
    "RealInterview",
    "WallQuestion",
    "WallAnswer",
]
