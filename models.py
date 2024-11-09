class User:
    def __init__(self, id, email,first_name, last_name, company, role):
        self.id = id
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
    def __init__(self, id, name, street, city, post_number, vat_id):
        self.id = id
        self.name = name
        self.street = street
        self.city = city
        self.post_number = post_number
        self.vat_id = vat_id

    def __repr__(self):
        return self.name