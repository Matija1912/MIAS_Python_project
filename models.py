class User:
    def __init__(self, _id, email, first_name, last_name, company, role):
        self.id = _id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.role = role
        self.is_auth = False

    def __repr__(self):
        return self.first_name + " " + self.last_name


    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)
    def is_authenticated(self):
        return self.is_auth
    def login(self):
        self.is_auth = True
    def logout(self):
        self.is_auth = False

class Company:
    def __init__(self, _id, name, street, city, post_number, vat_id):
        self.id = _id
        self.name = name
        self.street = street
        self.city = city
        self.post_number = post_number
        self.vat_id = vat_id

    def __repr__(self):
        return self.name

class Customer:
    def __init__(self, name, email, address, postal_code, city, country, vat_id):
        self.name = name
        self.email = email
        self.address = address
        self.postal_code = postal_code
        self.city = city
        self.country = country
        self.vat_id = vat_id
    def __repr__(self):
        return self.name + " " + self.email + " " + self.address + " " + self.postal_code + " " + self.city + " " + self.country + " " + self.vat_id

class Product:
    def __init__(self, name, description, price_no_vat, vat_percentage):
        self.name = name
        self.description = description
        self.price_no_vat = price_no_vat
        self.vat_percentage = vat_percentage
        self.stock = 0

class Invoice:
    def __init__(self, customer_id, invoice_number, invoice_device_number, invoice_office_number, created_at, status, with_vat, note):
        self.customer_id = customer_id
        self.invoice_number = invoice_number
        self.invoice_device_number = invoice_device_number
        self.invoice_office_number = invoice_office_number
        self.created_at = created_at
        self.status = status
        self.with_vat = with_vat
        self.note = note
    def __repr__(self):
        return self.customer + " " + self.invoice_number + "/" + self.invoice_device_number + "/" + self.invoice_office_number + " " + self.created_at + " " + self.status

    def get_formatted_reference(self):
        return f"{self.invoice_number:02}/{self.invoice_device_number:02}/{self.invoice_office_number:02}"