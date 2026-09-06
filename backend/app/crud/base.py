"""通用 CRUD：只做数据库读写，不含业务逻辑。"""
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        return await db.get(self.model, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ModelType:
        obj = self.model(**obj_in)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType | None:
        obj = await self.get(db, id)
        if obj is not None:
            await db.delete(obj)
            await db.commit()
        return obj
