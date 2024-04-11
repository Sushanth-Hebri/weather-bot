import asyncio
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
import requests
from bs4 import BeautifulSoup
import websockets
import transformers
import numpy as np
import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO

# Load cities from the text file
with open("cities.txt", "r") as file:
    cities = [city.strip().lower() for city in file.readlines()]

class ChatBot():
    def __init__(self, name):
        self.name = name

    def wake_up(self, text):
        return True if self.name in text.lower() else False

    @staticmethod
    def action_time():
        return datetime.datetime.now().time().strftime('%H:%M')

    @staticmethod
    def text_to_text(input_text):
        nlp = transformers.pipeline("conversational", model="microsoft/DialoGPT-medium")
        chat = nlp(transformers.Conversation(input_text), pad_token_id=50256)
        response = str(chat)
        response = response[response.find("bot >> ") + 6:].strip()
        return response

chatbot = ChatBot(name="Dave")

async def handle_client(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        query = data.get('query')  # Assuming the user sends the query in the 'query' field
        response = {}  # Initialize an empty dictionary for the response data under "response" key
        if query:
            if chatbot.wake_up(query):
                response = "Hello, I am Dave the AI. How can I assist you?"
            elif "time" in query:
                response = chatbot.action_time()
            elif any(i in query for i in ["thank", "thanks"]):
                response = np.random.choice(["you're welcome!", "anytime!", "no problem!", "cool!", "I'm here if you need me!", "mention not"])
            elif any(i in query for i in ["exit", "close"]):
                response = np.random.choice(["Tata", "Have a good day", "Bye", "Goodbye", "Hope to meet soon", "peace out!"])
            else:
                response = chatbot.text_to_text(query)
        else:
            response = "No query provided"
        await websocket.send(json.dumps({"response": response}))  # Send response data as JSON

@app.route("/", methods=["POST"])
def chatbot_http():
    data = request.json
    query = data.get('query')  # Assuming the user sends the query in the 'query' field
    response = {}  # Initialize an empty dictionary for the response data under "response" key
    if query:
        async def send_to_websocket():
            async with websockets.connect('ws://localhost:8765') as websocket:
                await websocket.send(json.dumps({"query": query}))
                response = await websocket.recv()
                return response

        response = asyncio.run(send_to_websocket())
    else:
        response = "No query provided"
    return jsonify({"response": response})  # Return response data as JSON under "response" key

async def start_websocket_server():
    server = await websockets.serve(handle_client, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_websocket_server())
    serve(app, host='0.0.0.0', port=5000)
