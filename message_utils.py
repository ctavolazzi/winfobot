import uuid
from datetime import datetime

def format_message(user_name, user_id, role, content, time=None, message_id=None, ai_response=None):
    if not message_id:
        message_id = str(uuid.uuid4())
    if not time:
        time = str(datetime.now())
    return {
        "message_id": message_id,
        "username": user_name,
        "user_id": user_id,
        "role": role,
        "content": content,
        "time": time,
        "ai_response": ai_response
    }
