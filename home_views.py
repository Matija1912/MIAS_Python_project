from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from product_customer_database_utils import get_company_product_count, get_company_products

home_views = Blueprint('home_views', __name__)


@home_views.route('/', methods=['GET'])
def home_page():
    return render_template('home.html', title='Welcom to Motorsport innovations and solutions', user=current_user)


@home_views.route('/mInvoices', methods=['GET'])
@login_required
def mInvoices():
    return render_template('mInvoices.html', title='mInvoices', user=current_user)


@home_views.route('/mStock', methods=['GET'])
@login_required
def mStock():
    page = request.args.get('page', 1, type=int)
    per_page = 25
    offset = (page - 1) * page
    product_count = get_company_product_count(current_user.company.id)[0]
    page_count = ((product_count - 1) // per_page) + 1
    _products = get_company_products(current_user.company.id, per_page, offset)
    return render_template('mStock.html', title='mStock', products=_products, user=current_user, page=page, page_count=page_count)
