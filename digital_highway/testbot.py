import time
from bot import Bot
from port import Port

class TestBot(Bot):
    def __init__(self, bot_instance=None):
        if bot_instance:
            self.bot_instance = bot_instance
        else:
            super().__init__()
            self.bot_instance = self
        self.test_results = []

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
