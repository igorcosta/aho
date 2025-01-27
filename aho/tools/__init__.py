from .base import Tool, ToolResponse
from .utils.registry import ToolRegistry

# Import tool categories to ensure registration
from . import search

# Convenience functions
get_tool = ToolRegistry.get_tool
get_all_tools = ToolRegistry.get_all_tools
get_tools_by_category = ToolRegistry.get_tools_by_category

__all__ = [
    'Tool',
    'ToolResponse',
    'ToolRegistry',
    'get_tool',
    'get_all_tools',
    'get_tools_by_category'
]
