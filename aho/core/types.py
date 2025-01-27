from typing import Dict, Any, TypedDict, List, Optional
from pydantic import BaseModel


class Message(TypedDict):
    """A message in a conversation."""
    role: str
    content: str


class Response(BaseModel):
    """A response from an LLM."""
    content: str
    raw: Any
    usage: Dict[str, int]
    tool_calls: Optional[List[Dict[str, Any]]] = None


class Tool(BaseModel):
    """Definition of a tool that can be used by an agent."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str]
    examples: List[Dict[str, Any]]
