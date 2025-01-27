import unittest
from aho.agent import Agent, create_agent, BaseAgent
from aho.llm import OpenAI
from aho.plugin import Plugin
from aho.memory import Memory

class MockPlugin(Plugin):
    def on_event(self, event_type, data):
        return f"Processed {data}"
    
    def get_hooks(self):
        return ["test"]

class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        self.llm = OpenAI(api_key="test_key")
        self.memory = Memory()
        self.agent = BaseAgent(self.llm, self.memory)
        self.plugin = MockPlugin()

    def test_add_plugin(self):
        self.agent.add_plugin("test_plugin", self.plugin)
        self.assertIn("test_plugin", self.agent.plugins)
        
    def test_add_invalid_plugin(self):
        with self.assertRaises(ValueError):
            self.agent.add_plugin("invalid", object())
            
    def test_remove_plugin(self):
        self.agent.add_plugin("test_plugin", self.plugin)
        self.agent.remove_plugin("test_plugin")
        self.assertNotIn("test_plugin", self.agent.plugins)
        
    def test_get_plugin(self):
        self.agent.add_plugin("test_plugin", self.plugin)
        plugin = self.agent.get_plugin("test_plugin")
        self.assertEqual(plugin, self.plugin)
        
    def test_get_nonexistent_plugin(self):
        plugin = self.agent.get_plugin("nonexistent")
        self.assertIsNone(plugin)

class TestAgent(unittest.TestCase):
    def test_create_agent(self):
        agent = create_agent("TestAgent")
        self.assertEqual(agent.name, "TestAgent")

    def test_think_without_llm(self):
        agent = Agent("NoLLMAgent")
        response = agent.think("Any input?")
        self.assertEqual(response, "No LLM attached.")

    def test_think_with_llm(self):
        agent = Agent("LLMAgent", llm=OpenAI(api_key="test_key"))
        response = agent.think("Hello")
        self.assertIn("OpenAI response to:", response)
    
    def test_agent_inherits_plugin_functionality(self):
        agent = Agent("TestAgent", llm=OpenAI(api_key="test_key"))
        plugin = MockPlugin()
        
        agent.add_plugin("test_plugin", plugin)
        self.assertIn("test_plugin", agent.plugins)
        
        retrieved_plugin = agent.get_plugin("test_plugin")
        self.assertEqual(retrieved_plugin, plugin)

if __name__ == "__main__":
    unittest.main()