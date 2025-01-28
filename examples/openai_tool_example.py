import asyncio
import os
from aho.core.memory import Memory
from aho.tools.search.web_search import WebSearchTool
from aho.plugins.openai_plugin import OpenAIPlugin
from aho.tools.utils.registry import ToolRegistry

async def main():
    # Initialize OpenAI plugin with your API key
    openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    plugin = OpenAIPlugin(api_key=openai_api_key)
    
    # Register the WebSearchTool
    ToolRegistry.register(WebSearchTool)
    
    # Initialize memory system
    memory = Memory()
    
    # Example conversation with tools
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant with access to web search capabilities."},
        {"role": "user", "content": "What's the latest news about Python 3.12?"}
    ]
    
    # Get available tools for OpenAI
    tools = [
        {
            "type": "function",
            "function": tool.get_schema()
        } for tool in memory.tools.values()
    ]
    
    # Generate response with tool usage
    response = await plugin.generate_response(
        messages=messages,
        temperature=0.7,
        tools=tools
    )
    
    print("Assistant's response:")
    print(response["content"])
    
    # If the model wants to use a tool
    if response.get("tool_calls"):
        for tool_call in response["tool_calls"]:
            tool_name = tool_call.function.name
            tool_args = eval(tool_call.function.arguments)  # Be careful with eval in production
            
            print(f"\nExecuting tool: {tool_name}")
            print(f"Tool arguments: {tool_args}")
            
            # Use the tool through memory system
            tool_result = await memory.use_tool(tool_name, **tool_args)
            print(f"Tool result: {tool_result}")
            
            # Add tool response to conversation
            messages.extend([
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result.result)
                }
            ])
            
            # Get final response incorporating tool results
            final_response = await plugin.generate_response(
                messages=messages,
                temperature=0.7
            )
            
            print("\nFinal response incorporating tool results:")
            print(final_response["content"])
    
    # Check memory for tool usage history
    print("\nTool usage history:")
    history = memory.retrieve_short_term()
    for entry in history:
        if "tool" in entry:
            print(f"Tool: {entry['tool']}")
            print(f"Args: {entry['args']}")
            print(f"Result: {entry['result']}\n")

if __name__ == "__main__":
    asyncio.run(main())
