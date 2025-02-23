from flask import Blueprint, request, jsonify
from dbconfig import get_connection
import uuid

from helper_functions import fetch_user_id_from_user_email, validate_request

links_bp = Blueprint('links', __name__)

@links_bp.route('/links', methods=['POST'])
def add_new_link():
    data = request.json
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    validate_request(data.get('link'), data.get('link_desc'), data.get('link_category_name'), data.get('user_email'))

    user_id = fetch_user_id_from_user_email(data['user_email'])

    cursor.execute("SELECT link FROM Links where user_id = %s", (user_id,))
    all_links = [row["link"] for row in cursor.fetchall()]
    if data.get('link') in all_links:
        return jsonify({"error": "Link already exists!"}), 400

    cursor.execute("SELECT link_category_id FROM LinkCategories WHERE link_category_name = %s", (data.get('link_category_name'),))
    link_category_id = cursor.fetchone()
    if link_category_id is None or not link_category_id:
        return jsonify({"error": "Incorrect Link Category!"}), 404

    query = """
    INSERT INTO Links (link, link_desc, link_category_name, user_id)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (data.get('link'), data['link_desc'], data['link_category_name'], user_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Link added successfully!"}), 201

@links_bp.route('/links', methods=['GET'])
def get_all_links():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Links")
    links = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({"links": links, "count": len(links)})

@links_bp.route('/links/<link_id>', methods=['DELETE'])
def delete_link_by_id(link_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("DELETE FROM Links WHERE link_id = %s", (link_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return jsonify({"message": "Link deleted successfully!"})

@links_bp.route('/links/all', methods=['DELETE'])
def delete_all_notes():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("DELETE FROM Links;")
    connection.commit()
    
    cursor.close()
    connection.close()

    return jsonify({"message": "All Links deleted successfully"}), 200