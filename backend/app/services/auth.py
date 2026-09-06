"""认证业务逻辑。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError
from app.core.security import hash_password, verify_password
from app.crud.user import user_crud
from app.models.user import User


async def register_user(db: AsyncSession, *, phone: str, password: str) -> User:
    """注册新用户：校验手机号唯一后创建。"""
    existing = await user_crud.get_by_phone(db, phone=phone)
    if existing is not None:
        raise BusinessError(code=10001, message="该手机号已注册")
    return await user_crud.create(db, obj_in={"phone": phone, "password_hash": hash_password(password)})


async def authenticate_user(db: AsyncSession, *, phone: str, password: str) -> User:
    """校验手机号与密码，返回用户或抛业务异常。"""
    user = await user_crud.get_by_phone(db, phone=phone)
    if user is None or not user.password_hash or not verify_password(password, user.password_hash):
        raise BusinessError(code=10002, message="手机号或密码错误")
    return user
