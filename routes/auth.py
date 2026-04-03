# routes/auth.py
# ── تسجيل الدخول والتسجيل ──────────────────────────────────────

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from core.database import get_db
from core.auth import hash_password, verify_password, create_token
from models.student import Student

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    grade: int = 3
    avatar: str = "👦"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """📝 تسجيل طالب جديد"""
    # التحقق أن الإيميل غير مستخدم
    result = await db.execute(select(Student).where(Student.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="هذا الإيميل مسجل مسبقاً")

    student = Student(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        grade=req.grade,
        avatar=req.avatar,
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)

    token = create_token({"sub": str(student.id), "role": "student"})
    return {"token": token, "student_id": str(student.id), "name": student.name}


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """🔐 تسجيل الدخول"""
    result = await db.execute(select(Student).where(Student.email == req.email))
    student = result.scalar_one_or_none()

    if not student or not verify_password(req.password, student.password_hash):
        raise HTTPException(status_code=401, detail="إيميل أو كلمة مرور خاطئة")

    token = create_token({"sub": str(student.id), "role": "student"})
    return {
        "token": token,
        "student": {
            "id": str(student.id),
            "name": student.name,
            "avatar": student.avatar,
            "total_xp": student.total_xp,
        },
    }


# ─────────────────────────────────────────────────────────────
# routes/analytics.py
# ── تحليلات لوحة المعلم ─────────────────────────────────────
from fastapi import APIRouter as AnalyticsRouter
from sqlalchemy import func

analytics_router = AnalyticsRouter()


# نستخدم router مباشرة في main.py
# هذا الملف يُضاف للـ routes/analytics.py
