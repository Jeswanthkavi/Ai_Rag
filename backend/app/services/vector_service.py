import uuid

from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    FilterSelector,
)


class VectorService:

    def __init__(self):

        self.client = QdrantClient(
            url="http://localhost:6333"
        )

        self.collection_name = "documents"

    # =====================================================
    # CREATE COLLECTION
    # =====================================================

    def create_collection(
        self,
        dimension: int
    ):

        collections = (
            self.client
            .get_collections()
        )

        existing_collections = [
            collection.name
            for collection
            in collections.collections
        ]

        if (
            self.collection_name
            not in existing_collections
        ):

            self.client.create_collection(

                collection_name=
                    self.collection_name,

                vectors_config=
                    VectorParams(
                        size=dimension,
                        distance=Distance.COSINE,
                    ),
            )

    # =====================================================
    # ADD CHUNKS
    # =====================================================

    def add_chunks(
        self,
        chunks,
        vectors,
        document_id,
        filename,
    ):

        points = []

        for chunk, vector in zip(
            chunks,
            vectors,
        ):

            point_id = str(
                uuid.uuid4()
            )

            points.append(

                PointStruct(

                    id=point_id,

                    vector=
                        vector.tolist(),

                    payload={

                        "document_id":
                            document_id,

                        "filename":
                            filename,

                        "page":
                            chunk["page"],

                        "text":
                            chunk["text"],

                        "chunk_index":
                            chunk.get(
                                "chunk_index",
                                0
                            ),
                    },
                )
            )

        self.client.upsert(

            collection_name=
                self.collection_name,

            points=points,
        )

        return len(points)

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query_vector,
        limit=8,
        document_id=None,
    ):

        query_filter = None

        if document_id:

            query_filter = Filter(

                must=[

                    FieldCondition(

                        key="document_id",

                        match=MatchValue(
                            value=document_id
                        ),
                    )
                ]
            )

        response = (
            self.client
            .query_points(

                collection_name=
                    self.collection_name,

                query=
                    query_vector.tolist(),

                query_filter=
                    query_filter,

                limit=limit,

                with_payload=True,
            )
        )

        return response.points

    # =====================================================
    # DELETE DOCUMENT
    # =====================================================

    def delete_document(
        self,
        document_id: str,
    ):

        document_filter = Filter(

            must=[

                FieldCondition(

                    key="document_id",

                    match=MatchValue(
                        value=document_id
                    ),
                )
            ]
        )

        self.client.delete(

            collection_name=
                self.collection_name,

            points_selector=
                FilterSelector(
                    filter=
                        document_filter
                ),
        )