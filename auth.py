from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import database

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "username, email, and password are required"}), 400

    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']

    if len(password) < 5:
        return jsonify({"error": "Password must be at least 5 characters"}), 400

    if database.get_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409

    if database.get_user_by_username(username):
        return jsonify({"error": "Username already taken"}), 409

    password_hash = generate_password_hash(password)
    user_id = database.create_user(username, email, password_hash)

    access_token = create_access_token(identity=str(user_id))
    return jsonify({"access_token": access_token}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "email and password are required"}), 400

    email = data['email'].strip().lower()
    user = database.get_user_by_email(email)

    if not user or not check_password_hash(user['password_hash'], data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user['id']))
    return jsonify({"access_token": access_token}), 200
