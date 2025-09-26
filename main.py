from modules.voice_input import *
from modules.tts_output import *
from modules.ai_engine import ask_lily
from modules.lily_memory import save_important_point
from modules.handle_command import *
from modules.reminder_tasks import *
from modules.emotion_analyser import get_sentiment
from modules.history_manager import *
from modules.task_manager import *
from modules.log_writer import log_conversation
from modules.interrupt_handler import *
from modules.greet_user import *
from modules.reminider_watcher import check_reminders_loop
from modules.error_logger import log_error
from threading import Thread
from modules.notification_watcher import watch_notifications_loop
from datetime import datetime
import random
import speech_recognition as sr 


def pre_adjust_microphone():
    with suppress_stderr():

        with sr.Microphone(device_index=1) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)


def preload_system_data():
    try:
        print("📦 Preloading system data...")
        pre_adjust_microphone()

        # Load reminders, alarms, etc.
        load_alarms()
        load_reminders()

        # Load tasks
        tasks = load_tasks()
        print(f"📝 {len(tasks)} tasks loaded.")

        # Load calendar events
        events = load_events()
        print(f"📅 {len(events)} calendar events loaded.")

        # Load conversation context
        context = recall_context(last_n=5)
        print(f"🧠 Conversation context loaded: {context[:50]}...")

        print("✅ All systems ready.")
    except Exception as e:
        log_error(e, context="System Preload", extra="Error during initial data load")
        print("⚠️ Preload error occurred.")


def main():
    VERSION = "Lily 1.0.0"
    print(f"🌸 Starting Lily — Version {VERSION}")
    #speak(f"Hello Aman, I’m Lily version {VERSION}, ready to help you.")

    greet_user()
    Thread(target=watch_notifications_loop, daemon=True).start()
    Thread(target=check_reminders_loop, daemon=True).start()
    start_interrupt_listeners(keyboard_only=True)

    lily_sleeping = False
    print("👂 Lily is awake and listening...")

    while True:
        try:
            if get_interrupt_flag():
                speak("Command stopped.")
                reset_interrupt_flag()
                continue

            # Sleep Mode
            if lily_sleeping:
                query = listen_for_command()
                if query and any(kw in query.lower() for kw in ["wake up lily", "hey lily", "lily come back"]):
                    lily_sleeping = False
                    speak("I'm back! How can I help you?")
                    continue
                else:
                    continue  # Stay sleeping

            # Normal Listening
            query = listen_for_command()

            if not query:
                continue

            query = query.strip().lower()

            if "sleep now" in query:
                speak("Okay, I'll rest. Say 'wake up Lily' when you need me.")
                lily_sleeping = True
                continue

            if get_interrupt_flag():
                speak("Command stopped.")
                reset_interrupt_flag()
                continue

            if any(word in query for word in ["exit", "quit", "stop listening"]):
                speak("Okay, shutting down. Take care!")
                break

            if "remember" in query:
                point = query.replace("remember", "").strip()
                if point:
                    save_important_point(point, source="user")
                    speak("Got it! I'll keep that in mind.")
                    save_to_history(query, "Remembered: " + point)
                continue

            if handle_command(query):
                save_to_history(query, "[System Command Executed]")
                continue
            elif fuzzy_handle_command(query):
                save_to_history(query, f"[Fuzzy Command Matched]")
                continue

            sentiment = get_sentiment(query)
            context = recall_context(last_n=5)

            prompt = f"User seems {sentiment}. Continue the conversation naturally.\nPrevious: {context}\n\nUser: {query}"
            response = ask_lily(prompt)

            if response:
                ai_emotion, _ = extract_emotion(response)
                if not ai_emotion:
                    ai_emotion = get_sentiment(response)
                speak(f"({ai_emotion}) {response}")

        except Exception as e:
            print("Caught an error, no worries.")
            log_error(e, context="Main Loop", extra=f"Last query: {query if 'query' in locals() else 'N/A'}")



if __name__ == "__main__":
    preload_system_data()
    main()
