import json
from datetime import datetime

def load_log(filename, default_value):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_value

def save_log(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def add_message(log, category, message, max_length=20):
    log[category].append(message)
    if len(log[category]) > max_length:  # Only keep the last max_length messages
        log[category].pop(0)

def load_log(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_log(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def log_message(log_filename, category, message_object):
    log_data = load_log(log_filename)
    if category not in log_data:
        log_data[category] = []
    log_data[category].append(message_object)
    if len(log_data[category]) > 20:  # Only keep the last 20 messages
        log_data[category].pop(0)
    save_log(log_filename, log_data)
