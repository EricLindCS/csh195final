import pandas as pd
import json

# Read the JSON file
with open('pointdata.json', 'r') as file:
    data = json.load(file)

# Convert JSON data to a pandas DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('pointdata.csv', index=False)