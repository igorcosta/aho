import faiss
import numpy as np
from typing import Any, Dict, List, Optional
from pydantic import Field
from aho.tools.base import Tool, ToolResponse

class FaissVectorTool(Tool):
    """
    Tool for storing and retrieving vector embeddings using FAISS.
    Operations:
      - "index": Index a list of documents by embedding them.
      - "query": Query the index with a text or embedding, returning top-k matches.
    """

    name: str = "faiss_vector_store"
    description: str = "Store and retrieve vectors using FAISS."
    category: str = "vector"

    # You can store some config fields, e.g. dimension
    dimension: int = Field(default=384, description="Embedding dimension")  
    index: Optional[faiss.Index] = None
    docs: List[str] = Field(default_factory=list)  # Keep track of doc texts
    embeddings: List[np.ndarray] = Field(default_factory=list)  # Mirror doc embeddings

    def __init__(
        self,
        embedding_fn, 
        dimension: int = 384,
        **data
    ):
        """
        Args:
            embedding_fn: A callable that takes text and returns a NumPy array embedding.
            dimension (int): Dimension of the embeddings. Must match embedding_fn output size.
        """
        super().__init__(**data)
        self.embedding_fn = embedding_fn
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # Simple L2 index
        self.docs = []
        self.embeddings = []

    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Either 'index' or 'query'.",
                "enum": ["index", "query"],
                "required": True
            },
            "docs": {
                "type": "array",
                "items": {"type": "string"},
                "description": "(If operation='index') list of documents to embed and add to FAISS.",
                "required": False
            },
            "query": {
                "type": "string",
                "description": "(If operation='query') text to embed and retrieve nearest docs.",
                "required": False
            },
            "k": {
                "type": "integer",
                "description": "Number of top results to retrieve",
                "default": 3
            }
        }

    async def execute(
        self,
        operation: str,
        docs: Optional[List[str]] = None,
        query: Optional[str] = None,
        k: int = 3
    ) -> ToolResponse:
        if operation == "index":
            if not docs:
                return ToolResponse(
                    success=False,
                    error="No docs provided for indexing."
                )
            # Embed each doc and add to FAISS
            new_embeddings = []
            for doc in docs:
                emb = self.embedding_fn(doc)
                if isinstance(emb, list):
                    emb = np.array(emb, dtype=np.float32)
                new_embeddings.append(emb)

            new_embeddings_np = np.vstack(new_embeddings)  # shape: (num_docs, dimension)
            self.index.add(new_embeddings_np)
            self.docs.extend(docs)
            self.embeddings.extend(new_embeddings)

            return ToolResponse(
                success=True,
                result=f"Indexed {len(docs)} documents."
            )

        elif operation == "query":
            if not query:
                return ToolResponse(
                    success=False,
                    error="No query text provided."
                )
            query_emb = self.embedding_fn(query)
            if isinstance(query_emb, list):
                query_emb = np.array(query_emb, dtype=np.float32)
            query_emb = np.expand_dims(query_emb, axis=0)  # shape (1, dimension)

            distances, indices = self.index.search(query_emb, k)
            # Collect matched docs
            matched_docs = []
            for idx, dist in zip(indices[0], distances[0]):
                if 0 <= idx < len(self.docs):
                    matched_docs.append({
                        "text": self.docs[idx],
                        "distance": float(dist)
                    })

            return ToolResponse(
                success=True,
                result={
                    "matches": matched_docs
                }
            )
        else:
            return ToolResponse(
                success=False,
                error=f"Unsupported operation: {operation}"
            )
