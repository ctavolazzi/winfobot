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

class BehaviorHandler:
    def __init__(self, owner):
        self.owner = owner
        self.behaviors = []

    def add_behavior(self, behavior):
        """Adds a behavior to the bot"""
        if isinstance(behavior, Behavior):
            self.behaviors.append(behavior)
            self.owner.logger.info(f"Added behavior: {type(behavior).__name__}")
        else:
            raise TypeError(f"The provided behavior must be an instance of the 'Behavior' class.")

    def remove_behavior(self, behavior):
        """Removes a behavior from the bot"""
        if behavior in self.behaviors:
            self.behaviors.remove(behavior)
            self.owner.logger.info(f"Removed behavior: {type(behavior).__name__}")
        else:
            raise ValueError(f"The provided behavior is not in the bot's behavior list.")

    def execute_behaviors(self):
        """Executes all behaviors of the bot"""
        for behavior in self.behaviors:
            try:
                behavior.execute(self.owner)
            except Exception as e:
                self.owner.logger.error(f"Error executing behavior {type(behavior).__name__}: {str(e)}")