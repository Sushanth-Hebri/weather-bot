import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO

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

def get_news_headlines(class_name):
    url = 'https://timesofindia.indiatimes.com/'  # Replace with the actual URL
    try:
        logging.info(f"Fetching news headlines from Times of India with class {class_name}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        parent_div = soup.find('div', class_=class_name)
        if parent_div:
            figcaption_tag = parent_div.find('figcaption')
            if figcaption_tag:
                headlines_text = figcaption_tag.get_text(strip=True)
                return headlines_text
            else:
                logging.error("No figcaption tag found within the parent div")
                return None
        else:
            logging.error(f"No parent div found with the specified class {class_name}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching news headlines: {e}")
        return None
    except Exception as e:
        logging.error(f"Error parsing news headlines: {e}")
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
                response = "No city found in the query"
    else:
        response = "No query provided"
    return jsonify({"response": response})  # Return response data as JSON under "response" key

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
