from typing import List, Dict, Any

from sentence_transformers import CrossEncoder


class RerankerService:

    def __init__(self):

        self.model_name = (
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        self.model = CrossEncoder(
            self.model_name
        )

        self.final_limit = 3

    # =====================================================
    # RERANK
    # =====================================================

    def rerank(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        if not chunks:

            return []

        pairs = []

        for chunk in chunks:

            pairs.append(
                [
                    question,
                    chunk["text"],
                ]
            )

        scores = self.model.predict(
            pairs
        )

        reranked = []

        for chunk, score in zip(
            chunks,
            scores
        ):

            item = chunk.copy()

            item["rerank_score"] = (
                float(score)
            )

            reranked.append(
                item
            )

        # -------------------------------------------------
        # Sort by reranker score
        # -------------------------------------------------

        reranked.sort(

            key=lambda item:
                item["rerank_score"],

            reverse=True,
        )

        # -------------------------------------------------
        # Return best chunks
        # -------------------------------------------------

        return reranked[
            :self.final_limit
        ]