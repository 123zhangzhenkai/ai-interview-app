"""求职档案接口。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.crud.profile import profile_crud
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter()


@router.get("/me", response_model=ResponseModel[ProfileRead | None], summary="获取当前用户档案")
async def get_my_profile(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    profile = await profile_crud.get_by_user_id(db, user_id=user.id)
    return ResponseModel(data=profile)


@router.put("/me", response_model=ResponseModel[ProfileRead], summary="创建或更新当前用户档案")
async def update_my_profile(
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)
    profile = await profile_crud.get_by_user_id(db, user_id=user.id)
    if profile is None:
        profile = await profile_crud.create(db, obj_in={"user_id": user.id, **data})
    else:
        profile = await profile_crud.update(db, db_obj=profile, obj_in=data)
    return ResponseModel(data=profile)
