import json
from flask import Flask, request
from flask_cors import CORS
from waitress import serve
import requests

app = Flask(__name__)
CORS(app)

# Load cities from the text file
with open("cities.txt", "r") as file:
    cities = [city.strip().lower() for city in file.readlines()]

def get_weather(city):
    api_key = "7f2847f45cfd99c08cd9d979d939bb21"  # Replace with your OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "units": "metric",  # Change to "imperial" for Fahrenheit
        "appid": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        print("Error fetching weather data")
        return None

def extract_city(query):
    # Split the query into words and check if any word is a city name
    words = query.lower().split()
    for word in words:
        if word in cities:
            return word.title()  # Return the city name with proper casing
    return None

@app.route("/", methods=["POST"])
def chatbot():
    data = request.json
    query = data.get('query')  # Assuming the user sends the query in the 'query' field
    if query:
        city = extract_city(query)
        if city:
            weather_data = get_weather(city)
            if weather_data:
                temperature = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                response = f"Weather in {city}: Temperature: {temperature} °C, Description: {description}"
            else:
                response = f"Sorry, weather data for {city} is not available"
        else:
            response = "City not found in the query"
    else:
        response = "No query provided"
    return {"response": response}

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
