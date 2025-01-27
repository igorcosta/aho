from typing import Dict, Any, Optional, List
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

class ClaudePlugin:
    """
    Plugin for interacting with Anthropic's Claude API.
    Handles API calls, retry logic, and response processing.
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """
        Initialize Claude plugin.
        
        Args:
            api_key (str): Anthropic API key
            model (str): Model to use for completions (default: claude-3-opus-20240229)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
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
        Generate a response using Claude's API.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries
            temperature (float): Sampling temperature
            max_tokens (Optional[int]): Maximum tokens to generate
            tools (Optional[List[Dict[str, Any]]]): List of tools available to the model
            
        Returns:
            Dict[str, Any]: Response from the API
        """
        try:
            # Convert messages to Claude's format
            formatted_messages = self._format_messages(messages)
            
            params = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
                
            if tools:
                params["tools"] = tools
            
            response = await self.client.messages.create(**params)
            return self._process_response(response)
            
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Convert standard message format to Claude's expected format.
        
        Args:
            messages (List[Dict[str, str]]): Standard message format
            
        Returns:
            List[Dict[str, str]]: Claude-formatted messages
        """
        formatted_messages = []
        
        for message in messages:
            role = message["role"]
            if role == "system":
                # Claude handles system messages differently
                formatted_messages.append({
                    "role": "user",
                    "content": message["content"]
                })
            elif role in ["user", "assistant"]:
                formatted_messages.append(message)
                
        return formatted_messages
            
    def _process_response(self, response: Any) -> Dict[str, Any]:
        """
        Process the raw API response into a standardized format.
        
        Args:
            response (Any): Raw API response
            
        Returns:
            Dict[str, Any]: Processed response
        """
        try:
            content = response.content[0].text
            tool_calls = response.tool_calls if hasattr(response, 'tool_calls') else None
            
            processed_response = {
                "content": content,
                "tool_calls": tool_calls,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "raw_response": response
            }
            
            return processed_response
            
        except Exception as e:
            raise Exception(f"Error processing Claude response: {str(e)}")