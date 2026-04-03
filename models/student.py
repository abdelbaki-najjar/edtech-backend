# models/student.py — أضف حقل plan
# في الكلاس Student أضف هذا السطر:

# plan: Mapped[str] = mapped_column(String(20), default="free")
# 
# القيم الممكنة: "free" | "premium" | "school"
#
# مثال كامل:

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base


class Student(Base):
    __tablename__ = "students"

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:          Mapped[str]       = mapped_column(String(100))
    email:         Mapped[str]       = mapped_column(String(255), unique=True)
    password_hash: Mapped[str]       = mapped_column(String(255))
    avatar:        Mapped[str]       = mapped_column(String(10),  default="👦")
    grade:         Mapped[int]       = mapped_column(Integer,     default=3)

    # ── Gamification ───────────────────────────────────────────
    total_xp:       Mapped[int] = mapped_column(Integer, default=0)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    avg_score:      Mapped[int] = mapped_column(Integer, default=0)

    # ── Subscription ── الاشتراك ───────────────────────────────
    plan:      Mapped[str]  = mapped_column(String(20), default="free")
    # free | premium | school

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="student", lazy="selectin")
