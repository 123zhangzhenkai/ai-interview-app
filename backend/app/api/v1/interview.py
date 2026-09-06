"""模拟面试接口（骨架：会话创建/列表/详情，Dify 编排在 services 层接入）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.crud.base import CRUDBase
from app.models.interview import Interview
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.interview import InterviewCreate, InterviewRead

router = APIRouter()
interview_crud = CRUDBase(Interview)


@router.get("", response_model=ResponseModel[list[InterviewRead]], summary="面试列表")
async def list_interviews(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    items = await interview_crud.get_multi(db, skip=0, limit=50)
    return ResponseModel(data=items)


@router.post("", response_model=ResponseModel[InterviewRead], summary="创建面试会话")
async def create_interview(
    payload: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    interview = await interview_crud.create(db, obj_in={"user_id": user.id, **payload.model_dump()})
    return ResponseModel(data=interview)


@router.get("/{interview_id}", response_model=ResponseModel[InterviewRead], summary="面试详情")
async def get_interview(
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    interview = await interview_crud.get(db, interview_id)
    return ResponseModel(data=interview)
