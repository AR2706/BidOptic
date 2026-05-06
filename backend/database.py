from pymongo import MongoClient
import os
import certifi

# Replace this string with your ACTUAL MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://aritrarickar987_db_user:BRo0W47RwiHQnj3H@cluster0.jiv6ai3.mongodb.net/?appName=Cluster0"

# We pass tlsCAFile=certifi.where() to avoid SSL handshake errors
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# This will automatically create a database named 'bidoptic' in your cloud
db = client.bidoptic

# Collections
tenders_collection = db.tenders
evaluations_collection = db.evaluations