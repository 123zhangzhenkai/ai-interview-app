"""求职档案相关 schema。"""
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class ProfileBase(BaseModel):
    real_name: str | None = None
    gender: int | None = None
    age: int | None = None
    phone: str | None = None
    email: str | None = None
    target_position: str | None = None
    target_city: str | None = None
    expected_salary_min: Decimal | None = None
    expected_salary_max: Decimal | None = None
    available_date: str | None = None
    job_seeker_type: str | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase, ORMModel):
    id: int
    user_id: int
