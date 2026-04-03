# core/auth.py
# ── نظام المصادقة JWT ──────────────────────────────────────────

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

# ── تشفير كلمات المرور ────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """التحقق من كلمة المرور"""
    return pwd_context.verify(plain, hashed)


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """إنشاء JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """فك تشفير JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token غير صالح أو منتهي الصلاحية",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency — يسترجع المستخدم الحالي من الـ Token"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token غير صالح")
    return {"id": user_id, "role": payload.get("role", "student")}


async def require_teacher(current_user: dict = Depends(get_current_user)):
    """Dependency — يسمح فقط للمعلمين"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="غير مسموح — للمعلمين فقط")
    return current_user
