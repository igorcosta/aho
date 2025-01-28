from typing import Dict, Any, Optional
import requests
from pydantic import Field
from aho.tools.base import Tool, ToolResponse
from aho.tools.config import get_config, SearchConfig

class BraveSearchTool(Tool):
    """
    Tool for performing web searches using Brave Search API (free tier).
    Returns: URL, Title, Snippet.
    """

    name: str = "brave_search"
    description: str = "Search the web using Brave. Returns URL, title, snippet."
    category: str = "search"

    endpoint: str = Field(default="https://api.brave.com/search")

    def __init__(self):
        config = get_config("search")
        if not isinstance(config, SearchConfig):
            raise ValueError("Search configuration not found or invalid.")
        self.config = config
        self.api_key = config.api_key or self._get_default_api_key()

    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "The search query to execute",
                "required": True
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": self.config.max_results,
                "minimum": 1,
                "maximum": 50
            }
        }

    async def execute(self, query: str, num_results: Optional[int] = None) -> ToolResponse:
        try:
            num_results = num_results or self.config.max_results
            # Suppose Brave's search API also requires an Authorization header
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            params = {
                "q": query,
                "count": num_results
            }
            response = requests.get(self.endpoint, headers=headers, params=params, timeout=self.config.default_timeout)
            response.raise_for_status()
            data = response.json()

            # Adjust to Brave's actual JSON response structure
            raw_results = data.get("results", [])
            results = []
            for item in raw_results:
                results.append({
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "snippet": item.get("snippet")
                })

            return ToolResponse(success=True, result={"results": results})
        except Exception as e:
            return ToolResponse(success=False, error=str(e))
