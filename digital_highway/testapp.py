from bot import Bot
from state import State
from memory import Memory
from port import Port
import logging
import pprint

def test_bot_creation():
    """
    Test the creation of a bot with default values, specific values, and a mix of default and specific values.
    """
    # Test creating a bot with default values
    bot1 = Bot()
    bot1.logger.info("Created bot with default values")
    assert bot1.id is not None, "Default bot id is None."

    # Test creating a bot with specific values
    bot2_config = {
    'id': 'Bot2',
    'state': State({'name': 'Bot2State'}),
    'memory': Memory({'short_term': [], 'long_term': []}),
    'password': 'pass2',
    }


    bot2 = Bot(bot2_config)
    bot2.logger.info("Created bot with specific values")
    bot2.change_port(Port(bot2.id, {'address': '8080'}))
    assert bot2.id == 'Bot2', "Bot2 id doesn't match."
    assert bot2.port.get_address() == '8080', "Bot2 port doesn't match."
    assert bot2.state.get('name') == 'Bot2State', "Bot2 state doesn't match."

    # Test creating a bot with some default and some specific values
    bot3_config = {
        'id': 'Bot3',
    }
    bot3 = Bot(bot3_config)
    bot3.logger.info("Created bot with mixed values")
    bot3.change_port(Port(bot3.id, {'address': '9090'}))
    assert bot3.id == 'Bot3', "Bot3 id doesn't match."
    assert bot3.port.get_address() == '9090', "Bot3 port doesn't match."
    assert bot3.state is not None, "Bot3 state is None."

def test_bot_methods():
    """
    Test the methods of a bot, including getting and setting the state and memory, and accessing bot items.
    """
    bot = Bot({'id': 'TestBot'})

    # Test the get_state method
    state = bot.get_state()
    bot.logger.info(f"Got state: {state}")
    assert state == bot.state, "get_state method failed."

    # Test the set_state method
    bot.set_state(State({'name': 'NewState'}))
    new_state = bot.get_state()
    bot.logger.info(f"Set and got new state: {new_state}")
    assert new_state.get('name') == 'NewState', "set_state or get_state method failed."

    # Test remember and get_memory methods
    for i in range(3):
        bot.remember(f"Test{i}")
        new_memory = bot.get_memory()
        bot.logger.info(f"Set and got new memory: {new_memory}")
        assert f"Test{i}" in new_memory['short_term'], "remember or get_memory method failed."

    # Test recall method
    assert bot.recall('Test0'), "recall method failed."

    # Test forget method
    bot.forget('Test0')
    assert not bot.recall('Test0'), "forget method failed."

    # Test accessing bot items
    for k, v in bot.__dict__.items():
        if callable(v):
            bot.logger.info(f"{k}: {pprint.pformat(v)}")
        else:
            bot.logger.info(f"{k}: {pprint.pformat(v)}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(filename='testapp.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    # Run tests
    test_bot_creation()
    test_bot_methods()
