from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import render_template, Blueprint, request, redirect, url_for
from flask_login import login_required
from models import Customer, Product, Invoice

#DATABSE UTILS
from product_customer_database_utils import *
from invoice_proforma_database_utils import *


mInvoicesViews = Blueprint('mInvoicesViews', __name__)


@mInvoicesViews.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        cid = request.form.get('customer_id')
        remove_selected_customer(cid, current_user.company.id)
        return redirect(url_for('mInvoicesViews.customers'))

    page = request.args.get('page', 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page
    customer_count = get_company_customers_count(current_user.company.id)[0]
    page_count = ((customer_count - 1) // per_page) + 1
    _customers = get_company_customers(current_user.company.id, per_page, offset)

    return render_template('customers.html', user=current_user, customers=_customers, page=page, per_page=per_page,
                           page_count=page_count)

@mInvoicesViews.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        pid = request.form.get("product_id")
        remove_selected_product(pid, current_user.company.id)
        return redirect(url_for('mInvoicesViews.products'))
    page = request.args.get('page', 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page
    product_count = get_company_product_count(current_user.company.id)[0]
    page_count = ((product_count - 1) // per_page) + 1
    _products = get_company_products(current_user.company.id, per_page, offset)
    return render_template('products.html', user=current_user, products=_products, page=page, per_page=per_page, page_count=page_count)

@mInvoicesViews.route('/customers/newCustomer', methods=['GET', 'POST'])
@login_required
def add_new_customer():
    if request.method == 'POST':
        name = request.form.get('customer-name')
        email = request.form.get('customer-email')
        address = request.form.get('customer-address')
        postal_code = request.form.get('customer-postal-code')
        city = request.form.get('customer-city')
        country = request.form.get('customer-country')
        vat_id = request.form.get('customer-id')
        if name and address and postal_code and city and country and vat_id:
            new_customer = Customer(name, email, address, postal_code, city, country, vat_id)

            add_new_customer_to_db(new_customer)
        else:
            flash('Please fill out the form.', category='error')
    return render_template('newCustomer.html', user=current_user)

@mInvoicesViews.route('/products/newProduct', methods=['GET', 'POST'])
@login_required
def add_new_product():
    if request.method == 'POST':
        name = request.form.get('product-name')
        description = request.form.get('product-description')
        price_no_vat = request.form.get('product-price')
        vat_percentage = request.form.get('product-vat')

        if name and price_no_vat and vat_percentage:
            try:
                _price = Decimal(price_no_vat)
                _vat = Decimal(vat_percentage)

                new_product = Product(name, description, float(_price), float(_vat))
                add_new_product_to_db(new_product)

            except InvalidOperation:
                flash('Enter valid values', category='error')
        else:
            flash('Please fill out the form.', category='error')

    return render_template('newProduct.html', user=current_user)


@mInvoicesViews.route('/customers/customer', methods=['GET', 'POST'])
@login_required
def customer():
    customer_id = request.args.get('id')
    res = get_customer_by_id(customer_id, current_user.company.id)
    if res:
        selected_customer = Customer(res[1], res[2], res[3], res[4], res[5], res[6], res[7])
        if request.method == 'POST':

            name = request.form.get('customer-name')
            email = request.form.get('customer-email')
            address = request.form.get('customer-address')
            postal_code = request.form.get('customer-postal-code')
            city = request.form.get('customer-city')
            country = request.form.get('customer-country')
            vat_id = request.form.get('customer-id')

            updated_customer_info = Customer(name, email, address, postal_code, city, country, vat_id)
            update_customer_info(updated_customer_info, customer_id)

            return redirect(url_for('mInvoicesViews.customers'))


        return render_template('customer.html', user=current_user, customer=selected_customer)
    else:
        return redirect(url_for('mInvoicesViews.customers'))

@mInvoicesViews.route('/products/product', methods=['GET', 'POST'])
@login_required
def product():
    product_id = request.args.get('id')
    res = get_product_by_id(product_id, current_user.company.id)
    if res:
        _price = Decimal(res[3])
        _vat = Decimal(res[4])
        selected_product = Product(res[1], res[2], _price, _vat)
        if request.method == 'POST':
            name = request.form.get('product-name')
            description = request.form.get('product-description')
            price = request.form.get('product-price')
            vat = request.form.get('product-vat')

            updated_product_info = Product(name, description, price, vat)
            update_product_info(updated_product_info, product_id)

            return redirect(url_for('mInvoicesViews.products'))

        return render_template('product.html', user=current_user, product=selected_product)
    else:
        return redirect(url_for('mInvoicesViews.products'))


@mInvoicesViews.route('/invoices', methods=['GET', 'POST'])
@login_required
def invoices():
    if request.method == 'POST':
        invoice_id = request.form.get("invoice_id")
        remove_selected_invoice(invoice_id, current_user.company.id)
        return redirect(url_for('mInvoicesViews.invoices'))

    page = request.args.get('page', 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page
    invoice_count = get_company_invoice_count(current_user.company.id)[0]
    page_count = ((invoice_count - 1) // per_page) + 1
    _invoices = get_company_invoices(current_user.company.id, per_page, offset)

    return render_template('invoices.html', user=current_user, invoices=_invoices, page=page, per_page=per_page, page_count=page_count)


@mInvoicesViews.route('/invoices/newInvoice', methods=['GET', 'POST'])
@login_required
def newInvoice():

    _customers = get_all_company_customers(current_user.company.id)
    current_dt = datetime.now()
    current_year = "{:04d}".format(current_dt.year)
    current_date = "{:02d}".format(current_dt.month) + "-" + "{:02d}".format(current_dt.day)
    current_time = "{:02d}".format(current_dt.hour) + ":" + "{:02d}".format(current_dt.minute)
    if request.method == "POST":
        invoice_number = request.form.get('invoice-number')
        invoice_date_time = datetime.strptime(request.form.get('invoice-date-time'), '%Y-%m-%dT%H:%M')
        customer_id = request.form.get('customer-id')
        invoice_note = request.form.get('invoice-note')
        invoice_with_vat = request.form.get('invoice-with-vat')
        if invoice_with_vat:
            invoice_with_vat = True
        else:
            invoice_with_vat = False

        if invoice_date_time and customer_id:
            if not invoice_number:
                invoice = Invoice(customer_id, None, 1, 1, invoice_date_time, "Pending", invoice_with_vat,
                                  invoice_note)
                create_new_invoice_auto_gen(current_user.company.id, invoice, invoice_date_time.year)
            else:
                try:
                    _invoice_number = int(invoice_number)
                    invoice = Invoice(customer_id, _invoice_number, 1, 1, invoice_date_time, "Pending", invoice_with_vat,
                                      invoice_note)
                    create_new_invoice(current_user.company.id, invoice, invoice_date_time.year)
                except ValueError:
                    flash('Invoice number can not be a string', category='error')
        else:
            flash('Please fill out the form', category='error')
    return render_template('newInvoice.html', user=current_user, customers=_customers, current_year=current_year, current_date=current_date, current_time=current_time)