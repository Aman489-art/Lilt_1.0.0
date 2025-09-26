import time
from datetime import datetime
from modules.tts_output import *
from modules.reminder_tasks import *
from modules.task_manager import *
from threading import Thread

reminder_shown = set()
task_shown = set()

def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M")

def check_reminders_loop():
    while True:
        try:
            now = datetime.now()
            current_time_str = format_time(now)

            # 🔔 Check reminders
            reminders = load_reminders()
            for r in reminders:
                r_time = r.get("time")
                task = r.get("task")
                if r_time and format_time(datetime.strptime(r_time, "%Y-%m-%d %H:%M:%S")) == current_time_str:
                    uid = f"{task}_{r_time}"
                    if uid not in reminder_shown:
                        speak(f"⏰ Reminder: {task}")
                        reminder_shown.add(uid)

            # ✅ Check tasks
            tasks = load_tasks()
            for t in tasks:
                t_due = t.get("due")
                t_desc = t.get("description")
                if t_due and format_time(datetime.strptime(t_due, "%Y-%m-%d %H:%M:%S")) == current_time_str:
                    uid = f"{t_desc}_{t_due}"
                    if uid not in task_shown:
                        speak(f"📝 Task Due: {t_desc}")
                        task_shown.add(uid)

            time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            from modules.error_logger import log_error
            log_error(e, context="Reminder Watcher")
            time.sleep(60)
