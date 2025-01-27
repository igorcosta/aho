import unittest
from aho.memory import Memory

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        
    def test_store_and_retrieve_short_term(self):
        memory = Memory()
        memory.store_short_term("Event1")
        memory.store_short_term("Event2")
        self.assertEqual(memory.retrieve_short_term(), ["Event1", "Event2"])
        
    def test_empty_memory(self):
        self.assertEqual(len(self.memory.retrieve_short_term()), 0)
        
    def test_store_multiple_types(self):
        test_data = [
            "string",
            123,
            {"key": "value"},
            ["list", "items"],
            None
        ]
        for data in test_data:
            self.memory.store_short_term(data)
            
        stored = self.memory.retrieve_short_term()
        self.assertEqual(len(stored), len(test_data))
        self.assertEqual(stored, test_data)
        
    def test_memory_persistence(self):
        self.memory.store_short_term("test1")
        first_retrieve = self.memory.retrieve_short_term()
        second_retrieve = self.memory.retrieve_short_term()
        self.assertEqual(first_retrieve, second_retrieve)
        
    def test_memory_order(self):
        items = ["first", "second", "third"]
        for item in items:
            self.memory.store_short_term(item)
        
        retrieved = self.memory.retrieve_short_term()
        self.assertEqual(retrieved, items)

if __name__ == "__main__":
    unittest.main()