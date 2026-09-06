"""求职档案数据访问。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.profile import Profile


class CRUDProfile(CRUDBase[Profile]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Profile | None:
        result = await db.execute(select(Profile).where(Profile.user_id == user_id))
        return result.scalar_one_or_none()


profile_crud = CRUDProfile(Profile)
