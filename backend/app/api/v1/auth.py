"""认证接口：注册、登录、刷新令牌。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.exceptions import BusinessError
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.common import ResponseModel
from app.services import auth as auth_service

router = APIRouter()


def _token_response(user_id: int) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/register", response_model=ResponseModel[TokenResponse], summary="注册")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """手机号注册（短信验证码校验待短信服务接入后补充）。"""
    user = await auth_service.register_user(db, phone=payload.phone, password=payload.password)
    return ResponseModel(data=_token_response(user.id))


@router.post("/login", response_model=ResponseModel[TokenResponse], summary="登录")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, phone=payload.phone, password=payload.password)
    return ResponseModel(data=_token_response(user.id))


@router.post("/refresh", response_model=ResponseModel[TokenResponse], summary="刷新令牌")
async def refresh(payload: RefreshRequest):
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise BusinessError(code=10003, message="刷新令牌无效或已过期")
    if data.get("type") != "refresh":
        raise BusinessError(code=10003, message="令牌类型错误")
    subject = data.get("sub")
    if subject is None:
        raise BusinessError(code=10003, message="刷新令牌无效")
    return ResponseModel(data=_token_response(int(subject)))
