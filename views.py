from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def home_page():
    return render_template('home.html', title='Welcom to Motorsport innovations and solutions', user=current_user)

@views.route('/mInvoices', methods=['GET'])
@login_required
def mInvoices():
    return render_template('mInvoices.html',title='mInvoices', user=current_user)

@views.route('/mStock', methods=['GET'])
@login_required
def mStock():
    return render_template('mStock.html', title='mStock', user=current_user)