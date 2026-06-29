import numpy as np
from typing import List
from fastembed import TextEmbedding, SparseTextEmbedding
from src.utils.logger import logger
from src.config import DENSE_MODEL_NAME, SPARSE_MODEL_NAME

class CPUEmbeddingGenerator:
    """Generates ultra-fast Dense and Sparse embeddings locally on CPU without external API calls."""

    def __init__(self):
        logger.info("Initializing CPU-Optimized Dense and Sparse FastEmbed Models...")
        try:
            # 100% CPU optimized models that do not require any network or GPU boundaries
            self.dense_model = TextEmbedding(model_name=DENSE_MODEL_NAME)
            self.sparse_model = SparseTextEmbedding(model_name=SPARSE_MODEL_NAME)
            logger.info("FastEmbed local models successfully loaded into system memory.")
        except Exception as e:
            logger.critical(f"Failed to load local embedding models: {str(e)}")
            raise e

    def generate_dense_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generates semantic dense vectors for context understanding."""
        if not texts:
            return []
        # fastembed returns generators, we cast to lists for clean structured array serialization
        return list(self.dense_model.embed(texts))

    def generate_sparse_embeddings(self, texts: List[str]) -> List[dict]:
        """Generates tokenized sparse vectors for perfect keyword and version constraints matching."""
        if not texts:
            return []
        sparse_embeddings = list(self.sparse_model.embed(texts))
        
        # Format for Qdrant payload consumption conversion layer
        formatted_sparse = []
        for emb in sparse_embeddings:
            formatted_sparse.append({
                "indices": emb.indices.tolist(),
                "values": emb.values.tolist()
            })
        return formatted_sparse
