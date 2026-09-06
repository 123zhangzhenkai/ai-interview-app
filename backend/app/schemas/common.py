"""通用响应模型与分页结构。"""
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应结构：code == 0 表示成功，code != 0 表示业务异常。"""

    code: int = 0
    message: str = "ok"
    data: T | None = None


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ORMModel(BaseModel):
    """ORM 模型的 Pydantic 基类，支持从 SQLAlchemy 对象直接序列化。"""

    model_config = ConfigDict(from_attributes=True)
