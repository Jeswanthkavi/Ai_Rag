from app.database import SessionLocal

from app.models.document import Document

from app.services.document_service import (
    load_pdf,
    create_chunks
)

from app.services.embedding_service import (
    EmbeddingService
)

from app.services.vector_service import (
    VectorService
)

from app.utils.logger import logger
embedding_service = EmbeddingService()

vector_service = VectorService()


def process_document(
    document_id: str,
    file_path: str,
    filename: str
):

    db = SessionLocal()

    try:

        # -----------------------------------------
        # Find document record
        # -----------------------------------------

        document = (
            db.query(Document)
            .filter(
                Document.document_id
                == document_id
            )
            .first()
        )

        if not document:
            print(
                f"Document not found: "
                f"{document_id}"
            )
            return

        # -----------------------------------------
        # Set status
        # -----------------------------------------

        document.status = "processing"

        db.commit()

        print(
            f"[PROCESSING] {filename}"
        )

        # -----------------------------------------
        # 1. Extract PDF text
        # -----------------------------------------

        pages = load_pdf(
            file_path
        )

        if not pages:

            raise ValueError(
                "No readable text found in PDF"
            )

        print(
            f"Pages extracted: "
            f"{len(pages)}"
        )

        # -----------------------------------------
        # 2. Create chunks
        # -----------------------------------------

        chunks = create_chunks(
            pages
        )

        if not chunks:

            raise ValueError(
                "No chunks created"
            )

        print(
            f"Chunks created: "
            f"{len(chunks)}"
        )

        # -----------------------------------------
        # 3. Generate embeddings
        # -----------------------------------------

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        vectors = (
            embedding_service
            .embed_documents(
                texts
            )
        )

        print(
            f"Embeddings created: "
            f"{len(vectors)}"
        )

        # -----------------------------------------
        # 4. Store vectors in Qdrant
        # -----------------------------------------

        stored_count = (
            vector_service
            .add_chunks(
                chunks=chunks,
                vectors=vectors,
                document_id=document_id,
                filename=filename
            )
        )

        print(
            f"Qdrant points stored: "
            f"{stored_count}"
        )

        # -----------------------------------------
        # 5. Mark ready
        # -----------------------------------------

        document.status = "ready"

        db.commit()

        print(
            f"[READY] {filename}"
        )

    except Exception as error:

        print(
            f"[FAILED] "
            f"{filename}: {error}"
        )

        document = (
            db.query(Document)
            .filter(
                Document.document_id
                == document_id
            )
            .first()
        )

        if document:

            document.status = "failed"

            db.commit()

    finally:

        db.close()