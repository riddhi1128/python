'''
General Conversation & Help
"Hello"
"What can you do?"
"Help"
"Who are you?"
"How are you?"
"Thank you"
"Bye" / "Exit" / "Quit"
Wikipedia & Information Search
"Search Wikipedia for Albert Einstein"
"Tell me about Python programming from Wikipedia"
"Wikipedia Tesla"
"Search Wikipedia"
Jokes and Fun
"Tell me a joke"
"Say something funny"
"Make me laugh"
Time and Date
"What is the time?"
"Tell me the time"
"What’s the date today?"
"Which day is it?"
Weather
"What's the weather?"
"Weather in Mumbai"
"Is it raining in Delhi?"
"Temperature in Bangalore"
Reminders
"Set a reminder"
"Remind me to call mom in 10 minutes"
"List reminders"
"Show my reminders"
Calculations
"Calculate 5 plus 8"
"What is 10 divided by 2?"
"Calculate seven times three"
Music
"Play music"
"Play a song"
"Turn on some music"
Opening and Searching Websites
"Open Google"
"Open YouTube"
"Open GitHub"
"Search for latest news"
"Google for skincare routine tips"
'''
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

# Initialize text-to-speech with error handling
def init_engine():
    """Initialize pyttsx3 engine with proper settings"""
    try:
        engine = pyttsx3.init('sapi5')  # Windows
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        return engine
    except:
        try:
            engine = pyttsx3.init()  # Other OS
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 1.0)
            return engine
        except Exception as e:
            print(f"Engine initialization error: {e}")
            return None

engine = init_engine()

# Conversation context
conversation_history = []
user_name = None
reminders = []

def speak(text, rate=1.3):
    """Text-to-speech with adjustable rate and error handling"""
    global engine
    try:
        if engine is None:
            engine = init_engine()
            if engine is None:
                print("Speech engine not available")
                return
        
        engine.stop()  # Clear queue
        engine.setProperty('rate', int(180 * rate))
        engine.say(text)
        engine.runAndWait()
        
    except RuntimeError as e:
        print(f"Runtime error in speech: {e}")
        # Reinitialize and retry
        engine = init_engine()
        if engine:
            try:
                engine.say(text)
                engine.runAndWait()
            except:
                pass
    except Exception as e:
        print(f"Speech error: {e}")

def bot_say(text, rate=1.3):
    """Print and speak bot responses with long text handling"""
    print(f"🤖 Bot: {text}")
    
    # Split very long text into manageable chunks
    if len(text) > 250:
        # Split by sentences
        sentences = []
        for delimiter in ['. ', '! ', '? ']:
            if delimiter in text:
                parts = text.split(delimiter)
                for i, part in enumerate(parts[:-1]):
                    sentences.append(part + delimiter.strip())
                if parts[-1]:
                    sentences.append(parts[-1])
                break
        
        if not sentences:
            sentences = [text]
        
        for sentence in sentences:
            if sentence.strip():
                speak(sentence.strip(), rate)
                time.sleep(0.3)
    else:
        speak(text, rate)
    
    conversation_history.append(("bot", text))

def take_command(duration=4):
    """Capture and recognize voice input with improved error handling"""
    r = sr.Recognizer()
    r.energy_threshold = 4000
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
            result = wikipedia.summary(topic, sentences=2, auto_suggest=True)
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
        expression = query.replace('calculate', '').replace('what is', '').replace('plus', '+').replace('minus', '-').replace('times', '*').replace('multiplied by', '*').replace('divided by', '/').strip()
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
            city = city_response.replace('weather', '').replace('in', '').replace('of', '').strip()
        else:
            city = "Mumbai"
    
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        current = data['current_condition'][0]
        temp = current['temp_C']
        feels_like = current['FeelsLikeC']
        description = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        
        weather_info = f"The weather in {city} is {description}. "
        weather_info += f"Temperature is {temp} degrees Celsius, feels like {feels_like}. "
        weather_info += f"Humidity is {humidity} percent."
        
        bot_say(weather_info)
    
    except requests.exceptions.Timeout:
        bot_say("The weather service is taking too long to respond.")
    except requests.exceptions.ConnectionError:
        bot_say("Check your internet connection.")
    except KeyError:
        bot_say(f"I couldn't find weather information for {city}.")
    except Exception as e:
        bot_say("I couldn't fetch the weather right now.")
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
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            minutes = int(numbers[0])
            bot_say(f"Okay! I'll remind you in {minutes} minutes.")
            
            reminder_info = {
                'task': task,
                'minutes': minutes,
                'set_time': datetime.now()
            }
            reminders.append(reminder_info)
            
            def remind():
                time.sleep(minutes * 60)
                bot_say(f"Reminder: {task}")
                if reminder_info in reminders:
                    reminders.remove(reminder_info)
            
            threading.Thread(target=remind, daemon=True).start()
        else:
            bot_say("I didn't get the time correctly.")
    except Exception as e:
        bot_say("I couldn't set the reminder.")
        print(f"Reminder Error: {e}")

