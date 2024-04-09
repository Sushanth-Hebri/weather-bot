import json
from flask import Flask, request
from flask_cors import CORS
from waitress import serve
import requests

app = Flask(__name__)
CORS(app)

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

@app.route("/", methods=["POST"])
def chatbot():
    data = request.json
    city = data.get('city')  # Assuming the user sends the city name in the 'city' field
    if city:
        weather_data = get_weather(city)
        if weather_data:
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            response = f"Weather in {city}: Temperature: {temperature} °C, Description: {description}"
        else:
            response = f"Sorry, weather data for {city} is not available"
    else:
        response = "No city provided"
    return {"response": response}

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
