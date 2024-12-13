import requests
from bs4 import BeautifulSoup
from feedai import *

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

class PrivacySummary(typing.TypedDict):
    grade: Grade
    positive: list[str]
    negative: list[str]
    neutral: list[str]

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(["Summarize the privacy policy text and provide a good/bad/neutral list of things a website visitor should know based on the policy. Additionally, assign it a grade based on how good the policy is", text], 
                                    generation_config=genai.GenerationConfig(
                                    response_mime_type="application/json", response_schema=PrivacySummary
                                 ),
                                )
print(response.text)


