import requests
import time
import csv

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
    def __init__(self, service_id, name, first_url, points, terms_url=None, privacy_url=None):
        self.service_id = service_id
        self.name = name
        self.first_url = first_url
        self.points = points
        self.terms_url = terms_url
        self.privacy_url = privacy_url

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
        
    terms_url = None
    privacy_url = None
    for document in data['documents']:
        if document['name'] == 'Terms of Service':
            terms_url = document['url']
        elif document['name'] == 'Privacy Policy':
            privacy_url = document['url']
    
    return Service(service_id, name, first_url, points, terms_url, privacy_url)


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

def save_services_to_csv(filename, services):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=services[0].keys())
        writer.writeheader()
        writer.writerows(services)

def read_services_from_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def filter_comprehensively_reviewed_services(services):
    return [service for service in services if service['is_comprehensively_reviewed'] == "True"]


all_services = []
page = 1


def doread():
    while True:
        services_data = fetch_all_services(page)
        if services_data is not None:
            services = services_data.get('services', [])
            all_services.extend(services)
            if services_data['_page']['end'] >= services_data['_page']['total']:
                break
            print("Fetched Page", page)
        else:
            print("Timed Out, Next", page)

        if page > 100:
            break
        page += 1
        time.sleep(1)  # Add a 1-second delay between each page fetch
    
    save_services_to_csv('all_services.csv', all_services)


# Example usage
if __name__ == "__main__":
    # Fetch all services (first page)
    #services = fetch_all_services(page=1)
    #if services:
    #    print("Services:", services)
    
    #doread()
    #all_services = read_services_from_csv('all_services.csv')
    #comprehensively_reviewed_services = filter_comprehensively_reviewed_services(all_services)
    #save_services_to_csv('comprehensively_reviewed_services.csv', comprehensively_reviewed_services)
    
    comprehensively_reviewed_services = read_services_from_csv('comprehensively_reviewed_services.csv')

    # Fetch a specific service by ID
    #service_id = 312  # Example ID
    with open('services_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header
        writer.writerow(['Service ID', 'Service Name', 'First URL', 'Terms URL', 'Privacy URL', 'Point Text', 'Point Weight', 'Point Rating'])
        
        # Fetch a specific service by ID
        for serviceget in comprehensively_reviewed_services:
            time.sleep(1)  # Add a 1-second delay between each page fetch
            print("Fetching Service", serviceget['id'], "Name:", serviceget['name'])
            service = fetch_service_by_id(serviceget['id'])
            if service:
                #print(service)
                service = initialize_service(service)
                for point in service.points:
                    # Write the service data to the CSV file
                    writer.writerow([service.service_id, service.name, service.first_url, service.terms_url, service.privacy_url, point.text, point.weight, point.rating])
