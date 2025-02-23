from flask import Blueprint, request, jsonify
from dbconfig import get_connection
import uuid

from helper_functions import validate_request

link_categories_bp = Blueprint('link_categories', __name__)

@link_categories_bp.route('/link_categories', methods=['POST'])
def add_category():
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to get results as dict

    validate_request(data.get('link_category_name'))

    cursor.execute("SELECT link_category_name FROM LinkCategories")
    link_category_names = {row["link_category_name"] for row in cursor.fetchall()}

    if data["link_category_name"] in link_category_names:
        return jsonify({"error": "Category already exists!"}), 400

    query = """
    INSERT INTO LinkCategories (link_category_name) VALUES (%s)
    """
    cursor.execute(query, (data['link_category_name'],))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({ "message": "Category added successfully!" }), 201

@link_categories_bp.route('/link_categories', methods=['GET'])
def get_all_note_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM LinkCategories")
    link_categories = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return jsonify({"link_categories": link_categories, "count": len(link_categories)})