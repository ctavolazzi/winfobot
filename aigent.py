import openai
import requests
import uuid
import logging
import os
import json
from dotenv import load_dotenv
import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class AIGent:
    # def __init__(self):
    #     user_data = self.get_random_user_data()
    #     self.user_data = user_data
    #     self.name = user_data['name']['first']
    #     self.id = user_data['login']['uuid']
    #     self.age = user_data['dob']['age']
    #     self.username = user_data['login']['username']
    #     self.gender = user_data['gender']
    #     self.email = user_data['email']
    #     self.location = user_data['location']
    #     log_file_name = f"{self.name}_{self.id}.log"
    #     logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s %(message)s')
    #     self.logger = logging.getLogger(__name__)




    def __init__(self):
      user_data = self.get_random_user_data()
      self.user_data = user_data

      # List of keys we are interested in
      keys_of_interest = ["name", "login", "dob", "email", "location", "gender"]

      for key in keys_of_interest:
          if key in user_data:
              if isinstance(user_data[key], dict):
                  for sub_key in user_data[key]:
                      setattr(self, f"{key}_{sub_key}", user_data[key][sub_key])
              else:
                  setattr(self, key, user_data[key])

      log_file_name = f"{self.name_first}_{self.login_uuid}.log"

      # Create a logger for this instance
      self.logger = logging.getLogger(f"{__name__}_{self.login_uuid}")
      self.logger.setLevel(logging.INFO)  # Set the log level

      # Create a file handler for this logger
      handler = logging.FileHandler(log_file_name)

      # Create a formatter and set it for the handler
      formatter = logging.Formatter('%(asctime)s %(message)s')
      handler.setFormatter(formatter)

      # Add the handler to the logger
      self.logger.addHandler(handler)

      # Log the agent's user data
      self.logger.info(f"User data: {json.dumps(self.user_data, indent=4)}")



    @staticmethod
    def get_random_user_data():
        """Fetch a random user's data from the 'randomuser.me' API."""
        response = requests.get('https://randomuser.me/api/')
        if response.status_code == 200:
            data = response.json()
            return data['results'][0]
        else:
            return {}

    # Rest of your class code...

    @staticmethod
    def get_random_id():
        """Generate a random UUID and use the first 9 characters as the ID."""
        return str(uuid.uuid4())[:9]

    def chat(self, user_message):
      """
      Use OpenAI's GPT-3.5-turbo model to chat with the user.
      """
      model = "gpt-3.5-turbo"

      # Construct system message by iterating over the user data
      system_message_parts = [f"You are a helpful assistant named {self.name_first} with the ID {self.login_uuid}."]

      for key, value in self.user_data.items():
          if key != 'name' and key != 'id':  # We've already included name and ID
              system_message_parts.append(f"Your {key} is {value}.")
      system_message = " ".join(system_message_parts)

      messages = [
          {"role": "system", "content": system_message},
          {"role": "user", "content": user_message}
      ]

      response = openai.ChatCompletion.create(
          model=model,
          messages=messages,
      )

      # Log the user's message
      user_log_entry = json.dumps({
          'role': 'User',
          'message': user_message,
          'timestamp': datetime.now().isoformat()
      })
      self.logger.info(user_log_entry)

      # Log the AI's response
      ai_log_entry = json.dumps({
          'role': 'AI',
          'message': response.choices[0]['message']['content'],
          'timestamp': datetime.now().isoformat()
      })
      self.logger.info(ai_log_entry)


      return response.choices[0]['message']['content']



    def make_decision(self, user_message):
        """
        Make a decision based on the user's message. This is a simple example
        where the agent will decide to 'agree' if the user_message includes the word 'agree'
        or 'disagree' if it includes the word 'disagree'. This should be replaced with your own
        decision-making logic.
        """
        if 'agree' in user_message:
            decision = 'agree'
        elif 'disagree' in user_message:
            decision = 'disagree'
        else:
            decision = 'uncertain'

        self.log_decision(decision)

        return decision

    def get_agent_info(self):
        """Return the agent's information."""
        return json.dumps(self.user_data, indent=4)

    def log_decision(self, decision):
        """Log the decision made by the agent."""
        self.logger.info(f"Decision: {decision}")
