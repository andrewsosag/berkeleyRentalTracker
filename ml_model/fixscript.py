import pandas as pd
import numpy as np

# Function to calculate distance using Haversine formula
def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 # Radius of earth in kilometers
    return c * r

# UC Berkeley coordinates
ucb_lat, ucb_lon = 37.8702, -122.2595

# Load the data
df = pd.read_csv('clean_data.csv')

# Calculate distance to UC Berkeley for each row and add it to the dataframe
df['distance_to_ucb_km'] = df.apply(lambda row: haversine(ucb_lon, ucb_lat, row['longitude'], row['latitude']), axis=1)

# Save the updated dataframe to a new CSV file
df.to_csv('clean_data_with_distance.csv', index=False)

print("Updated dataframe saved to 'clean_data_with_distance.csv'.")
