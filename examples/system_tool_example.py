import asyncio
from aho.core.memory import Memory
from aho.tools.system.file_system import FileSystemTool
from aho.tools.utils.registry import ToolRegistry

async def main():
    # Register the FileSystemTool
    ToolRegistry.register(FileSystemTool)
    
    # Initialize memory system
    memory = Memory()
    
    # Example: Write and read a file
    file_path = "test_file.txt"
    content = "Hello from Aho Framework!"
    
    # Write file
    print("Writing file...")
    await memory.use_tool(
        "file_system",
        path=file_path,
        operation="write",
        content=content
    )
    
    # Read file
    print("Reading file...")
    result = await memory.use_tool(
        "file_system",
        path=file_path,
        operation="read"
    )
    print(f"File content: {result.result}")
    
    # Delete file
    print("Deleting file...")
    await memory.use_tool(
        "file_system",
        path=file_path,
        operation="delete"
    )
    
    # Check tool usage history
    history = memory.retrieve_short_term()
    print("\nTool usage history:")
    for entry in history:
        if "tool" in entry:
            print(f"Tool: {entry['tool']}")
            print(f"Args: {entry['args']}")
            print(f"Result: {entry['result']}\n")

if __name__ == "__main__":
    asyncio.run(main())
