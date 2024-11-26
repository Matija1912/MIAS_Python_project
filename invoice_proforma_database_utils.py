from flask import flash
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db_connection import get_db_connection

def get_company_invoices(company_id, limit, offset):
    query = text("""SELECT i.*, c.name AS customer_name, DATE(i.created_at) as formatted_date FROM invoices i
                    INNER JOIN customers c 
                    ON c.id = i.customer_id
                    WHERE i.company_id = :company_id ORDER BY YEAR(i.created_at) DESC, i.invoice_number DESC LIMIT :limit OFFSET :offset
                    """)
    with get_db_connection() as connection:
        result = connection.execute(query, {
            "company_id": company_id,
            "limit": limit,
            "offset": offset
        }).fetchall()
    return result


def get_company_invoice_count(company_id):
    query = text("SELECT count(*) FROM invoices WHERE company_id = :company_id")
    with get_db_connection() as connection:
        result = connection.execute(query, {"company_id": company_id}).fetchone()
    return result

def create_new_invoice(company_id ,invoice, _year):
    query = text("""INSERT INTO invoices
                 (customer_id, invoice_with_vat, created_at, invoice_number, invoice_office_number, invoice_device_number, company_id, note)
                  VALUES (:customer_id, :invoice_with_vat, :created_at, :invoice_number, :invoice_office_number, :invoice_device_number, :company_id, :note)
                """)
    update_counter_query = text("""CALL UpdateInvoiceCounter(:_company_id, :_year, :_invoice_number)""")
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(update_counter_query, {
                    "_company_id": company_id,
                    "_year": _year,
                    "_invoice_number": invoice.invoice_number
                })

                connection.execute(query, {
                    "customer_id": invoice.customer_id,
                    "invoice_with_vat": invoice.with_vat,
                    "created_at": invoice.created_at,
                    "invoice_number": invoice.invoice_number,
                    "invoice_office_number": invoice.invoice_office_number,
                    "invoice_device_number": invoice.invoice_device_number,
                    "company_id": company_id,
                    "note": invoice.note
                })

                flash('You have created a new invoice!', category='success')
    except IntegrityError as e:
        flash("Invoice with that number already exists.", category='error')
    except Exception as e:
        flash('An error has occurred while creating a new invoice. Please try again or contact MIAS.', category='error')

def create_new_invoice_auto_gen(company_id ,invoice, _year):
    query = text("""INSERT INTO invoices
                     (customer_id, invoice_with_vat, created_at, invoice_number, invoice_office_number, invoice_device_number, company_id, note)
                      VALUES (:customer_id, :invoice_with_vat, :created_at, :invoice_number, :invoice_office_number, :invoice_device_number, :company_id, :note)
                    """)
    update_counter_query = text("""CALL  UpdateInvoiceCounterAutoGen(:_company_id, :_year)""")
    get_next_invoice_number_query = text("SELECT next_invoice_number FROM invoice_counter WHERE company_id = :company_id AND year = :invoice_year")
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(update_counter_query, {
                    "_company_id": company_id,
                    "_year": _year,
                })

                next_invoice_number = connection.execute(get_next_invoice_number_query, {
                    "company_id": company_id,
                    "invoice_year": _year
                }).fetchone()

                connection.execute(query, {
                    "customer_id": invoice.customer_id,
                    "invoice_with_vat": invoice.with_vat,
                    "created_at": invoice.created_at,
                    "invoice_number": next_invoice_number[0],
                    "invoice_office_number": invoice.invoice_office_number,
                    "invoice_device_number": invoice.invoice_device_number,
                    "company_id": company_id,
                    "note": invoice.note
                })

                flash('You have created a new invoice!', category='success')
    except IntegrityError as e:
        flash("Invoice with that number already exists.", category='error')
    except Exception as e:
        flash('An error has occurred while adding a new product. Please try again or contact MIAS.', category='error')


def remove_selected_invoice(invoice_id, company_id):
    query = text("""CALL RemoveInvoiceAndUpdateCounter(:in_invoice_id, :in_company_id)""")
    try:
        with get_db_connection() as connection:
            with connection.begin():
                connection.execute(query, {
                    "in_invoice_id": invoice_id,
                    "in_company_id": company_id
                })
                flash('Invoice removed', category="success")
    except Exception as e:
        flash('An error has occurred while removing an invoice. Please try again or contact MIAS.',category='error')
