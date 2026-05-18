import uuid
from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

# Lightweight in-memory user store for instant out-of-the-box local demo run
# Format: { email: { "name": str, "password": str, "id": str } }
USER_DB = {
    "demo@loanlens.ai": {
        "id": "user_demo_123",
        "name": "Sarah Jenkins",
        "password": "password123"
    }
}


@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user in the in-memory database."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not name or not email or not password:
        return jsonify({"error": "All fields are required."}), 400

    if email in USER_DB:
        return jsonify({"error": "Email address already registered."}), 400

    user_id = "user_" + str(uuid.uuid4())[:8]
    USER_DB[email] = {
        "id": user_id,
        "name": name,
        "password": password
    }

    return jsonify({
        "message": "Registration successful!",
        "user": {
            "id": user_id,
            "name": name,
            "email": email
        }
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Validate credentials and return user info."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = USER_DB.get(email)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid email or password credentials."}), 401

    return jsonify({
        "message": "Login successful!",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": email
        }
    }), 200


@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Forgot password request simulation."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({"error": "Email address is required."}), 400

    # Simulate checking database and issuing password reset instructions
    user = USER_DB.get(email)
    if not user:
        return jsonify({"error": "No account associated with this email."}), 404

    # Simulated recovery response
    reset_instructions = (
        f"A secure password recovery instructions link has been sent to {email}. "
        "Please check your inbox (or spam) to finalize credentials reset."
    )

    return jsonify({
        "message": "Reset instructions dispatched!",
        "instructions": reset_instructions
    }), 200


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Clear session simulation."""
    return jsonify({"message": "Logout successful!"}), 200
