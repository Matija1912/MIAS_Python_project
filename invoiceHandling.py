from flask import render_template

def generate_html_invoice(invoice_data, out):
    rendered_html = render_template('invoice_html_templates/default_template.html', **invoice_data)
    with open(out, 'w', encoding='utf-8') as file:
        file.write(rendered_html)


