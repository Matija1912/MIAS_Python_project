import io

from flask import Blueprint, render_template, send_file, request, flash, redirect, url_for
from flask_login import login_required, current_user
from pdfkit import from_string
from invoice_proforma_database_utils import get_invoice_by_id
from product_customer_database_utils import get_customer_by_id

download_views = Blueprint('download_views', __name__)


@download_views.route('/invoice')
@login_required
def download_invoice():
    invoice_id = request.args.get('id')
    invoice_data = get_invoice_by_id(invoice_id, current_user.company.id)
    customer_id = invoice_data.get("invoice").customer_id
    customer_data = get_customer_by_id(customer_id, current_user.company.id)

    vat_total = 0
    total_with_vat = 0

    for item in invoice_data.get('invoice_items'):
        amount_no_vat = (item.get('price_no_vat') * item.get('quantity')) * (1 - (item.get('discount_percentage') / 100))
        vat_amount = (item.get('vat_percentage') / 100) * amount_no_vat
        vat_total += vat_amount
        total_with_vat += (vat_amount + amount_no_vat)

    if invoice_data and customer_data:
        invoice = {
            "invoice": invoice_data.get('invoice'),
            "invoice_items": invoice_data.get('invoice_items'),
            "user": current_user,
            "customer": customer_data,
            "vat_total": vat_total,
            "total_with_vat": total_with_vat
        }
        download_file_name = f"Invoice{invoice.get('invoice')[5]}/{invoice.get('invoice')[8]}/{invoice.get('invoice')[9]}({current_user.company.name}).pdf"

        rendered_html_string = render_template("invoice_html_templates/default_template.html", **invoice)
        pdf_bytes = from_string(rendered_html_string)
        pdf_obj = io.BytesIO(pdf_bytes)
        pdf_obj.seek(0)
        return send_file(
            pdf_obj,
            as_attachment=True,
            download_name=download_file_name,
            mimetype="application/pdf"
        )
    else:
        flash('An error occured', category='error')
        return redirect(url_for('mInvoicesViews.invoices'))
