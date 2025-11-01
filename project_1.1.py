import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pyttsx3
import random
import time
import os
import wikipedia
from datetime import datetime
import webbrowser
import re
import requests
import threading

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 180)

# Conversation context
conversation_history = []
user_name = None
reminders = []

def speak(text, rate=1.3):
    """Text-to-speech with adjustable rate"""
    engine.setProperty('rate', int(180 * rate))
    engine.say(text)
    engine.runAndWait()

def bot_say(text, rate=1.3):
    """Print and speak bot responses"""
    print(f"🤖 Bot: {text}")
    speak(text, rate)
    conversation_history.append(("bot", text))

def take_command(duration=4):
    """Capture and recognize voice input with improved error handling"""
    r = sr.Recognizer()
    r.energy_threshold = 4000  # Adjust for background noise
    r.dynamic_energy_threshold = True
    temp_file = "temp_audio.wav"
    fs = 44100

    print("🎤 Listening...")
    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        sf.write(temp_file, audio, fs)

        with sr.AudioFile(temp_file) as source_audio:
            r.adjust_for_ambient_noise(source_audio, duration=0.5)
            audio_content = r.record(source_audio)
        
        print("🔍 Recognizing...")
        query = r.recognize_google(audio_content, language='en-in')
        print(f"👤 You: {query}")
        conversation_history.append(("user", query))
        return query.lower()
    
    except sr.UnknownValueError:
        responses = [
            "I didn't quite catch that. Could you repeat?",
            "Sorry, I missed that. Say it again?",
            "Hmm, I didn't understand. One more time?"
        ]
        bot_say(random.choice(responses))
        return ""
    except Exception as e:
        bot_say("I'm having trouble hearing you right now.")
        return ""
    finally:
        try:
            os.remove(temp_file)
        except:
            pass

def get_user_name():
    """Ask and remember user's name"""
    global user_name
    bot_say("By the way, what should I call you?")
    name = take_command()
    if name:
        # Extract likely name (first capitalized word)
        words = name.split()
        for word in words:
            if len(word) > 2 and word not in ['my', 'name', 'is', 'call', 'me']:
                user_name = word.capitalize()
                break
        if user_name:
            responses = [
                f"Nice to meet you, {user_name}!",
                f"Great! I'll remember that, {user_name}.",
                f"{user_name}! What a lovely name."
            ]
            bot_say(random.choice(responses))
        else:
            bot_say("Alright, I'll just call you friend!")
            user_name = "friend"
    else:
        user_name = "friend"

def tell_joke():
    """Tell interactive jokes"""
    jokes = [
        ("Why don't programmers like nature?", "Because it has too many bugs!", "🐛"),
        ("Why did the computer go to the doctor?", "Because it caught a virus!", "🦠"),
        ("What do you call a programmer from Finland?", "Nerdic!", "🇫🇮"),
        ("Why do Java developers wear glasses?", "Because they can't C sharp!", "👓"),
        ("How many programmers does it take to change a light bulb?", "None. It's a hardware problem!", "💡"),
        ("Why did the developer go broke?", "Because they used up all their cache!", "💰"),
        ("What's a programmer's favorite hangout place?", "Foo Bar!", "🍺"),
    ]
    setup, punchline, emoji = random.choice(jokes)
    
    bot_say(setup)
    time.sleep(0.5)
    bot_say("Want to guess?", rate=1.2)
    
    # Give user time to respond
    response = take_command(duration=3)
    
    if response:
        reactions = [
            "Haha, creative guess!",
            "Nice try!",
            "Interesting answer!",
            "That's a good one too!"
        ]
        bot_say(random.choice(reactions))
    
    time.sleep(0.3)
    bot_say(f"{punchline} {emoji}")

def tell_time():
    """Tell current time conversationally"""
    current_time = datetime.now().strftime("%I:%M %p")
    responses = [
        f"It's {current_time} right now.",
        f"The time is {current_time}.",
        f"Right now it's {current_time}."
    ]
    bot_say(random.choice(responses))

def tell_date():
    """Tell current date conversationally"""
    current_date = datetime.now().strftime("%B %d, %Y")
    day = datetime.now().strftime("%A")
    bot_say(f"Today is {day}, {current_date}.")

def search_wikipedia(topic):
    """Search Wikipedia with better error handling"""
    if not topic:
        bot_say("What would you like me to search for?")
        topic = take_command()
    
    if topic:
        bot_say(f"Let me look up {topic} for you...")
        try:
            result = wikipedia.summary(topic, sentences=3, auto_suggest=True)
            bot_say("Here's what I found:")
            bot_say(result)
        except wikipedia.exceptions.DisambiguationError as e:
            bot_say(f"There are multiple results for {topic}. Could you be more specific?")
        except wikipedia.exceptions.PageError:
            bot_say(f"I couldn't find anything about {topic} on Wikipedia.")
        except:
            bot_say("Sorry, I'm having trouble accessing Wikipedia right now.")
    else:
        bot_say("I didn't catch what to search for.")

