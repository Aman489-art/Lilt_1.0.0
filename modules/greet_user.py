from datetime import datetime
from modules.tts_output import speak
from modules.ai_engine import *
from modules.weather import *
from modules.system_tasks import news

def greet_user():
    # Get current hour
    hour = datetime.now().hour

    # Decide greeting based on time
    if 5 <= hour < 12:
        time_greeting = "Good morning"
        speak(f"Today {weather_report}")
        speak(f"Today news is : {news}")
    elif 12 <= hour < 17:
        time_greeting = "Good afternoon"
    elif 17 <= hour < 22:
        time_greeting = "Good evening"
    else:
        time_greeting = "It's a peaceful time of the night"

    # Friendly prompt for Lily to generate personalized greeting
    prompt = (
        f"{time_greeting}, Aman! Greet Aman with a short, warm, emotionally uplifting message. "
        "generate a time greeting based welcome message"
        "Make it sound friendly, energetic, and personal — like you're excited to meet him again. "
        "Avoid robotic tone. One line only."
    )

    # Generate and speak the greeting
    greeting = ask_lily(prompt)
    speak(time_greeting)
    speak(greeting)



