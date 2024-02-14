import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# Initialize Firestore
service_account_path = 'berkeley-housing-app-firebase-adminsdk-2oetp-5419402200.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Fetch data from Firestore
properties_ref = db.collection(u'properties')
docs = properties_ref.stream()

# Convert documents to DataFrame
data = []
for doc in docs:
    doc_data = doc.to_dict()
    data.append(doc_data)

df = pd.DataFrame(data)

# Save to CSV
df.to_csv('properties_data.csv', index=False)
