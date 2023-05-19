import uuid
from utils import setup_logger

class MemoryItem:
    def __init__(self, data):
        self.id = str(uuid.uuid4())
        self.data = data

    def __repr__(self):
        return f'MemoryItem(id={self.id}, data={self.data})'


class Memory:
    def __init__(self, config=None):
        self.id = str(uuid.uuid4())
        self.working_memory = []
        self.short_term = []
        self.long_term = []
        if config:
            for key, value in config.items():
                setattr(self, key, value)

        # Initialize the logger
        self.logger = setup_logger(self)

    def get_memory(self):
        return {'working_memory': self.working_memory, 'short_term': self.short_term, 'long_term': self.long_term}

    def remember(self, data):
        memory_item = MemoryItem(data)
        if memory_item not in self.working_memory:
            self.working_memory.append(memory_item)
            self.logger.info(f"Added {memory_item} to working memory.")
        else:
            self.logger.warning(f"{memory_item} is already in working memory.")

    def commit_to_short_term(self, memory_item):
        if memory_item in self.working_memory:
            self.working_memory.remove(memory_item)
            self.short_term.append(memory_item)
            self.logger.info(f"Moved {memory_item} from working memory to short-term memory.")
        else:
            self.logger.warning(f"Can't move {memory_item}. It's not in working memory.")

    def commit_to_long_term(self, memory_item):
        if memory_item in self.working_memory:
            self.working_memory.remove(memory_item)
            self.long_term.append(memory_item)
            self.logger.info(f"Moved {memory_item} from working memory to long-term memory.")
        else:
            self.logger.warning(f"Can't move {memory_item}. It's not in working memory.")

    def recall(self, memory_item_id):
        for memory_location in [self.working_memory, self.short_term, self.long_term]:
            for memory_item in memory_location:
                if memory_item.id == memory_item_id:
                    self.logger.info(f"Recalled {memory_item} from memory.")
                    return memory_item

        self.logger.warning(f"Memory with ID {memory_item_id} not found in memory.")
        return None

    def clear(self):
        self.working_memory.clear()
        self.short_term.clear()
        self.long_term.clear()
        self.logger.info("Cleared all memories.")

    def __repr__(self):
        return f'Memory(id={self.id}, working_memory={self.working_memory}, short_term={self.short_term}, long_term={self.long_term})'

def test_memory():
    memory = Memory()

    # Test remembering an item
    test_memory_data = 'test_item'
    memory.remember(test_memory_data)
    test_memory_item = memory.working_memory[-1]  # Keep a reference to the added item
    assert test_memory_item.data in [item.data for item in memory.get_memory()['working_memory']]

    # Test moving an item to short-term memory
    memory.commit_to_short_term(test_memory_item)
    assert test_memory_item.data in [item.data for item in memory.get_memory()['short_term']]

    # Test moving an item to long-term memory
    another_test_memory_data = 'another_test_item'
    memory.remember(another_test_memory_data)
    another_test_memory_item = memory.working_memory[-1]  # Keep a reference to the added item
    memory.commit_to_long_term(another_test_memory_item)
    assert another_test_memory_item.data in [item.data for item in memory.get_memory()['long_term']]

    # Test recalling an item
    assert memory.recall(test_memory_item.id).data == 'test_item'
    assert memory.recall(another_test_memory_item.id).data == 'another_test_item'

    # Test clearing memory
    memory.clear()
    assert memory.get_memory() == {'working_memory': [], 'short_term': [], 'long_term': []}

if __name__ == "__main__":
    print("Testing Memory class")
    test_memory()
