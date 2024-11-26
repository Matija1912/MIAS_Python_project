from flask import render_template, Blueprint, request, flash, url_for, redirect, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import User
from auth_database_utils import *
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        res = check_for_user(email)
        if res:
            if check_password_hash(res[2], password):
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

@auth.route('/registerUser', methods=['GET', 'POST'])
@login_required
def register_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password')
        password2 = request.form.get('re-enter-password')
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')

        if email and password1 and password2 and first_name and last_name:
            if password1 == password2:
                if check_for_user(email):
                    flash('User with this email already exists.', category='error')
                else:
                    register_company_user(first_name, last_name, email, password1, current_user)

            else:
                flash('Passwords do not match.', category='error')
        else:
            flash('Please fill in all the fields.', category='error')

    return render_template('registerUser.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))