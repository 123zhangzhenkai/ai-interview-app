"""安全工具：密码哈希（argon2）与 JWT 签发/校验。"""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    """对明文密码做哈希，禁止存明文。"""
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def _create_token(subject: str | Any, token_type: str, expires_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {"sub": str(subject), "type": token_type, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str | Any) -> str:
    return _create_token(subject, "access", settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(subject: str | Any) -> str:
    return _create_token(subject, "refresh", settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token: str) -> dict[str, Any]:
    """解码 JWT，失败抛异常由调用方处理。"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
