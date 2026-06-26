import os
from dotenv import load_dotenv

# Load .env file
load_dotenv(override=True)

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
    TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
    TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID")
    UPLOAD_FOLDER = "temp_uploads"