from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
import uuid


class VectorService:

    def __init__(self):

        self.client = QdrantClient(
            url="http://localhost:6333"
        )

        self.collection_name = "documents"

    # -----------------------------------------
    # Create collection
    # -----------------------------------------

    def create_collection(self, dimension: int):

        collections = self.client.get_collections()

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if self.collection_name not in existing_collections:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )

            print(
                f"Created collection: "
                f"{self.collection_name}"
            )

    # -----------------------------------------
    # Store chunks
    # -----------------------------------------

    def add_chunks(
        self,
        chunks,
        vectors,
        document_id,
        filename
    ):

        points = []

        for chunk, vector in zip(chunks, vectors):

            point_id = str(uuid.uuid4())

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector.tolist(),
                    payload={
                        "document_id": document_id,
                        "filename": filename,
                        "page": chunk["page"],
                        "text": chunk["text"]
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return len(points)

    # -----------------------------------------
    # Search
    # -----------------------------------------

    def search(
    self,
    query_vector,
    limit=3,
    document_id=None
):
        query_filter = None

        if document_id:

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(
                            value=document_id
                        )
                    )
                ]
            )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        # query_points returns a QueryResponse; points are under `result` structure
        # The client returns an object with `.result` containing points in some versions,
        # but here we return the `points` attribute if present, otherwise return the
        # QueryResponse directly so callers can handle it.
        try:
            return results.points
        except Exception:
            return results