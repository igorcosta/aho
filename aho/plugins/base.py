from typing import Any, Dict


class BasePlugin:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def generate_response(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError