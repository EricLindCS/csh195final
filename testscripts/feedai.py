import requests

def analyze_privacy_policy_with_gemini(text, api_key):
    """
    Send privacy policy text to Google Gemini API for analysis.

    :param text: The privacy policy text to analyze.
    :param api_key: Your API key for Google Gemini.
    :return: Analysis result as JSON.
    """
    api_url = "https://api.google.com/gemini/analyze"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model": "analysis",  # Specify the model or task type if required.
        "parameters": {
            "output_format": "categorized"
        }
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with API: {e}")
        return None

# Example usage:
api_key = "YOUR_API_KEY"  # Replace with your actual API key.


