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

def process_user_query(query):
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in ["weather", "temperature"]):
        if "temperature" in query_lower or "weather" in query_lower:
            # Check if the query contains "temperature" or "weather"
            session['expect_location'] = True  # Set a flag to expect location input
            return "Please specify the city for weather information."
    elif session.get('expect_location'):
        # If the session expects a location input
        city = query_lower.capitalize()  # Assume the first letter of the city is capitalized
        session.pop('expect_location')  # Clear the flag
        return f"Weather in {city}: Temperature: 25 °C, Description: Sunny"  # Placeholder response

    # Check for partial matches in non-weather responses
    matched_item = None
    for item in non_weather_data["requests"]:
        if partial_match(query_lower, item["request"]):
            matched_item = item
            break
    if matched_item:
        return matched_item["response"]
    else:
        return "Sorry, I can only provide weather information. Please ask about weather or temperature."

@app.route("/", methods=["GET", "HEAD"])
def chatbot():
    if request.method == "GET":
        query = request.args.get("query")
        if query:
            response = process_user_query(query)
        else:
            response = "No query provided"
        return jsonify({"response": response})
    else:
        return "", 200  # Return empty response with status code 200 for HEAD requests

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
