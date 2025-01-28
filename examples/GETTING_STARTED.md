# Getting Started with Aho

This guide demonstrates how to use the Aho with Groq and basic tools.

## Basic Setup

```python
import asyncio
from aho.plugins import GroqPlugin
from aho.tools.system import FileSystemTool
from aho.tools.utils.registry import ToolRegistry
from aho.core.memory import Memory

# Initialize Groq plugin
groq = GroqPlugin(api_key="your-groq-api-key")

# Register tools
ToolRegistry.register(FileSystemTool)

# Initialize memory system
memory = Memory()

async def main():
    # Example: Use Groq to analyze a text file
    content = "Let's analyze this text and create a summary."
    
    # Write content to a file
    await memory.use_tool(
        "file_system",
        operation="write",
        path="sample.txt",
        content=content
    )
    
    # Create a prompt for analysis
    prompt = """
    Read the content of the file and create a detailed analysis. Consider:
    1. Main themes
    2. Key points
    3. Suggested improvements
    """
    
    # Use Groq for analysis
    response = await groq.chat(
        messages=[
            {"role": "system", "content": "You are an expert text analyzer."},
            {"role": "user", "content": prompt}
        ]
    )
    
    print("Analysis Results:")
    print(response.content)
    
    # Save analysis to a new file
    await memory.use_tool(
        "file_system",
        operation="write",
        path="analysis.txt",
        content=response.content
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage: Combining Tools and LLM

```python
async def advanced_example():
    # Create a research assistant that uses web search and file system
    from aho.tools.search import WebSearchTool
    ToolRegistry.register(WebSearchTool)
    
    research_topic = "Latest developments in quantum computing"
    
    # Search for information
    search_results = await memory.use_tool(
        "web_search",
        query=research_topic,
        num_results=5
    )
    
    # Use Groq to synthesize the research
    synthesis = await groq.chat(
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant. Synthesize the search results into a coherent report."
            },
            {
                "role": "user",
                "content": f"Create a report based on these search results:\n{search_results}"
            }
        ]
    )
    
    # Save the report
    await memory.use_tool(
        "file_system",
        operation="write",
        path="research_report.md",
        content=synthesis.content
    )

# Run the example
asyncio.run(advanced_example())
```

## Tool Documentation

Each tool in AHO Framework comes with clear documentation and type hints. Here's how to view tool documentation:

```python
# Get tool documentation
file_system_doc = FileSystemTool.get_schema()
print(file_system_doc)

# List available tools
available_tools = ToolRegistry.list_tools()
print("Available tools:", available_tools)
```

## Error Handling

The framework includes built-in error handling and retries:

```python
from aho.core.types import ToolError

async def robust_example():
    try:
        result = await memory.use_tool(
            "file_system",
            operation="read",
            path="nonexistent.txt"
        )
    except ToolError as e:
        print(f"Tool error: {e}")
        # Handle the error appropriately
```

## Next Steps

- Explore other available tools in the `aho.tools` package
- Try different LLM providers (OpenAI, Anthropic, etc.)
- Implement custom tools for your specific needs
- Check out the orchestration examples for more complex workflows
