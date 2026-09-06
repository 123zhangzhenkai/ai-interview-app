"""模拟面试相关 schema。"""
from pydantic import BaseModel

from app.schemas.common import ORMModel


class InterviewCreate(BaseModel):
    interview_mode: str = "one_to_one"
    target_position: str | None = None
    interview_round: str | None = None
    interview_style: str | None = None


class InterviewRead(InterviewCreate, ORMModel):
    id: int
    user_id: int
    status: str
    total_questions: int
    current_question: int
