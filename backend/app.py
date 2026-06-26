import os
import json
import whisper  # type: ignore
import requests  # type: ignore
import google.generativeai as genai  # type: ignore
from flask import Flask, request, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore
from dotenv import load_dotenv  # type: ignore
from werkzeug.utils import secure_filename  # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # Added for auth
from pymongo import MongoClient # Added for MongoDB

# 1. Configuration & Setup
load_dotenv(override=True)  # Forces reload of .env
app = Flask(__name__)
CORS(app)

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------------------------------------------------------
# NEW: MongoDB Configuration
# ---------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI)
    db = client["actionpoint_db"]  # Create/Connect to database
    users_collection = db["users"] # Create/Connect to users collection
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
# ---------------------------------------------------------

# Load Local Whisper Model (This runs on your computer!)
# 'base' is a good balance of speed and accuracy. Try 'small' if you want better results.
print("Loading Whisper model... (this happens only once)")
whisper_model = whisper.load_model("base")

UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------
# NEW: Authentication Endpoints
# ---------------------------------------------------------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # 1. Check if user already exists in MongoDB
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 409

    # 2. Hash the password for security
    hashed_password = generate_password_hash(password)

    # 3. Save to MongoDB
    new_user = {
        "name": name,
        "email": email,
        "password": hashed_password
    }
    users_collection.insert_one(new_user)

    return jsonify({"status": "success", "message": "User registered successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # 1. Find user by email
    user = users_collection.find_one({"email": email})

    # 2. Check if user exists AND password matches the hashed password
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # (Note: In a production app, you would generate and return a JWT token here)
    
    return jsonify({
        "status": "success", 
        "message": "Login successful",
        "user": {
            "name": user.get("name"),
            "email": user.get("email")
        }
    }), 200
# ---------------------------------------------------------


# Process meeting endpoint
@app.route("/api/process-meeting", methods=["POST"])
def process_meeting():
    print("... Incoming Audio File ...")

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    print(f"File saved to: {filepath}")

    try:
        # --- Step 2: Transcribe (Local Whisper) ---
        print("Transcribing locally (this takes a moment)...")
        # No API call here! It uses your CPU/GPU.
        result = whisper_model.transcribe(filepath)
        transcript_text = result["text"]
        print(f"Transcription complete: {transcript_text[:50]}...")

        # --- Step 3: Analyze (Google Gemini Free Tier) ---
        print("Analyzing with Gemini...")

        # Configure the model to return JSON specifically
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"},
        )

        prompt = f"""
        You are an AI Project Manager.
        Analyze this meeting transcript and extract actionable tasks.
        
        Transcript:
        {transcript_text}

        You MUST output strict JSON in this exact format:
        {{
            "summary": "Two sentence summary of the meeting.",
            "tasks": [
                {{
                    "title": "Short task name",
                    "description": "Specific details",
                    "assignee": "Name or 'Unassigned'",
                    "priority": "High/Medium/Low"
                }}
            ]
        }}
        """

        response = model.generate_content(prompt)

        # Clean up the response text to ensure it's valid JSON
        analysis_data = json.loads(response.text)

        # --- Cleanup ---
        os.remove(filepath)

        return jsonify(
            {
                "status": "success",
                "transcript": transcript_text,
                "analysis": analysis_data,
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# 4. Trello Integration
@app.route("/api/create-trello-cards", methods=["POST"])
def create_trello_cards():
    data = request.json
    tasks = data.get("tasks", [])

    # Get Keys from .env
    API_KEY = os.getenv("TRELLO_API_KEY")
    TOKEN = os.getenv("TRELLO_TOKEN")
    LIST_ID = os.getenv("TRELLO_LIST_ID")

    if not all([API_KEY, TOKEN, LIST_ID]):
        return jsonify({"error": "Missing Trello credentials in .env"}), 500

    created_cards = []

    for task in tasks:
        # Construct the card Name and Description
        card_name = f"{task['title']} ({task['assignee']})"
        card_desc = f"**Priority:** {task['priority']}\n\n{task['description']}"

        # Trello API URL
        url = "https://api.trello.com/1/cards"

        query = {
            "key": API_KEY,
            "token": TOKEN,
            "idList": LIST_ID,
            "name": card_name,
            "desc": card_desc,
            "pos": "top",
        }

        response = requests.post(url, params=query)

        if response.status_code == 200:
            created_cards.append(response.json())
        else:
            print(f"Failed to create card: {response.text}")

    return jsonify({"status": "success", "created": created_cards})


if __name__ == "__main__":
    app.run(debug=True, port=5000)