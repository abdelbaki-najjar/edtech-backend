# models/session.py
# ── نموذج جلسة اللعب ──────────────────────────────────────────

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"))

    # تفاصيل الدرس
    subject: Mapped[str]       = mapped_column(String(50))   # math, arabic...
    lesson: Mapped[str]        = mapped_column(String(100))  # الضرب، الجمع...
    game_type: Mapped[str]     = mapped_column(String(50))   # bubbles, quiz...
    difficulty: Mapped[str]    = mapped_column(String(20), default="medium")

    # النتائج
    score: Mapped[int]         = mapped_column(Integer)
    total: Mapped[int]         = mapped_column(Integer)
    percentage: Mapped[float]  = mapped_column(Float)
    xp_earned: Mapped[int]     = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)

    played_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # العلاقات
    student = relationship("Student", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.subject}/{self.lesson} {self.score}/{self.total}>"
