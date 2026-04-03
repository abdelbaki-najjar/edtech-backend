# services/usage_service.py
# ── نظام حدود الاستخدام ────────────────────────────────────────

from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.student import Student
from models.session import Session as GameSession


# ── الخطط ─────────────────────────────────────────────────────
PLANS = {
    "free":     {"daily_limit": 3,  "label": "مجاني"},
    "premium":  {"daily_limit": 10, "label": "مميز"},
    "school":   {"daily_limit": 50, "label": "مدرسة"},
}


async def get_usage_today(student_id, db: AsyncSession) -> int:
    """كم لعبة ولّدها الطالب اليوم؟"""
    today = date.today()
    result = await db.execute(
        select(func.count(GameSession.id)).where(
            GameSession.student_id == student_id,
            func.date(GameSession.played_at) == today,
        )
    )
    return result.scalar() or 0


async def check_limit(student: Student, db: AsyncSession) -> dict:
    """
    يتحقق هل يمكن للطالب توليد لعبة جديدة.
    يرجع: { allowed, used, limit, plan }
    """
    plan      = student.plan or "free"
    limit     = PLANS.get(plan, PLANS["free"])["daily_limit"]
    used      = await get_usage_today(student.id, db)
    allowed   = used < limit

    return {
        "allowed":  allowed,
        "used":     used,
        "limit":    limit,
        "plan":     plan,
        "remaining": max(0, limit - used),
    }


async def upgrade_student(student_id: str, plan: str, db: AsyncSession) -> bool:
    """
    ترقية طالب يدوياً (تستخدمه أنت من الـ Admin endpoint)
    """
    from uuid import UUID
    result = await db.execute(
        select(Student).where(Student.id == UUID(student_id))
    )
    student = result.scalar_one_or_none()
    if not student:
        return False

    student.plan = plan
    await db.commit()
    return True
