"""用户数据访问。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase[User]):
    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> User | None:
        result = await db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()


user_crud = CRUDUser(User)
