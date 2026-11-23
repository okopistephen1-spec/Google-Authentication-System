from flask import Flask, session, render_template, request, jsonify
import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verify-google-token", methods=["POST"])
def verify_google_token():

    data = request.get_json()

    token = data.get("credential")

    if not token:
        return jsonify({
            "error": "No Google ID token provided"
        }), 400

    try:
        user_data = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        return jsonify({
            "message": "Google authentication successful!",
            "name": user_data.get("name"),
            "email": user_data.get("email")
        })

    except ValueError:
        return jsonify({
            "error": "Invalid Google ID token"
        }), 401

if __name__ == "__main__":
    app.run(debug=True)