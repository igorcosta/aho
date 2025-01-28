import asyncio
from aho.workflows import PromptChain, ParallelProcessor
from aho.plugins.openai_plugin import OpenAIPlugin
from aho.plugins.claude_plugin import ClaudePlugin

async def main():
    # 1) Create LLM plugins
    openai = OpenAIPlugin(api_key="YOUR_OPENAI_KEY", model="gpt-3.5-turbo")
    claude = ClaudePlugin(api_key="YOUR_ANTHROPIC_KEY")

    # 2) Demo: PromptChain
    translate_improve_chain = PromptChain([
        (openai,  "Translate this text to French: {input}"),
        (claude,  "Improve the style of the following French text: {input}")
    ])
    text = "Hello world!"
    chain_output = await translate_improve_chain.run(text)
    print("PromptChain output:", chain_output)

    # 3) Demo: ParallelProcessor
    parallel = ParallelProcessor([openai, claude])
    question = "Is this content safe to publish?"
    p_result = await parallel.run(question)
    print("Parallel responses:", p_result.raw_responses)
    print("Parallel majority vote:", p_result.majority_vote)

if __name__ == "__main__":
    asyncio.run(main())
