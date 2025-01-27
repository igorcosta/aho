
from ast import Dict
import os
from typing import Any, Optional
from ..base import Tool, ToolResponse

class FileSystemTool(Tool):
    name = "file_system"
    description = "Interact with the file system"
    category = "system"
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "path": {
                "type": "string",
                "description": "The file system path to interact with",
                "required": True
            },
            "operation": {
                "type": "string",
                "description": "The operation to perform (e.g., read, write, delete)",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "The content to write (if applicable)",
                "required": False
            }
        }
    
    async def execute(self, path: str, operation: str, content: Optional[str] = None) -> ToolResponse:
        try:
            if operation == "read":
                with open(path, "r") as file:
                    result = file.read()
            elif operation == "write":
                with open(path, "w") as file:
                    file.write(content or "")
                    result = "File written successfully"
            elif operation == "delete":
                os.remove(path)
                result = "File deleted successfully"
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            return ToolResponse(success=True, result=result)
        
        except Exception as e:
            return ToolResponse(success=False, error=str(e))