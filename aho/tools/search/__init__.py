from aho.tools.utils.registry import ToolRegistry
from aho.tools.search import (
    BingSearchTool,
    BraveSearchTool,
    DuckDuckGoSearchTool,
    ExaSearchTool,
    GoogleSearchTool
)

ToolRegistry.register(BingSearchTool())
ToolRegistry.register(BraveSearchTool())
ToolRegistry.register(DuckDuckGoSearchTool())
ToolRegistry.register(ExaSearchTool())
ToolRegistry.register(GoogleSearchTool())
