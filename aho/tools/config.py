from typing import Dict, Any, Optional
import os
from pydantic import BaseModel

class ToolConfig(BaseModel):
    """Base configuration for tools"""
    enabled: bool = True
    default_timeout: int = 30

class SearchConfig(ToolConfig):
    """Configuration for search tools"""
    api_key: Optional[str] = None
    max_results: int = 10
    
    @classmethod
    def from_env(cls) -> 'SearchConfig':
        """Create config from environment variables"""
        return cls(
            api_key=os.getenv("SEARCH_API_KEY"),
            max_results=int(os.getenv("SEARCH_MAX_RESULTS", "10"))
        )

_config_registry: Dict[str, ToolConfig] = {}

def register_config(name: str, config: ToolConfig) -> None:
    """Register a tool configuration"""
    _config_registry[name] = config

def get_config(name: str) -> Optional[ToolConfig]:
    """Get a tool configuration"""
    return _config_registry.get(name)

# Register default configurations
register_config("search", SearchConfig.from_env())
