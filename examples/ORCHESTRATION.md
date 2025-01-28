# Multi-Agent Orchestration Example

This example demonstrates how multiple agents can collaborate to create a comprehensive markdown document.

## Implementation

```python
import asyncio
from aho.plugins import OpenAIPlugin, AnthropicPlugin, GroqPlugin
from aho.core.orchestrator import ManagerAgent
from aho.core.memory import Memory
from aho.tools.utils.registry import ToolRegistry
from aho.tools.system import FileSystemTool

async def create_collaborative_document():
    # Initialize different LLM plugins
    openai = OpenAIPlugin(api_key="your-openai-key")
    claude = AnthropicPlugin(api_key="your-anthropic-key")
    groq = GroqPlugin(api_key="your-groq-key")
    
    # Register tools
    ToolRegistry.register(FileSystemTool)
    memory = Memory()
    
    # Create specialized agents
    agents = {
        "researcher": openai,  # Good at finding and organizing information
        "writer": claude,      # Excellent at writing and structuring content
        "editor": groq        # Fast at reviewing and suggesting improvements
    }
    
    # Initialize manager agent
    manager = ManagerAgent(agents)
    
    # Define the document creation task
    task = """
    Create a comprehensive guide about 'The Future of AI in Healthcare'.
    The document should include:
    1. Current State of AI in Healthcare
    2. Emerging Trends
    3. Challenges and Opportunities
    4. Future Predictions
    """
    
    # Use debate strategy for collaborative creation
    result = await manager.coordinate(
        task=task,
        strategy="debate",
        timeout=600  # 10 minutes timeout
    )
    
    # Save the final document
    await memory.use_tool(
        "file_system",
        operation="write",
        path="ai_healthcare_guide.md",
        content=result["consensus"]
    )
    
    return result

async def main():
    print("Starting collaborative document creation...")
    result = await create_collaborative_document()
    
    print("\nDocument created successfully!")
    print("\nAgent Contributions:")
    for agent, contribution in result["results"].items():
        print(f"\n{agent} contributed:")
        print(contribution[:200] + "...")

if __name__ == "__main__":
    asyncio.run(main())
```

## Example Output

When you run this script, the agents will collaborate to create a markdown document. Here's what happens behind the scenes:

1. The researcher agent (OpenAI) gathers and organizes information about AI in healthcare
2. The writer agent (Claude) structures this information into a coherent document
3. The editor agent (Groq) reviews and suggests improvements
4. The manager agent facilitates debate and builds consensus
5. The final document is saved to the filesystem

The resulting file will be structured like this:

```markdown
# The Future of AI in Healthcare

## Current State of AI in Healthcare
[Comprehensive overview backed by research...]

## Emerging Trends
[Analysis of current developments...]

## Challenges and Opportunities
[Balanced discussion of pros and cons...]

## Future Predictions
[Well-reasoned forecasts...]
```

## Orchestration Patterns

This example demonstrates several key orchestration patterns:

1. **Role Specialization**: Each agent has a specific role based on their strengths
2. **Consensus Building**: Agents debate and refine each other's work
3. **Manager Oversight**: The ManagerAgent coordinates the process
4. **Tool Integration**: Using FileSystemTool for output
5. **Error Handling**: Timeout and retry mechanisms

## Customization

You can customize this example by:

- Adding more agents with different specialties
- Modifying the debate strategy
- Adding additional tools (e.g., web search, citation checking)
- Implementing different consensus mechanisms
- Adding human-in-the-loop review steps

## Best Practices

- Always set reasonable timeouts
- Implement proper error handling
- Save intermediate results
- Monitor agent interactions
- Validate outputs before saving
