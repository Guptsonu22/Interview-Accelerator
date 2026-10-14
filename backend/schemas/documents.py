from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentPasteRequest(BaseModel):
    doc_type: str = Field(..., description="'job_description' or 'resume'")
    text: str = Field(..., min_length=20, max_length=100000, description="Raw text of the job description or resume")
    filename: Optional[str] = Field(default=None, description="Optional label or filename")


class DocumentResponse(BaseModel):
    id: str
    doc_type: str
    filename: str
    char_count: int
    parsed_metadata: Dict[str, Any] = {}
    created_at: str
