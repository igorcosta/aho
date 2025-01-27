from typing import List, Dict, Any, Callable, Optional
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import inspect
import logging

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable

class AgentState(BaseModel):
    role: str
    goals: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    tools: List[Tool] = Field(default_factory=list)
    memory: Optional[Any] = None
    history: List[Dict] = Field(default_factory=list)

class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.state = AgentState(**config)
        self.llm = self._init_llm(config.get('llm'))
        self._tool_registry = {}

    def _init_llm(self, config: Dict) -> Any:
        # Implementation in llm.py
        pass

    @abstractmethod
    async def plan(self, task: str) -> List[Dict]:
        """Generate execution plan for task"""
        pass

    @abstractmethod
    async def execute(self, plan: List[Dict]) -> Any:
        """Execute planned actions"""
        pass

    def register_tool(self, tool: Tool):
        self._tool_registry[tool.name] = tool

    def _validate_tool_usage(self, tool_name: str, params: Dict) -> bool:
        tool = self._tool_registry.get(tool_name)
        if not tool:
            return False
        return all(param in tool.parameters for param in params.keys())

class ConversationalAgent(BaseAgent):
    def __init__(self, config: Dict):
        super().__init__(config)
        self._init_memory(config.get('memory'))
    
    def _init_memory(self, config: Dict):
        # Implementation in memory.py
        pass

    async def chat(self, message: str) -> str:
        plan = await self.plan(message)
        result = await self.execute(plan)
        self._update_memory(message, result)
        return result