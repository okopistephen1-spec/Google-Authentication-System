from flask import (
    Flask,
    session,
    render_template,
    request,
    jsonify,
    redirect,
    url_for
)

import os

from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth.exceptions import TransportError

from database import get_db_connection
from functools import wraps


# ==========================================
# 1. ENVIRONMENT CONFIGURATION
# ==========================================

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")


# ==========================================
# 2. FLASK APPLICATION CONFIGURATION
# ==========================================

app = Flask(__name__)

if not GOOGLE_CLIENT_ID:
    raise RuntimeError("GOOGLE_CLIENT_ID is missing from .env")

if not FLASK_SECRET_KEY:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

app.secret_key = FLASK_SECRET_KEY

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

# ==========================================
# ROLE-BASED ACCESS CONTROL
# ==========================================

def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        # Check whether the user is logged in
        if "user_id" not in session:
            print("DEBUG: no user_id found in session")
            return redirect(url_for("home"))
        print("DEBUG: Logged-in user ID:", session["user_id"])

        connection = get_db_connection()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT role
                FROM users
                WHERE id = ?
            """, (session["user_id"],))

            user = cursor.fetchone()

        finally:
            connection.close()

        # Check whether the account exists
        if user is None:
            session.clear()
            return redirect(url_for("home"))

        # Check administrator permission
        if user[0] != "admin":
            return "Access denied: Administrators only.", 403

        return function(*args, **kwargs)

    return decorated_function

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    return "Welcome to the administrator dashboard!"

# ==========================================
# 3. LOGIN PAGE
# ==========================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("church_home"))

    return render_template("index.html")


# ==========================================
# 4. GOOGLE AUTHENTICATION
# ==========================================

@app.route("/verify-google-token", methods=["POST"])
def verify_google_token():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request data"
        }), 400

    token = data.get("credential")

    if not isinstance(token, str) or not token.strip():
        return jsonify({
            "error": "No valid Google ID token provided"
        }), 400

    try:

        # Verify Google's ID token
        user_data = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Extract verified user information
        google_id = user_data.get("sub")
        name = user_data.get("name")
        email = user_data.get("email")
        picture = user_data.get("picture")

        if (
            not google_id
            or not name
            or not email
            or not user_data.get("email_verified")
        ):
            return jsonify({
                "error": "Required verified Google account information is missing"
            }), 401

        # Connect to the database
        connection = get_db_connection()

        try:

            cursor = connection.cursor()

            # Register user if they don't already exist
            cursor.execute("""
                INSERT OR IGNORE INTO users
                (google_id, name, email, profile_picture)
                VALUES (?, ?, ?, ?)
            """, (google_id, name, email, picture))

            connection.commit()

            # Retrieve the user's database record
            cursor.execute("""
                SELECT id, name, email, profile_picture, role
                FROM users
                WHERE google_id = ?
            """, (google_id,))

            user = cursor.fetchone()

        finally:
            connection.close()

        if user is None:
            return jsonify({
                "error": "Unable to retrieve your account"
            }), 409

        # Create Flask login session
        session.clear()

        session["user_id"] = user[0]

        return jsonify({
            "success": True,
            "message": "Google authentication successful!"
        })

    except ValueError:

        return jsonify({
            "error": "Invalid Google ID token"
        }), 401

    except TransportError:

        return jsonify({
            "error": "Unable to contact Google's authentication service. Please try again."
        }), 503


# ==========================================
# 5. CHURCH HOME PAGE
# ==========================================

@app.route("/home")
def church_home():

    # Check if the user is logged in
    if "user_id" not in session:
        return redirect(url_for("home"))

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, email, profile_picture, role
            FROM users
            WHERE id = ?
        """, (session["user_id"],))

        user = cursor.fetchone()

    finally:
        connection.close()

    # Check if the user exists
    if user is None:
        session.clear()
        return redirect(url_for("home"))

    user_data = {
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "profile_picture": user[3],
        "role": user[4]
    }

    return render_template("home.html", user=user_data)

# ==========================================
# 6. LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==========================================
# 7. RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    from database import create_users_table

    create_users_table()

    app.run(debug=True)