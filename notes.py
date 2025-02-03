from flask import Blueprint, request, jsonify
from dbconfig import get_connection
import uuid

notes_bp = Blueprint('notes', __name__)

# ✅ Create a new note
@notes_bp.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    user_email = data.get("user_email")
    category = data.get("category")

    if not all([title, description, user_email, category]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT category_id FROM NoteCategories where category_name = %s", (category,))
    category_id = cursor.fetchone()

    if not category_id:
        return jsonify({"error": "Category not found"}), 400
    
    cursor.execute("SELECT user_id FROM Users where email = %s", (user_email,))
    user_email = cursor.fetchone()
    print("user_email: ", user_email)

    if not user_email:
        return jsonify({"error": "Email not found"}), 400
    
    category_id = category_id["category_id"]
    user_id = user_email["user_id"]
    note_id = str(uuid.uuid4())
    
    query = "INSERT INTO Notes (note_id, title, description, user_id, category_id) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (note_id, title, description, user_id, category_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Note created successfully", "note_id": note_id}), 201

# ✅ Get all notes
@notes_bp.route('/notes', methods=['GET'])
def get_notes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(notes)

# ✅ Get a single note by ID
@notes_bp.route('/notes/<note_id>', methods=['GET'])
def get_note(note_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes WHERE note_id = %s", (note_id,))
    note = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note)

# ✅ Update a note
@notes_bp.route('/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    category = data.get("category")

    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE notes SET title = %s, description = %s, category = %s WHERE note_id = %s"
    cursor.execute(query, (title, description, category, note_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Note updated successfully"}), 200

# ✅ Delete a note
@notes_bp.route('/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE note_id = %s", (note_id,))
    conn.commit()
    
    cursor.close()
    conn.close()

    return jsonify({"message": "Note deleted successfully"}), 200
