import os
import subprocess
import uuid
import time
import hashlib
from pathlib import Path
from gradio_client import Client, handle_file

# S1-mini HuggingFace client
client = Client("fishaudio/openaudio-s1-mini")

# Create cache directory
CACHE_DIR = Path("tts_cache")
CACHE_DIR.mkdir(exist_ok=True)

def speak_openaudio(text, use_cache=True):
    """
    Convert text to speech using OpenAudio S1-mini (HuggingFace).
    
    Args:
        text (str): Text to convert to speech
        use_cache (bool): Whether to use cached audio files
    """
    if not text or not text.strip():
        print("⚠️ Empty text. Skipping TTS.")
        return False

    # Hash text to cache file
    text_hash = hashlib.md5(f"openaudio_{text}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"{text_hash}.wav"

    if use_cache and cache_file.exists():
        print("🎵 Playing cached OpenAudio voice...")
        return play_audio(str(cache_file))

    try:
        #print("⏳ Generating voice using OpenAudio S1-mini...")

        # Call HuggingFace model
        result = client.predict(
            text=text,
            reference_id="Lily-female-01",
            reference_audio=handle_file("/home/aman_mi_938/Lily/tts_cache/7ff088cf781d800e3bd59711bc808b01.mp3"),
            reference_text="",
            max_new_tokens=0,
            chunk_length=0,
            top_p=0.9,
            repetition_penalty=1.1,
            temperature=0.9,
            seed=0,
            use_memory_cache="on",
            api_name="/partial"
        )

        # result is a tuple (audio_path, None)
        audio_path = result[0]

        # Save as cache if needed
        if use_cache:
            os.rename(audio_path, cache_file)
            return play_audio(str(cache_file))
        else:
            return play_audio(audio_path)

    except Exception as e:
        print(f"❌ Error using OpenAudio: {e}")
        return False

def play_audio(filename):
    """Play audio file using ffplay."""
    try:
        result = subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", filename], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            timeout=30
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Audio playback timed out")
        return False
    except FileNotFoundError:
        print("❌ ffplay not found. Install ffmpeg.")
        return False
    except Exception as e:
        print(f"🎵 Audio playback error: {e}")
        return False

def clear_cache():
    """Clear the TTS cache."""
    import shutil
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
        CACHE_DIR.mkdir()
        print("🗑️ TTS cache cleared")

import re

def extract_emotion(text):
    """Detect emotion tag like (angry), (sad) in the beginning of the response."""
    match = re.match(r"\((.*?)\)", text)
    if match:
        emotion = match.group(1)
        clean_text = re.sub(r"^\(.*?\)\s*", "", text)  # Remove emotion tag
        return emotion.lower(), clean_text
    return None, text

def speak(text, use_cache=True):
    """
    Main TTS function using OpenAudio S1-mini with emotion preprocessing.
    Detects emotion from text tag (like (sad)) or uses default.
    """
    if not text or not text.strip():
        print("⚠️ Empty text. Skipping TTS.")
        return False

    emotion, clean_text = extract_emotion(text)

    # Add emotion tag back if detected, so S1 voice reflects it
    final_text = f"({emotion}) {clean_text}" if emotion else clean_text

    print(f"🗣️ Lily says: {clean_text}")
    return speak_openaudio(final_text, use_cache)

def speak_with_fallback(text, use_cache=True):
    """Alias for backward compatibility."""
    return speak(text, use_cache)
