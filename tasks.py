from flask import Blueprint, request, jsonify
from dbconfig import get_connection
import uuid

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['POST'])
def add_task():
    """Add a new task for a user"""
    data = request.json

    connection = get_connection()
    cursor = connection.cursor()

    if not all([
        data.get('title'),
        data.get('description'),
        data.get('due_date'),
        data.get('status'),
        data.get('priority'),
        data.get('user_email')
    ]):
        print("Request body error!")
        return jsonify({"error": "Error in request body"}), 400

    # Fetch user_id
    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (data['user_email'],))
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

@tasks_bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    """Fetch all tasks"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Tasks")
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(tasks)

@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task_by_id(task_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Tasks WHERE task_id = %s", (task_id,))
    task = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify(task)

@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
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

@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Tasks WHERE task_id = %s", (task_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return jsonify({"message": "Task deleted successfully!"})

@tasks_bp.route('/tasks/user/<user_id>', methods=['GET'])
def get_tasks_by_user_id(user_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    print("user_id: ", user_id)

    cursor.execute("SELECT * FROM Tasks where user_id = %s", (user_id,))
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(tasks)