from typing import Dict, Type, Optional
from loguru import logger
from ..base import Tool

class ToolRegistry:
    """Global registry for tool management"""
    _tools: Dict[str, Type[Tool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[Tool]) -> None:
        """Register a new tool class"""
        cls._tools[tool_class.name] = tool_class
        logger.info(f"Registered tool: {tool_class.name} in category {tool_class.category}")
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[Type[Tool]]:
        """Get a tool class by name"""
        return cls._tools.get(name)
    
    @classmethod
    def get_all_tools(cls) -> Dict[str, Type[Tool]]:
        """Get all registered tools"""
        return cls._tools.copy()
    
    @classmethod
    def get_tools_by_category(cls, category: str) -> Dict[str, Type[Tool]]:
        """Get all tools in a specific category"""
        return {
            name: tool for name, tool in cls._tools.items()
            if tool.category == category
        }
