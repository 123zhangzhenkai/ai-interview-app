"""求职档案多表数据访问（复用现有 profile 系列表）。

保存策略：主档/偏好/补充按 user_id upsert；教育/工作/技能/证书为子表，
前端整份提交，后端对子表按 user_id 全量替换（先删后插），天然支持增删改。
"""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import (
    Education,
    JobPreference,
    Profile,
    ProfileExtra,
    UserCertificate,
    UserSkill,
    WorkExperience,
)


async def get_full(db: AsyncSession, *, user_id: int) -> dict:
    """读取某用户完整档案；无记录时返回各子表为空的结构。"""
    profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
    educations = (await db.execute(select(Education).where(Education.user_id == user_id).order_by(Education.sort_order))).scalars().all()
    works = (await db.execute(select(WorkExperience).where(WorkExperience.user_id == user_id).order_by(WorkExperience.sort_order))).scalars().all()
    skills = (await db.execute(select(UserSkill).where(UserSkill.user_id == user_id).order_by(UserSkill.sort_order))).scalars().all()
    certs = (await db.execute(select(UserCertificate).where(UserCertificate.user_id == user_id).order_by(UserCertificate.sort_order))).scalars().all()
    prefs = (await db.execute(select(JobPreference).where(JobPreference.user_id == user_id))).scalar_one_or_none()
    extras = (await db.execute(select(ProfileExtra).where(ProfileExtra.user_id == user_id))).scalar_one_or_none()

    return {
        "profile": profile,
        "educations": list(educations),
        "work_experiences": list(works),
        "skills": list(skills),
        "certificates": list(certs),
        "preferences": prefs,
        "extras": extras,
    }


async def _replace_children(db: AsyncSession, *, user_id: int, model, rows: list[dict]) -> None:
    """子表全量替换：删旧 + 插新，sort_order 按列表顺序。"""
    await db.execute(delete(model).where(model.user_id == user_id))
    for i, row in enumerate(rows):
        db.add(model(user_id=user_id, **row, sort_order=i))


async def save_full(db: AsyncSession, *, user_id: int, data: dict) -> None:
    """整份档案保存：一次性事务，子表先删后插。入参 data 已序列化为 dict。"""
    profile_in = data.get("profile") or {}
    if profile_in:
        profile = (await db.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
        if profile is None:
            db.add(Profile(user_id=user_id, **profile_in))
        else:
            for k, v in profile_in.items():
                setattr(profile, k, v)

    await _replace_children(db, user_id=user_id, model=Education, rows=data.get("educations") or [])
    await _replace_children(db, user_id=user_id, model=WorkExperience, rows=data.get("work_experiences") or [])
    await _replace_children(db, user_id=user_id, model=UserSkill, rows=data.get("skills") or [])
    await _replace_children(db, user_id=user_id, model=UserCertificate, rows=data.get("certificates") or [])

    prefs_in = data.get("preferences")
    if prefs_in:
        prefs = (await db.execute(select(JobPreference).where(JobPreference.user_id == user_id))).scalar_one_or_none()
        if prefs is None:
            db.add(JobPreference(user_id=user_id, **prefs_in))
        else:
            for k, v in prefs_in.items():
                setattr(prefs, k, v)

    extras_in = data.get("extras")
    if extras_in:
        extras = (await db.execute(select(ProfileExtra).where(ProfileExtra.user_id == user_id))).scalar_one_or_none()
        if extras is None:
            db.add(ProfileExtra(user_id=user_id, **extras_in))
        else:
            for k, v in extras_in.items():
                setattr(extras, k, v)

    await db.commit()
