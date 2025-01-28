import pinecone
import numpy as np
from typing import Any, Dict, List, Optional
from pydantic import Field
from aho.tools.base import Tool, ToolResponse

class PineconeVectorTool(Tool):
    """
    Tool for indexing/searching documents via Pinecone.
    Operations:
      - 'index': store docs
      - 'query': search docs
    """

    name: str = "pinecone_vector_store"
    description: str = "Store and retrieve vectors using Pinecone."
    category: str = "vector"

    api_key: str = Field(..., description="Pinecone API key")
    environment: str = Field(..., description="Pinecone environment, e.g., 'us-east1-gcp'")
    index_name: str = Field(default="aho-index")
    dimension: int = Field(default=384)
    top_k: int = Field(default=3)

    def __init__(self, embedding_fn, **data):
        super().__init__(**data)
        self.embedding_fn = embedding_fn

        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)
        # Create or connect to index
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(self.index_name, dimension=self.dimension)
        self.index = pinecone.Index(self.index_name)

    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Either 'index' or 'query'",
                "enum": ["index", "query"],
                "required": True
            },
            "docs": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of docs to embed if operation='index'.",
                "required": False
            },
            "query": {
                "type": "string",
                "description": "Text to embed if operation='query'.",
                "required": False
            },
            "k": {
                "type": "integer",
                "description": "Number of top results to retrieve for queries",
                "default": self.top_k
            }
        }

    async def execute(
        self,
        operation: str,
        docs: Optional[List[str]] = None,
        query: Optional[str] = None,
        k: Optional[int] = None
    ) -> ToolResponse:
        if operation == "index":
            if not docs:
                return ToolResponse(success=False, error="No docs provided.")
            # Upsert each doc with a unique ID, e.g. doc-0, doc-1
            vectors_to_upsert = []
            for i, doc in enumerate(docs):
                emb = self.embedding_fn(doc)
                if isinstance(emb, list):
                    emb = np.array(emb, dtype=np.float32)
                # Convert to list for Pinecone
                vector_list = emb.tolist()
                vectors_to_upsert.append((f"doc-{i}", vector_list, {"text": doc}))
            self.index.upsert(vectors=vectors_to_upsert)

            return ToolResponse(
                success=True,
                result=f"Upserted {len(docs)} documents into Pinecone"
            )

        elif operation == "query":
            if not query:
                return ToolResponse(success=False, error="No query text provided.")
            if k is None:
                k = self.top_k
            emb = self.embedding_fn(query)
            if isinstance(emb, list):
                emb = np.array(emb, dtype=np.float32)
            query_vec = emb.tolist()
            search_res = self.index.query(vector=query_vec, top_k=k, include_metadata=True)

            matches = []
            if search_res and search_res.matches:
                for match in search_res.matches:
                    matches.append({
                        "id": match.id,
                        "score": match.score,
                        "text": match.metadata.get("text", "")
                    })

            return ToolResponse(success=True, result={"matches": matches})
        else:
            return ToolResponse(
                success=False,
                error=f"Unsupported operation: {operation}"
            )
