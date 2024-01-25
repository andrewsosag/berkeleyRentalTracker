import firebase_admin
import logging
import requests
import re
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore
from homeharvest import scrape_property
from datetime import datetime

def construct_detailed_url(original_url, street, city, state, zip_code):
    # Extract the unique identifier from the original URL
    unique_id_match = re.search(r"(\d+)-(\d+)$", original_url)
    unique_id = f"M{unique_id_match.group(1)}-{unique_id_match.group(2)}" if unique_id_match else ""

    # Transform the street address into the format used in the detailed URLs
    formatted_street = street.replace(" ", "-").replace(",", "").replace(".", "")

    # Construct the URL in the desired format
    url = f"https://www.realtor.com/realestateandhomes-detail/{formatted_street}_{city}_{state}_{zip_code}_{unique_id}"
    return url

def scrape_additional_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the number of beds
    beds_tag = soup.find('li', {'data-testid': 'property-meta-beds'})
    beds = beds_tag.find('span', {'data-testid': 'meta-value'}).get_text().strip() if beds_tag else None

    # Extract the number of baths
    baths_tag = soup.find('li', {'data-testid': 'property-meta-baths'})
    baths = baths_tag.find('span', {'data-testid': 'meta-value'}).get_text().strip() if baths_tag else None

    # Extract the rent information
    rent_tag = soup.find('div', {'class': 'price-details'})
    rent = rent_tag.get_text().strip() if rent_tag else None

    return beds, baths, rent

def update_firestore_listings():
    try:
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            
            # cred = credentials.ApplicationDefault() # For Cloud Deployment
            cred = credentials.Certificate('berkeley-housing-app-firebase-adminsdk-2oetp-5419402200.json') # For Local Testing
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        # Scrape property data
        properties = scrape_property(
            location="Berkeley, CA",
            listing_type="for_rent",
            past_days=365,
        )

        # Function to check if a listing already exists in the database
        def listing_exists(url):
            docs = db.collection('listings').where('property_url', '==', url).limit(1).stream()
            return any(docs)
        
        added_listings = 0

        # Update Firestore with new listings
        for index, property in properties.iterrows():
            if added_listings >= 5:  # Limit to 5 listings for testing
                break
            if not listing_exists(property['property_url']):
                # Construct detailed URL
                detailed_url = construct_detailed_url(
                    property['property_url'],  # Pass the original URL
                    property['street'],
                    "Berkeley",  # Assuming city is always Berkeley
                    "CA",        # Assuming state is always CA
                    property['zip_code']
                )
                # Scrape additional details
                beds, baths, rent = scrape_additional_details(detailed_url)

                property_dict = property.to_dict()
                # Add new details to property_dict
                property_dict['beds'] = beds
                property_dict['baths'] = baths
                property_dict['rent'] = rent

                db.collection('listings').add(property_dict)
                added_listings += 1

        return f"Database update complete. Added {added_listings} listings."

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"

# Call the function for local testing
update_firestore_listings()