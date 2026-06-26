from flask import Flask
from flask_cors import CORS

# Import the blueprints from your routes folder
from routes.auth_routes import auth_bp
from routes.meeting_routes import meeting_bp
from routes.trello_routes import trello_bp

app = Flask(__name__)
CORS(app)

# Register all the routes
app.register_blueprint(auth_bp)
app.register_blueprint(meeting_bp)
app.register_blueprint(trello_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)