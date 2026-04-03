# core/config.py — نسخة محدّثة مع معلومات التواصل
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── AI ─────────────────────────────────────────────────────
    OPENROUTER_API_KEY: str = ""
    AI_MODEL: str = "openai/gpt-4o-mini"
    AI_MAX_TOKENS: int = 2000

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/mydb"

    # ── Auth ───────────────────────────────────────────────────
    SECRET_KEY: str = "غيّر-هذا"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # ── Admin ──────────────────────────────────────────────────
    ADMIN_SECRET_KEY: str = "admin-secret-123"
    # ⚠️ غيّر هذا لكلمة سر قوية في .env

    # ── معلومات التواصل للاشتراك ──────────────────────────────
    CONTACT_WHATSAPP: str = "+216XXXXXXXX"
    CONTACT_FACEBOOK: str = "https://facebook.com/yourpage"
    CONTACT_EMAIL:    str = "contact@edtech-tunisia.tn"

    # ── App ────────────────────────────────────────────────────
    APP_NAME: str = "EdTech Tunisia"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
