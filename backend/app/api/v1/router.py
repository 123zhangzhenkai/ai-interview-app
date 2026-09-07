"""API v1 路由聚合。"""
from fastapi import APIRouter

from app.api.v1 import ai, auth, guidance, interview, job_profile, profile, resume

api_router = APIRouter()
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(profile.router, prefix="/profiles", tags=["求职档案"])
api_router.include_router(job_profile.router, prefix="/job-profile", tags=["求职档案"])
api_router.include_router(interview.router, prefix="/interviews", tags=["模拟面试"])
api_router.include_router(resume.router, prefix="/resumes", tags=["简历优化"])
api_router.include_router(guidance.router, prefix="/guidance", tags=["就业指导"])
