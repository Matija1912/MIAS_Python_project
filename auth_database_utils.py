from flask import flash, redirect, url_for
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from db_connection import get_db_connection


def get_user_by_id(id):
    query = text("""SELECT * FROM users
                    JOIN companies ON users.company_id = companies.id
                    WHERE users.id = :id""")
    with get_db_connection() as connection:
        result = connection.execute(query, {"id": id}).fetchone()

    return result

def check_for_user(email):
    query = text("SELECT * FROM users WHERE email = :email")
    with get_db_connection() as connection:
        result = connection.execute(query, {"email": email}).fetchone()

    return result

def register_company_user(first_name, last_name, email, password, user):
    query = text("""INSERT INTO 
                    users (first_name, last_name, email, password_hash, company_id)
                    VALUES (:first_name, :last_name, :email, :password_hash, :company_id)
                   """)
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password_hash": generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
                    "company_id": user.company.id
                })
                flash('You have registered a new user!', category='success')
                return redirect(url_for('views.home_page'))
    except Exception as e:
        flash('An error has occurred while registering a new user. Please try again or contact MIAS.', category='error')