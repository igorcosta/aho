from typing import Dict, Any, Optional
import requests
from ..base import Tool, ToolResponse

class WebSearchTool(Tool):
    """Tool for performing web searches"""
    name = "web_search"
    description = "Search the web for information using a search engine API"
    category = "search"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._get_default_api_key()
    
    def _get_default_api_key(self) -> str:
        # In practice, you'd want to load this from environment variables
        # or a config file
        return "YOUR_DEFAULT_API_KEY"
    
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
                "default": 5,
                "minimum": 1,
                "maximum": 10
            }
        }
    
    async def execute(self, query: str, num_results: int = 5) -> ToolResponse:
        """Execute a web search query"""
        try:
            response = requests.get(
                "https://api.search.example.com/search",
                params={
                    "q": query,
                    "num": num_results,
                    "key": self.api_key
                }
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
