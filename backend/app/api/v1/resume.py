"""简历优化接口（骨架：上传记录创建/列表，解析走 Dify 工作流）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.crud.base import CRUDBase
from app.models.resume import Resume
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.resume import ResumeCreate, ResumeRead

router = APIRouter()
resume_crud = CRUDBase(Resume)


@router.get("", response_model=ResponseModel[list[ResumeRead]], summary="简历列表")
async def list_resumes(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    items = await resume_crud.get_multi(db, skip=0, limit=50)
    return ResponseModel(data=items)


@router.post("", response_model=ResponseModel[ResumeRead], summary="创建简历记录")
async def create_resume(
    payload: ResumeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    resume = await resume_crud.create(db, obj_in={"user_id": user.id, **payload.model_dump()})
    return ResponseModel(data=resume)
