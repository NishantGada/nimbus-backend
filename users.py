from flask import Blueprint, request, jsonify
from dbconfig import get_connection
import uuid

from helper_functions import fetch_user_id_from_user_email

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
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT user_id, name, email FROM Users")
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({"users": users})

@users_bp.route('/users/details', methods=['POST'])
def get_user_details():
    data = request.json
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    user_id = fetch_user_id_from_user_email(data['user_email'])

    cursor.execute("SELECT * FROM Users where user_id = %s", (user_id,))
    user_details = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify({"user_details": user_details})

@users_bp.route('/users', methods=['PUT'])
def update_user_details():
    data = request.json

    # Remove the user_id from the update data (you don't want to update the ID)
    fields_to_update = {key: value for key, value in data.items() if key not in ['user_id', 'created_at']}
    print("fields_to_update: ", fields_to_update)
    
    if not fields_to_update:
        return jsonify({"status": "error", "message": "No fields to update"}), 400
    
    # Generate the SET part of the query dynamically based on fields provided
    set_clause = ', '.join([f"{key} = %s" for key in fields_to_update.keys()])
    values = list(fields_to_update.values())

    # Construct the SQL query
    query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
    values.append(data["user_id"])

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query, values)
        connection.commit()

        return jsonify({"status": "success", "message": "User details updated successfully"}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
