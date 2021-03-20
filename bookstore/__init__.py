import bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
#app.secret_key = 'monkey'
#Saw this way to set secret key
app.config['SECRET_KEY'] = 'monkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cen4010group11@gmail.com'
app.config['MAIL_PASSWORD'] = 'monkeyseemonkeydo'
mail = Mail(app)

from bookstore import routes


