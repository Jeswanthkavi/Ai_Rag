from typing import List, Dict, Any


class ContextService:

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build_context(
        self,
        chunks: List[Dict[str, Any]]
    ) -> str:

        if not chunks:

            return (
                "No relevant information "
                "was retrieved from the document."
            )

        context_parts = []

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            filename = (
                chunk.get(
                    "filename"
                )
                or "Unknown"
            )

            page = (
                chunk.get(
                    "page"
                )
                or "Unknown"
            )

            text = (
                chunk.get(
                    "text"
                )
                or ""
            )

            context_parts.append(

                f"""
SOURCE {index}
File: {filename}
Page: {page}

{text}
""".strip()
            )

        return "\n\n".join(
            context_parts
        )

    # =====================================================
    # BUILD SOURCES
    # =====================================================

    def build_sources(
        self,
        chunks: List[Dict[str, Any]]
    ):

        sources = []

        seen = set()

        for chunk in chunks:

            key = (

                chunk.get(
                    "filename"
                ),

                chunk.get(
                    "page"
                ),
            )

            if key in seen:

                continue

            seen.add(key)

            sources.append({

                "filename":
                    chunk.get(
                        "filename"
                    ),

                "page":
                    chunk.get(
                        "page"
                    ),

                "vector_score":
                    round(
                        float(
                            chunk.get(
                                "score",
                                0
                            )
                        ),
                        4
                    ),

                "rerank_score":
                    round(
                        float(
                            chunk.get(
                                "rerank_score",
                                0
                            )
                        ),
                        4
                    ),
            })

        return sources