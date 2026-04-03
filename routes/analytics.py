# routes/analytics.py
# ── تحليلات لوحة المعلم ─────────────────────────────────────────

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.auth import require_teacher
from models.student import Student
from models.session import Session as GameSession

router = APIRouter()


@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    # teacher: dict = Depends(require_teacher),  # فعّل في الإنتاج
):
    """📊 نظرة عامة للمعلم"""
    # إجمالي الطلاب
    students_count = await db.execute(func.count(Student.id))

    # إجمالي الجلسات
    sessions_result = await db.execute(select(GameSession))
    all_sessions = sessions_result.scalars().all()

    # متوسط الأداء العام
    avg = (
        round(sum(s.percentage for s in all_sessions) / len(all_sessions), 1)
        if all_sessions else 0
    )

    # أداء حسب المادة
    subject_stats = {}
    for s in all_sessions:
        if s.subject not in subject_stats:
            subject_stats[s.subject] = {"scores": [], "count": 0}
        subject_stats[s.subject]["scores"].append(s.percentage)
        subject_stats[s.subject]["count"] += 1

    subjects = {
        sub: {
            "avg": round(sum(d["scores"]) / len(d["scores"]), 1),
            "count": d["count"],
        }
        for sub, d in subject_stats.items()
    }

    # أفضل الطلاب
    top_result = await db.execute(
        select(Student).order_by(Student.total_xp.desc()).limit(5)
    )
    top_students = [
        {"name": s.name, "avatar": s.avatar, "xp": s.total_xp, "avg": s.avg_score}
        for s in top_result.scalars().all()
    ]

    # آخر الجلسات
    recent_result = await db.execute(
        select(GameSession).order_by(GameSession.played_at.desc()).limit(10)
    )
    recent = [
        {
            "subject": s.subject,
            "lesson": s.lesson,
            "score": s.score,
            "total": s.total,
            "played_at": s.played_at.isoformat(),
        }
        for s in recent_result.scalars().all()
    ]

    return {
        "total_sessions": len(all_sessions),
        "avg_score": avg,
        "subject_stats": subjects,
        "top_students": top_students,
        "recent_sessions": recent,
    }


@router.get("/recommendations")
async def get_ai_recommendations(db: AsyncSession = Depends(get_db)):
    """💡 توصيات AI للمعلم بناءً على بيانات الفصل"""
    sessions_result = await db.execute(select(GameSession))
    sessions = sessions_result.scalars().all()

    recommendations = []

    # حساب أداء كل مادة
    subject_avgs = {}
    for s in sessions:
        if s.subject not in subject_avgs:
            subject_avgs[s.subject] = []
        subject_avgs[s.subject].append(s.percentage)

    for subject, scores in subject_avgs.items():
        avg = sum(scores) / len(scores)
        if avg < 65:
            recommendations.append({
                "type": "warning",
                "subject": subject,
                "message": f"⚠️ الطلاب يحتاجون دعماً في {subject} (معدل {avg:.0f}%)",
                "action": "فعّل وضع السهل وأضف تمارين إضافية",
            })
        elif avg >= 88:
            recommendations.append({
                "type": "success",
                "subject": subject,
                "message": f"✅ أداء ممتاز في {subject} (معدل {avg:.0f}%)",
                "action": "يمكن رفع مستوى الصعوبة",
            })

    return {"recommendations": recommendations}
