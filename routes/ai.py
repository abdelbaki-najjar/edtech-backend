# routes/ai.py — مع نظام الحدود
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import uuid

from core.database import get_db
from core.auth import get_current_user
from core.config import settings
from services.ai_service import generate_game, generate_worksheet, analyze_student
from services.usage_service import check_limit, upgrade_student, PLANS

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────
class GameRequest(BaseModel):
    grade: int
    subject: str
    lesson_title: str
    game_type: str
    difficulty: str = "medium"
    num_questions: int = 8

class WorksheetRequest(BaseModel):
    grade: int
    subject: str
    lesson_title: str
    difficulty: str = "medium"
    student_name: Optional[str] = None

class UpgradeRequest(BaseModel):
    student_id: str
    plan: str           # premium | school | free
    admin_key: str      # مفتاح سري تضعه في .env


# ── POST /api/ai/generate-game ─────────────────────────────────
@router.post("/generate-game")
async def api_generate_game(
    req: GameRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """🤖 توليد لعبة مع التحقق من الحد اليومي"""
    from models.student import Student

    # جلب الطالب
    result = await db.execute(
        select(Student).where(Student.id == uuid.UUID(user["id"]))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # ── التحقق من الحد ────────────────────────────────────────
    usage = await check_limit(student, db)

    if not usage["allowed"]:
        # إرجاع خطأ خاص مع معلومات الاشتراك
        raise HTTPException(
            status_code=402,   # Payment Required
            detail={
                "type": "limit_reached",
                "plan": usage["plan"],
                "used": usage["used"],
                "limit": usage["limit"],
                "message": "وصلت للحد اليومي. اشترك للحصول على المزيد!",
                "contact": {
                    "whatsapp": settings.CONTACT_WHATSAPP,
                    "facebook": settings.CONTACT_FACEBOOK,
                    "email":    settings.CONTACT_EMAIL,
                }
            }
        )

    # ── توليد اللعبة ──────────────────────────────────────────
    try:
        data = await generate_game(
            grade=req.grade,
            subject=req.subject,
            lesson_title=req.lesson_title,
            game_type=req.game_type,
            difficulty=req.difficulty,
            num_questions=req.num_questions,
        )
        return {
            "success": True,
            "data": data,
            "usage": {
                "used":      usage["used"] + 1,
                "limit":     usage["limit"],
                "remaining": usage["remaining"] - 1,
                "plan":      usage["plan"],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /api/ai/generate-worksheet ───────────────────────────
@router.post("/generate-worksheet")
async def api_generate_worksheet(
    req: WorksheetRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    from models.student import Student
    result = await db.execute(select(Student).where(Student.id == uuid.UUID(user["id"])))
    student = result.scalar_one_or_none()

    usage = await check_limit(student, db)
    if not usage["allowed"]:
        raise HTTPException(
            status_code=402,
            detail={
                "type": "limit_reached",
                "message": "وصلت للحد اليومي",
                "contact": {
                    "whatsapp": settings.CONTACT_WHATSAPP,
                    "facebook": settings.CONTACT_FACEBOOK,
                    "email":    settings.CONTACT_EMAIL,
                }
            }
        )

    try:
        data = await generate_worksheet(
            grade=req.grade,
            subject=req.subject,
            lesson_title=req.lesson_title,
            difficulty=req.difficulty,
            student_name=req.student_name,
        )
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/ai/usage ──────────────────────────────────────────
@router.get("/usage")
async def get_my_usage(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """يرجع استخدام الطالب اليوم"""
    from models.student import Student
    result = await db.execute(select(Student).where(Student.id == uuid.UUID(user["id"])))
    student = result.scalar_one_or_none()
    usage = await check_limit(student, db)
    return usage


# ── POST /api/ai/upgrade ───────────────────────────────────────
@router.post("/upgrade")
async def admin_upgrade(
    req: UpgradeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    🔑 ترقية مستخدم يدوياً — للمشرف فقط
    تستخدمه أنت بعد تأكيد الدفع
    """
    # التحقق من مفتاح المشرف
    if req.admin_key != settings.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="مفتاح المشرف خاطئ")

    if req.plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"الخطة غير صحيحة. الخيارات: {list(PLANS.keys())}")

    success = await upgrade_student(req.student_id, req.plan, db)
    if not success:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    return {
        "success": True,
        "message": f"✅ تم ترقية المستخدم لخطة {req.plan}",
        "plan": req.plan,
        "daily_limit": PLANS[req.plan]["daily_limit"],
    }