def open_website(query):
    """Open websites based on command"""
    if 'youtube' in query:
        bot_say("Opening YouTube for you!")
        webbrowser.open("https://www.youtube.com")
    elif 'google' in query:
        bot_say("Opening Google!")
        webbrowser.open("https://www.google.com")
    elif 'github' in query:
        bot_say("Opening GitHub!")
        webbrowser.open("https://www.github.com")
    else:
        search_term = query.replace('search', '').replace('google', '').strip()
        if search_term:
            bot_say(f"Searching for {search_term}...")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
        else:
            bot_say("What should I search for?")

def calculate(query):
    """Simple calculator function"""
    try:
        # Extract mathematical expression
        expression = query.replace('calculate', '').replace('what is', '').replace('plus', '+').replace('minus', '-').replace('times', '*').replace('multiplied by', '*').replace('divided by', '/').strip()
        
        # Simple evaluation (be careful with eval in production!)
        result = eval(expression)
        bot_say(f"The answer is {result}")
    except:
        bot_say("I couldn't calculate that. Try saying something like 'calculate 5 plus 3'")

def get_weather(city=None):
    """Fetch weather information using wttr.in (no API key needed)"""
    
    if not city:
        bot_say("Which city's weather would you like to know?")
        city_response = take_command()
        if city_response:
            # Extract city name
            city = city_response.replace('weather', '').replace('in', '').replace('of', '').strip()
        else:
            city = "Mumbai"  # Default city
    
    try:
        # Using wttr.in - free weather service, no API key needed
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Extract weather information
        current = data['current_condition'][0]
        temp = current['temp_C']
        feels_like = current['FeelsLikeC']
        description = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind_speed = current['windspeedKmph']
        
        weather_info = f"The weather in {city} is {description}. "
        weather_info += f"Temperature is {temp} degrees Celsius, but it feels like {feels_like} degrees. "
        weather_info += f"Humidity is {humidity} percent, and wind speed is {wind_speed} kilometers per hour."
        
        bot_say(weather_info)
    
    except requests.exceptions.Timeout:
        bot_say("The weather service is taking too long to respond. Please try again later.")
    except requests.exceptions.ConnectionError:
        bot_say("I'm having trouble connecting to the weather service. Check your internet connection.")
    except KeyError:
        bot_say(f"I couldn't find weather information for {city}. Please check the city name.")
    except Exception as e:
        bot_say("I couldn't fetch the weather right now. Please try again later.")
        print(f"Weather Error: {e}")


def set_reminder(query):
    """Set a reminder with time delay"""
    bot_say("What should I remind you about?")
    task = take_command()
    
    if not task:
        bot_say("I didn't catch what to remind you about.")
        return
    
    bot_say("In how many minutes should I remind you?")
    time_str = take_command()
    
    try:
        # Extract number from speech
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            minutes = int(numbers[0])
            bot_say(f"Okay! I'll remind you about '{task}' in {minutes} minute{'s' if minutes > 1 else ''}.")
            
            reminder_info = {
                'task': task,
                'minutes': minutes,
                'set_time': datetime.now()
            }
            reminders.append(reminder_info)
            
            def remind():
                time.sleep(minutes * 60)
                bot_say(f"⏰ Reminder: {task}")
                if reminder_info in reminders:
                    reminders.remove(reminder_info)
            
            threading.Thread(target=remind, daemon=True).start()
        else:
            bot_say("I didn't get the time correctly. Please say a number like '5 minutes'.")
    except Exception as e:
        bot_say("I couldn't set the reminder. Please try again.")
        print(f"Reminder Error: {e}")

def list_reminders():
    """List all active reminders"""
    if not reminders:
        bot_say("You don't have any active reminders.")
    else:
        bot_say(f"You have {len(reminders)} active reminder{'s' if len(reminders) > 1 else ''}:")
        for i, reminder in enumerate(reminders, 1):
            elapsed = (datetime.now() - reminder['set_time']).seconds // 60
            remaining = reminder['minutes'] - elapsed
            bot_say(f"{i}. {reminder['task']} - {remaining} minutes remaining")

