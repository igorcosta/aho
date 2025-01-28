from .base import Tool, ToolResponse
from .utils.registry import ToolRegistry
from .config import get_config, register_config, ToolConfig

# Import all tool categories to ensure registration
from . import search
from . import system
from .search.web_search import WebSearchTool
from .system.file_system import FileSystemTool

# Ensure configurations are loaded
from . import config

# Register default tools
ToolRegistry.register(WebSearchTool)
ToolRegistry.register(FileSystemTool)

# Convenience functions
get_tool = ToolRegistry.get_tool
get_all_tools = ToolRegistry.get_all_tools
get_tools_by_category = ToolRegistry.get_tools_by_category

__all__ = [
    'Tool',
    'ToolResponse',
    'ToolRegistry',
    'WebSearchTool',
    'FileSystemTool',
    'get_tool',
    'get_all_tools',
    'get_tools_by_category',
    'get_config',
    'register_config',
    'ToolConfig'
]
