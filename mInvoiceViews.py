from flask import render_template, Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import text
from db_connection import get_db_connection

def check_for_user(email):
    query = text("SELECT * FROM companies WHERE email = :email")
    with get_db_connection() as connection:
        result = connection.execute(query, {"email": email}).fetchone()

    return result

def get_users_customers(user_id, limit, offset):
    query = text("SELECT * FROM customers WHERE user_id = :user_id LIMIT :limit OFFSET :offset")
    with get_db_connection() as connection:
        result = connection.execute(query, {"user_id": user_id, "limit": limit, "offset": offset}).fetchall()
    return result

def get_users_customers_count(user_id):
    query = text("SELECT count(*) FROM customers WHERE user_id = :user_id")
    with get_db_connection() as connection:
        result = connection.execute(query, {"user_id": user_id}).fetchone()
    return result

mInvoicesViews = Blueprint('mInvoicesViews', __name__)

@mInvoicesViews.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page
    customer_count = get_users_customers_count(current_user.id)[0]
    page_count = ((customer_count - 1)  // per_page) + 1
    _customers = get_users_customers(current_user.id, per_page, offset)

    return render_template('customers.html', user=current_user, customers=_customers, page=page, per_page=per_page, page_count=page_count)

@mInvoicesViews.route('/invoices', methods=['GET', 'POST'])
@login_required
def invoices():
    return render_template('invoices.html', user=current_user)