import csv
import requests
from bs4 import BeautifulSoup
import json
import re
#from nltk.corpus import stopwords


def fetch_privacy_policy(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

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

def main():
    input_csv = 'services_data.csv'
    output_json = 'privacy_policies.json'
    data = {}
    timed_out_urls = set()

    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        numser = 0
        for row in reader:
            service_name = row['Service Name']
            privacy_url = row['Privacy URL']
            point_text = row['Point Text']
            point_type = row['Point Rating']


            if row['Privacy URL'] is None or row['Privacy URL'] == '' or privacy_url in timed_out_urls:
                continue

            if service_name not in data:
                data[service_name] = {
                    'privacy_policy': '',
                    'points': []
                }
                print("Working Service #", numser+1, "Name", service_name, "URL:", privacy_url)
                numser += 1

            if not data[service_name]['privacy_policy']:
                raw_text = fetch_privacy_policy(privacy_url)
                if raw_text == "":
                    timed_out_urls.add(privacy_url)
                    print("Skipped:", privacy_url)
                    continue
                cleaned_text = clean_text(raw_text)
                data[service_name]['privacy_policy'] = cleaned_text

            data[service_name]['points'].append([point_text, point_type])

    with open(output_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()