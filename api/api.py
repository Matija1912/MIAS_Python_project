from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from product_customer_database_utils import get_company_products

api = Blueprint('api', __name__)


@api.route('fetch-products', methods=['GET'])
@login_required
def fetch_products():
    company_id = current_user.company.id
    limit = 25
    offset = 0
    products = get_company_products(company_id, limit, offset)
    keys = ['id', 'name', 'description', 'price', 'vat_percentage', 'stock', 'company_id', 'vat_status']
    dict_list = [dict(zip(keys, product)) for product in products]
    return jsonify(dict_list)
