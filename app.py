from flask import Flask

app = Flask(__name__)

from views import views

app.register_blueprint(views, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)
