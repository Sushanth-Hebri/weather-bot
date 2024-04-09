import json
from difflib import SequenceMatcher
from flask import Flask, request

app = Flask(__name__)

# Load non-weather responses from JSON file
with open("/content/non_weather_responses.json") as file:
    non_weather_data = json.load(file)

def partial_match(query, item):
    similarity = SequenceMatcher(None, query, item).ratio()
    return similarity > 0.6  # Adjust the threshold as needed

def process_user_query(query):
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in ["weather", "temperature"]):
        city = input("May I know the name of the city you're interested in? ")
        # Code to fetch weather data and process response
        response = f"Weather in {city}: Temperature: 25 °C, Description: Sunny"  # Placeholder response
    else:
        # Check for partial matches in non-weather responses
        matched_item = None
        for item in non_weather_data["requests"]:
            if partial_match(query_lower, item["request"]):
                matched_item = item
                break
        if matched_item:
            response = matched_item["response"]
        else:
            response = "Sorry, I can only provide weather information. Please ask about weather or temperature."
    return response

@app.route("/", methods=["GET", "HEAD"])
def chatbot():
    if request.method == "GET":
        query = request.args.get("query")
        if query:
            response = process_user_query(query)
        else:
            response = "No query provided"
        return {"response": response}
    else:
        return "", 200  # Return empty response with status code 200 for HEAD requests

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