def play_music():
    """Play music from specified directory"""
    # Change this path to your music folder
    music_dir = os.path.expanduser("~/Music")  # Default music folder
    
    # Alternative paths you can try:
    # Windows: "C:\\Users\\YourUsername\\Music"
    # Mac/Linux: "/home/yourusername/Music"
    
    if not os.path.exists(music_dir):
        bot_say("I couldn't find your music folder. Please update the music directory path in the code.")
        print(f"Music directory not found: {music_dir}")
        return
    
    try:
        # Get all music files (mp3, wav, flac, m4a)
        music_files = [f for f in os.listdir(music_dir) 
                      if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
        
        if music_files:
            song = random.choice(music_files)
            song_path = os.path.join(music_dir, song)
            bot_say(f"Playing {song.replace('.mp3', '').replace('.wav', '')} for you!")
            
            # Open with default music player
            if os.name == 'nt':  # Windows
                os.startfile(song_path)
            elif os.name == 'posix':  # Mac/Linux
                os.system(f'open "{song_path}"' if os.uname().sysname == 'Darwin' 
                         else f'xdg-open "{song_path}"')
        else:
            bot_say(f"I couldn't find any music files in {music_dir}. Please add some songs there!")
    
    except Exception as e:
        bot_say("I encountered an error while trying to play music.")
        print(f"Music Error: {e}")

def wish_user():
    """Greet user based on time of day"""
    hour = int(time.strftime('%H'))
    if 0 <= hour < 12:
        greeting = "Good Morning!"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon!"
    elif 17 <= hour < 21:
        greeting = "Good Evening!"
    else:
        greeting = "Good Night!"
    
    bot_say(greeting)
    bot_say("I'm your smart assistant, ready to help!")
    
    # Get user's name for personalization
    get_user_name()

def show_help():
    """Show available commands"""
    bot_say("Here's what I can do:")
    commands = [
        "🤣 Tell jokes",
        "📚 Search Wikipedia",
        "⏰ Tell time and date",
        "🌐 Open websites like YouTube and Google",
        "🔢 Do simple calculations",
        "🔍 Search the web",
        "🌤️ Get weather information",
        "⏰ Set reminders",
        "🎵 Play music"
    ]
    for cmd in commands:
        print(f"   {cmd}")
    bot_say("Just ask me anything!")

def main():
    """Main conversation loop"""
    wish_user()
    
    # Interaction counter for personality
    interaction_count = 0
    
    while True:
        query = take_command()
        interaction_count += 1
        
        if not query:
            continue
        
        # Personalized greeting
        name_prefix = f"{user_name}, " if user_name and random.random() > 0.7 else ""
        
        # Wikipedia search
        if 'wikipedia' in query or 'wiki' in query:
            topic = query.replace("wikipedia", "").replace("wiki", "").replace("search", "").strip()
            search_wikipedia(topic)
        
        # Jokes
        elif 'joke' in query or 'funny' in query or 'laugh' in query:
            tell_joke()
        
        # Time
        elif 'time' in query:
            tell_time()
        
        # Date
        elif 'date' in query or 'today' in query:
            tell_date()
        
        # Weather
        elif 'weather' in query or 'temperature' in query:
            city = query.replace('weather', '').replace('temperature', '').replace('in', '').replace('of', '').strip()
            get_weather(city if city else None)
        
        # Reminders - Set
        elif 'remind' in query or 'reminder' in query:
            if 'list' in query or 'show' in query or 'what are' in query:
                list_reminders()
            else:
                set_reminder(query)
        
        # Music
        elif 'play music' in query or 'play song' in query or 'music' in query:
            play_music()
        
        # Open websites
        elif 'open' in query or 'youtube' in query or 'google' in query:
            open_website(query)
        
        # Web search
        elif 'search' in query:
            open_website(query)
        
        # Calculator
        elif 'calculate' in query or 'plus' in query or 'minus' in query or ('what is' in query and any(char.isdigit() for char in query)):
            calculate(query)
        
        # Help
        elif 'help' in query or 'what can you do' in query or 'commands' in query:
            show_help()
        
        # How are you
        elif 'how are you' in query or 'how do you do' in query:
            responses = [
                "I'm doing great! Thanks for asking.",
                "I'm excellent! How about you?",
                "Fantastic! Ready to help you.",
                "I'm wonderful! What can I do for you?"
            ]
            bot_say(random.choice(responses))
        
        # Thank you
        elif 'thank' in query:
            responses = [
                f"You're welcome, {name_prefix}!",
                "Happy to help!",
                "Anytime!",
                "My pleasure!"
            ]
            bot_say(random.choice(responses))
        
        # Exit commands
        elif any(word in query for word in ['exit', 'quit', 'bye', 'goodbye', 'see you']):
            farewells = [
                f"Goodbye, {user_name}! Have a wonderful day!",
                f"See you later, {user_name}!",
                f"Take care, {user_name}!",
                f"Bye {user_name}! Come back soon!"
            ]
            bot_say(random.choice(farewells))
            break
        
        # Small talk responses
        elif 'your name' in query:
            bot_say("I'm your smart assistant. You can call me whatever you like!")
        
        elif 'who are you' in query or 'what are you' in query:
            bot_say("I'm your AI voice assistant, here to make your life easier!")
        
        # Default response with encouragement
        else:
            responses = [
                "I'm not sure how to help with that yet, but I'm learning every day!",
                "Hmm, I don't have that feature yet. Try asking for help to see what I can do!",
                "I'm still learning that. Ask me to tell a joke or search Wikipedia!",
                f"I didn't understand that, {name_prefix}. Say 'help' to see what I can do."
            ]
            bot_say(random.choice(responses))
        
        # Occasional engagement prompts
        if interaction_count % 5 == 0:
            prompts = [
                "What else can I help you with?",
                "Anything else you need?",
                "I'm here if you need more help!"
            ]
            bot_say(random.choice(prompts))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        bot_say("Shutting down. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")
        bot_say("I encountered an error. Please restart me.")