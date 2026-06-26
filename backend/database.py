from pymongo import MongoClient
from config import Config

try:
    client = MongoClient(Config.MONGO_URI)
    db = client["actionpoint_db"]  
    users_collection = db["users"] 
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    users_collection = None