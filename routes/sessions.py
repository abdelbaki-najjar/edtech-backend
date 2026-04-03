# routes/sessions.py
# ── حفظ جلسات اللعب ────────────────────────────────────────────

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import uuid

from core.database import get_db
from core.auth import get_current_user
from models.session import Session as GameSession
from models.student import Student
from sqlalchemy import select

router = APIRouter()


class SaveSessionRequest(BaseModel):
    subject: str
    lesson: str
    game_type: str
    difficulty: str
    score: int
    total: int
    duration_seconds: Optional[int] = 0


@router.post("/save")
async def save_session(
    req: SaveSessionRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """💾 يحفظ نتيجة اللعبة ويحدّث XP الطالب"""
    percentage = round((req.score / req.total) * 100, 1)
    xp_earned  = round(percentage)  # XP = النسبة المئوية

    # إنشاء الجلسة
    session = GameSession(
        student_id=uuid.UUID(user["id"]),
        subject=req.subject,
        lesson=req.lesson,
        game_type=req.game_type,
        difficulty=req.difficulty,
        score=req.score,
        total=req.total,
        percentage=percentage,
        xp_earned=xp_earned,
        duration_seconds=req.duration_seconds,
    )
    db.add(session)

    # تحديث بيانات الطالب
    result = await db.execute(select(Student).where(Student.id == uuid.UUID(user["id"])))
    student = result.scalar_one_or_none()
    if student:
        student.total_xp       += xp_earned
        student.total_sessions += 1
        # إعادة حساب المعدل
        all_sessions_result = await db.execute(
            select(GameSession).where(GameSession.student_id == student.id)
        )
        all_sessions = all_sessions_result.scalars().all()
        if all_sessions:
            student.avg_score = round(
                sum(s.percentage for s in all_sessions) / len(all_sessions)
            )

    await db.commit()
    return {
        "success": True,
        "xp_earned": xp_earned,
        "percentage": percentage,
        "message": "تم حفظ الجلسة ✅",
    }
