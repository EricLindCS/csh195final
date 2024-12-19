import requests
from bs4 import BeautifulSoup
from feedai import *
import re
import time

# Replace with your actual API Key and Privacy Policy Text
from api_key import API_KEY

import google.generativeai as genai

import typing_extensions as typing
import enum


genai.configure(api_key=API_KEY)

for model_info in genai.list_tuned_models():
    print(model_info.name)

model = genai.GenerativeModel("tunedModels/pointtoweight-gq0xspdqyvrm")

print("Starting Gen")

response = model.generate_content("When the service wants to make a material change to its terms, you are notified at least 30 days in advance")
print(response.text)

