from typing import List, Dict, Any
from app.utils.logger import logger

class RetrievalService:

    def __init__(
        self,
        vector_service,
        embedding_service,
        reranker_service,
        query_service,
    ):

        self.vector_service = (
            vector_service
        )

        self.embedding_service = (
            embedding_service
        )

        self.reranker_service = (
            reranker_service
        )

        self.query_service = (
            query_service
        )

        self.score_threshold = 0.45

        self.initial_limit = 8

    # =====================================================
    # RETRIEVE
    # =====================================================

    def retrieve(
        self,
        question: str,
        document_id: str,
    ) -> List[Dict[str, Any]]:

        # -------------------------------------------------
        # 1. Generate search queries
        # -------------------------------------------------

        queries = (
            self.query_service
            .generate_queries(
                question
            )
        )

        # -------------------------------------------------
        # 2. Search with every query
        # -------------------------------------------------

        all_candidates = []

        for query in queries:

            query_vector = (
                self.embedding_service
                .embed_query(
                    query
                )
            )

            results = (
                self.vector_service.search(

                    query_vector=
                        query_vector,

                    limit=
                        self.initial_limit,

                    document_id=
                        document_id,
                )
            )

            for result in results:

                payload = (
                    result.payload
                    or {}
                )

                text = payload.get(
                    "text",
                    ""
                )

                if not text.strip():

                    continue

                all_candidates.append({

                    "text": text,

                    "score":
                        float(
                            result.score
                        ),

                    "document_id":
                        payload.get(
                            "document_id"
                        ),

                    "filename":
                        payload.get(
                            "filename"
                        ),

                    "page":
                        payload.get(
                            "page"
                        ),

                    "chunk_index":
                        payload.get(
                            "chunk_index"
                        ),

                    "search_query":
                        query,
                })

        # -------------------------------------------------
        # 3. Remove low-score results
        # -------------------------------------------------

        filtered = [

            candidate

            for candidate
            in all_candidates

            if candidate["score"]
            >= self.score_threshold
        ]

        # -------------------------------------------------
        # 4. Remove duplicate chunks
        # -------------------------------------------------

        unique_chunks = {}

        for candidate in filtered:

            key = (

                candidate.get(
                    "document_id"
                ),

                candidate.get(
                    "chunk_index"
                ),

                candidate.get(
                    "page"
                ),

                candidate.get(
                    "text"
                ),
            )

            existing = (
                unique_chunks.get(
                    key
                )
            )

            if (
                existing is None
                or candidate["score"]
                > existing["score"]
            ):

                unique_chunks[key] = (
                    candidate
                )

        unique_candidates = list(
            unique_chunks.values()
        )

        # -------------------------------------------------
        # 5. Rerank
        # -------------------------------------------------

        reranked = (
            self.reranker_service
            .rerank(

                question=
                    question,

                chunks=
                    unique_candidates,
            )
        )

        return reranked