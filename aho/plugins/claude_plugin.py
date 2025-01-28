from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
import anthropic

class ClaudePlugin:
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "claude-3-opus-20240229"
        self.client = anthropic.Anthropic(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        try:
            formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
            response = await self.client.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens or 512
            )
            return {
                "content": response["choices"][0]["message"]["content"],
                "usage": response.get("usage", {})
            }
        except Exception as e:
            raise RuntimeError(f"Claude API error: {e}")