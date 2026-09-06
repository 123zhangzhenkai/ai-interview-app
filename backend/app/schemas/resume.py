"""简历优化相关 schema。"""
from pydantic import BaseModel

from app.schemas.common import ORMModel


class ResumeCreate(BaseModel):
    file_name: str
    file_url: str | None = None
    file_type: str | None = None
    file_size: int | None = None


class ResumeRead(ResumeCreate, ORMModel):
    id: int
    user_id: int
    upload_status: str
    parse_status: str
