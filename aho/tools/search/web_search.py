from typing import Dict, Any, Optional
import requests
from ..base import Tool, ToolResponse
from ..config import get_config, SearchConfig

class WebSearchTool(Tool):
    """Tool for performing web searches"""
    name = "web_search"
    description = "Search the web for information using a search engine API"
    category = "search"
    
    def __init__(self):
        config = get_config("search")
        if not isinstance(config, SearchConfig):
            raise ValueError("Search configuration not found or invalid")
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
        """Execute a web search query"""
        try:
            num_results = num_results or self.config.max_results
            
            response = requests.get(
                "https://api.search.example.com/search",
                params={
                    "q": query,
                    "num": num_results,
                    "key": self.api_key
                },
                timeout=self.config.default_timeout
            )
            response.raise_for_status()
            
            return ToolResponse(
                success=True,
                result=response.json()
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                error=str(e)
            )
