import uuid
from utils import setup_logger

class State:
    def __init__(self, config=None):
        self.id = str(uuid.uuid4())
        self.state_dict = config if config else {}

        if config:
            for key, value in config.items():
                self.state_dict[key] = value

        # Initialize the logger
        self.logger = setup_logger(self)
        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {config}')

    def get_state(self):
        return self.state_dict

    def get(self, key):
        return self.state_dict.get(key)

    def set_state(self, key, value):
        self.state_dict[key] = value
        self.logger.info(f'Set state: {key} = {value}')

    def update(self, state_dict):
        if not isinstance(state_dict, dict):
            raise TypeError(f"Expected a dictionary, but got {type(state_dict).__name__}")

        # Define a simple validation function for the new keys and values
        def validate(key, value):
            # For example, ensure keys are strings and not empty, and values are not None
            if not isinstance(key, str) or not key:
                self.logger.warning(f"Invalid key: {key}")
                return False
            if value is None:
                self.logger.warning(f"None value for key: {key}")
                return False
            # Add more checks here as needed...

            return True

        # Apply validation to each item in the new state dictionary and update state_dict accordingly
        valid_dict = {k: v for k, v in state_dict.items() if validate(k, v)}

        # Update the state dictionary
        self.state_dict.update(valid_dict)
        self.logger.info(f'Updated state: {valid_dict}')

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        attributes = vars(self)
        lines = [f'State {self.id}']
        for attr, value in attributes.items():
            if attr in {'id', '_password'}:  # Skip these attributes
                continue
            if attr == 'modules':  # For modules, we want to list the module names only
                value = ', '.join(value.keys())
            elif attr == 'port':  # For port and state, we want to use their IDs
                value = value.id
            elif attr == 'logger':  # For logger, we want to display its level
                value = value.level
            elif attr == 'lock':  # For lock, we want to display its state
                value = 'locked' if value.locked() else 'unlocked'
            lines.append(f'{attr}: {value}')
        return '\n'.join(lines)

    def __str__(self):
        return str(self.state_dict)

def main():
    # Create a new State instance with default settings
    state = State()
    print("Created new State with ID: ", state.id)

    # Test State's attributes
    assert state.id is not None, "State's ID should not be None."

    # Test State's get_state method
    assert isinstance(state.get_state(), dict), "State's get_state() should return a dictionary."

    # Test State's set_state method
    state.set_state("test_key", "test_value")
    assert state.get_state()["test_key"] == "test_value", "State's set_state() should correctly set state key-value pairs."

    # Test State's get method
    assert state.get("test_key") == "test_value", "State's get() should correctly get the value for the given key."

    # Test State's update method with valid input
    state.update({"new_key": "new_value"})
    assert state.get("new_key") == "new_value", "State's update() should correctly update state dictionary with valid input."

    # Test State's update method with invalid input
    try:
        state.update({"invalid_key": None})
    except Exception as e:
        print("Successfully caught exception for invalid input to update(): ", e)

if __name__ == '__main__':
    main()