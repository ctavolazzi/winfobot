from bot import Bot
from state import State
from memory import Memory
from port import Port
import logging
import pprint
from hub import Hub

def test_hub_creation():
    """
    Test the creation of a hub.
    """
    hub = Hub()
    assert hub.id is not None, "Hub id is None."
    assert hub.port is not None, "Hub port is None."

def test_hub_methods():
    """
    Test the methods of a hub, including adding bots, broadcasting data, and removing bots.
    """
    # Create a hub and bots
    hub = Hub()
    bot1 = Bot()
    bot2 = Bot()

    # Test adding bots
    hub.add_bot(bot1)
    assert len(hub.bots) == 1, "Bot was not added to hub correctly."
    hub.add_bot(bot2)
    assert len(hub.bots) == 2, "Bot was not added to hub correctly."

    # Test broadcasting data
    hub.broadcast("Test data")
    assert bot1.receive(), "Bot1 didn't receive broadcasted data."
    assert bot2.receive(), "Bot2 didn't receive broadcasted data."

    # Test receiving data from a bot
    hub.receive("Test data from bot1", bot1.port)
    assert "Test data from bot1" in hub.memory, "Hub did not receive data correctly."

    # Test removing a bot
    hub.remove_bot(bot1)
    assert len(hub.bots) == 1, "Bot was not removed from hub correctly."
    hub.remove_bot(bot2)
    assert len(hub.bots) == 0, "Bot was not removed from hub correctly."

def test_bot_creation():
    """
    Test bot creation
    """
    bot = Bot()
    # Initial bot checks
    assert isinstance(bot.id, str), "Bot ID should be a string."
    assert bot._base_type == 'Bot', "Base type should be 'Bot'."
    assert isinstance(bot.port, Port), "Bot port should be an instance of Port."
    assert isinstance(bot.state, State), "Bot state should be an instance of State."
    assert isinstance(bot.memory, Memory), "Bot memory should be an instance of Memory."

def test_bot_methods():
    """
    Test bot methods
    """
    bot1 = Bot()
    bot2 = Bot()

    # Test connection methods
    bot1.attempt_connection(bot2.port)
    assert bot2.port in bot1.port.connections, "attempt_connection method failed."

    bot1.disconnect(bot2.port)
    assert bot2.port not in bot1.port.connections, "disconnect method failed."

    # Test data sending and receiving
    bot1.attempt_connection(bot2.port)
    bot1.send("Test message", bot2.port)
    botmemory = bot2.memory.get_memory()
    print(botmemory)
    assert bot2.memory.recall("Test message") == "Test message", "send method failed."

def test_update_config():
    """
    Test update_config method
    """
    bot = Bot()
    restricted_key = 'id'
    nonrestricted_key = 'name'
    bot.update_config({restricted_key: 'newValue', nonrestricted_key: 'newValue'})
    assert bot.id != 'newValue', f"{restricted_key} should not be updated."
    assert bot.name == 'newValue', f"{nonrestricted_key} should be updated."

def test_state_handling():
    """
    Test update_state method
    """
    bot = Bot()
    state_key = 'stateKey'
    state_value = 'stateValue'
    bot.update_state({state_key: state_value})
    assert bot.state.get(state_key) == state_value, "State should update correctly."

def test_state_handling():
    """
    Test update_state method
    """
    bot = Bot()
    state_key = 'stateKey'
    state_value = 'stateValue'
    bot.update_state({state_key: state_value})
    assert bot.state.get(state_key) == state_value, "Bot state should update correctly."

def test_memory_handling():
    """
    Test memory methods
    """
    bot = Bot()
    memory_value = 'memoryValue'
    bot.remember(memory_value)
    assert bot.recall(memory_value) == memory_value, "Bot should recall the remembered item."
    bot.forget(memory_value)
    assert bot.recall(memory_value) is None, "Bot should forget the forgotten item."

def test_data_handling():
    """
    Test data handling methods
    """
    bot1 = Bot()
    bot2 = Bot()
    bot1.attempt_connection(bot2.port)
    sent_data = 'sentData'
    bot1.send(sent_data, bot2.port)
    assert bot2.recall(sent_data) == sent_data, "Bot should receive and remember the sent data."

def run_tests():
    # Configure logging
    logging.basicConfig(filename='testapp.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    print("Running bot creation tests...")
    test_bot_creation()
    print("Running bot methods tests...")
    test_bot_methods()

    print("Running hub creation tests...")
    test_hub_creation()
    print("Running hub methods tests...")
    test_hub_methods()

    print("Running config update tests...")
    test_update_config()

    print("Running state handling tests...")
    test_state_handling()

    print("Running memory handling tests...")
    test_memory_handling()

    print("Running data handling tests...")
    test_data_handling()

    print("All tests finished.")

if __name__ == "__main__":
    run_tests()
