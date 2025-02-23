from flask import jsonify
from dbconfig import get_connection

def validate_request(*args):
    if not all([ args ]):
        print("Request body error!")
        return jsonify({"error": "Error in request body"}), 400
    return None

def fetch_user_id_from_user_email(user_email):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (user_email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": "User not found!"}), 404
    user_id = user[0]
    return user_id
    