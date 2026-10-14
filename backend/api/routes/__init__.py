from backend.api.routes.health import router as health_router
from backend.api.routes.documents import router as documents_router
from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.interview import router as interview_router
from backend.api.routes.reports import router as reports_router

__all__ = [
    "health_router",
    "documents_router",
    "analysis_router",
    "interview_router",
    "reports_router",
]
