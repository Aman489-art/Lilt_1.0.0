import os
from datetime import datetime
from modules.tts_output import speak
#import pyautogui
import time
import subprocess 
from modules.music_player import search_youtube_music, play_music_from_url
import psutil 
import brightnessctl
import re 
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
# Import the functions from your reminder system
from modules.reminder_tasks import (
    set_timer
)

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def tell_time():
    now = datetime.now()
    speak(f"The time is {now.strftime('%H:%M')}")

def tell_date():
    today = datetime.now().strftime("%A, %d %B %Y")
    speak(f"Today is {today}")

def open_browser():
    speak("Opening Brave browser.")
    os.system("brave-browser &")

def open_terminal():
    print("Opening terminal.")
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'alt', 't')

def open_calculator():
    speak("Calculator is ready. Type your expression.")
    try:
        expression = input("🧮 Enter math expression: ")
        result = eval(expression)
        speak(f"The result is {result}")
        print(f"Result: {result}")
    except Exception as e:
        speak("Sorry, that expression is invalid.")
        print("Error:", e)

def system_shutdown():
    speak("Shutting down the system. Goodbye!")
    os.system("shutdown now")

def system_restart():
    speak("Restarting the system. Hold tight!")
    os.system("reboot")

def take_note():
    speak("Opening a text editor for notes.")
    os.system("featherpad &")

def check_battery():
    try:
        output = subprocess.getoutput("upower -i $(upower -e | grep BAT) | grep percentage")
        battery_str = output.split(":")[-1].strip().replace('%', '')
        battery_level = int(battery_str)

        if battery_level >= 90:
            message = f"Battery is at {battery_level}%. You're fully charged and ready to go!"
        elif 70 <= battery_level < 90:
            message = f"Battery is at {battery_level}%. You're in a good zone!"
        elif 40 <= battery_level < 70:
            message = f"Battery is at {battery_level}%. Moderate level. You can continue, but keep an eye on it."
        elif 20 <= battery_level < 40:
            message = f"Battery is at {battery_level}%. Consider plugging in soon."
        elif battery_level < 20:
            message = f"Battery is critically low at {battery_level}%. Please plug in your charger immediately!"
        else:
            message = f"Battery level is {battery_level}%."

        print(message)
        speak(message)

    except Exception as e:
        error_msg = "Sorry, I couldn't check the battery status."
        print(error_msg)
        print("Battery check error:", e)
        speak(error_msg)

def check_system_status():
    try:
        # ------------------ DISK USAGE ------------------
        disk_output = subprocess.getoutput("df -h --output=source,size,used,avail,pcent,target | grep '^/'")
        disk_lines = disk_output.strip().split('\n')

        print("📀 Disk Usage Details:")
        speak("Here are your disk usage details.")
        for line in disk_lines:
            parts = line.split()
            if len(parts) >= 6:
                filesystem, size, used, avail, percent, mount = parts
                percent_value = int(percent.replace('%', ''))

                if percent_value < 50:
                    msg = f"Disk {mount} is using {used} of {size}. Plenty of space: {avail} free."
                elif 50 <= percent_value < 75:
                    msg = f"Disk {mount} is at {percent}. Used {used} of {size}. Consider monitoring space."
                elif 75 <= percent_value < 90:
                    msg = f"Warning! Disk {mount} is {percent} full. Only {avail} left."
                else:
                    msg = f"Critical! Disk {mount} is almost full with {percent} used. Just {avail} free. Please clean up!"

                #print(msg)
                speak(msg)

        # ------------------ RAM USAGE ------------------
        ram_output = subprocess.getoutput("free -h | awk 'NR==2'")
        parts = ram_output.split()
        total_ram, used_ram, free_ram = parts[1], parts[2], parts[3]

        print("\n🧠 RAM Usage Details:")
        speak("Now checking memory usage.")
        ram_msg = f"You are using {used_ram} out of {total_ram} RAM. {free_ram} is free."

        #print(ram_msg)
        speak(ram_msg)

        # ========== CPU LOAD ==========
        load1, load5, load15 = psutil.getloadavg()
        cpu_count = psutil.cpu_count()

        load_msg = f"CPU load: {round(load1,2)} over 1 minute. System has {cpu_count} cores."

        if load1 > cpu_count * 0.9:
            load_msg += " High CPU usage detected!"
        #print("🔥", load_msg)
        speak("Checking CPU performance.")
        speak(load_msg)

        # ========== CPU TEMPERATURE ==========
        try:
            sensors_output = subprocess.getoutput("sensors")
            cpu_temp_line = next(line for line in sensors_output.split('\n') if "Package id 0" in line)
            temp_value = cpu_temp_line.split('+')[1].split('°')[0]
            temp = float(temp_value)

            if temp > 80:
                temp_msg = f"Warning! CPU temperature is high at {temp} degrees Celsius."
            else:
                temp_msg = f"CPU temperature is {temp} degrees. All good."

        except Exception:
            temp_msg = "CPU temperature couldn't be read."

        #print("🌡️", temp_msg)
        speak(temp_msg)

    except Exception as e:
        error_msg = "Sorry, I couldn't check the system status."
        print(error_msg)
        print("System check error:", e)
        speak(error_msg)

def handle_music_command():
    speak("What song do you want to play?")
    query = input("🎶 What song do you want to play? ").strip()
    if not query:
        print("⚠️ No song name provided.")
        return True

    results = search_youtube_music(query)
    if not results:
        print("❌ No results found.")
        return True

    print("\n🎧 Search Results:")
    for i, item in enumerate(results):
        print(f"{i+1}. {item['title']}")

    choice = input("\nSelect a song number: ").strip()
    if not choice.isdigit():
        print("⚠️ Invalid input.")
        return True

    choice = int(choice) - 1
    if 0 <= choice < len(results):
        video_url = f"https://www.youtube.com/watch?v={results[choice]['id']}"
        play_music_from_url(video_url)
    else:
        print("⚠️ Number out of range.")

    return True

