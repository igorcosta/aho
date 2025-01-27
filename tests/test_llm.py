import unittest
from unittest.mock import patch
from aho.llm import OpenAI, LLM

class MockLLM(LLM):
    def generate_text(self, prompt: str) -> str:
        return f"Mock response to: {prompt}"
        
    def set_api_key(self, key: str):
        self.api_key = key

class TestLLM(unittest.TestCase):
    def test_abstract_class(self):
        with self.assertRaises(TypeError):
            LLM()

class TestOpenAI(unittest.TestCase):
    def setUp(self):
        self.llm = OpenAI(api_key="test_key")
    
    def test_set_api_key(self):
        llm = OpenAI()
        llm.set_api_key("dummy_key")
        self.assertEqual(llm.api_key, "dummy_key")
        
    def test_generate_text(self):
        llm = OpenAI(api_key="dummy_key")
        result = llm.generate_text("Test")
        self.assertIn("OpenAI response to:", result)
        
    def test_missing_api_key(self):
        llm = OpenAI()
        with self.assertRaises(ValueError):
            llm.generate_text("Test without API key")
            
    def test_empty_prompt(self):
        result = self.llm.generate_text("")
        self.assertIn("OpenAI response to:", result)
        
    @patch('aho.llm.OpenAI.generate_text')
    def test_api_error_handling(self, mock_generate):
        mock_generate.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.llm.generate_text("Test error handling")
            
    def test_mock_llm_implementation(self):
        mock_llm = MockLLM()
        mock_llm.set_api_key("mock_key")
        response = mock_llm.generate_text("test prompt")
        self.assertEqual(response, "Mock response to: test prompt")

if __name__ == "__main__":
    unittest.main()