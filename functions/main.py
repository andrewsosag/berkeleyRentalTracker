# Welcome to Cloud Functions for Firebase for Python!
# Deploy with `firebase deploy`

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from firebase_functions import https_fn, pubsub_fn
import requests
import re
import logging
from bs4 import BeautifulSoup
from homeharvest import scrape_property
import time
from datetime import datetime, timedelta
import urllib.parse
from ml_model.predict import predict_rental_price
import config

@https_fn.on_request()
def test_predictions(req: https_fn.Request) -> https_fn.Response:
    logging.info("Starting manual prediction update")
    
    try:
        properties_ref = db.collection('properties').stream()
        count = 0
        success = 0
        
        for doc in properties_ref:
            count += 1
            property_data = doc.to_dict()
            
            # Force update all properties
            try:
                prediction_input = {
                    'beds': property_data.get('beds', 'N/A'),
                    'baths': property_data.get('baths', 'N/A'),
                    'latitude': property_data.get('latitude', 37.8715),
                    'longitude': property_data.get('longitude', -122.2730),
                    'style': property_data.get('style', 'APARTMENT'),
                    'zip_code': property_data.get('zip_code', '94704'),
                    'days_on_mls': property_data.get('days_on_mls', 0)
                }
                
                logging.info(f"Processing property: {doc.id}")
                logging.info(f"Prediction input: {prediction_input}")
                
                prediction_result = predict_rental_price(prediction_input)
                
                if prediction_result:
                    property_data.update({
                        'predicted_rent': prediction_result['predicted_rent'],
                        'rent_prediction_range_low': prediction_result['confidence_range'][0],
                        'rent_prediction_range_high': prediction_result['confidence_range'][1],
                        'model_version': prediction_result['model_version'],
                        'prediction_quality': prediction_result.get('prediction_quality', 'medium'),
                        'prediction_success': True
                    })
                    
                    # Force update
                    db.collection('properties').document(doc.id).set(property_data)
                    logging.info(f"Updated property {doc.id}")
                    success += 1
                
            except Exception as e:
                logging.error(f"Error processing property {doc.id}: {e}")
                
        return https_fn.Response(f"Processing complete. Processed {count} properties, {success} successful predictions")
        
    except Exception as e:
        logging.error(f"Error in test_predictions: {e}")
        return https_fn.Response(f"Error: {str(e)}", status=500)

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Firestore
service_account_path = config.SERVICE_ACCOUNT_PATH
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def encode_url_for_firestore(url):
    return urllib.parse.quote(url, safe='')

def construct_detailed_url(original_url, street, city, state, zip_code):
    # Assuming the original URL is of the format 'https://www.realtor.com/realestateandhomes-detail/2225339747'
    # and the detailed URL should be 'https://www.realtor.com/realestateandhomes-detail/2724-Channing-Way_Berkeley_CA_94704_M22253-39747'
    # We need to extract the last part of the original URL and append it after 'M'
    unique_id_match = re.search(r"/(\d+)$", original_url)
    if unique_id_match:
        unique_id = f"M{unique_id_match.group(1)}"
    else:
        logging.error(f"Could not extract unique ID from URL: {original_url}")
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
        with requests.get(url, headers=headers, timeout=10) as response:
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract details
                beds_tag = soup.find('li', {'data-testid': 'property-meta-beds'})
                baths_tag = soup.find('li', {'data-testid': 'property-meta-baths'})
                rent_tag = soup.find('div', {'class': 'price-details'})

                beds = beds_tag.find('span', {'data-testid': 'meta-value'}).get_text().strip() if beds_tag else "N/A"
                baths = baths_tag.find('span', {'data-testid': 'meta-value'}).get_text().strip() if baths_tag else "N/A"
                rent = rent_tag.get_text().strip() if rent_tag else "N/A"

                return beds, baths, rent
            else:
                logging.warning(f"Unexpected status code {response.status_code} for URL: {url}")
                return "N/A", "N/A", "N/A"
    except requests.RequestException as e:
        logging.error(f"Request failed for {url}: {e}")
        return "N/A", "N/A", "N/A"
    except Exception as e:
        logging.error(f"Error scraping details from {url}: {e}")
        return "N/A", "N/A", "N/A"
    

