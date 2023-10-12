from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

import sys
sys.path.append("..")

from DB.database import Database

app = Flask(__name__)
app.static_folder = 'static'
app.config.update(SECRET_KEY = 'some secret key')

bcrypt = Bcrypt(app)
def gen_hashed_password(password : str):
    return bcrypt.generate_password_hash(password).decode('utf8')

def check_password_hash(hashed_password, password) :
    return bcrypt.check_password_hash(hashed_password, password)

db = Database()
db.insert_doctor_credentials("Petrovich", gen_hashed_password("simple_password")) #для теста login_post

login_manager = LoginManager(app)