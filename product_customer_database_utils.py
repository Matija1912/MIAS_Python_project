from flask import flash
from flask_login import current_user
from sqlalchemy import text

from db_connection import get_db_connection


#PRODUCT UTILS AND MANIPULATION
def get_product_by_id(product_id, company_id):
    query = text("SELECT * FROM products WHERE id = :product_id AND company_id = :company_id LIMIT 1")
    with get_db_connection() as connection:
        result = connection.execute(query, {
            "product_id": product_id,
            "company_id": company_id
        }).fetchone()
    return result

def get_company_products(company_id, limit, offset):
    query = text("SELECT * FROM products WHERE company_id = :company_id LIMIT :limit OFFSET :offset")
    with get_db_connection() as connection:
        result = connection.execute(query, {"company_id": company_id, "limit": limit, "offset": offset}).fetchall()
    return result

def get_company_product_count(company_id):
    query = text("SELECT count(*) FROM products WHERE company_id = :company_id")
    with get_db_connection() as connection:
        result = connection.execute(query, {"company_id": company_id}).fetchone()
    return result

def add_new_product_to_db(_product):
    query = text("""INSERT INTO products 
           (name, description, price_no_vat, vat_percentage, company_id)
           VALUES (:name, :description, :price_no_vat, :vat_percentage, :company_id)
           """)

    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "name": _product.name,
                    "description": _product.description,
                    "price_no_vat": _product.price_no_vat,
                    "vat_percentage": _product.vat_percentage,
                    "company_id": current_user.company.id
                })
                flash('You have added a new product!', category='success')
    except Exception as e:
        flash('An error has occurred while adding a new product. Please try again or contact MIAS.', category='error')


def update_product_info(updated_product_info, product_id):
    query = text("""
        UPDATE products
        SET
        name = :name,
        description = :description,
        price_no_vat = :price_no_vat,
        vat_percentage = :vat_percentage
        WHERE id = :id 
    """)
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "name": updated_product_info.name,
                    "description": updated_product_info.description,
                    "price_no_vat": updated_product_info.price_no_vat,
                    "vat_percentage": updated_product_info.vat_percentage,
                    "id": product_id
                })
                flash('Update successful', category="success")
    except Exception as e:
        flash('An error has occurred while updating product information. Please try again or contact MIAS.', category='error')


def remove_selected_product(product_id, company_id):
    query = text("UPDATE products SET company_id = NULL WHERE id = :product_id AND company_id = :company_id")
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "product_id": product_id,
                    "company_id": company_id
                })
                flash('Product removed', category="success")
    except Exception as e:
        flash('An error has occurred while removing product. Please try again or contact MIAS.',category='error')


#CUSTOMER UTILS AND MANIPULATION
def get_customer_by_id(customer_id, company_id):
    query = text("SELECT * FROM customers WHERE id = :customer_id AND company_id = :company_id LIMIT 1")
    with get_db_connection() as connection:
        result = connection.execute(query, {
            "customer_id": customer_id,
            "company_id": company_id
        }).fetchone()
    return result

def get_company_customers(company_id, limit, offset):
    query = text("SELECT * FROM customers WHERE company_id = :company_id LIMIT :limit OFFSET :offset")
    with get_db_connection() as connection:
        result = connection.execute(query, {"company_id": company_id, "limit": limit, "offset": offset}).fetchall()
    return result

def get_all_company_customers(company_id):
    query = text("SELECT * FROM customers WHERE company_id = :company_id")
    with get_db_connection() as connection:
        result = connection.execute(query, {"company_id": company_id}).fetchall()
    return result

def get_company_customers_count(company_id):
    query = text("SELECT count(*) FROM customers WHERE company_id = :company_id")
    with get_db_connection() as connection:
        result = connection.execute(query, {"company_id": company_id}).fetchone()
    return result

def add_new_customer_to_db(_customer):
    query = text("""INSERT INTO customers 
           (name, email, street, post_number, city, country, vat_id, registration_number, phone, fax, company_id)
           VALUES (:name, :email, :street, :post_number, :city, :country, :vat_id, NULL, NULL, NULL, :company_id)
           """)

    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "name": _customer.name,
                    "email": _customer.email,
                    "street": _customer.address,
                    "post_number": _customer.postal_code,
                    "city": _customer.city,
                    "country": _customer.country,
                    "vat_id": _customer.vat_id,
                    "company_id": current_user.company.id
                })
                flash('You have added a new customer!', category='success')
    except Exception as e:
        flash('An error has occurred while adding a new customer. Please try again or contact MIAS.', category='error')


def update_customer_info(updated_customer_info, customer_id):
    query = text("""UPDATE customers
                SET 
                name = :name, 
                email = :email, 
                street = :street, 
                post_number = :post_number, 
                city = :city, 
                country = :country, 
                vat_id = :vat_id 
                WHERE id = :id
                """)
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "name": updated_customer_info.name,
                    "email": updated_customer_info.email,
                    "street": updated_customer_info.address,
                    "post_number": updated_customer_info.postal_code,
                    "city": updated_customer_info.city,
                    "country": updated_customer_info.country,
                    "vat_id": updated_customer_info.vat_id,
                    "id": customer_id
                })
                flash('Update successful', category="success")
    except Exception as e:
        flash('An error has occurred while updating customer information. Please try again or contact MIAS.', category='error')

def remove_selected_customer(customer_id, company_id):
    query = text("UPDATE customers SET company_id = NULL WHERE id = :customer_id AND company_id = :company_id")
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "customer_id": customer_id,
                    "company_id": company_id
                })
                flash('Customer removed', category="success")
    except Exception as e:
        flash('An error has occurred while removing customer. Please try again or contact MIAS.',category='error')

