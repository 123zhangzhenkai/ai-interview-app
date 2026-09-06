"""就业指导接口（骨架：陪伴会话创建/列表）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.crud.base import CRUDBase
from app.models.guidance import GuidanceChat
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.guidance import GuidanceChatCreate, GuidanceChatRead

router = APIRouter()
chat_crud = CRUDBase(GuidanceChat)


@router.get("/chats", response_model=ResponseModel[list[GuidanceChatRead]], summary="会话列表")
async def list_chats(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    items = await chat_crud.get_multi(db, skip=0, limit=50)
    return ResponseModel(data=items)


@router.post("/chats", response_model=ResponseModel[GuidanceChatRead], summary="创建陪伴会话")
async def create_chat(
    payload: GuidanceChatCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await chat_crud.create(db, obj_in={"user_id": user.id, **payload.model_dump()})
    return ResponseModel(data=chat)
