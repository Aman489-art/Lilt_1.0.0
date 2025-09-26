# modules/interrupt_handler.py
# modules/interrupt_handler.py

from pynput import keyboard as kb
import threading


stop_flag = False

def reset_interrupt_flag():
    global stop_flag
    stop_flag = False

def get_interrupt_flag():
    return stop_flag

def keyboard_interrupt_listener():
    def on_press(key):
        global stop_flag
        try:
            if key.char == 'q':
                print("❌ Keyboard Interrupt Detected (Q pressed)")
                stop_flag = True
                return False  # Stop listener
        except AttributeError:
            pass  # handle special keys if needed

    with kb.Listener(on_press=on_press) as listener:
        listener.join()

def start_interrupt_listeners(keyboard_only=True):
    reset_interrupt_flag()
    threading.Thread(target=keyboard_interrupt_listener, daemon=True).start()

def voice_interrupt_listener():
    global stop_flag
    while voice_enabled:
        query = listen_for_command()
        if "stop" in query.lower() or "cancel" in query.lower():
            print("🗣️ Voice Interrupt Detected")
            stop_flag = True
            break


