"""FastAPI 应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

app = FastAPI(title=settings.PROJECT_NAME)

# MVP 阶段放开跨域，生产环境需收紧为白名单
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["健康检查"])
async def health() -> dict:
    return {"code": 0, "message": "ok", "data": {"status": "healthy"}}
