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
function displayAverageRent(rentData) {
  let tableContent = `<table class="table">
    <thead>
      <tr>
        <th>Type</th>
        <th>Average Rent</th>
      </tr>
    </thead>
    <tbody>`;

  const order = ['Studio', '1', '2', '3'];
  order.forEach(type => {
    const averageRent = rentData[type]?.length
      ? (rentData[type].reduce((a, b) => a + b) / rentData[type].length).toFixed(2)
      : 'N/A';
    tableContent += `<tr>
      <td>${type === 'Studio' ? 'Studio' : type + ' Bedroom'}</td>
      <td>$${averageRent}</td>
    </tr>`;
  });

  tableContent += `</tbody></table>`;
  document.getElementById('average-rent-table').innerHTML = tableContent;
}
```
### Interactive Map Integration
```javascript
function createMapWithRentData(rentData) {
  const map = L.map('mapid').setView([37.8715, -122.2730], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
  }).addTo(map);

  L.geoJson(zipCodeBoundaries, {
    style: feature => ({
      color: "#000",
      weight: 2,
      fillColor: getColor(rentData[feature.properties.ZIP_CODE]?.averageRent || 0),
      fillOpacity: 0.7
    }),
    onEachFeature: (feature, layer) => {
      const zipCode = feature.properties.ZIP_CODE;
      const avgRent = rentData[zipCode]?.averageRent || "Data not available";
      layer.bindPopup(
        `<strong>ZIP Code:</strong> ${zipCode}<br>
         <strong>Average Rent:</strong> $${avgRent}`
      );
    }
  }).addTo(map);
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
