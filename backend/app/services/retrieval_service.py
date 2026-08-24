import faiss
import numpy as np


class RetrievalService:

    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.index = None
        self.chunks = []

    def build_index(self, chunks):
        self.chunks = chunks

        texts = [chunk["text"] for chunk in chunks]

        vectors = self.embedding_service.embed_documents(texts)

        vectors = np.array(vectors).astype("float32")

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(vectors)

    def search(self, question: str, k: int = 3):

        query_vector = self.embedding_service.embed_query(question)

        query_vector = np.array(
            [query_vector]
        ).astype("float32")

        scores, indices = self.index.search(
            query_vector,
            k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):

            if index == -1:
                continue

            result = self.chunks[index].copy()

            result["score"] = float(score)

            results.append(result)

        return results