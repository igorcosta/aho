from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class BasePlugin(ABC):
    """Abstract base class for AI service plugins."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the AI service.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: List of tools available to the model
            
        Returns:
            Dict containing the response content and metadata
        """
        pass