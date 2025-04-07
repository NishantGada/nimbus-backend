from flask import Blueprint, request, jsonify
from dbconfig import get_connection

from helper_functions import fetch_user_id_from_user_email, validate_request

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses/<string:category_name>', methods=['GET'])
def get_total_by_category(category_name):
    category_name = "groceries"
    from_date = request.args.get("from_date")  # Format: YYYY-MM-DD
    to_date = request.args.get("to_date")

    print("category_name:", category_name)
    print("from_date:", from_date)
    print("to_date:", to_date)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)  # Return dicts instead of tuples

    query = """
        SELECT * 
        FROM Expenses 
        WHERE LOWER(expense_category_name) = %s
    """
    params = [category_name]

    if from_date and to_date:
        query += " AND DATE(expense_add_date) BETWEEN %s AND %s"
        params.extend([from_date, to_date])
    elif from_date:
        query += " AND DATE(expense_add_date) >= %s"
        params.append(from_date)
    elif to_date:
        query += " AND DATE(expense_add_date) <= %s"
        params.append(to_date)

    cursor.execute(query, tuple(params))
    expenses = cursor.fetchall()
    print("expenses:", expenses)

    total = sum([float(expense["expense_amount"]) for expense in expenses])

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({
        "total": total,
        "count": len(expenses),
        "expenses": expenses
    })

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

@expenses_bp.route('/expenses/expense/<string:id>', methods=['GET'])
def get_expense_by_id(id):
    print("id: ", id)
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Expenses WHERE expense_id = %s", (id,))
    expense = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    return expense, 201

@expenses_bp.route('/expenses/<string:id>', methods=['GET'])
def get_all_expenses_by_user_id(id):
    print("user id: ", id)
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Expenses WHERE user_id = %s", (id,))
    expenses = cursor.fetchall()

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"data": expenses, "count": len(expenses)})