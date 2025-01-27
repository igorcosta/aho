
from .web_search import WebSearchTool
from ..utils.registry import ToolRegistry

# Register search tools
ToolRegistry.register(WebSearchTool)