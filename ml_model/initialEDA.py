import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the cleaned dataset
df = pd.read_csv('cleaned_properties_data_with_neighborhood.csv')
df.describe()

# Preprocess 'rent' to remove non-numeric values
df['rent'] = df['rent'].str.replace('$', '').str.replace('/mo', '').str.replace(',', '')
df['rent'] = pd.to_numeric(df['rent'], errors='coerce')

# Now you can drop NaN values or fill them with a specific value (mean, median, etc.)
# For example, to fill NaN values with the mean:
df['rent'].fillna(df['rent'].mean(), inplace=True)

# Rental price distribution
plt.hist(df['rent'], bins=20)
plt.title('Rental Price Distribution')
plt.xlabel('Monthly Rent ($)')
plt.ylabel('Number of Listings')
plt.show()

# Average Rent by Apartment Type
avg_rent_by_type = df.groupby('beds')['rent'].mean().reset_index()
avg_rent_by_type['beds'] = avg_rent_by_type['beds'].astype(str)  # Convert beds to string for better representation
print("Average Rent by Apartment Type:\n", avg_rent_by_type)

# Apartment Rent Ranges Donut Chart
rent_bins = [0, 1000, 2000, 3000, 4000, 5000, np.inf]
rent_labels = ['$0-1000', '$1001-2000', '$2001-3000', '$3001-4000', '$4001-5000', '$5000+']
df['rent_range'] = pd.cut(df['rent'], bins=rent_bins, labels=rent_labels)
rent_range_counts = df['rent_range'].value_counts().sort_index()
plt.figure(figsize=(8, 8))
plt.pie(rent_range_counts, labels=rent_range_counts.index, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.3))
plt.title('Apartment Rent Ranges')
plt.show()

# Average Rent by Neighborhood
avg_rent_by_neighborhood = df.groupby('neighborhood')['rent'].mean().reset_index()
print("Average Rent by Neighborhood:\n", avg_rent_by_neighborhood)


# Assuming 'df' has columns 'neighborhood' and 'days_on_mls'
# Calculate Demand Index
df['days_on_mls'] = pd.to_numeric(df['days_on_mls'], errors='coerce').fillna(0)

# Step 1: Aggregate total DOM and count listings per neighborhood
demand_data = df.groupby('neighborhood')['days_on_mls'].agg(['sum', 'count']).reset_index()
demand_data.rename(columns={'sum': 'total_DOM', 'count': 'listings'}, inplace=True)

# Step 2: Calculate initial demand index
demand_data['average_DOM'] = demand_data['total_DOM'] / demand_data['listings']
max_listings = demand_data['listings'].max()
demand_data['demand_index'] = demand_data['listings'].apply(lambda x: x / max_listings) / demand_data['average_DOM']

# Step 3: Normalize the demand index to a 0-1 scale
max_demand_index = demand_data['demand_index'].max()
demand_data['normalized_demand_index'] = demand_data['demand_index'] / max_demand_index

# Visualize Demand Index
plt.figure(figsize=(10, 6))
demand_data.sort_values('normalized_demand_index', ascending=False, inplace=True)
plt.bar(demand_data['neighborhood'], demand_data['normalized_demand_index'])
plt.xticks(rotation=45, ha='right')
plt.title('Normalized Demand Index by Neighborhood')
plt.xlabel('Neighborhood')
plt.ylabel('Normalized Demand Index')
plt.tight_layout()
plt.show()


# Correlation Heatmap
import seaborn as sns

corr = df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()