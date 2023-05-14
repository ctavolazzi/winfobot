import openai
import requests
import uuid
import logging
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class AIGent:
    def __init__(self):
        user_data = self.get_random_user_data()
        self.user_data = user_data

        keys_of_interest = ["name", "login", "dob", "email", "location", "gender"]

        for key in keys_of_interest:
            if key in user_data:
                if isinstance(user_data[key], dict):
                    for sub_key in user_data[key]:
                        setattr(self, f"{key}_{sub_key}", user_data[key][sub_key])
                else:
                    setattr(self, key, user_data[key])

        log_file_name = f"{self.name_first}_{self.login_uuid}.log"

        self.logger = logging.getLogger(f"{__name__}_{self.login_uuid}")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file_name)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info(f"User data: {json.dumps(self.user_data, indent=4)}")

    @staticmethod
    def get_random_user_data():
        response = requests.get('https://randomuser.me/api/')
        if response.status_code == 200:
            data = response.json()
            return data['results'][0]
        else:
            return {}

    @staticmethod
    def get_random_id():
        return str(uuid.uuid4())[:9]

    def chat(self, user_message):
        model = "gpt-3.5-turbo"

        system_message_parts = [f"You are a helpful assistant named {self.name_first} with the ID {self.login_uuid}."]

        for key, value in self.user_data.items():
            if key != 'name' and key != 'id':
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

        user_log_entry = json.dumps({
            'role': 'User',
            'message': user_message,
            'timestamp': datetime.now().isoformat()
        })
        self.logger.info(user_log_entry)

        ai_log_entry = json.dumps({
            'role': 'AI',
            'message': response.choices[0]['message']['content'],
            'timestamp': datetime.now().isoformat()
        })
        self.logger.info(ai_log_entry)

        return response.choices[0]['message']['content']

    def make_decision(self, user_message):
        if 'agree' in user_message:
            decision = 'agree'
        elif 'disagree' in user_message:
            decision = 'disagree'
        else:
            decision = 'uncertain'

        self.log_decision(decision)

        return decision

    def get_agent_info(self):
        return json.dumps(self.user_data, indent=4)

    def log_decision(self, decision):
        self.logger.info(f"Decision: {decision}")
