import csv
import json

# Read the CSV file
csv_file = 'services_data.csv'
json_file = 'pointdata.json'

data = []

with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        data.append({
            "text-input": row["Point Text"],
            "output": row["Point Weight"]
        })

# Write to JSON file
with open(json_file, mode='w', encoding='utf-8') as file:
    json.dump(data, file, indent=4)

print(f"Data has been written to {json_file}")