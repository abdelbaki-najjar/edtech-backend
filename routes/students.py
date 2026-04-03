# routes/students.py
# ── نقاط نهاية الطلاب ──────────────────────────────────────────

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional
import uuid

from core.database import get_db
from core.auth import get_current_user
from models.student import Student
from models.session import Session as GameSession
from services.ai_service import calc_adaptive_difficulty, calc_badges

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────
class StudentOut(BaseModel):
    id: str
    name: str
    avatar: str
    grade: int
    total_xp: int
    total_sessions: int
    avg_score: int
    badges: list[str]
    difficulty: str  # المستوى التكيّفي الحالي

    class Config:
        from_attributes = True


# ── GET /api/students/me ───────────────────────────────────────
@router.get("/me", response_model=StudentOut)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """يرجع بيانات الطالب الحالي مع المستوى التكيّفي"""
    result = await db.execute(select(Student).where(Student.id == uuid.UUID(user["id"])))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="الطالب غير موجود")

    # جلب آخر الجلسات لحساب الصعوبة
    sessions_result = await db.execute(
        select(GameSession)
        .where(GameSession.student_id == student.id)
        .order_by(GameSession.played_at.desc())
        .limit(5)
    )
    sessions = sessions_result.scalars().all()
    sessions_data = [{"percentage": s.percentage} for s in sessions]

    return StudentOut(
        id=str(student.id),
        name=student.name,
        avatar=student.avatar,
        grade=student.grade,
        total_xp=student.total_xp,
        total_sessions=student.total_sessions,
        avg_score=student.avg_score,
        badges=calc_badges(student.total_xp, student.total_sessions, student.avg_score),
        difficulty=calc_adaptive_difficulty(sessions_data),
    )


# ── GET /api/students/leaderboard ─────────────────────────────
@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    """🏆 قائمة أفضل الطلاب"""
    result = await db.execute(
        select(Student)
        .where(Student.is_active == True)
        .order_by(Student.total_xp.desc())
        .limit(20)
    )
    students = result.scalars().all()

    return [
        {
            "rank": i + 1,
            "id": str(s.id),
            "name": s.name,
            "avatar": s.avatar,
            "total_xp": s.total_xp,
            "avg_score": s.avg_score,
            "badges": calc_badges(s.total_xp, s.total_sessions, s.avg_score),
        }
        for i, s in enumerate(students)
    ]


# ── GET /api/students/{student_id}/progress ───────────────────
@router.get("/{student_id}/progress")
async def get_student_progress(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """📈 تقدم طالب محدد مع تحليل المواد"""
    result = await db.execute(
        select(GameSession)
        .where(GameSession.student_id == uuid.UUID(student_id))
        .order_by(GameSession.played_at.desc())
        .limit(20)
    )
    sessions = result.scalars().all()

    # تجميع الأداء حسب المادة
    by_subject: dict = {}
    for s in sessions:
        if s.subject not in by_subject:
            by_subject[s.subject] = {"scores": [], "count": 0}
        by_subject[s.subject]["scores"].append(s.percentage)
        by_subject[s.subject]["count"] += 1

    subject_stats = {
        subject: {
            "avg": round(sum(data["scores"]) / len(data["scores"]), 1),
            "count": data["count"],
        }
        for subject, data in by_subject.items()
    }

    return {
        "sessions": [
            {
                "subject": s.subject,
                "lesson": s.lesson,
                "score": s.score,
                "total": s.total,
                "percentage": s.percentage,
                "xp_earned": s.xp_earned,
                "played_at": s.played_at.isoformat(),
            }
            for s in sessions
        ],
        "subject_stats": subject_stats,
        "adaptive_difficulty": calc_adaptive_difficulty(
            [{"percentage": s.percentage} for s in sessions]
        ),
    }
