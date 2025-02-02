from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

from dbconfig import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask API"})

# ---------------------- User Routes ----------------------

@app.route('/users', methods=['POST'])
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

@app.route('/users', methods=['GET'])
def get_all_users():
    """Fetch all users"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to return column names in results

    cursor.execute("SELECT user_id, name, email FROM Users")
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({"users": users})

# ---------------------- Task Routes ----------------------

@app.route('/tasks', methods=['POST'])
def add_task():
    """Add a new task for a user"""
    data = request.json

    connection = get_connection()
    cursor = connection.cursor()

    # Fetch user_id
    cursor.execute("SELECT user_id FROM Users WHERE user_id = %s", (data['user_id'],))
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": "User not found!"}), 404
    user_id = user[0]

    task_id = str(uuid.uuid4())
    query = """
    INSERT INTO Tasks (task_id, title, description, status, priority, due_date, user_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (task_id, data['title'], data['description'], data['status'], data['priority'], data['due_date'], user_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Task added successfully!", "task_id": task_id}), 201

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    """Fetch all tasks"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Tasks")
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(tasks)

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task_by_id(task_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Tasks WHERE task_id = %s", (task_id,))
    task = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify(task)

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    data = request.json
    connection = get_connection()
    cursor = connection.cursor()

    updated_fields = []
    values = []

    if 'title' in data:
        updated_fields.append("title = %s")
        values.append(data['title'])
    if 'description' in data:
        updated_fields.append("description = %s")
        values.append(data['description'])
    if 'status' in data:
        updated_fields.append("status = %s")
        values.append(data['status'])
    if 'priority' in data:
        updated_fields.append("priority = %s")
        values.append(data['priority'])
    if 'due_date' in data:
        updated_fields.append("due_date = %s")
        values.append(data['due_date'])

    if not updated_fields:
        return jsonify({"error": "No fields to update!"}), 400

    values.append(task_id)
    update_query = f"UPDATE Tasks SET {', '.join(updated_fields)} WHERE task_id = %s"
    cursor.execute(update_query, tuple(values))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Task updated successfully!"})

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Tasks WHERE task_id = %s", (task_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return jsonify({"message": "Task deleted successfully!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)