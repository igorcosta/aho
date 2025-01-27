from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .memory import Memory
from .types import Message, Response, Tool


class BaseLLM(ABC):
    """Base class for all LLM implementations."""
    
    @abstractmethod
    async def generate(self, messages: List[Message], **kwargs) -> Response:
        """Generate a response from the LLM."""
        pass


class BasePlugin(ABC):
    """Base class for all plugins."""
    
    @abstractmethod
    async def setup(self) -> None:
        """Initialize any resources needed by the plugin."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the plugin's main functionality."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up any resources used by the plugin."""
        pass


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(
        self,
        name: str,
        llm: Optional[BaseLLM] = None,
        memory: Optional[Memory] = None,
        tools: Optional[List[Tool]] = None
    ):
        self.name = name
        self.llm = llm
        self.memory = memory or Memory()
        self.tools = tools or []
        self.plugins: Dict[str, BasePlugin] = {}
    
    async def think(self, input_data: str) -> Response:
        """Process input and generate a plan."""
        if not self.llm:
            raise ValueError("No LLM configured for this agent")
        
        # Use memory for context
        context = self.memory.retrieve_relevant(input_data)
        messages = [
            {"role": "system", "content": f"You are {self.name}, an AI assistant."},
            {"role": "user", "content": input_data}
        ]
        
        if context:
            messages.insert(1, {"role": "system", "content": f"Context: {context}"})
        
        response = await self.llm.generate(messages)
        self.memory.store(input_data, response)
        return response
    
    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the agent's toolkit."""
        self.tools.append(tool)
    
    def add_plugin(self, name: str, plugin: BasePlugin) -> None:
        """Add a plugin to the agent."""
        self.plugins[name] = plugin
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self.plugins.get(name)
