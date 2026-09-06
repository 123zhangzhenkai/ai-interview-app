"""认证相关 schema。"""
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1\d{10}$", description="手机号")
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    code: str = Field(..., description="短信验证码")


class LoginRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
