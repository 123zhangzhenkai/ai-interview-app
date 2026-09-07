"""求职信息登记接口（复用现有 profile 系列表，整份档案读写）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.crud import job_profile as job_profile_crud
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.job_profile import (
    CertificateRead,
    EducationRead,
    ExtraRead,
    JobProfileRead,
    JobProfileUpsert,
    PreferenceRead,
    ProfileRead,
    SkillRead,
    WorkRead,
)

router = APIRouter()


@router.get("", response_model=ResponseModel[JobProfileRead], summary="获取当前用户求职档案（整份）")
async def get_job_profile(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    full = await job_profile_crud.get_full(db, user_id=user.id)
    return ResponseModel(
        data=JobProfileRead(
            profile=ProfileRead.model_validate(full["profile"]) if full["profile"] else None,
            educations=[EducationRead.model_validate(e) for e in full["educations"]],
            work_experiences=[WorkRead.model_validate(w) for w in full["work_experiences"]],
            skills=[SkillRead.model_validate(s) for s in full["skills"]],
            certificates=[CertificateRead.model_validate(c) for c in full["certificates"]],
            preferences=PreferenceRead.model_validate(full["preferences"]) if full["preferences"] else None,
            extras=ExtraRead.model_validate(full["extras"]) if full["extras"] else None,
        )
    )


@router.put("", response_model=ResponseModel[dict], summary="保存更新当前用户求职档案（整份）")
async def save_job_profile(
    payload: JobProfileUpsert,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = payload.model_dump()
    await job_profile_crud.save_full(db, user_id=user.id, data=data)
    return ResponseModel(data={"user_id": user.id})
