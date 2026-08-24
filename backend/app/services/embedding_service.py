from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def embed_documents(
        self,
        texts: list[str]
    ):

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )

    def embed_query(
        self,
        text: str
    ):

        return self.model.encode(
            [text],
            normalize_embeddings=True
        )[0]

    def get_dimension(self):

        return self.model.get_sentence_embedding_dimension()