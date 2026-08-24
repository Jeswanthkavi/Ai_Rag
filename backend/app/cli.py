from app.config import settings

from app.services.document_service import (
    load_pdf,
    create_chunks
)

from app.services.embedding_service import (
    EmbeddingService
)

from app.services.retrieval_service import (
    RetrievalService
)

from app.services.llm_service import (
    LLMService
)


PDF_PATH = "data/handbook.pdf"


def main():

    print("Loading PDF...")

    pages = load_pdf(PDF_PATH)

    print(f"Pages loaded: {len(pages)}")

    print("Creating chunks...")

    chunks = create_chunks(pages)

    print(f"Chunks created: {len(chunks)}")

    print("Loading embedding model...")

    embedding_service = EmbeddingService()

    print("Building vector index...")

    retrieval_service = RetrievalService(
        embedding_service
    )

    retrieval_service.build_index(chunks)

    print("RAG system ready.")

    llm_service = LLMService(
        settings.gemini_api_key,
        settings.gemini_model
    )

    while True:

        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        results = retrieval_service.search(
            question,
            k=3
        )

        print("\nRetrieved sources:")

        for result in results:
            print(
                f"Page {result['page']} "
                f"| Score: {result['score']:.3f}"
            )

        context = "\n\n".join(
            result["text"]
            for result in results
        )

        answer = llm_service.generate_answer(
            question,
            context
        )

        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()
