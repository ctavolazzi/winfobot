import time
from bot import Bot
from port import Port
import utils
import uuid

class TestBot(Bot):
    DEFAULT_CONFIG = {
        'id': lambda: str(uuid.uuid4()),
        'test_results': lambda: [],
    }

    DEFAULT_CONFIG_SELF = {
        'type': lambda self: self.__class__.__name__,
        '_base_type': lambda self: self.__class__.__base__.__name__,
        'port': lambda self: Port({'owner': self}),
    }

    def __init__(self, bot_instance=None):
        if bot_instance:
            self.bot_instance = bot_instance
            super().__init__(self.bot_instance)
        else:
            super().__init__()
            self.bot_instance = self

        self.run_default_config() # Always run this first
        self.logger = utils.setup_logger(self, 'DEBUG') # Always run this second

    def run_default_config(self):
        for key, default_value_func in self.DEFAULT_CONFIG.items():
            setattr(self, key, default_value_func())

        for key, default_value_func in self.DEFAULT_CONFIG_SELF.items():
            setattr(self, key, default_value_func(self))

    # rest of your code...

    # rest of your code ...

    def _begin_test(self, test_name):
        print(f"Running {test_name}...")

    def _end_test(self, test_name, status):
        if status:
            self.test_results.append(True)
            print(f"{test_name}: PASS")
        else:
            self.test_results.append(False)
            print(f"{test_name}: FAIL")

    def test_id(self):
        self._begin_test("test_id")
        status = isinstance(self.bot_instance.id, str)
        self._end_test("test_id", status)

    def test_port(self):
        self._begin_test("test_port")
        status = isinstance(self.bot_instance.port, Port) and self.bot_instance.port.owner.id == self.bot_instance.id
        self._end_test("test_port", status)

    # Continue defining the tests here

    def run_all_tests(self):
        start_time = time.time()

        # Run all tests
        self.test_id()
        self.test_port()

        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results)
        failed_tests = total_tests - passed_tests

        print("\n-----TEST SUMMARY-----")
        print(f"Total tests run: {total_tests}")
        print(f"Tests passed: {passed_tests}")
        print(f"Tests failed: {failed_tests}")
        print(f"Test run duration: {time.time() - start_time} seconds")

if __name__ == '__main__':
    my_bot = Bot()
    test_bot = TestBot(my_bot)
    test_bot.run_all_tests()
