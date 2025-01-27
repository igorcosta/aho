from typing import Dict, List, Optional
from pydantic import BaseModel
import logging
import httpx

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: int
    finish_reason: str

class BaseLLM:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        raise NotImplementedError
        
    async def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        raise NotImplementedError
        
    async def embed(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        raise NotImplementedError

class OpenAILLM(BaseLLM):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config["api_key"]
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        
    async def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.config["model"],
                    "messages": messages,
                    **kwargs
                },
                timeout=30
            )
            
        response.raise_for_status()
        data = response.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            tokens_used=data["usage"]["total_tokens"],
            finish_reason=data["choices"][0]["finish_reason"]
        )

class LiteLLMWrapper(BaseLLM):
    """Unified interface for 100+ LLM providers via LiteLLM"""
    def __init__(self, config: Dict):
        super().__init__(config)
        self.provider = config["provider"]
        
    async def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        try:
            import litellm
        except ImportError:
            raise RuntimeError("LiteLLM not installed. Run 'pip install litellm'")
            
        response = await litellm.acompletion(
            model=f"{self.provider}/{self.config['model']}",
            messages=messages,
            **kwargs
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason
        )
