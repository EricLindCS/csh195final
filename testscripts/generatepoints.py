import requests
from bs4 import BeautifulSoup
from feedai import *
import re
import time

def clean_text(text):
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove stopwords
    #stop_words = set(stopwords.words('english'))
    #text = ' '.join(word for word in text.split() if word not in stop_words)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def extract_privacy_link(url):

    try:
        response = requests.get(url)
        response.raise_for_status()  

        soup = BeautifulSoup(response.content, 'html.parser')

        # Prioritize exact matches for 'privacy policy'
        privacy_links = soup.find_all('a', href=True, text=lambda text: text and 'privacy policy' in text.lower())

        if privacy_links:
            return privacy_links[0]['href']

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
                if keyword in link.text.lower():
                    if rank < highest_rank:
                        highest_rank = rank
                        highest_ranked_link = link['href']

        return highest_ranked_link

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None

# Example usage:
url = "https://www.si.edu"
privacy_link = extract_privacy_link(url)

if privacy_link:
    print("Privacy Policy Link:", url + privacy_link)
else:
    print("Privacy policy link not found.")


#####Parse Page for Text

import requests
from bs4 import BeautifulSoup

if privacy_link:
    url = url + privacy_link
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        text = clean_text(text)

    else:
        print(f"Failed to retrieve the URL: {response.status_code}")

import requests

# Replace with your actual API Key and Privacy Policy Text
from api_key import API_KEY
privacy_text = text  # Replace with actual text

import google.generativeai as genai

import typing_extensions as typing
import enum

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

class PrivacySummary(typing.TypedDict):
    points: list[str, Type]

genai.configure(api_key=API_KEY)

model_exists = False
for model_info in genai.list_tuned_models():
    print(model_info.name)
    if model_info.name == 'tunedModels/privacysummarizer-4hqz1fx0ajrs':
        model = genai.GenerativeModel(model_name="tunedModels/privacysummarizer-4hqz1fx0ajrs")
        print("FOUND")
        model_exists = True
        break

dotry = False

if not model_exists and dotry:

    import json
    # Load the privacy policies from the JSON file
    with open('privacy_policies3.json', 'r') as file:
        privacy_policies = json.load(file)
    # Function to format the privacy policy text
    def format_privacy_policy(policy):
        trimmed_policy = policy[:39000]
        return f"Provide a good/bad/neutral list of things a website visitor should know based on the given privacy policy.\n\nPrivacy Policy:\n{trimmed_policy}"
    # Create the training data
    training_data1 = []

    for service, details in privacy_policies.items():
        if details['privacy_policy'] == "":
            print("Skipped")
            continue
        text_input = format_privacy_policy(details['privacy_policy'])
        #output = details['points']  # Assuming 'points' field contains the list of points and type
        output = ', '.join(map(str, details['points']))  # Assuming 'points' field contains the list of points and type
        trimmed_output = output[:4950]
        training_data1.append({"text_input": text_input, "output": trimmed_output})

    # Save the training data to a new JSON file
    with open('training_data.json', 'w') as file:
        json.dump(training_data1, file, indent=4)

    base_model = "models/gemini-1.5-flash-001-tuning"

    operation = genai.create_tuned_model(
        # You can use a tuned model here too. Set `source_model="tunedModels/..."`
        display_name="privacysummarizer",
        source_model=base_model,
        epoch_count=20,
        batch_size=4,
        learning_rate=0.001,
        training_data=training_data1,
    )

    for status in operation.wait_bar():
        print(status)
        time.sleep(10)

    result = operation.result()
    print(result)
    model = genai.GenerativeModel(model_name=result.name)



print("Starting Gen")

response = model.generate_content(["Provide a good/bad/neutral list of things a website visitor should know based on the given privacy policy.", text], 
                                    generation_config=genai.GenerationConfig(
                                    response_schema=PrivacySummary
                                 ),
                                )
print(response.text)

