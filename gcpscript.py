import firebase_admin
from firebase_admin import credentials, firestore
from firebase_functions import pubsub_fn
import requests
import re
import logging
from bs4 import BeautifulSoup
from homeharvest import scrape_property
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Firestore
service_account_path = 'berkeley-housing-app-firebase-adminsdk-2oetp-5419402200.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def construct_detailed_url(original_url, street, city, state, zip_code):
    # Assuming the original URL is of the format 'https://www.realtor.com/realestateandhomes-detail/2225339747'
    # and the detailed URL should be 'https://www.realtor.com/realestateandhomes-detail/2724-Channing-Way_Berkeley_CA_94704_M22253-39747'
    # We need to extract the last part of the original URL and append it after 'M'
    unique_id_match = re.search(r"/(\d+)$", original_url)
    if unique_id_match:
        unique_id = f"M{unique_id_match.group(1)}"
    else:
        print(f"Could not extract unique ID from URL: {original_url}")
        return None

    # Transform the street address into the format used in the detailed URLs
    formatted_street = street.replace(" ", "-").replace(",", "").replace(".", "")

    # Construct the URL in the desired format
    url = f"https://www.realtor.com/realestateandhomes-detail/{formatted_street}_{city}_{state}_{zip_code}_{unique_id}"
    return url

def scrape_additional_details(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',  # or the specific types you've seen in the network capture
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Referer': 'https://www.realtor.com/',  # Adjust this based on your observation
            'Origin': 'https://www.realtor.com',  # This might be necessary for some sites
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to retrieve data from {url} (Status code: {response.status_code})")
            return None, None, None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract details
        beds_tag = soup.find('li', {'data-testid': 'property-meta-beds'})
        baths_tag = soup.find('li', {'data-testid': 'property-meta-baths'})
        rent_tag = soup.find('div', {'class': 'price-details'})

        beds = beds_tag.find('span', {'data-testid': 'meta-value'}).get_text().strip() if beds_tag else "N/A"
        baths = baths_tag.find('span', {'data-testid': 'meta-value'}).get_text().strip() if baths_tag else "N/A"
        rent = rent_tag.get_text().strip() if rent_tag else None

        return beds, baths, rent
    except Exception as e:
        print(f"Error scraping details from {url}: {e}")
        return None, None, None

# Scrape property data
properties = scrape_property(location="Berkeley, CA", listing_type="for_rent", past_days=5)
print(f"Number of properties: {len(properties)}")

# Loop through the properties and scrape additional details
for index, row in properties.iterrows():
    original_url = row['property_url']
    street = row['street']
    city = row['city']
    state = row['state']
    zip_code = row['zip_code']
    
    detailed_url = construct_detailed_url(original_url, street, city, state, zip_code)
    if detailed_url:
        beds, baths, rent = scrape_additional_details(detailed_url)
        print(f"Property {index+1}: URL: {detailed_url}, Beds: {beds}, Baths: {baths}, Rent: {rent}")
    else:
        print(f"Property {index+1}: Failed to construct URL for original URL: {original_url}")

# Convert and upload data
for index, row in properties.iterrows():
    property_data = row.to_dict()
    property_id = row['property_url']  # or any other unique identifier
    db.collection('properties').document(property_id).set(property_data)
