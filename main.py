# Voice Command AI — Updated Code
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

# ------------------ Initialization ------------------ #

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 130)

WAKE_WORDS = ["hey assistant", "wake up", "hello"]
assistant_awake = False

# SECURITY: Configure NEWS_API_KEY in your environment.
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

EMAIL_ADDRESS = os.getenv("MY_EMAIL", "Add Your Email.")
EMAIL_PASSWORD = os.getenv("MY_APP_PASSWORD", "Add Your APP Password")

email_list = {
    "dude": "wefybcsnj1111@gmail.com",
    "mom": "mom@example.com",
    "dad": "dad@example.com"
}


# ------------------ Text to Speech ------------------ #

def speak(audio):
    print(f"[Assistant]: {audio}")
    engine.say(audio)
    engine.runAndWait()
    time.sleep(1)


# ------------------ Speech Recognition ------------------ #

def recognize_speech():
    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(
                source, duration=1
            )

            try:
                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=7
                )
            except sr.WaitTimeoutError:
                print("⏱️ Timeout: No speech detected.")
                return ""

        print("🧠 Recognizing...")
        command = recognizer.recognize_google(audio)
        print("✅ You said:", command)

        return command.lower()

    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return ""

    except sr.RequestError as error:
        print(f"🚫 Speech recognition API error: {error}")
        return ""

    except (OSError, AttributeError) as error:
        print(f"🎤 Microphone error: {error}")
        return ""


# ------------------ Wake and Sleep ------------------ #

def listen_for_wake_word():
    command = recognize_speech()
    print("Wake word check:", command)

    return any(
        wake_word in command
        for wake_word in WAKE_WORDS
    )


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


# ------------------ Weather ------------------ #

def get_weather():
    latitude, longitude = 21.2472, 72.8508

    url = "Add Your Weather API Key Here."

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        current_weather = data.get("current_weather")

        if not current_weather:
            speak("Sorry, current weather data is unavailable.")
            return

        temperature = current_weather.get("temperature")
        wind_speed = current_weather.get("windspeed")

        if temperature is None or wind_speed is None:
            speak("Sorry, the weather data is incomplete.")
            return

        speak(
            f"It's {temperature} degrees Celsius "
            f"with a wind speed of {wind_speed} kilometers per hour."
        )

    except requests.RequestException as error:
        print(f"Weather network error: {error}")
        speak("Sorry, I couldn't connect to the weather service.")

    except (ValueError, TypeError, KeyError) as error:
        print(f"Weather data error: {error}")
        speak("Sorry, I couldn't process the weather information.")


# ------------------ News ------------------ #

def get_news():
    if not NEWS_API_KEY:
        speak(
            "News is not configured. "
            "Please set your NEWS_API_KEY environment variable."
        )
        return

    url = "Add Your News API Key Here."

    params = {
        "country": "us",
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            error_message = data.get(
                "message", "Unknown NewsAPI error"
            )

            print(f"NewsAPI error: {error_message}")
            speak("Sorry, I couldn't fetch the news.")
            return

        articles = data.get("articles", [])

        if not articles:
            speak("There are no headlines available right now.")
            return

        speak("Here are today's top headlines.")

        for number, article in enumerate(articles[:5], start=1):
            title = article.get("title") or "No title available"
            speak(f"News {number}: {title}")

    except requests.RequestException as error:
        print(f"News network error: {error}")
        speak("Sorry, I couldn't connect to the news service.")

    except (ValueError, TypeError, KeyError) as error:
        print(f"News data error: {error}")
        speak("Sorry, I couldn't process the news information.")


# ------------------ Google and YouTube ------------------ #

def google_search(query):
    query = query.replace("search in google", "").strip()

    if query:
        from urllib.parse import quote_plus
        webbrowser.open(
            f"https://www.google.com/search?q={quote_plus(query)}"
        )


def song_youtube(query):
    query = query.replace("search in youtube", "").strip()

    if query:
        from urllib.parse import quote_plus
        webbrowser.open(
            "https://www.youtube.com/results?search_query="
            + quote_plus(query)
        )


def play_song(command):
    song = command.replace("play", "", 1).strip()

    if song:
        speak(f"Playing {song}")

        try:
            pywhatkit.playonyt(song)
        except Exception as error:
            print(f"YouTube playback error: {error}")
            speak("Sorry, I couldn't play that song.")


# ------------------ Volume Control ------------------ #

def adjust_volume(command):
    if "set volume to" not in command:
        speak("Say set volume to followed by a number from 0 to 100.")
        return

    try:
        level = int(
            command.split("set volume to ", 1)[1].strip()
        )

        if not 0 <= level <= 100:
            speak("Volume should be between 0 and 100.")
            return

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )

        volume.SetMasterVolumeLevelScalar(
            level / 100,
            None
        )

        speak(f"Volume set to {level} percent.")

    except (ValueError, OSError, AttributeError) as error:
        print(f"Volume adjustment error: {error}")
        speak("Sorry, I couldn't change the volume.")

    except Exception as error:
        print(f"Unexpected volume error: {error}")
        speak("An error occurred while changing the volume.")


# ------------------ Email ------------------ #

def send_email(receiver, subject, message):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        speak(
            "Email is not configured. "
            "Please set MY_EMAIL and MY_APP_PASSWORD."
        )
        return

    try:
        email = EmailMessage()
        email["From"] = EMAIL_ADDRESS
        email["To"] = receiver
        email["Subject"] = subject
        email.set_content(message)

        with smtplib.SMTP(
            "smtp.gmail.com", 587, timeout=15
        ) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(email)

        speak("Email sent successfully.")

    except (smtplib.SMTPException, OSError) as error:
        print(f"Email error: {error}")
        speak("Failed to send email.")


def get_email_info():
    speak("Who do you want to email? Say dude, mom, or dad.")

    name = recognize_speech().strip().lower()

    # FIX: Use the spoken name instead of always choosing 'dude'.
    receiver = email_list.get(name)

    if not receiver:
        speak(
            "I'm not familiar with that name. "
            "Please say dude, mom, or dad."
        )
        return

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        speak(
            "Email is not configured. "
            "Please set MY_EMAIL and MY_APP_PASSWORD."
        )
        return

    speak("What's the subject?")
    subject = recognize_speech().strip()

    if not subject:
        speak("I didn't catch the subject. Email cancelled.")
        return

    speak("What's the message?")
    message = recognize_speech().strip()

    if not message:
        speak("I didn't catch the message. Email cancelled.")
        return

    speak(f"I will send the email to {name}.")
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

        elif command.startswith("play "):
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
            speak(
                "You can say: search in Google, search in YouTube, "
                "play music, check weather, get news, set volume, "
                "send email, go to sleep, or exit."
            )

        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            assistant_awake = False
            break


# ------------------ Entry Point ------------------ #

if __name__ == "__main__":
    test_mode = input("Run in test mode? (y/n): ").strip().lower()

    if test_mode == "y":
        assistant_awake = True
        main()
    else:
        wake_up_system()
