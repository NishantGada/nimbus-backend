from flask import Blueprint, request, jsonify
from dbconfig import get_connection

from helper_functions import fetch_user_id_from_user_email, validate_request

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['POST'])
def get_expense_by_user():
    data = request.json
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    validate_request(data)

    user_id = fetch_user_id_from_user_email(data.get('user_email'))

    query = """
    INSERT INTO Expenses (expense_name, expense_desc, expense_amount, expense_category_name, user_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (data['expense_name'], data['expense_desc'], data['expense_amount'], data['expense_category_name'], user_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Expense added successfully!"}), 201
