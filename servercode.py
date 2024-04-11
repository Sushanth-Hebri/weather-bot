import os
import datetime
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import Conversation, pipeline

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
        logging.error("Error fetching weather data")
        return None

def extract_city(query):
    query_words = query.lower().split()
    for word in query_words:
        if word in cities:
            return word.title()
    return None

@app.route("/", methods=["POST"])
def chatbot():
    data = request.json
    query = data.get('query')  # Assuming the user sends the query in the 'query' field
    response = {}  # Initialize an empty dictionary for the response data under "response" key
    if query:
        if query.lower() == "hi":
            response = "Hey there, how can I help you today?"
        elif query.lower() == "thanks":
            response = "My pleasure."
        elif query.lower() == "bye":
            response = "Goodbye!"
        elif query.lower() == "who is your creator":
            response = "sushanth , is my owner"
        elif query.lower() == "how are you":
            response = "as a bot i am idle"
        elif query.lower() == "what is your name":
            response = "personal assistant bot"
        elif query.lower() == "what can you do":
            response = "i can tell weather, haedlines and i can greet"
        elif query.lower() == "headlines":
            headlines = get_news_headlines('hoid1')
            if headlines:
                response = headlines
            else:
                response = "Sorry, could not fetch news headlines at the moment."
        else:
            nlp = pipeline("conversational", model="microsoft/DialoGPT-medium")
            chat = nlp(Conversation(query), pad_token_id=50256)
            response = chat[0]['generated_text']
    else:
        response = "No query provided"
    return jsonify({"response": response})  # Return response data as JSON under "response" key

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
