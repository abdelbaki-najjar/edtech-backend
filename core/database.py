# core/database.py
# ── إعداد قاعدة البيانات (PostgreSQL async) ────────────────────

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings

# تحويل postgresql:// → postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL

# أضف asyncpg إذا لم يكن موجوداً
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# ── Engine (الاتصال بقاعدة البيانات) ──────────────────────────
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,   # يطبع SQL في وضع التطوير
    pool_size=5,
    max_overflow=10,
    #connect_args={"ssl": "require"},
)

# ── Session Factory ────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── Base Model ─────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── إنشاء الجداول عند البداية ──────────────────────────────────
async def create_tables():
    # import هنا لتجنب circular imports
    from models import student, session, school  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── Dependency للـ Routes ──────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
