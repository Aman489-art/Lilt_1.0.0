from modules.config import GEMINI_API_KEY
import json
import google.generativeai as genai
import time

genai.configure(api_key=GEMINI_API_KEY)

# Define models
PRIMARY_MODEL = "gemini-2.0-flash-exp"
FALLBACK_MODEL = "gemini-2.5-flash-lite"

# Cooldown settings (in seconds)
COOLDOWN_DURATION = 60  # You can change to 120 for 2 minutes, etc.
last_failure_time = 0  # Timestamp of last failure

# Load system prompt
path = "//home//aman_mi_938//Lily//modules//lily_prompt.json"
def load_lily_prompt():
    with open(path, "r") as file:
        prompt_data = json.load(file)

    full_prompt = prompt_data["persona"] + "\n\n"
    for section in prompt_data:
        if section == "persona":
            continue
        elif isinstance(prompt_data[section], list):
            full_prompt += "\n".join(prompt_data[section]) + "\n\n"

    return full_prompt.strip()

lily_system_prompt = load_lily_prompt()

# Create chat session
def create_chat(model_name):
    model = genai.GenerativeModel(model_name)
    return model.start_chat(history=[{"role": "user", "parts": [lily_system_prompt]}])

# Initialize chat sessions
primary_chat = create_chat(PRIMARY_MODEL)
fallback_chat = create_chat(FALLBACK_MODEL)

def ask_lily(prompt: str) -> str:
    global last_failure_time
    prompt = prompt.strip()
    if not prompt:
        return ""

    now = time.time()
    in_cooldown = now - last_failure_time < COOLDOWN_DURATION

    # Decide which model to use
    if not in_cooldown:
        try:
            response = primary_chat.send_message(prompt)
            reply = response.text.strip()
            if reply:
                return reply
            else:
                raise Exception("Empty reply from primary model.")
        except Exception as e:
            print("⚠️ Primary model failed. Switching to fallback for a while.")
            last_failure_time = time.time()  # Start cooldown

    else:
        print("⏳ Primary model in cooldown. Using fallback...")

    # Fallback execution
    try:
        response = fallback_chat.send_message(prompt)
        reply = response.text.strip()
        if reply:
            return reply
        else:
            return "I'm having trouble answering right now. Please try again later."
    except Exception:
        print("❌ Fallback model also failed.")
        return "Sorry, I couldn't respond due to temporary issues."
