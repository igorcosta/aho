from typing import Dict, Any, Optional, List
import groq
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import BasePlugin

class GroqPlugin(BasePlugin):
    """
    Plugin for interacting with Groq's API services.
    Handles API calls, retry logic, and response processing.
    """
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        """
        Initialize Groq plugin.
        
        Args:
            api_key (str): Groq API key
            model (str): Model to use for completions (default: mixtral-8x7b-32768)
        """
        self.client = groq.Client(api_key=api_key)
        self.model = model
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using Groq's API.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries
            temperature (float): Sampling temperature
            max_tokens (Optional[int]): Maximum tokens to generate
            tools (Optional[List[Dict[str, Any]]]): List of tools available to the model
            
        Returns:
            Dict[str, Any]: Response from the API
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
                
            if tools:
                params["tools"] = tools
            
            response = await self.client.chat.completions.create(**params)
            return self._process_response(response)
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
            
    def _process_response(self, response: Any) -> Dict[str, Any]:
        """
        Process the raw API response into a standardized format.
        
        Args:
            response (Any): Raw API response
            
        Returns:
            Dict[str, Any]: Processed response
        """
        try:
            content = response.choices[0].message.content
            tool_calls = response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None
            
            processed_response = {
                "content": content,
                "tool_calls": tool_calls,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "raw_response": response
            }
            
            return processed_response
            
        except Exception as e:
            raise Exception(f"Error processing Groq response: {str(e)}")
