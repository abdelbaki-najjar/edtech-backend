# ╔══════════════════════════════════════════════════════════════╗
# ║          EdTech Tunisia — FastAPI Backend                    ║
# ║          تشغيل: uvicorn main:app --reload                   ║
# ╚══════════════════════════════════════════════════════════════╝

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import create_tables
from routes import ai, students, sessions, analytics, auth


# ── Startup / Shutdown ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 EdTech Backend يبدأ...")
    await create_tables()
    print("✅ قاعدة البيانات جاهزة")
    yield
    print("🛑 Backend يتوقف...")


# ── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="EdTech Tunisia API",
    description="منصة الألعاب التعليمية للتعليم الابتدائي التونسي 🇹🇳",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (السماح لـ React بالتواصل مع الـ API) ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",        # React dev
        "http://localhost:5173",        # Vite dev
        "https://edtech-tunisia.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/auth",      tags=["🔐 Auth"])
app.include_router(ai.router,        prefix="/api/ai",        tags=["🤖 AI"])
app.include_router(students.router,  prefix="/api/students",  tags=["👨‍🎓 Students"])
app.include_router(sessions.router,  prefix="/api/sessions",  tags=["🎮 Sessions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["📊 Analytics"])


# ── Health Check ───────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "✅ يعمل",
        "app": "EdTech Tunisia API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
