import os
import sys
import subprocess
import speech_recognition as sr
import pyttsx3
from contextlib import contextmanager
from modules.interrupt_handler import *


# ==============================
# CONFIG
# ==============================

DEVICE_INDEX = 1

# ==============================
# SYSTEM UTILS
# ==============================

@contextmanager
def suppress_stderr():
    """Temporarily suppress stderr (e.g., ALSA warnings)."""
    original_stderr_fd = sys.stderr.fileno()
    saved_stderr_fd = os.dup(original_stderr_fd)
    try:
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, original_stderr_fd)
        os.close(devnull_fd)
        yield
    finally:
        os.dup2(saved_stderr_fd, original_stderr_fd)
        os.close(saved_stderr_fd)


# ==============================
# VOICE RECOGNITION
# ==============================

recognizer = sr.Recognizer()

def listen_for_command():
    """Listen for a voice command with clean logic and simple timing."""
    with suppress_stderr():
        with sr.Microphone(device_index=DEVICE_INDEX) as source:
            print("\n🎤 Listening...")


            if get_interrupt_flag():
                print("🛑 Interrupt flag set — aborting listen.")
                return ""
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

            except sr.WaitTimeoutError:
                # If speech already started and silence is more than 5 sec, break
                return None
            except Exception as e:
                print(f"⚠️ Mic error: {e}")
                return None


    try:
        print("🔎 Recognizing speech...")
        text = recognizer.recognize_google(audio)
        print(f"🗣 You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        #print("❓ Couldn't understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"🚫 API error: {e}")
        return None

