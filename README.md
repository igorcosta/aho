# AHO Framework

<!-- [![Documentation Status](https://readthedocs.org/projects/aho-framework/badge/?version=latest)](https://aho-framework.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/aho-framework.svg)](https://badge.fury.io/py/aho-framework)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python version](https://img.shields.io/pypi/pyversions/aho-framework.svg)](https://pypi.org/project/aho-framework/)
[![Downloads](https://pepy.tech/badge/aho-framework)](https://pepy.tech/project/aho-framework) -->
Advanced hybrid orchestration, aka Aho for AI agents - a lightweight, composable framework for building production ready AI agents.

## Key Features

🧬 **Simple Yet Powerful**

- Direct API integrations with leading LLM providers (OpenAI, Anthropic)
- No complex abstractions or magic - just clean, predictable Python code
- Built for production with comprehensive error handling and retry logic

🔄 **Flexible Workflows**

- Chain prompts for complex multi-step reasoning
- Route requests to specialized models based on complexity
- Run parallel operations for speed and consensus
- Implement evaluator-optimizer loops for iterative refinement

🛠 **Robust Tooling**

- Standardized interface for all LLM providers
- Built-in support for common agent patterns
- Type-safe tool definitions with comprehensive documentation
- Automatic retry handling and error recovery

🔌 **Easy Integration**

- Works with any Python async framework
- Simple plugin architecture for custom tools
- Comprehensive logging and observability
- Built-in support for popular embeddings and vector stores

## Installation

### Development Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install the package in development mode with all extras:

```bash
pip install -e ".[llm,local,dev]"
```

### Production Installation

```bash
pip install aho
```

## Quick Start

```python
from aho.plugins import OpenAIPlugin, ClaudePlugin
from aho.workflows import PromptChain, ParallelProcessor

# Initialize plugins with your API keys
openai = OpenAIPlugin(api_key="your-openai-key")
claude = ClaudePlugin(api_key="your-anthropic-key")

# Create a simple prompt chain
async def translate_and_improve():
    chain = PromptChain([
        # First, translate text to French
        (openai, "Translate this to French: {input}"),
        # Then, have Claude improve the style
        (claude, "Improve this French text while keeping the meaning: {input}")
    ])
    
    result = await chain.run("Hello world!")
    return result

# Or run parallel operations
async def get_consensus():
    validator = ParallelProcessor([openai, claude])
    result = await validator.run("Is this content safe to publish?")
    return result.majority_vote

```

## Architecture

AHO Framework follows three core principles:

1. **Simplicity**: Clear, understandable code with no hidden complexity
2. **Composability**: Build complex workflows from simple, reusable components
3. **Reliability**: Production-ready with proper error handling and recovery

## Documentation

For detailed documentation and examples, visit our [documentation site](https://aho-framework.readthedocs.io/).

## Development

1. Install development dependencies:

```bash
pip install -e ".[dev]"
```

2. Run tests:

```bash
pytest tests/
```

3. Run code formatting:

```bash
black .
isort .
```

4. Run type checking:

```bash
mypy aho/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

> In Te Reo Māori (Māori language), "aho" means string or cord - representing the threads that connect and weave together different components of our AI systems. Like a master weaver creating intricate patterns, AHO framework helps you orchestrate AI agents with elegance and precision.
