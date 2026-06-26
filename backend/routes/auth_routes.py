from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import users_collection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 409

    hashed_password = generate_password_hash(password)

    new_user = {
        "name": name,
        "email": email,
        "password": hashed_password
    }
    users_collection.insert_one(new_user)

    return jsonify({"status": "success", "message": "User registered successfully"}), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = users_collection.find_one({"email": email})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "status": "success", 
        "message": "Login successful",
        "user": {
            "name": user.get("name"),
            "email": user.get("email")
        }
    }), 200