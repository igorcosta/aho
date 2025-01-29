from aho.plugins.ollama_plugin import OllamaPlugin

# Example 1: Pull a model with progress
async def pull_model_example():
    plugin = OllamaPlugin()
    try:
        async for progress in plugin.pull_model("llama2:13b", stream=True):
            print(f"Status: {progress['status']} - {progress['progress']}")
    finally:
        await plugin.close()

# Example 2: Use custom template
async def template_example():
    plugin = OllamaPlugin({
        "model": "mistral",
        "template_name": "coder"
    })
    
    # Register custom template
    plugin.register_template("coder", """
    You are a senior Python developer. Create a solution for:
    {problem}
    
    Include:
    - Type hints
    - Error handling
    - Unit tests
    """)
    
    try:
        response = await plugin.generate_response([{
            "role": "user",
            "content": "Create a REST API client",
            "variables": {
                "problem": "Implement async HTTP client with retries"
            }
        }])
        print(response["content"])
    finally:
        await plugin.close()

# Example 3: Create custom model
async def create_model_example():
    plugin = OllamaPlugin()
    try:
        modelfile = """
        FROM llama2
        SYSTEM You are a expert marine biologist
        """
        success = await plugin.create_model("marine-bio", modelfile)
        print(f"Model created: {success}")
    finally:
        await plugin.close()