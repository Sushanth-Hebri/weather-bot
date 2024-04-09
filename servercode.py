import json
from difflib import SequenceMatcher
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
CORS(app)

# Load non-weather responses from JSON file
with open("non_weather_responses.json") as file:
    non_weather_data = json.load(file)

def partial_match(query, item):
    similarity = SequenceMatcher(None, query, item).ratio()
    return similarity > 0.6  # Adjust the threshold as needed

@app.route("/", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        data = request.json
        query = data.get("query", "").lower()
        if "weather" in query or "temperature" in query:
            session['expect_location'] = True  # Set a flag to expect location input
            return jsonify({"response": "Please specify the city for weather information."})
        elif session.get('expect_location'):
            # If the session expects a location input
            city = query.capitalize()  # Capitalize the city name
            session.pop('expect_location')  # Clear the flag
            response = f"Weather in {city}: Temperature: 25 °C, Description: Sunny"  # Placeholder response
            return jsonify({"response": response})
        else:
            # Check for partial matches in non-weather responses
            matched_item = None
            for item in non_weather_data["requests"]:
                if partial_match(query, item["request"].lower()):
                    matched_item = item
                    break
            if matched_item:
                return jsonify({"response": matched_item["response"]})
            else:
                return jsonify({"response": "Sorry, I can only provide weather information. Please ask about weather or temperature."})
    else:
        return jsonify({"response": "No query provided"})

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
