import os
import json
import whisper
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
            model_name="gemini-1.5-flash",
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)