from pathlib import Path
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    BackgroundTasks
)

from sqlalchemy.orm import Session

from app.database import get_db

from dependencies import get_current_user

from app.models.user import User

from app.models.document import Document

from app.services.document_processing_service import (
    process_document
)

from app.services.vector_service import (
    VectorService
)

from app.utils.security import (
    MAX_FILE_SIZE,
    sanitize_filename,
    is_pdf_signature
)


router = APIRouter()


UPLOAD_DIR = Path(
    "storage/documents"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


vector_service = VectorService()


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@router.post("/upload")
async def upload_document(

    background_tasks: BackgroundTasks,

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # -----------------------------------------
    # 1. Validate filename
    # -----------------------------------------

    original_filename = (
        file.filename
        or "document.pdf"
    )

    safe_filename = (
        sanitize_filename(
            original_filename
        )
    )

    # -----------------------------------------
    # 2. Validate file extension
    # -----------------------------------------

    if not safe_filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # -----------------------------------------
    # 3. Validate content type
    # -----------------------------------------

    if file.content_type != (
        "application/pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid content type"
        )

    # -----------------------------------------
    # 4. Read file
    # -----------------------------------------

    content = await file.read()

    # -----------------------------------------
    # 5. Validate file size
    # -----------------------------------------

    if len(content) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "File is too large. "
                "Maximum size is 10 MB."
            )
        )

    # -----------------------------------------
    # 6. Validate PDF signature
    # -----------------------------------------

    if not is_pdf_signature(
        content
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded file is not "
                "a valid PDF"
            )
        )

    # -----------------------------------------
    # 7. Generate document ID
    # -----------------------------------------

    document_id = str(
        uuid.uuid4()
    )

    # -----------------------------------------
    # 8. Generate internal filename
    # -----------------------------------------

    stored_filename = (
        f"{document_id}.pdf"
    )

    file_path = (
        UPLOAD_DIR /
        stored_filename
    )

    # -----------------------------------------
    # 9. Save PDF
    # -----------------------------------------

    file_path.write_bytes(
        content
    )

    # -----------------------------------------
    # 10. Create DB record
    # -----------------------------------------

    document = Document(

        document_id=document_id,

        user_id=current_user.id,

        filename=safe_filename,

        file_path=str(file_path),

        status="processing"
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    # -----------------------------------------
    # 11. Start processing in background
    # -----------------------------------------

    background_tasks.add_task(

        process_document,

        document_id,

        str(file_path),

        safe_filename
    )

    # -----------------------------------------
    # 12. Return response
    # -----------------------------------------

    return {

        "document_id":
            document_id,

        "filename":
            safe_filename,

        "status":
            "processing",

        "message": (
            "Document uploaded successfully. "
            "Processing started."
        )
    }


# =========================================================
# LIST DOCUMENTS
# =========================================================

@router.get("/")
def list_documents(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    documents = (

        db.query(Document)

        .filter(

            Document.user_id
            == current_user.id
        )

        .order_by(

            Document.created_at.desc()
        )

        .all()
    )

    return [

        {

            "document_id":
                document.document_id,

            "filename":
                document.filename,

            "status":
                document.status,

            "created_at":
                document.created_at
        }

        for document
        in documents
    ]


# =========================================================
# GET DOCUMENT
# =========================================================

@router.get("/{document_id}")
def get_document(

    document_id: str,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    document = (

        db.query(Document)

        .filter(

            Document.document_id
            == document_id,

            Document.user_id
            == current_user.id
        )

        .first()
    )

    if not document:

        raise HTTPException(

            status_code=404,

            detail="Document not found"
        )

    return {

        "document_id":
            document.document_id,

        "filename":
            document.filename,

        "status":
            document.status,

        "created_at":
            document.created_at
    }


# =========================================================
# DELETE DOCUMENT
# =========================================================

@router.delete("/{document_id}")
def delete_document(

    document_id: str,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    document = (

        db.query(Document)

        .filter(

            Document.document_id
            == document_id,

            Document.user_id
            == current_user.id
        )

        .first()
    )

    if not document:

        raise HTTPException(

            status_code=404,

            detail="Document not found"
        )

    # -----------------------------------------
    # Delete Qdrant vectors
    # -----------------------------------------

    vector_service.delete_document(
        document_id
    )

    # -----------------------------------------
    # Delete local PDF file
    # -----------------------------------------

    file_path = Path(
        document.file_path
    )

    if file_path.exists():

        file_path.unlink()

    # -----------------------------------------
    # Delete DB record
    # -----------------------------------------

    db.delete(document)

    db.commit()

    return {

        "message":
            "Document deleted successfully"
    }