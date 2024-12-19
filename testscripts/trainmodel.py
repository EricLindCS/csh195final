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

class Type(enum.Enum):
    GOOD = "good"
    NEUTRAL = "neutral"
    BAD = "bad"

genai.configure(api_key=API_KEY)

for model_info in genai.list_tuned_models():
    print(model_info.name)

import json
# Load the privacy policies from the JSON file
with open('pointdata.json', 'r') as file:
    data = json.load(file)

training_data1 = [{"text_input": f"{item["text-input"]}", "output": f"{item["output"]}"} for item in data][:500]

base_model = "models/gemini-1.5-flash-001-tuning"

operation = genai.create_tuned_model(
    # You can use a tuned model here too. Set `source_model="tunedModels/..."`
    display_name="pointtoweight",
    source_model=base_model,
    training_data=training_data1,
    epoch_count=20,
    batch_size=4,
    learning_rate=0.001,
)

for status in operation.wait_bar():
    print(status)
    time.sleep(10)

result = operation.result()
print(result)
model = genai.GenerativeModel(model_name=result.name)


