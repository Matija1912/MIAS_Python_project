from flask import flash, jsonify
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db_connection import get_db_connection


def get_invoice_by_id(invoice_id, company_id):
    invoice_query = text("""
        SELECT i.*, c.id, c.name
        FROM invoices i
        JOIN customers c ON c.id = i.customer_id
        WHERE i.id = :invoice_id AND i.company_id = :company_id
    """)

    invoice_items_query = text("""
                    SELECT p.name, ii.*
                    FROM 
                    invoice_items ii
                    JOIN products p ON p.id = ii.product_id
                    WHERE ii.invoice_id = :invoice_id
    """)

    with get_db_connection() as connection:
        invoice_result = connection.execute(invoice_query, {
            "invoice_id": invoice_id,
            "company_id": company_id
        }).fetchone()

        invoice_items_result = connection.execute(invoice_items_query, {
            "invoice_id": invoice_id
        }).fetchall()
        invoice_items_list = []
        if invoice_items_result:
            for e in invoice_items_result:
                invoice_items_list.append({
                    "product_id": e[3],
                    "product_name": e[0],
                    "product_description": e[7],
                    "price_no_vat": e[6],
                    "quantity": e[4],
                    "vat_percentage": e[8],
                    "discount_percentage": e[5],
                })

        if invoice_result:
            result = {
                "invoice": invoice_result,
                "invoice_items": invoice_items_list
            }
        else:
            result = None
    return result


