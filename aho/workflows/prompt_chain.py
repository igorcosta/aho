import asyncio
from typing import List, Tuple, Union, Any

class PromptChain:
    """
    Executes a list of (plugin, prompt_template) steps in sequence.
    The output of step[i] is fed as the {input} to step[i+1].
    
    Example usage:
        steps = [
            (openai_plugin, "Translate this text to French: {input}"),
            (claude_plugin, "Improve the style of this French text: {input}")
        ]
        chain = PromptChain(steps)
        result = await chain.run("Hello world!")
    """

    def __init__(self, steps: List[Tuple[Any, str]]):
        """
        Args:
            steps: A list of tuples (plugin, prompt_template).
                   - plugin: an object with an async method, e.g. generate_response(messages).
                   - prompt_template: a string that may contain {input} to be replaced
                                     by the output of the previous step.
        """
        self.steps = steps

    async def run(self, initial_input: str) -> str:
        """
        Executes the chain of prompts sequentially, passing output from
        one step to the next.
        
        Args:
            initial_input: The initial input text to feed into step[0].
        
        Returns:
            The final output text from the last step in the chain.
        """
        current_input = initial_input

        for idx, (plugin, prompt_template) in enumerate(self.steps):
            # Format the prompt with the current input
            prompt = prompt_template.format(input=current_input)

            # For demonstration, we wrap the prompt in a minimal "messages" structure
            # if your plugin uses an interface like plugin.generate_response(messages).
            messages = [{"role": "user", "content": prompt}]

            try:
                response = await plugin.generate_response(messages=messages)
            except Exception as e:
                # Basic error handling: you can log or decide how to proceed
                raise RuntimeError(f"Error in PromptChain step {idx}: {e}")

            # The plugin response is expected to be a dict with "content" or similar.
            # Adjust to your plugin’s actual return schema.
            output_text = response.get("content", "")
            
            # Move on to the next step
            current_input = output_text

        # Return the final output
        return current_input
