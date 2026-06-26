import os
import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import google.generativeai as genai
from config import Config
from ai_services import whisper_model

meeting_bp = Blueprint("meeting", __name__)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

@meeting_bp.route("/api/process-meeting", methods=["POST"])
def process_meeting():
    print("... Incoming Audio File ...")

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    print(f"File saved to: {filepath}")

    try:
        print("Transcribing locally (this takes a moment)...")
        result = whisper_model.transcribe(filepath)
        transcript_text = result["text"]

        print("Analyzing with Gemini...")
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
        analysis_data = json.loads(response.text)

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