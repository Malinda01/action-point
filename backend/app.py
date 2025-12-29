import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from openai import OpenAI

# 1. Configuration & Setup
load_dotenv()
app = Flask(__name__)
CORS(app)  # Allow React (Port 3000) to talk to Flask (Port 5000)

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create a temporary folder to store audio files while processing
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 2. The Core Logic
@app.route('/api/process-meeting', methods=['POST'])
def process_meeting():
    print("... Incoming Audio File ...")
    
    # --- Check A: Did the user send a file? ---
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # --- Step 1: Save the Audio Temporarily ---
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    print(f"File saved to: {filepath}")

    try:
        # --- Step 2: Transcribe (The Ears) ---
        print("Transcribing with Whisper...")
        audio_file = open(filepath, "rb")
        transcript_response = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        transcript_text = transcript_response.text
        print(f"Transcription complete: {transcript_text[:50]}...") # Print first 50 chars

        # --- Step 3: Analyze (The Brain) ---
        print("Analyzing with GPT-4...")
        system_prompt = """
        You are an AI Project Manager. 
        You will receive a meeting transcript. 
        You must extract actionable tasks and return them in strict JSON format.
        
        Output Format:
        {
            "summary": "Two sentence summary of the meeting.",
            "tasks": [
                {
                    "title": "Short task name",
                    "description": "Specific details about what needs to be done",
                    "assignee": "Name of person assigned (or 'Unassigned')",
                    "priority": "High/Medium/Low"
                }
            ]
        }
        """

        gpt_response = client.chat.completions.create(
            model="gpt-4-turbo", # or "gpt-3.5-turbo-0125" if you want to save money
            response_format={ "type": "json_object" }, # CRITICAL: Forces valid JSON
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript_text}
            ]
        )
        
        # Parse the string response into a real Python Dictionary
        analysis_data = json.loads(gpt_response.choices[0].message.content)

        # --- Cleanup ---
        # Close the file and delete it to save space
        audio_file.close()
        os.remove(filepath)

        # Return the result to the Frontend
        return jsonify({
            "status": "success",
            "transcript": transcript_text,
            "analysis": analysis_data
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# 3. Start Server
if __name__ == '__main__':
    app.run(debug=True, port=5000)