def list_reminders():
    """List all active reminders"""
    if not reminders:
        bot_say("You don't have any active reminders.")
    else:
        bot_say(f"You have {len(reminders)} active reminders.")
        for i, reminder in enumerate(reminders, 1):
            elapsed = (datetime.now() - reminder['set_time']).seconds // 60
            remaining = reminder['minutes'] - elapsed
            bot_say(f"Number {i}. {reminder['task']}. {remaining} minutes remaining.")

def play_music():
    """Play music from specified directory"""
    music_dir = os.path.expanduser("~/Music")
    
    if not os.path.exists(music_dir):
        bot_say("I couldn't find your music folder.")
        return
    
    try:
        music_files = [f for f in os.listdir(music_dir) 
                      if f.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg'))]
        
        if music_files:
            song = random.choice(music_files)
            song_path = os.path.join(music_dir, song)
            bot_say(f"Playing music for you!")
            
            if os.name == 'nt':
                os.startfile(song_path)
            elif os.name == 'posix':
                os.system(f'open "{song_path}"' if os.uname().sysname == 'Darwin' 
                         else f'xdg-open "{song_path}"')
        else:
            bot_say("I couldn't find any music files.")
    
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
    get_user_name()

def show_help():
    """Show available commands"""
    bot_say("Here's what I can do:")
    time.sleep(0.3)
    bot_say("Tell jokes")
    time.sleep(0.2)
    bot_say("Search Wikipedia")
    time.sleep(0.2)
    bot_say("Tell time and date")
    time.sleep(0.2)
    bot_say("Open websites")
    time.sleep(0.2)
    bot_say("Do calculations")
    time.sleep(0.2)
    bot_say("Get weather information")
    time.sleep(0.2)
    bot_say("Set reminders")
    time.sleep(0.2)
    bot_say("And play music")

def main():
    """Main conversation loop"""
    wish_user()
    interaction_count = 0
    
    while True:
        query = take_command()
        interaction_count += 1
        
        if not query:
            continue
        
        name_prefix = f"{user_name}, " if user_name and random.random() > 0.7 else ""
        
        if 'wikipedia' in query or 'wiki' in query:
            topic = query.replace("wikipedia", "").replace("wiki", "").replace("search", "").strip()
            search_wikipedia(topic)
        
        elif 'joke' in query or 'funny' in query or 'laugh' in query:
            tell_joke()
        
        elif 'time' in query:
            tell_time()
        
        elif 'date' in query or 'today' in query:
            tell_date()
        
        elif 'weather' in query or 'temperature' in query:
            city = query.replace('weather', '').replace('temperature', '').replace('in', '').replace('of', '').strip()
            get_weather(city if city else None)
        
        elif 'remind' in query or 'reminder' in query:
            if 'list' in query or 'show' in query or 'what are' in query:
                list_reminders()
            else:
                set_reminder(query)
        
        elif 'play music' in query or 'play song' in query or 'music' in query:
            play_music()
        
        elif 'open' in query or 'youtube' in query or 'google' in query:
            open_website(query)
        
        elif 'search' in query:
            open_website(query)
        
        elif 'calculate' in query or 'plus' in query or 'minus' in query or ('what is' in query and any(char.isdigit() for char in query)):
            calculate(query)
        
        elif 'help' in query or 'what can you do' in query or 'commands' in query:
            show_help()
        
        elif 'how are you' in query or 'how do you do' in query:
            responses = [
                "I'm doing great! Thanks for asking.",
                "I'm excellent! How about you?",
                "Fantastic! Ready to help you."
            ]
            bot_say(random.choice(responses))
        
        elif 'thank' in query:
            responses = [
                f"You're welcome!",
                "Happy to help!",
                "Anytime!"
            ]
            bot_say(random.choice(responses))
        
        elif any(word in query for word in ['exit', 'quit', 'bye', 'goodbye', 'see you', 'byebye']):
            farewells = [
                f"Goodbye, {user_name}! Have a wonderful day!",
                f"See you later, {user_name}!",
                f"Take care, {user_name}!"
            ]
            bot_say(random.choice(farewells))
            break
        
        elif 'your name' in query:
            bot_say("I'm your smart assistant.")
        
        elif 'who are you' in query or 'what are you' in query:
            bot_say("I'm your AI voice assistant!")
        
        else:
            responses = [
                "I'm not sure how to help with that yet.",
                "Try asking for help to see what I can do!",
                f"I didn't understand that. Say 'help' to see commands."
            ]
            bot_say(random.choice(responses))
        
        if interaction_count % 5 == 0:
            prompts = [
                "What else can I help you with?",
                "Anything else?",
                "I'm here if you need more help!"
            ]
            bot_say(random.choice(prompts))

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("🎙️  VOICE ASSISTANT STARTING...")
        print("=" * 50)
        main()
    except KeyboardInterrupt:
        bot_say("Shutting down. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")
        bot_say("I encountered an error.")
