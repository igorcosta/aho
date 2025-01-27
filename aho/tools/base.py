from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolResponse(BaseModel):
    """Base class for tool execution responses"""
    success: bool = True
    error: Optional[str] = None
    result: Any = None

class Tool(ABC):
    """Abstract base class for all tools"""
    name: str
    description: str
    category: str = "general"
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the tool with given parameters"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the tool's parameter schema"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": self._get_parameters_schema()
        }
    
    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Return the schema for the tool's parameters"""
        pass
