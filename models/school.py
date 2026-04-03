# models/school.py
# ── نموذج المدرسة (B2B) ────────────────────────────────────────

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]       = mapped_column(String(200), nullable=False)
    email: Mapped[str]      = mapped_column(String(255), unique=True)
    phone: Mapped[str]      = mapped_column(String(20), nullable=True)
    city: Mapped[str]       = mapped_column(String(100), nullable=True)

    # الاشتراك
    plan: Mapped[str]       = mapped_column(String(20), default="free")   # free | basic | pro
    max_students: Mapped[int] = mapped_column(default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<School {self.name} | {self.plan}>"
