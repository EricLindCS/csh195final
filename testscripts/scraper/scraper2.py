import requests
import time


def fetch_all_services(page=1):
    """
    Fetches all services from the ToS;DR API.

    :param page: Pagination page number (default: 1)
    :return: JSON response containing the list of services.
    """
    url = "https://api.tosdr.org/service/v2/"
    params = {"page": page}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        if data.get("error") == 256:
            return data.get("parameters")
        else:
            print("Error in response:", data.get("message"))
            return None

    except requests.exceptions.RequestException as e:
        print("Error fetching services:", e)
        return None


def fetch_service_by_id(service_id):
    """
    Fetches a specific service by ID from the ToS;DR API.

    :param service_id: The ID of the service to fetch.
    :return: JSON response containing the service details.
    """
    url = "https://api.tosdr.org/service/v2/"
    params = {"id": service_id}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        if data.get("error") == 256:
            return data.get("parameters")
        else:
            print("Error in response:", data.get("message"))
            return None

    except requests.exceptions.RequestException as e:
        print("Error fetching service by ID:", e)
        return None

class Point:
    def __init__(self, weight, text, rating):
        self.weight = weight
        self.text = text
        self.rating = rating

class Service:
    def __init__(self, service_id, name, first_url, points):
        self.service_id = service_id
        self.name = name
        self.first_url = first_url
        self.points = points

def initialize_service(data):
    service_id = data['id']
    name = data['name']
    first_url = data['urls'][0]
    
    points = []
    for point in data['points']:
        if point['status'] == 'approved':
            weight = point['case']['weight']
            text = point['title']
            rating = point['case']['classification']
            points.append(Point(weight, text, rating))
    
    return Service(service_id, name, first_url, points)


def fetch_comprehensively_reviewed_services():
    comprehensively_reviewed_services = []
    page = 1
    while True:
        leng = len(comprehensively_reviewed_services)
        services_data = fetch_all_services(page)
        if services_data is not None:
            services = services_data.get('services', [])
            comprehensively_reviewed_services.extend(
                [service for service in services if service['is_comprehensively_reviewed']]
            )
            if services_data['_page']['end'] >= services_data['_page']['total']:
                break
            print("Found:", len(comprehensively_reviewed_services)-leng, "Next Page", page)
        else:
            print("Timed Out, Next", page)

        if page > 250:
            break
        page += 1
            
        time.sleep(1)  # Add a 1-second delay between each page fetch


    '''
    for page in range(10):
        services_data = fetch_all_services(page)
        services = services_data.get('services', [])
        comprehensively_reviewed_services.extend(
            [service for service in services if service['is_comprehensively_reviewed']]
        )
    '''
    return comprehensively_reviewed_services

import csv
import time

# Example usage
if __name__ == "__main__":
    # Fetch all services (first page)
    #services = fetch_all_services(page=1)
    #if services:
    #    print("Services:", services)

    comprehensively_reviewed_services = fetch_comprehensively_reviewed_services()
    
    # Fetch a specific service by ID
    #service_id = 312  # Example ID
    with open('services_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header
        writer.writerow(['Service ID', 'Service Name', 'First URL', 'Point Text', 'Point Weight', 'Point Rating'])
        
        # Fetch a specific service by ID
        for serviceget in comprehensively_reviewed_services:
            time.sleep(1)  # Add a 1-second delay between each page fetch
            print("Fetching Service", serviceget['id'])
            service = fetch_service_by_id(serviceget['id'])
            if service:
                service = initialize_service(service)
                for point in service.points:
                    # Write the service data to the CSV file
                    writer.writerow([service.service_id, service.name, service.first_url, point.text, point.weight, point.rating])
