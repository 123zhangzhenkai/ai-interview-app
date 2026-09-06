"""账号认证相关模型：用户、第三方绑定、验证码。"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, IDMixin, TimestampMixin


class User(IDMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户账号表"}

    phone: Mapped[str | None] = mapped_column(String(20), unique=True, comment="手机号（第三方登录可为空）")
    password_hash: Mapped[str | None] = mapped_column(String(255), comment="密码哈希（第三方登录为空）")
    nickname: Mapped[str | None] = mapped_column(String(50), comment="昵称")
    avatar_url: Mapped[str | None] = mapped_column(String(255), comment="头像URL")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="账号状态：0禁用 1正常")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, comment="最后登录时间")


class ThirdPartyAccount(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "third_party_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "open_id", name="uk_provider_open"),
        {"comment": "第三方登录绑定表"},
    )

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, comment="用户ID")
    provider: Mapped[str] = mapped_column(String(20), comment="平台：wechat / qq")
    open_id: Mapped[str] = mapped_column(String(128), comment="第三方OpenID")
    union_id: Mapped[str | None] = mapped_column(String(128), comment="微信UnionID")


class VerificationCode(IDMixin, CreatedAtMixin, Base):
    __tablename__ = "verification_codes"
    __table_args__ = {"comment": "短信验证码表"}

    phone: Mapped[str] = mapped_column(String(20), index=True, comment="手机号")
    code: Mapped[str] = mapped_column(String(10), comment="验证码")
    scene: Mapped[str] = mapped_column(String(20), comment="场景：login / register / reset_password")
    expires_at: Mapped[datetime] = mapped_column(DateTime, comment="过期时间")
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已使用：0否 1是")
