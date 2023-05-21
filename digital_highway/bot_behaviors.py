class Behavior:
    @staticmethod
    def can_handle(type):
        raise NotImplementedError("This method should be overridden in subclass")

    def handle(self, data):
        raise NotImplementedError("This method should be overridden in subclass")

class GreetBehavior(Behavior):
    def can_handle(self, data):
        if isinstance(data, str):
            return data.lower().startswith("hello")
        return False

    def handle(self, data):
        print("Hello to you too!")


class FarewellBehavior(Behavior):
    def can_handle(self, data):
        if isinstance(data, str):
            return data.lower().startswith("goodbye")
        return False

    def handle(self, data):
        print("Goodbye! See you soon!")


class BehaviorFactory:
    @staticmethod
    def create_behaviors():
        return [GreetBehavior(), FarewellBehavior()]
