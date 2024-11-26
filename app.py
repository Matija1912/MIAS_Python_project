from flask import Flask, session, redirect, url_for, flash
from flask_login import LoginManager, logout_user
from auth import get_user_by_id
from models import User
from models import Company
from datetime import timedelta, datetime

app = Flask(__name__)

from api.api import api
from views import views
from auth import auth
from mInvoiceViews import mInvoicesViews

# ONLY IN DEVELOPMENT
app.config['SECRET_KEY'] = 'mias'

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(mInvoicesViews, url_prefix='/mInvoices')

login_manager = LoginManager()
login_manager.login_message_category = "info"
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


# LOGIC FOR SESSION EXPIRATION
@app.before_request
def function_before_request():
    if '_user_id' in session:
        now = datetime.now()
        last_activity = session.get('_last_activity')
        if last_activity:
            time_passed = now - datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if time_passed > timedelta(minutes=45):
                logout_user()
                session.clear()
                flash('Session expired!', category='error')
                return redirect(url_for('auth.login', message="Session expired."))
        session['_last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S')


@login_manager.user_loader
def load_user(_id):
    res = get_user_by_id(_id)
    if res:
        company = Company(res[7], res[8], res[9], res[10], res[11], res[12])
        user = User(res[0], res[1], res[3], res[4], company, res[6])
        return user


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
