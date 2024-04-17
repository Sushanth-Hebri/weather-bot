import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
import requests
from bs4 import BeautifulSoup
import logging
import wikipediaapi

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
# Function to scrape news headlines from AP News
def apnews():
    try:
        url = "https://apnews.com/"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            headlines = []
            # Find all news elements with the specified class name
            news_elements = soup.find_all(class_="PagePromoContentIcons-text")
            for news in news_elements:
                headline = news.get_text().strip()
                headlines.append(headline)
            return json.dumps({"headlines": headlines})
        else:
            return json.dumps({"error": "Failed to fetch news headlines"})
    except Exception as e:
        return json.dumps({"error": str(e)})
        
def get_image_url(class_name):
    url = 'https://timesofindia.indiatimes.com/'  # Replace with the actual URL
    try:
        logging.info(f"Fetching image URL from Times of India with class {class_name}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        parent_div = soup.find('div', class_=class_name)
        if parent_div:
            img_tag = parent_div.find('img')
            if img_tag:
                image_url = img_tag['src']
                return image_url
            else:
                logging.error("No img tag found within the parent div")
                return None
        else:
            logging.error(f"No parent div found with the specified class {class_name}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching image URL: {e}")
        return None
    except Exception as e:
        logging.error(f"Error parsing image URL: {e}")
        return None

def scrape_deccan_herald_news():
    url = 'https://www.deccanherald.com/'  # Update this with the actual URL
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        news_articles = soup.find_all(class_='Kk1mG')

        headlines = []
        for article in news_articles:
            headline_element = article.find('h2', class_='headline')
            if headline_element:
                headline_text = headline_element.get_text(strip=True)
                headlines.append(headline_text)

        return headlines
    else:
        return None

def scrape_news(url):
    # Send a GET request to the specified URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all the article containers on the page
        articles = soup.find_all('div', class_='article-container')
        
        # Initialize an empty list to store the scraped headlines
        headlines = []
        
        # Iterate through each article container and extract the headline
        for article in articles:
            article_title = article.find('div', class_='article-title')
            if article_title:
                title_text = article_title.find('a', href=True).text.strip()
                headlines.append(title_text)
        
        # Create a dictionary with the headlines list
        response_json = {
            'headlines': headlines
        }
        
        # Return the JSON response
        return response_json
    else:
        # If the request was not successful, return None
        return None

def get_wikipedia_content(query):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',  # Specify the language ('en' for English)
        user_agent='MyWikiBot/1.0'  # Specify a user agent string
    )

    # Fetch the Wikipedia page based on the user's query
    page = wiki_wiki.page(query)

    if page.exists():
        # Return the summary of the Wikipedia page
        return page.summary
    else:
        return "Page not found on Wikipedia."

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
                image_url = get_image_url('Bw78m cardactive')
                response = {"headlines": headlines, "image_url": image_url} if image_url else headlines
            else:
                response = "Sorry, could not fetch news headlines at the moment."
        elif query.lower().startswith("wiki:"):
            search_query = query[5:].strip()  # Remove "wiki:" prefix
            wiki_content = get_wikipedia_content(search_query)
            response = {"wiki_content": wiki_content}
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

@app.route("/scrape-deccan-herald", methods=["GET"])
def scrape_deccan_herald():
    headlines = scrape_deccan_herald_news()
    if headlines:
        return jsonify({"headlines": headlines})
    else:
        return jsonify({"error": "Failed to fetch news from Deccan Herald"}), 500


# Route for scraping AP News headlines
@app.route("/apnews", methods=["GET"])
def scrape_apnews():
     headlines = apnews()
     if headlines:
        return jsonify({"headlines": headlines})
    else:
        return jsonify({"error": "Failed to fetch news from Deccan Herald"}), 500



@app.route("/wire", methods=["GET"])
def scrape_wire():
    # URL of the website to scrape
    url_to_scrape = 'https://thewire.in/'
    
    # Scrape news and get the JSON response in the desired format
    news_json = scrape_news(url_to_scrape)

    if news_json:
        return jsonify(news_json)
    else:
        return jsonify({"error": "Failed to fetch news from The Wire"}), 500

@app.route("/bbc_news", methods=["GET"])
def bbc_news():
    url = 'https://www.bbc.com/news'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines = soup.find_all('h2', {'class': 'sc-4fedabc7-3', 'data-testid': 'card-headline'})

        if headlines:
            news_list = [headline.text.strip() for headline in headlines]
            response_json = {'headlines': news_list}
        else:
            response_json = {'error': 'No headlines found with the specified class and data-testid.'}
    else:
        response_json = {'error': 'Failed to fetch the webpage.'}

    return json.dumps(response_json)

@app.route("/wiki", methods=["POST"])
def wiki():
    data = request.json
    query = data.get('query')  # Assuming the user sends the query in the 'query' field
    if query:
        search_query = query.strip()  # Remove any leading/trailing spaces
        wiki_content = get_wikipedia_content(search_query)
        return jsonify({"wiki_content": wiki_content})
    else:
        return jsonify({"error": "No query provided"}), 400

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
