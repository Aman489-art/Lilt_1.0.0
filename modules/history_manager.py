# modules/history_manager.py

import json
import os
from datetime import datetime

history_file = "logs/conversation_log.json"

def save_to_history(user, assistant):
    data = {
        "user": user,
        "assistant": assistant,
        "timestamp": datetime.now().isoformat()
    }
    if not os.path.exists("logs"):
        os.makedirs("logs")

    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(data)

    with open(history_file, "w") as f:
        json.dump(history[-50:], f, indent=4)  # Keep last 50

def recall_context(last_n=5):
    if not os.path.exists(history_file):
        return ""
    with open(history_file, "r") as f:
        history = json.load(f)
    
    recent = history[-last_n:]
    lines = []

    for h in recent:
        user = h.get("user", "User")
        assistant = h.get("assistant", "Lily didn't respond.")
        lines.append(f"User: {user}\nLily: {assistant}")

    return "\n".join(lines)
