from flask import Blueprint, request, jsonify
from dbconfig import get_connection
import uuid

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['POST'])
def create_user_logic():
    """API endpoint to create a user"""
    data = request.get_json()  # Get JSON data from the request body

    # Validate the required fields
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    try:
        create_user(name, email, password)
        return jsonify({"message": "User created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_user(name, email, password):
    """Creates a new user"""
    connection = get_connection()
    cursor = connection.cursor()
    
    user_id = str(uuid.uuid4())
    query = "INSERT INTO Users (user_id, name, email, password) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (user_id, name, email, password))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print(f"User {name} created successfully!")

@users_bp.route('/users', methods=['GET'])
def get_all_users():
    """Fetch all users"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to return column names in results

    cursor.execute("SELECT user_id, name, email FROM Users")
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({"users": users})