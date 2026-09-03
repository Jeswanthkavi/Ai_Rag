from __future__ import annotations

from typing import List


class QueryService:

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
    ):
        self.api_key = api_key
        self.model_name = model_name

    def generate_queries(
        self,
        question: str,
    ) -> List[str]:

        text = (question or "").strip()

        if not text:
            return []

        normalized = " ".join(text.split())

        queries = [
            normalized,
            f"What is the document saying about {normalized}?",
            f"Explain {normalized} in detail.",
        ]

        deduped: List[str] = []
        seen = set()

        for query in queries:
            query_str = " ".join(query.split())
            if query_str and query_str.lower() not in seen:
                seen.add(query_str.lower())
                deduped.append(query_str)

        return deduped
