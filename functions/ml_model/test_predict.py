# test_predict.py
import logging
from predict import predict_rental_price

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test cases
test_cases = [
    {
        # Normal case
        'beds': '2',
        'baths': '1',
        'latitude': 37.8715,
        'longitude': -122.2730,
        'style': 'APARTMENT',
        'zip_code': '94704',
        'days_on_mls': 14
    },
    {
        # N/A case
        'beds': 'N/A',
        'baths': 'N/A',
        'latitude': 37.853304,
        'longitude': -122.262528,
        'style': 'APARTMENT',
        'zip_code': '94705',
        'days_on_mls': 14
    },
    {
        # Studio case
        'beds': 'Studio',
        'baths': '1',
        'latitude': 37.8715,
        'longitude': -122.2730,
        'style': 'APARTMENT',
        'zip_code': '94704',
        'days_on_mls': 0
    }
]

# Run tests
for i, test_case in enumerate(test_cases):
    print(f"\nTesting case {i+1}:")
    print(f"Input: {test_case}")
    result = predict_rental_price(test_case)
    print(f"Result: {result}")