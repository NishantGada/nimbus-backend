from flask import Blueprint, request, jsonify
from dbconfig import get_connection
import uuid

noteCategories_bp = Blueprint('noteCategories', __name__)

@noteCategories_bp.route('/note-categories', methods=['GET'])
def get_all_note_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM NoteCategories")
    noteCategories = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return jsonify(noteCategories)

@noteCategories_bp.route('/note-categories', methods=['POST'])
def add_category():
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to get results as dict

    cursor.execute("SELECT category_name FROM NoteCategories")
    noteCategoryNames = {row["category_name"] for row in cursor.fetchall()}  # Convert to a set for faster lookup

    print("noteCategoryNames: ", noteCategoryNames)
    print(data["name"] in noteCategoryNames)  # This will now work correctly

    if data["name"] in noteCategoryNames:
        return jsonify({"error": "Category already exists!"}), 400

    category_id = str(uuid.uuid4())
    query = """
    INSERT INTO NoteCategories (category_id, category_name) 
    VALUES (%s, %s)
    """

    # cursor.execute(query, (category_id, data['name']))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Category added successfully!", "category_id": category_id}), 201