# This is the first Python project file
import speech_recognition as sr
import pyttsx3
import datetime
import wikipediaapi
import webbrowser
import os
import sounddevice as sd
import numpy as np
import io
import sys

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    print("Bot:", text)
    engine.say(text)
    engine.runAndWait()

def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am your voice assistant. How can I help you?")

def takeCommand():
    recognizer = sr.Recognizer()

    # Record audio from the default microphone using sounddevice
    print("Listening...")
    duration = 5  # seconds
    fs = 16000  # sample rate
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # wait until recording is finished

    # Convert NumPy array to AudioData for speech_recognition
    byte_data = audio_data.tobytes()
    audio_stream = sr.AudioData(byte_data, fs, 2)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio_stream, language='en-in')
        print(f"You said: {query}")
    except Exception:
        speak("Sorry, I didn't catch that. Please say that again.")
        return "None"
    return query.lower()

def handleCommand(query):
    if 'wikipedia' in query:
        speak('Searching Wikipedia...')
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent='MyVoiceBot/1.0 (https://example.com/)',
            language='en'
        )
        topic = query.replace("wikipedia", "").strip()
        page = wiki_wiki.page(topic)
        if page.exists():
            summary = page.summary[:300]
            speak("According to Wikipedia...")
            speak(summary)
        else:
            speak("Sorry, no information found.")

    elif 'open google' in query:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")

    elif 'time' in query:
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {time_str}")

    elif 'exit' in query or 'quit' in query or 'thank you' in query:
        speak("Goodbye!")
        exit()

    else:
        speak("Sorry, I don't understand that command.")
 
if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand()
        if query != "None":
            handleCommand(query)