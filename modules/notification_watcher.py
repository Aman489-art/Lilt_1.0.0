import subprocess
import json
import os
import time
from dotenv import load_dotenv
from modules.tts_output import speak

load_dotenv()
phone_ssh = os.getenv("SSH_CODE")

# 🧠 Only important package names (you can customize this)
PRIORITY_APPS = {
    "com.whatsapp": "WhatsApp",
    "com.google.android.gm": "Gmail",
    "com.google.android.dialer": "Phone",
    "com.android.mms": "SMS",
    "com.truecaller": "Truecaller"
}

# 📲 Tracks already spoken notifications
seen_notifications = set()

def get_priority_notifications():
    try:
        cmd = f"{phone_ssh} termux-notification-list"
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        data = json.loads(output)
        return data
    except:
        return {}


def watch_notifications_loop(poll_interval=10):
    while True:
        notifications = get_priority_notifications()

        # Handle both dict and list formats safely
        if isinstance(notifications, dict):
            notif_list = list(notifications.values())
        elif isinstance(notifications, list):
            notif_list = notifications
        else:
            notif_list = []

        for notif in notif_list:
            # Create a unique ID using package + title + content
            unique_id = (
                notif.get("package_name", "") + 
                notif.get("title", "") + 
                notif.get("content", "")
            ).strip()

            if unique_id in seen_notifications:
                continue

            package = notif.get("package_name", "")
            title = notif.get("title", "No Title")
            content = notif.get("content", "No Content")

            if package in PRIORITY_APPS:
                app_name = PRIORITY_APPS[package]
                message = f"📲 New {app_name} notification: {title}. {content}"
                speak(message)
                seen_notifications.add(unique_id)

        time.sleep(poll_interval)

