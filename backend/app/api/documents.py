import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from app.services.document_service import create_chunks, load_pdf
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from dependencies import get_current_user
from app.models.user import User


from sqlalchemy.orm import Session

from app.database import get_db

from app.models.document import Document


router = APIRouter()

UPLOAD_DIR = Path("storage/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

embedding_service = EmbeddingService()
vector_service = VectorService()


def ensure_vector_collection():
    try:
        vector_service.create_collection(embedding_service.get_dimension())
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    ensure_vector_collection()

    document_id = str(uuid.uuid4())
    path = UPLOAD_DIR / f"{document_id}.pdf"
    content = await file.read()
    path.write_bytes(content)

    print(f"PDF saved: {path}")

    pages = load_pdf(str(path))
    print(f"Pages extracted: {len(pages)}")

    if not pages:
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF",
        )

    chunks = create_chunks(pages)
    print(f"Chunks created: {len(chunks)}")

    texts = [chunk["text"] for chunk in chunks]
    vectors = embedding_service.embed_documents(texts)
    print(f"Embeddings created: {len(vectors)}")

    stored_count = vector_service.add_chunks(
        chunks=chunks,
        vectors=vectors,
        document_id=document_id,
        filename=filename,
    )
    document = Document(
    document_id=document_id,
    user_id=current_user.id,
    filename=file.filename,
    file_path=str(path)
)

    db.add(document)

    db.commit()

    db.refresh(document)

    print(f"Stored in Qdrant: {stored_count}")

    return {
        "document_id": document_id,
        "filename": filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "vectors": stored_count,
        "status": "ready",
    }