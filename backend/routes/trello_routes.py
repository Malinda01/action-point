import requests
from flask import Blueprint, request, jsonify
from config import Config

trello_bp = Blueprint("trello", __name__)

@trello_bp.route("/api/create-trello-cards", methods=["POST"])
def create_trello_cards():
    data = request.json
    tasks = data.get("tasks", [])

    if not all([Config.TRELLO_API_KEY, Config.TRELLO_TOKEN, Config.TRELLO_LIST_ID]):
        return jsonify({"error": "Missing Trello credentials in .env"}), 500

    created_cards = []

    for task in tasks:
        card_name = f"{task['title']} ({task['assignee']})"
        card_desc = f"**Priority:** {task['priority']}\n\n{task['description']}"

        url = "https://api.trello.com/1/cards"

        query = {
            "key": Config.TRELLO_API_KEY,
            "token": Config.TRELLO_TOKEN,
            "idList": Config.TRELLO_LIST_ID,
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