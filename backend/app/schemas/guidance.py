"""就业指导相关 schema。"""
from pydantic import BaseModel

from app.schemas.common import ORMModel


class GuidanceChatCreate(BaseModel):
    chat_type: str = "companion"


class GuidanceChatRead(GuidanceChatCreate, ORMModel):
    id: int
    user_id: int
    status: str
