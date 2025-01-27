from typing import Callable, Dict, Any
import functools

class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.tools = {}
        return cls._instance

def tool(name: str, description: str, **param_types):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper.metadata = {
            'name': name,
            'description': description,
            'parameters': param_types
        }
        ToolRegistry().tools[name] = wrapper
        return wrapper
    return decorator

class ToolExecutor:
    def __init__(self, agent):
        self.agent = agent
    
    def execute(self, tool_name: str, params: Dict) -> Any:
        if not self.agent._validate_tool_usage(tool_name, params):
            raise ValueError(f"Invalid parameters for tool {tool_name}")
        return ToolRegistry().tools[tool_name](**params)
