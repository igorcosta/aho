
from aho.agent import create_agent
from aho.llm import OpenAI
from aho.tool import WebScraper

agent = create_agent("MyAgent", llm=OpenAI(api_key="secret"))
agent.add_tool(WebScraper())
answer = agent.think("Who is the current President of France?")
print(answer)