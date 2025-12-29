import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 1. Load the secrets from .env
load_dotenv()

# 2. Setup Flask
app = Flask(__name__)
CORS(app) # Allow other apps to talk to us

# 3. A simple test route
@app.route('/', methods=['GET'])
def health_check():
    # Check if keys are loaded correctly
    openai_key = os.getenv("OPENAI_API_KEY")
    trello_key = os.getenv("TRELLO_API_KEY")
    
    status = {
        "server": "Running",
        "openai_key_found": bool(openai_key),
        "trello_key_found": bool(trello_key)
    }
    return jsonify(status)

# 4. Start the server
if __name__ == '__main__':
    print("🚀 Starting ActionPoint Backend...")
    app.run(debug=True, port=5000)