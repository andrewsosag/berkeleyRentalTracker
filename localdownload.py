# firestore_download.py
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import os
import json

# Get the directory where this script is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONS_DIR = os.path.join(CURRENT_DIR, 'functions')
SERVICE_ACCOUNT_PATH = os.path.join(FUNCTIONS_DIR, 'berkeley-housing-app-firebase-adminsdk-2oetp-5419402200.json')

def download_firestore_data():
    # Initialize Firebase if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    
    # Get all properties
    properties_ref = db.collection('properties')
    docs = properties_ref.stream()
    
    # Convert to list of dictionaries
    properties = []
    for doc in docs:
        data = doc.to_dict()
        # Convert timestamp to string if present
        if 'list_date' in data and hasattr(data['list_date'], 'timestamp'):
            data['list_date'] = data['list_date'].strftime('%Y-%m-%d %H:%M:%S')
        properties.append(data)
    
    # Convert to DataFrame
    df = pd.DataFrame(properties)
    
    # Save both CSV and JSON versions
    df.to_csv('current_properties.csv', index=False)
    
    # Save raw JSON for backup
    with open('current_properties.json', 'w') as f:
        json.dump(properties, f)
    
    print(f"Downloaded {len(properties)} properties")
    print("\nDataset Info:")
    print(df.info())
    print("\nSample Data:")
    print(df[['beds', 'baths', 'rent', 'neighborhood']].head())
    
    return df

if __name__ == "__main__":
    df = download_firestore_data()