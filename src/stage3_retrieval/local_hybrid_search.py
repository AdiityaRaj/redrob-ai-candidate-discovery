from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, SparseVector, NamedVector, NamedSparseVector
from typing import List, Dict, Any
from src.utils.logger import logger
from src.config import COLLECTION_NAME

class LocalHybridSearchEngine:
    """Local Qdrant In-Memory Hybrid Search Engine combining context and token matching seamlessly on CPU."""

    def __init__(self):
        logger.info("Spinning up local In-Memory Qdrant Client...")
        # Instantiating pure clean memory boundary setup as strictly allowed per sandbox rules
        self.client = QdrantClient(":memory:")
        self._initialize_collection()

    def _initialize_collection(self):
        """Creates the indexing schemas for parallel Dense and Sparse vectors."""
        try:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={
                    "dense-text": VectorParams(
                        size=384,  # Dimensionality configuration match for BGE-Small-EN-v1.5
                        distance=Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "sparse-text": SparseVectorParams() # Standard configuration setup layout
                }
            )
            logger.info(f"Qdrant In-Memory Collection '{COLLECTION_NAME}' successfully schema-locked.")
        except Exception as e:
            logger.error(f"Initialization crash on database setup schema creation: {str(e)}")

    def upsert_candidates_batch(self, points: List[Dict[str, Any]]):
        """Bulk inserts processed candidate vectors and metadata records into the local engine."""
        if not points:
            return
        
        qdrant_points = []
        for pt in points:
            qdrant_points.append({
                "id": pt["id"],
                "vector": {
                    "dense-text": pt["dense_vector"],
                    "sparse-text": SparseVector(
                        indices=pt["sparse_vector"]["indices"],
                        values=pt["sparse_vector"]["values"]
                    )
                },
                "payload": pt["payload"]
            })
            
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=qdrant_points
        )
        logger.info(f"Successfully indexed batch of {len(points)} records into the retrieval engine.")

    def search_hybrid(self, dense_query: List[float], sparse_query: Dict[str, Any], limit: int = 500) -> List[Dict[str, Any]]:
        """Executes full offline fusion retrieval across dual vector lanes matching exact targets under low latency."""
        try:
            # Query configuration layer executing fusion matching without external dependencies
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                prefetch=[
                    # Lane 1: Semantic Dense Matcher
                    self.client.models.Prefetch(
                        query=NamedVector(name="dense-text", vector=dense_query),
                        limit=limit
                    ),
                    # Lane 2: Exact Keyword Token Matcher
                    self.client.models.Prefetch(
                        query=NamedSparseVector(
                            name="sparse-text",
                            vector=SparseVector(
                                indices=sparse_query["indices"],
                                values=sparse_query["values"]
                            )
                        ),
                        limit=limit
                    )
                ],
                # Combines score spaces cleanly via Reciprocal Rank Fusion / Relative Weights
                query=self.client.models.FusionQuery(fusion=self.client.models.Fusion.RRF),
                limit=limit
            )
            
            extracted_hits = []
            for hit in results.points:
                extracted_hits.append({
                    "candidate_id": hit.id,
                    "retrieval_score": hit.score,
                    "metadata": hit.payload
                })
            return extracted_hits
            
        except Exception as e:
            logger.error(f"Hybrid retrieval runtime lane execution failure: {str(e)}")
            return []
