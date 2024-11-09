from flask import render_template, Blueprint, request, flash, url_for, redirect, session
from flask_login import login_user, logout_user, login_required, current_user
from db_connection import get_db_connection
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
auth = Blueprint('auth', __name__)

def get_user_by_id(id):
    query = text("""SELECT * FROM users
                    JOIN companies ON users.id = companies.id
                    WHERE users.id = :id""")
    with get_db_connection() as connection:
        result = connection.execute(query, {"id": id}).fetchone()

    return result

def check_for_user(email):
    query = text("SELECT * FROM users WHERE email = :email")
    with get_db_connection() as connection:
        result = connection.execute(query, {"email": email}).fetchone()

    return result
def check_password(password):
    pass

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        res = check_for_user(email)
        if res:
            if(check_password_hash(res[2], password)):
                user = User(res[0], res[1], res[3], res[4], res[5], res[6])
                user.is_auth = True
                login_user(user)
                session['_user_id'] = user.id
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.home_page'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('User does not exist', category='error')


    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))