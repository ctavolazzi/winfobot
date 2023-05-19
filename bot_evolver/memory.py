# Memory class
class Memory():
    """
    The Memory class represents a bot's memory.

    There are two types of memories: short-term and long-term.

    TODO: Implement short-term memory.
    """
    def __init__(self):
        self.memories = []

    def add_memory(self, memory):
        self.memories.append(memory)

    def get_memories(self):
        return self.memories

    def test_self(self):
        assert hasattr(self, 'memories'), "memories attribute is missing"
        assert hasattr(self, 'add_memory'), "add_memory method is missing"
        assert hasattr(self, 'get_memories'), "get_memories method is missing"
        print("All tests pass.")