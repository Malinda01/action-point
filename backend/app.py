import os
import json
import whisper
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# 1. Configuration & Setup
load_dotenv(override=True) # Forces reload of .env
app = Flask(__name__)
CORS(app)

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Local Whisper Model (This runs on your computer!)
# 'base' is a good balance of speed and accuracy. Try 'small' if you want better results.
print("Loading Whisper model... (this happens only once)")
whisper_model = whisper.load_model("base") 

UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/process-meeting', methods=['POST'])
def process_meeting():
    print("... Incoming Audio File ...")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
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
            generation_config={"response_mime_type": "application/json"}
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

        return jsonify({
            "status": "success",
            "transcript": transcript_text,
            "analysis": analysis_data
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# 4. Trello Integration
@app.route('/api/create-trello-cards', methods=['POST'])
def create_trello_cards():
    data = request.json
    tasks = data.get('tasks', [])
    
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
            'key': API_KEY,
            'token': TOKEN,
            'idList': LIST_ID,
            'name': card_name,
            'desc': card_desc,
            'pos': 'top'
        }

        response = requests.post(url, params=query)
        
        if response.status_code == 200:
            created_cards.append(response.json())
        else:
            print(f"Failed to create card: {response.text}")

    return jsonify({"status": "success", "created": created_cards})

if __name__ == '__main__':
    app.run(debug=True, port=5000)