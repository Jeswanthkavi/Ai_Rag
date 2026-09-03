import json

from pathlib import Path

from app.services.embedding_service import (
    EmbeddingService
)

from app.services.vector_service import (
    VectorService
)

from app.services.reranker_service import (
    RerankerService
)

from app.services.retrieval_service import (
    RetrievalService
)


# =========================================================
# CONFIG
# =========================================================

DOCUMENT_ID = "PUT_YOUR_DOCUMENT_ID_HERE"

QUESTIONS_FILE = (
    Path(__file__).parent
    / "rag_questions.json"
)


# =========================================================
# LOAD QUESTIONS
# =========================================================

with open(
    QUESTIONS_FILE,
    "r",
    encoding="utf-8"
) as file:

    questions = json.load(
        file
    )


# =========================================================
# SERVICES
# =========================================================

embedding_service = (
    EmbeddingService()
)

vector_service = (
    VectorService()
)

reranker_service = (
    RerankerService()
)

retrieval_service = RetrievalService(

    vector_service=
        vector_service,

    embedding_service=
        embedding_service,

    reranker_service=
        reranker_service,
)


# =========================================================
# EVALUATION
# =========================================================

total = len(
    questions
)

correct = 0


for index, item in enumerate(
    questions,
    start=1
):

    question = item[
        "question"
    ]

    expected_pages = set(
        item[
            "expected_pages"
        ]
    )

    results = (
        retrieval_service
        .retrieve(

            question=
                question,

            document_id=
                DOCUMENT_ID,
        )
    )

    retrieved_pages = set(

        result.get(
            "page"
        )

        for result
        in results

        if result.get(
            "page"
        ) is not None
    )

    is_correct = bool(
        expected_pages
        &
        retrieved_pages
    )

    if is_correct:

        correct += 1

    print()
    print(
        "=" * 60
    )

    print(
        f"Question {index}: "
        f"{question}"
    )

    print(
        f"Expected pages: "
        f"{sorted(expected_pages)}"
    )

    print(
        f"Retrieved pages: "
        f"{sorted(retrieved_pages)}"
    )

    print(
        f"Result: "
        f"{'PASS' if is_correct else 'FAIL'}"
    )


# =========================================================
# FINAL SCORE
# =========================================================

accuracy = (

    correct / total * 100

    if total > 0

    else 0
)


print()
print(
    "=" * 60
)

print(
    f"Retrieval Accuracy: "
    f"{accuracy:.2f}%"
)

print(
    f"Passed: {correct}/{total}"
)

print(
    "=" * 60
)