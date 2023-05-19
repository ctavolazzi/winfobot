import uuid
from datetime import datetime

# def format_message(user_name, user_id, role, content, time=None, message_id=None, ai_response=None):
#     if not message_id:
#         message_id = str(uuid.uuid4())
#     if not time:
#         time = str(datetime.now())
#     return {
#         "message_id": message_id,
#         "username": user_name,
#         "user_id": user_id,
#         "role": role,
#         "content": content,
#         "time": time,
#         "ai_response": ai_response
#     }

def format_message(message, type='None'):
    message_object = {}

    keys_of_interest = ['message_id', 'username', 'user_id', 'role', 'content', 'time']

    for key in keys_of_interest:
        if key not in message:
            message_object[key] = None

    if type == 'assistant':
        message_object['message_id'] = str(uuid.uuid4())
        message_object['username'] = 'Winfo'
        message_object['user_id'] = 'Winfo#8921'
        message_object['role'] = 'assistant'
        message_object['content'] = message
        message_object['time'] = str(datetime.now())

    elif type == 'user':
        message_object['role'] = 'user'
        message_object['content'] = message
        message_object['time'] = str(datetime.now())
        message_object['message_id'] = str(uuid.uuid4())
        if message['username']:
            message_object['username'] = message['username']
        else:
            message_object['username'] = 'Anonymous'
        if message['user_id']:
            message_object['user_id'] = message['user_id']
        else:
            message_object['user_id'] = 'Anonymous#0000'

    else:
        raise ValueError("message type must be either 'assistant' or 'user'")

def check_message(message_object):
    if type(message_object) != dict:
        raise TypeError("message_object must be a dictionary")

    role = message_object['role']

    keys_of_interest = ['message_id', 'username', 'user_id', 'role', 'content', 'time', 'ai_response']

    for key in keys_of_interest:
        if key not in message_object:
            raise KeyError(f"message_object must contain key '{key}'")

    if role not in ['user', 'assistant']:
        raise ValueError("role must be either 'user' or 'assistant'")

    return message_object