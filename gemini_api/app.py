from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os
from flask_cors import CORS
import typing_extensions as typing
import enum
from parsepoints import weightpoints


load_dotenv()

API_KEY = os.getenv('API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')

with open('prompt.txt', 'r') as file:
    prompt = file.read()

class Grade(enum.Enum):
    A_PLUS = "a+"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    F = "f"

class Type(enum.Enum):
    GOOD = "good"
    NEUTRAL = "neutral"
    BAD = "bad"

class Point(typing.TypedDict):
    text: str
    rating: Type

class PrivacySummary(typing.TypedDict):
    points: list[Point]


app = Flask(__name__)
CORS(app)

def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters and digits
    text = text.lower()  # Convert to lowercase
    text = ' '.join(text.split())  # Remove extra whitespace
    return text

def extract_privacy_link(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        privacy_links = soup.find_all('a', href=True, text=lambda text: text and 'privacy policy' in text.lower())
        if privacy_links:
            return privacy_links[0]['href']

        #Present on 50 Websites, Ranked order
        privacy_keywords = [
            'privacy', 'policy', 'terms', 'legal', 'about',
            'confidential', 'security', 'data', 'protection',
            'personal information', 'user data', 'cookie',
            'consent', 'GDPR', 'CCPA', 'HIPAA', 'PII'
        ]

        potential_links = soup.find_all('a', href=True, string=lambda text: text and any(keyword in text.lower() for keyword in privacy_keywords))

        highest_ranked_link = None
        highest_rank = len(privacy_keywords)

        for link in potential_links:
            if 'privacy' in link['href'].lower():
                return link['href']
            for rank, keyword in enumerate(privacy_keywords):
                if keyword in link.text.lower() and rank < highest_rank:
                    highest_rank = rank
                    highest_ranked_link = link['href']

        return highest_ranked_link

    except Exception as e:
        print(f"Error extracting privacy link: {e}")
        return None

#This function is needed if gemini ai generation hits the text cap/cuts off to keep only full elements
def sanitize_privacy_analysis(privacy_analysis):

    elements = re.findall(r"\['(.*?)', '(.*?)'\]", privacy_analysis)

    sanitized_elements = [list(element) for element in elements if len(element) == 2]
    
    return sanitized_elements

def sanitize_proper_analysis(result):
    result = json.loads(result)  
    data = result.get("points", [])
    sanitized_elements = [[point["text"], point["rating"]] for point in data]
    return sanitized_elements

@app.route('/fetch', methods=['GET'])
def analyze_privacy():
    url = request.args.get('url')
    if not url:
        print("No Url")
        return jsonify({"error": "Missing 'url' parameter"}), 400
    
    url = url if url.startswith("http") else "http://" + url

    print("Revieved Request:", url)

    privacy_link = extract_privacy_link(url)
    if not privacy_link:
        return jsonify({"error": "Privacy policy link not found"}), 404

    full_url = privacy_link if privacy_link.startswith("http") else url + privacy_link
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        privacy_text = clean_text(soup.get_text())
        print("Soup Fetched")
    except Exception as e:
        return jsonify({"error": f"Failed to fetch privacy policy content: {e}"}), 500

    genai.configure(api_key=API_KEY)

    try:
        #model = genai.GenerativeModel(model_name=MODEL_NAME)
        model = genai.GenerativeModel(model_name=MODEL_NAME)
    except Exception as e:
        print(e)
        return jsonify({"error": f"Failed to load GenAI model: {e}"}), 500

    print(privacy_text)
    try:
        response = model.generate_content([
            prompt,
            privacy_text
        ], 
                                    generation_config=genai.GenerationConfig(
                                    response_schema=PrivacySummary,
                                    response_mime_type="application/json"

                                 ),)
        result = response.text
    except Exception as e:
        print(e)
        return jsonify({"error": f"Error during model generation: {e}"}), 500
    
    try:
        result_json = json.loads(result)
        sanitized_elements = sanitize_proper_analysis(result)
        points = result_json.get("points", [])
        sentences = [point["text"] for point in points]
        summarized_points = weightpoints(sentences)
        for point in points:
            point_text = point["text"]
            point["value"] = summarized_points.get(point_text, 0)

        good_points = sorted([point for point in points if point["rating"] == Type.GOOD], key=lambda x: x["value"], reverse=True)[:6]
        neutral_points = sorted([point for point in points if point["rating"] == Type.NEUTRAL], key=lambda x: x["value"], reverse=True)[:6]
        bad_points = sorted([point for point in points if point["rating"] == Type.BAD], key=lambda x: x["value"], reverse=True)[:6]

        top_points = good_points + neutral_points + bad_points

    except Exception as e:
        return jsonify({"error": f"Error processing points: {e}"}), 500

    return jsonify({"privacy_analysis": top_points})

if __name__ == '__main__':
    app.run(debug=True)