def get_company_invoices(company_id, limit, offset):
    query = text("""
                    SELECT 
                        i.*,
                        c.name as customer_name,
                        DATE(i.created_at) as formatted_date,
                        ROUND(SUM(ii.product_price_no_vat * ii.quantity), 2) AS subtotal,
                        ROUND(SUM((ii.product_price_no_vat * ii.quantity) * (1 - (ii.discount / 100))), 2) AS discounted_total,
                        ROUND(SUM((ii.product_price_no_vat * ii.quantity) * (1 - (ii.discount / 100)) * (1 + (ii.vat_percentage / 100))), 2) AS total_with_vat
                    FROM
                    invoices i
                    JOIN customers c
                    on c.id = i.customer_id
                    JOIN invoice_items ii 
                    ON ii.invoice_id = i.id 
                    WHERE i.company_id = :company_id
                    GROUP BY i.id
                    ORDER BY YEAR(i.created_at) DESC, i.invoice_number DESC LIMIT :limit OFFSET :offset
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


def create_new_invoice(company_id, invoice, _year, invoice_products):
    query = text("""INSERT INTO invoices
                 (customer_id, invoice_with_vat, created_at, invoice_number, invoice_office_number, invoice_device_number, company_id, note)
                  VALUES (:customer_id, :invoice_with_vat, :created_at, :invoice_number, :invoice_office_number, :invoice_device_number, :company_id, :note)
                """)
    update_counter_query = text("""CALL UpdateInvoiceCounter(:_company_id, :_year, :_invoice_number)""")
    query_last_inserted_invoice = text("""
            SELECT id 
            FROM
            invoices
            WHERE company_id = :company_id
              AND invoice_number = :invoice_number
              AND invoice_year = :invoice_year
            LIMIT 1
        """)
    query_items = text("""
            INSERT INTO invoice_items (invoice_id, product_id, quantity, discount, product_price_no_vat, product_description, vat_percentage, product_name)
            VALUES (:invoice_id, :product_id, :quantity, :discount, :product_price_no_vat, :product_description, :vat_percentage, :product_name)
        """)
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

                last_insert_id = connection.execute(query_last_inserted_invoice, {
                    "invoice_number": invoice.invoice_number,
                    "invoice_year": _year,
                    "company_id": company_id
                }).fetchone()[0]

                for item in invoice_products:
                    connection.execute(query_items, {
                        "invoice_id": last_insert_id,
                        "product_id": item.get('id'),
                        "quantity": item.get('quantity'),
                        "discount": item.get('discount'),
                        "product_price_no_vat": item.get('price'),
                        "product_description": item.get('description'),
                        "vat_percentage": item.get('vatPercentage'),
                        "product_name": item.get('productName')
                    })

                return jsonify({'message': "Invoice created!"}), 201
    except IntegrityError as e:
        return jsonify({'error': "Invoice with that number already exists!"}), 400
    except Exception as e:
        return jsonify(
            {'error': "An error has occurred while adding a new product. Please try again or contact MIAS."}), 400


def create_new_invoice_auto_gen(company_id, invoice, _year, invoice_products):
    query = text("""INSERT INTO invoices
                     (customer_id, invoice_with_vat, created_at, invoice_number, invoice_office_number, invoice_device_number, company_id, note)
                      VALUES (:customer_id, :invoice_with_vat, :created_at, :invoice_number, :invoice_office_number, :invoice_device_number, :company_id, :note)
                    """)
    update_counter_query = text("""CALL  UpdateInvoiceCounterAutoGen(:_company_id, :_year)""")
    get_next_invoice_number_query = text(
        "SELECT next_invoice_number FROM invoice_counter WHERE company_id = :company_id AND year = :invoice_year")
    query_last_inserted_invoice = text("""
        SELECT id 
        FROM
        invoices
        WHERE company_id = :company_id
          AND invoice_number = :invoice_number
          AND invoice_year = :invoice_year
        LIMIT 1
    """)
    query_items = text("""
        INSERT INTO invoice_items (invoice_id, product_id, quantity, discount, product_price_no_vat, product_description, vat_percentage, product_name)
        VALUES (:invoice_id, :product_id, :quantity, :discount, :product_price_no_vat, :product_description, :vat_percentage, :product_name)
    """)
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

                last_insert_id = connection.execute(query_last_inserted_invoice, {
                    "invoice_number": next_invoice_number[0],
                    "invoice_year": _year,
                    "company_id": company_id
                }).fetchone()[0]

                for item in invoice_products:
                    connection.execute(query_items, {
                        "invoice_id": last_insert_id,
                        "product_id": item.get('id'),
                        "quantity": item.get('quantity'),
                        "discount": item.get('discount'),
                        "product_price_no_vat": item.get('price'),
                        "product_description": item.get('description'),
                        "vat_percentage": item.get('vatPercentage'),
                        "product_name": item.get('productName')
                    })

                return jsonify({'message': "Invoice created!"}), 201
    except IntegrityError as e:
        return jsonify({'error': "Invoice with that number already exists!"}), 400
    except Exception as e:
        return jsonify(
            {'error': "An error has occurred while adding a new product. Please try again or contact MIAS."}), 400


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
        flash('An error has occurred while removing an invoice. Please try again or contact MIAS.', category='error')

def update_selected_invoice(invoice_id, company_id, invoice_items, invoice_number, created_at, invoice_with_vat, note, customer_id):
    remove_invoice_items = text("""
        DELETE ii 
        FROM invoice_items ii
        JOIN invoices i ON i.id = ii.invoice_id 
        WHERE ii.invoice_id = :invoice_id
        AND i.company_id = :company_id
    """)
    insert_new_invoice_items = text("""
        INSERT INTO invoice_items
        (invoice_id, product_id, quantity, discount, product_price_no_vat, product_description, vat_percentage, product_name)
        VALUES 
        (:invoice_id, :product_id, :quantity, :discount, :product_price_no_vat, :product_description, :vat_percentage, :product_name)
    """)
    validation_query = text("""
        SELECT company_id
        FROM invoices
        WHERE id = :invoice_id
    """)
    update_counter_query = text("""CALL UpdateInvoiceCounter(:_company_id, :_year, :_invoice_number)""")

    set_new_invoice_data_query = text("""
        UPDATE invoices
        SET invoice_number = :invoice_number,
            created_at = :created_at,
            customer_id = :customer_id,
            invoice_with_vat = :invoice_with_vat,
            note = :note
        WHERE id = :invoice_id
        AND company_id = :company_id
    """)

    try:
        with get_db_connection() as connection:
            with connection.begin():
                res = connection.execute(validation_query, {
                    "invoice_id": invoice_id
                }).fetchone()
                if not res or res[0] != company_id:
                    raise ValueError("Unauthorized acces to invoice.")

                connection.execute(remove_invoice_items, {
                    "invoice_id": invoice_id,
                    "company_id": company_id
                })

                for item in invoice_items:
                    connection.execute(insert_new_invoice_items, {
                        "invoice_id": invoice_id,
                        "product_id": item.get('id'),
                        "quantity": item.get('quantity'),
                        "discount": item.get('discount'),
                        "product_price_no_vat": item.get('price'),
                        "product_description": item.get('description'),
                        "vat_percentage": item.get('vatPercentage'),
                        "product_name": item.get('productName')
                    })

                connection.execute(set_new_invoice_data_query, {
                    "invoice_number": invoice_number,
                    "invoice_id": invoice_id,
                    "created_at": created_at,
                    "customer_id": customer_id,
                    "invoice_with_vat": invoice_with_vat,
                    "note": note,
                    "company_id": company_id
                })

                connection.execute(update_counter_query, {
                    "_company_id": company_id,
                    "_year": created_at.year,
                    "_invoice_number": invoice_number,
                })

                return jsonify({'message': "Invoice updated!"}), 201
    except IntegrityError:
        return jsonify({'error': "Invoice with that number already exists."}), 400
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': "Error updating invoice."}), 400
