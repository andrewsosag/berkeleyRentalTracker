import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import tensorflow as tf



# Load the dataset
df = pd.read_csv('/Users/andrew/Documents/GitRepos/berkeleyRentalTracker/ml_model/clean_data_with_distance.csv')

# Check for and handle missing values
imputer = SimpleImputer(strategy='mean')
df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
df_imputed['rent'] = df_imputed['rent'].fillna(df_imputed['rent'].mean())

# Selecting features and target variable
X = df_imputed.drop('rent', axis=1)
y = df_imputed['rent']

# Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import tensorflow as tf



# Load the dataset
df = pd.read_csv('/Users/andrew/Documents/GitRepos/berkeleyRentalTracker/ml_model/clean_data_with_distance.csv')

# Check for and handle missing values
imputer = SimpleImputer(strategy='mean')
df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
df_imputed['rent'] = df_imputed['rent'].fillna(df_imputed['rent'].mean())

# Selecting features and target variable
X = df_imputed.drop('rent', axis=1)
y = df_imputed['rent']

# Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalizing the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)  # Output layer for regression
])

model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae', 'mse'])

history = model.fit(X_train_scaled, y_train, epochs=100, validation_split=0.2, verbose=1)

test_loss, test_mae, test_mse = model.evaluate(X_test_scaled, y_test, verbose=2)
print(f"Test MAE: {test_mae}, Test MSE: {test_mse}")

model.save('rent_prediction_model.h5')

# Convert the model to TensorFlow Lite format
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TensorFlow Lite model to a file
with open('rent_prediction_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("TensorFlow Lite model has been saved.")