def set_volume(level=None):
    if level is None:
        speak("Please tell me the volume percentage you want.")
        try:
            level = int(input("🔊 Enter volume percentage (0-100): ").strip())
        except:
            speak("Invalid input.")
            return

    if 0 <= level <= 100:
        os.system(f"amixer -D pulse sset Master {level}%")
        speak(f"Volume set to {level} percent.")
    else:
        speak("Please enter a valid volume between 0 and 100.")

def set_brightness(level=None):
    if level is None:
        speak("Please tell me the brightness percentage you want.")
        try:
            level = int(input("💡 Enter brightness percentage (0-100): ").strip().replace('%', ''))
        except:
            speak("Invalid input.")
            return
     
    if 0 <= level <= 100:
        # Calculate brightness value based on your system's max brightness
        max_brightness = 19200
        brightness_value = int((level / 100) * max_brightness)
        
        # Use the working direct method
        result = os.system(f"echo {brightness_value} | sudo tee /sys/class/backlight/intel_backlight/brightness > /dev/null")
        
        if result == 0:
            speak(f"Brightness set to {level} percent.")
        else:
            speak("Sorry, I couldn't change the brightness. Please check permissions.")
    else:
        speak("Please enter a valid brightness between 0 and 100.")

def clean_junk():
    speak("Cleaning system junk and temporary files.")
    os.system("sudo apt clean && sudo rm -rf /tmp/* ~/.cache/thumbnails/*")
    speak("System cleanup complete.")

def lock_screen():
    speak("Locking the screen.")
    os.system("xdg-screensaver lock")

def take_screenshot(save_to_file=True):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/home/aman_mi_938/Pictures/screenshot_{timestamp}.png"
    
    if save_to_file:
        speak("Taking screenshot and saving it.")
        cmd = f"flameshot full --delay 0 --path {filename}"
    else:
        speak("Taking screenshot to clipboard.")
        cmd = "flameshot gui"

    result = os.system(cmd)

    if result == 0 and save_to_file:
        speak(f"Screenshot saved to your Pictures folder.")
    elif result == 0:
        speak("Screenshot taken to clipboard.")
    else:
        speak("Failed to take screenshot.")

def parse_time_string(time_str):
    try:
        now = datetime.now()
        if "am" in time_str.lower() or "pm" in time_str.lower():
            remind_time = datetime.strptime(time_str, "%I:%M %p")
            return now.replace(hour=remind_time.hour, minute=remind_time.minute, second=0, microsecond=0)
        elif ":" in time_str:
            remind_time = datetime.strptime(time_str, "%H:%M")
            return now.replace(hour=remind_time.hour, minute=remind_time.minute, second=0, microsecond=0)
        else:
            # "6 am" → try adding :00
            time_str += ":00"
            remind_time = datetime.strptime(time_str, "%I:%M %p")
            return now.replace(hour=remind_time.hour, minute=remind_time.minute, second=0, microsecond=0)
    except:
        return None

def get_ip_location():

    try:
        response = requests.get('https://ipinfo.io/json')
        response.raise_for_status()
        data = response.json()
        #print(data)
        ip = data.get('ip')
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
        location = data.get('loc')
        speak(f"You are in {city} city of {region} state in {country}")
        speak(f"Your location address is {location}")
        speak(f"Your ip address is {ip}")


        
        # Return city with country for better context
        if city and country:
            return f"{city}, {country}"
        return city
        
    except requests.RequestException as e:
        print(f"⚠️ IP-based location detection failed: {e}")
        return None
    except json.JSONDecodeError:
        speak("⚠️ Invalid response from location service")
        return None

def wiki_search(query):
    import wikipedia
    wikipedia.set_lang("en")
    try:
        results = wikipedia.search(query)
        if results:
            summary = wikipedia.summary(results[0], sentences=3)
            return summary
        else:
            return "No results found."
    except wikipedia.exceptions.DisambiguationError as e:
        return "Your search is ambiguous. Try being more specific."
    except wikipedia.exceptions.PageError:
        return "The page was not found on Wikipedia."
    except Exception as e:
        return f"Error: {e}"

def news():

    # Your NewsAPI key

    API_KEY = os.getenv("NEWS_API")


    # Base URL for top headlines
    url = 'https://newsapi.org/v2/top-headlines'

    # Combine national and international sources or countries
    params = {
        'apiKey': API_KEY,
        'language': 'en',
        'pageSize': 10,  # You can increase for more results
    }

    # You can also filter by country (e.g. 'in' for India, 'us' for USA)
    # For mixed national + international, we do two requests

    def fetch_news(country=None):
        if country:
            params['country'] = country
        else:
            params.pop('country', None)  # Remove country for global search

        response = requests.get(url, params=params)
        data = response.json()

        if data.get('status') != 'ok':
            return f"❌ Error: {data.get('message', 'Unknown error')}"
        articles = data.get('articles', [])
        
        if not articles:
            return "⚠️ No news articles found."
            
        for i, article in enumerate(data['articles'], 1):
            speak(f"\n{i}. {article['title']}")
            print(f"   📰 Source: {article['source']['name']}")
            print(f"   🔗 URL: {article['url']}")
            speak(f"   📝 {article['description']}\n")


    # Fetch Indian (national) news
    speak("🇮🇳 National News (India):")
    fetch_news(country='in')

    # Fetch Global (international) news
    speak("\n🌐 International News:")
    fetch_news()  # no country = global news

