import speech_recognition as sr
import pyttsx3
import requests
from datetime import datetime
import google.generativeai as genai

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Gemini API setup (replace with your key)
GEMINI_API_KEY = "AIzaSyDwVy6UD8sIUj4YycQo67bNTu9fLbTCZRE"  # Replace with your actual key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # Use a suitable Gemini model

# OpenWeatherMap API setup (for weather feature)
WEATHER_API_KEY = "7092c6fae9a79e4c7cdbffc68daaa458"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn’t understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, there’s an issue with the speech service.")
            return None

# Function to get weather
def get_weather(city):
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            speak(f"The weather in {city} is {temp} degrees Celsius with {description}.")
        else:
            speak(f"Sorry, I couldn’t find the weather for {city}.")
    except Exception:
        speak("There was an error fetching the weather.")

# Function to get Gemini response
def get_gemini_response(query):
    try:
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        return f"Sorry, I couldn’t process that. Error: {str(e)}"

# Main assistant logic
def assistant():
    speak("Hello! I’m your voice assistant powered by Gemini. Ask me anything!")
    while True:
        command = listen()
        if command:
            # Time
            if "time" in command:
                current_time = datetime.now().strftime("%I:%M %p")
                speak(f"The current time is {current_time}.")
            
            # Weather
            elif "weather" in command:
                speak("Which city’s weather would you like to know?")
                city_command = listen()
                if city_command:
                    get_weather(city_command.strip())
            
            # Exit
            elif "exit" in command or "goodbye" in command:
                speak("Goodbye! Have a great day!")
                break
            
            # Any other question goes to Gemini
            else:
                speak("Let me think about that...")
                answer = get_gemini_response(command)
                print(f"Gemini says: {answer}")
                speak(answer)

# Run the assistant
if __name__ == "__main__":
    assistant()