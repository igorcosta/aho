from typing import Dict, Any, Optional
import requests
from pydantic import Field
from aho.tools.base import Tool, ToolResponse
from aho.tools.config import get_config, SearchConfig

class DuckDuckGoSearchTool(Tool):
    """
    Free search via DuckDuckGo's unofficial API.
    Returns: URL, Title, Snippet.
    """

    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo. Returns URL, title, snippet."
    category: str = "search"

    # For official DuckDuckGo, there's no official public API. Some use serpapi or unofficial endpoints:
    endpoint: str = Field(default="https://api.duckduckgo.com")

    def __init__(self):
        config = get_config("search")
        if not isinstance(config, SearchConfig):
            raise ValueError("Search configuration not found or invalid.")
        self.config = config
        # Might not need an API key for DuckDuckGo or might use a third-party service
        self.api_key = config.api_key or ""

    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "The search query to execute",
                "required": True
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (some implementations might ignore or approximate)",
                "default": self.config.max_results,
                "minimum": 1,
                "maximum": 50
            }
        }

    async def execute(self, query: str, num_results: Optional[int] = None) -> ToolResponse:
        try:
            num_results = num_results or self.config.max_results
            params = {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1"
            }
            # Possibly use a third-party or a serp api for more robust results
            response = requests.get(self.endpoint, params=params, timeout=self.config.default_timeout)
            response.raise_for_status()
            data = response.json()

            # Basic extraction from DuckDuckGo's Instant Answer JSON
            # Official doc: https://api.duckduckgo.com/?q=duckduckgo&format=json
            related_topics = data.get("RelatedTopics", [])
            results = []
            for item in related_topics[:num_results]:
                # Some are "Topics," some are direct "Text" and "FirstURL"
                if "Text" in item and "FirstURL" in item:
                    results.append({
                        "url": item["FirstURL"],
                        "title": item["Text"],
                        "snippet": None  # DuckDuckGo might not provide a snippet
                    })

            return ToolResponse(success=True, result={"results": results})
        except Exception as e:
            return ToolResponse(success=False, error=str(e))
