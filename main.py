import speech_recognition as sr
import webbrowser
import smtplib
import os
import datetime
import pyttsx3
from email.message import EmailMessage
import numpy as np
import sounddevice as sd
import requests
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pywhatkit
import time

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Use [1] for female voice
engine.setProperty('rate', 130)

WAKE_WORDS = ["hey assistant", "wake up", "hello"]
assistant_awake = False

NEWS_API_KEY = "5879e823b2c14743b48c23b6ec39b3ad"  # Replace with your own

email_list = {
    'dude': 'wefybcsnj1111@gmail.com',
    'mom': 'mom@example.com',
    'dad': 'dad@example.com'
}

EMAIL_ADDRESS = os.getenv("MY_EMAIL") or ""# Replace with your own
EMAIL_PASSWORD = os.getenv("MY_APP_PASSWORD") or ""# Replace with your own

def speak(audio):
    print(f"[Assistant]: {audio}")
    engine.say(audio)
    engine.runAndWait()
    time.sleep(1)

def recognize_speech():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            print("⏱️ Timeout: No speech detected.")
            return ""
    try:
        print("🧠 Recognizing...")
        command = recognizer.recognize_google(audio)
        print("✅ You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"🚫 API Request error: {e}")
        return ""

# ------------------ Wake and Sleep ------------------ #

def listen_for_wake_word():
    command = recognize_speech()
    print("Wake word check:", command)
    return any(wake_word in command for wake_word in WAKE_WORDS)

def wake_up_system():
    global assistant_awake
    while not assistant_awake:
        if listen_for_wake_word():
            assistant_awake = True
            speak("I am now awake. How can I help you?")
            main()

def respond_to_go_to_sleep():
    global assistant_awake
    speak("Going to sleep. Say 'wake up' to reactivate.")
    assistant_awake = False
    wake_up_system()

# ------------------ Core Functionalities ------------------ #

def get_weather():
    latitude, longitude = 21.2472, 72.8508  # Your location
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = requests.get(url).json()
    if "current_weather" in response:
        temp = response["current_weather"]["temperature"]
        wind = response["current_weather"]["windspeed"]
        speak(f"It's {temp}°C with a wind speed of {wind} km/h.")
    else:
        speak("Sorry, I couldn't fetch the weather.")

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    if response["status"] != "ok":
        speak("Sorry, I couldn't fetch the news.")
        return
    speak("Here are today's top headlines.")
    for i, article in enumerate(response["articles"][:5], start=1):
        speak(f"News {i}: {article.get('title', 'No title')}")

def google_search(query):
    query = query.replace("search in google", "")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def song_youtube(query):
    query = query.replace("search in youtube", "")
    webbrowser.open(f'https://www.youtube.com/results?search_query={query}')

def play_song(command):
    song = command.replace('play', '').strip()
    speak(f'Playing {song}')
    pywhatkit.playonyt(song)

def adjust_volume(command):
    if "set volume to" in command:
        try:
            level = int(command.split("set volume to ")[1])
            if 0 <= level <= 100:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100, None)
                speak(f"Volume set to {level}")
            else:
                speak("Volume should be between 0 and 100.")
        except:
            speak("I didn't understand the volume level.")

# ------------------ Email ------------------ #

def send_email(receiver, subject, message):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        email = EmailMessage()
        email['From'] = EMAIL_ADDRESS
        email['To'] = receiver
        email['Subject'] = subject
        email.set_content(message)
        server.send_message(email)
        server.quit()
        speak("Email sent successfully.")
    except Exception as e:
        speak("Failed to send email.")
        print("Error:", e)

def get_email_info():
    speak("Who do you want to email?")
    name = recognize_speech()
    receiver = email_list.get('dude')
    if not receiver:
        speak("I'm not familiar with that name.")
        return
    speak("What's the subject?")
    subject = recognize_speech()
    speak("What's the message?")
    message = recognize_speech()
    send_email(receiver, subject, message)

# ------------------ Main Assistant Loop ------------------ #

def main():
    global assistant_awake
    while assistant_awake:
        command = recognize_speech()

        if not command:
            continue

        if "go to sleep" in command:
            respond_to_go_to_sleep()
            break
        elif "search in google" in command:
            google_search(command)
        elif "search in youtube" in command:
            song_youtube(command)
        elif "play" in command:
            play_song(command)
        elif "volume" in command:
            adjust_volume(command)
        elif "weather" in command:
            get_weather()
        elif "news" in command:
            get_news()
        elif "send email" in command:
            get_email_info()
        elif "help" in command:
            speak("You can say: play music, check weather, get news, or send email.")
        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            assistant_awake = False
            break

# ------------------ Entry Point ------------------ #

if __name__ == "__main__":
    test_mode = input("Run in test mode? (y/n): ")
    if test_mode.lower() == 'y':
        assistant_awake = True
        main()
    else:
        wake_up_system()