def delete_old_listings():
    try:
        db = firestore.Client()
        one_year_ago = datetime.now() - timedelta(days=365)
        old_listings = db.collection('properties').where('list_date', '<=', one_year_ago).stream()

        batch = db.batch()
        for listing in old_listings:
            batch.delete(db.collection('properties').document(listing.id))
            logging.info(f"Deleted old listing: {listing.id}")
        batch.commit()
    except Exception as e:
        logging.error(f"Error in delete_old_listings: {e}")

def string_to_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d')

def retry_scrape_property(attempts=3, delay=5):
    for i in range(attempts):
        try:
            return scrape_property(location="Berkeley, CA", listing_type="for_rent", past_days=365)
        except Exception as e:
            logging.warning(f"Attempt {i+1} failed: {e}")
            if i < attempts - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise

# Function to be triggered
@pubsub_fn.on_message_published(topic="property-update-topic")
def scheduled_function(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]):
    logging.info("Starting scheduled function at: %s", datetime.now())
    delete_old_listings()

    try:
        properties = retry_scrape_property()
    except Exception as e:
        logging.error(f"Failed to scrape properties after retries: {e}")
        return
    
    logging.info(f"Number of properties: {len(properties)}")

    for index, row in properties.iterrows():
        try:
            original_url = row['property_url']
            encoded_url = encode_url_for_firestore(original_url)

            # Get existing property data if it exists
            existing_property = db.collection('properties').document(encoded_url).get()
            property_data = existing_property.to_dict() if existing_property.exists else {}
            
            # Only update if no prediction exists or it failed
            if not property_data.get('prediction_success'):
                if not existing_property.exists:
                    # New property - get all details
                    street = row['street']
                    city = row['city']
                    state = row['state']
                    zip_code = row['zip_code']

                    detailed_url = construct_detailed_url(original_url, street, city, state, zip_code)
                    if detailed_url:
                        beds, baths, rent = scrape_additional_details(detailed_url)
                    else:
                        logging.warning(f"Skipped scraping additional details for: {original_url}")
                        continue

                    property_data = row.to_dict()
                    property_data['list_date'] = string_to_date(property_data['list_date'])
                    property_data.update({'beds': beds, 'baths': baths, 'rent': rent})

                # Get ML prediction for new or existing property
                try:
                    beds = property_data.get('beds', 'N/A')
                    baths = property_data.get('baths', 'N/A')
                    
                    prediction_input = {
                        'beds': beds,
                        'baths': float(baths.replace('N/A', '1')) if baths else 1.0,
                        'latitude': property_data.get('latitude', 37.8715),
                        'longitude': property_data.get('longitude', -122.2730),
                        'neighborhood': 'Central Berkeley',
                        'days_on_mls': property_data.get('days_on_mls', 0)
                    }

                    logging.info(f"Attempting prediction for property: {encoded_url}")
                    logging.info(f"Prediction input: {prediction_input}")
                    
                    prediction_result = predict_rental_price(prediction_input)
                    
                    if prediction_result:
                        logging.info(f"Prediction details for {encoded_url}: {prediction_result}")
                        property_data.update({
                            'predicted_rent': prediction_result['predicted_rent'],
                            'rent_prediction_range_low': prediction_result['confidence_range'][0],
                            'rent_prediction_range_high': prediction_result['confidence_range'][1],
                            'model_version': prediction_result['model_version'],
                            'prediction_success': True
                        })
                        logging.info(f"Prediction successful for property: {encoded_url}")
                    else:
                        property_data['prediction_success'] = False
                        logging.warning(f"Prediction returned None for property: {encoded_url}")
                        
                except Exception as e:
                    logging.error(f"Error predicting rent for property {encoded_url}: {e}")
                    property_data['prediction_success'] = False

                # Store updated property data
                try:
                    db.collection('properties').document(encoded_url).set(property_data)
                    logging.info(f"Successfully stored property: {encoded_url}")
                except Exception as e:
                    logging.error(f"Failed to store property {encoded_url} in database: {e}")
                    
        except Exception as e:
            logging.error(f"Error processing property at index {index}: {e}")
            continue