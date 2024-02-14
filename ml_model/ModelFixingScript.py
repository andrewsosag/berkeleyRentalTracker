import pandas as pd
import numpy as np

# Load the dataset
file_path = '/Users/andrew/Documents/GitRepos/berkeleyRentalTracker/ml_model/properties_data.csv'
df = pd.read_csv(file_path)


# Columns to drop
columns_to_drop = [
    'primary_photo', 'alt_photos', 'property_url', 'list_date', 'last_sold_date',
    'mls', 'mls_id', 'status', 'price_per_sqft', 'style', 'sold_price', 'unit', 'street', 'hoa_fee'
]

# Drop the specified columns
df_cleaned = df.drop(columns=columns_to_drop, errors='ignore')

def preprocess_value(value):
    """Strip the string and handle None values."""
    return str(value).strip() if pd.notnull(value) and value.strip() != '' else None


def preprocess_beds(beds):
    """Ensure the function always returns a list, correctly handling 'Studio - X' ranges."""
    if beds is None or beds.strip() == '':
        return [None]
    beds_range = beds.replace('Studio', '0').split('-')
    if len(beds_range) == 2:
        beds_start, beds_end = map(int, beds_range)
        return list(range(beds_start, beds_end + 1))
    elif 'Studio' in beds:
        return [0]
    return [int(beds)]

def expand_rows(row):
    """Expand rows based on beds, rent, and baths ranges, correctly handling 'Studio - X'."""
    expanded_rows = []
    beds_list = preprocess_beds(preprocess_value(row['beds']))
    rent = preprocess_value(row['rent'])
    baths = preprocess_value(row['baths'])

    rent_values = [float(x.replace('$', '').replace('/mo', '').replace(',', '')) for x in rent.split('-')] if rent and 'Contact' not in rent else [None]
    baths_values = [float(x) for x in baths.split('-')] if baths and '-' in baths else [float(baths)] if baths else [None]

    for bed in beds_list:
        new_row = row.copy()
        new_row['beds'] = 'Studio' if bed == 0 else str(bed)

        if rent_values[0] is not None:
            rent_for_bed = rent_values[0] if len(rent_values) == 1 else rent_values[0] + (rent_values[1] - rent_values[0]) * (beds_list.index(bed) / max(len(beds_list) - 1, 1))
            new_row['rent'] = f"${rent_for_bed:.2f}/mo"
        else:
            new_row['rent'] = "Contact For Price"

        if baths_values[0] is not None:
            baths_for_bed = baths_values[0] if len(baths_values) == 1 else baths_values[0] + (baths_values[1] - baths_values[0]) * (beds_list.index(bed) / max(len(beds_list) - 1, 1))
            new_row['baths'] = f"{baths_for_bed:.1f}"
        else:
            new_row['baths'] = ""

        expanded_rows.append(new_row)

    return expanded_rows


# Drop 'sqft' and 'year_built' columns
df = df.drop(['sqft', 'year_built'], axis=1)

# Function to convert rent to a float value, returns None for 'Contact For Price'
def rent_to_float(rent):
    if 'Contact' in rent:
        return None
    else:
        return float(rent.replace('$', '').replace('/mo', '').replace(',', ''))

# Apply the function to the 'rent' column
df['rent'] = df['rent'].apply(rent_to_float)

# Calculate the average rent for each bedroom count, excluding 'Contact For Price'
average_rents = df.groupby('beds')['rent'].mean().to_dict()

# Function to replace 'Contact For Price' with the average rent
def replace_contact_for_price(row):
    if pd.isnull(row['rent']):
        return average_rents.get(row['beds'], None)
    return row['rent']

# Apply the function to each row
df['rent'] = df.apply(replace_contact_for_price, axis=1)

# Replace NaN values in 'rent' with the column average (for any missing values after replacement)
df['rent'].fillna(df['rent'].mean(), inplace=True)

# Convert 'rent' back to the original format
df['rent'] = df['rent'].apply(lambda x: f"${x:.2f}/mo")


# Ensure zip_code column is of type string
df['zip_code'] = df['zip_code'].astype(str)

# Mapping of zip codes to neighborhoods
zip_to_neighborhood = {
    "94702": "West Berkeley",
    "94703": "Central Berkeley",
    "94704": "Southside",
    "94705": "Claremont Elmwood",
    "94706": "Albany",
    "94707": "Thousand Oaks",
    "94708": "Berkeley Hills",
    "94709": "North Berkeley",
    "94710": "West Berkeley",
    "94720": "University of California, Berkeley"
}

# Replace zip_code with neighborhood
df['neighborhood'] = df['zip_code'].map(zip_to_neighborhood)

# Drop the original zip_code column
df.drop('zip_code', axis=1, inplace=True)


# Assuming 'your_data.csv' is your dataset file
df = pd.read_csv('your_data.csv')

# Convert "Studio" in 'beds' column to "0"
df['beds'] = df['beds'].replace('Studio', 0).astype(float)

# Optional: Drop 'city' and 'neighborhood' if you decide to do so
# Uncomment the next line if you decide to drop these columns
# df.drop(['city', 'neighborhood'], axis=1, inplace=True)

# Convert "Studio" in 'beds' column to "0"
df['beds'] = df['beds'].replace('Studio', 0).astype(float)

# Drop 'city' and 'neighborhood' if you decide to do so
df.drop(['city', 'neighborhood'], axis=1, inplace=True)

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

# Calculate distance to UC Berkeley for each row and add it to the dataframe
df['distance_to_ucb_km'] = df.apply(lambda row: haversine(ucb_lon, ucb_lat, row['longitude'], row['latitude']), axis=1)

# Save the updated dataframe to a new CSV file
df.to_csv('clean_data_with_distance.csv', index=False)

print("Updated dataframe saved to 'clean_data_with_distance.csv'.")
