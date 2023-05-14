from flask import Flask, request
from aigent import AIGent
import logging
import os
import json

app = Flask(__name__)
winfo_bot = AIGent()

@app.route('/')
def home():
    return "WinfoBot is up and running!"  # Return a simple string to indicate that the bot is running

@app.route('/winfo', methods=['POST'])
def chat():
    user_message = request.json['content']
    bot_message = winfo_bot.chat(user_message)
    return {'message': f"{winfo_bot.name_first}: {bot_message}"}

@app.route('/logs', methods=['GET'])
def list_logs():
    log_files = os.listdir('path/to/your/log/directory')
    return {'logs': log_files}

@app.route('/logs/<log_file>', methods=['GET'])
def get_log(log_file):
    with open(f'path/to/your/log/directory/{log_file}', 'r') as file:
        log_content = file.readlines()
    return {'log_content': log_content}

if __name__ == '__main__':
    # Get the absolute path of the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the absolute path of the log file
    log_file_path = os.path.join(current_dir, 'flask.log')

    # Create the file handler
    handler = logging.FileHandler(log_file_path)
    handler.setLevel(logging.INFO)  # Set the log level to INFO
    app.logger.addHandler(handler)  # Add the handler to Flask's logger

    # Set Werkzeug's log handlers to be the same as Flask's logger
    log = logging.getLogger('werkzeug')
    log.handlers = app.logger.handlers

    app.run(debug=True)
