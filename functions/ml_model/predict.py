# functions/ml_model/predict.py

import joblib
import numpy as np
import pandas as pd
from pathlib import Path

def load_model():
    """Load the trained model and encoder"""
    model_path = Path(__file__).parent / 'rent_prediction_model.joblib'
    return joblib.load(model_path)

def predict_rental_price(property_info):
    """
    Predict rental price for a property
    
    Args:
        property_info (dict): Property information including:
            - beds (int/str): Number of bedrooms or 'Studio'
            - baths (float): Number of bathrooms
            - latitude (float): Property latitude
            - longitude (float): Property longitude
            - neighborhood (str): Property neighborhood
            - days_on_mls (int): Days on market
            
    Returns:
        dict: Prediction results including predicted rent and confidence range
    """
    try:
        # Load model and encoder
        model, le_neighborhood = load_model()
        
        # Create DataFrame with single property
        df = pd.DataFrame([property_info])
        
        # Prepare features
        df['beds'] = df['beds'].replace('Studio', '0')
        df['beds'] = pd.to_numeric(df['beds'])
        
        # Create all required features
        df['beds_baths'] = df['beds'] * df['baths']
        df['days_on_mls_log'] = np.log1p(df['days_on_mls'])
        df['price_per_bed'] = df['beds'].replace(0, 1)  # Placeholder
        df['neighborhood_encoded'] = le_neighborhood.transform([df['neighborhood'].iloc[0]])
        
        # Calculate distance to center of Berkeley
        df['dist_to_center'] = np.sqrt(
            (df['latitude'] - 37.8715)**2 +
            (df['longitude'] - -122.2730)**2
        )
        
        # Select features in correct order
        features = [
            'beds', 'baths', 'beds_baths',
            'latitude', 'longitude', 'dist_to_center',
            'days_on_mls_log', 'neighborhood_encoded',
            'price_per_bed'
        ]
        
        # Make prediction
        prediction_log = model.predict(df[features])
        prediction = np.expm1(prediction_log)[0]
        
        # Round to nearest 50
        prediction = round(prediction / 50) * 50
        
        # Calculate confidence range
        rmse = 520.14  # From our model evaluation
        confidence_range = (
            max(0, prediction - rmse),
            prediction + rmse
        )
        
        return {
            'predicted_rent': prediction,
            'confidence_range': confidence_range,
            'model_version': '1.0'
        }
        
    except Exception as e:
        print(f"Error making prediction: {e}")
        return None