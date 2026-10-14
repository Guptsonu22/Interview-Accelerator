import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    ENV: str = Field(default="development")
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8000)
    FRONTEND_PORT: int = Field(default=5173)
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
    DATABASE_URL: str = Field(default="sqlite:///./interview_accelerator.db")

    # LLM Settings
    LLM_PROVIDER: str = Field(default="demo")  # "demo", "gemini", "openai", "groq"
    GEMINI_API_KEY: str = Field(default="")
    OPENAI_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")

    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile")

    # Limits
    MAX_UPLOAD_SIZE_MB: int = Field(default=10)
    ALLOWED_EXTENSIONS: str = Field(default=".pdf,.docx,.txt")
    MAX_INTERVIEW_QUESTIONS: int = Field(default=6)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_extensions_set(self) -> set:
        return {ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()}

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
