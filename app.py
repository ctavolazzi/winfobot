from flask import Flask, request, render_template
from aigent import AIGent
import logging
import os
import json
from dotenv import load_dotenv
from flask_cors import CORS
import openai
import requests

app = Flask(__name__)
agent = AIGent()

@app.route('/')
def home():
    return render_template('index.html')  # Assuming you have a template named index.html

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    agent_message = agent.chat(user_message)
    return {'message': f"{agent.name_first}: {agent_message}"}

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
