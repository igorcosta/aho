from typing import Dict, Any, Optional, List, AsyncGenerator
from pydantic import BaseModel, Field, ValidationError
from ollama import AsyncClient
from tenacity import retry, stop_after_attempt, wait_exponential
from pathlib import Path
import yaml
from .base import BasePlugin

class OllamaConfig(BaseModel):
    base_url: str = Field("http://localhost:11434", description="Ollama server URL")
    model: str = Field("llama2", description="Default model to use")
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    num_ctx: int = Field(4096, description="Context window size")
    system: Optional[str] = Field(None, description="System prompt")
    template_name: Optional[str] = Field(None, description="Registered template to use")
    timeout: int = Field(30, description="Request timeout in seconds")

class OllamaPlugin(BasePlugin):
    def __init__(self, config: Optional[Dict] = None):
        self.config = OllamaConfig(**(config or {}))
        self.client = AsyncClient(host=self.config.base_url)
        self.templates = self._load_default_templates()
        
    def _load_default_templates(self) -> Dict[str, str]:
        """Load built-in prompt templates"""
        return {
            "alpaca": (
                "Below is an instruction that describes a task. "
                "Write a response that appropriately completes the request.\n\n"
                "### Instruction:\n{instruction}\n\n### Response:"
            ),
            "chatml": (
                "<|im_start|>system\n{system}<|im_end|>\n"
                "<|im_start|>user\n{user}<|im_end|>\n"
                "<|im_start|>assistant\n"
            )
        }

    async def pull_model(self, model_name: str, stream: bool = False) -> AsyncGenerator[Dict, None]:
        """Pull a model from the Ollama registry with progress streaming"""
        try:
            async for progress in self.client.pull(model=model_name, stream=stream):
                yield {
                    "status": progress.status,
                    "progress": progress.progress,
                    "digest": progress.digest,
                    "total": progress.total
                }
        except Exception as e:
            raise RuntimeError(f"Model pull failed: {str(e)}")

    async def create_model(self, model_name: str, modelfile: str) -> bool:
        """Create a custom model from a Modelfile"""
        try:
            response = await self.client.create(
                model=model_name,
                modelfile=modelfile
            )
            return response.status == "success"
        except Exception as e:
            raise RuntimeError(f"Model creation failed: {str(e)}")

    def register_template(self, name: str, template: str, override: bool = False):
        """Register a custom prompt template"""
        if not override and name in self.templates:
            raise ValueError(f"Template '{name}' already exists")
        self.templates[name] = template

    def load_templates_from_file(self, file_path: Path):
        """Load templates from YAML file"""
        try:
            with open(file_path, 'r') as f:
                templates = yaml.safe_load(f)
                self.templates.update(templates)
        except (yaml.YAMLError, IOError) as e:
            raise RuntimeError(f"Failed to load templates: {str(e)}")

    def _apply_template(self, messages: List[Dict]) -> str:
        """Apply registered template to messages"""
        if not self.config.template_name:
            return messages[-1]["content"]
            
        template = self.templates.get(self.config.template_name)
        if not template:
            raise ValueError(f"Template '{self.config.template_name}' not found")
            
        # Extract variables from last message
        variables = messages[-1].get("variables", {})
        return template.format(**variables)

    async def generate_response(self, messages: List[Dict], **kwargs) -> Dict:
        """Generate response with template support"""
        try:
            # Apply template if specified
            if self.config.template_name:
                content = self._apply_template(messages)
                messages = [{"role": "user", "content": content}]

            response = await self.client.chat(
                model=self.config.model,
                messages=messages,
                options={
                    "temperature": self.config.temperature,
                    "num_ctx": self.config.num_ctx
                },
                **kwargs
            )
            
            return {
                "content": response.message.content,
                "model": response.model,
                "usage": {
                    "input_tokens": response.prompt_eval_count,
                    "output_tokens": response.eval_count
                }
            }
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")

    async def list_models(self) -> List[Dict]:
        """List models with details"""
        try:
            response = await self.client.list()
            return [model.dict() for model in response.models]
        except Exception as e:
            raise RuntimeError(f"Failed to list models: {str(e)}")

    async def close(self):
        await self.client.close()
