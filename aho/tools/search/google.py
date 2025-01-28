from typing import Dict, Any, Optional
import requests
from pydantic import Field
from aho.tools.base import Tool, ToolResponse
from aho.tools.config import get_config, SearchConfig

class GoogleSearchTool(Tool):
    """
    Tool for performing web searches using Google's Custom Search JSON API.
    Paid.
    Returns: URL, Title, Snippet.
    """

    name: str = "google_search"
    description: str = "Search the web using Google. Returns URL, title, snippet."
    category: str = "search"

    # For Google's Custom Search API:
    # https://developers.google.com/custom-search/v1/overview
    endpoint: str = Field(default="https://www.googleapis.com/customsearch/v1")

    def __init__(self):
        config = get_config("search")
        if not isinstance(config, SearchConfig):
            raise ValueError("Search configuration not found or invalid.")
        self.config = config
        self.api_key = config.api_key or self._get_default_api_key()
        # Also need a custom search engine ID (cx):
        self.cx = "YOUR_CX_ID"

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
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "num": num_results
            }
            response = requests.get(self.endpoint, params=params, timeout=self.config.default_timeout)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            results = []
            for item in items:
                results.append({
                    "url": item.get("link"),
                    "title": item.get("title"),
                    "snippet": item.get("snippet")
                })

            return ToolResponse(success=True, result={"results": results})
        except Exception as e:
            return ToolResponse(success=False, error=str(e))
