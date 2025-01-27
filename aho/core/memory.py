from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from loguru import logger
from pydantic import BaseModel, Field
from ..tools import ToolRegistry, Tool, ToolResponse

class MemoryItem(BaseModel):
    content: str
    embedding: List[float] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    importance: float = Field(ge=0.0, le=1.0, default=0.5)
    access_count: int = Field(default=0)

class Memory:
    """
    Memory system for agents to store and retrieve information.
    Supports both simple key-value storage and sophisticated memory management.
    """
    
    def __init__(self, max_items: int = 1000):
        self.short_term: List[Dict[str, Any]] = []
        self.long_term: Dict[str, Any] = {}
        self.max_items = max_items
        self.tools: Dict[str, Tool] = {}
        self._load_default_tools()
        
    def _load_default_tools(self) -> None:
        """Load all registered tools"""
        for name, tool_cls in ToolRegistry.get_all_tools().items():
            tool = tool_cls()
            self.tools[name] = tool
            logger.debug(f"Loaded tool: {name}")
    
    def register_tool(self, tool_name: str) -> bool:
        """Register a specific tool by name"""
        tool_cls = ToolRegistry.get_tool(tool_name)
        if tool_cls:
            self.tools[tool_name] = tool_cls()
            logger.info(f"Registered tool in memory: {tool_name}")
            return True
        return False
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a registered tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        result = await tool.execute(**kwargs)
        
        # Store tool usage in memory
        self.store_short_term({
            "tool": tool_name,
            "args": kwargs,
            "result": result
        })
        
        return result
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered tools"""
        return {
            name: tool.get_schema() 
            for name, tool in self.tools.items()
        }
        
    def store(self, key: str, value: Any, permanent: bool = False) -> None:
        """Store information in memory with timestamp."""
        timestamp = datetime.utcnow().isoformat()
        memory_item = {
            "key": key,
            "value": value,
            "timestamp": timestamp
        }
        
        if permanent:
            self.long_term[key] = memory_item
            logger.debug(f"Stored permanent memory: {key}")
        else:
            self.short_term.append(memory_item)
            if len(self.short_term) > self.max_items:
                removed = self.short_term.pop(0)
                logger.debug(f"Removed oldest memory: {removed['key']}")
            logger.debug(f"Stored short-term memory: {key}")

    def store_short_term(self, data: Any) -> None:
        """Quick store to short-term memory without key."""
        self.store(f"auto_{len(self.short_term)}", data, permanent=False)
    
    def store_conversation(self, role: str, content: str) -> None:
        """Store a conversation turn with role information."""
        self.store(
            f"conversation_{len(self.short_term)}", 
            {"role": role, "content": content},
            permanent=False
        )
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve information from either short-term or long-term memory."""
        # Check short-term memory first
        for item in reversed(self.short_term):
            if item["key"] == key:
                return item["value"]
        
        # Then check long-term memory
        if key in self.long_term:
            return self.long_term[key]["value"]
        
        return None

    def retrieve_short_term(self) -> List[Any]:
        """Get all short-term memories as a list."""
        return [item["value"] for item in self.short_term]
    
    def retrieve_conversation(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Retrieve conversation history.
        
        Args:
            last_n: Optional number of most recent messages to retrieve
        """
        conversations = [
            item["value"] for item in self.short_term 
            if isinstance(item["value"], dict) and "role" in item["value"]
        ]
        if last_n:
            conversations = conversations[-last_n:]
        return conversations

    def retrieve_relevant(self, query: str, limit: int = 5) -> List[Any]:
        """
        Retrieve relevant information based on a query.
        Simple implementation - in practice, you might want to use
        embeddings and similarity search.
        """
        # Combine both memories for search
        all_memories = (
            [(item["value"], item["timestamp"]) for item in self.short_term] +
            [(item["value"], item["timestamp"]) 
             for item in self.long_term.values()]
        )
        
        # Sort by recency
        all_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return most recent items
        return [memory for memory, _ in all_memories[:limit]]
    
    def clear_short_term(self) -> None:
        """Clear short-term memory."""
        self.short_term = []
        logger.debug("Cleared short-term memory")
    
    def clear_all(self) -> None:
        """Clear all memory."""
        self.short_term = []
        self.long_term = {}
        logger.debug("Cleared all memory")

    def serialize(self) -> str:
        """Serialize memory state to JSON string."""
        memory_state = {
            "short_term": self.short_term,
            "long_term": self.long_term,
            "max_items": self.max_items
        }
        return json.dumps(memory_state)
    
    @classmethod
    def deserialize(cls, json_str: str) -> 'Memory':
        """Create a Memory instance from serialized state."""
        memory_state = json.loads(json_str)
        memory = cls(max_items=memory_state["max_items"])
        memory.short_term = memory_state["short_term"]
        memory.long_term = memory_state["long_term"]
        return memory
