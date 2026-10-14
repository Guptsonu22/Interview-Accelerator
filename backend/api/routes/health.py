import os
from datetime import datetime
from fastapi import APIRouter
from backend.core.config import settings
from backend.services.llm_provider import get_llm_provider
from backend.db.database import get_db_connection

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def health_check():
    provider = get_llm_provider()
    db_ok = False
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1;").fetchone()
            db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "app": "Interview Accelerator",
        "version": "1.0.0",
        "environment": settings.ENV,
        "database_connected": db_ok,
        "llm_provider": {
            "name": provider.name,
            "is_demo_mode": provider.is_demo,
            "configured_type": settings.LLM_PROVIDER
        },
        "limits": {
            "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB,
            "allowed_extensions": list(settings.allowed_extensions_set)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
