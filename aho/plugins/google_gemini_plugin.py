from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

class GoogleGeminiPlugin:
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "gemini-1"
        self.base_url = "https://gemini.googleapis.com/v1"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 512
            }
            response = requests.post(f"{self.base_url}/generate", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {})
            }
        except Exception as e:
            raise RuntimeError(f"Google Gemini API error: {e}")