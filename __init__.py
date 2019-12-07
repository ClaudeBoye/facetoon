from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ajesdfneue8w0389jfa0debj7enkdioe9i8e7uu48'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facetoon.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cboye66@gmail.com'
app.config['MAIL_PASSWORD'] = 'yesitmine007'

mail = Mail(app)

from facetoonblog import routes