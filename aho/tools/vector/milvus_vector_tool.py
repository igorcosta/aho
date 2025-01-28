from typing import Any, Dict, List, Optional
from pydantic import Field
import numpy as np
from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType,
    Collection, utility
)
from aho.tools.base import Tool, ToolResponse

class MilvusVectorTool(Tool):
    """
    Tool that uses Milvus as the vector DB. 
    Operations:
      - 'index': Store docs
      - 'query': Search docs
    """

    name: str = "milvus_vector_store"
    description: str = "Store and retrieve vectors using Milvus."
    category: str = "vector"

    milvus_host: str = Field(default="localhost")
    milvus_port: str = Field(default="19530")
    collection_name: str = Field(default="aho_collection")
    dimension: int = Field(default=384)
    index_created: bool = Field(default=False)

    def __init__(self, embedding_fn, **data):
        super().__init__(**data)
        self.embedding_fn = embedding_fn

        # Connect to Milvus
        connections.connect(alias="default", host=self.milvus_host, port=self.milvus_port)

        # Create a collection if it doesn't exist
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048)
            ]
            schema = CollectionSchema(fields, description="AHO vector store collection")
            self.collection = Collection(name=self.collection_name, schema=schema)
            # Create an IVF_FLAT index, for example
            index_params = {
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
                "metric_type": "L2"
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            self.index_created = True
        else:
            self.collection = Collection(self.collection_name)

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
                "description": "If 'index', list of docs to store in Milvus.",
                "required": False
            },
            "query": {
                "type": "string",
                "description": "If 'query', text to embed and find similar docs.",
                "required": False
            },
            "k": {
                "type": "integer",
                "description": "Number of top results to retrieve.",
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
                return ToolResponse(success=False, error="No docs provided.")
            # Insert docs
            embeddings = []
            texts = []
            for d in docs:
                emb = self.embedding_fn(d)
                if isinstance(emb, list):
                    emb = np.array(emb, dtype=np.float32)
                embeddings.append(emb.tolist())
                texts.append(d)

            # Data to insert: [[embedding1, embedding2, ...], [text1, text2, ...]]
            data_to_insert = [embeddings, texts]  # id is auto_id
            self.collection.insert(data_to_insert)
            # Make data queryable
            self.collection.flush()

            return ToolResponse(
                success=True,
                result=f"Indexed {len(docs)} documents into Milvus"
            )

        elif operation == "query":
            if not query:
                return ToolResponse(success=False, error="No query text provided.")
            query_emb = self.embedding_fn(query)
            if isinstance(query_emb, list):
                query_emb = np.array(query_emb, dtype=np.float32)
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = self.collection.search(
                data=[query_emb.tolist()],
                anns_field="embedding",
                param=search_params,
                limit=k,
                output_fields=["text"]
            )
            # results is a list of hits for each query
            if not results:
                return ToolResponse(success=True, result={"matches": []})

            hits = []
            for hit in results[0]:
                hits.append({
                    "text": hit.entity.get("text", ""),
                    "distance": float(hit.distance)
                })
            return ToolResponse(success=True, result={"matches": hits})

        else:
            return ToolResponse(success=False, error=f"Unknown operation: {operation}")
