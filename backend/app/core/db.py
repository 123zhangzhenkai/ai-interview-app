"""数据库引擎与会话：异步 SQLAlchemy + aiomysql 驱动。"""
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "dev",
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：请求级数据库会话，请求结束自动关闭。"""
    async with AsyncSessionLocal() as session:
        yield session
