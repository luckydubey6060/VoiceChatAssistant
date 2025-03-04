from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import google.generativeai as genai
import os

app = Flask(__name__)

# Gemini API setup
GEMINI_API_KEY = "AIzaSyDwVy6UD8sIUj4YycQo67bNTu9fLbTCZRE"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# OpenWeatherMap API setup
WEATHER_API_KEY = "7092c6fae9a79e4c7cdbffc68daaa458"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Function to save data to a log file
def save_to_log(query, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("conversation_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}]\nQuery: {query}\nResponse: {response}\n\n")

# Function to read the log file
def read_log():
    if os.path.exists("conversation_log.txt"):
        with open("conversation_log.txt", "r", encoding="utf-8") as log_file:
            return log_file.read()
    return "No conversation history yet."

# Function to get weather
def get_weather(city):
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            return f"The weather in {city} is {temp} degrees Celsius with {description}."
        else:
            return f"Sorry, I couldn’t find the weather for {city}."
    except Exception:
        return "There was an error fetching the weather."

# Function to get Gemini response
def get_gemini_response(query):
    try:
        response = model.generate_content(query)
        return response.text
    except Exception:
        return "Sorry, I couldn’t process that right now."

# Routes
@app.route('/')
def index():
    log_content = read_log()
    return render_template('index.html', log=log_content)

@app.route('/ask', methods=['POST'])
def ask():
    query = request.json.get('query', '').lower()
    
    if "time" in query:
        current_time = datetime.now().strftime("%I:%M %p")
        response = f"The current time is {current_time}."
    elif "weather" in query:
        city = query.split("weather in")[-1].strip() if "weather in" in query else None
        if not city:
            response = "Please specify a city for the weather."
        else:
            response = get_weather(city)
    else:
        response = get_gemini_response(query)
    
    # Save the query and response to the log
    save_to_log(query, response)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)