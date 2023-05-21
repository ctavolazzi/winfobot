class Behavior:
    @staticmethod
    def can_handle(type):
        raise NotImplementedError("This method should be overridden in subclass")

    def handle(self, data):
        raise NotImplementedError("This method should be overridden in subclass")

class GreetingBehavior(Behavior):
    def can_handle(self, data):
        return isinstance(data, dict) and data.get('type') == 'Greeting'

    def handle(self, data):
        print(f"Greeting behavior handling data: {data}")


class FarewellBehavior(Behavior):
    def can_handle(self, data):
        return isinstance(data, dict) and data.get('type') == 'Farewell'

    def handle(self, data):
        print(f"Farewell behavior handling data: {data}")


class BehaviorFactory:
    @staticmethod
    def create_behaviors():
        # Create instances of different behaviors
        greeting_behavior = GreetingBehavior()
        farewell_behavior = FarewellBehavior()

        # Return all behaviors in a list
        return [greeting_behavior, farewell_behavior]
