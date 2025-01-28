from typing import Dict, Any, Optional
import requests
from pydantic import Field
from aho.tools.base import Tool, ToolResponse
from aho.tools.config import get_config, SearchConfig

class BingSearchTool(Tool):
    """
    Tool for performing web searches using Bing Search API.
    Paid service.
    Returns: URL, Title, Snippet.
    """

    name: str = "bing_search"
    description: str = "Search the web using Bing. Returns URL, title, snippet."
    category: str = "search"

    # Example: you'll likely set your own "endpoint" and pass the API key in a header.
    endpoint: str = Field(default="https://api.bing.microsoft.com/v7.0/search")

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

            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key
            }
            params = {
                "q": query,
                "count": num_results
            }
            response = requests.get(self.endpoint, headers=headers, params=params, timeout=self.config.default_timeout)
            response.raise_for_status()
            data = response.json()

            # This part depends on Bing's actual JSON structure:
            # e.g., data["webPages"]["value"] is a typical place for results
            results_data = data.get("webPages", {}).get("value", [])
            results = []
            for item in results_data:
                results.append({
                    "url": item.get("url"),
                    "title": item.get("name"),
                    "snippet": item.get("snippet")
                })

            return ToolResponse(success=True, result={"results": results})
        except Exception as e:
            return ToolResponse(success=False, error=str(e))
