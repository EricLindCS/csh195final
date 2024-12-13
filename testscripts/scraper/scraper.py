import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    response = requests.get(url)
    return response.text

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def extract_data(soup):
    positive = []
    negative = []
    neutral = []

    rows = soup.find_all('tr', class_='toSort')
    for row in rows:
        classification = row.get('data-classification')
        title = row.find('td').text.strip()
        
        if classification == 'good':
            positive.append(title)
        elif classification == 'bad':
            negative.append(title)
        elif classification == 'neutral':
            neutral.append(title)
    
    return positive, negative, neutral

def main(url):
    html = fetch_html(url)
    soup = parse_html(html)
    positive, negative, neutral = extract_data(soup)
    
    return {
        'positive': positive,
        'negative': negative,
        'neutral': neutral
    }

if __name__ == "__main__":
    url = 'https://edit.tosdr.org/services/312'  # Replace with the actual URL
    result = main(url)
    print(result)