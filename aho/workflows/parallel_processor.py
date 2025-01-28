import asyncio
from typing import List, Any, Dict

class ParallelProcessorResult:
    """
    Holds the raw responses from each plugin and provides convenience methods
    like majority_vote.
    """
    def __init__(self, responses: List[Dict[str, Any]]):
        """
        Args:
            responses: A list of plugin response dicts. Each dict might look like:
                {
                  "plugin_name": str,
                  "content": str,
                  "raw_response": ...
                }
        """
        self.responses = responses

    @property
    def raw_responses(self) -> List[Dict[str, Any]]:
        """Return the raw response objects from each plugin."""
        return self.responses

    @property
    def majority_vote(self) -> str:
        """
        A naive aggregator that tries to pick the most common 'content'.
        If there's a tie, it just picks the first.
        
        Customize as needed for more sophisticated logic.
        """
        if not self.responses:
            return ""
        contents = [r["content"] for r in self.responses if "content" in r]
        if not contents:
            return ""
        # Tally the frequency of each content
        freq = {}
        for c in contents:
            freq[c] = freq.get(c, 0) + 1
        # Find the content with the maximum frequency
        sorted_contents = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_contents[0][0]

class ParallelProcessor:
    """
    Sends the same prompt to multiple LLM plugins in parallel.
    Collects their responses and provides aggregator methods.
    
    Example usage:
        plugins = [openai_plugin, claude_plugin, local_llama_plugin]
        processor = ParallelProcessor(plugins)
        result = await processor.run("Is this content safe to publish?")
        print(result.majority_vote)
    """

    def __init__(self, plugins: List[Any]):
        """
        Args:
            plugins: A list of LLM plugin instances that provide an async method:
                     generate_response(messages=[...]) -> Dict
        """
        self.plugins = plugins

    async def run(self, user_input: str) -> ParallelProcessorResult:
        """
        Executes the same user_input prompt across all plugins *concurrently*.
        
        Args:
            user_input: The input text prompt to send to each plugin.
        
        Returns:
            ParallelProcessorResult object with each plugin’s response.
        """
        if not self.plugins:
            return ParallelProcessorResult([])

        # Build the message for each plugin. Adjust if you have a custom format.
        messages = [{"role": "user", "content": user_input}]

        # We'll gather tasks for each plugin call
        tasks = []
        for plugin in self.plugins:
            tasks.append(self._call_plugin(plugin, messages))

        plugin_responses = await asyncio.gather(*tasks, return_exceptions=True)
        # plugin_responses is a list of either dict or Exception

        # Build a list of response dicts with a minimal common format
        final_responses = []
        for idx, resp in enumerate(plugin_responses):
            plugin_name = getattr(self.plugins[idx], "name", f"plugin_{idx+1}")
            if isinstance(resp, Exception):
                # If an error occurred, we record it
                final_responses.append({
                    "plugin_name": plugin_name,
                    "content": "",
                    "error": str(resp)
                })
            else:
                # We expect a dict with at least "content"
                final_responses.append({
                    "plugin_name": plugin_name,
                    "content": resp.get("content", ""),
                    "raw_response": resp
                })

        return ParallelProcessorResult(final_responses)

    async def _call_plugin(self, plugin: Any, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Helper method to call plugin.generate_response in a safe block.
        """
        # Each plugin should have an async generate_response(...) method
        return await plugin.generate_response(messages=messages)
