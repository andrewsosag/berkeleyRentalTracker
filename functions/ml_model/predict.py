import joblib
import pandas as pd
import numpy as np
import logging

def extract_first_number(value):
    """Extract first number with better N/A handling"""
    if pd.isna(value) or value == "N/A":
        return 1  # Default to 1 instead of None
        
    value = str(value).lower()
    
    if "studio" in value:
        return 0
        
    if "-" in value:
        first_part = value.split("-")[0].strip()
        if "studio" in first_part:
            return 0
        try:
            return float(first_part)
        except:
            return 1  # Default to 1
            
    if "+" in value:
        base = value.replace("+", "").strip()
        if "studio" in base:
            return 0
        try:
            return float(base)
        except:
            return 1  # Default to 1
            
    try:
        return float(value)
    except:
        return 1  # Default to 1
    

def get_property_defaults(property_info):
    """Get property info with default values"""
    beds = extract_first_number(property_info.get('beds'))
    baths = extract_first_number(property_info.get('baths'))
    
    # Make sure beds and baths are not None
    beds = 1 if beds is None else beds
    baths = 1 if baths is None else baths
    
    return {
        'beds': beds,
        'baths': baths,
        'latitude': property_info.get('latitude', 37.8715),
        'longitude': property_info.get('longitude', -122.2730),
        'style': property_info.get('style', 'APARTMENT'),
        'zip_code': property_info.get('zip_code', '94704'),
        'days_on_mls': property_info.get('days_on_mls', 0),
        'list_date': property_info.get('list_date', pd.Timestamp.now())
    }

def get_neighborhood_from_zip(zip_code):
    zip_code = zip_code.astype(str)
    neighborhood_map = {
        '94704': 'Southside',
        '94703': 'South Berkeley',
        '94702': 'West Berkeley',
        '94709': 'North Berkeley',
        '94710': 'Northwest Berkeley',
        '94720': 'UC Campus',
        '94705': 'Elmwood',
        '94708': 'Berkeley Hills'
    }
    neighborhood = zip_code.map(neighborhood_map)
    return neighborhood

def load_model():
    try:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'rent_prediction_model.joblib')
        
        logging.info(f"Current directory: {current_dir}")
        logging.info(f"Looking for model at: {model_path}")
        
        if not os.path.exists(model_path):
            logging.error(f"Model file not found at {model_path}")
            logging.info(f"Directory contents: {os.listdir(current_dir)}")
            return None, None, None
            
        model, le_neighborhood, features = joblib.load(model_path)
        return model, le_neighborhood, features
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        return None, None, None

def predict_rental_price(property_info):
    try:
        logging.info(f"Loading model...")
        model, le_neighborhood, features = load_model()
        if not model:
            logging.error("Failed to load model")
            return None
            
        # Get property info with defaults
        property_info = get_property_defaults(property_info)
        
        logging.info(f"Using property info with defaults: {property_info}")
        
        # Create feature dictionary with safe values
        feature_dict = {
            'beds': property_info['beds'],
            'baths': property_info['baths'],
            'is_studio': 1 if property_info['beds'] == 0 else 0,
            'total_rooms': property_info['beds'] + property_info['baths'],
            'latitude': property_info['latitude'],
            'longitude': property_info['longitude'],
            'days_on_market_log': np.log1p(property_info['days_on_mls']),
            'is_apartment': 1 if property_info['style'] == 'APARTMENT' else 0,
            'is_house': 1 if property_info['style'] == 'SINGLE_FAMILY' else 0,
            'has_sqft': 0,
            'is_student_housing': 1 if property_info['zip_code'] in ['94704', '94720'] else 0,
            'is_luxury': 1 if (property_info['beds'] >= 2 and 
                              property_info['style'] == 'APARTMENT') else 0,
            'price_per_room': 0
        }
        
        # Calculate distances
        berkeley_center = (37.8715, -122.2730)
        UC_BERKELEY = (37.8719, -122.2585)
        DOWNTOWN_BART = (37.8703, -122.2677)
        
        feature_dict['dist_to_center'] = np.sqrt(
            (feature_dict['latitude'] - berkeley_center[0])**2 +
            (feature_dict['longitude'] - berkeley_center[1])**2
        )
        
        feature_dict['dist_to_uc'] = np.sqrt(
            (feature_dict['latitude'] - UC_BERKELEY[0])**2 +
            (feature_dict['longitude'] - UC_BERKELEY[1])**2
        )
        
        feature_dict['dist_to_bart'] = np.sqrt(
            (feature_dict['latitude'] - DOWNTOWN_BART[0])**2 +
            (feature_dict['longitude'] - DOWNTOWN_BART[1])**2
        )
        
        # Safe seasonal features
        try:
            list_date = pd.to_datetime(property_info['list_date'])
            feature_dict['is_summer'] = 1 if list_date.month in [6, 7, 8] else 0
        except:
            feature_dict['is_summer'] = 0
            
        # Safe ratio features
        feature_dict['bed_bath_ratio'] = (feature_dict['beds'] / feature_dict['baths'] 
                                        if feature_dict['baths'] > 0 else 1)
        
        # Create DataFrame and add neighborhood encoding
        df = pd.DataFrame([feature_dict])
                # Get neighborhood encoding
        zip_code = property_info.get('zip_code', '94704')
        neighborhood_map = {
            '94704': 'Southside',
            '94703': 'South Berkeley',
            '94702': 'West Berkeley',
            '94709': 'North Berkeley',
            '94710': 'Northwest Berkeley',
            '94720': 'UC Campus',
            '94705': 'Elmwood',
            '94708': 'Berkeley Hills'
        }
        neighborhood = neighborhood_map.get(property_info['zip_code'], 'Central Berkeley')
        df['neighborhood_encoded'] = le_neighborhood.transform([neighborhood])[0]
        
        logging.info(f"Features created: {df.columns.tolist()}")
        
        # Ensure all required features are present
        missing_features = set(features) - set(df.columns)
        if missing_features:
            logging.error(f"Missing features: {missing_features}")
            return None
            
        # Make prediction using only required features
        prediction = model.predict(df[features])[0]
        prediction = round(prediction / 50) * 50
        
        # Dynamic confidence range
        rmse = 675.56
        confidence_factor = 1.0
        if feature_dict['is_studio']:
            confidence_factor = 1.2
        elif feature_dict['beds'] >= 3:
            confidence_factor = 1.3
            
        confidence_range = (
            max(0, prediction - (rmse * confidence_factor)),
            prediction + (rmse * confidence_factor)
        )
        
        result = {
            'predicted_rent': prediction,
            'confidence_range': confidence_range,
            'model_version': '2.0',
            'prediction_quality': 'high' if confidence_factor == 1.0 else 'medium'
        }
        logging.info(f"Prediction successful: {result}")
        return result
        
    except Exception as e:
        logging.error(f"Error making prediction: {str(e)}")
        logging.error(f"Property info: {property_info}")
        return None