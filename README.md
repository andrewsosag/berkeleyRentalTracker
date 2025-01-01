# BerkeleyNest.com: Berkeley Rental Market Analytics Platform

## Overview

BerkeleyNest.com is a comprehensive data analytics platform analyzing the Berkeley apartment rental market in real-time. The platform processes over 5,000 rental listings daily, giving users actionable insights related to rental trends and fair pricing to make informed decisions in a competitive housing market.

![Berkeley Rental Analytics Dashboard](https://andrewsosag.github.io/images/projects/berkeleynest.png)

## Key Features

### Market Intelligence
- Real-time processing of 5,000+ daily rental listings
- Interactive visualizations of market trends
- Neighborhood-specific pricing analysis
- Dynamic demand index mapping

### Analytics Dashboard
- Average rent visualization by apartment type
- Rent distribution analysis via interactive donut charts
- Geographic heat maps showing neighborhood trends
- ZIP code-level price and demand comparisons

### Machine Learning Price Predictions
- Random Forest model with 85% accuracy
- Key performance metrics:
  - Mean Absolute Error (MAE): $676.27
  - Root Mean Square Error (RMSE): $1,042.29
  - R² Score: 0.62

## Technical Architecture

### Tech Stack
- **Frontend**: React.js, D3.js, Bootstrap
- **Backend**: Python, NoSQL
- **Cloud Infrastructure**: Google Cloud Platform
- **Machine Learning**: TensorFlow
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Database**: Firebase Firestore
- **Visualization**: Chart.js, Leaflet.js

### Core Components

#### ETL Pipeline
- Automated data collection and validation
- Real-time data processing system
- GCP-based scalable infrastructure
- Robust error handling and monitoring

#### Analytics Engine
- Dynamic market trend analysis
- Real-time price comparison algorithms
- Demand index calculation
- Geographic data processing

#### Machine Learning Pipeline
- Feature engineering and data preprocessing
- Model training and validation
- Real-time prediction serving
- Performance monitoring and retraining

## Data Analysis Insights

### Feature Engineering
- Strong correlation between rent and bedroom/bathroom count
- Rent distribution centered around $2,500
- Variance analysis by bedroom count:
  - Stable: 1, 2, and 4 bedrooms
  - Higher variation: 3 and 5 bedrooms

### Market Trends
- ZIP code specific price trends
- Demand index based on days-on-market
- Seasonal variation analysis
- Neighborhood price differentials

## Code Examples

### Market Insights Component
```javascript
/**
 * Renders a dynamic table displaying average rent prices by apartment type.
 * Processes raw rental data and creates an HTML table with formatted pricing.
 * 
 * @param {Object} rentData - Object containing arrays of rent prices by apartment type
 * @example
 * rentData = {
 *   'Studio': [1500, 1600, 1450],
 *   '1': [2000, 2100, 1950],
 *   '2': [2800, 2900, 2750]
 * }
 */
function displayAverageRent(rentData) {
  // Initialize table structure with header
  let tableContent = `<table class="table">
    <thead>
      <tr>
        <th>Type</th>
        <th>Average Rent</th>
      </tr>
    </thead>
    <tbody>`;

  // Define display order for consistent presentation
  const order = ['Studio', '1', '2', '3'];
  
  // Generate table rows for each apartment type
  order.forEach(type => {
    // Calculate average rent, handling potential null or empty data
    const averageRent = rentData[type]?.length
      ? (rentData[type].reduce((a, b) => a + b) / rentData[type].length).toFixed(2)
      : 'N/A';
    
    // Append formatted row with proper apartment type label
    tableContent += `<tr>
      <td>${type === 'Studio' ? 'Studio' : type + ' Bedroom'}</td>
      <td>$${averageRent}</td>
    </tr>`;
  });

  // Complete table structure and update DOM
  tableContent += `</tbody></table>`;
  document.getElementById('average-rent-table').innerHTML = tableContent;
}
```
### Interactive Map Integration
```
/**
 * Creates and configures an interactive map showing rental prices by ZIP code.
 * Utilizes Leaflet.js for map rendering and GeoJSON for ZIP code boundaries.
 * 
 * @param {Object} rentData - Object containing average rent data by ZIP code
 * @example
 * rentData = {
 *   '94704': { averageRent: 2500 },
 *   '94705': { averageRent: 2800 }
 * }
 */
function createMapWithRentData(rentData) {
  // Initialize map centered on Berkeley
  const map = L.map('mapid').setView([37.8715, -122.2730], 13);
  
  // Add OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
  }).addTo(map);

  // Add GeoJSON layer with ZIP code boundaries
  L.geoJson(zipCodeBoundaries, {
    // Style each ZIP code region based on average rent
    style: feature => ({
      color: "#000",
      weight: 2,
      fillColor: getColor(rentData[feature.properties.ZIP_CODE]?.averageRent || 0),
      fillOpacity: 0.7
    }),
    // Add interactive popups showing ZIP code data
    onEachFeature: (feature, layer) => {
      const zipCode = feature.properties.ZIP_CODE;
      const avgRent = rentData[zipCode]?.averageRent || "Data not available";
      
      // Create formatted popup content
      layer.bindPopup(
        `<strong>ZIP Code:</strong> ${zipCode}<br>
         <strong>Average Rent:</strong> $${avgRent}`
      );
    }
  }).addTo(map);
}

/**
 * Determines fill color for ZIP code regions based on average rent.
 * Implements a gradient scale from green (lower rent) to red (higher rent).
 * 
 * @param {number} rentAmount - Average rent for the ZIP code
 * @returns {string} - Hex color code for the region
 */
function getColor(rentAmount) {
  // Color scale thresholds
  return rentAmount > 3000 ? '#bd0026' :
         rentAmount > 2500 ? '#f03b20' :
         rentAmount > 2000 ? '#fd8d3c' :
         rentAmount > 1500 ? '#feb24c' :
                            '#fed976';
}
```

## Challenges and Solutions

### Data Processing
- Challenge: Managing large-scale daily data ingestion
- Solution: Implemented robust ETL pipeline with validation and error handling

### Real-time Analytics
- Challenge: Processing complex analytics in real-time
- Solution: Optimized database queries and implemented caching strategies

### Map Integration
- Challenge: Integrating ZIP code boundaries with dynamic rent data
- Solution: Custom Leaflet.js implementation with optimized data structures
