from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from backend.schemas.documents import DocumentPasteRequest, DocumentResponse
from backend.services.document_parser import DocumentParserService
from backend.db.models import DocumentDAO
from backend.core.security import sanitize_untrusted_text, check_for_prompt_injection

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(..., description="'job_description' or 'resume'")
):
    clean_type = doc_type.strip().lower()
    if clean_type not in ["job_description", "resume"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="doc_type must be either 'job_description' or 'resume'."
        )

    try:
        content_bytes = await file.read()
        sanitized_text, metadata = DocumentParserService.parse_file(file.filename, content_bytes)
        
        # Check for instruction injection markers
        if check_for_prompt_injection(sanitized_text):
            metadata["injection_flagged"] = True

        doc_record = DocumentDAO.create(
            doc_type=clean_type,
            filename=metadata.get("filename", file.filename),
            raw_text=sanitized_text,
            parsed_metadata=metadata
        )
        return doc_record
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the file: {str(e)}"
        )


@router.post("/paste", response_model=DocumentResponse)
async def paste_document(payload: DocumentPasteRequest):
    clean_type = payload.doc_type.strip().lower()
    if clean_type not in ["job_description", "resume"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="doc_type must be either 'job_description' or 'resume'."
        )

    sanitized_text = sanitize_untrusted_text(payload.text)
    if len(sanitized_text) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text must contain at least 20 non-whitespace characters."
        )

    metadata = {
        "format": "paste",
        "extracted_chars": len(sanitized_text),
        "filename": payload.filename or f"pasted_{clean_type}.txt"
    }

    if check_for_prompt_injection(sanitized_text):
        metadata["injection_flagged"] = True

    doc_record = DocumentDAO.create(
        doc_type=clean_type,
        filename=metadata["filename"],
        raw_text=sanitized_text,
        parsed_metadata=metadata
    )
    return doc_record


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    doc = DocumentDAO.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return doc
