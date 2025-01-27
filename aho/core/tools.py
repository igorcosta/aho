from typing import Callable, Dict, Any
import functools
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field
import requests
from loguru import logger

class ToolResponse(BaseModel):
    """Base class for tool execution responses"""
    success: bool = True
    error: Optional[str] = None
    result: Any = None

class Tool(ABC):
    """Abstract base class for all tools"""
    name: str
    description: str
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the tool with given parameters"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the tool's parameter schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Return the schema for the tool's parameters"""
        pass

class ToolFactory:
    """Factory for creating and managing tools"""
    _tools: Dict[str, Type[Tool]] = {}
    
    @classmethod
    def register_tool(cls, tool_class: Type[Tool]) -> None:
        """Register a new tool class"""
        cls._tools[tool_class.name] = tool_class
        logger.info(f"Registered tool: {tool_class.name}")
    
    @classmethod
    def create_tool(cls, tool_name: str) -> Optional[Tool]:
        """Create a tool instance by name"""
        tool_class = cls._tools.get(tool_name)
        if tool_class:
            return tool_class()
        logger.error(f"Tool not found: {tool_name}")
        return None
    
    @classmethod
    def get_available_tools(cls) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered tools"""
        return {
            name: tool_class().get_schema()
            for name, tool_class in cls._tools.items()
        }